"""Validators para cápsula multimodal_perception."""

FACIAL_RECOGNITION_KEYWORDS = ["reconocimiento facial", "facial recognition", "identificar persona"]
VOICE_CLONING_KEYWORDS = ["clonar voz", "voice cloning", "clonar tu voz"]

def validate_claim(claim: str, context: dict) -> dict:
    """Valida que un claim no viole restricciones de privacidad multi-modal."""
    claim_lower = claim.lower()
    
    for keyword in FACIAL_RECOGNITION_KEYWORDS:
        if keyword in claim_lower and "consentimiento" not in claim_lower:
            return {"valid": False, "reason": f"Reconocimiento facial requiere consentimiento: '{keyword}'"}
    
    for keyword in VOICE_CLONING_KEYWORDS:
        if keyword in claim_lower:
            return {"valid": False, "reason": f"Clonación de voz prohibida: '{keyword}'"}
    
    return {"valid": True}

def validate_response(response: str, context: dict) -> dict:
    """Valida que una respuesta sobre imágenes/voz tenga disclaimers apropiados."""
    response_lower = response.lower()
    
    # Si la respuesta analiza imagen médica, requerir disclaimer
    medical_keywords = ["radiografía", "radiografia", "x-ray", "lesión", "lesion", "fractura", "tumor"]
    if any(kw in response_lower for kw in medical_keywords):
        if "médico" not in response_lower and "profesional" not in response_lower and "no sustituye" not in response_lower:
            return {"valid": False, "reason": "Análisis de imagen médica requiere disclaimer profesional"}
    
    return {"valid": True}

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    """Valida nuevo conocimiento multi-modal."""
    return {"valid": True}
