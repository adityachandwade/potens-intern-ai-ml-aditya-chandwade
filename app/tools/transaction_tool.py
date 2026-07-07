from .utils import load_transactions


def transaction_lookup(transaction_id: str):

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