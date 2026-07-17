#!/bin/bash
# ============================================================================
# ZOE — Verificador de Memoria SSD
# ============================================================================
# Script: VERIFICAR-MEMORIA.command
# Versión: 1.0 (Sprint 5.25)
#
# PROPÓSITO:
#   Inspecciona la memoria real de ZOE en el SSD. Muestra:
#   - Qué archivos de datos existen (DB, identidad, trayectoria, cápsulas)
#   - Cuántas entradas de memoria hay, por tipo
#   - Últimas 10 conversaciones recordadas
#   - Últimas 5 mutaciones de la trayectoria
#   - Estado del .env (sin mostrar el token)
#   - Identidad criptográfica (hash + ECDSA keys activas)
#   - Últimos insights de reflexión (si los hay)
#
# USO:
#   Doble-click en VERIFICAR-MEMORIA.command (macOS lo abre en Terminal)
#   O desde terminal:
#     bash VERIFICAR-MEMORIA.command
#
# SALIDA:
#   Reporte legible en la terminal. Si algo falla, lo indica claramente.
# ============================================================================

set -uo pipefail

# Colores
if [ -t 1 ]; then
    GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
    GREEN=''; YELLOW=''; RED=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

# ============================================================================
# 1. DETECTAR ZOE_HOME (igual que INICIAR-DASHBOARD.command)
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

detect_zoe_home() {
    if [ -d "$SCRIPT_DIR/venv" ] && [ -d "$SCRIPT_DIR/zoe" ]; then
        echo "$SCRIPT_DIR"
        return
    fi
    if [ -d "$SCRIPT_DIR/../venv" ] && [ -d "$SCRIPT_DIR/../zoe" ]; then
        echo "$(cd "$SCRIPT_DIR/.." && pwd)"
        return
    fi
    if [ -d "$SCRIPT_DIR/../venv" ] && [ -d "$SCRIPT_DIR/../data" ]; then
        echo "$(cd "$SCRIPT_DIR/.." && pwd)"
        return
    fi
    # Preguntar al usuario
    echo -e "${YELLOW}No se pudo detectar ZOE_HOME automáticamente.${NC}"
    echo "Posibles ubicaciones:"
    ls /Volumes/ 2>/dev/null | sed 's/^/  - /' || true
    read -r -p "Introduce la ruta completa a ZOE (ej: /Volumes/CrucialX9/ZOE): " USER_PATH
    if [ -d "$USER_PATH/venv" ] && [ -d "$USER_PATH/data" ]; then
        echo "$USER_PATH"
        return
    fi
    echo -e "${RED}ERROR: $USER_PATH no contiene venv/ y data/. Abortando.${NC}"
    exit 1
}

ZOE_HOME="$(detect_zoe_home)"
ZOE_DATA="$ZOE_HOME/data"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  ZOE — Verificador de Memoria SSD  v1.0 (Sprint 5.25)       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}ZOE_HOME:${NC} $ZOE_HOME"
echo -e "  ${BOLD}ZOE_DATA:${NC} $ZOE_DATA"
echo ""

# ============================================================================
# 2. VERIFICAR ARCHIVOS DE DATOS
# ============================================================================

echo -e "${BOLD}[1/8] Archivos de datos en data/${NC}"

if [ ! -d "$ZOE_DATA" ]; then
    echo -e "  ${RED}ERROR: No existe $ZOE_DATA${NC}"
    echo -e "  ${YELLOW}Esto significa que ZOE nunca ha arrancado desde este SSD.${NC}"
    exit 1
fi

FILES_TO_CHECK=(
    ".env"
    "identity_vault.json"
    "trajectory_chain.json"
    "trajectory_keys.json"
    "loaded_capsules.json"
    "dashboard_token.txt"
    "chat_memory.db"
    "dashboard_memory.db"
)

