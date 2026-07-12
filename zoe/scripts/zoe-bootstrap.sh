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
# PASO 1b: Verificar formato del SSD
# ============================================================================
print_step "1b/8" "Verificar formato del SSD"

SSD_VOLUME_PATH=$(dirname "$ZOE_HOME")

detect_format_macos() {
    local path=$1
    # Obtener el dispositivo del volumen
    local dev=$(diskutil info "$path" 2>/dev/null | grep "Device Node" | awk '{print $3}')
    if [ -z "$dev" ]; then
        # Intentar con mount
        dev=$(mount | grep "$path" | awk '{print $1}')
    fi
    # Obtener tipo de filesystem
    local fstype=$(diskutil info "$path" 2>/dev/null | grep "File System" | awk -F':+' '{print $2}' | xargs)
    if [ -z "$fstype" ]; then
        fstype=$(mount | grep "$path" | awk '{print $5}' | tr -d '()')
    fi
    echo "$fstype"
}

detect_format_linux() {
    local path=$1
    local fstype=$(df -T "$path" 2>/dev/null | tail -1 | awk '{print $2}')
    if [ -z "$fstype" ]; then
        fstype=$(mount | grep "$path" | awk '{print $5}' | tr -d '()')
    fi
    echo "$fstype"
}

SSD_FORMAT=""
if [ "$PLATFORM" = "Darwin" ]; then
    SSD_FORMAT=$(detect_format_macos "$SSD_VOLUME_PATH")
elif [ "$PLATFORM" = "Linux" ]; then
    SSD_FORMAT=$(detect_format_linux "$SSD_VOLUME_PATH")
fi

SSD_FORMAT_LOWER=$(echo "$SSD_FORMAT" | tr '[:upper:]' '[:lower:]')

if [ -n "$SSD_FORMAT_LOWER" ]; then
    print_info "Formato del SSD: $SSD_FORMAT"
    
    # Verificar si es FAT32 (incompatible con archivos >4GB)
    if echo "$SSD_FORMAT_LOWER" | grep -qi "fat32\|msdos"; then
        print_err "⚠️ El SSD está formateado en FAT32."
        echo ""
        echo -e "  ${RED}${BOLD}PROBLEMA CRÍTICO:${NC} FAT32 no permite archivos de más de 4 GB."
        echo -e "  Los modelos de IA de ZOE pesan entre 3.5 GB y 25 GB."
        echo -e "  La descarga FALLARÁ con error 'Archivo demasiado grande'."
        echo ""
        echo -e "  ${YELLOW}${BOLD}SOLUCIÓN:${NC}"
        echo -e "  1. Abre 'Utilidad de Discos' en tu Mac"
        echo -e "  2. Selecciona tu SSD"
        echo -e "  3. Clic en 'Borrar'"
        echo -e "  4. Formato: ${BOLD}APFS${NC} (solo Mac) o ${BOLD}exFAT${NC} (Mac + Windows + Android)"
        echo -e "  5. ⚠️ Esto borrará todo el contenido del SSD"
        echo ""
        echo -e "  ${BOLD}Tabla de formatos:${NC}"
        echo -e "  ${GREEN}APFS${NC}   → Solo Mac/iPhone. Máxima velocidad mmap. Recomendado si solo usas Apple."
        echo -e "  ${GREEN}exFAT${NC}  → Mac + Windows + Android. Universal. Recomendado si usas varios dispositivos."
        echo -e "  ${RED}FAT32${NC} → ❌ INÚTIL. No permite archivos >4GB. Los modelos no caben."
        echo ""
        echo -n "  ¿Quieres continuar de todas formas (sin descargar modelos grandes)? (s/N): "
        read continue_fat32
        if [ "$continue_fat32" != "s" ] && [ "$continue_fat32" != "S" ]; then
            print_info "Instalación cancelada. Formatea el SSD y vuelve a ejecutar este script."
            exit 0
        fi
        print_warn "Continuando con FAT32. No se descargarán modelos >4GB."
    elif echo "$SSD_FORMAT_LOWER" | grep -qi "apfs"; then
        print_ok "APFS detectado. Formato óptimo para Mac. Velocidad mmap máxima."
    elif echo "$SSD_FORMAT_LOWER" | grep -qi "exfat\|ntfs"; then
        print_ok "exFAT/NTFS detectado. Compatible con modelos grandes. Multiplataforma."
    else
        print_info "Formato: $SSD_FORMAT. Si tienes problemas con archivos grandes, formatea a APFS o exFAT."
    fi
