import os
import sys
import subprocess
import time

def run_script(script_path, args=None):
    """Runs a python script as a subprocess, inherits standard input/output, and checks exit code."""
    print("\n" + "="*80)
    print(f"RUNNING STEP: {script_path}")
    print("="*80)
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
        
    start_time = time.time()
    
    # Run process and wait
    result = subprocess.run(cmd)
    
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n[+] SUCCESS: {script_path} completed successfully in {elapsed:.2f} seconds.")
        print("="*80)
        return True
    else:
        print(f"\n[-] FAILURE: {script_path} failed with exit code {result.returncode} after {elapsed:.2f} seconds.")
        print("="*80)
        return False

def main():
    print("="*80)
    print("BLUESTOCK FINTECH MUTUAL FUND ANALYTICS PIPELINE ORCHESTRATOR")
    print("="*80)
    
    pipeline_steps = [
        "scripts/data_ingestion.py",
        "scripts/data_cleaning.py",
        "scripts/db_loader.py",
        "scripts/compute_metrics.py",
        "scripts/advanced_analytics.py",
        "scripts/generate_delivery_files.py"
    ]
    
    total_start = time.time()
    
    for step in pipeline_steps:
        # Check if file exists
        if not os.path.exists(step):
            # Try matching inside scripts folder
            if not step.startswith("scripts/") and os.path.exists(os.path.join("scripts", step)):
                step = os.path.join("scripts", step)
            else:
                print(f"[-] ERROR: Pipeline step file not found: {step}")
                sys.exit(1)
                
        success = run_script(step)
        if not success:
            print("\n[-] PIPELINE ABORTED: One of the pipeline steps encountered an error.")
            sys.exit(1)
            
    total_elapsed = time.time() - total_start
    print("\n" + "="*80)
    print("BLUESTOCK FINTECH PIPELINE EXECUTION COMPLETE")
    print(f"Total Pipeline Runtime: {total_elapsed:.2f} seconds")
    print("Deliverables generated:")
    print("  - SQLite Database:      db/bluestock_mf.db")
    print("  - Advanced CSV Reports: data/processed/ (cagr_report.csv, var_cvar_report.csv, etc.)")
    print("  - Visual Figures:       reports/figures/ (rolling_sharpe_chart.png, sector_hhi_chart.png)")
    print("  - PPTX Slide Deck:      reports/Presentation.pptx")
    print("  - PDF Document Report:  reports/Final_Report.pdf")
    print("="*80)

if __name__ == "__main__":
    main()
