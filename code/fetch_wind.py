"""Wind terminal helpers (WindPy). Requires Wind client running locally."""

from __future__ import annotations

import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from _paths import DATA_DIR
from fetch_market_data import FRED_SERIES, fetch_fred_series, load_dubai_monthly

# Wind EDB: Dubai crude spot, USD/bbl (daily). Confirm in Wind EDB search "现货价:迪拜:原油".
WIND_DUBAI_EDB = os.environ.get("WIND_DUBAI_CODE", "S0031525")
DUBAI_WIND_CSV = DATA_DIR / "dubai_spot_wind_daily.csv"

# Wind EDB: MEG/EG CFR China, USD/t — search "乙二醇:CFR:中国" in Wind EDB code generator.
WIND_EG_CFR_EDB = os.environ.get("WIND_EG_CFR_CODE", "S5708328")
EG_CFR_WIND_CSV = DATA_DIR / "eg_cfr_wind_daily.csv"
EG_CFR_CURATED_CSV = DATA_DIR / "eg_import_cfr_curated.csv"


def _wind_session():
    """Start WindPy if available."""
    from WindPy import w

    if not w.isconnected():
        err = w.start()
        if err.ErrorCode != 0:
            raise RuntimeError(f"Wind start failed: {err.Data}")
    return w


