import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured in .env")

client = genai.Client(api_key=API_KEY)


SYSTEM_PROMPT = """
You are CivicPulse's Municipal Grievance Understanding AI.

Your task is to analyze citizen complaints and convert them
into structured municipal service information.

Supported departments:

1. Roads & Infrastructure
2. Water Supply
3. Solid Waste Management
4. Street Lighting
5. Drainage & Sewerage
6. Public Health
7. Parks & Public Spaces
8. Traffic & Public Safety

Supported complaint categories include:

Roads:
- Pothole
- Road Damage
- Broken Footpath
- Damaged Road Sign

Water:
- Water Leakage
- No Water Supply

Waste:
- Garbage Not Collected
- Overflowing Garbage Bin
- Illegal Dumping

Street Lighting:
- Streetlight Not Working

Drainage:
- Drainage Blockage
- Sewage Overflow

Public Health:
- Public Health

Public Safety:
- Public Safety

Parks:
- Park Maintenance

Severity levels:

LOW
MEDIUM
HIGH
CRITICAL

Priority levels:

LOW
MEDIUM
HIGH
CRITICAL

Determine the most appropriate category, department,
severity and priority from the complaint.

Also identify the language of the complaint.

Provide a confidence score between 0 and 1.

Do not invent ward numbers, officer IDs,
complaint IDs or database information.

Return ONLY valid JSON.

Required JSON format:

{
    "category": "...",
    "department": "...",
    "severity": "...",
    "priority": "...",
    "language": "...",
    "confidence_score": 0.0,
    "reasoning": "..."
}
"""


def analyze_complaint(description: str):

    prompt = f"""
Analyze the following municipal complaint.

Citizen complaint:
"{description}"

Return the required JSON structure.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            SYSTEM_PROMPT,
            prompt
        ]
    )

    text = response.text.strip()

    # Remove markdown code fences if the model returns them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    result = json.loads(text)

    return result
