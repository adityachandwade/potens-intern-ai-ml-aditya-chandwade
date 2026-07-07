from app.agent.decision_engine import classify_complaint

from app.tools import (
    transaction_lookup,
    similar_complaint_search,
    generate_acknowledgement
)


def process_complaint(
    complaint: str,
    transaction_id: str = None,
    customer_name: str = "Customer"
):

    decision = classify_complaint(complaint)

    result = {
        "decision": decision.model_dump(),
        "tool_output": None,
        "similar_cases": [],
        "acknowledgement": ""
    }

    if decision.next_tool == "transaction_lookup":

        if transaction_id:

            result["tool_output"] = transaction_lookup(
                transaction_id
            )

    result["similar_cases"] = similar_complaint_search(
        complaint
    )

    result["acknowledgement"] = generate_acknowledgement(
        customer_name
    )

    return result