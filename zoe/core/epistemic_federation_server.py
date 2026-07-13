"""
ZOE v1.1 — Epistemic Federation Server/Client (Fase 6A, Opción 4 real)

Implementación real de la federación epistémica entre dos instancias ZOE
vía HTTP. Permite que una ZOE valide conocimiento consultando a peers.

Componentes:
- EpistemicFederationServer: endpoints HTTP para recibir validation requests
- EpistemicFederationClient: cliente que envía requests a peers
- Integración con Web Dashboard (rutas /federation/epistemic/*)
- Integración con KnowledgeQuarantine (promote/reject automático)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PeerEndpoint:
    """Endpoint de un peer ZOE para federación epistémica."""
    organism_id: str
    base_url: str  # ej. "http://zoe-2.local:8642"
    auth_token: Optional[str] = None
    last_seen: float = 0.0
    requests_sent: int = 0
    requests_received: int = 0
    confirmations_sent: int = 0
    contradictions_sent: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "organism_id": self.organism_id,
            "base_url": self.base_url,
            "last_seen": self.last_seen,
            "requests_sent": self.requests_sent,
            "requests_received": self.requests_received,
            "confirmations_sent": self.confirmations_sent,
            "contradictions_sent": self.contradictions_sent,
        }


class EpistemicFederationServer:
    """
    Servidor de federación epistémica.
    
    Expone endpoints HTTP para que otras ZOEs envíen:
    - POST /federation/epistemic/validate: knowledge_validation_request
    - GET /federation/epistemic/knowledge/{claim_hash}: consulta si tenemos un claim
    - POST /federation/epistemic/register: registrar peer
    - GET /federation/epistemic/peers: lista peers registrados
    
    Se integra con el Web Dashboard existente.
    """
    
    def __init__(self, federation_manager, quarantine=None):
        self.federation = federation_manager
        self.quarantine = quarantine
        self._peers: Dict[str, PeerEndpoint] = {}
    
    def register_peer(self, organism_id: str, base_url: str, auth_token: str = None) -> bool:
        """Registra un peer para federación epistémica."""
        self._peers[organism_id] = PeerEndpoint(
            organism_id=organism_id,
            base_url=base_url.rstrip("/"),
            auth_token=auth_token,
            last_seen=time.time(),
        )
        logger.info(f"Peer registered: {organism_id} @ {base_url}")
        return True
    
    def list_peers(self) -> List[Dict[str, Any]]:
        """Lista peers registrados."""
        return [p.to_dict() for p in self._peers.values()]
    
    async def handle_validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Endpoint: POST /federation/epistemic/validate
        
        Recibe knowledge_validation_request de un peer y responde.
        """
        try:
            # Procesar request vía EpistemicFederation
            response = self.federation.receive_validation_request(request_data)
            
            # Actualizar stats del peer si lo conocemos
            sender_id = request_data.get("sender_id")
            if sender_id in self._peers:
                self._peers[sender_id].requests_received += 1
                self._peers[sender_id].last_seen = time.time()
            
            return {
                "status": "ok",
                "response": response.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error handling validate request: {e}")
            return {"status": "error", "error": str(e)}
    
    async def handle_knowledge_query(self, claim_hash: str) -> Dict[str, Any]:
        """
        Endpoint: GET /federation/epistemic/knowledge/{claim_hash}
        
        Consulta si tenemos conocimiento sobre un claim (por hash).
        """
        entry = self.federation._local_knowledge_index.get(claim_hash)
        if entry:
            return {
                "found": True,
                "confidence": entry.get("confidence", 0),
                "provenance": entry.get("provenance", "unknown"),
                "contradicts": entry.get("contradicts", False),
            }
        return {"found": False}
    
    async def handle_register_peer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Endpoint: POST /federation/epistemic/register
        
        Registra un peer.
        """
        organism_id = data.get("organism_id")
        base_url = data.get("base_url")
        auth_token = data.get("auth_token")
        
        if not organism_id or not base_url:
            return {"status": "error", "error": "organism_id and base_url required"}
        
        self.register_peer(organism_id, base_url, auth_token)
        return {"status": "ok", "registered": organism_id}
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "peers_count": len(self._peers),
            "peers": self.list_peers(),
            "federation_stats": self.federation.get_stats(),
        }


class EpistemicFederationClient:
    """
    Cliente de federación epistémica.
    
    Envía knowledge_validation_request a peers vía HTTP y procesa respuestas.
    Se integra con CapsuleManager / KnowledgeQuarantine para promover/reject.
    """
    
    def __init__(self, federation_manager, quarantine=None, validator=None):
        self.federation = federation_manager
        self.quarantine = quarantine
        self.validator = validator
        self._peers: Dict[str, PeerEndpoint] = {}
    
    def add_peer(self, organism_id: str, base_url: str, auth_token: str = None) -> None:
        """Añade un peer para enviar requests."""
        self._peers[organism_id] = PeerEndpoint(
            organism_id=organism_id,
            base_url=base_url.rstrip("/"),
            auth_token=auth_token,
        )
    
    def remove_peer(self, organism_id: str) -> None:
        self._peers.pop(organism_id, None)
    
    def list_peers(self) -> List[str]:
        return list(self._peers.keys())
    
    async def request_validation_from_peers(
        self,
        claim: str,
        source: str,
        domain: Optional[str],
        confidence_local: float,
        quarantine_entry_id: Optional[str] = None,
        timeout_per_peer: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Envía knowledge_validation_request a todos los peers registrados.
        
        Returns:
            Dict con resultados agregados:
            - request_id: ID para trackear
            - responses: dict {peer_id: response}
            - confirmations: int
            - contradictions: int
            - unknowns: int
            - final_status: 'promoted' | 'rejected' | 'pending'
        """
        if not self._peers:
            return {
                "request_id": None,
                "responses": {},
                "confirmations": 0,
                "contradictions": 0,
                "unknowns": 0,
                "final_status": "no_peers",
            }
        
        # Crear request en el federation manager
        peer_ids = list(self._peers.keys())
        request_id = self.federation.request_validation(
            claim=claim,
            source=source,
            domain=domain,
            confidence_local=confidence_local,
            peer_ids=peer_ids,
        )
        
        # Enviar HTTP a cada peer en paralelo
        tasks = []
        for peer_id, peer in self._peers.items():
            tasks.append(self._send_to_peer(peer, claim, source, domain, confidence_local, request_id, timeout_per_peer))
        
        responses_raw = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar respuestas
        responses = {}
        for peer_id, raw in zip(peer_ids, responses_raw):
            if isinstance(raw, Exception):
                responses[peer_id] = {"response": "error", "error": str(raw)}
                # Tratar error como unknown
                self.federation.receive_validation_response({
                    "request_id": request_id,
                    "responder_id": peer_id,
                    "response": "unknown",
                    "confidence": 0.0,
                    "evidence": f"error: {raw}",
                })
            elif isinstance(raw, dict) and raw.get("status") == "ok":
                resp = raw.get("response", {})
                responses[peer_id] = resp
                # Alimentar al federation manager
                self.federation.receive_validation_response({
                    "request_id": request_id,
                    "responder_id": peer_id,
                    "response": resp.get("response", "unknown"),
                    "confidence": resp.get("confidence", 0),
                    "evidence": resp.get("evidence"),
                })
            else:
                responses[peer_id] = {"response": "unknown", "error": "invalid_response"}
                self.federation.receive_validation_response({
                    "request_id": request_id,
                    "responder_id": peer_id,
                    "response": "unknown",
                    "confidence": 0.0,
                })
        
        # Verificar si se completó
        final_result = self.federation._check_completed(request_id)
        
        # Si se completó y hay quarantine, aplicar
        if final_result and quarantine_entry_id and self.quarantine:
            if final_result["status"] == "promoted":
                self.quarantine.promote(
                    entry_id=quarantine_entry_id,
                    new_confidence=final_result["final_confidence"],
                    reason="federatively_validated",
                )
            elif final_result["status"] == "rejected":
                self.quarantine.reject(
                    entry_id=quarantine_entry_id,
                    contradicting_source="federation",
                    reason="federatively_contradicted",
                )
        
        # Si sigue pendiente, devolver estado
        if not final_result:
            responses_received = self.federation._responses.get(request_id, [])
            confirmations = sum(1 for r in responses_received if r.response == "confirmed")
            contradictions = sum(1 for r in responses_received if r.response == "contradicted")
            unknowns = sum(1 for r in responses_received if r.response == "unknown")
            final_status = "pending" if (confirmations < 2 and contradictions < 1) else "incomplete"
        else:
            confirmations = final_result.get("confirmations", 0)
            contradictions = final_result.get("contradictions", 0)
            unknowns = final_result.get("unknowns", 0)
            final_status = final_result["status"]
        
        return {
            "request_id": request_id,
            "responses": responses,
            "confirmations": confirmations,
            "contradictions": contradictions,
            "unknowns": unknowns,
            "final_status": final_status,
            "final_confidence": final_result.get("final_confidence") if final_result else None,
        }
    
    async def _send_to_peer(
        self,
        peer: PeerEndpoint,
        claim: str,
        source: str,
        domain: Optional[str],
        confidence_local: float,
        request_id: str,
        timeout: float,
    ) -> Dict[str, Any]:
        """Envía HTTP POST al peer."""
        try:
            import aiohttp
        except ImportError:
            return {"status": "error", "error": "aiohttp not available"}
        
        url = f"{peer.base_url}/federation/epistemic/validate"
        headers = {"Content-Type": "application/json"}
        if peer.auth_token:
            headers["Authorization"] = f"Bearer {peer.auth_token}"
        
        payload = {
            "request_id": request_id,
            "claim": claim,
            "source": source,
            "domain": domain,
            "confidence_local": confidence_local,
            "sender_id": self.federation.organism_id,
            "timestamp": time.time(),
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        peer.requests_sent += 1
                        peer.last_seen = time.time()
                        return data
                    else:
                        return {"status": "error", "error": f"HTTP {resp.status}", "body": await resp.text()}
        except asyncio.TimeoutError:
            return {"status": "error", "error": "timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "peers_count": len(self._peers),
            "peers": [p.to_dict() for p in self._peers.values()],
            "federation_stats": self.federation.get_stats(),
        }
