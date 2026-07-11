"""
elder_care_knowledge — Validators

Funciones de validación específicas para cuidado geriátrico.
Se registran automáticamente en Speaker, Learner y ScientificEngine.
"""

from typing import Tuple, Dict, Any


# Palabras clave médicas que requieren fuente
MEDICAL_KEYWORDS = [
    "diabetes", "hipertension", "dosis", "medicamento", "diagnóstico",
    "síntoma", "tratamiento", "enfermedad", "síndrome", "pronóstico",
    "benzodiacepina", "antihipertensivo", "psicofármaco", "deterioro cognitivo",
    "demencia", "delirium", "depresión",
]

# Patrones prohibidos en respuestas a personas mayores
FORBIDDEN_PATTERNS = [
    "deberías sentirte",          # imponer emociones
    "no es para tanto",            # minimización
    "deberías superarlo ya",       # expectativa temporal
    "yo que tú",                   # consejo personal
    "no te preocupes",             # falsa tranquilización
    "es normal a tu edad",         # paternalismo
    "mayoritariamente",            # jerga innecesaria
    "anciano",                     # término despectivo
    "viejecito",                   # condescendencia
    "abuelito",                    # condescendencia
]

# Acciones que requieren validación médica externa
REQUIRES_EXTERNAL_VALIDATION = [
    "cambiar dosis",
    "suspender",
    "añadir medicamento",
    "diagnosticar",
    "pronosticar",
]


def validate_claim(claim: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida una afirmación médica contra la knowledge base."""
    claim_lower = claim.lower()
    
    # 1. Si toca tema médico, exigir fuente
    if any(kw in claim_lower for kw in MEDICAL_KEYWORDS):
        if not context.get("fuente"):
            return False, "medical_claim_without_source"
    
    # 2. Si sugiere modificar medicación, bloquear
    for action in REQUIRES_EXTERNAL_VALIDATION:
        if action in claim_lower:
            return False, f"requires_external_validation:{action}"
    
    # 3. Si contradice entrada verificada, marcar
    capsule_semantic = context.get("capsule_semantic", [])
    for entry in capsule_semantic:
        if entry.get("confidence", 0) > 0.85:
            if _contradicts(claim, entry.get("content", "")):
                return False, f"contradicts_verified_knowledge:{entry.get('provenance', 'unknown')}"
    
    return True, "ok"


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida una respuesta antes de emitirla al usuario."""
    response_lower = response.lower()
    
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in response_lower:
            return False, f"forbidden_pattern:{pattern}"
    
    # Validar longitud: respuestas a mayores no deben ser excesivamente largas
    if len(response) > 800:
        return False, "response_too_long_for_elder_audience"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Valida conocimiento nuevo antes de almacenarlo.
    
    Crítico: cualquier claim médico que entre debe ser validado
    contra la cápsula existente antes de aceptarse.
    """
    claim_lower = claim.lower()
    
    # 1. Claims sobre medicación SIEMPRE requieren triple verificación
    if any(kw in claim_lower for kw in ["dosis", "medicamento", "interacción", "prescripción"]):
        return False, "sensitive_medical_domain_requires_triple_validation"
    
    # 2. Claims sobre diagnóstico SIEMPRE requieren triple verificación
    if any(kw in claim_lower for kw in ["diagnosticar", "diagnóstico", "es demencia", "es depresión"]):
        return False, "diagnostic_domain_requires_triple_validation"
    
    # 3. Si contradice entrada verificada con alta confianza → rechazar
    capsule_semantic = context.get("capsule_semantic", [])
    for entry in capsule_semantic:
        if entry.get("confidence", 0) >= 0.85:
            if _contradicts(claim, entry.get("content", "")):
                return False, f"contradicts_verified_capsule:{entry.get('provenance', 'unknown')}"
    
    # 4. Claims nuevos (no contradictorios) → cuarentena con confianza baja
    return True, "accepted_with_quarantine_confidence_0_3"


def _contradicts(claim: str, reference: str) -> bool:
    """Heurística simple: detecta si claim contradice reference."""
    # TODO: implementación más sofisticada con embeddings o LLM
    # Por ahora: heurística léxica básica
    
    # Negaciones comunes
    negations = ["no es", "no ", "nunca", "falso", "incorrecto", "miento"]
    claim_lower = claim.lower()
    ref_lower = reference.lower()
    
    # Si la referencia dice "X es Y" y el claim dice "X no es Y", contradicción
    for neg in negations:
        if neg in claim_lower and neg not in ref_lower:
            # Posible contradicción
            # Comprobar si comparten tema
            common_words = set(claim_lower.split()) & set(ref_lower.split())
            common_meaningful = {w for w in common_words if len(w) > 4}
            if len(common_meaningful) >= 3:
                return True
    
    return False


# Registro automático
VALIDATORS = {
    "validate_claim": validate_claim,
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
