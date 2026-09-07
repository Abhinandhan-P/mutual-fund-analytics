from pathlib import Path
import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Create processed folder if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Data cleaning pipeline started.")
print(f"Raw data folder: {RAW_DIR}")
print(f"Processed data folder: {PROCESSED_DIR}")# ============================================================
# 1. Load NAV History
# ============================================================

nav_file = next(RAW_DIR.glob("*02_nav_history.csv"))

nav_df = pd.read_csv(nav_file)

print("\nNAV History loaded successfully.")
print(f"File: {nav_file.name}")
print(f"Rows: {len(nav_df):,}")
print(f"Columns: {list(nav_df.columns)}")

print("\nFirst 5 rows:")
print(nav_df.head())

print("\nData types:")
print(nav_df.dtypes)

print("\nMissing values:")
print(nav_df.isnull().sum())
# ============================================================
# 2. Convert NAV date to datetime
# ============================================================

nav_df["date"] = pd.to_datetime(nav_df["date"])

print("\nDate conversion completed.")
print(f"Date data type: {nav_df['date'].dtype}")
print(f"Minimum date: {nav_df['date'].min().date()}")
print(f"Maximum date: {nav_df['date'].max().date()}")
# ============================================================
# 3. Sort NAV History
# ============================================================

nav_df = nav_df.sort_values(
    by=["amfi_code", "date"]
).reset_index(drop=True)

print("\nNAV sorting completed.")
print("\nFirst 10 rows after sorting:")
print(nav_df.head(10))

print("\nLast 10 rows after sorting:")
print(nav_df.tail(10))
# ============================================================
# 4. Check for duplicate NAV records
# ============================================================

duplicate_count = nav_df.duplicated(
    subset=["amfi_code", "date"]
).sum()

print("\nDuplicate NAV records check:")
print(f"Duplicate (amfi_code, date) records: {duplicate_count:,}")

if duplicate_count > 0:
    print("Duplicates found. They will be removed.")
else:
    print("No duplicate NAV records found.")
    # ============================================================
# 5. Validate NAV values
# ============================================================

invalid_nav_count = (nav_df["nav"] <= 0).sum()

print("\nNAV value validation:")
print(f"NAV values <= 0: {invalid_nav_count:,}")

if invalid_nav_count == 0:
    print("All NAV values are greater than 0.")
else:
    print("Invalid NAV values found. Please review them.")
    # ============================================================
# 6. Check date gaps in NAV history
# ============================================================

nav_df["date_gap"] = (
    nav_df.groupby("amfi_code")["date"]
    .diff()
    .dt.days
)

gap_summary = nav_df["date_gap"].value_counts().sort_index()

print("\nNAV date gap summary:")
print(gap_summary)

print("\nLargest date gaps:")
print(
    nav_df[nav_df["date_gap"] > 1]
    [["amfi_code", "date", "date_gap"]]
    .head(20)
)
# ============================================================
# 7. Remove temporary date gap column
# ============================================================

nav_df = nav_df.drop(columns=["date_gap"])

print("\nTemporary date_gap column removed.")
print(f"Current columns: {list(nav_df.columns)}")
# ============================================================
# ============================================================
# 8. Reindex each fund to a complete daily date range
#    and forward-fill NAV for non-trading days
# ============================================================

def reindex_fund(group):
    amfi_code = group.name

    group = group.set_index("date")

    full_dates = pd.date_range(
        start=group.index.min(),
        end=group.index.max(),
        freq="D"
    )

    group = group.reindex(full_dates)

    group["amfi_code"] = amfi_code
    group["nav"] = group["nav"].ffill()

    group.index.name = "date"

    return group.reset_index()


nav_df = (
    nav_df.groupby("amfi_code", group_keys=False)
    .apply(reindex_fund)
    .reset_index(drop=True)
)

print("\nCalendar reindexing and NAV forward-fill completed.")
print(f"Rows before reindexing: 46,000")
print(f"Rows after reindexing: {len(nav_df):,}")

print("\nMissing values after forward-fill:")
print(nav_df.isnull().sum())
# ============================================================
# 9. Verify weekend forward-fill
# ============================================================

sample_code = nav_df["amfi_code"].iloc[0]

sample_nav = nav_df[
    nav_df["amfi_code"] == sample_code
].head(10)

print("\nSample NAV after calendar reindexing:")
print(sample_nav)

print("\nWeekend records in sample:")
print(
    sample_nav[
        sample_nav["date"].dt.dayofweek >= 5
    ]
)
# ============================================================
# 10. Final sort of cleaned NAV data
# ============================================================

nav_df = nav_df.sort_values(
    by=["amfi_code", "date"]
).reset_index(drop=True)

