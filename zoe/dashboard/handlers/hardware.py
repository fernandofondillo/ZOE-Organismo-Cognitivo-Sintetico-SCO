"""Handlers de hardware + ACD router + PWA manifest (8 endpoints)."""

import os
from pathlib import Path
from typing import Any

from aiohttp import web


async def _handle_hardware_ssds(server, request) -> Any:
    """GET /api/hardware/ssds -- SSDs portatiles recomendados."""
    from zoe.core.model_optimizer import ModelOptimizer
    ssds = ModelOptimizer.get_recommended_ssds()
    return web.json_response({
        "ssds": ssds,
        "count": len(ssds),
    })


async def _handle_hardware_token_rates(server, request) -> Any:
    """GET /api/hardware/token_rates -- velocidades esperadas por modelo."""
    from zoe.core.model_optimizer import ModelOptimizer
    rates = ModelOptimizer.get_expected_token_rates()
    return web.json_response({
        "token_rates": rates,
        "count": len(rates),
        "benchmark": {
            "hardware": "MacBook Air M2/M3 8GB",
            "ssd": "2000 MB/s USB-C",
            "cable": "USB 3.2 Gen 2 (cable corto original)",
            "note": "Con pendrive USB normal (400 MB/s), divide entre 3-5",
        },
    })


async def _handle_hardware_cable_warning(server, request) -> Any:
    """GET /api/hardware/cable_warning -- warning sobre el cable USB-C."""
    from zoe.core.model_optimizer import ModelOptimizer
    return web.json_response(ModelOptimizer.get_cable_warning())


async def _handle_hardware_system(server, request) -> Any:
    """GET /api/hardware/system -- info de hardware del host actual."""
    from zoe.core.model_optimizer import ModelOptimizer
    opt = ModelOptimizer()
    return web.json_response(opt.get_system_info())


async def _handle_router_stats(server, request) -> Any:
    """GET /api/router/stats -- estadisticas del ACD Model Router."""
    loop = server.chat.loop
    if hasattr(loop, "get_router_stats"):
        return web.json_response(loop.get_router_stats())
    return web.json_response({"enabled": False, "error": "router not available"})


async def _handle_router_installed(server, request) -> Any:
    """GET /api/router/installed -- lista modelos IQ2_M instalados en el SSD."""
    try:
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        models_dir = os.environ.get("OLLAMA_MODELS", "models")
        installed = []
        for key, m in OPTIMIZED_MODELS.items():
            local = Path(models_dir) / m.hf_filename
            if local.exists():
                installed.append({
                    "key": key,
                    "display_name": m.display_name,
                    "size_gb": m.size_gb,
                    "quantization": m.quantization,
                    "ollama_tag": m.ollama_tag,
                    "path": str(local),
                    "estimated_tokens_s": m.estimated_tokens_s,
                })
        return web.json_response({
            "models_dir": models_dir,
            "installed_count": len(installed),
            "installed": installed,
            "available_catalog": len(OPTIMIZED_MODELS),
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def _handle_router_profile(server, request) -> Any:
    """GET /api/router/profile -- perfil activo del ModelProfileRouter."""
    loop = server.chat.loop
    if hasattr(loop, "_active_profile") and loop._active_profile:
        profile = loop._active_profile
        return web.json_response(profile.to_dict())
    return web.json_response({
        "name": "none",
        "description": "ACD Router no activo. Ejecuta con --model auto.",
    })


async def _handle_manifest(server, request) -> Any:
    """GET /manifest.json -- PWA manifest para instalacion en movil."""
    manifest = {
        "name": "ZOE -- Synthetic Cognitive Organism",
        "short_name": "ZOE",
        "description": "Organismo cognitivo sintetico soberano",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a0f",
        "theme_color": "#7c4dff",
        "orientation": "any",
        "icons": [],
        "lang": "es",
        "categories": ["productivity", "utilities"],
    }
    return web.json_response(manifest)


