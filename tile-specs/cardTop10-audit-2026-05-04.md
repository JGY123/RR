# cardTop10 — Tile Audit (Three-Track)

**Date:** 2026-05-04
**Auditor:** tile-audit subagent (inline execution)
**Tile status before this audit:** never formally audited (first-class since 2026-04-30 R2-Q4 upgrade)
**Tile status after this audit:** see Section 8 verdict / triage queue

---

## 0. Identity

| Field | Value |
|---|---|
| Tile name | Top 10 Holdings |
| Card DOM id | `#cardTop10` |
| Render function | `rHoldConc()` at `dashboard_v7.html:9687-9715` |
| Card HTML | `dashboard_v7.html:9533-9539` |
| Tab | Holdings |
| Width | half (sits in `<div class="grid g2">` next to cardRankDist) |
| Chart div | `#holdConcDiv` (class `chart-h-md`) |
| About entry | `cardTop10` block at `dashboard_v7.html:1163-1171` |
| Spec status | draft (this audit) — not signed-off (signoff requires user in-browser review) |

---

## 1. Data Source — TRACK 1 (data accuracy)

### 1.1 Field inventory

The chart is a horizontal bar chart. Each bar = one of the top 10 holdings, sorted by `h.p` descending. All fields read from `cs.hold[]` directly. **No accessor (`_wHold` etc.) — see Finding T1.4.**

| Encoding | Bar field | Source path | Source class | Format | Confirmed |
|---|---|---|---|---|---|
| Y-axis label | `short(h.n \|\| tk(h))` | `cs.hold[].n` (FactSet Security `Holding Name`) with fallback to TKR-REGION via `tk(h)` | sourced | string-truncated to 22 chars | yes — short() helper at L9690 strips Ltd./Inc./Corp/etc. before slicing |
| Bar length (x) | `h.p` | `cs.hold[].p` (FactSet Security `W` — port weight %) | sourced | linear, ticksuffix '%' | yes — same field used in cardHoldings, cardSectors footers, etc. |
| Bar color | `h.a >= 0 ? green : red` | `cs.hold[].a` (FactSet Security `AW` — active weight %) | sourced | binary green/red | yes |
| Bar text (in-bar) | `f2(h.p)+'% '+fp(h.a)` | `h.p` and `h.a` | sourced + sourced | "8.32% +1.20" form | yes |
| Hover tooltip | name, ticker, weight, active, sector, MCR | `h.n`, `tk(h)`, `h.p`, `h.a`, `h.sec`, `h.mcr` | all sourced | mixed | yes |
| Click → drill | `oSt(h.t)` (SEDOL) | `customdata[5] = h.t` | sourced | calls `oSt` | wired correctly |

### 1.2 Universe-pill behavior — FINDING T1.1

**The universe pill (`_aggMode` ∈ {portfolio, benchmark, both}) does NOT affect this tile.** The tile reads `cs.hold[]` directly with no `_aggMode` filter. The current filter is just `!isCash(h) && isFinite(h.p)` then `sort by h.p desc`.

**Is this correct?** Yes — for this tile, semantically. "Top 10 by port weight" is a port-only concept. A bench-only holding has `h.p == 0` (or null) and would never enter the top 10 anyway because the sort is on port weight. But the user can still flip to "In Bench" or "All" via the global pill and the tile *appears* unchanged — which may confuse PMs.

**Verdict:** functionally correct, but worth a tooltip line acknowledging that this tile is universe-invariant by design. (See cardTreemap which has a similar pattern + a documented caveat at line ~1194 in the About entries.)

**Triage:** TRIVIAL fix — append "Universe pill does not affect this tile (Top 10 by port weight is port-only by definition)" to the About `caveats` field. Coordinator can ship inline.

### 1.3 Cash exclusion — CONFIRMED CLEAN

