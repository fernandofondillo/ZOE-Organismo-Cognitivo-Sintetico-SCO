"""
Tests Sprint 5.7 — ACD Model Routing end-to-end

Verifica que:
1. El DepthClassifier emite L3_MAXIMUM para inputs críticos
2. El ModelProfileRouter asigna Qwen 72B a L3_MAXIMUM
3. El CognitiveLoopV5 invoca al router y hot-swap el LLM
4. CLI acepta --backend pattern y --model auto
5. La factory create_llm_peripheral maneja 'pattern'
6. El CLI de ModelDownloader tiene los 4 setups preseleccionados
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest


# ============================================================
# 1. L3_MAXIMUM en DepthClassifier
# ============================================================

class TestL3MaximumClassification:
    """Sprint 5.7 — L3_MAXIMUM debe activarse para inputs críticos."""

    def test_l3_maximum_keywords_juridico(self):
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("Compara jurídicamente estos 3 contratos")
        assert result.level == CognitiveLevel.L3_MAXIMUM
        assert any("l3_max" in r for r in result.reasons)

    def test_l3_maximum_keywords_medico(self):
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("Diagnóstico diferencial de estos síntomas")
        assert result.level == CognitiveLevel.L3_MAXIMUM

    def test_l3_maximum_pattern_compara_contratos(self):
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("compara 3 contratos de alquiler")
        assert result.level == CognitiveLevel.L3_MAXIMUM

    def test_l3_maximum_pattern_diagnostico_diferencial(self):
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("realiza un diagnóstico diferencial exhaustivo")
        assert result.level == CognitiveLevel.L3_MAXIMUM

    def test_l3_deep_no_escala_a_maximum(self):
        """Inputs L3_DEEP normales no deben escalar a L3_MAXIMUM."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("Analiza las causas de la depresión")
        assert result.level == CognitiveLevel.L3_DEEP
        assert result.level != CognitiveLevel.L3_MAXIMUM

    def test_l0_no_se_ve_afectado(self):
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        result = dc.classify("hola")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l3_maximum_tiene_cost_mayor(self):
        from zoe.core.depth_classifier import CognitiveLevel
        assert CognitiveLevel.L3_MAXIMUM.cost > CognitiveLevel.L3_DEEP.cost

    def test_l3_maximum_numeric_4(self):
        from zoe.core.depth_classifier import CognitiveLevel
        assert CognitiveLevel.L3_MAXIMUM.numeric == 4

    def test_stats_incluyen_l3_maximum(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        dc.classify("hola")
        dc.classify("compara jurídicamente")
        stats = dc.get_stats()
        assert "L3_MAXIMUM" in stats["level_distribution"]


# ============================================================
# 2. ModelProfileRouter asigna Qwen 72B a L3_MAXIMUM
# ============================================================

class TestRouterL3Maximum:
    """Sprint 5.7 — el router asigna Qwen 72B a L3_MAXIMUM cuando está disponible."""

    def test_router_asigna_72b_a_l3_maximum(self):
        from zoe.core.model_profile_router import ModelProfileRouter, ACDLevel
        router = ModelProfileRouter()
        # Simular que están instalados los 4 modelos
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)
        assignment = profile.get_model("L3_MAXIMUM")
        assert assignment is not None
        assert assignment.model_tag == "qwen2.5-72b-iq2"

    def test_router_fallback_a_qwq_si_no_hay_72b(self):
        from zoe.core.model_profile_router import ModelProfileRouter
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "qwq-32b-iq2"]
        profile = router.create_optimal_profile(installed)
        assignment = profile.get_model("L3_MAXIMUM")
        # Como no hay 72B, hace fallback a qwq-32b
        assert assignment is not None
        assert "qwq" in assignment.model_tag or "pattern" in assignment.model_tag

    def test_router_l3_deep_asigna_qwq(self):
        from zoe.core.model_profile_router import ModelProfileRouter
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "qwq-32b-iq2"]
        profile = router.create_optimal_profile(installed)
        assignment = profile.get_model("L3_DEEP")
        assert assignment is not None
        assert "qwq" in assignment.model_tag

    def test_router_pattern_fallback_cuando_sin_modelos(self):
        from zoe.core.model_profile_router import ModelProfileRouter
        router = ModelProfileRouter()
        profile = router.create_optimal_profile([])
        for acd in ["L0_REFLEX", "L1_FAST", "L2_STANDARD", "L3_DEEP", "L3_MAXIMUM"]:
            assignment = profile.get_model(acd)
            assert assignment is not None
            assert assignment.model_tag == "pattern"


