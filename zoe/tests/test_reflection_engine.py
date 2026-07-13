"""
ZOE v2.1.1 — Tests reales para ReflectionEngine con DeepSeek-R1:32B Q4_K_M
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zoe.core.reflection_engine import (
    ReflectionConfig,
    ReflectionEngine,
    ReflectionResult,
    BudgetTracker,
)


class TestReflectionConfig:
    """Tests para la configuracion del ReflectionEngine."""

    def test_default_config_deepseek_q4km(self):
        """Config por defecto usa DeepSeek-R1:32B Q4_K_M."""
        cfg = ReflectionConfig()
        assert cfg.model_tag == "deepseek-r1:32b-q4km"
        assert cfg.model_fallback_tag == "qwq-32b-iq2"
        assert cfg.reflection_period_cycles == 1
        assert cfg.max_reflections_per_cycle == 2
        assert cfg.daily_cloud_budget == 1.0

    def test_custom_config(self):
        """Config personalizada."""
        cfg = ReflectionConfig(
            model_tag="qwq-32b-iq2",
            daily_cloud_budget=5.0,
            max_reflections_per_cycle=5,
        )
        assert cfg.model_tag == "qwq-32b-iq2"
        assert cfg.daily_cloud_budget == 5.0


class TestBudgetTracker:
    """Tests para el gestor de presupuesto cloud."""

    def test_daily_budget_default(self):
        bt = BudgetTracker()
        assert bt.daily_budget == 1.0
        assert bt.remaining_budget() == 1.0

    def test_can_spend_within_budget(self):
        bt = BudgetTracker(daily_budget=1.0)
        assert bt.can_spend(estimated_cost=0.5) is True

    def test_can_spend_over_budget(self):
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.9
        bt.last_reset = time.time()
        assert bt.can_spend(estimated_cost=0.2) is False

    def test_record_spend_calculates_cost(self):
        bt = BudgetTracker()
        cost = bt.record_spend("gpt-4o", input_tokens=1000, output_tokens=500)
        expected = 1.0 * 0.00250 + 0.5 * 0.01000
        assert abs(cost - expected) < 0.001

    def test_daily_reset(self):
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.9
        bt.last_reset = time.time() - 90000
        assert bt.remaining_budget() == 1.0

    def test_remaining_hours_estimate(self):
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.5
        bt.last_reset = time.time()
        hours = bt.remaining_hours_estimate(avg_hourly_spend=0.1)
        assert abs(hours - 5.0) < 0.01


class TestReflectionEngineInit:
    """Tests para inicializacion."""

    def test_init_defaults_deepseek(self):
        """Inicializacion con DeepSeek-R1:32B Q4_K_M por defecto."""
        engine = ReflectionEngine()
        assert engine.config.model_tag == "deepseek-r1:32b-q4km"
        assert engine.config.model_fallback_tag == "qwq-32b-iq2"
        assert engine._total_reflections == 0
        assert engine._total_insights == 0

    def test_init_with_mocks(self):
        mock_llm = MagicMock()
        engine = ReflectionEngine(llm_peripheral=mock_llm)
        assert engine._llm is mock_llm


class TestShouldReflect:
    """Tests para _should_reflect."""

    def test_should_reflect_normal(self):
        mock_llm = MagicMock()
        engine = ReflectionEngine(llm_peripheral=mock_llm)
        assert engine._should_reflect({"fatigue": 0.5}) is True

    def test_should_reflect_high_fatigue(self):
        engine = ReflectionEngine(config=ReflectionConfig(max_fatigue_for_reflection=0.8))
        assert engine._should_reflect({"fatigue": 0.9}) is False

    def test_should_reflect_no_llm(self):
        engine = ReflectionEngine(llm_peripheral=None)
        assert engine._should_reflect({"fatigue": 0.5}) is False


class TestComputeSalience:
    """Tests para _compute_salience."""

    def test_salience_recent_high_emotion(self):
        engine = ReflectionEngine()
        entry = {"timestamp": time.time(), "emotional_intensity": 0.9, "confidence": 0.3, "related_ids": ["a", "b"]}
        s = engine._compute_salience(entry)
        assert s > 0.7

    def test_salience_base(self):
        engine = ReflectionEngine()
        entry = {"timestamp": time.time(), "confidence": 0.8}
        s = engine._compute_salience(entry)
        assert 0.5 <= s <= 1.0


class TestBuildReflectionPrompt:
    """Tests para _build_reflection_prompt."""

    def test_prompt_episodic(self):
        engine = ReflectionEngine()
        memory = {"content": "El usuario estaba triste", "_type": "episodic"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Reflexiona sobre esta experiencia" in prompt

    def test_prompt_semantic(self):
        engine = ReflectionEngine()
        memory = {"content": "Python es un lenguaje", "_type": "semantic"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Analiza este conocimiento" in prompt

    def test_prompt_counterfactual(self):
        engine = ReflectionEngine()
        memory = {"content": "Que hubiera pasado si...", "_type": "counterfactual"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Contin\xfaa esta l\xednea de pensamiento" in prompt


class TestDecideLocalVsCloud:
    """Tests para _decide_local_vs_cloud."""

    def test_prefers_local(self):
        engine = ReflectionEngine()
        assert engine._decide_local_vs_cloud() is False

    def test_no_budget_uses_local(self):
        engine = ReflectionEngine(config=ReflectionConfig(daily_cloud_budget=0.0))
        assert engine._decide_local_vs_cloud() is False


class TestGetMetrics:
    """Tests para get_metrics."""

    def test_metrics_initial(self):
        engine = ReflectionEngine()
        m = engine.get_metrics()
        assert m["total_reflections"] == 0
        assert m["total_insights"] == 0
        assert m["model_tag"] == "deepseek-r1:32b-q4km"

    def test_metrics_after_activity(self):
        engine = ReflectionEngine()
        engine._total_reflections = 5
        engine._total_insights = 3
        engine._total_cost_usd = 0.15
        m = engine.get_metrics()
        assert m["total_reflections"] == 5
        assert m["total_insights"] == 3
        assert abs(m["total_cost_usd"] - 0.15) < 0.01


class TestReflectionHook:
    """Tests para ReflectionHook."""

    def test_hook_init(self):
        from zoe.core.reflection_hook import ReflectionHook
        engine = ReflectionEngine()
        hook = ReflectionHook(engine)
        assert hook._engine is engine

    def test_hook_on_sleeping_no_engine(self):
        from zoe.core.reflection_hook import ReflectionHook
        hook = ReflectionHook(None)
        result = asyncio.run(hook.on_sleeping({"fatigue": 0.5, "compute_budget": 1.0}))
        assert result == []

    def test_hook_on_sleeping_low_budget(self):
        from zoe.core.reflection_hook import ReflectionHook
        engine = ReflectionEngine()
        hook = ReflectionHook(engine)
        result = asyncio.run(hook.on_sleeping({"fatigue": 0.5, "compute_budget": 0.1}))
        assert result == []


class TestValidateInsight:
    """Tests para _validate_insight."""

    @pytest.mark.asyncio
    async def test_valid_insight_good(self):
        engine = ReflectionEngine()
        insight = "Este es un insight sustantivo sobre patrones detectados."
        memory = {"content": "Algo"}
        confidence = await engine._validate_insight(insight, memory)
        assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_valid_insight_short(self):
        engine = ReflectionEngine()
        insight = "Si"
        memory = {"content": "Algo"}
        confidence = await engine._validate_insight(insight, memory)
        assert 0.3 < confidence < 0.7

    @pytest.mark.asyncio
    async def test_valid_insight_duplicate(self):
        engine = ReflectionEngine()
        insight = "El usuario estaba triste"
        memory = {"content": "El usuario estaba triste"}
        confidence = await engine._validate_insight(insight, memory)
        assert confidence < 0.5
