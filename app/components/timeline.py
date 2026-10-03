"""CivicPulse - Complaint Timeline Component
Renders the audit trail and lifecycle progression of a municipal complaint.
"""

from typing import Any, Dict, List
import streamlit as st

from app.components.cards import get_status_badge_html


def render_complaint_timeline(history: List[Dict[str, Any]]):
    """Renders a chronological visual timeline of grievance events."""
    if not history:
        st.info("ℹ️ No historical activity transitions recorded yet for this complaint.")
        return

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    for idx, item in enumerate(history):
        action = item.get("action", "STATUS_CHANGE").replace("_", " ")
        performer = item.get("performed_by", "System")
        ts = item.get("timestamp") or "Timestamp pending"
        remarks = item.get("remarks") or "No additional remarks logged."
        new_status = item.get("new_status")
        prev_status = item.get("previous_status")

        # Determine icon based on performer or action
        icon = "🤖"
        if "CITIZEN" in performer.upper() or "CITIZEN" in action.upper():
            icon = "👤"
        elif "OFFICER" in performer.upper():
            icon = "👮"
        elif "WORK_ORDER" in action.upper():
            icon = "📋"
        elif "DUPLICATE" in action.upper():
            icon = "🔍"
        elif "ESCALAT" in action.upper():
            icon = "🚨"

        status_transition_html = ""
        if new_status:
            if prev_status and prev_status != new_status:
                status_transition_html = f'<div style="margin: 6px 0;">{get_status_badge_html(prev_status)} ➔ {get_status_badge_html(new_status)}</div>'
            else:
                status_transition_html = f'<div style="margin: 6px 0;">{get_status_badge_html(new_status)}</div>'

        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="timeline-bullet"></div>
                <div class="timeline-content">
                    <div class="timeline-title">
                        {icon} {action}
                    </div>
                    <div class="timeline-meta">
                        <strong>Actor:</strong> {performer} &nbsp;|&nbsp; <strong>Date:</strong> {ts}
                    </div>
                    {status_transition_html}
                    <div class="timeline-remarks">
                        {remarks}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
