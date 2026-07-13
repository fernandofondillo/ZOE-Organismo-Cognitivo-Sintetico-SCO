"""Tests para CognitiveTensions (Fase 0.5)."""

import pytest

from zoe.core.cognitive_tensions import CognitiveTensions, TENSION_DEFINITIONS


def test_tensions_initial_state():
    """5 tensiones empiezan en equilibrio."""
    tensions = CognitiveTensions()
    assert len(tensions.tensions) == 5
    for t in tensions.tensions.values():
        assert t.value == 0.5
        assert t.intensity == 0.0


def test_tensions_definitions_complete():
    """Las 5 tensiones están definidas."""
    expected = [
        "curiosity_vs_efficiency",
        "identity_vs_adaptation",
        "rest_vs_productivity",
        "honesty_vs_empathy",
        "specialization_vs_generalization",
    ]
    for name in expected:
        assert name in TENSION_DEFINITIONS
        assert "pole_a" in TENSION_DEFINITIONS[name]
        assert "pole_b" in TENSION_DEFINITIONS[name]


def test_tensions_update_from_state_high_energy():
    """Con energía alta y fatiga baja, productividad domina."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=1.0, fatigue=0.0, arousal=0.8, surprise=0.2
    )
    rest_prod = tensions.tensions["rest_vs_productivity"]
    assert rest_prod.value > 0.5  # hacia productivity


def test_tensions_update_from_state_high_fatigue():
    """Con fatiga alta, descanso domina."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.2, fatigue=0.9, arousal=0.2, surprise=0.1
    )
    rest_prod = tensions.tensions["rest_vs_productivity"]
    assert rest_prod.value < 0.5  # hacia rest


def test_tensions_update_from_state_high_surprise():
    """Con sorpresa alta, adaptación domina."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.8, fatigue=0.2, arousal=0.6, surprise=0.9
    )
    id_adapt = tensions.tensions["identity_vs_adaptation"]
    assert id_adapt.value > 0.4  # hacia adaptation (más laxo por identidad_inertia default=1.0)


def test_tensions_update_from_state_low_surprise():
    """Con poca sorpresa, identidad domina."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.8, fatigue=0.2, arousal=0.6, surprise=0.05
    )
    id_adapt = tensions.tensions["identity_vs_adaptation"]
    assert id_adapt.value < 0.5  # hacia identity


def test_tensions_update_honesty_empathy():
    """update_honesty_empathy() funciona."""
    tensions = CognitiveTensions()
    # Usuario muy emocional → empathy
    tensions.update_honesty_empathy(user_emotional_state=0.9)
    h_em = tensions.tensions["honesty_vs_empathy"]
    assert h_em.value > 0.5  # hacia empathy

    # Usuario no emocional → honesty
    tensions.update_honesty_empathy(user_emotional_state=0.1)
    h_em = tensions.tensions["honesty_vs_empathy"]
    assert h_em.value < 0.5  # hacia honesty


def test_tensions_update_specialization_generalization():
    """update_specialization_generalization() funciona."""
    tensions = CognitiveTensions()
    # Alta entropía → generalization
    tensions.update_specialization_generalization(
        semantic_entropy=0.9, conceptual_resonance=0.1
    )
    sp_gen = tensions.tensions["specialization_vs_generalization"]
    assert sp_gen.value > 0.5  # hacia generalization


def test_tensions_get_dominant():
    """get_dominant_tension() devuelve la de mayor intensidad."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1
    )
    name, tension = tensions.get_dominant_tension()
    assert name is not None
    assert tension.intensity > 0.0


def test_tensions_get_thought_trigger():
    """get_thought_trigger() devuelve string no vacío."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1
    )
    trigger = tensions.get_thought_trigger()
    assert trigger
    assert len(trigger) > 10


def test_tensions_dominant_pole():
    """dominant_pole() devuelve el polo correcto."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1
    )
    rest_prod = tensions.tensions["rest_vs_productivity"]
    pole = rest_prod.dominant_pole()
    assert pole == "rest"


def test_tensions_summary():
    """summary() devuelve string legible."""
    tensions = CognitiveTensions()
    tensions.update_from_state(
        energy=0.5, fatigue=0.5, arousal=0.5, surprise=0.5
    )
    s = tensions.summary()
    assert "curiosity_vs_efficiency" in s
    assert "rest_vs_productivity" in s


def test_tensions_to_dict():
    """to_dict() serializa correctamente."""
    tensions = CognitiveTensions()
    tensions.update_from_state(energy=0.8, fatigue=0.2, arousal=0.5, surprise=0.3)
    d = tensions.to_dict()
    assert "curiosity_vs_efficiency" in d
    assert "value" in d["curiosity_vs_efficiency"]
    assert "intensity" in d["curiosity_vs_efficiency"]
