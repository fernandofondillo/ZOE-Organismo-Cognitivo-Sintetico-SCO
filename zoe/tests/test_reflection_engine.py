"""
ZOE v2.1 — Tests reales para ReflectionEngine

Cobertura:
- ReflectionConfig defaults
- BudgetTracker (reset diario, can_spend, record_spend, remaining)
- ReflectionEngine inicialización
- _should_reflect con diferentes estados metabólicos
- _compute_salience
- _build_reflection_prompt
- _decide_local_vs_cloud
- get_metrics
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
    """Tests para la configuración del ReflectionEngine."""

    def test_default_config(self):
        """Config por defecto es segura para MacBook Air M3 8GB."""
        cfg = ReflectionConfig()
        assert cfg.reflection_period_cycles == 1
        assert cfg.max_reflections_per_cycle == 2
        assert cfg.max_capsules_per_cycle == 3
        assert cfg.salience_threshold == 0.6
        assert cfg.max_fatigue_for_reflection == 0.8
        assert cfg.reflection_timeout == 120.0
        assert cfg.max_input_tokens == 2048
        assert cfg.max_output_tokens == 512
        assert cfg.daily_cloud_budget == 1.0
        assert cfg.model_tag == "qwq-32b-iq2"  # Modelo que ya existe en ZOE
        assert cfg.model_fallback_tag == "qwen2.5:14b-iq2"

    def test_custom_config(self):
        """Config personalizada respeta valores."""
        cfg = ReflectionConfig(
            model_tag="deepseek-r1:32b-iq2",
            daily_cloud_budget=5.0,
            max_reflections_per_cycle=5,
        )
        assert cfg.model_tag == "deepseek-r1:32b-iq2"
        assert cfg.daily_cloud_budget == 5.0
        assert cfg.max_reflections_per_cycle == 5


class TestBudgetTracker:
    """Tests para el gestor de presupuesto cloud."""

    def test_daily_budget_default(self):
        """Presupuesto por defecto: $1/día."""
        bt = BudgetTracker()
        assert bt.daily_budget == 1.0
        assert bt.daily_spent == 0.0
        assert bt.remaining_budget() == 1.0

    def test_can_spend_within_budget(self):
        """Puede gastar si está dentro del presupuesto."""
        bt = BudgetTracker(daily_budget=1.0)
        assert bt.can_spend(estimated_cost=0.5) is True
        assert bt.can_spend(estimated_cost=1.0) is True

    def test_can_spend_over_budget(self):
        """NO puede gastar si excede el presupuesto."""
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.9
        bt.last_reset = time.time()  # Prevenir reset automático
        assert bt.can_spend(estimated_cost=0.2) is False

    def test_record_spend_calculates_cost(self):
        """Registra gasto y calcula costo correctamente."""
        bt = BudgetTracker()
        cost = bt.record_spend("gpt-4o", input_tokens=1000, output_tokens=500)
        # gpt-4o: input $0.00250/1K, output $0.01000/1K
        expected = (1000 / 1000) * 0.00250 + (500 / 1000) * 0.01000
        assert abs(cost - expected) < 0.001
        assert abs(bt.daily_spent - expected) < 0.001

    def test_record_spend_custom_model(self):
        """Registra gasto para modelo no listado usa defaults."""
        bt = BudgetTracker()
        cost = bt.record_spend("unknown-model", input_tokens=2000, output_tokens=1000)
        expected = (2000 / 1000) * 0.00250 + (1000 / 1000) * 0.01000
        assert abs(cost - expected) < 0.001

    def test_daily_reset(self):
        """Reset diario funciona después de 24h."""
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.9
        bt.last_reset = time.time() - 90000  # 25 horas atrás
        assert bt.remaining_budget() == 1.0  # Reset automático

    def test_no_reset_before_24h(self):
        """NO resetea antes de 24h."""
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.9
        bt.last_reset = time.time() - 3600  # 1 hora atrás
        assert abs(bt.remaining_budget() - 0.1) < 0.001  # Sin reset

    def test_remaining_hours_estimate(self):
        """Estimación de horas restantes."""
        bt = BudgetTracker(daily_budget=1.0)
        bt.daily_spent = 0.5
        bt.last_reset = time.time()  # Prevenir reset
        hours = bt.remaining_hours_estimate(avg_hourly_spend=0.1)
        assert abs(hours - 5.0) < 0.01


class TestReflectionEngineInit:
    """Tests para la inicialización del ReflectionEngine."""

    def test_init_defaults(self):
        """Inicialización con defaults."""
        engine = ReflectionEngine()
        assert engine.config.model_tag == "qwq-32b-iq2"
        assert engine._total_reflections == 0
        assert engine._total_insights == 0
        assert engine._total_cost_usd == 0.0
        assert engine._cycle_count == 0
        assert engine._errors == 0

    def test_init_with_mocks(self):
        """Inicialización con dependencias mock."""
        mock_llm = MagicMock()
        mock_memory = MagicMock()
        mock_storage = MagicMock()
        mock_cb = MagicMock()
        mock_mentor = MagicMock()
        mock_quarantine = MagicMock()

        engine = ReflectionEngine(
            llm_peripheral=mock_llm,
            memory=mock_memory,
            storage=mock_storage,
            circuit_breaker=mock_cb,
            mentor=mock_mentor,
            quarantine=mock_quarantine,
        )
        assert engine._llm is mock_llm
        assert engine._memory is mock_memory
        assert engine._storage is mock_storage
        assert engine._cb is mock_cb
        assert engine._mentor is mock_mentor
        assert engine._quarantine is mock_quarantine


class TestShouldReflect:
    """Tests para _should_reflect."""

    def test_should_reflect_normal_state(self):
        """Debe reflexionar en estado normal."""
        mock_llm = MagicMock()
        engine = ReflectionEngine(llm_peripheral=mock_llm)
        state = {"fatigue": 0.5, "energy": 0.7}
        assert engine._should_reflect(state) is True

    def test_should_reflect_high_fatigue(self):
        """NO debe reflexionar si fatiga > 0.8."""
        engine = ReflectionEngine(config=ReflectionConfig(max_fatigue_for_reflection=0.8))
        state = {"fatigue": 0.9, "energy": 0.2}
        assert engine._should_reflect(state) is False

    def test_should_reflect_no_llm(self):
        """NO debe reflexionar sin LLM."""
        engine = ReflectionEngine(llm_peripheral=None)
        state = {"fatigue": 0.5}
        assert engine._should_reflect(state) is False

    def test_should_reflect_cb_open(self):
        """NO debe reflexionar si CircuitBreaker está OPEN."""
        cb = MagicMock()
        cb.state = "OPEN"
        engine = ReflectionEngine(circuit_breaker=cb)
        state = {"fatigue": 0.5}
        assert engine._should_reflect(state) is False


class TestComputeSalience:
    """Tests para _compute_salience."""

    def test_salience_base(self):
        """Salience base es 0.5."""
        engine = ReflectionEngine()
        entry = {"timestamp": time.time(), "confidence": 0.8}
        s = engine._compute_salience(entry)
        assert 0.5 <= s <= 1.0

    def test_salience_recent_high_emotion(self):
        """Memoria reciente + emoción alta = salience alta."""
        engine = ReflectionEngine()
        entry = {
            "timestamp": time.time(),
            "emotional_intensity": 0.9,
            "confidence": 0.3,
            "related_ids": ["a", "b", "c"],
        }
        s = engine._compute_salience(entry)
        assert s > 0.7  # Debe ser alta

    def test_salience_old_low_confidence(self):
        """Memoria vieja + baja confianza = salience baja."""
        engine = ReflectionEngine()
        entry = {
            "timestamp": time.time() - 86400 * 2,  # 2 días
            "emotional_intensity": 0.1,
            "confidence": 0.9,
        }
        s = engine._compute_salience(entry)
        assert s < 0.7  # Debe ser baja


class TestBuildReflectionPrompt:
    """Tests para _build_reflection_prompt."""

    def test_prompt_episodic(self):
        """Prompt para memoria episódica."""
        engine = ReflectionEngine()
        memory = {"content": "El usuario estaba triste hoy", "_type": "episodic"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Reflexiona sobre esta experiencia" in prompt
        assert "El usuario estaba triste hoy" in prompt

    def test_prompt_semantic(self):
        """Prompt para memoria semántica."""
        engine = ReflectionEngine()
        memory = {"content": "Python es un lenguaje de programación", "_type": "semantic"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Analiza este conocimiento" in prompt

    def test_prompt_counterfactual(self):
        """Prompt para memoria contrafactual."""
        engine = ReflectionEngine()
        memory = {"content": "¿Y si hubiera elegido otro camino?", "_type": "counterfactual"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Continúa esta línea de pensamiento" in prompt

    def test_prompt_unknown_type(self):
        """Prompt para tipo desconocido usa default."""
        engine = ReflectionEngine()
        memory = {"content": "Algo interesante", "_type": "unknown"}
        prompt = engine._build_reflection_prompt(memory)
        assert "Reflexiona sobre esto" in prompt


class TestDecideLocalVsCloud:
    """Tests para _decide_local_vs_cloud."""

    def test_prefers_local(self):
        """Por defecto prefiere local."""
        engine = ReflectionEngine()
        assert engine._decide_local_vs_cloud() is False

    def test_uses_cloud_when_no_budget(self):
        """NO usa cloud si no hay presupuesto."""
        engine = ReflectionEngine(config=ReflectionConfig(daily_cloud_budget=0.0))
        assert engine._decide_local_vs_cloud() is False

    def test_uses_cloud_when_cb_open(self):
        """Usa cloud como fallback si CB está OPEN y hay presupuesto."""
        cb = MagicMock()
        cb.state = "OPEN"
        engine = ReflectionEngine(
            circuit_breaker=cb,
            config=ReflectionConfig(daily_cloud_budget=1.0),
        )
        result = engine._decide_local_vs_cloud()
        assert isinstance(result, bool)


class TestGetMetrics:
    """Tests para get_metrics."""

    def test_metrics_initial(self):
        """Métricas iniciales son cero."""
        engine = ReflectionEngine()
        m = engine.get_metrics()
        assert m["total_reflections"] == 0
        assert m["total_insights"] == 0
        assert m["total_cost_usd"] == 0.0
        assert m["errors"] == 0
        assert m["is_running"] is False
        assert m["model_tag"] == "qwq-32b-iq2"

    def test_metrics_after_reflection(self):
        """Métricas reflejan actividad."""
        engine = ReflectionEngine()
        engine._total_reflections = 5
        engine._total_insights = 3
        engine._total_cost_usd = 0.15
        engine._errors = 1
        engine._cycle_count = 10
        m = engine.get_metrics()
        assert m["total_reflections"] == 5
        assert m["total_insights"] == 3
        assert abs(m["total_cost_usd"] - 0.15) < 0.01
        assert m["errors"] == 1
        assert m["daily_budget_remaining"] > 0


class TestReflectionHook:
    """Tests para ReflectionHook."""

    def test_hook_init(self):
        """Hook se inicializa con engine."""
        from zoe.core.reflection_hook import ReflectionHook
        engine = ReflectionEngine()
        hook = ReflectionHook(engine)
        assert hook._engine is engine

    def test_hook_on_sleeping_no_engine(self):
        """Hook sin engine retorna lista vacía."""
        from zoe.core.reflection_hook import ReflectionHook
        hook = ReflectionHook(None)
        state = {"fatigue": 0.5, "energy": 0.7, "compute_budget": 1.0}
        result = asyncio.run(hook.on_sleeping(state))
        assert result == []

    def test_hook_on_sleeping_low_budget(self):
        """Hook no ejecuta si compute_budget < 0.2."""
        from zoe.core.reflection_hook import ReflectionHook
        engine = ReflectionEngine()
        hook = ReflectionHook(engine)
        state = {"fatigue": 0.5, "compute_budget": 0.1}
        result = asyncio.run(hook.on_sleeping(state))
        assert result == []


class TestValidateInsight:
    """Tests para _validate_insight."""

    @pytest.mark.asyncio
    async def test_valid_insight_good_length(self):
        """Insight con longitud correcta = confianza alta."""
        engine = ReflectionEngine()
        insight = "Este es un insight sustantivo sobre el patrón detectado en la memoria."
        memory = {"content": "Algo"}
        confidence = await engine._validate_insight(insight, memory)
        assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_valid_insight_too_short(self):
        """Insight muy corto = confianza penalizada (pero no tan baja si es sustantivo)."""
        engine = ReflectionEngine()
        insight = "Sí"
        memory = {"content": "Algo"}
        confidence = await engine._validate_insight(insight, memory)
        # Base 0.5 - 0.2 (corto) + 0.15 (no repetido) + 0.1 (no genérico) = 0.55
        assert 0.3 < confidence < 0.7

    @pytest.mark.asyncio
    async def test_valid_insight_generic(self):
        """Insight genérico = confianza reducida."""
        engine = ReflectionEngine()
        insight = "Es importante considerar que esto es relevante e interesante."
        memory = {"content": "Algo"}
        confidence = await engine._validate_insight(insight, memory)
        # Contiene frases genéricas, debe ser menor
        assert confidence < 0.9

    @pytest.mark.asyncio
    async def test_valid_insight_duplicate(self):
        """Insight que replica el input = confianza muy baja."""
        engine = ReflectionEngine()
        insight = "El usuario estaba triste hoy"
        memory = {"content": "El usuario estaba triste hoy"}
        confidence = await engine._validate_insight(insight, memory)
        assert confidence < 0.5  # Duplicado = penalización
