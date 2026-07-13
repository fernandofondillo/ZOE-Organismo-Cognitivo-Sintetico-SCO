"""
ZOE v1.0 — Global Workspace (Fase 2.5)

Espacio compartido de capacidad limitada donde los sub-agentes compiten
por acceso. El ganador hace "broadcast" a todos los demás.

Inspiración: Global Workspace Theory de Baars.

Diferencia con bucle lineal (Fase 0-1):
- En Fase 0-1: el bucle decide qué sub-agente ejecutar en secuencia
- En Fase 2: todos los sub-agentes proponen acciones, el workspace
  selecciona la ganadora por relevancia, urgencia, novedad, energía
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Proposal:
    """Propuesta de un sub-agente para el workspace."""

    subagent_name: str
    action: str  # qué quiere hacer
    content: str  # pensamiento o acción propuesta
    relevance: float = 0.5  # 0-1, cuán relevante para el contexto actual
    urgency: float = 0.5  # 0-1, cuán urgente
    novelty: float = 0.5  # 0-1, cuán novedoso
    energy_cost: float = 0.3  # 0-1, cuánta energía requiere
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def score(self, available_energy: float = 1.0) -> float:
        """Puntaje de la propuesta para selección."""
        # Ponderación: relevancia + urgencia + novedad, penalizado por coste
        base = (
            self.relevance * 0.4
            + self.urgency * 0.3
            + self.novelty * 0.2
            - self.energy_cost * 0.1
        )
        # Penalizar si el coste excede energía disponible
        if self.energy_cost > available_energy:
            base *= 0.3
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subagent_name": self.subagent_name,
            "action": self.action,
            "content": self.content[:100],
            "relevance": self.relevance,
            "urgency": self.urgency,
            "novelty": self.novelty,
            "energy_cost": self.energy_cost,
            "score": self.score(),
            "timestamp": self.timestamp,
        }


class GlobalWorkspace:
    """
    Espacio compartido donde los sub-agentes compiten.

    Flujo:
    1. Cada sub-agente propone una acción al workspace
    2. El workspace selecciona la propuesta con mayor score
    3. La propuesta ganadora hace broadcast a todos los sub-agentes
    4. Los sub-agentes actualizan su estado interno según el broadcast
    """

    def __init__(self, max_proposals: int = 12, broadcast_capacity: int = 3):
        self.max_proposals = max_proposals
        self.broadcast_capacity = broadcast_capacity  # cuántas propuestas ganan

        # Estado actual del workspace
        self._proposals: List[Proposal] = []
        self._winners: List[Proposal] = []
        self._broadcast_state: Dict[str, Any] = {}

        # Estadísticas
        self._total_competitions: int = 0
        self._winner_history: List[str] = []  # nombres de sub-agentes ganadores
        self._broadcasts_made: int = 0

    def submit(self, proposal: Proposal) -> None:
        """Un sub-agente envía una propuesta al workspace."""
        self._proposals.append(proposal)
        if len(self._proposals) > self.max_proposals:
            # Mantener solo las de mayor score
            self._proposals.sort(key=lambda p: p.score(), reverse=True)
            self._proposals = self._proposals[: self.max_proposals]

    def submit_batch(self, proposals: List[Proposal]) -> None:
        """Envía múltiples propuestas."""
        for p in proposals:
            self.submit(p)

    def compete(self, available_energy: float = 1.0) -> List[Proposal]:
        """
        Los sub-agentes compiten. Selecciona los ganadores.

        Returns:
            Lista de propuestas ganadoras (top N por score)
        """
        if not self._proposals:
            return []

        # Ordenar por score
        self._proposals.sort(
            key=lambda p: p.score(available_energy), reverse=True
        )

        # Seleccionar ganadores (top broadcast_capacity)
        winners = self._proposals[: self.broadcast_capacity]

        self._winners = winners
        self._total_competitions += 1

        # Registrar ganadores
        for w in winners:
            self._winner_history.append(w.subagent_name)
        if len(self._winner_history) > 100:
            self._winner_history = self._winner_history[-50:]

        # Crear broadcast state
        self._broadcast_state = {
            "winning_actions": [w.action for w in winners],
            "winning_contents": [w.content[:50] for w in winners],
            "winning_subagents": [w.subagent_name for w in winners],
            "timestamp": time.time(),
        }

        return winners

    def broadcast(self) -> Dict[str, Any]:
        """
        Devuelve el estado del broadcast para que todos los sub-agentes
        se actualicen.

        Returns:
            Estado del broadcast (qué ganó, qué debe hacer cada sub-agente)
        """
        self._broadcasts_made += 1
        return dict(self._broadcast_state)

    def clear(self) -> None:
        """Limpia propuestas para la próxima iteración."""
        self._proposals = []

    def get_winners(self) -> List[Proposal]:
        """Devuelve los ganadores actuales."""
        return self._winners

    def get_stats(self) -> Dict[str, Any]:
        # Distribución de ganadores
        winner_dist: Dict[str, int] = {}
        for name in self._winner_history:
            winner_dist[name] = winner_dist.get(name, 0) + 1

        return {
            "total_competitions": self._total_competitions,
            "broadcasts_made": self._broadcasts_made,
            "current_proposals": len(self._proposals),
            "current_winners": len(self._winners),
            "winner_distribution": winner_dist,
            "broadcast_capacity": self.broadcast_capacity,
        }

    def summary(self) -> str:
        return (
            f"GlobalWorkspace(competitions={self._total_competitions}, "
            f"broadcasts={self._broadcasts_made}, "
            f"proposals={len(self._proposals)}, "
            f"winners={len(self._winners)})"
        )
