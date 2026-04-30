# Tab Quality Audit — Risk + Holdings vs Exposures (gold standard)

**Date:** 2026-04-30
**Scope:** Risk tab (`rRisk`, dashboard_v7.html L6322-6620) + Holdings tab (`rHold` / `renderHoldTab`, L7451-7693) compared to Exposures tab (`rExp`, L1726-2142).
**File audited:** `/Users/ygoodman/RR/dashboard_v7.html` (11,689 lines).
**Method:** Read-only inspection. No code changes. Coordinator serializes any fixes proposed here.

---

## Summary

| Tab | Status | Headline |
|---|---|---|
| Exposures | GREEN (gold standard) | Header chrome consistent, About registry covers every tile, period chips synced, themed hovers throughout, B116 universe rule respected. |
| **Risk** | **YELLOW** | Hero charts (TEStacked, FacContrib, RiskByDim, FacHist) are well-built and tile-audited. But: 3 dead-code orphans (rCalHeatCard, rCalHeat, rMCR + 1 stale ABOUT entry per orphan), 1 untitled tile (Factor Correlation Matrix has no id, no About), 0 reset-zoom buttons on 5 of 6 chart tiles, Beta History click-target swallows tile chrome, and Impact column doesn't pick up the global period selector that cardFacDetail does. |
| **Holdings** | **YELLOW** | cardHoldRisk + cardHoldings are first-class. The two ride-along charts at the bottom (Rank Distribution, Top 10 Holdings) are bare cards — no id, no About button, no CSV, no click-to-drill, raw `h.t` instead of `tk(h)` ticker labels. cardHoldRisk also missing reset-zoom + full-screen affordances that cardFacRisk has. |

Net: both tabs work, both are usable, neither is at parity with the chrome on Exposures. Bulk of the gap is **trivial chrome** (10-line header swaps), one **medium item** (hooking Risk-tab Impact into the global period selector), one **cleanup** (deleting ~150 lines of dead code from the cardCalHeat / cardMCR / cardRiskCtryFactor removals).

---

## Removal-cleanup verification (specific user asks)

### `cardCalHeat` — referenced commit `fd31b26`
- **Removed from Risk-tab markup:** YES (L6404-6408 placeholder comment, L6611 commented-out render call).
- **Removed from About registry:** NO — `_ABOUT_REG.cardCalHeat` still at L894-901. Will render in modal if user hits `openAbout('cardCalHeat')` from a stale link, but no live link exists, so it's inert clutter.
- **Render functions still in file:** YES — `rCalHeatCard()` (L6109-6124) and `rCalHeat()` (L6130-6233) still defined. ~120 lines of dead code. Helper `setCalHeatMetric` (L6125-6129), `isoWeekNum` referenced at L11207 in their support, never called from live code.
- **Spec preserved:** YES per commit message — `viz-specs/cardCalendarHeatmap-spec.md` retained.
- **Verdict:** YELLOW — UI is clean but dead code + dead About entry remain. Trivial cleanup.

### `cardRiskCtryFactor` — same commit `fd31b26`
- **Removed from Risk-tab markup:** YES (L6557-6562 placeholder comment, L6620 commented-out render call).
- **Removed from About registry:** NO — `_ABOUT_REG.cardRiskCtryFactor` still at L854-861. Same inert-clutter as above.
- **Render function:** Already inline-deleted (no `function rRiskCtryFactor` exists in file — search confirms). Good.
- **Stale cross-reference in cardSectors related list:** YES — `_ABOUT_REG.cardRiskByDim.related` still says "cardSectors · cardCountry · cardRiskCtryFactor" at L852. Should drop the dangling entry.
- **Stale comment in rCountryChart:** L5511 still says "chart-view AND a Risk-tab tile (cardRiskCtryFactor)". Should be updated to acknowledge the tile no longer exists on the Risk tab.
- **Verdict:** YELLOW — UI clean, two stale text references + dead About entry.

