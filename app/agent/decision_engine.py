import json

from app.agent.gemini_client import client
from app.agent.prompts import SYSTEM_PROMPT
from app.schemas import TriageDecision


def classify_complaint(text: str):

    prompt = f"""
{SYSTEM_PROMPT}

Complaint:

{text}

Return ONLY JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    cleaned = response.text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "").strip()

    data = json.loads(cleaned)

    return TriageDecision(**data)