# Tile Audit: cardScatter — "MCR vs TE Contribution"

> **Audit date:** 2026-04-21
> **Auditor:** Tile Audit Specialist (CLI) — Batch 3 of Tier-1 sweep
> **Dashboard file:** `dashboard_v7.html` (6,501 lines)
> **Methodology:** 3-track audit per `tile-audit-framework` + `AUDIT_LEARNINGS.md`
> **Siblings in 2×2 cluster:** cardRanks, cardChars (both audited), cardTreemap (pending)
> **Gold-standard refs:** cardSectors, cardHoldings

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | MCR vs TE Contribution |
| **Card DOM id** | `#cardScatter` |
| **Render function** | `rScat(s)` at `dashboard_v7.html:L2577` |
| **Chart target div** | `#scatDiv` (height: 320px, L1259) |
| **Full-screen opener** | `openFullScreen('scatter')` at L5516 |
| **Full-screen renderer** | `renderFsScatter(s)` at L5616 |
| **Full-screen panel helpers** | `_renderFsScatPanel` L5647, `_fsScat_selectHold` L5690, `_renderFsHoldDetail` L5704, `_fsScatSearch` L5678 |
| **Tab** | Exposures (row 7 of Exposures template, L1251–1260) |
| **Paired tile** | cardTreemap (same `g2` row) |
| **Width** | Half (`g2`) |
| **Owner** | CoS / main session |
| **Spec status (prior)** | `tile-specs/risk-return-scatter-spec.md` — **PHANTOM JSONL TRANSCRIPT from 2026-04-13** (see §10 drift section) |

---

## 1. Data Source & Schema — TRACK 1 (Data Accuracy)

**Section grade: RED — urgent PM-facing labeling bug.** The chart's card title, X-axis label, and hovertemplate all call `h.mcr` "Marginal Contribution to Risk (MCR)" but per `CLAUDE.md` and `factset_parser.py:L501`, `h.mcr` is literally the FactSet `%S` column — the **stock-specific component of tracking error**, not marginal contribution to risk. This is a domain-term error a risk PM will catch in seconds.

### 1.1 Primary data source

- **Object path:** `s.hold[]` — per-holding array, 100–700 rows depending on strategy.
- **Filter applied in `rScat`:** `h.p > 0 && !isCash(h)` (excludes benchmark-only holdings and cash/FX pseudo-rows).
- **Filter applied in `renderFsScatter`:** `!isCash(h) && (h.p||0) > 0` (functionally identical, order inverted).

### 1.2 Field inventory — half-tile (`rScat`, L2580–2586)

| # | Role | Field | Parser origin | CLAUDE.md meaning | Label in chart | Correct? |
|---|---|---|---|---|---|---|
| 1 | X axis | `h.mcr` | `%S` (`PCT_S`, parser L501) | **Stock-specific TE component** | "Marginal Contribution to Risk" | **WRONG — mislabeled** |
| 2 | Y axis | `h.tr` | `%T` (`PCT_T`) | **% of total TE contributed by this holding** (sums to ~100% across portfolio) | "TE Contribution %" | Correct |
| 3 | Bubble size | `h.p` | WGT_PORT | Portfolio weight % | Tooltip-only | Correct |
| 4 | Bubble color | `h.a` | Active weight (p − b) | Overweight/underweight % | Colorbar "Active" (red/gray/green diverging) | Correct |
| 5 | Text label | `h.t` | Ticker | — | Shown above dot | Correct |
| — | Hover | `h.t`, `h.mcr`, `h.tr` | — | — | shows ticker + MCR + TE Contrib | Same mislabel as axis |

### 1.3 Field inventory — full-screen (`renderFsScatter`, L5616–5645)

