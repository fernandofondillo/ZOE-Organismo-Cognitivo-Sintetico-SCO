"""
Tests Sprint 5.6 — Model Profile Router

Valida que ZOE asigna el modelo correcto a cada nivel ACD.
"""

import pytest
from zoe.core.model_profile_router import (
    ModelProfileRouter, ModelProfile, ModelAssignment,
    ACDLevel,
)


# ============================================================
# 1. ModelProfileRouter — creación
# ============================================================

class TestRouterCreation:

    def test_creation(self):
        router = ModelProfileRouter()
        assert router is not None

    def test_default_assignments_exist(self):
        """Tiene asignaciones por defecto para todos los ACD levels."""
        router = ModelProfileRouter()
        assert "L0_REFLEX" in router.DEFAULT_ASSIGNMENTS
        assert "L1_FAST" in router.DEFAULT_ASSIGNMENTS
        assert "L2_STANDARD" in router.DEFAULT_ASSIGNMENTS
        assert "L3_DEEP" in router.DEFAULT_ASSIGNMENTS
        assert "L3_MAXIMUM" in router.DEFAULT_ASSIGNMENTS

    def test_fallback_chains_exist(self):
        """Tiene cadenas de fallback para todos los ACD levels."""
        router = ModelProfileRouter()
        for acd in ACDLevel:
            assert acd.value in router.FALLBACK_CHAINS
            assert "pattern" in router.FALLBACK_CHAINS[acd.value]


# ============================================================
# 2. Perfil sin modelos (PatternSpeaker)
# ============================================================

class TestPatternOnlyProfile:

    def test_no_models_creates_pattern_profile(self):
        """Sin modelos, todo va a PatternSpeaker."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(installed_models=[])
        assert profile.name == "pattern_only"
        
        for acd in ACDLevel:
            assignment = profile.get_model(acd.value)
            assert assignment.model_tag == "pattern"

    def test_pattern_profile_get_model(self):
        """get_model devuelve PatternSpeaker para todos los niveles."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(installed_models=[])
        
        model = profile.get_model("L0_REFLEX")
        assert model.model_tag == "pattern"
        
        model = profile.get_model("L3_DEEP")
        assert model.model_tag == "pattern"


# ============================================================
# 3. Perfil con 4 modelos (espectro completo)
# ============================================================

class TestFullSpectrumProfile:

    def test_full_spectrum_profile(self):
        """Perfil de espectro completo con 4 modelos."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        assert profile.name == "full_spectrum"
        
        # L0 → Gemma 2 9B
        l0 = profile.get_model("L0_REFLEX")
        assert l0.model_key == "gemma-2-9b-iq2"
        
        # L1 → Gemma 2 9B
        l1 = profile.get_model("L1_FAST")
        assert l1.model_key == "gemma-2-9b-iq2"
        
        # L2 → Agents-A1 MoE
        l2 = profile.get_model("L2_STANDARD")
        assert l2.model_key == "agents-a1-iq2"
        
        # L3 → QwQ-32B
        l3 = profile.get_model("L3_DEEP")
        assert l3.model_key == "qwq-32b-iq2"
        
        # L3 máximo → Qwen 72B
        l3max = profile.get_model("L3_MAXIMUM")
        assert l3max.model_key == "qwen2.5:72b-iq2"

    def test_full_spectrum_covers_all_levels(self):
        """El perfil de espectro completo cubre todos los niveles."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        
        for acd in ACDLevel:
            assert acd.value in profile.assignments
            assert profile.assignments[acd.value].model_tag != ""


# ============================================================
# 4. Perfil con detección automática
# ============================================================

