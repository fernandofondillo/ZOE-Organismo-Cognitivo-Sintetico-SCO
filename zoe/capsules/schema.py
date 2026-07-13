"""
ZOE v1.1 — Capsule Schema

Define la estructura válida de una cápsula de conocimiento/capacidades.
Una cápsula es un paquete declarativo que ZOE carga al inicializarse
para disponer de conocimiento profesional previo y habilidades específicas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class TrustLevel(str, Enum):
    """Nivel de confianza de una cápsula."""
    VERIFIED = "verified"        # Sello profesional, fuente académica o clínica
    CURATED = "curated"          # Curada por expertos pero sin verificación formal
    COMMUNITY = "community"      # Creada por la comunidad, sin revisión formal
    EXPERIMENTAL = "experimental"  # En desarrollo, no para producción


# Mapa de trust_level a confianza base
TRUST_TO_CONFIDENCE = {
    TrustLevel.VERIFIED: 0.95,
    TrustLevel.CURATED: 0.80,
    TrustLevel.COMMUNITY: 0.55,
    TrustLevel.EXPERIMENTAL: 0.40,
}


@dataclass
class CapsuleMeta:
    """Metadata de una cápsula (lo que va en capsule.yaml)."""
    name: str
    version: str
    description: str
    domain: str
    trust_level: TrustLevel
    provenance: str
    last_updated: str
    content_hash: Optional[str] = None
    
    # Dependencias
    depends_on: List[str] = field(default_factory=list)
    
    # Compatibilidad
    compatible_use_cases: List[str] = field(default_factory=list)
    
    # Peso cognitivo
    load_cost: float = 0.15
    default_confidence: Optional[float] = None  # Si None, se deriva de trust_level
    
    # Componentes
    components: Dict[str, bool] = field(default_factory=lambda: {
        "semantic_memory": False,
        "procedural_skills": False,
        "causal_models": False,
        "emotional_patterns": False,
        "ethical_guidelines": False,
        "validators": False,
        "tools": False,
        "prompts": False,
    })
    
    # Capacidades y restricciones
    capabilities: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    
    # Opcional: expiración
    expires_at: Optional[str] = None
    
    @property
    def effective_confidence(self) -> float:
        """Confianza efectiva: default_confidence o derivada de trust_level."""
        if self.default_confidence is not None:
            return self.default_confidence
        return TRUST_TO_CONFIDENCE.get(self.trust_level, 0.5)


# Schema de validación (campos obligatorios)
REQUIRED_FIELDS = [
    "name", "version", "description", "domain", "trust_level",
    "provenance", "last_updated",
]

VALID_TRUST_LEVELS = {t.value for t in TrustLevel}

VALID_COMPONENTS = {
    "semantic_memory", "procedural_skills", "causal_models",
    "emotional_patterns", "ethical_guidelines", "validators",
    "tools", "prompts",
}


def validate_capsule_yaml(data: Dict[str, Any]) -> List[str]:
    """
    Valida que un dict (parseado de capsule.yaml) cumple el schema.
    
    Returns:
        Lista de errores (vacía si OK).
    """
    errors = []
    
    # Campos obligatorios
    for f in REQUIRED_FIELDS:
        if f not in data:
            errors.append(f"missing_required_field:{f}")
    
    # trust_level válido
    tl = data.get("trust_level")
    if tl and tl not in VALID_TRUST_LEVELS:
        errors.append(f"invalid_trust_level:{tl} (valid: {VALID_TRUST_LEVELS})")
    
    # components válidos
    components = data.get("components", {})
    for key in components:
        if key not in VALID_COMPONENTS:
            errors.append(f"invalid_component:{key}")
    
    # name formato válido (snake_case)
    name = data.get("name", "")
    if name and not all(c.isalnum() or c == "_" for c in name):
        errors.append(f"invalid_name_format:{name} (must be snake_case)")
    
    # version formato semver
    version = data.get("version", "")
    if version and not _is_valid_semver(version):
        errors.append(f"invalid_version_format:{version} (must be semver X.Y.Z)")
    
    # load_cost en rango
    lc = data.get("load_cost", 0.15)
    if not (0.0 <= lc <= 1.0):
        errors.append(f"load_cost_out_of_range:{lc} (must be 0.0-1.0)")
    
    # default_confidence en rango
    dc = data.get("default_confidence")
    if dc is not None and not (0.0 <= dc <= 1.0):
        errors.append(f"default_confidence_out_of_range:{dc}")
    
    return errors


def _is_valid_semver(version: str) -> bool:
    """Valida formato semver básico X.Y.Z."""
    parts = version.split(".")
    if len(parts) != 3:
        return False
    try:
        return all(int(p) >= 0 for p in parts)
    except ValueError:
        return False


def parse_capsule_yaml(data: Dict[str, Any]) -> CapsuleMeta:
    """Convierte un dict YAML en CapsuleMeta. Lanza ValueError si inválido."""
    errors = validate_capsule_yaml(data)
    if errors:
        raise ValueError(f"Invalid capsule YAML: {errors}")
    
    return CapsuleMeta(
        name=data["name"],
        version=data["version"],
        description=data["description"],
        domain=data["domain"],
        trust_level=TrustLevel(data["trust_level"]),
        provenance=data["provenance"],
        last_updated=data["last_updated"],
        content_hash=data.get("content_hash"),
        depends_on=data.get("depends_on", []),
        compatible_use_cases=data.get("compatible_use_cases", []),
        load_cost=data.get("load_cost", 0.15),
        default_confidence=data.get("default_confidence"),
        components=data.get("components", {}),
        capabilities=data.get("capabilities", []),
        restrictions=data.get("restrictions", []),
        expires_at=data.get("expires_at"),
    )
