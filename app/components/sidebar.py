"""CivicPulse - Sidebar Navigation Component
Renders the municipal portal sidebar, logo, page routing, and backend connection monitor.
"""

import streamlit as st

from app.api_client import api_client
from app.config import (
    CIVICPULSE_API_URL,
    MUNICIPAL_NAME,
    PAGE_ABOUT,
    PAGE_ADMIN,
    PAGE_ASSISTANT,
    PAGE_CITIZEN,
    PAGE_HOME,
    PAGE_OFFICER,
    PAGE_TRACK,
    PAGES,
)


def render_sidebar() -> str:
    """Renders the sidebar navigation and returns selected page name."""
    with st.sidebar:
        # Header / Brand with Gradient Aesthetic
        st.markdown(
            f"""
            <div style="padding: 6px 0 16px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #06b6d4 100%); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);">
                        🏛️
                    </div>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; color: #0f172a;">
                            Civic<span style="color: #2563eb;">Pulse</span>
                        </div>
                        <div style="font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;">
                            Autonomous Municipal Agent
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Page Navigation
        default_index = 0
        if "current_page" in st.session_state and st.session_state["current_page"] in PAGES:
            default_index = PAGES.index(st.session_state["current_page"])

        page_icons = {
            PAGE_HOME: "🏠  Home",
            PAGE_CITIZEN: "📝  Submit Complaint",
            PAGE_TRACK: "🔍  Track Complaint",
            PAGE_ASSISTANT: "🤖  AI Assistant",
            PAGE_OFFICER: "👮  Officer Dashboard",
            PAGE_ADMIN: "📊  Admin Dashboard",
            PAGE_ABOUT: "ℹ️  About"
        }

        selected_page = st.radio(
            "Navigation",
            options=PAGES,
            index=default_index,
            format_func=lambda p: page_icons.get(p, p),
            label_visibility="collapsed"
        )
        st.session_state["current_page"] = selected_page

        st.markdown("<hr style='margin: 18px 0 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

        # Live Backend Connection Monitor with Animated Pulsing LED
        is_healthy, status_text = api_client.health_check()
        if is_healthy:
            st.markdown(
                f"""
                <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 10px 12px; font-size: 0.76rem; color: #065f46; box-shadow: 0 1px 3px rgba(16, 185, 129, 0.1);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                        <span class="live-pulse-dot"></span>
                        <strong style="color: #047857; font-size: 0.78rem;">Backend API: Online</strong>
                    </div>
                    <div style="font-size: 0.7rem; color: #059669; padding-left: 16px;">
                        <code>{CIVICPULSE_API_URL}</code>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 10px 12px; font-size: 0.76rem; color: #9f1239;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                        <span style="height: 8px; width: 8px; background: #e11d48; border-radius: 50%; display: inline-block;"></span>
                        <strong style="font-size: 0.78rem;">Backend API: Disconnected</strong>
                    </div>
                    <div style="font-size: 0.7rem; line-height: 1.35; color: #881337; padding-left: 14px;">
                        Start server:<br/><code>uvicorn api.main:app --reload</code>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Municipal Jurisdiction Info & Academic Demo Badge
        st.markdown(
            f"""
            <div style="margin-top: 16px; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.72rem; color: #64748b; line-height: 1.45; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);">
                <div style="color: #0f172a; font-weight: 700; margin-bottom: 4px; font-size: 0.75rem;">
                    🏛️ {MUNICIPAL_NAME}
                </div>
                <div><strong>Architecture:</strong> LangGraph + Gemini + ChromaDB</div>
                <div><strong>Stack:</strong> FastAPI + Streamlit</div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #cbd5e1; color: #2563eb; font-weight: 600;">
                    🎓 SCIT MBA-DSDA Project Demo
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        return selected_page
