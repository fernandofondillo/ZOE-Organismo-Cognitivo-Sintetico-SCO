"""
ZOE v1.0 -- Web Dashboard Server

Backward compatibility shim.
El dashboard ha sido refactorizado en zoe.dashboard/ como paquete modular.
Este archivo re-exporta DashboardServer y run_dashboard para compatibilidad.

Uso:
    python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b
    python -m zoe.web_dashboard --backend zai
    python -m zoe.web_dashboard --backend mock --port 8642
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

# Re-export everything from the modular dashboard package
from .dashboard.server import DashboardServer
from .dashboard.utils import _sanitize_name, _safe_path
# Sprint 5.12 — Re-export _get_dashboard_html for backward compatibility with
# tests and external callers that import it from zoe.web_dashboard directly.
# Source: zoe/dashboard/html/dashboard_html.py
from .dashboard.html.dashboard_html import _get_dashboard_html

logger = logging.getLogger(__name__)

__all__ = [
    "DashboardServer",
    "run_dashboard",
    "_sanitize_name",
    "_safe_path",
    "_get_dashboard_html",
    "main",
]


async def run_dashboard(
    backend: str = "mock",
    model: str = None,
    use_case: str = None,
    port: int = 8642,
    db_path: str = None,
    api_key: str = None,
    base_url: str = None,
    host: str = "127.0.0.1",
    auth_token: str = None,
):
    """Ejecuta el dashboard web."""
    server = DashboardServer(
        backend=backend,
        model=model,
        use_case=use_case,
        port=port,
        db_path=db_path,
        api_key=api_key,
        base_url=base_url,
        host=host,
        auth_token=auth_token,
    )

    await server.initialize()
    await server.start()

    # Sprint 5.13 B6: NEVER print the auth_token to stdout. Logs are captured
    # by container log aggregators and would leak the bearer token.
    # Instead, build the URL with the token (browser auto-strips it via JS)
    # and tell the user where to find the token if they need it manually.
    from pathlib import Path
    _token_file = Path(server.db_path).parent / "dashboard_token.txt" if server.db_path else None
    _token_loc = str(_token_file) if _token_file else "data/dashboard_token.txt"

    print("=" * 60)
    print("  ZOE v2.1.2 -- Web Dashboard")
    print("=" * 60)
    print(f"  URL (abrir en navegador):")
    print(f"    http://localhost:{port}/?token=<token-embebido-en-url>")
    print()
    print(f"  LLM: {backend}")
    print(f"  Identity: {server.chat.vault.identity_hash[:16]}...")
    print(f"  Memory: {server.chat.memory.count()} entries")
    print(f"  Token persistido en: {_token_loc} (chmod 0600)")
    print()
    print("  Abriendo navegador automaticamente con token embebido...")
    print("  (Si no se abre, copia el token del archivo de arriba y abre")
    print(f"   http://localhost:{port}/?token=TU_TOKEN manualmente)")
    print("  Presiona Ctrl+C para detener.")
    print("=" * 60)

    # Sprint 5.13 B6: Abrir el navegador CON el token embebido en la URL.
    # El navegador recibe la URL completa (con token), el JS del dashboard
    # lo extrae, lo guarda en localStorage, y limpia la URL con
    # history.replaceState. Asi el token NO aparece en logs.
    import threading
    import webbrowser
    def _open_browser():
        import time
        time.sleep(2.0)  # esperar a que el servidor arranque
        url_with_token = f"http://localhost:{port}/?token={server.auth_token}"
        try:
            webbrowser.open(url_with_token)
        except Exception:
            pass  # navegador no disponible (headless, server, etc.)
    threading.Thread(target=_open_browser, daemon=True).start()

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
    parser = argparse.ArgumentParser(description="ZOE v1.0 -- Web Dashboard")
    parser.add_argument(
        "--backend",
        choices=["mock", "zai", "ollama", "openai_compatible", "anthropic", "pattern"],
        default="mock",
        help="Backend LLM (default: mock). 'pattern' = PatternSpeaker sin LLM.",
    )
    parser.add_argument(
        "--model",
        help="Modelo especifico del backend. Usa 'auto' para routing automatico por nivel ACD (solo ollama).",
    )
    parser.add_argument("--use-case", help="Caso de uso YAML")
    parser.add_argument("--port", type=int, default=8642)
    # Sprint 5.12 GAP-R: si no se pasa --db-path, usar $ZOE_DATA/dashboard_memory.db
    # si la variable existe (definida por los lanzadores del SSD), o el default
    # relativo en caso contrario. Evita que ZOE se cree en el CWD del Mac.
    _default_db = os.path.join(
        os.environ.get("ZOE_DATA", "zoe_data"),
        "dashboard_memory.db",
    )
    parser.add_argument("--db-path", default=_default_db)
    parser.add_argument("--api-key", help="API key para backends cloud")
    parser.add_argument("--base-url", help="URL base para APIs compatibles")
    parser.add_argument("--host", default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1 -- use 0.0.0.0 to expose to network)")
    parser.add_argument("--auth-token", default=None,
        help="Token required for all requests (Bearer token)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    try:
        asyncio.run(run_dashboard(
            backend=args.backend,
            model=args.model,
            use_case=args.use_case,
            port=args.port,
            db_path=args.db_path,
            api_key=args.api_key,
            base_url=args.base_url,
            host=args.host,
            auth_token=args.auth_token,
        ))
    except KeyboardInterrupt:
        print("\nAdios.")


if __name__ == "__main__":
    main()
