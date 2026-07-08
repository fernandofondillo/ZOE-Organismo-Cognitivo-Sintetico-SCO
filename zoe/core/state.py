"""
ZOE v1.0 — Internal State

Estado interno del organismo (homeostasis mínima para Fase 0).
En fases posteriores evoluciona a Metabolismo completo.

Variables:
- attention (0-1): cuánto cómputo dedicar a cada iteración
- energy (0-1): presupuesto de cómputo restante (se recarga en reposo)
- arousal (0-1): nivel de activación (alto = urgente)
- fatigue (0-1): acumulada por uso, reduce profundidad
- iteration_count: cuántas iteraciones del bucle han pasado
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class InternalState:
    """Estado interno del organismo ZOE."""

    # Homeostasis (0-1)
    attention: float = 0.5
    energy: float = 1.0
    arousal: float = 0.3
    fatigue: float = 0.0

    # Contadores
    iteration_count: int = 0
    last_input_timestamp: float = field(default_factory=time.time)
    last_thought_timestamp: float = field(default_factory=time.time)

    # Configuración
    fatigue_per_iteration: float = 0.01
    energy_recharge_per_second: float = 0.005
    arousal_decay_per_second: float = 0.01

    def tick(self, dt: float) -> None:
        """Actualiza el estado tras `dt` segundos transcurridos."""
        # Fatigue aumenta con cada iteración
        self.fatigue = min(1.0, self.fatigue + self.fatigue_per_iteration)

        # Energy se recarga con el tiempo (especialmente sin actividad)
        self.energy = min(1.0, self.energy + self.energy_recharge_per_second * dt)

        # Arousal decae con el tiempo si no hay eventos
        self.arousal = max(0.0, self.arousal - self.arousal_decay_per_second * dt)

        # Attention depende de energy y fatigue
        self.attention = max(0.1, min(1.0, self.energy * (1.0 - self.fatigue * 0.5)))

        self.iteration_count += 1

    def stimulate(self, intensity: float = 0.5) -> None:
        """Estimula el estado (por input o sorpresa)."""
        self.arousal = min(1.0, self.arousal + intensity)
        self.last_input_timestamp = time.time()

    def register_thought(self) -> None:
        """Registra que se generó un pensamiento."""
        self.last_thought_timestamp = time.time()

    def should_think(self) -> bool:
        """Decide si el organismo debe pensar ahora o descansar."""
        # Si hay arousal alto, pensar
        if self.arousal > 0.4:
            return True
        # Si hay energía y no mucha fatiga, pensar
        if self.energy > 0.3 and self.fatigue < 0.7:
            return True
        # Si no, descansar
        return False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InternalState":
        return cls(**d)
