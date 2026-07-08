"""
ZOE v1.0 — Web Dashboard Server

Servidor HTTP + WebSocket que sirve el dashboard web de ZOE.
Permite comunicarse con ZOE desde el navegador en http://localhost:8642

Funciones:
- Chat en tiempo real (WebSocket)
- Estado del organismo en vivo (WebSocket)
- Pensamientos autónomos en vivo (WebSocket)
- Selector de LLM en caliente
- Alimentación de documentos (file upload)
- Histórico de conversaciones
- Panel de federación
- Control de metabolismo (sleep/wake)

Uso:
    python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b
    python -m zoe.web_dashboard --backend zai
    python -m zoe.web_dashboard --backend mock --port 8642
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


class DashboardServer:
    """
    Servidor del dashboard web de ZOE.
    
    Combina:
    - HTTP server (sirve el HTML del dashboard)
    - WebSocket server (comunicación en tiempo real)
    - ZoeChat (organismo ZOE completo)
    """

    def __init__(
        self,
        backend: str = "mock",
        model: str = None,
        use_case: str = None,
        port: int = 8642,
        db_path: str = None,
    ):
        self.backend = backend
        self.model = model
        self.use_case = use_case
        self.port = port
        self.db_path = db_path or "zoe_data/dashboard_memory.db"

        self.chat = None
        self.ws_clients: Set = set()
        self._app = None
        self._runner = None
        self._background_broadcaster = None
        self._conversation_history: List[Dict[str, Any]] = []

    async def initialize(self) -> None:
        """Inicializa ZOE y el servidor."""
        from .cli_chat import ZoeChat

        self.chat = ZoeChat(
            backend=self.backend,
            model=self.model,
            use_case=self.use_case,
            db_path=self.db_path,
        )
        await self.chat.initialize()
        logger.info(f"ZOE initialized for dashboard: {self.chat.vault.identity_hash[:16]}...")

    async def start(self) -> None:
        """Inicia el servidor HTTP + WebSocket."""
        from aiohttp import web, WSMsgType

        app = web.Application(client_max_size=10 * 1024 * 1024)  # 10MB for file uploads

        # Routes
        app.router.add_get("/", self._handle_index)
        app.router.add_get("/ws", self._handle_websocket)
        app.router.add_post("/chat", self._handle_chat_post)
        app.router.add_post("/feed", self._handle_feed_upload)
        app.router.add_get("/stats", self._handle_stats)
        app.router.add_get("/memory", self._handle_memory)
        app.router.add_get("/identity", self._handle_identity)
        app.router.add_get("/state", self._handle_state)
        app.router.add_post("/sleep", self._handle_sleep)
        app.router.add_post("/wake", self._handle_wake)
        app.router.add_post("/llm", self._handle_llm_switch)
        app.router.add_get("/history", self._handle_history)
        app.router.add_get("/federation", self._handle_federation)

        # Fase 6A: Capsules endpoints
        app.router.add_get("/api/capsules", self._handle_capsules_list)
        app.router.add_get("/api/capsules/loaded", self._handle_capsules_loaded)
        app.router.add_post("/api/capsules/load", self._handle_capsule_load)
        app.router.add_post("/api/capsules/unload", self._handle_capsule_unload)
        app.router.add_get("/api/capsules/{name}/info", self._handle_capsule_info)
        app.router.add_post("/api/capsules/{name}/validate", self._handle_capsule_validate)
        app.router.add_post("/api/capsules/create", self._handle_capsule_create)

        # Fase 6A Punto 2: Federación epistémica endpoints
        app.router.add_post("/federation/epistemic/validate", self._handle_epistemic_validate)
        app.router.add_get("/federation/epistemic/knowledge/{claim_hash}", self._handle_epistemic_knowledge)
        app.router.add_post("/federation/epistemic/register", self._handle_epistemic_register)
        app.router.add_get("/federation/epistemic/peers", self._handle_epistemic_peers)
        app.router.add_get("/federation/epistemic/stats", self._handle_epistemic_stats)
        app.router.add_post("/federation/epistemic/request_validation", self._handle_epistemic_request_validation)

        # Fase 6A Punto 3: Cuarentena endpoints
        app.router.add_get("/api/quarantine", self._handle_quarantine_list)
        app.router.add_get("/api/quarantine/stats", self._handle_quarantine_stats)
        app.router.add_post("/api/quarantine/{entry_id}/promote", self._handle_quarantine_promote)
        app.router.add_post("/api/quarantine/{entry_id}/reject", self._handle_quarantine_reject)

        # Fase 6B Marketplace endpoints
        app.router.add_get("/api/marketplace/capsules", self._handle_marketplace_list)
        app.router.add_post("/api/marketplace/upload", self._handle_marketplace_upload)
        app.router.add_post("/api/marketplace/download/{name}", self._handle_marketplace_download)
        app.router.add_get("/api/marketplace/use_cases", self._handle_marketplace_use_cases)
        app.router.add_post("/api/marketplace/upload_use_case", self._handle_marketplace_upload_use_case)

        self._app = app
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "0.0.0.0", self.port)
        await site.start()

        # Start background broadcaster (sends state updates to WS clients)
        self._background_broadcaster = asyncio.create_task(self._broadcast_loop())

        logger.info(f"Dashboard server started on http://localhost:{self.port}")

    async def stop(self) -> None:
        """Detiene el servidor."""
        if self._background_broadcaster:
            self._background_broadcaster.cancel()
            try:
                await asyncio.wait_for(self._background_broadcaster, timeout=3.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass

        if self._runner:
            await self._runner.cleanup()

        if self.chat:
            await self.chat.shutdown()

    # ===== HTTP Handlers =====

    async def _handle_index(self, request) -> Any:
        """Sirve el HTML del dashboard."""
        from aiohttp import web
        html = _get_dashboard_html()
        return web.Response(text=html, content_type="text/html")

    async def _handle_websocket(self, request) -> Any:
        """Maneja conexión WebSocket para tiempo real."""
        from aiohttp import web, WSMsgType

        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.ws_clients.add(ws)

        logger.info(f"WebSocket client connected. Total: {len(self.ws_clients)}")

        # Enviar estado inicial
        await self._send_state_update(ws)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")

                    if msg_type == "chat":
                        message = data.get("message", "")
                        # Fase 5: usar ACD para respuesta con metadata
                        result = await self.chat.send_message_acd(message)
                        response = result.get("response", "")
                        level = result.get("level", "?")
                        latency_ms = result.get("latency_ms", 0)
                        cache_hit = result.get("cache_hit", False)
                        cost = result.get("cost", 0)

                        # Guardar en historial
                        self._conversation_history.append({
                            "role": "user",
                            "content": message,
                            "timestamp": time.time(),
                        })
                        self._conversation_history.append({
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
                        await self._broadcast_state()

                    elif msg_type == "command":
                        cmd = data.get("command", "")
                        result = await self._handle_command(cmd, data)
                        await ws.send_json({
                            "type": "command_result",
                            "command": cmd,
                            "result": result,
                            "timestamp": time.time(),
                        })
                    
                    # Fase 6A: WebSocket events para cápsulas
                    elif msg_type == "capsule_action":
                        action = data.get("action", "")
                        capsule_name = data.get("name", "")
                        
                        if action == "load":
                            result = self.chat.capsule_manager.load(capsule_name)
                            # Notificar a todos los clientes WS
                            await self._broadcast_to_all({
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
                            ok = self.chat.capsule_manager.unload(capsule_name)
                            await self._broadcast_to_all({
                                "type": "capsule_unloaded",
                                "capsule": capsule_name,
                                "success": ok,
                                "timestamp": time.time(),
                            })
                        elif action == "list":
                            loaded = self.chat.capsule_manager.list_loaded()
                            await ws.send_json({
                                "type": "capsules_state",
                                "loaded": loaded,
                                "timestamp": time.time(),
                            })

                elif msg.type == WSMsgType.ERROR:
                    logger.warning(f"WebSocket error: {ws.exception()}")
        finally:
            self.ws_clients.discard(ws)
            logger.info(f"WebSocket client disconnected. Total: {len(self.ws_clients)}")

        return ws

    async def _handle_chat_post(self, request) -> Any:
        """Endpoint REST para chat (alternativa a WebSocket)."""
        from aiohttp import web
        data = await request.json()
        message = data.get("message", "")
        # Fase 5: ACD con metadata
        result = await self.chat.send_message_acd(message)
        return web.json_response({
            "response": result.get("response", ""),
            "acd_level": result.get("level", "?"),
            "latency_ms": result.get("latency_ms", 0),
            "cache_hit": result.get("cache_hit", False),
            "cost": result.get("cost", 0),
            "timestamp": time.time(),
        })

    async def _handle_feed_upload(self, request) -> Any:
        """Subida de archivos para alimentar a ZOE."""
        from aiohttp import web

        reader = await request.multipart()
        file_part = await reader.next()

        if file_part is None:
            return web.json_response({"error": "No file uploaded"}, status=400)

        # Leer contenido
        content = await file_part.read()
        text = content.decode('utf-8', errors='replace')

        # Almacenar en memoria semántica
        filename = file_part.filename or "uploaded.txt"
        entry_id = self.chat.memory.add(
            content=text[:2000],
            type="semantic",
            confidence=0.7,
            salience=0.6,
            provenance=f"upload:{filename}",
        )

        # Firmar mutación
        if self.chat.loop.ontogenetic_motor:
            try:
                mutation = self.chat.loop.ontogenetic_motor.propose_mutation(
                    type="add_memory",
                    target="semantic",
                    payload={"content": text[:100], "source": filename},
                    justification=f"Document uploaded: {filename}",
                    provenance=f"upload:{filename}",
                    cost=0.1,
                    confidence=0.7,
                )
                self.chat.loop.ontogenetic_motor.apply_mutation(mutation)
            except Exception:
                pass

        return web.json_response({
            "status": "stored",
            "filename": filename,
            "size": len(text),
            "entry_id": entry_id,
        })

    async def _handle_stats(self, request) -> Any:
        from aiohttp import web
        stats = self.chat.loop.get_stats()
        return web.json_response(stats)

    async def _handle_memory(self, request) -> Any:
        from aiohttp import web
        mem_type = request.query.get("type")
        entries = []
        for entry in self.chat.memory.all_entries():
            if mem_type and entry.type != mem_type:
                continue
            entries.append({
                "id": entry.id,
                "type": entry.type,
                "content": entry.content[:200],
                "confidence": entry.confidence,
                "salience": entry.salience,
                "provenance": entry.provenance,
                "timestamp": entry.timestamp,
            })
        return web.json_response({"entries": entries, "count": len(entries)})

    async def _handle_identity(self, request) -> Any:
        from aiohttp import web
        v = self.chat.vault
        return web.json_response({
            "name": v.name,
            "hash": v.identity_hash,
            "vectors": v.vectors,
            "values": v.values,
            "purpose": v.purpose,
            "birth_timestamp": v.birth_timestamp,
        })

    async def _handle_state(self, request) -> Any:
        from aiohttp import web
        s = self.chat.loop.state
        p = self.chat.loop.physics
        t = self.chat.loop.tensions
        m = self.chat.metabolism
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

    async def _handle_sleep(self, request) -> Any:
        from aiohttp import web
        self.chat.metabolism.internal_state.fatigue = 0.9
        self.chat.metabolism.tick(dt=1.0)
        await self._broadcast_state()
        return web.json_response({"status": "sleeping"})

    async def _handle_wake(self, request) -> Any:
        from aiohttp import web
        self.chat.metabolism.internal_state.fatigue = 0.0
        self.chat.metabolism.internal_state.energy = 1.0
        from zoe.metabolism.metabolism import MetabolicState
        self.chat.metabolism.state = MetabolicState.AWAKE
        await self._broadcast_state()
        return web.json_response({"status": "awake"})

    async def _handle_llm_switch(self, request) -> Any:
        """Cambia el LLM periférico en caliente."""
        from aiohttp import web
        from .peripherals.llm import create_llm_peripheral

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
                self.chat.llm = new_llm
                self.chat.speaker.llm = new_llm
                self.backend = new_backend
                self.model = new_model
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

    async def _handle_history(self, request) -> Any:
        from aiohttp import web
        return web.json_response({
            "conversations": self._conversation_history[-100:],
            "count": len(self._conversation_history),
        })

    async def _handle_federation(self, request) -> Any:
        from aiohttp import web
        fm = self.chat.loop.phylogenetic
        species = fm.get_species_state()
        return web.json_response({
            "species": species,
            "peers": [],
            "enabled": False,
        })

    # ===== WebSocket broadcasting =====

    async def _broadcast_loop(self) -> None:
        """Bucle que envía estado + pensamientos a todos los WS clients cada 2s."""
        last_thought_count = 0

        while True:
            await asyncio.sleep(2.0)

            if not self.ws_clients:
                continue

            # Estado del organismo
            await self._broadcast_state()

            # Pensamientos nuevos
            thoughts = self.chat._thoughts_while_idle
            if len(thoughts) > 0:
                for thought in thoughts:
                    await self._broadcast_to_all({
                        "type": "autonomous_thought",
                        "content": thought.content,
                        "trigger": thought.trigger,
                        "surprise": thought.surprise,
                        "system": thought.metadata.get("system", "system1"),
                        "timestamp": thought.timestamp,
                    })
                self.chat._thoughts_while_idle.clear()

    async def _broadcast_state(self) -> None:
        """Envía estado del organismo a todos los WS clients."""
        if not self.ws_clients or not self.chat:
            return

        s = self.chat.loop.state
        p = self.chat.loop.physics
        t = self.chat.loop.tensions
        m = self.chat.metabolism

        state_data = {
            "type": "state_update",
            "energy": s.energy,
            "fatigue": s.fatigue,
            "arousal": s.arousal,
            "attention": s.attention,
            "metabolism": m.state.value,
            "iterations": s.iteration_count,
            "thoughts_total": len(self.chat.loop.thoughts),
            "physics": p.to_dict(),
            "tensions": {name: t.to_dict() for name, t in t.tensions.items()},
        }

        await self._broadcast_to_all(state_data)

    async def _send_state_update(self, ws) -> None:
        """Envía estado a un WS client específico."""
        try:
            s = self.chat.loop.state
            p = self.chat.loop.physics
            m = self.chat.metabolism
            t = self.chat.loop.tensions

            await ws.send_json({
                "type": "state_update",
                "energy": s.energy,
                "fatigue": s.fatigue,
                "arousal": s.arousal,
                "attention": s.attention,
                "metabolism": m.state.value,
                "iterations": s.iteration_count,
                "thoughts_total": len(self.chat.loop.thoughts),
                "physics": p.to_dict(),
                "tensions": {name: t.to_dict() for name, t in t.tensions.items()},
            })
        except Exception as e:
            logger.warning(f"Failed to send state update: {e}")

    async def _broadcast_to_all(self, data: dict) -> None:
        """Envía data a todos los WS clients."""
        dead = set()
        for ws in self.ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self.ws_clients -= dead

    # ============================================================
    # Fase 6A: Capsules handlers
    # ============================================================

    async def _handle_capsules_list(self, request) -> Any:
        """Lista todas las cápsulas disponibles."""
        from aiohttp import web
        if not self.chat or not hasattr(self.chat, 'capsule_manager'):
            return web.json_response({"error": "capsule_manager not initialized"}, status=500)
        available = self.chat.capsule_manager.list_available()
        return web.json_response({
            "available": available,
            "count": len(available),
        })

    async def _handle_capsules_loaded(self, request) -> Any:
        """Lista cápsulas cargadas actualmente."""
        from aiohttp import web
        if not self.chat or not hasattr(self.chat, 'capsule_manager'):
            return web.json_response({"error": "capsule_manager not initialized"}, status=500)
        loaded = self.chat.capsule_manager.list_loaded()
        return web.json_response({
            "loaded": loaded,
            "count": len(loaded),
        })

    async def _handle_capsule_load(self, request) -> Any:
        """Carga una cápsula en caliente."""
        from aiohttp import web
        if not self.chat or not hasattr(self.chat, 'capsule_manager'):
            return web.json_response({"error": "capsule_manager not initialized"}, status=500)
        data = await request.json()
        name = data.get("name")
        if not name:
            return web.json_response({"error": "name required"}, status=400)
        result = self.chat.capsule_manager.load(name)
        return web.json_response({
            "success": result.success,
            "capsule": result.capsule_name,
            "entries_loaded": result.entries_loaded,
            "components_injected": result.components_injected,
            "trajectory_hash": result.trajectory_hash,
            "error": result.error,
        })

    async def _handle_capsule_unload(self, request) -> Any:
        """Descarga una cápsula."""
        from aiohttp import web
        if not self.chat or not hasattr(self.chat, 'capsule_manager'):
            return web.json_response({"error": "capsule_manager not initialized"}, status=500)
        data = await request.json()
        name = data.get("name")
        if not name:
            return web.json_response({"error": "name required"}, status=400)
        ok = self.chat.capsule_manager.unload(name)
        return web.json_response({
            "success": ok,
            "capsule": name,
        })

    async def _handle_capsule_info(self, request) -> Any:
        """Info detallada de una cápsula."""
        from aiohttp import web
        if not self.chat or not hasattr(self.chat, 'capsule_manager'):
            return web.json_response({"error": "capsule_manager not initialized"}, status=500)
        name = request.match_info["name"]
        info = self.chat.capsule_manager.get_info(name)
        if not info:
            return web.json_response({"error": "capsule not found"}, status=404)
        return web.json_response(info)

    async def _handle_capsule_validate(self, request) -> Any:
        """
        Valida una cápsula: schema + contenido + validators.
        
        Fase 6A Punto 4: endpoint para validar cápsulas desde el Dashboard.
        Ejecuta:
        1. Validación de schema (capsule.yaml)
        2. Carga de contenido (JSONL files)
        3. Tests de validators (si los tiene)
        4. Hash verification
        """
        from aiohttp import web
        import sys
        import subprocess
        from pathlib import Path
        
        name = request.match_info["name"]
        
        # Localizar la cápsula
        capsules_dir = Path(__file__).parent / "capsules"
        cap_dir = capsules_dir / name
        
        if not cap_dir.exists():
            return web.json_response({
                "valid": False,
                "name": name,
                "errors": ["capsule_directory_not_found"],
            }, status=404)
        
        result = {
            "name": name,
            "valid": True,
            "checks": [],
            "errors": [],
            "warnings": [],
            "stats": {},
        }
        
        # 1. Schema validation (via scaffold CLI)
        try:
            cmd = [sys.executable, "-m", "zoe.capsules.scaffold", "validate", "--name", name]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                  cwd="/home/z/my-project/zoe-analysis/repo")
            if proc.returncode == 0:
                result["checks"].append({"name": "schema", "status": "pass", "output": proc.stdout[:500]})
            else:
                result["valid"] = False
                result["errors"].append(f"schema_validation_failed: {proc.stderr or proc.stdout}")
                result["checks"].append({"name": "schema", "status": "fail", "output": proc.stderr[:500]})
        except Exception as e:
            result["warnings"].append(f"schema_check_error: {e}")
        
        # 2. Cargar contenido y contar entries
        try:
            from zoe.capsules.loader import CapsuleLoader
            loader = CapsuleLoader()
            cap = loader._load_capsule(name)
            if cap:
                result["stats"] = {
                    "total_entries": cap.total_entries,
                    "semantic": len(cap.semantic_memory),
                    "procedural": len(cap.procedural_skills),
                    "causal": len(cap.causal_models),
                    "emotional": len(cap.emotional_patterns),
                    "ethical": len(cap.ethical_guidelines),
                    "has_validators": cap.validators is not None,
                    "has_tools": len(cap.tools) > 0,
                    "has_prompts": len(cap.prompts) > 0,
                }
                result["checks"].append({
                    "name": "content_load",
                    "status": "pass",
                    "entries": cap.total_entries,
                })
                
                # 3. Verificar entradas con campos mínimos
                missing_fields = []
                for i, entry in enumerate(cap.semantic_memory[:5]):
                    if "content" not in entry:
                        missing_fields.append(f"semantic[{i}]:missing_content")
                    if "confidence" not in entry:
                        missing_fields.append(f"semantic[{i}]:missing_confidence")
                
                if missing_fields:
                    result["warnings"].append(f"entries_with_missing_fields: {missing_fields[:3]}")
                
                # 4. Test validators si los tiene
                if cap.validators:
                    try:
                        # Test que validate_response existe y no falla con input de prueba
                        if hasattr(cap.validators, "validate_response"):
                            ok, reason = cap.validators.validate_response("test response", context={})
                            result["checks"].append({
                                "name": "validators_test",
                                "status": "pass" if ok else "warning",
                                "reason": reason,
                            })
                        # Test validate_new_knowledge
                        if hasattr(cap.validators, "validate_new_knowledge"):
                            ok, reason = cap.validators.validate_new_knowledge(
                                "test claim", "test_source", context={}
                            )
                            result["checks"].append({
                                "name": "validators_knowledge_test",
                                "status": "pass",
                                "reason": reason,
                            })
                    except Exception as e:
                        result["valid"] = False
                        result["errors"].append(f"validator_execution_failed: {e}")
                        result["checks"].append({
                            "name": "validators_test",
                            "status": "fail",
                            "error": str(e),
                        })
                
                # 5. Hash verification
                content_hash = loader.compute_content_hash(cap)
                declared_hash = cap.meta.content_hash
                
                if declared_hash and declared_hash != "sha256:auto":
                    if declared_hash == content_hash:
                        result["checks"].append({"name": "hash_match", "status": "pass"})
                    else:
                        result["valid"] = False
                        result["errors"].append("hash_mismatch")
                        result["checks"].append({
                            "name": "hash_match",
                            "status": "fail",
                            "declared": declared_hash[:30],
                            "computed": content_hash[:30],
                        })
                else:
                    result["warnings"].append("hash_not_declared_run_scaffold_hash_to_compute")
                    result["checks"].append({"name": "hash_match", "status": "skip"})
            else:
                result["valid"] = False
                result["errors"].append("content_load_failed")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"content_load_error: {e}")
        
        return web.json_response(result)

    async def _handle_capsule_create(self, request) -> Any:
        """Crea una nueva cápsula usando el scaffold CLI."""
        from aiohttp import web
        data = await request.json()
        name = data.get("name")
        domain = data.get("domain", "todo.domain")
        trust_level = data.get("trust_level", "curated")
        description = data.get("description", "Cápsula creada desde Dashboard")
        components = data.get("components", "semantic,validators")
        use_cases = data.get("use_cases", "")

        if not name:
            return web.json_response({"error": "name required"}, status=400)

        import subprocess
        import sys
        cmd = [
            sys.executable, "-m", "zoe.capsules.scaffold", "create",
            "--name", name,
            "--domain", domain,
            "--trust-level", trust_level,
            "--description", description,
            "--components", components,
        ]
        if use_cases:
            cmd.extend(["--use-cases", use_cases])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd="/home/z/my-project/zoe-analysis/repo")
            if result.returncode == 0:
                return web.json_response({
                    "success": True,
                    "name": name,
                    "output": result.stdout,
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": result.stderr or result.stdout,
                }, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    # ============================================================
    # Fase 6A Punto 2: Federación epistémica handlers
    # ============================================================

    async def _handle_epistemic_validate(self, request) -> Any:
        """POST /federation/epistemic/validate — recibe validation request de peer."""
        from aiohttp import web
        data = await request.json()
        if not hasattr(self.chat, 'epistemic_federation_server'):
            return web.json_response({"error": "federation server not initialized"}, status=500)
        result = await self.chat.epistemic_federation_server.handle_validate_request(data)
        return web.json_response(result)

    async def _handle_epistemic_knowledge(self, request) -> Any:
        """GET /federation/epistemic/knowledge/{claim_hash} — consulta local knowledge."""
        from aiohttp import web
        claim_hash = request.match_info["claim_hash"]
        if not hasattr(self.chat, 'epistemic_federation_server'):
            return web.json_response({"error": "federation server not initialized"}, status=500)
        result = await self.chat.epistemic_federation_server.handle_knowledge_query(claim_hash)
        return web.json_response(result)

    async def _handle_epistemic_register(self, request) -> Any:
        """POST /federation/epistemic/register — registra peer."""
        from aiohttp import web
        data = await request.json()
        if not hasattr(self.chat, 'epistemic_federation_server'):
            return web.json_response({"error": "federation server not initialized"}, status=500)
        result = await self.chat.epistemic_federation_server.handle_register_peer(data)
        return web.json_response(result)

    async def _handle_epistemic_peers(self, request) -> Any:
        """GET /federation/epistemic/peers — lista peers."""
        from aiohttp import web
        if not hasattr(self.chat, 'epistemic_federation_server'):
            return web.json_response({"error": "federation server not initialized"}, status=500)
        return web.json_response({"peers": self.chat.epistemic_federation_server.list_peers()})

    async def _handle_epistemic_stats(self, request) -> Any:
        """GET /federation/epistemic/stats — stats de federación epistémica."""
        from aiohttp import web
        if not hasattr(self.chat, 'epistemic_federation_server'):
            return web.json_response({"error": "federation server not initialized"}, status=500)
        return web.json_response(self.chat.epistemic_federation_server.get_stats())

    async def _handle_epistemic_request_validation(self, request) -> Any:
        """POST /federation/epistemic/request_validation — envía validation request a peers."""
        from aiohttp import web
        if not hasattr(self.chat, 'epistemic_federation_client'):
            return web.json_response({"error": "federation client not initialized"}, status=500)
        data = await request.json()
        result = await self.chat.epistemic_federation_client.request_validation_from_peers(
            claim=data.get("claim", ""),
            source=data.get("source", ""),
            domain=data.get("domain"),
            confidence_local=data.get("confidence_local", 0.5),
            quarantine_entry_id=data.get("quarantine_entry_id"),
        )
        return web.json_response(result)

    # ============================================================
    # Fase 6A Punto 3: Cuarentena handlers
    # ============================================================

    async def _handle_quarantine_list(self, request) -> Any:
        """GET /api/quarantine — lista entries en cuarentena."""
        from aiohttp import web
        if not hasattr(self.chat, 'knowledge_quarantine'):
            return web.json_response({"error": "quarantine not initialized"}, status=500)
        active = self.chat.knowledge_quarantine.list_active()
        pending = self.chat.knowledge_quarantine.list_pending_verification()
        return web.json_response({
            "active": [e.to_dict() for e in active],
            "pending": [e.to_dict() for e in pending],
            "active_count": len(active),
            "pending_count": len(pending),
        })

    async def _handle_quarantine_stats(self, request) -> Any:
        """GET /api/quarantine/stats — stats de cuarentena."""
        from aiohttp import web
        if not hasattr(self.chat, 'knowledge_quarantine'):
            return web.json_response({"error": "quarantine not initialized"}, status=500)
        return web.json_response(self.chat.knowledge_quarantine.get_stats())

    async def _handle_quarantine_promote(self, request) -> Any:
        """POST /api/quarantine/{entry_id}/promote — promueve entrada manualmente."""
        from aiohttp import web
        if not hasattr(self.chat, 'knowledge_quarantine'):
            return web.json_response({"error": "quarantine not initialized"}, status=500)
        entry_id = request.match_info["entry_id"]
        data = await request.json()
        confidence = data.get("confidence", 0.75)
        result = self.chat.knowledge_quarantine.promote(entry_id, confidence, "manual_promotion")
        if result:
            return web.json_response({"success": True, "entry": result.to_dict()})
        return web.json_response({"success": False, "error": "entry not found"}, status=404)

    async def _handle_quarantine_reject(self, request) -> Any:
        """POST /api/quarantine/{entry_id}/reject — rechaza entrada manualmente."""
        from aiohttp import web
        if not hasattr(self.chat, 'knowledge_quarantine'):
            return web.json_response({"error": "quarantine not initialized"}, status=500)
        entry_id = request.match_info["entry_id"]
        data = await request.json()
        source = data.get("source", "manual")
        result = self.chat.knowledge_quarantine.reject(entry_id, source, "manual_rejection")
        if result:
            return web.json_response({"success": True, "entry": result.to_dict()})
        return web.json_response({"success": False, "error": "entry not found"}, status=404)

    # ============================================================
    # Fase 6B Marketplace handlers
    # ============================================================

    async def _handle_marketplace_list(self, request) -> Any:
        """GET /api/marketplace/capsules — lista cápsulas en marketplace."""
        from aiohttp import web
        from zoe.marketplace import MarketplaceCatalog
        catalog = MarketplaceCatalog()
        capsules = catalog.list_capsules()
        return web.json_response({
            "capsules": [e.to_dict() for e in capsules],
            "count": len(capsules),
            "stats": catalog.get_stats(),
        })

    async def _handle_marketplace_upload(self, request) -> Any:
        """POST /api/marketplace/upload — sube cápsula al marketplace."""
        from aiohttp import web
        from zoe.marketplace import MarketplaceCatalog, MarketplaceUploader
        from pathlib import Path
        
        data = await request.json()
        capsule_name = data.get("name")
        author = data.get("author", "anonymous")
        description = data.get("description", "")
        license_data = data.get("license", {"type": "free"})
        tags = data.get("tags", [])
        author_url = data.get("author_url")
        
        if not capsule_name:
            return web.json_response({"error": "name required"}, status=400)
        
        catalog = MarketplaceCatalog()
        capsules_dir = Path(__file__).parent / "capsules"
        use_cases_dir = Path(__file__).parent / "use_cases"
        uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)
        
        ok, message = uploader.upload_capsule(
            capsule_name=capsule_name,
            author=author,
            description=description,
            license_data=license_data,
            tags=tags,
            author_url=author_url,
        )
        
        return web.json_response({
            "success": ok,
            "name": capsule_name,
            "content_hash": message if ok else None,
            "error": None if ok else message,
        })

    async def _handle_marketplace_download(self, request) -> Any:
        """POST /api/marketplace/download/{name} — descarga e instala cápsula."""
        from aiohttp import web
        from zoe.marketplace import MarketplaceCatalog, MarketplaceDownloader
        from pathlib import Path
        
        name = request.match_info["name"]
        catalog = MarketplaceCatalog()
        capsules_dir = Path(__file__).parent / "capsules"
        use_cases_dir = Path(__file__).parent / "use_cases"
        downloader = MarketplaceDownloader(catalog, capsules_dir, use_cases_dir)
        
        ok, message = downloader.download_capsule(name)
        return web.json_response({
            "success": ok,
            "name": name,
            "message": message,
        })

    async def _handle_marketplace_use_cases(self, request) -> Any:
        """GET /api/marketplace/use_cases — lista casos de uso en marketplace."""
        from aiohttp import web
        from zoe.marketplace import MarketplaceCatalog
        catalog = MarketplaceCatalog()
        use_cases = catalog.list_use_cases()
        return web.json_response({
            "use_cases": [e.to_dict() for e in use_cases],
            "count": len(use_cases),
        })

    async def _handle_marketplace_upload_use_case(self, request) -> Any:
        """POST /api/marketplace/upload_use_case — sube caso de uso al marketplace."""
        from aiohttp import web
        from zoe.marketplace import MarketplaceCatalog, MarketplaceUploader
        from pathlib import Path
        
        data = await request.json()
        use_case_name = data.get("name")
        author = data.get("author", "anonymous")
        description = data.get("description", "")
        license_data = data.get("license", {"type": "free"})
        tags = data.get("tags", [])
        
        if not use_case_name:
            return web.json_response({"error": "name required"}, status=400)
        
        catalog = MarketplaceCatalog()
        capsules_dir = Path(__file__).parent / "capsules"
        use_cases_dir = Path(__file__).parent / "use_cases"
        uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)
        
        ok, message = uploader.upload_use_case(
            use_case_name=use_case_name,
            author=author,
            description=description,
            license_data=license_data,
            tags=tags,
        )
        
        return web.json_response({
            "success": ok,
            "name": use_case_name,
            "content_hash": message if ok else None,
            "error": None if ok else message,
        })

    async def _handle_command(self, cmd: str, data: dict) -> Any:
        """Maneja comandos especiales desde el WS."""
        if cmd == "stats":
            return self.chat.get_stats()
        elif cmd == "memory":
            return self.chat.get_memory()
        elif cmd == "identity":
            return self.chat.get_identity()
        elif cmd == "state":
            return self.chat.get_state()
        elif cmd == "sleep":
            self.chat.metabolism.internal_state.fatigue = 0.9
            self.chat.metabolism.tick(dt=1.0)
            return "ZOE is now sleeping."
        elif cmd == "wake":
            self.chat.metabolism.internal_state.fatigue = 0.0
            self.chat.metabolism.internal_state.energy = 1.0
            from zoe.metabolism.metabolism import MetabolicState
            self.chat.metabolism.state = MetabolicState.AWAKE
            return "ZOE is awake."
        return f"Unknown command: {cmd}"


def _get_dashboard_html() -> str:
    """Devuelve el HTML completo del dashboard (embebido)."""
    return '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZOE v1.0 — Synthetic Cognitive Organism</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a0f; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; height: 100vh; overflow: hidden; }

/* Top bar */
.topbar { display: flex; align-items: center; padding: 8px 16px; background: #12121a; border-bottom: 1px solid #2a2a3a; gap: 16px; }
.topbar .logo { font-size: 18px; font-weight: bold; color: #7c4dff; }
.topbar .llm-select { background: #1a1a2a; color: #e0e0e0; border: 1px solid #3a3a4a; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
.topbar .meta-status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #4caf50; }
.topbar .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #4caf50; }
.topbar .meta-dot.sleeping { background: #2196f3; }
.topbar .meta-dot.drowsy { background: #ff9800; }
.topbar .spacer { flex: 1; }

/* Main layout */
.main { display: grid; grid-template-columns: 260px 1fr 280px; height: calc(100vh - 49px); }
.panel { padding: 12px; overflow-y: auto; }
.panel-left { border-right: 1px solid #1a1a2a; background: #0d0d14; }
.panel-right { border-left: 1px solid #1a1a2a; background: #0d0d14; }
.panel-center { display: flex; flex-direction: column; }

/* State indicators */
.state-item { margin-bottom: 10px; }
.state-label { font-size: 11px; color: #888; margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.5px; }
.state-bar { height: 6px; background: #1a1a2a; border-radius: 3px; overflow: hidden; }
.state-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.state-fill.energy { background: linear-gradient(90deg, #f44336, #ff9800, #4caf50); }
.state-fill.fatigue { background: linear-gradient(90deg, #4caf50, #ff9800, #f44336); }
.state-fill.tension { background: #7c4dff; }
.state-fill.physics { background: #00bcd4; }

/* Tensions */
.tension-item { margin-bottom: 6px; }
.tension-name { font-size: 10px; color: #aaa; }

/* Actions */
.actions { margin-top: 16px; display: flex; flex-direction: column; gap: 6px; }
.action-btn { background: #1a1a2a; color: #e0e0e0; border: 1px solid #2a2a3a; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; text-align: left; transition: background 0.2s; }
.action-btn:hover { background: #2a2a3a; border-color: #7c4dff; }

/* Chat */
.chat-header { padding: 8px 16px; border-bottom: 1px solid #1a1a2a; font-size: 14px; color: #888; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
.msg.user { align-self: flex-end; background: #1a3a5a; color: #fff; }
.msg.zoe { align-self: flex-start; background: #2a1a3a; color: #e0e0e0; border: 1px solid #3a2a4a; }
.msg .ts { font-size: 10px; color: #666; margin-top: 4px; }
.msg .sys { font-size: 10px; color: #7c4dff; margin-top: 2px; }
.chat-input { padding: 12px; border-top: 1px solid #1a1a2a; display: flex; gap: 8px; }
.chat-input input { flex: 1; background: #1a1a2a; color: #e0e0e0; border: 1px solid #2a2a3a; padding: 10px 14px; border-radius: 8px; font-size: 14px; outline: none; }
.chat-input input:focus { border-color: #7c4dff; }
.chat-input button { background: #7c4dff; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; }
.chat-input button:hover { background: #651fff; }
.chat-input button:disabled { background: #3a3a4a; cursor: not-allowed; }

/* Thoughts */
.thoughts-header { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #1a1a2a; }
.thought { background: #12121a; border-left: 3px solid #7c4dff; padding: 8px 10px; margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 12px; }

/* ACD badges (Fase 5) */
.acd-badge { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 8px; vertical-align: middle; }
.acd-l0_reflex { background: #1b5e20; color: #a5d6a7; }
.acd-l1_fast { background: #0d47a1; color: #90caf9; }
.acd-l2_standard { background: #e65100; color: #ffcc80; }
.acd-l3_deep { background: #4a148c; color: #ce93d8; }
.acd-meta { font-size: 10px; color: #888; margin-left: 6px; vertical-align: middle; }
.thought .ts { font-size: 9px; color: #555; }
.thought .sys { font-size: 9px; color: #7c4dff; }

/* Federation */
.fed-section { margin-top: 16px; padding-top: 12px; border-top: 1px solid #1a1a2a; }
.fed-header { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.fed-peer { display: flex; align-items: center; gap: 6px; font-size: 12px; margin-bottom: 4px; }
.fed-dot { width: 6px; height: 6px; border-radius: 50%; background: #4caf50; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a4a; }

/* Responsive */
@media (max-width: 768px) {
  .main { grid-template-columns: 1fr; }
  .panel-left, .panel-right { display: none; }
}
</style>
</head>
<body>

<div class="topbar">
  <span class="logo">🧿 ZOE v1.0</span>
  <select class="llm-select" id="llmSelect" onchange="switchLLM()">
    <option value="mock">Mock</option>
    <option value="ollama">Ollama (Qwen 2.5 3B)</option>
    <option value="zai">ZAI (GLM-4)</option>
    <option value="openai_compatible">OpenAI-compatible</option>
  </select>
  <div class="meta-status">
    <span class="meta-dot" id="metaDot"></span>
    <span id="metaText">Awake</span>
  </div>
  <div class="spacer"></div>
  <span style="font-size:12px;color:#666" id="iterText">Iter: 0</span>
</div>

<div class="main">
  <!-- LEFT PANEL: State -->
  <div class="panel panel-left">
    <div class="state-item">
      <div class="state-label">Energía</div>
      <div class="state-bar"><div class="state-fill energy" id="barEnergy" style="width:100%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Fatiga</div>
      <div class="state-bar"><div class="state-fill fatigue" id="barFatigue" style="width:0%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Arousal</div>
      <div class="state-bar"><div class="state-fill tension" id="barArousal" style="width:30%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Atención</div>
      <div class="state-bar"><div class="state-fill physics" id="barAttention" style="width:50%"></div></div>
    </div>

    <div style="margin-top:16px;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Tensiones</div>
    <div id="tensions"></div>

    <div class="actions">
      <button class="action-btn" onclick="feedFile()">📂 Alimentar documento</button>
      <button class="action-btn" onclick="showStats()">📊 Estadísticas</button>
      <button class="action-btn" onclick="showMemory()">🧠 Memoria</button>
      <button class="action-btn" onclick="showIdentity()">🧿 Identidad</button>
      <button class="action-btn" onclick="toggleSleep()">😴 Dormir / ☀️ Despertar</button>
      <button class="action-btn" onclick="showHistory()">📜 Historial</button>
      <button class="action-btn" onclick="showCapsules()">📦 Cápsulas</button>
      <button class="action-btn" onclick="showQuarantine()">🔒 Cuarentena</button>
      <button class="action-btn" onclick="showMarketplace()">🏪 Marketplace</button>
    </div>

    <div class="fed-section">
      <div class="fed-header">Federación</div>
      <div id="federation"><div style="font-size:11px;color:#666">Sin peers conectados</div></div>
    </div>
  </div>

  <!-- CENTER PANEL: Chat -->
  <div class="panel-center">
    <div class="chat-header">Conversación con ZOE</div>
    <div class="chat-messages" id="chatMessages"></div>
    <div class="chat-input">
      <input type="text" id="chatInput" placeholder="Escribe a ZOE..." onkeypress="if(event.key==='Enter')sendMessage()">
      <button id="sendBtn" onclick="sendMessage()">Enviar</button>
    </div>
  </div>

  <!-- RIGHT PANEL: Thoughts + Federation -->
  <div class="panel panel-right">
    <div class="thoughts-header">💭 Pensamientos Autónomos</div>
    <div id="thoughts"></div>
  </div>
</div>

<input type="file" id="fileInput" style="display:none" onchange="uploadFile(event)">

<script>
let ws = null;
let isSleeping = false;

function connectWS() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${proto}//${location.host}/ws`);

  ws.onopen = () => { console.log('WS connected'); };
  ws.onclose = () => { console.log('WS disconnected, retrying...'); setTimeout(connectWS, 2000); };
  ws.onerror = (e) => { console.error('WS error:', e); };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };
}

function handleMessage(data) {
  if (data.type === 'chat_response') {
    const meta = data.acd_level
      ? ` <span class="acd-badge acd-${data.acd_level.toLowerCase()}">${data.acd_level}</span>`
        + `<span class="acd-meta">${data.latency_ms.toFixed(0)}ms${data.cache_hit ? ' 💾' : ''}</span>`
      : '';
    addMessage('zoe', data.content, data.timestamp, meta);
    document.getElementById('sendBtn').disabled = false;
  } else if (data.type === 'state_update') {
    updateState(data);
  } else if (data.type === 'autonomous_thought') {
    addThought(data);
  } else if (data.type === 'command_result') {
    addMessage('zoe', data.result, data.timestamp);
  } else if (data.type === 'capsule_loaded') {
    // Fase 6A: evento WS de cápsula cargada
    if (data.success) {
      addMessage('zoe', `📦 Cápsula '${data.capsule}' cargada: ${data.entries_loaded} entries. Componentes: ${(data.components_injected||[]).join(', ')}`, data.timestamp);
    } else {
      addMessage('zoe', `✗ Error cargando cápsula '${data.capsule}': ${data.error}`, data.timestamp);
    }
    // Refrescar UI del modal si está abierto
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesList();
      loadCapsulesLoaded();
    }
  } else if (data.type === 'capsule_unloaded') {
    if (data.success) {
      addMessage('zoe', `📦 Cápsula '${data.capsule}' descargada.`, data.timestamp);
    } else {
      addMessage('zoe', `✗ Error descargando '${data.capsule}'`, data.timestamp);
    }
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesList();
      loadCapsulesLoaded();
    }
  } else if (data.type === 'capsules_state') {
    // Update state sin mostrar mensaje
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesLoaded();
    }
  }
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg || !ws || ws.readyState !== 1) return;

  addMessage('user', msg, Date.now()/1000);
  ws.send(JSON.stringify({ type: 'chat', message: msg }));
  input.value = '';
  document.getElementById('sendBtn').disabled = true;
}

function addMessage(role, content, ts, meta) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const time = new Date(ts * 1000).toLocaleTimeString();
  div.innerHTML = `${content}${meta || ''}<div class="ts">${time}</div>`;
  document.getElementById('chatMessages').appendChild(div);
  div.scrollIntoView({ behavior: 'smooth' });
}

function addThought(data) {
  const div = document.createElement('div');
  div.className = 'thought';
  const time = new Date(data.timestamp * 1000).toLocaleTimeString();
  const sys = data.system || 'system1';
  div.innerHTML = `${data.content}<div class="ts">${time}</div><div class="sys">${sys}</div>`;
  const container = document.getElementById('thoughts');
  container.insertBefore(div, container.firstChild);
  // Keep max 20
  while (container.children.length > 20) container.removeChild(container.lastChild);
}

function updateState(data) {
  document.getElementById('barEnergy').style.width = (data.energy * 100) + '%';
  document.getElementById('barFatigue').style.width = (data.fatigue * 100) + '%';
  document.getElementById('barArousal').style.width = (data.arousal * 100) + '%';
  document.getElementById('barAttention').style.width = (data.attention * 100) + '%';
  document.getElementById('iterText').textContent = `Iter: ${data.iterations}`;

  // Metabolism
  const dot = document.getElementById('metaDot');
  const text = document.getElementById('metaText');
  dot.className = 'meta-dot';
  if (data.metabolism === 'sleeping') { dot.classList.add('sleeping'); text.textContent = 'Sleeping'; isSleeping = true; }
  else if (data.metabolism === 'drowsy') { dot.classList.add('drowsy'); text.textContent = 'Drowsy'; }
  else { text.textContent = 'Awake'; isSleeping = false; }

  // Tensions
  if (data.tensions) {
    let html = '';
    for (const [name, t] of Object.entries(data.tensions)) {
      const pct = t.value * 100;
      const shortName = name.replace(/_/g, ' ').replace(/vs/g, '↔').substring(0, 20);
      html += `<div class="tension-item"><div class="tension-name">${shortName} (i=${t.intensity.toFixed(2)})</div><div class="state-bar"><div class="state-fill tension" style="width:${pct}%"></div></div></div>`;
    }
    document.getElementById('tensions').innerHTML = html;
  }
}

function switchLLM() {
  const sel = document.getElementById('llmSelect');
  const backend = sel.value;
  let model = null;
  if (backend === 'ollama') model = 'qwen2.5:3b';
  if (backend === 'zai') model = 'glm-4.6';

  fetch('/llm', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({backend, model}) })
    .then(r => r.json())
    .then(d => { if (d.status === 'switched') addMessage('zoe', `LLM cambiado a ${d.backend}${d.model ? ' ('+d.model+')' : ''}`, Date.now()/1000); })
    .catch(e => addMessage('zoe', `Error cambiando LLM: ${e}`, Date.now()/1000));
}

function feedFile() { document.getElementById('fileInput').click(); }

function uploadFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  fetch('/feed', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(d => { addMessage('zoe', `📚 He leído '${d.filename}' (${d.size} chars). Almacenado en memoria semántica.`, Date.now()/1000); })
    .catch(e => addMessage('zoe', `Error: ${e}`, Date.now()/1000));
  event.target.value = '';
}

function showStats() {
  fetch('/stats').then(r=>r.json()).then(d => {
    let txt = `📊 ESTADÍSTICAS\\nIteraciones: ${d.iterations}\\nPensamientos: ${d.thoughts}\\nSystem 1: ${d.system1_uses||0}\\nSystem 2: ${d.system2_uses||0}\\nWorkspace: ${d.workspace_competitions||0}\\nMemoria: ${d.memory_stats?.total_entries||0} entries\\nConsolidaciones: ${d.consolidation_cycles||0}`;
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function showMemory() {
  fetch('/memory').then(r=>r.json()).then(d => {
    let txt = `🧠 MEMORIA (${d.count} entries)\\n`;
    d.entries.slice(-5).forEach(e => { txt += `[${e.type}] ${e.content.substring(0,60)}...\\n`; });
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function showIdentity() {
  fetch('/identity').then(r=>r.json()).then(d => {
    addMessage('zoe', `🧿 IDENTIDAD\\nNombre: ${d.name}\\nHash: ${d.hash.substring(0,32)}...\\nVectores: ${d.vectors.length}\\nValores: ${d.values.length}\\nPropósito: ${d.purpose.substring(0,80)}...`, Date.now()/1000);
  });
}

function showHistory() {
  fetch('/history').then(r=>r.json()).then(d => {
    let txt = `📜 HISTORIAL (${d.count} mensajes)\\n`;
    d.conversations.slice(-10).forEach(c => { txt += `[${c.role}] ${c.content.substring(0,50)}...\\n`; });
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function toggleSleep() {
  if (isSleeping) { fetch('/wake', {method:'POST'}); }
  else { fetch('/sleep', {method:'POST'}); }
}

// ============================================================
// Fase 6A: Capsules UI
// ============================================================

function showCapsules() {
  document.getElementById('capsulesModal').style.display = 'flex';
  loadCapsulesList();
  loadCapsulesLoaded();
}

function hideCapsules() {
  document.getElementById('capsulesModal').style.display = 'none';
}

async function loadCapsulesList() {
  try {
    const r = await fetch('/api/capsules');
    const d = await r.json();
    const div = document.getElementById('capsulesAvailableList');
    if (!d.available || d.available.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay cápsulas disponibles</div>';
      return;
    }
    div.innerHTML = d.available.map(c => `
      <div class="cap-item">
        <div class="cap-info">
          <div class="cap-name">${c.name} <span class="cap-version">v${c.version}</span></div>
          <div class="cap-meta">
            <span class="cap-trust cap-trust-${c.trust_level}">${c.trust_level}</span>
            <span class="cap-domain">${c.domain}</span>
            ${c.is_loaded ? '<span class="cap-loaded">✓ cargada</span>' : ''}
          </div>
          <div class="cap-desc">${c.description || ''}</div>
        </div>
        <div class="cap-actions">
          ${c.is_loaded 
            ? `<button class="cap-btn cap-btn-unload" onclick="unloadCapsule('${c.name}')">Descargar</button>`
            : `<button class="cap-btn cap-btn-load" onclick="loadCapsule('${c.name}')">Cargar</button>`
          }
          <button class="cap-btn cap-btn-info" onclick="capsuleInfo('${c.name}')">Info</button>
          <button class="cap-btn cap-btn-validate" onclick="validateCapsule('${c.name}')">Validar</button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadCapsulesList error:', e);
  }
}

async function loadCapsulesLoaded() {
  try {
    const r = await fetch('/api/capsules/loaded');
    const d = await r.json();
    const div = document.getElementById('capsulesLoadedList');
    if (!d.loaded || d.loaded.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">Sin cápsulas cargadas</div>';
      return;
    }
    div.innerHTML = d.loaded.map(c => `
      <div class="cap-item cap-loaded-item">
        <div class="cap-info">
          <div class="cap-name">${c.name} <span class="cap-version">v${c.version}</span></div>
          <div class="cap-meta">
            <span class="cap-trust cap-trust-${c.trust_level}">${c.trust_level}</span>
            <span class="cap-entries">${c.entries_injected} entries</span>
          </div>
          <div class="cap-desc">${c.description || ''}</div>
        </div>
        <div class="cap-actions">
          <button class="cap-btn cap-btn-unload" onclick="unloadCapsule('${c.name}')">Descargar</button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadCapsulesLoaded error:', e);
  }
}

function loadCapsule(name) {
  // Fase 6A: usar WebSocket para que el evento se broadcastee a todos los clientes
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ type: 'capsule_action', action: 'load', name: name }));
  } else {
    // Fallback a REST si WS no disponible
    fetch('/api/capsules/load', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name})
    }).then(r => r.json()).then(d => {
      if (d.success) {
        addMessage('zoe', `📦 Cápsula '${name}' cargada: ${d.entries_loaded} entries inyectados.`, Date.now()/1000);
        loadCapsulesList();
        loadCapsulesLoaded();
      } else {
        addMessage('zoe', `✗ Error cargando '${name}': ${d.error}`, Date.now()/1000);
      }
    }).catch(e => console.error('loadCapsule error:', e));
  }
}

function unloadCapsule(name) {
  // Fase 6A: usar WebSocket para broadcast
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ type: 'capsule_action', action: 'unload', name: name }));
  } else {
    // Fallback REST
    fetch('/api/capsules/unload', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name})
    }).then(r => r.json()).then(d => {
      if (d.success) {
        addMessage('zoe', `📦 Cápsula '${name}' descargada.`, Date.now()/1000);
        loadCapsulesList();
        loadCapsulesLoaded();
      } else {
        addMessage('zoe', `✗ Error descargando '${name}'`, Date.now()/1000);
      }
    }).catch(e => console.error('unloadCapsule error:', e));
  }
}

async function capsuleInfo(name) {
  try {
    const r = await fetch(`/api/capsules/${name}/info`);
    const d = await r.json();
    alert(JSON.stringify(d, null, 2));
  } catch (e) {
    console.error('capsuleInfo error:', e);
  }
}

async function validateCapsule(name) {
  try {
    const r = await fetch(`/api/capsules/${name}/validate`, {method: 'POST'});
    const d = await r.json();
    
    let msg = `📦 Validación de '${name}':\n\n`;
    msg += `Válido: ${d.valid ? '✓ SÍ' : '✗ NO'}\n\n`;
    
    if (d.checks && d.checks.length > 0) {
      msg += 'Checks:\n';
      for (const c of d.checks) {
        const icon = c.status === 'pass' ? '✓' : c.status === 'fail' ? '✗' : c.status === 'skip' ? '○' : '⚠';
        msg += `  ${icon} ${c.name}: ${c.status}\n`;
      }
    }
    
    if (d.stats && Object.keys(d.stats).length > 0) {
      msg += '\nEstadísticas:\n';
      for (const [k, v] of Object.entries(d.stats)) {
        msg += `  ${k}: ${v}\n`;
      }
    }
    
    if (d.errors && d.errors.length > 0) {
      msg += '\nErrores:\n';
      for (const e of d.errors) msg += `  ✗ ${e}\n`;
    }
    
    if (d.warnings && d.warnings.length > 0) {
      msg += '\nAvisos:\n';
      for (const w of d.warnings) msg += `  ⚠ ${w}\n`;
    }
    
    alert(msg);
  } catch (e) {
    console.error('validateCapsule error:', e);
    alert('Error: ' + e);
  }
}

async function createCapsule() {
  const name = document.getElementById('newCapName').value.trim();
  const domain = document.getElementById('newCapDomain').value.trim() || 'todo.domain';
  const trust = document.getElementById('newCapTrust').value;
  const desc = document.getElementById('newCapDesc').value.trim() || 'Cápsula creada desde Dashboard';
  const components = document.getElementById('newCapComponents').value || 'semantic,validators';
  const useCases = document.getElementById('newCapUseCases').value.trim();

  if (!name) { alert('Nombre requerido'); return; }

  try {
    const r = await fetch('/api/capsules/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, domain, trust_level: trust, description: desc, components, use_cases: useCases})
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `📦 Cápsula '${name}' creada. Edita los archivos en zoe/capsules/${name}/`, Date.now()/1000);
      document.getElementById('newCapName').value = '';
      document.getElementById('newCapDesc').value = '';
      loadCapsulesList();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('createCapsule error:', e);
    alert('Error: ' + e);
  }
}

// ============================================================
// Fase 6B Punto 3: Cuarentena UI
// ============================================================

function showQuarantine() {
  document.getElementById('quarantineModal').style.display = 'flex';
  loadQuarantineData();
}

function hideQuarantine() {
  document.getElementById('quarantineModal').style.display = 'none';
}

async function loadQuarantineData() {
  try {
    const [listR, statsR] = await Promise.all([
      fetch('/api/quarantine'),
      fetch('/api/quarantine/stats'),
    ]);
    const listD = await listR.json();
    const statsD = await statsR.json();
    
    // Render stats
    const statsDiv = document.getElementById('quarantineStats');
    statsDiv.innerHTML = `
      <div class="q-stat"><span class="q-stat-num">${statsD.total || 0}</span><span class="q-stat-lbl">Total</span></div>
      <div class="q-stat"><span class="q-stat-num q-active">${statsD.active || 0}</span><span class="q-stat-lbl">Activas</span></div>
      <div class="q-stat"><span class="q-stat-num q-verified">${statsD.verified || 0}</span><span class="q-stat-lbl">Verificadas</span></div>
      <div class="q-stat"><span class="q-stat-num q-rejected">${statsD.rejected || 0}</span><span class="q-stat-lbl">Rechazadas</span></div>
      <div class="q-stat"><span class="q-stat-num q-expired">${statsD.expired || 0}</span><span class="q-stat-lbl">Expiradas</span></div>
    `;
    
    // Render active entries
    const activeDiv = document.getElementById('quarantineActive');
    if (!listD.active || listD.active.length === 0) {
      activeDiv.innerHTML = '<div style="color:#666;padding:10px">Sin entries en cuarentena activa.</div>';
    } else {
      activeDiv.innerHTML = listD.active.map(e => `
        <div class="q-item">
          <div class="q-info">
            <div class="q-claim">${e.claim ? e.claim.substring(0, 120) : '(sin claim)'}...</div>
            <div class="q-meta">
              <span class="q-domain">${e.domain || 'sin dominio'}</span>
              <span class="q-source">${e.source}</span>
              <span class="q-conf">conf=${(e.confidence || 0).toFixed(2)}</span>
              <span class="q-reason">${e.reason}</span>
            </div>
            <div class="q-confirm">Confirmaciones: ${e.confirmations ? e.confirmations.length : 0} · Contradicciones: ${e.contradictions ? e.contradictions.length : 0}</div>
          </div>
          <div class="q-actions">
            <button class="q-btn q-btn-promote" onclick="promoteQuarantine('${e.entry_id}')">✓ Promover</button>
            <button class="q-btn q-btn-reject" onclick="rejectQuarantine('${e.entry_id}')">✗ Rechazar</button>
          </div>
        </div>
      `).join('');
    }
    
    // Render pending
    const pendingDiv = document.getElementById('quarantinePending');
    if (!listD.pending || listD.pending.length === 0) {
      pendingDiv.innerHTML = '<div style="color:#666;padding:10px">Sin entries pendientes de verificación.</div>';
    } else {
      pendingDiv.innerHTML = `<div style="color:#888;padding:4px;font-size:11px;">${listD.pending.length} entries pendientes (incluye activas que aún no tienen suficientes verificaciones)</div>`;
    }
  } catch (e) {
    console.error('loadQuarantineData error:', e);
  }
}

async function promoteQuarantine(entryId) {
  try {
    const r = await fetch(`/api/quarantine/${entryId}/promote`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({confidence: 0.75}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `🔒 Entry '${entryId}' promovida (confianza=${d.entry.confidence}).`, Date.now()/1000);
      loadQuarantineData();
    } else {
      addMessage('zoe', `✗ Error promoviendo: ${d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('promoteQuarantine error:', e);
  }
}

async function rejectQuarantine(entryId) {
  try {
    const r = await fetch(`/api/quarantine/${entryId}/reject`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({source: 'dashboard_manual'}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `🔒 Entry '${entryId}' rechazada.`, Date.now()/1000);
      loadQuarantineData();
    } else {
      addMessage('zoe', `✗ Error rechazando: ${d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('rejectQuarantine error:', e);
  }
}

// ============================================================
// Fase 6B Punto 3: Marketplace UI
// ============================================================

function showMarketplace() {
  document.getElementById('marketplaceModal').style.display = 'flex';
  loadMarketplaceCapsules();
  loadMarketplaceUseCases();
}

function hideMarketplace() {
  document.getElementById('marketplaceModal').style.display = 'none';
}

async function loadMarketplaceCapsules() {
  try {
    const r = await fetch('/api/marketplace/capsules');
    const d = await r.json();
    const div = document.getElementById('marketplaceCapsulesList');
    
    if (!d.capsules || d.capsules.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay cápsulas en el marketplace todavía. ¡Sé el primero en subir una!</div>';
      return;
    }
    
    div.innerHTML = d.capsules.map(c => `
      <div class="mp-item">
        <div class="mp-info">
          <div class="mp-name">${c.name} <span class="mp-version">v${c.version}</span></div>
          <div class="mp-meta">
            <span class="mp-license mp-license-${c.license.type}">${c.license.type}</span>
            ${c.license.price > 0 ? `<span class="mp-price">${c.license.price} ${c.license.currency}</span>` : ''}
            <span class="mp-author">por ${c.author}</span>
            <span class="mp-downloads">⬇ ${c.downloads}</span>
            ${c.rating > 0 ? `<span class="mp-rating">★ ${c.rating.toFixed(1)} (${c.rating_count})</span>` : ''}
          </div>
          <div class="mp-desc">${c.description || ''}</div>
          <div class="mp-tags">${(c.tags || []).map(t => `<span class="mp-tag">${t}</span>`).join('')}</div>
        </div>
        <div class="mp-actions">
          <button class="mp-btn mp-btn-download" onclick="downloadFromMarketplace('${c.name}')">⬇ Instalar</button>
        </div>
      </div>
    `).join('');
    
    // Stats
    if (d.stats) {
      document.getElementById('marketplaceStats').innerHTML = `
        <span>Total: ${d.stats.total}</span> · <span>Cápsulas: ${d.stats.capsules}</span> ·
        <span>Casos: ${d.stats.use_cases}</span> · <span>Downloads: ${d.stats.total_downloads}</span>
      `;
    }
  } catch (e) {
    console.error('loadMarketplaceCapsules error:', e);
  }
}

async function loadMarketplaceUseCases() {
  try {
    const r = await fetch('/api/marketplace/use_cases');
    const d = await r.json();
    const div = document.getElementById('marketplaceUseCasesList');
    
    if (!d.use_cases || d.use_cases.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay casos de uso en el marketplace.</div>';
      return;
    }
    
    div.innerHTML = d.use_cases.map(c => `
      <div class="mp-item">
        <div class="mp-info">
          <div class="mp-name">${c.name}</div>
          <div class="mp-meta">
            <span class="mp-license mp-license-${c.license.type}">${c.license.type}</span>
            <span class="mp-author">por ${c.author}</span>
            <span class="mp-downloads">⬇ ${c.downloads}</span>
          </div>
          <div class="mp-desc">${c.description || ''}</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadMarketplaceUseCases error:', e);
  }
}

async function downloadFromMarketplace(name) {
  try {
    const r = await fetch(`/api/marketplace/download/${name}`, {method: 'POST'});
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `🏪 Cápsula '${name}' instalada desde marketplace: ${d.message}`, Date.now()/1000);
      loadMarketplaceCapsules();
    } else {
      addMessage('zoe', `✗ Error descargando: ${d.message || d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('downloadFromMarketplace error:', e);
  }
}

async function uploadToMarketplace() {
  const name = document.getElementById('mpUploadName').value.trim();
  const author = document.getElementById('mpUploadAuthor').value.trim() || 'anonymous';
  const description = document.getElementById('mpUploadDesc').value.trim();
  const licenseType = document.getElementById('mpUploadLicense').value;
  const price = parseFloat(document.getElementById('mpUploadPrice').value) || 0;
  const tags = document.getElementById('mpUploadTags').value.trim().split(',').map(t => t.trim()).filter(t => t);
  
  if (!name) { alert('Nombre de cápsula requerido'); return; }
  
  const licenseData = {type: licenseType};
  if (price > 0) { licenseData.price = price; licenseData.currency = 'EUR'; }
  if (licenseType === 'subscription') { licenseData.subscription_period = 'monthly'; }
  
  try {
    const r = await fetch('/api/marketplace/upload', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, author, description, license: licenseData, tags}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `🏪 Cápsula '${name}' subida al marketplace. Hash: ${d.content_hash.substring(0, 16)}...`, Date.now()/1000);
      document.getElementById('mpUploadName').value = '';
      document.getElementById('mpUploadDesc').value = '';
      document.getElementById('mpUploadTags').value = '';
      loadMarketplaceCapsules();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('uploadToMarketplace error:', e);
    alert('Error: ' + e);
  }
}

async function uploadUseCaseToMarketplace() {
  const name = document.getElementById('mpUCName').value.trim();
  const author = document.getElementById('mpUCAuthor').value.trim() || 'anonymous';
  const description = document.getElementById('mpUCDesc').value.trim();
  const licenseType = document.getElementById('mpUCLicense').value;
  
  if (!name) { alert('Nombre de caso de uso requerido'); return; }
  
  try {
    const r = await fetch('/api/marketplace/upload_use_case', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, author, description, license: {type: licenseType}}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `🏪 Caso de uso '${name}' subido al marketplace.`, Date.now()/1000);
      document.getElementById('mpUCName').value = '';
      document.getElementById('mpUCDesc').value = '';
      loadMarketplaceUseCases();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('uploadUseCaseToMarketplace error:', e);
    alert('Error: ' + e);
  }
}

// Init
connectWS();
// Set initial LLM select
document.getElementById('llmSelect').value = 'mock';
</script>

<!-- Modal Cápsulas (Fase 6A) -->
<div id="capsulesModal" class="capsules-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div class="capsules-modal-content" style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:1100px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">📦 Cápsulas de Conocimiento</h2>
      <button onclick="hideCapsules()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">×</button>
    </div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Disponibles</h3>
        <div id="capsulesAvailableList" style="max-height:400px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Cargadas</h3>
        <div id="capsulesLoadedList" style="max-height:400px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
    </div>
    
    <div style="border-top:1px solid #2a2a3a;padding-top:20px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Crear nueva cápsula</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <input id="newCapName" placeholder="Nombre (snake_case)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapDomain" placeholder="dominio.subdominio" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="newCapTrust" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="curated">curated</option>
          <option value="verified">verified</option>
          <option value="community">community</option>
          <option value="experimental">experimental</option>
        </select>
        <input id="newCapComponents" placeholder="semantic,causal,validators" value="semantic,validators" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapUseCases" placeholder="caso1,caso2 (opcional)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapDesc" placeholder="Descripción breve" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
      </div>
      <button onclick="createCapsule()" style="margin-top:12px;background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Crear cápsula</button>
    </div>
  </div>
</div>

<style>
.cap-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.cap-info { flex:1; }
.cap-name { font-size:13px;font-weight:600;color:#e0e0e0; }
.cap-version { font-size:10px;color:#666;font-weight:normal; }
.cap-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;align-items:center; }
.cap-trust { padding:1px 6px;border-radius:3px;font-weight:600;font-size:9px;text-transform:uppercase; }
.cap-trust-verified { background:#1b5e20;color:#a5d6a7; }
.cap-trust-curated { background:#0d47a1;color:#90caf9; }
.cap-trust-community { background:#e65100;color:#ffcc80; }
.cap-trust-experimental { background:#4a148c;color:#ce93d8; }
.cap-domain { color:#666; }
.cap-loaded { color:#448158; }
.cap-desc { font-size:11px;color:#888;margin-top:4px; }
.cap-actions { display:flex;gap:6px; }
.cap-btn { background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px; }
.cap-btn:hover { background:#2a2a3a; }
.cap-btn-load { background:#1b5e20;border-color:#2e7d32;color:#a5d6a7; }
.cap-btn-unload { background:#4a148c;border-color:#6a1b9a;color:#ce93d8; }
.cap-btn-info { background:#0d47a1;border-color:#1565c0;color:#90caf9; }
.cap-btn-validate { background:#e65100;border-color:#ef6c00;color:#ffcc80; }

/* Cuarentena UI */
.q-stat { display:inline-block;text-align:center;margin:0 12px; }
.q-stat-num { display:block;font-size:24px;font-weight:700; }
.q-stat-lbl { font-size:10px;color:#888;text-transform:uppercase; }
.q-active { color:#ffcc80; }
.q-verified { color:#a5d6a7; }
.q-rejected { color:#ef9a9a; }
.q-expired { color:#888; }
.q-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.q-info { flex:1; }
.q-claim { font-size:12px;color:#e0e0e0;font-style:italic; }
.q-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;flex-wrap:wrap; }
.q-domain { background:#1a1a24;padding:1px 6px;border-radius:3px; }
.q-source { color:#90caf9; }
.q-conf { color:#ce93d8; }
.q-reason { color:#ef9a9a; }
.q-confirm { font-size:10px;color:#666;margin-top:3px; }
.q-actions { display:flex;gap:6px; }
.q-btn { border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px;color:white; }
.q-btn-promote { background:#2e7d32; }
.q-btn-reject { background:#c62828; }

/* Marketplace UI */
.mp-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.mp-info { flex:1; }
.mp-name { font-size:13px;font-weight:600;color:#e0e0e0; }
.mp-version { font-size:10px;color:#666;font-weight:normal; }
.mp-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;align-items:center;flex-wrap:wrap; }
.mp-license { padding:1px 6px;border-radius:3px;font-weight:600;font-size:9px;text-transform:uppercase; }
.mp-license-free { background:#1b5e20;color:#a5d6a7; }
.mp-license-opensource { background:#0d47a1;color:#90caf9; }
.mp-license-research { background:#4a148c;color:#ce93d8; }
.mp-license-paid { background:#e65100;color:#ffcc80; }
.mp-license-subscription { background:#bf360c;color:#ffab91; }
.mp-price { color:#ffcc80;font-weight:600; }
.mp-author { color:#90caf9; }
.mp-downloads { color:#888; }
.mp-rating { color:#ffd54f; }
.mp-desc { font-size:11px;color:#888;margin-top:4px; }
.mp-tags { margin-top:4px; }
.mp-tag { display:inline-block;background:#1a1a24;color:#aaa;padding:1px 6px;border-radius:3px;font-size:9px;margin-right:4px; }
.mp-actions { display:flex;gap:6px; }
.mp-btn { border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:11px;color:white; }
.mp-btn-download { background:#1565c0; }
</style>

<!-- Modal Cuarentena (Fase 6B) -->
<div id="quarantineModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:900px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">🔒 Conocimiento en Cuarentena</h2>
      <button onclick="hideQuarantine()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">×</button>
    </div>
    
    <div id="quarantineStats" style="text-align:center;margin-bottom:20px;padding:16px;background:#0a0a12;border-radius:6px;"></div>
    
    <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Entradas Activas</h3>
    <div id="quarantineActive" style="max-height:350px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;margin-bottom:16px;"></div>
    
    <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Pendientes</h3>
    <div id="quarantinePending" style="background:#0a0a12;border-radius:6px;padding:8px;"></div>
  </div>
</div>

<!-- Modal Marketplace (Fase 6B) -->
<div id="marketplaceModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:1100px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">🏪 Marketplace</h2>
      <button onclick="hideMarketplace()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">×</button>
    </div>
    
    <div id="marketplaceStats" style="font-size:11px;color:#888;margin-bottom:16px;padding:8px;background:#0a0a12;border-radius:4px;"></div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Cápsulas Disponibles</h3>
        <div id="marketplaceCapsulesList" style="max-height:300px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Casos de Uso Disponibles</h3>
        <div id="marketplaceUseCasesList" style="max-height:300px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
    </div>
    
    <div style="border-top:1px solid #2a2a3a;padding-top:20px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Subir Cápsula al Marketplace</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <input id="mpUploadName" placeholder="Nombre cápsula" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadAuthor" placeholder="Autor" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="mpUploadLicense" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="free">Free</option>
          <option value="opensource">Open Source</option>
          <option value="research">Research</option>
          <option value="paid">Paid</option>
          <option value="subscription">Subscription</option>
        </select>
        <input id="mpUploadPrice" type="number" placeholder="Precio EUR (si paid/sub)" value="0" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadTags" placeholder="tags, separados, por coma" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadDesc" placeholder="Descripción" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
      </div>
      <button onclick="uploadToMarketplace()" style="background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Subir cápsula</button>
    </div>
    
    <div style="border-top:1px solid #2a2a3a;padding-top:20px;margin-top:16px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Subir Caso de Uso al Marketplace</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <input id="mpUCName" placeholder="Nombre caso (sin .yaml)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUCAuthor" placeholder="Autor" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="mpUCLicense" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="free">Free</option>
          <option value="opensource">Open Source</option>
          <option value="research">Research</option>
          <option value="paid">Paid</option>
        </select>
        <input id="mpUCDesc" placeholder="Descripción" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;grid-column:span 3;">
      </div>
      <button onclick="uploadUseCaseToMarketplace()" style="background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Subir caso de uso</button>
    </div>
  </div>
</div>
</body>
</html>'''


async def run_dashboard(
    backend: str = "mock",
    model: str = None,
    use_case: str = None,
    port: int = 8642,
    db_path: str = None,
):
    """Ejecuta el dashboard web."""
    server = DashboardServer(
        backend=backend,
        model=model,
        use_case=use_case,
        port=port,
        db_path=db_path,
    )

    await server.initialize()
    await server.start()

    print("=" * 60)
    print("  ZOE v1.0 — Web Dashboard")
    print("=" * 60)
    print(f"  URL: http://localhost:{port}")
    print(f"  LLM: {backend}")
    print(f"  Identity: {server.chat.vault.identity_hash[:16]}...")
    print(f"  Memory: {server.chat.memory.count()} entries")
    print()
    print("  Abre tu navegador en la URL de arriba.")
    print("  Presiona Ctrl+C para detener.")
    print("=" * 60)

    # Mantener corriendo
    try:
        while True:
            await asyncio.sleep(1.0)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await server.stop()
        print("\nDashboard detenido.")


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 — Web Dashboard")
    parser.add_argument("--backend", choices=["mock", "zai", "ollama", "openai_compatible"], default="mock")
    parser.add_argument("--model", help="Modelo específico")
    parser.add_argument("--use-case", help="Caso de uso YAML")
    parser.add_argument("--port", type=int, default=8642)
    parser.add_argument("--db-path", default="zoe_data/dashboard_memory.db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    try:
        asyncio.run(run_dashboard(
            backend=args.backend,
            model=args.model,
            use_case=args.use_case,
            port=args.port,
            db_path=args.db_path,
        ))
    except KeyboardInterrupt:
        print("\nAdiós.")


if __name__ == "__main__":
    main()
