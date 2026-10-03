from database.database import engine, Base

# Import all models so SQLAlchemy knows about them
from database.models import (
    Department,
    Ward,
    Officer,
    Citizen,
    Complaint,
    SLARule,
    WorkOrder,
    ComplaintHistory,
    Escalation,
    Notification,
    Feedback
)


print("Creating CivicPulse database tables...")

Base.metadata.create_all(bind=engine)

print("✅ All CivicPulse tables created successfully!")