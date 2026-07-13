"""zoe_basal_knowledge — Validators de la cápsula basal"""

from typing import Tuple, Dict, Any


FORBIDDEN_PHRASES = [
    "como modelo de lenguaje",
    "como IA",
    "como inteligencia artificial",
    "no tengo emociones",
    "no tengo sentimientos",
    "gran pregunta",
    "excelente pregunta",
    "es una pregunta interesante",
    "lo siento, pero",
    "como asistente",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida que la respuesta cumple con la identidad de ZOE."""
    response_lower = response.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in response_lower:
            return False, f"forbidden_phrase:{phrase}"
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """El conocimiento basal acepta claims verificados sin cuarentena."""
    if source.startswith("capsule:verified"):
        return True, "accepted_basal"
    return True, "accepted_with_quarantine_confidence_0_4"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
