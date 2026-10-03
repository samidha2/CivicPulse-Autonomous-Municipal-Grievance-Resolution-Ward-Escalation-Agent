from database.database import SessionLocal
from database.models import Complaint

from services.routing_service import route_complaint
from services.work_order_service import create_work_order
from services.notification_service import send_notification


db = SessionLocal()

try:

    # --------------------------------------------------
    # Get latest classified complaint
    # --------------------------------------------------

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.category.isnot(None)
        )
        .order_by(Complaint.id.desc())
        .first()
    )

    if not complaint:
        print("No classified complaints found.")
        exit()

    print("\n======================================")
    print("CIVICPULSE AUTOMATED WORKFLOW TEST")
    print("======================================")

    print(f"Complaint ID     : {complaint.id}")
    print(f"Complaint Number : {complaint.complaint_number}")
    print(f"Category         : {complaint.category}")
    print(f"Status           : {complaint.status}")

    # --------------------------------------------------
    # STEP 1 — Routing
    # --------------------------------------------------

    print("\n[1] Routing complaint...")

    routing_result = route_complaint(
        complaint.id,
        db
    )

    print(
        f"Department : "
        f"{routing_result['department']}"
    )

    print(
        f"Ward       : "
        f"{routing_result['ward']}"
    )

    print(
        f"Officer    : "
        f"{routing_result['officer']}"
    )

    print(
        f"SLA        : "
        f"{routing_result['sla_hours']} hours"
    )

    # --------------------------------------------------
    # STEP 2 — Work Order
    # --------------------------------------------------

    print("\n[2] Creating work order...")

    work_order_result = create_work_order(
        complaint.id,
        db
    )

    print(
        f"Work Order : "
        f"{work_order_result['work_order_number']}"
    )

    print(
        f"Assigned To: "
        f"{work_order_result['assigned_officer']}"
    )

    # --------------------------------------------------
    # STEP 3 — Officer notification
    # --------------------------------------------------

    print("\n[3] Sending officer notification...")

    officer_notification = send_notification(
        complaint.id,
        "OFFICER",
        db
    )

    print(
        f"Notification ID: "
        f"{officer_notification['notification_id']}"
    )

    # --------------------------------------------------
    # STEP 4 — Citizen notification
    # --------------------------------------------------

    print("\n[4] Sending citizen notification...")

    citizen_notification = send_notification(
        complaint.id,
        "CITIZEN",
        db
    )

    print(
        f"Notification ID: "
        f"{citizen_notification['notification_id']}"
    )

    print("\n======================================")
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("======================================")

finally:
    db.close()