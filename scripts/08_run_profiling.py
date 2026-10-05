# ============================================
# BDM Fraud Detection Project
# Stage 2: Run Basic SQL Profiling
# ============================================

import os
import re
import psycopg2
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")


# SQL file location
SQL_FILE = "sql/04_basic_profiling.sql"


# Read SQL file
with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql_content = file.read()


# Split SQL statements
statements = [
    statement.strip()
    for statement in sql_content.split(";")
    if statement.strip()
]


# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


print("=" * 70)
print("BDM FRAUD DETECTION - BASIC SQL PROFILING")
print("=" * 70)


try:
    for index, statement in enumerate(statements, start=1):

        # Extract section title from the SQL comments
        titles = re.findall(
            r"--\s*\d+\.\s*(.+)",
            statement
        )

        if titles:
            title = titles[0].strip()
        else:
            title = f"Query {index}"

        print("\n" + "-" * 70)
        print(f"{index}. {title}")
        print("-" * 70)

        cursor.execute(statement)

        # SELECT queries return rows
        if cursor.description:

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

            # Print column names
            print(" | ".join(columns))
            print("-" * 70)

            # Print results
            for row in rows[:20]:
                print(" | ".join(str(value) for value in row))

            # Show if more rows exist
            if len(rows) > 20:
                print(f"... {len(rows) - 20} more rows")

        else:
            print("Query executed successfully.")

    conn.commit()

    print("\n" + "=" * 70)
    print("BASIC PROFILING COMPLETED")
    print("=" * 70)

except Exception as e:
    conn.rollback()

    print("\n" + "=" * 70)
    print("ERROR DURING PROFILING")
    print("=" * 70)
    print(e)

    raise

finally:
    cursor.close()
    conn.close()