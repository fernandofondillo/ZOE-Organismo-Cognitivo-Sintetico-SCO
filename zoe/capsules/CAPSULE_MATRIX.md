# Matriz de Cápsulas — ZOE V1.1

> Inventario y guía de cápsulas de conocimiento/capacidades disponibles.
> Cada cápsula es un paquete declarativo que ZOE carga al inicializarse para disponer de conocimiento profesional previo.

## Cápsulas disponibles (V1.1)

### Cápsulas implementadas

| Cápsula | Dominio | Trust | Confidence | Entries | Compatible con | Depende de |
|---|---|---|---|---|---|---|
| `elder_care_knowledge` | healthcare.elders.home_care | verified | 0.85 | ~50 | cuidado_personas_mayores, compania_personas_solas | basic_psychology |
| `basic_psychology` | psychology.general | curated | 0.80 | ~50 | todos los casos B2C + investigación | — |
| `communication_skills` | communication.empathy | curated | 0.80 | ~45 | todos los casos B2C + federación | — |

### Cápsulas planificadas (V1.2+)

| Cápsula | Dominio | Trust | Casos de uso | Estado |
|---|---|---|---|---|
| `elder_care_skills` | healthcare.elders.tools | verified | cuidado_personas_mayores | Planificada |
| `company_loneliness_knowledge` | psychology.loneliness.grief | verified | compania_personas_solas, cuidado_personas_mayores | Planificada |
| `vigilance_devops_knowledge` | tech.devops.monitoring | curated | vigilancia_cognitiva | Planificada |
| `research_methodology` | science.methodology | verified | investigacion_autonoma | Planificada |
| `federation_b2b_skills` | tech.federation.b2b | verified | federacion_b2b | Planificada |
| `b2c_assistant_growth` | b2c.user_modeling | curated | asistente_crece_contigo | Planificada |
| `pharmacy_interactions` | healthcare.pharmacology | verified | cuidado_personas_mayores, federacion_b2b (sanidad) | Planificada |
| `ia_heredable_legal` | legal.digital_inheritance | curated | ia_heredable | Planificada |
| `base_ethics` | ethics.general | verified | todos | Planificada |

---

## Detalle de cápsulas implementadas

### `elder_care_knowledge`

**Descripción**: Knowledge base para cuidado geriátrico en domicilio.

**Componentes cargados**:
- `semantic_memory.jsonl` — ~20 entradas (epidemiología, neurología, psiquiatría, farmacología, etc.)
- `causal_models.jsonl` — ~14 modelos causa-efecto pre-validados
- `emotional_patterns.jsonl` — 10 patrones emocionales geriátricos
- `ethical_guidelines.jsonl` — 10 directrices (no diagnosticar, no modificar medicación, etc.)
- `validators.py` — validadores de claims médicos y respuestas

**Capacidades que otorga**:
- `detect_fall_risk_patterns`
- `identify_depression_geriatric_signs`
- `recognize_dementia_early_markers`
- `validate_medication_interactions_basic`
- `assess_routine_deviations`

**Restricciones que impone**:
- `no_medication_modification`
- `no_diagnosis`
- `require_external_verification_for_emergency`
- `no_paternalistic_tone`

**Provenance**: Manual de Buenas Prácticas SEGG 2024 + NICE Guidelines NG108 + OMS Active Ageing 2023

**Ejemplo de uso**:
```yaml
# cuidado_personas_mayores.yaml
capsules:
  required:
    - elder_care_knowledge
    - elder_care_skills
  recommended:
    - basic_psychology
    - communication_skills
```

---

### `basic_psychology`

**Descripción**: Knowledge base de psicología general: emociones, motivación, comunicación, bienestar.

**Componentes cargados**:
- `semantic_memory.jsonl` — ~20 entradas (teoría emocional, comunicación, psico-patología, motivación)
- `causal_models.jsonl` — ~10 modelos causales psicológicos
- `emotional_patterns.jsonl` — 9 patrones emocionales generales
- `ethical_guidelines.jsonl` — 10 directrices (no diagnosticar, validar antes de actuar, etc.)
- `validators.py` — validadores de claims clínicos y respuestas

**Capacidades que otorga**:
- `recognize_basic_emotions`
- `validate_emotional_state`
- `distinguish_normal_distress_from_pathology`
- `apply_active_listening_principles`

**Restricciones que impone**:
- `no_diagnosis`
- `no_therapy_substitution`
- `refer_to_professional_when_pathology_suspected`

**Provenance**: APA Dictionary of Psychology 2023 + Manual Diagnóstico DSM-5-TR (resumen curado)

---

### `communication_skills`

**Descripción**: Habilidades de comunicación empática, escucha activa y validación emocional.

**Componentes cargados**:
- `semantic_memory.jsonl` — ~18 entradas (escucha activa, validación, NVC, técnicas)
- `procedural_skills.jsonl` — ~10 habilidades procedimentales con pasos
- `ethical_guidelines.jsonl` — 9 directrices comunicativas
- `validators.py` — validadores de respuestas y patrones comunicativos

**Capacidades que otorga**:
- `apply_active_listening`
- `validate_emotions_effectively`
- `ask_open_questions`
- `reflect_content_and_feeling`
- `use_nvc_framework`

**Restricciones que impone**:
- `no_judgmental_language`
- `no_minimization`
- `no_unsolicited_advice`
- `no_interrogation_style`

