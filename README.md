# Bluestock Mutual Fund Analytics & Delivery Platform

An end-to-end analytical platform designed to clean, store, and evaluate mutual fund performance data, calculate advanced risk metrics, model investor behavior, and recommend portfolios aligned with client risk tolerances.

---

## Project Architecture & Directory Structure

The project adheres to the standardized folder structure outlined in the capstone guidelines:

```
bluestock_mf_capstone/
│
├── data/
│   ├── raw/                  # Source files (Fund master, NAV history, transactions, benchmarks)
│   └── processed/            # Clean CSV extracts (cagr_report, var_cvar_report, cohort_analysis, etc.)
│
├── db/                       # Centralized SQLite database
│   └── bluestock_mf.db       # Relational database storing dimension and fact tables
│
├── sql/                      # Relational schema DDL and views
│   └── schema.sql            # Table structures, primary/foreign keys, and indexes
│
├── scripts/                  # Programmatic ETL, analytics, and deliverable generators
│   ├── data_ingestion.py     # Acquires source data files
│   ├── data_cleaning.py      # Cleans, imputes, and standardizes data
│   ├── db_loader.py          # Populates SQLite relational database
│   ├── compute_metrics.py    # Calculates performance analytics (CAGR, Sharpe, Sortino, Alpha, Beta)
│   ├── advanced_analytics.py # Calculates VaR, CVaR, rolling Sharpe, HHI, and cohorts
│   ├── recommender.py        # CLI interactive fund recommendation engine
│   └── generate_delivery_files.py # Compiles slide presentation and final PDF report
│
├── notebooks/                # Exploratory analyses and analytics outputs
│   ├── EDA_Findings.ipynb    # Visual data exploration
│   ├── Performance_Analytics.ipynb # Day 4 performance calculations
│   └── 05_advanced_analytics.ipynb  # Day 6 risk and behavioral models
│
├── reports/                  # Client deliverables
│   ├── figures/              # Analytical charts (Sharpe charts, concentration HHI charts)
│   ├── Presentation.pptx     # 12-slide client presentation deck
│   └── Final_Report.pdf      # Multi-page executive PDF report
│
├── dashboard/                # Business intelligence assets
│   └── Dashboard_Build_Guide.md # Guide for Power BI / Tableau dashboard setup
│
├── run_pipeline.py           # Master pipeline orchestrator script
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Installation & Setup

1. **Clone or Open Workspace:**
   Ensure you are in the project root directory:
   ```bash
   cd bluestock_mf_capstone
   ```

2. **Set Up Python Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate     # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install reportlab python-pptx
   ```

---

## Running the Analytics Pipeline

You can run the entire data engineering, metrics calculation, and deliverable compilation workflow sequentially in a single step using the orchestrator:

```bash
python run_pipeline.py
```

### Steps Executed by the Pipeline:
1. **Data Ingestion:** Gathers raw mutual fund records.
2. **Data Cleaning:** Imputes missing NAVs (FFill), filters transaction anomalies (amount <= 0), and standardizes naming conventions.
3. **Database Loading:** Builds the SQLite star schema tables in `db/bluestock_mf.db` and loads the cleaned datasets.
4. **Performance Calculations:** Computes CAGR (1y/3y/5y), Sharpe and Sortino ratios, and OLS regression Alpha and Beta against the Nifty 100 benchmark.
5. **Advanced Risk Analytics:** Computes Historical VaR & CVaR (95%), sector HHI concentration metrics, rolling Sharpe ratios, and investor acquisition cohorts.
6. **Report Compilation:** Programmatically builds `reports/Presentation.pptx` and `reports/Final_Report.pdf`.

---

## Interactive Fund Recommender CLI

Advisors can run the recommender engine directly from the command line:

```bash
python scripts/recommender.py
```

### Command Line Arguments:
You can also bypass interactive prompts by providing arguments:
```bash
python scripts/recommender.py --risk High --category Equity
```

---

## Key Business Insights & Highlights

- **SIP Retention Warning:** Over **97% of active SIP investors** were flagged as 'at-risk' due to payment gaps exceeding 35 days, indicating a critical need for automated payment reminders and mandate monitoring.
- **Regular vs. Direct Plan Drag:** Regular plans charge an average of **0.8% - 1.2% higher expense ratios** than Direct plans, which acts as a major drag on annualized compounding returns and portfolio Sharpe ratios.
- **Tail-Risk Clustering:** High sector concentration (HHI > 2500) was detected in thematic equity funds, resulting in a daily VaR 95% of up to -2.3%, highlighting the importance of blending them with liquid and debt funds to cushion drawdowns.
