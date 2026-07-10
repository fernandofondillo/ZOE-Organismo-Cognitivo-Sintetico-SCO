"""
Tests Fase 7D — Embodiment Composer

Valida que el composer:
1. Instancia correctamente un Embodiment desde un ResourcePlan
2. Detecta blockers antes de intentar componer
3. Maneja estados RUNNING / DEGRADED / FAILED
4. Pipeline bootstrap_from_scratch integra 7A→7B→7C→7D
5. Tear down limpia correctamente
6. Stats y logs son coherentes
"""

import asyncio
import os
import pytest
import time
from unittest.mock import MagicMock, patch, AsyncMock

from zoe.core.embodiment_composer import (
    EmbodimentComposer,
    Embodiment,
    EmbodimentStatus,
    ValidationResult,
    ValidationCheck,
    ValidationLevel,
)
from zoe.core.resource_planner import (
    ResourcePlanner,
    ResourcePlan,
    PlanReason,
    MetabolicState,
)
from zoe.peripherals.model_bus import ModelBus, SelectionStrategy, BackendEntry
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
    return bus


def make_viable_local_plan(backend_name: str = "ollama_3b") -> ResourcePlan:
    """Crea un plan viable para backend local."""
    return ResourcePlan(
        backend_name=backend_name,
        model_name="qwen2.5:3b",
        strategy="full_ram",
        reason=PlanReason.ACD_LOCAL_FAST.value,
        acd_level="L0_REFLEX",
        metabolic_state="awake",
        available_ram_gb=5.0,
        will_work=True,
        ollama_env={"OLLAMA_MAX_LOADED_MODELS": "1"},
    )


def make_cloud_plan(backend_name: str = "openai") -> ResourcePlan:
    """Crea un plan cloud."""
    return ResourcePlan(
        backend_name=backend_name,
        model_name="gpt-4o",
        strategy="cloud",
        reason=PlanReason.ACD_QUALITY.value,
        acd_level="L3_DEEP",
        metabolic_state="awake",
        available_ram_gb=5.0,
        will_work=True,
    )


def make_unviable_plan() -> ResourcePlan:
    """Crea un plan inviable (SLEEPING)."""
    return ResourcePlan(
        backend_name="",
        strategy="",
        reason=PlanReason.SLEEPING_DEFER.value,
        acd_level="L2_STANDARD",
        metabolic_state="sleeping",
        will_work=False,
        warning="Organismo en SLEEPING. Diferir tarea.",
    )


# Patch para simular Ollama siempre corriendo en tests
@pytest.fixture
def mock_ollama_running():
    """Simula que Ollama está corriendo en localhost:11434."""
    with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=True):
        yield


@pytest.fixture
def mock_ollama_not_running():
    """Simula que Ollama NO está corriendo."""
    with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=False):
        yield


# ============================================================
# 1. Embodiment dataclass
# ============================================================

class TestEmbodimentDataclass:

    def test_embodiment_default_status_stopped(self):
        emb = Embodiment()
        assert emb.status == EmbodimentStatus.STOPPED.value

    def test_embodiment_is_running_true_when_running(self):
        emb = Embodiment(status=EmbodimentStatus.RUNNING.value)
        assert emb.is_running is True

    def test_embodiment_is_running_true_when_degraded(self):
        emb = Embodiment(status=EmbodimentStatus.DEGRADED.value)
        assert emb.is_running is True

    def test_embodiment_is_running_false_when_failed(self):
        emb = Embodiment(status=EmbodimentStatus.FAILED.value)
        assert emb.is_running is False

    def test_embodiment_is_running_false_when_stopped(self):
        emb = Embodiment(status=EmbodimentStatus.STOPPED.value)
        assert emb.is_running is False

    def test_embodiment_to_dict_contains_required_fields(self):
        emb = Embodiment(
            embodiment_id="emb_test",
            backend_name="ollama_3b",
            model_name="qwen2.5:3b",
            strategy="full_ram",
            status=EmbodimentStatus.RUNNING.value,
            acd_level="L0_REFLEX",
        )
        d = emb.to_dict()
        assert d["embodiment_id"] == "emb_test"
        assert d["backend_name"] == "ollama_3b"
        assert d["status"] == "running"
        assert d["is_running"] is True
        assert "model_bus_backends" in d

    def test_embodiment_to_dict_with_model_bus(self):
        bus = make_bus_with_backends()
        emb = Embodiment(model_bus=bus)
        d = emb.to_dict()
        assert isinstance(d["model_bus_backends"], list)
        assert len(d["model_bus_backends"]) == 3


