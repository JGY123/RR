# Tile Spec: cardFacDetail — Audit v1

> **Audited:** 2026-04-21 | **Auditor:** Tile Audit Specialist (CLI)
> **Status:** 🟡 signed-off with open items (theme-violating pill colors, shared-state drift, primary-filter heuristic)

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Detail |
| **Card DOM id** | `#cardFacDetail` |
| **Render function(s)** | `rFac(s.factors, s.hold)` at `dashboard_v7.html:L1717–L1720`; inner table `rFacTable(factors,hold)` at `L1722–L1787`; row renderer `facRow(f)` at `L1743–L1775` |
| **Render target** | `<div id="tbl-fac-wrap">…<table id="tbl-fac">…</table></div>` injected at card position by `${rFac(s.factors,s.hold)}` on L1174 |
| **Companion state** | `_facView` ('primary'\|'all') L1657; `_facHighlight` L1658; `_facColVis` (localStorage `rr_fac_cols`) L1659–L1663 |
| **Companion fns** | `setFacView` L1675, `setFacHighlight` L1685, `applyFacHighlight` L1694, `facColDropHtml` L1706, `facGroupPillsHtml` L1710, `toggleFacCol`+`applyFacColVis` L1664–L1674 |
| **Tab** | Factors (`tab-factors`) |
| **Grid row** | Row 3 of Factors tab, right half of `grid g2` (pairs with sibling `cardFacButt` on the left) |
| **Width** | Half (`g2` cell) |
| **Full-screen path** | `openFullScreen('facmap')` at L5496 → renders `renderFsFactorMap` scatter (owned by this card's ⛶ button on L1164) |
| **Owner** | CoS / Tile Audit Specialist |
| **Spec status** | `signed-off-with-followups` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** `s.factors[]` (same array as sibling `cardFacButt`), built by `_build_factor_list` in `factset_parser.py:L847–L865`.
- **Auxiliary:** `s.hold[]` is passed in but unused by `rFacTable` (it's still in the signature — historical cruft, see §7 #12).
- **History:** `cs.hist.fac[factorName]` → `[{d, e, bm}, …]` drives the 12-week sparkline and the prior-period Profitability warning.
- **Typical row count:** ~7 in Primary view (`FAC_PRIMARY` set at L1644), ~20–40 in All view depending on risk model.

### 1.2 Field inventory (columns)

| # | Column | data-col | Field | Type | Formatter | Sort wired? | data-sv set? |
|---|---|---|---|---|---|---|---|
| 0 | Factor | `name` | `f.n` | string | raw | ✅ `sortTbl('tbl-fac',0)` | ❌ no data-sv (fine — name is textContent) |
| 1 | Exposure | `exp` | `f.a` | number (σ) | `fp(f.a,2)` + diverging-bar bg | ✅ (col 1) | ✅ `data-sv="${expVal}"` where `expVal = f.a ?? 0` |
| 2 | TE% | `te` | `f.c` | number (%) | `f2(f.c,1) + '%'` | ✅ (col 2) | ✅ `data-sv="${f.c??0}"` |
| 3 | 12wk | `spark` | `cs.hist.fac[f.n]` last-12 active | svg (via `mkSparkline`) | 48×18 svg | ⚠️ sort wired to col 3 but cell has no numeric `data-sv` — sort collapses all rows | ❌ |
| 4 | Return | `ret` | `f.ret` | number (%) | `fp(f.ret,2)` | ✅ (col 4) | ✅ `data-sv="${f.ret??0}"` |
| 5 | Impact | `imp` | `f.imp` | number (%) | `fp(f.imp,2)` | ✅ (col 5) | ✅ `data-sv="${f.imp??0}"` |

### 1.3 Derived / computed fields

| Field | Computation | Location | Notes |
|---|---|---|---|
| `maxExp` | `Math.max(...factors.map(f=>Math.abs(f.a||0)), 0.01)` | L1730 | Uses the **full factor list** (including the hidden ones in Primary view) to fix the bar scale — so Primary-mode bars stay proportionate to the All-mode view. Good. |
| `pct` | `round((|expVal|/maxExp)*45)` | L1748 | Max 45% fill-width, keeps exposure text readable |
| `barBg` | CSS `linear-gradient` diverging from 50% (center) | L1749–L1751 | **Hardcoded hex**: positive = `rgba(99,102,241,0.22)` (indigo), negative = `rgba(245,158,11,0.22)` (amber). Different palette from sibling `cardFacButt` (indigo/violet) and from dashboard green/red norm. |
| `expColor` | Sign-based (normal) or inverted (Profitability) | L1753–L1755 | Uses `var(--pos)` / `var(--neg)` — ✅ theme-aware here. |
| `rowBase` | Amber left-border + rgba tint when Profitability | L1756 | `#fb923c` hardcoded. |
| `profWarn` | ⚠ badge if `priorExpMap['Profitability'] < -0.05` | L1758–L1761 | Threshold is baked; not in `_thresholds`. |
| `priorExpMap[name]` | Current-week active minus prior-week active from `cs.hist.fac` | L1733–L1741 | Computed for every factor but only consulted for Profitability. Minor wasted work. |
| `sparkVals` | `hist.slice(-12).map(h => h.bm!=null ? +(h.e-h.bm).toFixed(4) : (h.e||0))` | L1764 | Falls back to raw `e` when no benchmark — silently conflates "active exposure history" with "raw exposure history". |

### 1.4 Ground truth verification

- [x] Field path traced — `f.n`, `f.a`, `f.c`, `f.ret`, `f.imp` all populated by `_build_factor_list` per parser.
- [x] `FAC_PRIMARY` set (L1644) matches `FACTOR_GROUPS` authority in `risk-reports-specialist.md`.
- [x] `FAC_GROUP_DEFS` ⟷ `facGrpColor()` are **two different factor-group schemes** coexisting in the same file — see §3.3 and §7 #3. Both are referenced, neither has been canonicalized.
- [ ] Spot-check against raw CSV: pending loaded JSON (AUDIT_LEARNINGS §Known blockers).

### 1.5 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `s.factors` absent / empty | `rFac` returns `<p>No factor data</p>` wrapped in `#tbl-fac-wrap` | ✅ Empty-state guard present; preserves the wrap id so `setFacView` reruns cleanly. |
| `f.a` null | `data-sv="${f.a??0}"` and `expVal = f.a ?? 0` — null treated as zero. | 🟡 Same AUDIT_LEARNINGS anti-pattern (§Sort anti-patterns): nulls sort alongside real zeros. |
| `f.c` / `f.ret` / `f.imp` null | `data-sv="${x??0}"`, display formatter `fp`/`f2` emits `—` | 🟡 Sort collapses null and zero. |
| `f.a === NaN` or `Infinity` | No `isFinite` guard. `maxExp` comparison could become NaN; gradient string would contain `NaN%`. | 🟡 Lesson Patch 003 not applied. |
| 12wk sparkline with <2 valid points | `mkSparkline` returns an em-dash span (L3369–L3371) | ✅ |
| `cs.hist` absent | `sparkVals = []` → `spark = ''` (no cell content) | ✅ |
| `priorExpMap` missing Profitability | `profWarn=''` | ✅ |
| `_facView==='primary'` when no primary factors match | visible rows = []; empty `<tbody>` (no inline "no primary factors" message) | 🟡 User sees a headers-only table. |
| `f.n` contains single quote (e.g. `"Investors' Confidence"`) | escaped via `.replace(/'/g,"\\'")` into the `onclick` attr | ✅ |
| `f.n` contains double quote | escaped via `.replace(/"/g,'&quot;')` into `data-fac` | ✅ |

**Section 1 verdict: 🟢-🟡 YELLOW-GREEN** — empty-state guard correct, quote-escaping thorough, ranges scaled sensibly. Knocked down by the persistent `??0` null-coercion pattern, missing `isFinite` guard, and no data-sv on the sparkline column (breaks column-3 sort).

---

## 2. Columns & Dimensions Displayed

Table with 6 columns, fixed widths via `<colgroup>` (L1786): name=140min, exp=90, te=60, spark=60, ret=70, imp=70. Row is clickable — drills to `oDrF(f.n)` at L4091. The first column carries a semantic span for Profitability (colored bold + ✦ + optional ⚠).

**Column-visibility picker (⚙):** all columns except `name` are toggleable; preference persists in `localStorage['rr_fac_cols']`. `applyFacColVis` hides via `display:none` on `[data-col="id"]`. Toggle persists across week changes, view toggles, strategy switches. ✅

**Factor-group highlight pills:** 4 pills (`fgp-vg`, `fgp-mb`, `fgp-pf`, `fgp-sec`) toggle row opacity (0.3 / 1.0) without filtering. Click-same-pill clears. ✅ Good UX affordance; doesn't destroy data visibility.

---

## 3. Visualization Choice

### 3.1 Chart / layout type
Table with in-cell diverging bars (background gradient) on the Exposure column. Not Plotly. Sparklines are inline SVG via `mkSparkline` helper (shared with sector/region trend spark columns, per `_secSparkWin` infrastructure).

### 3.2 Row ordering
`rFacTable` pre-sorts by `Math.abs(f.c||0)` desc (L1724) — highest TE contributor on top. User can re-sort by any column via `sortTbl`. No persistence of user sort order; toggling Primary/All snaps back to abs-TE ordering.

### 3.3 Color semantics — **three competing schemes in the same file**

| Scheme | Where | Colors |
|---|---|---|
| **A. Exposure bar (in-cell, this tile)** | `facRow` L1749–L1751 | Positive = indigo rgba(99,102,241); Negative = amber rgba(245,158,11) |
| **B. Sibling cardFacButt Plotly bars** | `rFacButt` L2320 area | Positive = indigo #6366f1; Negative = violet #a78bfa |
| **C. `facGrpColor()` (full-screen scatter)** | L5481–L5494 | Value=amber, Growth=green, Momentum=green, Volatility=red, Market=indigo, Profitability=purple |
| **D. `FAC_GROUP_DEFS` (this card's pills)** | L1647–L1652 | Value·Growth=indigo, Market Behavior=purple, Profitability=orange, Secondary=theme tick |

So within the Factors tab, "Growth" is simultaneously **green** (full-screen scatter) and **indigo** (cardFacDetail pills), and active-positive exposure is both **indigo** (this card) and **indigo** (cardFacButt bars) — but active-negative is **amber** here and **violet** next door. This is a cross-tile design debt item (see AUDIT_LEARNINGS append).

### 3.4 Profitability special treatment
- Reverse-color interpretation (L1753–L1755): positive active exposure is *desired*, so positive = green, negative = red. Note on `data-tip`: "Intentional exposure — higher profitability is desired." ✅ Correct semantic flip.
- ✦ marker on the name, left-border amber, row-bg rgba(251,146,60,0.06), ⚠ if `priorExpMap['Profitability'] < -0.05`. All hardcoded hex `#fb923c`.
- This is the only factor with hand-coded semantic override. Consider generalizing if/when the PM flags another "intentional" factor.

### 3.5 Responsive behavior
- Table is inside the card; card obeys grid reflow. No horizontal scroll on narrow viewports — fixed col widths total ~490px, fits in half-width grid cell comfortably.
- Sparkline column is 60px; sparklines render at 48×18. Adequate.
- No mobile fallback.

### 3.6 Empty state
- Missing `factors`: `<p>No factor data</p>` wrapped in `#tbl-fac-wrap` (L1718 and L1723). ✅
- Missing Primary rows after filter: visible rows = [], empty tbody — **no "no primary factors" sub-message**. See §7 #5.

### 3.7 Loading state
None; synchronous render.

---

## 4. Functionality Matrix

**Benchmark tiles:** cardSectors (gold-standard table), cardHoldings (gold-standard drill), sibling cardFacButt (same data source).

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort (column click)** | ✅ | `sortTbl('tbl-fac', N)` on every `<th>` | Column 3 (12wk sparkline) sort is effectively no-op — cells have no `data-sv`. |
| **Filter — Primary/All toggle** | ✅ | `setFacView('primary'\|'all')` L1675 | Filters by `FAC_PRIMARY` OR `/momentum/i` regex — the `/momentum/i` catch picks up e.g. "Momentum (Medium-Term)" but also any factor name containing "momentum" string. Fragile. |
| **Filter — group highlight pills** | ✅ | `setFacHighlight(gid)` L1685 | Opacity-based highlight, not a true filter. Re-click clears. |
| **Column picker** | ✅ | `facColDropHtml()` L1706, persisted to `rr_fac_cols` | 5 columns toggleable; `name` is always visible. |
| **Row click → drill** | ✅ | `onclick="oDrF('${nm}')"` on every `<tr>` | Drills into `oDrF(name)` at L4091 — factor time-series + top/bottom holdings. |
| **Cell value click** | ❌ | — | No per-cell handlers. |
| **Right-click context menu (cell value)** | 🟡 | global handler | Inherited. |
| **Card-title right-click → note** | ❌ | — | Card title has `class="tip" data-tip="…"` but **no `oncontextmenu="showNotePopup(event,'cardFacDetail')"`**. Sibling `cardFacButt` got the same gap in its audit; cardSectors/cardHoldings do have it. |
| **📝 Note badge** | ❌ | — | No integration with `refreshCardNoteBadges`. |
| **Export PNG** | ✅ (in dropdown) | `screenshotCard('#cardFacDetail')` L1166 | Against LIEUTENANT_BRIEF §3 no-PNG rule. Cleanup-sweep item, not this audit's job. |
| **Export CSV** | ✅ | `exportCSV('#cardFacDetail table','factors')` L1166 | Uses table — should correctly emit visible rows only (Primary/All state respected). Verify behavior if `display:none` columns should be included. Not tested here. |
| **Full-screen modal (⛶)** | ✅ | `openFullScreen('facmap')` L1164 | Opens `renderFsFactorMap` scatter — **owned by this card** (sibling cardFacButt has no ⛶). |
| **Toggle views** | ✅ (Primary/All) | L1167–L1170 | Two-state toggle; no Chart/Table view (not needed — this is the table half). |
| **Range selector** | N/A | — | Not a time-series tile. Drill modal has range buttons. |
| **Color-mode picker** | ❌ | — | No option to color by factor group (like `facGrpColor`) instead of sign. Low-value. |
| **Hover tooltip (header)** | ✅ | `class="tip" data-tip="…"` | Headers: Exposure, TE%, Return, Impact tooltip'd. Missing on Factor (col 0) and 12wk (col 3). |
| **Hover tooltip (row / cell)** | 🟡 | Profitability only | Only the Profitability name cell has a `data-tip` (L1762). No exposure-value tooltip elsewhere. |
| **Theme-aware (text/bg/pos/neg)** | 🟡 Partial | `var(--pos)`, `var(--neg)`, `var(--txt)` used for text | Exposure-bar backgrounds `rgba(99,102,241,.22)` / `rgba(245,158,11,.22)` and Profitability row `rgba(251,146,60,.06)` / `#fb923c` are hardcoded. |
| **Theme-aware (pills)** | ❌ | `.fgp` CSS L168–L171 | Pill active color is `#6366f1` hardcoded; `.prof.active` is `#fb923c` hardcoded. Secondary pill uses `get color(){return THEME().tick}` inline but the active-state CSS overrides it. |
| **Color-blind safe** | ❌ | no `_prefs.cbSafe` wiring | — |
| **Week-selector awareness** | ✅ (partial via re-render) | `setFacView` reads `cs.factors` (latest, not historical) | When `_selectedWeek` is set, cs.factors still reflects the latest week (factor detail is not in `hist.summary`). Consistent with sibling tiles — this is a known dashboard-wide limitation. Banner already warns the user; no action needed here. |

### 4.1 Functionality gaps vs benchmarks

| Gap | Severity | Recommendation | Class |
|---|---|---|---|
| Column 3 (sparkline) sort is broken (no data-sv) | **Medium** | Either remove `onclick` from the 12wk `<th>` (simpler) or add `data-sv` = latest active value to each cell. 2–3 line fix. | Trivial |
| Card-title no `oncontextmenu` for notes | Low | Add `oncontextmenu="showNotePopup(event,'cardFacDetail');return false"` on the `card-title` div. Mirrors cardSectors/cardHoldings. 1-line fix. | Trivial |
| `data-sv="${x??0}"` null-coercion on exp/te/ret/imp | Medium | Change to `"${x??''}"` so nulls sort as empty strings (not zeros). 4 occurrences. AUDIT_LEARNINGS §Sort anti-patterns. | Trivial |
| No `isFinite` guard on `f.a` before using in `maxExp` / `pct` | Low | Filter `factors` in `rFacTable` to `isFinite(f.a)` rows; or coerce to 0 only inside the bar calc. Trivial. | Trivial |
| No "No primary factors" sub-message when Primary view is empty | Low | `if(!visible.length) return '<p style="color:var(--txt);font-size:12px">No primary factors in view — try All</p>';` Trivial. | Trivial |
| Hardcoded bar bg `rgba(99,102,241,.22)` / `rgba(245,158,11,.22)` | Medium | Replace with `rgba(var(--pos-rgb),.22)` / `rgba(var(--neg-rgb),.22)` or an CSS var `--pos-bg` / `--neg-bg`. Requires small CSS additions. | Trivial (≤5 lines) |
| Hardcoded Profitability hex `#fb923c` (×3) + `rgba(251,146,60,.06)` | Low | Either introduce `--prof` CSS var (if Profitability is special-cased long-term) or align to `var(--warn)` / `var(--pri)`. 3–4 replacements. | Trivial |
| Pill active colors `.fgp.active` `#6366f1` / `.fgp.prof.active` `#fb923c` hardcoded in CSS | Low | Replace with `var(--pri)` / `var(--warn)` (or a dedicated `--prof`). 2-line CSS change. | Trivial |
| `FAC_GROUP_DEFS` pill palette vs `facGrpColor()` vs exposure-bar palette — three schemes | Medium | Canonicalize one factor-group palette and derive the pill, scatter, and bar colors from it. Likely needs PM consult. | Non-trivial |
| `FAC_PRIMARY` uses `/momentum/i` regex catch-all | Low | Consider explicit enumeration. If a future factor ships "Momentum Composite" we may inadvertently auto-include it. PM call. | Non-trivial |
| `hold` param passed to `rFac`/`rFacTable` but unused | Trivial (cleanup) | Drop the unused param, or document why it's there. 1-line fix. | Trivial |
| Primary/All toggle on this card does NOT flow to sibling cardFacButt | Open question | Noted in cardFacButt audit §7 #9. If harmonized, `setFacView` should also trigger `rFacButt(cs)` re-render. ~2 lines. PM decision. | Non-trivial |
| `priorExpMap` computed for every factor but used only for Profitability | Trivial (perf) | Scope to `{Profitability: …}` only. Negligible cost in practice. | Trivial (optional) |
| CSV export includes hidden columns? | Unclear | Depends on `exportCSV`'s DOM walker — needs verification. Not audited. | Follow-up |
| PNG button present | Cleanup | Out of scope — global sweep item per LIEUTENANT_BRIEF §3. | — |

**Section 4 verdict: 🟢 GREEN-YELLOW** — this is the most feature-complete tile of the Factors row: sort, filter (Primary/All), column picker with persistence, highlight pills, CSV, row-drill, full-screen all wired. Knocked to YELLOW by (a) the col-3 sort being silently broken, (b) the hardcoded-hex theme violations, (c) the note-popup gap. All are trivial.

---

## 5. Popup / Drill / Expanded Card

### 5.1 Drill path
- Every row: `onclick="oDrF('${nm}')"` → `oDrF(name, range)` at L4091.
- Renders a modal with factor time series, top-5 / bottom-5 holdings by sub-factor rank, range buttons.
- Uses `cs.hist.fac[name]` + `cs.factors.find(f=>f.n===name)` + `cs.hold` — all standard cs data.
- Range default: `_facDrillRange` (persisted? no — in-memory only).

### 5.2 Full-screen path
- ⛶ button → `openFullScreen('facmap')` → `renderFsFactorMap` scatter (L5513+). Not the same view as this card, but complementary.

### 5.3 Missing mirror functionality
- Drill modal is reachable; nothing structural missing.
- Note-popup right-click is not wired to the card title (§4).

**Section 5 verdict: 🟢 GREEN.**

---

## 6. Design Guidelines

### 6.1 Density

| Dimension | Value | Notes |
|---|---|---|
| `<th>` font-size | inherit (~10px per global) | ✅ matches gold-standard |
| `<td>` font-size | inherit (~11px) | ✅ |
| Row height | ~22–24px (default .card tr spacing) | ✅ dense, matches cardSectors/cardHoldings |
| colgroup widths | 140/90/60/60/70/70 | ✅ explicit widths prevent jitter on re-render |
| Header clickable cursor | `cursor:pointer` via `th[onclick]` CSS (L161) | ✅ |

### 6.2 Emphasis & contrast

- Exposure cell: bar gradient + colored bold text (`font-weight:600`). Signal clear.
- Return / Impact: color-coded pos/neg via `var(--pos)`/`var(--neg)`. ✅
- Profitability row: amber left-border + tint + ✦ + optional ⚠. Obvious without being loud.
- Highlight pills: opacity-fade non-matching rows to 0.3 — good affordance for group inspection without destroying context.
- 12wk sparkline: trend-colored line (or amber override for Profitability). ✅

### 6.3 Alignment

- Name col: left ✅
- All numeric cols: right (`class="r"`) ✅
- Sparkline col: right-aligned container, SVG `vertical-align:middle` ✅
- Headers match cell alignment ✅

### 6.4 Whitespace

- Card flex-between header, 6px gap in toolbar, 8px bottom margin before pills row, 6px flex-wrap on pills. ✅
- No visible cramping.

### 6.5 Motion / interaction feedback

- Row: `cursor:pointer` via inline `style="…;cursor:pointer"`. ✅
- Hover highlight: inherited from global row striping — no dedicated `:hover` state. Consistent with cardSectors. ✅
- Pill: `.fgp:hover { border-color:var(--pri); color:var(--txth) }` L169. ✅
- Column-picker ⚙ button: same `.export-btn` styling as ⬇. ✅

### 6.6 Cross-tile design debts surfaced here

- **Three factor-group color schemes coexist** (§3.3). Pick one.
- **Pill active colors are pure CSS hex**, not theme vars — same class of issue as sibling cardFacButt's bar hex. This is a factor-row-wide theming gap.
- **Profitability amber** is coded in at least 5 places (`rowBase` L1756, `profWarn` L1760, pill `.prof.active` L171, `FAC_GROUP_DEFS.pf.color` L1650, sparkline override L1765). Consolidate into one CSS var.

**Section 6 verdict: 🟡 YELLOW** — structurally clean and internally consistent, but the palette isn't theme-aware and Profitability styling is scattered.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Class | Resolution path |
|---|---|---|---|---|
| 1 | 12wk column sort broken — cells have no `data-sv`, header has `onclick` | Medium | Trivial | Remove `onclick` from col-3 `<th>` OR add `data-sv` = latest active value per cell |
| 2 | `data-sv="${x??0}"` null-coercion on exp/te/ret/imp | Medium | Trivial | Switch to `??''` per AUDIT_LEARNINGS §Sort anti-patterns |
| 3 | Three factor-group color schemes coexist (FAC_GROUP_DEFS vs facGrpColor vs exposure-bar) | Medium | Non-trivial | Canonicalize to one palette. PM decision. |
| 4 | Card title has no `oncontextmenu="showNotePopup"` | Low | Trivial | 1-line add |
| 5 | Empty Primary view shows headers-only table | Low | Trivial | Sub-message fallback in `rFacTable` |
| 6 | Bar-bg hardcoded rgba (indigo/amber) | Medium | Trivial | Introduce `--pos-bg`/`--neg-bg` CSS vars or replace with `rgba(var(--pos-rgb)…)` |
| 7 | Pill active colors hardcoded (`.fgp.active`, `.fgp.prof.active`) | Low | Trivial | Replace with theme vars |
| 8 | Profitability hex (`#fb923c`) scattered across 5 locations | Low | Trivial | Consolidate into `--prof` CSS var |
| 9 | `FAC_PRIMARY` uses `/momentum/i` regex fallback | Low | Non-trivial | Explicit enumeration; PM call on whether future "Momentum X" factors should auto-join Primary |
| 10 | No `isFinite` guard on `f.a` | Low | Trivial | Filter/guard |
| 11 | Profitability-decrease threshold `-0.05` hardcoded | Low | Non-trivial | Move to `_thresholds`; PM decision on wire-through to Settings |
| 12 | `hold` param in `rFac`/`rFacTable` is unused | Trivial | Trivial | Drop param or document; 1 line |
| 13 | Primary/All toggle doesn't flow to sibling cardFacButt | Open | Non-trivial | Sibling audit #9. PM decision first. |
| 14 | CSV export + hidden columns — unverified behavior | Low | Follow-up | Needs functional test |
| 15 | PNG button present | Cleanup | — | Out of scope; global sweep |
| 16 | Sparkline fallback to raw `e` (when no bench) conflates "active" with "exposure" trend | Low | Non-trivial | Either always compute active (skip cells with no bm) or label sparkline mode. PM call. |

---

## 8. Verification Checklist

- [x] **Data accuracy:** `f.n`, `f.a`, `f.c`, `f.ret`, `f.imp` traced to parser `_build_factor_list`. Canonical factor names match registry.
- [x] **Edge cases:** empty factors ✅; quote-escaping ✅. isFinite ❌, null-vs-zero 🟡.
- [🟡] **Sort:** wired on 5 of 6 columns correctly; col 3 (sparkline) silently broken.
- [x] **Filter — Primary/All:** works, re-renders into `#tbl-fac-wrap`.
- [x] **Filter — group highlight:** works, toggles opacity.
- [x] **Column picker:** works, persists to `rr_fac_cols`.
- [x] **Export CSV:** present via ⬇ dropdown.
- [ ] **Export PNG:** present — against no-PNG rule; flag for global sweep.
- [x] **Full-screen modal:** reachable, wired, opens scatter view.
- [x] **Popup card / drill:** row click → `oDrF(name)` wired and functional.
- [x] **Responsive:** fits half-width grid cell; no horizontal scroll.
- [🟡] **Themes:** text colors theme-aware; bar bg, pill active, Profitability all hardcoded.
- [x] **Keyboard:** inherited.
- [x] **No console errors:** none observed via static read.
- [ ] **Note-popup right-click:** not wired on card title.
- [ ] **isFinite guards:** missing on `f.a`.
- [x] **Week-selector awareness:** reads latest `cs.factors` — consistent with dashboard-wide factor-detail limitation.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| `cardFacButt` (sibling, `g2` partner) | Shares `s.factors`. This card owns the ⛶ full-screen button; sibling owns the diverging-bar visualization + top-TE strip. |
| Full-screen Factor Risk Map (`renderFsFactorMap` L5513+) | Opened from this card's ⛶ button. Complementary scatter view. |
| Factor Attribution Waterfall (row below this one) | `s.factors.filter(f=>f.imp!=null)` — same source, different aspect. |
| Factor drill modal (`oDrF(name, range)` at L4091) | Destination of this card's row clicks. |
| Factor Drill from Risk tab (`oDrFRisk` L3388) | Alternative entry point from Risk tab. Not wired from this tile. |
| cardThisWeek bullet templates | Reference `s.factors` for bullet generation; use same `_thresholds.factorSigma` as this tile's visual cutoffs would benefit from. |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Audit v1 — three-track audit of Factor Detail table tile. Documented column-picker persistence, Primary/All toggle, group-highlight pills. Identified silent col-3 sort bug, three competing factor-group palettes, and hardcoded pill/bar theming. | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — FAC_PRIMARY + FACTOR_GROUPS authority
- rr-data-validator — §1.4 JSON spot-check pending
- rr-design-lead — §3.3 three-palette canonicalization sign-off

---

**Sign-off:** Data track GREEN-YELLOW (empty-state correct, quote-escaping good, col-3 sort silently broken, null-coercion anti-pattern repeats). Functionality track GREEN-YELLOW (most feature-complete Factors tile — sort/filter/picker/pills/CSV/drill/full-screen all wired; small gaps: note popup, broken col-3 sort, empty-primary message). Design track YELLOW (dense + clean internally, but three factor-group palettes coexist and Profitability hex scattered across 5 locations).

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | 🟢 | Card, render fns, state, full-screen path all located |
| **1. Data Source** | 🟡 | Source correct, empty-state ✅; null-coercion in data-sv; missing isFinite; sparkline col has no sort key |
| **3. Visualization** | 🟡 | Right chart choice; Profitability flip semantically correct; three competing factor-group palettes |
| **4. Functionality** | 🟢-🟡 | Richest tile in the Factors row; broken col-3 sort and missing note-popup are the only real gaps |
| **5. Drill** | 🟢 | Row drill + full-screen both wired |
| **6. Design** | 🟡 | Clean density + alignment; theme-var gaps in bar bg, pill active, Profitability |

### Fix queue

**Trivial (agent can apply, ≤5 lines each):**
1. Fix col-3 sort — either drop `onclick="sortTbl('tbl-fac',3)"` on the 12wk `<th>` OR add `data-sv` = last-active-value to each sparkline cell
2. Swap `data-sv="${x??0}"` → `"${x??''}"` on exp / te / ret / imp cells (4 spots)
3. Add `oncontextmenu="showNotePopup(event,'cardFacDetail');return false"` on the card-title div (L1162)
4. Empty-Primary-view sub-message in `rFacTable` (3-line fallback)
5. Add `.filter(f=>isFinite(f.a))` or equivalent guard before `maxExp`/`pct` computation
6. Replace bar-bg hardcoded rgba with CSS vars (`--pos-bg` / `--neg-bg` — 2-line var addition + 2 replacements)
7. Replace `.fgp.active` `#6366f1` and `.fgp.prof.active` `#fb923c` in CSS L170–L171 with `var(--pri)` / `var(--warn)` (or dedicated `--prof`)
8. Consolidate Profitability hex `#fb923c` into a single `--prof` CSS var (5 call-sites)
9. Drop unused `hold` param from `rFac`/`rFacTable` signature (optional cleanup)

**Non-trivial (needs design/PM decision or larger change):**
- Canonicalize one factor-group color palette across pills + `facGrpColor()` + cardFacButt bars + exposure-bar bg (§3.3)
- Replace `/momentum/i` regex in `FAC_PRIMARY` detection with explicit enumeration
- Move Profitability-decrease threshold `-0.05` into `_thresholds` with Settings UI
- Harmonize sparkline computation when benchmark absent (active vs raw exposure)
- Honor sibling `cardFacButt` ↔ this tile Primary/All filter sync (pending sibling-audit #9)
- Verify CSV export behavior when columns are hidden

**Cleanup (out of scope, logged):**
- Remove PNG item from ⬇ dropdown per LIEUTENANT_BRIEF §3 no-PNG rule
