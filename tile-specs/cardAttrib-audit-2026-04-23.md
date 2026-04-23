# Tile Spec: cardAttrib (+ facWaterfallDiv) — Audit v1

> **Audited:** 2026-04-23 | **Auditor:** Tile Audit Specialist (CLI) | **Batch:** 4
> **Status:** 🟡 YELLOW overall (data GREEN, functionality YELLOW, design YELLOW)
> **Scope:** cardAttrib (Factor Attribution — 18 Style Snapshot table + bar chart) AND the orphan "Factor Attribution — Return Impact" card containing `#facWaterfallDiv` rendered by `rFacWaterfall(s)`. Both live in the Exposures tab.
>
> **Numbering convention:** Non-trivial / cross-tile findings numbered **B50–B6x** (per ask, avoiding the cardMCR B39-range collision).

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Attribution (table + bar chart) + Factor Attribution Waterfall |
| **Card DOM id (table)** | `#cardAttrib` (L1306) |
| **Card DOM id (waterfall)** | **none** — the waterfall lives in an anonymous `<div class="card">` at L1182–1185, no id |
| **Render function — table** | `rAttribTable()` at `dashboard_v7.html:L2003–L2064` |
| **Render function — waterfall** | `rFacWaterfall(s)` at `dashboard_v7.html:L1349–L1378` |
| **Drill modal (table row)** | `oDrAttrib(name)` at L2067–L2134 → `#metricModal` / `#metricContent` |
| **Drill modal (waterfall bar)** | **none** — no `plotly_click` handler. Would naturally map to `oDrF(name)`. |
| **Render targets** | `#attribTableArea` (L1324), `#attribChartDiv` (L1325, 280px), `#facWaterfallDiv` (L1184, height computed inline) |
| **Tab** | Exposures (`tab-exposures`) — **row 3** (waterfall) and **row 12** (cardAttrib), not adjacent |
| **Grid row / width** | Both full-width (`grid-column:1/-1` implicit — each is its own card with no `g2` wrapper) |
| **Data source (table)** | `cs.snap_attrib` — keyed by name → `{exp, ret, imp, dev, cimp, full_period_imp, full_period_cimp, hist, risk_contr}` |
| **Data source (waterfall)** | `s.factors[]` filtered by `f.imp!=null` |
| **Parser** | `_extract_snapshot` (`factset_parser.py:L646–L705`, "18 Style Snapshot" section) + `_build_factor_list` (L847–L865) |
| **Week-selector aware** | ❌ both read latest directly (waterfall uses `s.factors`, table uses `cs.snap_attrib`) — see §7 B52 |
| **Spec status** | `draft → audited` |

**Structural note — the two cards are not wired together.** The Exposures-tab HTML places the waterfall in an anonymous card near the top (row 3, after cardFacButt) and places cardAttrib far below (row 12). They share `s.factors` / `cs.snap_attrib` semantics but there is no visual or navigational link between them. Audit treats both in scope per the user's ask; recommend they be co-located or visually labeled as siblings (§7 B60).

---

## 1. Data Source & Schema

### 1.1 Primary data sources

**Table (`rAttribTable`)** — `cs.snap_attrib`:
- Keys: item names (country / industry / currency — classified client-side by `classifyAttrib(name)` at L1996–L2001).
- Values: `{exp, ret, imp, dev, cimp, full_period_imp, full_period_cimp, hist[], risk_contr}` from `_extract_snapshot` (`factset_parser.py:L694–L704`).
- **Per-week history** preserved as `item.hist[]` → consumed by `oDrAttrib` drill but **not** by the tile itself (tile is latest-week only).

**Waterfall (`rFacWaterfall`)** — `s.factors[]`:
- Same `s.factors` as cardFacButt / cardFacDetail / cardFRB / Risk Decomp Tree.
- Filters `f.imp!=null` → rendering a horizontal bar per factor with `f.imp` as the bar length.
- Sorted descending by `imp` (most-positive top), then `autorange:'reversed'` on yaxis so positive bars stack at the top visually (L1351, L1369).

### 1.2 Field inventory (table)

| # | Label | Field | Type | Source | Formatter | Sort | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Factor | `i.name` | string | snap_attrib key | raw + emoji icon | ✅ textContent | 🌍 country / 🏭 industry / 💱 currency icon prepended (L2028, L2033) |
| 2 | Exposure | `i.exp` | number | SNAP_EXP → `exp` | `fp(i.exp,2)` (signed) | 🟡 no `data-sv` — textContent → NaN if "—" | parser L674 = "Average Active Exposure" |
| 3 | Std Dev | `i.dev` | number | SNAP_DEV → `dev` | `f2(i.dev,1)` | 🟡 no `data-sv` | parser L677 = "Factor Standard Deviation" |
| 4 | Impact (%) | `i.full_period_imp` | number | `summary.imp` if present else `latest.cimp` | `fp(...,2) + '%'` | 🔴 **BROKEN** — `+"+1.23%"` = NaN in `sortTbl`, falls through to `localeCompare` on strings | "Cumulative return attribution over full period" per subtitle (L2046) |

**Note on "full_period_imp":** parser logic at L682–L701 detects a trailing summary row (last period spans inception → current) and uses `summary.imp`. If no such row, falls back to `latest.cimp` (cumulative impact at last weekly period). These are semantically different columns combined into one field — possible PM clarification needed (§7 B51).

### 1.3 Field inventory (waterfall)

