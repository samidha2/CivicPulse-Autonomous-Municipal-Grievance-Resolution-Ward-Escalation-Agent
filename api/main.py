# uvicorn api.main:app --reload

import sys
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Ensure UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from api.automation import router as automation_router
from database.database import get_db, SessionLocal
from database.models import (
    Complaint,
    Citizen,
    Department,
    Ward,
    Officer,
    WorkOrder,
    ComplaintHistory,
    Escalation,
    Feedback,
    SLARule
)
from ai.grievance_understanding import analyze_complaint
from api.schemas import ComplaintCreate, ComplaintResponse
from services.status_service import update_complaint_status
from services.sla_service import check_sla_status


app = FastAPI(
    title="CivicPulse API",
    description="Autonomous Municipal Grievance Resolution & Ward Escalation Platform",
    version="1.0.0"
)

app.include_router(automation_router)


# -------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------

class StatusUpdateRequest(BaseModel):
    new_status: str
    performed_by: str = "Officer"
    remarks: str = ""


class FeedbackCreate(BaseModel):
    rating: int
    comments: Optional[str] = None
    resolution_accepted: bool = True


# -------------------------------------------------
# SERIALIZATION HELPERS
# -------------------------------------------------

def serialize_complaint(c: Complaint) -> dict:
    return {
        "id": c.id,
        "complaint_number": c.complaint_number,
        "citizen_id": c.citizen_id,
        "citizen_name": c.citizen.name if c.citizen else None,
        "description": c.description,
        "category": c.category,
        "department_id": c.department_id,
        "department_name": c.department.name if c.department else None,
        "ward_id": c.ward_id,
        "ward_name": c.ward.name if c.ward else None,
        "ward_number": c.ward.ward_number if c.ward else None,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "severity": c.severity,
        "priority": c.priority,
        "status": c.status,
        "confidence_score": c.confidence_score,
        "assigned_officer_id": c.assigned_officer_id,
        "assigned_officer_name": c.assigned_officer.name if c.assigned_officer else None,
        "duplicate_of": c.duplicate_of,
        "sla_deadline": str(c.sla_deadline) if c.sla_deadline else None,
        "resolution": c.resolution,
        "created_at": str(c.created_at) if c.created_at else None,
        "updated_at": str(c.updated_at) if c.updated_at else None,
        "work_order_count": len(c.work_orders) if c.work_orders else 0
    }


def serialize_complaint_detail(c: Complaint) -> dict:
    sla_info = check_sla_status(c.id) if c.id else {}
    return {
        "id": c.id,
        "complaint_number": c.complaint_number,
        "citizen_id": c.citizen_id,
        "citizen_name": c.citizen.name if c.citizen else None,
        "citizen_phone": c.citizen.phone if c.citizen else None,
        "citizen_email": c.citizen.email if c.citizen else None,
        "preferred_language": c.citizen.preferred_language if c.citizen else "English",
        "description": c.description,
        "category": c.category,
        "department_id": c.department_id,
        "department_name": c.department.name if c.department else None,
        "ward_id": c.ward_id,
        "ward_name": c.ward.name if c.ward else None,
        "ward_number": c.ward.ward_number if c.ward else None,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "severity": c.severity,
        "priority": c.priority,
        "status": c.status,
        "confidence_score": c.confidence_score,
        "assigned_officer_id": c.assigned_officer_id,
        "assigned_officer_name": c.assigned_officer.name if c.assigned_officer else None,
        "assigned_officer_email": c.assigned_officer.email if c.assigned_officer else None,
        "assigned_officer_designation": c.assigned_officer.designation if c.assigned_officer else None,
        "duplicate_of": c.duplicate_of,
        "sla_deadline": str(c.sla_deadline) if c.sla_deadline else None,
        "sla_info": sla_info,
        "resolution": c.resolution,
        "resolution_time": str(c.resolution_time) if c.resolution_time else None,
        "created_at": str(c.created_at) if c.created_at else None,
        "updated_at": str(c.updated_at) if c.updated_at else None,
        "work_orders": [
            {
                "id": wo.id,
                "work_order_number": wo.work_order_number,
                "assigned_to": wo.assigned_to,
                "status": wo.status,
                "description": wo.description,
                "created_at": str(wo.created_at) if wo.created_at else None,
                "completed_at": str(wo.completed_at) if wo.completed_at else None
            }
            for wo in (c.work_orders or [])
        ],
        "history": [
            {
                "id": h.id,
                "action": h.action,
                "performed_by": h.performed_by,
                "previous_status": h.previous_status,
                "new_status": h.new_status,
                "remarks": h.remarks,
                "timestamp": str(h.timestamp) if h.timestamp else None
            }
            for h in sorted(c.history or [], key=lambda x: x.timestamp or datetime.min)
        ],
        "escalations": [
            {
                "id": e.id,
                "escalation_level": e.escalation_level,
                "reason": e.reason,
                "escalated_to": e.escalated_to,
                "status": e.status,
                "created_at": str(e.created_at) if e.created_at else None,
                "resolved_at": str(e.resolved_at) if e.resolved_at else None
            }
            for e in (c.escalations or [])
        ],
        "feedback": [
            {
                "id": fb.id,
                "rating": fb.rating,
                "comments": fb.comments,
                "resolution_accepted": fb.resolution_accepted,
                "created_at": str(fb.created_at) if fb.created_at else None
            }
            for fb in (c.feedback or [])
        ]
    }


