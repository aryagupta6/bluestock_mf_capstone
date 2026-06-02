import os
import requests
import pandas as pd
from datetime import datetime

# List of mutual fund schemes to fetch
SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip"
}

import time

def fetch_and_save_nav(scheme_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    max_retries = 3
    timeout_seconds = 30
    
    for attempt in range(1, max_retries + 1):
        print(f"Fetching NAV data for {scheme_name} (Code: {scheme_code}) from {url}... (Attempt {attempt}/{max_retries})")
        try:
            # Request with timeout
            response = requests.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            
            json_data = response.json()
            
            if "data" not in json_data or not json_data["data"]:
                print(f"[-] No data found in the response for scheme: {scheme_code}")
                return False
            
            # Parse records
            records = []
            for item in json_data["data"]:
                raw_date = item.get("date")
                nav_value = item.get("nav")
                
                # Convert date from DD-MM-YYYY to YYYY-MM-DD
                try:
                    formatted_date = datetime.strptime(raw_date, "%d-%m-%Y").strftime("%Y-%m-%d")
                except Exception as e:
                    formatted_date = raw_date  # fallback
                    
                records.append({
                    "amfi_code": int(scheme_code),
                    "date": formatted_date,
                    "nav": float(nav_value) if nav_value else None
                })
                
            # Create DataFrame
            df = pd.DataFrame(records)
            
            # Ensure directory exists
            os.makedirs("data/raw", exist_ok=True)
            
            # Save as raw CSV
            output_file = f"data/raw/nav_{scheme_code}.csv"
            df.to_csv(output_file, index=False)
            print(f"[+] Successfully saved {len(df)} records to {output_file}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"[-] Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                sleep_time = attempt * 5
                print(f"[*] Sleeping for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                print(f"[-] All attempts failed to fetch scheme {scheme_code}")
                return False
        except ValueError as e:
            print(f"[-] JSON/Parsing error for scheme {scheme_code}: {e}")
            return False
        except Exception as e:
            print(f"[-] Unexpected error for scheme {scheme_code}: {e}")
            return False

def main():
    print("="*60)
    print("Mutual Fund Live & Historical NAV Fetcher")
    print("="*60)
    
    success_count = 0
    for code, name in SCHEMES.items():
        if fetch_and_save_nav(code, name):
            success_count += 1
        print("-" * 60)
        
    print(f"Fetching complete. Success: {success_count}/{len(SCHEMES)}")
    print("="*60)

if __name__ == "__main__":
    main()
