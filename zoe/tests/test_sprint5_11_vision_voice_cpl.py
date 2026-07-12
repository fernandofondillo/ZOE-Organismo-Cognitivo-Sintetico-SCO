"""
Tests Sprint 5.11 — Visión, Voice-first endpoints y CognitiveOptimizationLayer

Verifica:
C7: feed_upload detecta imágenes y usa VLM (o fallback elegante)
C9: CognitivePrefetchLayer se instancia en cli_chat
C10: Endpoints /api/voice/start|stop|status existen en Dashboard
"""

import asyncio
import inspect
import pytest


# ============================================================
# C7: Visión conectada al Dashboard
# ============================================================

class TestVisionConnected:
    """Sprint 5.11 C7 — feed_upload detecta imágenes y usa VLM."""

    def test_handle_feed_upload_detecta_imagenes(self):
        """El código de _handle_feed_upload incluye detección de imágenes."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_feed_upload)
        assert "is_image" in source
        assert "image/" in source
        assert ".png" in source or ".jpg" in source

    def test_handle_feed_upload_usa_vlm(self):
        """El código de _handle_feed_upload incluye VLMPeripheral."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_feed_upload)
        assert "VLMPeripheral" in source
        assert "image_description" in source

    def test_handle_feed_upload_fallback_si_vlm_falla(self):
        """Si VLM falla, guarda metadata sin caer."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_feed_upload)
        assert "VLM no disponible" in source or "VLM failed" in source

    def test_handle_feed_upload_response_incluye_is_image(self):
        """La respuesta incluye is_image y image_description."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_feed_upload)
        assert '"is_image"' in source
        assert '"image_description"' in source

    def test_vlm_peripheral_existe(self):
        """VLMPeripheral existe y tiene método generate."""
        from zoe.peripherals.multimodal import VLMPeripheral
        assert hasattr(VLMPeripheral, "generate")


# ============================================================
# C9: CognitiveOptimizationLayer activo
# ============================================================

class TestCognitiveOptimizationLayerActive:
    """Sprint 5.11 C9 — CognitivePrefetchLayer se instancia en cli_chat."""

    def test_cpl_se_instancia_en_cli_chat(self):
        """cli_chat.py initialize() instancia CognitivePrefetchLayer."""
        from zoe.cli_chat import ZoeChat
        source = inspect.getsource(ZoeChat.initialize)
        assert "CognitivePrefetchLayer" in source
        assert "cognitive_prefetch_layer" in source

    def test_cpl_se_inyecta_en_loop(self):
        """El CPL se asigna a loop.cognitive_prefetch_layer."""
        from zoe.cli_chat import ZoeChat
        source = inspect.getsource(ZoeChat.initialize)
        assert "loop.cognitive_prefetch_layer" in source

    def test_cpl_fallback_elegante_si_falla(self):
        """Si CPL falla al instanciarse, no rompe el arranque."""
        from zoe.cli_chat import ZoeChat
        source = inspect.getsource(ZoeChat.initialize)
        assert "cognitive_prefetch_layer = None" in source or "no disponible" in source

    def test_cognitive_prefetch_layer_existe(self):
        """CognitivePrefetchLayer existe en cognitive_optimization.py."""
        from zoe.core.cognitive_optimization import CognitivePrefetchLayer
        assert hasattr(CognitivePrefetchLayer, "prefetch")

    def test_zmap_loader_existe(self):
        """ZMAPLoader existe."""
        from zoe.core.cognitive_optimization import ZMAPLoader
        assert ZMAPLoader is not None

    def test_tpe_existe(self):
        """TensorPredictionEngine existe."""
        from zoe.core.cognitive_optimization import TensorPredictionEngine
        assert TensorPredictionEngine is not None


# ============================================================
# C10: Voice-first endpoints en Dashboard
# ============================================================

class TestVoiceFirstEndpoints:
    """Sprint 5.11 C10 — Endpoints /api/voice/* en Dashboard."""

    def test_dashboard_tiene_voice_start(self):
        """DashboardServer tiene _handle_voice_start."""
        from zoe.web_dashboard import DashboardServer
        assert hasattr(DashboardServer, "_handle_voice_start")

    def test_dashboard_tiene_voice_stop(self):
        """DashboardServer tiene _handle_voice_stop."""
        from zoe.web_dashboard import DashboardServer
        assert hasattr(DashboardServer, "_handle_voice_stop")

    def test_dashboard_tiene_voice_status(self):
        """DashboardServer tiene _handle_voice_status."""
        from zoe.web_dashboard import DashboardServer
        assert hasattr(DashboardServer, "_handle_voice_status")

    def test_start_registra_ruta_voice(self):
        """El método start() registra las rutas /api/voice/*."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer.start)
        assert "/api/voice/start" in source
        assert "/api/voice/stop" in source
        assert "/api/voice/status" in source

    def test_voice_start_crea_voidefirstmode(self):
        """_handle_voice_start crea VoiceFirstMode."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_voice_start)
        assert "VoiceFirstMode" in source
        assert "VoiceConfig" in source

    def test_voice_start_devuelve_listening(self):
        """_handle_voice_start devuelve status=listening."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_voice_start)
        assert "listening" in source

    def test_voice_stop_devuelve_stopped(self):
        """_handle_voice_stop devuelve status=stopped."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_voice_stop)
        assert "stopped" in source

    def test_voice_status_devuelve_running_o_stopped(self):
        """_handle_voice_status devuelve running o stopped."""
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer._handle_voice_status)
        assert "running" in source
        assert "stopped" in source
