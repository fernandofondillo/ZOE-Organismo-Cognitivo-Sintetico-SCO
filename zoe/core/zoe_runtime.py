#!/usr/bin/env python3
"""
ZOE V1.7 — Runtime Mínimo (Sprint 3.5)

Este script se incluye dentro de cada archivo .zoe. Permite ejecutar ZOE
sin instalar nada (solo Python 3.10+ en el host).

Carga automáticamente:
1. Memory.db desde el directorio del .zoe
2. Cápsulas desde capsules/
3. PatternSpeaker como backend (siempre disponible)
4. Embedded model si existe embedded_model.gguf
5. Ollama si está disponible en el host
6. Dashboard web si se solicita

Uso:
    # Después de desempaquetar un .zoe:
    cd /path/to/ZOE
    python zoe_runtime.py                    # CLI chat
    python zoe_runtime.py --dashboard        # Dashboard web
    python zoe_runtime.py --port 8642        # Puerto custom
    python zoe_runtime.py --backend pattern  # Forzar PatternSpeaker
    python zoe_runtime.py --inspect          # Ver info del .zoe

Sin dependencias externas (solo Python stdlib + sqlite3 que viene con Python).
"""

import argparse
import asyncio
import json
import os
import sys
import sqlite3
import time
from pathlib import Path

# ============================================================
# Constants
# ============================================================

RUNTIME_DIR = Path(__file__).parent
MANIFEST_PATH = RUNTIME_DIR / "manifest.json"
MEMORY_DB_PATH = RUNTIME_DIR / "memory.db"
CAPSULES_DIR = RUNTIME_DIR / "capsules"
CONFIG_PATH = RUNTIME_DIR / "config.yaml"
EMBEDDED_MODEL_PATH = RUNTIME_DIR / "embedded_model.gguf"
IDENTITY_VAULT_PATH = RUNTIME_DIR / "identity_vault.json"
TRAJECTORY_CHAIN_PATH = RUNTIME_DIR / "trajectory_chain.json"

# ============================================================
# Minimal ZOE runtime (no external dependencies)
# ============================================================

class ZoeRuntime:
    """
    Runtime mínimo de ZOE que funciona sin dependencias externas.
    
    Usa PatternSpeaker para generar respuestas (siempre disponible).
    Si detecta Ollama o embedded model, los usa para mejor calidad.
    """

    def __init__(self, backend: str = "auto", port: int = 8642):
        self.backend_choice = backend
        self.port = port
        self.manifest = {}
        self.memory_entries = 0
        self.capsule_count = 0
        self.has_embedded_model = False
        self.has_ollama = False
        self.has_cloud_api = False
        self.backend_name = "pattern"
        self.identity_hash = "unknown"
        self.running = False
        self.iteration_count = 0
        self._conversation_history = []

    def initialize(self):
        """Inicializa el runtime cargando todos los componentes del .zoe."""
        self._load_manifest()
        self._load_memory()
        self._count_capsules()
        self._detect_backends()
        self._load_identity()

    def _load_manifest(self):
        """Carga manifest.json."""
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH, "r") as f:
                self.manifest = json.load(f)

    def _load_memory(self):
        """Carga memoria SQLite y cuenta entries."""
        if MEMORY_DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(MEMORY_DB_PATH))
                cursor = conn.cursor()
                for table in ["episodic", "semantic", "procedural", "causal",
                              "emotional", "corporeal", "social", "prospective",
                              "counterfactual", "evolutionary", "cultural"]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        self.memory_entries += cursor.fetchone()[0]
                    except:
                        pass
                conn.close()
            except Exception as e:
                print(f"  Warning: memory.db load error: {e}")

    def _count_capsules(self):
        """Cuenta cápsulas disponibles."""
        if CAPSULES_DIR.exists():
            for item in CAPSULES_DIR.iterdir():
                if item.is_dir() and (item / "capsule.yaml").exists():
                    self.capsule_count += 1

    def _detect_backends(self):
        """Detecta qué backends están disponibles."""
        # Embedded model
        if EMBEDDED_MODEL_PATH.exists():
            self.has_embedded_model = True

        # Ollama (check if running on localhost:11434)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            result = sock.connect_ex(("localhost", 11434))
            if result == 0:
                self.has_ollama = True
        except:
            pass
        finally:
            sock.close()

        # Cloud API keys
        if os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
            self.has_cloud_api = True

        # Decide backend
        if self.backend_choice == "pattern":
            self.backend_name = "pattern"
        elif self.backend_choice == "ollama" and self.has_ollama:
            self.backend_name = "ollama"
        elif self.backend_choice == "embedded" and self.has_embedded_model:
            self.backend_name = "embedded"
        elif self.backend_choice == "auto":
            if self.has_ollama:
                self.backend_name = "ollama"
            elif self.has_cloud_api:
                self.backend_name = "cloud"
            elif self.has_embedded_model:
                self.backend_name = "embedded"
            else:
                self.backend_name = "pattern"

    def _load_identity(self):
        """Carga identity vault si existe."""
        if IDENTITY_VAULT_PATH.exists():
            try:
                with open(IDENTITY_VAULT_PATH, "r") as f:
                    vault = json.load(f)
                    self.identity_hash = vault.get("identity_hash", "unknown")[:16]
            except:
                pass

    def get_banner(self) -> str:
        """Devuelve el banner de inicio."""
        organism_id = self.manifest.get("organism_id", "zoe_unknown")
        zoe_version = self.manifest.get("zoe_version", "1.7.0")
        description = self.manifest.get("description", "")

        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║  ZOE v{zoe_version} — Synthetic Cognitive Organism               ║
