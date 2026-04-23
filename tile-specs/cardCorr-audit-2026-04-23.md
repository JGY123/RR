# Tile Spec: cardCorr — Audit v1

> **Audited:** 2026-04-23 | **Auditor:** Tile Audit Specialist (CLI) | **Batch:** 4
> **Status:** RED — `#cardCorr` is a **ghost tile**: it renders in the Exposures tab as a static placeholder ("Computed from historical factor data — see Risk tab.") that is never populated by any code path. The actual correlation heatmap lives in an **anonymous sibling card** inside the Risk tab (L3096), rendered by `rUpdateCorr()` into `#corrMatrixWrap`. Two UIs, one name; the user-facing tile is non-functional.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Correlation Matrix |
| **Card DOM id** | `#cardCorr` (Exposures tab, L1299) — inert placeholder |
| **Render target (live)** | `#corrMatrixWrap` inside an **anonymous card** in Risk tab (L3096) |
| **Render function** | `rUpdateCorr()` at `dashboard_v7.html:L2136–L2222` |
| **Inner plot id** | `#corrHeatPlot` injected by `rUpdateCorr` at L2199 |
| **Controls (Risk tab only)** | `#corrPeriod` (L3100 — all/3Y/1Y/6M/3M), `#corrFreq` (L3103 — weekly/monthly), `#corrFactorSel` checkbox strip (L3108), `#corrInsights` summary row (L3112) |
| **Data source** | `cs.hist.fac[factorName] → [{d,e,bm,a}, …]` — parser-computed in `factset_parser.py:L938–L949` (`_build_hist_fac`) |
| **Tab** | Exposures (for the ghost placeholder) + Risk (for the live heatmap) |
| **Width** | Full-width in both tabs |
| **Full-screen path** | None |
| **Drill path** | None — heatmap is read-only; no `plotly_click` handler |
| **Owner** | CoS / Tile Audit Specialist |
| **Spec status** | `audit-only` — no edits landed |

---

## 1. Data Source & Schema

### 1.1 Data path (traced)

1. **Parser** `factset_parser.py:L836` writes `s.hist.fac = self._build_hist_fac(riskm_rows)`.
2. `_build_hist_fac` (L938–L949) produces `{factorName: [{d, e, bm, a}, …]}` — one entry per risk-model date per factor, with current-period exposure `e`, benchmark exposure `bm`, and active `a = e-bm`.
3. **Dashboard** `rUpdateCorr()` L2151 reads `s.hist.fac` directly, slices per `corrPeriod`, dedupes monthly if `corrFreq==='monthly'`, then for each factor maps each observation to `h.bm!=null ? +(h.e-h.bm).toFixed(4) : +(h.e||0)` (L2168).
4. **Correlation** is a local `pearson(a,b)` (L2170–L2179) over the sliced series pairwise.

**Net:** this tile is parser-computed-then-discarded-reversed — unlike the cardRanks Pattern B (parser ships aggregate, dashboard re-derives from raw). Here the parser ships raw time-series and the dashboard computes the statistic. That's the healthier direction.

### 1.2 Field domain — **what is being correlated?**

The card title says "Factor Correlation Matrix" and the tooltip says "Factor correlations computed from historical exposure data." Per the code at L2168:
- If `bm` is present on a given observation → use **active exposure** (`e - bm`)
- If `bm` is null → fall back to **raw exposure** (`e`)

Per-observation, per-factor fallback means the correlation can be computed on a **mixed** time series where Factor A is "active" and Factor B is "raw" for the same (i,j) pair — or even where a single factor flips between active and raw across its own history. Same pattern as cardFacDetail's 12-wk sparkline (AUDIT_LEARNINGS §Completed / cardFacDetail §1.3). Cleaner options:
- **(a)** always compute active, skip observations where `bm==null` — symmetric, honest, but loses data for benchmark-free factors
- **(b)** always compute raw exposure — changes the semantic (this would be "factor-exposure correlation" not "active-exposure correlation")
- **(c)** PM call on which — and surface it in the card title/tooltip so the user knows which series is under the hood

Current wording ("factor correlations") is ambiguous enough that both options would pass a PM read — but the calculation should not silently mix them. **B60.**

### 1.3 Correlation method

