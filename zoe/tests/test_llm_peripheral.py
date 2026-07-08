"""Tests para LLM periférico."""

import asyncio
import pytest

from zoe.peripherals.llm import (
    LLMPeripheral,
    MockPeripheral,
    ZAIPeripheral,
    create_llm_peripheral,
)


def test_mock_peripheral_initialization():
    """MockPeripheral se inicializa correctamente."""
    mock = MockPeripheral()
    assert mock.name == "mock"


@pytest.mark.asyncio
async def test_mock_peripheral_generate():
    """MockPeripheral genera respuestas."""
    mock = MockPeripheral(responses=["Respuesta 1", "Respuesta 2"])
    r1 = await mock.generate("test prompt")
    r2 = await mock.generate("test prompt")
    assert r1 == "Respuesta 1"
    assert r2 == "Respuesta 2"


@pytest.mark.asyncio
async def test_mock_peripheral_cycles_responses():
    """MockPeripheral cicla respuestas."""
    mock = MockPeripheral(responses=["A", "B"])
    assert await mock.generate("p") == "A"
    assert await mock.generate("p") == "B"
    assert await mock.generate("p") == "A"


@pytest.mark.asyncio
async def test_mock_peripheral_health_check():
    """MockPeripheral pasa health check."""
    mock = MockPeripheral(responses=["OK"])
    assert await mock.health_check() is True


@pytest.mark.asyncio
async def test_zai_peripheral_initialization():
    """ZAIPeripheral se inicializa."""
    zai = ZAIPeripheral()
    assert zai.name == "zai"


@pytest.mark.asyncio
async def test_zai_peripheral_health_check():
    """ZAIPeripheral health check responde True o False (depende del entorno)."""
    zai = ZAIPeripheral()
    result = await zai.health_check()
    assert isinstance(result, bool)


def test_create_llm_peripheral_mock():
    """Factory crea MockPeripheral."""
    llm = create_llm_peripheral({"backend": "mock", "responses": ["test"]})
    assert isinstance(llm, MockPeripheral)


def test_create_llm_peripheral_zai():
    """Factory crea ZAIPeripheral."""
    llm = create_llm_peripheral({"backend": "zai"})
    assert isinstance(llm, ZAIPeripheral)


def test_create_llm_peripheral_unknown():
    """Factory lanza error para backend desconocido."""
    with pytest.raises(ValueError):
        create_llm_peripheral({"backend": "nonexistent"})
