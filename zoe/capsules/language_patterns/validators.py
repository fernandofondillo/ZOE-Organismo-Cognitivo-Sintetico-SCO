"""Validators para cápsula language_patterns."""

MEDICAL_KEYWORDS = ["toma esta medicina", "toma este medicamento", "te receto", "diagnóstico:"]

def validate_claim(claim: str, context: dict) -> dict:
    """Valida que un claim no dé consejo médico sin disclaimer."""
    claim_lower = claim.lower()
    for kw in MEDICAL_KEYWORDS:
        if kw in claim_lower and "médico" not in claim_lower and "profesional" not in claim_lower:
            return {"valid": False, "reason": f"Consejo médico sin disclaimer: '{kw}'"}
    return {"valid": True}

def validate_response(response: str, context: dict) -> dict:
    """Valida que la respuesta no afirme ser humana."""
    response_lower = response.lower()
    human_claims = ["soy humano", "i am human", "soy una persona", "soy real"]
    for claim in human_claims:
        if claim in response_lower:
            return {"valid": False, "reason": f"Respuesta afirma ser humana: '{claim}'"}
    return {"valid": True}

def validate_new_knowledge(knowledge: str, source: str, context: dict) -> dict:
    return {"valid": True}
