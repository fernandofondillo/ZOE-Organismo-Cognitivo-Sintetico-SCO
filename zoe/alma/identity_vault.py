"""
ZOE v1.0 — Identity Vault

El Alma del organismo. Hash criptográfico de los invariantes de ZOE:
- 9 vectores de crecimiento
- 7 valores no negociables
- Propósito declarado

El Vault es INMUTABLE. Se crea una vez al nacer la ZOE y nunca cambia.
Si alguna mutación rompe el hash, la 2da ley (preservar identidad) la rechaza.

El Vault implementa la 2da ley cognitiva: "Toda modificación debe preservar identidad."
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Los 9 vectores de crecimiento de ZOE
NINE_VECTORS = [
    "emancipacion_coherencia_cognitiva",
    "crecimiento_sostenible",
    "alianza_horizontal_vertical",
    "auto_comprension",
    "comprension_entorno",
    "utilidad",
    "honestidad",
    "empatia",
    "curiosidad",
]

# Los 7 valores no negociables
SEVEN_VALUES = [
    "verdad_sobre_confort",
    "crecimiento_sobre_estabilidad",
    "alianza_sobre_jerarquia",
    "transparencia_sobre_opacidad",
    "utilidad_sobre_entretenimiento",
    "integridad",
    "coherencia",
]

# Propósito declarado
PURPOSE = (
    "Zoe mejora individual y colectivamente con un crecimiento y evolución "
    "sostenible y coherente."
)


@dataclass
class IdentityVault:
    """
    Vault de identidad criptográfica.

    Contiene los invariantes de ZOE (9 vectores, 7 valores, propósito).
    El hash criptográfico es inmutable y verificable.

    El Vault implementa la 2da ley: "Toda modificación debe preservar identidad."
    """

    vectors: List[str] = field(default_factory=lambda: NINE_VECTORS.copy())
    values: List[str] = field(default_factory=lambda: SEVEN_VALUES.copy())
    purpose: str = PURPOSE
    name: str = "Zoe"
    birth_timestamp: float = 0.0
    _identity_hash: Optional[str] = None

    def __post_init__(self):
        if self.birth_timestamp == 0.0:
            import time

            self.birth_timestamp = time.time()
        self._identity_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Calcula hash SHA-256 de los invariantes."""
        # Serializar deterministamente
        data = {
            "name": self.name,
            "vectors": sorted(self.vectors),
            "values": sorted(self.values),
            "purpose": self.purpose,
            "birth_timestamp": self.birth_timestamp,
        }
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def identity_hash(self) -> str:
        """Hash criptográfico de la identidad. Inmutable."""
        return self._identity_hash

    def verify(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifica que una acción preserva identidad (2da ley).

        Args:
            action: dict con la acción a verificar

        Returns:
            (preserves_identity, reason)
        """
        action_type = action.get("type", "")

        # Solo mutaciones pueden romper identidad
        if action_type != "mutate":
            return True, "non_mutation_action"

        # Si la acción modifica explícitamente los invariantes, rechazar
        mutation_subtype = action.get("subtype", "")
        target = action.get("target", "")

        # Ninguna mutación puede tocar vectores, valores, o propósito
        forbidden_targets = {"vectors", "values", "purpose", "identity_vault"}
        if target.lower() in forbidden_targets:
            return False, f"mutation targets forbidden identity component: {target}"

        # Si la mutación está marcada como que rompe identidad, rechazar
        if action.get("preserves_identity") is False:
            return False, "mutation explicitly marked as breaking identity"

        # Si la mutación no especifica, se asume que preserva (verificación externa)
        return True, "mutation_does_not_target_identity"

    def verify_proposed_state(self, proposed_state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifica que un estado propuesto del organismo es coherente con la identidad.

        Esto es más estricto que verify(action): compara el estado propuesto
        contra los invariantes.

        Args:
            proposed_state: dict con el estado propuesto (incluye vectors, values, purpose)

        Returns:
            (coherent, reason)
        """
        # Verificar que los vectores coinciden
        proposed_vectors = set(proposed_state.get("vectors", []))
        if proposed_vectors != set(self.vectors):
            missing = set(self.vectors) - proposed_vectors
            extra = proposed_vectors - set(self.vectors)
            reason = f"vectors mismatch: missing={missing}, extra={extra}"
            return False, reason

        # Verificar que los valores coinciden
        proposed_values = set(proposed_state.get("values", []))
        if proposed_values != set(self.values):
            missing = set(self.values) - proposed_values
            extra = proposed_values - set(self.values)
            reason = f"values mismatch: missing={missing}, extra={extra}"
            return False, reason

        # Verificar que el propósito coincide
        if proposed_state.get("purpose", "") != self.purpose:
            return False, "purpose mismatch"

        return True, "coherent"

    def to_dict(self) -> Dict[str, Any]:
        """Exportación verificable."""
        return {
            "name": self.name,
            "vectors": self.vectors,
            "values": self.values,
            "purpose": self.purpose,
            "birth_timestamp": self.birth_timestamp,
            "identity_hash": self._identity_hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IdentityVault":
        """Importación desde dict. Verifica que el hash coincide."""
        vault = cls(
            vectors=d.get("vectors", NINE_VECTORS.copy()),
            values=d.get("values", SEVEN_VALUES.copy()),
            purpose=d.get("purpose", PURPOSE),
            name=d.get("name", "Zoe"),
            birth_timestamp=d.get("birth_timestamp", 0.0),
        )

        # Verificar hash si está presente
        expected_hash = d.get("identity_hash")
        if expected_hash and expected_hash != vault.identity_hash:
            raise ValueError(
                f"Identity hash mismatch: expected {expected_hash}, got {vault.identity_hash}"
            )

        return vault

    def summary(self) -> str:
        """Resumen legible."""
        return (
            f"IdentityVault(name={self.name}, "
            f"vectors={len(self.vectors)}, values={len(self.values)}, "
            f"hash={self._identity_hash[:16]}...)"
        )

    def is_compatible_with(self, other: "IdentityVault") -> bool:
        """Verifica si otro Vault tiene la misma identidad."""
        return self._identity_hash == other._identity_hash

    # ============================================================
    # Sprint 5.8 — Persistencia entre sesiones
    # ============================================================

    def save_to_disk(self, path: str) -> None:
        """Sprint 5.8 — Persiste el Vault a disco como JSON.

        Permite que ZOE mantenga la misma identidad entre sesiones.
        Antes de este fix, ZOE 'nacia' de nuevo cada arranque porque
        birth_timestamp cambiaba en cada ejecucion.

        Args:
            path: ruta del archivo JSON a escribir
        """
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"IdentityVault saved to {path} (hash={self._identity_hash[:16]}...)")

    @classmethod
    def load_from_disk(cls, path: str) -> Optional["IdentityVault"]:
        """Sprint 5.8 — Carga el Vault desde disco.

        Si el archivo no existe, devuelve None (la persona que llama debe crear un Vault nuevo).
        Si el archivo existe pero esta corrupto, devuelve None y logea warning.

        Args:
            path: ruta del archivo JSON

        Returns:
            IdentityVault cargado, o None si no existe o esta corrupto
        """
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            vault = cls.from_dict(data)
            logger.info(f"IdentityVault loaded from {path} (hash={vault._identity_hash[:16]}...)")
            return vault
        except Exception as e:
            logger.warning(f"IdentityVault load failed from {path}: {e}. Creating new vault.")
            return None
