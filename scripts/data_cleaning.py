import os
import pandas as pd
import numpy as np

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_fund_master():
    print("[*] Cleaning Fund Master...")
    df = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    # Drop duplicates
    df = df.drop_duplicates(subset=["amfi_code"])
    # Parse dates
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    # Save
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_nav_history():
    print("[*] Cleaning NAV History...")
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    
    # Combine with fetched live NAV files
    import glob
    fetched_files = glob.glob(os.path.join(RAW_DIR, "nav_*.csv"))
    if fetched_files:
        print(f"    - Found {len(fetched_files)} fetched live NAV file(s). Combining with history...")
        dfs = [df]
        for f in fetched_files:
            try:
                temp_df = pd.read_csv(f)
                dfs.append(temp_df)
            except Exception as e:
                print(f"      [!] Error loading {f}: {e}")
        df = pd.concat(dfs, ignore_index=True)
    
    # 1. Parse dates and check types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # 2. Sort by amfi_code and date
    df = df.sort_values(by=["amfi_code", "date"])
    
    # 3. Drop duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    
    # 4. Validate NAV > 0
    df = df[df["nav"] > 0]
    
    # 5. Forward fill missing NAV values within each amfi_code group
    df["nav"] = df.groupby("amfi_code")["nav"].ffill()
    
    # Format date back to string YYYY-MM-DD
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # Save
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_aum_by_fund_house():
    print("[*] Cleaning AUM by Fund House...")
    df = pd.read_csv(os.path.join(RAW_DIR, "03_aum_by_fund_house.csv"))
    df = df.drop_duplicates()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["aum_crore"] > 0]
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_aum_by_fund_house.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_monthly_sip_inflows():
    print("[*] Cleaning Monthly SIP Inflows...")
    df = pd.read_csv(os.path.join(RAW_DIR, "04_monthly_sip_inflows.csv"))
    df = df.drop_duplicates(subset=["month"])
    
    # yoy_growth_pct has nulls for the first 12 months. Ensure it's typed properly.
    df["yoy_growth_pct"] = pd.to_numeric(df["yoy_growth_pct"], errors="coerce")
    
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_monthly_sip_inflows.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_category_inflows():
    print("[*] Cleaning Category Inflows...")
    df = pd.read_csv(os.path.join(RAW_DIR, "05_category_inflows.csv"))
    df = df.drop_duplicates()
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_category_inflows.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_industry_folio_count():
    print("[*] Cleaning Industry Folio Count...")
    df = pd.read_csv(os.path.join(RAW_DIR, "06_industry_folio_count.csv"))
    df = df.drop_duplicates()
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_industry_folio_count.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_scheme_performance():
    print("[*] Cleaning Scheme Performance...")
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))
    df = df.drop_duplicates(subset=["amfi_code"])
    
    # 1. Validate returns are numeric
    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # 2. Flag negative Sharpe ratios
    df["is_negative_sharpe"] = df["sharpe_ratio"] < 0
    
    # 3. Check expense ratio (0.1% to 2.5%)
    # Let's inspect values out of range
    out_of_range = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    if not out_of_range.empty:
        print(f"    [!] Warning: Expense ratios out of normal bounds (0.1% - 2.5%) detected:\n{out_of_range[['amfi_code', 'expense_ratio_pct']]}")
        
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_performance.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_investor_transactions():
    print("[*] Cleaning Investor Transactions...")
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    df = df.drop_duplicates()
    
    # 1. Standardise transaction_type
    tx_map = {
        "sip": "SIP",
        "lumpsum": "Lumpsum",
        "redemption": "Redemption"
    }
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.lower().map(tx_map).fillna(df["transaction_type"])
    
    # 2. Validate amount_inr > 0
    invalid_amt = (df["amount_inr"] <= 0).sum()
    if invalid_amt > 0:
        print(f"    [!] Dropping {invalid_amt} rows with invalid transaction amount <= 0")
        df = df[df["amount_inr"] > 0]
        
    # 3. Check KYC status
    # Standard values should be Verified/Pending. Let's strip and title-case them.
    df["kyc_status"] = df["kyc_status"].astype(str).str.strip().str.title()
    
    # 4. Fix date formats
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_portfolio_holdings():
    print("[*] Cleaning Portfolio Holdings...")
    df = pd.read_csv(os.path.join(RAW_DIR, "09_portfolio_holdings.csv"))
    df = df.drop_duplicates()
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_portfolio_holdings.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def clean_benchmark_indices():
    print("[*] Cleaning Benchmark Indices...")
    df = pd.read_csv(os.path.join(RAW_DIR, "10_benchmark_indices.csv"))
    df = df.drop_duplicates()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"), index=False)
    print(f"    - Cleaned shape: {df.shape}")

def main():
    print("="*60)
    print("DATA CLEANING PIPELINE")
    print("="*60)
    
    clean_fund_master()
    clean_nav_history()
    clean_aum_by_fund_house()
    clean_monthly_sip_inflows()
    clean_category_inflows()
    clean_industry_folio_count()
    clean_scheme_performance()
    clean_investor_transactions()
    clean_portfolio_holdings()
    clean_benchmark_indices()
    
    print("="*60)
    print("[+] All 10 datasets successfully cleaned and saved to data/processed/")
    print("="*60)

if __name__ == "__main__":
    main()
