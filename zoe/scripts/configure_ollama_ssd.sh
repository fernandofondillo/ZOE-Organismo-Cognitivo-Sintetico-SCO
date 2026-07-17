#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# ZOE v2.1.1 — Configuracion de Ollama para SSD Externo
# Configura Ollama para almacenar modelos en el SSD Crucial X9 en vez del
# disco interno del Mac. Esto libera espacio en el Mac y permite modelos
# grandes (hasta 85GB con el SSD de 1TB).
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

print_ok() { echo -e "${GREEN}  ✓ ${1}${NC}"; }
print_warn() { echo -e "${YELLOW}  ⚠ ${1}${NC}"; }
print_error() { echo -e "${RED}  ✗ ${1}${NC}"; }
print_step() { echo -e "${BLUE}  → ${1}${NC}"; }

# ── Detectar SSD ────────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "  ███████╗ ██████╗ ███████╗     ██████╗ ███████╗██╗     ███████╗████████╗ █████╗ "
echo "  ╚══███╔╝██╔═══██╗██╔════╝    ██╔═══██╗██╔════╝██║     ██╔════╝╚══██╔══╝██╔══██╗"
echo "    ███╔╝ ██║   ██║█████╗      ██║   ██║█████╗  ██║     █████╗     ██║   ███████║"
echo "   ███╔╝  ██║   ██║██╔══╝      ██║   ██║██╔══╝  ██║     ██╔══╝     ██║   ██╔══██║"
echo "  ███████╗╚██████╔╝███████╗    ╚██████╔╝██║     ███████╗███████╗   ██║   ██║  ██║"
echo "  ╚══════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝"
echo -e "${NC}"
echo -e "  ${BOLD}Configuracion de Ollama para SSD Externo${NC}"
echo ""

# Detectar SSD
SSD_CANDIDATES=()
for vol in /Volumes/*/; do
    volname=$(basename "$vol")
    [[ "$volname" == "Macintosh HD" ]] && continue
    size=$(df -h "$vol" 2>/dev/null | awk 'NR==2 {print $2}')
    SSD_CANDIDATES+=("$vol ($size)")
done

if [[ ${#SSD_CANDIDATES[@]} -eq 0 ]]; then
    print_error "No se detecto ningun SSD externo."
    echo "  Conecta el SSD Crucial X9 y vuelve a ejecutar."
    exit 1
fi

if [[ ${#SSD_CANDIDATES[@]} -eq 1 ]]; then
    SSD_PATH=$(echo "/Volumes/$(basename "$(ls -d /Volumes/*/ | head -1)" | tr -d '/')")
    print_ok "SSD detectado: ${SSD_CANDIDATES[0]}"
else
    echo -e "  ${BOLD}SSDs detectados:${NC}"
    for i in "${!SSD_CANDIDATES[@]}"; do
        echo "    [$((i+1))] ${SSD_CANDIDATES[$i]}"
    done
    echo -n "  Selecciona: "
    read CHOICE
    idx=$((CHOICE - 1))
    volname=$(basename "$(ls -d /Volumes/*/ | sed -n "$((idx+1))p")" | tr -d '/')
    SSD_PATH="/Volumes/$volname"
fi

# ── Verificar espacio ──────────────────────────────────────────────────────
FREE_GB=$(df -g "$SSD_PATH" 2>/dev/null | awk 'NR==2 {print $4}')
if [[ ${FREE_GB:-0} -lt 20 ]]; then
    print_warn "Espacio libre en SSD: ${FREE_GB}GB (recomendado: 20GB+)"
else
    print_ok "Espacio libre en SSD: ${FREE_GB}GB"
fi

# ── Crear directorio en SSD ────────────────────────────────────────────────
OLLAMA_SSD_DIR="$SSD_PATH/ZOE/models/ollama"
print_step "Creando directorio en SSD: $OLLAMA_SSD_DIR"
mkdir -p "$OLLAMA_SSD_DIR/manifests"
mkdir -p "$OLLAMA_SSD_DIR/blobs"
print_ok "Directorio creado"

# ── Backup y symlink ────────────────────────────────────────────────────────
print_step "Configurando symlink..."

ORIGINAL_DIR="$HOME/.ollama/models"
if [[ -d "$ORIGINAL_DIR" && ! -L "$ORIGINAL_DIR" ]]; then
    print_step "Haciendo backup del directorio original..."
    mv "$ORIGINAL_DIR" "$HOME/.ollama/models_backup_$(date +%Y%m%d_%H%M%S)"
    print_ok "Backup creado"
fi

if [[ -L "$ORIGINAL_DIR" ]]; then
    print_step "Eliminando symlink anterior..."
    rm "$ORIGINAL_DIR"
