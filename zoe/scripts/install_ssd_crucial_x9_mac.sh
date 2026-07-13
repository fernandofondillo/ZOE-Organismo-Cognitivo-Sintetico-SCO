#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# ZOE — Instalador para SSD Crucial X9 1TB + MacBook Air M3
# Synthetic Cognitive Organism (SCO) v2.1.1
# ═══════════════════════════════════════════════════════════════════════════════
# Uso: bash install_ssd_crucial_x9_mac.sh
# Requisitos: MacBook Air M3 8GB+, SSD Crucial X9 1TB, Python 3.10+, Git
# Mejoras v2.1.1: Auto-dependencias, descarga modelos, dashboard, post-install
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; MAGENTA='\033[0;35m'; NC='\033[0m'

# ── Banner ───────────────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "  ███████╗ ██████╗ ███████╗"
echo "  ╚══███╔╝██╔═══██╗██╔════╝"
echo "    ███╔╝ ██║   ██║█████╗  "
echo "   ███╔╝  ██║   ██║██╔══╝  "
echo "  ███████╗╚██████╔╝███████╗"
echo "  ╚══════╝ ╚═════╝ ╚══════╝"
echo -e "${NC}"
echo -e "${BOLD}  Synthetic Cognitive Organism (SCO) v2.1.1${NC}"
echo -e "  Instalador para ${BOLD}SSD Crucial X9 1TB${NC} + ${BOLD}MacBook Air M3${NC}"
echo ""
echo -e "  ${MAGENTA}Nuevo en v2.1.1:${NC} Auto-instalación de dependencias, descarga de modelos,"
echo -e "  lanzador de dashboard, y menú de post-instalación."
echo ""
echo -e "  Tiempo estimado: 15-30 minutos (sin modelos) / 1-3 horas (con modelos)"
echo ""

# ── Funciones auxiliares ─────────────────────────────────────────────────────
step=0
total_steps=15