# -------------------------------------------------
# CORE ENDPOINTS
# -------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "CivicPulse API is running",
        "platform": "Autonomous Municipal Grievance Resolution & Ward Escalation Platform",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CivicPulse Backend",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/complaints", status_code=201)
def create_complaint(
    payload: ComplaintCreate,
    skip_ai: bool = Query(False, description="Set True to defer AI processing to LangGraph orchestrator"),
    db: Session = Depends(get_db)
):
    # 1. Validate citizen
    citizen = (
        db.query(Citizen)
        .filter(Citizen.id == payload.citizen_id)
        .first()
    )

    if not citizen:
        raise HTTPException(
            status_code=404,
            detail="Citizen not found"
        )

    # 2. Generate complaint number
    latest_complaint = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .first()
    )

    next_id = (
        latest_complaint.id + 1
        if latest_complaint
        else 1
    )

    complaint_number = f"CP-{datetime.utcnow().year}-{next_id:04d}"

    # 3. Create initial complaint
    complaint = Complaint(
        complaint_number=complaint_number,
        citizen_id=payload.citizen_id,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="SUBMITTED"
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Record history
    history = ComplaintHistory(
        complaint_id=complaint.id,
        action="COMPLAINT_SUBMITTED",
        performed_by="Citizen",
        previous_status=None,
        new_status="SUBMITTED",
        remarks="Complaint filed via CivicPulse portal"
    )
    db.add(history)
    db.commit()

    # 4. Optional Initial AI Understanding (skipped if client triggers LangGraph orchestrator next)
    if not skip_ai:
        try:
            ai_result = analyze_complaint(payload.description)

            valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
            valid_priorities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

            severity = ai_result.get("severity", "MEDIUM").upper()
            priority = ai_result.get("priority", "MEDIUM").upper()

            if severity not in valid_severities:
                severity = "MEDIUM"

            if priority not in valid_priorities:
                priority = "MEDIUM"

            complaint.category = ai_result.get("category")
            complaint.severity = severity
            complaint.priority = priority
            complaint.confidence_score = ai_result.get("confidence_score")
            complaint.status = "UNDER_REVIEW"

            db.commit()
            db.refresh(complaint)

        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            complaint.status = "UNDER_REVIEW"
            db.commit()
            db.refresh(complaint)

    return serialize_complaint(complaint)


@app.get("/complaints")
def list_complaints(
    department_id: Optional[int] = None,
    ward_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 200,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)

    if department_id:
        query = query.filter(Complaint.department_id == department_id)
    if ward_id:
        query = query.filter(Complaint.ward_id == ward_id)
    if status and status.upper() != "ALL":
        query = query.filter(Complaint.status == status.upper())
    if priority and priority.upper() != "ALL":
        query = query.filter(Complaint.priority == priority.upper())
    if category and category.upper() != "ALL":
        query = query.filter(Complaint.category == category)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Complaint.complaint_number.ilike(search_pattern)) |
            (Complaint.description.ilike(search_pattern)) |
            (Complaint.category.ilike(search_pattern))
        )

    total = query.count()
    complaints = query.order_by(Complaint.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "complaints": [serialize_complaint(c) for c in complaints]
    }


