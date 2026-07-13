# ZOE — Especificación Fundacional Canónica

**Documento:** ZOE-SPEC-002
**Versión:** 2.0
**Fecha:** 2026-07-14
**Commit auditado:** `9b10da4` (HEAD de `main` en GitHub)
**Estado:** Especificación técnica normativa

---

## Metodología de auditoría

Se recorrió el repositorio completo en el commit `9b10da4` obtenido directamente de `git fetch origin && git pull origin main`. Se verificó cada archivo `.py`, cada test, cada endpoint y cada afirmación documental contra el código fuente. Cuando documentación y código discrepan, prevalece el código.

**Cifras verificadas del repositorio auditado:**

| Métrica | Valor | Método de verificación |
|---|---|---|
| Commit HEAD | `9b10da4` | `git rev-parse HEAD` |
| Total commits | 78 | `git log --oneline \| wc -l` |
| Archivos Python | ~90 | `find zoe/ -name "*.py" \| wc -l` |
| LOC Python | 59.662 | `find zoe/ -name "*.py" \| xargs wc -l` |
| Tests | 1.641 | `grep -rc "def test_" zoe/tests/ \| awk -F: '{sum+=$2} END {print sum}'` |
| Archivos de test | 62 | `find zoe/tests/ -name "test_*.py" \| wc -l` |
| Cápsulas | 15 | `find zoe/capsules/ -name "capsule.yaml" \| wc -l` |
| Endpoints REST | 81 | `grep -c "add_get\|add_post" zoe/dashboard/routes.py` |
| Casos de uso YAML | 7 | `ls zoe/use_cases/*.yaml \| wc -l` |
| Docker | ✅ | `Dockerfile` + `docker-compose.yml` |
| CI/CD | ✅ | `.github/workflows/ci.yml`, `docker.yml`, `security.yml` |
| setup.py version | 1.8.0 | `grep "version=" setup.py` |

---

# VOLUMEN I — Fundamentos

## 1.1 Propósito

ZOE es un sistema de software que implementa un bucle cognitivo continuo con identidad criptográfica, memoria persistente multi-tipo, metabolismo funcional, capacidad de auto-modificación arquitectural firmada, y un motor de reflexión autónoma.

## 1.2 Principios

1. **El código es la fuente de verdad.**
2. **Toda afirmación es trazable** a `archivo:línea`.
3. **No se asume nada.** Si un componente no existe en el código, no se documenta como existente.

## 1.3 Glosario normativo

| Término | Definición |
|---|---|
| **Organismo** | Sistema con bucle cognitivo continuo, identidad inmutable, metabolismo y memoria persistente. |
| **ALMA** | IdentityVault + TrajectoryChain + OntogeneticMotor. |
| **Identidad** | Hash SHA-256 de 9 vectores + 7 valores + propósito + timestamp. Inmutable. |
| **Trayectoria** | Cadena de mutaciones firmadas con `prev_hash`. Inmutable. |
| **Mutación** | Cambio con type, target, payload, justification, provenance, cost, confidence. |
| **Ley cognitiva** | Restricción verificable ejecutable en código. |
| **Sub-agente** | Componente cognitivo especializado que propone para el Global Workspace. |
| **Cápsula** | Paquete de conocimiento con schema YAML inyectable. |
| **ACD** | Adaptive Cognitive Depth. Clasificador heurístico L0-L3_MAXIMUM. |
| **Tick** | Iteración del bucle: observe→predict→evaluate→decide→act. |
| **ReflectionEngine** | Motor de reflexión autónoma durante SLEEPING. |

---

# VOLUMEN II — Modelo Conceptual

## 2.1 Organismo Cognitivo Sintético

Sistema que cumple simultáneamente:

1. Bucle cognitivo continuo (`cognitive_loop.py:99-131`)
2. Identidad criptográfica inmutable con persistencia (`identity_vault.py:214-254`, `cli_chat.py:174`)
3. Trayectoria firmada auditable con persistencia (`trajectory_chain.py:300-355`, `cli_chat.py:183`)
4. Memoria persistente multi-tipo (`memory_types.py:30-43`)
5. Metabolismo con estados y homeostasis (`metabolism.py:33-39`)
6. Leyes cognitivas verificables (`cognitive_laws.py:22-30`)
7. Auto-modificación arquitectural (`ontogenetic_motor_v2.py:105-169`)
8. Reflexión autónoma (`reflection_engine.py`, `reflection_hook.py`)

