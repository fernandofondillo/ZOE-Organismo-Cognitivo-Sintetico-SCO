"""
ZOE v2.1 — Dashboard handlers for ReflectionEngine

Endpoints:
  GET  /api/reflections         — Lista reflexiones recientes
  GET  /api/reflections/metrics — Métricas del engine (presupuesto, insights, costes)
  GET  /api/reflections/config  — Configuración actual del ReflectionEngine

Capa correcta: dashboard/ (presentación). No rompe separación de capas.
"""

import logging
from aiohttp import web

logger = logging.getLogger(__name__)


async def _handle_reflections_list(server, request: web.Request) -> web.Response:
    """GET /api/reflections — Lista reflexiones recientes autogeneradas."""
    try:
        # Obtener el reflection_engine desde el chat/loop si está disponible
        engine = _get_reflection_engine(server)
        if engine is None:
            return web.json_response({
                "status": "not_configured",
                "message": "ReflectionEngine not yet initialized. It will be available after the first SLEEPING cycle.",
                "count": 0,
                "reflections": [],
            })

        limit = int(request.query.get("limit", "10"))
        limit = min(max(limit, 1), 100)
        reflections = await engine.get_recent_reflections(limit=limit)
        return web.json_response({
            "status": "ok",
            "count": len(reflections),
            "reflections": reflections,
        })
    except Exception as e:
        logger.error("Error listing reflections: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_reflections_metrics(server, request: web.Request) -> web.Response:
    """GET /api/reflections/metrics — Métricas del ReflectionEngine."""
    try:
        engine = _get_reflection_engine(server)
        if engine is None:
            return web.json_response({
                "status": "not_configured",
                "message": "ReflectionEngine not yet initialized.",
            })

        metrics = engine.get_metrics()
        return web.json_response({
            "status": "ok",
            "metrics": metrics,
        })
    except Exception as e:
        logger.error("Error getting reflection metrics: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_reflections_config(server, request: web.Request) -> web.Response:
    """GET /api/reflections/config — Configuración actual del ReflectionEngine."""
    try:
        engine = _get_reflection_engine(server)
        if engine is None:
            return web.json_response({
                "status": "not_configured",
                "message": "ReflectionEngine not yet initialized.",
                "default_config": {
                    "model_tag": "qwq-32b-iq2",
                    "model_fallback_tag": "qwen2.5:14b-iq2",
                    "reflection_period_cycles": 1,
                    "max_reflections_per_cycle": 2,
                    "max_capsules_per_cycle": 3,
                    "salience_threshold": 0.6,
                    "reflection_timeout": 120.0,
                    "max_output_tokens": 512,
                    "daily_cloud_budget": 1.0,
                },
            })

        cfg = engine.config
        return web.json_response({
            "status": "ok",
            "config": {
                "model_tag": cfg.model_tag,
                "model_fallback_tag": cfg.model_fallback_tag,
                "reflection_period_cycles": cfg.reflection_period_cycles,
                "max_reflections_per_cycle": cfg.max_reflections_per_cycle,
                "max_capsules_per_cycle": cfg.max_capsules_per_cycle,
                "salience_threshold": cfg.salience_threshold,
                "max_fatigue_for_reflection": cfg.max_fatigue_for_reflection,
                "reflection_timeout": cfg.reflection_timeout,
                "max_input_tokens": cfg.max_input_tokens,
                "max_output_tokens": cfg.max_output_tokens,
                "daily_cloud_budget": cfg.daily_cloud_budget,
            },
        })
    except Exception as e:
        logger.error("Error getting reflection config: %s", e)
        return web.json_response({"error": str(e)}, status=500)


def _get_reflection_engine(server):
    """Obtiene el ReflectionEngine desde el servidor si está disponible.

    El engine se conecta lazy: durante la inicialización de ZoeChat,
    o durante el primer ciclo de SLEEPING.
    """
    try:
        # Path 1: Via chat.loop.reflection_engine (si está conectado al loop)
        if hasattr(server, 'chat') and server.chat is not None:
            if hasattr(server.chat, 'loop') and server.chat.loop is not None:
                loop = server.chat.loop
                if hasattr(loop, 'reflection_engine'):
                    return loop.reflection_engine
            # Path 2: Via chat.reflection_engine (directo)
            if hasattr(server.chat, 'reflection_engine'):
                return server.chat.reflection_engine
            # Path 3: Via chat.metabolism._reflection_hook
            if hasattr(server.chat, 'metabolism') and server.chat.metabolism is not None:
                metabolism = server.chat.metabolism
                if hasattr(metabolism, '_reflection_hook') and metabolism._reflection_hook is not None:
                    hook = metabolism._reflection_hook
                    if hasattr(hook, '_engine'):
                        return hook._engine
    except Exception:
        pass
    return None
