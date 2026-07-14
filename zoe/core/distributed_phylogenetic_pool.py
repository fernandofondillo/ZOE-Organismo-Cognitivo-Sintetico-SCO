"""
ZOE v2.1 -- DistributedPhylogeneticPool

Extiende PhylogeneticPool con persistencia en disco (JSON).
Permite que multiples ZOEs que montan el mismo SSD compartan
mejoras arquitecturales.

Escenario: dos MacBooks con el mismo SSD Crucial X9.
ZOE A publica una mejora -> se guarda en el SSD.
ZOE B al arrancar lee el archivo -> descubre la mejora.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency
_PhylogeneticPool = None
_ArchitecturalImprovement = None


def _get_classes():
    """Lazy import to avoid circular imports at module level."""
    global _PhylogeneticPool, _ArchitecturalImprovement
    if _PhylogeneticPool is None:
        from .phylogenetic_motor import PhylogeneticPool, ArchitecturalImprovement
        _PhylogeneticPool = PhylogeneticPool
        _ArchitecturalImprovement = ArchitecturalImprovement
    return _PhylogeneticPool, _ArchitecturalImprovement


class DistributedPhylogeneticPool:
    """
    PhylogeneticPool con persistencia en disco JSON.

    Mantiene la misma interfaz que PhylogeneticPool.
    Cada write sincroniza al disco; cada read recarga si el archivo cambio.
    """

    def __init__(self, pool_path: str):
        PhylogeneticPool, ArchitecturalImprovement = _get_classes()
        # Compose with PhylogeneticPool instead of inheriting to avoid __init__ conflicts
        self._pool = PhylogeneticPool()
        self._pool_path = pool_path
        self._last_mtime = 0.0
        self._ArchitecturalImprovement = ArchitecturalImprovement
        self._load()

    # Delegate property access to composed pool
    @property
    def _improvements(self):
        return self._pool._improvements

    @property
    def _species_version(self):
        return self._pool._species_version

    @_species_version.setter
    def _species_version(self, value):
        self._pool._species_version = value

    def _load(self) -> None:
        """Carga mejoras desde disco si el archivo existe y cambio."""
        if not os.path.exists(self._pool_path):
            return
        try:
            mtime = os.path.getmtime(self._pool_path)
            if mtime <= self._last_mtime:
                return
            with open(self._pool_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for imp_data in data.get("improvements", []):
                imp = self._ArchitecturalImprovement(**imp_data)
                self._pool._improvements[imp.id] = imp
            self._pool._species_version = data.get(
                "species_version", self._pool._species_version
            )
            self._last_mtime = mtime
            logger.info(
                f"DistributedPhylogeneticPool: loaded "
                f"{len(self._pool._improvements)} improvements from {self._pool_path}"
            )
        except Exception as e:
            logger.warning(f"DistributedPhylogeneticPool: load failed: {e}")

    def _save(self) -> None:
        """Guarda mejoras a disco."""
        try:
            os.makedirs(os.path.dirname(self._pool_path), exist_ok=True)
            data = {
                "species_version": self._pool._species_version,
                "updated_at": time.time(),
                "improvements": [
                    imp.to_dict() for imp in self._pool._improvements.values()
                ],
            }
            tmp_path = self._pool_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self._pool_path)
            self._last_mtime = os.path.getmtime(self._pool_path)
        except Exception as e:
            logger.warning(f"DistributedPhylogeneticPool: save failed: {e}")

    def publish(self, improvement) -> str:
        """Publica y sincroniza a disco."""
        result = self._pool.publish(improvement)
        self._save()
        return result

    def get_pending(self, zoe_id: str) -> List[Any]:
        """Devuelve mejoras pendientes."""
        self._load()
        return self._pool.get_pending(zoe_id)

    def get_validated(self) -> List[Any]:
        """Devuelve mejoras validadas."""
        self._load()
        return self._pool.get_validated()

    def record_test_result(
        self,
        improvement_id: str,
        zoe_id: str,
        passed: bool,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        rejection_reason: str = "",
    ) -> None:
        """Registra resultado y sincroniza."""
        self._pool.record_test_result(
            improvement_id, zoe_id, passed,
            metrics_before, metrics_after, rejection_reason,
        )
        self._save()

    def mark_incorporated(self, improvement_id: str, zoe_id: str) -> None:
        """Marca incorporada y sincroniza."""
        self._pool.mark_incorporated(improvement_id, zoe_id)
        self._save()

    def get_species_state(self) -> Dict[str, Any]:
        """Estado de la especie."""
        self._load()
        return self._pool.get_species_state()
