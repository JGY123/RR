# Tile Spec: cardFacButt — Audit v1

> **Audited:** 2026-04-21 | **Auditor:** Tile Audit Specialist (CLI)
> **Status:** 🟡 signed-off with open items (functionality gaps + hardcoded palette)

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Risk Map (diverging-bar factor exposure) |
| **Card DOM id** | `#cardFacButt` |
| **Render function(s)** | `rFacButt(s)` at `dashboard_v7.html:L2320–L2356`; strip helper `rFacTopTeStrip(s)` at `L2305–L2318`; full-screen version `renderFsFactorMap(s)` at `L5513–L5565` (invoked via `openFullScreen('facmap')` from sibling `cardFacDetail`) |
| **Render target** | `<div id="facButtDiv" style="height:480px">` (inline height is overwritten dynamically to `max(480, facs.length*30+60)px`) |
| **Sibling strip** | `<div id="facTopTeStrip">` rendered above the chart |
| **Tab** | Factors (`tab-factors`) |
| **Grid row** | Row 3 of Factors tab, left half of `grid g2` (pairs with `cardFacDetail` on the right) |
| **Width** | Half (`g2` cell) |
| **Owner** | CoS / Tile Audit Specialist |
| **Spec status** | `signed-off-with-followups` |

---

## 1. Data Source & Schema

### 1.1 Primary data source
- **Object path:** `s.factors[]` — built by parser `_build_factor_list` (`factset_parser.py:L847–L865`) from the 9-col exposures block + 31-col attribution section.
- **Typical array length:** ~20–40 factors depending on model (FactSet MAC / APT / RMM variant). `facs.length` directly drives chart height.
- **Filter:** `rFacButt` takes `s.factors` **unfiltered** — renders every factor regardless of exposure magnitude or materiality. The full-screen version filters `f.a!=null && (f.c||0)>0 && f.dev!=null`.

### 1.2 Field inventory

| # | Encoding | Field | Type | Source | Example | Formatter | Notes |
|---|---|---|---|---|---|---|---|
| 1 | y-axis label | `f.n` | string | Factor name from RISKMODEL section | "Value" | raw (automargin) | Categorical; order preserved from parser |
| 2 | x value / bar length | `f.a` | number | Active exposure (port − bench, in σ) | +0.152 | `(f.a??0).toFixed(3)` | Diverging: pos → right (indigo), neg → left (violet) |
| 3 | strip — badge value | `f.a` | number | Same as above | −0.08 | `fp(a,2)` + `σ` | Top 4 by `|f.c|` only |
| 4 | strip — TE% | `f.c` | number | %T contribution of factor | 3.2 | `f2(c,1) + '% TE'` | Sort key + threshold (`top[0].c < 0.01` → strip hidden) |
| 5 | hover (main) | `f.a` | number | Same | 0.125 | `%{x:.3f}` | Plotly hovertemplate |

**Not rendered but available on the object:** `f.e` (port exposure), `f.bm` (bench exposure), `f.c` (TE contribution), `f.ret`, `f.imp`, `f.dev` (factor σ), `f.cimp`, `f.risk_contr`. The sibling `cardFacDetail` table and full-screen modal use these — this tile only uses `f.n`, `f.a`, `f.c` (the latter only inside the strip).

### 1.3 Derived / computed fields

| Field | Computation | Location | Notes |
|---|---|---|---|
| `maxE` | `Math.max(...vals.map(Math.abs), 0.3)` | L2328 | Floor at 0.3 prevents tiny-range chart when all exposures are near zero |
| `xmax` | `Math.ceil(maxE*10)/10 + 0.2` | L2329 | Axis extent, symmetric ±xmax |
| `tvStep` | `xmax>1 ? 0.5 : xmax>0.5 ? 0.2 : 0.1` | L2330 | Adaptive tick spacing |
| `tickVals` / `tickText` | mirrored around 0 | L2331–2334 | Manual tick array so negatives display as positive magnitudes ("butterfly" labels) |
| `h` (height) | `max(480, facs.length*30 + 60)` | L2335 | Scales with factor count; overrides the static 480px inline style |
| strip `ow` | `f.a >= 0` | L2312 | Green treatment for overweight, red for underweight — note: uses hardcoded `#22c55e`/`#ef4444`, not THEME() |

