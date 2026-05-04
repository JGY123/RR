# Tile Spec: cardBetaHist — First-Pass Audit

> **Audited:** 2026-05-04 | **Auditor:** Tile Audit Specialist (subagent)
> **Scope:** First formal three-track audit on `cardBetaHist`. No prior audit on file.
> **Status:** **YELLOW** — multiple findings, none are data-correctness blockers, but **two are user-facing copy/data mismatches** (D2, D3) that should land before any PM rollout. F4 (CSV exporter referenced but undefined) is the only finding that misleads a user mid-click.
> **Color status by track:** Data **YELLOW** · Functionality **YELLOW** · Design **YELLOW**

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Beta History — Predicted |
| **Card DOM id** | `#cardBetaHist` (Risk tab) |
| **Card markup line** | `dashboard_v7.html:7770` |
| **Render function** | `rMultiBeta(s)` at `dashboard_v7.html:8105–8148` |
| **Render dispatch** | `rRiskTab` → `riskFns` array, line 8000 |
| **Inner plot id** | `#riskBetaMultiDiv` (`class="chart-h-sm"` — clamp 180–260px) |
| **CSV exporter** | **`exportBetaMultiCsv` is undefined** — referenced via `&&` short-circuit guard (see F4) |
| **About entry** | `_ABOUT_REG.cardBetaHist` at `dashboard_v7.html:1221–1228` (registered) |
| **Drill route** | Whole-card click → `oDrMetric('beta')` (line 7770 `onclick`) — beta-specific stat layout at `dashboard_v7.html:11424–11473` |
| **Right-click → note** | wired (`oncontextmenu="showNotePopup(event,'cardBetaHist')"`) |
| **Tab** | Risk |
| **Width** | Full-width within Risk tab grid |
| **Full-screen path** | Generic `openTileFullscreen('cardBetaHist')` (clones the card; reattempts Plotly redraw — no bespoke handler at `window._tileFullscreen.cardBetaHist`) |
| **Spec status** | `audit-only` — coordinator serializes any code fixes |
| **Data source** | `cs.hist.sum[].beta` (predicted Axioma beta per week, from `factset_parser.py:1635`) + `cs.sum.betas.{predicted,historical,mpt}` reference lines |

---

## Trivial fixes (1–5 lines each, agent can apply once approved)

