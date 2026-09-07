# Day 1 — Data Quality Summary

## Dataset Inspection

All 10 provided CSV datasets were successfully loaded using Pandas.

Key observations:

- `fund_master.csv`: 40 rows, 15 columns
- `nav_history.csv`: 46,000 rows, 3 columns
- `monthly_sip_inflows.csv`: 48 rows, 6 columns
- `category_inflows.csv`: 144 rows, 3 columns
- `aum_by_fund_house.csv`: 90 rows, 5 columns
- `industry_folio_count.csv`: 21 rows, 6 columns
- `scheme_performance.csv`: 40 rows, 19 columns
- `investor_transactions.csv`: 32,778 rows, 13 columns
- `portfolio_holdings.csv`: 322 rows, 8 columns
- `benchmark_indices.csv`: 8,050 rows, 3 columns

## Data Quality Findings

Most datasets contain no missing values.

`monthly_sip_inflows.csv` contains 12 missing values in
`yoy_growth_pct`. These occur in the initial period where a
year-over-year comparison is not available. These values were
left unchanged.

## Fund Master Exploration

- Unique fund houses: 10
- Main categories: 2
  - Equity
  - Debt
- Sub-categories: 12
- Risk categories: 5
- Unique AMFI codes: 40
- AMFI code range: 100016 to 149324

## AMFI Code Validation

Every AMFI code in `fund_master.csv` exists in `nav_history.csv`.

- Fund master unique codes: 40
- NAV history unique codes: 40
- Missing fund-master codes in NAV history: None
- Extra NAV codes not present in fund master: None

**Validation result: PASS**

## Live NAV API Observation

Live NAV data was successfully fetched from MFAPI for the six
requested scheme codes.

The API responses should be treated as the source returned by the
live API. Several requested code-to-scheme-name mappings did not
match the names stated in the project task.

Observed live API responses included:

- 125497 → SBI SMALL CAP FUND - Direct Plan - Growth
- 119551 → Aditya Birla Sun Life Banking & PSU Debt Fund - Direct Plan - IDCW-Re-investment
- 120503 → Axis ELSS- Tax Saver Fund - Direct Plan - Growth Option
- 118632 → Nippon India Large Cap Fund - Direct Plan - Growth Option
- 119092 → HDFC Money Market Fund - Direct Plan - Growth Option
- 120841 → Quant Mid Cap Fund - Direct Plan - Growth Option

These discrepancies were preserved rather than modifying the returned
API data.

## Overall Status

Day 1 data ingestion, initial exploration, API ingestion, and AMFI
code validation completed successfully.