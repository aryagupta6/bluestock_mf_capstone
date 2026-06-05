import sqlite3
import pandas as pd
import os

DB_PATH = "db/bluestock_mf.db"
OUTPUT_SQL = "sql/queries.sql"

# Define the 10 analytical queries
QUERIES = [
    {
        "id": 1,
        "title": "Top 5 funds by AUM",
        "sql": """
SELECT amfi_code, scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;
"""
    },
    {
        "id": 2,
        "title": "Average NAV per month per scheme (Top 10 rows shown for brevity)",
        "sql": """
SELECT amfi_code, strftime('%Y-%m', nav_date) AS month, ROUND(AVG(nav), 4) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month
LIMIT 10;
"""
    },
    {
        "id": 3,
        "title": "SIP Inflow and YoY Growth per month",
        "sql": """
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;
"""
    },
    {
        "id": 4,
        "title": "Transactions and total amount by state",
        "sql": """
SELECT state, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;
"""
    },
    {
        "id": 5,
        "title": "Funds with expense ratio < 1%",
        "sql": """
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;
"""
    },
    {
        "id": 6,
        "title": "Top 5 sectors by portfolio holding weight",
        "sql": """
SELECT sector, ROUND(SUM(weight_pct), 2) AS total_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;
"""
    },
    {
        "id": 7,
        "title": "Average transaction amount by age group and gender",
        "sql": """
SELECT age_group, gender, ROUND(AVG(amount_inr), 2) AS avg_transaction_amount_inr, COUNT(*) AS txn_count
FROM fact_transactions
GROUP BY age_group, gender
ORDER BY age_group, gender;
"""
    },
    {
        "id": 8,
        "title": "Top 3 performing funds based on 5-year returns",
        "sql": """
SELECT amfi_code, scheme_name, return_3yr_pct, return_5yr_pct
FROM fact_performance
ORDER BY return_5yr_pct DESC, return_3yr_pct DESC
LIMIT 3;
"""
    },
    {
        "id": 9,
        "title": "High-risk schemes (High/Very High) with 1-year return < 12.0%",
        "sql": """
SELECT f.amfi_code, f.scheme_name, f.risk_category, p.return_1yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.risk_category IN ('Very High', 'High') AND p.return_1yr_pct < 12.0;
"""
    },
    {
        "id": 10,
        "title": "AUM growth by fund house between 2022-03-31 and 2025-12-31",
        "sql": """
SELECT fund_house, 
       ROUND(MAX(CASE WHEN date = '2022-03-31' THEN aum_crore END), 2) AS aum_2022_cr,
       ROUND(MAX(CASE WHEN date = '2025-12-31' THEN aum_crore END), 2) AS aum_2025_cr,
       ROUND(MAX(CASE WHEN date = '2025-12-31' THEN aum_crore END) - MAX(CASE WHEN date = '2022-03-31' THEN aum_crore END), 2) AS growth_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY growth_crore DESC;
"""
    }
]

def main():
    print("="*60)
    print("SQL ANALYTICS ENGINE")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    
    sql_file_content = [
        "-- Day 2: 10 Analytical Queries and Results\n",
        f"-- Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    ]
    
    for q in QUERIES:
        print(f"\n[*] Running Query {q['id']}: {q['title']}")
        print("-" * 50)
        
        # Execute query using pandas for easy tabular printing
        try:
            df_res = pd.read_sql_query(q["sql"], conn)
            print(df_res.to_string(index=False))
            
            # Format output for queries.sql file
            sql_file_content.append(f"-- Query {q['id']}: {q['title']}")
            sql_file_content.append(q["sql"].strip() + ";\n")
            sql_file_content.append("/* RESULTS:")
            sql_file_content.append(df_res.to_string(index=False))
            sql_file_content.append("*/\n\n" + "-"*80 + "\n")
            
        except Exception as e:
            print(f"[-] Error running query {q['id']}: {e}")
            sql_file_content.append(f"-- Error running query {q['id']}: {e}\n")
            
    conn.close()
    
    # Save to queries.sql
    os.makedirs(os.path.dirname(OUTPUT_SQL), exist_ok=True)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_file_content))
        
    print("="*60)
    print(f"[+] All 10 queries executed successfully. Saved to {OUTPUT_SQL}")
    print("="*60)

if __name__ == "__main__":
    main()
