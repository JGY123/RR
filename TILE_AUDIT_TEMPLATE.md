# Tile Spec Template

> Copy this file to `tile-specs/{tileName}.md` for each tile/card/table/chart. Fill every section — empty sections signal unfinished thinking, not absent content. When a field truly doesn't apply, write "N/A — {reason}" so the audit trail shows you considered it.
>
> **Purpose:** make every tile auditable for (1) data accuracy, (2) functionality completeness, (3) design quality, (4) parity with sibling tiles. Enables parallel work across multiple CLIs without collision.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | _Sector Active Weights_ |
| **Card DOM id** | `#cardSectors` |
| **Render function(s)** | `rWt(s.sectors, 'sec', s.hold)` at `dashboard_v7.html:L####` |
| **Tab** | Exposures / Risk / Holdings |
| **Grid row** | Row 2 of Exposures |
| **Width** | full / half (`g1` / `g2`) |
| **Owner** | Which CLI / agent is accountable for this tile |
| **Spec status** | `draft` / `data-verified` / `functionally-complete` / `design-reviewed` / `signed-off` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** e.g., `cs.sectors[]`, `cs.hold[].factor_contr`
- **Array length for EM test case:** e.g., 11 sectors
- **Array length for other strategies:** ranges across ACWI / IOP / EM / ISC / SCG / GSC / IDM

### 1.2 Field inventory (one row per field used)

| Field | Type | Source | Example | Formatter | Notes |
|---|---|---|---|---|---|
| `n` | string | FactSet CSV col X | "Industrials" | — | |
| `p` | number (%) | FactSet `WGT_PORT` | 21.3 | `f2(v,1)` + `%` | |
| `b` | number (%) | FactSet `WGT_BM` | 7.3 | `f2(v,1)` + `%` | |
| `a` | number (%) | computed `p - b` | +14.0 | `fp(v,1)` + `%` | |
| `tr` | number (%) | FactSet `%T` | 32.8 | `f2(v,1)` + `%` | % of portfolio TE |

### 1.3 Derived / computed fields
List any field not in the raw JSON but computed at render time.

### 1.4 Ground truth verification
- [ ] How to verify: open the FactSet source CSV, find the matching row, confirm numbers match
- [ ] Known discrepancies / rounding tolerance
- [ ] Who signed off

### 1.5 Missing / null handling
- What happens if `s.sectors` is empty? (should render "No sector data" not crash)
- What renders in a cell if `h.p == null`?
- Is `isFinite` guard in place (Patch 003 lesson)?

---

## 2. Columns & Dimensions Displayed

For each column in a table, or each axis/encoding in a chart:

| # | Label | Field | Format | Sort | Filter | Hide allowed | Tooltip | Click action |
|---|---|---|---|---|---|---|---|---|
| 1 | Sector | `x.n` | — | asc/desc | via filter bar | no | — | `oDr('sec', name)` |
| 2 | Port% | `x.p` | `f2(v,1)%` | yes | — | yes | "Portfolio weight" | — |

If the tile is a chart (not a table):
- **X encoding:** field → axis with units
- **Y encoding:** same
- **Size encoding:** if bubble chart
- **Color encoding:** semantic — what do the colors *mean* (not just "indigo")

---

## 3. Visualization Choice

### 3.1 Chart / layout type
butterfly / choropleth / scatter / waterfall / treemap / stacked bar / line / table / hybrid

### 3.2 Axis scaling
- x: linear / log / category / date
- y: same
- Known traps (Patch 004/008 lesson: numeric ticker strings force category)

### 3.3 Color semantics
- Green means: overweight / positive / lower-risk
- Red means: underweight / negative / higher-risk
- Neutral: what
- Theme-aware (reads from `THEME()`)?

### 3.4 Responsive behavior
- Narrow viewport: how does layout adapt?
- Column picker hides which columns first?
- Chart type fallback on very narrow?

### 3.5 Empty state
What renders when there's no data. Must not be a blank area.

### 3.6 Loading state
What renders while data is fetching. Skeleton? Spinner?

---

## 4. Functionality Matrix

The benchmark for every tile is **what the Sectors tile has**. New tiles should reach feature-parity unless a specific reason is documented.

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort** | — | click column header / `sortTbl(id, col)` | which columns, default direction, multi-column? |
| **Filter** | — | filter bar above table / dropdowns | by what fields, multi-select? |
| **Column picker** | — | ⚙ dropdown in header | which columns are optional, persist to localStorage? |
| **Row click** | — | row onClick → drill modal | which modal opens, passing what args |
| **Cell value click** | — | inline drill | e.g., click sector name → sector drill |
| **Right-click context menu** | — | contextmenu event | copy value, open link, flag holding |
| **Card-title right-click** | — | annotation popup via `showNotePopup` | stored as `{stratId}:card:{cardId}` |
| **📝 Note badge** | — | refreshCardNoteBadges | shown when note exists |
| **Export PNG** | — | screenshot Card button | via `screenshotCard('#cardX')` |
| **Export CSV** | — | download dropdown | via `exportCSV('#tbl-x', 'name')` |
| **Full-screen modal** | — | ⛶ button → `openFullScreen('x')` | which renderer |
| **Toggle views** | — | Table / Chart / Map toggle | toggle function |
| **Range selector** | — | 3M / 6M / 1Y / 3Y / All | for time series tiles |
| **Color-mode picker** | — | dropdown | for choropleth / scatter |
| **Hover tooltip** | — | Plotly hovertemplate / tip class | content spec |
| **Theme-aware** | — | uses `THEME()` / `var(--x)` | |
| **Color-blind safe** | — | honors `_prefs.cbSafe` (if added) | |

