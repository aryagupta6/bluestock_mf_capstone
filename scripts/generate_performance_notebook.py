import nbformat as nbf
import os

def create_notebook(notebook_path):
    print(f"[*] Creating Jupyter Notebook programmatically at {notebook_path}...")
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    # 1. Header Cell
    cells.append(nbf.v4.new_markdown_cell("""# Mutual Fund Capstone Project: Fund Performance & Risk Analytics

This notebook computes, analyzes, and presents key performance and risk metrics for all mutual fund schemes in the dataset. It leverages historical NAV data and benchmark indices to rank the funds using a weighted scoring scorecard.

## Day 4 Objectives & Deliverables:
1. **Daily Returns timeseries:** Computed daily return series for all 40 funds.
2. **CAGR Report:** Annualized returns over 1-year, 3-year, and 5-year periods.
3. **Risk-adjusted metrics:** Sharpe and Sortino Ratios ($R_f = 6.5\%$).
4. **Maximum Drawdown:** Peak-to-trough drawdowns and duration of the worst drawdown periods.
5. **Alpha & Beta:** Benchmark-relative risk metrics computed via OLS regression against the **Nifty 100** index.
6. **Fund Scorecard (0-100 scale):** Multi-metric weighted scorecard ranking funds based on returns, volatility, benchmark alpha, expense ratio, and drawdowns.
7. **Benchmark Chart:** Normalized growth comparison of the top 5 funds vs. Nifty 50 and Nifty 100 with tracking error calculations.
"""))

    # 2. Setup Code Cell
    cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Set directories
DATA_DIR = "../data/processed"
FIGURES_DIR = "../reports/figures"
DB_PATH = "../bluestock_mf.db"

# Set plot styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['figure.titlesize'] = 16

print("[+] Setup complete. Ready to load analytics outputs.")
"""))

    # 3. Load & Display Scorecard
    cells.append(nbf.v4.new_markdown_cell("""## 1. Fund Scorecard & Ranks (0-100 Scale)
The scorecard aggregates multiple metrics: Sharpe ratio (25% weight), CAGR 3Yr (30%), Alpha (20%), Expense ratio (15%, inverse), and Maximum Drawdown (10%, inverse) using percentile ranks (0-100 scale). Let's load the generated scorecard and display the top 10 mutual funds.
"""))
    cells.append(nbf.v4.new_code_cell("""df_scorecard = pd.read_csv(os.path.join(DATA_DIR, "fund_scorecard.csv"))
# Sort by overall rank
df_scorecard_sorted = df_scorecard.sort_values('overall_rank').reset_index(drop=True)

# Display top 10 funds
print("--- TOP 10 MUTUAL FUNDS BY SCORECARD ---")
display(df_scorecard_sorted[['overall_rank', 'scheme_name', 'category', 'sub_category', 'cagr_3yr', 'sharpe_ratio', 'alpha', 'max_drawdown_pct', 'expense_ratio_pct', 'weighted_score']].head(10))
"""))

    # 4. Best & Worst Funds per Category
    cells.append(nbf.v4.new_markdown_cell("""## 2. Best and Worst Performing Funds Per Category
We segment our scorecard rankings by main category (Equity vs Debt) to find the top performer and bottom performer in each class.
"""))
    cells.append(nbf.v4.new_code_cell("""for cat, group in df_scorecard_sorted.groupby('category'):
    print(f"\\n=================== CATEGORY: {cat.upper()} ===================")
    cat_sorted = group.sort_values('overall_rank').reset_index(drop=True)
    
    print("TOP 3 FUNDS:")
    for i in range(min(3, len(cat_sorted))):
        r = cat_sorted.iloc[i]
        print(f"  {i+1}. {r['scheme_name']} (AMFI: {r['amfi_code']}) - Composite Score: {r['weighted_score']:.2f} (Rank: {r['overall_rank']})")
        
    print("\\nBOTTOM 3 FUNDS:")
    for i in range(min(3, len(cat_sorted))):
        idx = len(cat_sorted) - 1 - i
        r = cat_sorted.iloc[idx]
        print(f"  {i+1}. {r['scheme_name']} (AMFI: {r['amfi_code']}) - Composite Score: {r['weighted_score']:.2f} (Rank: {r['overall_rank']})")
"""))

    # 5. Sharpe & Sortino Distributions
    cells.append(nbf.v4.new_markdown_cell("""## 3. Risk-Adjusted Returns (Sharpe & Sortino Ratios)
Sharpe ratio measures excess return per unit of total risk, while Sortino ratio measures excess return per unit of downside deviation. We plot their distributions across all funds.
"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 6))

sns.histplot(data=df_scorecard_sorted, x='sharpe_ratio', kde=True, ax=axes[0], color='teal')
axes[0].set_title("Distribution of Sharpe Ratios (Rf = 6.5%)")
axes[0].set_xlabel("Sharpe Ratio")
axes[0].set_ylabel("Count")