| Role | Field | Label in chart | Delta vs half-tile |
|---|---|---|---|
| X | `h.mcr` | **"MCR (Stock-Specific TE)"** | Better — calls out stock-specific, but still uses "MCR" name |
| Y | `h.tr` | **"Total TE Contribution %"** | Adds "Total" — clearer than tile |
| Size | `Math.max(sqrt(h.p)*9, 5)` | — | **Different scaling from tile** (`Math.max(h.p*3, 6)`). Tile is linear, FS is sqrt — same data, different visual weight per dot. |
| Color | Quintile rank `h.r` (1..5) → 5-step green→red | Undocumented | **Different encoding from tile** (tile = continuous active wt; FS = discrete quant rank). Two tiles, two stories for the same data. |
| Hover | ticker, sector, rank, TE, Port% | — | Richer than tile (tile has only ticker+MCR+TE) |

**Cross-tile consistency failure:** half-tile color ≠ full-screen color. This is the same anti-pattern called out in `cardFRB` (tile/drill palette drift) and surfaced in AUDIT_LEARNINGS.md §"Palette duplication across tile + drill". Here the drift is **semantic, not cosmetic** — a PM dragging a screenshot of the tile into an email and captioning it "colored by rank" would be factually wrong.

### 1.4 Derived / computed values

- None persisted. Both functions read straight from `s.hold[h]`.
- Size scaling: tile uses `Math.max(h.p * 3, 6)`, full-screen uses `Math.max(sqrt(h.p) * 9, 5)`. No maxBubble cap → one outlier ≥30% weight dominates the chart visually.

### 1.5 Ground truth verification

- [x] Parser mapping traced: `%S → h.mcr` (L501), `%T → h.tr` (L500 adjacent), `WGT_PORT → h.p`, `(p-b) → h.a`.
- [x] CLAUDE.md confirms `%T` sums to ~100% and is "% of tracking error" per holding. Y axis label "TE Contribution %" is correct.
- [x] CLAUDE.md confirms `%S` = "stock-specific component of that holding's tracking error". **X axis label "Marginal Contribution to Risk" is incorrect.** MCR in risk-model parlance is ∂σ_portfolio / ∂w_i (a different quantity FactSet does not provide in this column).
- [ ] Spot-check pending a loaded JSON — flagged per AUDIT_LEARNINGS convention.
- [ ] Week-selector awareness: `rScat` reads `s.hold` directly. When `_selectedWeek` is set, the tile silently shows latest holdings (correct per two-layer history architecture, but the historical-week amber banner visually promises otherwise). Same as cardSectors/cardCountry — not a bug, but worth noting.

### 1.6 Missing / null / edge handling

| Scenario | `rScat` (tile) | `renderFsScatter` (full-screen) |
|---|---|---|
| Empty `hold` | Renders `<p>No holdings to plot</p>` into `#scatDiv` (L2579) — GOOD | Renders `<p>No holdings data available</p>` — GOOD |
| `h.mcr` null | `h.mcr \|\| 0` coerces to 0 — places dot at origin (hides missing data) | Same coercion. |
| `h.tr` null | `h.tr \|\| 0` — same silent coerce | Same. |
| `h.a` null | `h.a \|\| 0` used for color → defaults to neutral gray. Acceptable. | N/A (uses rank) |
| `h.mcr` Infinity/NaN | **No `isFinite` guard** — Plotly will silently drop or mis-plot | Same gap |
| Outlier holding (one 30%+ weight) | Linear sizing → 90px+ dot drowns the chart | Sqrt sizing less bad but still no cap |

**Gap:** no `.filter(h => isFinite(h.mcr) && isFinite(h.tr))` guard. Per AUDIT_LEARNINGS.md §"Viz-renderer pattern", Plotly silently coerces NaN/null to 0 — hides missing data as a cluster at the origin. Should filter then note dropped count.

---

## 2. Columns & Dimensions Displayed

No table — chart-only tile. Columns N/A.

---

## 3. Visualization Choice

### 3.1 Layout type
Single Plotly scatter (`scatter` + `markers+text`). Half-tile: 320px high. Full-screen: fills `fsChartDiv` with a right-panel (table) of holdings.

### 3.2 Axis scaling
- Default auto-ranging (inherits `plotBg` at L2238).
- **No zero lines on axes** despite X and Y both being meaningful at zero (zero TE contribution = not contributing to portfolio risk; negative MCR on %S should not happen but is theoretically possible). The full-screen `renderFsFactorMap` (L5571) *does* draw a `zeroline:true, zerolinecolor:THEME().zero, zerolinewidth:2` — cardScatter should match for the X axis at minimum.
- No quadrant annotations, no benchmark-average crosshair. Both were explicitly requested in the phantom spec (§10).

