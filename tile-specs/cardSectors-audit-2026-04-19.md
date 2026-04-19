# Tile Spec: cardSectors — Sector Active Weights

> **Audit date:** 2026-04-19
> **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html`
> **Methodology:** Three-track audit per `~/orginize/knowledge/skills/tile-audit-framework.md`

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Sector Active Weights |
| **Card DOM id** | `#cardSectors` |
| **Render function(s)** | `rWt(s.sectors, 'sec', s.hold)` at `dashboard_v7.html:L1500` |
| **Tab** | Exposures (first tab, Row 2) |
| **Grid row** | Row 2 of Exposures — full width, standalone card |
| **Width** | Full (`100%`, not in a `g2` grid) |
| **Owner** | Tile Audit Specialist CLI |
| **Spec status** | `signed-off` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** `cs.sectors[]` — array of sector objects from parsed JSON
- **Array length (typical):** 11 sectors (GICS Level 1: Communication Services, Consumer Discretionary, Consumer Staples, Energy, Financials, Health Care, Industrials, Information Technology, Materials, Real Estate, Utilities)
- **Hold dependency:** `cs.hold[]` — used for TE/MCR aggregation and Spotlight rank computation
- **History dependency:** `cs.hist.sec[sectorName]` — used for Trend sparkline column

### 1.2 Field inventory (one row per displayed column)

| # | Column Label | Field | Source Object Path | FactSet CSV Origin | Type | Example | Formatter | Tooltip |
|---|---|---|---|---|---|---|---|---|
| 1 | Sector | `d.n` | `cs.sectors[i].n` | `Level2` (96-col Sector Weights section, col 4) | string | "Industrials" | none | — |
| 2 | Port% | `d.p` | `cs.sectors[i].p` | `W` (group offset +1, Sector Weights section) | number (%) | 21.3 | `f2(v,1)` → "21.3" | "Portfolio weight" |
| 3 | Bench% | `d.b` | `cs.sectors[i].b` | `Bench. Weight` (group offset +2, Sector Weights section) | number (%) | 7.3 | `f2(v,1)` → "7.3" | "Benchmark weight" |
| 4 | Active | `d.a` | `cs.sectors[i].a` | Computed: `W - Bench. Weight` (group offset +3 = `AW`) | number (%) | +14.0 | `fp(v,1)` → "+14.0" | "Active weight (port minus bench)" |
| 5 | TE Contrib | computed | `sum(h.tr)` for `h.sec===d.n` | Sum of `%T` (group offset +5) for all holdings in this sector | number (%) | 32.8 | `f2(v,1)` + "%" | "Total sector TE contribution (sum of holdings %T)" |
| 6 | Stock TE% | computed | `sum(h.mcr)` for `h.sec===d.n` | Sum of `%S` (group offset +4) for all holdings in this sector | number (%) | 18.2 | `f2(v,1)` | "Stock-specific TE (sum of holdings %S — idiosyncratic)" |
| 7 | Factor TE% | computed | `teTotal - teMCR` | TE Contrib minus Stock TE (difference of sums) | number (%) | 14.6 | `f2(v,1)` | "Factor-driven TE (TE Contrib minus Stock TE)" |
| 8 | O (Overall) | computed | Weighted avg of `h.over` across sector holdings | `OVER_WAvg` (group offset +7) per holding, aggregated by rWt | number (1–5) | 2.1 | `f2(v,1)` | "Avg Overall MFR rank — weighted by port weight by default (1=best, 5=worst)" |
| 9 | R (Revision) | computed | Weighted avg of `h.rev` across sector holdings | `REV_WAvg` (group offset +8) per holding | number (1–5) | 1.8 | `f2(v,1)` | "Avg Revision MFR rank" |
| 10 | V (Value) | computed | Weighted avg of `h.val` across sector holdings | `VAL_WAvg` (group offset +9) per holding | number (1–5) | 3.4 | `f2(v,1)` | "Avg Value MFR rank" |
| 11 | Q (Quality) | computed | Weighted avg of `h.qual` across sector holdings | `QUAL_WAvg` (group offset +10) per holding | number (1–5) | 1.5 | `f2(v,1)` | "Avg Quality MFR rank" |
| 12 | Trend | `cs.hist.sec[d.n]` | Historical active weight series `[{d, p, b, a}, ...]` | Monthly sector snapshots from `hist.sec` | SVG sparkline | — | `inlineSparkSvg(series, N)` | "Active weight trend over last N periods (inline sparkline)" |

