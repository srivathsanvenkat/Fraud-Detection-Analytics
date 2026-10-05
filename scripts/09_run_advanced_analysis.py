import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# ============================================================
# CONNECTION
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

conn = psycopg2.connect(DATABASE_URL)

print("=" * 70)
print("STAGE 3 - ADVANCED SQL ANALYSIS")
print("=" * 70)


# ============================================================
# HELPER FUNCTION
# ============================================================

def run_query(title, query, limit=20):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    df = pd.read_sql_query(query, conn)

    if limit:
        print(df.head(limit).to_string(index=False))
    else:
        print(df.to_string(index=False))

    print(f"\nRows returned: {len(df)}")

    return df


# ============================================================
# 1. HIGH ACTIVITY USERS
# ============================================================

q1 = """
SELECT
    u.user_id,
    u.user_region,
    u.membership_type,
    COUNT(t.transaction_id) AS transaction_count,
    COUNT(*) FILTER (
        WHERE t.is_completed_purchase = TRUE
    ) AS purchase_count,
    ROUND(AVG(t.final_amount), 2) AS avg_transaction_amount,
    ROUND(SUM(t.final_amount), 2) AS total_transaction_value
FROM fraud.users u
JOIN fraud.transactions t
    ON u.user_id = t.user_id
GROUP BY
    u.user_id,
    u.user_region,
    u.membership_type
ORDER BY transaction_count DESC,
         total_transaction_value DESC
LIMIT 20;
"""

high_activity_users = run_query(
    "1. HIGH ACTIVITY USERS",
    q1
)


# ============================================================
# 2. AMOUNT VS USER AOV
# ============================================================

q2 = """
SELECT
    t.transaction_id,
    t.user_id,
    ROUND(t.final_amount, 2) AS final_amount,
    ROUND(u.average_order_value, 2) AS user_aov,
    ROUND(
        t.final_amount /
        NULLIF(u.average_order_value, 0),
        2
    ) AS amount_aov_ratio
FROM fraud.transactions t
JOIN fraud.users u
    ON t.user_id = u.user_id
ORDER BY amount_aov_ratio DESC
LIMIT 20;
"""

amount_anomalies = run_query(
    "2. TRANSACTIONS WITH HIGH AMOUNT/AOV RATIO",
    q2
)


# ============================================================
# 3. HIGH DISCOUNT TRANSACTIONS
# ============================================================

q3 = """
SELECT
    t.transaction_id,
    t.user_id,
    t.product_id,
    ROUND(t.base_price, 2) AS base_price,
    ROUND(t.final_amount, 2) AS final_amount,
    ROUND(t.discount_percent, 2) AS discount_percent,
    t.is_completed_purchase
FROM fraud.transactions t
WHERE t.discount_percent >= 60
ORDER BY t.discount_percent DESC;
"""

high_discount = run_query(
    "3. HIGH DISCOUNT TRANSACTIONS",
    q3
)


# ============================================================
# 4. DEVICE / TRAFFIC PERFORMANCE
# ============================================================

q4 = """
SELECT
    device_type,
    traffic_source,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS purchase_count,
    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate,
    ROUND(AVG(final_amount), 2) AS avg_amount
FROM fraud.transactions
GROUP BY device_type, traffic_source
ORDER BY purchase_rate DESC;
"""

channel_analysis = run_query(
    "4. DEVICE AND TRAFFIC ANALYSIS",
    q4,
    limit=None
)


# ============================================================
# 5. USER TRANSACTION DEVIATION
# ============================================================

q5 = """
SELECT
    t.transaction_id,
    t.user_id,
    ROUND(t.final_amount, 2) AS final_amount,
    ROUND(
        AVG(t.final_amount) OVER (
            PARTITION BY t.user_id
        ),
        2
    ) AS user_avg_transaction,
    ROUND(
        t.final_amount /
        NULLIF(
            AVG(t.final_amount) OVER (
                PARTITION BY t.user_id
            ),
            0
        ),
        2
    ) AS transaction_to_user_avg_ratio
FROM fraud.transactions t
ORDER BY transaction_to_user_avg_ratio DESC
LIMIT 20;
"""

