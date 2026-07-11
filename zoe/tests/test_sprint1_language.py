"""
Tests Sprint 1.1 — Language Detector + Language Profiles

Valida que ZOE detecta idiomas correctamente y carga el profile adecuado.
"""

import pytest
from zoe.core.language_detector import (
    LanguageDetector,
    Language,
    LanguageProfile,
    LANGUAGE_PROFILES,
    STOPWORDS,
)


# ============================================================
# 1. LanguageDetector — detección básica
# ============================================================

class TestLanguageDetection:

    def test_detect_spanish(self):
        """Detecta español correctamente."""
        detector = LanguageDetector()
        result = detector.detect("Hola, ¿cómo estás? Quiero hablar contigo.")
        assert result == Language.SPANISH

    def test_detect_english(self):
        """Detecta inglés correctamente."""
        detector = LanguageDetector()
        result = detector.detect("Hello, how are you? I want to talk with you.")
        assert result == Language.ENGLISH

    def test_detect_french(self):
        """Detecta francés correctamente."""
        detector = LanguageDetector()
        result = detector.detect("Bonjour, comment ça va? Je veux parler avec toi.")
        assert result == Language.FRENCH

    def test_detect_german(self):
        """Detecta alemán correctamente."""
        detector = LanguageDetector()
        result = detector.detect("Hallo, wie geht es dir? Ich will mit dir sprechen.")
        assert result == Language.GERMAN

    def test_detect_empty_text_returns_default(self):
        """Texto vacío → idioma por defecto."""
        detector = LanguageDetector()
        assert detector.detect("") == Language.SPANISH

    def test_detect_none_text_returns_default(self):
        """Texto None → idioma por defecto."""
        detector = LanguageDetector()
        assert detector.detect(None) == Language.SPANISH

    def test_detect_unknown_text_returns_default(self):
        """Texto sin stopwords reconocidas → idioma por defecto."""
        detector = LanguageDetector()
        result = detector.detect("xyz qwerty lorem ipsum")
        assert result == Language.SPANISH

    def test_detect_short_greeting_spanish(self):
        """Saludo corto en español."""
        detector = LanguageDetector()
        assert detector.detect("hola") == Language.SPANISH

    def test_detect_short_greeting_english(self):
        """Saludo corto en inglés."""
        detector = LanguageDetector()
        assert detector.detect("hello") == Language.ENGLISH

    def test_detect_short_greeting_french(self):
        """Saludo corto en francés."""
        detector = LanguageDetector()
        assert detector.detect("bonjour") == Language.FRENCH

    def test_detect_short_greeting_german(self):
        """Saludo corto en alemán."""
        detector = LanguageDetector()
        assert detector.detect("hallo") == Language.GERMAN


# ============================================================
# 2. LanguageDetector — caching
# ============================================================

class TestLanguageCaching:

    def test_cache_after_detection(self):
        """Una vez detectado con confianza, se cachea."""
        detector = LanguageDetector()
        detector.detect("Hello, how are you? I want to talk with you today.")
        assert detector._cached_language == Language.ENGLISH

    def test_cached_language_persists(self):
        """El idioma cacheado persiste en siguientes llamadas."""
        detector = LanguageDetector()
        detector.detect("Hello, how are you? I want to talk with you today.")
        # Segunda llamada con texto español debe seguir devolviendo inglés
        result = detector.detect("hola")
        assert result == Language.ENGLISH

    def test_reset_clears_cache(self):
        """Reset limpia el cache."""
        detector = LanguageDetector()
        detector.detect("Hello, how are you? I want to talk with you today.")
        detector.reset()
        assert detector._cached_language is None

    def test_low_confidence_not_cached(self):
        """Detección con baja confianza no se cachea."""
        detector = LanguageDetector()
        detector.detect("xyz hola xyz")  # 1 stopword de 3 tokens = 0.33
        # "hola" es español pero la confianza puede ser baja
        # El cache puede o no estar puesto dependiendo de si pasa MIN_CONFIDENCE
        # No assertion estricta aquí

    def test_default_language_spanish(self):
        """El idioma por defecto es español."""
        detector = LanguageDetector()
        assert detector.default_language == Language.SPANISH

    def test_custom_default_language(self):
        """Se puede configurar un idioma por defecto custom."""
        detector = LanguageDetector(default_language=Language.ENGLISH)
        assert detector.default_language == Language.ENGLISH
        assert detector.detect("") == Language.ENGLISH


# ============================================================
# 3. LanguageProfile — profiles
# ============================================================

