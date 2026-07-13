"""Handlers de model optimizer: /api/models/* (4 endpoints)."""

from typing import Any

from aiohttp import web


async def _handle_models_system_info(server, request) -> Any:
    """GET /api/models/system_info -- info del hardware."""
    from zoe.core.model_optimizer import ModelOptimizer
    opt = ModelOptimizer()
    return web.json_response(opt.get_system_info())


async def _handle_models_recommend(server, request) -> Any:
    """GET /api/models/recommend -- recomendaciones por nivel ACD."""
    from zoe.core.model_optimizer import ModelOptimizer
    opt = ModelOptimizer()
    return web.json_response(opt.recommend_for_acd())


async def _handle_models_catalog(server, request) -> Any:
    """GET /api/models/catalog -- catalogo de modelos compatibles."""
    from zoe.core.model_optimizer import ModelOptimizer
    opt = ModelOptimizer()
    models = opt.list_models_for_ram()
    return web.json_response({"models": models, "count": len(models)})


async def _handle_models_optimize(server, request) -> Any:
    """POST /api/models/optimize -- optimiza un modelo especifico."""
    from zoe.core.model_optimizer import ModelOptimizer
    data = await request.json()
    model_name = data.get("model", "qwen2.5:3b")
    opt = ModelOptimizer()
    result = opt.optimize(model_name)
    env = opt.generate_ollama_env(result)
    return web.json_response({
        "optimization": result.to_dict(),
        "ollama_env": env,
    })


