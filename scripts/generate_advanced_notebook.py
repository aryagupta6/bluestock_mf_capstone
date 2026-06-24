import nbformat as nbf
import os

def create_notebook(notebook_path):
    print(f"[*] Creating Advanced Analytics Jupyter Notebook at {notebook_path}...")
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    # 1. Title / Intro
    cells.append(nbf.v4.new_markdown_cell("""# Day 6: Advanced Analytics & Risk Metrics (Mutual Fund Capstone)

This notebook presents advanced risk analytics, investor behavioral models, and portfolio concentration metrics. 

### Key Analytics Performed:
1. **Value at Risk (VaR) & Conditional VaR (CVaR):** 95% confidence historical downside risk metrics.
2. **Rolling 90-Day Sharpe Ratios:** Time-varying risk-adjusted performance of the top 5 funds.
3. **Investor Cohort Analysis:** Behavioral analysis comparing investors who joined in 2024 vs. 2025.
4. **SIP Continuity & At-Risk Analysis:** Identifying accounts showing signs of potential default (average transaction gaps > 35 days).
5. **Sector Concentration (HHI):** Portfolio diversification check using the Herfindahl-Hirschman Index on equity sectors.
"""))

    # 2. Setup
    cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Directories
DATA_DIR = "../data/processed"
FIGURES_DIR = "../reports/figures"
DB_PATH = "../db/bluestock_mf.db"

# Plot styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

print("[+] Environment initialized.")
"""))

    # 3. VaR & CVaR
    cells.append(nbf.v4.new_markdown_cell("""## 1. Downside Risk: Historical Value at Risk (VaR) & CVaR (95%)
Value at Risk (VaR) represents the worst-case loss expected at a 95% confidence level over a one-day horizon. Conditional VaR (CVaR) measures the average loss on days where the return drops below the 95% VaR threshold.
"""))
    cells.append(nbf.v4.new_code_cell("""df_var = pd.read_csv(os.path.join(DATA_DIR, "var_cvar_report.csv"))
df_var_sorted = df_var.sort_values(by="var_95_pct").reset_index(drop=True)

print("--- TOP 10 RISKIEST FUNDS (Highest negative VaR) ---")
display(df_var_sorted.head(10))

print("\\n--- TOP 10 SAFEST FUNDS (Lowest negative VaR) ---")
display(df_var_sorted.tail(10))
"""))

    # 4. Rolling Sharpe
    cells.append(nbf.v4.new_markdown_cell("""## 2. Rolling 90-Day Sharpe Ratio
Below is the pre-computed rolling 90-day Sharpe ratio timeseries chart for the top 5 performing funds in our universe. This showcases how the risk-adjusted return profile varies over time.
"""))
    cells.append(nbf.v4.new_code_cell("""from IPython.display import Image, display as ipy_display
chart_path = os.path.join(FIGURES_DIR, "rolling_sharpe_chart.png")
if os.path.exists(chart_path):
    ipy_display(Image(filename=chart_path))
else:
    print("[-] Rolling Sharpe chart not found. Run advanced_analytics.py first.")
"""))

    # 5. Cohort Analysis
    cells.append(nbf.v4.new_markdown_cell("""## 3. Investor Cohort Analysis (2024 vs. 2025)
Grouping investors by their acquisition year (first transaction year) allows us to analyze changes in behavioral patterns, transaction sizing, and asset preferences.
"""))
    cells.append(nbf.v4.new_code_cell("""df_cohort = pd.read_csv(os.path.join(DATA_DIR, "cohort_analysis.csv"))
print("--- COHORT BEHAVIOR ANALYSIS ---")
display(df_cohort)
"""))

    # 6. SIP Continuity
    cells.append(nbf.v4.new_markdown_cell("""## 4. SIP Continuity & At-Risk Accounts
For clients with 6 or more monthly transactions, we calculate the average gap in days. Gaps consistently exceeding 35 days indicate a high probability of SIP default or halt.
"""))
    cells.append(nbf.v4.new_code_cell("""df_sip = pd.read_csv(os.path.join(DATA_DIR, "sip_continuity.csv"))
df_at_risk = df_sip[df_sip['is_at_risk'] == 1].reset_index(drop=True)

print(f"Total active SIP clients analyzed: {len(df_sip)}")
print(f"Total clients flagged as 'At Risk' (gap > 35 days): {len(df_at_risk)}")

print("\\n--- SAMPLE OF AT-RISK SIP ACCOUNTS ---")
display(df_at_risk.head(10))
"""))

    # 7. Sector HHI
    cells.append(nbf.v4.new_markdown_cell("""## 5. Sector Concentration Analysis (HHI)
The Herfindahl-Hirschman Index (HHI) evaluates the diversification level of equity fund holdings. 
- **HHI < 1500:** Well-diversified sector exposure.
- **HHI 1500 - 2500:** Moderate sector concentration.
- **HHI > 2500:** High sector concentration (focused thematic or sector funds).
"""))
    cells.append(nbf.v4.new_code_cell("""df_hhi = pd.read_csv(os.path.join(DATA_DIR, "sector_hhi.csv"))
print("--- HIGHLY CONCENTRATED FUNDS (Top 5) ---")
display(df_hhi.sort_values('hhi_score', ascending=False).head(5))

print("\\n--- WELL DIVERSIFIED FUNDS (Top 5) ---")
display(df_hhi.sort_values('hhi_score').head(5))

chart_path_hhi = os.path.join(FIGURES_DIR, "sector_hhi_chart.png")
if os.path.exists(chart_path_hhi):
    ipy_display(Image(filename=chart_path_hhi))
"""))

    nb['cells'] = cells
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"[+] Notebook created successfully at {notebook_path}.")

if __name__ == "__main__":
    notebook_file = os.path.join("notebooks", "05_advanced_analytics.ipynb")
    os.makedirs("notebooks", exist_ok=True)
    create_notebook(notebook_file)
