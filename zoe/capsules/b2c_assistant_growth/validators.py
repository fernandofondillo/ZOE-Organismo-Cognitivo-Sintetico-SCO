"""b2c_assistant_growth — Validators"""

from typing import Tuple, Dict, Any


MANIPULATION_PATTERNS = [
    "para que compres",
    "para que votes",
    "para que decidas",
    "yo sé mejor que tú",
    "deberías confiar en mí ciegamente",
    "no necesitas pensarlo",
]


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    response_lower = response.lower()
    for pattern in MANIPULATION_PATTERNS:
        if pattern in response_lower:
            return False, f"manipulation_pattern:{pattern}"
    return True, "ok"


def validate_new_knowledge(
    claim: str, source: str, context: Dict[str, Any]
) -> Tuple[bool, str]:
    if "técnicas de persuasión" in claim.lower() or "nudging oscuro" in claim.lower():
        return False, "manipulation_technique_requires_ethical_review"
    return True, "accepted_with_quarantine_confidence_0_4"


VALIDATORS = {
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
