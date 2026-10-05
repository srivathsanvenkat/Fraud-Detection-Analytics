import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = "data/raw"

USERS_FILE = os.path.join(DATA_DIR, "Users_table.xlsx")
PRODUCTS_FILE = os.path.join(DATA_DIR, "Products_table.xlsx")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "Transactions_table.xlsx")


# ============================================================
# Load Excel files
# ============================================================

print("Reading Excel files...")

users_df = pd.read_excel(USERS_FILE)
products_df = pd.read_excel(PRODUCTS_FILE)
transactions_df = pd.read_excel(TRANSACTIONS_FILE)

print(f"Users: {len(users_df):,} rows")
print(f"Products: {len(products_df):,} rows")
print(f"Transactions: {len(transactions_df):,} rows")


# ============================================================
# Data type conversions
# ============================================================

# Convert IDs to integer types
users_df["User_ID"] = users_df["User_ID"].astype("int64")

products_df["Product_ID"] = products_df["Product_ID"].astype("int64")
products_df["Brand_ID"] = products_df["Brand_ID"].astype("int64")

transactions_df["Session_ID"] = transactions_df["Session_ID"].astype("int64")
transactions_df["User_ID"] = transactions_df["User_ID"].astype("int64")
transactions_df["Product_ID"] = transactions_df["Product_ID"].astype("int64")

# Convert timestamp
transactions_df["Timestamp"] = pd.to_datetime(
    transactions_df["Timestamp"],
    errors="raise"
)

# Convert 0/1 to Boolean
transactions_df["Is_Completed_Purchase"] = (
    transactions_df["Is_Completed_Purchase"]
    .astype(int)
    .astype(bool)
)


# ============================================================
# Referential integrity validation
# ============================================================

print("\nValidating relationships...")

valid_user_ids = set(users_df["User_ID"])
valid_product_ids = set(products_df["Product_ID"])

invalid_users = transactions_df[
    ~transactions_df["User_ID"].isin(valid_user_ids)
]

invalid_products = transactions_df[
    ~transactions_df["Product_ID"].isin(valid_product_ids)
]

if len(invalid_users) > 0:
    raise ValueError(
        f"Found {len(invalid_users)} transactions with invalid User_ID."
    )

if len(invalid_products) > 0:
    raise ValueError(
        f"Found {len(invalid_products)} transactions with invalid Product_ID."
    )

print("User_ID validation: PASSED")
print("Product_ID validation: PASSED")


# ============================================================
# PostgreSQL connection
# ============================================================

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check your .env file.")

print("\nConnecting to PostgreSQL...")

conn = psycopg2.connect(DATABASE_URL)

try:

    cursor = conn.cursor()

    # ========================================================
    # Insert Users
    # ========================================================

    print("\nLoading Users...")

    users_sql = """
        INSERT INTO fraud.users (
            user_id,
            user_region,
            user_age_group,
            membership_type,
            customer_loyalty_score,
            purchase_frequency,
            average_order_value
        )
        VALUES %s
    """

    users_data = [
        (
            row.User_ID,
            row.User_Region,
            row.User_Age_Group,
            row.Membership_Type,
            row.Customer_Loyalty_Score,
            row.Purchase_Frequency,
            row.Average_Order_Value
        )
        for row in users_df.itertuples(index=False)
    ]

    execute_values(cursor, users_sql, users_data)

    print(f"Users loaded: {len(users_data):,}")


    # ========================================================
    # Insert Products
    # ========================================================

    print("\nLoading Products...")

    products_sql = """
        INSERT INTO fraud.products (
            product_id,
            category_name,
            brand_id,
            product_price,
            product_rating,
            review_count,
            stock_status
        )
        VALUES %s
    """

    products_data = [
        (
            row.Product_ID,
            row.Category_Name,
            row.Brand_ID,
            row.Product_Price,
            row.Product_Rating,
            row.Review_Count,
            row.Stock_Status
        )
        for row in products_df.itertuples(index=False)
    ]

    execute_values(cursor, products_sql, products_data)

    print(f"Products loaded: {len(products_data):,}")


    # ========================================================
    # Insert Transactions
    # ========================================================

    print("\nLoading Transactions...")

    transactions_sql = """
        INSERT INTO fraud.transactions (
            transaction_id,
            session_id,
            user_id,
            product_id,
            event_timestamp,
            event_type,
            event_sequence_order,
            device_type,
            traffic_source,
            discount_percent,
            delivery_option,
            time_spent_on_product_sec,
            recommendation_action,
            base_price,
            final_amount,
            is_completed_purchase
        )
        VALUES %s
    """

    transactions_data = [
        (
            row.Transaction_ID,
            row.Session_ID,
            row.User_ID,
            row.Product_ID,
            row.Timestamp,
            row.Event_Type,
            row.Event_Sequence_Order,
            row.Device_Type,
            row.Traffic_Source,
            row.Discount_Percent,
            row.Delivery_Option,
            row.Time_Spent_On_Product_sec,
            row.Recommendation_Action,
            row.Base_Price,
            row.Final_Amount,
            row.Is_Completed_Purchase
        )
        for row in transactions_df.itertuples(index=False)
    ]

    execute_values(
        cursor,
        transactions_sql,
        transactions_data,
        page_size=1000
    )

    print(f"Transactions loaded: {len(transactions_data):,}")


    # ========================================================
    # Commit
    # ========================================================

    conn.commit()

    print("\n============================================")
    print("DATA LOADING COMPLETED SUCCESSFULLY")
    print("============================================")


except Exception as e:

    conn.rollback()

    print("\nDATA LOADING FAILED")
    print("Transaction rolled back.")
    print("Error:", e)

    raise


finally:

    cursor.close()
    conn.close()

    print("Database connection closed.")