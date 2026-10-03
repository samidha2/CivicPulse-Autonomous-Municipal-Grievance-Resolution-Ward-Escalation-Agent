"""CivicPulse - Card & Badge UI Components
Reusable presentation widgets for metrics, badges, headers, and callouts.
"""

from typing import Optional, Union
import streamlit as st

from app.config import PRIORITY_COLORS, SLA_COLORS, STATUS_COLORS


def hero_header(title: str, subtitle: str, tag: str = "PUNE MUNICIPAL CORPORATION"):
    """Renders a sleek municipal-tech hero banner with gradient accents."""
    title_html = title
    if "CivicPulse" in title:
        title_html = title.replace("CivicPulse", 'Civic<span class="gradient-text">Pulse</span>')

    st.markdown(
        f"""
        <div class="civic-hero">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span class="hero-tag">
                    🏛️ {tag}
                </span>
                <span style="font-size: 0.78rem; font-weight: 600; color: #7dd3fc; letter-spacing: 0.04em;">
                    ⚡ AI-Autonomous Grievance Mesh
                </span>
            </div>
            <h1>{title_html}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(
    label: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,

    accent: str = "#2563eb",
    icon: Optional[str] = None
):
    """Renders an executive KPI metric card with an accent top bar and optional icon."""
    delta_html = f'<div style="font-size: 0.75rem; color: #10b981; font-weight: 700; margin-top: 4px;">▲ {delta}</div>' if delta else ""
   
    icon_html = f'<div class="metric-icon-badge">{icon}</div>' if icon else ""

    st.markdown(
        f"""
        <div class="civic-metric" style="border-top-color: {accent};">
            <div class="metric-header">
                <div class="metric-label">{label}</div>
                {icon_html}
            </div>
            <div class="metric-val">{value}</div>
            {delta_html}

        </div>
        """,
        unsafe_allow_html=True
    )


def get_status_badge_html(status: Optional[str]) -> str:
    """Returns HTML for a status badge with semantic theme styling."""
    if not status:
        return '<span class="badge badge-submitted">UNKNOWN</span>'
    st_upper = status.upper().strip()
    color = STATUS_COLORS.get(st_upper, "#64748B")

    # Map CSS class for preset background
    class_map = {
        "SUBMITTED": "badge-submitted",
        "UNDER_REVIEW": "badge-under-review",
        "ASSIGNED": "badge-assigned",
        "IN_PROGRESS": "badge-in-progress",
        "RESOLVED": "badge-resolved",
        "CITIZEN_CONFIRMED": "badge-confirmed",
        "CITIZEN_REJECTED": "badge-rejected",
        "ESCALATED": "badge-escalated",
        "CLOSED": "badge-submitted"
    }
    css_class = class_map.get(st_upper, "badge-submitted")

    return f'<span class="badge {css_class}"><span style="display:inline-block; width:6px; height:6px; border-radius:50%; background-color:{color};"></span> {st_upper.replace("_", " ")}</span>'


def get_priority_badge_html(priority: Optional[str]) -> str:
    """Returns HTML for a priority badge."""
    if not priority:
        return '<span class="badge badge-medium">MEDIUM</span>'
    p_upper = priority.upper().strip()

    class_map = {
        "CRITICAL": "badge-critical",
        "HIGH": "badge-high",
        "MEDIUM": "badge-medium",
        "LOW": "badge-low"
    }
    css_class = class_map.get(p_upper, "badge-medium")
    color = PRIORITY_COLORS.get(p_upper, "#F59E0B")

    return f'<span class="badge {css_class}"><span style="display:inline-block; width:6px; height:6px; border-radius:50%; background-color:{color};"></span> {p_upper}</span>'


def get_sla_badge_html(sla_status: Optional[str]) -> str:
    """Returns HTML for an SLA status badge."""
    if not sla_status:
        return '<span class="badge badge-submitted">⏱️ UNKNOWN</span>'
    sla_upper = sla_status.upper().strip()
    color = SLA_COLORS.get(sla_upper, "#64748B")

    class_map = {
        "ON_TRACK": "badge-resolved",
        "AT_RISK": "badge-under-review",
        "OVERDUE": "badge-high",
        "CRITICAL": "badge-critical",
        "RESOLVED": "badge-confirmed"
    }
    css_class = class_map.get(sla_upper, "badge-submitted")

    return f'<span class="badge {css_class}">⏱️ {sla_upper.replace("_", " ")}</span>'


def policy_notice_card():
    """Renders mandatory synthetic policy notice disclaimer."""
    st.markdown(
        """
        <div class="policy-banner">
            <div style="font-weight: 700; display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                🏛️ CivicPulse Demo / Synthetic Policy Knowledge Base
            </div>
            <div style="font-size: 0.82rem; opacity: 0.9; line-height: 1.45;">
                All retrieved SLAs, escalation matrix trees, and civic bylaws are grounded in Pune Municipal Corporation Citizen Charters for testing and demonstration purposes.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