- **F1.** Header microcopy fix: change "across all 7 strategies" in the `data-tip` (line 7772) and the About entry `what` (line 1223) to "for the active strategy" — the chart only ever plots the current `cs`.
- **F2.** Tile title is incomplete given the chart actually overlays Predicted + Historical + MPT reference lines. Change "Beta History — Predicted" to "Beta History" or "Beta History — Predicted vs Historical vs MPT" so the legend matches the title.
- **F3.** Empty-state guard: `rMultiBeta` returns silently when `!hist.length` (line 8107). Wrap an inline message in the `#riskBetaMultiDiv` so the tile doesn't render as a blank box. Pattern from `rTEStackedArea` (line 8031).
- **D1.** Replace literal hex `'#6366f1'` (line 8113), `'#10b981'` (line 8122), `'#8b5cf6'` (line 8134), and `'#a78bfa'` annotation hooks with theme-resolved tokens via the `getComputedStyle` pattern used in `rRiskFacBarsMode` (lines 8170–8175). Plotly does need literals (Lessons-Learned anti-pattern #4-3), so resolve `var(--pri)` / `var(--pos)` / `var(--acc)` up-front. Restores dark/light theme parity.
- **D5.** Footer/empty caption wattage: tile has no inception/wks-shown footer like `cardTEStacked` ("stock-specific (purple) + factor (indigo) = total TE · ${s.hist.sum.length} wk", line 7760) does. Add `· ${s.hist.sum.length} wk · since ${isoDate(s.hist.sum[0].d)}` to title row.

## Larger fixes (1–2 hours each, queued)

- **F4.** Wire `exportBetaMultiCsv` (referenced in `tileChromeStrip` at line 7773 — currently a no-op via `&&` guard). Pattern: copy `exportTEStackedCsv` (line 8087) — emits Date / Beta / Predicted / Historical / MPT.
- **F5.** Tile data scope mismatch: tile-title promises "across all 7 strategies" but the renderer only plots `s.hist.sum.beta` (single strategy). Decide: (a) rewrite `rMultiBeta` to actually overlay all 7 strategies in `A` (cross-strategy multi-line view — expensive, would need cross-strategy color palette + universe-aware filtering), OR (b) accept the single-strategy framing and update labels per F1+F2. Recommendation: option (b) — peer tiles (`cardTEStacked`, `cardRiskHistTrends`) are also single-strategy and the multi-strategy comparison lives on the Risk-tab heatmap / sector heatmap.
- **D3.** No KPI strip atop the chart. Peer time-series tiles (`cardTEStacked`) inline the latest values; `cardBetaHist` is just a chart. Add a 1-row strip with Current β / Active β (Δ vs 1.0) / 1Y range / 3Y range. Source: `s.sum.beta`, `s.hist.sum`. Mirrors the rich strip already in the drill modal (line 11448).
- **F6.** Highlight currently-selected week. When the user picks a historical week via the global selector (`_selectedWeek` ≠ null), `rMultiBeta` does NOT respect it — the chart end-date is always latest, no marker on the picked week. This is a week-flow bug (the tile is the only live time-series tile that ignores the selector — `cardTEStacked` and `cardRiskHistTrends` both honor it). Fix: read `_selectedWeek`, drop a vertical shape + annotation at that x. Use the `_histEndIdx(hist)` accessor (line 963).

## PM-decision items

- **X1.** Title says "Predicted" but the overlay table inside the drill modal (line 11193) shows three β measures (Predicted, Historical, MPT). The card itself plots only the time series of `hist.sum[].beta` (predicted) but draws Historical + MPT as flat reference lines. PM call: keep the "Predicted only over time + reference lines for siblings" framing, OR persist the Historical / MPT TIME-SERIES into `hist.sum[].hist_beta` / `mpt_beta` so all three become real lines. This is a parser-side question (B114-style work).
- **X2.** Reference-band threshold at β = 0.9 / 1.1 (visible only in the drill modal, line 11145) should arguably appear on the tile chart too. PM call: are these team-wide guardrails (in which case publish on the tile) or just analyst guides (in which case keep in the drill).

---

## 1. Data Accuracy — Track 1

### 1.1 Provenance — every plotted point traces to source

| Plotted | Source path | Fabricated? | Markers? |
|---|---|---|---|
| Main β line, y-values | `s.hist.sum[].beta` | No — direct read | n/a |
| Main β line, x-values | `s.hist.sum[].d` via `isoDate(...)` | No | n/a |
| Predicted ref line | `s.sum.betas.predicted` (= `s.sum.beta`) | No | green dotted |
| Hist Ref line | `s.sum.betas.historical` (parser pcv "Axioma- Historical Beta") | No | gray dotted |
| MPT line | `s.sum.betas.mpt` (parser pcv "Port. MPT Beta") | No | violet dashdot |

The parser populates `s.hist.sum[].beta` from "Axioma- Predicted Beta to Benchmark" per period (`factset_parser.py:1635`). `_b115AssertIntegrity` (line 2017) checks `beta` as a critical field on every load — drift surfaces in the console. **GREEN.**

### 1.2 Null / gap handling

`hist.map(h=>h.beta)` (line 8109) does NOT skip null β. Plotly handles `null` y-values by breaking the line (default `connectgaps:false`), so a missing weekly beta produces a visible gap — correct behavior. **No fabrication, no synthesis path.** GREEN.

### 1.3 Reference-line behavior when source is null

Lines 8119, 8125, 8131 each guard with `if(betas.X != null)` before pushing a trace. If `betas.historical` is null, the gray dotted Historical line is simply absent. **No silent fabrication. GREEN.**

### 1.4 Week-selector interaction (`_selectedWeek`)

**RED-leaning YELLOW.** When the user picks a historical week via the global week selector (`_selectedWeek` set by `initWeekSelector`), the chart end-date is still latest — no vertical marker drops on the picked week, no slice happens. Peer tiles like `cardTEStacked` (line 8027) and `cardRiskHistTrends` (line 7578) implicitly respect the selector via `_histEndIdx(hist)`. `rMultiBeta` is the sole live time-series tile that ignores it. See F6 — proposed fix: vertical Plotly shape at `_selectedWeek` + annotation. Not a data-fabrication finding, but a **week-flow inconsistency**.

### 1.5 localStorage anti-pattern check

`rMultiBeta` reads only from `s` (passed in) and from `THEME()`. **No `localStorage` reads anywhere in this tile.** GREEN.

### 1.6 Spot-check (sample)

I did not load-test against `latest_data.json` here (subagent runtime), but the integrity assertion + parser-side single source of truth (`_hist_entry`, line 1622) means any drift would surface in `_b115AssertIntegrity`'s `hist.sum.length` check (line 2034). Recommend running in-browser smoke check post-fixes. GREEN posture.

### 1.7 Data anti-pattern audit (Lessons Learned 8 RED)

| Pattern | Present? |
|---|---|
| Hardcoded column positions | No — render reads named fields (`h.beta`, `h.d`) only. |
| Multiple parsers for same input | No — `rMultiBeta` consumes `s.hist.sum` directly. |
| `normalize()` synthesis without markers | No — uses raw `h.beta` per point; nullables surface as gaps. |
| Hardcoded numeric fallbacks | No. |
| localStorage as data | No (see 1.5). |
| Missing integrity assertion | Covered by `_b115AssertIntegrity` for `beta` (`CRITICAL_FIELDS` line 2021). |
| Fabricated dates | No — uses `h.d` directly. |
| Tooltips without source paths | The hover tooltip is `Beta: %{y:.3f}` with no source-path link. Could add a one-line source caption. (D6 below) |

**Track 1 verdict: YELLOW (only because of week-flow bug 1.4 / F6). All other data lines are clean.**

---

## 2. Columns / Visual Encoding

| Trace | Encoding | Style | Notes |
|---|---|---|---|
| Beta line | x=date, y=β | indigo `#6366f1`, width 2.5 | LITERAL HEX (D1). Theme tokens not used. |
| Predicted ref | flat horizontal | green `#10b981` dotted | Same value as latest point on main line — visually redundant. (X3 below) |
| Hist Ref ref | flat horizontal | `THEME().tick` dotted | Theme-aware (good). |
| MPT ref | flat horizontal | violet `#8b5cf6` dashdot | LITERAL HEX (D1). |
| Annotations | right of chart at each ref line | matched colors, no background | Minimal — could use `bgcolor:'rgba(...)'` for legibility on dark + light. (D2) |
| Legend | horizontal, y:1.12, font 10 | matches peer tiles | OK. |

**X3 PM-decision:** redundant Predicted reference line. The latest value of the main β line equals `betas.predicted` by construction. Either drop it or relabel as "Latest" so it doesn't read as a redundant trace.

---

## 3. Visualization (chart-level)

| Aspect | Status |
|---|---|
| `chart-h-sm` class (180–260px) | Used. Same height token as `cardCashHist` etc. — good. |
| `Plotly.newPlot` config | `plotCfg` standard config; no scrollZoom, no rangeslider. |
| Range slider | **Absent.** `cardTEStacked` HAS a rangeslider (line 8057); `cardBetaHist` does NOT. The drill modal's chart DOES (line 11683). Inconsistent. (V1 below) |
| Reset Zoom button | Yes — `resetZoomBtn('riskBetaMultiDiv')` in card title row (line 7772). |
| Click-through | Whole card has `cursor:pointer` + `onclick="oDrMetric('beta')"` — works. |
| `plotly_click` handler | NOT bound on the inner div — only the card's outer onclick. Acceptable (whole-card click is the canonical UX). |
| Legend overlap risk | At very narrow viewports the 4-trace legend at y:1.12 may collide with the title. Mild concern; not blocking. |

**V1 (medium fix):** add `rangeslider:{visible:true,bgcolor:THEME().card,thickness:0.04}` on the xaxis to match `cardTEStacked`'s zoom-and-scrub behavior. This is the single most-requested time-series UX feature in peer audits.

---

## 4. Functionality Matrix — Track 2

Benchmark: peer tiles `cardTEStacked` (line 7755), `cardRiskHistTrends` (line 7578). Both are full-width Risk-tab time-series tiles.

| Capability | `cardTEStacked` | `cardRiskHistTrends` | `cardBetaHist` | Gap |
|---|---|---|---|---|
| Whole-card click → drill | yes (`plotly_click` bound) | yes | yes (`onclick`) | OK |
| `tileChromeStrip` | yes | yes | yes | OK |
| About btn (ⓘ) | yes | yes | yes | OK |
| Reset Zoom (⤾) | yes | n/a (multi-mini chart) | yes | OK |
| CSV export | yes (`exportTEStackedCsv`) | yes (`exportHistTrendsCsv`) | **referenced but UNDEFINED** | **F4** |
| Full screen (⛶) | yes (custom `openCardTEStackedFullscreen`) | yes | generic `openTileFullscreen` (clone-overlay fallback) | F7 — should ship a dedicated handler (see below) |
| Reset View | yes | yes | yes | OK |
| Hide tile | yes | yes | yes | OK |
| Right-click note | yes | yes | yes | OK |
| Range buttons inside drill | yes (TE drill) | yes | **yes** — `oDrMetric('beta',range)` wires 3M/6M/1Y/3Y/All | OK |
| Range buttons on tile itself | yes (Plotly rangeslider) | n/a | NO | V1 |
| Inline KPI strip (latest values) | yes | yes (4 minis) | NO | D3 |
| Empty-state messaging | yes | yes | NO (silent return) | F3 |
| Highlight `_selectedWeek` | yes (rangeslider auto-syncs) | yes (mini chart end-stop) | NO | F6 |
| Universe pill | n/a (TE = portfolio level) | n/a | n/a (β is a portfolio-level metric) | n/a |

**F7 (medium):** the generic `openTileFullscreen` fallback (line 1448) clones the entire card outerHTML and re-runs Plotly on every `[id$="Div"]` it finds. This works but the clone keeps the card's small `chart-h-sm` class — the Plotly redraw bumps height to `min(window.innerHeight-160, 720)` but the wrapper card style retains the small height. Result: the chart fills 720px but inside a slim card. A bespoke `openBetaHistFullscreen()` would let us render the full β panorama with a richer KPI strip and possibly cross-strategy overlay.

### 4.1 Drill modal (`oDrMetric('beta')`) parity check

The beta drill modal (lines 11424–11473) is **rich**:
- 4-card stat strip (Current β, Active β, Variant Spread, Beta Percentile)
- Range buttons (3M / 6M / 1Y / 3Y / All)
- Beta variant table — Predicted / Historical / MPT — click to toggle each as a chart overlay
- Threshold annotations (β = 0.9 / 1.1)
- Rangeslider on chart axis

The drill is significantly more valuable than the tile. The tile under-delivers vs. its drill. **D3 (KPI strip on tile) and V1 (rangeslider on tile) would close the gap.**

### 4.2 Universe-invariance check

β is a portfolio-level metric — universe pill (Port-Held / In-Bench / All) does NOT apply. No regression here. GREEN.

---

## 5. Popup / Drill experience

Whole-card click → `oDrMetric('beta')` → modal renders at line 11424. Modal:

- **GREEN** stat-strip layout (4 cards, `border-top` semantic colors).
- **GREEN** Variant Spread card (multi-β framing) explicitly invites the user to click variant rows for overlay — a UX touch peer tiles don't have.
- **GREEN** range buttons.
- **YELLOW** the percentile cell uses `numVals.length` which is `vals.filter(v=>v!=null)` — for β this is fine but the percentile is ALWAYS computed against the SLICED hist (range-button-aware, line 11138). So "Beta Percentile" within a 3M view is the percentile within those 13 weeks, not lifetime. This is correct for UX but the label "vs ${numVals.length} wks" is the only signal — could be more explicit.

Drill design is good; main gap is **the tile itself feeds nothing into the drill** beyond the click — no per-week deep linking (e.g., click a point at June 2024 → drill opens with the chart auto-scoped to that period). Optional enhancement, not blocking.

---

## 6. Design Consistency — Track 3

### 6.1 Tile chrome

`tileChromeStrip` is used (line 7773). Migration COMPLETE per Phase D. GREEN.

But: notice the chrome strip uses `extra:'<span style="font-size:9px;color:var(--pri)">click for detail ›</span>'`. This is **inline styling** rather than a tokenized class — minor but the design system has `font-size` tokens (`--text-xs`, `--text-md` etc.). Consider extracting to a `.tile-hint` class. (D7 nit)

### 6.2 Color tokens vs literal hex (LESSONS_LEARNED anti-pattern)

`rMultiBeta` line 8113 (`#6366f1`), 8122 (`#10b981`), 8134 (`#8b5cf6`) hardcode hex. The project pattern (e.g. `_teStackColors` at line 8014, `rRiskFacBarsMode` at line 8170) resolves CSS tokens via `getComputedStyle` up-front. Lessons-Learned anti-pattern #4-3-2: "Plotly's `marker.color`/`line.color`/`paper_bgcolor` need literal hex — never CSS vars. Resolve up-front." `rMultiBeta` violates the resolve-up-front idiom. (D1 above.)

Visible impact: dark/light theme switch will leave the indigo line at indigo (which happens to match `--pri` in dark theme but may not in light). Low-risk today but a portability concern.

### 6.3 Typography & spacing

Card title font matches peer tiles (uses `.card-title.tip` shared class). The title row has the standard `flex-between` flex + 4px margin-bottom. GREEN.

### 6.4 Chart height

`chart-h-sm` is appropriate for a hero tile? Peer hero `cardTEStacked` uses `chart-h-md` (260–400px). β-hist is also full-width. Arguably it should match (`chart-h-md`) since it's a top-of-Risk-tab tile. PM call. (X4)

### 6.5 Hairline footer

No footer caption like `cardTEStacked`'s "stock-specific (purple) + factor (indigo) = total TE · ${s.hist.sum.length} wk". Adding one (e.g. "Predicted Axioma β · ${s.hist.sum.length} wk") closes the design-consistency gap. (D5 above.)

### 6.6 Empty state

Currently silent. (F3 above.)

### 6.7 Tooltip on header

`data-tip="Predicted beta over time across all 7 strategies. Click anywhere on the card for detail. Right-click for notes."` — has the **misleading "all 7 strategies"** copy (F1). Fix to "Predicted Axioma beta over time + Historical/MPT reference lines."

### 6.8 Theme awareness

`THEME().tick` IS used for the Hist Ref line and annotation (line 8128, 8138). PARTIAL theme-awareness — main line and Predicted/MPT lines still use literal hex. (D1 cleans up.)

### 6.9 Clickable tile cursor

`cursor:pointer` on the card itself + `cursor:pointer` should NOT cascade to the chrome strip buttons (event-bubbling concern). Verified line 7772-7773 wrap each chrome control in `<span onclick="event.stopPropagation()">` — clicks on About / Reset Zoom / CSV / FS / Reset View / Hide do NOT bubble to the card-level `oDrMetric('beta')`. GREEN — well-implemented.

---

## 7. Known Issues / Open Questions

1. **F1/F2/F5 (TIE):** the title and `data-tip` say "all 7 strategies" but the renderer plots only the active strategy. This is the highest-impact finding because it's a user-facing falsehood. PM-decide: rewrite render to actually plot 7 lines (option a — large) OR fix the copy (option b — trivial).
2. **F4:** the CSV button is a no-op due to undefined `exportBetaMultiCsv`. Users clicking it will see nothing happen — no error, no download. This is the **only** finding that misleads a user mid-click.
3. **F6:** week-selector ignored. Moderate-severity week-flow bug; consistent with the inconsistency the lint-week-flow tool was built to catch.
4. **X1:** Historical / MPT shown as flat reference lines because parser only ships the latest scalar. Long-shelf B114-style work to ship hist arrays for these — would be a real upgrade.

## 8. Verification Checklist

- [x] Data accuracy — `s.hist.sum[].beta` reads cleanly; `_b115AssertIntegrity` covers `beta` as critical field
- [x] Edge cases — empty hist (F3 — message missing but no crash), null betas (skipped via Plotly default)
- [x] Drill modal range buttons work (3M/6M/1Y/3Y/All)
- [x] Right-click → note popup wired
- [x] Reset Zoom button wired to `riskBetaMultiDiv`
- [x] About btn (ⓘ) registered in `_ABOUT_REG`
- [ ] **Title/tooltip copy matches data scope** (F1/F2)
- [ ] **CSV button works** (F4)
- [ ] **Week selector reflected on chart** (F6)
- [ ] **KPI strip with current values** (D3)
- [ ] **Theme tokens resolved up-front** (D1)
- [ ] **Empty-state message** (F3)
- [ ] **Footer / wks caption** (D5)
- [ ] **Tile rangeslider** (V1)
- [ ] **Bespoke fullscreen handler** (F7)

---

## Findings index (numbered, by track)

| # | Track | Severity | Location | What | Why-matters | Proposed fix |
|---|---|---|---|---|---|---|
| F1 | D | trivial | line 7772, 1223 | "across all 7 strategies" copy is wrong | User-facing falsehood — chart only shows active strategy | Replace with "Predicted Axioma β + Historical/MPT reference lines" |
| F2 | D | trivial | line 7772 title | Title "Beta History — Predicted" doesn't match the 3-overlay reality | Title undersells the chart | "Beta History" or "Beta History — Predicted vs Historical vs MPT" |
| F3 | F | trivial | line 8107 | Empty hist returns silently — blank box | Looks broken on no-data strategies | Inline `<p>` empty-state message |
| F4 | F | larger | line 7773 | `exportBetaMultiCsv` undefined; CSV button no-ops | Mid-click dead-end | Define `exportBetaMultiCsv` (pattern: `exportTEStackedCsv` line 8087) |
| F5 | F | larger / PM | line 8105 | Renderer plots active strategy only despite multi-strategy framing | UX mismatch with About/title | Either rewrite as multi-strategy overlay OR converge to single-strategy framing (recommend latter) |
| F6 | F | larger | line 8105–8148 | Week-selector ignored | Week-flow inconsistency | Drop vertical shape + annotation at `_selectedWeek` via `_histEndIdx(hist)` |
| F7 | F | larger | line 7773 | Generic `openTileFullscreen` fallback used | FS view inherits cramped card height | Bespoke handler with KPI strip + larger chart |
| D1 | X | trivial | line 8113, 8122, 8134 | Literal hex `#6366f1`, `#10b981`, `#8b5cf6` instead of resolved tokens | Theme portability, project idiom violation | Use `getComputedStyle` resolve pattern from `_teStackColors` line 8014 |
| D2 | X | nit | line 8137–8140 | Annotations have no bg fill — may collide with grid lines | Legibility on dark + light | Add `bgcolor:'rgba(15,23,42,0.65)'` |
| D3 | X | larger | line 7770 | No KPI strip atop chart | Tile under-delivers vs drill | Add 4-card strip mirroring drill (Current β / Active β / 1Y range / 3Y range) |
| D5 | X | trivial | line 7772 | No `${hist.length} wk` footer caption | Design inconsistency vs cardTEStacked | Add caption span next to title |
| D6 | X | nit | line 8114 | Hover tooltip has no source-path link | Lessons #B reverse-pattern: cells should be source-traceable | Add `<br>source: hist.sum[].beta` |
| D7 | X | nit | line 7773 | "click for detail ›" inline-styled span | Token system has `--text-xs` | Extract to `.tile-hint` class |
| V1 | F | medium | line 8141 | No rangeslider on tile chart | Inconsistency with `cardTEStacked` | Add `rangeslider:{visible:true,bgcolor:THEME().card,thickness:0.04}` |
| X1 | – | PM | parser-side B114 work | Hist/MPT as flat refs (parser ships scalar only) | Long-shelf upgrade | Persist `hist.sum[].hist_beta` / `mpt_beta` |
| X2 | – | PM | line 11145 | β = 0.9 / 1.1 thresholds in drill but not on tile | Guardrails not visible at glance | Promote to tile if team-wide |
| X3 | – | PM | line 8119 | Predicted reference line redundant with latest point of main line | Visual noise | Drop OR relabel "Latest" |
| X4 | – | PM | line 7775 | `chart-h-sm` (180–260px) for a top-of-tab tile | Smaller than peer hero (`chart-h-md`) | Bump to `chart-h-md` if PM agrees |

---

## Appendix — code locations

- Tile markup: `/Users/ygoodman/RR/dashboard_v7.html:7770–7776`
- Renderer: `/Users/ygoodman/RR/dashboard_v7.html:8105–8148`
- Render dispatch: `/Users/ygoodman/RR/dashboard_v7.html:8000`
- About entry: `/Users/ygoodman/RR/dashboard_v7.html:1221–1228`
- Drill modal (beta path): `/Users/ygoodman/RR/dashboard_v7.html:11424–11473` and chart at line 11684
- Parser source for `hist.sum[].beta`: `/Users/ygoodman/RR/factset_parser.py:1635`
- Parser source for `sum.betas`: `/Users/ygoodman/RR/factset_parser.py:1438–1442`
- Integrity assertion (covers β): `/Users/ygoodman/RR/dashboard_v7.html:2017–2045`
- Week-flow accessor: `/Users/ygoodman/RR/dashboard_v7.html:963–970`
- Tile chrome strip helper: `/Users/ygoodman/RR/dashboard_v7.html:1511–1525`

---

**End of audit.** Coordinator may now serialize fixes per `Trivial fixes` / `Larger fixes` / `PM-decision` lists at top.
