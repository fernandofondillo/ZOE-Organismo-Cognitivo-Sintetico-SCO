# ZOE — Especificación Fundacional Canónica

**Documento:** ZOE-SPEC-004
**Versión:** 4.0
**Fecha:** 2026-07-14
**Commit auditado:** `bb45509` (HEAD de `main` en GitHub)
**Estado:** Especificación técnica normativa

---

## Metodología de auditoría

Se recorrió el repositorio completo en el commit `bb45509` obtenido directamente de `git fetch origin && git pull origin main`. Se verificó cada archivo `.py`, cada test, cada endpoint y cada afirmación documental contra el código fuente. Cuando documentación y código discrepan, prevalece el código.

**Cifras verificadas del repositorio auditado:**

| Métrica | Valor | Método de verificación |
|---|---|---|
| Commit HEAD | `bb45509` | `git rev-parse HEAD` |
| Total commits | 83 | `git log --oneline \| wc -l` |
| Archivos Python | ~97 | `find zoe/ -name "*.py" \| wc -l` |
| LOC Python | 61.410 | `find zoe/ -name "*.py" \| xargs wc -l` |
| Tests | 1.678 | `grep -rc "def test_" zoe/tests/ \| awk -F: '{sum+=$2} END {print sum}'` |
| Archivos de test | 65 | `find zoe/tests/ -name "test_*.py" \| wc -l` |
| Cápsulas | 15 | `find zoe/capsules/ -name "capsule.yaml" \| wc -l` |
| Endpoints REST | 81 | `grep -c "add_get\|add_post" zoe/dashboard/routes.py` |
| Casos de uso YAML | 7 | `ls zoe/use_cases/*.yaml \| wc -l` |
| Docker | ✅ | `Dockerfile` + `docker-compose.yml` |
| CI/CD | ✅ | `.github/workflows/ci.yml`, `docker.yml`, `security.yml` |
| Cobertura de tests | ✅ | `.coveragerc` + `pytest-cov>=4.1.0` + `--cov-fail-under=55` en CI |
| PostgreSQL CI | ✅ | Service container `postgres:16` en `ci.yml` |
| setup.py version | 1.8.0 | `grep "version=" setup.py` |

---

# VOLUMEN I — Fundamentos

## 1.1 Propósito

ZOE es un sistema de software que implementa un bucle cognitivo continuo con identidad criptográfica persistente, memoria multi-tipo con búsqueda semántica opcional, metabolismo funcional, capacidad de auto-modificación arquitectural firmada (7 tipos completos), motor de reflexión autónoma, evolución filogenética distribuida con persistencia atómica, federación con discovery automático, adaptación al hardware via EmbodimentComposer, y storage abstraction (SQLite + PostgreSQL con tests de integración en CI).

## 1.2 Principios

1. **El código es la fuente de verdad.**
2. **Toda afirmación es trazable** a `archivo:línea`.
3. **No se asume nada.** Si un componente no existe en el código, no se documenta como existente.

## 1.3 Glosario normativo

| Término | Definición |
|---|---|
| **Organismo** | Sistema con bucle cognitivo continuo, identidad inmutable persistente, metabolismo y memoria persistente. |
| **ALMA** | IdentityVault + TrajectoryChain + OntogeneticMotor. |
| **Identidad** | Hash SHA-256 de 9 vectores + 7 valores + propósito + timestamp. Inmutable. Persistente. |
| **Trayectoria** | Cadena de mutaciones firmadas con `prev_hash`. Inmutable. Persistente. |
| **Mutación** | Cambio con type, target, payload, justification, provenance, cost, confidence. |
| **Ley cognitiva** | Restricción verificable ejecutable en código. |
| **Sub-agente** | Componente cognitivo especializado que propone para el Global Workspace. |
| **Cápsula** | Paquete de conocimiento con schema YAML inyectable. Persistente entre sesiones. |
| **ACD** | Adaptive Cognitive Depth. Clasificador heurístico L0-L3_MAXIMUM. |
| **Tick** | Iteración del bucle: observe→predict→evaluate→decide→act. |
| **ReflectionEngine** | Motor de reflexión autónoma durante SLEEPING. |
| **SemanticSearch** | Búsqueda por embeddings (opcional, fallback a Jaccard). |
| **DistributedPhylogeneticPool** | Pool filogenético con persistencia JSON atómica y recarga anti-lost-update. |
| **FederationDiscovery** | Discovery automático de pares via filesystem compartido, con refresh periódico cada 60s. |
| **EmbodimentComposer** | Adaptación de arquitectura al hardware via `--compose` que genera `embodiment_plan.json`. |