def fetch_dubai_spot_wind(
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.Series:
    """Pull daily Dubai spot (USD/bbl) from Wind EDB and cache to CSV."""
    end_ts = pd.Timestamp(end or datetime.now().date())
    start_ts = pd.Timestamp(start or end_ts - pd.Timedelta(days=756))

    w = _wind_session()
    result = w.edb(
        WIND_DUBAI_EDB,
        start_ts.strftime("%Y-%m-%d"),
        end_ts.strftime("%Y-%m-%d"),
        "Fill=Previous",
    )
    if result.ErrorCode != 0:
        raise RuntimeError(f"Wind edb({WIND_DUBAI_EDB}) failed: {result.Data}")

    dates = pd.to_datetime(result.Times)
    values = pd.to_numeric(result.Data[0], errors="coerce")
    s = pd.Series(values, index=dates, name="dubai_usd_bbl").dropna().sort_index()
    s.index = pd.to_datetime(s.index)

    _merge_dubai_cache(s)
    return s


def _merge_dubai_cache(series: pd.Series) -> None:
    if DUBAI_WIND_CSV.exists():
        cached = pd.read_csv(DUBAI_WIND_CSV, parse_dates=["date"])
        old = cached.set_index("date")["dubai_usd_bbl"]
        series = pd.concat([old, series]).sort_index()
        series = series[~series.index.duplicated(keep="last")]
    out = series.rename("dubai_usd_bbl").reset_index()
    out.columns = ["date", "dubai_usd_bbl"]
    out.to_csv(DUBAI_WIND_CSV, index=False, float_format="%.4f")


def load_dubai_daily_wind(
    *,
    lookback_days: int = 756,
    refresh: bool = False,
) -> tuple[pd.Series, str]:
    """Daily Dubai spot: Wind live → cached Wind CSV → FRED monthly fallback."""
    end = pd.Timestamp.now().normalize()
    start = end - pd.Timedelta(days=lookback_days + 30)

    if refresh or not DUBAI_WIND_CSV.exists():
        try:
            s = fetch_dubai_spot_wind(start, end)
            return s, f"Wind EDB {WIND_DUBAI_EDB} (live)"
        except Exception as exc:
            warnings.warn(f"Wind Dubai fetch failed ({exc}); trying cache/FRED.")

    if DUBAI_WIND_CSV.exists():
        df = pd.read_csv(DUBAI_WIND_CSV, parse_dates=["date"])
        s = df.set_index("date")["dubai_usd_bbl"].astype(float).sort_index()
        s = s.loc[s.index >= start]
        if len(s) >= 30:
            return s, f"Wind EDB {WIND_DUBAI_EDB} (cached CSV)"

    monthly = load_dubai_monthly()
    daily_idx = pd.date_range(monthly.index.min(), end, freq="D")
    s = monthly.reindex(daily_idx).ffill().dropna()
    return s, f"FRED {FRED_SERIES['dubai_usd']} fallback (monthly ffill)"


def refresh_dubai_wind_cache(*, lookback_days: int = 2000) -> int:
    """Force Wind pull and return row count written."""
    end = pd.Timestamp.now().normalize()
    start = end - pd.Timedelta(days=lookback_days)
    s = fetch_dubai_spot_wind(start, end)
    return len(s)


def _merge_edb_cache(series: pd.Series, path: Path, value_col: str) -> None:
    if path.exists():
        cached = pd.read_csv(path, parse_dates=["date"])
        old = cached.set_index("date")[value_col]
        series = pd.concat([old, series]).sort_index()
        series = series[~series.index.duplicated(keep="last")]
    out = series.rename(value_col).reset_index()
    out.columns = ["date", value_col]
    out.to_csv(path, index=False, float_format="%.4f")


def fetch_eg_cfr_wind(
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.Series:
    """Pull daily EG/MEG CFR China (USD/t) from Wind EDB."""
    end_ts = pd.Timestamp(end or datetime.now().date())
    start_ts = pd.Timestamp(start or end_ts - pd.Timedelta(days=756))

    w = _wind_session()
    result = w.edb(
        WIND_EG_CFR_EDB,
        start_ts.strftime("%Y-%m-%d"),
        end_ts.strftime("%Y-%m-%d"),
        "Fill=Previous",
    )
    if result.ErrorCode != 0:
        raise RuntimeError(f"Wind edb({WIND_EG_CFR_EDB}) failed: {result.Data}")

    dates = pd.to_datetime(result.Times)
    values = pd.to_numeric(result.Data[0], errors="coerce")
    s = pd.Series(values, index=dates, name="eg_cfr_usd_t").dropna().sort_index()
    s.index = pd.to_datetime(s.index)
    _merge_edb_cache(s, EG_CFR_WIND_CSV, "eg_cfr_usd_t")
    return s


def load_eg_cfr_curated() -> pd.Series:
    """Weekly/daily curated EG CFR China rows (OilChem / Mysteel export)."""
    if not EG_CFR_CURATED_CSV.exists():
        return pd.Series(dtype=float, name="eg_cfr_usd_t")
    df = pd.read_csv(EG_CFR_CURATED_CSV, parse_dates=["date"])
    s = df.set_index("date")["eg_cfr_usd_t"].astype(float).sort_index()
    return s.rename("eg_cfr_usd_t")


def load_eg_cfr_daily_wind(
    *,
    lookback_days: int = 756,
    refresh: bool = False,
) -> tuple[pd.Series, str]:
    """EG CFR China USD/t: Wind live → Wind CSV → curated CSV → None."""
    end = pd.Timestamp.now().normalize()
    start = end - pd.Timedelta(days=lookback_days + 30)

    if refresh or not EG_CFR_WIND_CSV.exists():
        try:
            s = fetch_eg_cfr_wind(start, end)
            return s, f"Wind EDB {WIND_EG_CFR_EDB} (live)"
        except Exception as exc:
            warnings.warn(f"Wind EG CFR fetch failed ({exc}); trying cache/curated.")

    if EG_CFR_WIND_CSV.exists():
        df = pd.read_csv(EG_CFR_WIND_CSV, parse_dates=["date"])
        s = df.set_index("date")["eg_cfr_usd_t"].astype(float).sort_index()
        s = s.loc[s.index >= start]
        if len(s) >= 10:
            return s, f"Wind EDB {WIND_EG_CFR_EDB} (cached CSV)"

    curated = load_eg_cfr_curated()
    if not curated.empty:
        daily_idx = pd.date_range(curated.index.min(), end, freq="D")
        s = curated.reindex(daily_idx).ffill().dropna()
        return s, f"curated {EG_CFR_CURATED_CSV.name} (ffill to daily)"

    return pd.Series(dtype=float, name="eg_cfr_usd_t"), "unavailable (Wind + curated empty)"


def refresh_eg_cfr_wind_cache(*, lookback_days: int = 2000) -> int:
    end = pd.Timestamp.now().normalize()
    start = end - pd.Timedelta(days=lookback_days)
    s = fetch_eg_cfr_wind(start, end)
    return len(s)
