import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup paths
DB_PATH = "db/bluestock_mf.db"
OUTPUT_DIR = "data/processed"
FIGURES_DIR = "reports/figures"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Risk-free rate (annualized)
RF_ANNUAL = 0.065
RF_DAILY = RF_ANNUAL / 252

def load_connection():
    """Establishes and returns a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        # Fallback to root directory database if db/ folder copy is missing
        if os.path.exists("bluestock_mf.db"):
            os.makedirs("db", exist_ok=True)
            import shutil
            shutil.copy("bluestock_mf.db", DB_PATH)
        else:
            raise FileNotFoundError(f"Database not found at {DB_PATH} or root folder.")
    return sqlite3.connect(DB_PATH)

def compute_var_cvar():
    """Computes Historical VaR (95%) and CVaR (95%) for all funds."""
    print("[*] Computing Historical Value at Risk (VaR) and Conditional VaR (CVaR)...")
    conn = load_connection()
    
    # Query daily returns
    query = """
    SELECT f.amfi_code, f.scheme_name, n.nav_date, n.daily_return
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
    WHERE n.daily_return IS NOT NULL;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    results = []
    for (amfi_code, scheme_name), group in df.groupby(['amfi_code', 'scheme_name']):
        rets = group['daily_return'].values
        if len(rets) >= 30: # Ensure sufficient history for risk calculations
            # 5th percentile return
            var_95 = np.percentile(rets, 5)
            # Average of returns below or equal to VaR 95%
            cvar_95 = rets[rets <= var_95].mean()
            results.append({
                'amfi_code': amfi_code,
                'scheme_name': scheme_name,
                'var_95_pct': var_95 * 100, # convert to percentage
                'cvar_95_pct': cvar_95 * 100
            })
        else:
            results.append({
                'amfi_code': amfi_code,
                'scheme_name': scheme_name,
                'var_95_pct': np.nan,
                'cvar_95_pct': np.nan
            })
            
    df_var = pd.DataFrame(results)
    var_csv_path = os.path.join(OUTPUT_DIR, "var_cvar_report.csv")
    df_var.to_csv(var_csv_path, index=False)
    print(f"[+] VaR/CVaR calculations completed. Saved to {var_csv_path}")
    return df_var

