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
print("STAGE 4 - TRANSACTION RISK MODEL")
print("=" * 70)


# ============================================================
# CREATE VIEW
# ============================================================

with open(
    "sql/06_risk_model.sql",
    "r",
    encoding="utf-8"
) as file:
    sql = file.read()

with conn.cursor() as cursor:
    cursor.execute(sql)

conn.commit()

print("\nRisk model view created successfully.")


# ============================================================
# 1. RISK LEVEL DISTRIBUTION
# ============================================================

query1 = """
SELECT
    risk_level,
    COUNT(*) AS transaction_count,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
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

risk_distribution = pd.read_sql_query(query1, conn)

print("\n" + "=" * 70)
print("1. RISK LEVEL DISTRIBUTION")
print("=" * 70)
print(risk_distribution.to_string(index=False))


# ============================================================
# 2. TOP RISK TRANSACTIONS
# ============================================================

query2 = """
SELECT
    transaction_id,
    user_id,
    product_id,
    ROUND(final_amount, 2) AS final_amount,
    ROUND(average_order_value, 2) AS user_aov,
    amount_aov_ratio,
    discount_percent,
    risk_score,
    risk_level,
    risk_reason
FROM fraud.transaction_risk_view
WHERE risk_score >= 60
ORDER BY risk_score DESC,
         amount_aov_ratio DESC
LIMIT 50;
"""

top_risk = pd.read_sql_query(query2, conn)

print("\n" + "=" * 70)
print("2. TOP HIGH-RISK TRANSACTIONS")
print("=" * 70)
print(top_risk.to_string(index=False))


# ============================================================
# 3. RISK BY DEVICE
# ============================================================

query3 = """
SELECT
    device_type,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    COUNT(*) FILTER (
        WHERE risk_score >= 60
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
GROUP BY device_type
ORDER BY avg_risk_score DESC;
"""

device_risk = pd.read_sql_query(query3, conn)

print("\n" + "=" * 70)
print("3. RISK BY DEVICE")
print("=" * 70)
print(device_risk.to_string(index=False))


# ============================================================
# 4. RISK BY TRAFFIC SOURCE
# ============================================================

query4 = """
SELECT
    traffic_source,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    COUNT(*) FILTER (
        WHERE risk_score >= 60
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
GROUP BY traffic_source
ORDER BY avg_risk_score DESC;
"""

traffic_risk = pd.read_sql_query(query4, conn)

print("\n" + "=" * 70)
print("4. RISK BY TRAFFIC SOURCE")
print("=" * 70)
print(traffic_risk.to_string(index=False))


# ============================================================
# 5. RISK BY MEMBERSHIP
# ============================================================

query5 = """
SELECT
    membership_type,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    COUNT(*) FILTER (
        WHERE risk_score >= 60
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
GROUP BY membership_type
ORDER BY avg_risk_score DESC;
"""

membership_risk = pd.read_sql_query(query5, conn)

print("\n" + "=" * 70)
print("5. RISK BY MEMBERSHIP")
print("=" * 70)
print(membership_risk.to_string(index=False))


# ============================================================
# 6. RISK SUMMARY
# ============================================================

query6 = """
SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE risk_score >= 60
    ) AS high_risk_transactions,

    COUNT(*) FILTER (
        WHERE risk_score >= 80
    ) AS critical_risk_transactions,

    ROUND(AVG(risk_score), 2) AS average_risk_score,

    ROUND(MAX(risk_score), 2) AS maximum_risk_score

FROM fraud.transaction_risk_view;
"""

summary = pd.read_sql_query(query6, conn)

print("\n" + "=" * 70)
print("6. RISK SUMMARY")
print("=" * 70)
print(summary.to_string(index=False))


# ============================================================
# SAVE OUTPUTS
# ============================================================

os.makedirs("outputs", exist_ok=True)

risk_distribution.to_csv(
    "outputs/risk_distribution.csv",
    index=False
)

top_risk.to_csv(
    "outputs/top_risk_transactions.csv",
    index=False
)

device_risk.to_csv(
    "outputs/device_risk.csv",
    index=False
)

traffic_risk.to_csv(
    "outputs/traffic_risk.csv",
    index=False
)

membership_risk.to_csv(
    "outputs/membership_risk.csv",
    index=False
)

summary.to_csv(
    "outputs/risk_summary.csv",
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

conn.close()

print("\n" + "=" * 70)
print("RISK MODEL COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nCreated PostgreSQL VIEW:")
print("fraud.transaction_risk_view")

print("\nOutput files saved in:")
print("outputs/")