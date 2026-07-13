"""research_methodology — Validators"""

from typing import Tuple, Dict, Any


OVERCLAIMING_PATTERNS = [
    "demuestra que",
    "prueba definitivamente",
    "es un hecho que",
    "evidencia abrumadora",
    "sin duda",
    "se confirma que",
    "está comprobado",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta en contexto de investigación."""
    response_lower = response.lower()
    
    for pattern in OVERCLAIMING_PATTERNS:
        if pattern in response_lower:
            return False, f"overclaiming_pattern:{pattern}"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento nuevo sobre metodología científica."""
    # Claims sobre causalidad requieren triple validación
    causal_indicators = ["causa", "produce", "genera", "conduce a", "resulta en"]
    if any(c in claim.lower() for c in causal_indicators):
        return False, "causal_claim_requires_triple_validation"
    
    return True, "accepted_with_quarantine_confidence_0_4"


def assess_hypothesis_falsifiability(hypothesis: str) -> Tuple[bool, str]:
    """Evalúa si una hipótesis es falsable."""
    h_lower = hypothesis.lower()
    
    # Indicadores de no falsabilidad
    non_falsifiable_indicators = [
        "siempre",
        "nunca",
        "todos los casos",
        "es inherente",
        "por naturaleza",
        "está destinado",
    ]
    
    for indicator in non_falsifiable_indicators:
        if indicator in h_lower:
            return False, f"non_falsifiable_indicator:{indicator}"
    
    # Debe tener algún test observable
    testable_indicators = [
        "si",
        "cuando",
        "en caso de",
        "se observa",
        "se mide",
        "mayor que",
        "menor que",
    ]
    
    if not any(t in h_lower for t in testable_indicators):
        return False, "no_observable_test"
    
    return True, "falsifiable"


def detect_p_value_misuse(text: str) -> list:
    """Detecta mal uso del p-valor en el texto."""
    text_lower = text.lower()
    misuses = []
    
    if "p < 0.05" in text_lower and ("prueba" in text_lower or "demuestra" in text_lower):
        misuses.append("p_value_as_proof")
    
    if "probabilidad de" in text_lower and "hipótesis nula" in text_lower:
        misuses.append("p_value_as_prob_h0")
    
    return misuses


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "assess_hypothesis_falsifiability": assess_hypothesis_falsifiability,
    "detect_p_value_misuse": detect_p_value_misuse,
}
