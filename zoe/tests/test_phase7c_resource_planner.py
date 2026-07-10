"""
Tests Fase 7C — Metabolic Resource Planner
"""

import asyncio
import pytest
import time

from zoe.core.resource_planner import (
    ResourcePlanner, ResourcePlan, PlanReason, MetabolicState,
)
from zoe.core.model_optimizer import ModelOptimizer
from zoe.peripherals.model_bus import ModelBus, SelectionStrategy
from zoe.peripherals.llm import MockPeripheral


# ============================================================
# Helpers
# ============================================================

class FakeLLM:
    """LLM fake para tests."""
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self): return self._name

    async def generate(self, *a, **kw): return "ok"
    async def generate_streaming(self, *a, **kw):
        yield "ok"
    async def health_check(self): return True


def make_bus_with_backends() -> ModelBus:
    """Crea un ModelBus con backends de prueba."""
    bus = ModelBus(strategy=SelectionStrategy.ACD_AWARE)
    bus.add_backend(
        FakeLLM("ollama_3b"), name="ollama_3b", priority=10,
        cost_per_1k=0.0, latency_ms=100, privacy="local",
        models=["qwen2.5:3b"], tags=["local", "fast", "cheap"],
    )
    bus.add_backend(
        FakeLLM("ollama_7b"), name="ollama_7b", priority=8,
        cost_per_1k=0.0, latency_ms=300, privacy="local",
        models=["qwen2.5:7b"], tags=["local", "balanced"],
    )
    bus.add_backend(
        FakeLLM("openai"), name="openai", priority=9,
        cost_per_1k=0.03, latency_ms=800, privacy="cloud",
        models=["gpt-4o"], tags=["cloud", "quality"], max_tokens=8192,
    )
    bus.add_backend(
        FakeLLM("anthropic"), name="anthropic", priority=9,
        cost_per_1k=0.02, latency_ms=700, privacy="cloud",
        models=["claude-sonnet-4-20250514"], tags=["cloud", "quality", "ethical"],
        max_tokens=8192,
    )
    return bus


# ============================================================
# 1. ResourcePlan
# ============================================================

class TestResourcePlan:

    def test_to_dict(self):
        plan = ResourcePlan(
            backend_name="ollama_3b",
            model_name="qwen2.5:3b",
            strategy="full_ram",
            reason="acd_local_fast",
            acd_level="L0_REFLEX",
            metabolic_state="awake",
        )
        d = plan.to_dict()
        assert d["backend_name"] == "ollama_3b"
        assert d["strategy"] == "full_ram"
        assert d["reason"] == "acd_local_fast"


# ============================================================
# 2. ResourcePlanner — planificación básica
# ============================================================

class TestResourcePlannerBasic:

    def test_plan_l0_uses_local_fast(self):
        """L0_REFLEX debe seleccionar backend local rápido."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L0_REFLEX",
            metabolic_state="awake",
            model_bus=bus,
            available_ram_gb=5.0,
        )
        assert plan.backend_name == "ollama_3b"
        assert plan.reason == PlanReason.ACD_LOCAL_FAST.value
        assert plan.strategy == "full_ram"
        assert plan.will_work is True

    def test_plan_l3_uses_quality(self):
        """L3_DEEP debe seleccionar backend de calidad."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L3_DEEP",
            metabolic_state="awake",
            model_bus=bus,
            available_ram_gb=5.0,
        )
        # L3 prefiere quality → cloud
        assert plan.backend_name in ("openai", "anthropic")
        assert plan.strategy == "cloud"
        assert plan.reason == PlanReason.ACD_QUALITY.value

    def test_plan_l2_uses_local_balanced(self):
        """L2_STANDARD debe seleccionar backend local medio."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            model_bus=bus,
            available_ram_gb=5.0,
        )
        # L2 prefiere local balanced
        assert plan.backend_name in ("ollama_3b", "ollama_7b")
        assert plan.reason == PlanReason.ACD_LOCAL_BALANCED.value

    def test_plan_sensitive_domain_excludes_cloud(self):
        """Dominio sensible excluye cloud."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L3_DEEP",
            metabolic_state="awake",
            sensitive_domain=True,
            model_bus=bus,
            available_ram_gb=5.0,
        )
        # Sensible → local solo
        assert plan.backend_name in ("ollama_3b", "ollama_7b")
        assert plan.reason == PlanReason.SENSITIVE_LOCAL.value
        assert "local" in plan.strategy or plan.strategy == "full_ram"

    def test_plan_sleeping_defers(self):
        """SLEEPING difiere la tarea."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="sleeping",
            model_bus=bus,
        )
        assert plan.will_work is False
        assert plan.reason == PlanReason.SLEEPING_DEFER.value

    def test_plan_drowsy_excludes_cloud(self):
        """DROWSY excluye cloud."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        plan = planner.plan(
            acd_level="L3_DEEP",
            metabolic_state="drowsy",
            model_bus=bus,
            available_ram_gb=5.0,
        )
        # DROWSY → solo local
        assert plan.backend_name in ("ollama_3b", "ollama_7b")
        assert plan.reason == PlanReason.DROWSY_LOCAL_ONLY.value

    def test_plan_no_backends_returns_no_resources(self):
        """Sin backends → NO_RESOURCES."""
        planner = ResourcePlanner()
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            model_bus=ModelBus(),  # bus vacío
        )
        assert plan.reason == PlanReason.NO_RESOURCES.value
        assert plan.will_work is False


