"""
ZOE v1.0 — Meta-Cognition (System 1 / System 2)

Meta-cognición que decide cuándo pasar de respuesta rápida (System 1)
a deliberación profunda (System 2).

Inspiración: Kahneman (System 1/2), CognitivePhysics (uncertainty_pressure).

- System 1: respuesta rápida con patrón aprendido. Latencia <1s.
- System 2: razonamiento paso a paso. Latencia 5-30s.
- Meta-cognición decide cuándo pasar de 1 a 2 según:
  - Confianza de System 1
  - Stakes (importancia de la decisión)
  - Energía disponible
  - Presión de incertidumbre
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class MetaCognition:
    """
    Meta-cognición: decide System 1 vs System 2.

    System 1 (rápido): responde con patrón aprendido.
    System 2 (deliberativo): razona paso a paso con todos los sub-agentes.
    """

    # Thresholds
    confidence_threshold_system2: float = 0.5  # si confianza < esto, System 2
    stakes_threshold_system2: float = 0.6  # si stakes > esto, System 2
    energy_threshold_system2: float = 0.3  # si energía < esto, no System 2

    # Histórico
    _system1_uses: int = 0
    _system2_uses: int = 0
    _system2_triggered_by: Dict[str, int] = field(default_factory=dict)

    def evaluate_confidence(
        self,
        response: str,
        surprise: float,
        physics: Any = None,
    ) -> float:
        """
        Evalúa la confianza en una respuesta de System 1.

        Returns:
            confianza 0-1 (alto = System 1 suficiente, bajo = System 2 necesario)
        """
        confidence = 1.0

        # Sorpresa alta = baja confianza
        confidence -= surprise * 0.5

        # Incertidumbre acumulada = baja confianza
        if physics:
            uncertainty = getattr(physics, "uncertainty_pressure", 0.0)
            confidence -= uncertainty * 0.3

            # Potencial creativo alto = baja confianza (hay múltiples opciones)
            creative = getattr(physics, "creative_potential", 0.0)
            if creative > 0.7:
                confidence -= 0.1

        # Respuesta muy corta o vacía = baja confianza
        if not response or len(response) < 20:
            confidence -= 0.3

        return max(0.0, min(1.0, confidence))

    def should_deliberate(
        self,
        confidence: float,
        stakes: float = 0.5,
        energy: float = 1.0,
        arousal: float = 0.3,
    ) -> Tuple[bool, str]:
        """
        Decide si activar System 2 (deliberación).

        Args:
            confidence: confianza en System 1 (0-1)
            stakes: importancia de la decisión (0-1)
            energy: energía disponible (0-1)
            arousal: nivel de activación (0-1)

        Returns:
            (should_deliberate, reason)
        """
        # Sin energía para System 2
        if energy < self.energy_threshold_system2:
            self._system1_uses += 1
            return False, f"low_energy ({energy:.2f} < {self.energy_threshold_system2})"

        # Confianza baja
        if confidence < self.confidence_threshold_system2:
            self._system2_uses += 1
            self._system2_triggered_by["low_confidence"] = \
                self._system2_triggered_by.get("low_confidence", 0) + 1
            return True, f"low_confidence ({confidence:.2f} < {self.confidence_threshold_system2})"

        # Stakes altos
        if stakes > self.stakes_threshold_system2:
            self._system2_uses += 1
            self._system2_triggered_by["high_stakes"] = \
                self._system2_triggered_by.get("high_stakes", 0) + 1
            return True, f"high_stakes ({stakes:.2f} > {self.stakes_threshold_system2})"

        # Arousal muy alto (urgencia) → System 1 (respuesta rápida)
        if arousal > 0.9:
            self._system1_uses += 1
            return False, f"high_arousal ({arousal:.2f}), fast response needed"

        # Default: System 1
        self._system1_uses += 1
        return False, "sufficient_confidence"

    def evaluate_stakes(
        self,
        context: Dict[str, Any],
    ) -> float:
        """
        Evalúa la importancia (stakes) de una decisión.

        Returns:
            stakes 0-1 (alto = merece System 2)
        """
        stakes = 0.3  # default

        # Si hay input del usuario, stakes más altos
        observations = context.get("recent_observations", [])
        if any(o.get("source") == "user" for o in observations):
            stakes += 0.3

        # Si hay sorpresa alta, stakes más altos
        surprise = context.get("surprise", 0.0)
        stakes += surprise * 0.2

        # Si hay intención de alta prioridad, stakes más altos
        intentions = context.get("intentions", [])
        if intentions:
            max_priority = max(i.get("priority", 0) for i in intentions) if intentions else 0
            stakes += max_priority * 0.2

        return min(1.0, stakes)

    def get_stats(self) -> Dict[str, Any]:
        total = self._system1_uses + self._system2_uses
        return {
            "system1_uses": self._system1_uses,
            "system2_uses": self._system2_uses,
            "system2_rate": self._system2_uses / max(1, total),
            "triggered_by": dict(self._system2_triggered_by),
            "thresholds": {
                "confidence": self.confidence_threshold_system2,
                "stakes": self.stakes_threshold_system2,
                "energy": self.energy_threshold_system2,
            },
        }

    def summary(self) -> str:
        return (
            f"MetaCog(s1={self._system1_uses}, s2={self._system2_uses}, "
            f"s2_rate={self._system2_uses / max(1, self._system1_uses + self._system2_uses):.2f})"
        )
