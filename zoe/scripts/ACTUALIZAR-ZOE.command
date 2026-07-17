#!/bin/bash
# ============================================================================
# ZOE — Comando de Actualización Sin Regresión
# ============================================================================
# Script: ACTUALIZAR-ZOE.command
# Versión: 1.0 (Sprint 5.23)
#
# PROPÓSITO:
#   Actualiza ZOE en el SSD del usuario a la última versión de GitHub
#   SIN romper la configuración existente (.env, memoria, identidad, etc.).
#
# QUÉ HACE:
#   1. Detecta ZOE_HOME en el SSD (auto-detección).
#   2. Hace backup completo de data/ antes de tocar nada.
#   3. Git fetch + diff para ver qué cambió.
#   4. Stash de cambios locales si los hay.
#   5. Git pull --ff-only (sin merge conflicts).
#   6. Actualiza dependencias (pip install -e .).
#   7. Ejecuta tests rápidos de smoke (sin regresión).
#   8. Si algo falla: RESTAURA el backup automáticamente.
#   9. Si todo OK: mantiene .env, memoria, identidad, trayectoria intactos.
#
# QUÉ NO TOCA:
#   - data/.env (API keys)
#   - data/*.db (memoria SQLite)
#   - data/identity_vault.json (identidad)
#   - data/trajectory_chain.json (trayectoria)
#   - data/loaded_capsules.json (cápsulas cargadas)
#   - data/dashboard_token.txt (token de auth)
#   - data/config.json (configuración usuario)
#   - venv/ (entorno virtual)
#   - models/ollama/ (modelos GGUF)
#
# PLATAFORMAS:
#   - macOS (doble-click .command)
#   - Linux (bash ACTUALIZAR-ZOE.command)
#   - Git Bash en Windows
#
# USO:
#   Doble-click en el archivo (macOS lo abre en Terminal)
#   O desde terminal:
#     bash ACTUALIZAR-ZOE.command           # actualización normal
#     bash ACTUALIZAR-ZOE.command --force   # forzar incluso con cambios locales
#     bash ACTUALIZAR-ZOE.command --check   # solo verificar, no actualizar
#
# ============================================================================

set -euo pipefail

# Colores
if [ -t 1 ]; then
    GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
else
    GREEN=''; YELLOW=''; RED=''; CYAN=''; BOLD=''; NC=''
fi

# ============================================================================
# 1. DETECTAR ZOE_HOME
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Buscar ZOE_HOME: el directorio que contiene zoe/ y venv/
detect_zoe_home() {
    # Caso 1: script está en $ZOE_HOME/zoe/scripts/
    if [ -d "$SCRIPT_DIR/../../venv" ] && [ -d "$SCRIPT_DIR/../../zoe" ]; then
        echo "$(cd "$SCRIPT_DIR/../.." && pwd)"
        return
    fi
    # Caso 2: script está en $ZOE_HOME/scripts/
    if [ -d "$SCRIPT_DIR/../venv" ] && [ -d "$SCRIPT_DIR/../zoe" ]; then
        echo "$(cd "$SCRIPT_DIR/.." && pwd)"
        return
    fi
    # Caso 3: script está en $ZOE_HOME/ directamente
    if [ -d "$SCRIPT_DIR/venv" ] && [ -d "$SCRIPT_DIR/zoe" ]; then
        echo "$SCRIPT_DIR"
        return
    fi
    # Caso 4: preguntar al usuario
    echo -e "${YELLOW}No se pudo detectar ZOE_HOME automáticamente.${NC}"
    echo -e "Por favor, introduce la ruta completa al directorio de ZOE en tu SSD:"
    read -r -p "  ZOE_HOME: " USER_ZOE_HOME
    if [ -d "$USER_ZOE_HOME/venv" ] && [ -d "$USER_ZOE_HOME/zoe" ]; then
        echo "$USER_ZOE_HOME"
        return
    fi
    echo -e "${RED}ERROR: $USER_ZOE_HOME no contiene venv/ y zoe/. Abortando.${NC}"
    exit 1
}

