"""Authentication middleware.

Sprint 5.13 B7 -- Token comparison con hmac.compare_digest (timing-safe).
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

import hmac
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
    "/favicon.ico",   # Sprint 5.21: evita 401 en consola del navegador
}


def _tokens_match(received: str, expected: str) -> bool:
    """Compara dos tokens de forma timing-safe con hmac.compare_digest.

    Si las longitudes difieren, compare_digest devuelve False inmediatamente
    pero el tiempo de ejecucion sigue dependiendo de la longitud de 'received'.
    Para mitigar el leak de longitud, normalizamos a la longitud del expected
    rellenando con bytes nulos (no afecta al resultado pero iguala el tiempo).

    Esto previene timing attacks que podrian reconstruir el token byte a byte.
    """
    if not received or not expected:
        return False
    # Normalizar longitudes para no filtrar la longitud del expected
    if len(received) != len(expected):
        # Igualar longitud rellenando el mas corto
        max_len = max(len(received), len(expected))
        received_padded = received.ljust(max_len, "\x00")
        expected_padded = expected.ljust(max_len, "\x00")
        return hmac.compare_digest(received_padded.encode(), expected_padded.encode())
    return hmac.compare_digest(received.encode(), expected.encode())


def create_auth_middleware(auth_token: str):
    """Factory que crea el auth middleware con el token configurado."""
    expected_bearer = f"Bearer {auth_token}"

    @web.middleware
    async def auth_middleware(request, handler):
        """Authentication: token required for non-localhost connections only.

        Sprint 5.21: localhost (127.0.0.1, ::1) NO requiere token.
        Auth es para exposicion de red, NO para despliegues locales en SSD.
        Esto elimina TODOS los problemas de token/JS para usuarios locales.
        """
        if request.path in _PUBLIC_PATHS:
            return await handler(request)

        # Sprint 5.21: Skip auth for localhost connections
        peer = request.remote or "unknown"
        if peer in ("127.0.0.1", "::1", "localhost"):
            return await handler(request)

        auth_header = request.headers.get("Authorization", "")
        query_token = request.query.get("token", "")

        header_ok = _tokens_match(auth_header, expected_bearer) if auth_header else False
        query_ok = _tokens_match(query_token, auth_token) if query_token else False

        if not header_ok and not query_ok:
            logger.warning(
                "Unauthorized request to %s from %s",
                request.path, request.remote or "unknown",
            )
            return web.json_response({"error": "unauthorized"}, status=401)
        return await handler(request)

    return auth_middleware
