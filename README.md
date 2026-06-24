# China-sc-crude-oil-research

Research on **China INE SC crude** (Layer 1) and a **Kilian-type Bayesian VAR** for global structural oil shocks. Built for a Clocktower investment-team presentation on China's chemical value chain.

**Thesis:** Structural crude shocks (supply vs aggregate demand vs oil-specific / precautionary) transmit unevenly; this repo covers **Layer 1 landed-cost signals** and the **BVAR shock-regime module**. PTA/EG/PX (Layers 2–4) are archived locally only.

**Stage:** 1 (frozen) | **As-of:** 2026-06-24 | **Scope:** Layer 1 + BVAR | **Deck:** PDF only

See [STATUS.md](STATUS.md) for the module checklist.

---

## Key findings

**Layer 1 (SC / refining)** — details in [`notes/layer1_finding.md`](notes/layer1_finding.md):

- **Backwardation** on INE SC (−2.5 CNY/bbl front→6M) → near-term deliverable tightness
- **SC discount vs Brent** (~−5 USD/bbl, z ≈ −1.7σ) → China landed-cost wedge, not offshore parity
- **INE warehouse receipts** near multi-year lows (~2.96M bbl) → thin deliverable inventory
- **Refinery CDU utilization 57.5%** (−16pp vs Feb 2026 baseline) → sharp run-cut phase
- **Import dependence ~72%** (2024 EIA); runs fell faster than imports YoY

**BVAR** — details in [`notes/oil_BVAR_finding.md`](notes/oil_BVAR_finding.md):

- Kilian Cholesky: supply → activity → oil-specific demand on (`d_prod`, `rea`, `rpo_sc`)
- **2024–25:** structural shock realizations **near zero** (muted global shock environment)
- **Oil price channel:** oil-specific shock owns contemporaneous `rpo` moves; own-shock FEVD ~76% at h=15 months
- **Combined read:** global precautionary premium quiet; China SC driven more by **domestic refining margin / deliverable frictions** (see deck)

---

## Repository map

| Path | Contents |
|------|----------|
| [`SC_research.ipynb`](SC_research.ipynb) | Layer 1 data pulls (term structure, basis, EIA, utilization, receipts) |
| [`BVAR_shock_model.ipynb`](BVAR_shock_model.ipynb) | Gibbs BVAR, IRFs, FEVD, shock decomposition |
| [`code/`](code/) | Reproducible fetch/build scripts |
| [`src/`](src/) | BVAR Gibbs sampler and helpers |
| [`data/`](data/) | Curated CSV/JSON (offline reproducibility) |
| [`notes/`](notes/) | Findings and methodology notes |
| [`research/`](research/) | Value chain context (Layer 1 scope in repo) |
| [`deck/main.pdf`](deck/main.pdf) | Presentation slides (PDF only; LaTeX in local `backup/`) |

**Not on GitHub:** `backup/` (Layer 2–4 code, data, notes, deck sources) — gitignored.

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter notebook SC_research.ipynb      # Layer 1
jupyter notebook BVAR_shock_model.ipynb  # BVAR (12k Gibbs draws — allow several minutes)

# Slides
open deck/main.pdf
```

Run scripts from repo root, e.g. `python code/sc_basis.py`.

---

## Refresh data (optional)

| Script | Env / deps | Output |
|--------|------------|--------|
| `code/sc_basis.py` | akshare, FRED via akshare | `data/sc_basis_*.json/csv` |
| `code/sc_term_structure.py` | akshare INE | `data/sc_term_structure_*` |
| `code/china_crude_supply_demand.py` | `EIA_API_KEY` optional | `data/china_crude_*` |
| `code/fetch_refinery_utilization.py` | curated OilChem CSV | `data/china_refinery_utilization.csv` |
| `code/build_oil_splice.py` | FRED + akshare | `data/oil_price_splice_*.csv` |
| `code/build_data_csv.py` | Kilian + splice | `data/BVAR_data.csv` |

See [`data/sc_data_sources.md`](data/sc_data_sources.md) and [`notes/bvar_data_sources.md`](notes/bvar_data_sources.md).

---

## Methodology (short)

**Variables (BVAR):** global Δproduction, Kilian real activity index, log real oil price (`rpo_sc` = Brent pre-2018, INE SC post-2018).

**Identification:** recursive Cholesky — ε₁ supply, ε₂ aggregate demand, ε₃ oil-specific demand (interpreted as **precautionary** in Kilian taxonomy).

**Sample:** BVAR estimation uses post–SC-era filter from 2018-03 in the notebook; full splice 1987–2025 for price history.

---

## Limitations

- Monthly global BVAR — informs **regime**, not day-trade SC timing
- OilChem refinery utilization is a **curated weekly CSV**, not a live API
- Short effective sample after 24 lags in SC era
- Layers 2–4 (PX, PTA, EG) intentionally omitted from this repository

---

## License & disclaimer

MIT License. Research exercise for interview presentation — **not investment advice**.

## Related

- Kilian, L. (2009). [*Not All Oil Price Shocks Are Alike*](https://www.aeaweb.org/articles?id=10.1257/aer.99.3.1053)
- [INE SC contract](https://www.ine.cn/eng/market/futures/energy/sc/)
