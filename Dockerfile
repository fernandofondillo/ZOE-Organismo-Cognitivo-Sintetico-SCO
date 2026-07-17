# =============================================================================
# ZOE v1.2 — Synthetic Cognitive Organism (SCO)
# Dockerfile — Multi-stage build para producción
#
# Build:  docker build -t zoe .
# Run:    docker run -d --name zoe -v zoe_data:/opt/zoe/data zoe
# =============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder — Dependencias y wheel compilation
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar build dependencies (compilación de paquetes nativos si es necesario)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para cacheo eficiente de layers
COPY requirements.txt .
COPY setup.py .
COPY README.md .

# Instalar dependencias de producción (solo runtime, no test/dev)
# NOTA: No instalamos pytest ni pytest-asyncio en la imagen de producción
RUN pip install --no-cache-dir --user \
    aiohttp>=3.9.0 \
    PyYAML>=6.0

# Instalar el paquete zoe-sco en modo producción
COPY zoe/ ./zoe/
RUN pip install --no-cache-dir --user -e .

# ------------------------------------------------------------------------------
# STAGE 2: Runtime — Imagen mínima de producción
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="Fernando Fondillo <fernandofondillo@users.noreply.github.com>"
LABEL org.opencontainers.image.title="ZOE — Synthetic Cognitive Organism"
LABEL org.opencontainers.image.version="1.2.0"
LABEL org.opencontainers.image.description="El primer organismo cognitivo digital"
LABEL org.opencontainers.image.source="https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO"

# Crear usuario y grupo zoe no-root (UID/GID 1000)
RUN groupadd --gid 1000 zoe && \
    useradd --uid 1000 --gid zoe --shell /bin/bash --create-home zoe

# Instalar solo dependencias runtime esenciales
# procps: para pgrep (health check)
# curl: para health check HTTP (cuando se use dashboard)
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Directorios de datos persistentes
RUN mkdir -p /opt/zoe/data /opt/zoe/logs /app && \
    chown -R zoe:zoe /opt/zoe /app

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /root/.local /home/zoe/.local
COPY --from=builder /build/zoe ./zoe/
COPY --from=builder /build/setup.py .
COPY --from=builder /build/README.md .
COPY --from=builder /build/requirements.txt .

# Instalar el paquete en modo runtime (necesario para entry points y package_data)
RUN pip install --no-cache-dir -e . && \
    chown -R zoe:zoe /home/zoe/.local /app

# Variables de entorno para configuración
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    ZOE_ENV=production \
    ZOE_CONFIG_PATH=zoe/config/production.yaml \
    ZOE_DATA_DIR=/opt/zoe/data \
    ZOE_LOG_DIR=/opt/zoe/logs \
    PATH=/home/zoe/.local/bin:$PATH \
    OLLAMA_HOST=http://ollama:11434 \
    OLLAMA_MODEL=qwen2.5:3b \
    HOME=/home/zoe

# Configurar el usuario no-root
USER zoe

# Puerto del dashboard web (cuando se ejecute zoe-dashboard)
EXPOSE 8642

# Puerto de federación (cuando esté habilitada)
EXPOSE 8643

# Health check: verifica que el proceso zoe.serve esté activo
# El serve.py ejecuta el cognitive loop; verificamos que el proceso Python
# esté corriendo y responda correctamente.
# Nota: serve.py no expone un endpoint HTTP nativo. El health check usa pgrep
# para verificar que el proceso principal esté activo.
# Si se ejecuta zoe-dashboard (modo web), usar en su lugar:
#   --health-cmd="curl -fsS http://localhost:8642/stats || exit 1"
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD pgrep -f "zoe.serve" > /dev/null || exit 1

# Entry point: Inicia ZOE con configuración de producción
# Se puede sobreescribir para ejecutar otros componentes:
#   docker run zoe python -m zoe.web_dashboard --port 8642
#   docker run zoe zoe-chat
#   docker run zoe zoe-capsules --list
ENTRYPOINT ["python", "-m", "zoe.serve"]
CMD ["--config", "zoe/config/production.yaml"]
