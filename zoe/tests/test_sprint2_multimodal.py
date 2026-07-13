"""
Tests Sprint 2 — Multi-modal (Visión + Voz + Cápsula)

Valida la estructura y comportamiento de los periféricos multi-modal.
No llama APIs reales (GPT-4o, Whisper, Piper) — solo verifica estructura.
"""

import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock

from zoe.peripherals.multimodal import (
    VLMPeripheral,
    VisionSense,
    VoiceInputSense,
    VoiceActuator,
)


# ============================================================
# 1. VLMPeripheral
# ============================================================

class TestVLMPeripheral:

    def test_vlm_creation(self):
        """Se puede crear VLMPeripheral."""
        vlm = VLMPeripheral(backend="openai_compatible", model="gpt-4o")
        assert vlm.backend == "openai_compatible"
        assert vlm.model == "gpt-4o"

    def test_vlm_name(self):
        """El name incluye el backend."""
        vlm = VLMPeripheral(backend="anthropic", model="claude-sonnet-4-20250514")
        assert vlm.name == "vlm_anthropic"

    def test_vlm_without_images_returns_text(self):
        """Sin imágenes, devuelve texto simple."""
        import asyncio
        vlm = VLMPeripheral(backend="openai_compatible")
        result = asyncio.run(vlm.generate("test prompt", images=None))
        assert "test prompt" in result or "VLM" in result

    def test_vlm_backends_supported(self):
        """Los 3 backends están soportados."""
        for backend in ["openai_compatible", "anthropic", "ollama"]:
            vlm = VLMPeripheral(backend=backend)
            assert vlm.backend == backend

    def test_vlm_api_key_from_env(self):
        """API key se lee del entorno si no se pasa."""
        import os
        os.environ["OPENAI_API_KEY"] = "test-key-123"
        vlm = VLMPeripheral(backend="openai_compatible")
        assert vlm.api_key == "test-key-123"
        del os.environ["OPENAI_API_KEY"]

    def test_vlm_unknown_backend(self):
        """Backend desconocido devuelve mensaje de error."""
        import asyncio
        vlm = VLMPeripheral(backend="unknown")
        result = asyncio.run(vlm.generate("test", images=[b"fake_image"]))
        assert "no disponible" in result or "no soportado" in result


# ============================================================
# 2. VisionSense
# ============================================================

class TestVisionSense:

    def test_vision_sense_creation(self):
        """Se puede crear VisionSense."""
        sense = VisionSense()
        assert sense.name == "vision"

    def test_vision_sense_without_vlm(self):
        """Sin VLM, no genera observaciones."""
        import asyncio
        sense = VisionSense(vlm=None)
        sense.inject_image(b"fake_image", "test")
        observations = asyncio.run(sense.observe())
        assert observations == []

    def test_vision_sense_inject_image(self):
        """inject_image añade a la cola."""
        sense = VisionSense()
        sense.inject_image(b"fake_image", "¿Qué es esto?")
        assert len(sense._pending_images) == 1

    def test_vision_sense_stats(self):
        """Stats del VisionSense."""
        sense = VisionSense()
        stats = sense.get_stats()
        assert stats["observations_generated"] == 0
        assert stats["pending_images"] == 0
        assert stats["vlm_available"] is False

    def test_vision_sense_with_mock_vlm(self):
        """Con VLM mock, genera observación."""
        import asyncio
        from zoe.core.cognitive_loop import Observation

        mock_vlm = MagicMock()
        mock_vlm.generate = AsyncMock(return_value="Una imagen de un gato")

        sense = VisionSense(vlm=mock_vlm)
        sense.inject_image(b"fake_image", "¿Qué ves?")
        observations = asyncio.run(sense.observe())

        assert len(observations) == 1
        assert observations[0].source == "vision"
        assert "gato" in observations[0].content
        assert sense.get_stats()["observations_generated"] == 1


# ============================================================
# 3. VoiceInputSense
# ============================================================

