# NSE Corporate Actions & Capital Adjustment Factors

Automated corporate actions engine that parses official exchange notices (stock splits, bonuses, rights issues, demergers, and cash dividends) and computes backward cumulative price adjustment factors (`split_adj_factor` and `tri_adj_factor`) for Indian equities.

Companion repository to [`prathmeshgupta/nifty-pit-universe`](https://github.com/prathmeshgupta/nifty-pit-universe).

---

## 📊 Summary of Datasets

All processed datasets are saved in [`output/`](output/):

| Dataset | Records | Action Types | Formats |
| :--- | :---: | :--- | :--- |
| **Corporate Actions** | **40+** | Splits, Bonuses, Dividends, Demergers | [`corporate_actions.parquet`](output/corporate_actions.parquet), [`corporate_actions.csv`](output/corporate_actions.csv) |

---

## 💡 Why This Exists: The Adjustment Distortion Trap

Using naive, pre-adjusted price histories from brokers or Yahoo Finance causes critical simulation distortions:
1. **Capital Distortions**: If a stock underwent a 10:1 split, back-adjusted prices make historical trade sizes look like fractional pennies, distorting lot-size allocations and cash constraints.
2. **Limit Order Distortion**: Historical high/low levels and round-number limit levels are shifted.
3. **Dividend Yield Erasure**: Simple price backtests omit cash dividends, which compound to $1.5\%\text{--}3.0\%$ per annum in Indian markets (especially in dividend-yield or high-ROC factor models).
4. **Demerger Phantom Drops**: When a company spins off a subsidiary (e.g. Reliance spinning off Jio Financial Services `JIOFIN`), the parent stock drops on the ex-date. Naive systems treat this as an unhedged catastrophic loss unless the spun-off asset allocation is recorded.

This engine cleanly decouples **raw nominal trade prices** from **point-in-time adjustment multipliers**.

---

## 🧱 Data Schema

### `corporate_actions`
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `symbol` | String | Exchange ticker | `RELIANCE` |
| `isin` | String | Permanent security identifier | `INE002A01018` |
| `ex_date` | Date | Date when stock traded ex-action | `2024-10-28` |
| `action_type` | String | `SPLIT`, `BONUS`, `DIVIDEND`, `DEMERGER`, `RIGHTS` | `BONUS` |
| `purpose` | String | Original corporate action disclosure | `Bonus 1:1` |
| `split_ratio` | Float | Multiplier for shares (e.g. `2.0` for 1:1 bonus) | `2.0` |
| `dividend_amount` | Float | Cash dividend payout per share (INR) | `0.0` |
| `is_demerger` | Integer | `1` if corporate spin-off / demerger, else `0` | `0` |

---

## 🔍 How to Query

### 1. Using Python & Pandas
```python
import pandas as pd

df = pd.read_parquet("output/corporate_actions.parquet")

# Inspect all historical splits and bonuses for a ticker
splits = df[df["action_type"].isin(["SPLIT", "BONUS"])]
print(splits[["symbol", "ex_date", "action_type", "split_ratio", "purpose"]])
```

### 2. Using the CLI Helper
```bash
python runner.py --symbol RELIANCE
```

---

## 🧪 Quality Audit
```bash
python evaluate_quality.py
```
* **Identifier Completeness**: 0 null symbols, 0 null ex-dates ([PASS]).
* **Ratio Normalization**: All splits and bonuses parsed with positive multipliers ([PASS]).

---

## 📄 License
MIT License. Copyright (c) 2026 Prathmesh Gupta.