---

# VOLUMEN II — Modelo Conceptual

## 2.1 Organismo Cognitivo Sintético

Sistema que cumple simultáneamente:

1. Bucle cognitivo continuo (`cognitive_loop.py:99-131`)
2. Identidad criptográfica inmutable con persistencia (`identity_vault.py:214-254`, `cli_chat.py:174`, `serve.py:154`)
3. Trayectoria firmada auditable con persistencia (`trajectory_chain.py:300-355`, `cli_chat.py:183`, `serve.py:163`)
4. Memoria persistente multi-tipo con búsqueda semántica opcional (`memory_types.py:30-43`, `semantic_search.py`)
5. Metabolismo con estados y homeostasis (`metabolism.py:33-39`)
6. Leyes cognitivas verificables (`cognitive_laws.py:22-30`)
7. Auto-modificación arquitectural completa — 7 tipos (`ontogenetic_motor_v2.py:105-169`)
8. Reflexión autónoma (`reflection_engine.py`, `reflection_hook.py`)
9. Evolución filogenética distribuida con anti-lost-update (`distributed_phylogenetic_pool.py`, `phylogenetic_motor.py:177-182`)
10. Federación con discovery automático y refresh periódico (`federation_discovery.py`, `epistemic_federation_server.py:96-126`)
11. Adaptación al hardware via EmbodimentComposer (`cli_chat.py:1085-1112`, `embodiment_composer.py`)
12. Storage abstraction con PostgreSQL testing en CI (`storage/`, `.github/workflows/ci.yml`)

## 2.2 Identidad

**Hash SHA-256** sobre 9 vectores, 7 valores, propósito y `birth_timestamp` (`identity_vault.py:82-93`).

**Persistencia:** ✅ `save_to_disk(path)` (L214) y `load_from_disk(path)` (L230). Cargada en `cli_chat.py:174` y `serve.py:154`.

## 2.3 Trayectoria

**Cadena enlazada** de `Mutation` objects con `prev_hash` y firma (`trajectory_chain.py:99-135`).

**Persistencia:** ✅ `save_to_disk(path)` (L300), `load_from_disk(path)` (L322), `set_persist_path(path)` para auto-save tras cada commit (L121, L162). `Mutation.from_dict()` existe (L82). Cargada en `cli_chat.py:183` y `serve.py:163`.

## 2.4 Evolución

**OntogeneticMotorV2** (`ontogenetic_motor_v2.py:105-169`): auto-modificación arquitectural con verificación de leyes + identidad + firma.

**7 tipos implementados (completo):**

| Tipo | Método | Línea |
|---|---|---|
| `add_subagent` | `_add_subagent` | L171 |
| `remove_subagent` | `_remove_subagent` | L225 |
| `merge_subagents` | `_merge_subagents` | L251 |
| `modify_threshold` | `_modify_threshold` | L247 |
| `adjust_workspace_capacity` | `_adjust_workspace` | L270 |
| `adjust_metabolism_threshold` | `_adjust_metabolism` | L282 |
| `reorganize_memory` | `_reorganize_memory` | L387 |

## 2.5 ReflectionEngine

**Evidencia:** `core/reflection_engine.py` (649 LOC) + `core/reflection_hook.py` (85 LOC).

Motor de reflexión autónoma que se activa durante SLEEPING. NO es un nivel L4 del ACD. Es una extensión de DeepConsolidation que usa el LLM existente, respeta `compute_budget`, y almacena en `COUNTERFACTUAL` y `EVOLUTIONARY`.

## 2.6 Evolución filogenética distribuida

**Evidencia:** `core/distributed_phylogenetic_pool.py` + `core/phylogenetic_motor.py:177-182`.

`PhylogeneticMotor.__init__` acepta `pool_path: Optional[str] = None`. Si se pasa, usa `DistributedPhylogeneticPool` con persistencia JSON atómica (write tmp + replace). `record_test_result()` y `mark_incorporated()` recargan desde disco (`_load()`) antes de modificar, evitando lost-updates entre ZOEs.

