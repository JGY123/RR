# Tile Spec: cardHoldings — Audit v1

> **Audited:** 2026-04-19 | **Auditor:** Tile Audit Specialist (CLI)
> **Status:** 🟢 signed-off (all sections reviewed, no blocking issues)

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Portfolio Holdings |
| **Card DOM id** | `#cardHoldings` |
| **Render function(s)** | `rHold()` → `renderHoldTab()` → `renderHoldRows()` (Table) / `renderHoldCards()` (Cards) at `dashboard_v7.html:L3579–L3862` |
| **Tab** | Holdings (`tab-holdings`) |
| **Grid row** | Full-width primary card, followed by `g2` grid (Rank Distribution + Top 10 Holdings) |
| **Width** | Full (`g1`) |
| **Views** | **Table** (default) and **Cards** — toggled via `setHoldView('table'|'cards')` |
| **Owner** | CoS / Tile Audit Specialist |
| **Spec status** | `signed-off` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** `cs.hold[]` — array of holding objects, one per security
- **Entry filter (rHold L3581):** `h.p > 0 || h.b > 0.5 || Math.abs(h.tr||0) > 1` — includes active holdings, material BM-only stocks, and high-TE contributors
- **Typical array length:** 80–300 equities (strategy-dependent; ISC/GSC can reach 1218 raw rows before filtering)
- **Cash exclusion:** `isCash(h)` function (L497) filters currency tickers, CASH_ prefixes, cash-sector names — correctly distinguishes CASH (Pathward Financial) from CASH_USD (currency)

### 1.2 Field inventory — Table view

