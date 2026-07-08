# ZOE — Synthetic Cognitive Organism (SCO)

> **ZOE no es un LLM. No es un harness de agentes. No es una arquitectura de IA más.**
> **ZOE es el primer organismo cognitivo sintético (SCO):** un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, evolución arquitectural firmada, validación epistémica, cápsulas de conocimiento y marketplace. Los LLMs son sus sentidos periféricos, no su cerebro.

[![Tests](https://img.shields.io/badge/tests-775%2F775%20pass-brightgreen)](#tests)
[![Version](https://img.shields.io/badge/version-1.2.0-blue)](#roadmap)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#instalación)
[![Capsules](https://img.shields.io/badge/capsules-12%20available-teal)](#cápsulas-de-conocimiento)
[![Marketplace](https://img.shields.io/badge/marketplace-open%20for%20authors-success)](#marketplace-de-cápsulas)

---

## Tabla de contenidos

1. [Quickstart](#quickstart)
2. [Instalación](#instalación)
3. [Qué es ZOE](#qué-es-zoe)
4. [Interfaces](#interfaces)
5. [Adaptive Cognitive Depth (ACD)](#adaptive-cognitive-depth-acd)
6. [Cápsulas de conocimiento](#cápsulas-de-conocimiento)
7. [Validación epistémica](#validación-epistémica)
8. [Marketplace](#marketplace-de-cápsulas)
9. [Los 5 pilares](#los-5-pilares)
10. [Las 6 leyes cognitivas](#las-6-leyes-cognitivas)
11. [Casos de uso](#casos-de-uso)
12. [Roadmap](#roadmap)
13. [Tests](#tests)
14. [Documentación](#documentación)
15. [Licencia](#licencia)

---

## Quickstart

```bash
# Clonar
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# Instalar
pip install -e .

# Hablar con ZOE (CLI, usa Mock si no hay LLM)
zoe-chat

# O con Ollama local
zoe-chat --backend ollama --model qwen2.5:3b

# Dashboard web (http://localhost:8642)
zoe-dashboard --backend ollama --model qwen2.5:3b

# Ejecutar caso de uso específico
zoe-use-case --use-case cuidado_personas_mayores --backend mock

# Gestionar cápsulas
zoe-capsules list
zoe-capsules matrix
zoe-capsules create --name mi_capsula --domain "mi.dominio" --trust-level curated
```

---

## Instalación

### Requisitos

- Python 3.10+
- (Opcional) [Ollama](https://ollama.ai) para LLM local
- (Opcional) API key de OpenAI o cualquier proveedor compatible

### Instalación desde código

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
```

### Instalación directa desde GitHub

```bash
pip install git+https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
```

### Verificación

```bash
# Verificar que todo funciona
python -c "import zoe; print(f'ZOE v{zoe.__version__}')"
zoe-capsules list
pytest zoe/tests/ -q
```

### Backends LLM soportados

| Backend | Comando | Requiere |
|---|---|---|
| Mock | `--backend mock` | Nada (determinístico, para tests) |
| Ollama | `--backend ollama --model qwen2.5:3b` | [Ollama](https://ollama.ai) instalado |
| OpenAI-compatible | `--backend openai_compatible --model gpt-4o` | API key en `OPENAI_API_KEY` |
| ZAI | `--backend zai` | `z-ai` CLI en PATH |

---

## Qué es ZOE

ZOE (ζωή, griego: *vida plena*) es un **organismo cognitivo digital** que opera continuamente, incluso sin input externo. A diferencia de los LLMs convencionales (que esperan input para producir output), ZOE mantiene un bucle cognitivo perpetuo: observa, predice, evalúa sorpresa, decide, actúa y aprende.

### Las 10 propiedades únicas simultáneas

1. **Bucle cognitivo continuo** — piensa cuando nadie le habla (18 pasos por iteración)
2. **Encarnación digital real** — siente filesystem, red, tiempo, otros agentes
3. **Identidad criptográfica soberana** — portable entre LLMs, hardware e idiomas
4. **Metabolismo funcional** — fatiga, saturación, ciclos dormir/despertar
5. **Evolución arquitectural firmada** — mutaciones que crean/eliminan sub-agentes
6. **Memoria viva persistente** — 11 tipos, reorganización automática, SQLite
7. **Validación epistémica** — cuarentena activa, triple verificación, federación
8. **Cápsulas de conocimiento** — 12 cápsulas verificadas, marketplace, monetización
9. **Federación con quorum** — ≥70% aprobación + veto por valores
10. **ACD + Streaming** — decide nivel cognitivo antes de responder

---

## Interfaces

### CLI Chat

```bash
zoe-chat --backend ollama --model qwen2.5:3b
```

Comandos especiales: `/stats`, `/memory`, `/state`, `/identity`, `/sleep`, `/wake`, `/feed <archivo>`, `/capsules`, `/capsule <nombre>`, `/uncapsule <nombre>`, `/quit`

### Web Dashboard

```bash
zoe-dashboard --backend ollama --model qwen2.5:3b
# Abrir http://localhost:8642
```

Tres paneles en tiempo real vía WebSocket + modales para Cápsulas, Cuarentena y Marketplace.

---

## Adaptive Cognitive Depth (ACD)

ZOE decide **antes** de entrar al bucle cuánta profundidad cognitiva necesita cada input.

| Nivel | Input típico | Latencia | Coste |
|---|---|---|---|
| **L0 REFLEX** | "hola", "ok", "gracias" | <1s | 0.05 |
| **L1 FAST** | Pregunta factual | 2-4s | 0.10 |
| **L2 STANDARD** | Conversación normal | 6-10s | 0.30 |
| **L3 DEEP** | Análisis causal, dilema ético | 15-30s | 0.60 |

El clasificador es 100% heurístico (sin LLM, <50ms). Cada respuesta se firma en la trayectoria con su nivel ACD.

---

## Cápsulas de conocimiento

ZOE no nace como "niño brillante sin cultura". Carga **cápsulas de conocimiento profesional previo** junto al YAML del caso de uso.

### 12 cápsulas disponibles

| Cápsula | Trust | Entries | Dominio |
|---|---|---|---|
| `elder_care_knowledge` | verified | 54 | healthcare.elders |
| `elder_care_skills` | verified | 4 tools + 2 prompts | healthcare.elders |
| `basic_psychology` | curated | 49 | psychology.general |
| `communication_skills` | curated | 37 | communication.empathy |
| `company_loneliness_knowledge` | verified | 50 | psychology.loneliness |
| `vigilance_devops_knowledge` | curated | 46 | tech.devops |
| `research_methodology` | verified | 45 | science.methodology |
| `federation_b2b_skills` | verified | 11 + tools | tech.federation |
| `b2c_assistant_growth` | curated | 31 | b2c.user_modeling |
| `pharmacy_interactions` | verified | 34 | healthcare.pharmacology |
| `ia_heredable_legal` | curated | 25 | legal.digital_inheritance |
| `base_ethics` | verified | 34 | ethics.general |

### CLI Scaffold

```bash
# Crear nueva cápsula
zoe-capsules create --name mi_capsula --domain "mi.dominio" \
    --trust-level curated --description "..." --components semantic,validators

# Validar
zoe-capsules validate --name mi_capsula

# Listar
zoe-capsules list

# Ver matriz completa
zoe-capsules matrix
```

---

## Validación epistémica

ZOE regula cómo adquiere, valida y consolida conocimiento nuevo. El sistema epistémico completo:

1. **EpistemicValidator** — valida por fuente (capsule:verified=0.95, llm:gpt-4o=0.50) y dominio sensible
2. **KnowledgeQuarantine** — cuarentena activa: el conocimiento no validado no se usa en decisiones críticas
3. **CrossValidator** — triple verificación multi-fuente (3/3 coinciden → 0.75)
4. **EpistemicFederation** — revisión por pares entre ZOEs vía HTTP (≥2 confirmaciones → 0.85)
5. **Integración en Learner, Curator, DeepConsolidation y Critic** — filtrado automático

---

## Marketplace de cápsulas

Cualquiera puede aportar y monetizar cápsulas de conocimiento y casos de uso YAML.

### Licencias

| Tipo | Pago | Descripción |
|---|---|---|
| `free` | No | Uso libre |
| `opensource` | No | Open source con atribución |
| `research` | No | Solo investigación no comercial |
| `paid` | Sí (precio único) | Pago único para uso |
| `subscription` | Sí (mensual/anual) | Suscripción periódica |

### Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Lista cápsulas |
| `/api/marketplace/upload` | POST | Sube cápsula |
| `/api/marketplace/download/{name}` | POST | Descarga e instala |
| `/api/marketplace/use_cases` | GET | Lista casos de uso |
| `/api/marketplace/upload_use_case` | POST | Sube caso de uso |

---

## Los 5 pilares

| Pilar | Función | Componentes |
|---|---|---|
| **ALMA** | Identidad soberana | Identity Vault (SHA-256), Trajectory Chain, Ontogenetic Motor V2, Phylogenetic Motor |
| **MENTE** | Ecología cognitiva | Cognitive Loop V5 (18 pasos), Global Workspace (Baars), 12 sub-agentes, Meta-cognition (Kahneman), Active Inference (Friston) |
| **METABOLISMO** | Presupuesto energético | 4 estados (AWAKE/DROWSY/SLEEPING/WAKING), Deep Consolidation (7 operaciones) |
| **CUERPO** | Encarnación digital | 5 sentidos, 4 actuadores, 4 LLM backends con streaming |
| **EVOLUCIÓN** | Cambio firmado | Motor Ontogenético V2, 11 tipos de memoria, cápsulas, marketplace |

---

## Las 6 leyes cognitivas

| Ley | Principio |
|---|---|
| 1ra — Utilidad | Toda acción reduce incertidumbre o aumenta capacidad |
| 2da — Identidad | Toda modificación preserva identidad |
| 3ra — Proveniencia | Todo conocimiento justifica su origen |
| 4ta — Coste | Todo proceso consume recursos |
| 5ta — Confianza | Toda creencia tiene nivel de confianza |
| 6ta — Modularidad | Todo módulo puede reemplazarse |

---

## Casos de uso

7 casos configurables vía YAML:

| Caso | Tick | Segmento |
|---|---|---|
| Compañía para personas solas | 10s | B2C wellness |
| Vigilancia cognitiva autónoma | 2s | B2B DevOps |
| Cuidado de personas mayores | 30s | B2C health |
| Investigación autónoma | 5s | B2B R&D |
| Federación B2B privada | 5s | B2B enterprise |
| Asistente que crece contigo | 5s | B2C premium |
| IA heredable | 5s | B2C legacy |

---

## Roadmap

| Fase | Estado | Entregable |
|---|---|---|
| 0 — Bucle cognitivo | ✅ | Observar-predecir-evaluar-decidir-actuar |
| 0.5 — Organismo cognitivo | ✅ | 6 leyes + 12 física + 6 campos + 5 tensiones |
| 1 — Alma + Cuerpo + Metabolismo | ✅ | Identity Vault + Trajectory Chain + 11 Memory Types |
| 2 — Mente completa | ✅ | 12 sub-agentes + Global Workspace + Meta-cog + Active Inference |
| 3 — Integración + Persistencia | ✅ | CognitiveLoopV3 + SQLite + MO V2 arquitectural |
| 4 — Federación + Deploy | ✅ | CognitiveLoopV4 + federación HTTP + quorum + 7 casos |
| 5 — ACD + Streaming | ✅ | CognitiveLoopV5 + DepthClassifier + Cache + Streaming |
| 6A — Epistemic Validation | ✅ | EpistemicValidator + Quarantine + CrossValidator + Federation |
| 6B — Capsules + Marketplace | ✅ | 12 cápsulas + Scaffold CLI + Marketplace + Dashboard UI |
| App móvil | 🟡 | PWA/React Native |
| Bot Telegram | 🟡 | Bot con mismo ZoeChat |

---

## Tests

```
775 tests, 100% pass
```

| Suite | Tests | Cobertura |
|---|---|---|
| Fase 0-0.5 (state, loop, laws, physics, fields, tensions, memory) | 149 | Núcleo cognitivo |
| Fase 1 (vault, trajectory, ontogenetic, metabolism, memory_types) | 191 | Alma + Cuerpo |
| Fase 2-3 (sub-agentes, workspace, meta-cog, V3, persistencia) | 159 | Mente + Integración |
| Fase 4 (federación, config, V4, casos de uso) | 69 | Federación + Deploy |
| Fase 5 — ACD + Streaming | 44 | DepthClassifier + Cache + V5 |
| Fase 6A — Epistemic Validation | 41 | Validator + Quarantine + CrossValidator |
| Fase 6B — Capsules + Marketplace | 138 | 12 cápsulas + Scaffold + Marketplace + Federation |
| **TOTAL** | **775** | **100% pass** |

---

## Documentación

- **[`zoe/docs/ZOE_V1_GUIDE.md`](zoe/docs/ZOE_V1_GUIDE.md)** — Guía completa (17 secciones + 2 anexos)
- **[`zoe/docs/ZOE_V1_AUDITORIA_Y_PRESENTACION.md`](zoe/docs/ZOE_V1_AUDITORIA_Y_PRESENTACION.md)** — Auditoría integral del proyecto
- **[`zoe/phases/`](zoe/phases/)** — Planes, resultados y análisis de cada fase
- **[`zoe/capsules/CAPSULE_MATRIX.md`](zoe/capsules/CAPSULE_MATRIX.md)** — Matriz de cápsulas

---

## Licencia

Apache 2.0 — [LICENSE](LICENSE)

---

*ZOE V1.2 — Synthetic Cognitive Organism (SCO).*
*Repositorio: `fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO`*
*775 tests · 12 cápsulas · 7 casos de uso · 6 fases completas*
