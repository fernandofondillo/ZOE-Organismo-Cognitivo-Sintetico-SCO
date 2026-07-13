"""
ZOE v2.1 — Dashboard handlers for ReflectionEngine

Endpoints:
  GET  /api/reflections         — Lista reflexiones recientes
  GET  /api/reflections/metrics — Métricas del engine
  GET  /api/reflections/config  — Configuración actual

Capa correcta: dashboard/ (presentación). No rompe separación de capas.
"""

import logging
from aiohttp import web

logger = logging.getLogger(__name__)


class ReflectionHandlers:
    """Handlers para endpoints de reflexión autónoma."""

    def __init__(self, reflection_engine=None):
        self._engine = reflection_engine

    def register(self, app: web.Application):
        """Registra rutas en la app aiohttp."""
        app.router.add_get("/api/reflections", self._handle_list)
        app.router.add_get("/api/reflections/metrics", self._handle_metrics)
        app.router.add_get("/api/reflections/config", self._handle_config)

    async def _handle_list(self, request: web.Request) -> web.Response:
        """GET /api/reflections — Lista reflexiones recientes."""
        if self._engine is None:
            return web.json_response(
                {"error": "ReflectionEngine not initialized"}, status=503
            )

        try:
            limit = int(request.query.get("limit", "10"))
            limit = min(max(limit, 1), 100)
            reflections = await self._engine.get_recent_reflections(limit=limit)
            return web.json_response({
                "count": len(reflections),
                "reflections": reflections,
            })
        except Exception as e:
            logger.error("Error listing reflections: %s", e)
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_metrics(self, request: web.Request) -> web.Response:
        """GET /api/reflections/metrics — Métricas del ReflectionEngine."""
        if self._engine is None:
            return web.json_response(
                {"error": "ReflectionEngine not initialized"}, status=503
            )

        try:
            metrics = self._engine.get_metrics()
            return web.json_response(metrics)
        except Exception as e:
            logger.error("Error getting reflection metrics: %s", e)
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_config(self, request: web.Request) -> web.Response:
        """GET /api/reflections/config — Configuración actual."""
        if self._engine is None:
            return web.json_response(
                {"error": "ReflectionEngine not initialized"}, status=503
            )

        try:
            cfg = self._engine.config
            return web.json_response({
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
            })
        except Exception as e:
            logger.error("Error getting reflection config: %s", e)
            return web.json_response({"error": str(e)}, status=500)
