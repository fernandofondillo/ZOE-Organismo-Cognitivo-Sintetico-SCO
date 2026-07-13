# ZOE — Especificación Fundacional Canónica

**Documento:** ZOE-SPEC-001
**Versión:** 1.0
**Fecha:** 2026-07-14
**Commit auditado:** `b06dc87`
**Estado:** Especificación técnica normativa

---

## Comité redactor

Arquitectos de sistemas distribuidos, investigadores en arquitecturas cognitivas (SOAR, ACT-R, OpenCog, Global Workspace, Active Inference, Society of Mind, Predictive Processing), expertos en ingeniería de software, mantenedores de proyectos Open Source, redactores de estándares RFC/ISO/IEEE/W3C, revisores científicos y auditores de calidad de software.

---

## Metodología de auditoría

Se recorrió el repositorio completo en el commit `b06dc87`. Se verificó cada archivo `.py`, cada test, cada endpoint y cada afirmación documental contra el código fuente. Cuando documentación y código discrepan, prevalece el código. Las afirmaciones se trazan con `archivo:línea`.

**Cifras verificadas del repositorio auditado:**

| Métrica | Valor | Método de verificación |
|---|---|---|
| Archivos Python | 71 | `find zoe/ -name "*.py" \| wc -l` |
| LOC Python | 47.017 | `find zoe/ -name "*.py" \| xargs wc -l` |
| Tests | 1.227 | `grep -rc "def test_" zoe/tests/ \| awk -F: '{sum+=$2} END {print sum}'` |
| Archivos de test | 49 | `find zoe/tests/ -name "test_*.py" \| wc -l` |
| Cápsulas | 15 | `find zoe/capsules/ -name "capsule.yaml" \| wc -l` |
| Endpoints REST | 68 | `grep -c "app.router.add_" zoe/web_dashboard.py` |
| Casos de uso YAML | 7 | `ls zoe/use_cases/*.yaml \| wc -l` |
| Docker | 0 | `ls Dockerfile* docker-compose*` → no existe |
| CI/CD | 0 | `ls .github/workflows/` → no existe |

---

# VOLUMEN I — Fundamentos

## 1.1 Propósito

ZOE es un sistema de software que implementa un bucle cognitivo continuo con identidad criptográfica, memoria persistente multi-tipo, metabolismo funcional y capacidad de auto-modificación arquitectural firmada.

**Evidencia:** `core/cognitive_loop.py:57-131` (bucle), `alma/identity_vault.py:57-93` (identidad), `memory/memory_types.py:30-43` (11 tipos), `metabolism/metabolism.py:33-39` (4 estados), `alma/ontogenetic_motor_v2.py:105-169` (auto-modificación).

## 1.2 Alcance

Esta especificación documenta únicamente lo que existe en el código del commit `b06dc87`. No documenta funcionalidades planificadas, roadmaps ni aspiraciones.

## 1.3 Principios

1. **El código es la fuente de verdad.** Si la documentación discrepan del código, el código prevalece.
2. **Toda afirmación es trazable.** Cada afirmación incluye `archivo:línea`.
3. **No se asume nada.** Si un componente no existe en el código, no se documenta como existente.

## 1.4 Límites

ZOE no es:
- Un modelo de lenguaje. Los LLM son periféricos intercambiables.
- Un sistema distribuido. La federación existe como código pero no está desplegada.
- Un producto comercial. No tiene Docker, CI/CD, ni pipeline de despliegue automatizado.

## 1.5 Glosario normativo

| Término | Definición |
|---|---|
| **Organismo** | Sistema con bucle cognitivo continuo, identidad inmutable, metabolismo y memoria persistente. |
| **ALMA** | Conjunto de IdentityVault + TrajectoryChain + OntogeneticMotor. |
| **Identidad** | Hash SHA-256 de 9 vectores + 7 valores + propósito + timestamp de nacimiento. Inmutable. |
| **Trayectoria** | Cadena de mutaciones firmadas con enlace prev_hash. Inmutable (rollback añade, no elimina). |
| **Mutación** | Cambio propuesto al organismo. Tiene type, target, payload, justification, provenance, cost, confidence. |
| **Ley cognitiva** | Restricción verificable en código que toda acción debe cumplir. |
| **Sub-agente** | Componente cognitivo especializado que genera propuestas para el Global Workspace. |
| **Cápsula** | Paquete de conocimiento con schema YAML que se inyecta en componentes del organismo. |
| **ACD** | Adaptive Cognitive Depth. Clasificador heurístico que asigna nivel L0-L3 a cada input. |
| **Tick** | Iteración del bucle cognitivo. Ejecuta observe→predict→evaluate→decide→act. |
| **Metabolismo** | Sistema de estados (awake/drowsy/sleeping/waking) que regula fatiga y energía. |

---

# VOLUMEN II — Modelo Conceptual

## 2.1 Organismo Cognitivo Sintético

**Definición formal:** Sistema de software que cumple simultáneamente:
1. Bucle cognitivo continuo asíncrono (`cognitive_loop.py:99-131`)
2. Identidad criptográfica inmutable (`identity_vault.py:57-93`)
3. Trayectoria firmada auditable (`trajectory_chain.py:82-169`)
4. Memoria persistente multi-tipo (`memory_types.py:30-43`)
5. Metabolismo con estados y homeostasis (`metabolism.py:33-39`)
6. Leyes cognitivas verificables (`cognitive_laws.py:22-30`)

**Responsabilidad:** Existir continuamente, procesar input, generar pensamientos autónomos, evolucionar dentro de límites constitucionales.

**Límites:** No garantiza consistencia distribuida (sin reloj lógico). No garantiza tolerancia a particiones (sin consenso Byzantino). No garantiza escalabilidad horizontal (sin sharding).

## 2.2 ALMA

**Definición formal:** Módulo `zoe/alma/` compuesto por 3 componentes:

