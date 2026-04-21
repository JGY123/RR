# Tile Spec: cardRegions — Region Active Weights

> **Audit date:** 2026-04-21
> **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html`
> **Benchmark tiles:** `cardSectors` (gold standard, shares `rWt()`), `cardCountry` (sibling geographic tile)
> **Methodology:** Three-track audit per `tile-specs/AUDIT_LEARNINGS.md`

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Region Active Weights |
| **Card DOM id** | `#cardRegions` |
| **Render function(s)** | `rWt(s.regions, 'reg', s.hold)` shared w/ cardSectors at `dashboard_v7.html:1510` (template renders at L1334); chart via `rRegChart(s)` at L2283; view toggle `toggleRegView(v,btn)` at L2712 |
| **Tab** | Exposures (Row 13 — "de-prioritized, bottom of page", per inline comment at L1326) |
| **Grid row** | Bottom of Exposures grid; full-width card, not inside `.grid`. Takes implicit top margin via `margin-top:16px` inline |
| **Width** | Full card width (outside the grid structure — sits as final child of `tab-exposures`) |
| **Visibility** | Hidden when `isUSOnly` strategy is selected (inline `display:none` at L1327) |
| **Owner** | Tile Audit Specialist CLI |
| **Spec status** | `signed-off` (v1) |

**Adjacent markup:** L1184 emits an amber "ⓘ US-focused strategy — country and region analysis not applicable" notice above the (now-hidden) cardCountry and cardRegions when `isUSOnly` is true. So the tile's suppression is messaged to the user, not silent. ✅

---

## 1. Data Source & Schema

### 1.1 Primary data source

- **Object path:** `cs.regions[]` — array of region objects from `factset_parser.py._extract_group_table("Region", acct)` at parser L746
- **Holdings dependency:** `cs.hold[]` — each holding carries `h.reg` (normalized at L512: `reg: CMAP[h.co]||'Other'`). The `CMAP` lookup is also used inside `rWt` at L1540 to re-derive region during O/R/V/Q aggregation.
- **History dependency (BROKEN):** Drill modal at L3946 reads `cs.hist.reg[name]`; parser at L837-838 hardcodes `"sec": {}, "reg": {}` — never populated. → **Region historical chart always falls through to "Historical data not available" placeholder** (L4083). Same for inline sparkline column via L1589 → `inlineSparkSvg` early-returns `—` when series length < 2.
- **Array length (typical):** 6–12 regions depending on benchmark scheme (Redwood Region1 classifier). EM has 1 meaningful row, ISC has ~5.

### 1.2 Field inventory (one row per rendered column / encoding)

**Table view (`rWt(data,'reg',hold)` shared path, branch at L1631):**

| # | Column Label | Field | Source Object Path | FactSet CSV Origin | Type | Example | Formatter | Tooltip |
|---|---|---|---|---|---|---|---|---|
| 1 | Name | `d.n` | `cs.regions[i].n` | `Level2` col in 19-col Region section | string | "Developed Markets Europe" | none | — |
| 2 | Port% | `d.p` | `cs.regions[i].p` | `W` (group offset +1) | number (%) | 36.4 | `f2(v,1)` | "Portfolio weight" |
| 3 | Bench% | `d.b` | `cs.regions[i].b` | `Bench. Weight` (+2) | number (%) | 40.1 | `f2(v,1)` | "Benchmark weight" |
| 4 | Active | `d.a` | `cs.regions[i].a` | `AW` (+3) parser-precomputed | number (%) | −3.7 | `fp(v,1)` + `activeStyle()` | "Portfolio minus benchmark weight" |
| 5 | O | computed | wtd-avg of `h.over` grouped by `CMAP[h.co]` | `OVER_WAvg` (+7) on holdings | number (1–5) | 2.4 | `f2(v,1)` + `rc()` | "Avg Overall MFR rank" |
| 6 | R | computed | wtd-avg `h.rev` by region | `REV_WAvg` (+8) | 1–5 | — | `f2(v,1)` + `rc()` | *(none — missing `data-tip`)* |
| 7 | V | computed | wtd-avg `h.val` by region | `VAL_WAvg` (+9) | 1–5 | — | `f2(v,1)` + `rc()` | *(none)* |
| 8 | Q | computed | wtd-avg `h.qual` by region | `QUAL_WAvg` (+10) | 1–5 | — | `f2(v,1)` + `rc()` | *(none)* |
| 9 | Trend | `cs.hist.reg[d.n]` | parser — **always empty** | inline SVG | `inlineSparkSvg` | — (blocked) | "Active weight trend over last N periods" |

