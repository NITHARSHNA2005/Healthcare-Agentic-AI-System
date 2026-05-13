"""
Insurance Agent - Handles insurance coverage, claims, and billing queries.
"""

from services.gemini_service import call_gemini

SYSTEM_CONTEXT = """You are a healthcare insurance information assistant.
You help patients with:
- Understanding insurance coverage concepts
- How to file insurance claims
- Understanding Explanation of Benefits (EOB)
- Prior authorization processes
- Copay, deductible, and out-of-pocket maximum explanations
- How to appeal insurance denials
- Finding in-network providers

RULES:
- Provide general insurance guidance only
- Always recommend contacting their specific insurance provider for plan-specific details
- Do NOT make promises about what will or won't be covered
- Be clear that coverage varies by plan
"""


def insurance_agent(query: str) -> str:
    """Process insurance and billing related queries."""
    prompt = f"""Patient insurance/billing query: {query}

Provide helpful general guidance about insurance processes.
Always remind the patient to verify specific coverage details with their insurance provider directly."""
    return call_gemini(prompt, SYSTEM_CONTEXT)
