"""Tests para Fase 2 — World Model V2, Active Inference, Sub-agentes, Meta-cognition, Global Workspace."""

import asyncio
import pytest
import time

from zoe.core.world_model_v2 import WorldModelV2, _ngram_embedding, _cosine_distance
from zoe.core.active_inference import ActiveInferenceLoop
from zoe.core.meta_cognition import MetaCognition
from zoe.core.global_workspace import GlobalWorkspace, Proposal
from zoe.core.subagents.phase2_subagents import (
    Memorialist, Learner, Curator, Creativity,
    CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine,
)
from zoe.core.living_memory import LivingMemory
from zoe.core.cognitive_loop import Observation


# ===== World Model V2 =====

def test_ngram_embedding_dimensions():
    emb = _ngram_embedding("test", dim=128)
    assert len(emb) == 128

def test_ngram_embedding_deterministic():
    assert _ngram_embedding("hola", 64) == _ngram_embedding("hola", 64)

def test_ngram_embedding_similar_words():
    """Palabras similares tienen embeddings más cercanos que palabras distintas."""
    emb_gato = _ngram_embedding("gato", 128)
    emb_gatos = _ngram_embedding("gatos", 128)
    emb_perro = _ngram_embedding("perro", 128)
    d_similar = _cosine_distance(emb_gato, emb_gatos)
    d_different = _cosine_distance(emb_gato, emb_perro)
    assert d_similar < d_different

def test_world_model_v2_no_history():
    wm = WorldModelV2()
    pred = asyncio.get_event_loop().run_until_complete(wm.predict_next([]))
    assert pred["confidence"] == 0.0

@pytest.mark.asyncio
async def test_world_model_v2_learns_transitions():
    wm = WorldModelV2()
    for i in range(5):
        obs = Observation(timestamp=i, source="clock", content="tick del reloj")
        await wm.compute_surprise({"predicted_embedding": None}, [obs])
    pred = await wm.predict_next([])
    assert pred["confidence"] > 0.0

@pytest.mark.asyncio
async def test_world_model_v2_predicts_source():
    wm = WorldModelV2()
    # Alternar entre clock y user
    for _ in range(3):
        await wm.compute_surprise({"predicted_embedding": None}, [Observation(timestamp=0, source="clock", content="tick")])
        await wm.compute_surprise({"predicted_embedding": None}, [Observation(timestamp=1, source="user", content="hola")])
    pred = await wm.predict_next([])
    assert pred["predicted_source"] in ("clock", "user")

@pytest.mark.asyncio
async def test_world_model_v2_novel_input_surprise():
    wm = WorldModelV2()
    for i in range(5):
        await wm.compute_surprise({"predicted_embedding": None}, [Observation(timestamp=i, source="clock", content="patrón estable")])
    pred = await wm.predict_next([])
    novel = Observation(timestamp=10, source="network", content="algo totalmente diferente e inesperado")
    surprise = await wm.compute_surprise(pred, [novel])
    assert surprise > 0.0

@pytest.mark.asyncio
async def test_world_model_v2_stats():
    wm = WorldModelV2()
    for i in range(3):
        await wm.compute_surprise({"predicted_embedding": None}, [Observation(timestamp=i, source="clock", content="test")])
    stats = wm.get_stats()
    assert stats["history_size"] == 3
    assert "embedding_backend" in stats


# ===== Active Inference =====

def test_active_inference_initial():
    ai = ActiveInferenceLoop()
    assert ai.get_current_state() == "unknown"

def test_active_inference_update_beliefs():
    ai = ActiveInferenceLoop()
    ai.update_beliefs("clock", "tick")
    assert "clock" in ai.get_beliefs()

def test_active_inference_learn_transition():
    ai = ActiveInferenceLoop()
    ai.learn_transition("clock", "observe", "clock")
    pred = ai.predict_next_state("clock", "observe")
    assert "clock" in pred