print_step() {
    step=$((step + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Paso ${step}/${total_steps}: ${1}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_substep() {
    echo -e "${CYAN}    → ${1}${NC}"
}

print_ok() { echo -e "${GREEN}  ✓ ${1}${NC}"; }
print_warn() { echo -e "${YELLOW}  ⚠ ${1}${NC}"; }
print_error() { echo -e "${RED}  ✗ ${1}${NC}"; }
print_info() { echo -e "${BLUE}  ℹ ${1}${NC}"; }

# Barra de progreso visual
show_progress() {
    local current=$1
    local total=$2
    local width=40
    local pct=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    printf "\r${CYAN}  ["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%${NC}" "$pct"
}

# Verificar espacio disponible en disco (en GB)
get_free_space_gb() {
    local path="$1"
    local dir="$path"
    while [[ ! -d "$dir" ]]; do
        dir="$(dirname "$dir")"
    done
    df -g "$dir" 2>/dev/null | awk 'NR==2 {print $4}' || echo "0"
}

# Pregunta Sí/No con valor por defecto
ask_yes_no() {
    local prompt="$1"
    local default="${2:-N}"
    echo -n "  ${prompt} (s/N): "
    read RESPONSE
    [[ "$RESPONSE" =~ ^[sS]$ ]]
}

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

# ═══════════════════════════════════════════════════════════════════════════════
# NUEVO EN v2.1.1: DETECCIÓN E INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS
# ═══════════════════════════════════════════════════════════════════════════════

print_step "Detectar e instalar dependencias del sistema"

# ── 3.1: Homebrew ───────────────────────────────────────────────────────────
print_substep "Verificando Homebrew..."
if command -v brew &>/dev/null; then
    BREW_VER=$(brew --version | head -1)
    print_ok "Homebrew encontrado: ${BREW_VER}"
else
    print_warn "Homebrew no encontrado. Es necesario para instalar Python y otras dependencias."
    if ask_yes_no "¿Instalar Homebrew ahora?"; then
        print_info "Instalando Homebrew... (puede tardar varios minutos)"
        print_info "Se abrirá una ventana de instalación. Sigue las instrucciones."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
            print_error "No se pudo instalar Homebrew automáticamente."
            echo ""
            echo "  Instrucciones manuales:"
            echo "  1. Abre Terminal"
            echo "  2. Ejecuta: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  3. Vuelve a ejecutar este instalador"
            exit 1
        }
        # Añadir brew al PATH para Apple Silicon
        if [[ "$ARCH" == "arm64" && -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        print_ok "Homebrew instalado correctamente"
    else
        print_warn "Homebrew es necesario. Algunas funciones no estarán disponibles."
    fi
fi

# ── 3.2: Python 3.10+ ───────────────────────────────────────────────────────
print_substep "Verificando Python 3.10+..."
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
    print_warn "Python 3.10+ no encontrado."
    if command -v brew &>/dev/null; then
        if ask_yes_no "¿Instalar Python 3.11 vía Homebrew?"; then
            print_info "Instalando Python 3.11... (puede tardar 2-5 minutos)"
            brew install python@3.11
            if [[ "$ARCH" == "arm64" ]]; then
                eval "$(/opt/homebrew/bin/brew shellenv)"
            fi
            PYTHON="python3.11"
            print_ok "Python 3.11 instalado"
        else
            print_error "Python 3.10+ es requerido. Instálalo manualmente:"
            echo "  brew install python@3.11"
            exit 1
        fi
    else
        print_error "Python 3.10+ no encontrado y Homebrew no está disponible."
        echo "  Opciones:"
        echo "  1. Instala Homebrew primero"
        echo "  2. O descarga Python desde: https://python.org/downloads/mac-osx/"
        exit 1
    fi
fi

# ── 3.3: pip ────────────────────────────────────────────────────────────────
print_substep "Verificando pip..."
if $PYTHON -m pip --version &>/dev/null 2>&1 || $PYTHON -m ensurepip --version &>/dev/null 2>&1; then
    PIP_VER=$($PYTHON -m pip --version 2>/dev/null | awk '{print $2}' || echo "desconocida")
    print_ok "pip encontrado (versión ${PIP_VER})"
else
    print_warn "pip no encontrado. Instalando..."
    $PYTHON -m ensurepip --upgrade 2>/dev/null || {
        print_info "Descargando get-pip.py..."
        curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
        $PYTHON /tmp/get-pip.py --user
        rm -f /tmp/get-pip.py
    }
    print_ok "pip instalado"
fi

# ── 3.4: Git ────────────────────────────────────────────────────────────────
print_substep "Verificando Git..."
if command -v git &>/dev/null; then
    GIT_VER=$(git --version | awk '{print $3}')
    print_ok "Git ${GIT_VER}"
else
    print_warn "Git no encontrado. Es necesario para clonar ZOE."
    print_info "Se ejecutará 'xcode-select --install' para instalar las herramientas de desarrollo de Apple."
    print_info "Esto abrirá una ventana de diálogo. Sigue las instrucciones."
    echo ""
    echo -n "  Pulsa Enter para continuar..."
    read
    xcode-select --install 2>/dev/null || true
    print_info "Esperando instalación de Git... (puedes tardar 5-10 minutos)"
    print_info "El instalador continuará automáticamente cuando Git esté disponible."

    # Esperar hasta 5 minutos a que Git se instale
    GIT_WAIT=0
    while ! command -v git &>/dev/null && [[ $GIT_WAIT -lt 30 ]]; do
        sleep 10
        GIT_WAIT=$((GIT_WAIT + 1))
        printf "."
    done
    echo ""

    if command -v git &>/dev/null; then
        GIT_VER=$(git --version | awk '{print $3}')
        print_ok "Git ${GIT_VER} instalado correctamente"
    else
        print_error "Git no se instaló automáticamente."
        echo ""
        echo "  Instrucciones manuales:"
        echo "  1. Abre Terminal"
        echo "  2. Ejecuta: xcode-select --install"
        echo "  3. Completa la instalación (5-10 minutos)"
        echo "  4. Vuelve a ejecutar este instalador"
        echo ""
        echo "  Alternativa: descarga Git desde https://git-scm.com/download/mac"
        exit 1
    fi
fi

# ── 3.5: Ollama ─────────────────────────────────────────────────────────────
print_substep "Verificando Ollama..."
OLLAMA_INSTALLED=false
if command -v ollama &>/dev/null; then
    OLLAMA_VER=$(ollama --version 2>/dev/null | awk '{print $3}' || echo "instalado")
    print_ok "Ollama ${OLLAMA_VER} encontrado"
    OLLAMA_INSTALLED=true
else
    print_warn "Ollama no encontrado. Es necesario para ejecutar modelos locales."
    echo ""
    echo -e "  ${BOLD}Ollama${NC} permite ejecutar modelos de IA directamente en tu Mac,"
    echo -e "  sin depender de internet ni APIs de cloud."
    echo ""
    if ask_yes_no "¿Descargar e instalar Ollama ahora? (~200MB)"; then
        print_info "Descargando Ollama... (~200MB, puede tardar unos minutos)"
        OLLAMA_ZIP="/tmp/Ollama-darwin.zip"
        OLLAMA_APP="/Applications/Ollama.app"

        # Descargar con progreso
        if command -v curl &>/dev/null; then
            curl -L --progress-bar "https://ollama.com/download/Ollama-darwin.zip" -o "$OLLAMA_ZIP"
        else
            print_error "curl no está disponible. No se puede descargar Ollama."
            echo "  Descarga manual: https://ollama.com/download"
            OLLAMA_INSTALLED=false
        fi

        if [[ -f "$OLLAMA_ZIP" ]]; then
            print_info "Extrayendo Ollama..."
            unzip -q -o "$OLLAMA_ZIP" -d /tmp/
            print_info "Moviendo Ollama a /Applications..."
            if [[ -d "/tmp/Ollama.app" ]]; then
                mv -f "/tmp/Ollama.app" "$OLLAMA_APP"
            elif [[ -d "/tmp/Ollama/Ollama.app" ]]; then
                mv -f "/tmp/Ollama/Ollama.app" "$OLLAMA_APP"
            fi
            rm -f "$OLLAMA_ZIP"
            rm -rf /tmp/Ollama 2>/dev/null || true

            print_info "Iniciando Ollama por primera vez..."
            open -a Ollama
            print_ok "Ollama instalado y en ejecución"
            OLLAMA_INSTALLED=true
            print_info "Esperando 5 segundos a que Ollama inicialice..."
            sleep 5
        fi
    else
        print_warn "Ollama no se instalará. Los modelos locales no estarán disponibles."
        print_info "Puedes instalarlo más tarde desde: https://ollama.com/download"
        OLLAMA_INSTALLED=false
    fi
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

# ── Paso 6: Clonar repositorio ──────────────────────────────────────────────
print_step "Clonar ZOE en el destino"

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

# ── Paso 7: Crear entorno virtual ───────────────────────────────────────────
print_step "Crear entorno virtual"
cd "$ZOE_HOME/zoe"

if [[ ! -d "$ZOE_HOME/venv" ]]; then
    $PYTHON -m venv "$ZOE_HOME/venv"
    print_ok "Entorno virtual creado"
else
    print_ok "Entorno virtual ya existe"
fi

source "$ZOE_HOME/venv/bin/activate"

# ── Paso 8: Instalar dependencias ──────────────────────────────────────────
print_step "Instalar dependencias de Python (1-2 minutos)"
pip install --upgrade pip -q
pip install -e . -q
print_ok "Dependencias instaladas"

# ── Paso 9: Configurar directorios de datos ─────────────────────────────────
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

# ── Paso 10: Configurar API keys (opcional) ────────────────────────────────
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
# NUEVO EN v2.1.1: CREAR LANZADOR DEL DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

print_step "Crear lanzadores"

# Lanzador del Dashboard
print_substep "Creando INICIAR-DASHBOARD.command..."
cat > "$ZOE_HOME/INICIAR-DASHBOARD.command" << 'DASHBOARD_EOF'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# ZOE Dashboard Launcher v2.1.1
# Inicia el Dashboard web de ZOE y abre el navegador automáticamente
# ═══════════════════════════════════════════════════════════════════════════════
ZOE_HOME="$(cd "$(dirname "$0")" && pwd)"
cd "$ZOE_HOME/zoe"
source "$ZOE_HOME/venv/bin/activate"

# Cargar variables de entorno
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Dashboard Launcher v2.1.1                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Detectar backend preferido
BACKEND="mock"
if command -v ollama &>/dev/null; then
    MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
    if [[ "$MODEL_COUNT" -gt 0 ]]; then
        BACKEND="ollama"
        echo "  ✓ Usando Ollama con ${MODEL_COUNT} modelos locales"
    else
        echo "  ⚠ Ollama instalado pero sin modelos. Usando mock."
        echo "    Descarga modelos desde el menú de post-instalación."
    fi
fi

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    echo "  ✓ OpenAI API key configurada (fallback disponible)"
fi

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "  ✓ Anthropic API key configurada (fallback disponible)"
fi

echo ""
echo "  → Iniciando Dashboard en http://localhost:8642 ..."
echo "  → Backend: ${BACKEND}"
echo ""
echo "  Para detener: pulsa Ctrl+C en esta ventana"
echo ""

# Abrir navegador después de dar tiempo a que el servidor arranque
(sleep 4 && open "http://localhost:8642") &

python -m zoe.web_dashboard --backend "$BACKEND"
DASHBOARD_EOF
chmod +x "$ZOE_HOME/INICIAR-DASHBOARD.command"
print_ok "INICIAR-DASHBOARD.command creado"

# Lanzador principal: ZOE-Smart.command (elige el mejor backend disponible)
print_substep "Creando ZOE-Smart.command..."
cat > "$ZOE_HOME/ZOE-Smart.command" << 'LAUNCHER_EOF'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# ZOE Smart Launcher v2.1.1 — Elige automáticamente el mejor backend
# ═══════════════════════════════════════════════════════════════════════════════
ZOE_HOME="$(cd "$(dirname "$0")" && pwd)"
cd "$ZOE_HOME/zoe"
source "$ZOE_HOME/venv/bin/activate"

# Cargar variables de entorno
if [ -f "$ZOE_HOME/data/.env" ]; then
    export $(grep -v '^#' "$ZOE_HOME/data/.env" | xargs)
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Smart Launcher (v2.1.1)                             ║"
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
        echo "  Iniciando ZOE en modo SMART..."
        echo "  ZOE detectará automáticamente la complejidad de cada pregunta"
        echo "  y elegirá el modelo óptimo (local o cloud)."
        echo ""
        python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    2)
        echo ""
        echo -n "  Backend [mock/ollama/openai/anthropic]: "
        read BACKEND
        echo -n "  Modelo [auto/qwen2.5:3b/gpt-4o/claude-sonnet]: "
        read MODEL
        [[ "$MODEL" == "auto" ]] && MODEL=""
        python -m zoe.cli_chat --backend "${BACKEND:-mock}" --model "$MODEL" --db-path "$ZOE_HOME/data/zoe_memory.db"
        ;;
    3)
        echo ""
        echo -n "  Backend [mock/ollama/openai/anthropic]: "
        read BACKEND
        echo ""
        echo "  Abre tu navegador en: http://localhost:8642"
        echo ""
        python -m zoe.web_dashboard --backend "${BACKEND:-mock}"
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
print_ok "ZOE-Smart.command creado"

# Lanzador rápido: doble click
print_substep "Creando INICIAR-ZOE.command..."
cat > "$ZOE_HOME/INICIAR-ZOE.command" << 'EOF'
#!/bin/bash
# INICIAR ZOE — Doble click para empezar
ZOE_HOME="$(cd "$(dirname "$0")" && pwd)"
open -a Terminal "$ZOE_HOME/ZOE-Smart.command"
EOF
chmod +x "$ZOE_HOME/INICIAR-ZOE.command"
print_ok "INICIAR-ZOE.command creado"

# ── Paso 11: Mostrar resumen de instalación ──────────────────────────────────
print_step "Instalación completada"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ ZOE v2.1.1 instalada correctamente                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Ubicación:${NC} ${ZOE_HOME}"
echo -e "  ${BOLD}Tipo:${NC} $([[ "$INSTALL_TYPE" == "ssd_crucial" ]] && echo "SSD Crucial X9" || echo "Disco interno Mac")"
echo -e "  ${BOLD}Python:${NC} $($PYTHON --version 2>&1)"
echo -e "  ${BOLD}Ollama:${NC} $([[ "$OLLAMA_INSTALLED" == true ]] && echo "Instalado ✓" || echo "No instalado")"
echo ""
echo -e "  ${BOLD}Lanzadores creados en:${NC} ${ZOE_HOME}/"
echo -e "    • ${BOLD}INICIAR-ZOE.command${NC}       — Menú interactivo completo"
echo -e "    • ${BOLD}INICIAR-DASHBOARD.command${NC} — Dashboard web directo"
echo -e "    • ${BOLD}ZOE-Smart.command${NC}         — Lanzador avanzado con opciones"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# NUEVO EN v2.1.1: DESCARGA DE MODELOS LLM LOCALES
# ═══════════════════════════════════════════════════════════════════════════════

if [[ "$OLLAMA_INSTALLED" == true ]]; then
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BOLD}Modelos de IA Locales${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  Los modelos locales permiten usar ZOE ${BOLD}100% offline${NC}, sin"
    echo -e "  depender de APIs de cloud ni conexión a internet."
    echo ""

    if ask_yes_no "¿Quieres descargar modelos de IA locales ahora?"; then
        echo ""
        echo -e "  ${BOLD}Selecciona modelos a descargar (puedes elegir varios):${NC}"
        echo ""
        echo -e "  ${CYAN}[1]${NC} Gemma 2 9B (IQ2_M)      — ${BOLD}3.5 GB${NC}  — Rápido, bueno para preguntas simples"
        echo -e "  ${CYAN}[2]${NC} Qwen 2.5 32B (IQ2_M)    — ${BOLD}12.5 GB${NC} — Equilibrado calidad/velocidad"
        echo -e "  ${CYAN}[3]${NC} QwQ-32B (IQ2_M)         — ${BOLD}12.5 GB${NC} — Razonamiento profundo"
        echo -e "  ${CYAN}[4]${NC} DeepSeek-R1 32B (Q4_K_M) — ${BOLD}18 GB${NC}  — Reflexión autónoma v2.1"
        echo -e "  ${CYAN}[5]${NC} DeepSeek-R1 32B (IQ2_M) — ${BOLD}12.5 GB${NC} — Reflexión (versión ligera)"
        echo -e "  ${CYAN}[6]${NC} Qwen 2.5 72B (IQ2_M)    — ${BOLD}25 GB${NC}  — Máxima calidad"
        echo -e "  ${CYAN}[7]${NC} ${BOLD}TODOS${NC} los anteriores     — ${BOLD}~85 GB${NC}  — Instala todo el catálogo"
        echo -e "  ${CYAN}[8]${NC} Ninguno (usaré APIs de cloud)"
        echo ""

        # Definir modelos
        declare -A MODEL_TAGS
        declare -A MODEL_NAMES
        declare -A MODEL_SIZES
        MODEL_TAGS[1]="gemma2:9b"
        MODEL_NAMES[1]="Gemma 2 9B"
        MODEL_SIZES[1]=4
        MODEL_TAGS[2]="qwen2.5:32b"
        MODEL_NAMES[2]="Qwen 2.5 32B"
        MODEL_SIZES[2]=13
        MODEL_TAGS[3]="qwq:32b"
        MODEL_NAMES[3]="QwQ-32B"
        MODEL_SIZES[3]=13
        MODEL_TAGS[4]="deepseek-r1:32b"
        MODEL_NAMES[4]="DeepSeek-R1 32B Q4"
        MODEL_SIZES[4]=19
        MODEL_TAGS[5]="deepseek-r1:32b-iq2_m"
        MODEL_NAMES[5]="DeepSeek-R1 32B IQ2"
        MODEL_SIZES[5]=13
        MODEL_TAGS[6]="qwen2.5:72b"
        MODEL_NAMES[6]="Qwen 2.5 72B"
        MODEL_SIZES[6]=26

        echo -n "  Elige una opción [1-8]: "
        read MODEL_CHOICE

        # Determinar qué modelos descargar
        SELECTED_MODELS=()
        TOTAL_SIZE=0
        case "$MODEL_CHOICE" in
            1|2|3|4|5|6)
                SELECTED_MODELS+=("$MODEL_CHOICE")
                TOTAL_SIZE=${MODEL_SIZES[$MODEL_CHOICE]}
                ;;
            7)
                for i in 1 2 3 4 5 6; do
                    SELECTED_MODELS+=("$i")
                    TOTAL_SIZE=$((TOTAL_SIZE + MODEL_SIZES[$i]))
                done
                ;;
            *)
                print_info "No se descargarán modelos locales. Puedes usarlos más tarde."
                SELECTED_MODELS=()
                ;;
        esac

        # Verificar espacio disponible y descargar
        if [[ ${#SELECTED_MODELS[@]} -gt 0 ]]; then
            FREE_GB=$(get_free_space_gb "$ZOE_HOME")
            print_info "Espacio disponible en destino: ${FREE_GB}GB"
            print_info "Espacio requerido: ~${TOTAL_SIZE}GB"

            if [[ "$FREE_GB" -lt "$TOTAL_SIZE" ]]; then
                print_error "Espacio insuficiente. Tienes ${FREE_GB}GB libres y se necesitan ~${TOTAL_SIZE}GB."
                echo "  Libera espacio en el SSD o elige menos modelos."
            else
                echo ""
                for idx in "${SELECTED_MODELS[@]}"; do
                    TAG="${MODEL_TAGS[$idx]}"
                    NAME="${MODEL_NAMES[$idx]}"
                    SIZE="${MODEL_SIZES[$idx]}"

                    echo ""
                    echo -e "  ${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo -e "  Descargando: ${BOLD}${NAME}${NC} (${SIZE}GB)"
                    echo -e "  ${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

                    # Usar ollama pull para descargar
                    if command -v ollama &>/dev/null; then
                        print_info "Ejecutando: ollama pull ${TAG}"
                        ollama pull "$TAG" 2>&1 | while IFS= read -r line; do
                            printf "  %s\n" "$line"
                        done

                        if [[ $? -eq 0 ]]; then
                            print_ok "${NAME} descargado correctamente"
                        else
                            print_error "Error descargando ${NAME}. Intentando método alternativo..."
                            # Fallback: usar el downloader de ZOE si existe
                            if [[ -f "$ZOE_HOME/zoe/zoe/core/model_downloader.py" ]]; then
                                print_info "Intentando con model_downloader..."
                                cd "$ZOE_HOME/zoe"
                                python -m zoe.core.model_downloader --model "$TAG" --output "$ZOE_HOME/models/" 2>/dev/null || {
                                    print_error "No se pudo descargar ${NAME}. Salta al siguiente."
                                }
                            fi
                        fi
                    else
                        print_error "Ollama no está disponible. No se pueden descargar modelos."
                        break
                    fi
                done

                # Resumen de modelos instalados
                echo ""
                echo -e "${GREEN}  ✓ Descarga de modelos completada${NC}"
                if command -v ollama &>/dev/null; then
                    INSTALLED_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
                    echo -e "  ${BOLD}Modelos instalados:${NC} ${INSTALLED_COUNT}"
                    ollama list 2>/dev/null | tail -n +2 | while IFS= read -r line; do
                        echo -e "    • $line"
                    done
                fi
            fi
        fi
    else
        print_info "Saltando descarga de modelos. Puedes hacerlo más tarde con 'ollama pull <modelo>'"
    fi
else
    echo ""
    print_warn "Ollama no está instalado. Los modelos locales no están disponibles."
    print_info "Para usar modelos locales, instala Ollama desde: https://ollama.com/download"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# NUEVO EN v2.1.1: MENÚ DE POST-INSTALACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ZOE v2.1.1 instalada correctamente                      ║${NC}"
echo -e "${GREEN}║  en ${ZOE_HOME}                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Función para mostrar menú de post-instalación
show_post_install_menu() {
    echo -e "  ${BOLD}¿Qué quieres hacer ahora?${NC}"
    echo ""
    echo -e "  ${CYAN}[1]${NC} ${BOLD}Iniciar Chat${NC} (terminal)         — Interfaz de texto interactiva"
    echo -e "  ${CYAN}[2]${NC} ${BOLD}Iniciar Dashboard${NC} (navegador)   — Interfaz web en http://localhost:8642"
    echo -e "  ${CYAN}[3]${NC} ${BOLD}Descargar más modelos${NC}           — Añadir más modelos locales"
    echo -e "  ${CYAN}[4]${NC} ${BOLD}Configurar API keys${NC}             — OpenAI / Claude para máxima calidad"
    echo -e "  ${CYAN}[5]${NC} ${BOLD}Ver guía de usuario${NC}             — Documentación completa"
    echo -e "  ${CYAN}[6]${NC} ${BOLD}Salir${NC}                           — Cerrar instalador"
    echo ""
}

# Bucle del menú de post-instalación
while true; do
    show_post_install_menu
    echo -n "  Elige una opción [1-6]: "
    read POST_CHOICE

    case "$POST_CHOICE" in
        1)
            echo ""
            print_info "Iniciando Chat CLI..."
            cd "$ZOE_HOME/zoe"
            source "$ZOE_HOME/venv/bin/activate"
            if [[ "$OLLAMA_INSTALLED" == true ]]; then
                INSTALLED_MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
                if [[ "$INSTALLED_MODELS" -gt 0 ]]; then
                    print_info "Usando Ollama con modelos locales"
                    python -m zoe.cli_chat --backend ollama --db-path "$ZOE_HOME/data/zoe_memory.db"
                else
                    print_warn "No hay modelos locales. Iniciando en modo demo."
                    print_info "Descarga modelos desde el menú [3]"
                    python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
                fi
            else
                python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
            fi
            echo ""
            echo -n "  Pulsa Enter para volver al menú..."
            read
            ;;

        2)
            echo ""
            print_info "Iniciando Dashboard..."
            print_info "Se abrirá una nueva ventana de Terminal con el Dashboard"
            print_info "El navegador se abrirá automáticamente en http://localhost:8642"
            open -a Terminal "$ZOE_HOME/INICIAR-DASHBOARD.command"
            echo ""
            echo -n "  Pulsa Enter para volver al menú..."
            read
            ;;

        3)
            echo ""
            if [[ "$OLLAMA_INSTALLED" == false ]]; then
                print_error "Ollama no está instalado. Instálalo primero:"
                echo "  https://ollama.com/download"
            else
                print_info "Modelos disponibles para descargar:"
                echo ""
                echo -e "  ${CYAN}[1]${NC} Gemma 2 9B (IQ2_M)      — 3.5GB"
                echo -e "  ${CYAN}[2]${NC} Qwen 2.5 32B (IQ2_M)    — 12.5GB"
                echo -e "  ${CYAN}[3]${NC} QwQ-32B (IQ2_M)         — 12.5GB"
                echo -e "  ${CYAN}[4]${NC} DeepSeek-R1 32B (Q4_K_M) — 18GB"
                echo -e "  ${CYAN}[5]${NC} DeepSeek-R1 32B (IQ2_M) — 12.5GB"
                echo -e "  ${CYAN}[6]${NC} Qwen 2.5 72B (IQ2_M)    — 25GB"
                echo ""
                echo -n "  Elige modelo [1-6]: "
                read EXTRA_MODEL
                case "$EXTRA_MODEL" in
                    1) ollama pull gemma2:9b ;;
                    2) ollama pull qwen2.5:32b ;;
                    3) ollama pull qwq:32b ;;
                    4) ollama pull deepseek-r1:32b ;;
                    5) ollama pull deepseek-r1:32b-iq2_m ;;
                    6) ollama pull qwen2.5:72b ;;
                    *) print_warn "Opción no válida" ;;
                esac
            fi
            echo ""
            echo -n "  Pulsa Enter para volver al menú..."
            read
            ;;

        4)
            echo ""
            print_info "Configurar API keys de LLM cloud"
            echo ""
            ENV_FILE="$ZOE_HOME/data/.env"

            echo -n "  ¿Configurar OpenAI API key? (s/N): "
            read CFG_OAI
            if [[ "$CFG_OAI" =~ ^[sS]$ ]]; then
                echo -n "  Pega tu API key (sk-...): "
                read -s KEY_OAI
                echo ""
                if [[ -n "$KEY_OAI" ]]; then
                    # Eliminar key anterior si existe
                    grep -v "^OPENAI_API_KEY=" "$ENV_FILE" > /tmp/.env.tmp 2>/dev/null || cp "$ENV_FILE" /tmp/.env.tmp
                    echo "OPENAI_API_KEY=$KEY_OAI" >> /tmp/.env.tmp
                    mv /tmp/.env.tmp "$ENV_FILE"
                    chmod 600 "$ENV_FILE"
                    print_ok "OpenAI API key guardada"
                fi
            fi

            echo -n "  ¿Configurar Anthropic (Claude) API key? (s/N): "
            read CFG_ANT
            if [[ "$CFG_ANT" =~ ^[sS]$ ]]; then
                echo -n "  Pega tu API key (sk-ant-...): "
                read -s KEY_ANT
                echo ""
                if [[ -n "$KEY_ANT" ]]; then
                    grep -v "^ANTHROPIC_API_KEY=" "$ENV_FILE" > /tmp/.env.tmp 2>/dev/null || cp "$ENV_FILE" /tmp/.env.tmp
                    echo "ANTHROPIC_API_KEY=$KEY_ANT" >> /tmp/.env.tmp
                    mv /tmp/.env.tmp "$ENV_FILE"
                    chmod 600 "$ENV_FILE"
                    print_ok "Anthropic API key guardada"
                fi
            fi

            echo ""
            echo -n "  Pulsa Enter para volver al menú..."
            read
            ;;

        5)
            echo ""
            print_info "Abriendo guía de usuario..."
            GUIDE_PATH="$ZOE_HOME/zoe/zoe/docs/20_ZOE_GUIA_USUARIO.md"
            GUIDE_PATH_ALT="$ZOE_HOME/zoe/docs/20_ZOE_GUIA_USUARIO.md"
            if [[ -f "$GUIDE_PATH" ]]; then
                open "$GUIDE_PATH"
            elif [[ -f "$GUIDE_PATH_ALT" ]]; then
                open "$GUIDE_PATH_ALT"
            else
                print_warn "No se encontró la guía de usuario en la ruta esperada."
                print_info "Buscando documentación..."
                find "$ZOE_HOME/zoe" -name "*.md" -path "*doc*" -o -name "*GUÍA*" -o -name "*guia*" 2>/dev/null | head -5 | while IFS= read -r doc; do
                    echo -e "  Encontrado: $doc"
                done
            fi
            echo ""
            echo -n "  Pulsa Enter para volver al menú..."
            read
            ;;

        6|*)
            echo ""
            print_ok "¡Hasta pronto!"
            break
            ;;
    esac
