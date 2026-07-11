#!/bin/bash
# ============================================================================
# ZOE BOOTSTRAP — Instalador Todo-en-Uno para SSD/Pendrive (V1.8.0)
# ============================================================================
# Este script configura ZOE COMPLETO en un SSD/pendrive con un solo comando.
# No carga la memoria del Mac. Todo va al SSD.
#
# Qué hace automáticamente:
#   1. Detecta tu SSD/pendrive
#   2. Verifica Python y Git (los instala si faltan en macOS)
#   3. Instala ZOE + entorno virtual EN EL SSD
#   4. Detecta si tienes Ollama (lo ofrece instalar si no)
#   5. Descarga modelos optimizados al SSD (tú eliges cuáles)
#   6. Configura API keys opcionales (OpenAI, Anthropic)
#   7. Crea scripts lanzadores (.command en macOS, .bat en Windows)
#   8. Arranca el Dashboard de ZOE
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash
#
# O si ya tienes el repo:
#   bash zoe/scripts/zoe-bootstrap.sh
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

print_ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
print_warn() { echo -e "  ${YELLOW}⚠️ ${NC} $1"; }
print_err()  { echo -e "  ${RED}❌${NC} $1"; }
print_info() { echo -e "  ${BLUE}ℹ️${NC} $1"; }
print_step() { echo -e "\n${BOLD}${CYAN}[$1]${NC} $2"; }
print_title() { echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"; echo -e "${BOLD}${CYAN} $1${NC}"; echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}\n"; }

# ============================================================================
# INICIO
# ============================================================================
print_title "ZOE BOOTSTRAP — Instalador Todo-en-Uno"
echo -e "  Configura ZOE completo en tu SSD/pendrive."
echo -e "  No carga la memoria de tu Mac. Todo va al SSD."
echo ""

# ============================================================================
# PASO 1: Detectar SSD/Pendrive
# ============================================================================
print_step "1/8" "Detectar SSD o pendrive"

PLATFORM=$(uname)
ZOE_HOME=""