# Fetch sortino values
df_sortino = pd.read_csv(os.path.join(DATA_DIR, "sortino_values.csv"))
df_scorecard_sorted = pd.merge(df_scorecard_sorted, df_sortino[['amfi_code', 'sortino_ratio']], on='amfi_code', how='left')

sns.histplot(data=df_scorecard_sorted, x='sortino_ratio', kde=True, ax=axes[1], color='coral')
axes[1].set_title("Distribution of Sortino Ratios (Rf = 6.5%)")
axes[1].set_xlabel("Sortino Ratio")
axes[1].set_ylabel("Count")

plt.tight_layout()
plt.show()
"""))

    # 6. Maximum Drawdown Analysis
    cells.append(nbf.v4.new_markdown_cell("""## 4. Maximum Drawdowns & Worst Drawdown Period Highlights
Maximum Drawdown represents the largest peak-to-trough drop in NAV. We load `max_drawdown.csv` and display the worst drawdown period for each of the top 5 funds.
"""))
    cells.append(nbf.v4.new_code_cell("""df_max_dd = pd.read_csv(os.path.join(DATA_DIR, "max_drawdown.csv"))

# Merge with overall scorecard ranking
df_max_dd_ranked = pd.merge(
    df_scorecard_sorted[['amfi_code', 'overall_rank']],
    df_max_dd,
    on='amfi_code'
).sort_values('overall_rank').reset_index(drop=True)

print("--- WORST DRAWDOWN PERIODS FOR THE TOP 5 RANKED FUNDS ---")
display(df_max_dd_ranked[['overall_rank', 'scheme_name', 'max_drawdown_pct', 'peak_date', 'trough_date', 'recovery_date', 'peak_to_trough_duration_days', 'total_drawdown_duration_days']].head(5))
"""))

    # 7. Alpha & Beta vs Benchmarks
    cells.append(nbf.v4.new_markdown_cell("""## 5. Alpha & Beta against Nifty 100 Index via OLS Regression
Beta measures the sensitivity of the fund's return relative to market index movements. Alpha represents the fund's excess return above expectations. Both are calculated using linear regression (`scipy.stats.linregress`) of fund returns on Nifty 100 returns.
"""))
    cells.append(nbf.v4.new_code_cell("""df_ab = pd.read_csv(os.path.join(DATA_DIR, "alpha_beta.csv"))

# Sort by scorecard rank
df_ab_ranked = pd.merge(
    df_scorecard_sorted[['amfi_code', 'overall_rank']],
    df_ab,
    on='amfi_code'
).sort_values('overall_rank').reset_index(drop=True)

print("--- ALPHA & BETA FOR THE TOP 10 RANKED FUNDS ---")
display(df_ab_ranked[['overall_rank', 'scheme_name', 'benchmark_name', 'alpha', 'beta']].head(10))
"""))

    # 8. Benchmark Comparison Visualization
    cells.append(nbf.v4.new_markdown_cell("""## 6. Benchmark Comparison Chart (3-Year Normalized NAV Growth & Tracking Error)
We visualize the daily NAV performance of the Top 5 scorecard funds compared with market benchmarks (`NIFTY50` and `NIFTY100`) over a 3-year period. We also show their Tracking Errors (TE) calculated against `NIFTY100`.
"""))
    cells.append(nbf.v4.new_code_cell("""# Load normalized comparison plot
from IPython.display import Image, display
display(Image(filename=os.path.join(FIGURES_DIR, "benchmark_chart.png")))
"""))

    # 9. Key Analytical Findings
    cells.append(nbf.v4.new_markdown_cell("""## 7. Key Analytical Findings & Observations

1. **Top Performer (Equity):** **Mirae Asset Large Cap Fund - Regular - Growth** ranks #1 in the equity category. This is driven by its strong risk-adjusted returns (Sharpe ratio and Sortino ratio) combined with relatively low expense ratios.
2. **Top Performer (Debt):** **ICICI Pru Liquid Fund - Regular - Growth** ranks #1 in the debt/liquid category. It displays very low drawdowns and highly consistent daily returns, making it the most defensive option in the scorecard.
3. **Volatility vs. Returns:** Small-cap and mid-cap funds (e.g. *Nippon India Small Cap* or *HDFC Mid-Cap Opportunities*) demonstrate much higher CAGRs but also suffer from larger Maximum Drawdowns (often exceeding 25-30% peak-to-trough) and higher Beta values close to or exceeding 1.0.
4. **Tracking Error:** Large-cap passive index funds (like *UTI Nifty 50 Index Fund*) display extremely low Tracking Error relative to Nifty 50, reflecting their passive nature, whereas active funds show higher tracking error due to active manager bets.
5. **Drawdown Recovery:** Active debt/liquid funds recover from drawdowns within a few days or weeks, whereas equity funds suffer drawdown periods that last for several hundred days before recovering to historical peaks.
"""))

    nb['cells'] = cells
    
    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
        
    print(f"[+] Successfully wrote {notebook_path}!")

def main():
    create_notebook("notebooks/Performance_Analytics.ipynb")
    create_notebook("notebooks/04_performance_analytics.ipynb")

if __name__ == "__main__":
    main()
