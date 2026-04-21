# Tile Spec: cardFRB — Audit v1

> **Audited:** 2026-04-21 | **Auditor:** Tile Audit Specialist (CLI)
> **Status:** 🟡 signed-off with open items (design token drift + tile-wide click is an ambiguous UX pattern)

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Risk Budget (donut) |
| **Card DOM id** | `#cardFRB` |
| **Render function(s)** | `rFRB(s)` at `dashboard_v7.html:L2693–L2703`; invoked from Exposures tab render pipeline at L1342 |
| **Drill modal** | `oDrRiskBudget()` at `dashboard_v7.html:L5386–L5431` → `#riskBudgetModal` (L440) |
| **Render target** | `<div id="frbDiv" style="height:260px">` at L1285 |
| **Tab** | Exposures (`tab-exposures`) |
| **Grid row** | Row 8 of Exposures — right half of `grid g2` (pairs with `cardMCR` on the left) |
| **Width** | Half (`g2` cell) |
| **Tile-wide interaction** | `onclick="oDrRiskBudget()"` on the `.card` element, `cursor:pointer` inline; export-bar uses `event.stopPropagation()` so the PNG button doesn't also drill |
| **Owner** | CoS / Tile Audit Specialist |
| **Spec status** | `draft → signed-off-with-followups` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** `s.factors[]` (same array as cardFacButt, cardFacDetail, factor waterfall, risk decomposition tree). Built by parser `_build_factor_list` (`factset_parser.py:L847–L865`).
- **Typical array length:** ~20–40 factors (FactSet MAC / APT / RMM variant).
- **Filter before render:** none. `rFRB` plots every factor returned by the parser, regardless of whether `f.c` is null, zero, or present.

### 1.2 Field inventory

| # | Encoding | Field | Type | Source | Example | Formatter | Notes |
|---|---|---|---|---|---|---|---|
| 1 | slice label | `f.n` | string | Factor name from RISKMODEL section | "Value" | raw | Categorical; parser-order preserved |
| 2 | slice value | `Math.abs(f.c \|\| 0)` | number | %T factor contribution → absolute value | 3.2 | `%{value:.2f}` | **Critical: absolute value erases sign.** A positive and negative contribution of equal magnitude look identical. |
| 3 | slice tooltip | `f.c` | number | same | 3.2 | `f2(v,2)` + `%` | Rendered through hovertemplate |
| 4 | percent display | `(abs(f.c)/total)*100` | derived | computed at render | 12% | Plotly `%{percent}` | Sums to 100% by construction |
| 5 | slice color | palette index (`i % 7`) | — | hardcoded array | `#6366f1` (indigo) | — | No semantic meaning; position-in-array determines color |

**Not rendered but available on the object:** `f.a` (active exposure), `f.e` (port exposure), `f.bm` (bench exposure), `f.ret`, `f.imp`, `f.dev`, `f.cimp`, `f.risk_contr`. The drill modal (`oDrRiskBudget`) uses `f.a` and computes `f.c*cs.sum.te/100` as MCR.

### 1.3 Derived / computed fields

| Field | Computation | Location | Notes |
|---|---|---|---|
| `total` | `facs.reduce((a,f)=>a+Math.abs(f.c\|\|0),0) \|\| 1` | L2696 | Normalizer for percent display; `\|\| 1` guards zero-divide |
| slice sort | none | — | Slices rendered in parser order, not by magnitude. Plotly auto-sorts pie slices by default (`sort:true`), which **does** re-order visually but does not affect color assignment — so the palette becomes non-deterministic vs factor identity. |

### 1.4 Ground truth verification

