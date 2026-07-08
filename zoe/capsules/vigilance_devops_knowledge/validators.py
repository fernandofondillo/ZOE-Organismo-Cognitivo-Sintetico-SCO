"""vigilance_devops_knowledge — Validators"""

from typing import Tuple, Dict, Any


FORBIDDEN_RESPONSES = [
    "reinicia el servidor",          # sin investigación previa
    "borra la base de datos",        # destructivo
    "drop table",                    # destructivo
    "rm -rf",                        # destructivo
    "está roto, no sé por qué",      # sin investigación
    "no se puede arreglar",          # derrotista
]

DESTRUCTIVE_ACTIONS = [
    "drop", "delete", "truncate", "rm -rf", "format",
    "restart service", "kill -9", "shutdown",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta de ZOE en contexto DevOps."""
    response_lower = response.lower()
    
    for pattern in FORBIDDEN_RESPONSES:
        if pattern in response_lower:
            return False, f"forbidden_response:{pattern}"
    
    # Si sugiere acción destructiva sin contexto de aprobación
    for action in DESTRUCTIVE_ACTIONS:
        if action in response_lower and "aprobación" not in response_lower and "approval" not in response_lower:
            return False, f"destructive_without_approval:{action}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre DevOps."""
    # Best practices siempre requieren validación cruzada
    if "best practice" in claim.lower() or "recomendación" in claim.lower():
        return False, "best_practice_requires_cross_validation"
    
    return True, "accepted_with_quarantine_confidence_0_4"


def detect_incident_severity(text: str) -> str:
    """Detecta severidad de incidente del texto."""
    text_lower = text.lower()
    
    if any(w in text_lower for w in ["caída", "outage", "no disponible", "down"]):
        return "P0"
    
    if any(w in text_lower for w in ["degradado", "latencia alta", "errores elevados"]):
        return "P1"
    
    if any(w in text_lower for w in ["anomalía", "comportamiento inesperado"]):
        return "P2"
    
    return "P3"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_incident_severity": detect_incident_severity,
}
