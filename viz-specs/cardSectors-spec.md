# cardSectors viz spec — chart-view rebuild + trend sparkline upgrade

**Drafted:** 2026-04-27
**Author:** data-viz framework (executed inline; see `~/.claude/agents/data-viz.md`)
**Coordinator:** main session
**Replaces:**
- The "Chart" view of cardSectors (currently a simple bar chart of port-vs-bench weights at line ~rSecChart) — flagged "pale in comparison to the table"
- The Trend sparkline column inside the table — currently a single-line active-weight sparkline via `inlineSparkSvg(series, win)` at line ~1869 — flagged "too simple"

## User intent

The PM scans cardSectors looking for: "where is my biggest TE coming from, AND is my off-benchmark stance justified by stock quality?" The current chart (port-vs-bench bars) shows ONE dim. The table next to it shows 17 columns. The chart should show at least 4 of those dims, simultaneously, with quick-read encoding.

For the sparkline: in 72px wide × 22px tall, encode 2 simultaneous time-series (active weight AND TE contribution) so the PM can see at a glance whether a sector's TE is rising or falling along with its bet size.

---

## Source data

| Field | Path | Type | Coverage | Used in current viz? |
|---|---|---|---|---|
| Sector name | `cs.sectors[].n` | str | 100% | Yes (x-axis) |
| Port wt | `cs.sectors[].p` | num | 100% | Yes |
| Bench wt | `cs.sectors[].b` | num | 100% | Yes |
| Active wt | `cs.sectors[].a` | num | 100% | No (derivable) |
| TE contrib | `factorAgg[name].tr` | num | 100% w/ hold | No |
| Stock-spec TE | `factorAgg[name].mcr` | num | 100% w/ hold | No |
| Avg Overall rank | `factorAgg[name].avg.over` (or weighted via accumulators) | num | 100% w/ ranks | No |
| Holdings count | `factorAgg[name].count` | int | 100% w/ hold | No |
| Factor-contrib breakdown | `factorAgg[name].factor[fname]` | num | 100% w/ hold | No |
| Active-wt history | `cs.hist.sec[name][].a` | series | varies (B6 backlog — hist.sec sparse) | Yes (sparkline) |
| TE-contrib history | (not present — would need to derive from `cs.hist.sec[name][].tr` IF parser starts emitting it) | — | 0% currently | No |

**Important:** `cs.hist.sec[name]` exists for some sectors but has only 1-3 monthly entries. Until `factset_parser.py` writes weekly TE history per sector (B6 backlog), the dual-encoded sparkline can only fall back to a single time-series and overlay the *current* TE contrib as a static colored band — better than nothing, but not full dual-time-series. Document the limitation in tooltip.

---

## Recommended design — Chart view: 4D quadrant scatter

### Why this design wins

A quadrant scatter naturally encodes the 4 most-decision-relevant dims of a sector view in a single plot, with the *position* channel (the most-accurately decoded preattentive variable) reserved for the most important pair.

| Channel | Dimension | Reasoning |
|---|---|---|
| x position | Active weight (% port − % bench) | "How much off-benchmark am I?" — primary policy decision |
| y position | TE contribution (% T) | "How much risk is this position generating?" — primary risk decision |
| Marker size | Port weight | "How big is the actual position?" — context |
| Marker color | Avg Overall MFR rank (1=best=green, 5=worst=red) | "Is the stance justified by stock quality?" — quality judgment |
| Marker text label | Sector short name (4 chars) | Direct labeling — no legend needed |

**Quadrant interpretation** (axis lines at x=0 and y=0):
- **Top-right (x>0, y>0):** overweight + adding risk. Green markers = justified (good ranks), red = "why are we long bad stocks?"
- **Top-left (x<0, y>0):** underweight but still adding risk. Bench-only holdings dragging TE up.
- **Bottom-right (x>0, y<0):** overweight + diversifying — rare, usually a hedge construction.
- **Bottom-left (x<0, y<0):** underweight + diversifying — i.e., the underweight is doing what we hoped.

### Plotly trace config

