from datetime import datetime, timedelta

from sentence_transformers import SentenceTransformer

from database.database import SessionLocal
from database.models import Complaint


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(text1: str, text2: str) -> float:

    embeddings = model.encode(
        [text1, text2],
        normalize_embeddings=True
    )

    similarity = float(
        embeddings[0] @ embeddings[1]
    )

    return similarity


def calculate_category_score(
    complaint1,
    complaint2
) -> float:

    if not complaint1.category or not complaint2.category:
        return 0.0

    return 1.0 if (
        complaint1.category.lower()
        == complaint2.category.lower()
    ) else 0.0


def calculate_location_score(
    complaint1,
    complaint2
) -> float:

    if (
        complaint1.latitude is None
        or complaint1.longitude is None
        or complaint2.latitude is None
        or complaint2.longitude is None
    ):
        return 0.0

    lat_diff = abs(
        complaint1.latitude
        - complaint2.latitude
    )

    lon_diff = abs(
        complaint1.longitude
        - complaint2.longitude
    )

    distance = (
        (lat_diff ** 2 + lon_diff ** 2)
        ** 0.5
    )

    # Approximate geographic scoring
    if distance <= 0.001:
        return 1.0

    if distance <= 0.003:
        return 0.8

    if distance <= 0.005:
        return 0.5

    return 0.0


def calculate_time_score(
    complaint1,
    complaint2
) -> float:

    if (
        complaint1.created_at is None
        or complaint2.created_at is None
    ):
        return 0.0

    time_difference = abs(
        complaint1.created_at
        - complaint2.created_at
    )

    hours = (
        time_difference.total_seconds()
        / 3600
    )

    if hours <= 24:
        return 1.0

    if hours <= 72:
        return 0.8

    if hours <= 168:
        return 0.5

    return 0.0


def calculate_duplicate_score(
    semantic_score: float,
    category_score: float,
    location_score: float,
    time_score: float
) -> float:

    score = (
        0.40 * semantic_score
        + 0.20 * category_score
        + 0.30 * location_score
        + 0.10 * time_score
    )

    return round(score, 4)


def find_duplicate_complaint(
    complaint_id: int,
    duplicate_threshold: float = 0.75
):

    db = SessionLocal()

    try:

        complaint = (
            db.query(Complaint)
            .filter(
                Complaint.id == complaint_id
            )
            .first()
        )

        if not complaint:

            return {
                "duplicate_found": False,
                "duplicate_complaint_id": None,
                "similarity": 0.0,
                "duplicate_score": 0.0
            }

        existing_complaints = (
            db.query(Complaint)
            .filter(
                Complaint.id != complaint_id,
                Complaint.description.isnot(None)
            )
            .order_by(
                Complaint.id.desc()
            )
            .limit(100)
            .all()
        )

        best_match = None
        best_score = 0.0
        best_semantic_score = 0.0

        for existing in existing_complaints:

            semantic_score = calculate_similarity(
                complaint.description,
                existing.description
            )

            category_score = calculate_category_score(
                complaint,
                existing
            )

            location_score = calculate_location_score(
                complaint,
                existing
            )

            time_score = calculate_time_score(
                complaint,
                existing
            )

            duplicate_score = calculate_duplicate_score(
                semantic_score,
                category_score,
                location_score,
                time_score
            )

            if duplicate_score > best_score:

                best_score = duplicate_score
                best_match = existing
                best_semantic_score = semantic_score

        if (
            best_match
            and best_score >= duplicate_threshold
        ):

            return {
                "duplicate_found": True,
                "duplicate_complaint_id":
                    best_match.id,
                "similarity":
                    round(best_semantic_score, 4),
                "duplicate_score":
                    best_score
            }

        return {
            "duplicate_found": False,
            "duplicate_complaint_id": None,
            "similarity":
                round(best_semantic_score, 4),
            "duplicate_score":
                round(best_score, 4)
        }

    finally:

        db.close()