### 1.4 Ground truth verification

- [x] Field path traced: `f.n`, `f.a`, `f.c` all present in parser output (`factset_parser.py:L853–L863`).
- [x] Canonical factor names (per `risk-reports-specialist.md`): Value, Growth, Dividend Yield, Earnings Yield, Momentum, Momentum (Medium-Term), Market Sensitivity, Volatility, Profitability — these match the `FACTOR_GROUPS` registry at `dashboard_v7.html:L1638–L1642`. **Note:** the ORVQ sub-factors named in CLAUDE.md (REV/VAL/QUAL/MOM/STAB_WAvg, OVER_WAvg) are *holding-level quintile ranks* from the 18-col group layout — they are **not** risk-model factor exposures, so they should *not* appear here. Correct separation confirmed.
- [ ] Spot-check against raw CSV: pending loaded JSON (see AUDIT_LEARNINGS §Known blockers).

### 1.5 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `s.factors` absent or empty | `<p ...>No factor exposure data</p>` written into `facButtDiv` | ✅ Guard present per Plotly empty-state pattern (AUDIT_LEARNINGS §Viz-renderer pattern) |
| `f.a == null` | `(f.a??0)` → 0 bar. Factor still plotted on y-axis at zero. | 🟡 Silently coerces missing data to zero. A genuinely missing exposure is indistinguishable from a true-zero exposure. |
| `f.a === NaN` or `Infinity` | **No `isFinite` guard.** `.toFixed(3)` on NaN returns `"NaN"`, which Plotly converts to 0. | 🟡 Lesson Patch 003 not applied here. |
| Strip: `top[0].c < 0.01` | Strip is cleared (empty string). Main chart still renders. | ✅ |
| Strip: missing `f.c` | `isFinite(f.c)` filter at L2308 removes the row. | ✅ Strip has the guard; main chart does not. |
| Factor name collisions (`f.n` duplicates) | Plotly silently stacks on the same y-row. Not observed in practice. | 🟡 Not defended. |

**Section 1 verdict: 🟡 YELLOW** — data is correctly sourced; empty-state guard is present (good); but no `isFinite` guard on `f.a` and null exposure is coerced to zero without distinction.

---

## 2. Columns & Dimensions Displayed

Chart tile — no table columns. Encodings:

- **Y encoding:** `f.n` (categorical), `autorange:'reversed'` so first-in-array is at top
- **X encoding:** `f.a` (active exposure, σ-units), linear, symmetric range `[-xmax, +xmax]`
- **Color encoding:** binary by sign — `#6366f1` (indigo, positive / overweight) vs `#a78bfa` (violet, negative / underweight). **Hardcoded hex.** Not `THEME().pos/neg`, not the diverging red/green semantics used elsewhere.
- **Size encoding:** none (bar height fixed by `facs.length*30+60`).
- **Hover:** `'<b>%{y}</b><br>Active Exposure: %{x:.3f}'` — shows name + exposure to 3 decimals. No TE%, no port/bench context, no σ units label.

Strip (above chart) displays top-4-by-|TE| factors as colored pills — this is effectively a second encoding of the same data sorted differently.

---

## 3. Visualization Choice

### 3.1 Chart / layout type
Horizontal diverging bar (not a true butterfly — single trace, `f.a` only). Comment at L2322–2323 explicitly says "Single-trace diverging bar … not portfolio vs benchmark."

### 3.2 Axis scaling
- **x:** linear, symmetric `[-xmax, +xmax]` with adaptive tick step. Manual `tickvals`/`ticktext` arrays so both sides show positive magnitudes.
- **y:** categorical, reversed autorange. `automargin:true` prevents long factor names from being clipped.
- **Known trap:** the static `height:480px` inline style on the div is overwritten on render to a dynamic height — fine, but if `rFacButt` errors before the assignment, the div remains 480px regardless of factor count.

