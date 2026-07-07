from app.agent.orchestrator import process_complaint

response = process_complaint(
    complaint="Money deducted but receiver didn't receive payment.",
    transaction_id="TXN1002",
    customer_name="Aditya"
)

from pprint import pprint

pprint(response)