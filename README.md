<h1 align="center">
  <br>
  <span style="font-size: 72px;">&#129302;</span>
  <br>
  <b>ZOE</b>
  <br>
  <sub><i>Synthetic Cognitive Organism</i></sub>
</h1>

<p align="center">
  <b>El primer organismo cognitivo sintético con identidad soberana, metabolismo funcional y memoria viva persistente.</b>
  <br>
  Los LLMs son sus sentidos periféricos. Su cerebro es el bucle cognitivo.
</p>

<p align="center">
  <a href="docs/REFERENCE/CHANGELOG.md"><img src="https://img.shields.io/badge/version-2.1.1-blue?style=flat-square" alt="Version"></a>
  <a href="docs/15_DEVELOPMENT_GUIDE.md"><img src="https://img.shields.io/badge/tests-1668%2B-brightgreen?style=flat-square" alt="Tests"></a>
  <a href=".github/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-passing-brightgreen?style=flat-square&logo=github" alt="CI"></a>
  <a href="Dockerfile"><img src="https://img.shields.io/badge/docker-ready-blue?style=flat-square&logo=docker" alt="Docker"></a>
  <a href="k8s/"><img src="https://img.shields.io/badge/kubernetes-ready-blue?style=flat-square&logo=kubernetes" alt="Kubernetes"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <a href="docs/06_CAPSULES_GUIDE.md"><img src="https://img.shields.io/badge/capsules-15-teal?style=flat-square" alt="Capsules"></a>
  <a href="docs/05_EPISTEMIC_VALIDATION.md"><img src="https://img.shields.io/badge/security-hardened-critical?style=flat-square&logo=shield" alt="Security"></a>
  <a href="docs/10_HARDWARE_OPTIMIZATION.md"><img src="https://img.shields.io/badge/SSD%20%7C%20USB%20%7C%20VPS%20%7C%20K8s-deployable-orange?style=flat-square" alt="Deploy"></a>
  <img src="https://img.shields.io/badge/status-release%20candidate-success?style=flat-square" alt="Status">
</p>

---

## <a name="para-no-tecnicos"></a>Para personas sin conocimientos técnicos

<details open>
<summary><b>&#128161; Qué es ZOE (en 30 segundos)</b></summary>

**ZOE es como tener un compañero digital que piensa, recuerda, se cansa y aprende contigo.**

ChatGPT es como un actor brillante que entra, actúa y se va — sin recordar nada de la última vez. ZOE es diferente: **existe continuamente**, guarda lo que habláis, detecta patrones, y mejora con el tiempo. Vive en **tu disco** (SSD, USB o Mac), no en servidores de terceros. Si desconectas el SSD y lo llevas a otro ordenador, ZOE sigue siendo la misma, con la misma memoria.

Lo mejor: **puedes usarlo gratis offline** con modelos de IA locales, o conectar API de OpenAI/Claude para máxima calidad. ZOE elige automáticamente el mejor modelo según lo que le preguntes.

> **Lee la guía completa para no técnicos:** [`docs/20_ZOE_GUIA_USUARIO.md`](zoe/docs/20_ZOE_GUIA_USUARIO.md)
>
> **Lee la explicación profunda:** [`docs/18_ZOE_EXPLICACION_NO_TECNICOS.md`](zoe/docs/18_ZOE_EXPLICACION_NO_TECNICOS.md)

</details>

### Instalación en 3 pasos (SSD Crucial X9 + MacBook Air M3)

