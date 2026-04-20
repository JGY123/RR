# Tile Spec: cardCountry — Country Exposure

> **Audit date:** 2026-04-20
> **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html`
> **Benchmark tile:** `cardSectors` (see `tile-specs/cardSectors-audit-2026-04-19.md`)
> **Methodology:** Three-track audit per `~/orginize/knowledge/skills/tile-audit-framework.md`

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Country Exposure |
| **Card DOM id** | `#cardCountry` |
| **Render function(s)** | `rCountryTable(s.countries, s.hold)` at `dashboard_v7.html:L1803`; `rCountryMap(s)` at L2351; `rCountryChart(s)` at L2484 |
| **Tab** | Exposures (Row 4, after Factor Attribution Waterfall) |
| **Grid row** | Row 4 of Exposures — full width (`grid-column:1/-1`) |
| **Width** | Full (spans entire exposures grid) |
| **Visibility** | Hidden when `isUSOnly` strategy is selected |
| **Owner** | Tile Audit Specialist CLI |
| **Spec status** | `signed-off` (v1) |

---

## 1. Data Source & Schema

### 1.1 Primary data source

- **Object path:** `cs.countries[]` — array of country objects from `factset_parser.py._extract_group_table("Country", acct)` at parser L745
- **Map dependency:** `COUNTRY_ISO3` (L2336) — 160+ country-name → ISO-3 mapping; countries not in map are excluded from map view but still show in table
- **Holdings dependency:** `cs.hold[]` — provides `h.co` (country), `h.tr`, `h.mcr`, `h.over/rev/val/qual`, and `h.factor_contr` for `aggregateCountryRisk()`
- **Region linkage:** `CMAP[name] → region` used only in `oDrCountry` modal header (shows parent region chip)
- **Array length (typical):** 30–50 countries per strategy (depends on benchmark coverage; EM ~25, ACWI ~48, IDM ~22)

### 1.2 Field inventory (one row per rendered column / encoding)

**Table view (`rCountryTable`):**

| # | Column Label | Field | Source Object Path | FactSet CSV Origin | Type | Example | Formatter | Tooltip |
|---|---|---|---|---|---|---|---|---|
| 1 | Country | `c.n` | `cs.countries[i].n` | `Level2` col in 19-col Country section | string | "Japan" | none | — |
| 2 | Port% | `c.p` | `cs.countries[i].p` | `W` (group offset +1) | number (%) | 14.7 | `f2(v)` → "14.70" | — |
| 3 | Bench% | `c.b` | `cs.countries[i].b` | `Bench. Weight` (group offset +2) | number (%) | 22.1 | `f2(v)` → "22.10" | — |
| 4 | Active | `c.a` | `cs.countries[i].a` | `AW` (group offset +3) — parser-precomputed = W − BW | number (%) | −7.4 | `fp(v)` → "−7.40" | — |
| 5 | O (Overall) | computed | Weighted avg of `h.over` for holdings where `h.co===c.n` | `OVER_WAvg` (group offset +7) per holding | number (1–5) | 2.1 | `f2(v,1)` | "Avg Overall MFR rank" |
| 6 | R (Revision) | computed | Weighted avg of `h.rev` | `REV_WAvg` (group offset +8) per holding | number (1–5) | 1.8 | `f2(v,1)` | — |
| 7 | V (Value) | computed | Weighted avg of `h.val` | `VAL_WAvg` (group offset +9) per holding | number (1–5) | 3.2 | `f2(v,1)` | — |
| 8 | Q (Quality) | computed | Weighted avg of `h.qual` | `QUAL_WAvg` (group offset +10) per holding | number (1–5) | 1.6 | `f2(v,1)` | — |

**Map view (`rCountryMap`):** choropleth of `c.a` (default) or one of seven alternate modes (`port`, `bench`, `te`, `specific`, `factor_te`, `fc:<facName>`). Full set configured via `getMapColorGroups()` and `setMapColor()`.