if [ "$PLATFORM" = "Darwin" ]; then
    # macOS: listar /Volumes
    echo "  Discos disponibles:"
    volumes=()
    i=1
    for vol in /Volumes/*/; do
        volname=$(basename "$vol")
        if [ "$volname" = "Macintosh HD" ] || [ "$volname" = "MacintoshHD" ]; then
            continue
        fi
        # Obtener tamaño
        size=$(diskutil info "$vol" 2>/dev/null | grep "Disk Size" | awk '{print $3, $4}' || echo "?")
        echo "    [$i] $volname ($size) — $vol"
        volumes+=("$vol")
        i=$((i+1))
    done
    
    if [ ${#volumes[@]} -eq 0 ]; then
        print_err "No se encontraron discos externos."
        echo -e "  Conecta un SSD o pendrive y vuelve a ejecutar este script."
        exit 1
    fi
    
    echo ""
    echo -n "  Selecciona el disco [1-${#volumes[@]}] (o 'L' para local en ~/ZOE): "
    read choice
    
    if [ "$choice" = "L" ] || [ "$choice" = "l" ]; then
        ZOE_HOME="$HOME/ZOE"
    elif [ "$choice" -ge 1 ] && [ "$choice" -le ${#volumes[@]} ] 2>/dev/null; then
        ZOE_HOME="${volumes[$((choice-1))]}ZOE"
    else
        print_err "Selección inválida"
        exit 1
    fi

elif [ "$PLATFORM" = "Linux" ]; then
    # Linux: listar /media
    echo "  Discos disponibles en /media:"
    volumes=()
    i=1
    for vol in /media/*/*/; do
        echo "    [$i] $vol"
        volumes+=("$vol")
        i=$((i+1))
    done
    
    if [ ${#volumes[@]} -eq 0 ]; then
        print_info "No se encontraron discos en /media. Instalando en ~/ZOE"
        ZOE_HOME="$HOME/ZOE"
    else
        echo -n "  Selecciona [1-${#volumes[@]}] (o 'L' para ~/ZOE): "
        read choice
        if [ "$choice" = "L" ] || [ "$choice" = "l" ]; then
            ZOE_HOME="$HOME/ZOE"
        elif [ "$choice" -ge 1 ] && [ "$choice" -le ${#volumes[@]} ] 2>/dev/null; then
            ZOE_HOME="${volumes[$((choice-1))]}ZOE"
        fi
    fi
fi

# Crear directorio
mkdir -p "$ZOE_HOME"
print_ok "Instalando en: $ZOE_HOME"

# ============================================================================
# PASO 2: Verificar Python y Git
# ============================================================================
print_step "2/8" "Verificar Python y Git"

# Python
if command -v python3 &> /dev/null; then
    PYVER=$(python3 --version 2>&1)
    print_ok "Python: $PYVER"
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYVER=$(python --version 2>&1)
    print_ok "Python: $PYVER"
    PYTHON=python
else
    print_err "Python no encontrado."
    if [ "$PLATFORM" = "Darwin" ]; then
        echo -e "  Instala con: xcode-select --install"
        echo -e "  O descarga desde: https://python.org"
    else
        echo -e "  Instala con: sudo apt install python3 python3-venv"
    fi
    exit 1
fi

# Git
if command -v git &> /dev/null; then
    print_ok "Git: $(git --version)"
else
    print_warn "Git no encontrado. Instalando..."
    if [ "$PLATFORM" = "Darwin" ]; then
        xcode-select --install 2>/dev/null || true
    else
        sudo apt update && sudo apt install -y git
    fi
fi

# ============================================================================
# PASO 3: Clonar ZOE y crear entorno virtual EN EL SSD
# ============================================================================
print_step "3/8" "Instalar ZOE en el SSD"

if [ -d "$ZOE_HOME/zoe" ]; then
    print_info "ZOE ya existe en el SSD. Actualizando..."
    cd "$ZOE_HOME/zoe"
    git pull --quiet || true
else
    print_info "Clonando repositorio de ZOE..."
    git clone --quiet https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git "$ZOE_HOME/zoe"
fi

# Crear entorno virtual EN EL SSD (no en el Mac)
if [ ! -d "$ZOE_HOME/venv" ]; then
    print_info "Creando entorno virtual Python en el SSD..."
    $PYTHON -m venv "$ZOE_HOME/venv"
fi

# Activar e instalar
print_info "Instalando dependencias (1-2 min)..."
cd "$ZOE_HOME/zoe"
"$ZOE_HOME/venv/bin/pip" install --upgrade pip --quiet
"$ZOE_HOME/venv/bin/pip" install -e . --quiet
print_ok "ZOE instalado en el SSD"

# Crear directorio de datos
mkdir -p "$ZOE_HOME/data"

# ============================================================================
# PASO 4: Ollama (opcional pero recomendado)
# ============================================================================
print_step "4/8" "Configurar Ollama (IA local gratis)"

INSTALL_OLLAMA="n"
OLLAMA_RUNNING=false

if command -v ollama &> /dev/null; then
    print_ok "Ollama instalado: $(ollama --version 2>/dev/null || echo 'OK')"
    # Verificar si está corriendo
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_ok "Ollama está corriendo"
        OLLAMA_RUNNING=true
    else
        print_info "Iniciando Ollama..."
        ollama serve &> /dev/null &
        sleep 3
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            OLLAMA_RUNNING=true
            print_ok "Ollama iniciado"
        else
            print_warn "Ollama no pudo iniciar. Lo iniciarás manualmente con: ollama serve"
        fi
    fi
else
    print_warn "Ollama no está instalado."
    echo -e "  ${BOLD}¿Instalar Ollama?${NC} (recomendado — IA local gratis, sin internet)"
    echo -n "  Instalar Ollama ahora? (s/N): "
    read INSTALL_OLLAMA
    
    if [ "$INSTALL_OLLAMA" = "s" ] || [ "$INSTALL_OLLAMA" = "S" ]; then
        print_info "Instalando Ollama..."
        if [ "$PLATFORM" = "Darwin" ]; then
            curl -fsSL https://ollama.com/install.sh | sh
        else
            curl -fsSL https://ollama.com/install.sh | sh
        fi
        # Iniciar
        ollama serve &> /dev/null &
        sleep 4
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            OLLAMA_RUNNING=true
            print_ok "Ollama instalado y corriendo"
        else
            print_warn "Ollama instalado. Inicia con: ollama serve"
        fi
    else
        print_info "Ollama no instalado. ZOE funcionará con PatternSpeaker (sin IA)."
        print_info "Puedes instalarlo después desde https://ollama.com"
    fi
fi

# ============================================================================
# PASO 5: Descargar modelos optimizados al SSD
# ============================================================================
print_step "5/8" "Descargar modelos de IA al SSD"

MODELS_DIR="$ZOE_HOME/models"
mkdir -p "$MODELS_DIR"

# Configurar Ollama para usar el SSD como almacenamiento
export OLLAMA_MODELS="$MODELS_DIR"

if [ "$OLLAMA_RUNNING" = true ]; then
    
    echo ""
    echo -e "  ${BOLD}ZOE puede usar diferentes modelos según el tipo de pregunta:${NC}"
    echo -e "  ${CYAN}L0/L1${NC} (rápido):     Gemma 2 9B (3.5GB, 15-25 t/s) ⚡"
    echo -e "  ${CYAN}L2${NC} (estándar):    Qwen 2.5 7B (4.5GB, 12-18 t/s) ✅"
    echo -e "  ${CYAN}L3${NC} (profundo):    Qwen 2.5 14B (8GB, 4-8 t/s) 📖"
    echo ""
    echo "  Puedes elegir qué modelos descargar:"
    echo "    [1] Solo Gemma 2 9B (3.5GB) — mínimo, ultra rápido"
    echo "    [2] Gemma 2 9B + Qwen 2.5 7B (8GB) — equilibrado"
    echo "    [3] Gemma 2 9B + Qwen 2.5 14B (11.5GB) — completo"
    echo "    [4] No descargar modelos ahora (usar PatternSpeaker)"
    echo "    [5] Saltar — ya tengo modelos"
    echo ""
    echo -n "  Elige [1-5]: "
    read model_choice
    
    download_model() {
        local name=$1
        local size=$2
        if ! ollama list 2>/dev/null | grep -q "$name"; then
            echo -e "  📥 Descargando $name ($size)..."
            ollama pull "$name" 2>&1 | tail -1
            print_ok "$name descargado"
        else
            print_ok "$name ya está instalado"
        fi
    }
    
    case $model_choice in
        1)
            download_model "gemma2:9b" "5.5GB"
            ;;
        2)
            download_model "gemma2:9b" "5.5GB"
            download_model "qwen2.5:7b" "4.5GB"
            ;;
        3)
            download_model "gemma2:9b" "5.5GB"
            download_model "qwen2.5:14b" "8GB"
            ;;
        4)
            print_info "Sin modelos. ZOE usará PatternSpeaker (funciona sin IA)."
            ;;
        5)
            print_info "Saltando descarga de modelos."
            ;;
        *)
            print_info "Opción no válida. ZOE usará PatternSpeaker."
            ;;
    esac
