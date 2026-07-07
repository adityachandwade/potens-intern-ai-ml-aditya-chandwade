import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def similar_complaint_search(query: str, top_k: int = 3):
    """
    Find the most similar historical complaints.
    """

    complaints = load_complaints()

    complaint_texts = [
        complaint["complaint"]
        for complaint in complaints
    ]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(
        complaint_texts + [query]
    )

    similarity_scores = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )[0]

    ranked_indices = similarity_scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:

        complaint = complaints[index]

        results.append({
            "id": complaint["id"],
            "category": complaint["category"],
            "priority": complaint["priority"],
            "complaint": complaint["complaint"],
            "resolution": complaint["resolution"],
            "similarity": round(float(similarity_scores[index]), 3)
        })

    return results