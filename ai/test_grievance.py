from ai.grievance_understanding import analyze_complaint


complaint = """
There is a huge pothole near the school gate.
Two-wheelers are almost falling because of it.
It has been there for a week.
"""


result = analyze_complaint(complaint)

print("\nCivicPulse AI Analysis")
print("----------------------")

for key, value in result.items():
    print(f"{key}: {value}")