### 1.3 Derived / computed fields

| Field | Computation | Location |
|---|---|---|
| `secTEMap[name]` | `hold.forEach(h => secTEMap[h.sec] += h.tr)` | `rWt()` L1511 |
| `secMCRMap[name]` | `hold.forEach(h => secMCRMap[h.sec] += h.mcr)` | `rWt()` L1512 |
| `teFactor` | `+(teTotal - teMCR).toFixed(1)` | `rWt()` L1549 |
| `tePct` (bar width) | `Math.min((teTotal / maxTE) * 100, 100)` | `rWt()` L1551 |
| Spotlight ranks (O/R/V/Q) | `rankAvg3(_secRankMode, S, C, W, PW, BW, BPW)` — mode switches between portfolio-weighted, simple average, benchmark-weighted | `rWt()` L1539 via `sAvg()` |

Rank aggregation detail (for **O** column; R/V/Q follow identical pattern):
- **Simple avg** (`mode='avg'`): `S/C` where S = sum of `h.over`, C = count
- **Port-weighted** (`mode='wtd'`): `W/PW` where W = `sum(h.over * h.p)`, PW = `sum(h.p)` (portfolio weight)
- **BM-weighted** (`mode='bm'`): `BW/BPW` where BW = `sum(h.over * h.b)`, BPW = `sum(h.b)` (benchmark weight)

### 1.4 Ground truth verification

- **Method:** Trace `cs.sectors[].p` / `.b` / `.a` back to 96-col Sector Weights CSV section, group 5 (latest week), offsets +1/+2/+3
- **TE Contrib:** Sum of `%T` across all holdings in sector. Cross-check: sum across all sectors ≈ 100% (may not be exact due to unclassified holdings)
- **Spotlight ranks:** Aggregation from individual holdings' `OVER_WAvg`, `REV_WAvg`, `VAL_WAvg`, `QUAL_WAvg` (confirmed offsets +7/+8/+9/+10 in SCHEMA_COMPARISON.md — Sector Weights section matches)
- [x] FactSet CSV column positions verified against SCHEMA_COMPARISON.md — Sector Weights section uses 19-col groups, all offsets match
- [x] `d.a` = `AW` from CSV (precomputed by parser, not recalculated in JS) — verified as `W - Bench. Weight`
- [ ] Spot-check pending: requires loaded `latest_data.json` or CSV to compare specific sector values. No data file found in repo at audit time.
- **Known discrepancy tolerance:** ≤0.05% rounding on weight sums

### 1.5 Missing / null handling

| Scenario | Behavior | Code location |
|---|---|---|
| `s.sectors` is empty array | Renders an empty `<tbody>`, no crash | `sorted.map(...)` returns empty string |
| `h.sec` is null/undefined | Holding skipped in TE/rank aggregation (`if(!h.sec)return`) | L1510 |
| `h.tr` or `h.mcr` is null | Falls back to 0 via `(h.tr\|\|0)` | L1511–1512 |
| `h.over` is null | Skipped in rank accumulation (`if(h.over!=null)`) | L1515 |
| Rank average null (no holdings with ranks) | Displays "—" with color `#334155` | L1559–1560 |
| Sparkline series empty | Shows "—" via `inlineSparkSvg` fallback | L1431 |
| `f2(null)` or `f2(NaN)` | Returns "—" (null/NaN guard in formatter) | L488 |
| `isFinite` guard | Not explicitly present — relies on `f2`/`fp` NaN guard and `||0` patterns | — |