Local Pearson (L2170–L2179):
- `n = min(a.length, b.length)` — **positional pairing on the first n observations**, not **date-aligned pairing**. If two factors have the same length arrays, OK. If they differ (e.g., a factor entered the risk model mid-history), the shorter window is used from the *start* of both arrays — even though it should be date-aligned. In practice `_build_hist_fac` enumerates `riskm_rows` in date order and appends one entry per factor per date when that factor exists — so arrays are typically aligned at the tail, not the head. **Truncating from the front on `min` instead of date-joining can silently misalign factors with shorter histories.** Real impact depends on data shape — flag for verification with a loaded JSON. **B61.**
- Returns 0 when `n<3` or `denom<1e-10` (zero-variance factor). Silent zero on both failure modes; the cell will just show "0.00" in the heatmap. No warning shown in the cell itself. **B62 (low).**

### 1.4 Field inventory

| Axis / element | Field | Type | Format | Notes |
|---|---|---|---|---|
| x-axis labels | `facNames` (subset of `Object.keys(cs.hist.fac)`) | string[] | raw, rotated -35° | Not truncated; long names spill — margin l=150 / b=110 provides room |
| y-axis labels | same `facNames` | string[] | raw, `autorange:'reversed'` | Same as x (symmetric axes) |
| Cell value `z` | Pearson r | number | `fixed(3)` in pearson, `toFixed(2)` in cell label | `zmin:-1 / zmax:1` — symmetric range, sensible |
| Cell text overlay | `r.toFixed(2)` | string | `textfont:{size:10, color:'#0f172a'}` | **Hardcoded dark text** — works on most cell colors (light-gray midtones, red, indigo) but NOT themed; see §6. |
| Hover | `%{y} × %{x}<br>r = %{z:.3f}` | string | — | ✅ shows both factor pair AND 3-dp value |
| Insight bullets | derived | string[] | injected into `#corrInsights` | `r>0.7` ⚠ high-positive; `r<-0.5` ✓ diversifying. Hardcoded thresholds — see §7. |

### 1.5 Missing / null handling

| Scenario | Behavior | Status |
|---|---|---|
| `cs.hist.fac` absent / all empty | `<p>No factor history available</p>` | GREEN |
| `<2` factors selected via checkboxes | `<p>Select at least 2 factors</p>` | GREEN |
| Any sliced series has `<3` points | `<p>⚠ Insufficient data — need at least 3 data points (have N)</p>` (amber) | GREEN |
| 3–9 points (marginal) | Note shown: `⚠ Only N data points in selected period` | GREEN |
| Self-correlation `f===f` | hard-coded to `1` at L2186 (not computed) | GREEN — correct; avoids NaN when stdev=0 |
| Zero-variance factor (all same value) | `pearson` returns 0 | YELLOW — silent collapse; user sees 0 and can't distinguish from "genuinely uncorrelated" |
| Date misalignment (different factor histories) | positional first-n pairing via `min(a.length,b.length)` | YELLOW — see §1.3 |
| Benchmark flip mid-history (`bm` toggles null↔num) | series silently conflates active and raw | YELLOW — see §1.2 |
| `_selectedWeek` set (historical week) | `hist.fac` is full series regardless — correlation unaffected | GREEN — actually the right behavior; correlation over history doesn't change by pointer to "current" week |

### 1.6 Ground truth verification

- [x] Data path traced: parser populates, dashboard reads directly; no `normalize()` override for `hist.fac`.
- [x] Symmetry: `corrMatrix[i][j] === corrMatrix[j][i]` — both computed independently but from the same inputs, so equal up to floating-point rounding.
- [ ] Spot-check Pearson output against numpy.corrcoef on loaded JSON — **pending** (AUDIT_LEARNINGS §Known blockers).

**Section 1 verdict: YELLOW.** Clean parser→dashboard path with correct empty-state guards and sensible method choice; knocked down by (a) the active-vs-raw fallback silently conflating two series types, (b) positional n-pairing that could misalign factors with mismatched histories, (c) zero-variance and misalignment failures silently render as r=0.

---

## 2. Columns & Dimensions Displayed

Two instances of this tile coexist:

### 2.1 Exposures-tab placeholder (L1299–L1303)
- **Static HTML**, zero dynamic behavior. Inner `#corrMatrixCardArea` contains a single `<p>` directing the user to the Risk tab.
- No render fn ever writes into `#corrMatrixCardArea` (grep confirms the id is referenced only at L1302).
- PNG button at L1301 screenshots an empty card → produces a meaningless image.
- This is **dead UI real estate** that occupies a full-width row in the Exposures tab between cardUnowned (Row 10) and cardAttrib (Row 12).

