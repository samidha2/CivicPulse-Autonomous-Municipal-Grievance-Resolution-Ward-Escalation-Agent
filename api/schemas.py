from pydantic import BaseModel
from typing import Optional


class ComplaintCreate(BaseModel):
    citizen_id: int
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ComplaintResponse(BaseModel):
    id: int
    complaint_number: str
    citizen_id: int
    description: str
    category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None
    ward_id: Optional[int] = None
    department_id: Optional[int] = None
    assigned_officer_id: Optional[int] = None

    class Config:
        from_attributes = True