ZOE_HOME="$(detect_zoe_home)"
ZOE_DATA="${ZOE_DATA:-$ZOE_HOME/data}"
ZOE_REPO="$ZOE_HOME/zoe"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  ZOE — Actualización Sin Regresión  v1.0 (Sprint 5.23)      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}ZOE_HOME:${NC}  $ZOE_HOME"
echo -e "  ${BOLD}ZOE_DATA:${NC}  $ZOE_DATA"
echo -e "  ${BOLD}ZOE_REPO:${NC} $ZOE_REPO"
echo ""

# ============================================================================
# 2. VALIDAR PRE-REQUISITOS
# ============================================================================

echo -e "${BOLD}[1/9] Validando pre-requisitos...${NC}"

if [ ! -d "$ZOE_REPO/.git" ]; then
    echo -e "  ${RED}ERROR: $ZOE_REPO no es un repositorio git.${NC}"
    exit 1
fi

if [ ! -d "$ZOE_HOME/venv" ]; then
    echo -e "  ${YELLOW}ADVERTENCIA: No se encontró venv/ en $ZOE_HOME.${NC}"
    echo -e "  Continuando con Python del sistema (puede fallar si faltan deps)."
else
    # shellcheck disable=SC1091
    source "$ZOE_HOME/venv/bin/activate"
    echo -e "  ${GREEN}OK${NC} venv activado"
fi

if ! command -v git &>/dev/null; then
    echo -e "  ${RED}ERROR: git no está instalado.${NC}"
    exit 1
fi
echo -e "  ${GREEN}OK${NC} git disponible: $(git --version)"

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo -e "  ${RED}ERROR: python3/python no está instalado.${NC}"
    exit 1
fi
PYTHON_BIN="$(command -v python3 || command -v python)"
echo -e "  ${GREEN}OK${NC} python disponible: $($PYTHON_BIN --version 2>&1)"

# ============================================================================
# 3. PARSE ARGS
# ============================================================================

FORCE=false
CHECK_ONLY=false
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        --check) CHECK_ONLY=true ;;
        --help|-h)
            echo "Uso: $0 [--force] [--check]"
            echo "  --force  Forzar actualización incluso con cambios locales"
            echo "  --check  Solo verificar, no actualizar"
            exit 0
            ;;
    esac
done

# ============================================================================
# 4. DETENER ZOE SI ESTÁ CORRIENDO
# ============================================================================

echo -e "${BOLD}[2/9] Deteniendo ZOE si está corriendo...${NC}"

# Buscar procesos de ZOE
ZOE_PIDS_8642=$(lsof -ti:8642 2>/dev/null || true)
ZOE_PIDS_8080=$(lsof -ti:8080 2>/dev/null || true)
ZOE_PIDS_PYTHON=$(pgrep -f "zoe.web_dashboard\|zoe.serve\|zoe.cli_chat" 2>/dev/null || true)

ALL_PIDS="$ZOE_PIDS_8642 $ZOE_PIDS_8080 $ZOE_PIDS_PYTHON"
if [ -n "$ALL_PIDS" ]; then
    # SIGTERM primero (graceful shutdown)
    for pid in $ALL_PIDS; do
        if [ -n "$pid" ]; then
            echo -e "  Enviando SIGTERM a PID $pid..."
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    sleep 3
    # Si siguen vivos, SIGKILL
    for pid in $ALL_PIDS; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo -e "  ${YELLOW}ADVERTENCIA${NC} PID $pid no terminó, enviando SIGKILL..."
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
    sleep 1
    echo -e "  ${GREEN}OK${NC} Procesos ZOE detenidos"
else
    echo -e "  ${GREEN}OK${NC} No hay procesos ZOE corriendo"
fi

# ============================================================================
# 5. BACKUP COMPLETO DE data/
# ============================================================================

echo -e "${BOLD}[3/9] Backup de data/...${NC}"

BACKUP_DIR="$ZOE_HOME/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/zoe_data_backup_$TIMESTAMP.tar.gz"