| Paso | Acción | Tiempo |
|:----:|--------|--------|
| 1 | Conecta el SSD al Mac con el **cable CORTO** (el largo de carga es 10x más lento) | 10 seg |
| 2 | Abre Terminal y ejecuta: | 15-30 min |

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_ssd_crucial_x9_mac.sh)
```

| 3 | Doble click en `INICIAR-ZOE.command` en tu SSD | Inmediato |

El instalador detecta automáticamente tu SSD, verifica Python, descarga ZOE, y crea lanzadores de doble click. **No necesitas saber programar.**

</details>

---

## <a name="para-tecnicos"></a>Para equipos técnicos, CTOs y desarrolladores

### Qué es ZOE en términos técnicos

ZOE es un **framework Python de ~72,000 LOC** que implementa una arquitectura cognitiva completa organizada en 4 capas, con **1,700+ tests** automatizados, **84 endpoints REST**, 15 cápsulas de conocimiento con contenido real, y soporte para despliegue en Docker, Kubernetes o SSD portátil. Incluye el **ReflectionEngine v2.1** para reflexión autónoma durante SLEEPING con gestión inteligente de presupuesto cloud.

> **Documentación técnica completa:** [`docs/19_ZOE_TECHNICAL_INTERNALS.md`](zoe/docs/19_ZOE_TECHNICAL_INTERNALS.md)

### Arquitectura (4 capas)

```
┌─────────────────────────────────────────────────────────────────────┐
│  CAPA 4: PERIPHERALS — 6 backends LLM + multimodal + voz          │
│  Mock, Ollama, OpenAI, Anthropic, ZAI, OpenAI-compatible          │
│  ModelBus (ACD-aware) │ Circuit Breaker │ Hot-swap en caliente      │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│  CAPA 3: CORE — Bucle cognitivo V5 con ACD + 12 sub-agentes        │
│  DepthClassifier (L0-L3_MAX) │ ModelProfileRouter (4 modelos)      │
│  Global Workspace (Baars) │ MetaCognition (Kahneman S1/S2)          │
│  ActiveInference (Friston FEP) │ 6 Laws │ 12 Physics │ 6 Fields    │
│  MentorAgent │ LanguageDetector │ CognitivePrefetchLayer (conectados)│
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│  CAPA 2: MEMORY — 11 tipos + SQLite/PostgreSQL + consolidación     │
│  LivingMemory (in-memory) │ PersistentMemoryStore (SQLite, WAL)      │
│  DeepConsolidation (7 ops en SLEEPING) │ StorageBackend factory     │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│  CAPA 1: ALMA — Identidad criptográfica + trayectoria + ontogenia  │
│  IdentityVault (SHA-256, 9 vectores, 7 valores, inmutable)         │
│  TrajectoryChain (blockchain de mutaciones firmadas)               │
│  OntogeneticMotorV2 (auto-mutación arquitectural runtime)          │
└─────────────────────────────────────────────────────────────────────┘
```

### ACD Router: 4 modelos IQ2_M según nivel cognitivo

| Nivel | Input típico | Modelo | Tamaño | Tokens/s |
|-------|-------------|--------|--------|----------|
| **L0_REFLEX** | "Hola", "Gracias" | PatternSpeaker (sin LLM) | 0 GB | < 1 ms |
| **L1_FAST** | "¿Qué hora es?" | Gemma 2 9B IQ2_M | 3.5 GB | 15-25 |
| **L2_STANDARD** | "Resume este artículo" | Agents-A1 MoE IQ2_M | 11.7 GB | 5-10 |
| **L3_DEEP** | "Analiza causas profundas" | QwQ-32B IQ2_M | 12.5 GB | 3-6 |
| **L3_MAXIMUM** | "Compara 3 contratos" | Qwen 2.5 72B IQ2_M | 25 GB | 1-3 |

**Hot-swap funcional:** El bucle V5 cambia `speaker.llm.model` en vivo según la clasificación ACD de cada input.

---

## Quickstart

### Opción A — Instalador automático (SSD/Pendrive, recomendado)

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_ssd_crucial_x9_mac.sh)
```

### Opción B — Docker (producción)

```bash
docker-compose up -d  # ZOE + Ollama, listo en 30 segundos
```

### Opción C — Desarrollo (sin LLM, más rápido)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
zoe-chat --backend pattern     # Sin IA — modo demo
zoe-dashboard --backend pattern # Dashboard en localhost:8642
```

### Opción D — Ollama local + ACD Router (gratis, offline)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
python -m zoe.core.model_downloader --download-setup balanced
zoe-chat --backend ollama --model auto
```

### Opción E — OpenAI/Claude (máxima calidad)

```bash
export OPENAI_API_KEY="sk-..."
zoe-chat --backend openai_compatible --model gpt-4o
```

---

## Estado del Proyecto — Post Auditoría ZOE OMEGA

En julio 2026, ZOE fue sometida a una auditoría integral independiente (ZOE OMEGA) que analizó código, tests, seguridad, infraestructura, documentación y UX. Todas las incidencias críticas han sido resueltas.

