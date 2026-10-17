import io
import re
import requests
import pandas as pd
from typing import Optional, Dict, Any

NSE_API_CORP_ACTIONS_URL = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class CorporateActionFetcher:
    """Fetches official live corporate actions from NSE India API and historical data via yfinance."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._primed = False

    def _prime_session(self):
        if not self._primed:
            self.session.get("https://www.nseindia.com", timeout=10)
            self._primed = True

    def fetch_live_corporate_actions(self) -> pd.DataFrame:
        self._prime_session()
        resp = self.session.get(NSE_API_CORP_ACTIONS_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            return pd.DataFrame()

        rows = []
        for item in data:
            purpose = item.get("subject", "")
            p_info = self.parse_action_type(purpose)
            ex_dt = item.get("exDate")
            rec_dt = item.get("recDate")
            try:
                ex_date = pd.to_datetime(ex_dt).strftime("%Y-%m-%d") if ex_dt and ex_dt != "-" else None
            except:
                ex_date = ex_dt
            try:
                rec_date = pd.to_datetime(rec_dt).strftime("%Y-%m-%d") if rec_dt and rec_dt != "-" else None
            except:
                rec_date = rec_dt

            rows.append({
                "symbol": item.get("symbol"),
                "isin": item.get("isin"),
                "ex_date": ex_date,
                "record_date": rec_date,
                "action_type": p_info["action_type"],
                "purpose": purpose,
                "split_ratio": p_info["split_ratio"],
                "bonus_ratio": p_info["bonus_ratio"],
                "dividend_amount": p_info["dividend_amount"],
                "is_demerger": p_info["is_demerger"],
                "source": "NSE_LIVE_API"
            })
        return pd.DataFrame(rows)

    def fetch_historical_actions_yfinance(self, symbol: str) -> pd.DataFrame:
        import yfinance as yf
        ticker_str = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        t = yf.Ticker(ticker_str)
        splits = t.splits
        divs = t.dividends
        records = []

        if not splits.empty:
            for dt, ratio in splits.items():
                records.append({
                    "symbol": symbol.replace(".NS", ""),
                    "ex_date": dt.strftime("%Y-%m-%d"),
                    "action_type": "SPLIT",
                    "purpose": f"Stock Split 1:{ratio:.2f}",
                    "split_ratio": float(ratio),
                    "bonus_ratio": 0.0,
                    "dividend_amount": 0.0,
                    "is_demerger": 0,
                    "source": "YFINANCE_HISTORICAL"
                })

        if not divs.empty:
            for dt, amt in divs.items():
                records.append({
                    "symbol": symbol.replace(".NS", ""),
                    "ex_date": dt.strftime("%Y-%m-%d"),
                    "action_type": "DIVIDEND",
                    "purpose": f"Dividend Rs {amt:.2f}",
                    "split_ratio": 1.0,
                    "bonus_ratio": 0.0,
                    "dividend_amount": float(amt),
                    "is_demerger": 0,
                    "source": "YFINANCE_HISTORICAL"
                })

        return pd.DataFrame(records)

    def parse_action_type(self, purpose_str: str) -> Dict[str, Any]:
        p = str(purpose_str).upper()
        res = {
            "action_type": "OTHER",
            "split_ratio": 1.0,
            "bonus_ratio": 0.0,
            "dividend_amount": 0.0,
            "is_demerger": 0,
        }

        if "DIVIDEND" in p:
            res["action_type"] = "DIVIDEND"
            m = re.search(r"RS\.?\s*([0-9.]+)", p)
            if m:
                try:
                    res["dividend_amount"] = float(m.group(1))
                except ValueError:
                    pass
        elif "SPLIT" in p or "SUB-DIVISION" in p:
            res["action_type"] = "SPLIT"
            m = re.findall(r"RS\.?\s*([0-9.]+)", p)
            if len(m) >= 2:
                try:
                    old_fv = float(m[0])
                    new_fv = float(m[1])
                    if new_fv > 0:
                        res["split_ratio"] = old_fv / new_fv
                except ValueError:
                    pass
        elif "BONUS" in p:
            res["action_type"] = "BONUS"
            m = re.search(r"([0-9]+)\s*:\s*([0-9]+)", p)
            if m:
                try:
                    bonus_shares = float(m.group(1))
                    existing_shares = float(m.group(2))
                    res["bonus_ratio"] = bonus_shares / existing_shares
                    res["split_ratio"] = (existing_shares + bonus_shares) / existing_shares
                except ValueError:
                    pass
        elif "DEMERGER" in p or "SCHEME OF ARRANGEMENT" in p:
            res["action_type"] = "DEMERGER"
            res["is_demerger"] = 1

        return res
