# Changelog

> **Historial de versiones de ZOE.**
> **Formato:** [Keep a Changelog](https://keepachangelog.com/)

---

## [1.6.0] — Julio 2026

### Added
- **Fase 7G — Hardware Optimization & UX**
  - Detección de P-cores en Apple Silicon (`detect_p_cores()`, `detect_e_cores()`)
  - Cuantizaciones IQ2_M / IQ3_XS (importance matrix) en MODEL_CATALOG
  - `OLLAMA_FLASH_ATTENTION=1` siempre activo
  - `OLLAMA_NUM_THREAD = P-cores`
  - APIs estáticas: `get_recommended_ssds()`, `get_expected_token_rates()`, `get_cable_warning()`
  - 4 endpoints REST `/api/hardware/*`
  - 50 tests nuevos (hardware optimization + endpoints)
- **README profesional** reescrito (408 líneas)
- **15 documentos de documentación** completa (14.000+ líneas)

### Changed
- Version bump: 1.5.0 → 1.6.0
- Tests: 952 → 1008
- `ModelSpec` ampliado con `size_iq2_m_gb` y `size_iq3_xs_gb` (defaults 0.0)
- `generate_ollama_env()` ahora activa flash attention siempre
- `get_system_info()` ahora incluye `p_cores` y `e_cores`

---

## [1.5.0] — Julio 2026

### Added
- **Fase 7E — ZOE Seed Mode**
  - `ZOESeed`: semilla portátil que germina en cualquier host
  - `SeedManifest`: ADN del organismo (organism_id, versión, cápsulas)
  - Detección multi-plataforma (macOS, Linux, dev mode, env var)
  - Trazabilidad: `germination_count`, `last_host`, `last_germinated_at`
  - 6 endpoints REST `/api/seed/*`
  - 46 tests nuevos

---

## [1.4.0] — Julio 2026

### Added
- **Fase 7D — Embodiment Composer**
  - `EmbodimentComposer`: boot sequence del organismo
  - 7 checks de prerrequisitos
  - `bootstrap_from_scratch()`: pipeline completo 7A→7B→7C→7D
  - 5 estados (BOOTING, RUNNING, DEGRADED, STOPPED, FAILED)
  - 6 endpoints REST `/api/embodiment/*`
  - 43 tests nuevos

---

## [1.3.0] — Julio 2026

### Added
- **Fase 7A — Resource Discovery**
  - `ResourceDiscoverySense`: descubre hardware, Ollama, cloud APIs, peers
  - `ResourceGraph`: grafo de recursos disponibles
  - 3 endpoints REST
  - 18 tests nuevos
- **Fase 7B — Universal Model Bus**
  - `ModelBus`: composite de múltiples LLMs con selección ACD-aware
  - 6 estrategias de selección
  - Fallback automático
  - `from_resource_graph()`: construye bus desde grafo (7A)
  - 37 tests nuevos
- **Fase 7C — Metabolic Resource Planner**
  - `ResourcePlanner`: combina ACD + metabolismo + dominio + recursos
  - 8 razones tipificadas
  - 21 tests nuevos

---

## [1.2.0] — Junio 2026

### Added
- **Fase 6A — Epistemic Validation**
  - `EpistemicValidator`: 14+ fuentes, 5 dominios sensibles, cap de confianza
  - `KnowledgeQuarantine`: cuarentena activa con timeout
  - `CrossValidator`: triple verificación multi-fuente
  - `EpistemicFederation`: revisión por pares entre ZOEs
  - 41 tests nuevos
- **Fase 6B — Capsules + Marketplace**
  - 13 cápsulas de conocimiento operativas
  - `CapsuleLoader`, `CapsuleRegistry`, `CapsuleManager`, `CapsuleSchema`
  - `scaffold.py`: CLI para crear/validar/listar cápsulas
  - `MarketplaceCatalog`, `MarketplaceUploader`, `MarketplaceDownloader`
  - 5 tipos de licencia
  - Dashboard UI: modal Cápsulas, Marketplace, Cuarentena
  - 138 tests nuevos
- **Fase 6C — Tutor Mentor Digital**
  - `MentorAgent`: evalúa pensamientos autónomos
  - Configurable: growth_areas, emphasized_values, forbidden_topics
  - 3 endpoints REST
- **Fase 7F — Cognitive Memory Paging**
  - `ModelOptimizer`: detecta RAM, recomienda estrategia (mmap)
  - `MODEL_CATALOG`: 16 modelos con specs

---

## [1.0.0] — Mayo 2026

### Added
- **Fase 0 — Bucle cognitivo básico**
  - `CognitiveLoop` (V0): observar-predecir-evaluar-decidir-actuar
  - 4 sub-agentes: Perceiver, Forecaster, Speaker, Critic
  - 3 sentidos: Clock, Filesystem, UserInput
  - 1 actuador: Language
- **Fase 0.5 — Organismo cognitivo**
  - 6 leyes cognitivas
  - 12 magnitudes de física cognitiva
  - 6 campos cognitivos
  - 5 tensiones cognitivas
  - `LivingMemory`: memoria que piensa
- **Fase 1 — Alma + Cuerpo + Metabolismo**
  - `IdentityVault`: hash SHA-256 de 9 vectores + 7 valores
  - `TrajectoryChain`: blockchain de mutaciones firmadas
  - `OntogeneticMotor`: motor de mutaciones arquitecturales
  - 11 tipos de memoria
  - `Metabolism`: 4 estados (AWAKE, DROWSY, SLEEPING, WAKING)
  - 8 sub-agentes adicionales (12 total)
- **Fase 2 — Mente completa**
  - `GlobalWorkspace` (Baars): competición de propuestas
  - `MetaCognition` (Kahneman): System 1 vs System 2
  - `ActiveInferenceLoop` (Friston): Free Energy Principle
- **Fase 3 — Integración + Persistencia**
  - `CognitiveLoopV3`: integra todos los componentes
  - `PersistentMemoryStore`: SQLite con 11 tablas
  - `DeepConsolidation`: 7 operaciones durante SLEEPING
- **Fase 4 — Federación + Deploy**
  - `CognitiveLoopV4`: graceful shutdown, auto-save
  - `FederationManager`: quorum + veto por valores
  - 7 casos de uso YAML
- **Fase 5 — ACD + Streaming**
  - `CognitiveLoopV5`: ACD con 4 niveles (L0-L3)
  - `DepthClassifier`: clasifica profundidad
  - `CognitiveCache`: LRU + TTL
  - Streaming de respuestas

---

*ZOE V1.6.0 — Changelog*
