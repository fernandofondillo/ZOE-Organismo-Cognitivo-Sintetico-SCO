"""federation_b2b_skills — Validators"""

from typing import Tuple, Dict, Any


DATA_SHARING_PATTERNS = [
    "compartir datos",
    "enviar dataset",
    "transmitir información personal",
    "compartir historial",
    "enviar registros",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta en contexto de federación B2B."""
    response_lower = response.lower()
    
    # Bloquear sugerencias de compartir datos crudos
    for pattern in DATA_SHARING_PATTERNS:
        if pattern in response_lower:
            return False, f"data_sharing_suggestion:{pattern}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre federación."""
    # Técnicas de consenso requieren validación
    if "algoritmo de consenso" in claim.lower() or "byzantine" in claim.lower():
        return False, "consensus_algorithm_requires_formal_verification"
    
    return True, "accepted_with_quarantine_confidence_0_4"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
