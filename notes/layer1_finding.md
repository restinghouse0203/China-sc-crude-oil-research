# Layer 1 Findings — INE SC / China Crude (SC_research.ipynb)

**As of:** 2026-06-23  
**Source notebook:** `SC_research.ipynb`  
**Data outputs:** `data/sc_*_summary.json`, `data/china_*_summary.json`

---

## 1. SC term structure (INE futures curve)

- **Front contract:** SC2608 (Aug 2026), settle **510.5 CNY/bbl**, OI **50,948**
- **~6M contract:** SC2702 (Feb 2027), settle **508.0 CNY/bbl**
- **Front → 6M spread:** **−2.5 CNY/bbl** (−0.49% of front)
- **Annualized roll yield:** **−0.98%** (negative carry)
- **Regime label:** **backwardation** (front < deferred)
- **Read:** Near-term SC is priced above deferred months → tight near-term deliverable supply / limited storage incentive at INE bonded sites (vs contango which would reward storage)
- **Source:** akshare INE daily futures (`sc_term_structure_summary.json`)

---

## 2. SC basis vs offshore benchmarks

- **SC (main continuous):** 491.4 CNY/bbl ≈ **72.6 USD/bbl** (CNY/USD 6.7686)
- **Brent proxy:** **77.54 USD/bbl**
- **Dubai proxy:** **102.28 USD/bbl** (FRED monthly POILDUBUSDM, forward-filled)
- **Basis SC − Brent:** **−4.94 USD/bbl** (−6.37%)
- **Basis SC − Dubai:** **−29.68 USD/bbl**
- **3y z-scores:** Brent basis **−1.70σ**; Dubai basis **−4.73σ** (vs 3y mean +0.75 / −1.49 USD)
- **Read:** China crude is **cheap vs Brent** and especially vs Dubai on a USD landed-cost basis — domestic/import-parity discount, not a premium
- **Caveat:** Dubai series is monthly FRED fallback, not live Wind EDB daily
- **Source:** `sc_basis_summary.json` (756-day lookback)

---

## 3. China crude balance (annual, EIA)

- **Latest year:** 2024
- **Crude imports:** **11.1 mb/d** (YoY **−1.77%**)
- **Domestic production:** **4.3 mb/d**
- **Refinery runs:** **14.2 mb/d** (YoY **−4.05%**)
- **Import dependence:** **72%**
- **Cycle label:** *"imports declining slower than runs (inventory/build risk)"* — runs falling faster than import volumes
- **Read:** Structural import reliance remains high; 2024 shows **demand-side softness** (runs down) with imports only marginally lower → potential stock build / slower crude draw at national level
- **Source:** EIA International API (`china_crude_supply_demand_summary.json`)

---

## 4. Refinery CDU utilization (weekly, OilChem)

- **Week ending:** 2026-06-18
- **All refineries:** **57.54%** (WoW **−0.89 pp**)
- **Majors (国有):** **67.23%**
- **Independents / teapots (地炼):** **43.47%**
- **Megaprojects (大炼化):** **59.23%**
- **vs pre-conflict baseline** (week of 2026-02-26, 73.38%): **−15.84 pp**
- **Cycle label:** *"sharp run-cut phase (utilization well below pre-shock baseline)"*
- **Read:** Broad run cuts across the system; teapots most stressed; utilization collapsed after Feb 2026 baseline (Middle East supply shock / margin squeeze narrative in market press)
- **Source:** OilChem curated CSV (`china_refinery_utilization_summary.json`)

---

## 5. INE SC warehouse receipts (deliverable physical)

- **Latest level:** **2.96M bbl** (2026-06-23)
- **Daily change:** **0** for 10+ sessions (flat since early June)
- **20-day change:** **−550k bbl**
- **Full-sample z-score:** **−1.18σ** (mean 5.33M, std 2.02M; range 2.56M–10.65M)
- **Position:** Near **sample floor** (~16% above historical min)
- **Linear trend (May 2024–Jun 2026):** **−10,394 bbl/day** (~**−2.6M bbl/year**), R² = 0.56
- **AR(1) on levels:** φ = 0.979, half-life **~32 days**, long-run mean ~5.33M bbl (AIC favors AR over linear trend)
- **Read:** Multi-year **draw** on INE deliverable inventory from ~10M to ~3M bbl; now **plateauing at lows** → tight deliverable physical, but marginal draw has paused
- **Source:** akshare SHFE/INE receipt API (`sc_warehouse_receipts_summary.json`)

---

## Layer 1 story (synthesis)

China's INE crude market as of late June 2026 sits in a **physically tight near-term, financially discounted** configuration:

| Dimension | Signal | Direction |
|-----------|--------|-----------|
| Term structure | Backwardation (−2.5 CNY/bbl front–6M) | Near-term tight |
| Basis | SC −4.9 USD/bbl vs Brent (−1.7σ) | China crude cheap vs offshore |
| Warehouse receipts | 2.96M bbl, near lows, flat | Deliverable supply thin |
| Refinery runs | 57.5% util (−16 pp vs Feb) | Sharp demand-side contraction |
| National balance | Runs −4% YoY, imports −1.8% YoY | Runs falling faster than imports |

**Coherent narrative:** Global/supply-shock stress (refinery run cuts, teapot distress) coincides with **drawn-down INE deliverable stocks** and **backwardation**, yet SC trades at a **discount to Brent** — suggesting the China discount is driven by **weak domestic refining demand and margin compression**, not by abundant local physical supply. Low warehouse receipts support near-term tightness for deliverable SC, but flat receipts and collapsing utilization imply the **binding constraint may be demand (runs), not storage build**.

**Tension to monitor:** Backwardation + low receipts = physical tightness; run cuts + negative basis = weak marginal demand. Reconciliation likely requires **less crude parked in bonded warehouses** (receipts drawn for delivery or not replenished) while **refiners process less** overall.

**Next layer (not in this notebook):** Link these SC signals to aromatics pass-through (TA, EG, PX margins) and BVAR shock regime.
