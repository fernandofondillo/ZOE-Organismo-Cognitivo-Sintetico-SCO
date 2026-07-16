#!/bin/bash
# ============================================================================
# ZOE Dashboard Launcher v2.1.2 -- macOS
# Doble click para abrir el Dashboard de ZOE en el navegador.
# Detecta automáticamente el mejor backend (Ollama > OpenAI > Anthropic > pattern).
# ============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Calcular ZOE_HOME
if [ -d "$SCRIPT_DIR/venv" ] && [ -d "$SCRIPT_DIR/zoe" ]; then
    ZOE_HOME="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/../venv" ] && [ -d "$SCRIPT_DIR/../zoe" ]; then
    ZOE_HOME="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    ZOE_HOME="$SCRIPT_DIR"
fi

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  ZOE Dashboard v2.1.2                                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}ZOE_HOME:${NC} $ZOE_HOME"

# ── Paso 0: Matar cualquier proceso ZOE previo en el puerto 8642 ──────────
echo -e "  ${CYAN}INFO${NC} Verificando puerto 8642..."
PID_8642=$(lsof -ti:8642 2>/dev/null || true)
if [ -n "$PID_8642" ]; then
    echo -e "  ${YELLOW}ADVERTENCIA${NC} Puerto 8642 en uso por PID $PID_8642. Deteniendo..."
    kill -9 $PID_8642 2>/dev/null || true
    sleep 2
    echo -e "  ${GREEN}OK${NC} Proceso previo detenido"
else
    echo -e "  ${GREEN}OK${NC} Puerto 8642 libre"
fi

# ── Paso 0b: Matar cualquier proceso ZOE previo en el puerto 8080 ─────────
PID_8080=$(lsof -ti:8080 2>/dev/null || true)
if [ -n "$PID_8080" ]; then
    kill -9 $PID_8080 2>/dev/null || true
    sleep 1
fi

# ── Paso 1: Actualizar código desde GitHub ────────────────────────────────
echo -e "  ${CYAN}INFO${NC} Actualizando código desde GitHub..."
cd "$ZOE_HOME/zoe"
git pull --quiet origin main 2>/dev/null && echo -e "  ${GREEN}OK${NC} Código actualizado" || echo -e "  ${YELLOW}ADVERTENCIA${NC} No se pudo actualizar (sin internet?)"

# ── Paso 2: Cargar variables de entorno ───────────────────────────────────
ENV_FILE="$ZOE_HOME/data/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    echo -e "  ${GREEN}OK${NC} Variables cargadas"
fi

# ── Paso 3: Activar entorno virtual ───────────────────────────────────────
if [ -f "$ZOE_HOME/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ZOE_HOME/venv/bin/activate"
    echo -e "  ${GREEN}OK${NC} Entorno virtual activado"
fi

# ── Paso 4: Apuntar OLLAMA_MODELS al SSD ─────────────────────────────────
if [ -d "$ZOE_HOME/models/ollama" ]; then
    export OLLAMA_MODELS="$ZOE_HOME/models/ollama"
    echo -e "  ${GREEN}OK${NC} OLLAMA_MODELS -> $OLLAMA_MODELS"
fi

# ── Paso 5: Detectar backend ─────────────────────────────────────────────
DASH_BACKEND="pattern"
DASH_MODEL=""
if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    DASH_BACKEND="ollama"; DASH_MODEL="auto"
    # Asegurar que Ollama está corriendo
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${CYAN}INFO${NC} Iniciando Ollama..."
        ollama serve &>/dev/null &
        sleep 3
    fi
    echo -e "  ${GREEN}OK${NC} Ollama detectado -- ACD Router activo (5 niveles cognitivos)"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    DASH_BACKEND="openai_compatible"; DASH_MODEL="gpt-4o"
    echo -e "  ${GREEN}OK${NC} OpenAI -- GPT-4o"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    DASH_BACKEND="anthropic"; DASH_MODEL="claude-sonnet-4-20250514"
    echo -e "  ${GREEN}OK${NC} Anthropic -- Claude Sonnet"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} Sin modelos IA -- PatternSpeaker (offline)"
fi

# ── Paso 6: Arrancar Dashboard ────────────────────────────────────────────
PORT="${ZOE_DASHBOARD_PORT:-8642}"
echo ""
echo -e "  ${BOLD}Iniciando Dashboard en http://localhost:${PORT}/${NC}"
echo -e "  ${BOLD}El navegador se abrirá automáticamente con el token.${NC}"
echo -e "  ${BOLD}Pulsa Ctrl+C para detener ZOE.${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

[ -d "$ZOE_HOME/zoe" ] && cd "$ZOE_HOME/zoe"

exec python -m zoe.web_dashboard \
    --backend "$DASH_BACKEND" \
    ${DASH_MODEL:+--model "$DASH_MODEL"} \
    --port "$PORT" \
    --host "127.0.0.1" \
    --db-path "${ZOE_DATA:-$ZOE_HOME/data}/dashboard_memory.db"
