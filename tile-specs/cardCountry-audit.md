# Tile Audit: cardCountry — Country Exposure (Map / Chart / Table)

> **Audit date:** 2026-04-30
> **Auditor:** Tile Audit Specialist
> **Dashboard:** dashboard_v7.html (10,419 lines)
> **Prior audit:** `cardCountry-audit-2026-04-20.md` (10 days ago) — covered the table view exhaustively, lightly touched the map. Heatmap chart view did not exist yet.
> **Gold standard for header pattern:** cardFacRisk (L1760–1773) + cardChars (L1887–1899, after the 2026-04-30 fix at 11a5c7e).
> **Methodology:** 3-track audit (data accuracy / functionality parity / design consistency).

---

## VERDICT: YELLOW

The tile is functionally rich — three view modes, 12 map color modes, factor-context drill-through, full-screen for each view, country picker, threshold row classes, TE / Stock TE / Factor TE columns now populated, click-through to country drill with attribution chart. Most of the prior audit's "missing" items have shipped. **Two real data-correctness findings keep this from GREEN:**

1. **Top-N pill is silently inert on the Map view** (the default sub-view) — tooltip says "Top N countries by absolute TE contribution" but `rCountryMap` does not consult `_ctryTopN`. PMs flipping to "Top 10" expect the map to highlight 10 countries; nothing changes. This is the most prominent control on the tile, and on the most-viewed sub-view, it does nothing.
2. **`_aggMode='benchmark'` produces wildly under-reported numbers in the table's count + factor breakdown columns** because `cs.hold[]` only ships top BM-only stocks (materiality threshold). Verified: GSC's US row aggregates to `agg(b)=3.58` from 62 holdings via `aggregateHoldingsBy(...,{mode:'benchmark'})` — but the actual benchmark weight is **61.12** (per `cs.countries[].b`). The displayed "Bench %" column reads `c.b` directly so that cell is right, but the # column and the Factor TE Breakdown columns ALL run through `aggregateHoldingsBy` and dramatically misreport when the user toggles Universe → Benchmark. Same issue must exist on cardSectors, cardGroups, cardRanks but is most visible here because users toggle Universe most often when looking at country/regional bets.

Plus header polish (no subtitle / no KPI strip vs cardFacRisk gold), the equirectangular projection (Q26 default-C is Robinson with an explainer), and the country-of-risk vs country-of-listing toggle (Q25, default A) being shipped as a caveat-only rather than a real toggle.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | Country Exposure |
| Card DOM id | `#cardCountry` (L1820) |
| Render fns | `rCountryTable(s.countries,s.hold)` L3580–3666; `rCountryMap(s)` L4737–4866; `rCountryChart(s,divId)` L5006–5081 |
| Drill fn | `oDrCountry(name, factorContext?)` L9019–9070 (with optional factor context for heatmap-cell drill) |
| Drill modal id | `#countryModal` (registered in `ALL_MODALS`) |
| FS opener | `openCtryFullscreen()` L4918 — view-aware: Map → `openFullScreen('country')` L9621 (`renderFsCountry`); Chart → `openCtryChartFullscreen()` L4933; Table → `openCtryTableFullscreen()` L4961 |
| About entry | `_ABOUT_REG.cardCountry` L670–677 (states country-of-RISK convention + Q25/Q26 backlog) |
| Tab / row | Exposures Row 4 (full-width `grid-column:1/-1`); hidden when `isUSOnly` |
| Top-N pill | `_ctryTopN` (default 0/All; persisted `rr.ctryTopN`) — applies to Table + Chart, **NOT to Map** |
| Country picker | `_ctryChartCountries` (Set, default empty=all; persisted `rr.ctryChartCountries`) — chart-view ONLY |
| Filter chip | `#ctryFilterChip` (per-column tile filters, shared infra with sectors) |
| Universe (Aggregator) | global `_aggMode` (portfolio / benchmark / both) — drives `aggregateHoldingsBy` for table count + factor cells |

---

## 1. DATA ACCURACY — FINDINGS

### 1.1 [SEV-1] Universe='benchmark' silently under-reports # and Factor TE columns

Verified against `latest_data.json` (GSC, 26 countries, 131 hold rows):

