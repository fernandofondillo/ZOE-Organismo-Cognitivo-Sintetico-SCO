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

    # Check 1: Memory DB responde
    # Sprint 5.17 F3.3: Detectar si es SQLite o PostgreSQL.
    # Sprint 5.16 F2.6: Usar asyncio.to_thread para no bloquear el event loop.
    storage_type = os.environ.get("ZOE_STORAGE_TYPE", "sqlite").lower()
    checks["storage_type"] = storage_type

    try:
        import asyncio
        if storage_type == "postgres":
            # PostgreSQL check
            def _check_postgres():
                import asyncpg
                import asyncio as _asyncio
                # asyncpg es async, pero estamos en thread sync.
                # Usar asyncio.run dentro del thread.
                async def _pg_check():
                    conn = await asyncpg.connect(
                        host=os.environ.get("POSTGRES_HOST", "localhost"),
                        port=int(os.environ.get("POSTGRES_PORT", "5432")),
                        database=os.environ.get("POSTGRES_DB", "zoe"),
                        user=os.environ.get("POSTGRES_USER", "zoe"),
                        password=os.environ.get("POSTGRES_PASSWORD", ""),
                    )
                    try:
                        await conn.fetchval("SELECT 1")
                    finally:
                        await conn.close()
                _asyncio.run(_pg_check())
            await asyncio.to_thread(_check_postgres)
        else:
            # SQLite check
            def _check_sqlite():
                conn = sqlite3.connect(server.db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                finally:
                    conn.close()
            await asyncio.to_thread(_check_sqlite)
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
    # Sprint 5.17 F3.3: Detectar si es SQLite o PostgreSQL.
    # Sprint 5.16 F2.6: Usar asyncio.to_thread para no bloquear el event loop.
    storage_type = os.environ.get("ZOE_STORAGE_TYPE", "sqlite").lower()
    checks["storage_type"] = storage_type

    try:
        import asyncio
        if storage_type == "postgres":
            def _check_postgres():
                import asyncpg
                import asyncio as _asyncio
                async def _pg_check():
                    conn = await asyncpg.connect(
                        host=os.environ.get("POSTGRES_HOST", "localhost"),
                        port=int(os.environ.get("POSTGRES_PORT", "5432")),
                        database=os.environ.get("POSTGRES_DB", "zoe"),
                        user=os.environ.get("POSTGRES_USER", "zoe"),
                        password=os.environ.get("POSTGRES_PASSWORD", ""),
                    )
                    try:
                        await conn.fetchval("SELECT 1")
                    finally:
                        await conn.close()
                _asyncio.run(_pg_check())
            await asyncio.to_thread(_check_postgres)
        else:
            def _check_sqlite():
                conn = sqlite3.connect(server.db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                finally:
                    conn.close()
            await asyncio.to_thread(_check_sqlite)
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
    """GET /live -- Liveness probe real.

    Sprint 5.17 F3.2: Antes /live siempre devolvia 200 sin checks reales.
    Ahora verifica:
    1. El proceso responde (implicito al servir la request)
    2. El cognitive loop ha avanzado (iteration_count > 0 o < 60s desde start)
    3. Memoria del proceso disponible (no OOM inminente)
    4. Disco disponible para SQLite (no disk full)
    """
    from zoe import __version__
    import time

    checks = {}
    alive = True

    # Check 1: Cognitive loop ha avanzado
    try:
        if server.chat and hasattr(server.chat, 'loop') and server.chat.loop:
            iter_count = server.chat.loop.state.iteration_count
            checks["cognitive_loop_iterations"] = iter_count
            # Si 0 iteraciones y el servidor lleva >60s corriendo, algo esta mal
            if iter_count == 0 and hasattr(server, '_start_time'):
                uptime = time.time() - server._start_time
                if uptime > 60:
                    checks["cognitive_loop"] = "error: no iterations in 60s+ uptime"
                    alive = False
                else:
                    checks["cognitive_loop"] = f"warming up ({uptime:.0f}s)"
            else:
                checks["cognitive_loop"] = "ok"
        else:
            checks["cognitive_loop"] = "error: not initialized"
            alive = False
    except Exception as e:
        checks["cognitive_loop"] = f"error: {e}"
        alive = False

    # Check 2: Memoria del proceso disponible (no OOM inminente)
    try:
        import psutil
        mem = psutil.virtual_memory()
        checks["memory_percent"] = mem.percent
        if mem.percent > 95:
            checks["memory"] = f"critical: {mem.percent:.1f}% used"
            alive = False
        elif mem.percent > 85:
            checks["memory"] = f"warning: {mem.percent:.1f}% used"
        else:
            checks["memory"] = "ok"
    except ImportError:
        checks["memory"] = "psutil not available"
    except Exception as e:
        checks["memory"] = f"error: {e}"

    # Check 3: Disco disponible para SQLite
    try:
        import shutil
        db_dir = os.path.dirname(server.db_path) if server.db_path else "."
        disk = shutil.disk_usage(db_dir)
        disk_percent = (disk.used / disk.total) * 100
        checks["disk_percent"] = disk_percent
        if disk_percent > 95:
            checks["disk"] = f"critical: {disk_percent:.1f}% used"
            alive = False
        elif disk_percent > 85:
            checks["disk"] = f"warning: {disk_percent:.1f}% used"
        else:
            checks["disk"] = "ok"
    except Exception as e:
        checks["disk"] = f"error: {e}"

    body = {
        "status": "alive" if alive else "not_alive",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": __version__,
        "checks": checks,
    }
    return web.json_response(body, status=200 if alive else 503)