else
    print_info "Ollama no está corriendo. Saltando descarga de modelos."
    print_info "ZOE funcionará con PatternSpeaker (sin IA, patrones + memoria)."
fi

# ============================================================================
# PASO 6: API Keys opcionales (cloud)
# ============================================================================
print_step "6/8" "Configurar API keys de cloud (opcional)"

ENV_FILE="$ZOE_HOME/data/.env"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

echo "  Puedes configurar API keys de cloud para máxima calidad en L3."
echo "  ZOE usará cloud SOLO para preguntas complejas (ahorra dinero)."
echo ""

echo -n "  ¿Configurar OpenAI API key? (s/N): "
read config_openai
if [ "$config_openai" = "s" ] || [ "$config_openai" = "S" ]; then
    echo -n "  Pega tu API key (sk-...): "
    read -s openai_key
    echo "OPENAI_API_KEY=$openai_key" >> "$ENV_FILE"
    print_ok "OpenAI API key guardada en $ENV_FILE"
fi

echo -n "  ¿Configurar Anthropic (Claude) API key? (s/N): "
read config_anthropic
if [ "$config_anthropic" = "s" ] || [ "$config_anthropic" = "S" ]; then
    echo -n "  Pega tu API key (sk-ant-...): "
    read -s anthropic_key
    echo "ANTHROPIC_API_KEY=$anthropic_key" >> "$ENV_FILE"
    print_ok "Anthropic API key guardada en $ENV_FILE"
fi

# ============================================================================
# PASO 7: Crear scripts lanzadores
# ============================================================================
print_step "7/8" "Crear scripts lanzadores"

# Función para cargar .env
LOAD_ENV='if [ -f "$ZOE_HOME/data/.env" ]; then export $(grep -v "^#" "$ZOE_HOME/data/.env" | xargs); fi'

# --- macOS: .command ---
if [ "$PLATFORM" = "Darwin" ]; then
    
    # ZOE-Chat (PatternSpeaker — sin IA)
    cat > "$ZOE_HOME/ZOE-Chat.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat.command"
    
    # ZOE-Chat-Ollama
    cat > "$ZOE_HOME/ZOE-Chat-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend ollama --model qwen2.5:7b
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.command"
    
    # ZOE-Dashboard (PatternSpeaker — sin IA)
    cat > "$ZOE_HOME/ZOE-Dashboard.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard.command"
    
    # ZOE-Dashboard-Ollama
    cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend ollama --model qwen2.5:7b
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.command"
    
    print_ok "4 scripts .command creados en $ZOE_HOME"

