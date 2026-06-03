-- Day 2: Relational Database Schema Design for SQLite
-- This DDL script defines 10 tables mapped to the cleaned mutual fund datasets.

-- Drop existing tables to ensure clean setup
DROP TABLE IF EXISTS fact_portfolio_holdings;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_sip_inflows;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_industry_folios;
DROP TABLE IF EXISTS fact_benchmark;

-- 1. Dimension Table: dim_fund (Fund Master Details)
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Fact Table: fact_nav (Historical and Live NAV Data)
CREATE TABLE fact_nav (
    amfi_code INTEGER,
    nav_date DATE,
    nav REAL NOT NULL,
    daily_return REAL, -- Computed column: (nav - nav_prev) / nav_prev
    PRIMARY KEY (amfi_code, nav_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code) ON DELETE CASCADE
);

-- 3. Fact Table: fact_transactions (Investor Transaction Log)
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Synthesized unique PK for transaction row
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code) ON DELETE SET NULL
);

-- 4. Fact Table: fact_performance (Fund Performance Metrics)
CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
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
    is_negative_sharpe BOOLEAN,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code) ON DELETE CASCADE
);

-- 5. Fact Table: fact_portfolio_holdings (Fund Stock Holdings)
CREATE TABLE fact_portfolio_holdings (
    amfi_code INTEGER,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code) ON DELETE CASCADE
);

-- 6. Fact Table: fact_aum (AUM History by Fund House)
CREATE TABLE fact_aum (
    date DATE,
    fund_house TEXT,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (date, fund_house)
);

-- 7. Fact Table: fact_sip_inflows (Monthly SIP Industry Inflow Statistics)
CREATE TABLE fact_sip_inflows (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- 8. Fact Table: fact_category_inflows (Net Inflows grouped by Fund Category)
CREATE TABLE fact_category_inflows (
    month TEXT,
    category TEXT,
    net_inflow_crore REAL,
    PRIMARY KEY (month, category)
);

-- 9. Fact Table: fact_industry_folios (Industry-Wide Folio Count History)
CREATE TABLE fact_industry_folios (
    month TEXT PRIMARY KEY,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- 10. Fact Table: fact_benchmark (Benchmark Index Close Prices History)
CREATE TABLE fact_benchmark (
    date DATE,
    index_name TEXT,
    close_value REAL,
    PRIMARY KEY (date, index_name)
);

-- Create Indexes to optimize analytical performance
CREATE INDEX idx_nav_date ON fact_nav(nav_date);
CREATE INDEX idx_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX idx_trans_amfi ON fact_transactions(amfi_code);
CREATE INDEX idx_trans_date ON fact_transactions(transaction_date);
CREATE INDEX idx_holdings_sector ON fact_portfolio_holdings(sector);
