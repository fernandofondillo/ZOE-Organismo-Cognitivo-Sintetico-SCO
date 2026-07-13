# 04 — Memory & Learning

> **Cómo recuerda y aprende ZOE: los 11 tipos de memoria, consolidación, aprendizaje y cápsulas.**
> **Audiencia:** desarrolladores, investigadores.
> **Versión:** V1.8.0 — Julio 2026

---

## Tabla de contenidos

1. [Los 11 tipos de memoria](#1-los-11-tipos-de-memoria)
2. [LivingMemory — la memoria que piensa](#2-livingmemory--la-memoria-que-piensa)
3. [PersistentMemoryStore — SQLite](#3-persistentmemorystore--sqlite)
4. [DeepConsolidation — consolidación profunda](#4-deepconsolidation--consolidación-profunda)
5. [Aprendizaje](#5-aprendizaje)
6. [Memoria y metabolismo](#6-memoria-y-metabolismo)
7. [Configuración de memoria](#7-configuración-de-memoria)

---

## 1. Los 11 tipos de memoria

**Archivo:** `zoe/memory/memory_types.py` (256 LOC)

ZOE tiene 11 tipos de memoria especializados, como la memoria humana:

### 1.1 EPISODIC — eventos específicos

```python
@dataclass
class EpisodicEntry(MemoryEntry):
    """Memoria episódica: evento específico con timestamp."""
    timestamp: float
    location: str = ""
    participants: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0  # -1 a 1
```

**Ejemplo:** "2026-07-10 14:23 — Usuario preguntó sobre cuidado de su madre. Valencia emocional: -0.3 (preocupación)."

### 1.2 SEMANTIC — hechos y conceptos

```python
@dataclass
class SemanticEntry(MemoryEntry):
    """Memoria semántica: hecho o concepto."""
    fact: str
    source: str
    confidence: float
    domain: str
```

**Ejemplo:** "La paracetamol no debe combinarse con alcohol. Fuente: FDA. Confianza: 0.95."

### 1.3 PROCEDURAL — cómo hacer cosas

```python
@dataclass
class ProceduralEntry(MemoryEntry):
    """Memoria procedural: cómo hacer algo (skill)."""
    skill_name: str
    steps: List[str]
    prerequisites: List[str] = field(default_factory=list)
    success_rate: float = 0.0
```

**Ejemplo:** "Protocolo detección depresión geriátrica: 1) Observar cambios, 2) Evaluar GDS-15, 3) Comparar baseline, 4) Si score >5 derivar."

### 1.4 CAUSAL — relaciones causa-efecto

```python
@dataclass
class CausalEntry(MemoryEntry):
    """Memoria causal: relación causa-efecto."""
    cause: str
    effect: str
    confidence: float
    mechanism: str = ""
```

**Ejemplo:** "Causa: interrupción medicación → Efecto: riesgo recaída. Confianza: 0.85."

### 1.5 EMOTIONAL — asociaciones emocionales

```python
@dataclass
class EmotionalEntry(MemoryEntry):
    """Memoria emocional: asociación emocional."""
    trigger: str
    emotional_response: dict  # {valence, arousal, dominance}
    intensity: float
    coping_strategy: str = ""
```

**Ejemplo:** "Trigger: aniversario esposo → Respuesta: {valence: -0.7, arousal: 0.6}. Intensidad: 0.8."

### 1.6 CORPOREAL — estado interno

```python
@dataclass
class CorporealEntry(MemoryEntry):
    """Memoria corporal: estado interno del organismo."""
    internal_state: dict  # {energy, fatigue, arousal, attention}
    context: str
```

**Ejemplo:** "Estado: energy=0.3, fatigue=0.7. Contexto: después de sesión L3 larga."

### 1.7 SOCIAL — relaciones

```python
@dataclass
class SocialEntry(MemoryEntry):
    """Memoria social: relación con otra entidad."""
    entity: str  # persona, otra ZOE, agente
    relationship: str
    history: List[str]
    trust_level: float
```

**Ejemplo:** "Entity: Fernando. Relationship: usuario principal. Trust: 0.92. Historial: 6 meses de interacción."

### 1.8 PROSPECTIVE — planes e intenciones

```python
@dataclass
class ProspectiveEntry(MemoryEntry):
    """Memoria prospectiva: plan o intención futura."""
    intention: str
    when: str  # "mañana", "próxima semana", etc.
    priority: float
    prerequisites: List[str] = field(default_factory=list)
```

**Ejemplo:** "Intención: preguntar por su nieto. Cuándo: próxima sesión. Prioridad: 0.7."

### 1.9 COUNTERFACTUAL — qué hubiera pasado

```python
@dataclass
class CounterfactualEntry(MemoryEntry):
    """Memoria contrafactual: qué hubiera pasado si..."""
    actual_event: str
    hypothetical: str
    estimated_outcome: str
    learning: str
```

**Ejemplo:** "Evento real: sugerí médico. Hipotético: no sugerí. Outcome estimado: retraso diagnóstico. Learning: siempre sugerir consulta ante sospecha."

### 1.10 EVOLUTIONARY — cambios arquitecturales

```python
@dataclass
class EvolutionaryEntry(MemoryEntry):
    """Memoria evolutiva: cambio arquitectural propio."""
    mutation_type: str
    description: str
    before_state: dict
    after_state: dict
    trajectory_hash: str
```

**Ejemplo:** "Mutación: add_skill_subgraph (pintura_como_therapeutic). Antes: 12 sub-agentes. Después: 13 sub-agentes. Hash: a3f7b2c1..."

### 1.11 CULTURAL — normas y contexto

```python
@dataclass
class CulturalEntry(MemoryEntry):
    """Memoria cultural: norma o contexto cultural."""
    culture: str
    norm: str
    context: str
    importance: float
```

**Ejemplo:** "Cultura: España. Norma: mayores prefieren trato de tú. Contexto: generacional. Importancia: 0.7."

---

## 2. LivingMemory — la memoria que piensa

**Archivo:** `zoe/core/living_memory.py` (378 LOC)

`LivingMemory` es la memoria "en caliente" — la que ZOE consulta en cada tick. Y **piensa autónomamente**.

### 2.1 Estructura

```python
class LivingMemory:
    """Memoria viva que piensa autónomamente."""
    
    def __init__(self, max_entries: int = 1000):
        self._entries: Dict[str, MemoryEntry] = {}
        self._max_entries = max_entries
        self._index = {}  # índice por tipo
```

### 2.2 Operaciones básicas

```python
def add(self, entry: MemoryEntry) -> str:
    """Añade entrada. Devuelve ID."""
    entry_id = str(uuid.uuid4())
    self._entries[entry_id] = entry
    self._index[entry.memory_type].append(entry_id)
    return entry_id

def get(self, entry_id: str) -> Optional[MemoryEntry]:
    """Recupera entrada por ID."""

def search(self, query: str, n: int = 5) -> List[MemoryEntry]:
    """Busca entries relevantes por similitud semántica."""
    # Usa Jaccard similarity sobre tokens
    query_tokens = set(query.lower().split())
    scores = []
    for entry_id, entry in self._entries.items():
        entry_tokens = set(entry.content.lower().split())
        similarity = len(query_tokens & entry_tokens) / len(query_tokens | entry_tokens)
        scores.append((similarity, entry))
    scores.sort(reverse=True)
    return [entry for _, entry in scores[:n]]

def count(self) -> int:
    """Total de entries."""
    return len(self._entries)
```

### 2.3 Operaciones autónomas (think)

```python
async def think(self):
    """Operación autónoma de memoria."""
    if self._has_mergeable():
        self._merge_similar()
    if self._has_generalizable():
        self._generalize()
    if self._has_contradictions():
        self._detect_contradictions()
    self._forget_low_salience()
    self._summarize_old()
```

#### _merge_similar()

Fusiona entries con alta similitud (Jaccard > 0.7):

```python
def _merge_similar(self):
    """Fusiona entries duplicadas."""
    # 1. Compara todos los pares
    # 2. Si similitud > 0.7, fusiona en una sola
    # 3. Combina timestamps, sources, confidences
```

#### _generalize()

Generaliza patrones desde entries específicas:

```python
def _generalize(self):
    """Generaliza patrones."""
    # Si observa "usuario pregunta sobre X los lunes" 3 veces,
    # crea entry semántica: "usuario pregunta sobre X los lunes"
```

#### _detect_contradictions()

```python
def _detect_contradictions(self):
    """Detecta entries que se contradicen."""
    # Si entry A dice "X es verdad" y entry B dice "X es falso",
    # marca ambas para revisión
```

#### _forget_low_salience()

```python
def _forget_low_salience(self):
    """Olvida entries con baja importancia."""
    # Si entry tiene salience < 0.2 y antigua > 7 días, eliminar
    # Libera espacio para nuevo aprendizaje
```

#### _summarize_old()

```python
def _summarize_old(self):
    """Resume entries antiguas."""
    # Si 10 entries episódicas sobre mismo tema, crear 1 entry semántica
    # Ej: 10 eventos "usuario preguntó sobre medicación" →
    #     1 semántica "usuario se preocupa por medicación"
```

---

## 3. PersistentMemoryStore — SQLite

**Archivo:** `zoe/memory/persistent_store.py` (377 LOC)

### 3.1 Estructura

```python
class PersistentMemoryStore:
    """Persistencia en SQLite con 11 tablas (una por tipo de memoria)."""
    
    def __init__(self, db_path: str = "zoe_data/memory.db", 
                 auto_save_interval: int = 50):
        self.db_path = db_path
        self._ensure_connection()
        self._create_tables_internal()  # 11 tablas
```

### 3.2 Las 11 tablas

```sql
CREATE TABLE IF NOT EXISTS episodic (
    id TEXT PRIMARY KEY,
    timestamp REAL,
    content TEXT,
    location TEXT,
    participants TEXT,  -- JSON array
    emotional_valence REAL,
    salience REAL,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS semantic (
    id TEXT PRIMARY KEY,
    fact TEXT,
    source TEXT,
    confidence REAL,
    domain TEXT,
    salience REAL,
    created_at REAL
);

-- ... 9 tablas más, una por tipo de memoria
```

### 3.3 Operaciones

```python
def save_entry(self, entry: MemoryEntry) -> bool:
    """Guarda entrada en la tabla correspondiente."""
    table = entry.memory_type.value
    # INSERT OR REPLACE INTO {table} ...

def load_all(self) -> List[MemoryEntry]:
    """Carga todas las entradas de todas las tablas."""

def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
    """Busca por similitud en SQLite (LIKE + scoring)."""

def count_by_type(self) -> Dict[MemoryType, int]:
    """Cuenta entries por tipo."""
    # SELECT memory_type, COUNT(*) FROM ... GROUP BY memory_type
```

### 3.4 PersistentLivingMemory

Wrapper que sincroniza LivingMemory con SQLite:

```python
class PersistentLivingMemory(PersistentMemoryStore):
    """Sincroniza LivingMemory con SQLite."""
    
    def save_to_disk(self) -> int:
        """Guarda toda la LivingMemory a SQLite."""
        # 1. Para cada entry en LivingMemory
        # 2. save_entry() en SQLite
        # Returns: número de entries guardadas
    
    def load_from_disk(self) -> int:
        """Carga SQLite a LivingMemory."""
        # 1. load_all() desde SQLite
        # 2. Para cada entry, LivingMemory.add()
        # Returns: número de entries cargadas
    
    def maybe_auto_save(self):
        """Auto-save cada N iteraciones."""
        if self._iteration_count % self.auto_save_interval == 0:
            self.save_to_disk()
```

---

## 4. DeepConsolidation — consolidación profunda

**Archivo:** `zoe/memory/deep_consolidation.py` (325 LOC)

La consolidación profunda se ejecuta **solo durante SLEEPING**. Son 7 operaciones que reorganizan la memoria a largo plazo.

### 4.1 Las 7 operaciones

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

### 4.2 Operación 1: _episodic_to_semantic()

Convierte memoria episódica repetida en semántica:

```python
def _episodic_to_semantic(self) -> int:
    """Convierte episodios repetidos en hechos semánticos."""
    # 1. Buscar episodios similares (Jaccard > 0.6)
    # 2. Si hay >3 episodios sobre mismo tema
    # 3. Crear entry semántica: "X suele pasar"
    # 4. Eliminar episodios individuales (o marcar como consolidados)
    # Returns: número de episodios consolidados
```

**Ejemplo:** 10 episodios "usuario preguntó sobre paracetamol" → 1 semántica "usuario se preocupa por medicación".

### 4.3 Operación 2: _extract_patterns()

```python
def _extract_patterns(self) -> int:
    """Extrae patrones de secuencias de eventos."""
    # Buscar secuencias repetidas:
    # "los martes pregunta sobre X"
    # "después de hablar de Y, siempre pregunta sobre Z"
    # Crear entries causales o semánticas con los patrones
```

### 4.4 Operación 3: _reinforce_beliefs()

```python
def _reinforce_beliefs(self) -> int:
    """Refuerza creencias confirmadas."""
    # Si una predicción se cumplió, subir confianza
    # Si una creencia fue verificada por 2+ fuentes, subir a 0.85
    # Firmar mutación strengthen_belief en trayectoria
```

### 4.5 Operación 4: _deep_forget()

```python
def _deep_forget(self) -> int:
    """Olvida entries con muy baja salience y antiguas."""
    # Criterios:
    # - salience < 0.2
    # - antigua > 30 días
    # - no referenciada en últimos 100 ticks
    # Eliminar para liberar espacio
```

### 4.6 Operación 5: _generate_hypotheses()

```python
def _generate_hypotheses(self) -> int:
    """Genera hipótesis desde patrones observados."""
    # Si CausalEngine detectó patrón, generar hipótesis formal
    # "Quizás el usuario está deprimido porque..."
    # Poner hipótesis en cuarentena para validación futura
```

### 4.7 Operación 6: _detect_contradictions()

```python
def _detect_contradictions(self) -> int:
    """Detecta entries que se contradicen."""
    # Si entry A y B se contradicen:
    # 1. Marcar ambas para revisión
    # 2. Si una tiene más confianza, debilitar la otra
    # 3. Si contradicción persiste, poner en cuarentena
```

### 4.8 Operación 7: _reorganize_types()

```python
def _reorganize_types(self) -> int:
    """Reorganiza entries entre tipos."""
    # Mover entries mal clasificadas:
    # - Episódica que se repite → Semántica
    # - Semántica con carga emocional → Emocional
    # - Causal confirmada → Procedural (protocolo)
```

---

## 5. Aprendizaje

ZOE aprende de 3 formas:

### 5.1 Learner — extractor de patrones

**Archivo:** `zoe/core/subagents/phase2_subagents.py`

```python
class Learner:
    """Extrae regularidades de las observaciones."""
    
    def propose_learning(self, observations) -> Optional[Mutation]:
        """Propone mutación de aprendizaje."""
        # 1. Buscar regularidades en observaciones
        # 2. Si encuentra patrón, proponer:
        #    - strengthen_belief (reforzar creencia)
        #    - weaken_belief (debilitar creencia)
        # 3. Validar con EpistemicValidator (Fase 6A)
        # 4. Si pasa, firmar en trayectoria
```

### 5.2 CausalEngine — modelador de causa-efecto

```python
class CausalEngine:
    """Construye grafos causales del entorno."""
    
    def add_causal_link(self, cause: str, effect: str, confidence: float):
        """Añade relación causal."""
        # Si observa A seguido de B repetidamente:
        # causal_graph[A][B] = confidence
```

### 5.3 ScientificEngine — método científico

```python
class ScientificEngine:
    """Forma hipótesis, diseña experimentos, actualiza creencias."""
    
    def propose_theory(self, observations) -> Optional[Thought]:
        """Propone teoría desde observaciones."""
    
    def design_experiment(self, hypothesis: str) -> Dict:
        """Diseña experimento para testar hipótesis."""
```

---

## 6. Memoria y metabolismo

La memoria se consolida principalmente durante SLEEPING:

```python
# En CognitiveLoopV4._tick()
if self.metabolism.state == MetabolicState.SLEEPING:
    if self.deep_consolidation:
        self.deep_consolidation.consolidate()
```

### Ciclo diario típico

```
08:00-22:00 (AWAKE): 
  - Recoger observaciones
  - Almacenar memoria episódica
  - Aprender patrones (Learner)
  
22:00-23:00 (DROWSY):
  - Reducir capacidad
  - Memoria se prepara para consolidación
  
23:00-07:00 (SLEEPING):
  - DeepConsolidation ejecuta 7 operaciones
  - Episódica → Semántica
  - Olvidar bajo salience
  - Generar hipótesis
  - Detectar contradicciones
  
07:00-08:00 (WAKING):
  - Restaurar energía
  - Memoria consolidada lista
```

---

## 7. Configuración de memoria

```yaml
# production.yaml
memory:
  db_path: "/opt/zoe/data/memory.db"
  auto_save_interval: 50    # cada 50 iteraciones
  max_entries: 5000         # máximo en LivingMemory
```

### Parámetros

| Parámetro | Default | Descripción |
|---|---|---|
| `db_path` | `zoe_data/memory.db` | Path a SQLite |
| `auto_save_interval` | 50 | Auto-save cada N iteraciones |
| `max_entries` | 5000 | Máximo entries en LivingMemory |

### Memory stats

```bash
# Desde CLI
zoe> /memory
Total: 3,421 entries
By type:
  EPISODIC: 892
  SEMANTIC: 1203
  PROCEDURAL: 234
  CAUSAL: 156
  EMOTIONAL: 287
  CORPOREAL: 89
  SOCIAL: 124
  PROSPECTIVE: 67
  COUNTERFACTUAL: 23
  EVOLUTIONARY: 89
  CULTURAL: 45
```

---

## Cierre

La memoria de ZOE es radicalmente distinta a la de un chatbot:
- **11 tipos especializados** (no solo conversacional)
- **Piensa autónomamente** (reorganiza, fusiona, generaliza)
- **Consolida durante el sueño** (7 operaciones)
- **Persiste entre sesiones** (SQLite)
- **Aprende de patrones** (Learner, CausalEngine, ScientificEngine)

**Documentos relacionados:**
- [03_COGNITIVE_ENGINE.md](03_COGNITIVE_ENGINE.md) — cómo piensa ZOE
- [05_EPISTEMIC_VALIDATION.md](05_EPISTEMIC_VALIDATION.md) — validación de conocimiento
- [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — arquitectura del subsistema memoria

---

*ZOE V1.8.0 — Documento 04: Memory & Learning*
*Julio 2026*
