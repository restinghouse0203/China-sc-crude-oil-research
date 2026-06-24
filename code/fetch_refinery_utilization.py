#!/usr/bin/env python3
"""China refinery CDU utilization (weekly operating rate).

Primary source: OilChem (隆众资讯) weekly 常减压装置产能利用率 — published in industry
articles (no free API). This module reads/maintains a curated CSV that can be extended
manually or from Wind/iFinD exports.

Reference (2026-06-18): https://www.oilchem.net/26-0618-16-ec4c64f377cd3a47.html

Outputs (via china_crude_supply_demand.py or standalone):
  - data/china_refinery_utilization.csv
  - data/china_refinery_utilization_summary.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from _paths import DATA_DIR

UTILIZATION_CSV = DATA_DIR / "china_refinery_utilization.csv"
BASELINE_WEEK = pd.Timestamp("2026-02-26")
BASELINE_ALL_PCT = 73.38  # OilChem pre-conflict reference in Jun-2026 article


def load_refinery_utilization() -> pd.DataFrame:
    """Load weekly CDU utilization panel."""
    df = pd.read_csv(UTILIZATION_CSV, parse_dates=["week_end"])
    return df.sort_values("week_end").reset_index(drop=True)


def summarize_refinery_utilization(df: pd.DataFrame | None = None) -> dict:
    """Summarize latest utilization and cycle positioning."""
    df = load_refinery_utilization() if df is None else df.sort_values("week_end")
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    baseline_row = df[df["week_end"] == BASELINE_WEEK]
    baseline_all = (
        float(baseline_row.iloc[0]["util_all_pct"]) if not baseline_row.empty else BASELINE_ALL_PCT
    )

    wow_all = float(latest["util_all_pct"]) - float(prev["util_all_pct"])
    vs_baseline = float(latest["util_all_pct"]) - baseline_all

    if vs_baseline <= -10:
        cycle_phase = "sharp run-cut phase (utilization well below pre-shock baseline)"
    elif vs_baseline <= -3:
        cycle_phase = "moderate run-cut / margin-driven curtailment"
    elif wow_all >= 0.5:
        cycle_phase = "utilization recovering week-on-week"
    elif wow_all <= -0.5:
        cycle_phase = "utilization still sliding week-on-week"
    else:
        cycle_phase = "utilization stabilizing at reduced level"

    return {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "latest_week_end": latest["week_end"].strftime("%Y-%m-%d"),
        "util_all_pct": round(float(latest["util_all_pct"]), 2),
        "util_major_pct": round(float(latest["util_major_pct"]), 2),
        "util_independent_pct": round(float(latest["util_independent_pct"]), 2),
        "util_megaproject_pct": round(float(latest["util_megaproject_pct"]), 2),
        "wow_change_all_pp": round(wow_all, 2),
        "vs_pre_conflict_baseline_pp": round(vs_baseline, 2),
        "pre_conflict_baseline_week": BASELINE_WEEK.strftime("%Y-%m-%d"),
        "pre_conflict_baseline_all_pct": baseline_all,
        "cycle_phase": cycle_phase,
        "source": str(latest.get("source", "OilChem")),
        "source_url": "https://www.oilchem.net/26-0618-16-ec4c64f377cd3a47.html",
        "notes": (
            "CDU capacity utilization = crude throughput / nameplate CDU capacity. "
            "Independent (地炼) rate is the margin-sensitive teapot segment; "
            "megaproject (大炼化) captures integrated coastal complexes (Hengli, Rongsheng, etc.)."
        ),
    }


def main() -> None:
    df = load_refinery_utilization()
    summary = summarize_refinery_utilization(df)
    out_path = DATA_DIR / "china_refinery_utilization_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"Loaded {len(df)} weekly rows from {UTILIZATION_CSV}")
    print(f"Wrote {out_path}")
    for k, v in summary.items():
        if k not in ("notes", "source_url"):
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
