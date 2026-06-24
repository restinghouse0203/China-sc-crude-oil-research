#!/usr/bin/env python3
"""Compute SC vs Brent/Dubai import-parity basis and z-score.

Data:
  - SC continuous (CNY/bbl): akshare futures_main_sina SC0
  - Brent (USD/bbl): akshare futures_foreign_hist OIL (ICE Brent proxy)
  - Dubai (USD/bbl): Wind EDB S0031525 daily (cached CSV; FRED monthly fallback)
  - CNY/USD: FRED DEXCHUS

Outputs:
  - data/sc_basis_daily.csv
  - data/sc_basis_summary.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from _paths import DATA_DIR
from fetch_market_data import FRED_SERIES, fetch_fred_series, load_brent_daily, load_sc_continuous_daily
from fetch_wind import load_dubai_daily_wind


def build_basis_panel(lookback_days: int = 756) -> tuple[pd.DataFrame, str]:
    sc = load_sc_continuous_daily()
    brent = load_brent_daily()
    dubai_m, dubai_source = load_dubai_daily_wind(lookback_days=lookback_days)
    cny = fetch_fred_series(FRED_SERIES["cny_usd"]).rename("cny_usd")

    idx = sc.index.union(brent.index).union(cny.index).sort_values()
    panel = pd.DataFrame(index=idx)
    panel["sc_cny_bbl"] = sc.reindex(idx)
    panel["brent_usd_bbl"] = brent.reindex(idx).ffill()
    panel["dubai_usd_bbl"] = dubai_m.reindex(idx).ffill()
    panel["cny_usd"] = cny.reindex(idx).ffill()

    panel = panel.dropna(subset=["sc_cny_bbl", "brent_usd_bbl", "cny_usd"])
    panel["sc_usd_bbl"] = panel["sc_cny_bbl"] / panel["cny_usd"]
    panel["basis_sc_minus_brent_usd"] = panel["sc_usd_bbl"] - panel["brent_usd_bbl"]
    panel["basis_sc_minus_dubai_usd"] = panel["sc_usd_bbl"] - panel["dubai_usd_bbl"]
    panel["basis_sc_minus_brent_pct"] = panel["basis_sc_minus_brent_usd"] / panel["brent_usd_bbl"] * 100

    panel = panel.tail(lookback_days).copy()
    return panel.reset_index(names="date"), dubai_source


def summarize_basis(panel: pd.DataFrame, *, dubai_source: str = "") -> dict:
    latest = panel.iloc[-1]
    brent_series = panel["basis_sc_minus_brent_usd"]
    mu_b = brent_series.mean()
    sigma_b = brent_series.std(ddof=1)
    z_b = (latest["basis_sc_minus_brent_usd"] - mu_b) / sigma_b if sigma_b else np.nan

    dubai_series = panel["basis_sc_minus_dubai_usd"]
    mu_d = dubai_series.mean()
    sigma_d = dubai_series.std(ddof=1)
    z_d = (latest["basis_sc_minus_dubai_usd"] - mu_d) / sigma_d if sigma_d else np.nan

    return {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "latest_date": latest["date"].strftime("%Y-%m-%d"),
        "sc_cny_bbl": round(float(latest["sc_cny_bbl"]), 2),
        "sc_usd_bbl": round(float(latest["sc_usd_bbl"]), 2),
        "brent_usd_bbl": round(float(latest["brent_usd_bbl"]), 2),
        "dubai_usd_bbl": round(float(latest["dubai_usd_bbl"]), 2),
        "cny_usd": round(float(latest["cny_usd"]), 4),
        "basis_sc_minus_brent_usd": round(float(latest["basis_sc_minus_brent_usd"]), 2),
        "basis_sc_minus_dubai_usd": round(float(latest["basis_sc_minus_dubai_usd"]), 2),
        "basis_sc_minus_brent_pct": round(float(latest["basis_sc_minus_brent_pct"]), 2),
        "basis_zscore_3y": round(float(z_b), 2),
        "basis_dubai_zscore_3y": round(float(z_d), 2),
        "basis_mean_3y_usd": round(float(mu_b), 2),
        "basis_std_3y_usd": round(float(sigma_b), 2),
        "basis_dubai_mean_3y_usd": round(float(mu_d), 2),
        "basis_dubai_std_3y_usd": round(float(sigma_d), 2),
        "lookback_days": len(panel),
        "sources": {
            "sc": "akshare.futures_main_sina(symbol='SC0')",
            "brent": "akshare.futures_foreign_hist(symbol='OIL') — ICE Brent daily proxy",
            "dubai": dubai_source or f"Wind EDB (see fetch_wind.py)",
            "fx": f"FRED {FRED_SERIES['cny_usd']}",
        },
        "interpretation": (
            "Negative basis = SC below Brent/Dubai in USD (cheaper China landed cost); "
            "positive = premium vs offshore benchmarks after FX conversion."
        ),
    }


def main() -> None:
    panel, dubai_source = build_basis_panel()
    summary = summarize_basis(panel, dubai_source=dubai_source)

    panel_path = DATA_DIR / "sc_basis_daily.csv"
    summary_path = DATA_DIR / "sc_basis_summary.json"

    panel.to_csv(panel_path, index=False, float_format="%.4f")
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"Wrote {panel_path} ({len(panel)} rows)")
    print(f"Wrote {summary_path}")
    print("\nBasis snapshot:")
    for k in [
        "latest_date",
        "sc_usd_bbl",
        "brent_usd_bbl",
        "basis_sc_minus_brent_usd",
        "basis_sc_minus_brent_pct",
        "basis_zscore_3y",
    ]:
        print(f"  {k}: {summary[k]}")


if __name__ == "__main__":
    main()
