from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.database import SessionLocal
from database.models import Complaint

from agents.sla_agent import sla_monitoring_agent
from services.sla_service import (
    check_sla_status,
    escalate_complaint
)
from services.notification_service import send_notification


router = APIRouter(
    prefix="/automation",
    tags=["Automation"]
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class ComplaintAutomationRequest(BaseModel):
    complaint_id: int


class EscalationRequest(BaseModel):
    complaint_id: int
    reason: str


class NotificationRequest(BaseModel):
    complaint_id: int
    notification_type: str


# --------------------------------------------------
# 1. SLA CHECK
# --------------------------------------------------

@router.post("/sla-check")
def automation_sla_check(
    request: ComplaintAutomationRequest
):

    result = check_sla_status(
        request.complaint_id
    )

    if not result.get("found"):
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return {
        "success": True,
        "complaint_id": request.complaint_id,
        "result": result
    }


# --------------------------------------------------
# 2. SLA MONITORING AGENT
# --------------------------------------------------

@router.post("/sla-monitor")
def automation_sla_monitor(
    request: ComplaintAutomationRequest
):

    result = sla_monitoring_agent(
        request.complaint_id
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get(
                "message",
                "SLA monitoring failed"
            )
        )

    return {
        "success": True,
        "complaint_id": request.complaint_id,
        "agent_result": result
    }


# --------------------------------------------------
# 3. MANUAL / AUTOMATED ESCALATION
# --------------------------------------------------

@router.post("/escalate")
def automation_escalate(
    request: EscalationRequest
):

    result = escalate_complaint(
        request.complaint_id,
        request.reason
    )

    return {
        "success": True,
        "complaint_id": request.complaint_id,
        "escalation": result
    }
# ------------------------------------------

@router.post("/process-complaint")
def process_complaint(
        request: ComplaintAutomationRequest
    ):
        from agents.orchestrator import build_civicpulse_graph

        graph = build_civicpulse_graph()

        try:
            result = graph.invoke({
                "complaint_id": request.complaint_id
            })

            return {
                "success": True,
                "complaint_id": request.complaint_id,
                "agent_result": result
            }

        except Exception as e:

            return {
                "success": False,
                "complaint_id": request.complaint_id,
                "error": str(e)
            }

# --------------------------------------------------
# 4. NOTIFICATION
# --------------------------------------------------

@router.post("/notify")
def automation_notify(
    request: NotificationRequest
):

    db = SessionLocal()

    try:

        complaint = (
            db.query(Complaint)
            .filter(
                Complaint.id == request.complaint_id
            )
            .first()
        )

        if not complaint:

            raise HTTPException(
                status_code=404,
                detail="Complaint not found"
            )

        result = send_notification(
            request.complaint_id,
            request.notification_type,
            db
        )

        return {
            "success": True,
            "complaint_id": request.complaint_id,
            "notification": result
        }

    finally:

        db.close()


# --------------------------------------------------
# 5. POLICY QUERY (RAG AGENT)
# --------------------------------------------------

class PolicyQueryRequest(BaseModel):
    query: str


@router.post("/policy-query")
def automation_policy_query(
    request: PolicyQueryRequest
):
    from agents.policy_agent import policy_agent

    try:
        result = policy_agent(request.query)
        return {
            "success": True,
            "query": request.query,
            "answer": result.get("answer", "No answer generated."),
            "sources": result.get("sources", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Policy agent query failed: {str(e)}"
        )


# --------------------------------------------------
# 6. ACTIVE COMPLAINTS FOR SLA MONITORING
# --------------------------------------------------

@router.get("/active-complaints")
def get_active_complaints():
    db = SessionLocal()
    try:
        active_statuses = [
            "SUBMITTED",
            "UNDER_REVIEW",
            "ASSIGNED",
            "IN_PROGRESS",
            "ESCALATED",
            "REOPENED",
            "PENDING_INFORMATION"
        ]

        complaints = (
            db.query(Complaint)
            .filter(Complaint.status.in_(active_statuses))
            .order_by(Complaint.id.desc())
            .all()
        )

        results = []
        for c in complaints:
            sla_info = check_sla_status(c.id)
            results.append({
                "id": c.id,
                "complaint_number": c.complaint_number,
                "category": c.category,
                "priority": c.priority,
                "severity": c.severity,
                "status": c.status,
                "department_name": c.department.name if c.department else None,
                "ward_name": c.ward.name if c.ward else None,
                "assigned_officer_name": c.assigned_officer.name if c.assigned_officer else None,
                "sla_deadline": str(c.sla_deadline) if c.sla_deadline else None,
                "sla_status": sla_info.get("sla_status", "UNKNOWN"),
                "remaining_hours": sla_info.get("remaining_hours"),
                "should_escalate": sla_info.get("should_escalate", False)
            })

        return {
            "success": True,
            "count": len(results),
            "active_complaints": results
        }
    finally:
        db.close()


    

