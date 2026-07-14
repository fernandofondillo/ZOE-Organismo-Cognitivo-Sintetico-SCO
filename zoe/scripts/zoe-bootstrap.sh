#!/bin/bash
# ============================================================================
# ZOE BOOTSTRAP v2.1.1 -- Instalador Todo-en-Uno para SSD/Pendrive
# ============================================================================
# Este script configura ZOE COMPLETO en un SSD/pendrive con un solo comando.
# No carga la memoria del Mac. Todo va al SSD.
#
# Que hace automaticamente:
#   1. Detecta tu SSD/pendrive
#   2. Verifica Python y Git (los instala si faltan en macOS)
#   3. Instala ZOE + entorno virtual EN EL SSD
#   4. Detecta si tienes Ollama (lo ofrece instalar si no)
#   4.5 Configura Ollama para usar el SSD como almacenamiento de modelos
#   5. Descarga modelos optimizados al SSD (tu eliges cuales)
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

print_ok()   { echo -e "  ${GREEN}OK${NC} $1"; }
print_warn() { echo -e "  ${YELLOW}ADVERTENCIA${NC} $1"; }
print_err()  { echo -e "  ${RED}ERROR${NC} $1"; }
print_info() { echo -e "  ${BLUE}INFO${NC} $1"; }
print_step() { echo -e "\n${BOLD}${CYAN}[$1]${NC} $2"; }
print_title() { echo -e "\n${BOLD}${CYAN}===============================================${NC}"; echo -e "${BOLD}${CYAN} $1${NC}"; echo -e "${BOLD}${CYAN}===============================================${NC}\n"; }

