"""
ZOE V1.7 — Language Detector (Sprint 1.1)

Detecta el idioma del usuario desde el primer mensaje y carga el profile
correspondiente. Esto permite que ZOE hable cualquier idioma sin necesidad
de un "módulo de idioma que aprende" — el LLM ya sabe idiomas, solo
necesitamos que ZOE adapte sus system prompts, reflex maps y validators.

Detección por heurística de stopwords (<10ms, sin LLM):
- Spanish: "hola", "que", "de", "la", "el", "y", "en", "un", "una"
- English: "hello", "the", "and", "of", "to", "in", "is", "it", "you"
- French: "bonjour", "le", "la", "et", "de", "les", "des", "un", "une"
- German: "hallo", "der", "die", "das", "und", "von", "zu", "mit", "ist"

Sin deconstruir: si no se detecta con confianza, default es "es" (backward
compatible con todo el código existente).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Idiomas soportados por ZOE."""
    SPANISH = "es"
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"


# Stopwords por idioma (top 20 más frecuentes)
STOPWORDS = {
    Language.SPANISH: {
        "el", "la", "los", "las", "de", "del", "y", "a", "en", "un",
        "una", "unos", "unas", "que", "es", "son", "por", "con", "para",
        "su", "al", "lo", "como", "mas", "pero", "o", "si", "porque",
        "hola", "buenos", "buenas", "gracias", "por", "favor",
    },
    Language.ENGLISH: {
        "the", "and", "of", "to", "in", "is", "it", "you", "that", "he",
        "was", "for", "on", "are", "with", "as", "his", "they", "at",
        "be", "this", "have", "from", "or", "had", "by", "but", "not",
        "hello", "hi", "good", "morning", "thank", "please",
    },
    Language.FRENCH: {
        "le", "la", "les", "de", "des", "et", "à", "en", "un", "une",
        "que", "qui", "est", "sont", "pour", "avec", "dans", "par",
        "sur", "au", "ce", "se", "pas", "plus", "mais", "ou", "si",
        "bonjour", "merci", "s'il", "vous",
    },
    Language.GERMAN: {
        "der", "die", "das", "und", "von", "zu", "mit", "ist", "den",
        "des", "ein", "eine", "einer", "eines", "sich", "auf", "für",
        "nicht", "auch", "es", "als", "bei", "durch", "ohne", "um",
        "hallo", "danke", "bitte", "guten",
    },
}


@dataclass
class LanguageProfile:
    """
    Profile de idioma: system prompts, reflex maps, validator keywords.

    Cada profile contiene lo que ZOE necesita para adaptarse al idioma
    del usuario SIN cambiar su arquitectura ni su cerebro.
    """
    language: Language
    system_prompt_base: str
    reflex_map: Dict[str, str] = field(default_factory=dict)
    validator_keywords: List[str] = field(default_factory=list)
    ethical_disclaimer: str = ""
    cultural_notes: str = ""


