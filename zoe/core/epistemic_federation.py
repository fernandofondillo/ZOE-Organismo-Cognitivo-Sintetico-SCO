"""
ZOE v1.1 — Epistemic Federation (Fase 6A, Opción 4)

Validación federada de conocimiento entre ZOEs.

El problema que resuelve:
- 100 ZOEs activas pueden aprender lo mismo 100 veces independientemente,
  cada una con su sesgo local.
- La federación epistémica convierte las ZOEs en revisores por pares:
  cuando una ZOE aprende algo y lo valida localmente, lo envía a peers
  con un knowledge_validation_request. Los peers responden confirmed,
  contradicted o unknown.

Protocolo:
1. ZOE-A valida localmente un claim (con CrossValidator o EpistemicValidator)
2. ZOE-A envía knowledge_validation_request a N peers
3. Cada peer responde:
   - confirmed: ya tenía el claim con confidence ≥0.7
   - contradicted: tiene evidencia contraria
   - unknown: no lo sabe
4. Si ≥2 peers confirman → confianza sube a 0.85, sale de cuarentena
5. Si algún peer contradice → conflicto, requiere validación científica externa
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeValidationRequest:
    """Solicitud de validación de conocimiento enviada a peers."""
    request_id: str
    claim: str
    source: str  # quién lo afirma inicialmente
    domain: Optional[str]
    confidence_local: float
    sender_id: str
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None  # firma criptográfica del sender
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "claim": self.claim[:500],
            "source": self.source,
            "domain": self.domain,
            "confidence_local": self.confidence_local,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


@dataclass
class KnowledgeValidationResponse:
    """Respuesta de un peer a una solicitud de validación."""
    request_id: str
    responder_id: str
    response: str  # "confirmed" | "contradicted" | "unknown"
    confidence: float  # confianza del responder en su respuesta
    evidence: Optional[str] = None  # explicación o referencia
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "responder_id": self.responder_id,
            "response": self.response,
            "confidence": round(self.confidence, 3),
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }


class EpistemicFederation:
    """
    Gestiona validación federada de conocimiento entre ZOEs.
    
    Integración:
    - Cuando ZOE valida localmente, llama a request_validation()
    - Los peers responden vía receive_validation_response()
    - Cuando se acumulan suficientes respuestas, se aplica el resultado
    """
    
    MIN_CONFIRMATIONS_FOR_PROMOTION = 2
    MIN_CONTRADICTIONS_FOR_REJECTION = 1
    CONFIDENCE_AFTER_FEDERATION = 0.85
    
    def __init__(self, organism_id: str):
        self.organism_id = organism_id
        
        # Requests enviados (esperando respuesta)
        self._pending_requests: Dict[str, KnowledgeValidationRequest] = {}
        
        # Responses recibidas por request_id
        self._responses: Dict[str, List[KnowledgeValidationResponse]] = {}
        
        # Validations que hemos respondido a otros
        self._responded: Dict[str, KnowledgeValidationResponse] = {}
        
        # Knowledge local indexado por hash del claim (para responder a otros)
        self._local_knowledge_index: Dict[str, Dict[str, Any]] = {}
        
        # Callback para enviar requests a peers (se registra externamente)
        self._send_to_peer: Optional[Any] = None  # Callable[[str, Dict], None]
        
        # Stats
        self.requests_sent = 0
        self.requests_received = 0
        self.confirmations_sent = 0
        self.contradictions_sent = 0
        self.unknowns_sent = 0
        self.promotions = 0
        self.rejections = 0
    
    def register_send_callback(self, callback) -> None:
        """Registra función para enviar requests a peers."""
        self._send_to_peer = callback
    
    def index_local_knowledge(
        self, claim_hash: str, entry: Dict[str, Any]
    ) -> None:
        """Indexa conocimiento local para responder a requests de otros."""
        self._local_knowledge_index[claim_hash] = entry
    
    def request_validation(
        self,
        claim: str,
        source: str,
        domain: Optional[str],
        confidence_local: float,
        peer_ids: List[str],
    ) -> str:
        """
        Envía solicitud de validación a peers.
        
        Returns:
            request_id para trackear respuestas
        """
        import hashlib
        request_id = f"req_{hashlib.md5(claim.encode()).hexdigest()[:12]}"
        
        request = KnowledgeValidationRequest(
            request_id=request_id,
            claim=claim,
            source=source,
            domain=domain,
            confidence_local=confidence_local,
            sender_id=self.organism_id,
        )
        
        self._pending_requests[request_id] = request
        self._responses[request_id] = []
        self.requests_sent += 1
        
        # Enviar a peers
        if self._send_to_peer:
            for peer_id in peer_ids:
                try:
                    self._send_to_peer(peer_id, request.to_dict())
                except Exception as e:
                    logger.warning(f"Failed to send validation request to {peer_id}: {e}")
        
        return request_id
    
    def receive_validation_request(
        self, request_data: Dict[str, Any]
    ) -> KnowledgeValidationResponse:
        """
        Recibe solicitud de validación de otro peer y responde.
        
        Responde según el conocimiento local indexado:
        - Si tiene el claim con confidence ≥0.7 → confirmed
        - Si tiene evidencia contraria → contradicted
        - Si no lo sabe → unknown
        """
        self.requests_received += 1
        
        request = KnowledgeValidationRequest(
            request_id=request_data["request_id"],
            claim=request_data["claim"],
            source=request_data.get("source", "unknown"),
            domain=request_data.get("domain"),
            confidence_local=request_data.get("confidence_local", 0.0),
            sender_id=request_data.get("sender_id", "unknown"),
            timestamp=request_data.get("timestamp", time.time()),
        )
        
        # Buscar en knowledge local
        import hashlib
        claim_hash = hashlib.md5(request.claim.encode()).hexdigest()
        local_entry = self._local_knowledge_index.get(claim_hash)
        
        if local_entry and local_entry.get("confidence", 0) >= 0.7:
            response = KnowledgeValidationResponse(
                request_id=request.request_id,
                responder_id=self.organism_id,
                response="confirmed",
                confidence=local_entry.get("confidence", 0.7),
                evidence=local_entry.get("provenance", "local_verified"),
            )
            self.confirmations_sent += 1
        elif local_entry and local_entry.get("contradicts", False):
            response = KnowledgeValidationResponse(
                request_id=request.request_id,
                responder_id=self.organism_id,
                response="contradicted",
                confidence=local_entry.get("confidence", 0.5),
                evidence=local_entry.get("contradicting_evidence", "local_contradiction"),
            )
            self.contradictions_sent += 1
        else:
            response = KnowledgeValidationResponse(
                request_id=request.request_id,
                responder_id=self.organism_id,
                response="unknown",
                confidence=0.0,
                evidence=None,
            )
            self.unknowns_sent += 1
        
        self._responded[request.request_id] = response
        return response
    
    def receive_validation_response(
        self, response_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Recibe respuesta de un peer. Si hay suficientes, aplica resultado.
        
        Returns:
            Dict con resultado si se completó la validación, None si pendiente
        """
        response = KnowledgeValidationResponse(
            request_id=response_data["request_id"],
            responder_id=response_data["responder_id"],
            response=response_data["response"],
            confidence=response_data.get("confidence", 0.0),
            evidence=response_data.get("evidence"),
        )
        
        if response.request_id not in self._responses:
            self._responses[response.request_id] = []
        
        self._responses[response.request_id].append(response)
        
        # Verificar si ya hay suficientes respuestas
        return self._check_completed(response.request_id)
    
    def _check_completed(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Verifica si una solicitud ha recibido suficientes respuestas."""
        responses = self._responses.get(request_id, [])
        request = self._pending_requests.get(request_id)
        
        if not request:
            return None
        
        confirmations = [r for r in responses if r.response == "confirmed"]
        contradictions = [r for r in responses if r.response == "contradicted"]
        unknowns = [r for r in responses if r.response == "unknown"]
        
        # Si hay contradicciones → rechazo
        if len(contradictions) >= self.MIN_CONTRADICTIONS_FOR_REJECTION:
            self.rejections += 1
            result = {
                "request_id": request_id,
                "status": "rejected",
                "reason": "federatively_contradicted",
                "confirmations": len(confirmations),
                "contradictions": len(contradictions),
                "unknowns": len(unknowns),
                "final_confidence": 0.0,
            }
            del self._pending_requests[request_id]
            return result
        
        # Si hay suficientes confirmaciones → promoción
        if len(confirmations) >= self.MIN_CONFIRMATIONS_FOR_PROMOTION:
            self.promotions += 1
            result = {
                "request_id": request_id,
                "status": "promoted",
                "reason": "federatively_validated",
                "confirmations": len(confirmations),
                "contradictions": len(contradictions),
                "unknowns": len(unknowns),
                "final_confidence": self.CONFIDENCE_AFTER_FEDERATION,
            }
            del self._pending_requests[request_id]
            return result
        
        # Pendiente
        return None
    
    def get_pending(self) -> List[Dict[str, Any]]:
        """Lista solicitudes pendientes de validación federada."""
        result = []
        for request_id, request in self._pending_requests.items():
            responses = self._responses.get(request_id, [])
            result.append({
                "request_id": request_id,
                "claim": request.claim[:200],
                "domain": request.domain,
                "responses_received": len(responses),
                "confirmations": sum(1 for r in responses if r.response == "confirmed"),
                "contradictions": sum(1 for r in responses if r.response == "contradicted"),
                "unknowns": sum(1 for r in responses if r.response == "unknown"),
            })
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "organism_id": self.organism_id,
            "requests_sent": self.requests_sent,
            "requests_received": self.requests_received,
            "confirmations_sent": self.confirmations_sent,
            "contradictions_sent": self.contradictions_sent,
            "unknowns_sent": self.unknowns_sent,
            "promotions": self.promotions,
            "rejections": self.rejections,
            "pending_requests": len(self._pending_requests),
            "local_knowledge_indexed": len(self._local_knowledge_index),
        }