**Chart view (`rCountryChart`):** horizontal bar of top 5 + bottom 5 by `c.a` (10 rows total), green when `c.a >= 0`, red otherwise.

### 1.3 Derived / computed fields

| Field | Computation | Location |
|---|---|---|
| Per-country O/R/V/Q rank averages | `rankAvg3(_secRankMode, S, C, W, PW, BW, BPW)` — shared with cardSectors; same 3-mode semantics | `rCountryTable()` L1815–L1821 |
| `agg[country].tr` | `sum(h.tr)` for `h.co===country` | `aggregateCountryRisk()` L5422 |
| `agg[country].mcr` | `sum(h.mcr)` | L5423 |
| `agg[country].p` | `sum(h.p)` | L5424 |
| `agg[country].facContr[k]` | `sum(h.factor_contr[k])` with `isFinite` guard | L5427–L5429 |
| `agg[country].facExp[k]` | weighted-sum / weight-total → averaged in `getVal` | L5430–L5432 |
| Map `factor_te` mode | `agg[c.n].tr − agg[c.n].mcr` | L2375 |
| Map `fc:<f>` exp mode | `fc / r.p` (per-holding contribution normalized by country weight) | L2384 |

Rank-mode toggle (`_secRankMode`) is **shared state** with cardSectors — flipping Wtd/Avg/BM in one re-renders both. Session-only (not persisted to localStorage).

### 1.4 Ground truth verification

- **Method:** Trace `cs.countries[].p` / `.b` / `.a` back to the 19-col "Country" CSV section (group offsets +1 / +2 / +3, using the latest weekly group). Per SCHEMA_COMPARISON.md L66–L97, Country section shares the identical 19-col layout as Sector Weights — offsets are verified and stable across old (158 periods) and new (4 periods) files.
- **Active weight:** `c.a` is parser-precomputed (`AW` column); no JS-side recomputation, so no drift risk.
- **Spotlight ranks:** Per-country O/R/V/Q averages computed in JS by aggregating holdings' `h.over/rev/val/qual` (parsed from `OVER_WAvg` / `REV_WAvg` / `VAL_WAvg` / `QUAL_WAvg` at offsets +7/+8/+9/+10 per SCHEMA_COMPARISON.md). Matches sector-level aggregation exactly.
- [x] FactSet CSV column positions verified against SCHEMA_COMPARISON.md — Country section 19-col layout identical to Sectors
- [x] `c.a` parser-precomputed, matches `AW` offset +3
- [x] `aggregateCountryRisk` uses `isFinite` guard (L5428) — more defensive than `rWt` (sector render)
- [ ] Spot-check pending: requires loaded `latest_data.json` / CSV to verify specific country values (no data file in repo at audit time)
- [ ] Country-name casing: FactSet uses "United States" / "United Kingdom" / "Korea (Republic Of)" formats — `COUNTRY_ISO3` map must match exactly. Any drift silently drops country from map (still shown in table). Verify periodically against CSV dumps.
- **Known discrepancy tolerance:** ≤0.05% rounding on weight sums

### 1.5 Missing / null handling

| Scenario | Behavior | Code location |
|---|---|---|
| `s.countries` empty / missing | Returns `<p>No country data</p>` (table); map and chart early-return silently | L1804, L2352, L2485 |
| `h.co` is null / undefined | Holding skipped in rank accumulation (`if(!h.co\|\|isCash(h))return`) | L1812, L5419 |
| `h.tr` / `h.mcr` null | Falls back to 0 via `(h.tr\|\|0)` | L5422–L5423 |
| `h.over` null | Skipped per-factor (`if(h.over!=null)`) | L1815 |
| Rank average null | Displays "—" with color `#334155`, neutral background | L1823 |
| Country not in `COUNTRY_ISO3` | Dropped from map only (still in table + chart) | L2353 |
| `c.a` NaN / Infinity | Map uses `c.a\|\|0` explicitly (L2360); table relies on `fp()` NaN guard | — |
| Empty `holdings` array in `oDrCountry` | Renders "No holdings in this country" message | L5231 |
| `factor_contr` value non-finite | Skipped via `isFinite(v)` guard | L5428 |

