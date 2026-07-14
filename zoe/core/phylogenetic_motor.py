"""
ZOE v1.0 — Phylogenetic Motor

Evolución de especie, no solo de individuo.

Diferencia con Motor Ontogenético:
- Ontogenético: cambia un individuo (una ZOE concreta)
- Filogenético: cambia la especie (todas las ZOEs)

Flujo:
1. ZOE A descubre mejora arquitectural
2. Publica en Pool Filogenético
3. Otras ZOEs (B, C, D...) la prueban
4. Solo si mejora métricas verificables → la incorporan
5. Especies ZOE diverge/converge con criterio

En Fase 0.5 es un esqueleto en memoria.
En Fase 4 evoluciona a federación distribuida con quorum criptográfico.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ArchitecturalImprovement:
    """Una mejora arquitectural propuesta por una ZOE."""

    id: str
    proposer: str  # ID de la ZOE que la propone
    timestamp: float
    description: str
    change_type: str  # add_module | remove_module | modify_module | add_memory_type | ...
    payload: Dict[str, Any]  # especificación de la mejora
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    status: str = "proposed"  # proposed | testing | validated | rejected | incorporated
    tested_by: List[str] = field(default_factory=list)  # ZOEs que la probaron
    incorporated_by: List[str] = field(default_factory=list)  # ZOEs que la adoptaron
    rejection_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposer": self.proposer,
            "timestamp": self.timestamp,
            "description": self.description,
            "change_type": self.change_type,
            "payload": self.payload,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "status": self.status,
            "tested_by": self.tested_by,
            "incorporated_by": self.incorporated_by,
            "rejection_reasons": self.rejection_reasons,
        }


class PhylogeneticPool:
    """
    Pool filogenético compartido por todas las ZOEs.

    En Fase 0.5 es en memoria (un singleton).
    En Fase 4 evoluciona a federación distribuida con quorum criptográfico.
    """

    _instance: Optional["PhylogeneticPool"] = None

    @classmethod
    def get_instance(cls) -> "PhylogeneticPool":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._improvements: Dict[str, ArchitecturalImprovement] = {}
        self._next_id = 0
        self._species_version: str = "zoe-species-v0.5"
        self._species_history: List[Dict[str, Any]] = []

    def publish(self, improvement: ArchitecturalImprovement) -> str:
        """Publica una mejora en el pool."""
        self._improvements[improvement.id] = improvement
        logger.info(
            f"PhylogeneticPool: mejora {improvement.id} publicada por {improvement.proposer}"
        )
        return improvement.id

    def get_pending(self, zoe_id: str) -> List[ArchitecturalImprovement]:
        """Devuelve mejoras pendientes de probar por una ZOE específica."""
        pending = []
        for imp in self._improvements.values():
            if (
                imp.status in ["proposed", "testing"]
                and zoe_id not in imp.tested_by
                and zoe_id != imp.proposer
            ):
                pending.append(imp)
        return pending

    def get_validated(self) -> List[ArchitecturalImprovement]:
        """Devuelve mejoras validadas listas para incorporar."""
        return [i for i in self._improvements.values() if i.status == "validated"]

    def record_test_result(
        self,
        improvement_id: str,
        zoe_id: str,
        passed: bool,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        rejection_reason: str = "",
    ) -> None:
        """Registra el resultado de una prueba por una ZOE."""
        if improvement_id not in self._improvements:
            return

        imp = self._improvements[improvement_id]
        imp.tested_by.append(zoe_id)
        imp.metrics_before.update(metrics_before)
        imp.metrics_after.update(metrics_after)

        if not passed:
            imp.status = "rejected"
            if rejection_reason:
                imp.rejection_reasons.append(f"{zoe_id}: {rejection_reason}")
        else:
            # Si al menos 2 ZOEs validan, se marca como validada
            if len(imp.tested_by) >= 2:
                imp.status = "validated"
                logger.info(
                    f"PhylogeneticPool: mejora {improvement_id} validada por {len(imp.tested_by)} ZOEs"
                )

    def mark_incorporated(self, improvement_id: str, zoe_id: str) -> None:
        """Marca que una ZOE incorporó la mejora."""
        if improvement_id in self._improvements:
            imp = self._improvements[improvement_id]
            if zoe_id not in imp.incorporated_by:
                imp.incorporated_by.append(zoe_id)
                logger.info(
                    f"PhylogeneticPool: mejora {improvement_id} incorporada por {zoe_id}"
                )

    def get_species_state(self) -> Dict[str, Any]:
        """Estado de la especie ZOE."""
        return {
            "species_version": self._species_version,
            "total_improvements": len(self._improvements),
            "proposed": sum(1 for i in self._improvements.values() if i.status == "proposed"),
            "testing": sum(1 for i in self._improvements.values() if i.status == "testing"),
            "validated": sum(1 for i in self._improvements.values() if i.status == "validated"),
            "rejected": sum(1 for i in self._improvements.values() if i.status == "rejected"),
            "incorporation_rate": (
                sum(len(i.incorporated_by) for i in self._improvements.values())
                / max(1, len(self._improvements))
            ),
        }


class PhylogeneticMotor:
    """
    Motor filogenético para una ZOE específica.

    Permite a una ZOE:
    - Publicar mejoras que descubre
    - Probar mejoras de otras ZOEs
    - Incorporar mejoras validadas
    """

    def __init__(self, zoe_id: str, pool_path: Optional[str] = None):
        self.zoe_id = zoe_id
        if pool_path:
            # Import lazy para evitar circular import
            from .distributed_phylogenetic_pool import DistributedPhylogeneticPool
            self.pool = DistributedPhylogeneticPool(pool_path)
        else:
            self.pool = PhylogeneticPool.get_instance()
        self._next_improvement_id = 0

    def publish_improvement(
        self,
        description: str,
        change_type: str,
        payload: Dict[str, Any],
        metrics_before: Dict[str, float],
    ) -> str:
        """Publica una mejora arquitectural descubierta."""
        self._next_improvement_id += 1
        improvement = ArchitecturalImprovement(
            id=f"imp_{self.zoe_id}_{self._next_improvement_id}",
            proposer=self.zoe_id,
            timestamp=time.time(),
            description=description,
            change_type=change_type,
            payload=payload,
            metrics_before=metrics_before,
        )
        return self.pool.publish(improvement)

    def get_pending_improvements(self) -> List[ArchitecturalImprovement]:
        """Devuelve mejoras pendientes de probar por esta ZOE."""
        return self.pool.get_pending(self.zoe_id)

    def try_improvement(
        self,
        improvement: ArchitecturalImprovement,
        test_function,
    ) -> Dict[str, Any]:
        """
        Prueba una mejora en sandbox.

        Args:
            improvement: la mejora a probar
            test_function: función que toma payload + metrics_before,
                          devuelve (passed, metrics_after, reason)

        Returns:
            Resultado de la prueba
        """
        try:
            passed, metrics_after, reason = test_function(
                improvement.payload, improvement.metrics_before
            )
            self.pool.record_test_result(
                improvement_id=improvement.id,
                zoe_id=self.zoe_id,
                passed=passed,
                metrics_before=improvement.metrics_before,
                metrics_after=metrics_after,
                rejection_reason=reason,
            )
            return {
                "improvement_id": improvement.id,
                "passed": passed,
                "metrics_after": metrics_after,
                "reason": reason,
            }
        except Exception as e:
            logger.error(f"Error probando mejora {improvement.id}: {e}")
            self.pool.record_test_result(
                improvement_id=improvement.id,
                zoe_id=self.zoe_id,
                passed=False,
                metrics_before=improvement.metrics_before,
                metrics_after={},
                rejection_reason=f"exception: {e}",
            )
            return {
                "improvement_id": improvement.id,
                "passed": False,
                "metrics_after": {},
                "reason": str(e),
            }

    def incorporate_validated(self) -> List[str]:
        """Incorpora mejoras validadas por la especie."""
        incorporated = []
        for imp in self.pool.get_validated():
            if self.zoe_id not in imp.incorporated_by:
                # Aquí en Fase 0.5 solo marcamos; en Fase 4 aplicamos el cambio real
                self.pool.mark_incorporated(imp.id, self.zoe_id)
                incorporated.append(imp.id)
                logger.info(
                    f"PhylogeneticMotor {self.zoe_id}: incorporada mejora {imp.id}"
                )
        return incorporated

    def get_species_state(self) -> Dict[str, Any]:
        return self.pool.get_species_state()