- [x] Field path traced: `f.n`, `f.c` present in parser output (`factset_parser.py:L853–L863`). `f.c` = `exp.get("c")` from `current_rm.exposures` (RISKMODEL exposures block).
- [x] Canonical factor names (per `risk-reports-specialist.md`): Value, Growth, Dividend Yield, Earnings Yield, Momentum, Momentum (Medium-Term), Market Sensitivity, Volatility, Profitability. These match `FACTOR_GROUPS` at L1638–L1642.
- [x] Donut total (pre-normalization) = sum of `|f.c|`. **This is not guaranteed to equal 100%** — it will only equal ~100% if `c` is already a % of total TE (which FactSet returns for the risk model exposures). Audit note: the strip on cardFacButt treats `f.c` as "% TE", and the RBE formula at L5394 computes `f.c*cs.sum.te/100` as MCR — confirming `f.c` is a percentage of portfolio TE. So raw `Σ|f.c|` ≈ total factor risk as % of TE (often 40–70%), not 100. The donut's normalization makes the slice-labeled percentages **proportions-of-factor-risk**, not **proportions-of-total-TE**. Card title says "Factor Risk Budget" which supports that framing — but the hovertemplate labels the raw `f.c` as "Contrib" without clarifying it is a factor-risk-share number, not a TE-share number.
- [ ] Spot-check against raw CSV: pending loaded JSON (see AUDIT_LEARNINGS §Known blockers).

### 1.5 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `s.factors` absent or empty (`!facs \|\| !facs.length`) | `<p ...>No factor data</p>` written into `frbDiv` | ✅ Guard present per AUDIT_LEARNINGS §Viz-renderer pattern |
| `f.c == null` | `(f.c\|\|0)` → 0. Slice still present with value 0 (invisible, but label in legend) | 🟡 Silently included as zero-value slice. Pie slice of magnitude 0 renders nothing visible but still occupies label space. |
| `f.c === NaN` or `Infinity` | **No `isFinite` guard.** `Math.abs(NaN)` = `NaN`, Plotly silently drops the slice. | 🟡 Lesson Patch 003 not applied here (cf. sibling cardFacButt L2334 which does `isFinite(f.a)` filter). |
| All `f.c === 0` | `total \|\| 1` prevents divide-by-zero; Plotly renders an empty pie (no slices visible). | 🟡 No "No factor contribution" message — user sees the card title with a blank donut. |
| Factor name duplicates | Plotly merges slices silently. Not observed in practice. | 🟡 Not defended. |
| `f.c` negative | `Math.abs(f.c)` drops the sign. **A factor that diversifies risk (negative contribution) is indistinguishable from one that adds risk.** | 🔴 This is the single most material data concern — sign is part of the signal for risk budget framing. Discussed §7. |

**Section 1 verdict: 🟡 YELLOW** — source correct and empty-state guard is present; but (a) no `isFinite` guard on `f.c`, (b) negative-contribution sign is collapsed via `Math.abs`, and (c) the donut labels percents as "Contrib %" without clarifying the denominator is factor-risk, not TE. Drill modal has the same issues (also uses `Math.abs(f.c)`).

---

## 2. Columns & Dimensions Displayed

Chart tile — no table columns. Encodings:

- **Category encoding (slice):** `f.n` (factor name). Plotly `sort:true` (default) re-orders slices largest-first.
- **Value encoding (slice arc length):** `Math.abs(f.c || 0)`. Normalized by Plotly to percent of total.
- **Color encoding:** palette cycle `['#6366f1','#10b981','#a78bfa','#ef4444','#8b5cf6','#38bdf8','#ec4899']` — 7 positions, factor index mod 7. No semantic meaning: indigo and red here carry no over/under or positive/negative signal, they are just positions in the palette. A factor whose contribution happens to fall at index 3 renders red regardless of whether its exposure is intentional or unintentional.
- **Label rendering:** `textinfo:'label+percent'` — name + percentage shown on slice.
- **Hole:** 0.4 (donut style).
- **Hovertemplate:** `'%{label}<br>Contrib: %{value:.2f}%<br>%{percent}<extra></extra>'`.

**Observation:** cardFacButt (the sibling) colors factor bars by sign (over/under); cardFRB (this tile) colors slices by palette position; `renderFsFactorMap` colors bubbles by factor group. Three different coloring schemes for the same data array across three adjacent tiles.

---

## 3. Visualization Choice

### 3.1 Chart / layout type
Donut (pie with `hole:0.4`). Single trace. Static 260px height (no dynamic sizing even though factor count varies ~20–40).

### 3.2 Axis scaling
N/A — categorical.

### 3.3 Color semantics
- Palette hex values **hardcoded** at L2699 (7 colors). No `THEME()` integration. No `var(--pri)` / `var(--pos)` / `var(--neg)`.
- The same 7-color palette is duplicated verbatim in the drill modal (`oDrRiskBudget` L5422).
- Palette theming: since color = palette index, dark-mode colors are used in light-mode unchanged. The 7 chosen colors are saturated enough to read on both themes, but consistency with `THEME().pos`/`THEME().neg` (extended 2026-04-20, AUDIT_LEARNINGS §Viz-renderer pattern) is broken.
- Text color on slices: `color:THEME().tickH` ✅ theme-aware (L2700).

