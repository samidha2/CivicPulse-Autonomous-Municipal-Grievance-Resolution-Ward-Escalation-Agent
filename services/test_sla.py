from services.sla_service import check_sla_status
from database.database import SessionLocal
from database.models import Complaint


db = SessionLocal()

try:

    complaint = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .first()
    )

    if not complaint:
        print("No complaints found.")
    else:

        print(
            f"\nTesting Complaint: "
            f"{complaint.complaint_number}"
        )

        result = check_sla_status(
            complaint.id
        )

        print("\nSLA Result:")
        print(result)

finally:
    db.close()