fi

ln -s "$OLLAMA_SSD_DIR" "$ORIGINAL_DIR"
print_ok "Symlink creado: ~/.ollama/models → $OLLAMA_SSD_DIR"

# ── Configurar variable de entorno ──────────────────────────────────────────
print_step "Configurando variable de entorno OLLAMA_MODELS..."

SHELL_RC="$HOME/.zshrc"
if [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

# Eliminar linea anterior si existe
grep -v "OLLAMA_MODELS=" "$SHELL_RC" > "$SHELL_RC.tmp" 2>/dev/null || true
mv "$SHELL_RC.tmp" "$SHELL_RC" 2>/dev/null || true

echo "" >> "$SHELL_RC"
echo "# ZOE v2.1.1 — Ollama models en SSD externo" >> "$SHELL_RC"
echo "export OLLAMA_MODELS=\"$OLLAMA_SSD_DIR\"" >> "$SHELL_RC"
print_ok "Variable OLLAMA_MODELS configurada en $SHELL_RC"

# ── Exportar para sesion actual ─────────────────────────────────────────────
export OLLAMA_MODELS="$OLLAMA_SSD_DIR"

# ── Verificar ────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}Verificacion:${NC}"
ls -la ~/.ollama/models 2>/dev/null | head -5

echo ""
echo -e "  ${BOLD}OLLAMA_MODELS=${OLLAMA_MODELS}${NC}"

# ── Iniciar Ollama si no esta corriendo ─────────────────────────────────────
print_step "Verificando Ollama..."
if ! pgrep -x "ollama" > /dev/null 2>&1; then
    print_step "Iniciando Ollama..."
    open -a Ollama
    sleep 3
fi

# Verificar que responde
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_ok "Ollama funcionando en localhost:11434"
else
    print_warn "Ollama no responde todavia. Puede tardar unos segundos en iniciar."
fi

# ── Modelos recomendados segun RAM ──────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${BOLD}Modelos recomendados segun tu RAM:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

RAM_GB=$(sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1024/1024/1024)}')
echo -e "  RAM detectada: ${BOLD}${RAM_GB}GB${NC}"
echo ""

if [[ ${RAM_GB:-8} -le 8 ]]; then
    echo -e "  ${YELLOW}⚠ RAM limitada (8GB). Recomendacion:${NC}"
    echo -e "  • L1 (simples):     gemma-2-9b-iq2        ${GREEN}(3.5GB — comodo)${NC}"
    echo -e "  • L2 (estandar):    qwen2.5:14b-iq2       ${GREEN}(6GB — ajustado)${NC}"
    echo -e "  • L3 (profundo):    qwq-32b-iq2           ${YELLOW}(12.5GB — lento por swap)${NC}"
    echo -e "  • L4 (reflexion):   deepseek-r1:32b-iq2   ${YELLOW}(12.5GB — lento pero funciona)${NC}"
    echo -e "  • ${RED}EVITAR:${NC} deepseek-r1:32b-q4km (18GB — imposible con 8GB)"
    echo ""
    echo -e "  ${CYAN}💡 Tip: Si ves que ZOE va muy lenta, reduce a modelos mas pequenos${NC}"
    echo -e "     en el Dashboard → Configuracion → Modelos locales"
elif [[ ${RAM_GB:-0} -le 16 ]]; then
    echo -e "  ${GREEN}✓ RAM buena (16GB). Puedes usar casi todos los modelos:${NC}"
    echo -e "  • L1-L3: Todos los modelos IQ2_M (hasta 12.5GB)"
    echo -e "  • L4 (reflexion): deepseek-r1:32b-q4km  ${GREEN}(18GB — funciona)${NC}"
    echo -e "  • Maximo: qwen2.5:72b-iq2               ${YELLOW}(25GB — algo de swap)${NC}"
else
    echo -e "  ${GREEN}✓ RAM excelente (16GB+). Todos los modelos disponibles:${NC}"
    echo -e "  • Todos los modelos IQ2_M y Q4_K_M"
    echo -e "  • Incluso multiples modelos simultaneamente"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Ollama configurado para SSD externo                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Proximos pasos:${NC}"
echo -e "  1. Cierra y abre Terminal (o ejecuta: source $SHELL_RC)"
echo -e "  2. Descarga modelos: ollama pull gemma2:9b"
echo -e "  3. Inicia ZOE: doble click en INICIAR-ZOE.command"
echo ""
echo -e "  ${BOLD}Para verificar que funciona:${NC}"
echo -e "  ollama list              # Ver modelos instalados"
echo -e "  ollama run gemma2:9b     # Probar modelo"
echo ""
