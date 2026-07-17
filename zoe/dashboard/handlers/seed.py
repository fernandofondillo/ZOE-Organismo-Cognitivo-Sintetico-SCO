"""Handlers de seed mode: /api/seed/* (6 endpoints)."""

from typing import Any

from aiohttp import web


def _get_zoe_seed(server):
    """Lazy-init del ZOESeed compartido."""
    from zoe.core.seed_mode import ZOESeed
    if not hasattr(server, '_zoe_seed'):
        server._zoe_seed = ZOESeed()
    return server._zoe_seed


async def _handle_seed_detect(server, request) -> Any:
    """GET /api/seed/detect -- busca semilla ZOE en volumenes montados."""
    seed = _get_zoe_seed(server)
    custom_paths = request.query.get("paths")
    paths = custom_paths.split(",") if custom_paths else None
    vol = seed.detect_seed_volume(custom_paths=paths)
    if vol:
        return web.json_response({
            "found": True,
            "volume": vol.to_dict(),
            "searched_paths": seed.list_seed_paths(),
        })
    return web.json_response({
        "found": False,
        "searched_paths": seed.list_seed_paths(),
    })


async def _handle_seed_inspect(server, request) -> Any:
    """GET /api/seed/inspect -- inspecciona semilla sin germinarla."""
    seed = _get_zoe_seed(server)
    custom_paths = request.query.get("paths")
    paths = custom_paths.split(",") if custom_paths else None
    result = seed.inspect(custom_paths=paths)
    return web.json_response(result)


async def _handle_seed_create(server, request) -> Any:
    """
    POST /api/seed/create -- crea una nueva semilla en un volumen.
    """
    from zoe.core.seed_mode import ZOESeed
    data = await request.json()
    seed = ZOESeed()
    report = seed.create(
        volume_path=data["volume_path"],
        organism_id=data["organism_id"],
        organism_name=data.get("organism_name", "ZOE"),
        version=data.get("version", "1.5.0"),
        required_capsules=data.get("required_capsules", []),
        optional_capsules=data.get("optional_capsules", []),
        default_use_case=data.get("default_use_case", "asistente_crece_contigo"),
        default_acd_level=data.get("default_acd_level", "L2_STANDARD"),
        language=data.get("language", "es"),
        min_ram_gb=data.get("min_ram_gb", 4.0),
        requires_ollama=data.get("requires_ollama", False),
        allows_cloud=data.get("allows_cloud", True),
    )
    return web.json_response(report.to_dict())


async def _handle_seed_germinate(server, request) -> Any:
    """
    POST /api/seed/germinate -- germina la semilla detectada.
    """
    seed = _get_zoe_seed(server)
    data = await request.json() if request.can_read_body else {}
    report = seed.germinate(
        custom_paths=data.get("paths"),
        acd_level=data.get("acd_level"),
        force_allow_cloud=data.get("force_allow_cloud", True),
    )
    return web.json_response(report.to_dict())


async def _handle_seed_stats(server, request) -> Any:
    """GET /api/seed/stats -- estadisticas del ZOESeed."""
    seed = _get_zoe_seed(server)
    return web.json_response(seed.get_stats())


async def _handle_seed_last_report(server, request) -> Any:
    """GET /api/seed/last_report -- ultimo reporte de germinacion."""
    seed = _get_zoe_seed(server)
    report = seed.get_last_report()
    if report is None:
        return web.json_response({"found": False})
    return web.json_response({"found": True, "report": report.to_dict()})