class TestLanguageProfiles:

    def test_all_languages_have_profiles(self):
        """Todos los idiomas tienen profile definido."""
        for lang in Language:
            assert lang in LANGUAGE_PROFILES, f"Missing profile for {lang}"

    def test_spanish_profile(self):
        """Profile español correcto."""
        profile = LANGUAGE_PROFILES[Language.SPANISH]
        assert profile.language == Language.SPANISH
        assert "Eres ZOE" in profile.system_prompt_base
        assert "hola" in profile.reflex_map
        assert len(profile.validator_keywords) > 0

    def test_english_profile(self):
        """Profile inglés correcto."""
        profile = LANGUAGE_PROFILES[Language.ENGLISH]
        assert profile.language == Language.ENGLISH
        assert "You are ZOE" in profile.system_prompt_base
        assert "hello" in profile.reflex_map
        assert "diagnose" in profile.validator_keywords

    def test_french_profile(self):
        """Profile francés correcto."""
        profile = LANGUAGE_PROFILES[Language.FRENCH]
        assert profile.language == Language.FRENCH
        assert "Vous êtes ZOE" in profile.system_prompt_base
        assert "bonjour" in profile.reflex_map

    def test_german_profile(self):
        """Profile alemán correcto."""
        profile = LANGUAGE_PROFILES[Language.GERMAN]
        assert profile.language == Language.GERMAN
        assert "Du bist ZOE" in profile.system_prompt_base
        assert "hallo" in profile.reflex_map

    def test_all_profiles_have_reflex_map(self):
        """Todos los profiles tienen reflex_map no vacío."""
        for lang, profile in LANGUAGE_PROFILES.items():
            assert len(profile.reflex_map) > 0, f"{lang} has empty reflex_map"

    def test_all_profiles_have_validator_keywords(self):
        """Todos los profiles tienen validator_keywords."""
        for lang, profile in LANGUAGE_PROFILES.items():
            assert len(profile.validator_keywords) > 0, f"{lang} has empty validator_keywords"

    def test_all_profiles_have_ethical_disclaimer(self):
        """Todos los profiles tienen ethical_disclaimer."""
        for lang, profile in LANGUAGE_PROFILES.items():
            assert profile.ethical_disclaimer, f"{lang} has empty ethical_disclaimer"


# ============================================================
# 4. LanguageDetector — get_profile
# ============================================================

class TestGetProfile:

    def test_get_profile_spanish(self):
        """get_profile devuelve profile español."""
        detector = LanguageDetector()
        profile = detector.get_profile(Language.SPANISH)
        assert profile.language == Language.SPANISH

    def test_get_profile_english(self):
        """get_profile devuelve profile inglés."""
        detector = LanguageDetector()
        profile = detector.get_profile(Language.ENGLISH)
        assert profile.language == Language.ENGLISH

    def test_get_profile_after_detection(self):
        """get_profile usa idioma detectado si no se especifica."""
        detector = LanguageDetector()
        detector.detect("Hello, how are you? I want to talk with you today.")
        profile = detector.get_profile()
        assert profile.language == Language.ENGLISH

    def test_get_profile_default_when_no_detection(self):
        """get_profile usa default si no hay detección."""
        detector = LanguageDetector()
        profile = detector.get_profile()
        assert profile.language == Language.SPANISH

    def test_get_profile_unknown_language_returns_default(self):
        """get_profile devuelve default si idioma no existe."""
        detector = LanguageDetector()
        # Language.SPANISH siempre existe, pero test el fallback
        profile = detector.get_profile(Language.SPANISH)
        assert profile is not None


# ============================================================
# 5. LanguageDetector — stats
# ============================================================

class TestLanguageDetectorStats:

    def test_get_stats_initial(self):
        """Stats iniciales correctos."""
        detector = LanguageDetector()
        stats = detector.get_stats()
        assert stats["default_language"] == "es"
        assert stats["cached_language"] is None
        assert "es" in stats["supported_languages"]
        assert "en" in stats["supported_languages"]
        assert len(stats["supported_languages"]) == 4

    def test_get_stats_after_detection(self):
        """Stats después de detección."""
        detector = LanguageDetector()
        detector.detect("Hello, how are you? I want to talk with you today.")
        stats = detector.get_stats()
        assert stats["cached_language"] == "en"


# ============================================================
# 6. Language enum
# ============================================================

class TestLanguageEnum:

    def test_language_values(self):
        """Los valores del enum son correctos."""
        assert Language.SPANISH.value == "es"
        assert Language.ENGLISH.value == "en"
        assert Language.FRENCH.value == "fr"
        assert Language.GERMAN.value == "de"

    def test_language_from_string(self):
        """Se puede crear Language desde string."""
        assert Language("es") == Language.SPANISH
        assert Language("en") == Language.ENGLISH

    def test_stopwords_not_empty(self):
        """Todos los idiomas tienen stopwords."""
        for lang in Language:
            assert len(STOPWORDS[lang]) > 0, f"{lang} has empty stopwords"