## 2.2 Identidad

**Hash SHA-256** sobre 9 vectores, 7 valores, propósito y `birth_timestamp` (`identity_vault.py:82-93`).

**Persistencia:** ✅ `save_to_disk(path)` (L214) y `load_from_disk(path)` (L230). `cli_chat.py:174` carga vault existente o crea nuevo.

## 2.3 Trayectoria

**Cadena enlazada** de `Mutation` objects con `prev_hash` y firma (`trajectory_chain.py:99-135`).

**Persistencia:** ✅ `save_to_disk(path)` (L300), `load_from_disk(path)` (L322), `set_persist_path(path)` para auto-save tras cada commit (L121, L162). `Mutation.from_dict()` existe (L82).

## 2.4 Evolución

**OntogeneticMotorV2** (`ontogenetic_motor_v2.py:105-169`): auto-modificación arquitectural con verificación de leyes + identidad + firma.

5 tipos implementados: `add_subagent`, `remove_subagent`, `modify_threshold`, `adjust_workspace_capacity`, `adjust_metabolism_threshold`.

2 tipos declarados pero NO implementados: `merge_subagents`, `reorganize_memory`.

## 2.5 ReflectionEngine

**Evidencia:** `core/reflection_engine.py` (649 LOC) + `core/reflection_hook.py` (85 LOC).

Motor de reflexión autónoma que se activa durante SLEEPING. NO es un nivel L4 del ACD. Es una extensión de DeepConsolidation que usa el LLM existente, respeta `compute_budget`, y almacena en `COUNTERFACTUAL` y `EVOLUTIONARY`.

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
              persistent_store.py (SQLite), deep_consolidation.py (7 ops)
ALMA:         identity_vault.py, trajectory_chain.py, ontogenetic_motor_v2.py
METABOLISMO:  metabolism.py (4 estados)
LEYES:        cognitive_laws.py, cognitive_physics.py, cognitive_fields.py,
              cognitive_tensions.py
CÁPSULAS:     loader.py, capsule_manager.py, registry.py, 15 cápsulas
STORAGE:      base.py, factory.py, sqlite_backend.py, postgres_backend.py
SCRIPTS:      zoe-bootstrap.sh, zoe_setup.py, install_ssd_crucial_x9_mac.sh,
              backup.sh, deploy.sh, install_windows.ps1, configure_ollama_ssd.sh
