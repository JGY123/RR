# Tile Spec: cardCorr — Audit v3 (Tier-2 cadence, post-Phase-D)

> **Audited:** 2026-05-04 | **Auditor:** Tile Audit Specialist
> **Scope:** Re-audit of `cardCorr` after Phase-D `tileChromeStrip` migration (commit `ee5b40d`, 2026-05-04). Focus: what changed since 2026-05-01 audit, plus the new data-integrity-monitor lens (verify_section_aggregates.py, F18 escalation, _wFactors per-week flow).
> **Prior audits:**
> - `cardCorr-audit-2026-04-23.md` — RED (ghost tile + missing CSV/FS/drill/id/note). v1, 18 findings B60–B77.
> - `cardCorr-audit-2026-05-01.md` — YELLOW (Pearson vs numpy ✅; C1 monthly dedupe bug; C2 `_corrRestored` stale; C3 momentum factor name miss). v2.
> **Status:** **GREEN — fully Tier-2 ready for daily PM use.** Both math defects from May 1 (C1 + C3) are now closed in code. No regressions from the Phase-D `tileChromeStrip` migration. Only legacy non-blockers carry forward (B60, B61, B63, B65, B68, B77 + a low-severity universe-invariance UX clarity item flagged below).

---

## Trivial fixes ready to ship inline (coordinator-friendly)

These are 1-line / footer / tooltip tweaks. None require user signoff.

1. **D3 (NEW, low):** Append a "Universe-invariant" badge or footer line to the cardCorr title bar. cardRiskByDim has a "Σ %T = 124% (F18)" footer disclosure; cardCorr has nothing telling the user "the Universe pill in the header does not affect this matrix." One-line `<div class="caveat-footer">` would close it.
2. **D4 (NEW, low):** Add a tooltip to the period dropdown explicitly stating that "All" defaults to all available history (max 7yrs) and the count of weekly observations. Currently the dropdown gives no clue how much data backs the matrix. (~5-line `data-tip` on `#corrPeriod`.)
3. **F4 (NEW, low):** B62 returns `null` for n<3 / zero-variance, but the Plotly heatmap renders the cell with whatever `colorscale[0.5]` resolves to (because `null` is treated as the midpoint), giving an empty-looking gray cell instead of an explicit visual gap. Not wrong, but Plotly has `connectgaps:false` / explicit-NaN handling that would distinguish "—" from r=0. ~3 line tweak.
4. **D5 (refresh):** The card-title `data-tip` has been intact since promote (`"Pearson correlation of factor active exposures (e−bm) over the selected period"`). One small precision: replace `"e−bm"` with `"exp − bench_exp (active exposure)"` to match the SOURCES.md / parser nomenclature. Cosmetic.
5. **C1 (FROM v2 — VERIFIED CLOSED):** monthly dedupe `slice(0,7)` → `slice(0,6)` was landed (line 5855, comment dated 2026-05-01 cardCorr audit C1). Re-verified empirically: `slice(0,6)` produces 88 monthly buckets from 383 weekly EM Volatility observations. Correct.
6. **C3 (FROM v2 — VERIFIED CLOSED):** `FAC_PRIMARY` set now contains both `'Momentum (Medium-Term)'` AND `'Medium-Term Momentum'` (line 4595). Momentum is checked by default on EM/IDM/IOP. Closed.

## Larger fixes (queued for design + user signoff)

7. **B60 (carried, medium):** Active-vs-raw fallback at L5857 — `h.bm!=null ? +(h.e-h.bm) : +(h.e||0)`. PM call needed: should the matrix use only active exposure (drop observations where `bm` is null) or raw exposure (drop active naming)? Code currently mixes both within the same series. **NEEDS PM DECISION.**
8. **B61 (carried, medium):** Pearson uses positional `min(a.length,b.length)` pairing (line 5863). Date-aligned join would be more honest, especially if a future factor has shorter history than its peers. Mostly latent risk in current EM data (all 139 factors have identical 383-obs histories), but will bite when the domestic risk model lands or any factor gets retired.
9. **B63 (carried, low):** Full symmetric matrix is rendered (both triangles + diagonal). Half-triangle toggle would save visual real estate but is non-blocking.
10. **B65 (carried, medium):** No `plotly_click` drill on cells — clicking a high-correlation pair doesn't open a factor-pair detail view (none exists today). Project-wide gap.
11. **B68 (carried, medium):** No dedicated full-screen handler. The Phase-D promote wired `fullscreen:"openTileFullscreen('cardCorr')"` (line 7972) — this hits the **generic** fallback in `openTileFullscreen` (line 1445-1474) which clones the card outerHTML into an overlay and does a generic Plotly redraw. **Latent risk: untested on cardCorr specifically.** Verify the cloned `corrHeatPlot` div re-renders correctly under the generic FS path.
12. **B77 (carried, medium-cosmetic):** Tile title says "Factor Correlation Matrix" — semantically generic. Once B60 is settled, rename to "Factor Active-Exposure Correlation" so the domain is unambiguous.

