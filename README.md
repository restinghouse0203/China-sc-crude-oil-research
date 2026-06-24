# China-sc-crude-oil-research

Research on **China INE SC crude** (Layer 1) and a **Kilian-type Bayesian VAR** for global structural oil shocks, in the context of China's chemical value chain.

**Thesis:** Structural crude shocks (supply vs aggregate demand vs oil-specific / precautionary) transmit unevenly; this repo covers **Layer 1 landed-cost signals** and the **BVAR shock-regime module**.

---

## Key findings

### Weak refinery demand (China domestic story)

China has **weak refining demand** against a backdrop of **elevated crude costs** and **Middle East conflict stress** (refinery utilization fell ~16pp vs the Feb 2026 baseline). Evidence from this repo:

- **SC–Brent basis** — SC trades at a **discount** to Brent (~−5 USD/bbl, z ≈ −1.7σ) → China landed cost below offshore benchmarks despite global stress
- **SC futures term structure** — **backwardation** (−2.5 CNY/bbl front→6M) → near-term physical tight, not a storage-glut curve
- **Market volume** — front-month **open interest ~51k lots**; active SC continuous trading on INE
- **INE warehouse receipts** — **downward trend** from ~10M to ~3M bbl (2024–2026), now plateauing near lows → deliverable inventory drawn down

Together: refiners are **cutting runs** (CDU util **57.5%**) while deliverable SC stocks are **thin** — a demand-side margin squeeze, not a simple global fear-premium spike. Details in [`notes/layer1_finding.md`](notes/layer1_finding.md).

### Layer 1 (SC / refining)

- **Import dependence ~72%** (2024 EIA); refinery runs fell faster than imports YoY
- **Refinery CDU utilization 57.5%** — teapots at **43.5%**, megaprojects **59.2%**

### BVAR (global shock regime)

Details in [`notes/oil_BVAR_finding.md`](notes/oil_BVAR_finding.md):

- Kilian Cholesky: supply → activity → oil-specific demand on (`d_prod`, `rea`, `rpo_sc`)
- **2024–25:** structural shock realizations **near zero** (muted global shock environment)
- **Oil price channel:** oil-specific shock moves `rpo` on impact; own-shock FEVD ~76% at h=15 months
- **Combined read:** global precautionary premium quiet; SC dynamics driven more by **China refining margin / deliverable frictions**

---

## Repository structure

| Path | Contents |
|------|----------|
| [`Slide_China_s_Crude_Oil_Research`](Slide_China_s_Crude_Oil_Research.pdf) | Slides of the value chain from crude oil to polyester in China, covering areas including market characteristics, data pattern, macroeconomic shock decomposition |
| [`SC_research.ipynb`](SC_research.ipynb) | Layer 1 notebook — term structure, basis, EIA balance, utilization, warehouse receipts |
| [`Script/BVAR_shock_model.ipynb`](Script/BVAR_shock_model.ipynb) | BVAR notebook — Gibbs sampler, IRFs, FEVD, shock decomposition |
| [`code/`](code/) | Data fetch and build scripts (akshare, EIA, OilChem CSV) |
| [`src/`](src/) | BVAR Gibbs sampler and helpers function |
| [`data/`](data/) | Curated CSV/JSON dataset |
| [`notes/`](notes/) | Findings, methodology, project status ([`notes/STATUS.md`](notes/STATUS.md)) |
| [`research/`](research/) | Value chain notes (Layer 1 scope) |

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pandas numpy matplotlib scipy statsmodels akshare jupyter requests

jupyter notebook SC_research.ipynb
jupyter notebook Script/BVAR_shock_model.ipynb   # 12k Gibbs draws — allow several minutes
```

Run scripts from repo root, e.g. `python code/sc_basis.py`.

**Optional:** `WindPy` (proprietary) for daily Dubai via `code/fetch_wind.py`; FRED/akshare fallbacks are documented in [`data/sc_data_sources.md`](data/sc_data_sources.md).

---

## Refresh data (optional)

| Script | Env / deps | Output |
|--------|------------|--------|
| `code/sc_basis.py` | akshare | `data/sc_basis_*` |
| `code/sc_term_structure.py` | akshare INE | `data/sc_term_structure_*` |
| `code/china_crude_supply_demand.py` | `EIA_API_KEY` optional | `data/china_crude_*` |
| `code/fetch_refinery_utilization.py` | curated OilChem CSV | `data/china_refinery_utilization.csv` |
| `code/build_oil_splice.py` | FRED + akshare | `data/oil_price_splice_*.csv` |
| `code/build_data_csv.py` | Kilian + splice | `data/BVAR_data.csv` |

---

## Methodology (short)

**BVAR variables:** global Δproduction, Kilian real activity index, log real oil price (`rpo_sc` = Brent pre-2018, INE SC post-2018).

**Identification:** recursive Cholesky — ε₁ supply, ε₂ aggregate demand, ε₃ oil-specific demand (precautionary in Kilian taxonomy).

**Sample:** post–SC-era filter from 2018-03 in the notebook; full price splice 1987–2025.

---

## Limitations

- Monthly global BVAR — informs **regime**, not high-frequency SC trading
- OilChem refinery utilization is a **curated weekly CSV**, not a live API
- Short effective sample after lags in the SC era
- Layers 2–4 (PX, PTA, EG) not included in this repository

---

## License & disclaimer

MIT License. Research project — **not investment advice**.

## Related

- Kilian, L. (2009). [*Not All Oil Price Shocks Are Alike*](https://www.aeaweb.org/articles?id=10.1257/aer.99.3.1053)
- [INE SC contract](https://www.ine.cn/eng/market/futures/energy/sc/)
