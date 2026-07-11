# 08 — Deployment Guide

> **TODAS las opciones de despliegue de ZOE: pendrive, VPS, portátil, Docker, Kubernetes.**
> **Con requisitos claros por plataforma y qué se instala DÓNDE.**
> **Audiencia:** DevOps, CTO, usuarios finales.
> **Versión:** V1.6.0 — Julio 2026

---

## Tabla de contenidos

1. [Tabla de requisitos por plataforma](#1-tabla-de-requisitos-por-plataforma)
2. [Requisitos de software](#2-requisitos-de-software-qu%C3%A9-se-instala-d%C3%B3nde)
3. [Requisitos de hardware por modelo](#3-requisitos-de-hardware-por-modelo)
4. [Pendrive USB / SSD (macOS)](#4-pendrive-usb--ssd-macos)
5. [Pendrive USB / SSD (Linux)](#5-pendrive-usb--ssd-linux)
6. [Mac local](#6-mac-local-sin-pendrive)
7. [VPS Linux](#7-vps-linux)
8. [Portátil Linux](#8-portátil-linux-desarrollo)
9. [Portátil Windows](#9-portátil-windows)
10. [Docker](#10-docker)
11. [Kubernetes](#11-kubernetes)
12. [Federación B2B en producción](#12-federación-b2b-en-producción)
13. [Cloud gestionado](#13-cloud-gestionado-próximamente)
14. [Migración entre plataformas (ZOE Seed Mode)](#14-migración-entre-plataformas-zoe-seed-mode)
15. [Tabla comparativa de costes](#15-tabla-comparativa-de-costes)
16. [Decision tree](#16-decision-tree)

---

## 1. Tabla de requisitos por plataforma

| Plataforma | Software en host | Software en dispositivo | RAM mínima | Disco | Coste inicial | Coste mensual |
|---|---|---|---|---|---|---|
| **Pendrive macOS** | Python 3.10+, Git, Ollama (opcional) | Código + venv + memoria | 4 GB | 16-64 GB pendrive | €110 (SSD) o €20 (USB) | €0-20 |
| **Pendrive Linux** | Python 3.10+, Git, Ollama (opcional) | Código + venv + memoria | 4 GB | 16-64 GB pendrive | €110 (SSD) o €20 (USB) | €0-20 |
| **Mac local** | Python 3.10+, Git, Ollama (opcional) | Código + venv + memoria | 8 GB | 10 GB libres | €0 (ya tienes Mac) | €0-20 |
| **VPS Linux** | Python 3.10+, Git, Ollama | Código + venv + memoria | 8-32 GB | 50 GB | €5-50 (VPS) | €5-50 + €0-200 (cloud API) |
| **Portátil Linux** | Python 3.10+, Git, Ollama (opcional) | Código + venv + memoria | 8 GB | 10 GB libres | €0 | €0-20 |
| **Portátil Windows** | WSL2 + Python 3.10+ + Git | Código + venv + memoria | 8 GB | 10 GB libres | €0 | €0-20 |
| **Docker** | Docker | Container | 8 GB | 20 GB | €0 | €0-20 |
| **Kubernetes** | K8s cluster + Helm | Pod | 16 GB | 50 GB | €50-500 (cloud) | €50-500 |

---

## 2. Requisitos de software (qué se instala DÓNDE)

### Principio fundamental

> **ZOE necesita Python 3.10+ en el HOST. El código, venv, modelos y memoria van en el DISPOSITIVO (pendrive/SSD/disco).**

Esto significa:
- En **modo pendrive**: Python se instala en el Mac (no en el pendrive). El código de ZOE, el venv, los modelos y la memoria van en el pendrive.
- En **modo VPS**: Python se instala en el VPS. Todo va en el disco del VPS.
- En **modo Docker**: Python va en el container. Todo va en volúmenes persistentes.

### Software obligatorio en el HOST

| Software | Versión | Por qué | Cómo instalar |
|---|---|---|---|
| **Python** | 3.10+ | ZOE es Python | [python.org](https://python.org) o `apt install python3` |
| **pip** | 21+ | Instalar dependencias | Viene con Python |
| **Git** | 2.30+ | Clonar repositorio | [git-scm.com](https://git-scm.com) o `apt install git` |

### Software opcional en el HOST

| Software | Versión | Por qué | Cómo instalar |
|---|---|---|---|
| **Ollama** | 0.1+ | LLM local gratis | [ollama.com](https://ollama.com) |
| **OpenAI API key** | — | GPT-4o cloud | [platform.openai.com](https://platform.openai.com) |
| **Anthropic API key** | — | Claude cloud | [console.anthropic.com](https://console.anthropic.com) |

### Software que se instala en el DISPOSITIVO (no en el host)

| Software | Dónde | Tamaño |
|---|---|---|
| **Código ZOE** | Pendrive/SSD/disco | ~25 MB |
| **venv (entorno virtual)** | Pendrive/SSD/disco | ~200 MB |
| **Memoria SQLite** | Pendrive/SSD/disco | Crece con uso (~100 MB/año) |
| **Modelos Ollama** (opcional) | Pendrive/SSD/disco | 2-30 GB por modelo |

**Total inicial:** ~500 MB (sin modelos) o 2-30 GB (con modelos)

---

## 3. Requisitos de hardware por modelo

| Modelo | RAM mínima | RAM recomendada | Disco | Velocidad esperada (M2 8GB) | Estrategia |
|---|---|---|---|---|---|
| Qwen 2.5 3B (Q4) | 4 GB | 8 GB | 2 GB | 25-35 tokens/s ⚡ | full_ram |
| Qwen 2.5 7B (Q4) | 6 GB | 8 GB | 5 GB | 12-18 tokens/s ✅ | mmap_partial |
| Qwen 2.5 14B (Q4) | 8 GB | 16 GB | 9 GB SSD | 4-8 tokens/s 📖 | mmap_partial |
| Qwen 2.5 32B (IQ2_M) | 8 GB | 16 GB | 12 GB SSD | 3-6 tokens/s 🧠 | mmap_full |
| Qwen 2.5 32B (Q4) | 16 GB | 32 GB | 18 GB SSD | 2-4 tokens/s | mmap_full |
| Qwen 2.5 72B (IQ2_M) | 8 GB | 32 GB | 30 GB SSD | 1-3 tokens/s | mmap_full |
| Llama 3.1 8B (Q4) | 6 GB | 8 GB | 5 GB | 12-18 tokens/s | mmap_partial |
| Llama 3.1 70B (IQ2_M) | 8 GB | 32 GB | 25 GB SSD | 1-3 tokens/s | mmap_full |
| DeepSeek R1 14B (Q4) | 8 GB | 16 GB | 9 GB SSD | 4-8 tokens/s | mmap_partial |
| DeepSeek R1 32B (IQ2_M) | 8 GB | 16 GB | 12 GB SSD | 3-6 tokens/s | mmap_full |

> 💡 **1 token ≈ 0,75 palabras.** 12 tokens/s = ~9 palabras/s = más rápido de lo que lee un humano.
> Ver [Hardware Optimization](10_HARDWARE_OPTIMIZATION.md) para detalle completo.

### SSD vs Pendrive USB

| Dispositivo | Velocidad lectura | Modelos soportados | Precio |
|---|---|---|---|
| Pendrive USB 3.0 genérico | 100-400 MB/s | Hasta 7B (Q4) | 10-25€ |
| Pendrive USB 3.2 premium | 500-1000 MB/s | Hasta 14B (Q4, lento) | 30-60€ |
| **SSD portátil USB-C** (Crucial X10 Pro) | **2000 MB/s** | **Hasta 72B (IQ2_M)** | **~110€** |

> ⚠️ **Si quieres usar ZOE con modelos de 14B o más en un MacBook Air de 8 GB, necesitas un SSD portátil de 2000 MB/s.** Con un pendrive USB normal será 10x más lento.

---

## 4. Pendrive USB / SSD (macOS)

### 4.1 Qué necesitas

- MacBook Air (o cualquier Mac) con macOS 11+
- SSD portátil USB-C de 1TB (recomendado: Crucial X10 Pro, ~110€)
- O pendrive USB 3.0 de 16GB mínimo (para modelos pequeños)
- Python 3.10+ instalado en el Mac ([python.org](https://python.org))
- Git instalado en el Mac (`xcode-select --install`)

### 4.2 Regla de oro: el cable USB-C

> ⚠️ **CRÍTICO — Usa SIEMPRE el cable corto que viene dentro de la caja del SSD.**
>
> El cable largo que usas para cargar tu MacBook Air es **USB 2.0** (480 Mbps) y limita el SSD a ~60 MB/s. Si ZOE va lento, en el 90% de los casos el culpable es el cable equivocado.
>
> El cable corto que viene en la caja del SSD es **USB 3.2 Gen 2** (10 Gbps) y permite los 2000 MB/s reales.

**Síntomas para diagnosticar:**
- **Cable equivocado:** ZOE tarda 10+ segundos en responder, la primera palabra aparece muy lenta.
- **Cable correcto:** ZOE responde en 1-2 segundos, el texto fluye rápido.

### 4.3 Instalación paso a paso

**Paso 1: Preparar el Mac (5 min)**

```bash
# Instalar Xcode Command Line Tools (incluye Git)
xcode-select --install

# Verificar Python 3.10+
python3 --version
# Si no tienes Python 3.10+: instalar desde https://python.org

# Instalar Ollama (opcional, para LLM local gratis)
# Descargar desde https://ollama.com y instalar
```

**Paso 2: Conectar el SSD (1 min)**

1. Saca el SSD de la caja.
2. Conéctalo al Mac con **el cable corto que venía en la caja** (no el de carga).
3. Verás que aparece un nuevo disco en el Escritorio o en Finder → "Ubicaciones".

**Paso 3: Ejecutar el instalador (5 min)**

```bash
# Abrir Terminal (Cmd + Espacio, escribe "Terminal")
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh | bash
```

El instalador te preguntará:
1. **¿Qué disco quieres usar?** → Elige tu SSD (selecciónalo con el número)
2. **¿Quieres configurar OpenAI API key?** → Si no tienes una, di "No" (ZOE funcionará en modo local gratis)
3. **¿Quieres instalar modelos de Ollama?** → Si tienes Ollama, di "Sí"

**Paso 4: Verificación (2 min)**

```bash
# El instalador crea estos archivos en el SSD:
ls /Volumes/TU-SSD/ZOE/
# Debe mostrar:
# ZOE-Chat.command          ← Doble clic para Chat
# ZOE-Chat-Ollama.command   ← Doble clic para Chat con Ollama
# ZOE-Chat-OpenAI.command   ← Doble clic para Chat con GPT-4o
# ZOE-Dashboard.command     ← Doble clic para Dashboard web
# zoe/                      ← Código
# venv/                     ← Entorno virtual
# data/                     ← Memoria
```

**Paso 5: Hablar con ZOE (1 min)**

Doble clic en `ZOE-Chat-Ollama.command` (si tienes Ollama) o `ZOE-Chat.command` (modo Mock, sin IA).

Se abre Terminal con ZOE. Escribe: "Hola ZOE, ¿quién eres?"

### 4.4 Qué se instala DÓNDE

```
Mac (host):
├── Python 3.10+          ← en /usr/local/bin/python3 o /opt/homebrew/bin/python3
├── Git                   ← en /usr/bin/git
└── Ollama (opcional)     ← en /usr/local/bin/ollama
    └── Modelos           ← en ~/.ollama/models (en el Mac, no en el SSD)

SSD portátil (dispositivo):
└── ZOE/
    ├── zoe/              ← Código del proyecto (~25 MB)
    ├── venv/             ← Entorno virtual Python (~200 MB)
    ├── data/             ← Memoria de ZOE
    │   └── zoe_memory.db ← SQLite con memoria persistente
    ├── models/           ← Modelos Ollama (opcional, 2-30 GB)
    ├── ZOE-Chat.command         ← Doble clic → Chat Mock
    ├── ZOE-Chat-Ollama.command  ← Doble clic → Chat Ollama
    ├── ZOE-Chat-OpenAI.command  ← Doble clic → Chat GPT-4o
    ├── ZOE-Dashboard.command    ← Doble clic → Dashboard web
    └── data/.env         ← API keys (chmod 600)
```

**Espacio total:** ~500 MB inicial (sin modelos), 2-30 GB con modelos.

### 4.5 Los 12 scripts .command

El instalador crea hasta 12 scripts lanzadores:

| Script | Interfaz | Backend | Requiere |
|---|---|---|---|
| `ZOE-Chat.command` | CLI | Mock (sin LLM) | Nada |
| `ZOE-Chat-Ollama.command` | CLI | Ollama qwen2.5:3b | Ollama en Mac |
| `ZOE-Chat-Ollama-Pendrive.command` | CLI | Ollama (modelos en SSD) | Ollama en Mac |
| `ZOE-Chat-OpenAI.command` | CLI | OpenAI GPT-4o | API key |
| `ZOE-Chat-Anthropic.command` | CLI | Claude | API key |
| `ZOE-Chat-Custom.command` | CLI | DeepSeek/Kimi/Groq/etc. | API key |
| `ZOE-Dashboard.command` | Web | Mock | Nada |
| `ZOE-Dashboard-Ollama.command` | Web | Ollama | Ollama |
| `ZOE-Dashboard-Ollama-Pendrive.command` | Web | Ollama (modelos en SSD) | Ollama |
| `ZOE-Dashboard-OpenAI.command` | Web | OpenAI GPT-4o | API key |
| `ZOE-Dashboard-Anthropic.command` | Web | Claude | API key |
| `ZOE-Dashboard-Custom.command` | Web | DeepSeek/Kimi/Groq/etc. | API key |

### 4.6 API key segura en el SSD

El instalador guarda las API keys en `ZOE/data/.env` con `chmod 600` (solo el propietario puede leer). **Nunca se guardan en el Mac** — solo en el SSD.

```bash
# Si no configuraste la API key durante la instalación:
echo "OPENAI_API_KEY=sk-tu-key-aqui" > /Volumes/TU-SSD/ZOE/data/.env
chmod 600 /Volumes/TU-SSD/ZOE/data/.env
```

### 4.7 Desconectar el SSD correctamente

```bash
# Antes de desconectar, SIEMPRE:
# 1. En CLI: escribe /quit
# 2. En Dashboard: cierra el navegador y espera a que Terminal diga "ZOE stopped"
# 3. Expulsa el SSD desde Finder (clic derecho → Expulsar)
```

**Si desconectas sin /quit:** la memoria SQLite puede corromperse. ZOE tiene recovery automático, pero es mejor evitarlo.

### 4.8 Acceso desde otros dispositivos

El Dashboard escucha en `0.0.0.0:8642`, accesible desde cualquier dispositivo en la red local:
- Desde otro Mac: `http://IP-DE-TU-MAC:8642`
- Desde iPhone/iPad: `http://IP-DE-TU-MAC:8642`
- Desde Android: `http://IP-DE-TU-MAC:8642`

Para conocer la IP de tu Mac: `System Preferences → Network` o `ifconfig | grep inet`.

---

## 5. Pendrive USB / SSD (Linux)

### 5.1 Qué necesitas

- Cualquier distribución Linux con kernel 5.10+
- SSD portátil USB-C o pendrive USB 3.0
- Python 3.10+ (`sudo apt install python3.12`)
- Git (`sudo apt install git`)
- Ollama opcional (`curl -fsSL https://ollama.com/install.sh | sh`)

### 5.2 Instalación

```bash
# 1. Conectar SSD
# Linux lo montará automáticamente en /media/$USER/NOMBRE-SSD

# 2. Clonar ZOE al SSD
cd /media/$USER/TU-SSD
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git ZOE/zoe

# 3. Crear venv en el SSD
cd ZOE
python3.12 -m venv venv
source venv/bin/activate
pip install -e .

# 4. Crear directorios
mkdir -p data

# 5. Ejecutar
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b
```

### 5.3 Detección automática (ZOE Seed Mode)

ZOE detecta automáticamente SSDs montados en `/media/<user>/` vía el `ResourceDiscoverySense` (Fase 7A) y el `ZOESeed` (Fase 7E).

---

## 6. Mac local (sin pendrive)

### 6.1 Instalación

```bash
# 1. Clonar
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar
pip install -e .

# 3. Hablar con ZOE
zoe-chat --backend ollama --model qwen2.5:3b

# 4. Dashboard
zoe-dashboard --backend ollama --model qwen2.5:3b
# → http://localhost:8642
```

### 6.2 Verificación

```bash
# Verificar versión
python -c "import zoe; print(f'ZOE v{zoe.__version__}, phase={zoe.__phase__}')"
# Output: ZOE v1.6.0, phase=phase_7g

# Verificar cápsulas
zoe-capsules list
# Debe mostrar 13 cápsulas

# Ejecutar tests
pytest zoe/tests/ -q
# Debe mostrar "1008 passed"
```

### 6.3 Configurar Ollama

```bash
# 1. Instalar Ollama desde https://ollama.com
# 2. Descargar modelo
ollama pull qwen2.5:3b    # 2GB, rápido
# o
ollama pull qwen2.5:7b    # 4.5GB, más calidad

# 3. Verificar
ollama list
```

### 6.4 Configurar API keys (opcional)

```bash
# OpenAI
export OPENAI_API_KEY="sk-tu-key-aqui"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-tu-key-aqui"

# DeepSeek
export DEEPSEEK_API_KEY="tu-key-aqui"

# O añadir a ~/.zshrc o ~/.bashrc para persistencia
```

---

## 7. VPS Linux

### 7.1 Requisitos del VPS

| Recurso | Mínimo | Recomendado | Para modelos grandes |
|---|---|---|---|
| **RAM** | 8 GB | 16 GB | 32 GB |
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **Disco** | 50 GB SSD | 100 GB SSD | 200 GB NVMe |
| **GPU** | No | No | NVIDIA con CUDA (opcional) |
| **OS** | Ubuntu 22.04+ | Ubuntu 24.04 | Ubuntu 24.04 |
| **Red** | 100 Mbps | 1 Gbps | 1 Gbps |

### 7.2 Proveedores VPS recomendados

| Proveedor | VPS 8GB | VPS 16GB | VPS 32GB | Notas |
|---|---|---|---|---|
| Hetzner | €8/mes | €15/mes | €30/mes | Mejor precio/calidad en EU |
| DigitalOcean | €20/mes | €40/mes | €80/mes | Fácil de usar |
| Vultr | €12/mes | €24/mes | €48/mes | Buena red global |
| AWS EC2 | €15/mes | €30/mes | €60/mes | Caro pero fiable |
| Contabo | €6/mes | €10/mes | €20/mes | Muy barato, menos fiable |

### 7.3 Setup del VPS (paso a paso)

**Paso 1: Crear VPS**

```bash
# Crear VPS Ubuntu 24.04 en tu proveedor elegido
# Conectarse vía SSH
ssh root@IP-DEL-VPS
```

**Paso 2: Setup inicial del servidor**

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Crear usuario zoe
adduser zoe
usermod -aG sudo zoe

# Configurar SSH key (recomendado)
su - zoe
mkdir -p ~/.ssh
# Pegar tu clave pública SSH en ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Deshabilitar login root por SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

**Paso 3: Instalar dependencias**

```bash
# Python 3.12
sudo apt install -y python3.12 python3.12-venv python3-pip

# Git
sudo apt install -y git

# Ollama (para LLM local)
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull qwen2.5:7b  # o qwen2.5:3b si RAM limitada

# Nginx (reverse proxy)
sudo apt install -y nginx

# Certbot (TLS)
sudo apt install -y certbot python3-certbot-nginx
```

**Paso 4: Instalar ZOE**

```bash
# Como usuario zoe
cd /opt
sudo git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git zoe
sudo chown -R zoe:zoe /opt/zoe
cd /opt/zoe

# Crear venv
python3.12 -m venv venv
source venv/bin/activate
pip install -e .

# Crear directorios
mkdir -p /opt/zoe/data /opt/zoe/logs
```

**Paso 5: Configurar**

```bash
# Copiar config de producción
cp zoe/config/production.yaml zoe/config/myproduction.yaml

# Editar config
nano zoe/config/myproduction.yaml
```

Configuración recomendada para VPS:

```yaml
zoe:
  organism_id: "zoe_mi_empresa"
  tick_interval: 5.0
  environment: "production"

llm:
  backend: "ollama"
  model: "qwen2.5:7b"
  base_url: "http://localhost:11434"

metabolism:
  drowsy_threshold: 0.6
  sleep_threshold: 0.8
  wake_threshold: 0.3

memory:
  db_path: "/opt/zoe/data/memory.db"
  auto_save_interval: 50
  max_entries: 5000

federation:
  enabled: false  # true si vas a federar
  host: "0.0.0.0"
  port: 8642
  peers: []
  quorum_threshold: 0.7

logging:
  level: "INFO"
  file: "/opt/zoe/logs/zoe.log"
```

**Paso 6: O usar el script deploy.sh existente**

ZOE incluye un script de deploy que automatiza todo lo anterior:

```bash
# El script está en zoe/scripts/deploy.sh
# Hace:
# 1. Verificar dependencias (Python, Ollama)
# 2. Crear directorios (/opt/zoe, data, logs)
# 3. Copiar código
# 4. Crear usuario zoe
# 5. Instalar venv + dependencias
# 6. Crear systemd service
# 7. Descargar modelo Ollama
# 8. Iniciar servicio
# 9. Verificar (6 pasos)

# Ejecutar:
sudo bash zoe/scripts/deploy.sh
```

**Paso 7: Systemd service**

```ini
# /etc/systemd/system/zoe.service
[Unit]
Description=ZOE Synthetic Cognitive Organism
After=network.target ollama.service

[Service]
Type=simple
User=zoe
WorkingDirectory=/opt/zoe
Environment=ZOE_ENV=production
ExecStart=/opt/zoe/venv/bin/python -m zoe.serve --config zoe/config/myproduction.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable zoe
sudo systemctl start zoe
sudo systemctl status zoe

# Ver logs
sudo journalctl -u zoe -f
```

**Paso 8: Nginx reverse proxy + TLS**

```nginx
# /etc/nginx/sites-available/zoe
server {
    server_name zoe.tudominio.com;
    
    location / {
        proxy_pass http://localhost:8642;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/zoe /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# TLS con Let's Encrypt
sudo certbot --nginx -d zoe.tudominio.com
```

**Paso 9: Firewall**

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

**Paso 10: Verificación**

```bash
# Verificar que ZOE responde
curl http://localhost:8642/stats

# Verificar desde fuera
curl https://zoe.tudominio.com/stats
```

### 7.4 Backup automático

```bash
# Cron job para backup diario
sudo crontab -e

# Añadir:
0 3 * * * tar -czf /backups/zoe_$(date +\%Y\%m\%d).tar.gz /opt/zoe/data/ /opt/zoe/zoe/config/

# Retención 30 días
0 4 * * * find /backups/ -mtime +30 -delete
```

### 7.5 Monitoring

```bash
# Instalar Prometheus node exporter
sudo apt install -y prometheus-node-exporter

# ZOE expone métricas en /stats
# Configurar Prometheus para scrapear:
# - targets: ['localhost:8642']
# - interval: 30s
```

Métricas clave a monitorizar:
- `iteration_count` — ticks del bucle cognitivo
- `metabolic_state` — AWAKE/DROWSY/SLEEPING
- `energy`, `fatigue`, `arousal` — estado interno
- `modelbus.success_rate` — tasa de éxito de LLM calls
- `cache.hit_rate` — tasa de cache hits
- `quarantine.size` — items en cuarentena

---

## 8. Portátil Linux (desarrollo)

### 8.1 Instalación

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.12 python3.12-venv git

# Clonar
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# Instalar
python3.12 -m venv venv
source venv/bin/activate
pip install -e .

# Ejecutar
zoe-chat --backend mock  # para probar sin LLM
```

### 8.2 Detección de hardware

```bash
# NVIDIA GPU (para CUDA)
nvidia-smi

# AMD GPU
rocm-smi

# CPU cores
nproc

# RAM
free -h
```

### 8.3 Ollama en Linux

```bash
# Instalar
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull qwen2.5:7b

# Ejecutar ZOE
zoe-chat --backend ollama --model qwen2.5:7b
```

---

## 9. Portátil Windows

### 9.1 Windows nativo (Sprint 1 — recomendado)

ZOE tiene soporte nativo para Windows desde V1.7.0 (Sprint 1).

**Paso 1: Instalar dependencias**

```powershell
# Instalar Python 3.10+ desde https://python.org
# Instalar Git desde https://git-scm.com
# (Opcional) Instalar Ollama desde https://ollama.com
```

**Paso 2: Instalar ZOE con el installer PowerShell**

```powershell
# Descargar y ejecutar installer
.\install_windows.ps1
```

El installer:
1. Verifica Python y Git
2. Selecciona disco de instalación (D:, E:, o local)
3. Clona el repositorio
4. Crea entorno virtual
5. Instala dependencias
6. Crea 4 scripts `.bat` launchers (Chat Mock, Chat Ollama, Dashboard Mock, Dashboard Ollama)
7. Configura API key opcional

**Paso 3: Ejecutar ZOE**

```cmd
# Doble clic en ZOE-Chat.bat (modo Mock)
# Doble clic en ZOE-Chat-Ollama.bat (con Ollama)
# Doble clic en ZOE-Dashboard.bat (Dashboard web)
```

**Detección automática de drives Windows:**
- `ResourceDiscoverySense` detecta drives D: a Z: automáticamente
- `ZOESeed.detect_seed_volume()` busca semillas en drives Windows
- `ZOESeed.list_seed_paths()` incluye paths Windows

### 9.2 Vía WSL2 (alternativa)

Si prefieres usar WSL2:

```powershell
wsl --install -d Ubuntu-24.04
```

Dentro de WSL2, instalar ZOE como en Linux (ver §8).

### 9.3 Limitaciones actuales

- No soporte nativo para Windows (en roadmap 2027)
- Detección de pendrive USB en WSL2 requiere configuración adicional
- Ollama funciona en WSL2 pero con menor rendimiento que nativo

---

## 10. Docker

### 10.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio
WORKDIR /app

# Copiar código
COPY . .

# Instalar ZOE
RUN pip install --no-cache-dir -e .

# Crear directorios
RUN mkdir -p /app/data /app/logs

# Exponer puerto
EXPOSE 8642

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8642/stats || exit 1

# Comando
CMD ["python", "-m", "zoe.serve", "--config", "zoe/config/production.yaml"]
```

### 10.2 docker-compose.yml (con Ollama)

```yaml
# docker-compose.yml
version: '3.8'

services:
  zoe:
    build: .
    container_name: zoe
    ports:
      - "8642:8642"
    volumes:
      - zoe_data:/app/data
      - zoe_config:/app/zoe/config
    environment:
      - ZOE_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
    depends_on:
      - ollama
    restart: unless-stopped
    networks:
      - zoe_network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    restart: unless-stopped
    networks:
      - zoe_network

volumes:
  zoe_data:
  zoe_config:
  ollama_models:

networks:
  zoe_network:
    driver: bridge
```

### 10.3 Ejecutar

```bash
# Build + start
docker-compose up -d

# Ver logs
docker-compose logs -f zoe

# Descargar modelo en Ollama
docker exec -it ollama ollama pull qwen2.5:7b

# Acceder
curl http://localhost:8642/stats

# Parar
docker-compose down

# Parar y borrar volúmenes (¡CUIDADO! borra memoria)
docker-compose down -v
```

### 10.4 Variables de entorno

```bash
# .env file
OPENAI_API_KEY=sk-tu-key
ANTHROPIC_API_KEY=sk-ant-tu-key
DEEPSEEK_API_KEY=tu-key
ZOE_ENV=production
```

---

## 11. Kubernetes

### 11.1 Helm chart

ZOE incluye un Helm chart en `infra/helm/cfi-v2/`.

```bash
# Instalar con Helm
helm install zoe ./infra/helm/cfi-v2

# Con values custom
helm install zoe ./infra/helm/cfi-v2 -f my-values.yaml
```

### 11.2 my-values.yaml

```yaml
# my-values.yaml
replicaCount: 1

image:
  repository: zoe/zoe
  tag: "1.6.0"
  pullPolicy: IfNotPresent

resources:
  limits:
    memory: "8Gi"
    cpu: "4000m"
  requests:
    memory: "4Gi"
    cpu: "2000m"

persistence:
  enabled: true
  storageClass: "fast-ssd"
  size: 50Gi

ingress:
  enabled: true
  hostname: zoe.tudominio.com
  tls: true

env:
  ZOE_ENV: production
  LLM_BACKEND: ollama
  LLM_MODEL: qwen2.5:7b

autoscaling:
  enabled: false  # ZOE es single-tenant, no escalar horizontalmente
```

### 11.3 Deployment manual (sin Helm)

```yaml
# zoe-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zoe
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zoe
  template:
    metadata:
      labels:
        app: zoe
    spec:
      containers:
      - name: zoe
        image: zoe/zoe:1.6.0
        ports:
        - containerPort: 8642
        env:
        - name: ZOE_ENV
          value: "production"
        volumeMounts:
        - name: zoe-data
          mountPath: /app/data
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
      volumes:
      - name: zoe-data
        persistentVolumeClaim:
          claimName: zoe-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: zoe-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: zoe
spec:
  type: ClusterIP
  ports:
  - port: 8642
    targetPort: 8642
  selector:
    app: zoe
```

```bash
kubectl apply -f zoe-deployment.yaml
```

---

## 12. Federación B2B en producción

### 12.1 Arquitectura

```
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  ZOE Clínica │◄───►│ ZOE Hospital │◄───►│ ZOE Residencia│
    │  VPS A       │     │  VPS B       │     │  VPS C       │
    │  10.0.1.10   │     │  10.0.2.20   │     │  10.0.3.30   │
    └──────────────┘     └──────────────┘     └──────────────┘
            ▲                    ▲                    ▲
            └────────────────────┴────────────────────┘
                          │
                  Federación HTTP (puerto 8643)
                  - Propose mutation
                  - Vote (YES / NO / VETO)
                  - Check quorum (2/3)
                  - Apply if quorum
```

### 12.2 Configuración de peers

```yaml
# En production.yaml de cada ZOE
federation:
  enabled: true
  host: "0.0.0.0"
  port: 8643
  peers:
    - peer_id: "zoe_clinica"
      host: "10.0.1.10"
      port: 8643
      identity_hash: "abc123..."
    - peer_id: "zoe_hospital"
      host: "10.0.2.20"
      port: 8643
      identity_hash: "def456..."
  quorum_threshold: 0.7  # 70% approval needed
```

### 12.3 TLS entre peers (recomendado)

```bash
# Generar certificados mutuos
openssl req -x509 -newkey rsa:4096 -keyout zoe-key.pem -out zoe-cert.pem -days 365 -nodes

# Configurar en production.yaml
federation:
  tls:
    enabled: true
    cert: "/opt/zoe/certs/zoe-cert.pem"
    key: "/opt/zoe/certs/zoe-key.pem"
    ca: "/opt/zoe/certs/ca.pem"
```

### 12.4 Quorum y veto

- **Quorum**: 2/3 de peers activos deben votar YES
- **Veto**: cualquier peer puede vetar por violación de valores
- **Auditoría**: todo se registra en Trajectory Chain de cada ZOE

---

## 13. Cloud gestionado (próximamente)

ZOE Cloud estará disponible en Q4 2026 con:

- AWS / GCP / Azure
- Multi-tenant con aislamiento
- Auto-scaling
- Backup gestionado
- Marketplace integrado

**Estado:** En desarrollo. ETA Q4 2026.

---

## 14. Migración entre plataformas (ZOE Seed Mode)

ZOE Seed Mode (Fase 7E) permite migrar ZOE entre plataformas sin perder identidad ni memoria. El formato .zoe (Sprint 3) es la forma más portable: un archivo contiene todo el organismo.

### 14.1 Formato .zoe (Sprint 3 — portable)

```python
from zoe.core.zoe_packager import ZoePackager

# Crear .zoe
packager = ZoePackager()
packager.package(
    output_path="mi_zoe.zoe",
    organism_id="zoe_fernando",
    memory_db="zoe_data/memory.db",
    capsules_dir="zoe/capsules",
    config_path="zoe/config/production.yaml",
)

# Desempaquetar y ejecutar sin dependencias
packager.unpackage("mi_zoe.zoe", "/path/to/output")
# cd /path/to/output && python zoe_runtime.py
```

Ver [`16_ZOE_FORMAT.md`](16_ZOE_FORMAT.md) para detalle completo del formato.

### 14.2 Pendrive → VPS

```bash
# 1. En el Mac, crear semilla en el SSD
python -c "
from zoe.core.seed_mode import ZOESeed
seed = ZOESeed()
seed.create(
    volume_path='/Volumes/Mi-SSD',
    organism_id='zoe_fernando',
    required_capsules=['base_ethics', 'basic_psychology'],
)
"

# 2. Copiar el contenido del SSD al VPS
rsync -avz /Volumes/Mi-SSD/ZOE/ user@vps:/opt/zoe-seed/

# 3. En el VPS, germinar
ssh user@vps
cd /opt/zoe-seed
python -c "
from zoe.core.seed_mode import ZOESeed
seed = ZOESeed()
report = seed.germinate(custom_paths=['/opt/zoe-seed'])
print(f'Status: {report.status}')
print(f'Backend: {report.embodiment[\"backend_name\"]}')
"
```

### 14.2 VPS → Pendrive

```bash
# 1. En el VPS, crear semilla
python -c "
from zoe.core.seed_mode import ZOESeed
seed = ZOESeed()
seed.create(
    volume_path='/opt/zoe-seed',
    organism_id='zoe_fernando',
)
"

# 2. Copiar al SSD
rsync -avz user@vps:/opt/zoe-seed/ /Volumes/Mi-SSD/ZOE/

# 3. En el Mac, germinar
python -c "
from zoe.core.seed_mode import ZOESeed
seed = ZOESeed()
report = seed.germinate()
"
```

### 14.3 Detección multi-plataforma

ZOESeed detecta automáticamente semillas en:
- macOS: `/Volumes/*/ZOE/seed.json`
- Linux: `/media/<user>/*/ZOE/seed.json`
- Dev mode: `~/.zoe-seed/seed.json`
- Env var: `$ZOE_SEED_PATH`
- Custom: `custom_paths=[...]`

---

## 15. Tabla comparativa de costes

| Plataforma | Coste inicial | Coste mensual | Privacidad | Escalabilidad | Target |
|---|---|---|---|---|---|
| Pendrive SSD | €110 (SSD) | €0-20 (cloud API opcional) | Máxima | 1 usuario | B2C premium |
| Mac local | €0 | €0-20 | Máxima | 1 usuario | Desarrolladores |
| VPS Linux | €5-50 (VPS) | €5-50 + €0-200 (cloud) | Alta | 10-100 usuarios | B2B |
| Docker | €0 | €0-20 | Media | 1-10 usuarios | Dev/test |
| Kubernetes | €50-500 (cloud) | €50-500 | Media | 1000+ usuarios | Enterprise |
| Cloud gestionado | €0 | €20-100 | Media | Ilimitada | B2C masivo (Q4 2026) |

---

## 16. Decision tree

```
¿Quién va a usar ZOE?
│
├─ Yo solo, en mi Mac
│  → Mac local (§6) o Pendrive SSD (§4) si quiero portabilidad
│
├─ Yo solo, pero portátil (viajo, cambio de Mac)
│  → Pendrive SSD (§4)
│
├─ Mi empresa (B2B, federación)
│  → VPS Linux (§7) + Federación B2B (§12)
│
├─ Mi empresa, muchos usuarios
│  → Docker (§10) o Kubernetes (§11)
│
├─ Solo quiero probar sin instalar nada
│  → Cloud API (próximamente Q4 2026)
│
└─ Soy desarrollador y quiero extender ZOE
   → Mac local (§6) o Portátil Linux (§8)
   → Ver Development Guide (15_DEVELOPMENT_GUIDE.md)
```

### Por caso de uso

| Caso de uso | Plataforma recomendada | RAM | Modelo |
|---|---|---|---|
| Cuidado mayores (1 hogar) | Pendrive SSD en Mac del mayor | 8 GB | Qwen 7B |
| Soledad (B2C) | Pendrive SSD o Mac local | 8 GB | Qwen 7B |
| Vigilancia DevOps | VPS Linux | 16 GB | Qwen 14B |
| Investigación | VPS Linux o Mac local | 16 GB | Qwen 14B |
| Federación B2B | 3+ VPS Linux federados | 16 GB c/u | Qwen 14B |
| Asistente personal | Pendrive SSD | 8 GB | Qwen 7B |
| IA heredable | Pendrive SSD (germinable) | 8 GB | Qwen 7B |

---

## Cierre

ZOE se puede desplegar en **6 plataformas diferentes** según el caso de uso. La elección depende de:
- **Privacidad requerida** (offline vs cloud)
- **Portabilidad** (fija vs portátil)
- **Escalabilidad** (1 usuario vs 1000+)
- **Budget** (€0 a €500/mes)

La regla general:
- **B2C premium** → Pendrive SSD (portátil, soberano, heredable)
- **B2B** → VPS Linux (federable, escalable)
- **Enterprise** → Kubernetes (alta disponibilidad)
- **Desarrollo** → Mac local o Docker

**Documentos relacionados:**
- [09_USAGE_GUIDE.md](09_USAGE_GUIDE.md) — cómo usar ZOE una vez desplegado
- [10_HARDWARE_OPTIMIZATION.md](10_HARDWARE_OPTIMIZATION.md) — optimización de rendimiento
- [11_SECURITY_COMPLIANCE.md](11_SECURITY_COMPLIANCE.md) — hardening y cumplimiento
- [13_TROUBLESHOOTING.md](13_TROUBLESHOOTING.md) — problemas comunes

---

*ZOE V1.6.0 — Documento 08: Deployment Guide*
*Julio 2026*
