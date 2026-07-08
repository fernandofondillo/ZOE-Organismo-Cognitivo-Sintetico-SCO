"""
Tests Fase 6A Punto 3 — Curator + DeepConsolidation + Critic + Quarantine

Verifica que la integración de KnowledgeQuarantine en los componentes
de consolidación y validación funciona correctamente.
"""

import asyncio
import pytest
import time

from zoe.core.knowledge_quarantine import KnowledgeQuarantine
from zoe.core.subagents.phase2_subagents import Curator, Learner
from zoe.core.subagents.critic import Critic
from zoe.memory.deep_consolidation import DeepConsolidation
from zoe.core.living_memory import LivingMemory
from zoe.core.epistemic_validator import EpistemicValidator


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def memory_with_entries():
    """Memoria con entries de prueba."""
    mem = LivingMemory(max_entries=100)
    # Añadir entries de diferentes tipos
    mem.add(content="Hecho verificado importante", type="semantic", confidence=0.9, salience=0.8)
    mem.add(content="Hecho en cuarentena", type="semantic", confidence=0.5, salience=0.4, provenance="llm:gpt-4o")
    mem.add(content="Evento episódico frecuente", type="episodic", confidence=0.7, salience=0.6)
    mem.add(content="Evento poco relevante", type="episodic", confidence=0.2, salience=0.1)
    mem.add(content="Otro evento", type="episodic", confidence=0.6, salience=0.5)
    return mem


@pytest.fixture
def quarantine_with_entry(memory_with_entries):
    """Quarantine con una entry marcada."""
    q = KnowledgeQuarantine(default_timeout_days=30)
    # Marcar la segunda entry (índice 1) como en cuarentena
    entries = memory_with_entries.all_entries()
    if len(entries) >= 2:
        mem_id = entries[1].id
        q.add(
            entry_id=f"q_{mem_id}",
            claim="Hecho en cuarentena",
            source="llm:gpt-4o",
            confidence=0.5,
            domain="medical",
            reason="accepted_with_quarantine",
            verification_plan={"required_verifications": 2, "timeout_days": 30},
            memory_entry_id=mem_id,
        )
    return q


# ============================================================
# 1. Curator + Quarantine
# ============================================================

class TestCuratorQuarantine:

    @pytest.mark.asyncio
    async def test_curator_get_safe_entries_non_critical(self, memory_with_entries, quarantine_with_entry):
        """Sin critical_context, devuelve todas las entries (incluidas cuarentena)."""
        curator = Curator(memory=memory_with_entries, quarantine=quarantine_with_entry)
        safe = curator.get_safe_entries(n=10, critical_context=False)
        # Debe devolver 5 entries (sin filtrar)
        assert len(safe) == 5

    @pytest.mark.asyncio
    async def test_curator_get_safe_entries_critical_filters_quarantine(self, memory_with_entries, quarantine_with_entry):
        """Con critical_context=True, filtra las entries en cuarentena."""
        curator = Curator(memory=memory_with_entries, quarantine=quarantine_with_entry)
        safe = curator.get_safe_entries(n=10, critical_context=True)
        # Debe devolver 4 entries (1 cuarentena filtrada)
        assert len(safe) == 4
        # Verificar que la entry en cuarentena no está
        for e in safe:
            assert e["content"] != "Hecho en cuarentena"

    @pytest.mark.asyncio
    async def test_curator_stats_track_filtered(self, memory_with_entries, quarantine_with_entry):
        """Las stats del Curator registran entries filtradas."""
        curator = Curator(memory=memory_with_entries, quarantine=quarantine_with_entry)
        curator.get_safe_entries(n=10, critical_context=True)
        stats = curator.get_stats()
        assert stats["quarantine_filtered"] >= 1
        assert stats["quarantine_active"] is True

    @pytest.mark.asyncio
    async def test_curator_without_quarantine_compat(self, memory_with_entries):
        """Curator sin quarantine funciona como antes."""
        curator = Curator(memory=memory_with_entries)
        safe = curator.get_safe_entries(n=10, critical_context=True)
        # Sin quarantine, no filtra nada
        assert len(safe) == 5
        stats = curator.get_stats()
        assert stats["quarantine_active"] is False

    @pytest.mark.asyncio
    async def test_curator_curate_cleans_expired(self, memory_with_entries):
        """Curator.curate() limpia entries expiradas del quarantine."""
        q = KnowledgeQuarantine(default_timeout_days=1)
        # Añadir entry y forzar expiración
        entries = memory_with_entries.all_entries()
        mem_id = entries[1].id
        q.add(
            entry_id=f"q_{mem_id}",
            claim="test",
            source="llm",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id=mem_id,
        )
        # Forzar expiración
        q._entries[f"q_{mem_id}"].expires_at = time.time() - 1
        
        curator = Curator(memory=memory_with_entries, quarantine=q)
        # memory.think() necesita suficiente contenido
        result = await curator.curate()
        
        # Verificar que cleanup_expired fue llamado
        q_stats = q.get_stats()
        assert q_stats["expired"] >= 1


