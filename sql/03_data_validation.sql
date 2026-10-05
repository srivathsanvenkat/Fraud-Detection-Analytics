-- ============================================
-- BDM Fraud Detection Project
-- Data Validation & Quality Checks
-- ============================================

-- ============================================
-- 1. ROW COUNTS
-- ============================================

SELECT 'Users' AS table_name, COUNT(*) AS row_count
FROM fraud.users

UNION ALL

SELECT 'Products', COUNT(*)
FROM fraud.products

UNION ALL

SELECT 'Transactions', COUNT(*)
FROM fraud.transactions;


-- ============================================
-- 2. DUPLICATE PRIMARY KEY CHECKS
-- ============================================

-- Users
SELECT
    user_id,
    COUNT(*) AS occurrences
FROM fraud.users
GROUP BY user_id
HAVING COUNT(*) > 1;


-- Products
SELECT
    product_id,
    COUNT(*) AS occurrences
FROM fraud.products
GROUP BY product_id
HAVING COUNT(*) > 1;


-- Transactions
SELECT
    transaction_id,
    COUNT(*) AS occurrences
FROM fraud.transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- ============================================
-- 3. NULL CHECK - USERS
-- ============================================

SELECT
    COUNT(*) FILTER (WHERE user_id IS NULL) AS null_user_id,
    COUNT(*) FILTER (WHERE user_region IS NULL) AS null_region,
    COUNT(*) FILTER (WHERE user_age_group IS NULL) AS null_age_group,
    COUNT(*) FILTER (WHERE membership_type IS NULL) AS null_membership,
    COUNT(*) FILTER (WHERE customer_loyalty_score IS NULL) AS null_loyalty_score,
    COUNT(*) FILTER (WHERE purchase_frequency IS NULL) AS null_purchase_frequency,
    COUNT(*) FILTER (WHERE average_order_value IS NULL) AS null_aov
FROM fraud.users;


-- ============================================
-- 4. NULL CHECK - PRODUCTS
-- ============================================

SELECT
    COUNT(*) FILTER (WHERE product_id IS NULL) AS null_product_id,
    COUNT(*) FILTER (WHERE category_name IS NULL) AS null_category,
    COUNT(*) FILTER (WHERE brand_id IS NULL) AS null_brand_id,
    COUNT(*) FILTER (WHERE product_price IS NULL) AS null_product_price,
    COUNT(*) FILTER (WHERE product_rating IS NULL) AS null_product_rating,
    COUNT(*) FILTER (WHERE review_count IS NULL) AS null_review_count,
    COUNT(*) FILTER (WHERE stock_status IS NULL) AS null_stock_status
FROM fraud.products;


-- ============================================
-- 5. NULL CHECK - TRANSACTIONS
-- ============================================

SELECT
    COUNT(*) FILTER (WHERE transaction_id IS NULL) AS null_transaction_id,
    COUNT(*) FILTER (WHERE session_id IS NULL) AS null_session_id,
    COUNT(*) FILTER (WHERE user_id IS NULL) AS null_user_id,
    COUNT(*) FILTER (WHERE product_id IS NULL) AS null_product_id,
    COUNT(*) FILTER (WHERE event_timestamp IS NULL) AS null_timestamp,
    COUNT(*) FILTER (WHERE event_type IS NULL) AS null_event_type,
    COUNT(*) FILTER (WHERE event_sequence_order IS NULL) AS null_sequence,
    COUNT(*) FILTER (WHERE device_type IS NULL) AS null_device,
    COUNT(*) FILTER (WHERE traffic_source IS NULL) AS null_traffic_source,
    COUNT(*) FILTER (WHERE discount_percent IS NULL) AS null_discount,
    COUNT(*) FILTER (WHERE delivery_option IS NULL) AS null_delivery,
    COUNT(*) FILTER (WHERE time_spent_on_product_sec IS NULL) AS null_time_spent,
    COUNT(*) FILTER (WHERE recommendation_action IS NULL) AS null_recommendation,
    COUNT(*) FILTER (WHERE base_price IS NULL) AS null_base_price,
    COUNT(*) FILTER (WHERE final_amount IS NULL) AS null_final_amount,
    COUNT(*) FILTER (WHERE is_completed_purchase IS NULL) AS null_purchase_flag
