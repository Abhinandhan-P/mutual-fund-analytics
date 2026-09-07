import pandas as pd
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def inspect_csv_files():
    """Load and inspect all CSV files in data/raw."""

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw")
        return

    print(f"Found {len(csv_files)} CSV files.\n")

    for file_path in csv_files:
        print("=" * 80)
        print(f"FILE: {file_path.name}")
        print("=" * 80)

        try:
            df = pd.read_csv(file_path)

            print("\nSHAPE:")
            print(df.shape)

            print("\nDATA TYPES:")
            print(df.dtypes)

            print("\nFIRST 5 ROWS:")
            print(df.head())

            print("\nMISSING VALUES:")
            print(df.isnull().sum())

            print()

        except Exception as e:
            print(f"ERROR reading {file_path.name}: {e}")


def explore_fund_master():
    """Explore fund master dimensions."""

    fund_master_files = list(RAW_DATA_DIR.glob("*01_fund_master.csv"))

    if not fund_master_files:
        print("fund_master.csv not found.")
        return

    file_path = fund_master_files[0]

    df = pd.read_csv(file_path)

    print("\n" + "=" * 80)
    print("FUND MASTER EXPLORATION")
    print("=" * 80)

    print("\nUnique Fund Houses:")
    print(df["fund_house"].unique())

    print("\nUnique Categories:")
    print(df["category"].unique())

    print("\nUnique Sub-Categories:")
    print(df["sub_category"].unique())

    print("\nUnique Risk Categories:")
    print(df["risk_category"].unique())

    print("\nNumber of unique AMFI codes:")
    print(df["amfi_code"].nunique())

    print("\nAMFI code range:")
    print(df["amfi_code"].min(), "to", df["amfi_code"].max())


def validate_amfi_codes():
    """Validate AMFI codes between fund_master and nav_history."""

    fund_master_files = list(RAW_DATA_DIR.glob("*01_fund_master.csv"))
    nav_history_files = list(RAW_DATA_DIR.glob("*02_nav_history.csv"))

    if not fund_master_files:
        print("fund_master.csv not found.")
        return

    if not nav_history_files:
        print("nav_history.csv not found.")
        return

    fund_master = pd.read_csv(fund_master_files[0])
    nav_history = pd.read_csv(nav_history_files[0])

    master_codes = set(fund_master["amfi_code"].unique())
    nav_codes = set(nav_history["amfi_code"].unique())

    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes

    print("\n" + "=" * 80)
    print("AMFI CODE VALIDATION")
    print("=" * 80)

    print(f"\nUnique AMFI codes in fund_master: {len(master_codes)}")
    print(f"Unique AMFI codes in nav_history: {len(nav_codes)}")

    print("\nCodes in fund_master but missing from nav_history:")
    print(missing_in_nav if missing_in_nav else "None")

    print("\nCodes in nav_history but missing from fund_master:")
    print(extra_in_nav if extra_in_nav else "None")

    if not missing_in_nav and not extra_in_nav:
        print("\nRESULT: PASS - AMFI codes match between fund_master and nav_history.")
    else:
        print("\nRESULT: REVIEW REQUIRED - AMFI code mismatch found.")


if __name__ == "__main__":
    inspect_csv_files()
    explore_fund_master()
    validate_amfi_codes()