"""Tests para Memory Types (Fase 1) — 11 tipos especializados."""

import pytest

from zoe.memory.memory_types import (
    MemoryType,
    EpisodicEntry,
    SemanticEntry,
    ProceduralEntry,
    CausalEntry,
    EmotionalEntry,
    CorporealEntry,
    SocialEntry,
    ProspectiveEntry,
    CounterfactualEntry,
    EvolutionaryEntry,
    CulturalEntry,
    ENTRY_CLASSES,
    create_entry,
    get_all_types,
    get_type_description,
    MemoryTypeStats,
)


def test_memory_type_enum_complete():
    """Los 11 tipos están definidos."""
    assert len(MemoryType) == 11
    types = [t.value for t in MemoryType]
    expected = [
        "episodic", "semantic", "procedural", "causal", "emotional",
        "corporeal", "social", "prospective", "counterfactual",
        "evolutionary", "cultural",
    ]
    for t in expected:
        assert t in types


def test_get_all_types():
    """get_all_types devuelve 11 tipos."""
    types = get_all_types()
    assert len(types) == 11


def test_get_type_description():
    """get_type_description devuelve descripción."""
    desc = get_type_description(MemoryType.EPISODIC)
    assert "eventos" in desc.lower() or "espacio" in desc.lower()


def test_entry_classes_complete():
    """ENTRY_CLASSES tiene 11 entradas."""
    assert len(ENTRY_CLASSES) == 11


def test_create_entry_episodic():
    """create_entry crea EpisodicEntry."""
    entry = create_entry(
        MemoryType.EPISODIC,
        content="test event",
        event_time=1000.0,
        location="vps_ceo",
        participants=["user_1"],
        outcome="success",
    )
    assert isinstance(entry, EpisodicEntry)
    assert entry.event_time == 1000.0
    assert entry.location == "vps_ceo"
    assert entry.outcome == "success"
    assert entry.type == "episodic"


def test_create_entry_semantic():
    """create_entry crea SemanticEntry."""
    entry = create_entry(
        MemoryType.SEMANTIC,
        content="concepto de causalidad",
        concept="causalidad",
        relations={"causes": ["efecto"]},
    )
    assert isinstance(entry, SemanticEntry)
    assert entry.concept == "causalidad"
    assert "causes" in entry.relations


def test_create_entry_procedural():
    """create_entry crea ProceduralEntry."""
    entry = create_entry(
        MemoryType.PROCEDURAL,
        content="cómo hacer X",
        procedure_name="do_x",
        steps=["step1", "step2"],
        success_rate=0.8,
    )
    assert isinstance(entry, ProceduralEntry)
    assert entry.procedure_name == "do_x"
    assert len(entry.steps) == 2
    assert entry.success_rate == 0.8


def test_create_entry_causal():
    """create_entry crea CausalEntry."""
    entry = create_entry(
        MemoryType.CAUSAL,
        content="X causa Y",
        cause="X",
        effect="Y",
        confidence=0.7,
        evidence_count=5,
    )
    assert isinstance(entry, CausalEntry)
    assert entry.cause == "X"
    assert entry.effect == "Y"
    assert entry.evidence_count == 5


def test_create_entry_emotional():
    """create_entry crea EmotionalEntry."""
    entry = create_entry(
        MemoryType.EMOTIONAL,
        content="evento sorprendente",
        marker_type="surprise",
        intensity=0.8,
        trigger="unexpected_input",
    )
    assert isinstance(entry, EmotionalEntry)
    assert entry.marker_type == "surprise"
    assert entry.intensity == 0.8


def test_create_entry_corporeal():
    """create_entry crea CorporealEntry."""
    entry = create_entry(
        MemoryType.CORPOREAL,
        content="sensor de filesystem activo",
        sensor_name="filesystem",
        sensor_state="active",
        capacity="detect_changes",
    )
    assert isinstance(entry, CorporealEntry)
    assert entry.sensor_name == "filesystem"
    assert entry.capacity == "detect_changes"


def test_create_entry_social():
    """create_entry crea SocialEntry."""
    entry = create_entry(
        MemoryType.SOCIAL,
        content="modelo de usuario X",
        agent_id="user_X",
        agent_type="human",
        traits={"patience": 0.7},
        trust_level=0.6,
    )
    assert isinstance(entry, SocialEntry)
    assert entry.agent_id == "user_X"
    assert entry.agent_type == "human"
    assert entry.traits["patience"] == 0.7


def test_create_entry_prospective():
    """create_entry crea ProspectiveEntry."""
    entry = create_entry(
        MemoryType.PROSPECTIVE,
        content="plan para mañana",
        intention_id="int_1",
        planned_action="explore_X",
        priority=0.8,
        status="pending",
    )
    assert isinstance(entry, ProspectiveEntry)
    assert entry.intention_id == "int_1"
    assert entry.planned_action == "explore_X"
    assert entry.status == "pending"


def test_create_entry_counterfactual():
    """create_entry crea CounterfactualEntry."""
    entry = create_entry(
        MemoryType.COUNTERFACTUAL,
        content="qué habría pasado si X",
        original_event="X happened",
        alternative_action="Y instead",
        predicted_outcome="different result",
    )
    assert isinstance(entry, CounterfactualEntry)
    assert entry.alternative_action == "Y instead"
    assert entry.predicted_outcome == "different result"


def test_create_entry_evolutionary():
    """create_entry crea EvolutionaryEntry."""
    entry = create_entry(
        MemoryType.EVOLUTIONARY,
        content="mutación arquitectural",
        mutation_id="mut_1",
        mutation_type="add_module",
        component_affected="speaker",
        success=True,
    )
    assert isinstance(entry, EvolutionaryEntry)
    assert entry.mutation_id == "mut_1"
    assert entry.success is True


def test_create_entry_cultural():
    """create_entry crea CulturalEntry."""
    entry = create_entry(
        MemoryType.CULTURAL,
        content="norma social",
        norm="ser_directo",
        context="spanish_culture",
        enforcement="soft",
    )
    assert isinstance(entry, CulturalEntry)
    assert entry.norm == "ser_directo"
    assert entry.enforcement == "soft"


def test_create_entry_with_base_fields():
    """create_entry pasa campos base correctamente."""
    entry = create_entry(
        MemoryType.EPISODIC,
        content="test",
        confidence=0.8,
        salience=0.7,
        provenance="test_source",
    )
    assert entry.confidence == 0.8
    assert entry.salience == 0.7
    assert entry.provenance == "test_source"


def test_memory_type_stats():
    """MemoryTypeStats cuenta correctamente."""
    stats = MemoryTypeStats()
    stats.increment(MemoryType.EPISODIC)
    stats.increment(MemoryType.EPISODIC)
    stats.increment(MemoryType.SEMANTIC)

    d = stats.to_dict()
    assert d["counts"]["episodic"] == 2
    assert d["counts"]["semantic"] == 1
    assert d["total"] == 3
    assert d["types_active"] == 2


def test_memory_type_stats_decrement():
    """MemoryTypeStats decrementa."""
    stats = MemoryTypeStats()
    stats.increment(MemoryType.EPISODIC)
    stats.decrement(MemoryType.EPISODIC)

    d = stats.to_dict()
    assert d["counts"]["episodic"] == 0
    assert d["total"] == 0


def test_all_entries_inherit_memory_entry():
    """Todas las entries especializadas heredan de MemoryEntry."""
    from zoe.core.living_memory import MemoryEntry

    for entry_class in ENTRY_CLASSES.values():
        assert issubclass(entry_class, MemoryEntry)
