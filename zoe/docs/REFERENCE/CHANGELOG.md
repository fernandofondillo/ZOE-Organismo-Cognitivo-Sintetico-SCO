# Changelog

> **Historial de versiones de ZOE.**
> **Formato:** [Keep a Changelog](https://keepachangelog.com/)

---

## [1.7.0] — Julio 2026

### Added — Sprint 1: Multi-idioma + Windows + PWA + Telegram
- **LanguageDetector** (`zoe/core/language_detector.py`): detección de idioma por heurística de stopwords (<10ms, sin LLM). 4 idiomas: ES, EN, FR, DE.
- **LanguageProfile**: system prompts, reflex maps, validator keywords, ethical disclaimers y cultural notes por idioma.
- **Windows nativo**: detección de drives D:-Z: en `ResourceDiscoverySense` y `ZOESeed`. Installer PowerShell (`install_windows.ps1`). Scripts `.bat` launchers.
- **PWA responsive**: manifest.json endpoint, meta tags apple-mobile-web-app, CSS responsive 768px/480px. Instalable como app móvil.
- **Telegram bot bridge** (`zoe/peripherals/telegram_bridge.py`): puente entre Telegram y ZOE. 2 modos (api/direct). Comandos /start /help /stats /sleep /wake. Maneja texto, voz y fotos.
- 56 tests nuevos.

### Added — Sprint 2: Multi-modal (Visión + Voz)
- **VLMPeripheral** (`zoe/peripherals/multimodal.py`): LLM con capacidad de visión. 3 backends: OpenAI GPT-4o, Anthropic Claude, Ollama LLaVA.
- **VisionSense**: sentido que procesa imágenes. `inject_image(bytes, prompt)` → Observation con descripción.
- **VoiceInputSense**: STT con Whisper. `inject_audio(bytes)` → transcribe → Observation. Captura desde micrófono.
- **VoiceActuator**: TTS con Piper. `execute(action)` → genera voz → reproduce. Local, gratis, multilingüe.
- **Cápsula `multimodal_perception`** (14ª): 8 entries semánticas, 3 skills, 3 patrones emocionales, 5 directrices éticas, validators.
- 29 tests nuevos.

### Added — Sprint 3: Formato .zoe (PatternSpeaker + ZoePackager)
- **PatternPeripheral** (`zoe/peripherals/pattern_speaker.py`): LLMPeripheral que genera lenguaje SIN LLM. Clasifica intención (<1ms), busca en memoria, usa templates. Streaming simulado.
- **ZoePackager** (`zoe/core/zoe_packager.py`): empaqueta organismo ZOE completo en archivo `.zoe` (tarball). `package()`, `unpackage()`, `inspect()`. Incluye memory.db, capsules, config, manifest.json.
- **Cápsula `language_patterns`** (15ª): patrones de lenguaje para generación sin LLM. 5 semánticas, 2 skills, 3 éticas, validators.
- 35 tests nuevos.

### Added — Sprint 3.5: ZoeRuntime
- **zoe_runtime.py** (`zoe/core/zoe_runtime.py`): runtime mínimo que se incluye dentro de cada `.zoe`. Funciona con SOLO Python stdlib (sin pip install). Carga memory.db, capsules, identity. Detecta backends (pattern/embedded/ollama/cloud). CLI interactivo + Dashboard web mínimo con `http.server`.
- 32 tests nuevos.

### Added — Sprint 3.6: Enhanced PatternSpeaker
- **EnhancedPatternPeripheral** (`zoe/peripherals/enhanced_pattern_speaker.py`): PatternSpeaker mejorado con 3 capas:
  - **ResponseDistiller**: captura respuestas buenas de GPT-4o/Claude y las almacena en `distilled_responses.jsonl`. Recuperación por similitud léxica (Jaccard) + quality score.
  - **CapsuleRetriever**: carga 260+ entries de 15 cápsulas. Recupera knowledge relevante para enriquecer respuestas.
  - **DialogStateTracker**: rastrea emoción, tema, turnos. `_contextualize()` añade empatía según estado emocional.
- 30 tests nuevos.

### Added — Sprint 4: Voice-first mode
- **VoiceFirstMode** (`zoe/peripherals/voice_first.py`): conversación natural por voz tipo "Her". Bucle continuo: wake word → grabar → transcribir → ZOE → TTS → reproducir → repetir.
- **WakeWordDetector**: detecta "Hey ZOE" con openWakeWord (o fallback por energía).
- **VoiceActivityDetector**: detecta cuándo usuario habla/termina con webrtcvad (o fallback por energía).
- **InterruptionHandler**: detecta si usuario interrumpe a ZOE mientras habla.
- 2 modos: wake_word (automático) y push_to_talk (manual). 5 estados: IDLE/LISTENING/PROCESSING/SPEAKING/INTERRUPTED.
- 37 tests nuevos.

### Changed
- Version bump: 1.6.0 → 1.7.0
- Tests: 253 → 472 (219 nuevos)
- `__init__.py`: docstring actualizado con Sprint 1-4
- README: badges, features table, roadmap, estado actual actualizados
- `web_dashboard.py`: meta tags PWA + CSS responsive + endpoint manifest.json
- `resource_discovery.py`: detección de drives Windows
- `seed_mode.py`: detección de semillas en Windows

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
