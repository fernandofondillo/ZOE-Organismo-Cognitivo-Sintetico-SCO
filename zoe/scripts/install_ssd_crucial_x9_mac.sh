#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# ZOE — Instalador para SSD Crucial X9 1TB + MacBook Air M3
# Synthetic Cognitive Organism (SCO) v2.0.0-rc1
# ═══════════════════════════════════════════════════════════════════════════════
# Uso: bash install_ssd_crucial_x9_mac.sh
# Requisitos: MacBook Air M3 8GB+, SSD Crucial X9 1TB, Python 3.10+, Git
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ── Banner ───────────────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "  ███████╗ ██████╗ ███████╗"
echo "  ╚══███╔╝██╔═══██╗██╔════╝"
echo "    ███╔╝ ██║   ██║█████╗  "
echo "   ███╔╝  ██║   ██║██╔══╝  "
echo "  ███████╗╚██████╔╝███████╗"
echo "  ╚══════╝ ╚═════╝ ╚══════╝"
echo -e "${NC}"
echo -e "${BOLD}  Synthetic Cognitive Organism (SCO) v2.0.0-rc1${NC}"
echo -e "  Instalador para ${BOLD}SSD Crucial X9 1TB${NC} + ${BOLD}MacBook Air M3${NC}"
echo ""
echo -e "  Tiempo estimado: 15-30 minutos (sin modelos) / 1-3 horas (con modelos)"
echo ""

# ── Funciones auxiliares ─────────────────────────────────────────────────────
step=0
total_steps=12