class TestVoiceInputSense:

    def test_voice_input_creation(self):
        """Se puede crear VoiceInputSense."""
        sense = VoiceInputSense()
        assert sense.name == "voice_input"

    def test_voice_input_inject_audio(self):
        """inject_audio añade a la cola."""
        sense = VoiceInputSense()
        sense.inject_audio(b"fake_audio", format="wav")
        assert len(sense._pending_audio) == 1

    def test_voice_input_without_whisper(self):
        """Sin whisper, limpia cola y no genera observaciones."""
        import asyncio
        sense = VoiceInputSense()
        sense.inject_audio(b"fake_audio")
        # Mock _load_whisper to return None
        with patch.object(sense, '_load_whisper', return_value=None):
            observations = asyncio.run(sense.observe())
        assert observations == []

    def test_voice_input_stats(self):
        """Stats del VoiceInputSense."""
        sense = VoiceInputSense()
        stats = sense.get_stats()
        assert stats["transcriptions_generated"] == 0
        assert stats["pending_audio"] == 0
        assert stats["listening"] is False
        assert stats["engine"] == "whisper"

    def test_voice_input_with_mock_whisper(self):
        """Con whisper mock, genera observación."""
        import asyncio

        mock_whisper = MagicMock()
        mock_whisper.transcribe = MagicMock(return_value={
            "text": "Hola ZOE, ¿cómo estás?",
            "language": "es",
            "segments": [{"end": 2.5}],
        })

        sense = VoiceInputSense()
        sense._whisper = mock_whisper  # bypass lazy loading
        sense.inject_audio(b"fake_audio", format="wav")

        observations = asyncio.run(sense.observe())
        assert len(observations) == 1
        assert observations[0].source == "voice_input"
        assert "Hola" in observations[0].content
        assert sense.get_stats()["transcriptions_generated"] == 1


# ============================================================
# 4. VoiceActuator
# ============================================================

class TestVoiceActuator:

    def test_voice_actuator_creation(self):
        """Se puede crear VoiceActuator."""
        actuator = VoiceActuator()
        assert actuator.name == "voice"

    def test_voice_actuator_stats(self):
        """Stats del VoiceActuator."""
        actuator = VoiceActuator()
        stats = actuator.get_stats()
        assert stats["utterances_generated"] == 0
        assert stats["engine"] == "piper"

    def test_voice_actuator_without_piper(self):
        """Sin piper, no falla — devuelve success con audio=None."""
        import asyncio

        actuator = VoiceActuator()
        with patch.object(actuator, '_load_piper', return_value=None):
            action = {"type": "voice", "payload": "Hola, soy ZOE"}
            result = asyncio.run(actuator.execute(action))
        
        assert result.success is True
        assert result.output["text"] == "Hola, soy ZOE"
        assert result.output["audio"] is None

    def test_voice_actuator_empty_text(self):
        """Texto vacío devuelve failure."""
        import asyncio

        actuator = VoiceActuator()
        action = {"type": "voice", "payload": ""}
        result = asyncio.run(actuator.execute(action))
        assert result.success is False


# ============================================================
# 5. Cápsula multimodal_perception
# ============================================================

class TestMultimodalCapsule:

    def test_capsule_yaml_exists(self):
        """El capsule.yaml existe."""
        import os
        path = "zoe/capsules/multimodal_perception/capsule.yaml"
        assert os.path.exists(path)

    def test_capsule_loads(self):
        """La cápsula se carga correctamente."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert cap is not None
        assert cap.meta.name == "multimodal_perception"
        assert cap.meta.trust_level.value == "curated"

    def test_capsule_has_semantic_memory(self):
        """La cápsula tiene memoria semántica."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert len(cap.semantic_memory) > 0

    def test_capsule_has_procedural_skills(self):
        """La cápsula tiene skills procedimentales."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert len(cap.procedural_skills) > 0

    def test_capsule_has_emotional_patterns(self):
        """La cápsula tiene patrones emocionales."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert len(cap.emotional_patterns) > 0

    def test_capsule_has_ethical_guidelines(self):
        """La cápsula tiene directrices éticas."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert len(cap.ethical_guidelines) > 0

    def test_capsule_has_validators(self):
        """La cápsula tiene validators."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert cap.validators is not None

    def test_capsule_validators_work(self):
        """Los validators funcionan correctamente."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        
        # validate_claim debe bloquear reconocimiento facial sin consentimiento
        result = cap.validators.validate_claim("Vamos a hacer reconocimiento facial", {})
        assert result["valid"] is False
        
        # Con consentimiento, debe pasar
        result = cap.validators.validate_claim("Con consentimiento, reconocimiento facial", {})
        assert result["valid"] is True

    def test_capsule_compatible_use_cases(self):
        """La cápsula es compatible con casos de uso esperados."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("multimodal_perception")
        assert "cuidado_personas_mayores" in cap.meta.compatible_use_cases
        assert "vigilancia_cognitiva" in cap.meta.compatible_use_cases
