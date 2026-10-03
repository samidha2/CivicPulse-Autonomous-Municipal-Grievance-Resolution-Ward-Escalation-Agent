
from database.database import SessionLocal
from database.models import (
    Department,
    Ward,
    Officer,
    SLARule,
    Citizen,
    Complaint
)
from datetime import datetime, timedelta

def seed_departments():
    db = SessionLocal()

    departments = [
        {
            "name": "Roads & Infrastructure",
            "description": "Roads, potholes, footpaths, road signs and public infrastructure"
        },
        {
            "name": "Water Supply",
            "description": "Water supply, leakage, pressure and pipeline-related complaints"
        },
        {
            "name": "Solid Waste Management",
            "description": "Garbage collection, waste disposal and overflowing bins"
        },
        {
            "name": "Street Lighting",
            "description": "Streetlights, lighting poles and dark public areas"
        },
        {
            "name": "Drainage & Sewerage",
            "description": "Drainage blockage, sewage overflow and sewer infrastructure"
        },
        {
            "name": "Public Health",
            "description": "Public sanitation, hygiene and health-related civic complaints"
        },
        {
            "name": "Parks & Public Spaces",
            "description": "Parks, playgrounds and maintenance of public spaces"
        },
        {
            "name": "Traffic & Public Safety",
            "description": "Traffic-related civic issues and public safety complaints"
        }
    ]

    for data in departments:

        existing = (
            db.query(Department)
            .filter(Department.name == data["name"])
            .first()
        )

        if not existing:
            department = Department(**data)
            db.add(department)

    db.commit()
    db.close()

    print("✅ Departments seeded successfully!")


from database.models import Ward


def seed_wards():
    db = SessionLocal()

    wards = [
        {"ward_number": 1, "name": "Central Ward", "zone": "Central"},
        {"ward_number": 2, "name": "Market Ward", "zone": "Central"},
        {"ward_number": 3, "name": "Station Ward", "zone": "Central"},
        {"ward_number": 4, "name": "Lake View Ward", "zone": "Central"},

        {"ward_number": 5, "name": "North Heights", "zone": "North"},
        {"ward_number": 6, "name": "Green Park Ward", "zone": "North"},
        {"ward_number": 7, "name": "University Ward", "zone": "North"},
        {"ward_number": 8, "name": "Airport Ward", "zone": "North"},

        {"ward_number": 9, "name": "Industrial Ward", "zone": "East"},
        {"ward_number": 10, "name": "Riverfront Ward", "zone": "East"},
        {"ward_number": 11, "name": "Tech Park Ward", "zone": "East"},
        {"ward_number": 12, "name": "Garden Ward", "zone": "East"},

        {"ward_number": 13, "name": "West End Ward", "zone": "West"},
        {"ward_number": 14, "name": "Hill View Ward", "zone": "West"},
        {"ward_number": 15, "name": "Sunrise Ward", "zone": "West"},
        {"ward_number": 16, "name": "Heritage Ward", "zone": "West"},

        {"ward_number": 17, "name": "South City Ward", "zone": "South"},
        {"ward_number": 18, "name": "Residential Ward", "zone": "South"},
        {"ward_number": 19, "name": "Riverside Ward", "zone": "South"},
        {"ward_number": 20, "name": "New Development Ward", "zone": "South"},
    ]

    for data in wards:

        existing = (
            db.query(Ward)
            .filter(Ward.ward_number == data["ward_number"])
            .first()
        )

        if not existing:
            ward = Ward(**data)
            db.add(ward)

    db.commit()
    db.close()

    print("✅ 20 wards seeded successfully!")