print("\nFinal NAV sorting completed.")
print(f"Final row count: {len(nav_df):,}")
print(f"Final columns: {list(nav_df.columns)}")
# ============================================================
# 11. Standardize NAV column order
# ============================================================

nav_df = nav_df[["amfi_code", "date", "nav"]]

print("\nNAV column order standardized.")
print(f"Final columns: {list(nav_df.columns)}")
# ============================================================
# 12. Final NAV quality validation
# ============================================================

print("\nFinal NAV quality check:")

print(f"Total rows: {len(nav_df):,}")
print(f"Unique AMFI codes: {nav_df['amfi_code'].nunique():,}")
print(f"Duplicate records: {nav_df.duplicated(['amfi_code', 'date']).sum():,}")
print(f"Missing AMFI codes: {nav_df['amfi_code'].isna().sum():,}")
print(f"Missing dates: {nav_df['date'].isna().sum():,}")
print(f"Missing NAVs: {nav_df['nav'].isna().sum():,}")
print(f"NAV values <= 0: {(nav_df['nav'] <= 0).sum():,}")

if (
    nav_df["amfi_code"].isna().sum() == 0
    and nav_df["date"].isna().sum() == 0
    and nav_df["nav"].isna().sum() == 0
    and nav_df.duplicated(["amfi_code", "date"]).sum() == 0
    and (nav_df["nav"] <= 0).sum() == 0
):
    print("RESULT: PASS - NAV data is clean and valid.")
else:
    print("RESULT: FAIL - Please review the NAV data.")
    # ============================================================
# 13. Save cleaned NAV history
# ============================================================

nav_output_file = PROCESSED_DIR / "nav_history_cleaned.csv"

nav_df.to_csv(
    nav_output_file,
    index=False
)

print("\nCleaned NAV history saved successfully.")
print(f"Output file: {nav_output_file}")
# ============================================================
# 14. Verify saved NAV CSV
# ============================================================

nav_check = pd.read_csv(nav_output_file)

print("\nSaved NAV CSV verification:")
print(f"Rows: {len(nav_check):,}")
print(f"Columns: {list(nav_check.columns)}")
print(f"Missing values: {nav_check.isnull().sum().sum():,}")
# ============================================================
# 15. Load Investor Transactions
# ============================================================

transaction_file = next(
    RAW_DIR.glob("*08_investor_transactions.csv")
)

transactions_df = pd.read_csv(transaction_file)

print("\nInvestor Transactions loaded successfully.")
print(f"File: {transaction_file.name}")
print(f"Rows: {len(transactions_df):,}")
print(f"Columns: {list(transactions_df.columns)}")

print("\nFirst 5 rows:")
print(transactions_df.head())

print("\nData types:")
print(transactions_df.dtypes)

print("\nMissing values:")
print(transactions_df.isnull().sum())
# ============================================================
# 16. Inspect transaction types and KYC status
# ============================================================

print("\nUnique transaction types:")
print(transactions_df["transaction_type"].value_counts())

print("\nUnique KYC status values:")
print(transactions_df["kyc_status"].value_counts())

print("\nUnique payment modes:")
print(transactions_df["payment_mode"].value_counts())

print("\nUnique city tiers:")
print(transactions_df["city_tier"].value_counts())
# ============================================================
# 17. Convert transaction date to datetime
# ============================================================

transactions_df["transaction_date"] = pd.to_datetime(
    transactions_df["transaction_date"]
)

print("\nTransaction date conversion completed.")
print(f"Date data type: {transactions_df['transaction_date'].dtype}")
print(
    f"Minimum date: "
    f"{transactions_df['transaction_date'].min().date()}"
)
print(
    f"Maximum date: "
    f"{transactions_df['transaction_date'].max().date()}"
)
# ============================================================
# 18. Validate transaction amounts
# ============================================================

invalid_amount_count = (
    transactions_df["amount_inr"] <= 0
).sum()

print("\nTransaction amount validation:")
print(f"Amounts <= 0: {invalid_amount_count:,}")
print(
    f"Minimum transaction amount: "
    f"₹{transactions_df['amount_inr'].min():,}"
)
print(
    f"Maximum transaction amount: "
    f"₹{transactions_df['amount_inr'].max():,}"
)

if invalid_amount_count == 0:
    print("All transaction amounts are greater than 0.")
else:
    print("Invalid transaction amounts found. Please review them.")
    # ============================================================
# 19. Validate transaction type and KYC status
# ============================================================

valid_transaction_types = {
    "SIP",
    "Lumpsum",
    "Redemption"
}

valid_kyc_status = {
    "Verified",
    "Pending"
}

invalid_transaction_types = set(
    transactions_df["transaction_type"].unique()
) - valid_transaction_types

invalid_kyc_status = set(
    transactions_df["kyc_status"].unique()
) - valid_kyc_status

