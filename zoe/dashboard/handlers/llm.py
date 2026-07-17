"""Handlers de LLM: /llm, POST /llm (1 endpoint)."""

from typing import Any

from aiohttp import web


async def _handle_llm_switch(server, request) -> Any:
    """Cambia el LLM periferico en caliente."""
    from zoe.peripherals.llm import create_llm_peripheral

    data = await request.json()
    new_backend = data.get("backend", "mock")
    new_model = data.get("model")

    llm_config = {"backend": new_backend}
    if new_model:
        llm_config["model"] = new_model

    try:
        new_llm = create_llm_peripheral(llm_config)
        healthy = await new_llm.health_check()

        if healthy or new_backend == "mock":
            server.chat.llm = new_llm
            server.chat.speaker.llm = new_llm
            server.backend = new_backend
            server.model = new_model
            return web.json_response({
                "status": "switched",
                "backend": new_backend,
                "model": new_model,
            })
        else:
            return web.json_response({
                "status": "unhealthy",
                "backend": new_backend,
                "error": "LLM health check failed",
            }, status=503)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
