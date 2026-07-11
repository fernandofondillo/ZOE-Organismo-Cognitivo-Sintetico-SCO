# FASE 6 — Knowledge Capsules + Epistemic Validation

> **Objetivo**: ZOE deja de nacer como "niño brillante sin cultura". A partir de V1.1, cada instancia carga conocimiento profesional previo (cápsulas) y dispone de mecanismos epistémicos para adquirir conocimiento nuevo de forma fiable.

## Problema detectado (observación del CEO)

ZOE V1.0 tiene arquitectura cognitiva superior pero conocimiento cero al nacer. Esto produce tres problemas:

1. **Lentitud de utilidad**: el caso `cuidado_personas_mayores` tarda semanas en ser útil porque ZOE debe aprender lo que cualquier cuidador humano sabe el primer día.
2. **Sobre-confianza estructural**: la confianza en el proceso cognitivo no garantiza confianza en el contenido. Un proceso perfecto aplicado a contenido equivocado produce conclusiones equivocadas con aura de autoridad.
3. **Sesgo de fuente única**: si ZOE detecta un gap y consulta a un LLM, almacena la respuesta con confianza media. Si la respuesta está sesgada o es incorrecta, ZOE la propaga sin contrastar.

**Analogía**: ZOE es como un niño brillante sin adultos alrededor. Su padre es GPT-4o, que a veces miente con confianza. Su madre es su propio razonamiento, que parte de premisas vacías.

## Hipótesis

El problema no es de arquitectura; es de **epistemología**. ZOE necesita:

1. **Conocimiento de partida verificado** — cápsulas declarativas cargadas junto al YAML.
2. **Validación de adquisición** — todo conocimiento nuevo pasa por un validador antes de almacenarse.
3. **Verificación cruzada triple** — el ScientificEngine coordina múltiples fuentes y solo consolida si hay acuerdo.
4. **Cuarentena activa** — el conocimiento no validado no se usa para decisiones críticas.
5. **Validación federada** — las ZOEs se validan entre sí, como revisión por pares científica.
6. **Cap de confianza para auto-aprendido** — el conocimiento auto-aprendido nunca supera al verificado.

## Diseño — dividido en dos sub-fases

### Fase 6A — Epistemic Validation System

Sistema que regula cómo ZOE adquiere, valida y consolida conocimiento nuevo.

#### Componentes nuevos

| Archivo | Función |
|---|---|
| `zoe/core/epistemic_validator.py` | Validador epistémico con políticas por fuente y dominio |
| `zoe/core/knowledge_quarantine.py` | Gestión de cuarentena activa para conocimiento no validado |
| `zoe/core/cross_validator.py` | Coordinador de verificación triple (multi-LLM + cápsulas + federación) |
| Modificación de `zoe/core/subagents/phase2_subagents.py` | `ScientificEngine` coordina triple verificación |
| Modificación de `zoe/core/subagents/learner.py` (en phase2) | `Learner` pasa todo conocimiento nuevo por `EpistemicValidator` |
| Modificación de `zoe/core/subagents/curator.py` (en phase2) | `Curator` solo usa memorias no en cuarentena para decisiones críticas |
| Modificación de `zoe/core/subagents/critic.py` | `Critic` rechaza respuestas basadas en conocimiento en cuarentena |
| Modificación de `zoe/alma/trajectory_chain.py` | Nuevos tipos de mutación: `knowledge_validated`, `knowledge_rejected`, `knowledge_quarantined`, `knowledge_federatively_confirmed` |
| Modificación de `zoe/core/federation.py` | Nuevo tipo de mensaje: `knowledge_validation_request` |

#### Política de confianza por fuente

