from app.agent.decision_engine import classify_complaint

response = classify_complaint(
    "Money was deducted through UPI but receiver didn't receive the payment."
)

print(response)