print_step() {
    step=$((step + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Paso ${step}/${total_steps}: ${1}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_ok() { echo -e "${GREEN}  ✓ ${1}${NC}"; }
print_warn() { echo -e "${YELLOW}  ⚠ ${1}${NC}"; }
print_error() { echo -e "${RED}  ✗ ${1}${NC}"; }

# ── Paso 1: Verificar macOS ─────────────────────────────────────────────────
print_step "Verificar sistema operativo"
if [[ "$(uname -s)" != "Darwin" ]]; then
    print_error "Este instalador es solo para macOS. Detectado: $(uname -s)"
    exit 1
fi
MACOS_VERSION=$(sw_vers -productVersion)
print_ok "macOS ${MACOS_VERSION} detectado"

# ── Paso 2: Verificar arquitectura Apple Silicon ────────────────────────────
print_step "Verificar procesador Apple Silicon"
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_ok "Apple Silicon (M1/M2/M3/M4) detectado — Optimal"
else
    print_warn "Arquitectura Intel detectada. ZOE funciona pero los modelos serán más lentos."
fi

# ── Paso 3: Verificar RAM ───────────────────────────────────────────────────
print_step "Verificar memoria RAM"
RAM_GB=$(sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1024/1024/1024)}')
if [[ -z "$RAM_GB" || "$RAM_GB" == "0" ]]; then
    RAM_GB=$(system_profiler SPHardwareDataType 2>/dev/null | grep "Memory:" | awk '{print $2}')
fi
if [[ ${RAM_GB:-0} -ge 8 ]]; then
    print_ok "RAM: ${RAM_GB}GB (mínimo 8GB ✓)"
else
    print_error "RAM insuficiente: ${RAM_GB}GB. Se requieren al menos 8GB."
    exit 1
fi

# ── Paso 4: Detectar SSD Crucial X9 ─────────────────────────────────────────
print_step "Detectar SSD Crucial X9"

# Buscar SSDs conectados por USB-C
SSDS=()
SSD_INFOS=()

# Método 1: diskutil list external
while IFS= read -r line; do
    if echo "$line" | grep -q "external"; then
        DISK_ID=$(echo "$line" | awk '{print $1}')
        DISK_SIZE=$(echo "$line" | grep -o '[0-9]*\.[0-9]* \w*B' | head -1 || echo "?")
        DISK_NAME=$(echo "$line" | sed 's/.*physical //' | awk '{print $1}' || echo "External")
        SSDS+=("$DISK_ID")
        SSD_INFOS+=("$DISK_NAME ($DISK_SIZE)")
    fi
done < <(diskutil list external 2>/dev/null | grep "external" || true)

# Método 2: Volumes en /Volumes
VOLUMES=()
for vol in /Volumes/*/; do
    volname=$(basename "$vol")
    [[ "$volname" == "Macintosh HD" ]] && continue
    [[ "$volname" == "Home" ]] && continue
    size=$(diskutil info "$vol" 2>/dev/null | grep "Total Size" | awk '{print $3, $4}' || echo "?")
    # Verificar si es físico (no DMG, no red)
    is_physical=$(diskutil info "$vol" 2>/dev/null | grep "Protocol:" | grep -v "Disk Image" | grep -v "WebDAV" | head -1 || true)
    if [[ -n "$is_physical" ]]; then
        VOLUMES+=("$vol")
        vol_disp="${volname} (${size})"
        # Verificar si es Crucial X9
        if echo "$volname" | grep -qi "crucial\|x9"; then
            vol_disp="${volname} (${size}) — ${GREEN}¡SSD Crucial detectado!${NC}"
        fi
        # Solo añadir si no ya en SSDS
        found=0
        for s in "${SSDS[@]}"; do
            [[ "$s" == "$vol" ]] && found=1 && break
        done
        if [[ $found -eq 0 ]]; then
            SSDS+=("$vol")
            SSD_INFOS+=("$vol_disp")
        fi
    fi
done

if [[ ${#SSDS[@]} -eq 0 ]]; then
    print_error "No se detectó ningún SSD externo."
    echo ""
    echo "  Por favor:"
    echo "  1. Conecta el SSD Crucial X9 al MacBook con el cable USB-C CORTO"
    echo "     (el cable largo de carga es USB 2.0 y va 10x más lento)"
    echo "  2. Asegúrate de que el LED del SSD está encendido"
    echo "  3. Comprueba que aparece en Finder"
    echo ""
    echo -n "  ¿Quieres continuar con instalación en el Mac (sin SSD)? (s/N): "
    read CONTINUE
    if [[ ! "$CONTINUE" =~ ^[sS]$ ]]; then
        exit 1
    fi
    # Instalación en el Mac directamente
    ZOE_HOME="${HOME}/ZOE"
    INSTALL_TYPE="mac_internal"
    print_warn "Continuando con instalación en disco interno: ${ZOE_HOME}"
else
    echo ""
    echo -e "  ${BOLD}SSDs detectados:${NC}"
    for i in "${!SSDS[@]}"; do
        idx=$((i + 1))
        echo -e "    [${idx}] ${SSD_INFOS[$i]}"
    done
    echo ""
    if [[ ${#SSDS[@]} -eq 1 ]]; then
        SELECTED_IDX=0
        print_ok "SSD seleccionado automáticamente: ${SSD_INFOS[0]}"
    else
        echo -n "  Selecciona SSD [1-${#SSDS[@]}]: "
        read CHOICE
        SELECTED_IDX=$((CHOICE - 1))
    fi
    SELECTED_SSD="${SSDS[$SELECTED_IDX]}"
    ZOE_HOME="${SELECTED_SSD%/}/ZOE"
    INSTALL_TYPE="ssd_crucial"
    print_ok "Instalando en: ${ZOE_HOME}"
fi

# ── Paso 5: Verificar formato del SSD ───────────────────────────────────────
print_step "Verificar formato del SSD"
if [[ "$INSTALL_TYPE" == "ssd_crucial" ]]; then
    FS_TYPE=$(diskutil info "$SELECTED_SSD" 2>/dev/null | grep "Type (Bundle)" | awk '{print $3}' || echo "unknown")
    if [[ "$FS_TYPE" == "exfat" ]]; then
        print_ok "Formato exFAT — compatible con Mac, Windows, Android"
    elif [[ "$FS_TYPE" == "apfs" ]]; then
        print_ok "Formato APFS — máxima velocidad en Apple"
    else
        print_warn "Formato detectado: ${FS_TYPE}"
        echo ""
        echo "  Se recomienda formatear como exFAT (multiplataforma) o APFS (solo Mac)."
        echo "  Para formatear:"
        echo "  1. Abre Utilidad de Discos (Cmd+Espacio, escribe 'Utilidad de Discos')"
        echo "  2. Selecciona el SSD → Borrar"
        echo "  3. Formato: exFAT o APFS | Esquema: Mapa de particiones GUID"
        echo ""
        echo -n "  ¿Continuar con el formato actual? (s/N): "
        read CONTINUE_FORMAT
        if [[ ! "$CONTINUE_FORMAT" =~ ^[sS]$ ]]; then
            print_warn "Cancelado. Formatea el SSD y vuelve a ejecutar el instalador."
            exit 0
        fi
    fi
fi

# ── Paso 6: Verificar Python ────────────────────────────────────────────────
print_step "Verificar Python 3.10+"
PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        PY_VER=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 10 ]]; then
            PYTHON="$cmd"
            print_ok "Python ${PY_VER} encontrado (${cmd})"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    print_error "Python 3.10+ no encontrado."
    echo ""
    echo "  Instala Python desde: https://python.org/downloads/mac-osx/"
    echo "  Al instalar, marca 'Add Python to PATH'"
    echo "  O usa Homebrew: brew install python@3.11"
    exit 1
fi

# ── Paso 7: Verificar Git ───────────────────────────────────────────────────
print_step "Verificar Git"
if command -v git &>/dev/null; then
    GIT_VER=$(git --version | awk '{print $3}')
    print_ok "Git ${GIT_VER}"
else
    print_warn "Git no encontrado. Instalando..."
    xcode-select --install 2>/dev/null || true
    sleep 5
    if ! command -v git &>/dev/null; then
        print_error "No se pudo instalar Git. Instálalo manualmente desde: https://git-scm.com/download/mac"
        exit 1
    fi
fi

# ── Paso 8: Clonar repositorio ──────────────────────────────────────────────
print_step "Clonar ZOE en el SSD"

if [[ -d "$ZOE_HOME/zoe" ]]; then
    print_warn "ZOE ya existe en ${ZOE_HOME}"
    echo -n "  ¿Actualizar (conserva datos) o reinstalar (borra todo)? (a/r/N): "
    read UPDATE_CHOICE
    if [[ "$UPDATE_CHOICE" =~ ^[aA]$ ]]; then
        print_ok "Actualizando ZOE..."
        cd "$ZOE_HOME/zoe"
        git pull origin main 2>/dev/null || print_warn "No se pudo actualizar (ignorado)"
    elif [[ "$UPDATE_CHOICE" =~ ^[rR]$ ]]; then
        echo -n "  ${RED}¿Seguro? Se borrarán todos los datos de ZOE (memoria, identidad, etc.)${NC} (s/N): "
        read CONFIRM
        if [[ "$CONFIRM" =~ ^[sS]$ ]]; then
            rm -rf "$ZOE_HOME"
            mkdir -p "$ZOE_HOME"
        else
            print_ok "Cancelado. Datos preservados."
            exit 0
        fi
    else
        print_ok "Cancelado."
        exit 0
    fi
fi

mkdir -p "$ZOE_HOME"
cd "$ZOE_HOME"

if [[ ! -d "$ZOE_HOME/zoe/.git" ]]; then
    echo "  Clonando desde GitHub..."
    # Usar el token proporcionado por el usuario
    echo -n "  Token de GitHub (ghp_... o pulsa Enter si es público): "
    read GIT_TOKEN
    if [[ -n "$GIT_TOKEN" ]]; then
        git clone "https://${GIT_TOKEN}@github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git" zoe
    else
        git clone "https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git" zoe
    fi
    print_ok "ZOE clonado en ${ZOE_HOME}/zoe"
fi

# ── Paso 9: Crear entorno virtual ───────────────────────────────────────────
print_step "Crear entorno virtual"
cd "$ZOE_HOME/zoe"

if [[ ! -d "$ZOE_HOME/venv" ]]; then
    $PYTHON -m venv "$ZOE_HOME/venv"
    print_ok "Entorno virtual creado"
else
    print_ok "Entorno virtual ya existe"
fi

source "$ZOE_HOME/venv/bin/activate"

# ── Paso 10: Instalar dependencias ──────────────────────────────────────────
print_step "Instalar dependencias (1-2 minutos)"
pip install --upgrade pip -q
pip install -e . -q
print_ok "Dependencias instaladas"

# ── Paso 11: Configurar directorios de datos ────────────────────────────────
print_step "Configurar directorios de datos"
mkdir -p "$ZOE_HOME/data"
mkdir -p "$ZOE_HOME/models"
mkdir -p "$ZOE_HOME/identity"
mkdir -p "$ZOE_HOME/trajectory"
mkdir -p "$ZOE_HOME/capsules"
mkdir -p "$ZOE_HOME/backups"

# Configurar variables de entorno
ENV_FILE="$ZOE_HOME/data/.env"
cat > "$ENV_FILE" << EOF
# ZOE Environment Configuration
ZOE_HOME=$ZOE_HOME
ZOE_DATA=$ZOE_HOME/data
OLLAMA_MODELS=$ZOE_HOME/models
ZOE_STORAGE_TYPE=sqlite
PYTHONPATH=$ZOE_HOME/zoe
EOF
chmod 600 "$ENV_FILE"
print_ok "Directorios creados y .env configurado"

# ── Paso 12: Configurar API keys (opcional) ─────────────────────────────────
print_step "Configurar API keys de LLM cloud (opcional)"
echo ""
echo -e "  Puedes usar ZOE ${BOLD}100% offline${NC} con modelos locales (Ollama)."
echo -e "  O añadir API keys de cloud para nivel máximo de calidad."
echo ""

# OpenAI
echo -n "  ¿Configurar OpenAI API key? (s/N): "
read CONFIG_OPENAI
if [[ "$CONFIG_OPENAI" =~ ^[sS]$ ]]; then
    echo -n "  Pega tu API key (sk-...): "
    read -s OPENAI_KEY
    echo ""
    if [[ -n "$OPENAI_KEY" ]]; then
        echo "OPENAI_API_KEY=$OPENAI_KEY" >> "$ENV_FILE"
        print_ok "OpenAI API key guardada"
    fi
fi

# Anthropic
echo -n "  ¿Configurar Anthropic (Claude) API key? (s/N): "
read CONFIG_ANTHROPIC
if [[ "$CONFIG_ANTHROPIC" =~ ^[sS]$ ]]; then
    echo -n "  Pega tu API key (sk-ant-...): "
    read -s ANTHROPIC_KEY
    echo ""
    if [[ -n "$ANTHROPIC_KEY" ]]; then
        echo "ANTHROPIC_API_KEY=$ANTHROPIC_KEY" >> "$ENV_FILE"
        print_ok "Anthropic API key guardada"
    fi
fi

chmod 600 "$ENV_FILE"

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALACIÓN COMPLETADA
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ ZOE instalada correctamente                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Ubicación:${NC} ${ZOE_HOME}"
echo -e "  ${BOLD}Tipo:${NC} $([[ "$INSTALL_TYPE" == "ssd_crucial" ]] && echo "SSD Crucial X9" || echo "Disco interno Mac")"
echo ""
echo -e "  ${BOLD}Scripts de lanzador creados en:${NC} ${ZOE_HOME}/"
echo ""

# Crear scripts de lanzador finales
print_step "Crear scripts de lanzador"

# Lanzador principal: ZOE-Smart.command (elige el mejor backend disponible)
cat > "$ZOE_HOME/ZOE-Smart.command" << 'LAUNCHER_EOF'
#!/bin/bash
# ZOE Smart Launcher — Elige automáticamente el mejor backend
ZOE_HOME="$(cd "$(dirname "$0")" && pwd)"
cd "$ZOE_HOME/zoe"
source "$ZOE_HOME/venv/bin/activate"

# Cargar variables de entorno
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Smart Launcher (v2.0.0-rc1)                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Detectar qué backends están disponibles
BACKENDS=""

# 1. Verificar Ollama (modelos locales)
if command -v ollama &>/dev/null; then
    OLLAMA_MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
    if [[ "$OLLAMA_MODELS" -gt 0 ]]; then
        BACKENDS="${BACKENDS}ollama "
        echo "  ✓ Ollama: ${OLLAMA_MODELS} modelos locales disponibles"
    fi
fi

# 2. Verificar OpenAI
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    BACKENDS="${BACKENDS}openai "
    echo "  ✓ OpenAI API key configurada"
fi

# 3. Verificar Anthropic
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    BACKENDS="${BACKENDS}anthropic "
    echo "  ✓ Anthropic API key configurada"
fi

# 4. Mock (siempre disponible)
echo "  ✓ Mock (offline, sin LLM)"

# Menú de selección
echo ""
echo "  Selecciona modo de inicio:"
echo ""
echo "  [1] SMART — ZOE elige automáticamente el mejor modelo para cada pregunta"
echo "  [2] CHAT CLI — Terminal interactiva (texto)"
echo "  [3] DASHBOARD — Interfaz web (navegador)"
echo "  [4] OLLAMA — Solo modelos locales (100% offline)"
echo "  [5] OPENAI — Máxima calidad vía API cloud"
echo "  [6] ANTHROPIC — Claude vía API cloud"
echo "  [7] MOCK — Sin LLM, modo demo"
echo ""
echo -n "  Elige [1-7]: "
read MODE

case "$MODE" in
    1)
        echo ""
        echo -e "${CYAN}  ┌─────────────────────────────────────────────────────┐${NC}"
        echo -e "${CYAN}  │  ZOE SMART MODE v2.1.1                              │${NC}"
        echo -e "${CYAN}  │  ZOE elige automáticamente el mejor modelo          │${NC}"
        echo -e "${CYAN}  │  para cada pregunta usando ACD + DepthClassifier    │${NC}"
        echo -e "${CYAN}  └─────────────────────────────────────────────────────┘${NC}"
        echo ""
        # SMART: Detectar el mejor backend disponible automáticamente
        SMART_BACKEND="mock"
        SMART_MODEL=""
        if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
            SMART_BACKEND="ollama"
            SMART_MODEL="auto"
            echo -e "  ${GREEN}✓ Ollama detectado con modelos — ACD Router ACTIVO${NC}"
            echo -e "  ${GREEN}  ZOE clasificará cada pregunta (L0-L3) y elegirá:${NC}"
            echo -e "    L0 (hola/gracias)        → PatternSpeaker (<1ms)"
            echo -e "    L1 (preguntas simples)   → Gemma 2 9B (1-2s)"
            echo -e "    L2 (resúmenes)           → Agents-A1 MoE (3-5s)"
            echo -e "    L3 (análisis profundo)   → QwQ-32B (5-10s)"
            echo ""
        elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
            SMART_BACKEND="openai_compatible"
            SMART_MODEL="gpt-4o"
            echo -e "  ${GREEN}✓ OpenAI API key configurada — usando GPT-4o${NC}"
        elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
            SMART_BACKEND="anthropic"
            SMART_MODEL="claude-sonnet-4-20250514"
            echo -e "  ${GREEN}✓ Anthropic API key configurada — usando Claude${NC}"
        else
            echo -e "  ${YELLOW}⚠ Sin modelos locales ni APIs configuradas${NC}"
            echo -e "  ${YELLOW}  Usando PatternSpeaker (respuestas offline básicas)${NC}"
            echo ""
            echo -e "  ${CYAN}Para más calidad:${NC}"
            echo -e "  1. Instala Ollama: https://ollama.com/download"
            echo -e "  2. Descarga modelos: Opción [3] del menú post-instalación"
            echo -e "  3. O configura API: OPENAI_API_KEY=sk-..."
            echo ""
        fi
        echo -e "  ${CYAN}ZOE Chat CLI iniciando... Escribe '/quit' para salir.${NC}"
        echo ""
        python -m zoe.cli_chat --backend "$SMART_BACKEND" ${SMART_MODEL:+--model "$SMART_MODEL"} --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    2)
        echo ""
        echo -n "  Backend [mock/ollama/openai/anthropic]: "
        read BACKEND
        echo -n "  Modelo [auto/qwen2.5:3b/gpt-4o/claude-sonnet]: "
        read MODEL
        [[ "$MODEL" == "auto" ]] && MODEL=""
        echo -e "  ${CYAN}ZOE Chat CLI iniciando... Escribe '/quit' para salir.${NC}"
        echo ""
        python -m zoe.cli_chat --backend "${BACKEND:-mock}" --model "$MODEL" --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    3)
        echo ""
        echo -e "${CYAN}  ┌─────────────────────────────────────────────────────┐${NC}"
        echo -e "${CYAN}  │  ZOE DASHBOARD v2.1.1                               │${NC}"
        echo -e "${CYAN}  │  Interfaz web completa con chat, memoria,           │${NC}"
        echo -e "${CYAN}  │  cápsulas, configuración y más                      │${NC}"
        echo -e "${CYAN}  └─────────────────────────────────────────────────────┘${NC}"
        echo ""
        DASH_BACKEND="ollama"
        DASH_MODEL="auto"
        if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
            echo -e "  ${GREEN}✓ Ollama detectado — Dashboard con ACD Router activo${NC}"
        elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
            DASH_BACKEND="openai_compatible"
            DASH_MODEL="gpt-4o"
            echo -e "  ${GREEN}✓ OpenAI configurado — Dashboard con GPT-4o${NC}"
        else
            DASH_BACKEND="mock"
            DASH_MODEL=""
            echo -e "  ${YELLOW}⚠ Sin modelos — Dashboard en modo demo${NC}"
        fi
        echo ""
        echo -e "  ${CYAN}Abriendo navegador en http://localhost:8642 ...${NC}"
        sleep 2
        open "http://localhost:8642" 2>/dev/null || echo "  Abre manualmente: http://localhost:8642"
        echo ""
        python -m zoe.web_dashboard --backend "$DASH_BACKEND" ${DASH_MODEL:+--model "$DASH_MODEL"}
        ;;
    4)
        echo ""
        echo "  Iniciando con modelos locales (Ollama)..."
        python -m zoe.cli_chat --backend ollama --model qwen2.5:3b --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    5)
        echo ""
        echo "  Iniciando con OpenAI GPT-4o..."
        python -m zoe.cli_chat --backend openai_compatible --model gpt-4o --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    6)
        echo ""
        echo "  Iniciando con Anthropic Claude..."
        python -m zoe.cli_chat --backend anthropic --model claude-sonnet-4-20250514 --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    7|*)
        echo ""
        echo "  Iniciando en modo demo (sin LLM)..."
        python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
esac
LAUNCHER_EOF
chmod +x "$ZOE_HOME/ZOE-Smart.command"

# Lanzador rápido: doble click
cat > "$ZOE_HOME/INICIAR-ZOE.command" << 'EOF'
#!/bin/bash
# INICIAR ZOE — Doble click para empezar
ZOE_HOME="$(cd "$(dirname "$0")" && pwd)"
open -a Terminal "$ZOE_HOME/ZOE-Smart.command"
EOF
chmod +x "$ZOE_HOME/INICIAR-ZOE.command"

print_ok "Scripts de lanzador creados"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${BOLD}Próximos pasos:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  1. ${BOLD}Instalar Ollama${NC} (para modelos locales):"
echo -e "     https://ollama.com → Download → Install"
echo ""
echo -e "  2. ${BOLD}Iniciar ZOE:${NC}"
echo -e "     Abre Finder → ${ZOE_HOME}"
echo -e "     Doble click en: ${BOLD}INICIAR-ZOE.command${NC}"
echo ""
echo -e "  3. ${BOLD}Abrir Dashboard:${NC}"
echo -e "     http://localhost:8642 (después de iniciar ZOE)"
echo ""

if [[ "$INSTALL_TYPE" == "ssd_crucial" ]]; then
    echo -e "  ${CYAN}💡 El SSD Crucial X9 es portátil:${NC}"
    echo -e "     • Desconéctalo y llévalo a cualquier Mac/PC/Linux"
    echo -e "     • ZOE sigue siendo la misma, con tu memoria e identidad"
    echo -e "     • Doble click en INICIAR-ZOE.command en cualquier máquina"
    echo ""
fi

echo -e "  ${BOLD}Documentación:${NC}"
echo -e "     • Guía de usuario: ${ZOE_HOME}/zoe/zoe/docs/20_ZOE_GUIA_USUARIO.md"
echo -e "     • Explicación: ${ZOE_HOME}/zoe/zoe/docs/18_ZOE_EXPLICACION_NO_TECNICOS.md"
echo -e "     • Dashboard: http://localhost:8642"
echo ""
echo -e "${GREEN}  ¡ZOE está lista para despertar! 🧠${NC}"
echo ""
