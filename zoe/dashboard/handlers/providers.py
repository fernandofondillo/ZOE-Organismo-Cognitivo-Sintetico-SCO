"""Handlers para gestion de proveedores API/LLM y configuracion de backend."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from typing import Any

from aiohttp import web

logger = logging.getLogger(__name__)

# Ruta para persistir la configuracion de proveedores
_PROVIDERS_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "zoe_data", "providers_config.json"
)


def _ensure_config_dir() -> None:
    """Asegura que el directorio de configuracion existe."""
    os.makedirs(os.path.dirname(_PROVIDERS_CONFIG_PATH), exist_ok=True)


def _load_config() -> dict:
    """Carga la configuracion de proveedores desde disco."""
    _ensure_config_dir()
    if os.path.exists(_PROVIDERS_CONFIG_PATH):
        try:
            with open(_PROVIDERS_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error cargando config de proveedores: {e}")
    return _default_config()


def _save_config(config: dict) -> None:
    """Guarda la configuracion de proveedores en disco."""
    _ensure_config_dir()
    try:
        with open(_PROVIDERS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando config de proveedores: {e}")


def _default_config() -> dict:
    """Configuracion por defecto de proveedores."""
    return {
        "providers": {
            "openai": {
                "enabled": False,
                "api_key": "",
                "model": "gpt-4o",
                "available_models": ["gpt-4o", "gpt-4o-mini"],
            },
            "anthropic": {
                "enabled": False,
                "api_key": "",
                "model": "claude-sonnet",
                "available_models": ["claude-sonnet", "claude-haiku"],
            },
            "deepseek": {
                "enabled": False,
                "api_key": "",
                "model": "deepseek-chat",
                "available_models": ["deepseek-chat", "deepseek-coder"],
            },
        },
        "ollama": {
            "enabled": True,
            "default_model": "qwen2.5:3b",
            "installed_models": [],
        },
        "backend": {
            "mode": "auto",
            "available_modes": [
                {"id": "auto", "name": "Auto (ACD)", "description": "Adaptive Cognitive Depth: elige automaticamente el backend segun la complejidad de la consulta"},
                {"id": "local", "name": "Local (Ollama)", "description": "Usa siempre modelos locales via Ollama. Sin coste, pero puede ser mas lento"},
                {"id": "cloud", "name": "Cloud (API)", "description": "Usa siempre proveedores cloud (OpenAI, Anthropic, DeepSeek). Maxima calidad, con coste"},
                {"id": "mixed", "name": "Mixto", "description": "Intenta primero local, fallback a cloud si el local no responde"},
            ],
        },
        "budget": {
            "daily_limit_usd": 10.0,
            "spent_today_usd": 0.0,
            "alert_threshold": 0.8,
        },
    }


def _mask_api_key(key: str) -> str:
    """Enmascara una API key para mostrarla de forma segura."""
    if not key or len(key) < 8:
        return ""
    return key[:4] + "****" + key[-4:]


def _sanitize_config_for_display(config: dict) -> dict:
    """Devuelve una copia de la config con las API keys enmascaradas."""
    import copy
    display = copy.deepcopy(config)
    for provider in display.get("providers", {}).values():
        if "api_key" in provider and provider["api_key"]:
            provider["api_key"] = _mask_api_key(provider["api_key"])
    return display


async def _handle_providers_config_get(server, request) -> Any:
    """GET /api/providers/config -- Devuelve la configuracion de proveedores."""
    config = _load_config()
    return web.json_response(_sanitize_config_for_display(config))


async def _handle_providers_config_post(server, request) -> Any:
    """POST /api/providers/config -- Guarda la configuracion de proveedores."""
    try:
        body = await request.json()
        config = _load_config()

        # Actualizar proveedores
        if "providers" in body:
            for name, settings in body["providers"].items():
                if name in config["providers"]:
                    if "enabled" in settings:
                        config["providers"][name]["enabled"] = bool(settings["enabled"])
                    if "model" in settings:
                        config["providers"][name]["model"] = settings["model"]
                    # Solo actualizar api_key si se envia un valor nuevo (no enmascarado)
                    if "api_key" in settings and settings["api_key"] and "****" not in settings["api_key"]:
                        config["providers"][name]["api_key"] = settings["api_key"]

        # Actualizar backend
        if "backend" in body:
            if "mode" in body["backend"]:
                mode = body["backend"]["mode"]
                valid_modes = [m["id"] for m in config["backend"]["available_modes"]]
                if mode in valid_modes:
                    config["backend"]["mode"] = mode

        # Actualizar budget
        if "budget" in body:
            if "daily_limit_usd" in body["budget"]:
                config["budget"]["daily_limit_usd"] = float(body["budget"]["daily_limit_usd"])
            if "spent_today_usd" in body["budget"]:
                config["budget"]["spent_today_usd"] = float(body["budget"]["spent_today_usd"])
            if "alert_threshold" in body["budget"]:
                config["budget"]["alert_threshold"] = float(body["budget"]["alert_threshold"])

        # Actualizar ollama default_model
        if "ollama" in body and "default_model" in body["ollama"]:
            config["ollama"]["default_model"] = body["ollama"]["default_model"]

        _save_config(config)
        return web.json_response({"success": True, "config": _sanitize_config_for_display(config)})
    except Exception as e:
        logger.error(f"Error guardando config de proveedores: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def _handle_providers_status(server, request) -> Any:
    """GET /api/providers/status -- Devuelve el estado de todos los proveedores."""
    config = _load_config()
    status = {}

    # Estado de proveedores cloud
    for name, settings in config.get("providers", {}).items():
        has_key = bool(settings.get("api_key", ""))
        status[name] = {
            "enabled": settings.get("enabled", False),
            "configured": has_key and len(settings.get("api_key", "")) > 10,
            "model": settings.get("model", ""),
        }

    # Estado de Ollama
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=15
        )
        ollama_running = result.returncode == 0
        installed = []
        if ollama_running:
            # Parsear salida de 'ollama list'
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:  # Saltar header
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    model_size = parts[-2] + " " + parts[-1] if len(parts) >= 2 else "?"
                    installed.append({"name": model_name, "size": model_size})
        config["ollama"]["installed_models"] = [m["name"] for m in installed]
        _save_config(config)
        status["ollama"] = {
            "enabled": config["ollama"].get("enabled", True),
            "running": ollama_running,
            "installed_models": installed,
            "default_model": config["ollama"].get("default_model", ""),
            "model_count": len(installed),
        }
    except FileNotFoundError:
        status["ollama"] = {
            "enabled": False,
            "running": False,
            "installed_models": [],
            "default_model": config["ollama"].get("default_model", ""),
            "error": "Ollama no instalado",
        }
    except Exception as e:
        status["ollama"] = {
            "enabled": False,
            "running": False,
            "installed_models": [],
            "error": str(e),
        }

    # Info de budget
    budget = config.get("budget", {})
    limit = budget.get("daily_limit_usd", 10.0)
    spent = budget.get("spent_today_usd", 0.0)
    threshold = budget.get("alert_threshold", 0.8)
    status["budget"] = {
        "daily_limit_usd": limit,
        "spent_today_usd": spent,
        "remaining_usd": max(0.0, limit - spent),
        "usage_percent": (spent / limit * 100) if limit > 0 else 0,
        "alert_active": (spent / limit) >= threshold if limit > 0 else False,
    }

    status["backend"] = config.get("backend", {})

    return web.json_response(status)


async def _handle_providers_models(server, request) -> Any:
    """GET /api/providers/models -- Lista todos los modelos disponibles."""
    config = _load_config()
    models = []

    # Modelos cloud
    for provider_name, settings in config.get("providers", {}).items():
        for m in settings.get("available_models", []):
            models.append({
                "id": f"{provider_name}/{m}",
                "provider": provider_name,
                "name": m,
                "type": "cloud",
                "enabled": settings.get("enabled", False),
            })

    # Modelos locales
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    models.append({
                        "id": f"ollama/{parts[0]}",
                        "provider": "ollama",
                        "name": parts[0],
                        "type": "local",
                        "enabled": True,
                        "size": parts[-2] + " " + parts[-1] if len(parts) >= 2 else "?",
                    })
    except Exception:
        pass

    return web.json_response({"models": models, "count": len(models)})


async def _handle_ollama_pull(server, request) -> Any:
    """POST /api/providers/ollama/pull -- Descarga un modelo de Ollama."""
    try:
        body = await request.json()
        model_name = body.get("model", "").strip()
        if not model_name:
            return web.json_response({"success": False, "error": "Nombre de modelo requerido"}, status=400)

        # Iniciar descarga en background
        import asyncio
        asyncio.create_task(_pull_ollama_model(model_name))

        return web.json_response({
            "success": True,
            "message": f"Descarga de '{model_name}' iniciada en segundo plano",
        })
    except Exception as e:
        logger.error(f"Error iniciando descarga de modelo: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def _pull_ollama_model(model_name: str) -> None:
    """Descarga un modelo de Ollama en segundo plano."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ollama", "pull", model_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            logger.info(f"Modelo {model_name} descargado correctamente")
        else:
            logger.error(f"Error descargando {model_name}: {stderr.decode()}")
    except Exception as e:
        logger.error(f"Excepcion descargando {model_name}: {e}")


async def _handle_providers_reset_budget(server, request) -> Any:
    """POST /api/providers/budget/reset -- Resetea el gasto diario."""
    config = _load_config()
    config["budget"]["spent_today_usd"] = 0.0
    _save_config(config)
    return web.json_response({"success": True, "spent_today_usd": 0.0})