FROM fraud.transactions;


-- ============================================
-- 6. REFERENTIAL INTEGRITY - USER
-- ============================================

SELECT
    COUNT(*) AS orphan_transactions
FROM fraud.transactions t
LEFT JOIN fraud.users u
    ON t.user_id = u.user_id
WHERE u.user_id IS NULL;


-- ============================================
-- 7. REFERENTIAL INTEGRITY - PRODUCT
-- ============================================

SELECT
    COUNT(*) AS orphan_transactions
FROM fraud.transactions t
LEFT JOIN fraud.products p
    ON t.product_id = p.product_id
WHERE p.product_id IS NULL;


-- ============================================
-- 8. USER ID VALIDATION
-- ============================================

SELECT *
FROM fraud.users
WHERE user_id <= 0;


-- ============================================
-- 9. PRODUCT ID VALIDATION
-- ============================================

SELECT *
FROM fraud.products
WHERE product_id <= 0;


-- ============================================
-- 10. BRAND ID VALIDATION
-- ============================================

SELECT *
FROM fraud.products
WHERE brand_id <= 0;


-- ============================================
-- 11. LOYALTY SCORE VALIDATION
-- ============================================

SELECT *
FROM fraud.users
WHERE customer_loyalty_score < 0;


-- ============================================
-- 12. PURCHASE FREQUENCY VALIDATION
-- ============================================

SELECT *
FROM fraud.users
WHERE purchase_frequency < 0;


-- ============================================
-- 13. AVERAGE ORDER VALUE VALIDATION
-- ============================================

SELECT *
FROM fraud.users
WHERE average_order_value < 0;


-- ============================================
-- 14. PRODUCT PRICE VALIDATION
-- ============================================

SELECT *
FROM fraud.products
WHERE product_price < 0;


-- ============================================
-- 15. PRODUCT RATING RANGE CHECK
-- ============================================

SELECT *
FROM fraud.products
WHERE product_rating < 0
   OR product_rating > 5;


-- ============================================
-- 16. REVIEW COUNT VALIDATION
-- ============================================

SELECT *
FROM fraud.products
WHERE review_count < 0;


-- ============================================
-- 17. DISCOUNT RANGE CHECK
-- ============================================

SELECT *
FROM fraud.transactions
WHERE discount_percent < 0
   OR discount_percent > 100;


-- ============================================
-- 18. TIME SPENT VALIDATION
-- ============================================

SELECT *
FROM fraud.transactions
WHERE time_spent_on_product_sec < 0;


-- ============================================
-- 19. BASE PRICE VALIDATION
-- ============================================

SELECT *
FROM fraud.transactions
WHERE base_price < 0;


-- ============================================
-- 20. FINAL AMOUNT VALIDATION
-- ============================================

SELECT *
FROM fraud.transactions
WHERE final_amount < 0;


-- ============================================
-- 21. EVENT SEQUENCE VALIDATION
-- ============================================

SELECT *
FROM fraud.transactions
WHERE event_sequence_order < 0;


-- ============================================
-- 22. TRANSACTION TIMESTAMP RANGE
-- ============================================

SELECT
    MIN(event_timestamp) AS earliest_transaction,
    MAX(event_timestamp) AS latest_transaction
FROM fraud.transactions;


-- ============================================
-- 23. TRANSACTION TIMESTAMP VALIDATION
-- ============================================

SELECT *
FROM fraud.transactions
WHERE event_timestamp > CURRENT_TIMESTAMP;


-- ============================================
-- 24. PURCHASE FLAG DISTRIBUTION
-- ============================================

