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

# Re-export everything from the modular dashboard package
from .dashboard.server import DashboardServer
from .dashboard.utils import _sanitize_name, _safe_path

logger = logging.getLogger(__name__)


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

    print("=" * 60)
    print("  ZOE v1.0 -- Web Dashboard")
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
    parser.add_argument("--db-path", default="zoe_data/dashboard_memory.db")
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
