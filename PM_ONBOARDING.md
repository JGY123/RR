# RR — PM Onboarding ("First Monday Morning" Cheat Sheet)

**Audience:** Portfolio Managers using the Redwood Risk Control Panel for the first time.
**Time to first useful action:** ~10 minutes.
**Last updated:** 2026-05-04.

This doc is the operator's manual a PM holds in their hand on day one. It explains what the dashboard does, the 4 things you do most often, the conventions to know, and the few places where the data is honestly imperfect — so you know what to trust at a glance and where to look twice.

> **Companion docs:** `EXECUTIVE_SUMMARY.md` (the 90-second pitch), `PRESENTATION_DECK.md` (the slide-form walk-through), `ARCHITECTURE.md` (for the analyst / engineer behind you who wants to know how it's built). This doc is the everyday reference; those are for context.

---

## Table of contents

1. [What RR does (one paragraph)](#what-rr-does)
2. [Opening the dashboard](#opening-the-dashboard)
3. [The 4 daily moves](#the-4-daily-moves)
4. [Tabs map](#tabs-map)
5. [Conventions to know](#conventions-to-know)
6. [Data integrity model — where to look twice](#data-integrity-model)
7. [FAQ — common questions](#faq)
8. [Glossary](#glossary)
9. [What to do when something looks wrong](#when-something-looks-wrong)
10. [Where the doc surfaces of RR live](#where-the-docs-live)

---

## What RR does

A single-pane portfolio risk dashboard for 6 strategies (ACWI · ACWIXUS/IOP · EM · IDM · ISC · GSC), sourced directly from FactSet Portfolio Attribution CSV exports. ~30 tiles across 4 tabs (Overview / Exposures / Risk / Holdings). 7+ years of weekly history. Built around a strict no-fabrication policy: every number you see traces back to a documented source path; if data is missing, you see `—`, not a guessed value.

The dashboard isn't trying to be a replacement for FactSet PA — it's a fast, single-screen view of the things you check most (TE, Active Share, Beta, factor exposures, top contributors) plus a few cross-strategy views you can't easily get from PA itself.

---

## Opening the dashboard

You'll get the dashboard in one of two ways:

1. **Pre-loaded** — IT or your analyst opens it for you in Chrome at a stable URL (`http://localhost:3099/dashboard_v7.html`, or whatever your firm hosts it at). Just refresh (Cmd+Shift+R) to get the latest data.
2. **Drag-drop** — open `dashboard_v7.html` in Chrome, drag a per-strategy `*.json` file onto the page. The dashboard loads.

If you see "no data" / "loading" beyond a couple seconds, check that `data/strategies/index.json` is present in the served directory.

The strategy picker is in the top-right; the **week selector** is at the very top with the `‹ date ›` arrows. Both update every tile on the page when you change them.

---

## The 4 daily moves

These are what most PMs do every Monday.

### 1) Glance the top of Overview

Open to the **Overview** tab. The top row is `cardThisWeek` — the 4 KPIs every PM looks at:

- **Tracking Error** (TE) — the headline. Color-codes by your firm's risk band.
- **Active Share** (AS) — how different the portfolio is from the benchmark.
- **Beta** — predicted vs benchmark.
- **Holdings count** — N.

If anything is a deltaᵉ-marked or in a warning color, that's where to look first.

Beside it is `cardWeekOverWeek` — your week-vs-prior-week deltas + factor rotation.

### 2) Check the Risk tab

Open to the **Risk** tab. Top row is the time-series hero (`cardTEStacked`) — TE decomposed into stock-specific (amber) + factor (cyan) over time. Drag the rangeslider at the bottom to zoom. The footer below the chart tells you the provenance breakdown of the points (source-direct vs MCR-derived vs broadcast).

Below that: factor contribution bars (`cardFacContribBars`), factor correlation heatmap (`cardCorr`), beta history (`cardBetaHist`), risk-by-dimension (`cardRiskByDim`).

These are the "what's driving my TE today" tiles.

### 3) Drill into Exposures or Holdings

If a sector / country / group / holding stood out, click into it. Most tables and charts are clickable — opens a drill modal with time-series + peer holdings.

The **Holdings tab** has the full holdings list (`cardHoldings`), top 10 by weight (`cardTop10`), the holdings risk quadrant (`cardHoldRisk` — active wt × TE contrib bubble), and the treemap (`cardTreemap`).

### 4) Set notes / flags

Right-click any tile to add a note (sticky, persists to localStorage). On the Holdings tab, flag any ticker with the watchlist flag icon — categories Watch / Reduce / Add. Filter the holdings list by the flag from `cardWatchlist`.

That's 4 moves and you've covered 80% of daily use.

---

## Tabs map

| Tab | What it's for | Key tiles |
|---|---|---|
| **Overview** | Top-line KPIs, this-week summary, week-over-week, sector + group + ranks views | cardThisWeek, cardWeekOverWeek, cardSectors, cardGroups, cardRanks, cardChars, cardCashHist |
| **Exposures** | Per-dimension portfolio shape: sectors, countries, regions, groups | cardSectors, cardCountry, cardRegions, cardGroups, cardBenchOnlySec, cardUnowned, cardRankDist |
| **Risk** | TE decomposition, factor contributions, correlations, history | cardTEStacked, cardFacContribBars, cardFacRisk, cardCorr, cardFacHist, cardBetaHist, cardRiskHistTrends, cardRiskByDim, cardRiskFacTbl, cardRiskDecomp |
| **Holdings** | Full holdings list, top 10, holdings risk quadrant, treemap, attribution | cardHoldings, cardTop10, cardHoldRisk, cardTreemap, cardAttrib, cardAttribWaterfall |

---

## Conventions to know

| Convention | What it means |
|---|---|
| **`—` (em dash)** | Source data is null or missing. NOT zero. NOT fabricated. If you see `—` it means the underlying field wasn't shipped by FactSet (or the parser couldn't find it). |
| **ᵉ superscript** | The displayed value is **derived**, not source-direct. Hover the cell for the derivation chain. Example: `cumulative impactᵉ` means it was simple-summed from weekly contributions because FactSet only ships compounded for the "Full" period. |
| **Universe pill** (Port-Held / In Bench / All) | Filters the holdings universe. Affects holdings-driven tables (cardSectors aggregation, cardRanks). Does NOT affect risk-model columns (TE, MCR, factor contributions) — those are universe-invariant by design. |
| **Week selector** | The `‹ date ›` arrows in the header. Selecting a historical week updates all per-week-aware tiles. An amber banner appears when viewing a non-latest week. Some detail-layer tiles (cardHoldings, cardTop10) are latest-only and show a banner explaining why. |
| **Sector vs Group** | Sectors are GICS (Industrials, Financials, etc.). Groups are Redwood-defined (the 4-bucket tilt taxonomy your firm uses). Holdings can belong to one sector and one group. |
| **Idio vs Factor (in Risk tab)** | Stock-specific (idiosyncratic) risk vs systematic factor risk. Sum to total TE. Color: amber = idio, cyan = factor, on the cardTEStacked chart. |
| **Sign on TE Contrib** | Positive = adds risk, negative = diversifies. Color: red for additive, green for diversifying. |
| **MCR is NOT a percent** | Marginal Contribution to Risk values are bare numbers (e.g., "MCR 4.7"), never with a `%` sign. |

---

## Data integrity model

The single most important thing to know: **every number on this dashboard has a documented source path, and we never silently fabricate.** That said, three places have honest caveats you should know about.

### F18 — per-holding %T sums vary across portfolio

When you look at a tile like cardRiskByDim (TE Contribution by Country / Currency / Industry), the totals row at the bottom may show **Σ %T = 94% to 134%** depending on the strategy. Per CLAUDE.md's documented invariant, this should sum to ~100% per portfolio per week. It doesn't, consistently across all 6 strategies.

**Status:** escalated to FactSet (F18 inquiry letter drafted, awaiting send + reply). The deviation is a known finding from FactSet's data layer, not a bug in our dashboard. **Per-row values (each country / industry's TE Contrib) are individually correct.** It's only when summed across the whole portfolio that the deviation appears.

**What you'll see:** every tile that aggregates per-holding %T to a Σ now carries an "F18 disclosure footer" — for example, on cardRiskByDim:

> Σ %T = 134.2% (expected ~100%; see FACTSET_FEEDBACK F18). Per-row values individually correct.

This is intentional — we'd rather show you the deviation honestly than rescale and pretend.

### B114 — historical depth still being built up

Per-strategy history files at `data/strategies/<ID>.json` are designed to accumulate weeks across ingests (append-only). The merge logic shipped 2026-05-04. Until enough ingests have flowed through the merge pipeline, certain time-series tiles may show partial history with an explanatory note.

Tiles affected: cardTEStacked (provenance-tier footer surfaces this), cardBetaHist, cardCashHist.

### F12 — bench-only long-tail without per-holding %T

When you look at cardUnowned (benchmark holdings not in the portfolio), a footer line tells you something like:

> Bench-only universe: 819 holdings · 196 carry per-holding %T from FactSet Security section · 623 are long-tail bench constituents shipped without %T (FactSet inquiry F12 — pending). Top 10 ranked by |%T| over the 196 with real values.

So the **top 10 you see is correctly ranked** — but the tile doesn't have %T for the rest of the bench universe (FactSet doesn't ship it for long-tail constituents). This is also escalated.

### What "honest" means in practice

Three postures the dashboard takes when data is imperfect:

1. **Suppress** — render `—` and the cell is unambiguous (no value, no guess).
2. **Mark as derived** — show the value with an `ᵉ` superscript and a tooltip explaining the math.
3. **Disclose the deviation** — show the value AND a footer explaining why it doesn't match the expected invariant.

You should NEVER see a fabricated number presented as if real. If you do, that's a bug — please flag it (see "[when something looks wrong](#when-something-looks-wrong)").

---

## FAQ

**Q: Why does cardTEStacked show "Per-week TE history not yet ingested" sometimes?**
The split-file architecture is being populated week by week. Once enough weeks have been ingested (B114 cumulative merge), the chart populates. The footer note explains this. cardTEStacked sum-cards at the top of the Risk tab still show the latest week correctly even when the chart is empty.

**Q: I clicked a bar and nothing happened. Why?**
Two likely causes: (1) the bar represents a row with `—` values (no underlying data to drill); (2) you clicked a chrome button — those have `event.stopPropagation()` so they don't bubble up to the card-level click. If neither, that's a bug; report it.

**Q: My CSV download has a `Source` column with weird values like "mcr-derived". What does that mean?**
That's the F12(a) provenance disclosure. For tiles like cardTEStacked, the per-week values come from one of three tiers: source-direct (FactSet shipped pct_specific that week), MCR-derived (we computed it from sector-MCR aggregation, L2-verified), or broadcast (fallback when neither is available). The Source column tells you which tier each row came from so you can audit.

**Q: How do I export everything to share with a colleague / put in a deck?**
- **CSV per tile** — every tile has a CSV button in the chrome strip. Click `⬇` → "Download CSV".
- **Email snapshot** — `cardThisWeek` has an "Email Snapshot" button that copies a formatted summary to your clipboard with TE / AS / Beta / Holdings + factor tilts + sector OW/UW deltas.
- **Per-tile screenshot / PNG** — chrome strip's `⬇` dropdown also offers PNG download of the rendered tile.

**Q: Why does the Universe pill not change cardCorr / cardTEStacked / cardFacContribBars?**
These tiles read from the risk model (Axioma factor exposures, factor MCRs, portfolio-level pct_specific) which are universe-invariant by design. The Universe pill filters the holdings universe; risk-model columns don't change with holdings universe selection. Each affected tile has a small footer caveat noting this.

**Q: Where do the Spotlight ranks come from?**
The Spotlight rank columns (Overall / Revision / Value / Quality / Momentum / Stability) are weighted-average quintile ranks (1=best, 5=worst) shipped per-holding by FactSet. Q1 holdings are top-ranked; Q5 are bottom. The portfolio is typically tilted toward Q1 by design.

**Q: I see a number that looks wrong. What do I do?**
See the next section.

---

## When something looks wrong

The dashboard's anti-fabrication discipline means: if you see a wrong number, it's almost certainly EITHER a real upstream issue (FactSet data, B114 history not yet ingested) OR a parser-side bug we haven't caught. Either way, the path is the same:

1. **Right-click the tile** to add a note describing what you observed (the note persists; useful for reproducing later).
2. **Hover the cell** — does it have a tooltip with a source path? Does it show ᵉ? That's your first clue.
3. **Click the tile's About (ⓘ) button** — confirms what the cell SHOULD show.
4. **Send the right-click note + a screenshot to your analyst** (or whoever supports RR for your firm). They'll trace it through `SOURCES.md` to the parser to the CSV. If it's a real upstream issue, the trace ends in `FACTSET_FEEDBACK.md`. If it's a parser bug, fixing it is straightforward once the trace lands.

The dashboard never asks you to be the data-integrity engineer. It just asks you not to ignore something that looks off.

---

## Glossary

| Term | What it means |
|---|---|
| **TE** | Tracking Error. Predicted Axioma TE in % per the FactSet Portfolio Stats section. |
| **AS** | Active Share. % of portfolio different from benchmark. |
| **Beta** | Predicted Axioma beta to benchmark (per the model on file). |
| **MCR** | Marginal Contribution to Risk. Bare numbers, no `%` sign. |
| **%T** | Per-holding "Percentage of tracking error" — that holding's contribution to total portfolio TE. (Subject of F18 inquiry.) |
| **%S** | Stock-specific portion of the holding's TE. |
| **Idio / Idiosyncratic** | Stock-specific (non-factor) risk. Σ across holdings = portfolio's idio TE. |
| **Factor risk** | Systematic risk from Axioma factor exposures (Volatility, Value, Momentum, etc.). |
| **Spotlight rank** | Weighted-average quintile rank per holding from FactSet (Q1=best, Q5=worst). 6 sub-categories. |
| **Universe pill** | Top-bar 3-way: Port-Held (only stocks you own) / In Bench (everything in benchmark, includes overlap) / All (union). |
| **F18** | Open inquiry to FactSet on per-holding %T sum behavior. See `FACTSET_FEEDBACK.md`. |
| **F12** | Open inquiry to FactSet on long-tail bench-only %T_implied. See `FACTSET_FEEDBACK.md`. |
| **B114** | Internal backlog item — cumulative-history append-only merge. Shipped 2026-05-04. |
| **F19** | Internal parser fix — per-week pct_specific source-direct. Shipped 2026-05-04 (FORMAT 4.3). |
| **B-item / F-item** | B = internal backlog (we control). F = FactSet item (waiting on them). |

---

## Where the docs live

| File | What it has |
|---|---|
| `EXECUTIVE_SUMMARY.md` | 90-second pitch — what RR is, why we built it. |
| `PRESENTATION_DECK.md` | 12-slide walk-through. |
| `PM_ONBOARDING.md` | This file. |
| `ARCHITECTURE.md` | For your analyst — data flow, tile contract, design system, integrity model. |
| `STRATEGIC_REVIEW.md` | Where we are, what's NOT in good shape, priorities. |
| `LESSONS_LEARNED.md` | The April 2026 crisis story + the 16 lessons since. Read if you're curious why the discipline is so tight. |
| `SOURCES.md` | Per-cell provenance index. The data-integrity engineer's reference. |
| `FACTSET_FEEDBACK.md` | All open / closed inquiries to FactSet. F-numbered. |
| `BACKLOG.md` | Internal work queue. B-numbered. |
| `CHANGELOG.md` | High-level user-visible changes per release tag. |

---

## Section to be added when ready

This doc has structural placeholders for screenshots that the user will add when reviewing:

- [ ] Screenshot of `cardThisWeek` with annotations pointing at TE / AS / Beta / Holdings
- [ ] Screenshot of `cardTEStacked` with annotations on the rangeslider, the provenance footer, the click-to-drill behavior
- [ ] Screenshot of an F18 disclosure footer (e.g., on `cardRiskByDim`)
- [ ] Screenshot of the watchlist flag icons in action
- [ ] Screenshot of the Universe pill + its tooltip explaining the 3 modes
- [ ] Screenshot of an empty-state tile with explanation text (e.g., `cardCashHist` when no data)

When ready, drop them in `docs/onboarding-screenshots/` and link from this doc.
