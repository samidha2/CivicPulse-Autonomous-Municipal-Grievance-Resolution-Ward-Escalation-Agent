"""CivicPulse - Home & Landing Page
Comprehensive executive overview of the Autonomous Municipal Grievance Resolution & Ward Escalation Agent.
"""

import streamlit as st

from app.api_client import api_client
from app.components.cards import hero_header, metric_card
from app.config import (
    PAGE_ADMIN,
    PAGE_ASSISTANT,
    PAGE_CITIZEN,
    PAGE_OFFICER,
    PAGE_TRACK,
)


def render_home_page():
    """Renders the CivicPulse landing and architecture overview page."""
    hero_header(
        title="CivicPulse",
        subtitle="Autonomous Municipal Grievance Resolution & Ward Escalation Agent — End-to-End Multilingual Orchestration for 24/7 Smart City Redressal",
        tag="SMART CITY GOVERNANCE SYSTEM"
    )

    # -------------------------------------------------------------------------
    # Live Municipal Snapshot Bar
    # -------------------------------------------------------------------------
    summary, err = api_client.get_analytics_summary()
    if summary:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            metric_card("Total Registered", summary.get("total", 0), accent="#2563eb", icon="📊")
        with col2:
            metric_card("Active Open Cases", summary.get("open", 0), accent="#f59e0b", icon="📂")
        with col3:
            metric_card("Successfully Resolved", summary.get("resolved", 0), accent="#10b981", icon="✅")
        with col4:
            metric_card("SLA Escalated", summary.get("escalated", 0), accent="#e11d48", icon="🚨")
        with col5:
            metric_card("Work Orders", summary.get("work_orders", 0),accent="#7c3aed", icon="📋")
    elif err:
        st.warning(f"⚠️ Live metrics summary unavailable: {err}")

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Agent Workflow Pipeline
    # -------------------------------------------------------------------------
    st.markdown("### 🔄 End-to-End Autonomous Agent Workflow")
    st.caption("How a citizen complaint flows seamlessly through the autonomous multi-agent mesh without manual human bottlenecks:")

    workflow_steps = [
        {"num": "01", "icon": "📥", "title": "Complaint", "sub": "Citizen Ingestion"},
        {"num": "02", "icon": "🧠", "title": "AI Understanding", "sub": "Category & Intent"},
        {"num": "03", "icon": "🎯", "title": "Confidence Check", "sub": "Validation Threshold"},
        {"num": "04", "icon": "🔍", "title": "Duplicate Detection", "sub": "Dense Embeddings"},
        {"num": "05", "icon": "📚", "title": "Policy / RAG", "sub": "Municipal Bylaws"},
        {"num": "06", "icon": "🏢", "title": "Department Routing", "sub": "Ward Officer Assign"},
        {"num": "07", "icon": "📋", "title": "Work Order", "sub": "Field Dispatch"},
        {"num": "08", "icon": "📲", "title": "Notification", "sub": "SMS / Email Alerts"},
        {"num": "09", "icon": "⏱️", "title": "SLA Monitoring", "sub": "Real-time Countdown"},
        {"num": "10", "icon": "🚨", "title": "Escalation", "sub": "Ward Command Trigger"},
    ]

    # Render workflow in a horizontal responsive layout
    cols = st.columns(len(workflow_steps))
    for i, step in enumerate(workflow_steps):
        with cols[i]:
            arrow = "➔" if i < len(workflow_steps) - 1 else "🏁"
            st.markdown(
                f"""
                <div class="pipeline-step">
                    <div>
                        <div class="step-number">{step['num']}</div>
                        <div class="step-icon">{step['icon']}</div>
                        <div class="step-title">{step['title']}</div>
                        <div class="step-sub">{step['sub']}</div>
                    </div>
                    <div class="step-arrow">{arrow}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Core Agent Architecture & Capabilities
    # -------------------------------------------------------------------------
    st.markdown("### 🧩 Major Agents & AI Subsystems")
    st.caption("Specialized autonomous components orchestrating municipal grievance resolution:")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            """
            <div class="civic-card feature-card feature-indigo">
                <div style="font-size: 1.12rem; font-weight: 800; color: #1e3a8a; margin-bottom: 6px;">
                    🤖 Grievance Understanding Agent
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Ingests unstructured natural language grievances in English, Hindi, and Marathi. Identifies category, detects severity, assigns priority, and calculates an AI confidence score.
                </p>
                <div style="display: inline-block; background: #e0e7ff; color: #3730a3; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    Gemini 1.5 • LangGraph Node
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="civic-card feature-card feature-emerald">
                <div style="font-size: 1.12rem; font-weight: 800; color: #065f46; margin-bottom: 6px;">
                    🔍 Semantic Duplicate Detection
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Prevents municipal ticket bloat. Performs dense vector similarity search to cross-reference recent grievances within spatial and temporal proximity thresholds.
                </p>
                <div style="display: inline-block; background: #d1fae5; color: #065f46; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    ChromaDB • Vector Similarity
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_b:
        st.markdown(
            """
            <div class="civic-card feature-card feature-purple">
                <div style="font-size: 1.12rem; font-weight: 800; color: #5b21b6; margin-bottom: 6px;">
                    📚 Municipal Policy & RAG Agent
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Grounds actions in official citizen charters, bylaws, standard operating procedures, and resolution timelines. Provides conversational policy retrieval with verifiable citations.
                </p>
                <div style="display: inline-block; background: #ede9fe; color: #5b21b6; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    RAG Embeddings • Citizen Charters
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="civic-card feature-card feature-amber">
                <div style="font-size: 1.12rem; font-weight: 800; color: #92400e; margin-bottom: 6px;">
                    🏢 Smart Routing & Dispatch Agent
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Resolves municipal jurisdictional boundaries. Maps GPS coordinates to designated wards and routes tickets to appropriate department field engineers with automated work orders.
                </p>
                <div style="display: inline-block; background: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    GIS Matrix • Automated Work Orders
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_c:
        st.markdown(
            """
            <div class="civic-card feature-card feature-rose">
                <div style="font-size: 1.12rem; font-weight: 800; color: #9f1239; margin-bottom: 6px;">
                    ⏱️ Watchdog SLA & Escalation Engine
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Continuously checks resolution countdowns against category SLA rules. Autonomously escalates overdue cases up the municipal command chain to Ward Commissioners.
                </p>
                <div style="display: inline-block; background: #ffe4e6; color: #9f1239; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    Temporal SLA Engine • Ward Hierarchy
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="civic-card feature-card feature-cyan">
                <div style="font-size: 1.12rem; font-weight: 800; color: #0e7490; margin-bottom: 6px;">
                    📲 Citizen Notification Dispatcher
                </div>
                <p style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                    Keeps the citizen informed in real-time across the lifecycle: submission acknowledgement, officer assignment, resolution notification, and post-resolution feedback verification.
                </p>
                <div style="display: inline-block; background: #cffafe; color: #0e7490; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">
                    Omnichannel • Multilingual Templates
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Quick Action Portals
    # -------------------------------------------------------------------------
    st.markdown("### 🚀 Quick Action Portals")
    st.caption("Access role-based portals across the municipal grievance ecosystem:")

    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)

    with qa_col1:
        if st.button("📝 Citizen Portal", use_container_width=True, type="primary"):
            st.session_state["current_page"] = PAGE_CITIZEN
            st.rerun()
        st.caption("Submit new grievance & run AI workflow")

    with qa_col2:
        if st.button("🔍 Track Complaint", use_container_width=True):
            st.session_state["current_page"] = PAGE_TRACK
            st.rerun()
        st.caption("Real-time SLA & timeline tracking")

    with qa_col3:
        if st.button("👮 Officer Desk", use_container_width=True):
            st.session_state["current_page"] = PAGE_OFFICER
            st.rerun()
        st.caption("Ward queue management & status updates")

    with qa_col4:
        if st.button("📊 Executive Analytics", use_container_width=True):
            st.session_state["current_page"] = PAGE_ADMIN
            st.rerun()
        st.caption("Citywide Plotly metrics & GIS map")