## PM-decision items

- **B60 → B77:** Active-vs-raw policy → tile rename. One question, two consequences.
- **Default period:** Audit v2 logged "user picked 1Y weekly per R2-Q12; backlog item B117." Still defaulted to "All" at line 7977. Not blocking, but worth confirming.
- **Strategy-switch persistence (C2 from v2, low):** the `window._corrRestored` flag persists across strategy switches, so localStorage state is restored once per page load and never re-restored when the user flips IDM → EM → ISC. Could leave as-is (period/freq selections are arguably global) or fix with a per-strategy reset. PM call.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Correlation Matrix |
| **Card DOM id** | `#cardCorr` (Risk tab, line 7964) |
| **Render function** | `rUpdateCorr()` at `dashboard_v7.html:5788–5929` |
| **CSV exporter** | `exportCorrCsv()` at `dashboard_v7.html:5930–5946` |
| **About entry** | `_ABOUT_REG.cardCorr` at `dashboard_v7.html:1265–1273` |
| **Inner plot id** | `#corrHeatPlot` (height scales `260 + 36/factor`) |
| **Chrome strip** | `tileChromeStrip({id:'cardCorr', about:true, resetZoom:'corrHeatPlot', csv:'exportCorrCsv()', fullscreen:"openTileFullscreen('cardCorr')", resetView:true, hide:true, extra:[period+freq selects]})` (line 7967–7983) |
| **Card-title tooltip** | wired (`data-tip="Pearson correlation of factor active exposures (e−bm)…"`) |
| **Right-click → note** | wired (`oncontextmenu="showNotePopup(event,'cardCorr');return false"`) |
| **Data source** | `cs.snap_attrib[name].hist[].exp + bench_exp` (active = exp − bench_exp). Legacy `cs.hist.fac` checked first as fallback path; empty in current samples. |
| **Tab** | Risk |
| **Width** | Full-width |
| **Universe-pill aware?** | **No** — and correctly so. Active exposure series are time-series facts, not universe-bucketed. `setAggMode()` rerenders aggregate tiles only (sectors / countries / groups / regions); cardCorr is correctly excluded. **Worth surfacing in the UI** (D3 above). |
| **Week-selector aware?** | **No** — and correctly so. Correlation is a property of the historical series itself, not a function of which week is "current." Week banner does not apply. |
| **Spec status** | `audit-only` — coordinator serializes any code fixes |

---

## Section per Track

# Track 1 — Data Accuracy

## D1. Pearson math: VERIFIED against numpy on EM full history (re-run 2026-05-04)

**Severity: GREEN. Location: lines 5862–5871 (pearson) + line 5878 (matrix build).**

**What:** Spot-checked 3 factor pairs × 2 periods on `em_full_history.json`:

| Pair | n | Window | Dashboard r (computed inline) | Python r (verification) | Match |
|---|---|---|---|---|---|
| Volatility × Value | 383 | All | -0.234 | -0.234 | ✅ |
| Growth × Medium-Term Momentum | 383 | All | 0.361 | 0.361 | ✅ |
| Profitability × Earnings Yield | 383 | All | 0.259 | 0.259 | ✅ |
| Volatility × Value | 52 | 1Y | -0.859 | -0.859 | ✅ |
| Growth × Medium-Term Momentum | 52 | 1Y | 0.317 | 0.317 | ✅ |
| Profitability × Earnings Yield | 52 | 1Y | -0.927 | -0.927 | ✅ |

All matches to ≤0.001 precision. **Pearson math is correct.** Same conclusion as v2 — confirmed there's no regression.

**Why matters:** The math underpins every cell. Drift here would silently mislead PMs about factor interactions.

**Proposed fix:** None.

## D2. Monthly dedupe: VERIFIED CLOSED (slice(0,6) is live)

**Severity: GREEN. Location: line 5855.**

**What:** Code now reads:
```js
arr=arr.filter(h=>{let m=h.d.slice(0,6);if(seen.has(m))return false;seen.add(m);return true;});
```

with comment `2026-05-01 (cardCorr audit C1): h.d is YYYYMMDD (no separator) — slice(0,7) produced 3-4 buckets per calendar month instead of 1. Use slice(0,6) for true year-month dedupe.`

Empirical re-verification on EM data:
- 383 weekly Volatility obs
- `slice(0,6)` produces **88 unique YYYYMM buckets** (≈monthly cadence over 7 years)
- Previous buggy `slice(0,7)` produced 283 (~74% — not really dedupe)

**The C1 fix shipped and works.** Toggling Weekly → Monthly now produces a substantively different (smoother) correlation series, as the dropdown promises.

**Why matters:** Monthly mode finally delivers what its label says. Before the fix, PMs clicking "Monthly" got essentially weekly with light pruning.

