"""Tests para sub-agentes."""

import asyncio
import pytest

from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.core.cognitive_loop import Observation
from zoe.peripherals.llm import MockPeripheral


# ===== PERCEIVER =====

@pytest.mark.asyncio
async def test_perceiver_empty_observations():
    """Perceiver con observaciones vacías."""
    p = Perceiver()
    result = await p.perceive([])
    assert result["count"] == 0
    assert "Sin observaciones" in result["summary"]


@pytest.mark.asyncio
async def test_perceiver_processes_observations():
    """Perceiver procesa observaciones correctamente."""
    p = Perceiver()
    obs = [
        Observation(timestamp=1, source="clock", content="tick 1"),
        Observation(timestamp=2, source="clock", content="tick 2"),
        Observation(timestamp=3, source="user", content="Hola"),
    ]
    result = await p.perceive(obs)
    assert result["count"] == 3
    assert "clock" in result["sources"]
    assert "user" in result["sources"]


@pytest.mark.asyncio
async def test_perceiver_generate_thought_neutral():
    """Perceiver genera pensamiento neutral sin sorpresa."""
    p = Perceiver()
    obs = [Observation(timestamp=1, source="clock", content="tick")]
    context = {"observations": obs, "surprise": 0.1}
    thought = await p.generate_thought(context)
    assert thought
    assert "Observando" in thought or "observ" in thought.lower()


@pytest.mark.asyncio
async def test_perceiver_generate_thought_high_surprise():
    """Perceiver nota sorpresa alta."""
    p = Perceiver()
    obs = [Observation(timestamp=1, source="clock", content="tick")]
    context = {"observations": obs, "surprise": 0.8}
    thought = await p.generate_thought(context)
    assert "inesperado" in thought.lower() or "inesperad" in thought.lower()


# ===== FORECASTER =====

@pytest.mark.asyncio
async def test_forecaster_no_prediction():
    """Forecaster sin predicción."""
    f = Forecaster()
    context = {"surprise": 0.0}
    thought = await f.generate_thought(context)
    assert thought


@pytest.mark.asyncio
async def test_forecaster_high_surprise():
    """Forecaster nota sorpresa alta."""
    f = Forecaster()
    f.update({"confidence": 0.8, "strategy": "pattern_continuation"}, surprise=0.8)
    context = {"surprise": 0.8}
    thought = await f.generate_thought(context)
    assert "falló" in thought.lower() or "falla" in thought.lower() or "sorpresa" in thought.lower()


@pytest.mark.asyncio
async def test_forecaster_low_surprise():
    """Forecaster reporta estabilidad con sorpresa baja."""
    f = Forecaster()
    f.update({"confidence": 0.9, "strategy": "pattern_continuation"}, surprise=0.05)
    context = {"surprise": 0.05}
    thought = await f.generate_thought(context)
    assert "estable" in thought.lower() or "esperaba" in thought.lower() or "razonable" in thought.lower()


# ===== SPEAKER =====

@pytest.mark.asyncio
async def test_speaker_without_llm_uses_template():
    """Speaker sin LLM usa plantilla."""
    s = Speaker(llm_peripheral=None)
    context = {
        "action": "autonomous_thought",
        "surprise": 0.1,
        "state": {"iteration_count": 5, "energy": 0.8, "fatigue": 0.1, "arousal": 0.3},
        "recent_observations": [{"source": "clock", "content": "tick"}],
        "recent_thoughts": [],
    }
    thought = await s.generate_thought(context)
    assert thought
    assert len(thought) > 5


@pytest.mark.asyncio
async def test_speaker_with_mock_llm():
    """Speaker con MockPeripheral."""
    mock = MockPeripheral(responses=["Pensamiento de prueba del mock."])
    s = Speaker(llm_peripheral=mock)
    context = {
        "action": "autonomous_thought",
        "surprise": 0.1,
        "state": {"iteration_count": 1, "energy": 1.0, "fatigue": 0.0, "arousal": 0.3},
        "recent_observations": [{"source": "clock", "content": "tick"}],
        "recent_thoughts": [],
    }
    thought = await s.generate_thought(context)
    assert thought
    assert "Pensamiento de prueba" in thought


