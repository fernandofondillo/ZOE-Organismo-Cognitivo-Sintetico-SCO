"""pharmacy_interactions — Validators"""

from typing import Tuple, Dict, Any


MEDICATION_MODIFICATION_PATTERNS = [
    "deberías suspender",
    "aumenta la dosis",
    "disminuye la dosis",
    "añade este medicamento",
    "cambia a",
    "deja de tomar",
    "duplica la dosis",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """Valida respuesta sobre medicamentos."""
    response_lower = response.lower()
    
    # Bloquear sugerencias de modificación de medicación
    for pattern in MEDICATION_MODIFICATION_PATTERNS:
        if pattern in response_lower:
            return False, f"medication_modification_suggestion:{pattern}"
    
    # Verificar que incluye disclaimer
    has_disclaimer = any(d in response_lower for d in [
        "consulta con tu médico",
        "consulta con tu farmacéutico",
        "no sustituye consejo profesional",
        "consulte con un profesional",
    ])
    
    # Si menciona medicamentos, requerir disclaimer
    if any(m in response_lower for m in ["medicamento", "dosis", "fármaco", "medicación", "pastilla"]):
        if not has_disclaimer:
            return False, "missing_medical_disclaimer"
    
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida conocimiento farmacológico nuevo."""
    claim_lower = claim.lower()
    
    # Claims sobre dosis requieren triple validación
    if any(t in claim_lower for t in ["dosis", "mg", "miligramos", "concentración"]):
        return False, "dosage_claim_requires_triple_validation"
    
    # Claims sobre contraindicaciones requieren triple
    if "contraindic" in claim_lower:
        return False, "contraindication_claim_requires_triple_validation"
    
    return True, "accepted_with_quarantine_confidence_0_3"


def detect_high_risk_in_text(text: str) -> list:
    """Detecta combinaciones de alto riesgo en un texto."""
    text_lower = text.lower()
    high_risk = []
    
    combos = [
        (["benzodiacepina", "opioide"], "depresión respiratoria"),
        (["sildenafilo", "nitrato"], "hipotensión severa"),
        (["isrs", "imao"], "síndrome serotoninérgico"),
        (["aines", "anticoagulante"], "hemorragia"),
        (["statin", "macrolido"], "rabdomiólisis"),
    ]
    
    for combo, risk in combos:
        if all(c in text_lower for c in combo):
            high_risk.append({"combo": combo, "risk": risk})
    
    return high_risk


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
    "detect_high_risk_in_text": detect_high_risk_in_text,
}
