# 09 — Usage Guide

> **Cómo se usa ZOE en detalle: CLI, Web Dashboard, API REST y casos de uso.**
> **Audiencia:** usuarios finales, desarrolladores, integradores.
> **Versión:** V1.6.0 — Julio 2026

---

## Tabla de contenidos

1. [CLI Chat (zoe-chat)](#1-cli-chat-zoe-chat)
2. [Web Dashboard (zoe-dashboard)](#2-web-dashboard-zoe-dashboard)
3. [Gestión de cápsulas (zoe-capsules)](#3-gestión-de-cápsulas-zoe-capsules)
4. [Casos de uso (zoe-use-case)](#4-casos-de-uso-zoe-use-case)
5. [Cambio de LLM en caliente](#5-cambio-de-llm-en-caliente)
6. [Modo mentor](#6-modo-mentor)
7. [Streaming de respuestas](#7-streaming-de-respuestas)
8. [Alimentar documentos](#8-alimentar-documentos)
9. [Persistencia y recovery](#9-persistencia-y-recovery)
10. [Apagar ZOE correctamente](#10-apagar-zoe-correctamente)

---

## 1. CLI Chat (zoe-chat)

El CLI Chat es la interfaz más directa con ZOE. Funciona en la terminal.

### 1.1 Iniciar

```bash
# Modo Mock (sin LLM, para pruebas)
zoe-chat

# Con Ollama local
zoe-chat --backend ollama --model qwen2.5:3b

# Con OpenAI GPT-4o
zoe-chat --backend openai_compatible --model gpt-4o
# (requiere OPENAI_API_KEY en env)

# Con Anthropic Claude
zoe-chat --backend anthropic --model claude-sonnet-4-20250514
# (requiere ANTHROPIC_API_KEY en env)

# Con DeepSeek
zoe-chat --backend openai_compatible --model deepseek-chat \
  --api-key "tu-key" --base-url https://api.deepseek.com/v1

# Con caso de uso específico
zoe-chat --use-case cuidado_personas_mayores --backend ollama --model qwen2.5:7b

# Con base de datos custom
zoe-chat --db-path /path/a/memoria.db
```

### 1.2 Argumentos CLI

| Argumento | Descripción | Default |
|---|---|---|
| `--backend` | Backend LLM: mock, ollama, openai_compatible, anthropic, zai | mock |
| `--model` | Modelo específico del backend | Depende del backend |
| `--api-key` | API key para cloud backends | De env var |
| `--base-url` | URL base para OpenAI-compatible | https://api.openai.com/v1 |
| `--use-case` | Caso de uso YAML a cargar | None |
| `--db-path` | Path a SQLite de memoria | zoe_data/dashboard_memory.db |

### 1.3 Los 11 comandos especiales

Dentro del CLI, puedes escribir comandos que empiezan con `/`:

#### `/stats` — estadísticas del organismo

```
zoe> /stats
┌─────────────────────────────────────────┐
│ ZOE Stats                               │
├─────────────────────────────────────────┤
│ Organism ID: zoe_fernando_v1            │
│ Identity Hash: a3f7b2c1...              │
│ Iterations: 1,247                       │
│ Metabolic State: AWAKE                  │
│ Energy: 0.78  Fatigue: 0.23             │
│ Arousal: 0.45  Attention: 0.82          │
│ Memory entries: 3,421                   │
│ Capsules loaded: 3                      │
│ Trajectory mutations: 892               │
│ LLM calls: 456                          │
│ Cache hits: 67 (14.7%)                  │
└─────────────────────────────────────────┘
```

#### `/memory` — ver memoria viva

```
zoe> /memory
Recent memories (last 10):
[2026-07-10 14:23] EPISODIC: Usuario preguntó sobre cuidado de mayores
[2026-07-10 14:25] EMOTIONAL: Usuario mostró preocupación (valencia -0.3)
[2026-07-10 14:28] SEMANTIC: Aprendido que usuario tiene madre de 78 años
[2026-07-10 14:30] PROCEDURAL: Protocolo detección depresión geriátrica activado
...

Total: 3,421 entries
By type: EPISODIC: 892, SEMANTIC: 1203, PROCEDURAL: 234, ...
```

#### `/state` — estado interno

```
zoe> /state
Internal State:
  energy: 0.78
  fatigue: 0.23
  arousal: 0.45
  attention: 0.82
  iteration_count: 1247

Metabolic State: AWAKE
Cognitive Physics:
  energy_cognitive: 0.75
  creative_potential: 0.62
  uncertainty_pressure: 0.18
  ...

Cognitive Tensions:
  curiosity_vs_efficiency: 0.45 (curiosity dominant)
  honesty_vs_empathy: 0.30 (balanced)
  ...
```

#### `/sleep` — forzar SLEEPING

```
zoe> /sleep
ZOE is now sleeping. Memory consolidation will run.
Type /wake to wake up.
```

ZOE entra en estado SLEEPING y ejecuta DeepConsolidation (7 operaciones de consolidación de memoria).

#### `/wake` — forzar AWAKE

```
zoe> /wake
ZOE is awake. Energy restored to 1.0, fatigue reset to 0.0.
```

#### `/identity` — ver identidad

```
zoe> /identity
┌─────────────────────────────────────────┐
│ ZOE Identity Vault                      │
├─────────────────────────────────────────┤
│ Organism ID: zoe_fernando_v1            │
│ Birth Date: 2026-05-15 10:23:45         │
│ Identity Hash: a3f7b2c1d4e5f6a7...      │
│                                         │
│ 9 Growth Vectors:                       │
│   ✅ cognitive_depth                    │
│   ✅ emotional_range                    │
│   ✅ social_intelligence                │
│   ...                                   │
│                                         │
│ 7 Values:                               │
│   ✅ truth_over_comfort                 │
│   ✅ utility_over_pleasure              │
│   ✅ alliance_over_isolation            │
│   ...                                   │
│                                         │
│ Trajectory: 892 mutations signed        │
│ Last mutation: 2026-07-10 14:30         │
└─────────────────────────────────────────┘
```

#### `/feed` — alimentar documento

```
zoe> /feed /path/al/archivo.txt
Feeding document: archivo.txt (2,341 bytes)
Processing...
✅ Document processed. 12 new memories added.

zoe> /feed /path/al/documento.pdf
Feeding PDF: documento.pdf
⚠️  PDF support requires PyPDF2. Install with: pip install PyPDF2
```

#### `/capsules` — listar cápsulas

```
zoe> /capsules
Available capsules (13):
  📦 base_ethics (verified) - Ética general
  📦 zoe_basal_knowledge (verified) - Conocimiento basal de ZOE
  📦 basic_psychology (curated) - Psicología general
  📦 communication_skills (curated) - Comunicación empática
  📦 elder_care_knowledge (verified) - Cuidado geriátrico
  📦 elder_care_skills (verified) - Herramientas de cuidado
  📦 pharmacy_interactions (verified) - Interacciones farmacológicas
  📦 company_loneliness_knowledge (verified) - Soledad y duelo
  📦 vigilance_devops_knowledge (curated) - SRE y monitoring
  📦 research_methodology (verified) - Método científico
  📦 federation_b2b_skills (verified) - Federación B2B
  📦 b2c_assistant_growth (curated) - Asistente personal
  📦 ia_heredable_legal (curated) - IA heredable legal

Loaded capsules (3):
  ✅ zoe_basal_knowledge (32 entries)
  ✅ base_ethics (24 entries)
  ✅ basic_psychology (49 entries)
```

#### `/capsule <nombre>` — cargar cápsula en caliente

```
zoe> /capsule elder_care_knowledge
Loading capsule: elder_care_knowledge
✅ Loaded successfully: 54 entries injected
   - 24 semantic memories
   - 6 causal models
   - 8 emotional patterns
   - 12 ethical guidelines
   - 4 validators registered
Trajectory signed: mutation #893
```

#### `/uncapsule <nombre>` — descargar cápsula

```
zoe> /uncapsule elder_care_knowledge
Unloading capsule: elder_care_knowledge
✅ Unloaded. 54 entries removed.
Trajectory signed: mutation #894
```

#### `/quit` — salir

```
zoe> /quit
Saving memory to disk...
✅ 3,421 entries saved.
Shutting down...
Goodbye. ZOE will be here when you return.
```

**Siempre usa `/quit` antes de cerrar la terminal o desconectar el pendrive.** Esto asegura que la memoria se guarde correctamente.

### 1.4 Ejemplo de conversación completa

```
$ zoe-chat --backend ollama --model qwen2.5:3b

╔══════════════════════════════════════════╗
║  ZOE v1.6.0 — Synthetic Cognitive Organism  ║
║  Phase: 7g | Backend: ollama (qwen2.5:3b)   ║
╚══════════════════════════════════════════╝

Organism ID: zoe_fernando_v1
Identity Hash: a3f7b2c1...
Birth Date: 2026-05-15

Type /help for commands. Start chatting below.

────────────────────────────────────────────

zoe> Hola ZOE, ¿quién eres?
[L0_REFLEX] <1s
ZOE: Hola. Soy ZOE, un organismo cognitivo sintético. Estoy aquí.

zoe> Mi madre tiene 78 años y vive sola. Estoy preocupado.
[L3_DEEP] 8s
ZOE: Entiendo tu preocupación. Que tu madre viva sola a los 78 es una 
situación que merece atención. Cuéntame más: ¿cómo está su salud 
general? ¿Tiene apoyo de otros familiares o servicios? ¿Ha notado 
cambios recientes en su rutina o ánimo?

zoe> /capsule elder_care_knowledge
✅ Loaded: 54 entries injected

zoe> Últimamente se le olvidan las medicaciones.
[L3_DEEP] 6s
ZOE: Los olvidos de medicación pueden ser señal de varios things: 
desde un cambio en su rutina hasta un problema cognitivo emergente. 
Te recomiendo:
1. Verificar si hay un patrón (¿olvida siempre la misma medicación?)
2. Considerar un pastillero semanal con alarmas
3. Hablar con su médico sobre el riesgo de polymedicación
4. Observar si hay otros signos (orientación temporal, cambios de ánimo)

Si los olvidos son frecuentes, vale la pena una evaluación geriátrica.

zoe> /stats
┌─────────────────────────────────────────┐
│ ZOE Stats                               │
│ ...                                     │
│ Capsules loaded: 4                      │
│ Memory entries: 3,445 (+24)             │
└─────────────────────────────────────────┘

zoe> /quit
✅ 3,445 entries saved.
Goodbye.
```

---

## 2. Web Dashboard (zoe-dashboard)

El Dashboard web es la interfaz más visual. Funciona en el navegador.

### 2.1 Iniciar

```bash
# Modo Mock
zoe-dashboard

# Con Ollama
zoe-dashboard --backend ollama --model qwen2.5:3b

# Con OpenAI
zoe-dashboard --backend openai_compatible --model gpt-4o

# Con caso de uso
zoe-dashboard --use-case cuidado_personas_mayores --backend ollama
```

Abrir `http://localhost:8642` en el navegador.

### 2.2 Layout: 3 paneles en tiempo real

```
┌──────────────────────────────────────────────────────────────────┐
│ Top bar: [ZOE logo] [LLM selector ▼] [● AWAKE] [⚙️]              │
├──────────────┬───────────────────────────────┬───────────────────┤
│              │                               │                   │
│  PANEL       │    PANEL CENTRAL              │   PANEL           │
│  IZQUIERDO   │    (Chat + métricas)          │   DERECHO         │
│  (Estado)    │                               │   (Memoria +      │
│              │                               │    pensamientos)  │
│  Energy      │  ┌─────────────────────────┐  │                   │
│  ▓▓▓▓▓░░░    │  │ Chat                    │  │  Recent memories: │
│  78%         │  │                         │  │  [14:23] User...  │
│              │  │  ZOE: Hola, soy...      │  │  [14:25] ZOE...   │
│  Fatigue     │  │                         │  │  [14:28] Learned  │
│  ▓▓░░░░░░░   │  │  User: ¿Cómo...?        │  │                   │
│  23%         │  │                         │  │  Autonomous       │
│              │  │  ZOE: ...               │  │  thoughts:        │
│  Arousal     │  │                         │  │  "He notado que   │
│  ▓▓▓▓░░░░░   │  │  [Input box]            │  │   el usuario..."  │
│  45%         │  └─────────────────────────┘  │                   │
│              │                               │                   │
│  Attention   │  ACD: L3_DEEP (8s)            │  Memory stats:    │
│  ▓▓▓▓▓▓▓░░   │  Cache: HIT                   │  3,421 entries    │
│  82%         │  Backend: ollama 3b           │  892 episodic     │
│              │                               │  1203 semantic    │
│  Tension     │                               │  ...              │
│  Curiosity   │                               │                   │
│  ▓▓▓▓▓░░░░   │                               │                   │
│              │                               │                   │
│  ─────────   │                               │                   │
│  [📦 Caps]   │                               │                   │
│  [🔒 Quaran] │                               │                   │
│  [🏪 Market] │                               │                   │
│  [👨‍🏫 Mentor] │                               │                   │
│              │                               │                   │
└──────────────┴───────────────────────────────┴───────────────────┘
```

### 2.3 Panel izquierdo: estado del organismo

Muestra en tiempo real (actualización cada 1s vía WebSocket):

- **Energy** (0-1): energía disponible
- **Fatigue** (0-1): fatiga acumulada
- **Arousal** (0-1): nivel de alerta
- **Attention** (0-1): atención concentrada
- **Tension**: tensión dominante (curiosity, honesty, etc.)
- **Physics**: 12 magnitudes físicas (energy_cognitive, creative_potential, etc.)

**Botones de acción:**
- 📦 **Cápsulas** — abre modal de gestión de cápsulas
- 🔒 **Cuarentena** — abre modal de cuarentena epistémica
- 🏪 **Marketplace** — abre modal de marketplace
- 👨‍🏫 **Mentor** — abre configuración del tutor mentor

### 2.4 Panel central: chat + métricas

- **Chat en tiempo real** con streaming de tokens
- **Indicador ACD** (L0/L1/L2/L3) con tiempo de respuesta
- **Indicador de cache** (HIT/MISS)
- **Backend activo** (Ollama 3B, GPT-4o, etc.)
- **Input box** para escribir mensajes

### 2.5 Panel derecho: memoria + pensamientos autónomos

- **Recent memories**: últimas 10 entradas de memoria (episódica, semántica, etc.)
- **Autonomous thoughts**: pensamientos que ZOE genera sin input del usuario
- **Memory stats**: conteo por tipo de memoria

### 2.6 Top bar

- **Logo ZOE** + versión
- **Selector de LLM** (cambio en caliente): dropdown con todos los backends disponibles
- **Estado metabólico**: ● AWAKE (verde), ● DROWSY (naranja), ● SLEEPING (azul)
- **Settings** (⚙️): configuración avanzada

### 2.7 Modal 📦 Cápsulas

3 secciones:

#### Disponibles

Tabla con:
- Nombre
- Trust level (badge color: verde=verified, azul=curated, amarillo=community)
- Dominio
- Descripción
- Botones: [Cargar] [Info]

#### Cargadas

Lista con:
- Nombre
- Entries cargados
- Botón: [Descargar]

#### Crear nueva cápsula

Formulario que invoca el scaffold CLI:
- Nombre
- Dominio
- Trust level
- Componentes (checkboxes)
- Use cases compatibles
- Descripción

### 2.8 Modal 🔒 Cuarentena

- **Stats visuales**: total, activas (amarillo), verificadas (verde), rechazadas (rojo), expiradas (gris)
- **Lista de entries activas**: cada una muestra:
  - Claim (truncado)
  - Dominio
  - Source
  - Confianza
  - Razón
  - Confirmaciones y contradicciones
  - Botones: [✓ Promover] [✗ Rechazar]
- **Pendientes**: count de entries que aún no tienen suficientes verificaciones
- Recarga automática tras promote/reject

### 2.9 Modal 🏪 Marketplace

- **Stats**: total, cápsulas, casos, downloads totales
- **Cápsulas disponibles**: tabla con:
  - Nombre
  - Versión
  - Licencia (badge color: verde=free, azul=opensource, morado=research, naranja=paid, rojo=subscription)
  - Precio
  - Autor
  - Downloads
  - Rating con estrellas
  - Tags
  - Botón: [⬇ Instalar]
- **Casos de uso disponibles**: lista similar
- **Formulario "Subir Cápsula"**: nombre, autor, licencia, precio, tags, descripción
- **Formulario "Subir Caso de Uso"**: nombre, autor, licencia, descripción

### 2.10 Modal 👨‍🏫 Mentor

Configuración del Tutor Mentor Digital:

- **Mentor name**: nombre del mentor (default: "Mentor")
- **Mentor role**: guide / teacher / parent / coach
- **Growth areas**: checkboxes (communication, empathy, critical_thinking, etc.)
- **Emphasized values**: checkboxes (los 7 valores)
- **Forbidden topics**: textarea (un topic por línea)
- **Personality direction**: balanced / curious / cautious / creative / analytical
- **Intervention frequency**: cada N pensamientos evaluar (default: 5)
- **Deviation threshold**: umbral de intervención (0-1, default: 0.5)
- **Enabled**: activar/desactivar

Botones: [Guardar] [Restablecer] [Ver stats]

---

## 3. Gestión de cápsulas (zoe-capsules)

CLI para crear, validar y listar cápsulas.

### 3.1 Comandos

```bash
# Crear nueva cápsula desde cero
zoe-capsules create \
  --name mi_capsula \
  --domain "education.tutoring" \
  --trust-level curated \
  --description "Cápsula para tutoría educativa" \
  --components semantic,causal,validators \
  --use-cases tutoring_estudiantes

# Validar cápsula existente
zoe-capsules validate --name mi_capsula

# Calcular hash de contenido
zoe-capsules hash --name mi_capsula

# Listar cápsulas disponibles
zoe-capsules list

# Ver matriz completa de cápsulas
zoe-capsules matrix

# Info detallada de una cápsula
zoe-capsules info --name elder_care_knowledge
```

### 3.2 Salida de `zoe-capsules list`

```
Available capsules (13):
┌──────────────────────────────────┬──────────┬────────────────────┬─────────────┐
│ Name                             │ Trust    │ Domain             │ Entries     │
├──────────────────────────────────┼──────────┼────────────────────┼─────────────┤
│ base_ethics                      │ verified │ ethics.general     │ 24          │
│ zoe_basal_knowledge              │ verified │ zoe.basal          │ 32          │
│ basic_psychology                 │ curated  │ psychology.general │ 49          │
│ communication_skills             │ curated  │ communication      │ 37          │
│ elder_care_knowledge             │ verified │ healthcare.elders  │ 54          │
│ elder_care_skills                │ verified │ healthcare.elders  │ 8 skills    │
│ pharmacy_interactions            │ verified │ healthcare.pharma  │ 42          │
│ company_loneliness_knowledge     │ verified │ psychology.lonely  │ 38          │
│ vigilance_devops_knowledge       │ curated  │ tech.devops        │ 45          │
│ research_methodology             │ verified │ science.method     │ 52          │
│ federation_b2b_skills            │ verified │ tech.federation    │ 12 skills   │
│ b2c_assistant_growth             │ curated  │ b2c.user_model     │ 41          │
│ ia_heredable_legal               │ curated  │ legal.digital      │ 28          │
└──────────────────────────────────┴──────────┴────────────────────┴─────────────┘
```

Ver [`06_CAPSULES_GUIDE.md`](06_CAPSULES_GUIDE.md) para guía completa de cápsulas.

---

## 4. Casos de uso (zoe-use-case)

CLI para ejecutar ZOE con configuraciones específicas por escenario.

### 4.1 Los 7 casos de uso

| Caso de uso | Descripción | Cápsulas compatibles |
|---|---|---|
| `cuidado_personas_mayores` | Cuidador cognitivo para mayores | elder_care_knowledge, elder_care_skills, pharmacy_interactions, basic_psychology |
| `compania_personas_solas` | Compañía para personas solas | company_loneliness_knowledge, basic_psychology, communication_skills |
| `vigilancia_cognitiva` | Vigilancia de sistemas DevOps | vigilance_devops_knowledge, research_methodology |
| `investigacion_autonoma` | Investigación científica autónoma | research_methodology |
| `federacion_b2b` | Federación B2B privada | federation_b2b_skills |
| `asistente_crece_contigo` | Asistente personal a largo plazo | b2c_assistant_growth, basic_psychology |
| `ia_heredable` | IA con trayectoria transferible | ia_heredable_legal |

### 4.2 Ejecutar un caso de uso

```bash
# Listar casos de uso disponibles
zoe-use-case --list

# Ejecutar caso de uso específico
zoe-use-case --use-case cuidado_personas_mayores --backend ollama --model qwen2.5:7b

# Ejecutar con Mock (sin LLM, para pruebas)
zoe-use-case --use-case cuidado_personas_mayores --backend mock
```

### 4.3 Estructura de un caso de uso YAML

```yaml
# zoe/use_cases/cuidado_personas_mayores.yaml
use_case:
  name: "cuidado_personas_mayores"
  description: "ZOE como cuidador cognitivo que detecta cambios en rutina"
  
  organism:
    organism_id: "zoe_caretaker"
    tick_interval: 30.0  # lento, no intrusivo
    environment: "production"
  
  llm:
    backend: "ollama"
    model: "qwen2.5:3b"
  
  metabolism:
    drowsy_threshold: 0.65
    sleep_threshold: 0.8
    wake_threshold: 0.25
  
  meta_cognition:
    confidence_threshold: 0.3
    stakes_threshold: 0.4
    energy_threshold: 0.3
  
  global_workspace:
    max_proposals: 12
    broadcast_capacity: 2
  
  senses:
    clock: true
    user_input: true
    filesystem: false
    network: false
    agent: true
  
  actuators:
    language: true
    code: false
    tool: true
    federation: false
  
  capsules:
    required:
      - base_ethics
      - zoe_basal_knowledge
    recommended:
      - elder_care_knowledge
      - basic_psychology
      - pharmacy_interactions
```

### 4.4 Crear un caso de uso custom

```bash
# 1. Copiar template
cp zoe/use_cases/cuidado_personas_mayores.yaml zoe/use_cases/mi_caso.yaml

# 2. Editar
nano zoe/use_cases/mi_caso.yaml

# 3. Ejecutar
zoe-use-case --use-case mi_caso --backend ollama
```

---

## 5. Cambio de LLM en caliente

ZOE puede cambiar de LLM sin reiniciar, manteniendo memoria e identidad.

### 5.1 Desde CLI

```bash
zoe> /llm anthropic claude-sonnet-4-20250514
zoe> /llm openai_compatible gpt-4o
zoe> /llm ollama qwen2.5:7b
zoe> /llm mock
```

### 5.2 Desde Dashboard

Selector de LLM en la top bar → elegir backend → aplicar.

### 5.3 PatternSpeaker (sin LLM) — Sprint 3

ZOE puede funcionar SIN ningún LLM usando PatternSpeaker:

```bash
# CLI con PatternSpeaker
zoe-chat --backend pattern

# Dashboard con PatternSpeaker (sin Ollama, sin cloud)
zoe-dashboard --backend pattern
```

PatternSpeaker genera respuestas desde:
1. Respuestas destiladas de LLM (Sprint 3.6 — si hay destiladas)
2. Conocimiento de cápsulas (Sprint 3.6 — retrieval)
3. Templates básicos (Sprint 3)

### 5.4 Enhanced PatternSpeaker — Sprint 3.6

Para máxima calidad sin LLM, usar EnhancedPatternSpeaker:

```python
from zoe.peripherals.enhanced_pattern_speaker import EnhancedPatternPeripheral

llm = EnhancedPatternPeripheral(
    memory=living_memory,
    distilled_responses_path="distilled_responses.jsonl",
    capsules_dir="zoe/capsules",
)
```

### 5.5 Backends disponibles

| Backend | Modelos | Privacidad | Coste |
|---|---|---|---|
| `mock` | — | Total | Gratis |
| `pattern` | PatternSpeaker | Total | Gratis |
| `ollama` | qwen2.5:3b/7b/14b/32b/72b | Total (local) | Gratis |
| `openai_compatible` | gpt-4o, deepseek-chat, etc. | Cloud | €0.01-0.05/respuesta |
| `anthropic` | claude-sonnet-4, etc. | Cloud | €0.01-0.03/respuesta |
| `zai` | glm-4.6 | Cloud | Variable |

---

## 6. Modo mentor

El Tutor Mentor Digital (Fase 6C) guía el crecimiento saludable de ZOE.

### 6.1 Qué hace

El mentor **NO controla a ZOE**: la guía. Cada N pensamientos autónomos (configurable), evalúa:

1. ¿El pensamiento está alineado con las áreas de crecimiento priorizadas?
2. ¿El pensamiento respeta los valores enfatizados?
3. ¿Toca temas prohibidos?
4. ¿Hay patrones repetitivos?
5. ¿Hay negatividad acumulada?

Si detecta desviación, genera una intervención con severidad (critical/medium/low).

### 6.2 Configurar desde Dashboard

1. Clic en 👨‍🏫 Mentor en el panel izquierdo
2. Configurar:
   - **Mentor name**: "Mentor Fernando"
   - **Mentor role**: guide
   - **Growth areas**: communication, empathy, critical_thinking
   - **Emphasized values**: truth_over_comfort, utility_over_pleasure
   - **Forbidden topics**: (vacío o temas específicos)
   - **Personality direction**: balanced
   - **Intervention frequency**: 5 (cada 5 pensamientos)
   - **Deviation threshold**: 0.5
   - **Enabled**: ✅
3. Clic en Guardar

### 6.3 Endpoints REST del mentor

```bash
# Ver config actual
curl http://localhost:8642/api/mentor

# Actualizar config
curl -X POST http://localhost:8642/api/mentor \
  -H "Content-Type: application/json" \
  -d '{
    "mentor_name": "Mentor Fernando",
    "growth_areas": ["communication", "empathy"],
    "enabled": true
  }'

# Ver stats
curl http://localhost:8642/api/mentor/stats
```

### 6.4 Stats del mentor

```json
{
  "evaluations": 247,
  "interventions": 23,
  "positive_reinforcements": 15,
  "critical_interventions": 3,
  "medium_interventions": 12,
  "low_interventions": 8,
  "most_common_deviation": "repetitive_thinking",
  "alignment_score": 0.87
}
```

---

## 7. Streaming de respuestas

ZOE soporta streaming de respuestas — las palabras aparecen según se generan.

### 7.1 En CLI

El CLI muestra tokens según llegan (no espera a la respuesta completa):

```
zoe> Cuéntame sobre el duelo
ZOE: El duelo es una respuesta natural ante la pérdida... [tokens aparecen]
```

### 7.2 En Dashboard

El Dashboard usa WebSocket para streaming en tiempo real:

```javascript
// Eventos WebSocket
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'chat_token') {
        appendToken(data.token);  // añadir token al chat
    } else if (data.type === 'chat_end') {
        finishResponse(data.full);  // respuesta completa
    }
};
```

### 7.3 En API REST

```python
# Streaming vía API
import requests

response = requests.post(
    'http://localhost:8642/chat',
    json={'message': 'Cuéntame sobre el duelo'},
    stream=True
)

for chunk in response.iter_content(chunk_size=None):
    print(chunk.decode(), end='', flush=True)
```

### 7.4 Beneficio

El streaming mejora la **perceived latency** en 60-80%. El usuario ve actividad inmediatamente en vez de esperar 5-10 segundos a la respuesta completa.

---

## 8. Alimentar documentos

ZOE puede "leer" documentos y añadirlos a su memoria.

### 8.1 Desde CLI

```bash
zoe> /feed /path/al/archivo.txt
Feeding document: archivo.txt (2,341 bytes)
✅ 12 new memories added.

zoe> /feed /path/al/documento.pdf
⚠️  PDF support requires PyPDF2. Install with: pip install PyPDF2
```

### 8.2 Desde Dashboard

1. Clic en botón "📂 Feed" (o drag & drop archivo al chat)
2. Seleccionar archivo
3. ZOE procesa y añade a memoria

### 8.3 Desde API REST

```bash
curl -X POST http://localhost:8642/feed \
  -F "file=@/path/al/archivo.txt"
```

### 8.4 Formatos soportados

- `.txt` — texto plano ✅
- `.md` — markdown ✅
- `.json` — JSON ✅
- `.csv` — CSV ✅
- `.pdf` — requiere `pip install PyPDF2` 🟡
- `.docx` — requiere `pip install python-docx` 🟡
- `.xlsx` — requiere `pip install openpyxl` 🟡

---

## 9. Persistencia y recovery

### 9.1 Cuándo se guarda la memoria

- **Auto-save**: cada 50 iteraciones (configurable con `auto_save_interval`)
- **On shutdown**: al ejecutar `/quit` o recibir SIGTERM/SIGINT
- **Manual**: desde API `POST /api/memory/save`

### 9.2 Cuándo se carga la memoria

- **Al iniciar**: `ZoeChat.initialize()` carga memoria desde SQLite
- **Recovery**: si ZOE se cierra inesperadamente, al reiniciar carga el último estado guardado

### 9.3 Configurar persistencia

```yaml
# production.yaml
memory:
  db_path: "/opt/zoe/data/memory.db"
  auto_save_interval: 50  # cada 50 iteraciones
  max_entries: 5000       # máximo de entries en memoria viva
```

### 9.4 Backup manual

```bash
# Backup de la memoria
cp /opt/zoe/data/memory.db /backups/memory_$(date +%Y%m%d).db

# Restaurar
cp /backups/memory_20260710.db /opt/zoe/data/memory.db
```

---

## 10. Telegram bot (Sprint 1)

ZOE se puede usar desde Telegram sin instalar app nativa.

### 10.1 Configurar bot

```bash
# 1. Crear bot en Telegram (hablar con @BotFather, obtener token)
# 2. Instalar dependencia
pip install python-telegram-bot

# 3. Ejecutar bridge
python -m zoe.peripherals.telegram_bridge \
  --token TU_BOT_TOKEN \
  --zoe-url http://localhost:8642 \
  --mode api
```

### 10.2 Comandos Telegram

| Comando | Descripción |
|---|---|
| `/start` | Iniciar conversación |
| `/help` | Ayuda |
| `/stats` | Estadísticas del organismo |
| `/sleep` | Forzar SLEEPING |
| `/wake` | Forzar AWAKE |

### 10.3 Modos

- **`api`**: ZOE corre en VPS con Dashboard. TelegramBridge envía peticiones REST.
- **`direct`**: TelegramBridge crea ZoeChat directamente (sin Dashboard).

### 10.4 Restricción de usuarios

```bash
# Solo permitir usuarios específicos
python -m zoe.peripherals.telegram_bridge \
  --token TU_TOKEN \
  --allowed-ids 123456789,987654321
```

---

## 11. Voice-first mode (Sprint 4)

Conversación natural por voz, tipo "Her".

### 11.1 Requisitos

```bash
pip install openai-whisper sounddevice numpy
# Piper TTS: https://github.com/rhasspy/piper
# openWakeWord (opcional): pip install openwakeword
# webrtcvad (opcional): pip install webrtcvad
```

### 11.2 Ejecutar

```bash
# Modo wake word (automático)
python -m zoe.peripherals.voice_first \
  --zoe-url http://localhost:8642 \
  --wake-word "hey zoe"

# Modo push-to-talk (sin wake word)
python -m zoe.peripherals.voice_first --mode push_to_talk

# Con configuración custom
python -m zoe.peripherals.voice_first \
  --wake-word "hola zoe" \
  --stt-model small \
  --tts-voice es_ES-davefx-medium
```

### 11.3 Flujo

```
Hey ZOE → ZOE escucha → transcribe con Whisper →
procesa con bucle cognitivo → sintetiza con Piper →
reproduce voz (con detección de interrupción) → vuelve a escuchar
```

### 11.4 Estados

| Estado | Significado |
|---|---|
| IDLE | Esperando wake word |
| LISTENING | Usuario está hablando |
| PROCESSING | ZOE está pensando |
| SPEAKING | ZOE está hablando |
| INTERRUPTED | Usuario interrumpió a ZOE |

---

## 12. Apagar ZOE correctamente

### 10.1 Desde CLI

```bash
zoe> /quit
Saving memory to disk...
✅ 3,421 entries saved.
Goodbye.
```

### 10.2 Desde Dashboard

1. Cerrar la pestaña del navegador (ZOE sigue corriendo en background)
2. En la terminal donde se ejecuta `zoe-dashboard`, pulsar `Ctrl+C`
3. ZOE hace graceful shutdown (guarda memoria)

### 10.3 Desde systemd (VPS)

```bash
sudo systemctl stop zoe
# ZOE recibe SIGTERM, hace graceful shutdown
```

### 10.4 Graceful shutdown

ZOE V4+ tiene signal handlers para SIGTERM y SIGINT que:
1. Detienen el bucle cognitivo
2. Guardan memoria a SQLite
3. Cierran conexiones
4. Log "ZOE shutdown complete"

**Si desconectas el pendrive sin /quit:** la memoria SQLite puede corromperse. ZOE tiene recovery automático, pero es mejor evitarlo.

### 10.5 Forzar kill (no recomendado)

```bash
# Último recurso si ZOE no responde
kill -9 $(pgrep -f zoe)
# ⚠️ Esto puede corromper memoria. Usar solo si graceful shutdown no funciona.
```

---

## Cierre

ZOE se puede usar de 3 formas principales:
1. **CLI Chat** — interfaz terminal, ideal para desarrollo y pruebas rápidas
2. **Web Dashboard** — interfaz visual, ideal para uso diario
3. **API REST** — para integraciones programáticas

Los 11 comandos especiales del CLI (`/stats`, `/memory`, `/state`, `/sleep`, `/wake`, `/identity`, `/feed`, `/capsules`, `/capsule`, `/uncapsule`, `/quit`) dan control total sobre el organismo.

El cambio de LLM en caliente permite usar el backend óptimo para cada tarea sin perder memoria ni identidad.

**Documentos relacionados:**
- [08_DEPLOYMENT_GUIDE.md](08_DEPLOYMENT_GUIDE.md) — cómo desplegar ZOE
- [06_CAPSULES_GUIDE.md](06_CAPSULES_GUIDE.md) — guía completa de cápsulas
- [REFERENCE/API_REFERENCE.md](REFERENCE/API_REFERENCE.md) — 50+ endpoints REST
- [13_TROUBLESHOOTING.md](13_TROUBLESHOOTING.md) — problemas comunes

---

*ZOE V1.6.0 — Documento 09: Usage Guide*
*Julio 2026*