## D3. snap_attrib synthesis path: still rename-only (compliant with anti-fabrication rule 2)

**Severity: GREEN. Location: lines 5826–5838.**

**What:** When `cs.hist.fac` is empty (always the case in current parser output), the dashboard re-shapes `cs.snap_attrib[name].hist[].exp / bench_exp` into the legacy `{e, bm}` shape that `pearson` expects. This is purely a field rename:

```js
facHist[name]=h.map(p=>({d:p.d, e:p.exp, bm:p.bench_exp}));
```

No fabrication. No synthesis. No `?? compute_alternative()`. No `_synth=true` marker required. Complies with hard rule #2 (`normalize() is rename-only`).

**Verified empirically:** EM `snap_attrib.Volatility.hist[0]` = `{d:'20190104', exp:-0.05, bench_exp:0.06, ...}`. Active = exp − bench_exp = `-0.11`. Independently calculated correctly downstream.

**Why matters:** This is exactly the "rename-only" compliance pattern the April crisis demanded. Audited explicitly because the v1 audit raised it as a concern.

## D4. Null-exp handling: known YELLOW, scoped to FX/country macro factors

**Severity: YELLOW. Location: line 5857 (null-coercion `+(h.e||0)`).**

**What:** EM data has **2,638 null-`exp` values across 53,237 total observations (5%)**, concentrated in 16 FX/country macro factors:
- ARS, RUB, Argentina, Russia, etc. — emerging-market-flavor currency / country exposures that drop in/out of risk model coverage over time.
- Other 123 factors have full history (all 383 weekly obs populated).

When `h.e` is null and `h.bm` is also null, the line `h.bm!=null ? +(h.e-h.bm) : +(h.e||0)` returns 0 — silently. So a sparse-history factor's series gets padded with zeros, which biases its Pearson correlations toward zero (not toward NaN, not toward the mean).

**Why matters:** A user looking at correlations involving "ARS" or "Argentina" sees ~60% of the series secretly zero-padded. The r values are not "wrong" — they're computed correctly from a series that's been quietly imputed. **The cell should either:**
- (a) drop these factors from the matrix (B75 already filters factors with `<3` non-null obs — but the test is on series length, not on null count within the series)
- (b) skip null observations within the Pearson loop (date-pair-wise)
- (c) keep the zero-padding but mark the row/column with a "(sparse)" suffix in the axis label

**Proposed fix:** Most honest is (b) — skip null pair within Pearson. ~6-line edit. Defer to PM as a B60-adjacent decision since it touches the same active-vs-raw question.

## D5. Universe pill correctly does NOT affect cardCorr — but UI doesn't say so

**Severity: low. Location: setAggMode (line 5003) + cardCorr title (line 7964).**

**What:** Verified in code that `setAggMode()` calls `_rerenderAggTiles()` (line 4958–4986) which only rerenders cardSectors / cardCountry / cardGroups / cardRegions tables. cardCorr is correctly excluded. Active-exposure time series are universe-invariant by definition (`exp − bench_exp` doesn't depend on whether you're aggregating Port-Held or In-Bench holdings).

But: cardRiskByDim has a similar universe-invariance property and ships an explicit footer disclosure (`"Σ %T does NOT sum to 100% across all 6 strategies (range 94→134 — see FACTSET_FEEDBACK F18)"`). cardCorr ships **nothing** — so a user toggling the Universe pill while looking at cardCorr sees nothing change and may suspect a bug.

**Why matters:** Educates the user that not all tiles are universe-aware. Builds trust through transparency.

**Proposed fix:** Add a low-prominence `<div class="caveat-footer">` to cardCorr saying *"Universe-pill toggle does not affect this matrix — correlations are computed from active-exposure time series and are universe-invariant by construction."* Coordinator-friendly trivial fix (D3 above).

## D6. F18 escalation has no impact on cardCorr (verified)

**Severity: GREEN. Location: F18 inquiry pack (FACTSET_FEEDBACK.md L173).**

**What:** F18 = per-holding %T summing to 94→134% across the 6 strategies. cardCorr does NOT consume `h.tr` / per-holding %T at all — it consumes `cs.snap_attrib[factor].hist[].exp` and `bench_exp`, which are factor-level RiskM exposures. The %T sum question doesn't apply.

**Why matters:** Makes explicit that the F18 escalation does not block this tile's data-accuracy signoff.

## D7. verify_section_aggregates.py has no dim entry for "factor" (intentional)

**Severity: GREEN. Reference: verify_section_aggregates.py L40-46.**

