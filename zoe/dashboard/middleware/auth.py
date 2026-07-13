"""Authentication middleware."""

import logging
from aiohttp import web

logger = logging.getLogger(__name__)

_HEALTH_PATHS = {"/health", "/ready", "/live"}


def create_auth_middleware(auth_token: str):
    """Factory que crea el auth middleware con el token configurado."""
    @web.middleware
    async def auth_middleware(request, handler):
        """Authentication: token required for all non-health endpoints."""
        if request.path not in _HEALTH_PATHS:
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
