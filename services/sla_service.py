from datetime import datetime

from database.database import SessionLocal
from database.models import Complaint, Escalation


ESCALATION_LEVELS = {
    1: "Department Officer",
    2: "Ward Officer",
    3: "Zone Officer",
    4: "Municipal Authority"
}


def check_sla_status(complaint_id: int):

    db = SessionLocal()

    try:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return {
                "found": False,
                "message": "Complaint not found"
            }

        if not complaint.sla_deadline:
            return {
                "found": True,
                "sla_status": "NO_SLA",
                "should_escalate": False
            }

        now = datetime.utcnow()

        deadline = complaint.sla_deadline

        remaining_seconds = (
            deadline - now
        ).total_seconds()

        remaining_hours = remaining_seconds / 3600

        if complaint.status in [
            "RESOLVED",
            "CITIZEN_CONFIRMED",
            "CLOSED"
        ]:
            return {
                "found": True,
                "sla_status": "COMPLETED",
                "should_escalate": False,
                "remaining_hours": round(
                    remaining_hours, 2
                )
            }

        if remaining_hours < 0:

            return {
                "found": True,
                "sla_status": "OVERDUE",
                "should_escalate": True,
                "remaining_hours": round(
                    remaining_hours, 2
                )
            }

        if remaining_hours <= 4:

            return {
                "found": True,
                "sla_status": "CRITICAL",
                "should_escalate": True,
                "remaining_hours": round(
                    remaining_hours, 2
                )
            }

        if remaining_hours <= 12:

            return {
                "found": True,
                "sla_status": "AT_RISK",
                "should_escalate": True,
                "remaining_hours": round(
                    remaining_hours, 2
                )
            }

        return {
            "found": True,
            "sla_status": "ON_TRACK",
            "should_escalate": False,
            "remaining_hours": round(
                remaining_hours, 2
            )
        }

    finally:
        db.close()


def escalate_complaint(
    complaint_id: int,
    reason: str
):

    db = SessionLocal()

    try:

        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return None

        existing = (
            db.query(Escalation)
            .filter(
                Escalation.complaint_id
                == complaint_id,
                Escalation.status == "OPEN"
            )
            .order_by(
                Escalation.escalation_level.desc()
            )
            .first()
        )

        current_level = (
            existing.escalation_level
            if existing
            else 0
        )

        next_level = min(
            current_level + 1,
            4
        )

        escalation = Escalation(
            complaint_id=complaint_id,
            escalation_level=next_level,
            reason=reason,
            escalated_to=ESCALATION_LEVELS[
                next_level
            ],
            status="OPEN"
        )

        db.add(escalation)

        complaint.status = "ESCALATED"

        db.commit()

        print(
            f"🚨 Complaint {complaint_id} "
            f"escalated to Level {next_level}"
        )

        return {
            "escalation_level": next_level,
            "escalated_to":
                ESCALATION_LEVELS[next_level]
        }

    finally:
        db.close()