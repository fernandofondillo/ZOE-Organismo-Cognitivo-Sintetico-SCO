"""Handlers de embodiment composer: /api/embodiment/* (6 endpoints)."""

from typing import Any

from aiohttp import web


def _get_embodiment_composer(server):
    """Lazy-init del composer compartido."""
    from zoe.core.embodiment_composer import EmbodimentComposer
    if not hasattr(server, '_embodiment_composer'):
        server._embodiment_composer = EmbodimentComposer()
    return server._embodiment_composer


async def _handle_embodiment_compose(server, request) -> Any:
    """
    POST /api/embodiment/compose -- instancia un cuerpo desde un plan.
    """
    from zoe.core.embodiment_composer import EmbodimentComposer
    from zoe.core.resource_planner import ResourcePlanner
    from zoe.peripherals.model_bus import ModelBus

    data = await request.json()
    composer = _get_embodiment_composer(server)

    # Si el usuario pasa un plan explicito, usarlo
    if "plan" in data:
        from zoe.core.resource_planner import ResourcePlan
        plan_data = data["plan"]
        plan = ResourcePlan(**plan_data)
    else:
        # Generar plan con ResourcePlanner
        planner = ResourcePlanner()
        bus = getattr(server, '_model_bus', None) or ModelBus()
        plan = planner.plan(
            acd_level=data.get("acd_level", "L2_STANDARD"),
            metabolic_state=data.get("metabolic_state", "awake"),
            sensitive_domain=data.get("sensitive_domain", False),
            available_ram_gb=data.get("available_ram_gb", 5.0),
            model_bus=bus,
        )

    emb = composer.compose(
        plan=plan,
        model_bus=getattr(server, '_model_bus', None),
        capsules=data.get("capsules"),
    )
    return web.json_response(emb.to_dict())


async def _handle_embodiment_bootstrap(server, request) -> Any:
    """
    POST /api/embodiment/bootstrap -- pipeline completo discover->bus->plan->compose.
    """
    composer = _get_embodiment_composer(server)
    data = await request.json() if request.can_read_body else {}

    emb = composer.bootstrap_from_scratch(
        acd_level=data.get("acd_level", "L2_STANDARD"),
        metabolic_state=data.get("metabolic_state", "awake"),
        sensitive_domain=data.get("sensitive_domain", False),
        available_ram_gb=data.get("available_ram_gb"),
        capsules=data.get("capsules"),
        memory_db_path=data.get("memory_db_path"),
    )
    return web.json_response(emb.to_dict())


async def _handle_embodiment_status(server, request) -> Any:
    """GET /api/embodiment/status -- estado global del composer."""
    composer = _get_embodiment_composer(server)
    return web.json_response(composer.get_status())


async def _handle_embodiment_list(server, request) -> Any:
    """GET /api/embodiment/list -- lista embodiments activos."""
    composer = _get_embodiment_composer(server)
    return web.json_response({"embodiments": composer.list_active()})


async def _handle_embodiment_tear_down(server, request) -> Any:
    """
    POST /api/embodiment/tear_down -- detiene un embodiment.
    """
    composer = _get_embodiment_composer(server)
    data = await request.json()

    if "embodiment_id" in data:
        ok = composer.tear_down(data["embodiment_id"])
        return web.json_response({"success": ok, "embodiment_id": data["embodiment_id"]})
    else:
        closed = composer.tear_down_all()
        return web.json_response({"success": True, "closed_count": closed})


async def _handle_embodiment_log(server, request) -> Any:
    """GET /api/embodiment/log -- log reciente de composiciones."""
    composer = _get_embodiment_composer(server)
    return web.json_response({"log": composer.get_composition_log()})


