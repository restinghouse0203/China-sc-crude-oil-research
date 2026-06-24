# BVAR Data Assessment — Reusing Cornell Project for SC + Aromatics

Assessment of variables in `ECON 7300 bayes time series/project/submit` for the Clocktower **Aromatics B** presentation, plus data sources for the adapted specification.

**Project data path:** `/Users/tyau/Desktop/cornell course/spring/ECON 7300 bayes time series/project/submit/data/`

---

## Quick verdict

| Variable | Reuse as-is? | Role in China aromatics BVAR |
|----------|--------------|------------------------------|
| **`d_prod`** (global Δproduction) | **Yes** | Keeps Kilian supply-shock identification; China is import-dependent so global supply still drives marginal barrel |
| **`rea`** (Kilian activity index) | **Yes** (baseline); optional upgrade | Valid global aggregate-demand proxy; consider adding China IP/PMI in pass-through regressions, not necessarily inside 3-var BVAR |
| **`rpo`** (US real import price) | **No — replace with `rpo_sc`** | Use **log real SC** (nominal SC ÷ China CPI or PPI), same transform: `100 × ln(real_price)` |

**Do not use raw SC ticker without deflation** — Kilian `rpo` is a *real* price; mixing nominal SC breaks comparability with IRF literature and your prior results.

---

## Variable-by-variable detail

### 1. `d_prod` — global crude oil production change

| Item | Detail |
|------|--------|
| **Definition** | `1200 × ln(prod_t / prod_{t-1})` — annualized monthly % change in world crude output |
| **Source (your project)** | EIA `INTL.57-1-WORL-TBPD.M` via `INT-Export-04-28-2026_10-53-06.csv` |
| **Sample in repo** | 1987–2025 (`data.csv` in presentation `data/` folder) |
| **Usable?** | **Yes.** China imports crude; global supply shocks remain the correct first equation in Cholesky ordering. |
| **Optional extension** | China refinery runs or crude imports as *exogenous* regressor in TA/EG pass-through — not required inside core 3-var system. |

### 2. `rea` — Kilian real economic activity index

| Item | Detail |
|------|--------|
| **Definition** | % deviation from trend; dry-cargo freight-based global activity proxy |
| **Source (your project)** | `igrea.xlsx` — Federal Reserve Bank of Dallas (**2019-corrected** series) |
| **Sample** | 1973–2025 |
| **Usable?** | **Yes** for replication and global demand shocks. Correlation with China polyester exports is indirect but economically consistent for Kilian identification. |
| **Caveat** | Post-2008 volatility in shipping; China-specific stimulus may not appear immediately in `rea`. State this in the deck. |
| **Upgrade path** | Shock-augmented regression: Kilian shocks → Δ(TA) controlling for **China PPI** or **textile export growth** |

### 3. `rpo` → **`rpo_sc`** (spliced Brent + SC real price)

| Item | Detail |
|------|--------|
| **Definition** | `rpo_sc = 100 × ln(P_t^real)` — same log-real transform as Kilian `rpo`, applied to a Brent/SC spliced nominal price |
| **Usable for China SC study?** | **Yes** — replaces US refiner import `rpo` in the third BVAR equation |
| **Sample** | **1987-05 → 2025-12** (no pre-1987 proxy; aligns with FRED Brent start) |

#### `rpo_sc` formula (deflated)

**Step 1 — Spliced nominal price** \(P_t\) **(USD/bbl)**

| Period | Nominal source | Formula |
|--------|----------------|---------|
| 1987-05 → 2017-12 | FRED `MCOILBRENTEU` | \(P_t = \text{Brent}_t\) |
| 2018-01 → 2018-02 | Brent bridge | \(P_t = \text{Brent}_t\) (SC not listed until Mar 2018) |
| 2018-03 → 2025-12 | INE SC via akshare | \(P_t = \text{SC_t^{CNY}} / \text{CNYUSD}_t\) |

where \(\text{CNYUSD}_t\) is the monthly average of FRED `DEXCHUS`.

**Step 2 — Real price** \(P_t^{real}\) **(deflated)**

| Period | Deflator | Formula |
|--------|----------|---------|
| 1987-05 → 2017-12 | US CPI | \(P_t^{real} = P_t / \text{CPIUS}_t\) |
| 2018-01 → 2025-12 | China CPI | \(P_t^{real} = \text{SC}_t^{CNY} / \text{CPICN}_t\) |

- \(\text{CPIUS}_t\) = FRED `CPIAUCSL` (monthly, forward-filled to sample end)  
- \(\text{CPICN}_t\) = FRED `CHNCPIALLMINMEI` (monthly, forward-filled; US CPI fallback only for bridge months if China CPI lags)

**Step 3 — Log real oil price (BVAR input)**

\[
\text{rpo\_sc}_t = 100 \times \ln\!\left(P_t^{real}\right)
\]

