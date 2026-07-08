"""
ZOE v1.0 — Ontogenetic Motor V2 (Fase 3.5)

Motor Ontogenético avanzado que puede modificar ARQUITECTURA:
- Crear nuevos sub-agentes
- Eliminar sub-agentes obsoletos
- Fusionar sub-agentes redundantes
- Ajustar thresholds de meta-cognición
- Ajustar parámetros de Global Workspace
- Ajustar umbrales de Metabolism

Todas las mutaciones arquitecturales:
1. Se verifican contra las 6 leyes cognitivas
2. Se verifican contra el Identity Vault (2da ley)
3. Se firman en la Trajectory Chain
4. Son reversibles (rollback)

Extiende OntogeneticMotor de Fase 1 sin reemplazarlo.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from ..alma.identity_vault import IdentityVault
from ..alma.trajectory_chain import TrajectoryChain, Mutation
from ..alma.ontogenetic_motor import OntogeneticMotor, VALID_MUTATION_TYPES

logger = logging.getLogger(__name__)


# Nuevos tipos de mutación arquitectural
ARCHITECTURAL_MUTATION_TYPES = [
    "add_subagent",
    "remove_subagent",
    "merge_subagents",
    "modify_threshold",
    "adjust_workspace_capacity",
    "adjust_metabolism_threshold",
    "reorganize_memory",
]


class OntogeneticMotorV2(OntogeneticMotor):
    """
    Motor Ontogenético V2: puede modificar arquitectura del organismo.

    Extiende V1 con mutaciones que cambian la estructura cognitiva,
    no solo el contenido de la memoria.
    """

    def __init__(
        self,
        identity_vault: IdentityVault,
        trajectory_chain: Optional[TrajectoryChain] = None,
        laws: Optional[Any] = None,
        organism_id: str = "zoe_default",
    ):
        super().__init__(
            identity_vault=identity_vault,
            trajectory_chain=trajectory_chain,
            laws=laws,
            organism_id=organism_id,
        )
        self._architectural_changes: List[Dict[str, Any]] = []

        # Extender tipos válidos
        self._all_valid_types = VALID_MUTATION_TYPES + ARCHITECTURAL_MUTATION_TYPES

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
        """Propone una mutación (incluyendo arquitecturales)."""
        if type not in self._all_valid_types:
            raise ValueError(
                f"Invalid mutation type: {type}. Valid: {self._all_valid_types}"
            )

        if not provenance:
            provenance = f"ontogenetic_v2:{type}"

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

    def apply_architectural_mutation(
        self,
        mutation: Mutation,
        organism: Any = None,
    ) -> Tuple[bool, str]:
        """
        Aplica una mutación arquitectural al organismo.

        Args:
            mutation: mutación arquitectural a aplicar
            organism: referencia al organismo (loop) para modificar

        Returns:
            (success, reason)
        """
        # Verificar leyes
        if self.laws:
            law_action = self._mutation_to_law_action(mutation)
            law_action["capacity_increase"] = 0.3  # las arquitecturales aumentan capacidad
            laws_passed, violations = self.laws.verify_action(law_action)
            if not laws_passed:
                return False, f"laws violated: {[v.reason for v in violations]}"

        # Verificar identidad
        preserves_identity, id_reason = self.identity_vault.verify({
            "type": "mutate",
            "subtype": mutation.type,
            "target": mutation.target,
            "preserves_identity": True,
        })
        if not preserves_identity:
            return False, f"identity not preserved: {id_reason}"

        # Aplicar según tipo
        success = False
        reason = ""

        if mutation.type == "add_subagent":
            success, reason = self._add_subagent(mutation, organism)
        elif mutation.type == "remove_subagent":
            success, reason = self._remove_subagent(mutation, organism)
        elif mutation.type == "modify_threshold":
            success, reason = self._modify_threshold(mutation, organism)
        elif mutation.type == "adjust_workspace_capacity":
            success, reason = self._adjust_workspace(mutation, organism)
        elif mutation.type == "adjust_metabolism_threshold":
            success, reason = self._adjust_metabolism(mutation, organism)
        else:
            # Tipos no arquitecturales: delegar a V1
            return super().apply_mutation(mutation)

        if success:
            # Firmar en cadena
            commit_hash = self.trajectory_chain.commit(mutation)
            self._architectural_changes.append({
                "mutation_id": mutation.id,
                "type": mutation.type,
                "target": mutation.target,
                "timestamp": time.time(),
                "commit_hash": commit_hash[:16],
            })
            logger.info(f"Architectural mutation applied: {mutation.type} → {mutation.target}")
            return True, f"applied: {commit_hash[:16]}"
        else:
            return False, reason

    def _add_subagent(self, mutation: Mutation, organism: Any) -> Tuple[bool, str]:
        """Añade un sub-agente al organismo."""
        if not organism:
            return False, "no organism reference"

        # Solo permitir añadir sub-agentes de tipos conocidos
        subagent_type = mutation.payload.get("subagent_type", "")
        allowed_types = [
            "creativity", "causal_engine", "emotional_motor",
            "ethical_motor", "scientific_engine", "memorialist",
            "learner", "curator",
        ]

        if subagent_type not in allowed_types:
            return False, f"unknown subagent type: {subagent_type}"

        # Verificar si ya existe
        existing_names = [s.__class__.__name__.lower() for s in organism.subagents]
        if subagent_type.lower() in " ".join(existing_names):
            return False, f"subagent {subagent_type} already exists"

        # Crear sub-agente
        try:
            from ..core.subagents.phase2_subagents import (
                Creativity, CausalEngine, EmotionalMotor,
                EthicalMotor, ScientificEngine, Memorialist, Learner, Curator,
            )

            subagent_map = {
                "creativity": Creativity,
                "causal_engine": CausalEngine,
                "emotional_motor": EmotionalMotor,
                "ethical_motor": EthicalMotor,
                "scientific_engine": ScientificEngine,
                "memorialist": Memorialist,
                "learner": Learner,
                "curator": Curator,
            }

            cls = subagent_map.get(subagent_type)
            if not cls:
                return False, f"cannot create subagent type: {subagent_type}"

            # Crear instancia (algunos requieren memoria)
            if subagent_type in ("memorialist", "curator"):
                new_agent = cls(memory=getattr(organism, "memory", None))
            else:
                new_agent = cls()

            organism.subagents.append(new_agent)
            return True, f"subagent {subagent_type} added ({len(organism.subagents)} total)"
        except Exception as e:
            return False, f"failed to create subagent: {e}"

    def _remove_subagent(self, mutation: Mutation, organism: Any) -> Tuple[bool, str]:
        """Elimina un sub-agente del organismo."""
        if not organism:
            return False, "no organism reference"

        target_name = mutation.payload.get("subagent_name", "")
        if not target_name:
            return False, "no subagent_name specified"

        # No permitir eliminar sub-agentes críticos (Speaker, Critic, Perceiver, Forecaster)
        critical = ["perceiver", "forecaster", "speaker", "critic"]
        if target_name.lower() in critical:
            return False, f"cannot remove critical subagent: {target_name}"

        # Buscar y eliminar
        for i, agent in enumerate(organism.subagents):
            if target_name.lower() in agent.__class__.__name__.lower():
                removed = organism.subagents.pop(i)
                return True, f"subagent {removed.__class__.__name__} removed ({len(organism.subagents)} total)"

        return False, f"subagent {target_name} not found"

    def _modify_threshold(self, mutation: Mutation, organism: Any) -> Tuple[bool, str]:
        """Modifica un threshold de meta-cognición o leyes."""
        target_component = mutation.target  # "meta_cognition" o "laws"
        threshold_name = mutation.payload.get("threshold", "")
        new_value = mutation.payload.get("value", 0.5)

        if not (0.0 <= new_value <= 1.0):
            return False, f"threshold value out of range: {new_value}"

        if target_component == "meta_cognition" and organism and hasattr(organism, "meta_cognition"):
            mc = organism.meta_cognition
            if threshold_name == "confidence":
                mc.confidence_threshold_system2 = new_value
            elif threshold_name == "stakes":
                mc.stakes_threshold_system2 = new_value
            elif threshold_name == "energy":
                mc.energy_threshold_system2 = new_value
            else:
                return False, f"unknown threshold: {threshold_name}"
            return True, f"meta_cognition.{threshold_name} = {new_value}"

        return False, f"cannot modify threshold on {target_component}"

    def _adjust_workspace(self, mutation: Mutation, organism: Any) -> Tuple[bool, str]:
        """Ajusta capacidad del Global Workspace."""
        if not organism or not hasattr(organism, "global_workspace"):
            return False, "no global workspace"

        new_capacity = mutation.payload.get("capacity", 3)
        if not (1 <= new_capacity <= 12):
            return False, f"capacity out of range: {new_capacity}"

        organism.global_workspace.broadcast_capacity = new_capacity
        return True, f"workspace capacity = {new_capacity}"

    def _adjust_metabolism(self, mutation: Mutation, organism: Any) -> Tuple[bool, str]:
        """Ajusta umbrales del metabolismo."""
        if not organism or not hasattr(organism, "metabolism"):
            return False, "no metabolism"

        threshold_name = mutation.payload.get("threshold", "")
        new_value = mutation.payload.get("value", 0.5)

        if not (0.0 <= new_value <= 1.0):
            return False, f"value out of range: {new_value}"

        metab = organism.metabolism
        if threshold_name == "drowsy":
            metab.drowsy_threshold = new_value
        elif threshold_name == "sleep":
            metab.sleep_threshold = new_value
        elif threshold_name == "wake":
            metab.wake_threshold = new_value
        else:
            return False, f"unknown metabolism threshold: {threshold_name}"

        return True, f"metabolism.{threshold_name} = {new_value}"

    def get_architectural_changes(self) -> List[Dict[str, Any]]:
        """Devuelve historial de cambios arquitecturales."""
        return list(self._architectural_changes)

    def get_stats(self) -> Dict[str, Any]:
        base_stats = super().get_stats()
        base_stats["architectural_changes"] = len(self._architectural_changes)
        base_stats["architectural_types_available"] = ARCHITECTURAL_MUTATION_TYPES
        return base_stats
