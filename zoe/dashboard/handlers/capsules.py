"""Handlers de capsulas: /api/capsules/* (7 endpoints)."""

import subprocess
import sys
from pathlib import Path
from typing import Any

from aiohttp import web

from ..utils import _sanitize_name, _safe_path


async def _handle_capsules_list(server, request) -> Any:
    """Lista todas las capsulas disponibles."""
    if not server.chat or not hasattr(server.chat, 'capsule_manager'):
        return web.json_response({"error": "capsule_manager not initialized"}, status=500)
    available = server.chat.capsule_manager.list_available()
    return web.json_response({
        "available": available,
        "count": len(available),
    })


async def _handle_capsules_loaded(server, request) -> Any:
    """Lista capsulas cargadas actualmente."""
    if not server.chat or not hasattr(server.chat, 'capsule_manager'):
        return web.json_response({"error": "capsule_manager not initialized"}, status=500)
    loaded = server.chat.capsule_manager.list_loaded()
    return web.json_response({
        "loaded": loaded,
        "count": len(loaded),
    })


async def _handle_capsule_load(server, request) -> Any:
    """Carga una capsula en caliente."""
    if not server.chat or not hasattr(server.chat, 'capsule_manager'):
        return web.json_response({"error": "capsule_manager not initialized"}, status=500)
    data = await request.json()
    name = data.get("name")
    if not name:
        return web.json_response({"error": "name required"}, status=400)
    result = server.chat.capsule_manager.load(name)
    return web.json_response({
        "success": result.success,
        "capsule": result.capsule_name,
        "entries_loaded": result.entries_loaded,
        "components_injected": result.components_injected,
        "trajectory_hash": result.trajectory_hash,
        "error": result.error,
    })


async def _handle_capsule_unload(server, request) -> Any:
    """Descarga una capsula."""
    if not server.chat or not hasattr(server.chat, 'capsule_manager'):
        return web.json_response({"error": "capsule_manager not initialized"}, status=500)
    data = await request.json()
    name = data.get("name")
    if not name:
        return web.json_response({"error": "name required"}, status=400)
    ok = server.chat.capsule_manager.unload(name)
    return web.json_response({
        "success": ok,
        "capsule": name,
    })


async def _handle_capsule_info(server, request) -> Any:
    """Info detallada de una capsula."""
    if not server.chat or not hasattr(server.chat, 'capsule_manager'):
        return web.json_response({"error": "capsule_manager not initialized"}, status=500)
    name = _sanitize_name(request.match_info["name"])
    info = server.chat.capsule_manager.get_info(name)
    if not info:
        return web.json_response({"error": "capsule not found"}, status=404)
    return web.json_response(info)


async def _handle_capsule_validate(server, request) -> Any:
    """
    Valida una capsula: schema + contenido + validators.

    Fase 6A Punto 4: endpoint para validar capsulas desde el Dashboard.
    Ejecuta:
    1. Validacion de schema (capsule.yaml)
    2. Carga de contenido (JSONL files)
    3. Tests de validators (si los tiene)
    4. Hash verification
    """
    name = request.match_info["name"]

    # Localizar la capsula (sanitizado para prevenir path traversal)
    capsules_dir = Path(__file__).resolve().parent.parent.parent / "capsules"
    try:
        cap_dir = _safe_path(capsules_dir, name)
    except ValueError as exc:
        return web.json_response({"valid": False, "errors": [str(exc)]}, status=400)

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
    # Sprint 5.7.3 FIX: cwd dinamico
    _zoe_root = Path(__file__).resolve().parent.parent.parent.parent  # zoe-sco/
    try:
        cmd = [sys.executable, "-m", "zoe.capsules.scaffold", "validate", "--name", name]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                              cwd=str(_zoe_root))
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

            # 3. Verificar entradas con campos minimos
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
                    if hasattr(cap.validators, "validate_response"):
                        ok, reason = cap.validators.validate_response("test response", context={})
                        result["checks"].append({
                            "name": "validators_test",
                            "status": "pass" if ok else "warning",
                            "reason": reason,
                        })
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


async def _handle_capsule_create(server, request) -> Any:
    """Crea una nueva capsula usando el scaffold CLI."""
    data = await request.json()
    name = data.get("name")
    domain = data.get("domain", "todo.domain")
    trust_level = data.get("trust_level", "curated")
    description = data.get("description", "Capsula creada desde Dashboard")
    components = data.get("components", "semantic,validators")
    use_cases = data.get("use_cases", "")

    if not name:
        return web.json_response({"error": "name required"}, status=400)

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

    # Sprint 5.7.3 FIX: cwd dinamico
    _zoe_root = Path(__file__).resolve().parent.parent.parent.parent
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(_zoe_root))
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


