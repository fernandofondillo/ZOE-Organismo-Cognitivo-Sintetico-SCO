"""Tests para CLI Chat interface."""

import asyncio
import pytest
import tempfile
import os

from zoe.cli_chat import ZoeChat


@pytest.fixture
async def chat():
    """Crea una instancia de ZoeChat inicializada."""
    db_path = tempfile.mktemp(suffix=".db")
    c = ZoeChat(backend="mock", db_path=db_path)
    await c.initialize()
    yield c
    await c.shutdown()


@pytest.mark.asyncio
async def test_chat_initializes(chat):
    """El chat se inicializa correctamente."""
    assert chat._initialized is True
    assert chat.vault is not None
    assert chat.memory is not None
    assert chat.loop is not None


@pytest.mark.asyncio
async def test_chat_send_message(chat):
    """El chat responde a un mensaje."""
    response = await chat.send_message("Hola Zoe")
    assert response
    assert len(response) > 5


@pytest.mark.asyncio
async def test_chat_get_stats(chat):
    """get_stats devuelve estadísticas formateadas."""
    stats = chat.get_stats()
    assert "ESTADÍSTICAS" in stats
    assert "Iteraciones" in stats


@pytest.mark.asyncio
async def test_chat_get_memory(chat):
    """get_memory devuelve memoria formateada."""
    mem = chat.get_memory()
    assert "MEMORIA" in mem or "entries" in mem


@pytest.mark.asyncio
async def test_chat_get_state(chat):
    """get_state devuelve estado interno."""
    state = chat.get_state()
    assert "ESTADO" in state
    assert "Energía" in state


@pytest.mark.asyncio
async def test_chat_get_identity(chat):
    """get_identity devuelve identidad."""
    identity = chat.get_identity()
    assert "IDENTIDAD" in identity
    assert "Hash" in identity


@pytest.mark.asyncio
async def test_chat_feed_document(chat):
    """feed_document almacena documento en memoria."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Este es un documento de prueba para alimentar a ZOE.")
        f.flush()
        filepath = f.name

    try:
        result = chat.feed_document(filepath)
        assert "almacenado" in result.lower() or "leído" in result.lower()
    finally:
        os.unlink(filepath)


@pytest.mark.asyncio
async def test_chat_feed_nonexistent(chat):
    """feed_document con archivo inexistente devuelve error."""
    result = chat.feed_document("/nonexistent/file.txt")
    assert "no encontrado" in result.lower() or "error" in result.lower()


@pytest.mark.asyncio
async def test_chat_shutdown_saves(chat):
    """shutdown guarda memoria."""
    await chat.shutdown()
    # Verificar que el DB tiene entries
    from zoe.memory.persistent_store import PersistentMemoryStore
    store = PersistentMemoryStore(db_path=chat.db_path)
    assert store.count() >= 1