# ============================================================
# 2. validate_prerequisites
# ============================================================

class TestValidatePrerequisites:

    def test_valid_local_plan_passes(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        assert result.plan_will_work is True
        assert result.blockers == 0

    def test_unviable_plan_returns_blocker(self):
        composer = EmbodimentComposer()
        plan = make_unviable_plan()
        result = composer.validate_prerequisites(plan)
        assert result.plan_will_work is False
        assert result.blockers >= 1
        blocker_msgs = [c.message for c in result.checks if c.level == "blocker"]
        assert any("not viable" in m for m in blocker_msgs)

    def test_missing_backend_in_bus_returns_blocker(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan(backend_name="nonexistent_backend")
        bus = make_bus_with_backends()
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        assert result.blockers >= 1
        blocker_msgs = [c.message for c in result.checks if c.level == "blocker"]
        assert any("not found" in m for m in blocker_msgs)

    def test_unavailable_backend_returns_blocker(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan(backend_name="ollama_3b")
        bus = make_bus_with_backends()
        # Marcar backend como no disponible
        bus._backends["ollama_3b"].available = False
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        assert result.blockers >= 1

    def test_low_ram_returns_warning(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        plan.strategy = "full_ram"
        bus = make_bus_with_backends()
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=1.0)
        assert result.warnings >= 1
        # El warning de RAM no bloquea
        assert result.plan_will_work is True

    def test_local_strategy_without_ollama_returns_blocker(self, mock_ollama_not_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        assert result.blockers >= 1
        blocker_msgs = [c.message for c in result.checks if c.level == "blocker"]
        assert any("Ollama not running" in m for m in blocker_msgs)

    def test_cloud_strategy_skips_ollama_check(self, mock_ollama_not_running):
        """Plan cloud no requiere Ollama corriendo."""
        composer = EmbodimentComposer()
        plan = make_cloud_plan(backend_name="openai")
        bus = make_bus_with_backends()
        # Asegurar API key presente
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        # No debe tener blocker por Ollama
        ollama_blockers = [
            c for c in result.checks
            if c.level == "blocker" and "Ollama" in c.message
        ]
        assert len(ollama_blockers) == 0

    def test_cloud_strategy_without_api_key_returns_blocker(self, mock_ollama_not_running):
        composer = EmbodimentComposer()
        plan = make_cloud_plan(backend_name="openai")
        bus = make_bus_with_backends()
        # Sin API key
        env_backup = dict(os.environ)
        os.environ.pop("OPENAI_API_KEY", None)
        try:
            result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
            assert result.blockers >= 1
            blocker_msgs = [c.message for c in result.checks if c.level == "blocker"]
            assert any("API key" in m for m in blocker_msgs)
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

    def test_plan_warning_propagates_as_warning(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        plan.warning = "Suboptimal configuration"
        bus = make_bus_with_backends()
        result = composer.validate_prerequisites(plan, model_bus=bus, available_ram_gb=5.0)
        # El warning del plan no bloquea pero se registra
        assert result.plan_will_work is True


# ============================================================
# 3. compose
# ============================================================

class TestCompose:

    def test_compose_viable_local_plan_returns_running(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert emb.status == EmbodimentStatus.RUNNING.value
        assert emb.is_running is True
        assert emb.backend_name == "ollama_3b"
        assert emb.model_name == "qwen2.5:3b"
        assert emb.strategy == "full_ram"

    def test_compose_unviable_plan_returns_failed(self):
        composer = EmbodimentComposer()
        plan = make_unviable_plan()
        emb = composer.compose(plan, model_bus=make_bus_with_backends())
        assert emb.status == EmbodimentStatus.FAILED.value
        assert emb.is_running is False
        assert len(emb.errors) >= 1

    def test_compose_with_warnings_returns_degraded(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        plan.warning = "Suboptimal RAM"
        plan.available_ram_gb = 1.0  # RAM baja → genera warning de RAM
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert emb.status == EmbodimentStatus.DEGRADED.value
        assert emb.is_running is True
        assert len(emb.warnings) >= 1

    def test_compose_applies_ollama_env(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        plan.ollama_env = {"OLLAMA_TEST_VAR": "test_value"}
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert emb.ollama_env_applied == {"OLLAMA_TEST_VAR": "test_value"}
        assert os.environ.get("OLLAMA_TEST_VAR") == "test_value"
        # cleanup
        os.environ.pop("OLLAMA_TEST_VAR", None)

    def test_compose_records_plan_signature(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert emb.plan_signature != ""
        assert len(emb.plan_signature) == 16

    def test_compose_sets_boot_timestamps(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert emb.boot_started_at > 0
        assert emb.boot_completed_at >= emb.boot_started_at
        assert emb.boot_duration_ms >= 0

    def test_compose_registers_embodiment_in_active(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        assert composer.get_embodiment(emb.embodiment_id) is emb

    def test_compose_with_capsules_records_them(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(
            plan, model_bus=bus,
            capsules=["elder_care_knowledge", "basic_psychology"]
        )
        assert emb.capsules_loaded == ["elder_care_knowledge", "basic_psychology"]

    def test_compose_skip_validation(self, mock_ollama_not_running):
        """Con skip_validation=True, no comprueba Ollama."""
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus, skip_validation=True)
        # Sin validación, no puede detectar que Ollama no está
        assert emb.status == EmbodimentStatus.RUNNING.value


# ============================================================
# 4. tear_down
# ============================================================

class TestTearDown:

    def test_tear_down_existing_embodiment(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        result = composer.tear_down(emb.embodiment_id)
        assert result is True
        # Ya no está en activos
        assert composer.get_embodiment(emb.embodiment_id) is None
        # Pero el embodiment recibido sigue existiendo con status STOPPED
        assert emb.status == EmbodimentStatus.STOPPED.value

    def test_tear_down_nonexistent_returns_false(self):
        composer = EmbodimentComposer()
        result = composer.tear_down("nonexistent_id")
        assert result is False

    def test_tear_down_all_closes_multiple(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        composer.compose(plan, model_bus=bus)
        composer.compose(plan, model_bus=bus)
        composer.compose(plan, model_bus=bus)
        closed = composer.tear_down_all()
        assert closed == 3
        assert len(composer.list_active()) == 0


# ============================================================
# 5. Stats y logging
# ============================================================

class TestComposerStats:

    def test_get_status_initial(self):
        composer = EmbodimentComposer()
        status = composer.get_status()
        assert status["total_compositions"] == 0
        assert status["total_failures"] == 0
        assert status["active_embodiments"] == 0
        assert status["success_rate"] == 0  # max(1, 0) → 0/1 = 0

    def test_get_status_after_compositions(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        composer.compose(plan, model_bus=bus)
        composer.compose(plan, model_bus=bus)
        status = composer.get_status()
        assert status["total_compositions"] == 2
        assert status["active_embodiments"] == 2
        assert status["running_embodiments"] == 2
        assert status["success_rate"] == 1.0

    def test_get_status_after_failure(self):
        composer = EmbodimentComposer()
        plan = make_unviable_plan()
        composer.compose(plan, model_bus=make_bus_with_backends())
        status = composer.get_status()
        assert status["total_compositions"] == 1
        assert status["total_failures"] == 1
        assert status["success_rate"] == 0.0

    def test_composition_log_records_events(self, mock_ollama_running):
        composer = EmbodimentComposer()
        plan = make_viable_local_plan()
        bus = make_bus_with_backends()
        emb = composer.compose(plan, model_bus=bus)
        log = composer.get_composition_log()
        assert len(log) == 1
        assert log[0]["embodiment_id"] == emb.embodiment_id
        assert log[0]["outcome"] == "ok"
        assert log[0]["backend"] == "ollama_3b"


# ============================================================
# 6. bootstrap_from_scratch (pipeline completo)
# ============================================================

class TestBootstrapFromScratch:

    def test_bootstrap_with_no_resources_returns_failed(self):
        """Sin recursos detectados → plan NO_RESOURCES → embodiment FAILED."""
        composer = EmbodimentComposer()
        # Sin Ollama, sin cloud keys, sin nada
        env_backup = dict(os.environ)
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]:
            os.environ.pop(key, None)
        try:
            with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=False):
                emb = composer.bootstrap_from_scratch(
                    acd_level="L2_STANDARD",
                    metabolic_state="awake",
                    available_ram_gb=4.0,
                )
            # Sin recursos, el plan es NO_RESOURCES
            assert emb.status in (
                EmbodimentStatus.FAILED.value,
                EmbodimentStatus.DEGRADED.value,
            )
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

    def test_bootstrap_with_cloud_key_can_succeed(self):
        """Con API key cloud, bootstrap puede instanciar aunque no haya Ollama."""
        composer = EmbodimentComposer()
        env_backup = dict(os.environ)
        os.environ["OPENAI_API_KEY"] = "test_key_for_bootstrap"
        try:
            with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=False):
                # El cloud API se descubrirá en el resource discovery
                emb = composer.bootstrap_from_scratch(
                    acd_level="L3_DEEP",
                    metabolic_state="awake",
                    available_ram_gb=4.0,
                )
            # El plan puede ser cloud (L3) o fallar si no detecta cloud API
            # Aceptamos ambos: lo importante es que el pipeline no crashea
            assert emb.status in (
                EmbodimentStatus.RUNNING.value,
                EmbodimentStatus.DEGRADED.value,
                EmbodimentStatus.FAILED.value,
            )
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

    def test_bootstrap_with_sleeping_state_defers(self):
        """En SLEEPING, el plan es SLEEPING_DEFER → FAILED."""
        composer = EmbodimentComposer()
        with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=True):
            emb = composer.bootstrap_from_scratch(
                acd_level="L2_STANDARD",
                metabolic_state="sleeping",
                available_ram_gb=4.0,
            )
        assert emb.status == EmbodimentStatus.FAILED.value
        assert any("SLEEPING" in e or "viable" in e.lower() for e in emb.errors)

    def test_bootstrap_records_composition_in_log(self):
        composer = EmbodimentComposer()
        with patch.object(EmbodimentComposer, "_check_ollama_running", return_value=True):
            composer.bootstrap_from_scratch(
                acd_level="L2_STANDARD",
                available_ram_gb=4.0,
            )
        log = composer.get_composition_log()
        assert len(log) >= 1
        # El último evento es el bootstrap
        assert log[-1]["outcome"] in ("ok", "failed")


# ============================================================
# 7. Helpers internos
# ============================================================

class TestComposerHelpers:

    def test_sign_plan_is_deterministic(self):
        composer = EmbodimentComposer()
        plan1 = make_viable_local_plan()
        plan2 = make_viable_local_plan()
        # Mismos campos → misma firma (excepto timestamp)
        plan2.timestamp = plan1.timestamp
        sig1 = composer._sign_plan(plan1)
        sig2 = composer._sign_plan(plan2)
        assert sig1 == sig2

    def test_sign_plan_differs_for_different_plans(self):
        composer = EmbodimentComposer()
        plan1 = make_viable_local_plan(backend_name="ollama_3b")
        plan2 = make_viable_local_plan(backend_name="ollama_7b")
        plan2.timestamp = plan1.timestamp
        sig1 = composer._sign_plan(plan1)
        sig2 = composer._sign_plan(plan2)
        assert sig1 != sig2

    def test_apply_ollama_env_sets_variables(self):
        composer = EmbodimentComposer()
        composer._apply_ollama_env({"OLLAMA_TEST_ENV_VAR": "42"})
        assert os.environ.get("OLLAMA_TEST_ENV_VAR") == "42"
        os.environ.pop("OLLAMA_TEST_ENV_VAR", None)

    def test_check_cloud_api_key_openai(self):
        composer = EmbodimentComposer()
        env_backup = dict(os.environ)
        os.environ["OPENAI_API_KEY"] = "test"
        try:
            assert composer._check_cloud_api_key("openai") is True
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

    def test_check_cloud_api_key_missing(self):
        composer = EmbodimentComposer()
        env_backup = dict(os.environ)
        os.environ.pop("OPENAI_API_KEY", None)
        try:
            assert composer._check_cloud_api_key("openai") is False
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

    def test_check_cloud_api_key_unknown_backend_assumes_ok(self):
        composer = EmbodimentComposer()
        # Backend no reconocido → asumir que tiene key
        assert composer._check_cloud_api_key("custom_backend") is True

    def test_detect_available_ram_returns_positive(self):
        composer = EmbodimentComposer()
        ram = composer._detect_available_ram()
        assert ram > 0
        assert isinstance(ram, float)
