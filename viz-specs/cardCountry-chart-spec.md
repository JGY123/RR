# cardCountry chart-view rebuild — spec

**Drafted:** 2026-04-28
**Replaces:** `rCountryChart` (currently top-5/bottom-5 horizontal bar of active weights)

## User intent

User feedback round 1 Q4: "the chart needs ton of work, it's too simple — be creative and come up with much more sophisticated and useful chart."

For the country tile, the **map** already shows one variable per country geographically, and the **table** already shows every metric numerically. The chart-view should not duplicate either — it should show a dimension neither of them shows well.

## Recommended viz: Country × Factor TE Heatmap

### Why this design wins

- **Map shows 1 var × 27 countries.** **Table shows ~20 vars × 27 countries** as numbers. Neither makes "which countries drive which factors" answerable at a glance.
- A country×factor heatmap with cells colored by signed TE contribution creates instant pattern recognition: "Brazil + Indonesia are our two big Volatility contributors", "China's weight contribution is dominating Size factor".
- Sized for fit: 27 countries × 6 default factor columns = 162 cells. Comfortable. With factor-col picker expanded to 12, it's 324 cells — still readable.
- One row brightening across 3+ cells = a country with multiple factor exposures
- One column brightening across 3+ rows = a factor concentrated in a few countries

### Encoding

| Channel | Variable |
|---|---|
| y axis | Country (sorted by `|total TE|` desc, top-N controlled by existing pill) |
| x axis | Factor name (uses `_facCols` so the global ⚙ Cols picker drives both this chart AND the table's Factor TE Breakdown columns) |
| cell color | Signed factor TE contribution per country (Σ `h.factor_contr[fname]` for country's holdings, under current Universe pill mode) |
| cell text | Numeric value (1-decimal) shown on hover and as overlay if cell is large enough |
| color scale | Diverging: green (`#10b981`) = diversifies (negative) → neutral → red (`#ef4444`) = adds risk (positive) |

### Plotly trace config (sketch)

```javascript
const factorCols = RNK_FACTOR_COLS;  // user-picked subset
const countries = [...filtered].sort((a,b) => Math.abs(aggTE(b.n)) - Math.abs(aggTE(a.n))).slice(0, _ctryTopN || 27);
const z = countries.map(c => factorCols.map(f => factorAggCtry[c.n]?.factor[f] ?? 0));
const absMax = Math.max(0.5, ...z.flat().map(Math.abs));

Plotly.newPlot('countryChartDiv', [{
  type: 'heatmap',
  x: factorCols.map(shortLabel),
  y: countries.map(c => c.n),
  z: z,
  colorscale: [[0,'#10b981'], [0.5,'#1e293b'], [1,'#ef4444']],
  zmin: -absMax, zmid: 0, zmax: absMax,
  customdata: countries.map(c => factorCols.map(f => [c.n, f, factorAggCtry[c.n]?.factor[f] ?? 0])),
  hovertemplate: '<b>%{customdata[0]}</b><br>Factor: %{customdata[1]}<br>TE Contribution: %{customdata[2]:.2f}%<extra></extra>',
  colorbar: { title: 'TE Contribution', thickness: 12, len: 0.8, ticksuffix: '%' }
}], {
  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
  font: { color: '#cbd5e1', family: 'DM Sans' },
  xaxis: { side: 'top' },
  yaxis: { autorange: 'reversed' },
  margin: { l: 130, r: 50, t: 60, b: 20 }
}, { displayModeBar: false, responsive: true });
```

### Interactions

- **Hover:** rich tooltip with country, factor name, exact contribution
- **Click on a cell:** opens drill modal filtered to that country's holdings, sorted by `factor_contr[fname]` (so user sees which specific stocks drive that factor in that country)
- **Universe pill:** flips `factorAggCtry` between port / bench / both — heatmap re-renders
- **Cols picker:** the same ⚙ Cols picker that controls table factor cols also controls heatmap x-axis. Toggling Yield in/out adds/removes that column.
- **Top-N pill:** drives the y-axis depth (10/20/30/All countries by |TE|)

### Edge cases

- **Country with no holdings under current universe:** filter out (don't render zero rows)
- **Factor with all-zero contributions:** still render the column (consistency with table)
- **Bench-only universe:** factor_contr is computed across bench holdings; some countries may show zero if no bench holdings classified

### Why not other options

- **Quadrant scatter (cardSectors-style):** rejected per user direction "different tiles need different viz."
- **Multi-line time-series:** good but inflates the chart panel; better as a future tab.
- **Stacked area of TE over time:** good for trend but doesn't show factor decomposition.
- **Sankey country→industry→factor:** information-rich but visually heavy + hard to read for >10 countries.

### Implementation notes

- New helper `_aggregateCountryByFactor(s)` — Σ h.factor_contr per country, respects `_aggMode`.
- Replace body of `rCountryChart(s)` with the heatmap renderer.
- Wire into `_rerenderAggTiles` so Universe / Cols / Top-N changes propagate.
- ~80 lines new code, replaces ~10 lines of bar chart.

### Validation plan

- [ ] EM data: heatmap renders 27 rows × 6 default factor cols; clicking Brazil×Volatility opens drill of Brazilian holdings sorted by Volatility factor_contr
- [ ] Universe pill: flipping Bench shows benchmark-side heatmap (different colors)
- [ ] Cols picker: removing Size collapses one column; adding Liquidity adds one
- [ ] Top-N pill: 10 → 10 rows, 30 → all 27 (capped)
- [ ] No console errors; hovertemplate renders cleanly