### `cardMCR` — earlier commit `2eff789` / `0ba95bc`
- **Removed from Exposures-tab markup:** YES (L2011-2017 placeholder).
- **Removed from About registry:** NO — `_ABOUT_REG.cardMCR` still at L774-781. The entry even contains forward-looking notes ("Considering reframe as a TE-concentration tile…"), which is fine as design knowledge but currently unreachable as live UI.
- **Render function:** `rMCR()` still defined at L5934 (~50 lines), commented out in render queue at L2125. Dead code.
- **Stale cross-references in About registry:**
  - L740 `cardHoldings.related: 'cardHoldRisk · cardWatchlist · cardMCR'` — stale dangling.
  - L772 `cardWatchlist.related: 'cardHoldings · cardMCR'` — stale dangling.
  - L884 `cardHoldRisk.related: 'cardFacRisk (per-factor sibling) · cardMCR · cardHoldings · TE drill modal'` — stale dangling.
- **Verdict:** YELLOW — cleanup needed but no functional bug. cardHoldRisk on Holdings tab supersedes per the team decision.

---

## Risk tab — tile-by-tile findings

### 0. Sum cards (L6376-6402)
GREEN. 5 cards (TE / Factor Risk / Idio / Beta / Active Share), all clickable, all wired to drill modals via `oDrMetric` and `oDrFacRiskBreak`. Auto-fit grid (140px min) — wraps cleanly on narrow viewports.
- Minor: no drill on Active Share's "trend" sub-line; only the card itself is clickable.