### 3.3 Color semantics
- **Half-tile:** continuous diverging `[[0,'#ef4444'],[0.5,'#94a3b8'],[1,'#10b981']]` on `h.a` (active weight). Colorbar titled "Active".
- **Hardcoded hex:** `#ef4444`, `#94a3b8`, `#10b981` are written inline. Not routed through `THEME().pos` / `THEME().neg` / `--grid`. Breaks theme-aware color rule per AUDIT_LEARNINGS.md §"Viz-renderer pattern". cardCountry was fixed for this; cardScatter was not.
- **Full-screen:** 5-color discrete palette on `h.r` quintile — `#10b981 / #34d399 / #f59e0b / #fb923c / #ef4444`. Matches `_treeRankColor` in cardTreemap (L2597) — palette shared, but only via copy-paste, not a shared helper. Flag for consolidation.
- **Negative active weight** on a holding with **positive TE contribution** is a common pattern (underweight vs bench but still chews TE). Current coloring flags it red (the underweight direction), which is correct PM semantics, but there is no legend/annotation explaining *why* red might be "good" here.

### 3.4 Text labels
- Tile: every dot gets a `textposition:'top center'` ticker label at `size:8`. For 200+ holdings portfolios (IDM has ~450) this produces an unreadable text soup. No label-thinning logic.
- Full-screen: `mode:'markers'` only — **no text labels**. Ironically the larger canvas drops the labels. Either the tile should thin labels to top N by `|tr|`, or the full-screen should restore labels on hover.

### 3.5 Interactivity
| Capability | Tile (`rScat`) | Full-screen (`renderFsScatter`) |
|---|---|---|
| Plotly hover | yes | yes |
| Plotly click → drill | **no wiring** (L2580 has no `.on('plotly_click', ...)`) | yes → `_fsScat_selectHold(ticker)` (L5637) |
| Side panel | no | yes — sortable/searchable table + detail pane |
| Search | no | yes (`_fsScatSearch`) |
| Lasso / box-select | Plotly default but `staticPlot` unchecked — unclear if modebar renders | same |
| Export | PNG only (L1257) | inherits modal toolbar if any |

**Parity failure — critical:** the tile-level chart has **no click handler**. Per AUDIT_LEARNINGS.md §"Click-to-drill parity": if the full-screen sibling wires `plotly_click → oStDetail`, the half-tile should too. Exact pattern spelled out in the Learnings file — cardFacButt was flagged for this in an earlier audit. Fix: one line at end of `rScat`: `document.getElementById('scatDiv').on('plotly_click', d => { if(d?.points?.[0]) oSt(d.points[0].text); });`.

### 3.6 Empty state
Good on both sides. Error message writes to the div (L2579, L5618) — not a silent return. Matches AUDIT_LEARNINGS.md §"Viz-renderer pattern" guidance.

### 3.7 Responsive behavior
- Fixed 320px height on tile (L1259). On narrow viewports the `g2` grid collapses but the chart maintains height — scales horizontally only.
- No `config:{responsive:true}` check in `plotCfg` (inherited).

---

## 4. Functionality Matrix — TRACK 2 (Parity)

**Section grade: RED — half the features the phantom spec (2026-04-13) asked for are missing, AND basic click-drill parity to the full-screen sibling is missing. That compounds: no drill means the tile has one job (display) and it misleads you while doing it.**

Benchmark: cardSectors (gold standard) for tables; cardFacButt / cardFRB (also chart tiles) for chart parity.

