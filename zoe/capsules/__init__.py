"""
ZOE v1.1 — Capsules System

Sistema de cápsulas de conocimiento/capacidades para ZOE.

Una cápsula es un paquete declarativo que se carga al inicializar ZOE
para disponer de conocimiento profesional previo y habilidades específicas.

Componentes:
- schema: definición de estructura válida
- loader: carga cápsulas desde disco y las inyecta en componentes
- registry: índice de cápsulas disponibles
- scaffold: CLI para crear, validar y empaquetar cápsulas
"""

from .schema import (
    CapsuleMeta, TrustLevel, parse_capsule_yaml, validate_capsule_yaml,
    TRUST_TO_CONFIDENCE,
)
from .loader import CapsuleLoader, LoadedCapsule, CapsuleLoadError
from .registry import CapsuleRegistry

__all__ = [
    "CapsuleMeta", "TrustLevel", "parse_capsule_yaml", "validate_capsule_yaml",
    "TRUST_TO_CONFIDENCE", "CapsuleLoader", "LoadedCapsule", "CapsuleLoadError",
    "CapsuleRegistry",
]