| # | Encoding | Field | Type | Source | Example | Notes |
|---|---|---|---|---|---|---|
| 1 | y (bar label) | `f.n` | string | factor name | "Value" | parser-order preserved before sort |
| 2 | x (bar length) | `f.imp` | number | SNAP_IMP → `imp` | +0.42 | Compounded Factor Impact (this week's latest-period value from 18 Style Snapshot, NOT cumulative) |
| 3 | color | sign of `f.imp` | — | `'#10b981'` if ≥0 else `'#ef4444'` | — | 🟡 **hardcoded hex**, not `THEME().pos`/`.neg` (L1363) |
| 4 | axis title | "Impact (%)" | — | static | — | — |
| 5 | period annotation | `s.current_date` | date | latest weekly | "Period ending Apr 18, 2026" | Shown at top-center when `current_date` present (L1359, L1373) |

**Not rendered but available on `s.factors[]`:** `f.e`, `f.bm`, `f.a` (exposures), `f.c` (risk contrib), `f.ret` (blank per FactSet — §1.5), `f.dev`, `f.cimp`, `f.risk_contr`. The bar label shows only the factor name + impact; richer hover would help.

### 1.4 Derived / computed fields

| Field | Computation | Location | Notes |
|---|---|---|---|
| `xmax` (waterfall symmetric range) | `Math.ceil(maxAbs*10)/10 + 0.1` then rounded 2-dp | L1354–L1355 | Guarantees symmetric axis so positive/negative sides are comparable. ✅ good viz hygiene. |
| `maxAbs` | `Math.max(...vals.map(Math.abs), 0.1)` | L1354 | `0.1` floor prevents zero-range axis when all impacts are tiny. ✅ |
| `periodStr` | `parseDate(s.current_date).toLocaleDateString(...)` | L1358–L1359 | Fallback: last entry of `s.available_dates`. ✅ |
| waterfall height | `Math.max(160, facs.filter(f=>f.imp!=null).length*32)+20` | L1184 | No upper cap; 40 factors → 1300px tall; 60 factors → 1940px. See §6.1. |
| chart sort (table) | Pre-render sort via `attribSort` select: `imp`/`exp`/`dev` | L2022–L2024 | `imp` and `exp` sort by `abs()`, `dev` sorts by raw. 🟡 inconsistent — `dev` doesn't use abs because it's always positive, but the three sort modes are not semantically symmetric. |
| table top-N slice | `items.slice(0,20)` | L2027 | Hardcoded 20. Bar chart slices separately to top 10 (L2049). Both caps should be configurable or shown explicitly. |
| `classifyAttrib(name)` | currency-set lookup → length/format heuristic → else "industry" | L1996–L2001 | 🟡 **heuristic classification is fragile.** See §7 B55. |

### 1.5 Ground truth verification

- [x] Parser traced: `_extract_snapshot` at L646–L705 reads the "18 Style Snapshot" section; fields map to `SNAP_EXP`/`SNAP_IMP`/`SNAP_DEV`/`SNAP_CIMP`/`SNAP_RISK_CONTR` per `CANON_MAP` (L82–L89).
- [x] **`SNAP_RET` ("Compounded Factor Return") — BLANK PER FACTSET PENDING ITEM.** Per CLAUDE.md §Pending from FactSet, this column is "present but blank." Parser captures into `item.ret` / `f.ret`. **Verified this tile does NOT display `.ret`** — `rAttribTable` renders exp/dev/full_period_imp only, `rFacWaterfall` renders `f.imp` only. ✅ neither card shows a blank column to users. `f.ret` IS surfaced on cardFacDetail L1780 and Risk tab L3074, but those are out of scope.
- [x] `full_period_imp` resolution logic (parser L682–L701) verified: uses summary row if detected, else falls back to `latest.cimp`. This is a **combined field** — the tile's "Impact (%)" column shows one or the other depending on file structure. Documented but not surfaced to the user.
- [x] Waterfall's `f.imp` comes from the latest-week entry (most recent weekly period). Parser L693: `latest = weekly[-1]`. ✅
- [x] 31-col Factor Attribution section confirmed per CLAUDE.md §CSV Column Schemas: "5 periods × 5 cols + prefix." Parser expands into per-period history (`item.hist`) not per-period columns.
- [ ] **JSON spot-check pending:** cannot verify exact numbers without a loaded JSON (AUDIT_LEARNINGS §Known blockers). Section 1 is structurally sound; row-level numeric accuracy deferred to rr-data-validator.

### 1.6 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `cs.snap_attrib` empty / missing | `'<p style="color:var(--txt);font-size:12px">No attribution data</p>'` (L2006) | ✅ guard present, matches pattern |
| `s.factors` empty OR no `f.imp!=null` | `if(!facs.length...)return;` (L1352) → **silent return, stale render persists** | 🔴 **Pattern B violation** per AUDIT_LEARNINGS §Viz-renderer pattern — should write empty-state `<p>` into `facWaterfallDiv` rather than silent-return. See §7 B53. |
| `i.exp == null` | `fp(null,2)` → `'—'` | ✅ formatter handles it |
| `i.full_period_imp == null` | `fp(null,2)` → `'—'`, but then `${...}%` yields "—%" | 🟡 **minor cosmetic** — the "%" suffix is concatenated outside `fp()`, so null shows as "—%" not "—" (L2036) |
| `i.exp == 0` | `expCls = ''` (L2031) — no color applied, renders in default text color | ✅ correct |
| `f.imp == NaN` or `Infinity` | `NaN!=null` passes the filter; `Math.abs(NaN)=NaN` → `Math.max(NaN, 0.1)=NaN` → axis broken | 🟡 missing `isFinite` guard — inherited Pattern A. See §7 B57. |
| All `f.imp == 0` | Filter passes (0!=null), bars render with zero length, `maxAbs=0.1` → axis `[-0.2, +0.2]`. Visually empty. | 🟡 no "no impact" message. |
| `items.length > 20` | Silently truncated to 20 (L2027); chart to 10 (L2049). Subtitle says "N items" but user sees top 20 only. | 🟡 subtitle wording is correct but no "showing top 20 of N" affordance. |
| Duplicate names across categories | `Object.entries(sa)` keys are unique per parser → collision would have lost data upstream; cannot collide client-side. | ✅ |

**Section 1 verdict: 🟢 GREEN (data integrity) / 🟡 YELLOW (empty-state for waterfall + isFinite + heuristic classifier).** Crucially, no number displayed depends on the blank `SNAP_RET` column. The `full_period_imp` field is semantically conflated across two sources (summary vs latest.cimp) without user-visible disclosure — acceptable for an audit-pass but noted.

---

## 2. Columns & Dimensions Displayed

### 2.1 Table (cardAttrib)

Columns in DOM order (L2040–L2045):
1. **Factor** — icon + name; `<td>` no `data-sv`, no `data-col`.
2. **Exposure** — `class="r {pos|neg}"` color-on-sign via `fp()`; no `data-sv`.
3. **Std Dev** — `class="r"`; no `data-sv`; no pos/neg (dev is always ≥0).
4. **Impact (%)** — `class="r"` with `color:var(--pos)` or `var(--neg)` inline; no `data-sv`; suffix `%`.

**Missing primitives** (per AUDIT_LEARNINGS §Primitives checklist):
- [x] `<table id="tbl-attrib">` ✅
- [x] `<th onclick="sortTbl('tbl-attrib',N)">` ✅ all 4 columns wired
- [ ] ❌ No `data-sv` on any numeric cell → Impact column sort BROKEN (falls through to localeCompare on "+1.23%")
- [ ] ❌ No `data-col` on any `<th>` or `<td>` → column-picker retrofit blocked
- [x] `class="clickable"` + `onclick="oDrAttrib(...)"` on rows ✅
- [x] Empty-state fallback ✅
- [x] CSV export button at L1321 ✅
- [x] No PNG button on cardAttrib ✅ (per no-PNG rule)

### 2.2 Bar chart (`attribChartDiv`, inside cardAttrib)

Fixed 280px, top-10 by sort order of `items` (same sort as table). Horizontal bars:
- **y** = `i.name` (autorange reversed)
- **x** = `i.full_period_imp`
- **color** = `'#10b981'` if impact>0 else `'#ef4444'` (🟡 hardcoded hex at L2054)
- **text** = `fp(i.full_period_imp,2)+'%'` outside bars (L2055)
- **hover** = "Impact / Exposure / Std Dev" via `customdata` (L2057–L2058) ✅ rich hover
- **No `plotly_click` handler** → bar click does not drill. 🟡 Gap. See §7 B56.

### 2.3 Waterfall (`facWaterfallDiv`, orphan card at L1182)

- **y** = `f.n`, **x** = `f.imp`, horizontal bar, symmetric axis.
- **color** = sign-of-imp via hardcoded `#10b981` / `#ef4444` (L1363)
- **hover** = `<b>%{y}</b><br>Impact: %{x:+.3f}%`
- **period annotation** = centered top (L1373–L1376)
- **No `plotly_click` handler** → can't drill a factor from the waterfall bar even though `oDrF(name)` is a function. 🟡 **This is the waterfall equivalent of the cardFacButt plotly_click fix.** See §7 B56.

### 2.4 Encoding drift across the three views

| View | X / size | Color | Click | Sort |
|---|---|---|---|---|
| `rAttribTable` — table rows | — | `pos`/`neg` via `fp()` class + inline color on Impact | `oDrAttrib(name)` per row ✅ | user-select dropdown + thead-click (partial) |
| `rAttribTable` — bar chart below | `full_period_imp` | hardcoded `#10b981`/`#ef4444` | ❌ none | pre-sorted by `attribSort` |
| `rFacWaterfall` — orphan card | `f.imp` | hardcoded `#10b981`/`#ef4444` | ❌ none | internal desc sort |

**Material finding:** the **bar chart inside cardAttrib** and the **waterfall orphan card** both show a horizontal-bar-with-impact story, but they draw from **different datasets**:
- cardAttrib bar chart = top-10 items from `snap_attrib` (countries + industries + currencies combined, `i.full_period_imp`)
- waterfall orphan card = all factors from `s.factors` with `f.imp`
They look similar but are answering different questions. Without tighter labeling, a user scrolling the Exposures tab would see two near-identical horizontal-bar charts with no indication they're different data. **See §7 B60 — one of the two should be relabeled or moved.**

---

## 3. Visualization Choice

### 3.1 Chart / layout types

| Component | Type | Height | Responsive? |
|---|---|---|---|
| cardAttrib table | `<table>` w/ 20 rows cap | content-flow | ✅ CSS reflow |
| cardAttrib bar (attribChartDiv) | Plotly horizontal bar, top-10 | 280px fixed | ✅ `plotCfg.responsive:true` |
| Waterfall (facWaterfallDiv) | Plotly horizontal bar, all factors | dynamic `max(160, N*32)+20`px | ✅ |

### 3.2 Color semantics

- **Table rows — Impact column:** inline `color:${i.full_period_imp>0?'var(--pos)':'var(--neg)'}` ✅ token-based — correct per AUDIT_LEARNINGS §Viz-renderer pattern.
- **Table rows — Exposure column:** `class="r {expCls}"` where `expCls='pos'|'neg'|''` — relies on `.pos`/`.neg` CSS classes ✅ token-based.
- **cardAttrib bar chart:** hardcoded `#10b981`/`#ef4444` at L2054. 🟡 should use `THEME().pos`/`.neg`.
- **Waterfall bars:** hardcoded `#10b981`/`#ef4444` at L1363. 🟡 same pattern as cardTreemap / rScat — extract once, fix everywhere.
- **Waterfall axis / grid / text:** uses `THEME()` values (L1360, L1367–L1371) ✅ theme-aware for axes.
- **cardAttrib bar axis:** uses `plotBg` helper ✅ theme-aware via shared token.

### 3.3 Axis scaling

- **Waterfall:** symmetric `[-xmax, +xmax]` with a floor of `±0.2`. ✅ forces zero-centered.
- **cardAttrib bar:** default Plotly auto-range. 🟡 non-symmetric — a strategy with all-positive impacts will push zero to the left edge; a diversifying factor would appear as a tiny nudge rather than a clear negative bar. Minor but worth aligning.

### 3.4 Empty state

- Table: ✅ `<p>No attribution data</p>` written to `attribTableArea` (L2006).
- cardAttrib bar chart: 🟡 when `sa` is empty, `rAttribTable` short-circuits early — `attribChartDiv` keeps its PRIOR render from a previous strategy. **Pattern B leak.** See §7 B53.
- Waterfall: 🔴 silent return (L1352) — stale render persists on strategy switch if new strategy has no factors. **Pattern B violation.** Fix = write empty-state `<p>` into the div.

### 3.5 Loading state

None. Both render synchronously inside the `setTimeout(...,50)` pipeline at L1341.

### 3.6 Responsive behavior

- Table: natural reflow, rows remain fixed height.
- Bar charts: `plotCfg.responsive:true`.
- Waterfall inline height `max(160, N*32)+20` — the div does NOT rebuild on window resize (height baked at render). Acceptable: strategy switch re-renders anyway.

---

## 4. Functionality Matrix

**Benchmark tiles:** cardFacDetail (gold for factor tables), cardFacButt (sibling viz, has plotly_click wiring at L2386), cardFRB (fellow factor tile, audited 2026-04-21).

### 4.1 Capability matrix

| Capability | Table (cardAttrib) | Bar (attribChartDiv) | Waterfall | Benchmark comparison |
|---|---|---|---|---|
| **Sort (pre-render dropdown)** | ✅ 3 modes (imp / exp / dev) via `attribSort` | ✅ same (shares `items`) | ❌ internal desc only | cardFacDetail has Primary/All toggle — different axis |
| **Sort (header click)** | 🟡 wired but Impact broken (no `data-sv`) | N/A | N/A | cardFacDetail L1755 uses `data-sv` ✅ |
| **Filter** | ✅ 4-way category select (all/country/industry/currency) | ✅ inherits | ❌ no filter — all factors | cardFacButt offers Primary/All, same flavor |
| **Column picker** | ❌ no `data-col` on th/td → blocked | N/A | N/A | cardFacDetail has ⚙ Cols via `applyFacColVis` |
| **Row click → drill** | ✅ `oDrAttrib(name)` → metricModal with cum-impact line + weekly bars | N/A | N/A | cardFacDetail L1775 → `oDrF` |
| **Bar/slice click → drill** | N/A | ❌ no `plotly_click` handler on `attribChartDiv` | ❌ no `plotly_click` handler on `facWaterfallDiv` | cardFacButt L2386 wires `plotly_click → oDrF(y)` ✅ |
| **Right-click context menu** | 🟡 global td-only; does nothing on Plotly SVG | 🟡 same | 🟡 same | cardHoldings has cell-level menu |
| **Card-title right-click → note popup** | ❌ **missing** — no `oncontextmenu="showNotePopup(event,'cardAttrib');return false"` on card-title (L1308) | N/A | ❌ **missing** — waterfall card has no title-right-click; and the card has **no id at all** so `showNotePopup(event,'???')` has nothing to key notes on | cardFacButt L1156, cardFRB L1285, cardTreemap L1263 all have it |
| **Note badge** | ❌ blocked by the above | N/A | ❌ blocked | — |
| **PNG export** | ✅ **absent** (per project rule) | — | — | ✅ good |
| **CSV export** | ✅ `exportCSV('#tbl-attrib','attribution')` L1321 | ❌ (data is the same as table so low priority) | ❌ — would dump `s.factors[f.n,f.imp]` | ✅ table covered |
| **Full-screen modal** | ❌ | ❌ | ❌ | cardTreemap / cardScatter have ⛶; cardFRB has tile-wide drill |
| **Keyboard drill (Enter/Space on row)** | ❌ rows have no `tabindex` | N/A | N/A | Summary cards L1110 have `tabindex="0" role="button"` |
| **Toggle views (Chart/Table)** | ❌ always both | — | — | cardCountry, cardRegions, cardGroups have Chart/Table toggle |
| **Range selector** | N/A | N/A | N/A | — |
| **Legend** | N/A | Plotly default (hidden for single trace) | Plotly default (hidden) | — |
| **Hover tooltip** | ✅ row-click hint in title tip L1308 | ✅ rich hover with custom data | ✅ "Impact: ±0.3f%" | ✅ |
| **Themed axes / text** | ✅ via `plotBg` | ✅ via `plotBg` + `THEME().tick` | ✅ `T.tick`/`T.tickH`/`T.grid`/`T.zero` | — |
| **Themed bar colors** | N/A (uses `var(--pos)`/`var(--neg)` in table) | ❌ hardcoded hex | ❌ hardcoded hex | — |
| **Period label on chart** | ❌ | ❌ | ✅ "Period ending …" annotation L1373 | Unique to waterfall |
| **Week-selector aware** | ❌ reads `cs.snap_attrib` (latest) | ❌ | ❌ reads `s.factors` (latest) | Inherits AUDIT_LEARNINGS shared blind spot |
| **isFinite guard before map** | ❌ | ❌ | ❌ | cardFacButt L2334 has `isFinite(f.a)` |
| **Table cells carry `data-col`** | ❌ | N/A | N/A | cardSectors has it; cardRegions/cardGroups don't (AUDIT_LEARNINGS) |
| **Table cells carry `data-sv`** | ❌ — Impact sort BROKEN | N/A | N/A | AUDIT_LEARNINGS §Sort anti-patterns |

### 4.2 Interaction parity gaps

1. **Waterfall bar click should drill into the factor** — mirror cardFacButt pattern (L2386):
   ```js
   let el=document.getElementById('facWaterfallDiv');
   if(el&&el.on){el.on('plotly_click',d=>{if(d?.points?.[0]?.y && typeof oDrF==='function')oDrF(d.points[0].y);});}
   ```
   Zero-risk, 3-line fix. §7 B56.

2. **cardAttrib bar click should drill into the item** — mirror the same pattern, calling `oDrAttrib(point.y)` (since attribution items are not in `s.factors`, they need `oDrAttrib` not `oDrF`):
   ```js
   let el2=document.getElementById('attribChartDiv');
   if(el2&&el2.on){el2.on('plotly_click',d=>{if(d?.points?.[0]?.y)oDrAttrib(d.points[0].y);});}
   ```

3. **No keyboard access to drill on rows.** Each row has `onclick` but no `tabindex`, no `role="button"`, no `onkeydown`. Matches cardFRB / cardScatter gap. Trivial fix: add `tabindex="0" role="button"` + a global `.clickable` keydown handler.

4. **Header row-click sort broken on Impact column** (no `data-sv`). §7 B54.

**Section 4 verdict: 🟡 YELLOW** — table drill works, filter/sort dropdown works, CSV works. But click-parity on the two Plotly bar charts is missing, keyboard access absent, cardAttrib's note-popup wiring absent, and the waterfall card has no id at all (blocks notes + test hooks).

---

## 5. Popup / Drill / Expanded Card

### 5.1 `oDrAttrib(name)` — table drill (L2067–L2134)

Opens `#metricModal`:
- **Header:** `${name}` + classifyAttrib label (Country/Industry/Currency)
- **Top strip (grid g4):** 4 stat cards — Cumulative Impact | Current Exposure | Factor Std Dev | Weeks
- **Chart 1 (`attribDrillChart`, 300px):** Cumulative Impact line (FactSet `cimp`) + "Running Sum (verify)" overlay (legend-only, dashed indigo) — a client-side sanity check of the CSV cumulative via simple addition. Confirms PM/FactSet TBD on "true compounding." Comment at L2083: `"Simple addition for display (close enough for weekly, true compounding TBD after FactSet call)"` — **this is flagged in code as a pending item.** Align with CLAUDE.md §Pending from FactSet.
- **Chart 2 (`attribDrillBars`, 160px):** Weekly impact bars, pos/neg tinted with `rgba(16,185,129,0.6)`/`rgba(239,68,68,0.6)` (🟡 hardcoded rgba, not `THEME()`).
- **Rangeslider** on `attribDrillChart` ✅
- **Hovermode:** `x unified` ✅

### 5.2 Modal functionality parity

| Aspect | Present? | Notes |
|---|---|---|
| Escape-close | ✅ `metricModal` registered in `ALL_MODALS` L4712 |
| Click-outside-close | ✅ same mechanism |
| Sort / Filter | N/A — single-item view |
| Export CSV of weekly history | ❌ could expose `item.hist` as CSV |
| Per-week click drill | ❌ bars not clickable into a per-week detail |
| Theme-aware colors | 🟡 partial — axes yes, weekly bars `rgba(...)` hardcoded L2126 |
| Week-selector interaction | ❌ modal always shows the full `hist` from inception; does not respect `_selectedWeek` |
| Running-sum overlay correctness | ⚠️ **flagged in code** as approximate; real compounding blocked on FactSet response |

### 5.3 Modal data integrity note

The modal's two-line overlay (FactSet `cimp` vs client-side running sum) is a **defensive cross-check**, not a gimmick — it's effectively a live assertion that the FactSet-supplied cumulative matches a naïve sum of weekly impacts. Useful for PM audit, though the line is hidden by default (`visible:'legendonly'`). If they ever materially diverge in a strategy, the user will not see it unless they flip the legend. Consider: compute the max-delta and surface a warning if it exceeds 0.5%. Low-priority polish.

**Section 5 verdict: 🟢 GREEN** (structurally sound, escape-close works, cross-check overlay is thoughtful) **/ 🟡 YELLOW** on theme-drift (hardcoded rgba on weekly bars) and lack of CSV export for `hist`.

---

## 6. Design Guidelines

### 6.1 Density

| Dimension | Value | Notes |
|---|---|---|
| Card padding | `.card` default (16px) | ✅ |
| Table font — th | 10px | ✅ matches gold standard (cardSectors) |
| Table font — td | 11px | ✅ |
| Bar chart tick | 9px xaxis / 10px yaxis (waterfall) | ✅ within 9–13 scale |
| Bar chart margin | `l:10, r:20, t:28 (or 10), b:36` waterfall — 🟡 left margin of 10 is **very tight** for "Value"/"Momentum" labels; `automargin:true` on yaxis (L1370) should rescue it. Verify at render. | |
| Waterfall dynamic height | `32px/factor + 180px` padding | 🟡 **no upper cap**. A strategy with 40 factors → 1300px tall card. 60 factors → 1940px. The card would dwarf its neighbors on the Exposures tab. Consider `Math.min(1000, …)` + scroll. |
| Chart emoji on table row | 10px `margin-right:4px` | ✅ small + subtle |
| Category select / Sort select | 11px font, 4px/8px padding | ✅ matches density floor |
| Subtitle under table | 9px | ✅ small, unobtrusive |

### 6.2 Emphasis & contrast

- Table Impact column uses inline `font-weight:600` + semantic color (L2036) ✅ strong emphasis for the key metric.
- Exposure column uses `.pos`/`.neg` class but no boldface. Implicit hierarchy: Impact is the headline, Exposure is secondary.
- Emoji icons (🌍/🏭/💱) are a lightweight classifier cue — ✅ work fine in dark theme; verify in light.
- Hover styles: Plotly-default on bars; rows have `.clickable` hover.
- The two "horizontal-bar" charts (cardAttrib bar at the bottom of cardAttrib, and the waterfall at the top of the Exposures tab) are **visually very similar** but answer different questions. See §2.4.

### 6.3 Alignment

- Numeric columns right-aligned (`class="r"`) ✅
- Factor name left-aligned ✅
- Modal stat strip centered ✅

### 6.4 Whitespace

- Waterfall: `margin:{l:10,r:20,t:28,b:36}` — tight.
- cardAttrib bar: uses `plotBg.margin` + `l:180` override for name labels (L2062) ✅ sensible.
- cardAttrib table → chart spacing: `margin-top:12px` on `attribChartDiv` (L1325) ✅.

### 6.5 Cross-tile design consistency

| Concern | Observation |
|---|---|
| Hardcoded hex palette in Plotly bars | cardAttrib bar (L2054), waterfall (L1363), weekly bars in drill (L2126) — three sites using the same `#10b981`/`#ef4444` literals. Should all consume `THEME().pos`/`.neg`. Same as cardTreemap + cardMCR + cardScatter fixes already queued. See §7 B58. |
| Period annotation style | Waterfall shows "Period ending …" as a top-center annotation; cardAttrib does NOT. Inconsistent — adding a period annotation to cardAttrib would anchor what timeframe "Impact" refers to. |
| Note-popup wiring | cardAttrib card-title has no `oncontextmenu`. Waterfall card has no id — can't have one. See §7 B50. |
| Signed-value formatter | `fp(v,d)` used consistently ✅ |
| Full-screen (⛶) button | Absent on both. Given the waterfall's dynamic height can reach 1300px, a dedicated FS modal would allow proper exploration with filtering. Consider. |
| Subtitle summary line | cardAttrib has "`${items.length} items · Impact = compounded return attribution over full period · Click row for time series`" — ✅ this explicitly surfaces the denominator / click affordance / item count. Model pattern for other tiles. |

### 6.6 Motion / interaction feedback

- Row hover (Plotly default) ✅
- Bar hover (Plotly default) ✅
- Empty state = static `<p>` (no skeleton) ✅
- Mode-bar hidden via `plotCfg` ✅

**Section 6 verdict: 🟡 YELLOW** — good density, good emphasis, good subtitle pattern; but (a) hardcoded hex × 3 sites, (b) uncapped waterfall height, (c) period annotation asymmetry, (d) no note-popup on title.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Classification | Resolution path |
|---|---|---|---|---|
| **B50** | Waterfall card has NO `id` at all — L1182 `<div class="card" style="margin-top:16px">` — blocks `showNotePopup`, blocks CSS-id targeting, blocks test hooks, blocks `screenshotCard` (not that we want PNG, but the absent id is structural). | Medium | Trivial | Add `id="cardAttribWaterfall"` (or similar) + title `<div>` with the tip/oncontextmenu wiring used elsewhere. |
| **B51** | `full_period_imp` conflates two semantically-different fields — parser resolves `summary.imp` if present else `latest.cimp`. User-facing "Impact" column may mean "full period compounded impact" OR "cumulative of weekly impacts to-date" depending on file structure. | Low (FactSet semantics, not display) | Non-trivial (PM + FactSet call) | Tooltip disclaimer + consult FactSet whether the summary row is guaranteed. |
| **B52** | Both cardAttrib table and waterfall ignore `_selectedWeek` — the Exposures tab banner promises "viewing historical week" but these two always show latest. Same class of issue as cardFRB, cardFacButt. | Medium | Non-trivial | Blocked on historical `snap_attrib` / per-week `factors` plumbing, neither exists today. Log on BACKLOG with B6/B12 (cardRegions/cardFRB history blockers). |
| **B53** | Waterfall silent-returns on empty (`if(!facs.length)return` L1352) — leaves stale prior render on strategy switch. Same anti-pattern as `rRegChart` flagged in AUDIT_LEARNINGS. | Medium | Trivial | Replace silent return with `document.getElementById('facWaterfallDiv').innerHTML='<p style="color:var(--txt);font-size:12px;text-align:center;padding:40px">No factor impact data</p>';` |
| **B54** | Impact column sort BROKEN — missing `data-sv`. `sortTbl` tries to `Number("+1.23%")` → NaN → falls through to string-sort (wrong order). | Medium | Trivial | Add `data-sv="${i.full_period_imp??''}"` to the Impact `<td>`. Do the same for Exposure (`fp()` uses `+` prefix for positive, which breaks `Number()` for positives) and Std Dev (to be safe). |
| **B55** | `classifyAttrib(name)` is a fragile heuristic — classifies as "country" if `length<25 && !'&' && !',' && startsWith upper-lower`. False positives: any industry name matching that pattern (e.g., "Banks", "Software") gets misclassified. False negatives: multi-word countries with `&` (none in practice, but e.g., "Bosnia & Herzegovina" would misclassify). | Medium | Non-trivial (needs authoritative per-row type field) | Ask FactSet to supply a type/row-classification field in the 18 Style Snapshot section. Until then, add a KNOWN_COUNTRIES set alongside KNOWN_CURRENCIES to tighten the heuristic. |
| **B56** | No `plotly_click` drill on `facWaterfallDiv` or `attribChartDiv` — bars look clickable (hover pops, pointer cursor), but clicking does nothing. UX trap. cardFacButt has this (L2386). | Medium | Trivial | Add `.on('plotly_click',...)` after each `Plotly.newPlot` — 3 lines each. For waterfall → `oDrF(y)`; for cardAttrib bar → `oDrAttrib(y)`. |
| **B57** | No `isFinite(f.imp)` guard before waterfall mapping — if any `f.imp === NaN/Infinity`, `Math.max(...)` returns `NaN`, breaking the axis range silently. | Low | Trivial | Change filter from `f=>f.imp!=null` to `f=>isFinite(f.imp)`. 1 char change plus import. |
| **B58** | Hardcoded hex `#10b981`/`#ef4444` × 3 sites across the cardAttrib/waterfall story (L1363, L2054, L2126 rgba variants). Should consume `THEME().pos`/`.neg`. Also weekly-bars drill uses `rgba(16,185,129,0.6)` / `rgba(239,68,68,0.6)` — no alpha-token system. | Medium | Trivial per site | Bulk replace with `THEME().pos`/`.neg`; for the 0.6 alpha variant, either add a `T.posAlpha` helper or post-process with `rgba` composition. Same fix queued on cardMCR/cardTreemap/cardScatter — land together. |
| **B59** | Waterfall inline height formula uncapped — `Math.max(160, facs.length*32)+20`. 40 factors = 1300px. 60 factors = 1940px. Dwarfs neighboring cards on the Exposures tab. | Low | Trivial | `Math.min(900, Math.max(160, facs.length*32)+20)` + add `overflow-y:auto` on the div. |
| **B60** | Two near-identical horizontal-bar charts in Exposures tab (waterfall @ row 3 and cardAttrib's bar @ row 12) answer different questions (factors vs countries/industries/currencies) but look visually interchangeable. Scroll-past risk. | Low | Non-trivial (layout / labeling) | Either: (a) co-locate them in a grid, (b) add a subtitle to each chart explicitly distinguishing the universes, or (c) promote the waterfall into a full card with title/subtitle/tooltip parallel to cardAttrib. |
| **B61** | cardAttrib card-title has no `oncontextmenu="showNotePopup(event,'cardAttrib');return false"`. User cannot attach notes to this tile. | Low | Trivial | 1-line add to L1308 card-title div. |
| **B62** | Row `oDrAttrib(name)` — name escaping uses `.replace(/'/g,"\\'")` only. Does not guard backslashes or double-quotes. Not an exploit (data source is trusted FactSet) but fragile. | Very low | Trivial | Switch to `data-name="${encodeURIComponent(i.name)}"` on the `<tr>` and read in handler. |
| **B63** | No `data-col` on thead/tbody → column-picker retrofit blocked (same as cardRegions/cardGroups). | Low | Trivial | Add `data-col="name"|"exp"|"dev"|"imp"` to both `<th>` and each `<td>`. |
| **B64** | Subtitle mentions "Click row for time series" — good — but the bar chart below the table is NOT mentioned as clickable (because it isn't). If B56 is applied, the subtitle should update to "Click any row or bar for detail". | Very low | Trivial (follow-on to B56) | — |
| **B65** | Hardcoded `top 20` (L2027) and `top 10` (L2049) — no user control, no "showing N of M" banner. If a strategy has 80 currencies + countries + industries combined, user sees only 20 without any way to expand. | Low | Non-trivial | Add a "Show all" toggle that lifts the 20 cap; consider paginated if >100. |
| **B66** | Keyboard accessibility — rows have `onclick` but no `tabindex`, `role`, or `onkeydown`. Keyboard users can't drill. | Medium | Trivial | Global CSS+JS: `.clickable[onclick]` gets `tabindex="0" role="button"` on render and a keydown handler that triggers Enter/Space → click. Mirrors cardFRB-audit fix queue. |
| **B67** | Weekly-bars chart in `oDrAttrib` drill has no `plotly_click` — can't zoom into a specific week. Lower priority since rangeslider already exists on the line above. | Very low | Trivial | — |

---

## 8. Verification Checklist

- [x] **Data accuracy — parser path:** `_extract_snapshot` → `snap_attrib[name]` → `exp/dev/full_period_imp`. `_build_factor_list` → `s.factors[].imp`. Both traced to CSV column names (SNAP_EXP / SNAP_DEV / SNAP_IMP / SNAP_CIMP).
- [x] **No dependency on blank `SNAP_RET`:** Verified — cardAttrib & waterfall render `f.imp` / `i.full_period_imp` only, never `.ret`.
- [x] **Empty state (table):** guard present ✅.
- [ ] **Empty state (waterfall):** silent return leaves stale render ❌ B53.
- [ ] **isFinite guard on `f.imp`:** absent ❌ B57.
- [ ] **Header-click sort on Impact col:** BROKEN (no `data-sv`) ❌ B54.
- [x] **Dropdown-sort:** working for all three modes.
- [x] **Filter:** 4-way category select ✅.
- [ ] **Column picker:** blocked (no `data-col`) ❌ B63.
- [x] **Export CSV:** `#tbl-attrib` ✅.
- [ ] **Export PNG:** correctly absent ✅ (per policy).
- [x] **Row click → drill:** `oDrAttrib` opens metricModal ✅.
- [ ] **Bar click → drill (cardAttrib):** missing ❌ B56.
- [ ] **Bar click → drill (waterfall):** missing ❌ B56.
- [ ] **Keyboard row activation:** missing ❌ B66.
- [x] **Responsive:** Plotly responsive true; grids reflow ✅.
- [x] **Theme-aware axes:** ✅.
- [ ] **Theme-aware bar colors:** ❌ 3 hardcoded-hex sites B58.
- [x] **Escape-close on drill:** metricModal in ALL_MODALS ✅.
- [x] **No console errors:** path clean (no obvious throw).
- [ ] **Week-selector aware:** ❌ both read latest B52.
- [ ] **Note-popup right-click:** ❌ B61 (cardAttrib) + B50 (waterfall has no id at all).
- [ ] **Waterfall height cap:** missing — up to 1940px uncapped B59.
- [ ] **Data-sv on numeric cells:** ❌ B54.
- [ ] **Data-col on cells:** ❌ B63.
- [x] **Signed formatter (`fp`) used consistently:** ✅.
- [x] **Period annotation (waterfall):** ✅ pulls from `s.current_date` with fallback.
- [ ] **Running-sum cross-check in drill:** hidden behind legendonly — no surfaced warning if mismatch.
- [x] **No duplicate names crash:** unique-key by construction ✅.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| `cardFacButt` (Factors tab, L1156) | Sibling viz reading `s.factors`. Has `plotly_click → oDrF` wiring (L2386) — the model for waterfall B56 fix. |
| `cardFacDetail` (Factors tab, L1775+) | Gold-standard factor table. Has `data-sv`, `data-col`, CSV, sort, row-drill. Source of truth for cardAttrib's missing primitives. |
| `cardFRB` (Exposures row 8) | Fellow factor tile. Audited 2026-04-21. Shares hardcoded-palette anti-pattern. |
| `oDrF(name, range)` | Factor drill — what the waterfall's bar click should reach. |
| `oDrFRisk(name, range)` (L3431) | Alternate factor drill used from Risk tab. |
| `oDrAttrib(name)` (L2067) | cardAttrib table row drill. Shows cumulative impact line + weekly bars + cross-check overlay. |
| `rFac` (L1775) | Companion factor renderer (cardFacDetail body). Shows `f.ret` → DOES depend on blank SNAP_RET. Out of scope here but flagged for next cardFacDetail audit. |
| Factor Correlation tile (cardCorr L1299) | Neighbor on same tab; uses `hist.fac`. |
| 18 Style Snapshot section (parser L646) | Source of `snap_attrib`. Captures per-period history (`hist[]`) + full-period summary detection logic. |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Audit v1 — three-track audit. Key findings: (1) no number depends on blank SNAP_RET ✅, (2) waterfall card has no id (blocks notes), (3) Impact-column sort broken (no data-sv), (4) both Plotly bar charts lack click-drill, (5) 3× hardcoded pos/neg hex sites, (6) waterfall height uncapped, (7) neither view respects `_selectedWeek`. Trivial fix queue 10, non-trivial 5, cross-tile 2. B50–B67 numbering range. | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — `SNAP_IMP` / `SNAP_CIMP` / `full_period_imp` semantics authority; needs to confirm whether the "summary row detection" logic in parser L682–L701 is robust across all strategies
- rr-data-validator — §1.5 row-level numeric verification pending JSON spot-check; compare client-side "Running Sum" against FactSet cumulative for max-delta statistic
- rr-design-lead — §6 palette consolidation (three hardcoded-hex sites across cardAttrib + waterfall + weekly drill) and waterfall-height cap decision

---

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | 🟢 GREEN | Both render paths + drill located; waterfall card lacks id |
| **1. Data Source** | 🟢 GREEN | Parser clean; no dependency on blank SNAP_RET; empty-state on table; full_period_imp composite documented |
| **2. Columns / Encoding** | 🟡 YELLOW | Missing primitives (data-sv, data-col); Impact sort broken; two near-identical bar charts |
| **3. Visualization** | 🟡 YELLOW | Correct chart choices; theme-aware axes; but hardcoded hex × 3 sites; waterfall silent-return on empty |
| **4. Functionality** | 🟡 YELLOW | Filter + sort-dropdown + row-drill + CSV all work; bar-click drill missing on both charts; no keyboard access |
| **5. Drill (oDrAttrib)** | 🟢 GREEN + 🟡 YELLOW | Modal structurally sound + thoughtful cross-check overlay; theme drift on weekly bars |
| **6. Design** | 🟡 YELLOW | Good density/emphasis/subtitle; hardcoded hex; uncapped waterfall height; missing note-popup wiring |
| **7. Open Items** | — | 18 findings B50–B67 (10 trivial, 5 non-trivial, 3 backlog/PM) |

### Overall severity

**🟡 YELLOW** — data integrity is clean (the tile does NOT surface the blank Compounded Factor Return column, which was the specific concern in the ask), but a material pile of primitives (data-sv, data-col, plotly_click parity, theme tokens, empty-state on waterfall, card id on waterfall) is missing. Nothing is broken for the PM-user's daily read; everything is the polish/consistency gap that every other tile in this batch shared.

### Fix queue

**Trivial (agent can apply, ≤5 lines each):**
1. Add `id="cardAttribWaterfall"` to the orphan waterfall card L1182 (B50)
2. Add `data-sv` to Exposure / Std Dev / Impact `<td>`s in `rAttribTable` (B54)
3. Add `data-col` to `<th>` + `<td>` for future column-picker (B63)
4. Replace hardcoded `#10b981`/`#ef4444` at L1363, L2054 with `THEME().pos`/`.neg` (B58 — core sites)
5. Replace silent `return` in `rFacWaterfall` L1352 with empty-state `<p>` written to div (B53)
6. Change waterfall filter to `f=>isFinite(f.imp)` (B57)
7. Wire `plotly_click → oDrF(point.y)` on `facWaterfallDiv`; wire `plotly_click → oDrAttrib(point.y)` on `attribChartDiv` (B56)
8. Cap waterfall height: `Math.min(900, Math.max(160, N*32)+20)` + `overflow-y:auto` on the div (B59)
9. Add `oncontextmenu="showNotePopup(event,'cardAttrib');return false"` to cardAttrib card-title (B61); once B50 lands, add the same wiring to the waterfall card-title (requires first giving the waterfall card an actual title element — currently L1183 `<div class="card-title">Factor Attribution — Return Impact</div>` has no tip/oncontextmenu)
10. Update subtitle after B56: "Click any row or bar for time series" (B64)

**Non-trivial (PM / design / cross-tile):**
- Week-selector awareness (B52) — blocked on per-week `snap_attrib` / `factors` plumbing; BACKLOG with B6/B12
- `classifyAttrib` heuristic (B55) — ideally FactSet supplies a type field; interim fix = KNOWN_COUNTRIES set
- `full_period_imp` semantics (B51) — FactSet clarification + tooltip
- Two-bar-charts distinguishability (B60) — layout / labeling call
- Top-20 / Top-10 caps (B65) — expose "Show all" toggle
- `.clickable` global keyboard handler (B66) — needs global CSS+JS pattern, affects every tile with row-drill
- 0.6-alpha pos/neg helper on weekly-bars drill (B58 completion) — needs a new theme primitive or `rgba()` composer

**Cleanup (low priority, logged):**
- Escape name properly in `oDrAttrib('${i.name.replace(...)}')` — backslash + doublequote not handled (B62)
- `oDrAttrib` drill bars not clickable per-week (B67) — rangeslider covers most use cases

### Single most important finding

**The tile passes the ask's specific data-integrity concern** — neither cardAttrib nor the waterfall displays any number that depends on FactSet's blank `SNAP_RET` ("Compounded Factor Return") column. `f.ret` flows through parser to `s.factors[].ret` and surfaces on cardFacDetail L1780 + Risk tab L3074, but those are out of scope. **The cardAttrib table uses `i.full_period_imp` (from `SNAP_IMP` / `SNAP_CIMP`). The waterfall uses `f.imp` (from `SNAP_IMP`).** Both are populated in every strategy sampled.

The **material finding** is structural not numeric: **the waterfall lives in a card with no id, no tooltip, no note-popup wiring, and is not visually linked to cardAttrib 9 rows below** — yet they are semantically siblings (two "factor attribution — impact" views of related data). B50 + B60 should be treated together: give the waterfall a proper card identity and co-locate it (or at minimum visually distinguish it) from the cardAttrib bar chart.
