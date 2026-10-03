from typing import TypedDict, Optional


class CivicPulseState(TypedDict, total=False):

    complaint_id: int
    complaint_number: str
    description: str
    policy_answer: str
    policy_sources: list

    category: str
    department: str
    severity: str
    priority: str
    confidence_score: float
    language: str

    ward: str
    assigned_officer: str

    department_id: int
    ward_id: int
    officer_id: int

    duplicate_found: bool
    duplicate_complaint_id: Optional[int]
    duplicate_similarity: float

    policy_answer: str
    policy_sources: list

    sla_deadline: str
    status: str
    work_order_number: str
    notification_sent: bool
    next_action: str
    error: str