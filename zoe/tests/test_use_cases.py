"""Tests para Use Case Runner — valida que los 6 casos de uso funcionan."""

import asyncio
import pytest
import os

from zoe.use_cases.run_use_case import (
    load_use_case_config, list_available_use_cases, run_use_case
)


USE_CASES = [
    "compania_personas_solas",
    "vigilancia_cognitiva",
    "cuidado_personas_mayores",
    "investigacion_autonoma",
    "federacion_b2b",
    "asistente_crece_contigo",
    "ia_heredable",
]


def test_list_use_cases():
    """Lista los 7 casos de uso disponibles."""
    cases = list_available_use_cases()
    assert len(cases) >= 6
    for uc in USE_CASES:
        assert uc in cases, f"Missing use case: {uc}"


@pytest.mark.parametrize("use_case_name", USE_CASES)
def test_load_use_case_config(use_case_name):
    """Cada caso de uso tiene YAML válido."""
    raw = load_use_case_config(use_case_name)
    # YAML tiene todo bajo 'use_case:' key
    config = raw.get("use_case", raw)
    assert "organism" in config or "name" in config
    assert "llm" in config
    assert "memory" in config
    uc = raw.get("use_case", {})
    assert uc["name"] == use_case_name
    assert uc["description"]


@pytest.mark.parametrize("use_case_name", USE_CASES[:3])
@pytest.mark.asyncio
async def test_run_use_case_short(use_case_name):
    """Cada caso de uso corre por 5s sin crashear (subset para tiempo)."""
    result = await run_use_case(
        use_case_name=use_case_name,
        backend_override="mock",
        duration=5.0,
        thoughts_target=2,
    )
    assert result["use_case"] == use_case_name
    assert result["iterations"] >= 1
    assert result["identity_hash"]
    assert result["chain_verified"] is True


@pytest.mark.asyncio
async def test_use_case_companion_specifics():
    """Caso de uso compañía tiene configuración específica."""
    raw = load_use_case_config("compania_personas_solas")
    config = raw.get("use_case", raw)
    companion = config.get("companion", {})
    assert companion.get("proactive_interval") == 3600
    assert companion.get("emotional_detection") is True
    assert companion.get("tone") == "warm_direct"


@pytest.mark.asyncio
async def test_use_case_sentinel_specifics():
    """Caso de uso vigilancia tiene configuración específica."""
    raw = load_use_case_config("vigilancia_cognitiva")
    config = raw.get("use_case", raw)
    sentinel = config.get("sentinel", {})
    assert sentinel.get("auto_investigate") is True
    assert sentinel.get("alert_threshold") == 0.7


def test_use_case_caretaker_specifics():
    """Caso de uso cuidado mayores tiene configuración específica."""
    raw = load_use_case_config("cuidado_personas_mayores")
    config = raw.get("use_case", raw)
    caretaker = config.get("caretaker", {})
    assert caretaker.get("routine_detection") is True
    assert caretaker.get("family_notification") is True
    assert "caída" in caretaker.get("emergency_keywords", [])


def test_use_case_researcher_specifics():
    """Caso de uso investigación tiene configuración específica."""
    raw = load_use_case_config("investigacion_autonoma")
    config = raw.get("use_case", raw)
    researcher = config.get("researcher", {})
    assert researcher.get("hypothesis_generation") is True
    assert researcher.get("experiment_design") is True


def test_use_case_federation_b2b_specifics():
    """Caso de uso federación B2B tiene configuración específica."""
    raw = load_use_case_config("federacion_b2b")
    config = raw.get("use_case", raw)
    enterprise = config.get("enterprise", {})
    assert enterprise.get("data_privacy") == "strict"
    assert enterprise.get("shared_mutations_only") is True


def test_use_case_personal_specifics():
    """Caso de uso asistente personal tiene configuración específica."""
    raw = load_use_case_config("asistente_crece_contigo")
    config = raw.get("use_case", raw)
    personal = config.get("personal", {})
    assert personal.get("user_modeling") is True
    assert personal.get("long_term_memory") is True


def test_use_case_legacy_specifics():
    """Caso de uso IA heredable tiene configuración específica."""
    raw = load_use_case_config("ia_heredable")
    config = raw.get("use_case", raw)
    legacy = config.get("legacy", {})
    assert legacy.get("transferable") is True
    assert legacy.get("trajectory_export") is True
    assert legacy.get("inheritance_protocol") == "signed_handover"


def test_use_cases_have_different_tick_intervals():
    """Cada caso de uso tiene tick_interval distinto según su naturaleza."""
    intervals = {}
    for uc in USE_CASES:
        raw = load_use_case_config(uc)
        config = raw.get("use_case", raw)
        intervals[uc] = config.get("organism", {}).get("tick_interval", 5.0)
    # Vigilancia debe ser más rápida que cuidado de mayores
    assert intervals["vigilancia_cognitiva"] < intervals["cuidado_personas_mayores"]


def test_use_cases_have_different_metabolism():
    """Cada caso de uso tiene umbrales de metabolismo distintos."""
    for uc in USE_CASES:
        raw = load_use_case_config(uc)
        config = raw.get("use_case", raw)
        met = config.get("metabolism", {})
        assert "drowsy_threshold" in met
        assert "sleep_threshold" in met
        assert "wake_threshold" in met
