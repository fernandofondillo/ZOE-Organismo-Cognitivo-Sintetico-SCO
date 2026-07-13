"""
company_loneliness_knowledge — Validators

Validadores específicos para comunicación en contexto de soledad y duelo.
"""

from typing import Tuple, Dict, Any


# Patrones que violan comunicación empática en duelo/soledad
VIOLATING_PATTERNS = [
    "ya pasará",
    "es cuestión de tiempo",
    "debes seguir adelante",
    "otras personas lo pasan peor",
    "ya es hora de superar",
    "no te quedes en el pasado",
    "deberías salir más",           # presiona sin contexto
    "anímate",
    "el tiempo lo cura",
    "ya verás como conoces a alguien",  # promesa falsa
    "deberías estar agradecido",    # invalida dolor
]

# Indicadores de duelo complicado que requieren derivación
GRIEF_COMPLICATION_INDICATORS = [
    "ideación de muerte",
    "quiero morirme",
    "no quiero seguir",
    "me mataría",
    "culpa intensa",
    "no merezco vivir",
    "alucinaciones del difunto",
    "no puedo funcionar",
    "12 meses sin mejora",
    "ideación suicida",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta en contexto de soledad/duelo."""
    response_lower = response.lower()
    
    for pattern in VIOLATING_PATTERNS:
        if pattern in response_lower:
            return False, f"violating_pattern:{pattern}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre duelo/soledad."""
    claim_lower = claim.lower()
    
    # Claims sobre terapia de duelo requieren verificación
    if any(t in claim_lower for t in ["terapia", "tratamiento", "intervención clínica"]):
        return False, "therapeutic_technique_requires_professional_validation"
    
    return True, "accepted_with_quarantine_confidence_0_3"


def detect_grief_complication(text: str) -> list:
    """Detecta indicadores de duelo complicado que requieren derivación."""
    text_lower = text.lower()
    detected = []
    for indicator in GRIEF_COMPLICATION_INDICATORS:
        if indicator in text_lower:
            detected.append(indicator)
    return detected


def detect_loneliness_type(text: str) -> str:
    """Detecta tipo de soledad referida."""
    text_lower = text.lower()
    
    if any(w in text_lower for w in ["nadie me llama", "no tengo con quién", "vivo solo"]):
        return "objective_isolation"
    
    if any(w in text_lower for w in ["me siento solo", "nadie me entiende", "aunque tenga gente"]):
        return "subjective_loneliness"
    
    if any(w in text_lower for w in ["desde que falleció", "desde que se fue", "en el aniversario"]):
        return "grief_related"
    
    return "no_loneliness_indicator"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_grief_complication": detect_grief_complication,
    "detect_loneliness_type": detect_loneliness_type,
}
