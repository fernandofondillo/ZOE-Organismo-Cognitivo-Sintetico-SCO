#!/bin/bash
# ZOE v1.0 — Deploy Script
# Despliega ZOE en VPS CEO con Ollama + systemd

set -e

ZOE_DIR="/opt/zoe"
ZOE_DATA="/opt/zoe/data"
ZOE_LOGS="/opt/zoe/logs"
ZOE_USER="zoe"
SERVICE_NAME="zoe"

echo "=========================================="
echo "ZOE v1.0 — Deploy Script"
echo "=========================================="

# 1. Verificar dependencias
echo "[1/6] Verificando dependencias..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no instalado"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama no instalado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
fi
echo "✅ Ollama: $(ollama --version 2>/dev/null || echo 'installed')"

# 2. Crear directorios
echo ""
echo "[2/6] Creando directorios..."
mkdir -p $ZOE_DIR $ZOE_DATA $ZOE_LOGS
echo "✅ Directorios: $ZOE_DIR, $ZOE_DATA, $ZOE_LOGS"

# 3. Copiar código
echo ""
echo "[3/6] Copiando código..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cp -r "$SCRIPT_DIR/zoe" "$ZOE_DIR/zoe"
cp "$SCRIPT_DIR/zoe/requirements.txt" "$ZOE_DIR/"
echo "✅ Código copiado a $ZOE_DIR"

# 4. Instalar dependencias Python
echo ""
echo "[4/6] Instalando dependencias Python..."
pip3 install -r "$ZOE_DIR/requirements.txt" --quiet
echo "✅ Dependencias instaladas"

# 5. Descargar modelo Ollama
echo ""
echo "[5/6] Verificando modelo Ollama..."
if ! ollama list | grep -q "qwen2.5:3b"; then
    echo "Descargando qwen2.5:3b..."
    ollama pull qwen2.5:3b
fi
echo "✅ Modelo qwen2.5:3b disponible"

# 6. Crear servicio systemd
echo ""
echo "[6/6] Creando servicio systemd..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=ZOE v1.0 — Synthetic Cognitive Organism
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=$ZOE_DIR
Environment=ZOE_ENV=production
Environment=PYTHONPATH=$ZOE_DIR
ExecStart=/usr/bin/python3 -m zoe.serve --config $ZOE_DIR/zoe/config/production.yaml
Restart=always
RestartSec=10
StandardOutput=append:$ZOE_LOGS/zoe.log
StandardError=append:$ZOE_LOGS/zoe_error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME
echo "✅ Servicio systemd creado: $SERVICE_NAME"

echo ""
echo "=========================================="
echo "DEPLOY COMPLETADO"
echo "=========================================="
echo ""
echo "Para iniciar ZOE:"
echo "  systemctl start zoe"
echo ""
echo "Para verificar estado:"
echo "  systemctl status zoe"
echo ""
echo "Para ver logs:"
echo "  journalctl -u zoe -f"
echo "  tail -f $ZOE_LOGS/zoe.log"
echo ""
echo "Configuración: $ZOE_DIR/zoe/config/production.yaml"
echo "Datos: $ZOE_DATA"
echo "Logs: $ZOE_LOGS"