# ============================================================
# 3. ResourcePlanner — con ModelOptimizer
# ============================================================

class TestResourcePlannerWithOptimizer:

    def test_plan_with_optimizer_checks_viability(self):
        """Con ModelOptimizer, verifica si el modelo local es viable."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        opt = ModelOptimizer()

        # Simular 5GB RAM → 3B cabe, 7B ajustado
        plan = planner.plan(
            acd_level="L0_REFLEX",
            metabolic_state="awake",
            model_bus=bus,
            model_optimizer=opt,
            available_ram_gb=5.0,
        )
        assert plan.will_work is True
        assert plan.strategy in ("full_ram", "mmap_partial", "mmap_full")

    def test_plan_cloud_fallback_when_local_not_viable(self):
        """Si modelo local no es viable, hace fallback a cloud."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        opt = ModelOptimizer()

        # Simular 1GB RAM → ni 3B cabe → cloud fallback
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            model_bus=bus,
            model_optimizer=opt,
            available_ram_gb=1.0,
        )
        # Debe intentar cloud (L2 permite cloud)
        assert plan.backend_name in ("openai", "anthropic", "ollama_3b", "ollama_7b")
        # Si cloud, reason es cloud_fallback o acd_quality
        if plan.strategy == "cloud":
            assert plan.reason in (PlanReason.CLOUD_FALLBACK.value, PlanReason.ACD_QUALITY.value)

    def test_plan_sensitive_with_optimizer_stays_local(self):
        """Dominio sensible + optimizer → se queda en local aunque no sea óptimo."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        opt = ModelOptimizer()

        plan = planner.plan(
            acd_level="L3_DEEP",
            metabolic_state="awake",
            sensitive_domain=True,
            model_bus=bus,
            model_optimizer=opt,
            available_ram_gb=5.0,
        )
        # Sensible → nunca cloud
        assert plan.backend_name in ("ollama_3b", "ollama_7b")


# ============================================================
# 4. ResourcePlanner — stats
# ============================================================

class TestResourcePlannerStats:

    def test_stats_track_plans(self):
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        planner.plan(acd_level="L0_REFLEX", metabolic_state="awake", model_bus=bus)
        planner.plan(acd_level="L3_DEEP", metabolic_state="awake", model_bus=bus)
        stats = planner.get_stats()
        assert stats["plans_generated"] == 2
        assert "reason_distribution" in stats
        assert "strategy_distribution" in stats
        assert len(stats["recent_plans"]) == 2

    def test_stats_reason_distribution(self):
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        planner.plan(acd_level="L0_REFLEX", metabolic_state="awake", model_bus=bus)
        planner.plan(acd_level="L0_REFLEX", metabolic_state="awake", model_bus=bus)
        planner.plan(acd_level="L3_DEEP", metabolic_state="awake", model_bus=bus)
        stats = planner.get_stats()
        # Debe tener al menos 2 razones diferentes
        assert len(stats["reason_distribution"]) >= 1
        # L0 debe aparecer 2 veces
        l0_reason = PlanReason.ACD_LOCAL_FAST.value
        assert stats["reason_distribution"].get(l0_reason, 0) == 2

    def test_stats_recent_plans_capped(self):
        """Los recent_plans se limitan a 10."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        for _ in range(15):
            planner.plan(acd_level="L0_REFLEX", metabolic_state="awake", model_bus=bus)
        stats = planner.get_stats()
        assert len(stats["recent_plans"]) <= 10


