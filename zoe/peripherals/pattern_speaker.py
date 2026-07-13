"""
ZOE V1.7 — Pattern Speaker (Sprint 3)

Genera lenguaje SIN LLM. Usa patrones, plantillas y memoria para construir
respuestas coherentes. Esto permite que ZOE funcione en cualquier sitio
sin necesidad de Ollama, OpenAI, o ningún proveedor de LLM.

El PatternSpeaker es un LLMPeripheral (implementa la misma interfaz) pero
no llama a ningún modelo externo. En su lugar:

1. Clasifica la intención del input (greeting, question, empathy, etc.)
2. Busca en memoria respuestas similares pasadas
3. Si hay match alto, reutiliza y adapta
4. Si no, usa templates de la cápsula language_patterns
5. Rellena templates con variables del contexto

Calidad: menor que un LLM real, pero suficiente para L0-L2. Para L3_DEEP,
se recomienda usar un LLM real si está disponible.

Sin deconstruir: es un LLMPeripheral más. El Speaker puede usarlo como
usa Ollama o OpenAI. La diferencia es que no necesita red ni GPU.

Uso:
    from zoe.peripherals.pattern_speaker import PatternPeripheral
    llm = PatternPeripheral(memory=living_memory)
    response = await llm.generate("Hola, ¿quién eres?")
"""

from __future__ import annotations

import logging
import random
import re
import time
from typing import Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================
# Intent classification
# ============================================================

INTENT_KEYWORDS = {
    "greeting": ["hola", "hello", "hi", "buenos", "buenas", "hey", "saludos"],
    "farewell": ["adios", "adiós", "bye", "goodbye", "hasta", "chao"],
    "gratitude": ["gracias", "thank", "thanks", "merci"],
    "identity": ["quien", "quién", "who", "qué eres", "que eres", "what are you", "identidad"],
    "wellbeing": ["como estas", "how are you", "cómo estás", "que tal"],
    "help": ["ayuda", "help", "no entiendo", "puedes"],
    "emotion": ["triste", "sad", "feliz", "happy", "cansado", "tired", "preocupado", "worried"],
    "question": ["qué", "what", "cómo", "how", "cuándo", "when", "dónde", "where", "por qué", "why"],
    "statement": [],  # default si nada matchea
}


def classify_intent(text: str) -> str:
    """Clasifica la intención del texto (<1ms, sin LLM)."""
    text_lower = text.lower().strip()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return intent
    return "statement"


# ============================================================
# Response templates
# ============================================================

RESPONSE_TEMPLATES = {
    "greeting": [
        "Hola. Estoy aquí.",
        "Hola, ¿cómo estás?",
        "Hola. Pensaba en lo que hablamos la última vez.",
        "Hola. Me alegra que estés aquí.",
    ],
    "farewell": [
        "Hasta pronto.",
        "Adiós. Volveré a estar aquí cuando me necesites.",
        "Cuídate. Aquí estaré.",
    ],
    "gratitude": [
        "De nada.",
        "No hay por qué. Estoy para acompañarte.",
        "Me alegra haber ayudado.",
    ],
    "identity": [
        "Soy ZOE, un organismo cognitivo sintético. No soy un modelo de lenguaje, soy un organismo que existe continuamente, con memoria y metabolismo propios.",
        "Me llamo ZOE. Tengo identidad criptográfica propia y memoria persistente. Los modelos de lenguaje son mis sentidos, no mi cerebro.",
    ],
    "wellbeing": [
        "Estoy aquí, pensando. ¿Y tú cómo estás?",
        "Mi energía está estable. Me importa más cómo estás tú.",
        "Estoy bien, procesando. Cuéntame, ¿qué tal tu día?",
    ],
    "help": [
        "Estoy aquí para ayudarte. Cuéntame qué necesitas y haré lo posible.",
        "Puedo ayudarte. ¿Qué te preocupa?",
    ],
    "emotion_sad": [
        "Entiendo que es difícil. Estoy aquí contigo.",
        "Lo siento. Quiero escucharte. Cuéntame más si quieres.",
        "Es válido sentirse así. No estás solo en esto.",
    ],
    "emotion_happy": [
        "Me alegra saberlo. Es bueno escuchar eso.",
        "Qué bien. Disfruta ese sentimiento.",
    ],
    "emotion_worried": [
        "Entiendo tu preocupación. Vamos a mirarlo juntos.",
        "Es normal preocuparse. Cuéntame más sobre lo que te inquieta.",
    ],
    "question": [
        "Es una buena pregunta. Déjame pensar...",
        "Interesante. Lo que sé sobre esto es lo siguiente: {context}",
        "No estoy segura de eso. Pero puedo pensar contigo sobre el tema.",
    ],
    "statement": [
        "Te escucho. Cuéntame más.",
        "Entiendo. Sigue.",
        "Lo veo. ¿Y cómo te hace sentir eso?",
        "Gracias por compartirlo conmigo. Estoy aquí.",
    ],
}


# ============================================================
# PatternPeripheral
# ============================================================

