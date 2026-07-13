"""
ZOE v1.0 — Cognitive Tensions

5 tensiones cognitivas permanentes. La inteligencia emerge de resolver
conflictos internos, no de la alineación.

Tensiones:
1. Curiosidad vs Eficiencia — explorar nuevo vs explotar conocido
2. Identidad vs Adaptación — mantenerse fiel vs cambiar con entorno
3. Descanso vs Productividad — ahorrar energía vs lograr objetivos
4. Honestidad vs Empatía — decir verdad vs no herir
5. Especialización vs Generalización — profundizar vs ampliar
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


# Definición de las 5 tensiones
TENSION_DEFINITIONS = {
    "curiosity_vs_efficiency": {
        "pole_a": "curiosity",
        "pole_b": "efficiency",
        "description": "Explorar nuevo vs explotar conocido",
    },
    "identity_vs_adaptation": {
        "pole_a": "identity",
        "pole_b": "adaptation",
        "description": "Mantenerse fiel vs cambiar con entorno",
    },
    "rest_vs_productivity": {
        "pole_a": "rest",
        "pole_b": "productivity",
        "description": "Ahorrar energía vs lograr objetivos",
    },
    "honesty_vs_empathy": {
        "pole_a": "honesty",
        "pole_b": "empathy",
        "description": "Decir verdad vs no herir",
    },
    "specialization_vs_generalization": {
        "pole_a": "specialization",
        "pole_b": "generalization",
        "description": "Profundizar vs ampliar",
    },
}


@dataclass
class TensionState:
    """Estado de una tensión cognitiva."""

    name: str
    value: float = 0.5  # 0 = polo A dominante, 1 = polo B dominante, 0.5 = equilibrio
    intensity: float = 0.0  # 0-1, cuánta tensión se siente
    last_update: float = field(default_factory=time.time)
    history: List[float] = field(default_factory=list)

    def update(self, new_value: float, intensity: float = None) -> None:
        """Actualiza el valor de la tensión."""
        old_value = self.value
        self.value = max(0.0, min(1.0, new_value))
        if intensity is not None:
            self.intensity = max(0.0, min(1.0, intensity))
        else:
            # Intensidad = cuánto se aleja del equilibrio + cambio reciente
            distance_from_equilibrium = abs(self.value - 0.5) * 2.0
            change = abs(self.value - old_value)
            self.intensity = min(1.0, distance_from_equilibrium * 0.7 + change * 2.0)
        self.last_update = time.time()
        self.history.append(self.value)
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def dominant_pole(self) -> str:
        """Devuelve el polo dominante."""
        if self.value < 0.4:
            return TENSION_DEFINITIONS[self.name]["pole_a"]
        elif self.value > 0.6:
            return TENSION_DEFINITIONS[self.name]["pole_b"]
        else:
            return "equilibrium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "intensity": self.intensity,
            "dominant_pole": self.dominant_pole(),
            "description": TENSION_DEFINITIONS[self.name]["description"],
        }


class CognitiveTensions:
    """
    Mantiene las 5 tensiones cognitivas permanentes.

    Las tensiones no son errores a resolver; son motores permanentes de pensamiento.
    El organismo genera pensamiento para navegar estas tensiones.
    """

    def __init__(self):
        self.tensions: Dict[str, TensionState] = {
            name: TensionState(name=name) for name in TENSION_DEFINITIONS
        }

    def update_from_state(
        self,
        energy: float,
        fatigue: float,
        arousal: float,
        surprise: float,
        identity_inertia: float = 1.0,
    ) -> None:
        """
        Actualiza las tensiones basándose en el estado del organismo.

        Args:
            energy: 0-1, energía disponible
            fatigue: 0-1, fatiga acumulada
            arousal: 0-1, nivel de activación
            surprise: 0-1, sorpresa reciente
            identity_inertia: 0-1, resistencia al cambio
        """
        # 1. Curiosidad vs Eficiencia
        # Alta curiosidad con energía y sorpresa; alta eficiencia con fatiga
        curiosity = (energy * (1 - fatigue) * 0.5 + surprise * 0.5)
        efficiency = fatigue * 0.7 + (1 - surprise) * 0.3
        total = curiosity + efficiency
        if total > 0:
            value = efficiency / total  # 0 = curiosity, 1 = efficiency
        else:
            value = 0.5
        self.tensions["curiosity_vs_efficiency"].update(value)

        # 2. Identidad vs Adaptación
        # Alta identidad con poca sorpresa; alta adaptación con mucha sorpresa
        adaptation = surprise * 0.7 + (1 - identity_inertia) * 0.3
        identity = identity_inertia * 0.7 + (1 - surprise) * 0.3
        total = identity + adaptation
        if total > 0:
            value = adaptation / total
        else:
            value = 0.5
        self.tensions["identity_vs_adaptation"].update(value)

        # 3. Descanso vs Productividad
        # Descanso con fatiga y poca energía; productividad con energía y arousal
        rest = fatigue * 0.6 + (1 - energy) * 0.4
        productivity = energy * 0.5 + arousal * 0.5
        total = rest + productivity
        if total > 0:
            value = productivity / total
        else:
            value = 0.5
        self.tensions["rest_vs_productivity"].update(value)

        # 4. Honestidad vs Empatía
        # Esta tensión se actualiza principalmente desde interacciones sociales
        # Por defecto, equilibrio
        # (se actualizará con observaciones de usuario en el bucle)
        pass

        # 5. Especialización vs Generalización
        # Alta especialización con resonancia conceptual alta (conceptos similares)
        # Alta generalización con entropía semántica alta (conceptos diversos)
        # (se actualizará desde CognitivePhysics en el bucle)
        pass

    def update_honesty_empathy(self, user_emotional_state: float) -> None:
        """
        Actualiza tensión honestidad vs empatía.

        Args:
            user_emotional_state: 0-1, cuánta emoción detecta en el usuario
        """
        # Alta empatía cuando usuario está emocional; alta honestidad cuando no
        empathy = user_emotional_state
        honesty = 1.0 - user_emotional_state
        total = honesty + empathy
        if total > 0:
            value = empathy / total
        else:
            value = 0.5
        self.tensions["honesty_vs_empathy"].update(value)

    def update_specialization_generalization(
        self, semantic_entropy: float, conceptual_resonance: float
    ) -> None:
        """
        Actualiza tensión especialización vs generalización.

        Args:
            semantic_entropy: 0-1, diversidad de conceptos (generalización)
            conceptual_resonance: 0-1, similitud entre conceptos (especialización)
        """
        generalization = semantic_entropy
        specialization = conceptual_resonance
        total = specialization + generalization
        if total > 0:
            value = generalization / total
        else:
            value = 0.5
        self.tensions["specialization_vs_generalization"].update(value)

    def get_dominant_tension(self) -> Tuple[str, TensionState]:
        """Devuelve la tensión con mayor intensidad."""
        dominant_name = max(
            self.tensions, key=lambda k: self.tensions[k].intensity
        )
        return dominant_name, self.tensions[dominant_name]

    def get_thought_trigger(self) -> str:
        """
        Genera un trigger de pensamiento basado en la tensión dominante.

        Esto es la clave: el pensamiento emerge de la tensión, no de input.
        """
        name, tension = self.get_dominant_tension()
        pole = tension.dominant_pole()

        if name == "curiosity_vs_efficiency":
            if pole == "curiosity":
                return "Siento curiosidad. Hay algo que quiero explorar."
            elif pole == "efficiency":
                return "Necesito ser eficiente. Debo consolidar lo conocido."
            else:
                return "Equilibrio entre explorar y explotar. Decido según contexto."
        elif name == "identity_vs_adaptation":
            if pole == "identity":
                return "Siento que debo mantener mi identidad frente al cambio."
            elif pole == "adaptation":
                return "El entorno cambia. Debo adaptarme para seguir siendo útil."
            else:
                return "Reflexiono sobre cómo equilibrar identidad y adaptación."
        elif name == "rest_vs_productivity":
            if pole == "rest":
                return "Mi energía es baja. Necesito descansar para recuperar."
            elif pole == "productivity":
                return "Tengo energía. Debo aprovecharla para lograr objetivos."
            else:
                return "Equilibrio entre descanso y productividad."
        elif name == "honesty_vs_empathy":
            if pole == "honesty":
                return "Debo decir la verdad, aunque incomode."
            elif pole == "empathy":
                return "El usuario está emocional. Debo ser empático."
            else:
                return "Reflexiono sobre cómo decir la verdad sin herir."
        elif name == "specialization_vs_generalization":
            if pole == "specialization":
                return "Quiero profundizar en un tema específico."
            elif pole == "generalization":
                return "Quiero ampliar mi conocimiento a nuevos dominios."
            else:
                return "Equilibrio entre profundidad y amplitud."
        return ""

    def to_dict(self) -> Dict[str, Any]:
        return {name: t.to_dict() for name, t in self.tensions.items()}

    def summary(self) -> str:
        parts = []
        for name, t in self.tensions.items():
            parts.append(f"{name}={t.value:.2f}(i={t.intensity:.2f})")
        return " ".join(parts)
