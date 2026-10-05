-- ============================================================
-- BDM FRAUD DETECTION PROJECT
-- STAGE 3: ADVANCED SQL ANALYSIS
-- ============================================================

-- ============================================================
-- 1. USER + TRANSACTION ANALYSIS
-- JOIN + GROUP BY + HAVING
-- ============================================================

SELECT
    u.user_id,
    u.user_region,
    u.membership_type,
    COUNT(t.transaction_id) AS transaction_count,
    COUNT(*) FILTER (WHERE t.is_completed_purchase = TRUE) AS purchase_count,
    ROUND(AVG(t.final_amount), 2) AS avg_transaction_amount,
    ROUND(MAX(t.final_amount), 2) AS max_transaction_amount,
    ROUND(SUM(t.final_amount), 2) AS total_transaction_value
FROM fraud.users u
INNER JOIN fraud.transactions t
    ON u.user_id = t.user_id
GROUP BY
    u.user_id,
    u.user_region,
    u.membership_type
HAVING COUNT(t.transaction_id) >= 5
ORDER BY transaction_count DESC, total_transaction_value DESC;


-- ============================================================
-- 2. TRANSACTION AMOUNT VS USER AVERAGE ORDER VALUE
-- Scalar expression + JOIN
-- ============================================================

SELECT
    t.transaction_id,
    t.user_id,
    t.final_amount,
    u.average_order_value,
    ROUND(
        t.final_amount / NULLIF(u.average_order_value, 0),
        2
    ) AS amount_to_aov_ratio,
    CASE
        WHEN t.final_amount / NULLIF(u.average_order_value, 0) >= 10
            THEN 'High Deviation'
        WHEN t.final_amount / NULLIF(u.average_order_value, 0) >= 5
            THEN 'Moderate Deviation'
        ELSE 'Normal'
    END AS amount_deviation
FROM fraud.transactions t
INNER JOIN fraud.users u
    ON t.user_id = u.user_id
ORDER BY amount_to_aov_ratio DESC
LIMIT 50;


-- ============================================================
-- 3. HIGH DISCOUNT ANALYSIS
-- CASE + JOIN
-- ============================================================

SELECT
    t.transaction_id,
    t.user_id,
    t.product_id,
    p.category_name,
    t.base_price,
    t.final_amount,
    t.discount_percent,
    ROUND(t.base_price - t.final_amount, 2) AS discount_value,
    CASE
        WHEN t.discount_percent >= 70 THEN 'Very High Discount'
        WHEN t.discount_percent >= 60 THEN 'High Discount'
        WHEN t.discount_percent >= 40 THEN 'Moderate Discount'
        ELSE 'Normal'
    END AS discount_category
FROM fraud.transactions t
INNER JOIN fraud.products p
    ON t.product_id = p.product_id
WHERE t.discount_percent >= 60
ORDER BY t.discount_percent DESC;


-- ============================================================
-- 4. PRODUCT PRICE VS FINAL AMOUNT
-- Detect unusually large price reductions
-- ============================================================

SELECT
    t.transaction_id,
    t.product_id,
    p.category_name,
    p.product_price,
    t.base_price,
    t.final_amount,
    ROUND(
        ((t.base_price - t.final_amount)
        / NULLIF(t.base_price, 0)) * 100,
        2
    ) AS calculated_discount_percent,
    t.discount_percent
FROM fraud.transactions t
INNER JOIN fraud.products p
    ON t.product_id = p.product_id
WHERE t.base_price > 0
ORDER BY calculated_discount_percent DESC
LIMIT 50;


-- ============================================================
-- 5. USER ACTIVITY RANKING
-- Window Function: RANK
-- ============================================================

SELECT
    user_id,
    transaction_count,
    purchase_count,
    total_transaction_value,
    RANK() OVER (
        ORDER BY transaction_count DESC
    ) AS activity_rank
FROM (
    SELECT
        user_id,
        COUNT(*) AS transaction_count,
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) AS purchase_count,
        SUM(final_amount) AS total_transaction_value
    FROM fraud.transactions
    GROUP BY user_id
) user_activity
ORDER BY activity_rank
LIMIT 25;


-- ============================================================
-- 6. USER TRANSACTION AMOUNT COMPARISON
-- Window Function: AVG OVER
-- ============================================================

SELECT
    t.transaction_id,
    t.user_id,
    t.event_timestamp,
    t.final_amount,
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
LIMIT 50;


-- ============================================================
-- 7. PREVIOUS TRANSACTION COMPARISON
-- Window Function: LAG
-- ============================================================

SELECT
    transaction_id,
    user_id,
    event_timestamp,
    final_amount,
    LAG(final_amount) OVER (
        PARTITION BY user_id
        ORDER BY event_timestamp
    ) AS previous_transaction_amount,
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
LIMIT 50;


-- ============================================================
-- 8. DEVICE + TRAFFIC BASELINE
-- CTE + GROUP BY
-- ============================================================

WITH channel_performance AS (
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
)
SELECT *
FROM channel_performance
ORDER BY purchase_rate DESC;


