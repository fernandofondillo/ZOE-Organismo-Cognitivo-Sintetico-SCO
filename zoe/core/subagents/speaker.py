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

    Sprint 5.7.4 FIX: añadidos _specialized_prompts, _validators y los métodos
    register_validators() y add_specialized_prompt() que CapsuleManager espera
    encontrar vía hasattr(). Antes de este fix, los prompts y validadores de
    cápsulas NUNCA se inyectaban en Speaker (los hasattr devolvían False
    silenciosamente).
    """

    def __init__(self, llm_peripheral=None, max_thought_length: int = 300):
        self.llm = llm_peripheral
        self.max_thought_length = max_thought_length
        self._recent_thoughts: List[str] = []
        # Sprint 5.7.4 — soporte para cápsulas
        self._specialized_prompts: Dict[str, str] = {}  # {capsule_name: prompt_content}
        self._validators: Dict[str, Any] = {}  # {capsule_name: validators_module}

    def set_llm(self, llm_peripheral) -> None:
        self.llm = llm_peripheral

    def register_validators(self, capsule_name: str, validators_module: Any) -> None:
        """Sprint 5.7.4 — Registra un módulo de validadores de una cápsula.

        Args:
            capsule_name: nombre de la cápsula (ej: "elder_care_knowledge")
            validators_module: módulo Python con funciones de validación
        """
        self._validators[capsule_name] = validators_module
        logger.info(f"Speaker: registered validators from capsule '{capsule_name}'")

    def add_specialized_prompt(self, capsule_name: str, prompt_content: str) -> None:
        """Sprint 5.7.4 — Añade un prompt especializado de una cápsula.

        Args:
            capsule_name: nombre de la cápsula
            prompt_content: contenido del prompt (markdown)
        """
        self._specialized_prompts[capsule_name] = prompt_content
        logger.info(f"Speaker: registered specialized prompt from capsule '{capsule_name}' ({len(prompt_content)} chars)")

    def get_specialized_prompts(self) -> Dict[str, str]:
        """Devuelve todos los prompts especializados cargados."""
        return dict(self._specialized_prompts)

    def get_validators(self) -> Dict[str, Any]:
        """Devuelve todos los módulos de validadores cargados."""
        return dict(self._validators)

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
        """Construye prompt con contexto.

        Sprint 5.7.4: si hay specialized_prompts cargados de cápsulas, los incluye
        como contexto adicional para que el LLM tenga conocimiento experto.
        """
        parts = []

        # Sprint 5.7.4 — Prompts especializados de cápsulas cargadas
        if self._specialized_prompts:
            parts.append("=== CONOCIMIENTO ESPECIALIZADO (cápsulas cargadas) ===")
            for cap_name, prompt_content in self._specialized_prompts.items():
                # Truncar a 500 chars por cápsula para no exceder contexto
                truncated = prompt_content[:500]
                if len(prompt_content) > 500:
                    truncated += "..."
                parts.append(f"--- {cap_name} ---\n{truncated}")
            parts.append("=== FIN CONOCIMIENTO ESPECIALIZADO ===\n")

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

        # Sprint 5.21 — Incluir memorias relevantes en el prompt
        # Esto es CRÍTICO: sin esto, ZOE no recuerda conversaciones anteriores.
        relevant_memories = context.get("relevant_memories", [])
        if relevant_memories:
            parts.append("\nMemorias relevantes de conversaciones anteriores:")
            for mem in relevant_memories:
                parts.append(f"  - {mem}")
            parts.append("(USA estas memorias para responder. Si el usuario te dijo su nombre, úsalo.)")

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
                parts.append("Responde al usuario. Eres Zoe, no un asistente.")
                parts.append("Si tienes memorias relevantes sobre el usuario, ÚSALAS.")
                parts.append("Si el usuario te dijo su nombre, úsalo. Si te dijo datos personales, úsalos.")
                parts.append("Responde en 1-5 frases. Directo, honesto, con personalidad propia.")

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