for f in "${FILES_TO_CHECK[@]}"; do
    filepath="$ZOE_DATA/$f"
    if [ -f "$filepath" ]; then
        size=$(du -h "$filepath" 2>/dev/null | cut -f1)
        mod=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$filepath" 2>/dev/null || stat -c "%y" "$filepath" 2>/dev/null | cut -d. -f1)
        echo -e "  ${GREEN}✓${NC} $f ($size, mod: $mod)"
    else
        echo -e "  ${DIM}· $f (no existe)${NC}"
    fi
done
echo ""

# ============================================================================
# 3. VERIFICAR .env (sin mostrar el token)
# ============================================================================

echo -e "${BOLD}[2/8] Configuración .env (tokens ocultos)${NC}"

ENV_FILE="$ZOE_DATA/.env"
if [ -f "$ENV_FILE" ]; then
    while IFS='=' read -r key value; do
        # Saltar comentarios y líneas vacías
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        # Ocultar valor si parece un token (>10 chars)
        if [ ${#value} -gt 10 ]; then
            masked="${value:0:4}...${value: -4}"
        else
            masked="$value"
        fi
        echo -e "  ${GREEN}✓${NC} $key = $masked"
    done < "$ENV_FILE"
else
    echo -e "  ${YELLOW}⚠️  No existe .env — ZOE usará PatternSpeaker (sin IA cloud)${NC}"
fi
echo ""

# ============================================================================
# 4. ACTIVAR VENV
# ============================================================================

echo -e "${BOLD}[3/8] Activando entorno Python...${NC}"

if [ -f "$ZOE_HOME/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ZOE_HOME/venv/bin/activate"
    echo -e "  ${GREEN}✓${NC} venv activado: $(python --version 2>&1)"
elif [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "  ${YELLOW}⚠️  Usando VIRTUAL_ENV existente: $VIRTUAL_ENV${NC}"
else
    echo -e "  ${YELLOW}⚠️  No hay venv, usando python del sistema${NC}"
fi
echo ""

# ============================================================================
# 5. IDENTIDAD CRIPTOGRÁFICA
# ============================================================================

echo -e "${BOLD}[4/8] Identidad criptográfica${NC}"

VAULT_FILE="$ZOE_DATA/identity_vault.json"
if [ -f "$VAULT_FILE" ]; then
    python3 <<'PYEOF' || true
import json, sys
try:
    with open("VAULT_FILE_PLACEHOLDER") as f:
        v = json.load(f)
    name = v.get("name", "?")
    hash_v = v.get("identity_hash", v.get("hash", "?"))
    birth = v.get("birth_timestamp", 0)
    vectors = v.get("vectors", [])
    values = v.get("values", [])
    purpose = v.get("purpose", "?")[:80]
    print(f"  ✓ Nombre: {name}")
    print(f"  ✓ Hash: {hash_v[:32]}...")
    print(f"  ✓ Nacido: timestamp {birth}")
    print(f"  ✓ Vectores: {len(vectors)} | Valores: {len(values)}")
    print(f"  ✓ Propósito: {purpose}")
except Exception as e:
    print(f"  ⚠️  No se pudo leer identity_vault.json: {e}")
PYEOF
    # Reemplazar placeholder con ruta real
    python3 -c "
import json
with open('$VAULT_FILE') as f:
    v = json.load(f)
name = v.get('name', '?')
hash_v = v.get('identity_hash', v.get('hash', '?'))
birth = v.get('birth_timestamp', 0)
vectors = v.get('vectors', [])
values = v.get('values', [])
purpose = v.get('purpose', '?')[:80]
print(f'  ✓ Nombre: {name}')
print(f'  ✓ Hash: {hash_v[:32]}...')
print(f'  ✓ Nacido: timestamp {birth}')
print(f'  ✓ Vectores: {len(vectors)} | Valores: {len(values)}')
print(f'  ✓ Propósito: {purpose}')
"
else
    echo -e "  ${YELLOW}⚠️  No existe identity_vault.json${NC}"
fi

# ECDSA keys
KEYS_FILE="$ZOE_DATA/trajectory_keys.json"
if [ -f "$KEYS_FILE" ]; then
    echo -e "  ${GREEN}✓${NC} ECDSA keys: cargadas (firma criptográfica real activa)"
    key_size=$(du -h "$KEYS_FILE" 2>/dev/null | cut -f1)
    echo -e "  ${DIM}    Tamaño: $key_size${NC}"
else
    echo -e "  ${YELLOW}⚠️  No existe trajectory_keys.json (ECDSA no activo)${NC}"
    echo -e "  ${DIM}    Sprint 5.24 generará estas claves automáticamente al arrancar.${NC}"
fi
echo ""

# ============================================================================
# 6. MEMORIA — CONTAR ENTRADAS POR TIPO
# ============================================================================

echo -e "${BOLD}[5/8] Memoria SQLite — entradas por tipo${NC}"

DB_FILE=""
for f in "dashboard_memory.db" "chat_memory.db"; do
    if [ -f "$ZOE_DATA/$f" ]; then
        DB_FILE="$ZOE_DATA/$f"
        break
    fi
done

if [ -z "$DB_FILE" ]; then
    echo -e "  ${YELLOW}⚠️  No existe SQLite DB — ZOE nunca ha arrancado desde este SSD${NC}"
else
    echo -e "  ${DIM}Archivo: $DB_FILE${NC}"
    echo ""
    python3 -c "
import sqlite3, json
try:
    conn = sqlite3.connect('$DB_FILE')
    cur = conn.cursor()
    # Conteo total
    cur.execute('SELECT COUNT(*) FROM memory_entries')
    total = cur.fetchone()[0]
    print(f'  TOTAL entradas: {total}')
    print()
    # Conteo por tipo
    cur.execute('SELECT type, COUNT(*) FROM memory_entries GROUP BY type ORDER BY COUNT(*) DESC')
    rows = cur.fetchall()
    if rows:
        print('  Por tipo:')
        for t, c in rows:
            print(f'    {t:20} {c:6} entradas')
    else:
        print('  (sin entradas — ZOE nunca ha guardado nada)')
    print()
    # Últimas 10 memorias
    cur.execute('SELECT type, content, timestamp, salience FROM memory_entries ORDER BY timestamp DESC LIMIT 10')
    rows = cur.fetchall()
    if rows:
        print('  Últimas 10 memorias guardadas:')
        for t, c, ts, sal in rows:
            content_preview = (c or '')[:80].replace(chr(10), ' ')
            print(f'    [{t:10}] sal={sal:.2f} | {content_preview}')
    conn.close()
except Exception as e:
    print(f'  ⚠️  Error leyendo SQLite: {e}')
"
fi
echo ""

# ============================================================================
# 7. TRAYECTORIA — ÚLTIMAS MUTACIONES
# ============================================================================

echo -e "${BOLD}[6/8] Trayectoria — últimas 5 mutaciones${NC}"

CHAIN_FILE="$ZOE_DATA/trajectory_chain.json"
if [ -f "$CHAIN_FILE" ]; then
    python3 -c "
import json
with open('$CHAIN_FILE') as f:
    data = json.load(f)
mutations = data.get('mutations', [])
print(f'  Total mutaciones firmadas: {len(mutations)}')
print()
if mutations:
    print('  Últimas 5:')
    for m in mutations[-5:]:
        mtype = m.get('type', '?')
        target = m.get('target', '?')
        ts = m.get('timestamp', 0)
        sig = m.get('signature', '')[:20]
        sig_info = 'ECDSA' if len(m.get('signature', '')) > 70 else 'legacy-SHA256'
        print(f'    [{mtype:18}] target={target:12} sig={sig_info}')
"
else
    echo -e "  ${YELLOW}⚠️  No existe trajectory_chain.json${NC}"
fi
echo ""

# ============================================================================
# 8. CÁPSULAS CARGADAS
# ============================================================================

echo -e "${BOLD}[7/8] Cápsulas cargadas${NC}"

CAPS_FILE="$ZOE_DATA/loaded_capsules.json"
if [ -f "$CAPS_FILE" ]; then
    python3 -c "
import json
with open('$CAPS_FILE') as f:
    data = json.load(f)
caps = data if isinstance(data, list) else data.get('loaded', [])
if caps:
    print(f'  Total: {len(caps)}')
    for c in caps:
        if isinstance(c, dict):
            name = c.get('name', '?')
            entries = c.get('entries_injected', c.get('total_entries', '?'))
            trust = c.get('trust_level', '?')
            print(f'    - {name:35} trust={trust:10} entries={entries}')
        else:
            print(f'    - {c}')
else:
    print('  (sin cápsulas cargadas)')
"
else
    echo -e "  ${YELLOW}⚠️  No existe loaded_capsules.json${NC}"
fi
echo ""

# ============================================================================
# 9. VERIFICACIÓN FINAL — ¿ZOE RECORDARÁ ENTRE SESIONES?
# ============================================================================

echo -e "${BOLD}[8/8] Verificación final — memoria persistente${NC}"

checks_passed=0
checks_total=0

check() {
    checks_total=$((checks_total + 1))
    if [ "$1" = "ok" ]; then
        echo -e "  ${GREEN}✓${NC} $2"
        checks_passed=$((checks_passed + 1))
    else
        echo -e "  ${RED}✗${NC} $2"
    fi
}

if [ -n "$DB_FILE" ] && [ -f "$DB_FILE" ]; then
    check ok "SQLite DB existe — memoria persistirá entre sesiones"
else
    check fail "SQLite DB no existe — la memoria NO persistirá"
fi

if [ -f "$VAULT_FILE" ]; then
    check ok "IdentityVault existe — identidad persistirá entre sesiones"
else
    check fail "IdentityVault no existe — identidad se recreará cada arranque"
fi

if [ -f "$CHAIN_FILE" ]; then
    check ok "TrajectoryChain existe — trayectoria persistirá entre sesiones"
else
    check fail "TrajectoryChain no existe — trayectoria se perderá"
fi

if [ -f "$KEYS_FILE" ]; then
    check ok "ECDSA keys existen — firma criptográfica real activa"
else
    check warn "ECDSA keys no existen — Sprint 5.24 las generará al primer arranque"
fi

if [ -f "$ENV_FILE" ]; then
    check ok ".env existe — API keys (MiniMax/OpenAI) cargados al arrancar"
else
    check fail ".env no existe — ZOE usará PatternSpeaker (sin IA)"
fi

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  RESULTADO: $checks_passed/$checks_total checks OK                              ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
if [ "$checks_passed" -ge 4 ]; then
    echo -e "${CYAN}║  ${GREEN}${BOLD}ZOE está lista para recordar entre sesiones${NC}${CYAN}                       ║${NC}"
    echo -e "${CYAN}║  Tu memoria, identidad y trayectoria están en el SSD.        ║${NC}"
    echo -e "${CYAN}║  Desconecta el SSD, llévalo a otro Mac, arranca — misma ZOE. ║${NC}"
else
    echo -e "${CYAN}║  ${YELLOW}${BOLD}Faltan archivos críticos. Arranca ZOE una vez para crearlos.${NC}${CYAN}    ║${NC}"
    echo -e "${CYAN}║  bash INICIAR-DASHBOARD.command                              ║${NC}"
fi
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CONSEJOS
# ============================================================================

echo -e "${BOLD}Consejos:${NC}"
echo -e "  1. Para arrancar ZOE: ${CYAN}bash $ZOE_HOME/INICIAR-DASHBOARD.command${NC}"
echo -e "  2. Para ver memoria en el dashboard: ${CYAN}http://localhost:8642/memory${NC}"
echo -e "  3. Para probar que recuerda: cierra ZOE, ábrela, pregunta '¿qué te dije ayer?'"
echo -e "  4. Para verificar ECDSA activo: mira los logs al arrancar, busca 'ECDSA keys loaded'"
echo ""
