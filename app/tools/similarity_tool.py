from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import load_complaints


def similar_complaint_search(query: str, top_k: int = 3):

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

    ranked = similarity_scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked:

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