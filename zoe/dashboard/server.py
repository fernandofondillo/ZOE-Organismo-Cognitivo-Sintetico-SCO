"""
ZOE v1.0 -- Web Dashboard Server

Servidor HTTP + WebSocket que sirve el dashboard web de ZOE.
Permite comunicarse con ZOE desde el navegador en http://localhost:8642

Este modulo contiene la clase DashboardServer principal.
Los handlers HTTP estan organizados por dominio en handlers/.
"""

from __future__ import annotations

import asyncio
import logging
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from aiohttp import web

from .middleware.auth import create_auth_middleware
from .middleware.rate_limit import create_rate_limit_middleware
from .middleware.security_headers import security_headers_middleware
from .middleware.metrics import metrics_middleware
from .routes import register_routes

logger = logging.getLogger(__name__)


class DashboardServer:
    """
    Servidor del dashboard web de ZOE.

    Combina:
    - HTTP server (sirve el HTML del dashboard)
    - WebSocket server (comunicacion en tiempo real)
    - ZoeChat (organismo ZOE completo)
    """

    def __init__(
        self,
        backend: str = "mock",
        model: str = None,
        use_case: str = None,
        port: int = 8642,
        db_path: str = None,
        api_key: str = None,
        base_url: str = None,
        host: str = "127.0.0.1",
        auth_token: str = None,
    ):
        self.backend = backend
        self.model = model
        self.use_case = use_case
        self.port = port
        self.db_path = db_path or "zoe_data/dashboard_memory.db"
        self.api_key = api_key
        self.base_url = base_url
        self.host = host
        # SECURITY FIX: Auth is now MANDATORY by default.
        # Sprint 5.13 B6: NEVER log the auth_token. Only log that it was generated.
        if auth_token is None:
            self.auth_token = secrets.token_urlsafe(32)
            logger.warning(
                "SECURITY: No auth_token provided. Auto-generated token (hidden for security). "
                "Required for all endpoints except /, /manifest.json, /health, /ready, /live. "
                "Token persisted to data/dashboard_token.txt (chmod 0600) — read it from there."
            )
        else:
            self.auth_token = auth_token

        self.chat = None
        self.ws_clients: Set = set()
        self._app = None
        self._runner = None
        self._background_broadcaster = None
        # Sprint 5.17 F3.2: Track start time for /live liveness probe
        import time
        self._start_time = time.time()
        # Sprint 5.13 B4-bis — Bound _conversation_history to prevent memory leak.
        # Antes: List[Dict] = [] (unbounded, grows with every chat message).
        # Ahora: deque(maxlen=500) — keeps last 500 messages, discards oldest.
        from collections import deque
        self._conversation_history: deque = deque(maxlen=500)

        # Rate limiting (injected by middleware factory)
        self._rate_limit_middleware = None

        # Sprint 5.12 -- Persistir el token a un archivo para que los
        # lanzadores .command puedan leerlo y abrir el navegador con
        # ?token=XXX en la URL. Se guarda junto al db_path.
        try:
            data_dir = Path(self.db_path).parent if self.db_path else Path("zoe_data")
            data_dir.mkdir(parents=True, exist_ok=True)
            token_file = data_dir / "dashboard_token.txt"
            token_file.write_text(self.auth_token)
            # Permisos solo-lectura-dueno (0600) para no exponer el token
            try:
                token_file.chmod(0o600)
            except Exception:
                # Windows no soporta chmod Unix; ignoralo silenciosamente.
                pass
            logger.info("Auth token persisted to %s", token_file)
        except Exception as e:
            logger.warning("Could not persist auth token to disk: %s", e)


    async def initialize(self) -> None:
        """Inicializa ZOE y el servidor."""
        from zoe.cli_chat import ZoeChat

        self.chat = ZoeChat(
            backend=self.backend,
            model=self.model,
            use_case=self.use_case,
            db_path=self.db_path,
            api_key=self.api_key,
            base_url=self.base_url,
        )
        await self.chat.initialize()
        logger.info(f"ZOE initialized for dashboard: {self.chat.vault.identity_hash[:16]}...")


    async def start(self) -> None:
        """Inicia el servidor HTTP + WebSocket."""

        # Create middleware factories
        auth_middleware = create_auth_middleware(self.auth_token)
        self._rate_limit_middleware = create_rate_limit_middleware()

        # Sprint 5.19 F5.2: Tenant middleware para multi-tenant
        from ..core.tenant import tenant_middleware

        # Wire all middlewares: security headers -> metrics -> rate limit -> auth -> tenant
        app = web.Application(
            client_max_size=10 * 1024 * 1024,  # 10MB for file uploads
            middlewares=[
                security_headers_middleware,
                metrics_middleware,
                self._rate_limit_middleware,
                auth_middleware,
                tenant_middleware,
            ],
        )

        # Register all routes
        register_routes(app, self)

        self._app = app
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()

        # Start background broadcaster
        self._background_broadcaster = asyncio.create_task(self._broadcast_loop())

        logger.info(f"Dashboard server started on http://localhost:{self.port}")


    async def stop(self) -> None:
        """Detiene el servidor."""
        if self._background_broadcaster:
            self._background_broadcaster.cancel()
            try:
                await asyncio.wait_for(self._background_broadcaster, timeout=3.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass

        if self._runner:
            await self._runner.cleanup()

        if self.chat:
            await self.chat.shutdown()


    async def _broadcast_loop(self) -> None:
        """Bucle que envia estado + pensamientos a todos los WS clients cada 2s."""
        while True:
            await asyncio.sleep(2.0)

            if not self.ws_clients:
                continue

            # Estado del organismo
            await self._broadcast_state()

            # Pensamientos nuevos
            thoughts = self.chat._thoughts_while_idle
            if len(thoughts) > 0:
                for thought in thoughts:
                    await self._broadcast_to_all({
                        "type": "autonomous_thought",
                        "content": thought.content,
                        "trigger": thought.trigger,
                        "surprise": thought.surprise,
                        "system": thought.metadata.get("system", "system1"),
                        "timestamp": thought.timestamp,
                    })
                self.chat._thoughts_while_idle.clear()


    async def _broadcast_state(self) -> None:
        """Envia estado del organismo a todos los WS clients."""
        if not self.ws_clients or not self.chat:
            return

        s = self.chat.loop.state
        p = self.chat.loop.physics
        t = self.chat.loop.tensions
        m = self.chat.metabolism

        state_data = {
            "type": "state_update",
            "energy": s.energy,
            "fatigue": s.fatigue,
            "arousal": s.arousal,
            "attention": s.attention,
            "metabolism": m.state.value,
            "iterations": s.iteration_count,
            "thoughts_total": len(self.chat.loop.thoughts),
            "physics": p.to_dict(),
            "tensions": {name: t.to_dict() for name, t in t.tensions.items()},
        }

        await self._broadcast_to_all(state_data)


    async def _send_state_update(self, ws) -> None:
        """Envia estado a un WS client especifico."""
        try:
            s = self.chat.loop.state
            p = self.chat.loop.physics
            m = self.chat.metabolism
            t = self.chat.loop.tensions

            await ws.send_json({
                "type": "state_update",
                "energy": s.energy,
                "fatigue": s.fatigue,
                "arousal": s.arousal,
                "attention": s.attention,
                "metabolism": m.state.value,
                "iterations": s.iteration_count,
                "thoughts_total": len(self.chat.loop.thoughts),
                "physics": p.to_dict(),
                "tensions": {name: t.to_dict() for name, t in t.tensions.items()},
            })
        except Exception as e:
            logger.warning(f"Failed to send state update: {e}")


    async def _broadcast_to_all(self, data: dict) -> None:
        """Envia data a todos los WS clients."""
        dead = set()
        for ws in self.ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self.ws_clients -= dead


    async def _handle_command(self, cmd: str, data: dict) -> Any:
        """Maneja comandos especiales desde el WS."""
        if cmd == "stats":
            return self.chat.get_stats()
        elif cmd == "memory":
            return self.chat.get_memory()
        elif cmd == "identity":
            return self.chat.get_identity()
        elif cmd == "state":
            return self.chat.get_state()
        elif cmd == "sleep":
            self.chat.metabolism.internal_state.fatigue = 0.9
            self.chat.metabolism.tick(dt=1.0)
            return "ZOE is now sleeping."
        elif cmd == "wake":
            self.chat.metabolism.internal_state.fatigue = 0.0
            self.chat.metabolism.internal_state.energy = 1.0
            from zoe.metabolism.metabolism import MetabolicState
            self.chat.metabolism.state = MetabolicState.AWAKE
            return "ZOE is awake."
        return f"Unknown command: {cmd}"