```python
SOURCE_TRUST = {
    "capsule:verified": 0.95,         # Cápsula con sello profesional
    "capsule:curated": 0.80,          # Cápsula curada
    "capsule:community": 0.55,        # Cápsula comunitaria
    "llm:gpt-4o": 0.50,               # LLM grande
    "llm:claude-opus": 0.55,          # LLM grande
    "llm:qwen-7b": 0.45,              # LLM medio
    "llm:qwen-3b": 0.40,              # LLM pequeño
    "user:human": 0.70,               # Lo que dice el usuario sobre sí mismo
    "federated:peer_zoe": 0.60,       # Lo que dice otra ZOE
    "federated:peer_zoe_verified": 0.75, # Lo que dice otra ZOE con conocimiento ya validado
    "scientific:pubmed": 0.95,        # Búsqueda científica
    "scientific:arxiv": 0.85,         # Preprints
    "web:wiki": 0.65,                 # Wikipedia
    "web:general": 0.30,              # Web general
    "unknown": 0.20,                  # Sin provenance
}
```

#### Dominios sensibles — requieren doble verificación

```python
SENSITIVE_DOMAINS = {
    "medical": ["medicación", "diagnóstico", "pronóstico", "dosificación",
                "síntoma", "tratamiento", "enfermedad"],
    "psychological": ["trastorno", "terapia", "trauma", "depresión",
                      "ansiedad", "psicología", "psiquiatría"],
    "legal": ["contrato", "obligación", "derecho", "legal", "judicial"],
    "safety": ["emergencia", "riesgo", "peligro", "seguridad"],
    "financial": ["inversión", "préstamo", "impuesto", "dinero"],
}
```

#### Cap de confianza

- Conocimiento de cápsula verificada: hasta `0.95`
- Conocimiento federativamente validado: hasta `0.85`
- Conocimiento triple-verificado (multi-LLM): hasta `0.75`
- Conocimiento de fuente única LLM: máximo `0.50` (cuarentena)
- Conocimiento web general: máximo `0.30` (cuarentena)

El conocimiento en cuarentena **no se usa** para decisiones críticas (debería avisar a la familia, debería sugerir cambio de medicación, etc.).

#### Flujo de adquisición de conocimiento nuevo

```
1. ZOE detecta gap (ScientificEngine o Learner)
2. Formula query a fuente A (ej. GPT-4o)
   → respuesta A con confidence = SOURCE_TRUST["llm:gpt-4o"] = 0.50
   → marca quarantine=True
3. Si dominio sensible → dispara triple verificación obligatoria
4. ScientificEngine formula query a fuente B (ej. Qwen 7B)
   → respuesta B con confidence 0.45, quarantine=True
5. CrossValidator compara A y B:
   - Si coinciden → confidence sube a 0.65, sigue en cuarentena
   - Si divergen → marcar conflicto, pedir fuente C
6. Si hay cápsula relacionada → CrossValidator consulta
   - Si cápsula confirma → confidence sube a 0.75, sale de cuarentena
   - Si cápsula contradice → rechazar, almacenar como "rejected"
7. FederationActuator envía `knowledge_validation_request` a peers
   - Si ≥2 peers ya tienen la entrada con confidence ≥0.7 → confianza sube a 0.80
8. Si después de 30 días no se valida → Curator poda la entrada
9. Mutación firmada en TrajectoryChain con el resultado
```

#### Casos de uso

**Caso A — Gap médico no sensible**: ZOE cuidando a María detecta que no sabe qué es la escala GDS-15.

- Triple verificación: GPT-4o + Qwen 7B + Wikipedia → coinciden → confidence 0.70, sale de cuarentena.
- Mutación: `knowledge_validated` con `provenance: "multi_source:gpt-4o+qwen-7b+wiki"`.

**Caso B — Gap médico sensible**: ZOE detecta que no sabe sobre interacciones de benzodiacepinas en mayores.

- Triple verificación: GPT-4o + Qwen 7B divergen → conflicto.
- CrossValidator consulta `pharmacy_interactions` cápsula → coincide con Qwen.
- 2 de 3 fuentes → confidence 0.75, sale de cuarentena.
- Federación: 12 ZOEs ya tenían la entrada verificada → confianza sube a 0.85.
- Mutación: `knowledge_validated_federatively`.

**Caso C — Rechazo**: ZOE recibe de GPT-4o la afirmación "las benzodiacepinas son seguras en mayores de 80".