print("\nTransaction type validation:")
print(f"Invalid transaction types: {invalid_transaction_types}")

print("\nKYC status validation:")
print(f"Invalid KYC status values: {invalid_kyc_status}")

if not invalid_transaction_types:
    print("All transaction types are valid.")

if not invalid_kyc_status:
    print("All KYC status values are valid.")
    # ============================================================
# 20. Check for duplicate transactions
# ============================================================

transaction_duplicate_count = transactions_df.duplicated().sum()

print("\nDuplicate transaction check:")
print(
    f"Exact duplicate transaction rows: "
    f"{transaction_duplicate_count:,}"
)

if transaction_duplicate_count == 0:
    print("No duplicate transactions found.")
else:
    print("Duplicate transactions found. Please review them.")
    # ============================================================
# 21. Final Investor Transactions quality validation
# ============================================================

print("\nFinal Investor Transactions quality check:")

print(f"Total rows: {len(transactions_df):,}")
print(f"Unique investors: {transactions_df['investor_id'].nunique():,}")
print(f"Unique AMFI codes: {transactions_df['amfi_code'].nunique():,}")
print(f"Duplicate rows: {transactions_df.duplicated().sum():,}")
print(f"Missing values: {transactions_df.isnull().sum().sum():,}")
print(f"Amounts <= 0: {(transactions_df['amount_inr'] <= 0).sum():,}")

invalid_types = (
    ~transactions_df["transaction_type"].isin(valid_transaction_types)
).sum()

invalid_kyc = (
    ~transactions_df["kyc_status"].isin(valid_kyc_status)
).sum()

print(f"Invalid transaction types: {invalid_types:,}")
print(f"Invalid KYC status values: {invalid_kyc:,}")

if (
    transactions_df.isnull().sum().sum() == 0
    and transactions_df.duplicated().sum() == 0
    and (transactions_df["amount_inr"] <= 0).sum() == 0
    and invalid_types == 0
    and invalid_kyc == 0
):
    print(
        "RESULT: PASS - Investor Transactions "
        "data is clean and valid."
    )
else:
    print(
        "RESULT: FAIL - Please review the "
        "Investor Transactions data."
    )
    # ============================================================
# 22. Save cleaned Investor Transactions
# ============================================================

transaction_output_file = (
    PROCESSED_DIR / "investor_transactions_cleaned.csv"
)

transactions_df.to_csv(
    transaction_output_file,
    index=False
)

print("\nCleaned Investor Transactions saved successfully.")
print(f"Output file: {transaction_output_file}")
# ============================================================
# 23. Verify saved Investor Transactions CSV
# ============================================================

transaction_check = pd.read_csv(transaction_output_file)

print("\nSaved Investor Transactions CSV verification:")
print(f"Rows: {len(transaction_check):,}")
print(f"Columns: {list(transaction_check.columns)}")
print(
    f"Missing values: "
    f"{transaction_check.isnull().sum().sum():,}"
)
# ============================================================
# 24. Load Scheme Performance
# ============================================================

performance_file = next(
    RAW_DIR.glob("*07_scheme_performance.csv")
)

performance_df = pd.read_csv(performance_file)

print("\nScheme Performance loaded successfully.")
print(f"File: {performance_file.name}")
print(f"Rows: {len(performance_df):,}")
print(f"Columns: {list(performance_df.columns)}")

print("\nFirst 5 rows:")
print(performance_df.head())

print("\nData types:")
print(performance_df.dtypes)

print("\nMissing values:")
print(performance_df.isnull().sum())
# ============================================================
# 25. Inspect Scheme Performance ranges
# ============================================================

performance_numeric_columns = [
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
    "morningstar_rating"
]

print("\nScheme Performance numeric ranges:")

for column in performance_numeric_columns:
    print(
        f"{column}: "
        f"min={performance_df[column].min():.2f}, "
        f"max={performance_df[column].max():.2f}"
    )
    # ============================================================
# 26. Validate Scheme Performance
# ============================================================

invalid_expense_ratio = (
    (performance_df["expense_ratio_pct"] < 0.1)
    | (performance_df["expense_ratio_pct"] > 2.5)
).sum()

duplicate_performance = performance_df.duplicated(
    subset=["amfi_code"]
).sum()

print("\nScheme Performance validation:")
print(
    f"Expense ratios outside 0.1%-2.5%: "
    f"{invalid_expense_ratio:,}"
)
print(
    f"Duplicate AMFI codes: "
    f"{duplicate_performance:,}"
)

if invalid_expense_ratio == 0:
    print("All expense ratios are within the required range.")

if duplicate_performance == 0:
    print("No duplicate AMFI codes found.")

if invalid_expense_ratio == 0 and duplicate_performance == 0:
    print(
        "RESULT: PASS - Scheme Performance "
        "data is clean and valid."
    )
