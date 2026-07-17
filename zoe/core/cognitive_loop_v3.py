"""
ZOE v1.0 — Cognitive Loop V3 (Fase 3)

Extiende CognitiveLoopV05 con:
- 12 sub-agentes integrados en el bucle (no solo los 4 de Fase 0)
- Global Workspace: sub-agentes proponen, workspace selecciona ganadores
- Meta-cognición: System 1 vs System 2 (Kahneman)
- Active Inference: selección de acción que minimiza sorpresa esperada
- Sub-agentes leen/escriben CognitiveFields
- Motor Ontogenético disponible para mutaciones arquitecturales

Mantiene compatibilidad: si los componentes Fase 2/3 no se proporcionan,
funciona como CognitiveLoopV05 de Fase 0.5/1.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Optional, List, Dict, Any, Callable, Awaitable

from .cognitive_loop_v05 import CognitiveLoopV05
from .cognitive_loop import Thought, Observation
from .state import InternalState
from .cognitive_laws import CognitiveLaws
from .cognitive_physics import CognitivePhysics
from .cognitive_fields import CognitiveFields
from .cognitive_tensions import CognitiveTensions
from .living_memory import LivingMemory
from .intentionality_motor import IntentionalityMotor
from .phylogenetic_motor import PhylogeneticMotor
from .global_workspace import GlobalWorkspace, Proposal
from .meta_cognition import MetaCognition
from .active_inference import ActiveInferenceLoop

logger = logging.getLogger(__name__)


class CognitiveLoopV3(CognitiveLoopV05):
    """
    Bucle cognitivo Fase 3.

    Integra TODO:
    - Fase 0: bucle básico
    - Fase 0.5: leyes, física, campos, tensiones, memoria viva, intencionalidad, filogenético
    - Fase 1: Identity Vault, Trajectory Chain, Ontogenetic Motor, Metabolism, 11 Memory Types
    - Fase 2: World Model V2, Active Inference, 12 sub-agentes, Meta-cognition, Global Workspace
    - Fase 3: integración de todo en el bucle + Global Workspace activo + meta-cog activa
    """

    def __init__(
        self,
        *args,
        # Componentes Fase 2/3 (opcionales para compatibilidad)
        global_workspace: Optional[GlobalWorkspace] = None,
        meta_cognition: Optional[MetaCognition] = None,
        active_inference: Optional[ActiveInferenceLoop] = None,
        world_model_v2: Any = None,
        # Componentes Fase 1 (opcionales, para acceso directo)
        identity_vault: Any = None,
        trajectory_chain: Any = None,
        ontogenetic_motor: Any = None,
        metabolism: Any = None,
        actuator_manager: Any = None,
        **kwargs,
    ):
        # Inicializar V05 (que a su vez inicializa V0)
        super().__init__(*args, **kwargs)

        # Componentes Fase 2/3
        self.global_workspace = global_workspace or GlobalWorkspace()
        self.meta_cognition = meta_cognition or MetaCognition()
        self.active_inference = active_inference or ActiveInferenceLoop()
        self.world_model_v2 = world_model_v2

        # Componentes Fase 1 (acceso directo)
        self.identity_vault = identity_vault
        self.trajectory_chain = trajectory_chain
        self.ontogenetic_motor = ontogenetic_motor
        self.metabolism = metabolism
        self.actuator_manager = actuator_manager

        # Estadísticas Fase 3
        self.workspace_competitions: int = 0
        self.system1_uses: int = 0
        self.system2_uses: int = 0
        self.active_inference_consultations: int = 0
        self.subagent_proposals: int = 0

    async def _tick(self) -> None:
        """Ejecuta una iteración del bucle cognitivo Fase 3."""
        tick_start = time.time()

        # 1. OBSERVE (Fase 0)
        observations = await self._observe()

        # 2. PREDICT (Fase 0 o V2)
        if self.world_model_v2:
            prediction = await self.world_model_v2.predict_next(observations)
        else:
            prediction = await self._predict(observations)

        # 3. EVALUATE (Fase 0 o V2)
        if self.world_model_v2:
            surprise = await self.world_model_v2.compute_surprise(prediction, observations)
        else:
            surprise = await self._evaluate(prediction, observations)

        # Sprint 5.23 F1-10 (BUG-026 fix): ``Forecaster.update`` jamás se
        # invocaba, así que ``Forecaster._last_prediction`` siempre era None
        # y ``generate_thought`` siempre devolvía templates "no history".
        # Ahora sí se le alimenta la predicción y la sorpresa.
        forecaster = None
        for agent in self.subagents:
            if agent.__class__.__name__ == "Forecaster":
                forecaster = agent
                break
        if forecaster is not None and hasattr(forecaster, "update"):
            try:
                forecaster.update(prediction, surprise)
            except Exception as fe:
                logger.debug(f"Forecaster.update failed (non-fatal): {fe}")

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

        # 9. METABOLISM TICK (Fase 1)
        if self.metabolism:
            dt = time.time() - tick_start
            self.metabolism.tick(dt)

        # 10. COLLECT PROPOSALS FROM ALL SUB-AGENTS (Fase 3)
        proposals = await self._collect_proposals(observations, surprise, prediction)

        # 11. GLOBAL WORKSPACE COMPETITION (Fase 2/3)
        winners = self._workspace_compete(proposals)

        # 12. META-COGNITION: System 1 vs System 2 (Fase 2/3)
        use_system2 = self._evaluate_meta_cognition(winners, surprise)

        # 13. ACTIVE INFERENCE: seleccionar acción (Fase 2/3)
        ai_action = self._consult_active_inference(observations, surprise)

        # 14. DECIDE (combinar winners + meta-cog + AI)
        decision = self._decide_v3(winners, surprise, observations, use_system2, ai_action)

        # 15. VERIFY LAWS (Fase 0.5)
        law_action = self._build_law_action(decision, surprise)
        laws_passed, violations = self.laws.verify_action(law_action)

        if not laws_passed:
            for v in violations:
                self.law_violations.append({
                    "law": v.law.value,
                    "reason": v.reason,
                    "timestamp": time.time(),
                    "iteration": self.state.iteration_count,
                })
            decision["should_act"] = False
            decision["reason"] = f"law_violation: {[v.law.value for v in violations]}"

        # 16. ACT (Fase 0 + Fase 3: usar ganador del workspace)
        if decision.get("should_act"):
            thought = await self._act_v3(decision, observations, surprise, winners)
            if thought:
                self.thoughts.append(thought)
                # Sprint 5.13 B4-bis — Truncar thoughts para prevenir memory leak.
                if hasattr(self, '_max_thoughts') and len(self.thoughts) > self._max_thoughts:
                    del self.thoughts[:-self._max_thoughts]
                self.state.register_thought()

                # Almacenar en Living Memory
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
                        "system": "system2" if use_system2 else "system1",
                    },
                )

                # Si hay ontogenetic motor, proponer mutación de aprendizaje
                if self.ontogenetic_motor and thought.surprise > 0.5:
                    try:
                        mutation = self.ontogenetic_motor.propose_mutation(
                            type="add_memory",
                            target="episodic",
                            payload={"content": thought.content[:100]},
                            justification=f"Sorpresa alta ({thought.surprise:.2f}) detectada",
                            provenance=f"loop_v3:surprise",
                            cost=0.1,
                            confidence=0.6,
                        )
                        self.ontogenetic_motor.apply_mutation(mutation)
                    except Exception as e:
                        logger.debug(f"Ontogenetic mutation failed: {e}")

                if self.on_thought_callback:
                    await self.on_thought_callback(thought)

        # 17. BROADCAST to all sub-agents (Fase 3)
        self._broadcast_to_subagents(winners, decision, surprise)

        # 18. UPDATE STATE (Fase 0)
        dt = time.time() - tick_start
        self.state.tick(dt)
        if surprise > 0.3:
            self.state.stimulate(intensity=surprise)

    async def _collect_proposals(
        self,
        observations: List[Observation],
        surprise: float,
        prediction: Dict[str, Any],
    ) -> List[Proposal]:
        """
        Recoge propuestas de todos los sub-agentes para el Global Workspace.
        Cada sub-agente puede proponer una acción.
        """
        proposals: List[Proposal] = []

        # Contexto compartido para todos los sub-agentes
        context = {
            "observations": observations,
            "surprise": surprise,
            "prediction": prediction,
            "state": self.state.to_dict(),
            "recent_thoughts": [t.to_dict() for t in self.thoughts[-5:]],
            "recent_observations": [
                {"source": o.source, "content": o.content}
                for o in self.observations[-10:]
            ],
            "tensions": self.tensions.to_dict(),
            "physics": self.physics.to_dict(),
            "fields": self.fields.read_all(),
            "intentions": [i.to_dict() for i in self.intentionality.get_active_intentions()],
            "tension_trigger": self.tensions.get_thought_trigger(),
        }

        # Pedir a cada sub-agente que proponga
        # Sprint 5.23 F1-11 (BUG-027 fix): ``Critic.generate_thought`` siempre
        # retorna ``""`` (es un evaluador, no un generador). Invocarlo en
        # ``_collect_proposals`` desperdicia un ciclo y ensucia el log.
        # Lo excluimos explícitamente del loop de propuestas.
        for agent in self.subagents:
            try:
                if agent.__class__.__name__ == "Critic":
                    continue
                if hasattr(agent, "generate_thought"):
                    content = await agent.generate_thought(context)
                    if content and len(content) > 5:
                        # Calcular score de la propuesta
                        relevance = 0.5
                        if surprise > 0.5 and "sorpresa" in content.lower():
                            relevance = 0.8
                        elif "explor" in content.lower():
                            relevance = 0.7
                        elif "recuerd" in content.lower():
                            relevance = 0.6

                        urgency = min(1.0, surprise + self.state.arousal * 0.3)
                        novelty = 0.5
                        # Comparar con pensamientos recientes para novedad
                        recent_contents = [t.content.lower() for t in self.thoughts[-5:]]
                        if content.lower() not in " ".join(recent_contents):
                            novelty = 0.7

                        proposals.append(Proposal(
                            subagent_name=agent.__class__.__name__,
                            content=content,
                            relevance=relevance,
                            urgency=urgency,
                            novelty=novelty,
                            energy_cost=0.2 + len(content) / 1000,
                        ))
                        self.subagent_proposals += 1
            except Exception as e:
                logger.debug(f"Sub-agent {agent.__class__.__name__} proposal failed: {e}")

        return proposals

    def _workspace_compete(self, proposals: List[Proposal]) -> List[Proposal]:
        """El Global Workspace selecciona ganadores."""
        if not proposals:
            return []

        self.global_workspace.clear()
        self.global_workspace.submit_batch(proposals)
        winners = self.global_workspace.compete(
            available_energy=self.state.energy if self.state else 1.0
        )
        self.workspace_competitions += 1

        return winners

    def _evaluate_meta_cognition(
        self, winners: List[Proposal], surprise: float
    ) -> bool:
        """Meta-cognición decide System 1 vs System 2."""
        if not winners:
            return False

        # Evaluar confianza en el ganador
        best = winners[0]
        confidence = self.meta_cognition.evaluate_confidence(
            response=best.content,
            surprise=surprise,
            physics=self.physics,
        )

        # Evaluar stakes
        context = {
            "surprise": surprise,
            "recent_observations": [
                {"source": o.source, "content": o.content}
                for o in self.observations[-5:]
            ],
            "intentions": [i.to_dict() for i in self.intentionality.get_active_intentions()],
        }
        stakes = self.meta_cognition.evaluate_stakes(context)

        # Decidir
        deliberate, reason = self.meta_cognition.should_deliberate(
            confidence=confidence,
            stakes=stakes,
            energy=self.state.energy,
            arousal=self.state.arousal,
        )

        if deliberate:
            self.system2_uses += 1
        else:
            self.system1_uses += 1

        return deliberate

    def _consult_active_inference(
        self, observations: List[Observation], surprise: float
    ) -> Optional[str]:
        """Active Inference sugiere acción."""
        if not observations:
            return None

        current_state = self.active_inference.get_current_state()
        if current_state == "unknown" and observations:
            source = observations[-1].source if observations else "unknown"
            self.active_inference.update_beliefs(source, observations[-1].content if observations else "")

        action = self.active_inference.select_action(current_state)
        self.active_inference_consultations += 1

        # Registrar resultado
        next_state = observations[-1].source if observations else "unknown"
        self.active_inference.record_action_result(current_state, action, next_state, surprise)

        return action

    def _decide_v3(
        self,
        winners: List[Proposal],
        surprise: float,
        observations: List[Observation],
        use_system2: bool,
        ai_action: Optional[str],
    ) -> Dict[str, Any]:
        """Decide qué hacer combinando winners + meta-cog + AI."""

        # Si hay input del usuario, priorizar respuesta
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
                "system": "system2" if use_system2 else "system1",
            }

        # Si hay ganadores del workspace, usar el mejor
        if winners:
            best = winners[0]
            return {
                "should_act": True,
                "action": "autonomous_thought",
                "reason": f"workspace_winner:{best.subagent_name}",
                "target_subagent": best.subagent_name.lower()[:4],
                "content_hint": best.content,
                "uncertainty_reduction": surprise,
                "capacity_increase": 0.2 if "explor" in best.content.lower() else 0.1,
                "cost": best.energy_cost,
                "preserves_identity": True,
                "provenance": f"workspace:{best.subagent_name}",
                "confidence": 0.6,
                "system": "system2" if use_system2 else "system1",
            }

        # Si sorpresa alta, pensar
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
                "system": "system2",
            }

        # Si AI sugiere descansar
        if ai_action == "rest" and self.physics.should_rest():
            return {
                "should_act": False,
                "action": "rest",
                "reason": "active_inference:suggests_rest",
                "uncertainty_reduction": 0.0,
                "capacity_increase": 0.1,
                "cost": 0.0,
                "preserves_identity": True,
                "provenance": "active_inference",
                "confidence": 0.5,
                "system": "system1",
            }

        # Default: observar
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
            "system": "system1",
        }

    async def _act_v3(
        self,
        decision: Dict[str, Any],
        observations: List[Observation],
        surprise: float,
        winners: List[Proposal],
    ) -> Optional[Thought]:
        """Ejecuta la decisión usando el ganador del workspace."""

        # Si hay content_hint del workspace, usarlo
        content_hint = decision.get("content_hint")

        # Buscar sub-agente objetivo
        target = decision.get("target_subagent", "speaker")
        target_agent = None
        for agent in self.subagents:
            name = agent.__class__.__name__.lower()
            if name.startswith(target.lower()[:4]):
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
                "action": decision.get("action", "autonomous_thought"),
                "decision": decision,
                "observations": observations,
                "surprise": surprise,
                "state": self.state.to_dict(),
                "recent_thoughts": [t.to_dict() for t in self.thoughts[-5:]],
                "recent_observations": [
                    {"source": o.source, "content": o.content}
                    for o in self.observations[-10:]
                ],
                "tensions": self.tensions.to_dict(),
                "physics": self.physics.to_dict(),
                "fields": self.fields.read_all(),
                "intentions": [i.to_dict() for i in self.intentionality.get_active_intentions()],
                "tension_trigger": self.tensions.get_thought_trigger(),
                "workspace_winners": [p.to_dict() for p in winners],
                "content_hint": content_hint,
                "use_system2": decision.get("system") == "system2",
            }

            thought_content = await target_agent.generate_thought(context)

            if not thought_content and content_hint:
                thought_content = content_hint

            if not thought_content:
                return None

            return Thought(
                timestamp=time.time(),
                content=thought_content,
                surprise=surprise,
                trigger=decision.get("action", "autonomous_thought"),
                subagent_source=target_agent.__class__.__name__,
                metadata={
                    "decision": decision.get("reason", ""),
                    "laws_verified": True,
                    "physics": self.physics.summary(),
                    "system": decision.get("system", "system1"),
                    "workspace_winner": winners[0].subagent_name if winners else None,
                },
            )
        except Exception as e:
            logger.error(f"Sub-agent {target_agent.__class__.__name__} failed: {e}")
            return None

    def _broadcast_to_subagents(
        self,
        winners: List[Proposal],
        decision: Dict[str, Any],
        surprise: float,
    ) -> None:
        """Broadcast del resultado a todos los sub-agentes (Global Workspace)."""
        if not winners:
            return

        broadcast = self.global_workspace.broadcast()

        # Escribir broadcast en campos cognitivos
        self.fields.contribute(
            "attention",
            "GlobalWorkspace",
            {
                "winning_subagent": winners[0].subagent_name if winners else None,
                "winning_action": decision.get("action", "none"),
                "surprise": surprise,
            },
        )

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas completas incluyendo Fase 3."""
        stats = super().get_stats()

        # Fase 2/3 stats
        stats["workspace_competitions"] = self.workspace_competitions
        stats["system1_uses"] = self.system1_uses
        stats["system2_uses"] = self.system2_uses
        stats["system2_rate"] = (
            self.system2_uses / max(1, self.system1_uses + self.system2_uses)
        )
        stats["active_inference_consultations"] = self.active_inference_consultations
        stats["subagent_proposals"] = self.subagent_proposals
        stats["workspace_stats"] = self.global_workspace.get_stats()
        stats["meta_cognition_stats"] = self.meta_cognition.get_stats()
        stats["active_inference_stats"] = self.active_inference.get_stats()

        return stats
