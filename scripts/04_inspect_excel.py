import pandas as pd
from pathlib import Path

# ---------------------------------------
# File paths
# ---------------------------------------

DATA_DIR = Path("data/raw")

FILES = {
    "Users": DATA_DIR / "Users_table.xlsx",
    "Products": DATA_DIR / "Products_table.xlsx",
    "Transactions": DATA_DIR / "Transactions_table.xlsx"
}


# ---------------------------------------
# Inspection function
# ---------------------------------------

def inspect_file(name, file_path):

    print("\n" + "=" * 70)
    print(f"{name.upper()} TABLE")
    print("=" * 70)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    df = pd.read_excel(file_path)

    print(f"\nRows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nUnique values for categorical columns:")

    categorical_columns = [
        "User_Region",
        "User_Age_Group",
        "Membership_Type",
        "Category_Name",
        "Stock_Status",
        "Event_Type",
        "Device_Type",
        "Traffic_Source",
        "Delivery_Option",
        "Recommendation_Action",
        "Is_Completed_Purchase"
    ]

    for column in categorical_columns:
        if column in df.columns:
            print(f"\n{column}:")
            print(df[column].dropna().unique()[:30])


# ---------------------------------------
# Inspect all files
# ---------------------------------------

for name, file_path in FILES.items():
    inspect_file(name, file_path)

print("\n" + "=" * 70)
print("EXCEL INSPECTION COMPLETED")
print("=" * 70)