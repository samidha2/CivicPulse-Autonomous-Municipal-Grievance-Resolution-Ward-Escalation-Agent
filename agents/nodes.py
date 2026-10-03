from database.database import SessionLocal
from database.models import Complaint, ComplaintHistory

from ai.grievance_understanding import analyze_complaint
from services.routing_service import route_complaint
from services.work_order_service import create_work_order
from services.notification_service import send_notification
from agents.policy_agent import policy_agent

from duplicate.duplicate_detector import (
    find_duplicate_complaint
)

from duplicate.duplicate_detector import find_duplicate_complaint

def load_complaint(state):

    db = SessionLocal()

    try:
        complaint_id = state["complaint_id"]

        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return {
                "error": f"Complaint {complaint_id} not found",
                "next_action": "END"
            }

        return {
            "complaint_id": complaint.id,
            "complaint_number": complaint.complaint_number,
            "description": complaint.description,
            "status": complaint.status,
            "next_action": "UNDERSTAND"
        }

    finally:
        db.close()


def understand_complaint(state):

    complaint_id = state["complaint_id"]

    db = SessionLocal()

    try:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return {
                "error": "Complaint not found",
                "next_action": "END"
            }

        # If already analyzed (e.g. from create_complaint), reuse it to avoid duplicate AI processing
        if complaint.category and complaint.confidence_score is not None:
            dept_name = complaint.department.name if complaint.department else state.get("department")
            return {
                "category": complaint.category,
                "department": dept_name,
                "severity": complaint.severity,
                "priority": complaint.priority,
                "confidence_score": complaint.confidence_score,
                "language": "English",
                "next_action": "ROUTE"
            }

        result = analyze_complaint(
            complaint.description
        )

        complaint.category = result.get("category")
        complaint.severity = result.get("severity", "MEDIUM")
        complaint.priority = result.get("priority", "MEDIUM")
        complaint.confidence_score = result.get("confidence_score")
        db.commit()

        return {
            "category": result.get("category"),
            "department": result.get("department"),
            "severity": result.get("severity"),
            "priority": result.get("priority"),
            "confidence_score": result.get("confidence_score"),
            "language": result.get("language"),
            "next_action": "ROUTE"
        }

    except Exception as e:

        return {
            "error": str(e),
            "next_action": "END"
        }

    finally:
        db.close()


def route_complaint_node(state):

    db = SessionLocal()

    try:

        complaint_id = state["complaint_id"]

        result = route_complaint(
            complaint_id,
            db
        )

        return {
            "department_id": result.get("department_id"),
            "ward_id": result.get("ward_id"),
            "officer_id": result.get("officer_id"),
            "sla_deadline": str(result.get("sla_deadline"))
            if result.get("sla_deadline")
            else None,
            "assigned_officer": result.get("officer") or result.get("officer_name"),
            "status": result.get("status"),
            "next_action": "WORK_ORDER"
        }

    except Exception as e:

        return {
            "error": str(e),
            "next_action": "END"
        }

    finally:
        db.close()


def create_work_order_node(state):

    db = SessionLocal()

    try:

        complaint_id = state["complaint_id"]

        result = create_work_order(
            complaint_id,
            db
        )

        return {
            "work_order_number": result.get("work_order_number"),
            "status": result.get("status"),
            "next_action": "NOTIFY"
        }

    except Exception as e:

        return {
            "error": str(e),
            "next_action": "END"
        }

    finally:
        db.close()


def notify_node(state):

    db = SessionLocal()

    try:

        complaint_id = state["complaint_id"]

        result = send_notification(
            complaint_id,
            "OFFICER",
            db
        )

        return {
            "notification_sent": True,
            "next_action": "END"
        }

    except Exception as e:

        return {
            "notification_sent": False,
            "error": str(e),
            "next_action": "END"
        }

    finally:
        db.close()
def confidence_check(state):

    confidence = state.get("confidence_score", 0.0)

    print(
        f"\n🤖 AI Confidence Score: {confidence}"
    )

    if confidence >= 0.85:

        print(
            "✅ High confidence → Autonomous processing"
        )

        return {
            "next_action": "ROUTE"
        }

    elif confidence >= 0.70:

        print(
            "⚠️ Medium confidence → Human review recommended"
        )

        return {
            "next_action": "ROUTE"
        }

    else:

        print(
            "🛑 Low confidence → Human review required"
        )

        return {
            "next_action": "HUMAN_REVIEW"
        }
