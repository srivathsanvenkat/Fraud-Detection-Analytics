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

    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS fraud;
    """)

    conn.commit()

    print("Schema 'fraud' created successfully!")

    cursor.close()
    conn.close()

except Exception as e:
    print("Error creating schema:")
    print(e)