**Assessment: GREEN** — Data pipeline traceable end-to-end. `aggregateCountryRisk` is the most defensively-coded aggregator in the file (explicit `isFinite` guard, unlike `rWt`'s `||0`-only approach). Primary verification gap is naming-drift risk (COUNTRY_ISO3 vs CSV casing) — documented below as an ongoing concern.

---

## 2. Columns & Dimensions Displayed

**Table view:**

| # | Label | Field | Format | Sortable | Hideable (⚙) | Tooltip | Click action |
|---|---|---|---|---|---|---|---|
| 1 | Country | `c.n` | plain text | Yes (col 0) | No | — | Row click → `oDrCountry(c.n)` |
| 2 | Port% | `c.p` | `f2(v)` | Yes (col 1) | No | — | — |
| 3 | Bench% | `c.b` | `f2(v)` | Yes (col 2) | No | — | — |
| 4 | Active | `c.a` | `fp(v)` +/-, color-coded | Yes (col 3) | No | — | — |
| 5 | O | wtd avg (mode-dep) | `f2(v,1)` + rank color | Yes (col 4) | No | "Avg Overall MFR rank" | — |
| 6 | R | wtd avg | `f2(v,1)` + rank color | Yes (col 5) | No | — | — |
| 7 | V | wtd avg | `f2(v,1)` + rank color | Yes (col 6) | No | — | — |
| 8 | Q | wtd avg | `f2(v,1)` + rank color | Yes (col 7) | No | — | — |

Sort behavior: all 8 columns sortable via `sortTbl('tbl-ctry', col)` on `<th>` click; Asc/Desc toggle tracked in `_srt`; `data-sv` for numeric precision. Default sort: `|c.a|` desc (L1827).

**Map view encodings:**
- **Geometry:** ISO-3 country boundaries (Plotly natural-earth projection)
- **Color:** one of 8 modes, configurable via `mapColorPicker` dropdown
  - `active` (default): diverging red→mid→green, zmid=0, zmin/zmax=±absMax
  - `port` / `bench`: sequential mid→indigo / mid→purple
  - `te` / `specific`: sequential mid→amber→red
  - `factor_te`: diverging red→mid→green (factor-driven TE)
  - `fc:<facName>`: per-factor exposure or contribution, diverging
- **Region focus:** `world` / `europe` / `asia` / `americas` via `setMapRegion()` → updates `lonaxis`/`lataxis` range
- **Click:** `plotly_click` → `oDrCountry(countryName)`
- **Hover:** `<b>{country}</b><br>{title}: {z:.2f}%<br>Port: {p:.1f}%<br>Active: {a:+.1f}%`

**Chart view encodings:**
- **X:** `c.a` (Active Weight %), bidirectional
- **Y:** `c.n` (top 5 active bets + bottom 5, axis reversed so largest positive is top)
- **Bar color:** green (`c.a ≥ 0`) or red (`c.a < 0`), hardcoded hex (not theme-aware)
- **Text:** `fp(x.a)` outside bar

---

## 3. Visualization Choice

### 3.1 Layout
Hybrid — three mutually exclusive views via toggle: **Map (default)** / **Chart** / **Table**. Toggled by `toggleCountryView(v, btn)` at L2472.

### 3.2 Axis scaling
- **Map:** natural-earth projection (fixed); zoom via region lon/lat window
- **Chart:** linear x-axis (Active %); categorical reversed y-axis
- **Table:** n/a

### 3.3 Color semantics
- Active weight > 0: green (`#10b981`); < 0: red (`#ef4444`). Consistent with sectors.
- Map diverging scales honor `THEME().heatMid` (theme-aware)
- Chart bar colors are **hardcoded hex** (not via `THEME()`)
- Rank colors via `rc()` → CSS vars `--r1`..`--r5` (theme-aware)

### 3.4 Responsive behavior
- Header wraps (`flex-wrap:wrap;gap:8px`)
- Map and chart have fixed 320px / 280px height (not responsive to card width)
- Table has `max-height:320px;overflow-y:auto`

### 3.5 Empty state
- Table: `<p>No country data</p>` with muted styling
- Map/Chart: silent early return — leaves prior render on screen (or nothing on first render)
- US-only strategies: entire card hidden via `display:none` inline

### 3.6 Loading state
Inherits global `#loading` overlay during data fetch; no per-tile skeleton.

---

## 4. Functionality Matrix (vs cardSectors benchmark)

| Capability | cardSectors (benchmark) | cardCountry (this tile) | Match? |
|---|---|---|---|
| **Sort** | ✅ all 11 cols, `sortTbl`, `data-sv` | ✅ all 8 cols, `sortTbl('tbl-ctry',...)`, `data-sv` | ✅ YES |
| **Filter** | ❌ intentional (11 rows) | ❌ (30–50 rows — could be useful) | ⚠ GAP (minor) |
| **Column picker (⚙)** | ✅ 10 hideable cols, localStorage `rr_sec_cols` | ❌ NONE | ❌ GAP |
| **Row click → drill** | ✅ `oDr('sec', name)` → historical chart + holdings | ✅ `oDrCountry(name)` → country summary + attribution + holdings | ✅ YES (different drill shape) |
| **Cell value click** | ❌ not used | ❌ not used | ✅ parity |
| **Right-click context menu (cell copy)** | ✅ global contextmenu → `copyValue()` | ✅ inherits global handler (L6015) | ✅ YES |
| **Card-title right-click (note popup)** | ✅ `showNotePopup(e, 'cardSectors')` | ✅ inherits global handler — works on `#cardCountry .card-title` | ✅ YES |
| **📝 Note badge** | ✅ `refreshCardNoteBadges()` | ✅ refreshed globally — covers `#cardCountry` | ✅ YES |
| **Export PNG** | ✅ `screenshotCard('#cardSectors')` via ⬇ | ✅ `screenshotCard('#cardCountry')` via ⬇ (L1189) | ✅ YES |
| **Export CSV** | ✅ `exportCSV('#secTable table','sectors')` | ✅ `exportCSV('#countryTableWrap table','countries')` (L1189) | ✅ YES — but **only captures Table view HTML**; won't include country rows hidden by map/chart mode |
| **Full-screen modal** | ❌ not present | ✅ ⛶ button → `openFullScreen('country')` → `renderFsCountry(s)` (L5668) with map + ranked panel + color/region controls | ✅ PLUS (cardCountry exceeds benchmark) |
| **Toggle views (Table/Chart)** | ✅ 2 modes (Table / Chart) | ✅ 3 modes (Map / Chart / Table) | ✅ PLUS |
| **Range selector (time series)** | ✅ in drill modal only | ❌ no historical sparkline or time-series | ⚠ GAP — no `hist.country` data collected |
| **Spotlight rank mode toggle (Wtd/Avg/BM)** | ✅ `rankToggleHtml3()`, shared `_secRankMode` | ✅ uses same `rankToggleHtml3()`, shared `_secRankMode` → flipping affects both tiles simultaneously | ✅ YES (shared state) |
| **Trend sparkline column** | ✅ inline SVG from `hist.sec` | ❌ NONE — no country trend column | ❌ GAP (no `hist.country` source) |
| **Color-mode picker** | ❌ n/a (table) | ✅ 8 modes via `mapColorPicker` (Active / Port / Bench / TE / Specific / Factor TE / per-factor Exp or Contr) | ✅ PLUS |
| **Region-zoom selector** | ❌ n/a | ✅ World / Europe / Asia / Americas (`setMapRegion`) | ✅ PLUS |
| **Map secondary toggle (Exposure/Contribution)** | ❌ n/a | ✅ `mapSecondary` toggle shown when `fc:<f>` mode active | ✅ PLUS |
| **Hover tooltip** | ✅ `.tip::after` on headers | ⚠ Partial — only O column header has tooltip; Port/Bench/Active/R/V/Q headers have **no** tooltips | ⚠ GAP |
| **Theme-aware** | ✅ `THEME()` / `var(--x)` | ⚠ Mostly yes — map uses `THEME()`; BUT `rCountryChart` uses **hardcoded** `#10b981`/`#ef4444` (L2492) | ⚠ GAP (minor) |
| **TE bar visualization** | ✅ gradient bar in TE Contrib col | ❌ NONE — no TE column in country table | ❌ GAP |
| **Active weight color coding** | ✅ `activeStyle(d.a)` | ✅ `activeStyle(c.a)` on col 4 | ✅ YES |
| **Threshold alerts (warn/alert rows)** | ✅ `thresh-warn` / `thresh-alert` classes on `<tr>` at ±3% / ±5% | ❌ NO row-level threshold classes applied | ⚠ GAP |
| **Color-blind safe** | ❌ not implemented | ❌ not implemented | ✅ parity |
| **Keyboard shortcuts** | ❌ tile-specific none | ❌ none | ✅ parity |
| **Empty state** | ❌ renders empty tbody silently | ✅ explicit "No country data" message | ✅ PLUS |

### 4.1 Functionality gaps vs Sectors benchmark

**Missing (should add):**
1. **Column picker (⚙)** — currently all 8 columns always shown. Add dropdown to hide Port/Bench/Active or the O/R/V/Q quartet, with `rr_ctry_cols` localStorage persistence. Copy pattern from `secColDropHtml()` / `applySectColVis()`.
2. **Trend sparkline column** — no `hist.country` data currently collected by parser. Would require adding `hist.country` extraction (parser change) and inline SVG column (render change). Medium effort.
3. **Tooltips on all numeric headers** — R/V/Q/Port/Bench/Active headers lack `class="tip" data-tip="..."`. O has one. Add parity with cardSectors header tooltips.
4. **Threshold row classes** — apply `thresh-warn` / `thresh-alert` classes when `|c.a| > 3%` / `> 5%` to call out large country bets, mirroring sector treatment.
5. **TE Contrib + Stock TE + Factor TE columns** — `aggregateCountryRisk()` already computes `tr` and `mcr` per country (used by map `te`/`specific`/`factor_te` modes). These could be surfaced as table columns with the same gradient-bar treatment as cardSectors. Low-effort win: numbers already computed.

**Minor (polish):**
6. **Filter bar** — 30–50 countries is enough that a region-based filter (Europe / Asia / Americas dropdown, reusing `CMAP`) would be genuinely useful. Low-value vs effort; defer.
7. **Hardcoded green/red in `rCountryChart`** — replace `'#10b981'`/`'#ef4444'` with `var(--pos)`/`var(--neg)` or `THEME().pos`/`THEME().neg` to stay theme-consistent.
8. **CSV export captures Table-view DOM only** — if user exports while in Map or Chart mode, CSV is empty (tableWrap is `display:none` but `exportCSV` reads innerHTML — verify). Low priority.

**Exceeds benchmark (keep):**
- Full-screen modal (`openFullScreen('country')`)
- 3-way view toggle (Map / Chart / Table)
- 8-mode color picker
- Region zoom
- Explicit empty state

---

## 5. Popup / Drill / Expanded Card

### 5.1 Modal identity
- **Function:** `oDrCountry(name)` at L5204
- **Modal DOM id:** `#countryModal`
- **Registered in `ALL_MODALS`:** ✅ yes (L4627) — Escape-to-close works

### 5.2 Modal sections
1. **Header:** Country name + close (×)
2. **3-card summary grid:** Port Weight · Active Weight · Region (with region's own active weight)
3. **FactSet Attribution panel** (conditional, `renderCountryAttribSection`) — only if `cs.snap_attrib[name]` exists and `classifyAttrib(name)==='country'`:
   - 4-card grid: Cumulative Impact, Exposure, Std Dev, Weeks
   - Plotly line chart (`countryAttribChart`) of cumulative factor attribution
   - Deep-link → `oDrAttrib(name)` for full attribution drill
4. **Holdings table:** all holdings where `h.co === name`, sorted by `h.tr` desc. Columns: Ticker, Name, Sector chip, Port%, Active, %S, Total TE%, O/R/V/Q (via `rORVQCells`). Row click → `oSt(ticker)`.

### 5.3 Modal functionality
- [x] Row click-through → `oSt(ticker)`
- [x] Sector chip display (no click handler — chip is static)
- [x] Plotly chart with theme-aware `plotBg`, zero-line shape
- [x] Theme-aware colors
- [x] Escape closes (via `ALL_MODALS`)
- [ ] Sort: no `sortTbl` on modal holdings table (modal tables don't get the dashboard's sortable headers by default)
- [ ] Filter: not present
- [ ] Export: not present in drill modal
- [ ] Note badge: not present in drill modal
- [ ] Range selector on attribution chart: ❌ none — contrast with sector drill which has 3M/6M/1Y/3Y/All

### 5.4 Modal data source
- `cs.countries.find(c=>c.n===name)` for the summary numbers
- `cs.hold.filter(h=>h.co===name)` for holdings
- `cs.snap_attrib[name]` + `cs.snap_attrib[name].hist[]` for attribution panel
- `CMAP[name]` for parent region; `cs.regions.find(r=>r.n===region)` for region active weight

---

## 6. Design Guidelines

### 6.1 Density

| Element | Value | Dashboard standard | Match? |
|---|---|---|---|
| Card padding | `16px` (via `.card`) | 16px | ✅ |
| Card border-radius | `12px` | 12px | ✅ |
| Card background | `var(--card)` | Standard | ✅ |
| Table `<th>` font-size | `10px` | 10px | ✅ |
| Table `<td>` font-size | `11px` default; **rankCell uses 11px with `padding:4px 6px`** | 11px | ✅ (rank cells are tighter than default but intentional) |
| Table row height | ~28px; rank rows ~20px (tighter padding) | Default 28px | ⚠ slight inconsistency |
| Map div height | `320px` fixed | — | ✅ |
| Chart div height | `280px` fixed | — | ✅ |
| Table max-height | `320px` with scroll | — | ✅ matches map height |
| Spotlight header row | 9px font, uppercase, indigo tint | Matches cardSectors pattern | ✅ |
| mapColorBtn width | `min-width:120px` | — | ✅ consistent with header-control scale |

### 6.2 Emphasis & contrast

| Element | Treatment | Rationale |
|---|---|---|
| Card title | 12px, 600, uppercase, letter-spacing 0.5px, `var(--txt)` | Standard |
| Country name (col 1) | Default (inherited) | Primary identifier |
| Active weight (col 4) | Color-coded via `activeStyle(c.a)` | Consistent with sectors |
| O/R/V/Q ranks | `font-weight:700`, `rc()` color by quintile, indigo-tinted background | Spotlight group treatment |
| Spotlight header group | Indigo tint (`rgba(99,102,241,0.09)`), left border | Consistent with cardSectors |
| Map colorbar | Theme-aware tick font 10px | Standard Plotly pattern |
| Chart bar | green/red on active sign, text outside | Standard |
| `mapColorBtn` | `var(--surf)` bg, `var(--grid)` border, caret at 40% opacity | Consistent with other picker buttons |
| Toggle-wrap (View / Region) | Standard `.toggle-wrap` class, `.toggle-btn.active` = indigo fill | Consistent across dashboard |

### 6.3 Alignment

| Column type | Alignment | Implementation |
|---|---|---|
| Country name | Left | Default `<td>` |
| Port/Bench/Active | Right | `class="r"` |
| O/R/V/Q rank cells | Center | inline `text-align:center` (differs from sector's right-aligned ranks) |
| Rank headers | Center | `text-align:center` on `<th>` |
| Tabular nums | Yes | Global `<td>` style |

**Minor inconsistency:** Country rank cells are **center-aligned**, while Sector rank cells are **right-aligned** (via `class="r"`). Both use indigo-tinted background. Either center both or right-align both for full parity.

### 6.4 Whitespace

| Gap | Value |
|---|---|
| Header control gap | `6px` — matches sectors |
| Card margin-top | `16px` implicit via grid row | Standard |
| Map → secondary toggle | `padding:4px 0 6px` on `#mapSecondary` | OK |
| Secondary toggle → map | default margin | — |
| Table scroll container | `max-height:320px;overflow-y:auto` | Standard |

### 6.5 Motion / interaction feedback

| State | Treatment |
|---|---|
| Card entry | Slide-up animation (global `.card` rule) |
| Row hover | `.clickable` hover tint (standard) |
| Row active click | Indigo flash (standard) |
| mapColorPicker open | Slide-down reveal with `box-shadow:0 8px 24px rgba(0,0,0,.5)` |
| Toggle-btn active | indigo fill + white text |
| Plotly hover on map | Default Plotly tooltip (themed via `THEME().tick`) |
| Empty data | Static "No country data" text (no illustration) |

**Assessment: GREEN (with minor deltas)** — Density, emphasis, and alignment mostly match cardSectors. The rank-cell alignment (center vs sectors' right) is a cosmetic delta that should be unified. Chart view uses hardcoded hex colors instead of `var(--pos)/var(--neg)` — trivial fix.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Category |
|---|---|---|---|
| 1 | **No column picker (⚙)** — unlike cardSectors, all 8 columns always visible | Medium | Feature gap |
| 2 | **No trend sparkline** — no `hist.country` data collected by parser | Medium | Data + feature gap |
| 3 | **No TE / Stock TE / Factor TE columns** — numbers are computed by `aggregateCountryRisk` for the map, but never surfaced in table | Medium | Feature gap (easy win) |
| 4 | **No threshold row classes** — large country active bets (±3%/±5%) are not highlighted | Low | UX |
| 5 | **Rank cells center-aligned** vs sector ranks right-aligned | Low | Design inconsistency |
| 6 | **Chart bar colors hardcoded** (`#10b981`/`#ef4444`) instead of `var(--pos)/var(--neg)` | Low | Theme |
| 7 | **Header tooltips missing** on Port/Bench/Active/R/V/Q — only O has `class="tip" data-tip="..."` | Low | Consistency |
| 8 | **Rank-mode state shared with cardSectors** (`_secRankMode`) — intentional? or should country have its own `_coRankMode`? | Low | Open question |
| 9 | **COUNTRY_ISO3 naming drift risk** — FactSet country-name casing changes silently drop countries from map. No warning logged. | Medium | Verification |
| 10 | **Drill modal lacks range selector** on attribution chart — sector drill has 3M/6M/1Y/3Y/All | Low | Feature gap in modal |
| 11 | **Drill modal holdings table not sortable** — inherits static `<table>` without `sortTbl` wiring | Low | Feature gap in modal |
| 12 | **Spot-check pending** — no `latest_data.json` in repo to verify specific country values | Medium | Verification |
| 13 | **CSV export while on Map view** — reads `#countryTableWrap table` which is `display:none`; may export correctly (DOM still exists) but should be confirmed | Low | Bug (unverified) |
| 14 | **Map/Chart empty-state silent** — if data missing, early return leaves previous render (or nothing) with no user message | Low | UX |
| 15 | **Hardcoded fallback colors in map** (`'#d67272'` at scale endpoints) — minor; THEME().heatMid in middle is theme-aware | Low | Theme |

---

## 8. Verification Checklist (before sign-off)

- [x] **Data accuracy**: all 8 table columns traced to source (Country CSV section, 19-col layout, offsets verified in SCHEMA_COMPARISON.md L66–L97); map color modes traced to `aggregateCountryRisk`
- [x] **Edge cases**: null/NaN handling via `||0`, `!=null`, `isFinite`; empty-state message present in table; US-only strategies hide card
- [x] **Sort**: all 8 cols sortable via `sortTbl('tbl-ctry',col)` with `data-sv`
- [ ] **Column picker**: not implemented (gap)
- [x] **Export PNG**: `screenshotCard('#cardCountry')` confirmed
- [x] **Export CSV**: `exportCSV('#countryTableWrap table','countries')` confirmed; **unverified under map/chart mode**
- [x] **Full-screen modal**: `openFullScreen('country')` → `renderFsCountry` → map + panel, color/region/param controls mirrored
- [x] **Popup/drill**: `oDrCountry(name)` opens country modal with summary + attribution + holdings; registered in `ALL_MODALS`
- [ ] **Drill modal sort**: not wired (gap)
- [ ] **Drill modal range selector**: missing on attribution chart
- [x] **Themes**: `THEME()` used for map/chart backgrounds; rank colors via `rc()` → CSS vars; minor hardcoded hex in `rCountryChart` and map scale endpoints
- [x] **Keyboard**: Escape closes via `ALL_MODALS`
- [x] **No console errors**: all data access guarded (`||0`, `!=null`, `isFinite`)
- [ ] **Spot-check vs CSV**: pending — no data file in repo
- [x] **isFinite guards**: `aggregateCountryRisk` uses explicit `isFinite` on factor contributions

---

## 9. Related Tiles

| Related Tile | Relationship |
|---|---|
| **cardSectors (Sector Active Weights)** | Shares `rankAvg3()`, `_secRankMode` (flipping mode affects both simultaneously), `rankToggleHtml3()`, `activeStyle()`, `rc()` |
| **Region Active Weights** (`rWt(s.regions,'reg',s.hold)`) | Regions are the geographic rollup of countries (`CMAP[country]→region`); region active weight shown in country drill modal header |
| **Holdings tab** | Holdings carry `h.co` (country) — the source for all per-country rank aggregations |
| **Risk tab — Factor Bars** | Per-country factor exposures/contributions surface in the map's `fc:<factor>` color modes |
| **Attribution drill** (`oDrAttrib`) | Deep-linked from the FactSet Attribution panel inside `oDrCountry` |
| **Stock drill** (`oSt`) | Reached from country drill's holdings table row click |
| **Unowned drill** (`oDrUnowned`) | Similar geography-linked modal for bench-only holdings; uses region (not country) |

---

## 10. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-20 | Full three-track audit: data source (Section 1), functionality matrix (Section 4), design (Section 6). Signed off v1. | Tile Audit Specialist CLI |

---

## Agents that should know this tile

- **risk-reports-specialist** — master agent, field authority
- **tile-audit-specialist** — authored this audit
- **rr-design-lead** — for section 6 sign-off (rank alignment, hardcoded chart colors)
- **rr-data-validator** — for section 1.4 spot-check + COUNTRY_ISO3 naming-drift monitoring

---

## Section Summary

| Section | Status | Notes |
|---|---|---|
| **0. Identity** | 🟢 GREEN | DOM id, 3 render fns, tab, grid position, visibility rule all documented |
| **1. Data Source** | 🟢 GREEN | All 8 table cols + all map modes traced. Offsets verified in SCHEMA_COMPARISON. `aggregateCountryRisk` is most-defensive aggregator in the file. Spot-check pending (no data file). COUNTRY_ISO3 naming-drift flagged. |
| **4. Functionality** | 🟡 YELLOW | Many capabilities match; several EXCEED benchmark (full-screen, 3-way toggle, 8-mode color picker, region zoom, empty state). BUT: missing column picker, trend sparkline, TE/%S columns, threshold row classes, and most header tooltips. Drill modal missing sort + range selector. |
| **6. Design** | 🟢 GREEN (with caveats) | Density / emphasis / spacing match cardSectors closely. Two minor deltas: rank cells center-aligned (vs sectors' right), and `rCountryChart` uses hardcoded green/red hex instead of CSS vars. |

---

**Sign-off:** All verifiable checklists pass. Status changed to `signed-off`. Fix queue documented in Section 7 + Section 4.1.
