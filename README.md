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
  <a href="docs/REFERENCE/CHANGELOG.md"><img src="https://img.shields.io/badge/version-2.1.2-blue?style=flat-square" alt="Version"></a>
  <a href="docs/15_DEVELOPMENT_GUIDE.md"><img src="https://img.shields.io/badge/tests-1700%2B-brightgreen?style=flat-square" alt="Tests"></a>
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

## Por que ZOE es un Organismo (no una herramienta)

ZOE es un **Organismo Cognitivo Sintetico** porque el codigo demuestra:

| Capacidad | Evidencia en codigo |
|-----------|---------------------|
| **Piensa sin input** | Bucle cognitivo infinito con 5 fases (OBSERVE -> PREDICT -> EVALUATE -> DECIDE -> ACT) que corre cada 3-5s |
| **Se cansa y duerme** | 4 estados metabolicos (AWAKE/DROWSY/SLEEPING/WAKING) con umbrales de fatiga |
| **Tiene identidad inmutable** | SHA-256 de 9 vectores + 7 valores + proposito. Ninguna mutacion puede alterarlos |
| **11 tipos de memoria** | Episodica, Semantica, Procedural, Causal, Emocional, Corporal, Social, Prospectiva, Contrafactual, Evolutiva, Cultural |
| **Consolida mientras duerme** | 7 operaciones de DeepConsolidation durante SLEEPING |
| **Registra cada cambio** | TrajectoryChain criptografica con hashes encadenados (blockchain de la vida de ZOE) |
| **Tiene 6 leyes constitucionales** | UTILITY, IDENTITY, PROVENANCE, COST, CONFIDENCE, MODULARITY — cada accion se verifica |
| **Modifica su arquitectura** | OntogeneticMotorV2 puede anadir/eliminar sub-agentes, modificar thresholds, ajustar metabolismo |
| **Evoluciona como especie** | PhylogeneticMotor con pool compartido: mejoras validadas por >=2 ZOEs se propagan |
| **Delibera consciente** | GlobalWorkspace (Baars) + MetaCognition (Kahneman S1/S2) |
| **Mutaciones reales** | organism.subagents.append() — modificaciones de objetos Python en runtime |
| **No reescribe su pasado** | Rollback anade, nunca elimina. La cadena es inmutable |

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

