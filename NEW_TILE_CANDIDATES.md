# New Tile Candidates — Q121 brainstorm

**Drafted:** 2026-04-30 · Owner: Yuda + Claude · Source: Q121 from the Inquisitor queue.

Ten net-new tile ideas, prioritized by **PM impact ÷ implementation cost**. Each card has a one-line pitch, the data we'd need (and whether we already have it), the sketch of the visualization, and the sub-question it answers that no current tile answers cleanly.

The current dashboard is dense at 25+ tiles and is excellent at telling you **what** the portfolio looks like right now. Most of the gaps are in **why** and **what changed** — these candidates lean on the time dimension (week-over-week diff, regime detection) and on **counterfactuals** (what if we had X% more / less of factor Y?) — not just more snapshot views.

---

## Ranked: Top 10

### #1 — cardWeekOverWeek (the diff tile)
**Pitch:** "What changed this week." The PM walks in Monday morning — they don't want to re-read the whole dashboard. They want a single tile listing the 5–10 most material moves: holdings added/dropped, biggest weight changes, biggest TE-contribution changes, factor rotation.

**Data needed:** Two snapshots (this week vs. previous week). We **already have** this — `cs.hist.summary` ships every week, and `cs.hold` is per-week (parser appends). For positional diffs (added/dropped names), we'd need to keep `cs.hold` snapshots for at least the prior week — the simplest implementation persists last week's `hold[]` in `latest_data.json` under `cs.hold_prev` (small footprint).

**Viz sketch:**
- 4 mini-cards at top: Δ TE / Δ Active Share / Δ Beta / Δ Holdings count (each with arrow + number)
- Below: 3-column layout
  - "Added" — new holdings sorted by initial port wt
  - "Dropped" — exited holdings, wt at exit
  - "Resized" — top 5 weight changes (sorted by |Δ wt|)
- Bottom: factor rotation summary — 3 factors with biggest active-exposure changes

**Effort:** Medium. ~150 lines. Needs parser to persist `hold_prev`.

**Why now:** Daily/weekly review is the core PM workflow. This is the single most-asked-for view by every PM I've seen use a risk tool. The data already flows — just nobody's connected the wire.

---

### #2 — cardRegimeDetector
**Pitch:** "Are we in a new market regime?" Detects when factor relationships, sector dispersion, or correlation structure shift sharply versus trailing 6 months. Signals when the PM should question whether their model is still calibrated.

**Data needed:** `cs.hist.fac` (factor exposure history) + `cs.snap_attrib[].hist` (factor return history) + `cs.hist.summary.te` (TE history). We have all of this when the multi-year file lands; current GSC quick sample (5 weeks) is too short.

**Viz sketch:**
- Top strip: 4 regime indicators (color dots) — "Factor correlations shifted ✓", "Idio share rising ⚠", "Sector dispersion widening", "Volatility regime change". Click each for the underlying chart.
- Center: rolling 26-week correlation of top 5 factor pairs. Heatmap with delta-from-prior cell coloring. Red = newly correlated, green = newly diversifying.
- Below: 4 mini line charts — TE trend, Idio %, Sector dispersion (cross-sectional std of sector active wts), Factor return dispersion.

**Effort:** Higher. ~250 lines. Statistical work + thoughtful threshold tuning.

**Why now:** This is the "should I be worried?" tile. PMs have it nowhere else; their typical alternative is staring at returns + saying "feels different." A real regime indicator turns gut into spec.

---

### #3 — cardWhatIf
**Pitch:** "What if I…" The PM types a position adjustment ("trim AAPL by 100 bps", "add 50 bps SAP", "double my Energy weight") and sees the resulting TE / active wt / factor exposures **before** committing. Counterfactual stress test.

**Data needed:** Per-holding %T contribution + per-factor MCR loadings. We have %T (h.tr) for actual current holdings. For counterfactuals at the holding level, we need each holding's marginal factor contribution per dollar of weight change — Axioma ships this as the factor exposure vector × covariance matrix product. **Currently not in our parser** — but FactSet exports it as the Factor Tilts section. C-tier ask from FactSet.

**Viz sketch:**
- Left: position editor — list of holdings, each row has +/– pill buttons (10/50/100 bps) and a manual entry. Σ tracker enforces 100% weight.
- Right: live KPI strip — current TE / projected TE / Δ. Below: top 5 factor-exposure changes from the simulation. Animated.
- Persistent. Save button → "Save scenario as 'Energy tilt 5%'", revisit later.

**Effort:** Higher with FactSet ask. ~200 lines once data shipped. Could prototype with simple TE recomputation (sum of new h.tr proportional to weight changes — first-order approximation).