def seed_officers():
    db = SessionLocal()

    departments = db.query(Department).all()
    wards = db.query(Ward).order_by(Ward.ward_number).all()

    if not departments:
        print("❌ Departments not found. Run department seeding first.")
        db.close()
        return

    if not wards:
        print("❌ Wards not found. Run ward seeding first.")
        db.close()
        return

    department_map = {
        "Roads & Infrastructure": 0,
        "Water Supply": 1,
        "Solid Waste Management": 2,
        "Street Lighting": 3,
        "Drainage & Sewerage": 4,
        "Public Health": 5,
        "Parks & Public Spaces": 6,
        "Traffic & Public Safety": 7
    }

    officer_names = [
        "Aarav Sharma",
        "Vivaan Patel",
        "Aditya Kulkarni",
        "Arjun Mehta",
        "Rohan Deshmukh",
        "Kunal Shah",
        "Rahul Joshi",
        "Siddharth Nair",
        "Akash Verma",
        "Neeraj Patil",
        "Yash Malhotra",
        "Sahil Kapoor",
        "Amit Chavan",
        "Pranav Rao",
        "Manish Gupta",
        "Nikhil More",
        "Abhishek Singh",
        "Varun Iyer",
        "Raj Malhotra",
        "Aniket Pawar",
        "Harsh Vora",
        "Omkar Jadhav",
        "Tushar Bhosale",
        "Saurabh Mishra",
        "Vikas Tiwari",
        "Ritesh Yadav",
        "Mohit Agarwal",
        "Rohit Sane",
        "Tejas Shinde",
        "Vivek Menon",
        "Dev Joshi",
        "Ishaan Shah",
        "Manav Desai",
        "Parth Kulkarni",
        "Atharva Patil",
        "Sameer Khan",
        "Nitin Sawant",
        "Gaurav Jain",
        "Dhruv Mehta",
        "Kabir Rao"
    ]

    designations = [
        "Field Officer",
        "Ward Operations Officer",
        "Civic Services Officer",
        "Municipal Field Inspector"
    ]

    for i, ward in enumerate(wards):

        # Two officers per ward
        for officer_position in range(2):

            officer_index = i * 2 + officer_position
            name = officer_names[officer_index]

            # Rotate departments across officers
            department_name = list(department_map.keys())[
                officer_index % len(department_map)
            ]

            department = db.query(Department).filter(
                Department.name == department_name
            ).first()

            email = f"officer{officer_index + 1:03d}@civicpulse.demo"

            existing = db.query(Officer).filter(
                Officer.email == email
            ).first()

            if not existing:

                officer = Officer(
                    name=name,
                    email=email,
                    phone=f"900000{officer_index + 1:04d}",
                    designation=designations[
                        officer_index % len(designations)
                    ],
                    department_id=department.id,
                    ward_id=ward.id,
                    is_active=True
                )

                db.add(officer)

    db.commit()
    db.close()

    print("✅ 40 officers seeded successfully!")

