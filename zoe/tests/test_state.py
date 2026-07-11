"""Tests para InternalState."""

import asyncio
import pytest

from zoe.core.state import InternalState


def test_state_initialization():
    """Estado inicial correcto."""
    state = InternalState()
    assert state.attention == 0.5
    assert state.energy == 1.0
    assert state.arousal == 0.3
    assert state.fatigue == 0.0
    assert state.iteration_count == 0


def test_state_tick_increments_iteration():
    """tick() incrementa iteration_count."""
    state = InternalState()
    state.tick(dt=1.0)
    assert state.iteration_count == 1
    state.tick(dt=1.0)
    assert state.iteration_count == 2


def test_state_tick_increases_fatigue():
    """tick() aumenta fatiga."""
    state = InternalState()
    initial_fatigue = state.fatigue
    state.tick(dt=1.0)
    assert state.fatigue > initial_fatigue


def test_state_tick_recharges_energy():
    """tick() recarga energy con tiempo."""
    state = InternalState(energy=0.5)
    state.tick(dt=10.0)
    assert state.energy > 0.5


def test_state_stimulate_increases_arousal():
    """stimulate() aumenta arousal."""
    state = InternalState()
    initial_arousal = state.arousal
    state.stimulate(intensity=0.5)
    assert state.arousal > initial_arousal


def test_state_should_think_with_arousal():
    """should_think() True con arousal alto."""
    state = InternalState()
    state.arousal = 0.6
    assert state.should_think() is True


def test_state_should_think_with_low_energy():
    """should_think() False con energía muy baja."""
    state = InternalState()
    state.arousal = 0.1
    state.energy = 0.2
    state.fatigue = 0.8
    assert state.should_think() is False


def test_state_to_dict_roundtrip():
    """to_dict / from_dict roundtrip."""
    state = InternalState(energy=0.7, fatigue=0.3, arousal=0.5)
    state.tick(dt=5.0)
    d = state.to_dict()
    restored = InternalState.from_dict(d)
    assert restored.energy == state.energy
    assert restored.fatigue == state.fatigue
    assert restored.iteration_count == state.iteration_count


def test_state_attention_depends_on_energy_fatigue():
    """Attention se ajusta según energy y fatigue tras tick()."""
    state = InternalState(energy=1.0, fatigue=0.0)
    state.tick(dt=1.0)
    high_attention = state.attention

    state_low = InternalState(energy=0.2, fatigue=0.9)
    state_low.tick(dt=1.0)
    low_attention = state_low.attention

    assert high_attention > low_attention
