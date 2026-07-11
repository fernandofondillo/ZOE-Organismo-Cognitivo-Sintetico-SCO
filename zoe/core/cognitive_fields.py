"""
ZOE v1.0 — Cognitive Fields

Campos cognitivos compartidos. Los sub-agentes no se mandan mensajes
directamente; modifican campos compartidos. Esto elimina acoplamiento.

6 campos:
1. Atención — a qué se está prestando atención
2. Emocional — estado emocional funcional (sorpresa, curiosidad, fatiga)
3. Social — modelos de otros agentes y usuarios
4. Creativo — hipótesis, combinaciones, exploraciones
5. Causal — relaciones causa-efecto detectadas
6. Ético — evaluación de valores en curso
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class FieldContribution:
    """Contribución de un sub-agente a un campo."""

    contributor: str  # nombre del sub-agente
    timestamp: float
    value: Any  # valor aportado
    weight: float = 1.0  # peso de la contribución


class CognitiveField:
    """
    Campo cognitivo compartido.

    Los sub-agentes escriben contribuciones; otros sub-agentes leen el estado
    agregado del campo. No hay mensajes directos entre agentes.
    """

    def __init__(self, name: str, description: str = "", max_history: int = 50):
        self.name = name
        self.description = description
        self.max_history = max_history
        self._contributions: List[FieldContribution] = []
        self._state: Dict[str, Any] = {}
        self._tension: float = 0.0  # nivel de tensión en este campo

    def contribute(
        self,
        contributor: str,
        value: Any,
        weight: float = 1.0,
        replace: bool = False,
    ) -> None:
        """Un sub-agente contribuye al campo."""
        contribution = FieldContribution(
            contributor=contributor,
            timestamp=time.time(),
            value=value,
            weight=weight,
        )
        self._contributions.append(contribution)
        if len(self._contributions) > self.max_history:
            self._contributions = self._contributions[-self.max_history :]

        # Actualizar estado agregado
        if replace:
            self._state = value if isinstance(value, dict) else {"value": value}
        else:
            self._merge_value(value, weight)

        # Recalcular tensión (cuántas contribuciones recientes divergentes)
        self._update_tension()

    def _merge_value(self, value: Any, weight: float) -> None:
        """Merge el valor contribuido al estado del campo."""
        if isinstance(value, dict):
            for k, v in value.items():
                if k in self._state:
                    # Si ya existe, promediar (para numéricos) o concatenar
                    if isinstance(v, (int, float)) and isinstance(self._state[k], (int, float)):
                        old_weight = self._state.get(f"_weight_{k}", 1.0)
                        new_weight = old_weight + weight
                        self._state[k] = (self._state[k] * old_weight + v * weight) / new_weight
                        self._state[f"_weight_{k}"] = new_weight
                    elif isinstance(v, list):
                        if isinstance(self._state[k], list):
                            self._state[k] = (self._state[k] + v)[-20:]  # acotar
                        else:
                            self._state[k] = v
                    else:
                        # Para strings y otros, reemplazar
                        self._state[k] = v
                else:
                    self._state[k] = v
                    self._state[f"_weight_{k}"] = weight
        else:
            # Valor escalar
            if "value" in self._state and isinstance(self._state["value"], (int, float)):
                old_weight = self._state.get("_weight_value", 1.0)
                new_weight = old_weight + weight
                self._state["value"] = (self._state["value"] * old_weight + value * weight) / new_weight
                self._state["_weight_value"] = new_weight
            else:
                self._state["value"] = value
                self._state["_weight_value"] = weight

    def _update_tension(self) -> None:
        """Calcula tensión: cuántas contribuciones recientes son divergentes."""
        if len(self._contributions) < 2:
            self._tension = 0.0
            return

        # Tensión = variabilidad de valores recientes
        recent = self._contributions[-5:]
        unique_contributors = set(c.contributor for c in recent)
        # Más contribuidores distintos = más tensión
        self._tension = min(1.0, len(unique_contributors) / 4.0)

    def read(self) -> Dict[str, Any]:
        """Lee el estado agregado del campo."""
        return dict(self._state)

    def read_tension(self) -> float:
        """Lee el nivel de tensión del campo."""
        return self._tension

    def read_contributions(self, n: int = 10) -> List[Dict[str, Any]]:
        """Lee últimas N contribuciones."""
        return [
            {
                "contributor": c.contributor,
                "timestamp": c.timestamp,
                "value": c.value,
                "weight": c.weight,
            }
            for c in self._contributions[-n:]
        ]

    def clear(self) -> None:
        """Limpia el campo (sin afectar contribuciones históricas)."""
        self._state = {}
        self._tension = 0.0


class CognitiveFields:
    """
    Conjunto de los 6 campos cognitivos de ZOE.
    """

    def __init__(self):
        self.fields: Dict[str, CognitiveField] = {
            "attention": CognitiveField(
                "attention", "A qué se está prestando atención ahora"
            ),
            "emotional": CognitiveField(
                "emotional", "Estado emocional funcional (sorpresa, curiosidad, fatiga)"
            ),
            "social": CognitiveField(
                "social", "Modelos de otros agentes y usuarios"
            ),
            "creative": CognitiveField(
                "creative", "Hipótesis, combinaciones, exploraciones"
            ),
            "causal": CognitiveField(
                "causal", "Relaciones causa-efecto detectadas"
            ),
            "ethical": CognitiveField(
                "ethical", "Evaluación de valores en curso"
            ),
        }

    def contribute(self, field_name: str, contributor: str, value: Any, weight: float = 1.0, replace: bool = False) -> None:
        """Contribuye a un campo específico."""
        if field_name not in self.fields:
            logger.warning(f"Campo cognitivo desconocido: {field_name}")
            return
        self.fields[field_name].contribute(contributor, value, weight, replace)

    def read(self, field_name: str) -> Dict[str, Any]:
        """Lee el estado de un campo."""
        if field_name not in self.fields:
            return {}
        return self.fields[field_name].read()

    def read_all(self) -> Dict[str, Dict[str, Any]]:
        """Lee el estado de todos los campos."""
        return {name: field.read() for name, field in self.fields.items()}

    def read_tensions(self) -> Dict[str, float]:
        """Lee las tensiones de todos los campos."""
        return {name: field.read_tension() for name, field in self.fields.items()}

    def get_field(self, field_name: str) -> Optional[CognitiveField]:
        """Obtiene un campo específico."""
        return self.fields.get(field_name)

    def total_tension(self) -> float:
        """Tensión total del sistema (suma de tensiones de todos los campos)."""
        return sum(field.read_tension() for field in self.fields.values())

    def summary(self) -> str:
        """Resumen legible."""
        parts = []
        for name, field in self.fields.items():
            tension = field.read_tension()
            parts.append(f"{name}(t={tension:.2f})")
        return " ".join(parts)