```
United States row in cs.countries:
  c.p = 44.8     c.b = 61.12     c.a = -16.3     (✓ FactSet "Country" 19-col section)

Aggregated from cs.hold[] in 'benchmark' mode (h.b > 0 filter):
  agg.count = 62 holdings
  agg.b     = 3.58       ← OFF BY 17x
```

Root cause. The 19-col Country section (parser-level rollup) covers the **full benchmark country list with full benchmark weights**. The Security section in v2 ships **port + materially-large BM-only** (per the v2 Security slim, see CLAUDE.md "Upcoming FactSet format change"), so `cs.hold[]` only carries a tiny fraction of bench holdings. The dashboard's `aggregateHoldingsBy` with `mode='benchmark'` filters to `h.b > 0` — which captures the small subset that's both BM-only AND material — and treats this as the full universe. So:

- **Bench%** column: reads `c.b` (parser rollup) — **correct**.
- **#** column: reads `factorAgg[c.n]?.count` — **wrong in benchmark mode**. Says US = 62 (top BM holdings), reality is "all benchmark constituents in US" which is hundreds.
- **Factor TE Breakdown** columns (12 factor cols at the right): read `factorAgg[c.n]?.factor[fname]` — **wrong in benchmark mode**. Sum is over only the materially-large BM-only subset, missing the long tail.
- **Spotlight rank columns (O/R/V/Q)**: same — `pickRankAvg` operates on the same per-country accumulator.

In **portfolio mode** these are all correct (port holdings ARE shipped fully). In **both** mode they're approximately correct (port + material BM-only is most of risk-relevant universe). The bug bites specifically when a PM clicks Universe → Benchmark to see "what does the benchmark side look like across countries" — they get a 17x understated answer.

This is the same pattern on cardSectors, cardGroups, cardRanks per construction — but on cardCountry it's the most likely user path because of how Q25/Q26 frame the geographic-comparison use case.

**Proposed fix.** Two options:
- **(a) Honest fix**: when `_aggMode==='benchmark'` and the displayed metric is a holdings-aggregated quantity, display "—" or a "(port+material BM only)" qualifier. The factor breakdown rows that exist via `c.factor_breakdown` (parser-level country aggregates, if shipped — verify) should be sourced from there.
- **(b) Carry-on workaround**: hide the # column and Factor TE Breakdown columns entirely when `_aggMode==='benchmark'`. The Bench% column stays. Less data, but no wrong data.

Either way, this needs a SEV-1 anti-fabrication callout per the April 27 hard rules — silent corruption when toggling a primary control.

### 1.2 [SEV-2] Country-of-risk vs country-of-listing — Q25 default-A "toggleable" not yet shipped as toggle

Per INQUISITOR_DECISIONS_2026-04-30.md Q25: "Country-of-risk vs listing toggleable (default A)". The about-popup caveat acknowledges the open question:

> "Country = country-of-RISK (issuer domicile), not country-of-listing. Toggle planned in Q25 backlog."

