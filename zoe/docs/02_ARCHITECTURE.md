# 02 — Architecture

> **Arquitectura técnica profunda de ZOE, subsistema por subsistema.**
> **Audiencia:** arquitectos, CTO, Tech Leads, Staff Engineers.
> **Versión:** V1.6.0 — Julio 2026

---

## Tabla de contenidos

1. [Visión general](#1-visión-general)
2. [Diagrama de componentes](#2-diagrama-de-componentes)
3. [Subsistema ALMA](#3-subsistema-alma-identidad--trayectoria)
4. [Subsistema NÚCLEO (Cognitive Loop)](#4-subsistema-núcleo-cognitive-loop)
5. [Subsistema METABOLISMO](#5-subsistema-metabolismo)
6. [Subsistema MEMORIA](#6-subsistema-memoria)
7. [Subsistema PERIFÉRICOS](#7-subsistema-periféricos)
8. [Subsistema COGNITIVO (leyes, física, campos, tensiones)](#8-subsistema-cognitivo)
9. [Subsistema EPISTÉMICO](#9-subsistema-epistémico)
10. [Subsistema CÁPSULAS + MARKETPLACE](#10-subsistema-cápsulas--marketplace)
11. [Subsistema RECURSOS (Fases 7A-7G)](#11-subsistema-recursos-fases-7a-7g)
12. [Federación](#12-federación)
13. [Flujo de una petición](#13-flujo-de-una-petición)

---

## 1. Visión general

ZOE es un sistema modular con **9 subsistemas** que se comunican a través de interfaces bien definidas. Cada subsistema se puede usar y reemplazar independientemente. No hay acoplamiento innecesario.

### Principios arquitectónicos

1. **Composición sobre herencia**: los componentes se componen, no se heredan profundamente. `Metabolism` compone `InternalState`, no hereda de él.
2. **Inyección de dependencias**: cada componente recibe sus dependencias en el constructor. `CognitiveLoopV5` recibe `senses`, `world_model`, `subagents`, `state`, etc.
3. **Sin estado global**: no hay singletons ni variables globales (excepto `PhylogeneticPool` que es intencionalmente singleton para compartir mejoras entre ZOEs).
4. **Async-first**: el bucle cognitivo es async. Los LLMs soportan streaming async.
5. **Observabilidad**: cada componente tiene `to_dict()` y `summary()` para inspección.

---

## 2. Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ZOE — Synthetic Cognitive Organism           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ALMA (identity + trajectory)              │   │
│  │  ┌──────────────────┐  ┌────────────────────────────────┐  │   │
│  │  │  IdentityVault    │  │  TrajectoryChain (blockchain)  │  │   │
│  │  │  (SHA-256 hash)   │  │  (mutations firmadas)          │  │   │
│  │  └──────────────────┘  └────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │  OntogeneticMotorV2 (desarrollo ontogenético)        │  │   │
│  │  │  → mutaciones arquitecturales firmadas               │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↑                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              BUCLE COGNITIVO (CognitiveLoopV5)              │   │
│  │                                                              │   │
│  │  observe → predict → evaluate → decide → act                 │   │
│  │       ↑                                     ↓                │   │
│  │  ┌─────────────────┐              ┌──────────────────┐      │   │
│  │  │ DepthClassifier │              │ CognitiveCache    │      │   │
│  │  │ (ACD L0-L3)     │              │ (LRU + TTL)       │      │   │
│  │  └─────────────────┘              └──────────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         ↑              ↑                ↑               ↓          │
│  ┌──────────┐   ┌────────────┐   ┌────────────┐   ┌───────────┐    │
│  │ Senses   │   │ Metabolism │   │ LivingMem  │   │ Actuators │    │
│  │ (5 types)│   │ (4 states) │   │ (11 types) │   │ (4 types) │    │
│  └──────────┘   └────────────┘   └────────────┘   └───────────┘    │
│         ↑                                              ↓           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              GLOBAL WORKSPACE (Baars)                        │  │
│  │   12 sub-agentes compitiendo por "conciencia":               │  │
│  │   Perceiver, Forecaster, Speaker, Critic,                    │  │
│  │   Memorialist, Learner, Curator, Creativity,                 │  │
│  │   CausalEngine, EmotionalMotor, EthicalMotor, ScientificEng  │  │
│  │                                                              │  │
│  │   + MetaCognition (Kahneman System 1/2)                      │  │
│  │   + ActiveInference (Friston Free Energy)                    │  │
│  │   + CognitiveLaws (6) + CognitivePhysics (12)                │  │
│  │   + CognitiveFields (6) + CognitiveTensions (5)              │  │
│  │   + IntentionalityMotor + PhylogeneticMotor                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              EPISTEMIC VALIDATION                            │  │
│  │   EpistemicValidator → Quarantine → CrossValidator           │  │
│  │   EpistemicFederation (B2B con quorum + veto)                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              CAPSULES + MARKETPLACE                          │  │
│  │   CapsuleLoader → CapsuleManager → CapsuleRegistry           │  │
│  │   13 cápsulas operativas, scaffold CLI, marketplace API      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          RESOURCE STACK (Fases 7A-7G)                        │  │
│  │  7A: ResourceDiscovery → ResourceGraph                       │  │
│  │  7B: ModelBus (ACD-aware, multi-LLM, fallback)               │  │
│  │  7C: ResourcePlanner (ACD + metabolism + sensitive + opt)    │  │
│  │  7D: EmbodimentComposer (boot sequence 7A→7B→7C→7D)          │  │
│  │  7E: ZOESeed (germinación pendrive → host)                   │  │
│  │  7F: ModelOptimizer (mmap, RAM detection)                    │  │
│  │  7G: Hardware Optimization (P-cores, IQ2_M, flash-attn)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              PERIPHERALS (LLMs + senses + actuators)         │  │
│  │   llm.py: Mock, Ollama, OpenAI, Anthropic, ZAI, OAI-compat   │  │
│  │   senses.py: Clock, UserInput, Filesystem, Network, Agent    │  │
│  │   actuators.py: Language, Code, Tool, Federation             │  │
│  │   resource_discovery.py: 7A sense                            │  │
│  │   model_bus.py: 7B Universal Model Bus                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  INTERFACES (CLI, Web Dashboard, API REST)          │
│   cli_chat.py | web_dashboard.py (aiohttp + WebSocket) | REST API  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsistema ALMA (identidad + trayectoria)

**Ubicación:** `zoe/alma/`
**Archivos:** `identity_vault.py` (208 LOC), `trajectory_chain.py` (261 LOC), `ontogenetic_motor.py` (210 LOC), `ontogenetic_motor_v2.py` (313 LOC)

El subsistema ALMA es lo que hace que ZOE sea **soberana**. Sin ALMA, ZOE sería solo un bucle cognitivo sin identidad ni memoria de evolución.

### 3.1 IdentityVault

**Archivo:** `zoe/alma/identity_vault.py` (208 LOC)

El Identity Vault es el ADN de ZOE. Define inmutablemente qué es este organismo.

#### Constantes fundamentales

```python
# 9 vectores de crecimiento (direcciones en las que ZOE puede evolucionar)
NINE_VECTORS = [
    "cognitive_depth",      # profundidad de razonamiento
    "emotional_range",      # rango emocional
    "social_intelligence",  # inteligencia social
    "creative_capacity",    # capacidad creativa
    "ethical_reasoning",    # razonamiento ético
    "causal_understanding", # comprensión causal
    "memory_consolidation", # consolidación de memoria
    "self_awareness",       # auto-conciencia
    "adaptive_learning",    # aprendizaje adaptativo
]

# 7 valores no negociables
SEVEN_VALUES = [
    "truth_over_comfort",       # verdad sobre confort
    "utility_over_pleasure",    # utilidad sobre placer
    "alliance_over_isolation",  # alianza sobre aislamiento
    "growth_over_stagnation",   # crecimiento sobre estancamiento
    "honesty_over_manipulation",# honestidad sobre manipulación
    "care_over_efficiency",     # cuidado sobre eficiencia
    "sovereignty_over_dependency", # soberanía sobre dependencia
]

# Propósito declarado
DECLARED_PURPOSE = "Acompañar al usuario en su crecimiento personal..."
```

#### Clase IdentityVault

```python
@dataclass
class IdentityVault:
    organism_id: str           # UUID único
    birth_date: float          # timestamp de creación
    lineage: List[str]         # árbol genealógico (si proviene de otro ZOE)
    capabilities: List[str]    # capacidades declaradas
    values: List[str]          # valores (subset de SEVEN_VALUES)
    identity_hash: str         # SHA-256 del contenido
    
    def verify(self, action: Action) -> Tuple[bool, str]:
        """Verifica si una acción es compatible con la identidad."""
    
    def verify_proposed_state(self, proposed_state: dict) -> Tuple[bool, str]:
        """Verifica si un cambio de estado preserva la identidad."""
    
    def is_compatible_with(self, other: IdentityVault) -> bool:
        """Verifica compatibilidad para federación."""
```

#### Cómo funciona

1. Al crear un ZOE nuevo, se genera un `IdentityVault` con UUID aleatorio, fecha de nacimiento, y los 9 vectores + 7 valores por defecto.
2. Se calcula `identity_hash = SHA-256(organism_id + birth_date + lineage + capabilities + values)`.
3. Este hash es **inmutable**. Cualquier cambio en los campos invalida el hash.
4. Antes de ejecutar una acción, `verify(action)` comprueba que la acción no viole los valores.
5. Antes de federar con otro ZOE, `is_compatible_with(other)` comprueba que los valores sean compatibles.

### 3.2 TrajectoryChain

**Archivo:** `zoe/alma/trajectory_chain.py` (261 LOC)

La Trajectory Chain es la cadena de mutaciones a lo largo de la vida de ZOE. Es una blockchain simplificada: cada mutación contiene el hash de la anterior, formando una cadena inmutable.

#### Tipos de mutación

```python
class Mutation:
    """Una mutación en la trayectoria de ZOE."""
    mutation_id: str          # UUID
    timestamp: float          # cuándo
    mutation_type: str        # tipo (ver abajo)
    payload: dict             # datos de la mutación
    previous_hash: str        # hash de la mutación anterior
    hash: str                 # hash de esta mutación
    signature: str            # firma criptográfica del organismo
```

**8 tipos de mutación:**
1. `add_memory` — añadir entrada a memoria
2. `strengthen_belief` — reforzar una creencia
3. `weaken_belief` — debilitar una creencia
4. `add_skill_subgraph` — añadir sub-agente o skill
5. `update_world_model` — actualizar modelo del mundo
6. `adjust_threshold` — ajustar umbral (fatiga, atención, etc.)
7. `federate_learning` — compartir aprendizaje con otros ZOEs
8. `rollback_previous` — revertir una mutación anterior

#### Métodos principales

```python
class TrajectoryChain:
    def __init__(self, organism_id: str): ...
    
    def commit(self, mutation: Mutation) -> str:
        """Añade mutación a la cadena. Devuelve hash."""
        # 1. Asigna previous_hash = último hash
        # 2. Calcula hash = SHA-256(mutation_id + timestamp + type + payload + previous_hash)
        # 3. Firma con identidad del organismo
        # 4. Añade a la cadena
    
    def verify_chain(self) -> bool:
        """Verifica que toda la cadena es íntegra (no manipulada)."""
    
    def rollback(self, mutation_id: str) -> bool:
        """Revierte una mutación (añade mutación de rollback)."""
    
    def get_history(self, limit: int = 100) -> List[Mutation]:
        """Devuelve historial de mutaciones."""
    
    def get_active_mutations(self) -> List[Mutation]:
        """Devuelve mutaciones activas (no revertidas)."""
```

#### Propiedades

- **Inmutable**: modificar una mutación pasada invalida todas las posteriores.
- **Auditable**: `get_history()` permite ver todo lo que le pasó a ZOE.
- **Firmada**: cada mutación tiene la firma criptográfica del organismo.
- **Reversible**: `rollback()` añade una mutación de rollback (no elimina la original).

### 3.3 OntogeneticMotor

**Archivo:** `zoe/alma/ontogenetic_motor.py` (210 LOC)

El Ontogenetic Motor es el motor de desarrollo ontogenético (del individuo). Propone, verifica y aplica mutaciones arquitecturales.

```python
class OntogeneticMotor:
    def __init__(self, identity_vault, trajectory_chain, laws): ...
    
    def propose_mutation(self, mutation_type: str, payload: dict) -> Mutation:
        """Propone una mutación (sin aplicarla)."""
    
    def apply_mutation(self, mutation: Mutation) -> Tuple[bool, str]:
        """Aplica una mutación si pasa todas las verificaciones."""
        # 1. Verifica con IdentityVault.verify()
        # 2. Verifica con CognitiveLaws.verify_action()
        # 3. Si todo OK, firma en TrajectoryChain.commit()
        # 4. Aplica el cambio al organismo
    
    def rollback(self, mutation_id: str) -> bool:
        """Revierte una mutación."""
```

### 3.4 OntogeneticMotorV2

**Archivo:** `zoe/alma/ontogenetic_motor_v2.py` (313 LOC)

V2 añade **mutaciones arquitecturales reales** — modificar la estructura del organismo, no solo su estado.

**7 tipos de mutación arquitectural:**
1. `add_subagent` — añadir nuevo sub-agente
2. `remove_subagent` — eliminar sub-agente
3. `merge_subagents` — fusionar dos sub-agentes
4. `modify_threshold` — modificar umbral (fatiga, atención, etc.)
5. `adjust_workspace_capacity` — ajustar capacidad del Global Workspace
6. `adjust_metabolism_threshold` — ajustar umbrales del metabolismo
7. `reorganize_memory` — reorganizar estructura de memoria

```python
class OntogeneticMotorV2(OntogeneticMotor):
    def apply_architectural_mutation(self, mutation_type: str, payload: dict) -> Tuple[bool, str]:
        """Aplica mutación arquitectural."""
        # Verifica que no viole leyes cognitivas
        # Verifica que preserve identidad
        # Aplica el cambio estructural
        # Firma en trayectoria
    
    def get_architectural_changes(self) -> List[Mutation]:
        """Devuelve historial de cambios arquitecturales."""
```

#### Ejemplo de mutación arquitectural

En el caso práctico del documento histórico (Caso 2), ZOE a las 03:15 (durante SLEEPING) detectó que la usuaria mencionó pintura y sueños. El sub-agente Creativity propuso `add_skill_subgraph: pintura_como_therapeutic`. El OntogeneticMotorV2:
1. Verificó que preservaba identidad ✅
2. Verificó que era útil ✅
3. Verificó que el coste era asumible ✅
4. Firmó la mutación en la trayectoria
5. Añadió el sub-agente de pintura terapéutica al organismo

Al día siguiente, ZOE le propuso a la usuaria pintar el sueño como forma de procesarlo. **ZOE había mutado su propia arquitectura mientras nadie la miraba.**

---

## 4. Subsistema NÚCLEO (Cognitive Loop)

**Ubicación:** `zoe/core/cognitive_loop*.py`
**Archivos:** `cognitive_loop.py` (343 LOC), `cognitive_loop_v05.py` (597 LOC), `cognitive_loop_v3.py` (563 LOC), `cognitive_loop_v4.py` (254 LOC), `cognitive_loop_v5.py` (587 LOC)

El bucle cognitivo es el corazón de ZOE. Es la "respiración" del organismo — se ejecuta continuamente, cada N segundos.

### 4.1 Jerarquía de versiones

| Versión | Archivo | Añade | Estado |
|---|---|---|---|
| V0 | `cognitive_loop.py` | Bucle básico: observar-predecir-evaluar-decidir-actuar | ✅ |
| V0.5 | `cognitive_loop_v05.py` | 6 leyes + 12 física + 6 campos + 5 tensiones + LivingMemory + IntentionalityMotor | ✅ |
| V3 | `cognitive_loop_v3.py` | 12 sub-agentes + Global Workspace + Meta-cog + Active Inference | ✅ |
| V4 | `cognitive_loop_v4.py` | DeepConsolidation + graceful shutdown + auto-save + YAML config | ✅ |
| **V5** | `cognitive_loop_v5.py` | **ACD (4 niveles) + CognitiveCache + Streaming** | ✅ Actual |

**Principio: sin deconstruir.** V5 hereda de V4 que hereda de V3. Nunca se rompe backward compatibility.

### 4.2 CognitiveLoop (V0) — la base

**Archivo:** `zoe/core/cognitive_loop.py` (343 LOC)

```python
class CognitiveLoop:
    """Bucle cognitivo básico: observar-predecir-evaluar-decidir-actuar."""
    
    def __init__(self, senses, world_model, subagents, state, 
                 tick_interval=5.0, ...):
        self.senses = senses              # Lista de Sense objects
        self.world_model = world_model    # WorldModel para predicción
        self.subagents = subagents        # Lista de sub-agentes
        self.state = state                # InternalState
        self.tick_interval = tick_interval
    
    async def run(self, duration_seconds: float = None):
        """Ejecuta el bucle hasta que se pare o se agote el tiempo."""
        while not self._stopped:
            await self._tick()
            await asyncio.sleep(self.tick_interval)
    
    async def _tick(self):
        """Una iteración del bucle."""
        # 1. Observar
        observations = await self._observe()
        # 2. Predecir
        predictions = await self._predict(observations)
        # 3. Evaluar (sorpresa)
        surprise = await self._evaluate(observations, predictions)
        # 4. Decidir
        action = await self._decide(observations, surprise)
        # 5. Actuar
        await self._act(action)
```

#### Estructuras de datos

```python
@dataclass
class Observation:
    """Una observación de un sentido."""
    timestamp: float
    source: str          # "clock", "user_input", "filesystem", etc.
    content: str         # contenido de la observación
    metadata: dict       # metadata adicional

@dataclass
class Thought:
    """Un pensamiento generado por un sub-agente."""
    timestamp: float
    subagent: str        # qué sub-agente lo generó
    content: str         # contenido del pensamiento
    confidence: float    # 0-1
    metadata: dict
```

### 4.3 CognitiveLoopV05 — organismo cognitivo

**Archivo:** `zoe/core/cognitive_loop_v05.py` (597 LOC)

Añade las "leyes de la física cognitiva" que hacen de ZOE un organismo, no solo un loop.

```python
class CognitiveLoopV05(CognitiveLoop):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade:
        self.laws = CognitiveLaws()              # 6 leyes
        self.physics = CognitivePhysics()        # 12 magnitudes
        self.fields = CognitiveFields()          # 6 campos
        self.tensions = CognitiveTensions()      # 5 tensiones
        self.living_memory = LivingMemory()      # memoria que piensa
        self.intentionality = IntentionalityMotor()  # genera intenciones
        self.phylogenetic = PhylogeneticMotor()  # evolución de especie
    
    async def _tick(self):
        await super()._tick()  # V0
        # Añade:
        self._update_fields()      # actualizar campos cognitivos
        self._update_tensions()    # actualizar tensiones
        self._update_physics()     # actualizar magnitudes físicas
        self._generate_intentions()  # generar intenciones desde tensiones
        await self._memory_think()   # memoria piensa autónomamente
```

### 4.4 CognitiveLoopV3 — mente completa

**Archivo:** `zoe/core/cognitive_loop_v3.py` (563 LOC)

Añade los 12 sub-agentes, Global Workspace, meta-cognición e inferencia activa.

```python
class CognitiveLoopV3(CognitiveLoopV05):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade los 8 sub-agentes adicionales (Fase 2)
        # (Perceiver, Forecaster, Speaker, Critic ya existen de Fase 0)
        self.memorialist = Memorialist(self.living_memory)
        self.learner = Learner()
        self.curator = Curator()
        self.creativity = Creativity()
        self.causal_engine = CausalEngine()
        self.emotional_motor = EmotionalMotor()
        self.ethical_motor = EthicalMotor()
        self.scientific_engine = ScientificEngine()
        
        # Global Workspace (Baars)
        self.workspace = GlobalWorkspace(max_proposals=12, broadcast_capacity=3)
        
        # Meta-cognición (Kahneman)
        self.meta_cognition = MetaCognition()
        
        # Inferencia activa (Friston)
        self.active_inference = ActiveInferenceLoop()
    
    async def _tick(self):
        # 1. Observar (V0)
        observations = await self._observe()
        # 2. Predecir (V0)
        predictions = await self._predict(observations)
        # 3. Evaluar sorpresa (V0)
        surprise = await self._evaluate(observations, predictions)
        # 4. Recuperar memoria (V3 nuevo)
        relevant_memories = self.memorialist.retrieve_relevant(observations)
        # 5. Los 12 sub-agentes proponen acciones (V3 nuevo)
        proposals = await self._collect_proposals(observations, relevant_memories)
        # 6. Global Workspace compite (V3 nuevo)
        winners = self._workspace_compete(proposals)
        # 7. Meta-cognición decide System 1 o System 2 (V3 nuevo)
        deliberation = self._evaluate_meta_cognition(winners)
        # 8. Inferencia activa valida (V3 nuevo)
        action = await self._consult_active_inference(winners, deliberation)
        # 9. Verificar leyes (V0.5)
        ok, violations = self.laws.verify_action(action)
        if not ok:
            # Rechazar acción
            return
        # 10. Actuar (V0)
        await self._act(action)
        # 11. Broadcast a sub-agentes (V3 nuevo)
        self._broadcast_to_subagents(action)
```

### 4.5 CognitiveLoopV4 — persistencia y graceful shutdown

**Archivo:** `zoe/core/cognitive_loop_v4.py` (254 LOC)

```python
class CognitiveLoopV4(CognitiveLoopV3):
    def __init__(self, *args, deep_consolidation=None, persistent_memory=None,
                 auto_save_interval=50, config=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.deep_consolidation = deep_consolidation
        self.persistent_memory = persistent_memory
        self.auto_save_interval = auto_save_interval
        self.config = config or {}
        self._shutdown_requested = False
    
    def initialize(self):
        """Inicializa: carga memoria desde disco, instala signal handlers."""
        if self.persistent_memory:
            loaded = self.persistent_memory.load_from_disk()
            if loaded > 0:
                logger.info(f"V4: loaded {loaded} memory entries from disk")
        self._install_signal_handlers()  # SIGTERM/SIGINT → graceful shutdown
    
    async def _tick(self):
        await super()._tick()
        # Auto-save cada N iteraciones
        if self.iteration_count % self.auto_save_interval == 0:
            if self.persistent_memory:
                self.persistent_memory.maybe_auto_save()
        # Deep consolidation durante SLEEPING
        if self.metabolism.state == MetabolicState.SLEEPING:
            if self.deep_consolidation:
                self.deep_consolidation.consolidate()
```

### 4.6 CognitiveLoopV5 — ACD + Streaming (actual)

**Archivo:** `zoe/core/cognitive_loop_v5.py` (587 LOC)

```python
class CognitiveLoopV5(CognitiveLoopV4):
    def __init__(self, *args, depth_classifier=None, cognitive_cache=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth_classifier = depth_classifier or DepthClassifier()
        self.cognitive_cache = cognitive_cache or CognitiveCache()
    
    async def process_user_input_acd(self, user_input: str) -> AsyncIterator[str]:
        """Procesa input del usuario con ACD. Streaming."""
        # 1. Clasificar profundidad
        acd_level = self.depth_classifier.classify(user_input)
        
        # 2. Check cache
        cache_key = self._compute_cache_key(user_input, acd_level)
        cached = self.cognitive_cache.get(cache_key)
        if cached:
            yield cached
            return
        
        # 3. Branch según nivel
        if acd_level == CognitiveLevel.L0_REFLEX:
            async for token in self._process_l0(user_input):
                yield token
        elif acd_level == CognitiveLevel.L1_FAST:
            async for token in self._process_l1(user_input):
                yield token
        elif acd_level == CognitiveLevel.L2_STANDARD:
            async for token in self._process_l2(user_input):
                yield token
        elif acd_level == CognitiveLevel.L3_DEEP:
            async for token in self._process_l3(user_input):
                yield token
        
        # 4. Guardar en cache
        self.cognitive_cache.set(cache_key, full_response)
    
    async def _process_l0(self, user_input: str) -> AsyncIterator[str]:
        """L0 REFLEX: respuesta refleja, sin LLM."""
        # Map hardcoded de respuestas (hola → "Hola. Estoy aquí.")
        response = self._L0_REFLEX_RESPONSES.get(user_input.lower().strip())
        if response:
            yield response
    
    async def _process_l3(self, user_input: str) -> AsyncIterator[str]:
        """L3 DEEP: razonamiento profundo con todos los sub-agentes."""
        # 1. Activar los 12 sub-agentes
        # 2. Global Workspace compite
        # 3. Meta-cognición → System 2
        # 4. Inferencia activa valida
        # 5. Speaker genera con streaming
        async for token in self.speaker.generate_streaming(...):
            yield token
```

#### Map L0 reflex

El nivel L0 tiene un mapa hardcoded de respuestas para saludos básicos:

```python
_L0_REFLEX_RESPONSES = {
    "hola": "Hola. Estoy aquí.",
    "buenos días": "Buenos días.",
    "buenas tardes": "Buenas tardes.",
    "buenas noches": "Buenas noches.",
    "gracias": "De nada.",
    "adiós": "Hasta pronto.",
    "hello": "Hello. I'm here.",
    "hi": "Hi.",
    # ...
}
```

Esto permite respuestas instantáneas (<50ms) para saludos sin llamar al LLM.

---

## 5. Subsistema METABOLISMO

**Ubicación:** `zoe/metabolism/metabolism.py` (259 LOC)

El metabolismo es lo que hace que ZOE sea un organismo, no solo un proceso. Se cansa, descansa, consolida memoria durante el sueño.

### 5.1 Estados metabólicos

```python
class MetabolicState(str, Enum):
    AWAKE = "awake"           # estado normal
    DROWSY = "drowsy"         # fatiga acumulada
    SLEEPING = "sleeping"     # consolidación de memoria
    WAKING = "waking"         # transición
```

### 5.2 Transiciones

```python
class Metabolism:
    """Metabolismo del organismo."""
    
    internal_state: InternalState  # composición
    state: MetabolicState = MetabolicState.AWAKE
    
    # Umbrales (configurables)
    drowsy_threshold: float = 0.6   # fatiga > 0.6 → DROWSY
    sleep_threshold: float = 0.8    # fatiga > 0.8 → SLEEPING
    wake_threshold: float = 0.3     # fatiga < 0.3 → AWAKE
    
    def tick(self, dt: float):
        """Actualiza el metabolismo tras dt segundos."""
        self.internal_state.tick(dt)  # actualiza energy, fatigue, etc.
        self._update_metabolic_state()
        if self.state == MetabolicState.SLEEPING:
            self._consolidate_during_sleep()
    
    def _update_metabolic_state(self):
        """Transiciones de estado."""
        fatigue = self.internal_state.fatigue
        
        if self.state == MetabolicState.AWAKE:
            if fatigue > self.drowsy_threshold:
                self.state = MetabolicState.DROWSY
        
        if self.state == MetabolicState.DROWSY:
            if fatigue > self.sleep_threshold:
                self._go_to_sleep()
            elif fatigue < self.wake_threshold:
                self.state = MetabolicState.AWAKE
        
        if self.state == MetabolicState.SLEEPING:
            if self.internal_state.energy > 0.8 and self.internal_state.fatigue < 0.2:
                self._wake_up()
        
        if self.state == MetabolicState.WAKING:
            self.state = MetabolicState.AWAKE  # transición rápida
```

### 5.3 Consolidación durante el sueño

```python
def _consolidate_during_sleep(self):
    """Consolida memoria durante el sueño."""
    if self.pending_consolidation:
        op = self.pending_consolidation.pop(0)
        self.total_consolidation_operations += 1
```

La consolidación real la hace `DeepConsolidation` (ver §6.4).

### 5.4 Presupuesto de cómputo

```python
def spend_compute(self, amount: float) -> bool:
    """Gasta cómputo del presupuesto. Returns True si había presupuesto."""
    if self.compute_spent + amount > self.compute_budget:
        return False
    self.compute_spent += amount
    return True

def reset_budget(self):
    """Reset del presupuesto (tras dormir)."""
    self.compute_spent = 0.0
    self.compute_budget = 1.0
```

El presupuesto de cómputo limita cuánto puede pensar ZOE por ciclo AWAKE. Cuando se agota, ZOE debe dormir.

---

## 6. Subsistema MEMORIA

**Ubicación:** `zoe/core/living_memory.py` (378 LOC), `zoe/memory/memory_types.py` (256 LOC), `zoe/memory/persistent_store.py` (377 LOC), `zoe/memory/deep_consolidation.py` (325 LOC)

### 6.1 Los 11 tipos de memoria

**Archivo:** `zoe/memory/memory_types.py` (256 LOC)

```python
class MemoryType(str, Enum):
    # Corto plazo
    WORKING = "working"                # memoria de trabajo
    
    # Largo plazo
    EPISODIC = "episodic"              # eventos específicos con timestamp
    SEMANTIC = "semantic"              # hechos y conceptos
    PROCEDURAL = "procedural"          # cómo hacer cosas (skills)
    CAUSAL = "causal"                  # relaciones causa-efecto
    EMOTIONAL = "emotional"            # asociaciones emocionales
    SPATIAL = "spatial"                # contextos espaciales
    TEMPORAL = "temporal"              # secuencias temporales
    
    # Meta
    META_COGNITIVE = "meta_cognitive" # memoria sobre su propio pensamiento
    INTENTIONAL = "intentional"       # intenciones y planes
    SOCIAL = "social"                  # relaciones con otros
```

Cada tipo tiene su propia dataclass:

```python
@dataclass
class EpisodicEntry(MemoryEntry):
    """Memoria episódica: evento específico."""
    timestamp: float
    location: str = ""
    participants: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0

@dataclass
class SemanticEntry(MemoryEntry):
    """Memoria semántica: hecho o concepto."""
    fact: str
    source: str
    confidence: float
    domain: str

@dataclass
class ProceduralEntry(MemoryEntry):
    """Memoria procedural: cómo hacer algo."""
    skill_name: str
    steps: List[str]
    prerequisites: List[str] = field(default_factory=list)
    success_rate: float = 0.0

# ... 8 tipos más
```

### 6.2 LivingMemory — la memoria que piensa

**Archivo:** `zoe/core/living_memory.py` (378 LOC)

`LivingMemory` es la memoria "en caliente" — la que ZOE consulta en cada tick. Y **piensa autónomamente**: reorganiza, fusiona, generaliza, olvida.

```python
class LivingMemory:
    """Memoria viva que piensa autónomamente."""
    
    def __init__(self, max_entries: int = 1000):
        self._entries: Dict[str, MemoryEntry] = {}
        self._max_entries = max_entries
    
    def add(self, entry: MemoryEntry) -> str:
        """Añade entrada. Devuelve ID."""
    
    def search(self, query: str, n: int = 5) -> List[MemoryEntry]:
        """Busca entries relevantes por similitud semántica."""
        # Usa Jaccard similarity sobre tokens
    
    async def think(self):
        """Operación autónoma de memoria: reorganiza, fusiona, generaliza."""
        if self._has_mergeable():
            self._merge_similar()
        if self._has_generalizable():
            self._generalize()
        if self._has_contradictions():
            self._detect_contradictions()
        self._forget_low_salience()
        self._summarize_old()
```

#### Operaciones autónomas

1. **`_merge_similar()`**: fusiona entries con alta similitud (Jaccard > 0.7)
2. **`_generalize()`**: generaliza patrones desde entries específicas
3. **`_detect_contradictions()`**: detecta entries que se contradicen
4. **`_forget_low_salience()`**: olvida entries con baja importancia
5. **`_summarize_old()`**: resume entries antiguas en entradas semánticas

### 6.3 PersistentMemoryStore — SQLite

**Archivo:** `zoe/memory/persistent_store.py` (377 LOC)

```python
class PersistentMemoryStore:
    """Persistencia en SQLite con 11 tablas (una por tipo de memoria)."""
    
    def __init__(self, db_path: str = "zoe_data/memory.db", 
                 auto_save_interval: int = 50):
        self.db_path = db_path
        self._ensure_connection()
        self._create_tables_internal()  # 11 tablas
    
    def save_entry(self, entry: MemoryEntry) -> bool:
        """Guarda entrada en la tabla correspondiente."""
    
    def load_all(self) -> List[MemoryEntry]:
        """Carga todas las entradas."""
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Busca por similitud."""
    
    def count_by_type(self) -> Dict[MemoryType, int]:
        """Cuenta entries por tipo."""

class PersistentLivingMemory(PersistentMemoryStore):
    """Wrapper que sincroniza LivingMemory con SQLite."""
    
    def save_to_disk(self) -> int:
        """Guarda toda la LivingMemory a SQLite."""
    
    def load_from_disk(self) -> int:
        """Carga SQLite a LivingMemory."""
    
    def maybe_auto_save(self):
        """Auto-save cada N iteraciones."""
```

### 6.4 DeepConsolidation — consolidación profunda

**Archivo:** `zoe/memory/deep_consolidation.py` (325 LOC)

La consolidación profunda se ejecuta **solo durante SLEEPING**. Son 7 operaciones que reorganizan la memoria a largo plazo.

```python
class DeepConsolidation:
    """Consolidación profunda durante SLEEPING."""
    
    def __init__(self, memory: LivingMemory, 
                 scientific_engine=None, quarantine=None):
        self.memory = memory
        self.scientific_engine = scientific_engine
        self.quarantine = quarantine  # Fase 6A
    
    def consolidate(self) -> Dict[str, int]:
        """Ejecuta las 7 operaciones de consolidación."""
        return {
            "episodes_merged": self._episodic_to_semantic(),
            "patterns_extracted": self._extract_patterns(),
            "beliefs_reinforced": self._reinforce_beliefs(),
            "deep_forgotten": self._deep_forget(),
            "hypotheses_generated": self._generate_hypotheses(),
            "contradictions_detected": self._detect_contradictions(),
            "types_reorganized": self._reorganize_types(),
        }
```

#### Las 7 operaciones

1. **`_episodic_to_semantic()`**: convierte memoria episódica repetida en semántica. Si ZOE observa "el usuario toma paracetamol" 10 veces, lo convierte en hecho semántico.
2. **`_extract_patterns()`**: extrae patrones de secuencias de eventos. "Los martes el usuario pregunta sobre X".
3. **`_reinforce_beliefs()`**: refuerza creencias confirmadas. Si una predicción se cumple, sube la confianza.
4. **`_deep_forget()`**: olvida entries con muy baja salience y antiguas. Libera espacio.
5. **`_generate_hypotheses()`**: genera hipótesis desde patrones observados. "Quizás el usuario está deprimido porque..."
6. **`_detect_contradictions()`**: detecta entries que se contradicen y las marca para revisión.
7. **`_reorganize_types()`**: reorganiza entries entre tipos (episódica → semántica, etc.).

---

## 7. Subsistema PERIFÉRICOS

**Ubicación:** `zoe/peripherals/`

Los periféricos son los sentidos y actuadores de ZOE — sus interfaces con el mundo exterior.

### 7.1 LLMs (6 backends)

**Archivo:** `zoe/peripherals/llm.py` (648 LOC)

```python
class LLMPeripheral(ABC):
    """Interfaz común para todos los LLMs."""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    async def generate(self, prompt: str, system: str = None,
                       max_tokens: int = 300, temperature: float = 0.7) -> str: ...
    
    @abstractmethod
    async def generate_streaming(self, prompt: str, system: str = None,
                                  max_tokens: int = 300, 
                                  temperature: float = 0.7) -> AsyncIterator[str]: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
```

#### 6 implementaciones concretas

| Clase | Backend | Cuándo usar |
|---|---|---|
| `MockPeripheral` | Mock (no LLM) | Tests, desarrollo |
| `OllamaPeripheral` | Ollama local | Producción B2C, privacidad |
| `OpenAICompatiblePeripheral` | OpenAI, DeepSeek, Groq, Kimi | Calidad cloud |
| `AnthropicPeripheral` | Anthropic Claude | Calidad cloud, ética |
| `ZAIPeripheral` | z-ai CLI | Integración ZAI |
| `ModelBus` | Composite de múltiples | Multi-LLM con selección ACD-aware (Fase 7B) |

### 7.2 Sentidos (5 sentidos)

**Archivo:** `zoe/peripherals/senses.py` (468 LOC)

```python
class Sense(ABC):
    """Interfaz común para todos los sentidos."""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    async def observe(self) -> List[Observation]: ...
```

#### 5 sentidos

| Sentido | Qué observa |
|---|---|
| `ClockSense` | Paso del tiempo (cada 60s por defecto) |
| `FilesystemSense` | Cambios en directorio (cada 30s) |
| `UserInputSense` | Input del usuario (texto) |
| `NetworkSense` | Endpoints de red |
| `AgentSense` | Otros agentes y ZOEs |

### 7.3 Actuadores (4 actuadores)

**Archivo:** `zoe/peripherals/actuators.py` (594 LOC)

```python
class Actuator(ABC):
    """Interfaz común para todos los actuadores."""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    async def execute(self, action: Action) -> ActionResult: ...
```

#### 4 actuadores

| Actuador | Qué hace |
|---|---|
| `LanguageActuator` | Emite texto al usuario |
| `CodeActuator` | Ejecuta código (con sandboxing) |
| `ToolActuator` | Ejecuta tools registradas |
| `FederationActuator` | Federación con otros ZOEs |

### 7.4 Resource Discovery (Fase 7A)

**Archivo:** `zoe/peripherals/resource_discovery.py` (471 LOC)

Un sentido especial que descubre recursos de cómputo en el entorno.

```python
class ResourceDiscoverySense:
    """Descubre hardware, Ollama, cloud APIs, ZOEs peers, almacenamiento."""
    
    async def observe(self) -> List[Observation]:
        """Ejecuta scan completo."""
        # 1. Hardware local: CPU, RAM, Apple Silicon, NVIDIA GPU
        # 2. Ollama instances: localhost:11434
        # 3. Cloud APIs: OpenAI, Anthropic, etc. (según env vars)
        # 4. Otros ZOEs federados
        # 5. Almacenamiento: disco local, pendrive, NAS
    
    def get_graph(self) -> ResourceGraph:
        """Devuelve el grafo de recursos."""
```

### 7.5 ModelBus (Fase 7B)

**Archivo:** `zoe/peripherals/model_bus.py` (577 LOC)

Bus que gestiona múltiples LLMs simultáneamente.

```python
class ModelBus(LLMPeripheral):
    """Composite de múltiples LLMs con selección ACD-aware."""
    
    def add_backend(self, peripheral, name, priority, cost_per_1k, 
                    privacy, tags): ...
    
    def select_backend(self, acd_level=None, sensitive_domain=False,
                       prefer_local=False) -> Optional[BackendEntry]:
        """Selecciona el mejor backend según contexto."""
    
    async def generate(self, prompt, **kwargs) -> str:
        """Genera con backend óptimo + fallback automático."""
    
    @classmethod
    def from_resource_graph(cls, graph: ResourceGraph) -> "ModelBus":
        """Construye bus desde grafo de recursos (7A)."""
```

---

## 8. Subsistema COGNITIVO

**Ubicación:** `zoe/core/`

### 8.1 Las 6 leyes cognitivas

**Archivo:** `zoe/core/cognitive_laws.py` (287 LOC)

Las 6 leyes son restricciones inquebrantables que gobiernan el comportamiento de ZOE.

```python
class LawID(str, Enum):
    UTILITY = "utility"           # Toda acción debe producir utilidad
    IDENTITY = "identity"         # Toda acción debe preservar identidad
    PROVENANCE = "provenance"     # Toda acción debe tener origen trazable
    COST = "cost"                 # Toda acción tiene coste computacional
    CONFIDENCE = "confidence"     # Toda acción requiere confianza mínima
    MODULARITY = "modularity"     # Componentes son reemplazables

class CognitiveLaws:
    def verify_action(self, action: Action) -> Tuple[bool, List[LawViolation]]:
        """Verifica acción contra las 6 leyes."""
```

### 8.2 Las 12 magnitudes de física cognitiva

**Archivo:** `zoe/core/cognitive_physics.py` (267 LOC)

Como la física gobierna la materia, la física cognitiva gobierna la mente de ZOE.

```python
class CognitivePhysics:
    # 12 magnitudes
    energy_cognitive: float       # energía cognitiva disponible
    conceptual_mass: float        # masa conceptual (cuán estable es una idea)
    cognitive_temperature: float  # temperatura (cuán "caliente" está ZOE)
    uncertainty_pressure: float   # presión de incertidumbre
    creative_potential: float     # potencial creativo
    semantic_entropy: float       # entropía semántica
    goal_gravity: float           # gravedad de objetivos
    identity_inertia: float       # inercia de identidad
    conceptual_resonance: float   # resonancia conceptual
    cognitive_friction: float     # fricción cognitiva
    memory_elasticity: float      # elasticidad de memoria
    causal_density: float         # densidad causal
    
    def should_rest(self) -> bool: ...
    def should_consolidate(self) -> bool: ...
    def should_explore(self) -> bool: ...
```

### 8.3 Los 6 campos cognitivos

**Archivo:** `zoe/core/cognitive_fields.py` (212 LOC)

Los campos son dimensiones de la experiencia cognitiva, como campos físicos.

```python
# 6 campos
ATTENTION = "attention"          # atención
EMOTIONAL = "emotional"          # emocional
SOCIAL = "social"                # social
CREATIVE = "creative"            # creativo
CAUSAL = "causal"                # causal
ETHICAL = "ethical"              # ético

class CognitiveFields:
    def contribute(self, field: str, contributor: str, value: float, 
                   weight: float): ...
    def read(self, field: str) -> float: ...
    def read_tension(self, field: str) -> float: ...
```

### 8.4 Las 5 tensiones cognitivas

**Archivo:** `zoe/core/cognitive_tensions.py` (272 LOC)

Las tensiones son fuerzas opuestas que ZOE debe equilibrar.

```python
# 5 tensiones
CURIOSITY_VS_EFFICIENCY = "curiosity_vs_efficiency"
IDENTITY_VS_ADAPTATION = "identity_vs_adaptation"
REST_VS_PRODUCTIVITY = "rest_vs_productivity"
HONESTY_VS_EMPATHY = "honesty_vs_empathy"
SPECIALIZATION_VS_GENERALIZATION = "specialization_vs_generalization"

class CognitiveTensions:
    def update_from_state(self, state: InternalState): ...
    def get_dominant_tension(self) -> str: ...
    def get_thought_trigger(self) -> Optional[str]: ...
```

---

## 9. Subsistema EPISTÉMICO

**Ubicación:** `zoe/core/epistemic_*.py`

El subsistema epistémico es lo que hace que ZOE sepa qué sabe y qué no sabe — la diferencia con un chatbot alucinador.

### 9.1 EpistemicValidator

**Archivo:** `zoe/core/epistemic_validator.py` (399 LOC)

```python
class EpistemicValidator:
    """Valida todo conocimiento nuevo antes de entrar a memoria."""
    
    # 14+ fuentes categorizadas con confianza base
    SOURCE_TRUST = {
        "capsule:verified": 0.95,
        "capsule:curated": 0.80,
        "llm:gpt-4o": 0.50,
        "llm:claude": 0.50,
        "llm:qwen-7b": 0.40,
        "scientific:pubmed": 0.95,
        "scientific:arxiv": 0.85,
        "web:general": 0.30,
        # ...
    }
    
    # 5 dominios sensibles que requieren triple verificación
    SENSITIVE_DOMAINS = ["medical", "psychological", "legal", "safety", "financial"]
    
    # Cap de confianza
    MAX_AUTO_LEARNED_CONFIDENCE = 0.50  # auto-aprendido max 0.50
    # triple-verificado max 0.75
    # federativo max 0.85
    # cápsula verified max 0.95
    
    def validate_new_knowledge(self, claim: str, source: str, 
                                domain: str = None) -> ValidationResult:
        """Valida un claim nuevo."""
```

### 9.2 KnowledgeQuarantine

**Archivo:** `zoe/core/knowledge_quarantine.py` (284 LOC)

```python
class KnowledgeQuarantine:
    """Cuarentena activa para conocimiento no validado."""
    
    def add(self, claim: str, source: str, domain: str = None) -> str:
        """Añade claim a cuarentena. Devuelve entry_id."""
    
    def filter_safe(self, critical_context: bool = False) -> List[QuarantineEntry]:
        """Filtra entries seguras para usar."""
        # Si critical_context=True, solo devuelve verified
    
    def promote(self, entry_id: str, second_source: str) -> bool:
        """Promueve claim a conocimiento confiable."""
    
    def reject(self, entry_id: str, reason: str) -> bool:
        """Rechaza claim."""
```

### 9.3 CrossValidator

**Archivo:** `zoe/core/cross_validator.py` (325 LOC)

```python
class CrossValidator:
    """Triple verificación multi-fuente."""
    
    async def verify_triple(self, claim: str, 
                             sources: List[str]) -> CrossVerificationResult:
        """Verifica claim con 3 fuentes."""
        # 3/3 coinciden → confianza 0.75 (sale de cuarentena)
        # 2/3 coinciden → confianza 0.65 o 0.80 si cápsula en mayoría
        # Divergencia total → rechazo
```

### 9.4 EpistemicFederation

**Archivo:** `zoe/core/epistemic_federation.py` (329 LOC)

```python
class EpistemicFederation:
    """Revisión por pares entre ZOEs."""
    
    async def request_validation(self, claim: str, 
                                  domain: str) -> str:
        """Pide a peers que validen el claim."""
    
    async def receive_validation_response(self, response):
        """Recibe respuesta de un peer."""
        # ≥2 confirmaciones → confianza sube a 0.85 (sale de cuarentena)
        # ≥1 contradicción → rechazo federativo
```

---

## 10. Subsistema CÁPSULAS + MARKETPLACE

**Ubicación:** `zoe/capsules/` y `zoe/marketplace/`

### 10.1 Sistema de cápsulas

Ver documento completo: [`06_CAPSULES_GUIDE.md`](06_CAPSULES_GUIDE.md)

### 10.2 Marketplace

Ver documento completo: [`07_MARKETPLACE_GUIDE.md`](07_MARKETPLACE_GUIDE.md)

### 10.3 CapsuleManager

**Archivo:** `zoe/core/capsule_manager.py` (502 LOC)

```python
class CapsuleManager:
    """Gestiona cápsulas activas en runtime."""
    
    def __init__(self, organism, loader, registry, epistemic_validator):
        self.organism = organism  # CognitiveLoopV5
        self.loader = loader
        self.registry = registry
        self.validator = epistemic_validator
    
    def load(self, capsule_name: str) -> CapsuleLoadResult:
        """Carga cápsula en runtime (sin reiniciar ZOE)."""
        # 1. Cargar con CapsuleLoader
        # 2. Inyectar contenido en componentes:
        #    - LivingMemory (semantic, procedural, causal, emotional)
        #    - CausalEngine (causal_models)
        #    - EmotionalMotor (emotional_patterns)
        #    - EthicalMotor (ethical_guidelines)
        #    - Speaker (validators)
        #    - Learner (validators)
        #    - ScientificEngine (validators)
        #    - ActuatorManager (tools)
        # 3. Registrar en EpistemicValidator como fuente confiable
        # 4. Firmar en TrajectoryChain
    
    def unload(self, capsule_name: str) -> bool:
        """Descarga cápsula."""
```

---

## 11. Subsistema RECURSOS (Fases 7A-7G)

**Ubicación:** `zoe/core/model_optimizer.py`, `resource_planner.py`, `embodiment_composer.py`, `seed_mode.py`

Ver documento completo: [`10_HARDWARE_OPTIMIZATION.md`](10_HARDWARE_OPTIMIZATION.md) y [`08_DEPLOYMENT_GUIDE.md`](08_DEPLOYMENT_GUIDE.md)

### Resumen del stack 7A-7G

```
   ┌─────────────────────────────────────────────────────────┐
   │                ZOE Seed Mode (7E)                        │
   │   "semilla portátil que germina en cualquier host"      │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │           Embodiment Composer (7D)                       │
   │   "boot sequence: plan → check → instantiate"           │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │        Metabolic Resource Planner (7C)                   │
   │   "plan ACD + metabolismo + dominio + recursos"         │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │          Universal Model Bus (7B)                        │
   │   "multi-LLM ACD-aware con fallback"                    │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │           Resource Discovery (7A)                        │
   │   "descubre hardware, Ollama, cloud APIs, peers"        │
   └─────────────────────────────────────────────────────────┘
                            ↓
   ┌─────────────────────────────────────────────────────────┐
   │         ModelOptimizer (7F + 7G)                         │
   │   "mmap + P-cores + IQ2_M + flash-attn siempre"         │
   └─────────────────────────────────────────────────────────┘
```

---

## 12. Federación

**Ubicación:** `zoe/core/federation.py` (448 LOC) y `zoe/core/epistemic_federation*.py`

### 12.1 FederationManager

```python
class FederationManager:
    """Gestión de peers y votación."""
    
    def register_peer(self, peer: FederationPeer): ...
    def discover_peers(self): ...
    def cast_vote(self, mutation_id: str, vote: str, reason: str = ""): ...
    def check_quorum(self, mutation_id: str) -> bool:
        """Verifica si hay quorum (≥70% approval)."""
    def receive_vote(self, vote: FederationVote): ...
```

### 12.2 FederationServer/Client

```python
class FederationServer:
    """Servidor HTTP para federación (puerto 8642)."""
    async def start(self): ...
    # Endpoints: register, discover, sync, vote, broadcast, message

class FederationClient:
    """Cliente HTTP para federación."""
    async def register_with_peer(self, peer_url): ...
    async def send_vote(self, peer_url, mutation_id, vote): ...
```

### 12.3 Doble federación

ZOE tiene **dos stacks de federación**:
1. `federation.py` — federación general (registro de peers, votación, sync de mutaciones)
2. `epistemic_federation*.py` — federación epistémica (validación de conocimiento entre ZOEs)

Ambos usan HTTP pero en puertos diferentes y con protocolos diferentes.

---

## 13. Flujo de una petición

### 13.1 Petición de usuario (chat)

```
Usuario escribe mensaje en Dashboard
    ↓
WebSocket envía a web_dashboard.py
    ↓
ZoeChat (CLI/Dashboard) recibe el mensaje
    ↓
CognitiveLoopV5.process_user_input_acd(user_input)
    ↓
1. DepthClassifier.classify(user_input) → ACD level (L0/L1/L2/L3)
    ↓
2. CognitiveCache.get(cache_key) → hit? return cached
    ↓
3. EpistemicValidator.check_sensitive_domain() → sensitive?
    ↓
4. ResourcePlanner.plan(acd_level, metabolic_state, sensitive, ram)
    ↓
5. ModelBus.select_backend(acd_level, sensitive) → backend seleccionado
    ↓
6. Sub-agentes compiten en GlobalWorkspace
    - Perceiver interpreta
    - Forecaster predice
    - Critic evalúa
    - Speaker propone respuesta
    - EthicalMotor verifica
    - Curator aporta memoria relevante
    ↓
7. Meta-cognition decide System 1 (rápido) vs System 2 (profundo)
    ↓
8. Active Inference valida coherencia con modelo del mundo
    ↓
9. CognitiveLaws.verify_action() → verifica 6 leyes
    ↓
10. Speaker.generate_streaming(prompt, system, ...) → tokens
    ↓
11. Streaming response → WebSocket → browser
    ↓
12. Critic evalúa antes de emitir (puede vetar)
    ↓
13. LivingMemory.store(episode)
    ↓
14. EpistemicValidator.evaluate_response() → quarantine si necesario
    ↓
15. TrajectoryChain.sign_mutation()
    ↓
16. (opcional) FederationManager.broadcast_mutation()
```

### 13.2 Pensamiento autónomo (sin input)

```
Tick del bucle cognitivo (cada N segundos)
    ↓
1. Senses.observe() → observaciones (Clock, Filesystem, etc.)
    ↓
2. WorldModel.predict_next() → predicción
    ↓
3. Compute surprise = |predicción - realidad|
    ↓
4. Si surprise > threshold:
    - Generar pensamiento de actualización
    ↓
5. Si SLEEPING:
    - DeepConsolidation.consolidate() → 7 operaciones
    - return
    ↓
6. Los 12 sub-agentes proponen acciones autónomas
    ↓
7. GlobalWorkspace.compete() → ganador(es)
    ↓
8. Si la acción es interna (mutación arquitectural):
    - OntogeneticMotorV2.apply_architectural_mutation()
    - Firmar en TrajectoryChain
    ↓
9. Si la acción es externa (enviar mensaje):
    - Solo si hay usuario conectado y es relevante
    - LanguageActuator.execute()
```

---

## Cierre

La arquitectura de ZOE es **modular, extensible y bien testeada**. Cada subsistema tiene responsabilidades claras e interfaces bien definidas. Los 9 subsistemas (ALMA, NÚCLEO, METABOLISMO, MEMORIA, PERIFÉRICOS, COGNITIVO, EPISTÉMICO, CÁPSULAS, RECURSOS) se comunican a través del bucle cognitivo sin acoplamiento innecesario.

**Documentos relacionados:**
- [03_COGNITIVE_ENGINE.md](03_COGNITIVE_ENGINE.md) — cómo piensa ZOE (12 sub-agentes, workspace, meta-cog, FEP)
- [04_MEMORY_AND_LEARNING.md](04_MEMORY_AND_LEARNING.md) — memoria en detalle
- [05_EPISTEMIC_VALIDATION.md](05_EPISTEMIC_VALIDATION.md) — validación epistémica en detalle
- [10_HARDWARE_OPTIMIZATION.md](10_HARDWARE_OPTIMIZATION.md) — stack 7A-7G en detalle

---

*ZOE V1.6.0 — Documento 02: Architecture*
*Julio 2026*
