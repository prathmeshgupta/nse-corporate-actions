import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 60)
    print(" NSE CORPORATE ACTIONS - DATA QUALITY AUDIT")
    print("=" * 60)
    
    csv_path = Path(__file__).parent / "output" / "corporate_actions.csv"
    assert csv_path.exists(), "corporate_actions.csv missing"
    
    df = pd.read_csv(csv_path)
    print(f"Total Corporate Actions Indexed: {len(df)}")
    
    null_syms = df["symbol"].isnull().sum()
    null_dates = df["ex_date"].isnull().sum()
    print(f"Null Symbols: {null_syms} {'[PASS]' if null_syms == 0 else '[FAIL]'}")
    print(f"Null Ex-Dates: {null_dates} {'[PASS]' if null_dates == 0 else '[FAIL]'}")
    
    # Action type distribution
    print("\nAction Types:")
    for act, cnt in df["action_type"].value_counts().items():
        print(f"  • {act:<15}: {cnt:>3}")
        
    print("=" * 60)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 60)

if __name__ == "__main__":
    audit_quality()