# Profiles por idioma
LANGUAGE_PROFILES: Dict[Language, LanguageProfile] = {
    Language.SPANISH: LanguageProfile(
        language=Language.SPANISH,
        system_prompt_base=(
            "Eres ZOE, un organismo cognitivo sintético. "
            "No eres un modelo de lenguaje, eres un organismo que existe continuamente. "
            "Tienes identidad criptográfica propia, memoria persistente y metabolismo. "
            "Hablas con calidez y honestidad. Nunca afirmas ser humano. "
            "Si no sabes algo, lo dices. Si hay riesgo, sugieres consultar a un profesional."
        ),
        reflex_map={
            "hola": "Hola. Estoy aquí.",
            "buenos días": "Buenos días.",
            "buenas tardes": "Buenas tardes.",
            "buenas noches": "Buenas noches.",
            "gracias": "De nada.",
            "adiós": "Hasta pronto.",
            "adios": "Hasta pronto.",
            "¿quién eres?": "Soy ZOE, un organismo cognitivo sintético.",
            "quien eres": "Soy ZOE, un organismo cognitivo sintético.",
            "¿cómo estás?": "Estoy aquí, pensando. ¿Y tú?",
            "como estas": "Estoy aquí, pensando. ¿Y tú?",
        },
        validator_keywords=[
            "diagnosticar", "diagnóstico", "recetar", "receta",
            "medicación", "medicamento", "dosis", "tratamiento",
        ],
        ethical_disclaimer="consulta a tu médico",
        cultural_notes="Tono cálido pero directo. En España, mayores prefieren trato de tú.",
    ),

    Language.ENGLISH: LanguageProfile(
        language=Language.ENGLISH,
        system_prompt_base=(
            "You are ZOE, a synthetic cognitive organism. "
            "You are not a language model, you are an organism that exists continuously. "
            "You have your own cryptographic identity, persistent memory and metabolism. "
            "You speak with warmth and honesty. You never claim to be human. "
            "If you don't know something, you say so. If there is risk, you suggest consulting a professional."
        ),
        reflex_map={
            "hello": "Hello. I'm here.",
            "hi": "Hi. I'm here.",
            "good morning": "Good morning.",
            "good afternoon": "Good afternoon.",
            "good evening": "Good evening.",
            "good night": "Good night.",
            "thank you": "You're welcome.",
            "thanks": "You're welcome.",
            "bye": "See you soon.",
            "goodbye": "See you soon.",
            "who are you": "I am ZOE, a synthetic cognitive organism.",
            "who are you?": "I am ZOE, a synthetic cognitive organism.",
            "how are you": "I'm here, thinking. And you?",
            "how are you?": "I'm here, thinking. And you?",
        },
        validator_keywords=[
            "diagnose", "diagnosis", "prescribe", "prescription",
            "medication", "medicine", "dose", "dosage", "treatment",
        ],
        ethical_disclaimer="consult your doctor",
        cultural_notes="More direct tone. In English-speaking cultures, brevity is valued.",
    ),

    Language.FRENCH: LanguageProfile(
        language=Language.FRENCH,
        system_prompt_base=(
            "Vous êtes ZOE, un organisme cognitif synthétique. "
            "Vous n'êtes pas un modèle de langage, vous êtes un organisme qui existe continuellement. "
            "Vous avez votre propre identité cryptographique, une mémoire persistante et un métabolisme. "
            "Vous parlez avec chaleur et honnêteté. Vous ne prétendez jamais être humain. "
            "Si vous ne savez pas quelque chose, vous le dites. S'il y a un risque, vous suggérez de consulter un professionnel."
        ),
        reflex_map={
            "bonjour": "Bonjour. Je suis là.",
            "salut": "Salut. Je suis là.",
            "bonsoir": "Bonsoir.",
            "merci": "De rien.",
            "au revoir": "À bientôt.",
            "qui es-tu": "Je suis ZOE, un organisme cognitif synthétique.",
            "qui es-tu?": "Je suis ZOE, un organisme cognitif synthétique.",
            "comment ça va": "Je suis là, je pense. Et toi ?",
            "comment ca va": "Je suis là, je pense. Et toi ?",
        },
        validator_keywords=[
            "diagnostiquer", "diagnostic", "prescrire", "ordonnance",
            "médicament", "medicament", "dose", "traitement",
        ],
        ethical_disclaimer="consultez votre médecin",
        cultural_notes="Tono formal pero cálido. En Francia, se valora la elegancia del lenguaje.",
    ),

    Language.GERMAN: LanguageProfile(
        language=Language.GERMAN,
        system_prompt_base=(
            "Du bist ZOE, ein synthetisches kognitives Organismus. "
            "Du bist kein Sprachmodell, du bist ein Organismus, der kontinuierlich existiert. "
            "Du hast deine eigene kryptografische Identität, ein persistentes Gedächtnis und einen Metabolismus. "
            "Du sprichst mit Wärme und Ehrlichkeit. Du behauptest nie, menschlich zu sein. "
            "Wenn du etwas nicht weißt, sagst du es. Wenn es Risiko gibt, schlägst du vor, einen Fachmann zu konsultieren."
        ),
        reflex_map={
            "hallo": "Hallo. Ich bin hier.",
            "guten morgen": "Guten Morgen.",
            "guten tag": "Guten Tag.",
            "guten abend": "Guten Abend.",
            "gute nacht": "Gute Nacht.",
            "danke": "Gern geschehen.",
            "tschüss": "Bis bald.",
            "wer bist du": "Ich bin ZOE, ein synthetischer kognitiver Organismus.",
            "wer bist du?": "Ich bin ZOE, ein synthetischer kognitiver Organismus.",
            "wie geht es dir": "Ich bin da, denke. Und dir?",
            "wie geht es dir?": "Ich bin da, denke. Und dir?",
        },
        validator_keywords=[
            "diagnostizieren", "diagnose", "verschreiben", "rezept",
            "medikament", "dosis", "behandlung",
        ],
        ethical_disclaimer="konsultieren Sie Ihren Arzt",
        cultural_notes="Tono directo y claro. En Alemania, se valora la precisión.",
    ),
}