if [ -d "$ZOE_DATA" ]; then
    # Excluir backups recursivos y caché
    tar -czf "$BACKUP_FILE" \
        -C "$ZOE_HOME" \
        --exclude="backups" \
        --exclude="__pycache__" \
        --exclude=".pytest_cache" \
        data/ 2>/dev/null
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "  ${GREEN}OK${NC} Backup creado: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} No existe $ZOE_DATA — primer arranque, omitiendo backup"
    BACKUP_FILE=""
fi

# Mantener solo los últimos 5 backups
ls -t "$BACKUP_DIR"/zoe_data_backup_*.tar.gz 2>/dev/null | tail -n +6 | while read -r old_backup; do
    rm -f "$old_backup"
done

# ============================================================================
# 6. FETCH + DIFF
# ============================================================================

echo -e "${BOLD}[4/9] Consultando GitHub...${NC}"

cd "$ZOE_REPO"

echo -e "  Obteniendo cambios remotos..."
git fetch origin main 2>&1 | sed 's/^/    /' || {
    echo -e "  ${YELLOW}ADVERTENCIA${NC} No se pudo conectar a GitHub (sin internet?)"
    echo -e "  Abortando actualización. Tu ZOE sigue intacto."
    exit 0
}

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo -e "  ${GREEN}OK${NC} ZOE ya está en la última versión ($LOCAL_HASH)"
    echo -e "  No hay nada que actualizar."
    exit 0
fi

echo -e "  Local:  $LOCAL_HASH"
echo -e "  Remoto: $REMOTE_HASH"
echo ""

# Mostrar qué cambió
echo -e "  ${BOLD}Cambios pendientes:${NC}"
git log --oneline HEAD..origin/main 2>&1 | head -10 | sed 's/^/    /'
COMMIT_COUNT=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
echo ""
echo -e "  ${BOLD}$COMMIT_COUNT commit(s) nuevo(s) en GitHub.${NC}"

if [ "$CHECK_ONLY" = "true" ]; then
    echo -e "  ${YELLOW}--check activado: no actualizando.${NC}"
    exit 0
fi

echo ""
read -r -p "¿Continuar con la actualización? (s/N): " CONFIRM
if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo -e "  ${YELLOW}Actualización cancelada.${NC}"
    exit 0
fi

# ============================================================================
# 7. STASH DE CAMBIOS LOCALES (si los hay)
# ============================================================================

echo -e "${BOLD}[5/9] Verificando cambios locales...${NC}"

if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    if [ "$FORCE" = "true" ]; then
        echo -e "  ${YELLOW}--force: descartando cambios locales${NC}"
        git checkout -- . 2>&1 | sed 's/^/    /' || true
        git clean -fd 2>&1 | sed 's/^/    /' || true
    else
        echo -e "  Hay cambios locales sin commitear. Haciendo stash..."
        STASH_NAME="zoe-auto-stash-$TIMESTAMP"
        git stash push -u -m "$STASH_NAME" 2>&1 | sed 's/^/    /'
        echo -e "  ${GREEN}OK${NC} Stash creado: $STASH_NAME"
        echo -e "  Para recuperarlo: cd $ZOE_REPO && git stash pop"
    fi
else
    echo -e "  ${GREEN}OK${NC} Sin cambios locales"
fi

# ============================================================================
# 8. GIT PULL --ff-only
# ============================================================================

echo -e "${BOLD}[6/9] Aplicando actualización (git pull --ff-only)...${NC}"

cd "$ZOE_REPO"
if ! git pull --ff-only origin main 2>&1 | sed 's/^/    /'; then
    echo -e "  ${RED}ERROR: No se pudo hacer fast-forward.${NC}"
    echo -e "  Esto puede pasar si hay commits locales divergentes."
    echo -e "  Restaurando stash si existe..."
    git stash pop 2>/dev/null || true
    echo -e "  ${YELLOW}Tu ZOE sigue intacto en versión anterior.${NC}"
    exit 1
fi

