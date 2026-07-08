"""
ZOE v1.0 — Ontogenetic Motor

Motor que propone, aplica y revierte mutaciones al organismo.
Conecta Identity Vault (2da ley) + Trajectory Chain (3ra ley) + CognitiveLaws.

Flujo:
1. propose_mutation(type, target, payload, justification)
2. apply_mutation(mutation) → verifica leyes → verifica identidad → firma en cadena
3. rollback(mutation_id) → revierte mutación

El motor es la implementación operativa del Motor Ontogenético descrito
en el doc 14. En Fase 1 hace 7 tipos de mutaciones. En Fase 3-4 evoluciona
a modificar arquitectura (crear/eliminar sub-agentes, reorganizar memorias, etc.).
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from .identity_vault import IdentityVault
from .trajectory_chain import TrajectoryChain, Mutation

logger = logging.getLogger(__name__)


# Tipos de mutación válidos
VALID_MUTATION_TYPES = [
    "add_memory",
    "strengthen_belief",
    "weaken_belief",
    "add_skill_subgraph",
    "update_world_model",
    "adjust_threshold",
    "federate_learning",
    "rollback_previous",
    # Fase 5: ACD
    "respond_to_user",
    # Fase 6A: cápsulas
    "capsule_loaded",
    "capsule_unloaded",
]


class OntogeneticMotor:
    """
    Motor que propone, aplica y revierte mutaciones al organismo.

    Integra:
    - Identity Vault: verifica que mutaciones preserven identidad (2da ley)
    - Trajectory Chain: firma mutaciones en cadena criptográfica (3ra ley)
    - CognitiveLaws: verifica todas las leyes antes de aplicar
    """

    def __init__(
        self,
        identity_vault: IdentityVault,
        trajectory_chain: Optional[TrajectoryChain] = None,
        laws: Optional[Any] = None,  # CognitiveLaws
        organism_id: str = "zoe_default",
    ):
        self.identity_vault = identity_vault
        self.trajectory_chain = trajectory_chain or TrajectoryChain(organism_id)
        self.laws = laws
        self.organism_id = organism_id
        self._next_mutation_id = 0

    def propose_mutation(
        self,
        type: str,
        target: str,
        payload: Dict[str, Any],
        justification: str,
        provenance: str = "",
        cost: float = 0.1,
        confidence: float = 0.5,
    ) -> Mutation:
        """
        Propone una mutación (sin aplicarla).

        Args:
            type: tipo de mutación (add_memory, strengthen_belief, etc.)
            target: qué componente afecta
            payload: datos específicos de la mutación
            justification: por qué se hace
            provenance: origen (3ra ley)
            cost: coste (4ta ley)
            confidence: confianza (5ta ley)

        Returns:
            Mutation propuesta (no aplicada)
        """
        if type not in VALID_MUTATION_TYPES:
            raise ValueError(f"Invalid mutation type: {type}. Valid: {VALID_MUTATION_TYPES}")

        if not provenance:
            provenance = f"ontogenetic_motor:{type}"

        self._next_mutation_id += 1
        mutation = Mutation(
            id=f"mut_{self.organism_id}_{self._next_mutation_id}",
            type=type,
            target=target,
            payload=payload,
            justification=justification,
            provenance=provenance,
            cost=cost,
            confidence=confidence,
        )

        return mutation

    def apply_mutation(self, mutation: Mutation) -> Tuple[bool, str]:
        """
        Aplica una mutación: verifica leyes + identidad + firma en cadena.

        Args:
            mutation: mutación a aplicar

        Returns:
            (success, reason)
        """
        # 1. Verificar leyes cognitivas (si hay)
        if self.laws:
            law_action = self._mutation_to_law_action(mutation)
            laws_passed, violations = self.laws.verify_action(law_action)
            if not laws_passed:
                violation_reasons = [v.reason for v in violations]
                reason = f"laws violated: {violation_reasons}"
                logger.warning(f"Mutation {mutation.id} rejected: {reason}")
                return False, reason

        # 2. Verificar identidad (2da ley, explícita via Vault)
        preserves_identity, id_reason = self.identity_vault.verify(
            {
                "type": "mutate",
                "subtype": mutation.type,
                "target": mutation.target,
                "preserves_identity": True,
            }
        )
        if not preserves_identity:
            reason = f"identity not preserved: {id_reason}"
            logger.warning(f"Mutation {mutation.id} rejected: {reason}")
            return False, reason

        # 3. Commit a Trajectory Chain (firma)
        try:
            commit_hash = self.trajectory_chain.commit(mutation)
            logger.info(
                f"Mutation {mutation.id} applied. Hash: {commit_hash[:16]}..."
            )
            return True, f"applied: {commit_hash[:16]}"
        except Exception as e:
            reason = f"trajectory chain commit failed: {e}"
            logger.error(f"Mutation {mutation.id} failed: {reason}")
            return False, reason

    def rollback(self, mutation_id: str) -> Tuple[bool, str]:
        """
        Revierte una mutación.

        Args:
            mutation_id: ID de la mutación a revertir

        Returns:
            (success, reason)
        """
        success, reason = self.trajectory_chain.rollback(mutation_id)
        if success:
            logger.info(f"Mutation {mutation_id} rolled back: {reason}")
        else:
            logger.warning(f"Cannot rollback {mutation_id}: {reason}")
        return success, reason

    def _mutation_to_law_action(self, mutation: Mutation) -> Dict[str, Any]:
        """Convierte mutación a dict de acción para verificar leyes."""
        return {
            "type": "mutate",
            "subtype": mutation.type,
            "target": mutation.target,
            "uncertainty_reduction": 0.2,  # default; las mutaciones reducen incertidumbre
            "capacity_increase": 0.2 if mutation.type == "add_skill_subgraph" else 0.1,
            "cost": mutation.cost,
            "preserves_identity": True,
            "provenance": mutation.provenance,
            "confidence": mutation.confidence,
        }

    def get_active_mutations(self) -> List[Mutation]:
        """Devuelve mutaciones activas (no revertidas)."""
        return self.trajectory_chain.get_active_mutations()

    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Historial de mutaciones."""
        return self.trajectory_chain.get_history(n)

    def verify_integrity(self) -> bool:
        """Verifica integridad de la cadena de mutaciones."""
        return self.trajectory_chain.verify_chain()

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del motor."""
        return {
            "identity_vault": self.identity_vault.summary(),
            "trajectory_chain": self.trajectory_chain.get_stats(),
            "total_mutations_proposed": self._next_mutation_id,
        }
