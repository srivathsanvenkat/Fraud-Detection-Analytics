import os
import pandas as pd
import streamlit as st
import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(
    page_title="BDM Transaction Risk Analytics",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_connection():
    return psycopg2.connect(DATABASE_URL)


@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    return pd.read_sql_query(query, conn)


# ============================================================
# HEADER
# ============================================================

st.title("📊 BDM Transaction Risk Analytics")
st.caption(
    "PostgreSQL-based transaction monitoring and risk analysis dashboard"
)

st.markdown("---")


# ============================================================
# LOAD BASIC METRICS
# ============================================================

overview_query = """
SELECT
    (SELECT COUNT(*) FROM fraud.users) AS total_users,
    (SELECT COUNT(*) FROM fraud.products) AS total_products,
    (SELECT COUNT(*) FROM fraud.transactions) AS total_transactions,
    (SELECT COUNT(*)
     FROM fraud.transactions
     WHERE is_completed_purchase = TRUE) AS completed_purchases,
    (SELECT ROUND(
        COUNT(*) FILTER (WHERE is_completed_purchase = TRUE) * 100.0
        / COUNT(*),
        2
    )
     FROM fraud.transactions) AS purchase_rate,
    (SELECT ROUND(SUM(final_amount), 2)
     FROM fraud.transactions) AS total_transaction_value,
    (SELECT COUNT(*)
     FROM fraud.transaction_risk_view
     WHERE risk_level = 'High Risk') AS high_risk_transactions,
    (SELECT COUNT(*)
     FROM fraud.transaction_risk_view
     WHERE risk_level = 'Critical Risk') AS critical_risk_transactions
"""

overview = run_query(overview_query).iloc[0]


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Users",
    f"{int(overview['total_users']):,}"
)

col2.metric(
    "Total Transactions",
    f"{int(overview['total_transactions']):,}"
)

col3.metric(
    "Completed Purchases",
    f"{int(overview['completed_purchases']):,}"
)

col4.metric(
    "Purchase Rate",
    f"{float(overview['purchase_rate']):.2f}%"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Total Products",
    f"{int(overview['total_products']):,}"
)

col6.metric(
    "Transaction Value",
    f"₹{float(overview['total_transaction_value']):,.0f}"
)

col7.metric(
    "High-Risk Transactions",
    f"{int(overview['high_risk_transactions']):,}"
)

col8.metric(
    "Critical-Risk Transactions",
    f"{int(overview['critical_risk_transactions']):,}"
)


st.markdown("---")


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

risk_options = [
    "All",
    "Low Risk",
    "Medium Risk",
    "High Risk",
    "Critical Risk"
]

selected_risk = st.sidebar.selectbox(
    "Risk Level",
    risk_options
)

device_query = """
SELECT DISTINCT device_type
FROM fraud.transactions
ORDER BY device_type
"""

device_data = run_query(device_query)

device_options = ["All"] + device_data["device_type"].tolist()

selected_device = st.sidebar.selectbox(
    "Device Type",
    device_options
)

traffic_query = """
SELECT DISTINCT traffic_source
FROM fraud.transactions
ORDER BY traffic_source
"""

traffic_data = run_query(traffic_query)

traffic_options = ["All"] + traffic_data["traffic_source"].tolist()

selected_traffic = st.sidebar.selectbox(
    "Traffic Source",
    traffic_options
)


# ============================================================
# RISK FILTER CONDITION
# ============================================================

conditions = []

if selected_risk != "All":
    conditions.append(
        f"risk_level = '{selected_risk}'"
    )

if selected_device != "All":
    conditions.append(
        f"device_type = '{selected_device}'"
    )

if selected_traffic != "All":
    conditions.append(
        f"traffic_source = '{selected_traffic}'"
    )

if conditions:
    filter_condition = "WHERE " + " AND ".join(conditions)
else:
    filter_condition = ""


# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.header("1. Risk Overview")

risk_query = f"""
SELECT
    risk_level,
    transaction_count,
    percentage,
    average_risk_score,
    maximum_risk_score,
    average_transaction_amount,
    total_transaction_value
FROM fraud.transaction_risk_summary
ORDER BY
    CASE risk_level
        WHEN 'Critical Risk' THEN 1
        WHEN 'High Risk' THEN 2
        WHEN 'Medium Risk' THEN 3
        WHEN 'Low Risk' THEN 4
    END;
"""

risk_data = run_query(risk_query)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Risk Level Distribution")

    if not risk_data.empty:
        chart_data = risk_data.set_index("risk_level")

        st.bar_chart(
            chart_data["transaction_count"]
        )

