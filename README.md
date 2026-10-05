# BDM Transaction Risk & Fraud Detection

A PostgreSQL-based project for identifying suspicious transaction patterns using SQL analytics, behavioural indicators, and an interactive Streamlit dashboard.

> **Note:** The system identifies transaction risk indicators, not confirmed fraud, because the dataset does not contain a verified fraud label.

---

## 📌 Project Overview

The project integrates three datasets:

* **Users** – customer demographics and purchasing behaviour
* **Products** – product, pricing and stock information
* **Transactions** – transaction events, amounts, discounts and behavioural data

The data is stored in PostgreSQL, analysed using SQL, and presented through a Streamlit dashboard.

---

## 🏗️ Architecture

```text
Excel Files
    ↓
Python + Pandas
    ↓
PostgreSQL
    ↓
SQL Analytics
    ↓
Risk Model
    ↓
PostgreSQL View + Materialized View
    ↓
Streamlit Dashboard
```

---

## 🔗 Entity Relationship Diagram

```text
┌──────────────────────┐
│        USERS         │
├──────────────────────┤
│ PK user_id           │
│ user_region          │
│ user_age_group       │
│ membership_type      │
│ customer_loyalty...  │
│ purchase_frequency   │
│ average_order_value  │
└──────────┬───────────┘
           │
           │ 1 : N
           │
           ▼
┌────────────────────────────┐
│       TRANSACTIONS         │
├────────────────────────────┤
│ PK transaction_id          │
│ session_id                 │
│ FK user_id                 │
│ FK product_id              │
│ event_timestamp            │
│ event_type                 │
│ device_type                │
│ traffic_source             │
│ discount_percent           │
│ final_amount               │
│ is_completed_purchase      │
└────────────┬───────────────┘
             │
             │ N : 1
             │
             ▼
┌──────────────────────┐
│      PRODUCTS        │
├──────────────────────┤
│ PK product_id        │
│ category_name        │
│ brand_id             │
│ product_price        │
│ product_rating       │
│ review_count         │
│ stock_status         │
└──────────────────────┘
```

### Relationships

```text
Users 1 ───────── N Transactions
Products 1 ────── N Transactions
```

---

## 📊 Dataset

| Table        |       Rows |
| ------------ | ---------: |
| Users        |      5,128 |
| Products     |      5,205 |
| Transactions |     12,000 |
| **Total**    | **22,328** |

---

## 🧠 PostgreSQL Concepts Used

The project applies core BDM/PostgreSQL concepts:

* Database schema and relational tables
* Primary keys & foreign keys
* `NOT NULL` and `CHECK` constraints
* `INSERT`, `UPDATE`, `DELETE`
* `WHERE`, `IN`, `BETWEEN`, `LIKE`
* `GROUP BY` & `HAVING`
* `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
* `INNER JOIN` & `LEFT JOIN`
* Subqueries
* CTEs
* Window functions

  * `LAG()`
  * `RANK()`
  * `COUNT() OVER()`
* Views
* Materialized views
* Indexes
* Transactions and data validation

---

## ⚠️ Risk Model

The project uses a **rule-based, multi-factor risk scoring model**. Each transaction is evaluated against several behavioural indicators.

| Indicator           | Condition                                      | Points |
| ------------------- | ---------------------------------------------- | -----: |
| Very high amount    | Amount/AOV ≥ 10×                               |    +40 |
| High amount         | Amount/AOV 5× to <10×                          |    +25 |
| Very high discount  | Discount ≥ 70%                                 |    +20 |
| High discount       | Discount 60% to <70%                           |    +10 |
| Large amount change | Difference from previous transaction ≥ ₹50,000 |    +20 |
| High activity       | User has ≥ 6 transactions                      |    +10 |
| Rapid purchase      | Purchase occurs at event sequence ≤ 2          |    +10 |

### How the score is calculated

The **Risk Score is the sum of applicable indicator points**.

However, the two tiered indicators are mutually exclusive:

* Amount/AOV contributes **either +40, +25, or 0**
* Discount contributes **either +20, +10, or 0**

The remaining indicators can contribute independently.

### Example

For a transaction with:

```text
Amount/AOV Ratio = 48.30×
Discount = 9.68%
Large previous-transaction change = Yes
High activity = No
Rapid purchase = No
```

The score is:

```text
Amount/AOV ≥ 10×             +40
Discount ≥ 60%                 +0
Large amount change           +20
High activity                  +0
Rapid purchase                 +0
                              ----