# ============================================================
# 2. DeepConsolidation + Quarantine
# ============================================================

class TestDeepConsolidationQuarantine:

    def test_episodic_to_semantic_skips_quarantine(self):
        """_episodic_to_semantic NO promueve entries en cuarentena."""
        mem = LivingMemory(max_entries=100)
        # Añadir entries episódicas
        e1 = mem.add(content="Evento 1", type="episodic", confidence=0.7, salience=0.6)
        e2 = mem.add(content="Evento 2", type="episodic", confidence=0.7, salience=0.6)
        
        # Simular access_count alto (necesario para promoción)
        entries = mem.all_entries()
        for e in entries:
            e.access_count = 5
            e.timestamp = time.time() - 7200  # 2h old
        
        # Configurar quarantine marcando la primera entry
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id=entries[0].id,
        )
        
        dc = DeepConsolidation(memory=mem, quarantine=q)
        promoted = dc._episodic_to_semantic()
        
        # Solo debe promover 1 (la no-cuarentena)
        assert promoted == 1
        # Verificar que la entry en cuarentena sigue siendo episódica
        assert entries[0].type == "episodic"
        assert entries[1].type == "semantic"

    def test_reinforce_beliefs_skips_quarantine(self):
        """_reinforce_beliefs NO refuerza entries en cuarentena."""
        mem = LivingMemory(max_entries=100)
        mem.add(content="Hecho 1", type="semantic", confidence=0.7, salience=0.8)
        mem.add(content="Hecho 2", type="semantic", confidence=0.7, salience=0.8)
        
        entries = mem.all_entries()
        for e in entries:
            e.access_count = 5
        
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id=entries[0].id,
        )
        
        dc = DeepConsolidation(memory=mem, quarantine=q)
        reinforced = dc._reinforce_beliefs()
        
        # Solo 1 reforzada (la no-cuarentena)
        assert reinforced == 1
        # La entry en cuarentena no cambió
        assert entries[0].confidence == 0.7
        assert entries[1].confidence == 0.75  # +0.05

    def test_deep_forget_prunes_expired_quarantine(self):
        """_deep_forget poda entries de cuarentena expiradas."""
        mem = LivingMemory(max_entries=100)
        mem.add(content="Hecho normal", type="semantic", confidence=0.9, salience=0.8)
        mem.add(content="Hecho en cuarentena expirada", type="semantic", confidence=0.5, salience=0.4)
        
        entries = mem.all_entries()
        assert len(entries) == 2
        
        q = KnowledgeQuarantine(default_timeout_days=1)
        q.add(
            entry_id="q_expired",
            claim="test",
            source="llm",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id=entries[1].id,
        )
        # Forzar expiración
        q._entries["q_expired"].expires_at = time.time() - 1
        q._entries["q_expired"].status = "expired"
        
        dc = DeepConsolidation(memory=mem, quarantine=q)
        forgotten = dc._deep_forget()
        
        assert forgotten >= 1
        # La entry expirada debe haber sido eliminada
        remaining = mem.all_entries()
        contents = [e.content for e in remaining]
        assert "Hecho en cuarentena expirada" not in contents
        assert "Hecho normal" in contents

    def test_consolidate_includes_quarantine_stats(self):
        """consolidate() incluye stats de cuarentena en el resultado."""
        mem = LivingMemory(max_entries=100)
        for i in range(5):
            mem.add(content=f"Hecho {i}", type="semantic", confidence=0.7, salience=0.6)
        
        q = KnowledgeQuarantine()
        dc = DeepConsolidation(memory=mem, quarantine=q)
        result = dc.consolidate()
        
        assert "quarantine_stats" in result
        assert result["quarantine_stats"]["total"] == 0

    def test_without_quarantine_compat(self):
        """DeepConsolidation sin quarantine funciona como antes."""
        mem = LivingMemory(max_entries=100)
        for i in range(5):
            mem.add(content=f"Hecho {i}", type="semantic", confidence=0.7, salience=0.6)
        
        dc = DeepConsolidation(memory=mem)
        # No debe fallar
        result = dc.consolidate()
        assert result["total_operations"] >= 0


