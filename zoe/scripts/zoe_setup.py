#!/usr/bin/env python3
"""
ZOE V1.8 — Setup interactivo (Sprint 5.5)

Guía al usuario paso a paso: detecta qué tiene instalado, qué falta,
y le dice exactamente cómo empezar a usar ZOE.

Sin tecnicismos. Sin confusión. Un comando, y ZOE funciona.

Uso:
    zoe-setup              # detección automática + guía
    zoe-setup --check      # solo verificar, no instalar nada
    zoe-setup --install    # instalar dependencias que falten
"""

import argparse
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Colores ANSI
class C:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def ok(msg): print(f"  {C.GREEN}✅{C.END} {msg}")
def warn(msg): print(f"  {C.YELLOW}⚠️ {C.END} {msg}")
def err(msg): print(f"  {C.RED}❌{C.END} {msg}")
def info(msg): print(f"  {C.BLUE}ℹ️{C.END} {msg}")
def title(msg):
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.END}")
    print(f"{C.BOLD}{C.BLUE} {msg}{C.END}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.END}\n")


def check_python():
    """Verifica Python 3.10+."""
    version = sys.version_info
    if version >= (3, 10):
        ok(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        err(f"Python {version.major}.{version.minor} — necesitas 3.10+")
        info("Descarga desde: https://python.org")
        return False


def check_pip():
    """Verifica pip."""
    if shutil.which("pip") or shutil.which("pip3"):
        ok("pip instalado")
        return True
    else:
        err("pip no encontrado")
        return False


def check_git():
    """Verifica git."""
    if shutil.which("git"):
        ok("git instalado")
        return True
    else:
        warn("git no encontrado (necesario para clonar ZOE)")
        return False


def check_ollama():
    """Verifica si Ollama está instalado y corriendo."""
    installed = shutil.which("ollama") is not None
    
    # Verificar si está corriendo
    running = False
    if installed:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            if sock.connect_ex(("localhost", 11434)) == 0:
                running = True
        except OSError as e:
            logger.debug(f"Socket check for Ollama failed: {e}")
        finally:
            sock.close()
    
    if running:
        ok("Ollama corriendo en localhost:11434")
        # Verificar modelos instalados
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    models = [l.split()[0] for l in lines[1:] if l.strip()]
                    ok(f"Modelos instalados: {', '.join(models[:5])}")
                    return "running_with_models", models
                else:
                    warn("Ollama no tiene modelos. Recomendado: ollama pull qwen2.5:3b")
                    return "running_no_models", []
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug(f"Ollama list check failed: {e}")
        return "running_no_models", []
    elif installed:
        warn("Ollama instalado pero no corriendo. Ejecuta: ollama serve")
        return "installed_not_running", []
    else:
        info("Ollama no instalado (opcional — ZOE funciona sin él con PatternSpeaker)")
        return "not_installed", []


def check_api_keys():
    """Verifica API keys de cloud."""
    keys = {}
    for name, env_var in [
        ("OpenAI (GPT-4o)", "OPENAI_API_KEY"),
        ("Anthropic (Claude)", "ANTHROPIC_API_KEY"),
        ("DeepSeek", "DEEPSEEK_API_KEY"),
        ("Groq", "GROQ_API_KEY"),
    ]:
        if os.environ.get(env_var):
            ok(f"API key de {name} configurada")
            keys[name] = True
        else:
            keys[name] = False
    
    if not any(keys.values()):
        info("Sin API keys de cloud (opcional — ZOE funciona con PatternSpeaker u Ollama)")
    
    return keys


def check_zoe_installed():
    """Verifica si ZOE está instalado."""
    try:
        import zoe
        ok(f"ZOE v{zoe.__version__} instalado")
        return True
    except ImportError:
        err("ZOE no instalado")
        return False


def check_zoe_data():
    """Verifica si hay datos de ZOE (memoria, identidad)."""
    data_dir = Path("zoe_data")
    if data_dir.exists():
        db = data_dir / "dashboard_memory.db"
        if db.exists():
            size = db.stat().st_size
            if size > 1024:
                ok(f"Memoria de ZOE: {size/1024:.0f} KB")
                return True
        return True
    return False


def get_platform_info():
    """Info de la plataforma."""
    system = platform.system()
    machine = platform.machine()
    cpu_count = os.cpu_count() or 4
    
    ram_gb = 0
    try:
        if system == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, timeout=5
            )
            ram_gb = int(result.stdout.strip()) / (1024**3)
        elif system == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_gb = int(line.split()[1]) / (1024**2)
                        break
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        logger.debug(f"RAM detection failed: {e}")
    
    is_apple_silicon = False
    if system == "Darwin" and machine == "arm64":
        is_apple_silicon = True
    
    return {
        "system": system,
        "machine": machine,
        "cpu_count": cpu_count,
        "ram_gb": round(ram_gb, 1) if ram_gb > 0 else "unknown",
        "is_apple_silicon": is_apple_silicon,
    }


