import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

class AdjustmentCalculator:
    """Calculates backward cumulative price adjustment factors from splits and bonuses."""

    def __init__(self, actions_df: pd.DataFrame):
        self.actions = actions_df.copy()
        if not self.actions.empty:
            self.actions["ex_date"] = pd.to_datetime(self.actions["ex_date"]).dt.strftime("%Y-%m-%d")

    def compute_factors(self, symbol: str, price_dates: pd.Series) -> pd.DataFrame:
        df = pd.DataFrame({"trade_date": price_dates}).sort_values("trade_date")
        df["trade_date_str"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        df["split_adj_factor"] = 1.0

        sym_actions = self.actions[self.actions["symbol"] == symbol]
        for _, act in sym_actions.iterrows():
            ratio = act["split_ratio"]
            ex_dt = act["ex_date"]
            if ratio > 0 and ratio != 1.0:
                mask = df["trade_date_str"] < ex_dt
                df.loc[mask, "split_adj_factor"] *= (1.0 / ratio)

        df["symbol"] = symbol
        return df[["symbol", "trade_date", "split_adj_factor"]]
