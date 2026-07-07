from fastapi import APIRouter

from app.schemas import (
    ComplaintRequest,
    HealthResponse
)

from app.agent.orchestrator import process_complaint

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():

    return {
        "status": "AEGIS API Running"
    }


@router.post("/triage")
def triage(request: ComplaintRequest):

    return process_complaint(
        complaint=request.complaint,
        transaction_id=request.transaction_id,
        customer_name=request.customer_name
    )