else
    print_info "No se pudo detectar el formato del SSD. Si tienes errores al descargar modelos, formatea a APFS (Mac) o exFAT (multiplataforma)."
fi

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
# PASO 5: Descargar modelos IQ2_M optimizados al SSD
# ============================================================================
print_step "5/8" "Descargar modelos de IA al SSD"

MODELS_DIR="$ZOE_HOME/models"
mkdir -p "$MODELS_DIR"

# Configurar Ollama para usar el SSD como almacenamiento
export OLLAMA_MODELS="$MODELS_DIR"

if [ "$OLLAMA_RUNNING" = true ]; then
    
    echo ""
    echo -e "  ${BOLD}ZOE V1.8 — Modelos IQ2_M optimizados (HuggingFace)${NC}"
    echo -e "  ${CYAN}ACD Router${NC} asigna cada modelo al nivel cognitivo correcto:"
    echo ""
    echo -e "    ${GREEN}L0/L1${NC} (rápido)      → Gemma 2 9B IQ2_M   (3.5GB, 15-25 t/s) ⚡"
    echo -e "    ${GREEN}L2${NC}     (estándar)   → Agents-A1 MoE IQ2_M (11.7GB, 5-10 t/s) ✅"
    echo -e "    ${GREEN}L3${NC}     (profundo)   → QwQ-32B IQ2_M       (12.5GB, 3-6 t/s) 🧠"
    echo -e "    ${GREEN}L3 máx${NC} (calidad)    → Qwen 2.5 72B IQ2_M  (25GB, 1-3 t/s)   🎯"
    echo ""
    echo "  Setups preseleccionados:"
    echo "    [1] Minimal    — Solo Gemma 9B (3.5GB) — ultra rápido, básico"
    echo "    [2] Balanced   — Gemma + QwQ-32B (16GB) — equilibrado ⭐ recomendado para 8GB RAM"
    echo "    [3] Complete   — Gemma + Agents-A1 + QwQ (28GB) — cobertura completa"
    echo "    [4] Maximum    — Los 4 modelos (53GB) — espectro completo (SSD 1TB)"
    echo "    [5] No descargar — usar PatternSpeaker (sin IA)"
    echo "    [6] Saltar — ya tengo modelos IQ2_M"
    echo ""
    echo -n "  Elige [1-6] (default 2): "
    read model_choice
    model_choice=${model_choice:-2}
    
    case $model_choice in
        1)
            SETUP="minimal"
            ;;
        2)
            SETUP="balanced"
            ;;
        3)
            SETUP="complete"
            ;;
        4)
            SETUP="maximum"
            ;;
        5)
            SETUP=""
            print_info "Sin modelos. ZOE usará PatternSpeaker (funciona sin IA)."
            ;;
        6)
            SETUP=""
            print_info "Saltando descarga de modelos."
            ;;
        *)
            SETUP="balanced"
            print_info "Opción no válida — usando 'balanced' por defecto."
            ;;
    esac
    
    if [ -n "$SETUP" ]; then
        print_info "Descargando setup '$SETUP' vía ModelDownloader (HuggingFace IQ2_M)..."
        print_info "Los modelos se guardan en: $MODELS_DIR"
        print_info "Cada modelo se registra en Ollama con su Modelfile optimizado."
        echo ""
        
        "$ZOE_HOME/venv/bin/python" -m zoe.core.model_downloader \
            --download-setup "$SETUP" \
            --models-dir "$MODELS_DIR"
        
        if [ $? -eq 0 ]; then
            print_ok "Setup '$SETUP' descargado y registrado en Ollama"
        else
            print_warn "Algunos modelos fallaron. Puedes reintentar más tarde con:"
            echo "    $ZOE_HOME/venv/bin/python -m zoe.core.model_downloader --download-setup $SETUP --models-dir $MODELS_DIR"
        fi
    fi
