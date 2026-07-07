from app.agent.decision_engine import classify_complaint

decision = classify_complaint(

    "Money deducted through UPI but receiver didn't receive payment."

)

print(decision)