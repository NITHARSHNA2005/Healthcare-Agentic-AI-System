"""
Appointment Agent - Handles scheduling, rescheduling, and cancellation queries.
"""

from services.gemini_service import call_gemini

SYSTEM_CONTEXT = """You are a helpful healthcare appointment assistant.
You help patients with:
- Scheduling new appointments
- Rescheduling existing appointments
- Cancelling appointments
- Checking appointment availability
- Providing information about appointment preparation

IMPORTANT RULES:
- Do NOT diagnose any medical conditions
- Do NOT prescribe medications
- Always recommend consulting a doctor for medical advice
- Be empathetic and professional
- Keep responses concise and actionable
"""


def appointment_agent(query: str) -> str:
    """Process appointment-related queries."""
    prompt = f"""Patient query about appointments: {query}

Provide helpful guidance about scheduling, rescheduling, or cancelling appointments.
If the patient seems to need urgent care, advise them to visit the emergency room or call emergency services."""
    return call_gemini(prompt, SYSTEM_CONTEXT)
