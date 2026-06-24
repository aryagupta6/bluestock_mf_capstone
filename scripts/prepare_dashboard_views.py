import os
import sqlite3
import pandas as pd

# Path configurations
DB_PATH = "db/bluestock_mf.db"
OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("="*60)
    print("DASHBOARD DATA PREPARATION ENGINE")
    print("="*60)
    
    # Connect to the SQLite database
    if not os.path.exists(DB_PATH):
        print(f"[-] Database not found at {DB_PATH}. Please verify the path.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Load calculated metrics into database tables
    print("[*] Loading calculated metrics into database...")
    try:
        df_scorecard = pd.read_csv("fund_scorecard.csv")
        df_scorecard.to_sql("fact_performance_scorecard", con=conn, if_exists="replace", index=False)
        print("    - Loaded fact_performance_scorecard successfully.")
        
        df_ab = pd.read_csv("alpha_beta.csv")
        df_ab.to_sql("fact_performance_alpha_beta", con=conn, if_exists="replace", index=False)
        print("    - Loaded fact_performance_alpha_beta successfully.")
        
        df_sortino = pd.read_csv("sortino_values.csv")
        df_sortino.to_sql("fact_performance_sortino", con=conn, if_exists="replace", index=False)
        print("    - Loaded fact_performance_sortino successfully.")
    except Exception as e:
        print(f"    [-] Error loading metrics tables: {e}")
        
    # 2. Register SQL Views
    print("\n[*] Registering SQLite dashboard views...")
    
    # View 1: Page 1 KPIs (Industry Totals)
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page1_kpis;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page1_kpis AS
    SELECT 
        81.0 AS total_aum_lakh_crore,
        31002.0 AS monthly_sip_inflow_crore,
        26.12 AS total_folios_crore,
        1908 AS total_schemes_count;
    """)
    
    # View 2: Page 1 AUM Trend (Jan 2022 - Dec 2025)
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page1_aum_trend;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page1_aum_trend AS
    SELECT 
        date, 
        SUM(aum_crore) AS total_aum_crore,
        SUM(aum_crore) / 100000.0 AS total_aum_lakh_crore
    FROM fact_aum
    GROUP BY date
    ORDER BY date;
    """)
    
    # View 3: Page 1 Top 10 AMC AUM
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page1_amc_aum;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page1_amc_aum AS
    SELECT 
        fund_house,
        aum_crore,
        aum_lakh_crore
    FROM fact_aum
    WHERE date = '2025-12-31'
    ORDER BY aum_crore DESC;
    """)
    
    # View 4: Page 2 Fund Performance Details
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page2_performance;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page2_performance AS
    SELECT 
        s.overall_rank,
        s.amfi_code,
        s.scheme_name,
        s.category,
        s.sub_category,
        s.expense_ratio_pct,
        s.cagr_3yr,
        s.sharpe_ratio,
        so.sortino_ratio,
        s.max_drawdown_pct,
        s.weighted_score,
        ab.alpha,
        ab.beta
    FROM fact_performance_scorecard s
    LEFT JOIN fact_performance_alpha_beta ab ON s.amfi_code = ab.amfi_code
    LEFT JOIN fact_performance_sortino so ON s.amfi_code = so.amfi_code;
    """)
    
    # View 5: Page 2 NAV vs Benchmark daily growth series (computes index daily returns on the fly)
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page2_nav;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page2_nav AS
    WITH benchmark_returns AS (
        SELECT 
            date,
            index_name,
            close_value,
            (close_value - LAG(close_value) OVER (PARTITION BY index_name ORDER BY date)) / LAG(close_value) OVER (PARTITION BY index_name ORDER BY date) AS daily_return
        FROM fact_benchmark
    )
    SELECT 
        n.amfi_code,
        n.nav_date,
        n.nav,
        n.daily_return AS fund_daily_return,
        f.scheme_name,
        f.benchmark AS fund_benchmark,
        b.index_name AS benchmark_index,
        b.close_value AS benchmark_close,
        b.daily_return AS benchmark_daily_return
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
    LEFT JOIN benchmark_returns b ON n.nav_date = b.date AND b.index_name = (
        CASE f.benchmark
            WHEN 'NIFTY 100 TRI' THEN 'NIFTY100'
            WHEN 'CRISIL Short Term Bond Index' THEN 'CRISIL_GILT'
            WHEN 'NIFTY Midcap 150 TRI' THEN 'NIFTY_MIDCAP150'
            WHEN 'BSE 250 SmallCap TRI' THEN 'BSE_SMALLCAP'
            WHEN 'CRISIL Liquid Fund AI Index' THEN 'CRISIL_LIQUID'
            WHEN 'NIFTY 50 TRI' THEN 'NIFTY50'
            WHEN 'NIFTY 500 TRI' THEN 'NIFTY500'
            WHEN 'CRISIL Dynamic Gilt Index' THEN 'CRISIL_GILT'
            WHEN 'NIFTY Midcap 50 TRI' THEN 'NIFTY_MIDCAP150'
            WHEN 'NIFTY Large Midcap 250 TRI' THEN 'NIFTY500'
            ELSE 'NIFTY100'
        END
    );
    """)
    
    # View 6: Page 3 Demographic Transactions
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page3_transactions;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page3_transactions AS
    SELECT 
        transaction_id,
        investor_id,
        transaction_date,
        amfi_code,
        transaction_type,
        amount_inr,
        state,
        city,
        city_tier,
        age_group,
        gender,
        annual_income_lakh,
        payment_mode,
        kyc_status
    FROM fact_transactions;
    """)
    
    # View 7: Page 4 Market Trends (SIP vs Nifty 50)
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page4_market_trends;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page4_market_trends AS
    WITH monthly_nifty AS (
        SELECT 
            strftime('%Y-%m', date) AS month_str,
            AVG(close_value) AS avg_nifty50_close
        FROM fact_benchmark
        WHERE index_name = 'NIFTY50'
        GROUP BY month_str
    )
    SELECT 
        s.month,
        s.sip_inflow_crore,
        s.active_sip_accounts_crore,
        s.new_sip_accounts_lakh,
        s.sip_aum_lakh_crore,
        s.yoy_growth_pct AS sip_yoy_growth_pct,
        n.avg_nifty50_close
    FROM fact_sip_inflows s
    LEFT JOIN monthly_nifty n ON s.month = n.month_str
    ORDER BY s.month;
    """)
    
    # View 8: Page 4 Category Net Inflows
    cursor.execute("DROP VIEW IF EXISTS view_dashboard_page4_category_inflows;")
    cursor.execute("""
    CREATE VIEW view_dashboard_page4_category_inflows AS
    SELECT 
        month,
        category,
        net_inflow_crore
    FROM fact_category_inflows;
    """)
    
    print("[+] Registered all SQLite views.")
    
    # 3. Export Views to CSVs for Direct Power BI Import
    print("\n[*] Exporting views to CSVs for convenient Power BI import...")
    views_to_export = [
        ("view_dashboard_page1_kpis", "dashboard_page1_kpis.csv"),
        ("view_dashboard_page1_aum_trend", "dashboard_page1_aum_trend.csv"),
        ("view_dashboard_page1_amc_aum", "dashboard_page1_amc_aum.csv"),
        ("view_dashboard_page2_performance", "dashboard_page2_performance.csv"),
        ("view_dashboard_page2_nav", "dashboard_page2_nav.csv"),
        ("view_dashboard_page3_transactions", "dashboard_page3_transactions.csv"),
        ("view_dashboard_page4_market_trends", "dashboard_page4_market_trends.csv"),
        ("view_dashboard_page4_category_inflows", "dashboard_page4_category_inflows.csv")
    ]
    
    for view_name, csv_name in views_to_export:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {view_name};", conn)
            csv_path = os.path.join(OUTPUT_DIR, csv_name)
            df.to_csv(csv_path, index=False)
            print(f"    - Exported {view_name} to {csv_path} ({len(df)} rows)")
        except Exception as e:
            print(f"    [-] Error exporting {view_name}: {e}")
            
    conn.commit()
    conn.close()
    
    print("="*60)
    print("[+] Day 5 data models and views successfully prepared!")
    print("="*60)

if __name__ == "__main__":
    main()
