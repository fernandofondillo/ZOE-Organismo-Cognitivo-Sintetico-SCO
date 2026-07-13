"""Handlers de chat: WebSocket, POST /chat, /feed upload."""

import asyncio
import json
import logging
import os
import time
from typing import Any

from aiohttp import web, WSMsgType

logger = logging.getLogger(__name__)


async def _handle_websocket(server, request) -> Any:
    """Maneja conexion WebSocket para tiempo real."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    server.ws_clients.add(ws)

    logger.info(f"WebSocket client connected. Total: {len(server.ws_clients)}")

    # Enviar estado inicial
    await server._send_state_update(ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get("type")

                if msg_type == "chat":
                    message = data.get("message", "")
                    # Fase 5: usar ACD para respuesta con metadata
                    result = await server.chat.send_message_acd(message)
                    response = result.get("response", "")
                    level = result.get("level", "?")
                    latency_ms = result.get("latency_ms", 0)
                    cache_hit = result.get("cache_hit", False)
                    cost = result.get("cost", 0)

                    # Guardar en historial
                    server._conversation_history.append({
                        "role": "user",
                        "content": message,
                        "timestamp": time.time(),
                    })
                    server._conversation_history.append({
                        "role": "zoe",
                        "content": response,
                        "timestamp": time.time(),
                        "acd_level": level,
                        "latency_ms": latency_ms,
                        "cache_hit": cache_hit,
                    })

                    # Enviar respuesta con metadata ACD
                    await ws.send_json({
                        "type": "chat_response",
                        "content": response,
                        "acd_level": level,
                        "latency_ms": latency_ms,
                        "cache_hit": cache_hit,
                        "cost": cost,
                        "timestamp": time.time(),
                    })

                    # Broadcast estado actualizado
                    await server._broadcast_state()

                elif msg_type == "command":
                    cmd = data.get("command", "")
                    result = await server._handle_command(cmd, data)
                    await ws.send_json({
                        "type": "command_result",
                        "command": cmd,
                        "result": result,
                        "timestamp": time.time(),
                    })

                # Fase 6A: WebSocket events para capsulas
                elif msg_type == "capsule_action":
                    action = data.get("action", "")
                    capsule_name = data.get("name", "")

                    if action == "load":
                        result = server.chat.capsule_manager.load(capsule_name)
                        # Notificar a todos los clientes WS
                        await server._broadcast_to_all({
                            "type": "capsule_loaded",
                            "capsule": capsule_name,
                            "success": result.success,
                            "entries_loaded": result.entries_loaded,
                            "components_injected": result.components_injected,
                            "trajectory_hash": result.trajectory_hash,
                            "error": result.error,
                            "timestamp": time.time(),
                        })
                    elif action == "unload":
                        ok = server.chat.capsule_manager.unload(capsule_name)
                        await server._broadcast_to_all({
                            "type": "capsule_unloaded",
                            "capsule": capsule_name,
                            "success": ok,
                            "timestamp": time.time(),
                        })
                    elif action == "list":
                        loaded = server.chat.capsule_manager.list_loaded()
                        await ws.send_json({
                            "type": "capsules_state",
                            "loaded": loaded,
                            "timestamp": time.time(),
                        })

            elif msg.type == WSMsgType.ERROR:
                logger.warning(f"WebSocket error: {ws.exception()}")
    finally:
        server.ws_clients.discard(ws)
        logger.info(f"WebSocket client disconnected. Total: {len(server.ws_clients)}")

    return ws


async def _handle_chat_post(server, request) -> Any:
    """Endpoint REST para chat (alternativa a WebSocket)."""
    data = await request.json()
    message = data.get("message", "")
    # Fase 5: ACD con metadata
    result = await server.chat.send_message_acd(message)
    return web.json_response({
        "response": result.get("response", ""),
        "acd_level": result.get("level", "?"),
        "latency_ms": result.get("latency_ms", 0),
        "cache_hit": result.get("cache_hit", False),
        "cost": result.get("cost", 0),
        "timestamp": time.time(),
    })


async def _handle_feed_upload(server, request) -> Any:
    """Subida de archivos para alimentar a ZOE."""
    reader = await request.multipart()
    file_part = await reader.next()

    if file_part is None:
        return web.json_response({"error": "No file uploaded"}, status=400)

    # Leer contenido
    content = await file_part.read()
    filename = file_part.filename or "uploaded.txt"
    content_type = file_part.headers.get("Content-Type", "")

    # Sprint 5.11 C7 -- Si es imagen, usar VLM para describirla
    is_image = content_type.startswith("image/") or filename.lower().endswith(
        (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    )

    text = ""
    image_description = None

    if is_image:
        # Intentar describir la imagen con VLM
        try:
            from zoe.peripherals.multimodal import VLMPeripheral
            vlm_backend = os.environ.get("ZOE_VLM_BACKEND", "ollama")
            vlm_model = os.environ.get("ZOE_VLM_MODEL", "llava:7b")
            api_key = os.environ.get("OPENAI_API_KEY") if vlm_backend == "openai" else None

            vlm = VLMPeripheral(
                model=vlm_model,
                backend=vlm_backend,
                api_key=api_key,
            )
            image_description = await vlm.generate(
                prompt="Describe esta imagen en detalle. Que ves?",
                images=[content],
            )
            text = f"[Imagen: {filename}] {image_description}"
            logger.info(f"VLM described image {filename}: {image_description[:100]}...")
        except Exception as e:
            logger.warning(f"VLM failed for {filename}: {e}. Storing raw metadata.")
            text = f"[Imagen: {filename}] (VLM no disponible - {e})"
    else:
        # Archivo de texto
        text = content.decode('utf-8', errors='replace')

    # Almacenar en memoria semantica
    entry_id = server.chat.memory.add(
        content=text[:2000],
        type="semantic",
        confidence=0.7,
        salience=0.6,
        provenance=f"upload:{filename}",
    )

    # Firmar mutacion
    if server.chat.loop.ontogenetic_motor:
        try:
            mutation = server.chat.loop.ontogenetic_motor.propose_mutation(
                type="add_memory",
                target="semantic",
                payload={"content": text[:100], "source": filename},
                justification=f"Document uploaded: {filename}",
                provenance=f"upload:{filename}",
                cost=0.1,
                confidence=0.7,
            )
            server.chat.loop.ontogenetic_motor.apply_mutation(mutation)
        except Exception:
            pass

    return web.json_response({
        "status": "stored",
        "filename": filename,
        "size": len(content),
        "entry_id": entry_id,
        "is_image": is_image,
        "image_description": image_description,
    })