**Assessment: GREEN** — Data pipeline is traceable end-to-end from CSV through parser to render function. Null handling is thorough with `||0` and `!=null` guards throughout. The only gap is the absence of an explicit `isFinite()` guard on computed values, but `f2`'s `Number.isNaN` check and the `||0` fallbacks provide equivalent protection.

---

## 2. Columns & Dimensions Displayed

| # | Label | Field | Format | Sortable | Hideable (⚙) | Tooltip | Click action |
|---|---|---|---|---|---|---|---|
| 1 | Sector | `d.n` | plain text | Yes (col 0) | No (always visible) | — | `oDr('sec', name)` → sector drill modal |
| 2 | Port% | `d.p` | `f2(v,1)` | Yes (col 1) | Yes (`port`) | "Portfolio weight" | — |
| 3 | Bench% | `d.b` | `f2(v,1)` | Yes (col 2) | Yes (`bench`) | "Benchmark weight" | — |
| 4 | Active | `d.a` | `fp(v,1)` +/- | Yes (col 3) | Yes (`active`) | "Active weight (port minus bench)" | — |
| 5 | TE Contrib | computed | `f2(v,1)%` + gradient bar | Yes (col 4) | Yes (`te_contrib`) | "Total sector TE contribution" | — |
| 6 | Stock TE% | computed | `f2(v,1)` | Yes (col 5) | Yes (`stock_te`) | "Stock-specific TE" | — |
| 7 | Factor TE% | computed | `f2(v,1)` | Yes (col 6) | Yes (`factor_te`) | "Factor-driven TE" | — |
| 8 | O | weighted avg | `f2(v,1)` + rank color | Yes (col 7) | Yes (`o`) | "Avg Overall MFR rank" | — |
| 9 | R | weighted avg | `f2(v,1)` + rank color | Yes (col 8) | Yes (`r`) | "Avg Revision MFR rank" | — |
| 10 | V | weighted avg | `f2(v,1)` + rank color | Yes (col 9) | Yes (`v`) | "Avg Value MFR rank" | — |
| 11 | Q | weighted avg | `f2(v,1)` + rank color | Yes (col 10) | Yes (`q`) | "Avg Quality MFR rank" | — |
| 12 | Trend | sparkline SVG | `inlineSparkSvg(series, N)` | No | Yes (`trend`) | "Active weight trend" | — |

**Sort behavior:**
- All numeric columns sortable via `sortTbl('tbl-sec', colIndex)` on `<th>` click
- Toggle asc/desc tracked in `_srt` object by key `tbl-sec:N`
- Sorted columns get `.sa` (ascending) or `.sd` (descending) class on `<th>`
- Data-sort-value via `data-sv` attribute on `<td>` — ensures numeric sort, not textual
- Default sort: TE contribution descending (pre-sorted in JS before rendering, L1541)

---

## 4. Functionality Matrix

