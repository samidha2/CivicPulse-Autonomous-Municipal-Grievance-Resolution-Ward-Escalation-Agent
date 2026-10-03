"""CivicPulse - Configuration and Constants
Frontend configuration module for the Streamlit dashboard.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Backend API Configuration
CIVICPULSE_API_URL = os.getenv("CIVICPULSE_API_URL", "http://127.0.0.1:8000").rstrip("/")
API_TIMEOUT_SECONDS = int(os.getenv("CIVICPULSE_API_TIMEOUT", "120"))

# Navigation Pages
PAGE_HOME = "Home"
PAGE_CITIZEN = "Submit Complaint"
PAGE_TRACK = "Track Complaint"
PAGE_ASSISTANT = "AI Assistant"
PAGE_OFFICER = "Officer Dashboard"
PAGE_ADMIN = "Admin Dashboard"
PAGE_ABOUT = "About"

PAGES = [
    PAGE_HOME,
    PAGE_CITIZEN,
    PAGE_TRACK,
    PAGE_ASSISTANT,
    PAGE_OFFICER,
    PAGE_ADMIN,
    PAGE_ABOUT,
]

# Municipal Presets (Pune Municipal Corporation Area)
MUNICIPAL_NAME = "Pune Municipal Corporation"
DEFAULT_LATITUDE = 18.5204
DEFAULT_LONGITUDE = 73.8567

WARD_PRESETS = [
    {"label": "Ward 1 - Central Ward (Budhwar Peth / Kasba)", "lat": 18.5204, "lon": 73.8567},
    {"label": "Ward 2 - Shivajinagar / Model Colony", "lat": 18.5314, "lon": 73.8446},
    {"label": "Ward 3 - Kothrud / Paud Road", "lat": 18.5074, "lon": 73.8077},
    {"label": "Ward 4 - Hadapsar / Magarpatta", "lat": 18.5089, "lon": 73.9260},
    {"label": "Ward 5 - Viman Nagar / Kalyani Nagar", "lat": 18.5679, "lon": 73.9143},
    {"label": "Ward 6 - Aundh / Baner", "lat": 18.5602, "lon": 73.8031},
    {"label": "Ward 7 - Bibvewadi / Dhankawadi", "lat": 18.4719, "lon": 73.8643},
    {"label": "Ward 8 - Yerwada / Nagar Road", "lat": 18.5529, "lon": 73.8797},
]

# Status Palette
STATUS_COLORS = {
    "SUBMITTED": "#64748B",          # Slate
    "UNDER_REVIEW": "#F59E0B",       # Amber
    "ASSIGNED": "#0284C7",           # Sky
    "IN_PROGRESS": "#3B82F6",        # Blue
    "RESOLVED": "#10B981",           # Emerald
    "CITIZEN_CONFIRMED": "#059669",  # Deep Green
    "CITIZEN_REJECTED": "#DC2626",   # Red
    "CLOSED": "#475569",             # Slate dark
    "ESCALATED": "#E11D48",          # Rose/Crimson
    "REOPENED": "#D97706",           # Amber dark
    "PENDING_INFORMATION": "#8B5CF6" # Violet
}

# Priority Palette
PRIORITY_COLORS = {
    "LOW": "#10B981",       # Emerald
    "MEDIUM": "#F59E0B",    # Amber
    "HIGH": "#EA580C",      # Orange
    "CRITICAL": "#E11D48",  # Rose/Crimson
}

# SLA Status Palette
SLA_COLORS = {
    "ON_TRACK": "#10B981",  # Emerald
    "AT_RISK": "#F59E0B",   # Amber
    "OVERDUE": "#EA580C",   # Orange
    "CRITICAL": "#E11D48",  # Rose
    "RESOLVED": "#059669",  # Dark Emerald
    "UNKNOWN": "#64748B",   # Slate
}

# Sample Prompts for Policy RAG Assistant
SAMPLE_POLICY_PROMPTS = [
    "What is the maximum SLA deadline for resolving a drinking water contamination complaint?",
    "What are the escalation steps if a high-severity road pothole is not resolved within 48 hours?",
    "How does CivicPulse detect duplicate complaints submitted by multiple citizens?",
    "Which department handles fallen tree branches obstructing traffic during monsoon?",
    "What is the citizen confirmation process once an officer marks a complaint resolved?",
]
