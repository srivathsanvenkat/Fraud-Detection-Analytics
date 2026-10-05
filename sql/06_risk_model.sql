-- ============================================================
-- BDM FRAUD DETECTION PROJECT
-- STAGE 4: TRANSACTION RISK MODEL
-- ============================================================

DROP VIEW IF EXISTS fraud.transaction_risk_view;

CREATE VIEW fraud.transaction_risk_view AS

WITH transaction_base AS (

    SELECT
        t.transaction_id,
        t.session_id,
        t.user_id,
        t.product_id,
        t.event_timestamp,
        t.event_type,
        t.event_sequence_order,
        t.device_type,
        t.traffic_source,
        t.discount_percent,
        t.delivery_option,
        t.time_spent_on_product_sec,
        t.recommendation_action,
        t.base_price,
        t.final_amount,
        t.is_completed_purchase,

        u.user_region,
        u.user_age_group,
        u.membership_type,
        u.customer_loyalty_score,
        u.purchase_frequency,
        u.average_order_value,

        p.category_name,
        p.brand_id,
        p.product_price,
        p.product_rating,
        p.review_count,
        p.stock_status,

        ROUND(
            t.final_amount /
            NULLIF(u.average_order_value, 0),
            2
        ) AS amount_aov_ratio,

        LAG(t.final_amount) OVER (
            PARTITION BY t.user_id
            ORDER BY t.event_timestamp
        ) AS previous_transaction_amount,

        COUNT(*) OVER (
            PARTITION BY t.user_id
        ) AS user_transaction_count

    FROM fraud.transactions t

    INNER JOIN fraud.users u
        ON t.user_id = u.user_id

    INNER JOIN fraud.products p
        ON t.product_id = p.product_id
),

indicators AS (

    SELECT
        *,

        CASE
            WHEN amount_aov_ratio >= 10 THEN 1
            ELSE 0
        END AS amount_anomaly,

        CASE
            WHEN amount_aov_ratio >= 5
             AND amount_aov_ratio < 10
            THEN 1
            ELSE 0
        END AS moderate_amount_anomaly,

        CASE
            WHEN discount_percent >= 70 THEN 1
            ELSE 0
        END AS very_high_discount,

        CASE
            WHEN discount_percent >= 60
             AND discount_percent < 70
            THEN 1
            ELSE 0
        END AS high_discount,

        CASE
            WHEN previous_transaction_amount IS NOT NULL
             AND ABS(
                 final_amount - previous_transaction_amount
             ) >= 50000
            THEN 1
            ELSE 0
        END AS large_amount_change,

        CASE
            WHEN user_transaction_count >= 6
            THEN 1
            ELSE 0
        END AS high_activity,

        CASE
            WHEN event_sequence_order <= 2
             AND is_completed_purchase = TRUE
            THEN 1
            ELSE 0
        END AS rapid_purchase

    FROM transaction_base
),

scored AS (

    SELECT
        *,

        (
            CASE
                WHEN amount_anomaly = 1
                    THEN 40
                WHEN moderate_amount_anomaly = 1
                    THEN 25
                ELSE 0
            END

            +

            CASE
                WHEN very_high_discount = 1
                    THEN 20
                WHEN high_discount = 1
                    THEN 10
                ELSE 0
            END

            +

            CASE
                WHEN large_amount_change = 1
                    THEN 20
                ELSE 0
            END

            +

            CASE
                WHEN high_activity = 1
                    THEN 10
                ELSE 0
            END

            +

            CASE
                WHEN rapid_purchase = 1
                    THEN 10
                ELSE 0
            END

        ) AS risk_score

    FROM indicators
)

SELECT
    transaction_id,
    session_id,
    user_id,
    product_id,
    event_timestamp,

    user_region,
    user_age_group,
    membership_type,
    customer_loyalty_score,

    category_name,
    brand_id,
    product_rating,
    review_count,
    stock_status,

    event_type,
    event_sequence_order,
    device_type,
    traffic_source,
    delivery_option,
    recommendation_action,

    base_price,
    final_amount,
    discount_percent,
    is_completed_purchase,

    average_order_value,
    amount_aov_ratio,
    previous_transaction_amount,
    user_transaction_count,

    amount_anomaly,
    moderate_amount_anomaly,
    very_high_discount,
    high_discount,
    large_amount_change,
    high_activity,
    rapid_purchase,

    risk_score,

    CASE
        WHEN risk_score >= 70
            THEN 'Critical Risk'
        WHEN risk_score >= 50
            THEN 'High Risk'
        WHEN risk_score >= 30
            THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_level,

    CONCAT(
        CASE
            WHEN amount_anomaly = 1
                THEN 'High amount/AOV deviation; '
            WHEN moderate_amount_anomaly = 1
                THEN 'Moderate amount/AOV deviation; '
            ELSE ''
        END,

        CASE
            WHEN very_high_discount = 1
                THEN 'Very high discount; '
            WHEN high_discount = 1
                THEN 'High discount; '
            ELSE ''
        END,

        CASE
            WHEN large_amount_change = 1
                THEN 'Large change from previous transaction; '
            ELSE ''
        END,

        CASE
            WHEN high_activity = 1
                THEN 'High user activity; '
            ELSE ''
        END,

        CASE
            WHEN rapid_purchase = 1
                THEN 'Rapid purchase behaviour'
            ELSE ''
        END
    ) AS risk_reason

FROM scored;