**Do not use raw SC close without deflation** — Kilian `rpo` is a *real* price; nominal SC breaks shock identification.

#### Level shift at 2018 splice

A constant level gap at Jan 2018 (Brent USD vs SC/CNY deflated by China CPI) is expected and is **absorbed by the VAR intercept** — same logic as the CPI base-year offset in your Cornell `rpo` replication.

---

## `oil_price_splice_1973_2025.csv` — build documentation

> **Note:** Filename retained for continuity; **sample starts 1987-05** (no pre-Brent proxy rows).

| Item | Detail |
|------|--------|
| **Script** | `data/build_oil_splice.py` |
| **Output** | `data/oil_price_splice_1973_2025.csv` |
| **Frequency** | Monthly (`MS`) |
| **Rows** | 464 (1987-05 → 2025-12) |

### Build steps

1. **Download Brent** — FRED `MCOILBRENTEU` → `brent_nominal_usd`  
2. **Download SC** — akshare `futures_main_sina("SC0")`, month-end close → `sc_nominal_cny`  
3. **Download FX** — FRED `DEXCHUS`, monthly average → `cny_usd`; compute `sc_nominal_usd = sc_nominal_cny / cny_usd`  
4. **Download CPI** — FRED `CPIAUCSL` → `us_cpi`; FRED `CHNCPIALLMINMEI` → `china_cpi`  
5. **Splice nominal** — Brent through 2017-12; SC USD from 2018-01 (`segment` column: `brent` / `brent_bridge` / `sc`)  
6. **Deflate** — US CPI pre-2018, China CPI post-2018 → `price_spliced_real`  
7. **Compute** `rpo_sc = 100 × ln(price_spliced_real)`

### Output columns

| Column | Description |
|--------|-------------|
| `date` | Month-start timestamp |
| `brent_nominal_usd` | FRED Brent (NaN after 2017-12 in pre-2018 column) |
| `brent_pre2018_usd` | Brent through 2017-12 only |
| `sc_nominal_cny` | INE SC continuous (akshare) |
| `sc_nominal_usd` | SC converted to USD |
| `cny_usd`, `us_cpi`, `china_cpi` | Deflator / FX inputs |
| `price_spliced_nominal_usd` | Combined nominal series |
| `price_real_pre2018`, `price_real_post2018` | Segment-specific real prices |
| `price_spliced_real` | Deflated series fed into `rpo_sc` |
| `rpo_sc` | **BVAR third variable** |
| `segment` | `brent` / `brent_bridge` / `sc` |

**Re-run:** `python3 data/build_oil_splice.py`

---

## `data.csv` — merged BVAR dataset

| Item | Detail |
|------|--------|
| **Script** | `data/build_data_csv.py` |
| **Output** | `data/data.csv` |
| **Columns** | `date`, `d_prod`, `rea`, `rpo` (where `rpo` = `rpo_sc`) |
| **Sample** | 1987-05 → 2025-12 (464 rows) |

### Merge steps

1. Load `data_1973_2007.xlsx` → parse `obs` (`YYYYMMM`) to `date`; keep `dprod` → `d_prod`, `rea`; **truncate to ≥ 1987-05** (through 2007-12).  
2. Load `data_extended_2008_2025.csv` → `d_prod`, `rea` (2008-01 → 2025-12).  
3. Concatenate on `date` (no overlap: xlsx ends 2007-12, extended starts 2008-01).  
4. Inner-join `rpo_sc` from `oil_price_splice_1973_2025.csv` on `date`.  
5. Rename `rpo_sc` → `rpo`; export 4-column CSV.

**Re-run:** `python3 data/build_data_csv.py` (calls `build_oil_splice` internally)

---

## Variable-by-variable detail (original assessment)

### 3 (legacy). `rpo` — log real US refiner acquisition cost (imported)

| Item | Detail |
|------|--------|
| **Definition** | `100 × ln(nominal_oil_price / US_CPI)`; EIA refiner acquisition cost, imported |
| **Source (your project)** | EIA Table 9.1 + `cpi.txt` / FRED `CPIAUCSL` |
| **Usable for China SC study?** | **Not as the price equation** — it measures US landed refiner cost, not INE SC. |
| **Replacement** | **`rpo_sc = 100 × ln(SC_nominal / China_CPI)`** (or China PPI sub-index for chemicals) |

#### Should `rpo` be replaced by SC ticker price?

| Approach | Verdict |
|----------|---------|
| Raw SC close (nominal) | **No** — not comparable to Kilian real price; FX and inflation confound shocks |
| Log SC without deflator | **No** — same issue |
| **Log real SC** (`rpo_sc`) | **Yes — recommended** |
| SC continuous main-contract spliced | **Yes** for monthly average; document roll rule |
| Brent real (`POILBREUSDM`) as substitute | **Acceptable fallback** for 1992–2018 pre-SC; use SC from 2018-03 onward |

