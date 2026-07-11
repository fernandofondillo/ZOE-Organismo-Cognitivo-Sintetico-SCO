"""
Tests Sprint 4 — Voice-First Mode

Valida la estructura y comportamiento del Voice-first mode.
No usa micrófono real — solo verifica estructura y lógica.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from zoe.peripherals.voice_first import (
    VoiceFirstMode,
    VoiceState,
    VoiceConfig,
    WakeWordDetector,
    VoiceActivityDetector,
    InterruptionHandler,
)


# ============================================================
# 1. VoiceConfig
# ============================================================

class TestVoiceConfig:

    def test_default_config(self):
        """Config por defecto."""
        config = VoiceConfig()
        assert config.wake_word == "hey zoe"
        assert config.sample_rate == 16000
        assert config.enable_interruption is True

    def test_custom_config(self):
        """Config custom."""
        config = VoiceConfig(
            wake_word="hola zoe",
            stt_model="small",
            tts_voice="en_US-lessac-medium",
            enable_interruption=False,
        )
        assert config.wake_word == "hola zoe"
        assert config.stt_model == "small"
        assert config.tts_voice == "en_US-lessac-medium"
        assert config.enable_interruption is False

    def test_all_fields_have_defaults(self):
        """Todos los campos tienen defaults."""
        config = VoiceConfig()
        assert config.wake_word_sensitivity > 0
        assert config.vad_aggressiveness >= 0
        assert config.silence_duration > 0
        assert config.max_recording_duration > 0
        assert config.min_response_delay >= 0
        assert config.cooldown_after_speaking >= 0


# ============================================================
# 2. WakeWordDetector
# ============================================================

class TestWakeWordDetector:

    def test_creation(self):
        """Se puede crear WakeWordDetector."""
        detector = WakeWordDetector(wake_word="hey zoe")
        assert detector.wake_word == "hey zoe"

    def test_initialize_without_openwakeword(self):
        """Initialize sin openwakeword instalado no crashea."""
        detector = WakeWordDetector()
        # Probablemente no está instalado en test env
        result = detector.initialize()
        assert isinstance(result, bool)

    def test_detect_fallback_energy(self):
        """Detect fallback por energía cuando no hay openWakeWord."""
        detector = WakeWordDetector()
        detector._available = False  # forzar fallback

        # Audio con energía alta (ruido)
        import numpy as np
        loud_audio = (np.random.randn(16000) * 5000).astype(np.int16).tobytes()
        result = detector.detect(loud_audio)
        assert isinstance(result, bool)

    def test_detect_silence(self):
        """Silencio no activa wake word (fallback energía)."""
        detector = WakeWordDetector()
        detector._available = False

        # Audio silencioso
        import numpy as np
        silence = np.zeros(16000, dtype=np.int16).tobytes()
        result = detector.detect(silence)
        assert result is False

    def test_available_property(self):
        """available property."""
        detector = WakeWordDetector()
        detector._available = False
        assert detector.available is False


# ============================================================
# 3. VoiceActivityDetector
# ============================================================

class TestVoiceActivityDetector:

    def test_creation(self):
        """Se puede crear VoiceActivityDetector."""
        vad = VoiceActivityDetector()
        assert vad.aggressiveness == 3
        assert vad.silence_duration == 1.5

    def test_initialize_without_webrtcvad(self):
        """Initialize sin webrtcvad no crashea."""
        vad = VoiceActivityDetector()
        result = vad.initialize()
        assert isinstance(result, bool)

    def test_is_speech_fallback(self):
        """is_speech fallback por energía."""
        vad = VoiceActivityDetector()
        vad._available = False

        import numpy as np
        loud_audio = (np.random.randn(16000) * 5000).astype(np.int16).tobytes()
        result = vad.is_speech(loud_audio)
        assert isinstance(result, bool)

    def test_is_speech_silence(self):
        """Silencio no es speech."""
        vad = VoiceActivityDetector()
        vad._available = False

        import numpy as np
        silence = np.zeros(16000, dtype=np.int16).tobytes()
        result = vad.is_speech(silence)
        assert result is False

    def test_available_property(self):
        """available property."""
        vad = VoiceActivityDetector()
        vad._available = False
        assert vad.available is False


# ============================================================
# 4. InterruptionHandler
# ============================================================

class TestInterruptionHandler:

    def test_creation(self):
        """Se puede crear InterruptionHandler."""
        vad = VoiceActivityDetector()
        handler = InterruptionHandler(vad=vad)
        assert handler.enabled is True

    def test_disabled(self):
        """Disabled no detecta interrupciones."""
        vad = VoiceActivityDetector()
        handler = InterruptionHandler(vad=vad, enabled=False)
        handler.start_monitoring()

        import numpy as np
        loud_audio = (np.random.randn(16000) * 5000).astype(np.int16).tobytes()
        result = handler.check_interruption(loud_audio)
        assert result is False

    def test_start_stop_monitoring(self):
        """Start/stop monitoring."""
        vad = VoiceActivityDetector()
        handler = InterruptionHandler(vad=vad)
        
        handler.start_monitoring()
        assert handler._monitoring is True
        
        handler.stop_monitoring()
        assert handler._monitoring is False

    def test_reset(self):
        """Reset limpia interrupción."""
        vad = VoiceActivityDetector()
        handler = InterruptionHandler(vad=vad)
        handler._interrupted = True
        handler.reset()
        assert handler._interrupted is False

    def test_was_interrupted(self):
        """was_interrupted property."""
        vad = VoiceActivityDetector()
        handler = InterruptionHandler(vad=vad)
        assert handler.was_interrupted is False


# ============================================================
# 5. VoiceFirstMode
# ============================================================

class TestVoiceFirstMode:

    def test_creation(self):
        """Se puede crear VoiceFirstMode."""
        mode = VoiceFirstMode()
        assert mode is not None
        assert mode.state == VoiceState.IDLE

    def test_default_config(self):
        """Config por defecto."""
        mode = VoiceFirstMode()
        assert mode.config.wake_word == "hey zoe"
        assert mode.config.sample_rate == 16000

    def test_custom_config(self):
        """Config custom."""
        config = VoiceConfig(wake_word="hola zoe", stt_model="small")
        mode = VoiceFirstMode(config=config)
        assert mode.config.wake_word == "hola zoe"
        assert mode.config.stt_model == "small"

    def test_get_stats(self):
        """get_stats devuelve dict."""
        mode = VoiceFirstMode()
        stats = mode.get_stats()
        assert isinstance(stats, dict)
        assert "mode" in stats
        assert "state" in stats
        assert "turns" in stats
        assert "config" in stats

    def test_stop(self):
        """stop() detiene el modo."""
        mode = VoiceFirstMode()
        mode._running = True
        mode.stop()
        assert mode._running is False

    def test_get_banner(self):
        """get_banner devuelve string con info."""
        mode = VoiceFirstMode()
        banner = mode._get_banner()
        assert isinstance(banner, str)
        assert "ZOE Voice-First" in banner
        assert "hey zoe" in banner

    def test_zoe_url_trailing_slash(self):
        """zoe_url sin trailing slash."""
        mode = VoiceFirstMode(zoe_url="http://localhost:8642/")
        assert mode.zoe_url == "http://localhost:8642"

    def test_state_transitions(self):
        """Los estados están definidos."""
        assert VoiceState.IDLE.value == "idle"
        assert VoiceState.LISTENING.value == "listening"
        assert VoiceState.PROCESSING.value == "processing"
        assert VoiceState.SPEAKING.value == "speaking"
        assert VoiceState.INTERRUPTED.value == "interrupted"


# ============================================================
# 6. VoiceFirstMode — métodos async (con mocks)
# ============================================================

class TestVoiceFirstModeAsync:

    def test_process_with_zoe_api_mode(self):
        """_process_with_zoe en modo API funciona."""
        import asyncio

        mode = VoiceFirstMode(zoe_url="http://localhost:8642")

        # Mock aiohttp response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"response": "Hola"})

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = asyncio.run(mode._process_with_zoe("Hola"))
            assert result == "Hola"

    def test_process_with_zoe_direct_mode(self):
        """_process_with_zoe en modo directo funciona."""
        import asyncio

        mock_chat = MagicMock()
        mock_chat.send_message_acd = AsyncMock(return_value="Hola de ZOE")

        mode = VoiceFirstMode(zoe_chat=mock_chat)
        result = asyncio.run(mode._process_with_zoe("Hola"))
        assert result == "Hola de ZOE"

    def test_transcribe_without_whisper(self):
        """_transcribe sin Whisper devuelve None."""
        import asyncio

        mode = VoiceFirstMode()
        mode._whisper = None
        result = asyncio.run(mode._transcribe(b"fake_audio"))
        assert result is None

    def test_transcribe_with_mock_whisper(self):
        """_transcribe con Whisper mock funciona."""
        import asyncio

        mode = VoiceFirstMode()
        mode._whisper = MagicMock()
        mode._whisper.transcribe = MagicMock(return_value={"text": "Hola ZOE"})

        result = asyncio.run(mode._transcribe(b"fake_audio"))
        assert result == "Hola ZOE"

    def test_speak_without_piper(self):
        """_speak sin Piper no falla."""
        import asyncio

        mode = VoiceFirstMode()
        with patch.object(mode, "_check_piper", return_value=False):
            asyncio.run(mode._speak("Hola"))

    def test_stats_after_interaction(self):
        """Stats reflejan interacción."""
        import asyncio

        mock_chat = MagicMock()
        mock_chat.send_message_acd = AsyncMock(return_value="Hola")

        mode = VoiceFirstMode(zoe_chat=mock_chat)
        asyncio.run(mode._process_with_zoe("Hola"))

        stats = mode.get_stats()
        assert isinstance(stats, dict)

    def test_check_piper(self):
        """_check_piper devuelve bool."""
        mode = VoiceFirstMode()
        result = mode._check_piper()
        assert isinstance(result, bool)


# ============================================================
# 7. Integración — estructura completa
# ============================================================

class TestVoiceFirstIntegration:

    def test_all_components_exist(self):
        """Todos los componentes existen."""
        assert VoiceFirstMode is not None
        assert WakeWordDetector is not None
        assert VoiceActivityDetector is not None
        assert InterruptionHandler is not None
        assert VoiceConfig is not None
        assert VoiceState is not None

    def test_has_main_function(self):
        """Tiene función main como entry point."""
        from zoe.peripherals.voice_first import main
        assert callable(main)

    def test_voice_first_imports_from_multimodal(self):
        """VoiceFirstMode puede coexistir con multimodal (Sprint 2)."""
        from zoe.peripherals.multimodal import VoiceInputSense, VoiceActuator
        from zoe.peripherals.voice_first import VoiceFirstMode

        # Ambos módulos se cargan sin conflicto
        assert VoiceInputSense is not None
        assert VoiceActuator is not None
        assert VoiceFirstMode is not None

    def test_config_supports_multiple_languages(self):
        """Config soporta múltiples voces/idiomas."""
        config_es = VoiceConfig(tts_voice="es_ES-davefx-medium")
        config_en = VoiceConfig(tts_voice="en_US-lessac-medium")
        config_fr = VoiceConfig(tts_voice="fr_FR-siwis-medium")

        assert "es_ES" in config_es.tts_voice
        assert "en_US" in config_en.tts_voice
        assert "fr_FR" in config_fr.tts_voice
