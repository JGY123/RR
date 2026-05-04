# Drill Modal Migration — Spec & Scope

**Drafted:** 2026-05-04
**Status:** SPEC — pending PM signoff before any code changes
**Trigger:** Refactor Plan outstanding item ("Drill modal migration — drill modals (oDr, oDrMetric, oDrCountry, oSt) still have inline chrome").

---

## Why this doc exists

The Phase D refactor (April-May 2026) migrated all 30 tile chrome rows to `tileChromeStrip()`. **Drill modals are the holdouts** — each one assembles its own header / close button / range-pill row / chart / detail-table inline, with subtle inconsistencies between them. Adding a feature (e.g., "show synth marker on cumulative impact") today requires touching every drill function separately. That's the same pattern the tile-chrome migration solved.

This doc inventories the drill modals, identifies the inconsistencies, and proposes a migration spec. **It does NOT modify code.** Coordinator implements only after PM reviews + signs off on the contract.

---

## Drill-modal inventory

| Drill function | Line | Modal id | Trigger | Content shape |
|---|---|---|---|---|
| `oDr(type, name, range)` | 9754 | `#drillModal` | row click on cardSectors / cardCountry / cardRegions | range pills · time-series chart · holdings-in-bucket table · bench-only sub-table |
| `oDrF(name, range)` | 10017 | `#drillModal` | row click on cardFacContribBars / cardRiskFacTbl | range pills · factor exposure time-series · top contributing holdings |
| `oDrMetric(metric, range)` | 11452 | `#metricModal` | whole-card click on cardTEStacked / cardBetaHist / cardRiskHistTrends | KPI strip · time-series chart with reference bands · stat cards |
| `oDrCountry(name, factorContext)` | 12137 | `#countryModal` | row click on cardCountry · click on cardCountryHeatmap row | country detail · per-country attribution · sector breakdown · related holdings |
| `oDrChar(metric, range)` | 12317 | `#charModal` | row click on cardChars | metric definition · history chart · port-vs-bench delta over time |
| `oDrAttrib(name)` | 5776 | (varies) | row click on cardAttrib | factor attribution time-series · period selector |
| `oDrUnowned(ticker)` | 12227 | `#unownedModal` | row click on cardUnowned | bench-only stock detail · region peer holdings |
| `oSt(ticker)` | 10427 | `#stockModal` | bar click on cardTop10 / cardHoldRisk / row click on cardHoldings | stock detail · factor exposures · sector context · TE attribution |

**Total: 8 drill functions across 7 modal overlay containers.**