- CrossValidator consulta cápsula: contradice entrada verificada con confidence 0.92.
- Rechazo automático.
- Mutación: `knowledge_rejected` con `reason: "contradicts_verified_capsule"`.

---

### Fase 6B — Knowledge Capsules System

Sistema de cápsulas declarativas que se cargan junto al YAML del caso de uso.

#### Arquitectura de cápsulas

```
zoe/capsules/
├── __init__.py
├── loader.py                          # Carga cápsulas al inicializar ZOE
├── schema.py                          # Schema de validación
├── registry.py                        # Registro de cápsulas disponibles
├── scaffold.py                        # Generador de nuevas cápsulas (CLI)
│
├── elder_care_knowledge/              # Cápsula de conocimiento
│   ├── capsule.yaml                   # Metadata + dependencias
│   ├── semantic_memory.jsonl          # Hechos para memoria semántica
│   ├── procedural_skills.jsonl        # Habilidades procedimentales
│   ├── causal_models.jsonl            # Modelos causa-efecto
│   ├── emotional_patterns.jsonl       # Patrones para EmotionalMotor
│   ├── ethical_guidelines.jsonl       # Directrices para EthicalMotor
│   └── validators.py                  # Validadores de código
│
├── elder_care_skills/                 # Cápsula de capacidades
│   ├── capsule.yaml
│   ├── tools/
│   │   ├── routine_tracker.py
│   │   ├── fall_risk_assessor.py
│   │   └── medication_checker.py
│   └── prompts/
│       ├── system_caretaker.md
│       └── emergency_protocol.md
│
├── basic_psychology/                  # Cápsula de psicología general
├── communication_skills/              # Comunicación empática
├── company_loneliness_knowledge/      # Soledad y duelo
├── vigilance_devops_knowledge/        # Monitoring sistemas
├── research_methodology/              # Método científico
├── federation_b2b_skills/             # Federación y quorum
├── b2c_assistant_growth/              # Modelado de usuario
└── pharmacy_interactions/             # Interacciones farmacológicas
```

#### Schema de `capsule.yaml`

```yaml
# Metadata obligatoria
name: elder_care_knowledge
version: 1.0.0
description: "Knowledge base para cuidado geriátrico en domicilio"
domain: healthcare.elders.home_care
trust_level: verified          # verified | curated | community | experimental
provenance: "Manual de Buenas Prácticas SEGG 2024 + NICE Guidelines NG108"
last_updated: 2026-06-15
content_hash: sha256:abc123...

# Dependencias (otras cápsulas requeridas)
depends_on:
  - basic_psychology
  - communication_skills

# Compatibilidad
compatible_use_cases:
  - cuidado_personas_mayores
  - compania_personas_solas

# Peso cognitivo
load_cost: 0.15
default_confidence: 0.85

# Componentes incluidos
components:
  semantic_memory: true
  procedural_skills: true
  causal_models: true
  emotional_patterns: true
  ethical_guidelines: true
  validators: true
  tools: false                  # esta cápsula no trae tools
  prompts: false

# Capacidades que otorga al organismo
capabilities:
  - detect_fall_risk_patterns
  - identify_depression_geriatric_signs
  - recognize_dementia_early_markers
  - validate_medication_interactions_basic

# Restricciones que impone
restrictions:
  - no_medication_modification
  - no_diagnosis
  - require_external_verification_for_emergency
```

#### Tipos de contenido en cápsulas

| Archivo | Tipo de memoria | Sub-agente destino | Formato |
|---|---|---|---|
| `semantic_memory.jsonl` | Semántica | Memorialist | JSON Lines, una entrada por línea |
| `procedural_skills.jsonl` | Procedimental | Memorialist + Learner | JSON Lines |
| `causal_models.jsonl` | Causal | CausalEngine | JSON Lines con causa/efecto/confianza |
| `emotional_patterns.jsonl` | Emocional | EmotionalMotor | JSON Lines con patrón/valencia/arousal |
| `ethical_guidelines.jsonl` | Ética | EthicalMotor | JSON Lines con directriz/razón |
| `validators.py` | — | Speaker + Learner + ScientificEngine | Funciones Python |
| `tools/*.py` | — | ToolActuator | Módulos Python con interfaz estándar |
| `prompts/*.md` | — | Speaker | System prompts específicos |