### 1. `riskHistoricalTrends` / `cardRiskHistTrends` (L6236-6279, render at L6281)
GREEN. Auto-fit 4 mini-charts (TE / AS / Beta / Holdings), per-metric `rangemode` (so Beta/AS variation isn't crushed flat), themed via tokens (`--pri`, `--acc`, `--cyan`, `--txt`). Has ⓘ About + right-click notes. Tile-audited 2026-04-23. fixedrange so no zoom — reset not needed.

### 2. `riskDecompTree` (L6060-6101)
**RED chrome / GREEN data**. Total Risk + Factor + Idio waterfall tree with 7 top holdings under idio + 4 factor groups under factor.
- **Missing chrome:** no card `id`, no ⓘ About button, no right-click notes wiring, no CSV export.
- **No About-registry entry** — the only Risk-tab tile fully invisible to the About system.
- Visualization is informative (good use of bar + pct + grouping), but it cannot be linked to / referenced like every other tile.
- **Recommendation:** Promote to first-class — give it `id="cardRiskDecomp"`, register in `_ABOUT_REG`, add ⓘ button, tile-audit it. ~6 lines of HTML chrome + a 12-line registry entry.

### 3. `cardTEStacked` (L6415-6428)
GREEN. Hero. Has all chrome: ⓘ About, right-click notes, ⤾ Reset Zoom, CSV button, themed hover via stacked traces, range slider in xaxis. Click-to-drill on chart wired to `oDrMetric('te')`. Tile-audited 2026-04-24.

### 4. `cardBetaHist` (L6431-6437)
**YELLOW**. Multi-strategy beta line chart.
- **Missing chrome:** no Reset Zoom, no CSV button, no full-screen.
- **The whole tile is `cursor:pointer + onclick="oDrMetric('beta')"`** which means the user can't interact with the chart (zoom, hover, range select) without triggering the drill modal. The ⓘ About button has `onclick="event.stopPropagation()"` to escape this — confirms the swallowing is real.
- **Hover label:** uses `hovertemplate` but builds layout without spreading `plotBg` and without setting `hoverlabel:HOVERLABEL_THEME` explicitly on the trace. Risk of inheriting Plotly defaults rather than the project theme. Worth checking against the rest of the file.
- **Tile-audited:** YES (2026-04-23) but findings haven't all been applied.
- **Recommendation (3 small):** (a) move the click handler from card-level to a chart-overlay div with Z-index above hover events, OR add a small "open drill" button in the header and drop card-level click; (b) add Reset Zoom; (c) verify themed hover.

### 5. `cardFacContribBars` (L6440-6490)
GREEN with one minor. Has all chrome: ⓘ About, right-click notes, mode-toggle radio (TE/Exposure/Both), group pills + threshold slider + checkboxes, explicit ⤾ Reset button (resets the entire control state, not just zoom). Profitability alert builds from history. Click-to-drill works.
- **Minor — no Reset-Zoom for Plotly:** the `⤾ Reset` button resets controls (mode, threshold, checks) but NOT the chart zoom. If a user pans/zooms the bar chart, double-clicking is the only way back. Add `resetZoomBtn('riskFacBarDiv')` next to the existing Reset.
- Snapshot data only (uses `f.c` not period-aware) — by design; this tile is the snapshot view, period view is on Exposures (`cardFacButt`).

### 6. `cardRiskFacTbl` (L6493-6533)
**YELLOW**. Sortable factor table — Active Exposure / Contrib % / MCR to TE / Return % / Impact / Trend sparkline.
- **Missing period awareness on Impact column:** `cardFacDetail` on Exposures shows Impact `(${getImpactPeriodLabel()})` and uses `getImpactForPeriod(f.n,_impactPeriod)` (L3447). cardRiskFacTbl uses raw `f.imp` (snapshot/last-week only). Two tables with the same column header label and divergent values when the user changes the global period selector — confusing. Same fix pattern as cardFacDetail.
- **Missing period awareness on Return column too:** uses raw `f.ret` instead of period-sliced.
- Trend sparkline correctly falls back to `cs.snap_attrib` when `cs.hist.fac` is empty (per the 2026-04-30 fix). Good.
- Has ⓘ About, right-click notes, CSV. Click-row drill wired to `oDrFRisk` (which is now an alias to the unified `oDrF`).
- **Recommendation:** rewire `f.imp` / `f.ret` cells to use period-aware helpers. Add `(${getImpactPeriodLabel()})` to the column headers like cardFacDetail does.

### 7. `cardRiskByDim` (L6538-6555)
GREEN. Clean toolbar — Dim toggle (Country/Currency/Industry pills), threshold slider, CSV export. Has ⓘ About + right-click notes. Hover label themed. B102 design fully shipped, click-to-drill modal wired (`oDrRiskByDim`). B116-respecting (TE aggregates portfolio-invariant). Tile-audited 2026-04-23.
- **Minor — no Reset Zoom** on `rbdChartDiv`. Bar chart, but height auto-recomputed per render so a stuck zoom can hide rows. Add `resetZoomBtn('rbdChartDiv')`.

### 8. `cardFacHist` (L6565-6584)
GREEN with two minors. Time-series chart for selected factors, metric toggle (Active Exp / Factor Return / Cum Return) with localStorage persistence, primary-factor checkboxes + nested industry/country sub-pickers. Themed hover. Has ⓘ About + right-click notes.
- **Minor — no Reset Zoom** on `riskExpHistDiv`. Time-series chart, prime candidate for reset.
- **Minor — no period chips.** The Return / Cum Return modes show all available history; user can't slice to 1Y / 3Y / All like they can on the Exposures-tab Cash Hist or any drill chart's range buttons. Optional but consistent with the global selector spirit.

### 9. Factor Correlation Matrix (L6587-6605)
**RED chrome / GREEN data**. Pearson correlation heatmap with period selector + frequency selector + factor multi-select.
- **No card `id`** — only untitled tile in the file. Every other Risk-tab tile has a stable id.
- **No ⓘ About button.** No About-registry entry.
- **No right-click notes** wiring.
- The data layer is solid (B62/64/66/73-76 have all shipped — robust against zero-variance, monthly dedupe, persisted state, themed colorscale, configurable thresholds). Tile-audited 2026-04-23.
- **Recommendation:** Promote to first-class — `id="cardCorr"`, ⓘ About registry entry (call it Factor Correlation Matrix, what / how / source / caveats / related). The cardCorr alias entry already exists in code (L722-725 inert alias), so the entry skeleton can be drafted from there.

### Cross-cutting Risk-tab observations

- **Reset Zoom coverage:** 1 of 6 chart tiles (cardTEStacked only). Add to: cardBetaHist, cardFacContribBars, cardRiskByDim, cardFacHist, cardCorr. ~6 × 1-line additions of `${resetZoomBtn(divId)}`.
- **About registry coverage:** 7 of 9 tiles (`riskDecompTree` and Factor Correlation Matrix lack entries). Both are fixable in ~30 minutes.
- **Themed hover coverage:** All Plotly calls inherit `plotBg` (which now includes a default `hoverlabel`) since the 2026-04-29 sweep. Risk-tab is GREEN here.
- **Universe pill (B116) compliance:** All Risk-tab aggregations correctly aggregate TE without filtering by universe. GREEN.
- **Period selector consistency:** cardRiskFacTbl is the lone divergence — Impact/Return aren't period-aware while Exposures-tab's cardFacDetail is. YELLOW.

---

## Holdings tab — tile-by-tile findings

### 1. `cardHoldRisk` (L7602-7614, render `rHoldRisk` at L5707-5787)
GREEN data / YELLOW chrome. Per-holding quadrant scatter (active wt × TE contrib × bubble = |MCR|), wired with click-to-drill (`oSt`), bubble + color legend below.
- Hover label themed inline (matches HOVERLABEL_THEME shape). Tickers shown via `tk(h)` (TKR-REGION). Quadrant annotations + faint quadrant tints + zero crosshairs. Solid.
- **Missing chrome vs cardFacRisk** (its sibling on Exposures):
  - No ⛶ full-screen button. cardFacRisk has `openFacRiskFullscreen()`.
  - No Reset Zoom button. cardFacRisk has none either, so this is consistent — but with hundreds of bubbles, the user *will* zoom and lose their way back. Worth adding.
  - No KPI strip above the chart. cardFacRisk has a `facRiskKpi` strip (Idio% / Factor% / Total TE summary chips).
  - No CSV export. cardFacRisk has none either, so this is consistent — but a "top 20 by |TE|" CSV would mirror the cardMCR-style export the team removed and could be a place to land that ask if/when revived.

### 2. `cardHoldings` (L7615-7670)
GREEN. The full holdings table with view toggle (Table / Cards), search box, sector + rank filters, sort pills (By Risk / Weight / Rank / Name), pagination, flag column, RBE column. Card view alternative renders archetypes + factor bars + summary text. Top-10 TE concentration pill in the title. Tile-audited 2026-04-19.
- Uses `tk(h)` for ticker display (`tkrDisplay = h.tkr_region || h.t`) per CLAUDE.md instruction. GREEN.
- Has CSV + PNG download dropdown, view toggle, multi-filter. About registry entry present.
- **Minor:** `cardHoldings` has no ⓘ About *button* in the markup — the registry entry exists at L734 but the row at L7617 only renders `<div class="card-title">` without the `aboutBtn('cardHoldings')` adjacent. Quick check confirms: search of `aboutBtn('cardHoldings')` returns no matches in dashboard_v7.html. Other tiles with About entries all wire the button. **One-line fix.**

### 3. Bottom dual-tile (L7674-7683): "Rank Distribution" + "Top 10 Holdings"
**RED**. Two side-by-side charts in `<div class="grid g2">`, each with literally just `<div class="card-title">` and a chart div. No id. No ⓘ About. No right-click notes. No CSV. No tip / hover documentation in the title. No click-to-drill.
- `rRankDist` (L7777-7784): bar chart of rank quintile distribution. Inherits themed hover from `plotBg`. No labels on x-axis. No interactivity.
- `rHoldConc` (L7786-7808): top-10 holdings horizontal bar.
  - **Uses raw `h.t` (SEDOL) instead of `tk(h)`** in customdata + label fallback. Violates the project standard (memory: "Show TKR-REGION when available"). Fix at L7790: `let labels = top10.map(h => short(h.n || tk(h)));` and L7794 customdata index [0]: `tk(h) || h.t`.
  - **No click handler** — bars don't open the holding drill (`oSt`) like the equivalent on cardHoldRisk does.
  - **No ⤾ Reset Zoom.** `holdConcDiv` is fixed to top 10 so probably fine, but worth double-checking.
- **Recommendation:** Wrap each in proper card chrome with `id`, ⓘ About, click handler. If they're worth keeping (and Rank Distribution duplicates the Spotlight tile on Exposures — see "Cross-tab placement" below), give them first-class treatment; if not, consider removing.

### 4. `cardWatchlist` — currently rendered on EXPOSURES tab (L1797), not Holdings (where it logically lives)
YELLOW. The watchlist is built from per-holding flags (set via the ⚑ icon on Holdings rows). The tile renders only on the Exposures tab via `watchlistCardHtml(s)`. See "Cross-tab placement" below for the proposed move.

### Cross-cutting Holdings-tab observations

- **`cardHoldings` missing the ⓘ button** — registry entry exists, button doesn't render. One-line fix.
- **The two ride-along charts are second-class.** Either upgrade them to first-class with id+About+drill, or delete (Rank Distribution exists in better form on Exposures `cardRanks`; Top-10 Holdings overlaps with `cardHoldRisk`'s top-N labeled bubbles + cardHoldings sorted by weight).
- **`tk(h)` adoption gap:** rHoldConc still uses raw SEDOL. Sweep all per-holding charts to use the standard helper.

---

## Cross-tab placement recommendations

The user's invitation to "rethink which tile belongs where" — opinionated picks:

| Tile | Currently on | Proposed on | Reason |
|---|---|---|---|
| **`cardWatchlist`** | Exposures | **Holdings** | The watchlist is a per-holding curation activity. Flags are set from Holdings rows. Putting the watchlist on the same tab as the source of those flags is natural — see your watchlist while filtering the table. The Exposures tab is portfolio-state-snapshot territory, not "items I'm tracking". Move 2 lines (template insertion + render hook). |
| **`cardBetaHist`** | Risk | **Exposures** | The user's question raises this directly. Beta is a portfolio-level snapshot metric (one of the 5 in the Exposures sum-cards already), and the multi-strategy beta-history line chart is more "where am I in the family" than "what's driving risk". On Risk it's also the smallest tile and gets squeezed below the TE Stacked hero. On Exposures it pairs naturally with the existing Beta sum-card (which currently opens a drill modal that shows the same chart bigger). **Counterargument:** keeping it on Risk justifies the Risk tab's wide left-rail "predicted beta over time" identity. Suggested compromise: move it to Exposures *immediately under* the sum-cards (above `cardSectors`) so it lives with the portfolio-snapshot family, leaving Risk to focus on TE decomposition. |
| **`riskDecompTree`** | Risk | **Risk (keep)** | This is the right tab — risk decomposition is core Risk-tab business. Stays. Just needs first-class chrome (id + About). |
| **Factor Correlation Matrix** | Risk | **Risk (keep)** | Right tab. Risk-tab's only "covariance / co-movement" tile. Just needs first-class chrome. |
| **Rank Distribution chart** | Holdings | **Delete (or Exposures)** | Already covered by `cardRanks` (Spotlight) on Exposures, which has 5 quintiles + factor-contribution columns + universe pill awareness. The bare bar chart on Holdings is a strict subset. Consider deletion. |
| **Top 10 Holdings chart** | Holdings | **Holdings (keep)** | Useful at-a-glance view. But upgrade to first-class — `cardTop10`, About entry, click-to-drill, use `tk(h)`. Or delete in favor of cardHoldRisk's labeled top-20 bubbles. |
| **`cardChars`** (Portfolio Characteristics) | Exposures | **Exposures (keep) but consider Holdings** | Currently full-width Exposures. PMs often look at "fundamentals of holdings" alongside the holdings list. Not strongly mis-placed on Exposures, but worth a flag for future thought. |

**Recommended placement principle going forward:**
- **Exposures** = portfolio-state-snapshot (the latest week, what we hold, vs benchmark, vs target).
- **Risk** = decomposition + time-series (how is risk built up, where is it concentrated, how has it evolved).
- **Holdings** = per-holding browse + per-holding scatter / treemap views.

Watchlist is the only tile that obviously violates the principle today.

---

## Prioritized fix queue (max 8)

| # | Fix | Estimated effort | Trivial / Needs PM / Blocked | Tab |
|---|---|---|---|---|
| 1 | **Cleanup orphan code from prior removals** — delete `rCalHeatCard`, `rCalHeat`, `setCalHeatMetric`, `rMCR`, the cardCalHeat/cardMCR/cardRiskCtryFactor `_ABOUT_REG` entries, and the dangling `related:` references in cardHoldings / cardWatchlist / cardHoldRisk / cardRiskByDim. ~150 lines of dead code. | ~30 min | TRIVIAL | Both |
| 2 | **Move `cardWatchlist` from Exposures to Holdings.** Move the `${watchlistCardHtml(s)}` template insertion from L1797 to the top of Holdings tab (above cardHoldRisk). Update About registry's `related:` cross-refs. | ~10 min | TRIVIAL (after PM ack) | Both |
| 3 | **Move `cardBetaHist` from Risk to Exposures.** Place under sum-cards / above cardSectors. Risk tab loses one tile but gains focus. | ~15 min | NEEDS PM DECISION (move tradeoff) | Both |
| 4 | **Hook `cardRiskFacTbl` to global Impact period selector.** Replace `f.imp` / `f.ret` with `getImpactForPeriod(f.n, _impactPeriod)` and add `(${getImpactPeriodLabel()})` to column headers. Mirror exactly what cardFacDetail does. Surfaces consistent values when the user toggles the global period. | ~25 min | TRIVIAL | Risk |
| 5 | **Promote `riskDecompTree` and Factor Correlation Matrix to first-class.** Add card `id` (`cardRiskDecomp`, `cardCorr`), ⓘ About-registry entries (what/how/source/caveats/related), right-click-notes wiring on the title. Then queue tile-audits for both. | ~30 min | TRIVIAL | Risk |
| 6 | **Sweep Reset Zoom buttons across Risk + Holdings.** Add `${resetZoomBtn(divId)}` to: cardBetaHist (`riskBetaMultiDiv`), cardFacContribBars (`riskFacBarDiv`), cardRiskByDim (`rbdChartDiv`), cardFacHist (`riskExpHistDiv`), cardCorr (`corrHeatPlot`), cardHoldRisk (`holdRiskDiv`). Six 1-line additions. | ~15 min | TRIVIAL | Both |
| 7 | **Decide fate of Rank Distribution + Top 10 Holdings ride-alongs at the bottom of Holdings.** Either upgrade both to first-class (id + About + drill + `tk(h)`) or delete (Rank Distribution is duplicated by Exposures cardRanks; Top 10 is duplicated by cardHoldRisk top-20 labels). | ~10 min PM call, ~30 min implementation either way | NEEDS PM DECISION | Holdings |
| 8 | **Fix `cardHoldings` missing ⓘ button + sweep `tk(h)` adoption in `rHoldConc`.** Add `aboutBtn('cardHoldings')` to the holdings card-title row at L7617. In rHoldConc (L7790, L7794) replace raw `h.t` with `tk(h)||h.t` for display labels + customdata. | ~10 min | TRIVIAL | Holdings |

**Out of scope for this audit (logged for later):**
- cardBetaHist's "whole tile is clickable" interaction model — separate UX call (B-row backlog).
- Adding period chips to cardFacHist — unclear if PM wants the chips or the wide-open scrollable view.
- The cardRanks-vs-Holdings-Rank-Distribution duplication should be settled by the user; this audit calls it out but doesn't pre-empt.

---

## Closing notes

The Risk and Holdings tabs both work. Both have benefited from the recent (2026-04-30) batch fixes — the cardCalHeat / cardRiskCtryFactor / cardMCR removals, the Spotlight full-width fix, the FacRisk 6-KPI strip, and so on. The gap that remains is mostly **chrome consistency** (Reset Zoom on every chart, ⓘ About on every tile, `tk(h)` on every per-holding label) — items that are individually trivial and collectively visible to a PM doing a five-minute walkthrough.

The single biggest data-consistency risk on Risk is `cardRiskFacTbl` not being period-aware: if a PM toggles the global Impact selector to 1Y, the table still shows the latest-week values under the same column label as the period view on Exposures. This is the one item that could produce a "wait, why don't these match?" moment — Item #4 in the queue is the highest-priority correctness fix.

Sign-off requires user review per project policy. Audit is propose-only. No code modified.