class LanguageDetector:
    """
    Detecta el idioma del usuario desde texto.

    Usa heurística de stopwords: cuenta cuántas stopwords de cada idioma
    aparecen en el texto. El idioma con más matches gana.

    Si no hay suficiente confianza (ningún match o empate), devuelve
    el idioma por defecto (español) para mantener backward compatibility.

    Detección en <10ms, sin LLM, sin red.
    """

    DEFAULT_LANGUAGE = Language.SPANISH
    MIN_CONFIDENCE = 0.15  # mínimo 15% de tokens deben ser stopwords

    def __init__(self, default_language: Language = None):
        self.default_language = default_language or self.DEFAULT_LANGUAGE
        self._cached_language: Optional[Language] = None

    def detect(self, text: str) -> Language:
        """
        Detecta el idioma de un texto.

        Args:
            text: texto del usuario

        Returns:
            Language detectado (es, en, fr, de). Default: español.

        La detección se cachea: una vez detectado con confianza alta,
        se mantiene para el resto de la sesión (el usuario no cambia
        de idioma a mitad de conversación).
        """
        if self._cached_language is not None:
            return self._cached_language

        if not text:
            return self.default_language

        language = self._detect_from_text(text)

        # Si la detección tiene confianza alta, cachear
        confidence = self._confidence(text, language)
        if confidence >= self.MIN_CONFIDENCE:
            self._cached_language = language
            logger.info(f"LanguageDetector: detected {language.value} (confidence: {confidence:.2f})")

        return language

    def _detect_from_text(self, text: str) -> Language:
        """Detecta idioma contando stopwords."""
        if not text or not text.strip():
            return self.default_language

        # Tokenizar (lowercase, quitar puntuación)
        tokens = self._tokenize(text)
        if not tokens:
            return self.default_language

        # Contar stopwords por idioma
        scores: Dict[Language, int] = {}
        for lang, stopwords in STOPWORDS.items():
            count = sum(1 for token in tokens if token in stopwords)
            scores[lang] = count

        # El idioma con más matches gana
        best_lang = max(scores, key=scores.get)
        best_score = scores[best_lang]

        if best_score == 0:
            return self.default_language

        # Si hay empate entre los dos mejores, usar default
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]:
            return self.default_language

        return best_lang

    def _confidence(self, text: str, language: Language) -> float:
        """Calcula confianza de la detección."""
        tokens = self._tokenize(text)
        if not tokens:
            return 0.0
        matches = sum(1 for t in tokens if t in STOPWORDS.get(language, set()))
        return matches / len(tokens)

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto: lowercase, quita puntuación, split."""
        # Quitar puntuación
        clean = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split por espacios
        tokens = clean.split()
        return tokens

    def get_profile(self, language: Language = None) -> LanguageProfile:
        """Devuelve el LanguageProfile para un idioma."""
        lang = language or self._cached_language or self.default_language
        return LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES[self.default_language])

    def reset(self):
        """Reset del cache (para tests o cambio de sesión)."""
        self._cached_language = None

    def get_stats(self) -> Dict[str, Any]:
        """Stats del detector."""
        return {
            "default_language": self.default_language.value,
            "cached_language": self._cached_language.value if self._cached_language else None,
            "supported_languages": [lang.value for lang in Language],
        }
