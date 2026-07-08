# ZOE — Synthetic Cognitive Organism

> **ZOE no es un LLM. No es un harness de agentes. No es una arquitectura de IA más.**
> **ZOE es el primer organismo cognitivo sintético (SCO):** un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, y evolución arquitectural firmada. Los LLMs son sus sentidos periféricos, no su cerebro.

[![Tests](https://img.shields.io/badge/tests-775%2F775%20pass-brightgreen)](#tests)
[![Phase](https://img.shields.io/badge/phase-6B%20Marketplace%20%2B%20Federation-blue)](#roadmap)
[![Interfaces](https://img.shields.io/badge/interfaces-CLI%20%2B%20Web%20Dashboard-orange)](#interfaces)
[![ACD](https://img.shields.io/badge/ACD-L0%2FL1%2FL2%2FL3-purple)](#adaptive-cognitive-depth-acd)
[![Capsules](https://img.shields.io/badge/capsules-12%20available-teal)](#cápsulas-de-conocimiento)
[![Marketplace](https://img.shields.io/badge/marketplace-open%20for%20authors-success)](#marketplace-de-cápsulas)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

---

## Tabla de contenidos

1. [Qué es ZOE](#qué-es-zoe)
2. [Interfaces](#interfaces)
3. [Adaptive Cognitive Depth (ACD)](#adaptive-cognitive-depth-acd)
4. [Cápsulas de conocimiento](#cápsulas-de-conocimiento)
5. [Validación epistémica (Fase 6A)](#validación-epistémica-fase-6a)
6. [Federación epistémica real (Punto 2)](#federación-epistémica-real-punto-2)
7. [Panel de cuarentena (Punto 3)](#panel-de-cuarentena-punto-3)
8. [Marketplace de cápsulas](#marketplace-de-cápsulas)
9. [Los 5 pilares](#los-5-pilares)
10. [Las 6 leyes cognitivas](#las-6-leyes-cognitivas)
11. [Física cognitiva (12 magnitudes)](#física-cognitiva)
12. [Arquitectura](#arquitectura)
13. [Quickstart](#quickstart)
14. [Casos de uso](#casos-de-uso)
15. [Roadmap](#roadmap)
16. [Tests](#tests)
17. [Comparativa](#comparativa)
18. [Documentación](#documentación)
19. [Licencia](#licencia)

---

## Qué es ZOE

ZOE (ζωή, griego: *vida plena*) es un **organismo cognitivo digital** que opera continuamente, incluso sin input externo. A diferencia de los LLMs convencionales (que esperan input para producir output), ZOE mantiene un bucle cognitivo perpetuo: observa, predice, evalúa sorpresa, decide, actúa, y aprende.

### Las 10 propiedades únicas simultáneas

Ningún competidor en el mercado tiene estas propiedades al mismo tiempo:

1. **Bucle cognitivo continuo** — piensa cuando nadie le habla (18 pasos por iteración)
2. **Encarnación digital real** — siente filesystem, red, tiempo, otros agentes
3. **Identidad criptográfica soberana** — portable entre LLMs/hardware/idiomas
4. **Metabolismo funcional** — fatiga, saturación, ciclos dormir/despertar
5. **Evolución arquitectural firmada** — mutaciones que crean/eliminan sub-agentes
6. **Memoria viva persistente** — 11 tipos, reorganización automática, SQLite
7. **Física cognitiva** — 12 magnitudes medibles que gobiernan el sistema
8. **Leyes cognitivas** — 6 leyes verificadas en cada acción
9. **Federación HTTP con quorum** — ≥70% aprobación + veto por valores
10. **2 interfaces funcionales** — CLI Chat + Web Dashboard en tiempo real

---

## Interfaces

ZOE tiene **dos interfaces** para comunicarse con ella, más dos planificadas:

### 1. CLI Chat (terminal)

```bash
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b
```

Chat interactivo en el terminal. Soporta comandos especiales (`/stats`, `/memory`, `/feed`, `/sleep`, `/wake`, `/identity`, `/quit`). Memoria persistente entre sesiones.

### 2. Web Dashboard (navegador)

```bash
python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b
```

Abre `http://localhost:8642` en el navegador. Tres paneles en tiempo real:

| Panel | Qué muestra |
|---|---|
| **Izquierdo** | Estado del organismo (energía, fatiga, tensiones, metabolismo) + acciones |
| **Central** | Chat en tiempo real (WebSocket) |
| **Derecho** | Pensamientos autónomos en vivo + federación |

**Características del dashboard:**
- Estado del organismo actualizado cada 2s vía WebSocket
- Pensamientos autónomos aparecen en vivo (incluso sin hablar)
- Selector de LLM en caliente (cambia sin reiniciar)
- Alimentación de documentos (file picker o drag & drop)
- Histórico de conversaciones
- Control de metabolismo (dormir/despertar)
- Panel de federación (peers, quorum)

### 3. App móvil (planificada)

Mismos endpoints HTTP/WS que el dashboard. React Native o PWA. Notificaciones push para pensamientos autónomos.

### 4. Bot Telegram (planificada)

Usa el mismo `ZoeChat` que el CLI. Comandos de Telegram mapeados a comandos de ZOE. Pensamientos autónomos enviados como mensajes proactivos.

---

## Adaptive Cognitive Depth (ACD)

> **Fase 5 — ACD + Streaming.** ZOE decide ANTES de entrar al bucle cuánta profundidad cognitiva necesita cada input. Inspirado en System 1/System 2 de Kahneman, pero aplicado ANTES del pipeline, no después.

### El problema que resuelve

Antes de Fase 5, ZOE ejecutaba siempre el bucle cognitivo completo (18 pasos, 12 sub-agentes, 6–10 llamadas LLM) para cualquier input —incluido "hola". Resultado: 8–15 segundos para responder a un saludo. El organismo "se perdía en sus pensamientos".

### La solución: 4 niveles cognitivos

| Nivel | Nombre | Input típico | Sub-agentes activos | Latencia objetivo | Coste (4ta ley) |
|---|---|---|---|---|---|
| **L0** | REFLEX | "hola", "ok", "gracias", "vale" | Ninguno (tabla refleja + cache) | **<1s** | 0.05 |
| **L1** | FAST | Pregunta factual, "¿cómo te llamas?" | Perceiver + Memorialist + Speaker | **2–4s** | 0.10 |
| **L2** | STANDARD | Conversación normal, opinión | Fase 0 completa (4 sub-agentes) | **6–10s** | 0.30 |
| **L3** | DEEP | Análisis causal, dilema ético, creatividad | Los 12 sub-agentes + meta-cog + workspace | **15–30s** | 0.60 |

### Cómo funciona

```python
from zoe.core.depth_classifier import DepthClassifier
from zoe.core.cognitive_cache import CognitiveCache
from zoe.core.cognitive_loop_v5 import CognitiveLoopV5

loop = CognitiveLoopV5(
    ...,
    depth_classifier=DepthClassifier(),
    cognitive_cache=CognitiveCache(max_size=100, ttl_seconds=300),
)

result = await loop.process_user_input_acd("hola")
# result = {
#   "response": "Hola. Estoy aquí.",
#   "level": "L0_REFLEX",
#   "latency_ms": 12.3,
#   "cache_hit": False,
#   "cost": 0.05,
#   "trajectory_hash": "abc123...",
# }
```

El `DepthClassifier` es **100% heurístico** (sin LLM, <50ms por clasificación). Combina:

1. **Tokens L0** — saludos/despedidas/acks
2. **Keywords L3** — `analiza`, `causas`, `dilema`, `ético`, `diseña`, `investiga`...
3. **Longitud** — más texto suele implicar más profundidad
4. **Estructura sintáctica** — condicional `si...entonces`, listas numeradas, multisentence
5. **Puntuación compleja** — múltiples `?`, `;`, multiline

### Streaming parcial

Para L1/L2/L3, el Speaker emite tokens en streaming real (vía Ollama NDJSON o OpenAI SSE):

```python
async for event in chat.send_message_streaming("analiza las causas de la inflación"):
    if event["type"] == "metadata":
        print(f"Nivel: {event['level']}")
    elif event["type"] == "chunk":
        print(event["content"], end="", flush=True)
    elif event["type"] == "done":
        print(f"\nRespuesta completa: {event['content']}")
```

### Auditoría: nivel ACD en trayectoria firmada

Cada respuesta queda firmada en la `TrajectoryChain` con su nivel cognitivo:

```python
mutation = ontogenetic_motor.propose_mutation(
    type="respond_to_user",
    target="speaker",
    payload={
        "user_input": "...",
        "response": "...",
        "acd_level": "L3_DEEP",  # ← auditable
        "score": 0.78,
    },
    provenance="acd:L3_DEEP",
    cost=0.60,  # ← 4ta ley
    confidence=0.55,  # ← 5ta ley
)
```

La cadena es verificable: `trajectory_chain.verify_chain()` confirma que ninguna respuesta fue alterada.

### Estadísticas ACD

```python
stats = loop.get_stats()
# stats["acd_classifications"] = 142
# stats["acd_level_counts"] = {"L0_REFLEX": 87, "L1_FAST": 31, "L2_STANDARD": 18, "L3_DEEP": 6}
# stats["acd_cache_hits"] = 23
# stats["acd_latency_by_level"] = {
#   "L0_REFLEX": {"avg_ms": 8.2, "p50_ms": 5.1, "max_ms": 18.7},
#   "L3_DEEP":   {"avg_ms": 18420, "p50_ms": 17200, "max_ms": 28500},
# }
```

### Backward compatibility

`CognitiveLoopV5` es subclase de `CognitiveLoopV4`. Si no se pasa `depth_classifier`, comportamiento = V4 (sin ACD). **Sin desconstruir nada.**

---

## Cápsulas de conocimiento

> **Fase 6B + 6A V1.2.** ZOE no nace como "niño brillante sin cultura". Carga cápsulas de conocimiento profesional previo junto al YAML del caso de uso, gestionables desde el Dashboard en tiempo real.

### Las 12 cápsulas disponibles

| Cápsula | Dominio | Trust | Entries | Casos de uso |
|---|---|---|---|---|
| `elder_care_knowledge` | healthcare.elders.home_care | verified | 54 | cuidado_personas_mayores, compania_personas_solas |
| `elder_care_skills` | healthcare.elders.tools | verified | 4 tools + 2 prompts | cuidado_personas_mayores |
| `basic_psychology` | psychology.general | curated | 49 | todos los casos B2C |
| `communication_skills` | communication.empathy | curated | 37 | todos los casos B2C |
| `company_loneliness_knowledge` | psychology.loneliness.grief | verified | 50 | compania_personas_solas |
| `vigilance_devops_knowledge` | tech.devops.monitoring | curated | 46 | vigilancia_cognitiva |
| `research_methodology` | science.methodology | verified | 45 | investigacion_autonoma |
| `federation_b2b_skills` | tech.federation.b2b | verified | 11 + tools | federacion_b2b |
| `b2c_assistant_growth` | b2c.user_modeling | curated | 31 | asistente_crece_contigo |
| `pharmacy_interactions` | healthcare.pharmacology | verified | 34 | cuidado_personas_mayores, federacion_b2b |
| `ia_heredable_legal` | legal.digital_inheritance | curated | 25 | ia_heredable |
| `base_ethics` | ethics.general | verified | 34 | todos |

**Total**: 12 cápsulas, ~500 entries de conocimiento verificado, 7 verified + 5 curated.

### Componentes de una cápsula

Una cápsula puede incluir:

- `semantic_memory.jsonl` — hechos para memoria semántica
- `procedural_skills.jsonl` — habilidades con pasos
- `causal_models.jsonl` — modelos causa-efecto para CausalEngine
- `emotional_patterns.jsonl` — patrones para EmotionalMotor
- `ethical_guidelines.jsonl` — directrices para EthicalMotor
- `validators.py` — validadores de código específicos del dominio
- `tools/*.py` — herramientas ejecutables
- `prompts/*.md` — system prompts específicos

### CLI Scaffold

```bash
# Crear nueva cápsula
python -m zoe.capsules.scaffold create \
    --name my_capsule --domain "my.domain" --trust-level curated \
    --description "..." --components semantic,validators

# Validar cápsula existente
python -m zoe.capsules.scaffold validate --name X

# Calcular hash de contenido
python -m zoe.capsules.scaffold hash --name X

# Listar cápsulas disponibles
python -m zoe.capsules.scaffold list

# Ver matriz completa
python -m zoe.capsules.scaffold matrix

# Info detallada
python -m zoe.capsules.scaffold info --name X
```

### Carga en runtime

Las cápsulas se cargan automáticamente al iniciar ZOE según el caso de uso, y pueden cargarse/descargarse en caliente desde:

- **CLI**: comandos `/capsules`, `/capsule <nombre>`, `/uncapsule <nombre>`
- **Web Dashboard**: botón "📦 Cápsulas" → modal con lista, cargar/descargar, validar, crear nueva
- **WebSocket**: evento `capsule_action` con `load`/`unload`/`list` broadcasts a todos los clientes conectados
- **REST API**: endpoints `/api/capsules`, `/api/capsules/load`, `/api/capsules/unload`, `/api/capsules/{name}/info`, `/api/capsules/{name}/validate`, `/api/capsules/create`

Cada carga/descarga se firma criptográficamente en la TrajectoryChain (`capsule_loaded`/`capsule_unloaded`).

---

## Validación epistémica (Fase 6A)

> **ZOE regula cómo adquiere, valida y consolida conocimiento nuevo.** Las 4 opciones de Fase 6A cierran el problema del "niño brillante sin cultura".

### Opción 1 — EpistemicValidator

Valida todo conocimiento nuevo antes de entrar a memoria.

- **Política SOURCE_TRUST**: 14+ fuentes categorizadas (capsule:verified=0.95, llm:gpt-4o=0.50, scientific:pubmed=0.95, web:general=0.30, etc.)
- **Dominios sensibles**: medical, psychological, legal, safety, financial requieren triple verificación obligatoria
- **Cap de confianza**: auto-aprendido max 0.50, triple-verificado max 0.75, federativo max 0.85, cápsula verified max 0.95
- **Rechazo automático** de claims que contradicen conocimiento verificado

### Opción 2 — KnowledgeQuarantine

Cuarentena activa: el conocimiento no validado no se usa para decisiones críticas.

- `filter_safe(entries, critical_context=True)` elimina cuarentena de contextos críticos
- Plan de verificación con timeout (default 30 días, luego poda)
- `verify()` acumula confirmaciones, `promote()` al alcanzar umbral, `reject()` con contradicciones

### Opción 3 — CrossValidator

Triple verificación multi-fuente.

- Consulta 3 fuentes (LLM-A + LLM-B + cápsula o tercera fuente)
- 3/3 coinciden → confianza 0.75, sale de cuarentena
- 2/3 coinciden → confianza 0.65 o 0.80 si cápsula en mayoría
- Divergencia total → rechazo
- Similitud léxica Jaccard para comparar respuestas

### Opción 4 — EpistemicFederation

Revisión por pares científica entre ZOEs.

- `knowledge_validation_request` enviado a peers
- Peers responden: `confirmed` | `contradicted` | `unknown`
- ≥2 confirmaciones → confianza sube a 0.85, sale de cuarentena
- ≥1 contradicción → rechazo, requiere validación científica externa
- Cada ZOE indexa su conocimiento local para responder a requests de otras

### Integración con Learner

El `Learner` pasa todo conocimiento nuevo por `EpistemicValidator` antes de proponerlo. Si la validación devuelve:

- `ACCEPTED` → mutación normal
- `ACCEPTED_WITH_QUARANTINE` → mutación con `metadata.quarantine=True` (Curator/Critic la filtran en contextos críticos)
- `REJECTED` → no se propone la mutación, se registra rechazo
- `NEEDS_TRIPLE_VALIDATION` → cuarentena hasta triple verificación

### Integración con Curator, DeepConsolidation y Critic

El `CapsuleManager` inyecta `KnowledgeQuarantine` automáticamente en los componentes de consolidación y validación al cargar la primera cápsula:

**Curator** — `get_safe_entries(critical_context=True)`
- En contextos críticos (medico, psicológico, etc.), filtra las entries en cuarentena
- `curate()` ejecuta `cleanup_expired()` del quarantine y poda las entries expiradas de memoria
- Stats: `quarantine_filtered`, `quarantine_active`, `quarantine_stats`

**DeepConsolidation** — durante SLEEPING
- `_episodic_to_semantic()` NO promueve entries en cuarentena (no validadas) a semántica
- `_reinforce_beliefs()` NO refuerza entries en cuarentena (no ganan confianza durante el sueño)
- `_deep_forget()` poda entries de cuarentena expiradas + limpia referencias
- `consolidate()` incluye `quarantine_stats` en el resultado

**Critic** — `evaluate(thought, context)`
- Si `context.critical_context=True` o detecta dominio sensible (médico, psicológico, legal, safety), verifica `used_memory_ids`
- Si alguna entry usada está en cuarentena → rechazo automático (`quarantine_violation`)
- En contexto NO crítico (brainstorming, exploración), aprueba uso de cuarentena
- Stats: `quarantine_checks`, `quarantine_rejections`

---

## Federación epistémica real (Punto 2)

> **ZOE valida conocimiento consultando a otras ZOEs vía HTTP.** Revisión por pares científica aplicada a organismos cognitivos.

### Componentes

- `zoe/core/epistemic_federation_server.py` — `EpistemicFederationServer` (recibe requests de peers) + `EpistemicFederationClient` (envía requests a peers)
- Integración con `Web Dashboard` (rutas `/federation/epistemic/*`)
- Integración con `KnowledgeQuarantine` (promote/reject automático al recibir confirmaciones)

### Endpoints HTTP

| Endpoint | Método | Descripción |
|---|---|---|
| `/federation/epistemic/validate` | POST | Recibe knowledge_validation_request de peer |
| `/federation/epistemic/knowledge/{claim_hash}` | GET | Consulta si tenemos un claim indexado |
| `/federation/epistemic/register` | POST | Registra peer |
| `/federation/epistemic/peers` | GET | Lista peers registrados |
| `/federation/epistemic/stats` | GET | Stats de federación epistémica |
| `/federation/epistemic/request_validation` | POST | Envía validation request a todos los peers |

### Protocolo

```
1. ZOE-A valida localmente un claim (con CrossValidator o EpistemicValidator)
2. ZOE-A envía knowledge_validation_request a N peers vía HTTP POST
3. Cada peer responde: confirmed | contradicted | unknown
4. Si ≥2 peers confirman → confianza sube a 0.85, sale de cuarentena
5. Si algún peer contradice → rechazo, requiere validación científica externa
6. Si no hay quorum → queda pending (pendiente de más respuestas)
```

### Cómo configurar federación

```python
from zoe.core.epistemic_federation import EpistemicFederation
from zoe.core.epistemic_federation_server import EpistemicFederationClient

fed = EpistemicFederation(organism_id="zoe_1")
client = EpistemicFederationClient(fed, quarantine=q, validator=v)
client.add_peer("zoe_2", "http://zoe-2.local:8642")
client.add_peer("zoe_3", "http://zoe-3.local:8642")

# Enviar validation request a peers
result = await client.request_validation_from_peers(
    claim="Las benzodiacepinas son seguras en mayores.",
    source="llm:gpt-4o",
    domain="medical",
    confidence_local=0.5,
    quarantine_entry_id="q_abc123",
)
# result = {final_status: "promoted", confirmations: 2, ...}
```

---

## Panel de cuarentena (Punto 3)

> **Gestión visual del conocimiento en cuarentena desde el Dashboard.** Permite ver entries activas, promover, rechazar y ver stats.

### Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/quarantine` | GET | Lista entries activas y pendientes |
| `/api/quarantine/stats` | GET | Stats de cuarentena (active, verified, rejected, expired) |
| `/api/quarantine/{entry_id}/promote` | POST | Promueve entrada manualmente |
| `/api/quarantine/{entry_id}/reject` | POST | Rechaza entrada manualmente |

### UI en Dashboard

Botón **"🔒 Cuarentena"** en panel de acciones → modal con:
- **Stats**: total, activas, verificadas, rechazadas, expiradas (con colores)
- **Entradas Activas**: lista con claim, dominio, source, confianza, razón, confirmaciones y contradicciones. Botones **✓ Promover** y **✗ Rechazar** en cada entry
- **Pendientes**: count de entries que aún no tienen suficientes verificaciones

### Integración con componentes

El `CapsuleManager` inyecta `KnowledgeQuarantine` automáticamente en:

- **Curator**: `get_safe_entries(critical_context=True)` filtra cuarentena; `curate()` limpia expiradas
- **DeepConsolidation**: `_episodic_to_semantic()` no promueve cuarentena; `_reinforce_beliefs()` no refuerza; `_deep_forget()` poda expiradas
- **Critic**: `evaluate(thought, context)` rechaza respuestas que usen cuarentena en dominios sensibles
- **Learner**: `propose_learning()` pasa todo conocimiento nuevo por `EpistemicValidator` antes de proponerlo

---

## Marketplace de cápsulas

> **Cualquiera puede aportar y monetizar cápsulas de conocimiento y casos de uso YAML nuevos.** ZOE se convierte en plataforma, no solo en producto.

### Modelo

1. **Autores crean** cápsulas/casos con `scaffold CLI`
2. **Suben al marketplace** (local o remoto) con licencia (free, paid, subscription, opensource, research)
3. **Otros usuarios descubren, descargan e instalan**
4. **Sistema de monetización** con licencias verificables

### Componentes

- `zoe/marketplace/core.py`:
  - `MarketplaceCatalog` — catálogo local/remote de cápsulas y casos disponibles
  - `MarketplaceEntry` — entrada con metadata, licencia, downloads, rating
  - `CapsuleLicense` — licencia de uso (free, paid, subscription, opensource, research)
  - `CapsulePackager` — empaqueta/desempaqueta en `.zcap` (cápsulas) y `.zyaml` (casos)
  - `MarketplaceUploader` — sube cápsulas y casos al marketplace
  - `MarketplaceDownloader` — descarga e instala
  - `LicenseChecker` — verifica licencias

### Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Lista cápsulas disponibles |
| `/api/marketplace/upload` | POST | Sube cápsula al marketplace |
| `/api/marketplace/download/{name}` | POST | Descarga e instala cápsula |
| `/api/marketplace/use_cases` | GET | Lista casos de uso disponibles |
| `/api/marketplace/upload_use_case` | POST | Sube caso de uso al marketplace |

### UI en Dashboard

Botón **"🏪 Marketplace"** en panel de acciones → modal con:
- **Stats**: total, cápsulas, casos, downloads totales
- **Cápsulas Disponibles**: tabla con nombre, versión, licencia (badge color), precio, autor, downloads, rating, tags. Botón **⬇ Instalar** en cada una
- **Casos de Uso Disponibles**: lista similar
- **Subir Cápsula**: formulario con nombre, autor, licencia (free/opensource/research/paid/subscription), precio, tags, descripción
- **Subir Caso de Uso**: formulario similar

### Licencias

| Tipo | Uso comercial | Pago | Descripción |
|---|---|---|---|
| `free` | Sí | No | Uso libre, sin restricciones |
| `opensource` | Sí | No | Tipo open source, atribución requerida |
| `research` | No | No | Solo investigación, no comercial |
| `paid` | Sí | Sí (precio único) | Pago único para uso |
| `subscription` | Sí | Sí (mensual/anual) | Suscripción periódica |

### Cómo subir una cápsula al marketplace

```bash
# 1. Crear cápsula con scaffold
python -m zoe.capsules.scaffold create --name my_capsule --domain "my.domain" \
    --trust-level curated --description "..." --components semantic,validators

# 2. Editar contenido (semantic_memory.jsonl, validators.py, etc.)

# 3. Validar
python -m zoe.capsules.scaffold validate --name my_capsule

# 4. Subir al marketplace (vía Dashboard o API)
curl -X POST http://localhost:8642/api/marketplace/upload \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "my_capsule",
        "author": "my_name",
        "description": "...",
        "license": {"type": "paid", "price": 19.99, "currency": "EUR"},
        "tags": ["domain1", "domain2"]
    }'
```

### Cómo descargar e instalar

```bash
curl -X POST http://localhost:8642/api/marketplace/download/my_capsule
```

### Cómo subir un caso de uso YAML

```bash
curl -X POST http://localhost:8642/api/marketplace/upload_use_case \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "my_use_case",
        "author": "my_name",
        "description": "...",
        "license": {"type": "free"},
        "tags": ["wellness"]
    }'
```

### Cómo se integran los YAML y las cápsulas en los nuevos procesos

#### YAML de caso de uso

El YAML define qué cápsulas se cargan al iniciar ZOE:

```yaml
use_case:
  name: "mi_caso_personalizado"
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

Al ejecutar `python -m zoe.use_cases.run_use_case --use-case mi_caso_personalizado`:
1. El runner carga el YAML
2. `CapsuleManager.load_for_use_case()` carga las cápsulas `required` (falla si no encuentra)
3. Carga las `recommended` si existen
4. Carga las `optional` si existen y no hay conflicto
5. Cada cápsula se inyecta en memoria, CausalEngine, EmotionalMotor, EthicalMotor
6. Se firman mutaciones `capsule_loaded` en la trayectoria

#### Cápsulas en runtime

Las cápsulas pueden cargarse/descargarse en caliente desde:
- **CLI**: `/capsule <nombre>`, `/uncapsule <nombre>`, `/capsules`
- **Dashboard**: botón "Cápsulas" → modal con cargar/descargar/validar/crear
- **WebSocket**: evento `capsule_action` broadcasts a todos los clientes
- **REST API**: `/api/capsules/load`, `/api/capsules/unload`

#### Marketplace en runtime

Las cápsulas descargadas del marketplace se instalan automáticamente en `zoe/capsules/` y quedan disponibles para carga inmediata.

---

## Los 5 pilares

```
┌───────────────────────────────────────────────────┐
│  ZOE (Synthetic Cognitive Organism)               │
│                                                   │
│  1. ALMA (inmutable, soberana)                    │
│     • Identity Vault (hash SHA-256 de 9V+7V)     │
│     • Trajectory Chain (cadena firmada)           │
│     • Ontogenetic Motor V2 (arquitectural)        │
│     • Phylogenetic Motor (evolución de especie)   │
│                                                   │
│  2. MENTE (ecología cognitiva)                    │
│     • Cognitive Loop V4 (18 pasos/iteración)      │
│     • Global Workspace (Baars — competición)      │
│     • World Model V2 (n-gram/sentence-transform)  │
│     • Active Inference (Free Energy Principle)    │
│     • Meta-Cognition (System 1/2 — Kahneman)     │
│     • Society of Mind (12 sub-agentes)            │
│                                                   │
│  3. METABOLISMO (presupuesto, fatiga)             │
│     • Estados: awake→drowsy→sleeping→waking      │
│     • Presupuesto de cómputo                      │
│     • Consolidación profunda en sueño (7 ops)     │
│                                                   │
│  4. CUERPO (encarnación digital)                  │
│     • 5 sentidos (Clock, FS, User, Network, Agent)│
│     • 4 actuadores (Language, Code, Tool, Fed)    │
│     • LLMs como periféricos (4 backends)          │
│                                                   │
│  5. EVOLUCIÓN                                     │
│     • Motor Ontogenético V2 (crear/eliminar mods) │
│     • Motor Filogenético (especie)                │
│     • 11 tipos de memoria viva + persistencia     │
│     • Deep Consolidation (7 operaciones en sueño) │
└───────────────────────────────────────────────────┘
```

---

## Las 6 leyes cognitivas

ZOE no se define por componentes. Se define por leyes, como la biología no define un ser vivo por sus órganos, sino por homeostasis, evolución, metabolismo, adaptación, autopoiesis.

| Ley | Principio |
|---|---|
| **1ra — Utilidad** | Toda acción reduce incertidumbre o aumenta capacidad. No hay acciones gratuitas. |
| **2da — Identidad** | Toda modificación preserva identidad. |
| **3ra — Proveniencia** | Todo conocimiento justifica su origen. No hay memoria "mágica". |
| **4ta — Coste** | Todo proceso consume recursos. Nadie piensa gratis. |
| **5ta — Confianza** | Toda creencia tiene nivel de confianza. No hay verdades absolutas. |
| **6ta — Modularidad** | Todo módulo puede reemplazarse sin romper identidad. |

Cada acción del bucle cognitivo pasa por `verify_action()` antes de ejecutarse.

---

## Física cognitiva

ZOE es un sistema dinámico gobernado por 12 magnitudes cuantificables:

| Magnitud | Símbolo | Descripción |
|---|---|---|
| Energía cognitiva | `eCog` | Presupuesto de cómputo disponible |
| Masa conceptual | `mCon` | Conexiones de un concepto en memoria |
| Temperatura cognitiva | `tCog` | Actividad del bucle (iter/s) |
| Presión de incertidumbre | `pUnc` | Sorpresa acumulada no resuelta |
| Potencial creativo | `pCre` | Diversidad de hipótesis |
| Entropía semántica | `hSem` | Diversidad de conceptos activos |
| Gravedad de objetivos | `gObj` | Atracción de intenciones |
| Inercia de identidad | `iIden` | Resistencia al cambio |
| Resonancia conceptual | `rCon` | Similitud entre conceptos |
| Fricción cognitiva | `fCog` | Coste de cambiar contexto |
| Elasticidad de memoria | `eMem` | Capacidad de reorganización |
| Densidad causal | `dCau` | Concentración de relaciones causales |

---

## Arquitectura

```
zoe/
├── core/                          # MENTE
│   ├── cognitive_loop.py          # Bucle Fase 0
│   ├── cognitive_loop_v05.py      # Bcle Fase 0.5
│   ├── cognitive_loop_v3.py       # Bucle Fase 3 (18 pasos)
│   ├── cognitive_loop_v4.py       # Bucle Fase 4 (+ consolidación + auto-save)
│   ├── cognitive_laws.py          # 6 leyes cognitivas
│   ├── cognitive_physics.py       # 12 magnitudes
│   ├── cognitive_fields.py        # 6 campos compartidos
│   ├── cognitive_tensions.py      # 5 tensiones permanentes
│   ├── living_memory.py           # Memoria que piensa
│   ├── intentionality_motor.py    # Generador de intenciones
│   ├── phylogenetic_motor.py      # Evolución de especie
│   ├── federation.py              # Federación HTTP + quorum
│   ├── world_model.py             # Predictor V1
│   ├── world_model_v2.py          # Predictor V2 (n-gram/ST)
│   ├── active_inference.py        # Free Energy Principle
│   ├── meta_cognition.py          # System 1/2 (Kahneman)
│   ├── global_workspace.py        # Ecología de procesos (Baars)
│   ├── state.py                   # Homeostasis básica
│   └── subagents/                 # Society of Mind (12 sub-agentes)
├── alma/                          # ALMA
│   ├── identity_vault.py          # Hash criptográfico 9V+7V
│   ├── trajectory_chain.py        # Cadena firmada de mutaciones
│   ├── ontogenetic_motor.py       # V1: mutaciones de memoria
│   └── ontogenetic_motor_v2.py    # V2: mutaciones arquitecturales
├── metabolism/                    # METABOLISMO
│   └── metabolism.py              # AWAKE/DROWSY/SLEEPING/WAKING
├── memory/                        # 11 MEMORY TYPES + PERSISTENCIA
│   ├── memory_types.py            # Episodic, Semantic, Procedural, ...
│   ├── persistent_store.py        # SQLite backing store
│   └── deep_consolidation.py      # Consolidación profunda (7 ops)
├── peripherals/                   # CUERPO
│   ├── llm.py                     # 4 backends: Mock, ZAI, Ollama, OpenAI
│   ├── senses.py                  # Clock, Filesystem, UserInput, Network, Agent
│   └── actuators.py               # Language, Code, Tool, Federation, Manager
├── use_cases/                     # 7 CASOS DE USO
│   ├── run_use_case.py            # Runner
│   ├── compania_personas_solas.yaml
│   ├── vigilancia_cognitiva.yaml
│   ├── cuidado_personas_mayores.yaml
│   ├── investigacion_autonoma.yaml
│   ├── federacion_b2b.yaml
│   ├── asistente_crece_contigo.yaml
│   └── ia_heredable.yaml
├── config/                        # Configuración
│   ├── production.yaml
│   └── development.yaml
├── scripts/                       # Deploy
│   └── deploy.sh
├── examples/                      # Demos
│   ├── demo_phase0.py
│   ├── demo_phase0_5.py
│   ├── demo_integrated.py
│   └── demo_phase1.py
├── docs/                          # Guía completa
│   └── ZOE_V1_GUIDE.md
├── phases/                        # Planes, resultados y análisis
├── tests/                         # 534 tests
├── cli_chat.py                    # CLI Chat interface
├── web_dashboard.py               # Web Dashboard interface
├── serve.py                       # Punto de entrada producción
└── README.md                      # Este archivo
```

---

## Quickstart

### Instalación

```bash
git clone -b zoe-v1-sco https://github.com/fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2.git
cd CFI-Cognitive-Fractal-Intelligence-V2
pip install -r zoe/requirements.txt
```

### Tests

```bash
# Todos los tests (534)
python -m pytest zoe/tests/ -v

# Solo dashboard
python -m pytest zoe/tests/test_web_dashboard.py -v
```

### Hablar con ZOE — CLI Chat

```bash
# Con Mock (probar rápido)
python -m zoe.cli_chat --backend mock

# Con Ollama (producción)
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b

# Con ZAI (GLM-4)
python -m zoe.cli_chat --backend zai

# Con caso de uso
python -m zoe.cli_chat --use-case compania_personas_solas --backend ollama --model qwen2.5:3b
```

Comandos dentro del chat: `/stats`, `/memory`, `/state`, `/identity`, `/sleep`, `/wake`, `/feed <archivo>`, `/quit`

### Hablar con ZOE — Web Dashboard

```bash
# Iniciar dashboard
python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b

# Abrir navegador en
http://localhost:8642
```

El dashboard muestra: chat en tiempo real, estado del organismo en vivo, pensamientos autónomos, selector de LLM, alimentación de documentos, historial, federación.

### Alimentar a ZOE con información

**Desde CLI:**
```bash
/feed mis_notas.txt
```

**Desde Dashboard:**
- Botón 📂 Alimentar (file picker)
- Arrastrar y soltar archivo en el chat

ZOE almacena documentos en memoria semántica, los firma en Trajectory Chain, y los recuerda en futuras sesiones (persistencia SQLite).

### Ejecutar casos de uso

```bash
# Listar disponibles
python -m zoe.use_cases.run_use_case --list

# Ejecutar
python -m zoe.use_cases.run_use_case --use-case compania_personas_solas --backend mock
python -m zoe.use_cases.run_use_case --use-case vigilancia_cognitiva --backend ollama
```

### Configurar LLM periférico

ZOE es agnóstica al LLM. Cualquiera funciona como sentido periférico:

```python
from zoe.peripherals.llm import create_llm_peripheral

llm = create_llm_peripheral({"backend": "ollama", "model": "qwen2.5:3b"})
llm = create_llm_peripheral({"backend": "openai_compatible", "model": "gpt-4o-mini"})
llm = create_llm_peripheral({"backend": "mock"})
```

En el Web Dashboard, puedes cambiar el LLM en caliente sin reiniciar.

---

## Casos de uso

ZOE soporta 7 casos de uso configurables vía YAML en `zoe/use_cases/`:

| Caso de uso | YAML | Descripción | Tick |
|---|---|---|---|
| Compañía para personas solas | `compania_personas_solas.yaml` | Toma iniciativa, detecta emociones | 10s |
| Vigilancia cognitiva autónoma | `vigilancia_cognitiva.yaml` | Monitorea sistemas, investiga anomalías | 2s |
| Cuidado de personas mayores | `cuidado_personas_mayores.yaml` | Detecta cambios en rutina | 30s |
| Investigación autónoma | `investigacion_autonoma.yaml` | Persigue hipótesis, diseña experimentos | 5s |
| Federación privada B2B | `federacion_b2b.yaml` | Comparte aprendizajes sin compartir datos | 5s |
| Asistente que crece contigo | `asistente_crece_contigo.yaml` | Acumula modelo del usuario durante años | 5s |
| IA heredable | `ia_heredable.yaml` | Trayectoria firmada transferible | 5s |

---

## Roadmap

| Fase | Semanas | Estado | Entregable |
|---|---|---|---|
| **0** — Bucle cognitivo | 1-2 | ✅ Completa | Bucle observar-predecir-evaluar-decidir-actuar |
| **0.5** — Organismo cognitivo | 1-2 | ✅ Completa | 6 leyes + 12 física + 6 campos + 5 tensiones + memoria viva |
| **1** — Alma + Cuerpo + Metabolismo | 3-6 | ✅ Completa | Identity Vault + Trajectory Chain + Metabolism + 11 Memory Types + Actuadores |
| **2** — Mente completa | 7-10 | ✅ Completa | World Model V2 + Active Inference + 12 sub-agentes + System 1/2 + Global Workspace |
| **3** — Integración + Persistencia | 11-14 | ✅ Completa | CognitiveLoopV3 + persistencia SQLite + MO V2 arquitectural + consolidación profunda |
| **4** — Federación + Deploy | 15-18 | ✅ Completa | CognitiveLoopV4 + federación HTTP + quorum + deploy VPS + config YAML + 7 casos de uso |
| **5** — ACD + Streaming | 19-20 | ✅ Completa | CognitiveLoopV5 + DepthClassifier + Cache + Streaming + Trajectory ACD |
| **6A** — Epistemic Validation | — | ✅ Completa | EpistemicValidator + Quarantine + CrossValidator + Federation + Learner integration |
| **6B** — Marketplace + Federation | — | ✅ Completa | Marketplace cápsulas+YAML, federación epistémica HTTP, cuarentena Dashboard |
| **Interfaces** | — | ✅ Completa | CLI Chat + Web Dashboard (WebSocket, tiempo real, ACD, Capsules) |
| **App móvil** | — | 🟡 Planificada | PWA/React Native con mismos endpoints |
| **Bot Telegram** | — | 🟡 Planificada | Bot con mismo ZoeChat |

---

## Tests

```
775 passed (534 previos + 44 Fase 5 + 52 Fase 6B + 41 Fase 6A + 49 V1.2 + 19 Curator integration + 36 Marketplace+Federation+Quarantine)
```

| Suite | Tests | Cobertura |
|---|---|---|
| Fase 0 (state, loop, world_model, subagents, llm, senses) | 63 | Núcleo cognitivo |
| Fase 0.5 (laws, physics, fields, tensions, memory, intentionality, phylogenetic) | 86 | Organismo cognitivo |
| Integración Fase 0+0.5 | 27 | Coherencia end-to-end |
| Fase 1.1-1.4 (vault, trajectory, ontogenetic, metabolism, memory_types) | 75 | Alma + Metabolismo |
| Fase 1.5 (actuators, senses) | 38 | Cuerpo completo |
| Fase 1.6 (integración) | 16 | Organismo Fase 1 completo |
| Fase 2 (world_model_v2, active_inference, sub-agentes, meta-cog, workspace) | 42 | Mente completa |
| Integración completa 0+0.5+1+2 | 51 | Sistema completo end-to-end |
| Fase 3 (CognitiveLoopV3) | 20 | Bucle integrado |
| Fase 3.4-3.5 (persistencia, MO V2, consolidación) | 29 | Persistencia + arquitectura |
| Integración Fase 3 | 17 | Organismo Fase 3 completo |
| Fase 4 (config, federación, V4) | 29 | Federación + deploy |
| Casos de uso (7 YAML + runner + tests) | 20 | 7 casos de uso validados |
| CLI Chat | 9 | Interfaz CLI |
| Web Dashboard | 12 | Interfaz web |
| Fase 5 — ACD + Streaming | 44 | DepthClassifier + Cache + V5 + Streaming + Trayectoria ACD |
| Fase 6B — Capsules System | 52 | Schema + Loader + Registry + Scaffold + 3 cápsulas iniciales |
| Fase 6A — Epistemic Validation | 41 | EpistemicValidator + Quarantine + CrossValidator + Federation |
| Fase 6A V1.2 — 9 cápsulas + integración | 49 | 9 nuevas cápsulas + Learner integration + Dashboard endpoints |
| Fase 6A Punto 3 — Curator+Quarantine | 19 | Curator filter_safe + DeepConsolidation skip cuarentena + Critic reject cuarentena crítica |
| Fase 6B Marketplace + Federation + Quarantine | 36 | Marketplace (catalog, upload, download, license) + Federation server/client + Quarantine endpoints |
| **TOTAL** | **775** | **100% pass** |

---

## Comparativa

| Dimensión | LLM (GPT-4) | Harness (Hermes) | **ZOE** |
|---|---|---|---|
| Cuando no hay input | Apagado | Apagado | **Pensando (bucle continuo, 18 pasos)** |
| Identidad | Ninguna | soul.md (editable) | **Vault criptográfico (inmutable)** |
| Memoria | Contexto de sesión | Vector DB | **11 tipos + memoria viva + persistencia SQLite** |
| Aprendizaje | Reentrenamiento | Reescribir prompt | **Mutaciones firmadas (memoria + arquitectura)** |
| Evolución | Versiones nuevas | Sin evolución | **MO V2 arquitectural + MO filogenético** |
| Metabolismo | No | No | **AWAKE/DROWSY/SLEEPING/WAKING + consolidación profunda** |
| Transparencia | Caja negra | Logs en texto | **Trayectoria criptográfica + 6 leyes verificadas** |
| LLM | Es el cerebro | Es el cerebro | **Es un sentido periférico (4 backends, intercambiable en caliente)** |
| Federación | No | No | **Quorum con veto por valores** |
| Física cognitiva | No | No | **12 magnitudes medibles** |
| Decisiones | Forward pass | Tool calls | **Global Workspace (Baars) + System 1/2** |
| Interfaces | API | Framework | **CLI + Web Dashboard + (móvil + Telegram planificados)** |

---

## Documentación

### Guía completa

**[`docs/ZOE_V1_GUIDE.md`](docs/ZOE_V1_GUIDE.md)** — Guía completa de ZOE V1 (17 secciones + anexo de interfaces)

### Documentación del proyecto ZOE (`docs/ZOE/`)

| Doc | Título |
|---|---|
| 00-14 | Tesis, ejecución, auditorías, análisis, planes y hoja de ruta |

### Documentación de fases (`zoe/phases/`)

| Doc | Contenido |
|---|---|
| `PHASE_0_PLAN.md` → `PHASE_4_ANALYSIS.md` | Planes, resultados y análisis de cada fase |
| `EVOLUTION_PHASES_0_TO_2.md` | Trazabilidad completa de evolución |

---

## Licencia

Apache 2.0

---

*ZOE V1.2 — Synthetic Cognitive Organism (SCO). Proyecto independiente.*
*Repositorio: `fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO`*
*775 tests · 12 cápsulas · 7 casos de uso · 5 fases completas + Fase 6 (Epistemic + Marketplace)*
