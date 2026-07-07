import json

from app.agent.gemini_client import client
from app.agent.prompts import SYSTEM_PROMPT


def classify_complaint(text: str):

    prompt = f"""
{SYSTEM_PROMPT}

Complaint:
{text}

Return ONLY valid JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text