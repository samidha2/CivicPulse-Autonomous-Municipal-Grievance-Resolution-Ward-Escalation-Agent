from database.database import SessionLocal
from database.models import Complaint

from services.status_service import update_complaint_status


db = SessionLocal()

try:

    # --------------------------------------------------
    # Find latest assigned complaint
    # --------------------------------------------------

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.status == "ASSIGNED"
        )
        .order_by(Complaint.id.desc())
        .first()
    )

    if not complaint:
        print("No ASSIGNED complaint found.")

    else:

        print("\n======================================")
        print("CIVICPULSE STATUS LIFECYCLE TEST")
        print("======================================")

        print(
            f"Complaint : "
            f"{complaint.complaint_number}"
        )

        print(
            f"Current Status : "
            f"{complaint.status}"
        )

        # --------------------------------------------------
        # ASSIGNED → IN_PROGRESS
        # --------------------------------------------------

        result = update_complaint_status(
            complaint.id,
            "IN_PROGRESS",
            "Officer",
            "Officer accepted the assigned work order.",
            db
        )

        print("\nStatus Update 1")
        print("----------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

        # --------------------------------------------------
        # IN_PROGRESS → RESOLVED
        # --------------------------------------------------

        result = update_complaint_status(
            complaint.id,
            "RESOLVED",
            "Officer",
            "Issue has been resolved successfully.",
            db
        )

        print("\nStatus Update 2")
        print("----------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

        # --------------------------------------------------
        # RESOLVED → CITIZEN_CONFIRMED
        # --------------------------------------------------

        result = update_complaint_status(
            complaint.id,
            "CITIZEN_CONFIRMED",
            "Citizen",
            "Citizen confirmed that the issue was resolved.",
            db
        )

        print("\nStatus Update 3")
        print("----------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

        # --------------------------------------------------
        # CITIZEN_CONFIRMED → CLOSED
        # --------------------------------------------------

        result = update_complaint_status(
            complaint.id,
            "CLOSED",
            "CivicPulse System",
            "Complaint lifecycle completed.",
            db
        )

        print("\nStatus Update 4")
        print("----------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

        print("\n======================================")
        print("STATUS LIFECYCLE COMPLETED")
        print("======================================")


finally:
    db.close()