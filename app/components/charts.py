"""CivicPulse - Chart & GIS Map Visualizations
Plotly charting and Folium spatial GIS mapping components.
"""

from typing import Any, Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import MarkerCluster

from app.config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    PRIORITY_COLORS,
    STATUS_COLORS,
)

# Plotly theme layout adjustments for seamless embedding
PLOTLY_TEMPLATE = "plotly_white"
CHART_HEIGHT = 340
FONT_FAMILY = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif"


def plot_department_distribution(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing complaint volume per department."""
    if df.empty or "department_name" not in df.columns:
        return go.Figure()

    dept_counts = (
        df["department_name"]
        .fillna("Unassigned")
        .value_counts()
        .reset_index()
    )
    dept_counts.columns = ["department", "count"]
    dept_counts = dept_counts.sort_values(by="count", ascending=True)

    fig = px.bar(
        dept_counts,
        x="count",
        y="department",
        orientation="h",
        text="count",
        title="Complaints by Department",
        color="count",
        color_continuous_scale="Blues",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        font_family=FONT_FAMILY,
        title_font_size=15,
        title_font_color="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Complaint Count",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(
        textposition="outside",
        marker=dict(line=dict(width=1, color="rgba(37, 99, 235, 0.4)"))
    )
    return fig


def plot_category_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing grievances grouped by category."""
    if df.empty or "category" not in df.columns:
        return go.Figure()

    cat_counts = (
        df["category"]
        .fillna("General Grievance")
        .value_counts()
        .reset_index()
    )
    cat_counts.columns = ["category", "count"]

    fig = px.pie(
        cat_counts,
        names="category",
        values="count",
        hole=0.48,
        title="Grievance Categories",
        color_discrete_sequence=px.colors.qualitative.Prism,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        font_family=FONT_FAMILY,
        title_font_size=15,
        title_font_color="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#ffffff", width=2))
    )
    return fig


def plot_severity_distribution(df: pd.DataFrame) -> go.Figure:
    """Pie/Bar chart of complaints partitioned by severity."""
    if df.empty or "severity" not in df.columns:
        return go.Figure()

    sev_counts = df["severity"].fillna("MEDIUM").str.upper().value_counts().reset_index()
    sev_counts.columns = ["severity", "count"]

    # Map colors
    color_map = {k: PRIORITY_COLORS.get(k, "#64748B") for k in sev_counts["severity"]}

    fig = px.bar(
        sev_counts,
        x="severity",
        y="count",
        color="severity",
        color_discrete_map=color_map,
        text="count",
        title="Severity Level Distribution",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        font_family=FONT_FAMILY,
        title_font_size=15,
        title_font_color="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="",
        yaxis_title="Count",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(
        textposition="outside",
        marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1))
    )
    return fig


def plot_ward_distribution(df: pd.DataFrame) -> go.Figure:
    """Bar chart showing complaint volume per municipal ward."""
    if df.empty or "ward_name" not in df.columns:
        return go.Figure()

    ward_counts = (
        df["ward_name"]
        .fillna("Unassigned Ward")
        .value_counts()
        .reset_index()
    )
    ward_counts.columns = ["ward", "count"]
    ward_counts = ward_counts.sort_values(by="count", ascending=False).head(10)

    fig = px.bar(
        ward_counts,
        x="ward",
        y="count",
        text="count",
        title="Top Wards by Volume",
        color="count",
        color_continuous_scale="Teal",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        font_family=FONT_FAMILY,
        title_font_size=15,
        title_font_color="#0F172A",
        margin=dict(l=20, r=20, t=40, b=40),
        xaxis_title="",
        yaxis_title="Complaints",
        coloraxis_showscale=False,
        xaxis_tickangle=-25,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(
        textposition="outside",
        marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1))
    )
    return fig


def plot_status_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart for complaint status distribution."""
    if df.empty or "status" not in df.columns:
        return go.Figure()

    stat_counts = df["status"].fillna("SUBMITTED").str.upper().value_counts().reset_index()
    stat_counts.columns = ["status", "count"]

    color_map = {k: STATUS_COLORS.get(k, "#64748B") for k in stat_counts["status"]}

    fig = px.pie(
        stat_counts,
        names="status",
        values="count",
        hole=0.48,
        title="Status Pipeline Breakdown",
        color="status",
        color_discrete_map=color_map,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        font_family=FONT_FAMILY,
        title_font_size=15,
        title_font_color="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#ffffff", width=2))
    )
    return fig


def render_folium_complaint_map(complaints: List[Dict[str, Any]], height: int = 520):
    """Generates an interactive Folium GIS map showing complaint geolocations."""
    m = folium.Map(
        location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    marker_cluster = MarkerCluster(name="Municipal Grievances").add_to(m)

    valid_points = 0
    for c in complaints:
        lat = c.get("latitude")
        lon = c.get("longitude")
        if lat is None or lon is None:
            continue

        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            continue

        valid_points += 1
        num = c.get("complaint_number", f"ID: {c.get('id')}")
        cat = c.get("category", "General")
        status = c.get("status", "SUBMITTED")
        priority = (c.get("priority") or "MEDIUM").upper()
        ward = c.get("ward_name") or f"Ward #{c.get('ward_number', 'N/A')}"
        dept = c.get("department_name") or "Unassigned"
        desc = (c.get("description") or "")[:120]

        # Select color based on priority
        color = "blue"
        if priority == "CRITICAL" or status == "ESCALATED":
            color = "red"
        elif priority == "HIGH":
            color = "orange"
        elif status in ("RESOLVED", "CITIZEN_CONFIRMED", "CLOSED"):
            color = "green"
        elif priority == "LOW":
            color = "lightblue"

        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px; width: 230px; line-height: 1.4;">
            <div style="font-weight: 800; font-size: 13px; color: #0f172a; margin-bottom: 6px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px;">
                🏛️ {num}
            </div>
            <div style="margin-bottom: 3px;"><strong>Category:</strong> <span style="color:#2563eb;">{cat}</span></div>
            <div style="margin-bottom: 3px;"><strong>Status:</strong> {status}</div>
            <div style="margin-bottom: 3px;"><strong>Priority:</strong> {priority}</div>
            <div style="margin-bottom: 3px;"><strong>Department:</strong> {dept}</div>
            <div style="margin-bottom: 3px;"><strong>Ward:</strong> {ward}</div>
            <p style="margin-top: 6px; font-style: italic; color: #64748b; font-size: 11px; background: #f8fafc; padding: 4px; border-radius: 4px;">
                "{desc}..."
            </p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=270),
            tooltip=f"{num}: {cat} ({priority})",
            icon=folium.Icon(color=color, icon="info-sign", prefix="glyphicon"),
        ).add_to(marker_cluster)

    # Render via streamlit_folium or fallback to components.html
    try:
        from streamlit_folium import st_folium
        st_folium(m, width=None, height=height, returned_objects=[])
    except Exception:
        map_html = m._repr_html_()
        components.html(map_html, height=height + 20)

    if valid_points == 0:
        st.caption("ℹ️ No complaints with geographic coordinates (Latitude/Longitude) found.")
    else:
        st.caption(f"📍 Displaying **{valid_points}** geo-located municipal grievances across Pune municipal zones.")
