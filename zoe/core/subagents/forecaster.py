"""
ZOE v1.0 — Forecaster sub-agent

Usa el World Model para predecir próximos estados.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class Forecaster:
    """
    Forecaster: predice próximos estados usando World Model.

    En Fase 0: reporta predicciones del World Model en lenguaje.
    En fases posteriores: genera múltiples hipótesis contrafactuales.
    """

    def __init__(self, world_model=None):
        self.world_model = world_model
        self._last_prediction: Optional[Dict[str, Any]] = None
        self._last_surprise: float = 0.0

    def update(self, prediction: Dict[str, Any], surprise: float) -> None:
        """Actualiza con última predicción y sorpresa observada."""
        self._last_prediction = prediction
        self._last_surprise = surprise

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento sobre predicción y sorpresa."""
        surprise = context.get("surprise", 0.0)
        prediction = self._last_prediction or {}

        confidence = prediction.get("confidence", 0.0)
        strategy = prediction.get("strategy", "unknown")

        if surprise > 0.7:
            return (
                f"Mi predicción falló significativamente (sorpresa={surprise:.2f}). "
                f"El entorno no se comporta como esperaba. Necesito actualizar mi modelo."
            )
        elif surprise > 0.4:
            return (
                f"Detecto desviación moderada (sorpresa={surprise:.2f}). "
                f"Mi modelo tenía confianza {confidence:.2f}. Ajustando expectativas."
            )
        elif strategy == "no_history":
            return (
                "Aún no tengo historial suficiente para predecir. "
                "Acumulando observaciones para construir mi modelo del entorno."
            )
        elif surprise < 0.1:
            return (
                f"El entorno se comporta como esperaba (sorpresa={surprise:.2f}, "
                f"confianza={confidence:.2f}). Patrón estable."
            )
        else:
            return (
                f"Predicción razonable (sorpresa={surprise:.2f}, "
                f"confianza={confidence:.2f}). Monitoreando."
            )
