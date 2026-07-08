"""
ZOE v1.0 — Memory Types (11 tipos especializados)

Especializa LivingMemory en 11 tipos con campos específicos.
Cada tipo tiene políticas de acceso y consolidación distintas.

Los 11 tipos:
1. EpisodicMemory — eventos con contexto espacio-temporal
2. SemanticMemory — conceptos y relaciones
3. ProceduralMemory — habilidades, recetas, algoritmos
4. CausalMemory — causa-efecto verificado
5. EmotionalMemory — marcadores de relevancia
6. CorporalMemory — estado de sensores, capacidades
7. SocialMemory — modelos de otros agentes y usuarios
8. ProspectiveMemory — planes e intenciones futuras
9. CounterfactualMemory — qué habría pasado si
10. EvolutionaryMemory — historial de cambios arquitecturales
11. CulturalMemory — normas, convenciones, contextos sociales
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

from ..core.living_memory import MemoryEntry


class MemoryType(str, Enum):
    """Los 11 tipos de memoria."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CAUSAL = "causal"
    EMOTIONAL = "emotional"
    CORPOREAL = "corporeal"
    SOCIAL = "social"
    PROSPECTIVE = "prospective"
    COUNTERFACTUAL = "counterfactual"
    EVOLUTIONARY = "evolutionary"
    CULTURAL = "cultural"


# Descripciones de cada tipo
MEMORY_TYPE_DESCRIPTIONS = {
    MemoryType.EPISODIC: "Eventos con contexto espacio-temporal",
    MemoryType.SEMANTIC: "Conceptos y relaciones (conocimiento general)",
    MemoryType.PROCEDURAL: "Habilidades, recetas, algoritmos",
    MemoryType.CAUSAL: "Relaciones causa-efecto verificadas",
    MemoryType.EMOTIONAL: "Marcadores de relevancia (no emociones humanas)",
    MemoryType.CORPOREAL: "Estado de sensores, capacidades y limitaciones",
    MemoryType.SOCIAL: "Modelos de otros agentes y usuarios",
    MemoryType.PROSPECTIVE: "Planes e intenciones futuras",
    MemoryType.COUNTERFACTUAL: "Simulaciones de qué habría pasado si",
    MemoryType.EVOLUTIONARY: "Historial de cambios arquitecturales (mutaciones)",
    MemoryType.CULTURAL: "Normas, convenciones, contextos sociales",
}


@dataclass
class EpisodicEntry(MemoryEntry):
    """Evento con contexto espacio-temporal."""

    event_time: float = 0.0
    location: str = ""  # contexto digital: "vps_ceo", "mobile", etc.
    participants: List[str] = field(default_factory=list)
    outcome: str = ""  # qué pasó


@dataclass
class SemanticEntry(MemoryEntry):
    """Concepto o relación."""

    concept: str = ""
    relations: Dict[str, List[str]] = field(default_factory=dict)  # {relación: [conceptos]}
    examples: List[str] = field(default_factory=list)


@dataclass
class ProceduralEntry(MemoryEntry):
    """Habilidad o receta."""

    procedure_name: str = ""
    steps: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    success_rate: float = 0.5


@dataclass
class CausalEntry(MemoryEntry):
    """Relación causa-efecto."""

    cause: str = ""
    effect: str = ""
    confidence: float = 0.5
    evidence_count: int = 0
    counterexamples: int = 0


@dataclass
class EmotionalEntry(MemoryEntry):
    """Marcador de relevancia emocional."""

    marker_type: str = ""  # "positive", "negative", "surprise", "curiosity"
    intensity: float = 0.5
    trigger: str = ""
    associated_event: str = ""


@dataclass
class CorporealEntry(MemoryEntry):
    """Estado corporal (sensores, capacidades)."""

    sensor_name: str = ""
    sensor_state: str = ""
    capacity: str = ""
    limitation: str = ""


