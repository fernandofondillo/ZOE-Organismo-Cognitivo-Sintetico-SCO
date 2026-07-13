#!/bin/bash
# ZOE Dashboard Launcher v2.1.1
# Doble click para abrir el Dashboard de ZOE en el navegador

ZOE_HOME="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ZOE_HOME"

# Activar entorno virtual
if [ -f "$ZOE_HOME/../venv/bin/activate" ]; then
    source "$ZOE_HOME/../venv/bin/activate"
elif [ -f "$ZOE_HOME/venv/bin/activate" ]; then
    source "$ZOE_HOME/venv/bin/activate"
fi

# Cargar variables de entorno
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Dashboard v2.1.1                                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Detectar backend disponible
DASH_BACKEND="mock"
DASH_MODEL=""

if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    DASH_BACKEND="ollama"
    DASH_MODEL="auto"
    echo "  ✓ Ollama detectado — Dashboard con ACD Router activo"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    DASH_BACKEND="openai_compatible"
    DASH_MODEL="gpt-4o"
    echo "  ✓ OpenAI configurado — Dashboard con GPT-4o"
else
    echo "  ⚠ Sin modelos — Dashboard en modo demo"
fi

echo ""
echo "  Iniciando servidor en http://localhost:8642 ..."
echo "  El navegador se abrirá automáticamente"
echo ""

# Abrir navegador después de 3 segundos
(sleep 3 && open "http://localhost:8642" 2>/dev/null) &

python -m zoe.web_dashboard --backend "$DASH_BACKEND" ${DASH_MODEL:+--model "$DASH_MODEL"}
