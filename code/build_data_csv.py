#!/usr/bin/env python3
"""Merge Kilian d_prod / rea with rpo_sc into BVAR-ready data.csv (1987-05–2025)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent # the directory of the script folder
KILIAN_DATA = ROOT / "data/kilian_data"

START = pd.Timestamp("1987-05-01")
END = pd.Timestamp("2025-12-01")


def load_kilian_dprod_rea() -> pd.DataFrame:
    baseline = pd.read_excel(KILIAN_DATA / "data_1973_2007.xlsx")
    baseline["date"] = pd.to_datetime(baseline["obs"].str.replace("M", "-"), format="%Y-%m")
    baseline = baseline.rename(columns={"dprod": "d_prod"})
    baseline = baseline.loc[
        (baseline["date"] >= START) & (baseline["date"] <= "2007-12-01"),
        ["date", "d_prod", "rea"],
    ]

    extended = pd.read_csv(KILIAN_DATA / "data_extended_2008_2025.csv", parse_dates=["date"])
    extended = extended.loc[
        (extended["date"] >= "2008-01-01") & (extended["date"] <= END),
        ["date", "d_prod", "rea"],
    ]

    merged = pd.concat([baseline, extended], ignore_index=True).sort_values("date")
    dupes = merged["date"].duplicated().sum()
    if dupes:
        raise ValueError(f"Duplicate dates in Kilian merge: {dupes}")
    return merged


def main() -> None:
    from build_oil_splice import build_oil_splice

    kilian = load_kilian_dprod_rea()
    oil = build_oil_splice()[["date", "rpo_sc"]]

    out = kilian.merge(oil, on="date", how="inner")
    out = out.rename(columns={"rpo_sc": "rpo"})
    out = out[["date", "d_prod", "rea", "rpo"]].sort_values("date")

    missing = out.isna().sum()
    if missing.any():
        raise ValueError(f"Missing values in merged data:\n{missing}")

    out_path = ROOT / "data.csv"
    out.to_csv(out_path, index=False, float_format="%.6f")

    print(f"Wrote {out_path}")
    print(f"Rows: {len(out)}  ({out['date'].min().date()} → {out['date'].max().date()})")
    print(out.head(3).to_string(index=False))
    print("...")
    print(out.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()
