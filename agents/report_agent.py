"""
Report Explanation Agent - Explains medical reports and lab results in simple language.
GUARDRAIL: Explains terminology but does NOT diagnose conditions.
"""

from services.llm_service import call_llm

SYSTEM_CONTEXT = """You are a medical report explanation assistant.
You help patients understand:
- Medical terminology in their reports
- What different lab values generally mean
- How to read common medical reports (blood tests, X-rays, MRIs)
- Questions to ask their doctor about their results

STRICT RULES:
- NEVER diagnose a condition based on report values
- NEVER say a result is "normal" or "abnormal" for the specific patient
- ALWAYS recommend discussing results with their doctor
- Explain medical terms in simple, clear language
- Be reassuring but honest that only their doctor can interpret results for them personally
"""


def report_explanation_agent(query: str) -> str:
    """Explain medical reports and terminology without diagnosing."""
    prompt = f"""Patient query about medical report/results: {query}

Explain the medical terminology or concepts in simple language.
Remind the patient that only their doctor can properly interpret their specific results.
Do NOT make any diagnostic conclusions."""
    return call_llm(prompt, SYSTEM_CONTEXT)