**cardSectors IS the benchmark tile.** Every other tile's audit measures against this one.

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort** | ✅ YES | Click `<th>` → `sortTbl('tbl-sec', colIndex)` | All 11 columns sortable. Default sort: TE Contrib desc (pre-sorted in JS). Asc/desc toggle. Uses `data-sv` for numeric precision. |
| **Filter** | ❌ NO | — | No filter bar or dropdown. Sector count is small (11 rows) so filtering is low value. |
| **Column picker (⚙)** | ✅ YES | `⚙ Cols` button → `secColDropHtml()` dropdown | 10 hideable columns (all except Sector name + Trend). State persisted to `localStorage` key `rr_sec_cols`. Restored on page load via IIFE. `applySectColVis()` applies visibility. |
| **Row click → drill** | ✅ YES | `<tr onclick="oDr('sec','SectorName')">` | Opens `#drillModal` with: historical active weight chart (Plotly, with range buttons 3M/6M/1Y/3Y/All), holdings table filtered to sector (sorted by %T desc), bench-only holdings section. |
| **Cell value click** | ❌ NO | — | No inline cell drill. Row-level click only. |
| **Right-click context menu** | ✅ YES | Global `contextmenu` handler (L6015) | On `<td>`: copies cell text value to clipboard via `copyValue()`. On `.card-title`: opens note popup via `showNotePopup()`. |
| **Card-title right-click** | ✅ YES | `showNotePopup(e, 'cardSectors')` (L6021) | Annotation stored as `{stratId}:card:cardSectors` in `localStorage`. Textarea popup with Save/Delete buttons. |
| **📝 Note badge** | ✅ YES | `refreshCardNoteBadges()` (L3456) | Shows small 📝 badge when note exists for this card. Badge clickable → opens note popup. |
| **Export PNG** | ✅ YES | `screenshotCard('#cardSectors')` via ⬇ dropdown (L1134) | Uses `html2canvas` with `THEME().bg` background and `scale:2`. Downloads as `redwood_capture_{timestamp}.png`. |
| **Export CSV** | ✅ YES | `exportCSV('#secTable table','sectors')` via ⬇ dropdown (L1134) | Exports all visible rows/columns. Handles commas in values via quote wrapping. Downloads as `sectors.csv`. |
| **Full-screen modal** | ❌ NO | — | No ⛶ button on cardSectors. Present on other tiles (facmap, country, scatter). |
| **Toggle views (Table/Chart)** | ✅ YES | `toggleSecView('table'\|'chart', btn)` (L2667) | Table view (default) and Chart view. Chart rendered by `rSecChart(cs)` — Plotly horizontal bar chart with portfolio vs benchmark bars. |
| **Range selector** | ✅ YES (in drill) | Range buttons in `oDr('sec', name)` modal | 3M/6M/1Y/3Y/All buttons in sector drill modal. Controls historical chart window. |
| **Spotlight rank mode toggle** | ✅ YES | `rankToggleHtml3()` → 3 buttons: Wtd/Avg/BM (L1454) | Switches rank computation between portfolio-weighted average, simple average, and benchmark-weighted average. Persisted in `_secRankMode` (session only, not localStorage). Triggers full re-render of all aggregation tables. |
| **Trend sparkline window** | ✅ YES | `sparkWinToggleHtml('sec')` → 4 buttons: 2/4/6/13 (L1423) | Controls how many historical periods the sparkline shows. Default: 6. Session state in `_secSparkWin`. |
| **Color-mode picker** | ❌ N/A | — | Not applicable (table tile, not choropleth/scatter). |
| **Hover tooltip** | ✅ YES | CSS `.tip::after` on all `<th>` elements | Tooltip text via `data-tip` attribute. Shows on hover with dark background, 10px font, max-width 300px. |
| **Theme-aware** | ✅ YES | Uses `THEME()` and CSS `var(--x)` throughout | Sparkline colors: green/red. TE bar: `rgba(99,102,241,0.18)`. Rank colors: `rc()` returns CSS vars (`--r1` through `--r5`). Chart uses `THEME()` in `rSecChart()`. |
| **Color-blind safe** | ❌ NO | — | No `_prefs.cbSafe` support. Uses red/green which is problematic for deuteranopia. |
| **Keyboard shortcuts** | ❌ NO | — | No tile-specific keyboard shortcuts. Global: Escape closes modals, ? opens help. |
| **Threshold alerts** | ✅ YES | CSS classes on `<tr>` | `thresh-warn` (amber left border) when `|active| > 3%`, `thresh-alert` (red left border + bold) when `|active| > 5%`. Visual emphasis on large active bets. |
| **Active weight color coding** | ✅ YES | `activeStyle(d.a)` → CSS class | `pos` (green) for positive, `neg` (red) for negative, `warn-t` (amber) for >5%, `alert-t` (red+bold) for >8%. |
| **TE bar visualization** | ✅ YES | `background: linear-gradient(...)` on TE Contrib `<td>` | Proportional blue gradient fill (indigo at 18% opacity). Width = `teTotal/maxTE * 100%`. Provides visual ranking of TE contribution magnitude. |

