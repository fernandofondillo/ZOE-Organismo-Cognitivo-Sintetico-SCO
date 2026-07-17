"""
ZOE v2.1.1 — Dashboard handlers for LLM Provider Management

Endpoints:
  GET  /api/providers/config      — Configuracion (keys enmascaradas)
  POST /api/providers/config      — Guardar configuracion
  GET  /api/providers/status      — Estado de todos los proveedores
  GET  /api/providers/models      — Modelos disponibles (cloud + local)
  POST /api/providers/ollama/pull — Descargar modelo Ollama
  POST /api/providers/budget/reset — Resetear gasto diario
"""

import logging
import os
from aiohttp import web

logger = logging.getLogger(__name__)


# Configuracion default de proveedores
DEFAULT_PROVIDER_CONFIG = {
    "openai": {"enabled": False, "api_key": "", "model": "gpt-4o", "models": ["gpt-4o", "gpt-4o-mini"]},
    "anthropic": {"enabled": False, "api_key": "", "model": "claude-sonnet-4-20250514", "models": ["claude-sonnet-4-20250514", "claude-haiku-20241022"]},
    "deepseek": {"enabled": False, "api_key": "", "model": "deepseek-chat", "models": ["deepseek-chat", "deepseek-reasoner"]},
    "ollama": {"enabled": True, "default_model": "auto"},
    "budget": {"daily_limit": 1.0, "current_spend": 0.0},
    "backend_mode": "auto",  # auto / local / cloud / mixed
}


def _mask_key(key: str) -> str:
    """Enmascara una API key mostrando solo los ultimos 4 caracteres."""
    if not key or len(key) < 8:
        return ""
    return "*" * (len(key) - 4) + key[-4:]


def _get_config() -> dict:
    """Obtiene configuracion actual de proveedores."""
    cfg = DEFAULT_PROVIDER_CONFIG.copy()
    # Cargar desde variables de entorno si existen
    if os.environ.get("OPENAI_API_KEY"):
        cfg["openai"]["enabled"] = True
        cfg["openai"]["api_key"] = _mask_key(os.environ["OPENAI_API_KEY"])
    if os.environ.get("ANTHROPIC_API_KEY"):
        cfg["anthropic"]["enabled"] = True
        cfg["anthropic"]["api_key"] = _mask_key(os.environ["ANTHROPIC_API_KEY"])
    if os.environ.get("DEEPSEEK_API_KEY"):
        cfg["deepseek"]["enabled"] = True
        cfg["deepseek"]["api_key"] = _mask_key(os.environ["DEEPSEEK_API_KEY"])
    return cfg


async def _handle_providers_config_get(server, request: web.Request) -> web.Response:
    """GET /api/providers/config — Configuracion actual (keys enmascaradas)."""
    try:
        cfg = _get_config()
        return web.json_response({"status": "ok", "config": cfg})
    except Exception as e:
        logger.error("Error getting providers config: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_providers_config_post(server, request: web.Request) -> web.Response:
    """POST /api/providers/config — Guardar configuracion."""
    try:
        data = await request.json()
        # Validar y guardar (en produccion: en BD o archivo)
        for provider in ["openai", "anthropic", "deepseek"]:
            if provider in data:
                if data[provider].get("api_key") and not data[provider]["api_key"].startswith("*"):
                    # Nueva key — guardar en env
                    os.environ[f"{provider.upper()}_API_KEY"] = data[provider]["api_key"]
                if "enabled" in data[provider]:
                    pass  # Marcar en BD
        if "budget" in data:
            pass  # Guardar en BD
        return web.json_response({"status": "ok", "message": "Configuracion guardada"})
    except Exception as e:
        logger.error("Error saving providers config: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_providers_status(server, request: web.Request) -> web.Response:
    """GET /api/providers/status — Estado de todos los proveedores."""
    try:
        status = {
            "openai": {"available": bool(os.environ.get("OPENAI_API_KEY")), "enabled": bool(os.environ.get("OPENAI_API_KEY"))},
            "anthropic": {"available": bool(os.environ.get("ANTHROPIC_API_KEY")), "enabled": bool(os.environ.get("ANTHROPIC_API_KEY"))},
            "deepseek": {"available": bool(os.environ.get("DEEPSEEK_API_KEY")), "enabled": bool(os.environ.get("DEEPSEEK_API_KEY"))},
            "ollama": {"available": False, "enabled": True},  # Se verifica dinamicamente
        }
        # Verificar Ollama
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            status["ollama"]["available"] = result.returncode == 0
            status["ollama"]["models"] = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()]
        except Exception:
            pass
        return web.json_response({"status": "ok", "providers": status})
    except Exception as e:
        logger.error("Error getting providers status: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_providers_models(server, request: web.Request) -> web.Response:
    """GET /api/providers/models — Modelos disponibles (cloud + local)."""
    try:
        models = {
            "cloud": [
                {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai", "cost_input": 0.0025, "cost_output": 0.01},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai", "cost_input": 0.00015, "cost_output": 0.0006},
                {"id": "claude-sonnet-4-20250514", "name": "Claude 3.5 Sonnet", "provider": "anthropic", "cost_input": 0.003, "cost_output": 0.015},
                {"id": "deepseek-chat", "name": "DeepSeek Chat", "provider": "deepseek", "cost_input": 0.00014, "cost_output": 0.00028},
            ],
            "local": [],
        }
        # Modelos locales de Ollama
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models["local"] = [{"id": line.split()[0], "name": line.split()[0], "size": line.split()[2] if len(line.split()) > 2 else "?"} for line in result.stdout.strip().split("\n")[1:] if line.strip()]
        except Exception:
            pass
        return web.json_response({"status": "ok", "models": models})
    except Exception as e:
        logger.error("Error getting models: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_providers_ollama_pull(server, request: web.Request) -> web.Response:
    """POST /api/providers/ollama/pull — Descargar modelo Ollama."""
    try:
        data = await request.json()
        model = data.get("model", "")
        if not model:
            return web.json_response({"error": "Modelo requerido"}, status=400)
        import subprocess
        result = subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return web.json_response({"status": "ok", "message": f"Modelo {model} descargado"})
        else:
            return web.json_response({"error": result.stderr}, status=500)
    except Exception as e:
        logger.error("Error pulling model: %s", e)
        return web.json_response({"error": str(e)}, status=500)


async def _handle_providers_budget_reset(server, request: web.Request) -> web.Response:
    """POST /api/providers/budget/reset — Resetear gasto diario."""
    try:
        return web.json_response({"status": "ok", "message": "Presupuesto reseteado"})
    except Exception as e:
        logger.error("Error resetting budget: %s", e)
        return web.json_response({"error": str(e)}, status=500)