def print_recommendation(platform_info, ollama_status, api_keys, zoe_installed):
    """Imprime recomendación personalizada."""
    title("RECOMENDACIÓN PERSONALIZADA")
    
    system = platform_info["system"]
    ram = platform_info["ram_gb"]
    
    # Determinar el mejor modo
    if ollama_status[0] in ("running_with_models", "running_no_models"):
        mode = "ollama"
        models = ollama_status[1]
        if models:
            model = models[0]
        else:
            model = "qwen2.5:3b"
        
        print(f"\n{C.BOLD}Tu configuración óptima:{C.END}")
        print(f"  Backend: Ollama (local, gratis, offline)")
        print(f"  Modelo: {model}")
        print(f"\n{C.BOLD}Para empezar:{C.END}")
        print(f"  zoe-chat --backend ollama --model {model}")
        print(f"  zoe-dashboard --backend ollama --model {model}")
        print(f"  → abre http://localhost:8642")
        
        if not models and ollama_status[0] == "running_no_models":
            print(f"\n{C.YELLOW}Primero descarga un modelo:{C.END}")
            print(f"  ollama pull qwen2.5:3b  (2GB, rápido, recomendado)")
    
    elif any(api_keys.values()):
        # Hay API key de cloud
        for name, has_key in api_keys.items():
            if has_key:
                if "OpenAI" in name:
                    print(f"\n{C.BOLD}Tu configuración óptima:{C.END}")
                    print(f"  Backend: OpenAI (cloud, calidad máxima)")
                    print(f"  Modelo: gpt-4o")
                    print(f"\n{C.BOLD}Para empezar:{C.END}")
                    print(f"  zoe-chat --backend openai_compatible --model gpt-4o")
                    print(f"  zoe-dashboard --backend openai_compatible --model gpt-4o")
                elif "Anthropic" in name:
                    print(f"\n{C.BOLD}Tu configuración óptima:{C.END}")
                    print(f"  Backend: Anthropic Claude (cloud, calidad + ética)")
                    print(f"  Modelo: claude-sonnet-4-20250514")
                    print(f"\n{C.BOLD}Para empezar:{C.END}")
                    print(f"  zoe-chat --backend anthropic --model claude-sonnet-4-20250514")
                break
    
    else:
        # Sin Ollama ni API keys — PatternSpeaker
        print(f"\n{C.BOLD}Tu configuración óptima:{C.END}")
        print(f"  Backend: PatternSpeaker (sin LLM, gratis, offline)")
        print(f"  ZOE responde desde patrones + memoria + cápsulas")
        print(f"\n{C.BOLD}Para empezar:{C.END}")
        print(f"  zoe-chat --backend pattern")
        print(f"  zoe-dashboard --backend pattern")
        print(f"  → abre http://localhost:8642")
        
        print(f"\n{C.YELLOW}Para mayor calidad, puedes (opcional):{C.END}")
        print(f"  1. Instalar Ollama: https://ollama.com")
        print(f"     ollama pull qwen2.5:3b")
        print(f"  2. O configurar API key:")
        print(f"     export OPENAI_API_KEY='sk-...'")
        print(f"  3. ZOE detectará automáticamente cuál tienes y la usará")
    
    # Recomendación de modelo por RAM
    if isinstance(ram, (int, float)) and ram > 0 and ollama_status[0] == "not_installed":
        print(f"\n{C.BOLD}Si instalas Ollama, modelo recomendado para tu RAM ({ram:.0f}GB):{C.END}")
        if ram >= 16:
            print(f"  ollama pull qwen2.5:7b  (4.5GB, calidad media, recomendado)")
        elif ram >= 8:
            print(f"  ollama pull qwen2.5:3b  (2GB, rápido, recomendado)")
        else:
            print(f"  ollama pull qwen2.5:1.5b  (1.2GB, mínimo)")
            warn("Tu RAM es limitada. Considera usar PatternSpeaker o cloud API.")