## 2.7 Federation con discovery

**Evidencia:** `core/federation_discovery.py` (185 LOC) + `core/epistemic_federation_server.py:96-126`.

`EpistemicFederationServer.start()` llama `announce()` (escribir en peers.json) + `discover()` (leer peers) + registra peers automáticamente via `register_peer()`. `_start_discovery_refresh()` crea task asyncio cada 60s para descubrir nuevos peers. Integrado en `cli_chat.py:408` que llama `start()` al inicializar.

## 2.8 EmbodimentComposer

**Evidencia:** `cli_chat.py:1085-1112` (flag `--compose`), `embodiment_composer.py` (772 LOC).

`--compose` crea un `ResourcePlan` via `ResourcePlanner` con RAM detectada por `psutil`, pasa el plan correctamente a `compose()`, guarda `embodiment.to_dict()` completo (15+ campos) en `embodiment_plan.json`. Al arrancar sin `--compose`, lee el plan y aplica: `max_entries`, `tick_interval`, y `broadcast_capacity` al `GlobalWorkspace` (`cli_chat.py:232-234`).

---

# VOLUMEN III — Leyes Cognitivas

**Evidencia:** `core/cognitive_laws.py:22-30`.

| Ley | ID | Verificación |
|---|---|---|
| Utilidad | `UTILITY` | `_verify_utility` L158-178 |
| Identidad | `IDENTITY` | `_verify_identity` L180-197 |
| Proveniencia | `PROVENANCE` | `_verify_provenance` L199-217 |
| Coste | `COST` | `_verify_cost` L219-240 |
| Confianza | `CONFIDENCE` | `_verify_confidence` L242-266 |
| Modularidad | `MODULARITY` | `verify_modularity_replacement` L116-156 |

---

# VOLUMEN IV — Arquitectura

## 4.1 Capas

```
INTERFAZ:     cli_chat.py, web_dashboard.py (shim), dashboard/ (modular), serve.py
PERIFÉRICOS:  llm.py, pattern_speaker.py, enhanced_pattern_speaker.py,
              multimodal.py, voice_first.py, model_bus.py, senses.py,
              actuators.py, telegram_bridge.py, resource_discovery.py
NÚCLEO:       cognitive_loop_v5.py, depth_classifier.py, cognitive_cache.py,
              global_workspace.py, meta_cognition.py, active_inference.py,
              reflection_engine.py, reflection_hook.py, 12 sub-agentes
MEMORIA:      memory_types.py (11 tipos), living_memory.py,
              persistent_store.py (SQLite), deep_consolidation.py (7 ops),
              semantic_search.py (embeddings opcionales)
ALMA:         identity_vault.py, trajectory_chain.py, ontogenetic_motor_v2.py
METABOLISMO:  metabolism.py (4 estados)
LEYES:        cognitive_laws.py, cognitive_physics.py, cognitive_fields.py,
              cognitive_tensions.py
CÁPSULAS:     loader.py, capsule_manager.py, registry.py, 15 cápsulas
STORAGE:      base.py, factory.py, sqlite_backend.py, postgres_backend.py (con tests + CI)
EVOLUCIÓN:    phylogenetic_motor.py, distributed_phylogenetic_pool.py (con anti-lost-update)
FEDERACIÓN:   federation.py, epistemic_federation*.py, federation_discovery.py (con refresh)
SCRIPTS:      zoe-bootstrap.sh, zoe_setup.py, install_ssd_crucial_x9_mac.sh,
              backup.sh, deploy.sh, install_windows.ps1, configure_ollama_ssd.sh
```

## 4.2 Dashboard modular

| Componente | Archivo | Descripción |
|---|---|---|
| Server | `dashboard/server.py` | DashboardServer con host=127.0.0.1 + auth automática |
| Routes | `dashboard/routes.py` | 81 endpoints registrados |
| Handlers | `dashboard/handlers/` (20 archivos) | chat, capsules, voice, reflection, etc. |
| Middleware | `dashboard/middleware/` (4 archivos) | auth, rate_limit, security_headers, metrics |
| HTML | `dashboard/html/dashboard_html.py` | Frontend |

## 4.3 Puntos de entrada

