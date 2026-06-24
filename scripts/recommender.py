import os
import sqlite3
import argparse
import pandas as pd

DB_PATH = "db/bluestock_mf.db"

def load_connection():
    if not os.path.exists(DB_PATH):
        if os.path.exists("bluestock_mf.db"):
            os.makedirs("db", exist_ok=True)
            import shutil
            shutil.copy("bluestock_mf.db", DB_PATH)
        else:
            raise FileNotFoundError(f"Database not found at {DB_PATH}.")
    return sqlite3.connect(DB_PATH)

def recommend_funds(risk_appetite, category=None):
    """
    Recommends the top 3 mutual funds sorted by Sharpe ratio matching the appropriate risk and category.
    """
    conn = load_connection()
    
    # 1. Map user risk appetite to database risk categories
    # Database categories in dim_fund/fact_performance typically:
    # Low, Low to Moderate, Moderate, Moderately High, High, Very High
    risk_appetite = risk_appetite.strip().lower()
    
    if risk_appetite == "low":
        risk_filter = "('Low', 'Low to Moderate')"
    elif risk_appetite == "moderate":
        risk_filter = "('Moderate', 'Moderately High')"
    elif risk_appetite == "high":
        risk_filter = "('High', 'Very High')"
    else:
        # Fallback to wildcard/all if not recognized
        risk_filter = None

    # 2. Build the query
    query = """
    SELECT f.amfi_code, f.scheme_name, f.category, f.sub_category, f.risk_category, p.sharpe_ratio, p.return_3yr_pct, p.expense_ratio_pct
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    WHERE p.sharpe_ratio IS NOT NULL
    """
    
    params = []
    
    if risk_filter:
        query += f" AND f.risk_category IN {risk_filter}"
        
    if category:
        query += " AND f.category LIKE ?"
        params.append(f"%{category}%")
        
    query += " ORDER BY p.sharpe_ratio DESC LIMIT 3;"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def main():
    print("="*60)
    print("BLUESTOCK MUTUAL FUND RECOMMENDER ENGINE")
    print("="*60)
    
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender CLI")
    parser.add_argument("--risk", type=str, help="Risk Appetite: Low, Moderate, High")
    parser.add_argument("--category", type=str, help="Category: Equity, Debt, etc.")
    args = parser.parse_args()
    
    risk = args.risk
    category = args.category
    
    # If not provided via CLI, prompt interactively
    if not risk:
        print("\nChoose your Risk Appetite:")
        print("  1. Low      (Focus on preservation of capital, e.g., Liquid/Debt funds)")
        print("  2. Moderate (Balanced risk and return, e.g., Short Term Debt / Large Cap)")
        print("  3. High     (Maximize growth potential, e.g., Mid Cap / Small Cap / Equity)")
        choice = input("Enter choice (1-3 or Low/Moderate/High): ").strip().lower()
        if choice in ['1', 'low']:
            risk = 'low'
        elif choice in ['2', 'moderate']:
            risk = 'moderate'
        elif choice in ['3', 'high']:
            risk = 'high'
        else:
            print("[!] Invalid risk selection. Defaulting to 'moderate'.")
            risk = 'moderate'
            
    if not category:
        print("\nChoose Asset Category (Optional):")
        print("  - Press Enter to search all categories")
        print("  - Type 'Equity' for stock funds")
        print("  - Type 'Debt' for bond/fixed-income funds")
        cat_input = input("Enter category: ").strip()
        category = cat_input if cat_input else None

    print("\n[*] Processing recommendations...")
    try:
        recommendations = recommend_funds(risk, category)
        if len(recommendations) == 0:
            print("[-] No funds found matching your criteria.")
        else:
            print("\n" + "="*80)
            print(f"TOP 3 RECOMMENDED FUNDS FOR RISK PROFILE: {risk.upper()} | CATEGORY: {str(category).upper() if category else 'ALL'}")
            print("="*80)
            for idx, row in recommendations.iterrows():
                print(f"Rank {idx+1}: {row['scheme_name']}")
                print(f"  - AMFI Code:      {row['amfi_code']}")
                print(f"  - Category:       {row['category']} ({row['sub_category']})")
                print(f"  - Risk Profile:   {row['risk_category']}")
                print(f"  - Sharpe Ratio:   {row['sharpe_ratio']:.4f} (Annualized)")
                print(f"  - 3-Year CAGR:    {row['return_3yr_pct']:.2f}%")
                print(f"  - Expense Ratio:  {row['expense_ratio_pct']:.2f}%")
                print("-" * 80)
    except Exception as e:
        print(f"[-] Error generating recommendations: {e}")
        
    print("="*60)

if __name__ == "__main__":
    main()
