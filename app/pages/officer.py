"""CivicPulse - Officer Dashboard Page
Workstation for municipal field officers and ward desk operators.
"""

from typing import Any, Dict, List
import pandas as pd
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


def render_officer_page():
    """Renders the municipal officer workstation and queue management desk."""
    hero_header(
        title="Municipal Officer Command Desk",
        subtitle="Manage assigned ward grievances, track resolution countdowns, update statuses, and handle escalations.",
        tag="OFFICER WORKSTATION"
    )

    # 1. Fetch metadata
    officers, _ = api_client.get_officers()
    departments, _ = api_client.get_departments()

    # Officer Filter / Selector
    col_sel1, col_sel2 = st.columns([6, 6])
    with col_sel1:
        officer_opts = {"ALL": "All Officers (Citywide Queue)"}
        for o in officers:
            officer_opts[str(o["id"])] = f"{o['name']} — {o.get('designation', 'Officer')} (ID: {o['id']})"

        selected_officer_key = st.selectbox(
            "Officer Profile / Workstation",
            options=list(officer_opts.keys()),
            format_func=lambda k: officer_opts[k]
        )

    with col_sel2:
        dept_opts = {"ALL": "All Departments"}
        for d in departments:
            dept_opts[str(d["id"])] = d["name"]
        selected_dept_key = st.selectbox(
            "Department Filter",
            options=list(dept_opts.keys()),
            format_func=lambda k: dept_opts[k]
        )

    # 2. Fetch complaints data
    dept_filter = int(selected_dept_key) if selected_dept_key != "ALL" else None
    with st.spinner("Fetching active municipal work queue..."):
        list_res, list_err = api_client.list_complaints(department_id=dept_filter, limit=300)
        active_res, _ = api_client.get_active_complaints()

    all_complaints = list_res.get("complaints", []) if list_res else []
    active_complaints = active_res.get("active_complaints", []) if active_res else []

    # Map SLA statuses to complaint list
    sla_map = {ac["id"]: ac.get("sla_status", "UNKNOWN") for ac in active_complaints}

    # Filter by officer if selected
    if selected_officer_key != "ALL":
        target_o_id = int(selected_officer_key)
        complaints_pool = [c for c in all_complaints if c.get("assigned_officer_id") == target_o_id]
    else:
        complaints_pool = all_complaints

    # -------------------------------------------------------------------------
    # Key Performance & Queue Metrics
    # -------------------------------------------------------------------------
    total_assigned = len(complaints_pool)
    pending_count = sum(1 for c in complaints_pool if c.get("status") in ("SUBMITTED", "UNDER_REVIEW"))
    in_progress_count = sum(1 for c in complaints_pool if c.get("status") in ("ASSIGNED", "IN_PROGRESS"))
    resolved_count = sum(1 for c in complaints_pool if c.get("status") in ("RESOLVED", "CITIZEN_CONFIRMED", "CLOSED"))

    # SLA metrics from active_complaints
    pool_ids = {c["id"] for c in complaints_pool}
    at_risk_count = sum(1 for ac in active_complaints if ac["id"] in pool_ids and ac.get("sla_status") == "AT_RISK")
    overdue_count = sum(1 for ac in active_complaints if ac["id"] in pool_ids and ac.get("sla_status") in ("OVERDUE", "CRITICAL"))

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        metric_card("Total Assigned", total_assigned, accent="#0284c7")
    with m2:
        metric_card("Pending Review", pending_count, accent="#f59e0b")
    with m3:
        metric_card("In Progress", in_progress_count, accent="#3b82f6")
    with m4:
        metric_card("Resolved", resolved_count, accent="#10b981")
    with m5:
        metric_card("SLA At Risk", at_risk_count, accent="#f97316")
    with m6:
        metric_card("Overdue / Critical", overdue_count, accent="#e11d48")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Filters & Complaint Table
    # -------------------------------------------------------------------------
    st.subheader("📋 Active Grievance Queue")

    f_col1, f_col2, f_col3 = st.columns([4, 4, 4])
    with f_col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["ALL", "SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "ESCALATED", "CITIZEN_CONFIRMED", "CLOSED"]
        )
    with f_col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        )
    with f_col3:
        search_filter = st.text_input("Search (ID, category, description)", placeholder="Search keyword...")

    # Apply filters
    filtered = complaints_pool
    if status_filter != "ALL":
        filtered = [c for c in filtered if (c.get("status") or "").upper() == status_filter]
    if priority_filter != "ALL":
        filtered = [c for c in filtered if (c.get("priority") or "").upper() == priority_filter]
    if search_filter:
        s_lower = search_filter.lower()
        filtered = [
            c for c in filtered
            if s_lower in str(c.get("id")).lower()
            or s_lower in (c.get("complaint_number") or "").lower()
            or s_lower in (c.get("category") or "").lower()
            or s_lower in (c.get("description") or "").lower()
        ]

    st.caption(f"Showing **{len(filtered)}** grievances matching criteria:")

    if filtered:
        # Prepare DataFrame for Streamlit display
        table_rows = []
        for c in filtered:
            cid = c.get("id")
            sla_st = sla_map.get(cid, "UNKNOWN")
            table_rows.append({
                "ID": cid,
                "Number": c.get("complaint_number"),
                "Category": c.get("category") or "General",
                "Priority": c.get("priority") or "MEDIUM",
                "Severity": c.get("severity") or "MEDIUM",
                "Status": c.get("status"),
                "Department": c.get("department_name") or "Unassigned",
                "Ward": c.get("ward_name") or f"Ward {c.get('ward_number', '')}",
                "Officer": c.get("assigned_officer_name") or "Unassigned",
                "SLA Status": sla_st,
                "Deadline": c.get("sla_deadline") or "N/A"
            })

        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No grievances match the selected filter criteria.")

    # -------------------------------------------------------------------------
    # Officer Action & Inspection Panel
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("⚡ Action Desk: Update Status & Manage Complaint")

    if filtered:
        comp_pick_map = {
            c["id"]: f"{c.get('complaint_number')} — {c.get('category')} ({c.get('status')})"
            for c in filtered
        }
        selected_target_id = st.selectbox(
            "Select Complaint to Inspect or Action",
            options=list(comp_pick_map.keys()),
            format_func=lambda cid: comp_pick_map[cid]
        )

        with st.spinner("Fetching full complaint details..."):
            detail_c, _ = api_client.get_complaint(selected_target_id)

        if detail_c:
            act_col1, act_col2 = st.columns([6, 6])

            with act_col1:
                st.markdown("##### ✏️ Update Status")
                with st.form("status_update_form"):
                    allowed_statuses = [
                        "UNDER_REVIEW",
                        "ASSIGNED",
                        "IN_PROGRESS",
                        "RESOLVED",
                        "ESCALATED",
                        "CLOSED"
                    ]
                    current_st = detail_c.get("status", "UNDER_REVIEW")
                    default_idx = allowed_statuses.index(current_st) if current_st in allowed_statuses else 0

                    new_status = st.selectbox("New Lifecycle Status", options=allowed_statuses, index=default_idx)
                    officer_name_input = st.text_input("Performed By", value=detail_c.get("assigned_officer_name") or "Field Officer")
                    remarks_input = st.text_area("Remarks / Work Notes", placeholder="Excavation completed, pipe leak plugged with epoxy sealant.")
                    submit_status = st.form_submit_button("Update Status", type="primary", use_container_width=True)

                if submit_status:
                    with st.spinner("Updating complaint status..."):
                        up_res, up_err = api_client.update_status(
                            complaint_id=selected_target_id,
                            new_status=new_status,
                            performed_by=officer_name_input,
                            remarks=remarks_input
                        )
                    if up_err:
                        st.error(f"❌ Failed to update status: {up_err}")
                    else:
                        st.success(f"✅ Complaint status updated to **{new_status}**!")
                        st.rerun()

            with act_col2:
                st.markdown("##### 🚨 Ward Escalation & SLA Agent Trigger")
                st.markdown(
                    f"""
                    <div class="civic-card" style="padding: 14px; margin-bottom: 12px;">
                        <div><strong>Complaint:</strong> {detail_c.get('complaint_number')}</div>
                        <div><strong>Description:</strong> {detail_c.get('description')}</div>
                        <div><strong>Current Status:</strong> {get_status_badge_html(detail_c.get('status'))}</div>
                        <div><strong>SLA Health:</strong> {get_sla_badge_html(detail_c.get('sla_info', {}).get('sla_status'))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("###### Trigger SLA Monitoring Agent")
                if st.button("⏱️ Run SLA Monitor Agent", key="btn_sla_mon", use_container_width=True):
                    with st.spinner("Executing SLA monitoring agent..."):
                        sla_res, sla_err = api_client.monitor_sla(selected_target_id)
                    if sla_err:
                        st.error(f"❌ {sla_err}")
                    else:
                        st.success(f"✅ SLA Monitor Agent executed: {sla_res.get('agent_result', {}).get('action', 'Completed')}")
                        st.rerun()

                st.markdown("###### Manual Ward Escalation")
                with st.form("manual_escalation_form"):
                    esc_reason = st.text_input("Escalation Reason", placeholder="Requires heavy machinery not available at ward depot.")
                    esc_submit = st.form_submit_button("🚨 Escalate to Ward Head", type="secondary", use_container_width=True)

                if esc_submit:
                    if not esc_reason:
                        st.error("Please specify a reason for escalation.")
                    else:
                        with st.spinner("Escalating grievance to senior authority..."):
                            esc_res, esc_err = api_client.escalate_complaint(selected_target_id, esc_reason)
                        if esc_err:
                            st.error(f"❌ Escalation failed: {esc_err}")
                        else:
                            st.warning(f"🚨 Complaint escalated successfully!")
                            st.rerun()
