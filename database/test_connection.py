from database.database import engine


try:
    with engine.connect() as connection:
        print("✅ CivicPulse successfully connected to MySQL!")
except Exception as e:
    print("❌ Database connection failed.")
    print(e)
    