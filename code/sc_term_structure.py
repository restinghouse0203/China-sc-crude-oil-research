#!/usr/bin/env python3
"""Snapshot INE SC term structure: front month vs ~6M contract.

Data: akshare get_futures_daily (INE) — mirrors INE daily settlement prices.
Output: data/sc_term_structure_curve.csv, data/sc_term_structure_summary.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from _paths import DATA_DIR
from fetch_market_data import fetch_sc_curve, pick_front_and_6m


def build_term_structure_snapshot() -> tuple[pd.DataFrame, dict]:
    curve, trade_date = fetch_sc_curve()
    summary = pick_front_and_6m(curve)
    summary["trade_date"] = trade_date.strftime("%Y-%m-%d")
    summary["as_of_utc"] = datetime.now(timezone.utc).isoformat()
    summary["source"] = "akshare.get_futures_daily(market='INE')"
    summary["note"] = (
        "Contango (positive front→6M spread) implies storage/carry incentive at "
        "INE bonded delivery sites; backwardation implies tight near-term supply."
    )

    curve_out = curve[
        ["symbol", "contract_month", "close", "settle", "volume", "open_interest"]
    ].copy()
    curve_out["contract_month"] = curve_out["contract_month"].dt.strftime("%Y-%m")
    curve_out["trade_date"] = trade_date.strftime("%Y-%m-%d")
    return curve_out, summary


def main() -> None:
    curve, summary = build_term_structure_snapshot()

    curve_path = DATA_DIR / "sc_term_structure_curve.csv"
    summary_path = DATA_DIR / "sc_term_structure_summary.json"

    curve.to_csv(curve_path, index=False, float_format="%.4f")
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"Wrote {curve_path} ({len(curve)} contracts)")
    print(f"Wrote {summary_path}")
    print("\nTerm structure snapshot:")
    for k in [
        "trade_date",
        "front_symbol",
        "six_m_symbol",
        "spread_cny_bbl",
        "spread_pct_of_front",
        "annualized_roll_yield_pct",
        "term_structure",
    ]:
        print(f"  {k}: {summary[k]}")


if __name__ == "__main__":
    main()
