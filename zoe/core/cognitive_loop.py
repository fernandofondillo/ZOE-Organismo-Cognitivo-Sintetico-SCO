"""
ZOE v1.0 — Cognitive Loop

Bucle cognitivo continuo asíncrono.
Observar → Predecir → Evaluar → Decidir → Actuar → (repetir)

Este es el corazón de ZOE. A diferencia de los LLMs reactivos,
ZOE piensa continuamente incluso sin input.
"""

from __future__ import annotations

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Awaitable

from .state import InternalState

logger = logging.getLogger(__name__)


@dataclass
class Thought:
    """Un pensamiento generado por ZOE."""

    timestamp: float
    content: str
    surprise: float  # 0-1, cuánta sorpresa lo generó
    trigger: str  # "input" | "autonomous" | "consolidation"
    subagent_source: str  # qué sub-agente lo generó
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "content": self.content,
            "surprise": self.surprise,
            "trigger": self.trigger,
            "subagent_source": self.subagent_source,
            "metadata": self.metadata,
        }


@dataclass
class Observation:
    """Una observación del entorno."""

    timestamp: float
    source: str  # "clock" | "filesystem" | "llm" | "user" | ...
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveLoop:
    """
    Bucle cognitivo continuo asíncrono.

    El bucle ejecuta iteraciones cada `tick_interval` segundos.
    Cada iteración:
    1. OBSERVE: recoger observaciones de los sentidos
    2. PREDICT: World Model predice el próximo estado
    3. EVALUATE: comparar predicción con realidad, calcular sorpresa
    4. DECIDE: decidir si pensar, comunicar, explorar, o descansar
    5. ACT: ejecutar la decisión (generar pensamiento, mutar, etc.)

    Uso:
        loop = CognitiveLoop(...)
        await loop.run(duration_seconds=3600)
    """

    def __init__(
        self,
        senses: List[Any] = None,
        world_model: Any = None,
        subagents: List[Any] = None,
        state: Optional[InternalState] = None,
        tick_interval: float = 5.0,
        on_thought: Optional[Callable[[Thought], Awaitable[None]]] = None,
    ):
        self.senses = senses or []
        self.world_model = world_model
        self.subagents = subagents or []
        self.state = state or InternalState()
        self.tick_interval = tick_interval
        self.on_thought_callback = on_thought

        # Historial
        self.observations: List[Observation] = []
        # Sprint 5.13 B4-bis — Bound self.thoughts to prevent memory leak.
        # NO usamos deque (no soporta slicing self.thoughts[-5:]).
        # Usamos list con truncado manual en append.
        self.thoughts: List[Thought] = []
        self._max_thoughts = 1000  # limite para prevenir memory leak
        self.predictions: List[Dict[str, Any]] = []

        # Control
        self._running = False
        self._stop_requested = False

    async def run(self, duration_seconds: Optional[float] = None) -> None:
        """
        Ejecuta el bucle cognitivo.

        Args:
            duration_seconds: cuánto tiempo correr. None = indefinido.
        """
        self._running = True
        self._stop_requested = False
        start_time = time.time()

        logger.info(f"CognitiveLoop iniciado. Duration: {duration_seconds}s, tick: {self.tick_interval}s")

        try:
            while not self._stop_requested:
                # Verificar duración
                if duration_seconds is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        logger.info(f"Duración alcanzada ({elapsed:.1f}s). Deteniendo.")
                        break

                # Ejecutar iteración
                await self._tick()

                # Esperar próximo tick
                await asyncio.sleep(self.tick_interval)
        finally:
            self._running = False
            logger.info(
                f"CognitiveLoop detenido. Iteraciones: {self.state.iteration_count}, "
                f"Pensamientos: {len(self.thoughts)}"
            )

    def stop(self) -> None:
        """Solicita detener el bucle."""
        self._stop_requested = True

    async def _tick(self) -> None:
        """Ejecuta una iteración del bucle cognitivo."""
        tick_start = time.time()

        # 1. OBSERVE
        observations = await self._observe()

        # 2. PREDICT
        prediction = await self._predict(observations)

        # 3. EVALUATE
        surprise = await self._evaluate(prediction, observations)

        # 4. DECIDE
        decision = await self._decide(surprise, observations)

        # 5. ACT
        if decision.get("should_act"):
            thought = await self._act(decision, observations, surprise)
            if thought:
                self.thoughts.append(thought)
                # Sprint 5.13 B4-bis — Truncar thoughts para prevenir memory leak.
                if hasattr(self, '_max_thoughts') and len(self.thoughts) > self._max_thoughts:
                    del self.thoughts[:-self._max_thoughts]
                self.state.register_thought()
                if self.on_thought_callback:
                    await self.on_thought_callback(thought)

        # Actualizar estado
        dt = time.time() - tick_start
        self.state.tick(dt)
        if surprise > 0.3:
            self.state.stimulate(intensity=surprise)

        logger.debug(
            f"Tick {self.state.iteration_count}: obs={len(observations)}, "
            f"surprise={surprise:.3f}, decision={decision.get('action', 'none')}, "
            f"energy={self.state.energy:.2f}, fatigue={self.state.fatigue:.2f}"
        )

    async def _observe(self) -> List[Observation]:
        """Recoge observaciones de todos los sentidos."""
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
        # Mantener historial acotado
        if len(self.observations) > 1000:
            self.observations = self.observations[-500:]

        return observations

    async def _predict(self, observations: List[Observation]) -> Dict[str, Any]:
        """World Model predice el próximo estado."""
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
        """Compara predicción con realidad, devuelve sorpresa (0-1)."""
        if not self.world_model or not observations:
            return 0.0

        try:
            surprise = await self.world_model.compute_surprise(prediction, observations)
            return float(surprise)
        except Exception as e:
            logger.warning(f"WorldModel compute_surprise failed: {e}")
            return 0.0

    async def _decide(
        self, surprise: float, observations: List[Observation]
    ) -> Dict[str, Any]:
        """Decide qué hacer basado en sorpresa y observaciones."""
        # Si hay mucha sorpresa, pensar
        if surprise > 0.5:
            return {
                "should_act": True,
                "action": "think_on_surprise",
                "reason": f"high_surprise={surprise:.3f}",
                "target_subagent": "speaker",
            }

        # Si hay input del usuario, responder
        user_obs = [o for o in observations if o.source == "user"]
        if user_obs:
            return {
                "should_act": True,
                "action": "respond_to_user",
                "reason": "user_input",
                "target_subagent": "speaker",
                "user_content": user_obs[-1].content,
            }

        # Si el organismo debe pensar (según estado), generar pensamiento autónomo
        if self.state.should_think() and self.state.energy > 0.4:
            # No generar pensamiento en cada tick, solo ~30% de las veces
            import random

            if random.random() < 0.3:
                return {
                    "should_act": True,
                    "action": "autonomous_thought",
                    "reason": "proactive_thinking",
                    "target_subagent": "speaker",
                }

        # Si no, descansar o consolidar
        if self.state.fatigue > 0.6:
            return {
                "should_act": False,
                "action": "rest",
                "reason": f"high_fatigue={self.state.fatigue:.3f}",
            }

        return {
            "should_act": False,
            "action": "observe_only",
            "reason": "low_priority",
        }

    async def _act(
        self,
        decision: Dict[str, Any],
        observations: List[Observation],
        surprise: float,
    ) -> Optional[Thought]:
        """Ejecuta la decisión, genera pensamiento si procede."""
        target = decision.get("target_subagent")
        action = decision.get("action")

        # Buscar sub-agente objetivo
        target_agent = None
        for agent in self.subagents:
            if agent.__class__.__name__.lower().startswith(target.lower()[:4]):
                target_agent = agent
                break

        if not target_agent:
            # Fallback: cualquier sub-agente que pueda hablar
            for agent in self.subagents:
                if hasattr(agent, "generate_thought"):
                    target_agent = agent
                    break

        if not target_agent:
            logger.warning(f"No sub-agent found for action: {action}")
            return None

        try:
            # Contexto para el sub-agente
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
                metadata={"decision": decision.get("reason", "")},
            )
        except Exception as e:
            logger.error(f"Sub-agent {target_agent.__class__.__name__} failed: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del bucle."""
        return {
            "iterations": self.state.iteration_count,
            "observations": len(self.observations),
            "thoughts": len(self.thoughts),
            "predictions": len(self.predictions),
            "energy": self.state.energy,
            "fatigue": self.state.fatigue,
            "arousal": self.state.arousal,
            "attention": self.state.attention,
        }
