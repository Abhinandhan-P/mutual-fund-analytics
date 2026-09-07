-- ============================================================
-- Bluestock Mutual Fund Analytics
-- 10 Analytical SQL Queries
-- ============================================================


-- Query 1: Top 10 funds by 3-year return
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 10;


-- Query 2: Top funds by Sharpe ratio
SELECT
    f.scheme_name,
    f.fund_house,
    p.sharpe_ratio,
    p.return_3yr_pct,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 10;


-- Query 3: Fund house AUM ranking
SELECT
    fund_house,
    ROUND(SUM(aum_crore), 2) AS total_aum_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_crore DESC;


-- Query 4: Average return by category
SELECT
    f.category,
    ROUND(AVG(p.return_1yr_pct), 2) AS avg_1yr_return,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(AVG(p.return_5yr_pct), 2) AS avg_5yr_return
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY avg_3yr_return DESC;


-- Query 5: Transaction volume by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;


-- Query 6: SIP investment by city tier
SELECT
    city_tier,
    COUNT(*) AS sip_transactions,
    ROUND(SUM(amount_inr), 2) AS sip_amount_inr
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY city_tier
ORDER BY sip_amount_inr DESC;


-- Query 7: KYC status distribution
SELECT
    kyc_status,
    COUNT(*) AS investor_transactions
FROM fact_transactions
GROUP BY kyc_status
ORDER BY investor_transactions DESC;


-- Query 8: Monthly transaction activity
SELECT
    substr(transaction_date, 1, 7) AS year_month,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY year_month
ORDER BY year_month;


-- Query 9: Funds with highest risk-adjusted performance
SELECT
    f.scheme_name,
    f.category,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio >= 2
ORDER BY p.sharpe_ratio DESC;


-- Query 10: Fund performance versus benchmark
SELECT
    f.scheme_name,
    f.fund_house,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(
        p.return_3yr_pct - p.benchmark_3yr_pct,
        2
    ) AS excess_return_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY excess_return_pct DESC;