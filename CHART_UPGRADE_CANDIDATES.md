# Chart Upgrade Candidates — Vote + Comment Sheet

**Drafted:** 2026-05-05
**How to use:** edit this file inline. Each candidate has a vote field — change the marker (`[ ]` → `[x]`) and add notes in the **Notes** field. I'll read the file when you're done and ship the YES items in priority order.

**Voting key:**
- `[x] YES — ship` → I implement next session
- `[x] LATER — keep but defer` → queued, not yet
- `[x] SKIP — leave as-is` → it's fine as it is, don't touch
- `[x] DIFFERENT — see notes` → has a different angle than what I proposed

You can vote multiple ways (e.g., YES + DIFFERENT, with notes explaining your tweak).

---

## Candidates already covered in earlier conversation

- **cardCashHist** — user said: SKIP, it should stay simple. ✅
- **cardBetaHist** — user said: yes, do upgrade (full rich version per audit D3). 👇 captured below as #1.
- **cardCorr** — user said: yes. 👇 captured below as #2.
- **cardTop10** — user said: yes. 👇 captured below as #3.
- **cardRiskHistTrends** — user said: yes (one of the simple ones to upgrade). 👇 captured below as #4.

---

## Risk tab — main candidates

### #1 — cardBetaHist (Beta History)

**Today:** β line + 3 flat reference lines (Predicted / Historical / MPT). Plain. Audit (`cardBetaHist-audit-2026-05-04.md`) D3 + V1 already specified the upgrade.

**Proposed:**
- KPI strip atop chart: Current β · Active β (Δ vs 1.0) · 1Y range · 3Y range · % weeks above 1.05 · % weeks below 0.95
- Tile-level rangeslider (currently only in drill modal)
- Annotation: highlight the most-extreme β week visible
- Faint ±1σ band around predicted line

**Effort:** ~2-3 hr.

```
Vote: [x] YES — ship  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #2 — cardCorr (Factor Correlation Matrix)

**Today:** factor × factor Pearson heatmap, alphabetical-ish order, 12×12.

**Proposed:**
- Hierarchical clustering reorders the rows/cols so correlated factors sit next to each other (visually obvious blocks of red/blue)
- Highlight cells where |r| > 0.6 with a subtle ring
- Click a cell → drill to the time-series of those two factors' active exposures overlaid

**Effort:** ~2-3 hr (clustering is a well-known algo).

**Trade-off:** clustering changes row order — if PMs are used to alphabetical, this is "different." A toggle (alphabetical / clustered) is +30 min.

```
Vote: [x] YES — ship  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes (alphabetical+cluster toggle? or just cluster?):
```

---

### #3 — cardTop10 (Top 10 Holdings)

**Today:** simple horizontal bar of port weight, top 10. Click → drill.

**Proposed:**
- Triple-encoded bars: bar length = port weight; sub-bar overlay = active wt; secondary axis tick = TE contribution. Three dimensions in one chart.
- Color by sector (vs uniform color) — visually obvious sector concentration
- Annotation: TE rank vs weight rank (big delta = "this position is risk-disproportionate to its weight")

**Effort:** ~2-3 hr.

**Trade-off:** simplicity is a feature for daily glance. Could be too busy.

```
Vote: [x] YES — ship  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes (keep simple? more dims?):
```

---

### #4 — cardRiskHistTrends (4 mini sparklines)

**Today:** 4 thin sparklines at the top of the Risk tab — TE / AS / Beta / Holdings. Each shows the latest value + a tiny line.

**Proposed:**
- Target band per metric (e.g., TE 4-7%, Beta 0.95-1.05) — color-coded
- Annotation: current value vs 1Y mean (z-score) — surfaces "is this normal?"
- Mouseover detail on any past week (date + value)
- Click → expanded view (full historical chart in a drill)

**Effort:** ~1.5 hr.

```
Vote: [x] YES — ship  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

## Risk tab — additional candidates

### #5 — cardFacButt (Factor Performance Map)

**Today:** quadrant scatter — x = active exposure, y = period impact, bubble = TE contrib, color = sign. Recently fixed axis labels.

**Proposed:**
- Quadrant labels are already in the corners ("OW · working ✓" etc.) — make them clickable filters (click "OW · hurting" → filter table to those factors)
- Add a "trail" — for each factor show its position 4 weeks ago as a faint marker connected by a line to current. Movement = trend.
- Annotation on the most-shifting factor (largest movement WoW)

**Effort:** ~3 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #6 — cardFacRisk (Factor Risk Snapshot)

