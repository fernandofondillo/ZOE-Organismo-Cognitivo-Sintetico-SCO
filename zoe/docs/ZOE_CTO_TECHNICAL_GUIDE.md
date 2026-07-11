# ZOE — Guía Técnica para CTO

> **Documento para el equipo técnico directivo.**
> **Propósito:** entender la arquitectura de ZOE en profundidad, cómo sacarle máximo partido, cómo extenderlo, cómo operarlo en producción y cómo contribuir al código.
> **Audiencia:** CTO, VP Engineering, Tech Leads, Staff Engineers, SREs, Arquitectos de solución.
> **Versión:** ZOE V1.6 — Julio 2026

---

## Tabla de contenidos

1. [Visión técnica de ZOE](#1-visión-técnica-de-zoe)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Estructura del código](#3-estructura-del-código)
4. [Bucle cognitivo (CognitiveLoopV5)](#4-bucle-cognitivo-cognitiveloopv5)
5. [Subsistema ALMA (identidad y trayectoria)](#5-subsistema-alma-identidad-y-trayectoria)
6. [Subsistema Metabolismo](#6-subsistema-metabolismo)
7. [Subsistema Memoria](#7-subsistema-memoria)
8. [Subsistema Periféricos (LLMs, sentidos, actuadores)](#8-subsistema-periféricos-llms-sentidos-actuadores)
9. [Subsistema Epistémico](#9-subsistema-epistémico)
10. [Cápsulas y marketplace](#10-cápsulas-y-marketplace)
11. [Stack de recursos (Fases 7A-7G)](#11-stack-de-recursos-fases-7a-7g)
12. [Adaptive Cognitive Depth (ACD)](#12-adaptive-cognitive-depth-acd)
13. [Federación B2B](#13-federación-b2b)
14. [API REST completa](#14-api-rest-completa)
15. [Operación en producción](#15-operación-en-producción)
16. [Performance y optimización](#16-performance-y-optimización)
17. [Seguridad y cumplimiento](#17-seguridad-y-cumplimiento)
18. [Cómo extender ZOE](#18-cómo-extender-zoe)
19. [Testing y CI/CD](#19-testing-y-cicd)
20. [Troubleshooting y debug](#20-troubleshooting-y-debug)
21. [Roadmap técnico](#21-roadmap-técnico)
22. [Glosario técnico](#22-glosario-técnico)

---

## 1. Visión técnica de ZOE

### 1.1 Tesis arquitectónica

ZOE no es un LLM ni un framework de agentes. **ZOE es un organismo cognitivo sintético (SCO)**: un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo, evolución arquitectural firmada, validación epistémica y cápsulas de conocimiento intercambiables.

La distinción clave con otros sistemas de IA:

| Sistema | Modelo | ZOE |
|---|---|---|
| **LLM directo (GPT-4, Claude)** | Llamada API stateless | LLM es un sentido periférico, no el cerebro |
| **Framework de agentes (LangChain, CrewAI)** | Orquestación de tools | Orquestación de un organismo con identidad y metabolismo |
| **RAG ( Retrieval Augmented Generation)** | Vector DB + LLM | Memoria viva multi-tipo + validación epistémica |
| **Multi-agent (AutoGen, Swarm)** | Agentes coordinados | Sub-agentes compitiendo en Global Workspace (Baars) |
| **ChatGPT Memory** | Memoria conversacional cloud | Memoria longitudinal soberana + 11 tipos |

### 1.2 Principios de diseño

1. **Soberanía por defecto**: ZOE vive en tu hardware. Cloud es opcional.
2. **Modularidad estricta**: cada subsistema se puede usar/reemplazar independientemente.
3. **Sin deconstruir**: las nuevas fases extienden, no reemplazan. CognitiveLoopV5 hereda de V4 que hereda de V3.
4. **Tests primero**: 952 tests automatizados, 100% pasando. Toda nueva feature requiere tests.
5. **Documentación en código**: cada módulo tiene docstring explicando qué hace y por qué.
6. **Backward compatibility**: las nuevas versiones no rompen las anteriores. ModelSpec se amplía con defaults.
7. **Observabilidad**: todo se loguea, todo se audita (Trajectory Chain).

### 1.3 Stack tecnológico

| Capa | Tecnología | Por qué |
|---|---|---|
| Lenguaje | Python 3.10+ | Madurez, ecosistema IA, facilidad de extensión |
| Async IO | asyncio + aiohttp | Bucle cognitivo continuo, WebSocket dashboard |
| LLMs locales | Ollama (llama.cpp internamente) | Estándar de facto, mmap, flash attention |
| LLMs cloud | OpenAI, Anthropic, DeepSeek, Groq, Kimi, ZAI | Multi-cloud, no lock-in |
| Memoria persistente | SQLite (default), PostgreSQL (optional) | SQLite embeddable, PostgreSQL para escala |
| Memoria vectorial | numpy + cosine similarity (default), pgvector (optional) | Simple, sin dependencias |
| Frontend | HTML/CSS/JS vanilla embebido | Sin build step, sin dependencias npm |
| Tests | pytest + pytest-asyncio | Estándar Python, soporta async |
| Empaquetado | setuptools + pip | Estándar Python |
| CI/CD | GitHub Actions (en roadmap) | Integrado con GitHub |

---

## 2. Arquitectura del sistema

### 2.1 Diagrama de componentes

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
│  │  │ (ACD L0-L3)     │              │ (LRU)             │      │   │
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
│  └──────────────────────────────────────────────────────────────┘  │
│         ↑                                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           META-COGNITION (Kahneman System 1/2)               │  │
│  │           ACTIVE INFERENCE (Friston Free Energy)             │  │
│  │           COGNITIVE LAWS (6) + PHYSICS (12) + FIELDS (6)     │  │
│  │           COGNITIVE TENSIONS (5)                             │  │
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
│  │   12 cápsulas operativas, scaffold CLI, marketplace API      │  │
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
│  │   llm.py: Mock, Ollama, OpenAI, Anthropic, ZAI               │  │
│  │   senses.py: Clock, UserInput, Filesystem, Network, Agent    │  │
│  │   actuators.py: Language, Code, Memory, Federation           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↑ ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  INTERFACES (CLI, Web Dashboard, API REST)          │
│   cli_chat.py | web_dashboard.py (aiohttp + WebSocket) | REST API  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de una petición

```
Usuario escribe mensaje en Dashboard
    ↓
WebSocket envía a web_dashboard.py
    ↓
ZoeChat (CLI/Dashboard) recibe el mensaje
    ↓
CognitiveLoopV5.step(user_input)
    ↓
1. Senses.observation(user_input) → Observation object
    ↓
2. DepthClassifier.classify(observation) → ACD level (L0/L1/L2/L3)
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
8. Backend.generate(prompt, system, max_tokens, temperature)
    ↓
9. Streaming response → WebSocket → browser
    ↓
10. LivingMemory.store(episode)
    ↓
11. EpistemicValidator.evaluate_response() → quarantine si necesario
    ↓
12. TrajectoryChain.sign_mutation()
    ↓
13. (opcional) FederationManager.broadcast_mutation()
```

---

## 3. Estructura del código

### 3.1 Layout del repositorio

```
ZOE-Organismo-Cognitivo-Sintetico-SCO/
├── setup.py                    # pip install -e . + 4 entry points
├── requirements.txt            # Dependencias
├── pytest.ini                  # Configuración tests
├── README.md                   # Documentación principal (2800+ líneas)
├── LICENSE                     # Apache 2.0
└── zoe/                        # Paquete principal
    ├── __init__.py             # v1.6.0, phase_7g
    ├── cli_chat.py             # CLI Chat interactivo (entry point: zoe-chat)
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
    │   ├── cognitive_loop_v3.py       # V3 (SQLite + MO V2)
    │   ├── cognitive_loop_v4.py       # V4 (DeepConsolidation, graceful shutdown)
    │   ├── cognitive_loop_v5.py       # V5 actual (ACD + streaming)
    │   ├── depth_classifier.py        # ACD
    │   ├── cognitive_cache.py         # Cache LRU
    │   ├── epistemic_validator.py     # Validación epistémica
    │   ├── knowledge_quarantine.py    # Cuarentena activa
    │   ├── cross_validator.py         # Triple verificación
    │   ├── epistemic_federation.py    # Federación entre ZOEs
    │   ├── epistemic_federation_server.py  # Server/client HTTP
    │   ├── capsule_manager.py         # Gestión de cápsulas en runtime
    │   ├── mentor.py                  # Tutor Mentor Digital (Fase 6C)
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
    │   ├── model_optimizer.py         # 7F + 7G: mmap, P-cores, IQ2_M
    │   ├── resource_planner.py        # 7C: plan ACD+metabolismo+sensible
    │   ├── embodiment_composer.py     # 7D: boot sequence
    │   ├── seed_mode.py               # 7E: semilla portátil
    │   └── subagents/                 # 12 sub-agentes
    │       ├── perceiver.py
    │       ├── forecaster.py
    │       ├── speaker.py
    │       ├── critic.py
    │       └── phase2_subagents.py    # 8 sub-agentes adicionales
    ├── metabolism/              # 4 estados + consolidación
    │   └── metabolism.py
    ├── memory/                  # 11 tipos + SQLite + deep consolidation
    │   ├── memory_types.py
    │   ├── persistent_store.py
    │   └── deep_consolidation.py
    ├── peripherals/             # LLMs + sentidos + actuadores
    │   ├── llm.py               # 5 backends + streaming
    │   ├── senses.py            # 5 sentidos
    │   ├── resource_discovery.py # 7A: descubre hardware/cloud/peers
    │   ├── model_bus.py          # 7B: Universal Model Bus (ACD-aware)
    │   └── actuators.py         # 4 actuadores
    ├── capsules/                # 13 cápsulas + sistema
    │   ├── schema.py / loader.py / registry.py / scaffold.py
    │   ├── CAPSULE_MATRIX.md
    │   └── [13 directorios de cápsulas]
    ├── marketplace/             # Marketplace de cápsulas y YAML
    ├── use_cases/               # 7 YAML + runner
    ├── config/                  # production.yaml, development.yaml
    ├── docs/                    # Guía V1 + auditoría PDF
    ├── phases/                  # Planes y resultados por fase
    ├── tests/                   # 40 archivos, 952 tests
    ├── examples/                # Demos
    └── scripts/                 # deploy.sh, install_pendrive_macos.sh
```

### 3.2 Entry points (setup.py)

```python
entry_points={
    'console_scripts': [
        'zoe-chat=zoe.cli_chat:main',
        'zoe-dashboard=zoe.web_dashboard:main',
        'zoe-use-case=zoe.use_cases.run_use_case:main',
        'zoe-capsules=zoe.capsules.scaffold:main',
    ],
}
```

### 3.3 Dependencias (requirements.txt)

- `aiohttp` — Web Dashboard + REST API
- `pyyaml` — Config + use cases YAML
- `pytest` + `pytest-asyncio` — Tests
- `requests` — LLM API clients (síncrono fallback)
- `psutil` (opcional) — Detección de RAM mejorada
- `openai` — OpenAI API
- `anthropic` — Anthropic API

**Sin dependencias pesadas.** Sin PyTorch, sin transformers, sin LangChain. ZOE usa LLMs vía API, no carga modelos directamente.

---

## 4. Bucle cognitivo (CognitiveLoopV5)

### 4.1 Jerarquía de versiones

| Versión | Añade | Estado |
|---|---|---|
| CognitiveLoop (V0) | Observar-predecir-evaluar-decidir-actuar | ✅ |
| CognitiveLoopV05 | 6 leyes + 12 física + 6 campos + 5 tensiones | ✅ |
| CognitiveLoopV3 | SQLite + MO V2 arquitectural | ✅ |
| CognitiveLoopV4 | DeepConsolidation + graceful shutdown + auto-save | ✅ |
| **CognitiveLoopV5** | **ACD + Cache + Streaming (actual)** | ✅ |

V5 hereda de V4 que hereda de V3. **Sin deconstruir**: cada versión extiende.

### 4.2 CognitiveLoopV5._tick()

```python
async def _tick(self) -> None:
    """Ejecuta una iteración del bucle cognitivo V5."""
    # 1. Ejecutar tick de V4 (que ejecuta V3, etc.)
    await super()._tick()
    
    # 2. ACD: clasificar profundidad
    acd_level = self.depth_classifier.classify(self.last_observation)
    
    # 3. Check cache (LRU)
    cache_key = self._compute_cache_key(self.last_observation, acd_level)
    if cached := self.cognitive_cache.get(cache_key):
        return cached  # hit, sin llamar LLM
    
    # 4. Generar respuesta con streaming
    async for token in self._stream_response(acd_level):
        yield token
    
    # 5. Guardar en cache
    self.cognitive_cache.set(cache_key, response)
```

### 4.3 States y transitions

```python
class InternalState:
    energy: float          # 0-1, baja con uso
    fatigue: float         # 0-1, sube con uso
    arousal: float         # 0-1, sube con estímulos
    attention: float       # 0-1, derivado de energy + arousal
    iteration_count: int   # contador de ticks
```

El `tick(dt)` actualiza estos valores según las 6 leyes cognitivas y 12 magnitudes físicas.

---

## 5. Subsistema ALMA (identidad y trayectoria)

### 5.1 IdentityVault

```python
class IdentityVault:
    """
    Identidad criptográfica soberana de ZOE.
    
    Contiene:
    - organism_id: UUID único
    - identity_hash: SHA-256 del vault
    - birth_date: timestamp de creación
    - lineage: árbol genealógico (si proviene de otro ZOE)
    - capabilities: lista de capacidades declaradas
    - values: valores éticos fundamentales
    """
    
    def __init__(self, organism_id=None, lineage=None):
        self.organism_id = organism_id or str(uuid.uuid4())
        self.birth_date = time.time()
        self.lineage = lineage or []
        self.capabilities = []
        self.values = []
        self.identity_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """SHA-256 del contenido del vault."""
        ...
```

### 5.2 TrajectoryChain

```python
class TrajectoryChain:
    """
    Cadena firmada de mutaciones (blockchain-style).
    
    Cada mutación contiene:
    - timestamp
    - mutation_type (capsule_loaded, value_changed, capability_added, etc.)
    - payload (datos de la mutación)
    - previous_hash (hash de la mutación anterior)
    - hash (hash de esta mutación)
    - signature (firma criptográfica del organismo)
    
    La cadena es inmutable: cualquier intento de modificar una mutación
    anterior invalida todas las posteriores.
    """
    
    def add_mutation(self, mutation_type: str, payload: dict) -> str:
        """Añade una mutación a la cadena. Devuelve el hash."""
        ...
```

### 5.3 OntogeneticMotorV2

Motor de desarrollo ontogenético: ZOE evoluciona su arquitectura interna según la experiencia. Versión V2 añade promoción de capacidades (de "experimentales" a "estables") y degradación de capacidades no usadas.

---

## 6. Subsistema Metabolismo

### 6.1 MetabolicState

```python
class MetabolicState(str, Enum):
    AWAKE = "awake"           # estado normal
    DROWSY = "drowsy"         # fatiga acumulada
    SLEEPING = "sleeping"     # consolidación de memoria
    WAKING = "waking"         # transición
```

### 6.2 Transiciones

```python
def _update_metabolic_state(self) -> None:
    """Transiciones de estado metabólico."""
    fatigue = self.internal_state.fatigue
    
    if self.state == MetabolicState.AWAKE:
        if fatigue > self.drowsy_threshold:  # 0.6
            self.state = MetabolicState.DROWSY
    
    if self.state == MetabolicState.DROWSY:
        if fatigue > self.sleep_threshold:  # 0.8
            self._go_to_sleep()
        elif fatigue < self.wake_threshold:  # 0.3
            self.state = MetabolicState.AWAKE
    
    if self.state == MetabolicState.SLEEPING:
        if self.energy > 0.8 and self.fatigue < 0.2:
            self._wake_up()
```

### 6.3 Consolidación durante el sueño

Cuando ZOE duerme, ejecuta `DeepConsolidation`:
- Reorganiza memoria episódica
- Fusiona memorias similares
- Generaliza patrones
- Mueve memorias de corto plazo a largo plazo
- Elimina memorias obsoletas

Esto es análogo al sueño humano donde el cerebro consolida lo aprendido.

---

## 7. Subsistema Memoria

### 7.1 Los 11 tipos de memoria

```python
class MemoryType(str, Enum):
    # Corto plazo
    WORKING = "working"              # memoria de trabajo (frenética)
    EPISODIC_SHORT = "episodic_short" # eventos recientes
    
    # Largo plazo
    EPISODIC = "episodic"            # eventos específicos con timestamp
    SEMANTIC = "semantic"            # hechos y conceptos
    PROCEDURAL = "procedural"        # cómo hacer cosas (skills)
    EMOTIONAL = "emotional"          # asociaciones emocionales
    SPATIAL = "spatial"              # contextos espaciales
    TEMPORAL = "temporal"            # secuencias temporales
    
    # Meta
    META_COGNITIVE = "meta_cognitive" # memoria sobre su propio pensamiento
    INTENTIONAL = "intentional"       # intenciones y planes
    SOCIAL = "social"                 # relaciones con otros
```

### 7.2 LivingMemory

`LivingMemory` es la memoria "en caliente" — la que ZOE consulta en cada tick. Es una estructura en memoria con persistencia opcional.

```python
class LivingMemory:
    def store(self, memory_type: MemoryType, content: dict) -> str:
        """Almacena un recuerdo. Devuelve ID."""
        ...
    
    def retrieve(self, query: str, memory_types: List[MemoryType], 
                 limit: int = 10) -> List[Memory]:
        """Recupera recuerdos relevantes por similitud semántica."""
        ...
    
    def consolidate(self) -> int:
        """Ejecuta consolidación (durante SLEEPING). Devuelve núm. consolidados."""
        ...
```

### 7.3 PersistentMemoryStore

Persistencia en SQLite (default) o PostgreSQL (optional). Dos clases:

- `PersistentMemoryStore` — store key-value genérico
- `PersistentLivingMemory` — wrapper que sincroniza LivingMemory con SQLite

```python
class PersistentMemoryStore:
    def __init__(self, db_path: str = "zoe_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def save_to_disk(self) -> int: ...
    def load_from_disk(self) -> int: ...
    def count_entries(self) -> int: ...
```

### 7.4 DeepConsolidation

Consolidación profunda durante SLEEPING:

```python
class DeepConsolidation:
    def consolidate(self, living_memory: LivingMemory) -> Dict[str, int]:
        """Ejecuta consolidación profunda. Devuelve stats."""
        return {
            "episodes_merged": ...,
            "patterns_generalized": ...,
            "memories_promoted_to_long_term": ...,
            "obsolete_memories_pruned": ...,
        }
```

---

## 8. Subsistema Periféricos (LLMs, sentidos, actuadores)

### 8.1 LLMPeripheral (abstract)

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
                                  max_tokens: int = 300, temperature: float = 0.7) -> AsyncIterator[str]: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
    
    @property
    def supports_streaming(self) -> bool:
        return True
```

### 8.2 Implementaciones concretas

| Clase | Backend | Cuándo usar |
|---|---|---|
| `MockPeripheral` | Mock (no LLM) | Tests, desarrollo |
| `OllamaPeripheral` | Ollama local | Producción B2C, privacidad |
| `OpenAICompatiblePeripheral` | OpenAI, DeepSeek, Groq, Kimi | Calidad cloud |
| `AnthropicPeripheral` | Anthropic Claude | Calidad cloud, ética |
| `ZAIPeripheral` | z-ai CLI | Integración ZAI |

### 8.3 Cambio de LLM en caliente

```python
# Desde CLI
zoe> /llm anthropic

# Desde Dashboard
POST /llm {"backend": "anthropic", "model": "claude-sonnet-4-20250514"}

# Desde código
chat.switch_llm(backend="anthropic", model="claude-sonnet-4-20250514", api_key="...")
```

El cambio es instantáneo, sin reiniciar ZOE. La memoria y trayectoria se conservan.

### 8.4 Senses

5 sentidos que producen `Observation` objects:

```python
class Senses:
    async def observe(self) -> List[Observation]:
        """Recoge observaciones de todos los sentidos activos."""
        observations = []
        if self.clock: observations.append(await self._observe_clock())
        if self.user_input: observations.append(await self._observe_user_input())
        if self.filesystem: observations.append(await self._observe_filesystem())
        if self.network: observations.append(await self._observe_network())
        if self.agent: observations.append(await self._observe_agents())
        return observations
```

### 8.5 Actuators

4 actuadores que ejecutan acciones:

```python
class Actuators:
    async def act(self, action: Action) -> Any:
        if action.type == "language":
            return await self._speak(action.payload)
        elif action.type == "code":
            return await self._execute_code(action.payload)
        elif action.type == "memory":
            return await self._store_memory(action.payload)
        elif action.type == "federation":
            return await self._federate(action.payload)
```

---

## 9. Subsistema Epistémico

### 9.1 EpistemicValidator

Cuantifica la confianza de ZOE en sus afirmaciones:

```python
class EpistemicValidator:
    def validate(self, claim: str, sources: List[str]) -> ValidationResult:
        """
        Valida una afirmación.
        
        Returns:
            ValidationResult con:
            - confidence: 0-1 (cuánto confía ZOE)
            - uncertainty: 0-1 (cuánto no sabe)
            - sources: lista de fuentes
            - status: VERIFIED / LIKELY / UNCERTAIN / QUARANTINED
        """
        ...
```

### 9.2 KnowledgeQuarantine

Conocimiento nuevo va a cuarentena hasta validación:

```python
class KnowledgeQuarantine:
    def add(self, claim: str, source: str) -> str:
        """Añade claim a cuarentena. Devuelve entry_id."""
        ...
    
    def promote(self, entry_id: str, second_source: str) -> bool:
        """Promueve claim a conocimiento confiable (2 fuentes)."""
        ...
    
    def reject(self, entry_id: str, reason: str) -> bool:
        """Rechaza claim (no se aplica)."""
        ...
```

### 9.3 CrossValidator

Triple verificación con 2 fuentes independientes:

```python
class CrossValidator:
    async def cross_validate(self, claim: str, source_a: str, 
                              source_b: str) -> CrossValidationResult:
        """
        Verifica claim con dos fuentes independientes.
        
        Si ambas confirman → VERIFIED
        Si solo una → LIKELY (cuarentena extendida)
        Si ninguna → REJECTED
        """
        ...
```

### 9.4 EpistemicFederation

Federación B2B con quorum y veto:

```python
class EpistemicFederation:
    async def propose_mutation(self, mutation: Mutation) -> str:
        """Propone mutación a la federación. Devuelve proposal_id."""
        ...
    
    async def vote(self, proposal_id: str, vote: Vote) -> bool:
        """Vota sobre una propuesta. Vote = YES / NO / VETO."""
        ...
    
    async def check_quorum(self, proposal_id: str) -> QuorumStatus:
        """Verifica si la propuesta tiene quorum (2/3)."""
        ...
```

---

## 10. Cápsulas y marketplace

### 10.1 Estructura de una cápsula

```
zoe/capsules/elder_care_knowledge/
├── capsule.yaml              # Metadata
├── semantic_memory.jsonl     # Hechos
├── procedural_skills.jsonl   # Cómo hacer cosas
├── causal_models.jsonl       # Causa-efecto
├── emotional_patterns.jsonl  # Patrones emocionales
├── ethical_guidelines.jsonl  # Restricciones éticas
├── validators.py             # Validadores ejecutables
├── tools/                    # (opcional) Código Python
└── prompts/                  # (opcional) System prompts
```

### 10.2 capsule.yaml schema

```yaml
name: elder_care_knowledge
version: 1.0.0
description: "Knowledge base para cuidado geriátrico en domicilio"
domain: healthcare.elders.home_care
trust_level: verified  # verified | curated | community | experimental
provenance: "Manual SEGG 2024 + NICE NG108 + OMS Active Ageing 2023"
last_updated: 2026-06-15

depends_on:
  - basic_psychology

compatible_use_cases:
  - cuidado_personas_mayores
  - compania_personas_solas

load_cost: 0.15  # costo computacional estimado
default_confidence: 0.85

components:
  semantic_memory: true
  procedural_skills: false
  causal_models: true
  emotional_patterns: true
  ethical_guidelines: true
  validators: true
  tools: false
  prompts: false

capabilities:
  - detect_fall_risk_patterns
  - identify_depression_geriatric_signs
  - recognize_dementia_early_markers
  - validate_medication_interactions_basic
  - assess_routine_deviations

restrictions:
  - no_medication_modification
  - no_diagnosis
  - require_external_verification_for_emergency
  - no_paternalistic_tone

expires_at: null  # null = no expira
```

### 10.3 CapsuleLoader

```python
class CapsuleLoader:
    def load(self, capsule_name: str) -> LoadedCapsule:
        """Carga una cápsula desde filesystem."""
        ...
    
    def load_for_use_case(self, use_case: str, config: dict) -> List[LoadedCapsule]:
        """Carga todas las cápsulas compatibles con un caso de uso."""
        ...
```

### 10.4 CapsuleManager

Gestiona cápsulas activas en runtime:

```python
class CapsuleManager:
    def __init__(self, organism: CognitiveLoopV5, 
                 epistemic_validator: EpistemicValidator):
        ...
    
    def load(self, capsule_name: str) -> CapsuleLoadResult:
        """Carga cápsula en runtime (sin reiniciar)."""
        ...
    
    def unload(self, capsule_name: str) -> bool:
        """Descarga cápsula."""
        ...
    
    def list_loaded(self) -> List[str]:
        """Lista cápsulas cargadas."""
        ...
```

### 10.5 Scaffold CLI

```bash
# Crear nueva cápsula
zoe-capsules create mi_capsula --domain health.nutrition --trust curated

# Validar cápsula
zoe-capsules validate mi_capsula

# Listar cápsulas disponibles
zoe-capsules list

# Ver matriz de cápsulas
zoe-capsules matrix
```

---

## 11. Stack de recursos (Fases 7A-7G)

### 11.1 Visión general

El stack 7A-7G es la capa de orquestación de recursos. Resuelve: **dónde, cuándo y cómo ejecutar cada tarea cognitiva**.

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

### 11.2 Fase 7A — Resource Discovery

```python
class ResourceDiscoverySense:
    """Descubre recursos de cómputo en el entorno."""
    
    async def observe(self) -> List[Observation]:
        """Ejecuta scan completo y devuelve observaciones."""
        # 1. Hardware local: CPU, RAM, Apple Silicon, NVIDIA GPU
        # 2. Ollama instances: localhost:11434 + red local
        # 3. Cloud APIs: OpenAI, Anthropic, etc. (según env vars)
        # 4. Otros ZOEs federados
        # 5. Almacenamiento: disco local, pendrive, NAS
        ...
    
    def get_graph(self) -> ResourceGraph: ...
```

### 11.3 Fase 7B — Universal Model Bus

```python
class ModelBus(LLMPeripheral):
    """Bus que gestiona múltiples LLMs simultáneamente."""
    
    def add_backend(self, peripheral: LLMPeripheral, name: str,
                    priority: int, cost_per_1k: float, 
                    privacy: str, tags: List[str]): ...
    
    def select_backend(self, acd_level: str = None,
                       sensitive_domain: bool = False,
                       prefer_local: bool = False) -> Optional[BackendEntry]:
        """Selecciona el mejor backend según contexto."""
        ...
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Genera con backend óptimo + fallback automático."""
        ...
    
    @classmethod
    def from_resource_graph(cls, graph: ResourceGraph) -> "ModelBus":
        """Construye bus desde ResourceGraph (7A)."""
        ...
```

### 11.4 Fase 7C — Metabolic Resource Planner

```python
class ResourcePlanner:
    """Planifica dónde ejecutar cada tarea cognitiva."""
    
    def plan(self, acd_level: str, metabolic_state: str,
             sensitive_domain: bool, available_ram_gb: float,
             model_bus: ModelBus, resource_graph: ResourceGraph = None,
             model_optimizer: ModelOptimizer = None) -> ResourcePlan:
        """
        Combina: ACD + metabolismo + dominio + recursos + optimizador.
        
        Returns:
            ResourcePlan con backend, modelo, estrategia y razón.
        """
        ...
```

### 11.5 Fase 7D — Embodiment Composer

```python
class EmbodimentComposer:
    """Boot sequence: plan → check → instantiate."""
    
    def validate_prerequisites(self, plan: ResourcePlan,
                                model_bus: ModelBus) -> ValidationResult:
        """7 checks: plan_will_work, backend_exists, backend_available,
        ram_sufficient, ollama_running, cloud_api_key, plan_warning."""
        ...
    
    def compose(self, plan: ResourcePlan, model_bus: ModelBus,
                memory_store=None, capsules=None) -> Embodiment:
        """Instancia Embodiment desde un plan."""
        ...
    
    def bootstrap_from_scratch(self, acd_level="L2_STANDARD",
                                metabolic_state="awake",
                                sensitive_domain=False,
                                available_ram_gb=None,
                                capsules=None) -> Embodiment:
        """Pipeline completo: 7A → 7B → 7C → 7D."""
        ...
```

### 11.6 Fase 7E — ZOE Seed Mode

```python
class ZOESeed:
    """Semilla portátil que germina en cualquier host."""
    
    def detect_seed_volume(self, custom_paths=None) -> Optional[SeedVolume]:
        """Busca semilla en /Volumes/*, /media/*, ~/.zoe-seed/, $ZOE_SEED_PATH."""
        ...
    
    def create(self, volume_path: str, organism_id: str, ...) -> GerminationReport:
        """Crea nueva semilla en un volumen."""
        ...
    
    def validate_seed(self, seed_volume: SeedVolume) -> Tuple[bool, List[str]]:
        """Valida integridad: manifiesto, directorios, versión, organism_id."""
        ...
    
    def germinate(self, custom_paths=None, acd_level=None,
                  force_allow_cloud=True) -> GerminationReport:
        """Pipeline completo de germinación: detect → validate → RAM → 
        capsules → bootstrap_from_scratch → memory → manifest update."""
        ...
```

### 11.7 Fase 7F + 7G — ModelOptimizer

```python
class ModelOptimizer:
    """7F: Cognitive Memory Paging (mmap para modelos grandes en 8GB)."""
    """7G: Hardware Optimization (P-cores, IQ2_M, flash-attn siempre)."""
    
    # 7F
    def detect_available_ram_gb(self) -> float: ...
    def detect_total_ram_gb(self) -> float: ...
    def detect_cpu_cores(self) -> int: ...
    def is_apple_silicon(self) -> bool: ...
    def optimize(self, model_name: str, available_ram_gb=None) -> OptimizationResult: ...
    def recommend_for_acd(self, ram_gb=None) -> Dict[str, Any]: ...
    
    # 7G
    def detect_p_cores(self) -> int:
        """Lee hw.perflevel0.physicalcpu en Apple Silicon."""
        ...
    
    def detect_e_cores(self) -> int:
        """Lee hw.perflevel1.physicalcpu en Apple Silicon."""
        ...
    
    def generate_ollama_env(self, result: OptimizationResult) -> Dict[str, str]:
        """
        Genera env vars óptimas:
        - OLLAMA_FLASH_ATTENTION=1 (siempre, 7G)
        - OLLAMA_NUM_THREAD = P-cores (7G)
        - OLLAMA_KEEP_ALIVE según estrategia
        - OLLAMA_MAX_LOADED_MODELS=1
        - OLLAMA_NUM_PARALLEL=1
        """
        ...
    
    def get_system_info(self) -> Dict[str, Any]:
        """Info con p_cores y e_cores (7G)."""
        ...
    
    # APIs estáticas para UX
    @staticmethod
    def get_recommended_ssds() -> List[Dict[str, Any]]: ...
    
    @staticmethod
    def get_expected_token_rates() -> List[Dict[str, Any]]: ...
    
    @staticmethod
    def get_cable_warning() -> Dict[str, str]: ...
```

### 11.8 MODEL_CATALOG con IQ2_M / IQ3_XS (7G)

```python
@dataclass
class ModelSpec:
    name: str
    params_b: float
    size_q4_gb: float
    size_q8_gb: float
    min_ram_gb: float
    mmap_ram_gb: float
    recommended_for: str
    ollama_tag: str
    # 7G: cuantizaciones avanzadas
    size_iq2_m_gb: float = 0.0   # ~30% del Q4, 95% calidad
    size_iq3_xs_gb: float = 0.0  # ~40% del Q4, 97% calidad
```

Lógica de selección en `optimize()`:
1. Si Q4_K_M cabe → usar Q4_K_M
2. Si no, probar IQ3_XS (mejor calidad)
3. Si no, probar IQ2_M (más comprimido)
4. Si no, MMAP_FULL con Q4_K_M
5. Si no, CLOUD_FALLBACK

---

## 12. Adaptive Cognitive Depth (ACD)

### 12.1 DepthClassifier

```python
class DepthClassifier:
    def classify(self, observation: Observation) -> str:
        """
        Clasifica la profundidad de pensamiento necesaria.
        
        Returns: "L0_REFLEX" | "L1_FAST" | "L2_STANDARD" | "L3_DEEP"
        """
        # Heurísticas:
        # - "Hola", "Gracias" → L0_REFLEX
        # - Pregunta simple con respuesta factual → L1_FAST
        # - Análisis medio, conversación normal → L2_STANDARD
        # - Análisis profundo, decisiones importantes → L3_DEEP
        ...
```

### 12.2 Niveles y configuración

| Nivel | Modelo preferido | Latencia target | Coste target |
|---|---|---|---|
| L0_REFLEX | Ollama 3B local | <1s | 0€ |
| L1_FAST | Ollama 3B/7B local | <3s | 0€ |
| L2_STANDARD | Ollama 7B local o cloud barato | <10s | <0.01€ |
| L3_DEEP | Cloud calidad (GPT-4o, Claude) | <60s | <0.10€ |

### 12.3 CognitiveCache

Cache LRU para evitar recalcular respuestas idénticas:

```python
class CognitiveCache:
    def __init__(self, max_size: int = 1000):
        self._cache = OrderedDict()
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[str]:
        """Cache hit → devuelve respuesta. Miss → None."""
        ...
    
    def set(self, key: str, value: str) -> None:
        """Guarda en cache. Evicta LRU si tamaño > max."""
        ...
```

---

## 13. Federación B2B

### 13.1 Arquitectura

```
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  ZOE Clínica │◄───►│ ZOE Hospital │◄───►│ ZOE Residencia│
    │  (peer A)    │     │  (peer B)    │     │  (peer C)    │
    └──────────────┘     └──────────────┘     └──────────────┘
            ▲                    ▲                    ▲
            └────────────────────┴────────────────────┘
                          │
                  Federation Protocol (HTTP)
                  - Propose mutation
                  - Vote (YES / NO / VETO)
                  - Check quorum (2/3)
                  - Apply if quorum
```

### 13.2 EpistemicFederationServer

```python
class EpistemicFederationServer:
    """Servidor HTTP para federación entre ZOEs."""
    
    async def start(self, port: int = 8643):
        """Inicia servidor de federación."""
        ...
    
    # Endpoints:
    # POST /federation/epistemic/validate       — validar claim
    # GET  /federation/epistemic/knowledge/{hash}  — obtener conocimiento
    # POST /federation/epistemic/register       — registrar peer
    # GET  /federation/epistemic/peers          — listar peers
    # GET  /federation/epistemic/stats          — stats federación
    # POST /federation/epistemic/request_validation  — pedir validación
```

### 13.3 Quorum y veto

- **Quorum**: 2/3 de peers activos deben votar YES
- **Veto**: cualquier peer puede vetar por violación de valores
- **Auditoría**: todo se registra en Trajectory Chain de cada ZOE

---

## 14. API REST completa

### 14.1 Endpoints por categoría

#### Core (CLI/Dashboard)
| Endpoint | Método | Descripción |
|---|---|---|
| `/` | GET | Dashboard HTML |
| `/ws` | GET | WebSocket (chat en tiempo real) |
| `/chat` | POST | Chat síncrono |
| `/feed` | POST | Subir archivo (file upload) |
| `/stats` | GET | Stats del organismo |
| `/memory` | GET | Memoria viva |
| `/identity` | GET | Identity Vault |
| `/state` | GET | InternalState |
| `/sleep` | POST | Forzar SLEEPING |
| `/wake` | POST | Forzar AWAKE |
| `/llm` | POST | Cambiar LLM en caliente |
| `/history` | GET | Histórico conversaciones |
| `/federation` | GET | Estado federación |

#### Cápsulas (6B)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/capsules` | GET | Lista cápsulas disponibles |
| `/api/capsules/loaded` | GET | Cápsulas cargadas |
| `/api/capsules/load` | POST | Cargar cápsula |
| `/api/capsules/unload` | POST | Descargar cápsula |
| `/api/capsules/{name}/info` | GET | Info de cápsula |
| `/api/capsules/{name}/validate` | POST | Validar cápsula |
| `/api/capsules/create` | POST | Crear nueva cápsula |

#### Epistémico (6A)
| Endpoint | Método | Descripción |
|---|---|---|
| `/federation/epistemic/validate` | POST | Validar claim |
| `/federation/epistemic/knowledge/{hash}` | GET | Obtener conocimiento |
| `/federation/epistemic/register` | POST | Registrar peer |
| `/federation/epistemic/peers` | GET | Listar peers |
| `/federation/epistemic/stats` | GET | Stats federación |
| `/federation/epistemic/request_validation` | POST | Pedir validación |

#### Cuarentena (6A)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/quarantine` | GET | Lista cuarentena |
| `/api/quarantine/stats` | GET | Stats cuarentena |
| `/api/quarantine/{id}/promote` | POST | Promover a confiable |
| `/api/quarantine/{id}/reject` | POST | Rechazar |

#### Marketplace (6B)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Lista cápsulas marketplace |
| `/api/marketplace/upload` | POST | Subir cápsula |
| `/api/marketplace/download/{name}` | POST | Descargar cápsula |
| `/api/marketplace/use_cases` | GET | Lista casos de uso |
| `/api/marketplace/upload_use_case` | POST | Subir caso de uso |

#### Mentor (6C)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/mentor` | GET | Config mentor |
| `/api/mentor` | POST | Actualizar mentor |
| `/api/mentor/stats` | GET | Stats mentor |

#### Model Optimizer (7F + 7G)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/models/system_info` | GET | Info hardware (con p_cores, e_cores) |
| `/api/models/recommend` | GET | Recomendaciones por ACD |
| `/api/models/catalog` | GET | Catálogo modelos |
| `/api/models/optimize` | POST | Optimizar modelo específico |

#### Hardware (7G)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/hardware/ssds` | GET | SSDs recomendados |
| `/api/hardware/token_rates` | GET | Tabla tokens/s esperadas |
| `/api/hardware/cable_warning` | GET | Warning cable USB-C |
| `/api/hardware/system` | GET | Info hardware host |

#### Resource Discovery (7A)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/resources` | GET | Grafo recursos |
| `/api/resources/stats` | GET | Stats recursos |
| `/api/resources/scan` | POST | Ejecutar scan |

#### Model Bus (7B)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/modelbus` | GET | Lista backends |
| `/api/modelbus/stats` | GET | Stats bus |
| `/api/modelbus/select` | POST | Seleccionar backend óptimo |

#### Resource Planner (7C)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/planner/plan` | POST | Generar plan |
| `/api/planner/stats` | GET | Stats planner |
| `/api/planner/recommend` | GET | Recomendaciones |

#### Embodiment Composer (7D)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/embodiment/compose` | POST | Componer desde plan |
| `/api/embodiment/bootstrap` | POST | Pipeline completo |
| `/api/embodiment/status` | GET | Estado composer |
| `/api/embodiment/list` | GET | Lista embodiments |
| `/api/embodiment/tear_down` | POST | Detener embodiment |
| `/api/embodiment/log` | GET | Log composiciones |

#### Seed Mode (7E)
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/seed/detect` | GET | Detectar semilla |
| `/api/seed/inspect` | GET | Inspeccionar semilla |
| `/api/seed/create` | POST | Crear semilla |
| `/api/seed/germinate` | POST | Germinar semilla |
| `/api/seed/stats` | GET | Stats ZOESeed |
| `/api/seed/last_report` | GET | Último reporte germinación |

**Total: 50+ endpoints REST**

### 14.2 WebSocket events

El WebSocket `/ws` soporta eventos bidireccionales:

**Cliente → Servidor:**
- `{cmd: "chat", message: "..."}` — enviar mensaje
- `{cmd: "stats"}` — pedir stats
- `{cmd: "memory"}` — pedir memoria
- `{cmd: "sleep"}` — forzar sleep
- `{cmd: "wake"}` — forzar wake

**Servidor → Cliente:**
- `{type: "chat_token", token: "..."}` — token de respuesta streaming
- `{type: "chat_end", full: "..."}` — respuesta completa
- `{type: "state", state: {...}}` — actualización de estado (cada 1s)
- `{type: "thought", thought: "..."}` — pensamiento autónomo
- `{type: "metabolism", state: "..."}` — cambio metabólico

---

## 15. Operación en producción

### 15.1 Despliegue en servidor Linux

```bash
# 1. Setup servidor (Ubuntu 22.04+)
sudo apt update && sudo apt install -y python3.12 python3.12-venv git

# 2. Clonar
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 3. Venv + install
python3.12 -m venv venv
source venv/bin/activate
pip install -e .

# 4. Configurar
cp zoe/config/production.yaml zoe/config/myproduction.yaml
# Editar myproduction.yaml con tu config

# 5. Iniciar
ZOE_ENV=production python -m zoe.serve --config zoe/config/myproduction.yaml
```

### 15.2 Systemd service

```ini
# /etc/systemd/system/zoe.service
[Unit]
Description=ZOE Synthetic Cognitive Organism
After=network.target

[Service]
Type=simple
User=zoe
WorkingDirectory=/opt/ZOE-Organismo-Cognitivo-Sintetico-SCO
Environment=ZOE_ENV=production
ExecStart=/opt/ZOE-Organismo-Cognitivo-Sintetico-SCO/venv/bin/python -m zoe.serve
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable zoe
sudo systemctl start zoe
sudo systemctl status zoe
```

### 15.3 Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8642
CMD ["python", "-m", "zoe.serve", "--config", "zoe/config/production.yaml"]
```

```bash
docker build -t zoe:latest .
docker run -d -p 8642:8642 --name zoe zoe:latest
```

### 15.4 Monitoreo

ZOE expone métricas en `/stats` y logs estructurados. Para producción:

- **Prometheus**: scrapear `/stats` cada 30s
- **Grafana**: dashboards con estado, memoria, latencia
- **OpenTelemetry**: traces distribuidos (config en `infra/otel/collector.yml`)
- **Loki/ELK**: logs centralizados

Métricas clave a monitorizar:
- `iteration_count` — ticks del bucle cognitivo
- `metabolic_state` — AWAKE/DROWSY/SLEEPING
- `energy`, `fatigue`, `arousal` — estado interno
- `modelbus.success_rate` — tasa de éxito de LLM calls
- `modelbus.fallback_count` — número de fallbacks
- `cache.hit_rate` — tasa de cache hits
- `quarantine.size` — items en cuarentena
- `trajectory.mutations` — mutaciones en la cadena

### 15.5 Backup

**Crítico:**
- `zoe_data/dashboard_memory.db` — memoria persistente
- `zoe_data/identity_vault.json` — identidad
- `zoe_data/trajectory_chain.json` — trayectoria

**Backup strategy:**
```bash
# Diario (cron)
0 3 * * * tar -czf /backups/zoe_$(date +\%Y\%m\%d).tar.gz zoe_data/

# Retención 30 días
find /backups/ -mtime +30 -delete
```

### 15.6 Escalado

ZOE es **single-tenant por diseño**: cada instancia es un organismo. Para escalar:

- **Vertical**: más RAM, mejor GPU (modelos más grandes)
- **Horizontal**: múltiples ZOEs federados (Fase 6A)
- **Cloud**: Kubernetes con un pod por ZOE (Helm chart en `infra/helm/`)

No recomendamos compartir un ZOE entre usuarios — perdería la identidad personal.

---

## 16. Performance y optimización

### 16.1 Modelos locales en Mac 8GB (Fase 7F + 7G)

ZOE puede ejecutar modelos de 70B en MacBook Air 8GB gracias a:

1. **Cognitive Memory Paging (mmap)**: el modelo se memory-mapea desde SSD. Solo las capas activas cargan en RAM.
2. **Detección de P-cores**: `OLLAMA_NUM_THREAD = P-cores` (no total cores). Usar E-cores DEGRADA rendimiento.
3. **Flash Attention siempre activo**: reduce cómputo en contextos largos hasta 40%.
4. **Cuantizaciones IQ2_M / IQ3_XS**: modelos 30B+ caben en 8GB (5-9GB vs 18-40GB con Q4).

**Velocidades esperadas (MacBook Air M2/M3 8GB + SSD 2000 MB/s):**

| Modelo | Cuantización | Tokens/s | Experiencia |
|---|---|---|---|
| Qwen 2.5 3B | Q4_K_M | 25-35 | Más rápido que lectura |
| Qwen 2.5 7B | Q4_K_M | 12-18 | Tipo ChatGPT gratuito |
| Qwen 2.5 14B | Q4_K_M | 4-8 | Lectura pausada |
| Qwen 2.5 32B | IQ2_M | 3-6 | Análisis background |
| Qwen 2.5 72B | IQ2_M | 1-3 | Lento pero funcional |

### 16.2 ACD optimization

ACD optimiza coste automáticamente:
- L0/L1 → local 3B (gratis, rápido)
- L2 → local 7B o cloud barato
- L3 → cloud calidad (GPT-4o, Claude)

Para tareas simples, ZOE gasta 0€. Para tareas complejas, gasta ~€0.05. Sin configuración manual.

### 16.3 CognitiveCache

Cache LRU evita recalcular respuestas idénticas. Configurable:

```python
CognitiveCache(max_size=1000)  # 1000 respuestas cacheadas
```

Tasa de hit típica: 15-30% en conversaciones normales.

### 16.4 Streaming

Las respuestas se streamen via WebSocket. El usuario ve tokens según se generan, no espera a la respuesta completa. **Mejora UX perceived latency en 60-80%.**

### 16.5 Profiling

```python
import cProfile
import pstats

with cProfile.Profile() as pr:
    await zoe.run_turn("mensaje del usuario")

stats = pstats.Stats(pr)
stats.sort_stats("cumulative").print_stats(20)
```

Hot paths típicos:
- `LLMPeripheral.generate()` — 80-95% del tiempo
- `LivingMemory.retrieve()` — 5-10%
- `DepthClassifier.classify()` — 1-3%

---

## 17. Seguridad y cumplimiento

### 17.1 Modelo de amenazas

| Amenaza | Vector | Mitigación |
|---|---|---|
| Robo de identidad | Alguien se hace pasar por tu ZOE | Identity Vault con SHA-256, no falsificable |
| Manipulación de trayectoria | Modificar mutaciones pasadas | Trajectory Chain con hashes encadenados (blockchain-style) |
| Inyección de conocimiento falso | Convencer a ZOE de algo falso | Quarantine + Cross-Validator (2 fuentes) |
| Exfiltración de datos | Cloud API envía datos a terceros | Modo offline, cloud es opt-in |
| Federación maliciosa | Peer malicioso propone mutaciones dañinas | Veto por valores, quorum 2/3, auditoría |
| Prompt injection | Usuario intenta extraer system prompt | Validators en Speaker, EthicalMotor |

### 17.2 GDPR compliance

**Por arquitectura:**
- Datos no salen del dispositivo (modo offline)
- Sin telemetría a terceros
- Usuario controla 100% sus datos
- Derecho al olvido: `rm -rf zoe_data/`
- Portabilidad: ZOE Seed Mode (SSD portátil)
- Consentimiento explícito para cloud APIs

### 17.3 HIPAA compatibility

Para datos médicos:
- Modo 100% offline
- Sin cloud APIs
- Cápsulas específicas (`pharmacy_interactions`, `elder_care_knowledge`)
- Audit log completo (Trajectory Chain)
- No diagnosis, no medication modification (restrictions en cápsulas)

### 17.4 EU AI Act 2024

ZOE cumple requisitos para "Trustworthy AI":
- **Transparencia**: Trajectory Chain auditable
- **Human oversight**: humano en el loop en decisiones críticas
- **Technical robustness**: 952 tests, validación epistémica, cuarentena
- **Privacy**: GDPR compliant por diseño
- **Accountability**: identidad criptográfica, firma de mutaciones
- **Societal well-being**: veto por valores en federación
- **Diversity/non-discrimination**: cápsulas con restrictions explícitas

### 17.5 Hardening checklist producción

- [ ] API key de cloud APIs en env vars, no en código
- [ ] `chmod 600 zoe_data/*.json` (permisos restrictivos)
- [ ] Firewall: solo puertos necesarios (8642 dashboard, 8643 federación)
- [ ] TLS termination con nginx/Caddy
- [ ] Rate limiting en `/chat` (evitar abuso)
- [ ] Authentication para dashboard (Basic Auth o OAuth)
- [ ] Backup automático diario
- [ ] Monitoring con alertas (fatiga alta, fallos LLM, etc.)
- [ ] Log rotation
- [ ] Regular `git pull` + `pip install -e .` para updates

---

## 18. Cómo extender ZOE

### 18.1 Añadir un nuevo LLM backend

```python
# zoe/peripherals/llm.py

class MyNewLLMPeripheral(LLMPeripheral):
    @property
    def name(self) -> str:
        return "my_new_llm"
    
    async def generate(self, prompt: str, system: str = None,
                       max_tokens: int = 300, temperature: float = 0.7) -> str:
        # Implementar llamada a tu LLM
        ...
    
    async def generate_streaming(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        # Implementar streaming
        ...
    
    async def health_check(self) -> bool:
        # Implementar health check
        ...
```

### 18.2 Añadir un nuevo sense

```python
# zoe/peripherals/senses.py

class MyNewSense(Sense):
    async def observe(self) -> Observation:
        return Observation(
            timestamp=time.time(),
            source="my_new_sense",
            content="...",
            metadata={...}
        )
```

### 18.3 Crear una cápsula custom

```bash
# 1. Scaffold
zoe-capsules create my_domain --domain health.nutrition --trust curated

# 2. Rellenar capsule.yaml
vim zoe/capsules/my_domain/capsule.yaml

# 3. Añadir conocimiento
vim zoe/capsules/my_domain/semantic_memory.jsonl
vim zoe/capsules/my_domain/procedural_skills.jsonl
vim zoe/capsules/my_domain/ethical_guidelines.jsonl
vim zoe/capsules/my_domain/validators.py

# 4. Validar
zoe-capsules validate my_domain

# 5. Cargar en runtime
zoe-capsules load my_domain
```

### 18.4 Añadir un caso de uso

```yaml
# zoe/use_cases/my_use_case.yaml
use_case:
  name: "my_use_case"
  description: "ZOE para mi escenario específico"
  
  organism:
    organism_id: "zoe_my_use_case"
    tick_interval: 5.0
  
  llm:
    backend: "ollama"
    model: "qwen2.5:7b"
  
  metabolism:
    drowsy_threshold: 0.6
    sleep_threshold: 0.8
  
  senses:
    clock: true
    user_input: true
    filesystem: true
    network: false
    agent: false
  
  capsules:
    required:
      - base_ethics
    optional:
      - basic_psychology
```

```bash
zoe-use-case --use-case my_use_case --backend ollama
```

### 18.5 Añadir un endpoint REST

```python
# zoe/web_dashboard.py

async def _handle_my_endpoint(self, request) -> Any:
    """GET /api/my_endpoint — mi nuevo endpoint."""
    from aiohttp import web
    data = {"hello": "world"}
    return web.json_response(data)

# En start():
app.router.add_get("/api/my_endpoint", self._handle_my_endpoint)
```

### 18.6 Extender el bucle cognitivo (V6)

Si necesitas extender el bucle:

```python
# zoe/core/cognitive_loop_v6.py

from .cognitive_loop_v5 import CognitiveLoopV5

class CognitiveLoopV6(CognitiveLoopV5):
    """V6: añade nueva capacidad sobre V5."""
    
    def __init__(self, *args, new_capability=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_capability = new_capability
    
    async def _tick(self) -> None:
        # Ejecutar V5
        await super()._tick()
        # Añadir lógica V6
        ...
```

**Regla: sin deconstruir.** V6 hereda de V5, no lo reemplaza.

---

## 19. Testing y CI/CD

### 19.1 Tests structure

```
zoe/tests/
├── conftest.py
├── test_phase0.py              # state, loop, laws, physics, fields, tensions
├── test_phase1.py              # vault, trajectory, ontogenetic, metabolism
├── test_phase2_3.py            # sub-agentes, workspace, meta-cog, V3
├── test_phase4.py              # federación, config, V4, casos de uso
├── test_phase5_acd.py          # ACD + Streaming + Cache + V5
├── test_phase6a_epistemic.py   # Validator + Quarantine + CrossValidator
├── test_phase6a_v12.py         # 12 cápsulas
├── test_phase6a_curator_integration.py
├── test_phase6b_marketplace.py # Capsules + Marketplace
├── test_phase6_capsules.py
├── test_phase7a_resource_discovery.py    # 7A
├── test_phase7b_model_bus.py             # 7B
├── test_phase7c_resource_planner.py      # 7C
├── test_phase7d_embodiment_composer.py   # 7D
├── test_phase7e_seed_mode.py             # 7E
├── test_phase7g_hardware_optimization.py # 7G
├── test_phase7g_hardware_endpoints.py    # 7G endpoints
└── ... (40 archivos, 952 tests)
```

### 19.2 Ejecutar tests

```bash
# Todos
pytest zoe/tests/ -q

# Una fase
pytest zoe/tests/test_phase7e_seed_mode.py -v

# Con coverage
pytest zoe/tests/ --cov=zoe --cov-report=term-missing

# Solo tests que matchean patrón
pytest zoe/tests/ -k "test_seed" -v

# Paralelo (requiere pytest-xdist)
pytest zoe/tests/ -n auto
```

### 19.3 Convenciones de tests

- Un test file por fase: `test_phaseN_xxx.py`
- Tests agrupados por clase: `class TestPhaseNFeature`
- Usar `pytest.fixture` para setup compartido
- Tests async con `@pytest.mark.asyncio` o fixture `asyncio`
- Mocks para LLMs (no llamar APIs reales en CI)
- Tests determinísticos (no flaky)

### 19.4 CI/CD (recomendado)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -e .
    - run: pip install pytest pytest-asyncio pytest-cov
    - run: pytest zoe/tests/ --cov=zoe --cov-report=xml
    - uses: codecov/codecov-action@v3
```

### 19.5 Release process

1. Bump version en `zoe/__init__.py`
2. Actualizar `README.md` badges
3. Update `CHANGELOG.md`
4. Tag: `git tag v1.7.0`
5. Push tag: `git push origin v1.7.0`
6. GitHub Release con notas
7. (Opcional) PyPI: `python -m build && twine upload dist/*`

---

## 20. Troubleshooting y debug

### 20.1 Problemas comunes

#### ZOE no inicia

```bash
# Verificar Python
python --version  # debe ser 3.10+

# Verificar instalación
python -c "import zoe; print(zoe.__version__)"

# Verificar tests pasan
pytest zoe/tests/test_state.py -v
```

#### Ollama no responde

```bash
# Verificar Ollama corriendo
curl http://localhost:11434/api/tags

# Si no responde:
ollama serve  # inicia Ollama

# Verificar modelo instalado
ollama list
ollama pull qwen2.5:3b  # si no está
```

#### Dashboard no carga

```bash
# Verificar puerto
lsof -i :8642

# Verificar logs
tail -f zoe_data/dashboard.log

# Probar endpoint
curl http://localhost:8642/stats
```

#### Modelo grande muy lento

1. **Verificar cable USB-C**: usa el cable corto de la caja del SSD, no el del cargador Mac
2. **Verificar SSD**: debe ser 2000 MB/s (Crucial X10 Pro, Kingston XS2000)
3. **Verificar P-cores**: `sysctl -n hw.perflevel0.physicalcpu`
4. **Verificar flash attention**: `OLLAMA_FLASH_ATTENTION=1` en env
5. **Probar cuantización menor**: IQ2_M en vez de Q4_K_M para 30B+

#### Memoria no persiste

```bash
# Verificar DB
ls -la zoe_data/dashboard_memory.db

# Verificar permisos
chmod 644 zoe_data/dashboard_memory.db

# Verificar config
cat zoe/config/production.yaml | grep memory
```

### 20.2 Debug mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs detallados de cada subsistema
logging.getLogger("zoe.core.cognitive_loop_v5").setLevel(logging.DEBUG)
logging.getLogger("zoe.core.epistemic_validator").setLevel(logging.DEBUG)
logging.getLogger("zoe.peripherals.model_bus").setLevel(logging.DEBUG)
```

### 20.3 Inspección de estado

```python
from zoe.cli_chat import ZoeChat

chat = ZoeChat(backend="mock")
await chat.initialize()

# Inspeccionar estado
print(chat.loop.state)              # InternalState
print(chat.metabolism.state)        # MetabolicState
print(chat.living_memory.stats())   # Memoria stats
print(chat.identity_vault)          # Identidad
print(chat.trajectory_chain)        # Trayectoria

# Inspeccionar cápsulas cargadas
print(chat.capsule_manager.list_loaded())

# Inspeccionar federación
print(chat.federation_manager.list_peers())
```

### 20.4 Logs estructurados

```python
import structlog
log = structlog.get_logger()

log.info("zoe.tick", 
         iteration=loop.iteration_count,
         state=loop.metabolism.state.value,
         energy=loop.state.energy,
         fatigue=loop.state.fatigue)
```

---

## 21. Roadmap técnico

### 21.1 Próximas fases (Q3-Q4 2026)

#### App móvil PWA
- Frontend responsive con Tailwind
- Service Worker para offline
- Push notifications
- Mismos endpoints REST

#### Bot Telegram
- `python-telegram-bot`
- Mismo `ZoeChat` backend
- Comandos: `/chat`, `/stats`, `/sleep`, `/wake`, `/llm`

#### Pasarela de pago
- Stripe Checkout para cápsulas paid
- Webhook para activación automática
- Revenue split 70/30 automatizado

#### Cloud gestionado
- ZOE Cloud (AWS/GCP/Azure)
- Multi-tenant con aislamiento
- Auto-scaling
- Backup gestionado

### 21.2 Mejoras técnicas futuras

#### Multi-modal (2027)
- Visión (VLM): análisis de imágenes
- Voz: TTS con voces naturales, STT con Whisper
- Archivos: PDFs, Excel, imágenes

#### Vector DB externa (opcional)
- pgvector para PostgreSQL
- Pinecone para scale
- Weaviate para hybrid search

#### Streaming de sub-agentes
- Mostrar en dashboard qué sub-agente está "ganando"
- Visualización del Global Workspace

#### Ontogenetic Motor V3
- Promoción automática de capacidades
- Degradación de capacidades no usadas
- Evolución arquitectural automática

### 21.3 Performance improvements

- **Speculative decoding**: V6 predecir tokens con modelo pequeño, verificar con grande
- **Self-distillation**: V7 destilar respuestas L3 en cache L2
- **Batch inference**: múltiples peticiones en paralelo
- **GPU pooling**: compartir GPU entre ZOEs federados

### 21.4 Investigación

- **Active Inference avanzado**: Friston Free Energy con planificación profunda
- **Meta-learning**: ZOE aprende a aprender mejor
- **Consciousness metrics**: medir "conciencia" del Global Workspace
- **Embodied cognition**: integración con robots físicos

---

## 22. Glosario técnico

| Término | Definición técnica |
|---|---|
| **ACD** | Adaptive Cognitive Depth. Clasificador que asigna L0/L1/L2/L3 según complejidad. |
| **Active Inference** | Marco de Friston. ZOE minimiza "free energy" = sorpresa predictional. |
| **Baars Global Workspace** | Modelo cognitivo. Múltiples sub-agentes compiten por "broadcast" al workspace. |
| **Capsule** | Paquete versionable de conocimiento experto. 8 tipos de contenido. |
| **Cognitive Cache** | Cache LRU para evitar recalcular respuestas ACD-equivalentes. |
| **CrossValidator** | Verifica claims con 2 fuentes independientes antes de promover. |
| **Cuantización IQ2_M** | Importance Matrix 2-bit medium. ~30% tamaño Q4, 95% calidad. |
| **Cuantización IQ3_XS** | Importance Matrix 3-bit extra small. ~40% tamaño Q4, 97% calidad. |
| **Cuantización Q4_K_M** | 4-bit quantization with K-quant medium. Default balanceado. |
| **Embodiment** | Instancia concreta de ZOE en un host con backend específico. |
| **Epistemic Validator** | Cuantifica confianza vs incertidumbre de claims. |
| **Flash Attention** | Algoritmo de atención optimizado. Reduce cómputo en contextos largos 40%. |
| **Free Energy** | En Active Inference, sorpresa predictional. ZOE la minimiza. |
| **Kahneman System 1/2** | Meta-cognición. System 1 rápido/intuitivo, System 2 lento/analítico. |
| **Knowledge Quarantine** | Estado donde claims nuevos esperan validación cruzada. |
| **LLMPeripheral** | Interfaz común para todos los LLMs (Mock, Ollama, OpenAI, etc.). |
| **mmap** | Memory-mapped file loading. Permite modelos grandes sin cargar todo en RAM. |
| **ModelBus** | Bus que gestiona múltiples LLMs simultáneamente con selección ACD-aware. |
| **P-cores / E-cores** | Performance / Efficiency cores en Apple Silicon. `hw.perflevel0/1`. |
| **ResourceGraph** | Grafo de recursos descubiertos (hardware, Ollama, cloud, peers). |
| **ResourcePlan** | Plan de ejecución: backend + modelo + estrategia + razón. |
| **SeedManifest** | Manifiesto JSON del ZOE Seed. Define ADN de la semilla. |
| **TrajectoryChain** | Blockchain de mutaciones firmadas. Inmutable. |
| **Trust Level** | Nivel de confianza de una cápsula: verified, curated, community, experimental. |
| **Universal Model Bus (UMB)** | Ver ModelBus. Fase 7B. |
| **VLM** | Vision Language Model. Multi-modal. En roadmap 2027. |

---

## Cierre técnico

ZOE es un sistema **modular, extensible y bien testeado** (952 tests). La arquitectura es deliberadamente conservadora: cada fase extiende la anterior sin deconstruir. Esto permite evolución incremental sin rewrites.

**Como CTO, tu rol es:**

1. **Operar ZOE en producción** con la checklist de hardening (sección 17.5)
2. **Extender ZOE** con cápsulas custom para tu vertical (sección 18.3)
3. **Contribuir al código** siguiendo las convenciones (sección 18, 19)
4. **Monitorizar** con Prometheus/Grafana (sección 15.4)
5. **Planificar escalado** con federación B2B (sección 13)

**Principios técnicos no negociables:**

- Sin deconstruir: V(N+1) hereda de V(N)
- Tests primero: toda nueva feature requiere tests
- Backward compatible: nuevos campos con defaults
- Soberanía por defecto: cloud es opt-in
- Observabilidad: todo se loguea, todo se audita

**Para dudas técnicas:**
- README.md del repositorio (2800+ líneas)
- Tests como documentación ejecutable
- Este documento
- Issues en GitHub

---

*Documento técnico ZOE V1.6 — Julio 2026*
*Para dudas técnicas: equipo CTO ZOE*
*Repositorio: github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO*
