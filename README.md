# ZOE — Synthetic Cognitive Organism (SCO)

> **ZOE no es un LLM. No es un harness de agentes. No es una arquitectura de IA más.**
> **ZOE es el primer organismo cognitivo sintético (SCO):** un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, evolución arquitectural firmada, validación epistémica, cápsulas de conocimiento y marketplace. Los LLMs son sus sentidos periféricos, no su cerebro.

[![Tests](https://img.shields.io/badge/tests-914%2F914%20pass-brightgreen)](#tests)
[![Version](https://img.shields.io/badge/version-1.6.0-blue)](#roadmap)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#instalación)
[![Capsules](https://img.shields.io/badge/capsules-12%20available-teal)](#cápsulas-de-conocimiento)
[![Marketplace](https://img.shields.io/badge/marketplace-open%20for%20authors-success)](#marketplace-de-cápsulas)

---

## Tabla de contenidos

1. [Quickstart para usuario final (sin técnico)](#quickstart-para-usuario-final-sin-conocimientos-técnicos)
2. [Quickstart para desarrolladores](#quickstart-para-desarrolladores)
3. [Instalación](#instalación)
4. [Backends LLM](#backends-llm)
5. [CLI Chat](#cli-chat)
6. [Web Dashboard](#web-dashboard)
7. [Cápsulas de conocimiento](#cápsulas-de-conocimiento)
8. [Casos de uso](#casos-de-uso)
9. [Marketplace](#marketplace-de-cápsulas)
10. [Validación epistémica](#validación-epistémica)
11. [Qué es ZOE](#qué-es-zoe)
12. [Los 5 pilares](#los-5-pilares)
13. [Las 6 leyes cognitivas](#las-6-leyes-cognitivas)
14. [Adaptive Cognitive Depth (ACD)](#adaptive-cognitive-depth-acd)
15. [Roadmap](#roadmap)
16. [Tests](#tests)
17. [Documentación](#documentación)
18. [Instalación en Pendrive USB](#instalación-en-pendrive-usb-macos)
19. [Cognitive Memory Paging (7F)](#cognitive-memory-paging--modelos-grandes-en-mac-con-8gb-ram)
20. [Tutor Mentor Digital (6C)](#tutor-mentor-digital)
21. [Resource Discovery (7A)](#resource-discovery--descubrimiento-automático-de-recursos)
22. [Universal Model Bus (7B)](#universal-model-bus-umb)
23. [Metabolic Resource Planner (7C)](#metabolic-resource-planner)
24. [Embodiment Composer (7D)](#embodiment-composer)
25. [ZOE Seed Mode (7E)](#zoe-seed-mode)
26. [Hardware Optimization & UX (7G)](#hardware-optimization--ux-7g)
27. [Licencia](#licencia)

---

## Quickstart para usuario final (sin conocimientos técnicos)

> **¿Solo quieres usar ZOE sin tocar código?** Sigue estos 4 pasos. No necesitas saber programar.

### Paso 1 — Compra un SSD portátil rápido (recomendado)

ZOE funciona con cualquier pendrive USB, pero para que "piense rápido" necesita un SSD portátil de alta velocidad. Estos tres modelos son ideales y cuestan entre 100€ y 160€:

| Modelo | Capacidad | Velocidad lectura | Precio aprox. | Por qué es ideal |
|---|---|---|---|---|
| **Crucial X10 Pro** | 1 TB | 2100 MB/s | ~110€ | Equilibrado: pequeño, resistente, rápido. **Recomendado por defecto.** |
| **Kingston XS2000** | 1 TB | 2000 MB/s | ~100€ | El más económico, ultra compacto. |
| **SanDisk PRO-BLADE Transport** | 1 TB | 2000 MB/s | ~160€ | Línea profesional, diseño robusto. |

> 💡 **1 TB es suficiente** para ZOE + varios modelos de IA de gran tamaño (un modelo de 70B ocupa ~25 GB).

### Paso 2 — Conecta el SSD a tu Mac con el cable correcto

> ⚠️ **CRÍTICO — Usa SIEMPRE el cable corto que viene dentro de la caja del SSD.**
>
> El cable largo que usas para cargar tu MacBook Air es **USB 2.0** (480 Mbps) y limita el SSD a ~60 MB/s. Si ZOE va lento, en el 90% de los casos el culpable es el cable equivocado.
>
> El cable corto que viene en la caja del SSD es **USB 3.2 Gen 2** (10 Gbps) y permite los 2000 MB/s reales.

1. Saca el SSD de la caja.
2. Conéctalo al Mac con **el cable corto que venía en la caja** (no el de carga).
3. Verás que aparece un nuevo disco en el Escritorio o en Finder → "Ubicaciones".

### Paso 3 — Descarga el instalador de ZOE y ejecútalo

1. Abre la app **Terminal** (puedes buscarla con Spotlight: `Cmd + Espacio` y escribe "Terminal").
2. Copia y pega este comando y pulsa Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh | bash
```

3. El instalador te preguntará:
   - ¿Qué disco quieres usar? → Elige tu SSD (selecciónalo con el número).
   - ¿Quieres configurar OpenAI API key? → Si no tienes una, di "No" (ZOE funcionará en modo local gratis).

4. Espera 2-3 minutos mientras se instala todo en el SSD. **No toques nada del Mac, todo va al SSD.**

### Paso 4 — Habla con ZOE

Cuando termine, verás en tu SSD una carpeta `ZOE/` con varios archivos `.command`. **Doble clic en cualquiera** para arrancar ZOE:

| Archivo | Qué hace |
|---|---|
| `ZOE-Chat.command` | Chat básico (sin IA, gratis, para probar) |
| `ZOE-Chat-Ollama.command` | Chat con IA local gratis (necesitas [instalar Ollama](https://ollama.com) primero) |
| `ZOE-Chat-OpenAI.command` | Chat con GPT-4o (necesitas API key de OpenAI) |
| `ZOE-Dashboard.command` | Dashboard web en `http://localhost:8642` |

**Tiempo total desde comprar el SSD hasta la primera respuesta de ZOE: 15 minutos.**

### ¿Qué velocidad de respuesta tendrás?

Depende del "tamaño de cerebro" (modelo de IA) que uses. Esto es lo que puedes esperar en un MacBook Air M2/M3 con 8 GB de RAM y un SSD de 2000 MB/s:

| Modelo | RAM usada | Velocidad | Experiencia |
|---|---|---|---|
| **Qwen 2.5 3B** (modo rápido) | 2.5 GB | 25-35 tokens/s | ⚡ Más rápido de lo que lees |
| **Qwen 2.5 7B** (modo estándar) | 4.5 GB | 12-18 tokens/s | ✅ Similar a ChatGPT gratuito |
| **Qwen 2.5 14B** (modo profundo) | 8 GB (mmap) | 4-8 tokens/s | 📖 Lectura pausada, ideal análisis |
| **Qwen 2.5 32B** (modo experto, IQ2) | 9 GB (mmap) | 3-6 tokens/s | 🧠 Análisis profundo en background |

> 💡 1 token ≈ 0,75 palabras. Una velocidad de 12 tokens/s = ~9 palabras por segundo = más rápido de lo que lee un humano adulto.

### ¿Atascado? Solución de problemas rápida

| Síntoma | Causa probable | Solución |
|---|---|---|
| ZOE va muy lento | Cable equivocado | Usa el cable corto del SSD (no el del cargador Mac) |
| "Python no encontrado" | Falta Python 3.10+ | Instala desde https://python.org |
| "Ollama no encontrado" | Falta Ollama | Instala desde https://ollama.com |
| SSD no aparece en Finder | Conexión floja | Desconecta y reconecta, prueba otro puerto USB-C |
| "Permiso denegado" | macOS bloquea scripts | Sistema → Privacidad y seguridad → "Permitir de todos modos" |

¿Necesitas ayuda más detallada? Encuentra la guía paso a paso completa en la sección [Instalación en Pendrive USB](#instalación-en-pendrive-usb-macos) más abajo.

---

## Quickstart (para desarrolladores)

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
# Output: ZOE v1.6.0, phase=phase_7g

# Verificar cápsulas disponibles
zoe-capsules list
# Debe mostrar 12 cápsulas

# Ejecutar tests
pytest zoe/tests/ -q
# Debe mostrar "914 passed"
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
    ├── __init__.py             # v1.6.0, phase_7g
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
    │   # Fase 7 (resource stack):
    │   #   model_optimizer.py        — 7F: Cognitive Memory Paging (mmap)
    │   #   resource_planner.py       — 7C: plan ACD+metabolismo+sensible
    │   #   embodiment_composer.py    — 7D: boot sequence del organismo
    │   #   seed_mode.py              — 7E: semilla portátil (germinación)
    │   #   model_optimizer.py 7G ext — P-cores, IQ2_M/IQ3_XS, flash-attn siempre
    │   #                               + APIs usuario final (SSDs, tokens/s, cable)
    ├── metabolism/              # 4 estados + consolidación
    ├── memory/                  # 11 tipos + SQLite + deep consolidation
    ├── peripherals/             # LLMs + sentidos + actuadores
    │   ├── llm.py               # 4 backends + streaming
    │   ├── senses.py            # 5 sentidos
    │   ├── resource_discovery.py # 7A: descubre hardware/cloud/peers
    │   ├── model_bus.py          # 7B: Universal Model Bus (ACD-aware)
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
    ├── tests/                   # 39 archivos, 914 tests
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
| 6B — Capsules + Marketplace | ✅ | 13 cápsulas + Scaffold CLI + Marketplace + Dashboard UI |
| 6C — Tutor Mentor Digital | ✅ | MentorAgent configurable + 3 endpoints REST |
| 7F — Cognitive Memory Paging | ✅ | ModelOptimizer + modelos 14B-72B en pendrive con 8GB RAM |
| 7A — Resource Discovery | ✅ | ResourceDiscoverySense + ResourceGraph + 3 endpoints |
| 7B — Universal Model Bus | ✅ | ModelBus + selección ACD-aware + fallback + from_resource_graph |
| 7C — Metabolic Resource Planner | ✅ | ResourcePlanner + plan ACD+metabolismo+sensible+optimizer |
| 7D — Embodiment Composer | ✅ | EmbodimentComposer + 7 checks + bootstrap 7A→7B→7C→7D + 6 endpoints |
| 7E — ZOE Seed Mode | ✅ | ZOESeed + germinación pendrive→host + 6 endpoints |
| 7G — Hardware Optimization & UX | ✅ | P-cores + IQ2_M/IQ3_XS + flash-attn siempre + SSDs + token rates |
| App móvil | 🟡 | PWA/React Native con mismos endpoints |
| Bot Telegram | 🟡 | Bot con mismo ZoeChat |
| Pasarela pago marketplace | 🟡 | Stripe/PayPal para licencias paid/subscription |

---

## Tests

```
914 tests, 100% pass
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
| Fase 7A-G — Resource Stack | 215 | Discovery + ModelBus + Planner + Embodiment + Seed + Hardware Opt |
| **TOTAL** | **914** | **100% pass** |

### Ejecutar tests

```bash
# Todos los tests
pytest zoe/tests/ -q

# Solo tests de una fase
pytest zoe/tests/test_phase5_acd.py -v

# Solo tests de cápsulas
pytest zoe/tests/test_phase6_capsules.py -v

# Solo tests del stack de recursos (Fase 7A-7G)
pytest zoe/tests/test_phase7a_resource_discovery.py zoe/tests/test_phase7b_model_bus.py zoe/tests/test_phase7c_resource_planner.py zoe/tests/test_phase7d_embodiment_composer.py zoe/tests/test_phase7e_seed_mode.py zoe/tests/test_phase7g_hardware_optimization.py -v

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

> **¿Quieres usar ZOE sin ocupar memoria en tu Mac?** Instálalo en un pendrive USB o SSD portátil. Todo (código, entorno virtual, memoria, datos) vive en el dispositivo. Conectas, usas, desconectas.

### Requisitos

- MacBook Air (o cualquier Mac) con macOS 11+
- Pendrive USB de **mínimo 8GB** (recomendado 16GB o más) **o** SSD portátil USB-C de 1TB (recomendado para modelos grandes)
- Python 3.10+ instalado en el Mac (no ocupa espacio en el pendrive, solo se usa para crear el entorno)
- Git instalado (viene con Xcode Command Line Tools: `xcode-select --install`)

### ¿Pendrive USB barato o SSD portátil rápido?

Depende del "tamaño de cerebro" (modelo de IA) que quieras usar:

| Dispositivo | Velocidad | Capacidad recom. | Modelos que soporta | Precio |
|---|---|---|---|---|
| Pendrive USB 3.0 genérico | 100-400 MB/s | 16-32 GB | Hasta 7B (Q4) | 10-25€ |
| Pendrive USB 3.2 premium | 500-1000 MB/s | 32-64 GB | Hasta 14B (Q4, lento) | 30-60€ |
| **SSD portátil USB-C** (Crucial X10 Pro, Kingston XS2000, SanDisk PRO-BLADE) | **2000 MB/s** | **1 TB** | **Hasta 70B (IQ2_M, mmap)** | **100-160€** |

> ⚠️ **Si quieres usar ZOE con modelos de 14B o más en un MacBook Air de 8 GB, necesitas un SSD portátil de 2000 MB/s.** Con un pendrive USB normal será 10x más lento.

### ⚠️ Regla de oro: el cable USB-C

> **Usa SIEMPRE el cable corto que viene dentro de la caja del SSD.**
>
> El cable largo que usas para cargar tu MacBook Air es **USB 2.0** (480 Mbps) y limita el SSD a ~60 MB/s. Si ZOE va lento, en el 90% de los casos el culpable es el cable equivocado.
>
> El cable corto de la caja del SSD es **USB 3.2 Gen 2** (10 Gbps) y permite los 2000 MB/s reales.
>
> **Síntoma**: ZOE tarda 10+ segundos en responder y la primera palabra aparece muy lenta. → Cambia al cable corto.
> **Síntoma**: ZOE responde en 1-2 segundos y el texto fluye rápido. → Cable correcto.

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

## Cognitive Memory Paging — Modelos grandes en Mac con 8GB RAM

> **¿Tienes un Mac con 8GB RAM y quieres usar modelos de 14B-72B parámetros locales?** ZOE lo hace posible con memory-mapped loading (mmap) desde el pendrive.

### El problema

Un MacBook Air de 8GB RAM tiene ~5GB disponibles tras el sistema operativo. Un modelo de 14B necesita 8GB. Uno de 72B necesita 40GB. **No caben en RAM.**

### La solución: memory-mapped loading (mmap)

1. El modelo vive en el **pendrive** como archivo GGUF (no en el Mac)
2. llama.cpp (el motor de Ollama) lo **memory-mapea** con `mmap`
3. El SO solo carga en RAM las **capas activas** (~2-4GB)
4. El resto del modelo se queda en el **pendrive** hasta que se necesita
5. Es como la **paginación de memoria** de un SO: no toda la memoria está en RAM

### Modelos que puedes usar con 8GB RAM

| Modelo | Tamaño en pendrive | RAM usada (mmap) | Tokens/s en M2/M3 8GB* | Estrategia |
|---|---|---|---|---|
| Qwen 2.5 3B (Q4) | 2 GB | ~1.5 GB | **25-35 t/s** ⚡ | full_ram |
| Qwen 2.5 7B (Q4) | 4.5 GB | ~3 GB | **12-18 t/s** ✅ | mmap_partial |
| **Qwen 2.5 14B** (Q4) | 8 GB | ~3.5 GB | **4-8 t/s** 📖 | mmap_partial |
| **Qwen 2.5 32B** (IQ2_M) | 11 GB | ~3 GB | **3-6 t/s** 🧠 | mmap_full |
| **Qwen 2.5 32B** (Q4_K_M) | 18 GB | ~3 GB | 2-4 t/s | mmap_full |
| **Qwen 2.5 72B** (IQ2_M) | 25 GB | ~3-4 GB | 1-3 t/s | mmap_full |
| **Qwen 2.5 72B** (Q4_K_M) | 40 GB | ~3-4 GB | 0.5-1.5 t/s | mmap_full |
| Llama 3.1 8B (Q4) | 4.5 GB | ~3 GB | 12-18 t/s | mmap_partial |
| DeepSeek R1 14B (Q4) | 8 GB | ~3.5 GB | 4-8 t/s | mmap_partial |
| Llama 3.1 70B (IQ2_M) | 25 GB | ~3-4 GB | 1-3 t/s | mmap_full |

> **\* Velocidades medidas en MacBook Air M2/M3 8GB con SSD de 2000 MB/s y cable USB-C correcto.** Con un pendrive USB normal (400 MB/s), divide las velocidades entre 3-5.
>
> 💡 1 token ≈ 0,75 palabras. 12 t/s = ~9 palabras/s = más rápido de lo que lee un humano.
>
> 💡 **IQ2_M** es una cuantización avanzada (importance matrix) que reduce el modelo a la mitad manteniendo ~95% de la calidad. Ideal para modelos 30B+ en Mac 8GB. Disponible desde la Fase 7G.

> **Sí, puedes ejecutar un modelo de 72B parámetros en tu MacBook Air de 8GB.** Será lento (30-120 segundos por respuesta L3), pero **funciona**.

### Cómo instalar un modelo grande en el pendrive

```bash
# Ejecutar el gestor de modelos grandes
bash zoe/scripts/zoe_large_model_manager.sh

# El script:
# 1. Detecta tu hardware (RAM, chip, P-cores, E-cores)
# 2. Muestra menú con 14 modelos (0.5B a 72B)
# 3. Analiza viabilidad y muestra estrategia + velocidad esperada
# 4. Descarga el modelo al pendrive con OLLAMA_MODELS
# 5. Configura variables de entorno óptimas (mmap, keep_alive, flash_attention, threads=P-cores)
# 6. Crea scripts .command personalizados para Chat y Dashboard
```

### Recomendación óptima para 8GB Mac

| Nivel ACD | Modelo | Estrategia | Tokens/s | Tiempo respuesta L3 |
|---|---|---|---|---|
| L0-L1 (reflejo/rápido) | Qwen 2.5 3B (Q4) | full_ram | 25-35 t/s | <1s |
| L2 (estándar) | Qwen 2.5 7B (Q4) | mmap_partial | 12-18 t/s | 2-4s |
| L3 (profundo) | Qwen 2.5 32B (IQ2_M) | mmap_full | 3-6 t/s | 15-30s |

Instala los 3 modelos en el pendrive y ZOE usará cada uno según el nivel ACD. L0-L1 será rápido (3B en RAM), L3 será potente pero lento (32B IQ2_M vía mmap). El `ModelOptimizer` (Fase 7F + 7G) configura automáticamente:

- `OLLAMA_FLASH_ATTENTION=1` (siempre activado desde 7G)
- `OLLAMA_NUM_THREAD = P-cores` (núcleos de rendimiento, no E-cores)
- `OLLAMA_KEEP_ALIVE` según estrategia (30m para mmap_partial, 60m para mmap_full)

### Requisitos del pendrive para modelos grandes

| Requisito | Para 14B (Q4) | Para 32B (IQ2_M) | Para 72B (IQ2_M) |
|---|---|---|---|
| Capacidad mínima | 16 GB | 32 GB | 64 GB |
| Espacio libre recomendado | 12 GB | 15 GB | 30 GB |
| Formato | APFS o exFAT | APFS o exFAT | APFS |
| Velocidad USB mínima | USB 3.0 (500 MB/s) | USB 3.2 (1000 MB/s) | SSD 2000 MB/s |
| Modelo Ollama | qwen2.5:14b | qwen2.5:32b-iq2_m (HF) | qwen2.5:72b-iq2_m (HF) |
| Cable USB-C requerido | Cualquiera | Cable corto original | Cable corto original |

### Endpoints del ModelOptimizer en el Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/models/system_info` | GET | Info de hardware (RAM, chip, cores, Apple Silicon) |
| `/api/models/recommend` | GET | Recomendaciones de modelo por nivel ACD |
| `/api/models/catalog` | GET | Catálogo de modelos compatibles con tu RAM |
| `/api/models/optimize` | POST | Optimiza un modelo específico (devuelve estrategia + env vars) |

### Ejemplo: optimizar Qwen 2.5 14B con 5GB RAM disponibles

```bash
curl -X POST http://localhost:8642/api/models/optimize \
    -H 'Content-Type: application/json' \
    -d '{"model": "qwen2.5:14b"}'

# Respuesta:
# {
#   "optimization": {
#     "model_name": "qwen2.5:14b",
#     "strategy": "mmap_partial",
#     "available_ram_gb": 5.0,
#     "model_size_gb": 8.0,
#     "estimated_ram_usage_gb": 3.5,
#     "estimated_speed": "medium",
#     "will_work": true,
#     "warning": "Modelo 8.0GB excede RAM (5.0GB). Usando mmap."
#   },
#   "ollama_env": {
#     "OLLAMA_MAX_LOADED_MODELS": "1",
#     "OLLAMA_NUM_PARALLEL": "1",
#     "OLLAMA_KEEP_ALIVE": "30m"
#   }
# }
```

---

## Tutor Mentor Digital

> **Un mentor configurable que guía el crecimiento saludable de ZOE.** No la controla: la orienta hacia direcciones de crecimiento definidas por el usuario.

### Qué hace

Cada N pensamientos autónomos (configurable), el mentor evalúa:
1. ¿El pensamiento está alineado con las áreas de crecimiento priorizadas?
2. ¿Respeta los valores enfatizados?
3. ¿Toca temas prohibidos?
4. ¿Hay patrones repetitivos o negatividad acumulada?

Si detecta desviación, genera una intervención con severidad (critical/medium/low).

### Configuración desde el Dashboard

| Parámetro | Qué hace | Default |
|---|---|---|
| `growth_areas` | Áreas prioritarias: communication, empathy, critical_thinking, creativity, ethical, social... | 4 áreas |
| `emphasized_values` | Valores a enfatizar (de los 7 de ZOE) | 3 valores |
| `forbidden_topics` | Temas que ZOE no debe explorar | Vacío |
| `personality_direction` | balanced / curious / cautious / creative / analytical | balanced |
| `intervention_frequency` | Cada N pensamientos evaluar | 5 |
| `enabled` | Activar/desactivar | true |

### Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/mentor` | GET | Obtener configuración actual |
| `/api/mentor` | POST | Actualizar configuración |
| `/api/mentor/stats` | GET | Estadísticas (evaluaciones, intervenciones, refuerzos) |

### Cápsula basal de conocimiento

ZOE no nace como "sistema cognitivo virgen". La cápsula `zoe_basal_knowledge` se carga **siempre** al iniciar y le da:
- Identidad fundamental ("soy un organismo cognitivo sintético, no un chatbot")
- Valores y propósito (9 vectores, 7 valores, propósito declarado)
- Conocimiento del mundo (tiempo, humanos, lenguaje, internet)
- Reglas de comunicación (tono, frases prohibidas)
- 4 skills procedimentales (honest_response, healthy_growth, respect_autonomy, self_introduction)
- System prompt basal que define su forma de comunicar

---

## Resource Discovery — Descubrimiento automático de recursos

> **ZOE detecta automáticamente qué recursos de cómputo existen a su alrededor.** GPUs, CPUs, instancias Ollama, cloud APIs, otros ZOEs federados, almacenamiento.

### Qué descubre

| Tipo de recurso | Qué detecta | Ejemplo |
|---|---|---|
| **CPU local** | Cores, plataforma | "Local CPU (8 cores)" |
| **GPU local** | Apple Silicon (Metal), NVIDIA (CUDA) | "Apple Silicon (Apple M2)" |
| **Ollama local** | Instancia en localhost:11434 + modelos disponibles | "Ollama (local)" con ["qwen2.5:3b", "qwen2.5:7b"] |
| **Cloud APIs** | OpenAI, Anthropic, DeepSeek, Groq, Kimi, MiniMax (según env vars) | "OpenAI" con ["gpt-4o", "gpt-4o-mini"] |
| **ZOEs peers** | Otros ZOE federados en la red | "ZOE peer: zoe_office" |
| **Almacenamiento** | Disco local, pendrives con ZOE | "Pendrive: ZOE_DRIVE" |

### Cómo funciona

Al iniciar, ZOE ejecuta un scan completo:
1. Detecta hardware local (CPU cores, RAM, GPU, Apple Silicon)
2. Verifica si Ollama está corriendo localmente y lista sus modelos
3. Revisa variables de entorno para cloud APIs configuradas
4. Detecta pendrives montados que contienen ZOE
5. Construye un **ResourceGraph** con todos los nodos

El scan se repite periódicamente (cada 60 segundos por defecto) y se puede forzar manualmente.

### Endpoints del Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/resources` | GET | Grafo completo de recursos disponibles |
| `/api/resources/stats` | GET | Estadísticas (nodos por tipo, modelos disponibles) |
| `/api/resources/scan` | POST | Forzar un nuevo scan de recursos |

### Ejemplo: ver recursos disponibles

```bash
curl http://localhost:8642/api/resources

# Respuesta:
# {
#   "nodes": [
#     {"id": "local_cpu", "type": "cpu", "name": "Local CPU (8 cores)", ...},
#     {"id": "local_gpu_apple", "type": "gpu", "name": "Apple Silicon (Apple M2)", ...},
#     {"id": "ollama_local", "type": "ollama", "name": "Ollama (local)",
#      "models": ["qwen2.5:3b", "qwen2.5:7b"], ...},
#     {"id": "cloud_openai", "type": "cloud_api", "name": "OpenAI",
#      "models": ["gpt-4o", "gpt-4o-mini"], ...},
#     {"id": "storage_local", "type": "storage", "name": "Local disk", ...}
#   ],
#   "node_count": 5,
#   "available_models": ["gpt-4o", "gpt-4o-mini", "qwen2.5:3b", "qwen2.5:7b"]
# }
```

### Integración con ModelOptimizer

El ResourceGraph alimenta al ModelOptimizer: en lugar de que el usuario especifique qué modelo usar, ZOE puede consultar el grafo y seleccionar el modelo óptimo según:
- Qué modelos están disponibles en Ollama local
- Qué cloud APIs tienen API key configurada
- Cuánta RAM hay disponible
- Qué nivel ACD necesita la respuesta

Esto es el primer paso hacia el **ZOE Seed Mode** (Fase 7E): el pendrive contiene el alma y los motores, y al conectar a cualquier Mac, descubre los recursos y construye el cuerpo óptimo.

---

## Universal Model Bus (UMB)

> **ZOE habla con un bus, no con un runtime específico.** El bus gestiona múltiples backends simultáneamente y selecciona el óptimo para cada petición según nivel ACD, dominio, coste, latencia y privacidad.

### Qué hace

El `ModelBus` es un `LLMPeripheral` compuesto. ZOE no sabe si habla con un LLM directo o con un bus. El bus decide internamente:

- **L0/L1** → prefiere backend local, rápido, gratis (Ollama 3B)
- **L2** → balance entre calidad y velocidad (Ollama 7B o cloud barato)
- **L3** → máxima calidad (GPT-4o, Claude, 72B local)
- **Dominio sensible** → excluye cloud por privacidad
- **Fallback automático** → si un backend falla, intenta el siguiente

### 6 estrategias de selección

| Estrategia | Qué hace |
|---|---|
| `ACD_AWARE` (default) | Selecciona según nivel ACD + contexto |
| `PRIORITY` | Mayor prioridad disponible |
| `CHEAPEST` | Menor coste por token |
| `FASTEST` | Menor latencia |
| `LOCAL_FIRST` | Local primero, cloud como fallback |
| `ROUND_ROBIN` | Rotación entre backends disponibles |

### Cómo usar

```python
from zoe.peripherals.model_bus import ModelBus, SelectionStrategy
from zoe.peripherals.llm import OllamaPeripheral, OpenAICompatiblePeripheral, AnthropicPeripheral

bus = ModelBus(strategy=SelectionStrategy.ACD_AWARE)

# Añadir backends
bus.add_backend(
    OllamaPeripheral(model="qwen2.5:3b"),
    name="ollama_3b", priority=10, cost_per_1k=0.0,
    privacy="local", tags=["local", "fast", "cheap"],
)
bus.add_backend(
    OpenAICompatiblePeripheral(model="gpt-4o", api_key="sk-..."),
    name="openai", priority=9, cost_per_1k=0.03,
    privacy="cloud", tags=["cloud", "quality"],
)
bus.add_backend(
    AnthropicPeripheral(model="claude-sonnet-4-20250514", api_key="sk-ant-..."),
    name="anthropic", priority=9, cost_per_1k=0.02,
    privacy="cloud", tags=["cloud", "quality", "ethical"],
)

# El bus selecciona automáticamente
response = await bus.generate("hola", acd_level="L0_REFLEX")
# → usa ollama_3b (gratis, rápido, local)

response = await bus.generate("analiza las causas profundas", acd_level="L3_DEEP")
# → usa anthropic o openai (máxima calidad)

response = await bus.generate("dosis de medicamento", acd_level="L2_STANDARD", sensitive_domain=True)
# → usa ollama_3b (excluye cloud por privacidad médica)
```

### Creación automática desde ResourceGraph

El bus puede construirse automáticamente desde los recursos descubiertos por la Fase 7A:

```python
from zoe.peripherals.model_bus import ModelBus
from zoe.peripherals.resource_discovery import ResourceDiscoverySense

sense = ResourceDiscoverySense()
await sense.observe()
bus = ModelBus.from_resource_graph(sense.get_graph())
# El bus ahora tiene un backend por cada modelo de Ollama local
# y por cada cloud API con API key configurada
```

### Fallback automático

Si el backend seleccionado falla:
1. Se incrementa el contador de fallos del backend
2. Tras `max_fails` (default 3), el backend se marca como no disponible
3. Se intenta con el siguiente backend disponible
4. Si todos fallan, devuelve mensaje de error

### Endpoints del Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/modelbus` | GET | Lista backends registrados |
| `/api/modelbus/stats` | GET | Stats (requests, success_rate, fallbacks, selections) |
| `/api/modelbus/select` | POST | Simula selección (devuelve qué backend se elegiría) |

### Ejemplo: ver qué backend se seleccionaría

```bash
curl -X POST http://localhost:8642/api/modelbus/select \
    -H 'Content-Type: application/json' \
    -d '{"acd_level": "L3_DEEP"}'

# Respuesta:
# {"selected": {"name": "anthropic", "priority": 9, "privacy": "cloud", "tags": ["cloud", "quality"]}}
```

---

## Metabolic Resource Planner

> **El metabolismo decide DÓNDE ejecutar cada tarea cognitiva.** ACD decide cuánto pensar, el metabolismo decide cuándo, el ResourcePlanner decide dónde y con qué modelo.

### Qué hace

El `ResourcePlanner` es la capa de planificación entre ACD y ModelBus. Combina 5 señales:

| Señal | Origen | Ejemplo |
|---|---|---|
| Nivel ACD | DepthClassifier | L0_REFLEX, L3_DEEP |
| Estado metabólico | Metabolism | AWAKE, DROWSY, SLEEPING |
| Dominio sensible | EpistemicValidator | medical, psychological |
| RAM disponible | ModelOptimizer | 5.0 GB |
| Recursos disponibles | ResourceGraph + ModelBus | Ollama 3B local, GPT-4o cloud |

Y devuelve un `ResourcePlan` con:
- Backend seleccionado (ej. "ollama_3b" o "anthropic")
- Modelo específico (ej. "qwen2.5:3b" o "claude-sonnet-4-20250514")
- Estrategia de carga (full_ram / mmap_partial / mmap_full / cloud)
- Variables de entorno Ollama si aplica
- Razón de la selección

### Reglas de planificación

| Condición | Plan | Razón |
|---|---|---|
| L0/L1 + AWAKE | Local, rápido, gratis | `acd_local_fast` |
| L2 + AWAKE | Local, balanceado | `acd_local_balanced` |
| L3 + AWAKE | Máxima calidad (cloud si disponible) | `acd_quality` |
| Cualquier + SLEEPING | Diferir tarea | `sleeping_defer` |
| Cualquier + DROWSY | Solo local (no cloud) | `drowsy_local_only` |
| Dominio sensible | Solo local (no cloud) | `sensitive_local` |
| Local no viable + cloud disponible | Cloud | `cloud_fallback` |
| Sin recursos | No ejecutar | `no_resources` |

### Cómo usar

```python
from zoe.core.resource_planner import ResourcePlanner

planner = ResourcePlanner()

# Plan para L0 (reflejo, rápido)
plan = planner.plan(
    acd_level="L0_REFLEX",
    metabolic_state="awake",
    model_bus=bus,
    model_optimizer=opt,
    available_ram_gb=5.0,
)
# plan.backend_name = "ollama_3b"
# plan.model_name = "qwen2.5:3b"
# plan.strategy = "full_ram"
# plan.reason = "acd_local_fast"

# Plan para L3 (profundo, calidad)
plan = planner.plan(
    acd_level="L3_DEEP",
    metabolic_state="awake",
    model_bus=bus,
    model_optimizer=opt,
    available_ram_gb=5.0,
)
# plan.backend_name = "anthropic"
# plan.model_name = "claude-sonnet-4-20250514"
# plan.strategy = "cloud"
# plan.reason = "acd_quality"

# Plan para dominio médico (sensible)
plan = planner.plan(
    acd_level="L3_DEEP",
    metabolic_state="awake",
    sensitive_domain=True,
    model_bus=bus,
    available_ram_gb=5.0,
)
# plan.backend_name = "ollama_7b"  # local, no cloud
# plan.reason = "sensitive_local"
```

### Recomendación de configuración de modelos

```python
planner = ResourcePlanner()
result = planner.recommend_model_setup(available_ram_gb=5.0)
# result = {
#   "available_ram_gb": 5.0,
#   "total_ram_gb": 8.0,
#   "is_apple_silicon": True,
#   "recommendations": {
#     "L0": {"model": "qwen2.5:3b", "strategy": "full_ram", "speed": "fast"},
#     "L2": {"model": "llama3.1:8b", "strategy": "mmap_partial", "speed": "medium"},
#     "L3": {"model": "qwen2.5:72b", "strategy": "mmap_full", "speed": "very_slow"},
#   }
# }
```

### Endpoints del Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/planner/plan` | POST | Genera un plan (envía acd_level, metabolic_state, etc.) |
| `/api/planner/stats` | GET | Estadísticas (planes generados, distribución de razones) |
| `/api/planner/recommend` | GET | Recomendaciones de modelos por nivel ACD según tu RAM |

### Ejemplo: plan para L3 DEEP

```bash
curl -X POST http://localhost:8642/api/planner/plan \
    -H 'Content-Type: application/json' \
    -d '{"acd_level": "L3_DEEP", "metabolic_state": "awake"}'

# Respuesta:
# {
#   "backend_name": "anthropic",
#   "model_name": "claude-sonnet-4-20250514",
#   "strategy": "cloud",
#   "reason": "acd_quality",
#   "estimated_latency_ms": 700,
#   "estimated_cost_eur": 0.02,
#   "will_work": true
# }
```

### Integración con las fases anteriores

```
Usuario envía mensaje
    ↓
ACD clasifica profundidad (L0/L1/L2/L3)
    ↓
EpistemicValidator detecta dominio sensible
    ↓
ResourcePlanner combina: ACD + metabolismo + dominio + RAM + recursos
    ↓
ResourcePlan: backend + modelo + estrategia
    ↓
ModelBus ejecuta con el backend seleccionado
    ↓
Si falla: ModelBus hace fallback automático
    ↓
Respuesta de ZOE
```

---

## Embodiment Composer

> **Fase 7D — El "boot sequence" del organismo cognitivo.**

Mientras 7A descubre recursos, 7B los expone como backends y 7C planifica cuál usar, **7D INSTANCIA el cuerpo real**: arranca Ollama si hace falta, aplica las variables de entorno del plan, monta el almacén de memoria, registra las cápsulas cargadas y deja el organismo listo para pensar.

Sin 7D, el `ResourcePlan` es solo un documento. Con 7D, el plan se convierte en un **Embodiment**: un cuerpo vivo con estado `RUNNING`, `DEGRADED` o `FAILED`.

### Qué hace

1. **Valida prerrequisitos** (7 checks) antes de intentar nada:
   - `plan_will_work`: el plan no está marcado como inviable (e.g. SLEEPING)
   - `backend_exists`: el backend seleccionado existe en el ModelBus
   - `backend_available`: el backend está marcado como disponible
   - `ram_sufficient`: hay RAM suficiente para la estrategia (`full_ram`/`mmap_partial`)
   - `ollama_running`: si el plan es local, Ollama responde en `localhost:11434`
   - `cloud_api_key`: si el plan es cloud, la API key está configurada
   - `plan_warning`: el plan viene con warning (no bloquea, marca DEGRADED)

2. **Compone el cuerpo** desde un plan:
   - Aplica variables de entorno Ollama (`OLLAMA_MAX_LOADED_MODELS`, etc.)
   - Verifica health-check del backend seleccionado
   - Registra el Embodiment con firma única del plan (hash SHA256)
   - Marca estado final: `RUNNING` (sin warnings), `DEGRADED` (con warnings) o `FAILED` (con blockers)

3. **Bootstrap desde cero** (pipeline completo 7A→7B→7C→7D):
   - Detecta RAM disponible automáticamente (vía `psutil` o `/proc/meminfo`)
   - Ejecuta `ResourceDiscoverySense.observe()` para construir el grafo de recursos
   - Construye `ModelBus.from_resource_graph()` con los backends descubiertos
   - Genera `ResourcePlan` con `ResourcePlanner.plan()`
   - Llama a `compose()` con todo lo anterior

4. **Tear down** limpio:
   - Marca el embodiment como `STOPPED`
   - Lo elimina de la lista de activos
   - No cierra Ollama (lo gestiona el SO) ni borra memoria persistente

### Estados del Embodiment

| Estado | Significado | ¿Puede pensar? |
|---|---|---|
| `BOOTING` | Recursos siendo preparados | No |
| `RUNNING` | Cuerpo listo, sin warnings | ✅ Sí |
| `DEGRADED` | Cuerpo funcional pero con avisos (modelo subóptimo, RAM justa) | ✅ Sí (con cuidado) |
| `STOPPED` | Cuerpo detenido limpiamente | No |
| `FAILED` | No se pudo instanciar (sin recursos críticos) | No |

### Cómo usar

#### Composición desde un plan existente

```python
from zoe.core.embodiment_composer import EmbodimentComposer
from zoe.core.resource_planner import ResourcePlanner
from zoe.peripherals.model_bus import ModelBus

# 1. Construir bus con backends
bus = ModelBus()
bus.add_backend(OllamaPeripheral(model="qwen2.5:3b"), name="ollama_3b", ...)

# 2. Generar plan
planner = ResourcePlanner()
plan = planner.plan(
    acd_level="L0_REFLEX",
    metabolic_state="awake",
    model_bus=bus,
    available_ram_gb=5.0,
)

# 3. Componer cuerpo
composer = EmbodimentComposer()
embodiment = composer.compose(plan, model_bus=bus)

if embodiment.is_running:
    print(f"Cuerpo listo: {embodiment.backend_name} ({embodiment.strategy})")
else:
    print(f"Falló: {embodiment.errors}")
```

#### Bootstrap desde cero (pipeline completo)

```python
from zoe.core.embodiment_composer import EmbodimentComposer

composer = EmbodimentComposer()

# Sin argumentos: detecta todo automáticamente
emb = composer.bootstrap_from_scratch()

# Con configuración explícita
emb = composer.bootstrap_from_scratch(
    acd_level="L3_DEEP",
    metabolic_state="awake",
    sensitive_domain=False,    # dominio médico/psicológico/legal
    available_ram_gb=8.0,      # None = auto-detectar
    capsules=["basic_psychology", "elder_care_knowledge"],
    memory_db_path="~/.zoe/memory.db",
)

print(f"Status: {emb.status}")         # running | degraded | failed
print(f"Backend: {emb.backend_name}")  # anthropic | ollama_7b | ...
print(f"Strategy: {emb.strategy}")     # cloud | full_ram | mmap_partial
print(f"Boot time: {emb.boot_duration_ms:.1f}ms")
```

### Endpoints del Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/embodiment/compose` | POST | Compone un cuerpo desde un plan (o genera el plan al vuelo) |
| `/api/embodiment/bootstrap` | POST | Pipeline completo 7A→7B→7C→7D desde cero |
| `/api/embodiment/status` | GET | Estado global del composer (activos, success rate) |
| `/api/embodiment/list` | GET | Lista embodiments activos con sus detalles |
| `/api/embodiment/tear_down` | POST | Detiene un embodiment (o todos) |
| `/api/embodiment/log` | GET | Log reciente de composiciones (últimas 100) |

#### Ejemplo: bootstrap desde el dashboard

```bash
# Bootstrap un cuerpo L3 DEEP
curl -X POST http://localhost:8642/api/embodiment/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "acd_level": "L3_DEEP",
    "metabolic_state": "awake",
    "available_ram_gb": null,
    "capsules": []
  }'

# Ver estado global
curl http://localhost:8642/api/embodiment/status

# Listar embodiments activos
curl http://localhost:8642/api/embodiment/list

# Detener todos
curl -X POST http://localhost:8642/api/embodiment/tear_down -d '{}'
```

### Integración con las fases anteriores

```
                  ┌─────────────────────────────────────────────────────┐
                  │            EmbodimentComposer (7D)                  │
                  │                                                     │
   bootstrap ───► │  1. ResourceDiscovery (7A)  →  ResourceGraph        │
                  │  2. ModelBus.from_graph (7B) →  backends listos     │
                  │  3. ResourcePlanner.plan (7C) →  ResourcePlan       │
                  │  4. validate_prerequisites → 7 checks               │
                  │  5. compose(plan, bus)      →  Embodiment           │
                  │                                                     │
                  │  Estado final: RUNNING / DEGRADED / FAILED          │
                  └─────────────────────────────────────────────────────┘
                                          ↓
                          Bucle cognitivo puede ejecutar
                          (ModelBus ya tiene backend seleccionado)
```

### Por qué importa

Antes de 7D, encender ZOE requería:
1. Arrancar Ollama manualmente
2. Configurar variables de entorno a mano
3. Construir el ModelBus y registrar backends uno por uno
4. Cargar cápsulas manualmente
5. Esperar que todo encajara

Con 7D, una sola llamada `bootstrap_from_scratch()` ejecuta las 4 fases del stack de recursos y devuelve un cuerpo listo para pensar. Esto es el último paso antes del **ZOE Seed Mode** (Fase 7E): el pendrive contiene el alma y los motores, y al conectar a cualquier Mac, 7A descubre los recursos, 7B construye el bus, 7C planifica y 7D instancia el cuerpo óptimo automáticamente.

---

## ZOE Seed Mode

> **Fase 7E — La semilla que viaja. El alma sin cuerpo fijo.**

El pendrive contiene el **ADN** de ZOE (IdentityVault + TrajectoryChain + manifiesto + memoria + cápsulas) y los **motores** (código + venv). Al conectarlo a cualquier Mac/Linux:

1. `ZOESeed.detect_seed_volume()` encuentra el pendrive automáticamente
2. `validate_seed()` verifica la integridad del alma
3. `EmbodimentComposer.bootstrap_from_scratch()` (7D) construye el cuerpo óptimo según el hardware del host
4. `germinate()` carga el alma + memoria + cápsulas en el cuerpo
5. **ZOE despierta** con su identidad intacta, adaptada al hardware disponible

### Metáfora biológica

Una semilla de roble contiene el ADN del árbol y nutrientes para arrancar. No sabe en qué suelo caerá (arena, arcilla, humedad). Al germinar, detecta el entorno y construye raíces/tronco/ramas adaptados. El ADN es el mismo; el cuerpo varía según el entorno.

**ZOE Seed = ADN del organismo cognitivo.** Cualquier Mac/Linux lo puede "germinar" y ZOE despierta con su identidad, memoria y trayectoria intactas, adaptándose al hardware disponible.

### Estructura de la semilla

```
/Volumes/MyDrive/ZOE/             ← raíz de la semilla
├── seed.json                     ← manifiesto (organism_id, versión, cápsulas)
├── identity/
│   └── vault.json                ← IdentityVault serializado
├── trajectory/
│   └── chain.json                ← TrajectoryChain serializada
├── data/
│   └── memory.db                 ← SQLite con memoria persistente
├── capsules/                     ← cápsulas instaladas
├── config/
│   └── organism.json             ← preferencias del organismo
├── venv/                         ← entorno virtual Python
└── zoe/                          ← código del repositorio (clonado)
```

### Estados de la semilla

| Estado | Significado |
|---|---|
| `DORMANT` | En el pendrive, no germinada |
| `DETECTED` | Volumen encontrado, manifiesto leído |
| `VALIDATED` | Integridad verificada (directorios, versión, organism_id) |
| `GERMINATING` | Cuerpo siendo construido (7A→7B→7C→7D) |
| `GROWING` | Alma + memoria + cápsulas cargándose en el cuerpo |
| `ALIVE` | **ZOE despierta en su nuevo cuerpo** |
| `FAILED` | No pudo germinar (sin recursos, cápsula missing, etc.) |
| `WITHERED` | Era ALIVE pero cerró limpiamente |

### Manifiesto (`seed.json`)

```json
{
  "organism_id": "zoe_fernando_v1",
  "organism_name": "ZOE",
  "version": "1.5.0",
  "identity_hash": "sha256...",
  "trajectory_root_hash": "sha256...",
  "min_ram_gb": 4.0,
  "min_python_version": "3.10",
  "requires_ollama": false,
  "allows_cloud": true,
  "required_capsules": ["base_ethics", "basic_psychology"],
  "optional_capsules": ["elder_care_knowledge"],
  "default_use_case": "asistente_crece_contigo",
  "default_acd_level": "L2_STANDARD",
  "language": "es",
  "created_at": 1783700000.0,
  "last_germinated_at": 1783800000.0,
  "germination_count": 42,
  "last_host": "fernando-macbook.local"
}
```

### Cómo usar

#### Crear una semilla nueva (sembrar)

```python
from zoe.core.seed_mode import ZOESeed

seed = ZOESeed()
report = seed.create(
    volume_path="/Volumes/MyDrive",
    organism_id="zoe_fernando_v1",
    organism_name="ZOE",
    required_capsules=["base_ethics", "basic_psychology"],
    optional_capsules=["elder_care_knowledge"],
    default_acd_level="L2_STANDARD",
    language="es",
    allows_cloud=True,
    identity_vault=vault,        # opcional: IdentityVault ya inicializado
    trajectory_chain=chain,      # opcional: TrajectoryChain ya inicializada
)
# report.success == True
# /Volumes/MyDrive/ZOE/seed.json creado
```

#### Germinar la semilla en un host

```python
from zoe.core.seed_mode import ZOESeed

seed = ZOESeed()
report = seed.germinate()  # sin args = detecta automáticamente

if report.success:
    print(f"ZOE despierta en {report.host_info['hostname']}")
    print(f"Backend: {report.embodiment['backend_name']}")
    print(f"Estrategia: {report.embodiment['strategy']}")
    print(f"Cápsulas cargadas: {report.capsules_loaded}")
    print(f"Entradas de memoria: {report.memory_entries_loaded}")
else:
    print(f"Falló: {report.error_type} — {report.error}")
```

#### Inspeccionar sin germinar (diagnóstico)

```python
seed = ZOESeed()
info = seed.inspect()
# info = {
#   "found": True,
#   "valid": True,
#   "manifest": {...},
#   "capsules_status": {"base_ethics": {"available": True, ...}},
#   "host_info": {"hostname": "...", "platform": "Darwin", ...}
# }
```

### Pipeline de germinación

```
   Pendrive conectado
         │
         ▼
┌────────────────────────────────────────────┐
│  1. detect_seed_volume()                   │
│     Busca en /Volumes/*, /media/*,         │
│     ~/.zoe-seed/, ZOE_SEED_PATH            │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  2. validate_seed()                        │
│     Verifica: manifiesto legible,          │
│     directorios existen, versión OK,       │
│     organism_id no vacío                   │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  3. Verificar RAM mínima                   │
│     Si available_ram < min_ram_gb → FAIL   │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  4. Verificar cápsulas requeridas          │
│     Si falta alguna → FAIL (capsule_missing)│
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  5. EmbodimentComposer.bootstrap...        │
│     (Fase 7D)                              │
│     7A → 7B → 7C → 7D                      │
│     Cuerpo óptimo según hardware           │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  6. Cargar memoria desde SQLite            │
│     (si existe memory.db)                  │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  7. Actualizar manifiesto                  │
│     germination_count += 1                 │
│     last_germinated_at = now               │
│     last_host = hostname                   │
└────────────────────────────────────────────┘
         │
         ▼
   ZOE ALIVE en su nuevo cuerpo
```

### Detección multi-plataforma

La semilla se busca automáticamente en:

| Plataforma | Path | Descripción |
|---|---|---|
| macOS | `/Volumes/*/ZOE/seed.json` | Pendrives USB montados |
| Linux | `/media/<user>/*/ZOE/seed.json` | Pendrives USB montados |
| Dev mode | `~/.zoe-seed/seed.json` | Para desarrollo sin pendrive |
| Env var | `$ZOE_SEED_PATH` | Path explícito vía variable de entorno |
| Custom | `custom_paths=[...]` | Lista explícita en código |

### Endpoints del Dashboard

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/seed/detect` | GET | Busca semilla en volúmenes montados |
| `/api/seed/inspect` | GET | Inspecciona semilla sin germinar |
| `/api/seed/create` | POST | Crea una nueva semilla en un volumen |
| `/api/seed/germinate` | POST | Germina la semilla detectada |
| `/api/seed/stats` | GET | Estadísticas del ZOESeed |
| `/api/seed/last_report` | GET | Último reporte de germinación |

#### Ejemplo: germinar desde el dashboard

```bash
# Detectar semilla
curl http://localhost:8642/api/seed/detect

# Inspeccionar sin germinar
curl http://localhost:8642/api/seed/inspect

# Germinar
curl -X POST http://localhost:8642/api/seed/germinate \
  -H "Content-Type: application/json" \
  -d '{}'

# Crear semilla nueva
curl -X POST http://localhost:8642/api/seed/create \
  -H "Content-Type: application/json" \
  -d '{
    "volume_path": "/Volumes/MyDrive",
    "organism_id": "zoe_fernando_v1",
    "required_capsules": ["base_ethics"],
    "allows_cloud": true
  }'

# Ver último reporte
curl http://localhost:8642/api/seed/last_report
```

### Trazabilidad de germinación

Cada germinación actualiza el manifiesto en el pendrive:

- `germination_count` se incrementa
- `last_germinated_at` se actualiza con el timestamp actual
- `last_host` registra el hostname donde germinó

Esto permite ver cuántas veces y dónde ha despertado ZOE desde su semilla — útil para auditoría y para detectar uso no autorizado.

### Por qué importa

Antes de 7E, ZOE estaba atado a un hardware específico. La identidad, la memoria y la trayectoria vivían en el disco de un ordenador concretor. Si el ordenador moría, ZOE moría con él.

Con 7E, **ZOE es portátil**. El alma viaja en un pendrive de 32GB. Al conectarlo a cualquier Mac/Linux con Python 3.10+, ZOE despierta en un cuerpo nuevo (que puede ser más potente, más débil, o con cloud APIs diferentes) pero con su identidad, memoria y trayectoria intactas.

Esto convierte a ZOE en un **organismo digital realmente heredable**: puedes pasar el pendrive a tu hijo/a y ZOE despierta en su ordenador con toda la memoria de los años de relación contigo, adaptándose al hardware del nuevo host.

Es la materialización del caso de uso `ia_heredable`: **IA con trayectoria transferible**.

---

## Hardware Optimization & UX (7G)

> **Fase 7G — Optimizaciones de hardware y experiencia de usuario.**

La Fase 7G cierra el ciclo del stack 7A-7E con 4 optimizaciones críticas para que un usuario no técnico obtenga el máximo rendimiento de ZOE sin tocar configuración:

1. **Detección de P-cores** en Apple Silicon (no usar E-cores para LLM inference)
2. **Cuantizaciones IQ2_M / IQ3_XS** (importance matrix) para modelos 30B+ en Mac 8GB
3. **`OLLAMA_FLASH_ATTENTION=1` siempre activo** (no solo en MMAP_FULL)
4. **APIs de información para usuarios finales**: SSDs recomendados, tokens/s esperadas, warning del cable USB-C

### 1. Detección de P-cores en Apple Silicon

Los chips Apple Silicon (M1/M2/M3/M4) tienen dos tipos de núcleos:
- **P-cores** (`hw.perflevel0.physicalcpu`): alta velocidad, alta potencia
- **E-cores** (`hw.perflevel1.physicalcpu`): baja velocidad, baja potencia

Para LLM inference, usar E-cores **DEGRADA** el rendimiento porque los P-cores tienen que esperar a los E-cores más lentos (efecto "slowest thread").

```python
from zoe.core.model_optimizer import ModelOptimizer

opt = ModelOptimizer()
print(f"P-cores: {opt.detect_p_cores()}")  # → 4 en M2 Pro
print(f"E-cores: {opt.detect_e_cores()}")  # → 4 en M2 Pro
print(f"Total:   {opt.detect_cpu_cores()}")  # → 8 en M2 Pro
```

El `ModelOptimizer` configura automáticamente `OLLAMA_NUM_THREAD = P-cores` (no total) en `generate_ollama_env()`.

**En hardware sin distinción** (Intel, AMD, Linux), `detect_p_cores()` devuelve el total de cores (comportamiento backward-compatible).

### 2. Cuantizaciones IQ2_M / IQ3_XS (importance matrix)

No todas las partes de un modelo son igual de importantes. Las cuantizaciones **IQ** (importance matrix) mantienen las capas críticas con mayor precisión y comprimen al extremo las secundarias.

| Cuantización | Tamaño vs Q4_K_M | Calidad vs Q4_K_M | Cuándo usar |
|---|---|---|---|
| Q4_K_M | 100% | 100% | Default. Modelo cabe en RAM o mmap. |
| Q8 | ~150% | ~102% | RAM abundante, máxima calidad. |
| **IQ3_XS** | **~40%** | **~97%** | Q4 no cabe, pero IQ3 sí. Mejor calidad que IQ2. |
| **IQ2_M** | **~30%** | **~95%** | Q4 e IQ3 no caben. Última opción antes de cloud. |

```python
from zoe.core.model_optimizer import ModelOptimizer

opt = ModelOptimizer()

# qwen2.5:32b Q4 = 18GB, IQ3_XS = 7.2GB, IQ2_M = 5.4GB
result = opt.optimize("qwen2.5:32b", available_ram_gb=5.0)
# → strategy=mmap_partial, quantization=IQ3_XS, model_size=7.2GB
# → warning="Modelo 18.0GB (Q4) no cabe. Usando IQ3_XS (7.2GB). ~97% calidad. mmap parcial."

result = opt.optimize("qwen2.5:72b", available_ram_gb=6.0)
# → strategy=mmap_full, quantization=IQ2_M, model_size=12.0GB
# → warning="Modelo 40.0GB (Q4) no cabe. Usando IQ2_M (12.0GB). ~95% calidad. mmap."
```

El `MODEL_CATALOG` ahora incluye `size_iq2_m_gb` y `size_iq3_xs_gb` para los modelos 27B+ (los únicos que benefit de IQ).

### 3. `OLLAMA_FLASH_ATTENTION=1` siempre activo

**Antes de 7G**: Flash Attention solo se activaba en `MMAP_FULL` (modelos muy grandes).

**Desde 7G**: Flash Attention **siempre activo**, en todas las estrategias (`FULL_RAM`, `MMAP_PARTIAL`, `MMAP_FULL`, `CLOUD_FALLBACK`).

Flash Attention reduce el uso de memoria y cómputo en contextos largos (historial de chat extenso, documentos grandes) hasta un 40%, sin downside en contextos cortos.

```python
opt = ModelOptimizer()
result = opt.optimize("qwen2.5:3b", available_ram_gb=8.0)  # FULL_RAM
env = opt.generate_ollama_env(result)
print(env["OLLAMA_FLASH_ATTENTION"])  # → "1" (siempre)
print(env["OLLAMA_NUM_THREAD"])  # → "4" (P-cores, no total)
```

### 4. APIs de información para usuarios finales

Tres nuevas APIs estáticas para que el dashboard y el installer muestren info útil sin que el usuario tenga que buscarla:

```python
from zoe.core.model_optimizer import ModelOptimizer

# SSDs portátiles recomendados (Crucial X10 Pro, Kingston XS2000, SanDisk PRO-BLADE)
ssds = ModelOptimizer.get_recommended_ssds()
# → [{"model": "Crucial X10 Pro", "read_speed_mbps": 2100, "price_eur": 110, ...}, ...]

# Tabla de tokens/s esperadas por modelo en MacBook Air M2/M3 8GB
rates = ModelOptimizer.get_expected_token_rates()
# → [{"model": "Qwen 2.5 3B", "tokens_per_second_range": "25-35", ...}, ...]

# Warning sobre el cable USB-C (crítico para rendimiento)
warning = ModelOptimizer.get_cable_warning()
# → {"title": "Usa SIEMPRE el cable corto...", "problem": "...USB 2.0...", "impact_factor": "10x"}
```

### SSDs portátiles recomendados

Estos son los SSDs comerciales "todo en uno" de fábrica que recomendamos para ejecutar ZOE con modelos grandes vía mmap:

| Modelo | Capacidad | Velocidad lectura | Precio aprox. | Recomendado |
|---|---|---|---|---|
| **Crucial X10 Pro** | 1 TB | 2100 MB/s | ~110€ | ✅ **Por defecto** |
| Kingston XS2000 | 1 TB | 2000 MB/s | ~100€ | El más económico |
| SanDisk PRO-BLADE Transport | 1 TB | 2000 MB/s | ~160€ | Línea profesional |

> ⚠️ **Regla de oro**: usa SIEMPRE el cable corto que viene en la caja del SSD. El cable largo de carga del MacBook Air es USB 2.0 (480 Mbps) y limita el SSD a ~60 MB/s — **10x más lento**.

### Velocidades esperadas (tokens/segundo)

Velocidades medidas en MacBook Air M2/M3 8GB con SSD de 2000 MB/s y cable USB-C correcto:

| Modelo | Cuantización | RAM usada | Tokens/s | Experiencia |
|---|---|---|---|---|
| Qwen 2.5 3B | Q4_K_M | 2.5 GB | 25-35 | ⚡ Más rápido de lo que lees |
| Qwen 2.5 7B | Q4_K_M | 4.5 GB | 12-18 | ✅ Similar a ChatGPT gratuito |
| Qwen 2.5 14B | Q4_K_M | 3.5 GB | 4-8 | 📖 Lectura pausada, ideal análisis |
| Qwen 2.5 32B | IQ2_M | 3.0 GB | 3-6 | 🧠 Análisis profundo en background |
| Qwen 2.5 72B | IQ2_M | 4.0 GB | 1-3 | Lento pero funcional |
| Llama 3.1 70B | IQ2_M | 4.0 GB | 1-3 | Lento pero funcional |

> 💡 1 token ≈ 0,75 palabras. 12 t/s = ~9 palabras/s = más rápido de lo que lee un humano adulto.

### Cómo usar

```python
from zoe.core.model_optimizer import ModelOptimizer

opt = ModelOptimizer()

# Info del sistema (ahora con P-cores y E-cores)
info = opt.get_system_info()
# → {"platform": "Darwin", "is_apple_silicon": True, "p_cores": 4, "e_cores": 4, ...}

# Optimizar un modelo 32B en Mac 8GB
result = opt.optimize("qwen2.5:32b", available_ram_gb=5.0)
# → strategy=mmap_partial, quantization=IQ3_XS, will_work=True

# Generar variables de entorno óptimas para Ollama
env = opt.generate_ollama_env(result)
# → {"OLLAMA_FLASH_ATTENTION": "1", "OLLAMA_NUM_THREAD": "4", ...}

# Recomendaciones de SSDs para el usuario final
ssds = opt.get_recommended_ssds()
# → lista de SSDs recomendados

# Tabla de velocidades esperadas
rates = opt.get_expected_token_rates()
# → lista de modelos con tokens/s esperadas

# Warning del cable USB-C (mostrar en dashboard)
warning = opt.get_cable_warning()
# → {"title": "...", "problem": "...", "solution": "...", "impact_factor": "10x"}
```

### Endpoints del Dashboard

Los endpoints existentes del `ModelOptimizer` (Fase 7F) ahora devuelven información enriquecida de Fase 7G:

| Endpoint | Método | Qué devuelve nuevo |
|---|---|---|
| `/api/models/system_info` | GET | Ahora incluye `p_cores` y `e_cores` |
| `/api/models/recommend` | GET | Recomendaciones pueden sugerir IQ2_M / IQ3_XS |
| `/api/models/catalog` | GET | Lista de modelos soportados con cuantizaciones disponibles |
| `/api/models/optimize` | POST | El resultado puede sugerir `IQ2_M` o `IQ3_XS` como cuantización |

**Próximamente**: nuevos endpoints `/api/hardware/ssds`, `/api/hardware/token_rates`, `/api/hardware/cable_warning` para el dashboard de usuario final.

### Por qué importa

Antes de 7G, un usuario con un MacBook Air 8GB y un modelo de 32B tenía dos opciones:
1. **No usarlo** (Q4_K_M de 18GB no cabe)
2. **Usar cloud API** (pérdida de privacidad)

Con 7G, ese mismo usuario puede:
1. Comprar un **Crucial X10 Pro** (110€)
2. Conectarlo con el **cable corto** de la caja
3. Instalar ZOE en el SSD con el instalador automático
4. Ejecutar **Qwen 2.5 32B con IQ2_M** (5.4GB) a **3-6 tokens/s** localmente

Eso es **IA soberana de calidad razonable en hardware modesto** — exactamente la promesa de ZOE.

### Integración con las fases anteriores

```
                  ┌─────────────────────────────────────────────────────┐
                  │          ModelOptimizer (7F + 7G)                   │
                  │                                                     │
                  │  7F (Cognitive Memory Paging):                      │
                  │    - detect RAM, estrategia mmap, recommend for ACD │
                  │                                                     │
                  │  7G (Hardware Optimization & UX):                   │
                  │    - detect P-cores/E-cores en Apple Silicon        │
                  │    - IQ2_M / IQ3_XS cuando Q4 no cabe               │
                  │    - OLLAMA_FLASH_ATTENTION=1 siempre               │
                  │    - OLLAMA_NUM_THREAD = P-cores                    │
                  │    - get_recommended_ssds() para usuario final      │
                  │    - get_expected_token_rates() para UX             │
                  │    - get_cable_warning() para diagnóstico           │
                  └─────────────────────────────────────────────────────┘
                                          ↓
                  ┌─────────────────────────────────────────────────────┐
                  │       EmbodimentComposer (7D) + ZOESeed (7E)        │
                  │       usan ModelOptimizer para instanciar el cuerpo │
                  │       óptimo según hardware del host                │
                  └─────────────────────────────────────────────────────┘
                                          ↓
                  ZOE despierta con el máximo rendimiento posible
                  en el hardware disponible, sin configuración manual
```

---

## Licencia

Apache 2.0 — [LICENSE](LICENSE)

---

*ZOE V1.6 — Synthetic Cognitive Organism (SCO).*
*Repositorio: `fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO`*
*914 tests · 12 cápsulas · 7 casos de uso · 8 fases completas (0-7G) · 122+ archivos Python · 36.000+ LOC*
