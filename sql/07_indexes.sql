-- ============================================
-- BDM Fraud Detection Project
-- Stage 5 - Database Indexes
-- ============================================

-- User-based transaction analysis
CREATE INDEX IF NOT EXISTS idx_transactions_user_id
ON fraud.transactions(user_id);

-- Product-based transaction analysis
CREATE INDEX IF NOT EXISTS idx_transactions_product_id
ON fraud.transactions(product_id);

-- Timestamp-based analysis
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
ON fraud.transactions(event_timestamp);

-- Purchase filtering
CREATE INDEX IF NOT EXISTS idx_transactions_purchase
ON fraud.transactions(is_completed_purchase);

-- Event type analysis
CREATE INDEX IF NOT EXISTS idx_transactions_event_type
ON fraud.transactions(event_type);

-- User activity and previous transaction analysis
CREATE INDEX IF NOT EXISTS idx_transactions_user_timestamp
ON fraud.transactions(user_id, event_timestamp);