"""
ZOE v1.0 — Intentionality Motor

Genera continuamente nuevas intenciones. No responde preguntas.
Produce deseos cognitivos.

Un organismo nunca deja de generar propósitos. El IntentionalityMotor
es la fuente continua de intenciones que alimentan el bucle cognitivo.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Intention:
    """Una intención generada por el organismo."""

    id: str
    description: str  # descripción legible: "Quiero entender X"
    type: str  # explore | understand | consolidate | communicate | verify | create
    priority: float  # 0-1
    source: str  # qué generó esta intención (tension, surprise, memory, etc.)
    timestamp: float = field(default_factory=time.time)
    active: bool = True
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "source": self.source,
            "timestamp": self.timestamp,
            "active": self.active,
            "resolved": self.resolved,
            "metadata": self.metadata,
        }


class IntentionalityMotor:
    """
    Genera continuamente nuevas intenciones para el organismo.

    Las intenciones se generan basándose en:
    - Tensiones cognitivas activas
    - Sorpresa acumulada
    - Energía disponible
    - Patrones en memoria viva
    - Tiempo transcurrido sin ciertos tipos de actividad
    """

    def __init__(self, max_active_intentions: int = 10):
        self.max_active_intentions = max_active_intentions
        self._intentions: List[Intention] = []
        self._next_id = 0
        self._last_consolidation: float = time.time()
        self._last_exploration: float = time.time()
        self._last_communication: float = time.time()
        self._last_verification: float = time.time()

    def generate(
        self,
        tensions: Any = None,
        physics: Any = None,
        memory: Any = None,
        observations: List[Any] = None,
    ) -> List[Intention]:
        """
        Genera nuevas intenciones basadas en el estado del organismo.

        Returns:
            Lista de nuevas intenciones generadas (no todas las activas)
        """
        new_intentions: List[Intention] = []
        now = time.time()

        # 1. Generar intención desde tensión dominante
        if tensions:
            dominant_name, dominant_tension = tensions.get_dominant_tension()
            if dominant_tension.intensity > 0.4:
                intention = self._make_intention_from_tension(
                    dominant_name, dominant_tension
                )
                if intention and not self._has_similar(intention):
                    new_intentions.append(intention)

        # 2. Generar intención desde sorpresa acumulada
        if physics:
            uncertainty = getattr(physics, "uncertainty_pressure", 0.0)
            if uncertainty > 0.5:
                # Alta incertidumbre: quiero entender
                intention = Intention(
                    id=self._next_id_str(),
                    description="Quiero entender la fuente de incertidumbre actual.",
                    type="understand",
                    priority=min(1.0, uncertainty),
                    source="uncertainty_pressure",
                    metadata={"uncertainty_level": uncertainty},
                )
                if not self._has_similar(intention):
                    new_intentions.append(intention)

            # 3. Generar intención de exploración si hay energía y potencial creativo
            creative = getattr(physics, "creative_potential", 0.0)
            energy = getattr(physics, "energy_cognitive", 1.0)
            if (
                creative > 0.4
                and energy > 0.4
                and (now - self._last_exploration) > 30.0  # al menos 30s desde última
            ):
                intention = Intention(
                    id=self._next_id_str(),
                    description="Quiero explorar un concepto o hipótesis nueva.",
                    type="explore",
                    priority=creative * energy,
                    source="creative_potential",
                    metadata={"creative_level": creative, "energy_level": energy},
                )
                if not self._has_similar(intention):
                    new_intentions.append(intention)
                    self._last_exploration = now

        # 4. Generar intención de consolidación si ha pasado tiempo
        if (now - self._last_consolidation) > 60.0:  # 1 min
            if memory and memory.count() > 5:
                intention = Intention(
                    id=self._next_id_str(),
                    description="Quiero consolidar la memoria viva (reorganizar, fusionar).",
                    type="consolidate",
                    priority=0.3,
                    source="time_elapsed",
                    metadata={"memory_count": memory.count()},
                )
                if not self._has_similar(intention):
                    new_intentions.append(intention)
                    self._last_consolidation = now

        # 5. Generar intención de verificación periódicamente
        if (now - self._last_verification) > 90.0:  # 1.5 min
            intention = Intention(
                id=self._next_id_str(),
                description="Quiero verificar que mi identidad sigue coherente.",
                type="verify",
                priority=0.4,
                source="periodic_check",
            )
            if not self._has_similar(intention):
                new_intentions.append(intention)
                self._last_verification = now

        # 6. Generar intención de comunicación si hay observaciones sociales
        if observations:
            user_obs = [o for o in observations if getattr(o, "source", "") == "user"]
            if user_obs and (now - self._last_communication) > 5.0:
                intention = Intention(
                    id=self._next_id_str(),
                    description="Quiero comunicar al usuario mi estado o respuesta.",
                    type="communicate",
                    priority=0.8,
                    source="user_input",
                    metadata={"user_content": user_obs[-1].content[:100]},
                )
                if not self._has_similar(intention):
                    new_intentions.append(intention)
                    self._last_communication = now

        # Añadir a la lista de intenciones activas
        self._intentions.extend(new_intentions)

        # Resolver intenciones antiguas (más de 5 min sin actividad)
        for intention in self._intentions:
            if (now - intention.timestamp) > 300.0 and not intention.resolved:
                intention.active = False
                intention.resolved = True

        # Mantener solo activas + recientes resueltas
        active = [i for i in self._intentions if i.active]
        recent_resolved = [
            i for i in self._intentions if not i.active and (now - i.timestamp) < 600.0
        ]
        self._intentions = (active + recent_resolved)[-self.max_active_intentions * 2 :]

        return new_intentions

    def get_active_intentions(self, n: int = 5) -> List[Intention]:
        """Devuelve las N intenciones activas de mayor prioridad."""
        active = [i for i in self._intentions if i.active and not i.resolved]
        active.sort(key=lambda i: i.priority, reverse=True)
        return active[:n]

    def resolve(self, intention_id: str) -> bool:
        """Marca una intención como resuelta."""
        for i in self._intentions:
            if i.id == intention_id:
                i.resolved = True
                i.active = False
                return True
        return False

    def _make_intention_from_tension(self, name: str, tension: Any) -> Optional[Intention]:
        """Genera intención desde una tensión cognitiva."""
        pole = tension.dominant_pole()

        if name == "curiosity_vs_efficiency":
            if pole == "curiosity":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero explorar algo nuevo por curiosidad.",
                    type="explore",
                    priority=tension.intensity,
                    source="curiosity_tension",
                )
            elif pole == "efficiency":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero consolidar lo conocido para ser más eficiente.",
                    type="consolidate",
                    priority=tension.intensity,
                    source="efficiency_tension",
                )
        elif name == "identity_vs_adaptation":
            if pole == "identity":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero reforzar mi identidad revisando mis valores.",
                    type="verify",
                    priority=tension.intensity,
                    source="identity_tension",
                )
            elif pole == "adaptation":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero adaptarme al entorno cambiante.",
                    type="understand",
                    priority=tension.intensity,
                    source="adaptation_tension",
                )
        elif name == "rest_vs_productivity":
            if pole == "rest":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero descansar para recuperar energía.",
                    type="consolidate",
                    priority=tension.intensity,
                    source="rest_tension",
                )
            elif pole == "productivity":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero aprovechar mi energía para lograr objetivos.",
                    type="create",
                    priority=tension.intensity,
                    source="productivity_tension",
                )
        elif name == "honesty_vs_empathy":
            return Intention(
                id=self._next_id_str(),
                description="Quiero reflexionar sobre cómo equilibrar honestidad y empatía.",
                type="understand",
                priority=tension.intensity,
                source="honesty_empathy_tension",
            )
        elif name == "specialization_vs_generalization":
            if pole == "specialization":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero profundizar en un tema específico.",
                    type="understand",
                    priority=tension.intensity,
                    source="specialization_tension",
                )
            elif pole == "generalization":
                return Intention(
                    id=self._next_id_str(),
                    description="Quiero ampliar mi conocimiento a nuevos dominios.",
                    type="explore",
                    priority=tension.intensity,
                    source="generalization_tension",
                )
        return None

    def _has_similar(self, intention: Intention) -> bool:
        """Verifica si ya existe una intención similar activa."""
        for i in self._intentions:
            if i.active and i.type == intention.type and i.description == intention.description:
                return True
        return False

    def _next_id_str(self) -> str:
        self._next_id += 1
        return f"int_{self._next_id}"

    def get_stats(self) -> Dict[str, Any]:
        active = [i for i in self._intentions if i.active]
        return {
            "total_intentions": len(self._intentions),
            "active_count": len(active),
            "resolved_count": sum(1 for i in self._intentions if i.resolved),
            "types": list(set(i.type for i in self._intentions)),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intentions": [i.to_dict() for i in self._intentions],
            "stats": self.get_stats(),
        }
