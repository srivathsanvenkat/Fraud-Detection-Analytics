import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check your .env file.")

SQL = """
DROP TABLE IF EXISTS fraud.transactions CASCADE;
DROP TABLE IF EXISTS fraud.products CASCADE;
DROP TABLE IF EXISTS fraud.users CASCADE;

CREATE TABLE fraud.users (
    user_id BIGINT PRIMARY KEY,
    user_region VARCHAR(50) NOT NULL,
    user_age_group VARCHAR(20) NOT NULL,
    membership_type VARCHAR(30) NOT NULL,
    customer_loyalty_score NUMERIC(10,2) NOT NULL,
    purchase_frequency NUMERIC(10,3) NOT NULL,
    average_order_value NUMERIC(12,2) NOT NULL,

    CONSTRAINT chk_loyalty_score
        CHECK (customer_loyalty_score >= 0),

    CONSTRAINT chk_purchase_frequency
        CHECK (purchase_frequency >= 0),

    CONSTRAINT chk_average_order_value
        CHECK (average_order_value >= 0)
);

CREATE TABLE fraud.products (
    product_id BIGINT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    brand_id BIGINT NOT NULL,
    product_price NUMERIC(12,2) NOT NULL,
    product_rating NUMERIC(4,2) NOT NULL,
    review_count INT NOT NULL,
    stock_status VARCHAR(30) NOT NULL,

    CONSTRAINT chk_product_price
        CHECK (product_price >= 0),

    CONSTRAINT chk_product_rating
        CHECK (product_rating >= 0 AND product_rating <= 5),

    CONSTRAINT chk_review_count
        CHECK (review_count >= 0)
);

CREATE TABLE fraud.transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    session_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_sequence_order INT NOT NULL,
    device_type VARCHAR(30) NOT NULL,
    traffic_source VARCHAR(50) NOT NULL,
    discount_percent NUMERIC(6,2) NOT NULL,
    delivery_option VARCHAR(30) NOT NULL,
    time_spent_on_product_sec INT NOT NULL,
    recommendation_action VARCHAR(50) NOT NULL,
    base_price NUMERIC(12,2) NOT NULL,
    final_amount NUMERIC(12,2) NOT NULL,
    is_completed_purchase BOOLEAN NOT NULL,

    CONSTRAINT fk_transaction_user
        FOREIGN KEY (user_id)
        REFERENCES fraud.users(user_id),

    CONSTRAINT fk_transaction_product
        FOREIGN KEY (product_id)
        REFERENCES fraud.products(product_id),

    CONSTRAINT chk_discount_percent
        CHECK (discount_percent >= 0 AND discount_percent <= 100),

    CONSTRAINT chk_time_spent
        CHECK (time_spent_on_product_sec >= 0),

    CONSTRAINT chk_base_price
        CHECK (base_price >= 0),

    CONSTRAINT chk_final_amount
        CHECK (final_amount >= 0),

    CONSTRAINT chk_event_sequence
        CHECK (event_sequence_order >= 0)
);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(SQL)
    conn.commit()

    print("Tables recreated successfully.")

    cursor.close()
    conn.close()

except Exception as e:
    print("Error:", e)
    raise