#### Loader de cápsulas

```python
# zoe/capsules/loader.py

class CapsuleLoader:
    """Carga cápsulas al inicializar ZOE y las inyecta en componentes."""
    
    def load_for_use_case(self, use_case_name: str, config: dict) -> List[Capsule]:
        """Carga todas las cápsulas compatibles con un caso de uso."""
        capsules = []
        capsule_names = config.get("capsules", {})
        
        # required: deben cargarse o fallar
        for name in capsule_names.get("required", []):
            cap = self._load_capsule(name)
            if not cap:
                raise CapsuleLoadError(f"Required capsule not found: {name}")
            capsules.append(cap)
        
        # recommended: cargar si existen
        for name in capsule_names.get("recommended", []):
            cap = self._load_capsule(name)
            if cap:
                capsules.append(cap)
        
        # optional: cargar si existen y no hay conflicto
        for name in capsule_names.get("optional", []):
            cap = self._load_capsule(name)
            if cap and not self._conflicts(cap, capsules):
                capsules.append(cap)
        
        # Resolver dependencias recursivas
        capsules = self._resolve_dependencies(capsules)
        
        # Verificar hashes
        for cap in capsules:
            self._verify_hash(cap)
        
        return capsules
    
    def inject(self, capsules: List[Capsule], organism: 'CognitiveLoopV5'):
        """Inyecta el contenido de las cápsulas en el organismo."""
        for cap in capsules:
            # 1. Inyectar en memoria viva
            for entry in cap.semantic_memory:
                organism.memory.add(
                    content=entry["content"],
                    type="semantic",
                    confidence=entry.get("confidence", cap.default_confidence),
                    salience=entry.get("salience", 0.6),
                    provenance=f"capsule:{cap.name}",
                    metadata={
                        "capsule": cap.name,
                        "capsule_version": cap.version,
                        "trust_level": cap.trust_level,
                        "domain": cap.domain,
                        "category": entry.get("category"),
                        "tags": entry.get("tags", []),
                    }
                )
            
            # 2. Inyectar en CausalEngine
            for model in cap.causal_models:
                organism.causal_engine.add_prevalidated_model(model)
            
            # 3. Inyectar en EmotionalMotor
            for pattern in cap.emotional_patterns:
                organism.emotional_motor.add_pattern(pattern)
            
            # 4. Inyectar en EthicalMotor
            for guideline in cap.ethical_guidelines:
                organism.ethical_motor.add_guideline(guideline)
            
            # 5. Registrar validators
            if cap.validators:
                cap.validators.register(organism.speaker)
                cap.validators.register(organism.learner)
                cap.validators.register(organism.scientific_engine)
            
            # 6. Registrar tools
            for tool in cap.tools:
                organism.actuator_manager.register_tool(tool)
            
            # 7. Inyectar prompts
            for prompt_name, prompt_content in cap.prompts.items():
                organism.speaker.add_specialized_prompt(prompt_name, prompt_content)
            
            # Mutación firmada: capsule_loaded
            organism.ontogenetic_motor.propose_and_apply(
                type="capsule_loaded",
                target="memory",
                payload={
                    "capsule": cap.name,
                    "version": cap.version,
                    "entries_loaded": len(cap.semantic_memory),
                    "trust_level": cap.trust_level,
                },
                justification=f"Capsule {cap.name} v{cap.version} loaded",
                provenance=f"capsule:{cap.name}",
                cost=cap.load_cost,
                confidence=cap.default_confidence,
            )
```

#### Modificación del YAML del caso de uso

```yaml
# cuidado_personas_mayores.yaml (con cápsulas)

use_case:
  name: "cuidado_personas_mayores"
  ...
  
  capsules:
    required:
      - elder_care_knowledge
      - elder_care_skills
    recommended:
      - basic_psychology
      - communication_skills
    optional:
      - pharmacy_interactions
```

