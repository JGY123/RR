---
name: RR Backlog
purpose: Append-only feature/work queue. Non-trivial items surfaced from audits, specs, and user direction. Not a roadmap — a capture surface. Priority is assigned when items get scheduled.
last_updated: 2026-05-01 (Round 2 inquisitor follow-ups added — see "Audit follow-ups" section)
---

# RR Backlog

Non-trivial work items (anything that isn't a ≤5-line trivial fix). Trivial fixes are applied inline during their audit pass and closed via tag; they do not appear here.

**Conventions:**
- Append-only. Newest at top.
- Each item has: ID · title · origin · rough size · blockers · notes.
- When an item ships, move to "Shipped" section at bottom.
- When a batch of audits produces many items, group them under one header to avoid bureaucracy.

---

## 🔭 Audit follow-ups (Round 2 deferred picks — 2026-05-01)

Items surfaced by `INQUISITOR_QUEUE_R2_2026-04-30.md` user replies on 2026-05-01. Each defers past the team presentation; user picked these explicitly but we ran out of time pre-demo. Not blockers; nice-to-haves.

### B117 · cardCorr default period 1Y weekly + pre-cache 3M weekly + 3Y monthly
- **Origin:** R2-Q12 user pick: "1Y weekly which you have to pre-calculate once you have all the data you also need 3 month weekly and 3 year monthly pre-calculated and perhaps a few more — let's make sure it works"
- **What:** cardCorr today computes correlation matrix on every period-dropdown change (~50ms-2s depending on factor count). Pre-compute the popular variants once per data load: {3M weekly, 1Y weekly, 3Y monthly, All}. Cache as `cs._corr_cache[period]`. Default dropdown to 1Y weekly.
- **Size:** S (~30 lines + parser-side maybe).
- **Blockers:** none. Defer for post-demo.

### B118 · cardRiskFacTbl Return column period-aware
- **Origin:** R2-Q13 user pick: "B although you can try convince otherwise."
- **Counterargument worth raising:** the Return column shows the FACTOR's return for the period — so making it period-aware means cumulative return over the global Impact period (3M / 6M / 1Y / All). The cumulative return doesn't simply linear-aggregate the per-week returns; it should be `Π(1 + r_t) - 1`. We have the per-week returns from `cs.snap_attrib[name].hist[].ret` so this is doable.
- **Implementation:** new helper `getReturnForPeriod(factorName, period)` that geometric-links the per-week returns over the period window. Update cardRiskFacTbl Return column header to show "(period)" label. Same for cardFacDetail.
- **Size:** M (~60 lines + helper). Cross-tile sweep with cardFacDetail.
- **Blockers:** none.

### B119 · Mockup mechanism enhancements (dynamic + selection buttons + nav)
- **Origin:** R2-Q15 user pick: "make sure that this like everything else is dynamic and updates when selecting a different week. in general when showing that html it would be cool if it could have all kind of yes/no selection buttons that indicates to you the selection or maintain some kind of note where you can look or i can paste and there should be a next button to go the next question"
- **What:** Upgrade the `viz-specs/{tile}-mockup.html` template to:
  - **Dynamic data**: read from `latest_data.json` (or a frozen snapshot) so changing the strategy/week selector updates the mockup
  - **Selection buttons**: each candidate design has Yes/No/Maybe buttons that capture user pick → write to `viz-specs/{tile}-decisions.json`
  - **Notes area**: free-text input that saves to localStorage; user can paste back to me
  - **Next button**: navigates between candidates / between mockups in the queue
- **Size:** L (~3-4 hours — dynamic data wiring, decision capture, navigation framework).
- **Blockers:** none. Big design-tooling investment, defer until next 2-3 mockups stack up.

### B120 · Tile chrome capability sweep (Reset View + Hide + Full Screen + PNG everywhere)
- **Origin:** R2-Q25 user pick: "give list of all tiles with buttons that they have vs buttons they could have, I can check any tile that needs more functionality such as hide, full screen etc."
- **Reference:** `TILE_CHROME_MATRIX.md` (shipped 2026-05-01) — 30 tiles × 10 affordances grid. User checks ☐→☑ on what to add.
- **Sub-batches once user marks the matrix:**
  - **B120.1** — Sweep Reset View (↺) across all chart tiles. Framework already shipped (commit 1848840). Per-tile: register custom handler in `window._tileDefaults['cardX']` + add `${resetViewBtn('cardX')}` to header.
  - **B120.2** — Add Full Screen (⛶) to chart tiles missing it. Generalize `openSecFullscreen` / `openCountryFullscreen` into `openTileFullscreen(tileId)`.
  - **B120.3** — Add Hide (×) collapse-button to all tiles. New mechanism: collapse state in localStorage `rr.collapsed.{tileId}` + smooth height transition.
  - **B120.4** — Add PNG export to all tiles via existing `screenshotCard(selector)`. Uniform `${pngBtn('cardX')}` helper.
- **Size:** M-L total (~6-8 hours across the 4 sub-batches).
- **Blockers:** B120.3 needs a Hide-state spec first.

### B121 · Period-aware sweep across drill modals
- **Origin:** R2-Q23 user pick: "yes — consistency win."
- **What:** every drill modal has an "Impact" or "Return" column. Today some honor the global Impact period selector, some don't. Audit and standardize.
- **Affected modals:** TE drill, Idio drill, Beta drill, AS drill, Factor drill, Country drill, Group drill, Sector drill, Holding drill (oSt).
- **Size:** M (~3 hours — audit + per-modal fix).
- **Blockers:** none.

### B122 · cardCorr formal tile audit
- **Origin:** R2-Q24 user pick: "yes."
- **What:** Run the standard tile-audit subagent against cardCorr (now first-class as of commit 819c493). Add to MARATHON_PROTOCOL.md.
- **Size:** S (~30 min for audit + ~30 min for any fixes).
- **Blockers:** none.

### B123 · Tableau-pattern mini-explainer doc
- **Origin:** R2-Q21 user pick: "need to learn more about each and ideally if you can show examples or direct to links where it's visual."
- **What:** Doc explaining the 7 Tableau patterns I flagged (bullet, marimekko, slope, highlight tables, dot plots, reference bands, annotated histograms) with:
  - One-paragraph explanation each
  - Link to a public example (Storytelling with Data / Bloomberg article / Tableau gallery)
  - "Where it'd fit in RR" — concrete tile candidate
- **Size:** S (~1 hour).
- **Blockers:** none. Can ship pre-coffee any morning.

### B124 · Audit cadence policy refinement
- **Origin:** R2-Q22 user pick: "a, b, c at least until there is full confidence and then report and recommend how to go once."
- **What:** Combo audit cadence — per-batch (every commit) + bi-weekly + triggered. After 4-6 weeks of clean audits, agent reports back and recommends "drop to triggered-only" or "continue rolling".
- **Mechanism:** automated tile-audit subagent run after every 5+ commits. Bi-weekly cron-style nudge. User can manually trigger an audit any time. Agent writes a MARATHON_AUDIT_LOG.md entry with each pass.
- **Size:** M (~2 hours for the agent-trigger mechanism + log format).
- **Blockers:** none. Wire after the dust settles post-demo.

---

## B116 · Universe='benchmark' aggregator under-report — cross-tile SEV-1 (NEEDS PM DECISION)
- **Origin:** cardCountry audit 2026-04-30, finding F2 (SEV-1). Same pattern affects cardSectors / cardGroups / cardRanks — wherever `aggregateHoldingsBy(...,{mode:'benchmark'})` is used.
- **Symptom:** When user toggles Universe → Benchmark, the # column and Factor TE Breakdown columns silently under-report by ~17x for major countries (e.g., GSC US: agg=3.58 vs c.b=61.12). Verified against `latest_data.json`.
- **Root cause:** v2 Security slim (per CLAUDE.md "Upcoming FactSet format change") — `cs.hold[]` only ships portfolio + materially-large BM-only holdings. Aggregating by `h.b > 0` captures only the small subset, not the full benchmark constituent universe.
- **Fix options (PM decision):**
  - **(a) Honest hide** — when `_aggMode==='benchmark'`, hide the # column and Factor TE Breakdown columns entirely. Bench% column stays (reads `c.b` directly, correct). Less data, no wrong data. Recommended per April-27 anti-fabrication rules.
  - **(b) Qualifier chip** — render the columns with "(only top BM-only shown)" qualifier and visual de-emphasis (italic / lower opacity).
  - **(c) Parser-side surface** — if FactSet ships per-bucket factor breakdowns at the aggregate level (`c.factor_breakdown` etc.), use those instead of holding-level aggregation. Requires parser dig + verification on next CSV sample.
- **Size:** S (option a, ~30 lines × 4 tiles = ~120 lines) or M (option b/c, more invasive).
- **Surfaced:** ceec116 commit message; tracking here for resolution.

---

## B115 · cardCountry header KPI strip — match cardFacRisk gold (DEFERRED)
- **Origin:** cardCountry audit 2026-04-30, finding F3 (SEV-2).
- **Items:** subtitle row ("geographic exposure · click any country to drill · N/M mapped"), inline KPI strip (Largest |Active| country, Largest |TE| country, Country count). Lift skeleton from `#facRiskKpi`.
- **Size:** S (~30 lines + a `_buildCtryKpi(s)` helper).
- **Blockers:** none. Deferred only on prioritization.

---

## B114 · History persistence — append-only architecture
- **Origin:** user direction during marathon, 2026-04-27. "We are building everything to be ready to ingest and show the full history which is long. Many would have 15 years of data. Once the massive run lands and is confirmed parsed, history doesn't change. Future uploads are appends."
- **Full design:** `HISTORY_PERSISTENCE.md` at repo root.
- **Recommended path:** Option D (cumulative `data/cumulative_history.json.gz` committed to repo) + Option B (IndexedDB for in-session preview before promoting).
- **Critical sequencing:** must land BEFORE the production massive-run CSV ingest. Otherwise the first ingest is a one-shot replace and the append-only model never starts.
- **Size:** L (~6–10 hours, parser merge logic + dashboard fetch path + IndexedDB cache + cumulative-save UI button + new test suite).
- **Open questions for user:** see `HISTORY_PERSISTENCE.md` Section "Open questions for the user".

---

## 🔭 Marathon-surfaced (B108–B113) — from cardFacDetail review

These items came directly out of user feedback during the live tile review on 2026-04-27.

### B108 · — *(reserved, unused — keeping numbering aligned with marathon-surfaced bucket)*

### B109 · Impact-period unified convention (cross-tile, HIGH priority)
- **Origin:** marathon review of cardFacDetail, 2026-04-27. User feedback: "Impact is shown but is meaningless without a time period — recurring issue across many tiles."
- **Scope:** every column showing factor-attribution Impact (Exposure × Return) gets explicit period qualifier in header. Add a global period selector near top-bar (next to strategy/week selectors). Default: latest snapshot. Periods available come from parser's 31-col attribution schema (5 periods/row).
- **Affected tiles:** cardFacDetail (Impact col), cardAttrib (Impact rows), cardAttribWaterfall (return-impact bars), drill modals (Impact stat row), cardThisWeek (where impact is mentioned in narrative bullets).
- **Why cross-tile:** apply once to convention, propagate everywhere. Don't fix piecemeal.
- **Sequence:** ships as ONE commit after marathon closes — all affected tiles touched together. Must ship before B111 (drill modal rebuild) since drill displays Impact too.
- **Data probe needed:** confirm exact period labels parser ships in 31-col attribution section (1Y / 6M / 3M / 1M / latest?).

### B110 · Sub-factor drill on Country / Currency / Industry (NEW feature)
- **Origin:** marathon review of cardFacDetail, 2026-04-27. User: "click into Country/Currency/Industry should drill to per-country/currency/industry contribution."
- **Scope:** when user clicks one of those 3 factor rows in cardFacDetail (or anywhere a factor row is clickable), open a nested drill showing the per-component decomposition. Data lives in CSV but in a different section (user offered to point at exact location).
- **Blockers:** confirm exact CSV section name + parser exposure path. User said "if you need help i can point you exactly to where" — flag for follow-up before implementation.
- **Pairs with:** B111 (drill modal rebuild) — natural place to nest sub-drill.
- **Size:** M.

### B111 · `oDrF` factor drill modal — full rebuild (replaces B103)
- **Origin:** marathon review, 2026-04-27. User feedback consolidates many issues into one rebuild.
- **B103 NOTE:** earlier-planned standalone tile "per-security raw factor drill" is now SUBSUMED into B111 as the `[Raw Exposure | TE Contribution]` toggle on the Top-5/Bot-5 panel. B103 closed as duplicate.
- **Scope:**
  - **NEW: Time series of active exposure** (from `hist.fac[name]` — already populated by parser, currently just rendered as KPI snapshot).
  - **NEW: Time series of TE contribution** (per-week `f.c` if available; else compute from `f.a × f.dev`).
  - **Resolve redundancy:** stats currently include "Contribution" (`f.c`) AND "% of Total Risk" (`f.risk_contr`). DATA PROBE confirms they are DIFFERENT metrics (different denominators) but `f.c` is null on most factors in current data. Decision: keep both, label clearly, OR drop the null one until parser populates. PM call.
  - **Top-5 / Bot-5 securities:** default to **portfolio holdings only**. Add `[Portfolio | Benchmark | Both]` toggle. Add `[Raw Factor Exposure | TE Contribution]` toggle — Raw Exp uses `cs.raw_fac[sedol].e[i]` per-security data shipped in `data-foundation-v1`. Each security row needs a real ticker (see B113).
  - **Resolve zero-stats issue:** root cause is `f.c` null. Show `—` instead of `0` when null.
  - **NEW: factor correlation panel** (was empty placeholder). See B112.
- **Size:** L (~2–3 hours, includes new chart components, toggles, and per-security wiring through `raw_fac`).
- **Sequence:** after B109 (so Impact column carries period correctly) and ideally after B113 (so security tickers are clean).

### B112 · Factor correlation matrix in `oDrF` drill (was empty)
- **Origin:** marathon review, 2026-04-27. Currently empty card-slot in the drill modal.
- **Scope:** rolling pearson correlation between this factor's returns and every other factor's returns (or this factor's TE contribution and others — PM decides denominator). Window: 52 weeks default, configurable.
- **Data:** `hist.fac[name][].e` × `hist.fac[other][].e` rolling correlation. Pure computation; ~30 LOC.
- **Sequence:** ships as part of B111 modal rebuild.

### B113 · Parser pass-through of clean ticker (`tkr`) on every holding
- **Origin:** marathon review, 2026-04-27. User: "the security 5's table on that card will need to have the actual ticker and not the cusip [SEDOL]".
- **Scope:** today `h.t` is a mixed identifier (Level2 from CSV — Japan 4-digit ticker, US ticker, EM SEDOL, etc.). The clean user-facing ticker (e.g., `2330-TW` for TSMC, `0700-HK` for Tencent) lives in `data/security_ref.json` under the `tkr` field. `_enrich_holding()` in `factset_parser.py` already loads from `security_ref.json` for `country/currency/industry` — extend to also pass through `tkr`.
- **Blockers:** USER PLANNED to add more identifier columns (SEDOL, CUSIP, ISIN, Ticker-Region) to the source CSV in next iteration — that will make this even cleaner. Until then, `data/security_ref.json` lookup gives ~97% coverage.
- **Affects:** every tile that displays a security identifier — cardHoldings, drill modals, Top-N tables. Once `h.tkr` exists, tile renders can prefer it over `h.t` with a fallback chain.
- **Size:** S parser change + S sweep across ~6 tiles to use new field.
- **Sequence:** ship parser change first (~10 LOC), then refactor display tiles in one pass.

### B108 — *(unused; preserves the numbering visible in older docs)*

---

## 🎨 SurpriseEdge adoption — 3-phase ambition ladder (B105 / B106 / B107)

**Origin:** Deep-dive study of the SurpriseEdge v3.2.0 Tauri desktop app on user's desktop (not just the HTML report). Full catalog at `design/SURPRISEEDGE_LESSONS.md` (rewritten 2026-04-24 after direct source inspection). User asked to "match or exceed" SurpriseEdge; honest gap analysis in the doc.

### B105 · Phase 1 — "Look as sharp" [~2 hours, can ship PRE-marathon on user greenlight]
- **Scope:** pure CSS + font bundle + class additions. Zero tile-render-function edits. Preserves all 24 `.v1.fixes` states at behavior level.
- **Deliverables:**
  - Adopt SurpriseEdge palette tokens: `--bg:#0b0e14`, `--accent:#22d3ee` (cyan primary), `--univ:#6366f1` (RR's old `--pri` becomes secondary), full hex-alpha convention
  - Bundle DM Sans + JetBrains Mono woff2 files (~80 KB, copied from `~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/`); inline `@font-face`
  - `.mono` class with `font-variant-numeric: tabular-nums`, applied to every numeric cell across 24 tiles
  - 11px uppercase card-titles, 600 weight, 1.5px letter-spacing, `--textDim` color
  - `::-webkit-scrollbar` 6px themed
  - Row separators at 8%-alpha
  - Unified pill convention (border + bg + text same-color hex-alpha)
  - Two-tone wordmark + 4px vertical gradient bar header accent
- **Risks:** DM Sans is slightly narrower than system-ui — browser regression check across 24 tiles mandatory. Cyan accent replaces indigo — expected <5 semantic-context sites need review.
- **Tag:** `design-polish-v1`. Browser regression check required before push.

### B106 · Phase 2 — "Feel as sharp" [~3–4 hours, POST-marathon]
- **Scope:** interaction patterns match SurpriseEdge's feel. Some render-fn edits required.
- **Deliverables:**
  - Card toolbar: ⛶ expand / 💡 Ask AI / ℹ insight icons top-right of every card (AI/insight stub-wired initially)
  - Left-border accent (`3px solid var(--accent)`) when card has notes
  - Smart filter bar at dashboard top: SCOPE / WEEK / STRATEGY pills with 1px vertical-rule separators, search box with ⌕/✕, filter-count cyan badge, inline active-filter chips
  - Multi-select filter panel component replacing per-tile inline toggles where >5 options
  - Key Takeaways tile on Overview — auto-generated findings with pin-to-persist (upgrade path for cardThisWeek)
- **Tag:** `feel-parity-v1`.

### B107 · Phase 3 — "Meta-layer depth" [~1–2 days, POST-Phase 2]
- **Scope:** meta-layer features that make SurpriseEdge feel deep. Adds RR's historical context as distinctive twist.
- **Deliverables:**
  - Insight panel per card (toggleable `ℹ`): methodology + data lineage chips (clickable to toggle fields per tile) + manual deep link
  - Ask AI per card: side panel with tile-specific Claude prompt (tile title + methodology + lineage + audit history from AUDIT_LEARNINGS)
  - `CARD_LINEAGE` map: every tile declares which fields it reads
  - PDF manual auto-generated from the 24 audit files + deep-linkable per tile
  - Winsorize controls for outlier-sensitive tiles (cardScatter, cardMCR)
  - Lazy tile placeholders for heavy computations
  - Settings panel for Claude API key entry
- **Tag:** `depth-v1`.

### Ambition beyond — Phase 4 "Exceed" [later, per-feature tags]
- Time-travel banner when `_selectedWeek` set (distinctive RR advantage — SurpriseEdge has no historical data model)
- Strategy comparison overlay (RR has 7 strategies; SurpriseEdge has 1 universe)
- Raw factor exposure decomposition (already scoped in B102–B104 Tier 2 queue)
- Historical animation / "heartbeat" view — pure RR differentiator

### Sequencing pinned in SESSION_STATE
```
marathon → B105 → Tier 2 tiles (B102/B103/B104 adopting polish) → B106 → B107 → Phase 4
```

B105 MAY ship pre-marathon on user greenlight — lowest-risk, highest emotional payoff; marathon reviews happen on polished version.

---

## 🧩 Tier 2 tile queue — post-marathon build (B102–B104)

**Status: deferred pending review-marathon signoff of the 21 Tier-1 tiles.**
Origin: data-foundation integration closing discussion (2026-04-24). `data-foundation-v1` shipped raw_fac + security_ref enrichment into the JSON; these tiles are the dashboard surface that consumes it. Built as a cluster after marathon — each follows the Batch 1–7 tile-audit cadence (safety tag → build → verify → tag `.v1`+`.v1.fixes` → review).

**User's literal words (2026-04-24, on receiving the Excel + new CSV):**
> "when security has 2% contribution to risk from country you will be able to using that data to map which country etc. this is very important and we need to make it right."

B102 is the tile that answers that ask.

### B102 · `cardRiskByDim` — risk contribution decomposed by country / currency / industry (USER KEY ASK)
- **Origin:** INTEGRATION_BRIEF.md Phase 3b.
- **Size:** M (new tile from scratch, ~200 LOC JS + a few CSS nits)
- **Where it lives:** Risk tab. Sibling to `cardRiskFacTbl`.
- **What it does:** for the active dimension toggle (Country / Currency / Industry), aggregate every holding's `%T` (TE contribution) by the security's static category (via `security_ref` enrichment, now on every `holding.country / .currency / .industry`). Render as a sorted horizontal bar chart — largest TE contributor at top.
- **Interaction:** Click a bar → drill modal listing the contributing stocks + their individual TE contributions. Mirror `oDrFRisk` drill pattern (modal with history chart + stock list table).
- **Dimension toggle:** 3-way pill group `[Country | Currency | Industry]` — default Country. Persist selection in `rr.cardRiskByDim.dim` localStorage per viz-tile checklist.
- **Data source:** `cs.hold[]` with `h.country`, `h.currency`, `h.industry` (already populated by parser enrichment in data-foundation-v1). Fallback for the 3–7% unmapped holdings: bucket as `"Unmapped"` and surface with a small warning badge.
- **Threshold:** option to hide bars below a threshold (default 0.5% TE contrib). Slider UX similar to cardFacContribBars threshold.
- **Tests:** aggregation math (sum of bars = total `%T` ± rounding), unmapped-bucket accounting.
- **Blockers:** none — data is live.
- **Must-have on v1:** note-hook, data-col/data-sv on drill table, CSV export, plotly_click wire, themed colors, empty-state fallback, no PNG button.

### B103 · Per-security raw factor drill (in `oSt` modal)
- **Origin:** INTEGRATION_BRIEF.md Phase 3a.
- **Size:** S (~80 LOC — extending an existing modal, not new tile)
- **Where it lives:** Inside the stock-detail modal opened by `oSt(ticker)` — add a new section below the existing KPI row and above the per-factor contribution table.
- **What it does:** for the given security, show its 12 raw factor z-scores (from `strategy.raw_fac[sedol].e` with labels from `strategy.raw_fac_labels`) as a horizontal bar chart. Color by sign. Below the chart, a tiny 4-period sparkline per factor drawn from `raw_fac[sedol].hist` (monthly cadence in current sample; weekly in production).
- **Data source:** `cs.raw_fac[sedol]` — keyed by the same identifier (`h.t` / Level2) already used throughout the dashboard. Fallback for 0–7% unmapped: show "Raw factor exposures unavailable for this security" panel, don't break the modal.
- **Narrative:** this tile answers "why is this stock in the portfolio" — e.g. "+2.3σ Profitability, +1.7σ Value, -1.1σ Leverage". Complements the existing active-weight + sector + country KPIs.
- **Must-have on v1:** note-hook keyed to the holding's ticker (per the existing modal convention), hovertemplate with factor label + z-score + direction word, themed colors, sparkline tokenized via `getComputedStyle`.

### B104 · Portfolio raw-exposure aggregate — synthesis hero
- **Origin:** INTEGRATION_BRIEF.md Phase 3c.
- **Size:** M (new tile, depends on B103 landing for sparkline helpers)
- **Where it lives:** Risk tab. Could slot between `cardFacContribBars` and `cardRiskFacTbl` or as a wider full-width hero above them.
- **What it does:** weight each holding's 12 raw factor z-scores by portfolio weight → aggregate portfolio raw exposure per factor. Do the same for the benchmark (weight by `h.b` not `h.p`). The **difference** is the portfolio's *active raw factor tilt* — which should reconcile with `cs.factors[].a` (already displayed in cardFacButt / cardFacDetail / cardRiskFacTbl).
- **Payoff:** a decomposition view — "this +0.8σ Momentum tilt is driven 55% by these 5 stocks". Click a factor bar → drill listing the top-N contributing holdings with their per-security Momentum z-score + portfolio weight.
- **Math invariant:** `Σ(h.p * h.raw_fac[i]) - Σ(h.b * h.raw_fac[i])` should ≈ `cs.factors[label_at_i].a` within rounding + coverage caveat. Sanity-check on render; if divergence > 0.05σ, log a console warning (diagnostic for enrichment-miss impact).
- **Blockers:** B103 first (for the sparkline helper), coverage audit (what happens when 3–7% of holdings lack raw_fac entries — is reconciliation still meaningful?).
- **Must-have on v1:** note-hook, CSV export of contribution table, reconciliation-diagnostic, themed colors.

### After these three land
Tier 2 complete = 24 tiles at `.v1.fixes`. Second mini-marathon to sign off B102–B104. Then whatever the user wants next (production deploy, B80/B96 RED-gate resolutions, B73/B74 cross-tile refactors).

---

## B101 · Recover legacy parser-behavior test coverage [optional, low priority]
Origin: Phase 3 of data-foundation integration (commit `33b6618`, 2026-04-24). Old
test_parser.py had ~40 tests for positional parser semantics; replaced with ~17
new-API tests. If future parser refactors want tight regression nets on dedup,
weekly-date slicing, or historical multi-year logic, recover intent from the
pre-replacement commit (last valid at `0d6699a`).

---

## B88–B96 · Batch 7 non-trivials (cardAttribWaterfall · cardFacContribBars · cardTEStacked)

### cardAttribWaterfall
Origin: `tile-specs/cardAttribWaterfall-audit-2026-04-24.md`. Verdicts: GREEN/YELLOW/YELLOW. Trivial fixes (CSV export button + `exportFacAttribCsv()` helper, flex-between header chrome, "Right-click for notes" tooltip addendum) applied inline. Confirmed **NOT** a B73 or B74 site — tile consumes only `f.imp` (signed, unambiguous).

- **B88 · Factor-family week-selector awareness sweep (audit-derived)** — when `_selectedWeek` is set, cardAttribWaterfall's "Period ending" label still shows latest `current_date`. Same pattern as cardRiskHistTrends Batch 5 fix but extended to 6 factor-family tiles (cardAttribWaterfall, cardFacDetail, cardFacButt, cardFRB donut, cardFRB donut, cardRiskFacTbl trends). Parser already preserves per-period `imp` at `factset_parser.py:703`, so the data exists — render-side exposure is the gap. Either render a historical-week disclaimer banner per factor-tile, or add explicit `getSelectedWeekFacImp()` lookup.
- **B89 · "Waterfall" naming disambiguation (PM gate)** — chart is a diverging bar chart, not a running-cumulative waterfall. Either rename the card title to "Factor Return Impact" (simpler) or implement a true cumulative waterfall with totals bar (more informative). Low-risk; PM sign-off on naming convention.

### cardFacContribBars (was anonymous Risk-tab card)
Origin: `tile-specs/cardFacContribBars-audit-2026-04-24.md`. Verdicts: RED/RED/YELLOW. Trivial fixes (id `cardFacContribBars` assigned per B78 sweep, card-title tip+oncontextmenu, `plotly_click → oDrFRisk` wired, `#fb923c` tokenized → `var(--prof)` at 4 sites, non-prof bar palette tokenized via getComputedStyle `--pri`/`--pri-alt`/`--warn` + inline `hex2rgba` helper, dead `--riskFacMode` custom-prop removed, `role="radiogroup"` + `tabindex` + focus-outline, `setFacGroup` + `setFacBarAll` now intersect with threshold slider instead of silently overriding it, `FAC_PRIMARY` filter dropped from Both mode so Secondary-group selections are visible, "TE Contrib %" → "|TE Contrib %|" label clarifying magnitude-only semantic) applied inline. Deferred: CSV export, localStorage persistence (large additions pending B94/B95).

- **B90 · cardFacContribBars CSV export ("export as visible")** — toggle+threshold state means standard `exportCSV` won't target the right rows; needs `exportFacBarVisible()` that snapshots currently-rendered `_rfbData` filtered by the checkbox set. ~15 LOC. No blockers, just deferred to a design-discussion round.
- **B91 · cardFacContribBars toolbar state persistence** — `_rfbMode` + threshold + group pill + checkbox set should save to `rr.facContrib.*` localStorage and restore on `rRiskNew`. ~20 LOC. Every reload resetting the toolbar is a daily-user irritant.
- **B92 · cardFacContribBars TE-mode shadow-bar denominator ambiguity** — `devPct` shadow (factor σ / total TE * 100) and main bar (`|f.c|` = % of TE) share x-axis but are different denominators. Either remove the shadow or clarify hovertemplate (currently "Factor σ: %{x:.1f}% of TE" vs "TE Contribution: %{x:.1f}% of total TE" — denominators visually look identical but semantically differ).
- **B93 · `setFacGroup` substring match is lossy** — L3465 uses bidirectional `includes()` match → "Momentum" checkbox matches "Momentum" group AND "Momentum (Medium-Term)" partial — acceptable today but fragile when FactSet adds new factor names. Switch to explicit `FAC_GROUPS[k]` membership check against `chk.value`.
- **B94 · cardFacContribBars full-screen variant (PM gate)** — worth it for a 3-mode bar chart with toolbar state? Same FS pattern as cardScatter / cardCountry.
- **B95 · cardFacContribBars Profitability alert data probe** — `hist.fac['Profitability'][].a ?? .e` fallback: confirm `a` populated across all 7 strategies. Couples to B73/parser L468 root cause. Spurious-alert risk if `a` ever falls through to raw `e`.

### cardTEStacked (was anonymous Risk-tab card)
Origin: `tile-specs/cardTEStacked-audit-2026-04-24.md`. Verdicts: RED/RED/YELLOW. Trivial fixes (id `cardTEStacked` assigned per B78 sweep, card-title tip+oncontextmenu, `plotly_click → oDrMetric('te')` wired, empty-state write-through `el.innerHTML='No TE history'` instead of silent return, fillcolor/line rgba tokenized via `_teStackColors()` helper using `--warn`/`--cyan` + hex2rgba, rangeslider border tokenized to `--pri`, CSV export `exportTEStackedCsv()` helper) applied inline.

- **B96 · cardTEStacked `pct_specific`/`pct_factor` semantics resolution (RED — PM gate, couples B74 scope)** — per `CSV_STRUCTURE_SPEC.md` L184, `pct_specific`/`pct_factor` are **"% of Total Risk, not % of TE"** but render at L3253 multiplies by `h.te` as if TE-shares. If CSV spec is authoritative, the stacked-area decomposition is mathematically wrong under `sqrt` assumption (Total Risk decomposes as variance, not as linear TE-shares). Fix depends on PM+parser-team decision: (A) trust the CSV's % semantics and render over Total Risk axis instead of TE, (B) recompute factor+specific TE from parser-side variance budget, (C) add disclaimer that current chart uses linear allocation proxy. Parallels B74's factor-tile-semantics cleanup family. Highest-impact Risk-tab data finding in Batch 7.
- **B97 · cardTEStacked `_selectedWeek` vertical marker (cross-tile design-lead gate, links B70)** — no vertical shape drawn when `_selectedWeek` is set. Same unified design decision as B70 (cardRiskHistTrends). Scope-merged with B70 once design lands.
- **B98 · Rangeslider state persistence** — user drags slider → navigates away → returns to Risk tab → range resets. Save `xaxis.range` post-relayout to `rr.teStacked.range` and restore on next render.
- **B99 · `factorRisk`/`idioRisk` heuristic audit (new cross-tile)** — fallback values built at `rRisk()` L3014 are a heuristic (`Σ|f.c|/100 * 1.2`, capped 0.85) used when `pct_*` missing. Every downstream consumer of these vars (cardTEStacked, riskDecompTree, potentially cardFRB) inherits the fudge coefficient silently. Audit every reader and either disclaim the heuristic nature in the UI or compute from a sounder base.
- **B100 · `--idio` / `--factor` palette tokens (design-system gate)** — amber/cyan split used by cardTEStacked + future decomposition tiles. Promote to shared `--idio:#f59e0b` / `--factor:#06b6d4` tokens so downstream consumers (riskDecompTree, Risk tab hero future variants) inherit consistently.

---

## B79–B87 · Batch 6 non-trivials (cardBenchOnlySec · cardUnowned · cardWatchlist)

### cardBenchOnlySec
Origin: `tile-specs/cardBenchOnlySec-audit-2026-04-23.md`. Trivial fixes (card-title note-hook, PNG button removed, `data-col` on 4 ths+tds, sort wiring + `data-sv` on Biggest Missed col 3, tooltip on col 3 th) applied inline.

- **B79 · Rename "% of benchmark missed" suffix (PM gate)** — Label ambiguity (same denominator-clarity family as factor "% of TE vs % of factor risk"). `totalMissed` = Σ `h.b` for bench-only holdings = **% of total benchmark weight** not held. Suggest: `"${f2(totalMissed,1)}% bench wt not held"`. PM sign-off on label. Trivial once approved (~1 line).

### cardUnowned
Origin: `tile-specs/cardUnowned-audit-2026-04-23.md`. Trivial fixes (card-title note-hook, `data-col` + `data-sv` null-guards, sort null-guard `Math.abs(b.tr||0)-...`, ticker escaping in drill invocation, region label lookup `Usa→USA · English→UK · Far East→Asia Pacific ex-Japan`, header tooltips on Bench Wt% + TE Contrib, defensive fallback `u.b??u.bw` and `u.tr??u.pct_t`, TE column color softened from hardcoded `--neg` to neutral `--txth` given empty data) applied inline.

- **B80 · Unowned Risk Contributors has no data source (RED — blocks entire tile)** — Data probe across all 7 strategies: `bw=null`, `pct_t=null`, `pct_s=null` on 100% of rows (22 rows total). Parser's `_extract_security` L577–644 partitions to `unowned` bucket iff `w`/`bw`/`aw` ALL None — so by construction these rows carry no weight and no TE. The "stocks not held that contribute most to TE" narrative is aspirational; actual bucket is orphan securities / rights / detached cash (e.g. `"Worldline SA Rights 2026-27.03.2026"`, `"Great Eagle (Detached 2)"`). Three options: (A) parser change to extract a real unowned-benchmark-TE feed from a different FactSet CSV section — adds to the pending-FactSet questions list; (B) hide the tile entirely until source is wired; (C) rename to "Unattributed Benchmark Rows" and drop TE/weight columns it can't populate. PM gate — blocks B81/B82/B83 cosmetics.
- **B81 · Pattern B variant: `normalize()` skips `st.unowned` rows** — L562–L573 maps `hn.b ?? hn.bw ?? 0` and `hn.tr ?? hn.pct_t ?? 0` for holdings only. `st.unowned` rows retain parser's `bw`/`pct_t` key names. Render read `u.b`/`u.tr` was silently `undefined` before the Batch 6 defensive fallback. Permanent fix: mirror the holdings field-name remap inside the unowned loop (2-line patch at L562). Ships together with B80 once source is decided.
- **B82 · Drill modal `oDrUnowned` narrative guard** — `oDrUnowned` L5475 hardcodes `"This stock has a ${f2(u.b)}% weight in the benchmark..."` which renders as `"This stock has a — % weight..."` for every current row. Guard with `isFinite(u.b)?normal:'No weight data available for this security.'`. Deferred until B80 resolves.
- **B83 · Sign-color semantic on TE Contrib column (4th sign-collapse site — links B74)** — Static `color:var(--neg)` was the 4th member of the sign-collapse family. Softened to neutral `var(--txth)` as Batch 6 trivial; permanent policy (magnitude-always-red vs signed vs neutral) rolls into B74 shared-helper decision.

### cardWatchlist
Origin: `tile-specs/cardWatchlist-audit-2026-04-23.md`. Trivial fixes (per-section `<table id="tbl-watch-{key}">`, `<thead>` with sortable `<th>` + per-column tooltips, `data-col` + `data-sv` on every cell, CSV export via new `exportWatchlistCsv(sid)`, empty-state shell with onboarding copy instead of invisible-until-populated, exited-ticker detection with muted row + `EXITED` chip, `cycleFlag` now re-renders `#cardWatchlist` in place, card-title note-hook + card-title tooltip, `FLAG_COLORS` tokenized `#f59e0b/#ef4444/#10b981` → `var(--warn/--neg/--pos)`, isCash filter, name-cell `data-sv` lowercase + `title=` hover, ticker escaping in `oSt` drill) applied inline.

- **B84 · Row-hover remove (×) affordance (trivial-ish deferred)** — Per-row hover-reveal `×` button that calls `delete _holdFlags[t]; saveHoldFlags(); re-render`. Ships after PM confirms user wants in-tile remove vs the existing "cycle `⚑` three times to clear" path from Holdings tab.
- **B85 · Threshold shading on watchlist Active % cell** — Apply the cardSectors `thresh-alert` (`|a|>5`) / `thresh-warn` (`|a|>3`) classes for visual parity with other tables. Deferred because watchlist is a flag-curated view and threshold semantics may differ — PM call on whether to signal risk-size of flagged positions.
- **B86 · Cross-strategy flag sharing (PM gate)** — Current `rr_flags_${s.id}` per-strategy scoping means a watchlist entry in IDM doesn't appear when switching to ISC. Arguably a ticker watched on one mandate often deserves watching on related mandates. PM: keep per-strategy isolation, or add a "shared" vs "strategy-local" toggle on each flag?
- **B87 · Merge Watch/Reduce/Add into single sortable table (PM gate)** — Current layout is three stacked sections with their own `<thead>`. Alternative: one table with a Flag column (`⚑ ▼ ▲` icons), fully sortable, denser. Loses narrative grouping; gains scanability for larger watchlists. PM decision.

---

## B73–B78 · cardRiskFacTbl non-trivials
Origin: `tile-specs/cardRiskFacTbl-audit-2026-04-23.md`. Trivial fixes (header rename Exposure→Active Exposure, tip+oncontextmenu, per-column data-tips, empty-state fallback, data-col on every th+td, drill annotation fix with a-fallback chain + y-axis relabel "Active Exposure", legacy alias `rRiskFacBars` dropped) applied inline.

- **B73 · Active-vs-raw unification (3rd site — escalates to cross-tile refactor; supersedes B53)** — cardFacDetail L1764 + cardCorr L2168 + cardRiskFacTbl (in-row divergence: Exposure cell renders `f.a` while Trend sparkline falls through to raw `h.e` whenever `h.bm==null`, which is always on riskm path per parser L468 `bm: None`). Decision needed globally: always active (`e−bm`), always raw, or expose `[Active|Raw]` toggle. Ripples: 3 tile renders + 1 drill + parser labelling. Highest-leverage single Risk-tab PM decision. Parser-side sub-fix: populate `bm` in riskm path via `bm=e-a` algebra (one line at factset_parser.py:468).
- **B74 · Sign-collapse policy on risk-budget views (4th site — escalates; supersedes scope of existing cardFRB Math.abs items)** — cardFRB L2696 + `oDrRiskBudget` L5389 + Risk Decomp Tree L2770 + cardRiskFacTbl MCR-to-TE L2996 + drill KPI L3526. PM gate: if keeping magnitude, colorize direction separately (stripes/icon/sign prefix); if preserving sign, reconcile with the "risk-budget always sums to 100%" narrative. Extract a shared `mcrSigned(f,totalTE)` helper when policy lands.
- **B75 · Consolidate `oDrF` + `oDrFRisk` drills** — L5513 vs L4216, ~150 LoC duplication; nearly identical modals with slightly different KPI cards. PM: two drills (Attribution-focused vs Risk-focused) or one unified modal with a context-toggle?
- **B76 · Risk-tab `_selectedWeek` awareness** — `rRisk()` L3048 never consults `getSelectedWeekSum()`; `cs.factors` is always latest, but `cs.hist.fac` is populated and could source a historical-week snapshot. PM: replay historical factor exposures when selecting a past week, or stay latest with disclaimer?
- **B77 · Primary/All toggle on cardRiskFacTbl** — mirror cardFacDetail `_facView` state; shared with group pills and `FAC_PRIMARY`. Most Risk-tab sibling bars filter to primary (L3332/L3342); table shows all. PM: default all or default primary?
- **B78 · Standardize Risk-tab card note-hooks (anonymous-cards sweep)** — Factor Contributions bars L3087, Factor Exposure History L3164, Factor Correlation Matrix L3177 (live cardCorr), TE Stacked Area L3070 all lack stable ids + `class="tip"`/`oncontextmenu` hooks. Batch assign. Mechanical sweep.

---

## B69–B72 · cardRiskHistTrends non-trivials
Origin: `tile-specs/cardRiskHistTrends-audit-2026-04-23.md`. Trivial fixes (tip+oncontextmenu, per-metric hovertemplate units, themed `--pri`/`--acc`/`--cyan`/`--txt` via getComputedStyle + hex2rgba fill, short-history placeholder in mini divs, `_selectedWeek`-aware cur/prev index, Holdings card drill via `oDrMetric('h')`, per-metric `rangemode:'normal'` for Beta/AS — `'tozero'` kept for TE/Holdings, raised noise floor `>0.05` TE/AS and `>0.005` beta) applied inline.

- **B69 · Beta `dir:'from1'` coloring (PM gate)** — Beta has a canonical reference at 1.0; rising beta above 1 = procyclical. Current `dir:'neutral'` gives no narrative direction. Flip to `dir:'from1'` → red as |beta−1| grows, green as it shrinks. PM call on whether to match cardThisWeek's beta bullet framing.
- **B70 · Vertical week-selector marker (cross-tile design-lead gate)** — when `_selectedWeek` is set, draw a vertical marker/shape on all 4 mini-charts at that date. Same treatment would apply to `rMultiBeta` + `teStackedArea`. Unified design decision: marker-only, marker-plus-faded-future-region, or full-range-dimming?
- **B71 · Recent-vs-All range toggle** — 3-year files dilute recent TE spikes against 156 weeks of history. Simplest: `[Last 52w | All]` 2-state toggle. Alternative: full 3M/6M/1Y/3Y/All bar matching `oDrMetric`. PM: how much history should glance-view show by default?
- **B72 · CSV export of `hist.summary`** — no `<table>` in this tile, so need a helper tweak to `exportCSV` to accept a data array, or render hidden `<table id="tbl-risk-hist">` and wire existing `exportCSV`. ~15 LOC.

---

## B61–B68 · cardGroups non-trivials
Origin: `tile-specs/cardGroups-audit-2026-04-23.md`. Trivial fixes (card-title tip + oncontextmenu, threshold row classes via `activeStyle(g.a)`, **dead-drill fix via `h.subg === groupName`** replacing broken `GROUPS_DEF + SEC_ALIAS` sector-match at `oDrGroup` L5464, `data-sv=""` on null rank cell, tokenize `#334155`→`var(--txt)`, PNG dropdown item removed from download menu, `plotly_click → oDrGroup` on chart, `data-col` on every th+td, R/V/Q header tooltips) applied inline.

- **B61 · Render recomputes ORVQ ranks via wrong (non-exclusive) GROUPS_DEF taxonomy (RED PM gate)** — `rGroupTable` L1895–L1918 accumulates O/R/V/Q from `cs.hold` via `GROUPS_DEF + SEC_ALIAS` where Info Tech, Materials, Energy, Health Care map to TWO subgroups each. Result (ACWI): **HARD CYCLICAL renders Q1 (green, "best") — FactSet authoritative value is Q3 (amber, mid)**; COMMODITY Q1 vs Q2; BOND PROXIES and SOFT CYCLICAL render ranks where FactSet returns null. Same PM-facing severity class as cardScatter `h.mcr` mislabel. Fix options: (a) consume `cs.groups[].over/rev/val/qual` directly (drops hold-loop; static-Wtd only); (b) keep loop but filter by `h.subg === gn` (enables `_secRankMode` toggle; matches parser values exactly in Wtd mode). PM picks policy.
- **B62 · `hist.grp` pipeline (batch with B6 / `hist.reg`)** — parser `factset_parser.py:834-839` hardcodes `hist:{summary,fac,sec:{},reg:{}}` — no `grp` key. Blocks cardGroups sparkline column + `oDrGroup` historical chart + range selector. Same shape as B6 (hist.reg) — ship together as "hist.geo/grp/reg parser pass".
- **B63 · `oDrGroup` drill parity uplift** — mirror `oDr('sec',n)`: historical chart (needs B62), range selector, rank distribution, factor tilt summary, bench-only holdings section (addable today without deps — useful because BOND PROXIES / SOFT CYCLICAL have p=0 b>0 and bench-only rows fall off the top-15 truncation).
- **B64 · Rank-mode toggle per tile (conditional on B61 resolution path)** — if PM picks B61(b), `_secRankMode` toggle needs per-tile state so cardGroups can bucket exclusively while cardSectors stays weighted-portfolio. Re-raise only if (b) lands.
- **B65 · cardTreemap Group-by toggle unblock** — cardTreemap D1 silent-dead because prior audit believed `h.subg` was unpopulated. **Updated ledger (see AUDIT_LEARNINGS): `h.subg` IS populated (~85% of non-cash holdings).** One-line fix: `buckets[h.subg||'Other']`. Supersedes B38 (`enrichHold` from GROUPS_DEF) — no parser change needed.
- **B66 · PNG removal sweep (cross-tile)** — user pref "no PNG on RR tiles" (MEMORY). Known offenders remaining: cardRegions download menu, probably cardTreemap dropdown, potentially cardCorr and cardRating. Low-risk single-session sweep.
- **B67 · Keyboard a11y sweep (cross-tile)** — `tabindex="0"` + `role="button"` + `onkeydown` on all `.clickable` rows and `.card[onclick]`. Batch across sectors/countries/regions/groups/ranks tiles when PM prioritizes.
- **B68 · GROUPS_DEF vs h.subg reconciliation memo (blocks B61 + closes taxonomy ambiguity)** — document: is Redwood's taxonomy the GROUPS_DEF overlap view (Info Tech in both GROWTH and GROWTH CYCLICAL) or FactSet's exclusive SEC_SUBGROUP view (each holding in one bucket)? Current code is schizophrenic: rank loop uses overlap, drill holdings-list uses sector membership of overlap groups (broken per T3 prior to this batch), `cs.groups[].p/b/a` are exclusive (sum to ~97%). Upstream cause of B61. PM decision memo needed before B61 lands.

---

## B53–B60 · cardCorr non-trivials
Origin: `tile-specs/cardCorr-audit-2026-04-23.md`. Trivial fixes (themed colorscale via `--pri`/`--neg`/`--txth`, CSV export `exportCorrCsv()`, threshold externalization to `_thresholdsDefault.corrHigh/corrDiversifier`, pearson null-when-n<3 + "—" cell text, insight-factor `oDrF` drill links, localStorage save/restore of period/freq/facs, monthly dedupe inline-comment, min-history filter `>=3`, note popup, data-tip on live card-title, ghost `screenshotCard` PNG button removed) applied inline.

- **B53 · Active-vs-raw exposure policy (cross-tile)** — `rUpdateCorr` L2168 correlates raw exposure `e` but the Risk-tab UX implies **active** exposure (`e−bm`). Same conflation already confirmed at cardFacDetail L1764. PM gate: unify on one field, or expose `[Active|Raw]` toggle on both tiles. Whichever lands, the tile rename (B60) follows.
- **B54 · Date-aligned pearson** — current pearson aligns by array index, not by date. Any factor with missing observations on some weeks shifts the alignment for that pair. Build per-factor `{date→value}` Maps, intersect dates pairwise, then compute. ~25 LOC.
- **B55 · Half-triangle toggle** — symmetric matrix redundantly renders both halves. Add `[Full | Upper]` toolbar toggle; upper-triangle view halves visual noise on 20+ factor grids. ~10 LOC.
- **B56 · Factor-pair drill** — click a cell → open a modal with the two factors' exposure series + correlation over time. Re-uses `oDrF` rendering patterns. ~60 LOC + PM call on modal layout.
- **B57 · Full-screen variant (`renderFsCorr`)** — 20+ factors cramped at tile size. Mirror `renderFsScatter`. ~50 LOC.
- **B58 · Id on live Risk-tab card** — anonymous card at L3096 wraps the real heatmap; `id="cardCorr"` currently belongs to the ghost placeholder (L1299). Deferred pending B59 disposition. ~2 LOC once B59 lands.
- **B59 · Ghost tile disposition (PM gate)** — `#cardCorr` at L1299 is a named placeholder whose innerHTML is never set. Options: (a) delete, (b) promote to a second (Exposures-tab) correlation view, (c) rename ghost + give live card its own id. Blocks B58.
- **B60 · Tile rename (post B53)** — once active-vs-raw resolves, rename card title to match ("Active Factor Correlations" vs "Factor Exposure Correlations"). ~2 LOC.

---

## B45–B52 · cardAttrib non-trivials
Origin: `tile-specs/cardAttrib-audit-2026-04-23.md`. Trivial fixes (waterfall card id `cardAttribWaterfall`, tip+oncontextmenu on both card titles, `isFinite(f.imp)` filter, waterfall height cap `min(900,max(160,N*32)+20)` + overflow-y, themed bar colors via `--pos`/`--neg`, `data-col`/`data-sv` on attrib table, `plotly_click → oDrAttrib` on attrib bar, subtitle "Click any row or bar for time series") applied inline.

- **B45 · `full_period_imp` semantics** — parser emits a single "full period" impact column whose window is implicit. Surface the window (e.g. "trailing 13 weeks") in the subtitle + tooltip. PM gate on exact phrasing.
- **B46 · Week-selector awareness** — `rAttribTable` and `rFacWaterfall` silently show latest when `_selectedWeek` is set. Either hide with banner or render the selected-week slice. Same shape as B19/B43.
- **B47 · `classifyAttrib` heuristic → explicit enumeration** — regex-based factor-family classifier is fragile; move to explicit `FAC_GROUP_DEFS` lookup. Parallel to B10.
- **B48 · Two bar charts visual distinguishability** — `cardAttribWaterfall` (bars by factor contribution) and attrib bar inside `cardAttrib` render nearly identically. PM call: retitle, reorder, or merge. ~15 LOC + PM.
- **B49 · Factor-name escaping in onclick handlers** — `oDrAttrib('${name}')` breaks on names with apostrophes. Use `data-factor` attribute + delegated listener. ~10 LOC.
- **B50 · Top-20 / top-10 cap policy** — waterfall caps at 20, table caps at 10, tile-subtitle implies "full". Expose as `[Top 10 | Top 20 | All]` toggle. ~15 LOC.
- **B51 · Keyboard handler on attrib modal** — Esc-to-close + arrow-key nav through factor rows. Mirror holdings modal pattern. ~15 LOC.
- **B52 · Per-week drill on weekly-bars chart** — bars are clickable at week level but drill isn't wired. `plotly_click → selectWeek(bar.x)`. ~10 LOC.

---

## B39–B44 · cardMCR non-trivials
Origin: `tile-specs/cardMCR-audit-2026-04-23.md`. Trivial fixes (themed `--pri`/`--pos` via getComputedStyle, zeroline, PNG removed + `exportMcrCsv()` added, `plotly_click → oSt(ticker)`, tip+oncontextmenu note popup, top-bottom disclaimer in subtitle) applied inline.

- **B39 · MCR domain rename — paired with B20 (cardScatter)** — `h.mcr` is FactSet `%S` (stock-specific TE), not true marginal contribution to risk. Must land atomically across cardMCR + cardScatter + full-screen `renderFsScatter` + any sibling drill. PM gate: (a) rename to "Stock-Specific TE" / "Idiosyncratic Risk" end-to-end, or (b) document "MCR = stock-specific TE contribution" as PM shorthand. Recommend (a). Highest-value Batch 4 PM gate.
- **B40 · Negative %S narrative** — some holdings have negative `h.mcr` (short/hedge). Current tile renders them in green but without explanation. Add hover-text line "Negative MCR = position reduces portfolio TE (hedge/short)." ~5 LOC + PM copy.
- **B41 · Color-semantic unification** — tile colors top bars indigo (positive MCR) and bottom bars green (negative/risk-reducing); full-screen sibling inverts green/red. Same class of tile↔FS drift as cardScatter (B21). Unify or expose mode toggle.
- **B42 · Full-screen variant (`renderFsMCR`)** — 10 bars cramped on large monitors; siblings all have ⛶. Preserve ordering + axis labels. ~60 LOC.
- **B43 · Week-selector disclaimer** — MCR always renders latest holdings (no per-week MCR history). Subtitle hints at this but not visibly during historical week view. Add banner when `_selectedWeek` ≠ latest. ~10 LOC.
- **B44 · CSV extension beyond top-10** — `exportMcrCsv()` currently emits only the rendered top-10+bottom-10. Extend to full holdings MCR table with opt-in via second button or modal. ~10 LOC.

---

## B34–B38 · cardTreemap non-trivials
Origin: `tile-specs/cardTreemap-audit-2026-04-21.md` §7. Trivial fixes (note popup, theme tokens for active-sign color, `_treeDrill=null` on strategy switch) applied inline; toolbar-class adoption (B27 in audit) deferred as low-risk visual change for review marathon.

- **B34 · Full-screen variant** — 360px is cramped for Country/80-bucket views; siblings all have ⛶. Must preserve Dim/Size/Color/Drill state. ~60–100 LOC mirroring `renderFsCountryMap`.
- **B35 · Bucket → sector/country detail modal (`oDr`) route** — user clicking "Financials" expects the gold-standard sector drill. Needs PM UX call (shift-click? breadcrumb button? context menu?). ~20 LOC + PM decision.
- **B36 · CSV export of bucket table** — `{label, count, wt, active, te, avgRank}`. ~15 LOC + new `exportTreeBuckets()` helper.
- **B37 · Toolbar state persistence to localStorage** — `_treeDim/_treeSize/_treeColor/_treeDrill`. Pattern: `rr.tree.*`. PMs using daily expect sticky. ~10 LOC.
- **B38 · Populate `h.subg` in `enrichHold` using GROUPS_DEF** — the "Group" toggle button is silently dead because `h.subg` is never populated (parser maps from a non-existent `SEC_SUBGROUP` column). PM gate on GROUPS_DEF overlap resolution (first-match heuristic vs multi-attribution). ~6 LOC + PM call.

---

## B29–B33 · cardRanks non-trivials
Origin: `tile-specs/cardRanks-audit-2026-04-21.md` §7.

- **B29 · Consume FactSet pre-aggregated rank tables as source-of-truth** — parser extracts `ranks.{overall,rev,val,qual}[{q,w,bw,aw}]`; `normalize()` L612 discards and rebuilds from holdings. Unblocks REV/VAL/QUAL sibling tiles (high value). Adds holdings-vs-FactSet divergence telemetry. ~30–50 LOC across parser + normalize + rRnk. Highest-value cardRanks item.
- **B30 · "Unranked holdings" affordance** — holdings with `h.r==null` silently fall out of every quintile. Surface as 6th row or subtitle. ~10 LOC + PM call on format.
- **B31 · Robust tab navigation in `filterByRank`** — replace magic `querySelectorAll('.tab')[2]` + `setTimeout(100)` with symbolic lookup + proper render callback. ~15 LOC.
- **B32 · Filter preservation on rank-drill** — current `ah=[...cs.hold]` clobbers any pre-existing Holdings-tab sector/search filter. PM call on whether preserve or intentional reset. ~20 LOC.
- **B33 · Drill breadcrumb / exit affordance** — visible "Filtered: Q3 (clear)" chip on Holdings tab when navigated from rank-drill. ~15 LOC.

---

## B20–B28 · cardScatter non-trivials
Origin: `tile-specs/cardScatter-audit-2026-04-21.md` §11. Trivial fixes (isFinite filter, theme-aware colors, opacity, 9px label, zeroline, widen right margin, plotly_click→oSt drill, CSV export replacing PNG, note popup, rewritten hover + axis + tooltip text) applied inline. T11 "MCR" rename deferred as PM-gated.

- **B20 · "MCR" axis-label domain rename** — `h.mcr` is FactSet `%S` (stock-specific TE), NOT marginal contribution to risk. PM gate: (a) rename to "Stock-Specific TE" / "Idiosyncratic Risk" end-to-end, or (b) keep "MCR" as PM shorthand + document. Recommend (a). Ripples: card title L1254, tooltip, `renderFsScatter` L5632. Same bug likely on cardMCR — audit next.
- **B21 · Color-semantic unification tile ↔ full-screen** — tile colors by continuous active weight; full-screen colors by quintile rank. Two legit views but inconsistent. Add color-mode toggle `[Active|Rank|Sector]` in both. ~30–50 LOC.
- **B22 · Historical scatter (per-holding history)** — blocked: parser doesn't persist per-holding history. No week-selector drill possible. Parser change needed.
- **B23 · Quadrant annotations + portfolio-average crosshair** — requested in phantom spec 2026-04-13, never landed. Highest-PM-value chart addition. ~80 LOC.
- **B24 · Axis toggle (MCR/Return, Exp/Vol, ActWt/TE)** — blocked on per-holding return from FactSet. Phantom-spec item.
- **B25 · Label thinning + sizeref normalization** — `mode:'markers+text'` overlaps into mush on 80+ holdings. Thin to top-N by `|tr|`. PM call on N (~20–30). ~15 LOC.
- **B26 · Full-screen panel table → standard primitives** — `<table id>`, sortable `<th>`, CSV export. Primitives checklist applied to modal panel. ~20 LOC.
- **B27 · Shared `RANK_COLORS` palette helper** — `[#10b981, #34d399, #f59e0b, #fb923c, #ef4444]` duplicated in cardTreemap L2597 + FS scatter L5623 + FS panel L5659. Zero-behavior refactor. Folds into / supersedes earlier B9 (factor-palette canonicalization) — consolidate under one ticket when scheduled.
- **B28 · Phantom-spec quarantine rule** — institutionalize in AUDIT_LEARNINGS: any `tile-specs/*.md` whose contents begin with JSONL gets renamed `*.phantom-DATE.md` on sight. Two phantom specs identified so far (cardChars, cardScatter).

---

## B19 · cardFRB — week-selector awareness
- **Origin:** `tile-specs/cardFRB-audit-2026-04-21.md` §7
- **Size:** S (~20 lines)
- **Blockers:** none on latest week; historical weeks only have `hist.sum` — factor-contribution slices unavailable pre-current-week.
- **Notes:** When `_selectedWeek` ≠ latest, either hide FRB with a "(latest week only)" banner or render a greyed-out snapshot. Parallel to B4.

## B18 · cardFRB — hover/focus affordance on clickable card
- **Origin:** cardFRB audit §7
- **Size:** XS (~5 lines CSS)
- **Blockers:** none
- **Notes:** `.card[role=button]:hover{box-shadow:...}` + focus ring. Applies to cardFacButt too (same pattern).

## B17 · cardFRB / factor drill — sortable + drillable detail table
- **Origin:** cardFRB audit §7
- **Size:** S–M (~60 lines)
- **Blockers:** none
- **Notes:** `oDrRiskBudget()` currently renders static summary. Upgrade: sortable table with factor name / TE contribution / direction / share-of-factor-risk; row click → `oDrF(factorName)`. Pattern mirrors existing `rFacTable`.

## B16 · cardFRB — CSV export
- **Origin:** cardFRB audit §7
- **Size:** XS (~10 lines)
- **Blockers:** none
- **Notes:** Add `CSV` export button pattern from neighbor tiles; export `[factor, contribution, direction]`. Hidden-table + `exportCSV` pattern.

## B15 · cardRegions — Spotlight two-row header parity
- **Origin:** `tile-specs/cardRegions-audit-2026-04-21.md` §7
- **Size:** S (~25 lines)
- **Blockers:** decision on whether to expose `rankToggleHtml3` for regions (shared `_secRankMode` with sectors — may be appropriate or may be confusing).
- **Notes:** The reg-branch table at rWt renders R/V/Q as plain columns. The sec-branch wraps them with a "Spotlight / Wtd·Avg·BM" two-row header. Parity would make the ranks discoverable and mode-switchable.

## B14 · Region column-picker
- **Origin:** cardRegions audit §7
- **Size:** S (~30 lines)
- **Blockers:** none
- **Notes:** Regions table has no column-visibility toggle (unlike sectors). Add `applyRegColVis()` + a small gear/eye toggle. Low priority — regions have fewer columns.

## B13 · CMAP drift telemetry
- **Origin:** cardRegions + cardFacDetail audits (cross-tile)
- **Size:** S (~20 lines)
- **Blockers:** none
- **Notes:** Multiple tiles read CSS vars in JS (`getComputedStyle(...).getPropertyValue('--pos')`). If a token is removed/renamed the fallback silently activates. Add a startup check that warns to console if any expected var is empty.

## B12 · Sparkline active-vs-raw mode when no bench
- **Origin:** cardRegions audit §6 (inlineSparkSvg)
- **Size:** XS (~10 lines)
- **Blockers:** none
- **Notes:** `inlineSparkSvg` plots `.a` (active weight). For strategies with no/low bench coverage, `.a` ≈ `.p`. Tooltip or line styling could indicate this. Low priority.

## B11 · Profitability-decrease threshold → `_thresholds`
- **Origin:** cardFacDetail audit §7
- **Size:** XS (~3 lines)
- **Blockers:** none
- **Notes:** Hardcoded `-0.05` σ threshold for Profitability-warn span lives in `facRow`. Should move to `_thresholdsDefault` as `profitabilityWarnSigma`.

## B10 · Factor primary/secondary regex → explicit enumeration
- **Origin:** cardFacDetail audit §7 (AUDIT_LEARNINGS cross-tile)
- **Size:** XS (~5 lines)
- **Blockers:** none
- **Notes:** `/momentum/i.test(f.n)` in `rFacTable` is a regex workaround for FAC_PRIMARY set miss. Replace with explicit `FAC_PRIMARY` population at config time. Fragile as-is.

## B9 · Factor-group palette canonicalization
- **Origin:** cardFacDetail + cardFRB + cardFacButt audits (cross-tile)
- **Size:** S (~25 lines CSS + JS)
- **Blockers:** none
- **Notes:** Factor-group hex colors (indigo, amber/prof, etc.) are duplicated across `FAC_GROUP_DEFS`, `.fgp` CSS, cardFacDetail row borders, FRB labels. Consolidate into a `--fac-*` CSS-var suite + single source of truth in `FAC_GROUP_DEFS`. Shared CSS additions in this batch (`--prof`, `--fac-bar-pos/neg`) are a first step; finish the job.

## B8 · Weekly-append ingestion automation
- **Origin:** HANDOFF.md §7, user direction 2026-04-20
- **Size:** M (parser change + trigger wiring)
- **Blockers:** Redwood IT confirmation of server layout + drop-folder path
- **Notes:** `factset_parser.py --append existing.json new_week.csv`. Idempotent by `report_date`. Trigger TBD (file-watcher vs cron). Dashboard side auto-updates via existing `refreshDataStamp()` at dashboard_v7.html:709.

## B7 · Frontend Playwright smoke test
- **Origin:** HANDOFF.md §9 (gotchas / test coverage gap), SurpriseEdge lessons extraction
- **Size:** ~1 day
- **Blockers:** none
- **Notes:** Load a known `portfolio_data.json`, assert every `.card[id]` renders, assert zero console errors, assert every Plotly div has content. Unblocks confident auto-append rollout.

## B6 · Trend sparklines on countries / groups / regions
- **Origin:** AUDIT_LEARNINGS.md Known blockers
- **Size:** M (parser change)
- **Blockers:** parser doesn't persist `hist.country` / `hist.grp` / `hist.reg`
- **Notes:** Parallel blocker structure to B2. When one is unblocked, both should ship together.

## B5 · cardFacButt polish pass
- **Origin:** `tile-specs/cardFacButt-audit-2026-04-21.md` §7 non-trivial queue
- **Size:** S–M (~100 lines total)
- **Blockers:** none (PM preference on a couple)
- **Items:**
  - CSV / Copy-to-clipboard export (hidden-table + exportCSV pattern)
  - Honor sibling `cardFacDetail` Primary/All toggle (tile-to-tile state sync)
  - Factor-group coloring mode toggle (`facGrpColor(f.n)` already exists)
  - Duplicate or move full-screen ⛶ button onto this card (currently lives on neighbor)
  - PM call: within-card color scheme — bars+strip indigo/violet, or both pos/neg?

## B4 · cardThisWeek — week-selector-aware "Picked week" narrative
- **Origin:** User decision 2026-04-21 (Q2), cardThisWeek-audit §7 #3
- **Size:** S–M (~50–80 lines)
- **Blockers:** Two-layer history architecture — historical weeks only have `hist.sum` (TE/AS/Beta/H/cash), no sectors/holdings/factors. S2/S3/S4/S5 bullets can't render fully for historical weeks.
- **Notes:** User direction: "keep the current week up top and then show the picked week narrative in a way that is clearly marked". Approach: render existing `thisWeekCardHtml(s)` as always (latest). When `_selectedWeek` is set and is NOT the latest, render a second narrative block below, clearly banner-labeled "Picked week: April 14" or similar, with whatever subset of bullets the historical data supports (C1–C4 deltas, S1/S6 from `hist.sum`, skip S2–S5 or show as "(latest week only)").

## B3 · cardThisWeek — inline drill links on all 11 bullets
- **Origin:** `tile-specs/cardThisWeek-audit-2026-04-21.md` §7 #1
- **Size:** S (~30 lines)
- **Blockers:** none
- **Notes:** Every bullet subject has a natural existing modal. Pattern: wrap `<strong>` in `<a onclick="oSt(ticker)">` etc. with `cursor:pointer;text-decoration:underline dotted`.
  - S1 / C1 → `oDrMetric('te')`
  - S2 / S3 → `oDr('sec', name)`
  - S4 / C5 → `oSt(ticker)`
  - S5 → `oDrFacRiskBreak()`
  - S6 → `oDrMetric('cash')`
  - C2 → `oDrMetric('as')`
  - C3 → `oDrMetric('beta')`

## B2 · cardChars — historical sparklines
- **Origin:** Phantom spec salvage (task 5), `cardChars-audit-2026-04-21.md` §11 non-trivial #15
- **Size:** M (parser change + UI)
- **Blockers:** parser overwrites `sum.mc/roe/...` each pass. Needs per-week chars persistence: `s.hist.chars[metricName] = [{d,p,b},...]`
- **Notes:** Ships together with B6 if both unblocked by the same parser change.

## B1 · cardChars — grouping + deviation bars + top-3 + profile pills
- **Origin:** Phantom spec salvage (user direction 2026-04-21 Q1 — "take the main stuff that would still be applicable and add it to the queue then delete")
- **Size:** S (~165 lines total, all CSS+JS, no data change)
- **Blockers:** none
- **Items (still-applicable features extracted from deleted phantom spec):**
  - **Metric grouping** (Risk / Valuation / Growth / Quality) — add `CHR_GROUPS` config + classifier + group-header rows (~60 lines)
  - **Inline deviation bars** in Diff column (`.chr-devbar` CSS + bar-render inside cell, driven by `maxAbsDiff`) (~40 lines)
  - **Top-3 highlighting** (sort by `|diff/b|`, tag top 3 rows with `.chr-top3`) (~15 lines)
  - **Portfolio Profile summary pills** above table ("Growth-tilted · Small-cap bias · Quality overweight") — threshold-based classifier emitting 2–4 colored pills (~50 lines)
- **Discarded from phantom spec:**
  - Historical sparklines → separate item B2 (blocked on parser)
  - Misleading card-title tooltip → handled as trivial in Batch 1 fixes
  - `screenshotCard('#cardChars')` PNG button → removed as trivial in Batch 1 fixes

---

## Shipped
*(move items here with date + commit hash when they close)*
