"""
ZOE Sprint 5.28 — Handler para /api/version

Endpoint que retorna la versión actual de ZOE.
"""

import logging
import subprocess
from aiohttp import web

logger = logging.getLogger(__name__)

# Sprint 5.28: versión canónica de ZOE
ZOE_VERSION = "2.1.2"
ZOE_SPRINT = "5.28"


def _get_git_commit() -> str:
    """Obtiene el hash corto del commit actual de git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=2,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


async def _handle_version(server, request: web.Request) -> web.Response:
    """
    GET /api/version — retorna versión, sprint y commit de ZOE.

    Response:
        {
            "version": "2.1.2",
            "sprint": "5.28",
            "commit": "abc1234",
            "python_version": "3.12.13",
            "backend": "anthropic",
            "model": "MiniMax-M3"
        }
    """
    import sys
    backend = getattr(server.chat, 'backend', 'unknown') if server.chat else 'unknown'
    model = getattr(server.chat, 'model', 'unknown') if server.chat else 'unknown'
    llm_type = type(server.chat.llm).__name__ if server.chat and server.chat.llm else 'none'

    return web.json_response({
        "version": ZOE_VERSION,
        "sprint": ZOE_SPRINT,
        "commit": _get_git_commit(),
        "python_version": sys.version.split()[0],
        "backend": backend,
        "model": model,
        "llm_type": llm_type,
    })
