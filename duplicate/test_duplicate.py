from duplicate.duplicate_detector import calculate_similarity


text1 = """
There is a huge pothole near the school gate.
Two-wheelers are almost falling because of it.
"""

text2 = """
A large pothole has appeared near the school entrance.
Many bikes are having difficulty passing through it.
"""

text3 = """
The garbage collection truck has not arrived
for three days and garbage is piling up.
"""


print("\n" + "=" * 60)
print("CIVICPULSE DUPLICATE DETECTION TEST")
print("=" * 60)

similarity_1 = calculate_similarity(
    text1,
    text2
)

similarity_2 = calculate_similarity(
    text1,
    text3
)

print(
    f"\nPothole vs Similar Pothole: "
    f"{similarity_1:.4f}"
)

print(
    f"Pothole vs Garbage Complaint: "
    f"{similarity_2:.4f}"
)

print("\n" + "=" * 60)