def decide_after_confidence(state):

    next_action = state.get(
        "next_action",
        "END"
    )

    if next_action == "ROUTE":
        return "duplicate_detection"

    return "human_review"

def human_review_node(state):

    print("\n" + "=" * 60)
    print("🧑 HUMAN REVIEW REQUIRED")
    print("=" * 60)

    print(
        f"Complaint ID: {state.get('complaint_id')}"
    )

    print(
        f"Description: {state.get('description')}"
    )

    print(
        f"AI Category: {state.get('category')}"
    )

    print(
        f"AI Confidence: {state.get('confidence_score')}"
    )

    print("=" * 60)

    return {
        "status": "PENDING_HUMAN_REVIEW",
        "next_action": "END"
    }

def duplicate_detection_node(state):

    complaint_id = state["complaint_id"]

    print("\n🔎 Duplicate Detection Agent")

    result = find_duplicate_complaint(complaint_id)

    print(
        f"Semantic Similarity: {result['similarity']}"
    )

    print(
        f"Combined Duplicate Score: {result['duplicate_score']}"
    )

    db = SessionLocal()

    try:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return {
                "duplicate_found": False,
                "duplicate_complaint_id": None,
                "duplicate_similarity": 0.0,
                "next_action": "ROUTE"
            }

        if result["duplicate_found"]:

            duplicate_id = result["duplicate_complaint_id"]

            complaint.duplicate_of = duplicate_id

            history = ComplaintHistory(
                complaint_id=complaint_id,
                action="DUPLICATE_DETECTED",
                performed_by="AI_DUPLICATE_AGENT",
                previous_status=complaint.status,
                new_status=complaint.status,
                remarks=(
                    f"Potential duplicate of complaint "
                    f"{duplicate_id}. "
                    f"Score: {result['duplicate_score']}"
                )
            )

            db.add(history)
            db.commit()

            print("⚠️ Potential duplicate detected!")
            print(f"Existing Complaint ID: {duplicate_id}")
            print("✅ Duplicate relationship saved to database.")

            return {
                "duplicate_found": True,
                "duplicate_complaint_id": duplicate_id,
                "duplicate_similarity": result["similarity"],
                "next_action": "DUPLICATE"
            }

        print("✅ No significant duplicate found")

        return {
            "duplicate_found": False,
            "duplicate_complaint_id": None,
            "duplicate_similarity": result["similarity"],
            "next_action": "ROUTE"
        }

    finally:
        db.close()


def duplicate_handling_node(state):

    complaint_id = state["complaint_id"]
    duplicate_id = state.get("duplicate_complaint_id")

    print("\n⚠️ Duplicate Complaint Handler")

    if not duplicate_id:
        return {
            "next_action": "ROUTE"
        }

    db = SessionLocal()

    try:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.id == complaint_id)
            .first()
        )

        if not complaint:
            return {
                "error": "Complaint not found",
                "next_action": "END"
            }

        complaint.status = "UNDER_REVIEW"

        history = ComplaintHistory(
            complaint_id=complaint_id,
            action="DUPLICATE_LINKED",
            performed_by="AI_DUPLICATE_AGENT",
            previous_status=complaint.status,
            new_status="UNDER_REVIEW",
            remarks=(
                f"Complaint linked to existing complaint "
                f"{duplicate_id}"
            )
        )

        db.add(history)
        db.commit()

        print(
            f"🔗 Complaint {complaint_id} linked to "
            f"existing complaint {duplicate_id}"
        )

        print("📨 Citizen will be notified.")

        return {
            "next_action": "END"
        }

    finally:
        db.close()

def policy_agent_node(state):

    print("\n📚 Policy Agent")

    query = (
        f"What municipal policy applies to this complaint? "
        f"Complaint: {state['description']}. "
        f"Category: {state.get('category')}. "
        f"Department: {state.get('department')}."
    )

    result = policy_agent(query)

    return {
        "policy_answer": result["answer"],
        "policy_sources": result["sources"],
        "next_action": "ROUTE"
    }