"""Tests para CognitiveFields (Fase 0.5)."""

import pytest
import time

from zoe.core.cognitive_fields import CognitiveField, CognitiveFields


def test_field_initial_state():
    """Campo empieza vacío."""
    field = CognitiveField("test", "campo de prueba")
    assert field.read() == {}
    assert field.read_tension() == 0.0


def test_field_contribute_scalar():
    """Contribución escalar se almacena."""
    field = CognitiveField("test")
    field.contribute("Perceiver", 0.5)
    state = field.read()
    assert "value" in state
    assert state["value"] == 0.5


def test_field_contribute_dict():
    """Contribución dict se merge."""
    field = CognitiveField("test")
    field.contribute("Perceiver", {"sources": ["clock"], "count": 1})
    state = field.read()
    assert state["sources"] == ["clock"]
    assert state["count"] == 1


def test_field_contribute_multiple_aggregates():
    """Múltiples contribuciones numéricas se promedian."""
    field = CognitiveField("test")
    field.contribute("A", 0.4, weight=1.0)
    field.contribute("B", 0.6, weight=1.0)
    state = field.read()
    # (0.4 + 0.6) / 2 = 0.5
    assert abs(state["value"] - 0.5) < 0.01


def test_field_contribute_weighted():
    """Contribuciones con peso se promedian ponderadamente."""
    field = CognitiveField("test")
    field.contribute("A", 0.4, weight=1.0)
    field.contribute("B", 0.6, weight=3.0)
    state = field.read()
    # (0.4*1 + 0.6*3) / (1+3) = (0.4 + 1.8) / 4 = 0.55
    assert abs(state["value"] - 0.55) < 0.01


def test_field_tension_increases_with_multiple_contributors():
    """Tensión aumenta con contribuidores distintos."""
    field = CognitiveField("test")
    field.contribute("A", 0.5)
    assert field.read_tension() == 0.0  # solo 1 contribuidor

    field.contribute("B", 0.5)
    assert field.read_tension() > 0.0


def test_field_replace_mode():
    """replace=True sobreescribe el estado."""
    field = CognitiveField("test")
    field.contribute("A", {"x": 1, "y": 2})
    field.contribute("B", {"z": 3}, replace=True)
    state = field.read()
    assert "z" in state
    assert "x" not in state


def test_field_read_contributions():
    """read_contributions() devuelve historial."""
    field = CognitiveField("test")
    field.contribute("A", 0.5)
    field.contribute("B", 0.6)
    contributions = field.read_contributions()
    assert len(contributions) == 2
    assert contributions[0]["contributor"] == "A"
    assert contributions[1]["contributor"] == "B"


def test_fields_collection_initial():
    """CognitiveFields tiene los 6 campos."""
    fields = CognitiveFields()
    expected = ["attention", "emotional", "social", "creative", "causal", "ethical"]
    for name in expected:
        assert name in fields.fields


def test_fields_contribute_and_read():
    """Contribuir y leer de CognitiveFields."""
    fields = CognitiveFields()
    fields.contribute("attention", "Perceiver", {"sources": ["clock"]})
    state = fields.read("attention")
    assert state["sources"] == ["clock"]


def test_fields_read_all():
    """read_all() devuelve todos los campos."""
    fields = CognitiveFields()
    fields.contribute("emotional", "F", {"surprise": 0.5})
    all_states = fields.read_all()
    assert "attention" in all_states
    assert "emotional" in all_states
    assert all_states["emotional"]["surprise"] == 0.5


def test_fields_read_tensions():
    """read_tensions() devuelve tensiones de todos los campos."""
    fields = CognitiveFields()
    fields.contribute("attention", "A", 0.5)
    fields.contribute("attention", "B", 0.6)
    tensions = fields.read_tensions()
    assert "attention" in tensions
    assert tensions["attention"] > 0.0


def test_fields_total_tension():
    """total_tension() suma tensiones."""
    fields = CognitiveFields()
    fields.contribute("attention", "A", 0.5)
    fields.contribute("attention", "B", 0.6)
    fields.contribute("emotional", "A", 0.5)
    fields.contribute("emotional", "B", 0.6)
    total = fields.total_tension()
    assert total > 0.0


def test_fields_summary():
    """summary() devuelve string legible."""
    fields = CognitiveFields()
    s = fields.summary()
    assert "attention" in s
    assert "emotional" in s
    assert "ethical" in s
