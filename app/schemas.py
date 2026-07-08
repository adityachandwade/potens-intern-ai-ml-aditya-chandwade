from pydantic import BaseModel, Field
from typing import List, Literal, Optional


Category = Literal["UPI", "CARD", "ACCOUNT", "LOAN", "FRAUD", "KYC", "NET BANKING"]
Priority = Literal["P0", "P1", "P2"]
NextTool = Literal["transaction_lookup", "similar_complaint_search", "generate_acknowledgement"]


class TriageDecision(BaseModel):
    category: Category
    priority: Priority
    next_tool: NextTool
    reasoning: str
    why: str
    # Populated either by the model directly, or synthesized by
    # decision_engine.py's fallback if the model omits it. Never absent
    # by the time this model is constructed, but defaulting to an empty
    # list keeps this schema safe to use standalone (e.g. in tests).
    reasoning_trace: List[str] = Field(default_factory=list)


class ComplaintRequest(BaseModel):
    complaint: str
    transaction_id: Optional[str] = None
    customer_name: str = "Customer"


class HealthResponse(BaseModel):
    status: str