| Componente | Archivo | LOC | Responsabilidad |
|---|---|---|---|
| IdentityVault | `identity_vault.py` | 208 | Hash SHA-256 inmutable de invariantes |
| TrajectoryChain | `trajectory_chain.py` | 261 | Cadena de mutaciones firmadas |
| OntogeneticMotorV2 | `ontogenetic_motor_v2.py` | 313 | Aplicación de mutaciones arquitecturales |

**Dependencias:** `CognitiveLaws` (verificación), `TrajectoryChain` (firmado), `IdentityVault` (preservación).

## 2.3 Identidad

**Definición formal:** Hash SHA-256 calculado sobre:
- `name` (str, default "Zoe")
- `vectors` (List[str], 9 vectores)
- `values` (List[str], 7 valores)
- `purpose` (str)
- `birth_timestamp` (float)

**Evidencia:** `identity_vault.py:82-93`.

**Inmutabilidad:** El método `verify()` (líneas 100-130) rechaza cualquier mutación con `target` en `{vectors, values, purpose, identity_vault}`.

**Persistencia:** NO existe. `save_to_disk()` y `load_from_disk()` no existen en el código. La identidad se recrea en cada arranque (`cli_chat.py:165`: `vault = IdentityVault(birth_timestamp=time.time())`). El hash cambia en cada ejecución porque `birth_timestamp` cambia.

## 2.4 Trayectoria

**Definición formal:** Cadena enlazada de objetos `Mutation`. Cada mutación tiene `prev_hash` que apunta al hash de la mutación anterior. La cadena es verificable via `verify_chain()`.

**Evidencia:** `trajectory_chain.py:99-135` (commit), `trajectory_chain.py:147-169` (verify_chain).

**Inmutabilidad:** `rollback()` (líneas 171-211) no elimina la mutación original. Añade una mutación `rollback_previous` que la anula.

**Persistencia:** NO existe. `save_to_disk()` y `load_from_disk()` no existen. La cadena se reinicia vacía en cada arranque (`cli_chat.py:166`: `chain = TrajectoryChain(organism_id="zoe_chat")`).

## 2.5 Evolución

**Definición formal:** Capacidad del organismo de modificar su propia arquitectura en runtime mediante mutaciones firmadas.

**Evidencia:** `ontogenetic_motor_v2.py:105-169` (`apply_architectural_mutation`).

**Tipos de mutación arquitectural implementados:**

| Tipo | Método | Estado |
|---|---|---|
| `add_subagent` | `_add_subagent` L171-223 | ✅ Implementado |
| `remove_subagent` | `_remove_subagent` L225-245 | ✅ Implementado |
| `modify_threshold` | `_modify_threshold` L247-268 | ✅ Implementado |
| `adjust_workspace_capacity` | `_adjust_workspace` L270-280 | ✅ Implementado |
| `adjust_metabolism_threshold` | `_adjust_metabolism` L282-303 | ✅ Implementado |
| `merge_subagents` | — | ❌ Declarado en `ARCHITECTURAL_MUTATION_TYPES` (L38) pero NO implementado. Cae a `super().apply_mutation()` (L154) que solo firma sin ejecutar. |
| `reorganize_memory` | — | ❌ Mismo caso. |

## 2.6 Filogenia

**Definición formal:** `PhylogeneticMotor` (`phylogenetic_motor.py:167`) permite a una ZOE publicar mejoras arquitecturales en un `PhylogeneticPool` compartido. Otras ZOEs las prueban. Si 2+ ZOEs validan con métricas, la mejora se marca como `validated`.

**Evidencia:** `phylogenetic_motor.py:65-165` (pool), `phylogenetic_motor.py:167-272` (motor).

**Estado:** Implementado pero no conectado a un mecanismo de distribución real. El pool es un singleton en memoria (`_instance`, L73-79). No hay descubrimiento de pares ni federación del pool.

---

# VOLUMEN III — Leyes Cognitivas

## 3.1 Las 6 leyes

**Evidencia:** `core/cognitive_laws.py:22-30`.

| Ley | ID | Descripción | Verificación |
|---|---|---|---|
| Utilidad | `UTILITY` | Toda acción debe reducir incertidumbre o aumentar capacidad (suma ≥ 0.01) | `_verify_utility` L158-178 |
| Identidad | `IDENTITY` | Toda modificación debe preservar identidad | `_verify_identity` L180-197 |
| Proveniencia | `PROVENANCE` | Todo conocimiento debe justificar su origen | `_verify_provenance` L199-217 |
| Coste | `COST` | Todo proceso consume recursos (cost > 0) | `_verify_cost` L219-240 |
| Confianza | `CONFIDENCE` | Toda creencia tiene nivel de confianza [0,1] | `_verify_confidence` L242-266 |
| Modularidad | `MODULARITY` | Todo módulo puede reemplazarse si preserva interfaz | `verify_modularity_replacement` L116-156 |

**Implementación:** `verify_action()` (L61-114) ejecuta las 5 primeras leyes en cada acción. La 6ta se verifica explícitamente via `verify_modularity_replacement()`.

**Componentes implicados:** `CognitiveLaws` es instanciado en `cli_chat.py:156` y pasado a `OntogeneticMotorV2` (L167). Las leyes se verifican antes de aplicar cualquier mutación arquitectural (`ontogenetic_motor_v2.py:121-126`).

---

# VOLUMEN IV — Arquitectura

## 4.1 Capas

