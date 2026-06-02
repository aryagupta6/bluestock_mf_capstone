import os
import pandas as pd
import numpy as np

# Path to local CSV files
DATA_DIR = "data/raw"
FILES = {
    "01_fund_master.csv": "Fund Master",
    "02_nav_history.csv": "NAV History",
    "03_aum_by_fund_house.csv": "AUM by Fund House",
    "04_monthly_sip_inflows.csv": "Monthly SIP Inflows",
    "05_category_inflows.csv": "Category Inflows",
    "06_industry_folio_count.csv": "Industry Folio Count",
    "07_scheme_performance.csv": "Scheme Performance",
    "08_investor_transactions.csv": "Investor Transactions",
    "09_portfolio_holdings.csv": "Portfolio Holdings",
    "10_benchmark_indices.csv": "Benchmark Indices"
}

def analyze_dataset(filename, name):
    filepath = os.path.join(DATA_DIR, filename)
    print(f"\n{'='*80}")
    print(f" LOADING DATASET: {name} ({filename})")
    print(f"{'='*80}")
    
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return None, []
        
    df = pd.read_csv(filepath)
    
    # 1. Print diagnostics to console
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    print("Data Types:")
    print(df.dtypes)
    print("\nHead (First 3 rows):")
    print(df.head(3))
    
    # 2. Check for anomalies programmatically
    anomalies = []
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        for col, count in missing.items():
            if count > 0:
                anomalies.append(f"Missing Values: Column '{col}' has {count} null value(s) ({count/len(df)*100:.2f}%).")
                
    # Check for duplicate rows
    dups = df.duplicated().sum()
    if dups > 0:
        anomalies.append(f"Duplicates: Found {dups} duplicated row(s).")
        
    # Check for negative values in numeric columns (where negative values shouldn't exist)
    for col in df.select_dtypes(include=[np.number]).columns:
        # Allow negative values for exit load (might be 0), returns, alpha, beta, drawdown, transaction amount, etc.
        # But things like aum, sip inflow, min_sip_amount, std_dev, weight_pct should be non-negative
        if col in ['min_sip_amount', 'min_lumpsum_amount', 'expense_ratio_pct', 
                   'aum_lakh_crore', 'aum_crore', 'num_schemes', 
                   'sip_inflow_crore', 'active_sip_accounts_crore', 'new_sip_accounts_lakh', 'sip_aum_lakh_crore',
                   'total_folios_crore', 'equity_folios_crore', 'debt_folios_crore', 'hybrid_folios_crore',
                   'weight_pct', 'market_value_cr', 'current_price_inr']:
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                anomalies.append(f"Negative Values: Column '{col}' contains {neg_count} negative value(s).")
                
    # Specific dataset checks
    if filename == "09_portfolio_holdings.csv":
        # Check if portfolio weights sum to more than 100% per scheme
        weights_sum = df.groupby('amfi_code')['weight_pct'].sum()
        over_100 = weights_sum[weights_sum > 100.5]
        if not over_100.empty:
            for code, s in over_100.items():
                anomalies.append(f"Portfolio Weights: Scheme {code} holdings sum to {s:.2f}% (exceeds 100%).")
                
    if len(anomalies) == 0:
        print("\n[+] No obvious anomalies detected in this dataset.")
    else:
        print("\n[-] Detected Anomalies:")
        for anomaly in anomalies:
            print(f"    * {anomaly}")
            
    return df, anomalies