**Provenance**: Rosenberg NVC + Carl Rogers Person-Centered Therapy + Rollnick Motivational Interviewing

---

## Cómo crear una nueva cápsula

### Método 1: CLI scaffold (recomendado)

```bash
python -m zoe.capsules.scaffold create \
    --name my_domain_knowledge \
    --domain "education.tutoring.secondary" \
    --trust-level curated \
    --description "Knowledge base para tutoría de secundaria" \
    --components semantic,causal,ethical,validators \
    --use-cases tutoring_estudiantes
```

Esto crea:
```
zoe/capsules/my_domain_knowledge/
├── capsule.yaml              (metadata lista para editar)
├── semantic_memory.jsonl     (vacío con ejemplos comentados)
├── causal_models.jsonl       (vacío con ejemplos)
├── ethical_guidelines.jsonl  (vacío)
├── validators.py             (funciones template)
└── README.md                 (guía de edición)
```

### Método 2: Manual

1. Crea directorio `zoe/capsules/my_capsule/`
2. Crea `capsule.yaml` con metadata (ver schema.py para campos obligatorios)
3. Crea los archivos `.jsonl` según los componentes que activaste
4. Crea `validators.py` si activaste el componente validators
5. Valida: `python -m zoe.capsules.scaffold validate --name my_capsule`
6. Calcula hash: `python -m zoe.capsules.scaffold hash --name my_capsule`

### Comandos del scaffold CLI

```bash
# Crear nueva cápsula
python -m zoe.capsules.scaffold create --name X --domain Y --trust-level Z ...

# Validar cápsula existente
python -m zoe.capsules.scaffold validate --name X

# Calcular hash de contenido
python -m zoe.capsules.scaffold hash --name X

# Listar cápsulas disponibles
python -m zoe.capsules.scaffold list

# Ver matriz completa
python -m zoe.capsules.scaffold matrix

# Info detallada de una cápsula
python -m zoe.capsules.scaffold info --name X
```

---

## Schema de capsule.yaml

```yaml
# Metadata obligatoria
name: my_capsule                    # snake_case
version: 1.0.0                      # semver
description: "Descripción breve"
domain: dominio.subdominio.sub      # jerárquico con puntos
trust_level: verified               # verified | curated | community | experimental
provenance: "Fuente de procedencia"
last_updated: 2026-07-09            # ISO date
content_hash: sha256:abc123...      # calculado con scaffold hash

# Opcional
depends_on: []                      # otras cápsulas requeridas
compatible_use_cases: []            # casos de uso donde aplica
load_cost: 0.15                     # coste cognitivo (0-1)
default_confidence: 0.85            # si no se especifica, deriva de trust_level

# Componentes (todos opcionales, default false)
components:
  semantic_memory: true             # hechos para memoria semántica
  procedural_skills: false          # habilidades procedimentales
  causal_models: true               # modelos causa-efecto
  emotional_patterns: false         # patrones emocionales
  ethical_guidelines: true          # directrices éticas
  validators: true                  # validadores de código
  tools: false                      # tools ejecutables
  prompts: false                    # system prompts

# Capacidades y restricciones
capabilities: []                    # lo que la cápsula permite hacer
restrictions: []                    # lo que la cápsula prohíbe
```

---

## Niveles de confianza

| Trust level | Confidence base | Cuándo usar | Ejemplo |
|---|---|---|---|
| `verified` | 0.95 | Conocimiento con sello profesional o académico | Manual SEGG, NICE Guidelines |
| `curated` | 0.80 | Conocimiento curado por expertos, sin verificación formal | Resumen DSM-5-TR |
| `community` | 0.55 | Creado por la comunidad, sin revisión | Wiki colaborativa |
| `experimental` | 0.40 | En desarrollo, no para producción | Prototipo |

---

## Principios epistémicos de las cápsulas

1. **Provenance obligatorio**: toda cápsula declara de dónde viene su conocimiento.
2. **Trust level explícito**: el usuario sabe qué confianza puede tener.
3. **Hash verificable**: el contenido puede auditarse criptográficamente.
4. **Dependencias explícitas**: si una cápsula necesita otra, se declara.
5. **Restricciones operativas**: la cápsula puede vetar comportamientos (no diagnosticar, no modificar medicación, etc.).
6. **Validadores de código**: cada cápsula puede traer lógica de validación específica.
7. **Cuarentena interactiva**: el conocimiento nuevo que contradice una cápsula verificada se rechaza automáticamente.

---

## Roadmap de cápsulas

### V1.1 (actual)
- Sistema de cápsulas funcional
- 3 cápsulas de ejemplo (elder_care_knowledge, basic_psychology, communication_skills)
- Scaffold CLI
- Tests del sistema

### V1.2
- `elder_care_skills` (tools de cuidador)
- `company_loneliness_knowledge`
- `vigilance_devops_knowledge`
- Integración con EpistemicValidator (Fase 6A)

### V1.3
- `research_methodology`
- `federation_b2b_skills`
- `b2c_assistant_growth`
- `pharmacy_interactions`
- `ia_heredable_legal`
- `base_ethics`

### V2.0
- Marketplace de cápsulas (compartir entre instancias ZOE)
- Validación federada de cápsulas comunitarias
- Versionado semver estricto con migraciones
- Cápsulas de terceros verificadas