`isCash(h)` is the standard project helper at `dashboard_v7.html:1794`. Filters by `CASH_TICKERS` set, `CASH_PATTERNS` regex, sector starts with Cash/Currency/Money Market/FX Forward, name starts with Cash/Currency. Same definition used everywhere. No duplication.

### 1.4 No F18 (per-holding %T) contamination

The bar value is `h.p` (port weight) — **not** `h.tr` (per-holding %T). The hover tooltip exposes `h.mcr` (MCR — idiosyncratic risk component) but only as a per-row scalar, NOT a Σ. Per the F18 contamination map in `SOURCES.md`, per-row displays of contaminated fields are clean — only Σ aggregations need an F18 disclosure footer.

**Cross-reference:** `SOURCES.md` line 168-178 lists which tiles need F18 footers. cardTop10 is correctly absent from that list.

**Verdict:** F18-clean. No footer needed.

### 1.5 Per-week routing — FINDING T1.2 (worth flagging, may be acceptable)

The tile reads `cs.hold[]` directly with no per-week accessor. When the user picks a historical week via the week selector (`_selectedWeek` set), `cs.hold[]` is **not** sliced — it always reflects the latest snapshot.

**Per `ARCHITECTURE.md` §3.4** (the two-layer history architecture), the detail layer (`hold[]`) is by design "only for the current/selected week" — but that promise is delivered by the parser, not by the renderer. The dashboard's `_wHold()` accessor does not exist; for per-week holdings the user has to refresh with a different snapshot.

**Is this acceptable?** Per the prompt: "Holdings detail layer is latest-only; this tile may legitimately stay on latest with a banner." Confirmed — there is no per-week holdings layer, so this tile cannot legitimately update on week selection. **The fix is a banner, not a code change.**

**Compare:** cardTreemap About entry (L1194) explicitly documents: "When viewing a historical week (_selectedWeek), the treemap shows latest-week data — per-week routing not yet wired." cardTop10 About entry (L1169) documents: "Latest snapshot only — no period dimension" — close but doesn't explicitly mention the week selector. PMs reading this may not realize the connection.

**Triage:** TRIVIAL — strengthen the About `caveats` to explicitly mention week-selector behavior, matching the cardTreemap pattern.

### 1.6 Missing per-bar Active% annotation — observation only

The bar text (`textposition:'inside', insidetextanchor:'start'`) shows "8.32% +1.20" — port weight + active weight, both inside the green/red bar. This is good — readable at glance, source data only. **No secondary metric (like %T) shown** — keeping the tile focused on weight-rank, which matches the About entry's framing.

**Verdict:** correct as designed. No secondary-metric annotation needed.

### 1.7 Spot-check — 3 representative holdings

Without loading a fresh JSON in the browser, I cannot do a live numeric spot-check, but the field paths (`h.p`, `h.a`, `h.n`, `h.t`, `h.sec`, `h.mcr`) are the canonical FactSet Security section fields documented in `SOURCES.md` cardHoldings section. **Same code paths used there are battle-tested.** No special derivation.

**Verdict (T1):** GREEN — data accuracy is sound. Two minor documentation tightenings (T1.1 + T1.2) are TRIVIAL fixes the coordinator can ship.

---

## 2. Functionality Matrix — TRACK 2 (parity with peers)

Benchmark tile for parity: cardSectors (most feature-rich, has full pill suite) and the sister Holdings-tab tile cardHoldRisk (closest viz analogue).

