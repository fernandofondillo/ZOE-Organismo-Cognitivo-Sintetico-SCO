#!/bin/bash
# ============================================================
# ZOE — Gestor de Modelos Grandes en Pendrive (macOS)
# ============================================================
# Permite usar modelos de 14B-72B parámetros desde un pendrive
# en un Mac con solo 8GB RAM, usando memory-mapped loading (mmap).
#
# El modelo vive en el pendrive. llama.cpp (motor de Ollama) lo
# memory-mapea: solo carga en RAM las capas activas (~2-4GB),
# el resto se queda en el pendrive hasta que se necesita.
#
# Uso:
#   bash zoe_large_model_manager.sh
# ============================================================

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ZOE — Gestor de Modelos Grandes en Pendrive             ║${NC}"
echo -e "${BLUE}║  Cognitive Memory Paging para Mac con 8GB RAM            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detectar ZOE_HOME
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    ZOE_HOME="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/zoe" ] && [ -f "$SCRIPT_DIR/ZOE-Chat.command" ]; then
    ZOE_HOME="$SCRIPT_DIR"
else
    # Buscar en /Volumes
    for vol in /Volumes/*/ZOE; do
        if [ -f "$vol/venv/bin/activate" ]; then
            ZOE_HOME="$vol"
            break
        fi
    done
fi

if [ -z "$ZOE_HOME" ]; then
    echo -e "${RED}❌ No se encontró instalación de ZOE en el pendrive.${NC}"
    echo "   Ejecuta primero install_pendrive_macos.sh"
    exit 1
fi

echo -e "${GREEN}✅ ZOE_HOME: $ZOE_HOME${NC}"
echo ""

# Activar entorno
cd "$ZOE_HOME/zoe"
source "$ZOE_HOME/venv/bin/activate"

# Detectar RAM
echo -e "${YELLOW}📊 Detectando hardware...${NC}"
TOTAL_RAM=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%.1f", $1/1073741824}')
CHIP=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Desconocido")
CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "?")
echo "   Chip: $CHIP"
echo "   RAM total: ${TOTAL_RAM}GB"
echo "   Cores: $CORES"
echo ""

# Calcular RAM disponible (aproximadamente 60% del total)
AVAIL_RAM=$(echo "$TOTAL_RAM * 0.6" | bc -l | awk '{printf "%.1f", $0}')
echo "   RAM disponible estimada: ${AVAIL_RAM}GB"
echo ""

# Menú de modelos
echo -e "${YELLOW}🤖 Selecciona modelo a instalar en el pendrive:${NC}"
echo ""
echo "  MODELOS PEQUEÑOS (caben en RAM, rápidos):"
echo "   1. Qwen 2.5 0.5B  (~0.5GB)  — Ultra rápido, básico"
echo "   2. Qwen 2.5 1.5B  (~1.2GB)  — Rápido, decente"
echo "   3. Qwen 2.5 3B    (~2.0GB)  — Rápido, bueno para L0-L1"
echo ""
echo "  MODELOS MEDIOS (caben en RAM, buen balance):"
echo "   4. Qwen 2.5 7B    (~4.5GB)  — Bueno para L2"
echo "   5. Llama 3.1 8B   (~4.9GB)  — Alternativa L2"
echo "   6. DeepSeek R1 7B (~4.5GB)  — Razonamiento L2"
echo ""
echo "  MODELOS GRANDES (vía mmap desde pendrive, lentos pero potentes):"
echo "   7. Qwen 2.5 14B   (~8GB)    — L3 profundo ⚠️ mmap parcial"
echo "   8. DeepSeek R1 14B(~8GB)    — L3 razonamiento ⚠️ mmap parcial"
echo "   9. Phi-4 14B      (~8GB)    — L3 Microsoft ⚠️ mmap parcial"
echo "  10. Gemma2 27B     (~16GB)   — L3 Google ⚠️ mmap completo"
echo "  11. Qwen 2.5 32B   (~18GB)   — L3 muy profundo ⚠️ mmap completo"
echo "  12. DeepSeek R1 32B(~18GB)   — L3 razonamiento avanzado ⚠️ mmap completo"
echo ""
echo "  MODELOS ENORMES (mmap completo, muy lentos):"
echo "  13. Llama 3.1 70B  (~40GB)   — Máxima calidad local ⚠️ MUY lento"
echo "  14. Qwen 2.5 72B   (~40GB)   — Máxima calidad local ⚠️ MUY lento"
echo ""
echo -n "Selecciona [1-14]: "
read MODEL_CHOICE

case $MODEL_CHOICE in
    1) MODEL="qwen2.5:0.5b"; SIZE_GB=0.5; LEVEL="L0" ;;
    2) MODEL="qwen2.5:1.5b"; SIZE_GB=1.2; LEVEL="L0-L1" ;;
    3) MODEL="qwen2.5:3b"; SIZE_GB=2.0; LEVEL="L0-L1" ;;
    4) MODEL="qwen2.5:7b"; SIZE_GB=4.5; LEVEL="L2" ;;
    5) MODEL="llama3.1:8b"; SIZE_GB=4.9; LEVEL="L2" ;;
    6) MODEL="deepseek-r1:7b"; SIZE_GB=4.5; LEVEL="L2" ;;
    7) MODEL="qwen2.5:14b"; SIZE_GB=8.0; LEVEL="L3" ;;
    8) MODEL="deepseek-r1:14b"; SIZE_GB=8.0; LEVEL="L3" ;;
    9) MODEL="phi4:14b"; SIZE_GB=8.0; LEVEL="L3" ;;
    10) MODEL="gemma2:27b"; SIZE_GB=16.0; LEVEL="L3" ;;
    11) MODEL="qwen2.5:32b"; SIZE_GB=18.0; LEVEL="L3" ;;
    12) MODEL="deepseek-r1:32b"; SIZE_GB=18.0; LEVEL="L3" ;;
    13) MODEL="llama3.1:70b"; SIZE_GB=40.0; LEVEL="L3" ;;
    14) MODEL="qwen2.5:72b"; SIZE_GB=40.0; LEVEL="L3" ;;
    *) echo -e "${RED}❌ Opción inválida${NC}"; exit 1 ;;
esac

echo ""
echo -e "${YELLOW}📦 Modelo seleccionado: $MODEL (${SIZE_GB}GB)${NC}"
echo "   Nivel ACD recomendado: $LEVEL"
echo ""

# Analizar viabilidad
AVAIL_NUM=$(echo "$AVAIL_RAM" | awk '{print $1+0}')
SIZE_NUM=$SIZE_GB

if [ $(echo "$SIZE_NUM <= $AVAIL_NUM * 0.8" | bc -l) -eq 1 ]; then
    STRATEGY="full_ram"
    SPEED="rápido"
    echo -e "${GREEN}✅ Estrategia: Carga completa en RAM${NC}"
    echo "   El modelo cabe en tu RAM. Velocidad: $SPEED"
elif [ $(echo "$SIZE_NUM <= $AVAIL_NUM * 2.5" | bc -l) -eq 1 ]; then
    STRATEGY="mmap_partial"
    SPEED="medio"
    echo -e "${YELLOW}⚠️  Estrategia: Memory-mapped loading parcial${NC}"
    echo "   El modelo NO cabe entero en RAM (${SIZE_GB}GB vs ${AVAIL_RAM}GB disponibles)."
    echo "   Se usará mmap: solo las capas activas se cargan en RAM."
    echo "   Velocidad: $SPEED (más lento que en RAM pero funcional)"
elif [ $(echo "$SIZE_NUM <= $AVAIL_NUM * 10" | bc -l) -eq 1 ]; then
    STRATEGY="mmap_full"
    SPEED="lento"
    echo -e "${YELLOW}⚠️  Estrategia: Memory-mapped loading completo desde pendrive${NC}"
    echo "   El modelo es ${SIZE_NUM}GB pero tu RAM disponible es ${AVAIL_RAM}GB."
    echo "   mmap paginará las capas desde el pendrive bajo demanda."
    echo "   Solo ~3-4GB de RAM se usarán. El resto vive en el pendrive."
    echo "   Velocidad: $SPEED (significativamente más lento, pero FUNCIONA)"
    echo ""
    echo -e "${YELLOW}   ⏱️ Tiempo estimado por respuesta L3: 30-120 segundos${NC}"
    echo -e "${YELLOW}   💡 Para respuestas rápidas, usa un modelo pequeño (3B) para L0-L1${NC}"
else
    echo -e "${RED}❌ Este modelo es demasiado grande incluso para mmap.${NC}"
    echo "   Usa cloud API (OpenAI, Anthropic, DeepSeek) para L3."
    exit 0
fi
echo ""

# Verificar espacio en pendrive
echo -e "${YELLOW}📏 Verificando espacio en pendrive...${NC}"
FREE_SPACE=$(df -h "$ZOE_HOME" | tail -1 | awk '{print $4}')
echo "   Espacio libre: $FREE_SPACE"
echo ""

# Configurar OLLAMA_MODELS
export OLLAMA_MODELS="$ZOE_HOME/models"
mkdir -p "$OLLAMA_MODELS"
echo -e "${GREEN}   Modelos se guardarán en: $OLLAMA_MODELS${NC}"
echo ""

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama no instalado en este Mac.${NC}"
    echo "   Instala desde https://ollama.ai (solo ~50MB en el Mac)"
    exit 1
fi

# Iniciar Ollama si no está corriendo
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}🔧 Iniciando Ollama...${NC}"
    ollama serve &> /dev/null &
    sleep 3
fi

# Descargar modelo
echo -e "${YELLOW}📥 Descargando $MODEL (${SIZE_GB}GB) al pendrive...${NC}"
echo "   Esto puede tardar varios minutos según tu conexión USB."
echo "   El modelo se guarda en el pendrive, NO en el Mac."
echo ""
ollama pull "$MODEL"
echo ""
echo -e "${GREEN}✅ Modelo $MODEL descargado en el pendrive${NC}"
echo ""

# Configurar variables de entorno óptimas
echo -e "${YELLOW}⚙️ Configurando variables de entorno óptimas...${NC}"

# Crear/actualizar .env con configuración Ollama
ENV_FILE="$ZOE_HOME/data/.ollama_env"
cat > "$ENV_FILE" << EOF
# Configuración Ollama para $MODEL ($STRATEGY)
export OLLAMA_MODELS="$OLLAMA_MODELS"
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
EOF

if [ "$STRATEGY" = "mmap_partial" ]; then
    echo 'export OLLAMA_KEEP_ALIVE=30m' >> "$ENV_FILE"
elif [ "$STRATEGY" = "mmap_full" ]; then
    echo 'export OLLAMA_KEEP_ALIVE=60m' >> "$ENV_FILE"
    echo 'export OLLAMA_FLASH_ATTENTION=1' >> "$ENV_FILE"
fi

echo -e "${GREEN}✅ Configuración guardada en $ENV_FILE${NC}"
echo ""

# Crear script lanzador para este modelo
LAUNCHER="$ZOE_HOME/ZOE-Chat-$MODEL.command"
cat > "$LAUNCHER" << EOF
#!/bin/bash
ZOE_HOME="$ZOE_HOME"
cd "\$ZOE_HOME/zoe"
source "\$ZOE_HOME/venv/bin/activate"
# Cargar configuración Ollama óptima
source "\$ZOE_HOME/data/.ollama_env"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Chat CLI ($MODEL)"
echo "║  Estrategia: $STRATEGY | Velocidad: $SPEED"
echo "╚══════════════════════════════════════════════════════════╝"
# Iniciar Ollama si no está corriendo
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
python -m zoe.cli_chat --backend ollama --model $MODEL --db-path "\$ZOE_HOME/data/zoe_memory.db"
EOF
chmod +x "$LAUNCHER"

# Crear también para Dashboard
LAUNCHER_DASH="$ZOE_HOME/ZOE-Dashboard-$MODEL.command"
cat > "$LAUNCHER_DASH" << EOF
#!/bin/bash
ZOE_HOME="$ZOE_HOME"
cd "\$ZOE_HOME/zoe"
source "\$ZOE_HOME/venv/bin/activate"
source "\$ZOE_HOME/data/.ollama_env"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ZOE — Dashboard ($MODEL)"
echo "║  Estrategia: $STRATEGY | Velocidad: $SPEED"
echo "╚══════════════════════════════════════════════════════════╝"
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &> /dev/null &
    sleep 3
fi
echo "Abre: http://localhost:8642"
python -m zoe.web_dashboard --backend ollama --model $MODEL
EOF
chmod +x "$LAUNCHER_DASH"

echo -e "${GREEN}✅ Scripts creados:${NC}"
echo "   • $(basename "$LAUNCHER")      → Chat con $MODEL"
echo "   • $(basename "$LAUNCHER_DASH") → Dashboard con $MODEL"
echo ""

# Resumen
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ MODELO INSTALADO                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📋 Resumen:"
echo "   Modelo: $MODEL (${SIZE_GB}GB en pendrive)"
echo "   Estrategia: $STRATEGY"
echo "   Velocidad: $SPEED"
echo "   RAM usada: ~$(echo "$AVAIL_RAM * 0.7" | bc -l | awk '{printf "%.1f", $0}')GB de ${AVAIL_RAM}GB disponibles"
echo "   Nivel ACD: $LEVEL"
echo ""
echo "🚀 Para usar:"
echo "   Doble clic en $(basename "$LAUNCHER") (Chat)"
echo "   Doble clic en $(basename "$LAUNCHER_DASH") (Dashboard)"
echo ""
if [ "$STRATEGY" != "full_ram" ]; then
    echo "💡 Tip: La primera respuesta puede tardar más (cargando capas)."
    echo "   Las siguientes serán más rápidas (capas ya en RAM)."
    echo ""
    echo "💡 Para máxima velocidad en L0-L1, instala también un modelo pequeño:"
    echo "   bash $(basename "$0") → selecciona opción 3 (Qwen 2.5 3B)"
fi
echo ""