#### Script generador de cápsulas — `capsule_scaffold.py`

```bash
# Crear nueva cápsula
python -m zoe.capsules.scaffold create \
    --name my_domain_knowledge \
    --domain "education.tutoring.secondary" \
    --trust-level curated \
    --description "Knowledge base para tutoría de secundaria" \
    --components semantic,causal,ethical,validators \
    --use-cases tutoring_estudiantes

# Resultado: crea zoe/capsules/my_domain_knowledge/ con:
#   capsule.yaml (template)
#   semantic_memory.jsonl (vacío con ejemplos comentados)
#   causal_models.jsonl (vacío con ejemplos)
#   ethical_guidelines.jsonl (vacío)
#   validators.py (con funciones template)
#   README.md (guía de edición)

# Validar cápsula existente
python -m zoe.capsules.scaffold validate \
    --name elder_care_knowledge
# Resultado: OK o lista de errores

# Empaquetar cápsula para distribución
python -m zoe.capsules.scaffold package \
    --name elder_care_knowledge \
    --output ./dist/elder_care_knowledge-1.0.0.zcap
# Resultado: archivo .zcap con hash verificable

# Cargar cápsula desde paquete
python -m zoe.capsules.scaffold install \
    --file ./dist/elder_care_knowledge-1.0.0.zcap
```

El script genera templates con ejemplos comentados, valida el schema, calcula hashes y empaqueta. Permite que cualquier persona (o ZOE) cree cápsulas nuevas sin necesidad de entender toda la arquitectura.

---

## Matriz de cápsulas — inventario inicial V1.1

| Cápsula | Dominio | Tipo | Trust | Casos de uso compatibles | Componentes | Entries aprox. |
|---|---|---|---|---|---|---|
| `elder_care_knowledge` | Geriatría domiciliaria | Knowledge | verified | cuidado_personas_mayores, compania_personas_solas | semantic, causal, emotional, ethical, validators | ~150 |
| `elder_care_skills` | Cuidador práctico | Skills + Tools | verified | cuidado_personas_mayores | tools, prompts | 4 tools, 2 prompts |
| `basic_psychology` | Psicología general | Knowledge | curated | todos los casos B2C | semantic, emotional | ~80 |
| `communication_skills` | Comunicación empática | Knowledge + Procedural | curated | todos los casos B2C | semantic, procedural, validators | ~60 |
| `company_loneliness_knowledge` | Soledad y duelo | Knowledge | verified | compania_personas_solas, cuidado_personas_mayores | semantic, emotional, ethical | ~70 |
| `vigilance_devops_knowledge` | Monitoring sistemas | Knowledge + Skills | curated | vigilancia_cognitiva | semantic, causal, procedural, tools | ~120 |
| `research_methodology` | Método científico | Knowledge + Procedural | verified | investigacion_autonoma | semantic, procedural, causal, validators | ~100 |
| `federation_b2b_skills` | Federación y quorum | Skills + Tools | verified | federacion_b2b | tools, prompts, validators | 3 tools |
| `b2c_assistant_growth` | Modelado de usuario | Knowledge | curated | asistente_crece_contigo | semantic, procedural | ~50 |
| `pharmacy_interactions` | Interacciones farmacológicas | Knowledge + Tools | verified | cuidado_personas_mayores, federacion_b2b (sanidad) | semantic, tools, validators | ~200 + DB |
| `ia_heredable_legal` | Aspectos legales y heredabilidad | Knowledge | curated | ia_heredable | semantic, ethical, validators | ~40 |
| `base_ethics` | Ética general | Knowledge | verified | todos | semantic, ethical | ~50 |

**Total inicial**: 12 cápsulas, ~1000 entries de conocimiento verificado.

---

## Plan de implementación

### Step 1 — Fase 6A: Epistemic Validator (1-2 semanas)

