-- ============================================
-- BDM Fraud Detection Project
-- Stage 6 - Materialized View
-- ============================================

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