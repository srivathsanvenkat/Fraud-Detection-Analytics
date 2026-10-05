import os
import psycopg2
from dotenv import load_dotenv

# ============================================
# Load environment variables
# ============================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")


# ============================================
# Connect to PostgreSQL
# ============================================

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("=" * 60)
print("BDM FRAUD DETECTION - DATA VALIDATION")
print("=" * 60)


# ============================================
# Validation queries
# ============================================

queries = {

    "1. ROW COUNTS": """
        SELECT 'Users' AS table_name, COUNT(*) AS row_count
        FROM fraud.users

        UNION ALL

        SELECT 'Products', COUNT(*)
        FROM fraud.products

        UNION ALL

        SELECT 'Transactions', COUNT(*)
        FROM fraud.transactions;
    """,

    "2. DUPLICATE USERS": """
        SELECT user_id, COUNT(*) AS occurrences
        FROM fraud.users
        GROUP BY user_id
        HAVING COUNT(*) > 1;
    """,

    "3. DUPLICATE PRODUCTS": """
        SELECT product_id, COUNT(*) AS occurrences
        FROM fraud.products
        GROUP BY product_id
        HAVING COUNT(*) > 1;
    """,

    "4. DUPLICATE TRANSACTIONS": """
        SELECT transaction_id, COUNT(*) AS occurrences
        FROM fraud.transactions
        GROUP BY transaction_id
        HAVING COUNT(*) > 1;
    """,

    "5. USER NULL CHECK": """
        SELECT
            COUNT(*) FILTER (WHERE user_id IS NULL),
            COUNT(*) FILTER (WHERE user_region IS NULL),
            COUNT(*) FILTER (WHERE user_age_group IS NULL),
            COUNT(*) FILTER (WHERE membership_type IS NULL),
            COUNT(*) FILTER (WHERE customer_loyalty_score IS NULL),
            COUNT(*) FILTER (WHERE purchase_frequency IS NULL),
            COUNT(*) FILTER (WHERE average_order_value IS NULL)
        FROM fraud.users;
    """,

    "6. PRODUCT NULL CHECK": """
        SELECT
            COUNT(*) FILTER (WHERE product_id IS NULL),
            COUNT(*) FILTER (WHERE category_name IS NULL),
            COUNT(*) FILTER (WHERE brand_id IS NULL),
            COUNT(*) FILTER (WHERE product_price IS NULL),
            COUNT(*) FILTER (WHERE product_rating IS NULL),
            COUNT(*) FILTER (WHERE review_count IS NULL),
            COUNT(*) FILTER (WHERE stock_status IS NULL)
        FROM fraud.products;
    """,

    "7. TRANSACTION NULL CHECK": """
        SELECT
            COUNT(*) FILTER (WHERE transaction_id IS NULL),
            COUNT(*) FILTER (WHERE session_id IS NULL),
            COUNT(*) FILTER (WHERE user_id IS NULL),
            COUNT(*) FILTER (WHERE product_id IS NULL),
            COUNT(*) FILTER (WHERE event_timestamp IS NULL),
            COUNT(*) FILTER (WHERE event_type IS NULL),
            COUNT(*) FILTER (WHERE device_type IS NULL),
            COUNT(*) FILTER (WHERE traffic_source IS NULL),
            COUNT(*) FILTER (WHERE discount_percent IS NULL),
            COUNT(*) FILTER (WHERE delivery_option IS NULL),
            COUNT(*) FILTER (WHERE time_spent_on_product_sec IS NULL),
            COUNT(*) FILTER (WHERE recommendation_action IS NULL),
            COUNT(*) FILTER (WHERE base_price IS NULL),
            COUNT(*) FILTER (WHERE final_amount IS NULL),
            COUNT(*) FILTER (WHERE is_completed_purchase IS NULL)
        FROM fraud.transactions;
    """,

    "8. ORPHAN USERS": """
        SELECT COUNT(*) AS orphan_transactions
        FROM fraud.transactions t
        LEFT JOIN fraud.users u
            ON t.user_id = u.user_id
        WHERE u.user_id IS NULL;
    """,

    "9. ORPHAN PRODUCTS": """
        SELECT COUNT(*) AS orphan_transactions
        FROM fraud.transactions t
        LEFT JOIN fraud.products p
            ON t.product_id = p.product_id
        WHERE p.product_id IS NULL;
    """,

    "10. INVALID PRODUCT RATINGS": """
        SELECT COUNT(*)
        FROM fraud.products
        WHERE product_rating < 0
           OR product_rating > 5;
    """,

    "11. INVALID DISCOUNTS": """
        SELECT COUNT(*)
        FROM fraud.transactions
        WHERE discount_percent < 0
           OR discount_percent > 100;
    """,

    "12. NEGATIVE AMOUNTS": """
        SELECT COUNT(*)
        FROM fraud.transactions
        WHERE base_price < 0
           OR final_amount < 0;
    """,

    "13. NEGATIVE TIME VALUES": """
        SELECT COUNT(*)
        FROM fraud.transactions
        WHERE time_spent_on_product_sec < 0;
    """,

    "14. NEGATIVE EVENT SEQUENCE": """
        SELECT COUNT(*)
        FROM fraud.transactions
        WHERE event_sequence_order < 0;
    """,

    "15. PURCHASE FLAG DISTRIBUTION": """
        SELECT
            is_completed_purchase,
            COUNT(*) AS transaction_count
        FROM fraud.transactions
        GROUP BY is_completed_purchase
        ORDER BY is_completed_purchase;
    """,

    "16. EVENT TYPE DISTRIBUTION": """
        SELECT
            event_type,
            COUNT(*) AS event_count
        FROM fraud.transactions
        GROUP BY event_type
        ORDER BY event_count DESC;
    """,

    "17. DEVICE DISTRIBUTION": """
        SELECT
            device_type,
            COUNT(*) AS transaction_count
        FROM fraud.transactions
        GROUP BY device_type
        ORDER BY transaction_count DESC;
    """,

    "18. TRAFFIC SOURCE DISTRIBUTION": """
        SELECT
            traffic_source,
            COUNT(*) AS transaction_count
        FROM fraud.transactions
        GROUP BY traffic_source
        ORDER BY transaction_count DESC;
    """,

    "19. RECOMMENDATION ACTION DISTRIBUTION": """
        SELECT
            recommendation_action,
            COUNT(*) AS transaction_count
        FROM fraud.transactions
        GROUP BY recommendation_action
        ORDER BY transaction_count DESC;
    """,

    "20. EVENT SEQUENCE SUMMARY": """
        SELECT
            MIN(event_sequence_order) AS minimum_sequence,
            MAX(event_sequence_order) AS maximum_sequence,
            ROUND(AVG(event_sequence_order), 2) AS average_sequence
        FROM fraud.transactions;
    """,

    "21. TRANSACTION AMOUNT SUMMARY": """
        SELECT
            COUNT(*) AS transaction_count,
            ROUND(MIN(base_price), 2) AS minimum_base_price,
            ROUND(MAX(base_price), 2) AS maximum_base_price,
            ROUND(AVG(base_price), 2) AS average_base_price,
            ROUND(MIN(final_amount), 2) AS minimum_final_amount,
            ROUND(MAX(final_amount), 2) AS maximum_final_amount,
            ROUND(AVG(final_amount), 2) AS average_final_amount
        FROM fraud.transactions;
    """,

    "22. DISCOUNT SUMMARY": """
        SELECT
            ROUND(MIN(discount_percent), 2) AS minimum_discount,
            ROUND(MAX(discount_percent), 2) AS maximum_discount,
            ROUND(AVG(discount_percent), 2) AS average_discount
        FROM fraud.transactions;
    """,

    "23. PURCHASE EVENT CONSISTENCY": """
        SELECT
            COUNT(*) AS inconsistent_purchase_events
        FROM fraud.transactions
        WHERE
            (event_type = 'Purchase' AND is_completed_purchase = FALSE)
            OR
            (event_type <> 'Purchase' AND is_completed_purchase = TRUE);
    """,

    "24. BASIC DATA QUALITY SUMMARY": """
        SELECT
            (SELECT COUNT(*) FROM fraud.users) AS users_count,
            (SELECT COUNT(*) FROM fraud.products) AS products_count,
            (SELECT COUNT(*) FROM fraud.transactions) AS transactions_count,
            (SELECT COUNT(DISTINCT user_id)
             FROM fraud.transactions) AS active_users,
            (SELECT COUNT(DISTINCT product_id)
             FROM fraud.transactions) AS active_products,
            (SELECT COUNT(DISTINCT session_id)
             FROM fraud.transactions) AS sessions,
            (SELECT COUNT(DISTINCT event_timestamp::date)
             FROM fraud.transactions) AS transaction_days;
    """
}


# ============================================
# Execute validation
# ============================================

for title, query in queries.items():

    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

    try:
        cursor.execute(query)

        results = cursor.fetchall()

        if not results:
            print("PASS - No issues found.")
        else:
            for row in results:
                print(row)

    except Exception as e:
        print("ERROR:", e)
        conn.rollback()


# ============================================
# Close connection
# ============================================

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("DATA VALIDATION COMPLETED")
print("=" * 60)