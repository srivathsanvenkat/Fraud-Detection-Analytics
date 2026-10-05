import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

try:
    with conn.cursor() as cur:

        query = """
        DROP MATERIALIZED VIEW IF EXISTS fraud.transaction_risk_summary;

        CREATE MATERIALIZED VIEW fraud.transaction_risk_summary AS

        SELECT
            risk_level,
            COUNT(*) AS transaction_count,
            ROUND(
                COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (),
                2
            ) AS percentage,
            ROUND(AVG(risk_score), 2) AS average_risk_score,
            ROUND(MAX(risk_score), 2) AS maximum_risk_score,
            ROUND(AVG(final_amount), 2) AS average_transaction_amount,
            ROUND(SUM(final_amount), 2) AS total_transaction_value

        FROM fraud.transaction_risk_view

        GROUP BY risk_level

        ORDER BY
            CASE risk_level
                WHEN 'Critical Risk' THEN 1
                WHEN 'High Risk' THEN 2
                WHEN 'Medium Risk' THEN 3
                WHEN 'Low Risk' THEN 4
            END;
        """

        cur.execute(query)
        conn.commit()

        print("=" * 70)
        print("STAGE 6 - MATERIALIZED VIEW")
        print("=" * 70)
        print()
        print("Materialized view created successfully.")
        print()
        print("View:")
        print("fraud.transaction_risk_summary")
        print()

        cur.execute("""
            SELECT *
            FROM fraud.transaction_risk_summary;
        """)

        rows = cur.fetchall()

        print("RISK SUMMARY")
        print("-" * 70)

        for row in rows:
            print(row)

        print()
        print("STAGE 6 COMPLETED SUCCESSFULLY")

except Exception as e:
    conn.rollback()
    print("Error:", e)

finally:
    conn.close()