| Capability | cardSectors (gold) | cardFacButt (chart peer) | cardScatter (current) | Gap? |
|---|---|---|---|---|
| Empty-state fallback in div | yes | yes | yes | — |
| Theme-aware colors (`THEME()`) | yes | yes (post-fix) | **no — hardcoded `#ef4444 / #10b981 / #94a3b8`** | **TRIVIAL** |
| `plotly_click → drill` | N/A (table) | yes → `oDrF` | **no** | **TRIVIAL (one-line fix)** |
| Full-screen modal button | yes | N/A | yes → `openFullScreen('scatter')` | — |
| PNG export button | yes | yes | yes — but violates `feedback_no_png_buttons.md` (user has said "no PNG buttons" multiple times) | **REMOVE** |
| CSV export | yes | N/A (chart) | **none** — ironically the FS panel renders a table but the tile offers no way to export the underlying holdings-with-MCR/TE list | **TRIVIAL** — wire to a CSV builder that emits `t,n,sec,p,a,mcr,tr` |
| `isFinite` filter before plot | (N/A) | varies | no | TRIVIAL |
| Card-title tooltip | yes | yes | yes ("Marginal contribution to risk vs TE contribution. Bubble size = portfolio weight.") — **parrots the misleading label** | TRIVIAL (rewrite text) |
| Note badge (📝) auto-wire | yes | yes (inherits global sweep) | yes (inherits) | — |
| Toggle views (e.g., MCR vs Exposure vs Volatility) | N/A | yes (cardFacButt has view modes) | **no — hardcoded axes** | NON-TRIVIAL |
| Quadrant annotations | N/A | N/A | **no** (phantom spec asked) | NON-TRIVIAL |
| Portfolio-avg crosshair | N/A | N/A | **no** (phantom spec asked) | NON-TRIVIAL |
| Label thinning (top N by \|tr\|) | N/A | N/A | no — all 200+ labels always drawn | TRIVIAL-to-MEDIUM |
| Sector-color toggle | N/A | N/A | **no** (phantom spec asked as option) | NON-TRIVIAL |

### 4.1 Functionality gaps vs gold + peer chart tiles