```javascript
function rSecChartV2(secs, hold) {
  // Pre-compute factorAgg with current _aggMode for color/size encoding
  const fa = aggregateHoldingsBy(hold, h => h.sec, RNK_FACTOR_COLS,
    {mode: _aggMode, avgFields: ['over']});

  const xs = secs.map(d => d.a);                             // active wt
  const ys = secs.map(d => fa[d.n]?.tr ?? 0);                // TE contrib
  const sizes = secs.map(d => Math.max(8, Math.sqrt(d.p) * 8)); // port wt → marker area
  const colors = secs.map(d => {
    const rank = fa[d.n]?.avg?.over;
    if (rank == null) return '#94a3b8';
    return rc(Math.round(rank));   // 1=green, 5=red — existing helper
  });
  const labels = secs.map(d => d.n.split(' ').map(w => w[0]).join('').slice(0, 4));
  const customdata = secs.map(d => ({
    name: d.n,
    p: d.p, b: d.b, a: d.a,
    tr: fa[d.n]?.tr ?? 0,
    mcr: fa[d.n]?.mcr ?? 0,
    rank: fa[d.n]?.avg?.over,
    cnt: fa[d.n]?.count ?? 0
  }));

  const trace = {
    type: 'scatter',
    mode: 'markers+text',
    x: xs, y: ys,
    text: labels,
    textposition: 'top center',
    textfont: { size: 10, color: '#cbd5e1', family: 'DM Sans' },
    marker: {
      size: sizes,
      sizemode: 'diameter',
      color: colors,
      line: { color: 'rgba(255,255,255,0.15)', width: 0.5 },
      opacity: 0.85
    },
    customdata: customdata,
    hovertemplate:
      '<b>%{customdata.name}</b><br>' +
      'Port: %{customdata.p:.1f}% / Bench: %{customdata.b:.1f}% / Active: %{customdata.a:+.1f}%<br>' +
      'TE Contrib: %{customdata.tr:.2f}% (Stock: %{customdata.mcr:.2f}%)<br>' +
      'Avg Overall Rank: %{customdata.rank:.2f}<br>' +
      'Holdings: %{customdata.cnt}<extra></extra>',
    showlegend: false
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#cbd5e1', family: 'DM Sans, system-ui' },
    xaxis: {
      title: { text: 'Active Weight (%)', font: { size: 11 } },
      zeroline: true, zerolinecolor: 'rgba(148,163,184,0.5)', zerolinewidth: 1,
      gridcolor: 'rgba(148,163,184,0.08)',
      tickformat: '+.0f'
    },
    yaxis: {
      title: { text: 'TE Contribution (%)', font: { size: 11 } },
      zeroline: true, zerolinecolor: 'rgba(148,163,184,0.5)', zerolinewidth: 1,
      gridcolor: 'rgba(148,163,184,0.08)'
    },
    margin: { l: 56, r: 16, t: 12, b: 48 },
    shapes: [
      // Quadrant background tints (very subtle)
      { type: 'rect', xref: 'x', yref: 'y', x0: 0, x1: 'paper', y0: 0, y1: 'paper',
        fillcolor: 'rgba(239,68,68,0.03)', line: { width: 0 }, layer: 'below' },
      { type: 'rect', xref: 'x', yref: 'y', x0: 'paper', x1: 0, y0: 'paper', y1: 0,
        fillcolor: 'rgba(16,185,129,0.03)', line: { width: 0 }, layer: 'below' }
    ],
    annotations: [
      { x: 1, y: 1, xref: 'paper', yref: 'paper', text: 'Overweight + Adding Risk',
        showarrow: false, font: { size: 9, color: 'rgba(239,68,68,0.65)' },
        xanchor: 'right', yanchor: 'top' },
      { x: 0, y: 0, xref: 'paper', yref: 'paper', text: 'Underweight + Diversifying',
        showarrow: false, font: { size: 9, color: 'rgba(16,185,129,0.65)' },
        xanchor: 'left', yanchor: 'bottom' }
    ]
  };

  Plotly.newPlot(div, [trace], layout,
    { displayModeBar: false, responsive: true });

  // Click → drill modal
  div.on('plotly_click', (e) => {
    const cd = e.points[0].customdata;
    oDr('sec', cd.name);
  });
}
```

### Interactions

- **Hover:** rich tooltip with all 4 dims + count + stock-spec split
- **Click marker:** opens existing `oDr('sec', name)` drill modal
- **Universe pill toggle:** chart re-renders via the existing `_rerenderAggTiles()` dispatcher (must add `rSecChartV2` call there)
- **Wtd/Avg pill:** changes the marker color (since rank avg uses _avgMode)
- **Cols picker:** does NOT affect the chart (chart uses fixed 4 dims; the column picker is for table columns only)

### Edge cases

- **Sectors with `count=0` under Port universe** (Energy, Materials, Utilities for EM): plot at `(d.a, 0)` with size=4, color=gray. Direct label still helps.
- **Negative TE contrib:** point appears below y=0; quadrant tinting visually catches it.
- **Wide range:** consider auto-symlog scaling if max(|y|) / median(|y|) > 20. Skip on first ship.
- **Many sectors (>20):** label overlap. Add `Plotly.relayout` to call `Plotly.d3.layout.force()` on labels OR fall back to hover-only labels when n>16.

---

## Recommended design — Trend sparkline upgrade (table cell)

### Why upgrade

72×22px is small but enough for two layers if encoded cleverly. PM wants to see "TE rising while active weight steady" or "active weight grew, did TE follow?"

### Design — layered sparkline

**Layer 1 (base):** Active-weight line, indigo `#6366f1`, line width 1.5px. Same as today.

**Layer 2 (overlay):** TE-contrib history as a colored band fill *behind* the line — green band when TE is negative (diversifying historically), red when positive. Opacity 0.18.

**Layer 3 (current marker):** Solid dot at the rightmost point (last week), color = sign of latest TE.

**Annotation:** Tiny `+` or `−` glyph in the top-left corner indicating the current TE sign.

### SVG sketch