1. `zoe/core/epistemic_validator.py` con políticas por fuente y dominio
2. `zoe/core/knowledge_quarantine.py` con gestión de cuarentena
3. `zoe/core/cross_validator.py` con triple verificación
4. Modificación de `ScientificEngine`, `Learner`, `Critic`, `Curator`
5. Nuevos tipos de mutación en `TrajectoryChain`
6. Tests: `test_phase6a_epistemic.py`

### Step 2 — Fase 6B: Capsule System (2-3 semanas)

1. `zoe/capsules/schema.py` con validación de schema
2. `zoe/capsules/loader.py` con inyección en componentes
3. `zoe/capsules/registry.py` con registro de cápsulas disponibles
4. `zoe/capsules/scaffold.py` con CLI generador
5. 3 cápsulas de ejemplo: `elder_care_knowledge`, `basic_psychology`, `communication_skills`
6. Modificación de `run_use_case.py` para cargar cápsulas
7. Tests: `test_phase6b_capsules.py`

### Step 3 — Integración 6A + 6B (1 semana)

1. Cápsulas se registran como fuente `capsule:*` en `EpistemicValidator`
2. `CrossValidator` consulta cápsulas automáticamente
3. `Learner` marca conocimiento de cápsula como no sobrescribible
4. Tests de integración end-to-end

### Step 4 — Federación epistémica (1 semana)

1. Nuevo tipo de mensaje federado: `knowledge_validation_request`
2. Protocolo: peer ZOE responde con su confianza sobre la entrada
3. Si ≥2 peers confirman → confianza sube a 0.85
4. Tests de federación epistémica

### Step 5 — Documentación y deploy

1. `PHASE_6_PLAN.md` (este documento)
2. `PHASE_6_RESULTS.md` con métricas
3. Actualización de README y guía V1
4. Commit y push

## Métricas de éxito

| Métrica | Antes (V1.0) | Objetivo (V1.1) |
|---|---|---|
| Tiempo a utilidad (cuidado mayores) | 2-4 semanas | <1 hora |
| Knowledge entries al nacer | 11 (Init) | ~1000 (con cápsulas) |
| Confianza máxima auto-aprendido | 0.7 (sin restricción) | 0.50 (cuarentena) → 0.75 (triple validado) |
| Confianza máxima cápsula | N/A | 0.95 |
| Validación cruzada | No | Triple obligatoria en sensible |
| Federación epistémica | No | Sí (revisión por pares) |
| Reject de conocimiento contradictorio | No | Sí automático |
| Tests | 578 | 620+ |

## Riesgos y mitigaciones

1. **Cápsulas desactualizadas**: la medicina cambia. Mitigación: campo `last_updated` + `expires_at` opcional + revisión humana periódica.
2. **Sesgo en cápsulas**: una cápsula verificada puede tener sesgo de fuente. Mitigación: `provenance` explícito + `trust_level: community` para cápsulas alternativas + federación para detectar sesgos sistémicos.
3. **Over-blocking**: el EpistemicValidator podría rechazar conocimiento correcto por exceso de cautela. Mitigación: mecanismo de `appeal` donde el ScientificEngine puede pedir revisión humana vía dashboard.
4. **Coste de triple validación**: 3 llamadas LLM por gap. Mitigación: solo se dispara en dominios sensibles o cuando hay contradicción; en dominios no sensibles basta 1 fuente con confianza 0.5.
5. **Dependencias circulares entre cápsulas**: A depende de B, B depende de A. Mitigación: el loader detecta ciclos y falla al cargar.

## Conclusión

Fase 6 convierte a ZOE de "niño brillante sin cultura" en "organismo cognitivo con cultura verificada y mecanismos epistémicos para crecer de forma fiable". Mantiene la iniciativa y proactividad para aprender, pero con filtros que evitan que sesgos externos se conviertan en creencias firmes. La auditabilidad criptográfica se extiende: cada entrada de memoria semántica tendrá `provenance` completo rastreable hasta su origen (cápsula, multi-LLM, federación, etc.).

La arquitectura de cápsulas además abre un modelo de ecosistema: terceros pueden crear cápsulas para dominios verticales (educación, jurídico, ingeniería) y distribuirlas. ZOE se convierte en plataforma, no solo en producto.
