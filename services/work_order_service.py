from datetime import datetime

from sqlalchemy.orm import Session

from database.models import (
    Complaint,
    WorkOrder,
    ComplaintHistory,
    Officer
)


def create_work_order(
    complaint_id: int,
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
    # 2. Check officer assignment
    # --------------------------------------------------

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
        raise ValueError("Assigned officer not found")

    # --------------------------------------------------
    # 3. Prevent duplicate work orders
    # --------------------------------------------------

    existing_work_order = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.complaint_id == complaint.id
        )
        .first()
    )

    if existing_work_order:
        return {
            "work_order_id": existing_work_order.id,
            "work_order_number": existing_work_order.work_order_number,
            "status": existing_work_order.status,
            "message": "Work order already exists"
        }

    # --------------------------------------------------
    # 4. Generate work order number
    # --------------------------------------------------

    latest_work_order = (
        db.query(WorkOrder)
        .order_by(WorkOrder.id.desc())
        .first()
    )

    next_id = (
        latest_work_order.id + 1
        if latest_work_order
        else 1
    )

    work_order_number = (
        f"WO-{datetime.utcnow().year}-{next_id:05d}"
    )

    # --------------------------------------------------
    # 5. Create work order
    # --------------------------------------------------

    work_order = WorkOrder(
        complaint_id=complaint.id,
        work_order_number=work_order_number,
        assigned_to=officer.id,
        status="CREATED",
        description=complaint.description
    )

    db.add(work_order)

    # --------------------------------------------------
    # 6. Update complaint status
    # --------------------------------------------------

    previous_status = complaint.status

    complaint.status = "ASSIGNED"

    # --------------------------------------------------
    # 7. Create audit history
    # --------------------------------------------------

    history = ComplaintHistory(
        complaint_id=complaint.id,
        action="WORK_ORDER_CREATED",
        performed_by="CivicPulse Agent",
        previous_status=previous_status,
        new_status="ASSIGNED",
        remarks=(
            f"Work order {work_order_number} created "
            f"and assigned to {officer.name}"
        )
    )

    db.add(history)

    db.commit()
    db.refresh(work_order)

    return {
        "work_order_id": work_order.id,
        "work_order_number": work_order.work_order_number,
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "assigned_officer": officer.name,
        "assigned_officer_id": officer.id,
        "status": work_order.status
    }