Today the data layer ships only one flavor (issuer domicile, per FactSet's standard Country field). For ADRs (e.g., Alibaba listed in NY but issuer-domiciled in China) this is the right canonical default, but the answer the user committed to was a **toggle**, not just a label. There's no code path in `rCountryTable` / `rCountryMap` / `rCountryChart` that branches on a "country source" flag.

The fix is two parts:
- **Parser side**: emit both `c.n_risk` and `c.n_listing` per holding (FactSet has `Country` and `Country_Of_Listing` columns; verify in the next CSV sample whether `Country_Of_Listing` is shipped — if not, add to FACTSET_FEEDBACK).
- **Dashboard side**: a header pill `Risk | Listing` that switches `cs.hold[h].co` source. ~15-line addition.

Until then, the about-popup caveat is honest disclosure, but the audit notes this is shipped as text rather than UI.

### 1.3 [SEV-2] Heatmap chart view's customdata-coded factor name is shortened — fragile drill round-trip

`rCountryChart` (L5070) builds a `shortToFull` map to recover the full factor name from the shortened axis label, because customdata stores the SHORTENED form (L5040: `customdata=...factorCols.map(f=>[c,f,...])` — wait, that's the FULL form). Re-reading more carefully:

```js
customdata=countries.map(c=>factorCols.map(f=>[c,f,(fa[c]?.factor?.[f]??0).toFixed(2)]));
                                              ^         ^
                                          full ctry  full factor name
```

Then on click (L5076):
```js
const factorShort=cd[1];   // BUG: misnamed — cd[1] is actually the FULL name
const factorFull=shortToFull[factorShort]||factorShort;
```

So `cd[1]` already contains the FULL factor name (because `factorCols` is the full list). The `shortToFull` dictionary lookup is a no-op because the key looked up is already the full name (which isn't a key of `shortToFull`); the `||factorShort` fallback then returns the full name unchanged. Net effect: works, but by accident. The variable naming `factorShort` is misleading.

Trivial cleanup: rename `factorShort` → `factorName` and drop the `shortToFull` dictionary on L5070–5072 (dead code). 4 lines deleted.

### 1.4 [SEV-3] `aggregateCountryRisk` and `aggregateHoldingsBy` are TWO separate aggregators on the same data path

`rCountryMap` (L4743) calls `aggregateCountryRisk(s)` (defined L9366) which loops `(s.hold||[]).forEach` and ignores `_aggMode`. `rCountryTable` (L3600) calls `aggregateHoldingsBy(hold,h=>h.co,...)` which honors `_aggMode`.

Two consequences:
- The MAP's `te`/`specific`/`factor_te` color modes are **always Universe='both'** (no `h.b > 0` or `h.p > 0` filter). They show the same answer regardless of the global Aggregator pill.
- A PM toggles the Aggregator pill, sees the table change, then looks at the map and sees no change. Silently inconsistent.

**Proposed fix.** Either pass `_aggMode` into `aggregateCountryRisk`, or refactor `rCountryMap` to use `aggregateHoldingsBy(s.hold, h=>h.co, [], {mode:_aggMode})`. The latter unifies the two aggregator paths and lets the map honor Universe. ~20 lines.

### 1.5 [SEV-3] COUNTRY_ISO3 + CMAP coverage gaps — silent drops, no warning

Verified against GSC sample (26 countries shipped):
- **Argentina** is in `cs.countries[]` but missing from both `COUNTRY_ISO3` (L4722) and `CMAP` (L539) — silently dropped from map AND from region rollup (CMAP fallback puts it in 'Other').
- **Singapore** is in `COUNTRY_ISO3` but missing from `CMAP` — shows on map, but in any region rollup falls into 'Other'.

Across the 7-strategy worldwide-model file these maps will need to cover ~50–60 country names. Today's static maps cover 48 ISO3 + 34 CMAP. The mismatch is silent — no console warning, no on-screen flag.

**Proposed fix.** At parse-time (verifier) or at first render, log a console warning + add a tiny chip "N countries unmapped" to the tile header when coverage < 100%. ~10 lines. Long-term: move the maps to a JSON file the parser owns (single source of truth for ISO3 + region grouping).

### 1.6 [SEV-3] Drift on `c.a` vs `c.p − c.b` — rounding, not corruption

Five GSC countries have `|p − b − a| > 0.05` after normalization. Examples: Australia `p=1.7, b=3.73, a=-2.1` (p−b=−2.03), France `p=2.4, b=1.36, a=1.1`. These are 1-decimal display rounding artifacts (`f2(v)` rounds to 1dp), not data corruption — the raw upstream `aw` values from FactSet are the source of truth, and the parser ships them. cardSectors's audit doc accepts ≤0.05% rounding tolerance and this is the same. Worth noting that the `data-sv` attributes carry the raw (unrounded) values for sort, so sort behavior is correct.

**No action needed**, but worth flagging in case of future user "5−3=2 not 1.9" complaints — the answer is the source rounding.

### 1.7 [SEV-3] `c.over` populated for only 11/26 countries (42%)

Map's `rk:over` mode reads `c.over` directly. For 15/26 countries that field is null → those countries render as missing (Plotly handles null gracefully but the colorbar shows zero), which is worse than rendering as "—" overlay or grey. This is a parser-side population gap (the parser only computes per-country avg ranks for the subset that has SEDOL → Spotlight rank match).

**Proposed fix.** At render time, post-compute `c.over/rev/val/qual` from the per-country aggregator IF the parser-shipped value is null. Currently the table view does this implicitly (table reads from `factorAgg.avg.over` not `c.over`); the map view doesn't. Unify. ~10 lines.

---

## 2. FUNCTIONALITY PARITY — FINDINGS

### 2.1 [SEV-1] Top-N pill silently inert on Map view (the default)

`setCtryTopN` (L2503) and `applyCtryTopN` (L2512) operate on `#tbl-ctry tbody tr` — DOM-only hide. `rCountryChart` (L5033) consults `_ctryTopN` directly. **`rCountryMap` does not.** The pill is rendered prominently in the card header (in fact it occupies more horizontal space than the title), and its tooltip says "Top N countries by absolute TE contribution".

User flow that breaks today:
1. Open Exposures tab → see Country Exposure with default Map view.
2. Click "Top 10" pill expecting to see only 10 countries highlighted.
3. Map shows zero change. All 26 countries still colored.
4. Pill stays in "active" state — UI lies that the filter is applied.

**Proposed fix.** Inside `rCountryMap` (L4737), after the `mapped` filter, if `_ctryTopN > 0`, sort `mapped` by `|getVal(c)|` desc, slice to N, and grey-out (rather than drop entirely — dropping breaks the map's continuity) the rest by setting their `z` to NaN or scaling alpha. ~10 lines. Either visually-prominent treatment (saturation drop) or a "showing top 10 of 26" disclosure chip in the header.

### 2.2 [SEV-2] No header KPI strip / subtitle vs cardFacRisk gold standard

cardFacRisk (L1760–1773) has:
- title + small subtitle ("exposure × risk · bubble = factor σ")
- KPI strip below title (`#facRiskKpi`) showing TE / Idio / Factor / Material count
- ⛶ button using `class="export-btn"`

cardCountry header (L1820–1859) has:
- title + ⓘ + filter chip + Top-N pill
- map-color picker + ⛶ + ⬇ + Region toggle + view toggle
- map-secondary toggle (Exposure/Contribution)

Lots of controls, but no subtitle and no KPI strip. The "punch-line numbers" PMs want at-a-glance:
- Largest **active** weight country (e.g., "US: −16.3% UW, largest country bet")
- Largest **|TE|** contributor (e.g., "US: 40% of TE")
- Country count (mapped vs total: "26 countries · 25 mapped")

This is a ~25-line addition: a `<div id="ctryKpi" style="display:flex;gap:8px;margin:4px 0 10px">` between the header row and the view divs, populated post-render by a dedicated `_buildCtryKpi(s)`.

### 2.3 [SEV-2] Map projection still equirectangular — Q26 default-C is Robinson

Both `rCountryMap` (L4855) and `_renderFsCtryMap` (L9687) hardcode `projection:{type:'natural earth'}`. Per Q26: "Map projection — equirectangular (current default), Mercator, Robinson? *A · B · C* (default: C)". Decisions doc adds: "🔥 **Recommendation: Robinson + add reset-zoom button.**"

Trivial change: `type:'robinson'` (Plotly supports it natively as a `geo.projection.type` value). 2 lines × 2 sites = 4-line change. Adding the reset-zoom button is another ~5 lines (the existing region buttons reset to the world preset, but a dedicated "Reset" button next to the region pills would save a click).

### 2.4 [SEV-2] No country search box on map (Q28 ✓ "yes")

Q28: "Add country search box: yes". Not yet shipped. With 26-50 countries on the map, manually finding "where does Singapore sit on this map" requires hover-scanning. A small inline search input above the map would jump to that country (set the region zoom + brief highlight pulse).

~15 lines: input element, on-input fuzzy-match against `cs.countries.map(c=>c.n)`, on-select call `setMapRegion(matchingRegion)` plus a Plotly hover-state injection on that country's iso3.

### 2.5 [SEV-2] Heatmap drill carries factor context cleanly — but the breadcrumb back to the heatmap is missing

When user clicks a Volatility×Hong Kong cell, `oDrCountry('Hong Kong', 'Volatility')` opens with a purple "★ Sorted by Volatility factor TE · clear" badge (L9055) — clean. Clicking "clear" reloads the modal sorted by total TE.

**Missing:** there's no breadcrumb back to the heatmap. After closing the modal, the user is back at the map view (not the chart view they came from). Heatmap state is preserved (which countries selected, which factors visible) but not focused.

**Proposed fix.** Add a small "← Back to heatmap" link next to the factor badge that closes the modal AND calls `toggleCountryView('chart', null)`. ~3 lines.

### 2.6 [SEV-3] Table view sorts the same columns as the heatmap shows? Yes — but column ordering differs

Heatmap columns are `RNK_FACTOR_COLS` order (Mom, Prof, Vol, Gro, DivYld, ErnYld, MktSens, FXSens, Liq, Lev, plus Value/Size which are excluded from RNK by default in the global ⚙ Cols picker). Table view's "Factor TE Breakdown" group at the right uses the same `RNK_FACTOR_COLS` list (L3639) so column 7+ in the table is column 0+ in the heatmap, but the table's `tableFilterIcon` cell width and column spacing differs — checking same factor in both views requires re-orienting.

Not a bug. But a UX papercut: clicking on the heatmap's "Vol" column header could highlight the Vol column in the table when the user toggles back to Table view. ~20 lines for a "linked highlight" treatment. Defer; nice-to-have.

### 2.7 [SEV-3] "isUSOnly hides entire tile" — wrong default for SCG/Alger domestic landing

`isUSOnly` at L1672 is computed from holdings (every non-cash holding has co matching `/^(united states|usa)$/i`). When SCG (Russell 2000 Growth) lands as a domestic-model file, every holding will be US, and the cardCountry tile + cardRegions tile will both `display:none`.

**That's the wrong policy** for a domestic-only fund. The PM still wants:
- Sector / industry / state-level breakdowns (state — even cruder than country, but state-of-incorp is a real US-only dimension)
- Region in the GICS sense (no longer geographic — "domestic developed" is one bucket, no value)

Today the entire tile vanishes. Better: keep the card visible with a polite "US-only strategy — geographic country analysis is degenerate (all US). See the State / GICS Region tile" chip + link to whatever replaces it (TBD per Q24-Q34 follow-up).

**Open question for PM**: when SCG's CSV lands, should the domestic-model verifier emit a `state` column instead of `country` and bind cardCountry to that, OR should cardCountry hide and cardState replace it?

### 2.8 [SEV-3] CSV export reads `#countryTableWrap table` — empty if user is on Map or Chart

`exportCSV('#countryTableWrap table','countries')` (L1832) reads from the table-view DOM, which is `display:none` while user is on Map or Chart. The `display:none` doesn't strip the `<table>` from DOM, so the CSV download succeeds — but the user never sees the table render they're exporting.

Today this is OK (user gets the right CSV regardless of which view they're on). But there's a UX quirk: if a user clicks "Download CSV" while looking at the heatmap, the file they get matches the table (which they may never have inspected). Not a bug — flag only.

### 2.9 [SEV-4] No range selector on country-attribution chart in drill modal

The drill modal's `renderCountryAttribChart` (L9088) plots `cs.snap_attrib[name].hist` cumulative impact, but unlike the metric drill (cardChars new behavior) there's no 3M/6M/1Y/3Y/All range selector. Inconsistent with cardChars and cardSectors drills. ~10 lines of `range-btn` HTML + a slice. Defer; minor.

---

## 3. DESIGN CONSISTENCY — FINDINGS

### 3.1 Header pattern doesn't match cardFacRisk gold

Same parity gap as cardScatter and cardChars (both flagged in their audits): missing the small grey subtitle + the inline KPI strip + the `class="export-btn"` ⛶. The current header is busy (5 button-groups + 1 chip + 1 pill) but lacks the tile-summary line that orients a PM at a glance.

Suggested subtitle: `geographic exposure · 26 countries · 25 mapped (1 unmapped: Argentina)` — and rotate based on actual data. The "1 unmapped" piece auto-flags 1.5 above.

### 3.2 Top-N pill visual prominence inconsistent with its actual scope

The Top-N pill is large (4 buttons + label, ~150px wide) and sits in the title row. But it only governs Table + Chart. On the default Map view it's a no-op. The user has no visual cue that it's view-scoped. Either:
- (a) Hide the pill when on Map view (simple)
- (b) Make it work on Map (per F1 above)
- (c) Add a small "Table+Chart only" qualifier to the pill label

(b) is the right fix. Until then (a) is the honest workaround.

### 3.3 Map color picker has 12+ entries — overflow on narrow screens

`getMapColorGroups` (L9339) returns 4 base groups (Weight, Risk, Spotlight, Style Factors) with 12+ items in Style Factors alone (one per factor). The picker is `max-height:400px;overflow-y:auto` (L1829) so it scrolls, but no search input, no fuzzy-match. With domestic-model SCG (smaller factor set) this is less of an issue; with worldwide ACWI's 16 factors it's a long scroll.

Add a search input at the top of the picker. ~10 lines.

### 3.4 Map view height fixed 320px — large empty space at bottom for Asia / Americas zooms

The 320px map height is fine for World view. When zoomed to Asia or Americas the visible content compresses but the canvas stays 320px. Result: bottom 30% of the map div is solid background.

Either let height adapt to selected region (e.g., Asia=280, Americas=300, World=320), or accept it. Low priority.

### 3.5 Heatmap chart view's adaptive height (~22px/row) is good — but no min-row guarantee

`rCountryChart` (L5045): `h=Math.min(600,Math.max(280,countries.length*22+80))`. If a user picks 1 country (via picker), height = 280px / 1 row = giant single-row strip. Cosmetic only. Either floor at 5 rows or render a "select more countries to see the heatmap" hint when picker has < 3 selections.

### 3.6 Hardcoded slate-700 hex in FS panel HTML (`#334155 / #64748b`)

`_renderFsCtryPanel` at L9714, 9731 uses literal `#334155` for unselected button borders. Same theme-hostility flagged in cardScatter audit §3 and cardChars. Replace with `var(--grid)`/`var(--textDim)`. ~6 sites.

### 3.7 `oDrCountry` modal header missing the cardFacRisk-style metadata strip

Modal opens with country name + 3 KPI cards (Port / Active / Region). Nice. But the holdings table that follows lacks a top-of-table summary:
- "Showing X holdings sorted by total TE (or by Y factor)"
- An aggregated row at the bottom: country totals (Σ Port, Σ Active, Σ TE)

Sector drill has both. Country drill has neither. ~15 lines.

---

## 4. PROPOSED FIXES (PRIORITIZED, MAX 5)

| # | Severity | Effort | Description |
|---|---|---|---|
| **F1** | SEV-1 | ~10 lines | **Make Top-N pill work on Map view.** Inside `rCountryMap` (L4737) after `mapped` filter, when `_ctryTopN>0`, rank `mapped` by `|getVal(c)|` desc, slice top N, set `z` to null (or apply low-saturation overlay) for the rest. Add a "showing top N of M" header chip when active. Removes the pill's silent-no-op state on the dashboard's most-viewed sub-view. |
| **F2** | SEV-1 | ~30 lines | **Honest Universe='benchmark' for table aggregator columns.** When `_aggMode==='benchmark'`, either (a) hide the # column and Factor TE Breakdown columns entirely (preferred, per anti-fabrication policy), or (b) render them with an "(only top BM-only shown)" qualifier chip below the header. Today these columns silently underreport by ~17x for major countries (US: agg=3.58 vs c.b=61.12). Apply the same fix to cardSectors / cardGroups / cardRanks — cross-tile pattern. Cite the April-27 anti-fabrication rule. |
| **F3** | SEV-2 | ~30 lines | **Adopt cardFacRisk header pattern.** Add (a) subtitle row: `geographic exposure · click any country to drill · ${mapped}/${total} mapped (${unmapped.length?'unmapped: '+unmapped.join(', '):''})`; (b) inline KPI strip with cards for: Largest |Active| country, Largest |TE| country, Country count (mapped/total). Lift skeleton from cardFacRisk's `#facRiskKpi`. Drops the tile from "control panel" to a real summary tile. |
| **F4** | SEV-2 | ~5 lines | **Switch projection to Robinson per Q26.** Both `rCountryMap` L4855 and `_renderFsCtryMap` L9687: `projection:{type:'natural earth'}` → `projection:{type:'robinson'}`. Add a "Reset zoom" button next to the region pills that calls `setMapRegion('world')` cleanly. The decision was already taken — this is shipping, not deciding. |
| **F5** | SEV-2 | ~25 lines | **Unify aggregator path between map and table.** Replace `aggregateCountryRisk(s)` (L9366) call site in `rCountryMap` with `aggregateHoldingsBy(s.hold, h=>h.co, [], {mode:_aggMode})`. The map's TE / Specific / Factor TE color modes will now honor the global Universe pill (today they always show "both"). Synchronizes the map and table on the same answer. After F2 lands, the under-report problem doesn't migrate to the map because we're using the same anti-fabrication-aware aggregator. |

**Out of scope for this round (next backlog):**
- Country-of-risk vs country-of-listing toggle (F2-adjacent, but blocked on parser shipping `Country_Of_Listing` field — needs FactSet ask in FACTSET_FEEDBACK)
- Country search box (Q28 ✓ "yes" but ~15 lines, defer until F1–F5 land)
- isUSOnly policy revision when SCG/Alger domestic file lands (PM-decision item — does cardCountry hide, or rebind to State/GICS region?)
- Range selector on country-attribution chart in drill modal
- Per-color picker search input
- Heatmap "1 country selected" minimum-row hint
- Slate-hex theme cleanup in `_renderFsCtryPanel`

---

## 5. CARRY-OVER FROM PRIOR AUDIT (2026-04-20)

**Closed since prior audit:**
- TE / Stock TE / Factor TE columns added to table (prior #3 gap — now L3627–3631).
- Threshold row classes applied at ±3% / ±5% — `thresh-warn` / `thresh-alert` on `<tr>` (prior #4 — now L3613).
- Tooltips on Port / Bench / Active / R / V / Q / count headers (prior #7 — all `class="tip" data-tip`).
- Filter chip + tile filter icons on every column (prior #1 column-picker gap, partially closed via column-level filters).
- Heatmap chart view rebuilt as Country × Factor TE (prior chart was top-5/bottom-5 active bars — now L5006).
- Spotlight rank map modes (`rk:over/rev/val/qual`) added to color picker (L9353–9358).
- Per-cell drill from heatmap with factor context (`oDrCountry(name, factorContext)` L9019, factor badge L9055).
- ⓘ About entry shipped (L670–677) — calls out country-of-risk and Q25/Q26 caveats explicitly.
- Top-N pill added (L1822) — partially shipped (works on table + chart; F1 above closes the map).
- Country picker for chart view (L2466).
- View-aware FS dispatch (`openCtryFullscreen` L4918) — Map → rich FS, Chart → heatmap-FS, Table → table-FS.
- # column showing per-country holding count (universe-aware in port/both modes — broken in benchmark mode per F2).
- Rich hover tooltip on map (L4825) — full block + top-3 holdings per country.

**Still open:**
- F1 (Top-N inert on map)
- F2 (benchmark-mode under-report)
- F3 (no header KPI strip)
- F4 (equirectangular default — Q26 says Robinson)
- F5 (map / table aggregator drift)
- COUNTRY_ISO3 + CMAP coverage chip (audit 1.5 above; no warning today)
- Hardcoded chart bar colors (prior audit #6) — moot now that the heatmap rebuild replaced the bar chart; new heatmap uses theme.
- Drill modal range selector (prior audit #10)
- Country-of-risk vs listing toggle (Q25 default-A) — shipped as caveat, not as toggle
- Search box on map (Q28 ✓)

**New (introduced by Raw Factors merge / v2 Security slim, 2026-04-30):**
- F2 is the v2-Security-slim consequence: as benchmark holdings get pruned to "materially-large" only, any aggregator over `cs.hold[]` in benchmark mode will under-report the long tail. This affects all Universe-aware aggregator columns across the dashboard, not just country.
- 1.7 above (c.over populated for only 11/26 countries) is a direct consequence — parser's per-country rank avg is computed on the SEDOL-matched subset.

**New (introduced by Q24–Q29 decisions logged 2026-04-30):**
- Q24 (default map color = TE Contribution) — verify this is `_mapColorMode` default. Check `let _mapColorMode='active'` somewhere — if so, change default to `'te'`.
- Q26 (Robinson projection) → F4.
- Q27 (zero-exposure countries grey) → check `rCountryMap` rendering for countries with `c.p=0&&c.b=0` — today they fall through to the `getVal(c)` returning 0, which sits at zmid color. May need explicit grey override.
- Q28 (search box) → 2.4 above, deferred.
- Q29 (EM strategy + DM countries greyed/desaturated) → not yet shipped; needs a per-strategy `inUniverseSet` filter. Defer.