# ============================================================================
# INICIO
# ============================================================================
print_title "ZOE BOOTSTRAP v2.1.1 -- Instalador Todo-en-Uno"
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
        # Obtener tamano
        size=$(diskutil info "$vol" 2>/dev/null | grep "Disk Size" | awk '{print $3, $4}' || echo "?")
        echo "    [$i] $volname ($size) -- $vol"
        volumes+=("$vol")
        i=$((i+1))
    done
    
    if [ ${#volumes[@]} -eq 0 ]; then
        print_warn "No se encontraron discos externos."
        echo -e "  Quieres instalar en local (~/${BOLD}ZOE${NC})? (s/N): "
        echo -n "  >> "
        read install_local
        if [ "$install_local" = "s" ] || [ "$install_local" = "S" ]; then
            ZOE_HOME="$HOME/ZOE"
        else
            print_err "Conecta un SSD o pendrive y vuelve a ejecutar este script."
            exit 1
        fi
    else
        echo ""
        echo -n "  Selecciona el disco [1-${#volumes[@]}] (o 'L' para local en ~/ZOE): "
        read choice
        
        if [ "$choice" = "L" ] || [ "$choice" = "l" ]; then
            ZOE_HOME="$HOME/ZOE"
        elif [ "$choice" -ge 1 ] && [ "$choice" -le ${#volumes[@]} ] 2>/dev/null; then
            ZOE_HOME="${volumes[$((choice-1))]}ZOE"
        else
            print_err "Seleccion invalida"
            exit 1
        fi
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

elif echo "$PLATFORM" | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    # Windows (Git Bash / MSYS2 / Cygwin)
    print_info "Windows detectado via $PLATFORM"
    echo "  Discos disponibles:"
    volumes=()
    i=1
    for drive in C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
        if [ -d "/${drive}" ] || [ -d "${drive}:/" ]; then
            # Saltar C: (sistema)
            if [ "$drive" = "C" ]; then continue; fi
            volpath="${drive}:/"
            if [ -d "$volpath" ]; then
                echo "    [$i] $volpath"
                volumes+=("$volpath")
                i=$((i+1))
            fi
        fi
    done
    
    if [ ${#volumes[@]} -eq 0 ]; then
        print_info "No se encontraron discos externos. Instalando en ~/ZOE"
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
else
    print_err "Plataforma no soportada: $PLATFORM"
    echo "  ZOE bootstrap funciona en macOS, Linux y Windows (Git Bash)."
    exit 1
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
        print_err "El SSD esta formateado en FAT32."
        echo ""
        echo -e "  ${RED}${BOLD}PROBLEMA CRITICO:${NC} FAT32 no permite archivos de mas de 4 GB."
        echo -e "  Los modelos de IA de ZOE pesan entre 3.5 GB y 25 GB."
        echo -e "  La descarga FALLARA con error 'Archivo demasiado grande'."
        echo ""
        echo -e "  ${YELLOW}${BOLD}SOLUCION:${NC}"
        echo -e "  1. Abre 'Utilidad de Discos' en tu Mac"
        echo -e "  2. Selecciona tu SSD"
        echo -e "  3. Clic en 'Borrar'"
        echo -e "  4. Formato: ${BOLD}APFS${NC} (solo Mac) o ${BOLD}exFAT${NC} (Mac + Windows + Android)"
        echo -e "  5. Esto borrara todo el contenido del SSD"
        echo ""
        echo -e "  ${BOLD}Tabla de formatos:${NC}"
        echo -e "  ${GREEN}APFS${NC}   -> Solo Mac/iPhone. Maxima velocidad mmap. Recomendado si solo usas Apple."
        echo -e "  ${GREEN}exFAT${NC}  -> Mac + Windows + Android. Universal. Recomendado si usas varios dispositivos."
        echo -e "  ${RED}FAT32${NC} -> INUTIL. No permite archivos >4GB. Los modelos no caben."
        echo ""
        echo -n "  Quieres continuar de todas formas (sin descargar modelos grandes)? (s/N): "
        read continue_fat32
        if [ "$continue_fat32" != "s" ] && [ "$continue_fat32" != "S" ]; then
            print_info "Instalacion cancelada. Formatea el SSD y vuelve a ejecutar este script."
            exit 0
        fi
        print_warn "Continuando con FAT32. No se descargaran modelos >4GB."
    elif echo "$SSD_FORMAT_LOWER" | grep -qi "apfs"; then
        print_ok "APFS detectado. Formato optimo para Mac. Velocidad mmap maxima."
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
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYVER=$(python --version 2>&1)
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

# Sprint 5.7.1 -- Verificar version Python >= 3.10
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    print_err "Python $PY_MAJOR.$PY_MINOR detectado -- ZOE requiere Python 3.10+"
    echo -e "  Descarga Python 3.10+ desde: https://python.org/downloads/"
    exit 1
fi
print_ok "Python: $PYVER (>= 3.10 OK)"

# Git
if command -v git &> /dev/null; then
    print_ok "Git: $(git --version)"
else
    print_warn "Git no encontrado. Intentando instalar..."
    if [ "$PLATFORM" = "Darwin" ]; then
        # xcode-select requiere interaccion del usuario; advertir y salir
        print_err "Git no esta instalado. En macOS, ejecuta primero:"
        echo -e "  xcode-select --install"
        echo -e "  (se abrira una ventana del sistema; espera a que termine)"
        echo -e "  Despues vuelve a ejecutar este script."
        exit 1
    elif echo "$PLATFORM" | grep -qi "MINGW\|MSYS\|CYGWIN"; then
        print_err "Git no esta instalado. En Windows, instala Git Bash desde:"
        echo -e "  https://git-scm.com/download/win"
        exit 1
    else
        sudo apt update && sudo apt install -y git || { print_err "No se pudo instalar git"; exit 1; }
    fi
fi

# Sprint 5.7.1 -- Verificar espacio libre en SSD antes de descargar modelos
# Requiere: ZOE_HOME creado (paso 1) y setup elegido (paso 5) -- movemos la verificacion
# justo antes de la descarga en el paso 5.

# ============================================================================
# PASO 3: Clonar ZOE y crear entorno virtual EN EL SSD
# ============================================================================
print_step "3/8" "Instalar ZOE en el SSD"

ZOE_REPO_URL="https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git"
ZOE_REPO_PUBLIC_URL="https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO"

if [ -d "$ZOE_HOME/zoe" ]; then
    print_info "ZOE ya existe en el SSD. Actualizando..."
    cd "$ZOE_HOME/zoe"
    git pull --quiet || print_warn "No se pudo actualizar (sin internet?). Continuando con version local."
else
    print_info "Clonando repositorio de ZOE..."
    # Sprint 5.7.1 -- Intentar clonar. Si falla (repo privado o sin creds), pedir token.
    if ! git clone --quiet "$ZOE_REPO_URL" "$ZOE_HOME/zoe" 2>/dev/null; then
        print_warn "Clone fallo. El repositorio es privado o no hay credenciales configuradas."
        echo ""
        echo -e "  ${BOLD}Opciones:${NC}"
        echo -e "  ${CYAN}[1]${NC} Tengo un Personal Access Token (PAT) de GitHub"
        echo -e "  ${CYAN}[2]${NC} Ya tengo el repo descargado en otro sitio -- copiare la carpeta manualmente"
        echo -e "  ${CYAN}[3]${NC} Cancelar instalacion"
        echo ""
        echo -n "  Elige [1-3]: "
        read clone_choice
        
        case "$clone_choice" in
            1)
                echo -n "  Pega tu GitHub PAT (ghp_...): "
                read -r gh_token
                if [ -z "$gh_token" ]; then
                    print_err "Token vacio. Cancelando."
                    exit 1
                fi
                print_info "Intentando clone con token..."
                if ! git clone --quiet "https://${gh_token}@github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git" "$ZOE_HOME/zoe" 2>/dev/null; then
                    print_err "Clone con token fallo. Verifica que el token tenga permiso 'repo'."
                    exit 1
                fi
                # Limpiar credenciales del .git/config para no dejar el token en el SSD
                cd "$ZOE_HOME/zoe"
                git remote set-url origin "$ZOE_REPO_PUBLIC_URL" 2>/dev/null || true
                print_ok "Repositorio clonado (token no guardado en el SSD)"
                ;;
            2)
                print_info "Copia manualmente la carpeta del repo a: $ZOE_HOME/zoe"
                echo -e "  Despues vuelve a ejecutar este script (detectara que ya existe)."
                exit 0
                ;;
            *)
                print_info "Instalacion cancelada."
                exit 0
                ;;
        esac
    fi
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
    # Verificar si esta corriendo
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_ok "Ollama esta corriendo"
        OLLAMA_RUNNING=true
    else
        print_info "Iniciando Ollama (puede tardar 10-15s la primera vez)..."
        ollama serve &> /dev/null &
        # Sprint 5.7.1 -- Retry con backoff (3 intentos: 3s, 5s, 10s = 18s total)
        for attempt in 1 2 3; do
            sleep_times=(3 5 10)
            sleep ${sleep_times[$((attempt-1))]}
            if curl -s http://localhost:11434/api/tags &> /dev/null; then
                OLLAMA_RUNNING=true
                print_ok "Ollama iniciado (intentos: $attempt)"
                break
            fi
            if [ $attempt -lt 3 ]; then
                print_info "Esperando Ollama... (intento $attempt/3)"
            fi
        done
        if [ "$OLLAMA_RUNNING" != "true" ]; then
            print_warn "Ollama no pudo iniciar en 18s. Lo iniciaras manualmente con: ollama serve"
            print_warn "Despues ejecuta de nuevo este script, o los lanzadores .command funcionaran."
        fi
    fi
else
    print_warn "Ollama no esta instalado."
    echo -e "  ${BOLD}Instalar Ollama?${NC} (recomendado -- IA local gratis, sin internet)"
    echo -n "  Instalar Ollama ahora? (s/N): "
    read INSTALL_OLLAMA
    
    if [ "$INSTALL_OLLAMA" = "s" ] || [ "$INSTALL_OLLAMA" = "S" ]; then
        print_info "Instalando Ollama..."
        if curl -fsSL https://ollama.com/install.sh | sh; then
            print_ok "Ollama instalado"
            # Verificar instalacion
            if ! command -v ollama &> /dev/null; then
                print_warn "Ollama instalado pero no en PATH. Reinicia tu terminal y vuelve a ejecutar."
            else
                # Iniciar con retry
                ollama serve &> /dev/null &
                for attempt in 1 2 3; do
                    sleep_times=(3 5 10)
                    sleep ${sleep_times[$((attempt-1))]}
                    if curl -s http://localhost:11434/api/tags &> /dev/null; then
                        OLLAMA_RUNNING=true
                        print_ok "Ollama corriendo (intento $attempt)"
                        break
                    fi
                done
                if [ "$OLLAMA_RUNNING" != "true" ]; then
                    print_warn "Ollama instalado. Inicia manualmente con: ollama serve"
                fi
            fi
        else
            print_err "La instalacion de Ollama fallo. Instalalo manualmente desde https://ollama.com"
        fi
    else
        print_info "Ollama no instalado. ZOE funcionara con PatternSpeaker (sin IA)."
        print_info "Puedes instalarlo despues desde https://ollama.com"
    fi
fi

# ============================================================================
# PASO 4.5: Configurar Ollama para usar SSD como almacenamiento de modelos
# ============================================================================
# Este paso solo se ejecuta si Ollama esta instalado (ya estaba o se instalo
# en el paso 4). Redirige ~/.ollama/models al SSD via symlink y persiste
# la variable OLLAMA_MODELS en el shell RC del usuario.
# ============================================================================

OLLAMA_CONFIGURED=false

if [ "$INSTALL_OLLAMA" = "s" ] || [ "$INSTALL_OLLAMA" = "S" ] || command -v ollama &> /dev/null; then
    print_step "4.5/8" "Configurar Ollama para usar SSD como almacenamiento de modelos"
    
    # 4.5a: Crear directorio Ollama en el SSD
    OLLAMA_SSD_DIR="$ZOE_HOME/models/ollama"
    print_info "Creando directorio de modelos Ollama en SSD: $OLLAMA_SSD_DIR"
    mkdir -p "$OLLAMA_SSD_DIR/manifests"
    mkdir -p "$OLLAMA_SSD_DIR/blobs"
    print_ok "Directorio creado en SSD"
    
    # 4.5b: Backup y symlink de ~/.ollama/models
    OLLAMA_MODELS_DIR="$HOME/.ollama/models"
    
    if [ -d "$OLLAMA_MODELS_DIR" ] && [ ! -L "$OLLAMA_MODELS_DIR" ]; then
        # Es un directorio real: hacer backup
        BACKUP_NAME="$HOME/.ollama/models_backup_$(date +%Y%m%d_%H%M%S)"
        print_info "Directorio existente detectado. Haciendo backup: $BACKUP_NAME"
        mv "$OLLAMA_MODELS_DIR" "$BACKUP_NAME"
        print_ok "Backup completado"
    fi
    
    if [ -L "$OLLAMA_MODELS_DIR" ]; then
        # Es un symlink: eliminarlo
        print_info "Eliminando symlink anterior..."
        rm "$OLLAMA_MODELS_DIR"
    fi
    
    # Crear symlink nuevo
    mkdir -p "$HOME/.ollama" 2>/dev/null || true
    ln -s "$OLLAMA_SSD_DIR" "$OLLAMA_MODELS_DIR"
    print_ok "Symlink creado: ~/.ollama/models -> $OLLAMA_SSD_DIR"
    
    # 4.5c: Persistir OLLAMA_MODELS en shell RC
    SHELL_RC="$HOME/.zshrc"
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    print_info "Configurando variable OLLAMA_MODELS en $SHELL_RC..."
    
    # Eliminar cualquier linea previa de OLLAMA_MODELS
    if [ -f "$SHELL_RC" ]; then
        grep -v "OLLAMA_MODELS=" "$SHELL_RC" > "$SHELL_RC.tmp" 2>/dev/null && mv "$SHELL_RC.tmp" "$SHELL_RC"
    fi
    
    # Anadir nueva linea
    echo "" >> "$SHELL_RC"
    echo "# ZOE v2.1.1 -- Ollama almacena modelos en SSD externo" >> "$SHELL_RC"
    echo "export OLLAMA_MODELS=\"$OLLAMA_SSD_DIR\"" >> "$SHELL_RC"
    print_ok "Variable OLLAMA_MODELS persistida en $SHELL_RC"
    
    # 4.5d: Exportar para sesion actual
    export OLLAMA_MODELS="$OLLAMA_SSD_DIR"
    
    # 4.5e: Confirmacion
    OLLAMA_CONFIGURED=true
    print_ok "Ollama configurado para usar SSD: $OLLAMA_SSD_DIR"
    print_info "Symlink: ~/.ollama/models -> $OLLAMA_SSD_DIR"
    
    # Verificar que el symlink es correcto
    if [ -L "$OLLAMA_MODELS_DIR" ]; then
        LINK_TARGET=$(readlink "$OLLAMA_MODELS_DIR" 2>/dev/null || echo "?")
        print_info "Verificacion: symlink apunta a: $LINK_TARGET"
    fi
else
    print_info "Ollama no esta instalado. Saltando configuracion de SSD para modelos."
fi

# ============================================================================
# PASO 5: Descargar modelos IQ2_M optimizados al SSD
# ============================================================================
print_step "5/8" "Descargar modelos de IA al SSD"

# Detectar RAM para seleccion inteligente de L4_REFLECTION
RAM_GB=0
if [ "$PLATFORM" = "Darwin" ]; then
    RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
    RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))
elif [ "$PLATFORM" = "Linux" ]; then
    RAM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
    RAM_GB=$((RAM_KB / 1024 / 1024))
fi
print_info "RAM detectada: ${RAM_GB} GB"

MODELS_DIR="$ZOE_HOME/models/ollama"
mkdir -p "$MODELS_DIR"

# Configurar Ollama para usar el SSD como almacenamiento
export OLLAMA_MODELS="$MODELS_DIR"

if [ "$OLLAMA_RUNNING" = true ]; then
    
    echo ""
    echo -e "  ${BOLD}ZOE v2.1.1 -- Modelos IQ2_M optimizados (HuggingFace)${NC}"
    echo -e "  ${CYAN}ACD Router${NC} asigna cada modelo al nivel cognitivo correcto:"
    echo ""
    echo -e "    ${GREEN}L0/L1${NC} (reflejo/rapido)  -> Gemma 2 9B IQ2_M   (3.5GB, 15-25 t/s)"
    echo -e "    ${GREEN}L2${NC}     (estandar)       -> Agents-A1 MoE IQ2_M  (11.7GB, 5-10 t/s)"
    echo -e "    ${GREEN}L3${NC}     (profundo)       -> QwQ-32B IQ2_M        (12.5GB, 3-6 t/s)"
    echo -e "    ${GREEN}L3 max${NC} (calidad)        -> Qwen 2.5 72B IQ2_M   (25GB, 1-3 t/s)"
    echo -e "    ${GREEN}L4${NC}     (reflexion)*     -> DeepSeek-R1 32B      (12.5-18GB, 2-4 t/s)"
    echo ""
    echo -e "    * L4_REFLECTION se adapta automaticamente a tu RAM:"
    echo -e "      - 8GB  RAM -> IQ2_M  (12.5GB, ~93% calidad, sin swap)"
    echo -e "      - 16GB RAM -> Q4_K_M (18GB, ~98% calidad)"
    echo ""
    echo "  Setups preseleccionados:"
    echo "    [1] Minimal       -- Solo Gemma 9B (3.5GB) -- ultra rapido, basico"
    echo "    [2] Balanced      -- Gemma + QwQ-32B (16GB) -- equilibrado (recomendado para 8GB RAM)"
    echo "    [3] Complete      -- Gemma + Agents-A1 + QwQ (28GB) -- cobertura completa"
    echo "    [4] Maximum       -- Los 4 modelos (53GB) -- espectro completo (SSD 1TB)"
    echo "    [5] Reflexion     -- Espectro + L4 IQ2_M  (41GB) -- para Mac 8GB"
    echo "    [6] Reflexion Pro -- Espectro + L4 Q4_K_M (46GB) -- solo 16GB RAM"
    echo "    [7] No descargar  -- usar PatternSpeaker (sin IA)"
    echo "    [8] Saltar        -- ya tengo modelos IQ2_M"
    echo ""
    echo -n "  Elige [1-8] (default 2): "
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
            SETUP="reflection"
            ;;
        6)
            if [ "$RAM_GB" -ge 16 ]; then
                SETUP="reflection-16gb"
            else
                print_warn "Reflexion Pro requiere 16GB RAM. Tienes ${RAM_GB}GB."
                print_info "Usando Reflexion estandar (IQ2_M) en su lugar."
                SETUP="reflection"
            fi
            ;;
        7)
            SETUP=""
            print_info "Sin modelos. ZOE usara PatternSpeaker (funciona sin IA)."
            ;;
        8)
            SETUP=""
            print_info "Saltando descarga de modelos."
            ;;
        *)
            SETUP="balanced"
            print_info "Opcion no valida -- usando 'balanced' por defecto."
            ;;
    esac

    # Mensaje de seleccion automatica L4_REFLECTION
    if [ "$SETUP" = "reflection" ] || [ "$SETUP" = "reflection-16gb" ]; then
        if [ "$RAM_GB" -ge 16 ]; then
            print_ok "L4_REFLECTION: DeepSeek-R1 Q4_K_M (maxima calidad, 16GB+ RAM detectada)"
        else
            print_ok "L4_REFLECTION: DeepSeek-R1 IQ2_M (optimizado para 8GB RAM, sin swap)"
            print_info "Con 8GB RAM, la reflexion usa IQ2_M (~93% calidad) para evitar swap."
            print_info "Si actualizas a 16GB RAM, reinstala con: --download-setup reflection-16gb"
        fi
    fi
    
    if [ -n "$SETUP" ]; then
        # Sprint 5.7.1 -- Verificar espacio libre en SSD antes de descargar
        # Tamanos minimos por setup (con margen 20%)
        case "$SETUP" in
            minimal)  NEEDED_GB=5 ;;
            balanced) NEEDED_GB=20 ;;
            complete) NEEDED_GB=35 ;;
            maximum)  NEEDED_GB=65 ;;
            reflection) NEEDED_GB=50 ;;
            reflection-16gb) NEEDED_GB=56 ;;
            *)        NEEDED_GB=20 ;;
        esac
        
        # Obtener espacio libre en MB
        if [ "$PLATFORM" = "Darwin" ]; then
            FREE_MB=$(df -m "$ZOE_HOME" 2>/dev/null | tail -1 | awk '{print $4}')
        else
            FREE_MB=$(df -m "$ZOE_HOME" 2>/dev/null | tail -1 | awk '{print $4}')
        fi
        
        if [ -n "$FREE_MB" ] && [ "$FREE_MB" -gt 0 ] 2>/dev/null; then
            FREE_GB=$((FREE_MB / 1024))
            print_info "Espacio libre en $ZOE_HOME: ${FREE_GB}GB (necesario: ~${NEEDED_GB}GB)"
            if [ "$FREE_GB" -lt "$NEEDED_GB" ]; then
                print_err "Espacio insuficiente. Necesitas ${NEEDED_GB}GB libres, tienes ${FREE_GB}GB."
                echo -e "  Opciones:"
                echo -e "   1. Borra archivos del SSD y reintenta"
                echo -e "   2. Elige un setup mas pequeno (minimal: 5GB, balanced: 20GB)"
                echo -e "   3. Continua de todas formas (la descarga puede fallar a mitad)"
                echo -n "  Continuar de todas formas? (s/N): "
                read continue_low_space
                if [ "$continue_low_space" != "s" ] && [ "$continue_low_space" != "S" ]; then
                    print_info "Descarga cancelada. ZOE funcionara con PatternSpeaker (sin IA)."
                    SETUP=""
                fi
            fi
        else
            print_warn "No se pudo verificar el espacio libre. Continuando con precaucion."
        fi
    fi
    
    if [ -n "$SETUP" ]; then
        print_info "Descargando setup '$SETUP' via ModelDownloader (HuggingFace IQ2_M)..."
        print_info "Los modelos se guardan en: $MODELS_DIR"
        print_info "Cada modelo se registra en Ollama con su Modelfile optimizado."
        print_info "Esto puede tardar 10-30 min segun tu conexion (no tu SSD)."
        echo ""
        
        "$ZOE_HOME/venv/bin/python" -m zoe.core.model_downloader \
            --download-setup "$SETUP" \
            --models-dir "$MODELS_DIR"
        
        if [ $? -eq 0 ]; then
            print_ok "Setup '$SETUP' descargado y registrado en Ollama"
        else
            print_warn "Algunos modelos fallaron. Puedes reintentar mas tarde con:"
            echo "    $ZOE_HOME/venv/bin/python -m zoe.core.model_downloader --download-setup $SETUP --models-dir $MODELS_DIR"
        fi
    fi
