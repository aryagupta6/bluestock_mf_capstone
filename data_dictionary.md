# Mutual Fund Analytics - Data Dictionary (Day 2)

This document provides a comprehensive schema description for the **SQLite Mutual Fund Database (`bluestock_mf.db`)**. It describes the tables, column names, data types, key constraints, logical descriptions, and their source files.

---

## Database Architecture

The database is built on a **star/snowflake-like schema** where `dim_fund` serves as the primary dimension table, and analytical datasets serve as fact tables linked via the unique `amfi_code` key.

```
                  +-----------------------+
                  |       dim_fund        | (Dimension)
                  +-----------------------+
                  | amfi_code (PK)        |
                  +-----------+-----------+
                              |
       +----------------------+----------------------+
       | (1:N)                | (1:1/1:N)            | (1:N)
+------+------+        +------+------+        +------+------+
|  fact_nav   |        |fact_perfor..|        |fact_transa..|
+------+------+        +------+------+        +------+------+
|amfi_code(FK)|        |amfi_code(FK)|        |amfi_code(FK)|
+-------------+        +-------------+        +-------------+
```

---

## Tables & Columns Dictionary

### 1. `dim_fund` (Fund Master)
*   **Description:** Contains master records of mutual fund schemes, categories, asset management details, and subscription rules.
*   **Source File:** `data/processed/clean_fund_master.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Unique Association of Mutual Funds in India identifier code |
| `fund_house` | TEXT | NOT NULL | Name of the Mutual Fund House (Asset Management Company) |
| `scheme_name` | TEXT | NOT NULL | Name of the mutual fund scheme |
| `category` | TEXT | NOT NULL | Broad asset category (e.g., Equity, Debt) |
| `sub_category` | TEXT | NOT NULL | Specific thematic classification (e.g., Large Cap, Gilt, Liquid) |
| `plan` | TEXT | NOT NULL | Subscription plan model (Regular or Direct) |
| `launch_date` | DATE | | Official inception/launch date of the fund |
| `benchmark` | TEXT | | Corresponding index used as performance benchmark |
| `expense_ratio_pct`| REAL | | Management fee charged to investors as an annual percentage |
| `exit_load_pct` | REAL | | Penalty charge applied upon redemption of fund units within a threshold |
| `min_sip_amount` | REAL | | Minimum transaction amount allowed for Systematic Investment Plan |
| `min_lumpsum_amount`| REAL | | Minimum amount required for a one-time purchase |
| `fund_manager` | TEXT | | Principal manager supervising the fund portfolio |
| `risk_category` | TEXT | | Qualitative risk profile assigned to the fund |
| `sebi_category_code`| TEXT | | Securities and Exchange Board of India classification code |

---

### 2. `fact_nav` (Historical NAV series)
*   **Description:** Daily Net Asset Value (NAV) price histories for all registered funds.
*   **Source File:** `data/processed/clean_nav.csv` (Merged history with live-fetched NAV data)
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK | Reference to `dim_fund.amfi_code` |
| `nav_date` | DATE | PRIMARY KEY | Date of the NAV valuation |
| `nav` | REAL | NOT NULL | Net Asset Value (price per unit) on that date |
| `daily_return` | REAL | | Calculated percentage change: `(NAV_t - NAV_t-1) / NAV_t-1` |

---

### 3. `fact_transactions` (Investor Transactions)
*   **Description:** Individual logs of investor transaction behaviors including purchases and redemptions.
*   **Source File:** `data/processed/clean_transactions.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `transaction_id` | INTEGER | PRIMARY KEY (AUTO) | Synthesized auto-incrementing unique primary key |
| `investor_id` | TEXT | NOT NULL | Anonymized identifier for the investor account |
| `transaction_date`| DATE | NOT NULL | Date the transaction was executed |
| `amfi_code` | INTEGER | FOREIGN KEY | Reference to `dim_fund.amfi_code` |
| `transaction_type`| TEXT | NOT NULL | Class of activity (`SIP`, `Lumpsum`, `Redemption`) |
| `amount_inr` | REAL | NOT NULL | Transaction value in Indian Rupees |
| `state` | TEXT | | Geographic state location of the investor |
| `city` | TEXT | | City location of the investor |
| `city_tier` | TEXT | | Classification category of the city (`T30` - Top 30, `B30` - Beyond 30) |
| `age_group` | TEXT | | Age demographic grouping of the investor |
| `gender` | TEXT | | Gender of the investor |
| `annual_income_lakh`| REAL | | Self-declared annual income of the investor (in Lakhs INR) |
| `payment_mode` | TEXT | | Method of transaction payment (`UPI`, `Net Banking`, `Cheque`, `Mandate`) |
| `kyc_status` | TEXT | | Status of Know-Your-Customer checks (`Verified`, `Pending`) |

---