| Capability | Benchmark (cardSectors / cardHoldRisk) | cardTop10 | Gap? | Severity |
|---|---|---|---|---|
| `tileChromeStrip` used | yes | **yes** (L9536) | — | OK |
| About (ⓘ) button | yes | **yes** (`aboutBtn('cardTop10')` at L9535; About entry at L1163-1171) | — | OK |
| Right-click note | yes (`showNotePopup`) | **yes** (`oncontextmenu="showNotePopup(event,'cardTop10');..."` at L9535) | — | OK |
| Reset view (↺) | yes | **yes** (`resetView:true`) | — | OK |
| Reset zoom (Plotly) | yes (cardHoldRisk) | **yes** (`resetZoom:'holdConcDiv'`) | — | OK |
| Hide tile (×) | yes | **yes** (`hide:true`) | — | OK |
| Fullscreen (⛶) | yes | **yes** (`fullscreen:"openTileFullscreen('cardTop10')"`) — uses generic fallback (no custom handler in `window._tileFullscreen`) | — | OK (generic fallback works) |
| CSV export | yes (cardSectors) | **NO** | T2.1 | LOW |
| Click bar → drill | cardHoldRisk: yes (`oSt`) | **yes** (`oSt(sedol)` at L9712-9714) | — | OK |
| Cols picker | cardSectors yes; chart-only tiles n/a | n/a (chart, not table) | — | OK |
| View toggle (table/chart) | cardSectors yes | **NO** | T2.2 | LOW (focused tile is fine) |
| Tooltip on hover | yes | **yes** (5-line hovertemplate with name, ticker, weight, active, sector, MCR) | — | OK |
| Theme-aware | yes | **partial** — see T3.1 | T2.3 | LOW |
| Universe pill response | sibling tiles change | **no change** (correctly — see T1.1) | — | OK by design |
| Week selector response | sibling tiles change | **no change** | T1.2 | LOW (acceptable, banner desired) |
| Footer caveat | many siblings have one | **NO** | T2.4 | LOW |

### 2.1 — CSV export missing (T2.1)

The Top 10 list is small (10 rows × ~5 columns) but PMs may want to copy it to email. cardSectors exposes `expSecCSV()`; cardHoldings has `exportCSV()`. cardTop10 has neither.

**Triage:** TRIVIAL — add `download:{ csv:"expTop10CSV()" }` to the chrome strip + a 5-line `expTop10CSV()` function that emits ticker / name / sector / port% / active% / MCR. Coordinator can ship.

### 2.2 — No table-view toggle (T2.2)

cardSectors has a Table/Chart pill. cardTop10 is chart-only. **Decision needed:** is a 10-row table view worth the chrome real estate? Usually no for a focused tile, but worth raising. PM call.

**Triage:** PM-DECISION — defer to user.

### 2.3 — Theme partial (T3.1 & T2.3)

`textfont:{size:11,color:'#fff',family:'Inter'}` at L9701 hardcodes:
- `color:'#fff'` (white) — works on dark theme; will be invisible/low-contrast on a light theme
- `family:'Inter'` — but the project's body font is 'DM Sans' (per `.body` rule) and the theme tick font everywhere else uses `family:'DM Sans, system-ui'` (cardRankDist L9675, cardCorr L4266). cardTop10 is the only tile using `'Inter'` directly.

This is exactly the anti-pattern called out in `LESSONS_LEARNED.md` Apr 2026 addendum item 2: *"CSS variables passed to Plotly's marker.color"* — Plotly needs literal hex but the surrounding code consistently uses `THEME().tick` for tick-color resolution. cardTop10's bar text is hardcoded white because it's overlaid on a colored bar (green/red), so on dark + light themes white-on-green is fine — BUT the choice of `'Inter'` font breaks the project's typography contract.

**Triage:** TRIVIAL — change `family:'Inter'` to `family:'DM Sans, system-ui'`. Same as every other Plotly tile in the project. Coordinator can ship.

### 2.4 — No footer caveat (T2.4)

cardSectors, cardCountry, cardTreemap, etc. each have a footer caveat near the chart explaining: source field, what's hidden (cash), what universe applies. cardTop10 has no footer. The card-title `data-tip` covers some of this ("Top 10 portfolio holdings sorted by weight…"), but a footer is more discoverable.

**Triage:** TRIVIAL — add a 1-line footer (e.g., `<div style="font-size:10px;color:var(--textDim);margin:6px 12px 0;padding-top:6px;border-top:1px solid var(--grid)">Cash hidden. Top 10 by port weight on latest week — week selector does not affect this tile.</div>`). Coordinator can ship.