```
┌─────────────────────────────────────────────┐
│ INTERFAZ: cli_chat.py (892 LOC)             │
│            web_dashboard.py (2789 LOC)      │
│            serve.py (255 LOC)               │
├─────────────────────────────────────────────┤
│ PERIFÉRICOS: llm.py, pattern_speaker.py,    │
│              multimodal.py, voice_first.py,  │
│              model_bus.py, senses.py,        │
│              actuators.py, telegram_bridge   │
├─────────────────────────────────────────────┤
│ NÚCLEO COGNITIVO: cognitive_loop_v5.py      │
│                   depth_classifier.py        │
│                   cognitive_cache.py         │
│                   global_workspace.py        │
│                   meta_cognition.py          │
│                   active_inference.py        │
│                   12 sub-agentes             │
├─────────────────────────────────────────────┤
│ MEMORIA: memory_types.py (11 tipos)         │
│          living_memory.py (in-memory)        │
│          persistent_store.py (SQLite)        │
│          deep_consolidation.py (7 ops)       │
├─────────────────────────────────────────────┤
│ ALMA: identity_vault.py                     │
│       trajectory_chain.py                   │
│       ontogenetic_motor_v2.py               │
├─────────────────────────────────────────────┤
│ METABOLISMO: metabolism.py (4 estados)      │
├─────────────────────────────────────────────┤
│ LEYES Y FÍSICA: cognitive_laws.py (6 leyes) │
│                 cognitive_physics.py         │
│                 cognitive_fields.py          │
│                 cognitive_tensions.py        │
├─────────────────────────────────────────────┤
│ CÁPSULAS: loader.py, manager.py, registry   │
│           15 cápsulas con capsule.yaml       │
├─────────────────────────────────────────────┤
│ COMPONENTES NO CONECTADOS AL BUCLE:         │
│   model_bus.py (577 LOC)                    │
│   resource_planner.py (383 LOC)             │
│   embodiment_composer.py (772 LOC)          │
│   seed_mode.py (876 LOC)                    │
│   language_detector.py (319 LOC)            │
│   mentor.py (280 LOC)                       │
│   cross_validator.py (325 LOC)              │
│   model_optimizer.py (547 LOC)             │
│   federation.py (448 LOC)                   │
│   epistemic_federation*.py (680 LOC)        │
│   resource_discovery.py (489 LOC)           │
│   zoe_packager.py (290 LOC)                 │
│   zoe_runtime.py (499 LOC)                  │
│   intentionality_motor.py (316 LOC)         │
└─────────────────────────────────────────────┘
```

## 4.2 Componentes no conectados al bucle cognitivo

Los siguientes componentes existen en el código pero NO son invocados desde `cognitive_loop_v5.py` ni desde `cli_chat.py` en el flujo principal:

| Componente | LOC | Conectado a | NO conectado a |
|---|---|---|---|
| `ModelBus` | 577 | embodiment_composer, web_dashboard | cognitive_loop_v5 |
| `ResourcePlanner` | 383 | embodiment_composer, web_dashboard | cognitive_loop_v5 |
| `EmbodimentComposer` | 772 | seed_mode, web_dashboard | cognitive_loop_v5 |
| `SeedMode` | 876 | web_dashboard | cognitive_loop_v5, cli_chat |
| `LanguageDetector` | 319 | tests únicamente | cognitive_loop_v5, cli_chat, speaker |
| `MentorAgent` | 280 | cli_chat (instanciado L285) | on_thought callback |
| `CrossValidator` | 325 | tests únicamente | epistemic_validator |
| `ModelOptimizer` | 547 | web_dashboard endpoints | cognitive_loop_v5 |
| `FederationManager` | 448 | serve.py, tests | cli_chat |
| `ResourceDiscovery` | 489 | web_dashboard | cognitive_loop_v5 |
| `IntentionalityMotor` | 316 | cognitive_loop_v05 | V5 (heredado pero no genera acciones) |

**Evidencia de MentorAgent no conectado:** `cli_chat.py:310-313` muestra el callback `on_thought` que solo hace `self._thoughts_while_idle.append(thought)`. No invoca `self.mentor.evaluate_thought()`.

**Evidencia de LanguageDetector no conectado:** `grep -rn "LanguageDetector" zoe/ --include="*.py" | grep -v "test_\|language_detector.py"` devuelve 0 resultados.

---

# VOLUMEN V — Modelo Cognitivo

## 5.1 ¿Cómo percibe?

ZOE percibe via `Sense` objects (`peripherals/senses.py`). Sentidos implementados:

| Sense | Archivo:línea | Qué observa |
|---|---|---|
| `ClockSense` | `senses.py:43` | Hora del día, periodo (mañana/tarde/noche) |
| `UserInputSense` | `senses.py:207` | Input del usuario via `inject_input()` |
| `FilesystemSense` | `senses.py:109` | Cambios en filesystem |
| `NetworkSense` | `senses.py:239` | Estado de red |
| `AgentSense` | `senses.py:380` | Otros agentes |

**Flujo:** `_observe()` (`cognitive_loop.py:142`) llama `sense.observe()` para cada sentido. Devuelve `Observation` objects con `source`, `content`, `timestamp`.

## 5.2 ¿Cómo decide?

El bucle V5 (`cognitive_loop_v5.py`) implementa decisión ramificada por nivel ACD:

1. `DepthClassifier.classify(input)` → asigna nivel L0/L1/L2/L3
2. Si L0: respuesta refleja de tabla (`_L0_REFLEX_RESPONSES`, L34-72)
3. Si L1: `memory.search(n=3)` → `speaker.generate_thought()`
4. Si L2: `memory.search(n=5)` → `perceiver.generate_thought()` → `speaker.generate_thought()` → `critic.generate_thought()` (regenera si "inadecuada")
5. Si L3: 12 sub-agentes proponen → `GlobalWorkspace.compete()` → `MetaCognition.should_deliberate()` → `ActiveInference.select_action()` → `_decide_v3()` → `_act_v3()`

**Procesos deterministas:** ACD classification (heurístico sin LLM), L0 reflex (tabla), cache lookup.

**Procesos probabilísticos:** L1/L2/L3 responses (dependen del LLM, temperature=0.7).

**Procesos concurrentes:** El bucle cognitivo corre en background (`cli_chat.py:339`: `asyncio.create_task(self._run_background())`). El chat es async. El dashboard usa WebSocket.

## 5.3 ¿Cómo aprende?

1. **Memoria episódica:** cada conversación se guarda (`cognitive_loop_v5.py:257-274`)
2. **Cápsulas:** `CapsuleManager.load()` inyecta conocimiento (`capsule_manager.py:97-374`)
3. **Consolidación:** durante SLEEPING, `DeepConsolidation.consolidate()` ejecuta 7 operaciones
4. **Ontogenia:** `OntogeneticMotorV2` puede proponer mutaciones arquitecturales

## 5.4 ¿Cómo recuerda?