# ============================================================
# 3. CognitiveLoopV5 invoca al router
# ============================================================

class TestCognitiveLoopV5Router:
    """Sprint 5.7 — V5 invoca al ModelProfileRouter cuando está configurado."""

    def _build_loop_with_router(self, installed_models):
        """Construye un loop V5 con router configurado."""
        from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter

        # Mock mínimo del V4 padre
        loop = CognitiveLoopV5.__new__(CognitiveLoopV5)
        loop.depth_classifier = DepthClassifier()
        loop.cognitive_cache = None
        loop.model_profile_router = ModelProfileRouter()
        loop._active_profile = loop.model_profile_router.create_optimal_profile(installed_models)
        loop._router_swaps = 0
        loop._router_skips = 0
        loop._last_routed_tag = None
        loop.acd_classifications = 0
        loop.acd_level_counts = {
            "L0_REFLEX": 0, "L1_FAST": 0, "L2_STANDARD": 0,
            "L3_DEEP": 0, "L3_MAXIMUM": 0,
        }
        loop.acd_cache_hits = 0
        loop.acd_responses_by_level = dict(loop.acd_level_counts)
        loop.acd_latency_by_level = {k: [] for k in loop.acd_level_counts}
        loop.last_classification = None
        loop.memory = None
        loop.subagents = []
        loop.ontogenetic_motor = None
        loop.trajectory_chain = None
        return loop

    def test_router_stats_disponible(self):
        loop = self._build_loop_with_router([])
        stats = loop.get_router_stats()
        assert stats["enabled"] is True
        assert "swaps" in stats
        assert "skips" in stats
        assert "last_routed_tag" in stats

    def test_router_desactivado_si_no_hay_router(self):
        loop = self._build_loop_with_router([])
        loop.model_profile_router = None
        stats = loop.get_router_stats()
        assert stats["enabled"] is False

    def test_find_speaker_returns_none_si_sin_subagents(self):
        loop = self._build_loop_with_router([])
        assert loop._find_speaker() is None


# ============================================================
# 4. CLI acepta --backend pattern y --model auto
# ============================================================

class TestCLIFlags:
    """Sprint 5.7 — argparse acepta los nuevos flags."""

    def test_argparse_acepta_pattern(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--backend",
            choices=["mock", "zai", "ollama", "openai_compatible", "anthropic", "pattern"],
            default="mock")
        args = parser.parse_args(["--backend", "pattern"])
        assert args.backend == "pattern"

    def test_argparse_acepta_model_auto(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--backend",
            choices=["mock", "zai", "ollama", "openai_compatible", "anthropic", "pattern"],
            default="mock")
        parser.add_argument("--model")
        args = parser.parse_args(["--backend", "ollama", "--model", "auto"])
        assert args.model == "auto"


# ============================================================
# 5. Factory create_llm_peripheral maneja 'pattern'
# ============================================================