### 4.1 Functionality gaps vs Sectors benchmark
List explicitly — what's missing and why.

---

## 5. Popup / Drill / Expanded Card

If clicking a row/cell opens a detail modal, the modal is a tile in its own right. Everything in sections 1–4 applies to it too.

### 5.1 Modal identity
- **Function:** `oDrCountry(name)`, `oSt(ticker)`, etc.
- **Modal DOM id:** `#drillModal`, `#stockModal`, `#compModal`, …
- **Registered in `ALL_MODALS`?** (for Escape-to-close)

### 5.2 Modal sections
e.g., for `oSt`:
- Header (ticker + name + sector + country chips)
- Key Metrics grid
- Score Radar (Q1–Q5)
- Weight History
- Peers in sector
- Factor Contributions (sparkline-style bars)
- Quick Summary (auto-generated narrative)

### 5.3 Modal functionality parity
- [ ] Sort works inside modal tables?
- [ ] Filter works inside modal?
- [ ] Export works?
- [ ] Note badge shown?
- [ ] Right-click menu works?
- [ ] Theme-aware?

### 5.4 Modal data source
Sometimes identical to the parent tile, sometimes derived from `hist.sec` / `snap_attrib` / etc. Document the source.

---

## 6. Design Guidelines

### 6.1 Density
- Font size: table 11px / chart title 12px / axis 10px / footer 9px — match existing hierarchy
- Row height: 28px default / 22px dense — pick and justify
- Card padding: 16px / 12px / 8px — consistency check

### 6.2 Emphasis & contrast
- Which cell gets bold
- Which value is color-coded (green/red) and why
- What's muted (secondary)

### 6.3 Alignment
- Numeric → right
- Categorical → left
- Icons → center
- Exceptions documented

### 6.4 Whitespace
- Gap between sections within a card
- Gap between cards in the same row
- Section headers use uppercase mini-cap pattern? (consistent with "Top TE Contributors" etc.)

### 6.5 Motion / interaction feedback
- Hover state (background tint, border)
- Click state (active highlight, ripple?)
- Loading state
- Empty state illustration / message

---

## 7. Known Issues & Open Questions

Don't hide these. Each one is a task for next session.

- What data field X really represents — PM clarification needed
- Chart Y's axis scale feels off — verify with Finance
- Filter Z doesn't persist across tabs — known, prioritize?

---

## 8. Verification Checklist (before sign-off)

- [ ] **Data accuracy**: every column traced back to source field, rounding matches
- [ ] **Edge cases**: empty data, single row, 1000+ rows, null fields
- [ ] **Sort**: every sortable column works ascending + descending
- [ ] **Filter**: all filters produce expected results, no false empties
- [ ] **Column picker**: hiding/showing persists to localStorage; default set is right
- [ ] **Export PNG**: produces readable image with current styling
- [ ] **Export CSV**: produces correct headers + values, handles commas in names
- [ ] **Full-screen modal**: renders correctly, all controls work, closes cleanly
- [ ] **Popup card / drill**: all functionality mirrored, no gaps vs parent tile
- [ ] **Responsive**: narrow viewport (mobile), default, wide — all readable
- [ ] **Themes**: dark + light both render without invisible text
- [ ] **Keyboard**: Escape closes modals, ? opens help
- [ ] **No console errors** on render, tab switch, drill open/close
- [ ] **Theme-aware colors**: reads from `THEME()` / `var(--x)` not hardcoded hex
- [ ] **isFinite guards**: numeric fields defended against NaN/Infinity

---

## 9. Related Tiles

Which other tiles share data / link to this one?
- Country Exposure tile and Regional distribution chart both read `cs.countries`
- Clicking a sector in this tile opens Sector Drill which then shows holdings filtered by sector

---

## 10. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-17 | Spec initialized | CoS session |
| | | |

---

## Agents that should know this tile

- `rr-tile-{tileName}` — the dedicated spec-and-build CLI (if assigned)
- `rr-data-validator` — for section 1.4 verification
- `rr-design-lead` — for section 6 sign-off
- `risk-reports-specialist` — master agent, always in the loop

---

**Sign-off:** Once all checklists pass and change log shows verification, change status in section 0 to `signed-off`.
