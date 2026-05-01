# TableSpec — Design Sketch

**Goal:** every table in the dashboard is declared once + rendered identically. New features (column hide/show, filter, sort, CSV, fullscreen) ship to all tables by editing one place.

**Non-goals:**
- Replacing Plotly chart tiles. Charts stay as-is for now.
- Replacing modal drill tables (cardCountry drill, TE breakdown modal). Phase 2.
- Visual redesign. Migrate to spec first, design polish second.

---

## API

```js
// Single declarative spec per table
TABLES.sec = {
  // Identity
  id: 'tbl-sec',
  tileId: 'cardSectors',          // for chrome integration
  csvName: 'sectors',

  // Data — function so it re-evaluates per week
  data: () => _wSec(),            // already per-week-aware
  hold: () => cs.hold,            // for holdings-aggregation columns (if any)

  // Columns — rendered in order
  columns: [
    {
      key: 'n',
      label: 'Sector',
      type: 'text',
      sticky: true,               // pinned left, can't hide
    },
    {
      key: 'p',
      label: 'Port %',
      type: 'pct1',
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    {
      key: 'b',
      label: 'Bench %',
      type: 'pct1',
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    {
      key: 'a',
      label: 'Active %',
      type: 'pct1signed',          // signed colors green/red
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    {
      key: 'tr',
      label: 'TE Contrib',
      type: 'pct1',
      renderer: 'teBar',           // custom renderer for the signed bar
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    {
      key: 'mcr',
      label: 'Stock TE',
      type: 'pct1',
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    // Computed column — not in raw data
    {
      key: '_factorTe',
      label: 'Factor TE',
      type: 'pct1',
      compute: (row) => row.tr - row.mcr,
      hideable: true,
      defaultVisible: true,
      sortable: true,
    },
    {
      key: 'over', label: 'O', type: 'rank', hideable: true, defaultVisible: true,
      group: 'spotlight',          // grouping for column-hide UI
    },
    {
      key: 'rev',  label: 'R', type: 'rank', hideable: true, defaultVisible: true, group: 'spotlight',
    },
    {
      key: 'val',  label: 'V', type: 'rank', hideable: true, defaultVisible: true, group: 'spotlight',
    },
    {
      key: 'qual', label: 'Q', type: 'rank', hideable: true, defaultVisible: true, group: 'spotlight',
    },
    // Per-factor TE breakdown — auto-generated for each factor in RNK_FACTOR_COLS.
    // Will be expanded into N columns at render time.
    {
      key: '_factorBreakdown',
      type: 'expand',
      expandFrom: () => RNK_FACTOR_COLS,  // ['Momentum','Value','Growth','Profitability','Size','Volatility']
      labelFor: (factor) => SHORT_FAC_LABEL[factor] || factor,
      valueFor: (row, factor) => factorAgg[row.n]?.factor?.[factor] ?? null,
      type: 'pct2signed',
      hideable: true,
      defaultVisible: true,
      group: 'factor_breakdown',
      histModeBehavior: 'blank',   // — in hist mode (data is latest-only)
    },
    {
      key: '_trend',
      label: 'Trend',
      type: 'sparkline',
      sparklineData: (row) => cs.hist?.sec?.[row.n],
      hideable: true,
      defaultVisible: true,
    },
  ],

  // Sorting / filtering
  defaultSort: { key:'tr', dir:'desc' },
  searchable: ['n'],               // which keys participate in free-text search

  // Drill behavior — clicking a row
  rowClick: (row) => oDr('sec', row.n),

  // Row classes (for highlighting alerts)
  rowClass: (row) => Math.abs(row.a||0) > 5 ? 'thresh-alert'
                   : Math.abs(row.a||0) > 3 ? 'thresh-warn' : '',

  // Aggregation hint — for the section-aggregate vs holdings-sum decision.
  // Renderer uses spec.data() → per-week dim entries (section aggregate),
  // and spec.hold() → for the per-holding factor breakdown columns only.
  preferSectionAggregate: true,    // already the right default after 2026-05-01 fix
};
```

## Renderer signature

```js
// One function — produces the entire table's HTML.
function renderTable(spec) {
  const data = spec.data();
  const visibleCols = visibleColumns(spec);   // applies user's hide/show preferences
  const sortedData = sortData(data, getSortState(spec.id));
  const filteredData = applyFilters(sortedData, getFilterState(spec.id));
  // Build header row from visibleCols
  // Build body rows by iterating filteredData × visibleCols, looking up cell renderer per column type
  // Build empty-state if no rows
  // Hook drill onclick + sort onclick + row-class
  return `<table id="${spec.id}">…</table>`;
}

// Per-column hide/show panel — sits next to the existing filter button
function tableFilterPanel(spec) {
  const groups = groupColumnsBy(spec.columns, c => c.group || 'main');
  // Renders a popover with checkboxes per column, grouped, with Reset
  return `<div class="col-hide-panel">…</div>`;
}

// CSV export uses the same visible columns + applied filter
function exportTableCsv(spec) { … }

// Fullscreen — calls openTileFullscreen with table-aware enrichment
// (KPI summary tiles for sectors, etc.)
```