user_deviation = run_query(
    "5. TRANSACTION DEVIATION FROM USER BEHAVIOUR",
    q5
)


# ============================================================
# 6. PREVIOUS TRANSACTION COMPARISON
# ============================================================

q6 = """
SELECT
    transaction_id,
    user_id,
    event_timestamp,
    ROUND(final_amount, 2) AS final_amount,
    ROUND(
        LAG(final_amount) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ),
        2
    ) AS previous_amount,
    ROUND(
        final_amount -
        LAG(final_amount) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ),
        2
    ) AS amount_difference
FROM fraud.transactions
ORDER BY ABS(
    final_amount -
    COALESCE(
        LAG(final_amount) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ),
        final_amount
    )
) DESC
LIMIT 20;
"""

transaction_changes = run_query(
    "6. LARGE CHANGES FROM PREVIOUS TRANSACTION",
    q6
)


# ============================================================
# 7. MULTI-FACTOR SUSPICIOUS TRANSACTIONS
# ============================================================

q7 = """
WITH analysis AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.product_id,
        t.final_amount,
        t.discount_percent,
        t.event_sequence_order,
        t.is_completed_purchase,
        u.average_order_value,

        t.final_amount /
        NULLIF(u.average_order_value, 0)
        AS amount_aov_ratio

    FROM fraud.transactions t
    JOIN fraud.users u
        ON t.user_id = u.user_id
)

SELECT
    *,
    CASE
        WHEN amount_aov_ratio >= 10 THEN 1
        ELSE 0
    END AS amount_anomaly,

    CASE
        WHEN discount_percent >= 60 THEN 1
        ELSE 0
    END AS discount_anomaly,

    CASE
        WHEN event_sequence_order <= 2
             AND is_completed_purchase = TRUE
        THEN 1
        ELSE 0
    END AS rapid_purchase_indicator

FROM analysis
WHERE amount_aov_ratio >= 10
   OR discount_percent >= 60
   OR (
       event_sequence_order <= 2
       AND is_completed_purchase = TRUE
   )
ORDER BY amount_aov_ratio DESC;
"""

suspicious_transactions = run_query(
    "7. MULTI-FACTOR SUSPICIOUS TRANSACTIONS",
    q7,
    limit=30
)


# ============================================================
# 8. SUMMARY STATISTICS FOR ANALYTICS
# ============================================================

q8 = """
SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS completed_purchases,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) / COUNT(*),
        2
    ) AS purchase_rate,

    ROUND(AVG(final_amount), 2) AS avg_transaction_amount,

    ROUND(MAX(final_amount), 2) AS max_transaction_amount,

    ROUND(AVG(discount_percent), 2) AS avg_discount

FROM fraud.transactions;
"""

summary = run_query(
    "8. ADVANCED ANALYTICS SUMMARY",
    q8,
    limit=None
)


# ============================================================
# SAVE IMPORTANT OUTPUTS
# ============================================================

os.makedirs("outputs", exist_ok=True)

high_activity_users.to_csv(
    "outputs/high_activity_users.csv",
    index=False
)

amount_anomalies.to_csv(
    "outputs/amount_anomalies.csv",
    index=False
)

high_discount.to_csv(
    "outputs/high_discount_transactions.csv",
    index=False
)

channel_analysis.to_csv(
    "outputs/channel_analysis.csv",
    index=False
)

user_deviation.to_csv(
    "outputs/user_transaction_deviation.csv",
    index=False
)

transaction_changes.to_csv(
    "outputs/transaction_changes.csv",
    index=False
)

suspicious_transactions.to_csv(
    "outputs/suspicious_transactions.csv",
    index=False
)

summary.to_csv(
    "outputs/advanced_summary.csv",
    index=False
)


# ============================================================
# CLOSE
# ============================================================

conn.close()

print("\n" + "=" * 70)
print("ADVANCED ANALYTICS COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nOutputs saved in:")
print("outputs/")