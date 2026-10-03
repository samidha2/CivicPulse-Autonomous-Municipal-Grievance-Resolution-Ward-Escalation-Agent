"""CivicPulse - Admin Executive Analytics & GIS Map Dashboard
Citywide executive reporting, Plotly analytics, and Folium geospatial mapping.
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from app.api_client import api_client
from app.components.cards import hero_header, metric_card
from app.components.charts import (
    plot_category_distribution,
    plot_department_distribution,
    plot_severity_distribution,
    plot_status_distribution,
    plot_ward_distribution,
    render_folium_complaint_map,
)


def render_admin_page():
    """Renders the executive municipal analytics and GIS hotspot dashboard."""
    hero_header(
        title="Municipal Executive Analytics & GIS Map",
        subtitle="Citywide operational intelligence, SLA compliance metrics, ward density, and geospatial hotspot clustering.",
        tag="MUNICIPAL COMMISSIONER SUITE"
    )

    # 1. Fetch live metrics & complaint dataset
    with st.spinner("Compiling citywide grievance intelligence..."):
        summary, sum_err = api_client.get_analytics_summary()
        complaints_res, comp_err = api_client.list_complaints(limit=500)

    complaints_list = complaints_res.get("complaints", []) if complaints_res else []
    df = pd.DataFrame(complaints_list) if complaints_list else pd.DataFrame()

    # -------------------------------------------------------------------------
    # Top KPI Metrics Cards
    # -------------------------------------------------------------------------
    if summary:
        total = summary.get("total", 0)
        open_c = summary.get("open", 0)
        resolved_c = summary.get("resolved", 0)
        escalated_c = summary.get("escalated", 0)
        at_risk_c = summary.get("at_risk", 0)
        overdue_c = summary.get("overdue", 0)
        critical_c = summary.get("critical", 0)
        duplicates = summary.get("duplicates", 0)

        sla_risk_total = at_risk_c + overdue_c + critical_c

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            metric_card("Total Complaints", total,  accent="#0284c7")
        with c2:
            metric_card("Open Complaints", open_c,  accent="#f59e0b")
        with c3:
            metric_card("Resolved", resolved_c,  accent="#10b981")
        with c4:
            metric_card("Escalated", escalated_c, accent="#e11d48")
        with c5:
            metric_card("SLA Risk / Overdue", sla_risk_total, f"At risk: {at_risk_c}, Overdue: {overdue_c + critical_c}", accent="#dc2626")
        with c6:
            dup_rate = f"{(duplicates / total * 100):.1f}%" if total > 0 else "0%"
            metric_card("Duplicate Rate", f"{duplicates} ({dup_rate})", accent="#8b5cf6")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Plotly Analytics Visualizations
    # -------------------------------------------------------------------------
    st.subheader("📈 Citywide Grievance Analytics")

    if not df.empty:
        # Row 1: Department & Category
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            fig_dept = plot_department_distribution(df)
            st.plotly_chart(fig_dept, use_container_width=True)
        with r1_c2:
            fig_cat = plot_category_distribution(df)
            st.plotly_chart(fig_cat, use_container_width=True)

        # Row 2: Severity & Ward Distribution
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            fig_sev = plot_severity_distribution(df)
            st.plotly_chart(fig_sev, use_container_width=True)
        with r2_c2:
            fig_ward = plot_ward_distribution(df)
            st.plotly_chart(fig_ward, use_container_width=True)

        # Row 3: Status Pipeline
        st.markdown("##### 🔄 Lifecycle Status Distribution")
        fig_stat = plot_status_distribution(df)
        st.plotly_chart(fig_stat, use_container_width=True)

    else:
        st.info("ℹ️ Insufficient complaint data available to render charts.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Folium GIS Geospatial Hotspot Map
    # -------------------------------------------------------------------------
    st.subheader("🗺️ Geospatial Grievance Hotspot Map")
    st.caption("Real-time geographic distribution of citizen complaints across municipal zones.")

    if complaints_list:
        # Filter map by priority or status
        m_f1, m_f2 = st.columns([6, 6])
        with m_f1:
            map_priority = st.selectbox("Map Priority Filter", options=["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"], key="map_p")
        with m_f2:
            map_status = st.selectbox("Map Status Filter", options=["ALL", "ACTIVE (Open)", "RESOLVED"], key="map_s")

        filtered_map_data = complaints_list
        if map_priority != "ALL":
            filtered_map_data = [c for c in filtered_map_data if (c.get("priority") or "").upper() == map_priority]
        if map_status == "ACTIVE (Open)":
            filtered_map_data = [c for c in filtered_map_data if c.get("status") not in ("RESOLVED", "CITIZEN_CONFIRMED", "CLOSED")]
        elif map_status == "RESOLVED":
            filtered_map_data = [c for c in filtered_map_data if c.get("status") in ("RESOLVED", "CITIZEN_CONFIRMED", "CLOSED")]

        render_folium_complaint_map(filtered_map_data, height=520)
    else:
        st.warning("⚠️ No geolocation data available to generate map.")