Risk Score                    60
```

Therefore:

```text
60 → High Risk
```

### Risk Levels

```text
0–29       Low Risk
30–49      Medium Risk
50–69      High Risk
70–100     Critical Risk
```

### Why a multi-factor model?

A single unusual behaviour does not automatically classify a transaction as high risk.

For example, a **70% discount alone contributes only 20 points**, keeping the transaction in the Low Risk range unless other risk indicators are also present.

This makes the model a **behaviour-based risk screening mechanism** rather than a simple single-condition fraud flag.

The model uses:

* `LAG()` to compare a transaction with the customer's previous transaction
* `COUNT() OVER()` to measure customer transaction activity
* `RANK()` for user activity analysis

---

## 👁️ PostgreSQL Views

### Transaction Risk View

```text
fraud.transaction_risk_view
```

Provides transaction-level:

* Risk Score
* Risk Level
* Risk Reason
* Behavioural indicators

### Materialized View

```text
fraud.transaction_risk_summary
```

Provides pre-aggregated:

* Risk-level counts
* Percentages
* Average risk scores
* Transaction values

---

## 📈 Dashboard

The Streamlit dashboard provides:

* Executive overview
* Risk distribution
* High-risk transactions
* User behaviour analysis
* Device and traffic-source analysis
* Product/category analysis
* Transaction-level investigation
* Interactive filters

### Example Filter

```text
Risk Level = High Risk
Device = Mobile
Traffic Source = Search Engine
```

This allows analysts to isolate specific transaction segments for investigation.

---

## 📸 Dashboard Screenshots

Add screenshots to a `screenshots/` folder:

```text
screenshots/
├── executive_overview.png
├── risk_analysis.png
├── high_risk_transactions.png
└── dashboard_filters.png
```

Then add:

```markdown
![Executive Overview](screenshots/executive_overview.png)

![Risk Analysis](screenshots/risk_analysis.png)

![High Risk Transactions](screenshots/high_risk_transactions.png)
```

---

## 🛠️ Technology Stack

**PostgreSQL • Python • Pandas • Psycopg2 • Streamlit • SQL • Excel • Git/GitHub**

---

## 📁 Project Structure

```text
BDM_Fraud_Detection/
├── data/raw/
├── scripts/
├── sql/
├── dashboard/
│   └── app.py
├── screenshots/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd BDM-Fraud-Detection
```

### 2. Create and activate environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create `.env`:

```env
DATABASE_URL="YOUR_POSTGRESQL_CONNECTION_STRING"
```

**Do not upload `.env` to GitHub.**

### 5. Run the setup scripts

```bash
python scripts/01_test_connection.py
python scripts/02_create_schema.py
python scripts/03_create_tables.py
python scripts/06_load_data.py
python scripts/07_run_validation.py
python scripts/10_build_risk_model.py
python scripts/11_create_indexes.py
python scripts/12_create_materialized_view.py
```

### 6. Launch dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📌 Key Results

* **12,000** transactions analysed
* **951** completed purchases
* **7.93%** purchase rate
* **13** High-Risk transactions
* **212** Medium-Risk transactions
* **11,775** Low-Risk transactions
* **0** Critical-Risk transactions

---

## ⚠️ Disclaimer

This is an academic **transaction-risk screening system**. Risk levels represent analytical indicators and should not be interpreted as confirmed fraud without further investigation.

---

### 👤 Business Data Management Project

**Focus:** PostgreSQL • SQL Analytics • Database Management • Transaction Risk Analysis • Business Dashboard
