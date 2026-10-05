import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check your .env file.")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS fraud.users (
    user_id VARCHAR(100) PRIMARY KEY,
    user_region VARCHAR(100),
    user_age_group VARCHAR(50),
    membership_type VARCHAR(50),
    customer_loyalty_score NUMERIC(10,2),
    purchase_frequency NUMERIC(10,2),
    average_order_value NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS fraud.products (
    product_id VARCHAR(100) PRIMARY KEY,
    category_name VARCHAR(150),
    brand_id VARCHAR(100),
    product_price NUMERIC(12,2),
    product_rating NUMERIC(4,2),
    review_count INT,
    stock_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS fraud.transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100),
    user_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP,
    event_type VARCHAR(50),
    event_sequence_order INT,
    device_type VARCHAR(50),
    traffic_source VARCHAR(100),
    discount_percent NUMERIC(6,2),
    delivery_option VARCHAR(100),
    time_spent_on_product_sec INT,
    recommendation_action VARCHAR(100),
    base_price NUMERIC(12,2),
    final_amount NUMERIC(12,2),
    is_completed_purchase BOOLEAN,

    CONSTRAINT fk_transaction_user
        FOREIGN KEY (user_id)
        REFERENCES fraud.users(user_id),

    CONSTRAINT fk_transaction_product
        FOREIGN KEY (product_id)
        REFERENCES fraud.products(product_id)
);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(CREATE_TABLES_SQL)
    conn.commit()

    print("All three tables created successfully!")

    cursor.close()
    conn.close()

except Exception as e:
    print("Error creating tables:")
    print(e)