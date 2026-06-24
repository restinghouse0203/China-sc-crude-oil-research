# Anchor Commodities — China Chemical Value Chain

Starter set of **8 commodities** spanning upstream feedstocks → midstream → downstream polymers/fertilizer.  
Prioritized for: China relevance, futures liquidity, cross-chain linkages, and modelability.

---

## Summary Table

| # | Commodity | Chain position | Exchange / code | China relevance | Liquidity | Primary demand drivers |
|---|-----------|----------------|-----------------|-----------------|-----------|------------------------|
| 1 | **Crude oil** | Upstream feedstock | INE **SC** | Import-dependent; sets naphtha/aromatics cost floor | ★★★★★ | Refining, petchem feedstock, macro |
| 2 | **Methanol** | Upstream / C1 platform | ZCE **MA** | Coal-to-chem hub; MTO/MTG feedstock | ★★★★☆ | MTO plants, formaldehyde, acetic acid, fuels blend |
| 3 | **LPG (propane)** | Upstream / PDH feed | DCE **PG** | PDH capacity wave; import arbitrage vs US/Mideast | ★★★★☆ | PDH → propylene → PP; heating |
| 4 | **Ethylene glycol (EG)** | Midstream | DCE **EG** | High import share historically; polyester chain | ★★★★☆ | PET/polyester fiber, bottles, antifreeze |
| 5 | **PTA** | Midstream (aromatics) | ZCE **TA** | World's largest producer; PX-PTA integration | ★★★★★ | Polyester (fiber, bottle chip, film) |
| 6 | **Polypropylene (PP)** | Downstream polymer | DCE **PP** | Olefin derivative; coal & naphtha routes converge | ★★★★★ | Packaging, auto, appliances, woven sacks |
| 7 | **LLDPE** | Downstream polymer | DCE **L** | Ethylene chain; packaging-heavy | ★★★★☆ | Film, packaging, agriculture |
| 8 | **Urea** | Fertilizer / coal-chem | ZCE **UR** | Coal-based capacity; policy-sensitive | ★★★★☆ | Agriculture; industrial (UF resins); export quotas |

---

## Characteristics & Modeling Approaches

| Commodity | Key characteristics | Typical spreads / relative value | Time-series modeling | Cross-section / fundamental |
|-----------|---------------------|----------------------------------|----------------------|----------------------------|
| **Crude (SC)** | Global macro anchor; SC reflects China landed cost + FX; delivery at INE warehouses; strong link to Brent/Dubai spreads | SC–Brent, SC–Dubai, crack spreads (not always listed) | ARIMA/VAR with FX, Brent, inventories; regime-switching around OPEC/geopolitics; GARCH for vol | Cost floor for naphtha route; pass-through elasticity to downstream margins |
| **Methanol (MA)** | **Coal-price linked** in China (unlike global gas-based methanol); MTO demand is key swing factor; seasonal gas-coal switching in NW China | MA–coal, MA–PP (MTO margin proxy), MA–crude (energy) | Seasonal ARIMA; error-correction with coal index & PP; structural break at MTO capacity adds | Plant operating rates by province; inland vs coastal freight; environmental curtailments |
| **LPG (PG)** | PDH feedstock; **import parity** vs FEI/C3 US Gulf; freight-sensitive | PG–propylene (when propylene listed), PG–PP margin, PG–crude | Cointegration with international propane benchmarks + CNY; freight-adjusted parity models | PDH utilization; propane cargo arrivals; winter heating demand |
| **EG (EG)** | Polyester upstream; **import arbitrage** historically important; ethylene cost linkage | EG–PTA (polyester margin), EG–naphtha/ethylene proxy, EG–MA (coal route) | VECM with PTA, crude, FX; inventory-driven mean reversion | Port inventory (华东港口), plant turnarounds, polyester operating rates |
| **PTA (TA)** | Tight link to **PX** (often not futures); massive China capacity; high operating rate sensitivity | TA–PX spread (spot), TA–EG (polyester chain), TA–crude | Pair with EG in VECM; margin model: PTA price = f(PX, utilisation); inventory cycles | PX-PTA integrated margins; polyester demand (textile exports); plant maintenance clusters |
| **PP** | Convergence of **naphtha steam cracker, PDH, and MTO** routes; most liquid olefin polymer future | PP–MA (MTO margin), PP–PG (PDH margin), PP–L (polyolefin spread) | Spread mean-reversion (PP-MA); VAR with crude, MA, PG; capacity cycle overlays | Operating rates; downstream orders (塑编, 注塑); export netbacks |
| **LLDPE (L)** | Ethylene-based; packaging demand; slightly less China-specific than PP but good macro demand signal | L–PP (product spread), L–EG (cost linkage) | Similar to PP; co-movement with crude/ethylene proxies | Film demand; import vs domestic supply; seasonal packaging |
| **Urea (UR)** | **Coal + agriculture policy**; export window regulated; gas vs coal plants | UR–coal, UR–international FOB (export arb) | Seasonal (planting/fertilizer season); policy dummy variables; coal pass-through regression | Operating rates; export quota; India/agri demand; energy dual-control |

---

## Value Chain Placement (simplified)

```
Crude (SC) ──┬── Naphtha route ──► Ethylene/Propylene ──► PP / LLDPE / EG
             │
Coal ────────┼── Methanol (MA) ──► MTO ──► PP / (olefins)
             │
             └── Urea (UR)

LPG (PG) ──► PDH ──► Propylene ──► PP

PX (spot) ──► PTA (TA) ──► EG (EG) ──► Polyester (fiber / bottles)
```

---

## Suggested Research Priority (pick 2–3 for thesis depth)

| Priority | Combo | Why |
|----------|-------|-----|
| **A (coal-chem)** | MA + PP + coal index | Most **China-specific** story; MTO margin trades |
| **B (aromatics)** | SC + TA + EG | Polyester chain; export & textile demand |
| **C (PDH)** | PG + PP | Import propane arb + capacity cycle |
| **D (policy)** | UR + coal | Agriculture + energy policy lens |

---

## Data Sources (China)

| Data type | Sources |
|-----------|---------|
| Futures prices, OI, volume | Wind, iFinD, exchange daily bulletins |
| Spot / factory prices | 百川盈孚, 隆众资讯, SCI (CCF) |
| Inventory | 隆众 (EG, PP, TA), exchange warehouse warrants |
| Operating rates / capacity | 隆众, company reports, MIIT |
| Coal / energy | ZCE thermal coal (ZC), NDRC benchmarks |
| Import parity | Customs, Bloomberg, manual arb spreadsheets |

---

## Modeling Toolkit (quick reference)

| Method | Use case |
|--------|----------|
| **Spread mean-reversion** | PP–MA, TA–EG, PG–PP; test with ADF/Engle-Granger or Johansen |
| **VAR / VECM** | Multi-commodity chain (SC, TA, EG); impulse response to crude shock |
| **Seasonal decomposition (STL)** | Urea (planting), methanol (winter gas curtailment) |
| **Regime switching (Markov)** | Capacity expansion vs consolidation phases |
| **GARCH / vol** | Position sizing; pre-event vol (policy, OPEC) |
| **Error correction (ECM)** | Slow fundamentals (capacity) vs fast futures |
| **Scenario matrix** | Bull/base/bear on crude × operating rate × policy |

*Contract codes and liquidity as of common practice; verify current contract specs on SHFE/DCE/ZCE before trading references in the deck.*
