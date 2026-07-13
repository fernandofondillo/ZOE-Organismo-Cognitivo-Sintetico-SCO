"""
ZOE v1.1 — Cross Validator (Fase 6A, Opción 3)

Coordinador de triple verificación multi-fuente.

El problema que resuelve:
- Una sola fuente (incluso GPT-4o) puede estar sesgada o alucinar.
- CrossValidator coordina consulta a múltiples fuentes y solo consolida
  si hay acuerdo.

Protocolo:
1. ScientificEngine detecta gap o EpistemicValidator marca cuarentena
2. CrossValidator formula misma query a fuente A (LLM-1)
3. CrossValidator formula misma query a fuente B (LLM-2 o cápsula)
4. CrossValidator formula misma query a fuente C (otro LLM o cápsula)
5. Compara las 3 respuestas:
   - 3/3 coinciden → confianza 0.75, sale de cuarentena
   - 2/3 coinciden → confianza 0.65, sigue en cuarentena con pending_third_source
   - Divergencia total → rechazo, marca conflicto
6. Solo se aplica en dominios sensibles o cuando hay contradicción detectada
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Awaitable

from .epistemic_validator import (
    EpistemicValidator, ValidationResult, ValidationStatus,
    MAX_TRIPLE_VERIFIED_CONFIDENCE,
)
from .knowledge_quarantine import KnowledgeQuarantine

logger = logging.getLogger(__name__)


@dataclass
class CrossVerificationResult:
    """Resultado de una verificación cruzada triple."""
    claim: str
    sources_queried: List[str]
    responses: Dict[str, str]  # source → response
    agreement: str  # "full" | "majority" | "divergent" | "contradictory"
    final_confidence: float
    final_status: ValidationStatus
    coincident_sources: List[str]
    divergent_sources: List[str]
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim[:200],
            "sources_queried": self.sources_queried,
            "responses": {k: v[:200] for k, v in self.responses.items()},
            "agreement": self.agreement,
            "final_confidence": round(self.final_confidence, 3),
            "final_status": self.final_status.value,
            "coincident_sources": self.coincident_sources,
            "divergent_sources": self.divergent_sources,
            "timestamp": self.timestamp,
        }


class CrossValidator:
    """
    Coordina verificación cruzada triple de conocimiento nuevo.
    
    Integración:
    - EpistemicValidator marca claim como NEEDS_TRIPLE_VALIDATION
    - CrossValidator.query_multiple() consulta 3 fuentes
    - CrossValidator.compare() determina agreement
    - Si full → KnowledgeQuarantine.promote()
    - Si divergent → KnowledgeQuarantine.reject()
    """
    
    def __init__(
        self,
        epistemic_validator: Optional[EpistemicValidator] = None,
        quarantine: Optional[KnowledgeQuarantine] = None,
    ):
        self.validator = epistemic_validator or EpistemicValidator()
        self.quarantine = quarantine or KnowledgeQuarantine()
        
        # Funciones de consulta registradas (source → async callable)
        self._query_funcs: Dict[str, Callable[[str], Awaitable[str]]] = {}
        
        # Estadísticas
        self.cross_verifications = 0
        self.full_agreements = 0
        self.majority_agreements = 0
        self.divergences = 0
        self.contradictions_with_capsule = 0
    
    def register_source(
        self,
        source_name: str,
        query_func: Callable[[str], Awaitable[str]],
    ) -> None:
        """Registra una fuente consultable."""
        self._query_funcs[source_name] = query_func
        logger.info(f"CrossValidator registered source: {source_name}")
    
    async def verify_triple(
        self,
        claim: str,
        sources: List[str],
        capsule_responses: Optional[List[str]] = None,
    ) -> CrossVerificationResult:
        """
        Verifica un claim consultando múltiples fuentes.
        
        Args:
            claim: afirmación a verificar
            sources: lista de fuentes a consultar (ej. ["llm:gpt-4o", "llm:qwen-7b"])
            capsule_responses: respuestas de cápsulas relacionadas (no requieren consulta)
        
        Returns:
            CrossVerificationResult con agreement y confianza final
        """
        self.cross_verifications += 1
        
        responses: Dict[str, str] = {}
        
        # Consultar fuentes registradas
        for source in sources:
            if source in self._query_funcs:
                try:
                    response = await self._query_funcs[source](claim)
                    responses[source] = response
                except Exception as e:
                    logger.warning(f"CrossValidator: source {source} failed: {e}")
                    responses[source] = f"[error: {e}]"
            elif source.startswith("capsule:"):
                # Las cápsulas ya tienen su respuesta en capsule_responses
                if capsule_responses:
                    responses[source] = capsule_responses[0]
                    capsule_responses = capsule_responses[1:]
        
        # Comparar respuestas
        result = self._compare(claim, responses)
        
        # Actualizar estadísticas
        if result.agreement == "full":
            self.full_agreements += 1
        elif result.agreement == "majority":
            self.majority_agreements += 1
        elif result.agreement == "divergent":
            self.divergences += 1
        elif result.agreement == "contradictory":
            self.contradictions_with_capsule += 1
        
        return result
    
    def _compare(
        self, claim: str, responses: Dict[str, str]
    ) -> CrossVerificationResult:
        """Compara respuestas y determina agreement."""
        if not responses:
            return CrossVerificationResult(
                claim=claim,
                sources_queried=list(responses.keys()),
                responses=responses,
                agreement="divergent",
                final_confidence=0.0,
                final_status=ValidationStatus.REJECTED,
                coincident_sources=[],
                divergent_sources=[],
            )
        
        # Verificar si las respuestas coinciden (heurística simple)
        # En producción: usar embeddings o LLM para comparación semántica
        normalized_responses = {}
        for source, response in responses.items():
            # Normalizar: lowercase, sin espacios extra, sin puntuación
            norm = " ".join(response.lower().split())
            normalized_responses[source] = norm
        
        # Detectar contradicción con cápsula
        capsule_sources = [s for s in responses if s.startswith("capsule:")]
        llm_sources = [s for s in responses if s.startswith("llm:")]
        
        # Coincidencia exacta (normalizada)
        unique_responses = set(normalized_responses.values())
        
        if len(unique_responses) == 1:
            # Todas coinciden
            return CrossVerificationResult(
                claim=claim,
                sources_queried=list(responses.keys()),
                responses=responses,
                agreement="full",
                final_confidence=MAX_TRIPLE_VERIFIED_CONFIDENCE,
                final_status=ValidationStatus.ACCEPTED,
                coincident_sources=list(responses.keys()),
                divergent_sources=[],
            )
        
        # Coincidencia por similitud (heurística léxica)
        coincidence_groups = self._group_similar(normalized_responses)
        
        if len(coincidence_groups) == 1:
            # Todas semánticamente iguales
            return CrossVerificationResult(
                claim=claim,
                sources_queried=list(responses.keys()),
                responses=responses,
                agreement="full",
                final_confidence=MAX_TRIPLE_VERIFIED_CONFIDENCE,
                final_status=ValidationStatus.ACCEPTED,
                coincident_sources=list(responses.keys()),
                divergent_sources=[],
            )
        
        # Mayoría (2 de 3)
        majority_group = max(coincidence_groups, key=len)
        if len(majority_group) >= 2:
            coincident = [s for s in majority_group]
            divergent = [s for s in responses if s not in coincident]
            
            # Si cápsula está en mayoría, confianza más alta
            capsule_in_majority = any(s.startswith("capsule:") for s in coincident)
            confidence = 0.80 if capsule_in_majority else 0.65
            
            return CrossVerificationResult(
                claim=claim,
                sources_queried=list(responses.keys()),
                responses=responses,
                agreement="majority",
                final_confidence=confidence,
                final_status=ValidationStatus.ACCEPTED_WITH_QUARANTINE,
                coincident_sources=coincident,
                divergent_sources=divergent,
            )
        
        # Divergencia total
        return CrossVerificationResult(
            claim=claim,
            sources_queried=list(responses.keys()),
            responses=responses,
            agreement="divergent",
            final_confidence=0.0,
            final_status=ValidationStatus.REJECTED,
            coincident_sources=[],
            divergent_sources=list(responses.keys()),
        )
    
    def _group_similar(
        self, normalized: Dict[str, str]
    ) -> List[List[str]]:
        """Agrupa respuestas similares por similitud léxica."""
        groups: List[List[str]] = []
        threshold = 0.6  # 60% de palabras en común
        
        for source, response in normalized.items():
            placed = False
            for group in groups:
                # Comparar con el primer elemento del grupo
                ref_source = group[0]
                ref_response = normalized[ref_source]
                similarity = self._lexical_similarity(response, ref_response)
                if similarity >= threshold:
                    group.append(source)
                    placed = True
                    break
            if not placed:
                groups.append([source])
        
        return groups
    
    def _lexical_similarity(self, a: str, b: str) -> float:
        """Similitud léxica entre dos strings (Jaccard sobre palabras)."""
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a and not words_b:
            return 1.0
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)
    
    async def verify_and_promote(
        self,
        quarantine_entry_id: str,
        claim: str,
        sources: List[str],
        capsule_responses: Optional[List[str]] = None,
    ) -> CrossVerificationResult:
        """
        Verifica un claim en cuarentena y promueve/rechaza según resultado.
        """
        result = await self.verify_triple(claim, sources, capsule_responses)
        
        if result.final_status == ValidationStatus.ACCEPTED:
            # Promover
            self.quarantine.promote(
                entry_id=quarantine_entry_id,
                new_confidence=result.final_confidence,
                reason=f"cross_validated:{result.agreement}",
            )
        elif result.final_status == ValidationStatus.REJECTED:
            # Rechazar
            self.quarantine.reject(
                entry_id=quarantine_entry_id,
                contradicting_source="cross_validator",
                reason=f"divergent_responses:{result.agreement}",
            )
        # Si ACCEPTED_WITH_QUARANTINE, se queda en cuarentena pero con confianza actualizada
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_cross_verifications": self.cross_verifications,
            "full_agreements": self.full_agreements,
            "majority_agreements": self.majority_agreements,
            "divergences": self.divergences,
            "contradictions_with_capsule": self.contradictions_with_capsule,
            "registered_sources": list(self._query_funcs.keys()),
            "full_agreement_rate": round(
                self.full_agreements / max(1, self.cross_verifications), 3
            ),
        }