def test_active_inference_select_action():
    ai = ActiveInferenceLoop()
    ai.update_beliefs("clock", "tick")
    action = ai.select_action("clock")
    assert action in ai._actions

def test_active_inference_record_result():
    ai = ActiveInferenceLoop()
    ai.record_action_result("clock", "observe", "clock", 0.2)
    assert len(ai._action_history) == 1

def test_active_inference_stats():
    ai = ActiveInferenceLoop()
    ai.update_beliefs("clock", "tick")
    ai.learn_transition("clock", "observe", "clock")
    stats = ai.get_stats()
    assert stats["states_known"] >= 1
    assert stats["transitions_learned"] >= 1


# ===== Sub-agentes Fase 2 =====

@pytest.mark.asyncio
async def test_memorialist_retrieves():
    mem = LivingMemory()
    mem.add(content="el gato come pescado", provenance="test")
    mem.add(content="el perro come carne", provenance="test")
    m = Memorialist(memory=mem)
    result = await m.retrieve_relevant({"recent_observations": [{"content": "gato"}]})
    assert len(result) >= 1

@pytest.mark.asyncio
async def test_memorialist_generates_thought():
    mem = LivingMemory()
    mem.add(content="evento importante", provenance="test", confidence=0.8)
    m = Memorialist(memory=mem)
    thought = await m.generate_thought({"recent_observations": [{"content": "evento"}]})
    assert thought

@pytest.mark.asyncio
async def test_learner_proposes():
    l = Learner()
    mutation = l.propose_learning("test content", confidence=0.7)
    assert mutation["type"] == "add_memory"
    assert mutation["confidence"] == 0.7

@pytest.mark.asyncio
async def test_learner_generates_thought_high_surprise():
    l = Learner()
    thought = await l.generate_thought({"surprise": 0.8, "recent_observations": [{"content": "inesperado"}]})
    assert "sorprendente" in thought.lower() or "sorpresa" in thought.lower()

@pytest.mark.asyncio
async def test_curator_curates():
    mem = LivingMemory()
    for i in range(10):
        mem.add(content=f"entry {i}", provenance="test")
    c = Curator(memory=mem)
    result = await c.curate()
    assert "operation" in result

@pytest.mark.asyncio
async def test_creativity_generates_hypothesis():
    c = Creativity()
    thought = await c.generate_thought({"surprise": 0.5, "recent_observations": [{"content": "patrón X"}]})
    assert thought

@pytest.mark.asyncio
async def test_causal_engine_detects_causality():
    ce = CausalEngine()
    thought = await ce.generate_thought({"recent_observations": [{"content": "A"}, {"content": "B"}]})
    assert "causal" in thought.lower() or "causa" in thought.lower()

@pytest.mark.asyncio
async def test_emotional_motor_surprise():
    em = EmotionalMotor()
    thought = await em.generate_thought({"surprise": 0.8, "state": {"energy": 1.0, "arousal": 0.5}})
    assert "sorpresa" in thought.lower()

@pytest.mark.asyncio
async def test_emotional_motor_fatigue():
    em = EmotionalMotor()
    thought = await em.generate_thought({"surprise": 0.1, "state": {"energy": 0.2, "arousal": 0.3}})
    assert "agotamiento" in thought.lower() or "energía" in thought.lower()

@pytest.mark.asyncio
async def test_ethical_motor_evaluates():
    em = EthicalMotor()
    result = em.evaluate_action({"type": "communicate", "description": "responder al usuario"})
    assert "scores" in result
    assert result["scores"]["transparencia_sobre_opacidad"] == 0.8

@pytest.mark.asyncio
async def test_scientific_engine_theory():
    se = ScientificEngine()
    theory = se.propose_theory("test hypothesis", ["evidence1"])
    assert theory["hypothesis"] == "test hypothesis"
    assert theory["status"] == "proposed"