ZOE es un **framework Python de ~68,000 LOC** que implementa una arquitectura cognitiva completa organizada en 4 capas, con **1,381+ tests** automatizados, **81 endpoints REST**, 15 cápsulas de conocimiento con contenido real, 12 sub-agentes, y soporte para despliegue en Docker, Kubernetes o SSD portátil. Incluye el **ReflectionEngine v2.1** para reflexión autónoma durante SLEEPING con gestión inteligente de presupuesto cloud.

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
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh)
```

Tras la instalación tendrás **seis lanzadores de doble click** en el SSD:

- `INICIAR-DASHBOARD.command` — Abre el Dashboard web en tu navegador (recomendado para usuarios no técnicos).
- `INICIAR-ZOE.command` — Abre el chat en Terminal con detección automática de backend.
- `ZOE-Dashboard-Ollama.command` — Dashboard con ACD Router (5 niveles cognitivos) usando Ollama.
- `ZOE-Chat-Ollama.command` — Chat con ACD Router en Terminal.
- `ZOE-Dashboard.command` / `ZOE-Chat.command` — Dashboard/chat con PatternSpeaker (offline, sin IA).

> **El instalador `zoe-bootstrap.sh`** detecta automáticamente tu SSD, tu RAM (8/16GB), verifica formato (exFAT/APFS), instala Ollama si falta, descarga modelos IQ2_M optimizados al SSD (configurando `OLLAMA_MODELS` via symlink), configura API keys opcionales, crea los lanzadores, y opcionalmente arranca el Dashboard. **Sin pasos manuales.**
>
> **Importante: coherencia SSD garantizada.** Todos los lanzadores pasan `--db-path "${ZOE_DATA:-$ZOE_HOME/data}/..."` para que el Dashboard y el Chat carguen el **mismo ZOE** (misma identidad, memoria, trayectoria) del SSD. Sin esta corrección (Sprint 5.12 GAP-Q), Dashboard y Chat crearían dos ZOEs distintos — uno en el SSD y otro en el Mac.
>
> **Alternativa:** `install_ssd_crucial_x9_mac.sh` es un instalador más ligero que NO instala Ollama ni descarga modelos. Úsalo solo si ya tienes Ollama instalado.
>
> **Manual completo paso a paso:** [`zoe/docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md`](zoe/docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md) — 2,090+ líneas, 19 secciones, pensado para que un no-técnico instale y use ZOE sin ninguna duda.

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

- **Seguridad:** 0 vulnerabilidades críticas. Auth obligatoria por defecto. Rate limiting (60/10 req/min) refactorizado a middleware funcional compatible con aiohttp 3.13+. 7 headers de seguridad HTTP. Path traversal y Zip Slip protegidos. SHA-256 en toda la federación. 69 tests de pentesting + 44 de chaos engineering. 34 bare except eliminados, 7 MD5 -> SHA-256.
- **Infraestructura:** Dockerfile multi-stage, docker-compose (ZOE + Ollama), 15 manifiestos Kubernetes, 3 workflows GitHub Actions (CI, Docker, Security), health checks (/health, /ready, /live), Prometheus metrics (/metrics), log rotation (10MB/5 backups).
- **Backend de persistencia:** PostgreSQL opcional vía factory pattern (asyncpg, JSONB, connection pooling). SQLite con WAL mode activo. Script de backup automatizado.
- **Dashboard refactorizado y utilizable:** Monolito de 3,351 LOC → 28 módulos separados (15 handlers + 4 middleware + HTML aislado). Backward compatible. **Sprint 5.12:** HTML maneja auth token automáticamente (?token= en URL → localStorage → Authorization: Bearer en fetch/XHR/WS). Modal de auth si falta token. Persistencia del token en `data/dashboard_token.txt`.
- **Resiliencia:** Circuit Breaker para LLM (CLOSED/OPEN/HALF_OPEN) con fallback a PatternSpeaker.
- **Integración:** MentorAgent, LanguageDetector (4 idiomas), y CognitiveOptimizationLayer conectados al bucle cognitivo V5.
- **Instalador SSD:** Script dedicado para SSD Crucial X9 1TB + MacBook Air M3 con detección automática de hardware. Crea 3 lanzadores universales (`INICIAR-DASHBOARD.command`, `INICIAR-ZOE.command`, `ZOE-Smart.command`) con detección automática de backend (Ollama > OpenAI > Anthropic > pattern).
- **L4_REFLECTION adaptativo por RAM:** DeepSeek-R1 32B IQ2_M (8GB) / Q4_K_M (16GB+), detectado automáticamente.
- **BudgetTracker:** Control de costes cloud con precios reales (OpenAI, Anthropic, DeepSeek). Límite diario configurable.
- **Thinking indicator:** "ZOE está pensando..." con animación visual durante procesamiento LLM.
- **Global Workspace recuperado:** Teoría de Baars implementada en `global_workspace.py`.
- **Manual de usuario completo:** 2,078 líneas en `docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md`, 19 secciones, pensado para que un no-técnico instale ZOE en SSD + Mac sin ninguna duda.

> **Informes completos de auditoría en:** [`zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md`](zoe/docs/ZOE_OMEGA_AUDITORIA_FINAL.md)

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | 210+ |
| Líneas de código | ~70,000 |
| Tests | 1,700+ (Sprint 5.12 añadió 8 tests) |
| Archivos de test | 62 |
| LOC de tests | ~28,000 |
| Cápsulas | 15 |
| Sub-agentes | 12 |
| Endpoints REST | 81 (+ health checks + metrics + reflections) |
| ReflectionEngine v2.1 | Sí — Reflexión autónoma durante SLEEPING |
| Documentos | 42+ (Manual de usuario ampliado a 2,078 líneas) |
| Backends LLM | 6 |
| Plataformas | macOS, Linux, Windows, Docker, Kubernetes, PWA, Telegram, SSD portátil |
| Idiomas | ES, EN, FR, DE (auto-detectado) |
| Vulnerabilidades críticas | 0 |
| except:pass restantes | 0 |
| CI/CD | GitHub Actions (CI + Docker + Security) |
| Lanzadores macOS | 6 (.command) + 6 en Linux (.sh) |

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

## Gaps Resueltos (Auditoria ZOE-SPEC-002)

Tres gaps identificados en la auditoria fundacional han sido resueltos sin deconstruir ni romper backward compatibility:

| Gap | Archivo | Estado |
|-----|---------|--------|
| `merge_subagents` no implementado | `zoe/alma/ontogenetic_motor_v2.py` | **Resuelto** |
| `reorganize_memory` no implementado | `zoe/alma/ontogenetic_motor_v2.py` | **Resuelto** |
| `serve.py` usa V4 (sin ACD ni persistencia) | `zoe/serve.py` | **Resuelto** |

### merge_subagents (OntogeneticMotorV2)

Fusiona dos sub-agentes del mismo tipo funcional en uno solo. Transferencia de estado interno (listas y diccionarios de atributos privados), eliminacion del source, verificacion de que ambos son del mismo tipo. Ahora las 7 mutaciones arquitecturales estan implementadas: add_subagent, remove_subagent, merge_subagents, modify_threshold, adjust_workspace_capacity, adjust_metabolism_threshold, reorganize_memory.

### reorganize_memory (OntogeneticMotorV2)

Reorganiza la estructura de la memoria en runtime. Acciones soportadas:
- **resize**: cambia LivingMemory.max_entries (olvida entradas si hay overflow)
- **retune_save_interval**: cambia auto_save_interval de PersistentMemoryStore
- **deactivate_type**: desactiva un MemoryType (nuevas entradas van a semantica)
- **activate_type**: reactiva un MemoryType previamente desactivado

Diferente de LivingMemory.think() y DeepConsolidation.consolidate() que reorganizan el CONTENIDO automaticamente. reorganize_memory cambia la ESTRUCTURA.

### serve.py migrado a V5

El entrypoint de produccion ahora usa CognitiveLoopV5 (hereda V4, backward-compatible):
- **ACD**: Adaptive Cognitive Depth con DepthClassifier
- **CognitiveCache**: idempotencia para entradas repetidas
- **LanguageDetector**: deteccion automatica de idioma
- **Persistencia**: identidad y trayectoria se cargan/guardan de disco entre reinicios
- **V5 sin V5-components** = V4: si no se pasan depth_classifier ni cognitive_cache, V5 se comporta como V4

---

## Mejoras ZOE-SPEC-002 (6 puntos)

Seis mejoras implementadas siguiendo el principio "añadir, no reemplazar; opt-in, no obligatorio":

### 1. Busqueda semantica (embeddings opcionales)

**Problema:** `LivingMemory.search()` usaba Jaccard (coincidencia lexica). "madre" y "progenitora" = similitud 0.

**Solucion:** `SemanticSearch` en `zoe/memory/semantic_search.py`:
- Usa `sentence-transformers` (instalacion: `pip install sentence-transformers`)
- Embeddings cacheados por entry_id
- Similitud coseno entre query y entries
- Fallback automatico a Jaccard si no esta instalado
- `memory.search("query", use_semantic=True)` — parametro opt-in

```python
from zoe.core.living_memory import LivingMemory
lm = LivingMemory()
results = lm.search("gato durmiendo")           # Jaccard (default)
results = lm.search("gato durmiendo", use_semantic=True)  # Semantico
```

### 2. Cobertura de tests medida

**Problema:** 1,381+ tests sin saber que porcentaje del codigo cubren.

**Solucion:** Configuracion completa:
- `pytest-cov>=4.1.0` en `extras_require["test"]`
- `.coveragerc`: source=zoe, omite tests/examples/phases, show_missing
- `pytest.ini`: testpaths, asyncio_mode

```bash
pip install -e ".[test]"
pytest --cov=zoe --cov-report=term-missing --cov-report=html
```

### 3. PhylogeneticMotor con persistencia

**Problema:** Pool en memoria; ZOEs en procesos diferentes no comparten mejoras.

**Solucion:** `DistributedPhylogeneticPool` en `zoe/core/distributed_phylogenetic_pool.py`:
- Persistencia JSON atomica (write tmp + replace)
- Lazy reload antes de cada read
- Misma interfaz que `PhylogeneticPool`
- Opt-in via `pool_path` en `PhylogeneticMotor.__init__()`

```python
from zoe.core.phylogenetic_motor import PhylogeneticMotor
motor = PhylogeneticMotor(zoe_id="zoe_A", pool_path="/ssd/zoe/phylogenetic_pool.json")
```

### 4. EmbodimentComposer en CLI

**Problema:** 772 LOC de composer no se usaban en el flujo principal.

**Solucion:** `--compose` en `cli_chat.py`:
- `python -m zoe.cli_chat --compose` ejecuta composer, guarda plan, sale
- Proximo arranque lee `embodiment_plan.json` y aplica configuraciones
- Ajusta `max_entries`, `tick_interval` segun el hardware detectado
- Opt-in: sin plan, usa defaults actuales

### 5. SeedMode auto-start

**Problema:** `germinate()` devolvia reporte pero no arrancaba ZOE.

**Solucion:** Parametro `auto_start: bool = False` en `ZOESeed.germinate()`:
- `python -m zoe.core.seed_mode --auto-start` germina y arranca en un paso
- Crea `ZoeChat` con backend segun manifiesto, inicializa y corre
- `GerminationReport` incluye `auto_started` y `auto_start_status`
- Default `False`: comportamiento existente preservado

### 6. Federation discovery

**Problema:** Registro manual de pares (90 configuraciones para 10 ZOEs).

**Solucion:** `FederationDiscovery` en `zoe/core/federation_discovery.py`:
- Modo `manual` (default): comportamiento existente
- Modo `filesystem`: `peers.json` en SSD compartido
  - `announce()`: escribe URL + organism_id en peers.json
  - `discover()`: lee peers, filtra stale (>5min), skip self
  - `cleanup_stale()`: elimina peers antiguos
- Integrado en `EpistemicFederationServer` via `discovery_mode`

```python
server = EpistemicFederationServer(
    federation_manager=fed,
    discovery_mode="filesystem",
    peers_file="/ssd/zoe/peers.json",
)
server.discover_peers()  # Registra peers descubiertos automaticamente
```

---

## ZOE-SPEC-002: 8 items resueltos (4 experimentales + 4 endurecimiento)

### Experimentales

| # | Item | Problema | Solucion | Archivos |
|---|------|----------|----------|----------|
| 1 | **EmbodimentComposer CLI** | Llamada incorrecta a compose(), plan incompleto, broadcast_capacity no aplicado | Crea ResourcePlan con RAM detectada, usa embodiment.to_dict() completo, aplica broadcast_capacity al GlobalWorkspace | cli_chat.py |
| 2 | **SeedMode auto_start** | Event loop se cerraba, backend hardcodeado, no mantenia vivo | Loop con while True + sleep, detecta backend (ollama/zai/pattern), captura CancelledError | seed_mode.py |
| 3 | **Federation discovery** | Inicializado pero nunca invocado (codigo inerte) | start() llama announce()+discover(), refresh periodico cada 60s, registra peers automaticamente | epistemic_federation_server.py, cli_chat.py |
| 4 | **PostgreSQL tests** | 669 LOC sin tests, sin CI, factory no conectada | 28 tests unitarios con AsyncMock, CI job con postgres:16 service container, factory integrada en CLI opt-in | test_postgres_backend.py, ci.yml, cli_chat.py |

### Endurecimiento

| # | Item | Que se hizo | Tests |
|---|------|-------------|-------|
| 1 | **Federacion multi-instancia** | Dos ZOEs con peers.json compartido se descubren mutuamente, validan mejoras filogeneticas | test_federation_integration.py: 4 tests (discovery bidireccional, stale filtering, cleanup, pool compartido) |
| 2 | **PostgreSQL CI** | Job postgres-integration con service container postgres:16, health check pg_isready | ci.yml: job independiente con variables ZOE_POSTGRES_* |
| 3 | **Cobertura CI** | Verificado: --cov-fail-under=55, upload a Codecov | ci.yml: ya estaba configurado correctamente |
| 4 | **EmbodimentComposer por hardware** | Tests parametrizados: Mac 8GB sin/con Ollama, VPS 64GB, sin GPU | test_embodiment_hardware_profiles.py: 5 tests (perfiles + to_dict) |

### Bug extra corregido

**Lost update en DistributedPhylogeneticPool:** `record_test_result()` y `mark_incorporated()` no recargaban desde disco antes de modificar, causando que una ZOE sobrescribiera los cambios de otra. Añadido `self._load()` al inicio de ambos metodos.

---

## Sprint 5.12 — Dashboard utilizable + macOS SSD launchers

Sprint 5.12 resuelve **8 gaps criticos de usabilidad** que impedian que un usuario real pudiera usar el Dashboard en macOS con SSD. Todos los cambios son **backward-compatibles**: no rompen ninguna API existente, solo anaden funcionalidad y corrigen bugs.

### Que se resolvio

| # | Gap | Solucion | Tests anadidos |
|---|-----|----------|----------------|
| **A** | Dashboard HTML no manejaba el token de auth → 401 en todas las llamadas fetch | HTML sirve sin token en `/`; JS lee `?token=` o `localStorage`, sobreescribe `window.fetch` para inyectar `Authorization: Bearer`, y WebSocket usa `?token=` | 4 tests en `TestSprint512AuthRefinements` |
| **B** | `tests/test_web_dashboard.py` no podia importar `_get_dashboard_html` del shim | Re-exportada desde `zoe/web_dashboard.py` | 1 test |
| **C** | `INICIAR-DASHBOARD.command` tenia paths rotos para encontrar `venv/` | Logica robusta: busca `venv/` en `$SCRIPT_DIR`, `$SCRIPT_DIR/..`, `$SCRIPT_DIR/../..` | — |
| **D** | Lanzadores usaban `xargs` para cargar `.env`, rompiendo API keys con `=` `/` `+` | Cambio a `set -a; source .env; set +a` en todos los lanzadores | — |
| **E** | HTML del Dashboard decia "v1.7" (obsoleto) | Actualizado a "v2.1.2" | — |
| **F** | `install_ssd_crucial_x9_mac.sh` no creaba `INICIAR-DASHBOARD.command` ni `INICIAR-ZOE.command` universales | Crea los 3 lanzadores: `ZOE-Smart.command`, `INICIAR-ZOE.command`, `INICIAR-DASHBOARD.command` con deteccion automatica de backend | — |
| **G** | `zoe-bootstrap.sh` solo creaba 4 lanzadores (ZOE-Chat, ZOE-Chat-Ollama, ZOE-Dashboard, ZOE-Dashboard-Ollama) | Ahora crea 6 lanzadores en macOS y 6 en Linux (anade INICIAR-DASHBOARD e INICIAR-ZOE con deteccion automatica) | — |
| **H** | Rate limit middleware roto en aiohttp 3.13+ (class-based middleware deprecated) | Refactorizado a **middleware funcional** con `@web.middleware` (compatible con aiohttp 3.9-3.14+) | 69 tests de seguridad + 44 chaos engineering ahora pasan (antes fail) |

### Persistencia del token de auth

El `DashboardServer` ahora persiste su token a `data/dashboard_token.txt` (permisos 0600) en cada arranque. Los lanzadores `.command` leen este archivo y abren el navegador con `?token=XXX` embebido en la URL, **para que el usuario no tenga que copiar/pegar nada manualmente**.

### Tests Sprint 5.12

Nueva clase `TestSprint512AuthRefinements` en `zoe/tests/test_sprint5_9_security.py` con 8 tests:

- `test_index_path_is_public` — La ruta `/` es publica.
- `test_health_paths_still_public` — `/health`, `/ready`, `/live` siguen publicos.
- `test_data_endpoints_not_public` — `/stats`, `/memory`, `/chat`, `/ws`, `/api/capsules` requieren token.
- `test_dashboard_persists_auth_token_to_disk` — Token se persiste en `dashboard_token.txt`.
- `test_dashboard_html_has_token_handling` — HTML contiene `getZoeToken`, `saveAuthToken`, `authModal`.
- `test_dashboard_html_ws_uses_token_query` — WebSocket usa `?token=` en la URL.
- `test_dashboard_html_overrides_fetch` — HTML sobreescribe `window.fetch` para inyectar `Authorization: Bearer`.
- `test_web_dashboard_shim_reexports_get_html` — Shim re-exporta `_get_dashboard_html` para compatibilidad.

### Smoke test end-to-end

Script `smoke_test_dashboard.py` verifica end-to-end:

1. `GET /` sin token → 200 (HTML servido).
2. `GET /health` sin token → 200.
3. `GET /manifest.json` sin token → 200.
4. `GET /stats` sin token → 401.
5. `GET /stats` con `Authorization: Bearer` → 200.
6. `GET /stats?token=XXX` → 200 (para WebSocket).
7. `data/dashboard_token.txt` existe y contiene el token correcto.

**Resultado:** 6/6 tests pasan, 161 tests del subset relacionado pasan sin regresiones.

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
| ✅ | ZOE-SPEC-002 Gaps (3) | merge_subagents, reorganize_memory, serve.py V5 |
| ✅ | ZOE-SPEC-002 Mejoras (6) | SemanticSearch, cobertura tests, Phylo persistencia, Composer CLI, Seed auto-start, Federation discovery |
| ✅ | ZOE-SPEC-002 Experimentales (4) | EmbodimentComposer fix, SeedMode auto_start fix, Federation discovery activado, PostgreSQL tests |
| ✅ | ZOE-SPEC-002 Endurecimiento (4) | Tests federacion multi-instancia, PostgreSQL CI, cobertura CI, Tests EmbodimentComposer por hardware |
| ✅ | Sprint 5.12 (Julio 2026) | Dashboard utilizable (auth automática), launchers macOS universales, rate_limit refactor, manual 2,078 líneas |
| 🔄 | Pasarela de pagos | Stripe/PayPal para marketplace |
| 📋 | Chaos engineering avanzado | Load testing, fuzzing, penetración profesional |
| 📋 | v2.0.0 GA | Production Ready tras hardening final |

---

## Documentación

### Para todos
| Documento | Contenido |
|-----------|-----------|
| [`docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md`](zoe/docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md) | **Manual completo (2,078 líneas, 19 secciones)** — Instalación paso a paso en Mac+SSD, Dashboard explicado, 10 casos de uso prácticos, FAQ ampliada, glosario A-Z. Pensado para no técnicos. |
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
  <b>ZOE v2.1.2 — Synthetic Cognitive Organism</b><br>
  1,700+ tests · 210+ archivos Python · 15 cápsulas · 12 sub-agentes · 81 endpoints · 6 backends LLM · 4 idiomas<br>
  Docker · Kubernetes · SSD portátil · 100% offline · Dashboard web con auth automática<br>
  <i>"ZOE no es un modelo que responde. Es un organismo que existe."</i>
</p>
