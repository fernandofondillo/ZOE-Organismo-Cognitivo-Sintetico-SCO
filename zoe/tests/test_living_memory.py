"""Tests para LivingMemory (Fase 0.5)."""

import pytest
import time

from zoe.core.living_memory import LivingMemory, MemoryEntry


def test_memory_initial_state():
    """Memoria empieza vacía."""
    mem = LivingMemory()
    assert mem.count() == 0


def test_memory_add_basic():
    """add() añade entry."""
    mem = LivingMemory()
    entry_id = mem.add(
        content="test content",
        type="episodic",
        confidence=0.5,
        salience=0.5,
        provenance="test",
    )
    assert entry_id
    assert mem.count() == 1


def test_memory_add_requires_provenance():
    """add() sin provenance lo marca como unknown pero almacena."""
    mem = LivingMemory()
    entry_id = mem.add(content="test", type="episodic")
    entry = mem.get(entry_id)
    assert entry.provenance == "unknown"


def test_memory_get_updates_access():
    """get() actualiza last_access y access_count."""
    mem = LivingMemory()
    entry_id = mem.add(content="test", provenance="test")
    entry = mem.get(entry_id)
    initial_count = entry.access_count
    mem.get(entry_id)
    entry = mem.get(entry_id)
    assert entry.access_count > initial_count


def test_memory_search():
    """search() encuentra entries por similitud."""
    mem = LivingMemory()
    mem.add(content="el gato come pescado", provenance="test")
    mem.add(content="el perro come carne", provenance="test")
    mem.add(content="el coche es rojo", provenance="test")

    results = mem.search("gato come", n=2)
    assert len(results) >= 1
    assert "gato" in results[0].content


def test_memory_think_reorganize():
    """think() puede reorganizar entries episódicas accedidas mucho a semánticas."""
    mem = LivingMemory()
    entry_id = mem.add(content="test", type="episodic", provenance="test")
    # Acceder múltiples veces
    for _ in range(5):
        mem.get(entry_id)
    # Modificar timestamp para que parezca viejo
    mem._entries[entry_id].timestamp = time.time() - 4000  # >1h

    result = mem.think()
    entry = mem.get(entry_id)
    assert entry.type == "semantic"


def test_memory_think_merge():
    """think() fusiona entries similares."""
    mem = LivingMemory()
    mem.add(content="el gato come pescado en la cocina", provenance="test")
    mem.add(content="el gato come pescado en la cocina", provenance="test")
    mem.add(content="el gato come pescado en la cocina", provenance="test")

    initial_count = mem.count()
    # Forzar operación de merge directamente
    result = mem._merge_similar()
    # Debería haber fusionado (reducido count)
    assert mem.count() < initial_count


def test_memory_think_forget_low_salience():
    """forget_low_salience elimina entries de baja saliencia."""
    mem = LivingMemory(max_entries=5)
    # Añadir 10 entries de baja saliencia
    for i in range(10):
        mem.add(content=f"entry {i}", salience=0.1, confidence=0.1, provenance="test")

    # El max_entries debería haber disparado forget automático
    assert mem.count() <= 5


def test_memory_think_generalize():
    """think() puede generalizar patrones."""
    mem = LivingMemory()
    # Añadir entries con palabra común
    for i in range(5):
        mem.add(content=f"el gato hace algo {i}", provenance="test")

    result = mem.think()
    # Al menos una operación se ejecutó
    assert result["operation"]


def test_memory_think_detect_contradictions():
    """think() detecta contradicciones."""
    mem = LivingMemory()
    mem.add(content="el cielo es azul", provenance="test")
    mem.add(content="no el cielo es azul", provenance="test")

    # Forzar operación de detección
    result = mem._detect_contradictions()
    assert result["changes"] >= 1


def test_memory_get_stats():
    """get_stats() devuelve estadísticas."""
    mem = LivingMemory()
    mem.add(content="test1", type="episodic", provenance="test")
    mem.add(content="test2", type="semantic", provenance="test")

    stats = mem.get_stats()
    assert stats["total_entries"] == 2
    assert stats["type_counts"]["episodic"] == 1
    assert stats["type_counts"]["semantic"] == 1


def test_memory_to_dict():
    """to_dict() serializa correctamente."""
    mem = LivingMemory()
    mem.add(content="test", provenance="test")
    d = mem.to_dict()
    assert "entries" in d
    assert "stats" in d


def test_memory_operations_logged():
    """Las operaciones se loguean."""
    mem = LivingMemory()
    for i in range(5):
        mem.add(content=f"test {i}", provenance="test")

    mem.think()
    stats = mem.get_stats()
    assert stats["operations_count"] >= 1
