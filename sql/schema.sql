-- ============================================================
-- Bluestock Mutual Fund Analytics
-- SQLite Star Schema
-- ============================================================

-- Dimension: Fund
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    risk_category TEXT
);


-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    month_name TEXT,
    day_of_week TEXT
);


-- Fact: NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);


-- Fact: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    investor_id TEXT,
    amfi_code INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT,
    amount_inr REAL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

-- Fact: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- Fact: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house TEXT NOT NULL,
    date TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (fund_house, date),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);
-- ============================================================
-- Fact: Monthly SIP Inflows
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_sip_inflows (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);


-- ============================================================
-- Fact: Category Inflows
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    inflow_crore REAL,
    PRIMARY KEY (month, category)
);


-- ============================================================
-- Fact: Industry Folio Count
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_folio_count (
    month TEXT PRIMARY KEY,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);


-- ============================================================
-- Fact: Portfolio Holdings
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- ============================================================
-- Fact: Benchmark Indices
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    date TEXT NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);