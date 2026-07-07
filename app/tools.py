import json
from pathlib import Path

# Database paths
BASE_DIR = Path(__file__).resolve().parent.parent
TRANSACTION_DB = BASE_DIR / "database" / "transactions.json"
COMPLAINT_DB = BASE_DIR / "database" / "complaints.json"


def load_transactions():
    """Load transaction records from JSON."""
    with open(TRANSACTION_DB, "r", encoding="utf-8") as file:
        return json.load(file)


def load_complaints():
    """Load complaint records from JSON."""
    with open(COMPLAINT_DB, "r", encoding="utf-8") as file:
        return json.load(file)


def transaction_lookup(transaction_id: str):
    """
    Search transaction by Transaction ID.
    """

    transactions = load_transactions()

    for transaction in transactions:
        if transaction["transaction_id"] == transaction_id:
            return {
                "found": True,
                "transaction": transaction
            }

    return {
        "found": False,
        "message": "Transaction not found."
    }