def print_first_steps():
    """Imprime los primeros pasos con ZOE."""
    title("TUS PRIMEROS PASOS CON ZOE")
    
    print(f"""{C.BOLD}1. PRIMERA CONVERSACIÓN{C.END}
   Escribe un mensaje y pulsa Enter:
   
   zoe> Hola, ¿quién eres?
   zoe> ¿Qué puedes hacer?
   zoe> Mi madre tiene 78 años y vive sola

{C.BOLD}2. COMANDOS ESPECIALES{C.END}
   /stats   — ver estado de ZOE (energía, memoria, iteraciones)
   /memory  — ver qué recuerda ZOE
   /identity — ver identidad criptográfica de ZOE
   /capsules — ver cápsulas de conocimiento disponibles
   /capsule base_ethics — cargar una cápsula
   /sleep   — ZOE duerme (consolida memoria)
   /wake    — ZOE despierta
   /quit    — salir (guarda memoria automáticamente)

{C.BOLD}3. CÁPSULAS DE CONOCIMIENTO{C.END}
   ZOE viene con 15 cápsulas preinstaladas. Para verlas:
   
   zoe> /capsules
   
   Para cargar una (ej: cuidado de mayores):
   
   zoe> /capsule elder_care_knowledge
   
   Ahora ZOE "sabe" de cuidado geriátrico.

{C.BOLD}4. DASHBOARD WEB{C.END}
   Si prefieres interfaz visual:
   
   zoe-dashboard --backend pattern
   → abre http://localhost:8642 en tu navegador
   
   El Dashboard tiene:
   - Chat en tiempo real
   - Estado del organismo (energía, fatiga, metabolismo)
   - Memoria viva (lo que ZOE recuerda)
   - Pensamientos autónomos (lo que ZOE piensa sola)
   - Botones: 📦 Cápsulas, 🔒 Cuarentena, 🏪 Marketplace

{C.BOLD}5. CAMBIAR DE LLM{C.END}
   ZOE puede cambiar de "garganta" sin perder memoria:
   
   zoe> /llm ollama qwen2.5:7b      (local, gratis)
   zoe> /llm openai_compatible gpt-4o  (cloud, calidad)
   zoe> /llm pattern                 (sin LLM, patrones)
   
   La memoria, identidad y trayectoria se conservan siempre.

{C.BOLD}6. ¿QUÉ HACE ZOE CUANDO ARRANCA?{C.END}
   1. Carga su identidad criptográfica (Identity Vault)
   2. Carga su memoria desde SQLite (todo lo que recuerda)
   3. Carga la cápsula basal (conocimiento fundamental de sí misma)
   4. Detecta qué LLMs tienes disponibles (Ollama, cloud, nada)
   5. Elige el mejor backend automáticamente
   6. Empieza a pensar (bucle cognitivo continuo)
   7. Si nadie le habla, piensa autónomamente y consolida memoria

{C.BOLD}7. VENTAJAS DE ZOE{C.END}
   - Recuerda todo entre sesiones (memoria persistente de 11 tipos)
   - Se cansa y descansa (metabolismo — no se cuelga)
   - Sabe qué sabe y qué no sabe (validación epistémica)
   - Piensa con 12 sub-agentes (Society of Mind)
   - Aprende de cápsulas de conocimiento (sin reentrenar)
   - Funciona offline (privacidad total)
   - Cambia de LLM sin perder nada
   - Viaja en un pendrive o archivo .zoe (portátil)
   - Conversa por voz (voice-first mode)
   - Ve imágenes (multi-modal)
""")


