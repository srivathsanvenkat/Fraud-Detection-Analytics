-- ============================================
-- BDM Fraud Detection Project
-- Stage 2: Basic SQL Profiling
-- ============================================

-- ============================================
-- 1. OVERALL DATABASE PROFILE
-- ============================================

SELECT
    (SELECT COUNT(*) FROM fraud.users) AS total_users,
    (SELECT COUNT(*) FROM fraud.products) AS total_products,
    (SELECT COUNT(*) FROM fraud.transactions) AS total_transactions;


-- ============================================
-- 2. TRANSACTION AMOUNT PROFILE
-- ============================================

SELECT
    COUNT(*) AS transaction_count,
    ROUND(AVG(final_amount), 2) AS average_amount,
    ROUND(MIN(final_amount), 2) AS minimum_amount,
    ROUND(MAX(final_amount), 2) AS maximum_amount,
    ROUND(SUM(final_amount), 2) AS total_transaction_value
FROM fraud.transactions;


-- ============================================
-- 3. DISCOUNT PROFILE
-- ============================================

SELECT
    COUNT(*) AS transaction_count,
    ROUND(AVG(discount_percent), 2) AS average_discount,
    ROUND(MIN(discount_percent), 2) AS minimum_discount,
    ROUND(MAX(discount_percent), 2) AS maximum_discount
FROM fraud.transactions;


-- ============================================
-- 4. PURCHASE VS NON-PURCHASE
-- ============================================

SELECT
    is_completed_purchase,
    COUNT(*) AS transaction_count,
    ROUND(
        COUNT(*) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM fraud.transactions), 0),
        2
    ) AS percentage
FROM fraud.transactions
GROUP BY is_completed_purchase
ORDER BY is_completed_purchase DESC;


-- ============================================
-- 5. DISTINCT USER REGIONS
-- ============================================

SELECT DISTINCT
    user_region
FROM fraud.users
ORDER BY user_region;


-- ============================================
-- 6. USERS BY REGION
-- ============================================

SELECT
    user_region,
    COUNT(*) AS user_count
FROM fraud.users
GROUP BY user_region
ORDER BY user_count DESC;


-- ============================================
-- 7. USERS BY MEMBERSHIP TYPE
-- ============================================

SELECT
    membership_type,
    COUNT(*) AS user_count,
    ROUND(AVG(customer_loyalty_score), 2) AS average_loyalty_score,
    ROUND(AVG(purchase_frequency), 2) AS average_purchase_frequency,
    ROUND(AVG(average_order_value), 2) AS average_order_value
FROM fraud.users
GROUP BY membership_type
ORDER BY user_count DESC;


-- ============================================
-- 8. USERS BY AGE GROUP
-- ============================================

SELECT
    user_age_group,
    COUNT(*) AS user_count,
    ROUND(AVG(customer_loyalty_score), 2) AS average_loyalty_score,
    ROUND(AVG(average_order_value), 2) AS average_order_value
FROM fraud.users
GROUP BY user_age_group
ORDER BY user_age_group;


-- ============================================
-- 9. CUSTOMER LOYALTY PROFILE
-- ============================================

SELECT
    ROUND(MIN(customer_loyalty_score), 2) AS minimum_loyalty,
    ROUND(AVG(customer_loyalty_score), 2) AS average_loyalty,
    ROUND(MAX(customer_loyalty_score), 2) AS maximum_loyalty
FROM fraud.users;


-- ============================================
-- 10. PURCHASE FREQUENCY PROFILE
-- ============================================

SELECT
    ROUND(MIN(purchase_frequency), 2) AS minimum_frequency,
    ROUND(AVG(purchase_frequency), 2) AS average_frequency,
    ROUND(MAX(purchase_frequency), 2) AS maximum_frequency
FROM fraud.users;


-- ============================================
-- 11. PRODUCT CATEGORY PROFILE
-- ============================================

SELECT
    category_name,
    COUNT(*) AS product_count,
    ROUND(AVG(product_price), 2) AS average_price,
    ROUND(AVG(product_rating), 2) AS average_rating,
    SUM(review_count) AS total_reviews
FROM fraud.products
GROUP BY category_name
ORDER BY product_count DESC;


-- ============================================
-- 12. PRODUCT STOCK STATUS
-- ============================================

SELECT
    stock_status,
    COUNT(*) AS product_count,
    ROUND(
        COUNT(*) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM fraud.products), 0),
        2
    ) AS percentage
FROM fraud.products
GROUP BY stock_status
ORDER BY product_count DESC;


-- ============================================
-- 13. EVENT TYPE PROFILE
-- ============================================

SELECT
    event_type,
    COUNT(*) AS event_count,
    ROUND(AVG(final_amount), 2) AS average_amount
FROM fraud.transactions
GROUP BY event_type
ORDER BY event_count DESC;


-- ============================================
-- 14. DEVICE TYPE PROFILE
-- ============================================

