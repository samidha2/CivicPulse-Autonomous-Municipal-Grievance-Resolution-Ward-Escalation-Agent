from datetime import datetime

from sqlalchemy.orm import Session

from database.models import (
    Complaint,
    Notification,
    Citizen,
    Officer
)


def send_notification(
    complaint_id: int,
    notification_type: str,
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

    # --------------------------------------------------
    # 2. Determine recipient
    # --------------------------------------------------

    recipient = None

    if notification_type == "OFFICER":

        if not complaint.assigned_officer_id:
            raise ValueError(
                "Complaint does not have an assigned officer"
            )

        officer = (
            db.query(Officer)
            .filter(
                Officer.id == complaint.assigned_officer_id
            )
            .first()
        )

        if not officer:
            raise ValueError("Officer not found")

        recipient = officer.email

        message = (
            f"New CivicPulse complaint assigned.\n\n"
            f"Complaint: {complaint.complaint_number}\n"
            f"Category: {complaint.category}\n"
            f"Priority: {complaint.priority}\n"
            f"Description: {complaint.description}\n\n"
            f"Please review and take necessary action."
        )

    elif notification_type == "CITIZEN":

        citizen = (
            db.query(Citizen)
            .filter(
                Citizen.id == complaint.citizen_id
            )
            .first()
        )

        if not citizen:
            raise ValueError("Citizen not found")

        recipient = citizen.email

        message = (
            f"Your CivicPulse complaint "
            f"{complaint.complaint_number} "
            f"has been registered successfully.\n\n"
            f"Current Status: {complaint.status}\n"
            f"Category: {complaint.category}\n"
            f"Priority: {complaint.priority}\n\n"
            f"We will keep you updated on its progress."
        )

    else:
        raise ValueError(
            "Invalid notification type. "
            "Use OFFICER or CITIZEN."
        )

    # --------------------------------------------------
    # 3. Store notification in database
    # --------------------------------------------------

    notification = Notification(
        complaint_id=complaint.id,
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        status="SENT",
        sent_at=datetime.utcnow()
    )

    db.add(notification)

    db.commit()
    db.refresh(notification)

    # --------------------------------------------------
    # 4. Simulate notification
    # --------------------------------------------------

    print("\n===================================")
    print("CivicPulse Notification")
    print("===================================")
    print(f"Type       : {notification_type}")
    print(f"Recipient  : {recipient}")
    print(f"Status     : SENT")
    print("-----------------------------------")
    print(message)
    print("===================================\n")

    return {
        "notification_id": notification.id,
        "complaint_id": complaint.id,
        "notification_type": notification_type,
        "recipient": recipient,
        "status": notification.status
    }