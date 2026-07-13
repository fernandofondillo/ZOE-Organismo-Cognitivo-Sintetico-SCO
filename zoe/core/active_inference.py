"""
ZOE v1.0 — Active Inference (simplificado, Fase 2.2)

Implementación simplificada del Free Energy Principle de Friston.
No requiere pymdp; usa heurística basada en minimización de sorpresa esperada.

Concepto: el organismo elige acciones que reducen la sorpresa esperada.
En lugar de cálculo variacional completo, usa:
- Modelo de transiciones aprendido (qué pasa si hago X)
- Selección de acción que minimiza sorpresa esperada
- Actualización del modelo tras cada acción

Si pymdp está disponible, se puede extender en el futuro.
"""

from __future__ import annotations

import logging
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ActiveInferenceLoop:
    """
    Bucle de inferencia activa simplificado.

    El organismo tiene un modelo generativo del mundo que le permite
    predecir qué pasará si ejecuta cada acción. Elige la acción que
    minimiza la energía libre esperada (sorpresa esperada).
    """

    # Modelo de transiciones: (state, action) -> {next_state: probability}
    _transition_model: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)

    # Modelo de observaciones: state -> {observation_type: probability}
    _observation_model: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Creencias actuales sobre el estado: {state: probability}
    _beliefs: Dict[str, float] = field(default_factory=dict)

    # Acciones disponibles
    _actions: List[str] = field(default_factory=lambda: [
        "observe", "think", "communicate", "explore", "rest", "consolidate"
    ])

    # Histórico de acciones y resultados
    _action_history: List[Tuple[str, str, float]] = field(default_factory=list)

    # Parámetros
    learning_rate: float = 0.1
    exploration_bonus: float = 0.1  # bonus para exploración
    discount_factor: float = 0.95

    def update_beliefs(self, observation_source: str, observation_content: str) -> None:
        """Actualiza creencias sobre el estado actual dado una observación."""
        # Simplificado: el estado es el source de la observación
        # Actualizar creencias con bayesiano simplificado
        total = sum(self._beliefs.values()) if self._beliefs else 1.0

        if observation_source not in self._beliefs:
            self._beliefs[observation_source] = 0.1 / max(total, 0.1)

        # Aumentar creencia en el estado observado
        for state in self._beliefs:
            if state == observation_source:
                self._beliefs[state] += self.learning_rate
            else:
                self._beliefs[state] *= (1 - self.learning_rate * 0.5)

        # Normalizar
        total = sum(self._beliefs.values())
        if total > 0:
            self._beliefs = {k: v / total for k, v in self._beliefs.items()}

    def learn_transition(self, state: str, action: str, next_state: str) -> None:
        """Aprende una transición: (state, action) -> next_state."""
        key = f"{state}|{action}"
        if key not in self._transition_model:
            self._transition_model[key] = {}
        self._transition_model[key][next_state] = \
            self._transition_model[key].get(next_state, 0) + 1

        # Normalizar
        total = sum(self._transition_model[key].values())
        for s in self._transition_model[key]:
            self._transition_model[key][s] /= total

    def predict_next_state(self, state: str, action: str) -> Dict[str, float]:
        """Predice distribución del próximo estado dado estado y acción."""
        key = f"{state}|{action}"
        if key in self._transition_model:
            return dict(self._transition_model[key])
        # Si no hay modelo, distribución uniforme sobre estados conocidos
        known_states = list(self._beliefs.keys()) or ["unknown"]
        return {s: 1.0 / len(known_states) for s in known_states}

    def expected_surprise(self, state: str, action: str) -> float:
        """
        Calcula sorpresa esperada para una acción desde un estado.
        Menor = mejor acción (menos sorpresa esperada).
        """
        next_states = self.predict_next_state(state, action)
        expected = 0.0

        for next_state, prob in next_states.items():
            # Sorpresa = entropía de Shannon: -sum(prob * log(prob))
            if prob > 0:
                surprise = -prob * math.log(prob)
            else:
                surprise = 0.0
            expected += prob * surprise

        # Bonus de exploración: acciones poco probadas tienen bonus
        key = f"{state}|{action}"
        times_tried = sum(self._transition_model.get(key, {}).values())
        exploration = self.exploration_bonus / (times_tried + 1)

        return expected - exploration

    def select_action(self, current_state: str, available_actions: List[str] = None) -> str:
        """
        Selecciona la acción que minimiza sorpresa esperada.

        Esto es el núcleo del Active Inference: elegir acciones que
        reducen incertidumbre sobre el mundo.
        """
        actions = available_actions or self._actions

        # Calcular sorpresa esperada para cada acción
        action_scores: List[Tuple[str, float]] = []
        for action in actions:
            score = self.expected_surprise(current_state, action)
            action_scores.append((action, score))

        # Seleccionar la de menor sorpresa esperada
        action_scores.sort(key=lambda x: x[1])
        best_action = action_scores[0][0] if action_scores else "observe"

        return best_action

    def record_action_result(
        self, state: str, action: str, next_state: str, surprise: float
    ) -> None:
        """Registra el resultado de una acción para aprendizaje."""
        self._action_history.append((action, next_state, surprise))
        self.learn_transition(state, action, next_state)

        # Mantener histórico acotado
        if len(self._action_history) > 200:
            self._action_history = self._action_history[-100:]

    def get_current_state(self) -> str:
        """Devuelve el estado más probable actual."""
        if not self._beliefs:
            return "unknown"
        return max(self._beliefs, key=self._beliefs.get)

    def get_beliefs(self) -> Dict[str, float]:
        """Devuelve creencias actuales."""
        return dict(self._beliefs)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "states_known": len(self._beliefs),
            "transitions_learned": sum(len(v) for v in self._transition_model.values()),
            "actions_available": len(self._actions),
            "actions_taken": len(self._action_history),
            "current_state": self.get_current_state(),
            "top_belief": max(self._beliefs.values()) if self._beliefs else 0.0,
        }

    def summary(self) -> str:
        return (
            f"ActiveInference(state={self.get_current_state()}, "
            f"transitions={sum(len(v) for v in self._transition_model.values())}, "
            f"actions_taken={len(self._action_history)})"
        )
