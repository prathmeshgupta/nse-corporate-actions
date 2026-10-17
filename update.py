"""
Automated Weekly Dataset Updater for nse-corporate-actions
Can be executed locally or via GitHub Actions.
Zero credentials required.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from nse_corporate_actions.fetcher import CorporateActionFetcher

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = OUTPUT_DIR / "corporate_actions.csv"
PARQUET_FILE = OUTPUT_DIR / "corporate_actions.parquet"


def update():
    print("[1/3] Fetching latest live corporate actions from NSE API...")
    fetcher = CorporateActionFetcher()
    
    live_df = fetcher.fetch_live_corporate_actions()
    print(f"      Retrieved {len(live_df)} upcoming/recent corporate actions from NSE.")

    print("[2/3] Merging with existing historical corporate actions...")
    if CSV_FILE.exists():
        existing_df = pd.read_csv(CSV_FILE)
        combined = pd.concat([existing_df, live_df], ignore_index=True)
    else:
        combined = live_df.copy()

    if not combined.empty:
        combined = combined.dropna(subset=["symbol", "ex_date", "action_type"])
        combined = combined.drop_duplicates(subset=["symbol", "ex_date", "action_type"], keep="last")
        combined = combined.sort_values(by="ex_date", ascending=False)

        combined.to_csv(CSV_FILE, index=False)
        combined.to_parquet(PARQUET_FILE, index=False)
        print(f"      Saved {len(combined)} corporate actions to {CSV_FILE.name} and {PARQUET_FILE.name}.")

    print("[3/3] Running automated quality audit...")
    from evaluate_quality import audit_quality
    audit_quality()
    print("Update complete successfully.")


if __name__ == "__main__":
    update()
