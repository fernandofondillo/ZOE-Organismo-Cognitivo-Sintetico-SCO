"""Tests para Fase 3.4-3.5 — Persistent Store + Ontogenetic V2 + Deep Consolidation."""

import asyncio
import os
import pytest
import tempfile
import time

from zoe.memory.persistent_store import PersistentMemoryStore, PersistentLivingMemory
from zoe.memory.deep_consolidation import DeepConsolidation
from zoe.alma.ontogenetic_motor_v2 import OntogeneticMotorV2, ARCHITECTURAL_MUTATION_TYPES
from zoe.alma.identity_vault import IdentityVault
from zoe.alma.trajectory_chain import TrajectoryChain
from zoe.core.living_memory import LivingMemory, MemoryEntry
from zoe.core.cognitive_laws import CognitiveLaws
from zoe.core.subagents.phase2_subagents import Creativity, ScientificEngine


# ===== PersistentMemoryStore =====


def test_persistent_store_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        assert store.count() == 0


def test_persistent_store_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))

        # Crear entry
        entry = MemoryEntry(
            id="test_1",
            type="episodic",
            content="test content",
            confidence=0.7,
            salience=0.6,
            provenance="test",
        )
        store.save_entry(entry)
        assert store.count() == 1

        # Cargar
        loaded = store.load_all()
        assert len(loaded) == 1
        assert loaded[0]["content"] == "test content"
        assert loaded[0]["confidence"] == 0.7


def test_persistent_store_save_all():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        mem.add(content="entry 1", provenance="test")
        mem.add(content="entry 2", provenance="test")

        count = store.save_all(mem._entries)
        assert count == 2
        assert store.count() == 2


def test_persistent_store_load_by_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        mem.add(content="episodic 1", type="episodic", provenance="test")
        mem.add(content="semantic 1", type="semantic", provenance="test")
        mem.add(content="episodic 2", type="episodic", provenance="test")

        store.save_all(mem._entries)
        episodic = store.load_by_type("episodic")
        semantic = store.load_by_type("semantic")
        assert len(episodic) == 2
        assert len(semantic) == 1


def test_persistent_store_delete():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        eid = mem.add(content="to delete", provenance="test")
        store.save_all(mem._entries)
        assert store.count() == 1

        store.delete_entry(eid)
        assert store.count() == 0


def test_persistent_store_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        mem.add(content="el gato come pescado", provenance="test")
        mem.add(content="el perro come carne", provenance="test")
        store.save_all(mem._entries)

        results = store.search("gato")
        assert len(results) == 1
        assert "gato" in results[0]["content"]


def test_persistent_store_clear():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        mem.add(content="test", provenance="test")
        store.save_all(mem._entries)
        assert store.count() == 1

        deleted = store.clear()
        assert deleted == 1
        assert store.count() == 0


def test_persistent_store_count_by_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PersistentMemoryStore(db_path=os.path.join(tmpdir, "test.db"))
        mem = LivingMemory()
        mem.add(content="e1", type="episodic", provenance="test")
        mem.add(content="e2", type="episodic", provenance="test")
        mem.add(content="s1", type="semantic", provenance="test")
        store.save_all(mem._entries)

        counts = store.count_by_type()
        assert counts["episodic"] == 2
        assert counts["semantic"] == 1