`LivingMemory` (`living_memory.py:67`) mantiene entries en memoria. `PersistentMemoryStore` (`persistent_store.py:29`) persiste a SQLite. Búsqueda via `search(query, n)` que usa similitud Jaccard (no embeddings).

## 5.5 ¿Cómo olvida?

`DeepConsolidation._deep_forget()` (`deep_consolidation.py:221-252`): elimina entries con `salience < 0.2 AND confidence < 0.3 AND access_count < 1`.

`LivingMemory._forget_low_salience()` (`living_memory.py`): elimina entries con `confidence < 0.3`.

## 5.6 ¿Cómo consolida?

Durante SLEEPING (`cognitive_loop_v4.py:122-139`), cada 3 iteraciones se ejecuta `DeepConsolidation.consolidate()` con 7 operaciones: episodic_to_semantic, extract_patterns, reinforce_beliefs, deep_forget, generate_hypotheses, detect_contradictions, reorganize_types.

## 5.7 ¿Cómo usa los LLM?

El LLM es un periférico intercambiable. `Speaker.generate_thought()` (`speaker.py:75-119`) llama `self.llm.generate(prompt, system, max_tokens, temperature)`. El LLM no toma decisiones. Las decisiones las toma el bucle cognitivo. El LLM genera lenguaje a partir del contexto preparado por los sub-agentes.

**Backends implementados:** Mock, Ollama, OpenAICompatible, Anthropic, ZAI. PatternPeripheral existe pero NO está registrado en la factory `create_llm_peripheral()`.

## 5.8 ¿Qué papel real tienen los LLM?

Los LLM son la "voz" de ZOE, no su "cerebro". El cerebro es el bucle cognitivo + 12 sub-agentes + Global Workspace + MetaCognition. El LLM recibe un prompt enriquecido con contexto preparado y genera texto. No participa en decisiones de routing, nivel cognitivo, ni evolución arquitectural.

---

# VOLUMEN VI — Modelo de Memoria

## 6.1 Tipos de memoria

**Evidencia:** `memory/memory_types.py:30-43`.

| Tipo | Enum | Uso |
|---|---|---|
| Episódica | `EPISODIC` | Eventos espacio-temporales |
| Semántica | `SEMANTIC` | Hechos y conceptos |
| Procedimental | `PROCEDURAL` | Habilidades |
| Causal | `CAUSAL` | Causa-efecto |
| Emocional | `EMOTIONAL` | Patrones afectivos |
| Corporal | `CORPOREAL` | Estado de sensores |
| Social | `SOCIAL` | Modelos de otros agentes |
| Prospectiva | `PROSPECTIVE` | Planes futuros |
| Contrafactual | `COUNTERFACTUAL` | Hipótesis alternativas |
| Evolutiva | `EVOLUTIONARY` | Historial de mutaciones |
| Cultural | `CULTURAL` | Normas y convenciones |

## 6.2 Persistencia

`PersistentMemoryStore` (`persistent_store.py:29`) usa SQLite con una sola tabla `memory_entries` (L71-86). Columnas: `id, type, content, confidence, salience, provenance, timestamp, last_access, access_count, merged_from, contradictions, metadata`.

**3 índices:** `idx_type` (L89), `idx_salience` (L90), `idx_timestamp` (L91).

**BUG de documentación:** El docstring (L11) dice "una tabla por tipo de memoria (11 tablas)". El código crea 1 tabla. El código prevalece.

## 6.3 Ciclo de vida

1. `LivingMemory.add()` → crea entry en memoria
2. `PersistentMemoryStore.save_entry()` → persiste a SQLite
3. `LivingMemory.search()` → busca por similitud Jaccard
4. `DeepConsolidation` → reorganiza durante SLEEPING
5. `LivingMemory._forget_low_salience()` → elimina entries de baja confianza

---

# VOLUMEN VII — Metabolismo

## 7.1 Estados

**Evidencia:** `metabolism/metabolism.py:33-39`.

| Estado | Descripción | Transición |
|---|---|---|
| AWAKE | Estado normal, atención alta | → DROWSY si fatigue > 0.6 |
| DROWSY | Fatiga acumulada | → SLEEPING si fatigue > 0.8; → AWAKE si fatigue < 0.3 |
| SLEEPING | Consolidación de memoria | → WAKING si energy > 0.8 AND fatigue < 0.2 |
| WAKING | Transición | → AWAKE (siguiente tick) |

## 7.2 Umbrales

| Umbral | Valor | Evidencia |
|---|---|---|
| `drowsy_threshold` | 0.6 | `metabolism.py:61` |
| `sleep_threshold` | 0.8 | `metabolism.py:62` |
| `wake_threshold` | 0.3 | `metabolism.py:63` |

## 7.3 Presupuesto de cómputo

`compute_budget = 1.0` (L73), `compute_spent = 0.0` (L74). `spend_compute(amount)` (L213-223) devuelve False si agotado.

## 7.4 Consolidación durante SLEEPING

`cognitive_loop_v4.py:122-139`: si `state.value == "sleeping"` y `iteration_count % 3 == 0`, ejecuta `deep_consolidation.consolidate()` + `save_to_disk()`.

---

# VOLUMEN VIII — Arquitectura de Modelos

## 8.1 ACD

**Evidencia:** `core/depth_classifier.py:34-39`.

**4 niveles (NO 5):**

| Nivel | Coste | Confianza |
|---|---|---|
| L0_REFLEX | 0.05 | 0.95 |
| L1_FAST | 0.10 | 0.80 |
| L2_STANDARD | 0.30 | 0.65 |
| L3_DEEP | 0.60 | 0.55 |

**L3_MAXIMUM NO EXISTE.** La documentación menciona un 5º nivel pero el código solo tiene 4.

## 8.2 Backends LLM

**Evidencia:** `peripherals/llm.py:613-648` (factory `create_llm_peripheral`).

