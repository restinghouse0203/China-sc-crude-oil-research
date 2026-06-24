# SC Research — Data Sources

**As-of:** 2026-06-23 | **Scripts:** `code/sc_term_structure.py`, `code/sc_basis.py`, `code/china_crude_supply_demand.py`, `code/fetch_refinery_utilization.py`, `code/fetch_wind.py`, `code/sc_warehouse_receipts.py`, `code/px_spot.py`, `code/ta_eg_basis.py`

This document records APIs and datasets used for Layer 1 (INE SC crude) research. Wind/iFinD are optional upgrades; all scripts run on **free** sources.

---

## 1. SC term structure (front vs ~6M)

| Item | Detail |
|------|--------|
| **Primary API** | [AKShare](https://github.com/akfamily/akshare) `get_futures_daily(start_date, end_date, market="INE")` |
| **Upstream** | INE daily settlement file (mirrored by AKShare from exchange data) |
| **Fields used** | `symbol`, `date`, `settle`, `close`, `volume`, `open_interest` |
| **Front month rule** | Highest `open_interest` among contracts with volume > 0 or OI > 100 |
| **6M contract rule** | Listed contract closest to front + 6 calendar months |
| **Output files** | `data/sc_term_structure_curve.csv`, `data/sc_term_structure_summary.json` |
| **Official alternative** | [INE SC daily quotes](https://www.ine.cn/en/market/futures/sc/domestic/) |
| **Wind equivalent** | INE SC active contract chain / settlement prices |

**Interpretation:** Positive front→6M spread = **contango** (storage/carry incentive at bonded delivery sites); negative = **backwardation**.

---

## 2. SC vs Brent / Dubai basis

| Series | Source | API / series ID | Frequency |
|--------|--------|-----------------|-----------|
| **SC continuous** | Sina via AKShare | `futures_main_sina(symbol="SC0")` | Daily (CNY/bbl) |
| **Brent** | Sina foreign futures via AKShare | `futures_foreign_hist(symbol="OIL")` | Daily (USD/bbl, ICE Brent proxy) |
| **Dubai spot** | **Wind EDB** (primary) | `S0031525` via `w.edb()` in `fetch_wind.py` | Daily (USD/bbl) |
| **Dubai spot (fallback)** | FRED | `POILDUBUSDM` | Monthly (forward-filled to daily) |
| **CNY/USD** | FRED | `DEXCHUS` | Daily |

**Formulas (in `code/sc_basis.py`):**

- `sc_usd_bbl = sc_cny_bbl / cny_usd`
- `basis_sc_minus_brent_usd = sc_usd_bbl - brent_usd_bbl`
- `basis_zscore_3y` = z-score of Brent basis over ~756 trading days

**Output files:** `data/sc_basis_daily.csv`, `data/sc_basis_summary.json`

**Notes:**

- Brent daily uses **OIL** (Sina ICE Brent futures), not FRED monthly `MCOILBRENTEU`, to align dates with SC.
- **Dubai daily:** Wind EDB `S0031525` (现货价:迪拜:原油). Cached at `data/dubai_spot_wind_daily.csv`. Requires Wind terminal + WindPy; falls back to FRED monthly if Wind unavailable.
- Refresh Wind Dubai cache: `python3 -c "from fetch_wind import refresh_dubai_wind_cache; print(refresh_dubai_wind_cache())"` (Wind must be running).

---

## 3. China crude imports vs refining

| Series | Source | API | Unit |
|--------|--------|-----|------|
| **Crude imports** | EIA International | `productId=57`, `activityId=3`, `countryRegionId=CHN` | TBPD |
| **Crude production** | EIA International | `productId=57`, `activityId=1` | TBPD |
| **Refinery demand proxy** | EIA International | `productId=53`, `activityId=2` (total petroleum consumption) | TBPD |
| **2023–24 validation** | EIA Today in Energy | [detail.php?id=64544](https://www.eia.gov/todayinenergy/detail.php?id=64544) | Mb/d |

**API endpoint:** `https://api.eia.gov/v2/international/data/`  
**API key:** Free at [eia.gov/opendata](https://www.eia.gov/opendata/register.php) — set `EIA_API_KEY` env var. Falls back to `DEMO_KEY` and local JSON cache in `data/eia_chn_*.json`.

**Derived metrics:**

- `import_dependence_pct = imports / (imports + production)`
- `import_minus_refinery_growth_pp` = YoY import growth − YoY refinery-run growth

**Output files:** `data/china_crude_imports_refining.csv`, `data/china_crude_supply_demand_summary.json`

**EIA refresh (priority 2):**

```bash
export EIA_API_KEY=your_key   # free at eia.gov/opendata
EIA_FORCE_REFRESH=1 python3 china_crude_supply_demand.py
```

Calls `refresh_eia_china_crude_caches()` to overwrite `data/eia_chn_p*.json`. Without a personal key, `DEMO_KEY` may rate-limit; cached JSON is used as fallback.

**Limitations:**

- EIA **consumption** is a refinery-demand proxy, not nameplate capacity.
- China Customs does not expose crude-only volume via AKShare; EIA is the primary free annual series.

---

## 4. China refinery CDU utilization (weekly)

| Item | Detail |
|------|--------|
| **Primary source** | OilChem (隆众资讯) weekly 常减压装置产能利用率 |
| **Access** | No free API — curated from published articles; extend via Wind/iFinD CSV export |
| **Reference article** | [OilChem 2026-06-18](https://www.oilchem.net/26-0618-16-ec4c64f377cd3a47.html) |
| **CSV** | `data/china_refinery_utilization.csv` (append weekly rows manually or from Wind) |
| **Script** | `code/fetch_refinery_utilization.py` |
| **Outputs** | `data/china_refinery_utilization_summary.json` (also embedded in supply/demand summary) |

**Segments tracked:** all-refinery, major (主营), independent (地炼), megaproject (大炼化).

**Latest snapshot (2026-06-18):** 57.54% all (−15.84pp vs 2026-02-26 baseline); independent 43.47%.

---

## 5. Layer 2 — PX spot & PX–naphtha spread

| Item | Detail |
|------|--------|
| **OilChem (primary attempt)** | [PX hub](https://fiber.oilchem.net/fiber/p-xylene.shtml) — scrapes PX–石脑油 加工费 article links |
| **OilChem limitation** | Detailed price tables **paywalled**; append subscriber rows to `data/px_naphtha_oilchem.csv` |
| **PX spot (daily)** | akshare `futures_spot_price` (latest ZCE spot assessment) + `futures_main_sina(PX0)` history |
| **PX–naphtha spread** | Curated OilChem CSV if populated; else Brent-implied naphtha proxy |
| **Naphtha proxy** | `naphtha_usd_t = brent_usd_bbl × 8.33 + 12 × 8.33` (crack + bbl/ton conversion) |
| **Script** | `code/px_spot.py` |
| **Outputs** | `data/px_spot_daily.csv`, `data/px_spot_summary.json` |

**Latest snapshot (2026-06-23):** PX spot **8,800 CNY/t**; PX–naphtha **~556 USD/t** (z = +2.75 vs 1y proxy).

**Optional:** `PX_FETCH_SPOT_HISTORY=1` forces slow full ZCE spot history via `futures_spot_price_daily`.

---

## 6. Layer 3–4 — TA/EG basis, PTA margin, EG import parity

| Item | Detail |
|------|--------|
| **TA continuous** | akshare `futures_main_sina(symbol="TA0")` — ZCE PTA main contract |
| **EG continuous** | akshare `futures_main_sina(symbol="EG0")` — DCE MEG main contract |
| **Spot overlay** | akshare `futures_spot_price` (latest-day ZCE/DCE assessments); historical basis backfilled as `futures_close − settle` |
| **PX feedstock** | Merged from `data/px_spot_daily.csv` (`px_spot_cny_t`, forward-filled) |
| **PTA margin** | `pta_margin = px_spot − ta_spot` (CNY/t) |
| **TA–EG spread** | `ta_spot − eg_spot`; also `0.86×TA + 0.34×EG` polyester chain margin |
| **EG CFR China** | Wind EDB via `fetch_wind.fetch_eg_cfr_wind()` (default code `S5708328` — verify in Wind terminal) |
| **EG CFR fallback** | `data/eg_import_cfr_curated.csv` (OilChem/Mysteel weekly CFR; forward-filled to daily) |
| **Import landed cost** | `eg_cfr_usd × cny_usd × 1.13 + 50` (VAT + port fee proxy) |
| **Import parity gap** | `eg_spot − landed` (negative = domestic below import parity) |
| **FX** | FRED `DEXCHUS` |
| **Script** | `code/ta_eg_basis.py` |
| **Outputs** | `data/ta_eg_basis_daily.csv`, `data/ta_eg_basis_summary.json` |

**Latest snapshot (2026-06-23):** TA spot **6,028 CNY/t** (basis **−252**); EG **4,495** (basis **−262**); PTA margin **2,772 CNY/t** (z = +0.5); TA–EG **1,533**; EG import parity gap **−442 CNY/t** (CFR curated).

**Wind refresh:** `python3 -c "from fetch_wind import refresh_eg_cfr_wind_cache; print(refresh_eg_cfr_wind_cache())"` (Wind terminal required).

**Optional:** `TA_EG_FETCH_SPOT_HISTORY=1` for slow full historical spot basis.

---

## 7. INE SC warehouse receipts (daily)

| Item | Detail |
|------|--------|
| **Primary API** | [AKShare](https://github.com/akfamily/akshare) `get_receipt(start_date, end_date, vars_list=['SC'])` |
| **Script** | `code/sc_warehouse_receipts.py` |
| **Cache** | `data/sc_warehouse_receipts.csv` (incremental quarterly fetches) |
| **Outputs** | `data/sc_warehouse_receipts_summary.json` |
| **Models** | OLS linear trend on level; AR(1) on level (half-life from φ) |

**Interpretation:** Receipts at INE designated bonded tanks = deliverable inventory signal. Rising receipts + contango = storage incentive; falling receipts + backwardation = tight physical (consistent with 2026 run-cut phase).

---

## 8. Dependencies

```bash
pip install akshare pandas numpy statsmodels
```

Optional: Wind terminal + WindPy for daily Dubai (`fetch_wind.py`).  
Optional: `EIA_API_KEY` for live EIA refresh (`EIA_FORCE_REFRESH=1` to bypass cache).

---

## 9. Reproducibility

From project root:

```bash
cd code
python3 sc_term_structure.py
python3 sc_basis.py                    # Wind Dubai if terminal running
python3 china_crude_supply_demand.py
python3 fetch_refinery_utilization.py
python3 sc_warehouse_receipts.py       # slow first run (~2018→today)
python3 px_spot.py                     # Layer 2 PX spot + spread
python3 ta_eg_basis.py                 # Layer 3–4 TA/EG basis + margins
```

Or run `SC_research.ipynb` in the project root.

---

## 10. Source log (dated)

| Claim | Source | Accessed |
|-------|--------|----------|
| SC curve 2026-06-22: SC2608 510.5 vs SC2702 508.0 (−2.5 CNY, backwardation) | `sc_term_structure_summary.json` | 2026-06-22 |
| SC–Brent basis −2.68 USD/bbl (z = −1.03) | `sc_basis_summary.json` | 2026-06-22 |
| China 2024 imports 11.1 Mb/d, runs 14.2 Mb/d, import dependence ~72% | EIA + `china_crude_supply_demand_summary.json` | 2026-06-22 |
| China refinery CDU util. 57.54% (2026-06-18) | `china_refinery_utilization_summary.json` | 2026-06-23 |
| PX spot 8,800 CNY/t; PX–naphtha ~556 USD/t | `px_spot_summary.json` | 2026-06-23 |
| TA/EG basis, PTA margin 2,772, EG import parity −442 | `ta_eg_basis_summary.json` | 2026-06-23 |
