"""
ZOE v1.1 — Knowledge Quarantine (Fase 6A, Opción 2)

Gestión de cuarentena activa para conocimiento no validado.

El problema que resuelve:
- Aunque un claim entre con confianza baja, el sistema podría usarlo para
  decisiones críticas (responder a usuario en dominio sensible, tomar acción
  externa, mutar arquitectura).
- KnowledgeQuarantine marca conocimiento no validado como quarantine=True
  y bloquea su uso en contextos críticos.

Política:
- Las memorias en cuarentena NO se usan para:
  * Respuestas a usuarios en dominios sensibles (médico, psicológico, etc.)
  * Decisiones de acción externa (avisar familia, ejecutar tool)
  * Mutaciones arquitecturales (cambiar sub-agentes o umbrales)
- Las memorias en cuarentena SÍ se usan para:
  * Brainstorming interno
  * Hipótesis para ScientificEngine explorar
  * Sugerencia al usuario de "podría ser, pero no estoy segura"
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class QuarantineEntry:
    """Entrada en cuarentena."""
    entry_id: str
    claim: str
    source: str
    confidence: float
    domain: Optional[str]
    reason: str
    verification_plan: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None  # None = usa default
    confirmations: List[str] = field(default_factory=list)  # fuentes que confirmaron
    contradictions: List[str] = field(default_factory=list)  # fuentes que contradijeron
    status: str = "active"  # active | verified | rejected | expired | promoted
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "claim": self.claim[:200],
            "source": self.source,
            "confidence": round(self.confidence, 3),
            "domain": self.domain,
            "reason": self.reason,
            "verification_plan": self.verification_plan,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "confirmations": self.confirmations,
            "contradictions": self.contradictions,
            "status": self.status,
        }


class KnowledgeQuarantine:
    """
    Gestiona el conocimiento en cuarentena.
    
    Integración:
    - Cuando EpistemicValidator devuelve quarantine=True, se llama a add()
    - Cuando CrossValidator valida, se llama a promote() o verify()
    - Cuando expires, se llama a expire()
    - Cuando se busca memoria para uso crítico, se llama a filter_safe()
    """
    
    DEFAULT_TIMEOUT_DAYS = 30
    
    def __init__(self, default_timeout_days: int = None):
        self.default_timeout_days = default_timeout_days or self.DEFAULT_TIMEOUT_DAYS
        self._entries: Dict[str, QuarantineEntry] = {}
        self._memory_entry_map: Dict[str, str] = {}  # memory_entry_id → quarantine_entry_id
    
    def add(
        self,
        entry_id: str,
        claim: str,
        source: str,
        confidence: float,
        domain: Optional[str],
        reason: str,
        verification_plan: Dict[str, Any],
        memory_entry_id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> QuarantineEntry:
        """Añade una entrada a cuarentena."""
        timeout = expires_in_days or self.default_timeout_days
        expires_at = time.time() + (timeout * 86400)
        
        entry = QuarantineEntry(
            entry_id=entry_id,
            claim=claim,
            source=source,
            confidence=confidence,
            domain=domain,
            reason=reason,
            verification_plan=verification_plan,
            expires_at=expires_at,
        )
        
        self._entries[entry_id] = entry
        
        if memory_entry_id:
            self._memory_entry_map[memory_entry_id] = entry_id
        
        logger.info(f"Quarantine ADD: {entry_id} (source={source}, domain={domain})")
        return entry
    
    def is_quarantined(self, memory_entry_id: str) -> bool:
        """Verifica si una entrada de memoria está en cuarentena."""
        qid = self._memory_entry_map.get(memory_entry_id)
        if not qid:
            return False
        entry = self._entries.get(qid)
        if not entry:
            return False
        return entry.status == "active"
    
    def get_quarantine_entry(self, memory_entry_id: str) -> Optional[QuarantineEntry]:
        """Obtiene la entrada de cuarentena asociada a una memoria."""
        qid = self._memory_entry_map.get(memory_entry_id)
        if not qid:
            return None
        return self._entries.get(qid)
    
    def filter_safe(
        self,
        memory_entries: List[Dict[str, Any]],
        critical_context: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filtra memorias para uso seguro.
        
        Args:
            memory_entries: lista de entradas de memoria candidatas
            critical_context: si True, elimina todas las cuarentena;
                             si False, las mantiene pero marca
        
        Returns:
            Lista filtrada
        """
        if not critical_context:
            # Contexto no crítico: mantener todas pero marcar cuarentena
            for entry in memory_entries:
                mem_id = entry.get("id") or entry.get("entry_id", "")
                if self.is_quarantined(mem_id):
                    entry["metadata"] = entry.get("metadata", {})
                    entry["metadata"]["quarantine"] = True
            return memory_entries
        
        # Contexto crítico: eliminar cuarentena
        safe = []
        for entry in memory_entries:
            mem_id = entry.get("id") or entry.get("entry_id", "")
            if not self.is_quarantined(mem_id):
                safe.append(entry)
        return safe
    
    def verify(
        self,
        entry_id: str,
        confirming_source: str,
        new_confidence: float,
    ) -> Optional[QuarantineEntry]:
        """
        Marca una entrada como verificada por una fuente adicional.
        
        Si acumula suficientes verificaciones, se promueve (sale de cuarentena).
        """
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        entry.confirmations.append(confirming_source)
        entry.confidence = new_confidence
        
        # Si tiene 2+ confirmaciones → promover
        plan = entry.verification_plan
        required = plan.get("required_verifications", 2)
        if len(entry.confirmations) >= required:
            return self.promote(entry_id, new_confidence, reason="verified_enough_sources")
        
        return entry
    
    def promote(
        self, entry_id: str, new_confidence: float, reason: str = "promoted"
    ) -> Optional[QuarantineEntry]:
        """Saca una entrada de cuarentena (promoción explícita)."""
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        entry.status = "verified"
        entry.confidence = new_confidence
        logger.info(f"Quarantine PROMOTE: {entry_id} (reason={reason}, confidence={new_confidence})")
        return entry
    
    def reject(
        self, entry_id: str, contradicting_source: str, reason: str = "contradicted"
    ) -> Optional[QuarantineEntry]:
        """Rechaza una entrada en cuarentena."""
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        entry.status = "rejected"
        entry.contradictions.append(contradicting_source)
        logger.info(f"Quarantine REJECT: {entry_id} (reason={reason})")
        return entry
    
    def expire(self, entry_id: str) -> Optional[QuarantineEntry]:
        """Marca una entrada como expirada (timeout alcanzado)."""
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        entry.status = "expired"
        logger.info(f"Quarantine EXPIRE: {entry_id} (timeout)")
        return entry
    
    def cleanup_expired(self) -> int:
        """Elimina entradas expiradas. Devuelve cuántas eliminó."""
        now = time.time()
        expired_ids = []
        for qid, entry in self._entries.items():
            if entry.status == "active" and entry.expires_at and now > entry.expires_at:
                entry.status = "expired"
                expired_ids.append(qid)
        
        for qid in expired_ids:
            self.expire(qid)
        
        return len(expired_ids)
    
    def list_active(self, domain: Optional[str] = None) -> List[QuarantineEntry]:
        """Lista entradas activas en cuarentena, opcionalmente filtradas por dominio."""
        result = []
        for entry in self._entries.values():
            if entry.status != "active":
                continue
            if domain and entry.domain != domain:
                continue
            result.append(entry)
        return result
    
    def list_pending_verification(self) -> List[QuarantineEntry]:
        """Lista entradas que aún necesitan verificación."""
        return [e for e in self._entries.values() if e.status == "active"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de cuarentena."""
        total = len(self._entries)
        active = sum(1 for e in self._entries.values() if e.status == "active")
        verified = sum(1 for e in self._entries.values() if e.status == "verified")
        rejected = sum(1 for e in self._entries.values() if e.status == "rejected")
        expired = sum(1 for e in self._entries.values() if e.status == "expired")
        
        by_domain: Dict[str, int] = {}
        for entry in self._entries.values():
            if entry.status == "active":
                d = entry.domain or "unknown"
                by_domain[d] = by_domain.get(d, 0) + 1
        
        return {
            "total": total,
            "active": active,
            "verified": verified,
            "rejected": rejected,
            "expired": expired,
            "by_domain_active": by_domain,
            "promotion_rate": round(verified / max(1, total), 3),
            "rejection_rate": round(rejected / max(1, total), 3),
        }