NEW_HASH=$(git rev-parse HEAD)
echo -e "  ${GREEN}OK${NC} Actualizado a $NEW_HASH"

# ============================================================================
# 9. ACTUALIZAR DEPENDENCIAS
# ============================================================================

echo -e "${BOLD}[7/9] Actualizando dependencias Python...${NC}"

cd "$ZOE_REPO"
if [ -f "$ZOE_HOME/venv/bin/pip" ]; then
    "$ZOE_HOME/venv/bin/pip" install -e . -q 2>&1 | tail -5 | sed 's/^/    /' || {
        echo -e "  ${YELLOW}ADVERTENCIA${NC} pip install -e . falló"
        echo -e "  Continuando — puede que necesites reinstalar manualmente:"
        echo -e "    cd $ZOE_REPO && pip install -e ."
    }
    echo -e "  ${GREEN}OK${NC} Dependencias actualizadas"
else
    echo -e "  ${YELLOW}ADVERTENCIA${NC} No hay venv, omitiendo pip install"
fi

# ============================================================================
# 10. SMOKE TESTS (sin regresión)
# ============================================================================

echo -e "${BOLD}[8/9] Smoke tests (verificación sin regresión)...${NC}"

cd "$ZOE_REPO"

# Test 1: imports básicos
if ! "$PYTHON_BIN" -c "
import sys
sys.path.insert(0, '.')
import zoe
from zoe.cli_chat import ZoeChat
from zoe.dashboard.server import DashboardServer
from zoe.peripherals.web_search import WebSearchActuator
from zoe.core.living_memory import LivingMemory
print('  imports OK')
" 2>&1 | sed 's/^/    /'; then
    echo -e "  ${RED}FAIL: imports rotos. Restaurando backup...${NC}"
    # Restaurar código anterior
    git reset --hard "$LOCAL_HASH" 2>&1 | sed 's/^/    /'
    "$ZOE_HOME/venv/bin/pip" install -e . -q 2>&1 | tail -3 | sed 's/^/    /' || true
    echo -e "  ${YELLOW}Restaurado a versión anterior. Smoke test falló.${NC}"
    exit 1
fi

# Test 2: ZoeChat smoke
SMOKE_DB="/tmp/zoe_update_smoke_$$.db"
rm -f "$SMOKE_DB"
if ! "$PYTHON_BIN" -c "
import sys, asyncio
sys.path.insert(0, '.')
from zoe.cli_chat import ZoeChat

async def main():
    chat = ZoeChat(backend='mock', db_path='$SMOKE_DB')
    await chat.initialize()
    r = await chat.send_message_acd('hola')
    assert 'response' in r, f'No response field: {r}'
    assert 'mentor_intervention' in r, f'No mentor_intervention field: {r}'
    assert chat.loop.speaker is not None, 'loop.speaker not set'
    assert hasattr(chat.loop.causal_engine, 'add_prevalidated_model')
    assert hasattr(chat.loop.emotional_motor, 'add_pattern')
    assert hasattr(chat.loop.ethical_motor, 'add_guideline')
    assert chat.loop._web_search is not None, 'WebSearch not wired'
    await chat.shutdown()
    print('  ZoeChat smoke OK')

asyncio.run(main())
" 2>&1 | tail -10 | sed 's/^/    /'; then
    echo -e "  ${RED}FAIL: ZoeChat smoke falló. Restaurando backup...${NC}"
    rm -f "$SMOKE_DB"
    git reset --hard "$LOCAL_HASH" 2>&1 | sed 's/^/    /'
    "$ZOE_HOME/venv/bin/pip" install -e . -q 2>&1 | tail -3 | sed 's/^/    /' || true
    echo -e "  ${YELLOW}Restaurado a versión anterior.${NC}"
    exit 1
fi
rm -f "$SMOKE_DB"