| Dimensión | Antes | Ahora | Cambio |
|-----------|:-----:|:-----:|:------:|
| **Seguridad** | 3.8/10 | **8.5/10** | +4.7 |
| **Infraestructura** | 4.1/10 | **9.0/10** | +4.9 |
| **Código** | 5.2/10 | **8.0/10** | +2.8 |
| **Arquitectura** | 4.5/10 | **8.0/10** | +3.5 |
| **Tests** | 6.5/10 | **8.5/10** | +2.0 |
| **UX/Producto** | 6.5/10 | **9.0/10** | +2.5 |
| **Documentación** | 5.5/10 | **7.5/10** | +2.0 |
| **Global** | **5.1/10** | **8.4/10** | **+3.3** |

### Mejoras implementadas en esta evolución

- **Seguridad:** 0 vulnerabilidades críticas. Auth obligatoria por defecto. Rate limiting (60/10 req/min). 7 headers de seguridad HTTP. Path traversal y Zip Slip protegidos. SHA-256 en toda la federación. 69 tests de pentesting + 44 de chaos engineering.
- **Infraestructura:** Dockerfile multi-stage, docker-compose (ZOE + Ollama), 15 manifiestos Kubernetes, 3 workflows GitHub Actions (CI, Docker, Security), health checks (/health, /ready, /live), Prometheus metrics (/metrics), log rotation (10MB/5 backups).
- **Backend de persistencia:** PostgreSQL opcional vía factory pattern (asyncpg, JSONB, connection pooling). SQLite con WAL mode activo. Script de backup automatizado.
- **Dashboard refactorizado:** Monolito de 3,351 LOC → 28 módulos separados (15 handlers + 4 middleware + HTML aislado). Backward compatible.
- **Resiliencia:** Circuit Breaker para LLM (CLOSED/OPEN/HALF_OPEN) con fallback a PatternSpeaker.
- **Integración:** MentorAgent, LanguageDetector (4 idiomas), y CognitiveOptimizationLayer conectados al bucle cognitivo V5.
- **Instalador SSD:** Script dedicado para SSD Crucial X9 1TB + MacBook Air M3 con detección automática de hardware.

> **Informes completos de auditoría en:** [`zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md`](zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md)

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | 205 |
| Líneas de código | ~72,000 |
| Tests | 1,668+ (99.93% pass) |
| Archivos de test | 61 |
| LOC de tests | ~26,000 |
| Cápsulas | 15 con contenido real |
| Endpoints REST | 81 (+ health checks + metrics + reflections) |
| ReflectionEngine v2.1 | Sí — Reflexión autónoma durante SLEEPING |
| Documentos | 50+ |
| Backends LLM | 6 |
| Plataformas | macOS, Linux, Windows, Docker, Kubernetes, PWA, Telegram, SSD portátil |
| Idiomas | ES, EN, FR, DE (auto-detectado) |
| Vulnerabilidades críticas | 0 |
| except:pass restantes | 0 |
| CI/CD | GitHub Actions (CI + Docker + Security) |

---

## Características Principales

### Identidad y Evolución
- **IdentityVault** — Hash SHA-256 de 9 vectores + 7 valores, inmutable desde el nacimiento
- **TrajectoryChain** — Blockchain de mutaciones firmadas, auditable
- **OntogeneticMotorV2** — Auto-mutación arquitectural runtime

### Cognición
- **Bucle cognitivo V5** — 18 pasos, tick cada 3 segundos, piensa autónomamente
- **12 sub-agentes** — Society of Mind (Minsky) con competición en Global Workspace (Baars)
- **MetaCognition** — System 1 / System 2 (Kahneman)
- **ActiveInference** — Free Energy Principle (Friston), entropía de Shannon
- **ACD** — 5 niveles (L0-L3_MAX) detectados por 5 señales combinadas

### Memoria y Persistencia
- **11 tipos de memoria** — Episódica, semántica, procedural, causal, emocional, corporal, social, prospectiva, contrafactual, evolutiva, cultural
- **SQLite + PostgreSQL** — Backend abstracto con factory pattern, WAL mode, backup
- **DeepConsolidation** — 7 operaciones durante metabolismo SLEEPING