### 2.2 Risk-tab live card (L3096–L3113)
- **Anonymous** card (no `id` attribute) — cannot be right-clicked for note, cannot be export-ed by id, cannot be deep-linked.
- Contains:
  - Title "Factor Correlation Matrix" (identical to the placeholder in Exposures tab)
  - Period dropdown (all/3Y/1Y/6M/3M)
  - Frequency dropdown (weekly/monthly)
  - **Per-factor checkbox strip** (L3108–L3110) — default-checked = `FAC_PRIMARY` factors only; users can widen to All
  - `#corrMatrixWrap` target div → `#corrHeatPlot` heatmap
  - `#corrInsights` rule-driven bullet summary

### 2.3 Heatmap geometry
- Dynamic height: `Math.max(260, facNames.length * 36 + 80)` — scales with factor count. Good.
- **Full symmetric matrix rendered** (both triangles). Information-theoretically redundant (it's symmetric) but visually familiar; no toggle to collapse to upper/lower triangle. **B63 (nice-to-have).**
- Diagonal is always `1` in indigo — wasteful cell count, no user value.

---

## 3. Visualization Choice

### 3.1 Chart type
Plotly heatmap (`type:'heatmap'`) with in-cell numeric labels (`texttemplate:'%{text}'`). Correct choice for a correlation matrix.

### 3.2 Colorscale
```
[[0, '#ef4444'], [0.5, '#e2e8f0'], [1, '#6366f1']]
```
with `zmin:-1, zmax:1`. **Hardcoded hex** — should use theme tokens. Structure is correct (diverging -1 ↦ 0 ↦ +1) but:
- Positive r is indigo (`--pri` / `#6366f1`) — fine.
- Negative r is red (`#ef4444` / `--neg`) — fine.
- Mid is `#e2e8f0` light gray — same color as `--grid` in light theme. **In dark theme, mid-correlation cells flash light-gray against a dark card background** — readable but visually loud.
- The per-cell text color `#0f172a` (dark slate) is applied uniformly regardless of theme. In dark theme, the light-gray mid-cells with dark text work; the indigo/red edges with dark text drop to ~3:1 contrast at extremes.

**Recommended:** switch to the themed colorscale pattern (AUDIT_LEARNINGS §Themed colorscale pattern — precedent: `mcrDiv`, `teStackedDiv`). Pull `getComputedStyle(document.body).getPropertyValue('--pos'/'--neg'/'--surf')` inside `rUpdateCorr()`, build the colorscale at call time. **B64.**

### 3.3 Label geometry
- X-axis: `tickangle:-35`, `tickfont:{size:10}`, bottom placement. ✅ legible on long factor names.
- Y-axis: no rotation, `tickfont:{size:10}`, `autorange:'reversed'` so y reads top-to-bottom. ✅ conventional for matrices.
- Margins: `l:150, r:60, t:20, b:110` — large enough for ~25-char factor names. ✅
- No truncation applied — if a future factor name > ~28 chars it will overflow; unlikely.

### 3.4 Legend / colorbar
`colorbar:{len:0.9, title:{text:'r', side:'right'}, tickfont:{size:9}, thickness:12}` ✅ compact and labeled.

### 3.5 Responsive behavior
`plotCfg` = `{displayModeBar:false, responsive:true}`. The heatmap div sets an explicit pixel height; on narrow viewports the plot scales horizontally but not vertically — wide factor names on a 480-wide screen would clip. Low priority; this tile is desktop-first.

### 3.6 Empty / insufficient-data states
Four distinct messages (§1.5) handled correctly. GREEN.

---

## 4. Functionality Matrix

**Benchmark:** cardSectors (gold-standard table), cardFacButt (sibling factor viz), cardMCR (sibling heatmap-ish plotly tile).

| Capability | Present? | How invoked | Notes |
|---|---|---|---|
| **Sort** | N/A | — | Not a table. Heatmap row/col ordering is alphabetical by factor name (from `Object.keys(hist.fac)`). No user reorder. |
| **Row / cell click → drill** | ❌ | — | `plotly_click` not wired. Users can't drill into a factor-pair detail. **B65.** |
| **Per-factor filter** | ✅ | `#corrFactorSel` checkboxes | Default = `FAC_PRIMARY` set; users can widen. No persistence — check state is reset on every `rRisk()` (strategy switch, week change, theme toggle). **B66.** |
| **Period filter** | ✅ | `#corrPeriod` dropdown | All / 3Y / 1Y / 6M / 3M. No localStorage persistence. Reset on re-render. |
| **Frequency toggle** | ✅ | `#corrFreq` dropdown | Weekly / Monthly. No persistence. |
| **Column picker** | N/A | — | Not applicable to heatmap. |
| **Export CSV** | ❌ | — | **No CSV export of the underlying correlation matrix.** High-value gap — correlation matrices are the canonical "I want this in Excel" artifact. **B67.** |
| **Export PNG** | Ghost only | `screenshotCard('#cardCorr')` L1301 | The PNG button is on the dead Exposures-tab placeholder; screenshots the empty card. The live Risk-tab card has **no PNG button**. Against the project no-PNG rule anyway — flag for removal. |
| **Full-screen modal (⛶)** | ❌ | — | No FS variant. For a correlation matrix that scales to ~25 factors, FS would substantially improve readability. **B68.** |
| **Card-title right-click → note** | ❌ | — | Neither instance has `oncontextmenu="showNotePopup(event,'cardCorr')"`. Ghost card has `class="tip"` only. Live Risk-tab card has no id at all, so the note infrastructure (keyed by DOM id) cannot attach. **B69.** |
| **Note badge** | ❌ | — | Same root cause — no stable id on the live card. |
| **Tile-wide onclick** | N/A | — | — |
| **Hover tooltip (header)** | Ghost only | `class="tip" data-tip="Factor correlations computed from historical exposure data."` (L1300) | The live Risk-tab card has a plain `card-title` div with no tooltip. Inconsistent with sibling tiles (cardFacButt, cardFacDetail, cardMCR all have header tooltips). **B70.** |
| **Hover tooltip (cell)** | ✅ | `hovertemplate:'%{y} × %{x}<br>r = %{z:.3f}'` | 3-dp precision, shows both factor names. ✅ |
| **Theme-aware** | Partial | `var(--txt)` on period dropdowns, text messages themed | Heatmap colorscale hardcoded hex (§3.2). Text overlay `#0f172a` hardcoded. |
| **Theme rebuild** | Partial | `applyPrefs()` → `upd()` → `rRisk()` → `rUpdateCorr()` | Theme toggle re-renders when the Risk tab is revisited. Light-theme colorscale OK; dark-theme mid-cells are too bright. |
| **Week-selector awareness** | N/A — correct | `hist.fac` is full series, not week-dependent | Correlation over history is invariant to `_selectedWeek`. This is the right behavior; does not need the week banner. |
| **Keyboard a11y** | ❌ | — | No `tabindex`, no `role`, no keyboard entry to any control beyond native `<select>` / `<input>` defaults. Heatmap cells are not focusable (Plotly limitation). |
| **Color-blind safe** | ❌ | — | Red-neutral-indigo diverging is adequate for most red-green color-blind types (indigo ≠ green), but not verified. |

### 4.1 Gaps vs benchmarks

| # | Gap | Severity | Class |
|---|---|---|---|
| B60 | Active-vs-raw fallback at L2168 silently conflates two series types inside the same Pearson computation | **Medium** | Non-trivial (PM call on which series to use) |
| B61 | Positional `min(a.length,b.length)` pairing — not date-aligned — can misalign factors with mismatched histories | **Medium** | Non-trivial (needs date-join refactor of `pearson` or of the slicing step) |
| B62 | Zero-variance factor silently returns r=0 — indistinguishable from genuine no-correlation | Low | Trivial (return `null`/NaN + render "—") |
| B63 | Full symmetric matrix rendered including redundant triangle + diagonal | Low | Non-trivial (UX choice) |
| B64 | Colorscale + in-cell text hardcoded hex — not theme-aware | Medium | Trivial (swap to `getComputedStyle` token lookup; precedent in other Risk-tab tiles) |
| B65 | No `plotly_click` drill — cells are read-only. Clicking a cell could open `oDrF(x)` or a factor-pair detail modal. | Medium | Non-trivial (decide target; no factor-pair detail view exists today) |
| B66 | Filter state (period, frequency, factor checkboxes) not persisted to localStorage | Low | Trivial (5-line `rr.corr.*` save/load) |
| B67 | **No CSV export of correlation matrix or underlying sliced series.** Highest-value feature gap. | **High** | Trivial-medium (custom builder; standard `exportCSV('#table')` doesn't apply to a non-table viz) |
| B68 | No full-screen modal. Matrix readability degrades past ~15 factors. | Medium | Non-trivial (new FS variant + renderer) |
| B69 | Card title has no `oncontextmenu="showNotePopup(event,'cardCorr')"`; live Risk-tab card has no DOM id at all, blocking note infra | Medium | Trivial (add id + handler on the live card; delete or de-dupe the ghost card) |
| B70 | Live Risk-tab card title has no `data-tip` tooltip (the ghost placeholder has one) | Low | Trivial (copy tooltip from ghost) |
| B71 | **Ghost tile: `#cardCorr` (Exposures tab) occupies a full-width row with inert placeholder text pointing users to the Risk tab.** Users see "Factor Correlation Matrix" twice but only one instance works. Either delete the ghost, or populate it by calling `rUpdateCorr()` into `#corrMatrixCardArea`. | **High** | Non-trivial (PM decision: delete vs promote) |
| B72 | Ghost card's PNG button (L1301) screenshots an empty card → produces a meaningless artifact. Not just dead UI; it's misleading output. | Low | Trivial (remove button — aligns with no-PNG rule anyway) |
| B73 | Insight thresholds `r>0.7` / `r<-0.5` hardcoded at L2192–L2193 — not in `_thresholds`. Same anti-pattern as cardFRB `abs(f.a)>0.2` heuristic (AUDIT_LEARNINGS §Hardcoded heuristic thresholds). | Low | Trivial after a `_thresholds.corrHigh` / `_thresholds.corrDiversifier` addition to Settings |

**Section 4 verdict: RED.** The ghost-tile duplication, missing CSV, missing FS, missing drill, missing id, missing note handle, and mixed active/raw series together define a tile that is half-shipped. The live Risk-tab instance is functional but unintegrated with the rest of the dashboard's conventions.

---

## 5. Popup / Drill / Expanded Card

### 5.1 Drill path
**None.** The heatmap has no `plotly_click` handler. Cells are read-only. The closest analog — `oDrF(factorName)` — is per-factor; a correlation cell is per-pair. No factor-pair detail view exists anywhere in the dashboard.

### 5.2 Full-screen path
None. See B68.

### 5.3 Insight row surrogate
`#corrInsights` (L3112 target, L2216–L2221 writer) renders text bullets for `r>0.7` and `r<-0.5` pairs. Bullets are rendered as inline HTML strings — **factor names in the bullet are not clickable**. User cannot click "Profitability & Value r=0.82" to drill into either factor. **B74.**

**Section 5 verdict: RED.** No drill anywhere — not cell, not insight, not factor-level from either.

---

## 6. Design Guidelines

### 6.1 Density

| Dimension | Value | Notes |
|---|---|---|
| Heatmap cell labels | `size:10` | OK; matches 10px density elsewhere |
| Axis tick font | `size:10` | ✅ |
| Colorbar tick | `size:9` | ✅ |
| Period / freq selects | `font-size:11px, padding:3px 6px` | ✅ matches toolbar density |
| Factor checkbox labels | `font-size:11px, padding:2px 6px` | ✅ |
| Card-level padding | Inherits `.card` | ✅ |
| Heatmap min-height | 260px; scales at 36px/factor + 80px base | ✅ |

### 6.2 Emphasis & contrast

- Heatmap cell text `color:#0f172a` **hardcoded**. In dark theme this renders dark text on:
  - Mid-value cells (r≈0, bg `#e2e8f0` light gray): high contrast ✅
  - Max-positive cells (r≈1, bg `#6366f1` indigo): ~3:1 — marginal
  - Max-negative cells (r≈-1, bg `#ef4444` red): ~4:1 — OK
  - In light theme all above still work; but the dark-slate text is the wrong tonality on a light overall theme (should be theme-derived)
- Diverging scale has a clear zero point (light gray) — ✅ the direction info is preserved for color-blind users (indigo vs red, not green vs red).

### 6.3 Alignment
- Axis labels default-aligned (x rotated bottom, y right-justified). ✅ conventional.
- Colorbar on the right. ✅
- Insight bullets inside `#corrInsights` left-aligned inside a `background:var(--surf)` chip. ✅

### 6.4 Whitespace
- Controls: `gap:8px` horizontal. ✅
- Factor-select strip has 8px bottom margin + 1px border-bottom separator. ✅
- Insight row has 8px top margin. ✅

### 6.5 Motion / interaction feedback
- No per-cell hover highlight beyond Plotly's default tooltip. ✅ sufficient.
- Period / freq dropdowns re-render immediately on change (0-setTimeout Plotly build). ✅ responsive.
- Factor-checkbox toggle re-renders the entire heatmap — not incremental. For 20+ factors this is ~100ms; noticeable but tolerable.

### 6.6 Cross-tile design debts surfaced here

- **Colorscale hardcoded hex** — same pattern as the older viz tiles. Now 4+ viz tiles need a themed colorscale refactor (see AUDIT_LEARNINGS §Themed colorscale pattern).
- **Anonymous Risk-tab cards** — cardCorr is the second Risk-tab card without an `id` attribute (along with the Factor Exposure History card at L3083). Without ids, `showNotePopup` can't target them, `screenshotCard` can't crop them, and future CSV/FS wiring has no handle. **Cross-tile recommendation:** give every card a stable `id` as a project-wide convention. Likely a 10-line sweep.
- **Ghost placeholder pattern** — the `#cardCorr` Exposures-tab div is unique: a visible, named card whose `innerHTML` is never replaced by any render fn. I haven't seen this exact pattern elsewhere in the audited tiles. Worth adding to AUDIT_LEARNINGS as a distinct anti-pattern if any other ghosts exist — grep for `id="card*"` that never get `innerHTML=` or interpolated into a render template.

**Section 6 verdict: YELLOW.** Geometry, density, and alignment are clean. Pulled down by hardcoded-hex colorscale + in-cell text color, and by the anonymous Risk-tab card lacking a stable handle.

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Class | Resolution path |
|---|---|---|---|---|
| B60 | Active-vs-raw fallback mixes two series types in the same Pearson | Medium | Non-trivial | PM decides: always active (drop no-bm obs) vs always raw (rename tile) vs toggle |
| B61 | Positional `min(a.length,b.length)` pairing can misalign factors with mismatched histories | Medium | Non-trivial | Date-join the two series before Pearson; falls back to current behavior when equal-length |
| B62 | Zero-variance factor → silent `r=0`, indistinguishable from "no correlation" | Low | Trivial | Return `null` from `pearson`; render "—" in cell |
| B63 | Full symmetric matrix — redundant triangle + diagonal | Low | Non-trivial | Add a "Half / Full" toggle; no code precedent in repo |
| B64 | Heatmap colorscale + `#0f172a` text hardcoded hex | Medium | Trivial | Themed-colorscale pattern (`getComputedStyle`) at call time |
| B65 | No `plotly_click` drill on cells | Medium | Non-trivial | Needs factor-pair detail view (currently none exist) |
| B66 | Period / freq / factor-checkbox state not persisted | Low | Trivial | localStorage `rr.corr.{period,freq,facs}` |
| B67 | **No CSV export** of the correlation matrix | **High** | Trivial-medium | Custom builder: iterate `facNames × facNames`, write header + rows |
| B68 | No full-screen modal | Medium | Non-trivial | Mirror `openFullScreen('facmap')` pattern |
| B69 | No `oncontextmenu="showNotePopup(event,'cardCorr')"` on card title; live Risk-tab card has no DOM id at all | Medium | Trivial (once id exists) | Add `id="cardCorr"` to live card + add handler; or dedupe with ghost |
| B70 | Live Risk-tab card title has no `data-tip` tooltip | Low | Trivial | Copy tooltip from Exposures-tab ghost |
| B71 | **Ghost tile: `#cardCorr` in Exposures tab is a placeholder pointing to Risk tab** — full-width dead real estate | **High** | Non-trivial | PM call: (a) delete the ghost from Exposures, or (b) populate `#corrMatrixCardArea` by moving `rUpdateCorr()` to also render there |
| B72 | Ghost card's PNG button screenshots an empty card | Low | Trivial | Remove; aligns with no-PNG rule |
| B73 | Insight thresholds `r>0.7` / `r<-0.5` hardcoded | Low | Trivial after `_thresholds.corrHigh`/`corrDiversifier` wiring | Move to `_thresholds` so Settings can tune |
| B74 | Insight bullets render factor names as inert HTML — not clickable | Low | Trivial | Wrap names in `<a onclick="oDrF('…')">` |
| B75 | `hasFacData` check (L2152) uses `Object.values(facHist).some(v=>v.length>0)` — passes if ANY factor has history. A factor with zero observations but others with full history will silently appear in the matrix with Pearson returning 0 against every neighbor. Recommend filtering `facNames` to those with `≥3` observations before building the matrix. | Low | Trivial |
| B76 | "hist.fac" assumption about weekly cadence is implicit — `corrFreq:'monthly'` dedupes by `h.d.slice(0,7)` picking the **first-seen** monthly observation (L2165–L2167), not e.g. month-end. OK if `hist.fac` is chronologically ordered (which it is by parser construction) — but worth an inline comment. | Low | Trivial (comment) |
| B77 | Decision not yet documented anywhere: should the "Factor Correlation Matrix" be correlation of (a) factor **active exposures over time**, (b) factor **returns over time**, or (c) factor **contributions to portfolio TE over time**? Per current code it's (a) — but PMs often assume (b) or (c). Tile title + tooltip should name the domain explicitly. | Medium | Trivial | Rename: "Factor Active-Exposure Correlation" + clarify tooltip |

---

## 8. Verification Checklist

- [x] **Data accuracy:** parser→dashboard path traced; `hist.fac` populated; no `normalize()` override.
- [🟡] **Edge cases:** empty ✅, `<3` points ✅, `<2` factors ✅, zero-variance silently 0 🟡, misaligned histories positionally paired 🟡.
- [N/A] **Sort:** not a table.
- [x] **Filter — period / freq / factor checkboxes:** all wired; re-render on change.
- [ ] **Filter persistence:** not persisted.
- [N/A] **Column picker.**
- [ ] **Export CSV:** missing.
- [ ] **Export PNG:** present on ghost only; against project rule.
- [ ] **Full-screen modal:** none.
- [ ] **Drill (cell / insight):** none.
- [x] **Responsive:** scales vertically with factor count; desktop-first; no mobile fallback.
- [🟡] **Themes:** text / card / control chrome themed; heatmap colorscale + in-cell text hardcoded.
- [x] **Week-selector awareness:** N/A — correlation is history-invariant.
- [x] **No console errors:** none observed via static read.
- [ ] **Card-title right-click → note:** not wired; live card has no id.
- [ ] **Hover tooltip (header):** missing on live card.
- [x] **Hover tooltip (cell):** wired, 3-dp.
- [x] **Empty states rendered into the card:** yes (wrap.innerHTML path).
- [ ] **Keyboard a11y:** Plotly default only.

---

## 9. Related Tiles

| Tile | Relationship |
|---|---|
| **`#cardCorr` (Exposures tab, L1299)** | **Ghost** placeholder; never populated. Either delete or promote. |
| Factor Correlation card in Risk tab (L3096, anonymous) | The live heatmap. Needs `id="cardCorr"` to integrate with note / screenshot / CSV infrastructure. |
| `cardFacDetail` (L1163) | Same `hist.fac` data source; same active-vs-raw fallback pattern in the 12-wk sparkline (L2168 here, L1764 there). Cross-tile sparkline/correlation harmonization candidate. |
| `cardFacButt` (L1158) | Sibling factor view; uses `s.factors` (current) not `hist.fac`. |
| `oDrF(factor)` drill (L4091) | Hardcodes "Factor correlations (no data)" at L4157 — there was presumably once a plan to render per-factor correlations inside the factor drill. Stub never developed. Potential integration target for B65. |
| `cardFRB` (L1284) | Sibling Risk-tab factor viz. Has `oncontextmenu`+`tabindex`+`role="button"`; cardCorr has none of these. |
| Factor Exposure History card (Risk tab L3083) | Sibling anonymous Risk-tab card. Share the same `id`-missing design debt. |

---

## 10. Change Log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Audit v1 — three-track audit of Factor Correlation Matrix. Surfaced ghost-tile duplication (`#cardCorr` inert placeholder in Exposures tab; live heatmap lives in an anonymous Risk-tab card). Traced parser→dashboard data path (healthy). Documented active-vs-raw series conflation, positional n-pairing mis-alignment risk, hardcoded colorscale, missing CSV, missing FS, missing drill, missing note handle, missing id. 18 numbered findings B60–B77. | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — authority on "what is being correlated" (§1.2 / B77 PM decision)
- rr-data-validator — §1.6 spot-check Pearson against numpy; verify B61 date-alignment impact on loaded data
- rr-design-lead — §3.2 colorscale theming + §6.6 anonymous-card convention

---

**Sign-off:** Data track YELLOW (healthy parser→dashboard path; active-vs-raw conflation, positional pairing, zero-variance silent-zero knock it from GREEN). Functionality track RED (ghost placeholder, no CSV, no FS, no drill, no id on live card, no note handle). Design track YELLOW (clean density and alignment; hardcoded heatmap colorscale + text; two anonymous Risk-tab cards need stable ids).

## Summary

| Section | Verdict | Notes |
|---|---|---|
| **0. Identity** | YELLOW | Tile is split across two tabs; placeholder vs live. Live card has no DOM id. |
| **1. Data Source** | YELLOW | Parser→dashboard path clean; active-vs-raw series mix; positional n-pairing risk; zero-variance silent-0. |
| **2. Columns / Dimensions** | YELLOW | Ghost tile is dead real-estate; live heatmap renders full symmetric matrix including redundant triangle + diagonal. |
| **3. Visualization** | YELLOW | Correct diverging heatmap; hardcoded colorscale + text color; tight label geometry. |
| **4. Functionality** | **RED** | Ghost duplication, no CSV, no FS, no drill, no id, no note, no hover tooltip on live. |
| **5. Drill** | RED | None anywhere (cell, insight bullet, or factor link). |
| **6. Design** | YELLOW | Clean density; theme-aware chrome but hardcoded heatmap palette; anonymous cards lack ids. |

**Overall severity: RED.** Two user-facing problems dominate — (a) the ghost tile (B71) visibly promises a feature that lives elsewhere, confusing users before they even look at the heatmap, and (b) the missing CSV (B67) means the most canonical-to-Excel Risk-tab artifact can only be exported via PNG screenshot of a Plotly canvas. Everything else is fixable in a single focused session.

### Fix queue

**Trivial (agent can apply, ≤5 lines each):**
1. **B69/B70/B72:** Add `id="cardCorr"` to the live Risk-tab card (L3096); add `oncontextmenu="showNotePopup(event,'cardCorr');return false"` and a `data-tip` tooltip to its title. Then **delete the ghost `#cardCorr` from the Exposures tab** (L1298–L1303) — or at minimum delete its PNG button.
2. **B64:** Replace hardcoded `colorscale:[[0,'#ef4444'],[0.5,'#e2e8f0'],[1,'#6366f1']]` and `textfont:{color:'#0f172a'}` with `getComputedStyle`-derived theme tokens at call time.
3. **B62:** Return `null` from `pearson` when `n<3` or `denom<1e-10`; render "—" in cell rather than `0.00`.
4. **B66:** localStorage persistence for `corrPeriod` / `corrFreq` / `corrFactorSel` under `rr.corr.*`.
5. **B70 (if keeping both cards):** add `data-tip="…"` to the live card title matching the Exposures-tab tooltip.
6. **B74:** wrap insight-bullet factor names in `<a onclick="oDrF('…')">` for drill from insights.
7. **B75:** filter `facNames` to series with `≥3` observations before building the matrix.
8. **B76:** inline comment in `rUpdateCorr` noting monthly dedupe is first-seen per month, assumes chronological order.
9. **B73 (partial):** add `_thresholds.corrHigh=0.7` / `_thresholds.corrDiversifier=-0.5` fields; swap the L2192–L2193 comparisons. (Settings-UI wiring can follow.)

**Trivial-medium:**
10. **B67:** CSV export of correlation matrix — custom builder (not standard `exportCSV`) since the matrix is not a `<table>`. 15–25 lines.

**Non-trivial (PM decision or larger change):**
11. **B60:** decide active-vs-raw policy; likely always-active with skip-null, and rename tile to "Factor Active-Exposure Correlation" (B77).
12. **B61:** date-join factors before Pearson rather than positional pairing.
13. **B63:** half/full-triangle toggle.
14. **B65:** factor-pair drill — needs a new pair-detail view; currently no dashboard surface for this.
15. **B68:** full-screen modal — new renderer.
16. **B71:** PM call — delete ghost vs promote it by calling `rUpdateCorr()` into `#corrMatrixCardArea`.
17. **B77:** tile rename + tooltip clarification once B60 is settled.

**Cleanup (out of scope, logged):**
- Ghost PNG button (B72) — remove per no-PNG rule regardless of B71 outcome.
- Anonymous Risk-tab cards lacking `id` attributes (cardCorr live + Factor Exposure History L3083) — add ids as a project-wide convention in a separate sweep.