1. **No `plotly_click` handler.** Half-tile is read-only; FS is clickable. Most egregious parity gap. One-line fix.
2. **Hardcoded hex colors** instead of `THEME()` / CSS vars. Breaks light theme elegance (continuous diverging colors don't re-tone against white bg).
3. **No CSV export** despite being the most data-rich tile in the cluster (per-holding MCR + TE + active isn't exported anywhere else).
4. **PNG button** violates user standing order (`feedback_no_png_buttons.md`). Trivial removal.
5. **Chart title says "MCR vs TE Contribution" but `h.mcr` is not MCR.** See §1. Labeling bug — PM will flag this.
6. **No `isFinite` filter** before mapping `h.mcr` / `h.tr` to x/y.
7. **Size scaling inconsistent** between tile (linear `h.p*3`) and full-screen (`sqrt(h.p)*9`). Pick one and share the helper.
8. **Color semantic inconsistent** between tile (continuous on active weight) and full-screen (discrete on quintile rank). This is worse than it sounds — the two views of the same dataset tell two different stories about which holdings are "good".

### 4.2 Full-screen modal (`renderFsScatter`) parity review

The FS renderer is noticeably richer than the tile but has its own issues:

- [ ] **Hardcoded panel colors** at L5623, L5656–5660 — mostly slate-palette text, not routed through CSS vars. Breaks in light theme.
- [ ] **Search input styles** (`background:#0f172a;border:1px solid #334155`, L5665) hardcoded — breaks light theme.
- [ ] **Rank thresholds** `h.r<=2 / ===3 / else` duplicated at L5659, L5724 — identical to `_treeRankColor` at L2597 but not factored into a shared helper. Same palette-duplication pattern as cardFRB tile/drill (flagged in AUDIT_LEARNINGS.md).
- [ ] **`selTicker` → detail pane renders factor contributions** at L5709 — nice, and is the only place per-holding factor breakdown surfaces in the UI. Worth flagging as a discoverability win that's buried two clicks deep (full-screen → click dot → scroll panel).
- [ ] Panel's `<table>` has no `id`, no `<th>` sort, no CSV export. A table inside a chart modal is a candidate for the standard table primitives.

---

## 5. Popup / Drill / Expanded Card

The full-screen modal (`fsModal` registered in ALL_MODALS L4655, dismissed by Escape L5545) *is* the drill for this tile. There is no separate holding-detail modal wired in — clicking a dot in FS fills the side panel's detail pane. No `oSt(ticker)` (stock-detail) invocation; no route from this tile to the Holdings tab's per-stock view. Consider: should dot-click deep-drill to the canonical stock-detail modal (`oSt`), not just the side-panel summary?

---

## 6. Design Guidelines — TRACK 3 (Consistency)

**Section grade: YELLOW** — the chart itself is readable, but hardcoded colors, missing zero line, and the text-label soup on high-holding portfolios are peer-inconsistent.

### 6.1 Density
- Height 320px — half-tile standard matches cardMCR (L1279).
- Full-screen panel uses 11px table font, 10px header — matches cardHoldings conventions.

### 6.2 Emphasis & contrast
- Text labels on tile use `color: THEME().tick` — correct. But `size:8` is below the project minimum (scale is 9/10/11/12/13 per AUDIT_LEARNINGS.md §"Density").
- Tile colorbar uses `titlefont:{size:10}, tickfont:{size:9}` — acceptable but `tickfont:9` is at the floor.
- **Bubble opacity** not set on tile — defaults to Plotly's 1.0. Full-screen uses `opacity:0.8` explicitly. For a scatter with 200+ overlapping dots, low opacity helps reveal density — tile should match FS at `opacity:0.8`.

### 6.3 Alignment
- Plot area: `margin:{l:50,r:20,t:10,b:40}` (default `plotBg`). Full-screen overrides to `{l:60,r:40,t:30,b:60}` — inconsistent. Tile's `r:20` leaves no room for colorbar (which renders at `x:1.02` and clips into the card edge on narrow viewports).

### 6.4 Whitespace / padding
- Card padding standard (`.card` base). OK.

### 6.5 Motion / feedback
- Plotly default hover animation only. No "highlight dot on panel-row hover" wiring (full-screen has it only one-way: panel click → chart, not hover → chart). Minor.

### 6.6 Theme adherence — key findings
- `#ef4444`, `#10b981`, `#94a3b8` hardcoded at L2583 — same drift flagged in `rRegChart` (L2298/2301) per AUDIT_LEARNINGS.md §"Viz-renderer pattern". Use `THEME().neg`, `THEME().pos`, `THEME().grid` (extended 2026-04-20).
- Full-screen panel's `#0f172a`, `#334155`, `#e2e8f0`, `#94a3b8`, `#64748b`, `#cbd5e1` are inline throughout L5655–5672 — breaks light theme end-to-end.
- Rank palette `#10b981 / #34d399 / #f59e0b / #fb923c / #ef4444` duplicated at L2597 (cardTreemap), L5623 (FS scatter), L5659 (panel row). Extract a shared `RANK_COLORS` constant.

### 6.7 Consistency issues in one list
1. X-axis: no zero line (peer `renderFsFactorMap` has one).
2. Text label size 8px (below 9px floor).
3. Bubble opacity unset on tile vs 0.8 on FS.
4. Colors hardcoded (all three channels: grid, negative, positive, rank palette).
5. Axis-label prose different between tile and FS (fix the label bug and pick one wording).
6. `margin:` between tile and FS not aligned — colorbar clips at tile's `r:20`.

---

## 7. Known Issues & Open Questions

**Non-trivial queue (backlog-worthy — PM decision or medium-effort work):**

1. **B20 — Card title / X-axis label says "MCR" but field is `%S` (stock-specific TE), not MCR.** This is a PM-facing risk-domain error. Two resolutions:
   - (a) rename everywhere to "Stock-Specific TE" / "Idiosyncratic Risk Contribution" (low code change, high clarity gain); or
   - (b) request MCR proper from FactSet (∂σ/∂w_i) and add a new column — large effort, probably not worth it since `%S` is the more actionable metric for PMs. **Recommend (a).** Ripples: card title L1254, tooltip L1254, axis L2585, `renderFsScatter` label L5632, and the tile's own id `cardScatter` (leave id; rename visible labels).
2. **B21 — Color semantic drift between tile and full-screen.** Tile colors by continuous active weight; full-screen colors by quintile rank. These are two legitimate views but one tile shouldn't silently toggle semantics when expanded. Choices: (a) unify on active-weight for both with optional toggle to rank, or (b) add a color-mode toggle `[Active | Rank | Sector]` rendered in both tile and FS headers. Est 30–50 lines.
3. **B22 — Historical cardScatter is not possible with current parser.** Per AUDIT_LEARNINGS.md blocker: holdings-level history not persisted. No week selector drill for this chart. PM should know.
4. **B23 — Quadrant annotations + portfolio-average crosshair** requested in phantom spec (2026-04-13) never landed. These are the single most valuable chart additions for the "where are we spending risk budget" narrative this tile is built to answer. Medium effort (~80 lines incl. annotation layout and recompute on resize).
5. **B24 — Alternate axis toggle: MCR vs Return / Exposure vs Volatility / Active Weight vs TE Contrib.** Phantom spec asked. This is a PM-decision question before it's an engineering one — the risk-return-scatter name the tile originally had implies "Return" is the intended Y but the parser does not emit per-holding return. Will need FactSet to add or a computation from another source. Flag as blocked/PM.
6. **B25 — Label thinning.** For portfolios with >80 holdings, the `mode:'markers+text'` labels overlap into mush. Thin to top-N by `|tr|` or use `hoverlabel` only. Small fix but needs a small PM call on N.
7. **B26 — Full-screen panel's table (L5666) lacks `<table id>`, sortable `<th>`, CSV export.** This is the primitives checklist applied to a panel inside a modal. Would bring the FS view up to table-primitives standard.

**Open questions for PM:**

- Is "MCR" the PM's preferred shorthand even if technically a misnomer? If yes, keep card title but add clarifying tooltip; if no, rename throughout. (#1 above)
- Should this tile eventually become a risk/return scatter (original phantom-spec intent) when per-holding return becomes available? If so, cardScatter is misnamed until then; consider a renaming pass.
- Should bubble size be capped? One 30%-weight holding currently dominates the visual — Plotly's `sizeref` math could normalize.

---

## 8. Verification Checklist

- [x] Data path traced: `cs.hold[].{mcr,tr,p,a,t,r}` all sourced from parser.
- [ ] Data accuracy: **X-axis field is mislabeled — `h.mcr` is not MCR.** Section 1.
- [x] Empty state: writes to div, doesn't silently return — GOOD.
- [ ] `isFinite` filter on `mcr` / `tr` — missing.
- [x] Full-screen opens via `openFullScreen('scatter')` and Esc dismisses.
- [ ] `plotly_click` on tile → drill: NOT WIRED. Full-screen has it.
- [x] `plotly_click` on full-screen: WIRED → `_fsScat_selectHold`.
- [ ] Theme-aware colors: **hardcoded `#ef4444 / #10b981 / #94a3b8`** on tile; panel side-palette also hardcoded. Light-theme-hostile.
- [x] CSV export on tile: **absent.** (PNG present — should be removed per user standing order.)
- [x] Note badge 📝 support: inherited from global sweep.
- [ ] Axis zero-line on X (stock-specific TE crosses zero conceptually): absent.
- [ ] Bubble size cap for outliers: absent.
- [ ] Label thinning for high-count portfolios: absent.
- [ ] Rank palette helper: duplicated 3× (cardTreemap, FS scatter, FS panel).
- [ ] No console errors: untestable without loaded JSON.

---

## 9. Related Tiles & Cross-Tile Patterns

- **cardTreemap** — same row; reuses identical rank palette (L2597) independently. Palette consolidation should touch both.
- **cardMCR** — row 8, reads `h.mcr` as well. If the name is wrong here, it's wrong there (grep `cardMCR` label copy on next sweep).
- **cardFRB** — same pattern of tile + drill duplicating palette + heuristics. Both should adopt a shared `RANK_COLORS` / `THEME().pos/neg/mid` approach.
- **cardFacButt** — precedent for wiring `plotly_click → oDrF` on a tile-level Plotly chart. Copy the pattern here for `plotly_click → oSt`.
- **cardRanks + cardChars** — the other two in the 2×2 cluster. cardRanks routes to Holdings tab filter by quintile (L1807); cardScatter *could* route clicks to `oSt(ticker)` to close the loop in the same 2×2.

---

## 10. Phantom Spec Drift — called out per main-session ask

`tile-specs/risk-return-scatter-spec.md` is a **JSONL transcript** from 2026-04-13 (parentUuid `4bc7a800...`, session `ca7876de-...`, agent `ad7492d0`) — not a hand-authored spec. It opens with the prompt to that agent:

> "YOUR TASKS:
> 1. Read the current rScat() function
> 2. Add a toggle to switch between: MCR vs Return (current) | Exposure vs Volatility | Active Weight vs TE Contribution
> 3. Add quadrant annotations: …
> 4. Add a crosshair at the portfolio average point (avg MCR, avg Return)
> 5. Make bubble hover show: name, sector, country, weight, all risk metrics
> 6. Consider adding a 'Select holding' click that opens the stock detail popup (oSt(ticker))
> 7. Add sector color coding option as a toggle"

| # | Spec promise | Status today |
|---|---|---|
| 1 | Read / understand rScat | n/a |
| 2 | **Axis toggle (MCR/Return, Exp/Vol, ActWt/TE)** | **NOT PRESENT.** No toggle UI. |
| 3 | **Quadrant annotations** | **NOT PRESENT.** |
| 4 | **Portfolio-avg crosshair** | **NOT PRESENT.** |
| 5 | **Rich hover (name, sector, country, weight, all metrics)** | **PARTIAL.** Tile hover is ticker/MCR/TE only. Full-screen adds sector+rank+Port% but not country nor "all factor contribs". |
| 6 | **Click dot → oSt(ticker) detail popup** | **NOT PRESENT on tile.** Full-screen routes to side-panel summary, not `oSt`. |
| 7 | **Sector color toggle** | **NOT PRESENT.** |
| — | Prompt itself says "Y=Total Return %" is the CURRENT state | **WRONG in prompt** — even then, code used `h.tr` which is TE contribution, not return. Agent was working from a misconception; any "Return" references in the transcript should be disregarded. |

**Drift count: 6 of 7 agent tasks unfulfilled.** This matches the same drift pattern as `portfolio-characteristics-spec.md` (6/6 missing, flagged in `cardChars-audit-2026-04-21.md` §10). Two for two — worth formalizing a **phantom-spec quarantine rule** in `AUDIT_LEARNINGS.md`.

**Recommendation for CoS:**
- Rename `tile-specs/risk-return-scatter-spec.md` → `…-spec.phantom-2026-04-13.md` or archive. Not a live spec.
- Tasks 2, 3, 4, 7 are legitimate PM-facing features. Promote into a fresh spec if PM wants them.
- Task 5 is trivially partially-done — can close most of it in 10 lines.
- Task 6 is the single most valuable fix (drill-click parity) — trivial, one line.

---

## 11. Proposed Fix Queue

### TRIVIAL (agent can apply, ≤5 lines each, no PM judgment)

T1. **Add `plotly_click` drill** on the tile: wire `document.getElementById('scatDiv').on('plotly_click', d => { let t = d?.points?.[0]?.text; if(t && typeof oSt === 'function') oSt(t); });` at the end of `rScat`. Matches cardFacButt / cardFRB-drill pattern.

T2. **Remove PNG button** at L1257. User standing order; same removal applied on other tiles.

T3. **Route hardcoded colors through `THEME()`.** Swap `#ef4444 / #94a3b8 / #10b981` colorscale at L2583 to `[[0,THEME().neg],[0.5,THEME().grid],[1,THEME().pos]]`. (Note: `THEME().grid` is the gridline color, which is close to the desired neutral gray but not identical to `#94a3b8`. If not an acceptable match, add `THEME().mid` = `--txt`.)

T4. **Add `isFinite` filter**: change L2578 to `let hold=(s.hold||[]).filter(h=>h.p>0 && !isCash(h) && isFinite(h.mcr) && isFinite(h.tr));`.

T5. **Add bubble opacity 0.8** to tile marker config (matches FS).

T6. **Bump text label font from 8 → 9** to meet project floor.

T7. **Widen tile margin right** from `r:20` to `r:60` so the colorbar doesn't clip; or move colorbar below (orientation).

T8. **Add X-axis zeroline** to match `renderFsFactorMap` convention: include `zeroline:true, zerolinecolor:THEME().zero, zerolinewidth:1` in the x-axis override.

T9. **Rewrite card-title tooltip at L1254** to match reality. Current: "Marginal contribution to risk vs TE contribution. Bubble size = portfolio weight." Proposed: "Stock-specific TE contribution (x) vs total TE contribution (y). Bubble size = portfolio weight. Color = active weight. Click a dot for details."

T10. **Add CSV export** (⬇ CSV button) emitting per-holding `t,n,sec,p,a,mcr,tr` for the currently-plotted `hold` array. Same pattern as cardHoldings/cardSectors. ~4 lines on the tile + reuse of `exportCSV`.

T11. **Label the card title accurately.** "MCR vs TE Contribution" → "Stock-Specific vs Total TE Contribution" (or the PM's preferred shorthand). One-line text change, but this is **T1-importance**, not design polish.

### NEEDS PM DECISION (cannot apply without call)

P1. **"MCR" rename.** Is PM OK calling `h.mcr` "stock-specific TE" end-to-end (T11 above)? Or keep "MCR" as the shorthand and just document? CLAUDE.md uses both conventions.
P2. **Color semantic: unify tile and FS?** Options (a) both continuous-on-active, (b) both discrete-on-rank, (c) add toggle to both.
P3. **Bubble size cap** for outlier holdings. Numeric choice.
P4. **Label thinning threshold** N. Probably 20–30 by |tr|.
P5. **Add `oSt` click-drill to full-screen too** (currently only opens the side-panel summary). PM preference — maybe side-panel is sufficient, maybe not.

### NON-TRIVIAL / BACKLOG (B-ids for backlog tracker)

B20. **Axis / chart labeling bug fix** — "MCR" isn't MCR. (See §7 #1.)
B21. **Color-semantic unification** tile ↔ full-screen. (§7 #2)
B22. **Historical scatter** blocked by parser — no per-holding history. (§7 #3)
B23. **Quadrant annotations + portfolio-average crosshair.** (§7 #4)
B24. **Axis toggle** (MCR/Return, Exp/Vol, ActWt/TE). Blocked on per-holding return from FactSet. (§7 #5)
B25. **Label-thinning + sizeref normalization.** (§7 #6 + P3)
B26. **Full-screen panel table → standard primitives** (`<table id>`, sort, CSV). (§7 #7)
B27. **Shared `RANK_COLORS` helper** — extract `[#10b981, #34d399, #f59e0b, #fb923c, #ef4444]` used in cardTreemap L2597, FS scatter L5623, FS panel L5659. Zero-behavior-change refactor.
B28. **Phantom-spec quarantine rule** — institutionalize in AUDIT_LEARNINGS.md that any file in `tile-specs/` whose contents begin with JSONL gets renamed `*.phantom-DATE.md` on sight. Two phantom specs identified so far.

---

## 12. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Audit completed; 3-track methodology; identified MCR-labeling risk-domain bug; 6/7 phantom-spec promises unfulfilled | tile-audit CLI |

---

## 13. Sign-off

**Status:** `draft` — do not promote to `signed-off` until at minimum T1 (click-drill), T11 (card title), and B20 (axis label) land. The labeling correctness is a domain-accuracy issue; the tile should not ship to a PM-facing review in its current state.

**Grades:**
- Section 1 (Data Accuracy): **RED** — correct field sources, but visible axis/card labels misrepresent the metric. Risk-PM-facing error.
- Section 4 (Functionality Parity): **RED** — missing click-drill (basic peer-parity), missing CSV export, PNG button still present against user standing order, 6/7 phantom-spec promises unfulfilled.
- Section 6 (Design Consistency): **YELLOW** — hardcoded colors + color-semantic drift + missing zero-line + below-floor label size. All individually trivial, collectively a pattern.

**Overall tile grade: RED** (data-label correctness override). Recommend addressing T1, T2, T11, T3 before any further polish.
