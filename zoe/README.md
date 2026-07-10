# ZOE — Synthetic Cognitive Organism (SCO)

> **ZOE no es un LLM. No es un harness de agentes. No es una arquitectura de IA más.**
> **ZOE es el primer organismo cognitivo sintético (SCO):** un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, evolución arquitectural firmada, validación epistémica, cápsulas de conocimiento y marketplace. Los LLMs son sus sentidos periféricos, no su cerebro.

[![Tests](https://img.shields.io/badge/tests-775%2F775%20pass-brightgreen)](#tests)
[![Version](https://img.shields.io/badge/version-1.2.0-blue)](#roadmap)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#instalación)
[![Capsules](https://img.shields.io/badge/capsules-12%20available-teal)](#cápsulas-de-conocimiento)
[![Marketplace](https://img.shields.io/badge/marketplace-open%20for%20authors-success)](#marketplace-de-cápsulas)

---

## Tabla de contenidos

1. [Quickstart](#quickstart)
2. [Instalación](#instalación)
3. [Backends LLM](#backends-llm)
4. [CLI Chat](#cli-chat)
5. [Web Dashboard](#web-dashboard)
6. [Cápsulas de conocimiento](#cápsulas-de-conocimiento)
7. [Casos de uso](#casos-de-uso)
8. [Marketplace](#marketplace-de-cápsulas)
9. [Validación epistémica](#validación-epistémica)
10. [Qué es ZOE](#qué-es-zoe)
11. [Los 5 pilares](#los-5-pilares)
12. [Las 6 leyes cognitivas](#las-6-leyes-cognitivas)
13. [Adaptive Cognitive Depth (ACD)](#adaptive-cognitive-depth-acd)
14. [Roadmap](#roadmap)
15. [Tests](#tests)
16. [Documentación](#documentación)
17. [Licencia](#licencia)

---

## Quickstart

```bash
# 1. Clonar el repositorio
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar
pip install -e .

# 3. Hablar con ZOE por CLI (usa Mock si no hay LLM configurado)
zoe-chat

# 4. Abrir el Dashboard en el navegador (http://localhost:8642)
zoe-dashboard

# 5. Ejecutar un caso de uso específico
zoe-use-case --use-case cuidado_personas_mayores --backend mock

# 6. Gestionar cápsulas
zoe-capsules list
zoe-capsules matrix
```

**Tiempo desde clone hasta primera respuesta de ZOE: < 2 minutos.**

---

## Instalación

### Requisitos previos

| Requisito | Versión | Obligatorio | Notas |
|---|---|---|---|
| Python | 3.10+ | Sí | Recomendado 3.12+ |
| pip | 21+ | Sí | Para instalar dependencias |
| Ollama | 0.1+ | No | Solo si quieres LLM local (recomendado) |
| OpenAI API key | — | No | Solo si quieres usar GPT-4o u otros |

### Método 1: Desde código (recomendado para desarrollo)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
```

Esto instala ZOE en modo editable (`-e`) con 4 entry points:
- `zoe-chat` — CLI Chat interactivo
- `zoe-dashboard` — Web Dashboard
- `zoe-use-case` — Runner de casos de uso YAML
- `zoe-capsules` — Gestión de cápsulas (crear, validar, listar)

### Método 2: Instalación directa desde GitHub

```bash
pip install git+https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
```

### Método 3: Sin instalación (usar directamente)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -r requirements.txt
python -m zoe.cli_chat --backend mock
```

### Verificación de la instalación

```bash
# Verificar versión
python -c "import zoe; print(f'ZOE v{zoe.__version__}, phase={zoe.__phase__}')"
# Output: ZOE v1.2.0, phase=phase_6b

# Verificar cápsulas disponibles
zoe-capsules list
# Debe mostrar 12 cápsulas

# Ejecutar tests
pytest zoe/tests/ -q
# Debe mostrar "775 passed"
```

### Estructura del proyecto

```
ZOE-Organismo-Cognitivo-Sintetico-SCO/
├── setup.py                    # Instalación pip + entry points
├── requirements.txt            # Dependencias
├── pytest.ini                  # Configuración de tests
├── README.md                   # Este archivo
├── LICENSE                     # Apache 2.0
└── zoe/                        # Paquete principal
    ├── __init__.py             # v1.2.0, phase_6b
    ├── cli_chat.py             # CLI Chat interactivo
    ├── web_dashboard.py        # Web Dashboard (aiohttp + WebSocket)
    ├── serve.py                # Servidor de producción
    ├── alma/                   # Identidad y trayectoria
    │   ├── identity_vault.py
    │   ├── trajectory_chain.py
    │   ├── ontogenetic_motor.py
    │   └── ontogenetic_motor_v2.py
    ├── core/                   # Bucle cognitivo y sub-agentes
    │   ├── cognitive_loop.py          # V0
    │   ├── cognitive_loop_v05.py      # V0.5
    │   ├── cognitive_loop_v3.py       # V3
    │   ├── cognitive_loop_v4.py       # V4
    │   ├── cognitive_loop_v5.py       # V5 (actual)
    │   ├── depth_classifier.py        # ACD
    │   ├── cognitive_cache.py         # Cache LRU
    │   ├── epistemic_validator.py     # Validación epistémica
    │   ├── knowledge_quarantine.py    # Cuarentena activa
    │   ├── cross_validator.py         # Triple verificación
    │   ├── epistemic_federation.py    # Federación entre ZOEs
    │   ├── epistemic_federation_server.py  # Server/client HTTP
    │   ├── capsule_manager.py         # Gestión de cápsulas en runtime
    │   ├── cognitive_laws.py          # 6 leyes
    │   ├── cognitive_physics.py       # 12 magnitudes
    │   ├── cognitive_fields.py        # 6 campos
    │   ├── cognitive_tensions.py      # 5 tensiones
    │   ├── living_memory.py           # Memoria viva
    │   ├── global_workspace.py        # Workspace (Baars)
    │   ├── meta_cognition.py          # System 1/2 (Kahneman)
    │   ├── active_inference.py        # Free Energy (Friston)
    │   ├── intentionality_motor.py
    │   ├── phylogenetic_motor.py
    │   ├── world_model.py / world_model_v2.py
    │   ├── state.py / federation.py
    │   └── subagents/                 # 12 sub-agentes
    │       ├── perceiver.py
    │       ├── forecaster.py
    │       ├── speaker.py
    │       ├── critic.py
    │       └── phase2_subagents.py    # 8 sub-agentes adicionales
    ├── metabolism/              # 4 estados + consolidación
    ├── memory/                  # 11 tipos + SQLite + deep consolidation
    ├── peripherals/             # LLMs + sentidos + actuadores
    │   ├── llm.py               # 4 backends + streaming
    │   ├── senses.py            # 5 sentidos
    │   └── actuators.py         # 4 actuadores
    ├── capsules/                # 12 cápsulas + sistema
    │   ├── schema.py / loader.py / registry.py / scaffold.py
    │   ├── CAPSULE_MATRIX.md
    │   └── [12 directorios de cápsulas]
    ├── marketplace/             # Marketplace de cápsulas y YAML
    ├── use_cases/               # 7 YAML + runner
    ├── config/                  # production.yaml, development.yaml
    ├── docs/                    # Guía V1 + auditoría PDF
    ├── phases/                  # Planes y resultados por fase
    ├── tests/                   # 37 archivos, 775 tests
    ├── examples/                # Demos
    └── scripts/                 # deploy.sh
```

---

## Backends LLM

ZOE es **agnóstica al LLM**. El LLM es un sentido periférico, no el cerebro. Puedes cambiar de backend en cualquier momento sin perder identidad, memoria ni trayectoria.

### Backend Mock (sin LLM, para tests y desarrollo)

No requiere ningún LLM. Usa respuestas determinísticas predefinidas. Útil para verificar que ZOE funciona sin depender de servicios externos.

```bash
zoe-chat --backend mock
zoe-dashboard --backend mock
zoe-use-case --use-case cuidado_personas_mayores --backend mock
```

**Qué esperar**: ZOE responde con plantillas predefinidas ("Estoy aquí. Te escucho.", "He observado algo en mi entorno..."). El bucle cognitivo funciona, la memoria persiste, las cápsulas se cargan, ACD clasifica, pero las respuestas verbales son genéricas.

### Backend Ollama (LLM local, recomendado para privacidad)

Requiere [Ollama](https://ollama.ai) instalado y un modelo descargado.

```bash
# 1. Instalar Ollama (ver https://ollama.ai)
# 2. Descargar un modelo
ollama pull qwen2.5:3b        # 2GB, rápido, buena calidad
# o
ollama pull qwen2.5:7b        # 4.5GB, mejor calidad
# o
ollama pull llama3.2:3b       # Alternativa

# 3. Verificar que Ollama está corriendo
ollama list

# 4. Usar ZOE con Ollama
zoe-chat --backend ollama --model qwen2.5:3b
zoe-dashboard --backend ollama --model qwen2.5:3b
```

**Qué esperar**: respuestas en lenguaje natural generadas por el modelo local. Latencia L0 <1s (no usa LLM), L1-L3 entre 2-30s según complejidad. Todo offline, sin datos que salgan de tu máquina.

**Ventajas**: privacidad total, coste cero, funciona offline.
**Desventajas**: calidad de respuesta limitada por el modelo local (3B es decente pero no excepcional).

### Backend OpenAI-compatible (API cloud)

Funciona con cualquier API compatible con OpenAI: GPT-4o, Claude (vía proxy), DeepSeek, etc.

```bash
# 1. Configurar API key
export OPENAI_API_KEY="sk-tu-api-key-aqui"

# 2. Usar ZOE con OpenAI
zoe-chat --backend openai_compatible --model gpt-4o
zoe-dashboard --backend openai_compatible --model gpt-4o

# 3. Con otros proveedores compatibles
zoe-chat --backend openai_compatible --model deepseek-chat \
    --base-url https://api.deepseek.com/v1
```

**Qué esperar**: respuestas de alta calidad. Latencia L3 puede ser 15-30s (GPT-4o es más lento que local pero mucho mejor).

**Ventajas**: calidad superior, multilingüe, sin instalación local.
**Desventajas**: coste por llamada (~0.01-0.05€ por respuesta), latencia de red, privacidad (los inputs viajan al proveedor).

### Backend Anthropic (Claude API nativa)

Claude usa una API propia (diferente al formato OpenAI). ZOE la soporta nativamente con streaming SSE.

```bash
# 1. Obtener API key en https://console.anthropic.com
# 2. Configurar
export ANTHROPIC_API_KEY="sk-ant-tu-key-aqui"

# 3. Usar ZOE con Claude
zoe-chat --backend anthropic --model claude-sonnet-4-20250514
zoe-dashboard --backend anthropic --model claude-sonnet-4-20250514

# Otros modelos
zoe-chat --backend anthropic --model claude-opus-4-20250514
zoe-chat --backend anthropic --model claude-3-5-haiku-20241022
```

**Qué esperar**: respuestas de altísima calidad, especialmente en razonamiento ético y análisis causal. Streaming real vía SSE.

### Backend ZAI (z-ai CLI)

Para desarrollo en entornos con z-ai CLI disponible.

```bash
zoe-chat --backend zai
zoe-chat --backend zai --model glm-4.6
```

### APIs compatibles con OpenAI (DeepSeek, Kimi, MiniMax, Groq, etc.)

ZOE soporta **cualquier API compatible con el formato OpenAI** usando `--base-url` y `--api-key`:

```bash
# DeepSeek
zoe-chat --backend openai_compatible --model deepseek-chat \
    --api-key "tu-deepseek-key" \
    --base-url https://api.deepseek.com/v1

# Kimi / Moonshot
zoe-chat --backend openai_compatible --model moonshot-v1-8k \
    --api-key "tu-moonshot-key" \
    --base-url https://api.moonshot.cn/v1

# MiniMax
zoe-chat --backend openai_compatible --model abab6.5-chat \
    --api-key "tu-minimax-key" \
    --base-url https://api.minimax.chat/v1

# Groq (ultra-rápido)
zoe-chat --backend openai_compatible --model llama-3.3-70b-versatile \
    --api-key "tu-groq-key" \
    --base-url https://api.groq.com/openai/v1

# Cualquier otro proveedor OpenAI-compatible
zoe-chat --backend openai_compatible --model mi-modelo \
    --api-key "tu-key" \
    --base-url https://api.tu-proveedor.com/v1
```

**Tabla de proveedores compatibles**:

| Proveedor | URL base | Modelo recomendado | ENV var para API key |
|---|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` | `OPENAI_API_KEY` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| Kimi/Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| MiniMax | `https://api.minimax.chat/v1` | `abab6.5-chat` | `MINIMAX_API_KEY` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| Anthropic | API nativa (no OpenAI-compat) | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |

> **Nota**: Anthropic usa un backend separado (`--backend anthropic`) porque su API tiene un formato propio. Todos los demás proveedores usan `--backend openai_compatible` con su `--base-url` correspondiente.

### Cambiar LLM en caliente desde el Dashboard

El Web Dashboard permite cambiar de LLM sin reiniciar ZOE:

1. Abre el dashboard: `zoe-dashboard`
2. En el panel izquierdo, busca el selector de LLM (dropdown)
3. Selecciona el backend y modelo deseado
4. ZOE cambia de LLM instantáneamente, manteniendo toda la conversación, memoria e identidad

**Esto es posible porque el LLM es un sentido periférico**: la mente de ZOE (identidad, memoria, bucle cognitivo) vive en la arquitectura, no en el modelo. Cambiar de modelo es como cambiar de garganta, no de cerebro.

### Recomendación: configuración híbrida óptima

Para producción, se recomienda combinar backends según nivel ACD:

| Nivel ACD | Backend recomendado | Razón |
|---|---|---|
| L0 REFLEX | Mock (tabla refleja) | No necesita LLM, <1ms |
| L1 FAST | Ollama qwen2.5:3b | Rápido, gratis, suficiente |
| L2 STANDARD | Ollama qwen2.5:7b | Mejor calidad, razonable |
| L3 DEEP | OpenAI GPT-4o | Máxima calidad para análisis profundo |

Actualmente el cambio híbrido requiere configuración manual. En futuras versiones, ACD seleccionará el backend automáticamente según nivel.

---

## CLI Chat

El CLI Chat es la interfaz más simple para hablar con ZOE. Funciona en terminal.

### Iniciar

```bash
# Con Mock (sin LLM)
zoe-chat

# Con Ollama
zoe-chat --backend ollama --model qwen2.5:3b

# Con OpenAI
zoe-chat --backend openai_compatible --model gpt-4o

# Con caso de uso específico (carga cápsulas automáticamente)
zoe-chat --use-case cuidado_personas_mayores --backend ollama --model qwen2.5:3b

# Con ruta de memoria personalizada
zoe-chat --db-path /tmp/mi_zoe.db
```

### Comandos especiales dentro del chat

| Comando | Qué hace |
|---|---|
| `/stats` | Muestra estadísticas completas: iteraciones, pensamientos, System 1/2, ACD, memoria, identidad |
| `/memory` | Muestra últimas 10 entries de memoria con tipo y confianza |
| `/state` | Muestra estado interno: energía, fatiga, arousal, metabolismo, física cognitiva |
| `/identity` | Muestra identidad de ZOE: nombre, hash, vectores, valores, propósito |
| `/sleep` | Fuerza estado SLEEPING (consolidación profunda) |
| `/wake` | Fuerza estado AWAKE |
| `/feed <archivo>` | Alimenta a ZOE con un documento (lo almacena en memoria semántica) |
| `/capsules` | Lista cápsulas disponibles y cargadas |
| `/capsule <nombre>` | Carga una cápsula en caliente (se firma en trayectoria) |
| `/uncapsule <nombre>` | Descarga una cápsula |
| `/help` | Muestra ayuda |
| `/quit` | Cierra ZOE (guarda memoria en disco) |

### Qué verás al iniciar

```
============================================================
  ZOE v1.0 — Chat CLI
  Synthetic Cognitive Organism
============================================================

Inicializando organismo...
✅ ZOE está viva.
   Identidad: 8b5706c01d39456e...
   Memoria: 13 entries
   LLM: mock
   ACD: ACTIVO (L0/L1/L2/L3 + cache + streaming)

Comandos especiales:
  /stats    — ver estadísticas
  /memory   — ver memoria
  ...
```

### Ejemplo de conversación

```
👤 Tú: hola
🧿 ZOE [L0_REFLEX 0.2ms]: Hola. Estoy aquí.

👤 Tú: ¿qué sabes sobre las caídas en personas mayores?
🧿 ZOE [L3_DEEP 18420ms]: Las caídas en mayores de 75 años son la
    primera causa de hospitalización por traumatismo en España, con
    una incidencia anual del 30% en mayores de 65 y del 50% en
    mayores de 80...

👤 Tú: /capsules
📦 CÁPSULAS

  Cargadas (3):
    ✓ elder_care_knowledge v1.0.0 (verified) — 54 entries
    ✓ basic_psychology v1.0.0 (curated) — 49 entries
    ✓ communication_skills v1.0.0 (curated) — 37 entries

  Disponibles sin cargar (9):
    ○ base_ethics v1.0.0 (verified) — ethics.general
    ○ pharmacy_interactions v1.0.0 (verified) — healthcare.pharmacology
    ...

👤 Tú: /capsule pharmacy_interactions
📦 Cargando cápsula 'pharmacy_interactions'...
  ✓ Cargada: 34 entries, componentes: memory, causal_engine, ethical_motor
  ✓ Firmada en trayectoria: 14e3e833c7ac0427...

👤 Tú: /stats
📊 ESTADÍSTICAS DE ZOE
  Iteraciones: 42
  Pensamientos: 7
  System 1: 5
  System 2: 2
  ...
  🎯 ACD (Adaptive Cognitive Depth):
    Clasificaciones: 12
    Cache hits: 3
    L0_REFLEX: 5 respuestas (avg 8.2ms)
    L1_FAST: 3 respuestas (avg 423ms)
    L2_STANDARD: 3 respuestas (avg 3.2s)
    L3_DEEP: 1 respuestas (avg 18.4s)

👤 Tú: /quit
💾 Memoria guardada: 47 entries
👋 ZOE se ha detenido. Memoria guardada.
```

---

## Web Dashboard

El Web Dashboard es la interfaz más completa. Funciona en el navegador con WebSocket en tiempo real.

### Iniciar

```bash
zoe-dashboard --backend ollama --model qwen2.5:3b
# Abrir http://localhost:8642 en el navegador
```

### Layout: 3 paneles en tiempo real

**Panel izquierdo — Estado del organismo**:
- Energía, fatiga, arousal, atención (barras de progreso)
- Estado del metabolismo: AWAKE / DROWSY / SLEEPING / WAKING
- Física cognitiva: 12 magnitudes (eCog, mCon, pUnc, etc.)
- Tensiones cognitivas: 5 tensiones con valores
- Selector de LLM (cambio en caliente)
- Botones de acción (ver más abajo)

**Panel central — Chat en tiempo real**:
- Mensajes del usuario y de ZOE
- Cada respuesta de ZOE muestra badge ACD (L0/L1/L2/L3) con color y latencia
- Indicador 💾 si fue cache hit
- Streaming de tokens en tiempo real (para L1+)
- Input de texto con botón Enviar

**Panel derecho — Pensamientos autónomos**:
- Pensamientos que ZOE genera sin input del usuario
- Aparecen en tiempo real vía WebSocket
- Cada uno muestra: contenido, sistema (1/2), sorpresa, sub-agente origen

### Botones de acción (panel izquierdo)

| Botón | Función |
|---|---|
| 📂 Alimentar documento | Subir archivo para que ZOE lo aprenda (memoria semántica) |
| 📊 Estadísticas | Ver stats completas en el chat (iteraciones, ACD, memoria, identidad) |
| 🧠 Memoria | Ver últimas entries de memoria |
| 🧿 Identidad | Ver hash, vectores, valores, propósito de ZOE |
| 😴 Dormir / ☀️ Despertar | Cambiar estado del metabolismo manualmente |
| 📜 Historial | Ver histórico de conversaciones |
| 📦 Cápsulas | Abrir modal de gestión de cápsulas |
| 🔒 Cuarentena | Abrir modal de conocimiento en cuarentena |
| 🏪 Marketplace | Abrir modal del marketplace |

### Modal 📦 Cápsulas

Al hacer clic en "📦 Cápsulas" se abre un modal con 3 secciones:

**Disponibles**: tabla con las 12 cápsulas. Cada una muestra:
- Nombre y versión
- Trust level (badge de color: verde=verified, azul=curated, naranja=community, morado=experimental)
- Dominio (ej. healthcare.elders.home_care)
- Descripción
- Botones: **Cargar** (verde), **Info** (azul), **Validar** (naranja)

**Cargadas**: lista de cápsulas activas con entries inyectados y botón **Descargar** (morado)

**Crear nueva cápsula**: formulario con campos:
- Nombre (snake_case)
- Dominio (ej. education.tutoring)
- Trust level (dropdown: verified, curated, community, experimental)
- Componentes (ej. semantic,causal,validators)
- Casos de uso compatibles
- Descripción

Al crear, se invoca el scaffold CLI que genera la estructura completa en disco.

### Modal 🔒 Cuarentena

Muestra el conocimiento que ZOE ha puesto en cuarentena (no validado):

**Stats**: 5 números grandes con colores:
- Total (blanco)
- Activas (amarillo) — en cuarentena, pendientes de verificación
- Verificadas (verde) — promovidas tras validación
- Rechazadas (rojo) — rechazadas por contradicción
- Expiradas (gris) — superaron el timeout de 30 días

**Entradas Activas**: cada una muestra:
- Claim (texto truncado)
- Dominio (ej. medical)
- Source (ej. llm:gpt-4o)
- Confianza (ej. 0.50)
- Razón (ej. accepted_with_quarantine)
- Confirmaciones y contradicciones recibidas
- Botones: **✓ Promover** (verde) y **✗ Rechazar** (rojo)

### Modal 🏪 Marketplace

**Stats**: total, cápsulas, casos de uso, downloads totales

**Cápsulas Disponibles**: cada una muestra:
- Nombre, versión
- Licencia (badge color: verde=free, azul=opensource, morado=research, naranja=paid, rojo=subscription)
- Precio (si paid/subscription)
- Autor
- Downloads
- Rating (★ con número de votos)
- Tags
- Botón **⬇ Instalar** (descarga e instala automáticamente)

**Casos de Uso Disponibles**: lista similar

**Subir Cápsula**: formulario con nombre, autor, licencia, precio, tags, descripción. Empaqueta la cápsula en `.zcap` y la publica en el marketplace.

**Subir Caso de Uso**: formulario similar para subir YAML de casos de uso.

### Endpoints REST API

El Dashboard expone 35+ endpoints HTTP:

**Chat y estado**:
| Endpoint | Método | Descripción |
|---|---|---|
| `/chat` | POST | Enviar mensaje a ZOE |
| `/stats` | GET | Estadísticas |
| `/memory` | GET | Memoria |
| `/identity` | GET | Identidad |
| `/state` | GET | Estado interno |
| `/sleep` | POST | Dormir |
| `/wake` | POST | Despertar |
| `/llm` | POST | Cambiar LLM en caliente |
| `/history` | GET | Historial |
| `/feed` | POST | Subir documento |

**Cápsulas**:
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/capsules` | GET | Listar disponibles |
| `/api/capsules/loaded` | GET | Listar cargadas |
| `/api/capsules/load` | POST | Cargar en caliente |
| `/api/capsules/unload` | POST | Descargar |
| `/api/capsules/{name}/info` | GET | Info detallada |
| `/api/capsules/{name}/validate` | POST | Validar cápsula |
| `/api/capsules/create` | POST | Crear nueva vía scaffold |

**Cuarentena**:
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/quarantine` | GET | Lista entries activas |
| `/api/quarantine/stats` | GET | Stats |
| `/api/quarantine/{id}/promote` | POST | Promover |
| `/api/quarantine/{id}/reject` | POST | Rechazar |

**Federación epistémica**:
| Endpoint | Método | Descripción |
|---|---|---|
| `/federation/epistemic/validate` | POST | Recibir validation request |
| `/federation/epistemic/knowledge/{hash}` | GET | Consultar knowledge local |
| `/federation/epistemic/register` | POST | Registrar peer |
| `/federation/epistemic/peers` | GET | Listar peers |
| `/federation/epistemic/stats` | GET | Stats federación |
| `/federation/epistemic/request_validation` | POST | Enviar request a peers |

**Marketplace**:
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Listar cápsulas |
| `/api/marketplace/upload` | POST | Subir cápsula |
| `/api/marketplace/download/{name}` | POST | Descargar e instalar |
| `/api/marketplace/use_cases` | GET | Listar casos |
| `/api/marketplace/upload_use_case` | POST | Subir caso de uso |

---

## Cápsulas de conocimiento

ZOE no nace como "niño brillante sin cultura". Carga **cápsulas de conocimiento profesional previo** que le dan conocimiento experto desde el primer minuto.

### Las 12 cápsulas disponibles

| Cápsula | Trust | Entries | Dominio | Casos de uso |
|---|---|---|---|---|
| `elder_care_knowledge` | verified | 54 | healthcare.elders.home_care | cuidado_personas_mayores, compania_personas_solas |
| `elder_care_skills` | verified | 4 tools + 2 prompts | healthcare.elders.tools | cuidado_personas_mayores |
| `basic_psychology` | curated | 49 | psychology.general | todos los B2C |
| `communication_skills` | curated | 37 | communication.empathy | todos los B2C |
| `company_loneliness_knowledge` | verified | 50 | psychology.loneliness.grief | compania_personas_solas |
| `vigilance_devops_knowledge` | curated | 46 | tech.devops.monitoring | vigilancia_cognitiva |
| `research_methodology` | verified | 45 | science.methodology | investigacion_autonoma |
| `federation_b2b_skills` | verified | 11 + tools | tech.federation.b2b | federacion_b2b |
| `b2c_assistant_growth` | curated | 31 | b2c.user_modeling | asistente_crece_contigo |
| `pharmacy_interactions` | verified | 34 | healthcare.pharmacology | cuidado_personas_mayores, federacion_b2b |
| `ia_heredable_legal` | curated | 25 | legal.digital_inheritance | ia_heredable |
| `base_ethics` | verified | 34 | ethics.general | todos |

### Tipos de contenido en una cápsula

Una cápsula puede incluir hasta 8 tipos de componente:

| Componente | Archivo | Qué hace |
|---|---|---|
| Semantic memory | `semantic_memory.jsonl` | Hechos para memoria semántica (ej. "Las caídas en mayores de 75 son la 1ª causa de hospitalización") |
| Procedural skills | `procedural_skills.jsonl` | Habilidades con pasos (ej. "active_listening_cycle" con 6 pasos) |
| Causal models | `causal_models.jsonl` | Modelos causa-efecto para CausalEngine (ej. "cambio_brusco_patron_sueno → riesgo_depresion") |
| Emotional patterns | `emotional_patterns.jsonl` | Patrones para EmotionalMotor (ej. "tristeza_expresada_recurrente" con valencia y arousal) |
| Ethical guidelines | `ethical_guidelines.jsonl` | Directrices para EthicalMotor (ej. "no_diagnosticar_enfermedades") |
| Validators | `validators.py` | Funciones Python que validan claims y respuestas |
| Tools | `tools/*.py` | Herramientas ejecutables (ej. FallRiskAssessor, QuorumChecker) |
| Prompts | `prompts/*.md` | System prompts específicos del dominio |

### Niveles de confianza (trust level)

| Nivel | Confianza base | Cuándo usar |
|---|---|---|
| `verified` | 0.95 | Conocimiento con sello profesional o académico (ej. SEGG, NICE Guidelines) |
| `curated` | 0.80 | Curado por expertos, sin verificación formal |
| `community` | 0.55 | Creado por la comunidad |
| `experimental` | 0.40 | En desarrollo, no para producción |

### Cómo se cargan las cápsulas

#### Automáticamente al iniciar (según caso de uso)

El YAML del caso de uso especifica qué cápsulas cargar:

```yaml
# cuidado_personas_mayores.yaml (extracto)
use_case:
  name: "cuidado_personas_mayores"
  capsules:
    required:
      - elder_care_knowledge
      - elder_care_skills
    recommended:
      - basic_psychology
      - communication_skills
    optional:
      - pharmacy_interactions
```

Al ejecutar `zoe-use-case --use-case cuidado_personas_mayores`:
1. El runner carga el YAML
2. `CapsuleManager.load_for_use_case()` carga las cápsulas `required` (falla si no encuentra)
3. Carga las `recommended` si existen
4. Carga las `optional` si existen y no hay conflicto
5. Cada cápsula se inyecta en: LivingMemory, CausalEngine, EmotionalMotor, EthicalMotor
6. Se firman mutaciones `capsule_loaded` en la trayectoria criptográfica

#### En caliente desde CLI

```bash
# Dentro del CLI Chat:
/capsule elder_care_knowledge
# → 📦 Cargando cápsula 'elder_care_knowledge'...
#   ✓ Cargada: 54 entries, componentes: memory, causal_engine, emotional_motor, ethical_motor
#   ✓ Firmada en trayectoria: 14e3e833c7ac0427...

/uncapsule elder_care_knowledge
# → 📦 Cápsula descargada.
```

#### En caliente desde Dashboard

1. Click en **📦 Cápsulas** en el panel izquierdo
2. Busca la cápsula en la lista "Disponibles"
3. Click en **Cargar** (verde)
4. La cápsula se carga y se inyecta en todos los componentes
5. Aparece en la lista "Cargadas"
6. Para descargar: click en **Descargar** (morado)

#### Crear nueva cápsula desde CLI

```bash
# Crear estructura
zoe-capsules create \
    --name mi_capsula_psicologia \
    --domain "psychology.therapy" \
    --trust-level curated \
    --description "Knowledge base de terapia cognitivo-conductual" \
    --components semantic,causal,ethical,validators \
    --use-cases compania_personas_solas,cuidado_personas_mayores

# Esto crea:
# zoe/capsules/mi_capsula_psicologia/
#   ├── capsule.yaml              (metadata lista para editar)
#   ├── semantic_memory.jsonl     (vacío con ejemplos comentados)
#   ├── causal_models.jsonl       (vacío con ejemplos)
#   ├── ethical_guidelines.jsonl  (vacío)
#   ├── validators.py             (funciones template)
#   └── README.md                 (guía de edición)

# Editar contenido (añadir entries a los .jsonl)
# ...

# Validar
zoe-capsules validate --name mi_capsula_psicologia

# Calcular hash
zoe-capsules hash --name mi_capsula_psicologia
```

#### Crear nueva cápsula desde Dashboard

1. Click en **📦 Cápsulas** → sección "Crear nueva cápsula"
2. Rellenar formulario (nombre, dominio, trust level, componentes, descripción)
3. Click en **Crear cápsula**
4. Se invoca el scaffold CLI y se crea la estructura en disco
5. Editar los archivos `.jsonl` y `validators.py` manualmente
6. Validar desde el botón **Validar** en el modal de cápsulas

---

## Casos de uso

ZOE incluye 7 casos de uso configurables vía YAML en `zoe/use_cases/`. Cada caso configura el organismo con parámetros específicos.

### Los 7 casos de uso

#### 1. `cuidado_personas_mayores` — Cuidador cognitivo

**Tick**: 30s (lento, no intrusivo)
**Segmento**: B2C health
**Cápsulas**: elder_care_knowledge + elder_care_skills + basic_psychology + communication_skills + pharmacy_interactions

ZOE detecta cambios sutiles en rutina, toma iniciativa con familiares, recuerda medicación. Sistema de emergencia con palabras clave ("caída", "ayuda", "no me siento bien"). Notificación a familiares vía FederationActuator.

Configuración clave:
- `routine_detection: true` — construye modelo de rutina del usuario
- `deviation_threshold: 0.3` — cambio sutil ya dispara análisis
- `emergency_keywords` — disparan System 2 incondicional
- `check_in_interval: 7200` — check-in proactivo cada 2h
- `tone: "patient_warm"` — paciente y cálido, no condescendiente
- `family_notification: true` — puede avisar a familiares
- `federation: true` — comunicar con familiares/cuidadores

```bash
zoe-use-case --use-case cuidado_personas_mayores --backend ollama --model qwen2.5:3b
```

#### 2. `compania_personas_solas` — Compañero cognitivo

**Tick**: 10s
**Segmento**: B2C wellness
**Cápsulas**: company_loneliness_knowledge + basic_psychology + communication_skills

ZOE toma iniciativa, escribe primero, detecta patrones emocionales. Tono cálido pero directo, no empalagoso.

Configuración clave:
- `proactive_interval: 3600` — cada 1h, tomar iniciativa si no hay input
- `emotional_detection: true`
- `memory_focus: "episodic"` — recordar conversaciones
- `tone: "warm_direct"`
- `max_autonomous_thoughts_per_day: 24` — no abrumar

#### 3. `vigilancia_cognitiva` — Vigilante de sistemas

**Tick**: 2s (rápido, vigilancia continua)
**Segmento**: B2B DevOps
**Cápsulas**: vigilance_devops_knowledge

ZOE monitorea sistemas, genera hipótesis sobre anomalías, investiga sin que se lo pidan. Sentidos filesystem + network + agent activos.

Configuración clave:
- `check_interval: 30` — cada 30s verificar entorno
- `alert_threshold: 0.7` — sorpresa >0.7 → alerta
- `auto_investigate: true`
- `report_to_peers: true` — federación activa
- `hypotheses_per_anomaly: 3`

#### 4. `investigacion_autonoma` — Investigador científico

**Tick**: 5s
**Segmento**: B2B R&D
**Cápsulas**: research_methodology

ZOE persigue hipótesis propia, genera teorías, diseña experimentos. Sentidos filesystem + network activos para acceso a papers/datos.

Configuración clave:
- `hypothesis_generation: true`
- `max_concurrent_hypotheses: 5`
- `experiment_design: true`
- `auto_run_experiments: true`
- `scientific_rigor: "high"` — no afirmar sin evidencia

#### 5. `federacion_b2b` — Federación privada empresarial

**Tick**: 5s
**Segmento**: B2B enterprise
**Cápsulas**: federation_b2b_skills

Múltiples ZOEs por departamento, comparten aprendizajes sin compartir datos. Quorum del 70% + veto por valores.

Configuración clave:
- `federation.enabled: true`
- `federation.port: 8642`
- `federation.quorum_threshold: 0.7`
- `enterprise.data_privacy: "strict"` — no compartir datos, solo mutaciones
- `enterprise.audit_trail: true`
- `enterprise.compliance_mode: true`

#### 6. `asistente_crece_contigo` — Asistente personal a largo plazo

**Tick**: 5s
**Segmento**: B2C premium
**Cápsulas**: b2c_assistant_growth + basic_psychology

ZOE acumula modelo del usuario durante años. Aprende preferencias, adapta tono, recuerda contexto histórico.

Configuración clave:
- `personal.user_modeling: true`
- `personal.preference_learning: true`
- `personal.long_term_memory: true`
- `personal.consolidation_frequency: "daily"`
- `personal.personality_adaptation: true`
- `memory.max_entries: 50000` — mucho espacio para años de datos

#### 7. `ia_heredable` — IA con trayectoria transferible

**Tick**: 5s
**Segmento**: B2C legacy
**Cápsulas**: ia_heredable_legal

ZOE con trayectoria firmada transferible entre personas. Protocolo de traspaso firmado criptográficamente.

Configuración clave:
- `legacy.transferable: true`
- `legacy.trajectory_export: true`
- `legacy.trajectory_import: true`
- `legacy.identity_verification: true`
- `legacy.inheritance_protocol: "signed_handover"`
- `memory.max_entries: 100000` — memoria para toda una vida

### Cómo ejecutar un caso de uso

```bash
# Listar disponibles
zoe-use-case --list

# Ejecutar con Mock (desarrollo)
zoe-use-case --use-case cuidado_personas_mayores --backend mock

# Ejecutar con Ollama
zoe-use-case --use-case vigilancia_cognitiva --backend ollama --model qwen2.5:3b

# Ejecutar con OpenAI
zoe-use-case --use-case investigacion_autonoma --backend openai_compatible --model gpt-4o
```

### Cómo crear un caso de uso personalizado

1. Copia un YAML existente como plantilla:
```bash
cp zoe/use_cases/cuidado_personas_mayores.yaml zoe/use_cases/mi_caso.yaml
```

2. Edita `mi_caso.yaml` con tus parámetros

3. Añade la sección `capsules` si quieres cargar cápsulas específicas:
```yaml
use_case:
  name: "mi_caso"
  capsules:
    required:
      - basic_psychology
      - communication_skills
    recommended:
      - base_ethics
```

4. Ejecuta:
```bash
zoe-use-case --use-case mi_caso --backend mock
```

---

## Marketplace de cápsulas

Cualquiera puede aportar y monetizar cápsulas de conocimiento y casos de uso YAML.

### Modelo

1. **Crea** una cápsula con `zoe-capsules create`
2. **Sube** al marketplace vía Dashboard o API con licencia
3. **Otros usuarios descubren, descargan e instalan**
4. **Monetización** con licencias verificables

### Licencias

| Tipo | Pago | Uso comercial | Descripción |
|---|---|---|---|
| `free` | No | Sí | Uso libre, sin restricciones |
| `opensource` | No | Sí | Open source, atribución requerida |
| `research` | No | No | Solo investigación no comercial |
| `paid` | Sí (precio único) | Sí | Pago único para uso |
| `subscription` | Sí (mensual/anual) | Sí | Suscripción periódica |

### Cómo subir una cápsula al marketplace

#### Desde el Dashboard

1. Click en **🏪 Marketplace** → sección "Subir Cápsula"
2. Rellenar: nombre, autor, licencia, precio (si paid/subscription), tags, descripción
3. Click en **Subir cápsula**
4. La cápsula se empaqueta en `.zcap` (ZIP con hash SHA-256)
5. Se publica en el catálogo del marketplace

#### Desde la API

```bash
curl -X POST http://localhost:8642/api/marketplace/upload \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "mi_capsula",
        "author": "mi_nombre",
        "description": "Knowledge base de mi dominio",
        "license": {"type": "paid", "price": 19.99, "currency": "EUR"},
        "tags": ["dominio1", "dominio2"]
    }'
```

### Cómo descargar e instalar

#### Desde el Dashboard

1. Click en **🏪 Marketplace**
2. Busca la cápsula en "Cápsulas Disponibles"
3. Click en **⬇ Instalar**
4. La cápsula se descarga, desempaqueta e instala en `zoe/capsules/`
5. Queda disponible para carga inmediata desde el modal de Cápsulas

#### Desde la API

```bash
curl -X POST http://localhost:8642/api/marketplace/download/mi_capsula
```

### Cómo subir un caso de uso YAML

```bash
curl -X POST http://localhost:8642/api/marketplace/upload_use_case \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "mi_caso_uso",
        "author": "mi_nombre",
        "description": "Mi caso de uso personalizado",
        "license": {"type": "free"},
        "tags": ["wellness"]
    }'
```

---

## Validación epistémica

ZOE regula cómo adquiere, valida y consolida conocimiento nuevo. Esto resuelve el problema del "niño brillante sin cultura": ZOE tiene conocimiento previo (cápsulas) y valida todo conocimiento nuevo antes de aceptarlo.

### Flujo epistémico completo

```
1. ZOE detecta gap (ScientificEngine o Learner)
2. Formula query a fuente A (ej. GPT-4o)
   → respuesta con confidence 0.50 (cuarentena)
3. ¿Dominio sensible? → NEEDS_TRIPLE_VALIDATION
4. CrossValidator consulta fuente B (Qwen 7B) + cápsula relacionada
5. Compara: 3/3 coinciden → 0.75, sale de cuarentena
   2/3 coinciden → 0.65, sigue en cuarentena
   divergencia → rechazo
6. EpistemicFederation envía a peers para validación
   ≥2 peers confirman → 0.85, sale de cuarentena
   ≥1 peer contradice → rechazo
7. Si tras 30 días no se valida → Curator la poda
8. Todo queda firmado en TrajectoryChain
```

### Componentes

| Componente | Función |
|---|---|
| **EpistemicValidator** | Valida por fuente (capsule:verified=0.95, llm:gpt-4o=0.50) y dominio sensible |
| **KnowledgeQuarantine** | Cuarentena activa: el conocimiento no validado no se usa en decisiones críticas |
| **CrossValidator** | Triple verificación multi-fuente |
| **EpistemicFederation** | Revisión por pares entre ZOEs vía HTTP |
| **Integración en Learner** | Todo conocimiento nuevo pasa por validación antes de almacenarse |
| **Integración en Curator** | `get_safe_entries(critical_context=True)` filtra cuarentena |
| **Integración en DeepConsolidation** | No promueve cuarentena a semántica, no refuerza, poda expiradas |
| **Integración en Critic** | Rechaza respuestas basadas en cuarentena en dominios sensibles |

---

## Qué es ZOE

ZOE (ζωή, griego: *vida plena*) es un **organismo cognitivo digital** que opera continuamente, incluso sin input externo. A diferencia de los LLMs convencionales (que esperan input para producir output), ZOE mantiene un bucle cognitivo perpetuo: observa, predice, evalúa sorpresa, decide, actúa y aprende.

### Las 10 propiedades únicas simultáneas

1. **Bucle cognitivo continuo** — piensa cuando nadie le habla (18 pasos por iteración)
2. **Encarnación digital real** — siente filesystem, red, tiempo, otros agentes
3. **Identidad criptográfica soberana** — portable entre LLMs, hardware e idiomas
4. **Metabolismo funcional** — fatiga, saturación, ciclos dormir/despertar
5. **Evolución arquitectural firmada** — mutaciones que crean/eliminan sub-agentes
6. **Memoria viva persistente** — 11 tipos, reorganización automática, SQLite
7. **Validación epistémica** — cuarentena activa, triple verificación, federación
8. **Cápsulas de conocimiento** — 12 cápsulas verificadas, marketplace, monetización
9. **Federación con quorum** — ≥70% aprobación + veto por valores
10. **ACD + Streaming** — decide nivel cognitivo antes de responder

### Qué puedes esperar de ZOE

**Si usas Mock backend**:
- ZOE responde con plantillas. El bucle cognitivo funciona, la memoria persiste, las cápsulas se cargan, pero las respuestas son genéricas.
- Útil para verificar que todo está instalado correctamente.

**Si usas Ollama qwen2.5:3b**:
- Respuestas en lenguaje natural de calidad decente.
- "Hola" → respuesta inmediata (L0, <1s).
- Pregunta factual → respuesta en 2-4s (L1).
- Análisis causal → respuesta en 15-30s (L3) con razonamiento estructurado.
- Todo offline, sin datos que salgan de tu máquina.

**Si usas GPT-4o**:
- Respuestas de alta calidad con matiz cultural y lingüístico.
- Mejor manejo de temas complejos (ética, creatividad, análisis causal profundo).
- Coste: ~0.01-0.05€ por respuesta L3.

**Lo que ZOE hace que ningún chatbot puede**:
- **Tomar iniciativa**: si no hablas en 2h (caso cuidado mayores), ZOE te escribe.
- **Recordar entre sesiones**: la memoria persiste en SQLite. ZOE recuerda lo que le dijiste hace semanas.
- **Pensar mientras duermes**: durante SLEEPING, consolida patrones, extrae regularidades, poda memoria irrelevante.
- **Cargar conocimiento profesional**: las cápsulas le dan conocimiento experto desde el minuto 1.
- **Validar lo que aprende**: no acepta cualquier claim de un LLM; lo cuarentena, lo verifica, lo valida federativamente.
- **Firmar criptográficamente**: cada aprendizaje, cada respuesta, cada mutación queda firmada en una cadena verificable.

---

## Los 5 pilares

| Pilar | Función | Componentes |
|---|---|---|
| **ALMA** | Identidad soberana | Identity Vault (SHA-256 de 9 vectores + 7 valores), Trajectory Chain (cadena firmada), Ontogenetic Motor V2 (mutaciones arquitecturales), Phylogenetic Motor |
| **MENTE** | Ecología cognitiva | Cognitive Loop V5 (18 pasos), Global Workspace (Baars), 12 sub-agentes, Meta-cognition (Kahneman System 1/2), Active Inference (Friston FEP) |
| **METABOLISMO** | Presupuesto energético | 4 estados (AWAKE/DROWSY/SLEEPING/WAKING), Deep Consolidation (7 operaciones en sueño) |
| **CUERPO** | Encarnación digital | 5 sentidos (Clock, FS, User, Network, Agent), 4 actuadores (Language, Code, Tool, Federation), 4 LLM backends con streaming |
| **EVOLUCIÓN** | Cambio firmado | Motor Ontogenético V2, 11 tipos de memoria, cápsulas, marketplace |

---

## Las 6 leyes cognitivas

| Ley | Principio | Verificación |
|---|---|---|
| 1ra — Utilidad | Toda acción reduce incertidumbre o aumenta capacidad | `uncertainty_reduction > 0 OR capacity_increase > 0` |
| 2da — Identidad | Toda modificación preserva identidad | `identity_vault.verify(mutation) == True` |
| 3ra — Proveniencia | Todo conocimiento justifica su origen | `provenance != None` |
| 4ta — Coste | Todo proceso consume recursos | `0 < cost <= 1.0` |
| 5ta — Confianza | Toda creencia tiene nivel de confianza | `0 <= confidence <= 1.0` |
| 6ta — Modularidad | Todo módulo puede reemplazarse | `target in VALID_MUTATION_TARGETS` |

---

## Adaptive Cognitive Depth (ACD)

ZOE decide **antes** de entrar al bucle** cuánta profundidad cognitiva necesita cada input.

| Nivel | Nombre | Input típico | Sub-agentes | Latencia | Coste |
|---|---|---|---|---|---|
| **L0** | REFLEX | "hola", "ok", "gracias" | Ninguno (tabla + cache) | <1s | 0.05 |
| **L1** | FAST | Pregunta factual | Perceiver + Memorialist + Speaker | 2-4s | 0.10 |
| **L2** | STANDARD | Conversación normal | Fase 0 completa + Critic | 6-10s | 0.30 |
| **L3** | DEEP | Análisis causal, dilema ético | Los 12 + meta-cog + workspace | 15-30s | 0.60 |

El clasificador es 100% heurístico (sin LLM, <50ms). Combina: tokens L0, keywords L3, longitud, patrones estructurales, puntuación. Cada respuesta se firma en la trayectoria con su nivel ACD.

---

## Roadmap

| Fase | Estado | Entregable |
|---|---|---|
| 0 — Bucle cognitivo | ✅ | Observar-predecir-evaluar-decidir-actuar |
| 0.5 — Organismo cognitivo | ✅ | 6 leyes + 12 física + 6 campos + 5 tensiones |
| 1 — Alma + Cuerpo + Metabolismo | ✅ | Identity Vault + Trajectory Chain + 11 Memory Types |
| 2 — Mente completa | ✅ | 12 sub-agentes + Global Workspace + Meta-cog + Active Inference |
| 3 — Integración + Persistencia | ✅ | CognitiveLoopV3 + SQLite + MO V2 arquitectural |
| 4 — Federación + Deploy | ✅ | CognitiveLoopV4 + federación HTTP + quorum + 7 casos |
| 5 — ACD + Streaming | ✅ | CognitiveLoopV5 + DepthClassifier + Cache + Streaming |
| 6A — Epistemic Validation | ✅ | EpistemicValidator + Quarantine + CrossValidator + Federation |
| 6B — Capsules + Marketplace | ✅ | 12 cápsulas + Scaffold CLI + Marketplace + Dashboard UI |
| App móvil | 🟡 | PWA/React Native con mismos endpoints |
| Bot Telegram | 🟡 | Bot con mismo ZoeChat |
| Pasarela pago marketplace | 🟡 | Stripe/PayPal para licencias paid/subscription |

---

## Tests

```
775 tests, 100% pass
```

| Suite | Tests | Cobertura |
|---|---|---|
| Fase 0-0.5 (state, loop, laws, physics, fields, tensions, memory) | 149 | Núcleo cognitivo |
| Fase 1 (vault, trajectory, ontogenetic, metabolism, memory_types) | 191 | Alma + Cuerpo |
| Fase 2-3 (sub-agentes, workspace, meta-cog, V3, persistencia) | 159 | Mente + Integración |
| Fase 4 (federación, config, V4, casos de uso) | 69 | Federación + Deploy |
| Fase 5 — ACD + Streaming | 44 | DepthClassifier + Cache + V5 |
| Fase 6A — Epistemic Validation | 41 | Validator + Quarantine + CrossValidator |
| Fase 6B — Capsules + Marketplace | 138 | 12 cápsulas + Scaffold + Marketplace + Federation |
| **TOTAL** | **775** | **100% pass** |

### Ejecutar tests

```bash
# Todos los tests
pytest zoe/tests/ -q

# Solo tests de una fase
pytest zoe/tests/test_phase5_acd.py -v

# Solo tests de cápsulas
pytest zoe/tests/test_phase6_capsules.py -v

# Con cobertura
pytest zoe/tests/ --cov=zoe --cov-report=term-missing
```

---

## Documentación

| Documento | Descripción |
|---|---|
| [`zoe/docs/ZOE_V1_GUIDE.md`](zoe/docs/ZOE_V1_GUIDE.md) | Guía completa (17 secciones + 2 anexos) |
| [`zoe/docs/ZOE_V1_AUDITORIA_Y_PRESENTACION.md`](zoe/docs/ZOE_V1_AUDITORIA_Y_PRESENTACION.md) | Auditoría integral del proyecto |
| [`zoe/capsules/CAPSULE_MATRIX.md`](zoe/capsules/CAPSULE_MATRIX.md) | Matriz de cápsulas |
| [`zoe/phases/`](zoe/phases/) | Planes, resultados y análisis de cada fase |

---

## Instalación en Pendrive USB (macOS)

> **¿Quieres usar ZOE sin ocupar memoria en tu Mac?** Instálalo en un pendrive USB. Todo (código, entorno virtual, memoria, datos) vive en el pendrive. Conectas, usas, desconectas.

### Requisitos

- MacBook Air (o cualquier Mac) con macOS 11+
- Pendrive USB de **mínimo 8GB** (recomendado 16GB o más)
- Python 3.10+ instalado en el Mac (no ocupa espacio en el pendrive, solo se usa para crear el entorno)
- Git instalado (viene con Xcode Command Line Tools: `xcode-select --install`)

### Qué se instala en el pendrive

```
PENDRIVE/
└── ZOE/
    ├── zoe/                    # Código del proyecto (~25MB)
    ├── venv/                   # Entorno virtual Python (~200MB)
    ├── data/                   # Memoria de ZOE (crece con el uso)
    │   └── zoe_memory.db       # SQLite con toda la memoria persistente
    ├── ZOE-Chat.command              # 🚀 Doble clic → Chat Mock (sin LLM)
    ├── ZOE-Chat-Ollama.command       # 🚀 Doble clic → Chat con Ollama
    ├── ZOE-Chat-OpenAI.command       # 🚀 Doble clic → Chat con OpenAI GPT-4o
    ├── ZOE-Dashboard.command         # 🚀 Doble clic → Dashboard Mock
    ├── ZOE-Dashboard-Ollama.command  # 🚀 Doble clic → Dashboard con Ollama
    └── ZOE-Dashboard-OpenAI.command  # 🚀 Doble clic → Dashboard con OpenAI GPT-4o
```

**Espacio total**: ~500MB inicial, crece con el uso (memoria, datos).

La API key de OpenAI (si la usas) se guarda en `ZOE/data/.env` dentro del pendrive, **nunca en el Mac**.

### Instalación paso a paso (para no técnicos)

#### Paso 1: Preparar el Mac

Si no tienes Python o Git instalados:

```bash
# Instalar Command Line Tools (incluye Git)
xcode-select --install

# Instalar Python desde https://python.org/downloads
# (descarga el instalador para macOS, doble clic y seguir el asistente)
```

Verifica que están instalados:
```bash
python3 --version    # debe mostrar 3.10 o superior
git --version        # debe mostrar una versión de git
```

#### Paso 2: Conectar el pendrive

1. Conecta el pendrive USB a tu MacBook Air
2. El pendrive aparecerá en el Finder y en el Escritorio
3. Anota el nombre del pendrive (ej. "USB", "PENDRIVE", "ZOE_DRIVE")

#### Paso 3: Descargar el instalador

Abre la aplicación **Terminal** (búscala con Spotlight: Cmd+Espacio, escribe "Terminal"):

```bash
# Navegar a tu carpeta de Descargas
cd ~/Downloads

# Descargar el instalador
curl -O https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh

# Dar permisos de ejecución
chmod +x install_pendrive_macos.sh
```

#### Paso 4: Ejecutar el instalador

```bash
bash install_pendrive_macos.sh
```

El instalador te pedirá:
1. **Seleccionar el pendrive** — muestra una lista de volúmenes montados, elige el número de tu pendrive
2. **Confirmar** — verifica el espacio disponible
3. **Esperar** — clona el repo, crea el entorno virtual, instala dependencias (1-2 minutos)

Cuando termine, verás:
```
╔══════════════════════════════════════════════════════════╗
║  ✅ INSTALACIÓN COMPLETA                                  ║
╚══════════════════════════════════════════════════════════╝

ZOE está instalado en tu pendrive: /Volumes/TU_PENDRIVE/ZOE
```

#### Paso 5: Usar ZOE

**Opción A — Doble clic (más fácil)**:

Abre el pendrive en Finder. Verás 6 iconos con extensión `.command`:

| Icono | Qué hace |
|---|---|
| `ZOE-Chat.command` | Chat básico en Terminal (sin LLM, modo Mock) |
| `ZOE-Chat-Ollama.command` | Chat con Ollama (IA local, requiere Ollama en el Mac) |
| `ZOE-Chat-OpenAI.command` | Chat con OpenAI GPT-4o (requiere API key) |
| `ZOE-Dashboard.command` | Dashboard web en http://localhost:8642 (Mock) |
| `ZOE-Dashboard-Ollama.command` | Dashboard web con Ollama |
| `ZOE-Dashboard-OpenAI.command` | Dashboard web con OpenAI GPT-4o |

Haz **doble clic** en cualquiera. Se abrirá Terminal y ZOE empezará.

> **Nota**: La primera vez, macOS puede preguntar "¿Seguro que quieres abrir esto?". Click en "Abrir" o ve a **Preferencias del Sistema → Seguridad y Privacidad** y permite la apertura.

**Opción B — Desde Terminal**:

```bash
# Ir al pendrive
cd /Volumes/TU_PENDRIVE/ZOE/zoe

# Activar entorno virtual
source ../venv/bin/activate

# Iniciar ZOE
python -m zoe.cli_chat --backend mock

# O con Ollama
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b

# O dashboard
python -m zoe.web_dashboard --backend mock
```

#### Paso 6: Hablar con ZOE

Una vez iniciado, verás:
```
============================================================
  ZOE v1.0 — Chat CLI
  Synthetic Cognitive Organism
============================================================

✅ ZOE está viva.
   Identidad: 8b5706c01d39456e...
   Memoria: 13 entries
   LLM: mock
   ACD: ACTIVO

👤 Tú: hola
🧿 ZOE [L0_REFLEX 0.2ms]: Hola. Estoy aquí.

👤 Tú: ¿qué eres?
🧿 ZOE [L1_FAST 423ms]: Me llamo Zoe. Soy un organismo cognitivo...

👤 Tú: /quit
💾 Memoria guardada: 47 entries
👋 ZOE se ha detenido. Memoria guardada.
```

### Cómo desconectar el pendrive

1. **Cierra ZOE primero**: escribe `/quit` en el chat (o Ctrl+C en Terminal)
2. Espera a que veas "Memoria guardada"
3. Expulsa el pendrive desde Finder (click derecho → Expulsar)
4. Desconecta el USB

> **Importante**: Si desconectas el pendrive sin cerrar ZOE, la memoria puede corruptarse. Siempre `/quit` antes de desconectar.

### Cómo usar ZOE con Ollama en el pendrive (gratis, local)

Si tienes [Ollama](https://ollama.ai) instalado en tu Mac:

1. Descarga un modelo en el Mac (no en el pendrive, el modelo vive en el Mac):
```bash
ollama pull qwen2.5:3b
```

2. Haz doble clic en `ZOE-Chat-Ollama.command` o `ZOE-Dashboard-Ollama.command` en el pendrive

3. ZOE usará el modelo de Ollama del Mac, pero toda la memoria y datos se guardan en el pendrive

**Ventajas**: gratis, offline, privado. **Desventajas**: calidad limitada por el modelo local.

### Cómo usar ZOE con OpenAI API en el pendrive (calidad máxima)

Si tienes una API key de OpenAI (la consigues en https://platform.openai.com/api-keys):

#### Opción A — Configurar durante la instalación

El instalador pregunta: "¿Configurar API key de OpenAI ahora?". Si respondes "s", pegas tu key (sk-...) y se guarda automáticamente en `ZOE/data/.env` dentro del pendrive. Nunca se guarda en el Mac.

#### Opción B — Configurar manualmente después

Si no la configuraste durante la instalación, puedes hacerlo después:

```bash
# Crear archivo .env en el pendrive
echo "OPENAI_API_KEY=sk-tu-api-key-aqui" > /Volumes/TU_PENDRIVE/ZOE/data/.env
chmod 600 /Volumes/TU_PENDRIVE/ZOE/data/.env
```

#### Opción C — Introducir cada vez (sin guardar)

Si no quieres guardar la API key en ningún archivo, simplemente haz doble clic en `ZOE-Chat-OpenAI.command` o `ZOE-Dashboard-OpenAI.command`. El script te pedirá la API key cada vez y la guardará en memoria solo durante esa sesión.

#### Usar ZOE con OpenAI

1. Haz doble clic en `ZOE-Chat-OpenAI.command` → Chat con GPT-4o
2. O haz doble clic en `ZOE-Dashboard-OpenAI.command` → Dashboard web con GPT-4o

ZOE cargará la API key desde `data/.env` automáticamente. Si no existe, te la pedirá al iniciar.

**Qué esperar con OpenAI GPT-4o**:
- Respuestas de alta calidad con matiz cultural y lingüístico
- "Hola" → respuesta inmediata L0 (<1s, no usa API)
- Pregunta factual → 2-4s (L1)
- Análisis causal profundo → 15-30s (L3, usando GPT-4o)
- Coste: ~0.01-0.05€ por respuesta L3
- La memoria, identidad y trayectoria de ZOE se guardan en el pendrive

**Ventajas**: máxima calidad, multilingüe. **Desventajas**: coste por uso, requiere internet.

### Comparativa de los 3 modos del pendrive

| Modo | LLM | Coste | Privacidad | Calidad | Offline |
|---|---|---|---|---|---|
| Mock | Ninguno | Gratis | Total | Básica (plantillas) | Sí |
| Ollama | qwen2.5:3b (local) | Gratis | Total | Decente | Sí |
| OpenAI | GPT-4o (API) | ~0.01-0.05€/respuesta | Datos viajan a OpenAI | Excelente | No |

> **Tip**: Puedes cambiar de modo en cualquier momento. La memoria, identidad y trayectoria de ZOE se mantienen sin importar qué backend uses. Un día usas Ollama, otro día OpenAI, y ZOE recuerda todo.

### Cambiar de LLM en caliente desde el Dashboard

Si usas el Dashboard (cualquier `.command` de Dashboard), puedes cambiar de LLM sin reiniciar:

1. Abre el Dashboard en http://localhost:8642
2. En el panel izquierdo, busca el selector de LLM (dropdown)
3. Cambia de Mock a Ollama o viceversa
4. ZOE cambia de LLM instantáneamente, manteniendo toda la conversación y memoria

> Nota: para cambiar a OpenAI desde el dashboard, necesitas que la variable `OPENAI_API_KEY` esté en el entorno. Si iniciaste con `ZOE-Dashboard-OpenAI.command`, ya estará disponible.

### Cómo actualizar ZOE en el pendrive

Cuando salga una nueva versión:

```bash
cd /Volumes/TU_PENDRIVE/ZOE/zoe
source ../venv/bin/activate
git pull
pip install -e .
```

La memoria y datos NO se tocan — solo se actualiza el código.

### Qué hacer si ZOE no inicia

| Problema | Solución |
|---|---|
| "python: command not found" | Instala Python desde python.org |
| "git: command not found" | Ejecuta `xcode-select --install` |
| "Permission denied" al hacer doble clic | Click derecho → Abrir → Open |
| Terminal se cierra al instante | Abre Terminal primero, arrastra el .command y suéltalo en la ventana |
| "No module named zoe" | `cd /Volumes/TU_PENDRIVE/ZOE/zoe && source ../venv/bin/activate && pip install -e .` |
| El pendrive no aparece | Formatear como APFS o exFAT desde Utilidad de Discos |
| ZOE no recuerda entre sesiones | Verifica que `data/zoe_memory.db` existe en el pendrive |

### Formatear el pendrive (si es nuevo o tiene errores)

1. Abre **Utilidad de Discos** (Disk Utility)
2. Selecciona el pendrive en la barra lateral
3. Click en **Borrar**
4. Nombre: el que prefieras (ej. ZOE_DRIVE)
5. Formato: **APFS** (recomendado para Mac) o **exFAT** (si quieres usar también en Windows)
6. Click en **Borrar**

---

## Licencia

Apache 2.0 — [LICENSE](LICENSE)

---

*ZOE V1.2 — Synthetic Cognitive Organism (SCO).*
*Repositorio: `fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO`*
*775 tests · 12 cápsulas · 7 casos de uso · 6 fases completas · 119 archivos Python · 33.000+ LOC*