# --- Linux ---
elif [ "$PLATFORM" = "Linux" ]; then
    
    # ZOE-Chat
    cat > "$ZOE_HOME/ZOE-Chat.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat.sh"
    
    # ZOE-Dashboard
    cat > "$ZOE_HOME/ZOE-Dashboard.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard.sh"
    
    print_ok "2 scripts .sh creados en $ZOE_HOME"
fi

# ============================================================================
# PASO 8: Resumen y arranque
# ============================================================================
print_step "8/8" "Resumen"

print_title "¡ZOE ESTÁ LISTA!"

echo -e "  ${BOLD}Ubicación:${NC} $ZOE_HOME"
echo ""

# Mostrar qué hay instalado
echo -e "  ${BOLD}Componentes instalados:${NC}"
print_ok "ZOE V1.8.0 (código + entorno virtual)"
print_ok "PatternSpeaker (funciona sin IA, siempre disponible)"

if [ "$OLLAMA_RUNNING" = true ]; then
    print_ok "Ollama (IA local gratis)"
    echo -e "  ${BOLD}Modelos disponibles:${NC}"
    ollama list 2>/dev/null | tail -n +2 | while read line; do
        if [ -n "$line" ]; then
            echo -e "    📦 $line"
        fi
    done
fi

if [ -s "$ENV_FILE" ]; then
    if grep -q "OPENAI_API_KEY" "$ENV_FILE" 2>/dev/null; then
        print_ok "OpenAI API key configurada"
    fi
    if grep -q "ANTHROPIC_API_KEY" "$ENV_FILE" 2>/dev/null; then
        print_ok "Anthropic API key configurada"
    fi
fi

echo ""
echo -e "  ${BOLD}Cómo usar ZOE:${NC}"
echo ""
echo -e "  ${CYAN}Opción 1: CLI (terminal)${NC}"
echo "    Doble clic en ZOE-Chat.command (macOS)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend pattern"
echo ""
echo -e "  ${CYAN}Opción 2: Dashboard web${NC}"
echo "    Doble clic en ZOE-Dashboard.command (macOS)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.web_dashboard --backend pattern"
echo "    → Abre http://localhost:8642 en tu navegador"
echo ""
echo -e "  ${CYAN}Opción 3: Con IA (si instalaste Ollama)${NC}"
echo "    Doble clic en ZOE-Chat-Ollama.command"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend ollama --model qwen2.5:7b"
echo ""
echo -e "  ${CYAN}Consejos:${NC}"
echo "    • Escribe /help dentro de ZOE para ver comandos"
echo "    • Escribe /capsules para ver cápsulas de conocimiento"
echo "    • Escribe /capsule elder_care_knowledge para cargar una"
echo "    • Escribe /quit para salir (guarda memoria automáticamente)"
echo ""

# ¿Arrancar Dashboard ahora?
echo -n "  ¿Arrancar Dashboard ahora? (s/N): "
read start_now

if [ "$start_now" = "s" ] || [ "$start_now" = "S" ]; then
    echo ""
    print_info "Arrancando Dashboard..."
    print_info "Abre http://localhost:8642 en tu navegador"
    echo ""
    
    # Determinar backend
    if [ "$OLLAMA_RUNNING" = true ]; then
        BACKEND="ollama"
        MODEL="--model qwen2.5:7b"
    else
        BACKEND="pattern"
        MODEL=""
    fi
    
    cd "$ZOE_HOME/zoe"
    export OLLAMA_MODELS="$MODELS_DIR"
    if [ -f "$ENV_FILE" ]; then
        export $(grep -v "^#" "$ENV_FILE" | xargs)
    fi
    
    "$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend $BACKEND $MODEL
else
    echo ""
    echo -e "  ${GREEN}Para empezar más tarde:${NC}"
    echo "    Doble clic en ZOE-Dashboard.command en tu SSD"
    echo ""
fi

echo ""
echo -e "  ${BOLD}${GREEN}¡Gracias por instalar ZOE!${NC}"
echo -e "  ZOE es un organismo cognitivo sintético. No es un chatbot."
echo -e "  Tiene memoria, metabolismo y identidad propia."
echo -e "  Trátala como un compañero, no como una herramienta."
echo ""