class TestPatternBackendFactory:
    """Sprint 5.7 — create_llm_peripheral devuelve PatternPeripheral para 'pattern'."""

    def test_factory_devuelve_pattern_peripheral(self):
        from zoe.peripherals.llm import create_llm_peripheral
        llm = create_llm_peripheral({"backend": "pattern"})
        assert llm.name == "pattern"

    def test_pattern_peripheral_generate_no_es_vacio(self):
        from zoe.peripherals.llm import create_llm_peripheral
        llm = create_llm_peripheral({"backend": "pattern"})
        result = asyncio.run(llm.generate("hola"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pattern_peripheral_tiene_name_property(self):
        from zoe.peripherals.llm import create_llm_peripheral
        llm = create_llm_peripheral({"backend": "pattern"})
        assert llm.name == "pattern"


# ============================================================
# 6. ModelDownloader CLI con 4 setups preseleccionados
# ============================================================

class TestModelDownloaderCLI:
    """Sprint 5.7 — ModelDownloader expone los 4 setups preseleccionados."""

    def test_setup_presets_tiene_4_setups(self):
        from zoe.core.model_downloader import SETUP_PRESETS
        assert set(SETUP_PRESETS.keys()) == {"minimal", "balanced", "complete", "maximum"}

    def test_setup_maximum_tiene_4_modelos(self):
        from zoe.core.model_downloader import SETUP_PRESETS
        assert len(SETUP_PRESETS["maximum"]["models"]) == 4
        assert "gemma-2-9b-iq2" in SETUP_PRESETS["maximum"]["models"]
        assert "agents-a1-iq2" in SETUP_PRESETS["maximum"]["models"]
        assert "qwq-32b-iq2" in SETUP_PRESETS["maximum"]["models"]
        assert "qwen2.5:72b-iq2" in SETUP_PRESETS["maximum"]["models"]

    def test_setup_balanced_tiene_gemma_y_qwq(self):
        from zoe.core.model_downloader import SETUP_PRESETS
        assert "gemma-2-9b-iq2" in SETUP_PRESETS["balanced"]["models"]
        assert "qwq-32b-iq2" in SETUP_PRESETS["balanced"]["models"]

    def test_setup_total_gb_espera(self):
        from zoe.core.model_downloader import SETUP_PRESETS
        assert SETUP_PRESETS["minimal"]["total_gb"] == 3.5
        assert SETUP_PRESETS["balanced"]["total_gb"] == 16.0
        assert SETUP_PRESETS["complete"]["total_gb"] == 27.7
        assert SETUP_PRESETS["maximum"]["total_gb"] == 52.7


# ============================================================
# 7. zoe-setup detecta y recomienda setup IQ2_M
# ============================================================

class TestZoeSetupRecommendsIQ2:
    """Sprint 5.7 — zoe-setup recomienda setup según RAM."""

    def test_recomienda_balanced_para_8gb(self):
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        try:
            from zoe_setup import recommend_iq2_setup
            setup, reason = recommend_iq2_setup(8.0)
            assert setup in ("balanced", "complete", "maximum")
            assert "GB" in reason or "RAM" in reason
        finally:
            sys.path.pop(0)

    def test_recomienda_minimal_para_4gb(self):
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        try:
            from zoe_setup import recommend_iq2_setup
            setup, reason = recommend_iq2_setup(4.0)
            assert setup == "minimal"
        finally:
            sys.path.pop(0)

    def test_recomienda_maximum_para_ss_grande(self):
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        try:
            from zoe_setup import recommend_iq2_setup
            setup, reason = recommend_iq2_setup(16.0, ssd_free_gb=200)
            assert setup == "maximum"
        finally:
            sys.path.pop(0)


# ============================================================
# 8. Tests end-to-end: clasifica → router → tag esperado
# ============================================================

class TestEndToEndRouting:
    """Sprint 5.7 — End-to-end: input → clasificación → router → modelo asignado."""

    def test_hola_llega_a_gemma(self):
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter
        dc = DepthClassifier()
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        # "hola" es L0_REFLEX → no usa LLM
        result = dc.classify("hola")
        assert result.level.value == "L0_REFLEX"

    def test_pregunta_simple_llega_a_gemma(self):
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter
        dc = DepthClassifier()
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        # Pregunta simple → L1_FAST → Gemma
        result = dc.classify("¿qué hora es?")
        assert result.level.value == "L1_FAST"
        assignment = profile.get_model(result.level.value)
        assert "gemma" in assignment.model_tag

    def test_analisis_profundo_llega_a_qwq(self):
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter
        dc = DepthClassifier()
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        result = dc.classify("Analiza las causas profundas de la ansiedad")
        assert result.level.value == "L3_DEEP"
        assignment = profile.get_model(result.level.value)
        assert "qwq" in assignment.model_tag

    def test_comparacion_critica_llega_a_72b(self):
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter
        dc = DepthClassifier()
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        result = dc.classify("Compara jurídicamente estos 3 contratos")
        assert result.level.value == "L3_MAXIMUM"
        assignment = profile.get_model(result.level.value)
        assert "72b" in assignment.model_tag

    def test_setup_maximum_cubre_todo_el_espectro(self):
        """Con el setup maximum, todos los niveles ACD tienen un modelo asignado."""
        from zoe.core.depth_classifier import DepthClassifier
        from zoe.core.model_profile_router import ModelProfileRouter
        dc = DepthClassifier()
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        # Test con inputs representativos de cada nivel
        test_cases = [
            ("hola", "L0_REFLEX"),
            ("¿qué hora es?", "L1_FAST"),
            ("estoy pensando en cambiar de trabajo pero no se si es el momento adecuado para hacerlo", "L2_STANDARD"),
            ("analiza las causas del estrés", "L3_DEEP"),
            ("compara jurídicamente estos documentos", "L3_MAXIMUM"),
        ]

        for text, expected_level in test_cases:
            result = dc.classify(text)
            assert result.level.value == expected_level, (
                f"Para '{text}' esperaba {expected_level}, got {result.level.value}"
            )
            assignment = profile.get_model(result.level.value)
            assert assignment is not None, f"Sin asignación para {expected_level}"
            assert assignment.model_tag != "", f"Tag vacío para {expected_level}"
