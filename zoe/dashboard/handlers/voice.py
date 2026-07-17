"""Handlers de voice-first: /api/voice/* (3 endpoints)."""

import asyncio
from typing import Any

from aiohttp import web


async def _handle_voice_start(server, request) -> Any:
    """POST /api/voice/start -- arranca el modo voice-first en background."""
    if hasattr(server, '_voice_mode') and server._voice_mode:
        return web.json_response({"status": "already_listening"})
    try:
        from zoe.peripherals.voice_first import VoiceFirstMode, VoiceConfig
        config = VoiceConfig(
            wake_word=request.query.get("wake_word", "hey zoe"),
        )
        server._voice_mode = VoiceFirstMode(config, zoe_chat=server.chat)
        asyncio.create_task(server._voice_mode.start())
        return web.json_response({"status": "listening", "wake_word": config.wake_word})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def _handle_voice_stop(server, request) -> Any:
    """POST /api/voice/stop -- detiene el modo voice-first."""
    if not hasattr(server, '_voice_mode') or not server._voice_mode:
        return web.json_response({"status": "not_running"})
    try:
        await server._voice_mode.stop()
        server._voice_mode = None
        return web.json_response({"status": "stopped"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def _handle_voice_status(server, request) -> Any:
    """GET /api/voice/status -- estado del modo voice-first."""
    if not hasattr(server, '_voice_mode') or not server._voice_mode:
        return web.json_response({"status": "stopped"})
    try:
        state = server._voice_mode.state.value if hasattr(server._voice_mode, 'state') else "unknown"
        return web.json_response({"status": "running", "state": state})
    except Exception:
        return web.json_response({"status": "running"})