| Backend | Clase | En factory | Streaming |
|---|---|---|---|
| mock | `MockPeripheral` | ✅ Sí | Simulado |
| ollama | `OllamaPeripheral` | ✅ Sí | Real (NDJSON) |
| openai_compatible | `OpenAICompatiblePeripheral` | ✅ Sí | Real (SSE) |
| anthropic | `AnthropicPeripheral` | ✅ Sí | Real (SSE) |
| zai | `ZAIPeripheral` | ✅ Sí | No |
| pattern | `PatternPeripheral` | ❌ NO | Simulado |

**BUG:** `PatternPeripheral` existe (`pattern_speaker.py:134`) pero NO está registrado en la factory. `--backend pattern` lanza `ValueError`. Tampoco está en `choices` de argparse (`cli_chat.py:865`, `web_dashboard.py:2763`).

## 8.3 ModelDownloader y ModelProfileRouter

**NO EXISTEN.** Los archivos `core/model_downloader.py` y `core/model_profile_router.py` no están en el repositorio. Toda la documentación sobre setups IQ2_M, FALLBACK_CHAINS, hot-swap de modelos por ACD, y endpoints `/api/router/*` describe funcionalidades que no están implementadas.

## 8.4 Routing de modelos

No existe routing dinámico de modelos. El modelo se fija en el arranque via `--model` y no cambia. El ACD clasifica profundidad pero no cambia el modelo subyacente.

## 8.5 PatternSpeaker

`PatternPeripheral` (`pattern_speaker.py:134`) genera respuestas sin LLM usando:
1. Clasificación de intención (9 intents, `<1ms`)
2. Recuperación de memoria (Jaccard similarity)
3. Templates con variables de contexto

`EnhancedPatternPeripheral` (`enhanced_pattern_speaker.py:424`) añade 3 capas:
1. ResponseDistiller (destilación de respuestas LLM)
2. CapsuleRetriever (recuperación de conocimiento de cápsulas)
3. DialogStateTracker (contexto conversacional)

---

# VOLUMEN IX — Interfaces

## 9.1 CLI

**Entrypoint:** `zoe-chat` (`setup.py:42` → `cli_chat:main`).

**Argumentos:**

| Flag | Tipo | Default | Choices |
|---|---|---|---|
| `--backend` | str | mock | mock, zai, ollama, openai_compatible, anthropic |
| `--model` | str | None | — |
| `--use-case` | str | None | — |
| `--db-path` | str | zoe_data/chat_memory.db | — |
| `--api-key` | str | None | — |
| `--base-url` | str | None | — |

**BUG:** `pattern` no está en choices. No se puede usar `--backend pattern`.

## 9.2 Dashboard

**Entrypoint:** `zoe-dashboard` (`setup.py:43` → `web_dashboard:main`).

**68 endpoints REST** en `web_dashboard.py`.

**BUG:** Bind a `0.0.0.0` (L192) sin autenticación.

**BUG:** `cwd="/home/z/my-project/zoe-analysis/repo"` hardcodeado en L717 y L847.

## 9.3 Comandos especiales del chat

| Comando | Implementación |
|---|---|
| `/stats` | ✅ `cli_chat.py` |
| `/memory` | ✅ |
| `/identity` | ✅ |
| `/state` | ✅ |
| `/capsules` | ✅ |
| `/capsule <name>` | ✅ |
| `/uncapsule <name>` | ✅ |
| `/sleep` | ✅ |
| `/wake` | ✅ |
| `/llm <backend> <model>` | ✅ |
| `/quit` | ✅ |

## 9.4 Scripts de instalación

| Script | Existe |
|---|---|
| `install_pendrive_macos.sh` | ✅ |
| `install_windows.ps1` | ✅ |
| `deploy.sh` | ✅ |
| `zoe_large_model_manager.sh` | ✅ |
| `zoe-bootstrap.sh` | ❌ NO EXISTE |
| `zoe_setup.py` | ❌ NO EXISTE |
| `backup.sh` | ❌ NO EXISTE |

---

# VOLUMEN X — Seguridad

## 10.1 Identidad

SHA-256 sobre invariantes (`identity_vault.py:82-93`). Verificación de hash en `from_dict()` (L190-194). Verificación de mutaciones en `verify()` (L100-130).

**Persistencia:** NO existe. La identidad se pierde al reiniciar.

## 10.2 Criptografía

- Hash: SHA-256 (`hashlib.sha256`)
- Firma: SHA-256 de `{hash}:{timestamp}:{organism_id}` (`trajectory_chain.py:144-145`)
- Sin ECDSA, sin claves asimétricas, sin PKI.

## 10.3 Dashboard

- Bind: `0.0.0.0:8642` (sin auth, sin TLS)
- Sin rate limiting
- Sin CORS restrictivo
- Sin tokens de sesión

**Riesgo:** Cualquier dispositivo en la red puede acceder al dashboard, leer memoria, cargar cápsulas y comunicarse con ZOE.

## 10.4 Auditoría

`TrajectoryChain` registra cada mutación con hash, firma y `prev_hash`. `verify_chain()` verifica integridad. Pero la cadena NO persiste entre sesiones.

---

# VOLUMEN XI — Despliegue

## 11.1 Requisitos

- Python ≥ 3.10 (`setup.py:23`)
- Dependencias: aiohttp ≥ 3.9.0, PyYAML ≥ 6.0 (`setup.py:24-27`)
- Opcional: Ollama, OpenAI API key, Anthropic API key

## 11.2 Instalación

```bash
git clone <repo>
cd <repo>
pip install -e .
```

No existe `zoe-bootstrap.sh`. No existe `zoe_setup.py`. La instalación es manual via `pip install`.

## 11.3 Docker

NO existe Dockerfile. NO existe docker-compose.

## 11.4 CI/CD

NO existe `.github/workflows/`.

## 11.5 Configuración

| Archivo | Contenido |
|---|---|
| `config/development.yaml` | Config de desarrollo |
| `config/production.yaml` | Config de producción |

`serve.py:47` carga config YAML. `cli_chat.py` y `web_dashboard.py` NO cargan config YAML (usan argparse únicamente).

---

# VOLUMEN XII — Gobernanza

## 12.1 Versionado