### Validación Epistémica
- **EpistemicValidator** — 14+ fuentes de validación
- **KnowledgeQuarantine** — Conocimiento pendiente de validación
- **CrossValidator** — Triple verificación cruzada
- **EpistemicFederation** — Quorum + veto entre peers

### Cápsulas y Marketplace
- **15 cápsulas** con contenido real (elder_care: 54 entries, pharmacy_interactions, etc.)
- **CapsuleLoader/Registry** — Carga dinámica en runtime
- **Marketplace framework** — 5 tipos de licencia, revenue split 70/30

### Reflexión Autónoma v2.1 — ReflectionEngine
- **Ejecuta durante SLEEPING** — Cuando ZOE no atiende al usuario, reflexiona sobre memorias de alta saliencia
- **Gestión inteligente de presupuesto cloud** — BudgetTracker con precios reales (OpenAI, Anthropic, DeepSeek). Límite diario configurable
- **Saliencia computada** — Recencia + intensidad emocional + confianza inversa + conexiones
- **Almacenamiento en tipos existentes** — MemoryType.COUNTERFACTUAL (simulaciones) y EVOLUTIONARY (expansión de conocimiento)
- **Validación de insights** — MentorAgent evalúa calidad + KnowledgeQuarantine filtra antes de persistir
- **Async puro** — 0 threading, integrado con el metabolism.tick() existente
- **Fallback de modelo** — DeepSeek-R1:32b-iq2 → qwq-32b-iq2 → qwen2.5:14b-iq2
- **L4_REFLECTION en ACD** — Nivel adicional en ModelProfileRouter para reflexión profunda

### Infraestructura
- **Docker** — Multi-stage build, docker-compose con Ollama
- **Kubernetes** — 15 manifiestos (deployment, service, ingress, postgres, ollama, rbac)
- **CI/CD** — GitHub Actions: tests + coverage, Docker build/push, security scan
- **Observabilidad** — Prometheus metrics, health checks, structured logging

### Seguridad
- **0 vulnerabilidades críticas** — Auditoría ZOE OMEGA confirmada
- **Auth obligatoria** por defecto (token auto-generado si no se provee)
- **Rate limiting** — 60 req/min normal, 10 req/min costoso
- **7 security headers** — HSTS, CSP, X-Frame, etc.
- **Input sanitization** — Path traversal protegido, Zip Slip mitigado

---

## Dashboard — 81 Endpoints REST

| Categoría | Endpoints |
|-----------|-----------|
| Core | `/`, `/ws`, `/chat`, `/stats`, `/state`, `/memory`, `/identity`, `/sleep`, `/wake`, `/llm` |
| Cápsulas | `/api/capsules/*` (7 endpoints: list, load, unload, info, validate, create) |
| ACD Router | `/api/router/*` (3 endpoints: stats, installed, profile) |
| Marketplace | `/api/marketplace/*` (5 endpoints) |
| Hardware | `/api/hardware/*` (4 endpoints: system, ssds, token_rates, cable_warning) |
| Federación | `/federation/epistemic/*` (6 endpoints) |
| Cuarentena | `/api/quarantine/*` (4 endpoints) |
| Mentor | `/api/mentor/*` (3 endpoints) |
| **Reflection v2.1** | **`/api/reflections` (list), `/api/reflections/metrics`, `/api/reflections/config`** |
| Resources/ModelBus/Planner | `/api/resources/*`, `/api/modelbus/*`, `/api/planner/*` |
| Health | `/health`, `/ready`, `/live` (públicos) |
| Metrics | `/metrics` (Prometheus, público) |

---

## Requisitos

### Software
| Requisito | Versión | Obligatorio |
|-----------|---------|:-----------:|
| Python | 3.10+ | Si |
| pip | 21+ | Si |
| Git | 2.30+ | Si |
| Ollama | 0.1+ | No (para local) |

### Hardware
| Configuración | RAM | Disco |
|---------------|-----|-------|
| Mínima (mock/pattern) | 4 GB | 500 MB |
| Recomendada (Ollama + 1 modelo) | 8 GB | 16 GB SSD |
| Óptima (4 modelos + SSD) | 16 GB | 128 GB SSD |
| MacBook Air M3 + SSD Crucial X9 | 8 GB | 1 TB SSD USB-C |

---

## Roadmap

