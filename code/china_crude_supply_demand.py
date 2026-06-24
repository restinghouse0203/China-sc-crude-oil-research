#!/usr/bin/env python3
"""China crude import growth vs refining / supply metrics.

Primary source: EIA International Data API v2 (free key via EIA_API_KEY env var).
  - Crude imports: productId=57, activityId=3 (TBPD)
  - Crude production: productId=57, activityId=1 (TBPD)
  - Total petroleum consumption (refinery demand proxy): productId=53, activityId=2

Weekly refinery CDU utilization: OilChem curated CSV (see fetch_refinery_utilization.py).

Refresh EIA caches:
  EIA_API_KEY=your_key EIA_FORCE_REFRESH=1 python3 china_crude_supply_demand.py

Outputs:
  - data/china_crude_imports_refining.csv
  - data/china_crude_supply_demand_summary.json
  - data/china_refinery_utilization_summary.json
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import pandas as pd

from _paths import DATA_DIR
from fetch_market_data import eia_fetch, eia_to_tbpd, refresh_eia_china_crude_caches
from fetch_refinery_utilization import load_refinery_utilization, summarize_refinery_utilization

EIA_REFERENCE_ANNUAL = pd.DataFrame(
    {
        "period": pd.to_datetime(["2023-01-01", "2024-01-01"]),
        "crude_imports_tbpd": [11300.0, 11100.0],
        "crude_production_tbpd": [4200.0, 4300.0],
        "refinery_runs_tbpd": [14800.0, 14200.0],
        "source_note": ["EIA Today in Energy", "EIA Today in Energy"],
    }
)


def _annual_series(product_id: str, activity_id: str, label: str) -> pd.DataFrame:
    try:
        raw = eia_fetch(
            product_id=product_id,
            activity_id=activity_id,
            frequency="annual",
            length=30,
            cache_key=f"eia_chn_p{product_id}_a{activity_id}_annual",
        )
        tbpd = eia_to_tbpd(raw)
        if tbpd.empty:
            return pd.DataFrame(columns=["period", label])
        return tbpd[["period", "value"]].rename(columns={"value": label})
    except Exception as exc:
        print(f"Warning: EIA fetch failed for {label} ({exc}); using fallback if available.")
        return pd.DataFrame(columns=["period", label])


def build_supply_demand_panel() -> pd.DataFrame:
    imports = _annual_series("57", "3", "crude_imports_tbpd")
    production = _annual_series("57", "1", "crude_production_tbpd")
    consumption = _annual_series("53", "2", "total_petroleum_consumption_tbpd")

    panel = imports.merge(production, on="period", how="outer")
    panel = panel.merge(consumption, on="period", how="outer")
    panel = panel.sort_values("period").reset_index(drop=True)

    if panel["crude_imports_tbpd"].isna().all():
        panel = EIA_REFERENCE_ANNUAL[
            ["period", "crude_imports_tbpd", "crude_production_tbpd", "refinery_runs_tbpd"]
        ].copy()
    else:
        ref = EIA_REFERENCE_ANNUAL.set_index("period")
        panel = panel.set_index("period")
        for col in ["crude_imports_tbpd", "crude_production_tbpd"]:
            if col in ref.columns:
                panel[col] = panel[col].combine_first(ref[col])
        panel["refinery_runs_tbpd"] = panel["total_petroleum_consumption_tbpd"]
        panel["refinery_runs_tbpd"] = panel["refinery_runs_tbpd"].combine_first(ref["refinery_runs_tbpd"])
        panel = panel.reset_index()

    panel["crude_supply_to_refineries_tbpd"] = (
        panel["crude_imports_tbpd"] + panel["crude_production_tbpd"]
    )
    if "refinery_runs_tbpd" not in panel.columns:
        panel["refinery_runs_tbpd"] = panel.get("total_petroleum_consumption_tbpd")
    if "total_petroleum_consumption_tbpd" in panel.columns:
        panel["refinery_runs_tbpd"] = panel["refinery_runs_tbpd"].fillna(
            panel["total_petroleum_consumption_tbpd"]
        )

    panel["import_dependence_pct"] = (
        panel["crude_imports_tbpd"] / panel["crude_supply_to_refineries_tbpd"] * 100
    )
    panel["imports_yoy_pct"] = panel["crude_imports_tbpd"].pct_change() * 100
    panel["refinery_runs_yoy_pct"] = panel["refinery_runs_tbpd"].pct_change() * 100
    panel["import_minus_refinery_growth_pp"] = (
        panel["imports_yoy_pct"] - panel["refinery_runs_yoy_pct"]
    )
    return panel


def summarize(panel: pd.DataFrame, util_summary: dict) -> dict:
    latest = panel.dropna(subset=["crude_imports_tbpd"]).iloc[-1]
    prev = panel.dropna(subset=["crude_imports_tbpd"]).iloc[-2] if len(panel) > 1 else latest

    phase = "imports lagging runs"
    if pd.notna(latest.get("import_minus_refinery_growth_pp")):
        if latest["import_minus_refinery_growth_pp"] > 1:
            phase = "imports declining slower than runs (inventory/build risk)"
        elif latest["import_minus_refinery_growth_pp"] < -1:
            phase = "runs falling faster than imports (run-cut / utilization down)"

    eia_refreshed = os.environ.get("EIA_FORCE_REFRESH", "") == "1"
    api_key_set = bool(os.environ.get("EIA_API_KEY"))

    return {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "latest_year": int(latest["period"].year),
        "crude_imports_tbpd": round(float(latest["crude_imports_tbpd"]), 1),
        "crude_production_tbpd": round(float(latest["crude_production_tbpd"]), 1)
        if pd.notna(latest.get("crude_production_tbpd"))
        else None,
        "refinery_runs_tbpd": round(float(latest["refinery_runs_tbpd"]), 1)
        if pd.notna(latest.get("refinery_runs_tbpd"))
        else None,
        "import_dependence_pct": round(float(latest["import_dependence_pct"]), 1)
        if pd.notna(latest.get("import_dependence_pct"))
        else None,
        "imports_yoy_pct": round(float(latest["imports_yoy_pct"]), 2)
        if pd.notna(latest.get("imports_yoy_pct"))
        else None,
        "refinery_runs_yoy_pct": round(float(latest["refinery_runs_yoy_pct"]), 2)
        if pd.notna(latest.get("refinery_runs_yoy_pct"))
        else None,
        "prior_year": int(prev["period"].year),
        "capacity_cycle_phase_annual": phase,
        "refinery_utilization": util_summary,
        "eia_refresh": {
            "forced": eia_refreshed,
            "api_key_set": api_key_set,
            "note": "Run with EIA_API_KEY=... EIA_FORCE_REFRESH=1 to pull live EIA International data",
        },
        "sources": {
            "annual_balance": "EIA International Data API v2 (product 57 imports/production; product 53 consumption)",
            "weekly_utilization": "OilChem CDU utilization — curated CSV (data/china_refinery_utilization.csv)",
            "reference": "https://www.eia.gov/todayinenergy/detail.php?id=64544",
        },
    }


def main() -> None:
    if os.environ.get("EIA_FORCE_REFRESH", "") == "1":
        print("Refreshing EIA China crude caches...")
        counts = refresh_eia_china_crude_caches()
        for key, n in counts.items():
            print(f"  {key}: {n} rows")

    panel = build_supply_demand_panel()
    util_df = load_refinery_utilization()
    util_summary = summarize_refinery_utilization(util_df)
    summary = summarize(panel, util_summary)

    panel_path = DATA_DIR / "china_crude_imports_refining.csv"
    summary_path = DATA_DIR / "china_crude_supply_demand_summary.json"
    util_summary_path = DATA_DIR / "china_refinery_utilization_summary.json"

    panel["period"] = panel["period"].dt.strftime("%Y")
    panel.to_csv(panel_path, index=False, float_format="%.2f")
    summary_path.write_text(json.dumps(summary, indent=2))
    util_summary_path.write_text(json.dumps(util_summary, indent=2))

    print(f"Wrote {panel_path} ({len(panel)} rows)")
    print(f"Wrote {summary_path}")
    print(f"Wrote {util_summary_path}")
    print("\nSupply/demand snapshot:")
    for k, v in summary.items():
        if k not in ("sources", "refinery_utilization", "eia_refresh"):
            print(f"  {k}: {v}")
    print("\nRefinery utilization:")
    for k in ["latest_week_end", "util_all_pct", "wow_change_all_pp", "cycle_phase"]:
        print(f"  {k}: {util_summary[k]}")


if __name__ == "__main__":
    main()
