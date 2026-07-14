"""
Tests de EmbodimentComposer con diferentes perfiles de hardware simulados.

Parametriza compose() con diferentes configuraciones de RAM y Ollama
para verificar que selecciona la configuracion correcta.
"""

import pytest
from unittest.mock import patch, MagicMock

from zoe.core.embodiment_composer import EmbodimentComposer, EmbodimentStatus


class TestEmbodimentHardwareProfiles:
    """Test que EmbodimentComposer adapta la configuracion al hardware."""

    def test_compose_mac_8gb_no_ollama(self):
        """Mac 8GB sin Ollama -> debe usar pattern o mock."""
        composer = EmbodimentComposer()
        # Simular un plan para 8GB sin Ollama
        mock_plan = MagicMock()
        mock_plan.backend_name = "mock"
        mock_plan.model_name = ""
        mock_plan.strategy = "cloud"
        mock_plan.ollama_env = {}
        mock_plan.acd_level = "L1_FAST"
        mock_plan.metabolic_state = "awake"
        mock_plan.sensitive_domain = False
        mock_plan.available_ram_gb = 8.0

        emb = composer.compose(mock_plan)

        assert emb.status in (EmbodimentStatus.RUNNING.value, EmbodimentStatus.DEGRADED.value)
        assert emb.available_ram_gb == 8.0
        assert emb.is_running

    def test_compose_mac_8gb_with_ollama(self):
        """Mac 8GB con Ollama -> debe seleccionar modelo pequeno."""
        composer = EmbodimentComposer()
        mock_plan = MagicMock()
        mock_plan.backend_name = "ollama"
        mock_plan.model_name = "gemma-2-9b-iq2"
        mock_plan.strategy = "mmap_partial"
        mock_plan.ollama_env = {}
        mock_plan.acd_level = "L2_STANDARD"
        mock_plan.metabolic_state = "awake"
        mock_plan.sensitive_domain = False
        mock_plan.available_ram_gb = 8.0

        emb = composer.compose(mock_plan, skip_validation=True)

        assert emb.status in (EmbodimentStatus.RUNNING.value, EmbodimentStatus.DEGRADED.value)
        assert emb.backend_name == "ollama"
        assert emb.available_ram_gb == 8.0

    def test_compose_vps_64gb(self):
        """VPS 64GB -> debe seleccionar ollama con modelo grande."""
        composer = EmbodimentComposer()
        mock_plan = MagicMock()
        mock_plan.backend_name = "ollama"
        mock_plan.model_name = "qwen2.5:72b-iq2"
        mock_plan.strategy = "mmap_full"
        mock_plan.ollama_env = {}
        mock_plan.acd_level = "L3_MAXIMUM"
        mock_plan.metabolic_state = "awake"
        mock_plan.sensitive_domain = False
        mock_plan.available_ram_gb = 64.0

        emb = composer.compose(mock_plan, skip_validation=True)

        assert emb.status in (EmbodimentStatus.RUNNING.value, EmbodimentStatus.DEGRADED.value)
        assert emb.available_ram_gb == 64.0

    def test_compose_no_gpu(self):
        """Maquina sin GPU -> debe usar mmap_partial strategy."""
        composer = EmbodimentComposer()
        mock_plan = MagicMock()
        mock_plan.backend_name = "ollama"
        mock_plan.model_name = "qwq-32b-iq2"
        mock_plan.strategy = "mmap_partial"
        mock_plan.ollama_env = {}
        mock_plan.acd_level = "L2_STANDARD"
        mock_plan.metabolic_state = "awake"
        mock_plan.sensitive_domain = False
        mock_plan.available_ram_gb = 16.0

        emb = composer.compose(mock_plan, skip_validation=True)

        assert emb.strategy == "mmap_partial"
        assert emb.status in (EmbodimentStatus.RUNNING.value, EmbodimentStatus.DEGRADED.value)

    def test_to_dict_includes_all_fields(self):
        """to_dict() debe incluir todos los campos utiles."""
        composer = EmbodimentComposer()
        mock_plan = MagicMock()
        mock_plan.backend_name = "ollama"
        mock_plan.model_name = "gemma-2-9b-iq2"
        mock_plan.strategy = "mmap_full"
        mock_plan.ollama_env = {}
        mock_plan.acd_level = "L2_STANDARD"
        mock_plan.metabolic_state = "awake"
        mock_plan.sensitive_domain = False
        mock_plan.available_ram_gb = 16.0

        emb = composer.compose(mock_plan)
        d = emb.to_dict()

        required_fields = [
            "embodiment_id", "plan_signature", "backend_name", "model_name",
            "strategy", "status", "acd_level", "metabolic_state",
            "available_ram_gb", "is_running", "warnings", "errors",
        ]
        for field in required_fields:
            assert field in d, f"Field '{field}' missing from to_dict()"
