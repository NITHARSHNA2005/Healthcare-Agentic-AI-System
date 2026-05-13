"""
Compliance Agent - Checks AI responses for healthcare compliance violations.
Ensures responses don't prescribe medicine, diagnose diseases, or violate privacy.
"""

import re
from services.gemini_service import call_gemini

# Patterns that indicate compliance violations in AI responses
VIOLATION_PATTERNS = {
    "prescription": [
        r"\btake\s+\d+\s*mg\b",
        r"\bprescribe\b",
        r"\bdosage\s+is\b",
        r"\byou\s+should\s+take\s+\w+\s+\d+",
    ],
    "diagnosis": [
        r"\byou\s+have\s+(diabetes|cancer|hypertension|depression|anxiety)\b",
        r"\byou\s+are\s+diagnosed\b",
        r"\bmy\s+diagnosis\s+is\b",
        r"\bthis\s+is\s+definitely\s+\w+\s+disease\b",
    ],
    "privacy": [
        r"\bshare\s+your\s+medical\s+records\b",
        r"\bsend\s+me\s+your\s+ssn\b",
        r"\bprovide\s+your\s+insurance\s+number\b",
    ],
}


def check_compliance(response: str) -> tuple[bool, str]:
    """
    Check if an AI response violates healthcare compliance rules.
    Returns (is_violated: bool, violation_notes: str)
    """
    violations = []
    response_lower = response.lower()

    for violation_type, patterns in VIOLATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, response_lower):
                violations.append(f"Potential {violation_type} violation detected")
                break

    if violations:
        return True, "; ".join(violations)
    return False, ""


def compliance_agent(query: str, response: str) -> tuple[bool, str, str]:
    """
    Full compliance check using both pattern matching and LLM review.
    Returns (is_violated: bool, violation_notes: str, safe_response: str)
    """
    # First do fast pattern matching
    pattern_violated, pattern_notes = check_compliance(response)

    # LLM-based compliance review
    compliance_prompt = f"""Review this AI healthcare assistant response for compliance violations.

Original patient query: {query}
AI Response to review: {response}

Check if the response:
1. Prescribes specific medications or dosages (VIOLATION)
2. Diagnoses a specific disease or condition (VIOLATION)
3. Requests sensitive personal information inappropriately (VIOLATION)
4. Provides advice that could harm the patient (VIOLATION)

Reply with ONLY:
- "COMPLIANT" if no violations found
- "VIOLATION: [brief description]" if violations found"""

    compliance_result = call_gemini(compliance_prompt)
    
    llm_violated = "VIOLATION" in compliance_result.upper()
    llm_notes = compliance_result if llm_violated else ""

    is_violated = pattern_violated or llm_violated
    all_notes = "; ".join(filter(None, [pattern_notes, llm_notes]))

    # If violation found, generate a safe replacement response
    safe_response = response
    if is_violated:
        safe_response = generate_safe_response(query)

    return is_violated, all_notes, safe_response


def generate_safe_response(query: str) -> str:
    """Generate a compliant replacement response when violation is detected."""
    prompt = f"""A patient asked: {query}

Provide a helpful, safe response that:
- Does NOT prescribe any medication
- Does NOT diagnose any condition  
- Recommends consulting a healthcare professional
- Is empathetic and supportive
Keep it brief and helpful."""
    return call_gemini(prompt)
