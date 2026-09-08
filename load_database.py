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

fund_master_df = pd.read_csv(
    PROCESSED_DIR / "fund_master_cleaned.csv"
)

nav_df = pd.read_csv(
    PROCESSED_DIR / "nav_history_cleaned.csv"
)

transactions_df = pd.read_csv(
    PROCESSED_DIR / "investor_transactions_cleaned.csv"
)

performance_df = pd.read_csv(
    PROCESSED_DIR / "scheme_performance_cleaned.csv"
)

aum_df = pd.read_csv(
    PROCESSED_DIR / "aum_by_fund_house_cleaned.csv"
)

sip_df = pd.read_csv(
    PROCESSED_DIR / "monthly_sip_inflows_cleaned.csv"
)

category_inflow_df = pd.read_csv(
    PROCESSED_DIR / "category_inflows_cleaned.csv"
)

folio_df = pd.read_csv(
    PROCESSED_DIR / "industry_folio_count_cleaned.csv"
)

portfolio_df = pd.read_csv(
    PROCESSED_DIR / "portfolio_holdings_cleaned.csv"
)

benchmark_df = pd.read_csv(
    PROCESSED_DIR / "benchmark_indices_cleaned.csv"
)

print("All 10 cleaned datasets loaded successfully.")


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
].drop_duplicates(
    subset=["amfi_code"]
)


# ============================================================
# 4. Prepare DIM_DATE
# ============================================================

all_dates = pd.concat(
    [
        pd.to_datetime(nav_df["date"]),
        pd.to_datetime(transactions_df["transaction_date"]),
        pd.to_datetime(aum_df["date"]),
        pd.to_datetime(benchmark_df["date"])
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

dim_date["date"] = dim_date["date"].dt.strftime(
    "%Y-%m-%d"
)

dim_date["year"] = pd.to_datetime(
    dim_date["date"]
).dt.year

dim_date["month"] = pd.to_datetime(
    dim_date["date"]
).dt.month

dim_date["quarter"] = pd.to_datetime(
    dim_date["date"]
).dt.quarter

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
    [
        "amfi_code",
        "date",
        "nav"
    ]
]


# ============================================================
# 6. Prepare FACT_TRANSACTIONS
# ============================================================

fact_transactions = transactions_df.copy()

fact_transactions["transaction_date"] = pd.to_datetime(
    fact_transactions["transaction_date"]
).dt.strftime("%Y-%m-%d")

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
# 9. Prepare FACT_SIP_INFLOW
# ============================================================

fact_sip_inflows = sip_df[
    [
        "month",
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct"
    ]
].copy()

fact_sip_inflows["month"] = pd.to_datetime(
    fact_sip_inflows["month"]
).dt.strftime("%Y-%m")


# ============================================================
# 10. Prepare FACT_CATEGORY_INFLOW
# ============================================================

fact_category_inflows = category_inflow_df[
    [
        "month",
        "category",
        "net_inflow_crore"
    ]
].copy()
fact_category_inflows = fact_category_inflows.rename(
    columns={
        "net_inflow_crore": "inflow_crore"
    }
)

fact_category_inflows["month"] = pd.to_datetime(
    fact_category_inflows["month"]
).dt.strftime("%Y-%m")


# ============================================================
# 11. Prepare FACT_FOLIO_COUNT
# ============================================================

fact_folio_count = folio_df[
    [
        "month",
        "total_folios_crore",
        "equity_folios_crore",
        "debt_folios_crore",
        "hybrid_folios_crore",
        "others_folios_crore"
    ]
].copy()

fact_folio_count["month"] = pd.to_datetime(
    fact_folio_count["month"]
).dt.strftime("%Y-%m")


# ============================================================
# 12. Prepare FACT_PORTFOLIO_HOLDINGS
# ============================================================

fact_portfolio_holdings = portfolio_df[
    [
        "amfi_code",
        "stock_symbol",
        "stock_name",
        "sector",
        "weight_pct",
        "market_value_cr",
        "current_price_inr",
        "portfolio_date"
    ]
].copy()

fact_portfolio_holdings["portfolio_date"] = pd.to_datetime(
    fact_portfolio_holdings["portfolio_date"]
).dt.strftime("%Y-%m-%d")


# ============================================================
# 13. Prepare FACT_BENCHMARK_INDICES
# ============================================================

fact_benchmark_indices = benchmark_df[
    [
        "date",
        "index_name",
        "close_value"
    ]
].copy()

fact_benchmark_indices["date"] = pd.to_datetime(
    fact_benchmark_indices["date"]
).dt.strftime("%Y-%m-%d")


# ============================================================
# 14. Create database tables from schema.sql
# ============================================================

print("\nCreating database schema...")

schema_path = BASE_DIR / "sql" / "schema.sql"

with open(schema_path, "r", encoding="utf-8") as file:
    schema_sql = file.read()

with engine.begin() as connection:
    connection.execute(text("PRAGMA foreign_keys = OFF"))

    # Drop existing tables so the database is rebuilt cleanly.
    tables_to_drop = [
        "fact_benchmark_indices",
        "fact_portfolio_holdings",
        "fact_folio_count",
        "fact_category_inflows",
        "fact_sip_inflows",
        "fact_aum",
        "fact_performance",
        "fact_transactions",
        "fact_nav",
        "dim_date",
        "dim_fund"
    ]

    for table in tables_to_drop:
        connection.execute(
            text(f"DROP TABLE IF EXISTS {table}")
        )

    # SQLite executes the schema statements individually.
    for statement in schema_sql.split(";"):
        statement = statement.strip()

        if statement:
            connection.execute(text(statement))

    connection.execute(text("PRAGMA foreign_keys = ON"))

print("Database schema created successfully.")


# ============================================================
# 15. Load data into SQLite
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

fact_sip_inflows.to_sql(
    "fact_sip_inflows",
    engine,
    if_exists="append",
    index=False
)

fact_category_inflows.to_sql(
    "fact_category_inflows",
    engine,
    if_exists="append",
    index=False
)

fact_folio_count.to_sql(
    "fact_folio_count",
    engine,
    if_exists="append",
    index=False
)

fact_portfolio_holdings.to_sql(
    "fact_portfolio_holdings",
    engine,
    if_exists="append",
    index=False
)

fact_benchmark_indices.to_sql(
    "fact_benchmark_indices",
    engine,
    if_exists="append",
    index=False
)


# ============================================================
# 16. Verify row counts
# ============================================================

print("\nDatabase row counts:")

tables = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_aum",
    "fact_sip_inflows",
    "fact_category_inflows",
    "fact_folio_count",
    "fact_portfolio_holdings",
    "fact_benchmark_indices"
]

with engine.connect() as connection:

    for table in tables:

        result = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        )

        count = result.scalar()

        print(f"{table}: {count:,}")


print("\nRESULT: Database loading completed successfully.")