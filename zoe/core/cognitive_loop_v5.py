"""
ZOE v1.0 — Cognitive Loop V5 (Fase 5: ACD + Streaming)

Extiende CognitiveLoopV4 con:
- Adaptive Cognitive Depth (ACD): pre-clasifica el input en L0/L1/L2/L3
- Cognitive Cache: idempotencia para entradas repetidas
- Pipeline ramificado por nivel (L0 = <1s, L3 = full pipeline)
- Marca el nivel ACD en la trayectoria firmada (auditable)
- Streaming parcial opcional vía Speaker.generate_streaming()

Sin desconstruir V4. Si no se pasa DepthClassifier, comportamiento = V4.

Compatibilidad:
- CognitiveLoopV5(deep_consolidation=..., persistent_memory=...) == V4
- CognitiveLoopV5(depth_classifier=...) → ACD activo
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, List, Dict, Any, AsyncIterator

from .cognitive_loop_v4 import CognitiveLoopV4
from .cognitive_loop import Thought, Observation
from .depth_classifier import DepthClassifier, CognitiveLevel, ClassificationResult
from .cognitive_cache import CognitiveCache

logger = logging.getLogger(__name__)

# ============================================================
# Componentes opcionales — lazy initialization con graceful fallback
# ============================================================

# MentorAgent: evalúa pensamientos autónomos contra criterios de crecimiento
try:
    from .mentor import MentorAgent, MentorConfig
except ImportError:
    MentorAgent = None  # type: ignore
    MentorConfig = None  # type: ignore
    logger.debug("MentorAgent no disponible (mentor.py no encontrado)")

# LanguageDetector: detecta idioma del usuario (<10ms, sin LLM)
try:
    from .language_detector import LanguageDetector, LANGUAGE_PROFILES
except ImportError:
    LanguageDetector = None  # type: ignore
    LANGUAGE_PROFILES = {}  # type: ignore
    logger.debug("LanguageDetector no disponible (language_detector.py no encontrado)")

# CognitiveOptimizationLayer: prefetch cognitivo, TPE, ZMAP
try:
    from .cognitive_optimization import (
        CognitivePrefetchLayer,
        TensorPredictionEngine,
        ZMAPLoader,
        PrefetchResult,
    )
except ImportError:
    CognitivePrefetchLayer = None  # type: ignore
    TensorPredictionEngine = None  # type: ignore
    ZMAPLoader = None  # type: ignore
    PrefetchResult = None  # type: ignore
    logger.debug("CognitivePrefetchLayer no disponible (cognitive_optimization.py no encontrado)")


# Respuestas reflejas para L0 (sin llamar al LLM)
_L0_REFLEX_RESPONSES = {
    "hola": "Hola. Estoy aquí.",
    "holaa": "Hola. Estoy aquí.",
    "hello": "Hola. Estoy aquí.",
    "hi": "Hola.",
    "hey": "Ey.",
    "buenas": "Buenas.",
    "buenosdias": "Buenos días.",
    "buenastardes": "Buenas tardes.",
    "buenasnoches": "Buenas noches.",
    "adios": "Hasta pronto.",
    "adiós": "Hasta pronto.",
    "chao": "Chao.",
    "bye": "Bye.",
    "hastaluego": "Hasta luego.",
    "nosvemos": "Nos vemos.",
    "ok": "Vale.",
    "okay": "Ok.",
    "vale": "Vale.",
    "venga": "Venga.",
    "bien": "Bien.",
    "genial": "Genial.",
    "perfecto": "Perfecto.",
    "entendido": "Entendido.",
    "claro": "Claro.",
    "sip": "Sip.",
    "sí": "Sí.",
    "si": "Sí.",
    "no": "No.",
    "nop": "Nop.",
    "gracias": "De nada.",
    "thanks": "You're welcome.",
    "muchasgracias": "Gracias a ti.",
    "denada": "👍",
    "k": "Ok.",
    "kk": "Ok.",
    "jeje": "Jeje.",
    "jaja": "Jaja.",
}


class CognitiveLoopV5(CognitiveLoopV4):
    """
    Bucle cognitivo Fase 5 — Adaptive Cognitive Depth.

    Añade sobre V4:
    - DepthClassifier pre-clasifica cada input
    - Cognitive Cache para respuestas idempotentes
    - Pipeline ramificado:
        L0_REFLEX    → respuesta directa sin LLM (cache o tabla refleja)
        L1_FAST      → Perceiver + Memorialist + Speaker (3 sub-agentes)
        L2_STANDARD  → pipeline Fase 0 completo
        L3_DEEP      → pipeline Fase 3 completo (12 sub-agentes + meta-cog)
    - Marca nivel ACD en TrajectoryChain (auditable)
    - Estadísticas por nivel
    """

    # Sprint 5.23 F3-1 (BUG-012 fix) — ACD cloud routing.
    # Mapas: nivel ACD → { backend_class_name → model_tag }.
    # Cuando no hay ``model_profile_router`` (backends cloud), se aplican
    # estos tags automáticamente por nivel cognitivo. Los tags son modelos
    # estándar de cada proveedor (no IQ2_M locales).
    #
    # Lógica:
    #   L1_FAST       → modelo más barato (haiku/mini/gpt-4o-mini/MiniMax-M3)
    #   L2_STANDARD   → modelo intermedio (sonnet/gpt-4o/MiniMax-M3)
    #   L3_DEEP/MAX   → modelo más potente (opus/o1/MiniMax-M3)
    #
    # Nota: MiniMax-M3 se deja en todos los niveles porque es el único
    # modelo disponible en la API de MiniMax (no hay variantes baratas/caras).
    _CLOUD_MODEL_ASSIGNMENTS: Dict[str, Dict[str, str]] = {
        "L1_FAST": {
            "AnthropicPeripheral": "claude-3-5-haiku-20241022",
            "OpenAICompatiblePeripheral": "gpt-4o-mini",
            "OpenAIPeripheral": "gpt-4o-mini",
        },
        "L2_STANDARD": {
            "AnthropicPeripheral": "claude-sonnet-4-20250514",
            "OpenAICompatiblePeripheral": "gpt-4o",
            "OpenAIPeripheral": "gpt-4o",
        },
        "L3_DEEP": {
            "AnthropicPeripheral": "claude-opus-4-20250514",
            "OpenAICompatiblePeripheral": "gpt-4o",
            "OpenAIPeripheral": "gpt-4o",
        },
        "L3_MAXIMUM": {
            "AnthropicPeripheral": "claude-opus-4-20250514",
            "OpenAICompatiblePeripheral": "o1",
            "OpenAIPeripheral": "o1",
        },
    }

    def __init__(
        self,
        *args,
        # Fase 5 componentes (opcionales)
        depth_classifier: Optional[DepthClassifier] = None,
        cognitive_cache: Optional[CognitiveCache] = None,
        # Sprint 5.7: routing ACD→modelo
        model_profile_router: Optional[Any] = None,
        active_profile: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Fase 5
        self.depth_classifier = depth_classifier
        self.cognitive_cache = cognitive_cache

        # Sprint 5.7 — ModelProfileRouter (ACD → modelo IQ2_M)
        self.model_profile_router = model_profile_router
        self._active_profile = active_profile
        self._router_swaps: int = 0
        self._router_skips: int = 0
        self._last_routed_tag: Optional[str] = None

        # Estadísticas Fase 5 + Sprint 5.7
        self.acd_classifications: int = 0
        self.acd_level_counts: Dict[str, int] = {
            "L0_REFLEX": 0, "L1_FAST": 0, "L2_STANDARD": 0,
            "L3_DEEP": 0, "L3_MAXIMUM": 0,
        }
        self.acd_cache_hits: int = 0
        self.acd_responses_by_level: Dict[str, int] = {
            "L0_REFLEX": 0, "L1_FAST": 0, "L2_STANDARD": 0,
            "L3_DEEP": 0, "L3_MAXIMUM": 0,
        }
        self.acd_latency_by_level: Dict[str, List[float]] = {
            "L0_REFLEX": [], "L1_FAST": [], "L2_STANDARD": [],
            "L3_DEEP": [], "L3_MAXIMUM": [],
        }

        # Última clasificación (para auditoría)
        self.last_classification: Optional[ClassificationResult] = None

        # ============================================================
        # Componentes opcionales — lazy initialization
        # ============================================================

        # Sprint 5.10 C8 — LanguageDetector (cacheado por sesión)
        self._language_detector: Optional[Any] = None
        if LanguageDetector is not None:
            try:
                self._language_detector = LanguageDetector()
                logger.info("LanguageDetector inicializado")
            except Exception as e:
                logger.debug(f"LanguageDetector init failed (non-fatal): {e}")
                self._language_detector = None

        # MentorAgent — evaluación de pensamientos autónomos
        self._mentor: Optional[Any] = None
        if MentorAgent is not None:
            try:
                self._mentor = MentorAgent()
                logger.info("MentorAgent inicializado")
            except Exception as e:
                logger.debug(f"MentorAgent init failed (non-fatal): {e}")
                self._mentor = None

        # Cognitive Prefetch Layer — optimización de inferencia
        self._cpl: Optional[Any] = None
        if CognitivePrefetchLayer is not None:
            try:
                # Buscar ModelBus y PatternSpeaker en subagentes (si existen)
                model_bus = getattr(self, "model_bus", None)
                pattern_speaker = self._find_subagent("pattern")
                self._cpl = CognitivePrefetchLayer(
                    model_bus=model_bus,
                    pattern_speaker=pattern_speaker,
                )
                logger.info("CognitivePrefetchLayer inicializado")
            except Exception as e:
                logger.debug(f"CognitivePrefetchLayer init failed (non-fatal): {e}")
                self._cpl = None

        # Sprint 5.23 F0-5 — WebSearchActuator para que ZOE busque en internet
        # cuando el usuario lo pida. Lazy init: solo se carga si el módulo
        # está disponible (siempre lo está — usa solo stdlib).
        self._web_search: Optional[Any] = None
        try:
            from ..peripherals.web_search import WebSearchActuator
            self._web_search = WebSearchActuator(max_results=5, timeout=15)
            logger.info("WebSearchActuator inicializado (DuckDuckGo Lite)")
        except Exception as e:
            logger.debug(f"WebSearchActuator init failed (non-fatal): {e}")
            self._web_search = None

        # System prompt del idioma detectado (para el Speaker)
        self._current_system_prompt: Optional[str] = None

    async def process_user_input_acd(self, user_input: str) -> Dict[str, Any]:
        """
        Procesa un input de usuario usando ACD.

        Este es el MÉODO PRINCIPAL que debería usarse para responder al usuario.
        Reemplaza el patrón de "inyectar en UserInputSense y esperar al tick".

        Args:
            user_input: texto del usuario

        Returns:
            Dict con:
                - response: str (respuesta de ZOE)
                - level: CognitiveLevel.value
                - cache_hit: bool
                - latency_ms: float
                - classification: dict
                - trajectory_hash: Optional[str]
        """
        if not self.depth_classifier:
            # Sin ACD: comportamiento legacy (delegar a V4)
            return await self._legacy_process(user_input)

        start = time.time()

        # 1. Clasificar
        classification = self.depth_classifier.classify(user_input)
        self.last_classification = classification
        self.acd_classifications += 1
        self.acd_level_counts[classification.level.value] += 1

        level = classification.level

        # 1a. Sprint 5.10 C8 — Detección de idioma (cacheado por sesión)
        detected_language = None
        if hasattr(self, '_language_detector') and self._language_detector:
            try:
                from .language_detector import LanguageDetector, LANGUAGE_PROFILES
                detected_language = self._language_detector.detect(user_input)
                # Guardar el system prompt del idioma detectado para el Speaker
                if detected_language and detected_language in LANGUAGE_PROFILES:
                    self._current_system_prompt = LANGUAGE_PROFILES[detected_language].system_prompt_base
            except Exception as e:
                logger.debug(f"Language detection failed: {e}")

        # 1b. Sprint 5.7 — Routing ACD→modelo (hot-swap del LLM)
        # Si hay ModelProfileRouter configurado, preguntarle qué modelo usar
        # para este nivel ACD. Solo para L1+ (L0_REFLEX no toca LLM).
        routed_tag: Optional[str] = None
        if self.model_profile_router and level != CognitiveLevel.L0_REFLEX:
            try:
                assignment = self.model_profile_router.get_model_for_acd(
                    acd_level=level.value,
                    profile=self._active_profile,
                )
                if assignment and hasattr(assignment, "model_tag"):
                    routed_tag = assignment.model_tag
                    # Hot-swap del LLM en el speaker si el modelo cambió
                    # y no es "pattern" (pattern se maneja aparte)
                    if routed_tag and routed_tag != "pattern":
                        # Buscar el speaker en los subagentes
                        speaker = self._find_speaker()
                        # Sprint 5.7.2 FIX: Speaker guarda el LLM en self.llm (no self.llm_peripheral)
                        if speaker:
                            llm_attr = getattr(speaker, "llm", None) or getattr(speaker, "llm_peripheral", None)
                            if llm_attr:
                                current_model = getattr(llm_attr, "model", None)
                                if current_model != routed_tag:
                                    # Hot-swap mutando el modelo del OllamaPeripheral existente
                                    # (más rápido que crear uno nuevo; Ollama recarga solo si hace falta)
                                    try:
                                        llm_attr.model = routed_tag
                                        self._router_swaps += 1
                                        self._last_routed_tag = routed_tag
                                        logger.info(
                                            f"ACD router: {level.value} → model '{routed_tag}' "
                                            f"(was '{current_model}')"
                                        )
                                    except Exception as e:
                                        logger.debug(f"ACD router swap failed: {e}")
                                        self._router_skips += 1
                                else:
                                    self._router_skips += 1
                            else:
                                self._router_skips += 1
                    elif routed_tag == "pattern":
                        # Pattern fallback — no swap, dejar que el speaker actual responda
                        self._router_skips += 1
                else:
                    self._router_skips += 1
            except Exception as e:
                logger.debug(f"ACD router error (non-fatal): {e}")
                self._router_skips += 1
        elif level != CognitiveLevel.L0_REFLEX:
            # Sprint 5.23 F3-1 (BUG-012 fix): ACD cloud routing.
            # Cuando no hay ``model_profile_router`` (backends cloud como
            # Anthropic/OpenAI/MiniMax), aplicamos asignaciones por defecto
            # según el nivel ACD. Esto permite que MiniMax-M3 (L1) y modelos
            # más potentes (L3) se enruten automáticamente sin tocar código.
            # Tabla de modelos baratos/carisimos por proveedor cloud.
            cloud_assignments = self._CLOUD_MODEL_ASSIGNMENTS.get(level.value)
            if cloud_assignments:
                speaker = self._find_speaker()
                if speaker:
                    llm_attr = getattr(speaker, "llm", None) or getattr(speaker, "llm_peripheral", None)
                    if llm_attr:
                        # Detectar backend por tipo
                        backend_name = type(llm_attr).__name__
                        target_model = cloud_assignments.get(backend_name)
                        if target_model:
                            current_model = getattr(llm_attr, "model", None)
                            if current_model != target_model:
                                try:
                                    llm_attr.model = target_model
                                    self._router_swaps += 1
                                    self._last_routed_tag = target_model
                                    logger.info(
                                        f"ACD cloud router: {level.value} → "
                                        f"{backend_name} '{target_model}' "
                                        f"(was '{current_model}')"
                                    )
                                except Exception as e:
                                    logger.debug(f"ACD cloud swap failed: {e}")
                                    self._router_skips += 1
                            else:
                                self._router_skips += 1
            else:
                self._router_skips += 1

        # 2. Cache lookup
        cache_hit = False
        cached = None
        if self.cognitive_cache and level in (CognitiveLevel.L0_REFLEX, CognitiveLevel.L1_FAST):
            cached = self.cognitive_cache.get(classification.cache_key)
            if cached is not None:
                cache_hit = True
                self.acd_cache_hits += 1

        # 3. Ejecutar pipeline según nivel
        mentor_intervention_data: Optional[Dict[str, Any]] = None
        if cache_hit:
            response = cached
            trajectory_hash = None  # no se registra mutación si cache hit
        else:
            if level == CognitiveLevel.L0_REFLEX:
                response, trajectory_hash = await self._process_l0(user_input, classification)
            elif level == CognitiveLevel.L1_FAST:
                response, trajectory_hash, mentor_intervention_data = await self._process_l1(user_input, classification)
            elif level == CognitiveLevel.L2_STANDARD:
                response, trajectory_hash, mentor_intervention_data = await self._process_l2(user_input, classification)
            elif level == CognitiveLevel.L3_MAXIMUM:
                # Sprint 5.7: L3_MAXIMUM usa el mismo pipeline que L3_DEEP
                # pero el router (si está activo) habrá cargado el modelo 72B
                response, trajectory_hash = await self._process_l3(user_input, classification)
            else:  # L3_DEEP
                response, trajectory_hash = await self._process_l3(user_input, classification)

            # Guardar en cache si procede
            if self.cognitive_cache and not cache_hit:
                self.cognitive_cache.put(
                    classification.cache_key, response, level.value
                )

        latency_ms = (time.time() - start) * 1000
        self.acd_responses_by_level[level.value] += 1
        self.acd_latency_by_level[level.value].append(latency_ms)
        # Mantener solo las últimas 50 muestras
        if len(self.acd_latency_by_level[level.value]) > 50:
            self.acd_latency_by_level[level.value] = self.acd_latency_by_level[level.value][-50:]

        # 4. Almacenar en memoria (siempre)
        if hasattr(self, 'memory') and self.memory:
            try:
                self.memory.add(
                    content=f"User: {user_input[:100]}",
                    type="episodic",
                    confidence=0.9,
                    salience=0.5 + classification.score * 0.5,
                    provenance=f"acd:{level.value}",
                )
                self.memory.add(
                    content=f"ZOE: {response[:100]}",
                    type="episodic",
                    confidence=level.default_confidence,
                    salience=0.6,
                    provenance=f"acd:{level.value}:response",
                )
            except Exception as e:
                logger.debug(f"Memory add failed: {e}")

        return {
            "response": response,
            "level": level.value,
            "score": classification.score,
            "reasons": classification.reasons,
            "cache_hit": cache_hit,
            "latency_ms": round(latency_ms, 2),
            "trajectory_hash": trajectory_hash,
            "cost": level.cost,
            "confidence": level.default_confidence,
            # Sprint 5.10 C8 — idioma detectado
            "language": detected_language.value if detected_language else None,
            # Sprint 5.23 F1-8 — mentor intervention visible al usuario
            "mentor_intervention": mentor_intervention_data,
        }

    async def _process_l0(
        self, user_input: str, classification: ClassificationResult
    ) -> tuple[str, Optional[str]]:
        """
        L0 REFLEX — respuesta sin LLM.

        - Lookup en tabla de reflejos
        - Si no match, respuesta genérica corta
        - Marca mutación de bajo coste en trayectoria
        """
        token = classification.normalized_text.rstrip(".!? ")
        response = _L0_REFLEX_RESPONSES.get(token)

        if not response:
            # Si es un token L0 sin entrada específica, respuesta genérica
            response = "Vale. Te escucho."

        # Marcar en trayectoria (coste mínimo)
        trajectory_hash = self._register_acd_mutation(
            level=CognitiveLevel.L0_REFLEX,
            user_input=user_input,
            response=response,
            classification=classification,
        )

        return response, trajectory_hash

    async def _process_l1(
        self, user_input: str, classification: ClassificationResult
    ) -> tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """
        L1 FAST — Perceiver + Memorialist + Speaker.

        Solo 3 sub-agentes, sin Global Workspace ni meta-cog.
        Recupera memoria relevante y responde.

        Sprint 5.23 F1-8: retorna también ``mentor_intervention_data``
        para que el caller (``process_user_input_acd``) lo incluya en
        el dict de respuesta y el dashboard pueda mostrarlo al usuario.
        """
        # Buscar memoria relevante
        memories = []
        if hasattr(self, 'memory') and self.memory:
            try:
                relevant = self.memory.search(user_input, n=3)
                memories = [m.content[:150] for m in relevant] if relevant else []
            except Exception:
                pass

        # Sprint 5.23 F0-5 — WebSearch si el usuario lo pide
        web_results: List[str] = []
        if self._web_search is not None:
            try:
                if self._web_search.should_use_search(user_input):
                    results = await self._web_search.search(user_input)
                    web_results = [
                        f"{r.title}: {r.url}" for r in results[:3] if r.url
                    ]
            except Exception as e:
                logger.debug(f"WebSearch L1 failed (non-fatal): {e}")

        # Buscar Speaker
        speaker = self._find_subagent("speaker")
        if not speaker:
            # Fallback: simple template
            response = f"Recibido. {user_input[:50]}..."
            return response, self._register_acd_mutation(
                CognitiveLevel.L1_FAST, user_input, response, classification
            ), None

        # === Cognitive Prefetch Layer (CPL) — Sprint 5 OPT ===
        # Pre-cargar modelo/contexto ANTES de llamar al Speaker
        cpl_result = None
        if self._cpl is not None:
            try:
                cpl_result = await self._cpl.prefetch(
                    acd_level="L1_FAST",
                    user_input=user_input,
                    memory=getattr(self, "memory", None),
                    metabolic_state=getattr(self, "metabolic_state", None),
                )
                # Si CPL devuelve pattern_response, usarla directamente
                if cpl_result and getattr(cpl_result, "pattern_response", None):
                    response = cpl_result.pattern_response
                    logger.debug(f"L1: CPL pattern shortcut used")
                    # Saltar a mentor + registro
                    if self._mentor is not None:
                        try:
                            mentor_intervention = self._mentor.evaluate_thought(response)
                            if mentor_intervention:
                                logger.info(
                                    f"Mentor L1: {mentor_intervention.get('type', 'unknown')} — "
                                    f"{mentor_intervention.get('message', '')[:80]}"
                                )
                        except Exception as me:
                            logger.debug(f"Mentor L1 evaluation failed: {me}")
                    trajectory_hash = self._register_acd_mutation(
                        CognitiveLevel.L1_FAST, user_input, response, classification,
                        metadata_extra={"cpl": "pattern_shortcut"} if cpl_result else None
                    )
                    return response, trajectory_hash, None
            except Exception as e:
                logger.debug(f"CPL L1 prefetch failed (non-fatal): {e}")

        # Generar respuesta
        try:
            context = {
                "action": "respond_to_user",
                "decision": {"user_content": user_input},
                "recent_observations": [{"source": "user", "content": user_input}],
                "recent_thoughts": [],
                "state": self.state.to_dict() if self.state else {},
                "surprise": 0.2,
                "acd_level": "L1_FAST",
                "relevant_memories": memories,
                "web_results": web_results,
            }
            # Inyectar system prompt del idioma si está disponible
            if self._current_system_prompt:
                context["system_prompt_override"] = self._current_system_prompt
            # Inyectar contexto pre-construido por CPL si existe
            if cpl_result and getattr(cpl_result, "context_built", False):
                context["cpl_context"] = getattr(cpl_result, "predicted_layers", {})

            response = await speaker.generate_thought(context)
            response = speaker._sanitize(response) if hasattr(speaker, "_sanitize") else response
            if not response:
                response = f"Vale, te entiendo. {user_input[:30]}..."
        except Exception as e:
            logger.warning(f"L1 Speaker failed: {e}")
            response = f"Recibido. Procesando: {user_input[:50]}..."

        # === MentorAgent — evaluar pensamiento generado ===
        # Sprint 5.23 F1-8: capturar intervention para retornarla al caller
        # y que el dashboard la muestre al usuario.
        _mentor_intervention_data: Optional[Dict[str, Any]] = None
        if self._mentor is not None:
            try:
                mentor_intervention = self._mentor.evaluate_thought(response)
                if mentor_intervention:
                    logger.info(
                        f"Mentor L1: {mentor_intervention.get('type', 'unknown')} — "
                        f"{mentor_intervention.get('message', '')[:80]}"
                    )
                    _mentor_intervention_data = mentor_intervention
                    # Si la intervención es crítica, adjuntar warning al log
                    if mentor_intervention.get("severity") == "critical":
                        logger.warning(f"Mentor CRITICAL L1: pensamiento desviado")
            except Exception as me:
                logger.debug(f"Mentor L1 evaluation failed: {me}")

        trajectory_hash = self._register_acd_mutation(
            CognitiveLevel.L1_FAST, user_input, response, classification
        )
        return response, trajectory_hash, _mentor_intervention_data

    async def _process_l2(
        self, user_input: str, classification: ClassificationResult
    ) -> tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """
        L2 STANDARD — pipeline Fase 0 completo.

        Perceiver, Forecaster, Speaker, Critic. Sin los 8 sub-agentes de Fase 2.
        """
        # Inyectar en UserInputSense si existe (para que entre al bucle)
        speaker = self._find_subagent("speaker")
        perceiver = self._find_subagent("perceiver")

        memories = []
        if hasattr(self, 'memory') and self.memory:
            try:
                relevant = self.memory.search(user_input, n=5)
                memories = [m.content[:200] for m in relevant] if relevant else []
            except Exception:
                pass

        if not speaker:
            response = f"Procesando tu mensaje: {user_input[:50]}..."
            return response, self._register_acd_mutation(
                CognitiveLevel.L2_STANDARD, user_input, response, classification
            ), None

        # === Cognitive Prefetch Layer (CPL) — Sprint 5 OPT ===
        cpl_result = None
        if self._cpl is not None:
            try:
                cpl_result = await self._cpl.prefetch(
                    acd_level="L2_STANDARD",
                    user_input=user_input,
                    memory=getattr(self, "memory", None),
                    metabolic_state=getattr(self, "metabolic_state", None),
                )
                if cpl_result and getattr(cpl_result, "pattern_response", None):
                    response = cpl_result.pattern_response
                    logger.debug(f"L2: CPL pattern shortcut used")
                    _mi: Optional[Dict[str, Any]] = None
                    if self._mentor is not None:
                        try:
                            mentor_intervention = self._mentor.evaluate_thought(response)
                            if mentor_intervention:
                                logger.info(
                                    f"Mentor L2: {mentor_intervention.get('type', 'unknown')} — "
                                    f"{mentor_intervention.get('message', '')[:80]}"
                                )
                                _mi = mentor_intervention
                        except Exception as me:
                            logger.debug(f"Mentor L2 evaluation failed: {me}")
                    trajectory_hash = self._register_acd_mutation(
                        CognitiveLevel.L2_STANDARD, user_input, response, classification,
                        metadata_extra={"cpl": "pattern_shortcut"} if cpl_result else None
                    )
                    return response, trajectory_hash, _mi
            except Exception as e:
                logger.debug(f"CPL L2 prefetch failed (non-fatal): {e}")

        try:
            # Perceiver interpreta (1 LLM call opcional)
            perceived_intent = None
            if perceiver and hasattr(perceiver, "generate_thought"):
                try:
                    perceived = await perceiver.generate_thought({
                        "action": "perceive",
                        "recent_observations": [{"source": "user", "content": user_input}],
                        "state": self.state.to_dict() if self.state else {},
                        "surprise": 0.3,
                    })
                    perceived_intent = perceived[:150] if perceived else None
                except Exception:
                    pass

            # Speaker responde con contexto
            context = {
                "action": "respond_to_user",
                "decision": {"user_content": user_input},
                "recent_observations": [{"source": "user", "content": user_input}],
                "recent_thoughts": [t.to_dict() for t in self.thoughts[-3:]],
                "state": self.state.to_dict() if self.state else {},
                "surprise": 0.3,
                "acd_level": "L2_STANDARD",
                "perceived_intent": perceived_intent,
                "relevant_memories": memories,
                "physics": self.physics.summary() if hasattr(self, 'physics') and self.physics else "",
                "tensions": self.tensions.summary() if hasattr(self, 'tensions') and self.tensions else "",
            }
            # Inyectar system prompt del idioma si está disponible
            if self._current_system_prompt:
                context["system_prompt_override"] = self._current_system_prompt
            # Inyectar contexto pre-construido por CPL si existe
            if cpl_result and getattr(cpl_result, "context_built", False):
                context["cpl_context"] = getattr(cpl_result, "predicted_layers", {})

            response = await speaker.generate_thought(context)
            response = speaker._sanitize(response) if hasattr(speaker, "_sanitize") else response
            if not response:
                response = f"Procesando: {user_input[:50]}..."

            # Critic evalúa (1 LLM call opcional)
            # Sprint 5.23 F1-5 (BUG-022 fix): pasar ``used_memory_ids`` en
            # el context para que ``Critic.evaluate`` pueda comprobar
            # cuarentena. Antes el context no llevaba este campo y la
            # comprobación era no-op.
            critic = self._find_subagent("critic")
            if critic and hasattr(critic, "generate_thought"):
                try:
                    # IDs de memorias relevantes usadas para responder
                    used_memory_ids = []
                    if hasattr(self, 'memory') and self.memory:
                        try:
                            relevant = self.memory.search(user_input, n=5)
                            used_memory_ids = [m.id for m in relevant if hasattr(m, 'id')]
                        except Exception:
                            pass
                    critique = await critic.generate_thought({
                        "action": "critique",
                        "recent_observations": [{"source": "user", "content": user_input}],
                        "recent_thoughts": [{"content": response, "surprise": 0.3, "trigger": "respond_to_user"}],
                        "state": self.state.to_dict() if self.state else {},
                        "surprise": 0.3,
                        "used_memory_ids": used_memory_ids,
                    })
                    # Si la crítica es muy negativa, regenerar
                    if critique and ("inadecuada" in critique.lower() or "incorrect" in critique.lower()):
                        response = await speaker.generate_thought({**context, "critique": critique})
                        response = speaker._sanitize(response) if hasattr(speaker, "_sanitize") else response
                except Exception:
                    pass

            # Sprint 5.24 F1v2-1 (BUG-002 fix): invocar ``Learner.propose_learning``
            # para que el conocimiento nuevo del usuario se valide con
            # EpistemicValidator y, si procede, se añada a KnowledgeQuarantine.
            # Antes ``propose_learning`` solo se invocaba desde el background
            # tick con surprise > 0.5; ahora también desde el chat L2 cuando
            # el usuario comparte conocimiento factual.
            learner = getattr(self, "learner", None) or self._find_subagent("learner")
            if learner and hasattr(learner, "propose_learning"):
                try:
                    # Heurística simple: si el input contiene afirmaciones
                    # factuales (verbos en presente + sustantivos técnicos),
                    # proponer aprendizaje. Evitamos invocar para saludos
                    # o preguntas cortas.
                    if (
                        len(user_input) > 30
                        and any(kw in user_input.lower() for kw in [
                            " es ", " son ", " significa", " porque ", " debido a",
                            " siempre ", " nunca ", " todos ", " is ", " are ",
                            " means ", " because ",
                        ])
                    ):
                        learner.propose_learning(
                            content=user_input[:500],
                            memory_type="semantic",
                            confidence=0.6,
                            source="user:chat",
                        )
                except Exception as e:
                    logger.debug(f"Learner.propose_learning failed (non-fatal): {e}")
        except Exception as e:
            logger.warning(f"L2 pipeline failed: {e}")
            response = f"Procesando tu mensaje. {user_input[:30]}..."

        # === MentorAgent — evaluar pensamiento generado ===
        # Sprint 5.23 F1-8: capturar intervention para retornarla al caller.
        _mentor_intervention_data_l2: Optional[Dict[str, Any]] = None
        if self._mentor is not None:
            try:
                mentor_intervention = self._mentor.evaluate_thought(response)
                if mentor_intervention:
                    logger.info(
                        f"Mentor L2: {mentor_intervention.get('type', 'unknown')} — "
                        f"{mentor_intervention.get('message', '')[:80]}"
                    )
                    _mentor_intervention_data_l2 = mentor_intervention
                    if mentor_intervention.get("severity") == "critical":
                        logger.warning(f"Mentor CRITICAL L2: pensamiento desviado")
            except Exception as me:
                logger.debug(f"Mentor L2 evaluation failed: {me}")

        trajectory_hash = self._register_acd_mutation(
            CognitiveLevel.L2_STANDARD, user_input, response, classification
        )
        return response, trajectory_hash, _mentor_intervention_data_l2

    async def _process_l3(
        self, user_input: str, classification: ClassificationResult
    ) -> tuple[str, Optional[str]]:
        """
        L3 DEEP — pipeline completo Fase 3.

        Los 12 sub-agentes + meta-cog + global workspace + active inference.
        Igual que el _tick de V3 pero con input explícito.
        """
        # === Cognitive Prefetch Layer (CPL) — Sprint 5 OPT ===
        cpl_result = None
        if self._cpl is not None:
            try:
                cpl_result = await self._cpl.prefetch(
                    acd_level="L3_DEEP",
                    user_input=user_input,
                    memory=getattr(self, "memory", None),
                    metabolic_state=getattr(self, "metabolic_state", None),
                    sensitive_domain=classification.score > 0.8 if classification else False,
                )
                if cpl_result and getattr(cpl_result, "pattern_response", None):
                    response = cpl_result.pattern_response
                    logger.debug(f"L3: CPL pattern shortcut used")
                    if self._mentor is not None:
                        try:
                            mentor_intervention = self._mentor.evaluate_thought(response)
                            if mentor_intervention:
                                logger.info(
                                    f"Mentor L3: {mentor_intervention.get('type', 'unknown')} — "
                                    f"{mentor_intervention.get('message', '')[:80]}"
                                )
                        except Exception as me:
                            logger.debug(f"Mentor L3 evaluation failed: {me}")
                    trajectory_hash = self._register_acd_mutation(
                        CognitiveLevel.L3_DEEP, user_input, response, classification,
                        metadata_extra={
                            "cpl": "pattern_shortcut",
                            "system": "system1",
                        }
                    )
                    return response, trajectory_hash
            except Exception as e:
                logger.debug(f"CPL L3 prefetch failed (non-fatal): {e}")

        # Recoger observaciones (incluyendo el input del usuario)
        observations = [Observation(
            timestamp=time.time(),
            source="user",
            content=user_input,
        )]

        # Predicción (World Model V2 si está)
        prediction = {"predicted": None, "confidence": 0.0}
        try:
            if self.world_model_v2:
                prediction = await self.world_model_v2.predict_next(observations)
            elif self.world_model:
                prediction = await self.world_model.predict_next(observations)
        except Exception as e:
            logger.debug(f"L3 predict failed: {e}")

        # Sorpresa
        surprise = 0.5  # L3 siempre implica cierta sorpresa
        try:
            if self.world_model_v2:
                surprise = await self.world_model_v2.compute_surprise(prediction, observations)
        except Exception:
            pass

        # Recolectar propuestas de TODOS los sub-agentes
        proposals = await self._collect_proposals(observations, surprise, prediction)

        # Global Workspace competition
        winners = self._workspace_compete(proposals)

        # Meta-cog
        use_system2 = self._evaluate_meta_cognition(winners, surprise)

        # Active Inference
        ai_action = self._consult_active_inference(observations, surprise)

        # Decidir
        decision = self._decide_v3(winners, surprise, observations, use_system2, ai_action)
        decision["should_act"] = True
        decision["action"] = "respond_to_user"
        decision["target_subagent"] = "speaker"
        decision["user_content"] = user_input
        # Inyectar system prompt del idioma y contexto CPL en la decisión
        if self._current_system_prompt:
            decision["system_prompt_override"] = self._current_system_prompt
        if cpl_result and getattr(cpl_result, "context_built", False):
            decision["cpl_context"] = getattr(cpl_result, "predicted_layers", {})

        # Verificar leyes
        law_action = self._build_law_action(decision, surprise)
        laws_passed, _ = self.laws.verify_action(law_action)
        if not laws_passed:
            decision["reason"] = "law_violation_overridden_for_user_response"

        # Actuar
        thought = await self._act_v3(decision, observations, surprise, winners)
        response = thought.content if thought else f"Procesando en profundidad: {user_input[:50]}..."

        # === MentorAgent — evaluar pensamiento generado ===
        if self._mentor is not None and thought:
            try:
                mentor_intervention = self._mentor.evaluate_thought(response)
                if mentor_intervention:
                    logger.info(
                        f"Mentor L3: {mentor_intervention.get('type', 'unknown')} — "
                        f"{mentor_intervention.get('message', '')[:80]}"
                    )
                    if mentor_intervention.get("severity") == "critical":
                        logger.warning(f"Mentor CRITICAL L3: pensamiento desviado")
            except Exception as me:
                logger.debug(f"Mentor L3 evaluation failed: {me}")

        # Broadcast
        self._broadcast_to_subagents(winners, decision, surprise)

        trajectory_hash = self._register_acd_mutation(
            CognitiveLevel.L3_DEEP, user_input, response, classification,
            metadata_extra={
                "system": "system2" if use_system2 else "system1",
                "winners": [w.subagent_name for w in winners[:3]],
                "surprise": surprise,
            }
        )
        return response, trajectory_hash

    def _register_acd_mutation(
        self,
        level: CognitiveLevel,
        user_input: str,
        response: str,
        classification: ClassificationResult,
        metadata_extra: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Registra mutación en TrajectoryChain con nivel ACD.

        Auditable: cada respuesta queda firmada con su nivel cognitivo.
        """
        if not self.trajectory_chain or not self.ontogenetic_motor:
            return None

        try:
            payload = {
                "user_input": user_input[:200],
                "response": response[:200],
                "acd_level": level.value,
                "score": classification.score,
                "reasons": classification.reasons[:3],
            }
            if metadata_extra:
                payload.update(metadata_extra)

            mutation = self.ontogenetic_motor.propose_mutation(
                type="respond_to_user",
                target="speaker",
                payload=payload,
                justification=f"ACD {level.value} response (score={classification.score:.2f})",
                provenance=f"acd:{level.value}",
                cost=level.cost,
                confidence=level.default_confidence,
            )
            self.ontogenetic_motor.apply_mutation(mutation)
            return mutation.hash
        except Exception as e:
            logger.debug(f"ACD trajectory mutation failed: {e}")
            return None

    def _find_subagent(self, name_prefix: str) -> Optional[Any]:
        """Encuentra un sub-agente por prefijo de nombre de clase."""
        for agent in self.subagents:
            cls_name = agent.__class__.__name__.lower()
            if cls_name.startswith(name_prefix.lower()[:6]):
                return agent
        return None

    def _find_speaker(self) -> Optional[Any]:
        """Sprint 5.7 — atajo para encontrar el Speaker."""
        return self._find_subagent("speaker")

    def get_router_stats(self) -> Dict[str, Any]:
        """Sprint 5.7 — estadísticas del ModelProfileRouter.

        Sprint 5.23 F3-1: ``enabled`` ahora también es True cuando hay
        ACD cloud routing activo (i.e., cuando hay un Speaker con LLM
        cloud configurado, aunque ``model_profile_router`` sea None).
        """
        # Sprint 5.23: detectar cloud routing
        cloud_routing_active = False
        speaker = self._find_speaker() if hasattr(self, "_find_speaker") else None
        if speaker:
            llm_attr = getattr(speaker, "llm", None) or getattr(speaker, "llm_peripheral", None)
            if llm_attr:
                backend_name = type(llm_attr).__name__
                if backend_name in (
                    "AnthropicPeripheral",
                    "OpenAICompatiblePeripheral",
                    "OpenAIPeripheral",
                ):
                    cloud_routing_active = True
        return {
            "enabled": self.model_profile_router is not None or cloud_routing_active,
            "mode": "ollama_profile" if self.model_profile_router else (
                "cloud" if cloud_routing_active else "disabled"
            ),
            "swaps": self._router_swaps,
            "skips": self._router_skips,
            "last_routed_tag": self._last_routed_tag,
            "active_profile": getattr(self._active_profile, "name", None)
                              if self._active_profile else None,
        }

    async def _legacy_process(self, user_input: str) -> Dict[str, Any]:
        """Comportamiento legacy (sin ACD) — para compatibilidad."""
        start = time.time()
        speaker = self._find_subagent("speaker")
        if not speaker:
            return {
                "response": "Sin speaker disponible.",
                "level": "LEGACY",
                "score": 0.0,
                "reasons": ["no_acd"],
                "cache_hit": False,
                "latency_ms": 0.0,
                "trajectory_hash": None,
                "cost": 0.0,
                "confidence": 0.5,
            }

        try:
            context = {
                "action": "respond_to_user",
                "decision": {"user_content": user_input},
                "recent_observations": [{"source": "user", "content": user_input}],
                "recent_thoughts": [],
                "state": self.state.to_dict() if self.state else {},
                "surprise": 0.3,
            }
            response = await speaker.generate_thought(context)
            response = speaker._sanitize(response) if hasattr(speaker, "_sanitize") else response
        except Exception as e:
            response = f"Error: {e}"

        latency_ms = (time.time() - start) * 1000
        return {
            "response": response,
            "level": "LEGACY",
            "score": 0.0,
            "reasons": ["no_acd"],
            "cache_hit": False,
            "latency_ms": round(latency_ms, 2),
            "trajectory_hash": None,
            "cost": 0.3,
            "confidence": 0.5,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas completas incluyendo Fase 5."""
        stats = super().get_stats()

        # Fase 5 stats
        stats["acd_classifications"] = self.acd_classifications
        stats["acd_level_counts"] = dict(self.acd_level_counts)
        stats["acd_cache_hits"] = self.acd_cache_hits
        stats["acd_responses_by_level"] = dict(self.acd_responses_by_level)

        # Latencia por nivel
        latency_stats = {}
        for level, samples in self.acd_latency_by_level.items():
            if samples:
                latency_stats[level] = {
                    "count": len(samples),
                    "avg_ms": round(sum(samples) / len(samples), 2),
                    "min_ms": round(min(samples), 2),
                    "max_ms": round(max(samples), 2),
                    "p50_ms": round(sorted(samples)[len(samples) // 2], 2),
                }
            else:
                latency_stats[level] = {"count": 0}
        stats["acd_latency_by_level"] = latency_stats

        if self.depth_classifier:
            stats["depth_classifier_stats"] = self.depth_classifier.get_stats()
        if self.cognitive_cache:
            stats["cognitive_cache_stats"] = self.cognitive_cache.get_stats()

        # Sprint 5.7.2 — Incluir stats del ACD Model Router en /stats
        stats["acd_router_stats"] = self.get_router_stats()

        # Sprint 5 OPT — Stats de componentes conectados
        # LanguageDetector stats
        if self._language_detector is not None:
            try:
                stats["language_detector"] = self._language_detector.get_stats()
            except Exception:
                stats["language_detector"] = {"enabled": False, "error": "stats_failed"}
        else:
            stats["language_detector"] = {"enabled": False}

        # MentorAgent stats
        if self._mentor is not None:
            try:
                stats["mentor"] = self._mentor.get_stats()
            except Exception:
                stats["mentor"] = {"enabled": False, "error": "stats_failed"}
        else:
            stats["mentor"] = {"enabled": False}

        # CognitivePrefetchLayer stats
        if self._cpl is not None:
            try:
                stats["cognitive_prefetch_layer"] = self._cpl.get_stats()
            except Exception:
                stats["cognitive_prefetch_layer"] = {"enabled": False, "error": "stats_failed"}
        else:
            stats["cognitive_prefetch_layer"] = {"enabled": False}

        return stats