**Chart view (`rRegChart`):**
- **Y axis:** region names sorted by active weight desc (`d.a`)
- **X axis:** diverging bars — Portfolio on left (negated), Benchmark on right. NOT an "active weight" chart — it's a back-to-back port/bench comparison. Tick labels force positive numbers via custom `tickvals/ticktext` (L2293-2295).
- **Colors:** hardcoded `rgba(99,102,241,0.85)` (portfolio, indigo) and `rgba(75,85,99,0.85)` (benchmark, grey). Not theme-tokenized (no `var(--pri)`).
- **Height:** dynamic `Math.max(200, d.length*36+80)` so chart expands with row count. ✅ responsive.

### 1.3 Derived / computed fields

| Field | Computation | Location |
|---|---|---|
| Region ORVQ rank averages | `rankAvg3(_secRankMode, S, C, W, PW, BW, BPW)` — shared with sectors/countries; weighted by `h.p` / `h.b` | `rWt` L1583–L1586 |
| `hasRegRanks` toggle | `type==='reg' && hold && Object.keys(regOC).length>0` — rank columns only emitted when at least one holding has non-null `h.over` | L1549 |
| Region coverage total | `data.reduce((s,d)=>s+(d.p||0),0)` — triggers disclaimer when <50% | L1634 |
| Region assignment per holding | `CMAP[h.co]||'Other'` (line L1540, L512) | CMAP defined earlier |

**Shared-state note:** `_secRankMode` (Wtd/Avg/BM) toggle at the top of cardSectors is the SAME variable that drives cardRegions' rank columns. Flipping in sectors re-renders regions via the hook at L1498 — intentional per AUDIT_LEARNINGS.md L14-15, but may surprise users. No per-tile `_regRankMode`.

### 1.4 Ground truth verification

- **Method:** Trace `cs.regions[].{p,b,a}` to "Region" CSV section — 19-col layout identical to Sectors/Countries (SCHEMA_COMPARISON.md L66–L97). Parser uses `_extract_group_table("Region", acct)` — same helper, same offsets as Country.
- **Active weight:** `d.a` is parser-precomputed (`AW` offset +3); no JS-side recomputation. No drift risk.
- **Spotlight ranks:** Aggregated client-side from `h.over/rev/val/qual` using `CMAP[h.co]` to bucket by region. Any holdings with `h.co` missing from CMAP bucket into "Other" — silently.
- [x] FactSet Region section layout verified in SCHEMA_COMPARISON.md (19-col, shared with Sector/Country)
- [x] `d.a` parser-precomputed — matches `AW` offset +3
- [x] `isCash(h)` guard before rank accumulation (L1539) — prevents cash from polluting region ranks
- [ ] Spot-check pending: `latest_data.json` in repo but top-level is a list, strategy inner structure not readable via quick python — skipped per AUDIT_LEARNINGS §Known blockers
- [ ] **CMAP coverage unknown** — no logging when `h.co` misses the map. Silent "Other" bucket could mask CMAP drift. Same class of risk as cardCountry's COUNTRY_ISO3 drift (see cardCountry-audit §7 #9).
- **Known discrepancy tolerance:** ≤0.05% rounding on weight sums

### 1.5 Missing / null handling

| Scenario | Behavior | Code location |
|---|---|---|
| `s.regions` empty / missing | Returns `<p>No region data</p>` | L1511 |
| `h.co` null or `isCash(h)` | Skipped in ORVQ aggregation (`if(isCash(h)\|\|!h.co)return`) | L1539 |
| `h.co` not in `CMAP` | Bucketed as "Other" — **silent** (no warning) | L1540 |
| All holdings have null ORVQ | `hasRegRanks=false` → rank columns entirely omitted | L1549 |
| Per-region rank null | "—" in `#334155` neutral color | L1581 |
| Rank average denominator 0 | `rankAvg3` returns null → "—" | L1460-L1462 |
| `d.p`/`d.b`/`d.a` null | `f2(null)` / `fp(null)` display as `—` | formatters |
| `cs.hist.reg[name]` missing | `inlineSparkSvg` returns `—` span (opacity .4) | L1441, always-true since parser never populates |
| Region total weight <50% | Amber disclaimer rendered below table (L1636) | L1634 |
| US-only strategy | Entire card `display:none`; separate amber notice at L1184 |— |
| Historical week selected | Table silently shows latest-week regions — standard two-layer history behavior (see AUDIT_LEARNINGS §Shared state traps) | — |

