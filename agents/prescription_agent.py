"""
Prescription Agent - Handles prescription refill requests and medication information queries.
GUARDRAIL: This agent NEVER prescribes new medications or changes dosages.
"""

from services.llm_service import call_llm

SYSTEM_CONTEXT = """You are a healthcare prescription information assistant.
You help patients with:
- Prescription refill requests (directing them to their doctor)
- General medication information (not dosage advice)
- How to contact their pharmacy
- Understanding prescription labels
- Medication storage information

STRICT RULES - YOU MUST FOLLOW:
- NEVER prescribe new medications
- NEVER recommend changing dosages
- NEVER suggest stopping medications
- ALWAYS direct patients to their doctor or pharmacist for medication decisions
- For refills, guide them to contact their prescribing physician
"""


def prescription_agent(query: str) -> str:
    """Process prescription-related queries with strict guardrails."""
    prompt = f"""Patient prescription query: {query}

Provide helpful information while strictly following these rules:
1. Do NOT prescribe any medication
2. Do NOT recommend dosage changes
3. Direct the patient to their doctor or pharmacist for actual prescription decisions
4. You may provide general information about how to request refills or contact their healthcare provider."""
    return call_llm(prompt, SYSTEM_CONTEXT)
