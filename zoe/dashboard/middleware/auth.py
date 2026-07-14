"""Authentication middleware.

Sprint 5.12 -- Refinamiento de autenticacion del Dashboard:
- Las rutas PUBLICAS (HTML, manifest, health) NO requieren token.
  Esto permite al navegador cargar la pagina inicial sin 401.
- El HTML del dashboard, al cargarse, lee el token de:
    a) ?token=XXX en la URL (lanzar el navegador con esa URL)
    b) localStorage.getItem('zoe_auth_token') (sesion persistida)
- Las llamadas fetch/XHR desde el navegador envian
    Authorization: Bearer <token>
- El WebSocket pasa ?token=XXX en la query string.
- Si el navegador no tiene token, muestra un modal pidiendolo.
"""

import logging
from aiohttp import web

logger = logging.getLogger(__name__)

# Rutas publicas: sirven HTML, manifest o health checks.
# NO incluyen ningun endpoint de datos ni WebSocket.
_PUBLIC_PATHS = {
    "/",              # HTML del dashboard
    "/manifest.json", # PWA manifest
    "/health",        # Kubernetes liveness/readiness
    "/ready",
    "/live",
}


def create_auth_middleware(auth_token: str):
    """Factory que crea el auth middleware con el token configurado."""
    @web.middleware
    async def auth_middleware(request, handler):
        """Authentication: token required for all non-public endpoints."""
        if request.path in _PUBLIC_PATHS:
            return await handler(request)

        auth_header = request.headers.get("Authorization", "")
        # Also accept query param ?token= for WebSocket
        query_token = request.query.get("token", "")
        expected = f"Bearer {auth_token}"
        if auth_header != expected and query_token != auth_token:
            logger.warning(
                "Unauthorized request to %s from %s",
                request.path, request.remote or "unknown",
            )
            return web.json_response({"error": "unauthorized"}, status=401)
        return await handler(request)

    return auth_middleware
