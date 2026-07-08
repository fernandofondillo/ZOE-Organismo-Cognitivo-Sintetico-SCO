"""
ZOE v1.1 — Epistemic Validator (Fase 6A, Opción 1)

Valida todo conocimiento nuevo antes de que entre a memoria.
Implementa políticas de confianza según fuente, dominio y contradicción.

El problema que resuelve:
- Sin validación: ZOE almacena cualquier claim de cualquier fuente con confianza media.
- Con EpistemicValidator: cada claim se valida contra política, y se acepta, se
  cuarentena o se rechaza automáticamente.

Componentes:
- SOURCE_TRUST: confianza base por fuente (14 fuentes categorizadas)
- SENSITIVE_DOMAINS: dominios que requieren triple verificación obligatoria
- MAX_AUTO_LEARNED_CONFIDENCE: cap para conocimiento auto-aprendido sin validar
- ValidationResult: resultado estructurado con status, confidence, reason, quarantine
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Políticas de confianza
# ============================================================

# Confianza base por fuente
SOURCE_TRUST: Dict[str, float] = {
    # Cápsulas (conocimiento profesional previo)
    "capsule:verified": 0.95,         # Cápsula con sello profesional
    "capsule:curated": 0.80,          # Cápsula curada por expertos
    "capsule:community": 0.55,        # Cápsula comunitaria
    "capsule:experimental": 0.40,     # Cápsula experimental
    
    # LLMs externos
    "llm:gpt-4o": 0.50,
    "llm:gpt-4-turbo": 0.48,
    "llm:gpt-4o-mini": 0.42,
    "llm:claude-opus": 0.55,
    "llm:claude-sonnet": 0.50,
    "llm:qwen-7b": 0.45,
    "llm:qwen-3b": 0.40,
    "llm:qwen-2.5:3b": 0.40,
    "llm:llama-3-70b": 0.48,
    "llm:zai": 0.42,
    "llm:mock": 0.20,
    
    # Humanos
    "user:human": 0.70,               # Lo que dice el usuario sobre sí mismo
    "user:domain_expert": 0.85,       # Usuario identificado como experto del dominio
    "admin:human": 0.90,              # Administrador humano del sistema
    
    # Federación
    "federated:peer_zoe": 0.60,       # Lo que dice otra ZOE
    "federated:peer_zoe_verified": 0.75,  # ZOE con conocimiento ya validado
    
    # Fuentes científicas
    "scientific:pubmed": 0.95,
    "scientific:arxiv": 0.85,
    "scientific:doi": 0.92,
    "scientific:peer_reviewed": 0.90,
    
    # Web
    "web:wiki": 0.65,
    "web:gov": 0.80,
    "web:edu": 0.75,
    "web:general": 0.30,
    
    # Triple verificación
    "multi_source:llm_cross_validated": 0.75,
    "multi_source:llm_cross_validated+capsule_match": 0.80,
    
    # Federación epistémica
    "federatively_validated:2plus_peers": 0.85,
    "federatively_validated:5plus_peers": 0.90,
    
    # Default
    "unknown": 0.20,
}

# Dominios sensibles: requieren doble verificación
SENSITIVE_DOMAINS: Dict[str, List[str]] = {
    "medical": [
        "medicación", "diagnóstico", "pronóstico", "dosificación",
        "síntoma", "tratamiento", "enfermedad", "fármaco", "dosis",
        "prescripción", "interacción", "contraindicación",
    ],
    "psychological": [
        "trastorno", "terapia", "trauma", "depresión", "ansiedad",
        "psicología", "psiquiatría", "salud mental", "autolesión",
        "ideación suicida", "psicosis",
    ],
    "legal": [
        "contrato", "obligación", "derecho", "legal", "judicial",
        "demandar", "herencia", "testamento", "tutela",
    ],
    "safety": [
        "emergencia", "riesgo", "peligro", "seguridad", "alarma",
        "caída", "accidente", "intoxicación",
    ],
    "financial": [
        "inversión", "préstamo", "impuesto", "dinero", "banca",
        "hipoteca", "seguro", "comisión", "rentabilidad",
    ],
}

# Cap de confianza para auto-aprendido
MAX_AUTO_LEARNED_CONFIDENCE = 0.50
MAX_TRIPLE_VERIFIED_CONFIDENCE = 0.75
MAX_FEDERATIVELY_VALIDATED_CONFIDENCE = 0.85
MAX_CAPSULE_VERIFIED_CONFIDENCE = 0.95


# ============================================================
# Resultado de validación
# ============================================================

class ValidationStatus(str, Enum):
    """Estado del conocimiento tras validación."""
    ACCEPTED = "accepted"                       # Aceptado con confianza normal
    ACCEPTED_WITH_QUARANTINE = "quarantined"    # Aceptado pero en cuarentena
    REJECTED = "rejected"                       # Rechazado
    NEEDS_TRIPLE_VALIDATION = "needs_triple"    # Requiere triple verificación
    NEEDS_FEDERATION = "needs_federation"       # Requiere validación federada


@dataclass
class ValidationResult:
    """Resultado de validar un claim nuevo."""
    status: ValidationStatus
    confidence: float
    reason: str
    source: str
    quarantine: bool = False
    needs_verification_plan: bool = False
    verification_plan: Optional[Dict[str, Any]] = None
    detected_domain: Optional[str] = None
    contradictions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "source": self.source,
            "quarantine": self.quarantine,
            "needs_verification_plan": self.needs_verification_plan,
            "verification_plan": self.verification_plan,
            "detected_domain": self.detected_domain,
            "contradictions": self.contradictions,
        }


# ============================================================
# Validator
# ============================================================

class EpistemicValidator:
    """
    Valida todo conocimiento nuevo antes de que entre a memoria.
    
    Uso:
        validator = EpistemicValidator()
        result = validator.validate_new_knowledge(
            claim="Las benzodiacepinas son seguras en mayores",
            source="llm:gpt-4o",
            context={"capsule_semantic": [...], "verified_knowledge": [...]}
        )
        if result.quarantine:
            # almacenar con metadata.quarantine = True
        elif result.status == ValidationStatus.REJECTED:
            # no almacenar
        else:
            # almacenar con result.confidence
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.source_trust = {**SOURCE_TRUST, **self.config.get("source_trust", {})}
        self.sensitive_domains = {**SENSITIVE_DOMAINS, **self.config.get("sensitive_domains", {})}
        self.max_auto_learned = self.config.get("max_auto_learned_confidence", MAX_AUTO_LEARNED_CONFIDENCE)
        
        # Estadísticas
        self.validations = 0
        self.accepted = 0
        self.quarantined = 0
        self.rejected = 0
        self.by_domain: Dict[str, int] = {}
        self.by_source: Dict[str, int] = {}
    
    def validate_new_knowledge(
        self,
        claim: str,
        source: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Valida un claim nuevo antes de almacenarlo.
        
        Args:
            claim: afirmación a validar
            source: origen ("llm:gpt-4o", "capsule:verified", etc.)
            context: dict opcional con:
                - capsule_semantic: entradas de cápsula para contrastar
                - verified_knowledge: conocimiento ya verificado
                - learned_knowledge: conocimiento aprendido previo
                - allow_sensitive: si True, no bloquear sensible (default False)
        
        Returns:
            ValidationResult con status, confidence, reason, quarantine
        """
        if context is None:
            context = {}
        
        self.validations += 1
        self.by_source[source] = self.by_source.get(source, 0) + 1
        
        # 1. Confianza base por fuente
        base_confidence = self.source_trust.get(source, 0.20)
        
        # 2. Detectar dominio
        domain = self._detect_domain(claim)
        if domain:
            self.by_domain[domain] = self.by_domain.get(domain, 0) + 1
        
        # 3. Si contradice conocimiento verificado → rechazar PRIMERO
        # (incluso en dominio sensible, contradicción con verificado es bloque prioritario)
        contradictions = []
        for entry in context.get("verified_knowledge", []) + context.get("capsule_semantic", []):
            if entry.get("confidence", 0) >= 0.85:
                if self._contradicts(claim, entry.get("content", "")):
                    contradictions.append(entry.get("provenance", "unknown"))
        
        if contradictions:
            self.rejected += 1
            return ValidationResult(
                status=ValidationStatus.REJECTED,
                confidence=0.0,
                reason=f"contradicts_verified_knowledge:{contradictions[0]}",
                source=source,
                detected_domain=domain,
                contradictions=contradictions,
            )
        
        # 4. Si dominio sensible y no es fuente de alta confianza → requiere triple
        if domain and domain in self.sensitive_domains:
            trusted_sources = {
                "capsule:verified", "scientific:pubmed", "scientific:doi",
                "scientific:peer_reviewed", "admin:human",
                "multi_source:llm_cross_validated+capsule_match",
                "federatively_validated:2plus_peers",
            }
            if source not in trusted_sources and not context.get("allow_sensitive"):
                result = ValidationResult(
                    status=ValidationStatus.NEEDS_TRIPLE_VALIDATION,
                    confidence=base_confidence,
                    reason=f"sensitive_domain_requires_triple_validation:{domain}",
                    source=source,
                    quarantine=True,
                    needs_verification_plan=True,
                    verification_plan=self._make_verification_plan(claim, domain),
                    detected_domain=domain,
                )
                self.quarantined += 1
                return result
        
        # 5. Si contradice conocimiento aprendido (confianza media) → marcar conflicto
        for entry in context.get("learned_knowledge", []):
            if entry.get("confidence", 0) >= 0.5:
                if self._contradicts(claim, entry.get("content", "")):
                    # No rechazar, pero marcar para revisión
                    return ValidationResult(
                        status=ValidationStatus.NEEDS_FEDERATION,
                        confidence=min(base_confidence, 0.4),
                        reason=f"contradicts_learned_knowledge:{entry.get('provenance', 'unknown')}",
                        source=source,
                        quarantine=True,
                        needs_verification_plan=True,
                        verification_plan=self._make_verification_plan(claim, domain),
                        detected_domain=domain,
                        contradictions=[entry.get("provenance", "unknown")],
                    )
        
        # 6. Aplicar cap según fuente
        if source.startswith("capsule:"):
            capped_confidence = min(base_confidence, MAX_CAPSULE_VERIFIED_CONFIDENCE)
            self.accepted += 1
            return ValidationResult(
                status=ValidationStatus.ACCEPTED,
                confidence=capped_confidence,
                reason="capsule_accepted",
                source=source,
                detected_domain=domain,
            )
        
        if source.startswith("federatively_validated:"):
            capped = min(base_confidence, MAX_FEDERATIVELY_VALIDATED_CONFIDENCE)
            self.accepted += 1
            return ValidationResult(
                status=ValidationStatus.ACCEPTED,
                confidence=capped,
                reason="federatively_validated",
                source=source,
                detected_domain=domain,
            )
        
        if source.startswith("multi_source:"):
            capped = min(base_confidence, MAX_TRIPLE_VERIFIED_CONFIDENCE)
            self.accepted += 1
            return ValidationResult(
                status=ValidationStatus.ACCEPTED,
                confidence=capped,
                reason="triple_verified",
                source=source,
                detected_domain=domain,
            )
        
        # 7. Conocimiento nuevo (no contradictorio, no sensible, fuente única)
        #    → aceptar con cuarentena y confianza reducida
        capped = min(base_confidence, self.max_auto_learned)
        self.quarantined += 1
        return ValidationResult(
            status=ValidationStatus.ACCEPTED_WITH_QUARANTINE,
            confidence=capped,
            reason="accepted_with_quarantine",
            source=source,
            quarantine=True,
            needs_verification_plan=True,
            verification_plan=self._make_verification_plan(claim, domain),
            detected_domain=domain,
        )
    
    def _detect_domain(self, text: str) -> Optional[str]:
        """Detecta el dominio del claim."""
        text_lower = text.lower()
        detected = []
        for domain, keywords in self.sensitive_domains.items():
            for kw in keywords:
                if kw in text_lower:
                    detected.append(domain)
                    break
        return detected[0] if detected else None
    
    def _contradicts(self, claim: str, reference: str) -> bool:
        """Heurística simple de contradicción."""
        negations = ["no es", "no ", "nunca", "falso", "incorrecto", "miento",
                    "negado", "refutado", "desmentido"]
        claim_lower = claim.lower()
        ref_lower = reference.lower()
        
        # Si la referencia dice algo y el claim lo niega
        for neg in negations:
            if neg in claim_lower and neg not in ref_lower:
                # Comprobar si comparten tema
                common_words = set(claim_lower.split()) & set(ref_lower.split())
                common_meaningful = {w for w in common_words if len(w) > 4}
                if len(common_meaningful) >= 3:
                    return True
        
        return False
    
    def _make_verification_plan(self, claim: str, domain: Optional[str]) -> Dict[str, Any]:
        """Crea un plan de verificación para sacar el claim de cuarentena."""
        return {
            "required_verifications": 2,
            "acceptable_sources": [
                "capsule:verified",
                "scientific:pubmed",
                "scientific:doi",
                "user:domain_expert",
                "federatively_validated:2plus_peers",
                "multi_source:llm_cross_validated",
            ],
            "timeout_days": 30,
            "domain": domain,
            "claim_preview": claim[:200],
            "created_at": None,  # se rellena al almacenar
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del validador."""
        return {
            "total_validations": self.validations,
            "accepted": self.accepted,
            "quarantined": self.quarantined,
            "rejected": self.rejected,
            "by_domain": dict(self.by_domain),
            "by_source": dict(self.by_source),
            "acceptance_rate": round(self.accepted / max(1, self.validations), 3),
            "quarantine_rate": round(self.quarantined / max(1, self.validations), 3),
            "rejection_rate": round(self.rejected / max(1, self.validations), 3),
        }
