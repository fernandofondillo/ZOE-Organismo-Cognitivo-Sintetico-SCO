"""Handlers de mentor digital: /api/mentor/* (3 endpoints)."""

from typing import Any

from aiohttp import web


async def _handle_mentor_get(server, request) -> Any:
    """GET /api/mentor -- obtiene configuracion del mentor."""
    if not hasattr(server.chat, 'mentor'):
        return web.json_response({"error": "mentor not initialized"}, status=500)
    return web.json_response(server.chat.mentor.get_config())


async def _handle_mentor_update(server, request) -> Any:
    """POST /api/mentor -- actualiza configuracion del mentor."""
    if not hasattr(server.chat, 'mentor'):
        return web.json_response({"error": "mentor not initialized"}, status=500)
    data = await request.json()
    config = server.chat.mentor.update_config(data)
    return web.json_response({
        "success": True,
        "config": config.to_dict(),
    })


async def _handle_mentor_stats(server, request) -> Any:
    """GET /api/mentor/stats -- estadisticas del mentor."""
    if not hasattr(server.chat, 'mentor'):
        return web.json_response({"error": "mentor not initialized"}, status=500)
    return web.json_response(server.chat.mentor.get_stats())


