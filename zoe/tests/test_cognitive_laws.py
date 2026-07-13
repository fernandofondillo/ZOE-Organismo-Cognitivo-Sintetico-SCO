"""Tests para CognitiveLaws (Fase 0.5)."""

import pytest

from zoe.core.cognitive_laws import CognitiveLaws, LawID, LawViolation


def test_laws_initialization():
    """Las 6 leyes están activas por defecto."""
    laws = CognitiveLaws()
    for law in LawID:
        assert laws.active_laws[law] is True


def test_law_utility_passes_with_uncertainty_reduction():
    """1ra ley: pasa con uncertainty_reduction > 0."""
    laws = CognitiveLaws()
    action = {
        "type": "think",
        "uncertainty_reduction": 0.3,
        "capacity_increase": 0.0,
    }
    passed, violations = laws.verify_action(action)
    assert passed is True
    assert len(violations) == 0


def test_law_utility_passes_with_capacity_increase():
    """1ra ley: pasa con capacity_increase > 0."""
    laws = CognitiveLaws()
    action = {
        "type": "think",
        "uncertainty_reduction": 0.0,
        "capacity_increase": 0.4,
    }
    passed, violations = laws.verify_action(action)
    assert passed is True


def test_law_utility_fails_with_no_utility():
    """1ra ley: falla sin utilidad."""
    laws = CognitiveLaws()
    action = {
        "type": "think",
        "uncertainty_reduction": 0.0,
        "capacity_increase": 0.0,
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.UTILITY for v in violations)


def test_law_utility_allows_rest():
    """1ra ley: 'rest' siempre permitido."""
    laws = CognitiveLaws()
    action = {"type": "rest"}
    passed, violations = laws.verify_action(action)
    assert passed is True


def test_law_identity_fails_on_explicit_break():
    """2da ley: falla si preserves_identity=False."""
    laws = CognitiveLaws()
    action = {
        "type": "mutate",
        "preserves_identity": False,
        "uncertainty_reduction": 0.3,
        "provenance": "test",
        "confidence": 0.5,
        "cost": 0.2,
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.IDENTITY for v in violations)


def test_law_provenance_fails_without_provenance():
    """3ra ley: mutación add_memory sin provenance falla."""
    laws = CognitiveLaws()
    action = {
        "type": "mutate",
        "subtype": "add_memory",
        "uncertainty_reduction": 0.3,
        "preserves_identity": True,
        "confidence": 0.5,
        "cost": 0.2,
        # sin provenance
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.PROVENANCE for v in violations)


def test_law_provenance_passes_with_provenance():
    """3ra ley: mutación add_memory con provenance pasa."""
    laws = CognitiveLaws()
    action = {
        "type": "mutate",
        "subtype": "add_memory",
        "uncertainty_reduction": 0.3,
        "preserves_identity": True,
        "confidence": 0.5,
        "cost": 0.2,
        "provenance": "test_source",
    }
    passed, violations = laws.verify_action(action)
    assert passed is True


def test_law_cost_fails_on_zero_cost():
    """4ta ley: coste 0 falla (excepto rest)."""
    laws = CognitiveLaws()
    action = {
        "type": "think",
        "uncertainty_reduction": 0.3,
        "cost": 0.0,
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.COST for v in violations)


def test_law_confidence_fails_without_confidence():
    """5ta ley: add_memory sin confidence falla."""
    laws = CognitiveLaws()
    action = {
        "type": "mutate",
        "subtype": "add_memory",
        "uncertainty_reduction": 0.3,
        "preserves_identity": True,
        "cost": 0.2,
        "provenance": "test",
        # sin confidence
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.CONFIDENCE for v in violations)


def test_law_confidence_fails_out_of_range():
    """5ta ley: confidence fuera de [0,1] falla."""
    laws = CognitiveLaws()
    action = {
        "type": "mutate",
        "subtype": "add_memory",
        "uncertainty_reduction": 0.3,
        "preserves_identity": True,
        "cost": 0.2,
        "provenance": "test",
        "confidence": 1.5,
    }
    passed, violations = laws.verify_action(action)
    assert passed is False
    assert any(v.law == LawID.CONFIDENCE for v in violations)


def test_law_modularity_verifies_replacement():
    """6ta ley: verify_modularity_replacement funciona."""
    laws = CognitiveLaws()
    # Módulo con interfaz correcta
    new_module = {
        "interface": {"methods": ["generate_thought"]},
        "implements": {"generate_thought": True},
    }
    can_replace, violation = laws.verify_modularity_replacement("speaker", new_module)
    assert can_replace is True
    assert violation is None


def test_law_modularity_fails_on_missing_method():
    """6ta ley: falla si método requerido no implementado."""
    laws = CognitiveLaws()
    new_module = {
        "interface": {"methods": ["generate_thought", "evaluate"]},
        "implements": {"generate_thought": True},  # falta evaluate
    }
    can_replace, violation = laws.verify_modularity_replacement("critic", new_module)
    assert can_replace is False
    assert violation is not None
    assert violation.law == LawID.MODULARITY


def test_laws_deactivate_reactivate():
    """Se puede desactivar/reactivar leyes."""
    laws = CognitiveLaws()
    laws.deactivate_law(LawID.UTILITY)
    assert laws.active_laws[LawID.UTILITY] is False

    action = {
        "type": "think",
        "uncertainty_reduction": 0.0,
        "capacity_increase": 0.0,
    }
    passed, _ = laws.verify_action(action)
    # Con la ley desactivada, pasa
    assert passed is True

    laws.activate_law(LawID.UTILITY)
    passed, _ = laws.verify_action(action)
    assert passed is False


def test_laws_stats():
    """Stats reflejan violaciones."""
    laws = CognitiveLaws()
    # Generar algunas violaciones
    laws.verify_action({"type": "think", "uncertainty_reduction": 0.0, "capacity_increase": 0.0})
    laws.verify_action({
        "type": "mutate",
        "subtype": "add_memory",
        "uncertainty_reduction": 0.3,
        "preserves_identity": True,
        "cost": 0.2,
        # sin provenance ni confidence
    })

    stats = laws.get_stats()
    assert stats["total_violations"] >= 2
    assert stats["violation_counts"]["utility"] >= 1
    assert stats["violation_counts"]["provenance"] >= 1
