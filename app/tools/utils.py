import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

TRANSACTION_DB = BASE_DIR / "database" / "transactions.json"
COMPLAINT_DB = BASE_DIR / "database" / "complaints.json"


def load_transactions():
    with open(TRANSACTION_DB, "r", encoding="utf-8") as file:
        return json.load(file)


def load_complaints():
    with open(COMPLAINT_DB, "r", encoding="utf-8") as file:
        return json.load(file)