# ZOE — Synthetic Cognitive Organism (SCO)

> **ZOE no es un LLM. No es un harness de agentes. No es una arquitectura de IA más.**
> **ZOE es el primer organismo cognitivo sintético (SCO):** un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, evolución arquitectural firmada, validación epistémica, cápsulas de conocimiento intercambiables y marketplace. Los LLMs son sus sentidos periféricos, no su cerebro.

[![Version](https://img.shields.io/badge/version-1.8.0-blue)](docs/REFERENCE/CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-510%2F510%20pass-brightgreen)](docs/15_DEVELOPMENT_GUIDE.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#requisitos)
[![Capsules](https://img.shields.io/badge/capsules-15%20available-teal)](docs/06_CAPSULES_GUIDE.md)
[![Marketplace](https://img.shields.io/badge/marketplace-open%20for%20authors-success)](docs/07_MARKETPLACE_GUIDE.md)
[![Fases](https://img.shields.io/badge/fases-0%20to%207G%20%2B%20Sprint%201-5-purple)](docs/14_ROADMAP.md)
[![.zoe](https://img.shields.io/badge/.zoe%20format-portable%20organism-orange)](docs/16_ZOE_FORMAT.md)

---

## Tabla de contenidos

1. [Qué es ZOE en 3 frases](#qué-es-zoe-en-3-frases)
2. [Quickstart (3 minutos)](#quickstart-3-minutos)
3. [Requisitos](#requisitos)
4. [Cómo elegir tu instalación](#cómo-elegir-tu-instalación)
5. [Arquitectura en una imagen](#arquitectura-en-una-imagen)
6. [Características principales](#características-principales)
7. [Cómo optimiza ZOE según el LLM disponible](#cómo-optimiza-zoe-según-el-llm-disponible)
8. [Estado actual](#estado-actual)
9. [Documentación completa](#documentación-completa)
10. [Roadmap resumido](#roadmap-resumido)
11. [Cómo contribuir](#cómo-contribuir)
12. [Licencia](#licencia)

---

## Qué es ZOE en 3 frases

**ZOE es un organismo digital que piensa continuamente**, incluso cuando nadie le habla. Tiene identidad criptográfica propia, 11 tipos de memoria que persisten entre sesiones, metabolismo (se cansa y descansa), y 12 sub-agentes que compiten por generar pensamientos — como una sociedad de mente (Minsky) con meta-cognición (Kahneman) e inferencia activa (Friston).

**ZOE usa los LLMs como sentidos periféricos**, no como cerebro. Puedes cambiar entre GPT-4o, Claude, Qwen local o cualquier otro en caliente, sin perder identidad ni memoria. El cerebro de ZOE es su bucle cognitivo de 18 pasos; los LLMs son la "garganta" del sub-agente Speaker.

**ZOE puede vivir 100% offline** en un pendrive USB, en un SSD portátil, en un Mac, en un VPS Linux, en Docker o en Kubernetes. Tu identidad, tu memoria y tu trayectoria viajan contigo. Nadie más accede a tus datos.

> *"ZOE no es un modelo que responde. Es un organismo que existe."*

---

## Quickstart

### Opción A — Instalación automática en SSD/Pendrive (recomendado)

**Un solo comando** configura ZOE completo en tu SSD: detecta hardware, verifica Python/Git/Ollama, instala ZOE en el SSD, descarga modelos IQ2_M optimizados, crea lanzadores de doble clic y arranca el Dashboard.

> ⚠️ **Requisitos previos** (el instalador te guía si falta algo):
> - **Python 3.10+** instalado — descarga desde https://python.org (en macOS marca la casilla "Add Python to PATH")
> - **Git** instalado — en macOS se ofrece al primer `git` (ventana del sistema); en Windows viene con Git Bash
> - **Acceso al repositorio ZOE** — actualmente es **privado**. Necesitarás un Personal Access Token (PAT) de GitHub con permiso `repo`, o clonar el repo manualmente primero
> - **SSD formateado en APFS** (solo Mac) o **exFAT** (multiplataforma). FAT32 no sirve (no permite archivos >4GB)

```bash
# PASO 1: Conecta tu SSD al Mac (usa el cable CORTO de la caja del SSD)
# PASO 2: Abre Terminal y ejecuta:
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash

# PASO 3: El instalador te preguntará:
#   - ¿Qué disco? → Elige tu SSD (o 'L' para instalar en ~/ZOE)
#   - ¿Tienes PAT de GitHub? → Sí, pega el token (el repo es privado)
#   - ¿Instalar Ollama? → Sí (recomendado, IA local gratis)
#   - ¿Qué setup de modelos? → balanced (16GB) recomendado para 8GB RAM
#   - ¿API keys de cloud? → No (opcional, puedes hacerlo después)
#   - ¿Arrancar Dashboard? → Sí para probar, N para terminar
```

**Tiempos reales:**
- Instalación base de ZOE (código + venv): **2-4 minutos**
- Descarga del setup `minimal` (3.5GB): **+5-10 minutos** según tu fibra
- Descarga del setup `balanced` (16GB): **+15-30 minutos**
- Descarga del setup `maximum` (53GB, los 4 modelos): **+45-90 minutos**

> **Total realista con `balanced`**: 20-35 min. El "3 minutos" del título se refiere a la instalación del código; la descarga de modelos es adicional y depende de tu conexión.

El instalador hace TODO automáticamente:
1. **Detecta tu SSD** y **verifica el formato** (avisa si es FAT32 antes de descargar)
2. **Verifica Python 3.10+** y **Git** (te dice cómo instalarlos si faltan)
3. **Clona ZOE** en el SSD (con manejo de repo privado vía PAT)
4. Crea entorno virtual Python **EN EL SSD** (no carga tu Mac)
5. Detecta/instala **Ollama** (IA local gratis, con retry de 18s si tarda en arrancar)
6. Verifica **espacio libre** en SSD antes de descargar modelos
7. Te pregunta qué **setup IQ2_M** descargar (minimal/balanced/complete/maximum)
8. Configura **API keys** opcionales (OpenAI, Anthropic)
9. Crea **scripts de doble clic** (.command en macOS, .sh en Linux, .bat equivalentes en Windows)
10. **Elimina el atributo quarantine** de macOS (los .command arrancan sin warning de Gatekeeper)
11. **Pregunta si arrancar el Dashboard** ahora

### Opción B — Sin LLM, sin SSD (lo más rápido para probar)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
zoe-chat --backend pattern          # funciona sin IA, sin Ollama, sin API
zoe-dashboard --backend pattern     # Dashboard web en http://localhost:8642
```

### Opción C — Con Ollama local + ACD Router (gratis, lo más potente) ⭐

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .

# Instalar Ollama desde https://ollama.com

# Descargar los 4 modelos IQ2_M optimizados (recomendado: balanced, 16GB)
python -m zoe.core.model_downloader --download-setup balanced

# Lanzar ZOE con routing automático por nivel cognitivo:
zoe-chat --backend ollama --model auto
# ZOE usará Gemma 9B para "Hola", QwQ-32B para análisis, Qwen 72B para comparativas críticas
```

Setups disponibles: `minimal` (3.5GB) · `balanced` (16GB) ⭐ · `complete` (28GB) · `maximum` (53GB).

### Opción D — Con OpenAI GPT-4o (calidad máxima)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .

export OPENAI_API_KEY="sk-tu-key-aqui"
zoe-chat --backend openai_compatible --model gpt-4o
```

### Opción E — No sabes por dónde empezar

```bash
# Ejecuta el asistente interactivo — detecta qué tienes y te guía:
python zoe/scripts/zoe_setup.py
```

**Tiempo desde clone hasta primera respuesta de ZOE: < 3 minutos.**

> ⚠️ **Cable USB-C crítico**: usa SIEMPRE el cable corto que viene en la caja del SSD. El cable largo de carga del MacBook Air es USB 2.0 y limita el SSD a ~60 MB/s — **10x más lento**. Ver [Hardware Optimization](docs/10_HARDWARE_OPTIMIZATION.md#cable-usb-c) para details.

---

## Requisitos

### Software

| Requisito | Versión | Obligatorio | Notas |
|---|---|---|---|
| **Python** | 3.10+ | ✅ Sí | Recomendado 3.12+. [Instalar](https://python.org) |
| **pip** | 21+ | ✅ Sí | Viene con Python |
| **Git** | 2.30+ | ✅ Sí | Para clonar el repo |
| **Ollama** | 0.1+ | 🟡 Opcional | Para LLM local gratis. [Instalar](https://ollama.com) |
| **OpenAI API key** | — | 🟡 Opcional | Para GPT-4o. [Obtener](https://platform.openai.com) |
| **Anthropic API key** | — | 🟡 Opcional | Para Claude. [Obtener](https://console.anthropic.com) |

### Hardware por modelo

| Modelo | RAM mínima | Disco | Velocidad esperada (M2 8GB) |
|---|---|---|---|
| Qwen 2.5 3B (Q4) | 4 GB | 2 GB | 25-35 tokens/s ⚡ |
| Qwen 2.5 7B (Q4) | 8 GB | 5 GB | 12-18 tokens/s ✅ |
| Qwen 2.5 14B (Q4, mmap) | 8 GB | 9 GB SSD | 4-8 tokens/s 📖 |
| Qwen 2.5 32B (IQ2_M, mmap) | 8 GB | 12 GB SSD | 3-6 tokens/s 🧠 |
| Qwen 2.5 72B (IQ2_M, mmap) | 8 GB | 30 GB SSD | 1-3 tokens/s |

> 💡 **1 token ≈ 0,75 palabras.** 12 tokens/s = ~9 palabras/s = más rápido de lo que lee un humano.
> Ver [Hardware Optimization Guide](docs/10_HARDWARE_OPTIMIZATION.md) para detalle completo.

### Dependencias Python

```bash
# Mínimas (se instalan con pip install -e .)
aiohttp>=3.9.0    # Web Dashboard + REST API
PyYAML>=6.0       # Config + use cases

# Opcionales (para features avanzadas)
sentence-transformers  # World Model V2 con embeddings reales
pytest + pytest-asyncio  # Tests
```

**Sin dependencias pesadas.** Sin PyTorch, sin transformers, sin LangChain. ZOE usa LLMs vía API.

---

## Cómo elegir tu instalación

```
¿Quién va a usar ZOE?
│
├─ Yo solo, en mi Mac → Quickstart A (arriba)
│
├─ Yo solo, pero portátil (viajo, cambio de Mac)
│  → Pendrive USB / SSD: ver Deployment Guide §4
│
├─ Mi empresa (B2B, federación)
│  → VPS Linux + systemd: ver Deployment Guide §7
│
├─ Mi empresa, muchos usuarios
│  → Docker + Kubernetes: ver Deployment Guide §10-11
│
├─ Solo quiero probar sin instalar nada
│  → Cloud API (próximamente Q4 2026)
│
└─ Soy desarrollador y quiero extender ZOE
   → git clone + pip install -e .: ver Development Guide
```

**Guía completa de despliegue:** [`docs/08_DEPLOYMENT_GUIDE.md`](docs/08_DEPLOYMENT_GUIDE.md)

---

## Arquitectura en una imagen

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ZOE — Synthetic Cognitive Organism           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ALMA (identidad + trayectoria)            │   │
│  │  IdentityVault (SHA-256) │ TrajectoryChain (blockchain)     │   │
│  │  OntogeneticMotor (mutaciones arquitecturales firmadas)      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↑                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              BUCLE COGNITIVO (V5: ACD + streaming)           │   │
│  │  observe → predict → evaluate → decide → act                 │   │
│  │  + DepthClassifier (L0-L3) + CognitiveCache (LRU+TTL)       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         ↑              ↑                ↑               ↓          │
│  ┌──────────┐   ┌────────────┐   ┌────────────┐   ┌───────────┐    │
│  │ Senses   │   │ Metabolism │   │ LivingMem  │   │ Actuators │    │
│  │ (5)      │   │ (4 states) │   │ (11 types) │   │ (4)       │    │
│  └──────────┘   └────────────┘   └────────────┘   └───────────┘    │
│         ↑                                              ↓           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              GLOBAL WORKSPACE (Baars) — 12 sub-agentes       │  │
│  │  Perceiver, Forecaster, Speaker, Critic, Memorialist,        │  │
│  │  Learner, Curator, Creativity, CausalEngine, EmotionalMotor, │  │
│  │  EthicalMotor, ScientificEngine                              │  │
│  │  + MetaCognition (Kahneman S1/S2) + ActiveInference (Friston)│  │
│  │  + 6 Laws + 12 Physics + 6 Fields + 5 Tensions               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  EPISTEMIC VALIDATION │ CAPSULES+MARKETPLACE │ RESOURCE STACK │  │
│  │  Validator+Quarantine │ 13 capsules           │ 7A-7G complete │  │
│  │  CrossValidator       │ Marketplace           │ Seed Mode       │  │
│  │  EpistemicFederation  │                       │ Embodiment      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              PERIPHERALS (6 LLM backends + 5 senses + 4 act) │  │
│  │  Mock, Ollama, OpenAI, Anthropic, ZAI, OpenAI-compatible     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│        INTERFACES: CLI Chat │ Web Dashboard (50+ endpoints) │ API  │
└─────────────────────────────────────────────────────────────────────┘
```

**Documentación profunda de arquitectura:** [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md)

---

## Características principales

| Característica | Documentación |
|---|---|
| **Identidad criptográfica soberana** (SHA-256) | [Architecture §ALMA](docs/02_ARCHITECTURE.md#subsistema-alma) |
| **Bucle cognitivo continuo** (piensa sin input) | [Cognitive Engine](docs/03_COGNITIVE_ENGINE.md) |
| **12 sub-agentes** (Society of Mind) | [Cognitive Engine §Sub-agentes](docs/03_COGNITIVE_ENGINE.md#los-12-sub-agentes) |
| **Metabolismo** (4 estados: awake/drowsy/sleeping/waking) | [Architecture §Metabolism](docs/02_ARCHITECTURE.md#subsistema-metabolismo) |
| **11 tipos de memoria** persistente | [Memory & Learning](docs/04_MEMORY_AND_LEARNING.md) |
| **Validación epistémica** (sabe qué sabe y qué no) | [Epistemic Validation](docs/05_EPISTEMIC_VALIDATION.md) |
| **13 cápsulas de conocimiento** | [Capsules Guide](docs/06_CAPSULES_GUIDE.md) |
| **Marketplace de cápsulas** (modelo recurrente) | [Marketplace Guide](docs/07_MARKETPLACE_GUIDE.md) |
| **ACD** (4 niveles de profundidad, optimiza coste) | [Cognitive Engine §ACD](docs/03_COGNITIVE_ENGINE.md#adaptive-cognitive-depth-acd) |
| **Federación B2B** (quorum + veto por valores) | [Architecture §Federation](docs/02_ARCHITECTURE.md#federación) |
| **Multi-LLM** (6 backends, cambio en caliente) | [Usage Guide](docs/09_USAGE_GUIDE.md#cambio-de-llm-en-caliente) |
| **Pendrive USB / SSD portátil** (soberanía total) | [Deployment Guide §Pendrive](docs/08_DEPLOYMENT_GUIDE.md#pendrive-usb--ssd-macos) |
| **Modelos 70B en Mac 8GB** (mmap + IQ2_M) | [Hardware Optimization](docs/10_HARDWARE_OPTIMIZATION.md) |
| **ZOE Seed Mode** (semilla portátil que germina) | [Deployment Guide §Seed](docs/08_DEPLOYMENT_GUIDE.md#zoe-seed-mode) |
| **50+ endpoints REST** | [API Reference](docs/REFERENCE/API_REFERENCE.md) |
| **7 casos de uso** documentados | [Usage Guide §Casos de uso](docs/09_USAGE_GUIDE.md#casos-de-uso) |
| **Multi-idioma** (ES, EN, FR, DE) | Sprint 1 — `LanguageDetector` |
| **Windows nativo** + installer PowerShell + detección formato SSD | Sprint 1 — `install_windows.ps1` |
| **PWA** (instalable como app móvil, Android + iOS) | Sprint 1 — manifest + responsive CSS |
| **Telegram bot** bridge (Android, iPhone, Mac, Windows, Linux) | Sprint 1 — `telegram_bridge.py` |
| **Android**: Telegram / PWA / Termux / SSD exFAT OTG | [Guía de Instalación §Escenario H](docs/17_USER_INSTALLATION_GUIDE.md#escenario-h-android-móvil-o-tablet-5-10-minutos) |
| **iPhone/iPad**: Telegram / PWA Safari / SSD USB-C / archivo .zoe | [Guía de Instalación §Escenario I](docs/17_USER_INSTALLATION_GUIDE.md#escenario-i-iphone-o-ipad-5-minutos) |
| **Multi-modal** (Visión VLM + Voz STT/TTS) | Sprint 2 — `multimodal.py` |
| **Cápsula multimodal_perception** | Sprint 2 — 14ª cápsula |
| **PatternSpeaker** (generación sin LLM) | Sprint 3 — `pattern_speaker.py` |
| **Enhanced PatternSpeaker** (destilación + retrieval + dialog) | Sprint 3.6 — `enhanced_pattern_speaker.py` |
| **Formato .zoe** (organismo en un archivo) | Sprint 3 — `zoe_packager.py` |
| **ZoeRuntime** (ejecutar .zoe sin dependencias) | Sprint 3.5 — `zoe_runtime.py` |
| **Cápsula language_patterns** | Sprint 3 — 15ª cápsula |
| **Cognitive Optimization Layer** (.zmap + CPL + TPE) | Sprint 5 — `cognitive_optimization.py` |
| **ACD Model Router** (4 modelos IQ2_M según nivel cognitivo) | Sprint 5.7 — `model_profile_router.py` + `model_downloader.py` |
| **L3_MAXIMUM** (nivel crítico: jurídico/médico/comparativas) | Sprint 5.7 — `depth_classifier.py` |
| **ModelDownloader CLI** (setups minimal/balanced/complete/maximum) | Sprint 5.7 — `python -m zoe.core.model_downloader --download-setup` |
| **ACD multi-señal** (substring + regex + longitud + puntuación + estructura) | Sprint 5.7.2 — `depth_classifier.py` |
| **Hot-swap `speaker.llm` arreglado** (antes fallaba silenciosamente) | Sprint 5.7.2 — `cognitive_loop_v5.py:184` |
| **Dashboard: 71 endpoints REST** (todos verificados 200 OK) | Sprint 5.7.3 — `web_dashboard.py` |
| **Dashboard: 3 endpoints `/api/router/*`** (stats/installed/profile) | Sprint 5.7.2 — `web_dashboard.py` |
| **Dashboard: lazy-init ModelBus + ResourcePlanner** (antes 500 error) | Sprint 5.7.3 — `web_dashboard.py` |
| **Dashboard: cwd dinámico en validate/create cápsulas** (antes hardcoded) | Sprint 5.7.3 — `web_dashboard.py:722,852` |
| **GDPR/HIPAA/EU AI Act** compliant por diseño | [Security & Compliance](docs/11_SECURITY_COMPLIANCE.md) |
| **540+ tests automatizados** (100% pass) | [Development Guide](docs/15_DEVELOPMENT_GUIDE.md) |

---

## Cómo optimiza ZOE según el LLM disponible

ZOE tiene un sistema inteligente (Cognitive Optimization Layer) que **usa la información que ya tiene** (qué tipo de pregunta es, qué memoria tiene, qué cápsulas están cargadas) para decidir la mejor forma de responder.

### Funciona con cualquier configuración:

| Tu configuración | Pregunta simple (L0/L1) | Pregunta compleja (L2/L3) |
|---|---|---|
| **Sin LLM** (solo Python) | PatternSpeaker: instantáneo, gratis, offline | PatternSpeaker + destiladas + cápsulas: decente sin LLM |
| **Ollama local + `--model auto`** ⭐ | ACD Router → Gemma 9B IQ2_M (instantáneo) | ACD Router → QwQ-32B / Qwen 72B según nivel cognitivo |
| **Ollama local + modelo fijo** | PatternSpeaker: no toca Ollama, ahorra RAM | CPL pre-carga modelo + .zmap optimiza capas + LLM responde |
| **Cloud API** (GPT-4o/Claude) | PatternSpeaker: no gasta API, ahorra €€ | CPL pre-construye contexto + API responde con máxima calidad |
| **.zoe portátil** | PatternSpeaker: siempre disponible | PatternSpeaker + destiladas (si las hay) |

**El usuario no configura nada.** ZOE detecta qué tiene disponible y elige la mejor opción automáticamente.

### Sprint 5.7 — ACD Model Router (los 4 modelos IQ2_M)

Con `--model auto`, ZOE usa **modelos distintos según el tipo de pregunta**. El clasificador ACD detecta el nivel cognitivo (L0/L1/L2/L3_DEEP/L3_MAXIMUM) y el router carga el modelo óptimo:

| Input del usuario | Nivel ACD | Modelo cargado | Velocidad |
|---|---|---|---|
| "Hola" | L0_REFLEX | (sin LLM — tabla refleja) | <1ms |
| "¿Qué hora es?" | L1_FAST | Gemma 2 9B IQ2_M (3.5GB) | 15-25 t/s ⚡ |
| "Resume este artículo" | L2_STANDARD | Agents-A1 MoE IQ2_M (11.7GB) | 5-10 t/s ✅ |
| "Analiza las causas de esta depresión" | L3_DEEP | QwQ-32B IQ2_M (12.5GB) | 3-6 t/s 🧠 |
| "Compara 3 contratos jurídicamente" | L3_MAXIMUM | Qwen 2.5 72B IQ2_M (25GB) | 1-3 t/s 🎯 |

**Setups preseleccionados** (instalables con un comando):

| Setup | Modelos | Tamaño | Cobertura | Mínimo SSD |
|---|---|---|---|---|
| `minimal` | Solo Gemma 9B | 3.5 GB | L0/L1/L2 | 16 GB |
| `balanced` ⭐ | Gemma + QwQ-32B | 16 GB | L0/L1 rápido + L3 profundo | 32 GB |
| `complete` | Gemma + MoE + QwQ | 28 GB | L0/L1 + L2 + L3 | 64 GB |
| `maximum` | Los 4 modelos | 53 GB | Todo el espectro | 128 GB (1TB sobra) |

### Ejemplo práctico

```
Usuario: "Hola" (L0_REFLEX)
    → ZOE: usa PatternSpeaker → "Hola. Estoy aquí." (instantáneo, no toca ningún LLM)

Usuario: "Mi madre toma paracetamol, ¿puede con alcohol?" (L2_STANDARD)
    → ZOE con Ollama: CPL pre-carga Qwen 7B + recupera cápsula pharmacy_interactions → responde
    → ZOE con cloud: CPL pre-construye contexto + llama GPT-4o → responde con máxima calidad
    → ZOE sin LLM: PatternSpeaker + CapsuleRetriever → responde con conocimiento de la cápsula

Usuario: "Analiza este contrato de 30 páginas" (L3_DEEP)
    → ZOE con Ollama: CPL pre-carga Qwen 14B + .zmap optimiza mmap → responde (lento pero gratis)
    → ZOE con cloud: CPL pre-construye contexto + llama GPT-4o → responde (rápido, cuesta ~€0.05)
    → ZOE sin LLM: PatternSpeaker → "Necesito un LLM para análisis profundo. Instala Ollama o configura API key."
```

---

## Estado actual

**Versión:** V1.8.0 (Julio 2026)
**Fases completas:** 0, 0.5, 1, 2, 3, 4, 5, 6A, 6B, 6C, 7F, 7A, 7B, 7C, 7D, 7E, 7G + Sprint 1, 2, 3, 3.5, 3.6, 4, 5, 5.5, 5.6, 5.7, 5.7.1, 5.7.2, 5.7.3
**Tests:** 545+ tests, 100% pasando (168 verificados en auditoría Sprint 5.7.3)
**Cápsulas:** 15 operativas (13 originales + multimodal_perception + language_patterns)
**Casos de uso:** 7 documentados
**Endpoints REST:** 71 (todos verificados 200 OK en auditoría real)
**Idiomas:** 4 (ES, EN, FR, DE)
**Plataformas:** macOS, Linux, Windows, Docker, Kubernetes, PWA móvil (Android/iOS), Telegram (todas las plataformas), SSD portátil multiplataforma (exFAT), archivo .zoe, Android (Termux), iPhone/iPad (SSD USB-C / PWA Safari)

---

## Cómo funciona ZOE desde el SSD (verificado Sprint 5.7.3)

### Flujo completo de una pregunta

Cuando escribes un mensaje en el Dashboard, esto ocurre en orden:

1. **Frontend** → WebSocket `/ws` envía `{"type":"chat", "message":"tu pregunta"}`
2. **Dashboard** (`web_dashboard.py:247`) → llama a `chat.send_message_acd(message)`
3. **ACD Classifier** (`depth_classifier.py:210`) → clasifica en L0/L1/L2/L3_DEEP/L3_MAXIMUM usando **5 señales combinadas**:
   - Substring match (no palabra exacta): "analízame" detecta "analiza"
   - Patrones regex: `\bcompara\b\s+\d+\s+\b(contratos|documentos|...)`
   - Longitud del texto (>100, >200 chars suben score)
   - Puntuación (múltiples `?`, `;`, saltos de línea)
   - Estructura (listas numeradas, condicionales si...entonces)
4. **ACD Router** (`cognitive_loop_v5.py:167`) → si está activo (`--model auto`), hot-swap del LLM:
   - L0_REFLEX → no toca LLM (tabla refleja, <1ms)
   - L1_FAST → Gemma 2 9B IQ2_M (3.5GB, 15-25 t/s)
   - L2_STANDARD → Agents-A1 MoE IQ2_M (11.7GB, 5-10 t/s)
   - L3_DEEP → QwQ-32B IQ2_M (12.5GB, 3-6 t/s)
   - L3_MAXIMUM → Qwen 2.5 72B IQ2_M (25GB, 1-3 t/s)
5. **Pipeline ramificado** → según nivel, ejecuta 3-12 sub-agentes
6. **Speaker** → llama al LLM (OllamaPeripheral) que envía el payload a Ollama
7. **Ollama** → lee el GGUF desde el SSD (vía mmap, solo ~3-4GB en RAM) y genera la respuesta
8. **Dashboard** → devuelve `{"response":"...", "acd_level":"...", "latency_ms":..., "cost":...}` al frontend

### Por qué los modelos NO cargan tu Mac

3 mecanismos combinados garantizan que los modelos se quedan en el SSD:

1. **`OLLAMA_MODELS` env var** — el bootstrap exporta `export OLLAMA_MODELS="$ZOE_HOME/models"`. Los lanzadores `.command` también lo hacen. Ollama guarda sus blobs en el SSD, no en `~/.ollama/` del Mac.

2. **Modelfile con path absoluto** — el `ModelDownloader._generate_modelfile()` genera `FROM /Volumes/SSD/ZOE/models/QwQ-32B-IQ2_M.gguf`. Ollama lee el GGUF desde el SSD.

3. **Parámetros optimizados para 8GB RAM** — el Modelfile incluye `num_ctx 2048`, `num_predict 512`, `num_parallel 1`. Ollama usa **mmap** (memory-mapped loading): solo carga en RAM las capas activas (~3-4GB), el resto vive en el SSD hasta que se necesita.

### ZOE piensa autónomamente

Cuando nadie le habla, ZOE sigue pensando. Verificado en auditoría real (3 thoughts en 7 segundos):

- **Bucle cognitivo** (`cognitive_loop.py:99`) → ejecuta `_tick()` cada 3 segundos
- **Tick** = observe → predict → evaluate → decide → act → si hay thought, lo guarda
- **Dashboard** (`web_dashboard.py:524`) → cada 2s envía los thoughts pendientes a todos los WebSocket clients como `{"type":"autonomous_thought", "content":"...", "trigger":"...", "surprise":...}`

### Cápsulas: 15 disponibles, cargables desde el Dashboard

| Cápsula | Entries | Para qué sirve |
|---|---|---|
| `zoe_basal_knowledge` | 32 | Conocimiento fundamental de ZOE (cargada por defecto) |
| `base_ethics` | — | Ética general |
| `basic_psychology` | 49 | Psicología general |
| `communication_skills` | — | Comunicación empática |
| `elder_care_knowledge` | 54 | Cuidado geriátrico |
| `elder_care_skills` | — | Herramientas de cuidado |
| `pharmacy_interactions` | — | Interacciones de medicamentos |
| `company_loneliness_knowledge` | — | Soledad y duelo |
| `vigilance_devops_knowledge` | — | Sistemas y monitoring |
| `research_methodology` | — | Método científico |
| `federation_b2b_skills` | — | Federación entre empresas |
| `b2c_assistant_growth` | — | Asistente personal |
| `ia_heredable_legal` | — | IA heredable |
| `multimodal_perception` | — | Visión y voz |
| `language_patterns` | — | Patrones de lenguaje (sin LLM) |

**Carga desde el Dashboard:** `POST /api/capsules/load` con `{"name":"elder_care_knowledge"}` → inyecta 54 entries en memoria semántica, modelos causales, motor emocional, motor ético y validadores.

---

## Dashboard — 71 endpoints REST verificados

Todos los endpoints siguientes han sido testeados con `curl` real y devuelven **HTTP 200**:

### Core (13 endpoints)
| Endpoint | Función |
|---|---|
| `GET /` | Dashboard web (HTML) |
| `GET /ws` | WebSocket para chat en tiempo real |
| `POST /chat` | Chat REST (sin WebSocket) |
| `GET /stats` | Iteraciones, thoughts, ACD stats, router stats |
| `GET /state` | Energía, fatiga, metabolismo, physics, tensions |
| `GET /memory` | Memoria episódica de ZOE |
| `GET /identity` | Identidad criptográfica (hash SHA-256) |
| `POST /sleep` | ZOE duerme (consolida memoria) |
| `POST /wake` | ZOE despierta |
| `POST /llm` | Cambio de LLM en caliente |
| `GET /history` | Historial de conversación |
| `POST /feed` | Subir archivos (imágenes, audio) |

### Cápsulas (7 endpoints)
| Endpoint | Función |
|---|---|
| `GET /api/capsules` | Lista 15 cápsulas disponibles |
| `GET /api/capsules/loaded` | Cápsulas cargadas actualmente |
| `POST /api/capsules/load` | Cargar cápsula (inyecta entries en memoria) |
| `POST /api/capsules/unload` | Descargar cápsula |
| `GET /api/capsules/{name}/info` | Info detallada de una cápsula |
| `POST /api/capsules/{name}/validate` | Validar schema de cápsula |
| `POST /api/capsules/create` | Crear nueva cápsula |

### ACD Model Router (3 endpoints — Sprint 5.7.2)
| Endpoint | Función |
|---|---|
| `GET /api/router/stats` | Swaps, skips, last_routed_tag, active_profile |
| `GET /api/router/installed` | Modelos IQ2_M en el SSD (path, size, tag) |
| `GET /api/router/profile` | Perfil activo del ModelProfileRouter |

### Marketplace (5 endpoints)
| Endpoint | Función |
|---|---|
| `GET /api/marketplace/capsules` | Lista cápsulas del marketplace |
| `POST /api/marketplace/upload` | Subir cápsula al marketplace |
| `POST /api/marketplace/download/{name}` | Descargar cápsula del marketplace |
| `GET /api/marketplace/use_cases` | Lista casos de uso |
| `POST /api/marketplace/upload_use_case` | Subir caso de uso |

### Hardware & Models (8 endpoints)
| Endpoint | Función |
|---|---|
| `GET /api/hardware/system` | Info del sistema (RAM, CPU, chip) |
| `GET /api/hardware/ssds` | SSDs detectados |
| `GET /api/hardware/token_rates` | Velocidades estimadas por modelo |
| `GET /api/hardware/cable_warning` | Warning si cable USB 2.0 lento |
| `GET /api/models/system_info` | Info detallada del sistema |
| `GET /api/models/recommend` | Recomendación de modelo por RAM |
| `GET /api/models/catalog` | Catálogo de modelos disponibles |
| `POST /api/models/optimize` | Optimizar parámetros de un modelo |

### Federación epistémica (6 endpoints)
| Endpoint | Función |
|---|---|
| `POST /federation/epistemic/validate` | Validar claim con peer |
| `GET /federation/epistemic/knowledge/{hash}` | Recuperar knowledge por hash |
| `POST /federation/epistemic/register` | Registrar peer |
| `GET /federation/epistemic/peers` | Lista de peers |
| `GET /federation/epistemic/stats` | Stats de federación |
| `POST /federation/epistemic/request_validation` | Solicitar validación |

### Cuarentena (4 endpoints)
| Endpoint | Función |
|---|---|
| `GET /api/quarantine` | Knowledge en cuarentena |
| `GET /api/quarantine/stats` | Stats de cuarentena |
| `POST /api/quarantine/{id}/promote` | Promover knowledge validado |
| `POST /api/quarantine/{id}/reject` | Rechazar knowledge |

### Mentor digital (3 endpoints)
| Endpoint | Función |
|---|---|
| `GET /api/mentor` | Configuración del mentor |
| `POST /api/mentor` | Actualizar mentor |
| `GET /api/mentor/stats` | Stats del mentor |

### Resource Discovery, Model Bus, Planner, Embodiment, Seed Mode (19 endpoints)
- `GET/POST /api/resources/*` — grafo de recursos disponibles
- `GET/POST /api/modelbus/*` — bus universal de backends (lazy-init Sprint 5.7.3)
- `POST /api/planner/plan`, `GET /api/planner/stats`, `GET /api/planner/recommend` — planificador metabólico (lazy-init Sprint 5.7.3)
- `POST/GET /api/embodiment/*` — composer de encarnaciones
- `GET/POST /api/seed/*` — modo semilla portátil

### PWA (1 endpoint)
| Endpoint | Función |
|---|---|
| `GET /manifest.json` | Manifest para instalación como app móvil |

**Líneas de código:** ~41.000 LOC Python + ~16.300 LOC tests

### Roadmap resumido

| Estado | Fase | Entregable |
|---|---|---|
| ✅ | 0 — Bucle cognitivo | Observar-predecir-evaluar-decidir-actuar |
| ✅ | 0.5 — Organismo cognitivo | 6 leyes + 12 física + 6 campos + 5 tensiones |
| ✅ | 1 — Alma + Cuerpo + Metabolismo | Identity Vault + Trajectory Chain + 11 Memory Types |
| ✅ | 2 — Mente completa | 12 sub-agentes + Global Workspace + Meta-cog + Active Inference |
| ✅ | 3 — Integración + Persistencia | CognitiveLoopV3 + SQLite + MO V2 |
| ✅ | 4 — Federación + Deploy | CognitiveLoopV4 + federación HTTP + quorum |
| ✅ | 5 — ACD + Streaming | CognitiveLoopV5 + DepthClassifier + Cache + Streaming |
| ✅ | 6A — Epistemic Validation | EpistemicValidator + Quarantine + CrossValidator + Federation |
| ✅ | 6B — Capsules + Marketplace | 13 cápsulas + Scaffold + Marketplace + Dashboard UI |
| ✅ | 6C — Tutor Mentor Digital | MentorAgent configurable |
| ✅ | 7F — Cognitive Memory Paging | ModelOptimizer (mmap para 70B en 8GB) |
| ✅ | 7A — Resource Discovery | ResourceDiscoverySense + ResourceGraph |
| ✅ | 7B — Universal Model Bus | ModelBus ACD-aware + fallback |
| ✅ | 7C — Metabolic Resource Planner | ResourcePlanner (ACD+metabolismo+sensible) |
| ✅ | 7D — Embodiment Composer | Boot sequence 7A→7B→7C→7D |
| ✅ | 7E — ZOE Seed Mode | Semilla portátil que germina en cualquier host |
| ✅ | 7G — Hardware Optimization | P-cores + IQ2_M + flash-attn + SSDs + endpoints |
| ✅ | Sprint 1 — Multi-idioma + Windows + PWA + Telegram | 4 idiomas, Windows nativo, PWA móvil, bot Telegram |
| ✅ | Sprint 2 — Multi-modal | Visión (VLM) + Voz (STT/TTS) + cápsula multimodal |
| ✅ | Sprint 3 — Formato .zoe | PatternSpeaker (sin LLM) + ZoePackager + .zoe portátil |
| ✅ | Sprint 3.5 — ZoeRuntime | Runtime mínimo para ejecutar .zoe sin dependencias |
| ✅ | Sprint 3.6 — Enhanced PatternSpeaker | Destilación + retrieval + dialog state (sin LLM, más capaz) |
| ✅ | Sprint 4 — Voice-first mode | Conversación natural por voz + wake word + interrupción |
| ✅ | Sprint 5 — Cognitive Optimization Layer | .zmap + Cognitive Prefetch Layer + Tensor Prediction Engine |
| ✅ | Sprint 5.5 — ModelDownloader | Descarga IQ2_M de HuggingFace + Modelfile + registro Ollama |
| ✅ | Sprint 5.6 — ModelProfileRouter | Asignación de 4 modelos a 5 niveles ACD |
| ✅ | Sprint 5.7 — ACD Routing Wiring | L3_MAXIMUM + conexión al bucle V5 + bootstrap + zoe-setup |
| ✅ | Sprint 5.7.1 — Quickstart Audit | 9 bugs reales arreglados (cwd, retry Ollama, repo privado, etc.) |
| ✅ | Sprint 5.7.2 — Hot-swap fix + Dashboard endpoints | Bug speaker.llm arreglado + 3 endpoints /api/router/* |
| ✅ | Sprint 5.7.3 — Dashboard audit completo | cwd dinámico + lazy-init ModelBus/Planner + 71 endpoints verificados 200 OK |
| 🟡 | Pasarela pago marketplace | Stripe/PayPal |

**Roadmap completo:** [`docs/14_ROADMAP.md`](docs/14_ROADMAP.md)

---

## Documentación completa

### Documentos principales

| # | Documento | Para quién |
|---|---|---|
| 01 | [ZOE Overview](docs/01_ZOE_OVERVIEW.md) | Todos — qué es ZOE, evolución, filosofía |
| 02 | [Architecture](docs/02_ARCHITECTURE.md) | Arquitectos, CTO — arquitectura profunda |
| 03 | [Cognitive Engine](docs/03_COGNITIVE_ENGINE.md) | Todos — cómo piensa ZOE (12 sub-agentes, workspace, meta-cog, FEP) |
| 04 | [Memory & Learning](docs/04_MEMORY_AND_LEARNING.md) | Desarrolladores — 11 tipos de memoria, consolidación |
| 05 | [Epistemic Validation](docs/05_EPISTEMIC_VALIDATION.md) | Desarrolladores — validación de conocimiento |
| 06 | [Capsules Guide](docs/06_CAPSULES_GUIDE.md) | Autores, desarrolladores — 13 cápsulas + cómo crear |
| 07 | [Marketplace Guide](docs/07_MARKETPLACE_GUIDE.md) | Autores, compradores — marketplace y monetización |
| 08 | [Deployment Guide](docs/08_DEPLOYMENT_GUIDE.md) | DevOps, CTO — todas las opciones de despliegue |
| 09 | [Usage Guide](docs/09_USAGE_GUIDE.md) | Usuarios finales — CLI, Dashboard, API |
| 10 | [Hardware Optimization](docs/10_HARDWARE_OPTIMIZATION.md) | Usuarios, DevOps — performance, modelos, SSDs |
| 11 | [Security & Compliance](docs/11_SECURITY_COMPLIANCE.md) | CTO, legal — GDPR, HIPAA, EU AI Act |
| 12 | [Integration Guide](docs/12_INTEGRATION_GUIDE.md) | Desarrolladores — integrar ZOE en sistemas externos |
| 13 | [Troubleshooting](docs/13_TROUBLESHOOTING.md) | Todos — problemas comunes y soluciones |
| 14 | [Roadmap](docs/14_ROADMAP.md) | Todos — estado actual + futuro |
| 15 | [Development Guide](docs/15_DEVELOPMENT_GUIDE.md) | Contribuidores — tests, contribuir, ADRs |
| 16 | [ZOE Format (.zoe)](docs/16_ZOE_FORMAT.md) | Todos — formato .zoe portable, runtime, Enhanced PatternSpeaker |
| 17 | [Guía de Instalación y Uso](docs/17_USER_INSTALLATION_GUIDE.md) | No técnicos — instalación en SSD, Android, iPhone, VPS |
| 18 | [ZOE Explicación para No Técnicos](docs/18_ZOE_EXPLICACION_NO_TECNICOS.md) | **Cualquier persona** — qué es ZOE, cómo piensa, evoluciona, compara con ChatGPT |
| 19 | [ZOE Technical Internals](docs/19_ZOE_TECHNICAL_INTERNALS.md) | **Equipo técnico, CTOs, desarrolladores** — arquitectura completa, APIs, puntos de extensión, ADRs |

### Referencia

| Documento | Contenido |
|---|---|
| [API Reference](docs/REFERENCE/API_REFERENCE.md) | 50+ endpoints REST documentados |
| [Glossary](docs/REFERENCE/GLOSSARY.md) | Glosario completo de términos |
| [Configuration](docs/REFERENCE/CONFIGURATION.md) | Todas las opciones YAML |
| [Changelog](docs/REFERENCE/CHANGELOG.md) | Historial de versiones |

### Documentos históricos (obsoletos)

| Documento | Estado |
|---|---|
| [ZOE V1 Guide](docs/ZOE_V1_GUIDE.md) | ⚠️ Obsoleto (V1.0) |
| [ZOE V1 Auditoría](docs/ZOE_V1_AUDITORIA_Y_PRESENTACION.md) | ⚠️ Obsoleto |
| [Auditoría Técnica](docs/AUDITORIA_TECNICA_COMPLETA.md) | ⚠️ Obsoleto |
| [Certificado Funcionalidad](docs/CERTIFICADO_FUNCIONALIDAD.md) | ⚠️ Obsoleto |
| [Histórico Conversaciones](docs/historico_conversaciones_ZOE.md) | 📦 Archivo histórico (Fases 0-6) |

### Documentos ejecutivos

| Documento | Para quién |
|---|---|
| [Guía Ejecutiva](docs/ZOE_EXECUTIVE_GUIDE.md) | CEO, CFO, CMO, inversores (no técnico) |
| [Guía CTO](docs/ZOE_CTO_TECHNICAL_GUIDE.md) | CTO, VP Engineering (técnico) |

---

## Cómo contribuir

ZOE es **open source Apache 2.0**. Aceptamos contribuciones via pull requests.

### Tipos de contribución

- **Cápsulas de conocimiento**: crear nuevas cápsulas para dominios verticales
- **Casos de uso**: crear nuevos YAML para escenarios específicos
- **Backends LLM**: añadir soporte para nuevos proveedores
- **Senses/Actuators**: añadir nuevos sentidos o actuadores
- **Tests**: mejorar cobertura de tests
- **Documentación**: mejorar y traducir docs
- **Bug fixes**: reportar y arreglar bugs

### Empezar a contribuir

```bash
# 1. Fork + clone
git clone https://github.com/TU-USUARIO/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar en modo desarrollo
pip install -e ".[test]"

# 3. Ejecutar tests
pytest zoe/tests/ -q

# 4. Crear rama para tu feature
git checkout -b feature/mi-feature

# 5. Her commits + push + PR
```

**Guía completa de contribución:** [`docs/15_DEVELOPMENT_GUIDE.md`](docs/15_DEVELOPMENT_GUIDE.md)

---

## Licencia

**Apache 2.0** — ver [LICENSE](LICENSE)

```
Copyright 2026 Fernando Fondillo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## Enlaces

| Recurso | URL |
|---|---|
| **Repositorio** | https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO |
| **Issues** | https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues |
| **Pull Requests** | https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/pulls |
| **Documentación** | [`docs/`](docs/) |
| **Changelog** | [`docs/REFERENCE/CHANGELOG.md`](docs/REFERENCE/CHANGELOG.md) |
| **Ollama** | https://ollama.com |
| **OpenAI API** | https://platform.openai.com |
| **Anthropic API** | https://console.anthropic.com |

---

*ZOE V1.8.0 — Synthetic Cognitive Organism (SCO).*
*510+ tests · 15 cápsulas · 7 casos de uso · 4 idiomas · 9 plataformas · .zoe portable · Cognitive Optimization Layer · Sprint 1-5 completos*
*"ZOE no es un modelo que responde. Es un organismo que existe."*
