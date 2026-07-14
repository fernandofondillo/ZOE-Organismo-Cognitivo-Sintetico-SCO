"""
ZOE Multi-Tenant Support — Sprint 5.19 F5.2

Proporciona aislamiento de datos por tenant_id para despliegues multi-usuario.

Como funciona:
1. Cada request incluye un header `X-ZOE-Tenant` con el tenant_id.
2. El middleware extrae el tenant_id y lo inyecta en request['tenant_id'].
3. Los handlers usan request['tenant_id'] para filtrar memoria, identidad,
   trayectoria y capsulas por tenant.

Sin este header, se usa el tenant default 'default' (backward compatible).

Uso:
    curl -H "Authorization: Bearer TOKEN" -H "X-ZOE-Tenant: alice" http://localhost:8642/memory

En produccion, el Ingress Controller puede inyectar X-ZOE-Tenant basado en
el JWT del usuario o la API key usada.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from aiohttp import web

logger = logging.getLogger(__name__)

# Pattern valido para tenant_id: alphanumeric + underscore + hyphen, max 64 chars
_TENANT_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
_DEFAULT_TENANT = "default"


def get_tenant_id(request: web.Request) -> str:
    """Extrae el tenant_id de la request.

    Orden de precedencia:
    1. Header X-ZOE-Tenant
    2. Query param ?tenant=
    3. Default 'default'

    Returns:
        tenant_id validado y saneado.
    """
    # 1. Header
    tenant = request.headers.get("X-ZOE-Tenant", "")
    if not tenant:
        # 2. Query param
        tenant = request.query.get("tenant", "")
    if not tenant:
        # 3. Default
        return _DEFAULT_TENANT

    # Validar pattern
    if not _TENANT_PATTERN.match(tenant):
        logger.warning(f"Invalid tenant_id rejected: {tenant[:20]}...")
        return _DEFAULT_TENANT

    return tenant


@web.middleware
async def tenant_middleware(request: web.Request, handler):
    """Middleware que inyecta tenant_id en la request.

    Sprint 5.19 F5.2: Extrae X-ZOE-Tenant header o ?tenant= query param,
    lo valida, y lo inyecta en request['tenant_id'] para que los handlers
    puedan filtrar datos por tenant.
    """
    request['tenant_id'] = get_tenant_id(request)
    return await handler(request)
