"""
ZOE v1.0 — Federation Protocol (Fase 4.4)

Protocolo HTTP/JSON para federación entre instancias de ZOE.

Servidor: recibe mensajes de otras ZOEs (register, sync, vote, broadcast)
Cliente: envía mensajes a otras ZOEs

Quorum federativo:
- Una mutación requiere ≥70% de aprobación para propagarse
- Cualquier Zoe puede vetar si viola valores (Identity Vault)
- Votos firmados criptográficamente (hash simple en Fase 4)

Endpoints del servidor:
- POST /register — una Zoe se registra como peer
- GET  /discover — lista de peers conocidos
- POST /sync_mutations — sincroniza mutaciones entre instancias
- POST /vote — vota sobre una mutación
- POST /broadcast — broadcast de evento a todas las ZOEs
- GET  /stats — estadísticas de la instancia
- POST /message — envía mensaje directo a esta Zoe
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FederationPeer:
    """Un peer en la federación."""
    peer_id: str
    host: str
    port: int
    identity_hash: str = ""  # hash del Identity Vault del peer
    registered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    status: str = "active"  # active | inactive | vetoed

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peer_id": self.peer_id,
            "host": self.host,
            "port": self.port,
            "identity_hash": self.identity_hash,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
            "status": self.status,
        }


@dataclass
class FederationVote:
    """Un voto sobre una mutación."""
    mutation_id: str
    voter_id: str
    vote: str  # "approve" | "reject" | "veto"
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    signature: str = ""  # hash simple del voto

    def compute_signature(self) -> str:
        data = f"{self.mutation_id}:{self.voter_id}:{self.vote}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "voter_id": self.voter_id,
            "vote": self.vote,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "signature": self.signature or self.compute_signature(),
        }


class FederationManager:
    """
    Gestiona la federación entre instancias de ZOE.

    Mantiene:
    - Lista de peers conocidos
    - Registro de votos por mutación
    - Quorum: ≥70% aprobación + veto por valores
    - Pool de mutaciones federadas
    """

    def __init__(
        self,
        organism_id: str = "zoe_default",
        host: str = "0.0.0.0",
        port: int = 8642,
        quorum_threshold: float = 0.7,
    ):
        self.organism_id = organism_id
        self.host = host
        self.port = port
        self.quorum_threshold = quorum_threshold

        self.peers: Dict[str, FederationPeer] = {}
        self.votes: Dict[str, List[FederationVote]] = {}  # mutation_id → votes
        self.broadcast_log: List[Dict[str, Any]] = []
        self.messages_received: List[Dict[str, Any]] = []

        # Estadísticas
        self.registrations_received: int = 0
        self.mutations_synced: int = 0
        self.votes_cast: int = 0
        self.broadcasts_sent: int = 0
        self.vetos_received: int = 0

    def register_peer(
        self,
        peer_id: str,
        host: str,
        port: int,
        identity_hash: str = "",
    ) -> Dict[str, Any]:
        """Registra un peer en la federación."""
        peer = FederationPeer(
            peer_id=peer_id,
            host=host,
            port=port,
            identity_hash=identity_hash,
        )
        self.peers[peer_id] = peer
        self.registrations_received += 1
        logger.info(f"Federation: peer {peer_id} registered at {host}:{port}")
        return {"status": "registered", "peer_id": peer_id}

    def discover_peers(self) -> List[Dict[str, Any]]:
        """Devuelve lista de peers conocidos."""
        return [p.to_dict() for p in self.peers.values() if p.status == "active"]

    def cast_vote(
        self,
        mutation_id: str,
        vote: str,
        reason: str = "",
    ) -> FederationVote:
        """Emite un voto sobre una mutación."""
        if vote not in ("approve", "reject", "veto"):
            raise ValueError(f"Invalid vote: {vote}")

        v = FederationVote(
            mutation_id=mutation_id,
            voter_id=self.organism_id,
            vote=vote,
            reason=reason,
        )
        v.signature = v.compute_signature()

        if mutation_id not in self.votes:
            self.votes[mutation_id] = []
        self.votes[mutation_id].append(v)
        self.votes_cast += 1

        if vote == "veto":
            self.vetos_received += 1
            logger.warning(f"Federation: VETO on {mutation_id} by {self.organism_id}: {reason}")

        return v

    def check_quorum(self, mutation_id: str) -> Tuple[bool, str]:
        """
        Verifica si una mutación tiene quorum suficiente.

        Returns:
            (has_quorum, reason)
        """
        votes = self.votes.get(mutation_id, [])

        # Si hay algún veto, no hay quorum
        vetos = [v for v in votes if v.vote == "veto"]
        if vetos:
            return False, f"vetoed by {len(vetos)} peer(s)"

        # Contar aprobaciones vs rechazos
        approvals = [v for v in votes if v.vote == "approve"]
        rejections = [v for v in votes if v.vote == "reject"]

        total_votes = len(approvals) + len(rejections)
        if total_votes == 0:
            return False, "no votes"

        approval_rate = len(approvals) / total_votes

        if approval_rate >= self.quorum_threshold:
            return True, f"quorum reached: {len(approvals)}/{total_votes} ({approval_rate:.0%})"
        else:
            return False, f"quorum not reached: {len(approvals)}/{total_votes} ({approval_rate:.0%})"

    def receive_vote(self, vote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recibe un voto de otra Zoe."""
        v = FederationVote(
            mutation_id=vote_data.get("mutation_id", ""),
            voter_id=vote_data.get("voter_id", ""),
            vote=vote_data.get("vote", ""),
            reason=vote_data.get("reason", ""),
            timestamp=vote_data.get("timestamp", time.time()),
            signature=vote_data.get("signature", ""),
        )

        mutation_id = v.mutation_id
        if mutation_id not in self.votes:
            self.votes[mutation_id] = []
        self.votes[mutation_id].append(v)

        if v.vote == "veto":
            self.vetos_received += 1

        return {"status": "vote_received", "mutation_id": mutation_id}

    def sync_mutation(self, mutation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recibe una mutación de otra Zoe para sincronización."""
        self.mutations_synced += 1
        mutation_id = mutation_data.get("id", "unknown")
        logger.info(f"Federation: mutation {mutation_id} synced from peer")
        return {"status": "synced", "mutation_id": mutation_id}

    def broadcast_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast de evento a todos los peers."""
        self.broadcasts_sent += 1
        event["broadcast_id"] = f"bc_{self.broadcasts_sent}"
        event["timestamp"] = time.time()
        event["sender"] = self.organism_id
        self.broadcast_log.append(event)
        return {"status": "broadcast", "recipients": len(self.peers)}

    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Recibe un mensaje directo de otra Zoe."""
        self.messages_received.append({
            **message,
            "received_at": time.time(),
        })
        return {"status": "received"}

    def get_stats(self) -> Dict[str, Any]:
        return {
            "organism_id": self.organism_id,
            "host": self.host,
            "port": self.port,
            "peers_count": len(self.peers),
            "active_peers": sum(1 for p in self.peers.values() if p.status == "active"),
            "registrations_received": self.registrations_received,
            "mutations_synced": self.mutations_synced,
            "votes_cast": self.votes_cast,
            "broadcasts_sent": self.broadcasts_sent,
            "vetos_received": self.vetos_received,
            "pending_quorums": sum(1 for mid in self.votes if not self.check_quorum(mid)[0]),
            "quorum_threshold": self.quorum_threshold,
        }

    def summary(self) -> str:
        return (
            f"FederationManager(peers={len(self.peers)}, "
            f"votes={self.votes_cast}, "
            f"vetos={self.vetos_received}, "
            f"synced={self.mutations_synced})"
        )


class FederationServer:
    """
    Servidor HTTP para federación.

    Usa aiohttp si disponible; si no, es un stub que procesa requests manualmente.
    """

    def __init__(self, manager: FederationManager):
        self.manager = manager
        self._app = None
        self._runner = None

    async def start(self) -> None:
        """Inicia el servidor HTTP."""
        try:
            from aiohttp import web

            app = web.Application()
            app.router.add_post("/register", self._handle_register)
            app.router.add_get("/discover", self._handle_discover)
            app.router.add_post("/sync_mutations", self._handle_sync)
            app.router.add_post("/vote", self._handle_vote)
            app.router.add_post("/broadcast", self._handle_broadcast)
            app.router.add_get("/stats", self._handle_stats)
            app.router.add_post("/message", self._handle_message)

            self._app = app
            self._runner = web.AppRunner(app)
            await self._runner.setup()
            site = web.TCPSite(self._runner, self.manager.host, self.manager.port)
            await site.start()
            logger.info(f"FederationServer started on {self.manager.host}:{self.manager.port}")
        except ImportError:
            logger.warning("aiohttp not available, FederationServer is stub")
        except Exception as e:
            logger.error(f"FederationServer failed to start: {e}")

    async def stop(self) -> None:
        """Detiene el servidor."""
        if self._runner:
            await self._runner.cleanup()
            logger.info("FederationServer stopped")

    async def _handle_register(self, request) -> web.Response:
        from aiohttp import web
        data = await request.json()
        result = self.manager.register_peer(
            peer_id=data.get("peer_id", ""),
            host=data.get("host", ""),
            port=data.get("port", 0),
            identity_hash=data.get("identity_hash", ""),
        )
        return web.json_response(result)

    async def _handle_discover(self, request) -> web.Response:
        from aiohttp import web
        return web.json_response({"peers": self.manager.discover_peers()})

    async def _handle_sync(self, request) -> web.Response:
        from aiohttp import web
        data = await request.json()
        result = self.manager.sync_mutation(data)
        return web.json_response(result)

    async def _handle_vote(self, request) -> web.Response:
        from aiohttp import web
        data = await request.json()
        result = self.manager.receive_vote(data)
        return web.json_response(result)

    async def _handle_broadcast(self, request) -> web.Response:
        from aiohttp import web
        data = await request.json()
        result = self.manager.broadcast_event(data)
        return web.json_response(result)

    async def _handle_stats(self, request) -> web.Response:
        from aiohttp import web
        return web.json_response(self.manager.get_stats())

    async def _handle_message(self, request) -> web.Response:
        from aiohttp import web
        data = await request.json()
        result = self.manager.receive_message(data)
        return web.json_response(result)


class FederationClient:
    """
    Cliente HTTP para federación.

    Envía mensajes a otras ZOEs.
    """

    def __init__(self, organism_id: str, host: str = "0.0.0.0", port: int = 8642):
        self.organism_id = organism_id
        self.host = host
        self.port = port

    async def register_with_peer(self, peer: FederationPeer, identity_hash: str = "") -> Dict[str, Any]:
        """Se registra con un peer."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{peer.url}/register",
                    json={
                        "peer_id": self.organism_id,
                        "host": self.host,
                        "port": self.port,
                        "identity_hash": identity_hash,
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return await resp.json()
        except Exception as e:
            logger.warning(f"Failed to register with {peer.url}: {e}")
            return {"status": "error", "error": str(e)}

    async def discover_peers(self, peer: FederationPeer) -> List[Dict[str, Any]]:
        """Descubre peers desde un peer conocido."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{peer.url}/discover",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    data = await resp.json()
                    return data.get("peers", [])
        except Exception as e:
            logger.warning(f"Failed to discover from {peer.url}: {e}")
            return []

    async def send_vote(self, peer: FederationPeer, vote: FederationVote) -> Dict[str, Any]:
        """Envía un voto a un peer."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{peer.url}/vote",
                    json=vote.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return await resp.json()
        except Exception as e:
            logger.warning(f"Failed to send vote to {peer.url}: {e}")
            return {"status": "error", "error": str(e)}

    async def broadcast_to_peers(
        self,
        peers: List[FederationPeer],
        event: Dict[str, Any],
    ) -> int:
        """Broadcast a todos los peers."""
        sent = 0
        for peer in peers:
            try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{peer.url}/broadcast",
                        json=event,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            sent += 1
            except Exception:
                pass
        return sent