SELECT
    is_completed_purchase,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY is_completed_purchase
ORDER BY is_completed_purchase;


-- ============================================
-- 25. EVENT TYPE DISTRIBUTION
-- ============================================

SELECT
    event_type,
    COUNT(*) AS event_count
FROM fraud.transactions
GROUP BY event_type
ORDER BY event_count DESC;


-- ============================================
-- 26. DEVICE TYPE DISTRIBUTION
-- ============================================

SELECT
    device_type,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY device_type
ORDER BY transaction_count DESC;


-- ============================================
-- 27. TRAFFIC SOURCE DISTRIBUTION
-- ============================================

SELECT
    traffic_source,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY traffic_source
ORDER BY transaction_count DESC;


-- ============================================
-- 28. DELIVERY OPTION DISTRIBUTION
-- ============================================

SELECT
    delivery_option,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY delivery_option
ORDER BY transaction_count DESC;


-- ============================================
-- 29. RECOMMENDATION ACTION DISTRIBUTION
-- ============================================

SELECT
    recommendation_action,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY recommendation_action
ORDER BY transaction_count DESC;


-- ============================================
-- 30. USER REGION DISTRIBUTION
-- ============================================

SELECT
    user_region,
    COUNT(*) AS user_count
FROM fraud.users
GROUP BY user_region
ORDER BY user_count DESC;


-- ============================================
-- 31. AGE GROUP DISTRIBUTION
-- ============================================

SELECT
    user_age_group,
    COUNT(*) AS user_count
FROM fraud.users
GROUP BY user_age_group
ORDER BY user_count DESC;


-- ============================================
-- 32. MEMBERSHIP TYPE DISTRIBUTION
-- ============================================

SELECT
    membership_type,
    COUNT(*) AS user_count
FROM fraud.users
GROUP BY membership_type
ORDER BY user_count DESC;


-- ============================================
-- 33. PRODUCT CATEGORY DISTRIBUTION
-- ============================================

SELECT
    category_name,
    COUNT(*) AS product_count
FROM fraud.products
GROUP BY category_name
ORDER BY product_count DESC;


-- ============================================
-- 34. STOCK STATUS DISTRIBUTION
-- ============================================

SELECT
    stock_status,
    COUNT(*) AS product_count
FROM fraud.products
GROUP BY stock_status
ORDER BY product_count DESC;


-- ============================================
-- 35. EVENT SEQUENCE SUMMARY
-- ============================================

SELECT
    MIN(event_sequence_order) AS minimum_sequence,
    MAX(event_sequence_order) AS maximum_sequence,
    ROUND(AVG(event_sequence_order), 2) AS average_sequence
FROM fraud.transactions;


-- ============================================
-- 36. TRANSACTION AMOUNT SUMMARY
-- ============================================

SELECT
    COUNT(*) AS transaction_count,
    ROUND(MIN(base_price), 2) AS minimum_base_price,
    ROUND(MAX(base_price), 2) AS maximum_base_price,
    ROUND(AVG(base_price), 2) AS average_base_price,
    ROUND(MIN(final_amount), 2) AS minimum_final_amount,
    ROUND(MAX(final_amount), 2) AS maximum_final_amount,
    ROUND(AVG(final_amount), 2) AS average_final_amount
FROM fraud.transactions;


-- ============================================
-- 37. DISCOUNT SUMMARY
-- ============================================

SELECT
    ROUND(MIN(discount_percent), 2) AS minimum_discount,
    ROUND(MAX(discount_percent), 2) AS maximum_discount,
    ROUND(AVG(discount_percent), 2) AS average_discount
FROM fraud.transactions;


-- ============================================
-- 38. DISCOUNT CONSISTENCY CHECK
-- ============================================