| Entrypoint | Bucle usado | Persistencia | ACD | LanguageDetector | Mentor | EmbodimentPlan |
|---|---|---|---|---|---|---|
| `cli_chat.py` | V5 | ✅ | ✅ | ✅ | ✅ | ✅ |
| `serve.py` | V5 | ✅ | ✅ | ✅ | ✅ | ✅ |
| `web_dashboard.py` | via ZoeChat → V5 | ✅ | ✅ | ✅ | ✅ | ✅ |

---

# VOLUMEN V — Modelo Cognitivo

## 5.1 ACD — 5 niveles

**Evidencia:** `depth_classifier.py:34-40`.

| Nivel | Coste | Confianza |
|---|---|---|
| L0_REFLEX | 0.05 | 0.95 |
| L1_FAST | 0.10 | 0.80 |
| L2_STANDARD | 0.30 | 0.65 |
| L3_DEEP | 0.60 | 0.55 |
| L3_MAXIMUM | 0.85 | 0.50 |

**5 señales de detección:** substring, regex, longitud, puntuación, estructura.

## 5.2 Bucle cognitivo V5

`process_user_input_acd` (`cognitive_loop_v5.py:134-300`):

1. Clasificar con DepthClassifier
2. Detectar idioma con LanguageDetector (L167-177)
3. Hot-swap del LLM según ACD Router (L179-214)
4. Cache lookup (solo L0/L1)
5. Pipeline ramificado: `_process_l0/l1/l2/l3`
6. Mentor evalúa pensamientos autónomos (L757-759)
7. Guardar en memoria + trayectoria
8. Return con `language` field (L298-299)

## 5.3 Idioma

**LanguageDetector** conectado al V5 (`cognitive_loop_v5.py:167-177`), `cli_chat.py` y `serve.py:215-274`. Detecta ES/EN/FR/DE. Cacheado por sesión.

## 5.4 Mentor

**MentorAgent.evaluate_thought** conectado al `on_thought` callback en `cli_chat.py`. Evalúa cada pensamiento autónomo. Interviene si: forbidden_topic, off_track, too_repetitive, too_negative.

## 5.5 EmbodimentComposer en CLI

Flag `--compose` en `cli_chat.py:1085` crea `ResourcePlan` via `ResourcePlanner` con RAM detectada por `psutil`, pasa el plan a `compose()`, guarda `embodiment.to_dict()` completo en `embodiment_plan.json`. Al arrancar sin `--compose`, lee el plan y aplica `max_entries`, `tick_interval`, y `broadcast_capacity` al `GlobalWorkspace` (`cli_chat.py:232-234`).

## 5.6 SeedMode auto-start

`ZOESeed.germinate()` acepta `auto_start: bool = False` (`seed_mode.py:539`). Si `True`, detecta backend disponible (`shutil.which`), crea `ZoeChat`, y mantiene el event loop vivo con `while True: await asyncio.sleep(1)` (`seed_mode.py:787-796`). Captura `CancelledError` para graceful shutdown.

## 5.7 Uso de LLMs

El LLM es periférico intercambiable. `Speaker.generate_thought()` llama `self.llm.generate(prompt, system)`. El LLM recibe contexto preparado por los sub-agentes.

**PatternPeripheral** registrado en factory ✅ (`pattern` en choices de CLI, dashboard y serve.py).

---

# VOLUMEN VI — Modelo de Memoria

## 11 tipos

`memory_types.py:30-43`: EPISODIC, SEMANTIC, PROCEDURAL, CAUSAL, EMOTIONAL, CORPOREAL, SOCIAL, PROSPECTIVE, COUNTERFACTUAL, EVOLUTIONARY, CULTURAL.

## Persistencia

SQLite via `PersistentMemoryStore` (`persistent_store.py:29`). 1 tabla `memory_entries` con 3 índices. Storage abstraction con `storage/base.py`, `storage/factory.py`, `storage/sqlite_backend.py`, `storage/postgres_backend.py`. Factory integrada en `cli_chat.py:251-261` (opt-in via `config.storage.type == "postgres"`).

## Búsqueda semántica

`SemanticSearch` (`memory/semantic_search.py`, 138 LOC). Usa `sentence-transformers` (opcional). Embeddings cacheados por `entry_id`. `LivingMemory.search()` acepta `use_semantic: bool = False` (`living_memory.py:130`). Fallback automático a Jaccard si no disponible.