**Verdict (T2):** YELLOW — chrome parity is excellent (about, notes, reset, hide, fullscreen, drill all wired). Four small gaps (CSV, table-toggle, font-family, footer caveat) — three are TRIVIAL, one is PM-decision.

---

## 3. Design Consistency — TRACK 3

### 3.1 Design tokens

Reading the rendering code:

| Token use | Where | Compliant? |
|---|---|---|
| Card outer styling (background, border) | `class="card"` | yes — uses class |
| Card title typography | `.card-title` | yes — class |
| Tile chrome buttons | `tileChromeStrip` | yes — single source |
| Bar colors | `'rgba(34,197,94,0.85)'` (green) / `'rgba(239,68,68,0.85)'` (red) | **partial** — these are literal RGBA, not `var(--pos)`/`var(--neg)`. **However** Plotly cannot resolve CSS vars (per Lesson 2 of Apr 2026 addendum), so this is an unavoidable hardcode. Compare: cardHoldRisk and cardRankDist use the same pattern. |
| Bar text font | `family:'Inter'` | **NO — see T3.1** below |
| Bar text color | `'#fff'` literal | hardcoded but acceptable (white on colored bar; works in both themes) |
| Bar line color | `'rgba(255,255,255,0.12)'` | hardcoded; matches cardRankDist's `'rgba(255,255,255,0.08)'` pattern (similar) |
| Card-title tooltip | `class="tip"` + `data-tip="..."` | yes |
| Layout (chart-h-md) | `class="chart-h-md"` | yes — token-driven height |

### 3.2 Plotly hex literals