SELECT
    transaction_id,
    base_price,
    discount_percent,
    final_amount,
    ROUND(
        base_price * (1 - discount_percent / 100),
        2
    ) AS expected_amount,
    ROUND(
        final_amount -
        (base_price * (1 - discount_percent / 100)),
        2
    ) AS amount_difference
FROM fraud.transactions
ORDER BY ABS(
    final_amount -
    (base_price * (1 - discount_percent / 100))
) DESC
LIMIT 20;


-- ============================================
-- 39. DISCOUNT CONSISTENCY SUMMARY
-- ============================================

SELECT
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE ABS(
            final_amount -
            (base_price * (1 - discount_percent / 100))
        ) <= 0.01
    ) AS consistent_transactions,
    COUNT(*) FILTER (
        WHERE ABS(
            final_amount -
            (base_price * (1 - discount_percent / 100))
        ) > 0.01
    ) AS inconsistent_transactions
FROM fraud.transactions;


-- ============================================
-- 40. FINAL AMOUNT GREATER THAN BASE PRICE
-- ============================================

SELECT
    transaction_id,
    base_price,
    discount_percent,
    final_amount
FROM fraud.transactions
WHERE final_amount > base_price
ORDER BY (final_amount - base_price) DESC;


-- ============================================
-- 41. ZERO VALUE TRANSACTIONS
-- ============================================

SELECT
    COUNT(*) AS zero_amount_transactions
FROM fraud.transactions
WHERE final_amount = 0;


-- ============================================
-- 42. TRANSACTIONS BY USER
-- ============================================

SELECT
    user_id,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY user_id
ORDER BY transaction_count DESC
LIMIT 20;


-- ============================================
-- 43. TRANSACTIONS BY SESSION
-- ============================================

SELECT
    session_id,
    COUNT(*) AS event_count
FROM fraud.transactions
GROUP BY session_id
ORDER BY event_count DESC
LIMIT 20;


-- ============================================
-- 44. USERS WITH MULTIPLE SESSIONS
-- ============================================

SELECT
    user_id,
    COUNT(DISTINCT session_id) AS session_count
FROM fraud.transactions
GROUP BY user_id
ORDER BY session_count DESC
LIMIT 20;


-- ============================================
-- 45. USERS WITH MULTIPLE PURCHASES
-- ============================================

SELECT
    user_id,
    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS completed_purchases
FROM fraud.transactions
GROUP BY user_id
HAVING COUNT(*) FILTER (
    WHERE is_completed_purchase = TRUE
) > 1
ORDER BY completed_purchases DESC
LIMIT 20;


-- ============================================
-- 46. PURCHASE EVENTS VS PURCHASE FLAG
-- ============================================

SELECT
    event_type,
    is_completed_purchase,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY
    event_type,
    is_completed_purchase
ORDER BY
    event_type,
    is_completed_purchase;


-- ============================================
-- 47. PURCHASE EVENT CONSISTENCY
-- ============================================

SELECT
    COUNT(*) AS inconsistent_purchase_events
FROM fraud.transactions
WHERE
    (
        event_type = 'Purchase'
        AND is_completed_purchase = FALSE
    )
    OR
    (
        event_type <> 'Purchase'
        AND is_completed_purchase = TRUE
    );


-- ============================================
-- 48. RECOMMENDATION VS EVENT CONSISTENCY
-- ============================================

SELECT
    recommendation_action,
    event_type,
    COUNT(*) AS transaction_count
FROM fraud.transactions
GROUP BY
    recommendation_action,
    event_type
ORDER BY
    recommendation_action,
    transaction_count DESC;


-- ============================================
-- 49. DEVICE VS PURCHASE RATE
-- ============================================

SELECT
    device_type,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS completed_purchases,
    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate_percent
FROM fraud.transactions
GROUP BY device_type
ORDER BY purchase_rate_percent DESC;


-- ============================================
-- 50. TRAFFIC SOURCE VS PURCHASE RATE
-- ============================================