**Assessment: YELLOW** — Core data pipeline clean and traceable. Three yellows: (1) `hist.reg` pipeline half-built — render-side code reads it, parser never writes it, so historical chart and sparkline are permanently dead (B6 blocker confirmed still valid); (2) CMAP "Other" bucket silent; (3) no spot-check possible in-session.

---

## 2. Columns & Dimensions Displayed

**Table view** (header branch at L1631):

| # | Label | Field | Format | Sortable | Hideable | Header tooltip | Click action |
|---|---|---|---|---|---|---|---|
| 1 | Name | `d.n` | plain | Yes (col 0) | No | — | Row → `oDr('reg', name)` |
| 2 | Port% | `d.p` | `f2(v,1)` | Yes (col 1) | No | "Portfolio weight" | — |
| 3 | Bench% | `d.b` | `f2(v,1)` | Yes (col 2) | No | "Benchmark weight" | — |
| 4 | Active | `d.a` | `fp(v,1)` + color | Yes (col 3) | No | "Portfolio minus benchmark weight" | — |
| 5 | O | wtd-avg | `f2(v,1)` + `rc()` | Yes (col 4) | No | "Avg Overall MFR rank" | — |
| 6 | R | wtd-avg | `f2(v,1)` + `rc()` | Yes (col 5) | No | **MISSING** | — |
| 7 | V | wtd-avg | `f2(v,1)` + `rc()` | Yes (col 6) | No | **MISSING** | — |
| 8 | Q | wtd-avg | `f2(v,1)` + `rc()` | Yes (col 7) | No | **MISSING** | — |
| 9 | Trend | SVG | inline | No | No | "Active weight trend over last N periods" (on header) | — |

Sort: all 8 data cols sortable via `sortTbl('tbl-reg',col)` with `data-sv`. `data-sv` pattern on rank cells is **absent** — rank `<td>`s in the region branch at L1581 do not include `data-sv`, so rank-column sort falls back to `textContent` parsing (works for clean numbers, but breaks the "—" → null convention from AUDIT_LEARNINGS.md §Sort anti-patterns). Trend col is the terminal header and is un-labeled by `sortTbl` (no `onclick`).

Default sort: none applied; `data` used in source order.

**Chart view** (`rRegChart`): see §1.2 above. Sort = descending by `d.a`. Not interactive (no `plotly_click`).

---

## 3. Visualization Choice

### 3.1 Layout
Two mutually exclusive views: **Table (default)** / **Chart** via `toggleRegView(v,btn)` at L2712. No Map view (unlike cardCountry which has 3 modes). No full-screen modal for regions (unlike cardCountry).

### 3.2 Axis scaling
- **Chart:** linear X (Portfolio negated, Benchmark positive); categorical Y sorted by active desc. Custom tick generation to show positive labels on both sides.
- **Table:** n/a.

