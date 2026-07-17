"""Handlers de cuarentena: /api/quarantine/* (4 endpoints)."""

from typing import Any

from aiohttp import web


async def _handle_quarantine_list(server, request) -> Any:
    """GET /api/quarantine -- lista entries en cuarentena."""
    if not hasattr(server.chat, 'knowledge_quarantine'):
        return web.json_response({"error": "quarantine not initialized"}, status=500)
    active = server.chat.knowledge_quarantine.list_active()
    pending = server.chat.knowledge_quarantine.list_pending_verification()
    return web.json_response({
        "active": [e.to_dict() for e in active],
        "pending": [e.to_dict() for e in pending],
        "active_count": len(active),
        "pending_count": len(pending),
    })


async def _handle_quarantine_stats(server, request) -> Any:
    """GET /api/quarantine/stats -- stats de cuarentena."""
    if not hasattr(server.chat, 'knowledge_quarantine'):
        return web.json_response({"error": "quarantine not initialized"}, status=500)
    return web.json_response(server.chat.knowledge_quarantine.get_stats())


async def _handle_quarantine_promote(server, request) -> Any:
    """POST /api/quarantine/{entry_id}/promote -- promueve entrada manualmente."""
    if not hasattr(server.chat, 'knowledge_quarantine'):
        return web.json_response({"error": "quarantine not initialized"}, status=500)
    entry_id = request.match_info["entry_id"]
    data = await request.json()
    confidence = data.get("confidence", 0.75)
    result = server.chat.knowledge_quarantine.promote(entry_id, confidence, "manual_promotion")
    if result:
        return web.json_response({"success": True, "entry": result.to_dict()})
    return web.json_response({"success": False, "error": "entry not found"}, status=404)


async def _handle_quarantine_reject(server, request) -> Any:
    """POST /api/quarantine/{entry_id}/reject -- rechaza entrada manualmente."""
    if not hasattr(server.chat, 'knowledge_quarantine'):
        return web.json_response({"error": "quarantine not initialized"}, status=500)
    entry_id = request.match_info["entry_id"]
    data = await request.json()
    source = data.get("source", "manual")
    result = server.chat.knowledge_quarantine.reject(entry_id, source, "manual_rejection")
    if result:
        return web.json_response({"success": True, "entry": result.to_dict()})
    return web.json_response({"success": False, "error": "entry not found"}, status=404)


