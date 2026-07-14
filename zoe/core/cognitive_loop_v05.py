"""
ZOE v1.0 — Cognitive Loop (Fase 0.5 extendida)

Extiende el bucle de Fase 0 con:
- CognitiveLaws: cada acción se verifica contra las 6 leyes
- CognitivePhysics: 12 magnitudes calculadas por iteración
- CognitiveFields: 6 campos compartidos en vez de mensajes
- CognitiveTensions: 5 tensiones permanentes que generan pensamiento
- LivingMemory: memoria que piensa (reorganiza, olvida, fusiona)
- IntentionalityMotor: genera continuamente nuevas intenciones
- PhylogeneticMotor: disponible para evolución de especie

Mantiene compatibilidad con Fase 0: si los componentes nuevos no
se proporcionan, el bucle funciona igual que en Fase 0.
"""

from __future__ import annotations

import asyncio
import time
import logging
from typing import Optional, List, Dict, Any, Callable, Awaitable

from .state import InternalState
from .cognitive_laws import CognitiveLaws, LawID
from .cognitive_physics import CognitivePhysics
from .cognitive_fields import CognitiveFields
from .cognitive_tensions import CognitiveTensions
from .living_memory import LivingMemory
from .intentionality_motor import IntentionalityMotor
from .phylogenetic_motor import PhylogeneticMotor

# Re-exportar Thought y Observation de Fase 0 para compatibilidad
from .cognitive_loop import Thought, Observation

logger = logging.getLogger(__name__)


