"""Shared fetch helpers for SC research scripts."""

from __future__ import annotations

import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any

import akshare as ak
import numpy as np
import pandas as pd

from _paths import DATA_DIR

FRED_SERIES = {
    "brent_usd_monthly": "MCOILBRENTEU",
    "dubai_usd": "POILDUBUSDM",
    "cny_usd": "DEXCHUS",
}


def load_brent_daily() -> pd.Series:
    """ICE Brent daily close proxy via akshare Sina foreign futures (symbol OIL)."""
    df = ak.futures_foreign_hist(symbol="OIL")
    s = df.set_index(pd.to_datetime(df["date"]))["close"].astype(float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index().rename("brent_usd_bbl")


def load_dubai_monthly() -> pd.Series:
    """Dubai spot USD/bbl (monthly) from FRED, for import-parity reference."""
    return fetch_fred_series(FRED_SERIES["dubai_usd"]).rename("dubai_usd_bbl")


def fetch_fred_series(series_id: str) -> pd.Series:
    """Download a FRED series as a daily DatetimeIndex series."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        df = pd.read_csv(
            io.StringIO(resp.read().decode()),
            parse_dates=["observation_date"],
        )
    col = [c for c in df.columns if c != "observation_date"][0]
    s = df.set_index("observation_date")[col].astype(float).rename(series_id)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def latest_trading_day(max_lookback: int = 10) -> pd.Timestamp:
    """Return the most recent INE trading day with SC data."""
    end = datetime.now()
    start = end - timedelta(days=max_lookback)
    daily = ak.get_futures_daily(
        start_date=start.strftime("%Y%m%d"),
        end_date=end.strftime("%Y%m%d"),
        market="INE",
    )
    sc = daily[daily["symbol"].str.match(r"^SC\d", case=False, na=False)]
    if sc.empty:
        raise RuntimeError("No INE SC contracts returned in lookback window.")
    return pd.to_datetime(sc["date"].max())


def fetch_sc_curve(trade_date: pd.Timestamp | None = None) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Fetch all SC contract closes/settles for a trade date."""
    if trade_date is None:
        trade_date = latest_trading_day()

    start = trade_date - timedelta(days=7)
    daily = ak.get_futures_daily(
        start_date=start.strftime("%Y%m%d"),
        end_date=trade_date.strftime("%Y%m%d"),
        market="INE",
    )
    sc = daily[daily["symbol"].str.match(r"^SC\d", case=False, na=False)].copy()
    sc["date"] = pd.to_datetime(sc["date"])
    sc = sc[sc["date"] == trade_date].copy()

    def _parse_contract(symbol: str) -> pd.Timestamp:
        m = re.match(r"^SC(\d{2})(\d{2})$", symbol, flags=re.I)
        if not m:
            raise ValueError(f"Unexpected SC symbol: {symbol}")
        year = 2000 + int(m.group(1))
        month = int(m.group(2))
        return pd.Timestamp(year=year, month=month, day=1)

    sc["contract_month"] = sc["symbol"].str.upper().map(_parse_contract)
    sc["settle"] = pd.to_numeric(sc["settle"], errors="coerce")
    sc["close"] = pd.to_numeric(sc["close"], errors="coerce")
    sc["volume"] = pd.to_numeric(sc["volume"], errors="coerce").fillna(0)
    sc["open_interest"] = pd.to_numeric(sc["open_interest"], errors="coerce").fillna(0)
    sc = sc.sort_values(["contract_month", "open_interest"], ascending=[True, False])
    return sc.reset_index(drop=True), trade_date


def pick_front_and_6m(sc_curve: pd.DataFrame) -> dict[str, Any]:
    """Select front month (max OI among liquid nearby) and ~6M contract."""
    liquid = sc_curve[(sc_curve["volume"] > 0) | (sc_curve["open_interest"] > 100)].copy()
    if liquid.empty:
        liquid = sc_curve.copy()

    front = liquid.sort_values("open_interest", ascending=False).iloc[0]
    front_month = front["contract_month"]
    target_month = front_month + pd.DateOffset(months=6)

    candidates = sc_curve[sc_curve["contract_month"] >= target_month].copy()
    if candidates.empty:
        six_m = sc_curve.iloc[-1]
    else:
        candidates["month_diff"] = (
            (candidates["contract_month"].dt.year - target_month.year) * 12
            + (candidates["contract_month"].dt.month - target_month.month)
        ).abs()
        six_m = candidates.sort_values(["month_diff", "open_interest"], ascending=[True, False]).iloc[0]

    months_apart = (
        (six_m["contract_month"].year - front_month.year) * 12
        + (six_m["contract_month"].month - front_month.month)
    )
    spread_cny = float(six_m["settle"] - front["settle"])
    structure = "contango" if spread_cny > 0 else "backwardation" if spread_cny < 0 else "flat"

    return {
        "front_symbol": front["symbol"],
        "front_month": front_month.strftime("%Y-%m"),
        "front_settle_cny_bbl": float(front["settle"]),
        "front_open_interest": int(front["open_interest"]),
        "six_m_symbol": six_m["symbol"],
        "six_m_month": six_m["contract_month"].strftime("%Y-%m"),
        "six_m_settle_cny_bbl": float(six_m["settle"]),
        "months_apart": int(months_apart),
        "spread_cny_bbl": spread_cny,
        "spread_pct_of_front": spread_cny / float(front["settle"]) * 100,
        "annualized_roll_yield_pct": (
            spread_cny / float(front["settle"]) * (12 / months_apart) * 100 if months_apart else np.nan
        ),
        "term_structure": structure,
    }


def load_sc_continuous_daily() -> pd.Series:
    """SC main continuous close (CNY/bbl) from Sina via akshare."""
    df = ak.futures_main_sina(symbol="SC0")
    s = df.set_index(pd.to_datetime(df["日期"]))["收盘价"].astype(float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index().rename("sc_cny_bbl")


def eia_fetch(
    *,
    product_id: str,
    activity_id: str,
    frequency: str = "annual",
    country: str = "CHN",
    length: int = 40,
    cache_key: str | None = None,
) -> pd.DataFrame:
    """Fetch EIA International data with local JSON cache."""
    api_key = os.environ.get("EIA_API_KEY", "DEMO_KEY")
    cache_key = cache_key or f"eia_{country}_{product_id}_{activity_id}_{frequency}"
    cache_path = DATA_DIR / f"{cache_key}.json"

    if cache_path.exists() and os.environ.get("EIA_FORCE_REFRESH", "") != "1":
        cached = json.loads(cache_path.read_text())
        age_hours = (time.time() - cached.get("fetched_at", 0)) / 3600
        if age_hours < 24 * 7:
            return pd.DataFrame(cached["rows"])

    params = {
        "api_key": api_key,
        "frequency": frequency,
        "data[0]": "value",
        "facets[countryRegionId][]": country,
        "facets[productId][]": product_id,
        "facets[activityId][]": activity_id,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": str(length),
    }
    url = "https://api.eia.gov/v2/international/data/?" + urllib.parse.urlencode(params, doseq=True)

    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read())
            rows = payload["response"]["data"]
            cache_path.write_text(json.dumps({"fetched_at": time.time(), "rows": rows}, indent=2))
            return pd.DataFrame(rows)
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                time.sleep(5 * (attempt + 1))
                continue
            if cache_path.exists():
                cached = json.loads(cache_path.read_text())
                return pd.DataFrame(cached["rows"])
            raise

    if cache_path.exists():
        cached = json.loads(cache_path.read_text())
        return pd.DataFrame(cached["rows"])
    raise RuntimeError(f"EIA fetch failed and no cache at {cache_path}")


def eia_to_tbpd(df: pd.DataFrame) -> pd.DataFrame:
    """Keep thousand-barrels-per-day rows only."""
    out = df[df["unit"] == "TBPD"].copy()
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["value"])
    out["period"] = pd.to_datetime(out["period"].astype(str).str.slice(0, 4), format="%Y")
    return out.sort_values("period")


def refresh_eia_china_crude_caches(*, length: int = 40) -> dict[str, int]:
    """Force-refresh all EIA China crude cache files. Set EIA_FORCE_REFRESH=1 before calling."""
    os.environ["EIA_FORCE_REFRESH"] = "1"
    specs = [
        ("57", "3", "annual", "eia_chn_p57_a3_annual"),
        ("57", "1", "annual", "eia_chn_p57_a1_annual"),
        ("53", "2", "annual", "eia_chn_p53_a2_annual"),
    ]
    counts: dict[str, int] = {}
    for product_id, activity_id, frequency, cache_key in specs:
        df = eia_fetch(
            product_id=product_id,
            activity_id=activity_id,
            frequency=frequency,
            length=length,
            cache_key=cache_key,
        )
        counts[cache_key] = len(df)
        time.sleep(2)
    return counts
