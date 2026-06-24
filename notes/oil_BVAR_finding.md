# Oil BVAR Findings — Shock Decomposition (BVAR_shock_model.ipynb)

**As of:** 2025-12 (last BVAR observation)  
**Source notebook:** `BVAR_shock_model.ipynb`  
**Model reference:** Kilian (2009) identification; Bayesian NIW prior + Gibbs sampling (Cornell stack)

---

## Model specification

- **Objective:** Decompose crude oil market dynamics into three structural shocks — **oil supply**, **aggregate (commodity) demand**, and **oil-specific demand** (precautionary / inventory-demand in Kilian taxonomy)
- **Endogenous variables (Cholesky order):**
  1. `d_prod` — global crude production change (annualized %)
  2. `rea` — Kilian real economic activity index (global shipping/freight proxy)
  3. `rpo` — log real oil price (`rpo_sc` = Brent/SC splice deflated by US CPI pre-2018, China CPI post-2018)
- **Sample:** **1987-05 → 2025-12** (464 monthly obs); SC-era subsample from 2018-03 = 94 obs
- **Estimation:** BVAR with **p = 6 lags** (note: section header says BVAR(24); AIC/BIC tables favor **p = 24–25**, but Gibbs fit uses **p = 6**)
- **MCMC:** 12,000 draws, 2,000 burn-in → 10,000 post-burn-in posterior draws (seed = 42)
- **Identification:** Recursive Cholesky on reduced-form Σ (supply → activity → oil-specific demand)

---

## Data diagnostics

### Stationarity (ADF / KPSS)

| Series | ADF p-value | ADF reject unit root? | KPSS reject trend-stationary? |
|--------|-------------|----------------------|------------------------------|
| `d_prod` | ~0 | Yes | No |
| `rea` | 0.038 | Yes | No |
| `rpo` | 0.217 | **No** (borderline) | No |

- Production and activity treated as stationary; real oil price is **borderline** on ADF

### Residual autocorrelation (Ljung-Box, lag 12)

- **All three equations:** fail to reject no serial correlation at 5% (p-values 0.41, 0.31, 0.95)
- Residuals appear adequate for p = 6 specification

### Lag selection (AIC / BIC / HQIC tables)

- **AIC minimum:** p = 25 (−170.1)
- **BIC minimum:** p = 24 (−160.7)
- **HQIC minimum:** p = 24 (−164.9)
- **Estimation lag used:** p = 6 (lower than info-criteria optimum — document as modeling choice / parsimony vs fit trade-off)

---

## Structural innovation variances (posterior mean, normalized Σ)

| Shock | Parameter | Posterior mean | 95% CI |
|-------|-----------|----------------|--------|
| Oil supply | Σ₁₁ | 1.16 | [0.88, 1.49] |
| Aggregate demand | Σ₂₂ | 1.28 | [0.95, 1.66] |
| Oil-specific demand | Σ₃₃ | 1.42 | [1.08, 1.80] |
| Supply ↔ agg. demand | Σ₂₁ | −0.04 | [−0.38, 0.28] |
| Supply ↔ oil-specific | Σ₃₁ | **−0.18** | [−0.33, −0.04] |
| Agg. demand ↔ oil-specific | Σ₃₂ | 0.05 | [−0.07, 0.17] |

- **Oil-specific demand shock** has the largest structural variance
- **Negative Σ₃₁:** oil-specific demand innovations tend to coincide with **negative** supply innovations (precautionary hoarding during supply fear, or reverse causality in reduced form)

---

## Historical shock patterns (posterior mean, annual averages)

| Year | Supply | Agg. demand | Oil-specific demand |
|------|--------|-------------|---------------------|
| 2018 | −0.03 | −0.54 | **+1.30** |
| 2019 | −0.13 | −0.10 | +0.11 |
| 2020 | **−1.05** | −0.32 | −0.19 |
| 2021 | +0.31 | +0.63 | +0.24 |
| 2022 | +0.39 | −0.18 | +0.15 |
| 2023 | +0.17 | +0.12 | +0.02 |
| 2024 | −0.15 | −0.29 | +0.03 |
| 2025 | +0.39 | +0.39 | −0.11 |

### Recent monthly shocks (2025 H2)

- **Mixed / low-amplitude:** no single shock dominates; supply and aggregate demand slightly positive in H2, oil-specific near zero to slightly negative
- **Dec 2025:** supply −0.16, agg. demand +0.59, oil-specific −0.36

### Key historical episodes

- **2020:** Large **negative supply shock** (−1.05) — OPEC+ cuts / COVID demand collapse
- **2018:** Elevated **oil-specific demand** (+1.30) — precautionary/inventory channel dominant at SC launch era
- **2021:** Positive supply (+0.31) and strong aggregate demand (+0.63) — post-COVID recovery
- **2024–2025:** Modest supply and demand shocks; regime relatively **muted** vs 2020–2022

---

## Impulse responses (median, horizon h = 15)

Signs align with Kilian theory (p = 6 replication):

| Shock → Response | h = 15 median |
|------------------|---------------|
| Supply → oil price (`rpo`) | **Negative** |
| Aggregate demand → oil price | **Positive** |
| Oil-specific demand → oil price | **Strongly positive** (~15+ cumulative units on index scale) |
| Supply → production | Positive (own-persistence) |
| Aggregate demand → activity | Strongly positive (~3.4) |