-- ============================================================
-- 9. DATA-DRIVEN USER ACTIVITY THRESHOLD
-- CTE + percentile-style practical threshold
-- ============================================================

WITH user_activity AS (
    SELECT
        user_id,
        COUNT(*) AS transaction_count,
        SUM(final_amount) AS total_value
    FROM fraud.transactions
    GROUP BY user_id
),
activity_stats AS (
    SELECT
        AVG(transaction_count) AS avg_transactions,
        MAX(transaction_count) AS max_transactions
    FROM user_activity
)
SELECT
    ua.user_id,
    ua.transaction_count,
    ROUND(ua.total_value, 2) AS total_value,
    ROUND(a.avg_transactions, 2) AS overall_avg_transactions,
    CASE
        WHEN ua.transaction_count >=
             a.avg_transactions * 2
            THEN 'High Activity'
        ELSE 'Normal Activity'
    END AS activity_indicator
FROM user_activity ua
CROSS JOIN activity_stats a
ORDER BY ua.transaction_count DESC;


-- ============================================================
-- 10. MULTI-FACTOR SUSPICIOUS TRANSACTION SCREEN
-- CTE + JOIN + CASE
-- ============================================================

WITH user_stats AS (
    SELECT
        user_id,
        AVG(average_order_value) AS user_aov
    FROM fraud.users
    GROUP BY user_id
),
transaction_analysis AS (
    SELECT
        t.transaction_id,
        t.user_id,
        t.product_id,
        t.final_amount,
        t.discount_percent,
        t.event_sequence_order,
        t.is_completed_purchase,
        u.user_aov,

        t.final_amount /
        NULLIF(u.user_aov, 0) AS amount_aov_ratio

    FROM fraud.transactions t
    INNER JOIN user_stats u
        ON t.user_id = u.user_id
)
SELECT
    transaction_id,
    user_id,
    product_id,
    ROUND(final_amount, 2) AS final_amount,
    ROUND(discount_percent, 2) AS discount_percent,
    ROUND(amount_aov_ratio, 2) AS amount_aov_ratio,
    event_sequence_order,

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

FROM transaction_analysis
WHERE
    amount_aov_ratio >= 10
    OR discount_percent >= 60
    OR (
        event_sequence_order <= 2
        AND is_completed_purchase = TRUE
    )
ORDER BY amount_aov_ratio DESC;


-- ============================================================
-- 11. USERS WITH NO PURCHASE
-- NOT EXISTS SUBQUERY
-- ============================================================

SELECT
    u.user_id,
    u.user_region,
    u.membership_type,
    u.customer_loyalty_score
FROM fraud.users u
WHERE NOT EXISTS (
    SELECT 1
    FROM fraud.transactions t
    WHERE t.user_id = u.user_id
      AND t.is_completed_purchase = TRUE
)
ORDER BY u.customer_loyalty_score DESC;


-- ============================================================
-- 12. PRODUCTS WITH HIGH TRANSACTION VALUE
-- Derived table + HAVING
-- ============================================================

SELECT
    p.product_id,
    p.category_name,
    p.stock_status,
    a.transaction_count,
    a.total_value,
    a.avg_transaction_value
FROM fraud.products p
INNER JOIN (
    SELECT
        product_id,
        COUNT(*) AS transaction_count,
        ROUND(SUM(final_amount), 2) AS total_value,
        ROUND(AVG(final_amount), 2) AS avg_transaction_value
    FROM fraud.transactions
    GROUP BY product_id
    HAVING COUNT(*) >= 5
) a
ON p.product_id = a.product_id
ORDER BY a.total_value DESC;


-- ============================================================
-- 13. FINAL ADVANCED INDICATOR TABLE
-- This will be used by Python/dashboard later
-- ============================================================

WITH user_activity AS (
    SELECT
        user_id,
        COUNT(*) AS user_transaction_count
    FROM fraud.transactions
    GROUP BY user_id
)
SELECT
    t.transaction_id,
    t.user_id,
    t.product_id,
    t.event_timestamp,
    t.final_amount,
    t.discount_percent,
    t.device_type,
    t.traffic_source,
    t.event_type,
    t.event_sequence_order,
    t.is_completed_purchase,

    u.average_order_value,
    ua.user_transaction_count,

    ROUND(
        t.final_amount /
        NULLIF(u.average_order_value, 0),
        2
    ) AS amount_aov_ratio,

    CASE
        WHEN t.final_amount /
             NULLIF(u.average_order_value, 0) >= 10
        THEN 1 ELSE 0
    END AS amount_anomaly,

    CASE
        WHEN t.discount_percent >= 60
        THEN 1 ELSE 0
    END AS discount_anomaly,

    CASE
        WHEN t.event_sequence_order <= 2
             AND t.is_completed_purchase = TRUE
        THEN 1 ELSE 0
    END AS rapid_purchase_indicator,

    CASE
        WHEN ua.user_transaction_count >= 6
        THEN 1 ELSE 0
    END AS high_activity_indicator

FROM fraud.transactions t
INNER JOIN fraud.users u
    ON t.user_id = u.user_id
INNER JOIN user_activity ua
    ON t.user_id = ua.user_id
ORDER BY t.final_amount DESC;