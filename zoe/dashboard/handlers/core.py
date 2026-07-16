"""Handlers core: /, /stats, /memory, /state, /identity, /history, /federation, sleep/wake."""

import logging
import time
from typing import Any

from aiohttp import web

from ..html.dashboard_html import _get_dashboard_html

logger = logging.getLogger(__name__)


async def _handle_index(server, request) -> Any:
    """Sirve el HTML del dashboard.

    Sprint 5.21: Inyecta el token directamente en el HTML como variable JS.
    Esto elimina la necesidad de leerlo de URL params o localStorage,
    que fallaba en Safari y causaba que el dashboard no fuera funcional.
    """
    html = _get_dashboard_html()
    # Inyectar el token antes del primer <script> tag
    token_js = f'<script>window.ZOE_SERVER_TOKEN = "{server.auth_token}";</script>'
    html = html.replace('<script>', token_js + '\n<script>', 1)
    return web.Response(text=html, content_type="text/html")


async def _handle_stats(server, request) -> Any:
    """Devuelve estadisticas del loop cognitivo."""
    stats = server.chat.loop.get_stats()
    return web.json_response(stats)


async def _handle_memory(server, request) -> Any:
    """Devuelve entradas de memoria con paginación.

    Sprint 5.16 F2.2: Añadido paginación limit/offset para evitar
    respuestas enormes cuando ZOE tiene miles de entradas.
    Default: limit=50, offset=0. Max: limit=200.
    """
    mem_type = request.query.get("type")
    # Sprint 5.16 F2.2: paginación
    try:
        limit = int(request.query.get("limit", 50))
        offset = int(request.query.get("offset", 0))
    except ValueError:
        limit, offset = 50, 0
    # Cap limit to prevent abuse
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    all_entries = []
    for entry in server.chat.memory.all_entries():
        if mem_type and entry.type != mem_type:
            continue
        all_entries.append({
            "id": entry.id,
            "type": entry.type,
            "content": entry.content[:200],
            "confidence": entry.confidence,
            "salience": entry.salience,
            "provenance": entry.provenance,
            "timestamp": entry.timestamp,
        })

    total = len(all_entries)
    paginated = all_entries[offset:offset + limit]
    return web.json_response({
        "entries": paginated,
        "count": len(paginated),
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    })


async def _handle_identity(server, request) -> Any:
    """Devuelve la identidad de ZOE."""
    v = server.chat.vault
    return web.json_response({
        "name": v.name,
        "hash": v.identity_hash,
        "vectors": v.vectors,
        "values": v.values,
        "purpose": v.purpose,
        "birth_timestamp": v.birth_timestamp,
    })


async def _handle_state(server, request) -> Any:
    """Devuelve el estado del organismo."""
    s = server.chat.loop.state
    p = server.chat.loop.physics
    t = server.chat.loop.tensions
    m = server.chat.metabolism
    return web.json_response({
        "energy": s.energy,
        "fatigue": s.fatigue,
        "arousal": s.arousal,
        "attention": s.attention,
        "metabolism": m.state.value,
        "physics": p.to_dict(),
        "tensions": t.to_dict(),
        "iterations": s.iteration_count,
    })


async def _handle_sleep(server, request) -> Any:
    """Fuerza a ZOE a dormir."""
    server.chat.metabolism.internal_state.fatigue = 0.9
    server.chat.metabolism.tick(dt=1.0)
    await server._broadcast_state()
    return web.json_response({"status": "sleeping"})


async def _handle_wake(server, request) -> Any:
    """Despierta a ZOE."""
    server.chat.metabolism.internal_state.fatigue = 0.0
    server.chat.metabolism.internal_state.energy = 1.0
    from zoe.metabolism.metabolism import MetabolicState
    server.chat.metabolism.state = MetabolicState.AWAKE
    await server._broadcast_state()
    return web.json_response({"status": "awake"})


async def _handle_history(server, request) -> Any:
    """Devuelve el historial de conversaciones."""
    # Sprint 5.14: _conversation_history es deque(maxlen=500) que no soporta slicing.
    # Convertir a list antes de slicear.
    history_list = list(server._conversation_history)
    return web.json_response({
        "conversations": history_list[-100:],
        "count": len(server._conversation_history),
    })


async def _handle_federation(server, request) -> Any:
    """Devuelve el estado de la federacion."""
    fm = server.chat.loop.phylogenetic
    species = fm.get_species_state()
    return web.json_response({
        "species": species,
        "peers": [],
        "enabled": False,
    })