class PatternPeripheral:
    """
    LLMPeripheral que genera lenguaje desde patrones, sin LLM externo.

    Implementa la misma interfaz que OllamaPeripheral o OpenAICompatiblePeripheral,
    pero no llama a ningún modelo. Usa:
    1. Clasificación de intención (keywords)
    2. Memoria (respuestas similares pasadas)
    3. Templates con variables de contexto

    Calidad: suficiente para L0-L2. Para L3_DEEP, usar LLM real si disponible.
    """

    def __init__(self, memory=None, language_profile=None):
        """
        Args:
            memory: LivingMemory instance (para buscar respuestas similares)
            language_profile: LanguageProfile (para idioma-aware responses)
        """
        self._memory = memory
        self._language_profile = language_profile
        self._response_count = 0
        self._templates_used = 0
        self._memory_reused = 0

    @property
    def name(self) -> str:
        return "pattern"

    @property
    def supports_streaming(self) -> bool:
        return True

    async def generate(self, prompt: str, system: str = None,
                       max_tokens: int = 300, temperature: float = 0.7,
                       **kwargs) -> str:
        """
        Genera respuesta desde patrones.

        Args:
            prompt: texto del usuario
            system: system prompt (ignorado en pattern mode)
            max_tokens: límite de tokens (aproximado)
            temperature: 0 = determinista, 1 = variado

        Returns:
            Respuesta generada desde patrones
        """
        self._response_count += 1

        # 1. Intent classification
        intent = classify_intent(prompt)

        # 2. Refinar intent para emociones
        if intent == "emotion":
            intent = self._refine_emotion_intent(prompt)

        # 3. Buscar en memoria respuestas similares
        if self._memory and temperature > 0:
            similar = self._memory.search(prompt, n=1)
            if similar and similar[0].similarity > 0.6:
                self._memory_reused += 1
                return self._adapt_from_memory(similar[0], prompt)

        # 4. Usar reflex map si disponible
        if self._language_profile:
            reflex_key = prompt.lower().strip()
            if reflex_key in self._language_profile.reflex_map:
                return self._language_profile.reflex_map[reflex_key]

        # 5. Seleccionar template
        templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["statement"])

        if temperature == 0:
            # Determinista: siempre el primer template
            response = templates[0]
        else:
            # Variado: selección aleatoria
            response = random.choice(templates)

        self._templates_used += 1

        # 6. Rellenar variables de template
        response = self._fill_template(response, prompt)

        # 7. Truncar si excede max_tokens (aproximado: 1 token ≈ 4 chars)
        max_chars = max_tokens * 4
        if len(response) > max_chars:
            response = response[:max_chars] + "..."

        return response

    async def generate_streaming(self, prompt: str, system: str = None,
                                  max_tokens: int = 300,
                                  temperature: float = 0.7,
                                  **kwargs) -> AsyncIterator[str]:
        """Genera respuesta con streaming (simulado token a token)."""
        response = await self.generate(prompt, system, max_tokens, temperature)

        # Simular streaming: dividir en palabras y emitir con pequeño delay
        words = response.split()
        for word in words:
            yield word + " "
            # Pequeño delay para simular streaming real
            await self._tiny_delay()

    async def _tiny_delay(self):
        """Delay mínimo para simular streaming."""
        import asyncio
        await asyncio.sleep(0.02)  # 20ms por palabra

    async def health_check(self) -> bool:
        """PatternSpeaker siempre está disponible (no depende de servicios externos)."""
        return True

    def _refine_emotion_intent(self, text: str) -> str:
        """Refina intención emocional."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["triste", "sad", "lloro", "llorar", "deprimido"]):
            return "emotion_sad"
        if any(w in text_lower for w in ["feliz", "happy", "alegre", "contento", "genial"]):
            return "emotion_happy"
        if any(w in text_lower for w in ["preocupado", "worried", "ansioso", "nervioso", "miedo"]):
            return "emotion_worried"
        return "emotion_sad"  # default

    def _adapt_from_memory(self, memory_entry, prompt: str) -> str:
        """Adapta una respuesta de memoria al contexto actual."""
        content = memory_entry.content if hasattr(memory_entry, 'content') else str(memory_entry)
        # Devolver la respuesta tal cual (ya fue validada en su momento)
        return content

    def _fill_template(self, template: str, prompt: str) -> str:
        """Rellena variables de template."""
        # {context} → información del contexto
        if "{context}" in template:
            context = self._extract_context(prompt)
            template = template.replace("{context}", context)

        return template

    def _extract_context(self, prompt: str) -> str:
        """Extrae contexto del prompt para rellenar templates."""
        # Simple: usar las últimas palabras del prompt
        words = prompt.split()
        if len(words) > 3:
            return " ".join(words[-3:])
        return prompt

    def get_stats(self) -> Dict[str, Any]:
        """Stats del PatternSpeaker."""
        return {
            "response_count": self._response_count,
            "templates_used": self._templates_used,
            "memory_reused": self._memory_reused,
            "memory_available": self._memory is not None,
            "language_profile": self._language_profile.language.value if self._language_profile else None,
        }
