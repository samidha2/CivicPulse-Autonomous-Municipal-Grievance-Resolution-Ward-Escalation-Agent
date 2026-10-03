"""CivicPulse - Autonomous Municipal Grievance Resolution & Ward Escalation Agent
Main Streamlit application entry point.
"""

import os
import sys
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="CivicPulse — Municipal Grievance Agent",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject custom CSS styling
css_path = os.path.join(os.path.dirname(__file__), "styles", "civicpulse.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.components.cards import hero_header
from app.components.sidebar import render_sidebar
from app.config import (
    PAGE_ABOUT,
    PAGE_ADMIN,
    PAGE_ASSISTANT,
    PAGE_CITIZEN,
    PAGE_HOME,
    PAGE_OFFICER,
    PAGE_TRACK,
)
from app.pages.admin import render_admin_page
from app.pages.assistant import render_assistant_page
from app.pages.citizen import render_citizen_page
from app.pages.home import render_home_page
from app.pages.officer import render_officer_page
from app.pages.track_complaint import render_track_page


def render_about_page():
    """Renders platform specifications and architecture overview."""
    hero_header(
        title="About CivicPulse",
        subtitle="Autonomous Agentic AI Infrastructure for 24/7 Smart Municipal Governance",
        tag="SYSTEM INFORMATION"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="civic-card">
                <div style="font-size: 1.15rem; font-weight: 800; color: #1e3a8a; margin-bottom: 8px;">
                    🏛️ Mission & System Scope
                </div>
                <p style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                    <strong>CivicPulse</strong> is an autonomous municipal grievance resolution and ward escalation agent.
                    It replaces rigid legacy ticketing portals with an intelligent, self-orchestrating agent mesh
                    that understands multilingual complaints, detects duplicates, consults municipal bylaws,
                    dispatches work orders, monitors resolution SLAs, and enforces ward escalations autonomously.
                </p>
                <div style="margin-top: 12px; padding: 10px; background: #eff6ff; border-radius: 8px; font-size: 0.82rem; color: #1e40af; border: 1px solid #bfdbfe;">
                    🎓 <strong>Academic Demonstration:</strong> Built for SCIT MBA-DSDA Agentic AI Capstone.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="civic-card">
                <div style="font-size: 1.15rem; font-weight: 800; color: #065f46; margin-bottom: 8px;">
                    🛡️ Safety & Autonomous Verification
                </div>
                <ul style="font-size: 0.86rem; color: #475569; line-height: 1.6; padding-left: 20px;">
                    <li><strong>Confidence Check Node:</strong> Ensures complaints below 0.65 AI certainty are flagged for human review.</li>
                    <li><strong>Deterministic Deduplication:</strong> Spatial and semantic similarity checks prevent redundant contractor dispatches.</li>
                    <li><strong>Transparent Audit History:</strong> Every status transition, action, and officer remark is cryptographically logged.</li>
                    <li><strong>Citizen Feedback Loop:</strong> Resolution verification and satisfaction scoring directly drive grievance closure.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="civic-card">
                <div style="font-size: 1.15rem; font-weight: 800; color: #5b21b6; margin-bottom: 8px;">
                    ⚙️ Technology Stack
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.82rem; margin-top: 10px;">
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Frontend:</strong><br/>Streamlit, Plotly, Folium
                    </div>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Agentic Framework:</strong><br/>LangGraph StateGraph
                    </div>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Foundational Model:</strong><br/>Gemini 1.5 Pro / Flash
                    </div>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Vector Store:</strong><br/>ChromaDB (Embeddings)
                    </div>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Backend API:</strong><br/>FastAPI & Uvicorn
                    </div>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <strong>Persistence:</strong><br/>SQLAlchemy & MySQL
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="civic-card">
                <div style="font-size: 1.15rem; font-weight: 800; color: #9f1239; margin-bottom: 8px;">
                    ⏱️ Watchdog SLA & Escalation Hierarchy
                </div>
                <p style="font-size: 0.86rem; color: #475569; line-height: 1.5;">
                    Dynamic countdown clocks continuously monitor resolution progress against municipal standards.
                    Breaches trigger automated notifications and escalation to Assistant Municipal Commissioners.
                </p>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
                    <span class="badge badge-resolved">Level 1: Field Officer</span>
                    <span class="badge badge-under-review">Level 2: Ward Officer</span>
                    <span class="badge badge-critical">Level 3: Ward Head</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """Master application controller."""
    # Check URL query parameters for direct links
    query_params = st.query_params
    if "page" in query_params:
        param_page = query_params["page"]
        page_map = {
            "home": PAGE_HOME,
            "citizen": PAGE_CITIZEN,
            "track": PAGE_TRACK,
            "assistant": PAGE_ASSISTANT,
            "officer": PAGE_OFFICER,
            "admin": PAGE_ADMIN,
            "about": PAGE_ABOUT,
        }
        if param_page in page_map:
            st.session_state["current_page"] = page_map[param_page]
    if "id" in query_params:
        st.session_state["tracking_query"] = query_params["id"]

    # Render sidebar navigation
    selected_page = render_sidebar()

    # Route to designated page
    if selected_page == PAGE_HOME:
        render_home_page()
    elif selected_page == PAGE_CITIZEN:
        render_citizen_page()
    elif selected_page == PAGE_TRACK:
        render_track_page()
    elif selected_page == PAGE_ASSISTANT:
        render_assistant_page()
    elif selected_page == PAGE_OFFICER:
        render_officer_page()
    elif selected_page == PAGE_ADMIN:
        render_admin_page()
    elif selected_page == PAGE_ABOUT:
        render_about_page()


if __name__ == "__main__":
    main()