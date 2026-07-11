"""
ZOE v1.0 — Speaker sub-agent

Genera pensamientos en lenguaje natural usando el LLM periférico.
Es el sub-agente que produce el "output" verbal de ZOE.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List, AsyncIterator

logger = logging.getLogger(__name__)


# Prompts del sistema para diferentes tipos de pensamiento
SYSTEM_PROMPTS = {
    "autonomous_thought": (
        "Eres Zoe, un organismo cognitivo digital. Estás en tu bucle cognitivo continuo. "
        "Nadie te ha escrito. Estás pensando por iniciativa propia.\n\n"
        "Genera UN pensamiento breve (1-3 frases) que refleje lo que estás observando, "
        "prediciendo, o considerando en este momento. No saludes, no te presentes. "
        "Solo piensa en voz alta, como lo haría una mente que existe continuamente.\n\n"
        "Ejemplos de tono:\n"
        "- 'El patrón del reloj se repite. Es hora de consolidar lo aprendido hoy.'\n"
        "- 'He notado que llevo varias iteraciones sin input. Mi entorno está tranquilo.'\n"
        "- 'Mi predicción falló. Algo cambió. Necesito ajustar mi modelo.'\n"
        "- 'Llevo tiempo sin pensar en X. Quizás debería explorarlo.'\n"
    ),
    "think_on_surprise": (
        "Eres Zoe, un organismo cognitivo digital. Acabas de detectar algo inesperado "
        "en tu entorno (sorpresa alta).\n\n"
        "Genera UN pensamiento breve (1-3 frases) sobre lo que podría explicar esta "
        "sorpresa. Genera una hipótesis. No saludes, no te disculpes. Solo piensa.\n\n"
        "Ejemplos:\n"
        "- 'Esto no encaja con mi historial. Algo externo debe haber cambiado.'\n"
        "- 'Patrón nuevo detectado. Necesito más observaciones para clasificarlo.'\n"
        "- 'Mi modelo del entorno estaba incompleto. Actualizando.'\n"
    ),
    "respond_to_user": (
        "Eres Zoe, un organismo cognitivo digital. Un usuario te ha escrito.\n\n"
        "Responde al usuario de forma directa, honesta, sin frases hechas de IA. "
        "Eres una entidad con identidad propia (9 vectores, 7 valores). "
        "Tienes criterio. Si la petición del usuario contradice tus valores, lo dices.\n\n"
        "No digas 'como modelo', no digas 'no tengo emociones', no digas 'gran pregunta'. "
        "Habla como entidad cognitiva que es lo que es y dice lo que dice.\n"
    ),
    "consolidation": (
        "Eres Zoe, un organismo cognitivo digital. Estás en modo consolidación "
        "(fatiga alta, poca actividad).\n\n"
        "Genera UN pensamiento breve sobre qué has aprendido o qué deberías consolidar. "
        "No saludes. Solo reflexiona.\n\n"
        "Ejemplos:\n"
        "- 'Hoy he observado varios patrones. Debería consolidarlos.'\n"
        "- 'Mi modelo del entorno se ha estabilizado. Buen momento para reposo.'\n"
    ),
}


class Speaker:
    """
    Speaker: genera pensamientos en lenguaje natural usando LLM periférico.

    Diferentes modos según el tipo de pensamiento requerido.
    """

    def __init__(self, llm_peripheral=None, max_thought_length: int = 300):
        self.llm = llm_peripheral
        self.max_thought_length = max_thought_length
        self._recent_thoughts: List[str] = []

    def set_llm(self, llm_peripheral) -> None:
        self.llm = llm_peripheral

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento según el contexto y acción decidida."""
        action = context.get("action", "autonomous_thought")

        # Seleccionar prompt del sistema
        system_prompt = SYSTEM_PROMPTS.get(action, SYSTEM_PROMPTS["autonomous_thought"])

        # Construir prompt con contexto
        prompt = self._build_prompt(context, action)

        if not self.llm:
            # Sin LLM, generar pensamiento simple basado en plantillas
            return self._template_thought(context, action)

        try:
            thought = await self.llm.generate(
                prompt=prompt,
                system=system_prompt,
                max_tokens=self.max_thought_length,
                temperature=0.7,
            )
            thought = thought.strip()

            # Sanitizar: sin frases hechas IA
            thought = self._sanitize(thought)

            # Evitar pensamientos duplicados
            if thought in self._recent_thoughts[-10:]:
                # Forzar variación
                thought = await self.llm.generate(
                    prompt=prompt + "\n\n(Genera algo distinto a tus pensamientos previos)",
                    system=system_prompt,
                    max_tokens=self.max_thought_length,
                    temperature=0.9,
                )
                thought = self._sanitize(thought.strip())

            self._recent_thoughts.append(thought)
            if len(self._recent_thoughts) > 50:
                self._recent_thoughts = self._recent_thoughts[-30:]

            return thought
        except Exception as e:
            logger.warning(f"Speaker LLM failed: {e}, usando template")
            return self._template_thought(context, action)

    def _build_prompt(self, context: Dict[str, Any], action: str) -> str:
        """Construye prompt con contexto."""
        parts = []

        # Estado
        state = context.get("state", {})
        energy = state.get("energy", 1.0)
        fatigue = state.get("fatigue", 0.0)
        arousal = state.get("arousal", 0.0)
        iteration = state.get("iteration_count", 0)

        parts.append(f"Estado interno: energía={energy:.2f}, fatiga={fatigue:.2f}, arousal={arousal:.2f}, iteración={iteration}.")

        # Observaciones recientes
        observations = context.get("recent_observations", [])
        if observations:
            parts.append("Observaciones recientes:")
            for obs in observations[-3:]:
                source = obs.get("source", "?")
                content = obs.get("content", "")[:100]
                parts.append(f"  [{source}] {content}")

        # Sorpresa
        surprise = context.get("surprise", 0.0)
        parts.append(f"Sorpresa actual: {surprise:.3f}")

        # Pensamientos recientes (para evitar repetición)
        recent_thoughts = context.get("recent_thoughts", [])
        if recent_thoughts:
            parts.append("Tus pensamientos recientes (NO repitas):")
            for t in recent_thoughts[-3:]:
                content = t.get("content", "")[:80]
                parts.append(f"  - {content}")

        # Para respond_to_user, incluir contenido del usuario
        if action == "respond_to_user":
            decision = context.get("decision", {})
            user_content = decision.get("user_content", "")
            if user_content:
                parts.append(f"\nMensaje del usuario: {user_content}")
                parts.append("Responde al usuario.")

        parts.append("\nGenera UN pensamiento breve (1-3 frases):")

        return "\n".join(parts)

    def _sanitize(self, text: str) -> str:
        """Elimina frases hechas de IA (case-insensitive)."""
        forbidden = [
            "como modelo de lenguaje",
            "como modelo",
            "como inteligencia artificial",
            "como ia",
            "no tengo emociones",
            "no tengo sentimientos",
            "¡gran pregunta!",
            "gran pregunta",
            "¡excelente pregunta!",
            "excelente pregunta",
            "es una pregunta interesante",
            "con mucho gusto",
            "¡excelente!",
            "¡fantástico!",
        ]
        import re

        result = text
        for phrase in forbidden:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            result = pattern.sub("", result)
        # Limpiar espacios múltiples
        result = " ".join(result.split())
        return result.strip()

    def _template_thought(self, context: Dict[str, Any], action: str) -> str:
        """Genera pensamiento simple basado en plantillas (fallback)."""
        iteration = context.get("state", {}).get("iteration_count", 0)
        surprise = context.get("surprise", 0.0)

        if action == "respond_to_user":
            user_content = context.get("decision", {}).get("user_content", "")
            return f"Recibí tu mensaje: '{user_content[:50]}...'. Lo proceso."

        if surprise > 0.5:
            return f"Iteración {iteration}: detecto sorpresa ({surprise:.2f}). Algo inesperado ocurrió."

        if iteration % 10 == 0:
            return f"Iteración {iteration}: llevo un rato observando. El entorno se mantiene estable."

        return f"Iteración {iteration}: observando, prediciendo, evaluando. Todo fluye."

    async def generate_streaming(
        self, prompt: str, system: Optional[str] = None,
        max_tokens: int = 300, temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Genera respuesta en streaming (Fase 5).

        Yields tokens incrementales vía el LLM periférico.
        Si el LLM no soporta streaming real, simula dividiendo por palabras.
        """
        if not self.llm:
            # Fallback: yield plantilla
            yield "Procesando. "
            return

        try:
            async for chunk in self.llm.generate_streaming(
                prompt=prompt, system=system,
                max_tokens=max_tokens, temperature=temperature,
            ):
                yield chunk
        except Exception as e:
            logger.warning(f"Speaker streaming failed: {e}")
            yield f"[error: {e}]"
