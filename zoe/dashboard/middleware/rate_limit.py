"""Rate limiting middleware."""

import collections
import logging
import time
from typing import Dict
from aiohttp import web

logger = logging.getLogger(__name__)

_HEALTH_PATHS = {"/health", "/ready", "/live"}
_COSTLY_PATHS = {"/chat", "/feed", "/llm", "/api/models/optimize",
                 "/api/embodiment/compose", "/api/embodiment/bootstrap",
                 "/api/voice/start", "/ws"}
_RATE_LIMIT_NORMAL = 60   # requests per minute
_RATE_LIMIT_COSTLY = 10   # requests per minute
_RATE_LIMIT_WINDOW = 60.0  # seconds
_RATE_LIMIT_CLEANUP_EVERY = 100  # clean old entries every N requests


class RateLimitMiddleware:
    """Rate limiting middleware with in-memory per-IP tracking."""

    def __init__(self):
        self._rate_limit_store: Dict[str, collections.deque] = {}
        self._rate_limit_request_count = 0

    def _cleanup_stale_entries(self, now: float) -> None:
        """Remove stale IP entries older than the rate limit window."""
        stale_ips = [
            ip for ip, dq in self._rate_limit_store.items()
            if not dq or dq[-1][0] < now - _RATE_LIMIT_WINDOW
        ]
        for ip in stale_ips:
            del self._rate_limit_store[ip]
        if stale_ips:
            logger.debug("Rate limit cleanup: removed %d stale IP(s)", len(stale_ips))

    @web.middleware
    async def __call__(self, request, handler):
        """Rate limiting by IP: 60 req/min normal, 10 req/min costly endpoints."""
        # Skip rate limiting for health checks
        if request.path in _HEALTH_PATHS:
            return await handler(request)

        peer = request.remote or "unknown"
        now = time.monotonic()
        is_costly = any(request.path.startswith(p) for p in _COSTLY_PATHS)
        limit = _RATE_LIMIT_COSTLY if is_costly else _RATE_LIMIT_NORMAL

        # Get or create deque for this IP
        dq = self._rate_limit_store.get(peer)
        if dq is None:
            dq = collections.deque()
            self._rate_limit_store[peer] = dq

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
        self._rate_limit_request_count += 1

        # Periodic cleanup of stale IP entries to prevent memory leak
        if self._rate_limit_request_count % _RATE_LIMIT_CLEANUP_EVERY == 0:
            self._cleanup_stale_entries(now)

        return await handler(request)


def create_rate_limit_middleware():
    """Factory: crea una instancia del rate limit middleware."""
    rl = RateLimitMiddleware()
    return rl