**Sample constraint:** SC futures launched **March 2018**. Options:

1. **Full-history BVAR (recommended for deck):** Keep `d_prod`, `rea`, replace `rpo` with **real Brent** 1973–2017 + splice **real SC** 2018–present (note structural break in appendix).  
2. **SC-only subsample:** 2018–2025 only — **~7 years**, too short for BVAR(24) with stable inference; use for auxiliary charts, not main Gibbs run.  
3. **Two-step narrative:** BVAR on full sample with real Brent; separate SC–Brent basis panel for China channel post-2018.

---

## Recommended specification for presentation

### Core BVAR (reuse code, swap price series)

```
Ordering:  d_prod  →  rea  →  rpo_sc
           (supply)   (activity)  (China real crude)
```

**`rpo_sc` construction (implemented):**

1. Splice nominal: Brent (`MCOILBRENTEU`) through 2017-12; SC USD from 2018-01.  
2. Deflate: US CPI pre-2018; China CPI post-2018.  
3. `rpo_sc = 100 × ln(price_spliced_real)` — see formula section above.

### Pass-through to aromatics (outside or augmented BVAR)

Monthly Δlog(TA), Δlog(EG), or Δ(TA–EG) regressed on **lagged structural oil shocks** from BVAR (your Cornell GDP/CPI regression pattern).

Variables to add (not in core 3-var):

| Series | Use |
|--------|-----|
| ZCE TA continuous | PTA price pass-through |
| DCE EG continuous | EG / polyester upstream |
| TA–EG spread | Chain margin |
| PTA operating rate (OilChem) | Fundamental overlay on slides |
| SC–Brent | China basis channel (weekly chart) |

---

## Data sources — BVAR inputs

### From existing project (reuse)

| Series | File / source | URL or path |
|--------|---------------|-------------|
| World crude production | `INT-Export-*.csv` (EIA) | https://www.eia.gov/international/data/world |
| Kilian `rea` | `igrea.xlsx` | https://www.dallasfed.org/research/economists/kilian |
| US `rpo` (reference only) | `Table_9.1_Crude_Oil_Price_Summary.xlsx` + CPI | EIA + https://fred.stlouisfed.org/series/CPIAUCSL |
| Merged extended CSV | `data/data_extended_2008_2025.csv` | Local project `data/` |

### New series for China adaptation

| Series | Source | Link | Notes |
|--------|--------|------|-------|
| **SC futures** (nominal) | INE / Wind / iFinD | https://www.ine.cn/en/market/futures/sc/domestic/ | Monthly avg of daily close; continuous contract |
| **China CPI** | FRED / NBS | https://fred.stlouisfed.org/series/CHNCPIALLMINMEI | For `rpo_sc`; align monthly |
| **China PPI (chem)** | NBS / Wind | https://www.stats.gov.cn/english/ | Alternative deflator; more sector-specific |
| **Brent nominal** | FRED | https://fred.stlouisfed.org/series/POILBREUSDM | Pre-2018 real oil proxy (already in `POILBREUSDM.csv`) |
| **CNY/USD** | FRED | https://fred.stlouisfed.org/series/DEXCHUS | SC FX channel; optional 4th variable later |
| **TA futures** | ZCE / Wind | http://www.czce.com.cn/ | Pass-through regression |
| **EG futures** | DCE / Wind | http://www.dce.com.cn/ | Pass-through regression |
| **PTA operating rate** | 隆众 OilChem | https://www.oilchem.net/ | Weekly → monthly avg for charts |
| **EG port inventory** | 隆众 | https://www.oilchem.net/ | East China ports; inventory slide |

---

## Implementation checklist

- [x] Build Brent + SC splice (`oil_price_splice_1973_2025.csv`, sample from 1987-05)  
- [x] Merge `d_prod`, `rea`, `rpo_sc` → `data/data.csv`  
- [ ] Re-run `gibbs_bvar_niw.py` with `data/data.csv`  
- [ ] Export one IRF figure (supply vs precautionary) for Beamer  
- [ ] Run one shock-augmented regression: shocks → Δ(TA) or Δ(TA–EG)  
- [ ] Document splice level shift in appendix footnote  

---

## Honest limitations (state in presentation)

1. Kilian ordering is **global**; SC has **CNY, storage, and policy** frictions not in the VAR.  
2. **SC history ~7 years** — full BVAR on SC-only sample is underpowered; prefer spliced Brent or global price + SC basis module.  
3. **PX** (key PTA feedstock) is not a futures contract — TA analysis needs spot PX or margin proxies.  
4. Monthly BVAR informs **shock taxonomy and regime**, not weekly entry timing.  
5. Apr 2020 WTI negative episode is irrelevant to SC; validates using SC-specific price series.
