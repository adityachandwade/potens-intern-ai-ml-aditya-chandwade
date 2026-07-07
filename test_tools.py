from app.tools import (
    transaction_lookup,
    similar_complaint_search,
    generate_acknowledgement
)


print("=" * 60)
print("Acknowledgement")
print("=" * 60)

print(generate_acknowledgement("Aditya"))

print("\n")

print("=" * 60)
print("Transaction Lookup")
print("=" * 60)

print(transaction_lookup("TXN1002"))

print("\n")

print("=" * 60)
print("Similar Complaint Search")
print("=" * 60)

results = similar_complaint_search(
    "Money deducted but payment not received"
)

for complaint in results:
    print(complaint)