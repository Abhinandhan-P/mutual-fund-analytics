from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# 1. Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"

engine = create_engine(f"sqlite:///{DB_PATH}")


# ============================================================
# 2. Load cleaned datasets
# ============================================================

nav_df = pd.read_csv(
    PROCESSED_DIR / "nav_history_cleaned.csv"
)

transactions_df = pd.read_csv(
    PROCESSED_DIR / "investor_transactions_cleaned.csv"
)

performance_df = pd.read_csv(
    PROCESSED_DIR / "scheme_performance_cleaned.csv"
)

fund_master_df = pd.read_csv(
    PROCESSED_DIR / "fund_master_cleaned.csv"
)

aum_df = pd.read_csv(
    PROCESSED_DIR / "aum_by_fund_house_cleaned.csv"
)


print("Cleaned datasets loaded successfully.")


# ============================================================
# 3. Prepare DIM_FUND
# ============================================================

dim_fund = fund_master_df[
    [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "plan",
        "risk_category"
    ]
].drop_duplicates(subset=["amfi_code"])


# ============================================================
# 4. Prepare DIM_DATE
# ============================================================

all_dates = pd.concat(
    [
        pd.to_datetime(nav_df["date"]),
        pd.to_datetime(transactions_df["transaction_date"]),
        pd.to_datetime(aum_df["date"])
    ]
)

date_range = pd.date_range(
    start=all_dates.min(),
    end=all_dates.max(),
    freq="D"
)

dim_date = pd.DataFrame({
    "date": date_range
})

dim_date["date"] = dim_date["date"].dt.strftime("%Y-%m-%d")
dim_date["year"] = pd.to_datetime(dim_date["date"]).dt.year
dim_date["month"] = pd.to_datetime(dim_date["date"]).dt.month
dim_date["quarter"] = pd.to_datetime(dim_date["date"]).dt.quarter
dim_date["month_name"] = pd.to_datetime(
    dim_date["date"]
).dt.month_name()
dim_date["day_of_week"] = pd.to_datetime(
    dim_date["date"]
).dt.day_name()


# ============================================================
# 5. Prepare FACT_NAV
# ============================================================

fact_nav = nav_df.copy()

fact_nav["date"] = pd.to_datetime(
    fact_nav["date"]
).dt.strftime("%Y-%m-%d")

fact_nav = fact_nav[
    ["amfi_code", "date", "nav"]
]


# ============================================================
# ============================================================
# 6. Prepare FACT_TRANSACTIONS
# ============================================================

fact_transactions = transactions_df.copy()

fact_transactions["transaction_date"] = pd.to_datetime(
    fact_transactions["transaction_date"]
).dt.strftime("%Y-%m-%d")

# Create a unique transaction ID because
# the source dataset does not contain one.
fact_transactions["transaction_id"] = (
    "TXN_" +
    fact_transactions.index.astype(str)
)

fact_transactions = fact_transactions[
    [
        "transaction_id",
        "investor_id",
        "amfi_code",
        "transaction_date",
        "transaction_type",
        "amount_inr",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "annual_income_lakh",
        "payment_mode",
        "kyc_status"
    ]
]

# ============================================================
# 7. Prepare FACT_PERFORMANCE
# ============================================================

fact_performance = performance_df[
    [
        "amfi_code",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade"
    ]
].copy()


# ============================================================
# ============================================================
# 8. Prepare FACT_AUM
# ============================================================

fact_aum = aum_df[
    [
        "fund_house",
        "date",
        "aum_lakh_crore",
        "aum_crore",
        "num_schemes"
    ]
].copy() 

fact_aum["date"] = pd.to_datetime(
    fact_aum["date"]
).dt.strftime("%Y-%m-%d")
# ============================================================
# 9. Load data into SQLite
# ============================================================

print("\nLoading data into SQLite...")

dim_fund.to_sql(
    "dim_fund",
    engine,
    if_exists="append",
    index=False
)

dim_date.to_sql(
    "dim_date",
    engine,
    if_exists="append",
    index=False
)

fact_nav.to_sql(
    "fact_nav",
    engine,
    if_exists="append",
    index=False
)

fact_transactions.to_sql(
    "fact_transactions",
    engine,
    if_exists="append",
    index=False
)

fact_performance.to_sql(
    "fact_performance",
    engine,
    if_exists="append",
    index=False
)

fact_aum.to_sql(
    "fact_aum",
    engine,
    if_exists="append",
    index=False
)


# ============================================================
# 10. Verify row counts
# ============================================================

print("\nDatabase row counts:")

tables = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_aum"
]

with engine.connect() as connection:

    for table in tables:

        result = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        )

        count = result.scalar()

        print(f"{table}: {count:,}")


print("\nRESULT: Database loading completed successfully.")