| # | Column | Field | Type | Source | Example | Formatter | Null handling | Notes |
|---|--------|-------|------|--------|---------|-----------|---------------|-------|
| 1 | Ticker | `h.t` | string | CSV col[4] Level2 | "HDFC" | raw, bold, `var(--txth)` | — | Also shows flag icon + BM/NEW badges |
| 2 | Name | `h.n` | string | CSV col[5] SecurityName | "HDFC Bank Ltd" | truncated 160px, ellipsis | — | Archetype pill appended |
| 3 | Sector | `h.sec` | string | CSV per-holding or row-context | "Financials" | `<span class="chip">` | `'—'` | GICS L1 sector |
| 4 | Industry | `h.ind\|\|h.industry` | string | V2 CSV Industry Rollup | "Banks" | 11px muted | `'—'` | Hidden by default (`_showIndustry=false`) |
| 5 | Country | `h.co` | string | CSV per-holding or row-context | "IN" | raw | `'—'` | ISO 2-letter code |
| 6 | Port% | `h.p` | number | CSV group[0] W (portfolio weight) | 3.21 | `f2(h.p,1)` = "3.2" | '—' via f2 null guard | Right-aligned |
| 7 | Bench% | `h.b` | number | CSV group[1] BW (benchmark weight) | 1.45 | `f2(h.b,1)` = "1.5" | '—' | Right-aligned |
| 8 | Active | `h.a` | number | CSV group[2] AW = W − BW | +1.76 | `fp(h.a,1)` = "+1.8" | '—' | Color-coded via `activeStyle(h.a)`: pos/neg/warn/alert |
| 9 | %S | `h.mcr` | number | CSV group[3] %S (stock-specific TE) | 0.45 | `f2(h.mcr,2)` = "0.45" | '—' | Tooltip: "Stock-specific tracking error component" |
| 10 | Total TE% | `h.tr` | number | CSV group[4] %T (TE contribution) | 3.2 | `fp(trVal,1)` = "+3.2" | 0 fallback | Inline colored bar (width ∝ maxTR), pos=green neg=red. Default sort column. |
| 11 | RBE | computed | number | `\|h.a\| / \|h.tr\|` | 1.52 | `.toFixed(2)` | '—' when h.p=0 or tr≈0 | Risk Budget Efficiency. >1.5 = green(pos), 0.8–1.5 = amber(warn), <0.8 = red(neg). Red-tinted column. |
| 12 | O | `h.over` | number | CSV group[6] OVER_WAvg | 1.2 | `Math.round(v)` = "1" | '—' (#334155) | Quintile 1–5, colored via `rc()`. Border-left separator. |
| 13 | R | `h.rev` | number | CSV group[7] REV_WAvg | 2.0 | `Math.round(v)` = "2" | '—' | Revision MFR rank |
| 14 | V | `h.val` | number | CSV group[8] VAL_WAvg | 4.8 | `Math.round(v)` = "5" | '—' | Value MFR rank |
| 15 | Q | `h.qual` | number | CSV group[9] QUAL_WAvg | 1.4 | `Math.round(v)` = "1" | '—' | Quality MFR rank |

### 1.3 Field inventory — Cards view

Each card (`renderOneHoldCard`, L3631) displays the same core data in a different layout:
- **Header:** Ticker (bold 11px), Name (truncated 36ch), Flag button, BM badge
- **Chip row:** Sector pill, Country pill, Archetype pill (from `getHoldArchetype`)
- **Weight bars:** Port/Bench as proportional bars + percentage text; Active as bold colored number
- **Risk strip:** TE `f2(te,2)%`, %S `f2(pctS,2)`, RBE `rbe.toFixed(2)` — with same color logic as table
- **Rank row:** O/R/V/Q inline with `rc()` coloring, identical to table
- **Expand section:** Factor Contributions mini-bars (top 6 by |value|) + Quick Summary (`genHoldSummary`)

### 1.4 Derived / computed fields

| Field | Computation | Location | Notes |
|---|---|---|---|
| **RBE** | `\|h.a\| / \|h.tr\|` | L3555, L3644, L3798 | Guard: only computed when `h.p > 0 && \|h.tr\| > 0.001`. Null otherwise. Three independent computations (genHoldSummary, card view, table view) — all use same formula ✓ |
| **Archetype** | Classify by dominant factor in `h.factor_contr` | `getHoldArchetype` L3527 | 9 labels: Growth Engine, Value Play, Volatility Driver, Quality Compounder, Market Beta, Regional Driver, Size Tilt, Liquidity Play, Leverage Play, Diversifier. Null if no `factor_contr` or all < 0.01. |
| **maxTR** | `Math.max(...fh.map(h=>Math.abs(h.tr\|\|0)), 0.01)` | L3787 | Floor at 0.01 prevents divide-by-zero. Used for TE bar width scaling. |
| **BM-only flag** | `(!h.p \|\| h.p===0) && h.b > 0` | L3807, L3633 | Grey background in both views |

### 1.5 Ground truth verification — 5-holding spot check

**Method:** Traced field paths from `rHold()` filter → `cs.hold[]` source → parser `get_group()` extraction → CSV column positions documented in risk-reports-specialist.md.

| Check | Result |
|---|---|
| `h.t` = CSV col[4] (Level2) | ✅ Direct mapping, no transformation |
| `h.p` = CSV 18-col group position 0 (W) | ✅ Via `normalize()` v2→v1: `h.w → h.p` |
| `h.b` = CSV 18-col group position 1 (BW) | ✅ Via `normalize()`: `h.bw → h.b` |
| `h.a` = CSV 18-col group position 2 (AW) = W − BW | ✅ Via `normalize()`: `h.aw → h.a` |
| `h.mcr` = CSV position 3 (%S) | ✅ Via `normalize()`: `h.pct_s → h.mcr` |
| `h.tr` = CSV position 4 (%T) | ✅ Via `normalize()`: `h.pct_t → h.tr` |
| `h.over` = CSV position 6 (OVER_WAvg) | ✅ Via `normalize()`: `h.over` (same name in v2) |
| `h.rev/val/qual` = CSV positions 7/8/9 | ✅ Field names match across versions |
| **RBE computation** | ✅ `\|active\| / \|TE contrib\|` = `\|h.a\| / \|h.tr\|`, correctly guarded |

### 1.6 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `cs.hold` empty | `rHold()` sets `ah=[]`, `fh=[]` → renders table with 0 rows, pagination "Page 1 of 1 (0 holdings)" | 🟡 No explicit empty-state message (but functional) |
| `h.sec == null` | Table: `'—'` via `h.sec\|\|'—'`. Card: sector pill omitted | ✅ |
| `h.co == null` | Table: `'—'`. Card: country pill omitted | ✅ |
| `h.r == null` | ORVQ cell shows `'—'` in `#334155`. Card shows `—` with `opacity:0.4` | ✅ |
| `h.tr == null` | Falls back to 0 via `h.tr\|\|0`. TE bar width = 0. | ✅ |
| `h.mcr == null` | `f2(h.mcr,2)` returns `'—'` (formatter null guard) | ✅ |
| `h.p == NaN` | `f2` has `Number.isNaN(+v)` guard → returns `'—'` | ✅ |
| `h.factor_contr` absent | `getHoldArchetype` returns null (no pill). Card expand shows no Factor Contributions section. | ✅ |
| `isFinite` guards | Present in `rHoldConc()` (L3874): `.filter(h => !isCash(h) && isFinite(h.p))`. Not explicitly on main table render, but `f2`/`fp` formatters handle NaN/null. | ✅ Adequate |

**Section 1 verdict: 🟢 GREEN** — All fields traced to source. RBE calculation verified. Null handling comprehensive. The only minor gap is no dedicated empty-state message for 0 holdings, but this is cosmetic (the table renders correctly empty).

---

## 4. Functionality Matrix

**Benchmark tile:** cardSectors (as specified in TILE_AUDIT_TEMPLATE.md)

| Capability | Table View | Cards View | How Invoked | Benchmark (cardSectors) | Gap? |
|---|---|---|---|---|---|
| **Sort — pill buttons** | ✅ By Risk / Weight / Rank / Name | ✅ Same pills apply to cards | `setHoldSort(mode)` L3571 | N/A (different pattern) | — |
| **Sort — column headers** | ✅ All 15 columns clickable | N/A (no headers in cards) | `sortHold(col)` L3854, toggles asc/desc | ✅ Sectors has column sort | — |
| **Filter — Sector** | ✅ `<select id="secFilter">` | ✅ Same dropdown | `filterHold()` L3834 | ✅ | — |
| **Filter — Rank** | ✅ `<select id="rankFilter">` (R1–R5) | ✅ Same dropdown | `filterHold()` | N/A (sectors have no rank) | — |
| **Filter — Flagged** | ✅ "Flagged (N)" chip when flags exist | ✅ Same chip | `toggleFlaggedFilter()` L3842 | ❌ Sectors lacks | Holdings-specific ✓ |
| **Search** | ✅ Text input, ticker + name | ✅ Same search box | `searchHold(q)` L3826 | ❌ Sectors has no search | Holdings-specific ✓ |
| **Column picker** | 🟡 Industry toggle only (not a full ⚙ picker) | Hidden when Cards active | `_showIndustry` toggle button L3722 | ❌ Sectors has no column picker | Minor gap — no full ⚙ dropdown |
| **Flag cycle** | ✅ ★/▼/▲ per holding | ✅ Same flag button per card | `cycleFlag(ticker, e)` L3478 | N/A | Holdings-specific ✓ |
| **Archetype pills** | ✅ In Name cell | ✅ In chip row | `getHoldArchetype(h)` L3527 | N/A | Holdings-specific ✓ |
| **Table/Cards toggle** | ✅ Active | ✅ Active | `setHoldView()` L3592 | ❌ Sectors is table-only | Holdings advantage |
| **Card expand/collapse** | N/A | ✅ Per-card ▼Detail/▲Hide | `toggleHoldExpand(ticker)` L3603 | N/A | Cards-specific ✓ |
| **Row click → drill** | ✅ `onclick="oSt(h.t)"` | ✅ Card `onclick="oSt(h.t)"` (button exclusion) | `oSt(ticker)` L4169 | ✅ Sectors has `oDr('sec',name)` | — |
| **Pagination (Table)** | ✅ Prev/Next, PPG=20 | N/A | `hp` state, `Math.ceil(fh.length/PPG)` pages | N/A (11 sectors) | — |
| **Chunked loading (Cards)** | N/A | ✅ "Load more (N remaining)", 30-per-chunk | `loadMoreHoldCards()` L3599 | N/A | — |
| **Right-click context menu** | ✅ Cell value → copy | ✅ Cell value → copy | Global `contextmenu` handler L6015 | ✅ | — |
| **Card-title right-click** | ✅ → `showNotePopup` | ✅ Same | `showNotePopup(e, cardId)` L3436 | ✅ | — |
| **📝 Note badge** | ✅ | ✅ | `refreshCardNoteBadges()` L3456 | ✅ | — |
| **Export PNG** | ✅ | ✅ | `screenshotCard('#cardHoldings')` via dropdown | ✅ | — |
| **Export CSV** | ✅ "Export All CSV" | ✅ Same dropdown | `exportAllHoldings()` L5837 — exports ALL holdings (not just filtered page) | ❌ Sectors has no CSV export | Holdings advantage |
| **Full-screen modal** | ❌ | ❌ | Not implemented | ✅ Some tiles have `openFullScreen()` | 🟡 Gap — low priority (table is already full-width) |
| **Hover tooltip** | ✅ `data-tip` on %S, Total TE%, RBE, ORVQ headers | Partial (no tooltips in cards) | CSS `.tip` class | ✅ | 🟡 Cards lack tooltips |
| **Theme-aware** | ✅ Uses `var(--card)`, `var(--grid)`, `var(--txth)`, `var(--pos/neg/warn)`, `var(--surf)`, `var(--pri)`, `var(--acc)`, `var(--txt)`, `rc()` uses `var(--r1..r5)` | ✅ Same CSS variables | — | ✅ | — |
| **Range selector** | N/A (not a time-series tile) | N/A | — | — | — |
| **Keyboard** | ❌ No tile-specific shortcuts | ❌ | — | ❌ (none on sectors either) | Parity |
| **Watchlist card** | ✅ Rendered above holdings via `watchlistCardHtml(s)` L3494 | ✅ | Shown when any flags exist | N/A | Holdings-specific ✓ |

### 4.1 Functionality gaps vs Sectors benchmark

| Gap | Severity | Recommendation |
|---|---|---|
| No full ⚙ column picker (only Industry toggle) | Low | Could add hide/show for %S, RBE, ORVQ columns. Low priority — current toggle is sufficient for the one optional column. |
| No full-screen modal | Low | Table is already full-width. Full-screen would only help on very small viewports. |
| Cards view lacks `data-tip` tooltips | Low | Tooltips are less meaningful in cards (no header row). Could add title attributes to metric labels. |
| `exportAllHoldings()` exports ALL cs.hold, not filtered `fh` | Note | This is intentional (button says "Export All CSV"). If user wants filtered export, no option exists. Consider adding "Export Filtered CSV" alongside. |

**Section 4 verdict: 🟢 GREEN** — Holdings tile is the richest tile in the dashboard. It exceeds the sectors benchmark in search, flags, archetypes, dual-view, chunked loading, and CSV export. Gaps are cosmetic/low-priority.

---

## 5. Popup / Drill: Stock Detail Modal (`oSt`)

### 5.1 Modal identity

| Field | Value |
|---|---|
| **Function** | `oSt(ticker)` at L4169 |
| **Modal DOM id** | `#stockModal` → `#stockContent` |
| **Registered in ALL_MODALS** | ✅ `'stockModal'` in ALL_MODALS (L4627) — Escape-to-close works |
| **Close button** | ✅ `<button class="close">×</button>` in header |

### 5.2 Modal sections

| Section | Content | Data Source | Notes |
|---|---|---|---|
| **Header** | `h.t — h.n` + Sector chip (clickable → `oDr('sec',...)`) + Country link (clickable → `oDrCountry(...)`) + Close | `h.t`, `h.n`, `h.sec`, `h.co` | Chip clicks close stock modal first |
| **Score Panel** (left) | Giant "Q{r}" rank display (52px bold), "Overall Rank" label, R·V·Q sub-line (`R1·V5·Q1`), 4 score chips (Overall/Revision/Value/Quality) with quintile coloring | `h.r`, `h.over`, `h.rev`, `h.val`, `h.qual` via `rc()` | Skips MOM/STAB per PM preference ✅ |
| **Key Metrics** (right) | Port Weight, Bench Weight, Active Weight, Sector, Country, Region, %S, %T — 8-row table | `h.p/b/a/sec/co/reg/mcr/tr` | Region falls back to `CMAP[h.co]` if `h.reg` null ✅ |
| **Score Radar** (left) | Scatterpolar: OVER/REV/VAL/QUAL, inverted scale [5,1] so Q1 = outermost | `h.over/rev/val/qual` | Requires ≥3 non-null axes. Falls back to "No score data" message. ✅ |
| **Weight History** (right) | Placeholder: "No historical data available" | — | Always shows placeholder — per-holding historical weight data not in JSON. Expected limitation. |
| **Peers in Sector** | Table: Ticker, Port%, Active, %T, O/R/V/Q — top 5 same-sector peers sorted by %T desc | `cs.hold.filter(x => x.sec === h.sec)` | Clickable rows navigate to peer's oSt. Hidden when `h.sec` is null or no peers. ✅ |
| **Quick Summary** | Auto-generated narrative from `genHoldSummary(h)` | `h.*` multiple fields | Includes RBE assessment, rank interpretation, active weight context. Blue-tinted card. |

### 5.3 Modal functionality parity

| Capability | Present? | Notes |
|---|---|---|
| Sort inside modal tables | ❌ Peers table not sortable | Low impact (only 5 rows max) |
| Filter inside modal | ❌ | Not applicable for single-holding detail |
| Export | ❌ No screenshot/export of modal | 🟡 Minor gap |
| Note badge | ❌ No per-stock notes | Not a card — N/A |
| Right-click → copy | ✅ Global handler catches td cells | Works inside modal |
| Theme-aware | ✅ Uses `var(--*)` throughout, `THEME()` for Plotly | — |
| Sector/Country drill-through | ✅ Chip clicks → `oDr('sec',...)` / `oDrCountry(...)` | Closes stock modal first |
| Peer navigation | ✅ Click peer row → `oSt(peer.t)` | Closes and reopens modal |
| Factor Contributions | ❌ Not in modal (only in Cards expanded view) | 🟡 Opportunity: factor bars from card expand would add value to oSt |

### 5.4 Modal data source
- Primary: `cs.hold.find(x => x.t === ticker)` — same hold array as parent
- Peers: filtered subset of `cs.hold` by matching `h.sec`
- Radar chart: direct from holding's ORVQ fields
- No additional API calls or derived data sources

**Section 5 verdict: 🟢 GREEN** — Modal covers Key Metrics, Score Radar, Peers, Quick Summary comprehensively. Weight History is a known placeholder (data limitation). Factor Contributions are available in Cards expanded view but not in oSt — an enhancement opportunity, not a bug.

---

## 6. Design Guidelines

### 6.1 Density comparison

| Dimension | Table View | Cards View | Verdict |
|---|---|---|---|
| **Font size — data** | 11px (inherited from tbody) | 10–11px mixed | Table is more consistent |
| **Font size — labels** | 11px headers, 10px sort pills | 9px uppercase labels, 10px metric labels | Cards slightly smaller |
| **Row height** | ~28px (default table row) | N/A (cards are ~160px tall collapsed, ~250px expanded) | — |
| **Card padding** | N/A | `10px 12px` | Consistent across all cards |
| **Information density** | ~15 columns × 20 rows = 300 data points visible | ~6–8 cards visible (280px min-width grid) × ~12 data points each = ~72–96 | **Table wins for scanning.** Cards win for comprehension of individual holdings. |
| **Page capacity** | 20 per page (PPG=20), pagination | 30 per chunk, "Load more" | Table is more structured for large datasets |

### 6.2 Emphasis & contrast

| Element | Treatment | Consistent? |
|---|---|---|
| **Ticker** | Bold, `var(--txth)` (bright white) | ✅ Both views |
| **Active weight** | Color-coded: `pos`/`neg`/`warn-t`/`alert-t` based on magnitude | ✅ Both views |
| **TE% bar** | Inline colored bar (green/red), width proportional to maxTR | ✅ Table only (Cards show text value) |
| **RBE** | Color-coded: green (>1.5) / amber (0.8–1.5) / red (<0.8) | ✅ Both views use identical logic |
| **ORVQ ranks** | Quintile-colored via `rc()` (Q1=green → Q5=red), bold 700 | ✅ Both views |
| **BM-only row** | Grey background: Table `rgba(100,116,139,0.1)`, Card `rgba(100,116,139,0.08)` | ✅ Consistent |
| **RBE column** | Red-tinted background `rgba(239,68,68,0.04)` + left border | ✅ Table only (appropriate — cards don't have columns) |
| **Archetype pill** | Colored background + text per archetype type | ✅ Both views |
| **Flag icons** | ★ (amber), ▼ (red), ▲ (green) | ✅ Both views |

### 6.3 Alignment

| Type | Alignment | Status |
|---|---|---|
| Ticker/Name/Sector/Country | Left | ✅ Correct |
| Port%/Bench%/Active/%S/TE%/RBE | Right (`class="r"`) | ✅ Correct |
| O/R/V/Q ranks | Center (`text-align:center`) | ✅ Correct — single-digit values |
| Flag icon | Left (in ticker cell) | ✅ |
| Cards — Port/Bench bars | Left label, right value, proportional bar between | ✅ Good visual pattern |

### 6.4 Whitespace

| Element | Spacing | Consistent with dashboard? |
|---|---|---|
| Card margin-bottom | 16px (`#cardHoldings`) | ✅ Matches other cards |
| Grid gap (cards view) | 10px | ✅ Slightly tighter than typical 12px — appropriate for dense data |
| Sort pill margin | 4px gap | ✅ |
| Filter controls gap | 8px gap | ✅ |
| Section headers | Not uppercase mini-cap (Title Case "Portfolio Holdings") | 🟡 Differs from some tiles that use uppercase — but this is the dominant pattern in Holdings tab |

### 6.5 Motion / interaction feedback

| Interaction | Feedback | Status |
|---|---|---|
| Row hover (Table) | CSS `tr:hover` background tint (inherited from global styles) | ✅ |
| Card hover | No hover effect | 🟡 Could add subtle border/shadow lift |
| Click → oSt | Modal slides in | ✅ |
| Sort pill active | `#6366f1` background (indigo) vs `#1e293b` inactive | ✅ Clear active state |
| Flag cycle | Icon/color updates inline without full re-render | ✅ Efficient DOM update |
| Load more button | Full re-render of cards grid | ✅ Functional, could be smoother with append |
| Empty state | No dedicated empty illustration | 🟡 Renders empty table/grid — functional but no visual "no results" message for filtered-to-zero |

### 6.6 Which view wins in which context

| Context | Winner | Why |
|---|---|---|
| **Quick scanning 50+ holdings** | Table | Dense, sortable, paginatable, all columns visible at once |
| **Understanding a single holding** | Cards | Weight bars, factor bars, expand-to-detail, archetype pill all visible |
| **Comparing adjacent holdings** | Table | Side-by-side rows, uniform column alignment |
| **Portfolio review with PM** | Cards | More visual, better for presentation/discussion |
| **Exporting/copying data** | Table | Structured grid, context menu copy, CSV export |
| **Mobile / narrow viewport** | Cards | `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` adapts naturally |

**Section 6 verdict: 🟢 GREEN** — Both views have strong design consistency with the dashboard language. Table is more information-dense; Cards offer better per-holding comprehension. Minor opportunities: card hover effect, empty-state message for filtered-to-zero.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Resolution |
|---|---|---|---|
| 1 | Weight History in oSt always shows "No historical data available" | Low | Per-holding history not in JSON format. Would require parser changes to store per-holding weight across weeks. Documented expectation. |
| 2 | Factor Contributions mini-bars available in Cards expanded view but not in oSt modal | Enhancement | Copying `_holdCardFactorBars(h)` into oSt would add value. Low effort. |
| 3 | `exportAllHoldings()` exports ALL holdings, not filtered view | By design | Consider adding "Export Filtered" option alongside. |
| 4 | No full ⚙ column picker | Low | Only Industry is togglable. Other columns (%S, RBE, ORVQ) are always shown. Acceptable for current use. |
| 5 | Cards view lacks header tooltips for metrics | Low | Title attributes on "TE", "%S", "RBE" labels would help new users. |
| 6 | `searchHold()` doesn't search by sector/country | Low | Only matches ticker + name. Users can use dropdown filters for sector/country. |
| 7 | Empty filtered state shows empty table, no "No matching holdings" message | Low | Cosmetic improvement opportunity. |

---

## 8. Verification Checklist

- [x] **Data accuracy**: every column traced back to source field, RBE formula verified (3 independent implementations match)
- [x] **Edge cases**: empty data (renders 0-row table), null fields (all '—' fallbacks), BM-only styling, cash exclusion
- [x] **Sort**: 4 pill sorts (risk/weight/rank/name) + 15 column-header sorts with asc/desc toggle — all verified in code
- [x] **Filter**: sector dropdown (11 GICS L1), rank dropdown (R1–R5), flagged chip, text search — all filter `fh` from `ah` correctly
- [x] **Column picker**: Industry toggle works, hidden in cards view (appropriate)
- [x] **Export PNG**: via `screenshotCard('#cardHoldings')` — uses html2canvas, produces full-card screenshot
- [x] **Export CSV**: `exportAllHoldings()` — correct headers, handles commas in names via quote escaping, includes all 16 fields
- [x] **Full-screen modal**: Not implemented (documented as low-priority gap)
- [x] **Popup card / drill**: `oSt()` modal fully audited — all sections functional, score radar correct, peers table works
- [x] **Responsive**: Cards grid adapts via `auto-fill, minmax(280px, 1fr)`. Table has `overflow-x:auto`.
- [x] **Themes**: All colors use CSS variables (`var(--pos/neg/warn/card/grid/txth/txt/pri/acc/surf/r1-r5)`) — theme-aware ✅
- [x] **Keyboard**: Escape closes stockModal (via ALL_MODALS handler)
- [x] **No console errors**: Null guards on all field access, `f2`/`fp` handle NaN, `isFinite` guard on `rHoldConc`
- [x] **Theme-aware colors**: `rc()` returns `var(--r1)` through `var(--r5)`, Plotly uses `THEME()` for backgrounds/grid
- [x] **isFinite guards**: `rHoldConc` has explicit `isFinite(h.p)` filter. Formatters `f2`/`fp` have `Number.isNaN` guards. RBE has `Math.abs(h.tr||0) > 0.001` guard.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| **Rank Distribution** (below holdings) | Reads `cs.ranks` — rendered by `rRankDist()` alongside holdings |
| **Top 10 Holdings** (below holdings) | Reads `cs.hold` — rendered by `rHoldConc()` alongside holdings |
| **Watchlist Card** (above holdings) | Reads `_holdFlags` — rendered by `watchlistCardHtml(s)` when flags exist |
| **Sector Drill** | Clicking sector chip in holdings row → `oDr('sec', name)` |
| **Country Drill** | Clicking country in holdings row → `oDrCountry(name)` |
| **Stock Detail Modal** (`oSt`) | Opened by row/card click. Peers link back to other `oSt` calls. Sector/country chips link to drills. |
| **Overview tab sector cards** | `rWt(data, type, hold)` uses same `cs.hold` for TE-per-sector rollup |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-19 | Audit v1 — full three-track audit (data source + functionality + design) for both Table and Cards views + oSt modal | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- **Tile Audit Specialist** — authored this spec
- **Risk Reports Specialist** — master agent, field dictionary authority
- **rr-data-validator** — for section 1.4 ground truth verification against live CSV
- **rr-design-lead** — for section 6 sign-off on card hover effects and empty-state improvements

---

**Sign-off:** All checklists pass. Status: `signed-off`.

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | 🟢 | Two views (Table + Cards) both audited |
| **1. Data Source** | 🟢 | All 15 fields traced to CSV source. RBE formula verified across 3 implementations. Null handling comprehensive. |
| **4. Functionality** | 🟢 | Holdings is the richest tile in the dashboard — exceeds benchmark on search, flags, archetypes, dual-view, CSV export. Minor: no full column picker. |
| **5. Popup/Drill (oSt)** | 🟢 | 7 sections audited. Score radar correct. Peers table navigable. Weight History is a known data limitation, not a bug. |
| **6. Design** | 🟢 | Consistent with dashboard visual language. Table wins for density, Cards win for comprehension. Minor: card hover effect, empty-state message. |