Plus 2 additional modals for derived flows: `#reportModal`, `#compModal`, `#groupModal`, `#riskBudgetModal` (these aren't "drills" but share the same modal-chrome substrate).

---

## Inconsistencies the migration would close

### 1. Close button placement / styling
- `#drillModal` (oDr / oDrF): close button rendered inside the inserted HTML, varying placement.
- `#stockModal` (oSt): inline close at top-right of inserted HTML.
- `#unownedModal`: inline close inside h2 header.
- `#metricModal`, `#countryModal`, `#charModal`: each renders its own close button.

The canonical class `.modal-close-btn` exists (CSS rule at L190) but is used inconsistently inside drill content.

**Migration target:** every modal renders a `.modal-close-btn` in the same position (top-right of modal container), via a shared `_drillCloseBtn(modalId)` helper that the drill content slots into.

### 2. Range-pill row (3M / 6M / 1Y / 3Y / All)
- `oDr` (L9770): `['3M','6M','1Y','3Y','All'].map(r => '<button class="range-btn ...')`
- `oDrF` (L10031): same pattern, repeated inline
- `oDrMetric` (L11475): same pattern, repeated inline
- `oDrChar` (L12340): same pattern, repeated inline

That's **4 inline copies of the same range-pill builder**, each with its own state variable (`_drillRange`, `_facDrillRange`, `_metricDrillRange`, `_charDrillRange`). Adding a new range option (e.g., "YTD") requires editing 4 sites.

**Migration target:** `_drillRangePills(currentRange, onChangeFn)` helper. One source of truth. State per drill type still stored separately, but the HTML + click-binding is one function.

### 3. Stat-card strip (KPI block at top of modal)
- `oDrMetric` (L11475 onward): rich 4-card stat-strip with Current / Active / Δ vs benchmark / 1Y range. Uses `.stat-card` canonical class (Phase K).
- `oDr`: thinner — just the header + "TE Contribution: X%" callout.
- `oDrCountry`: 3-card strip — Country exposure / TE Contrib / N Holdings.
- `oDrChar`: 2-card strip — Port / Bench / Diff.
- `oSt`: 4-card strip — Position / Active / TE Contrib / MCR.

**Migration target:** `_drillStatStrip([{label, value, color, tooltip}, ...])` helper. Each drill function declares its stat-strip data; the helper renders the canonical `.stat-card` markup.

### 4. Time-series chart container
- Every drill renders a Plotly chart in a div: `#drillHistDiv`, `#facDrillDiv`, `#metricDrillDiv`, `#charDrillDiv`. Each height (250px / 280px / 280px / 240px) is hardcoded slightly differently.

**Migration target:** Standardize on `chart-h-md` class (260-400px, the canonical token). Container id parametrized through the drill helper.

### 5. CSV export from drill
- Some drills offer CSV export of the displayed data; some don't. Inconsistent.

**Migration target:** Optional `csv` param on the drill helper — if supplied, renders a CSV button in the close-button cluster.

### 6. F18 disclosure footers
- The cardRiskByDim drill (which itself uses `oDr('sec', name)`) shows F18 disclosure on the card. The drill modal doesn't yet repeat the disclosure.
- Other F18-sensitive drills (oDrMetric for 'te', cardRanks drill chain) similarly lack the disclosure inside the modal.

**Migration target:** Drill helper takes optional `f18_disclose: true` and renders the standard footer at the bottom.

### 7. Per-week / `_selectedWeek` highlight
- `oDr`'s time-series chart honors `_selectedWeek` in some paths and not others.
- Other drills are inconsistent.

**Migration target:** The drill chart helper (one wrapper around `Plotly.newPlot`) injects the `_selectedWeek` vertical marker shape automatically when the drill is showing a time-series and `_selectedWeek != null`.

---

## Proposed migration architecture

A single `drillChrome({...})` helper analogous to `tileChromeStrip({...})` for tiles, plus a small set of canonical sub-helpers:

```js
function drillChrome({
  modalId,        // 'drillModal' | 'stockModal' | 'metricModal' | etc.
  title,          // string — modal title
  closeFn,        // string — JS to close the modal (defaults to standard pattern)
  statStrip,      // array of {label, value, color, tooltip} — optional
  rangePills,     // {current, onChange, options=['3M','6M','1Y','3Y','All']} — optional
  chartId,        // chart container id — optional
  csv,            // CSV export function name — optional
  f18Disclose,    // boolean — surface F18 footer
  body,           // string — drill-specific HTML below the chart (peer holdings table, etc.)
  footer,         // string — additional footer content
}){
  // Returns full modal-content HTML.
}
```

Each drill function becomes a thin wrapper that builds its data + invokes `drillChrome(...)`. Example:

```js
function oDrMetric(metric, range){
  // ... compute KPIs, hist, etc. ...
  $('metricContent').innerHTML = drillChrome({
    modalId: 'metricModal',
    title: METRIC_LABELS[metric],
    statStrip: [
      {label: 'Current', value: f2(curr), color: 'var(--txth)'},
      {label: 'Active', value: fp(active), color: activeStyle(active)},
      {label: '1Y Range', value: rangeTxt, color: 'var(--txt)'},
      {label: 'Δ vs benchmark', value: fp(deltaBm), color: deltaColor},
    ],
    rangePills: {current: range, onChange: 'oDrMetric(\''+metric+'\','},
    chartId: 'metricDrillDiv',
    csv: 'exportMetricDrillCsv("'+metric+'")',
    f18Disclose: metric === 'te',
    body: '',
    footer: '',
  });
  $('metricModal').classList.add('show');
  // ... Plotly.newPlot('metricDrillDiv', ...) ...
}
```

After migration: ~8 drill functions × ~30 lines of inline chrome each = **~240 lines of inline chrome → ~80 lines of declarative configs.** Adding a feature (e.g., "show synth marker on cumulative impact across ALL drills") becomes one edit in `drillChrome`, not 8.

---

## Migration phases

This is meant as a sequenced migration, not a one-shot rewrite.

| Phase | Scope | Estimate | Risk |
|---|---|---|---|
| **A — Build helpers** | `drillChrome()`, `_drillStatStrip()`, `_drillRangePills()`, `_drillCloseBtn()`, `_drillF18Footer()`. Wire into `_drillChartLayout(div, layout)` for the `_selectedWeek` marker injection. | 1.5-2 hr | Low (additive — no existing drill behavior changes) |
| **B — Migrate `oDrMetric` first** (canary) | The richest drill (KPI strip + range pills + reference bands + variant table). If the helpers can express oDrMetric cleanly, they can express the others. | 1 hr | Low (canary, easy rollback) |
| **C — Migrate `oDr` and `oDrF`** | The two highest-traffic drills. Both share `#drillModal` overlay. | 1 hr | Medium (state vars `_drillRange` / `_facDrillRange` need careful handling) |
| **D — Migrate `oDrCountry`, `oDrChar`, `oDrAttrib`** | Lower-traffic but consistent shape. | 1 hr | Low |
| **E — Migrate `oSt`, `oDrUnowned`** | Per-stock drills. Shape diverges most from the others — may need a sub-variant of drillChrome (`stockChrome`). | 1.5 hr | Medium |
| **F — F18 disclosure pass** | Once all drills go through the helper, flip `f18Disclose: true` on TE-related drills + audit the result. | 30 min | Low |
| **G — Cleanup** | Delete dead inline code; smoke test; cross-tile in-browser audit cycle. | 30 min | Low |

**Total: ~6-7 hours.** Should ship as a single tag (`refactor.YYYYMMDD.drill-modal-complete`) after all phases land + smoke + visual diff vs baseline.

---

## What's intentionally NOT in scope

- **Adding new drill features.** This is a chrome refactor, not a UX redesign. New features ship after the migration as a separate phase.
- **Modal stacking / z-index audit.** Some drills can open over fullscreen views. Existing behavior preserved; not part of this migration.
- **The full-screen modals** (`secFsModal`, `riskBudgetModal`) — those are a different beast (whole-tile fullscreen) and have their own pattern. Out of scope here.
- **Drill-modal-from-keyboard navigation.** Existing keyboard handlers (`_drillKeyHandler`) are wired separately and stay as-is.

---

## Smoke test gates per phase

Before tagging each phase complete:

1. **Visual diff** — open the dashboard, open each drill, screenshot. Compare to baseline.
2. **Function diff** — every drill behavior previously available still works (range buttons, click-through, close, ESC, click-outside-to-close).
3. **`smoke_test.sh --quick`** — must stay 20/21 (parse-bomb pre-existing) or better.
4. **Tag** — `refactor.YYYYMMDD.HHMM.phase-X-drill-canary` etc.

---

## Open questions for PM

1. **Should `oSt` get the full `drillChrome` treatment, or stay separate?**
   The stock drill is the most-used drill on the dashboard. Some users may have keyboard / interaction patterns built around its current shape. Migrating it will land last (Phase E) and should pass an extra-careful in-browser review.

2. **F18 disclosure inside drills — same wording as the tile, or a shorter variant?**
   The tile-level F18 footer is full-prose ("Σ %T = X% — see F18..."). The drill is smaller real estate. Recommendation: same wording in a smaller font, but PM may prefer different.

3. **Should the drill-helper add a "report bug" button?**
   Currently right-click on the tile opens a note popup. Drills don't have an equivalent. Could add a small "report" pill near the close button that surfaces a textarea + preset error template. Useful for the PM-onboarding flow (see PM_ONBOARDING.md "When something looks wrong").

When the user signs off on (1) and (2), Phase A can start. (3) is optional and can defer.
