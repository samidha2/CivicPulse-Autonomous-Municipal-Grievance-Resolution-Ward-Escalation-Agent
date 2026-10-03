from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


# ============================================================
# 1. DEPARTMENT
# ============================================================

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    officers = relationship("Officer", back_populates="department")
    complaints = relationship("Complaint", back_populates="department")


# ============================================================
# 2. WARD
# ============================================================

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ward_number = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    zone = Column(String(100))

    officers = relationship("Officer", back_populates="ward")
    complaints = relationship("Complaint", back_populates="ward")


# ============================================================
# 3. OFFICER
# ============================================================

class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))

    designation = Column(String(100))

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False
    )

    ward_id = Column(
        Integer,
        ForeignKey("wards.id"),
        nullable=False
    )

    is_active = Column(Boolean, default=True)

    department = relationship(
        "Department",
        back_populates="officers"
    )

    ward = relationship(
        "Ward",
        back_populates="officers"
    )

    complaints = relationship(
        "Complaint",
        back_populates="assigned_officer"
    )


# ============================================================
# 4. CITIZEN
# ============================================================

class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))

    preferred_language = Column(
        String(20),
        default="English"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    complaints = relationship(
        "Complaint",
        back_populates="citizen"
    )


# ============================================================
# 5. COMPLAINT
# ============================================================

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_number = Column(
        String(30),
        unique=True,
        nullable=False
    )

    citizen_id = Column(
        Integer,
        ForeignKey("citizens.id"),
        nullable=False
    )

    description = Column(Text, nullable=False)

    category = Column(String(100))
    department_id = Column(
        Integer,
        ForeignKey("departments.id")
    )

    ward_id = Column(
        Integer,
        ForeignKey("wards.id")
    )

    latitude = Column(Float)
    longitude = Column(Float)

    severity = Column(String(20))
    priority = Column(String(20))

    status = Column(
        String(40),
        default="SUBMITTED"
    )

    confidence_score = Column(Float)

    assigned_officer_id = Column(
        Integer,
        ForeignKey("officers.id")
    )

    duplicate_of = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=True
    )

    sla_deadline = Column(DateTime)

    resolution = Column(Text)

    resolution_time = Column(DateTime)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships

    citizen = relationship(
        "Citizen",
        back_populates="complaints"
    )

    department = relationship(
        "Department",
        back_populates="complaints"
    )

    ward = relationship(
        "Ward",
        back_populates="complaints"
    )

    assigned_officer = relationship(
        "Officer",
        back_populates="complaints"
    )

    history = relationship(
        "ComplaintHistory",
        back_populates="complaint",
        cascade="all, delete-orphan"
    )

    work_orders = relationship(
        "WorkOrder",
        back_populates="complaint"
    )

    escalations = relationship(
        "Escalation",
        back_populates="complaint"
    )

    notifications = relationship(
        "Notification",
        back_populates="complaint"
    )

    feedback = relationship(
        "Feedback",
        back_populates="complaint"
    )


# ============================================================
# 6. SLA RULE
# ============================================================

class SLARule(Base):
    __tablename__ = "sla_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    category = Column(
        String(100),
        unique=True,
        nullable=False
    )

    severity = Column(String(20))

    resolution_hours = Column(Integer, nullable=False)

    description = Column(Text)


# ============================================================
# 7. WORK ORDER
# ============================================================

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False
    )

    work_order_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("officers.id")
    )

    status = Column(
        String(40),
        default="CREATED"
    )

    description = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(DateTime)

    complaint = relationship(
        "Complaint",
        back_populates="work_orders"
    )


# ============================================================
# 8. COMPLAINT HISTORY / AUDIT LOG
# ============================================================

class ComplaintHistory(Base):
    __tablename__ = "complaint_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False
    )

    action = Column(String(100), nullable=False)

    performed_by = Column(String(100))

    previous_status = Column(String(40))
    new_status = Column(String(40))

    remarks = Column(Text)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    complaint = relationship(
        "Complaint",
        back_populates="history"
    )


# ============================================================
# 9. ESCALATION
# ============================================================

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False
    )

    escalation_level = Column(Integer, nullable=False)

    reason = Column(Text)

    escalated_to = Column(String(150))

    status = Column(
        String(40),
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    resolved_at = Column(DateTime)

    complaint = relationship(
        "Complaint",
        back_populates="escalations"
    )


# ============================================================
# 10. NOTIFICATION
# ============================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id")
    )

    recipient = Column(String(150))

    notification_type = Column(String(50))

    message = Column(Text)

    status = Column(
        String(30),
        default="PENDING"
    )

    sent_at = Column(DateTime)

    complaint = relationship(
        "Complaint",
        back_populates="notifications"
    )


# ============================================================
# 11. FEEDBACK
# ============================================================

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False
    )

    rating = Column(Integer)

    comments = Column(Text)

    resolution_accepted = Column(Boolean)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    complaint = relationship(
        "Complaint",
        back_populates="feedback"
    )