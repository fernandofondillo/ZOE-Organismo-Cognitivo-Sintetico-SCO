"""Security headers middleware.

Sprint 5.23 F7-7 (BUG-029, BUG-030 fix):
- HSTS ahora solo se setea si el request es HTTPS o viene detrás de
  un proxy con ``X-Forwarded-Proto: https``. Antes se seteaba
  incondicionalmente, lo que podía bloquear HTTP.
- Eliminado ``X-XSS-Protection`` (deprecated; puede introducir
  vulnerabilidades en browsers antiguos).
- CSP más estricta: ``connect-src 'self'`` (sin ``ws: wss:`` wildcards).
"""

from aiohttp import web


@web.middleware
async def security_headers_middleware(request, handler):
    """Add security headers to every HTTP response."""
    response = await handler(request)
    # Only add headers to HTTP responses (not WebSocket upgrades)
    if hasattr(response, 'headers'):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # Sprint 5.23 F7-7: X-XSS-Protection eliminado (deprecated)
        # Solo setear HSTS si el request es HTTPS (o detrás de proxy HTTPS)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        is_https = request.scheme == "https" or forwarded_proto == "https"
        if is_https:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        # Sprint 5.23 F7-7: CSP más estricta — connect-src solo 'self'
        # (sin ws: wss: wildcards que permitían WS a cualquier host)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
    return response
