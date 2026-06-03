import os
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "bluestock_mf.db"
PROCESSED_DIR = "data/processed"
SCHEMA_SQL = "sql/schema.sql"

def main():
    print("="*60)
    print("DATABASE LOADING ENGINE")
    print("="*60)
    
    # 1. Initialize SQLite Database Engine
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # 2. Run DDL commands from schema.sql
    print("[*] Running SQL schema DDL...")
    if not os.path.exists(SCHEMA_SQL):
        print(f"[-] Schema file not found: {SCHEMA_SQL}")
        return
        
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        ddl = f.read()
        
    with engine.connect() as conn:
        conn.connection.executescript(ddl)
    print("[+] Database tables initialized successfully.")
    
    # 3. Load tables
    
    # 3.1 Load dim_fund (Fund Master)
    print("[*] Loading dim_fund...")
    df_fund = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"))
    df_fund.to_sql("dim_fund", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_fund)} rows")
    
    # 3.2 Load fact_nav (with daily_return calculation)
    print("[*] Loading fact_nav...")
    df_nav = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"))
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    
    # Sort to compute pct_change correctly
    df_nav = df_nav.sort_values(by=["amfi_code", "date"])
    
    # Compute daily return grouped by fund code
    print("    - Computing daily returns...")
    df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()
    
    # Format date and rename columns for SQL table schema
    df_nav["nav_date"] = df_nav["date"].dt.strftime("%Y-%m-%d")
    df_nav_final = df_nav[["amfi_code", "nav_date", "nav", "daily_return"]]
    
    df_nav_final.to_sql("fact_nav", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_nav_final)} rows")
    
    # 3.3 Load fact_transactions
    print("[*] Loading fact_transactions...")
    df_tx = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"))
    # In SQLite, transaction_id is AUTOINCREMENT, so we don't load it
    df_tx.to_sql("fact_transactions", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_tx)} rows")
    
    # 3.4 Load fact_performance
    print("[*] Loading fact_performance...")
    df_perf = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_performance.csv"))
    df_perf.to_sql("fact_performance", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_perf)} rows")
    
    # 3.5 Load fact_portfolio_holdings
    print("[*] Loading fact_portfolio_holdings...")
    df_hold = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_portfolio_holdings.csv"))
    df_hold.to_sql("fact_portfolio_holdings", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_hold)} rows")
    
    # 3.6 Load fact_aum
    print("[*] Loading fact_aum...")
    df_aum = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_aum_by_fund_house.csv"))
    df_aum.to_sql("fact_aum", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_aum)} rows")
    
    # 3.7 Load fact_sip_inflows
    print("[*] Loading fact_sip_inflows...")
    df_sip = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_monthly_sip_inflows.csv"))
    df_sip.to_sql("fact_sip_inflows", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_sip)} rows")
    
    # 3.8 Load fact_category_inflows
    print("[*] Loading fact_category_inflows...")
    df_catin = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_category_inflows.csv"))
    df_catin.to_sql("fact_category_inflows", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_catin)} rows")
    
    # 3.9 Load fact_industry_folios
    print("[*] Loading fact_industry_folios...")
    df_folios = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_industry_folio_count.csv"))
    df_folios.to_sql("fact_industry_folios", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_folios)} rows")
    
    # 3.10 Load fact_benchmark
    print("[*] Loading fact_benchmark...")
    df_bench = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"))
    df_bench.to_sql("fact_benchmark", con=engine, if_exists="append", index=False)
    print(f"    - Loaded {len(df_bench)} rows")
    
    print("="*60)
    print(f"[+] All data loaded successfully into {DB_PATH}!")
    print("="*60)

if __name__ == "__main__":
    main()
