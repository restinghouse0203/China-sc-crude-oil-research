#!/usr/bin/env python3
"""Build Brent (pre-2018) + INE SC (post-2018) monthly oil price splice, 1987-05–2025.

No pre-1987 proxy — sample starts when FRED Brent (MCOILBRENTEU) begins.

Data sources (API):
  - Brent nominal USD/bbl : FRED MCOILBRENTEU (from 1987-05)
  - SC nominal CNY/bbl    : akshare futures_main_sina SC0 (from 2018-03)
  - US CPI                : FRED CPIAUCSL
  - China CPI             : FRED CHNCPIALLMINMEI
  - CNY/USD               : FRED DEXCHUS (monthly average)

Splice rule: Brent through 2017-12; SC (USD-converted) from 2018-01 (Brent bridge if SC missing).
"""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent # the directory of the script folder

START = pd.Timestamp("1987-05-01")
END = pd.Timestamp("2025-12-01")
SPLICE_START = pd.Timestamp("2018-01-01")


def fetch_fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        df = pd.read_csv(
            io.StringIO(resp.read().decode()),
            parse_dates=["observation_date"],
        )
    col = [c for c in df.columns if c != "observation_date"][0]
    s = df.set_index("observation_date")[col].rename(series_id)
    s.index = s.index.to_period("M").to_timestamp(how="start")
    return s.sort_index()


def monthly_mean(series: pd.Series) -> pd.Series:
    s = series.copy()
    s.index = pd.to_datetime(s.index)
    return s.resample("MS").mean()


def load_sc_monthly() -> pd.Series:
    df = ak.futures_main_sina(symbol="SC0")
    df["date"] = pd.to_datetime(df["日期"])
    close = df.set_index("date")["收盘价"].astype(float)
    close.index = close.index.to_period("M").to_timestamp(how="start")
    return close.groupby(level=0).last().rename("sc_nominal_cny")


def build_oil_splice() -> pd.DataFrame:
    brent = fetch_fred("MCOILBRENTEU").rename("brent_nominal_usd")
    us_cpi = fetch_fred("CPIAUCSL").rename("us_cpi")
    china_cpi = fetch_fred("CHNCPIALLMINMEI").rename("china_cpi")
    cny_usd = monthly_mean(fetch_fred("DEXCHUS")).rename("cny_usd")

    idx = pd.date_range(START, END, freq="MS")
    us_cpi = us_cpi.reindex(idx).ffill()
    china_cpi = china_cpi.reindex(idx).ffill()

    brent_on_idx = brent.reindex(idx)
    brent_pre = brent_on_idx.copy()
    brent_pre.loc[brent_pre.index >= SPLICE_START] = np.nan

    sc_cny = load_sc_monthly()
    sc_usd = (sc_cny / cny_usd.reindex(sc_cny.index)).rename("sc_nominal_usd")

    out = pd.DataFrame(index=idx)
    out.index.name = "date"

    out["brent_nominal_usd"] = brent_on_idx
    out["brent_pre2018_usd"] = brent_pre
    out["sc_nominal_cny"] = sc_cny.reindex(idx)
    out["sc_nominal_usd"] = sc_usd.reindex(idx)
    out["cny_usd"] = cny_usd.reindex(idx)
    out["us_cpi"] = us_cpi
    out["china_cpi"] = china_cpi

    # Spliced nominal USD: Brent through 2017-12; SC USD from 2018-01
    out["price_spliced_nominal_usd"] = out["brent_pre2018_usd"]
    sc_mask = out.index >= SPLICE_START
    out.loc[sc_mask, "price_spliced_nominal_usd"] = out.loc[sc_mask, "sc_nominal_usd"]
    bridge = sc_mask & out["price_spliced_nominal_usd"].isna()
    out.loc[bridge, "price_spliced_nominal_usd"] = out.loc[bridge, "brent_nominal_usd"]

    # Real price for rpo_sc: US CPI pre-2018; China CPI post-2018
    out["price_real_pre2018"] = out["brent_pre2018_usd"] / out["us_cpi"]
    china_cpi_fill = out["china_cpi"].fillna(out["us_cpi"])
    out["price_real_post2018"] = out["sc_nominal_cny"] / china_cpi_fill
    out["price_spliced_real"] = out["price_real_pre2018"]
    out.loc[sc_mask, "price_spliced_real"] = out.loc[sc_mask, "price_real_post2018"]
    bridge_real = sc_mask & out["price_spliced_real"].isna()
    out.loc[bridge_real, "price_spliced_real"] = (
        out.loc[bridge_real, "price_spliced_nominal_usd"] / out.loc[bridge_real, "us_cpi"]
    )

    out["rpo_sc"] = 100.0 * np.log(out["price_spliced_real"])
    out["segment"] = np.where(
        out.index < SPLICE_START,
        "brent",
        np.where(out["sc_nominal_usd"].notna(), "sc", "brent_bridge"),
    )

    return out.reset_index()


def main() -> None:
    out = build_oil_splice()
    out_path = ROOT / "data" / "oil_price_splice_1973_2025.csv"
    out.to_csv(out_path, index=False, float_format="%.6f")

    print(f"Wrote {out_path}")
    print(f"Rows: {len(out)}  ({START.date()} → {END.date()})")
    print(f"Missing brent_nominal_usd: {out['brent_nominal_usd'].isna().sum()}")
    print(f"Missing rpo_sc: {out['rpo_sc'].isna().sum()}")
    print("\nSplice window:")
    print(
        out[(out["date"] >= "2017-10-01") & (out["date"] <= "2018-04-01")][
            ["date", "brent_pre2018_usd", "sc_nominal_usd", "price_spliced_nominal_usd", "rpo_sc", "segment"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