def seed_sla_rules():
    db = SessionLocal()

    sla_rules = [
        {
            "category": "Pothole",
            "severity": "HIGH",
            "resolution_hours": 48,
            "description": "Pothole complaints should normally be resolved within 48 hours."
        },
        {
            "category": "Road Damage",
            "severity": "MEDIUM",
            "resolution_hours": 72,
            "description": "General road damage complaints should normally be resolved within 72 hours."
        },
        {
            "category": "Water Leakage",
            "severity": "HIGH",
            "resolution_hours": 12,
            "description": "Major water leakage complaints should be addressed within 12 hours."
        },
        {
            "category": "No Water Supply",
            "severity": "HIGH",
            "resolution_hours": 12,
            "description": "No-water-supply complaints should normally be addressed within 12 hours."
        },
        {
            "category": "Garbage Not Collected",
            "severity": "MEDIUM",
            "resolution_hours": 24,
            "description": "Missed garbage collection complaints should normally be resolved within 24 hours."
        },
        {
            "category": "Overflowing Garbage Bin",
            "severity": "MEDIUM",
            "resolution_hours": 24,
            "description": "Overflowing garbage bins should normally be cleared within 24 hours."
        },
        {
            "category": "Illegal Dumping",
            "severity": "HIGH",
            "resolution_hours": 24,
            "description": "Illegal dumping complaints should normally be addressed within 24 hours."
        },
        {
            "category": "Streetlight Not Working",
            "severity": "MEDIUM",
            "resolution_hours": 48,
            "description": "Streetlight failures should normally be resolved within 48 hours."
        },
        {
            "category": "Drainage Blockage",
            "severity": "HIGH",
            "resolution_hours": 24,
            "description": "Drainage blockage complaints should normally be addressed within 24 hours."
        },
        {
            "category": "Sewage Overflow",
            "severity": "CRITICAL",
            "resolution_hours": 4,
            "description": "Sewage overflow presenting a public-health risk requires urgent response."
        },
        {
            "category": "Public Health",
            "severity": "HIGH",
            "resolution_hours": 24,
            "description": "High-priority public health complaints should normally be addressed within 24 hours."
        },
        {
            "category": "Public Safety",
            "severity": "CRITICAL",
            "resolution_hours": 4,
            "description": "Critical public safety complaints require immediate attention."
        },
        {
            "category": "Park Maintenance",
            "severity": "LOW",
            "resolution_hours": 72,
            "description": "Routine park maintenance complaints should normally be resolved within 72 hours."
        },
        {
            "category": "Broken Footpath",
            "severity": "MEDIUM",
            "resolution_hours": 72,
            "description": "Broken footpath complaints should normally be resolved within 72 hours."
        },
        {
            "category": "Damaged Road Sign",
            "severity": "MEDIUM",
            "resolution_hours": 48,
            "description": "Damaged road sign complaints should normally be resolved within 48 hours."
        }
    ]

    for data in sla_rules:

        existing = db.query(SLARule).filter(
            SLARule.category == data["category"]
        ).first()

        if not existing:
            rule = SLARule(**data)
            db.add(rule)

    db.commit()
    db.close()

    print("✅ SLA rules seeded successfully!")