else
    print_info "Ollama no esta corriendo. Saltando descarga de modelos."
    print_info "ZOE funcionara con PatternSpeaker (sin IA, patrones + memoria)."
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

echo "  Puedes configurar API keys de cloud para maxima calidad en L3."
echo "  ZOE usara cloud SOLO para preguntas complejas (ahorra dinero)."
echo ""

echo -n "  Configurar OpenAI API key? (s/N): "
read config_openai
if [ "$config_openai" = "s" ] || [ "$config_openai" = "S" ]; then
    echo -n "  Pega tu API key (sk-...): "
    read -s openai_key
    echo "OPENAI_API_KEY=$openai_key" >> "$ENV_FILE"
    print_ok "OpenAI API key guardada en $ENV_FILE"
fi

echo -n "  Configurar Anthropic (Claude) API key? (s/N): "
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

# Funcion para cargar .env (Sprint 5.7.1: source en vez de xargs para no romper API keys)
LOAD_ENV='if [ -f "$ZOE_HOME/data/.env" ]; then set -a; source "$ZOE_HOME/data/.env"; set +a; fi'

# --- macOS: .command ---
if [ "$PLATFORM" = "Darwin" ]; then
    
    # ZOE-Chat (PatternSpeaker -- sin IA)
    cat > "$ZOE_HOME/ZOE-Chat.command" << EOF