def plot_rolling_sharpe():
    """Computes and plots rolling 90-day Sharpe ratio for the top 5 funds by overall Sharpe ratio."""
    print("[*] Computing rolling 90-day Sharpe ratios for top 5 funds...")
    conn = load_connection()
    
    # Fetch performance to identify top 5 funds by Sharpe ratio
    perf_df = pd.read_sql_query("SELECT amfi_code, scheme_name, sharpe_ratio FROM fact_performance;", conn)
    
    # Drop NaNs or infinite values and select top 5
    perf_df = perf_df.dropna(subset=['sharpe_ratio'])
    top_5 = perf_df.nlargest(5, 'sharpe_ratio')
    top_5_codes = top_5['amfi_code'].tolist()
    top_5_names = top_5['scheme_name'].tolist()
    
    print("    - Top 5 funds selected:")
    for idx, row in top_5.iterrows():
        print(f"      Code: {row['amfi_code']} | {row['scheme_name']} (Sharpe: {row['sharpe_ratio']:.4f})")
        
    # Fetch NAV return timeseries for these 5 funds
    top_codes_str = ",".join(str(c) for c in top_5_codes)
    nav_query = f"""
    SELECT amfi_code, nav_date, daily_return
    FROM fact_nav
    WHERE amfi_code IN ({top_codes_str}) AND daily_return IS NOT NULL
    ORDER BY amfi_code, nav_date;
    """
    df_nav = pd.read_sql_query(nav_query, conn)
    df_nav['nav_date'] = pd.to_datetime(df_nav['nav_date'])
    conn.close()
    
    plt.figure(figsize=(12, 6))
    
    for code in top_5_codes:
        name = top_5[top_5['amfi_code'] == code]['scheme_name'].values[0]
        # Clean name for legend
        clean_name = name.split(" - ")[0]
        
        fund_nav = df_nav[df_nav['amfi_code'] == code].sort_values('nav_date')
        
        if len(fund_nav) >= 90:
            # Calculate rolling mean and standard deviation
            rolling_mean = fund_nav['daily_return'].rolling(window=90).mean()
            rolling_std = fund_nav['daily_return'].rolling(window=90).std(ddof=1)
            
            # Annualized rolling Sharpe
            rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)
            
            plt.plot(fund_nav['nav_date'], rolling_sharpe, label=clean_name, linewidth=1.8)
            
    plt.title("Rolling 90-Day Sharpe Ratio for Top 5 Funds (2022-2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, labelpad=10)
    plt.ylabel("Annualized Rolling Sharpe Ratio", fontsize=11, labelpad=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="best", frameon=True, shadow=False)
    plt.tight_layout()
    
    chart_path = os.path.join(FIGURES_DIR, "rolling_sharpe_chart.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"[+] Rolling Sharpe ratio chart saved to {chart_path}")

def run_cohort_analysis():
    """Performs investor cohort analysis (2024 vs 2025 cohorts)."""
    print("[*] Performing investor cohort analysis...")
    conn = load_connection()
    
    # Query transactions and fund names
    query = """
    SELECT t.investor_id, t.transaction_date, t.transaction_type, t.amount_inr, f.scheme_name
    FROM fact_transactions t
    LEFT JOIN dim_fund f ON t.amfi_code = f.amfi_code;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['year'] = df['transaction_date'].dt.year
    
    # 1. Identify first transaction date and year for each investor
    first_tx = df.groupby('investor_id')['transaction_date'].min().reset_index()
    first_tx.columns = ['investor_id', 'first_tx_date']
    first_tx['cohort_year'] = first_tx['first_tx_date'].dt.year
    
    # Merge cohort classification back to transactions
    df = df.merge(first_tx[['investor_id', 'cohort_year']], on='investor_id', how='left')
    
    cohort_data = []
    for year in [2024, 2025]:
        cohort_df = df[df['cohort_year'] == year]
        unique_investors = cohort_df['investor_id'].nunique()
        
        # Average SIP size
        sip_tx = cohort_df[cohort_df['transaction_type'] == 'SIP']
        avg_sip_size = sip_tx['amount_inr'].mean() if len(sip_tx) > 0 else 0
        
        # Total invested capital (SIP + Lumpsum)
        invested_tx = cohort_df[cohort_df['transaction_type'].isin(['SIP', 'Lumpsum'])]
        total_invested = invested_tx['amount_inr'].sum()
        
        # Top fund preference (by transaction count)
        fund_counts = cohort_df['scheme_name'].value_counts()
        top_fund = fund_counts.index[0] if len(fund_counts) > 0 else "N/A"
        top_fund_count = fund_counts.values[0] if len(fund_counts) > 0 else 0
        
        cohort_data.append({
            'cohort_year': year,
            'investor_count': unique_investors,
            'avg_sip_size_inr': avg_sip_size,
            'total_invested_inr': total_invested,
            'top_preferred_fund': top_fund,
            'top_fund_transaction_count': top_fund_count
        })
        
    df_cohort = pd.DataFrame(cohort_data)
    cohort_csv_path = os.path.join(OUTPUT_DIR, "cohort_analysis.csv")
    df_cohort.to_csv(cohort_csv_path, index=False)
    print(f"[+] Cohort analysis completed. Saved to {cohort_csv_path}")
    print(df_cohort)
    return df_cohort

def run_sip_continuity_analysis():
    """Performs SIP continuity analysis (flags gaps > 35 days for clients with 6+ SIPs)."""
    print("[*] Performing SIP continuity analysis...")
    conn = load_connection()
    
    # Query SIP transactions
    query = """
    SELECT investor_id, transaction_date, amount_inr
    FROM fact_transactions
    WHERE transaction_type = 'SIP'
    ORDER BY investor_id, transaction_date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    results = []
    for investor_id, group in df.groupby('investor_id'):
        sip_count = len(group)
        if sip_count >= 6:
            # Sort chronologically and calculate gaps between consecutive transactions
            group = group.sort_values('transaction_date')
            gaps = group['transaction_date'].diff().dt.days.dropna()
            
            avg_gap = gaps.mean() if len(gaps) > 0 else 0
            # Flag if average gap exceeds 35 days
            is_at_risk = 1 if avg_gap > 35 else 0
            
            results.append({
                'investor_id': investor_id,
                'sip_count': sip_count,
                'average_gap_days': avg_gap,
                'is_at_risk': is_at_risk
            })
            
    df_sip = pd.DataFrame(results)
    sip_csv_path = os.path.join(OUTPUT_DIR, "sip_continuity.csv")
    df_sip.to_csv(sip_csv_path, index=False)
    
    total_at_risk = df_sip['is_at_risk'].sum()
    print(f"[+] SIP continuity analysis completed. Saved to {sip_csv_path}")
    print(f"    - Analyzed {len(df_sip)} active investors (with 6+ SIPs)")
    print(f"    - Flagged {total_at_risk} ({total_at_risk/len(df_sip)*100:.1f}%) investors as 'at-risk' (average gap > 35 days)")
    return df_sip

def run_sector_concentration_hhi():
    """Calculates Herfindahl-Hirschman Index (HHI) of stock holdings' sector weights for equity funds."""
    print("[*] Performing sector concentration analysis (HHI)...")
    conn = load_connection()
    
    # Fetch portfolio holdings and join with dim_fund to check categories
    query = """
    SELECT h.amfi_code, f.scheme_name, f.category, h.sector, h.weight_pct
    FROM fact_portfolio_holdings h
    JOIN dim_fund f ON h.amfi_code = f.amfi_code
    WHERE f.category = 'Equity';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    results = []
    for (amfi_code, scheme_name), group in df.groupby(['amfi_code', 'scheme_name']):
        # Sum weight_pct by sector (in case a fund holds multiple stocks in the same sector)
        sector_weights = group.groupby('sector')['weight_pct'].sum()
        
        # Normalize weights so they sum to 100% of the portfolio holdings
        total_weight = sector_weights.sum()
        if total_weight > 0:
            norm_weights = (sector_weights / total_weight) * 100
            # HHI is sum of squared sector weights
            hhi = (norm_weights ** 2).sum()
            results.append({
                'amfi_code': amfi_code,
                'scheme_name': scheme_name,
                'hhi_score': hhi
            })
            
    df_hhi = pd.DataFrame(results)
    hhi_csv_path = os.path.join(OUTPUT_DIR, "sector_hhi.csv")
    df_hhi.to_csv(hhi_csv_path, index=False)
    print(f"[+] Sector HHI analysis completed. Saved to {hhi_csv_path}")
    
    # Plot concentration chart
    plt.figure(figsize=(10, 5))
    # Classify HHI concentration levels
    # < 1500: Diversified, 1500-2500: Moderate, > 2500: Concentrated
    bins = [0, 1500, 2500, 10000]
    labels = ['Low Concentration (<1500)', 'Moderate (1500-2500)', 'High Concentration (>2500)']
    df_hhi['concentration_level'] = pd.cut(df_hhi['hhi_score'], bins=bins, labels=labels)
    
    counts = df_hhi['concentration_level'].value_counts().reindex(labels).fillna(0)
    
    colors = ['#2ec4b6', '#ff9f1c', '#e71d36'] # Custom premium color scheme
    
    bars = plt.bar(counts.index, counts.values, color=colors, edgecolor='grey', width=0.6)
    
    # Add count values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, f"{int(yval)}", ha='center', va='bottom', fontweight='bold')
        
    plt.title("Equity Mutual Funds by Sector Concentration Risk (HHI)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Sector Concentration Category (Herfindahl-Hirschman Index)", fontsize=11, labelpad=10)
    plt.ylabel("Number of Mutual Funds", fontsize=11, labelpad=10)
    plt.ylim(0, max(counts.values) * 1.15)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    chart_path = os.path.join(FIGURES_DIR, "sector_hhi_chart.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"[+] Sector concentration HHI chart saved to {chart_path}")
    return df_hhi

def main():
    print("="*60)
    print("ADVANCED ANALYTICS & RISK METRICS ENGINE (DAY 6)")
    print("="*60)
    
    compute_var_cvar()
    plot_rolling_sharpe()
    run_cohort_analysis()
    run_sip_continuity_analysis()
    run_sector_concentration_hhi()
    
    print("="*60)
    print("[+] All advanced analytics tasks completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
