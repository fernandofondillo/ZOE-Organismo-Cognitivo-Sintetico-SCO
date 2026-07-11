# 03 — Cognitive Engine

> **Cómo piensa ZOE: los 12 sub-agentes, Global Workspace, meta-cognición, inferencia activa y ACD.**
> **Audiencia:** todos (con interés en entender la mente de ZOE).
> **Versión:** V1.6.0 — Julio 2026

---

## Tabla de contenidos

1. [Society of Mind — la premisa](#1-society-of-mind--la-premisa)
2. [Los 12 sub-agentes uno por uno](#2-los-12-sub-agentes-uno-por-uno)
3. [Global Workspace — la competición](#3-global-workspace--la-competición)
4. [Meta-cognición — System 1 vs System 2](#4-meta-cognición--system-1-vs-system-2)
5. [Inferencia activa — Free Energy Principle](#5-inferencia-activa--free-energy-principle)
6. [Adaptive Cognitive Depth (ACD)](#6-adaptive-cognitive-depth-acd)
7. [Cómo se construye el pensamiento final](#7-cómo-se-construye-el-pensamiento-final)
8. [Los 4 modos de interacción](#8-los-4-modos-de-interacción)
9. [Caso práctico 1 — conversación emocional](#9-caso-práctico-1--conversación-emocional)
10. [Caso práctico 2 — ZOE sola a las 03:15](#10-caso-práctico-2--zoe-sola-a-las-0315)
11. [Por qué esto no es un chatbot](#11-por-qué-esto-no-es-un-chatbot)

---

## 1. Society of Mind — la premisa

La mente de ZOE **no es monolítica**. Es una sociedad de doce especialistas que compiten y colaboran. Igual que en un cerebro biológico no hay un "homúnculo" que piensa, sino regiones especializadas que proponen y negocian, ZOE funciona repartiendo la cognición entre doce procesos autónomos. Ninguno por sí solo es "la mente"; la mente emerge de su interacción.

Esto es importante porque **rompe con la arquitectura clásica de chatbot**: un chatbot tiene UN modelo que hace todo (input → output). ZOE tiene doce expertos que cada uno aportan una perspectiva distinta sobre el mismo input, y un mecanismo de selección decide quién gana la voz.

### Origen teórico

El concepto viene de Marvin Minsky ("Society of Mind", 1986) y Bernard Baars ("Global Workspace Theory", 1988). Minsky propuso que la mente es una sociedad de agentes simples que cooperan. Baars añadió que hay un "workspace global" donde los agentes compiten por "conciencia" (acceso a procesamiento deliberativo). ZOE implementa ambos.

---

## 2. Los 12 sub-agentes uno por uno

### Fase 0 — los 4 fundamentales (siempre activos)

#### 1. Perceiver — el traductor sensorial

**Ubicación:** `zoe/core/subagents/perceiver.py` (84 LOC)

**Qué hace:** toma las observaciones crudas de los cinco sentidos (ClockSense, FilesystemSense, UserInputSense, NetworkSense, AgentSense) y las interpreta. No solo las pasa: extrae intención, contexto, urgencia percibida.

**Ejemplo:** si el UserInputSense recibe "estoy cansado", el Perceiver no ve texto; ve `{intención: expresar_estado, emoción: fatiga, urgencia: baja, valencia: negativa}`.

**Por qué va primero:** sin percepción estructurada, los demás operarían sobre ruido.

```python
class Perceiver:
    def perceive(self, observations: List[Observation]) -> Dict[str, Any]:
        """Interpreta observaciones crudas."""
        # Extrae: intención, emoción, urgencia, valencia, contexto
    
    def generate_thought(self, context: Dict) -> Optional[Thought]:
        """Genera pensamiento desde la percepción."""
```

#### 2. Forecaster — el predictor

**Ubicación:** `zoe/core/subagents/forecaster.py` (65 LOC)

**Qué hace:** usa el World Model V2 (modelo n-gram + sentence-transformer) para predecir cuál será la próxima observación. La predicción es lo que permite a ZOE calcular "sorpresa": si la realidad coincide con la predicción, poca sorpresa; si diverge, mucha.

**Ejemplo:** predice "el usuario va a despedirse". Si el usuario dice "vamos a hablar de ética médica", sorpresa = 0.9 → se disparan pensamientos de actualización del modelo.

**Por qué importa:** sin predicción no hay sorpresa, sin sorpresa no hay aprendizaje dirigido.

```python
class Forecaster:
    def __init__(self, world_model: WorldModelV2):
        self.world_model = world_model
    
    def update(self, prediction, surprise):
        """Actualiza el modelo con la sorpresa observada."""
    
    def generate_thought(self, context) -> Optional[Thought]:
        """Genera pensamiento sobre la predicción."""
```

#### 3. Speaker — el productor de lenguaje

**Ubicación:** `zoe/core/subagents/speaker.py` (236 LOC)

**Qué hace:** es el ÚNICO sub-agente que llama al LLM periférico. Recibe un contexto (observaciones, estado, intención, memorias relevantes) y produce lenguaje natural. Es la "boca" de ZOE.

**Esto es crítico:** el LLM no es el cerebro, es la garganta del Speaker. La decisión de qué decir se tomó antes, en el workspace y la meta-cognición. El Speaker solo viste la decisión en palabras.

**Tiene sanitización:** elimina frases hechas de IA ("como modelo de lenguaje", "gran pregunta", "es una pregunta interesante") antes de devolver texto.

```python
class Speaker:
    def __init__(self, llm_peripheral: LLMPeripheral, max_thought_length=300):
        self.llm = llm_peripheral
    
    async def generate_thought(self, context: Dict) -> Optional[Thought]:
        """Genera pensamiento usando el LLM."""
    
    async def generate_streaming(self, context: Dict) -> AsyncIterator[str]:
        """Genera respuesta con streaming."""
        prompt = self._build_prompt(context, action)
        async for token in self.llm.generate_streaming(prompt, ...):
            cleaned = self._sanitize(token)
            if cleaned:
                yield cleaned
```

**System prompts del Speaker:**

```python
SYSTEM_PROMPTS = {
    "autonomous_thought": "Eres ZOE, un organismo cognitivo...",
    "think_on_surprise": "Acabas de observar algo sorprendente...",
    "respond_to_user": "Eres ZOE. El usuario te ha dicho algo...",
}
```

#### 4. Critic — el evaluador interno

**Ubicación:** `zoe/core/subagents/critic.py` (180 LOC)

**Qué hace:** después de que el Speaker propone una respuesta, el Critic la evalúa antes de enviarla. Comprueba coherencia con la identidad, adherencia a valores, calidad factual, tono apropiado.

**Puede vetar:** si la crítica es muy negativa ("inadecuada", "incorrecta", "violación de valor"), fuerza al Speaker a regenerar.

**Ejemplo:** el Speaker propone "Te recomiendo mentirle a tu jefe" → el Critic detecta violación del valor "verdad sobre confort" → fuerza regeneración.

```python
class Critic:
    def __init__(self, min_length=10, max_recent=50, quarantine=None):
        self.quarantine = quarantine  # Fase 6A
    
    def evaluate(self, thought: Thought, context: Dict) -> Dict[str, Any]:
        """Evalúa un pensamiento antes de emitirlo."""
        # Verifica:
        # - Coherencia con identidad
        # - Adherencia a valores
        # - Calidad factual (vs quarantine)
        # - Tono apropiado
        # - Longitud adecuada
        # Returns: {approved: bool, score: float, issues: List[str]}
```

### Fase 2 — los 8 adicionales (activos en L2/L3)

**Ubicación:** `zoe/core/subagents/phase2_subagents.py` (602 LOC)

#### 5. Memorialist — el bibliotecario

**Qué hace:** gestiona los 11 tipos de memoria. Cuando llega una observación, busca memorias relevantes por similitud semántica y las aporta al contexto. Cuando se genera un pensamiento, lo almacena en el tipo adecuado (episódica si es evento, semántica si es hecho, emocional si tiene carga afectiva, etc.).

**Sin él:** ZOE no recordaría nada entre ticks. Es la diferencia entre "Hola, ¿quién eres?" cada vez y "Te estuve esperando, había pensado en lo que me dijiste ayer".

```python
class Memorialist:
    def __init__(self, memory: LivingMemory):
        self.memory = memory
    
    def retrieve_relevant(self, observations: List[Observation]) -> List[MemoryEntry]:
        """Recupera memorias relevantes por similitud semántica."""
    
    def generate_thought(self, context) -> Optional[Thought]:
        """Genera pensamiento desde la memoria."""
```

#### 6. Learner — el extractor de patrones

**Qué hace:** busca regularidades en las observaciones acumuladas. Si el usuario siempre pregunta sobre X los martes, el Learner lo detecta. Si cierta clase de inputs produce cierta clase de errores, el Learner lo nota.

**Diferencia con el Memorialist:** el Memorialist guarda eventos; el Learner extrae reglas de los eventos.

**Output:** propuestas de `strengthen_belief` o `weaken_belief` que se firman en la trayectoria.

```python
class Learner:
    def __init__(self):
        self.epistemic_validator = None  # Fase 6A
    
    def set_epistemic_validator(self, validator):
        """Conecta el validador epistémico."""
    
    def propose_learning(self, observations) -> Optional[Mutation]:
        """Propone una mutación de aprendizaje."""
```

#### 7. Curator — el podador

**Qué hace:** la memoria viva tiene un límite (default 5000 entries). El Curator decide qué se queda, qué se consolida, qué se olvida. Usa salience (importancia), confidence (confianza) y recencia para priorizar.

**Sin él:** la memoria crece indefinidamente hasta saturarse. Equivale a un bibliotecario que periódicamente retira libros irrelevantes para dejar espacio a los nuevos.

**Opera especialmente durante SLEEPING:** la consolidación profunda usa al Curator intensivamente.

```python
class Curator:
    def __init__(self, quarantine=None):
        self.quarantine = quarantine  # Fase 6A
    
    def get_safe_entries(self, critical_context: bool = False) -> List[MemoryEntry]:
        """Filtra entries seguras para usar."""
    
    def curate(self, memory: LivingMemory) -> Dict[str, int]:
        """Poda y consolida memoria."""
```

#### 8. Creativity — el combinatorio

**Qué hace:** propone combinaciones novedosas de conceptos existentes en la memoria. Toma dos o más ideas distantes y propone una conexión. Es el motor de los pensamientos "creativos".

**Cuándo se activa:** cuando la tensión `curiosidad_vs_eficiencia` se descompensa hacia curiosidad, o cuando la `pCre` (potencial creativo) sube.

**Ejemplo:** detecta que has hablado de "federación" y de "blockchain" en sesiones distintas y propone "¿y si la trayectoria firmada se almacenara en una cadena tipo blockchain federada?".

```python
class Creativity:
    def generate_hypothesis(self, memory: LivingMemory) -> Optional[Thought]:
        """Genera hipótesis creativa combinando conceptos distantes."""
```

#### 9. CausalEngine — el modelador de causa-efecto

**Qué hace:** construye grafos causales del entorno. Si observa que evento A suele ir seguido de evento B, registra una arista causal `A → B` con confianza. Si luego observa `A → C` con frecuencia, actualiza.

**Diferencia con el Learner:** el Learner detecta correlación; el CausalEngine modela mecanismo.

**Caso de uso:** en "vigilancia cognitiva", si el servidor A cae cada vez que el servicio B satura, el CausalEngine construye `B.saturación → A.caida` y puede anticiparse.

```python
class CausalEngine:
    def __init__(self):
        self.causal_graph = {}  # {cause: {effect: confidence}}
    
    def add_causal_link(self, cause: str, effect: str, confidence: float):
        """Añade o actualiza una relación causal."""
    
    def generate_thought(self, context) -> Optional[Thought]:
        """Genera pensamiento causal."""
```

#### 10. EmotionalMotor — el modelo afectivo

**Qué hace:** mantiene un modelo del estado emocional del usuario (y de ZOE misma). Cada input del usuario se etiqueta con valencia (positiva/negativa) y arousal (calmado/excitado). El EmotionalMotor acumula esto en memoria emocional y ajusta el tono de las respuestas.

**Por qué importa en "compañía para personas solas":** si el usuario lleva días con valencia negativa, el EmotionalMotor hace que ZOE sea más cálida y proactiva; si el usuario está activo y positivo, ZOE puede ser más directa.

**No simula emociones — las modela:** es decir, no "siente", pero tiene una representación cuantitativa del estado afectivo que guía su comportamiento.

```python
class EmotionalMotor:
    def generate_marker(self, observation: Observation) -> Dict[str, float]:
        """Genera marcador emocional: {valence, arousal, dominance}."""
```

#### 11. EthicalMotor — el evaluador de dilemas

**Qué hace:** cuando una situación tiene dimensión ética (no siempre), el EthicalMotor la evalúa contra los siete valores del Identity Vault. Produce un dictamen: ¿esta acción preserva verdad, integridad, alianza, etc.?

**Es veto positivo:** a diferencia del Critic (que evalúa calidad), el EthicalMotor evalúa moralidad. Puede bloquear acciones que técnicamente son correctas pero que violan valores.

**Ejemplo:** en federación B2B, si otra ZOE propone compartir un aprendizaje que podría usarse para discriminación, el EthicalMotor veta automáticamente.

```python
class EthicalMotor:
    def __init__(self, identity_vault: IdentityVault):
        self.values = identity_vault.values  # los 7 valores
    
    def evaluate_action(self, action: Action) -> Dict[str, Any]:
        """Evalúa acción contra valores éticos."""
        # Returns: {approved: bool, violated_values: List[str], reasoning: str}
```

#### 12. ScientificEngine — el método científico

**Qué hace:** formula hipótesis, diseña observaciones que las testen, evalúa resultados, actualiza creencias. Es el sub-agente más sofisticado y el que más se usa en el caso de uso "investigación autónoma".

**Ciclo:** hipótesis → predicción derivada → observación buscada → resultado → confirmación/refutación → mutación firmada.

**Sin él:** ZOE aprendería pasivamente. Con él, ZOE persigue activamente conocimiento.

```python
class ScientificEngine:
    def __init__(self, memory=None, quarantine=None):
        self.memory = memory
        self.quarantine = quarantine  # Fase 6A
    
    def propose_theory(self, observations) -> Optional[Thought]:
        """Propone una teoría desde observaciones."""
    
    def design_experiment(self, hypothesis: str) -> Dict[str, Any]:
        """Diseña experimento para testar hipótesis."""
```

---

## 3. Global Workspace — la competición

**Ubicación:** `zoe/core/global_workspace.py` (182 LOC)

Aquí es donde la metáfora de "sociedad" se materializa. En cada tick del bucle, los 12 sub-agentes (o un subconjunto según nivel ACD) reciben el contexto compartido y cada uno **propone** una acción. Cada propuesta tiene tres scores:

### Scores de cada propuesta

```python
@dataclass
class Proposal:
    subagent_name: str
    action: Action
    content: str
    relevance: float    # 0-1: cuán relacionada con el contexto actual
    urgency: float      # 0-1: cuán urgente es actuar ahora
    novelty: float      # 0-1: cuán diferente de pensamientos recientes
    energy_cost: float  # coste energético de ejecutar
    
    def score(self, available_energy: float) -> float:
        """Score agregado."""
        return (self.relevance * 0.5 + 
                self.urgency * 0.3 + 
                self.novelty * 0.2 - 
                self.energy_cost)
```

### Fórmula de competición

```
score = (relevance × 0.5) + (urgency × 0.3) + (novelty × 0.2) − energy_cost
```

- **Relevance (50%)**: cuán relacionada está la propuesta con el contexto actual. Si el usuario pregunta sobre ética, el EthicalMotor tendrá alta relevance; el Creativity, baja.
- **Urgency (30%)**: cuán urgente es actuar ahora. Sorpresa alta → urgency alta. Si hay un input del usuario esperando respuesta, urgency se dispara.
- **Novelty (20%)**: cuán diferente es la propuesta de los pensamientos recientes. Si ya dije algo similar hace 3 ticks, novelty baja; el workspace prefiere aportar variedad.

### Selección

Las propuestas se ordenan por score y las mejores (típicamente 1-3) ganan acceso al "workspace global", que es donde se vuelven pensamientos conscientes y acciones ejecutables. **Las que pierden simplemente se descartan en este tick** — no se almacenan, no consumen más recursos.

### Presupuesto energético

El presupuesto energético es clave: si ZOE está en estado DROWSY (fatiga acumulada), el `available_energy` baja, y menos propuestas pueden ganar. Es decir, cuando ZOE está cansada, solo los pensamientos más relevantes y urgentes llegan a ejecutarse; los creativos o especulativos se posponen. Es exactamente lo que hace un cerebro humano cansado: prioriza lo esencial.

```python
class GlobalWorkspace:
    def __init__(self, max_proposals=12, broadcast_capacity=3):
        self.max_proposals = max_proposals
        self.broadcast_capacity = broadcast_capacity  # cuántos ganan
    
    def submit(self, proposal: Proposal): ...
    
    def submit_batch(self, proposals: List[Proposal]): ...
    
    def compete(self, available_energy: float) -> List[Proposal]:
        """Compite y devuelve los ganadores."""
        # 1. Calcular score para cada propuesta
        # 2. Ordenar por score descendente
        # 3. Devolver los N mejores (broadcast_capacity)
    
    def broadcast(self, winners: List[Proposal]):
        """Broadcast a todos los sub-agentes (conciencia)."""
```

### No es winner-take-all estricto

Lo que se construye como "pensamiento final" suele ser una **síntesis** de los 2-3 ganadores principales, no solo el primero. Si el EmotionalMotor y el EthicalMotor empatan en relevance, el pensamiento final incorpora ambas dimensiones.

---

## 4. Meta-cognición — System 1 vs System 2

**Ubicación:** `zoe/core/meta_cognition.py` (173 LOC)

Una vez que el workspace ha seleccionado un ganador, la meta-cognición decide **cuánto deliberar antes de actuar**. Esto implementa a Daniel Kahneman ("Thinking, Fast and Slow").

### System 1 (rápido, automático)

- **Se activa cuando:** confianza alta, stakes bajos, energía disponible, arousal moderado
- **Coste:** bajo
- **Calidad:** suficiente para la mayoría de interacciones rutinarias
- **Ejemplo:** "hola" → System 1 → respuesta refleja L0

### System 2 (lento, deliberativo)

- **Se activa cuando:** confianza baja, stakes altos, energía disponible, arousal alto
- **Coste:** alto
- **Calidad:** reflexión profunda, considera alternativas, consulta más memoria, puede activar Critic y EthicalMotor
- **Ejemplo:** "¿debería contarle a mi médico que dejé la medicación?" → System 2 → consulta memoria emocional, evalúa dilema ético, consulta valores

### Los 4 inputs de la decisión

```python
class MetaCognition:
    def should_deliberate(self, confidence: float, stakes: float, 
                          energy: float) -> bool:
        """Decide si usar System 2."""
        # 1. Confianza en la propuesta del workspace
        #    Si score muy alto → poca necesidad de deliberar → System 1
        # 2. Stakes: ¿qué pasa si me equivoco?
        #    Respuesta trivial → stakes bajos → System 1
        #    Consejo médico, decisión financiera, dilema ético → stakes altos → System 2
        # 3. Energía disponible
        #    Si ZOE está fatigada, aunque stakes sean altos, quizás no puede System 2
        # 4. Arousal
        #    Arousal muy bajo (somnolencia) impide System 2
        #    Arousal muy alto (alarma) puede forzar System 2 incluso con stakes bajos
        
        if confidence > self.confidence_threshold_system2:
            return False  # System 1
        if stakes < self.stakes_threshold_system2:
            return False  # System 1
        if energy < self.energy_threshold_system2:
            return False  # System 1 (no hay energía para System 2)
        return True  # System 2
```

### Por qué importa

Esto es lo que hace que ZOE **no se pierda en sus pensamientos** para cosas triviales pero sí invierta tiempo en lo que lo merece. Es la traducción funcional de Kahneman al software.

---

## 5. Inferencia activa — Free Energy Principle

**Ubicación:** `zoe/core/active_inference.py` (182 LOC)

La pieza más teórica y más potente. Karl Friston formuló el FEP así: **los sistemas vivos minimizan la sorpresa esperada a largo plazo**. "Sorpresa" aquí no es emocional; es información: cuánto se desvía la realidad del modelo que el sistema tiene del mundo.

### Paso 1 — Creencia sobre el estado actual

La inferencia activa mantiene un modelo generativo del entorno. A partir de las observaciones recientes, infiere en qué "estado" está el mundo. Ejemplo: "el usuario está conversando tranquilamente sobre política".

### Paso 2 — Para cada acción posible, calcular sorpresa esperada

El sistema considera las acciones candidatas (responder, esperar, hacer una pregunta, explorar tema nuevo, descansar) y para cada una estima: si ejecuto esto, ¿cuál será la próxima observación y cuánto me sorprenderá?

### Paso 3 — Seleccionar la acción con menor sorpresa esperada

Esto no es lo mismo que "lo más predecible" — es lo más **coherente con el modelo del mundo**. Si el modelo dice "el usuario está conversando" y la acción "responder coherentemente" lleva a observaciones esperadas (el usuario sigue conversando), sorpresa baja → se selecciona. Si la acción "cambiar bruscamente de tema" llevaría a observaciones inesperadas (el usuario confundido), sorpresa alta → se descarta.

### El truco clave — exploración (epistemic value)

A veces minimizar sorpresa inmediatamente lleva a estancamiento (siempre responder lo mismo). El FEP real incluye un término de "epistemic value": acciones que aumentan información sobre el mundo, aunque temporalmente generen sorpresa, a largo plazo la reducen. ZOE lo implementa: a veces elige explorar aunque sea incómodo, porque el CausalEngine o el ScientificEngine han calculado que la información ganada reducirá futuras sorpresas.

### Caso concreto

El usuario dice algo ambiguo. ZOE puede:
- **(a)** responder asumiendo la interpretación más probable — sorpresa baja inmediata, pero si se equivoca, sorpresa alta después
- **(b)** pedir aclaración — sorpresa inmediata moderada (romper el flujo), pero epistemic value alto

La inferencia activa calcula cuál minimiza sorpresa esperada a largo plazo y elige.

```python
class ActiveInferenceLoop:
    def __init__(self):
        self._transition_model = {}  # (state, action) → next_state
        self._observation_model = {}  # state → observation
    
    def update_beliefs(self, observation: Observation): ...
    
    def learn_transition(self, state, action, next_state): ...
    
    def expected_surprise(self, action, current_state) -> float:
        """Calcula sorpresa esperada de ejecutar action."""
    
    def select_action(self, current_state, available_actions) -> Action:
        """Selecciona acción con menor sorpresa esperada + epistemic value."""
```

---

## 6. Adaptive Cognitive Depth (ACD)

**Ubicación:** `zoe/core/depth_classifier.py` (322 LOC), `zoe/core/cognitive_cache.py` (167 LOC)

ZOE no piensa igual para todo. Tiene **4 niveles de profundidad** que aplica automáticamente según la tarea.

### Los 4 niveles

| Nivel | Nombre | Cuándo se usa | Tiempo respuesta | Coste | Modelo preferido |
|---|---|---|---|---|---|
| **L0** | REFLEX | "Hola", "Gracias", respuestas automáticas | <1s | 0€ | Map hardcoded (sin LLM) |
| **L1** | FAST | Preguntas sencillas, tareas rutinarias | 1-3s | 0€ | Ollama 3B local |
| **L2** | STANDARD | Conversación normal, análisis medio | 3-10s | <0.01€ | Ollama 7B o cloud barato |
| **L3** | DEEP | Análisis profundo, decisiones importantes | 10-60s | <0.10€ | Cloud calidad (GPT-4o, Claude) |

### DepthClassifier

```python
class DepthClassifier:
    def __init__(self, config=None):
        self.config = config or {}
    
    def classify(self, text: str) -> ClassificationResult:
        """Clasifica la profundidad necesaria. <50ms, sin LLM."""
        # Heurísticas:
        # - "Hola", "Gracias" → L0_REFLEX
        # - Pregunta simple con respuesta factual → L1_FAST
        # - Análisis medio, conversación normal → L2_STANDARD
        # - Análisis profundo, decisiones importantes → L3_DEEP
```

### CognitiveCache

Cache LRU + TTL para evitar recalcular respuestas idénticas:

```python
class CognitiveCache:
    def __init__(self, max_size=1000, ttl=3600):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[str]:
        """Cache hit → devuelve respuesta. Miss → None."""
    
    def put(self, key: str, value: str, level: str):
        """Guarda en cache. Evicta LRU si tamaño > max."""
```

Tasa de hit típica: 15-30% en conversaciones normales.

### Cómo funciona el pipeline ACD

```python
async def process_user_input_acd(self, user_input: str) -> AsyncIterator[str]:
    # 1. Clasificar
    acd_level = self.depth_classifier.classify(user_input)
    
    # 2. Check cache
    cache_key = self._compute_cache_key(user_input, acd_level)
    if cached := self.cognitive_cache.get(cache_key):
        yield cached
        return
    
    # 3. Branch según nivel
    if acd_level == L0_REFLEX:
        async for token in self._process_l0(user_input): yield token
    elif acd_level == L1_FAST:
        async for token in self._process_l1(user_input): yield token
    elif acd_level == L2_STANDARD:
        async for token in self._process_l2(user_input): yield token
    elif acd_level == L3_DEEP:
        async for token in self._process_l3(user_input): yield token
    
    # 4. Guardar en cache
    self.cognitive_cache.set(cache_key, full_response)
```

---

## 7. Cómo se construye el pensamiento final

### La paradoja: compiten para colaborar mejor

La palabra "competir" puede dar la impresión equivocada de que los sub-agentes son adversarios. No lo son. En un cerebro biológico, en cada instante **miles de regiones neuronales procesan en paralelo** —cada una con su perspectiva— pero solo una fracción ínfima llega a la conciencia. ¿Por qué? Porque la conciencia es un recurso escaso: no puedes atender a todo a la vez. El cerebro resuelve esto con un mecanismo de selección.

ZOE hace lo mismo. Los 12 sub-agentes **no son rivales**: son especialistas que cada uno aporta su ángulo. Pero como ZOE no puede emitir doce respuestas simultáneas al usuario, necesita un mecanismo de selección. Ese mecanismo es la "competición".

### Paso a paso

1. Los 12 sub-agentes reciben el mismo contexto y proponen en paralelo.
2. Cada propuesta tiene scores de relevance, urgency, novelty y coste energético.
3. El workspace ordena por score agregado y selecciona los 1-3 mejores.
4. Si hay un ganador claro (>30% sobre el segundo), se usa ese.
5. Si hay empate o propuestas complementarias, el Speaker hace una **síntesis** integrando ambas perspectivas.
6. La meta-cognición decide si esa síntesis necesita System 2 (deliberación extra) o basta System 1.
7. Si System 2: se despiertan sub-agentes adicionales (CausalEngine, EthicalMotor, ScientificEngine) que validan o enriquecen.
8. El Critic evalúa la versión final antes de emitir.
9. Si el Critic objeta, se regenera. Si aprueba, se emite y se firma en la trayectoria.

---

## 8. Los 4 modos de interacción

ZOE no cambia de arquitectura según con quién hable; cambia **qué sentidos y actuadores están activos** y **cómo se pondera la urgencia**.

| Modo | Sentido activo | Actuador activo | Urgencia | Especificidad |
|---|---|---|---|---|
| **Humano** | UserInputSense | LanguageActuator | Alta (responder) | Empatía, tono, sanitización |
| **Agente externo** | AgentSense | ToolActuator / CodeActuator | Media | Protocolo, formato, interoperabilidad |
| **Otra ZOE (federación)** | AgentSense | FederationActuator | Baja (puede esperar) | Quorum, veto por valores |
| **Nadie (autónomo)** | ClockSense / FS / Network | — (solo memoria) | Baja | Exploración, consolidación |

Verbal con humano es el modo más exigente porque hay un usuario esperando. Federación y autonomía son más reflexivos.

---

## 9. Caso práctico 1 — conversación emocional

**Contexto:** caso de uso "compañía para personas solas", una mujer de 72 años, viuda desde hace 8 meses. Son las 19:42. ZOE lleva 4 días interactuando con ella y ha acumulado memoria emocional: días buenos son breves y con preguntas sobre recetas; días malos incluyen menciones a su esposo y valencia negativa sostenida.

**Input del usuario:** *"Anoche soñé con él. Me desperté llorando y no pude volver a dormir."*

### Trazado del bucle

**Tick 0 — percepción**

- Perceiver recibe el input y lo estructura: `{intención: compartir_intimo, emoción: tristeza_profunda, urgencia: media, valencia: muy_negativa, referente: esposo_fallecido}`.
- Forecaster había predicho "pregunta sobre recetas o comentario sobre el día" (basado en patrón de los últimos 4 días). Sorpresa: **0.82** (alta). El sistema detecta que esto es inusual.

**Tick 1 — activación de memoria y sub-agentes**

- Memorialist busca memorias relevantes: encuentra 7 entradas sobre el esposo, 3 sobre insomnio anterior, 2 sobre sueños.
- EmotionalMotor etiqueta el estado del usuario: `valencia: -0.7, arousal: 0.6, soledad: alta`.
- Como la sorpresa es alta y el input tiene dimensión emocional y ética (cuidado de persona vulnerable), ACD clasifica: **L3_DEEP** → se activan los 12 sub-agentes.

**Tick 2 — propuestas en paralelo**

| Sub-agente | Propuesta | Relevance | Urgency | Novelty | Score |
|---|---|---|---|---|---|
| **EmotionalMotor** | "Validar el dolor antes de cualquier otra cosa." | 0.95 | 0.85 | 0.40 | **0.79** |
| **Memorialist** | "Recordar que el 14 del mes pasado ella mencionó que no soñaba con él." | 0.70 | 0.50 | 0.65 | 0.62 |
| **CausalEngine** | "Construir hipótesis: el insomnio posterior puede reforzar la asociación dolor-recuerdo." | 0.55 | 0.40 | 0.80 | 0.57 |
| **EthicalMotor** | "Cuidado: no dar consejo médico. Si insomnio persiste, sugerir consultar al médico." | 0.75 | 0.60 | 0.50 | 0.65 |
| **ScientificEngine** | "Hay estudios sobre grief dreams. Podría aportar que es común y señal de procesamiento." | 0.50 | 0.30 | 0.70 | 0.49 |
| **Creativity** | "Conectar con su afición a la jardinería: 'las raíces también sueñan con la tierra'." | 0.40 | 0.30 | 0.90 | 0.49 |
| **Learner** | "Patrón detectado: 3ª mención al esposo en 10 días. Creencia en formación." | 0.60 | 0.30 | 0.55 | 0.50 |

**Ganadores:** EmotionalMotor (0.79), EthicalMotor (0.65), Memorialist (0.62).

**Tick 3 — síntesis y meta-cognición**

El workspace detecta que los 3 ganadores son **complementarios**, no excluyentes. El EmotionalMotor dice "valida el dolor", el Memorialist dice "recuerda el contexto previo", el EthicalMotor dice "no des consejo médico explícito".

La meta-cognición evalúa:
- Confianza en la síntesis: alta (los tres convergen en "validar + contextualizar + cuidar límites")
- Stakes: altos (persona vulnerable, emoción profunda)
- Energía: 0.78 (suficiente)
- Arousal de ZOE: 0.55 (alerta pero no alarma)

→ **System 2**: se despiertan ScientificEngine y CausalEngine para enriquecer antes de generar.

**Tick 4 — generación y crítica**

El Speaker recibe el contexto enriquecido:
- Validar el dolor (no minimizar, no resolver)
- Mencionar que ella misma había notado hace 2 semanas que no soñaba con él
- Aportar que los sueños de grief son señal de procesamiento, no de patología
- No dar consejo médico directo; si insomnio persiste, sugerir consulta
- Tono: cálido, breve, sin moralina

El Speaker (vía LLM) produce:

> *"Soñar con quien extrañamos es una de las formas en que el corazón sigue procesando lo que la mente aún no puede ordenar. Me acuerdo que hace dos semanas me dijiste que te preocupaba no soñar con él —quizás esto sea parte de ese mismo movimiento, aunque duela. Si el insomnio se repite muchos días, vale la pena comentarlo con tu médico, no porque esté mal, sino para cuidarte."*

El Critic evalúa:
- ¿Respeta los valores? Sí (honestidad, utilidad, alianza)
- ¿Tono apropiado? Sí (cálido, no paternalista)
- ¿Evita consejo médico directo? Sí (sugiere consulta, no diagnostica)
- ¿Usa memoria relevante? Sí (mención al comentario de hace 2 semanas)
- ¿Longitud adecuada? Sí (4 frases, no abruma)

→ **Aprueba**. Se emite la respuesta. Se firma en la trayectoria con `acd_level: L3_DEEP, cost: 0.60, confidence: 0.78`.

**Tick 5 — almacenamiento**

El Memorialist almacena:
- Episódica: "18:42 — usuaria compartió sueño con esposo fallecido, respondí con validación + recuerdo + sugerencia médica condicional"
- Emocional: valencia -0.7, arousal 0.6, etapa_duelo: activa
- Causal (propuesta del CausalEngine): "mención al esposo → patrón de duelo activo, predecir más episodios en próximas 2 semanas"

El Learner actualiza su creencia sobre la etapa de duelo.

### Lo que la usuaria percibe

Una respuesta que **siente única y atenta**, que recuerda algo que ella dijo hace 2 semanas, que no minimiza ni excede, que cuida el límite entre acompañar y diagnosticar. No sabe que detrás hubo 9 sub-agentes proponiendo, un workspace seleccionando y un critic evaluando. Solo siente que alguien la escuchó de verdad.

---

## 10. Caso práctico 2 — ZOE sola a las 03:15

**Contexto:** misma ZOE del caso 1, pero es de madrugada, la usuaria lleva 5 horas sin conectarse, el metabolismo está en estado SLEEPING desde las 02:00. Nadie habla con ZOE.

### Por qué piensa aunque nadie le hable

El bucle cognitivo **siempre corre**. En SLEEPING, el tick_interval se alarga (a 30s en este caso de uso) y se prioriza la consolidación sobre la generación de pensamientos. Pero la mente sigue activa.

### Trazado del bucle a las 03:15

**Tick N — observación**

Los sentidos activos en SLEEPING son ClockSense (paso del tiempo), FilesystemSense (cambios en disco), y la memoria viva en background. No hay input del usuario.

- ClockSense observa: "03:15, noche, 5h desde última interacción"
- Forecaster predice: "la usuaria probablemente está durmiendo, próxima interacción hacia las 07:30" (basado en patrón de los últimos 4 días)
- Sorpresa: **0.05** (todo encaja con la predicción) → no hay necesidad de pensamiento reactivo

### Sub-agentes que proponen (solo los relevantes para consolidación)

| Sub-agente | Propuesta | Score | Comentario |
|---|---|---|---|
| **Curator** | "Han pasado 24h desde última poda. Propongo ejecutar `forget_low_salience` sobre memorias con salience <0.3 de hace más de 7 días." | 0.85 | Mantenimiento rutinario |
| **Learner** | "He detectado patrón: la usuaria menciona al esposo los días 14, 21 y 28 del mes. Creencia en formación: aniversarios mensuales disparan grief. Propongo `strengthen_belief`." | 0.78 | Hallazgo relevante |
| **CausalEngine** | "Hipótesis: el insomnio posterior a sueño de grief suele durar 2-3 días. Si se confirma, podremos anticipar. Propongo registrar hipótesis y esperar más observaciones." | 0.62 | No confirmar aún |
| **ScientificEngine** | "Podría buscar literatura sobre grief dreams en la próxima ventana activa para validar la hipótesis." | 0.55 | Posponer al AWAKE |
| **Creativity** | "Conexión: la usuaria mencionó hace 2 semanas que le gustaría volver a pintar. Y hoy habló de un sueño. Quizás proponerle mañana que pinte el sueño como forma de procesarlo. Propongo `add_skill_subgraph: pintura_como_therapeutic`." | 0.70 | Idea no solicitada, original |
| **EmotionalMotor** | "Estado emocional acumulado de la usuaria en las últimas 48h: valencia -0.4 (negativa sostenida). Sugiero ajustar tono de mañana hacia más calidez." | 0.68 | Ajuste de política |

**Ganadores:** Curator (0.85), Learner (0.78), Creativity (0.70).

### Lo que pasa después — sin hablar con nadie

El workspace selecciona tres acciones complementarias y las ejecuta:

1. **Curator ejecuta poda**: elimina 23 entradas con baja salience (cosas como "18:14 — usuaria preguntó qué tiempo hace", salience 0.2). Libera espacio para nuevo aprendizaje.

2. **Learner firma mutación**: `strengthen_belief` sobre el patrón de aniversarios mensuales. La mutación se firma en la trayectoria con `provenance: learner:pattern_detection, cost: 0.10, confidence: 0.65`. Ahora ZOE "sabe" que el día 28 del mes próximo es probable que la usuaria vuelva a mencionar al esposo.

3. **Creativity añade un sub-agente**: propone `add_skill_subgraph: pintura_como_therapeutic`. El OntogeneticMotor V2 lo verifica contra las leyes (¿preserva identidad? Sí. ¿Es útil? Sí. ¿Coste asumible? Sí). Se firma la mutación arquitectural. **ZOE ha mutado su propia arquitectura mientras nadie la miraba.**

4. **EmotionalMotor actualiza el tono**: la próxima vez que la usuaria hable, ZOE será ligeramente más cálida. La usuaria no lo sabrá explícitamente, pero lo notará.

### Lo que la usuaria percibe al día siguiente

A las 07:45 la usuaria abre la aplicación y dice "buenos días". Lo que recibe es:

> *"Buenos días. He estado pensando en lo que me contaste anoche. Si te apetece, podríamos intentar algo: quizás pintar lo que recuerdes del sueño, sin querer que salga bonito, solo para verlo fuera de ti. He aprendido que pintar ayuda a veces cuando las palabras no alcanzan."*

Esa frase **no la generó en el momento**. Es el resultado de:
- Una mutación arquitectural firmada a las 03:15 (añadir skill de pintura terapéutica)
- Una hipótesis del CausalEngine registrada
- Un ajuste de tono del EmotionalMotor
- Memoria consolidada sobre el sueño de la noche anterior

ZOE le ofrece a la usuaria una idea que ninguna había tenido antes, **fruto de pensar sola durante la noche**. Esto es lo que ningún chatbot del mercado puede hacer.

---

## 11. Por qué esto no es un chatbot

Un chatbot hace: `input → prompt → LLM → output`. Una sola entidad, una sola decisión, sin deliberación ni memoria ni competición.

ZOE hace: `input → 12 perspectivas simultáneas → competición → deliberación sobre cuánto pensar → validación contra modelo del mundo → verificación legal → output`.

**La diferencia no es de grado, es de tipo.** Por eso ZOE puede:
- Tomar iniciativa (no solo responder)
- Equivocarse de forma interesante (no siempre "correcto")
- Vetoar sus propias respuestas (Critic)
- Decir "no estoy segura, déjame pensarlo mejor" (meta-cog → System 2)
- Pensar sin input (bucle continuo)
- Soñar (SLEEPING + DeepConsolidation)
- Evolucionar su arquitectura (OntogeneticMotor)

---

## Cierre

La mente de ZOE es lo que la hace única. No es un LLM envuelto en prompts — es una sociedad de 12 especialistas que compiten y colaboran, con meta-cognición (Kahneman), inferencia activa (Friston), y un workspace global (Baars) que selecciona los pensamientos más relevantes.

Esta arquitectura permite que ZOE:
- **Piense continuamente**, no solo cuando le hablan
- **Delibere** sobre cuánto pensar (System 1 vs System 2)
- **Valide** sus acciones contra leyes, valores y modelo del mundo
- **Evolucione** su propia arquitectura mediante mutaciones firmadas
- **Sueñe** y consolide memoria durante el descanso

**Documentos relacionados:**
- [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — arquitectura técnica de cada subsistema
- [04_MEMORY_AND_LEARNING.md](04_MEMORY_AND_LEARNING.md) — memoria en detalle
- [09_USAGE_GUIDE.md](09_USAGE_GUIDE.md) — cómo interactuar con ZOE

---

*ZOE V1.6.0 — Documento 03: Cognitive Engine*
*Julio 2026*