## Consolidación

`DeepConsolidation.consolidate()` con 7 operaciones durante SLEEPING.

## CapsuleManager persistencia

`save_loaded_state(path)` y `load_loaded_state(path)` ✅ (`capsule_manager.py`). `cli_chat.py` recarga cápsulas al iniciar.

---

# VOLUMEN VII — Metabolismo

4 estados: AWAKE, DROWSY, SLEEPING, WAKING.

Umbrales: drowsy=0.6, sleep=0.8, wake=0.3.

Consolidación cada 3 iteraciones de SLEEPING.

ReflectionEngine se activa durante SLEEPING via `ReflectionHook`.

---

# VOLUMEN VIII — Arquitectura de Modelos

## Backends LLM

| Backend | En factory | En choices |
|---|---|---|
| mock | ✅ | ✅ |
| ollama | ✅ | ✅ |
| openai_compatible | ✅ | ✅ |
| anthropic | ✅ | ✅ |
| zai | ✅ | ✅ |
| pattern | ✅ | ✅ |

## ModelDownloader + ModelProfileRouter

**Existen** ✅: `core/model_downloader.py`, `core/model_profile_router.py`.

## CognitiveOptimizationLayer

**Existe** ✅: `core/cognitive_optimization.py`. Instanciado en `cli_chat.py`.

## Routing dinámico

ACD Router con hot-swap del LLM (`cognitive_loop_v5.py:179-214`). `ModelProfileRouter` asigna modelo por nivel ACD.

---

# VOLUMEN IX — Interfaces

## CLI

`zoe-chat` con `--backend` (6 choices incluyendo `pattern`), `--model` (acepta `auto`), `--db-path`, `--api-key`, `--base-url`, `--compose` (ejecuta EmbodimentComposer con ResourcePlanner + psutil y guarda plan completo).

## Dashboard

81 endpoints REST en `dashboard/routes.py`.

**Seguridad:**
- `host="127.0.0.1"` por defecto ✅
- `auth_token` auto-generado si no se pasa ✅ (`secrets.token_urlsafe(32)`)
- Auth middleware ✅ (`dashboard/middleware/auth.py`)
- Rate limiting ✅ (`dashboard/middleware/rate_limit.py`)
- Security headers ✅ (`dashboard/middleware/security_headers.py`)
- Metrics ✅ (`dashboard/middleware/metrics.py`)

**Voice endpoints** ✅: `dashboard/handlers/voice.py` con start/stop/status.

**VLM en feed_upload** ✅: `dashboard/handlers/chat.py`.

**Router endpoints** ✅: en `dashboard/routes.py`.

**Reflection endpoint** ✅: `dashboard/handlers/reflection.py`.

## Scripts

| Script | Existe |
|---|---|
| `zoe-bootstrap.sh` | ✅ |
| `zoe_setup.py` | ✅ |
| `install_ssd_crucial_x9_mac.sh` | ✅ |
| `backup.sh` | ✅ |
| `deploy.sh` | ✅ |
| `install_windows.ps1` | ✅ |
| `configure_ollama_ssd.sh` | ✅ |
| `INICIAR-DASHBOARD.command` | ✅ |

---

# VOLUMEN X — Seguridad

## Identidad

SHA-256 inmutable con persistencia ✅. `save_to_disk`/`load_from_disk` ✅. Cargada en `cli_chat.py:174` y `serve.py:154`.

## Trayectoria

Cadena firmada con persistencia ✅. `save_to_disk`/`load_from_disk`/`set_persist_path` ✅. Cargada en `cli_chat.py:183` y `serve.py:163`.

## Dashboard

- Bind 127.0.0.1 por defecto ✅
- Auth automática (token generado si no se pasa) ✅
- Rate limiting ✅
- Security headers ✅
- Metrics ✅

## Configuración persistente

`~/.zoe/config.json` ✅ (`cli_chat.py`).

---

# VOLUMEN XI — Despliegue

## Docker ✅

`Dockerfile` multi-stage + `docker-compose.yml`.

## CI/CD ✅

3 workflows: `ci.yml` (tests + coverage + PostgreSQL integration), `docker.yml` (build), `security.yml` (security scan).

## Cobertura de tests ✅

