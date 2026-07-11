"""
ZOE v1.0 — Metabolism

Extiende InternalState con ciclos dormir/despertar + consolidación.
Conectado con CognitivePhysics (should_rest, should_consolidate) y
CognitiveTensions (rest_vs_productivity).

Estados del metabolismo:
- awake: estado normal, sentido activos, atención alta
- drowsy: fatiga acumulada, reducción de capacidad
- sleeping: consolidación de memoria, recarga de energía
- waking: transición, restauración gradual

El metabolismo hace aparecer comportamientos inteligentes emergentes:
- Si fatiga alta → dormir (no seguir pensando ineficientemente)
- Si sleeping → consolidar memoria (reorganizar, fusionar, generalizar)
- Si waking → restaurar gradualmente (no saltar a full atención)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List

from ..core.state import InternalState

logger = logging.getLogger(__name__)


class MetabolicState(str, Enum):
    """Estados del metabolismo."""

    AWAKE = "awake"
    DROWSY = "drowsy"
    SLEEPING = "sleeping"
    WAKING = "waking"


@dataclass
class Metabolism:
    """
    Metabolismo del organismo.

    Extiende InternalState con:
    - Estados (awake, drowsy, sleeping, waking)
    - Ciclos dormir/despertar
    - Consolidación de memoria en sueño
    - Presupuesto de cómputo
    """

    # Estado base (composición, no herencia — para compatibilidad)
    internal_state: InternalState = field(default_factory=InternalState)

    # Estado metabólico
    state: MetabolicState = MetabolicState.AWAKE

    # Umbrales
    drowsy_threshold: float = 0.6  # fatiga > 0.6 → drowsy
    sleep_threshold: float = 0.8  # fatiga > 0.8 → sleeping
    wake_threshold: float = 0.3  # fatiga < 0.3 → awake

    # Tiempos
    last_sleep_time: float = 0.0
    last_wake_time: float = field(default_factory=time.time)
    sleep_duration: float = 0.0
    total_sleep_cycles: int = 0
    total_consolidation_operations: int = 0

    # Presupuesto
    compute_budget: float = 1.0  # presupuesto total por ciclo awake
    compute_spent: float = 0.0  # gastado en ciclo actual

    # Consolidación (qué hacer al dormir)
    pending_consolidation: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.last_sleep_time == 0.0:
            self.last_sleep_time = time.time()

    @property
    def energy(self) -> float:
        return self.internal_state.energy

    @property
    def fatigue(self) -> float:
        return self.internal_state.fatigue

    @property
    def arousal(self) -> float:
        return self.internal_state.arousal

    @property
    def attention(self) -> float:
        return self.internal_state.attention

    @property
    def iteration_count(self) -> int:
        return self.internal_state.iteration_count

    def tick(self, dt: float) -> None:
        """Actualiza el metabolismo tras dt segundos."""
        self.internal_state.tick(dt)

        # Actualizar estado metabólico según fatiga
        self._update_metabolic_state()

        # Si está durmiendo, consolidar
        if self.state == MetabolicState.SLEEPING:
            self._consolidate_during_sleep()

    def _update_metabolic_state(self) -> None:
        """Transiciones de estado metabólico."""
        fatigue = self.internal_state.fatigue

        if self.state == MetabolicState.AWAKE:
            if fatigue > self.drowsy_threshold:
                self.state = MetabolicState.DROWSY
                logger.debug(f"Metabolism: AWAKE → DROWSY (fatigue={fatigue:.2f})")

        if self.state == MetabolicState.DROWSY:
            if fatigue > self.sleep_threshold:
                self._go_to_sleep()
            elif fatigue < self.wake_threshold:
                self.state = MetabolicState.AWAKE
                logger.debug(f"Metabolism: DROWSY → AWAKE (fatigue={fatigue:.2f})")

        if self.state == MetabolicState.SLEEPING:
            # Despertar cuando energía recuperada
            if self.internal_state.energy > 0.8 and self.internal_state.fatigue < 0.2:
                self._wake_up()

        if self.state == MetabolicState.WAKING:
            # Transición rápida a awake
            self.state = MetabolicState.AWAKE
            self.last_wake_time = time.time()
            logger.debug("Metabolism: WAKING → AWAKE")

    def _go_to_sleep(self) -> None:
        """Transición a sleeping."""
        self.state = MetabolicState.SLEEPING
        self.last_sleep_time = time.time()
        self.total_sleep_cycles += 1
        logger.info(
            f"Metabolism: DROWSY → SLEEPING (cycle #{self.total_sleep_cycles})"
        )

    def _wake_up(self) -> None:
        """Transición a waking."""
        self.sleep_duration = time.time() - self.last_sleep_time
        self.state = MetabolicState.WAKING
        # Reset fatiga tras dormir
        self.internal_state.fatigue = 0.0
        self.internal_state.energy = 1.0
        logger.info(
            f"Metabolism: SLEEPING → WAKING (slept {self.sleep_duration:.1f}s, "
            f"consolidated {self.total_consolidation_operations} ops)"
        )

    def _consolidate_during_sleep(self) -> None:
        """Consolida memoria durante el sueño."""
        # En Fase 1: marcar operaciones pendientes
        # En Fase 3: ejecutar consolidación real con LivingMemory
        if self.pending_consolidation:
            op = self.pending_consolidation.pop(0)
            self.total_consolidation_operations += 1
            logger.debug(f"Metabolism: consolidating '{op}' during sleep")

    def should_sleep(self, physics=None) -> bool:
        """Decide si es hora de dormir."""
        if self.state == MetabolicState.SLEEPING:
            return False  # ya durmiendo

        # Fatiga alta
        if self.internal_state.fatigue > self.sleep_threshold:
            return True

        # Physics sugiere descanso
        if physics and physics.should_rest():
            return True

        # Presupuesto agotado
        if self.compute_spent >= self.compute_budget:
            return True

        return False

    def should_wake(self) -> bool:
        """Decide si es hora de despertar."""
        if self.state != MetabolicState.SLEEPING:
            return False

        # Energía recuperada
        if self.internal_state.energy > 0.8 and self.internal_state.fatigue < 0.2:
            return True

        # Hay input del usuario (despertar por estímulo)
        # (esto se maneja externamente via stimulate())

        return False

    def stimulate(self, intensity: float = 0.5) -> None:
        """Estímulo externo (input del usuario, sorpresa, etc.)."""
        self.internal_state.stimulate(intensity)

        # Si está durmiendo y el estímulo es fuerte, despertar
        if self.state == MetabolicState.SLEEPING and intensity > 0.7:
            self._wake_up()
            logger.info("Metabolism: woken up by strong stimulus")

    def spend_compute(self, amount: float) -> bool:
        """
        Gasta cómputo del presupuesto.

        Returns:
            True si había presupuesto, False si agotado
        """
        if self.compute_spent + amount > self.compute_budget:
            return False
        self.compute_spent += amount
        return True

    def reset_budget(self) -> None:
        """Reset del presupuesto (tras dormir)."""
        self.compute_spent = 0.0
        self.compute_budget = 1.0

    def queue_consolidation(self, operation: str) -> None:
        """Encola operación de consolidación para el próximo sueño."""
        self.pending_consolidation.append(operation)

    def to_dict(self) -> Dict[str, Any]:
        """Serialización."""
        return {
            "internal_state": self.internal_state.to_dict(),
            "metabolic_state": self.state.value,
            "drowsy_threshold": self.drowsy_threshold,
            "sleep_threshold": self.sleep_threshold,
            "wake_threshold": self.wake_threshold,
            "last_sleep_time": self.last_sleep_time,
            "last_wake_time": self.last_wake_time,
            "sleep_duration": self.sleep_duration,
            "total_sleep_cycles": self.total_sleep_cycles,
            "total_consolidation_operations": self.total_consolidation_operations,
            "compute_budget": self.compute_budget,
            "compute_spent": self.compute_spent,
            "pending_consolidation": self.pending_consolidation,
        }

    def summary(self) -> str:
        """Resumen legible."""
        return (
            f"Metabolism(state={self.state.value}, "
            f"energy={self.energy:.2f}, fatigue={self.fatigue:.2f}, "
            f"budget={self.compute_spent:.2f}/{self.compute_budget:.2f}, "
            f"sleep_cycles={self.total_sleep_cycles})"
        )
