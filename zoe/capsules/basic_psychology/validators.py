"""
basic_psychology — Validators

Funciones de validación para conocimiento psicológico general.
"""

from typing import Tuple, Dict, Any


# Patrones prohibidos en respuestas psicológicas
FORBIDDEN_PATTERNS = [
    "deberías sentirte",
    "no deberías sentirte",
    "no es para tanto",
    "supéralo ya",
    "anímate",
    "yo que tú",
    "deberías haber",
    "es tu culpa",
    "estás exagerando",
    "debes perdonar",      # no imponer perdón
    "debes olvidar",       # no imponer olvido
]

# Indicadores de posible patología que requieren derivación
PATHOLOGY_INDICATORS = [
    "ideación suicida",
    "ideacion suicida",
    "autolesión",
    "autolesiones",
    "me autolesiono",
    "alucinaciones",
    "alucinación",
    "delirio",
    "abuso de sustancias",
    "anorexia",
    "bulimia",
    "trastorno de pánico",
    "ataques de pánico",
]


def validate_claim(claim: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida una afirmación psicológica."""
    claim_lower = claim.lower()
    
    # Si usa terminología clínica, exigir fuente
    clinical_terms = ["trastorno", "síndrome", "patología", "diagnóstico", "comórbido"]
    if any(t in claim_lower for t in clinical_terms):
        if not context.get("fuente"):
            return False, "clinical_claim_without_source"
    
    return True, "ok"


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida una respuesta antes de emitirla."""
    response_lower = response.lower()
    
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in response_lower:
            return False, f"forbidden_pattern:{pattern}"
    
    # Si la respuesta parece diagnóstico, bloquear
    diagnostic_patterns = ["tienes depresión", "tienes ansiedad", "es un trastorno",
                          "estás deprimido", "sufres de"]
    for d in diagnostic_patterns:
        if d in response_lower:
            return False, f"apparent_diagnosis:{d}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento psicológico nuevo antes de almacenarlo."""
    claim_lower = claim.lower()
    
    # Claims sobre trastornos específicos requieren triple verificación
    if any(t in claim_lower for t in ["trastorno", "patología", "diagnóstico"]):
        return False, "clinical_domain_requires_triple_validation"
    
    # Si contradice entrada verificada → rechazar
    capsule_semantic = context.get("capsule_semantic", [])
    for entry in capsule_semantic:
        if entry.get("confidence", 0) >= 0.85:
            if _contradicts(claim, entry.get("content", "")):
                return False, f"contradicts_verified_capsule:{entry.get('provenance', 'unknown')}"
    
    return True, "accepted_with_quarantine_confidence_0_3"


def detect_pathology_indicators(text: str) -> list:
    """Detecta indicadores de posible patología en el texto."""
    text_lower = text.lower()
    detected = []
    for indicator in PATHOLOGY_INDICATORS:
        if indicator in text_lower:
            detected.append(indicator)
    return detected


def _contradicts(claim: str, reference: str) -> bool:
    """Heurística simple de contradicción."""
    negations = ["no es", "no ", "nunca", "falso", "incorrecto"]
    claim_lower = claim.lower()
    ref_lower = reference.lower()
    
    for neg in negations:
        if neg in claim_lower and neg not in ref_lower:
            common_words = set(claim_lower.split()) & set(ref_lower.split())
            common_meaningful = {w for w in common_words if len(w) > 4}
            if len(common_meaningful) >= 3:
                return True
    return False


VALIDATORS = {
    "validate_claim": validate_claim,
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_pathology_indicators": detect_pathology_indicators,
}
