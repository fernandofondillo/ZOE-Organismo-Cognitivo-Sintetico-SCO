#!/bin/bash
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ZOE — Instalador para Pendrive (macOS)                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
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
echo -e "${YELLOW}📁 Creando $ZOE_HOME...${NC}"
mkdir -p "$ZOE_HOME"
echo -e "${YELLOW}🐍 Verificando Python...${NC}"
PYTHON=$(command -v python3 || command -v python)
$PYTHON -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null || { echo -e "${RED}❌ Python 3.10+ requerido${NC}"; exit 1; }
echo -e "${GREEN}✅ $($PYTHON --version)${NC}"
echo -e "${YELLOW}📥 Clonando repositorio...${NC}"
cd "$ZOE_HOME"; git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git zoe
echo -e "${YELLOW}🏗️ Creando entorno virtual en el pendrive...${NC}"
$PYTHON -m venv "$ZOE_HOME/venv"
source "$ZOE_HOME/venv/bin/activate"
echo -e "${YELLOW}📚 Instalando dependencias...${NC}"
cd zoe; pip install --upgrade pip -q; pip install -e . -q
echo -e "${YELLOW}💾 Creando directorio de datos...${NC}"
mkdir -p "$ZOE_HOME/data"
echo -e "${YELLOW}🚀 Creando scripts lanzadores...${NC}"
cat > "$ZOE_HOME/ZOE-Chat.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI                                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
python -m zoe.cli_chat --backend mock --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat.command"
cat > "$ZOE_HOME/ZOE-Chat-Ollama.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI (Ollama)                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b --db-path "$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$ZOE_HOME/ZOE-Chat-Ollama.command"
cat > "$ZOE_HOME/ZOE-Dashboard.command" << 'EOF'
#!/bin/bash
ZOE_HOME="$(dirname "$0")"; cd "$ZOE_HOME/zoe"; source "$ZOE_HOME/venv/bin/activate"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Web Dashboard                                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "Abre: http://localhost:8642"
python -m zoe.web_dashboard --backend mock
EOF
chmod +x "$ZOE_HOME/ZOE-Dashboard.command"
echo -e "${GREEN}✅ Scripts creados${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ INSTALACIÓN COMPLETA                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "ZOE está en: $ZOE_HOME"
echo ""
echo "📋 Cómo usar:"
echo "  Doble clic en el pendrive → ZOE-Chat.command"
echo "  O desde Terminal: cd $ZOE_HOME/zoe && source ../venv/bin/activate && python -m zoe.cli_chat --backend mock"
echo ""
echo "💾 Datos en: $ZOE_HOME/data/"
echo "🔌 Antes de desconectar: /quit en el chat"
echo "📦 Actualizar: cd $ZOE_HOME/zoe && git pull && pip install -e ."
