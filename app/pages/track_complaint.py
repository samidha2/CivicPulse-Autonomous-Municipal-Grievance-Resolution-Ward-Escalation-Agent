"""CivicPulse - Track Complaint Page
Real-time tracking of grievance status, SLA monitoring, work orders, and audit timeline.
"""

from typing import Any, Dict
import streamlit as st

from app.api_client import api_client
from app.components.cards import (
    get_priority_badge_html,
    get_sla_badge_html,
    get_status_badge_html,
    hero_header,
    metric_card,
)
from app.components.timeline import render_complaint_timeline


def render_track_page():
    """Renders the complaint tracking and lifecycle audit interface."""
    hero_header(
        title="Grievance Lifecycle Tracking",
        subtitle="Transparent audit trail, real-time SLA countdown, and officer field assignment status.",
        tag="PUBLIC AUDIT INTERFACE"
    )

    # Check if a tracking query was passed via session state
    initial_query = st.session_state.get("tracking_query", "CP-2026-0001")

    # Fetch recent complaints for quick selection
    recent_data, _ = api_client.list_complaints(limit=15)
    recent_complaints = recent_data.get("complaints", []) if recent_data else []

    col_search, col_picker = st.columns([6, 6])
    with col_search:
        search_input = st.text_input(
            "Enter Complaint Number or Database ID",
            value=initial_query,
            placeholder="e.g. CP-2026-0001 or 1"
        )
    with col_picker:
        if recent_complaints:
            options = {
                c["complaint_number"]: f"{c['complaint_number']} - {c.get('category', 'General')} ({c.get('status', 'SUBMITTED')})"
                for c in recent_complaints
            }
            selected_recent = st.selectbox(
                "Or Select a Recent Complaint to Inspect",
                options=["-- Select --"] + list(options.keys()),
                format_func=lambda x: options.get(x, x)
            )
            if selected_recent != "-- Select --":
                search_input = selected_recent

    track_btn = st.button("🔎 Track Complaint", use_container_width=True, type="primary")

    target_id = search_input.strip() if (track_btn or search_input) else None

    if target_id:
        with st.spinner(f"Fetching complaint records for '{target_id}'..."):
            complaint, err = api_client.get_complaint(target_id)

        if err:
            st.error(f"❌ {err}")
            return

        if not complaint:
            st.warning(f"⚠️ No complaint found matching identifier: '{target_id}'")
            return

        # ---------------------------------------------------------------------
        # Complaint Details Banner & Key Attributes
        # ---------------------------------------------------------------------
        comp_id = complaint.get("id")
        comp_num = complaint.get("complaint_number", f"ID: {comp_id}")
        st.markdown(f"### 📋 Overview: {comp_num}")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            metric_card("Status", complaint.get("status", "SUBMITTED"), accent="#0284c7")
        with col2:
            metric_card("Category", complaint.get("category") or "Unclassified", accent="#3b82f6")
        with col3:
            metric_card("Department", complaint.get("department_name") or "Unassigned", accent="#059669")
        with col4:
            metric_card("Ward", complaint.get("ward_name") or "Ward Pending", accent="#d97706")
        with col5:
            sla_info = complaint.get("sla_info", {})
            sla_st = sla_info.get("sla_status", "UNKNOWN")
            metric_card("SLA Status", sla_st, accent="#e11d48")

        # Detailed Attribute Grid
        st.markdown(
            f"""
            <div class="civic-card" style="margin-top: 14px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 0.85rem;">
                    <div><strong>Citizen Name:</strong> {complaint.get('citizen_name', 'Anonymous Citizen')}</div>
                    <div><strong>Citizen Contact:</strong> {complaint.get('citizen_phone') or 'Protected'}</div>
                    <div><strong>Registration Date:</strong> {complaint.get('created_at', 'N/A')}</div>
                    <div><strong>Priority Level:</strong> {get_priority_badge_html(complaint.get('priority'))}</div>
                    <div><strong>Severity Level:</strong> {get_priority_badge_html(complaint.get('severity'))}</div>
                    <div><strong>Current Status:</strong> {get_status_badge_html(complaint.get('status'))}</div>
                    <div><strong>Assigned Officer:</strong> {complaint.get('assigned_officer_name') or 'Pending Assignment'}</div>
                    <div><strong>Officer Email:</strong> {complaint.get('assigned_officer_email') or 'N/A'}</div>
                </div>
                <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 0.9rem;">
                    <strong>Citizen Description:</strong>
                    <div style="background: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 6px; color: #1e293b; border: 1px solid #e2e8f0;">
                        "{complaint.get('description', '')}"
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------------------------------
        # SLA & Work Orders Grid
        # ---------------------------------------------------------------------
        st.markdown("---")
        sla_col, wo_col = st.columns(2)

        with sla_col:
            st.subheader("⏱️ SLA Monitoring & Timelines")
            sla_data = complaint.get("sla_info", {})
            rem_hours = sla_data.get("remaining_hours")
            should_esc = sla_data.get("should_escalate", False)

            rem_text = f"{rem_hours:.1f} hours remaining" if rem_hours is not None else "Calculating..."
            if rem_hours is not None and rem_hours < 0:
                rem_text = f"⚠️ Overdue by {abs(rem_hours):.1f} hours"

            st.markdown(
                f"""
                <div class="civic-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong>SLA Health:</strong> {get_sla_badge_html(sla_data.get('sla_status'))}
                    </div>
                    <div style="font-size: 0.85rem; margin-bottom: 6px;">
                        <strong>SLA Deadline:</strong> <code>{complaint.get('sla_deadline') or 'No deadline configured'}</code>
                    </div>
                    <div style="font-size: 0.85rem; margin-bottom: 6px;">
                        <strong>Countdown:</strong> <span style="font-weight: 700; color: {'#dc2626' if (rem_hours and rem_hours < 0) else '#0284c7'};">{rem_text}</span>
                    </div>
                    <div style="font-size: 0.85rem;">
                        <strong>Auto-Escalation Flag:</strong> {'🚨 Escalation Required' if should_esc else '✅ Within safe parameters'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Manual SLA check button
            if st.button("🔄 Refresh SLA Status", key="refresh_sla"):
                with st.spinner("Recomputing SLA parameters..."):
                    sla_res, _ = api_client.check_sla(comp_id)
                    if sla_res:
                        st.toast("SLA parameters successfully refreshed!")
                        st.rerun()

        with wo_col:
            st.subheader("📋 Field Work Orders")
            work_orders = complaint.get("work_orders", [])
            if work_orders:
                for wo in work_orders:
                    st.markdown(
                        f"""
                        <div class="civic-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <strong>Work Order #{wo.get('work_order_number')}</strong>
                                <span class="badge badge-assigned">{wo.get('status', 'ACTIVE')}</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 4px;">
                                <strong>Assigned Field Staff ID:</strong> {wo.get('assigned_to') or 'General Field Unit'}
                            </div>
                            <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 4px;">
                                <strong>Issued Date:</strong> {wo.get('created_at', 'N/A')}
                            </div>
                            <div style="font-size: 0.85rem; color: #1e293b; background: #f8fafc; padding: 6px 8px; border-radius: 4px;">
                                {wo.get('description', 'Standard municipal remediation task.')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("ℹ️ No field work orders created yet for this grievance.")

        # ---------------------------------------------------------------------
        # Lifecycle Timeline
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📜 Status Audit Trail & Lifecycle Timeline")
        render_complaint_timeline(complaint.get("history", []))

        # ---------------------------------------------------------------------
        # Citizen Feedback Section
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.subheader("⭐ Citizen Resolution Verification & Feedback")

        feedbacks = complaint.get("feedback", [])
        if feedbacks:
            st.markdown("##### Previous Feedback Recorded:")
            for fb in feedbacks:
                acc_label = "✅ Accepted Resolution" if fb.get("resolution_accepted") else "❌ Rejected Resolution"
                st.markdown(
                    f"""
                    <div class="civic-card" style="padding: 12px;">
                        <div><strong>Rating:</strong> {'⭐' * fb.get('rating', 5)} ({fb.get('rating')}/5) &nbsp;|&nbsp; <strong>Verdict:</strong> {acc_label}</div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">"{fb.get('comments') or 'No comments provided.'}" - <em>{fb.get('created_at')}</em></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Allow citizen to submit feedback
        with st.expander("Submit Citizen Verification & Rating"):
            with st.form("feedback_form"):
                rating = st.slider("Satisfaction Rating (1 - 5 stars)", min_value=1, max_value=5, value=5)
                accepted = st.checkbox("I confirm the municipal grievance was satisfactorily addressed", value=True)
                fb_comments = st.text_area("Citizen Feedback Remarks", placeholder="The pothole was neatly filled and leveled. Thank you.")
                submit_fb = st.form_submit_button("Submit Feedback", use_container_width=True)

            if submit_fb:
                with st.spinner("Submitting citizen resolution feedback..."):
                    res_fb, err_fb = api_client.submit_feedback(
                        complaint_id=comp_id,
                        rating=rating,
                        comments=fb_comments.strip() or None,
                        resolution_accepted=accepted
                    )
                if err_fb:
                    st.error(f"❌ Failed to submit feedback: {err_fb}")
                else:
                    st.success("✅ Thank you! Your feedback has been recorded and the complaint status updated.")
                    st.rerun()