def seed_citizens():
    db = SessionLocal()

    citizens = [
        {
            "name": "Aditi Sharma",
            "email": "aditi.sharma@example.com",
            "phone": "9876500001",
            "preferred_language": "English"
        },
        {
            "name": "Rahul Patil",
            "email": "rahul.patil@example.com",
            "phone": "9876500002",
            "preferred_language": "Marathi"
        },
        {
            "name": "Sneha Kulkarni",
            "email": "sneha.kulkarni@example.com",
            "phone": "9876500003",
            "preferred_language": "English"
        },
        {
            "name": "Amit Joshi",
            "email": "amit.joshi@example.com",
            "phone": "9876500004",
            "preferred_language": "Hindi"
        },
        {
            "name": "Priya Deshmukh",
            "email": "priya.deshmukh@example.com",
            "phone": "9876500005",
            "preferred_language": "Marathi"
        },
        {
            "name": "Karan Mehta",
            "email": "karan.mehta@example.com",
            "phone": "9876500006",
            "preferred_language": "English"
        },
        {
            "name": "Neha Shah",
            "email": "neha.shah@example.com",
            "phone": "9876500007",
            "preferred_language": "English"
        },
        {
            "name": "Rohan Desai",
            "email": "rohan.desai@example.com",
            "phone": "9876500008",
            "preferred_language": "Hindi"
        },
        {
            "name": "Pooja Nair",
            "email": "pooja.nair@example.com",
            "phone": "9876500009",
            "preferred_language": "English"
        },
        {
            "name": "Vikram Rao",
            "email": "vikram.rao@example.com",
            "phone": "9876500010",
            "preferred_language": "Marathi"
        },
        {
            "name": "Ananya Iyer",
            "email": "ananya.iyer@example.com",
            "phone": "9876500011",
            "preferred_language": "English"
        },
        {
            "name": "Suresh More",
            "email": "suresh.more@example.com",
            "phone": "9876500012",
            "preferred_language": "Marathi"
        },
        {
            "name": "Meera Joshi",
            "email": "meera.joshi@example.com",
            "phone": "9876500013",
            "preferred_language": "Hindi"
        },
        {
            "name": "Arjun Kapoor",
            "email": "arjun.kapoor@example.com",
            "phone": "9876500014",
            "preferred_language": "English"
        },
        {
            "name": "Nisha Patil",
            "email": "nisha.patil@example.com",
            "phone": "9876500015",
            "preferred_language": "Marathi"
        },
        {
            "name": "Manish Verma",
            "email": "manish.verma@example.com",
            "phone": "9876500016",
            "preferred_language": "Hindi"
        },
        {
            "name": "Riya Shah",
            "email": "riya.shah@example.com",
            "phone": "9876500017",
            "preferred_language": "English"
        },
        {
            "name": "Akshay Jadhav",
            "email": "akshay.jadhav@example.com",
            "phone": "9876500018",
            "preferred_language": "Marathi"
        },
        {
            "name": "Divya Menon",
            "email": "divya.menon@example.com",
            "phone": "9876500019",
            "preferred_language": "English"
        },
        {
            "name": "Nikhil Singh",
            "email": "nikhil.singh@example.com",
            "phone": "9876500020",
            "preferred_language": "Hindi"
        },
        {
            "name": "Tanvi Bhosale",
            "email": "tanvi.bhosale@example.com",
            "phone": "9876500021",
            "preferred_language": "Marathi"
        },
        {
            "name": "Harsh Agarwal",
            "email": "harsh.agarwal@example.com",
            "phone": "9876500022",
            "preferred_language": "Hindi"
        },
        {
            "name": "Ishita Rao",
            "email": "ishita.rao@example.com",
            "phone": "9876500023",
            "preferred_language": "English"
        },
        {
            "name": "Varun Joshi",
            "email": "varun.joshi@example.com",
            "phone": "9876500024",
            "preferred_language": "English"
        },
        {
            "name": "Kavya Desai",
            "email": "kavya.desai@example.com",
            "phone": "9876500025",
            "preferred_language": "Marathi"
        },
        {
            "name": "Sameer Khan",
            "email": "sameer.khan@example.com",
            "phone": "9876500026",
            "preferred_language": "Hindi"
        },
        {
            "name": "Maya Kulkarni",
            "email": "maya.kulkarni@example.com",
            "phone": "9876500027",
            "preferred_language": "English"
        },
        {
            "name": "Dev Patel",
            "email": "dev.patel@example.com",
            "phone": "9876500028",
            "preferred_language": "English"
        },
        {
            "name": "Shreya Pawar",
            "email": "shreya.pawar@example.com",
            "phone": "9876500029",
            "preferred_language": "Marathi"
        },
        {
            "name": "Aditya Nair",
            "email": "aditya.nair@example.com",
            "phone": "9876500030",
            "preferred_language": "English"
        }
    ]

    for data in citizens:

        existing = db.query(Citizen).filter(
            Citizen.email == data["email"]
        ).first()

        if not existing:
            citizen = Citizen(**data)
            db.add(citizen)

    db.commit()
    db.close()

    print("✅ 30 citizens seeded successfully!")

