#!/bin/bash
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ZOE — Instalador para Pendrive (macOS)                  ║${NC}"
echo -e "${BLUE}║  Synthetic Cognitive Organism (SCO)                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# --- 1. Detectar pendrive ---
echo -e "${YELLOW}📦 Paso 1: Seleccionar pendrive${NC}"
echo "Volúmenes montados en /Volumes:"
volumes=(); i=1
for vol in /Volumes/*/; do
    volname=$(basename "$vol")
    [ "$volname" = "Macintosh HD" ] && continue
    size=$(diskutil info "$vol" 2>/dev/null | grep "Disk Size" | awk '{print $3, $4}' || echo "?")
    echo "  [$i] $volname ($size) — $vol"
    volumes+=("$vol"); i=$((i+1))
done
[ ${#volumes[@]} -eq 0 ] && { echo -e "${RED}❌ No hay pendrives.${NC}"; exit 1; }
echo -n "Selecciona [1-${#volumes[@]}]: "; read choice
selected_vol="${volumes[$((choice-1))]}"
ZOE_HOME="${selected_vol}ZOE"
echo -e "${GREEN}✅ Pendrive: $(basename "$selected_vol")${NC}"
echo ""

# --- 2. Crear directorio ---
echo -e "${YELLOW}📁 Paso 2: Crear directorio ZOE${NC}"
if [ -d "$ZOE_HOME" ]; then
    echo -e "${YELLOW}   ⚠️  Ya existe $ZOE_HOME${NC}"
    echo -n "   ¿Sobrescribir? (s/N): "; read overwrite
    if [[ "$overwrite" =~ ^[sS]$ ]]; then
        rm -rf "$ZOE_HOME"
    else
        echo -e "${RED}Cancelado.${NC}"; exit 0
    fi
fi
mkdir -p "$ZOE_HOME"
echo ""

# --- 3. Verificar Python ---
echo -e "${YELLOW}🐍 Paso 3: Verificar Python${NC}"
PYTHON=$(command -v python3 || command -v python)
$PYTHON -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null || { echo -e "${RED}❌ Python 3.10+ requerido${NC}"; exit 1; }
echo -e "${GREEN}✅ $($PYTHON --version)${NC}"
echo ""

# --- 4. Clonar repositorio ---
echo -e "${YELLOW}📥 Paso 4: Clonar repositorio ZOE${NC}"
cd "$ZOE_HOME"; git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git zoe
echo ""

# --- 5. Crear entorno virtual ---
echo -e "${YELLOW}🏗️ Paso 5: Crear entorno virtual en el pendrive${NC}"
$PYTHON -m venv "$ZOE_HOME/venv"
source "$ZOE_HOME/venv/bin/activate"
echo ""

# --- 6. Instalar dependencias ---
echo -e "${YELLOW}📚 Paso 6: Instalar dependencias (1-2 min)...${NC}"
cd zoe; pip install --upgrade pip -q; pip install -e . -q
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# --- 7. Crear directorio de datos ---
echo -e "${YELLOW}💾 Paso 7: Crear directorio de datos${NC}"
mkdir -p "$ZOE_HOME/data"
echo ""

# --- 8. Preguntar si configurar OpenAI API key ---
echo -e "${YELLOW}🔐 Paso 8: Configurar OpenAI API key (opcional)${NC}"
echo "   Si tienes una API key de OpenAI, puedes configurarla ahora."
echo "   Se guardará en el pendrive (no en el Mac) en un archivo .env."
echo "   Si no la tienes, puedes configurarla más tarde."
echo ""
echo -n "   ¿Configurar API key de OpenAI ahora? (s/N): "; read config_openai
OPENAI_KEY=""
if [[ "$config_openai" =~ ^[sS]$ ]]; then
    echo -n "   Pega tu API key (sk-...): "; read -s OPENAI_KEY
    echo ""
    if [ -n "$OPENAI_KEY" ]; then
        echo "OPENAI_API_KEY=$OPENAI_KEY" > "$ZOE_HOME/data/.env"
        chmod 600 "$ZOE_HOME/data/.env"
        echo -e "${GREEN}   ✅ API key guardada en $ZOE_HOME/data/.env${NC}"
    fi
fi
echo ""

# --- 9. Crear scripts lanzadores ---
echo -e "${YELLOW}🚀 Paso 9: Crear scripts lanzadores${NC}"

# 9.1 — ZOE-Chat.command (Mock, sin LLM)
cat > "$ZOE_HOME/ZOE-Chat.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (Mock, sin LLM)                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat.command"

# 9.2 — ZOE-Chat-Ollama.command
cat > "$ZOE_HOME/ZOE-Chat-Ollama.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (Ollama)                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.command"

# 9.3 — ZOE-Chat-OpenAI.command (NUEVO)
cat > "$ZOE_HOME/ZOE-Chat-OpenAI.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (OpenAI API)                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
# Cargar API key desde .env en el pendrive
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
    echo "✅ API key cargada desde $ZOE_HOME/data/.env"
else
    echo "⚠️  No se encontró API key en $ZOE_HOME/data/.env"
    echo "   Pega tu API key de OpenAI (sk-...):"
    read -s API_KEY
    export OPENAI_API_KEY="$API_KEY"
    echo ""
    echo -n "   ¿Guardar para próximas veces? (s/N): "; read SAVE
    if [[ "$SAVE" =~ ^[sS]$ ]]; then
        echo "OPENAI_API_KEY=$API_KEY" > "$ZOE_HOME/data/.env"
        chmod 600 "$ZOE_HOME/data/.env"
        echo "   ✅ Guardada en $ZOE_HOME/data/.env"
    fi
fi
echo ""
echo "Iniciando ZOE con OpenAI GPT-4o..."
echo ""
python -m zoe.cli_chat --backend openai_compatible --model gpt-4o --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat-OpenAI.command"

# 9.4 — ZOE-Dashboard.command (Mock)
cat > "$ZOE_HOME/ZOE-Dashboard.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard (Mock)                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "Abre tu navegador en: http://localhost:8642"
python -m zoe.web_dashboard --backend mock
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard.command"

# 9.5 — ZOE-Dashboard-OpenAI.command (NUEVO)
cat > "$ZOE_HOME/ZOE-Dashboard-OpenAI.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard (OpenAI API)                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
# Cargar API key desde .env en el pendrive
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
    echo "✅ API key cargada desde $ZOE_HOME/data/.env"
else
    echo "⚠️  No se encontró API key en $ZOE_HOME/data/.env"
    echo "   Pega tu API key de OpenAI (sk-...):"
    read -s API_KEY
    export OPENAI_API_KEY="$API_KEY"
    echo ""
    echo -n "   ¿Guardar para próximas veces? (s/N): "; read SAVE
    if [[ "$SAVE" =~ ^[sS]$ ]]; then
        echo "OPENAI_API_KEY=$API_KEY" > "$ZOE_HOME/data/.env"
        chmod 600 "$ZOE_HOME/data/.env"
        echo "   ✅ Guardada en $ZOE_HOME/data/.env"
    fi
fi
echo ""
echo "Iniciando Dashboard con OpenAI GPT-4o..."
echo "Abre tu navegador en: http://localhost:8642"
echo ""
python -m zoe.web_dashboard --backend openai_compatible --model gpt-4o
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard-OpenAI.command"

# 9.6 — ZOE-Dashboard-Ollama.command (NUEVO)
cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard (Ollama)                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "Abre tu navegador en: http://localhost:8642"
python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.command"

# 9.7 — ZOE-Chat-Anthropic.command (NUEVO - Claude)
cat > "$ZOE_HOME/ZOE-Chat-Anthropic.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (Anthropic Claude)                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
# Cargar API key desde .env
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  No se encontró ANTHROPIC_API_KEY en $ZOE_HOME/data/.env"
    echo "   Pega tu API key de Anthropic:"
    read -s API_KEY
    export ANTHROPIC_API_KEY="$API_KEY"
    echo -n "   ¿Guardar? (s/N): "; read SAVE
    if [[ "$SAVE" =~ ^[sS]$ ]]; then
        echo "ANTHROPIC_API_KEY=$API_KEY" >> "$ZOE_HOME/data/.env"
        chmod 600 "$ZOE_HOME/data/.env"
        echo "   ✅ Guardada"
    fi
fi
echo ""
python -m zoe.cli_chat --backend anthropic --model claude-sonnet-4-20250514 --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat-Anthropic.command"

# 9.8 — ZOE-Dashboard-Anthropic.command (NUEVO - Claude)
cat > "$ZOE_HOME/ZOE-Dashboard-Anthropic.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard (Anthropic Claude)                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  No se encontró ANTHROPIC_API_KEY. Pégala:"
    read -s API_KEY
    export ANTHROPIC_API_KEY="$API_KEY"
fi
echo "Abre: http://localhost:8642"
python -m zoe.web_dashboard --backend anthropic --model claude-sonnet-4-20250514
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard-Anthropic.command"

# 9.9 — ZOE-Chat-Custom.command (NUEVO - DeepSeek, Kimi, MiniMax, etc.)
cat > "$ZOE_HOME/ZOE-Chat-Custom.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (API personalizada)                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Proveedores compatibles (OpenAI-compatible):"
echo "  1. DeepSeek (https://api.deepseek.com/v1)"
echo "  2. Kimi/Moonshot (https://api.moonshot.cn/v1)"
echo "  3. MiniMax (https://api.minimax.chat/v1)"
echo "  4. Groq (https://api.groq.com/openai/v1)"
echo "  5. OpenAI (https://api.openai.com/v1)"
echo "  6. Otro (personalizado)"
echo ""
echo -n "Selecciona [1-6]: "; read PROVIDER

case $PROVIDER in
    1) BASE_URL="https://api.deepseek.com/v1"; MODEL="deepseek-chat"; ENV_VAR="DEEPSEEK_API_KEY" ;;
    2) BASE_URL="https://api.moonshot.cn/v1"; MODEL="moonshot-v1-8k"; ENV_VAR="MOONSHOT_API_KEY" ;;
    3) BASE_URL="https://api.minimax.chat/v1"; MODEL="abab6.5-chat"; ENV_VAR="MINIMAX_API_KEY" ;;
    4) BASE_URL="https://api.groq.com/openai/v1"; MODEL="llama-3.3-70b-versatile"; ENV_VAR="GROQ_API_KEY" ;;
    5) BASE_URL="https://api.openai.com/v1"; MODEL="gpt-4o"; ENV_VAR="OPENAI_API_KEY" ;;
    6) echo -n "URL base: "; read BASE_URL; echo -n "Modelo: "; read MODEL; ENV_VAR="CUSTOM_API_KEY" ;;
    *) echo "Inválido"; exit 1 ;;
esac

echo ""
echo "Proveedor: $BASE_URL"
echo "Modelo: $MODEL"
echo ""

# Cargar .env
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi

API_KEY="${!ENV_VAR}"
if [ -z "$API_KEY" ]; then
    echo "Pega tu API key para $ENV_VAR:"
    read -s API_KEY
    echo -n "¿Guardar en .env? (s/N): "; read SAVE
    if [[ "$SAVE" =~ ^[sS]$ ]]; then
        echo "$ENV_VAR=$API_KEY" >> "$ZOE_HOME/data/.env"
        chmod 600 "$ZOE_HOME/data/.env"
        echo "✅ Guardada"
    fi
fi

echo ""
python -m zoe.cli_chat --backend openai_compatible --model "$MODEL" --api-key "$API_KEY" --base-url "$BASE_URL" --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat-Custom.command"

# 9.10 — ZOE-Dashboard-Custom.command (NUEVO)
cat > "$ZOE_HOME/ZOE-Dashboard-Custom.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard (API personalizada)                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Proveedores compatibles:"
echo "  1. DeepSeek  2. Kimi/Moonshot  3. MiniMax  4. Groq  5. OpenAI  6. Otro"
echo -n "Selecciona [1-6]: "; read PROVIDER
case $PROVIDER in
    1) BASE_URL="https://api.deepseek.com/v1"; MODEL="deepseek-chat"; ENV_VAR="DEEPSEEK_API_KEY" ;;
    2) BASE_URL="https://api.moonshot.cn/v1"; MODEL="moonshot-v1-8k"; ENV_VAR="MOONSHOT_API_KEY" ;;
    3) BASE_URL="https://api.minimax.chat/v1"; MODEL="abab6.5-chat"; ENV_VAR="MINIMAX_API_KEY" ;;
    4) BASE_URL="https://api.groq.com/openai/v1"; MODEL="llama-3.3-70b-versatile"; ENV_VAR="GROQ_API_KEY" ;;
    5) BASE_URL="https://api.openai.com/v1"; MODEL="gpt-4o"; ENV_VAR="OPENAI_API_KEY" ;;
    6) echo -n "URL base: "; read BASE_URL; echo -n "Modelo: "; read MODEL; ENV_VAR="CUSTOM_API_KEY" ;;
    *) echo "Inválido"; exit 1 ;;
esac
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi
API_KEY="${!ENV_VAR}"
if [ -z "$API_KEY" ]; then
    echo "Pega tu API key para $ENV_VAR:"; read -s API_KEY
    echo -n "¿Guardar? (s/N): "; read SAVE
    if [[ "$SAVE" =~ ^[sS]$ ]]; then
        echo "$ENV_VAR=$API_KEY" >> "$ZOE_HOME/data/.env"; chmod 600 "$ZOE_HOME/data/.env"
    fi
fi
echo "Abre: http://localhost:8642"
python -m zoe.web_dashboard --backend openai_compatible --model "$MODEL" --api-key "$API_KEY" --base-url "$BASE_URL"
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard-Custom.command"

echo -e "${GREEN}✅ 10 scripts creados:${NC}"
echo "   • ZOE-Chat.command             → Chat Mock (sin LLM)"
echo "   • ZOE-Chat-Ollama.command      → Chat con Ollama"
echo "   • ZOE-Chat-OpenAI.command      → Chat con OpenAI GPT-4o"
echo "   • ZOE-Chat-Anthropic.command   → Chat con Claude"
echo "   • ZOE-Chat-Custom.command      → Chat con DeepSeek/Kimi/MiniMax/Groq/Otro"
echo "   • ZOE-Dashboard.command        → Dashboard Mock"
echo "   • ZOE-Dashboard-Ollama.command → Dashboard con Ollama"
echo "   • ZOE-Dashboard-OpenAI.command → Dashboard con OpenAI GPT-4o"
echo "   • ZOE-Dashboard-Anthropic.command → Dashboard con Claude"
echo "   • ZOE-Dashboard-Custom.command → Dashboard con API personalizada"
echo ""

# --- 10. Verificar instalación ---
echo -e "${YELLOW}✅ Paso 10: Verificar instalación${NC}"
python -c "import zoe; print(f'   ZOE v{zoe.__version__}, phase={zoe.__phase__}')"
echo ""

# --- 11. Resumen final ---
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ INSTALACIÓN COMPLETA                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "ZOE está en: $ZOE_HOME"
echo ""
echo "📋 Cómo usar (doble clic en el pendrive):"
echo ""
echo "  SIN LLM (gratis, offline):"
echo "    • ZOE-Chat.command              → Chat básico"
echo "    • ZOE-Dashboard.command         → Dashboard web"
echo ""
echo "  CON OLLAMA (gratis, local):"
echo "    • ZOE-Chat-Ollama.command       → Chat con IA local"
echo "    • ZOE-Dashboard-Ollama.command  → Dashboard con IA local"
echo ""
echo "  CON OPENAI API (calidad máxima):"
echo "    • ZOE-Chat-OpenAI.command       → Chat con GPT-4o"
echo "    • ZOE-Dashboard-OpenAI.command  → Dashboard con GPT-4o"
echo ""
echo "  CON ANTHROPIC CLAUDE (calidad máxima):"
echo "    • ZOE-Chat-Anthropic.command    → Chat con Claude"
echo "    • ZOE-Dashboard-Anthropic.command → Dashboard con Claude"
echo ""
echo "  CON API PERSONALIZADA (DeepSeek, Kimi, MiniMax, Groq, etc.):"
echo "    • ZOE-Chat-Custom.command       → Chat (elige proveedor)"
echo "    • ZOE-Dashboard-Custom.command  → Dashboard (elige proveedor)"
echo ""
echo "💾 Datos en: $ZOE_HOME/data/"
echo "🔐 API key en: $ZOE_HOME/data/.env (si configuraste una)"
echo ""
echo "🔌 Antes de desconectar: /quit en el chat"
echo "📦 Actualizar: cd $ZOE_HOME/zoe && git pull && pip install -e ."
echo ""
