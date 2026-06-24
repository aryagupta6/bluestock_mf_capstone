# Python Scripts Directory

This folder houses the core Python scripts containing the programmatic ETL, analytical engines, CLI tools, and deliverable compilers.

## Script Descriptions

- **`data_ingestion.py`**: Handles acquiring raw files.
- **`data_cleaning.py`**: Performs preprocessing, FFill imputation, transaction sanitization, and name standardisation.
- **`db_loader.py`**: Connects to the SQLite database, executes the schema DDL, and loads processed tables.
- **`compute_metrics.py`**: Calculates the performance metrics (returns, CAGR, Sharpe/Sortino ratios, Max Drawdown, OLS Alpha/Beta) and generates the weighted fund scorecard.
- **`advanced_analytics.py`**: Performs risk tail-risk modeling (VaR/CVaR), rolling Sharpe calculations, cohort behavioral grouping, SIP continuity checks, and sector HHI computations.
- **`recommender.py`**: CLI interactive engine matching client risk profiles and categories to the top 3 optimal funds sorted by Sharpe ratio.
- **`generate_delivery_files.py`**: Automated compiler generating `reports/Presentation.pptx` and `reports/Final_Report.pdf`.
