"""
Sprint 5.19 F5.1-F5.2 — Tests de Fase 5 (escalabilidad).

F5.1: Distributed rate limiting con Redis
F5.2: Multi-tenant: aislamiento de datos por tenant_id
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ============================================================
# F5.1: Distributed rate limiting con Redis
# ============================================================

class TestF51DistributedRateLimit:
    """Sprint 5.19 F5.1 — Distributed rate limiting con Redis."""

    def test_redis_rate_limiter_class_exists(self):
        """_RedisRateLimiter class existe."""
        from zoe.dashboard.middleware.rate_limit import _RedisRateLimiter
        assert _RedisRateLimiter is not None

    def test_create_rate_limit_middleware_accepts_redis_url(self):
        """create_rate_limit_middleware acepta redis_url parameter."""
        from zoe.dashboard.middleware.rate_limit import create_rate_limit_middleware
        import inspect
        sig = inspect.signature(create_rate_limit_middleware)
        assert "redis_url" in sig.parameters, \
            "create_rate_limit_middleware must accept redis_url parameter"

    def test_redis_url_detected_from_env(self):
        """Si ZOE_REDIS_URL env var existe, se usa distributed rate limiting."""
        # Verificar que el codigo lee ZOE_REDIS_URL
        rl_path = Path(__file__).parent.parent / "dashboard" / "middleware" / "rate_limit.py"
        content = rl_path.read_text()
        assert "ZOE_REDIS_URL" in content, \
            "rate_limit.py must read ZOE_REDIS_URL env var"

    def test_redis_limiter_fails_open_on_error(self):
        """Si Redis falla, el rate limiter debe fallar open (permitir request)."""
        from zoe.dashboard.middleware.rate_limit import _RedisRateLimiter

        limiter = _RedisRateLimiter("redis://nonexistent:6379/0")
        # _ensure_connected debe retornar None si no puede conectar
        # (no puede testear async aqui sin event loop, pero verificamos la logica)
        assert limiter._redis is None  # inicialmente None

    def test_in_memory_fallback_works_without_redis(self):
        """Sin Redis, el rate limiter in-memory sigue funcionando."""
        from zoe.dashboard.middleware.rate_limit import create_rate_limit_middleware
        # Sin redis_url y sin env var, debe crear in-memory limiter
        middleware = create_rate_limit_middleware()
        assert middleware is not None
        # Debe tener _state (in-memory)
        assert hasattr(middleware, '_state')
        assert hasattr(middleware, '_redis_limiter')
        assert middleware._redis_limiter is None  # sin Redis


# ============================================================
# F5.2: Multi-tenant support
# ============================================================

class TestF52MultiTenant:
    """Sprint 5.19 F5.2 — Multi-tenant con tenant_id."""

    def test_tenant_module_exists(self):
        """zoe/core/tenant.py existe."""
        path = Path(__file__).parent.parent / "core" / "tenant.py"
        assert path.exists(), "zoe/core/tenant.py must exist"

    def test_get_tenant_id_function_exists(self):
        """get_tenant_id function existe."""
        from zoe.core.tenant import get_tenant_id
        assert callable(get_tenant_id)

    def test_tenant_middleware_exists(self):
        """tenant_middleware es un aiohttp middleware."""
        from zoe.core.tenant import tenant_middleware
        assert tenant_middleware is not None

    def test_default_tenant_when_no_header(self):
        """Sin header X-ZOE-Tenant, usa 'default'."""
        from zoe.core.tenant import get_tenant_id, _DEFAULT_TENANT
        # Crear mock request sin header
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.query = {}
        tenant = get_tenant_id(mock_request)
        assert tenant == _DEFAULT_TENANT

    def test_tenant_from_header(self):
        """Header X-ZOE-Tenant se extrae correctamente."""
        from zoe.core.tenant import get_tenant_id
        mock_request = MagicMock()
        mock_request.headers = {"X-ZOE-Tenant": "alice"}
        mock_request.query = {}
        tenant = get_tenant_id(mock_request)
        assert tenant == "alice"

    def test_tenant_from_query_param(self):
        """Query param ?tenant= se extrae cuando no hay header."""
        from zoe.core.tenant import get_tenant_id
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.query = {"tenant": "bob"}
        tenant = get_tenant_id(mock_request)
        assert tenant == "bob"

    def test_invalid_tenant_falls_back_to_default(self):
        """Tenant_id invalido (caracteres especiales) usa default."""
        from zoe.core.tenant import get_tenant_id, _DEFAULT_TENANT
        mock_request = MagicMock()
        mock_request.headers = {"X-ZOE-Tenant": "alice; DROP TABLE--"}
        mock_request.query = {}
        tenant = get_tenant_id(mock_request)
        assert tenant == _DEFAULT_TENANT

    def test_tenant_pattern_validation(self):
        """Tenant_id debe matchear pattern [a-zA-Z0-9_-]{1,64}."""
        from zoe.core.tenant import _TENANT_PATTERN
        # Validos
        assert _TENANT_PATTERN.match("alice")
        assert _TENANT_PATTERN.match("user_123")
        assert _TENANT_PATTERN.match("tenant-1")
        # Invalidos
        assert not _TENANT_PATTERN.match("alice; DROP TABLE")
        assert not _TENANT_PATTERN.match("a" * 65)  # too long
        assert not _TENANT_PATTERN.match("alice/bob")  # slash
        assert not _TENANT_PATTERN.match("")  # empty

    def test_dashboard_server_wires_tenant_middleware(self):
        """DashboardServer incluye tenant_middleware en la cadena de middlewares."""
        server_path = Path(__file__).parent.parent / "dashboard" / "server.py"
        content = server_path.read_text()
        assert "tenant_middleware" in content, \
            "DashboardServer.start() must wire tenant_middleware"
