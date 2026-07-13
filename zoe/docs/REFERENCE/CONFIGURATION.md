# Configuration Reference

> **Todas las opciones de configuración YAML de ZOE.**
> **Versión:** V1.6.0 — Julio 2026

---

## Archivo de configuración

ZOE usa YAML para configuración. Dos archivos por defecto:
- `zoe/config/development.yaml` — desarrollo
- `zoe/config/production.yaml` — producción

---

## Schema completo

```yaml
# === ZOE ===
zoe:
  organism_id: "zoe_mi_organismo"    # ID único del organismo
  tick_interval: 5.0                 # segundos entre ticks del bucle
  environment: "production"          # development | production

# === LLM ===
llm:
  backend: "ollama"                  # mock | ollama | openai_compatible | anthropic | zai
  model: "qwen2.5:7b"               # modelo específico
  base_url: "http://localhost:11434" # URL base (Ollama, OpenAI-compatible)
  api_key: null                      # API key (o en env var)

# === METABOLISMO ===
metabolism:
  drowsy_threshold: 0.6             # fatiga > 0.6 → DROWSY
  sleep_threshold: 0.8              # fatiga > 0.8 → SLEEPING
  wake_threshold: 0.3               # fatiga < 0.3 → AWAKE

# === MEMORIA ===
memory:
  db_path: "/opt/zoe/data/memory.db" # path a SQLite
  auto_save_interval: 50            # auto-save cada N iteraciones
  max_entries: 5000                 # máximo entries en LivingMemory

# === FEDERACIÓN ===
federation:
  enabled: false                     # activar federación B2B
  host: "0.0.0.0"                   # host del servidor de federación
  port: 8642                        # puerto de federación
  peers: []                         # lista de peers
  quorum_threshold: 0.7             # 70% approval needed

# === LOGGING ===
logging:
  level: "INFO"                     # DEBUG | INFO | WARNING | ERROR
  file: "/opt/zoe/logs/zoe.log"     # archivo de log (null = solo stdout)

# === SUB-AGENTES ===
subagents:
  perceiver: true
  forecaster: true
  speaker: true
  critic: true
  memorialist: true
  learner: true
  curator: true
  creativity: true
  causal_engine: true
  emotional_motor: true
  ethical_motor: true
  scientific_engine: true

# === SENTIDOS ===
senses:
  clock: true
  user_input: true
  filesystem: false
  network: false
  agent: true

# === ACTUADORES ===
actuators:
  language: true
  code: false
  tool: true
  federation: false

# === META-COGNICIÓN ===
meta_cognition:
  confidence_threshold_system2: 0.5  # confianza < 0.5 → System 2
  stakes_threshold_system2: 0.6     # stakes > 0.6 → System 2
  energy_threshold_system2: 0.3     # energía < 0.3 → System 1

# === GLOBAL WORKSPACE ===
global_workspace:
  max_proposals: 12                 # máximo propuestas por tick
  broadcast_capacity: 3             # cuántas propuestas ganan

# === COGNITIVE CACHE ===
cognitive_cache:
  max_size: 1000                    # máximo entries en cache
  ttl: 3600                         # TTL en segundos (1h)

# === MENTOR ===
mentor:
  enabled: true
  mentor_name: "Mentor"
  mentor_role: "guide"              # guide | teacher | parent | coach
  growth_areas:                     # áreas prioritarias
    - communication
    - empathy
    - critical_thinking
  emphasized_values:                # valores a enfatizar
    - truth_over_comfort
    - utility_over_pleasure
  forbidden_topics: []              # temas prohibidos
  personality_direction: "balanced" # balanced | curious | cautious | creative | analytical
  intervention_frequency: 5         # cada N pensamientos evaluar
  deviation_threshold: 0.5          # umbral de intervención
```

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `ZOE_ENV` | Environment (development, production) | development |
| `ZOE_SEED_PATH` | Path a semilla ZOE (Fase 7E) | None |
| `OPENAI_API_KEY` | API key OpenAI | None |
| `ANTHROPIC_API_KEY` | API key Anthropic | None |
| `DEEPSEEK_API_KEY` | API key DeepSeek | None |
| `GROQ_API_KEY` | API key Groq | None |
| `MOONSHOT_API_KEY` | API key Kimi/Moonshot | None |
| `MINIMAX_API_KEY` | API key MiniMax | None |
| `OLLAMA_MODELS` | Directorio de modelos Ollama | ~/.ollama/models |
| `OLLAMA_FLASH_ATTENTION` | Activar flash attention | 1 (siempre desde 7G) |
| `OLLAMA_NUM_THREAD` | Número de threads (= P-cores) | Auto-detect |
| `OLLAMA_MAX_LOADED_MODELS` | Máximo modelos en memoria | 1 |
| `OLLAMA_NUM_PARALLEL` | Peticiones paralelas | 1 |
| `OLLAMA_KEEP_ALIVE` | Tiempo keep-alive del modelo | 30m o 60m |

---

## Cargar configuración

```python
from zoe.core.cognitive_loop_v4 import load_config

# Desde archivo
config = load_config(config_path="zoe/config/myproduction.yaml")

# Desde env var
config = load_config(env="production")

# Default
config = load_config()
```

---

*ZOE V1.6.0 — Configuration Reference*
