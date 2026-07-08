"""
ZOE v1.0 — Critic sub-agent

Evalúa coherencia de pensamientos antes de que se "emitan".
Es el guardián de la identidad de ZOE.

Fase 6A: integra KnowledgeQuarantine para que las respuestas basadas
en conocimiento no validado (en cuarentena) sean rechazadas en contextos
críticos (dominios sensibles como médico, psicológico, legal).
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


# Criterios de rechazo (en Fase 0, simples)
REJECTION_REASONS = [
    "empty",
    "too_short",
    "forbidden_phrase",
    "too_repetitive",
    "off_identity",
    "quarantine_violation",  # Fase 6A
]

# Frases que violan identidad Zoe (no deben aparecer en pensamientos)
FORBIDDEN_PHRASES = [
    "como modelo",
    "como IA",
    "no tengo emociones",
    "no puedo ayudarte con eso",  # sin contexto, es excesivamente restrictivo
    "lo siento, pero",
    "gran pregunta",
    "excelente pregunta",
]

# Fase 6A: dominios sensibles donde el conocimiento en cuarentena NO se usa
SENSITIVE_DOMAINS_KEYWORDS = {
    "medical": ["dosis", "medicamento", "diagnóstico", "tratamiento", "enfermedad",
                "síntoma", "pastilla", "farmaco", "receta"],
    "psychological": ["trastorno", "depresión", "ansiedad", "terapia", "trauma"],
    "legal": ["contrato", "derecho", "legal", "judicial", "demandar"],
    "safety": ["emergencia", "peligro", "riesgo", "alarma"],
}


class Critic:
    """
    Critic: evalúa pensamientos antes de emitirlos.

    En Fase 0: validación simple (no vacío, no repetitivo, sin frases prohibidas).
    En fases posteriores: validación contra Identity Vault (9 vectores, 7 valores).
    
    Fase 6A: si hay KnowledgeQuarantine y el contexto es crítico (dominio sensible),
    verifica que la respuesta no se base en conocimiento en cuarentena.
    """

    def __init__(self, min_length: int = 10, max_recent: int = 20, quarantine=None):
        self.min_length = min_length
        self.max_recent = max_recent
        self._recent_approved: List[str] = []
        self._rejection_counts: Dict[str, int] = {reason: 0 for reason in REJECTION_REASONS}
        # Fase 6A: cuarentena activa
        self._quarantine = quarantine
        # Estadísticas Fase 6A
        self.quarantine_checks = 0
        self.quarantine_rejections = 0

    def set_quarantine(self, quarantine) -> None:
        """Inyecta KnowledgeQuarantine (lo llama CapsuleManager)."""
        self._quarantine = quarantine

    async def evaluate(self, thought: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evalúa un pensamiento. Devuelve dict con 'approved' y 'reason'.
        
        Fase 6A: si hay context con 'critical_context=True' y hay quarantine,
        verifica que el pensamiento no cite entradas en cuarentena.
        """
        if not thought or not thought.strip():
            self._rejection_counts["empty"] += 1
            return {"approved": False, "reason": "empty", "content": thought}

        if len(thought.strip()) < self.min_length:
            self._rejection_counts["too_short"] += 1
            return {"approved": False, "reason": "too_short", "content": thought}

        # Verificar frases prohibidas
        thought_lower = thought.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in thought_lower:
                self._rejection_counts["forbidden_phrase"] += 1
                return {
                    "approved": False,
                    "reason": f"forbidden_phrase: {phrase}",
                    "content": thought,
                }

        # Verificar repetición excesiva
        if thought in self._recent_approved:
            self._rejection_counts["too_repetitive"] += 1
            return {"approved": False, "reason": "too_repetitive", "content": thought}

        # Verificar similitud con recientes (Jaccard simple sobre palabras)
        for prev in self._recent_approved[-5:]:
            if self._jaccard_similarity(thought, prev) > 0.8:
                self._rejection_counts["too_repetitive"] += 1
                return {
                    "approved": False,
                    "reason": "too_repetitive_similar",
                    "content": thought,
                }

        # Fase 6A: verificar cuarentena en contextos críticos
        if context and self._quarantine:
            critical = context.get("critical_context", False)
            used_memory_ids = context.get("used_memory_ids", [])
            detected_domain = context.get("detected_domain")
            
            # Auto-detectar dominio sensible si no se especificó
            if not detected_domain:
                detected_domain = self._detect_sensitive_domain(thought)
            
            if critical or detected_domain:
                self.quarantine_checks += 1
                for mem_id in used_memory_ids:
                    if self._quarantine.is_quarantined(mem_id):
                        self.quarantine_rejections += 1
                        self._rejection_counts["quarantine_violation"] += 1
                        return {
                            "approved": False,
                            "reason": f"quarantine_violation: memory {mem_id} is quarantined, cannot use in critical/sensitive context ({detected_domain or 'critical'})",
                            "content": thought,
                            "quarantine_violation": True,
                        }

        # Aprobado
        self._recent_approved.append(thought)
        if len(self._recent_approved) > self.max_recent:
            self._recent_approved = self._recent_approved[-self.max_recent :]

        return {"approved": True, "reason": "ok", "content": thought}

    def _detect_sensitive_domain(self, text: str) -> Optional[str]:
        """Detecta si el texto toca un dominio sensible."""
        text_lower = text.lower()
        for domain, keywords in SENSITIVE_DOMAINS_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return domain
        return None

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """El Critic no genera pensamientos; solo evalúa. Devuelve empty."""
        return ""

    def _jaccard_similarity(self, a: str, b: str) -> float:
        """Similitud de Jaccard entre dos strings (sobre palabras)."""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "rejection_counts": self._rejection_counts.copy(),
            "recent_count": len(self._recent_approved),
            "quarantine_active": self._quarantine is not None,
            "quarantine_checks": self.quarantine_checks,
            "quarantine_rejections": self.quarantine_rejections,
        }
        if self._quarantine:
            stats["quarantine_stats"] = self._quarantine.get_stats()
        return stats