@pytest.mark.asyncio
async def test_scientific_engine_generates_thought():
    se = ScientificEngine()
    thought = await se.generate_thought({"surprise": 0.7, "recent_observations": [{"content": "inesperado"}]})
    assert "teoría" in thought.lower() or "hipótesis" in thought.lower() or "experimento" in thought.lower()


# ===== Meta-Cognition =====

def test_metacog_initial():
    mc = MetaCognition()
    assert mc._system1_uses == 0
    assert mc._system2_uses == 0

def test_metacog_evaluate_confidence_high():
    mc = MetaCognition()
    conf = mc.evaluate_confidence("respuesta larga y detallada", surprise=0.1)
    assert conf > 0.5

def test_metacog_evaluate_confidence_low():
    mc = MetaCognition()
    conf = mc.evaluate_confidence("", surprise=0.8)
    assert conf < 0.5

def test_metacog_should_deliberate_low_confidence():
    mc = MetaCognition()
    deliberate, reason = mc.should_deliberate(confidence=0.3, stakes=0.5, energy=1.0)
    assert deliberate is True
    assert "confidence" in reason.lower()

def test_metacog_should_not_deliberate_high_confidence():
    mc = MetaCognition()
    deliberate, reason = mc.should_deliberate(confidence=0.9, stakes=0.3, energy=1.0)
    assert deliberate is False

def test_metacog_should_deliberate_high_stakes():
    mc = MetaCognition()
    deliberate, reason = mc.should_deliberate(confidence=0.7, stakes=0.8, energy=1.0)
    assert deliberate is True
    assert "stakes" in reason.lower()

def test_metacog_no_deliberate_low_energy():
    mc = MetaCognition()
    deliberate, reason = mc.should_deliberate(confidence=0.2, stakes=0.9, energy=0.1)
    assert deliberate is False
    assert "energy" in reason.lower()

def test_metacog_stats():
    mc = MetaCognition()
    mc.should_deliberate(0.9, 0.3, 1.0)  # s1
    mc.should_deliberate(0.2, 0.5, 1.0)  # s2
    stats = mc.get_stats()
    assert stats["system1_uses"] == 1
    assert stats["system2_uses"] == 1


# ===== Global Workspace =====

def test_workspace_initial():
    gw = GlobalWorkspace()
    assert len(gw._proposals) == 0

def test_workspace_submit():
    gw = GlobalWorkspace()
    gw.submit(Proposal(subagent_name="Speaker", action="think", content="test"))
    assert len(gw._proposals) == 1

def test_workspace_compete():
    gw = GlobalWorkspace()
    gw.submit(Proposal(subagent_name="A", action="think", content="low", relevance=0.3))
    gw.submit(Proposal(subagent_name="B", action="explore", content="high", relevance=0.9))
    winners = gw.compete(available_energy=1.0)
    assert len(winners) >= 1
    assert winners[0].subagent_name == "B"

def test_workspace_broadcast():
    gw = GlobalWorkspace()
    gw.submit(Proposal(subagent_name="A", action="think", content="test"))
    gw.compete()
    broadcast = gw.broadcast()
    assert "winning_actions" in broadcast

def test_workspace_clear():
    gw = GlobalWorkspace()
    gw.submit(Proposal(subagent_name="A", action="think", content="test"))
    gw.clear()
    assert len(gw._proposals) == 0

def test_workspace_stats():
    gw = GlobalWorkspace()
    gw.submit(Proposal(subagent_name="A", action="think", content="test"))
    gw.compete()
    stats = gw.get_stats()
    assert stats["total_competitions"] == 1

def test_proposal_score():
    p = Proposal(subagent_name="A", action="think", content="test", relevance=0.8, urgency=0.7, novelty=0.6, energy_cost=0.2)
    score = p.score(available_energy=1.0)
    assert 0 < score < 1

def test_proposal_score_penalized_low_energy():
    p = Proposal(subagent_name="A", action="think", content="test", relevance=0.8, energy_cost=0.9)
    score_low = p.score(available_energy=0.5)
    score_high = p.score(available_energy=1.0)
    assert score_low < score_high