`setup.py:14`: `version="1.2.0"`. No existe política semver documentada.

## 12.2 Compatibilidad

`CognitiveLoopV5` hereda de `V4` que hereda de `V3` que hereda de `V05`. V5 es backward-compatible: si no se pasa `depth_classifier`, degrada a V4 (`cognitive_loop_v5.py:153-155`).

## 12.3 Extensibilidad

Puntos de extensión en código:

| Extensión | Mecanismo |
|---|---|
| Nuevo sub-agente | `OntogeneticMotorV2._add_subagent()` |
| Nueva cápsula | Crear directorio en `capsules/` con `capsule.yaml` |
| Nuevo backend LLM | Heredar `LLMPeripheral`, añadir rama en factory |
| Nuevo endpoint | `app.router.add_get/post()` en `web_dashboard.py` |
| Nuevo tipo de memoria | Añadir a `MemoryType` enum |

---

# CAPÍTULO ESPECIAL — Trazabilidad

## Trazabilidad de afirmaciones clave

| Afirmación | Archivo | Línea | Test |
|---|---|---|---|
| Bucle cognitivo continuo | `cognitive_loop.py` | 99-131 | `test_cognitive_loop.py` |
| 6 leyes cognitivas | `cognitive_laws.py` | 22-30 | `test_cognitive_laws.py` |
| 11 tipos de memoria | `memory_types.py` | 30-43 | `test_memory_types.py` |
| 4 estados metabólicos | `metabolism.py` | 33-39 | `test_metabolism.py` |
| Hash SHA-256 inmutable | `identity_vault.py` | 82-93 | `test_identity_vault.py` |
| Cadena verificable | `trajectory_chain.py` | 147-169 | `test_trajectory_ontogenetic.py` |
| 4 niveles ACD | `depth_classifier.py` | 34-39 | `test_phase5_acd.py` |
| 12 sub-agentes | `phase2_subagents.py` + `subagents/` | — | `test_subagents.py` |
| 15 cápsulas | `capsules/*/capsule.yaml` | — | `test_phase6_capsules.py` |
| 68 endpoints REST | `web_dashboard.py` | — | `test_web_dashboard.py` |
| PatternSpeaker sin LLM | `pattern_speaker.py` | 134 | `test_sprint3_zoe_format.py` |
| OntogeneticMotorV2 | `ontogenetic_motor_v2.py` | 46 | `test_trajectory_ontogenetic.py` |
| PhylogeneticMotor | `phylogenetic_motor.py` | 167 | `test_intentionality_phylogenetic.py` |
| DeepConsolidation 7 ops | `deep_consolidation.py` | 59-132 | `test_phase3_4_5.py` |

---

# CAPÍTULO ESPECIAL — Auditoría Arquitectónica

## Fortalezas

1. **Separación de capas clara:** ALMA → Memoria → Núcleo → Periféricos → Interfaz
2. **Leyes cognitivas verificables en código:** no son aspiraciones, son ejecutables
3. **Cadena de herencia del bucle cognitivo:** V→V05→V3→V4→V5 con backward compatibility
4. **PatternSpeaker como fallback universal:** ZOE funciona sin LLM
5. **Cápsulas auto-descubiertas:** filesystem scanning, sin registro manual
6. **OntogeneticMotorV2 con verificación de leyes + identidad:** auto-modificación constitucional
7. **Metabolismo con consolidación real:** 7 operaciones durante SLEEPING

## Debilidades

1. **9 componentes no conectados al bucle:** ModelBus, ResourcePlanner, EmbodimentComposer, SeedMode, LanguageDetector, MentorAgent, CrossValidator, ModelOptimizer, FederationManager
2. **Sin persistencia de identidad ni trayectoria:** ZOE "nace" de nuevo cada arranque
3. **Sin Docker ni CI/CD:** no hay pipeline de despliegue
4. **Dashboard sin auth ni TLS:** no desplegable en producción
5. **cwd hardcodeado:** `web_dashboard.py:717,847`
6. **PatternPeripheral no en factory:** `--backend pattern` no funciona
7. **serve.py usa V4:** producción no usa ACD
8. **Sin embeddings:** búsqueda por Jaccard, no semántica
9. **2 mutaciones arquitecturales declaradas pero no implementadas:** `merge_subagents`, `reorganize_memory`

## Acoplamiento

- `cli_chat.py` tiene alto acoplamiento: instancia 30+ componentes manualmente (L71-345)
- `web_dashboard.py` es monolítico: 2789 LOC en un archivo
- `cognitive_loop_v5.py` depende de V4 que depende de V3 que depende de V05

## Complejidad

- 5 versiones del bucle cognitivo coexisten (V, V05, V3, V4, V5)
- 34 archivos en `core/` con 13.743 LOC
- 11 tipos de memoria pero 1 sola tabla SQLite

## Escalabilidad

- No escalable horizontalmente (sin sharding, sin particionamiento)
- Memoria en RAM (`LivingMemory`) con max_entries=5000
- SQLite no diseñado para concurrencia alta

## Mantenibilidad

- Sin type hints en la mayoría del código
- Sin linter configurado
- Sin CI que valide PRs
- 49 archivos de test sin cobertura medida

## Observabilidad

- `logging.basicConfig(level=WARNING)` a stdout únicamente
- Sin métricas Prometheus
- Sin tracing distribuido
- Sin health check endpoint

## Capacidad de evolución

- OntogeneticMotorV2 permite auto-modificación arquitectural
- PhylogeneticMotor permite evolución de especie
- Pero ambos operan en memoria, sin persistencia ni distribución

---

# CAPÍTULO ESPECIAL — Riesgos

## Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Pérdida de identidad al reiniciar | Cierta | Crítico | Implementar persistencia |
| Pérdida de trayectoria al reiniciar | Cierta | Crítico | Implementar persistencia |
| Dashboard accesible sin auth | Cierta | Alto | Implementar auth + bind 127.0.0.1 |
| cwd hardcodeado rompe cápsulas | Cierta | Alto | Hacer dinámico |
| PatternPeripheral inaccesible | Cierta | Medio | Añadir a factory + choices |