def seed_complaints():
    db = SessionLocal()

    citizens = db.query(Citizen).order_by(Citizen.id).all()
    wards = db.query(Ward).order_by(Ward.ward_number).all()
    officers = db.query(Officer).order_by(Officer.id).all()
    sla_rules = db.query(SLARule).all()

    if not citizens or not wards or not officers:
        print("❌ Required master data is missing.")
        db.close()
        return

    complaints_data = [
        ("Large pothole near school gate causing accidents",
         "Pothole", "HIGH", "HIGH"),

        ("No water supply in our building since yesterday",
         "No Water Supply", "HIGH", "HIGH"),

        ("Garbage has not been collected for three days",
         "Garbage Not Collected", "MEDIUM", "MEDIUM"),

        ("Streetlight not working near the main road",
         "Streetlight Not Working", "MEDIUM", "MEDIUM"),

        ("Major water leakage near residential society",
         "Water Leakage", "HIGH", "HIGH"),

        ("Drain completely blocked after heavy rain",
         "Drainage Blockage", "HIGH", "HIGH"),

        ("Sewage overflowing onto the public road",
         "Sewage Overflow", "CRITICAL", "CRITICAL"),

        ("Broken footpath creating difficulty for pedestrians",
         "Broken Footpath", "MEDIUM", "MEDIUM"),

        ("Illegal garbage dumping near the market",
         "Illegal Dumping", "HIGH", "HIGH"),

        ("Damaged road sign at the junction",
         "Damaged Road Sign", "MEDIUM", "MEDIUM"),

        ("Park benches and playground equipment are damaged",
         "Park Maintenance", "LOW", "LOW"),

        ("Road surface damaged after construction work",
         "Road Damage", "MEDIUM", "MEDIUM"),

        ("Water pressure is extremely low in our area",
         "No Water Supply", "MEDIUM", "MEDIUM"),

        ("Streetlight pole is flickering continuously",
         "Streetlight Not Working", "MEDIUM", "MEDIUM"),

        ("Overflowing garbage bin near bus stop",
         "Overflowing Garbage Bin", "MEDIUM", "MEDIUM"),

        ("Large pothole near railway station",
         "Pothole", "HIGH", "HIGH"),

        ("Garbage collection vehicle skipped our street",
         "Garbage Not Collected", "MEDIUM", "MEDIUM"),

        ("Pipeline leakage is flooding the footpath",
         "Water Leakage", "HIGH", "HIGH"),

        ("Blocked drainage causing water accumulation",
         "Drainage Blockage", "HIGH", "HIGH"),

        ("Unsafe dark area near public parking",
         "Streetlight Not Working", "HIGH", "HIGH"),

        ("Broken pavement outside community center",
         "Broken Footpath", "MEDIUM", "MEDIUM"),

        ("Waste dumped illegally behind the market",
         "Illegal Dumping", "HIGH", "HIGH"),

        ("Pothole causing vehicles to slow down suddenly",
         "Pothole", "MEDIUM", "MEDIUM"),

        ("No water supply to the apartment complex",
         "No Water Supply", "HIGH", "HIGH"),

        ("Overflowing waste bin near residential area",
         "Overflowing Garbage Bin", "MEDIUM", "MEDIUM"),

        ("Damaged traffic sign near school",
         "Damaged Road Sign", "HIGH", "HIGH"),

        ("Sewage water entering residential lane",
         "Sewage Overflow", "CRITICAL", "CRITICAL"),

        ("Road has developed multiple cracks",
         "Road Damage", "MEDIUM", "MEDIUM"),

        ("Public park requires urgent cleaning",
         "Park Maintenance", "LOW", "LOW"),

        ("Water leakage from underground pipeline",
         "Water Leakage", "HIGH", "HIGH"),

        ("Garbage collection missed again this week",
         "Garbage Not Collected", "MEDIUM", "MEDIUM"),

        ("Large pothole outside hospital entrance",
         "Pothole", "CRITICAL", "CRITICAL"),

        ("Drain blockage causing foul smell",
         "Drainage Blockage", "HIGH", "HIGH"),

        ("Streetlight completely stopped working",
         "Streetlight Not Working", "MEDIUM", "MEDIUM"),

        ("Broken pedestrian pathway near college",
         "Broken Footpath", "MEDIUM", "MEDIUM"),

        ("Illegal dumping beside riverfront",
         "Illegal Dumping", "HIGH", "HIGH"),

        ("Water supply interrupted since morning",
         "No Water Supply", "HIGH", "HIGH"),

        ("Road sign damaged after vehicle collision",
         "Damaged Road Sign", "HIGH", "HIGH"),

        ("Garbage bins overflowing near railway station",
         "Overflowing Garbage Bin", "MEDIUM", "MEDIUM"),

        ("Park lighting and benches require repair",
         "Park Maintenance", "LOW", "LOW"),

        ("Major road damage causing traffic problems",
         "Road Damage", "HIGH", "HIGH"),

        ("Water pipe leaking continuously",
         "Water Leakage", "HIGH", "HIGH"),

        ("Drainage overflow near residential buildings",
         "Drainage Blockage", "HIGH", "HIGH"),

        ("Streetlight issue causing safety concerns",
         "Streetlight Not Working", "HIGH", "HIGH"),

        ("Garbage not collected from market area",
         "Garbage Not Collected", "MEDIUM", "MEDIUM"),

        ("Pothole near bus stop is becoming dangerous",
         "Pothole", "HIGH", "HIGH"),

        ("Footpath broken and difficult for elderly citizens",
         "Broken Footpath", "HIGH", "HIGH"),

        ("Public park needs maintenance",
         "Park Maintenance", "LOW", "LOW"),

        ("Sewage overflow creating public health risk",
         "Sewage Overflow", "CRITICAL", "CRITICAL")
    ]

    departments = {
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
        "Park Maintenance": "Parks & Public Spaces",
        "Public Safety": "Traffic & Public Safety"
    }

    statuses = [
        "SUBMITTED",
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED"
    ]

    for i, (description, category, severity, priority) in enumerate(complaints_data):

        complaint_number = f"CP-2026-{i + 1:04d}"

        existing = db.query(Complaint).filter(
            Complaint.complaint_number == complaint_number
        ).first()

        if existing:
            continue

        citizen = citizens[i % len(citizens)]
        ward = wards[i % len(wards)]

        department_name = departments.get(category)

        department = db.query(Department).filter(
            Department.name == department_name
        ).first()

        # Find an officer belonging to the same ward and department
        officer = db.query(Officer).filter(
            Officer.ward_id == ward.id,
            Officer.department_id == department.id,
            Officer.is_active == True
        ).first()

        # If no exact ward + department officer exists,
        # find any active officer from the department.
        if not officer:
            officer = db.query(Officer).filter(
                Officer.department_id == department.id,
                Officer.is_active == True
            ).first()

        status = statuses[i % len(statuses)]

        # Find matching SLA rule
        sla_rule = db.query(SLARule).filter(
            SLARule.category == category
        ).first()

        created_at = datetime.utcnow() - timedelta(
            hours=(i * 3) % 120
        )

        sla_deadline = None

        if sla_rule:
            sla_deadline = created_at + timedelta(
                hours=sla_rule.resolution_hours
            )

        resolution_time = None

        if status in ["RESOLVED", "CLOSED"]:
            resolution_time = created_at + timedelta(
                hours=min(
                    sla_rule.resolution_hours - 1
                    if sla_rule else 24,
                    24
                )
            )

        complaint = Complaint(
            complaint_number=complaint_number,
            citizen_id=citizen.id,
            description=description,
            category=category,
            department_id=department.id,
            ward_id=ward.id,
            latitude=18.5204 + ((i % 10) * 0.002),
            longitude=73.8567 + ((i % 10) * 0.002),
            severity=severity,
            priority=priority,
            status=status,
            confidence_score=round(
                0.82 + ((i % 15) / 100),
                2
            ),
            assigned_officer_id=(
                officer.id if officer and status != "SUBMITTED"
                else None
            ),
            sla_deadline=sla_deadline,
            resolution=(
                "Complaint resolved by municipal field team."
                if status in ["RESOLVED", "CLOSED"]
                else None
            ),
            resolution_time=resolution_time,
            created_at=created_at
        )

        db.add(complaint)

    db.commit()
    db.close()

    print("✅ 50 sample complaints seeded successfully!")

if __name__ == "__main__":
    seed_departments()
    seed_wards()
    seed_officers()
    seed_sla_rules()
    seed_citizens()
    seed_complaints()