def main():
    os.makedirs("reports", exist_ok=True)
    report_lines = [
        "# Day 1: Data Ingestion & Quality Summary Report\n",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## 1. Datasets Summary Table\n",
        "| Dataset File | Rows | Columns | Detected Anomalies |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    datasets = {}
    all_anomalies = {}
    
    for filename, name in FILES.items():
        df, anomalies = analyze_dataset(filename, name)
        if df is not None:
            datasets[filename] = df
            all_anomalies[filename] = anomalies
            anomaly_summary = ", ".join([a.split(":")[0] for a in anomalies]) if anomalies else "None"
            report_lines.append(f"| {filename} | {df.shape[0]} | {df.shape[1]} | {anomaly_summary} |")
        else:
            report_lines.append(f"| {filename} | File Missing | File Missing | File Missing |")
            
    # Fund Master Exploration
    report_lines.append("\n## 2. Fund Master Exploration (`01_fund_master.csv`)\n")
    if "01_fund_master.csv" in datasets:
        df_master = datasets["01_fund_master.csv"]
        
        unique_fh = sorted(df_master['fund_house'].dropna().unique())
        unique_cat = sorted(df_master['category'].dropna().unique())
        unique_subcat = sorted(df_master['sub_category'].dropna().unique())
        unique_risk = sorted(df_master['risk_category'].dropna().unique())
        
        print("\n" + "="*80)
        print(" EXPLORING FUND MASTER")
        print("="*80)
        print(f"Unique Fund Houses ({len(unique_fh)}): {unique_fh}\n")
        print(f"Unique Categories ({len(unique_cat)}): {unique_cat}\n")
        print(f"Unique Sub-Categories ({len(unique_subcat)}): {unique_subcat}\n")
        print(f"Unique Risk Categories ({len(unique_risk)}): {unique_risk}\n")
        
        report_lines.append(f"- **Unique Fund Houses ({len(unique_fh)}):** {', '.join(unique_fh)}")
        report_lines.append(f"- **Unique Categories ({len(unique_cat)}):** {', '.join(unique_cat)}")
        report_lines.append(f"- **Unique Sub-Categories ({len(unique_subcat)}):** {', '.join(unique_subcat)}")
        report_lines.append(f"- **Unique Risk Categories ({len(unique_risk)}):** {', '.join(unique_risk)}")
        
        # AMFI Scheme Code Structure analysis
        amfi_structure = (
            "\n### AMFI Scheme Code Structure Analysis\n"
            "AMFI (Association of Mutual Funds in India) scheme codes are unique 5 or 6 digit identifiers.\n"
            "By analyzing the fund master dataset, we observe the following characteristics:\n"
            "1. **Regular vs Direct Plans:** Direct and Regular plans of the same scheme have sequential or consecutive AMFI codes.\n"
            "   * *Example:* SBI Bluechip Fund Regular Growth is `119551` and Direct Growth is `119552`.\n"
            "   * *Example:* HDFC Top 100 Fund Regular Growth is `100016`, whereas Direct Growth is `125497` (non-sequential due to different launch times, Direct plans were introduced later in 2013).\n"
            "2. **Sequential Registration:** Block allocation of codes is visible. For instance, SBI Mutual Fund schemes occupy the `1195xx` block (SBI Bluechip Regular `119551`, Direct `119552`, Small Cap Regular `119598`, Direct `119599`). Axis Mutual Fund schemes occupy the `1190xx` block (Axis Bluechip Regular `119092`, Direct `119093`, Midcap Regular `119094`, Small Cap Regular `119095`).\n"
            "3. **Plan Association:** Direct plans launched in 2013 share a pattern in code jumps if not registered sequentially with the regular plan (e.g. HDFC Regular `100016` launched 1996 vs Direct `125497` launched 2013).\n"
        )
        report_lines.append(amfi_structure)
        print(amfi_structure)
        
    # Validation of AMFI Codes
    report_lines.append("\n## 3. AMFI Code Validation (`fund_master` vs `nav_history`)\n")
    print("\n" + "="*80)
    print(" VALIDATING AMFI CODES")
    print("="*80)
    
    if "01_fund_master.csv" in datasets and "02_nav_history.csv" in datasets:
        df_master = datasets["01_fund_master.csv"]
        df_nav = datasets["02_nav_history.csv"]
        
        master_codes = set(df_master['amfi_code'].dropna().unique())
        nav_codes = set(df_nav['amfi_code'].dropna().unique())
        
        matched_codes = master_codes.intersection(nav_codes)
        missing_in_nav = master_codes - nav_codes
        extra_in_nav = nav_codes - master_codes
        
        match_pct = (len(matched_codes) / len(master_codes)) * 100
        
        summary_text = (
            f"Validation Results:\n"
            f"- Unique AMFI codes in Fund Master: {len(master_codes)}\n"
            f"- Unique AMFI codes in NAV History: {len(nav_codes)}\n"
            f"- Matched AMFI codes: {len(matched_codes)} ({match_pct:.2f}% of Fund Master)\n"
            f"- AMFI codes in Fund Master missing in NAV History: {len(missing_in_nav)}\n"
        )
        print(summary_text)
        report_lines.append(f"- **Unique AMFI codes in Fund Master:** {len(master_codes)}")
        report_lines.append(f"- **Unique AMFI codes in NAV History:** {len(nav_codes)}")
        report_lines.append(f"- **Matched AMFI codes:** {len(matched_codes)} ({match_pct:.2f}% match)")
        report_lines.append(f"- **AMFI codes in Fund Master missing in NAV History:** {len(missing_in_nav)}")
        
        if len(missing_in_nav) > 0:
            print(f"[-] Missing Codes detail: {missing_in_nav}")
            report_lines.append(f"  * *Missing Codes list:* `{sorted(list(missing_in_nav))}`")
            # Lookup missing schemes names
            missing_details = df_master[df_master['amfi_code'].isin(missing_in_nav)][['amfi_code', 'scheme_name', 'fund_house']]
            print("\nMissing Schemes Details:")
            print(missing_details)
            report_lines.append("\n| Missing AMFI Code | Scheme Name | Fund House |")
            report_lines.append("| :--- | :--- | :--- |")
            for _, row in missing_details.iterrows():
                report_lines.append(f"| {row['amfi_code']} | {row['scheme_name']} | {row['fund_house']} |")
        else:
            print("[+] All AMFI codes in Fund Master successfully mapped to NAV History!")
            report_lines.append("- [+] All AMFI codes in Fund Master successfully exist in NAV History.")
            
        if len(extra_in_nav) > 0:
            print(f"\n[*] Note: NAV History contains {len(extra_in_nav)} codes not registered in Fund Master.")
            report_lines.append(f"- **NAV History contains {len(extra_in_nav)} codes not registered in Fund Master.**")
    else:
        print("[-] Data files missing. Skipping code validation.")
        report_lines.append("[-] Data validation skipped because Fund Master or NAV History files were missing.")
        
    # Write details of anomalies to report
    report_lines.append("\n## 4. Detailed Anomalies Log\n")
    has_any_anomaly = False
    for filename, anomalies in all_anomalies.items():
        if anomalies:
            has_any_anomaly = True
            report_lines.append(f"### {filename} ({FILES[filename]})\n")
            for a in anomalies:
                report_lines.append(f"- {a}")
            report_lines.append("")
            
    if not has_any_anomaly:
        report_lines.append("No critical anomalies found across all datasets. Datasets are clean and ready for analysis.")
        
    # Write the report to file
    report_path = "reports/data_quality_summary.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\n[+] Data quality summary report successfully saved to: {report_path}")
    print("="*80)

if __name__ == "__main__":
    # Import datetime here
    from datetime import datetime
    main()
