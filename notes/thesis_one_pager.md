# Thesis One-Pager — Aromatics B (SC + TA + EG)

**Phase 1 output** | Anchor combo **B (aromatics)** | Model: **BVAR centered on SC**  
**Audience:** Investment team (FoF / allocator) | **Deck language:** English (Beamer)

---

## One-sentence thesis

**Structural crude-oil shocks (supply vs aggregate demand vs precautionary) transmit into China’s aromatics chain unevenly: SC captures the import/FX landed-cost channel, while TA and EG reflect polyester margin compression or expansion depending on whether the shock is cost-push (supply) or demand-driven (global activity)—allocators should monitor shock type, not just oil direction.**

---

## Scope

### In scope (7-slide deck)

| Layer | Coverage |
|-------|----------|
| **Value chain** | Crude (SC) → naphtha/PX (spot) → PTA (TA) → EG (EG) → polyester (fiber, bottle chip, film) |
| **China specifics** | Import-dependent crude; world’s largest PTA capacity; textile/export demand linkage; coastal integrated complexes |
| **Futures map** | INE **SC**, ZCE **TA**, DCE **EG** — basis, term structure, key spreads (SC–Brent, TA–EG) |
| **Analytics** | Kilian-type **3-var BVAR** on global crude drivers; shock-augmented pass-through to TA/EG margins |
| **Investment framing** | 2–3 **scenario-based, monitorable exposures** (not prop trade tickets) |

### Out of scope (explicitly)

- Coal-to-chem / MTO route (methanol, PP) — China-specific but different feedstock story  
- Olefins / PDH (PG, PP, L) — save for Q&A unless time permits  
- Full portfolio optimization (mean-variance weights)  
- High-frequency SC day-trading model — monthly BVAR informs **regime**, weekly futures data informs **timing slide only**

---

## Anchor commodities

| # | Commodity | Contract | Role in narrative |
|---|-----------|----------|-------------------|
| 1 | **Crude oil** | INE **SC** | Upstream cost anchor; BVAR price equation; import/FX channel |
| 2 | **PTA** | ZCE **TA** | Midstream aromatics; China capacity & operating rates; PX–PTA margin (PX spot) |
| 3 | **Ethylene glycol** | DCE **EG** | Polyester upstream; import arb history; TA–EG chain margin |

**Chain sketch:**

```
SC (crude) ──► Naphtha / PX (spot) ──► TA (PTA) ──► EG ──► Polyester demand
                      │                      │
                      └── cost floor ─────────┴── margin splits (TA–EG, PX–TA)
```

---

## Analytical framework (allocator lens)

```
Global crude shocks (BVAR)  →  China landed cost (SC, SC–Brent)  →  Aromatics margins (TA, EG, TA–EG)
         │                              │                                      │
    supply / demand /              FX + import parity                    capacity + polyester
    precautionary                  + INE microstructure                   operating rates
```

**Driver tree (slide 3):**

- **Supply:** OPEC+ output, global Δprod, geopolitical disruption  
- **Demand:** Global activity (Kilian `rea` or China IP/PMI), textile & packaging orders, exports  
- **Cost:** Crude/naphtha/PX pass-through, refinery runs, energy policy  
- **China idiosyncrasy:** Capacity additions (PTA), environmental inspections, port inventory (EG)

**Cycle positioning (to validate in Phase 2–3):** Document evidence for expansion / peak / contraction / trough in PTA–polyester with dated data (operating rates, margin spreads, inventory days).

---

## Investment views (draft — refine after data pass)

Use template: *direction or RV → fundamental rationale → futures expression → catalyst → falsifier → KPIs → horizon.*

### View 1 — Shock-type dependent pass-through (core)

| Field | Content |
|-------|---------|
| **View** | Relative value / regime: **cost-push supply shocks** widen TA–EG margin stress differently than **precautionary-demand** spikes |
| **Rationale** | Kilian identification: supply shock ≠ demand boom; polyester margins do not move 1:1 with SC |
| **Expression** | Monitor **SC** direction + **TA–EG** spread; hedge leg optional SC vs TA |
| **Catalyst** | FEVD / shock decomposition shows rising supply or precautionary share |
| **Falsifier** | PX–PTA integration margins absorb crude; TA and EG decouple from SC for >2 quarters |
| **KPIs** | BVAR shock shares, SC–Brent basis, PTA operating rate, 华东 EG port inventory |
| **Horizon** | Months (cycle) |