**Why now:** This is the killer app for a risk tool — but it requires parser-side data we don't yet have. Park as Phase 3 deliverable; ask FactSet for "factor exposure vector per holding" in the next response email.

---

### #4 — cardCalendarHeatmap
**Pitch:** GitHub-style calendar heatmap of weekly TE contribution change. Each cell = one week, color intensity = |Δ TE|. Click a cell → opens that week's snapshot. Pattern-detects clusters of high-volatility weeks, dead periods, etc.

**Data needed:** `cs.hist.sum[].te` already has this. Trivial.

**Viz sketch:**
- Inline SVG heatmap, 52 weeks × N years (e.g. 3 rows for 3-year file). Cells colored on a sequential scale (white → red).
- Hover: "Week of 2024-09-12 → TE 5.4 (+0.6 from prior wk)".
- Click: jumps the global week selector to that week.

**Effort:** Low. ~80 lines. Plotly heatmap or pure inline SVG.

**Why now:** Best return-on-effort tile in this list. Shows long-term context at a glance, takes minimal real estate, and doubles as a navigation device into the existing date picker.

---

### #5 — cardConsensusDashboard
**Pitch:** "Where does the portfolio agree / disagree with the benchmark?" Heatmap of every (sector, country, factor) bucket — green = portfolio leans in, red = portfolio leans out. Single tile that tells you what the active bets ARE in one glance.

**Data needed:** `cs.sectors`, `cs.countries`, `cs.factors`. All already shipped. No parser change.

**Viz sketch:**
- 3-row layout, each row a horizontal heatmap strip:
  - Row 1: Sectors — 11 cells colored by Active Wt, sized by |Active|.
  - Row 2: Countries — top 15 by active wt (or top-N pill), same coloring.
  - Row 3: Factors — all 12 factors, colored by f.a.
- Below each row: a 1-line summary — "Largest OW: Industrials +6.3%; Largest UW: Cons Staples −4.1%".
- Click any cell → drill into that bucket's details.

**Effort:** Low. ~100 lines. Pure SVG strips.

**Why now:** "Tell me the active bets in 5 seconds" is a real ask. This is the executive summary that doesn't currently exist in one place.

---

### #6 — cardCorrelationToReturn
**Pitch:** "Has my factor positioning paid off?" Scatter: x = avg active exposure (last 12 weeks), y = realized period return contribution. Shows whether the PM's factor bets actually showed up as return — separates "I know we're tilted to value" from "value tilt is paying off / hurting".

**Data needed:** `cs.snap_attrib[name].hist[].exp` (rolling avg) + `cs.snap_attrib[name].hist[].imp` (rolling sum). We have both — same as cardFacButt. The new view repositions the same data with a richer narrative axis.

**Viz sketch:**
- Same x/y as cardFacButt period view but adds:
  - Trendline + R² showing how well "active exposure" predicts "realized return"
  - Annotation on outliers ("Quality OW since Mar; +0.8% impact")
  - Period selector matches global Impact selector

**Effort:** Low. ~120 lines. Mostly an alternate visualization of cardFacButt.

**Why now:** Could replace cardFacButt's bubble view as the "smart" version. Might be worth folding into existing tile rather than spawning a new one.

---

### #7 — cardConcentrationStress
**Pitch:** "If I lost the top-N positions tomorrow, what happens to TE?" Drop-out simulator — pick a subset, compute the TE with that subset zeroed out vs. proportionally redistributed.

**Data needed:** Per-holding TE contribution (`h.tr`) + per-holding factor contribution (`h.factor_contr`). We have h.tr. Factor contribution per holding **is shipped** in current GSC sample (`h.factor_contr` exists per holding) — verified.

**Viz sketch:**
- Top: pill toggle — "Top 5 / Top 10 / Top 20 / By sector / By rank".
- Center: side-by-side bar — current TE vs. simulated TE.
- Below: factor exposure deltas + sector exposure deltas after the drop.
- Stress narrative: "Removing the top 10 holdings (35% of port wt) drops TE from 6.7 to 4.9 (−27%) and shifts the portfolio toward UW Industrials, OW Cons Disc."

**Effort:** Medium. ~180 lines. Needs careful redistribution math.

**Why now:** Concentration risk is one of the few real PM concerns. This makes it visible.

---

### #8 — cardSectorRotation
**Pitch:** "Sector active weights over time, animated." The PM can see the trajectory of sector tilts — were we OW Tech in 2024 then rotated to Energy in 2025? — instead of just the current snapshot.

**Data needed:** `cs.hist.sec` already ships monthly per-sector active weights. We have it.

**Viz sketch:**
- Stream graph (river chart) — 11 sectors, x-axis = time, y-axis = active wt. Each sector a colored band; bands move above/below zero.
- Or: small multiples — 11 line charts, each one sector's active wt over time.
- Annotations on biggest rotations.
- Click any sector → opens cardSectors filtered to that sector.

