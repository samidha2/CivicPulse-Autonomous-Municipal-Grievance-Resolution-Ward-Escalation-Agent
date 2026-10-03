from services.sla_service import (
    check_sla_status,
    escalate_complaint
)


def sla_monitoring_agent(complaint_id: int):

    print("\n⏱️ SLA Monitoring Agent")

    result = check_sla_status(complaint_id)

    if not result.get("found"):
        return {
            "success": False,
            "action": "ERROR",
            "message": "Complaint not found"
        }

    sla_status = result["sla_status"]

    print(f"SLA Status: {sla_status}")
    print(f"Remaining Hours: {result.get('remaining_hours')}")

    # Completed complaint
    if sla_status == "COMPLETED":

        print("✅ Complaint already completed.")

        return {
            "success": True,
            "action": "NONE",
            "sla_status": sla_status,
            "should_escalate": False
        }

    # SLA is healthy
    if sla_status == "ON_TRACK":

        print("🟢 Complaint is within SLA.")

        return {
            "success": True,
            "action": "MONITOR",
            "sla_status": sla_status,
            "should_escalate": False
        }

    # SLA approaching deadline
    if sla_status == "AT_RISK":

        print("🟡 Complaint is approaching SLA deadline.")

        return {
            "success": True,
            "action": "WARNING",
            "sla_status": sla_status,
            "should_escalate": False
        }

    # Critical or overdue
    if sla_status in ["CRITICAL", "OVERDUE"]:

        reason = (
            "SLA deadline approaching"
            if sla_status == "CRITICAL"
            else "SLA deadline breached"
        )

        print(f"🚨 {reason}")

        escalation = escalate_complaint(
            complaint_id,
            reason
        )

        return {
            "success": True,
            "action": "ESCALATE",
            "sla_status": sla_status,
            "should_escalate": True,
            "escalation": escalation
        }

    return {
        "success": True,
        "action": "NONE",
        "sla_status": sla_status,
        "should_escalate": False
    }