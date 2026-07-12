# ZOE — Documento Técnico para Equipo Técnico y CTO

> **Este documento describe las entrañas completas del proyecto ZOE.** Está dirigido a arquitectos, CTOs, desarrolladores senior e investigadores que necesitan entender el sistema a nivel de código para mejorarlo, contribuir o tomar decisiones de arquitectura.
>
> **Versión:** V1.8.0 — Julio 2026 (Sprint 5.7.3)
> **LOC totales:** ~80.000 (Python ~62.000 + docs ~18.000 + scripts)
> **Tests:** 526 tests en 54 archivos, 18.551 LOC
> **Python:** 3.10+
> **Licencia:** Apache 2.0
>
> **Lectura recomendada previa:** `docs/18_ZOE_EXPLICACION_NO_TECNICOS.md` para contexto conceptual.

---

## Índice

1. [Visión arquitectónica general](#1-visión-arquitectónica-general)
2. [Estructura del proyecto y LOC](#2-estructura-del-proyecto-y-loc)
3. [Cadena de herencia del CognitiveLoop](#3-cadena-de-herencia-del-cognitiveloop)
4. [ALMA — Identidad criptográfica y trayectoria](#4-alma--identidad-criptográfica-y-trayectoria)
5. [Memory — 11 tipos + SQLite + consolidación](#5-memory--11-tipos--sqlite--consolidación)
6. [Metabolism — 4 estados y presupuestos](#6-metabolism--4-estados-y-presupuestos)
7. [Bucle cognitivo V5 — flujo línea a línea](#7-bucle-cognitivo-v5--flujo-línea-a-línea)
8. [DepthClassifier — las 5 señales de detección](#8-depthclassifier--las-5-señales-de-detección)
9. [ModelDownloader y ModelProfileRouter](#9-modeldownloader-y-modelprofilerouter)
10. [Sub-agentes — los 12 agentes (Society of Mind)](#10-sub-agentes--los-12-agentes-society-of-mind)
11. [Capsules — arquitectura, loader, manager, registry](#11-capsules--arquitectura-loader-manager-registry)
12. [Peripherals — LLM, ModelBus, multimodal, voz, Telegram](#12-peripherals--llm-modelbus-multimodal-voz-telegram)
13. [Epistemic validation, cuarentena, federación](#13-epistemic-validation-cuarentena-federación)
14. [CLI y Dashboard — 71 endpoints](#14-cli-y-dashboard--71-endpoints)
15. [Scripts de instalación y despliegue](#15-scripts-de-instalación-y-despliegue)
16. [Tests y cobertura](#16-tests-y-cobertura)
17. [Puntos de extensión para contribuidores](#17-puntos-de-extensión-para-contribuidores)
18. [Decisiones arquitecturales clave (ADRs implícitos)](#18-decisiones-arquitecturales-clave-adrs-implícitos)
19. [Diagrama de flujo de datos end-to-end](#19-diagrama-de-flujo-de-datos-end-to-end)
20. [Deuda técnica y roadmap técnico](#20-deuda-técnica-y-roadmap-técnico)

---

## 1. Visión arquitectónica general

ZOE es un **organismo cognitivo sintético** organizado en 4 capas arquitecturales:

```
┌─────────────────────────────────────────────────────────────────┐
│  CAPA 4: PERIPHERALS (sentidos + actuadores + LLM)              │
│  - 6 backends LLM (Mock, Ollama, OpenAI, Anthropic, ZAI, Pattern) │
│  - ModelBus (6 estrategias selección)                           │
│  - Multimodal (VLM, Whisper STT, Piper TTS)                     │
│  - VoiceFirstMode (Hey ZOE, interrupción)                       │
│  - TelegramBridge                                               │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│  CAPA 3: CORE (bucle cognitivo + 12 sub-agentes)                │
│  - CognitiveLoopV5 (ACTIVO) con ACD + cache + hot-swap          │
│  - DepthClassifier (5 niveles, 5 señales)                       │
│  - ModelProfileRouter (ACD → modelo IQ2_M)                      │
│  - GlobalWorkspace + MetaCognition + ActiveInference            │
│  - CognitiveLaws (6 leyes) + CognitivePhysics + Fields/Tensions │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│  CAPA 2: MEMORY (11 tipos + SQLite + consolidación)             │
│  - LivingMemory (in-memory, Jaccard similarity)                 │
│  - PersistentMemoryStore (SQLite, 3 índices)                    │
│  - DeepConsolidation (7 operaciones durante SLEEPING)           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│  CAPA 1: ALMA (identidad + trayectoria + ontogenia)             │
│  - IdentityVault (SHA-256 hash, 9 vectores, 7 valores)          │
│  - TrajectoryChain (blockchain de mutaciones firmadas)          │
│  - OntogeneticMotorV2 (auto-modificación arquitectural runtime) │
└─────────────────────────────────────────────────────────────────┘
```

**Principios arquitectónicos:**

- **Inmutabilidad del ALMA**: el `IdentityVault` es inmutable desde el nacimiento. Lo que evoluciona es la trayectoria firmada, no la identidad.
- **Soberanía de datos**: todo puede funcionar offline. No hay dependencia de servicios cloud para existir.
- **Auditabilidad criptográfica**: cada decisión importante se firma en la `TrajectoryChain`.
- **Composición sobre herencia**: 12 sub-agentes se inyectan en el bucle, no se heredan.
- **Degradación elegante**: si no hay LLM, PatternSpeaker responde. Si no hay Ollama, cloud fallback. Si no hay nada, tabla refleja L0.

---

## 2. Estructura del proyecto y LOC

### 2.1 LOC por directorio (verificado con `wc -l`)

| Directorio | LOC | Descripción |
|---|---|---|
| `tests/` | 18.551 | 54 archivos, 526 tests |
| `docs/` | 18.482 | 18 documentos + REFERENCE/ |
| `core/` | 15.605 | Núcleo cognitivo (14.437 Python + 1.168 subagents) |
| `phases/` | 3.568 | Planes de fases históricos |
| `peripherals/` | 5.470 | Sentidos, actuadores, LLM, multimodal |
| `capsules/` | 4.328 | 15 cápsulas + infraestructura |
| `scripts/` | 2.513 | Instaladores (bash, ps1, py) |
| `examples/` | 1.622 | Demos |
| `web_dashboard.py` | 2.886 | Dashboard HTTP+WS (71 endpoints) |
| `alma/` | 993 | Identidad criptográfica |
| `memory/` | 959 | 11 tipos + SQLite + consolidación |
| `cli_chat.py` | 927 | CLI chat interactivo |
| `use_cases/` | 779 | 7 casos de uso YAML |
| `marketplace/` | 454 | Marketplace de cápsulas |
| `metabolism/` | 260 | 4 estados metabólicos |
| `config/` | 141 | development.yaml + production.yaml |
| `serve.py` | 255 | Punto entrada producción (systemd) |

**Total:** ~80.000 LOC

### 2.2 Archivos clave (top 20 por LOC)

| Archivo | LOC | Responsabilidad |
|---|---|---|
| `web_dashboard.py` | 2.886 | Dashboard HTTP+WS con 71 endpoints |
| `core/cognitive_loop_v5.py` | 671 | Bucle cognitivo activo con ACD |
| `core/cognitive_optimization.py` | 685 | Sprint 5 (ZMAP + CPL + TPE) |
| `core/model_downloader.py` | 646 | Descarga IQ2_M de HuggingFace |
| `cli_chat.py` | 927 | CLI interactivo ZoeChat |
| `core/cognitive_loop_v05.py` | 597 | Bucle Fase 0.5 (laws, physics, fields) |
| `core/embodiment_composer.py` | 771 | Fase 7D — encarnaciones |
| `core/cognitive_loop_v3.py` | 563 | Bucle Fase 3 (12 sub-agentes) |
| `core/model_optimizer.py` | 547 | Fase 7F/G (mmap, IQ2_M, flash-attn) |
| `core/zoe_runtime.py` | 499 | Runtime .zoe (sin dependencias) |
| `core/capsule_manager.py` | 502 | Inyección de cápsulas en organismo |
| `core/resource_planner.py` | 383 | Fase 7C (ACD→backend→strategy) |
| `core/model_profile_router.py` | 385 | Sprint 5.7 (ACD→modelo) |
| `core/depth_classifier.py` | 384 | Clasificador ACD (5 señales) |
| `core/living_memory.py` | 378 | Memoria viva in-memory |
| `core/seed_mode.py` | 876 | Fase 7E (semilla portátil) |
| `core/subagents/phase2_subagents.py` | 602 | 8 sub-agentes Fase 2 |
| `memory/persistent_store.py` | 377 | SQLite store |
| `memory/deep_consolidation.py` | 325 | Consolidación durante SLEEPING |
| `peripherals/llm.py` | 660 | 6 backends LLM + factory |

---

## 3. Cadena de herencia del CognitiveLoop

Confirmada leyendo los `from ... import` de cada archivo:

```
Thought, Observation (dataclasses)
   ← core/cognitive_loop.py:24-55 (343 LOC)

CognitiveLoop
   ← core/cognitive_loop.py:57
   • 5 fases: OBSERVE → PREDICT → EVALUATE → DECIDE → ACT
   • tick_interval=5.0, surprise threshold=0.5
        │
        ▼  (NO hereda — redefine API paralela)
CognitiveLoopV05
   ← core/cognitive_loop_v05.py:39 (597 LOC)
   • + 7 componentes Fase 0.5: laws, physics, fields, tensions, memory, intentionality, phylogenetic
   • 13 pasos por _tick(): adds _update_fields/_update_tensions/_update_physics/_generate_intentions/_memory_think
   • verify_action contra CognitiveLaws antes de actuar
        │
        ▼  (from .cognitive_loop_v05 import CognitiveLoopV05)
CognitiveLoopV3(CognitiveLoopV05)
   ← core/cognitive_loop_v3.py:41 (563 LOC)
   • + 12 sub-agentes + GlobalWorkspace + MetaCognition + ActiveInferenceLoop + WorldModelV2
   • + 18 pasos por _tick(): _collect_proposals → _workspace_compete → _evaluate_meta_cognition → _consult_active_inference → _decide_v3 → _act_v3 → _broadcast_to_subagents
   • OntogeneticMotor: si surprise > 0.5 propone mutación add_memory (L184-197)
        │
        ▼  (from .cognitive_loop_v3 import CognitiveLoopV3)
CognitiveLoopV4(CognitiveLoopV3)
   ← core/cognitive_loop_v4.py:30 (254 LOC)
   • + DeepConsolidation durante SLEEPING (cada 3 iteraciones, L126)
   • + auto_save_interval=50 (L142-153)
   • + signal handlers SIGTERM/SIGINT (L86-99) → graceful shutdown
   • + load_config(env='development'|'production') + _default_config()
        │
        ▼  (from .cognitive_loop_v4 import CognitiveLoopV4)
CognitiveLoopV5(CognitiveLoopV4)
   ← core/cognitive_loop_v5.py:75 (671 LOC)
   • + Adaptive Cognitive Depth (ACD): DepthClassifier pre-clasifica cada input
   • + CognitiveCache LRU + TTL (idempotencia L0/L1)
   • + Pipeline ramificado: _process_l0 / _process_l1 / _process_l2 / _process_l3
   • + ModelProfileRouter: hot-swap del LLM según nivel ACD (L171-214)
   • + 5 estadísticas: acd_classifications, acd_level_counts, acd_cache_hits, acd_responses_by_level, acd_latency_by_level
   • + get_router_stats() (Sprint 5.7.2)
```

### 3.1 Versión ACTIVA por entrypoint

| Entrypoint | Versión usada | Archivo:línea |
|---|---|---|
| `cli_chat.py` (interactivo) | **CognitiveLoopV5** | `cli_chat.py:75,235` |
| `web_dashboard.py` | Vía `ZoeChat` → V5 | `web_dashboard.py:74-76` |
| `serve.py` (producción systemd) | **CognitiveLoopV4** (sin ACD) | `serve.py:92,189` |
| `use_cases/run_use_case.py` | CognitiveLoopV4 | `run_use_case.py:112,249` |
| `examples/demo_phase1.py` | CognitiveLoopV05 | `demo_phase1.py:30` |

**Por qué V5 es la activa en uso interactivo:** V5 extiende V4 con ACD, cache y hot-swap de modelos. Si no se pasa `depth_classifier`, V5 degrada a comportamiento V4 (`cognitive_loop_v5.py:153-155`). `cli_chat.py` siempre pasa `depth_classifier=DepthClassifier()` y `cognitive_cache=CognitiveCache(max_size=100, ttl_seconds=300)`.

**V5 es backward-compatible con V4**: test explícito en `test_phase5_acd.py:604-605`:
```python
assert issubclass(CognitiveLoopV5, CognitiveLoopV4)
```

`serve.py` sigue en V4 porque el modo producción headless no usa chat interactivo; el bucle corre solo con ticks autónomos.

---

## 4. ALMA — Identidad criptográfica y trayectoria

Directorio: `zoe/alma/` (993 LOC, 4 archivos)

### 4.1 IdentityVault (`identity_vault.py:58`, 208 LOC)

**Hash criptográfico** (`_compute_hash` L82-93):

```python
def _compute_hash(self) -> str:
    data = {
        "name": self.name,                      # "Zoe"
        "vectors": sorted(self.vectors),        # 9 NINE_VECTORS
        "values": sorted(self.values),          # 7 SEVEN_VALUES
        "purpose": self.purpose,                # PURPOSE
        "birth_timestamp": self.birth_timestamp,
    }
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```

**Contenido inmutable:**

- **9 vectores de crecimiento** (`NINE_VECTORS`, L27-37): `emancipacion_coherencia_cognitiva, crecimiento_sostenible, alianza_horizontal_vertical, auto_comprension, comprension_entorno, utilidad, honestidad, empatia, curiosidad`
- **7 valores no negociables** (`SEVEN_VALUES`, L40-48): `verdad_sobre_confort, crecimiento_sobre_estabilidad, alianza_sobre_jerarquia, transparencia_sobre_opacidad, utilidad_sobre_entretenimiento, integridad, coherencia`
- **Propósito declarado** (`PURPOSE`, L51-54): "Zoe mejora individual y colectivamente con un crecimiento y evolución sostenible y coherente."

**Persistencia:** `to_dict()` (L167) y `from_dict()` (L178). Verificación de hash en import (L191-194) — lanza `ValueError` si mismatch.

**Verificación (2da ley):** `verify(action)` (L100-130) rechaza mutaciones con `target` en `{vectors, values, purpose, identity_vault}`. `verify_proposed_state()` (L132-165) compara sets completos.

### 4.2 TrajectoryChain (`trajectory_chain.py:82`, 261 LOC)

**Estructura de `Mutation`** (L28-79):

```python
@dataclass
class Mutation:
    id: str
    type: str             # add_memory | strengthen_belief | weaken_belief | add_skill_subgraph |
                          # update_world_model | adjust_threshold | federate_learning |
                          # rollback_previous | respond_to_user | capsule_loaded | capsule_unloaded
                          # V2 añade: add_subagent | remove_subagent | merge_subagents |
                          # modify_threshold | adjust_workspace_capacity | adjust_metabolism_threshold |
                          # reorganize_memory
    target: str
    payload: Dict[str, Any]
    justification: str
    provenance: str       # 3ra ley
    cost: float           # 4ta ley
    confidence: float     # 5ta ley
    timestamp: float
    signature: Optional[str]
    prev_hash: Optional[str]   # enlace blockchain
    hash: Optional[str]
    applied: bool
    rolled_back: bool
```

**`compute_hash()`** (L58-73): `sha256(json.dumps({id,type,target,payload,justification,provenance,cost,confidence,timestamp,prev_hash}, sort_keys=True))`

**Firma criptográfica** (`_sign`, L137-145): actualmente `sha256("{hash}:{timestamp}:{organism_id}")`. Comentario: "Fase 4: ECDSA con clave privada del organismo" — **no implementado aún**, sigue siendo SHA-256 simbólico. **Deuda técnica**.

**Cadena verificable** (`verify_chain`, L147-169): re-computa hash de cada mutación y verifica enlace `prev_hash`. Si cualquier mutación fue alterada → False.

**Tipos de mutación soportados** (18 tipos):
- V1 (11): `add_memory, strengthen_belief, weaken_belief, add_skill_subgraph, update_world_model, adjust_threshold, federate_learning, rollback_previous, respond_to_user, capsule_loaded, capsule_unloaded`
- V2 arquitecturales (7): `add_subagent, remove_subagent, merge_subagents, modify_threshold, adjust_workspace_capacity, adjust_metabolism_threshold, reorganize_memory`

**Rollback** (L171-211): no elimina — añade mutación `rollback_previous` que anula. Inmutable.

### 4.3 OntogeneticMotorV2 (`ontogenetic_motor_v2.py:46`, 313 LOC)

**Permite a ZOE modificar SU PROPIA ARQUITECTURA en runtime:**

| Mutación | Método | Restricciones |
|---|---|---|
| `add_subagent` | `_add_subagent` L171-223 | 8 tipos permitidos: creativity, causal_engine, emotional_motor, ethical_motor, scientific_engine, memorialist, learner, curator. No duplicados. |
| `remove_subagent` | `_remove_subagent` L225-245 | Protege 4 críticos: perceiver, forecaster, speaker, critic |
| `modify_threshold` | `_modify_threshold` L247-268 | Cambia meta_cognition thresholds |
| `adjust_workspace_capacity` | L270-280 | global_workspace.broadcast_capacity (1-12) |
| `adjust_metabolism_threshold` | L282-303 | Cambia drowsy/sleep/wake |
| `merge_subagents` | — | Pendiente implementación |

**Flujo de aplicación** (`apply_architectural_mutation`, L105-169):

1. Verifica leyes cognitivas (`laws.verify_action`)
2. Verifica identidad (`identity_vault.verify`)
3. Aplica según tipo (método `_add_subagent`, etc.)
4. Si éxito: `trajectory_chain.commit(mutation)` + append a `_architectural_changes`

**Cómo evoluciona la identidad:** NO la evoluciona — el Vault es inmutable. Lo que evoluciona es la trayectoria firmada del organismo. El organismo puede mutar su arquitectura y memoria, pero su hash de identidad permanece constante de por vida.

---

## 5. Memory — 11 tipos + SQLite + consolidación

Directorio: `zoe/memory/` (959 LOC)

### 5.1 Los 11 tipos de memoria (`memory_types.py:30-43`)

```python
class MemoryType(str, Enum):
    EPISODIC       = "episodic"         # eventos espacio-temporales
    SEMANTIC       = "semantic"         # conceptos y relaciones
    PROCEDURAL     = "procedural"       # habilidades, recetas, algoritmos
    CAUSAL         = "causal"           # causa-efecto verificado
    EMOTIONAL      = "emotional"        # marcadores de relevancia
    CORPOREAL      = "corporeal"        # estado de sensores
    SOCIAL         = "social"           # modelos de otros agentes
    PROSPECTIVE    = "prospective"      # planes futuros
    COUNTERFACTUAL = "counterfactual"   # qué habría pasado si
    EVOLUTIONARY   = "evolutionary"     # historial de mutaciones
    CULTURAL       = "cultural"         # normas y convenciones
```

Cada tipo tiene un dataclass especializado (`EpisodicEntry` L63, `SemanticEntry` L73, etc.) que hereda de `MemoryEntry`.

### 5.2 PersistentMemoryStore (`persistent_store.py:29`, 377 LOC)

**Schema SQLite** (tabla única):

```sql
CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    salience REAL DEFAULT 0.5,
    provenance TEXT DEFAULT '',
    timestamp REAL DEFAULT 0,
    last_access REAL DEFAULT 0,
    access_count INTEGER DEFAULT 0,
    merged_from TEXT DEFAULT '[]',
    contradictions TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}'
)
```

**Índices:**
- `idx_type` ON `memory_entries(type)` — filtrar por tipo
- `idx_salience` ON `memory_entries(salience DESC)` — buscar más relevantes
- `idx_timestamp` ON `memory_entries(timestamp DESC)` — recientes

**API pública:**
- `save_entry(entry)`, `save_all(entries)`, `load_all()`, `load_by_type(mem_type)`
- `delete_entry(entry_id)`, `clear()`, `search(query, limit=10)`, `count()`, `count_by_type()`

### 5.3 LivingMemory (`core/living_memory.py:67`, 378 LOC)

Estructura: `self._entries: Dict[str, MemoryEntry]`, auto-prune si > max_entries.

**API:**
- `add(content, type, confidence, salience, provenance, metadata) -> str`
- `get(entry_id) -> Optional[MemoryEntry]` (actualiza last_access, access_count)
- `search(query, n=5)` — similitud **Jaccard** simple (no embeddings)
- `think()` — la memoria viva piensa una operación por tick

**`think()` ejecuta 6 operaciones** (L150):

1. `_reorganize()` — episódica >3 accesos & >1h → semántica
2. `_forget_low_salience(n=10)` — borra entries con confidence < 0.3
3. `_merge_similar()` — Jaccard > 0.7 fusiona
4. `_summarize_old()` — entries >2h → 1 entry semántica resumen
5. `_generalize()` — palabras en 3+ entries → entry de patrón
6. `_detect_contradictions()` — entries "no X" + entry "X" → marcar mutuamente

### 5.4 DeepConsolidation (`deep_consolidation.py:27`, 325 LOC)

**Ejecutado durante SLEEPING** (V4 cada 3 iteraciones de sueño):

7 operaciones en cada ciclo `consolidate()` (L59-132):

1. **`_episodic_to_semantic`**: entries episódicas con access_count>3 AND age>30min → semantic + salience += 0.1
2. **`_extract_patterns`**: palabras en 3+ entries → crea entry semantic "Patrón consolidado en sueño"
3. **`_reinforce_beliefs`**: salience>0.7 AND access_count>2 → confidence += 0.05
4. **`_deep_forget`**: poda salience<0.2 AND confidence<0.3 AND access_count<1 + cuarentena expirada
5. **`_generate_hypotheses`**: teorías pendientes del ScientificEngine → entries counterfactual (max 3/ciclo)
6. **`_detect_contradictions`**: "no X" + "X" → marcar mutuamente, confidence *= 0.7
7. **`_reorganize_types`**: emotional con confidence>0.8 → semantic; counterfactual con access_count>5 → causal

Fase 6A: integra KnowledgeQuarantine. Stats: `_total_consolidations`, `_consolidation_history` (últimas 20).

---

## 6. Metabolism — 4 estados y presupuestos

Archivo: `zoe/metabolism/metabolism.py` (260 LOC)

### 6.1 Los 4 estados (`MetabolicState(str, Enum)` L33-39)

```python
class MetabolicState(str, Enum):
    AWAKE    = "awake"     # sentidos activos, atención alta
    DROWSY   = "drowsy"    # fatiga acumulada, capacidad reducida
    SLEEPING = "sleeping"  # consolidación, recarga
    WAKING   = "waking"    # transición
```

### 6.2 Umbrales de transición (`Metabolism.__init__` L61-63)

```python
drowsy_threshold: float = 0.6   # fatigue > 0.6 → AWAKE→DROWSY
sleep_threshold:  float = 0.8   # fatigue > 0.8 → DROWSY→SLEEPING
wake_threshold:   float = 0.3   # fatigue < 0.3 → DROWSY→AWAKE
```

### 6.3 Lógica de transición (`_update_metabolic_state` L114-139)

- `AWAKE → DROWSY`: fatigue > 0.6
- `DROWSY → SLEEPING`: fatigue > 0.8 (vía `_go_to_sleep` L141-148)
- `DROWSY → AWAKE`: fatigue < 0.3
- `SLEEPING → WAKING`: energy > 0.8 AND fatigue < 0.2 (vía `_wake_up` L150-160)
- `WAKING → AWAKE`: transición inmediata siguiente tick

**Despertar por estímulo externo** (`stimulate`, L204-211): si `state==SLEEPING AND intensity>0.7` → `_wake_up()` inmediato.

### 6.4 Cómo afecta al bucle cognitivo

1. **Tick del metabolismo** (V3 `_tick` L127-129): `self.metabolism.tick(dt)` después de memoria
2. **DeepConsolidation en SLEEPING** (V4 `_tick` L122-139): si `state.value == "sleeping"` y `iteration_count % 3 == 0`, ejecuta `deep_consolidation.consolidate()` + `save_to_disk`
3. **Presupuesto de cómputo**: `compute_budget=1.0, compute_spent=0.0`. `spend_compute(amount) -> bool` devuelve False si agotado
4. **`should_sleep(physics)`** (L171-188): True si `fatigue > sleep_threshold` OR `physics.should_rest()` OR `compute_spent >= compute_budget`

---

## 7. Bucle cognitivo V5 — flujo línea a línea

### 7.1 `process_user_input_acd(user_input: str) -> Dict[str, Any]` (L134-286)

```python
# L153-155: si no hay DepthClassifier, delega a _legacy_process (V4 compat)
if not self.depth_classifier:
    return await self._legacy_process(user_input)

start = time.time()

# 1. CLASIFICAR (L160-163)
classification = self.depth_classifier.classify(user_input)
self.last_classification = classification
self.acd_classifications += 1
self.acd_level_counts[classification.level.value] += 1
level = classification.level

# 1b. ROUTING ACD→MODELO (L170-214, Sprint 5.7)
if self.model_profile_router and level != CognitiveLevel.L0_REFLEX:
    assignment = self.model_profile_router.get_model_for_acd(
        acd_level=level.value, profile=self._active_profile,
    )
    if assignment and hasattr(assignment, "model_tag"):
        routed_tag = assignment.model_tag
        if routed_tag and routed_tag != "pattern":
            speaker = self._find_speaker()
            llm_attr = getattr(speaker, "llm", None) or getattr(speaker, "llm_peripheral", None)
            if llm_attr:
                current_model = getattr(llm_attr, "model", None)
                if current_model != routed_tag:
                    llm_attr.model = routed_tag  # HOT-SWAP
                    self._router_swaps += 1
                    self._last_routed_tag = routed_tag

# 2. CACHE LOOKUP (L217-223) — solo L0_REFLEX y L1_FAST
cached = self.cognitive_cache.get(classification.cache_key) if level in (L0_REFLEX, L1_FAST) else None

# 3. PIPELINE SEGÚN NIVEL (L226-247)
if cache_hit:
    response = cached
    trajectory_hash = None
else:
    if level == L0_REFLEX:
        response, trajectory_hash = await self._process_l0(...)
    elif level == L1_FAST:
        response, trajectory_hash = await self._process_l1(...)
    elif level == L2_STANDARD:
        response, trajectory_hash = await self._process_l2(...)
    elif level == L3_MAXIMUM:
        response, trajectory_hash = await self._process_l3(...)  # mismo pipeline que L3_DEEP
    else:  # L3_DEEP
        response, trajectory_hash = await self._process_l3(...)

# 4. ALMACENAR EN MEMORIA (L257-274)
self.memory.add(content=f"User: {user_input[:100]}", type="episodic", ...)
self.memory.add(content=f"ZOE: {response[:100]}", type="episodic", ...)

# RETURN (L276-286)
return {
    "response": response, "level": level.value, "score": classification.score,
    "reasons": classification.reasons, "cache_hit": cache_hit,
    "latency_ms": round(latency_ms, 2), "trajectory_hash": trajectory_hash,
    "cost": level.cost, "confidence": level.default_confidence,
}
```

### 7.2 Los 4 pipelines ramificados

#### `_process_l0` (L288-313) — REFLEX, sin LLM

- Lookup en `_L0_REFLEX_RESPONSES` dict (L34-72, 38 tokens: hola/hello/ok/gracias/jeje/jaja...)
- Si no match: `"Vale. Te escucho."`
- Registra mutación `respond_to_user` con `cost=0.05, confidence=0.95`

#### `_process_l1` (L315-365) — FAST, 3 sub-agentes

- `memory.search(user_input, n=3)` → memories[:150]
- `speaker.generate_thought(context)` con `acd_level="L1_FAST"`
- Fallback: `"Recibido. {user_input[:50]}..."` si Speaker falla
- Mutación `cost=0.10, confidence=0.80`

#### `_process_l2` (L367-451) — STANDARD, pipeline Fase 0

- `memory.search(n=5)` → memories[:200]
- `perceiver.generate_thought(...)` → `perceived_intent[:150]`
- `speaker.generate_thought(context)` con physics.summary(), tensions.summary(), perceived_intent, relevant_memories, acd_level
- `critic.generate_thought(...)` evalúa respuesta. Si contiene "inadecuada" o "incorrect" → **regenera respuesta**
- Mutación `cost=0.30, confidence=0.65`

#### `_process_l3` (L453-527) — DEEP/MAXIMUM, pipeline Fase 3 completo

1. Crea `Observation(source="user", content=user_input)`
2. `world_model_v2.predict_next(observations)` o fallback `world_model.predict_next`
3. `world_model_v2.compute_surprise(prediction, observations)` — L3 siempre `surprise=0.5` mínimo
4. `_collect_proposals(observations, surprise, prediction)` — TODOS los 12 sub-agentes proponen al Global Workspace
5. `_workspace_compete(proposals)` — GlobalWorkspace selecciona ganadores
6. `_evaluate_meta_cognition(winners, surprise)` — decide System 1 vs System 2 (Kahneman)
7. `_consult_active_inference(observations, surprise)` — sugiere acción
8. `_decide_v3(winners, surprise, observations, use_system2, ai_action)` — combina todo, fuerza `action="respond_to_user"`, `target_subagent="speaker"`
9. `laws.verify_action(law_action)` — si viola leyes, marca `reason="law_violation_overridden_for_user_response"` (override para responder al usuario)
10. `_act_v3(decision, observations, surprise, winners)` — ejecuta con el sub-agente ganador
11. `_broadcast_to_subagents(winners, decision, surprise)` — Global Workspace broadcast
12. Mutación `respond_to_user` con metadata extra: `system, winners, surprise`. `cost=0.60, confidence=0.55` (L3_DEEP) o `cost=0.85, confidence=0.50` (L3_MAXIMUM)

### 7.3 Estadísticas recopiladas (`get_stats` L638-671)

```python
stats["acd_classifications"]           # total
stats["acd_level_counts"]              # {L0: N, L1: N, L2: N, L3: N, L3_MAX: N}
stats["acd_cache_hits"]                # total
stats["acd_responses_by_level"]        # por nivel
stats["acd_latency_by_level"]          # {L0: {count, avg_ms, min_ms, max_ms, p50_ms}, ...}
stats["depth_classifier_stats"]        # level_distribution, level_percentages
stats["cognitive_cache_stats"]         # size, hits, misses, hit_rate, evictions
stats["acd_router_stats"]              # enabled, swaps, skips, last_routed_tag, active_profile.name
# + stats heredados de V4/V3/V05: iterations, thoughts, energy, fatigue, law_violations, 
#   workspace_competitions, system1_uses, system2_uses, memory_stats, etc.
```

---

## 8. DepthClassifier — las 5 señales de detección

Archivo: `core/depth_classifier.py` (384 LOC)

### 8.1 Los 5 niveles (`CognitiveLevel(str, Enum)` L34-57)

| Nivel | numeric | cost | default_confidence | Sub-agentes | Tiempo objetivo |
|---|---|---|---|---|---|
| L0_REFLEX | 0 | 0.05 | 0.95 | Ninguno (tabla refleja) | <1ms |
| L1_FAST | 1 | 0.10 | 0.80 | 3 (Perceiver, Memorialist, Speaker) | 2-4s |
| L2_STANDARD | 2 | 0.30 | 0.65 | 4 + Critic | 6-10s |
| L3_DEEP | 3 | 0.60 | 0.55 | 12 + meta-cog | 15-30s |
| L3_MAXIMUM | 4 | 0.85 | 0.50 | 12 + Qwen 72B | 30-60s+ |

### 8.2 Las 5 señales de detección (función `classify` L210-341)

**Señal 1 — Token exacto L0** (L231-247):
- `_L0_TOKENS` set (L83-96) con 38 tokens: `hola, holaa, hello, hi, hey, buenas, adios, chao, bye, ok, vale, venga, bien, genial, perfecto, entendido, claro, sip, sí, si, no, nop, gracias, thanks, denada, k, kk, jeje, jaja, lol, xD, xd...`
- Si `normalized.lower().rstrip(".!? ") in _L0_TOKENS` → `L0_REFLEX, score=0.05`
- Si `first_word in _L0_TOKENS AND len <= 25` → `L0_REFLEX, score=0.10`

**Señal 2 — Keywords L3** (L249-254):
- `_L3_KEYWORDS` set (L99-124) con ~50 palabras: `analiza, analizar, causas, consecuencias, porque, razones, fundamentamento, explica, justifica, compara, evalúa, valora, critica, dilema, ético, moral, debería, correcto, incorrecto, responsabilidad, principios, diseña, propón, crea, inventa, brainstorm, investiga, sintetiza, resume, comprende, profundiza, hipótesis, predice, predicción, escenarios, futuro, metodología, rigor, sesgo, validez, fiabilidad, evidencia, pruebas`
- Cada hit: `score += min(0.4, 0.15 * len(hits))`

**Señal 3 — Longitud** (L278-288):
- `len > 200`: `score += 0.2`
- `len > 100`: `score += 0.1`
- `len <= 80 (l1_max_length)`: `score += 0.05`

**Señal 4 — Puntuación compleja** (L290-299):
- `text.count("?") >= 2`: `+0.1` (multi_question)
- `";" in text`: `+0.05` (semicolon)
- `text.count("\n") >= 2`: `+0.1` (multiline)

**Señal 5 — Estructura (regex patterns)**:

`_L3_MAXIMUM_PATTERNS` (L150-155, 4 regex):
- `compara.+(documento|contrato|opción|caso|alternativa)`
- `compara\s+\d+\s+(contratos|documentos|opciones|alternativas|casos)`
- `(diagnóstico|diagnostico)\s+(diferencial|diferencia)`
- `(jurídico|médico|financiero).+(analysis|análisis|informe)`

`_L3_PATTERNS` (L167-173, 5 regex):
- `(si|si no|en caso de).+(entonces|debería|podría)`
- `(ventajas|desventajas|pros|contras)`
- `(primero|segundo|tercero|finalmente).+(primero|segundo|tercero|finalmente)` — listas numeradas
- `(por un lado|por otro lado|sin embargo|no obstante|aunque)`
- `\d+\.\s.+\n\d+\.\s` — lista numerada con 2+ items

### 8.3 Lógica de decisión (L307-341)

```python
force_l3_max = bool(l3_max_hits) or l3_max_pattern_hit
force_l3 = bool(l3_hits)

if force_l3_max and (length > 80 or l3_max_pattern_hit):
    level = L3_MAXIMUM; score = max(score, 0.85)
elif force_l3_max:
    level = L3_MAXIMUM; score = max(score, 0.75)
elif force_l3 and length > 80:
    level = L3_DEEP; score = max(score, 0.7)
elif force_l3:
    level = L3_DEEP; score = max(score, 0.5)
elif score >= 0.5:
    level = L3_DEEP
elif score >= 0.25:
    level = L2_STANDARD
elif score >= 0.10:
    level = L1_FAST
else:
    level = L1_FAST if length <= 80 else L2_STANDARD
```

**Cache key** (`_cache_key`, L367-372): `sha256(normalized.encode("utf-8")).hexdigest()`. **Latencia objetivo:** `<50ms` por clasificación.

---

## 9. ModelDownloader y ModelProfileRouter

### 9.1 Catálogo `OPTIMIZED_MODELS` (`model_downloader.py:76-203`) — 9 modelos

| Key | display_name | params_b | quant | size_gb | hf_repo | recommended_ram | tokens/s |
|---|---|---|---|---|---|---|---|
| `qwen2.5:32b-iq2` | Qwen 2.5 32B (IQ2_M) | 32 | IQ2_M | 12.5 | mradermacher/Qwen2.5-32B-Instruct-GGUF | 8GB | 3-6 |
| `qwen2.5:32b-iq3` | Qwen 2.5 32B (IQ3_XS) | 32 | IQ3_XS | 16.0 | mradermacher/Qwen2.5-32B-Instruct-GGUF | 8GB | 2-5 |
| `qwen2.5:72b-iq2` | Qwen 2.5 72B (IQ2_M) | 72 | IQ2_M | 25.0 | mradermacher/Qwen2.5-72B-Instruct-GGUF | 8GB | 1-3 |
| `llama3.1:70b-iq2` | Llama 3.1 70B (IQ2_M) | 70 | IQ2_M | 25.0 | mradermacher/Meta-Llama-3.1-70B-Instruct-GGUF | 8GB | 1-3 |
| `deepseek-r1:32b-iq2` | DeepSeek R1 32B (IQ2_M) | 32 | IQ2_M | 12.5 | mradermacher/DeepSeek-R1-Distill-Qwen-32B-GGUF | 8GB | 3-6 |
| `qwq-32b-iq2` | QwQ-32B (IQ2_M) | 32 | IQ2_M | 12.5 | bartowski/QwQ-32B-GGUF | 8GB | 3-6 |
| `qwen2.5-coder-32b-iq2` | Qwen 2.5 Coder 32B (IQ2_M) | 32 | IQ2_M | 12.5 | bartowski/Qwen2.5-Coder-32B-Instruct-GGUF | 8GB | 3-6 |
| `gemma-2-9b-iq2` | Gemma 2 9B (IQ2_M) | 9 | IQ2_M | 3.5 | bartowski/gemma-2-9b-it-GGUF | 4GB | 15-25 |
| `agents-a1-iq2` | Agents-A1 35B MoE (IQ2_M) | 35 | IQ2_M | 11.7 | KikoCis/Agents-A1-IQ2_M-GGUF | 8GB | 5-10 |

### 9.2 `SETUP_PRESETS` (`model_downloader.py:529-554`) — 4 setups

```python
SETUP_PRESETS = {
    "minimal":  {"models": ["gemma-2-9b-iq2"],
                 "total_gb": 3.5,  "min_ram_gb": 4.0},
    "balanced": {"models": ["gemma-2-9b-iq2", "qwq-32b-iq2"],
                 "total_gb": 16.0, "min_ram_gb": 8.0},
    "complete": {"models": ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2"],
                 "total_gb": 27.7, "min_ram_gb": 8.0},
    "maximum":  {"models": ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"],
                 "total_gb": 52.7, "min_ram_gb": 8.0},
}
```

### 9.3 `generate_modelfile` (`_generate_modelfile`, L398-420)

```python
return f"""# Modelfile para {model.display_name}
FROM {gguf_path}

PARAMETER num_ctx 2048
PARAMETER num_predict 512
PARAMETER num_parallel 1

TEMPLATE "{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>"

SYSTEM "Eres ZOE, un organismo cognitivo sintético."
"""
```

**Parámetros optimizados Mac 8GB**: `num_ctx=2048, num_predict=512, num_parallel=1`. Plantilla Qwen 2.5 (`<|im_start|>`).

### 9.4 `detect_installed_models` (`model_profile_router.py:153-190`)

```python
def detect_installed_models(self, models_dir: str) -> List[str]:
    installed = []
    models_path = Path(models_dir)
    # 1. Verificar archivos .gguf en el directorio
    for key, model in self._optimized_models.items():
        gguf_path = models_path / model.hf_filename
        if gguf_path.exists():
            installed.append(key)
    # 2. Verificar modelos registrados en Ollama
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        for key, model in self._optimized_models.items():
            if model.ollama_tag in result.stdout and key not in installed:
                installed.append(key)
    self._installed_models = installed
    return installed
```

### 9.5 `FALLBACK_CHAINS` (`model_profile_router.py:139-145`)

```python
FALLBACK_CHAINS = {
    "L0_REFLEX":    ["gemma-2-9b-iq2", "pattern"],
    "L1_FAST":      ["gemma-2-9b-iq2", "qwen2.5:32b-iq2", "pattern"],
    "L2_STANDARD":  ["agents-a1-iq2", "qwen2.5:32b-iq2", "deepseek-r1:32b-iq2", "gemma-2-9b-iq2", "pattern"],
    "L3_DEEP":      ["qwq-32b-iq2", "deepseek-r1:32b-iq2", "qwen2.5:32b-iq2", "agents-a1-iq2", "pattern"],
    "L3_MAXIMUM":   ["qwen2.5:72b-iq2", "llama3.1:70b-iq2", "qwq-32b-iq2", "qwen2.5:32b-iq2", "pattern"],
}
```

### 9.6 `DEFAULT_ASSIGNMENTS` (`model_profile_router.py:110-136`)

```python
DEFAULT_ASSIGNMENTS = {
    "L0_REFLEX":    {"preferred": "gemma-2-9b-iq2",   "fallback": "pattern"},
    "L1_FAST":      {"preferred": "gemma-2-9b-iq2",   "fallback": "pattern"},
    "L2_STANDARD":  {"preferred": "agents-a1-iq2",    "fallback": "qwen2.5:32b-iq2"},
    "L3_DEEP":      {"preferred": "qwq-32b-iq2",      "fallback": "qwen2.5:32b-iq2"},
    "L3_MAXIMUM":   {"preferred": "qwen2.5:72b-iq2",  "fallback": "qwq-32b-iq2"},
}
```

### 9.7 `create_optimal_profile` (`model_profile_router.py:192-278`)

Para cada nivel ACD en `ACDLevel` enum, recorre `FALLBACK_CHAINS[acd_level]` y asigna el PRIMER modelo disponible. Si ninguno disponible → `pattern` (PatternSpeaker). Si `installed_models` vacío → todos a `pattern`.

---

## 10. Sub-agentes — los 12 agentes (Society of Mind)

Directorio: `core/subagents/` (1.168 LOC, 5 archivos)

### 10.1 Los 12 sub-agentes

| # | Sub-agente | Archivo | LOC | Rol |
|---|---|---|---|---|
| 1 | `Perceiver` | `perceiver.py` | 84 | Interpreta observaciones |
| 2 | `Forecaster` | `forecaster.py` | 65 | Predice siguiente estado |
| 3 | `Speaker` | `speaker.py` | 236 | Genera output verbal (usa LLM) |
| 4 | `Critic` | `critic.py` | 180 | Evalúa acciones propuestas |
| 5 | `Memorialist` | `phase2_subagents.py:30` | — | Decide qué recordar |
| 6 | `Learner` | `phase2_subagents.py:95` | — | Extrae patrones |
| 7 | `Curator` | `phase2_subagents.py:170` | — | Cuida calidad del conocimiento |
| 8 | `Creativity` | `phase2_subagents.py:240` | — | Genera ideas nuevas |
| 9 | `CausalEngine` | `phase2_subagents.py:310` | — | Razona causa-efecto |
| 10 | `EmotionalMotor` | `phase2_subagents.py:380` | — | Color emocional |
| 11 | `EthicalMotor` | `phase2_subagents.py:450` | — | Principios éticos |
| 12 | `ScientificEngine` | `phase2_subagents.py:520` | — | Método científico |

### 10.2 API común

Todos los sub-agentes implementan:

```python
async def generate_thought(context: Dict[str, Any]) -> str:
    """Genera un pensamiento dado un contexto."""
```

El `context` dict típico incluye: `observations, surprise, prediction, relevant_memories, physics_summary, tensions_summary, perceived_intent, acd_level`.

### 10.3 Speaker — el agente que usa el LLM

`Speaker` (`speaker.py:67`) tiene:

```python
class Speaker:
    def __init__(self, llm_peripheral=None, max_thought_length=300):
        self.llm = llm_peripheral  # ← ATENCIÓN: atributo 'llm', no 'llm_peripheral'
        self.max_thought_length = max_thought_length
        self._recent_thoughts: List[str] = []
        self._specialized_prompts: Dict[str, str] = {}  # de cápsulas
        self._validators: Dict[str, ModuleType] = {}    # de cápsulas

    def set_llm(self, llm_peripheral) -> None:
        self.llm = llm_peripheral

    async def generate_thought(self, context: Dict) -> str:
        prompt = self._build_prompt(context, action)
        if not self.llm:
            return self._template_thought(context, action)  # fallback sin LLM
        thought = await self.llm.generate(prompt, system, max_tokens=self.max_thought_length)
        thought = self._sanitize(thought)
        # Evitar repetición
        if thought in self._recent_thoughts[-10:]:
            thought = await self.llm.generate(prompt, system, max_tokens=...)  # regenerar
        self._recent_thoughts.append(thought)
        return thought
```

**Punto crítico (Sprint 5.7.2 fix):** el atributo se llama `self.llm`, NO `self.llm_peripheral`. El ACD Router en `cognitive_loop_v5.py:184` busca el atributo correcto:

```python
llm_attr = getattr(speaker, "llm", None) or getattr(speaker, "llm_peripheral", None)
```

### 10.4 GlobalWorkspace — competencia de propuestas

`GlobalWorkspace` (`core/global_workspace.py:181`):

- `submit(proposal: Proposal)` — los 12 sub-agentes envían propuestas
- `compete() -> List[Proposal]` — selecciona ganadores por scoring (salience × relevance × novelty)
- `broadcast(winners, decision, surprise)` — difunde a todos los sub-agentes
- `broadcast_capacity` (default 3, ajustable por OntogeneticMotorV2)

### 10.5 MetaCognition — System 1 vs System 2

`MetaCognition` (`core/meta_cognition.py:172`) implementa el modelo Kahneman:

- `should_deliberate(surprise, stakes, energy) -> bool` — decide System 1 (rápido) vs System 2 (profundo)
- Thresholds: `confidence_threshold_system2=0.5, stakes_threshold_system2=0.7, energy_threshold_system2=0.4`
- Si `surprise > 0.5 AND stakes > 0.7 AND energy > 0.4` → System 2 (deliberate)
- Else → System 1 (intuitive)

---

## 11. Capsules — arquitectura, loader, manager, registry

Directorio: `capsules/` (4.328 LOC)

### 11.1 Estructura de una cápsula

```
capsules/<name>/
├── capsule.yaml              # Manifiesto (schema validado)
├── semantic_memory.jsonl     # Hechos y conceptos
├── procedural_skills.jsonl   # Habilidades
├── causal_models.jsonl       # Causa-efecto
├── emotional_patterns.jsonl  # Patrones afectivos
├── ethical_guidelines.jsonl  # Directrices éticas
├── validators.py             # Validadores Python (opcional)
├── tools/                    # Herramientas ejecutables (opcional)
│   └── *.py
└── prompts/                  # Prompts especializados (opcional)
    └── *.md
```

### 11.2 Schema de `capsule.yaml` (`schema.py:33-79`)

```yaml
name: snake_case            # REQUIRED
version: X.Y.Z semver       # REQUIRED
description: str            # REQUIRED
domain: dotted.path         # REQUIRED (ej: "healthcare.elders.home_care")
trust_level: enum           # REQUIRED: verified | curated | community | experimental
provenance: str             # REQUIRED (fuente)
last_updated: YYYY-MM-DD    # REQUIRED
content_hash: optional      # sha256:hex (lo calcula loader)
depends_on: [capsule_name]
compatible_use_cases: [use_case_name]
load_cost: 0.0-1.0          # default 0.15
default_confidence: 0.0-1.0 # si None, se deriva de trust_level
components:                 # 8 flags
  semantic_memory: bool
  procedural_skills: bool
  causal_models: bool
  emotional_patterns: bool
  ethical_guidelines: bool
  validators: bool
  tools: bool
  prompts: bool
capabilities: [str]
restrictions: [str]
expires_at: optional
```

**TrustLevel → confianza base** (`TRUST_TO_CONFIDENCE` L25-30):
- `VERIFIED` → 0.95
- `CURATED` → 0.80
- `COMMUNITY` → 0.55
- `EXPERIMENTAL` → 0.40

### 11.3 Las 15 cápsulas

| # | Cápsula | trust_level | dominio | depends_on | entries |
|---|---|---|---|---|---|
| 1 | `base_ethics` | verified | ethics.general | — | — |
| 2 | `zoe_basal_knowledge` | verified | zoe.basal | — | 32 |
| 3 | `basic_psychology` | curated | psychology.general | — | 49 |
| 4 | `communication_skills` | curated | communication.empathy | — | — |
| 5 | `elder_care_knowledge` | verified | healthcare.elders.home_care | basic_psychology | 54 |
| 6 | `elder_care_skills` | verified | healthcare.elders.tools | elder_care_knowledge | — |
| 7 | `pharmacy_interactions` | verified | healthcare.pharmacology | — | — |
| 8 | `company_loneliness_knowledge` | verified | psychology.loneliness.grief | basic_psychology, communication_skills | — |
| 9 | `b2c_assistant_growth` | curated | b2c.user_modeling | basic_psychology | — |
| 10 | `ia_heredable_legal` | curated | legal.digital_inheritance | — | — |
| 11 | `vigilance_devops_knowledge` | curated | tech.devops.monitoring | — | — |
| 12 | `research_methodology` | verified | science.methodology | — | — |
| 13 | `federation_b2b_skills` | verified | tech.federation.b2b | — | — |
| 14 | `multimodal_perception` | curated | perception.multimodal | base_ethics | — |
| 15 | `language_patterns` | verified | language.patterns | zoe_basal_knowledge | — |

### 11.4 CapsuleLoader (`loader.py:64`, 355 LOC)

**API:**
- `list_available() -> List[str]` — lista subdirectorios con `capsule.yaml`
- `load_for_use_case(use_case_name, config) -> List[LoadedCapsule]`
- `_load_capsule(name) -> Optional[LoadedCapsule]` (L150)
- `_load_jsonl(path) -> List[Dict]` — JSON Lines con tolerancia a errores
- `_load_python_module(path, module_name)` — `importlib.util.spec_from_file_location`
- `_load_tools(tools_dir)` — escanea `*.py`, instancia clases con `execute()` o `run()`
- `_load_prompts(prompts_dir)` — `*.md` → dict `{stem: content}`
- `_resolve_dependencies(capsules, loaded_names)` — carga `depends_on` recursivo
- `_check_circular_deps` — DFS con stack, lanza `CapsuleLoadError` si ciclo
- `_topological_sort` — dependencias primero
- `compute_content_hash(cap) -> str` — `sha256` de name+version+todas las entries

### 11.5 CapsuleManager (`core/capsule_manager.py:47`, 502 LOC)

**Cómo inyecta en el organismo** (`_inject` L142-374):

1. **LivingMemory** (L160-203): inyecta `semantic_memory` y `procedural_skills` con `provenance=f"capsule:{name}"`
2. **CausalEngine** (L205-214): `add_prevalidated_model(model)` por cada causal_model
3. **EmotionalMotor** (L216-225): `add_pattern(pattern)`
4. **EthicalMotor** (L227-236): `add_guideline(guideline)`
5. **Validators** (L238-253): `Speaker.register_validators(name, validators_module)`, `Learner.register_validators(name, validators_module)`
6. **EpistemicValidator** (L255-266): `Learner.set_epistemic_validator(validator, quarantine)` — solo la primera vez
7. **Quarantine injection** (L268-306): `Curator.set_quarantine`, `DeepConsolidation.set_quarantine`, `Critic.set_quarantine`
8. **Tools** (L308-316): `ActuatorManager.register_tool(tool)`
9. **Prompts** (L318-326): `Speaker.add_specialized_prompt(name, content)`
10. **EpistemicValidator source** (L328-331): si `trust_level==VERIFIED`, registra `source_trust[f"capsule:{name}"] = effective_confidence`
11. **Mutación firmada** (L333-355): `OntogeneticMotorV2.propose_mutation(type="capsule_loaded", target="memory", payload={capsule, version, trust_level, entries_loaded, components_injected})` + `apply_mutation`. El hash se devuelve como `trajectory_hash`.

**`unload(name)`** (L376-418): elimina entries por ID de memoria + mutación `capsule_unloaded`.

### 11.6 CapsuleRegistry (`registry.py:19`, 141 LOC)

- `_refresh_index()` — lee todos los `capsule.yaml` al inicializar
- `list_all() -> List[CapsuleMeta]`
- `get(name)`, `by_domain(prefix)`, `by_use_case(name)`, `by_trust_level(level)`
- `capabilities_for(name) -> List[str]`
- `check_compatibility(capsule_name, use_case) -> Tuple[bool, str]`
- `get_dependency_tree(name) -> Dict` — árbol recursivo
- `stats() -> Dict` — `total_capsules, by_trust_level, by_top_domain`

---

## 12. Peripherals — LLM, ModelBus, multimodal, voz, Telegram

Directorio: `peripherals/` (5.470 LOC)

### 12.1 LLMPeripheral jerarquía (`llm.py`, 660 LOC)

Clase abstracta base `LLMPeripheral(ABC)` (L31):

```python
class LLMPeripheral(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None,
                       max_tokens: int = 300, temperature: float = 0.7) -> str: ...
    
    async def generate_streaming(self, prompt, system, max_tokens, temperature) -> AsyncIterator[str]:
        # default: divide por palabras
        full = await self.generate(prompt, system, max_tokens, temperature)
        for word in full.split(" "):
            yield word + " "
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    async def health_check(self) -> bool:
        return True
```

**6 backends concretos:**

| Clase | LOC | Backend | Streaming | API key |
|---|---|---|---|---|
| `MockPeripheral` (L87) | 41 | Determinístico (rotación) | Sí (split palabras) | — |
| `OllamaPeripheral` (L131) | 100 | Local Ollama HTTP `/api/generate` (NDJSON) | Sí real | — |
| `OpenAICompatiblePeripheral` (L232) | 122 | OpenAI / DeepSeek / Groq / Kimi (`/chat/completions` SSE) | Sí real | `OPENAI_API_KEY` |
| `AnthropicPeripheral` (L355) | 144 | Claude (`/v1/messages`, headers `x-api-key`+`anthropic-version`) | Sí real SSE | `ANTHROPIC_API_KEY` |
| `ZAIPeripheral` (L500) | 112 | z-ai CLI (`subprocess.run` en thread pool) | No | — |
| `PatternPeripheral` | 292 | Sin LLM, patrones + memoria | Sí (delay 20ms/palabra) | — |

**Factory:** `create_llm_peripheral(config: Dict)` (L613-661) — backends: `mock, pattern, ollama, openai/openai_compatible, anthropic, zai`.

### 12.2 PatternPeripheral (`pattern_speaker.py:134`, 292 LOC)

**Cómo funciona sin LLM:**

1. **Intent classification** (`classify_intent` L59, `<1ms`): 9 intents con keywords — `greeting, farewell, gratitude, identity, wellbeing, help, emotion, question, statement`
2. **Refine emotion** (`_refine_emotion_intent` L249): sad/happy/worried
3. **Memory retrieval** (L192-196): `self._memory.search(prompt, n=1)` → si `similarity>0.6` reutiliza
4. **Reflex map** (L199-202): si hay `language_profile.reflex_map[prompt]` devuelve directo
5. **Template selection** (`RESPONSE_TEMPLATES` L73-127): 11 categorías con 2-4 templates cada una
6. **Template filling** (`_fill_template` L266): solo reemplaza `{context}`

### 12.3 EnhancedPatternPeripheral (`enhanced_pattern_speaker.py:424`, 599 LOC)

Hereda de PatternPeripheral. **3 capas nuevas:**

1. **ResponseDistillation** (`ResponseDistiller` L89):
   - `distill(input_text, response_text, source, quality_score, tags, domain)` → guarda en `distilled_responses.jsonl`
   - `retrieve(query, n=3, min_similarity=0.2)` → Jaccard similarity × quality_score

2. **CapsuleRetriever** (`CapsuleRetriever` L224):
   - Carga todos los `semantic_memory.jsonl` y `procedural_skills.jsonl` de TODAS las cápsulas
   - `retrieve(query, n=3, min_similarity=0.15)` → Jaccard sobre fact/content/description/skill_name/tags

3. **DialogStateTracker** (`DialogStateTracker` L337):
   - Recuerda: `_current_emotion, _current_topic, _pending_question, _turn_count, _history`
   - `get_context() -> Dict` con turn_count, current_emotion, current_topic, pending_question, last_intent

**Flujo `generate()` (L456-499):**
1. Intent classification + refine emotion
2. Buscar en distilled responses primero (calidad más alta, min_similarity=0.25)
3. Buscar en memoria (similarity>0.6)
4. Reflex map si disponible
5. Capsule knowledge + templates
6. Fallback a basic templates (PatternPeripheral)

### 12.4 ModelBus (`model_bus.py:95`, 577 LOC)

**Es un `LLMPeripheral` compuesto.** ZOE habla con el bus, no con un LLM directo.

**6 estrategias de selección** (`SelectionStrategy(str, Enum)` L52-59):
- `PRIORITY` — por priority (1-10)
- `ACD_AWARE` — scoring según ACD level
- `CHEAPEST` — menor cost_per_1k
- `FASTEST` — menor latency_ms
- `LOCAL_FIRST` — privacy=local primero
- `ROUND_ROBIN` — rotación

**`BackendEntry`** (L62-92): `peripheral, name, priority, cost_per_1k, latency_ms, privacy (local|network|cloud), streaming, available, max_tokens, max_fails=3, models, tags`

**API:**
- `add_backend(peripheral, name, priority, cost_per_1k, latency_ms, privacy, streaming, models, tags, max_tokens, max_fails)`
- `select_backend(acd_level, sensitive_domain, prefer_local) -> Optional[BackendEntry]`
- `generate(prompt, system, max_tokens, temperature, acd_level, sensitive_domain, prefer_local)` — fallback automático si falla (max 3 fails → mark unavailable)
- `from_resource_graph(resource_graph)` — classmethod
- `get_stats()`

### 12.5 Multimodal (`multimodal.py`, 636 LOC)

- **`VLMPeripheral`** (L41): visión con GPT-4o / Claude / LLaVA. `generate(prompt, images: List[bytes], system, max_tokens, temperature)`. NO hereda de LLMPeripheral. 3 métodos: `_generate_openai_vision` (base64 inline), `_generate_anthropic_vision`, `_generate_ollama_vision`
- **`VisionSense(Sense)`**: inyecta imágenes `_pending_images`, las procesa con VLM y produce `Observation(source="vision")`
- **`VoiceInputSense(Sense)`**: STT con Whisper (`whisper.load_model("base")`). `inject_audio(bytes, format)`, `start_listening(duration=5.0, sample_rate=16000)` con sounddevice. Lazy loading
- **`VoiceActuator(Actuator)`**: TTS con Piper (CLI externo). `execute(action)` → genera WAV desde texto. Lazy loading

### 12.6 VoiceFirstMode (`voice_first.py`, 797 LOC)

Conversación natural "Hey ZOE":

- `VoiceState(Enum)`: IDLE, LISTENING, PROCESSING, SPEAKING, INTERRUPTED
- `VoiceConfig`: wake_word="hey zoe", sensitivity, VAD aggressiveness, silence_duration, max_recording, stt_model="base", tts_voice="es_ES-davefx-medium"
- `WakeWordDetector` (openWakeWord o fallback energía)
- `VoiceActivityDetector` (webrtcvad)
- `InterruptionHandler` (detiene TTS si usuario habla)

### 12.7 TelegramBridge (`telegram_bridge.py:35`, 359 LOC)

Modos: `"api"` (vía REST a `http://localhost:8642/chat`) o `"direct"` (instancia `ZoeChat` interna).

Handlers: `/start, /help, /stats, /sleep, /wake`, texto, VOICE (transcribe con Whisper), PHOTO (envía a VLM). Filtrado por `allowed_user_ids`.

---

## 13. Epistemic validation, cuarentena, federación

### 13.1 EpistemicValidator (`core/epistemic_validator.py`, 399 LOC)

- `ValidationStatus(Enum)`: VERIFIED, UNVERIFIED, CONTRADICTED, QUARANTINED
- `validate(claim: str, source: str, confidence: float) -> ValidationResult`
- Comprueba: source_trust, contradictions en memoria, cuarentena activa
- Si confidence < 0.3 → QUARANTINED

### 13.2 KnowledgeQuarantine (`core/knowledge_quarantine.py`, 283 LOC)

- `QuarantineEntry`: id, claim, source, timestamp, timeout_days, status
- `add(claim, source, timeout_days=30)` → entry pending
- `filter_safe(critical_context: bool = False) -> List[QuarantineEntry]` — devuelve verified + quarantined (si no crítico)
- `promote(entry_id)` → mueve a verified
- `reject(entry_id)` → eliminado
- Stats: pending_count, expired_count, promoted_count, rejected_count

### 13.3 CrossValidator (`core/cross_validator.py`, 324 LOC)

- `CrossVerificationResult`: claim, sources, agreement_score, verdict
- `verify(claim, sources: List[str]) -> CrossVerificationResult`
- Si 2+ fuentes confirman → agreement_score alta
- Si fuentes contradictorias → agreement_score baja

### 13.4 EpistemicFederation (`core/epistemic_federation.py`, 328 LOC)

- `KnowledgeValidationRequest`: claim, requester_id, timestamp
- `KnowledgeValidationResponse`: claim, validator_id, verdict, confidence, timestamp
- `EpistemicFederation`: registry de peers, `request_validation(claim)`, `handle_validate_request(request)`

### 13.5 EpistemicFederationServer (`core/epistemic_federation_server.py`, 351 LOC)

- `PeerEndpoint`: url, id, public_key, last_seen, trust_score
- Server HTTP para recibir validation requests de otros ZOEs
- Client para enviar requests a peers
- Endpoints REST: `/federation/epistemic/validate`, `/federation/epistemic/register`, `/federation/epistemic/peers`

---

## 14. CLI y Dashboard — 71 endpoints

### 14.1 `cli_chat.py` (927 LOC) — `ZoeChat` class (L37)

**`initialize()` (L71-345):** Orquesta la creación de TODO el organismo:

1. Carga config de `use_case` YAML si existe (L112-119)
2. Crea `LLMPeripheral` vía `create_llm_peripheral(llm_config)` (L122-145)
3. Crea componentes Fase 0: `InternalState, WorldModel, [ClockSense, UserInputSense], Speaker(llm), [Perceiver, Forecaster, Speaker, Critic]` (L150-154)
4. Crea componentes Fase 0.5: `CognitiveLaws, CognitivePhysics, CognitiveFields, CognitiveTensions, LivingMemory(max_entries=5000), IntentionalityMotor, PhylogeneticMotor` (L156-163)
5. Crea componentes Fase 1: `IdentityVault, TrajectoryChain, OntogeneticMotorV2, Metabolism` (L165-170)
6. Inicializa 11 Memory Types con entries de bootstrap (L172-173)
7. Crea `ActuatorManager` + `LanguageActuator` (L175-176)
8. Crea componentes Fase 2: `WorldModelV2, ActiveInferenceLoop, MetaCognition, GlobalWorkspace` (L178-181)
9. Crea 8 sub-agentes Fase 2: `Memorialist, Learner, Curator, Creativity, CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine` (L183-190)
10. Crea `PersistentMemoryStore(db_path, auto_save_interval=20)` + `PersistentLivingMemory` + `DeepConsolidation` (L197-200)
11. Crea `DepthClassifier` + `CognitiveCache(max_size=100, ttl_seconds=300)` (L205-206)
12. Sprint 5.7: si `backend=="ollama" and model=="auto"`, crea `ModelProfileRouter`, detecta modelos en `$OLLAMA_MODELS`, crea `active_profile` (L211-233)
13. Instancia `CognitiveLoopV5` con TODOS los componentes inyectados (L235-267)
14. Fase 6A: crea `CapsuleManager, EpistemicValidator, KnowledgeQuarantine`, expone `curator/learner/critic_agent/causal_engine/emotional_motor/ethical_motor/scientific_engine` en el loop (L280-295)
15. Fase 6A P2: crea `EpistemicFederation, EpistemicFederationServer, EpistemicFederationClient` (L301-312)
16. Fase 6C: crea `MentorAgent` con config_path (L314-319)
17. Carga cápsula basal `zoe_basal_knowledge` SIEMPRE (L322-325)
18. Carga cápsulas del caso de uso si `--use-case` (L328-332)
19. `loop.initialize()` carga memoria desde disco (L335)
20. Arranca `_run_background` task que llama `loop.run()` (L339)
21. Registra callback `on_thought` para pensamientos autónomos (L342-345)

**`send_message_acd(message)` (L371-385):** Devuelve dict completo con metadata: `response, level, score, cache_hit, latency_ms, trajectory_hash, cost, confidence`.

**`send_message_streaming(message)` (L387-470):** AsyncIterator que yields `{"type": "metadata"|"chunk"|"done"|"error", ...}`.

**Comandos especiales:** `/stats, /memory, /state, /sleep, /wake, /identity, /feed <archivo>, /quit`.

### 14.2 `web_dashboard.py` (2.886 LOC) — `DashboardServer` class (L37)

**71 endpoints** registrados en `app.router.add_get/add_post`:

| Categoría | Endpoints | Cantidad |
|---|---|---|
| Core HTTP | `/`, `/ws`, `/chat`, `/feed`, `/stats`, `/memory`, `/identity`, `/state`, `/sleep`, `/wake`, `/llm`, `/history`, `/federation` | 13 |
| Capsules | `/api/capsules`, `/api/capsules/loaded`, `/api/capsules/load`, `/api/capsules/unload`, `/api/capsules/{name}/info`, `/api/capsules/{name}/validate`, `/api/capsules/create` | 7 |
| Federación epistémica | 6 endpoints | 6 |
| Cuarentena | 4 endpoints | 4 |
| Marketplace | 5 endpoints | 5 |
| Mentor | 3 endpoints | 3 |
| Models (Fase 7F) | 4 endpoints | 4 |
| Resources (Fase 7A) | 3 endpoints | 3 |
| ModelBus (Fase 7B) | 3 endpoints | 3 |
| Planner (Fase 7C) | 3 endpoints | 3 |
| Embodiment (Fase 7D) | 6 endpoints | 6 |
| Seed (Fase 7E) | 6 endpoints | 6 |
| Hardware (Fase 7G) | 4 endpoints | 4 |
| Router (Sprint 5.7.2) | `/api/router/stats`, `/api/router/installed`, `/api/router/profile` | 3 |
| PWA | `/manifest.json` | 1 |
| **TOTAL** | | **71** |

**WebSocket** (`_handle_websocket` L228-336):
- `msg_type == "chat"` → `chat.send_message_acd(message)` → envía `chat_response` con `acd_level, latency_ms, cache_hit, cost`
- `msg_type == "command"` → `_handle_command`
- `msg_type == "capsule_action"` → load/unload/list capsules, broadcast a TODOS los WS clients

**Broadcaster** (`_broadcast_loop`): cada 1s envía state update a todos los WS clients conectados.

### 14.3 Flujo: usuario → WS → loop → speaker → LLM

```
1. Usuario escribe en browser
   → JS envía {"type": "chat", "message": "..."} por WebSocket

2. DashboardServer._handle_websocket recibe (L247-281)

3. Llama self.chat.send_message_acd(message)
   → ZoeChat.send_message_acd (cli_chat.py:371)

4. ZoeChat.send_message_acd
   → self.loop.process_user_input_acd(message) (V5)

5. V5 clasifica con DepthClassifier.classify

6. V5 hot-swap del LLM según ACD Router si está activo
   (muta speaker.llm.model)

7. V5 ejecuta _process_lN según nivel
   → Speaker.generate_thought
   → self.llm.generate(prompt, system, ...)
   → Ollama/OpenAI/Anthropic/ZAI/Pattern

8. V5 registra mutación en TrajectoryChain (auditable)

9. V5 guarda en LivingMemory (user + response episódicos)

10. send_message_acd devuelve dict con response + metadata

11. DashboardServer envía chat_response por WebSocket con metadata ACD

12. JS del browser actualiza UI
```

---

## 15. Scripts de instalación y despliegue

### 15.1 `zoe-bootstrap.sh` (842 LOC) — Instalador todo-en-uno

8 pasos:
1. Detectar SSD o pendrive (macOS /Volumes, Linux /media, Windows drives D-Z)
2. Verificar formato del SSD (FAT32 bloqueado, APFS/exFAT/NTFS OK)
3. Verificar Python 3.10+ y Git (instrucciones si faltan)
4. Clonar ZOE en el SSD (manejo de repo privado con PAT)
5. Crear entorno virtual + `pip install -e .`
6. Configurar Ollama (instala si falta, retry 18s con backoff 3/5/10s)
7. Descargar modelos IQ2_M (4 setups: minimal/balanced/complete/maximum)
8. Configurar API keys cloud (opcional)
9. Crear lanzadores .command/.sh (con `--model auto`)
10. Eliminar atributo quarantine macOS (xattr)
11. Preguntar si arrancar Dashboard

### 15.2 `zoe_setup.py` (589 LOC) — Asistente interactivo

- `check_python, check_pip, check_git, check_ollama, check_api_keys, check_zoe_installed, check_zoe_data`
- `check_iq2_models(models_dir)` — verifica modelos IQ2_M instalados
- `recommend_iq2_setup(ram_gb, ssd_free_gb)` — recomienda setup según hardware
- CLI: `--check` (solo verificar), `--install` (instalar lo que falte), `--install-iq2-models <setup>`

### 15.3 `install_windows.ps1` (234 LOC) — Instalador Windows

6 pasos: verificar Python/Git, seleccionar disco, verificar formato SSD, instalar ZOE, configurar Ollama, crear lanzadores `.bat`.

### 15.4 `deploy.sh` (107 LOC) — Despliegue VPS Linux

6 pasos: verificar Python3+Ollama, crear `/opt/zoe/{data,logs}`, copiar código, `pip install`, `ollama pull qwen2.5:3b`, crear servicio systemd `/etc/systemd/system/zoe.service`.

### 15.5 `serve.py` (255 LOC) — Punto entrada producción

- Usa `CognitiveLoopV4` (sin ACD, modo autónomo)
- `--config config/production.yaml`
- Signal handlers SIGTERM/SIGINT
- Graceful shutdown

---

## 16. Tests y cobertura

### 16.1 Tests por módulo (LOC)

| Test | LOC | Valida |
|---|---|---|
| `test_full_system_integration.py` | 817 | Integración end-to-end |
| `test_phase6_capsules.py` | 721 | Carga/descarga/inyección de cápsulas |
| `test_phase6a_epistemic.py` | 647 | EpistemicValidator + KnowledgeQuarantine |
| `test_phase7e_seed_mode.py` | 627 | Seed mode (zoe-packager) |
| `test_phase5_acd.py` | 605 | ACD + CognitiveLoopV5 + cache |
| `test_integration_phase0_0_5.py` | 598 | Bucle V05 con 7 componentes |
| `test_phase7d_embodiment_composer.py` | 597 | Embodiment composer |
| `test_phase6b_marketplace.py` | 577 | Marketplace de cápsulas |
| `test_phase6a_curator_integration.py` | 525 | Curator con cuarentena |
| `test_sprint5_7_2_quickstart_audit.py` | 499 | Audit del quickstart |
| `test_phase3_4_5.py` | 483 | Fases 3, 4, 5 integradas |
| `test_sprint5_cognitive_optimization.py` | 470 | ZMAP prefetching |
| `test_phase7b_model_bus.py` | 462 | ModelBus con 6 estrategias |
| `test_phase4.py` | 444 | CognitiveLoopV4 + Federation + Config |
| `test_sprint5_5_model_downloader.py` | 438 | ModelDownloader + 9 modelos |
| `test_loop_v3.py` | 413 | CognitiveLoopV3 con 12 sub-agentes |
| `test_phase7c_resource_planner.py` | 396 | ResourcePlanner |
| `test_sprint5_7_acd_routing.py` | 392 | Hot-swap de modelos por ACD |
| `test_sprint4_voice_first.py` | 389 | VoiceFirstMode |
| `test_phase7g_hardware_endpoints.py` | 380 | Endpoints hardware |

**Total:** 54 archivos, 18.551 LOC, 526 tests.

### 16.2 Tests críticos que validan la arquitectura

- `test_identity_vault.py` (19 tests): hash inmutable, verify forbidden targets, from_dict lanza ValueError si hash mismatch
- `test_trajectory_ontogenetic.py` (20 tests): cadena verificable, rollback añade mutación (no elimina), OntogeneticMotorV2 mutaciones arquitecturales
- `test_cognitive_laws.py` (15 tests): 6 leyes, violations registrado, modularity replacement
- `test_phase5_acd.py:604-605`: `assert issubclass(CognitiveLoopV5, CognitiveLoopV4)` — backward compat
- `test_sprint5_7_acd_routing.py:136` (`TestCognitiveLoopV5Router`): valida hot-swap del LLM
- `test_phase6_capsules.py` (721 LOC): validación de schema, dependencias circulares, topological sort, inyección en componentes

### 16.3 Cobertura por módulo

| Módulo | Tests | Cobertura |
|---|---|---|
| ALMA (identity, trajectory, ontogenetic) | 59 tests | Alta |
| Memory (11 tipos, SQLite, consolidation) | 42 tests | Alta |
| Metabolism | 17 tests | Media |
| CognitiveLoop V05/V3/V4/V5 | 89 tests | Alta |
| DepthClassifier + ACD | 44 tests | Alta |
| ModelDownloader + Router | 42 tests | Alta |
| Capsules (loader, manager, registry) | 86 tests | Alta |
| LLM peripherals (6 backends) | 12 tests | Media |
| ModelBus | 32 tests | Alta |
| Epistemic validation + quarantine | 51 tests | Alta |
| Dashboard endpoints | 12 tests | Media |
| Sprint 5.7.x (router, audit) | 75 tests | Alta |

---

## 17. Puntos de extensión para contribuidores

### 17.1 Añadir nuevo sub-agente

1. Crear clase con método `async generate_thought(context: Dict) -> str` en `core/subagents/`
2. Añadir a `ALLOWED_TYPES` en `ontogenetic_motor_v2.py:178-182`
3. Añadir al `subagent_map` en `_add_subagent` (`ontogenetic_motor_v2.py:199-208`)
4. Importar e instanciar en `cli_chat.py:192-195` y `serve.py:158-161`

### 17.2 Añadir nueva cápsula

1. Crear directorio `capsules/<name>/` con `capsule.yaml` (usar `zoe-capsules create --name ...` scaffold)
2. Añadir componentes `.jsonl` y/o `validators.py`, `tools/`, `prompts/` según `components: true/false`
3. Añadir `compatible_use_cases` en el YAML
4. La cápsula se descubre automáticamente por `CapsuleRegistry._refresh_index()` — no requiere registro manual
5. Cargarla en runtime: `capsule_manager.load("<name>")` o vía endpoint `POST /api/capsules/load`

### 17.3 Añadir nuevo backend LLM

1. Crear clase que herede `LLMPeripheral` (`peripherals/llm.py:31`) implementando:
   - `name -> str` (property)
   - `async generate(prompt, system, max_tokens, temperature) -> str`
   - Opcional: `supports_streaming`, `generate_streaming`, `health_check`
2. Añadir rama en `create_llm_peripheral(config)` factory (`peripherals/llm.py:613-661`)
3. Para usarlo vía ModelBus: `bus.add_backend(MyPeripheral(), name=..., priority=..., cost_per_1k=..., privacy="local|network|cloud", streaming=True, tags=[...])`

### 17.4 Añadir nuevo endpoint REST

1. Añadir `app.router.add_get("/api/mi_endpoint", self._handle_mi_endpoint)` en `DashboardServer.start()` (`web_dashboard.py:87-193`)
2. Implementar método `async def _handle_mi_endpoint(self, request) -> Any` que devuelva `web.json_response({...})`
3. Para WebSocket events: usar `await self._broadcast_to_all({"type": "mi_evento", ...})`

### 17.5 Añadir nuevo tipo de memoria

1. Añadir entry al enum `MemoryType` en `memory/memory_types.py:30-43`
2. Añadir descripción en `MEMORY_TYPE_DESCRIPTIONS` (L47-59)
3. Crear dataclass heredando `MemoryEntry` con campos extra
4. Añadir entrada en `ENTRY_CLASSES` dict (L183-195)
5. Añadir lógica de consolidación en `memory/deep_consolidation.py` si procede
6. SQLite store es agnóstico al tipo (columna `type` TEXT) — no requiere migración

### 17.6 Añadir nuevo nivel ACD

1. Añadir entry al enum `CognitiveLevel` en `depth_classifier.py:34`
2. Añadir `numeric, cost, default_confidence` en las properties
3. Añadir entry en `level_distribution` dict del `__init__` (L205)
4. Añadir keywords/patrones específicos del nuevo nivel
5. Añadir lógica de decisión en `classify()` (L307-341)
6. Añadir entry en `DEFAULT_ASSIGNMENTS` y `FALLBACK_CHAINS` de `model_profile_router.py`
7. Añadir rama `elif level == NEW_LEVEL:` en `cognitive_loop_v5.py:226-247`

---

## 18. Decisiones arquitecturales clave (ADRs implícitos)

### ADR-1: Composición sobre herencia para sub-agentes

**Decisión:** Los 12 sub-agentes se inyectan en el bucle como objetos, no se heredan.

**Justificación:** Permite añadir/quitar sub-agentes en runtime vía `OntogeneticMotorV2.add_subagent`. Si fueran herencia, no se podría modificar la arquitectura sin reiniciar.

### ADR-2: Inmutabilidad del IdentityVault

**Decisión:** El hash SHA-256 del IdentityVault nunca cambia tras el nacimiento.

**Justificación:** Permite verificar la identidad de una ZOE en cualquier momento de su vida. Si el hash cambiara, no podrías saber si una ZOE es la "misma" que conociste.

### ADR-3: TrajectoryChain inmutable (blockchain)

**Decisión:** Las mutaciones no se eliminan, se anulan con `rollback_previous`.

**Justificación:** Auditoría completa. Puedes rastrear toda la historia de decisiones de una ZOE. Si se eliminaran, se perdería historia.

### ADR-4: ACD sin LLM

**Decisión:** El DepthClassifier es 100% heurístico (sin LLM), <50ms.

**Justificación:** Si clasificar costara una llamada a LLM, sería más lento que la respuesta misma. La clasificación debe ser instantánea para que el routing sea útil.

### ADR-5: Hot-swap mutando `.model` en vez de crear nuevo peripheral

**Decisión:** El ACD Router muta `speaker.llm.model = routed_tag` en vez de crear un `OllamaPeripheral` nuevo.

**Justificación:** Más rápido. Ollama recarga el modelo solo si hace falta (depende de `OLLAMA_KEEP_ALIVE`). Crear un peripheral nuevo implica reconstruir conexión HTTP.

### ADR-6: PatternSpeaker como fallback universal

**Decisión:** Si no hay LLM, PatternSpeaker responde. Si no hay modelo para un nivel ACD, fallback a pattern.

**Justificación:** ZOE nunca debe "no responder". PatternSpeaker garantiza respuesta siempre, aunque sea de menor calidad.

### ADR-7: mmap para modelos grandes en Mac 8GB

**Decisión:** Los Modelfiles incluyen `num_ctx 2048, num_predict 512, num_parallel 1` y los modelos IQ2_M están optimizados para mmap.

**Justificación:** Permite cargar modelos de 25GB en Mac con 8GB RAM. mmap solo carga en RAM las capas activas (~3-4GB), el resto vive en el SSD.

### ADR-8: SQLite para memoria persistente

**Decisión:** Una sola tabla `memory_entries` con columna `type` TEXT para los 11 tipos.

**Justificación:** Simplicidad. No requiere migraciones al añadir tipos. Los índices en `type, salience, timestamp` son suficientes para las queries actuales.

### ADR-9: Backward compatibility V5→V4

**Decisión:** `CognitiveLoopV5(CognitiveLoopV4)`. Si no se pasa `depth_classifier`, degrada a V4.

**Justificación:** Permite que `serve.py` siga usando V4 sin cambios. V5 es opt-in para CLI/Dashboard.

### ADR-10: Cápsulas auto-descubiertas vía filesystem

**Decisión:** `CapsuleRegistry._refresh_index()` escanea `capsules/*/capsule.yaml`.

**Justificación:** No requiere registro manual. Añadir una cápsula es tan simple como crear un directorio. Facilita el marketplace.

---

## 19. Diagrama de flujo de datos end-to-end

```
[Usuario]
   │
   ▼ (WebSocket "chat")
[DashboardServer] ──┐
   │                 │
   ▼                 ▼ (REST POST /chat)
[ZoeChat.send_message_acd]
   │
   ▼
[CognitiveLoopV5.process_user_input_acd]
   │
   ├─► [DepthClassifier.classify] → CognitiveLevel + score + reasons + cache_key
   │
   ├─► [ModelProfileRouter.get_model_for_acd] → ModelAssignment
   │       │
   │       └─► (hot-swap) Speaker.llm.model = routed_tag
   │
   ├─► [CognitiveCache.get(cache_key)] → hit? return cached
   │
   ├─► _process_lN según nivel:
   │       L0 → _L0_REFLEX_RESPONSES dict (sin LLM)
   │       L1 → Speaker.generate_thought (con memory.search n=3)
   │       L2 → Perceiver + Speaker + Critic (con memory.search n=5)
   │       L3 → WorldModelV2.predict_next + 12 subagentes _collect_proposals
   │            → GlobalWorkspace.compete → MetaCognition.should_deliberate
   │            → ActiveInference.select_action → _decide_v3 → _act_v3
   │            → _broadcast_to_subagents
   │
   ├─► [OntogeneticMotorV2.propose_mutation("respond_to_user")]
   │       │
   │       ├─► CognitiveLaws.verify_action (6 leyes)
   │       ├─► IdentityVault.verify (2da ley)
   │       └─► TrajectoryChain.commit(mutation) → hash firmado
   │
   ├─► [LivingMemory.add] x2 (User + ZOE, type="episodic")
   │       │
   │       └─► (auto-save cada 20 ops) PersistentMemoryStore.save_to_disk → SQLite
   │
   ├─► [CognitiveCache.put(cache_key, response, level)] si L0/L1
   │
   └─► return {response, level, score, cache_hit, latency_ms, trajectory_hash, cost, confidence}
       │
       ▼
[DashboardServer._handle_websocket] → ws.send_json({type:"chat_response", ...})
       │
       ▼
[Browser JS actualiza UI]

--- En paralelo (background task) ---
[CognitiveLoopV5.run] → cada tick_interval segundos:
   _tick() (V3 con V4/V5 extensiones):
     1. _observe (ClockSense, UserInputSense)
     2. WorldModelV2.predict_next
     3. WorldModelV2.compute_surprise
     4. _update_fields / _update_tensions / _update_physics
     5. _generate_intentions
     6. _memory_think (LivingMemory.think — 1 operación de consolidación ligera)
     7. metabolism.tick(dt) → si fatigue>0.8 → SLEEPING → DeepConsolidation.consolidate()
     8. _collect_proposals (12 sub-agentes → GlobalWorkspace)
     9. _workspace_compete
     10. _evaluate_meta_cognition (System 1 vs 2)
     11. _consult_active_inference
     12. _decide_v3
     13. laws.verify_action
     14. _act_v3 → Thought
     15. LivingMemory.add(type="episodic")
     16. _broadcast_to_subagents
     17. state.tick + state.stimulate si surprise>0.3
     18. auto_save cada 50 iteraciones
```

---

## 20. Deuda técnica y roadmap técnico

### 20.1 Deuda técnica identificada

| # | Deuda | Impacto | Esfuerzo |
|---|---|---|---|
| 1 | **TrajectoryChain usa SHA-256 simbólico, no ECDSA** | Bajo (auditable pero no criptográficamente seguro contra falsificación con clave privada) | Medio |
| 2 | **`serve.py` usa V4, no V5** | Medio (no aprovecha ACD ni routing en producción headless) | Bajo |
| 3 | **LivingMemory.search usa Jaccard, no embeddings** | Medio (búsqueda menos precisa) | Alto (requiere sentence-transformers) |
| 4 | **`merge_subagents` no implementado en OntogeneticMotorV2** | Bajo | Bajo |
| 5 | **5 módulos huérfanos** (cross_validator, cognitive_optimization, seed_mode, embodiment_composer, resource_planner) — solo vía REST | Medio (no integrados en el bucle activo) | Alto |
| 6 | **`test_phase6a_v12` esperaba 12 cápsulas** (arreglado en 5.7.3) | Resuelto | — |
| 7 | **CognitiveOptimization (ZMAP/CPL/TPE) no conectado por defecto** | Medio (Sprint 5 avanzado, opcional) | Medio |
| 8 | **No hay rate limiting en Dashboard** | Bajo (uso local) | Bajo |
| 9 | **No hay autenticación en Dashboard** | Medio (uso local, pero si se expone a red...) | Medio |
| 10 | **TrajectoryChain persistencia no implementada** (solo in-memory) | Alto (se pierde la cadena al reiniciar) | Medio |

### 20.2 Roadmap técnico sugerido

#### Sprint 5.8 — Persistencia y seguridad
- Persistir TrajectoryChain en SQLite (`trajectory_chain.db`)
- Implementar ECDSA en TrajectoryChain (`_sign` con clave privada del organismo)
- Autenticación básica en Dashboard (token o password)
- Rate limiting (token bucket)

#### Sprint 5.9 — Integración de módulos huérfanos
- Conectar `cognitive_optimization.py` (ZMAP/CPL/TPE) al bucle V5
- Conectar `resource_planner.py` al `process_user_input_acd` (alternativa al ModelProfileRouter)
- Conectar `cross_validator.py` al EpistemicValidator
- Migrar `serve.py` de V4 a V5

#### Sprint 5.10 — Búsqueda semántica
- Integrar `sentence-transformers` en LivingMemory.search
- Embeddings indexados en SQLite (columna `embedding BLOB`)
- Búsqueda por similitud coseno en vez de Jaccard
- Cache de embeddings (LRU)

#### Sprint 6 — Federation B2B real
- Implementar federation server HTTP real (no mock)
- Peer discovery (mDNS, DHT, o registry central)
- Conflict resolution en federación epistémica
- Quorum voting con veto por valores

#### Sprint 7 — Producción hardening
- Healthcheck endpoint (`/health`)
- Metrics endpoint (`/metrics` formato Prometheus)
- Structured logging (JSON)
- Distributed tracing (OpenTelemetry)
- Container Docker optimizado
- Helm chart para Kubernetes

### 20.3 Métricas de salud del proyecto

| Métrica | Valor | Estado |
|---|---|---|
| Tests | 526 (525 pasan, 1 obsoleto arreglado en 5.7.3) | ✅ |
| Cobertura | ~70% estimada | 🟡 |
| LOC | ~80.000 | ✅ |
| Deuda técnica | 10 items identificados | 🟡 |
| Documentación | 18 docs + REFERENCE/ | ✅ |
| Endpoints REST | 71 (todos 200 OK) | ✅ |
| Cápsulas | 15 operativas | ✅ |
| Modelos IQ2_M | 9 en catálogo, 4 setups | ✅ |
| Backends LLM | 6 (Mock, Ollama, OpenAI, Anthropic, ZAI, Pattern) | ✅ |
| Plataformas | macOS, Linux, Windows, Docker, K8s, PWA, Telegram | ✅ |

---

## Apéndice A — Comandos útiles para desarrollo

```bash
# Instalar en modo desarrollo
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e ".[test]"

# Ejecutar tests
pytest zoe/tests/ -v
pytest zoe/tests/test_sprint5_7_acd_routing.py -v  # solo routing

# Arrancar Dashboard
python -m zoe.web_dashboard --backend pattern

# Arrancar CLI
python -m zoe.cli_chat --backend pattern
python -m zoe.cli_chat --backend ollama --model auto  # con ACD Router

# Listar modelos IQ2_M disponibles
python -m zoe.core.model_downloader --list

# Detectar modelos instalados
python -m zoe.core.model_downloader --detect-installed --models-dir /Volumes/SSD/ZOE/models

# Descargar setup completo
python -m zoe.core.model_downloader --download-setup balanced

# Setup interactivo
python zoe/scripts/zoe_setup.py --check

# Crear nueva cápsula
zoe-capsules create --name mi_capsula --domain mi.dominio --trust-level experimental

# Empaquetar ZOE en .zoe
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().package('./mi_zoe.zoe')"

# Desempaquetar .zoe
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().unpackage('mi_zoe.zoe', './ZOE')"
```

---

## Apéndice B — Glosario técnico

| Término | Definición técnica |
|---|---|
| **ACD** | Adaptive Cognitive Depth. Clasificador heurístico que pre-clasifica inputs en 5 niveles antes de entrar al pipeline. |
| **ALMA** | Arquitectura de Layered Mutability & Auditability. IdentityVault + TrajectoryChain + OntogeneticMotor. |
| **BackendEntry** | Entrada en ModelBus con peripheral, priority, cost, latency, privacy, models, tags. |
| **CognitiveLevel** | Enum de 5 valores (L0_REFLEX, L1_FAST, L2_STANDARD, L3_DEEP, L3_MAXIMUM) con cost y confidence. |
| **FALLBACK_CHAINS** | Dict en ModelProfileRouter con orden de preferencia de modelos por nivel ACD. |
| **GlobalWorkspace** | Componente donde los 12 sub-agentes compiten por broadcast (Teoría de Baars). |
| **IQ2_M** | Importance Matrix Quantization 2-bit Medium. Compresión de GGUF que permite modelos 32B en 8GB RAM vía mmap. |
| **LLMPeripheral** | Clase abstracta con `async generate(prompt, system, max_tokens, temperature) -> str`. |
| **MetaCognition** | Sistema 1 vs System 2 (Kahneman) basado en surprise, stakes, energy. |
| **mmap** | Memory-mapped file. Permite leer archivos grandes desde disco sin cargarlos enteros en RAM. |
| **ModelAssignment** | Dataclass con acd_level, model_tag, model_key, reason, fallback. |
| **Mutation** | Dataclass en TrajectoryChain con type, target, payload, justification, provenance, cost, confidence, hash, prev_hash. |
| **OntogeneticMotorV2** | Permite a ZOE modificar su propia arquitectura en runtime (add/remove subagentes, ajustar thresholds). |
| **PatternPeripheral** | LLMPeripheral que genera respuestas sin LLM, usando patrones + memoria + templates. |
| **SETUP_PRESETS** | 4 setups preseleccionados (minimal/balanced/complete/maximum) con lista de modelos. |
| **TrajectoryChain** | Cadena inmutable de mutaciones firmadas (blockchain) que audita toda la vida de ZOE. |

---

## Apéndice C — Dónde encontrar más información

| Si quieres saber de... | Lee este documento |
|---|---|
| Visión general no técnica | `docs/18_ZOE_EXPLICACION_NO_TECNICOS.md` |
| Visión general técnica | `docs/01_ZOE_OVERVIEW.md` |
| Arquitectura profunda | `docs/02_ARCHITECTURE.md` |
| Cómo piensa (motor cognitivo) | `docs/03_COGNITIVE_ENGINE.md` |
| Memoria y aprendizaje | `docs/04_MEMORY_AND_LEARNING.md` |
| Validación epistémica | `docs/05_EPISTEMIC_VALIDATION.md` |
| Cápsulas de conocimiento | `docs/06_CAPSULES_GUIDE.md` |
| Cómo instalarla paso a paso | `docs/17_USER_INSTALLATION_GUIDE.md` |
| Optimización de hardware | `docs/10_HARDWARE_OPTIMIZATION.md` |
| Formato .zoe portátil | `docs/16_ZOE_FORMAT.md` |
| API REST completa | `docs/REFERENCE/API_REFERENCE.md` |
| Troubleshooting | `docs/13_TROUBLESHOOTING.md` |
| Guía de desarrollo | `docs/15_DEVELOPMENT_GUIDE.md` |
| Guía técnica CTO | `docs/ZOE_CTO_TECHNICAL_GUIDE.md` |
| Guía ejecutiva | `docs/ZOE_EXECUTIVE_GUIDE.md` |

---

*ZOE V1.8.0 — Documento técnico para equipo técnico y CTO*
*Julio 2026 — Sprint 5.7.3*
*"ZOE no es un modelo que responde. Es un organismo que existe."*

*Este documento ha sido verificado leyendo directamente los archivos en `/home/z/my-project/zoe-sco/zoe/`. Todas las clases, métodos, líneas, schemas y constantes referenciadas han sido verificadas contra el código fuente.*
