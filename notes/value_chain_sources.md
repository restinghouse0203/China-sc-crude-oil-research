# Value Chain Research Sources — China Aromatics (SC → TA → EG)

Curated links with short summaries for Phase 2–3 research. Prioritize **dated, verifiable** data for deck charts.

---

## Exchanges & contract specifications (futures linkage)

| Source | Link | Summary |
|--------|------|---------|
| **INE / SHFE — SC crude oil** | https://www.ine.cn/en/products/futures/sc/ | Official SC contract specs: medium-sour crude benchmark, CNY pricing, delivery at INE warehouses, margin and position rules. Start here for SC microstructure slide. |
| **ZCE — PTA (TA)** | http://www.czce.com.cn/en/DFSStaticFiles/Future/en/ENFutureData.htm | PTA futures contract details on Zhengzhou Commodity Exchange; verify current lot size, delivery brands, and trading hours. |
| **DCE — Ethylene glycol (EG)** | http://www.dce.com.cn/dceen/ | Dalian Commodity Exchange EG contract specs; link to English market data and delivery rules. |
| **INE market data** | https://www.ine.cn/en/market/futures/sc/domestic/ | Daily SC prices, volume, open interest — useful if Wind/iFinD unavailable. |

---

## Policy & industry regulation (China context)

| Source | Link | Summary |
|--------|------|---------|
| **MIIT (Ministry of Industry and IT)** | https://www.miit.gov.cn/ | Capacity guidance, chemical park regulation, industry bulletins. Search 石化 / 化工 for petrochemical policy. |
| **NDRC** | https://www.ndrc.gov.cn/ | Energy pricing, dual-control, major project approvals affecting refinery and petchem capacity. |
| **National Bureau of Statistics** | https://www.stats.gov.cn/english/ | China IP, PPI (including chemical sub-indices), production statistics for macro demand slide. |
| **General Administration of Customs** | http://www.customs.gov.cn/ | Import/export volumes: crude, PTA, EG, polyester — trade flow evidence. |

---

## Industry research & data providers (fundamentals)

| Source | Link | Summary |
|--------|------|---------|
| **ICIS** | https://www.icis.com/explore/commodities/chemicals/ | Global chemical price assessments, PTA/EG/PX chain commentary, capacity maps. Paywalled; use if you have access. |
| **Wood Mackenzie — Chemicals** | https://www.woodmac.com/industry/chemicals/ | Supply-demand balances, cost curves, project timelines for aromatics. Enterprise subscription. |
| **隆众资讯 (OilChem)** | https://www.oilchem.net/ | Leading China commodity intelligence: PTA/EG operating rates, port inventory, weekly spot prices. Chinese UI; core source for 华东港口 EG inventory. |
| **百川盈孚 (BAIINFO)** | https://www.baiinfo.com/ | China spot prices, capacity, operating rates across chemicals including PTA and EG. |
| **CCF / SCI (化纤信息网)** | http://www.ccf.com.cn/ | Polyester chain focus: PTA, EG, fiber operating rates and textile demand — strong for downstream link. |

---

## Listed companies & annual reports (capacity / integration)

| Source | Link | Summary |
|--------|------|---------|
| **Wanhua Chemical** | https://www.whchem.com/ | Major integrated petchem player; MDI + polyurethanes; useful for cost-curve and integration examples. |
| **Hengli Petrochemical** | http://www.hengliinc.com/en/ | Large integrated refining–PTA–polyester complex (Dalian); capacity cycle case study. |
| **Rongsheng Petrochemical** | http://www.rongsheng.com/en/ | Zhejiang integrated complex (ZPC); PX–PTA–polyester vertical integration. |
| **Sinopec — Investor relations** | http://www.sinopec.com/listco/en/ | National major; refining + chemical segment volumes, capex, utilization disclosures. |
| **PetroChina** | http://www.petrochina.com.cn/ptr/ | Upstream + refining; crude processing and petchem segment for supply context. |
| **HKEX / SSE disclosures** | https://www.hkexnews.hk/ ; https://www.sse.com.cn/ | Search 恒力石化, 荣盛石化, 桐昆股份 for PTA/polyester exposure and capacity guidance. |

---

## Global benchmarks & crude linkage (SC context)

| Source | Link | Summary |
|--------|------|---------|
| **EIA — International energy** | https://www.eia.gov/international/ | World crude production, China consumption/imports; pairs with BVAR `d_prod`. |
| **OPEC Monthly Oil Market Report** | https://www.opec.org/opec_web/en/publications/338.htm | Supply outlook, demand revisions — macro driver for SC scenarios. |
| **IEA Oil Market Report** | https://www.iea.org/reports/oil-market-report | Alternative supply-demand framing; useful for bull/base/bear crude scenarios. |
| **FRED — Brent real price** | https://fred.stlouisfed.org/series/POILBREUSDM | Deflated Brent for SC–Brent basis and as fallback real oil price series. |

---

## Academic & structural models (BVAR / shock framework)

| Source | Link | Summary |
|--------|------|---------|
| **Kilian (2009) — original paper** | https://www.aeaweb.org/articles?id=10.1257/aer.99.3.1053 | Foundational oil shock identification (supply / activity / precautionary); cite for BVAR ordering. |
| **Dallas Fed — Kilian activity index** | https://www.dallasfed.org/research/economists/kilian | Updated `rea` series (2019-corrected); direct download for BVAR replication. |
| **Your BVAR replication repo** | https://github.com/restinghouse0203/Bayesian-Time-Series-Oil-Market-Forecast/ | Cornell project code and methodology; reuse for SC-adapted estimation. |

---

## Market data terminals (if available)

| Source | Link | Summary |
|--------|------|---------|
| **Wind (万得)** | https://www.wind.com.cn/ | China futures continuous contracts (SC, TA, EG), PPI, operating rate proxies, equities. |
| **iFinD (同花顺)** | https://www.51ifind.com/ | Alternative to Wind for futures, spreads, and chemical sector indices. |
| **Bloomberg Terminal** | (terminal) | Offshore Brent/Dubai, PX assessments, ICIS-linked curves — for SC–offshore basis. |

---

## Suggested reading order (Phase 2)

1. INE SC specs + one week of SC/TA/EG futures data (exchange or Wind).  
2. OilChem or BAIINFO: PTA operating rate + EG port inventory (latest week).  
3. Hengli or Rongsheng annual report section on PTA/polyester capacity.  
4. Kilian (2009) abstract + Dallas Fed `rea` documentation (BVAR appendix).  
5. One ICIS/WoodMac PTA outlook piece if accessible — otherwise use 隆众 capacity tables.

---

## Deck footnote convention

For every chart: **source, as-of date, frequency, and any spliced continuous contract rule** (e.g. SC main contract roll methodology on Wind).