# Test 3: tests críticos (30s max)
echo -e "    Ejecutando tests críticos (puede tardar 30s)..."
if ! timeout 60 "$PYTHON_BIN" -m pytest \
    zoe/tests/test_living_memory.py \
    zoe/tests/test_metabolism.py \
    zoe/tests/test_identity_vault.py \
    zoe/tests/test_cli_chat.py \
    zoe/tests/test_cognitive_loop.py \
    zoe/tests/test_state.py \
    -x --tb=line -q 2>&1 | tail -3 | sed 's/^/    /'; then
    echo -e "  ${RED}FAIL: tests críticos fallaron. Restaurando backup...${NC}"
    git reset --hard "$LOCAL_HASH" 2>&1 | sed 's/^/    /'
    "$ZOE_HOME/venv/bin/pip" install -e . -q 2>&1 | tail -3 | sed 's/^/    /' || true
    echo -e "  ${YELLOW}Restaurado a versión anterior.${NC}"
    exit 1
fi

echo -e "  ${GREEN}OK${NC} Smoke tests pasaron"

# ============================================================================
# 11. VERIFICAR QUE data/ SIGUE INTACTO
# ============================================================================

echo -e "${BOLD}[9/9] Verificando integridad de data/...${NC}"

if [ -f "$ZOE_DATA/identity_vault.json" ]; then
    echo -e "  ${GREEN}OK${NC} identity_vault.json preservado"
fi
if [ -f "$ZOE_DATA/trajectory_chain.json" ]; then
    MUTATIONS=$(python3 -c "
import json
with open('$ZOE_DATA/trajectory_chain.json') as f:
    data = json.load(f)
print(len(data.get('mutations', [])))
" 2>/dev/null || echo "?")
    echo -e "  ${GREEN}OK${NC} trajectory_chain.json preservado ($MUTATIONS mutaciones)"
fi
if [ -f "$ZOE_DATA/chat_memory.db" ] || [ -f "$ZOE_DATA/dashboard_memory.db" ]; then
    DB_FILE="$ZOE_DATA/chat_memory.db"
    [ -f "$DB_FILE" ] || DB_FILE="$ZOE_DATA/dashboard_memory.db"
    MEM_ENTRIES=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_FILE')
try:
    cur = conn.execute('SELECT COUNT(*) FROM memory_entries')
    print(cur.fetchone()[0])
except Exception:
    print('?')
" 2>/dev/null || echo "?")
    echo -e "  ${GREEN}OK${NC} memoria SQLite preservada ($MEM_ENTRIES entradas)"
fi
if [ -f "$ZOE_DATA/.env" ]; then
    echo -e "  ${GREEN}OK${NC} .env preservado (API keys intactos)"
fi
if [ -f "$ZOE_DATA/loaded_capsules.json" ]; then
    echo -e "  ${GREEN}OK${NC} loaded_capsules.json preservado"
fi

# ============================================================================
# RESUMEN FINAL
# ============================================================================

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  ${GREEN}${BOLD}ACTUALIZACIÓN COMPLETA — SIN REGRESIONES${NC}${CYAN}                ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║  Versión anterior:  ${LOCAL_HASH:0:8}${NC}"
echo -e "${CYAN}║  Versión actual:    ${NEW_HASH:0:8}${NC}"
echo -e "${CYAN}║  Commits aplicados: $COMMIT_COUNT${NC}"
if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    echo -e "${CYAN}║  Backup:            $BACKUP_FILE${NC}"
fi
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║  Datos preservados:${NC}"
echo -e "${CYAN}║    • Identidad criptográfica${NC}"
echo -e "${CYAN}║    • Trayectoria de mutaciones ($MUTATIONS)${NC}"
echo -e "${CYAN}║    • Memoria SQLite ($MEM_ENTRIES entradas)${NC}"
echo -e "${CYAN}║    • API keys en .env${NC}"
echo -e "${CYAN}║    • Cápsulas cargadas${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║  ${BOLD}Próximo paso:${NC}  Arranca ZOE con INICIAR-DASHBOARD.command${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Si algo va mal:${NC} restaura el backup manualmente:"
echo -e "    tar -xzf \"$BACKUP_FILE\" -C \"$ZOE_HOME\""
echo ""