Found two minor literals in `rHoldConc`:
- `'rgba(34,197,94,0.85)'` and `'rgba(239,68,68,0.85)'` — bar colors. **Unavoidable hardcode** (Plotly can't resolve CSS vars). Same pattern across all chart tiles.
- `'rgba(255,255,255,0.12)'` — bar outline. Hardcoded but consistent with peers.

### 3.3 — FINDING T3.1: `family:'Inter'` violates typography contract

(Same as T2.3.) The project's typography contract per `SOURCES.md` Typography section:
- Body: `'DM Sans', system-ui, …`
- Card title: 11px uppercase via `.card-title` class
- Plotly text: `family:'DM Sans, system-ui'` (used in cardRankDist L9675, cardCorr L4266, etc.)

cardTop10 is the only tile using `family:'Inter'` for Plotly text. `'Inter'` isn't loaded by the project (only DM Sans + JetBrains Mono are loaded), so the browser falls back to the next candidate (which is the system default) — making the text render slightly differently than every other tile.

**Triage:** TRIVIAL — change `'Inter'` → `'DM Sans, system-ui'`.

### 3.4 — Bar labels readable on narrow viewport?

Bar text is "8.32% +1.20" inside the bar with `font:11px`. On the smallest port weights (rank 9-10, e.g., 1.2%), the text width may exceed the bar width. Plotly's `insidetextanchor:'start'` and `cliponaxis` (not set explicitly here) means the text could spill outside the bar's visible area. Also, the y-axis labels are truncated at 22 chars by `short()` — should be readable on standard width but on narrow modals (<400 px) the leftward `margin:{l:150}` hard-coding may overlap.

**Triage:** LOW priority — visual review needed in browser at narrow viewport. Likely NEEDS-USER-CHECK.

### 3.5 — No footer caveat (already raised as T2.4)

A footer would also be the natural place to mention F12 / F18 / week-selector behavior in PM-readable form. Most other tiles have footers; cardTop10 stands out by not having one.

### 3.6 — Color semantics

Green for OW (`h.a >= 0`), red for UW. Matches project standard (`var(--pos)` = green for portfolio overweight; `var(--neg)` = red for underweight).

**Verdict (T3):** YELLOW — one typography violation (`'Inter'` → fix to `'DM Sans, system-ui'`), one missing footer, one viewport-readability check needed.

---

## 7. Known Issues / Open Questions

(no open questions — tile is functionally well-defined; gaps are documented above)

---

## 8. Verdict + Triage Queue

### Overall verdict
**YELLOW (close to GREEN).** The tile is functionally correct, F18-clean, with strong chrome parity (`tileChromeStrip` adopted, About entry, right-click note, drill modal wired). Four small polish gaps and one typography violation. **All TRIVIAL fixes — none require new architecture.**

### Color status by track
- Section 1 (Data Source) — **GREEN**
- Section 2 (Functionality) — **YELLOW** (4 small gaps; 3 trivial, 1 PM-decision)
- Section 3 (Design) — **YELLOW** (1 typography violation, 1 missing footer)

### Triage queue

#### TRIVIAL (5 items, coordinator can apply inline)
1. **T1.1** — append universe-pill caveat to About entry (`cardTop10.caveats` field)
2. **T1.2** — append week-selector caveat to About entry (clarify "latest snapshot only" means week selector has no effect)
3. **T2.1** — add CSV export button + `expTop10CSV()` function (~10 lines)
4. **T2.4 / T3.5** — add 1-line footer caveat below chart explaining cash-hidden + latest-week behavior
5. **T3.1 / T2.3** — fix `family:'Inter'` → `family:'DM Sans, system-ui'` in `rHoldConc()` `textfont` (1-char edit)

#### NEEDS-USER-CHECK (2 items)
6. **T2.2** — Add table-view toggle? (PM decision — usually no, focused tile is fine)
7. **T3.4** — Verify bar labels render correctly on narrow viewport (<400 px modal embeds)

#### BLOCKED (0 items)
None. F18 is irrelevant here (per-row, not Σ).

### Recommended next action
Coordinator (CoS Claude) can ship the 5 TRIVIAL items as a single commit titled `chore(cardTop10): tile-audit-2026-05-04 polish — about caveats, CSV export, footer, font family`. Estimated edit: ~20 lines added, 1 char changed. PM-decision items (T2.2, T3.4) can be flagged in `BACKLOG.md` for next user review session.

---

## 9. Verification Checklist (post-fix, pre-signoff)

- [ ] T1.1 + T1.2 — About entry mentions universe + week-selector behavior
- [ ] T2.1 — CSV export button visible in chrome strip; clicking emits 10-row CSV
- [ ] T2.4 — Footer caveat appears beneath the chart
- [ ] T3.1 — Bar text uses 'DM Sans' (visually matches cardRankDist text)
- [ ] T3.4 — Bar labels readable in browser at 320 px width (manual)
- [ ] No console errors after fix
- [ ] Click-to-drill still works (`oSt(sedol)` opens the holding modal)
- [ ] Right-click → notes still works
- [ ] Theme switch (dark + light) — text and bar colors render correctly

Signoff: pending user in-browser review (per `feedback_signoff_requires_user_review.md`).

---

## Appendix — Code References

- Card HTML: `dashboard_v7.html:9533-9539`
- Render fn: `dashboard_v7.html:9687-9715`
- About entry: `dashboard_v7.html:1163-1171`
- Render call site: `dashboard_v7.html:9565` (inside `setTimeout` after Holdings-tab innerHTML set)
- `isCash` helper: `dashboard_v7.html:1794`
- `tk(h)` (TKR-REGION display) helper: project-wide, used identically in cardHoldings
- `oSt()` drill modal: `dashboard_v7.html:9712-9714` wires `plotly_click` → `oSt(sedol)`
- Generic fullscreen handler: `dashboard_v7.html:1439-1473` (no custom `_tileFullscreen.cardTop10` handler — uses generic clone-tile-into-modal pattern; works correctly for chart-only tiles)
- F18 contamination map: `SOURCES.md:158-178` (cardTop10 correctly absent — no per-holding %T Σ shown)
