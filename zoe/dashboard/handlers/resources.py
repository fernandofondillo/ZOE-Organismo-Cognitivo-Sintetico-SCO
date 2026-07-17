"""Handlers de recursos: /api/resources/*, /api/modelbus/*, /api/planner/* (9 endpoints)."""

import logging
from typing import Any

from aiohttp import web

logger = logging.getLogger(__name__)


async def _handle_resources_graph(server, request) -> Any:
    """GET /api/resources -- grafo de recursos disponibles."""
    from zoe.peripherals.resource_discovery import ResourceDiscoverySense
    sense = getattr(server, '_resource_sense', None)
    if not sense:
        sense = ResourceDiscoverySense()
        await sense.observe()
        server._resource_sense = sense
    return web.json_response(sense.get_graph().to_dict())


async def _handle_resources_stats(server, request) -> Any:
    """GET /api/resources/stats -- estadisticas de recursos."""
    from zoe.peripherals.resource_discovery import ResourceDiscoverySense
    sense = getattr(server, '_resource_sense', None)
    if not sense:
        sense = ResourceDiscoverySense()
        await sense.observe()
        server._resource_sense = sense
    return web.json_response(sense.get_stats())


async def _handle_resources_scan(server, request) -> Any:
    """POST /api/resources/scan -- ejecuta un nuevo scan."""
    from zoe.peripherals.resource_discovery import ResourceDiscoverySense
    sense = getattr(server, '_resource_sense', None)
    if not sense:
        sense = ResourceDiscoverySense()
        server._resource_sense = sense
    await sense.observe()
    return web.json_response({
        "success": True,
        "stats": sense.get_stats(),
        "graph": sense.get_graph().to_dict(),
    })


def _get_model_bus(server):
    """Sprint 5.7.3 -- Lazy-init del ModelBus."""
    if not hasattr(server, '_model_bus') or server._model_bus is None:
        try:
            from zoe.peripherals.model_bus import ModelBus
            server._model_bus = ModelBus()
        except Exception as e:
            logger.debug(f"ModelBus init failed: {e}")
            server._model_bus = None
    return server._model_bus


async def _handle_modelbus_list(server, request) -> Any:
    """GET /api/modelbus -- lista backends del ModelBus."""
    bus = _get_model_bus(server)
    if not bus:
        return web.json_response({"error": "model_bus not available", "backends": []})
    return web.json_response({"backends": bus.list_backends()})


async def _handle_modelbus_stats(server, request) -> Any:
    """GET /api/modelbus/stats -- estadisticas del ModelBus."""
    bus = _get_model_bus(server)
    if not bus:
        return web.json_response({"error": "model_bus not available"})
    return web.json_response(bus.get_stats())


async def _handle_modelbus_select(server, request) -> Any:
    """POST /api/modelbus/select -- selecciona backend optimo."""
    bus = _get_model_bus(server)
    if not bus:
        return web.json_response({"error": "model_bus not available"})
    data = await request.json()
    selected = bus.select_backend(
        acd_level=data.get("acd_level"),
        sensitive_domain=data.get("sensitive_domain", False),
        prefer_local=data.get("prefer_local", False),
    )
    if selected:
        return web.json_response({"selected": selected.to_dict()})
    return web.json_response({"selected": None, "reason": "no backends available"})


def _get_resource_planner(server):
    """Sprint 5.7.3 -- Lazy-init del ResourcePlanner."""
    if not hasattr(server, '_resource_planner') or server._resource_planner is None:
        try:
            from zoe.core.resource_planner import ResourcePlanner
            server._resource_planner = ResourcePlanner()
        except Exception as e:
            logger.debug(f"ResourcePlanner init failed: {e}")
            server._resource_planner = None
    return server._resource_planner


async def _handle_planner_plan(server, request) -> Any:
    """POST /api/planner/plan -- genera un plan de ejecucion."""
    data = await request.json()
    planner = _get_resource_planner(server)
    if not planner:
        return web.json_response({"error": "planner not available"})
    plan = planner.plan(
        acd_level=data.get("acd_level", "L2_STANDARD"),
        metabolic_state=data.get("metabolic_state", "awake"),
        sensitive_domain=data.get("sensitive_domain", False),
        available_ram_gb=data.get("available_ram_gb", 5.0),
    )
    return web.json_response(plan.to_dict())


async def _handle_planner_stats(server, request) -> Any:
    """GET /api/planner/stats -- estadisticas del planner."""
    planner = _get_resource_planner(server)
    if not planner:
        return web.json_response({"error": "planner not available"})
    return web.json_response(planner.get_stats())


async def _handle_planner_recommend(server, request) -> Any:
    """GET /api/planner/recommend -- recomendaciones de modelos por nivel ACD."""
    from zoe.core.resource_planner import ResourcePlanner
    planner = ResourcePlanner()
    result = planner.recommend_model_setup(available_ram_gb=5.0)
    return web.json_response(result)
