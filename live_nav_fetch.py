import requests
import pandas as pd
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def fetch_nav(amfi_code):
    """Fetch NAV history for a given AMFI scheme code."""

    url = f"https://api.mfapi.in/mf/{amfi_code}"

    print(f"Fetching NAV for AMFI code: {amfi_code}")
    print(f"URL: {url}")

    response = requests.get(url, timeout=30)

    # Raise an error if the API request failed
    response.raise_for_status()

    data = response.json()

    print(f"Scheme: {data.get('meta', {}).get('scheme_name', 'Unknown')}")

    # Convert NAV data into a DataFrame
    nav_data = data.get("data", [])

    df = pd.DataFrame(nav_data)

    if df.empty:
        print("No NAV data received.")
        return

    # Rename columns
    df = df.rename(
        columns={
            "date": "date",
            "nav": "nav"
        }
    )

    # Add AMFI code
    df.insert(0, "amfi_code", amfi_code)

    # Save raw API response as CSV
    output_file = RAW_DATA_DIR / f"live_nav_{amfi_code}.csv"

    df.to_csv(output_file, index=False)

    print(f"Saved {len(df)} NAV records.")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    scheme_codes = [
        125497,  # Task says HDFC Top 100 Direct
        119551,  # SBI Bluechip
        120503,  # ICICI Bluechip
        118632,  # Nippon Large Cap
        119092,  # Axis Bluechip
        120841,  # Kotak Bluechip
    ]

    for code in scheme_codes:
        try:
            fetch_nav(code)
            print("-" * 80)
        except Exception as e:
            print(f"Failed to fetch AMFI code {code}: {e}")