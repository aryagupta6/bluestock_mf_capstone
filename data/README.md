# Data Layer Directory

This folder contains raw source data and cleaned/processed CSV outputs used throughout the mutual fund capstone project.

## Directory Layout

- **`raw/`**: Contains raw, unmodified CSV data files:
  - `01_fund_master.csv`: Primary metadata for all mutual fund schemes.
  - `02_nav_history.csv`: Daily historical Net Asset Values (NAV).
  - `07_scheme_performance.csv`: Pre-calculated returns from AMCs.
  - `08_investor_transactions.csv`: Transaction logs including investor demographics.
  - `09_portfolio_holdings.csv`: Stock allocations and sector weights.
  - `10_benchmark_indices.csv`: Price series for benchmark indices (Nifty 50, Nifty 100).
- **`processed/`**: Cleaned, standard-compliant CSV files loaded into the database or produced during analytics:
  - `clean_fund_master.csv`: Standardized fund master fields.
  - `clean_nav.csv`: Imputed NAV data with forward fills.
  - `clean_transactions.csv`: Ledger with anomalous negative values removed.
  - `returns_computed.csv`: Full daily return timeseries.
  - `cagr_report.csv`: 1-year, 3-year, and 5-year CAGR per fund.
  - `var_cvar_report.csv`: Tail risk (Value at Risk and Conditional VaR) calculations.
  - `sector_hhi.csv`: Portfolio sector concentration scores.
  - `cohort_analysis.csv`: Behavioral metrics for 2024 vs. 2025 investor cohorts.
  - `sip_continuity.csv`: Active SIP accounts flagged with default risk.