## State management

Per-table state stored under one key in localStorage:

```
rr.tableState.v1 = {
  'tbl-sec': {
    hidden: ['mcr', '_factorBreakdown:Volatility'],
    sort:   { key:'tr', dir:'desc' },
    filters: { 'a': { op:'>=', val:1 } },
  },
  'tbl-ctry': { … },
}
```

- `hidden` overrides `defaultVisible: true`
- `sort` defaults to `spec.defaultSort` if missing
- `filters` is empty by default (no filtering)

## Column types

| Type | Format | Notes |
|---|---|---|
| `text` | as-is | sortable lexicographically |
| `pct1` | `12.3` | one decimal |
| `pct1signed` | `+12.3` / `-12.3` | green positive, red negative when active wt |
| `pct2signed` | `+1.23` | two decimals signed |
| `rank` | `2.5` | colored 1=green to 5=red |
| `sparkline` | inline SVG | renderer reads `spec.column.sparklineData(row)` |
| `teBar` | bar + number | center-axis signed bar — existing rWt() pattern |

## Column-hide UI integration

Where the user clicks for column hide/show:

- **Existing pattern**: tile chrome has a column-picker button (e.g. cardSectors has the `secColDropHtml()` `⚙ Cols` dropdown). It already drives column visibility for some columns.
- **Proposed unification**: `tableFilterPanel(spec)` becomes the single source. The existing `⚙ Cols` button calls into it. Existing column visibility state migrates into `rr.tableState.v1[id].hidden`.
- **Filter-panel co-location**: per the user's instruction, the column hide/show controls should sit "under the filtering panel" — same overlay, two sections (`filters` + `columns`).

## Migration strategy — visual + functional parity

1. Build `renderTable(spec)` + supporting helpers.
2. Build `TABLES.sec` spec for cardSectors — match every column the existing `rWt(s.sectors, 'sec', s.hold)` produces.
3. Replace the inline call `${rWt(_wSec(),'sec',s.hold)}` with `${renderTable(TABLES.sec)}`.
4. Visual diff: open dashboard before + after, screenshot both. If they look identical (or new is strictly better), proceed.
5. Smoke test: `node` JS parse + render sample, open in Safari, click around.
6. Commit checkpoint. Tag `refactor.YYYYMMDD.HHMM.tablespec-cardSectors-canary`.
7. Then migrate cardCountry, cardGroups, cardRegions, cardChars, cardAttrib, cardFacDetail one at a time. Each ~30 min.

## Risk register

| Risk | Mitigation |
|---|---|
| New renderer behaves subtly differently → silent data leak | Smoke test renders both old + new, compare HTML diff. Differ tool below. |
| Column-picker state diverges between old and new | Migration script: read old state from existing localStorage keys, write into `rr.tableState.v1`. |
| Sort direction off-by-one | Test cases: sort by `a` desc on cardSectors should put highest active wt first. |
| Sparkline renderer doesn't match | Reuse `inlineSparkSvgV2()` as-is — pass through `spec.column.sparklineData(row)`. |
| Drill click breaks | Test: clicking a sector row opens the sector drill modal. |
| Per-holding factor-breakdown columns wrong | Reuse `factorAgg` machinery. Don't reinvent. |

## Differ tool — tablespec-diff

Quick CLI that:
1. Reads two HTML strings (old `rWt()` output, new `renderTable(spec)` output)
2. Normalizes whitespace + attribute order
3. Reports cell-by-cell diff

Use this on every migration to confirm parity before committing.

```js
// Inline browser console:
function diffTableHtml(htmlA, htmlB) {
  const parse = h => Array.from(new DOMParser().parseFromString(h, 'text/html').querySelectorAll('tr')).map(tr =>
    Array.from(tr.children).map(td => td.textContent.trim())
  );
  const a = parse(htmlA), b = parse(htmlB);
  // Compare row-by-row, cell-by-cell, log diffs
}
```

## What's deliberately NOT in scope

- Modal drill tables (cardCountry drill, TE breakdown drill modal, holding drill)
- Holdings table (cardHoldings) — biggest table, more complex sort/filter/cards-vs-table view. Phase 2.
- Watchlist table — small, special — skip.
- Plotly charts / sparklines (already standardized via `inlineSparkSvgV2`)

---

**Approval before code change:** approve the spec / API above, or push back on any choice.