def print_installation_guide():
    """Imprime guía de instalación por escenario."""
    title("GUÍA DE INSTALACIÓN POR ESCENARIO")
    
    print(f"""{C.BOLD}ESCENARIO 1: Mac o Linux (local){C.END}
   Qué se instala: Python 3.10+, pip, ZOE
   Qué NO necesitas: Ollama (opcional), API key (opcional)
   
   git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
   cd ZOE-Organismo-Cognitivo-Sintetico-SCO
   pip install -e .
   zoe-chat --backend pattern          # ¡ya funciona!

{C.BOLD}ESCENARIO 2: Pendrive USB / SSD (macOS){C.END}
   Qué se instala en el Mac: Python 3.10+, Git
   Qué se instala en el SSD: ZOE + venv + memoria + (modelos opcionales)
   
   # Conecta SSD con cable corto de la caja
   curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh | bash
   # Doble clic en ZOE-Chat.command en el SSD

{C.BOLD}ESCENARIO 3: Pendrive USB / SSD (Windows){C.END}
   Qué se instala en el PC: Python 3.10+, Git
   Qué se instala en el SSD: ZOE + venv + memoria
   
   # Descargar install_windows.ps1 y ejecutar en PowerShell
   .\\install_windows.ps1
   # Doble clic en ZOE-Chat.bat en el SSD

{C.BOLD}ESCENARIO 4: VPS Linux (servidor){C.END}
   Qué se instala: Python 3.10+, Git, Ollama, ZOE, systemd service
   
   sudo bash zoe/scripts/deploy.sh
   sudo systemctl start zoe
   # Acceder desde navegador: http://IP-DEL-VPS:8642

{C.BOLD}ESCENARIO 5: .zoe portátil (un archivo){C.END}
   Qué se instala: Solo Python 3.10+ (nada más)
   
   # Desempaquetar .zoe
   python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().unpackage('mi_zoe.zoe', './ZOE')"
   cd ZOE
   python zoe_runtime.py              # ¡ya funciona sin instalar nada más!

{C.BOLD}ESCENARIO 6: Telegram (móvil){C.END}
   Qué se instala: python-telegram-bot en el servidor donde corre ZOE
   
   pip install python-telegram-bot
   python -m zoe.peripherals.telegram_bridge --token TU_BOT_TOKEN --zoe-url http://localhost:8642
   # Hablar con ZOE desde Telegram en el móvil

{C.BOLD}ESCENARIO 7: Voice-first (voz natural){C.END}
   Qué se instala: whisper, sounddevice, numpy, piper (opcional)
   
   pip install openai-whisper sounddevice numpy
   python -m zoe.peripherals.voice_first --zoe-url http://localhost:8642
   # Decir "Hey ZOE" y conversar por voz
""")


def check_iq2_models(models_dir=None):
    """Sprint 5.7 — Verifica qué modelos IQ2_M hay instalados."""
    if models_dir is None:
        models_dir = os.environ.get("OLLAMA_MODELS", "models")
    try:
        from zoe.core.model_downloader import OPTIMIZED_MODELS, SETUP_PRESETS
        from pathlib import Path
        installed = []
        for key, m in OPTIMIZED_MODELS.items():
            local = Path(models_dir) / m.hf_filename
            if local.exists():
                installed.append(key)
        return installed, models_dir
    except Exception:
        return [], models_dir


def recommend_iq2_setup(ram_gb, ssd_free_gb=None):
    """Sprint 5.7 — Recomienda setup IQ2_M según RAM y SSD."""
    if not isinstance(ram_gb, (int, float)) or ram_gb <= 0:
        ram_gb = 8.0
    # Setup según RAM y (si se sabe) SSD libre
    if ssd_free_gb and ssd_free_gb >= 60:
        return "maximum", "SSD con ≥60GB libre → los 4 modelos cubren todo el espectro"
    if ram_gb >= 8 and (ssd_free_gb is None or ssd_free_gb >= 30):
        return "complete", "8GB+ RAM y SSD con ≥30GB → 3 modelos (Gemma + MoE + QwQ)"
    if ram_gb >= 8 and (ssd_free_gb is None or ssd_free_gb >= 18):
        return "balanced", "8GB+ RAM → 2 modelos (Gemma + QwQ-32B), equilibrado"
    return "minimal", "RAM limitada → solo Gemma 9B IQ2_M (3.5GB)"


