#!/usr/bin/env python3
"""INE SC warehouse receipts — time series fetch and simple models.

Data: akshare SHFE/INE receipt API (get_shfe_receipt_2/3 for SC)
Outputs: data/sc_warehouse_receipts.csv, data/sc_warehouse_receipts_summary.json
"""

from __future__ import annotations

import json
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import statsmodels.api as sm
from akshare.futures import cons, receipt as ak_receipt
from statsmodels.tsa.arima.model import ARIMA

from _paths import DATA_DIR

RECEIPTS_CSV = DATA_DIR / "sc_warehouse_receipts.csv"
SC_LISTING_DATE = pd.Timestamp("2018-03-26")
SHFE_RECEIPT_V3_START = date(2025, 11, 18)
TRADING_CALENDAR = cons.get_calendar()
DEFAULT_LOOKBACK_DAYS = int(os.environ.get("SC_RECEIPT_LOOKBACK_DAYS", "756"))
FETCH_WORKERS = int(os.environ.get("SC_RECEIPT_WORKERS", "8"))


def _shfe_sc_receipt(trade_date: date) -> pd.DataFrame | None:
    """Single-day SC receipt via INE/SHFE warehouse API (fast path)."""
    if trade_date.strftime("%Y%m%d") not in TRADING_CALENDAR:
        return None
    if trade_date >= SHFE_RECEIPT_V3_START:
        fn = ak_receipt.get_shfe_receipt_3
    else:
        fn = ak_receipt.get_shfe_receipt_2
    df = fn(date=trade_date.strftime("%Y%m%d"), vars_list=["SC"])
    if df is None or df.empty:
        return None
    out = df.copy()
    out["date"] = pd.to_datetime(trade_date)
    return out


