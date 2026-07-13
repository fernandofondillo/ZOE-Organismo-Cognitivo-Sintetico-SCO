"""Handlers de federacion epistemica: /federation/* (6 endpoints)."""

from typing import Any

from aiohttp import web


async def _handle_epistemic_validate(server, request) -> Any:
    """POST /federation/epistemic/validate -- recibe validation request de peer."""
    data = await request.json()
    if not hasattr(server.chat, 'epistemic_federation_server'):
        return web.json_response({"error": "federation server not initialized"}, status=500)
    result = await server.chat.epistemic_federation_server.handle_validate_request(data)
    return web.json_response(result)


async def _handle_epistemic_knowledge(server, request) -> Any:
    """GET /federation/epistemic/knowledge/{claim_hash} -- consulta local knowledge."""
    claim_hash = request.match_info["claim_hash"]
    if not hasattr(server.chat, 'epistemic_federation_server'):
        return web.json_response({"error": "federation server not initialized"}, status=500)
    result = await server.chat.epistemic_federation_server.handle_knowledge_query(claim_hash)
    return web.json_response(result)


async def _handle_epistemic_register(server, request) -> Any:
    """POST /federation/epistemic/register -- registra peer."""
    data = await request.json()
    if not hasattr(server.chat, 'epistemic_federation_server'):
        return web.json_response({"error": "federation server not initialized"}, status=500)
    result = await server.chat.epistemic_federation_server.handle_register_peer(data)
    return web.json_response(result)


async def _handle_epistemic_peers(server, request) -> Any:
    """GET /federation/epistemic/peers -- lista peers."""
    if not hasattr(server.chat, 'epistemic_federation_server'):
        return web.json_response({"error": "federation server not initialized"}, status=500)
    return web.json_response({"peers": server.chat.epistemic_federation_server.list_peers()})


async def _handle_epistemic_stats(server, request) -> Any:
    """GET /federation/epistemic/stats -- stats de federacion epistemica."""
    if not hasattr(server.chat, 'epistemic_federation_server'):
        return web.json_response({"error": "federation server not initialized"}, status=500)
    return web.json_response(server.chat.epistemic_federation_server.get_stats())


async def _handle_epistemic_request_validation(server, request) -> Any:
    """POST /federation/epistemic/request_validation -- envia validation request a peers."""
    if not hasattr(server.chat, 'epistemic_federation_client'):
        return web.json_response({"error": "federation client not initialized"}, status=500)
    data = await request.json()
    result = await server.chat.epistemic_federation_client.request_validation_from_peers(
        claim=data.get("claim", ""),
        source=data.get("source", ""),
        domain=data.get("domain"),
        confidence_local=data.get("confidence_local", 0.5),
        quarantine_entry_id=data.get("quarantine_entry_id"),
    )
    return web.json_response(result)