# ============================================================
# 3. Critic + Quarantine
# ============================================================

class TestCriticQuarantine:

    @pytest.mark.asyncio
    async def test_critic_approves_normal_thought(self):
        """Critic aprueba pensamiento normal sin contexto crítico."""
        critic = Critic()
        result = await critic.evaluate("Este es un pensamiento válido y suficientemente largo.")
        assert result["approved"] is True

    @pytest.mark.asyncio
    async def test_critic_rejects_quarantine_in_critical_context(self):
        """Critic rechaza pensamiento que usa memoria en cuarentena en contexto crítico."""
        q = KnowledgeQuarantine()
        # Marcar una entry como en cuarentena
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem_001",
        )
        
        critic = Critic(quarantine=q)
        result = await critic.evaluate(
            "Te recomiendo esta medicación para tu tratamiento.",
            context={
                "critical_context": True,
                "used_memory_ids": ["mem_001"],
            }
        )
        assert result["approved"] is False
        assert "quarantine_violation" in result["reason"]
        assert result.get("quarantine_violation") is True

    @pytest.mark.asyncio
    async def test_critic_auto_detects_sensitive_domain(self):
        """Critic auto-detecta dominio sensible sin que se lo digan."""
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem_001",
        )
        
        critic = Critic(quarantine=q)
        # Texto con palabra médica → dominio sensible detectado
        result = await critic.evaluate(
            "Esta medicación te ayudará con tu diagnóstico.",
            context={
                "used_memory_ids": ["mem_001"],
            }
        )
        assert result["approved"] is False
        assert "quarantine_violation" in result["reason"]

    @pytest.mark.asyncio
    async def test_critic_approves_quarantine_in_non_critical(self):
        """Critic aprueba cuarentena en contexto NO crítico (puede usarse para brainstorming)."""
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id="mem_001",
        )
        
        critic = Critic(quarantine=q)
        result = await critic.evaluate(
            "Idea creativa sobre algo, sin tocar dominios sensibles.",
            context={
                "critical_context": False,
                "used_memory_ids": ["mem_001"],
            }
        )
        # Sin dominio sensible detectado y critical_context=False → aprueba
        assert result["approved"] is True

    @pytest.mark.asyncio
    async def test_critic_stats_track_quarantine(self):
        """Las stats del Critic registran checks y rejections."""
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q_test",
            claim="test",
            source="llm",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem_001",
        )
        
        critic = Critic(quarantine=q)
        await critic.evaluate(
            "Esta medicación te ayudará.",
            context={
                "critical_context": True,
                "used_memory_ids": ["mem_001"],
            }
        )
        
        stats = critic.get_stats()
        assert stats["quarantine_active"] is True
        assert stats["quarantine_checks"] >= 1
        assert stats["quarantine_rejections"] >= 1
        assert stats["rejection_counts"]["quarantine_violation"] >= 1

    @pytest.mark.asyncio
    async def test_critic_without_quarantine_compat(self):
        """Critic sin quarantine funciona como antes."""
        critic = Critic()
        result = await critic.evaluate(
            "Pensamiento normal.",
            context={"critical_context": True, "used_memory_ids": ["mem_001"]}
        )
        # Sin quarantine, no puede verificar → aprueba (backward compat)
        assert result["approved"] is True


# ============================================================
# 4. Integration: Learner + Quarantine + Curator + Critic
# ============================================================

