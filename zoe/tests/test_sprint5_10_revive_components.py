"""
Tests Sprint 5.10 — Revivir componentes muertos

Verifica:
C6: MentorAgent.evaluate_thought conectado al bucle (on_thought callback)
C8: LanguageDetector conectado al process_user_input_acd
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


# ============================================================
# C6: Mentor conectado al bucle
# ============================================================

class TestMentorConnected:
    """Sprint 5.10 C6 — Mentor evalúa pensamientos autónomos."""

    def test_mentor_evaluate_thought_existe(self):
        from zoe.core.mentor import MentorAgent
        assert hasattr(MentorAgent, "evaluate_thought")

    def test_mentor_devuelve_none_si_deshabilitado(self):
        from zoe.core.mentor import MentorAgent, MentorConfig
        mentor = MentorAgent()
        mentor.config = MentorConfig(enabled=False)
        result = mentor.evaluate_thought("test")
        assert result is None

    def test_mentor_devuelve_intervencion_si_tema_prohibido(self):
        from zoe.core.mentor import MentorAgent, MentorConfig
        mentor = MentorAgent()
        mentor.config = MentorConfig(enabled=True, forbidden_topics=["política"])
        # Forzar evaluación (el frequency filter puede saltarse)
        mentor._thought_count = mentor.config.intervention_frequency - 1
        result = mentor.evaluate_thought("Estoy pensando en política y sus efectos")
        assert result is not None
        assert result["type"] == "forbidden_topic"
        assert result["severity"] == "critical"

    def test_on_thought_callback_incluye_mentor_evaluation(self):
        """El callback on_thought en cli_chat.py incluye evaluación del mentor."""
        # Verificamos que el código fuente incluye la llamada al mentor
        import inspect
        from zoe.cli_chat import ZoeChat
        source = inspect.getsource(ZoeChat.initialize)
        assert "mentor" in source.lower()
        assert "evaluate_thought" in source
        assert "mentor_intervention" in source


# ============================================================
# C8: LanguageDetector conectado
# ============================================================

class TestLanguageDetectorConnected:
    """Sprint 5.10 C8 — LanguageDetector detecta idioma del usuario."""

    def test_language_detector_detect_existe(self):
        from zoe.core.language_detector import LanguageDetector
        det = LanguageDetector()
        assert hasattr(det, "detect")

    def test_detecta_espanol(self):
        from zoe.core.language_detector import LanguageDetector, Language
        det = LanguageDetector()
        result = det.detect("Hola, ¿cómo estás? Me gusta mucho hablar contigo.")
        assert result == Language.SPANISH

    def test_detecta_ingles(self):
        from zoe.core.language_detector import LanguageDetector, Language
        det = LanguageDetector()
        result = det.detect("Hello, how are you? I really like talking with you today.")
        assert result == Language.ENGLISH

    def test_detecta_frances(self):
        from zoe.core.language_detector import LanguageDetector, Language
        det = LanguageDetector()
        result = det.detect("Bonjour, comment allez-vous? J'aime beaucoup parler avec vous.")
        assert result == Language.FRENCH

    def test_detecta_aleman(self):
        from zoe.core.language_detector import LanguageDetector, Language
        det = LanguageDetector()
        result = det.detect("Hallo, wie geht es dir? Ich mag es sehr mit dir zu sprechen.")
        assert result == Language.GERMAN

    def test_language_profiles_tienen_system_prompt(self):
        from zoe.core.language_detector import LANGUAGE_PROFILES, Language
        for lang, profile in LANGUAGE_PROFILES.items():
            assert profile.system_prompt_base
            assert len(profile.system_prompt_base) > 50

    def test_language_detector_se_cachea(self):
        """La detección se cachea: una vez detectado, mantiene."""
        from zoe.core.language_detector import LanguageDetector, Language
        det = LanguageDetector()
        # Primera detección
        result1 = det.detect("Hola, ¿cómo estás?")
        # Segunda detección (en otro idioma) debe devolver el cacheado
        result2 = det.detect("Hello, how are you?")
        assert result1 == result2  # cacheado

    def test_cognitive_loop_v5_incluye_language_detection(self):
        """El código de cognitive_loop_v5.py incluye detección de idioma."""
        import inspect
        from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
        source = inspect.getsource(CognitiveLoopV5.process_user_input_acd)
        assert "language_detector" in source or "_language_detector" in source
        assert "detected_language" in source

    def test_cli_chat_inyecta_language_detector(self):
        """cli_chat.py inyecta LanguageDetector en el bucle."""
        import inspect
        from zoe.cli_chat import ZoeChat
        source = inspect.getsource(ZoeChat.initialize)
        assert "LanguageDetector" in source
        assert "_language_detector" in source

    def test_return_incluye_language(self):
        """El return de process_user_input_acd incluye 'language'."""
        import inspect
        from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
        source = inspect.getsource(CognitiveLoopV5.process_user_input_acd)
        assert '"language"' in source
        assert "detected_language" in source
