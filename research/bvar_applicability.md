# BVAR Project → China Chemical / Crude Oil Presentation

Crosswalk from **Cornell ECON 7300 BVAR oil project** (Kilian 2009 extension) to this China SC / aromatics presentation.

---

## Your prior project (recap)

| Element | Specification |
|---------|---------------|
| Model | BVAR(24), NIW prior, Gibbs sampler (12k draws) |
| Variables | Δprod (global oil output), rea (Kilian freight/activity), rpo (log real US import price) |
| Identification | Recursive Cholesky: supply → aggregate demand → precautionary demand |
| Outputs | IRFs, FEVD, cumulative shock decomposition, shock-augmented GDP/CPI regressions |
| Key finding | Not all oil price moves are alike — precautionary demand dominated pre-2008 price surges |

Repo: https://github.com/restinghouse0203/Bayesian-Time-Series-Oil-Market-Forecast/

---

## Can it apply to crude oil in *this* project?

**Yes — strongly, with adaptation.** Crude is the upstream anchor for China's naphtha/aromatics route; your project gives a **structural shock framework** that is more defensible in a 30–45 min allocator interview than a simple "oil up → chemicals up" chart.

### What transfers directly

| Prior project | This presentation use |
|---------------|----------------------------|
| Shock decomposition (supply / agg demand / precautionary) | Explain **why** SC moved — e.g. 2022 rally ≠ 2008 demand boom |
| IRFs with 68%/95% credible bands | Scenario fan charts for pass-through to TA/EG/PP margins |
| FEVD | "What drives SC variance over 6–15 months?" — allocator risk budgeting |
| BVAR posterior uncertainty | Honest confidence language vs point forecasts |
| Existing Python stack (`gibbs_bvar_niw.py`, IRF utilities) | Fast re-estimation on extended sample for one deck exhibit |

### What must change (global Kilian → China chemical lens)

| Kilian / your baseline | China presentation adaptation |
|--------------------------|--------------------------------|
| rpo = US real import price | **SC** (or SC deflated by China PPI/CPI); optionally SC–Brent spread as second price |
| Δprod = global production | Keep global Δprod **or** add China crude **imports**/refinery runs |
| rea = global freight index | China **industrial production / PMI / export orders** OR keep rea as global demand proxy |
| Macro regressions: US GDP, CPI | **China PPI (chem sector), PP/PTA margins, petchem operating rates** |
| Monthly 1973–2025 | Same frequency works for macro narrative; add **weekly** SC–spread for futures timing slide |
| US-dollar framing | **CNY/USD** as exogenous or extra equation — SC has FX component |

### Recommended "China chemical" crude module (1 slide + appendix)

**Minimal adaptation (1–2 days):**
- Re-run existing 3-variable BVAR; replace rpo with log real **Brent or SC** (deflated).
- Present Kilian shocks as **global crude drivers**; map to China via SC–Brent basis + import dependence narrative.

**Stronger adaptation (3–5 days):**
- 4-variable BVAR: (Δprod, China_IP or PMI, log real SC, **SC–Brent spread**).
- Shock-augmented regression: structural oil shocks → **Δ(PP–naphtha margin)** or **Δ(TA)** with distributed lags.
- One IRF panel: precautionary demand shock → SC → implied PTA cost pressure (qualitative + one regression).

### Caveats to state honestly in the presentation

- Kilian identification is **global** and **monthly** — not a high-frequency SC trading model.
- Post-2008 / COVID structural change (you already documented in the report) applies to China too.
- SC has **policy/market microstructure** (margin requirements, storage, INE vs offshore) that VAR omits.
- Apr 2020 negative WTI vs SC divergence — use SC-specific series, not WTI.

---

## Can the experience apply to other China commodities?

**Yes — methodology transfers; specification must be commodity-specific.**

### Transferability matrix