class TestFullEpistemicIntegration:

    def test_learner_propose_goes_to_quarantine_curator_filters(self):
        """Flujo completo: Learner propone → cuarentena → Curator filtra."""
        mem = LivingMemory(max_entries=100)
        q = KnowledgeQuarantine()
        validator = EpistemicValidator()
        
        learner = Learner(epistemic_validator=validator, quarantine=q)
        curator = Curator(memory=mem, quarantine=q)
        
        # Learner propone conocimiento de LLM (va a cuarentena)
        mutation = learner.propose_learning(
            content="Hecho nuevo de GPT-4o.",
            source="llm:gpt-4o",
        )
        assert mutation["metadata"]["quarantine"] is True
        
        # Añadir la entry a memoria manualmente (simulando aplicación de mutación)
        mem.add(
            content="Hecho nuevo de GPT-4o.",
            type="semantic",
            confidence=0.5,
            provenance="llm:gpt-4o",
        )
        
        # Marcar la entry en memoria como en cuarentena
        entries = mem.all_entries()
        last_entry = entries[-1]
        qid = mutation["metadata"].get("quarantine_entry_id")
        if qid:
            q._memory_entry_map[last_entry.id] = qid
        
        # Curator en contexto crítico filtra la entry
        safe = curator.get_safe_entries(n=10, critical_context=True)
        contents = [e["content"] for e in safe]
        assert "Hecho nuevo de GPT-4o." not in contents
        
        # En contexto no crítico, la entry está disponible
        all_entries = curator.get_safe_entries(n=10, critical_context=False)
        all_contents = [e["content"] for e in all_entries]
        assert "Hecho nuevo de GPT-4o." in all_contents

    @pytest.mark.asyncio
    async def test_critic_rejects_response_based_on_quarantined_knowledge(self):
        """Flujo completo: Learner cuarentena → Speaker usa → Critic rechaza."""
        q = KnowledgeQuarantine()
        validator = EpistemicValidator()
        
        # Learner propone hecho médico de LLM → cuarentena
        learner = Learner(epistemic_validator=validator, quarantine=q)
        mutation = learner.propose_learning(
            content="La dosis de paracetamol es 1g cada 6 horas.",
            source="llm:gpt-4o",
        )
        # Dominio médico sensible → triple validation requerida → cuarentena
        assert mutation["metadata"]["quarantine"] is True
        
        # Simular que Speaker construye respuesta usando esta entry
        qid = mutation["metadata"].get("quarantine_entry_id")
        # Registrar entry en memoria con ID ficticio "mem_medical_001"
        q._memory_entry_map["mem_medical_001"] = qid
        
        # Critic verifica: dominio médico + entry en cuarentena → rechazo
        critic = Critic(quarantine=q)
        result = await critic.evaluate(
            "Te recomiendo tomar paracetamol cada 6 horas para tu tratamiento.",
            context={
                "critical_context": True,
                "used_memory_ids": ["mem_medical_001"],
                "detected_domain": "medical",
            }
        )
        assert result["approved"] is False
        assert "quarantine_violation" in result["reason"]


# ============================================================
# 5. Stats aggregation
# ============================================================

class TestStatsAggregation:

    def test_quarantine_stats_visible_in_all_components(self):
        """Las stats de cuarentena son visibles desde Curator, DeepConsolidation y Critic."""
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q1",
            claim="test",
            source="llm",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem_001",
        )
        
        mem = LivingMemory(max_entries=100)
        # Añadir suficientes entries para que curate() funcione (>=5)
        for i in range(7):
            mem.add(content=f"test entry {i}", type="semantic", confidence=0.7, salience=0.6)
        
        curator = Curator(memory=mem, quarantine=q)
        dc = DeepConsolidation(memory=mem, quarantine=q)
        critic = Critic(quarantine=q)
        
        # Curate necesita >=5 entries
        import asyncio
        curator_result = asyncio.run(curator.curate())
        curator_stats = curator.get_stats()
        dc_result = dc.consolidate()
        critic_stats = critic.get_stats()
        
        # Todas deben mostrar quarantine_active=True
        assert curator_stats["quarantine_active"] is True
        assert critic_stats["quarantine_active"] is True
        assert "quarantine_stats" in dc_result
        
        # Curator stats (desde get_stats, no desde curate())
        assert "quarantine_stats" in curator_stats
        assert "quarantine_stats" in critic_stats
        
        # Y todas deben reportar 1 entry activa
        assert curator_stats["quarantine_stats"]["active"] == 1
        assert critic_stats["quarantine_stats"]["active"] == 1
