"""
ZOE v1.0 — Trajectory Chain

Cadena criptográfica de mutaciones. Cada mutación es un commit firmado
con hash, diff, justificación, y enlace al commit anterior.

Es la memoria autobiográfica del organismo: registra cada cambio
que ha sufrido, en orden, verificable, inmutable.

Implementa la 3ra ley (provenance) y la 4ta ley (coste):
- 3ra ley: cada mutación tiene provenance
- 4ta ley: cada mutación tiene coste registrado
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Mutation:
    """
    Una mutación propuesta al organismo.

    Tipos:
    - add_memory: añadir entry a memoria
    - strengthen_belief: aumentar confianza en creencia
    - weaken_belief: disminuir confianza
    - add_skill_subgraph: añadir habilidad
    - update_world_model: refinar predictor
    - adjust_threshold: cambiar parámetro de homeostasis
    - federate_learning: propagar mutación a otras ZOEs
    - rollback_previous: revertir mutación previa
    """

    id: str
    type: str  # add_memory | strengthen_belief | weaken_belief | add_skill_subgraph | ...
    target: str  # qué componente afecta
    payload: Dict[str, Any]  # datos de la mutación
    justification: str  # por qué se hace
    provenance: str  # 3ra ley: origen
    cost: float  # 4ta ley: coste
    confidence: float  # 5ta ley: confianza
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None  # firma criptográfica
    prev_hash: Optional[str] = None  # enlace a mutación anterior
    hash: Optional[str] = None  # hash de esta mutación
    applied: bool = False  # si se aplicó
    rolled_back: bool = False  # si se revirtió

    def compute_hash(self) -> str:
        """Calcula hash de la mutación."""
        data = {
            "id": self.id,
            "type": self.type,
            "target": self.target,
            "payload": self.payload,
            "justification": self.justification,
            "provenance": self.provenance,
            "cost": self.cost,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
        }
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.hash is None:
            d["hash"] = self.compute_hash()
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Mutation":
        """Sprint 5.8 — Deserializa una mutación desde dict."""
        return cls(
            id=d["id"],
            type=d["type"],
            target=d["target"],
            payload=d.get("payload", {}),
            justification=d.get("justification", ""),
            provenance=d.get("provenance", ""),
            cost=d.get("cost", 0.0),
            confidence=d.get("confidence", 0.5),
            timestamp=d.get("timestamp", 0.0),
            signature=d.get("signature"),
            prev_hash=d.get("prev_hash"),
            hash=d.get("hash"),
            applied=d.get("applied", False),
            rolled_back=d.get("rolled_back", False),
        )


class TrajectoryChain:
    """
    Cadena criptográfica de mutaciones.

    Cada mutación se enlaza a la anterior via prev_hash.
    La cadena es verificable: si cualquier mutación se altera,
    verify_chain() devuelve False.

    Es la memoria autobiográfica del organismo.
    """

    def __init__(self, organism_id: str = "zoe_default"):
        self.organism_id = organism_id
        self._mutations: List[Mutation] = []
        self._last_hash: Optional[str] = None
        self._next_id = 0
        # Sprint 5.8 — path de persistencia (si se setea, save tras cada commit)
        self._persist_path: Optional[str] = None

    def set_persist_path(self, path: str) -> None:
        """Sprint 5.8 — Setea el path de persistencia automática."""
        self._persist_path = path

    def commit(self, mutation: Mutation) -> str:
        """
        Añade una mutación a la cadena.

        Args:
            mutation: mutación a commitear

        Returns:
            hash de la mutación commiteada
        """
        # Asignar ID si no tiene
        if not mutation.id:
            self._next_id += 1
            mutation.id = f"mut_{self.organism_id}_{self._next_id}"

        # Enlazar con mutación anterior
        mutation.prev_hash = self._last_hash

        # Calcular hash
        mutation.hash = mutation.compute_hash()

        # Firmar (en Fase 1 con hash simple; Fase 4 con ECDSA real)
        mutation.signature = self._sign(mutation)

        # Marcar como aplicada
        mutation.applied = True

        # Añadir a la cadena
        self._mutations.append(mutation)
        self._last_hash = mutation.hash

        logger.info(
            f"TrajectoryChain commit: {mutation.id} (type={mutation.type}, "
            f"target={mutation.target}, hash={mutation.hash[:16]}...)"
        )

        # Sprint 5.8 — persistir tras cada commit si hay path configurado
        if self._persist_path:
            try:
                self.save_to_disk(self._persist_path)
            except Exception as e:
                logger.warning(f"TrajectoryChain persist failed: {e}")

        return mutation.hash

    def _sign(self, mutation: Mutation) -> str:
        """
        Firma la mutación.

        En Fase 1: hash simple del contenido + timestamp.
        En Fase 4: ECDSA con clave privada del organismo.
        """
        data = f"{mutation.hash}:{mutation.timestamp}:{self.organism_id}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def verify_chain(self) -> bool:
        """
        Verifica integridad de toda la cadena.

        Returns:
            True si la cadena es íntegra, False si alguna mutación fue alterada
        """
        prev_hash = None
        for mutation in self._mutations:
            # Verificar hash
            expected_hash = mutation.compute_hash()
            if mutation.hash != expected_hash:
                logger.warning(f"Hash mismatch in mutation {mutation.id}")
                return False

            # Verificar enlace
            if mutation.prev_hash != prev_hash:
                logger.warning(f"Chain link broken at mutation {mutation.id}")
                return False

            prev_hash = mutation.hash

        return True

    def rollback(self, mutation_id: str) -> Tuple[bool, str]:
        """
        Marca una mutación como revertida.

        No elimina la mutación de la cadena (la cadena es inmutable).
        Añade una mutación de rollback que la anula.

        Args:
            mutation_id: ID de la mutación a revertir

        Returns:
            (success, reason)
        """
        # Buscar la mutación
        target = None
        for m in self._mutations:
            if m.id == mutation_id and not m.rolled_back:
                target = m
                break

        if not target:
            return False, f"mutation {mutation_id} not found or already rolled back"

        # Marcar como revertida
        target.rolled_back = True

        # Crear mutación de rollback
        self._next_id += 1
        rollback_mutation = Mutation(
            id=f"rollback_{self.organism_id}_{self._next_id}",
            type="rollback_previous",
            target=target.id,
            payload={"original_type": target.type, "original_target": target.target},
            justification=f"rollback of {target.id}: {target.justification[:50]}",
            provenance="trajectory_chain:rollback",
            cost=0.1,
            confidence=1.0,
        )
        self.commit(rollback_mutation)

        return True, f"rolled back {mutation_id}"

    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Devuelve historial de mutaciones."""
        mutations = self._mutations[-n:] if n else self._mutations
        return [m.to_dict() for m in mutations]

    def get_active_mutations(self) -> List[Mutation]:
        """Devuelve mutaciones activas (no revertidas)."""
        return [m for m in self._mutations if not m.rolled_back and m.type != "rollback_previous"]

    def get_mutation(self, mutation_id: str) -> Optional[Mutation]:
        """Obtiene una mutación por ID."""
        for m in self._mutations:
            if m.id == mutation_id:
                return m
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de la cadena."""
        type_counts: Dict[str, int] = {}
        for m in self._mutations:
            type_counts[m.type] = type_counts.get(m.type, 0) + 1

        return {
            "organism_id": self.organism_id,
            "total_mutations": len(self._mutations),
            "active_mutations": len(self.get_active_mutations()),
            "rolled_back_mutations": sum(1 for m in self._mutations if m.rolled_back),
            "type_counts": type_counts,
            "chain_verified": self.verify_chain(),
            "last_hash": self._last_hash[:16] + "..." if self._last_hash else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialización completa."""
        return {
            "organism_id": self.organism_id,
            "mutations": [m.to_dict() for m in self._mutations],
            "stats": self.get_stats(),
        }

    def summary(self) -> str:
        """Resumen legible."""
        stats = self.get_stats()
        return (
            f"TrajectoryChain(organism={self.organism_id}, "
            f"mutations={stats['total_mutations']}, "
            f"active={stats['active_mutations']}, "
            f"verified={stats['chain_verified']})"
        )

    # ============================================================
    # Sprint 5.8 — Persistencia entre sesiones
    # ============================================================

    def save_to_disk(self, path: str) -> None:
        """Sprint 5.8 — Persiste la cadena completa a disco como JSON.

        Permite que la trayectoria de ZOE sobreviva entre sesiones.
        Antes de este fix, la blockchain de mutaciones se perdia al reiniciar.

        Args:
            path: ruta del archivo JSON a escribir
        """
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "organism_id": self.organism_id,
            "mutations": [m.to_dict() for m in self._mutations],
            "next_id": self._next_id,
            "last_hash": self._last_hash,
            "version": 1,
        }
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        logger.info(f"TrajectoryChain saved to {path} ({len(self._mutations)} mutations)")

    @classmethod
    def load_from_disk(cls, path: str) -> Optional["TrajectoryChain"]:
        """Sprint 5.8 — Carga la cadena desde disco.

        Si el archivo no existe, devuelve None.
        Si el archivo existe pero esta corrupto, devuelve None y logea warning.

        Args:
            path: ruta del archivo JSON

        Returns:
            TrajectoryChain cargada, o None si no existe o esta corrupta
        """
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            chain = cls(organism_id=data.get("organism_id", "zoe_default"))
            for m_dict in data.get("mutations", []):
                mutation = Mutation.from_dict(m_dict)
                chain._mutations.append(mutation)
            chain._next_id = data.get("next_id", len(chain._mutations))
            chain._last_hash = data.get("last_hash")
            # Verificar integridad de la cadena cargada
            if not chain.verify_chain():
                logger.warning(f"TrajectoryChain loaded from {path} but chain verification FAILED")
            else:
                logger.info(f"TrajectoryChain loaded from {path} ({len(chain._mutations)} mutations, verified=True)")
            return chain
        except Exception as e:
            logger.warning(f"TrajectoryChain load failed from {path}: {e}. Creating new chain.")
            return None