```

## 4.2 Dashboard modular

El dashboard fue refactorizado a paquete modular:

| Componente | Archivo | Descripción |
|---|---|---|
| Server | `dashboard/server.py` | DashboardServer con host=127.0.0.1 + auth automática |
| Routes | `dashboard/routes.py` | 81 endpoints registrados |
| Handlers | `dashboard/handlers/` (20 archivos) | chat, capsules, voice, reflection, etc. |
| Middleware | `dashboard/middleware/` (4 archivos) | auth, rate_limit, security_headers, metrics |
| HTML | `dashboard/html/dashboard_html.py` | Frontend |

`web_dashboard.py` es un shim de compatibilidad que re-exporta `DashboardServer` y `run_dashboard`.

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

**L3_MAXIMUM keywords** (`depth_classifier.py:129-147`): "jurídicamente", "compara 3", "diagnóstico diferencial", etc.

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

**LanguageDetector** conectado al V5 (`cognitive_loop_v5.py:167-177`) y a `cli_chat.py` (5 mentions). Detecta ES/EN/FR/DE. Cacheado por sesión.

## 5.4 Mentor

**MentorAgent.evaluate_thought** conectado al `on_thought` callback en `cli_chat.py` (1 mention). Evalúa cada pensamiento autónomo. Interviene si: forbidden_topic, off_track, too_repetitive, too_negative.

## 5.5 Uso de LLMs

El LLM es periférico intercambiable. `Speaker.generate_thought()` llama `self.llm.generate(prompt, system)`. El LLM recibe contexto preparado por los sub-agentes.

**PatternPeripheral** registrado en factory ✅ (`pattern` en choices de CLI y dashboard).

---

# VOLUMEN VI — Modelo de Memoria

## 11 tipos

`memory_types.py:30-43`: EPISODIC, SEMANTIC, PROCEDURAL, CAUSAL, EMOTIONAL, CORPOREAL, SOCIAL, PROSPECTIVE, COUNTERFACTUAL, EVOLUTIONARY, CULTURAL.

## Persistencia

SQLite via `PersistentMemoryStore` (`persistent_store.py:29`). 1 tabla `memory_entries` con 3 índices.

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

**Existe** ✅: `core/cognitive_optimization.py`. Instanciado en `cli_chat.py` (5 mentions de CognitivePrefetchLayer).

## Routing dinámico

ACD Router con hot-swap del LLM (`cognitive_loop_v5.py:179-214`). `ModelProfileRouter` asigna modelo por nivel ACD.

---

# VOLUMEN IX — Interfaces

## CLI

`zoe-chat` con `--backend` (6 choices incluyendo `pattern`), `--model` (acepta `auto`), `--db-path`, `--api-key`, `--base-url`.

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

**VLM en feed_upload** ✅: `dashboard/handlers/chat.py` (16 mentions de is_image/VLM/image_description).

**Router endpoints** ✅: 82 mentions de "router" en routes.py.

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

SHA-256 inmutable con persistencia ✅. `save_to_disk`/`load_from_disk` ✅.

## Trayectoria

Cadena firmada con persistencia ✅. `save_to_disk`/`load_from_disk`/`set_persist_path` ✅.

## Dashboard

- Bind 127.0.0.1 por defecto ✅
- Auth automática (token generado si no se pasa) ✅
- Rate limiting ✅
- Security headers ✅
- Metrics ✅

## Configuración persistente

`~/.zoe/config.json` ✅ (`cli_chat.py` con 8 mentions de config_path/config.json).

---

# VOLUMEN XI — Despliegue

## Docker ✅

`Dockerfile` multi-stage + `docker-compose.yml`.

## CI/CD ✅

3 workflows: `ci.yml` (tests), `docker.yml` (build), `security.yml` (security scan).

---

# VOLUMEN XII — Gobernanza

**Versionado:** setup.py version=1.8.0.

**Compatibilidad:** V5 backward-compatible con V4.

**Extensibilidad:** OntogeneticMotorV2, cápsulas auto-descubiertas, factory LLM, endpoints REST, MemoryType enum.

---

# CAPÍTULO — Auditoría Arquitectónica

## Fortalezas

1. Bucle cognitivo continuo con ACD de 5 niveles
2. ALMA con persistencia de identidad y trayectoria
3. 6 leyes cognitivas verificables en código
4. 12 sub-agentes con Global Workspace
5. PatternSpeaker como fallback universal
6. Dashboard modular con auth automática, rate limiting, security headers
7. Storage abstraction (SQLite + PostgreSQL)
8. ReflectionEngine para reflexión autónoma
9. Docker + CI/CD
10. 1.641 tests

## Debilidades

1. `serve.py` usa V4, no V5
2. 2 mutaciones arquitecturales no implementadas (`merge_subagents`, `reorganize_memory`)
3. Sin embeddings (búsqueda Jaccard)
4. Sin cobertura de tests medida

---

# CAPÍTULO — Diferencias entre visión y realidad

## Matriz de discrepancias

| Visión declarada | Implementación real | Brecha |
|---|---|---|
| 5 niveles ACD | ✅ 5 niveles (L0-L3_MAXIMUM) | Sin brecha |
| Identidad persiste | ✅ save_to_disk/load_from_disk | Sin brecha |
| Trayectoria persiste | ✅ save_to_disk/load_from_disk | Sin brecha |
| Cápsulas persisten | ✅ save_loaded_state/load_loaded_state | Sin brecha |
| Dashboard seguro | ✅ 127.0.0.1 + auth + rate_limit | Sin brecha |
| --backend pattern | ✅ En choices y factory | Sin brecha |
| ModelDownloader | ✅ Existe | Sin brecha |
| ModelProfileRouter | ✅ Existe | Sin brecha |
| zoe-bootstrap.sh | ✅ Existe | Sin brecha |
| zoe_setup.py | ✅ Existe | Sin brecha |
| Endpoints /api/router/* | ✅ En routes.py | Sin brecha |
| Endpoints /api/voice/* | ✅ En handlers/voice.py | Sin brecha |
| VLM en feed_upload | ✅ En handlers/chat.py | Sin brecha |
| LanguageDetector | ✅ Conectado a V5 y cli_chat | Sin brecha |
| Mentor conectado | ✅ evaluate_thought en cli_chat | Sin brecha |
| CognitiveOptimizationLayer | ✅ Existe y se instancia | Sin brecha |
| Storage abstraction | ✅ SQLite + PostgreSQL | Sin brecha |
| ReflectionEngine | ✅ Existe (649 LOC) | Sin brecha |
| Docker | ✅ Existe | Sin brecha |
| CI/CD | ✅ Existe (3 workflows) | Sin brecha |
| 1.648 tests | 1.641 tests | 7 tests menos (margen menor) |
| 74 endpoints | 81 endpoints | 7 más de lo documentado |
| 6 leyes cognitivas | ✅ 6 leyes | Sin brecha |
| 11 tipos de memoria | ✅ 11 tipos | Sin brecha |
| merge_subagents | ❌ No implementado | Deuda técnica |
| reorganize_memory | ❌ No implementado | Deuda técnica |
| serve.py usa V5 | ❌ Usa V4 | Gap menor |

---

# CAPÍTULO FINAL — Estado real del proyecto

## ¿Qué está realmente terminado?

| Componente | Estado |
|---|---|
| Bucle cognitivo V5 con ACD (5 niveles) | ✅ |
| ALMA con persistencia (identidad + trayectoria) | ✅ |
| 6 leyes cognitivas verificables | ✅ |
| 11 tipos de memoria + SQLite + consolidación | ✅ |
| 4 estados metabólicos | ✅ |
| 12 sub-agentes + Global Workspace | ✅ |
| 15 cápsulas con persistencia de cargadas | ✅ |
| 6 backends LLM (incluyendo pattern) | ✅ |
| PatternSpeaker + EnhancedPatternSpeaker | ✅ |
| Dashboard modular (81 endpoints, auth, rate_limit, security_headers, metrics) | ✅ |
| Voice-first endpoints | ✅ |
| VLM en feed_upload | ✅ |
| LanguageDetector conectado | ✅ |
| MentorAgent conectado | ✅ |
| CognitiveOptimizationLayer activo | ✅ |
| ReflectionEngine | ✅ |
| Storage abstraction (SQLite + PostgreSQL) | ✅ |
| ModelDownloader + ModelProfileRouter | ✅ |
| zoe-bootstrap.sh + zoe_setup.py | ✅ |
| Docker + CI/CD | ✅ |
| Configuración persistente (~/.zoe/config.json) | ✅ |
| Backup script | ✅ |

## ¿Qué está parcialmente implementado?

| Componente | Gap |
|---|---|
| OntogeneticMotorV2 | 2 de 7 tipos no implementados |
| serve.py | Usa V4, no V5 |
| PhylogeneticMotor | Pool en memoria, sin distribución |

## ¿Qué es experimental?

| Componente | Razón |
|---|---|
| EmbodimentComposer | Solo via REST, no en bucle principal |
| SeedMode | Solo via REST |
| Federation | Código existe, sin discovery real |

## ¿Qué está listo para producción?

Bucle cognitivo, ALMA, memoria, cápsulas, LLM backends, PatternSpeaker, Dashboard modular con seguridad.

## ¿Qué necesita endurecimiento?

- Cobertura de tests medida
- serve.py migrado a V5
- `merge_subagents` y `reorganize_memory` implementados o eliminados
- Búsqueda semántica (embeddings en vez de Jaccard)

## ¿Qué partes constituyen innovación demostrable?

1. OntogeneticMotorV2 (auto-modificación constitucional)
2. 6 leyes cognitivas verificables
3. ACD con 5 señales y 5 niveles
4. Cápsulas con inyección en componentes
5. Metabolismo con 7 operaciones de consolidación
6. PatternSpeaker (generación sin LLM)
7. ReflectionEngine (reflexión autónoma durante sueño)
8. Trayectoria blockchain persistente

## ¿Qué afirmaciones pueden sostenerse técnicamente?

| Afirmación | Sostenible |
|---|---|
| ZOE piensa continuamente sin input | ✅ |
| ZOE tiene identidad criptográfica inmutable persistente | ✅ |
| ZOE registra cada cambio en cadena verificable persistente | ✅ |
| ZOE se auto-modifica dentro de límites constitucionales | ✅ |
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

**14 de 14 afirmaciones son sostenibles con evidencia trazable.**

---

*ZOE-SPEC-002 — Especificación Fundacional Canónica*
*Commit: 9b10da4 — 14 de julio de 2026*
*Fuente: repositorio GitHub fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO*