### 3.4 Responsive behavior
- Chart resizes with viewport (`plotCfg.responsive:true`).
- On narrow viewports the half-width `g2` grid reflows to full width — CSS-driven.
- Fixed 260px height — on very narrow screens pie + labels may overlap. Not tested.

### 3.5 Empty state
`<p style="color:var(--txt);font-size:12px;text-align:center;padding:60px">No factor data</p>` at L2695 — ✅ correct pattern, writes into the div rather than silently returning. Matches AUDIT_LEARNINGS prescription.

### 3.6 Loading state
None. Synchronous render.

---

## 4. Functionality Matrix

**Benchmark tiles:** cardSectors (gold standard table tile), cardMCR (tile-row neighbor, similar half-width viz), cardFacButt (sibling viz that shares data).

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort** | 🟡 (implicit) | Plotly default `sort:true` | Slices auto-sorted largest-first by value. No user control. |
| **Filter** | ❌ | — | Every factor plotted, including zero-contribution and negative-contribution entries (post-abs). |
| **Column picker** | N/A | — | Not a table. |
| **Row click → drill** | 🟡 (tile-level, not slice-level) | `onclick="oDrRiskBudget()"` on the whole card | Clicking **anywhere** on the card opens the drill. Clicking an **individual slice** does nothing specific — no per-factor drill from this tile. Drill opens a tile-wide detail view, not the clicked factor. |
| **Slice click → drill into factor** | ❌ | — | Sibling `renderFsFactorMap` wires `plotly_click → oDrF(name)` (L5557); cardFacButt now wires it too (L2369). This tile does not. A slice click should drill to `oDrF(slice.label)`. |
| **Right-click context menu** | 🟡 | global handler | Captures `<td>` cells; does nothing on Plotly SVG slices. |
| **Card-title right-click → note** | ❌ | `showNotePopup` | No `oncontextmenu` wiring on the card title. Sibling cardFacButt L1156 has it; cardMCR L1278 does not; cardFRB does not. |
| **📝 Note badge** | ❌ | `refreshCardNoteBadges` | Runs globally at L842 but no hook on this card because there's no note-popup handler. |
| **Export PNG** | 🟥 (**present against policy**) | `screenshotCard('#cardFRB')` with `event.stopPropagation()` guard | LIEUTENANT_BRIEF §3 **hard rule: no PNG buttons.** Flag for global removal sweep. |
| **Export CSV** | ❌ | — | Donut data (`factor, contribution%, share%`) should be exportable. Sibling `cardFacDetail` has `exportCSV('#cardFacDetail table','factors')`. |
| **Full-screen modal** | ❌ (but drill modal is a de facto full-screen) | `oDrRiskBudget()` → `#riskBudgetModal` | The drill modal has a richer pie + breakdown table + bars. No separate "expand chart" affordance. |
| **Toggle views** | ❌ | — | No Donut/Bar toggle, though the drill shows both. |
| **Range selector** | N/A | — | Not time-series. |
| **Color-mode picker** | ❌ | — | Could toggle Palette / FactorGroup / Sign. |
| **Legend** | ❌ | `showlegend:false` | Legend suppressed; user relies on on-slice label+percent. Reasonable for space-constrained donut. |
| **Hover tooltip** | ✅ | Plotly hovertemplate | `%{label}<br>Contrib: %{value:.2f}%<br>%{percent}`. See §1.4 — "Contrib" terminology is ambiguous. |
| **Theme-aware (text on slice)** | ✅ | `THEME().tickH` | |
| **Theme-aware (slice colors)** | ❌ | hardcoded 7-color palette | Violates AUDIT_LEARNINGS §Viz-renderer pattern. |
| **Hover affordance showing it's clickable** | 🟡 | `cursor:pointer` on the whole card + "Detail →" hint text | The card has a small `<span>Detail →</span>` at L1284 and `cursor:pointer` inline, which together signal clickability. Tooltip on card-title reads "Click for detailed factor risk budget breakdown". ✅ reasonable affordance — but it signals a tile-level drill, not slice-level. |
| **Color-blind safe** | ❌ | no `_prefs.cbSafe` wiring | |
| **Keyboard activation** | ❌ | `onclick` only, no `tabindex`, no `role="button"`, no `onkeydown` | Summary cards at L1110 have `tabindex="0" role="button"`; this card does not. Keyboard users can't open the drill. |