**Effort:** Medium. ~150 lines. Stream graph is non-trivial in Plotly; small multiples cleaner.

**Why now:** Shows the temporal dimension of sector positioning that today's cardSectors view misses. Pairs naturally with cardWeekOverWeek.

---

### #9 — cardRiskBudgetReview
**Pitch:** Breakout of cardSectors' "Risk Budget" pill into a full tile. Shows σ-budget vs. σ-actual per sector + flag where the portfolio is outside the planned bands.

**Data needed:** Same as cardSectors + a new `risk_budgets.json` config that the PM owns (per-sector planned σ allocation). User-editable.

**Viz sketch:**
- Horizontal bar chart, one row per sector. Bar = actual σ contribution; vertical line = planned σ.
- Rows colored by `|actual − planned|` — green within band, red over.
- Edit mode: click planned line to drag-adjust. Saves to localStorage (preferences pattern).
- Below: total planned σ ≠ Σ → warning chip if budget doesn't sum to 100%.

**Effort:** Medium. ~180 lines + a budgets config file. Re-uses the existing oDrRiskBudget modal.

**Why now:** The Risk Budget concept is half-built (oDrRiskBudget modal exists; the input config doesn't). This finishes the workflow.

---

### #10 — cardCrossStrategy
**Pitch:** "How does GSC compare to ACWI on TE / Idio / Top-10 concentration?" Cross-strategy comparison heatmap — every metric, every strategy, in one matrix. Existing cardSectorHeatmap (sector-level multi-strategy) is a precedent; this generalizes it to all summary metrics.

**Data needed:** All strategies in `latest_data.json`. We have it.

**Viz sketch:**
- 7 strategies (rows) × 8 metrics (cols): TE / Idio% / Factor% / Beta / AS / Top-10 TE / Top-10 wt / Holdings.
- Cell colors by z-score within column (which strategy is most aggressive on this metric).
- Click any cell → switches the global strategy selector to that strategy.

**Effort:** Low. ~100 lines. Re-uses the multi-strategy pattern from sectorHeatmap.

**Why now:** When the multi-account file lands, the PM team will want to compare strategies side-by-side. Without this tile, they'd have to switch the strategy selector 7 times and remember each value.

---

## Honorable mentions (didn't make the top 10)

- **cardRecentHires** — flag holdings added in the last N weeks where conviction (port wt) hasn't yet ramped. PM nurture-list. (Requires hold_prev.)
- **cardSectorMomentum** — for each sector, are we adding to or trimming positions? Net flow per sector. Would need transaction-level data we don't have.
- **cardEarningsCalendar** — upcoming earnings dates × portfolio wt. Risk concentration around announcement clusters. Needs FactSet fundamentals delivery.
- **cardActiveWeightWaterfall** — sequential explanation of how the portfolio got to its current active weights vs. benchmark, decomposed by selection / weighting / cash. Standard performance-attribution chart.
- **cardScenarioLibrary** — pre-canned what-if scenarios (rate hike, oil shock, dollar weakness) with expected portfolio response. Requires scenario engine.
- **cardEMPositioning** — EM-specific deep dive (when EM is the strategy) on country / currency / political-risk overlap. Strategy-conditional.
- **cardCashTimeSeries** — how the cash buffer has evolved week-over-week. Useful when cash is >2%.
- **cardPMNarrative** — embedded markdown editor where the PM writes a 1-paragraph thesis per week. Cross-references the data automatically. Becomes the seed of the email snapshot.

---

## Recommended order of build

If we're building 3-5 in the next 4-6 weeks before the multi-account file lands:

1. **cardCalendarHeatmap (#4)** — 1 day. Best ROI, low risk, enriches existing nav.
2. **cardConsensusDashboard (#5)** — 2 days. Single-glance summary, no new data, instantly useful.
3. **cardWeekOverWeek (#1)** — 4 days (incl. parser-side hold_prev). Highest PM-value of all candidates; needs parser bump.
4. **cardCrossStrategy (#10)** — 2 days. Pays off the moment the multi-account file lands.
5. **cardConcentrationStress (#7)** — 4 days. Real risk-management value; pairs with risk-budget conversations.

The remainder (regime detector, what-if, sector rotation, risk-budget review, correlation-to-return) are Phase 3+ — most need either richer data or longer engineering arcs.

---

**Process note:** If the user wants any of these built, the next step is a `tile-specs/{cardName}-spec.md` doc per tile (similar to existing cardScatter-audit.md / cardChars-audit.md format) — drafted by `data-viz` subagent, then implemented per spec. Same pattern that produced cardCountry / cardGroups / cardFacRisk.
