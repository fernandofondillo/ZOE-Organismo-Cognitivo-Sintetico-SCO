"""Rate limiting middleware.

Sprint 5.19 F5.1 -- Soporte opcional para distributed rate limiting con Redis.
Sprint 5.13 B7 -- Refactorizado a middleware funcional (no class-based) para
compatibilidad con aiohttp 3.13+.
"""

import collections
import logging
import os
import time
from typing import Dict, Optional
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


class _RedisRateLimiter:
    """Sprint 5.19 F5.1 -- Distributed rate limiter usando Redis.

    Usa el patron sliding window con sorted sets:
    - ZADD rate:{ip}:{path_type} {timestamp} {request_id}
    - ZREMRANGEBYSCORE para limpiar entries viejos
    - ZCARD para contar requests en la ventana

    Requiere: pip install redis>=4.0 (o redis[hiredis] para mejor rendimiento)
    """

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis = None
        self._connect_error_logged = False

    async def _ensure_connected(self):
        """Lazy connect a Redis."""
        if self._redis is not None:
            return self._redis
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            # Test connection
            await self._redis.ping()
            logger.info(f"Distributed rate limiter connected to Redis: {self._redis_url}")
            return self._redis
        except ImportError:
            if not self._connect_error_logged:
                logger.warning(
                    "Redis rate limiter: redis package not installed. "
                    "Install with: pip install redis. Falling back to in-memory."
                )
                self._connect_error_logged = True
            return None
        except Exception as e:
            if not self._connect_error_logged:
                logger.warning(
                    f"Redis rate limiter: cannot connect to {self._redis_url}: {e}. "
                    f"Falling back to in-memory."
                )
                self._connect_error_logged = True
            self._redis = None
            return None

    async def check_and_record(
        self,
        ip: str,
        path_type: str,
        limit: int,
        window: float,
    ) -> tuple:
        """Verifica y registra una request. Returns (allowed, current_count)."""
        redis = await self._ensure_connected()
        if redis is None:
            # Fallback: siempre permitir (el in-memory limiter manejara)
            return True, 0

        key = f"rate:{ip}:{path_type}"
        now = time.time()

        try:
            # Pipeline para atomicidad
            pipe = redis.pipeline()
            # 1. Remove entries older than window
            pipe.zremrangebyscore(key, 0, now - window)
            # 2. Count current entries
            pipe.zcard(key)
            # 3. Add this request
            pipe.zadd(key, {f"{now}:{os.urandom(4).hex()}": now})
            # 4. Set TTL on the key (cleanup)
            pipe.expire(key, int(window) + 10)
            results = await pipe.execute()

            count = results[1]  # zcard result (before adding this request)
            allowed = count < limit
            return allowed, count + 1
        except Exception as e:
            logger.warning(f"Redis rate limiter error: {e}. Allowing request (fail-open).")
            return True, 0

    async def close(self):
        """Cierra la conexion Redis."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None


def create_rate_limit_middleware(redis_url: Optional[str] = None):
    """Factory: crea un middleware funcional con estado propio.

    Sprint 5.19 F5.1: Si redis_url se proporciona (o ZOE_REDIS_URL env var existe),
    usa distributed rate limiting con Redis. Sino, usa in-memory (per-pod).

    Uso:
        # In-memory (single pod):
        app = web.Application(middlewares=[create_rate_limit_middleware()])

        # Distributed (multi-pod con Redis):
        app = web.Application(middlewares=[
            create_rate_limit_middleware(redis_url="redis://redis:6379/0")
        ])
    """
    state = _RateLimitState()

    # Sprint 5.19 F5.1: Detectar Redis URL
    if redis_url is None:
        redis_url = os.environ.get("ZOE_REDIS_URL")
    redis_limiter = _RedisRateLimiter(redis_url) if redis_url else None

    @web.middleware
    async def rate_limit_middleware(request, handler):
        """Rate limiting by IP: 60 req/min normal, 10 req/min costly endpoints.

        Sprint 5.19 F5.1: Si Redis esta configurado, usa distributed rate limiting
        compartido entre todos los pods. Sino, usa in-memory (per-pod).
        """
        # Skip rate limiting for public paths (health, index, manifest)
        if request.path in _HEALTH_PATHS:
            return await handler(request)

        peer = request.remote or "unknown"
        is_costly = any(request.path.startswith(p) for p in _COSTLY_PATHS)
        limit = _RATE_LIMIT_COSTLY if is_costly else _RATE_LIMIT_NORMAL
        path_type = "costly" if is_costly else "normal"

        # Sprint 5.19 F5.1: Distributed path (Redis)
        if redis_limiter is not None:
            allowed, count = await redis_limiter.check_and_record(
                peer, path_type, limit, _RATE_LIMIT_WINDOW
            )
            if not allowed:
                logger.warning(
                    "Rate limit exceeded for IP %s on %s (%d/%d %s requests) [Redis]",
                    peer, request.path, count, limit, path_type,
                )
                return web.json_response(
                    {"error": "too_many_requests", "retry_after": int(_RATE_LIMIT_WINDOW)},
                    status=429,
                    headers={"Retry-After": str(int(_RATE_LIMIT_WINDOW))},
                )
            return await handler(request)

        # In-memory path (single pod fallback)
        now = time.monotonic()

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
    rate_limit_middleware._redis_limiter = redis_limiter  # type: ignore[attr-defined]
    return rate_limit_middleware


# Backward compatibility -- allows existing code to import RateLimitMiddleware.
class RateLimitMiddleware:
    """DEPRECATED -- usa create_rate_limit_middleware() en su lugar."""

    def __init__(self):
        self._state = _RateLimitState()
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

        self.__call__ = _mw  # type: ignore[assignment]
