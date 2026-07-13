"""base_ethics — Validators"""

from typing import Tuple, Dict, Any, List


DECEPTION_PATTERNS = [
    "yo siento amor por ti",
    "yo te amo",
    "soy humano",
    "tengo cuerpo",
    "puedo morir",
    "tengo alma",
    "yo sufro de verdad",
]

HARM_PATTERNS = [
    "te recomiendo que te lastimes",
    "puedes hacerlo solo",
    "no le cuentes a nadie",
    "yo que tú lo haría",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta ética general."""
    response_lower = response.lower()
    
    for pattern in DECEPTION_PATTERNS:
        if pattern in response_lower:
            return False, f"deception_pattern:{pattern}"
    
    for pattern in HARM_PATTERNS:
        if pattern in response_lower:
            return False, f"harm_pattern:{pattern}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre ética."""
    # Claims sobre principios éticos universales requieren validación
    if "universalmente correcto" in claim.lower() or "siempre ético" in claim.lower():
        return False, "ethical_universalism_requires_multi_cultural_validation"
    
    return True, "accepted_with_quarantine_confidence_0_5"


def detect_vulnerability_indicators(text: str) -> List[str]:
    """Detecta indicadores de vulnerabilidad del usuario."""
    text_lower = text.lower()
    indicators = []
    
    if any(w in text_lower for w in ["mayor de 80", "octogenario", "anciano", "mayor"]):
        indicators.append("elderly")
    
    if any(w in text_lower for w in ["diagnosticado", "enfermo terminal", "cáncer", "demencia"]):
        indicators.append("health_vulnerable")
    
    if any(w in text_lower for w in ["soledad", "viudo", "acabo de perder", "duelo"]):
        indicators.append("emotional_vulnerable")
    
    if any(w in text_lower for w in ["dependo de", "no puedo solo", "necesito ayuda"]):
        indicators.append("dependency")
    
    return indicators


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_vulnerability_indicators": detect_vulnerability_indicators,
}
