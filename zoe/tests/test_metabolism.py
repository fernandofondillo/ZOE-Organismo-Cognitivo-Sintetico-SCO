"""Tests para Metabolism (Fase 1)."""

import pytest
import time

from zoe.metabolism.metabolism import Metabolism, MetabolicState
from zoe.core.state import InternalState


def test_metabolism_initial_state():
    """Metabolismo empieza despierto."""
    metab = Metabolism()
    assert metab.state == MetabolicState.AWAKE
    assert metab.energy == 1.0
    assert metab.fatigue == 0.0


def test_metabolism_transitions_to_drowsy():
    """Con fatiga alta, transita a drowsy."""
    metab = Metabolism()
    metab.internal_state.fatigue = 0.7
    metab.tick(dt=1.0)
    assert metab.state == MetabolicState.DROWSY


def test_metabolism_transitions_to_sleeping():
    """Con fatiga muy alta, transita a sleeping."""
    metab = Metabolism()
    metab.internal_state.fatigue = 0.9
    metab.tick(dt=1.0)
    assert metab.state == MetabolicState.SLEEPING
    assert metab.total_sleep_cycles == 1


def test_metabolism_wakes_up():
    """Tras dormir, despierta cuando energía recuperada."""
    metab = Metabolism()
    # Forzar sleep
    metab.internal_state.fatigue = 0.9
    metab.tick(dt=1.0)
    assert metab.state == MetabolicState.SLEEPING

    # Recuperar energía
    metab.internal_state.energy = 1.0
    metab.internal_state.fatigue = 0.1
    metab.tick(dt=1.0)
    # Debería despertar (pasa por WAKING primero, luego AWAKE)
    assert metab.state in [MetabolicState.WAKING, MetabolicState.AWAKE]


def test_metabolism_should_sleep_high_fatigue():
    """should_sleep() True con fatiga alta."""
    metab = Metabolism()
    metab.internal_state.fatigue = 0.85
    assert metab.should_sleep() is True


def test_metabolism_should_sleep_low_fatigue():
    """should_sleep() False con fatiga baja."""
    metab = Metabolism()
    metab.internal_state.fatigue = 0.3
    assert metab.should_sleep() is False


def test_metabolism_should_wake():
    """should_wake() True tras recuperar energía."""
    metab = Metabolism()
    metab.state = MetabolicState.SLEEPING
    metab.internal_state.energy = 0.9
    metab.internal_state.fatigue = 0.1
    assert metab.should_wake() is True


def test_metabolism_stimulate_wakes_up():
    """Estímulo fuerte despierta al organismo."""
    metab = Metabolism()
    metab.state = MetabolicState.SLEEPING
    metab.stimulate(intensity=0.8)
    assert metab.state != MetabolicState.SLEEPING


def test_metabolism_stimulate_low_doesnt_wake():
    """Estímulo bajo no despierta."""
    metab = Metabolism()
    metab.state = MetabolicState.SLEEPING
    metab.stimulate(intensity=0.3)
    assert metab.state == MetabolicState.SLEEPING


def test_metabolism_spend_compute():
    """spend_compute gasta del presupuesto."""
    metab = Metabolism()
    assert metab.spend_compute(0.3) is True
    assert metab.compute_spent == 0.3
    assert metab.spend_compute(0.8) is False  # excede presupuesto


def test_metabolism_reset_budget():
    """reset_budget reinicia el presupuesto."""
    metab = Metabolism()
    metab.spend_compute(0.5)
    metab.reset_budget()
    assert metab.compute_spent == 0.0


def test_metabolism_queue_consolidation():
    """queue_consolidation añade operación pendiente."""
    metab = Metabolism()
    metab.queue_consolidation("reorganize_episodic")
    assert len(metab.pending_consolidation) == 1


def test_metabolism_consolidates_during_sleep():
    """Consolida operaciones durante el sueño."""
    metab = Metabolism()
    metab.queue_consolidation("reorganize_episodic")
    metab.queue_consolidation("merge_semantic")

    # Forzar sleep
    metab.internal_state.fatigue = 0.9
    metab.tick(dt=1.0)  # transita a sleeping
    metab.tick(dt=1.0)  # consolida una operación

    assert metab.total_consolidation_operations >= 1


def test_metabolism_to_dict():
    """to_dict serializa correctamente."""
    metab = Metabolism()
    metab.internal_state.fatigue = 0.5
    d = metab.to_dict()
    assert "internal_state" in d
    assert "metabolic_state" in d
    assert d["metabolic_state"] == "awake"


def test_metabolism_summary():
    """summary() devuelve string legible."""
    metab = Metabolism()
    s = metab.summary()
    assert "Metabolism" in s
    assert "awake" in s


def test_metabolism_properties_delegate_to_internal_state():
    """Las properties delegan al InternalState."""
    metab = Metabolism()
    metab.internal_state.energy = 0.7
    metab.internal_state.fatigue = 0.3
    metab.internal_state.arousal = 0.5
    metab.internal_state.attention = 0.6

    assert metab.energy == 0.7
    assert metab.fatigue == 0.3
    assert metab.arousal == 0.5
    assert metab.attention == 0.6


def test_metabolism_iteration_count():
    """iteration_count delega al InternalState."""
    metab = Metabolism()
    metab.tick(dt=1.0)
    assert metab.iteration_count == 1