@app.get("/complaints/{complaint_identifier}")
def get_complaint(
    complaint_identifier: str,
    db: Session = Depends(get_db)
):
    complaint = None

    if complaint_identifier.isdigit():
        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == int(complaint_identifier))
            .first()
        )

    if not complaint:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.complaint_number == complaint_identifier)
            .first()
        )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail=f"Complaint '{complaint_identifier}' not found"
        )

    return serialize_complaint_detail(complaint)


@app.post("/complaints/{complaint_id}/status")
def update_status(
    complaint_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        result = update_complaint_status(
            complaint_id=complaint_id,
            new_status=payload.new_status,
            performed_by=payload.performed_by,
            remarks=payload.remarks,
            db=db
        )
        return {"success": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/complaints/{complaint_id}/feedback")
def submit_feedback(
    complaint_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    fb = Feedback(
        complaint_id=complaint_id,
        rating=payload.rating,
        comments=payload.comments,
        resolution_accepted=payload.resolution_accepted
    )
    db.add(fb)

    # Transition status based on citizen response
    prev_status = complaint.status
    if payload.resolution_accepted:
        new_status = "CITIZEN_CONFIRMED"
    else:
        new_status = "CITIZEN_REJECTED"

    complaint.status = new_status

    history = ComplaintHistory(
        complaint_id=complaint_id,
        action="CITIZEN_FEEDBACK",
        performed_by="Citizen",
        previous_status=prev_status,
        new_status=new_status,
        remarks=f"Rating: {payload.rating}/5. Accepted: {payload.resolution_accepted}. Note: {payload.comments or 'None'}"
    )
    db.add(history)

    db.commit()
    db.refresh(fb)

    return {
        "success": True,
        "feedback_id": fb.id,
        "new_status": new_status,
        "rating": fb.rating
    }


# -------------------------------------------------
# METADATA & LOOKUP ENDPOINTS
# -------------------------------------------------

@app.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).order_by(Department.name).all()
    return [
        {"id": d.id, "name": d.name, "description": d.description}
        for d in depts
    ]


@app.get("/wards")
def get_wards(db: Session = Depends(get_db)):
    wards = db.query(Ward).order_by(Ward.ward_number).all()
    return [
        {"id": w.id, "ward_number": w.ward_number, "name": w.name, "zone": w.zone}
        for w in wards
    ]


@app.get("/officers")
def get_officers(db: Session = Depends(get_db)):
    officers = db.query(Officer).order_by(Officer.name).all()
    return [
        {
            "id": o.id,
            "name": o.name,
            "email": o.email,
            "phone": o.phone,
            "designation": o.designation,
            "department_id": o.department_id,
            "ward_id": o.ward_id,
            "is_active": o.is_active
        }
        for o in officers
    ]


@app.get("/citizens")
def get_citizens(db: Session = Depends(get_db)):
    citizens = db.query(Citizen).order_by(Citizen.id).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "preferred_language": c.preferred_language
        }
        for c in citizens
    ]


@app.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total = db.query(Complaint).count()
    open_count = db.query(Complaint).filter(Complaint.status.notin_(["RESOLVED", "CITIZEN_CONFIRMED", "CLOSED"])).count()
    resolved = db.query(Complaint).filter(Complaint.status.in_(["RESOLVED", "CITIZEN_CONFIRMED", "CLOSED"])).count()
    escalated = db.query(Complaint).filter(Complaint.status == "ESCALATED").count()
    duplicates = db.query(Complaint).filter(Complaint.duplicate_of.isnot(None)).count()
    work_orders = db.query(WorkOrder).count()

    active_complaints = db.query(Complaint).filter(Complaint.status.notin_(["RESOLVED", "CITIZEN_CONFIRMED", "CLOSED"])).all()
    at_risk = 0
    overdue = 0
    critical = 0

    for c in active_complaints:
        sla = check_sla_status(c.id)
        st = sla.get("sla_status")
        if st == "AT_RISK":
            at_risk += 1
        elif st == "OVERDUE":
            overdue += 1
        elif st == "CRITICAL":
            critical += 1

    return {
        "total": total,
        "open": open_count,
        "resolved": resolved,
        "at_risk": at_risk,
        "overdue": overdue,
        "critical": critical,
        "escalated": escalated,
        "duplicates": duplicates,
        "work_orders": work_orders
    }