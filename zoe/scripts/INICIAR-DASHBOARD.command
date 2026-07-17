#!/bin/bash
# ============================================================================
# ZOE Dashboard Launcher v2.1.2 -- macOS
# ============================================================================
# Doble click para abrir el Dashboard de ZOE en el navegador.
#
# Este script debe vivir en:
#   - $ZOE_HOME/INICIAR-DASHBOARD.command   (instalacion en SSD, junto a venv/)
#   - zoe/scripts/INICIAR-DASHBOARD.command (repo, para referencia)
#
# En el primer caso, ZOE_HOME es el directorio padre del script.
# En el segundo caso (repo), ZOE_HOME se calcula como 2 niveles arriba y
# se busca venv ahi; si no existe, se usa el venv del repo si esta.
# ============================================================================
set -e

# Colores
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ---------------------------------------------------------------------------
# 1. Calcular ZOE_HOME
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Caso A: script instalado en $ZOE_HOME/INICIAR-DASHBOARD.command
#         ZOE_HOME = SCRIPT_DIR (venv esta en $ZOE_HOME/venv)
# Caso B: script en repo (zoe/scripts/INICIAR-DASHBOARD.command)
#         ZOE_HOME = SCRIPT_DIR/../.. (venv en $ZOE_HOME/venv si fue bootstrap)
if [ -d "$SCRIPT_DIR/venv" ] && [ -d "$SCRIPT_DIR/zoe" ]; then
    ZOE_HOME="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/../venv" ] && [ -d "$SCRIPT_DIR/../zoe" ]; then
    ZOE_HOME="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$SCRIPT_DIR/../../venv" ] && [ -d "$SCRIPT_DIR/../../zoe" ]; then
    ZOE_HOME="$(cd "$SCRIPT_DIR/../.." && pwd)"
else
    # Fallback: usar el directorio del script
    ZOE_HOME="$SCRIPT_DIR"
fi

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  ZOE Dashboard v2.1.2                                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}ZOE_HOME:${NC} $ZOE_HOME"

# ---------------------------------------------------------------------------
# 2. Cargar variables de entorno de forma segura (sin xargs que rompe API keys)
# ---------------------------------------------------------------------------
ENV_FILE="$ZOE_HOME/data/.env"
if [ -f "$ENV_FILE" ]; then
    # Sprint 5.12 -- source en vez de xargs para soportar API keys con
    # caracteres especiales (=, /, +, etc.) sin corrupcion.
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    echo -e "  ${GREEN}OK${NC} Variables cargadas: $ENV_FILE"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} No se encontro $ENV_FILE (usando defaults)"
fi