done

# ── Mensaje final ────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${BOLD}Resumen de tu instalación ZOE v2.1.1:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}Ubicación:${NC} ${ZOE_HOME}"
echo -e "  ${BOLD}Tipo:${NC} $([[ "$INSTALL_TYPE" == "ssd_crucial" ]] && echo "SSD Crucial X9" || echo "Disco interno Mac")"
echo -e "  ${BOLD}Python:${NC} $($PYTHON --version 2>&1)"
echo -e "  ${BOLD}Entorno virtual:${NC} ${ZOE_HOME}/venv"
echo ""

if [[ "$OLLAMA_INSTALLED" == true ]]; then
    if command -v ollama &>/dev/null; then
        MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
        echo -e "  ${BOLD}Ollama:${NC} Instalado ✓ (${MODEL_COUNT} modelos)"
    else
        echo -e "  ${BOLD}Ollama:${NC} Instalado ✓"
    fi
else
    echo -e "  ${BOLD}Ollama:${NC} No instalado (modelos locales no disponibles)"
fi

echo ""
echo -e "  ${BOLD}Lanzadores disponibles:${NC}"
echo -e "    • ${ZOE_HOME}/INICIAR-ZOE.command       — Menú interactivo"
echo -e "    • ${ZOE_HOME}/INICIAR-DASHBOARD.command — Dashboard web"
echo -e "    • ${ZOE_HOME}/ZOE-Smart.command         — Lanzador avanzado"
echo ""

if [[ "$INSTALL_TYPE" == "ssd_crucial" ]]; then
    echo -e "  ${CYAN}El SSD Crucial X9 es portátil:${NC}"
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
echo -e "${GREEN}  ¡ZOE está lista para despertar!${NC}"
echo ""