with col2:

    st.subheader("Risk Summary")

    st.dataframe(
        risk_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RISK SCORE DISTRIBUTION
# ============================================================

risk_score_query = f"""
SELECT
    risk_score,
    COUNT(*) AS transaction_count
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY risk_score
ORDER BY risk_score
"""

risk_score_data = run_query(risk_score_query)

st.subheader("Risk Score Distribution")

if not risk_score_data.empty:

    st.line_chart(
        risk_score_data.set_index("risk_score")
    )


# ============================================================
# HIGH-RISK TRANSACTIONS
# ============================================================

st.subheader("High-Risk Transactions")

# Build conditions for high-risk transaction query
high_risk_conditions = [
    "risk_level IN ('High Risk', 'Critical Risk')"
]

if selected_risk != "All":
    high_risk_conditions.append(
        f"risk_level = '{selected_risk}'"
    )

if selected_device != "All":
    high_risk_conditions.append(
        f"device_type = '{selected_device}'"
    )

if selected_traffic != "All":
    high_risk_conditions.append(
        f"traffic_source = '{selected_traffic}'"
    )

high_risk_where = " AND ".join(high_risk_conditions)

high_risk_query = f"""
SELECT
    transaction_id,
    user_id,
    product_id,
    final_amount,
    average_order_value AS user_aov,
    amount_aov_ratio,
    discount_percent,
    risk_score,
    risk_level,
    risk_reason
FROM fraud.transaction_risk_view
WHERE {high_risk_where}
ORDER BY risk_score DESC, final_amount DESC
LIMIT 20
"""

high_risk_data = run_query(high_risk_query)

if high_risk_data.empty:

    st.info("No high-risk transactions match the selected filters.")

else:

    st.dataframe(
        high_risk_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# USER / BEHAVIOUR ANALYSIS
# ============================================================

st.markdown("---")

st.header("2. User & Behaviour Analysis")

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Membership Risk
# ------------------------------------------------------------

membership_query = f"""
SELECT
    membership_type,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    COUNT(*) FILTER (
        WHERE risk_level IN ('High Risk', 'Critical Risk')
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY membership_type
ORDER BY average_risk_score DESC
"""

membership_data = run_query(membership_query)

with col1:

    st.subheader("Risk by Membership")

    st.dataframe(
        membership_data,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# Device Risk
# ------------------------------------------------------------

device_risk_query = f"""
SELECT
    device_type,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    COUNT(*) FILTER (
        WHERE risk_level IN ('High Risk', 'Critical Risk')
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY device_type
ORDER BY average_risk_score DESC
"""

device_risk_data = run_query(device_risk_query)

with col2:

    st.subheader("Risk by Device")

    st.dataframe(
        device_risk_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TRAFFIC SOURCE ANALYSIS
# ============================================================

traffic_risk_query = f"""
SELECT
    traffic_source,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    COUNT(*) FILTER (
        WHERE risk_level IN ('High Risk', 'Critical Risk')
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY traffic_source
ORDER BY average_risk_score DESC
"""

traffic_risk_data = run_query(traffic_risk_query)

st.subheader("Risk by Traffic Source")

st.dataframe(
    traffic_risk_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TRANSACTION ANALYSIS
# ============================================================

st.markdown("---")

st.header("3. Transaction Analysis")

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Event Type
# ------------------------------------------------------------

event_query = f"""
SELECT
    event_type,
    COUNT(*) AS transactions,
    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS purchases,
    ROUND(
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) * 100.0 / COUNT(*),
        2
    ) AS purchase_rate
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY event_type
ORDER BY transactions DESC
"""

event_data = run_query(event_query)

with col1:

    st.subheader("Event Behaviour")

    st.dataframe(
        event_data,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# Discount Analysis
# ------------------------------------------------------------

discount_query = f"""
SELECT
    CASE
        WHEN discount_percent < 20 THEN '0-20%'
        WHEN discount_percent < 40 THEN '20-40%'
        WHEN discount_percent < 60 THEN '40-60%'
        WHEN discount_percent < 70 THEN '60-70%'
        ELSE '70%+'
    END AS discount_range,
    COUNT(*) AS transactions,
    ROUND(AVG(risk_score), 2) AS average_risk_score
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY
    CASE
        WHEN discount_percent < 20 THEN '0-20%'
        WHEN discount_percent < 40 THEN '20-40%'
        WHEN discount_percent < 60 THEN '40-60%'
        WHEN discount_percent < 70 THEN '60-70%'
        ELSE '70%+'
    END
ORDER BY
    MIN(discount_percent)
"""

discount_data = run_query(discount_query)

with col2:

    st.subheader("Discount Analysis")

    st.dataframe(
        discount_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# HIGH-VALUE TRANSACTIONS
# ============================================================

st.subheader("Top Transactions by Amount")

high_value_query = f"""
SELECT
    transaction_id,
    user_id,
    product_id,
    final_amount,
    discount_percent,
    device_type,
    traffic_source,
    risk_score,
    risk_level
FROM fraud.transaction_risk_view
{filter_condition}
ORDER BY final_amount DESC
LIMIT 15
"""

high_value_data = run_query(high_value_query)

st.dataframe(
    high_value_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PRODUCT ANALYSIS
# ============================================================

st.markdown("---")

st.header("4. Product Analysis")

product_query = f"""
SELECT
    category_name,
    COUNT(*) AS transactions,
    ROUND(SUM(final_amount), 2) AS transaction_value,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    COUNT(*) FILTER (
        WHERE risk_level IN ('High Risk', 'Critical Risk')
    ) AS high_risk_transactions
FROM fraud.transaction_risk_view
{filter_condition}
GROUP BY category_name
ORDER BY transaction_value DESC
"""

product_data = run_query(product_query)

st.subheader("Category-wise Risk Analysis")

st.dataframe(
    product_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TRANSACTION DETAILS
# ============================================================

st.markdown("---")

st.header("5. Transaction Details")

detail_query = f"""
SELECT
    transaction_id,
    event_timestamp,
    user_id,
    product_id,
    category_name,
    event_type,
    device_type,
    traffic_source,
    discount_percent,
    base_price,
    final_amount,
    is_completed_purchase,
    risk_score,
    risk_level,
    risk_reason
FROM fraud.transaction_risk_view
{filter_condition}
ORDER BY risk_score DESC, event_timestamp DESC
LIMIT 100
"""

detail_data = run_query(detail_query)

st.dataframe(
    detail_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "BDM Capstone Project | PostgreSQL + Python + Streamlit"
)

st.caption(
    "Risk levels represent analytical risk indicators and should "
    "not be interpreted as confirmed fraud without verified fraud labels."
)