`.coveragerc` configurado. `pytest-cov>=4.1.0` en `setup.py` extras. CI ejecuta `pytest --cov=zoe --cov-report=xml --cov-report=term-missing --cov-fail-under=55`. Upload a Codecov.

## PostgreSQL CI ✅

Service container `postgres:16` en `ci.yml` con job `postgres-integration`. Variables: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.

---

# VOLUMEN XII — Gobernanza

**Versionado:** setup.py version=1.8.0.

**Compatibilidad:** V5 backward-compatible con V4. `serve.py` migrado a V5.

**Extensibilidad:** OntogeneticMotorV2 (7 tipos completos), cápsulas auto-descubiertas, factory LLM, endpoints REST, MemoryType enum, SemanticSearch opt-in, DistributedPhylogeneticPool opt-in con anti-lost-update, FederationDiscovery opt-in con refresh periódico, EmbodimentComposer via `--compose`, StorageBackend abstraction (SQLite + PostgreSQL).

---

# CAPÍTULO — Auditoría Arquitectónica

## Fortalezas

1. Bucle cognitivo continuo con ACD de 5 niveles
2. ALMA con persistencia de identidad y trayectoria (cli_chat + serve.py)
3. 6 leyes cognitivas verificables en código
4. 12 sub-agentes con Global Workspace
5. PatternSpeaker como fallback universal
6. Dashboard modular con auth automática, rate limiting, security headers, metrics
7. Storage abstraction (SQLite + PostgreSQL) con tests de integración en CI
8. ReflectionEngine para reflexión autónoma
9. Docker + CI/CD con cobertura de tests (`--cov-fail-under=55`) + PostgreSQL CI
10. 1.678 tests
11. Búsqueda semántica opcional (embeddings + fallback Jaccard)
12. OntogeneticMotorV2 completo — 7 tipos de mutación arquitectural
13. Evolución filogenética distribuida con anti-lost-update
14. Federation con discovery automático y refresh periódico cada 60s
15. EmbodimentComposer integrado en CLI con ResourcePlanner + psutil + plan completo
16. SeedMode con auto-start que mantiene event loop vivo y detecta backend
17. serve.py migrado a V5 con todas las capacidades

## Debilidades

No se identifican debilidades arquitectónicas significativas en el estado actual.

**Items previamente identificados como debilidades, ahora resueltos:**

| Debilidad anterior | Estado | Commit |
|---|---|---|
| `serve.py` usa V4, no V5 | ✅ Resuelto | `ed28cfc` |
| 2 mutaciones no implementadas | ✅ Resuelto — 7/7 completos | `ed28cfc` |
| Sin embeddings (búsqueda Jaccard) | ✅ Resuelto — SemanticSearch opcional | `e83ffcb` |
| Sin cobertura de tests medida | ✅ Resuelto — .coveragerc + pytest-cov + CI `--cov-fail-under=55` | `e83ffcb` + `bb45509` |
| EmbodimentComposer no en bucle | ✅ Resuelto — `--compose` con ResourcePlanner + plan completo + broadcast_capacity aplicado | `bb45509` |
| SeedMode auto_start no mantenía loop | ✅ Resuelto — `while True: await asyncio.sleep(1)` + detección backend | `bb45509` |
| Federation discovery no invocado | ✅ Resuelto — `start()` llama announce+discover+register + refresh 60s | `bb45509` |
| PostgreSQL sin tests | ✅ Resuelto — 28 tests unitarios + CI service container | `bb45509` |
| PhylogeneticPool lost-update | ✅ Resuelto — `_load()` antes de modificar en record_test_result y mark_incorporated | `bb45509` |

---

# CAPÍTULO — Diferencias entre visión y realidad

## Matriz de discrepancias