# ---------------------------------------------------------------------------
# 3. Activar entorno virtual Python
# ---------------------------------------------------------------------------
if [ -f "$ZOE_HOME/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ZOE_HOME/venv/bin/activate"
    echo -e "  ${GREEN}OK${NC} Entorno virtual activado"
elif [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "  ${YELLOW}ADVERTENCIA${NC} Usando VIRTUAL_ENV existente: $VIRTUAL_ENV"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} No se encontro venv en $ZOE_HOME/venv -- usando python del sistema"
fi

# ---------------------------------------------------------------------------
# 4. Configurar OLLAMA_MODELS al SSD si la estructura existe
# ---------------------------------------------------------------------------
if [ -d "$ZOE_HOME/models/ollama" ]; then
    export OLLAMA_MODELS="$ZOE_HOME/models/ollama"
    echo -e "  ${GREEN}OK${NC} OLLAMA_MODELS -> $OLLAMA_MODELS"
fi

# ---------------------------------------------------------------------------
# 5. Detectar backend disponible
# ---------------------------------------------------------------------------
# Sprint 5.22+5.23 -- Prioridad de backends:
#   1. ANTHROPIC_API_KEY en .env -> Anthropic o MiniMax-M3 (via ANTHROPIC_BASE_URL)
#   2. Ollama con modelos -> Ollama (local, ACD Router 5 niveles)
#   3. OPENAI_API_KEY en .env -> OpenAI GPT-4o
#   4. PatternSpeaker (offline, sin IA)
#
# Sprint 5.22: Si ANTHROPIC_BASE_URL esta en .env, usarlo como --base-url
# Si ANTHROPIC_MODEL esta en .env, usarlo como --model
# Esto permite usar MiniMax-M3 (https://api.minimax.io/anthropic) u otros
# proveedores compatibles con Anthropic sin tocar codigo.
DASH_BACKEND="pattern"
DASH_MODEL=""
DASH_BASE_URL=""

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    DASH_BACKEND="anthropic"
    DASH_MODEL="${ANTHROPIC_MODEL:-claude-sonnet-4-20250514}"
    DASH_BASE_URL="${ANTHROPIC_BASE_URL:-}"
    if [ -n "$DASH_BASE_URL" ]; then
        echo -e "  ${GREEN}OK${NC} Anthropic-compat -- ${DASH_MODEL} @ ${DASH_BASE_URL}"
    else
        echo -e "  ${GREEN}OK${NC} Anthropic -- ${DASH_MODEL}"
    fi
elif command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    DASH_BACKEND="ollama"
    DASH_MODEL="auto"
    echo -e "  ${GREEN}OK${NC} Ollama detectado -- ACD Router activo (5 niveles cognitivos)"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    DASH_BACKEND="openai_compatible"
    DASH_MODEL="gpt-4o"
    echo -e "  ${GREEN}OK${NC} OpenAI configurado -- GPT-4o"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} Sin modelos IA -- PatternSpeaker (offline, sin IA)"
    echo -e "             Para activar IA: instala Ollama (https://ollama.com)"
    echo -e "             O anade ANTHROPIC_API_KEY/OPENAI_API_KEY a $ENV_FILE"
fi

# ---------------------------------------------------------------------------
# 6. Iniciar Ollama en background si esta instalado pero no corriendo
# ---------------------------------------------------------------------------
if [ "$DASH_BACKEND" = "ollama" ]; then
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${CYAN}INFO${NC} Iniciando Ollama en background..."
        ollama serve &>/dev/null &
        sleep 3
        if curl -s http://localhost:11434/api/tags &>/dev/null; then
            echo -e "  ${GREEN}OK${NC} Ollama corriendo"
        else
            echo -e "  ${YELLOW}ADVERTENCIA${NC} Ollama no responde -- dashboard usara PatternSpeaker"
            DASH_BACKEND="pattern"
            DASH_MODEL=""
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 7. Iniciar Dashboard (con detection de puerto libre)
# ---------------------------------------------------------------------------
PORT="${ZOE_DASHBOARD_PORT:-8642}"

# Verificar puerto libre; si ocupado, buscar siguiente
check_port() {
    python -c "import socket; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', $1))" 2>/dev/null
}

for try_port in $PORT $((PORT+1)) $((PORT+2)) $((PORT+3)); do
    if check_port $try_port; then
        PORT=$try_port
        break
    fi
done

echo ""
echo -e "  ${BOLD}URL del Dashboard:${NC}"
echo -e "  ${CYAN}http://localhost:${PORT}/${NC}"
echo ""
echo -e "  ${BOLD}El token de autenticacion se mostrara abajo cuando ZOE arranque.${NC}"
echo -e "  ${BOLD}Copia la URL completa (con ?token=...) en tu navegador.${NC}"
echo -e "  ${BOLD}Pulsa Ctrl+C para detener ZOE.${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Asegurar que cwd es ZOE_HOME/zoe (donde esta el paquete Python)
if [ -d "$ZOE_HOME/zoe" ]; then
    cd "$ZOE_HOME/zoe"
elif [ -d "$ZOE_HOME" ]; then
    cd "$ZOE_HOME"
fi

# Ejecutar dashboard
exec python -m zoe.web_dashboard \
    --backend "$DASH_BACKEND" \
    ${DASH_MODEL:+--model "$DASH_MODEL"} \
    ${DASH_BASE_URL:+--base-url "$DASH_BASE_URL"} \
    --port "$PORT" \
    --host "127.0.0.1" \
    --db-path "${ZOE_DATA:-$ZOE_HOME/data}/dashboard_memory.db"