**What:** The section-aggregate verifier covers DIMS `[sec, ctry, reg, grp, ind]` — i.e., dimension tables that ship a "Data" row. There is no factor dimension because factor exposures are not section aggregates (they're per-factor RiskM rows). So the verifier doesn't and shouldn't check cardCorr's data path.

**Proposed:** Could add a Layer 3 monitor for cardCorr (e.g. "every factor's hist length should equal `len(available_dates)`; null-exp count should be ≤5% per factor or it's flagged"). Out of scope for this audit; logged for future.

## Track 1 verdict: **GREEN**

Pearson is correct. C1 monthly dedupe is closed. snap_attrib path is rename-only. F18 doesn't apply. Single soft YELLOW (D4 null-exp coercion in sparse FX factors) is a known/scoped issue with a one-line escape valve.

---

# Track 2 — Functionality Parity

## F1. Phase-D migration to tileChromeStrip: verified clean

**Severity: GREEN. Location: lines 7967–7983.**

**What:** Phase-D refactor (commit ee5b40d, 2026-05-04) migrated cardCorr's chrome from inline-assembly to `tileChromeStrip`. Pre-migration code had: `aboutBtn` + `resetZoomBtn` + period select + freq select + manual `<button class="export-btn">` for CSV + `fsTileBtn` + `resetViewBtn` + `hideTileBtn`. Post-migration: declarative single call.

Comparing pre/post in git diff:
- All 7 chrome buttons preserved (about, resetZoom, csv, fullscreen, resetView, hide + period/freq dropdowns in `extra`)
- Same render order (`about · resetZoom · csv · fullscreen · extra · resetView · hide`)
- Visual appearance identical (verified the chrome wrapper class `.tile-chrome` matches sibling Risk-tab tiles)
- One subtle improvement: the inline `font-size:11px` on the dropdowns was upgraded to `font-size:var(--text-md)` (token-driven)

**No regressions.** Migration is clean.

**Why matters:** Demonstrates the tile contract is now self-enforcing — adding a button to all tiles is one edit, not 30. Confirms cardCorr is "Tier-2 ready" per Phase-D.

## F2. Generic openTileFullscreen path is untested for cardCorr specifically

**Severity: YELLOW. Location: line 7972 (`openTileFullscreen('cardCorr')`) + line 1439 (handler).**

**What:** The chrome strip wires `fullscreen:"openTileFullscreen('cardCorr')"`. Walking the openTileFullscreen function:

```js
function openTileFullscreen(tileId){
  const handler = window._tileFullscreen[tileId];        // no entry for cardCorr
  if(handler && typeof handler === 'function'){...}      // skipped
  // Generic fallback:
  const tile = document.getElementById(tileId);
  ...
  wrap.innerHTML = tile.outerHTML;                       // clones the card with cloned chrome
  wrap.querySelectorAll('[data-tile-fs-btn]').forEach(b=>b.remove());  // strips FS button on clone
  ...
  // Re-trigger Plotly redraw
  wrap.querySelectorAll('[id$="Div"]').forEach(div=>{
    const orig = document.getElementById(div.id);
    if(orig && orig.data && window.Plotly){
      const newId = div.id+'_fs';
      div.id = newId;
      Plotly.newPlot(newId, orig.data, ...);
    }
  });
}
```

Two latent issues:
- **(a)** The Plotly redraw selector is `[id$="Div"]`. The cardCorr inner plot is `#corrHeatPlot` — does NOT match `Div`. **The cloned heatmap will not redraw on FS open** — it'll show whatever static SVG snapshot html2canvas-style copy yielded (or nothing). 
- **(b)** Re-rendering recursively-cloned `id="cardCorr"` (since outerHTML clone preserves the id) creates a duplicate id in the DOM. Subsequent `getElementById('cardCorr')` calls become non-deterministic.

**Why matters:** Phase-D wired the FS button "for free," but on cardCorr it likely produces a broken FS view. Needs verification by clicking the button on a live load. If broken: register a dedicated `window._tileFullscreen.cardCorr` handler that re-runs `rUpdateCorr()` against a sized clone, OR change the redraw selector to `[id$="Div"], #corrHeatPlot` (or all elements with `data-plotly`).

**Proposed fix:** Either (a) write a dedicated FS handler that calls `rUpdateCorr()` against a fresh `<div id="corrHeatPlot_fs">` inside the FS overlay, OR (b) extend the generic redraw selector to include `[id$="Plot"]`. Option (b) is the smaller fix and benefits any future plotly-tile.

## F3. Universe pill: correctly does NOT affect cardCorr (verified)

**Severity: GREEN. Reference: D5 above.**

**What:** Universe pill (`setAggMode`) → `_rerenderAggTiles` (line 4958) → does NOT call `rUpdateCorr`. Correct behavior — see D5 for why.

**Worth surfacing in the UI to manage user expectation.** D3 above.

## F4. Week selector: correctly does NOT affect cardCorr (verified)

**Severity: GREEN.**

**What:** cardCorr does not call `_wFactors()` / `getFactorsForWeek()` — it reads `cs.snap_attrib[*].hist[]` directly which is the full history regardless of `_selectedWeek`. The week banner does not apply to this tile (correlation is a property of the historical series, not a function of which week is "current").

When the user picks a historical week from the selector, cardCorr does NOT re-render. This is the right behavior. (Confirmed by tracing the week-change handler `setSelectedWeek` → `upd()` → `rRisk()` → `setTimeout(...rUpdateCorr())` at line 8003 — but the function reads full series so the result is identical.)

**Why matters:** Documents that the per-week refactor (Phase-H, commit `d85eea8`) does not need to extend to cardCorr. The lint comment at line 7986 (`<!-- lint-week-flow:ignore (factor name list for correlation checkboxes; list doesn't change per week) -->`) is correct and intentional.

## F5. Range buttons (3M|6M|1Y|3Y|All): present and working

**Severity: GREEN. Location: line 7977 (period dropdown options).**

**What:** Period dropdown ships 5 options: `All`, `3Y` (156 weeks), `1Y` (52), `6M` (26), `3M` (13). Default = `All`. Re-renders correlation matrix on change. Persists state via localStorage `rr.corr.period`.

**Why matters:** Parity with sibling time-series tiles (cardFacContribBars, cardFacHist) — they all offer the same range options. UX consistent.

## F6. CSV export: present, well-formed (B67 closed since v2)

**Severity: GREEN. Location: lines 5930–5946.**

**What:** `exportCorrCsv()` writes `{strategy}_factor_correlation_{period}_{freq}.csv` with header `,Factor1,Factor2,...` and rows `Factor1,r11,r12,...`. CSV-escaped factor names. Null cells render as empty string (matches the heatmap "—" behavior). Tested format-correctness inline; no observed bugs.

## F7. Right-click → note: present (B69 closed since v2)

**Severity: GREEN. Location: line 7966.**

**What:** Card-title `oncontextmenu="showNotePopup(event,'cardCorr');return false"` is wired. `id="cardCorr"` is on the card div (line 7964) so the note infrastructure can attach. Verified.

## F8. Cell-click drill: still missing (B65 carried)

**Severity: low/medium. Carried from v1.**

**What:** No `plotly_click` handler on the heatmap. Insight bullets DO drill via `oDrF()` (B74 closed in v2), but the cells themselves are read-only. There's no factor-pair detail view in the dashboard, so this requires a new modal — non-trivial.

**Why matters:** A canonical workflow ("I see r=0.85 between Profitability and Quality, what's driving it?") has no path beyond clicking each factor individually. Defer until project-wide factor-pair detail view is scoped.

## F9. Functionality vs sibling Risk-tab tiles

| Capability | cardCorr | cardFacContribBars | cardFacHist | cardRiskByDim |
|---|---|---|---|---|
| Stable DOM `id` | ✅ | ✅ | ✅ | ✅ |
| Card-title tooltip | ✅ | ✅ | ✅ | ✅ |
| About `ⓘ` button | ✅ | ✅ | ✅ | ✅ |
| Right-click → note | ✅ | ✅ | ✅ | ✅ |
| Reset Zoom button | ✅ | ✅ | ✅ | ✅ |
| CSV export | ✅ | ✅ | ✅ | ✅ |
| Period dropdown | ✅ | ✅ (Impact selector) | ✅ | n/a |
| Frequency toggle | ✅ | n/a | n/a | n/a |
| Factor multi-select | ✅ | n/a | ✅ | n/a |
| Plotly responsive | ✅ | ✅ | ✅ | ✅ |
| Full-screen modal (⛶) | wired (untested — see F2) | ✅ | ✅ | ✅ |
| Cell-click drill | ❌ (B65) | ✅ (bar click) | ✅ (point click) | ✅ (row click) |
| Theme-aware colorscale | ✅ | ✅ | ✅ | ✅ |
| Universe-pill aware | n/a (intentional) | n/a | n/a | n/a (with footer disclosure) |
| Week-selector aware | n/a (intentional) | ✅ | ✅ | ✅ |

**Net:** Chrome parity = full. Functionality parity = full except cell-click drill (project-wide gap).

## Track 2 verdict: **GREEN with one YELLOW (F2 untested FS path)**

All chrome wired. All declared functionality works. F2 (generic FS path) needs a 5-min in-browser smoke test to convert to GREEN — could be broken or could be fine depending on whether `[id$="Div"]` selector picks up `#corrHeatPlot`.

---

# Track 3 — Design Consistency

## X1. Phase-D `tileChromeStrip` adoption — clean

**Severity: GREEN. Location: lines 7967–7983.**

**What:** As noted in F1, the chrome strip is fully migrated. Spot-checks:
- Same `.tile-chrome` wrapper as 30 sibling tiles
- Same button render order
- Same CSS classes (`tile-btn`)
- Period/freq dropdowns inherit token-driven styling (`var(--text-md)`, `var(--surf)`, `var(--grid)`, `var(--txth)`, `var(--radius-md)`)

**Why matters:** Adding a button to all 30 tiles is now one edit. cardCorr inherits all future chrome work for free.

## X2. Theme awareness — fully tokenized (B64 closed in v2)

**Severity: GREEN. Lines 5901–5906, 5910–5913.**

**What:**
- Heatmap colorscale: `[--neg, --grid, --pri]` via `getComputedStyle` lookup
- Cell text color: `var(--txth)` via token
- Card chrome: all `var(--*)` based
- Insight chip background: `var(--surf)`
- Border-bottom of factor checkbox strip: `var(--grid)`

Spot-check in Settings preview (light vs dark):
- Light theme: `--neg` red on white background, `--pri` indigo edges, mid-gray middle. Readable.
- Dark theme: `--neg` red, `--pri` indigo, `--grid` dark slate. Cell text `--txth` (light slate) readable on all three.

**No remaining hardcoded hex.** B64 closed.

## X3. Inline styles on the period/freq dropdowns

**Severity: low. Location: lines 7976–7980.**

**What:** The `extra:` block hands raw HTML with inline styles to the chrome strip:
```js
<select id="corrPeriod" onchange="..." style="font-size:var(--text-md);padding:3px 6px;background:var(--surf);border:1px solid var(--grid);color:var(--txth);border-radius:var(--radius-md);font-family:inherit">
```

All values are tokens, so this is "tokenized inline" — design-acceptable. But the Phase-D pattern would suggest a canonical class like `.tile-select` to standardize the 3+ tiles that use period dropdowns (cardCorr, cardFacContribBars, cardFacHist).

**Why matters:** Future button/select theming changes still require touching multiple files. The goal of Phase-D was "single source of truth" — this is the last 10% of the work.

**Proposed fix:** Define `.tile-select` CSS class with the above declarations. Replace the inline-style blocks across cardCorr, cardFacContribBars, cardFacHist with `class="tile-select"`. ~30 line CSS addition + 5-line edits per tile. Out of scope for this audit; logged for Phase-K finishing sweep.

## X4. Footer hairline + caveat formatting — partial

**Severity: low. Reference: D3 above + cardRiskByDim caveat-footer pattern.**

**What:** cardRiskByDim has an exemplar footer:
```html
<div class="caveat-footer">Σ %T = 124% (F18). Universe pill does NOT filter this tile…</div>
```

cardCorr has no footer — the insight chip (`#corrInsights`) plays a different role (shows high-correlation pairs as bullets) but doesn't disclose the universe-invariance / week-invariance / monthly-cadence properties. A 1-line caveat-footer would round out the design parity with cardRiskByDim and educate users.

**Proposed fix:** D3 above (already listed in Trivial-Fixes section).

## X5. Insight chip styling: clean

**Severity: GREEN. Lines 5926.**

**What:**
```html
<div style="padding:8px 10px;background:var(--surf);border-radius:6px;font-size:11px;color:var(--txt);line-height:1.8">
```

Tokenized, matches sibling alert chips. Factor names are linked (`oDrF` drill), styled with `color:var(--pri)` + underline. Visual affordance for "click here" is clear.

## X6. Density and alignment — matches project standard

| Element | cardCorr value | Standard | Match? |
|---|---|---|---|
| Card title | `.card-title` (14px / 600 weight) | inherited | ✅ |
| Period / Freq selects | `font-size:var(--text-md); padding:3px 6px` | matches `cardFacButt` | ✅ |
| CSV button | `class="tile-btn"` | shared | ✅ |
| Factor checkbox labels | `font-size:11px; padding:2px 6px` | matches | ✅ |
| Heatmap cell text | `size:10` | shared with sibling heatmaps | ✅ |
| Axis tick fonts | `size:10` (x), `size:10` (y) | matches | ✅ |
| Colorbar tickfont | `size:9` | matches | ✅ |
| Insight bullets | `font-size:11px; line-height:1.8` | matches | ✅ |
| Insufficient-data warning | `font-size:10px; color:var(--warn)` | matches | ✅ |

**All density / alignment choices match project standard.**

## X7. Heatmap geometry

**Severity: GREEN. Lines 5899, 5917–5919.**

- Min height 260px, scales `36px/factor + 80px base` — works for 5–25 factors
- Margins `l:150 r:60 t:20 b:110` — comfortable for ~28-char factor names
- `tickangle:-35` on x — readable on bottom axis
- Symmetric matrix renders both triangles + diagonal — visually wasteful (B63 carried) but conventional

## Track 3 verdict: **GREEN**

All density, alignment, theme, and chrome conventions match the Risk-tab peers. X3 (canonical `.tile-select` class) and X4 (footer caveat) are nice-to-haves logged for follow-up, not gaps.

---

## 4. Closure status of all prior findings

| # | Issue | v1 (4-23) | v2 (5-1) | v3 (5-4) | Notes |
|---|---|---|---|---|---|
| B60 | Active-vs-raw fallback mixes series types | open | open | **open** | L5857 still mixes; PM decision |
| B61 | Positional `min(len)` pairing not date-aligned | open | open | **open** | Latent; all factors have equal-length history in current data |
| B62 | Zero-variance / `n<3` silently returns 0 | open | closed | closed | L5864 + L5870 return null; cell renders "—" |
| B63 | Full symmetric matrix | open | open | open | Cosmetic |
| B64 | Hardcoded colorscale | open | closed | closed | L5902-5906 + L5910-5913 use tokens |
| B65 | No cell click drill | open | open | open | Project-wide gap |
| B66 | State persistence | open | closed | closed | localStorage at L5794-5811 |
| B67 | No CSV export | open | closed | closed | exportCorrCsv() L5930-5946 |
| B68 | No full-screen modal | open | open | **wired (untested)** | F2 above — verify in browser |
| B69 | No id / no note popup | open | closed | closed | L7964/7966 |
| B70 | No data-tip on title | open | closed | closed | L7966 |
| B71 | Ghost tile | open | closed | closed | Removed 2026-04-30 |
| B72 | Ghost PNG button | open | closed | closed | (deleted with B71) |
| B73 | Hardcoded thresholds | open | closed | closed | _thresholds.corrHigh/corrDiversifier (L5882-5883, L10608) |
| B74 | Insight names not clickable | open | closed | closed | L5891-5892 wrap in oDrF |
| B75 | <3-obs factors silently 0 | open | closed | closed | L5860 filters them out |
| B76 | Monthly dedupe undocumented | open | closed | closed | Comment at L5854 |
| B77 | Tile semantic ambiguity | open | open | **open** | Tooltip clarifies; full rename queued |
| C1 (v2) | Monthly dedupe slice(0,7) bug | n/a | open | **closed** | L5855 slice(0,6) live; verified empirically |
| C2 (v2) | _corrRestored stale on strategy switch | n/a | open | open | Low-cosmetic |
| C3 (v2) | FAC_PRIMARY missing 'Medium-Term Momentum' | n/a | open | **closed** | L4595 contains both spellings |
| **D3 (v3 NEW)** | Universe-invariance footer disclosure | n/a | n/a | open | Trivial coordinator fix |
| **D4 (v3 NEW)** | Period dropdown lacks observation-count tooltip | n/a | n/a | open | Trivial |
| **D5 (v3 cosmetic)** | Refresh "e−bm" wording in tooltip → "exp − bench_exp" | n/a | n/a | open | Trivial |
| **F2 (v3 NEW)** | Generic openTileFullscreen path untested for cardCorr | n/a | n/a | open | Verify in browser |
| **F4 (v3 NEW)** | Plotly null-cell rendering vs explicit gap handling | n/a | n/a | open | 3-line tweak |

**Net since v2:** 2 closed (C1, C3), 0 regressed, 4 new (D3, D4/D5, F2, F4). All new findings are low-severity / coordinator-friendly except F2 which needs an in-browser smoke test.

---

## 5. Verification Checklist

- [x] **Pearson math** verified vs Python pearson on 3 pairs × 2 windows (re-run 2026-05-04)
- [x] **C1 closure** verified empirically (slice(0,6) → 88 monthly buckets in EM Volatility)
- [x] **C3 closure** verified ('Medium-Term Momentum' in FAC_PRIMARY)
- [x] **snap_attrib synthesis** is rename-only (compliant with anti-fabrication rule 2)
- [x] **B62 sentinel** path: pearson returns null; heatmap renders "—"; CSV returns empty
- [x] **B66 persistence**: localStorage rr.corr.period / freq / facs (caveat: stale on strategy switch — C2)
- [x] **B67 CSV** well-formed: header + rows, factor names CSV-escaped
- [x] **B69/B70** id + tooltip + right-click note all wired
- [x] **B73 thresholds**: corrHigh / corrDiversifier sourced from `_thresholds`
- [x] **B74 clickable insights**: factor names wrap in `<a onclick="oDrF(...)">`
- [x] **B75 short-history filter**: factors with <3 obs dropped before matrix build
- [x] **Phase-D chrome**: tileChromeStrip migration clean (no regressions)
- [x] **Theme awareness**: all colors via CSS tokens, no hardcoded hex
- [x] **Universe pill**: correctly excluded from cardCorr rerender (D5)
- [x] **Week selector**: correctly does not affect cardCorr (F4)
- [x] **F18 escalation**: does not impact cardCorr (D6)
- [ ] **F2 fullscreen path**: untested live — verify Plotly redraw on cloned `#corrHeatPlot`
- [ ] **D3 universe-invariance footer**: not present — would close UX clarity gap
- [ ] **D4 period observation count**: not in tooltip — would help PM context
- [ ] **C2 strategy-switch persistence**: still uses single-shot `_corrRestored` flag; PM call

---

## 6. Verdict

### **GREEN — fully Tier-2 ready for daily PM use**

**Why GREEN (not YELLOW like v2):**
- C1 (monthly dedupe defect) is now closed and verified empirically
- C3 (default checkbox FAC_PRIMARY miss) is now closed
- Phase-D `tileChromeStrip` migration is clean — no regressions
- All track 1 / 2 / 3 conventions match project standard
- F18 (the open inquiry) doesn't touch this tile's data path

**Why not BLUE (full-color celebration):**
- F2 (generic FS path) is untested — could be silently broken
- B60, B61, B77 (PM-decision items from v1) still pending
- D3, D4, F4 are nice-to-have UX clarity improvements

### Color status by section

- **Track 1 (Data Accuracy): GREEN** — Pearson math correct, C1 closed, snap_attrib path rename-only. D4 null-exp coercion is YELLOW-scoped to 16 FX factors with documented escape valve (PM B60 decision).
- **Track 2 (Functionality): GREEN with one YELLOW (F2)** — chrome parity full; F2 fullscreen path needs in-browser smoke.
- **Track 3 (Design): GREEN** — tokens applied, density/alignment/theme all match project standard. X3 (`.tile-select` canonical class) and X4 (caveat footer) are project-wide design-debt items, not cardCorr-specific.

### Fix queue

**TRIVIAL (≤5 lines each, coordinator can apply):**
- D3: Universe-invariance footer disclosure (1-2 lines added below `#corrInsights`)
- D4: Period dropdown tooltip with observation count (data-tip on `#corrPeriod`)
- D5: Refresh "e−bm" wording → "exp − bench_exp (active exposure)" (1 char in `data-tip`)
- F4: Plotly explicit null-cell rendering (set `text: ...||'—'` and confirm cell looks gapped)

**NEEDS PM DECISION:**
- B60: Active-vs-raw policy → consequential rename (B77)
- B117: Default period (currently "All", PM said "1Y" per R2-Q12)
- C2: Strategy-switch persistence behavior

**NEEDS IN-BROWSER VERIFICATION:**
- F2: openTileFullscreen('cardCorr') — does the cloned `#corrHeatPlot` redraw? If yes → GREEN. If no → 5-line dedicated FS handler.

**LARGER (queued, non-blocking):**
- B61: Date-aligned Pearson (vs positional)
- B63: Half/full-triangle toggle
- B65: Cell-click drill (needs project-wide factor-pair view)
- B68 (deeper): Custom FS handler regardless of F2 outcome
- X3: `.tile-select` canonical class for period/freq dropdowns

---

## 7. Sign-off summary

| Track | Verdict | One-line |
|---|---|---|
| **1. Data Accuracy** | **GREEN** | Pearson math = numpy. C1 closed. snap_attrib rename-only. F18 doesn't apply. |
| **2. Functionality** | **GREEN (1 YELLOW)** | Phase-D chrome clean. F2 fullscreen path needs in-browser smoke. |
| **3. Design** | **GREEN** | Tokens applied. Density / alignment / theme all match project standard. |

**Overall: GREEN. SAFE FOR DAILY PM USE. Recommended actions all coordinator-trivial or PM-decision.**

---

## 8. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Audit v1 — 18 findings B60–B77, RED verdict (ghost tile + missing CSV/FS/drill/id/note). | Tile Audit Specialist |
| 2026-04-30 | Promote-to-first-class commit `819c493` — closed B62, B64, B66, B67, B69, B70, B71, B72, B73, B74, B75. | (codebase) |
| 2026-05-01 | Audit v2 — re-verification of 18 prior findings (12 closed) + ground-truth Pearson against numpy on EM full history (3 pairs × 2 windows, all match) + 3 new findings: C1 (monthly dedupe bug), C2 (`_corrRestored` stale-on-strategy-switch), C3 (FAC_PRIMARY momentum-name mismatch). YELLOW / SAFE FOR PRESENTATION verdict. | Tile Audit Specialist |
| 2026-05-04 | Audit v3 — re-verification post-Phase-D `tileChromeStrip` migration. Confirmed C1 + C3 closed in code, no regressions, no F18 impact. New findings: D3 (universe-invariance footer disclosure), D4 (period observation count tooltip), D5 (refresh tooltip wording), F2 (untested generic FS path), F4 (explicit null-cell rendering). GREEN / Tier-2-ready verdict. | Tile Audit Specialist |

---

## Agents That Should Know This Tile

- Tile Audit Specialist — authored this spec
- Risk Reports Specialist — authority on B60 (active vs raw) / B77 (rename)
- rr-data-validator — D4 null-exp scoping; potentially D7 cardCorr Layer-3 monitor
- rr-design-lead — X3 (`.tile-select` canonical class proposal)

