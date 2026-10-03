from database.database import SessionLocal
from database.models import Complaint
from services.routing_service import route_complaint


db = SessionLocal()

try:

    # Get the latest complaint from the database
    complaint = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .first()
    )

    if not complaint:
        print("No complaints found in database.")
    else:

        print(f"Testing complaint: {complaint.id}")
        print(f"Complaint number: {complaint.complaint_number}")
        print(f"Category: {complaint.category}")

        result = route_complaint(
            complaint.id,
            db
        )

        print("\nCivicPulse Routing Result")
        print("--------------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

finally:

    db.close()