| Commodity | BVAR / Bayesian TS fit | Suggested specification | Priority for your deck |
|-----------|------------------------|-------------------------|------------------------|
| **Crude (SC)** | ★★★★★ Direct extension of your project | Kilian-type 3–4 var BVAR; shocks → downstream margins | **Primary** — lead with this |
| **PP** | ★★★★☆ | BVAR(SC, MA, PG, PP) or spread ECM; pass-through from oil shocks | **High** — chain convergence |
| **Methanol (MA)** | ★★★★☆ | BVAR(coal price, MA, PP) — China-specific supply ordering | **High** — coal route story |
| **PTA (TA)** | ★★★☆☆ | VECM/BVAR with EG, crude proxy; PX often spot-only | Medium — pair with EG |
| **EG** | ★★★☆☆ | VECM(TA, EG, SC); inventory as exogenous | Medium |
| **LPG (PG)** | ★★★☆☆ | BVAR with FEI/US C3, PG, PP — import parity identification fragile | Medium — PDH narrative |
| **LLDPE (L)** | ★★★☆☆ | Similar to PP; often redundant if PP already in system | Low unless olefin focus |
| **Urea (UR)** | ★★☆☆☆ | Seasonal Bayesian DL + coal pass-through > BVAR; policy dummies critical | Low for BVAR; high for regression |

### What transfers across *all* commodities

1. **Shock taxonomy mindset** — decompose moves into supply vs demand vs "fear" (inventory, policy, arb).
2. **Bayesian uncertainty** — credible intervals on IRFs, spreads, margin forecasts (allocator-friendly).
3. **Distributed-lag pass-through** — your GDP/CPI regressions → **margin / spread regressions** on structural shocks.
4. **FEVD** — "what fraction of PP variance is crude vs coal vs own shock?"
5. **TVP-BVAR** (you have `kilian_07_tvp_bvar_niw.ipynb`) — capacity cycles, pre/post 2020 regimes.
6. **MCMC workflow** — same code pattern; swap data matrix and identification story.

### What does *not* transfer cleanly

| Issue | Commodities affected |
|-------|---------------------|
| No clear recursive ordering economics | TA–PX (PX not futures), some policy-driven windows (UR exports) |
| Dominant **seasonality** | UR, MA (winter gas curtailment) — need seasonal BVAR or STL first |
| **High-frequency** futures timing | All — monthly BVAR informs regime, not day-trade entry |
| **China-only idiosyncrasy** | MA (coal), UR (export quota) — need domestic variables not in Kilian |
| Thin history / structural breaks | PG (PDH wave), new INE contracts |

---

## Presentation talking points

1. **"I don't treat oil as a single factor."** — Three shocks have different implications for naphtha margins and hedge ratios.
2. **"Bayesian framework quantifies uncertainty for risk reporting."** — Credible bands on pass-through, not just point IRFs.
3. **"Same toolchain extends down the chain."** — Oil shocks → PP/PTA margins via augmented regressions; MA–coal block for coal-chem.
4. **"I know the limits."** — Monthly structural model complements, not replaces, inventory/basis/operating-rate monitoring.

---

## Suggested deck integration (don't overfit the econometrics)

| Slide | Econometrics content |
|-------|---------------------|
| Crude drivers | 1 IRF panel (precautionary vs supply) + plain-language interpretation |
| Futures linkage | SC–Brent basis time series; optional FEVD bar chart |
| Investment view | Scenario table informed by shock history (2022, 2020, 2008) |
| Appendix | BVAR spec, prior, identification — for quant PM questions |

**Rule:** One clean exhibit beats re-running full Kilian replication live in a 35-min slot.

---

## Practical next steps

- [ ] Download SC continuous futures + China PPI chem sub-index (Wind/iFinD)
- [ ] Re-run 3-var BVAR with SC replacing rpo (weekend task)
- [ ] One shock-augmented regression: quarterly oil shocks → monthly Δ(PP spot − MA×3) proxy
- [ ] Optional: 4-var with ZC (thermal coal) for MA block — second exhibit
