import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check your .env file.")

try:
    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()
    cursor.execute("SELECT version();")

    version = cursor.fetchone()[0]

    print("Database connection successful!")
    print("PostgreSQL version:")
    print(version)

    cursor.close()
    conn.close()

except Exception as e:
    print("Database connection failed.")
    print("Error:", e)