"""
Groq API service for Healthcare AI System.
Uses Llama 3.3 70B via Groq for fast, free inference.
"""

import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


def call_gemini(prompt: str, system_context: str = "") -> str:
    """
    Call Groq Llama 3.3 70B with a prompt and optional system context.
    Function name kept as call_gemini for compatibility with existing agents.
    Returns the text response or an error message.
    """
    try:
        messages = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try again."
