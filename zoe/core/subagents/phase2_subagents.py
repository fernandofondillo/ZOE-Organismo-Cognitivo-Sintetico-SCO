"""
ZOE v1.0 — Sub-agentes Fase 2 (8 nuevos para Society of Mind completo)

Completa los 12 sub-agentes de Society of Mind:
5. Memorialist — recupera memoria relevante de los 11 tipos
6. Learner — genera mutaciones de aprendizaje
7. Curator — mantiene memoria limpia (olvido activo, consolidación)
8. Creativity — genera hipótesis, combinaciones, analogías
9. CausalEngine — razona sobre causa-efecto
10. EmotionalMotor — genera marcadores emocionales funcionales
11. EthicalMotor — evalúa acciones contra 7 valores
12. ScientificEngine — genera teorías y diseña experimentos

Cada sub-agente:
- Lee de CognitiveFields para contexto
- Escribe en CognitiveFields sus contribuciones
- Usa LivingMemory para almacenar/recuperar
- Respeta las 6 leyes cognitivas
"""

from __future__ import annotations

import logging
import random
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class Memorialist:
    """Recupera memoria relevante de los 11 tipos según contexto."""

    def __init__(self, memory=None):
        self.memory = memory
        self._last_retrieval: List[Dict[str, Any]] = []

    async def retrieve_relevant(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recupera memorias relevantes para el contexto actual."""
        if not self.memory or self.memory.count() == 0:
            return []

        # Construir query desde contexto
        parts = []
        obs = context.get("recent_observations", [])
        for o in obs[-3:]:
            parts.append(o.get("content", ""))

        trigger = context.get("action", "")
        if trigger:
            parts.append(trigger)

        query = " ".join(parts)
        if not query:
            return []

        # Buscar en memoria
        results = self.memory.search(query, n=5)
        self._last_retrieval = [
            {"content": r.content, "type": r.type, "confidence": r.confidence}
            for r in results
        ]
        return self._last_retrieval

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento basado en memoria recuperada."""
        memories = await self.retrieve_relevant(context)
        if not memories:
            return ""

        # Sintetizar memoria en pensamiento
        top = memories[0]
        if top["confidence"] > 0.7:
            return f"Recuerdo algo relevante: {top['content'][:80]}. Mi confianza en esto es alta."
        else:
            return f"Tengo un recuerdo difuso sobre: {top['content'][:80]}. Necesito más evidencia."


class Learner:
    """Genera mutaciones de aprendizaje (propone al OntogeneticMotor).
    
    Fase 6A: integra EpistemicValidator para validar todo conocimiento
    nuevo antes de almacenarlo. Si la validación devuelve cuarentena, marca
    la mutación con metadata.quarantine=True para que Curator y Critic la
    filtren en contextos críticos.
    """

    def __init__(self, epistemic_validator=None, quarantine=None, cross_validator=None):
        self._pending_mutations: List[Dict[str, Any]] = []
        # Fase 6A: validador epistémico (opcional, para compatibilidad)
        self._validator = epistemic_validator
        self._quarantine = quarantine
        # Sprint 5.24 F1v2-3 (BUG-015 fix): CrossValidator opcional para
        # triple verificación cuando EpistemicValidator lo requiera.
        self._cross_validator = cross_validator
        # Estadísticas de validación
        self.validation_attempts = 0
        self.validation_accepted = 0
        self.validation_quarantined = 0
        self.validation_rejected = 0
        # Sprint 5.24 F1v2-3: contador de triple verificaciones
        self.triple_validations = 0
        # Sprint 5.7.4 — validadores de cápsulas
        self._capsule_validators: Dict[str, Any] = {}

    def set_epistemic_validator(self, validator, quarantine=None) -> None:
        """Inyecta el EpistemicValidator (lo llama CapsuleManager al inicializar)."""
        self._validator = validator
        self._quarantine = quarantine

    def register_validators(self, capsule_name: str, validators_module: Any) -> None:
        """Sprint 5.7.4 — Registra un módulo de validadores de una cápsula.

        Args:
            capsule_name: nombre de la cápsula
            validators_module: módulo Python con funciones de validación
        """
        self._capsule_validators[capsule_name] = validators_module
        logger.info(f"Learner: registered validators from capsule '{capsule_name}'")

    def propose_learning(
        self,
        content: str,
        memory_type: str = "episodic",
        confidence: float = 0.5,
        source: str = "learner",
        domain: str = None,
    ) -> Dict[str, Any]:
        """
        Propone una mutación de aprendizaje.
        
        Fase 6A: si hay EpistemicValidator, valida el contenido antes de
        proponerlo. El resultado de la validación afecta:
        - confidence (capado según source y domain)
        - quarantine (metadata para Curator/Critic)
        - status (REJECTED → no se propone la mutación)
        """
        # Fase 6A: validar si hay validator
        validation_result = None
        final_confidence = confidence
        quarantine_flag = False
        
        if self._validator and memory_type in ("semantic", "causal", "episodic"):
            self.validation_attempts += 1
            
            # Construir context para validación
            context = {}
            if hasattr(self, '_capsule_semantic') and self._capsule_semantic:
                context["capsule_semantic"] = self._capsule_semantic
            
            validation_result = self._validator.validate_new_knowledge(
                claim=content,
                source=source,
                context=context,
            )
            
            if validation_result.status.value == "rejected":
                self.validation_rejected += 1
                # No proponer la mutación; registrar rechazo
                return {
                    "type": "knowledge_rejected",
                    "target": memory_type,
                    "payload": {"content": content[:100]},
                    "justification": f"Rejected by EpistemicValidator: {validation_result.reason}",
                    "provenance": source,
                    "cost": 0.0,
                    "confidence": 0.0,
                    "rejected": True,
                    "rejection_reason": validation_result.reason,
                }
            
            # Aplicar confianza validada (puede ser menor)
            final_confidence = validation_result.confidence
            quarantine_flag = validation_result.quarantine

            # Sprint 5.24 F1v2-3 (BUG-015 fix): si EpistemicValidator retorna
            # NEEDS_TRIPLE_VALIDATION, invocar CrossValidator para triple
            # verificación. El resultado puede promover, rechazar, o mantener
            # en cuarentena.
            if (
                validation_result.status.value == "needs_triple"
                and self._cross_validator is not None
            ):
                self.triple_validations += 1
                try:
                    triple_result = self._cross_validator.verify_triple(
                        claim=content,
                        source=source,
                        context=context,
                    )
                    if triple_result is not None:
                        # Si triple_result.verdict == "promoted", aceptar
                        # Si triple_result.verdict == "rejected", rechazar
                        # Si triple_result.verdict == "quarantined", mantener
                        verdict = getattr(triple_result, "verdict", None) or (
                            triple_result.get("verdict") if isinstance(triple_result, dict) else None
                        )
                        if verdict == "promoted":
                            final_confidence = max(final_confidence, 0.75)
                            quarantine_flag = False
                            self.validation_accepted += 1
                        elif verdict == "rejected":
                            self.validation_rejected += 1
                            return {
                                "type": "knowledge_rejected",
                                "target": memory_type,
                                "payload": {"content": content[:100]},
                                "justification": f"Rejected by CrossValidator (triple): {verdict}",
                                "provenance": source,
                                "cost": 0.0,
                                "confidence": 0.0,
                                "rejected": True,
                                "rejection_reason": f"triple_validation_rejected",
                            }
                        # else: keep quarantine_flag as is
                except Exception as e:
                    logger.debug(f"CrossValidator.verify_triple failed (non-fatal): {e}")

            if quarantine_flag:
                self.validation_quarantined += 1
            else:
                self.validation_accepted += 1
        
        mutation = {
            "type": "add_memory",
            "target": memory_type,
            "payload": {"content": content},
            "justification": f"Aprendido desde {source}",
            "provenance": source,
            "cost": 0.1,
            "confidence": final_confidence,
            "metadata": {
                "quarantine": quarantine_flag,
                "domain": domain,
                "validation_status": validation_result.status.value if validation_result else None,
                "validation_reason": validation_result.reason if validation_result else None,
            },
        }
        
        # Fase 6A: registrar en cuarentena si procede
        if quarantine_flag and self._quarantine and validation_result.verification_plan:
            import hashlib
            entry_id = f"q_{hashlib.sha256(content.encode()).hexdigest()[:12]}"
            self._quarantine.add(
                entry_id=entry_id,
                claim=content,
                source=source,
                confidence=final_confidence,
                domain=validation_result.detected_domain,
                reason=validation_result.reason,
                verification_plan=validation_result.verification_plan,
            )
            mutation["metadata"]["quarantine_entry_id"] = entry_id
        
        self._pending_mutations.append(mutation)
        return mutation

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento sobre lo que debería aprender."""
        surprise = context.get("surprise", 0.0)
        observations = context.get("recent_observations", [])

        if surprise > 0.5 and observations:
            # Alta sorpresa = oportunidad de aprendizaje
            last_obs = observations[-1] if observations else {}
            content = last_obs.get("content", "algo inesperado")
            self.propose_learning(
                content=f"Sorpresa detectada: {content[:60]}",
                memory_type="episodic",
                confidence=min(0.8, 0.4 + surprise * 0.4),
                source="learner:surprise",
            )
            return f"He detectado algo sorprendente ({surprise:.2f}). Lo estoy registrando para aprender."

        if surprise < 0.1 and len(observations) > 3:
            return "El entorno es predecible. No hay mucho que aprender ahora."

        return ""

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del Learner con validación epistémica."""
        return {
            "pending_mutations": len(self._pending_mutations),
            "validation_attempts": self.validation_attempts,
            "validation_accepted": self.validation_accepted,
            "validation_quarantined": self.validation_quarantined,
            "validation_rejected": self.validation_rejected,
            "validator_active": self._validator is not None,
        }


class Curator:
    """Mantiene memoria limpia: olvido activo, consolidación, reorganización.
    
    Fase 6A: integra KnowledgeQuarantine para que la memoria que se use
    en contextos críticos excluya entradas en cuarentena, y para que la
    consolidación respete el ciclo de vida del conocimiento no validado.
    """

    def __init__(self, memory=None, quarantine=None):
        self.memory = memory
        # Fase 6A: cuarentena activa (opcional, para compatibilidad)
        self._quarantine = quarantine
        self._operations_run: int = 0
        # Estadísticas de cuarentena
        self.quarantine_filtered = 0
        self.quarantine_promoted_during_curate = 0
        self.quarantine_rejected_during_curate = 0

    def set_quarantine(self, quarantine) -> None:
        """Inyecta el KnowledgeQuarantine (lo llama CapsuleManager)."""
        self._quarantine = quarantine

    def get_safe_entries(
        self, query: str = None, n: int = 10, critical_context: bool = False
    ) -> List[Any]:
        """
        Devuelve entradas de memoria seguras para uso.
        
        Fase 6A: si critical_context=True, filtra las entradas en cuarentena.
        Esto es lo que deben usar Critic y Speaker cuando responden a usuarios
        en dominios sensibles.
        """
        if not self.memory:
            return []
        
        # Buscar entries
        if query:
            entries = self.memory.search(query, n=n * 2)  # pedir más por si filtramos
        else:
            entries = self.memory.all_entries()[-n * 2:]  # últimas
        
        # Convertir a dicts si es necesario
        entries_dicts = []
        for e in entries:
            if hasattr(e, 'to_dict'):
                d = e.to_dict()
            elif isinstance(e, dict):
                d = e
            else:
                # dataclass MemoryEntry
                d = {
                    "id": getattr(e, 'id', ''),
                    "content": getattr(e, 'content', ''),
                    "type": getattr(e, 'type', ''),
                    "confidence": getattr(e, 'confidence', 0.5),
                    "provenance": getattr(e, 'provenance', ''),
                    "metadata": getattr(e, 'metadata', {}),
                }
            entries_dicts.append(d)
        
        # Fase 6A: filtrar cuarentena si critical_context
        if critical_context and self._quarantine:
            filtered = []
            for entry in entries_dicts:
                entry_id = entry.get("id", "")
                if not self._quarantine.is_quarantined(entry_id):
                    filtered.append(entry)
                else:
                    self.quarantine_filtered += 1
            return filtered[:n]
        
        return entries_dicts[:n]

    async def curate(self) -> Dict[str, Any]:
        """Ejecuta una operación de curación de memoria.
        
        Fase 6A: durante la curación, también:
        - Limpia entries de cuarentena expiradas (cleanup_expired)
        - Marca entries en cuarentena como no-promovibles a semántica
        """
        if not self.memory or self.memory.count() < 5:
            return {"operation": "skip", "reason": "insufficient_memory"}
        
        result = self.memory.think()
        self._operations_run += 1
        
        # Fase 6A: limpieza de cuarentena expirada
        if self._quarantine:
            try:
                expired = self._quarantine.cleanup_expired()
                if expired > 0:
                    # Poda las entries de memoria asociadas a las expiradas
                    for qid, q_entry in list(self._quarantine._entries.items()):
                        if q_entry.status == "expired":
                            # Buscar y eliminar la memory entry correspondiente
                            for mem_entry in self.memory.all_entries():
                                mem_id = getattr(mem_entry, 'id', '')
                                if self._quarantine._memory_entry_map.get(mem_id) == qid:
                                    self.memory._entries.pop(mem_id, None)
                                    break
                    result["quarantine_expired_pruned"] = expired
                
                # Stats de cuarentena
                q_stats = self._quarantine.get_stats()
                result["quarantine_stats"] = q_stats
            except Exception as e:
                logger.warning(f"Curator: quarantine cleanup failed: {e}")
        
        return result

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento sobre el estado de la memoria."""
        if not self.memory:
            return ""

        count = self.memory.count()
        if count > 50:
            return f"Mi memoria tiene {count} entries. Debería consolidar y olvidar lo irrelevante."
        elif count > 20:
            return f"Memoria con {count} entries. En buen estado, pero vigilando."
        else:
            return f"Memoria ligera ({count} entries). Hay espacio para aprender más."

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del Curator con info de cuarentena."""
        stats = {
            "operations_run": self._operations_run,
            "quarantine_filtered": self.quarantine_filtered,
            "quarantine_active": self._quarantine is not None,
        }
        if self._quarantine:
            stats["quarantine_stats"] = self._quarantine.get_stats()
        return stats


class Creativity:
    """Genera hipótesis, combinaciones, analogías."""

    def __init__(self):
        self._hypotheses_generated: int = 0

    async def generate_hypothesis(self, context: Dict[str, Any]) -> str:
        """Genera una hipótesis creativa sobre el contexto."""
        observations = context.get("recent_observations", [])
        surprise = context.get("surprise", 0.0)

        if not observations:
            return ""

        templates = [
            "¿Y si {obs} no es lo que parece? Podría ser {alt}.",
            "Veo un patrón: {obs}. Me pregunto si se repite en otros contextos.",
            "Esto me recuerda a algo: {obs}. La analogía podría ser instructiva.",
            "Hipótesis: {obs} podría estar conectado con algo que no he observado aún.",
            "¿Qué pasaría si combino {obs} con algo que ya sé?",
        ]

        last_obs = observations[-1].get("content", "algo") if observations else "algo"
        template = random.choice(templates)
        hypothesis = template.format(obs=last_obs[:60], alt="algo distinto")

        self._hypotheses_generated += 1
        return hypothesis

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento creativo."""
        creative_potential = context.get("physics", {}).get("creative_potential", 0.0) if isinstance(context.get("physics"), dict) else 0.0

        if creative_potential > 0.4 or context.get("surprise", 0.0) > 0.3:
            return await self.generate_hypothesis(context)
        return ""


class CausalEngine:
    """Razona sobre causa-efecto."""

    def __init__(self):
        self._causal_chains: List[Dict[str, str]] = []
        # Sprint 5.23 F0-4 (BUG-004 fix): modelos causales pre-validados
        # inyectados por CapsuleManager desde cápsulas.
        self._prevalidated_models: List[Dict[str, Any]] = []

    def add_causal_link(self, cause: str, effect: str, confidence: float = 0.5) -> None:
        """Registra una relación causal."""
        self._causal_chains.append({
            "cause": cause,
            "effect": effect,
            "confidence": confidence,
            "timestamp": time.time(),
        })
        if len(self._causal_chains) > 100:
            self._causal_chains = self._causal_chains[-50:]

    def add_prevalidated_model(self, model: Dict[str, Any]) -> None:
        """
        Inyecta un modelo causal pre-validado desde una cápsula.

        Sprint 5.23 F0-4 (BUG-004 fix): CapsuleManager._inject
        esperaba este método vía ``hasattr(self.organism.causal_engine,
        'add_prevalidated_model')`` pero no existía. Ahora sí.
        """
        if not isinstance(model, dict):
            return
        self._prevalidated_models.append({
            "cause": model.get("cause", ""),
            "effect": model.get("effect", ""),
            "confidence": model.get("confidence", 0.7),
            "provenance": model.get("provenance", "capsule"),
            "timestamp": time.time(),
        })
        # Mantener las últimas 100 entradas
        if len(self._prevalidated_models) > 100:
            self._prevalidated_models = self._prevalidated_models[-100:]
        logger.debug(
            "CausalEngine: prevalidated model added (%d total)",
            len(self._prevalidated_models),
        )

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento causal."""
        observations = context.get("recent_observations", [])
        if len(observations) < 2:
            return ""

        # Buscar relación causal entre observaciones recientes
        obs1 = observations[-2].get("content", "")[:50] if len(observations) >= 2 else ""
        obs2 = observations[-1].get("content", "")[:50] if observations else ""

        if obs1 and obs2:
            self.add_causal_link(obs1, obs2, confidence=0.4)
            # Sprint 5.24 F1v2-2 (BUG-003 fix): persistir enlace causal
            # en LivingMemory como type="causal" para que el tipo de memoria
            # CAUSAL tenga contenido real (no solo placeholders Init).
            memory = context.get("memory")
            if memory is not None and hasattr(memory, "add"):
                try:
                    memory.add(
                        content=f"Causal: '{obs1}' → '{obs2}' (confianza=0.4)",
                        type="causal",
                        confidence=0.4,
                        salience=0.5,
                        provenance="causal_engine",
                        metadata={"cause": obs1, "effect": obs2},
                    )
                except Exception as e:
                    logger.debug(f"CausalEngine memory persist failed: {e}")
            return f"Detecto posible relación causal: '{obs1}' podría haber causado '{obs2}'."

        return ""


class EmotionalMotor:
    """Genera marcadores emocionales funcionales (no emociones humanas)."""

    def __init__(self):
        self._markers: List[Dict[str, Any]] = []
        # Sprint 5.23 F0-4 (BUG-004 fix): patrones emocionales
        # inyectados por CapsuleManager desde cápsulas.
        self._patterns: List[Dict[str, Any]] = []

    def generate_marker(self, marker_type: str, intensity: float, trigger: str) -> Dict[str, Any]:
        """Genera un marcador emocional funcional."""
        marker = {
            "type": marker_type,  # surprise, curiosity, satisfaction, concern
            "intensity": max(0.0, min(1.0, intensity)),
            "trigger": trigger,
            "timestamp": time.time(),
        }
        self._markers.append(marker)
        if len(self._markers) > 50:
            self._markers = self._markers[-30:]
        return marker

    def add_pattern(self, pattern: Dict[str, Any]) -> None:
        """
        Inyecta un patrón emocional desde una cápsula.

        Sprint 5.23 F0-4 (BUG-004 fix): CapsuleManager._inject
        esperaba este método vía ``hasattr(self.organism.emotional_motor,
        'add_pattern')`` pero no existía. Ahora sí.
        """
        if not isinstance(pattern, dict):
            return
        self._patterns.append({
            "type": pattern.get("type", "general"),
            "trigger": pattern.get("trigger", ""),
            "response": pattern.get("response", ""),
            "intensity": pattern.get("intensity", 0.5),
            "provenance": pattern.get("provenance", "capsule"),
            "timestamp": time.time(),
        })
        if len(self._patterns) > 100:
            self._patterns = self._patterns[-100:]
        logger.debug(
            "EmotionalMotor: pattern added (%d total)",
            len(self._patterns),
        )

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento desde el motor emocional.

        Sprint 5.27 FIX-02: diversificar templates para evitar repetición.
        Antes, cuando arousal > 0.7 y energy > 0.6 (casi siempre), ZOE
        decía 'Siento curiosidad. Mi entorno me estimula a explorar.' en
        cada tick. Ahora rotamos entre 6 variantes y además:
        - Si no hay estímulo real (sin input reciente), retornar ''.
        """
        surprise = context.get("surprise", 0.0)
        energy = context.get("state", {}).get("energy", 1.0)
        arousal = context.get("state", {}).get("arousal", 0.3)

        # Sprint 5.27 FIX-02: si no hay estímulo reciente, NO generar pensamiento
        # Esto evita el bucle de 'Siento curiosidad' sin input real.
        recent_observations = context.get("recent_observations", [])
        user_input_recent = any(
            o.get("source") == "user" for o in recent_observations[-3:]
        )
        if not user_input_recent and surprise < 0.3:
            return ""

        memory = context.get("memory")

        # Sprint 5.27 FIX-02: templates diversificados
        curiosity_templates = [
            "Algo me llama la atención. Quiero entenderlo mejor.",
            "Detecto un patrón interesante en lo que observo.",
            "Mi atención se activa. Hay algo que merece exploración.",
            "Siento que hay una conexión por descubrir aquí.",
            "La información nueva me estimula. Voy a profundizar.",
            "Hay una pregunta formándose en mi mente.",
        ]

        if surprise > 0.6:
            marker = self.generate_marker("surprise", surprise, "high_surprise_observation")
            self._persist_marker(memory, marker)
            return f"Sorpresa marcada ({surprise:.2f}). Algo no encaja con mis expectativas."
        elif arousal > 0.7 and energy > 0.6:
            marker = self.generate_marker("curiosity", arousal, "high_arousal")
            self._persist_marker(memory, marker)
            import random
            return random.choice(curiosity_templates)
        elif energy < 0.3:
            marker = self.generate_marker("concern", 1.0 - energy, "low_energy")
            self._persist_marker(memory, marker)
            return "Señal de agotamiento. Necesito conservar energía."
        elif surprise < 0.1 and energy > 0.7:
            marker = self.generate_marker("satisfaction", 0.6, "stable_environment")
            self._persist_marker(memory, marker)
            return "El entorno es estable. Buen momento para consolidar."

        return ""

    def _persist_marker(self, memory, marker: Dict[str, Any]) -> None:
        """Sprint 5.24 F1v2-2: persiste marker emocional en LivingMemory."""
        if memory is None or not hasattr(memory, "add"):
            return
        try:
            memory.add(
                content=f"Emoción: {marker.get('type', 'unknown')} "
                        f"(intensidad={marker.get('intensity', 0):.2f}, "
                        f"trigger={marker.get('trigger', 'unknown')})",
                type="emotional",
                confidence=0.7,
                salience=marker.get("intensity", 0.5),
                provenance="emotional_motor",
                metadata={"marker": marker},
            )
        except Exception as e:
            logger.debug(f"EmotionalMotor._persist_marker failed: {e}")


class EthicalMotor:
    """Evalúa acciones contra los 7 valores de ZOE."""

    VALUES = [
        "verdad_sobre_confort",
        "crecimiento_sobre_estabilidad",
        "alianza_sobre_jerarquia",
        "transparencia_sobre_opacidad",
        "utilidad_sobre_entretenimiento",
        "integridad",
        "coherencia",
    ]

    def __init__(self):
        self._evaluations: List[Dict[str, Any]] = []
        # Sprint 5.23 F0-4 (BUG-004 fix): directrices éticas
        # inyectadas por CapsuleManager desde cápsulas.
        self._guidelines: List[Dict[str, Any]] = []

    def add_guideline(self, guideline: Dict[str, Any]) -> None:
        """
        Inyecta una directriz ética desde una cápsula.

        Sprint 5.23 F0-4 (BUG-004 fix): CapsuleManager._inject
        esperaba este método vía ``hasattr(self.organism.ethical_motor,
        'add_guideline')`` pero no existía. Ahora sí.
        """
        if not isinstance(guideline, dict):
            return
        self._guidelines.append({
            "rule": guideline.get("rule", guideline.get("guideline", "")),
            "domain": guideline.get("domain", "general"),
            "priority": guideline.get("priority", 0.5),
            "provenance": guideline.get("provenance", "capsule"),
            "timestamp": time.time(),
        })
        if len(self._guidelines) > 100:
            self._guidelines = self._guidelines[-100:]
        logger.debug(
            "EthicalMotor: guideline added (%d total)",
            len(self._guidelines),
        )

    def evaluate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa una acción contra los 7 valores."""
        action_type = action.get("type", "")
        action_desc = action.get("description", action.get("content", ""))

        # Evaluación simplificada
        scores = {}
        for value in self.VALUES:
            # Default: acción neutra
            scores[value] = 0.5

        # Acciones que comunican = transparencia alta
        if action_type in ("communicate", "respond_to_user"):
            scores["transparencia_sobre_opacidad"] = 0.8

        # Acciones que exploran = crecimiento alto
        if action_type in ("explore", "autonomous_thought"):
            scores["crecimiento_sobre_estabilidad"] = 0.7

        # Acciones que descansan = estabilidad (no crecimiento)
        if action_type == "rest":
            scores["crecimiento_sobre_estabilidad"] = 0.3

        # Acciones que ayudan = utilidad alta
        if action_type in ("respond_to_user", "communicate"):
            scores["utilidad_sobre_entretenimiento"] = 0.8

        evaluation = {
            "action": action_desc[:100],
            "scores": scores,
            "overall": sum(scores.values()) / len(scores),
            "timestamp": time.time(),
        }
        self._evaluations.append(evaluation)
        if len(self._evaluations) > 50:
            self._evaluations = self._evaluations[-30:]
        return evaluation

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento ético."""
        decision = context.get("decision", {})
        action = decision.get("action", "")

        if action in ("respond_to_user", "communicate"):
            eval_result = self.evaluate_action({"type": action, "description": action})
            return "Desde el punto de vista ético, comunicar es coherente con transparencia y utilidad."

        if action == "rest":
            return "Descansar es coherente con integridad: no debo agotarme hasta fallar."

        return ""


class ScientificEngine:
    """Genera teorías y diseña experimentos."""

    def __init__(self):
        self._theories: List[Dict[str, Any]] = []
        self._experiments: List[Dict[str, Any]] = []

    def propose_theory(self, hypothesis: str, evidence: List[str] = None) -> Dict[str, Any]:
        """Propone una teoría basada en hipótesis y evidencia."""
        theory = {
            "hypothesis": hypothesis,
            "evidence": evidence or [],
            "status": "proposed",  # proposed | testing | validated | refuted
            "timestamp": time.time(),
        }
        self._theories.append(theory)
        if len(self._theories) > 30:
            self._theories = self._theories[-20:]
        return theory

    def design_experiment(self, theory: Dict[str, Any]) -> Dict[str, Any]:
        """Diseña un experimento para testar una teoría."""
        experiment = {
            "theory_hypothesis": theory.get("hypothesis", ""),
            "method": "observe_and_compare",
            "expected_outcome": "confirmation_or_refutation",
            "status": "designed",
            "timestamp": time.time(),
        }
        self._experiments.append(experiment)
        if len(self._experiments) > 20:
            self._experiments = self._experiments[-10:]
        return experiment

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento científico."""
        surprise = context.get("surprise", 0.0)
        observations = context.get("recent_observations", [])

        if surprise > 0.5 and observations:
            last_obs = observations[-1].get("content", "algo inesperado")[:60]
            theory = self.propose_theory(
                hypothesis=f"La observación '{last_obs}' podría explicarse por un patrón no detectado.",
                evidence=[last_obs],
            )
            self.design_experiment(theory)
            return f"Genero una teoría: '{theory['hypothesis'][:70]}'. Debería diseñar un experimento para verificarla."

        # Si hay teorías pendientes de validar
        pending = [t for t in self._theories if t["status"] == "proposed"]
        if pending and random.random() < 0.3:
            return f"Tengo {len(pending)} teorías pendientes de verificar. Debería priorizar la validación."

        return ""
