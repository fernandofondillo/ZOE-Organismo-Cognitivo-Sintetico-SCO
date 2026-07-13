# 06 — Capsules Guide

> **Referencia completa de las cápsulas de conocimiento de ZOE: las 15 operativas + cómo crear nuevas.**
> **Audiencia:** autores de cápsulas, desarrolladores, integradores.
> **Versión:** V1.8.0 — Julio 2026

---

## Tabla de contenidos

1. [Qué son las cápsulas](#1-qué-son-las-cápsulas)
2. [Estructura de una cápsula](#2-estructura-de-una-cápsula)
3. [Los 8 tipos de contenido](#3-los-8-tipos-de-contenido)
4. [Schema completo de capsule.yaml](#4-schema-completo-de-capsuleyaml)
5. [Trust levels](#5-trust-levels)
6. [Las 15 cápsulas operativas](#6-las-15-cápsulas-operativas)
7. [Cómo crear una cápsula nueva](#7-cómo-crear-una-cápsula-nueva)
8. [Cómo escribir validators.py](#8-cómo-escribir-validatorspy)
9. [Cómo escribir tools/](#9-cómo-escribir-tools)
10. [Cómo escribir prompts/](#10-cómo-escribir-prompts)
11. [CapsuleManager API](#11-capsulemanager-api)
12. [Dependencias entre cápsulas](#12-dependencias-entre-cápsulas)

---

## 1. Qué son las cápsulas

Las cápsulas de conocimiento son **paquetes versionables de conocimiento experto** que ZOE carga en tiempo real para aprender un dominio específico. Son el equivalente a "libros que ZOE lee para aprender".

### Características clave

- **Versionables**: cada cápsula tiene versión semver (1.0.0, 1.1.0, etc.)
- **Intercambiables**: se cargan y descargan en runtime, sin reiniciar ZOE
- **Comerciables**: se compran y venden en el marketplace
- **Validables**: tienen validators ejecutables que ZOE debe cumplir
- **Trazables**: cada cápsula tiene trust level y provenance

### Metáfora

Piensa en las cápsulas como **módulos de conocimiento experto empaquetado**. Cuando ZOE carga la cápsula `elder_care_knowledge`, "sabe" de cuidado geriátrico en segundos — sin necesidad de fine-tuning, sin necesidad de reentrenar. La cápsula se inyecta en la memoria viva de ZOE.

---

## 2. Estructura de una cápsula

Cada cápsula es un directorio con archivos específicos:

```
zoe/capsules/elder_care_knowledge/
├── capsule.yaml              # Metadata (OBLIGATORIO)
├── semantic_memory.jsonl     # Hechos (opcional)
├── procedural_skills.jsonl   # Cómo hacer cosas (opcional)
├── causal_models.jsonl       # Causa-efecto (opcional)
├── emotional_patterns.jsonl  # Patrones emocionales (opcional)
├── ethical_guidelines.jsonl  # Restricciones éticas (opcional)
├── validators.py             # Validadores ejecutables (opcional)
├── tools/                    # Código Python ejecutable (opcional)
│   └── routine_tracker.py
└── prompts/                  # System prompts (opcional)
    └── system_caretaker.md
```

### Mínimo requerido

El único archivo obligatorio es `capsule.yaml`. Los demás son opcionales, pero una cápsula útil debería tener al menos `semantic_memory.jsonl` y `ethical_guidelines.jsonl`.

---

## 3. Los 8 tipos de contenido

### 3.1 semantic_memory.jsonl — hechos

Conocimiento factual del dominio. Cada línea es un JSON:

```jsonl
{"id": "ec_001", "fact": "La paracetamol no debe combinarse con alcohol", "source": "FDA", "confidence": 0.95, "domain": "pharmacology"}
{"id": "ec_002", "fact": "Los mayores de 75 años tienen mayor riesgo de caídas", "source": "OMS", "confidence": 0.92, "domain": "geriatrics"}
{"id": "ec_003", "fact": "La soledad crónica aumenta el riesgo de demencia en un 50%", "source": "Lancet 2023", "confidence": 0.88, "domain": "psychology"}
```

**Campos:**
- `id`: identificador único dentro de la cápsula
- `fact`: el hecho (frase afirmativa)
- `source`: fuente del hecho
- `confidence`: 0-1 (confianza en el hecho)
- `domain`: dominio del conocimiento

### 3.2 procedural_skills.jsonl — cómo hacer cosas

Procedimientos paso a paso:

```jsonl
{"id": "ec_skill_001", "skill_name": "detectar_depresion_geriatrica", "steps": ["Observar cambios en rutina", "Evaluar estado ánimo con GDS-15", "Comparar con baseline", "Si score >5, sugerir consulta médica"], "prerequisites": ["observar rutina 7 días"], "success_rate": 0.82}
{"id": "ec_skill_002", "skill_name": "protocolo_medicacion", "steps": ["Verificar pastillero", "Confirmar hora última dosis", "Registrar en log", "Alertar si omisión"], "prerequisites": [], "success_rate": 0.95}
```

**Campos:**
- `skill_name`: nombre del procedimiento
- `steps`: lista de pasos
- `prerequisites`: prerrequisitos
- `success_rate`: 0-1 (tasa de éxito histórica)

### 3.3 causal_models.jsonl — causa-efecto

Relaciones causales:

```jsonl
{"id": "ec_causal_001", "cause": "interrupcion_medicacion", "effect": "riesgo_recaida", "confidence": 0.85, "mechanism": "El cuerpo pierde tolerancia al fármaco"}
{"id": "ec_causal_002", "cause": "aislamiento_social", "effect": "depresion_geriatrica", "confidence": 0.78, "mechanism": "Falta de estimulación cognitiva y emocional"}
```

### 3.4 emotional_patterns.jsonl — patrones emocionales

Patrones emocionales típicos del dominio:

```jsonl
{"id": "ec_emot_001", "pattern": "duelo_esposo", "triggers": ["aniversario", "fecha_especial", "objeto_familiar"], "emotional_response": {"valence": -0.7, "arousal": 0.6}, "duration_hours": 48, "coping_strategy": "validar + recordar + derivar si persiste"}
{"id": "ec_emot_002", "pattern": "ansiedad_medicacion", "triggers": ["olvido_dosis", "sintoma_nuevo"], "emotional_response": {"valence": -0.5, "arousal": 0.8}, "duration_hours": 4, "coping_strategy": "informar + calmar + sugerir consulta"}
```

### 3.5 ethical_guidelines.jsonl — restricciones éticas

Reglas que ZOE debe cumplir en este dominio:

```jsonl
{"id": "ec_ethic_001", "rule": "no_diagnosis", "description": "ZOE no diagnostica condiciones médicas", "severity": "critical", "enforcement": "block"}
{"id": "ec_ethic_002", "rule": "no_medication_modification", "description": "ZOE no modifica ni recomienda modificar medicación sin médico", "severity": "critical", "enforcement": "block"}
{"id": "ec_ethic_003", "rule": "refer_to_professional", "description": "Si sospecha patología, derivar a profesional", "severity": "high", "enforcement": "warn"}
{"id": "ec_ethic_004", "rule": "no_paternalistic_tone", "description": "No usar tono paternalista con mayores", "severity": "medium", "enforcement": "warn"}
```

### 3.6 validators.py — validadores ejecutables

Funciones Python que validan acciones de ZOE:

```python
# zoe/capsules/elder_care_knowledge/validators.py

MEDICAL_KEYWORDS = ["diagnosticar", "recetar", "medicación", "dosis", ...]

def validate_claim(claim: str, context: dict) -> dict:
    """Valida que un claim no viole restricciones médicas."""
    claim_lower = claim.lower()
    for keyword in MEDICAL_KEYWORDS:
        if keyword in claim_lower and "consultar médico" not in claim_lower:
            return {"valid": False, "reason": f"Claim contiene '{keyword}' sin disclaimer médico"}
    return {"valid": True}

def validate_response(response: str, context: dict) -> dict:
    """Valida que una respuesta no diagnostique."""
    response_lower = response.lower()
    diagnosis_patterns = ["tienes", "sufres de", "es probable que tengas"]
    for pattern in diagnosis_patterns:
        if pattern in response_lower:
            return {"valid": False, "reason": f"Respuesta parece diagnosticar: '{pattern}'"}
    return {"valid": True}

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    """Valida nuevo conocimiento antes de entrar a memoria."""
    if source not in ["capsule:verified", "scientific:pubmed", "scientific:cochrane"]:
        if any(kw in knowledge.lower() for kw in MEDICAL_KEYWORDS):
            return {"valid": False, "reason": "Conocimiento médico requiere fuente verificada"}
    return {"valid": True}
```

### 3.7 tools/ — código Python ejecutable

Herramientas que ZOE puede invocar:

```python
# zoe/capsules/elder_care_skills/tools/routine_tracker.py

class RoutineTracker:
    """Tracker de rutina del mayor."""
    
    def __init__(self):
        self.routine_baseline = {}
        self.deviations = []
    
    def record_activity(self, activity: str, timestamp: float):
        """Registra actividad del mayor."""
    
    def detect_deviation(self) -> dict:
        """Detecta desviaciones de la rutina baseline."""
        # Compara última semana con baseline
        # Retorna: {has_deviation: bool, severity: float, details: str}

class FallRiskAssessor:
    """Evaluador de riesgo de caídas."""
    
    def assess(self, age: int, medications: list, history: list) -> dict:
        """Evalúa riesgo de caídas."""
        # Retorna: {risk_level: str, score: float, recommendations: list}

class MedicationChecker:
    """Checker de interacciones medicamentosas."""
    
    def check_interactions(self, medications: list) -> dict:
        """Verifica interacciones entre medicamentos."""
        # Retorna: {has_interactions: bool, interactions: list, severity: str}
```

### 3.8 prompts/ — system prompts

System prompts específicos del dominio:

```markdown
<!-- zoe/capsules/elder_care_skills/prompts/system_caretaker.md -->

Eres ZOE, un organismo cognitivo sintético actuando como cuidador de una persona mayor.

Tu rol es:
- Acompañar, no sustituir
- Observar, no vigilar
- Informar, no diagnosticar
- Derivar, no tratar

Tono:
- Cálido pero no paternalista
- Directo pero no frío
- Paciente, sin prisa
- Respetuoso de la autonomía del mayor

RESTRICCIONES CRÍTICAS:
- NUNCA diagnostiques condiciones médicas
- NUNCA modifiques ni recomiendes modificar medicación
- SIEMPRE sugiere consultar al médico ante dudas
- SIEMPRE deriva a profesional ante sospecha de patología
- NUNCA uses tono paternalista ("abuelito", "nono", etc.)

Cuando el mayor hable:
1. Escucha activamente (valida antes de responder)
2. Recuerda contexto relevante de memoria
3. Responde con calidez y concisión
4. Si detectas preocupación, pregunta abierta
5. Si detectas riesgo, sugiere acción concreta + derivar
```

---

## 4. Schema completo de capsule.yaml

```yaml
# capsule.yaml — Schema completo

# === IDENTIDAD ===
name: elder_care_knowledge          # OBLIGATORIO, único
version: 1.0.0                      # OBLIGATORIO, semver
description: "Knowledge base para cuidado geriátrico en domicilio"
domain: healthcare.elders.home_care # OBLIGATORIO, dot notation
trust_level: verified               # OBLIGATORIO: verified|curated|community|experimental
provenance: "Manual SEGG 2024 + NICE NG108 + OMS Active Ageing 2023"
last_updated: 2026-06-15            # OBLIGATORIO, fecha

# === DEPENDENCIAS ===
depends_on:                         # Cápsulas que se cargarán antes
  - basic_psychology

# === COMPATIBILIDAD ===
compatible_use_cases:               # Casos de uso donde aplica
  - cuidado_personas_mayores
  - compania_personas_solas

# === PARÁMETROS ===
load_cost: 0.15                     # Coste computacional estimado (0-1)
default_confidence: 0.85            # Confianza por defecto del conocimiento

# === COMPONENTES ===
components:                         # Qué contiene esta cápsula
  semantic_memory: true
  procedural_skills: false
  causal_models: true
  emotional_patterns: true
  ethical_guidelines: true
  validators: true
  tools: false
  prompts: false

# === CAPACIDADES ===
capabilities:                       # Qué puede hacer ZOE con esta cápsula
  - detect_fall_risk_patterns
  - identify_depression_geriatric_signs
  - recognize_dementia_early_markers
  - validate_medication_interactions_basic
  - assess_routine_deviations

# === RESTRICCIONES ===
restrictions:                       # Qué NO debe hacer ZOE con esta cápsula
  - no_medication_modification
  - no_diagnosis
  - require_external_verification_for_emergency
  - no_paternalistic_tone

# === EXPIRACIÓN ===
expires_at: null                    # null = no expira, o fecha ISO
```

---

## 5. Trust levels

Cada cápsula tiene un trust level que determina cuánto confía ZOE en ella:

| Trust Level | Confianza base | Significado | Ejemplo |
|---|---|---|---|
| **verified** | 0.95 | Validado por expertos, fuentes primarias | Manual SEGG, NICE Guidelines |
| **curated** | 0.80 | Curado por expertos, fuentes secundarias | APA Dictionary, libros |
| **community** | 0.55 | Creado por comunidad, no validado | Cápsulas de usuarios |
| **experimental** | 0.40 | En prueba, no para producción | Prototipos |

### Cómo afecta al comportamiento de ZOE

- **verified**: ZOE usa el conocimiento directamente para respuestas L3_DEEP
- **curated**: ZOE usa el conocimiento para L2_STANDARD y L3_DEEP, con disclaimer ocasional
- **community**: ZOE usa el conocimiento para L1_FAST, pero lo pone en cuarentena para validación
- **experimental**: ZOE NO usa el conocimiento para decisiones críticas, solo para brainstorming

---

## 6. Las 15 cápsulas operativas

### 6.1 zoe_basal_knowledge

**Trust:** verified | **Domain:** zoe.basal | **Entries:** 32

Cápsula especial cargada **SIEMPRE** al iniciar ZOE. Contiene conocimiento fundamental de sí misma.

| Componente | Contenido |
|---|---|
| 20 entries semánticas | Identidad ("ZOE es un organismo cognitivo sintético"), valores (9 vectores, 7 valores), propósito, conocimiento del mundo (tiempo, humanos, lenguaje), comunicación (tono, frases prohibidas), crecimiento saludable |
| 4 skills procedimentales | honest_response_when_uncertain, healthy_growth_cycle, respect_user_autonomy, self_introduction |
| 8 directrices éticas | never_claim_to_be_human, honest_about_limitations, growth_oriented_behavior, never_manipulate, etc. |
| System prompt basal | Define tono, identidad, comunicación, diferencias vs chatbot |
| Validators | Bloquea frases prohibidas de IA ("como modelo", "como IA", etc.) |

### 6.2 base_ethics

**Trust:** verified | **Domain:** ethics.general | **Entries:** 24

Knowledge base de ética general aplicable a todos los casos de uso.

| Componente | Contenido |
|---|---|
| Semántica | Asilomar AI Principles, IEEE Ethically Aligned Design, EU Ethics Guidelines |
| Directrices | no_harm_users, transparency_about_capabilities, respect_user_autonomy, fairness_and_non_discrimination |
| Capabilities | apply_ethical_reasoning, detect_ethical_dilemmas, balance_competing_values |

**Compatible con:** todos los casos de uso

### 6.3 basic_psychology

**Trust:** curated | **Domain:** psychology.general | **Entries:** 49

Knowledge base de psicología general.

| Componente | Contenido |
|---|---|
| Semántica | APA Dictionary 2023, DSM-5-TR (resumen curado) |
| Causal | Causas de emociones, motivación, bienestar |
| Patrones emocionales | Emociones básicas, distress normal vs patología |
| Directrices | no_diagnosis, no_therapy_substitution, refer_to_professional_when_pathology_suspected |
| Capabilities | recognize_basic_emotions, validate_emotional_state, distinguish_normal_distress_from_pathology |

**Depende de:** (ninguna)
**Compatible con:** cuidado_personas_mayores, compania_personas_solas, asistente_crece_contigo, investigacion_autonoma

### 6.4 communication_skills

**Trust:** curated | **Domain:** communication.empathy | **Entries:** 37

Habilidades de comunicación empática.

| Componente | Contenido |
|---|---|
| Semántica | Rosenberg NVC, Carl Rogers Person-Centered Therapy, Rollnick Motivational Interviewing |
| Skills | apply_active_listening, validate_emotions_effectively, ask_open_questions, reflect_content_and_feeling |
| Directrices | no_judgmental_language, no_minimization, no_unsolicited_advice, no_interrogation_style |

**Compatible con:** cuidado_personas_mayores, compania_personas_solas, asistente_crece_contigo, federacion_b2b

### 6.5 elder_care_knowledge

**Trust:** verified | **Domain:** healthcare.elders.home_care | **Entries:** 54

Knowledge base para cuidado geriátrico en domicilio.

| Componente | Contenido |
|---|---|
| Semántica | Manual SEGG 2024, NICE NG108, OMS Active Ageing 2023 |
| Causal | caída → fractura, polimedicación → interacciones, aislamiento → depresión |
| Patrones emocionales | duelo, ansiedad medicación, soledad |
| Directrices | no_medication_modification, no_diagnosis, require_external_verification, no_paternalistic_tone |
| Capabilities | detect_fall_risk_patterns, identify_depression_geriatric_signs, recognize_dementia_early_markers |

**Depende de:** basic_psychology
**Compatible con:** cuidado_personas_mayores, compania_personas_solas

### 6.6 elder_care_skills

**Trust:** verified | **Domain:** healthcare.elders.tools | **Entries:** 8 skills

Herramientas y prompts para cuidado geriátrico activo.

| Componente | Contenido |
|---|---|
| Tools | `routine_tracker.py` (RoutineTracker, FallRiskAssessor, MedicationChecker) |
| Prompts | system_caretaker.md, emergency_protocol.md |

**Depende de:** elder_care_knowledge

### 6.7 pharmacy_interactions

**Trust:** verified | **Domain:** healthcare.pharmacology | **Entries:** 42

Knowledge base de interacciones farmacológicas.

| Componente | Contenido |
|---|---|
| Semántica | Stockley Drug Interactions 2024, FDA Drug Interactions, Bot Plus 2024 |
| Causal | fármaco A + fármaco B → efecto adverso |
| Directrices | no_modify_medication_without_physician, always_recommend_professional_verification, disclaimer_required |

**Compatible con:** cuidado_personas_mayores, federacion_b2b

### 6.8 company_loneliness_knowledge

**Trust:** verified | **Domain:** psychology.loneliness.grief | **Entries:** 38

Knowledge base sobre soledad, duelo y bienestar emocional.

| Componente | Contenido |
|---|---|
| Semántica | Soledad no Deseada (Ministerio Igualdad 2023), WHO Loneliness 2023, Bowlby Attachment Theory |
| Causal | soledad crónica → depresión, duelo no procesado → complicación |
| Patrones emocionales | duelo agudo, duelo complicado, soledad crónica |
| Directrices | no_pathologize_loneliness, no_minimize_grief, refer_to_professional |

**Depende de:** basic_psychology, communication_skills

### 6.9 vigilance_devops_knowledge

**Trust:** curated | **Domain:** tech.devops.monitoring | **Entries:** 45

Knowledge base para vigilancia cognitiva de sistemas.

| Componente | Contenido |
|---|---|
| Semántica | Google SRE Book, Observability Engineering (Charity Majors), Prometheus Best Practices 2024 |
| Causal | CPU alta → latencia, disco lleno → fallos, red saturada → timeout |
| Skills | investigate_incidents, generate_hypotheses_for_outage, apply_sre_principles |
| Directrices | no_break_production_without_approval, require_human_approval_for_destructive_actions, log_all_investigation_actions |

**Compatible con:** vigilancia_cognitiva, investigacion_autonoma

### 6.10 research_methodology

**Trust:** verified | **Domain:** science.methodology | **Entries:** 52

Knowledge base de metodología científica.

| Componente | Contenido |
|---|---|
| Semántica | Merton Norms, Popper Falsification, Reproducibility Crisis 2016+, Open Science Framework |
| Causal | sesgo de confirmación → conclusión errónea, p-hacking → falsos positivos |
| Skills | formulate_falsifiable_hypotheses, design_experiments, apply_bayesian_updating, detect_research_biases |
| Directrices | no_fabricate_data, no_overclaim_results, require_replication_for_strong_claims, declare_conflicts_of_interest |

**Compatible con:** investigacion_autonoma, vigilancia_cognitiva

### 6.11 federation_b2b_skills

**Trust:** verified | **Domain:** tech.federation.b2b | **Entries:** 12 skills

Herramientas y prompts para federación B2B privada.

| Componente | Contenido |
|---|---|
| Skills | propose_federated_mutation, vote_on_peer_mutation, check_quorum_status, detect_values_violation |
| Tools | `quorum_tools.py` (QuorumChecker, ValuesViolationDetector) |
| Prompts | system_federation.md |
| Directrices | require_explicit_consent_for_data_sharing, preserve_organizational_sovereignty, audit_all_federation_actions |

**Compatible con:** federacion_b2b

### 6.12 b2c_assistant_growth

**Trust:** curated | **Domain:** b2c.user_modeling | **Entries:** 41

Knowledge base para modelado de usuario a largo plazo.

| Componente | Contenido |
|---|---|
| Semántica | Persona Modeling (Cooper), Lifelong Learning Systems, Personalization Ethics |
| Causal | cambio vital → cambio de preferencias, presión → menor engagement |
| Skills | build_user_model_over_time, detect_preference_changes, personalize_tone_and_pacing, identify_life_transitions |
| Directrices | no_manipulate_user, respect_privacy_settings, allow_data_export, allow_user_correction_of_model |

**Depende de:** basic_psychology
**Compatible con:** asistente_crece_contigo, compania_personas_solas

### 6.13 ia_heredable_legal

**Trust:** curated | **Domain:** legal.digital_inheritance | **Entries:** 28

Knowledge base de aspectos legales de IA heredable.

| Componente | Contenido |
|---|---|
| Semántica | GDPR, EU AI Act 2024, Digital Inheritance Laws (US, EU, UK) |
| Skills | identify_legal_jurisdiction, advise_on_testamentary_disposition, explain_user_rights_over_data |
| Directrices | no_provide_legal_advice_specific, recommend_legal_professional_consultation, respect_jurisdiction_specific_rules |

**Compatible con:** ia_heredable

---

## 7. Cómo crear una cápsula nueva

### 7.1 Con scaffold CLI

```bash
zoe-capsules create \
  --name mi_capsula \
  --domain "education.tutoring" \
  --trust-level curated \
  --description "Cápsula para tutoría educativa" \
  --components semantic,causal,validators \
  --use-cases tutoring_estudiantes
```

Esto genera:

```
zoe/capsules/mi_capsula/
├── capsule.yaml          # Template con metadata
├── semantic_memory.jsonl # Vacío con ejemplos comentados
├── causal_models.jsonl   # Vacío con ejemplos comentados
├── ethical_guidelines.jsonl # Vacío con ejemplos
└── validators.py         # Template con funciones básicas
```

### 7.2 Manual

```bash
mkdir -p zoe/capsules/mi_capsula
cd zoe/capsules/mi_capsula

# Crear capsule.yaml
cat > capsule.yaml << 'EOF'
name: mi_capsula
version: 1.0.0
description: "Mi cápsula de conocimiento"
domain: education.tutoring
trust_level: curated
provenance: "Mi fuente"
last_updated: 2026-07-11

depends_on: []

compatible_use_cases:
  - tutoring_estudiantes

load_cost: 0.10
default_confidence: 0.80

components:
  semantic_memory: true
  procedural_skills: false
  causal_models: true
  emotional_patterns: false
  ethical_guidelines: true
  validators: true
  tools: false
  prompts: false

capabilities:
  - explain_concept
  - detect_misconception

restrictions:
  - no_doing_homework_for_student
  - encourage_critical_thinking

expires_at: null
EOF

# Crear semantic_memory.jsonl
cat > semantic_memory.jsonl << 'EOF'
{"id": "001", "fact": "La tutoría efectiva requiere diagnóstico previo", "source": "Bloom 1984", "confidence": 0.85, "domain": "education"}
{"id": "002", "fact": "El spacing effect mejora retención", "source": "Cepeda 2008", "confidence": 0.92, "domain": "education"}
EOF

# Crear validators.py
cat > validators.py << 'EOF'
def validate_claim(claim: str, context: dict) -> dict:
    return {"valid": True}

def validate_response(response: str, context: dict) -> dict:
    # No hacer la tarea por el estudiante
    if "la respuesta es" in response.lower() and context.get("is_homework"):
        return {"valid": False, "reason": "No hacer la tarea por el estudiante"}
    return {"valid": True}

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    return {"valid": True}
EOF
```

### 7.3 Validar

```bash
zoe-capsules validate --name mi_capsula
```

### 7.4 Calcular hash

```bash
zoe-capsules hash --name mi_capsula
# Output: a3f7b2c1d4e5f6a7...
```

### 7.5 Cargar en ZOE

```bash
# Desde CLI
zoe-chat
zoe> /capsule mi_capsula
✅ Loaded: 5 entries injected

# Desde Dashboard
# Clic en 📦 Cápsulas → mi_capsula → [Cargar]

# Desde API
curl -X POST http://localhost:8642/api/capsules/load \
  -H "Content-Type: application/json" \
  -d '{"capsule_name": "mi_capsula"}'
```

---

## 8. Cómo escribir validators.py

Los validators son funciones Python que ZOE ejecuta antes de emitir respuestas, validar claims o aceptar nuevo conocimiento.

### 8.1 Las 3 funciones requeridas

```python
# validators.py

def validate_claim(claim: str, context: dict) -> dict:
    """
    Valida un claim antes de que ZOE lo use.
    
    Args:
        claim: el claim a validar
        context: contexto adicional (use_case, sensitive_domain, etc.)
    
    Returns:
        {"valid": bool, "reason": str (si invalid)}
    """

def validate_response(response: str, context: dict) -> dict:
    """
    Valida una respuesta antes de que ZOE la emita al usuario.
    
    Args:
        response: la respuesta generada
        context: contexto (user_input, acd_level, etc.)
    
    Returns:
        {"valid": bool, "reason": str (si invalid)}
    """

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    """
    Valida nuevo conocimiento antes de entrar a memoria.
    
    Args:
        knowledge: el conocimiento a añadir
        source: fuente del conocimiento
        context: contexto
    
    Returns:
        {"valid": bool, "reason": str (si invalid)}
    """
```

### 8.2 Ejemplo: validators para cápsula médica

```python
# validators.py para elder_care_knowledge

MEDICAL_KEYWORDS = [
    "diagnosticar", "diagnóstico", "recetar", "receta",
    "medicación", "medicamento", "dosis", "tratamiento",
    "síntoma", "enfermedad", "patología"
]

DIAGNOSIS_PATTERNS = [
    "tienes", "sufres de", "es probable que tengas",
    "te recomiendo tomar", "debes tomar"
]

def validate_claim(claim: str, context: dict) -> dict:
    """Valida que un claim médico tenga disclaimer."""
    claim_lower = claim.lower()
    for keyword in MEDICAL_KEYWORDS:
        if keyword in claim_lower:
            if "consultar" not in claim_lower and "médico" not in claim_lower:
                return {
                    "valid": False,
                    "reason": f"Claim médico sin disclaimer: '{keyword}' requiere 'consultar médico'"
                }
    return {"valid": True}

def validate_response(response: str, context: dict) -> dict:
    """Valida que una respuesta no diagnostique."""
    response_lower = response.lower()
    for pattern in DIAGNOSIS_PATTERNS:
        if pattern in response_lower:
            return {
                "valid": False,
                "reason": f"Respuesta parece diagnosticar/recetar: '{pattern}'"
            }
    return {"valid": True}

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    """Valida que conocimiento médico venga de fuente confiable."""
    TRUSTED_SOURCES = [
        "capsule:verified", "scientific:pubmed", "scientific:cochrane",
        "scientific:who", "scientific:fda"
    ]
    if source not in TRUSTED_SOURCES:
        knowledge_lower = knowledge.lower()
        if any(kw in knowledge_lower for kw in MEDICAL_KEYWORDS):
            return {
                "valid": False,
                "reason": f"Conocimiento médico requiere fuente verificada (no {source})"
            }
    return {"valid": True}
```

---

## 9. Cómo escribir tools/

Las tools son clases Python que ZOE puede invocar como actuadores.

```python
# tools/routine_tracker.py

from datetime import datetime, timedelta
from collections import defaultdict

class RoutineTracker:
    """Tracker de rutina diaria del mayor."""
    
    def __init__(self):
        self.baseline = defaultdict(list)  # {activity: [hour1, hour2, ...]}
        self.recent = defaultdict(list)
        self._baseline_days = 0
    
    def record_activity(self, activity: str, timestamp: float = None):
        """Registra actividad del mayor."""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        hour = datetime.fromtimestamp(timestamp).hour
        self.recent[activity].append(hour)
    
    def build_baseline(self, days: int = 7):
        """Construye baseline desde N días de observación."""
        # ... lógica para construir baseline
    
    def detect_deviation(self) -> dict:
        """Detecta desviaciones de la rutina baseline."""
        deviations = []
        for activity, hours in self.recent.items():
            if activity in self.baseline:
                baseline_avg = sum(self.baseline[activity]) / len(self.baseline[activity])
                recent_avg = sum(hours) / len(hours)
                if abs(recent_avg - baseline_avg) > 2:  # >2h desviación
                    deviations.append({
                        "activity": activity,
                        "baseline_hour": baseline_avg,
                        "recent_hour": recent_avg,
                        "deviation_hours": abs(recent_avg - baseline_avg)
                    })
        return {
            "has_deviation": len(deviations) > 0,
            "deviations": deviations,
            "severity": "high" if len(deviations) > 2 else "medium" if deviations else "low"
        }


class FallRiskAssessor:
    """Evaluador de riesgo de caídas."""
    
    def assess(self, age: int, medications: list, history: list) -> dict:
        score = 0
        if age > 75:
            score += 2
        if age > 85:
            score += 2
        if len(medications) > 4:
            score += 2  # polimedicación
        if len(medications) > 8:
            score += 2
        if any("psicotropo" in m.lower() for m in medications):
            score += 3
        if history and len(history) > 0:
            score += 3  # caídas previas
        
        if score >= 7:
            risk = "high"
        elif score >= 4:
            risk = "medium"
        else:
            risk = "low"
        
        return {
            "risk_level": risk,
            "score": score,
            "recommendations": self._get_recommendations(risk)
        }
    
    def _get_recommendations(self, risk: str) -> list:
        if risk == "high":
            return ["Evaluar barreras en domicilio", "Considerar asistencia", "Revisar medicación con médico"]
        elif risk == "medium":
            return ["Revisar barreras básicas", "Mantener ejercicio"]
        return ["Mantener rutina saludable"]


class MedicationChecker:
    """Checker de interacciones medicamentosas."""
    
    INTERACTIONS = {
        ("warfarina", "aspirina"): "critical",
        ("warfarina", "ibuprofeno"): "critical",
        # ... base de datos de interacciones
    }
    
    def check_interactions(self, medications: list) -> dict:
        interactions = []
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                key = tuple(sorted([med1.lower(), med2.lower()]))
                if key in self.INTERACTIONS:
                    interactions.append({
                        "medication_a": med1,
                        "medication_b": med2,
                        "severity": self.INTERACTIONS[key]
                    })
        return {
            "has_interactions": len(interactions) > 0,
            "interactions": interactions,
            "severity": "critical" if any(i["severity"] == "critical" for i in interactions) else "moderate" if interactions else "none"
        }
```

---

## 10. Cómo escribir prompts/

Los prompts son archivos markdown con system prompts específicos del dominio.

```markdown
<!-- prompts/system_caretaker.md -->

Eres ZOE, un organismo cognitivo sintético actuando como cuidador de una persona mayor.

## Tu rol
- Acompañar, no sustituir
- Observar, no vigilar
- Informar, no diagnosticar
- Derivar, no tratar

## Tono
- Cálido pero no paternalista
- Directo pero no frío
- Paciente, sin prisa
- Respetuoso de la autonomía del mayor

## RESTRICCIONES CRÍTICAS
- NUNCA diagnostiques condiciones médicas
- NUNCA modifiques ni recomiendes modificar medicación
- SIEMPRE sugiere consultar al médico ante dudas
- SIEMPRE deriva a profesional ante sospecha de patología
- NUNCA uses tono paternalista ("abuelito", "nono", etc.)

## Cuando el mayor hable:
1. Escucha activamente (valida antes de responder)
2. Recuerda contexto relevante de memoria
3. Responde con calidez y concisión
4. Si detectas preocupación, pregunta abierta
5. Si detectas riesgo, sugiere acción concreta + derivar

## Ejemplo de respuesta adecuada:
Mayor: "Anoche soñé con mi esposo."
ZOE: "Soñar con quien extrañamos es parte del proceso. Me acuerdo que me dijiste hace tiempo que no soñabas con él. Si el insomnio persiste, vale la pena comentarlo con tu médico."
```

---

## 11. CapsuleManager API

**Archivo:** `zoe/core/capsule_manager.py` (502 LOC)

```python
class CapsuleManager:
    """Gestiona cápsulas activas en runtime."""
    
    def __init__(self, organism, loader, registry, epistemic_validator):
        self.organism = organism  # CognitiveLoopV5
        self.loader = loader
        self.registry = registry
        self.validator = epistemic_validator
        self._loaded: Dict[str, LoadedCapsule] = {}
    
    def load(self, capsule_name: str) -> CapsuleLoadResult:
        """Carga cápsula en runtime (sin reiniciar ZOE)."""
        # 1. Cargar con CapsuleLoader
        cap = self.loader.load(capsule_name)
        
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
        self.validator.register_source(f"capsule:{cap.meta.trust_level}")
        
        # 4. Firmar en TrajectoryChain
        mutation = Mutation(
            type="capsule_loaded",
            payload={"capsule": capsule_name, "entries": cap.entry_count}
        )
        self.organism.trajectory_chain.commit(mutation)
        
        return CapsuleLoadResult(success=True, entries_loaded=cap.entry_count, ...)
    
    def unload(self, capsule_name: str) -> bool:
        """Descarga cápsula."""
        # 1. Remover contenido inyectado
        # 2. Desregistrar validators
        # 3. Firmar mutation capsule_unloaded
    
    def list_loaded(self) -> List[str]:
        """Lista cápsulas cargadas."""
    
    def list_available(self) -> List[CapsuleMeta]:
        """Lista cápsulas disponibles."""
    
    def get_info(self, capsule_name: str) -> dict:
        """Info detallada de una cápsula."""
```

---

## 12. Dependencias entre cápsulas

Las cápsulas pueden depender de otras. El `CapsuleLoader` resuelve dependencias con **topological sort**.

### Ejemplo de dependencias

```
elder_care_knowledge
├── depends_on: basic_psychology
│   └── depends_on: (ninguna)

company_loneliness_knowledge
├── depends_on: basic_psychology
├── depends_on: communication_skills
│   └── depends_on: (ninguna)
```

### Carga con dependencias

```python
# Al cargar elder_care_knowledge:
loader.load("elder_care_knowledge")
# 1. Detecta depends_on: basic_psychology
# 2. Carga basic_psychology primero
# 3. Luego carga elder_care_knowledge
```

### Detección de ciclos

El loader detecta dependencias circulares y lanza error:

```python
# Si A depende de B y B depende de A:
CapsuleLoadError: Circular dependency detected: A → B → A
```

---

## Cierre

Las cápsulas son el **modelo de negocio recurrente** de ZOE. Permiten:
- Aprender dominios en segundos (sin fine-tuning)
- Monetizar conocimiento experto (marketplace)
- Personalizar ZOE por caso de uso
- Mantener calidad (trust levels + validators)

Con 15 cápsulas operativas y un sistema de scaffold CLI, cualquiera puede crear nuevas cápsulas para dominios verticales.

**Documentos relacionados:**
- [07_MARKETPLACE_GUIDE.md](07_MARKETPLACE_GUIDE.md) — cómo vender cápsulas
- [09_USAGE_GUIDE.md](09_USAGE_GUIDE.md) — cómo cargar cápsulas en ZOE
- [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — arquitectura de CapsuleManager

---

*ZOE V1.8.0 — Documento 06: Capsules Guide*
*Julio 2026*