### 3.3 Color semantics
- Indigo `#6366f1` (positive active exposure, overweight factor)
- Violet `#a78bfa` (negative, underweight)
- Zero-line: `T.zero` ✅ theme-aware
- Grid: `T.grid` ✅ theme-aware
- Font: `T.tick` / `T.tickH` ✅ theme-aware
- **The bar colors themselves are hardcoded hex** — this is inconsistent with the established pattern of `THEME().pos/neg` (documented in AUDIT_LEARNINGS §Viz-renderer pattern, extended 2026-04-20). It also deviates from the dashboard's established green/red semantics for overweight/underweight.
- Meaningful context: `FACTOR_GROUPS` at L1638–L1642 defines per-group colors (Value·Growth indigo, Market Behavior purple, Profitability orange, Secondary neutral). The full-screen version `renderFsFactorMap` correctly uses `facGrpColor(f.n)` to color each marker by its factor group. **This tile ignores that grouping entirely.**

### 3.4 Responsive behavior
- Chart resizes with viewport (`plotCfg.responsive:true`).
- On narrow viewports the half-width `g2` grid reflows — CSS-driven, not bespoke.
- No mobile fallback (table view).

### 3.5 Empty state
`<p style="color:var(--txt);font-size:12px;text-align:center;padding:60px">No factor exposure data</p>` — ✅ correct pattern, writes into the div rather than silently returning. Matches AUDIT_LEARNINGS prescription.

### 3.6 Loading state
None. Plotly renders synchronously once data is in memory; there is no fetch boundary.

---

## 4. Functionality Matrix