#!/bin/bash
# Sprint 5.7.1: ZOE_HOME se calcula en runtime (no en escritura del heredoc)
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD para que ZOE carge vault/trayectoria/memoria del SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend pattern --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/zoe_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat.command"
    
    # ZOE-Chat-Ollama (ACD Router -- usa --model auto para routing por nivel cognitivo)
    cat > "$ZOE_HOME/ZOE-Chat-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models/ollama"
# Iniciar Ollama si no esta corriendo
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend ollama --model auto --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/zoe_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.command"
    
    # ZOE-Dashboard (PatternSpeaker -- sin IA)
    cat > "$ZOE_HOME/ZOE-Dashboard.command" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD para que el dashboard carge el MISMO ZOE que el chat
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend pattern --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/dashboard_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard.command"
    
    # ZOE-Dashboard-Ollama (ACD Router -- routing automatico por nivel cognitivo)
    cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.command" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models/ollama"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend ollama --model auto --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/dashboard_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.command"

    # Sprint 5.12 -- INICIAR-DASHBOARD.command: lanzador universal que detecta
    # automaticamente el mejor backend disponible (Ollama > OpenAI > Anthropic > pattern)
    # y abre el navegador con el token de auth embebido en la URL.
    cat > "$ZOE_HOME/INICIAR-DASHBOARD.command" << 'DASH_EOF'