### 4. `fact_performance` (Performance Analytics)
*   **Description:** Aggregated fund statistics, risk indicators, ratings, and return rates.
*   **Source File:** `data/processed/clean_performance.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK | Reference to `dim_fund.amfi_code` |
| `scheme_name` | TEXT | NOT NULL | Name of the fund scheme |
| `fund_house` | TEXT | NOT NULL | Name of the Asset Management Company |
| `category` | TEXT | NOT NULL | Asset category class |
| `plan` | TEXT | NOT NULL | Subscription plan model (Regular or Direct) |
| `return_1yr_pct` | REAL | | Annual return percentage over 1 year |
| `return_3yr_pct` | REAL | | Annualized compound return percentage over 3 years |
| `return_5yr_pct` | REAL | | Annualized compound return percentage over 5 years |
| `benchmark_3yr_pct`| REAL | | Annualized benchmark returns over 3 years |
| `alpha` | REAL | | Outperformance of the fund relative to the benchmark |
| `beta` | REAL | | Systematic risk/volatility of the fund compared to the market (benchmark) |
| `sharpe_ratio` | REAL | | Risk-adjusted return metric (excess return per unit of volatility) |
| `sortino_ratio` | REAL | | Risk-adjusted return metric focusing only on negative deviation (downside risk) |
| `std_dev_ann_pct` | REAL | | Standard deviation of monthly returns annualized (volatility measure) |
| `max_drawdown_pct` | REAL | | Maximum peak-to-trough decline percentage over history |
| `aum_crore` | REAL | | Asset Under Management value in Crore INR |
| `expense_ratio_pct`| REAL | | Management fee ratio percentage |
| `morningstar_rating`| INTEGER| | 1 to 5 star rating given by Morningstar metrics |
| `risk_grade` | TEXT | | Volatility/risk tier classification |
| `is_negative_sharpe`| BOOLEAN | | Flag indicating if Sharpe Ratio is negative (True/False) |

---

### 5. `fact_portfolio_holdings` (Stock Holdings)
*   **Description:** Lists individual stock asset allocations and values within each mutual fund portfolio.
*   **Source File:** `data/processed/clean_portfolio_holdings.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK | Reference to `dim_fund.amfi_code` |
| `stock_symbol` | TEXT | PRIMARY KEY | Stock ticker symbol traded on the exchange |
| `stock_name` | TEXT | NOT NULL | Name of the underlying corporation |
| `sector` | TEXT | NOT NULL | Economic sector group of the company |
| `weight_pct` | REAL | NOT NULL | Percentage weight allocation in the fund's overall portfolio |
| `market_value_cr` | REAL | | Value of the holdings in Crore INR |
| `current_price_inr`| REAL | | Current per-share market price in INR |
| `portfolio_date` | DATE | NOT NULL | Valuation date of the portfolio holdings data |

---

### 6. `fact_aum` (AUM History by Fund House)
*   **Description:** Historical quarterly record of Assets Under Management (AUM) per Fund House.
*   **Source File:** `data/processed/clean_aum_by_fund_house.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date` | DATE | PRIMARY KEY | Recording date of the AUM check |
| `fund_house` | TEXT | PRIMARY KEY | Asset Management Company name |
| `aum_lakh_crore` | REAL | | AUM value in Lakh Crores INR |
| `aum_crore` | REAL | | AUM value in Crores INR |
| `num_schemes` | INTEGER | | Number of active schemes run by the fund house |

---

### 7. `fact_sip_inflows` (Monthly SIP Statistics)
*   **Description:** National aggregate metrics detailing monthly SIP accounts and dollar flows.
*   **Source File:** `data/processed/clean_monthly_sip_inflows.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Month of the metrics (Format: `YYYY-MM`) |
| `sip_inflow_crore` | REAL | | Monthly SIP investment inflows in Crore INR |
| `active_sip_accounts_crore`| REAL | | Total number of running active SIP accounts (in Crores) |
| `new_sip_accounts_lakh`| REAL | | Number of new SIP accounts opened during the month (in Lakhs) |
| `sip_aum_lakh_crore`| REAL | | Cumulative AUM built specifically through SIP investments |
| `yoy_growth_pct` | REAL | | Year-over-Year percentage growth in SIP inflows |

---

### 8. `fact_category_inflows` (Fund Category Inflows)
*   **Description:** Monthly net cash flows (inflow minus outflow) across different mutual fund categories.
*   **Source File:** `data/processed/clean_category_inflows.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Month of the recording (Format: `YYYY-MM`) |
| `category` | TEXT | PRIMARY KEY | Fund class category (e.g. Large Cap, Liquid, Gilt) |
| `net_inflow_crore` | REAL | | Net cash inflow in Crore INR |

---

### 9. `fact_industry_folios` (Industry-Wide Folios count)
*   **Description:** Historical monthly tracking of mutual fund accounts (folios) across the industry.
*   **Source File:** `data/processed/clean_industry_folio_count.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Recording month (Format: `YYYY-MM`) |
| `total_folios_crore`| REAL | | Total folios in the entire mutual fund industry (in Crores) |
| `equity_folios_crore`| REAL | | Folios registered in Equity mutual funds (in Crores) |
| `debt_folios_crore`| REAL | | Folios registered in Debt mutual funds (in Crores) |
| `hybrid_folios_crore`| REAL | | Folios registered in Hybrid mutual funds (in Crores) |
| `others_folios_crore`| REAL | | Folios in other classes like ETFs or Gold (in Crores) |

---

### 10. `fact_benchmark` (Benchmark Indices Prices)
*   **Description:** Daily tracking of benchmark close prices (e.g. NIFTY50 index) for fund benchmark comparisons.
*   **Source File:** `data/processed/clean_benchmark_indices.csv`
*   **Columns:**

| Column Name | Data Type | Key/Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date` | DATE | PRIMARY KEY | Recording date of the index close value |
| `index_name` | TEXT | PRIMARY KEY | Name of the benchmark index (e.g. NIFTY50) |
| `close_value` | REAL | | Market close valuation value of the index |
