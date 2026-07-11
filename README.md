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

## Quickstart (3 minutos)

### Opción A — Instalación automática en SSD/Pendrive (recomendado)

**Un solo comando** configura ZOE completo en tu SSD: detecta hardware, instala ZOE, descarga modelos, crea lanzadores y arranca el Dashboard.

```bash
# Conecta tu SSD al Mac (usa el cable CORTO de la caja)
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash
```

El instalador te guía paso a paso:
1. Detecta tu SSD automáticamente
2. Verifica Python y Git
3. Instala ZOE + entorno virtual **EN EL SSD** (no carga tu Mac)
4. Te pregunta si instalar Ollama (IA local gratis)
5. Te pregunta qué modelos descargar al SSD
6. Configura API keys opcionales (OpenAI, Anthropic)
7. Crea scripts de doble clic (.command en macOS)
8. Arranca el Dashboard automáticamente

**No necesitas saber programar.** El instalador lo hace todo.

### Opción B — Sin LLM, sin SSD (lo más rápido para probar)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
zoe-chat --backend pattern          # funciona sin IA, sin Ollama, sin API
zoe-dashboard --backend pattern     # Dashboard web en http://localhost:8642
```

### Opción C — Con Ollama local (gratis, más potente)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .

# Instalar Ollama desde https://ollama.com
ollama pull qwen2.5:3b              # 2GB, gratis

zoe-chat --backend ollama --model qwen2.5:3b
zoe-dashboard --backend ollama --model qwen2.5:3b
```

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
| **Windows nativo** + installer PowerShell | Sprint 1 — `install_windows.ps1` |
| **PWA** (instalable como app móvil) | Sprint 1 — manifest + responsive CSS |
| **Telegram bot** bridge | Sprint 1 — `telegram_bridge.py` |
| **Multi-modal** (Visión VLM + Voz STT/TTS) | Sprint 2 — `multimodal.py` |
| **Cápsula multimodal_perception** | Sprint 2 — 14ª cápsula |
| **PatternSpeaker** (generación sin LLM) | Sprint 3 — `pattern_speaker.py` |
| **Enhanced PatternSpeaker** (destilación + retrieval + dialog) | Sprint 3.6 — `enhanced_pattern_speaker.py` |
| **Formato .zoe** (organismo en un archivo) | Sprint 3 — `zoe_packager.py` |
| **ZoeRuntime** (ejecutar .zoe sin dependencias) | Sprint 3.5 — `zoe_runtime.py` |
| **Cápsula language_patterns** | Sprint 3 — 15ª cápsula |
| **Cognitive Optimization Layer** (.zmap + CPL + TPE) | Sprint 5 — `cognitive_optimization.py` |
| **GDPR/HIPAA/EU AI Act** compliant por diseño | [Security & Compliance](docs/11_SECURITY_COMPLIANCE.md) |
| **510 tests automatizados** (100% pass) | [Development Guide](docs/15_DEVELOPMENT_GUIDE.md) |

---

## Cómo optimiza ZOE según el LLM disponible

ZOE tiene un sistema inteligente (Cognitive Optimization Layer) que **usa la información que ya tiene** (qué tipo de pregunta es, qué memoria tiene, qué cápsulas están cargadas) para decidir la mejor forma de responder.

### Funciona con cualquier configuración:

| Tu configuración | Pregunta simple (L0/L1) | Pregunta compleja (L2/L3) |
|---|---|---|
| **Sin LLM** (solo Python) | PatternSpeaker: instantáneo, gratis, offline | PatternSpeaker + destiladas + cápsulas: decente sin LLM |
| **Ollama local** (gratis) | PatternSpeaker: no toca Ollama, ahorra RAM | CPL pre-carga modelo + .zmap optimiza capas + LLM responde |
| **Cloud API** (GPT-4o/Claude) | PatternSpeaker: no gasta API, ahorra €€ | CPL pre-construye contexto + API responde con máxima calidad |
| **.zoe portátil** | PatternSpeaker: siempre disponible | PatternSpeaker + destiladas (si las hay) |

**El usuario no configura nada.** ZOE detecta qué tiene disponible y elige la mejor opción automáticamente.

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
**Fases completas:** 0, 0.5, 1, 2, 3, 4, 5, 6A, 6B, 6C, 7F, 7A, 7B, 7C, 7D, 7E, 7G + Sprint 1, 2, 3, 3.5, 3.6, 4, 5
**Tests:** 510+ tests, 100% pasando
**Cápsulas:** 15 operativas (13 originales + multimodal_perception + language_patterns)
**Casos de uso:** 7 documentados
**Endpoints REST:** 50+
**Idiomas:** 4 (ES, EN, FR, DE)
**Plataformas:** macOS, Linux, Windows, Docker, Kubernetes, PWA móvil, Telegram, .zoe portable
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
| 17 | [Guía de Instalación y Uso (No Técnicos)](docs/17_USER_INSTALLATION_GUIDE.md) | Todos — guía paso a paso simplificada |

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