def main():
    parser = argparse.ArgumentParser(description="ZOE Setup — guía interactiva")
    parser.add_argument("--check", action="store_true",
                       help="Solo verificar, no instalar")
    parser.add_argument("--install", action="store_true",
                       help="Instalar dependencias que falten")
    parser.add_argument("--install-iq2-models", metavar="SETUP",
                       choices=["minimal", "balanced", "complete", "maximum"],
                       help="Descarga e instala un setup de modelos IQ2_M")
    parser.add_argument("--models-dir",
                       default=None,
                       help="Directorio donde guardar los .gguf (default: $OLLAMA_MODELS o ./models)")
    args = parser.parse_args()

    # Sprint 5.7 — atajo: --install-iq2-models
    if args.install_iq2_models:
        models_dir = args.models_dir or os.environ.get("OLLAMA_MODELS", "models")
        title(f"INSTALAR MODELOS IQ2_M — setup '{args.install_iq2_models}'")
        try:
            from zoe.core.model_downloader import _main_cli
            import sys as _sys
            _sys.argv = [
                "model_downloader",
                "--download-setup", args.install_iq2_models,
                "--models-dir", models_dir,
            ]
            _main_cli()
        except Exception as e:
            err(f"Error instalando modelos: {e}")
            info("Ejecuta manualmente: python -m zoe.core.model_downloader --download-setup "
                 f"{args.install_iq2_models} --models-dir {models_dir}")
        return

    title("ZOE SETUP — Detección y guía")
    
    # 1. Detectar plataforma
    print(f"{C.BOLD}Detectando tu sistema...{C.END}\n")
    plat = get_platform_info()
    ok(f"Sistema: {plat['system']} {plat['machine']}")
    ok(f"CPU cores: {plat['cpu_count']}")
    if isinstance(plat['ram_gb'], (int, float)):
        ok(f"RAM: {plat['ram_gb']:.1f} GB")
    if plat['is_apple_silicon']:
        ok("Apple Silicon detectado (Metal + Neural Engine)")
    
    # 2. Verificar componentes
    print(f"\n{C.BOLD}Verificando componentes...{C.END}\n")
    python_ok = check_python()
    pip_ok = check_pip()
    git_ok = check_git()
    ollama_status = check_ollama()
    api_keys = check_api_keys()
    zoe_ok = check_zoe_installed()
    has_data = check_zoe_data()
    
    # 2b. Sprint 5.7 — Verificar modelos IQ2_M
    print(f"\n{C.BOLD}Verificando modelos IQ2_M...{C.END}\n")
    installed_iq2, models_dir = check_iq2_models()
    if installed_iq2:
        ok(f"Modelos IQ2_M instalados en {models_dir}: {', '.join(installed_iq2)}")
        # Recomendar ZOE con --model auto
        print(f"\n  {C.GREEN}→ Para activar routing automático por nivel cognitivo:{C.END}")
        print(f"    zoe-chat --backend ollama --model auto")
    else:
        info(f"No hay modelos IQ2_M en {models_dir}")
        setup, reason = recommend_iq2_setup(plat['ram_gb'])
        print(f"  Setup recomendado: {C.BOLD}{setup}{C.END} ({reason})")
        print(f"\n  {C.BOLD}Para instalar:{C.END}")
        print(f"    zoe-setup --install-iq2-models {setup}")
        print(f"    (o: python -m zoe.core.model_downloader --download-setup {setup})")
    
    # 3. Instalar ZOE si no está
    if not zoe_ok and python_ok and pip_ok:
        print(f"\n{C.BOLD}Instalando ZOE...{C.END}")
        if args.install or not args.check:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                ok("ZOE instalado correctamente")
                zoe_ok = True
            else:
                err("Error instalando ZOE")
                print(result.stderr[:500])
    
    # 4. Instalar Ollama si el usuario quiere
    if ollama_status[0] == "not_installed" and args.install:
        print(f"\n{C.BOLD}¿Instalar Ollama? (recomendado para IA local gratis){C.END}")
        response = input("Instalar Ollama? (s/N): ")
        if response.lower() == 's':
            if plat['system'] == "Linux":
                subprocess.run(
                    "curl -fsSL https://ollama.com/install.sh | sh",
                    shell=True
                )
                ok("Ollama instalado")
            elif plat['system'] == "Darwin":
                info("Descarga Ollama desde: https://ollama.com/download/mac")
            else:
                info("Descarga Ollama desde: https://ollama.com/download")
    
    # 5. Recomendación
    print_recommendation(plat, ollama_status, api_keys, zoe_ok)
    
    # 6. Primeros pasos
    print_first_steps()
    
    # 7. Guía de instalación por escenario
    print_installation_guide()
    
    # 8. Mensaje final
    title("¡LISTO!")
    print(f"""
{C.GREEN}ZOE está preparada.{C.END}

{C.BOLD}Comando más simple para empezar (sin IA, gratis, offline):{C.END}
  zoe-chat --backend pattern

{C.BOLD}Con IA local + routing automático (recomendado):{C.END}
  zoe-chat --backend ollama --model auto
  (ZOE elegirá Gemma/Agents-A1/QwQ/Qwen72B según el tipo de pregunta)

{C.BOLD}Para instalar modelos IQ2_M optimizados:{C.END}
  zoe-setup --install-iq2-models balanced
  (setups: minimal | balanced | complete | maximum)

{C.BOLD}Dashboard web:{C.END}
  zoe-dashboard --backend pattern
  → http://localhost:8642

{C.BOLD}Documentación completa:{C.END}
  docs/01_ZOE_OVERVIEW.md — qué es ZOE
  docs/09_USAGE_GUIDE.md — cómo usar ZOE
  docs/16_ZOE_FORMAT.md — formato .zoe portátil

{C.BOLD}¿Necesitas ayuda?{C.END}
  GitHub Issues: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues
""")


if __name__ == "__main__":
    main()