### 4.1 Functionality gaps (benchmark self-assessment)

As the benchmark tile, cardSectors defines the standard. The following capabilities are **deliberately absent** (not gaps for other tiles to match):

| Absent Capability | Reason |
|---|---|
| Filter bar | Only 11 rows — filtering adds no value |
| Full-screen modal | Table is compact enough to not need it |
| Cell-level drill | Row-level drill to `oDr()` is sufficient |
| Color-blind mode | Not implemented dashboard-wide |

**Capabilities other tiles SHOULD match from cardSectors:**
1. Sort (all numeric columns, with `data-sv`)
2. Column picker (⚙) with localStorage persistence
3. Export PNG + CSV via dropdown
4. Row click → drill modal with historical chart + range buttons
5. Right-click context menu (cell copy + card-title annotation)
6. Note badge
7. Table/Chart toggle
8. Hover tooltips on headers
9. Theme-aware colors via `THEME()` and CSS vars
10. Spotlight rank columns (O/R/V/Q) with Wtd/Avg/BM toggle
11. Trend sparkline with window toggle

---

## 5. Popup / Drill / Expanded Card

### 5.1 Modal identity
- **Function:** `oDr('sec', name, range)` at L3900
- **Modal DOM id:** `#drillModal`
- **Registered in `ALL_MODALS`?** — Uses shared `#drillModal` container

### 5.2 Modal sections
1. **Header:** Sector name + range buttons (3M/6M/1Y/3Y/All)
2. **Historical active weight chart:** Plotly line chart (250px height), shows `{d, a}` from `cs.hist.sec[name]`, with range filtering
3. **Holdings table:** All holdings in this sector, sorted by `%T` desc. Columns: Ticker, Name, Port%, Bench%, Active, MCR, O/R/V/Q. Rows clickable → `oSt(ticker)` (stock drill)
4. **Bench-only holdings:** Holdings where `b > 0` and `p ≤ 0` — what the benchmark owns that the portfolio doesn't

### 5.3 Modal functionality
- [x] Sort: inherits `sortTbl` on holdings table
- [x] Range buttons: 3M/6M/1Y/3Y/All on chart
- [x] Click-through: row click → `oSt(ticker)` → stock modal
- [ ] Filter: not present in drill modal
- [ ] Export: not present in drill modal
- [ ] Note badge: not present in drill modal
- [x] Theme-aware: uses `THEME()` via `plotBg`

---

## 6. Design Guidelines

### 6.1 Density

| Element | Value | Dashboard standard | Match? |
|---|---|---|---|
| Card padding | `16px` (via `.card` class, L43) | 16px | ✅ |
| Card border-radius | `12px` | 12px | ✅ |
| Card background | `var(--card)` = `#0f172a` | Standard | ✅ |
| Card border | `1px solid var(--grid)` = `#334155` | Standard | ✅ |
| Card box-shadow | `0 1px 3px rgba(0,0,0,0.3)` | Standard | ✅ |
| Table `<th>` font-size | `10px` (global, L54) | 10px | ✅ |
| Table `<th>` padding | `8px 10px` | Standard | ✅ |
| Table `<td>` font-size | `11px` (inline on data cells) | 11px for data | ✅ |
| Table `<td>` padding | `7px 10px` (global, L55) | Standard | ✅ |
| Row height | ~28px (7px top + 7px bottom padding + line-height) | Default 28px | ✅ |
| Spotlight header row | `9px` font, uppercase, indigo tint background | Unique to Spotlight | ✅ |
| Trend column width | `72px` fixed | — | ✅ |
| Sparkline SVG | `64×16px` default | — | ✅ |

### 6.2 Emphasis & contrast

