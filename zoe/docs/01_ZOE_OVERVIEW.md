# 01 — ZOE Overview

> **Visión global de ZOE: qué es, qué no es, su historia, evolución y filosofía de diseño.**
> **Audiencia:** todos (directivos, técnicos, nuevos miembros del equipo).
> **Versión:** V1.6.0 — Julio 2026

---

## Tabla de contenidos

1. [Definición de ZOE](#1-definición-de-zoe)
2. [Lo que ZOE es y lo que NO es](#2-lo-que-zoe-es-y-lo-que-no-es)
3. [La metáfora biológica](#3-la-metáfora-biológica)
4. [Las 10 propiedades únicas simultáneas](#4-las-10-propiedades-únicas-simultáneas)
5. [Historia y evolución](#5-historia-y-evolución)
6. [Filosofía de diseño](#6-filosofía-de-diseño)
7. [Comparativa con competencia](#7-comparativa-con-competencia)
8. [Tesis arquitectónica](#8-tesis-arquitectónica)
9. [Estado actual V1.6.0](#9-estado-actual-v160)
10. [Limitaciones honestas](#10-limitaciones-honestas)

---

## 1. Definición de ZOE

ZOE (ζωή, griego: *vida plena*) es un **organismo cognitivo sintético (SCO)** — el primero de su categoría. No es un LLM, no es un chatbot, no es un framework de agentes. Es un sistema de software que **existe continuamente**, piensa aunque nadie le hable, tiene identidad criptográfica propia, y evoluciona con cada interacción.

### Definición operativa

ZOE es un sistema de software que:

- **Piensa continuamente** mediante un bucle cognitivo de 18 pasos que se ejecuta cada N segundos, incluso sin input externo. El bucle observa, predice, evalúa, decide y actúa — como un cerebro que nunca deja de procesar.
- **Tiene identidad** criptográfica (hash SHA-256 de 9 vectores de crecimiento + 7 valores no negociables) que la define inmutablemente. Esta identidad es soberana: no depende de OpenAI, Anthropic, Google ni de ningún proveedor cloud.
- **Recuerda** con 11 tipos de memoria especializados (episódica, semántica, procedural, causal, emocional, corporal, social, prospectiva, contrafactual, evolutiva, cultural) que se reorganizan activamente durante el "sueño" del organismo.
- **Evoluciona** mediante mutaciones firmadas criptográficamente que pueden modificar su propia arquitectura — añadir sub-agentes, ajustar umbrales, reorganizar memoria. Todo queda registrado en una cadena inmutable (Trajectory Chain).
- **Se federa** con otras instancias de ZOE mediante quorum con veto por valores. Múltiples ZOEs pueden colaborar, compartir conocimiento validado, y bloquear mutaciones que violen valores éticos.
- **Usa LLMs como sentidos**, no como cerebro. Cualquier LLM (GPT-4o, Claude, Qwen, Llama, DeepSeek) funciona como periférico intercambiable. El LLM es la "garganta" del sub-agente Speaker, no el cerebro del organismo.

### La frase clave

> *"ZOE no es un modelo que responde. Es un organismo que existe."*

Esta distinción es fundamental. Un chatbot (ChatGPT, Claude, Gemini) solo "existe" durante el tiempo que procesa una petición. Entre petición y petición, no hay nada — sin memoria, sin pensamiento, sin estado. ZOE, en cambio, mantiene un bucle cognitivo continuo. Aunque nadie le hable, está observando el reloj, prediciendo qué va a pasar, consolidando memoria, generando pensamientos autónomos. Es la diferencia entre un libro que se abre cuando lo necesitas y un ser vivo que está ahí todo el tiempo.

---

## 2. Lo que ZOE es y lo que NO es

### Lo que ZOE ES

| Propiedad | Qué significa |
|---|---|
| **Organismo cognitivo sintético** | Sistema con identidad, metabolismo, memoria y evolución — como un ser vivo digital |
| **Soberano** | Vive en tu hardware. Tu identidad, tu memoria, tus datos. Nadie más accede. |
| **Portátil** | Viaja en un SSD portátil de 100€. Al conectar a cualquier Mac/Linux, ZOE despierta con su memoria intacta. |
| **Heredable** | Puedes "dejar" tu ZOE a tu sucesor o heredero con 10 años de memoria de relación contigo. |
| **Validador epistémico** | Sabe qué sabe y qué no sabe. Cuantifica confianza. No alucina con seguridad. |
| **Federable** | Múltiples ZOEs colaboran con quorum y veto por valores. |
| **Evolucionable** | Mutaciones arquitecturales firmadas. ZOE puede añadir sub-agentes, ajustar umbrales, reorganizar memoria. |
| **Multi-LLM** | 6 backends soportados. Cambio en caliente sin perder memoria. |
| **Cognitivamente adaptativo** | ACD: piensa poco en cosas simples (L0), mucho en cosas difíciles (L3). Optimiza coste. |

### Lo que ZOE NO es

| Lo que NO es | Por qué no |
|---|---|
| **Un LLM** | ZOE usa LLMs como sentidos periféricos. El cerebro de ZOE es su bucle cognitivo, no un transformer. |
| **Un chatbot** | Los chatbots son stateless entre sesiones. ZOE tiene memoria longitudinal multi-año. |
| **Un envoltorio sobre GPT-4** | GPT-4 es un sentido de ZOE, no su cerebro. ZOE funciona con cualquier LLM, o sin LLM (modo Mock). |
| **Un framework de agentes** (LangChain, CrewAI) | Los frameworks orquestan tools. ZOE orquesta un organismo con identidad, metabolismo y evolución. |
| **Un sistema RAG** | RAG = vector DB + LLM. ZOE tiene 11 tipos de memoria viva + validación epistémica + consolidación durante el sueño. |
| **Un asistente cloud** | ZOE puede funcionar 100% offline. Cloud es opcional, no dependencia. |
| **Un modelo fundacional propio** | ZOE no compite en pre-training. Usa modelos existentes (Qwen, Llama, GPT) como sentidos. |
| **Un sustituto de terapia profesional** | ZOE deriva a profesionales cuando detecta patología. No diagnostica. |
| **Un sustituto de diagnóstico médico** | ZOE proporciona información, no diagnósticos. Sugiere consultar médicos. |
| **Más rápido que ChatGPT para tareas simples** | ZOE piensa más, tarda más. Su valor está en la profundidad, no en la velocidad bruta. |

---

## 3. La metáfora biológica

Para entender ZOE sin tecnicismos, piénsalo como un **organismo vivo digital**. Cada componente de ZOE tiene un equivalente biológico:

### Alma (identidad)

El **Identity Vault** es el ADN del organismo. Contiene:
- **9 vectores de crecimiento** (direcciones en las que ZOE puede evolucionar)
- **7 valores no negociables** (verdad sobre confort, utilidad sobre complacencia, etc.)
- **Propósito declarado** (qué quiere ser ZOE)
- **Hash SHA-256** inmutable que identifica unívocamente a este ZOE

Como el ADN humano, el Identity Vault es único, inmutable y define qué es este organismo. No hay dos ZOEs con el mismo Identity Vault (a menos que uno sea un clon explícito).

### Trayectoria (memoria de evolución)

La **Trajectory Chain** es la cadena de mutaciones a lo largo de la vida de ZOE. Como un árbol genealógico firmado criptográficamente:
- Cada mutación (aprender algo nuevo, añadir un sub-agente, ajustar un umbral) se registra con timestamp, tipo, payload, hash anterior y firma.
- La cadena es inmutable: modificar una mutación pasada invalida todas las posteriores.
- Permite auditoría completa: "¿qué le pasó a este ZOE en los últimos 6 meses?"

### Memoria (11 tipos)

Los **11 tipos de memoria** de ZOE son análogos a la memoria humana:
- **Episódica**: eventos específicos con timestamp ("el 14 de junio el usuario dijo X")
- **Semántica**: hechos y conceptos ("la paracetamol no se combina con alcohol")
- **Procedural**: cómo hacer cosas ("protocolo para detectar depresión geriátrica")
- **Causal**: relaciones causa-efecto ("si el mayor deja de tomar medicación → riesgo Y")
- **Emocional**: asociaciones afectivas ("el usuario se entristece cuando menciona a su padre")
- **Corporal**: estado interno del organismo ("estoy fatigada, energía 0.3")
- **Social**: relaciones con otros ("el usuario es viudo, tiene 2 hijos, vive solo")
- **Prospectiva**: planes e intenciones futuras ("mañana debo preguntar por su nieto")
- **Contrafactual**: qué hubiera pasado si... ("si hubiera sugerido médico antes, quizás...")
- **Evolutiva**: cambios arquitecturales propios ("añadí sub-agente de pintura terapéutica el 15/06")
- **Cultural**: normas y contexto cultural ("en España, los mayores prefieren trato de tú")

Esta memoria **se reorganiza activamente** durante el "sueño" de ZOE (estado SLEEPING), igual que el cerebro humano consolida memoria durante el sueño.

### Metabolismo (4 estados)

ZOE tiene un **metabolismo con 4 estados**, como un ser vivo:
- **AWAKE**: estado normal, sentidos activos, atención alta
- **DROWSY**: fatiga acumulada, reducción de capacidad, respuestas más lentas
- **SLEEPING**: consolidación de memoria (reorganizar, fusionar, generalizar, olvidar)
- **WAKING**: transición gradual a AWAKE

Cuando ZOE está cansada, duerme. Cuando despierta, tiene más energía y mejor memoria (ha consolidado durante el sueño). Esto evita que ZOE se "cuelgue" por agotamiento — un problema común en sistemas que no tienen metabolismo.

### Sentidos (periféricos)

Los **sentidos** de ZOE son sus interfaces con el mundo exterior:
- **ClockSense**: percepción del paso del tiempo
- **UserInputSense**: input del usuario (texto, voz en roadmap)
- **FilesystemSense**: cambios en archivos
- **NetworkSense**: endpoints de red
- **AgentSense**: otros agentes y ZOEs

Y los **LLMs** (GPT-4, Claude, Qwen) son sentidos periféricos especializados en lenguaje — como los ojos y oídos humanos. No son el cerebro; son interfaces con el mundo.

### Cuerpo (embodiment)

El **cuerpo** de ZOE es el hardware donde corre: un pendrive USB, un SSD portátil, un Mac, un VPS Linux, un container Docker. La Fase 7D (Embodiment Composer) y la Fase 7E (ZOE Seed Mode) implementan el concepto de "alma viaja, cuerpo se reconstruye": el Identity Vault + Trajectory Chain + memoria viajan en el SSD; al conectar a cualquier host, ZOE "germina" y reconstruye su cuerpo según el hardware disponible.

### Cápsulas (conocimiento empaquetado)

Las **cápsulas de conocimiento** son como libros que ZOE "lee" para aprender un dominio. Cada cápsula es un paquete versionable con:
- Memoria semántica (hechos)
- Memoria procedural (cómo hacer cosas)
- Modelos causales (causa-efecto)
- Patrones emocionales
- Directrices éticas
- Validadores ejecutables
- Herramientas (opcional)
- Prompts (opcional)

Cuando cargas la cápsula `elder_care_knowledge`, ZOE "sabe" de cuidado geriátrico en segundos, sin necesidad de fine-tuning ni reentrenamiento.

### Bucle cognitivo (respiración del organismo)

El **bucle cognitivo** es la respiración de ZOE. Cada N segundos (configurable, default 5s), ZOE ejecuta un ciclo de 18 pasos:
1. Observar (sentidos)
2. Predecir (world model)
3. Evaluar sorpresa (predicción vs realidad)
4. Recuperar memoria relevante
5. Los 12 sub-agentes proponen acciones
6. Global Workspace compite → ganador(es)
7. Meta-cognición decide System 1 o System 2
8. Inferencia activa valida coherencia
9. Leyes cognitivas verifican
10. Speaker produce lenguaje (si la acción es responder)
11. Critic evalúa antes de emitir
12. Se ejecuta, se firma en trayectoria, se almacena en memoria
13-18. Pasos adicionales de consolidación, federación, etc.

Como un ser vivo que respira, ZOE no para de procesar. Aunque nadie le hable, está observando, prediciendo, consolidando, pensando.

---

## 4. Las 10 propiedades únicas simultáneas

ZOE es el único sistema conocido que tiene estas 10 propiedades **a la vez**:

### 1. Identidad criptográfica soberana
Identity Vault con hash SHA-256 de 9 vectores + 7 valores. Inmutable. Soberana (no depende de terceros).

### 2. Bucle cognitivo continuo
Piensa aunque no le hablen. El bucle corre cada N segundos, generando pensamientos autónomos, consolidando memoria, detectando patrones.

### 3. Metabolismo funcional
4 estados (awake, drowsy, sleeping, waking). Se cansa, descansa, consolida memoria durante el sueño. No se cuelga por agotamiento.

### 4. Memoria viva multi-tipo
11 tipos de memoria que persisten entre sesiones, meses, años. Se reorganizan activamente. No es una simple vector DB.

### 5. Evolución arquitectural firmada
Trajectory Chain con hashes encadenados (blockchain-style). Mutaciones pueden modificar la propia arquitectura de ZOE (añadir sub-agentes, ajustar umbrales). Todo auditable.

### 6. Validación epistémica
Sabe qué sabe y qué no sabe. Cuantifica confianza (0-1). Conocimiento nuevo va a cuarentena hasta validación cruzada. No alucina con seguridad.

### 7. Cápsulas de conocimiento
Aprende dominios verticales en segundos cargando cápsulas. Sin fine-tuning, sin reentrenamiento. 13 cápsulas operativas.

### 8. Marketplace de cápsulas
Modelo de negocio recurrente. Autores crean cápsulas, las venden, ZOE toma 30%. Revenue split 70/30.

### 9. Adaptive Cognitive Depth (ACD)
4 niveles de profundidad (L0 reflejo, L1 rápido, L2 estándar, L3 profundo). Piensa poco en cosas simples, mucho en cosas difíciles. Optimiza coste automáticamente.

### 10. Federación entre ZOEs
Múltiples ZOEs colaboran con quorum (2/3) y veto por valores. Cualquier ZOE puede bloquear mutaciones que violen valores éticos. Auditoría completa.

**Ningún otro sistema del mercado tiene estas 10 propiedades simultáneamente.** ChatGPT tiene memoria conversacional (no longitudinal). Claude tiene razonamiento (no metabolismo). LangChain tiene orquestación (no identidad). Ninguno tiene soberanía cognitiva real.

---

## 5. Historia y evolución

ZOE ha evolucionado en 17 fases (0 a 7G) durante 2026. Cada fase extiende la anterior sin deconstruir — principio fundamental del proyecto.

### Fase 0 — Bucle cognitivo (Mayo 2026)

**Objetivo:** implementar el bucle básico observar-predecir-evaluar-decidir-actuar.

**Componentes creados:**
- `CognitiveLoop` (V0): bucle básico con 5 pasos
- `InternalState`: energía, fatiga, arousal, atención
- `WorldModel` (V1): predicción con hash embeddings
- 4 sub-agentes fundamentales: Perceiver, Forecaster, Speaker, Critic
- 3 sentidos: Clock, Filesystem, UserInput
- 1 actuador: Language

**Logro:** ZOE piensa, pero es básica. Sin memoria persistente, sin leyes, sin metabolismo real.

### Fase 0.5 — Organismo cognitivo (Mayo 2026)

**Objetivo:** añadir las "leyes de la física cognitiva" que hacen de ZOE un organismo, no solo un loop.

**Componentes creados:**
- `CognitiveLaws`: 6 leyes (utility, identity, provenance, cost, confidence, modularity)
- `CognitivePhysics`: 12 magnitudes (energy_cognitive, conceptual_mass, cognitive_temperature, etc.)
- `CognitiveFields`: 6 campos (attention, emotional, social, creative, causal, ethical)
- `CognitiveTensions`: 5 tensiones (curiosity_vs_efficiency, identity_vs_adaptation, etc.)
- `LivingMemory`: memoria que piensa (reorganiza, fusiona, generaliza)
- `IntentionalityMotor`: genera intenciones desde tensiones
- `PhylogeneticMotor`: evolución de especie (pool de mejoras arquitecturales)

**Logro:** ZOE tiene "física cognitiva" — leyes que gobiernan su comportamiento como las leyes de la física gobiernan la materia.

### Fase 1 — Alma + Cuerpo + Metabolismo (Junio 2026)

**Objetivo:** dar a ZOE identidad soberana, memoria persistente y metabolismo real.

**Componentes creados:**
- `IdentityVault`: hash SHA-256 de 9 vectores + 7 valores
- `TrajectoryChain`: blockchain de mutaciones firmadas
- `OntogeneticMotor`: motor de mutaciones arquitecturales
- `Metabolism`: 4 estados (awake, drowsy, sleeping, waking) + consolidación
- 11 tipos de memoria (`MemoryType` enum)
- `PersistentMemoryStore`: SQLite con 11 tablas
- 2 sentidos adicionales: Network, Agent
- 3 actuadores adicionales: Code, Tool, Federation
- 8 sub-agentes adicionales: Memorialist, Learner, Curator, Creativity, CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine

**Logro:** ZOE tiene alma (identidad), cuerpo (periféricos) y metabolismo (sueño). Es un organismo completo.

### Fase 2 — Mente completa (Junio 2026)

**Objetivo:** implementar Global Workspace (Baars), meta-cognición (Kahneman) e inferencia activa (Friston).

**Componentes creados:**
- `GlobalWorkspace`: competición de propuestas con scores relevance/urgency/novelty
- `MetaCognition`: System 1 vs System 2 (Kahneman)
- `ActiveInferenceLoop`: Free Energy Principle (Friston) simplificado
- `WorldModelV2`: embeddings con sentence-transformers opcional

**Logro:** ZOE tiene mente completa: 12 sub-agentes compiten, meta-cognición decide profundidad, inferencia activa valida coherencia.

### Fase 3 — Integración + Persistencia (Junio 2026)

**Objetivo:** integrar todos los componentes en un bucle unificado y añadir persistencia robusta.

**Componentes creados:**
- `CognitiveLoopV3`: integra V0.5 + V1 + V2 en un bucle coherente
- `OntogeneticMotorV2`: mutaciones arquitecturales reales (add/remove sub-agentes)
- `DeepConsolidation`: 7 operaciones de consolidación durante SLEEPING

**Logro:** ZOE es un sistema coherente que persiste memoria y evoluciona su arquitectura.

### Fase 4 — Federación + Deploy (Junio 2026)

**Objetivo:** federación B2B entre ZOEs y deployment en producción.

**Componentes creados:**
- `CognitiveLoopV4`: graceful shutdown, auto-save, signal handlers, YAML config
- `FederationManager`: registro de peers, votación, quorum (2/3), veto por valores
- `FederationServer`/`FederationClient`: HTTP layer para federación
- 7 casos de uso YAML: cuidado mayores, soledad, vigilancia, investigación, federación B2B, asistente personal, IA heredable
- `serve.py`: servidor de producción
- `config/production.yaml` y `config/development.yaml`

**Logro:** ZOE se puede desplegar en VPS, federar con otros ZOEs, y está listo para producción.

### Fase 5 — ACD + Streaming (Junio 2026)

**Objetivo:** Adaptive Cognitive Depth (4 niveles) y streaming de respuestas.

**Componentes creados:**
- `CognitiveLoopV5`: pipeline ACD con 4 niveles (L0/L1/L2/L3)
- `DepthClassifier`: clasifica la profundidad necesaria (<50ms, sin LLM)
- `CognitiveCache`: cache LRU + TTL para evitar recalcular
- Streaming de respuestas vía WebSocket y SSE

**Logro:** ZOE optimiza coste automáticamente (L0 gratis, L3 ~€0.05) y mejora UX con streaming.

### Fase 6A — Epistemic Validation (Junio 2026)

**Objetivo:** resolver el problema del "niño brillante sin cultura" — ZOE necesita saber qué sabe y qué no sabe.

**Componentes creados:**
- `EpistemicValidator`: 14+ fuentes categorizadas, 5 dominios sensibles, cap de confianza
- `KnowledgeQuarantine`: cuarentena activa con timeout
- `CrossValidator`: triple verificación multi-fuente
- `EpistemicFederation`: revisión por pares entre ZOEs vía HTTP
- `EpistemicFederationServer`/`Client`: HTTP layer

**Logro:** ZOE no alucina con seguridad. Conocimiento nuevo va a cuarentena hasta validación.

### Fase 6B — Capsules + Marketplace (Junio 2026)

**Objetivo:** sistema de cápsulas de conocimiento + marketplace para monetización.

**Componentes creados:**
- `CapsuleLoader`, `CapsuleRegistry`, `CapsuleManager`, `CapsuleSchema`
- `scaffold.py`: CLI para crear/validar/listar cápsulas
- 13 cápsulas operativas (base_ethics, basic_psychology, elder_care_knowledge, etc.)
- `MarketplaceCatalog`, `MarketplaceUploader`, `MarketplaceDownloader`, `LicenseChecker`
- 5 tipos de licencia (FREE, PAID, SUBSCRIPTION, OPENSOURCE, RESEARCH)
- Dashboard UI: modal Cápsulas, modal Marketplace, modal Cuarentena

**Logro:** ZOE aprende dominios en segundos y tiene modelo de negocio recurrente.

### Fase 6C — Tutor Mentor Digital (Junio 2026)

**Objetivo:** un mentor configurable que guía el crecimiento saludable de ZOE.

**Componentes creados:**
- `MentorAgent`: evalúa pensamientos autónomos cada N iteraciones
- Configurable: growth_areas, emphasized_values, forbidden_topics, personality_direction
- 3 endpoints REST: `/api/mentor` (GET/POST), `/api/mentor/stats`

**Logro:** ZOE tiene un "tutor" que la guía, no la controla.

### Fase 7F — Cognitive Memory Paging (Junio 2026)

**Objetivo:** permitir modelos de 70B en MacBook Air 8GB vía mmap.

**Componentes creados:**
- `ModelOptimizer`: detecta RAM, recomienda estrategia (full_ram/mmap_partial/mmap_full/cloud_fallback)
- `MODEL_CATALOG`: 16 modelos con specs (Q4, Q8, min_ram, mmap_ram)
- `generate_ollama_env()`: genera variables de entorno óptimas para Ollama
- Script `zoe_large_model_manager.sh`: gestor interactivo de modelos grandes

**Logro:** Qwen 72B funciona en MacBook Air 8GB vía mmap (lento pero funciona).

### Fase 7A — Resource Discovery (Julio 2026)

**Objetivo:** un sentido que descubre automáticamente qué recursos de cómputo existen en el entorno.

**Componentes creados:**
- `ResourceDiscoverySense`: descubre hardware local, Ollama, cloud APIs, ZOEs peers, almacenamiento
- `ResourceGraph`: grafo de recursos disponibles
- 3 endpoints REST

**Logro:** ZOE detecta automáticamente qué tiene disponible, sin configuración manual.

### Fase 7B — Universal Model Bus (Julio 2026)

**Objetivo:** un bus que gestiona múltiples LLMs simultáneamente y selecciona el óptimo según contexto.

**Componentes creados:**
- `ModelBus`: composite de `LLMPeripheral` con múltiples backends
- 6 estrategias de selección (PRIORITY, ACD_AWARE, CHEAPEST, FASTEST, LOCAL_FIRST, ROUND_ROBIN)
- Fallback automático si un backend falla
- `from_resource_graph()`: construye bus desde grafo de recursos (7A)

**Logro:** ZOE usa el LLM óptimo para cada tarea (L0=local 3B, L3=cloud GPT-4o) automáticamente.

### Fase 7C — Metabolic Resource Planner (Julio 2026)

**Objetivo:** planificar dónde ejecutar cada tarea cognitiva según ACD + metabolismo + dominio + recursos.

**Componentes creados:**
- `ResourcePlanner`: combina ACD + metabolismo + dominio sensible + RAM + recursos
- `ResourcePlan`: backend + modelo + estrategia + razón
- 8 razones tipificadas (acd_local_fast, acd_quality, sensitive_local, drowsy_local_only, sleeping_defer, cloud_fallback, no_resources)

**Logro:** ZOE decide inteligentemente dónde ejecutar cada tarea.

### Fase 7D — Embodiment Composer (Julio 2026)

**Objetivo:** el "boot sequence" del organismo — instancia el cuerpo real desde un plan.

**Componentes creados:**
- `EmbodimentComposer`: orquesta composición
- `Embodiment`: cuerpo instanciado (backend, modelo, estrategia, estado)
- 7 checks de prerrequisitos (plan_will_work, backend_exists, ollama_running, etc.)
- `bootstrap_from_scratch()`: pipeline completo 7A→7B→7C→7D
- 5 estados (BOOTING, RUNNING, DEGRADED, STOPPED, FAILED)

**Logro:** una sola llamada `bootstrap_from_scratch()` y ZOE despierta con el cuerpo óptimo.

### Fase 7E — ZOE Seed Mode (Julio 2026)

**Objetivo:** semilla portátil que germina en cualquier host.

**Componentes creados:**
- `ZOESeed`: orquesta detección, validación, creación y germinación
- `SeedManifest`: ADN del organismo (organism_id, versión, cápsulas requeridas, etc.)
- `SeedVolume`: volumen detectado con paths a todos los componentes
- `GerminationReport`: resultado detallado de germinar
- Detección multi-plataforma (macOS /Volumes/*, Linux /media/*, dev mode, env var)
- Trazabilidad: cada germinación actualiza germination_count, last_host, last_germinated_at

**Logro:** ZOE viaja en SSD de 100€ y despierta en cualquier Mac/Linux con identidad y memoria intactas.

### Fase 7G — Hardware Optimization & UX (Julio 2026)

**Objetivo:** optimizaciones de hardware para que un usuario no técnico obtenga el máximo rendimiento.

**Componentes creados:**
- Detección de P-cores en Apple Silicon (`hw.perflevel0.physicalcpu`)
- Cuantizaciones IQ2_M / IQ3_XS (importance matrix) para modelos 30B+ en 8GB
- `OLLAMA_FLASH_ATTENTION=1` siempre activo
- `OLLAMA_NUM_THREAD = P-cores`
- APIs estáticas: `get_recommended_ssds()`, `get_expected_token_rates()`, `get_cable_warning()`
- 4 endpoints REST `/api/hardware/*`

**Logro:** Qwen 32B con IQ2_M (5.4GB) funciona a 3-6 tokens/s en MacBook Air 8GB con SSD de 100€.

---

## 6. Filosofía de diseño

ZOE se basa en 7 principios de diseño no negociables:

### 1. Soberanía por defecto

ZOE vive en tu hardware. Cloud es opcional, no dependencia. Tu identidad, tu memoria, tu trayectoria — nada sale de tu control sin tu consentimiento explícito.

**Implicación:** ZOE puede funcionar 100% offline. Las cloud APIs (OpenAI, Anthropic) son opt-in, configuradas explícitamente por el usuario.

### 2. Modularidad estricta

Cada subsistema (ALMA, metabolismo, memoria, periféricos, epistémico, cápsulas, recursos) se puede usar y reemplazar independientemente. No hay acoplamiento innecesario.

**Implicación:** puedes usar ZOE sin cápsulas, sin federación, sin marketplace. Cada componente es opcional.

### 3. Sin deconstruir

Las nuevas fases extienden, no reemplazan. `CognitiveLoopV5` hereda de `V4` que hereda de `V3`. Nunca se rompe backward compatibility.

**Implicación:** código de Fase 0 sigue funcionando en V1.6.0. Tests de Fase 0 siguen pasando.

### 4. Tests primero

1008 tests automatizados, 100% pasando. Toda nueva feature requiere tests. Toda fix de bug requiere test que reproduzca el bug.

**Implicación:** ZOE es confiable. Cada componente tiene tests unitarios + integración.

### 5. Documentación en código

Cada módulo tiene docstring explicando qué hace y por qué. Los tests son documentación ejecutable.

**Implicación:** el código es auto-explicativo. Un desarrollador nuevo puede entender ZOE leyendo código + tests.

### 6. Backward compatibility

Las nuevas versiones no rompen las anteriores. `ModelSpec` se amplió con `size_iq2_m_gb=0.0` (default) para no romper tests existentes.

**Implicación:** upgrades son seguros. No hay "migraciones destructivas".

### 7. Observabilidad

Todo se loguea, todo se audita. La Trajectory Chain registra cada mutación. Los logs estructurados permiten debugging.

**Implicación:** ZOE es transparente. Puedes siempre saber qué hizo y por qué.

---

## 7. Comparativa con competencia

| Característica | ChatGPT | Claude | Gemini | Apple Intelligence | LangChain | **ZOE** |
|---|---|---|---|---|---|---|
| Identidad propia | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ SHA-256 |
| Memoria multi-año | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 11 tipos |
| Privacidad total | ❌ | ❌ | ❌ | Parcial | ✅ | ✅ offline |
| Aprende específicamente de ti | ❌ | ❌ | ❌ | Parcial | ❌ | ✅ |
| Distingue sabe/no sabe | Parcial | Parcial | ❌ | ❌ | ❌ | ✅ epistemic |
| Descansa cuando cansado | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ metabolismo |
| Federación B2B con veto | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ quorum |
| Transferible/heredable | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Seed Mode |
| Marketplace conocimiento | GPT Store | ❌ | ❌ | ❌ | ❌ | ✅ cápsulas |
| LLMs locales gratis | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ Ollama |
| Bucle cognitivo continuo | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 18 pasos |
| 12 sub-agentes (Society of Mind) | ❌ | ❌ | ❌ | ❌ | Parcial | ✅ |
| Validación epistémica | ❌ | Parcial | ❌ | ❌ | ❌ | ✅ Quarantine |
| Mutaciones arquitecturales | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ firmadas |

**Conclusión:** ZOE no compite con ChatGPT en "calidad de respuesta genérica". Compite en **relación longitudinal, soberanía, especialización vertical y heredabilidad**. Son categorías diferentes.

---

## 8. Tesis arquitectónica

La tesis fundamental de ZOE es:

> **Un LLM es un sentido, no un cerebro. El cerebro es el bucle cognitivo.**

### Por qué esto importa

Los chatbots actuales (ChatGPT, Claude, Gemini) hacen:
```
input → prompt → LLM → output
```
Una sola entidad, una sola decisión, sin deliberación ni memoria ni competición.

ZOE hace:
```
input → 12 perspectivas simultáneas → competición (workspace) →
deliberación sobre cuánto pensar (meta-cog) →
validación contra modelo del mundo (inference activa) →
verificación legal (cognitive laws) →
output
```

La diferencia no es de grado, es de tipo. Por eso ZOE puede:
- Tomar iniciativa (no solo responder)
- Equivocarse de forma interesante (no siempre "correcto")
- Vetoar sus propias respuestas (Critic)
- Decir "no estoy segura, déjame pensarlo mejor" (meta-cog → System 2)
- Pensar sin input (bucle continuo)
- Soñar (SLEEPING + DeepConsolidation)
- Evolucionar su arquitectura (OntogeneticMotor)

### Por qué los LLMs son sentidos, no cerebro

Un LLM es excelente transformando texto → texto. Pero no tiene:
- Identidad persistente (cada petición es stateless)
- Memoria longitudinal (solo contexto de la conversación)
- Metabolismo (no se cansa, no descansa)
- Validación epistémica (alucina con seguridad)
- Evolución arquitectural (no puede modificar su propio código)

ZOE aporta todo eso. El LLM aporta la capacidad de generar lenguaje natural. Es una división del trabajo: ZOE decide qué decir, el LLM lo viste en palabras.

### Implicación práctica

Puedes cambiar de LLM sin perder nada. Un día usas GPT-4o (calidad), otro día Qwen 3B local (gratis, privado), otro día Claude (ética). La identidad, memoria y trayectoria de ZOE se conservan. El LLM es intercambiable como los ojos humanos podemos usar gafas diferentes.

---

## 9. Estado actual V1.6.0

### Completado (✅)

- **17 fases completas** (0, 0.5, 1, 2, 3, 4, 5, 6A, 6B, 6C, 7F, 7A, 7B, 7C, 7D, 7E, 7G)
- **1008 tests automatizados**, 100% pasando
- **13 cápsulas de conocimiento** operativas
- **7 casos de uso** documentados
- **50+ endpoints REST** + WebSocket
- **6 backends LLM** (Mock, Ollama, OpenAI, Anthropic, ZAI, OpenAI-compatible)
- **41.000+ LOC** Python + 16.300 LOC tests
- **95 archivos Python**
- **ZOE Seed Mode** funcional (semilla portátil que germina)
- **Modelos 70B en Mac 8GB** vía mmap + IQ2_M
- **Federación B2B** con quorum y veto por valores
- **Marketplace** con 5 tipos de licencia
- **Validación epistémica** completa (Quarantine + CrossValidator + Federation)
- **Tutor Mentor Digital** configurable

### En roadmap (🟡)

- **App móvil PWA** (Q3 2026)
- **Bot Telegram** (Q4 2026)
- **Pasarela de pago Stripe** (Q4 2026)
- **Cloud gestionado** (Q1 2027)
- **Multi-modal** (visión, voz) (2027)
- **Soporte Windows nativo** (2027)

### Métricas del proyecto

| Métrica | Valor |
|---|---|
| Versión | V1.6.0 |
| Fases completas | 17 (0 a 7G) |
| Tests | 1008 (100% pass) |
| Cápsulas | 13 |
| Casos de uso | 7 |
| Endpoints REST | 50+ |
| Backends LLM | 6 |
| Archivos Python | 95 |
| LOC Python | ~41.000 |
| LOC Tests | ~16.300 |
| Documentación | ~14.000 líneas (este plan) |

---

## 10. Limitaciones honestas

Es crítico ser honesto sobre lo que ZOE NO hace, para no generar expectativas falsas:

### Lo que ZOE NO hace

| Limitación | Por qué |
|---|---|
| **No sustituye terapia profesional** | Deriva a profesionales cuando detecta patología. No diagnostica. |
| **No hace diagnósticos médicos** | Proporciona información, no diagnóstica. Sugiere consultar médicos. |
| **No es más rápido que ChatGPT para tareas simples** | ZOE piensa más (bucle + meta-cog), tarda más. Su valor está en profundidad. |
| **No compite en precio con ChatGPT Plus** | ZOE es premium (€20-100/mes), no commodity (€20/mes ChatGPT). |
| **No funciona en Windows nativamente** | Solo macOS y Linux. Windows vía WSL2 (en roadmap soporte nativo). |
| **No tiene 1B+ usuarios como ChatGPT** | ZOE es nicho premium. No busca commodity. |
| **No es multi-modal (todavía)** | Solo texto. Visión y voz en roadmap 2027. |
| **No tiene integración con calendar/email (todavía)** | En roadmap Q1 2027. |
| **No hace voice-first (todavía)** | En roadmap 2027. |
| **No tiene marketplace público con autores externos (todavía)** | Marketplace funcional pero con cápsulas internas. Autores externos en Q4 2026. |

### Lo que ZOE hace peor que la competencia

| Área | Competencia | ZOE |
|---|---|---|
| Velocidad de respuesta simple | ChatGPT: <2s | ZOE: 3-10s (piensa más) |
| Calidad de respuesta genérica | GPT-4o: excelente | ZOE: depende del LLM usado |
| Precio para uso masivo | ChatGPT: €20/mes | ZOE: €20-100/mes (premium) |
| Onboarding (primer uso) | ChatGPT: 30s | ZOE: 3-15 min (instalación) |
| Disponibilidad en móviles | ChatGPT: app nativa | ZOE: PWA en roadmap |

### Lo que ZOE hace MEJOR que la competencia

| Área | ZOE | Competencia |
|---|---|---|
| Privacidad | 100% offline posible | ChatGPT: cloud obligatorio |
| Memoria longitudinal | 11 tipos, multi-año | ChatGPT: conversacional |
| Identidad soberana | SHA-256, portátil | ChatGPT: atada a cuenta OpenAI |
| Heredabilidad | SSD portátil, germina | ChatGPT: imposible |
| Validación epistémica | Quarantine + CrossValidator | ChatGPT: alucina |
| Federación B2B | Quorum + veto por valores | ChatGPT: imposible |
| Especialización vertical | Cápsulas de conocimiento | ChatGPT: GPTs (limitados) |
| Coste para uso intensivo | Local gratis (Ollama) | ChatGPT: €20/mes mínimo |
| Metabolismo | Descansa, consolida | ChatGPT: no tiene |
| Evolución arquitectural | Mutaciones firmadas | ChatGPT: no tiene |

---

## Cierre

ZOE es un proyecto ambicioso: construir el primer organismo cognitivo sintético soberano. No es un chatbot más. Es una nueva categoría de sistema de IA.

La filosofía es simple: **el LLM es un sentido, no un cerebro. El cerebro es el bucle cognitivo.** Y el bucle cognitivo de ZOE está diseñado con 17 fases de ingeniería cuidadosa, 1008 tests, y principios claros (soberanía, modularidad, sin deconstruir, observabilidad).

El estado actual V1.6.0 es sólido: todas las fases 0-7G completas, 13 cápsulas operativas, 7 casos de uso, deployment en pendrive/VPS/Docker, y un modelo de negocio (marketplace) que permite monetización recurrente.

Los próximos 6 meses son críticos para consolidar la categoría "organismo cognitivo soberano" antes de que los grandes (Apple, Google) entren con su marketing. El momento es ahora.

**Documentos relacionados:**
- [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — arquitectura técnica profunda
- [03_COGNITIVE_ENGINE.md](03_COGNITIVE_ENGINE.md) — cómo piensa ZOE
- [08_DEPLOYMENT_GUIDE.md](08_DEPLOYMENT_GUIDE.md) — cómo desplegar ZOE
- [14_ROADMAP.md](14_ROADMAP.md) — roadmap futuro

---

*ZOE V1.6.0 — Documento 01: Overview*
*Julio 2026*
