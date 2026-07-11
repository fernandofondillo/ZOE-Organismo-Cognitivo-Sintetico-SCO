# Glossary

> **Glosario completo de términos ZOE.**
> **Versión:** V1.6.0 — Julio 2026

---

| Término | Definición |
|---|---|
| **ACD** | Adaptive Cognitive Depth. 4 niveles de profundidad (L0-L3). |
| **Active Inference** | Marco de Friston. ZOE minimiza "free energy" (sorpresa). |
| **ALMA** | Subsistema de identidad y trayectoria (Identity Vault + Trajectory Chain). |
| **AWAKE** | Estado metabólico normal. |
| **Baars Global Workspace** | Modelo cognitivo. Sub-agentes compiten por "broadcast". |
| **Capsule** | Paquete versionable de conocimiento experto. 8 tipos de contenido. |
| **CausalEngine** | Sub-agente que modela relaciones causa-efecto. |
| **Cognitive Cache** | Cache LRU+TTL para respuestas ACD-equivalentes. |
| **Cognitive Laws** | 6 leyes que gobiernan el comportamiento de ZOE. |
| **Cognitive Physics** | 12 magnitudes que describen el estado cognitivo. |
| **Cognitive Fields** | 6 dimensiones de experiencia cognitiva. |
| **Cognitive Tensions** | 5 fuerzas opuestas que ZOE equilibra. |
| **Creativity** | Sub-agente que combina conceptos distantes. |
| **Critic** | Sub-agente que evalúa respuestas antes de emitirlas. |
| **CrossValidator** | Triple verificación multi-fuente. |
| **Cuantización IQ2_M** | Importance Matrix 2-bit. ~30% tamaño Q4, 95% calidad. |
| **Cuantización IQ3_XS** | Importance Matrix 3-bit. ~40% tamaño Q4, 97% calidad. |
| **Cuantización Q4_K_M** | 4-bit quantization. Default balanceado. |
| **Curator** | Sub-agente que poda y consolida memoria. |
| **DeepConsolidation** | 7 operaciones de consolidación durante SLEEPING. |
| **DROWSY** | Estado metabólico de fatiga acumulada. |
| **Embodiment** | Instancia concreta de ZOE en un host. |
| **EmotionalMotor** | Sub-agente que modela estado emocional. |
| **Epistemic Validator** | Cuantifica confianza vs incertidumbre. |
| **EthicalMotor** | Sub-agente que evalúa dilemas éticos. |
| **Flash Attention** | Algoritmo optimizado. Reduce cómputo 40% en contextos largos. |
| **Forecaster** | Sub-agente que predice la próxima observación. |
| **Free Energy** | En Active Inference, sorpresa predictional. ZOE la minimiza. |
| **Global Workspace** | Mecanismo de competición entre sub-agentes (Baars). |
| **Identity Vault** | Identidad criptográfica SHA-256 de ZOE. |
| **Kahneman System 1/2** | Meta-cognición. System 1 rápido, System 2 deliberativo. |
| **Knowledge Quarantine** | Estado donde claims nuevos esperan validación. |
| **L0_REFLEX** | Nivel ACD más bajo. Respuesta refleja, <1s. |
| **L1_FAST** | Nivel ACD rápido. 1-3s. |
| **L2_STANDARD** | Nivel ACD estándar. 3-10s. |
| **L3_DEEP** | Nivel ACD profundo. 10-60s. |
| **Learner** | Sub-agente que extrae patrones. |
| **LivingMemory** | Memoria en caliente que piensa autónomamente. |
| **LLMPeripheral** | Interfaz común para todos los LLMs. |
| **Marketplace** | Tienda donde se compran y venden cápsulas. |
| **Memorialist** | Sub-agente bibliotecario. Gestiona 11 tipos de memoria. |
| **Metabolism** | 4 estados (AWAKE, DROWSY, SLEEPING, WAKING). |
| **MetaCognition** | System 1 vs System 2 (Kahneman). |
| **mmap** | Memory-mapped file loading. Modelos grandes sin cargar todo en RAM. |
| **ModelBus** | Bus que gestiona múltiples LLMs (Fase 7B). |
| **ModelOptimizer** | Optimiza carga de modelos según hardware (Fase 7F+7G). |
| **OntogeneticMotor** | Motor de mutaciones arquitecturales firmadas. |
| **P-cores / E-cores** | Performance / Efficiency cores en Apple Silicon. |
| **Perceiver** | Sub-agente traductor sensorial. |
| **PersistentMemoryStore** | Persistencia SQLite con 11 tablas. |
| **PhylogeneticMotor** | Motor de evolución de especie. |
| **Proposal** | Propuesta de un sub-agente en Global Workspace. |
| **ResourceGraph** | Grafo de recursos descubiertos (Fase 7A). |
| **ResourcePlan** | Plan de ejecución: backend + modelo + estrategia. |
| **ResourcePlanner** | Planifica dónde ejecutar cada tarea (Fase 7C). |
| **SCO** | Synthetic Cognitive Organism (organismo cognitivo sintético). |
| **ScientificEngine** | Sub-agente de método científico. |
| **SeedManifest** | Manifiesto JSON del ZOE Seed. ADN de la semilla. |
| **SLEEPING** | Estado metabólico de consolidación. |
| **Speaker** | Único sub-agente que llama al LLM. |
| **Trajectory Chain** | Blockchain de mutaciones firmadas. Inmutable. |
| **Trust Level** | Nivel de confianza de una cápsula: verified, curated, community, experimental. |
| **Umbrella Model Bus (UMB)** | Ver ModelBus. |
| **ZOE Seed** | Semilla portátil que germina en cualquier host (Fase 7E). |
| **.zoe** | Formato de archivo portable que contiene un organismo ZOE completo (memoria + cápsulas + patrones + config). Sprint 3. |
| **PatternSpeaker** | LLMPeripheral que genera lenguaje SIN LLM usando patrones, memoria y templates. Sprint 3. |
| **EnhancedPatternSpeaker** | PatternSpeaker mejorado con destilación de respuestas, retrieval de cápsulas y dialog state tracking. Sprint 3.6. |
| **ZoePackager** | Empaquetador de organismos ZOE en formato .zoe. Sprint 3. |
| **ZoeRuntime** | Runtime mínimo incluido en .zoe para ejecutar sin dependencias. Sprint 3.5. |
| **ResponseDistiller** | Captura respuestas buenas de LLMs (GPT-4o, Claude) y las almacena para reutilizar sin LLM. Sprint 3.6. |
| **CapsuleRetriever** | Recupera knowledge relevante de las cápsulas para enriquecer respuestas. Sprint 3.6. |
| **DialogStateTracker** | Rastrea emoción, tema y turnos de conversación. Sprint 3.6. |
| **LanguageDetector** | Detecta idioma del usuario por heurística de stopwords (<10ms). Sprint 1. |
| **LanguageProfile** | System prompts, reflex maps y validators por idioma. Sprint 1. |
| **VLMPeripheral** | LLM con capacidad de visión (GPT-4o, Claude, LLaVA). Sprint 2. |
| **VisionSense** | Sentido que procesa imágenes y genera Observations. Sprint 2. |
| **VoiceInputSense** | Sentido STT con Whisper que transcribe audio a texto. Sprint 2. |
| **VoiceActuator** | Actuador TTS con Piper que genera voz natural local. Sprint 2. |
| **VoiceFirstMode** | Conversación natural por voz tipo Her con wake word e interrupción. Sprint 4. |
| **WakeWordDetector** | Detecta "Hey ZOE" para activar escucha. Sprint 4. |
| **VoiceActivityDetector** | Detecta cuándo el usuario habla/termina (VAD). Sprint 4. |
| **InterruptionHandler** | Maneja interrupciones del usuario durante la respuesta de ZOE. Sprint 4. |
| **TelegramBridge** | Puente entre Telegram y ZOE. Sprint 1. |
| **PWA** | Progressive Web App. Dashboard instalable como app móvil. Sprint 1. |
| **DistilledResponse** | Respuesta capturada de un LLM de calidad para reutilizar sin LLM. Sprint 3.6. |
| **VoiceConfig** | Configuración del Voice-first mode (wake word, STT, TTS, VAD). Sprint 4. |
| **.zmap** | Tensor Optimization Map. Metadata que acompaña al GGUF con estrategias de carga optimizadas. Sprint 5. |
| **Cognitive Prefetch Layer (CPL)** | Capa que usa ACD + memory + capsules para preparar inferencia antes de llamar al LLM. Sprint 5. |
| **Tensor Prediction Engine (TPE)** | Predice qué capas del modelo necesitará según ACD + intención + dominio. Sprint 5. |
| **ZMAPLoader** | Carga archivos .zmap desde disco con cache. Sprint 5. |
| **RAMStrategy** | Estrategia de carga para una cantidad de RAM específica. Sprint 5. |

---

*ZOE V1.8.0 — Glossary*