**Today:** sibling quadrant — x = active exposure, y = TE contrib, bubble = factor σ, color = adds/diversifies.

**Proposed:**
- Labels overlap when many factors near the origin — implement leader lines or smart label staggering
- Add an "extreme" call-out band: any factor with |c| > 2% (or universe-aware threshold) gets a thicker bubble border
- Optional: show "what would the chart look like if you added/removed factor X?" via hover-modal

**Effort:** ~2 hr (just polish — no math redesign).

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #7 — cardFacHist (Factor History)

**Today:** multi-line chart, factors selected via toggle, metric pill (Active Exp / Factor Return / Cum Return).

**Proposed:**
- Range pills (3M / 6M / 1Y / 3Y / All) — peer cardCorr has them, cardFacHist doesn't (audit L1 from May)
- Smart label placement at the right edge (instead of legend)
- Mouseover crosshair showing all factor values at a single date
- "Reset to top 5 by current |exposure|" button

**Effort:** ~3 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #8 — cardRiskByDim (Risk by Dimension)

**Today:** horizontal bar chart of TE contribution by Country / Currency / Industry. Already has F18 disclosure footer.

**Proposed:**
- Threshold slider (already there) gets a histogram thumb showing the distribution of |TE| values — user sees where threshold should land
- Top-N quick-pick buttons (Top 5 / 10 / 20)
- Bench-line overlay: the bench's exposure to the same dimensions, faintly behind each bar

**Effort:** ~2 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #9 — cardRiskFacTbl (Factor Exposures Table)

**Today:** table of factors with columns: Factor / Exposure / TE Contrib / % TE / % Fac / Return / Impact.

**Proposed:**
- Inline sparkline column showing 12-week trend per factor
- Heat-shaded rows: row background tinted by TE contribution sign + magnitude
- Sortable expand: click a row → 8-12 of the largest contributing holdings appear inline

**Effort:** ~3 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #10 — cardRiskDecomp (Risk Decomposition Tree)

**Today:** collapsible tree with Total → Factor / Idio → leaves. Click to expand. Already has F18 footer.

**Proposed:**
- Sunburst-style alternative view — toggle button (Tree / Sunburst). Sunburst shows proportions visually; tree shows hierarchy.
- Click a factor leaf → in-place expand to show contributing holdings
- Per-week historical "shrink/grow" indicator on each node (animated transition when week changes)

**Effort:** ~4 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

## Holdings tab — candidates

### #11 — cardHoldRisk (Holdings Risk Quadrant)

**Today:** scatter of every holding by active wt × TE contrib, bubble = idio TE.

**Proposed:**
- Lasso-select tool to highlight a subset → see Σ port wt / Σ TE / count appear
- Quadrant-labels become clickable filters (click "OW · risk-on" → table view filtered)
- Optional: ability to ANNOTATE specific holdings with a click-to-pin-label feature

**Effort:** ~3 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #12 — cardRankDist (Rank Distribution)

**Today:** simple bar chart of port weight per quintile (Q1..Q5).

**Proposed:**
- Stacked bars: port wt + bench wt + active wt in same bar (3-segment bar per quintile)
- Sector mini-breakdown WITHIN each quintile bar
- Click a quintile → filter table

**Effort:** ~2 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #13 — cardChars (Portfolio Characteristics, 39 metrics)

**Today:** flat table of 39 metrics, grouped by category.

**Proposed:**
- Category tabs (Valuation / Profitability / Growth / Other) → fewer rows per view
- Per-row inline sparkline with the 12-week history (data already shipped per F19 fix)
- Visual deviation indicator: bar showing where Port sits within Bench's full historical range (z-score-ish)

**Effort:** ~3-4 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #14 — cardWeekOverWeek (Week over Week)

**Today:** stat strip + factor rotation table for the latest week vs prior week.

**Proposed:**
- Rolling 4-week trend: same metrics over 4 weeks instead of just WoW (catches building patterns)
- Animation: sparklines that "draw in" when a new week loads (small wow factor)
- Click a delta → drill to "what changed" (which holdings drove the move)

**Effort:** ~3 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

## Overview tab — candidates

### #15 — cardThisWeek (KPI strip — TE / AS / Beta / Holdings)

**Today:** 4 KPI cards with current value + delta vs prior week.