else:
    print(
        "RESULT: FAIL - Please review the "
        "Scheme Performance data."
    )
    # ============================================================
# 27. Save Cleaned Scheme Performance Data
# ============================================================

performance_df.to_csv(
    PROCESSED_DIR / "scheme_performance_cleaned.csv",
    index=False
)

print(
    f"\nSaved cleaned Scheme Performance data to: "
    f"{PROCESSED_DIR / 'scheme_performance_cleaned.csv'}"
)
# ============================================================
# 28. Clean Fund Master
# ============================================================

fund_master_df = pd.read_csv(
    next(RAW_DIR.glob("*01_fund_master.csv"))
)

print("\nFund Master validation:")

print(f"Rows: {len(fund_master_df):,}")
print(f"Unique AMFI codes: {fund_master_df['amfi_code'].nunique():,}")

duplicate_funds = fund_master_df.duplicated(
    subset=["amfi_code"]
).sum()

missing_funds = fund_master_df.isna().sum().sum()

print(f"Duplicate AMFI codes: {duplicate_funds:,}")
print(f"Missing values: {missing_funds:,}")

if duplicate_funds == 0 and missing_funds == 0:
    print("RESULT: PASS - Fund Master data is clean and valid.")
else:
    print("RESULT: FAIL - Please review Fund Master data.")


# Save cleaned Fund Master
fund_master_df.to_csv(
    PROCESSED_DIR / "fund_master_cleaned.csv",
    index=False
)

print(
    f"Saved cleaned Fund Master data to: "
    f"{PROCESSED_DIR / 'fund_master_cleaned.csv'}"
)
# ============================================================
# 29. Clean AUM by Fund House
# ============================================================

aum_df = pd.read_csv(
    next(RAW_DIR.glob("*03_aum_by_fund_house.csv"))
)

print("\nAUM by Fund House validation:")

print(f"Rows: {len(aum_df):,}")
print(f"Unique fund houses: {aum_df['fund_house'].nunique():,}")

duplicate_aum = aum_df.duplicated(
    subset=["fund_house", "date"]
).sum()

missing_aum = aum_df.isna().sum().sum()

invalid_aum = (
    aum_df["aum_crore"] <= 0
).sum()

print(f"Duplicate fund house/date rows: {duplicate_aum:,}")
print(f"Missing values: {missing_aum:,}")
print(f"AUM values <= 0: {invalid_aum:,}")

if (
    duplicate_aum == 0
    and missing_aum == 0
    and invalid_aum == 0
):
    print(
        "RESULT: PASS - AUM by Fund House "
        "data is clean and valid."
    )
else:
    print(
        "RESULT: FAIL - Please review "
        "AUM by Fund House data."
    )


# Save cleaned AUM data
aum_df.to_csv(
    PROCESSED_DIR / "aum_by_fund_house_cleaned.csv",
    index=False
)

print(
    f"Saved cleaned AUM data to: "
    f"{PROCESSED_DIR / 'aum_by_fund_house_cleaned.csv'}"
)
# ============================================================
# 30. Clean Monthly SIP Inflows
# ============================================================

sip_df = pd.read_csv(
    next(RAW_DIR.glob("*04_monthly_sip_inflows.csv"))
)

# Convert month to datetime
sip_df["month"] = pd.to_datetime(
    sip_df["month"]
)

print("\nMonthly SIP Inflows validation:")

print(f"Rows: {len(sip_df):,}")
print(f"Duplicate months: {sip_df.duplicated(subset=['month']).sum():,}")
print(f"Missing values: {sip_df.isna().sum().sum():,}")

invalid_sip_inflow = (
    sip_df["sip_inflow_crore"] <= 0
).sum()

invalid_accounts = (
    sip_df["active_sip_accounts_crore"] <= 0
).sum()

print(
    f"SIP inflows <= 0: "
    f"{invalid_sip_inflow:,}"
)

print(
    f"Active SIP accounts <= 0: "
    f"{invalid_accounts:,}"
)

if (
    sip_df.duplicated(subset=["month"]).sum() == 0
    and invalid_sip_inflow == 0
    and invalid_accounts == 0
):
    print(
        "RESULT: PASS - Monthly SIP Inflows "
        "data is clean and valid."
    )
else:
    print(
        "RESULT: FAIL - Please review "
        "Monthly SIP Inflows data."
    )

# Save cleaned SIP data
sip_df["month"] = sip_df["month"].dt.strftime("%Y-%m")

sip_df.to_csv(
    PROCESSED_DIR / "monthly_sip_inflows_cleaned.csv",
    index=False
)

print(
    f"Saved cleaned SIP data to: "
    f"{PROCESSED_DIR / 'monthly_sip_inflows_cleaned.csv'}"
)