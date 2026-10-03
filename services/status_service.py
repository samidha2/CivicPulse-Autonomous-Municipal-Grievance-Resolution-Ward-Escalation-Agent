from datetime import datetime

from sqlalchemy.orm import Session

from database.models import Complaint, ComplaintHistory


# --------------------------------------------------
# Allowed complaint status transitions
# --------------------------------------------------

ALLOWED_TRANSITIONS = {
    "SUBMITTED": ["UNDER_REVIEW"],
    "UNDER_REVIEW": ["ASSIGNED"],
    "ASSIGNED": ["IN_PROGRESS", "ESCALATED"],
    "IN_PROGRESS": ["RESOLVED", "ESCALATED"],
    "ESCALATED": ["IN_PROGRESS", "RESOLVED"],
    "RESOLVED": ["CITIZEN_CONFIRMED", "CITIZEN_REJECTED"],
    "CITIZEN_CONFIRMED": ["CLOSED"],
    "CITIZEN_REJECTED": ["REOPENED"],
    "REOPENED": ["IN_PROGRESS"],
    "CLOSED": []
}


def update_complaint_status(
    complaint_id: int,
    new_status: str,
    performed_by: str,
    remarks: str,
    db: Session
):
    # --------------------------------------------------
    # 1. Get complaint
    # --------------------------------------------------

    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:
        raise ValueError("Complaint not found")

    current_status = complaint.status

    # --------------------------------------------------
    # 2. Validate new status
    # --------------------------------------------------

    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError(
            f"Invalid status: {new_status}"
        )

    # --------------------------------------------------
    # 3. Validate transition
    # --------------------------------------------------

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid transition: "
            f"{current_status} → {new_status}"
        )

    # --------------------------------------------------
    # 4. Update complaint
    # --------------------------------------------------

    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()

    # --------------------------------------------------
    # 5. Create audit history
    # --------------------------------------------------

    history = ComplaintHistory(
        complaint_id=complaint.id,
        action="STATUS_CHANGED",
        performed_by=performed_by,
        previous_status=current_status,
        new_status=new_status,
        remarks=remarks,
        timestamp=datetime.utcnow()
    )

    db.add(history)

    db.commit()
    db.refresh(complaint)

    return {
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "previous_status": current_status,
        "new_status": new_status,
        "performed_by": performed_by,
        "remarks": remarks,
        "timestamp": history.timestamp
    }