def fetch_sc_receipts(
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
    *,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch INE SC warehouse receipts; merges with local CSV cache."""
    end = pd.Timestamp(end_date or datetime.now().date())
    default_start = end - pd.Timedelta(days=DEFAULT_LOOKBACK_DAYS)
    start = pd.Timestamp(start_date or max(SC_LISTING_DATE, default_start))

    cached = pd.DataFrame()
    if use_cache and RECEIPTS_CSV.exists():
        cached = pd.read_csv(RECEIPTS_CSV, parse_dates=["date"])
        cached = cached.sort_values("date").reset_index(drop=True)

    fetch_start = start
    if not cached.empty:
        last_cached = cached["date"].max()
        if last_cached >= end - pd.Timedelta(days=3):
            return cached[(cached["date"] >= start) & (cached["date"] <= end)].reset_index(drop=True)
        fetch_start = max(start, last_cached + pd.Timedelta(days=1))

    trade_days: list[date] = []
    cur = fetch_start.date()
    end_d = end.date()
    while cur <= end_d:
        if cur.strftime("%Y%m%d") in TRADING_CALENDAR:
            trade_days.append(cur)
        cur += timedelta(days=1)

    rows: list[pd.DataFrame] = []
    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as pool:
        futures = {pool.submit(_shfe_sc_receipt, d): d for d in trade_days}
        for fut in as_completed(futures):
            try:
                row = fut.result()
                if row is not None:
                    rows.append(row)
            except Exception as exc:
                warnings.warn(f"SC receipt {futures[fut]} failed: {exc}")

    if rows:
        fresh = pd.concat(rows, ignore_index=True)
        fresh["date"] = pd.to_datetime(fresh["date"])
        merged = pd.concat([cached, fresh], ignore_index=True) if not cached.empty else fresh
        merged = merged.sort_values("date").drop_duplicates("date", keep="last")
        merged.to_csv(RECEIPTS_CSV, index=False)
        out = merged[(merged["date"] >= start) & (merged["date"] <= end)].copy()
        return out.reset_index(drop=True)

    if not cached.empty:
        return cached[(cached["date"] >= start) & (cached["date"] <= end)].reset_index(drop=True)
    raise RuntimeError("No SC receipt data available.")


def fit_receipt_models(df: pd.DataFrame) -> dict:
    """Fit linear trend and AR(1) on receipt levels (000 bbl)."""
    ts = df.set_index("date")["receipt"].astype(float).sort_index()
    y = ts.values
    n = len(y)
    t = np.arange(n, dtype=float)

    # Linear trend: receipt ~ time index
    X = sm.add_constant(t)
    ols = sm.OLS(y, X).fit()
    linear = {
        "model": "OLS linear trend",
        "n_obs": int(n),
        "intercept_bbl": round(float(ols.params[0]), 0),
        "slope_bbl_per_day": round(float(ols.params[1]), 1),
        "slope_bbl_per_year": round(float(ols.params[1]) * 252, 0),
        "r_squared": round(float(ols.rsquared), 4),
        "aic": round(float(ols.aic), 1),
    }

    # AR(1) on levels
    ar1 = ARIMA(y, order=(1, 0, 0)).fit()
    params = getattr(ar1, "params", None)
    const_val = np.nan
    if params is not None:
        if hasattr(params, "get"):
            const_val = float(params.get("const", np.nan))
        elif len(params) > 1:
            const_val = float(params[0])
    phi = float(ar1.arparams[0]) if len(ar1.arparams) else np.nan
    ar1_summary = {
        "model": "AR(1) on level",
        "n_obs": int(n),
        "const": round(float(const_val), 0) if pd.notna(const_val) else None,
        "ar1_coef": round(phi, 4) if pd.notna(phi) else None,
        "aic": round(float(ar1.aic), 1),
        "bic": round(float(ar1.bic), 1),
    }

    # Mean-reversion half-life from AR(1): HL = -ln(2)/ln(phi) trading days
    if phi and 0 < phi < 1:
        half_life = -np.log(2) / np.log(phi)
        ar1_summary["half_life_days"] = round(float(half_life), 1)
    else:
        ar1_summary["half_life_days"] = None

    return {"linear_trend": linear, "ar1_level": ar1_summary}


def summarize_receipts(df: pd.DataFrame, models: dict | None = None) -> dict:
    if models is None:
        models = fit_receipt_models(df)

    latest = df.iloc[-1]
    receipt = df["receipt"].astype(float)
    mu = receipt.mean()
    sigma = receipt.std(ddof=1)
    z = (latest["receipt"] - mu) / sigma if sigma else np.nan

    # 20-day change
    chg_20d = np.nan
    if len(df) >= 21:
        chg_20d = latest["receipt"] - df.iloc[-21]["receipt"]

    return {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "latest_date": latest["date"].strftime("%Y-%m-%d"),
        "receipt_bbl": int(latest["receipt"]),
        "receipt_chg_day": int(latest.get("receipt_chg", 0)),
        "receipt_zscore_full_sample": round(float(z), 2),
        "receipt_mean_bbl": round(float(mu), 0),
        "receipt_std_bbl": round(float(sigma), 0),
        "receipt_min_bbl": int(receipt.min()),
        "receipt_max_bbl": int(receipt.max()),
        "change_20d_bbl": int(chg_20d) if pd.notna(chg_20d) else None,
        "n_obs": len(df),
        "start_date": df["date"].min().strftime("%Y-%m-%d"),
        "source": "akshare get_shfe_receipt_2/3 (SC via INE/SHFE warehouse API)",
        "models": models,
        "interpretation": (
            "Rising receipts at INE delivery sites = storage build / deliverable supply; "
            "falling receipts = draw / tight physical. Compare with term structure and run-cuts."
        ),
    }


def build_receipt_panel(**kwargs) -> tuple[pd.DataFrame, dict]:
    df = fetch_sc_receipts(**kwargs)
    models = fit_receipt_models(df)
    summary = summarize_receipts(df, models)
    return df, summary


def main() -> None:
    df, summary = build_receipt_panel()
    summary_path = DATA_DIR / "sc_warehouse_receipts_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Wrote {RECEIPTS_CSV} ({len(df)} rows)")
    print(f"Wrote {summary_path}")
    print("\nReceipt snapshot:")
    for k in ["latest_date", "receipt_bbl", "receipt_zscore_full_sample", "change_20d_bbl"]:
        print(f"  {k}: {summary[k]}")
    print("\nFitted models:")
    print(json.dumps(summary["models"], indent=2))


if __name__ == "__main__":
    main()