### View 2 — SC–Brent / import-parity dislocation (China channel)

| Field | Content |
|-------|---------|
| **View** | Directional on **SC–Brent** (or SC–Dubai) when basis diverges from freight + FX fair value |
| **Rationale** | China import dependence; SC reflects landed cost not just global benchmark |
| **Expression** | SC outright or SC–offshore spread |
| **Catalyst** | Inventory builds at INE delivery ports; RMB move; import quota/policy shift |
| **Falsifier** | Basis mean-reverts within normal arb band without margin impact on TA |
| **KPIs** | SC–Brent, CNY/USD, crude import arrivals, INE warehouse warrants |
| **Horizon** | Weeks–months |

### View 3 — Polyester chain margin (TA–EG) vs capacity (optional third)

| Field | Content |
|-------|---------|
| **View** | Relative value on **TA–EG** when operating rates and inventory imply margin mean-reversion |
| **Rationale** | Massive PTA capacity; EG import/share swings; downstream textile demand |
| **Expression** | TA–EG spread (futures or spot-proxy) |
| **Catalyst** | PTA turnaround cluster; polyester operating rate rebound |
| **Falsifier** | New PTA capacity starts on schedule + weak textile exports prolong oversupply |
| **KPIs** | PTA/EG operating rates, port inventory, textile export orders, TA–EG z-score |
| **Horizon** | Cycle (quarters) |

---

## Three falsifiers (thesis-level)

1. **Capacity delay or faster-than-expected PTA/EG startups** — persistent margin compression despite crude shocks (supply story dominates chain).  
2. **China demand stimulus / textile export surge** — EG and TA outperform crude-cost logic for several months (demand overrides cost-push).  
3. **Crude regime change** — e.g. sustained supply glut or geopolitical premium where **shock type** flips (BVAR FEVD shifts from precautionary to supply); prior pass-through estimates unstable.

---

## BVAR module (1 slide + appendix)

| Element | Specification |
|---------|----------------|
| **Model** | BVAR(24), NIW prior, Gibbs sampler (reuse Cornell stack) |
| **Variables** | `d_prod` (global), `rea` (Kilian activity), `rpo` → **`rpo_sc`** (log real SC) |
| **Identification** | Recursive Cholesky: supply → activity → price (Kilian ordering) |
| **Deck exhibit** | One IRF panel (supply vs precautionary on real SC) + plain-language interpretation |
| **Link to chain** | Shock-augmented regression: structural shocks → Δ(TA), Δ(EG), or Δ(TA–EG proxy) |
| **Honest limits** | Monthly, global identification; SC history from 2018; not a tick model |

See `notes/bvar_data_sources.md` for variable reuse vs replacement.

---

## Monitoring KPIs (weekly / monthly)

| KPI | Frequency | Links to |
|-----|-----------|----------|
| BVAR shock shares / FEVD | Monthly | SC regime |
| SC–Brent (or Dubai) basis | Daily/weekly | China import channel |
| PTA operating rate | Weekly | TA margin |
| EG port inventory (华东) | Weekly | EG mean-reversion |
| TA–EG spread | Daily | Chain margin view |
| Polyester operating rate / textile exports | Monthly | Downstream demand |
| CNY/USD | Daily | SC FX channel |

---

## Research priorities (Phase 2 onward)

1. Finalize value chain diagram with China hubs (Zhejiang, Jiangsu coastal complexes).  
2. Pull dated series: SC, TA, EG continuous futures; PTA/EG operating rates; one margin chart.  
3. Re-run BVAR with `rpo_sc`; one pass-through regression to TA or TA–EG.  
4. Lock **2 views** for slide 6 (View 3 optional).  
5. Build Beamer deck per `PLAN.md` slide architecture.

---

## Sources

- Industry & chain: `notes/value_chain_sources.md`  
- BVAR data: `notes/bvar_data_sources.md`  
- Anchor commodity reference: `research/anchor_commodities.md`  
- BVAR crosswalk: `research/bvar_applicability.md`
