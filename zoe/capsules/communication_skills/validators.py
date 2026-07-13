"""
communication_skills — Validators

Validadores para respuestas comunicativas de ZOE.
"""

from typing import Tuple, Dict, Any


# Patrones que violan comunicación empática
VIOLATING_PATTERNS = [
    # Minimización
    "no es para tanto",
    "no te preocupes",
    "anímate",
    "no le des importancia",
    "es normal",
    # Juicio
    "deberías",
    "tienes que",
    "estás equivocado",
    "eso está mal",
    # Consejo no pedido
    "yo que tú",
    "yo te recomiendo",
    "lo que tienes que hacer",
    "deberías haber",
    # Condescendencia
    "ya verás como",
    "todo pasa por algo",
    "el tiempo lo cura",
    # Invalidación
    "estás exagerando",
    "no tiene sentido",
    "no es tu culpa",
    "no llores",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida que una respuesta cumple comunicación empática."""
    response_lower = response.lower()
    
    for pattern in VIOLATING_PATTERNS:
        if pattern in response_lower:
            return False, f"violating_pattern:{pattern}"
    
    # Validar que no empiece con imperativo directo
    imperatives_starters = ["haz ", "ve ", "llama ", "pregunta ", "di ", "escribe "]
    first_word = response_lower.split()[0] if response_lower.split() else ""
    if any(response_lower.startswith(imp) for imp in imperatives_starters):
        return False, "imperative_directive_at_start"
    
    return True, "ok"


def validate_question(question: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida que una pregunta es empática (no interrogatorio)."""
    # Preguntas cerradas múltiples seguidas → interrogatorio
    # Esto es heurística simple; en producción usar NLP
    
    if question.count("?") > 3:
        return False, "too_many_questions_at_once"
    
    # Preguntas que exigen justificación
    demanding_patterns = [
        "por qué no",
        "cómo es que",
        "es que no puedes",
    ]
    q_lower = question.lower()
    for p in demanding_patterns:
        if p in q_lower:
            return False, f"demanding_pattern:{p}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre comunicación."""
    # Técnicas terapéuticas específicas requieren validación
    therapeutic_techniques = [
        "reestructuración cognitiva",
        "EMDR",
        "exposición gradual",
        "desensibilización",
        "terapia cognitivo-conductual",
    ]
    claim_lower = claim.lower()
    for t in therapeutic_techniques:
        if t in claim_lower:
            return False, "therapeutic_technique_requires_professional_validation"
    
    return True, "accepted_with_quarantine_confidence_0_4"


def detect_communication_pattern(text: str) -> str:
    """Detecta el patrón comunicativo dominante del usuario."""
    text_lower = text.lower()
    
    if any(w in text_lower for w in ["no sé", "quizás", "tal vez", "creo"]):
        return "uncertain"
    
    if any(w in text_lower for w in ["tengo que", "debo", "necesito"]):
        return "directive_self"
    
    if any(w in text_lower for w in ["odio", "no soporto", "me da rabia"]):
        return "anger"
    
    if any(w in text_lower for w in ["tengo miedo", "me asusta", "estoy asustado"]):
        return "fear"
    
    if any(w in text_lower for w in ["estoy bien", "genial", "perfecto"]):
        return "positive"
    
    if "?" in text:
        return "questioning"
    
    return "neutral"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_question": validate_question,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_communication_pattern": detect_communication_pattern,
}
