"""Security headers middleware."""

from aiohttp import web


@web.middleware
async def security_headers_middleware(request, handler):
    """Add security headers to every HTTP response."""
    response = await handler(request)
    # Only add headers to HTTP responses (not WebSocket upgrades)
    if hasattr(response, 'headers'):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
    return response
