import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Setup paths
DB_PATH = "db/bluestock_mf.db"
OUTPUT_DIR = "data/processed"
FIGURES_DIR = "reports/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Create db/ directory and check/copy database if not present to match PDF structure
os.makedirs("db", exist_ok=True)
if not os.path.exists(DB_PATH) and os.path.exists("bluestock_mf.db"):
    import shutil
    shutil.copy("bluestock_mf.db", DB_PATH)

# Risk-free rate (6.5%)
RF = 0.065

def load_data():
    conn = sqlite3.connect(DB_PATH)
    
    # Load funds master
    df_funds = pd.read_sql_query("SELECT * FROM dim_fund;", conn)
    
    # Load NAV history
    df_nav = pd.read_sql_query("SELECT * FROM fact_nav;", conn)
    df_nav['nav_date'] = pd.to_datetime(df_nav['nav_date'])
    df_nav = df_nav.sort_values(by=['amfi_code', 'nav_date']).reset_index(drop=True)
    
    # Load Benchmark indices
    df_bench = pd.read_sql_query("SELECT * FROM fact_benchmark;", conn)
    df_bench['date'] = pd.to_datetime(df_bench['date'])
    df_bench = df_bench.sort_values(by=['index_name', 'date']).reset_index(drop=True)
    
    conn.close()
    return df_funds, df_nav, df_bench

