# Bluestock Mutual Fund Analytics — Data Dictionary

## 1. dim_fund

Fund master dimension containing scheme-level information.

| Column | Description |
|---|---|
| amfi_code | Unique AMFI scheme identifier |
| scheme_name | Mutual fund scheme name |
| fund_house | Asset management company / fund house |
| category | Broad fund category such as Equity or Debt |
| sub_category | Fund sub-category |
| plan | Fund plan type |
| risk_category | Risk classification of the scheme |

---

## 2. dim_date

Calendar dimension used for time-based analysis.

| Column | Description |
|---|---|
| date | Calendar date |
| year | Calendar year |
| month | Numeric month |
| quarter | Calendar quarter |
| month_name | Name of the month |
| day_of_week | Day of the week |

---

## 3. fact_nav

Daily NAV history for mutual fund schemes.

| Column | Description |
|---|---|
| amfi_code | AMFI scheme identifier |
| date | NAV date |
| nav | Net Asset Value of the scheme |

---

## 4. fact_transactions

Investor transaction-level data.

| Column | Description |
|---|---|
| transaction_id | Unique transaction identifier generated during ETL |
| investor_id | Investor identifier |
| amfi_code | AMFI scheme identifier |
| transaction_date | Transaction date |
| transaction_type | SIP, Lumpsum, or Redemption |
| amount_inr | Transaction amount in INR |
| state | Investor state |
| city | Investor city |
| city_tier | T30 or B30 classification |
| age_group | Investor age group |
| gender | Investor gender |
| annual_income_lakh | Annual income in lakh INR |
| payment_mode | Payment method |
| kyc_status | KYC verification status |

---

## 5. fact_performance

Scheme-level performance and risk metrics.

| Column | Description |
|---|---|
| amfi_code | AMFI scheme identifier |
| return_1yr_pct | One-year return percentage |
| return_3yr_pct | Three-year return percentage |
| return_5yr_pct | Five-year return percentage |
| benchmark_3yr_pct | Three-year benchmark return percentage |
| alpha | Scheme alpha |
| beta | Scheme beta |
| sharpe_ratio | Sharpe ratio |
| sortino_ratio | Sortino ratio |
| std_dev_ann_pct | Annualized standard deviation |
| max_drawdown_pct | Maximum drawdown percentage |
| aum_crore | Scheme AUM in crore INR |
| expense_ratio_pct | Expense ratio percentage |
| morningstar_rating | Morningstar rating |
| risk_grade | Scheme risk grade |

---

## 6. fact_aum

Fund-house-level assets under management data.

| Column | Description |
|---|---|
| fund_house | Mutual fund house |
| date | AUM reporting date |
| aum_lakh_crore | AUM measured in lakh crore INR |
| aum_crore | AUM measured in crore INR |
| num_schemes | Number of schemes |

---

## Data Quality Summary

| Dataset | Rows | Status |
|---|---:|---|
| Fund Master | 40 | Clean |
| NAV History | 64,320 | Clean |
| Investor Transactions | 32,778 | Clean |
| Scheme Performance | 40 | Clean |
| AUM by Fund House | 90 | Clean |

## Database

SQLite database:

`data/db/bluestock_mf.db`

Schema:

`sql/schema.sql`

Analytical queries:

`sql/queries.sql`