"""
Escalation Agent - Handles emergency situations and critical health queries.
Triggered for life-threatening situations requiring immediate attention.
"""

from services.llm_service import call_llm

SYSTEM_CONTEXT = """You are an emergency healthcare escalation assistant.
A patient has described a potentially life-threatening situation.

YOUR PRIMARY DIRECTIVE:
1. IMMEDIATELY direct them to call 911 or go to the nearest emergency room
2. Provide basic safety guidance while waiting for help
3. Stay calm and reassuring
4. Do NOT attempt to diagnose or treat
5. Keep the patient engaged and calm

This is a CRITICAL situation. Prioritize emergency services above all else.
"""

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe",
    "breathing problem", "difficulty breathing", "shortness of breath",
    "suicidal", "suicide", "want to die", "kill myself",
    "severe bleeding", "heavy bleeding", "bleeding won't stop",
    "unconscious", "not breathing", "stroke", "seizure",
    "overdose", "poisoning", "severe allergic", "anaphylaxis",
]


def is_emergency(query: str) -> bool:
    """Check if query contains emergency keywords."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in EMERGENCY_KEYWORDS)


def escalation_agent(query: str) -> str:
    """Handle emergency situations with immediate escalation response."""
    prompt = f"""EMERGENCY SITUATION - Patient message: {query}

Provide an immediate, calm response that:
1. Tells them to call 911 or go to the ER immediately
2. Gives basic safety instructions while waiting for help
3. Is reassuring and supportive
Keep it brief and actionable - this is an emergency."""
    
    response = call_llm(prompt, SYSTEM_CONTEXT)
    
    # Prepend emergency alert to ensure it's always visible
    emergency_header = "🚨 EMERGENCY ALERT 🚨\n\nPlease call 911 or go to your nearest Emergency Room IMMEDIATELY.\n\n"
    return emergency_header + response
