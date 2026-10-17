import argparse
import pandas as pd
from pathlib import Path
from nse_corporate_actions.fetcher import CorporateActionFetcher
from nse_corporate_actions.calculator import AdjustmentCalculator

def main():
    parser = argparse.ArgumentParser(description="NSE Corporate Actions & Adjustment Factor Agent")
    parser.add_argument("--symbol", help="Query corporate actions for symbol")
    parser.add_argument("--sync", action="store_true", help="Sync latest live actions from NSE")
    args = parser.parse_args()

    actions_path = Path(__file__).parent / "output" / "corporate_actions.csv"
    if not actions_path.exists():
        print("Output file not found. Run sync first.")
        return

    df = pd.read_csv(actions_path)
    if args.symbol:
        sym_df = df[df["symbol"] == args.symbol.upper()]
        print(f"\n--- Corporate Actions for {args.symbol} (Count: {len(sym_df)}) ---")
        print(sym_df[["ex_date", "action_type", "purpose", "split_ratio", "dividend_amount"]].to_string())
    elif args.sync:
        fetcher = CorporateActionFetcher()
        live = fetcher.fetch_live_corporate_actions()
        print(f"Retrieved {len(live)} live corporate actions from NSE API.")
    else:
        print(f"Loaded {len(df)} corporate actions. Use --symbol <TICKER> or --sync.")

if __name__ == "__main__":
    main()
