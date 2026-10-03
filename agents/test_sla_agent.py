from database.database import SessionLocal
from database.models import Complaint

from agents.sla_agent import sla_monitoring_agent


db = SessionLocal()

try:

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.status.notin_([
                "RESOLVED",
                "CITIZEN_CONFIRMED",
                "CLOSED"
            ])
        )
        .order_by(Complaint.id.desc())
        .first()
    )

    if not complaint:

        print("No active complaint available for testing.")

    else:

        print(
            f"\nTesting Complaint: "
            f"{complaint.complaint_number}"
        )

        print(
            f"Current Status: "
            f"{complaint.status}"
        )

        result = sla_monitoring_agent(
            complaint.id
        )

        print("\nAgent Result:")
        print(result)

finally:

    db.close()