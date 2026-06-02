# Day 1: Data Ingestion & Quality Summary Report

Generated on: 2026-06-02 21:17:48

## 1. Datasets Summary Table

| Dataset File | Rows | Columns | Detected Anomalies |
| :--- | :--- | :--- | :--- |
| 01_fund_master.csv | 40 | 15 | None |
| 02_nav_history.csv | 46000 | 3 | None |
| 03_aum_by_fund_house.csv | 90 | 5 | None |
| 04_monthly_sip_inflows.csv | 48 | 6 | Missing Values |
| 05_category_inflows.csv | 144 | 3 | None |
| 06_industry_folio_count.csv | 21 | 6 | None |
| 07_scheme_performance.csv | 40 | 19 | None |
| 08_investor_transactions.csv | 32778 | 13 | None |
| 09_portfolio_holdings.csv | 322 | 8 | None |
| 10_benchmark_indices.csv | 8050 | 3 | None |

## 2. Fund Master Exploration (`01_fund_master.csv`)

- **Unique Fund Houses (10):** Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund
- **Unique Categories (2):** Debt, Equity
- **Unique Sub-Categories (12):** ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value
- **Unique Risk Categories (5):** High, Low, Moderate, Moderately High, Very High

### AMFI Scheme Code Structure Analysis
AMFI (Association of Mutual Funds in India) scheme codes are unique 5 or 6 digit identifiers.
By analyzing the fund master dataset, we observe the following characteristics:
1. **Regular vs Direct Plans:** Direct and Regular plans of the same scheme have sequential or consecutive AMFI codes.
   * *Example:* SBI Bluechip Fund Regular Growth is `119551` and Direct Growth is `119552`.
   * *Example:* HDFC Top 100 Fund Regular Growth is `100016`, whereas Direct Growth is `125497` (non-sequential due to different launch times, Direct plans were introduced later in 2013).
2. **Sequential Registration:** Block allocation of codes is visible. For instance, SBI Mutual Fund schemes occupy the `1195xx` block (SBI Bluechip Regular `119551`, Direct `119552`, Small Cap Regular `119598`, Direct `119599`). Axis Mutual Fund schemes occupy the `1190xx` block (Axis Bluechip Regular `119092`, Direct `119093`, Midcap Regular `119094`, Small Cap Regular `119095`).
3. **Plan Association:** Direct plans launched in 2013 share a pattern in code jumps if not registered sequentially with the regular plan (e.g. HDFC Regular `100016` launched 1996 vs Direct `125497` launched 2013).


## 3. AMFI Code Validation (`fund_master` vs `nav_history`)

- **Unique AMFI codes in Fund Master:** 40
- **Unique AMFI codes in NAV History:** 40
- **Matched AMFI codes:** 40 (100.00% match)
- **AMFI codes in Fund Master missing in NAV History:** 0
- [+] All AMFI codes in Fund Master successfully exist in NAV History.

## 4. Detailed Anomalies Log

### 04_monthly_sip_inflows.csv (Monthly SIP Inflows)

- Missing Values: Column 'yoy_growth_pct' has 12 null value(s) (25.00%).
