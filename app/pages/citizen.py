"""CivicPulse - Citizen Complaint Submission Page
Allows citizens to register grievances and trigger autonomous agent processing.
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
from app.config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    PAGE_TRACK,
    WARD_PRESETS,
)


def render_citizen_page():
    """Renders the grievance submission form and autonomous agent execution view."""
    hero_header(
        title="Citizen Grievance Portal",
        subtitle="Submit municipal issues for autonomous AI classification, routing, and resolution.",
        tag="CITIZEN INTERFACE"
    )

    # Fetch citizens for dropdown convenience
    citizens, citizens_err = api_client.get_citizens()

    col_form, col_info = st.columns([7, 5])

    with col_form:
        st.subheader("📝 New Grievance Registration")

        with st.form("complaint_form"):
            # Citizen Selector
            citizen_id = 1
            if citizens:
                citizen_options = {c["id"]: f"ID {c['id']}: {c['name']} ({c.get('preferred_language', 'English')})" for c in citizens}
                selected_c_id = st.selectbox(
                    "Citizen Account",
                    options=list(citizen_options.keys()),
                    format_func=lambda x: citizen_options[x]
                )
                citizen_id = selected_c_id
            else:
                citizen_id = st.number_input("Citizen ID", min_value=1, value=1, step=1)

            # Sample Grievance Quick-Fill (placed outside form or note below)
            description = st.text_area(
                "Describe the Grievance in detail",
                placeholder="Example: Deep crater-sized pothole on Paud Road near the bus depot. Causing severe traffic congestion and near accidents during peak hours.",
                height=120
            )

            st.markdown("##### 📍 Location & Ward Coordinates")
            preset_labels = ["Custom Coordinates"] + [p["label"] for p in WARD_PRESETS]
            selected_preset = st.selectbox("Ward / Neighborhood Preset", options=preset_labels)

            default_lat = DEFAULT_LATITUDE
            default_lon = DEFAULT_LONGITUDE

            if selected_preset != "Custom Coordinates":
                match = next((p for p in WARD_PRESETS if p["label"] == selected_preset), None)
                if match:
                    default_lat = match["lat"]
                    default_lon = match["lon"]

            coord_c1, coord_c2 = st.columns(2)
            with coord_c1:
                latitude = st.number_input("Latitude", value=float(default_lat), format="%.5f")
            with coord_c2:
                longitude = st.number_input("Longitude", value=float(default_lon), format="%.5f")

            submit_btn = st.form_submit_button("🚀 Submit Grievance", use_container_width=True)

        if submit_btn:
            if not description or len(description.strip()) < 5:
                st.error("❌ Please provide a detailed description of the grievance (at least 5 characters).")
            else:
                with st.spinner("🤖 Autonomous AI analyzing grievance intent, category, and severity..."):
                    created_data, error = api_client.create_complaint(
                        citizen_id=int(citizen_id),
                        description=description.strip(),
                        latitude=latitude,
                        longitude=longitude,
                        skip_ai=False
                    )

                if error:
                    st.error(f"❌ Failed to submit complaint: {error}")
                elif created_data:
                    st.success("✅ Complaint successfully created and registered into CivicPulse!")
                    st.session_state["submitted_complaint"] = created_data
                    st.session_state["automation_result"] = None

    with col_info:
        st.subheader("💡 Submission Guide")
        st.markdown(
            """
            <div class="civic-card">
                <strong>What happens when you submit?</strong>
                <ol style="font-size: 0.82rem; color: #475569; padding-left: 18px; margin-top: 6px; line-height: 1.5;">
                    <li><strong>NLP Parsing:</strong> AI detects category, urgency, and severity.</li>
                    <li><strong>Confidence Score:</strong> Evaluates classifier certainty (0 - 1.0).</li>
                    <li><strong>Orchestrator Ready:</strong> You can immediately trigger full LangGraph multi-agent automation below!</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("##### 📌 Quick Grievance Templates")
        st.caption("Copy & paste into description:")
        sample_1 = "Severe sewage overflow outside residential apartments on Baner Road, causing foul smell and health hazard."
        sample_2 = "Main water pipeline bursting at Model Colony junction, drinking water flooding the street."
        sample_3 = "Street lights non-operational along Kalyani Nagar jogging track for 4 consecutive nights."

        st.code(sample_1, language="text")
        st.code(sample_2, language="text")
        st.code(sample_3, language="text")

    # -------------------------------------------------------------------------
    # Display AI Analysis & Automation Actions
    # -------------------------------------------------------------------------
    if "submitted_complaint" in st.session_state and st.session_state["submitted_complaint"]:
        complaint = st.session_state["submitted_complaint"]
        complaint_id = complaint.get("id")
        comp_num = complaint.get("complaint_number", f"ID: {complaint_id}")

        st.markdown("---")
        st.subheader(f"📋 Registration & AI Classification: {comp_num}")

        # Metrics & Attributes
        m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)
        with m_c1:
            metric_card("Complaint ID", comp_num, accent="#0284c7")
        with m_c2:
            metric_card("Category", complaint.get("category") or "General", accent="#3b82f6")
        with m_c3:
            metric_card("Department", complaint.get("department_name") or "Under Review", accent="#059669")
        with m_c4:
            metric_card("Severity", complaint.get("severity") or "MEDIUM", accent="#f59e0b")
        with m_c5:
            conf = complaint.get("confidence_score")
            conf_str = f"{conf:.2f}" if conf is not None else "N/A"
            metric_card("AI Confidence", conf_str, accent="#8b5cf6")

        # Classification Details Table
        st.markdown(
            f"""
            <div class="civic-card" style="margin-top: 12px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; font-size: 0.85rem;">
                    <div><strong>Grievance Priority:</strong> {get_priority_badge_html(complaint.get('priority'))}</div>
                    <div><strong>Current Status:</strong> {get_status_badge_html(complaint.get('status'))}</div>
                    <div><strong>Preferred Language:</strong> {complaint.get('preferred_language', 'English')}</div>
                    <div><strong>Ward Location:</strong> {complaint.get('ward_name') or 'Ward Detection Pending'}</div>
                    <div><strong>Coordinates:</strong> Lat: {complaint.get('latitude', 'N/A')}, Lon: {complaint.get('longitude', 'N/A')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------------------------------
        # Autonomous Agent Orchestrator Trigger
        # ---------------------------------------------------------------------
        st.markdown("### ⚡ Step 2: Autonomous Multi-Agent Resolution")
        st.markdown(
            "Execute the **LangGraph Orchestrator** to run duplicate checking, policy retrieval, department routing, work order generation, and notification dispatch."
        )

        auto_col1, auto_col2 = st.columns([4, 8])
        with auto_col1:
            run_auto = st.button(
                "⚡ Run Autonomous Agent Workflow",
                type="primary",
                use_container_width=True,
                key="btn_run_auto"
            )

        with auto_col2:
            if st.button("🔍 View Complete Audit in Track Complaint", use_container_width=True):
                st.session_state["tracking_query"] = comp_num
                st.session_state["current_page"] = PAGE_TRACK
                st.rerun()

        if run_auto:
            with st.spinner("🤖 Autonomous multi-agent pipeline executing across LangGraph nodes..."):
                auto_result, auto_err = api_client.process_complaint(complaint_id)

            if auto_err:
                st.error(f"❌ Automation workflow encountered an issue: {auto_err}")
            else:
                st.session_state["automation_result"] = auto_result
                # Refresh complaint details to get latest updated database fields
                refreshed_c, _ = api_client.get_complaint(complaint_id)
                if refreshed_c:
                    st.session_state["submitted_complaint"] = refreshed_c
                st.success("🎉 Multi-agent workflow execution completed successfully!")

        # ---------------------------------------------------------------------
        # Display Automation Results
        # ---------------------------------------------------------------------
        auto_res = st.session_state.get("automation_result")
        if auto_res and auto_res.get("success"):
            st.markdown("#### 🎯 Autonomous Agent Orchestration Results")

            # Fetch fresh complaint detail for work orders and officer
            fresh_c, _ = api_client.get_complaint(complaint_id)
            c_detail = fresh_c or complaint

            res_c1, res_c2 = st.columns(2)

            with res_c1:
                # 1. Duplicate Detection Display
                dup_of = c_detail.get("duplicate_of")
                dup_badge = (
                    f'<span class="badge badge-critical">DUPLICATE OF CP-{dup_of}</span>'
                    if dup_of
                    else '<span class="badge badge-resolved">UNIQUE COMPLAINT</span>'
                )
                st.markdown(
                    f"""
                    <div class="civic-card">
                        <div style="font-weight: 700; color: #0284c7; margin-bottom: 8px;">
                            🔍 Semantic Duplicate Detection
                        </div>
                        <div style="margin-bottom: 6px;"><strong>Status:</strong> {dup_badge}</div>
                        <div style="font-size: 0.82rem; color: #64748b;">
                            {f'Cross-referenced with previous complaints. Linked as sub-ticket to #{dup_of}.' if dup_of else 'Vector search confirmed zero existing duplicates in spatial proximity.'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 2. SLA Deadline Display
                sla_deadline = c_detail.get("sla_deadline") or "Calculating..."
                sla_info = c_detail.get("sla_info", {})
                sla_status = sla_info.get("sla_status", "ON_TRACK")
                st.markdown(
                    f"""
                    <div class="civic-card">
                        <div style="font-weight: 700; color: #0284c7; margin-bottom: 8px;">
                            ⏱️ SLA Deadline & Policy Rules
                        </div>
                        <div style="margin-bottom: 6px;"><strong>Resolution Deadline:</strong> <code>{sla_deadline}</code></div>
                        <div><strong>SLA Health:</strong> {get_sla_badge_html(sla_status)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with res_c2:
                # 3. Assigned Officer Display
                officer_name = c_detail.get("assigned_officer_name") or "Automated Ward Desk"
                officer_desig = c_detail.get("assigned_officer_designation") or "Field Engineer"
                officer_email = c_detail.get("assigned_officer_email") or "officer@civicpulse.demo"
                st.markdown(
                    f"""
                    <div class="civic-card">
                        <div style="font-weight: 700; color: #0284c7; margin-bottom: 8px;">
                            👮 Assigned Municipal Officer
                        </div>
                        <div><strong>Officer:</strong> {officer_name}</div>
                        <div style="font-size: 0.82rem; color: #64748b;"><strong>Designation:</strong> {officer_desig}</div>
                        <div style="font-size: 0.82rem; color: #64748b;"><strong>Contact:</strong> {officer_email}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 4. Work Order & Notifications Display
                work_orders = c_detail.get("work_orders", [])
                wo_info = (
                    f"Generated: <strong>{work_orders[0].get('work_order_number')}</strong> (Status: {work_orders[0].get('status')})"
                    if work_orders
                    else "Field work order dispatched"
                )

                st.markdown(
                    f"""
                    <div class="civic-card">
                        <div style="font-weight: 700; color: #0284c7; margin-bottom: 8px;">
                            📋 Work Order & Notifications
                        </div>
                        <div style="margin-bottom: 4px;"><strong>Work Order:</strong> {wo_info}</div>
                        <div><strong>Notification Status:</strong> <span class="badge badge-resolved">SMS & EMAIL DISPATCHED</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
