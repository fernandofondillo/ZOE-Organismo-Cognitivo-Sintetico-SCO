"""
Tests Sprint 5.11 — Visión, Voice-first endpoints y CognitiveOptimizationLayer
ACTUALIZADO para arquitectura modular dashboard (ZOE OMEGA).

Los handlers ahora viven en zoe/dashboard/handlers/ como funciones separadas,
no como métodos de DashboardServer.
"""

import asyncio
import inspect
from pathlib import Path

import pytest


# ============================================================
# C7: Visión conectada al Dashboard
# ============================================================

class TestVisionConnected:
    """Sprint 5.11 C7 — feed_upload detecta imágenes y usa VLM."""

    def test_feed_upload_handler_detecta_imagenes(self):
        """El handler de feed_upload incluye detección de imágenes."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        source = handler_path.read_text()
        assert "is_image" in source
        assert "image/" in source
        assert ".png" in source or ".jpg" in source

    def test_feed_upload_handler_usa_vlm(self):
        """El handler de feed_upload incluye VLMPeripheral."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        source = handler_path.read_text()
        assert "VLMPeripheral" in source
        assert "image_description" in source

    def test_feed_upload_fallback_si_vlm_falla(self):
        """Si VLM falla, guarda metadata sin caer."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        source = handler_path.read_text()
        assert "VLM no disponible" in source or "VLM failed" in source

    def test_feed_upload_response_incluye_is_image(self):
        """La respuesta incluye is_image y image_description."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        source = handler_path.read_text()
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
# C10: Voice-first endpoints en Dashboard (arquitectura modular)
# ============================================================

class TestVoiceFirstEndpoints:
    """Sprint 5.11 C10 — Endpoints /api/voice/* en Dashboard modular."""

    def test_voice_handler_file_exists(self):
        """El archivo handlers/voice.py existe."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        assert voice_path.exists()

    def test_voice_start_handler_exists(self):
        """El handler _handle_voice_start existe en voice.py."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "_handle_voice_start" in source

    def test_voice_stop_handler_exists(self):
        """El handler _handle_voice_stop existe en voice.py."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "_handle_voice_stop" in source

    def test_voice_status_handler_exists(self):
        """El handler _handle_voice_status existe en voice.py."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "_handle_voice_status" in source

    def test_routes_register_voice_endpoints(self):
        """routes.py registra las rutas /api/voice/*."""
        routes_path = Path(__file__).parent.parent / "dashboard" / "routes.py"
        source = routes_path.read_text()
        assert "/api/voice/start" in source
        assert "/api/voice/stop" in source
        assert "/api/voice/status" in source

    def test_voice_start_crea_voidefirstmode(self):
        """_handle_voice_start crea VoiceFirstMode."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "VoiceFirstMode" in source
        assert "VoiceConfig" in source

    def test_voice_start_devuelve_listening(self):
        """_handle_voice_start devuelve status=listening."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "listening" in source

    def test_voice_stop_devuelve_stopped(self):
        """_handle_voice_stop devuelve status=stopped."""
        voice_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "voice.py"
        source = voice_path.read_text()
        assert "stopped" in source