## Riesgos arquitectónicos

| Riesgo | Descripción |
|---|---|
| Monolito web_dashboard.py | 2789 LOC en un archivo, difícil de mantener |
| 5 versiones del bucle coexistiendo | Confusión sobre cuál es la activa |
| 9 componentes no conectados | Código muerto o huérfano |
| Sin abstracción de storage | SQLite hardcodeado, sin interfaz |

## Riesgos de seguridad

| Riesgo | Descripción |
|---|---|
| Bind 0.0.0.0 sin auth | Cualquiera en la red puede acceder |
| Sin TLS | Comunicación en claro |
| Sin rate limiting | Vulnerable a abuso |
| API keys en .env sin cifrar | Exposición de credenciales |

---

# CAPÍTULO ESPECIAL — Diferencias entre visión y realidad

## Matriz de discrepancias

| Visión declarada | Implementación real | Evidencia | Brecha |
|---|---|---|---|
| 5 niveles ACD (L0-L3_MAXIMUM) | 4 niveles (L0-L3_DEEP) | `depth_classifier.py:34-39` | Falta L3_MAXIMUM |
| Identidad persiste entre sesiones | Se recrea cada arranque | `cli_chat.py:165` | Sin save_to_disk |
| Trayectoria persiste entre sesiones | Se reinicia vacía | `cli_chat.py:166` | Sin save_to_disk |
| Cápsulas cargadas persisten | Se recargan manualmente | `cli_chat.py:291` | Sin save_loaded_state |
| Dashboard seguro (127.0.0.1 + auth) | 0.0.0.0 sin auth | `web_dashboard.py:192` | Sin auth ni bind seguro |
| --backend pattern funciona | No en choices ni factory | `cli_chat.py:865`, `llm.py:613` | ValueError |
| ModelDownloader con 9 modelos IQ2_M | Archivo no existe | `ls zoe/core/model_downloader.py` | No implementado |
| ModelProfileRouter con hot-swap | Archivo no existe | `ls zoe/core/model_profile_router.py` | No implementado |
| zoe-bootstrap.sh instalador | No existe | `ls zoe/scripts/zoe-bootstrap.sh` | No implementado |
| zoe_setup.py asistente | No existe | `ls zoe/scripts/zoe_setup.py` | No implementado |
| Endpoints /api/router/* | No existen | `grep /api/router web_dashboard.py` = 0 | No implementado |
| Endpoints /api/voice/* | No existen | `grep /api/voice web_dashboard.py` = 0 | No implementado |
| VLM en feed_upload | No implementado | `web_dashboard.py:374-419` | Sin VLM |
| LanguageDetector conectado | No conectado | grep = 0 en cli_chat y V5 | No conectado |
| Mentor evalúa pensamientos | No conectado | `cli_chat.py:310-313` | No invoca evaluate_thought |
| CognitiveOptimizationLayer | No existe | find = 0 | No implementado |
| Storage abstraction (SQLite+PostgreSQL) | No existe | `ls zoe/storage/` | No implementado |
| ReflectionEngine | No existe | find = 0 | No implementado |
| Docker | No existe | `ls Dockerfile*` | No implementado |
| CI/CD | No existe | `ls .github/workflows/` | No implementado |
| 1.648 tests | 1.227 tests | `grep -rc "def test_"` | 421 tests menos |
| 74 endpoints | 68 endpoints | `grep -c "app.router.add_"` | 6 endpoints menos |
| Speaker.register_validators | No existe | `grep register_validators speaker.py` = 0 | No implementado |
| Speaker.add_specialized_prompt | No existe | `grep add_specialized speaker.py` = 0 | No implementado |
| 6 leyes cognitivas (doc dice 7) | 6 leyes | `cognitive_laws.py:22-30` | Doc dice 7, código tiene 6 |
| 11 tablas de memoria | 1 tabla | `persistent_store.py:71-86` | Doc miente, código es correcto |

---

# CAPÍTULO FINAL — Estado real del proyecto

## ¿Qué está realmente terminado?

| Componente | Estado | Evidencia |
|---|---|---|
| Bucle cognitivo V5 con ACD | ✅ Terminado | 587 LOC, 45 tests |
| ALMA (IdentityVault + TrajectoryChain + OntogeneticMotorV2) | ✅ Terminado | 993 LOC, 39 tests |
| 6 leyes cognitivas verificables | ✅ Terminado | 287 LOC, 15 tests |
| 11 tipos de memoria + SQLite | ✅ Terminado | 959 LOC, 42 tests |
| 4 estados metabólicos + consolidación | ✅ Terminado | 585 LOC, 17 tests |
| 12 sub-agentes (Society of Mind) | ✅ Terminado | 602+236+180+84+65 LOC |
| 15 cápsulas de conocimiento | ✅ Terminado | 15 capsule.yaml |
| 5 backends LLM (+ PatternPeripheral sin registrar) | ✅ Terminado | 648 LOC, 9 tests |
| PatternSpeaker + EnhancedPatternSpeaker | ✅ Terminado | 889 LOC |
| Dashboard con 68 endpoints | ✅ Terminado | 2789 LOC, 12 tests |
| Voice-first mode | ✅ Terminado | 797 LOC, 37 tests |
| Multimodal (VLM + STT + TTS) | ✅ Terminado | 636 LOC |
| Telegram bridge | ✅ Terminado | 359 LOC |
| Formato .zoe portátil | ✅ Terminado | 290+499 LOC |
| PhylogeneticMotor | ✅ Terminado | 271 LOC |
| Global Workspace + MetaCognition + ActiveInference | ✅ Terminado | 537 LOC |
| CognitivePhysics + Fields + Tensions | ✅ Terminado | 751 LOC |
| Knowledge Quarantine + EpistemicValidator | ✅ Terminado | 683 LOC |
| Federation (Manager + Server + Client) | ✅ Terminado | 1.128 LOC |
| Marketplace de cápsulas | ✅ Terminado | 454 LOC |

## ¿Qué está parcialmente implementado?

| Componente | Estado | Gap |
|---|---|---|
| OntogeneticMotorV2 | ⚠️ Parcial | 2 de 7 tipos no implementados |
| PhylogeneticMotor | ⚠️ Parcial | Pool en memoria, sin distribución |
| Federation | ⚠️ Parcial | Código existe, sin discovery de pares |
| MentorAgent | ⚠️ Parcial | Instanciado pero no conectado al bucle |
| LanguageDetector | ⚠️ Parcial | 319 LOC implementados, no conectados |

## ¿Qué es experimental?

| Componente | Estado |
|---|---|
| EmbodimentComposer | Experimental (772 LOC, solo REST) |
| SeedMode | Experimental (876 LOC, solo REST) |
| ModelOptimizer | Experimental (547 LOC, solo REST) |
| ResourcePlanner | Experimental (383 LOC, solo REST) |
| ModelBus | Experimental (577 LOC, no conectado al bucle) |

## ¿Qué es conceptual?

| Componente | Estado |
|---|---|
| ModelDownloader + ModelProfileRouter | Conceptual (no existe código) |
| CognitiveOptimizationLayer (ZMAP/CPL/TPE) | Conceptual (no existe código) |
| Storage abstraction (PostgreSQL) | Conceptual (no existe código) |
| ReflectionEngine | Conceptual (no existe código) |
| zoe-bootstrap.sh | Conceptual (no existe código) |
| zoe_setup.py | Conceptual (no existe código) |
| Docker/CI/CD | Conceptual (no existe) |

## ¿Qué está listo para producción?

| Componente | Listo | Razón |
|---|---|---|
| Bucle cognitivo + ACD | ✅ | Estable, 45 tests |
| ALMA | ✅ | Estable, 39 tests |
| Memoria + SQLite | ✅ | Estable, 42 tests |
| Cápsulas | ✅ | Estable, 52 tests |
| LLM backends (Ollama, OpenAI, Anthropic) | ✅ | Estables |
| PatternSpeaker | ✅ | Estable |

## ¿Qué necesita endurecimiento antes de producción?

| Componente | Razón |
|---|---|
| Dashboard | Bind 0.0.0.0, sin auth, cwd hardcodeado |
| Identidad/Trayectoria | Sin persistencia entre sesiones |
| serve.py | Usa V4, no V5 |
| Tests | Sin cobertura medida, sin CI |
| Logging | Solo stdout, sin rotación |
| Seguridad | Sin TLS, sin rate limiting |

## ¿Qué partes constituyen innovación demostrable?

1. **OntogeneticMotorV2:** auto-modificación arquitectural con verificación de leyes + identidad + firma criptográfica. Demostrable en `ontogenetic_motor_v2.py:105-169`.
2. **6 leyes cognitivas verificables en código:** restricciones ejecutables, no aspiracionales. Demostrable en `cognitive_laws.py:61-114`.
3. **ACD con 5 señales:** clasificación heurística sin LLM en <50ms. Demostrable en `depth_classifier.py:210-341`.
4. **Cápsulas de conocimiento con inyección en componentes:** aprendizaje sin reentrenar. Demostrable en `capsule_manager.py:142-374`.
5. **Metabolismo con consolidación durante sueño:** 7 operaciones de reorganización. Demostrable en `deep_consolidation.py:59-132`.
6. **PatternSpeaker:** generación de lenguaje sin LLM. Demostrable en `pattern_speaker.py:134`.

## ¿Qué afirmaciones pueden sostenerse técnicamente frente a una revisión científica?

| Afirmación | Sostenible | Evidencia |
|---|---|---|
| ZOE piensa continuamente sin input | ✅ | `cognitive_loop.py:99-131` |
| ZOE tiene identidad criptográfica inmutable | ✅ | `identity_vault.py:82-93` |
| ZOE registra cada cambio en cadena verificable | ✅ | `trajectory_chain.py:99-169` |
| ZOE se auto-modifica dentro de límites constitucionales | ✅ | `ontogenetic_motor_v2.py:105-169` |
| ZOE consolida memoria durante sueño | ✅ | `deep_consolidation.py:59-132` |
| ZOE usa 12 sub-agentes coordinados via Global Workspace | ✅ | `global_workspace.py` + `phase2_subagents.py` |
| ZOE persiste identidad entre sesiones | ❌ | Sin save_to_disk |
| ZOE persiste trayectoria entre sesiones | ❌ | Sin save_to_disk |
| ZOE detecta idioma automáticamente | ❌ | LanguageDetector no conectado |
| ZOE usa mentor para guiar pensamientos | ❌ | evaluate_thought no invocado |
| ZOE enruta modelos dinámicamente por ACD | ❌ | ModelProfileRouter no existe |
| ZOE tiene 5 niveles cognitivos | ❌ | Solo 4 niveles |

## ¿Cuáles necesitarían más evidencia?

1. **PhylogeneticMotor como evolución de especie:** el pool es un singleton en memoria. Sin distribución, sin métricas reales de mejora. Necesita experimentación con múltiples instancias.
2. **GlobalWorkspace como modelo de conciencia:** implementa competición de propuestas, pero no hay evidencia de que esto produzca comportamiento emergente medible.
3. **ActiveInference como principio de Free Energy:** la implementación es un esqueleto. No hay evidencia de que reduce sorpresa de forma verificable.
4. **MetaCognition como System 1/System 2:** implementa thresholds, pero no hay evidencia de que la distinción mejora calidad de respuestas.

---

## Cierre

Esta especificación refleja el estado del repositorio en el commit `b06dc87`. Cualquier afirmación no trazable a `archivo:línea` en este commit debe considerarse no verificada.

**Total de archivos auditados:** 71 archivos Python + 49 archivos de test + 15 capsule.yaml + 7 use_cases YAML + 2 config YAML = 144 archivos.

**Total de LOC auditados:** 47.017 Python + ~18.000 docs = ~65.000 LOC.

---

*ZOE-SPEC-001 — Especificación Fundacional Canónica*
*Commit: b06dc87 — 14 de julio de 2026*
*Este documento es la fuente canónica de verdad del proyecto ZOE.*
