import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

try:
    with conn.cursor() as cur:

        queries = [
            """
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id
            ON fraud.transactions(user_id);
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_transactions_product_id
            ON fraud.transactions(product_id);
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
            ON fraud.transactions(event_timestamp);
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_transactions_purchase
            ON fraud.transactions(is_completed_purchase);
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_transactions_event_type
            ON fraud.transactions(event_type);
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_transactions_user_timestamp
            ON fraud.transactions(user_id, event_timestamp);
            """
        ]

        for query in queries:
            cur.execute(query)

        conn.commit()

        print("=" * 70)
        print("STAGE 5 - DATABASE INDEXES")
        print("=" * 70)
        print()
        print("Indexes created successfully.")
        print()
        print("Created indexes:")
        print("1. idx_transactions_user_id")
        print("2. idx_transactions_product_id")
        print("3. idx_transactions_timestamp")
        print("4. idx_transactions_purchase")
        print("5. idx_transactions_event_type")
        print("6. idx_transactions_user_timestamp")
        print()
        print("STAGE 5 COMPLETED SUCCESSFULLY")

except Exception as e:
    conn.rollback()
    print("Error:", e)

finally:
    conn.close()