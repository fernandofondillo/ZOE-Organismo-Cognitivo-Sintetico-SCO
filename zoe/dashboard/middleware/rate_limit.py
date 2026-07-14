"""Rate limiting middleware.

Sprint 5.12 -- Refactorizado a middleware funcional (no class-based) para
compatibilidad con aiohttp 3.13+. En aiohttp 3.13, los middlewares deben
ser funciones decoradas con @web.middleware, no instancias de clases con
@web.middleware en __call__.
"""

import collections
import logging
import time
from typing import Dict
from aiohttp import web

logger = logging.getLogger(__name__)

_HEALTH_PATHS = {"/health", "/ready", "/live", "/", "/manifest.json"}
_COSTLY_PATHS = {"/chat", "/feed", "/llm", "/api/models/optimize",
                 "/api/embodiment/compose", "/api/embodiment/bootstrap",
                 "/api/voice/start", "/ws"}
_RATE_LIMIT_NORMAL = 60   # requests per minute
_RATE_LIMIT_COSTLY = 10   # requests per minute
_RATE_LIMIT_WINDOW = 60.0  # seconds
_RATE_LIMIT_CLEANUP_EVERY = 100  # clean old entries every N requests


class _RateLimitState:
    """Estado compartido del rate limiter (una sola instancia por factory)."""

    def __init__(self):
        self.store: Dict[str, collections.deque] = {}
        self.request_count: int = 0

    def cleanup_stale_entries(self, now: float) -> None:
        """Remove stale IP entries older than the rate limit window."""
        stale_ips = [
            ip for ip, dq in self.store.items()
            if not dq or dq[-1][0] < now - _RATE_LIMIT_WINDOW
        ]
        for ip in stale_ips:
            del self.store[ip]
        if stale_ips:
            logger.debug("Rate limit cleanup: removed %d stale IP(s)", len(stale_ips))


def create_rate_limit_middleware():
    """Factory: crea un middleware funcional con estado propio.

    Uso:
        app = web.Application(middlewares=[create_rate_limit_middleware()])
    """
    state = _RateLimitState()

    @web.middleware
    async def rate_limit_middleware(request, handler):
        """Rate limiting by IP: 60 req/min normal, 10 req/min costly endpoints."""
        # Skip rate limiting for public paths (health, index, manifest)
        if request.path in _HEALTH_PATHS:
            return await handler(request)

        peer = request.remote or "unknown"
        now = time.monotonic()
        is_costly = any(request.path.startswith(p) for p in _COSTLY_PATHS)
        limit = _RATE_LIMIT_COSTLY if is_costly else _RATE_LIMIT_NORMAL

        # Get or create deque for this IP
        dq = state.store.get(peer)
        if dq is None:
            dq = collections.deque()
            state.store[peer] = dq

        # Remove entries older than the window
        while dq and dq[0][0] < now - _RATE_LIMIT_WINDOW:
            dq.popleft()

        # Count requests in current window
        count = sum(c for _, c in dq)

        if count >= limit:
            logger.warning(
                "Rate limit exceeded for IP %s on %s (%d/%d %s requests)",
                peer, request.path, count, limit,
                "costly" if is_costly else "normal",
            )
            return web.json_response(
                {"error": "too_many_requests", "retry_after": int(_RATE_LIMIT_WINDOW)},
                status=429,
                headers={"Retry-After": str(int(_RATE_LIMIT_WINDOW))},
            )

        # Record this request
        dq.append((now, 1))
        state.request_count += 1

        # Periodic cleanup of stale IP entries to prevent memory leak
        if state.request_count % _RATE_LIMIT_CLEANUP_EVERY == 0:
            state.cleanup_stale_entries(now)

        return await handler(request)

    # Attach state for inspection/testing
    rate_limit_middleware._state = state  # type: ignore[attr-defined]
    return rate_limit_middleware


# Backward compatibility -- allows existing code to import RateLimitMiddleware.
class RateLimitMiddleware:
    """DEPRECATED -- usa create_rate_limit_middleware() en su lugar.

    Sprint 5.12: esta clase se mantiene solo para compatibilidad con
    codigo que la importe directamente. Internamente delega a la
    implementacion funcional.
    """

    def __init__(self):
        self._state = _RateLimitState()
        # Build a function with the same closure pattern
        state = self._state

        @web.middleware
        async def _mw(request, handler):
            if request.path in _HEALTH_PATHS:
                return await handler(request)
            peer = request.remote or "unknown"
            now = time.monotonic()
            is_costly = any(request.path.startswith(p) for p in _COSTLY_PATHS)
            limit = _RATE_LIMIT_COSTLY if is_costly else _RATE_LIMIT_NORMAL
            dq = state.store.get(peer)
            if dq is None:
                dq = collections.deque()
                state.store[peer] = dq
            while dq and dq[0][0] < now - _RATE_LIMIT_WINDOW:
                dq.popleft()
            count = sum(c for _, c in dq)
            if count >= limit:
                logger.warning(
                    "Rate limit exceeded for IP %s on %s (%d/%d %s requests)",
                    peer, request.path, count, limit,
                    "costly" if is_costly else "normal",
                )
                return web.json_response(
                    {"error": "too_many_requests", "retry_after": int(_RATE_LIMIT_WINDOW)},
                    status=429,
                    headers={"Retry-After": str(int(_RATE_LIMIT_WINDOW))},
                )
            dq.append((now, 1))
            state.request_count += 1
            if state.request_count % _RATE_LIMIT_CLEANUP_EVERY == 0:
                state.cleanup_stale_entries(now)
            return await handler(request)

        # When called as middleware (app = web.Application(middlewares=[instance])),
        # aiohttp 3.13+ expects a callable that takes (request, handler). We expose
        # the decorated function as __call__ so the instance behaves as a middleware.
        self.__call__ = _mw  # type: ignore[assignment]