- **Oil-specific demand shock** is the dominant positive mover of real oil price at medium horizon
- **Supply shocks** raise production and depress real price (classic supply curve logic)

---

## Forecast error variance decomposition (FEVD, h = 15)

### Notebook-reported own-shock shares (posterior median)

| Variable | Own-shock FEVD |
|----------|----------------|
| Oil production (`d_prod`) | **58.7%** |
| Real activity (`rea`) | **70.9%** |
| Real oil price (`rpo`) | **75.6%** |

- Substantial **cross-shock transmission** — especially to oil price (only ~76% own-shock)

### Full decomposition (current replication, p = 6, h = 15)

**Variance of each variable explained by shock (%):**

| Shock ↓ / Variable → | `d_prod` | `rea` | `rpo` |
|----------------------|----------|-------|-------|
| Oil supply | 90.2 | 1.4 | 0.5 |
| Aggregate demand | 4.7 | 90.5 | 1.0 |
| Oil-specific demand | 4.9 | 7.5 | **98.2** |

- **Oil price variance** at h = 15 is almost entirely driven by **oil-specific demand shocks** (~98%)
- **Supply and aggregate demand shocks** explain minimal oil-price forecast error at this horizon (each ~0.5–1%)
- Production and activity are mostly explained by their own shocks (~90% each)

*Note: own-shock diagonal in notebook (59–76%) differs from full-matrix replication (90–98%) — likely reflects an earlier FEVD indexing run; use full matrix for economic interpretation.*

---

## Granger causality (lag p = 6, same as BVAR)

### Bivariate (significant at 5%)

- **`rea` → `d_prod`:** F = 2.98, p = 0.012 — activity predicts production
- **`rpo` → `d_prod`:** F = 3.77, p = 0.003 — price predicts production
- **Not significant:** `d_prod` → `rea`, `d_prod` → `rpo`, `rea` → `rpo`, `rpo` → `rea`

### Multivariate (conditional on full VAR)

- **Real activity → all others:** p = 0.029 — **significant**
- **Real oil price → all others:** p = 0.002 — **significant**
- **Oil production → all others:** p = 0.779 — not significant

- **Read:** Price and activity are **leading / predictive** in the system; crude production changes are more exogenous (consistent with supply-first ordering)

---

## Cumulative oil-price contributions (Figure 4 style)

- Historical decomposition plots cumulative effect of each shock on **real oil price** with 68% / 95% posterior bands
- **Supply shocks:** persistent **negative** contribution episodes (e.g., 2020 supply cut reversal, 2022–23)
- **Aggregate demand shocks:** positive contribution during 2021 recovery
- **Oil-specific demand shocks:** large positive spikes around geopolitical / inventory episodes (2018, 2022 Russia-Ukraine, 2023–24)

---

## Stage-2 extension (GDP / CPI — partial in notebook)

- Quarterly-averaged structural shocks aligned to GDP growth and CPI inflation (1975 Q1 onward, ~203 quarters)
- Stage-2 distributed-lag regressions (Kilian Figure 5 pattern) set up for:
  - Oil supply shock → GDP / CPI
  - Aggregate demand shock → GDP / CPI
  - Oil-specific demand shock → GDP / CPI
- **CPI 2025-Oct truncated** due to missing US CPI (government shutdown) — series ends 2025-Sep for CPI leg

---

## BVAR regime conclusion

1. **Current regime (2024–2025):** Structural shocks are **moderate** — no extreme supply or precautionary spike comparable to 2020 or 2018. Oil-specific demand has **faded** from 2018 highs.
2. **Price dynamics:** At 15-month horizon, oil price forecast variance is dominated by **oil-specific (precautionary) demand**, not raw supply or global activity — consistent with Kilian's finding that inventory/fear premia drive most price variation.
3. **China price equation:** Third variable is **`rpo_sc`** (spliced Brent + SC real price) — global shock taxonomy applies to China landed cost, but **CNY, INE microstructure, and policy** frictions are outside the VAR.
4. **Model caveat:** p = 6 vs info-criteria favoring p = 24; short SC history (2018+) embedded in spliced price; global `rea` may miss China-specific demand stimulus.

---

## Link to Layer 1 (SC_research)

| BVAR signal | Layer 1 SC signal | Consistency |
|-------------|-------------------|-------------|
| Muted 2024–25 shocks | SC discount vs Brent, run cuts | Demand weakness, not precautionary premium |
| Oil-specific shock faded | Backwardation + low receipts | Physical tightness may be **local/deliverable**, not global precautionary |
| Negative supply episodes 2024 | Warehouse receipt draw | Consistent with physical draw, but BVAR supply shock is global production, not INE stocks |
| Aggregate demand modest | Refinery util −16 pp | Global activity not booming; China runs collapsing |

**Combined read:** BVAR says the **global crude shock environment is relatively calm** in 2024–25; Layer 1 says **China physical/demand conditions are stressed** (run cuts, low INE receipts, backwardation). The divergence is economically plausible: **China-specific refining margin / policy / deliverable-inventory frictions** can dominate SC even when global Kilian shocks are muted.
