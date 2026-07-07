from pydantic import BaseModel


class TriageDecision(BaseModel):
    category: str
    priority: str
    next_tool: str
    reasoning: str
    why: str