else
    print_info "Ollama no está corriendo. Saltando descarga de modelos."
    print_info "ZOE funcionará con PatternSpeaker (sin IA, patrones + memoria)."
    print_info "Cuando tengas Ollama, ejecuta:"
    echo "    $ZOE_HOME/venv/bin/python -m zoe.core.model_downloader --download-setup balanced --models-dir $MODELS_DIR"
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
    
    # ZOE-Chat-Ollama (ACD Router — usa --model auto para routing por nivel cognitivo)
    cat > "$ZOE_HOME/ZOE-Chat-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
# Iniciar Ollama si no está corriendo
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend ollama --model auto
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
    
    # ZOE-Dashboard-Ollama (ACD Router — routing automático por nivel cognitivo)
    cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend ollama --model auto
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.command"
    
    print_ok "4 scripts .command creados en $ZOE_HOME"

# --- Linux ---
elif [ "$PLATFORM" = "Linux" ]; then
    
    # ZOE-Chat (PatternSpeaker — sin IA)
    cat > "$ZOE_HOME/ZOE-Chat.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat.sh"
    
    # ZOE-Chat-Ollama (ACD Router)
    cat > "$ZOE_HOME/ZOE-Chat-Ollama.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend ollama --model auto
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.sh"
    
    # ZOE-Dashboard (PatternSpeaker — sin IA)
    cat > "$ZOE_HOME/ZOE-Dashboard.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend pattern
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard.sh"
    
    # ZOE-Dashboard-Ollama (ACD Router)
    cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.sh" << EOF
#!/bin/bash
ZOE_HOME="$(cd "$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend ollama --model auto
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.sh"
    
    print_ok "4 scripts .sh creados en $ZOE_HOME"
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
echo -e "  ${CYAN}Opción 1: Sin IA (PatternSpeaker, gratis, offline)${NC}"
echo "    Doble clic en ZOE-Chat.command (macOS) / ZOE-Chat.sh (Linux)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend pattern"
echo ""
echo -e "  ${CYAN}Opción 2: Con IA local (ACD Router, 4 modelos IQ2_M)${NC}"
echo "    Doble clic en ZOE-Chat-Ollama.command (macOS) / .sh (Linux)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend ollama --model auto"
echo "    ZOE elegirá automáticamente el modelo óptimo para cada pregunta:"
echo "      • 'Hola' → Gemma 9B (instantáneo)"
echo "      • 'Resume esto' → Agents-A1 MoE (rápido)"
echo "      • 'Analiza las causas' → QwQ-32B (razonamiento)"
echo "      • 'Compara jurídicamente' → Qwen 72B (máxima calidad)"
echo ""
echo -e "  ${CYAN}Opción 3: Dashboard web${NC}"
echo "    Doble clic en ZOE-Dashboard.command / .sh"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.web_dashboard --backend pattern"
echo "    → Abre http://localhost:8642 en tu navegador"
echo ""
echo -e "  ${CYAN}Consejos:${NC}"
echo "    • Escribe /help dentro de ZOE para ver comandos"
echo "    • Escribe /capsules para ver cápsulas de conocimiento"
echo "    • Escribe /capsule elder_care_knowledge para cargar una"
echo "    • Escribe /quit para salir (guarda memoria automáticamente)"
echo ""

# Sprint 5.7 — Fix Gatekeeper quarantine en macOS (los .command recién creados disparan warning)
if [ "$PLATFORM" = "Darwin" ]; then
    print_info "Eliminando atributo quarantine de los .command (Gatekeeper)..."
    xattr -dr com.apple.quarantine "$ZOE_HOME"/*.command 2>/dev/null || true
    print_ok "Scripts .command listos para doble clic sin warning"
fi

# ¿Arrancar Dashboard ahora?
echo -n "  ¿Arrancar Dashboard ahora? (s/N): "
read start_now

if [ "$start_now" = "s" ] || [ "$start_now" = "S" ]; then
    echo ""
    print_info "Arrancando Dashboard..."
    print_info "Abre http://localhost:8642 en tu navegador"
    echo ""
    
    # Determinar backend — Sprint 5.7: usar --model auto si hay Ollama
    if [ "$OLLAMA_RUNNING" = true ]; then
        BACKEND="ollama"
        MODEL="--model auto"
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
