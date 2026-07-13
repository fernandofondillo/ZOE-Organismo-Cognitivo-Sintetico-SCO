"""
ZOE v1.0 -- Global Workspace (Teoria de Bernard Baars)

Implementa la "conciencia" del organismo: los 12 sub-agentes envian
propuestas que compiten por acceso al espacio de trabajo global.
Las ganadoras se "emiten" a todos los sub-agentes.

Basado en: Baars, B.J. (1988) "A Cognitive Theory of Consciousness"
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Proposal:
    """Propuesta de un sub-agente para el Global Workspace."""

    # Autor
    subagent_name: str = ""
    content: str = ""

    # Scoring (0-1)
    relevance: float = 0.0   # 50% del score: relacion con contexto
    urgency: float = 0.0     # 30% del score: urgencia
    novelty: float = 0.0     # 20% del score: novedad vs pensamientos recientes

    # Coste
    energy_cost: float = 0.1  # cuanta energia consume ejecutarla

    # Metadata
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Score computado (se calcula en compete)
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subagent_name": self.subagent_name,
            "content": self.content[:200],
            "relevance": self.relevance,
            "urgency": self.urgency,
            "novelty": self.novelty,
            "energy_cost": self.energy_cost,
            "score": self.score,
            "timestamp": self.timestamp,
        }


class GlobalWorkspace:
    """
    Espacio de trabajo global (Baars).

    Los sub-agentes envian propuestas que compiten por acceso.
    Las ganadoras se emiten a todos (broadcast).

    Attributes:
        max_proposals: maximo propuestas a aceptar por tick
        broadcast_capacity: cuantas propuestas ganan (tipicamente 1-3)
    """

    def __init__(self, max_proposals: int = 12, broadcast_capacity: int = 3):
        self.max_proposals = max_proposals
        self.broadcast_capacity = broadcast_capacity

        # Propuestas del tick actual
        self._proposals: List[Proposal] = []

        # Ganadores del ultimo tick
        self._winners: List[Proposal] = []

        # Historial
        self._total_ticks: int = 0
        self._total_proposals: int = 0
        self._total_winners: int = 0

        logger.info(f"GlobalWorkspace: capacity={broadcast_capacity}, max_proposals={max_proposals}")

    def submit(self, proposal: Proposal) -> bool:
        """Envia una propuesta al workspace.

        Returns:
            True si se acepto, False si esta lleno.
        """
        if len(self._proposals) >= self.max_proposals:
            logger.debug(f"Workspace full ({self.max_proposals}), proposal rejected")
            return False

        self._proposals.append(proposal)
        return True

    def submit_batch(self, proposals: List[Proposal]) -> int:
        """Envia un lote de propuestas.

        Returns:
            Numero de propuestas aceptadas.
        """
        accepted = 0
        for p in proposals:
            if self.submit(p):
                accepted += 1
        return accepted

    def compete(self, available_energy: float = 1.0) -> List[Proposal]:
        """
        Compite y selecciona las mejores propuestas.

        El score se calcula como:
        - relevance * 0.50
        - urgency * 0.30
        - novelty * 0.20

        El presupuesto energetico limita cuantas pueden ganar.

        Args:
            available_energy: energia disponible (0-1, afecta cuantas ganan)

        Returns:
            Lista de propuestas ganadoras.
        """
        if not self._proposals:
            self._winners = []
            return []

        # Calcular score para cada propuesta
        for p in self._proposals:
            p.score = p.relevance * 0.50 + p.urgency * 0.30 + p.novelty * 0.20

        # Ordenar por score descendente
        sorted_proposals = sorted(self._proposals, key=lambda x: x.score, reverse=True)

        # Determinar cuantas pueden ganar segun energia disponible
        # broadcast_capacity es el maximo, pero la energia puede limitar
        effective_capacity = max(1, min(
            self.broadcast_capacity,
            int(self.broadcast_capacity * available_energy) + 1
        ))

        # Seleccionar ganadores (hasta effective_capacity)
        winners = []
        remaining_energy = available_energy
        for p in sorted_proposals:
            if len(winners) >= effective_capacity:
                break
            if p.energy_cost <= remaining_energy:
                winners.append(p)
                remaining_energy -= p.energy_cost

        self._winners = winners
        self._total_winners += len(winners)
        self._total_proposals += len(self._proposals)
        self._total_ticks += 1

        logger.debug(
            f"Workspace compete: {len(self._proposals)} proposals, "
            f"{len(winners)} winners, energy={available_energy:.2f}"
        )

        return winners

    def broadcast(self) -> List[Proposal]:
        """
        Emite las propuestas ganadoras a todos los sub-agentes.

        En la implementacion actual, esto devuelve los ganadores
        para que el cognitive_loop los procese.

        Returns:
            Lista de propuestas ganadoras del ultimo compete().
        """
        return list(self._winners)

    def clear(self) -> None:
        """Limpia las propuestas del tick actual."""
        self._proposals = []

    def get_winners(self) -> List[Proposal]:
        """Devuelve los ganadores del ultimo tick."""
        return list(self._winners)

    def get_stats(self) -> Dict[str, Any]:
        """Estadisticas del workspace."""
        return {
            "total_ticks": self._total_ticks,
            "total_proposals": self._total_proposals,
            "total_winners": self._total_winners,
            "win_rate": (
                self._total_winners / max(1, self._total_proposals)
            ),
            "current_proposals": len(self._proposals),
            "current_winners": len(self._winners),
            "broadcast_capacity": self.broadcast_capacity,
            "max_proposals": self.max_proposals,
        }

    def summary(self) -> str:
        """Resumen legible."""
        s = self.get_stats()
        return (
            f"GlobalWorkspace(ticks={s['total_ticks']}, "
            f"proposals={s['total_proposals']}, "
            f"winners={s['total_winners']}, "
            f"win_rate={s['win_rate']:.1%})"
        )
