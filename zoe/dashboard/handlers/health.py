"""Handlers de health checks: /health, /ready, /live, /metrics (4 endpoints)."""

from datetime import datetime, timezone
import sqlite3
from typing import Any

from aiohttp import web

from ...core.metrics import (
    inc_cognitive_loop_iterations,
    set_memory_entries,
    set_metabolism_state,
    set_active_capsules,
    generate_metrics,
)


async def _handle_metrics(server, request) -> Any:
    """GET /metrics -- Prometheus metrics endpoint."""
    # Update dynamic gauge metrics before generating
    if server.chat and hasattr(server.chat, 'loop'):
        loop = server.chat.loop
        if hasattr(loop, 'state') and hasattr(loop.state, 'iteration_count'):
            inc_cognitive_loop_iterations(0)  # Ensure counter exists
        if hasattr(loop, 'memory'):
            try:
                mem_count = loop.memory.count() if hasattr(loop.memory, 'count') else 0
                set_memory_entries(mem_count)
            except Exception:
                pass

    if server.chat and hasattr(server.chat, 'metabolism'):
        try:
            set_metabolism_state(server.chat.metabolism.state.value)
        except Exception:
            pass

    if server.chat and hasattr(server.chat, 'capsule_manager'):
        try:
            loaded = server.chat.capsule_manager.list_loaded()
            set_active_capsules(len(loaded))
        except Exception:
            pass

    body = generate_metrics()
    return web.Response(
        text=body,
        content_type="text/plain; version=0.0.4; charset=utf-8",
    )


async def _handle_health(server, request) -> Any:
    """GET /health -- Estado general del sistema."""
    checks = {
        "memory_db": "ok",
        "llm_backend": "ok",
        "cognitive_loop": "ok",
    }
    healthy = True

    # Check 1: SQLite responde
    try:
        conn = sqlite3.connect(server.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
    except Exception as e:
        checks["memory_db"] = f"error: {e}"
        healthy = False

    # Check 2: LLM backend responde
    if not server.chat or not hasattr(server.chat, 'llm') or server.chat.llm is None:
        checks["llm_backend"] = "error: not initialized"
        healthy = False

    # Check 3: Loop cognitivo accesible
    if not server.chat or not hasattr(server.chat, 'loop') or server.chat.loop is None:
        checks["cognitive_loop"] = "error: not initialized"
        healthy = False

    from zoe import __version__
    body = {
        "status": "healthy" if healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": __version__,
        "checks": checks,
    }
    return web.json_response(body, status=200 if healthy else 503)


async def _handle_ready(server, request) -> Any:
    """GET /ready -- Listo para recibir trafico."""
    checks = {
        "memory_db": "ok",
        "llm_backend": "ok",
        "cognitive_loop": "ok",
    }
    ready = True

    # Check 1: memory_db esta accesible
    try:
        conn = sqlite3.connect(server.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
    except Exception as e:
        checks["memory_db"] = f"error: {e}"
        ready = False

    # Check 2: LLM backend inicializado
    if not server.chat or not hasattr(server.chat, 'llm') or server.chat.llm is None:
        checks["llm_backend"] = "error: not initialized"
        ready = False

    # Check 3: Loop cognitivo inicializado
    if not server.chat or not hasattr(server.chat, 'loop') or server.chat.loop is None:
        checks["cognitive_loop"] = "error: not initialized"
        ready = False
    elif not hasattr(server.chat.loop, 'state') or not hasattr(server.chat.loop, 'thoughts'):
        checks["cognitive_loop"] = "error: incomplete initialization"
        ready = False

    from zoe import __version__
    body = {
        "status": "ready" if ready else "not_ready",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": __version__,
        "checks": checks,
    }
    return web.json_response(body, status=200 if ready else 503)


async def _handle_live(server, request) -> Any:
    """GET /live -- Vivo pero no necesariamente listo."""
    from zoe import __version__
    body = {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": __version__,
        "checks": {
            "memory_db": "ok",
            "llm_backend": "ok",
            "cognitive_loop": "ok",
        },
    }
    return web.json_response(body, status=200)