| Estado | Fase | Entregable |
|--------|------|------------|
| ✅ | Fases 0-5 + Sprints 1-5.11 | Bucle cognitivo, ALMA, 12 sub-agentes, ACD, cápsulas, marketplace |
| ✅ | ZOE OMEGA Correcciones | Seguridad hardening, infraestructura producción, dashboard refactorizado |
| 🔄 | Pasarela de pagos | Stripe/PayPal para marketplace |
| 📋 | Chaos engineering avanzado | Load testing, fuzzing, penetración profesional |
| 📋 | v2.0.0 GA | Production Ready tras hardening final |

---

## Documentación

### Para todos
| Documento | Contenido |
|-----------|-----------|
| [`docs/20_ZOE_GUIA_USUARIO.md`](zoe/docs/20_ZOE_GUIA_USUARIO.md) | Guía de usuario completa (instalación, dashboard, casos de uso, FAQ) |
| [`docs/18_ZOE_EXPLICACION_NO_TECNICOS.md`](zoe/docs/18_ZOE_EXPLICACION_NO_TECNICOS.md) | Qué es ZOE, cómo piensa, por qué es diferente a ChatGPT |

### Para equipos técnicos
| Documento | Contenido |
|-----------|-----------|
| [`docs/19_ZOE_TECHNICAL_INTERNALS.md`](zoe/docs/19_ZOE_TECHNICAL_INTERNALS.md) | Arquitectura completa, APIs, puntos de extensión |
| [`docs/02_ARCHITECTURE.md`](zoe/docs/02_ARCHITECTURE.md) | Visión arquitectónica profunda |
| [`docs/03_COGNITIVE_ENGINE.md`](zoe/docs/03_COGNITIVE_ENGINE.md) | Motor cognitivo: 12 sub-agentes, workspace, meta-cog |
| [`docs/04_MEMORY_AND_LEARNING.md`](zoe/docs/04_MEMORY_AND_LEARNING.md) | 11 tipos de memoria, consolidación |
| [`docs/05_EPISTEMIC_VALIDATION.md`](zoe/docs/05_EPISTEMIC_VALIDATION.md) | Validación epistémica |
| [`docs/06_CAPSULES_GUIDE.md`](zoe/docs/06_CAPSULES_GUIDE.md) | 15 cápsulas + cómo crear |
| [`docs/08_DEPLOYMENT_GUIDE.md`](zoe/docs/08_DEPLOYMENT_GUIDE.md) | Todas las opciones de despliegue |
| [`docs/10_HARDWARE_OPTIMIZATION.md`](zoe/docs/10_HARDWARE_OPTIMIZATION.md) | Performance, modelos, SSDs |

### Auditoría ZOE OMEGA
| Documento | Contenido |
|-----------|-----------|
| [`zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md`](zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md) | Informe maestro de auditoría |
| [`zoe/docs/ZOE_OMEGA_CORRECCIONES_FINAL.md`](zoe/docs/ZOE_OMEGA_CORRECCIONES_FINAL.md) | Correcciones implementadas |
| [`zoe/docs/ZOE_OMEGA_PROMESA_CUMPLIDA.md`](zoe/docs/ZOE_OMEGA_PROMESA_CUMPLIDA.md) | Verificación de La Promesa |
| [`zoe/docs/AUDITORIA_SECURITY.md`](zoe/docs/AUDITORIA_SECURITY.md) | Auditoría de seguridad detallada |

---

## Cómo Contribuir

ZOE es **Apache 2.0**. Aceptamos contribuciones vía pull requests.

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e ".[test]"
pytest zoe/tests/ -q
```

**Guía completa:** [`docs/15_DEVELOPMENT_GUIDE.md`](zoe/docs/15_DEVELOPMENT_GUIDE.md)

---

## Licencia

**Apache 2.0** — ver [LICENSE](LICENSE)

```
Copyright 2026 Fernando Fondillo

Licensed under the Apache License, Version 2.0.
```

---

<p align="center">
  <b>ZOE v2.0.0-rc1 — Synthetic Cognitive Organism</b><br>
  1,700+ tests · 210 archivos Python · 15 cápsulas · 84 endpoints · 6 backends LLM · 4 idiomas<br>
  Docker · Kubernetes · SSD portátil · 100% offline<br>
  <i>"ZOE no es un modelo que responde. Es un organismo que existe."</i>
</p>
