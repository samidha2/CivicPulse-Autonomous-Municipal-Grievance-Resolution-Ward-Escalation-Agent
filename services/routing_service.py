from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database.models import (
    Complaint,
    Department,
    Ward,
    Officer,
    SLARule
)


# ---------------------------------------------------------
# CATEGORY → DEPARTMENT MAPPING
# ---------------------------------------------------------

CATEGORY_DEPARTMENT_MAP = {

    "Pothole": "Roads & Infrastructure",
    "Road Damage": "Roads & Infrastructure",
    "Broken Footpath": "Roads & Infrastructure",
    "Damaged Road Sign": "Roads & Infrastructure",

    "Water Leakage": "Water Supply",
    "No Water Supply": "Water Supply",

    "Garbage Not Collected": "Solid Waste Management",
    "Overflowing Garbage Bin": "Solid Waste Management",
    "Illegal Dumping": "Solid Waste Management",

    "Streetlight Not Working": "Street Lighting",

    "Drainage Blockage": "Drainage & Sewerage",
    "Sewage Overflow": "Drainage & Sewerage",

    "Public Health": "Public Health",

    "Public Safety": "Traffic & Public Safety",

    "Park Maintenance": "Parks & Public Spaces"
}


def route_complaint(
    complaint_id: int,
    db: Session
):

    # -----------------------------------------------------
    # 1. Get complaint
    # -----------------------------------------------------

    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:
        raise ValueError("Complaint not found")

    if not complaint.category:
        raise ValueError(
            "Complaint has not been classified yet"
        )

    # -----------------------------------------------------
    # 2. Determine department
    # -----------------------------------------------------

    department_name = CATEGORY_DEPARTMENT_MAP.get(
        complaint.category
    )

    if not department_name:
        raise ValueError(
            f"No department mapping found for category: "
            f"{complaint.category}"
        )

    department = (
        db.query(Department)
        .filter(
            Department.name == department_name
        )
        .first()
    )

    if not department:
        raise ValueError(
            f"Department not found: {department_name}"
        )

    # -----------------------------------------------------
    # 3. Determine ward
    # -----------------------------------------------------

    ward = None

    if (
        complaint.latitude is not None
        and complaint.longitude is not None
    ):

        # -------------------------------------------------
        # DEMO LOGIC
        # -------------------------------------------------
        # For now we assign a deterministic ward using
        # the complaint location.
        #
        # Later we will replace this with actual GIS
        # point-in-polygon ward detection.
        # -------------------------------------------------

        ward_number = (
            int(abs(complaint.latitude * 1000))
            % 20
        ) + 1

        ward = (
            db.query(Ward)
            .filter(
                Ward.ward_number == ward_number
            )
            .first()
        )

    # If location is unavailable,
    # use a fallback ward.

    if not ward:

        ward = (
            db.query(Ward)
            .order_by(Ward.id)
            .first()
        )

    if not ward:
        raise ValueError("No wards available")

    # -----------------------------------------------------
    # 4. Find active officer
    # -----------------------------------------------------

    # --------------------------------------------------
    # Find officer for department + ward
    # --------------------------------------------------

    officer = (
        db.query(Officer)
        .filter(
            Officer.department_id == department.id,
            Officer.ward_id == ward.id,
            Officer.is_active == True
        )
        .first()
    )

    # --------------------------------------------------
    # Fallback:
    # If no officer exists in the selected ward,
    # find an active officer from the same department.
    # --------------------------------------------------

    if not officer:

        officer = (
            db.query(Officer)
            .filter(
                Officer.department_id == department.id,
                Officer.is_active == True
            )
            .order_by(Officer.id)
            .first()
        )

    # -----------------------------------------------------
    # 5. SLA calculation
    # -----------------------------------------------------

    sla_rule = (
        db.query(SLARule)
        .filter(
            SLARule.category == complaint.category
        )
        .first()
    )

    if not sla_rule:

        raise ValueError(
            f"SLA rule not found for category: "
            f"{complaint.category}"
        )

    created_time = (
        complaint.created_at
        or datetime.utcnow()
    )

    sla_deadline = (
        created_time
        + timedelta(
            hours=sla_rule.resolution_hours
        )
    )

    # -----------------------------------------------------
    # 6. Update complaint
    # -----------------------------------------------------

    complaint.department_id = department.id
    complaint.ward_id = ward.id
    complaint.sla_deadline = sla_deadline

    if officer:

        complaint.assigned_officer_id = officer.id
        complaint.status = "ASSIGNED"

    else:

        complaint.status = "UNDER_REVIEW"

    db.commit()
    db.refresh(complaint)

    # -----------------------------------------------------
    # 7. Return routing result
    # -----------------------------------------------------

    return {
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_number,

        "category": complaint.category,

        "department": department.name,
        "department_id": department.id,

        "ward": ward.name,
        "ward_number": ward.ward_number,
        "ward_id": ward.id,

        "officer": (
            officer.name
            if officer
            else None
        ),

        "officer_id": (
            officer.id
            if officer
            else None
        ),

        "sla_hours": sla_rule.resolution_hours,

        "sla_deadline": sla_deadline,

        "status": complaint.status
    }