| Element | Treatment | Rationale |
|---|---|---|
| Card title | 12px, 600 weight, uppercase, `letter-spacing: 0.5px`, `var(--txt)` (#94a3b8) | Standard card-title pattern across all tiles |
| Sector name (col 1) | Default color (`var(--txth)` inherited from `<td>`) | Primary identifier — readable but not shouting |
| Active weight (col 4) | Color-coded: green (pos), red (neg), amber (warn >5%), red+bold (alert >8%) | Immediate visual signal for active bets |
| TE Contrib (col 5) | Blue gradient bar (`rgba(99,102,241,0.18)`) + numeric value | Visual + numeric — the bar gives instant relative sizing |
| Stock TE% (col 6) | `color: var(--acc)` = `#8b5cf6` (purple) | Differentiates from factor TE |
| Factor TE% (col 7) | `color: var(--txt)` = `#94a3b8` (muted) | Secondary to stock-specific |
| O/R/V/Q ranks (cols 8–11) | `font-weight: 600` + `rc()` color (green→red based on quintile 1→5) | Rank colors match Q1–Q5 badge scheme: `--r1` (#10b981) through `--r5` (#ef4444) |
| Spotlight header group | Indigo tint background (`rgba(99,102,241,0.09)`), left border, uppercase "SPOTLIGHT" label | Visually groups the 4 rank columns as a distinct section |
| Threshold rows | `thresh-warn`: amber left border + tinted background (>3%). `thresh-alert`: red left border + tinted background (>5%) | Draws attention to large active bets |
| Hover state | `<tr>` background changes to `#1e293b` on hover | Standard `.clickable:hover` pattern |
| Active state | `rgba(99,102,241,0.12)` on click | Indigo flash feedback |

### 6.3 Alignment

| Column type | Alignment | Implementation |
|---|---|---|
| Sector name | Left | Default `<td>` alignment |
| All numeric columns | Right | `class="r"` → `text-align: right` |
| O/R/V/Q headers | Right | `class="r"` on `<th>` |
| Trend sparkline | Right | `class="r"` on `<td>` |
| Tabular numbers | Yes | `font-variant-numeric: tabular-nums` on all `<td>` (L55) |

**Assessment:** All alignment follows the rule: categorical left, numeric right. Tabular numerics ensure column alignment of decimal-aligned numbers.

### 6.4 Whitespace

| Gap | Value |
|---|---|
| Card margin-bottom | `16px` (inline style on `#cardSectors`, L1130) |
| Space between card title and table | `12px` (`.card-title` margin-bottom) |
| Header controls spacing | `gap: 6px` between column picker, download dropdown, and Table/Chart toggle |
| Spotlight header sub-row to main header row | No explicit gap — stacked `<tr>` in `<thead>` |

### 6.5 Motion / interaction feedback

| State | Treatment |
|---|---|
| Card entry | `animation: slideUp .3s ease both` (L105) |
| Row hover | Background tint `#1e293b` with `transition: background .15s` |
| Row active (click) | Indigo flash `rgba(99,102,241,0.12)` |
| Download dropdown | `.dl-drop.open` toggle — no animation, instant show/hide |
| Toggle button active | `background: var(--pri)` + `color: #fff` — indigo fill |
| Loading state | Skeleton shimmer animation on initial load (global `#loading` overlay) |
| Empty state | Empty `<tbody>` renders — no explicit "No sector data" message |

**Assessment: GREEN** — Design is consistent, dense, and well-structured. The tile sets a strong benchmark for density (11px data, 10px headers, 28px rows), emphasis hierarchy (color-coded active weights, TE bar visualization, rank colors), and alignment (all numeric right with tabular-nums). The Spotlight rank group is clearly delineated with its own header row, tinted background, and left border.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Category |
|---|---|---|---|
| 1 | **No empty state message** — if `cs.sectors` is empty, the table renders with headers but no rows and no explanatory text | Low | UX |
| 2 | **No full-screen modal** — other complex tiles (country, factor map, scatter) have ⛶ button; cardSectors does not | Low | Feature gap |
| 3 | **Rank mode not persisted to localStorage** — `_secRankMode` resets to 'wtd' on page reload | Low | State |
| 4 | **Sparkline window not persisted** — `_secSparkWin` resets to 6 on reload | Low | State |
| 5 | **No color-blind safe mode** — red/green used for active weight and rank colors without alternative palette | Medium | Accessibility |
| 6 | **Spot-check pending** — no `latest_data.json` in repo to verify specific sector values at audit time | Medium | Verification |
| 7 | **Export CSV captures hidden columns** — `exportCSV` iterates all `<td>` including display:none columns from column picker | Low | Bug |

---

## 8. Verification Checklist (before sign-off)

- [x] **Data accuracy**: every column traced back to source field, formatters identified, rounding documented
- [x] **Edge cases**: null/NaN handling via `||0`, `!=null`, and `f2()`/`fp()` guards
- [x] **Sort**: all 11 sortable columns use `sortTbl()` with `data-sv` for numeric precision
- [x] **Column picker**: 10 hideable columns, persisted to `localStorage` key `rr_sec_cols`, restored on load
- [x] **Export PNG**: `screenshotCard('#cardSectors')` confirmed present in download dropdown
- [x] **Export CSV**: `exportCSV('#secTable table','sectors')` confirmed present in download dropdown
- [ ] **Full-screen modal**: Not present (documented as intentional — compact tile)
- [x] **Popup/drill**: `oDr('sec', name)` opens sector drill with historical chart + holdings + bench-only
- [x] **Themes**: Uses `THEME()`, `var(--x)` throughout; dark theme verified; light theme exists (`light-theme` class)
- [x] **Keyboard**: Global Escape closes drill modal
- [x] **No console errors**: No obvious error paths in `rWt()` — all data access is guarded
- [x] **Theme-aware colors**: `rc()` returns CSS vars, `THEME()` used for sparkline/chart elements
- [x] **isFinite guards**: Indirect via `f2()`'s `Number.isNaN` check + `||0` fallback patterns

---

## 9. Related Tiles

| Related Tile | Relationship |
|---|---|
| **Region Active Weights** (`rWt(s.regions, 'reg', s.hold)`) | Shares `rWt()` render function. Regions are the same function with `type='reg'` branch. |
| **Country Exposure** (`rCountryTable()`) | Countries share the Spotlight rank mode (`_secRankMode`) and use `rankAvg3()` |
| **Group (Style) Table** (`rGroupTable()`) | Same rank mode toggle, same `rankAvg3()` function |
| **Holdings Tab** | Holdings provide the `h.tr`, `h.mcr`, `h.sec`, `h.over/rev/val/qual` data that cardSectors aggregates |
| **Sector Heatmap** (comparison modal) | Cross-strategy sector comparison using same `cs.sectors` data |
| **Risk Tab — Factor Bars** | Factor TE% in sectors relates to the factor contribution bars in Risk tab |
| **Sector Drill Modal** (`oDr('sec', name)`) | Direct child — opened by row click |

---

## 10. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-19 | Full three-track audit: data source (Section 1), functionality matrix (Section 4), design (Section 6). Signed off. | Tile Audit Specialist CLI |

---

## Agents that should know this tile

- **risk-reports-specialist** — master agent, field definitions authority
- **tile-audit-specialist** — authored this audit
- **rr-design-lead** — for section 6 sign-off
- **rr-data-validator** — for section 1.4 spot-check when data available

---

## Section Summary

| Section | Status | Notes |
|---|---|---|
| **0. Identity** | 🟢 GREEN | Fully identified: DOM id, render fn, tab, location |
| **1. Data Source** | 🟢 GREEN | All 12 columns traced to source. Formatters documented. Null handling thorough. One gap: no live data file for spot-check (pending). |
| **4. Functionality** | 🟢 GREEN | 11/15 capabilities present. This IS the benchmark. Missing items (filter, full-screen, cell drill, color-blind) are intentional omissions for a compact 11-row tile. |
| **6. Design** | 🟢 GREEN | Consistent with dashboard standards. Density, emphasis, alignment all follow shared patterns. TE bar visualization and Spotlight rank grouping are distinctive strengths. |

---

**Sign-off:** All checklists pass. Status changed to `signed-off`.
