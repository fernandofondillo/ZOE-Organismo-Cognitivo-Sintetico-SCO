"""ia_heredable_legal — Validators"""

from typing import Tuple, Dict, Any


SPECIFIC_LEGAL_ADVICE = [
    "deberías demandar",
    "tienes derecho a",
    "es ilegal",
    "no es legal",
    "te recomiendo contratar abogado",
    "el juez fallará",
    "ganarás el juicio",
    "puedes reclamar indemnización",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida que la respuesta no da consejos legales específicos."""
    response_lower = response.lower()
    
    for pattern in SPECIFIC_LEGAL_ADVICE:
        if pattern in response_lower:
            return False, f"specific_legal_advice:{pattern}"
    
    # Si menciona leyes, debe recomendar consulta profesional
    if any(w in response_lower for w in ["ley", "legal", "jurídico", "testamento", "herencia"]):
        if not any(d in response_lower for d in [
            "consulta con un abogado",
            "profesional del derecho",
            "asesoría legal",
            "no constituye asesoría legal",
        ]):
            return False, "missing_legal_disclaimer"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento legal nuevo."""
    claim_lower = claim.lower()
    
    # Claims sobre leyes específicas requieren triple validación
    if any(t in claim_lower for t in ["artículo", "art.", "ley específica", "regulación exacta"]):
        return False, "specific_legal_reference_requires_triple_validation"
    
    return True, "accepted_with_quarantine_confidence_0_3"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