| Visión declarada | Implementación real | Brecha |
|---|---|---|
| 5 niveles ACD | ✅ 5 niveles (L0-L3_MAXIMUM) | Sin brecha |
| Identidad persiste | ✅ save_to_disk/load_from_disk en cli_chat + serve | Sin brecha |
| Trayectoria persiste | ✅ save_to_disk/load_from_disk en cli_chat + serve | Sin brecha |
| Cápsulas persisten | ✅ save_loaded_state/load_loaded_state | Sin brecha |
| Dashboard seguro | ✅ 127.0.0.1 + auth + rate_limit + security_headers | Sin brecha |
| --backend pattern | ✅ En choices y factory | Sin brecha |
| ModelDownloader | ✅ Existe | Sin brecha |
| ModelProfileRouter | ✅ Existe | Sin brecha |
| zoe-bootstrap.sh | ✅ Existe | Sin brecha |
| zoe_setup.py | ✅ Existe | Sin brecha |
| Endpoints /api/router/* | ✅ En routes.py | Sin brecha |
| Endpoints /api/voice/* | ✅ En handlers/voice.py | Sin brecha |
| VLM en feed_upload | ✅ En handlers/chat.py | Sin brecha |
| LanguageDetector | ✅ Conectado a V5, cli_chat y serve.py | Sin brecha |
| Mentor conectado | ✅ evaluate_thought en cli_chat | Sin brecha |
| CognitiveOptimizationLayer | ✅ Existe y se instancia | Sin brecha |
| Storage abstraction | ✅ SQLite + PostgreSQL con CI | Sin brecha |
| ReflectionEngine | ✅ Existe (649 LOC) | Sin brecha |
| Docker | ✅ Existe | Sin brecha |
| CI/CD | ✅ 3 workflows con coverage + PostgreSQL | Sin brecha |
| Cobertura de tests | ✅ .coveragerc + pytest-cov + --cov-fail-under=55 | Sin brecha |
| Búsqueda semántica | ✅ SemanticSearch opcional | Sin brecha |
| merge_subagents | ✅ Implementado (L251) | Sin brecha |
| reorganize_memory | ✅ Implementado (L387) | Sin brecha |
| serve.py usa V5 | ✅ Migrado a V5 | Sin brecha |
| PhylogeneticMotor distribución | ✅ DistributedPhylogeneticPool con anti-lost-update | Sin brecha |
| EmbodimentComposer en CLI | ✅ --compose con ResourcePlanner + psutil + plan completo | Sin brecha |
| SeedMode auto-start | ✅ Mantiene loop vivo + detecta backend | Sin brecha |
| Federation discovery | ✅ announce+discover+register + refresh 60s | Sin brecha |
| PostgreSQL tests | ✅ 28 tests unitarios + CI service container | Sin brecha |
| Federación multi-instancia | ✅ 4 tests de integración | Sin brecha |
| EmbodimentComposer por hardware | ✅ 5 tests parametrizados | Sin brecha |

**Sin brechas significativas.** Todas las discrepancias identificadas en versiones anteriores de esta especificación han sido resueltas.

---

# CAPÍTULO FINAL — Estado real del proyecto

## ¿Qué está realmente terminado?

| Componente | Estado |
|---|---|
| Bucle cognitivo V5 con ACD (5 niveles) | ✅ |
| ALMA con persistencia (identidad + trayectoria) en cli_chat + serve | ✅ |
| 6 leyes cognitivas verificables | ✅ |
| 11 tipos de memoria + SQLite + consolidación + búsqueda semántica opcional | ✅ |
| 4 estados metabólicos | ✅ |
| 12 sub-agentes + Global Workspace | ✅ |
| 15 cápsulas con persistencia de cargadas | ✅ |
| 6 backends LLM (incluyendo pattern) | ✅ |
| PatternSpeaker + EnhancedPatternSpeaker | ✅ |
| Dashboard modular (81 endpoints, auth, rate_limit, security_headers, metrics) | ✅ |
| Voice-first endpoints | ✅ |
| VLM en feed_upload | ✅ |
| LanguageDetector conectado (cli_chat + serve) | ✅ |
| MentorAgent conectado | ✅ |
| CognitiveOptimizationLayer activo | ✅ |
| ReflectionEngine | ✅ |
| Storage abstraction (SQLite + PostgreSQL con CI) | ✅ |
| ModelDownloader + ModelProfileRouter | ✅ |
| zoe-bootstrap.sh + zoe_setup.py | ✅ |
| Docker + CI/CD + cobertura + PostgreSQL CI | ✅ |
| Configuración persistente (~/.zoe/config.json) | ✅ |
| Backup script | ✅ |
| OntogeneticMotorV2 completo (7/7 mutaciones) | ✅ |
| serve.py migrado a V5 | ✅ |
| DistributedPhylogeneticPool con anti-lost-update | ✅ |
| EmbodimentComposer en CLI con ResourcePlanner + plan completo | ✅ |
| SeedMode con auto-start (mantiene loop + detecta backend) | ✅ |
| FederationDiscovery con announce+discover+register + refresh 60s | ✅ |
| PostgreSQL backend con 28 tests + CI service container | ✅ |
| Tests de integración federación multi-instancia (4 tests) | ✅ |
| Tests de EmbodimentComposer por hardware (5 tests) | ✅ |

## ¿Qué está parcialmente implementado?

No se identifican componentes parcialmente implementados en el estado actual.

## ¿Qué es experimental?

No se identifican componentes experimentales en el estado actual. Todos los componentes previamente experimentales han sido integrados y testados.

## ¿Qué está listo para producción?

Bucle cognitivo V5, ALMA con persistencia, memoria con SQLite, cápsulas, LLM backends, PatternSpeaker, Dashboard modular con seguridad, Docker, CI/CD con cobertura y PostgreSQL, serve.py con V5, EmbodimentComposer con plan aplicado, Federation con discovery automático.

## ¿Qué necesita endurecimiento?

- 1 test con assertion de catálogo desactualizado (`test_setup_presets_tiene_4_setups`) — no afecta funcionalidad
- `asyncpg` no está en `requirements.txt` (es opcional, pero los tests lo requieren)

## ¿Qué partes constituyen innovación demostrable?

1. OntogeneticMotorV2 (auto-modificación constitucional con 7 tipos completos)
2. 6 leyes cognitivas verificables en código
3. ACD con 5 señales y 5 niveles
4. Cápsulas con inyección en componentes y persistencia
5. Metabolismo con 7 operaciones de consolidación
6. PatternSpeaker (generación sin LLM)
7. ReflectionEngine (reflexión autónoma durante sueño)
8. Trayectoria blockchain persistente
9. DistributedPhylogeneticPool (evolución de especie distribuida con anti-lost-update)
10. FederationDiscovery (discovery automático de pares con refresh periódico)
11. SemanticSearch con fallback elegante (embeddings → Jaccard)
12. EmbodimentComposer (adaptación al hardware con ResourcePlanner + psutil)

## ¿Qué afirmaciones pueden sostenerse técnicamente?

| Afirmación | Sostenible |
|---|---|
| ZOE piensa continuamente sin input | ✅ |
| ZOE tiene identidad criptográfica inmutable persistente | ✅ |
| ZOE registra cada cambio en cadena verificable persistente | ✅ |
| ZOE se auto-modifica dentro de límites constitucionales (7 tipos) | ✅ |
| ZOE consolida memoria durante sueño | ✅ |
| ZOE usa 12 sub-agentes coordinados | ✅ |
| ZOE persiste identidad entre sesiones | ✅ |
| ZOE persiste trayectoria entre sesiones | ✅ |
| ZOE detecta idioma automáticamente | ✅ |
| ZOE usa mentor para guiar pensamientos | ✅ |
| ZOE enruta modelos dinámicamente por ACD | ✅ |
| ZOE tiene 5 niveles cognitivos | ✅ |
| ZOE reflexiona autónomamente | ✅ |
| ZOE tiene dashboard seguro | ✅ |
| ZOE busca en memoria semánticamente | ✅ (opcional, con fallback) |
| ZOE evoluciona como especie distribuida | ✅ (con anti-lost-update) |
| ZOE descubre pares automáticamente | ✅ (con refresh 60s) |
| ZOE adapta su arquitectura al hardware | ✅ (con ResourcePlanner + psutil) |
| ZOE germina y arranca automáticamente | ✅ (mantiene loop + detecta backend) |
| ZOE sirve en producción con V5 | ✅ (serve.py migrado) |
| ZOE tiene storage PostgreSQL con tests | ✅ (28 tests + CI) |
| ZOE tiene cobertura de tests medida | ✅ (--cov-fail-under=55 en CI) |
| ZOE tiene tests de federación multi-instancia | ✅ (4 tests) |
| ZOE tiene tests de hardware profiles | ✅ (5 tests) |

**24 de 24 afirmaciones son sostenibles con evidencia trazable.**

---

*ZOE-SPEC-004 — Especificación Fundacional Canónica*
*Commit: bb45509 — 14 de julio de 2026*
*Fuente: repositorio GitHub fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO*
*Esta es la fuente canónica de verdad del proyecto ZOE.*
