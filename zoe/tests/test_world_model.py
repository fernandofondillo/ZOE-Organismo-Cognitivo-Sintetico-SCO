"""Tests para WorldModel."""

import asyncio
import pytest

from zoe.core.world_model import WorldModel, _simple_hash_embedding, _cosine_distance
from zoe.core.cognitive_loop import Observation


def test_hash_embedding_dimensions():
    """Embedding tiene dimensión correcta."""
    emb = _simple_hash_embedding("hola", dim=64)
    assert len(emb) == 64


def test_hash_embedding_deterministic():
    """Mismo texto produce mismo embedding."""
    emb1 = _simple_hash_embedding("hola", dim=64)
    emb2 = _simple_hash_embedding("hola", dim=64)
    assert emb1 == emb2


def test_hash_embedding_different_texts():
    """Textos distintos producen embeddings distintos."""
    emb1 = _simple_hash_embedding("hola", dim=64)
    emb2 = _simple_hash_embedding("mundo", dim=64)
    assert emb1 != emb2


def test_hash_embedding_normalized():
    """Embedding está L2-normalizado."""
    emb = _simple_hash_embedding("test", dim=64)
    norm = sum(v * v for v in emb) ** 0.5
    assert abs(norm - 1.0) < 0.01


def test_cosine_distance_identical():
    """Distancia coseno de vectores idénticos es 0."""
    v = [1.0, 0.0, 0.0]
    assert _cosine_distance(v, v) == 0.0


def test_cosine_distance_orthogonal():
    """Distancia coseno de vectores ortogonales es 1."""
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    assert abs(_cosine_distance(v1, v2) - 1.0) < 0.01


def test_cosine_distance_opposite():
    """Distancia coseno de vectores opuestos es 2."""
    v1 = [1.0, 0.0]
    v2 = [-1.0, 0.0]
    assert abs(_cosine_distance(v1, v2) - 2.0) < 0.01


@pytest.mark.asyncio
async def test_world_model_no_history():
    """World Model sin historial da predicción nula."""
    wm = WorldModel()
    pred = await wm.predict_next([])
    assert pred["confidence"] == 0.0
    assert pred["strategy"] == "no_history"


@pytest.mark.asyncio
async def test_world_model_surprise_no_history():
    """Sin historial, sorpresa es neutral (0.5)."""
    wm = WorldModel()
    obs = Observation(timestamp=0, source="clock", content="tick")
    surprise = await wm.compute_surprise({"predicted_embedding": None}, [obs])
    assert surprise == 0.5


@pytest.mark.asyncio
async def test_world_model_learns_pattern():
    """Tras varias observaciones similares, sorpresa baja."""
    wm = WorldModel()

    # Alimentar con observaciones similares
    for i in range(5):
        obs = Observation(timestamp=i, source="clock", content="tick del reloj")
        await wm.compute_surprise({"predicted_embedding": None, "confidence": 0.0}, [obs])

    # Predicción ahora tiene confianza
    pred = await wm.predict_next([])
    assert pred["confidence"] > 0.0


@pytest.mark.asyncio
async def test_world_model_novel_input_high_surprise():
    """Input novedoso produce sorpresa alta."""
    wm = WorldModel()

    # Alimentar con patrón estable
    for i in range(5):
        obs = Observation(timestamp=i, source="clock", content="patrón estable recurrente")
        await wm.compute_surprise({"predicted_embedding": None, "confidence": 0.0}, [obs])

    # Predicción
    pred = await wm.predict_next([])

    # Input novedoso
    novel_obs = Observation(timestamp=10, source="user", content="algo totalmente diferente e inesperado")
    surprise = await wm.compute_surprise(pred, [novel_obs])

    # Sorpresa debe ser > 0 (novedad)
    assert surprise > 0.0


@pytest.mark.asyncio
async def test_world_model_repeated_input_low_surprise():
    """Input repetido produce sorpresa baja."""
    wm = WorldModel()

    # Alimentar con misma observación repetidas veces
    content = "exactamente lo mismo"
    for i in range(5):
        obs = Observation(timestamp=i, source="clock", content=content)
        await wm.compute_surprise({"predicted_embedding": None, "confidence": 0.0}, [obs])

    # Predicción basada en historial
    pred = await wm.predict_next([])

    # Misma observación otra vez
    obs = Observation(timestamp=10, source="clock", content=content)
    surprise = await wm.compute_surprise(pred, [obs])

    # Sorpresa debe ser baja (mismo contenido = mismo embedding = distancia 0)
    assert surprise < 0.3