╠══════════════════════════════════════════════════════════════╣
║  Organism ID:  {organism_id:<46}║
║  Identity:     {self.identity_hash}...{" " * 38}║
║  Memory:       {self.memory_entries} entries{" " * (38 - len(str(self.memory_entries)))}║
║  Capsules:     {self.capsule_count} loaded{" " * (40 - len(str(self.capsule_count)))}║
║  Backend:      {self.backend_name:<46}║
║  Embedded:     {"Yes" if self.has_embedded_model else "No":<46}║
║  Ollama:       {"Yes" if self.has_ollama else "No":<46}║
║  Cloud API:    {"Yes" if self.has_cloud_api else "No":<46}║
╠══════════════════════════════════════════════════════════════╣
║  {description[:58]:<58}║
╚══════════════════════════════════════════════════════════════╝

Type /help for commands. Start chatting below.
────────────────────────────────────────────────────────────────
"""
        return banner

    async def process_message(self, user_input: str) -> str:
        """Procesa un mensaje del usuario y devuelve respuesta."""
        self.iteration_count += 1

        # Comandos especiales
        if user_input.startswith("/"):
            return self._handle_command(user_input)

        # Generar respuesta con PatternSpeaker
        response = self._generate_response(user_input)

        # Guardar en historial
        self._conversation_history.append({
            "timestamp": time.time(),
            "user": user_input,
            "zoe": response,
        })

        return response

    def _handle_command(self, cmd: str) -> str:
        """Maneja comandos especiales."""
        cmd = cmd.lower().strip()

        if cmd == "/help":
            return (
                "ZOE Runtime Commands:\n"
                "  /help     — Esta ayuda\n"
                "  /stats    — Estadísticas del organismo\n"
                "  /memory   — Ver memoria reciente\n"
                "  /identity — Ver identidad\n"
                "  /quit     — Salir"
            )

        elif cmd == "/stats":
            return (
                f"ZOE Stats:\n"
                f"  Organism ID: {self.manifest.get('organism_id', 'unknown')}\n"
                f"  Identity Hash: {self.identity_hash}...\n"
                f"  Iterations: {self.iteration_count}\n"
                f"  Memory entries: {self.memory_entries}\n"
                f"  Capsules: {self.capsule_count}\n"
                f"  Backend: {self.backend_name}\n"
                f"  Conversation turns: {len(self._conversation_history)}"
            )

        elif cmd == "/memory":
            if not self._conversation_history:
                return "No hay memoria de conversación todavía."
            recent = self._conversation_history[-5:]
            lines = ["Recent conversation:"]
            for entry in recent:
                lines.append(f"  User: {entry['user'][:50]}...")
                lines.append(f"  ZOE:  {entry['zoe'][:50]}...")
            return "\n".join(lines)

        elif cmd == "/identity":
            if IDENTITY_VAULT_PATH.exists():
                with open(IDENTITY_VAULT_PATH, "r") as f:
                    vault = json.load(f)
                return (
                    f"ZOE Identity Vault:\n"
                    f"  Organism ID: {vault.get('organism_id', 'unknown')}\n"
                    f"  Birth Date: {vault.get('birth_date', 'unknown')}\n"
                    f"  Identity Hash: {vault.get('identity_hash', 'unknown')[:32]}...\n"
                    f"  Values: {', '.join(vault.get('values', [])[:3])}..."
                )
            return "Identity vault not found."

        elif cmd == "/quit":
            return "__QUIT__"

        else:
            return f"Unknown command: {cmd}. Type /help for available commands."

    def _generate_response(self, user_input: str) -> str:
        """Genera respuesta usando PatternSpeaker."""
        # Importar PatternSpeaker (debe estar en el path del .zoe)
        try:
            # Intentar importar desde zoe package
            from zoe.peripherals.pattern_speaker import (
                PatternPeripheral, classify_intent, RESPONSE_TEMPLATES
            )
            import random

            intent = classify_intent(user_input)

            # Refinar emotion intent
            if intent == "emotion":
                text_lower = user_input.lower()
                if any(w in text_lower for w in ["triste", "sad", "lloro", "deprimido"]):
                    intent = "emotion_sad"
                elif any(w in text_lower for w in ["feliz", "happy", "alegre", "contento"]):
                    intent = "emotion_happy"
                elif any(w in text_lower for w in ["preocupado", "worried", "ansioso", "miedo"]):
                    intent = "emotion_worried"
                else:
                    intent = "emotion_sad"

            templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["statement"])
            response = random.choice(templates)

            # Truncar si muy largo
            if len(response) > 500:
                response = response[:497] + "..."

            return response

        except ImportError:
            # Fallback: respuestas básicas hardcoded
            input_lower = user_input.lower().strip()

            greetings = {"hola": "Hola. Estoy aquí.", "hello": "Hello. I'm here.",
                        "hi": "Hi. I'm here.", "bonjour": "Bonjour. Je suis là.",
                        "hallo": "Hallo. Ich bin hier."}

            for key, resp in greetings.items():
                if key in input_lower:
                    return resp

            if "quien" in input_lower or "who" in input_lower:
                return "Soy ZOE, un organismo cognitivo sintético."

            if "gracias" in input_lower or "thank" in input_lower:
                return "De nada."

            return "Te escucho. Cuéntame más."

    def get_stats(self) -> dict:
        """Devuelve stats del runtime."""
        return {
            "organism_id": self.manifest.get("organism_id", "unknown"),
            "identity_hash": self.identity_hash,
            "iteration_count": self.iteration_count,
            "memory_entries": self.memory_entries,
            "capsule_count": self.capsule_count,
            "backend": self.backend_name,
            "has_embedded_model": self.has_embedded_model,
            "has_ollama": self.has_ollama,
            "has_cloud_api": self.has_cloud_api,
            "conversation_turns": len(self._conversation_history),
        }

    def inspect(self) -> str:
        """Devuelve info detallada del .zoe."""
        lines = ["ZOE .zoe Inspection", "=" * 50]

        if self.manifest:
            lines.append(f"Organism ID: {self.manifest.get('organism_id', 'N/A')}")
            lines.append(f"ZOE Version: {self.manifest.get('zoe_version', 'N/A')}")
            lines.append(f"Format Version: {self.manifest.get('format_version', 'N/A')}")
            lines.append(f"Description: {self.manifest.get('description', 'N/A')}")
            lines.append(f"Size: {self.manifest.get('size_bytes', 0) / 1024 / 1024:.1f} MB")
            lines.append("")

        lines.append(f"Memory entries: {self.memory_entries}")
        lines.append(f"Capsules: {self.capsule_count}")
        lines.append(f"Identity hash: {self.identity_hash}...")
        lines.append(f"Embedded model: {'Yes' if self.has_embedded_model else 'No'}")
        lines.append(f"Ollama available: {'Yes' if self.has_ollama else 'No'}")
        lines.append(f"Cloud API available: {'Yes' if self.has_cloud_api else 'No'}")
        lines.append(f"Selected backend: {self.backend_name}")

        # Listar cápsulas
        if CAPSULES_DIR.exists():
            lines.append("")
            lines.append("Capsules:")
            for item in sorted(CAPSULES_DIR.iterdir()):
                if item.is_dir() and (item / "capsule.yaml").exists():
                    lines.append(f"  - {item.name}")

        # Listar archivos
        lines.append("")
        lines.append("Files:")
        for f in RUNTIME_DIR.iterdir():
            if f.is_file():
                size = f.stat().st_size
                if size > 1024 * 1024:
                    lines.append(f"  {f.name} ({size / 1024 / 1024:.1f} MB)")
                elif size > 1024:
                    lines.append(f"  {f.name} ({size / 1024:.1f} KB)")
                else:
                    lines.append(f"  {f.name} ({size} B)")

        return "\n".join(lines)


# ============================================================
# CLI entry point
# ============================================================

async def run_cli(runtime: ZoeRuntime):
    """Ejecuta ZOE en modo CLI."""
    print(runtime.get_banner())

    while True:
        try:
            user_input = input("zoe> ").strip()
            if not user_input:
                continue

            response = await runtime.process_message(user_input)

            if response == "__QUIT__":
                print("\nSaving conversation...")
                print("Goodbye. ZOE will be here when you return.\n")
                break

            print(f"ZOE: {response}\n")

        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye.\n")
            break


async def run_dashboard(runtime: ZoeRuntime):
    """Ejecuta ZOE en modo Dashboard web (mínimo)."""
    print(runtime.get_banner())
    print(f"Dashboard starting on http://localhost:{runtime.port}")
    print("Press Ctrl+C to stop.\n")

    # Dashboard mínimo usando solo stdlib (http.server)
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    class ZoeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self._send_html(runtime._dashboard_html())
            elif self.path == "/stats":
                self._send_json(runtime.get_stats())
            elif self.path == "/manifest":
                self._send_json(runtime.manifest)
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path == "/chat":
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode()
                try:
                    data = json.loads(body)
                    message = data.get("message", "")
                    response = asyncio.run(runtime.process_message(message))
                    self._send_json({"response": response})
                except Exception as e:
                    self._send_json({"error": str(e)}, status=500)
            else:
                self.send_error(404)

        def _send_html(self, html):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        def _send_json(self, data, status=200):
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        def log_message(self, format, *args):
            pass  # silence logs

    server = HTTPServer(("0.0.0.0", runtime.port), ZoeHandler)
    print(f"✅ Dashboard running at http://localhost:{runtime.port}")
    print(f"   Backend: {runtime.backend_name}")
    print(f"   Open in browser or use API: POST /chat with {{\"message\": \"...\"}}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        server.shutdown()


def main():
    """Entry point del runtime."""
    parser = argparse.ArgumentParser(description="ZOE Runtime — Execute .zoe files")
    parser.add_argument("--dashboard", action="store_true",
                       help="Start Dashboard web instead of CLI")
    parser.add_argument("--port", type=int, default=8642,
                       help="Dashboard port (default: 8642)")
    parser.add_argument("--backend", default="auto",
                       choices=["auto", "pattern", "ollama", "embedded"],
                       help="Force backend (default: auto-detect)")
    parser.add_argument("--inspect", action="store_true",
                       help="Inspect .zoe contents and exit")

    args = parser.parse_args()

    runtime = ZoeRuntime(backend=args.backend, port=args.port)
    runtime.initialize()

    if args.inspect:
        print(runtime.inspect())
        return

    if args.dashboard:
        asyncio.run(run_dashboard(runtime))
    else:
        asyncio.run(run_cli(runtime))


if __name__ == "__main__":
    main()