@dataclass
class SocialEntry(MemoryEntry):
    """Modelo de otro agente o usuario."""

    agent_id: str = ""
    agent_type: str = ""  # "human", "zoe", "other_ai", "system"
    traits: Dict[str, float] = field(default_factory=dict)
    preferences: List[str] = field(default_factory=list)
    interaction_count: int = 0
    trust_level: float = 0.5


@dataclass
class ProspectiveEntry(MemoryEntry):
    """Plan o intención futura."""

    intention_id: str = ""
    planned_action: str = ""
    target_time: float = 0.0
    priority: float = 0.5
    prerequisites: List[str] = field(default_factory=list)
    status: str = "pending"  # pending | in_progress | completed | abandoned


@dataclass
class CounterfactualEntry(MemoryEntry):
    """Simulación de qué habría pasado si."""

    original_event: str = ""
    alternative_action: str = ""
    predicted_outcome: str = ""
    actual_outcome: str = ""  # si se verificó
    divergence_score: float = 0.0


@dataclass
class EvolutionaryEntry(MemoryEntry):
    """Cambio arquitectural (mutación)."""

    mutation_id: str = ""
    mutation_type: str = ""
    component_affected: str = ""
    before_state: str = ""
    after_state: str = ""
    success: bool = True
    rollback_available: bool = True


@dataclass
class CulturalEntry(MemoryEntry):
    """Norma, convención, contexto social."""

    norm: str = ""
    context: str = ""
    authority: str = ""  # quién establece la norma
    scope: str = "general"  # general | specific_context
    enforcement: str = "soft"  # soft | hard


# Mapa de tipo → clase
ENTRY_CLASSES = {
    MemoryType.EPISODIC: EpisodicEntry,
    MemoryType.SEMANTIC: SemanticEntry,
    MemoryType.PROCEDURAL: ProceduralEntry,
    MemoryType.CAUSAL: CausalEntry,
    MemoryType.EMOTIONAL: EmotionalEntry,
    MemoryType.CORPOREAL: CorporealEntry,
    MemoryType.SOCIAL: SocialEntry,
    MemoryType.PROSPECTIVE: ProspectiveEntry,
    MemoryType.COUNTERFACTUAL: CounterfactualEntry,
    MemoryType.EVOLUTIONARY: EvolutionaryEntry,
    MemoryType.CULTURAL: CulturalEntry,
}


def create_entry(memory_type: MemoryType, content: str, **kwargs) -> MemoryEntry:
    """
    Factory para crear entry del tipo correcto.

    Args:
        memory_type: tipo de memoria
        content: contenido base
        **kwargs: campos específicos del tipo

    Returns:
        Entry del tipo correcto
    """
    entry_class = ENTRY_CLASSES.get(memory_type, MemoryEntry)
    # MemoryEntry base fields
    base_fields = {
        "id": kwargs.pop("id", ""),
        "content": content,
        "type": memory_type.value,
        "confidence": kwargs.pop("confidence", 0.5),
        "salience": kwargs.pop("salience", 0.5),
        "provenance": kwargs.pop("provenance", "unknown"),
        "metadata": kwargs.pop("metadata", {}),
    }
    # Type-specific fields
    return entry_class(**base_fields, **kwargs)


def get_all_types() -> List[MemoryType]:
    """Devuelve los 11 tipos de memoria."""
    return list(MemoryType)


def get_type_description(memory_type: MemoryType) -> str:
    """Descripción de un tipo."""
    return MEMORY_TYPE_DESCRIPTIONS.get(memory_type, "unknown type")


class MemoryTypeStats:
    """Estadísticas por tipo de memoria."""

    def __init__(self):
        self.counts: Dict[str, int] = {t.value: 0 for t in MemoryType}
        self.total: int = 0

    def increment(self, memory_type: MemoryType) -> None:
        self.counts[memory_type.value] += 1
        self.total += 1

    def decrement(self, memory_type: MemoryType) -> None:
        if self.counts[memory_type.value] > 0:
            self.counts[memory_type.value] -= 1
            self.total -= 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counts": self.counts.copy(),
            "total": self.total,
            "types_active": sum(1 for c in self.counts.values() if c > 0),
        }
