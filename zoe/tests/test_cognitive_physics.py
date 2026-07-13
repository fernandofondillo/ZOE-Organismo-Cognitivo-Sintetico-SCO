"""Tests para CognitivePhysics (Fase 0.5)."""

import pytest
import time

from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.state import InternalState
from zoe.core.cognitive_loop import Observation, Thought


def test_physics_initial_state():
    """Estado inicial correcto."""
    physics = CognitivePhysics()
    assert physics.energy_cognitive == 1.0
    assert physics.identity_inertia == 1.0
    assert physics.memory_elasticity == 1.0


def test_physics_update_basic():
    """update() calcula magnitudes básicas."""
    physics = CognitivePhysics()
    state = InternalState(energy=0.8, fatigue=0.2)
    obs = [Observation(timestamp=time.time(), source="clock", content="tick")]
    thoughts = [Thought(timestamp=time.time(), content="test", surprise=0.3, trigger="auto", subagent_source="Speaker")]

    result = physics.update(
        state=state,
        observations=obs,
        thoughts=thoughts,
        intentions=[],
        memory_concepts=["concepto1", "concepto2"],
        causal_relations=1,
        current_context="clock",
    )

    assert "energy_cognitive" in result
    assert "conceptual_mass" in result
    assert "semantic_entropy" in result
    assert result["energy_cognitive"] == 0.8
    assert result["conceptual_mass"] == 2.0


def test_physics_uncertainty_pressure_with_thoughts():
    """uncertainty_pressure se calcula con sorpresa de pensamientos."""
    physics = CognitivePhysics()
    state = InternalState()
    thoughts = [
        Thought(timestamp=time.time(), content="a", surprise=0.8, trigger="auto", subagent_source="S"),
        Thought(timestamp=time.time(), content="b", surprise=0.7, trigger="auto", subagent_source="S"),
    ]

    physics.update(
        state=state,
        observations=[],
        thoughts=thoughts,
        intentions=[],
        memory_concepts=[],
        current_context="test",
    )

    # Con sorpresa alta, uncertainty_pressure > 0
    assert physics.uncertainty_pressure > 0.0


def test_physics_creative_potential_increases_with_diversity():
    """creative_potential aumenta con pensamientos diversos."""
    physics = CognitivePhysics()
    state = InternalState()

    # Pensamientos muy diversos
    thoughts_diverse = [
        Thought(timestamp=time.time(), content=f"pensamiento único número {i}", surprise=0.3, trigger="auto", subagent_source="S")
        for i in range(5)
    ]

    physics.update(
        state=state,
        observations=[],
        thoughts=thoughts_diverse,
        intentions=[],
        memory_concepts=[],
        current_context="test",
    )

    assert physics.creative_potential > 0.3  # diversidad > 0.3


def test_physics_creative_potential_decreases_with_repetition():
    """creative_potential disminuye con pensamientos repetidos."""
    physics = CognitivePhysics()
    state = InternalState()

    # Pensamientos idénticos
    thoughts_same = [
        Thought(timestamp=time.time(), content="exactamente lo mismo", surprise=0.3, trigger="auto", subagent_source="S")
        for _ in range(5)
    ]

    physics.update(
        state=state,
        observations=[],
        thoughts=thoughts_same,
        intentions=[],
        memory_concepts=[],
        current_context="test",
    )

    assert physics.creative_potential < 0.3


def test_physics_goal_gravity_with_intentions():
    """goal_gravity aumenta con intenciones."""
    physics = CognitivePhysics()
    state = InternalState()

    intentions = ["int_1", "int_2", "int_3"]

    physics.update(
        state=state,
        observations=[],
        thoughts=[],
        intentions=intentions,
        memory_concepts=[],
        current_context="test",
    )

    assert physics.goal_gravity > 0.0


def test_physics_friction_increases_on_context_change():
    """cognitive_friction aumenta al cambiar de contexto."""
    physics = CognitivePhysics()
    state = InternalState()

    physics.update(state, [], [], [], [], current_context="A")
    initial_friction = physics.cognitive_friction

    physics.update(state, [], [], [], [], current_context="B")
    assert physics.cognitive_friction > initial_friction


def test_physics_friction_decreases_on_same_context():
    """cognitive_friction disminuye en mismo contexto."""
    physics = CognitivePhysics()
    state = InternalState()

    physics.update(state, [], [], [], [], current_context="A")
    physics.update(state, [], [], [], [], current_context="B")  # cambio
    friction_after_change = physics.cognitive_friction

    physics.update(state, [], [], [], [], current_context="B")  # mismo
    assert physics.cognitive_friction <= friction_after_change


def test_physics_memory_elasticity_depends_on_energy_fatigue():
    """memory_elasticity = energy * (1 - fatigue)."""
    physics = CognitivePhysics()
    state = InternalState(energy=0.8, fatigue=0.4)

    physics.update(state, [], [], [], [], current_context="test")
    assert abs(physics.memory_elasticity - (0.8 * 0.6)) < 0.01


def test_physics_should_rest():
    """should_rest() activa con energía baja."""
    physics = CognitivePhysics()
    physics.energy_cognitive = 0.1
    assert physics.should_rest() is True

    physics.energy_cognitive = 0.9
    assert physics.should_rest() is False


def test_physics_should_consolidate():
    """should_consolidate() activa con memoria elástica y masa."""
    physics = CognitivePhysics()
    physics.memory_elasticity = 0.8
    physics.conceptual_mass = 20
    physics.cognitive_temperature = 0.1
    assert physics.should_consolidate() is True


def test_physics_should_explore():
    """should_explore() activa con potencial creativo y energía."""
    physics = CognitivePhysics()
    physics.creative_potential = 0.7
    physics.energy_cognitive = 0.7
    physics.uncertainty_pressure = 0.3
    assert physics.should_explore() is True

    physics.uncertainty_pressure = 0.8
    assert physics.should_explore() is False


def test_physics_summary():
    """summary() devuelve string legible."""
    physics = CognitivePhysics()
    physics.energy_cognitive = 0.5
    physics.cognitive_temperature = 0.3
    physics.uncertainty_pressure = 0.4
    physics.creative_potential = 0.6
    physics.semantic_entropy = 0.5
    physics.identity_inertia = 0.9

    s = physics.summary()
    assert "eCog=0.50" in s
    assert "tCog=0.30" in s


def test_physics_to_dict():
    """to_dict() tiene todas las 12 magnitudes."""
    physics = CognitivePhysics()
    d = physics.to_dict()

    expected_keys = [
        "energy_cognitive",
        "conceptual_mass",
        "cognitive_temperature",
        "uncertainty_pressure",
        "creative_potential",
        "semantic_entropy",
        "goal_gravity",
        "identity_inertia",
        "conceptual_resonance",
        "cognitive_friction",
        "memory_elasticity",
        "causal_density",
    ]
    for key in expected_keys:
        assert key in d