SELECT
    traffic_source,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE is_completed_purchase = TRUE
    ) AS completed_purchases,
    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE is_completed_purchase = TRUE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate_percent
FROM fraud.transactions
GROUP BY traffic_source
ORDER BY purchase_rate_percent DESC;


-- ============================================
-- 51. MEMBERSHIP TYPE VS PURCHASE RATE
-- ============================================

SELECT
    u.membership_type,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE t.is_completed_purchase = TRUE
    ) AS completed_purchases,
    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE t.is_completed_purchase = TRUE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS purchase_rate_percent
FROM fraud.transactions t
JOIN fraud.users u
    ON t.user_id = u.user_id
GROUP BY u.membership_type
ORDER BY purchase_rate_percent DESC;


-- ============================================
-- 52. USER TRANSACTION VALUE VS AVERAGE ORDER VALUE
-- ============================================

SELECT
    t.transaction_id,
    t.user_id,
    t.final_amount,
    u.average_order_value,
    ROUND(
        t.final_amount / NULLIF(u.average_order_value, 0),
        2
    ) AS amount_to_user_aov_ratio
FROM fraud.transactions t
JOIN fraud.users u
    ON t.user_id = u.user_id
ORDER BY amount_to_user_aov_ratio DESC
LIMIT 20;


-- ============================================
-- 53. EXTREME TRANSACTION AMOUNTS
-- ============================================

SELECT
    transaction_id,
    user_id,
    product_id,
    final_amount,
    event_timestamp
FROM fraud.transactions
ORDER BY final_amount DESC
LIMIT 20;


-- ============================================
-- 54. EXTREME DISCOUNT TRANSACTIONS
-- ============================================

SELECT
    transaction_id,
    user_id,
    product_id,
    base_price,
    discount_percent,
    final_amount
FROM fraud.transactions
ORDER BY discount_percent DESC
LIMIT 20;


-- ============================================
-- 55. EXTREME TIME-SPENT TRANSACTIONS
-- ============================================

SELECT
    transaction_id,
    user_id,
    product_id,
    time_spent_on_product_sec,
    event_type
FROM fraud.transactions
ORDER BY time_spent_on_product_sec DESC
LIMIT 20;


-- ============================================
-- 56. BASIC DATA QUALITY SUMMARY
-- ============================================

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


-- ============================================
-- 57. TRANSACTION COVERAGE
-- ============================================

SELECT
    ROUND(
        100.0 *
        COUNT(DISTINCT t.user_id)
        / NULLIF((SELECT COUNT(*) FROM fraud.users), 0),
        2
    ) AS users_with_transactions_percent,

    ROUND(
        100.0 *
        COUNT(DISTINCT t.product_id)
        / NULLIF((SELECT COUNT(*) FROM fraud.products), 0),
        2
    ) AS products_with_transactions_percent
FROM fraud.transactions t;


-- ============================================
-- 58. USERS WITH NO TRANSACTIONS
-- ============================================

SELECT
    u.user_id,
    u.membership_type,
    u.average_order_value
FROM fraud.users u
LEFT JOIN fraud.transactions t
    ON u.user_id = t.user_id
WHERE t.user_id IS NULL
ORDER BY u.user_id;


-- ============================================
-- 59. PRODUCTS WITH NO TRANSACTIONS
-- ============================================

SELECT
    p.product_id,
    p.category_name,
    p.product_price,
    p.stock_status
FROM fraud.products p
LEFT JOIN fraud.transactions t
    ON p.product_id = t.product_id
WHERE t.product_id IS NULL
ORDER BY p.product_id;


-- ============================================
-- 60. FINAL VALIDATION STATUS
-- ============================================

SELECT
    'Users' AS table_name,
    COUNT(*) AS rows_loaded
FROM fraud.users

UNION ALL

SELECT
    'Products',
    COUNT(*)
FROM fraud.products

UNION ALL

SELECT
    'Transactions',
    COUNT(*)
FROM fraud.transactions;