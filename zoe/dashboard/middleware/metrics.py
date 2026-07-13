"""Prometheus metrics instrumentation middleware."""

import time
from aiohttp import web
from ...core.metrics import (
    inc_requests_total,
    observe_request_duration,
)


@web.middleware
async def metrics_middleware(request, handler):
    """Prometheus instrumentation: count requests and measure latency."""
    # Skip instrumentation for /metrics itself to avoid recursion
    if request.path == "/metrics":
        return await handler(request)
    start = time.monotonic()
    try:
        response = await handler(request)
        status = str(response.status)
    except Exception:
        status = "500"
        raise
    finally:
        duration = time.monotonic() - start
        method = request.method
        endpoint = request.path
        observe_request_duration(method, endpoint, duration)
        inc_requests_total(method, endpoint, status)
    return response