**Proposed:**
- Per-card 8-week sparkline below the value
- "Status" indicator: in-band / approaching threshold / breach (using each metric's target band)
- Click a card → drill to the metric drill modal (already exists for TE / AS / Beta)

**Effort:** ~2 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

## Cross-tile / structural

### #16 — Drill modals (oDr / oDrMetric / oDrCountry / oSt etc.)

**Today:** 8 separate functions, each builds its own chrome inline. Visually inconsistent. Already specced in `DRILL_MODAL_MIGRATION_SPEC.md`.

**Proposed:** Phase A (helpers) + Phase B (canary on oDrMetric) + Phase C-G (full migration). Unified `drillChrome()` helper.

**Effort:** ~6-7 hr (per spec doc).

```
Vote: [ ] YES — ship  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes (urgent for showing? worth the time?):
```

---

## Things I noticed scanning the dashboard (open candidates)

### #17 — Factor pills / chip-cards

Many tiles use small "chip" elements (sector chips, country chips, factor toggles). Visual style is inconsistent (some have rounded corners, some pill, some squircle, some have icons, some don't). Sweep to one canonical chip style.

**Effort:** ~2 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #18 — Loading states

Dashboard goes white/blank for ~1-2s on first load + on strategy switch. No skeleton. Per `DESIGN_TOUCH_UP.md` §7.

**Proposed:** skeleton tiles (gray rectangles) during load + dim previous strategy's tiles to 50% opacity during strategy switch + replace as new data arrives.

**Effort:** ~1.5 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #19 — Sortable column headers

Tables sort on click but there's no visible affordance (arrow ↑↓ indicating sort dir + active column). Adds polish.

**Effort:** ~1 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

### #20 — Print stylesheet (PDF export)

When PMs save the dashboard as PDF for committee meetings, current dark theme doesn't print well. Needs `@media print` ruleset (already specced in `DESIGN_TOUCH_UP.md` §3.6).

**Effort:** ~1.5 hr.

```
Vote: [ ] YES  [ ] LATER  [ ] SKIP  [ ] DIFFERENT
Notes:
```

---

## Summary table for quick eyeballing

| # | Candidate | Tab | Effort | My recommendation |
|---|---|---|---|---|
| 1 | cardBetaHist rich | Risk | 2-3 hr | Strong yes — audit already specced |
| 2 | cardCorr cluster | Risk | 2-3 hr | Strong yes — high-impact viz win |
| 3 | cardTop10 multi-dim | Holdings | 2-3 hr | Yes if you don't mind +complexity |
| 4 | cardRiskHistTrends polish | Risk | 1.5 hr | Yes — high-leverage small change |
| 5 | cardFacButt trails | Risk | 3 hr | Maybe — fancy but optional |
| 6 | cardFacRisk labels | Risk | 2 hr | Maybe — polish only |
| 7 | cardFacHist range pills | Risk | 3 hr | Yes — closes audit findings |
| 8 | cardRiskByDim sliders | Risk | 2 hr | Maybe — minor polish |
| 9 | cardRiskFacTbl heat-row | Risk | 3 hr | Maybe — interesting density |
| 10 | cardRiskDecomp sunburst | Risk | 4 hr | Maybe — alternative view |
| 11 | cardHoldRisk lasso | Holdings | 3 hr | Cool but not essential |
| 12 | cardRankDist stacked | Holdings | 2 hr | Yes — simple bar wants more dims |
| 13 | cardChars sparklines | Holdings | 3-4 hr | Strong yes — uses F19 data |
| 14 | cardWeekOverWeek rolling | Holdings | 3 hr | Maybe — already complex |
| 15 | cardThisWeek sparklines | Overview | 2 hr | Yes — instant context win |
| 16 | Drill modal migration | All | 6-7 hr | Defer — DRILL_MODAL_MIGRATION_SPEC |
| 17 | Chip canonicalization | All | 2 hr | Defer — design polish only |
| 18 | Loading skeleton | All | 1.5 hr | Defer — UX polish |
| 19 | Sort indicator arrows | All | 1 hr | Yes — quick polish |
| 20 | Print stylesheet | All | 1.5 hr | Yes — unblocks PDF use case |

---

## My suggested top-5 if I had to pick (no further input needed)

If you want to skip the voting and just say "do the top 5 you'd recommend":
1. **#1 cardBetaHist rich** — audit already specced, strong info-density gain
2. **#2 cardCorr cluster** — biggest "wow" visual — cluster-ordered heatmap immediately shows correlated factor groups
3. **#13 cardChars sparklines** — uses the F19 per-week data we just shipped; rich + new
4. **#4 cardRiskHistTrends polish** — small lift, big context win
5. **#15 cardThisWeek sparklines** — Overview tab gets a meaningful upgrade for ~2 hr

Or if you want something different, vote above and I'll execute your set.

---

**When you're done voting, ping me. I'll batch the YES items and ship them in priority order, smoke + commit + push as I go.**
