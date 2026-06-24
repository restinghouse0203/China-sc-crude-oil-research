# China Chemical Industry Presentation — Project Plan

> **Shipped scope:** See [STATUS.md](STATUS.md) and [README.md](README.md). Stage 1 freeze = **Layer 1 + BVAR** on GitHub ([China-sc-crude-oil-research](https://github.com/restinghouse0203/China-sc-crude-oil-research)). Layers 2–4 and deck LaTeX live in local `backup/` (not published).

**Task:** 5–8 slide deck + 30–45 min presentation and Q&A  
**Topic:** China's chemical industry value chain and related commodity futures strategies  
**Audience:** Clocktower full investment team (allocator / FoF platform)  
**Output language:** English (slides, speaker notes, research notes)  
**Deck format:** LaTeX (Beamer) → PDF

---

## What They Are Evaluating

This is not a textbook industry overview. They want to see:

1. **Research process** — how you scope, prioritize sources, and build a thesis.
2. **Analytical framework** — repeatable structure (drivers → scenarios → tradable expression).
3. **Investment translation** — how sector insights become actionable views in futures (and optionally equities/spreads).
4. **Fundamentals ↔ futures linkage** — inventory, basis, term structure, policy shocks, and cross-commodity relationships.

Given Clocktower's allocator model, frame views as **risk-aware, monitorable positions** an allocator or underlying macro manager might express — not as discretionary PM trade instructions.

---

## Recommended Slide Architecture (7 slides)

| # | Slide | Purpose | ~Time |
|---|-------|---------|-------|
| 1 | **Thesis & scope** | One-line view + what you will / won't cover | 3 min |
| 2 | **Value chain map** | Upstream → midstream → downstream with key commodities | 5 min |
| 3 | **Key drivers & framework** | Supply/demand, cost curve, policy, cycle positioning | 6 min |
| 4 | **China-specific fundamentals** | Capacity, margins, trade flows, current cycle phase | 7 min |
| 5 | **Futures market map** | Contracts (exchange, contract, liquidity), linkage to chain | 6 min |
| 6 | **Investment views & scenarios** | 2–3 concrete theses with bull/base/bear triggers | 8 min |
| 7 | **Risks, monitoring, appendix pointer** | What would falsify the view; KPIs to watch | 5 min |

Leave ~5–10 min buffer for transitions and discussion hooks.

---

## Step-by-Step Execution Plan

### Phase 1 — Scoping (Day 1)

**Goal:** Define a tight narrative so 7 slides stay deep, not broad.

- [ ] Pick **2–3 anchor commodities** along the chain (e.g. methanol → olefins → PP/PE; or crude/naphtha → aromatics → PTA).
- [ ] Confirm **English** for all deliverables (slides, notes, Q&A prep); live discussion may still be bilingual if the room prefers.
- [ ] Write a **one-sentence thesis** (e.g. "China olefin margins compress into 2026 capacity wave; long naphtha–olefin spread / short PP basis").
- [ ] List **3 falsifiers** (capacity delay, demand stimulus, crude regime change).

**Output:** `notes/thesis_one_pager.md`

---

### Phase 2 — Value Chain Research (Days 1–2)

**Goal:** Build a defensible chain map with Chinese context.

- [ ] Draw upstream → midstream → downstream flow (feedstock → intermediates → end products).
- [ ] Mark **major Chinese production hubs** (e.g. coastal integrated complexes, coal-to-chem in Inner Mongolia/Ningxia).
- [ ] Identify **top 5–8 listed / relevant players** (e.g. Wanhua, Hengli, Rongsheng, Sinochem, PetroChina/Sinopec chemical subsidiaries).
- [ ] Note **capacity cycle**: announced builds, start-ups, utilization, import dependence.
- [ ] Capture **cost curve logic** (coal vs naphtha vs ethane routes where relevant).

**Sources to prioritize:**

- Company annual reports & investor presentations (A-share / H-share)
- MIIT, NDRC policy releases; environmental inspection cycles
- ICIS / Wood Mackenzie / Bloomberg industry notes (if available)
- Exchange delivery rules and warehouse receipt data (SHFE, DCE, ZCE)
- Wind / iFinD for China prices, spreads, inventory proxies

**Output:** `research/value_chain.md` + one clean diagram for the deck

---

### Phase 3 — Fundamentals & Driver Framework (Days 2–3)

**Goal:** Show *how you think*, not just *what you found*.

- [ ] Build a **driver tree**: demand (construction, auto, packaging, agri) × supply (capacity, outages, imports) × cost (energy, feedstock) × policy.
- [ ] Place the industry on a **cycle clock** (expansion / peak / contraction / trough) with evidence.
- [ ] Quantify **2–3 key metrics** (operating rates, inventory days, margin spreads, import arbitrage windows).
- [ ] Run **one simple scenario table** (bull / base / bear) with price or spread implications.

**Output:** `research/fundamentals_framework.md` + scenario table for slide 6

---

### Phase 4 — Futures Market Mapping (Days 3–4)

**Goal:** Explicitly link fundamentals to tradable instruments — core ask from the email.

- [ ] List **relevant China futures** by segment:

  | Segment | Example contracts (verify codes) |
  |---------|----------------------------------|
  | Energy / feedstock | SC crude, LU low-sulfur fuel oil, PG LPG |
  | Olefins / aromatics | MA methanol, EG ethylene glycol, TA PTA, EB styrene |
  | Polymers | PP, PE (L/ V), PVC |
  | Agri-chem inputs | UR urea, SA soda ash, FG glass |

- [ ] For each anchor commodity, document:
  - Exchange, contract size, dominant participants (physical vs financial)
  - **Basis** vs spot / import parity
  - **Term structure** (contango/backwardation) and what it signals now
  - **Cross-contract spreads** you would monitor (e.g. MA-PP, TA-EG, crack/spread proxies)
- [ ] Note **liquidity and roll** considerations for allocator-style sizing.

**Output:** `research/futures_map.md` + slide-ready table

---

### Phase 5 — Formulate Investment Views (Days 4–5)

**Goal:** 2–3 actionable, differentiated views with clear risk/reward.

For each view, use this template:

```
View: [directional or relative value]
Fundamental rationale: [...]
Futures expression: [contract / spread / hedge leg]
Entry catalyst: [...]
Risk / stop thesis: [...]
Monitoring KPIs: [inventory, margin, policy, crude]
Horizon: [weeks / months / cycle]
```

**Example view types (pick what fits your thesis):**

- Relative value: long weak / short strong link in chain (e.g. spread trade)
- Directional: macro + cost push on single commodity
- Curve: inventory draw → backwardation play
- Hedge structure: long downstream margin vs short feedstock

- [ ] Draft **2–3 views** (not more — depth over breadth).
- [ ] Tie each view to **fundamentals AND futures microstructure**.
- [ ] State what an **allocator** would ask: liquidity, drawdown, correlation to macro book.

**Output:** `research/investment_views.md`

---

### Phase 6 — Build the Deck (Days 5–6)

**Goal:** 5–8 Beamer slides, clean visuals, English speaker notes for 30–45 min.

- [ ] Set up **LaTeX / Beamer** project (`deck/main.tex` + `deck/preamble.tex` or single-file deck).
- [ ] One **value chain diagram** (TikZ or exported PNG — avoid cluttered vendor charts).
- [ ] One **driver / framework** exhibit (2×2 or driver tree).
- [ ] One **data chart** (margins, inventory, or spread — sourced and dated; `\includegraphics` from `data/charts/`).
- [ ] One **futures map table** (contract ↔ fundamental link).
- [ ] One **scenario / view summary** table.
- [ ] Minimal text per slide; put detail in **`\note{...}`** speaker notes (Beamer `notes` option) or a parallel `notes/speaker_script.md`.
- [ ] Add **sources footnote** on data slides.
- [ ] Compile with `pdflatex` / `latexmk` → `deck/main.pdf` (primary deliverable).

**Suggested folder layout:**

```
Presentation - China Chemical Industry Value Chain/
├── task_requirements.yaml
├── PLAN.md
├── deck/
│   ├── main.tex              # Beamer master file
│   ├── preamble.tex          # packages, theme, macros (optional)
│   ├── sections/             # optional per-slide .tex inputs
│   └── main.pdf              # compiled output
├── research/
│   ├── value_chain.md
│   ├── fundamentals_framework.md
│   ├── futures_map.md
│   └── investment_views.md
├── notes/
│   ├── thesis_one_pager.md
│   └── speaker_script.md     # English talk track
└── data/
    └── charts/               # exported PNGs/PDFs with date stamps
```

- [ ] Verify PDF renders correctly (fonts, CJK not required if deck is English-only).

---

### Phase 7 — Rehearse & Discussion Prep (Days 6–7)

**Goal:** 30–45 min pacing; strong Q&A on futures mechanics and China policy.

**Timing drill:**

- [ ] Dry run with timer: target **35 min** talk + **10 min** built-in discussion hooks.
- [ ] Prepare **3 "if you only remember one thing"** messages.
- [ ] Anticipate questions:

  | Likely question | Prep |
  |-----------------|------|
  | Why these commodities vs others? | Scoping rationale, liquidity, cycle conviction |
  | How do futures prices lead / lag spot? | Basis, inventory, delivery logic |
  | Policy risk (dual control, carbon, export tariffs)? | Specific recent measures + scenario impact |
  | How would a macro HF express this? | Futures vs offshore swaps vs equity beta |
  | What data do you monitor weekly? | KPI list tied to each view |
  | What's your biggest uncertainty? | Honest gap + how you'd resolve it |

- [ ] Prepare **2 questions for them** (e.g. how their macro managers currently trade China commodity beta; LP risk budget for commodity sleeves).

**Output:** `notes/speaker_script.md` + `notes/qa_prep.md`

---

## Master To-Do Checklist

### Research
- [ ] Anchor commodities selected (max 3)
- [ ] Value chain diagram complete
- [ ] Driver framework + cycle positioning documented
- [ ] China capacity / margin / inventory data gathered (with dates)
- [ ] Futures contracts mapped to chain segments
- [ ] 2–3 investment views with scenarios drafted

### Deck & Delivery
- [ ] 5–8 Beamer slides drafted (`deck/main.tex`)
- [ ] English speaker notes written (`\note{}` and/or `notes/speaker_script.md`)
- [ ] Charts sourced and labeled
- [ ] `main.pdf` compiled and reviewed
- [ ] 35-min timed rehearsal completed
- [ ] Q&A prep document complete

### Day-of
- [ ] Deck loaded + backup PDF on hand
- [ ] Live data check on key spreads / inventories (morning of)
- [ ] Notepad for discussion takeaways

---

## Prioritization Principle (Aligns With Interviewer Ask)

When drowning in data, rank by:

1. **Materiality** — does it move margins or prices for your anchor commodities?
2. **Tradability** — is there a liquid futures or spread expression?
3. **Timeliness** — is it a live cycle/policy issue, not stale history?
4. **Falsifiability** — can you name what proves you wrong?

Drop everything else from the deck.

---

## Connection to Clocktower Role

Weave in (subtly, not forced):

- **Allocator lens:** views as monitorable exposures, not prop bets.
- **Risk framing:** gross/net thinking, correlation to macro, scenario loss.
- **Systems mindset:** mention KPIs you would automate (SQL/Python pipeline for spreads, inventory, manager positions) — mirrors their technical assessment and JD.

---

## Suggested Timeline (1 Week)

| Day | Focus |
|-----|-------|
| 1 | Scoping + value chain |
| 2 | Fundamentals + data |
| 3 | Futures mapping |
| 4 | Investment views + scenarios |
| 5 | Slide build |
| 6 | Rehearsal + Q&A prep |
| 7 | Buffer / polish / live data refresh |

---

## Next Action

Start with **Phase 1**: write the one-sentence thesis and pick anchor commodities. Everything else flows from that choice.