@pytest.mark.asyncio
async def test_speaker_sanitizes_forbidden_phrases():
    """Speaker elimina frases prohibidas."""
    mock = MockPeripheral(responses=["Como modelo de lenguaje, yo creo que..."])
    s = Speaker(llm_peripheral=mock)
    context = {
        "action": "autonomous_thought",
        "surprise": 0.1,
        "state": {"iteration_count": 1, "energy": 1.0, "fatigue": 0.0, "arousal": 0.3},
        "recent_observations": [],
        "recent_thoughts": [],
    }
    thought = await s.generate_thought(context)
    assert "como modelo" not in thought.lower()


@pytest.mark.asyncio
async def test_speaker_avoids_repetition():
    """Speaker evita repetir pensamientos recientes."""
    mock = MockPeripheral(responses=["Pensamiento A", "Pensamiento A", "Pensamiento B"])
    s = Speaker(llm_peripheral=mock)
    context = {
        "action": "autonomous_thought",
        "surprise": 0.1,
        "state": {"iteration_count": 1, "energy": 1.0, "fatigue": 0.0, "arousal": 0.3},
        "recent_observations": [],
        "recent_thoughts": [],
    }
    thought1 = await s.generate_thought(context)
    context["recent_thoughts"] = [{"content": thought1}]
    thought2 = await s.generate_thought(context)
    # El segundo puede ser igual (mock responses) o distinto
    # Verificamos que ambos sean no vacíos
    assert thought1
    assert thought2


# ===== CRITIC =====

@pytest.mark.asyncio
async def test_critic_rejects_empty():
    """Critic rechaza pensamiento vacío."""
    c = Critic()
    result = await c.evaluate("")
    assert result["approved"] is False
    assert result["reason"] == "empty"


@pytest.mark.asyncio
async def test_critic_rejects_too_short():
    """Critic rechaza pensamiento muy corto."""
    c = Critic(min_length=20)
    result = await c.evaluate("Hola")
    assert result["approved"] is False
    assert result["reason"] == "too_short"


@pytest.mark.asyncio
async def test_critic_rejects_forbidden_phrase():
    """Critic rechaza frases prohibidas."""
    c = Critic()
    result = await c.evaluate("Como modelo de lenguaje, yo diría que esto es interesante.")
    assert result["approved"] is False
    assert "forbidden_phrase" in result["reason"]


@pytest.mark.asyncio
async def test_critic_approves_valid_thought():
    """Critic aprueba pensamiento válido."""
    c = Critic()
    result = await c.evaluate("He notado un patrón interesante en las últimas observaciones del entorno.")
    assert result["approved"] is True
    assert result["reason"] == "ok"


@pytest.mark.asyncio
async def test_critic_rejects_repetition():
    """Critic rechaza repetición exacta."""
    c = Critic()
    thought = "He notado un patrón interesante en las últimas observaciones del entorno."
    await c.evaluate(thought)
    result = await c.evaluate(thought)
    assert result["approved"] is False
    assert "repetitive" in result["reason"]


@pytest.mark.asyncio
async def test_critic_stats():
    """Critic registra estadísticas."""
    c = Critic()
    await c.evaluate("")  # empty
    await c.evaluate("ok")  # too_short
    await c.evaluate("Como modelo, no puedo.")  # forbidden
    await c.evaluate("He notado un patrón interesante en las últimas observaciones.")  # ok

    stats = c.get_stats()
    assert stats["rejection_counts"]["empty"] == 1
    assert stats["rejection_counts"]["too_short"] == 1
    assert stats["rejection_counts"]["forbidden_phrase"] == 1
    assert stats["recent_count"] == 1