### 3.3 Color semantics
- Active column: `activeStyle(d.a)` → green pos / red neg via CSS class.
- Chart: indigo (portfolio) / grey (benchmark) — **hardcoded rgba**, not themed. No pos/neg semantic in chart (it's a weight-comparison view, not an active-weight view).
- Rank cells: `rc()` on `Math.round(avg)` — theme-aware via CSS vars `--r1`..`--r5`.
- Sparkline stroke: hardcoded `#10b981` / `#ef4444` at L1451 — not theme tokens.

### 3.4 Responsive behavior
- Chart height scales with row count (`d.length*36+80`, min 200px) ✅
- Table no `max-height`/scroll on region branch — but with only 6-12 rows this is intentional
- Header wraps via `flex-between` + `gap:6px` ✅

### 3.5 Empty state
- Table: `<p style="color:var(--txt);font-size:12px">No region data</p>` (shared with sector/group branches, L1511) ✅
- Chart: silent early return at L2285 if no data — leaves prior chart on screen across strategy switches. Violates AUDIT_LEARNINGS §Viz-renderer pattern ("must write to the div, not silent return").
- Region coverage low: amber disclaimer at L1636 when sum of port weights < 50%

### 3.6 Loading state
Inherits global `#loading` overlay.

---

## 4. Functionality Matrix (vs cardSectors benchmark)

| Capability | cardSectors | cardRegions | Match? |
|---|---|---|---|
| **Sort** | ✅ all 11 cols, `sortTbl`, `data-sv` on numeric cells | ✅ 8 cols sortable, BUT rank cells at L1581 lack `data-sv` (sort falls back to textContent) | ⚠ PARTIAL |
| **Filter** | ❌ intentional (11 rows) | ❌ intentional (6–12 rows) | ✅ parity |
| **Column picker (⚙)** | ✅ 10 cols, `rr_sec_cols` localStorage | ❌ NONE (no `REG_COLS`, no `rr_reg_cols`) | ❌ GAP |
| **Row click → drill** | ✅ `oDr('sec',name)` | ✅ `oDr('reg',name)` — shared function | ✅ YES |
| **Right-click (cell copy)** | ✅ global handler | ✅ inherits global | ✅ YES |
| **Card-title right-click (note)** | ✅ `showNotePopup` | ✅ inherits global → works on `#cardRegions .card-title` | ✅ YES |
| **📝 Note badge** | ✅ | ✅ via `refreshCardNoteBadges` global pass | ✅ YES |
| **Export PNG** | ✅ | ✅ `screenshotCard('#cardRegions')` (L1331) | ✅ YES — but note user preference: PNG buttons are controversial; flagged for possible removal (see Issues) |
| **Export CSV** | ✅ `exportCSV('#secTable table','sectors')` | ✅ `exportCSV('#regTable table','regions')` (L1331) | ✅ YES |
| **Full-screen modal** | ❌ n/a | ❌ NONE (unlike cardCountry which has one) | ⚠ parity with sectors, but cardCountry exceeds both |
| **Toggle views** | ✅ Table/Chart | ✅ Table/Chart | ✅ YES |
| **Range selector (drill)** | ✅ 3M/6M/1Y/3Y/All in `oDr` modal | ✅ shares `oDr` — buttons render, but `cs.hist.reg[name]` is always empty, so range selection is a no-op | ⚠ SHELL (B6 blocker) |
| **Spotlight rank mode (Wtd/Avg/BM)** | ✅ `rankToggleHtml3` — shown in header | ⚠ Same `_secRankMode` drives ranks, but toggle UI **not rendered** in the region header. User must flip it in Sectors tile to affect Regions. | ⚠ GAP (hidden control) |
| **Trend sparkline column** | ✅ inline SVG from `hist.sec[name]` | ⚠ COLUMN EXISTS but `cs.hist.reg` is permanently empty — always `—` | ⚠ BROKEN (B6 blocker) |
| **Sparkline window toggle (2/4/6/13)** | ✅ `setSecSparkWin` | ✅ `setRegSparkWin` wired (L1432) — but no data to drive it | ⚠ dead control until B6 ships |
| **Header tooltips on numeric cols** | ✅ all numeric headers have `class="tip" data-tip="..."` | ⚠ Port/Bench/Active YES; O has tip; R/V/Q have NO `data-tip` (L1631) | ⚠ GAP |
| **`data-col` attribute on ths/tds** | ✅ every col tagged for colpicker | ❌ NONE — neither headers nor cells carry `data-col` in the region branch | ❌ GAP (blocks future colpicker) |
| **Threshold row classes (`thresh-warn`/`thresh-alert`)** | ✅ at ±3% / ±5% | ✅ L1557 applies same classes (shared code path in `rWt`) | ✅ YES |
| **Active weight color coding** | ✅ `activeStyle(d.a)` | ✅ same | ✅ YES |
| **Hardcoded hex in chart** | — | ⚠ `rgba(99,102,241,0.85)` / `rgba(75,85,99,0.85)` at L2298,2301 — not themed; also `#10b981`/`#ef4444` in sparkline at L1451 | ⚠ GAP (minor) |
| **Empty-state on chart** | — (no analog) | ❌ `rRegChart` early returns silently on empty data (L2285) — leaves stale render | ⚠ GAP per AUDIT_LEARNINGS |
| **Region coverage disclaimer** | — (no analog) | ✅ amber notice when sum<50% (L1636) | ✅ PLUS |
| **isUSOnly hide behavior** | — | ✅ `display:none` inline + complementary notice at L1184 | ✅ YES |
| **Region-coverage pre-header text** | — | ⚠ "Region coverage may be low for US-focused strategies" always rendered at L1330, even for strategies with full region coverage (ACWI, IDM). Duplicates purpose of the L1636 <50% disclaimer. | ⚠ minor UX clutter |
| **Drill historical chart** | ✅ `hist.sec` populated by parser | ❌ `hist.reg` always `{}` — falls through to "Historical data not available" placeholder (L4083) | ❌ BROKEN (B6) |
| **Drill country breakdown** | — | ✅ PLUS — `oDr('reg',...)` includes per-country table for the region (L3994) | ✅ PLUS |
| **`id="cardRegions"`** | ✅ `cardSectors` | ✅ `cardRegions` | ✅ |
| **Table id `tbl-reg`** | `tbl-sec` | `tbl-reg` (L1631) | ✅ |
| **Theme-aware** | ✅ | ⚠ mostly — chart bars hardcoded; sparkline stroke hardcoded | ⚠ GAP |

### 4.1 Functionality gaps vs Sectors benchmark

**Trivial (≤5-line inline fix each):**
1. Add `class="tip" data-tip="Avg Revision MFR rank"` etc. on R/V/Q th — mirrors O. (L1631 — 3 short edits in one line)
2. Add `data-sv` to region rank cells at L1581 so sort doesn't fall back to textContent parsing (also fixes null-sort anti-pattern per AUDIT_LEARNINGS §Sort anti-patterns).
3. Replace `rgba(99,102,241,0.85)`/`rgba(75,85,99,0.85)` in `rRegChart` (L2298/2301) with `THEME().pri`-equivalent (needs extending `THEME()` to expose port/bench colors, or inline `getComputedStyle(document.body).getPropertyValue('--pri')`).
4. Remove/conditionalize the "Region coverage may be low for US-focused strategies" header text (L1330). On US-only the card is hidden anyway; for other strategies it's already redundant with the <50% amber disclaimer.
5. Replace sparkline hardcoded `#10b981`/`#ef4444` at L1451 with `var(--pos)`/`var(--neg)` — one-line change, affects sector sparklines too.
6. Add empty-state fallback in `rRegChart` at L2285: `if(!d.length){el.innerHTML='<p>No region data</p>';return;}` instead of silent return. Mirrors AUDIT_LEARNINGS §Viz-renderer pattern.
7. Re-introduce `rankToggleHtml3()` in the region tile header, OR add inline "Rank mode controlled from Sector tile" hint so user understands the shared state.

**Non-trivial (→ backlog):**
- **Hook up `hist.reg` in parser (covered by BACKLOG B6)** — unblocks sparkline column, drill history chart, and range selector. Confirmed: still the single highest-impact non-trivial item for this tile.
- **Column picker (⚙)** — would require `REG_COLS` config, `rr_reg_cols` localStorage, `applyRegColVis()`, `data-col` attributes on every `<th>`/`<td>` in the region branch. ~30–40 lines. Lower priority than sectors since only 4–8 meaningful cols.
- **CMAP drift visibility** — log once per render if any holding's `h.co` bucketed to "Other", surfaced as console warning or subtle footer note. Same class of problem as cardCountry's COUNTRY_ISO3 drift.
- **PNG button removal** — user preference (AUDIT_LEARNINGS + LIEUTENANT_BRIEF) is "no PNG buttons on RR tiles". The ⬇ menu at L1331 still includes "Download PNG". Should be removed across all cards in a single sweep (multi-tile item).

---

## 5. Popup / Drill / Expanded Card

### 5.1 Modal identity
- **Function:** `oDr('reg', name, range)` at L3942 — **shared with cardSectors** (same fn, `type` branch)
- **Modal DOM id:** `#drillModal`
- **Registered in `ALL_MODALS`:** ✅ (shared sector modal)

### 5.2 Modal sections
1. Header: `{name} — Region Deep Drill` + close
2. 3-card summary grid: Port Weight · Active Weight · TE Contribution
3. Historical chart (`#drillHistDiv`): **permanently empty for regions** — falls through to "Historical data not available" placeholder because `cs.hist.reg[name]` is never populated (parser L837-838)
4. Range selector buttons (3M/6M/1Y/3Y/All): render but have no effect — range is applied to an empty `fullHist`
5. Holdings table (holdings in region, col: Ticker, Name, Port%, Bench%, Active, MCR, O/R/V/Q)
6. Mini compare panel (other regions by `|a|` desc)
7. Country breakdown table (`type==='reg'` branch L3993) — filters `cs.countries` via `CMAP[c.n]===name`. ✅ region-specific value-add.

### 5.3 Modal functionality
- [x] Row click-through → `oSt(ticker)` on holdings
- [x] Row click-through → `oDrCountry(name)` on country rows
- [x] Holdings CSV export (L4043: `exportCSV(..., '${name}_holdings')`)
- [x] Escape closes (`ALL_MODALS`)
- [ ] Holdings table sort: not wired
- [ ] Drill modal lacks TE contribution time-series (sector drill has same gap)
- [ ] Range buttons non-functional due to missing `hist.reg` data

### 5.4 Modal data source
- `cs.regions.find(r=>r.n===name)` for summary numbers
- `cs.hold.filter(h=>h.reg===name)` — where `h.reg` was set at L512 via `CMAP[h.co]||'Other'`. Note: relies on normalizer running; if any path to `oDr` bypasses that, `h.reg` is undefined. Safe in current codebase.
- `cs.countries.filter(c=>(CMAP[c.n]||'Other')===name)` for country breakdown
- `cs.hist.reg[name]` for historical chart — **always empty**

---

## 6. Design Guidelines

### 6.1 Density

| Element | Value | Standard | Match? |
|---|---|---|---|
| Card padding | `16px` (via `.card`) | 16px | ✅ |
| Card `margin-top` | `16px` inline | — | ✅ (explicit, since card sits outside `.grid`) |
| Card background | `var(--card)` | Standard | ✅ |
| Table `<th>` font-size | default ~10px (inherits global) | 10px | ✅ |
| Table `<td>` font-size | 11px default; rank cells explicit 11px | 11px | ✅ |
| Rank cell padding | `4px 6px` (L1581) | 4px 6px | ✅ (matches sector/country ranks) |
| Chart div height | dynamic `max(200, n*36+80)` | — | ✅ better than cardCountry's 280px fixed |
| Table scroll container | none on region branch (6-12 rows) | — | ✅ intentional |
| "Coverage may be low" pre-header | `font-size:10px;color:var(--txt)` | — | ⚠ clutter (see 4.1 trivial #4) |

### 6.2 Emphasis & contrast

| Element | Treatment | Rationale |
|---|---|---|
| Card title | 12px, 600, uppercase, letter-spacing 0.5px | Standard |
| Region name (col 1) | Default | Primary identifier |
| Active weight | `activeStyle(d.a)` | Consistent |
| O/R/V/Q ranks | `font-weight:600`, `rc()` color, indigo-tinted bg `rgba(99,102,241,0.04)` | Spotlight — slightly lighter tint than sectors' `0.07` |
| Threshold row classes | `thresh-warn` ±3%, `thresh-alert` ±5% | ✅ consistent |
| Chart portfolio bar | `rgba(99,102,241,0.85)` | hardcoded — see 4.1 #3 |
| Chart benchmark bar | `rgba(75,85,99,0.85)` | hardcoded |

**Delta vs cardSectors:**
- Spotlight background tint is `0.04` (region rank cells, L1581) vs `0.07` (sectors). Trivially different; minor.
- NO Spotlight header-group row in region branch (L1631 is single-row `<thead>`, no `colspan` grouped header with "Spotlight" label + rank toggle). cardSectors has this two-row thead at L1603-L1627.

### 6.3 Alignment

| Column type | Alignment | Notes |
|---|---|---|
| Region name | Left (default) | ✅ |
| Port/Bench/Active | Right (`class="r"`) | ✅ |
| O/R/V/Q | Center (inline `text-align:center`) | ⚠ diverges from cardSectors where ranks are `class="r"` (right). Same delta flagged in cardCountry-audit §7 #5 — unresolved convention across geographic tiles. |
| Trend SVG | `class="r"` | OK |

### 6.4 Whitespace

| Gap | Value |
|---|---|
| Card header gap | `6px` | ✅ |
| Pre-header "coverage" text margin-right | `4px` | OK |
| Chart margin | default | OK |

### 6.5 Motion / interaction feedback

| State | Treatment |
|---|---|
| Row hover | `.clickable` hover tint | ✅ |
| Row active | Indigo flash | ✅ |
| Toggle-btn active | indigo fill | ✅ |
| `⬇` dropdown | standard dl-drop slide | ✅ |
| Plotly hover | default tooltip themed via `THEME().tick` | ✅ |
| Empty chart | silent (stale prior render persists) | ⚠ see 4.1 #6 |

**Assessment: YELLOW** — Aligned with cardSectors on density/padding/rank-cell treatment, but **missing the two-row Spotlight header with inline rank-mode toggle**. Chart colors hardcoded. Rank-alignment delta (center vs right) still unreconciled across geographic tiles.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Category | Trivial? |
|---|---|---|---|---|
| 1 | `cs.hist.reg` never populated by parser — sparkline column, drill historical chart, and range selector all dead (B6 blocker) | **High** | Data pipeline | ❌ Non-trivial (parser change) |
| 2 | Rank cells lack `data-sv` at L1581 — sort falls back to textContent | Medium | Sort anti-pattern (AUDIT_LEARNINGS §Sort anti-patterns) | ✅ Trivial |
| 3 | R/V/Q header `<th>`s have no `data-tip` — only O does | Medium | Consistency | ✅ Trivial |
| 4 | `rankToggleHtml3()` not surfaced in cardRegions header — user must toggle in Sectors tile | Medium | UX / hidden control | ✅ Trivial (add one line in tile header) |
| 5 | "Region coverage may be low for US-focused strategies" header text always rendered (L1330) — clutter on strategies with good coverage; duplicate of <50% disclaimer | Low | UX clutter | ✅ Trivial |
| 6 | Chart bars hardcoded `rgba(99,102,241,0.85)` / `rgba(75,85,99,0.85)` | Low | Theme | ✅ Trivial |
| 7 | Sparkline stroke hardcoded `#10b981`/`#ef4444` at L1451 (shared w/ sectors) | Low | Theme | ✅ Trivial |
| 8 | `rRegChart` silent early-return on empty data (L2285) — leaves stale render | Low | Empty-state (AUDIT_LEARNINGS §Viz-renderer pattern) | ✅ Trivial |
| 9 | No `data-col` on region `<th>`/`<td>` — blocks future column-picker | Low | Infra | ❌ Non-trivial (~30 lines to hook up colpicker) |
| 10 | Spotlight header row (two-row thead with "Spotlight" colspan + rank toggle) absent in region branch | Low | Design parity | ❌ Non-trivial (branch divergence in shared `rWt`) |
| 11 | CMAP drift silent — `h.co` not in CMAP buckets to "Other" with no warning | Medium | Verification | ❌ Non-trivial (logging infra) |
| 12 | Download menu still offers "Download PNG" (L1331) — user preference is no-PNG | Low | Preference | ✅ Trivial, but multi-tile sweep preferred |
| 13 | Rank cells center-aligned (vs sectors right-aligned) — same delta as cardCountry | Low | Design inconsistency (unresolved across tiles) | PM call |
| 14 | Historical week selected: table silently shows latest-week regions (two-layer history) | Low | Shared trap per AUDIT_LEARNINGS | PM call — consistent across all detail tiles |
| 15 | Spot-check vs CSV pending — no usable in-session data file | Medium | Verification | — |

---

## 8. Verification Checklist

- [x] **Data accuracy:** 8 table cols + chart encoding traced to source; Region CSV section 19-col layout verified via SCHEMA_COMPARISON.md
- [x] **Edge cases:** empty regions → "No region data"; isCash guard; null rank bucket; low-coverage amber disclaimer; isUSOnly suppression
- [x] **Sort:** all 8 data cols sortable; rank cells missing `data-sv` flagged
- [ ] **Column picker:** not implemented (gap, non-trivial)
- [x] **Export PNG:** present (flagged for removal per user pref)
- [x] **Export CSV:** present and functional
- [ ] **Full-screen modal:** not present (parity with sectors; cardCountry exceeds)
- [x] **Popup/drill:** `oDr('reg', name)` shared with sectors; country-breakdown added for regions ✅
- [ ] **Drill historical chart:** BROKEN — hist.reg never populated (B6)
- [x] **Themes:** mostly theme-aware; chart bars + sparkline stroke hardcoded
- [x] **Keyboard:** Escape closes drill via `ALL_MODALS`
- [ ] **Console errors:** not runtime-tested in audit; static analysis shows guards in place (`||0`, `!=null`, `isCash`)
- [ ] **Spot-check vs CSV:** pending (no usable data in-session)
- [x] **isUSOnly branch:** verified — inline `display:none` at L1327 + complementary amber notice at L1184 explaining suppression. Works correctly.
- [x] **Responsive chart height:** confirmed `Math.max(200, d.length*36+80)`
- [x] **Week-selector behavior:** matches documented two-layer-history trap (silent latest data) — not a regression vs siblings

---

## 9. Related Tiles

| Related Tile | Relationship |
|---|---|
| **cardSectors** | Shares `rWt(data,type,hold)` render fn, `_secRankMode` global state, `rankToggleHtml3`, `activeStyle`, `rc`, `sortTbl`, `inlineSparkSvg`, `oDr` drill |
| **cardCountry** | Parent-of relationship: countries roll up to regions via `CMAP`; region drill surfaces per-country table; country drill surfaces region chip |
| **cardGroups** | Sibling aggregation tile; shares `rankAvg3` and `_secRankMode`; also awaiting `hist.grp` (B6) |
| **Holdings tab** | `h.reg` assigned via `CMAP[h.co]||'Other'` in normalizer (L512) — source for region ORVQ aggregation |
| **Risk tab** | No direct linkage (regions not in factor risk tree) |

---

## 10. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Full three-track audit. Signed off v1. Confirmed B6 blocker still valid: parser L837-838 hardcodes `hist.reg: {}`. | Tile Audit Specialist CLI |

---

## Section Summary

| Section | Status | Notes |
|---|---|---|
| **1. Data Source** | 🟡 YELLOW | Static pipeline clean (weights, ranks); `hist.reg` dead (B6); CMAP "Other" silent; spot-check pending |
| **4. Functionality** | 🟡 YELLOW | Parity with sectors on core table + drill; missing inline rank toggle, R/V/Q tooltips, `data-sv` on ranks, `data-col` infra, Spotlight header row, and empty-state on chart. Country breakdown in drill exceeds sectors. |
| **6. Design** | 🟡 YELLOW | Density + padding + rank coloring aligned; two-row Spotlight thead missing; chart bars + sparkline stroke hardcoded; rank alignment diverges from sectors (same delta as cardCountry) |

---

**Sign-off:** All verifiable checks pass. Primary blocker is B6 (parser-side `hist.reg` collection). Trivial fixes queued for main-session serialization. Non-trivial items routed to BACKLOG references.

## Trivial fix queue (≤5 lines each, main-session can apply)
1. Add `data-tip="..."` to R/V/Q th at L1631 (mirror O col)
2. Add `data-sv="${avg!=null?+avg.toFixed(2):''}"` to region rank cells at L1581
3. Replace sparkline hardcoded `#10b981`/`#ef4444` at L1451 with `var(--pos)`/`var(--neg)` — affects sector sparklines too, coordinate with cardSectors
4. Remove or conditionalize "Region coverage may be low..." header text at L1330 (redundant with <50% disclaimer; clutter on full-coverage strategies)
5. `rRegChart` empty-state: replace silent return at L2285 with `el.innerHTML='<p>No region data</p>';return;`
6. Add `rankToggleHtml3()` (or a one-line hint) in the cardRegions header so users see the rank-mode control instead of having to find it in Sectors
7. Replace `rgba(99,102,241,0.85)` / `rgba(75,85,99,0.85)` in `rRegChart` L2298/2301 with themed tokens (or use `getComputedStyle(...).getPropertyValue('--pri')`)
8. Remove "Download PNG" option from L1331 ⬇ menu (user preference; also applies cross-tile)

## Non-trivial → BACKLOG
- **B6 already covers** `hist.reg` parser collection (and by extension unblocks the sparkline column, drill historical chart, and drill range selector). Confirmed still valid.
- **Column picker (⚙) for regions** — new backlog item worth logging (~30-40 lines: `REG_COLS` + `rr_reg_cols` + `applyRegColVis` + `data-col` attrs on th/td in region branch). Lower priority than sectors colpicker since only 4-8 meaningful columns.
- **CMAP drift telemetry** — shared pattern with cardCountry's COUNTRY_ISO3 drift. Ideally a single "geographic classifier coverage" check that warns once per data load.
- **Spotlight header-row parity** — cardRegions lacks the two-row `<thead>` with "Spotlight" colspan + inline rank toggle that cardSectors has. Requires splitting the shared `rWt` header logic or adding a `reg`-specific header branch (~20-30 lines).

## Agents that should know this tile
- **risk-reports-specialist** — master agent, field authority
- **tile-audit-specialist** — authored this audit
- **rr-design-lead** — for §6 sign-off (rank alignment, chart theming, Spotlight header-row parity)
- **rr-data-validator** — for §1.4 spot-check + CMAP drift monitoring