def main():
    print("="*60)
    print("COMPUTE METRICS ENGINE (DAY 4)")
    print("="*60)
    
    # Load data
    df_funds, df_nav, df_bench = load_data()
    print(f"[+] Loaded {len(df_funds)} funds, {len(df_nav)} NAV records, and {len(df_bench)} benchmark records.")
    
    # --- TASK 1: Compute Daily Returns & Annualized Returns ---
    print("\n[*] Running Task 1: Computing Daily & Annualized Returns...")
    
    # Calculate daily returns
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    # Save returns computed timeseries
    returns_csv_path = os.path.join(OUTPUT_DIR, "returns_computed.csv")
    df_nav.to_csv(returns_csv_path, index=False)
    print(f"    - Saved daily returns to {returns_csv_path}")
    
    # Compute annualized return per fund: (1 + daily_return).prod() ** (252 / n) - 1
    fund_annualized_returns = {}
    for code, group in df_nav.groupby('amfi_code'):
        rets = group['daily_return'].dropna()
        n = len(rets)
        if n > 0:
            ann_ret = (1 + rets).prod() ** (252 / n) - 1
            fund_annualized_returns[code] = ann_ret
        else:
            fund_annualized_returns[code] = np.nan
            
    # --- TASK 2: Calculate CAGR for 1yr, 3yr, 5yr ---
    print("\n[*] Running Task 2: Calculating CAGR (1yr, 3yr, 5yr)...")
    
    cagr_records = []
    for code, group in df_nav.groupby('amfi_code'):
        scheme_name = df_funds[df_funds['amfi_code'] == code]['scheme_name'].values[0]
        group = group.sort_values('nav_date').reset_index(drop=True)
        end_date = group['nav_date'].max()
        nav_end = group[group['nav_date'] == end_date]['nav'].values[0]
        
        cagr_vals = {}
        for years in [1, 3, 5]:
            target_start = end_date - pd.DateOffset(years=years)
            if group['nav_date'].min() <= target_start:
                idx = (group['nav_date'] - target_start).abs().idxmin()
                row_start = group.loc[idx]
                nav_start = row_start['nav']
                actual_years = (end_date - row_start['nav_date']).days / 365.25
                cagr = (nav_end / nav_start) ** (1.0 / actual_years) - 1.0
                cagr_vals[years] = cagr
            else:
                cagr_vals[years] = np.nan
                
        cagr_records.append({
            'amfi_code': code,
            'scheme_name': scheme_name,
            'cagr_1yr': cagr_vals[1],
            'cagr_3yr': cagr_vals[3],
            'cagr_5yr': cagr_vals[5]
        })
        
    df_cagr = pd.DataFrame(cagr_records)
    cagr_csv_path = os.path.join(OUTPUT_DIR, "cagr_report.csv")
    df_cagr.to_csv(cagr_csv_path, index=False)
    print(f"    - Saved CAGR report to {cagr_csv_path}")
    
    # --- TASK 3: Compute Sharpe Ratio ---
    print("\n[*] Running Task 3: Computing Sharpe Ratios...")
    
    sharpe_records = []
    for code, group in df_nav.groupby('amfi_code'):
        scheme_name = df_funds[df_funds['amfi_code'] == code]['scheme_name'].values[0]
        rets = group['daily_return'].dropna()
        n = len(rets)
        if n > 1:
            ann_ret = fund_annualized_returns[code]
            daily_std = rets.std(ddof=1)
            ann_std = daily_std * np.sqrt(252)
            sharpe = (ann_ret - RF) / ann_std if ann_std > 0 else np.nan
            sharpe_records.append({
                'amfi_code': code,
                'scheme_name': scheme_name,
                'annualized_return': ann_ret,
                'annualized_std': ann_std,
                'sharpe_ratio': sharpe
            })
        else:
            sharpe_records.append({
                'amfi_code': code,
                'scheme_name': scheme_name,
                'annualized_return': np.nan,
                'annualized_std': np.nan,
                'sharpe_ratio': np.nan
            })
            
    df_sharpe = pd.DataFrame(sharpe_records)
    sharpe_csv_path = os.path.join(OUTPUT_DIR, "sharpe_values.csv")
    df_sharpe.to_csv(sharpe_csv_path, index=False)
    print(f"    - Saved Sharpe ratios to {sharpe_csv_path}")
    
    # --- TASK 4: Compute Sortino Ratio ---
    print("\n[*] Running Task 4: Computing Sortino Ratios...")
    
    sortino_records = []
    for code, group in df_nav.groupby('amfi_code'):
        scheme_name = df_funds[df_funds['amfi_code'] == code]['scheme_name'].values[0]
        rets = group['daily_return'].dropna()
        ann_ret = fund_annualized_returns[code]
        
        neg_rets = rets[rets < 0]
        if len(neg_rets) > 1:
            downside_std = neg_rets.std(ddof=1) * np.sqrt(252)
            sortino = (ann_ret - RF) / downside_std if downside_std > 0 else np.nan
        else:
            sortino = np.nan
            
        sortino_records.append({
            'amfi_code': code,
            'scheme_name': scheme_name,
            'sortino_ratio': sortino
        })
        
    df_sortino = pd.DataFrame(sortino_records)
    sortino_csv_path = os.path.join(OUTPUT_DIR, "sortino_values.csv")
    df_sortino.to_csv(sortino_csv_path, index=False)
    print(f"    - Saved Sortino ratios to {sortino_csv_path}")
    
    # --- TASK 6: Compute Maximum Drawdown & Highlight Worst Period ---
    print("\n[*] Running Task 6: Computing Maximum Drawdown & Worst Drawdown Periods...")
    
    max_dd_records = []
    for code, group in df_nav.groupby('amfi_code'):
        scheme_name = df_funds[df_funds['amfi_code'] == code]['scheme_name'].values[0]
        group = group.sort_values('nav_date').reset_index(drop=True)
        
        navs = group['nav'].reset_index(drop=True)
        dates = group['nav_date'].reset_index(drop=True)
        
        running_max = navs.cummax()
        drawdowns = navs / running_max - 1.0
        
        min_dd_idx = drawdowns.idxmin()
        max_dd_val = drawdowns[min_dd_idx]
        
        trough_date = dates[min_dd_idx]
        trough_val = navs[min_dd_idx]
        
        peak_val = running_max[min_dd_idx]
        peak_idx = navs.loc[:min_dd_idx].idxmax()
        peak_date = dates[peak_idx]
        
        recovery_date = "Not Recovered"
        recovery_days = np.nan
        for j in range(min_dd_idx, len(navs)):
            if navs[j] >= peak_val:
                recovery_date = dates[j].strftime("%Y-%m-%d")
                recovery_days = (dates[j] - dates[peak_idx]).days
                break
                
        peak_to_trough_days = (dates[min_dd_idx] - dates[peak_idx]).days
        total_dd_days = recovery_days if not np.isnan(recovery_days) else (dates.iloc[-1] - dates[peak_idx]).days
        
        max_dd_records.append({
            'amfi_code': code,
            'scheme_name': scheme_name,
            'max_drawdown_pct': max_dd_val * 100,
            'peak_date': peak_date.strftime("%Y-%m-%d"),
            'peak_value': peak_val,
            'trough_date': trough_date.strftime("%Y-%m-%d"),
            'trough_value': trough_val,
            'recovery_date': recovery_date,
            'peak_to_trough_duration_days': peak_to_trough_days,
            'total_drawdown_duration_days': total_dd_days
        })
        
    df_max_dd = pd.DataFrame(max_dd_records)
    max_dd_csv_path = os.path.join(OUTPUT_DIR, "max_drawdown.csv")
    df_max_dd.to_csv(max_dd_csv_path, index=False)
    print(f"    - Saved Maximum Drawdown report to {max_dd_csv_path}")
    
    # --- TASK 5: Compute Alpha & Beta vs Benchmark (Regress on Nifty 100) ---
    print("\n[*] Running Task 5: Computing Alpha & Beta vs NIFTY 100 via OLS Regression...")
    
    # Filter Nifty 100 benchmark daily returns
    df_nifty100 = df_bench[df_bench['index_name'] == 'NIFTY100'].copy()
    df_nifty100['daily_return'] = df_nifty100['close_value'].pct_change()
    
    alpha_beta_records = []
    for code, group in df_nav.groupby('amfi_code'):
        fund_row = df_funds[df_funds['amfi_code'] == code].iloc[0]
        scheme_name = fund_row['scheme_name']
        benchmark_desc = fund_row['benchmark']
        
        # Merge returns on date
        df_merged = pd.merge(
            group[['nav_date', 'daily_return']],
            df_nifty100[['date', 'daily_return']],
            left_on='nav_date',
            right_on='date',
            suffixes=('_fund', '_bench')
        ).dropna()
        
        if len(df_merged) > 10:
            # Perform linear regression: R_p = Alpha_daily + Beta * R_b
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_merged['daily_return_bench'],
                df_merged['daily_return_fund']
            )
            beta = slope
            alpha = intercept * 252  # Annualize alpha
            
            alpha_beta_records.append({
                'amfi_code': code,
                'scheme_name': scheme_name,
                'benchmark_name': 'NIFTY 100 TRI',
                'alpha': alpha,
                'beta': beta
            })
        else:
            alpha_beta_records.append({
                'amfi_code': code,
                'scheme_name': scheme_name,
                'benchmark_name': 'NIFTY 100 TRI',
                'alpha': np.nan,
                'beta': np.nan
            })
            
    df_ab = pd.DataFrame(alpha_beta_records)
    ab_csv_path = os.path.join(OUTPUT_DIR, "alpha_beta.csv")
    df_ab.to_csv(ab_csv_path, index=False)
    print(f"    - Saved Alpha & Beta metrics (regressed vs Nifty 100) to {ab_csv_path}")
    
    # --- TASK 7: Build Fund Scorecard (Score 0-100) ---
    print("\n[*] Running Task 7: Building Weighted Scorecard (0-100)...")
    
    # Ranks (0-100 percentile rank)
    df_scorecard = df_funds[['amfi_code', 'scheme_name', 'category', 'sub_category', 'expense_ratio_pct']].copy()
    df_scorecard = pd.merge(df_scorecard, df_sharpe[['amfi_code', 'sharpe_ratio']], on='amfi_code', how='left')
    df_scorecard = pd.merge(df_scorecard, df_cagr[['amfi_code', 'cagr_3yr']], on='amfi_code', how='left')
    df_scorecard = pd.merge(df_scorecard, df_ab[['amfi_code', 'alpha']], on='amfi_code', how='left')
    df_scorecard = pd.merge(df_scorecard, df_max_dd[['amfi_code', 'max_drawdown_pct']], on='amfi_code', how='left')
    
    # Ranks: higher is better for CAGR, Sharpe, Alpha
    # lower is better for Expense Ratio and Max DD (less negative)
    df_scorecard['sharpe_pct'] = df_scorecard['sharpe_ratio'].rank(pct=True) * 100
    df_scorecard['cagr_3yr_pct'] = df_scorecard['cagr_3yr'].rank(pct=True) * 100
    df_scorecard['alpha_pct'] = df_scorecard['alpha'].rank(pct=True) * 100
    df_scorecard['expense_pct'] = df_scorecard['expense_ratio_pct'].rank(pct=True, ascending=False) * 100 # lower gets higher pct
    df_scorecard['max_dd_pct'] = df_scorecard['max_drawdown_pct'].rank(pct=True) * 100 # closer to 0 is higher value, so ascending=True matches
    
    # Fill NaNs with 0 (worst rank score)
    for col in ['sharpe_pct', 'cagr_3yr_pct', 'alpha_pct', 'expense_pct', 'max_dd_pct']:
        df_scorecard[col] = df_scorecard[col].fillna(0)
        
    # Score formula: 30% * CAGR + 25% * Sharpe + 20% * Alpha + 15% * Expense + 10% * Max DD
    df_scorecard['weighted_score'] = (
        0.30 * df_scorecard['cagr_3yr_pct'] +
        0.25 * df_scorecard['sharpe_pct'] +
        0.20 * df_scorecard['alpha_pct'] +
        0.15 * df_scorecard['expense_pct'] +
        0.10 * df_scorecard['max_dd_pct']
    )
    
    # Overall Rank (highest score is rank 1)
    df_scorecard['overall_rank'] = df_scorecard['weighted_score'].rank(ascending=False, method='min')
    
    scorecard_csv_path = os.path.join(OUTPUT_DIR, "fund_scorecard.csv")
    df_scorecard.to_csv(scorecard_csv_path, index=False)
    print(f"    - Saved Fund Scorecard (0-100) to {scorecard_csv_path}")
    
    # Print best and worst funds per category
    print("\n--- BEST AND WORST FUNDS PER CATEGORY (OLS MODEL) ---")
    for cat, cat_group in df_scorecard.groupby('category'):
        print(f"\nCategory: {cat}")
        best_fund = cat_group.sort_values('overall_rank').iloc[0]
        worst_fund = cat_group.sort_values('overall_rank').iloc[-1]
        print(f"    * Best Fund: {best_fund['scheme_name']} (Composite Score: {best_fund['weighted_score']:.2f}, Rank: {best_fund['overall_rank']})")
        print(f"    * Worst Fund: {worst_fund['scheme_name']} (Composite Score: {worst_fund['weighted_score']:.2f}, Rank: {worst_fund['overall_rank']})")
        
    # --- TASK 8: Benchmark Comparison Chart & Tracking Error ---
    print("\n[*] Running Task 8: Generating Benchmark Comparison Chart (3-Year)...")
    
    # Identify top 5 funds
    top_5_scorecard = df_scorecard.sort_values('overall_rank').head(5)
    top_5_codes = top_5_scorecard['amfi_code'].tolist()
    
    latest_global_date = df_nav['nav_date'].max()
    start_3yr = latest_global_date - pd.DateOffset(years=3)
    df_nav_3y = df_nav[(df_nav['nav_date'] >= start_3yr) & (df_nav['nav_date'] <= latest_global_date)].copy()
    
    plt.figure(figsize=(12, 7))
    
    # Plot top 5 funds and compute TE vs Nifty 100
    for code in top_5_codes:
        fund_nav = df_nav_3y[df_nav_3y['amfi_code'] == code].sort_values('nav_date').reset_index(drop=True)
        if len(fund_nav) > 0:
            initial_nav = fund_nav['nav'].iloc[0]
            fund_nav['normalized_nav'] = (fund_nav['nav'] / initial_nav) * 100
            
            # Align daily returns to compute Tracking Error vs Nifty 100
            df_merged = pd.merge(
                fund_nav[['nav_date', 'daily_return']],
                df_nifty100[['date', 'daily_return']],
                left_on='nav_date',
                right_on='date',
                suffixes=('_fund', '_bench')
            ).dropna()
            
            te_str = ""
            if len(df_merged) > 1:
                return_diff = df_merged['daily_return_fund'] - df_merged['daily_return_bench']
                te = return_diff.std(ddof=1) * np.sqrt(252)
                te_str = f" (TE: {te*100:.2f}%)"
                
            fund_row = df_funds[df_funds['amfi_code'] == code].iloc[0]
            plt.plot(fund_nav['nav_date'], fund_nav['normalized_nav'], label=f"{fund_row['scheme_name'][:30]}...{te_str}", linewidth=2)
            
    # Plot Benchmarks
    for idx_name in ['NIFTY50', 'NIFTY100']:
        df_ind = df_bench[(df_bench['index_name'] == idx_name) & 
                          (df_bench['date'] >= start_3yr) & 
                          (df_bench['date'] <= latest_global_date)].sort_values('date').reset_index(drop=True)
        if len(df_ind) > 0:
            initial_val = df_ind['close_value'].iloc[0]
            df_ind['normalized_close'] = (df_ind['close_value'] / initial_val) * 100
            plt.plot(df_ind['date'], df_ind['normalized_close'], label=f"{idx_name} (Benchmark)", linestyle='--', linewidth=2.5)
            
    plt.title("Top 5 Funds vs Benchmarks (3-Year Growth & Tracking Error vs NIFTY 100)", fontsize=14, fontweight='bold')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Normalized NAV Value (Base = 100)", fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    plt.tight_layout()
    
    chart_path = os.path.join(FIGURES_DIR, "benchmark_chart.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"    - Saved benchmark comparison chart to {chart_path}")
    
    # Copy deliverables to root directory for easy access
    import shutil
    shutil.copy(os.path.join(OUTPUT_DIR, "returns_computed.csv"), "returns_computed.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "cagr_report.csv"), "cagr_report.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "sharpe_values.csv"), "sharpe_values.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "sortino_values.csv"), "sortino_values.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "max_drawdown.csv"), "max_drawdown.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "alpha_beta.csv"), "alpha_beta.csv")
    shutil.copy(os.path.join(OUTPUT_DIR, "fund_scorecard.csv"), "fund_scorecard.csv")
    shutil.copy(os.path.join(FIGURES_DIR, "benchmark_chart.png"), "benchmark_chart.png")
    
    # Copy database to db/bluestock_mf.db to match PDF folder structure
    shutil.copy("bluestock_mf.db", "db/bluestock_mf.db")
    
    print("    - Saved deliverables to data/processed/, db/, and project root.")
    print("="*60)
    print("[+] All Day 4 OLS analytics completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