### 4.1 Tile-wide `onclick` — the primary UX question

Per the audit ask: **is the tile-level `onclick="oDrRiskBudget()"` the right pattern, and is hover affordance adequate?**

**Findings:**
1. **Mixed pattern across the dashboard.**
   - Summary cards (L1110+) use tile-wide click + `tabindex` + `role="button"` + `aria-label` → accessible.
   - cardFRB uses tile-wide click but without keyboard support / role / aria-label → not accessible.
   - Most table tiles (cardSectors, cardHoldings, cardCountry) use row-level click, not tile-level.
   - cardMCR (neighbor on same row) has **no** click-to-drill at all — inconsistency with cardFRB.
2. **Affordance quality.**
   - The card has: `cursor:pointer` (inline, ✅ explicit), `Detail →` chevron text (✅ visible signal), card-title tooltip "Click for detailed factor risk budget breakdown" (✅ explains action). These are stronger-than-average cues.
   - **Missing:** no hover-state (border tint, elevation, background change). Compared to `.clickable` row styling (see `rWt` output, `cursor:pointer` + hover bg), the card is visually static. User discovers clickability only by hovering → `cursor:pointer`.
3. **Semantic ambiguity.**
   - The donut slices look clickable (they're a chart, users expect drill-to-factor). But slice click currently bubbles up to tile-level drill (which opens the same page regardless of which slice clicked). This is a **UX trap**: users will click a specific slice expecting per-factor detail, and get a modal that shows all factors. Fix: wire `plotly_click` on `frbDiv` to call `oDrF(point.label)` so slice click goes to factor drill; keep card-background click for the overall breakdown.
4. **PNG button stops propagation** (L1284 `event.stopPropagation()`) which is correct defensive coding — but the PNG button should be removed per project rule, making that guard unnecessary.

**Recommendation:** tile-wide drill is an acceptable pattern (precedent exists), but the current implementation has three gaps: (a) no keyboard access, (b) no hover state on the card itself, (c) slice clicks should drill to the per-factor modal, not the parent modal. Fix (a) and (c) are trivial; (b) needs a `.card.clickable { transition ... }` CSS rule (small non-trivial).

### 4.2 Functionality gaps vs benchmarks

| Gap | Severity | Fix class | Recommendation |
|---|---|---|---|
| Slice click does not drill to per-factor view | **Medium** | Trivial | Add `document.getElementById('frbDiv').on('plotly_click', d => { if(d?.points?.[0]?.label && typeof oDrF==='function') oDrF(d.points[0].label); });` at end of `rFRB`. Mirror of cardFacButt L2369. Needs `event.stopPropagation()` or to prevent the tile-level `onclick` from firing on the same click — can be handled by checking the click target. |
| No keyboard access to drill | Medium | Trivial | Add `tabindex="0" role="button" aria-label="Factor risk budget — click to open detailed breakdown"` on the card, plus `onkeydown` that opens the drill on Enter/Space. Mirror summary cards L1110. |
| No note-popup right-click | Low | Trivial | Add `oncontextmenu="showNotePopup(event,'cardFRB');return false"` on the card-title div. Mirror cardFacButt L1156. |
| Hardcoded palette | Medium | Trivial | Replace 7-color hex array with a `THEME().palette` or read from CSS vars. Same fix applies to drill modal L5422 (keep in sync). |
| `Math.abs(f.c)` drops sign | **Medium / material** | Non-trivial (design decision) | Either (a) colorize negative-contribution slices differently and keep donut on absolute, or (b) drop negative-contribution factors from the donut and note them in the subtitle. PM decision. |
| No isFinite guard on `f.c` | Low | Trivial | Add `.filter(f => isFinite(f.c))` before `labels`/`values` mapping. Mirror cardFacButt L2334. |
| No CSV export | Medium | Non-trivial | Add a CSV button to the export-bar that writes `factor,contribution_pct,share_of_factor_risk_pct` via a hidden table or direct blob. |
| "Contrib" in tooltip is ambiguous (%of TE vs %of factor risk) | Low | Trivial | Change hovertemplate to `'<b>%{label}</b><br>TE contribution: %{value:.2f}%<br>Share of factor risk: %{percent}<extra></extra>'`. Clarifies denominator. |
| PNG button present | Cleanup | Trivial | Per LIEUTENANT_BRIEF §3 no-PNG rule — remove. Also remove the `event.stopPropagation()` guard once PNG is gone. |
| No hover state on clickable card | Low | Non-trivial | CSS: `.card[onclick]:hover { border-color:var(--pri); transform:translateY(-1px); }` or similar. Needs design review for consistency. |
| Legend suppressed but slices have only label+percent | Low | Trivial | Consider adding `textposition:'outside'` for narrow slices so small contributors are readable. Plotly defaults can collapse tiny labels. |

**Section 4 verdict: 🟡 YELLOW** — empty-state guard is correct and the drill path works, but the tile-wide click pattern is underpowered (no keyboard access, no slice-level drill, no hover state) and the palette + sign-collapse choices carry real design cost.

---

## 5. Popup / Drill / Expanded Card

### 5.1 Drill identity
- **Function:** `oDrRiskBudget()` at L5386
- **Modal DOM id:** `#riskBudgetModal` (outer), `#riskBudgetContent` (inner)
- **Registered in `ALL_MODALS`:** ✅ L4669 — Escape-close works

### 5.2 Modal contents

1. **Header:** "Factor Risk Budget — Detailed" + close button
2. **Left:** donut pie (`#rbPieDiv`) — re-renders the same donut with same hardcoded palette
3. **Right:** breakdown table (plain `<table>`, no `id`, not sortable) with columns: Factor | Exposure | Contrib% | % of Total | MCR | Type
4. **Bottom:** bar chart (`#rbBarDiv`) of "% of Total Risk" per factor, colored by intentional (indigo) / unintentional (red)

Modal adds two fields not shown on the tile:
- **`pct` = abs(f.c)/total*100** (% of Total factor risk)
- **`mcr` = f.c*cs.sum.te/100** (absolute MCR in TE units)
- **`intentional` = `abs(f.a??0) > 0.2`** (simple heuristic threshold: any exposure >|0.2σ| is treated as intentional)

### 5.3 Modal functionality parity

| Aspect | Drill modal | Gaps |
|---|---|---|
| Sort | ❌ sort by pct desc at render, no header-click sorting | Non-trivial — needs `id="tbl-rbBreakdown"` + `sortTbl` wiring |
| Filter | ❌ | Low priority |
| Export (CSV/PNG) | ❌ | Trivial to add CSV via table-id + `exportCSV` |
| Note badge | ❌ | N/A for modals |
| Click-to-drill (factor row → factor modal) | ❌ | Trivial — add `onclick="oDrF('${d.n}')"` + `cursor:pointer` on each row |
| Theme-aware colors | 🟡 | Donut palette hardcoded; bar colors hardcoded `#6366f1` / `#ef4444`; tick uses `THEME()` |
| Responsive | 🟡 | `grid g2` holds pie + table; narrow viewports will stack — not audited |
| Intentional threshold config | ❌ | Hardcoded `0.2` — should read from `_thresholds` (cross-tile pattern — see cardThisWeek audit). |

### 5.4 Modal data source
Identical to tile — `cs.factors`. Modal does NOT use `getSelectedWeekSum()`. If `_selectedWeek` is set, the drill modal silently shows the **latest** factor data regardless of the selected historical week. This is the same cross-tile trap flagged in AUDIT_LEARNINGS §"Shared state traps / Week-selector awareness" — the week-selector banner on the dashboard promises a historical view, but the FRB drill always reflects latest. **Same issue applies to the tile itself** (uses `s.factors` directly via `cs.factors` alias, no week awareness).

**Section 5 verdict: 🟡 YELLOW** — drill modal renders cleanly and is registered for Escape-close, but inherits all the data-track issues (sign collapse, hardcoded palette, hardcoded intentional threshold) and adds new gaps (table not sortable, not drillable, no CSV). Week-selector awareness is a shared blind spot with the tile.

---

## 6. Design Guidelines

### 6.1 Density

| Dimension | Value | Notes |
|---|---|---|
| Card padding | inherited from `.card` (16px) | ✅ |
| Chart height | fixed 260px | 🟡 tight — factor labels can crowd for 30+ factors |
| Slice label font | 10px | ✅ matches axis-tick scale |
| Card-title font | 13px (inherited) | ✅ |
| "Detail →" hint | 10px, `var(--pri)` | ✅ subtle |

### 6.2 Emphasis & contrast

- Slice values carried by arc length (standard).
- `textinfo:'label+percent'` places text on each slice. At 260px height with ~30 slices, smallest slices will have labels that overlap or clip. No outside-positioning fallback.
- "Detail →" chevron in `var(--pri)` is good affordance ✅
- The card does not style itself differently despite being clickable (no border tint, no hover-elevation). Compared to `.clickable` rows which have background-hover via CSS, this card signals click only via `cursor:pointer` + the chevron + tooltip. Adequate but could be stronger.

### 6.3 Alignment
N/A — pie chart. Plotly defaults.

### 6.4 Whitespace
- `margin:{l:20,r:20,t:10,b:10}` L2702 — symmetrical and compact. ✅

### 6.5 Motion / interaction feedback

- Hover on slice: Plotly default pull-out on hover. ✅ (built-in)
- Click on slice: **does nothing specific** — the tile's onclick fires via event bubbling, opening the modal regardless of which slice was clicked. This is the main interaction ambiguity.
- Click on card background: opens drill modal. ✅
- Empty state: plain text. ✅
- Focus ring: not implemented (no tabindex). ❌

### 6.6 Cross-tile design consistency

- **Palette divergence:** cardFRB uses a 7-color palette (indigo/green/violet/red/purple/cyan/pink) that does not match any other tile. cardMCR (neighbor, L2686) uses indigo/green binary. cardFacButt (sibling) uses sign-based pos/neg. renderFsFactorMap uses factor-group-based color. Four separate coloring systems for factor-related tiles.
- **Pos/neg conventions:** other factor tiles color positive exposure as `var(--pos)` / overweight-good. This tile uses `|f.c|` → positive-only, so pos/neg semantics are lost. The drill modal uses indigo-for-intentional, red-for-unintentional — also a sign-free encoding.
- **Section-header mini-cap pattern:** no section header inside the card. The strip pattern from cardFacButt is absent. 🟡 potentially a miss — a "Factor Risk Budget" card could benefit from a small "Total Factor Risk: X%" stat line above the donut, mirroring the Top-TE strip on cardFacButt.

**Section 6 verdict: 🟡 YELLOW** — dimensions clean, empty-state correct, but (a) palette drift vs AUDIT_LEARNINGS §Viz-renderer pattern, (b) no hover-state on the clickable card, (c) no keyboard affordance, (d) potential label overlap on 30+ factor strategies.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Classification | Resolution path |
|---|---|---|---|---|
| 1 | `Math.abs(f.c)` erases sign of factor contribution | Medium / material | Non-trivial (PM decision) | Either colorize negatives distinctly or drop them; either way, expose the direction. |
| 2 | Slice click does not drill to per-factor modal | Medium | Trivial | Wire `plotly_click → oDrF(label)` on `frbDiv`. ~3 lines. |
| 3 | Tile-wide onclick has no keyboard access | Medium | Trivial | Add `tabindex="0" role="button" aria-label="…" onkeydown="…"` to the card. ~2 lines. |
| 4 | Hardcoded 7-color palette (tile + drill) | Medium | Trivial | Define `THEME().palette` or a `--palette-*` CSS var set. Replace both L2699 and L5422. ~4 lines. |
| 5 | Hovertemplate "Contrib" is ambiguous about denominator | Low | Trivial | Rename to "TE contribution" + "Share of factor risk". Trivial string edit. |
| 6 | No `isFinite(f.c)` guard | Low | Trivial | Add `.filter(f => isFinite(f.c))`. Mirror cardFacButt L2334. 1 line. |
| 7 | No CSV export | Medium | Non-trivial | Add CSV button + hidden-table or blob-download handler. |
| 8 | PNG button present (violates no-PNG rule) | Cleanup | Trivial | Remove button at L1284; remove `event.stopPropagation()` guard. |
| 9 | No card-title right-click note-popup | Low | Trivial | Add `oncontextmenu="showNotePopup(event,'cardFRB');return false"`. 1 line. |
| 10 | Drill modal table not sortable, not drillable per row | Low | Non-trivial | Add `id="tbl-rbBreakdown"` + `onclick=oDrF(row.n)` + sort wiring. |
| 11 | Drill modal intentional threshold `>0.2` hardcoded | Low | Trivial | Read from `_thresholds.intentionalFactorSigma` (fall back 0.2). Matches cross-tile pattern. |
| 12 | Tile ignores `_selectedWeek` — historical week shows latest factor data | Medium | Non-trivial (needs `s.hist.fac` plumbing) | AUDIT_LEARNINGS §Shared state traps already has this pattern. |
| 13 | Slice colors by palette index (not by factor identity or group) | Low | Trivial | Option: `facGrpColor(f.n)` mapping for thematic consistency with renderFsFactorMap. |
| 14 | No hover-state on clickable card | Low | Non-trivial | Needs CSS for `.card[onclick]:hover` — design review. |
| 15 | On 30+ factor strategies, slice labels may overlap at 260px | Low | Trivial | `textposition:'outside'` for small slices + bump height to 300px. |
| 16 | No section header / subtitle (e.g., "Total Factor Risk: X%") | Low | Non-trivial | Design decision — mirror cardFacButt's Top-TE strip. |

---

## 8. Verification Checklist

- [x] **Data accuracy**: `f.n`, `f.c` traced to parser. Canonical factor names match FACTOR_GROUPS registry.
- [ ] **Edge cases**: empty-state guard ✅. NaN/Infinity ❌ (no isFinite). Null `f.c` coerced to 0. Negative `f.c` collapsed via `Math.abs`.
- [x] **Sort**: Plotly default sort:true — user has no control.
- [ ] **Filter**: none provided; zero-contribution factors render invisibly.
- [x] **Column picker**: N/A.
- [ ] **Export PNG**: present, against policy — flag for removal.
- [ ] **Export CSV**: missing.
- [x] **Full-screen modal (drill)**: `oDrRiskBudget` opens `#riskBudgetModal`, Escape-close works, renders donut + breakdown + bars.
- [ ] **Per-factor drill from tile**: absent — slice click falls through to tile-level drill.
- [ ] **Keyboard access**: no tabindex, no Enter/Space handler.
- [x] **Responsive**: Plotly responsive; card reflows to full width on narrow via grid.
- [ ] **Themes**: slice-text color ✅, slice colors ❌ hardcoded; drill modal same issue.
- [x] **Keyboard (Escape)**: drill modal closes via ALL_MODALS handler.
- [x] **No console errors**: code path is clean.
- [ ] **Theme-aware colors**: partial — fix queued.
- [ ] **isFinite guards**: missing — fix queued.
- [ ] **Week-selector awareness**: tile + drill silently show latest even when `_selectedWeek` is set.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| `cardMCR` (neighbor, `g2` partner on row 8) | Reads `s.hold[].mcr`. Does NOT have tile-level onclick — asymmetry on the same row. Also has hardcoded `#8b5cf6` / `#10b981`. |
| `cardFacButt` (Factors tab) | Reads same `s.factors`. Colors by sign. Has slice-click→`oDrF`. Has note-popup right-click. Gold-standard sibling for fix patterns. |
| `cardFacDetail` (Factors tab sibling of cardFacButt) | Reads same data. Has full-table CSV export, Primary/All toggle, group pills. Reference for "what factor tiles should offer". |
| `renderFsFactorMap` (full-screen Factor Risk Map) | Colors by factor group. Has plotly_click → oDrF. Aspirational target for color scheme. |
| `rFacWaterfall` (Factor attribution waterfall, Factors tab) | Reads same `s.factors`. Different field (`f.imp`). |
| Risk Decomposition Tree (L2782) | Also reads `s.factors`; sums `\|f.c\|` for group aggregates. Confirms the "factor risk as sum of abs contributions" pattern is used twice. |
| `oDrFacRiskBreak()` (L4945) | Alternate drill entry from Risk Alerts banner. Different UX path into similar data. |
| `oDrF(name, range)` | Destination the slice click *should* reach. Currently only reachable via cardFacButt, cardFacDetail row, or renderFsFactorMap bubble. |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Audit v1 — three-track audit. Key findings: `Math.abs(f.c)` sign-collapse is material; tile-wide onclick is an accepted pattern but lacks keyboard + slice-level drill + hover state; hardcoded 7-color palette + hardcoded intentional threshold in drill. 7 trivial fixes, 5 non-trivial. | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — factor-name + `f.c` semantics authority (is `f.c` a % of TE, or of factor risk, or of MCR? Drill suggests TE based on `f.c*te/100 = MCR`. Confirm with FactSet.)
- rr-data-validator — §1.4 JSON spot-check pending; specifically needs to confirm `Σ|f.c|` ≈ factor-risk share of TE (40–70%) not 100%
- rr-design-lead — §6 palette standardization + hover-state design decision

---

**Sign-off:** Data track 🟡 YELLOW (sign collapse + missing isFinite + ambiguous hovertemplate denominator; empty-state ✅). Functionality track 🟡 YELLOW (no keyboard, no slice-level drill, no CSV; tile-level drill works). Design track 🟡 YELLOW (palette drift vs AUDIT_LEARNINGS; missing hover-state; potential label crowding).

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | 🟢 | Tile, render fn, drill modal, neighbor row partner all located |
| **1. Data Source** | 🟡 | Source correct, empty-state ✅; missing isFinite; `Math.abs(f.c)` collapses sign; hovertemplate denominator ambiguous |
| **3. Visualization** | 🟡 | Donut is the right call; palette hardcoded; slice-text theme-aware only |
| **4. Functionality** | 🟡 | Tile-level drill works; slice-level drill, keyboard access, CSV all missing |
| **5. Drill** | 🟡 | Modal renders cleanly but inherits sign-collapse + palette drift; table not sortable/drillable; intentional threshold hardcoded |
| **6. Design** | 🟡 | Empty-state + density ✅; palette drift vs siblings; no hover-state on clickable card; chevron hint ✅ |

### Fix queue

**Trivial (agent can apply, ≤5 lines each):**
1. Add `.filter(f => isFinite(f.c))` before labels/values (L2698)
2. Wire `plotly_click → oDrF(label)` on `frbDiv` (mirrors cardFacButt L2369)
3. Add `tabindex="0" role="button" aria-label="Factor risk budget — click to open detail" onkeydown="if(event.key==='Enter'||event.key===' ')oDrRiskBudget()"` to the card (L1282)
4. Add `oncontextmenu="showNotePopup(event,'cardFRB');return false"` to the card-title (L1283)
5. Remove PNG button at L1284 + its `event.stopPropagation()` guard (per no-PNG rule)
6. Replace hovertemplate with `'<b>%{label}</b><br>TE contribution: %{value:.2f}%<br>Share of factor risk: %{percent}<extra></extra>'`
7. Replace hardcoded 7-color palette with `THEME().palette` or CSS-var array (both L2699 and L5422 together)
8. Add CSV button next to the (soon-removed) PNG button using a hidden table built from `facs`
9. Replace hardcoded intentional threshold `0.2` at L5393 with `_thresholds.intentionalFactorSigma ?? 0.2`

**Non-trivial (needs PM/design decision or larger change):**
- Sign-collapse on `f.c` — how should negative-contribution factors be represented? (color code? exclude? split-view? §7 item 1)
- Drill-modal table not sortable or drillable per row — needs table id + sort wiring + per-row onclick
- Week-selector ignorance — tile + drill always show latest (requires `s.hist.fac` plumbing)
- Hover-state on clickable card (`.card[onclick]:hover`) — global CSS change, needs design-lead review for consistency
- Factor-group coloring mode (`facGrpColor(f.n)`) vs current palette — alignment across cardFRB + cardFacButt + renderFsFactorMap (three-tile consistency PM call)

**Cleanup (out of scope, logged):**
- Asymmetry with cardMCR (neighbor on same row has no click-to-drill at all)

### Single most important finding

**`Math.abs(f.c)` at both L2696 (tile) and L5389 (drill) collapses sign.** A factor whose contribution is negative (diversifying risk, or a short position) is visually identical to one contributing the same magnitude positively. Users reading this tile cannot see the signed story of their risk budget. This is a data-fidelity miss in a risk-budget chart — not a design polish. Needs PM decision on representation before a fix can land.