class TestAutoProfile:

    def test_auto_profile_with_gemma_only(self):
        """Con solo Gemma, todo va a Gemma."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(installed_models=["gemma-2-9b-iq2"])
        
        l0 = profile.get_model("L0_REFLEX")
        assert l0.model_key == "gemma-2-9b-iq2"
        
        l3 = profile.get_model("L3_DEEP")
        # Sin QwQ, L3 fallback a Gemma o pattern
        assert l3.model_key in ("gemma-2-9b-iq2", "pattern")

    def test_auto_profile_with_gemma_and_qwq(self):
        """Con Gemma + QwQ, L0 va a Gemma y L3 a QwQ."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(
            installed_models=["gemma-2-9b-iq2", "qwq-32b-iq2"]
        )
        
        l0 = profile.get_model("L0_REFLEX")
        assert l0.model_key == "gemma-2-9b-iq2"
        
        l3 = profile.get_model("L3_DEEP")
        assert l3.model_key == "qwq-32b-iq2"

    def test_auto_profile_full_spectrum(self):
        """Con los 4 modelos, asigna cada uno al nivel correcto."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(
            installed_models=[
                "gemma-2-9b-iq2",
                "agents-a1-iq2",
                "qwq-32b-iq2",
                "qwen2.5:72b-iq2",
            ]
        )
        
        assert profile.get_model("L0_REFLEX").model_key == "gemma-2-9b-iq2"
        assert profile.get_model("L1_FAST").model_key == "gemma-2-9b-iq2"
        assert profile.get_model("L2_STANDARD").model_key == "agents-a1-iq2"
        assert profile.get_model("L3_DEEP").model_key == "qwq-32b-iq2"
        assert profile.get_model("L3_MAXIMUM").model_key == "qwen2.5:72b-iq2"

    def test_auto_profile_fallback_when_preferred_missing(self):
        """Si el preferido no está, usa fallback de la cadena."""
        router = ModelProfileRouter()
        # Sin Gemma, sin Agents-A1, solo QwQ
        profile = router.create_optimal_profile(
            installed_models=["qwq-32b-iq2"]
        )
        
        # L0 sin Gemma → pattern
        l0 = profile.get_model("L0_REFLEX")
        assert l0.model_key == "pattern"
        
        # L3 con QwQ → QwQ
        l3 = profile.get_model("L3_DEEP")
        assert l3.model_key == "qwq-32b-iq2"

    def test_auto_profile_l3_maximum_fallback_to_l3_deep(self):
        """L3_MAXIMUM usa L3_DEEP si no hay 72B."""
        router = ModelProfileRouter()
        profile = router.create_optimal_profile(
            installed_models=["qwq-32b-iq2"]
        )
        
        # Sin 72B, L3_MAXIMUM debería usar QwQ (mismo que L3_DEEP)
        l3max = profile.get_model("L3_MAXIMUM")
        assert l3max.model_key == "qwq-32b-iq2"


# ============================================================
# 5. Recomendaciones de setup
# ============================================================

class TestRecommendedSetup:

    def test_get_recommended_setup(self):
        """get_recommended_setup devuelve dict con setups."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup()
        
        assert "minimal" in setups
        assert "balanced" in setups
        assert "complete" in setups
        assert "maximum" in setups

    def test_maximum_setup_has_4_models(self):
        """Setup máximo tiene 4 modelos."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup()
        
        maximum = setups["maximum"]
        assert len(maximum["models"]) == 4
        assert "gemma-2-9b-iq2" in maximum["models"]
        assert "agents-a1-iq2" in maximum["models"]
        assert "qwq-32b-iq2" in maximum["models"]
        assert "qwen2.5:72b-iq2" in maximum["models"]

    def test_maximum_setup_fits_1tb(self):
        """Setup máximo cabe en 1TB."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup(ssd_capacity_gb=1000)
        
        maximum = setups["maximum"]
        assert maximum["fits_in_ssd"] is True
        assert maximum["total_gb"] < 1000

    def test_maximum_setup_fits_128gb(self):
        """Setup máximo también cabe en 128GB."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup(ssd_capacity_gb=128)
        
        maximum = setups["maximum"]
        assert maximum["fits_in_ssd"] is True
        assert maximum["total_gb"] < 128

    def test_minimal_setup_fits_16gb(self):
        """Setup mínimo cabe en 16GB."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup(ssd_capacity_gb=16)
        
        minimal = setups["minimal"]
        assert minimal["fits_in_ssd"] is True

    def test_balanced_setup_has_2_models(self):
        """Setup equilibrado tiene 2 modelos."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup()
        
        balanced = setups["balanced"]
        assert len(balanced["models"]) == 2

    def test_complete_setup_has_3_models(self):
        """Setup completo tiene 3 modelos."""
        router = ModelProfileRouter()
        setups = router.get_recommended_setup()
        
        complete = setups["complete"]
        assert len(complete["models"]) == 3


# ============================================================
# 6. get_model_for_acd
# ============================================================

class TestGetModelForACD:

    def test_get_model_for_acd_with_profile(self):
        """get_model_for_acd devuelve modelo correcto."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        
        model = router.get_model_for_acd("L0_REFLEX", profile)
        assert model.model_key == "gemma-2-9b-iq2"
        
        model = router.get_model_for_acd("L3_DEEP", profile)
        assert model.model_key == "qwq-32b-iq2"

    def test_get_model_for_acd_without_profile(self):
        """get_model_for_acd sin perfil crea uno automáticamente."""
        router = ModelProfileRouter()
        router._installed_models = ["gemma-2-9b-iq2"]
        
        model = router.get_model_for_acd("L0_REFLEX")
        assert model.model_key == "gemma-2-9b-iq2"


# ============================================================
# 7. Stats
# ============================================================

class TestRouterStats:

    def test_get_stats(self):
        """get_stats devuelve dict con info."""
        router = ModelProfileRouter()
        stats = router.get_stats()
        assert "installed_models" in stats
        assert "profiles_created" in stats
        assert "available_catalog_models" in stats

    def test_stats_after_creating_profile(self):
        """Stats reflejan perfiles creados."""
        router = ModelProfileRouter()
        router.create_full_spectrum_profile()
        stats = router.get_stats()
        assert stats["profiles_created"] >= 1


# ============================================================
# 8. Integración
# ============================================================

class TestRouterIntegration:

    def test_all_acd_levels_have_assignments(self):
        """Todos los ACD levels tienen asignación en el perfil completo."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        
        for acd in ACDLevel:
            assert acd.value in profile.assignments
            assert profile.assignments[acd.value].model_tag != ""

    def test_model_assignment_has_reason(self):
        """Cada asignación tiene una razón."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        
        for acd in ACDLevel:
            assignment = profile.assignments[acd.value]
            assert assignment.reason != ""

    def test_profile_to_dict(self):
        """to_dict del perfil funciona."""
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        d = profile.to_dict()
        assert "name" in d
        assert "assignments" in d
        assert "L0_REFLEX" in d["assignments"]

    def test_full_spectrum_total_under_60gb(self):
        """Los 4 modelos del espectro completo caben en 60GB."""
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        router = ModelProfileRouter()
        profile = router.create_full_spectrum_profile()
        
        total = 0
        for acd in ACDLevel:
            key = profile.assignments[acd.value].model_key
            if key in OPTIMIZED_MODELS:
                total += OPTIMIZED_MODELS[key].size_gb
        
        # L0 y L1 usan el mismo modelo (Gemma), no sumar duplicados
        unique_keys = set()
        for acd in ACDLevel:
            key = profile.assignments[acd.value].model_key
            if key in OPTIMIZED_MODELS:
                unique_keys.add(key)
        
        total_unique = sum(OPTIMIZED_MODELS[k].size_gb for k in unique_keys)
        assert total_unique < 60  # 4 modelos únicos < 60GB