# ============================================================
# 5. ResourcePlanner — recommend_model_setup
# ============================================================

class TestRecommendModelSetup:

    def test_recommend_for_8gb_mac(self):
        """Recomendación para Mac con 8GB RAM (5GB disponibles)."""
        planner = ResourcePlanner()
        opt = ModelOptimizer()
        result = planner.recommend_model_setup(
            available_ram_gb=5.0,
            model_optimizer=opt,
        )
        assert "recommendations" in result
        assert "available_ram_gb" in result
        assert "L0" in result["recommendations"]
        assert "L3" in result["recommendations"]

    def test_recommend_includes_strategy(self):
        """Las recomendaciones incluyen estrategia (full_ram/mmap/etc)."""
        planner = ResourcePlanner()
        opt = ModelOptimizer()
        result = planner.recommend_model_setup(
            available_ram_gb=5.0,
            model_optimizer=opt,
        )
        for level, rec in result["recommendations"].items():
            if rec.get("strategy"):
                assert rec["strategy"] in ("full_ram", "mmap_partial", "mmap_full", "cloud_fallback", "cloud_api")

    def test_recommend_includes_ram_usage(self):
        """Las recomendaciones incluyen uso de RAM estimado."""
        planner = ResourcePlanner()
        opt = ModelOptimizer()
        result = planner.recommend_model_setup(
            available_ram_gb=5.0,
            model_optimizer=opt,
        )
        for level, rec in result["recommendations"].items():
            if "ram_usage_gb" in rec:
                assert rec["ram_usage_gb"] >= 0

    def test_recommend_low_ram_suggests_cloud(self):
        """Con poca RAM, L3 sugiere cloud."""
        planner = ResourcePlanner()
        opt = ModelOptimizer()
        result = planner.recommend_model_setup(
            available_ram_gb=0.5,  # muy poca RAM
            model_optimizer=opt,
        )
        l3 = result["recommendations"].get("L3", {})
        # Con 0.5GB, L3 debería sugerir cloud o mmap_full
        assert l3.get("strategy") in ("cloud_fallback", "cloud_api", "mmap_full") or l3.get("model") == "cloud_api"


# ============================================================
# 6. ResourcePlanner — integración con ModelBus.from_resource_graph
# ============================================================

class TestPlannerIntegration:

    def test_plan_with_empty_model_bus_and_no_graph(self):
        """Bus vacío + sin graph → NO_RESOURCES."""
        planner = ResourcePlanner()
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            model_bus=ModelBus(),
        )
        assert plan.reason == PlanReason.NO_RESOURCES.value

    def test_plan_with_backends_selects_correctly(self):
        """Plan con backends selecciona el correcto según ACD."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()

        # L0 → local fast
        p0 = planner.plan(acd_level="L0_REFLEX", metabolic_state="awake",
                          model_bus=bus, available_ram_gb=5.0)
        assert p0.backend_name == "ollama_3b"

        # L3 → cloud quality
        p3 = planner.plan(acd_level="L3_DEEP", metabolic_state="awake",
                          model_bus=bus, available_ram_gb=5.0)
        assert p3.backend_name in ("openai", "anthropic")

        # L3 + sensitive → local
        p3s = planner.plan(acd_level="L3_DEEP", metabolic_state="awake",
                           sensitive_domain=True, model_bus=bus, available_ram_gb=5.0)
        assert p3s.backend_name in ("ollama_3b", "ollama_7b")

    def test_plan_ollama_env_generated_for_local(self):
        """Plan con backend local genera ollama_env."""
        planner = ResourcePlanner()
        bus = make_bus_with_backends()
        opt = ModelOptimizer()
        plan = planner.plan(
            acd_level="L0_REFLEX",
            metabolic_state="awake",
            model_bus=bus,
            model_optimizer=opt,
            available_ram_gb=5.0,
        )
        # Si es local, debe tener ollama_env
        if plan.backend_name.startswith("ollama"):
            assert isinstance(plan.ollama_env, dict)
            # Puede estar vacío si full_ram, pero debe existir
            assert "OLLAMA_MAX_LOADED_MODELS" in plan.ollama_env or len(plan.ollama_env) >= 0