class CognitiveLoopV05:
    """
    Bucle cognitivo Fase 0.5.

    Combina el bucle de Fase 0 con las 7 innovaciones del CEO.
    Si los componentes nuevos no se proporcionan, funciona como Fase 0.
    """

    def __init__(
        self,
        senses: List[Any] = None,
        world_model: Any = None,
        subagents: List[Any] = None,
        state: Optional[InternalState] = None,
        tick_interval: float = 5.0,
        on_thought: Optional[Callable[[Thought], Awaitable[None]]] = None,
        # Componentes Fase 0.5 (opcionales para compatibilidad)
        laws: Optional[CognitiveLaws] = None,
        physics: Optional[CognitivePhysics] = None,
        fields: Optional[CognitiveFields] = None,
        tensions: Optional[CognitiveTensions] = None,
        memory: Optional[LivingMemory] = None,
        intentionality: Optional[IntentionalityMotor] = None,
        phylogenetic: Optional[PhylogeneticMotor] = None,
        zoe_id: str = "zoe_default",
    ):
        self.senses = senses or []
        self.world_model = world_model
        self.subagents = subagents or []
        self.state = state or InternalState()
        self.tick_interval = tick_interval
        self.on_thought_callback = on_thought
        self.zoe_id = zoe_id

        # Componentes Fase 0.5
        self.laws = laws or CognitiveLaws()
        self.physics = physics or CognitivePhysics()
        self.fields = fields or CognitiveFields()
        self.tensions = tensions or CognitiveTensions()
        self.memory = memory or LivingMemory()
        self.intentionality = intentionality or IntentionalityMotor()
        self.phylogenetic = phylogenetic or PhylogeneticMotor(zoe_id=zoe_id)

        # Historial (compatible con Fase 0)
        self.observations: List[Observation] = []
        # Sprint 5.13 B4-bis — Bound self.thoughts to prevent memory leak.
        # Antes: List[Thought] = [] (unbounded, ~6GB/year en produccion).
        # Ahora: List[Thought] con truncado automatico en _add_thought().
        # NO usamos deque porque el codigo existente hace self.thoughts[-5:]
        # (slicing) que deque no soporta.
        self.thoughts: List[Thought] = []
        self._max_thoughts = 1000  # limite para prevenir memory leak
        self.predictions: List[Dict[str, Any]] = []

        # Nuevos históricos Fase 0.5
        self.law_violations: List[Dict[str, Any]] = []
        self.intentions_generated: List[Dict[str, Any]] = []
        self.physics_history: List[Dict[str, float]] = []
        self.memory_operations: List[Dict[str, Any]] = []

        # Control
        self._running = False
        self._stop_requested = False

    async def run(self, duration_seconds: Optional[float] = None) -> None:
        """Ejecuta el bucle cognitivo."""
        self._running = True
        self._stop_requested = False
        start_time = time.time()

        logger.info(
            f"CognitiveLoopV05 iniciado. Duration: {duration_seconds}s, tick: {self.tick_interval}s"
        )

        try:
            while not self._stop_requested:
                if duration_seconds is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        logger.info(f"Duración alcanzada ({elapsed:.1f}s). Deteniendo.")
                        break

                await self._tick()
                await asyncio.sleep(self.tick_interval)
        finally:
            self._running = False
            logger.info(
                f"CognitiveLoopV05 detenido. Iteraciones: {self.state.iteration_count}, "
                f"Pensamientos: {len(self.thoughts)}, "
                f"Violaciones de leyes: {len(self.law_violations)}"
            )

    def stop(self) -> None:
        self._stop_requested = True

    async def _tick(self) -> None:
        """Ejecuta una iteración del bucle cognitivo Fase 0.5."""
        tick_start = time.time()

        # 1. OBSERVE (Fase 0)
        observations = await self._observe()

        # 2. PREDICT (Fase 0)
        prediction = await self._predict(observations)

        # 3. EVALUATE (Fase 0)
        surprise = await self._evaluate(prediction, observations)

        # 4. UPDATE COGNITIVE FIELDS (Fase 0.5)
        self._update_fields(observations, surprise)

        # 5. UPDATE COGNITIVE TENSIONS (Fase 0.5)
        self._update_tensions(surprise)

        # 6. UPDATE COGNITIVE PHYSICS (Fase 0.5)
        self._update_physics(observations)

        # 7. GENERATE INTENTIONS (Fase 0.5)
        new_intentions = self._generate_intentions(observations)

        # 8. LIVING MEMORY THINK (Fase 0.5)
        memory_result = self._memory_think()

        # 9. DECIDE (Fase 0 + Fase 0.5)
        decision = await self._decide(surprise, observations, new_intentions)

        # 10. VERIFY LAWS (Fase 0.5)
        law_action = self._build_law_action(decision, surprise)
        laws_passed, violations = self.laws.verify_action(law_action)

        if not laws_passed:
            # Registrar violación y no ejecutar
            for v in violations:
                self.law_violations.append(
                    {
                        "law": v.law.value,
                        "reason": v.reason,
                        "timestamp": time.time(),
                        "iteration": self.state.iteration_count,
                    }
                )
            logger.warning(
                f"Iteración {self.state.iteration_count}: acción rechazada por leyes: "
                f"{[v.law.value for v in violations]}"
            )
            decision["should_act"] = False
            decision["reason"] = f"law_violation: {[v.law.value for v in violations]}"

        # 11. ACT (Fase 0)
        if decision.get("should_act"):
            thought = await self._act(decision, observations, surprise)
            if thought:
                self.thoughts.append(thought)
                # Sprint 5.13 B4-bis — Truncar thoughts para prevenir memory leak.
                # Mantener solo los ultimos 1000 (self._max_thoughts).
                if hasattr(self, '_max_thoughts') and len(self.thoughts) > self._max_thoughts:
                    del self.thoughts[:-self._max_thoughts]
                self.state.register_thought()
                # Almacenar en Living Memory (Fase 0.5)
                self.memory.add(
                    content=thought.content,
                    type="episodic",
                    confidence=max(0.3, 1.0 - thought.surprise),
                    salience=0.5 + thought.surprise * 0.5,
                    provenance=f"thought:{thought.subagent_source}",
                    metadata={
                        "trigger": thought.trigger,
                        "surprise": thought.surprise,
                        "subagent": thought.subagent_source,
                    },
                )
                if self.on_thought_callback:
                    await self.on_thought_callback(thought)

        # 12. UPDATE STATE (Fase 0)
        dt = time.time() - tick_start
        self.state.tick(dt)
        if surprise > 0.3:
            self.state.stimulate(intensity=surprise)

        # 13. PHYLOGENETIC CHECK (Fase 0.5, opcional)
        # En Fase 0.5 no publicamos mejoras automáticamente,
        # pero podríamos incorporar mejoras validadas
        # (se hace explícitamente vía self.phylogenetic.incorporate_validated())

    async def _observe(self) -> List[Observation]:
        """Recoge observaciones de los sentidos."""
        observations = []
        for sense in self.senses:
            try:
                obs = await sense.observe()
                if isinstance(obs, list):
                    observations.extend(obs)
                elif obs is not None:
                    observations.append(obs)
            except Exception as e:
                logger.warning(f"Sense {sense.__class__.__name__} failed: {e}")

        self.observations.extend(observations)
        if len(self.observations) > 1000:
            self.observations = self.observations[-500:]

        return observations

    async def _predict(self, observations: List[Observation]) -> Dict[str, Any]:
        if not self.world_model:
            return {"predicted": None, "confidence": 0.0}
        try:
            prediction = await self.world_model.predict_next(observations)
            self.predictions.append(prediction)
            return prediction
        except Exception as e:
            logger.warning(f"WorldModel predict failed: {e}")
            return {"predicted": None, "confidence": 0.0, "error": str(e)}

    async def _evaluate(
        self, prediction: Dict[str, Any], observations: List[Observation]
    ) -> float:
        if not self.world_model or not observations:
            return 0.0
        try:
            surprise = await self.world_model.compute_surprise(prediction, observations)
            return float(surprise)
        except Exception as e:
            logger.warning(f"WorldModel compute_surprise failed: {e}")
            return 0.0

    def _update_fields(self, observations: List[Observation], surprise: float) -> None:
        """Actualiza los campos cognitivos compartidos."""
        # Campo de atención: qué se está observando
        if observations:
            sources = [o.source for o in observations]
            self.fields.contribute(
                "attention",
                "Perceiver",
                {"sources": sources, "count": len(observations)},
            )

        # Campo emocional: sorpresa y arousal
        self.fields.contribute(
            "emotional",
            "Forecaster",
            {"surprise": surprise, "arousal": self.state.arousal},
        )

        # Campo social: si hay observaciones de usuario
        user_obs = [o for o in observations if o.source == "user"]
        if user_obs:
            self.fields.contribute(
                "social",
                "Perceiver",
                {"user_present": True, "last_message": user_obs[-1].content[:100]},
            )

    def _update_tensions(self, surprise: float) -> None:
        """Actualiza las tensiones cognitivas."""
        self.tensions.update_from_state(
            energy=self.state.energy,
            fatigue=self.state.fatigue,
            arousal=self.state.arousal,
            surprise=surprise,
            identity_inertia=self.physics.identity_inertia,
        )

        # Actualizar tensiones que requieren datos de physics
        self.tensions.update_specialization_generalization(
            semantic_entropy=self.physics.semantic_entropy,
            conceptual_resonance=self.physics.conceptual_resonance,
        )

    def _update_physics(self, observations: List[Observation]) -> None:
        """Actualiza las magnitudes de física cognitiva."""
        # Conceptos activos = palabras únicas en observaciones recientes
        concepts = []
        for obs in self.observations[-20:]:
            concepts.extend(obs.content.lower().split())
        # Filtrar stopwords simples
        concepts = [c for c in concepts if len(c) > 3]

        # Contexto actual = fuente dominante
        current_context = (
            max(set(o.source for o in observations), key=lambda s: sum(1 for o in observations if o.source == s))
            if observations
            else ""
        )

        physics_state = self.physics.update(
            state=self.state,
            observations=observations,
            thoughts=self.thoughts,
            intentions=self.intentionality.get_active_intentions(),
            memory_concepts=concepts,
            causal_relations=0,  # se calculará en Fase 2 con WorldModel causal
            current_context=current_context,
        )

        # Guardar en historial (acotado)
        self.physics_history.append(physics_state)
        if len(self.physics_history) > 100:
            self.physics_history = self.physics_history[-50:]

    def _generate_intentions(self, observations: List[Observation]) -> List[Dict[str, Any]]:
        """Genera nuevas intenciones."""
        new = self.intentionality.generate(
            tensions=self.tensions,
            physics=self.physics,
            memory=self.memory,
            observations=observations,
        )
        result = [i.to_dict() for i in new]
        self.intentions_generated.extend(result)
        if len(self.intentions_generated) > 100:
            self.intentions_generated = self.intentions_generated[-50:]
        return result

    def _memory_think(self) -> Optional[Dict[str, Any]]:
        """La memoria viva piensa (una operación por tick)."""
        if self.memory.count() < 3:
            return None
        result = self.memory.think()
        self.memory_operations.append(result)
        if len(self.memory_operations) > 50:
            self.memory_operations = self.memory_operations[-30:]
        return result

    async def _decide(
        self,
        surprise: float,
        observations: List[Observation],
        new_intentions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Decide qué hacer basado en todos los componentes."""
        # Si hay intención de alta prioridad, seguirla
        active_intentions = self.intentionality.get_active_intentions(n=3)
        if active_intentions and active_intentions[0].priority > 0.6:
            top_intention = active_intentions[0]
            if top_intention.type == "communicate":
                return {
                    "should_act": True,
                    "action": "respond_to_user",
                    "reason": f"intention:{top_intention.type}",
                    "target_subagent": "speaker",
                    "user_content": top_intention.metadata.get("user_content", ""),
                    "uncertainty_reduction": 0.3,
                    "capacity_increase": 0.0,
                    "cost": 0.3,
                    "preserves_identity": True,
                    "provenance": f"intention:{top_intention.id}",
                    "confidence": top_intention.priority,
                }
            elif top_intention.type in ["explore", "understand"]:
                return {
                    "should_act": True,
                    "action": "autonomous_thought",
                    "reason": f"intention:{top_intention.type}",
                    "target_subagent": "speaker",
                    "uncertainty_reduction": 0.4,
                    "capacity_increase": 0.3,
                    "cost": 0.3,
                    "preserves_identity": True,
                    "provenance": f"intention:{top_intention.id}",
                    "confidence": top_intention.priority,
                }
            elif top_intention.type == "consolidate":
                # Consolidar memoria
                return {
                    "should_act": False,
                    "action": "consolidate_memory",
                    "reason": f"intention:{top_intention.type}",
                    "uncertainty_reduction": 0.2,
                    "capacity_increase": 0.1,
                    "cost": 0.1,
                    "preserves_identity": True,
                    "provenance": f"intention:{top_intention.id}",
                    "confidence": top_intention.priority,
                }

        # Si hay sorpresa alta, pensar sobre eso (Fase 0)
        if surprise > 0.5:
            return {
                "should_act": True,
                "action": "think_on_surprise",
                "reason": f"high_surprise={surprise:.3f}",
                "target_subagent": "speaker",
                "uncertainty_reduction": surprise,
                "capacity_increase": 0.0,
                "cost": 0.4,
                "preserves_identity": True,
                "provenance": "surprise",
                "confidence": 0.7,
            }

        # Si hay input del usuario, responder (Fase 0)
        user_obs = [o for o in observations if o.source == "user"]
        if user_obs:
            return {
                "should_act": True,
                "action": "respond_to_user",
                "reason": "user_input",
                "target_subagent": "speaker",
                "user_content": user_obs[-1].content,
                "uncertainty_reduction": 0.3,
                "capacity_increase": 0.0,
                "cost": 0.3,
                "preserves_identity": True,
                "provenance": "user_input",
                "confidence": 0.8,
            }

        # Si hay intención de pensar desde tensión, hacerlo
        trigger = self.tensions.get_thought_trigger()
        if trigger and self.state.should_think() and self.state.energy > 0.4:
            import random

            if random.random() < 0.3:
                return {
                    "should_act": True,
                    "action": "autonomous_thought",
                    "reason": f"tension:{trigger}",
                    "target_subagent": "speaker",
                    "uncertainty_reduction": 0.2,
                    "capacity_increase": 0.2,
                    "cost": 0.3,
                    "preserves_identity": True,
                    "provenance": f"tension:{trigger}",
                    "confidence": 0.6,
                }

        # Si física cognitiva dice descansar, descansar
        if self.physics.should_rest():
            return {
                "should_act": False,
                "action": "rest",
                "reason": "physics:suggests_rest",
                "uncertainty_reduction": 0.0,
                "capacity_increase": 0.1,
                "cost": 0.0,
                "preserves_identity": True,
                "provenance": "physics",
                "confidence": 0.5,
            }

        return {
            "should_act": False,
            "action": "observe_only",
            "reason": "low_priority",
            "uncertainty_reduction": 0.0,
            "capacity_increase": 0.0,
            "cost": 0.0,
            "preserves_identity": True,
            "provenance": "default",
            "confidence": 0.3,
        }

    def _build_law_action(self, decision: Dict[str, Any], surprise: float) -> Dict[str, Any]:
        """Construye el dict de acción para verificar leyes."""
        action_type_map = {
            "respond_to_user": "communicate",
            "autonomous_thought": "think",
            "think_on_surprise": "think",
            "consolidate_memory": "mutate",
            "rest": "rest",
            "observe_only": "think",
        }

        action_type = action_type_map.get(decision.get("action", ""), "think")

        return {
            "type": action_type,
            "uncertainty_reduction": decision.get("uncertainty_reduction", 0.0),
            "capacity_increase": decision.get("capacity_increase", 0.0),
            "cost": decision.get("cost", 0.1),
            "preserves_identity": decision.get("preserves_identity", True),
            "provenance": decision.get("provenance", ""),
            "confidence": decision.get("confidence", 0.5),
            "subtype": decision.get("action", ""),
        }

    async def _act(
        self,
        decision: Dict[str, Any],
        observations: List[Observation],
        surprise: float,
    ) -> Optional[Thought]:
        """Ejecuta la decisión (igual que Fase 0)."""
        target = decision.get("target_subagent")
        action = decision.get("action")

        target_agent = None
        for agent in self.subagents:
            if agent.__class__.__name__.lower().startswith(target.lower()[:4]):
                target_agent = agent
                break

        if not target_agent:
            for agent in self.subagents:
                if hasattr(agent, "generate_thought"):
                    target_agent = agent
                    break

        if not target_agent:
            return None

        try:
            context = {
                "action": action,
                "decision": decision,
                "observations": observations,
                "surprise": surprise,
                "state": self.state.to_dict(),
                "recent_thoughts": [t.to_dict() for t in self.thoughts[-5:]],
                "recent_observations": [
                    {"source": o.source, "content": o.content}
                    for o in self.observations[-10:]
                ],
                # Fase 0.5: añadir contexto enriquecido
                "tensions": self.tensions.to_dict(),
                "physics": self.physics.to_dict(),
                "fields": self.fields.read_all(),
                "intentions": [i.to_dict() for i in self.intentionality.get_active_intentions()],
                "tension_trigger": self.tensions.get_thought_trigger(),
            }

            thought_content = await target_agent.generate_thought(context)

            if not thought_content:
                return None

            return Thought(
                timestamp=time.time(),
                content=thought_content,
                surprise=surprise,
                trigger=action,
                subagent_source=target_agent.__class__.__name__,
                metadata={
                    "decision": decision.get("reason", ""),
                    "laws_verified": True,
                    "physics": self.physics.summary(),
                },
            )
        except Exception as e:
            logger.error(f"Sub-agent {target_agent.__class__.__name__} failed: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas completas del bucle Fase 0.5."""
        return {
            # Fase 0
            "iterations": self.state.iteration_count,
            "observations": len(self.observations),
            "thoughts": len(self.thoughts),
            "predictions": len(self.predictions),
            "energy": self.state.energy,
            "fatigue": self.state.fatigue,
            "arousal": self.state.arousal,
            "attention": self.state.attention,
            # Fase 0.5
            "law_violations": len(self.law_violations),
            "law_stats": self.laws.get_stats(),
            "physics": self.physics.to_dict(),
            "physics_summary": self.physics.summary(),
            "fields_summary": self.fields.summary(),
            "tensions_summary": self.tensions.summary(),
            "memory_stats": self.memory.get_stats(),
            "intentionality_stats": self.intentionality.get_stats(),
            "species_state": self.phylogenetic.get_species_state(),
            "intentions_generated": len(self.intentions_generated),
            "memory_operations": len(self.memory_operations),
        }