def test_persistent_living_memory_roundtrip():
    """PersistentLivingMemory guarda y carga entre sesiones."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        # Sesión 1: crear y guardar
        mem1 = LivingMemory()
        store1 = PersistentMemoryStore(db_path=db_path)
        persistent1 = PersistentLivingMemory(mem1, store1)
        mem1.add(content="memoria persistente", type="episodic", provenance="test")
        persistent1.save_to_disk()

        # Sesión 2: cargar en memoria nueva
        mem2 = LivingMemory()
        store2 = PersistentMemoryStore(db_path=db_path)
        persistent2 = PersistentLivingMemory(mem2, store2)
        loaded = persistent2.load_from_disk()

        assert loaded == 1
        assert mem2.count() == 1
        entries = mem2.all_entries()
        assert "memoria persistente" in entries[0].content


# ===== OntogeneticMotorV2 =====


def test_ontogenetic_v2_initialization():
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotorV2(identity_vault=vault, organism_id="test")
    assert len(motor._all_valid_types) > len(ARCHITECTURAL_MUTATION_TYPES)


def test_ontogenetic_v2_proposes_architectural():
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotorV2(identity_vault=vault, organism_id="test")

    mutation = motor.propose_mutation(
        type="add_subagent",
        target="society_of_mind",
        payload={"subagent_type": "creativity"},
        justification="need more creativity",
        provenance="test",
    )
    assert mutation.type == "add_subagent"


def test_ontogenetic_v2_rejects_unknown_type():
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotorV2(identity_vault=vault, organism_id="test")

    with pytest.raises(ValueError):
        motor.propose_mutation(
            type="invalid_architectural",
            target="test",
            payload={},
            justification="test",
        )


def test_ontogenetic_v2_add_subagent():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    class FakeOrganism:
        subagents = []
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="add_subagent",
        target="society_of_mind",
        payload={"subagent_type": "creativity"},
        justification="test add",
        provenance="test",
        cost=0.2,
        confidence=0.6,
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is True
    assert len(organism.subagents) == 1
    assert isinstance(organism.subagents[0], Creativity)


def test_ontogenetic_v2_remove_subagent():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    class FakeOrganism:
        subagents = [Creativity()]
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="remove_subagent",
        target="society_of_mind",
        payload={"subagent_name": "creativity"},
        justification="test remove",
        provenance="test",
        cost=0.1,
        confidence=0.7,
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is True
    assert len(organism.subagents) == 0


def test_ontogenetic_v2_cannot_remove_critical():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    class FakeOrganism:
        subagents = []
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="remove_subagent",
        target="society_of_mind",
        payload={"subagent_name": "speaker"},
        justification="test",
        provenance="test",
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is False
    assert "critical" in reason.lower()


def test_ontogenetic_v2_modify_threshold():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    from zoe.core.meta_cognition import MetaCognition

    class FakeOrganism:
        meta_cognition = MetaCognition()
        subagents = []
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="modify_threshold",
        target="meta_cognition",
        payload={"threshold": "confidence", "value": 0.6},
        justification="adjust for more deliberation",
        provenance="test",
        cost=0.1,
        confidence=0.8,
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is True
    assert organism.meta_cognition.confidence_threshold_system2 == 0.6


def test_ontogenetic_v2_adjust_workspace():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    from zoe.core.global_workspace import GlobalWorkspace

    class FakeOrganism:
        global_workspace = GlobalWorkspace()
        subagents = []
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="adjust_workspace_capacity",
        target="global_workspace",
        payload={"capacity": 5},
        justification="more parallel proposals",
        provenance="test",
        cost=0.2,
        confidence=0.7,
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is True
    assert organism.global_workspace.broadcast_capacity == 5


def test_ontogenetic_v2_adjust_metabolism():
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotorV2(
        identity_vault=vault, laws=laws, organism_id="test"
    )

    from zoe.metabolism.metabolism import Metabolism

    class FakeOrganism:
        metabolism = Metabolism()
        subagents = []
        memory = LivingMemory()

    organism = FakeOrganism()

    mutation = motor.propose_mutation(
        type="adjust_metabolism_threshold",
        target="metabolism",
        payload={"threshold": "sleep", "value": 0.7},
        justification="sleep earlier",
        provenance="test",
        cost=0.1,
        confidence=0.6,
    )

    success, reason = motor.apply_architectural_mutation(mutation, organism)
    assert success is True
    assert organism.metabolism.sleep_threshold == 0.7


def test_ontogenetic_v2_stats():
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotorV2(identity_vault=vault, organism_id="test")
    stats = motor.get_stats()
    assert "architectural_changes" in stats
    assert "architectural_types_available" in stats


# ===== DeepConsolidation =====


def test_deep_consolidation_initialization():
    dc = DeepConsolidation()
    assert dc._total_consolidations == 0


def test_deep_consolidation_insufficient_memory():
    dc = DeepConsolidation(memory=LivingMemory())
    result = dc.consolidate()
    assert result["total_operations"] == 0


def test_deep_consolidation_runs():
    mem = LivingMemory()
    for i in range(10):
        mem.add(content=f"entry {i}", type="episodic", provenance="test")
    dc = DeepConsolidation(memory=mem)
    result = dc.consolidate()
    assert "operations" in result
    assert "total_operations" in result


def test_deep_consolidation_episodic_to_semantic():
    mem = LivingMemory()
    mem.add(content="filler 1", provenance="test")
    mem.add(content="filler 2", provenance="test")
    entry_id = mem.add(content="frequently accessed", type="episodic", provenance="test")
    entry = mem.get(entry_id)
    entry.access_count = 5
    entry.timestamp = time.time() - 2000  # old

    dc = DeepConsolidation(memory=mem)
    result = dc.consolidate()
    assert result["operations"]["episodic_to_semantic"] >= 1

    entry = mem.get(entry_id)
    assert entry.type == "semantic"


def test_deep_consolidation_deep_forget():
    mem = LivingMemory()
    mem.add(content="filler", provenance="test")
    mem.add(content="irrelevant", type="episodic", salience=0.1, confidence=0.1, provenance="test")
    mem.add(content="important", type="episodic", salience=0.9, confidence=0.9, provenance="test")

    dc = DeepConsolidation(memory=mem)
    result = dc.consolidate()
    assert result["operations"]["deep_forgetting"] >= 1
    assert mem.count() >= 1  # the important one stays


def test_deep_consolidation_belief_reinforcement():
    mem = LivingMemory()
    mem.add(content="filler 1", provenance="test")
    mem.add(content="filler 2", provenance="test")
    entry_id = mem.add(
        content="important belief", type="semantic",
        salience=0.8, confidence=0.7, provenance="test"
    )
    entry = mem.get(entry_id)
    entry.access_count = 5

    dc = DeepConsolidation(memory=mem)
    result = dc.consolidate()
    assert result["operations"]["belief_reinforcement"] >= 1

    entry = mem.get(entry_id)
    assert entry.confidence > 0.7  # reinforced


def test_deep_consolidation_hypothesis_generation():
    mem = LivingMemory()
    for i in range(5):
        mem.add(content=f"entry {i}", provenance="test")

    se = ScientificEngine()
    se.propose_theory("test hypothesis", ["evidence"])

    dc = DeepConsolidation(memory=mem, scientific_engine=se)
    result = dc.consolidate()
    assert result["operations"]["hypothesis_generation"] >= 1


def test_deep_consolidation_contradiction_detection():
    mem = LivingMemory()
    mem.add(content="filler entry", provenance="test")
    mem.add(content="el cielo es azul", provenance="test")
    mem.add(content="no el cielo es azul", provenance="test")

    dc = DeepConsolidation(memory=mem)
    result = dc.consolidate()
    assert result["operations"]["contradiction_detection"] >= 1


def test_deep_consolidation_stats():
    mem = LivingMemory()
    for i in range(5):
        mem.add(content=f"entry {i}", provenance="test")
    dc = DeepConsolidation(memory=mem)
    dc.consolidate()
    stats = dc.get_stats()
    assert stats["total_consolidations"] == 1


def test_deep_consolidation_summary():
    dc = DeepConsolidation()
    s = dc.summary()
    assert "DeepConsolidation" in s