```html
<svg width="72" height="22" viewBox="0 0 72 22">
  <!-- TE contrib band: piecewise rect or path showing positive/negative regions -->
  <rect x="0" y="2" width="72" height="18" fill="rgba(239,68,68,0.18)"/>  <!-- if historically positive -->
  <!-- Active-weight line -->
  <polyline points="..." fill="none" stroke="#6366f1" stroke-width="1.5"/>
  <!-- Current dot -->
  <circle cx="68" cy="10" r="2" fill="#ef4444"/>
  <!-- Sign glyph -->
  <text x="3" y="9" font-size="8" fill="#ef4444">+</text>
</svg>
```

### Helper

`inlineSparkSvgV2(activeSeries, teSeries, win, currentTE)` — extends the existing `inlineSparkSvg` to take an optional second series and a "current sign" value. Falls back to the existing single-series rendering when `teSeries` is missing (which is the case today since `cs.hist.sec[name]` doesn't carry TE — see "Important" note in source-data table).

### Initial-ship limitation

Until `cs.hist.sec[name][].tr` is populated by the parser (B6 backlog), the upgraded sparkline shows:
- Active-weight line (existing data)
- Current TE sign glyph + dot color (current snapshot)
- *No* TE band yet — gracefully omits it

This still beats the current single-line because the PM gets a "+/−" summary of TE state in the same cell.

---

## Alternative designs considered

### Alt A — Multi-axis bar chart (TE bars + active scatter overlay)

x-axis = sector name. Left y-axis = TE contrib (bar, signed). Right y-axis = active weight (scatter overlay). Color of bar = sign. Color of scatter = avg rank.

**Pros:** familiar bar form; sortable.
**Cons:** dual-axis is a known cognitive-load anti-pattern (Cleveland 1985). Plus, it doesn't reveal the QUADRANT relationship between active weight and TE — they're shown as parallel encodings, not paired.
**Reject reason:** quadrant scatter wins because the *relationship* between active and TE is the actual question.

### Alt B — Small-multiples panel (one mini-chart per sector)

11 small panels, each showing port/bench/active history for one sector.

**Pros:** great for "did each sector's position move recently?"
**Cons:** doesn't answer "where's my TE coming from RIGHT NOW?"; also requires `cs.hist.sec` to be richly populated (it isn't — B6 backlog).
**Reject reason:** wrong question for this tile. Would suit a future "sector trajectory" tile.

### Alt C — Heatmap (sectors × factors, cell = factor-contrib)

Rows = 11 sectors. Columns = 6-12 visible factors. Cell color = signed magnitude of `factor_contr[fname]` summed across that sector's holdings.

**Pros:** dense; reveals factor concentration patterns.
**Cons:** doesn't show port/active context — just factor exposure. Better as a *separate* tile (could spec one called `cardSectorFactorMatrix`).
**Reject reason:** complementary, not replacement.

---

## Implementation notes for coordinator

- New function `rSecChartV2(div, secs, hold)` near line ~1690 (where `rSecChart` lives).
- Replace the body of `rSecChart` with `rSecChartV2` — keep the function name so callers don't change.
- Add `if (cs.sectors && document.getElementById('secChart')?.style.display !== 'none') rSecChartV2(...)` to `_rerenderAggTiles()` so the chart updates with universe pill.
- New helper `inlineSparkSvgV2(activeSeries, teSeries, win, currentTESign)` next to existing `inlineSparkSvg`.
- Update sparkCell render in `rWt` to call `inlineSparkSvgV2(sparkSeries, null, sparkWin, teTotal)` (passing `null` for teSeries until B6 lands).
- localStorage prefs: none (no interactive config in the chart yet).
- B115 integrity: chart reads from `cs.sectors[]` and `factorAgg` — both already validated. No new sourcing.

---

## Validation plan

- [ ] Renders cleanly under EM (full data, 11 sectors)
- [ ] Renders cleanly under SCG (sparser holdings, more "Unmapped")
- [ ] Toggle Universe pill (Port → Bench → Both): markers reposition, sizes scale, colors update
- [ ] Toggle Wtd/Avg pill: marker colors shift (rank avg method changes)
- [ ] Cols picker: does NOT change the chart (intentional — chart uses fixed 4 dims)
- [ ] Hover: tooltip shows name, port/bench/active, TE/Stock, rank, count
- [ ] Click marker: opens `oDr('sec', name)` modal
- [ ] No console errors / no Plotly warnings
- [ ] B115 integrity check still passes
- [ ] cardSectors collapse (chart toggle off): clean unmount
- [ ] Sparkline upgrade: every row shows the indigo line + correct +/− glyph at left + colored dot at right end

---

## Estimated implementation effort

- `rSecChartV2`: ~120 lines new code. 30 min.
- `inlineSparkSvgV2`: ~40 lines new code. 15 min.
- Wiring + tests: 30 min.
- Total: **~75 min** of coordinator time.

Open question for user before implementing: should the *same* quadrant chart pattern roll out to cardCountry / cardRegions / cardGroups (consistent UX across the 4 sibling tiles)? Strong default = yes, but cardCountry has 27 buckets which makes label-overlap harder; might need a "show top-N by |TE|" filter.
