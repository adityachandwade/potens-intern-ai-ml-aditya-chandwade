from pydantic import BaseModel
from typing import Optional


class TriageDecision(BaseModel):
    category: str
    priority: str
    next_tool: str
    reasoning: str
    why: str


class ComplaintRequest(BaseModel):
    complaint: str
    transaction_id: Optional[str] = None
    customer_name: str = "Customer"


class HealthResponse(BaseModel):
    status: str