**Benchmark tiles:** cardSectors (gold standard table tile), `renderFsFactorMap` (sibling viz that shares the data source).

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort** | ❌ | — | Order is parser output order. No sort-by-|a| or sort-by-TE. |
| **Filter** | ❌ | — | Every factor renders, even near-zero ones. Sibling `cardFacDetail` has Primary/All toggle + group pills — this tile has neither. |
| **Column picker** | N/A | — | Not a table. |
| **Row click → drill** | ❌ | — | **No `plotly_click` handler.** Full-screen version wires `oDrF(name)`; `cardFacDetail` rows are clickable; this tile isn't. |
| **Cell value click** | N/A | — | |
| **Right-click context menu** | 🟡 | global handler | Captures td cells; does nothing on Plotly SVG bars. |
| **Card-title right-click → note** | 🟡 | `showNotePopup` | Not wired — card title has no right-click handler attached. (Many cards have this; cardFacButt doesn't.) |
| **📝 Note badge** | ❌ | `refreshCardNoteBadges` | No badge integration. |
| **Export PNG** | ✅ | `screenshotCard('#cardFacButt')` | Note: user preference is **no PNG buttons** (LIEUTENANT_BRIEF §3). Existing button should be removed as part of any subsequent cleanup; not this audit's job. |
| **Export CSV** | ❌ | — | No CSV button. Sibling `cardFacDetail` has one (`exportCSV('#cardFacDetail table','factors')`). |
| **"Copy factor exposures" (Plotly-tile equivalent of CSV)** | ❌ | — | Proposed: small text button that copies `n,a,c,dev` rows to clipboard. Low effort. |
| **Full-screen modal** | ✅ (indirect) | `openFullScreen('facmap')` on sibling `cardFacDetail` | The sibling card owns the ⛶ button; clicking it opens the *scatter* version, not this diverging-bar view. Mild confusion. |
| **Toggle views** | ❌ | — | No Bar / Scatter / Group toggle, though the data supports both. |
| **Range selector** | N/A | — | Not a time-series tile. |
| **Color-mode picker** | ❌ | — | Could toggle Sign / FactorGroup coloring. |
| **Hover tooltip** | ✅ | Plotly hovertemplate | Shows name + exposure. Could add TE% + σ units for richer context. |
| **Theme-aware (grid/text/zero)** | ✅ | `THEME()` | Grid / tick / zero pull from THEME. |
| **Theme-aware (bar colors)** | ❌ | hardcoded `#6366f1` / `#a78bfa` | Violates AUDIT_LEARNINGS §Viz-renderer pattern. |
| **Theme-aware (strip colors)** | ❌ | hardcoded `#22c55e` / `#ef4444` (L2313–L2315) | Same issue. `var(--pos)` / `var(--neg)` exist. |
| **Color-blind safe** | ❌ | no `_prefs.cbSafe` wiring | — |
| **Top TE strip** | ✅ | `rFacTopTeStrip(s)` at L2305 | Useful context band; only present on this tile. |

### 4.1 Functionality gaps vs benchmarks

| Gap | Severity | Recommendation |
|---|---|---|
| No click-to-drill on bars | **Medium** | Add `document.getElementById('facButtDiv').on('plotly_click', d => oDrF(d.points[0].y))` at the end of `rFacButt`. Mirrors pattern already in `renderFsFactorMap` L5542. 3-line fix. |
| No CSV / copy export | Medium | Add a small "Copy" button next to the PNG button, writing `n\ta\tc\tdev` TSV to clipboard. Or wire `exportCSV` against a hidden `<table>` built from `s.factors`. |
| Bar colors hardcoded | Medium | Replace `'#6366f1'` / `'#a78bfa'` with `T.pos` / `T.neg` (or keep indigo/violet for "exposure direction" semantics, but define them in CSS vars). |
| Strip colors hardcoded | Trivial | Replace `#22c55e` / `#ef4444` with `getComputedStyle(document.body).getPropertyValue('--pos')` / `--neg`, or read through `THEME()`. 4-line fix. |
| No note badge / card-title right-click | Low | Add `oncontextmenu="showNotePopup(event,'cardFacButt')"` on the card-title div. Standard pattern used by other cards. 1-line fix. |
| No factor-group coloring | Low (design option) | Option to color by `facGrpColor(f.n)` instead of sign. Already exists in renderFsFactorMap. |
| No tie to `_facView` (Primary/All) from sibling | Low | Currently `rFacButt` shows every factor regardless of the Primary/All toggle on `cardFacDetail`. Consider honoring the same toggle so both tiles stay in sync. Requires PM decision — listed as open question §7. |
| Hovertemplate missing TE% + σ | Trivial | Extend to `'<b>%{y}</b><br>Exp: %{x:.3f}σ<br>TE: %{customdata[0]}%'`. Requires building `customdata` array. ~6 lines. |
| PNG button present | — | Per LIEUTENANT_BRIEF §3 no-PNG rule, flag for removal in sweep; not in scope for this audit. |

**Section 4 verdict: 🟡 YELLOW** — solid empty-state + theme-aware frame elements, but the tile lags its sibling `renderFsFactorMap` materially on interactivity (no click-drill, no grouping colors) and lags `cardFacDetail` on export. Fixes are small and well-contained.

---

## 5. Popup / Drill / Expanded Card

### 5.1 "Drill" path — indirect

This tile does not open its own modal. The full-screen ⛶ button sits on the sibling `cardFacDetail` and opens `renderFsFactorMap` (scatter, not bar). From inside that full-screen view, clicking a bubble calls `oDrF(name)`.

- **Function:** `oDrF(name, range)` at L4077
- **Modal DOM id:** presumably `#drillModal` / `#facModal` — not audited here (factor drill is its own tile)
- **Registered in ALL_MODALS:** out of scope

### 5.2 Relationship to `renderFsFactorMap`

| Aspect | cardFacButt (`rFacButt`) | Full-screen (`renderFsFactorMap`) |
|---|---|---|
| Chart type | Horizontal diverging bar | Scatter: x=active, y=dev, size=|TE contribution|, color=factor group |
| Filtering | None — all factors plotted | `f.a!=null && f.c>0 && f.dev!=null` |
| Coloring | Sign-based (hardcoded indigo/violet) | Factor-group-based (`facGrpColor`) |
| Click-to-drill | ❌ | ✅ `oDrF` wired |
| Side panel | ❌ | ✅ `#fsPanelContent` — sortable factor list |

The two views are complementary, not redundant, which is good. The opening-control placement (on the neighbor card) is confusing — arguably the ⛶ should also live on cardFacButt.

### 5.3 Missing mirror functionality

- Click-to-drill: present in modal, absent in tile. Users must first open full-screen to drill a factor. **Primary proposed fix.**
- Side panel: out of scope for a half-width card, but the top-TE strip partially compensates.

**Section 5 verdict: 🟡 YELLOW** — drill is reachable, but only via a two-step path. Wiring `plotly_click → oDrF` on cardFacButt closes the gap.

---

## 6. Design Guidelines

### 6.1 Density

| Dimension | Value | Notes |
|---|---|---|
| Chart tick size (x) | 9px | Tight but legible |
| Chart tick size (y) | 10px | Factor names, left-aligned, automargin |
| Chart title | none (card-title "Factor Risk Map" 13px above chart) | ✅ |
| Strip label | 10px uppercase "Top TE Contributors" | ✅ matches dashboard section-header mini-cap pattern |
| Strip pill font | 11px | ✅ |
| Per-factor row height | ~30px (from `facs.length*30+60` formula) | Generous — prevents label clipping. Compare 22px dense rows in table tiles. |
| Card padding | inherited from `.card` class (16px) | ✅ consistent |

### 6.2 Emphasis & contrast

- Bar color carries the signal (indigo = over, violet = under).
- Strip pills use green/red tint + border — a **different** color scheme from the chart itself. This is a cross-visual inconsistency: within the same card the user sees blue/purple bars and green/red pills representing the same positive/negative distinction.
- Zero line is 2px and uses `T.zero` — correctly theme-aware.

### 6.3 Alignment

- Factor names: left-aligned y-axis labels ✅
- Numeric tick labels: mirrored positive on both sides ✅ (unusual but consistent with butterfly convention)
- Strip pills: horizontal flow, gap:6px ✅

### 6.4 Whitespace

- `margin:{l:10, r:20, t:10, b:30}` — tight top/left, slightly loose right. `automargin:true` on y-axis dynamically enlarges left margin for long names. ✅
- Strip-to-chart gap: `margin:4px 0 10px` — appropriate.
- Card-title to export-bar: via `.flex-between` — standard.

### 6.5 Motion / interaction feedback

- Hover: default Plotly tooltip. No bar highlight beyond Plotly's built-in marker opacity change.
- Click: **no affordance** — cursor remains default, no drill, no highlight. This is the single biggest UX tell that interactivity is incomplete.
- Empty state: plain text, no illustration. ✅ matches AUDIT_LEARNINGS prescription.

### 6.6 Inconsistencies worth noting

- Chart uses indigo/violet; strip uses green/red — **same semantics, different colors** within the same card. Pick one.
- Strip hardcodes hex; chart partially uses THEME. Pick one.
- Full-screen sibling colors by factor group, tile colors by sign. Could harmonize.

**Section 6 verdict: 🟡 YELLOW** — dimensionally clean, but the within-card color inconsistency and the dead-bar click affordance hurt polish.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Resolution path |
|---|---|---|---|
| 1 | No click-to-drill on bars | Medium | Wire `plotly_click → oDrF(point.y)`. 3 lines. Trivial. |
| 2 | Bar colors `#6366f1` / `#a78bfa` hardcoded; strip colors `#22c55e` / `#ef4444` hardcoded | Medium | Replace with `THEME().pos` / `THEME().neg` (already extended per AUDIT_LEARNINGS 2026-04-20). Trivial. |
| 3 | Within-card color inconsistency (bars indigo/violet, strip green/red) | Low | Pick one scheme. PM decision. |
| 4 | No isFinite guard on `f.a` | Low | Add `.filter(f => isFinite(f.a))` before mapping. Trivial. |
| 5 | `(f.a??0)` silently coerces missing exposures to zero | Medium | Either filter out null exposures, or distinguish visually (e.g., lighter bar + "n/a" label). PM decision. |
| 6 | No CSV / Copy export | Medium | Add a Copy-to-clipboard button or hidden-table CSV. Non-trivial (UI + handler). |
| 7 | No card-title note-popup right-click | Low | Add `oncontextmenu="showNotePopup(event,'cardFacButt')"`. Trivial. |
| 8 | Hovertemplate bare (no TE%, no σ) | Low | Extend template + customdata. Trivial. |
| 9 | Primary/All toggle on `cardFacDetail` not honored here | Open question | Should the bar chart reflect the sibling's filter? PM decision. |
| 10 | PNG button present (against no-PNG rule) | Cleanup | Out of scope for this audit; flag in global sweep. |
| 11 | Factor-group coloring available (`facGrpColor`) but unused | Low | Optional mode picker. Non-trivial (adds UI). |
| 12 | Full-screen ⛶ lives on sibling card, not this one | Low | Could duplicate. Low impact. |

---

## 8. Verification Checklist

- [x] **Data accuracy**: `f.n`, `f.a`, `f.c` traced to parser `_build_factor_list`. Canonical factor names match FACTOR_GROUPS registry.
- [ ] **Edge cases**: empty-state guard ✅. NaN/Infinity ❌ (no isFinite). Null `f.a` coerced to 0 (ambiguous).
- [x] **Sort**: N/A — parser order preserved. No sort control exposed.
- [x] **Filter**: N/A at tile level; none provided. Every factor plotted.
- [x] **Column picker**: N/A (chart).
- [ ] **Export PNG**: present, but against user preference (no-PNG rule).
- [ ] **Export CSV / Copy**: missing — fix queued.
- [x] **Full-screen modal**: reachable via sibling card (`openFullScreen('facmap')`).
- [ ] **Popup card / drill**: drill wired only from full-screen, not from tile bars. Fix queued.
- [x] **Responsive**: Plotly responsive + dynamic height formula. Good.
- [ ] **Themes**: grid / tick / zero ✅ theme-aware; bar + strip colors ❌ hardcoded.
- [x] **Keyboard**: Escape closes fsModal (inherited).
- [x] **No console errors**: code path is clean (no `.on('plotly_click')` that could throw on purge).
- [ ] **Theme-aware colors**: partial — fix queued.
- [ ] **isFinite guards**: missing on `f.a` — fix queued.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| `cardFacDetail` (sibling, `g2` partner) | Reads same `s.factors`. Owns the ⛶ full-screen button that opens `renderFsFactorMap`. Has Primary/All toggle + group pills + CSV export that this tile lacks. |
| `cardFacTopTE` strip (`facTopTeStrip`) | Co-rendered inline above the chart by the same function. Data: top 4 factors by `|f.c|`. |
| Full-screen Factor Risk Map (`renderFsFactorMap`) | Alternative visualization of same data, with drill wiring this tile lacks. Triggered from sibling's ⛶. |
| Factor drill modal (`oDrF(name, range)` at L4077) | The destination of any click-to-drill. Not wired from this tile today. |
| Factor Attribution Waterfall (Factors tab, later row) | Also reads `s.factors`. Uses `f.imp`/`f.cimp`, not `f.a`. |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Audit v1 — three-track audit of diverging-bar Factor Risk Map tile. Verified empty-state guard, traced data source to parser, documented interactivity gaps (no click-drill, no CSV, hardcoded palette). | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — factor-name + FACTOR_GROUPS authority
- rr-data-validator — §1.4 JSON spot-check pending
- rr-design-lead — §6 within-card color inconsistency sign-off

---

**Sign-off:** Data track GREEN-YELLOW (empty-state correct, but missing isFinite guard and null-coercion ambiguity). Functionality track YELLOW (no click-drill, no export, feature-poor vs siblings). Design track YELLOW (theme violations + within-card color split). Tile is functional and correct-by-data, but 4–5 trivial fixes would meaningfully lift it.

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | 🟢 | Card, render fn, strip, full-screen path all located |
| **1. Data Source** | 🟡 | Source correct, empty-state ✅; missing isFinite guard; null exposures silently zeroed |
| **3. Visualization** | 🟡 | Right chart type + clean axis logic; bar colors hardcoded; factor-group coloring available and unused |
| **4. Functionality** | 🟡 | No click-drill, no CSV/copy, no note-popup right-click, no Primary/All sync — all trivial fixes |
| **5. Drill** | 🟡 | Reachable only via sibling's full-screen path |
| **6. Design** | 🟡 | Within-card color inconsistency (bars indigo/violet vs strip green/red); otherwise clean |

### Fix queue

**Trivial (agent can apply, ≤5 lines each):**
1. Wire `plotly_click → oDrF(point.y)` on `facButtDiv` (~3 lines, mirrors L5542)
2. Replace bar hex `#6366f1`/`#a78bfa` with `T.pos`/`T.neg` or CSS vars
3. Replace strip hex `#22c55e`/`#ef4444` with `var(--pos)`/`var(--neg)`
4. Add `.filter(f => isFinite(f.a))` before `names`/`vals` mapping
5. Add `oncontextmenu="showNotePopup(event,'cardFacButt')"` on card-title
6. Extend hovertemplate with TE% and σ via customdata

**Non-trivial (needs design/PM decision or larger change):**
- CSV/Copy export button (UI + handler)
- Honor sibling's Primary/All filter
- Factor-group coloring mode toggle
- Move (or duplicate) full-screen ⛶ onto this card
- Resolve within-card color-scheme split (PM call)

**Cleanup (out of scope, logged):**
- Remove PNG button per LIEUTENANT_BRIEF §3