#!/bin/bash
# ============================================================================
# ZOE Dashboard Launcher v2.1.2 -- macOS
# Doble click para abrir el Dashboard de ZOE en el navegador.
# Detecta automaticamente el mejor backend (Ollama > OpenAI > Anthropic > pattern).
# ============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

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

# Cargar variables de entorno (source, no xargs)
ENV_FILE="$ZOE_HOME/data/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    echo -e "  ${GREEN}OK${NC} Variables cargadas"
fi

# Activar venv
if [ -f "$ZOE_HOME/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ZOE_HOME/venv/bin/activate"
    echo -e "  ${GREEN}OK${NC} Entorno virtual activado"
fi

# OLLAMA_MODELS al SSD
if [ -d "$ZOE_HOME/models/ollama" ]; then
    export OLLAMA_MODELS="$ZOE_HOME/models/ollama"
    echo -e "  ${GREEN}OK${NC} OLLAMA_MODELS -> $OLLAMA_MODELS"
fi

# Detectar backend
DASH_BACKEND="pattern"
DASH_MODEL=""
if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    DASH_BACKEND="ollama"; DASH_MODEL="auto"
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

# Iniciar Ollama si hace falta
if [ "$DASH_BACKEND" = "ollama" ]; then
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${CYAN}INFO${NC} Iniciando Ollama..."
        ollama serve &>/dev/null &
        sleep 3
    fi
fi

PORT="${ZOE_DASHBOARD_PORT:-8642}"
echo ""
echo -e "  ${BOLD}URL del Dashboard:${NC} ${CYAN}http://localhost:${PORT}/${NC}"
echo -e "  ${BOLD}Copia la URL completa (con ?token=...) al navegador cuando arranque.${NC}"
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
DASH_EOF
    chmod +x "$ZOE_HOME/INICIAR-DASHBOARD.command"

    # Sprint 5.12 -- INICIAR-ZOE.command: lanzador universal chat terminal
    cat > "$ZOE_HOME/INICIAR-ZOE.command" << 'CHAT_EOF'
#!/bin/bash
# ZOE Chat Launcher v2.1.2 -- macOS
# Doble click para iniciar chat ZOE en terminal con deteccion automatica de backend.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$SCRIPT_DIR/venv" ] && ZOE_HOME="$SCRIPT_DIR" || ZOE_HOME="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || echo "$SCRIPT_DIR")"

[ -f "$ZOE_HOME/data/.env" ] && { set -a; source "$ZOE_HOME/data/.env"; set +a; }
[ -f "$ZOE_HOME/venv/bin/activate" ] && source "$ZOE_HOME/venv/bin/activate"
[ -d "$ZOE_HOME/models/ollama" ] && export OLLAMA_MODELS="$ZOE_HOME/models/ollama"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Chat v2.1.2                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  ZOE_HOME: $ZOE_HOME"
echo ""

BACKEND="pattern"; MODEL=""
if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    BACKEND="ollama"; MODEL="auto"
    echo "  OK Ollama detectado -- ACD Router (5 niveles cognitivos)"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    BACKEND="openai_compatible"; MODEL="gpt-4o"
    echo "  OK OpenAI configurado"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    BACKEND="anthropic"; MODEL="claude-sonnet-4-20250514"
    echo "  OK Anthropic configurado"
else
    echo "  ADVERTENCIA Sin modelos IA -- PatternSpeaker (offline)"
fi

[ -d "$ZOE_HOME/zoe" ] && cd "$ZOE_HOME/zoe"
exec python -m zoe.cli_chat --backend "$BACKEND" ${MODEL:+--model "$MODEL"} --db-path "${ZOE_DATA:-$ZOE_HOME/data}/zoe_memory.db"
CHAT_EOF
    chmod +x "$ZOE_HOME/INICIAR-ZOE.command"

    # Eliminar quarantine de todos los .command
    xattr -dr com.apple.quarantine "$ZOE_HOME"/*.command 2>/dev/null || true

    print_ok "6 scripts .command creados en $ZOE_HOME"

# --- Linux ---
elif [ "$PLATFORM" = "Linux" ]; then
    
    # ZOE-Chat (PatternSpeaker -- sin IA)
    cat > "$ZOE_HOME/ZOE-Chat.sh" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend pattern --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/zoe_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat.sh"
    
    # ZOE-Chat-Ollama (ACD Router)
    cat > "$ZOE_HOME/ZOE-Chat-Ollama.sh" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models/ollama"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.cli_chat --backend ollama --model auto --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/zoe_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.sh"
    
    # ZOE-Dashboard (PatternSpeaker -- sin IA)
    cat > "$ZOE_HOME/ZOE-Dashboard.sh" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend pattern --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/dashboard_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard.sh"
    
    # ZOE-Dashboard-Ollama (ACD Router)
    cat > "$ZOE_HOME/ZOE-Dashboard-Ollama.sh" << EOF
#!/bin/bash
ZOE_HOME="\$(cd "\$(dirname "\$0")" && pwd)"
$LOAD_ENV
export OLLAMA_MODELS="\$ZOE_HOME/models/ollama"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
cd "\$ZOE_HOME/zoe"
# Sprint 5.12 GAP-Q: pasar --db-path al SSD
"\$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend ollama --model auto --db-path "\${ZOE_DATA:-\$ZOE_HOME/data}/dashboard_memory.db"
EOF
    chmod +x "$ZOE_HOME/ZOE-Dashboard-Ollama.sh"

    # Sprint 5.12 -- INICIAR-DASHBOARD.sh: lanzador universal con deteccion automatica
    cat > "$ZOE_HOME/INICIAR-DASHBOARD.sh" << 'DASH_EOF'
#!/bin/bash
# ZOE Dashboard Launcher v2.1.2 -- Linux
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$SCRIPT_DIR/venv" ] && ZOE_HOME="$SCRIPT_DIR" || ZOE_HOME="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
[ -f "$ZOE_HOME/data/.env" ] && { set -a; source "$ZOE_HOME/data/.env"; set +a; }
[ -f "$ZOE_HOME/venv/bin/activate" ] && source "$ZOE_HOME/venv/bin/activate"
[ -d "$ZOE_HOME/models/ollama" ] && export OLLAMA_MODELS="$ZOE_HOME/models/ollama"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Dashboard v2.1.2                                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  ZOE_HOME: $ZOE_HOME"

BACKEND="pattern"; MODEL=""
if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    BACKEND="ollama"; MODEL="auto"
    [ ! -s /tmp/ollama_ready ] && { ollama serve &>/dev/null & sleep 3; }
    echo "  OK Ollama detectado -- ACD Router"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    BACKEND="openai_compatible"; MODEL="gpt-4o"
    echo "  OK OpenAI -- GPT-4o"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    BACKEND="anthropic"; MODEL="claude-sonnet-4-20250514"
    echo "  OK Anthropic -- Claude"
else
    echo "  ADVERTENCIA Sin IA -- PatternSpeaker (offline)"
fi

PORT="${ZOE_DASHBOARD_PORT:-8642}"
echo "  URL: http://localhost:${PORT}/"
echo "  Copia la URL completa (con ?token=...) al navegador."
echo ""

[ -d "$ZOE_HOME/zoe" ] && cd "$ZOE_HOME/zoe"
exec python -m zoe.web_dashboard --backend "$BACKEND" ${MODEL:+--model "$MODEL"} --port "$PORT" --host "127.0.0.1" --db-path "${ZOE_DATA:-$ZOE_HOME/data}/dashboard_memory.db"
DASH_EOF
    chmod +x "$ZOE_HOME/INICIAR-DASHBOARD.sh"

    # INICIAR-ZOE.sh: lanzador chat universal
    cat > "$ZOE_HOME/INICIAR-ZOE.sh" << 'CHAT_EOF'
#!/bin/bash
# ZOE Chat Launcher v2.1.2 -- Linux
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$SCRIPT_DIR/venv" ] && ZOE_HOME="$SCRIPT_DIR" || ZOE_HOME="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
[ -f "$ZOE_HOME/data/.env" ] && { set -a; source "$ZOE_HOME/data/.env"; set +a; }
[ -f "$ZOE_HOME/venv/bin/activate" ] && source "$ZOE_HOME/venv/bin/activate"
[ -d "$ZOE_HOME/models/ollama" ] && export OLLAMA_MODELS="$ZOE_HOME/models/ollama"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE Chat v2.1.2                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"

BACKEND="pattern"; MODEL=""
if command -v ollama &>/dev/null && ollama list 2>/dev/null | grep -q .; then
    BACKEND="ollama"; MODEL="auto"; echo "  OK Ollama detectado"
elif [ -n "${OPENAI_API_KEY:-}" ]; then
    BACKEND="openai_compatible"; MODEL="gpt-4o"; echo "  OK OpenAI configurado"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    BACKEND="anthropic"; MODEL="claude-sonnet-4-20250514"; echo "  OK Anthropic configurado"
else
    echo "  ADVERTENCIA Sin IA -- PatternSpeaker (offline)"
fi

[ -d "$ZOE_HOME/zoe" ] && cd "$ZOE_HOME/zoe"
exec python -m zoe.cli_chat --backend "$BACKEND" ${MODEL:+--model "$MODEL"} --db-path "${ZOE_DATA:-$ZOE_HOME/data}/zoe_memory.db"
CHAT_EOF
    chmod +x "$ZOE_HOME/INICIAR-ZOE.sh"

    print_ok "6 scripts .sh creados en $ZOE_HOME"
fi

# ============================================================================
# PASO 8: Resumen y arranque
# ============================================================================
print_step "8/8" "Resumen"

print_title "ZOE ESTA LISTA!"

echo -e "  ${BOLD}Version:${NC} ZOE v2.1.1"
echo -e "  ${BOLD}Ubicacion:${NC} $ZOE_HOME"
echo ""

# Mostrar que hay instalado
echo -e "  ${BOLD}Componentes instalados:${NC}"
print_ok "ZOE v2.1.1 (codigo + entorno virtual)"
print_ok "PatternSpeaker (funciona sin IA, siempre disponible)"

if command -v ollama &> /dev/null; then
    print_ok "Ollama (IA local gratis)"
    if [ "$OLLAMA_CONFIGURED" = true ]; then
        print_ok "Ollama configurado para SSD: $MODELS_DIR"
        print_ok "Symlink: ~/.ollama/models -> $MODELS_DIR"
    fi
    echo -e "  ${BOLD}Modelos disponibles:${NC}"
    ollama list 2>/dev/null | tail -n +2 | while read line; do
        if [ -n "$line" ]; then
            echo -e "      $line"
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
echo -e "  ${BOLD}Como usar ZOE:${NC}"
echo ""
echo -e "  ${CYAN}Opcion 1: Sin IA (PatternSpeaker, gratis, offline)${NC}"
echo "    Doble clic en ZOE-Chat.command (macOS) / ZOE-Chat.sh (Linux)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend pattern"
echo ""
echo -e "  ${CYAN}Opcion 2: Con IA local (ACD Router, 5 niveles cognitivos)${NC}"
echo "    Doble clic en ZOE-Chat-Ollama.command (macOS) / .sh (Linux)"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.cli_chat --backend ollama --model auto"
echo "    ZOE elegira automaticamente el modelo optimo para cada pregunta:"
echo "      L0/L1 (reflejo)  -> Gemma 2 9B        -- 'Hola' (instantaneo)"
echo "      L2 (estandar)    -> Agents-A1 MoE     -- 'Resume esto' (rapido)"
echo "      L3 (profundo)    -> QwQ-32B           -- 'Analiza las causas' (razonamiento)"
echo "      L3 max (calidad) -> Qwen 2.5 72B       -- 'Compara juridicamente' (max calidad)"
echo "      L4 (reflexion)   -> DeepSeek-R1 32B   -- Activo durante SLEEPING*"
echo ""
echo -e "  *L4_REFLECTION: Se activa automaticamente durante el modo SLEEPING."
echo -e "   Requiere 16GB RAM o mas. Realiza introspeccion profunda del ciclo."
echo ""
echo -e "  ${CYAN}Opcion 3: Dashboard web${NC}"
echo "    Doble clic en ZOE-Dashboard.command / .sh"
echo "    O: $ZOE_HOME/venv/bin/python -m zoe.web_dashboard --backend pattern"
echo "    -> Abre http://localhost:8642 en tu navegador"
echo ""
echo -e "  ${CYAN}Consejos:${NC}"
echo "    * Escribe /help dentro de ZOE para ver comandos"
echo "    * Escribe /capsules para ver capsulas de conocimiento"
echo "    * Escribe /capsule elder_care_knowledge para cargar una"
echo "    * Escribe /quit para salir (guarda memoria automaticamente)"
echo ""

# Sprint 5.7 -- Fix Gatekeeper quarantine en macOS (los .command recien creados disparan warning)
if [ "$PLATFORM" = "Darwin" ]; then
    print_info "Eliminando atributo quarantine de los .command (Gatekeeper)..."
    xattr -dr com.apple.quarantine "$ZOE_HOME"/*.command 2>/dev/null || true
    print_ok "Scripts .command listos para doble clic sin warning"
fi

# Arrancar Dashboard ahora?
echo -n "  Arrancar Dashboard ahora? (s/N): "
read start_now

if [ "$start_now" = "s" ] || [ "$start_now" = "S" ]; then
    echo ""
    print_info "Arrancando Dashboard..."
    print_info "Abre http://localhost:8642 en tu navegador"
    echo ""
    
    # Determinar backend -- Sprint 5.7: usar --model auto si hay Ollama
    if [ "$OLLAMA_RUNNING" = true ]; then
        BACKEND="ollama"
        MODEL="--model auto"
    else
        BACKEND="pattern"
        MODEL=""
    fi
    
    cd "$ZOE_HOME/zoe"
    export OLLAMA_MODELS="$MODELS_DIR"
    # Sprint 5.7.1 -- Usar source en vez de xargs (xargs rompe API keys con =, /, etc.)
    if [ -f "$ENV_FILE" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
    fi
    
    # Sprint 5.12 GAP-Q: pasar --db-path al SSD para que el dashboard cargue el mismo ZOE
    "$ZOE_HOME/venv/bin/python" -m zoe.web_dashboard --backend $BACKEND $MODEL --db-path "${ZOE_DATA:-$ZOE_HOME/data}/dashboard_memory.db"
else
    echo ""
    echo -e "  ${GREEN}Para empezar mas tarde:${NC}"
    echo "    Doble clic en ZOE-Dashboard.command en tu SSD"
    echo ""
fi

echo ""
echo -e "  ${BOLD}${GREEN}Gracias por instalar ZOE!${NC}"
echo -e "  ZOE es un organismo cognitivo sintetico. No es un chatbot."
echo -e "  Tiene memoria, metabolismo e identidad propia."
echo -e "  Tratala como un companero, no como una herramienta."
echo ""