SELECT
    device_type,
    COUNT(*) AS transaction_count,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(
        SUM(
            CASE
                WHEN is_completed_purchase = TRUE THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate_percentage
FROM fraud.transactions
GROUP BY device_type
ORDER BY purchase_rate_percentage DESC;


-- ============================================
-- 15. TRAFFIC SOURCE PROFILE
-- ============================================

SELECT
    traffic_source,
    COUNT(*) AS transaction_count,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(
        SUM(
            CASE
                WHEN is_completed_purchase = TRUE THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate_percentage
FROM fraud.transactions
GROUP BY traffic_source
ORDER BY purchase_rate_percentage DESC;


-- ============================================
-- 16. DELIVERY OPTION PROFILE
-- ============================================

SELECT
    delivery_option,
    COUNT(*) AS transaction_count,
    ROUND(AVG(final_amount), 2) AS average_amount,
    ROUND(AVG(discount_percent), 2) AS average_discount
FROM fraud.transactions
GROUP BY delivery_option
ORDER BY transaction_count DESC;


-- ============================================
-- 17. RECOMMENDATION ACTION PROFILE
-- ============================================

SELECT
    recommendation_action,
    COUNT(*) AS transaction_count,
    ROUND(AVG(final_amount), 2) AS average_amount
FROM fraud.transactions
GROUP BY recommendation_action
ORDER BY transaction_count DESC;


-- ============================================
-- 18. EVENT SEQUENCE ANALYSIS
-- ============================================

SELECT
    event_sequence_order,
    COUNT(*) AS transaction_count,
    ROUND(AVG(final_amount), 2) AS average_amount
FROM fraud.transactions
GROUP BY event_sequence_order
ORDER BY event_sequence_order
LIMIT 20;


-- ============================================
-- 19. TRANSACTIONS BY MONTH
-- ============================================

SELECT
    DATE_TRUNC('month', event_timestamp) AS transaction_month,
    COUNT(*) AS transaction_count,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(SUM(final_amount), 2) AS total_transaction_value
FROM fraud.transactions
GROUP BY DATE_TRUNC('month', event_timestamp)
ORDER BY transaction_month;


-- ============================================
-- 20. TRANSACTIONS BY DAY
-- ============================================

SELECT
    event_timestamp::DATE AS transaction_date,
    COUNT(*) AS transaction_count,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases
FROM fraud.transactions
GROUP BY event_timestamp::DATE
ORDER BY transaction_date
LIMIT 20;


-- ============================================
-- 21. HIGH VALUE TRANSACTIONS
-- ============================================

SELECT
    transaction_id,
    user_id,
    product_id,
    final_amount,
    discount_percent,
    device_type,
    traffic_source,
    is_completed_purchase
FROM fraud.transactions
WHERE final_amount > 50000
ORDER BY final_amount DESC
LIMIT 20;


-- ============================================
-- 22. HIGH DISCOUNT TRANSACTIONS
-- ============================================

SELECT
    transaction_id,
    user_id,
    product_id,
    discount_percent,
    base_price,
    final_amount,
    is_completed_purchase
FROM fraud.transactions
WHERE discount_percent >= 60
ORDER BY discount_percent DESC
LIMIT 20;


-- ============================================
-- 23. USER + TRANSACTION PROFILE
-- ============================================

SELECT
    u.user_id,
    u.user_region,
    u.membership_type,
    u.customer_loyalty_score,
    u.purchase_frequency,
    u.average_order_value,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(
        CASE
            WHEN t.is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(AVG(t.final_amount), 2) AS average_transaction_amount
FROM fraud.users u
LEFT JOIN fraud.transactions t
    ON u.user_id = t.user_id
GROUP BY
    u.user_id,
    u.user_region,
    u.membership_type,
    u.customer_loyalty_score,
    u.purchase_frequency,
    u.average_order_value
ORDER BY transaction_count DESC
LIMIT 20;


-- ============================================
-- 24. PRODUCT + TRANSACTION PROFILE
-- ============================================

SELECT
    p.product_id,
    p.category_name,
    p.product_price,
    p.product_rating,
    p.stock_status,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(
        CASE
            WHEN t.is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(AVG(t.final_amount), 2) AS average_transaction_amount
FROM fraud.products p
LEFT JOIN fraud.transactions t
    ON p.product_id = t.product_id
GROUP BY
    p.product_id,
    p.category_name,
    p.product_price,
    p.product_rating,
    p.stock_status
ORDER BY transaction_count DESC
LIMIT 20;


-- ============================================
-- 25. MEMBERSHIP-WISE PURCHASE RATE
-- ============================================

SELECT
    u.membership_type,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(
        CASE
            WHEN t.is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(
        SUM(
            CASE
                WHEN t.is_completed_purchase = TRUE THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(COUNT(t.transaction_id), 0),
        2
    ) AS purchase_rate_percentage
FROM fraud.users u
INNER JOIN fraud.transactions t
    ON u.user_id = t.user_id
GROUP BY u.membership_type
ORDER BY purchase_rate_percentage DESC;


-- ============================================
-- 26. REGION-WISE PURCHASE RATE
-- ============================================

SELECT
    u.user_region,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(
        CASE
            WHEN t.is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(
        SUM(
            CASE
                WHEN t.is_completed_purchase = TRUE THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(COUNT(t.transaction_id), 0),
        2
    ) AS purchase_rate_percentage
FROM fraud.users u
INNER JOIN fraud.transactions t
    ON u.user_id = t.user_id
GROUP BY u.user_region
ORDER BY purchase_rate_percentage DESC;


-- ============================================
-- 27. USER TRANSACTION FREQUENCY
-- ============================================

SELECT
    user_id,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT session_id) AS session_count,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(AVG(final_amount), 2) AS average_transaction_amount
FROM fraud.transactions
GROUP BY user_id
HAVING COUNT(*) >= 5
ORDER BY transaction_count DESC
LIMIT 20;


-- ============================================
-- 28. SESSION ACTIVITY PROFILE
-- ============================================

SELECT
    session_id,
    user_id,
    COUNT(*) AS events_in_session,
    COUNT(DISTINCT product_id) AS products_viewed,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(SUM(final_amount), 2) AS session_value
FROM fraud.transactions
GROUP BY session_id, user_id
HAVING COUNT(*) >= 5
ORDER BY events_in_session DESC
LIMIT 20;


-- ============================================
-- 29. AMOUNT VS USER AVERAGE ORDER VALUE
-- ============================================

SELECT
    t.transaction_id,
    t.user_id,
    t.final_amount,
    u.average_order_value,
    ROUND(
        t.final_amount - u.average_order_value,
        2
    ) AS difference_from_user_aov,
    ROUND(
        t.final_amount /
        NULLIF(u.average_order_value, 0),
        2
    ) AS amount_to_aov_ratio
FROM fraud.transactions t
INNER JOIN fraud.users u
    ON t.user_id = u.user_id
ORDER BY amount_to_aov_ratio DESC
LIMIT 20;


-- ============================================
-- 30. PRODUCT PRICE VS FINAL AMOUNT
-- ============================================

SELECT
    t.transaction_id,
    t.product_id,
    p.product_price,
    t.base_price,
    t.final_amount,
    t.discount_percent,
    ROUND(
        p.product_price - t.final_amount,
        2
    ) AS product_price_difference
FROM fraud.transactions t
INNER JOIN fraud.products p
    ON t.product_id = p.product_id
ORDER BY product_price_difference DESC
LIMIT 20;


-- ============================================
-- 31. GROUPS WITH HIGH TRANSACTION ACTIVITY
-- ============================================

SELECT
    user_id,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT session_id) AS session_count
FROM fraud.transactions
GROUP BY user_id
HAVING COUNT(*) > 10
ORDER BY transaction_count DESC;


-- ============================================
-- 32. BASIC SUSPICIOUS-BEHAVIOUR SCREEN
-- ============================================

SELECT
    transaction_id,
    user_id,
    final_amount,
    discount_percent,
    event_sequence_order,
    time_spent_on_product_sec,
    device_type,
    traffic_source,
    CASE
        WHEN final_amount > 50000 THEN 'High Amount'
        WHEN discount_percent >= 60 THEN 'High Discount'
        WHEN event_sequence_order <= 2
             AND is_completed_purchase = TRUE
            THEN 'Rapid Purchase'
        ELSE 'Normal'
    END AS behaviour_flag
FROM fraud.transactions
WHERE
    final_amount > 50000
    OR discount_percent >= 60
    OR (
        event_sequence_order <= 2
        AND is_completed_purchase = TRUE
    )
ORDER BY final_amount DESC
LIMIT 50;


-- ============================================
-- 33. TOP TRANSACTION USERS
-- ============================================

SELECT
    user_id,
    COUNT(*) AS transaction_count,
    ROUND(SUM(final_amount), 2) AS total_transaction_value,
    ROUND(AVG(final_amount), 2) AS average_transaction_value
FROM fraud.transactions
GROUP BY user_id
ORDER BY total_transaction_value DESC
LIMIT 20;


-- ============================================
-- 34. TOP PRODUCTS BY TRANSACTION VALUE
-- ============================================

SELECT
    product_id,
    COUNT(*) AS transaction_count,
    ROUND(SUM(final_amount), 2) AS total_transaction_value,
    ROUND(AVG(final_amount), 2) AS average_transaction_value
FROM fraud.transactions
GROUP BY product_id
ORDER BY total_transaction_value DESC
LIMIT 20;


-- ============================================
-- 35. FINAL PROFILING SUMMARY
-- ============================================

SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT user_id) AS active_users,
    COUNT(DISTINCT product_id) AS active_products,
    COUNT(DISTINCT session_id) AS total_sessions,
    SUM(
        CASE
            WHEN is_completed_purchase = TRUE THEN 1
            ELSE 0
        END
    ) AS completed_purchases,
    ROUND(
        SUM(
            CASE
                WHEN is_completed_purchase = TRUE THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate,
    ROUND(AVG(final_amount), 2) AS average_transaction_amount,
    ROUND(AVG(discount_percent), 2) AS average_discount
FROM fraud.transactions;