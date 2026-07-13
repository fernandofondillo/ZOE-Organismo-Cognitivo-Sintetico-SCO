"""
ZOE v1.0 — Cognitive Laws

Las 6 leyes cognitivas que rigen todo el organismo.
ZOE no se define por componentes, se define por leyes.
Cada acción, mutación o decisión debe respetar las 6 leyes.

Las leyes son principios verificables, no sugerencias.
Cualquier acción que viole una ley se rechaza.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LawID(str, Enum):
    """IDs de las 6 leyes cognitivas de ZOE."""

    UTILITY = "utility"  # 1ra: toda acción reduce incertidumbre o aumenta capacidad
    IDENTITY = "identity"  # 2da: toda modificación preserva identidad
    PROVENANCE = "provenance"  # 3ra: todo conocimiento justifica su origen
    COST = "cost"  # 4ta: todo proceso consume recursos
    CONFIDENCE = "confidence"  # 5ta: toda creencia tiene nivel de confianza
    MODULARITY = "modularity"  # 6ta: todo módulo puede reemplazarse


@dataclass
class LawViolation:
    """Registro de violación de una ley."""

    law: LawID
    reason: str
    action: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class CognitiveLaws:
    """
    Verificador de las 6 leyes cognitivas.

    Cada acción propuesta por el bucle cognitivo pasa por verify_action()
    antes de ejecutarse. Si viola alguna ley, se rechaza con justificación.
    """

    # Histórico de violaciones (para análisis y aprendizaje)
    violations: List[LawViolation] = field(default_factory=list)
    max_violations_history: int = 100

    # Verificaciones activas (para desactivar leyes en tests si necesario)
    active_laws: Dict[LawID, bool] = field(
        default_factory=lambda: {law: True for law in LawID}
    )

    def verify_action(self, action: Dict[str, Any]) -> Tuple[bool, List[LawViolation]]:
        """
        Verifica una acción contra todas las leyes activas.

        Args:
            action: dict con keys:
                - 'type': 'think' | 'mutate' | 'communicate' | 'explore' | 'rest'
                - 'uncertainty_reduction': float (0-1) opcional
                - 'capacity_increase': float (0-1) opcional
                - 'cost': float (0-1) opcional
                - 'preserves_identity': bool opcional
                - 'provenance': str opcional
                - 'confidence': float (0-1) opcional

        Returns:
            (all_passed, list_of_violations)
        """
        violations: List[LawViolation] = []

        if self.active_laws[LawID.UTILITY]:
            v = self._verify_utility(action)
            if v:
                violations.append(v)

        if self.active_laws[LawID.IDENTITY]:
            v = self._verify_identity(action)
            if v:
                violations.append(v)

        if self.active_laws[LawID.PROVENANCE]:
            v = self._verify_provenance(action)
            if v:
                violations.append(v)

        if self.active_laws[LawID.COST]:
            v = self._verify_cost(action)
            if v:
                violations.append(v)

        if self.active_laws[LawID.CONFIDENCE]:
            v = self._verify_confidence(action)
            if v:
                violations.append(v)

        # 6ta ley (modularidad) se verifica al reemplazar módulos, no en cada acción
        # Se verifica explícitamente via verify_modularity_replacement()

        # Registrar violaciones
        for v in violations:
            self.violations.append(v)
        if len(self.violations) > self.max_violations_history:
            self.violations = self.violations[-self.max_violations_history :]

        return (len(violations) == 0, violations)

    def verify_modularity_replacement(
        self, module_to_replace: str, new_module: Dict[str, Any]
    ) -> Tuple[bool, Optional[LawViolation]]:
        """
        Verifica que reemplazar un módulo no rompe identidad (6ta ley).

        Args:
            module_to_replace: nombre del módulo a reemplazar
            new_module: dict con spec del nuevo módulo

        Returns:
            (can_replace, violation_if_any)
        """
        if not self.active_laws[LawID.MODULARITY]:
            return True, None

        # Todo módulo debe poder reemplazarse si preserva la interfaz
        required_interface = new_module.get("interface", {})
        if not required_interface:
            # Sin interfaz definida, no se puede verificar
            violation = LawViolation(
                law=LawID.MODULARITY,
                reason=f"Reemplazo de {module_to_replace} sin interfaz definida",
                action={"module": module_to_replace, "new_module": new_module},
            )
            self.violations.append(violation)
            return False, violation

        # Verificar que la interfaz cumple los métodos requeridos
        required_methods = required_interface.get("methods", [])
        for method in required_methods:
            if not new_module.get("implements", {}).get(method):
                violation = LawViolation(
                    law=LawID.MODULARITY,
                    reason=f"Nuevo módulo no implementa método requerido: {method}",
                    action={"module": module_to_replace, "missing_method": method},
                )
                self.violations.append(violation)
                return False, violation

        return True, None

    def _verify_utility(self, action: Dict[str, Any]) -> Optional[LawViolation]:
        """1ra Ley: toda acción debe reducir incertidumbre o aumentar capacidad."""
        action_type = action.get("type", "")

        # Acciones gratuitas permitidas: descansar (es homeostasis)
        if action_type == "rest":
            return None

        # Para pensar, mutar, comunicar, explorar: debe tener utilidad
        uncertainty_reduction = action.get("uncertainty_reduction", 0.0)
        capacity_increase = action.get("capacity_increase", 0.0)
        utility = uncertainty_reduction + capacity_increase

        if utility < 0.01:
            return LawViolation(
                law=LawID.UTILITY,
                reason=f"Acción '{action_type}' sin utilidad (uncertainty_reduction={uncertainty_reduction}, capacity_increase={capacity_increase})",
                action=action,
            )

        return None

    def _verify_identity(self, action: Dict[str, Any]) -> Optional[LawViolation]:
        """2da Ley: toda modificación debe preservar identidad."""
        action_type = action.get("type", "")

        # Solo mutaciones pueden romper identidad
        if action_type != "mutate":
            return None

        preserves_identity = action.get("preserves_identity", None)
        if preserves_identity is False:
            return LawViolation(
                law=LawID.IDENTITY,
                reason="Mutación marcada explícitamente como que rompe identidad",
                action=action,
            )

        # Si no se especifica, se asume True (verificación externa en Fase 1 con Identity Vault)
        return None

    def _verify_provenance(self, action: Dict[str, Any]) -> Optional[LawViolation]:
        """3ra Ley: todo conocimiento debe justificar su origen."""
        action_type = action.get("type", "")

        # Solo mutaciones que añaden conocimiento requieren provenance
        if action_type != "mutate":
            return None

        mutation_subtype = action.get("subtype", "")
        if mutation_subtype in ["add_memory", "strengthen_belief", "add_skill"]:
            provenance = action.get("provenance", "")
            if not provenance:
                return LawViolation(
                    law=LawID.PROVENANCE,
                    reason=f"Mutación '{mutation_subtype}' sin provenance",
                    action=action,
                )

        return None

    def _verify_cost(self, action: Dict[str, Any]) -> Optional[LawViolation]:
        """4ta Ley: todo proceso consume recursos."""
        action_type = action.get("type", "")

        # Descansar es la única acción sin coste (de hecho, recarga)
        if action_type == "rest":
            return None

        cost = action.get("cost", None)
        if cost is None:
            # Si no se especifica coste, se asigna uno por defecto
            # No es violación, solo warning
            return None

        if cost <= 0:
            return LawViolation(
                law=LawID.COST,
                reason=f"Acción '{action_type}' con coste 0 o negativo",
                action=action,
            )

        return None

    def _verify_confidence(self, action: Dict[str, Any]) -> Optional[LawViolation]:
        """5ta Ley: toda creencia tiene nivel de confianza."""
        action_type = action.get("type", "")

        # Solo mutaciones que añaden creencias requieren confidence
        if action_type != "mutate":
            return None

        mutation_subtype = action.get("subtype", "")
        if mutation_subtype in ["add_memory", "strengthen_belief"]:
            confidence = action.get("confidence", None)
            if confidence is None:
                return LawViolation(
                    law=LawID.CONFIDENCE,
                    reason=f"Mutación '{mutation_subtype}' sin confidence",
                    action=action,
                )
            if not (0.0 <= confidence <= 1.0):
                return LawViolation(
                    law=LawID.CONFIDENCE,
                    reason=f"Confidence fuera de rango [0,1]: {confidence}",
                    action=action,
                )

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de verificación de leyes."""
        violation_counts = {law.value: 0 for law in LawID}
        for v in self.violations:
            violation_counts[v.law.value] = violation_counts.get(v.law.value, 0) + 1
        return {
            "total_violations": len(self.violations),
            "violation_counts": violation_counts,
            "active_laws": {law.value: active for law, active in self.active_laws.items()},
        }

    def deactivate_law(self, law: LawID) -> None:
        """Desactiva una ley (para tests o casos especiales)."""
        self.active_laws[law] = False
        logger.warning(f"Ley cognitiva desactivada: {law.value}")

    def activate_law(self, law: LawID) -> None:
        """Reactiva una ley."""
        self.active_laws[law] = True
        logger.info(f"Ley cognitiva reactivada: {law.value}")
