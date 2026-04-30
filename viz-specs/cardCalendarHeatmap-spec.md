# cardCalendarHeatmap viz spec

**Drafted:** 2026-04-30
**Author:** data-viz subagent
**Coordinator:** main session
**Source brief:** NEW_TILE_CANDIDATES.md candidate #4 (highest ROI, ~1 day effort)
**Status:** Spec only — no implementation. Coordinator decides priority.

## User intent

Give the PM a single-glance long-horizon view of TE history that doubles as a navigation device. Answers two questions in one tile:

1. **"When were the volatile weeks?"** — pattern-detect clusters of high |ΔTE| weeks vs. dead periods.
2. **"Take me there."** — click any cell → global week selector jumps to that week → entire dashboard re-renders.

Existing tiles (`cardRiskHistTrends`, `cardTEStacked`) show TE as a continuous line. They're great for trend reading but bad for *picking out individual weeks* and impossible to use as a date picker. This is the GitHub-contribution-graph pattern applied to TE.

## Source data

| Field | Path | Type | Coverage | Used in current viz? |
|---|---|---|---|---|
| Week date | `cs.hist.sum[i].d` | string `YYYYMMDD` | All weeks (~69 GSC, ~150+ multi-yr) | Yes — sparklines |
| Tracking Error | `cs.hist.sum[i].te` | number, % annualized | All weeks | Yes — `miniTE` |
| ΔTE (computed) | `te[i] - te[i-1]` | number, signed | All weeks except first | **No — new derivation, marked ᵉ** |
| Selected week | `_selectedWeek` global | string `YYYYMMDD` or null | Always | Yes — week selector |
| Available dates | `cs.available_dates` / `_availDates` | string[] | Always sorted | Yes |
| Helpers | `parseDate(d)`, `isoDate(d)`, `changeWeek(d)` | functions | Always | Yes |

No parser change needed. `te` is already shipped per week.

## Recommended design

### Visual layout — calendar grid (year rows × week columns)

```
                         ←——— ISO week (1..53) ———→
              W01  W02  W03  W04  W05  W06  W07  W08  W09 ... W52
       2023   ░    ░    ▒    ▓    █    ▓    ▒    ░    ░  ...  ░
       2024   ▒    ▓    █    █    ▓    ░    ░    ▒    ▓  ...  ▓
       2025   ░    ░    ▒    ▒    ▓    █    █    ▓    ▒  ...  ▒
       2026   ░    ▒    ▓    █    ⬛   .    .    .    .       .   ← selected
              ────────────────────────────────────
              Jan       Apr       Jul       Oct     Dec
              ↑ month tick labels ↑

       Legend:  ░ low |ΔTE|     ▒ medium     ▓ high     █ extreme     ⬛ selected
```

**Why year-rows × week-cols (not month-rows):**
- Multi-year files (target: 3-yr) get 3-4 rows; tile stays short (~120-160px tall).
- 53 cols × ~14px each = ~740px wide, fits the full-width tile slot.
- Within-year seasonality is *immediately* visible (compare W12 across rows) — beats a month-grid for pattern detection.
- ISO week numbering already matches FactSet weekly cadence (Friday close).

**Cell dimensions:** 14×14 px with 2px gap. Row height = 16. 53 weeks × 14 + gaps ≈ 740px. Year-label gutter on left (40px). Total tile width: ~800px.

**Edge case — partial years:** Years with no data left transparent. Year row still rendered with the year label so the timeline is honest about missing weeks.

### Color scale — sequential by |ΔTE|, with absolute-TE toggle

Two metric modes (pill toggle, default = ΔTE):

- **|ΔTE| (default)** — magnitude of week-over-week TE change. Best for "when was risk shifting?" Range typically 0..1.5% week-to-week. Sequential palette: indigo `#6366f1` (light → dark, 5 quantile bins).
- **TE level** — raw TE value. Best for "when was risk highest in absolute terms?" Range typically 3..9% for international strategies, 5..12% for SCG. Sequential palette: amber → red (`#f59e0b` → `#ef4444`).

Why sequential, not diverging: |ΔTE| is unsigned (we strip the sign — "volatility of risk", not "direction"). For a directional view, the user uses the existing `cardTEStacked` line chart. Keeping signs separate prevents palette confusion.

**Quantile binning, not linear:** Long-tail distributions in TE moves — one outlier week (e.g. COVID-March-2020) compresses every other week to indistinguishable. 5 quantile bins per the file's actual range. Compute once at render time from the visible series.

**Selected-week marker:** Cell of `_selectedWeek` gets a 1.5px white outline (same visual weight as the existing week-selector amber banner). Cell still shows its color underneath.

**Empty cells (no data for week):** transparent fill, no stroke. Hover does nothing.

**Legend:** Inline below the grid — 5 swatches with min/max numeric labels. Same horizontal real estate as the cardRiskHistTrends sub-titles.

### Hover tooltip

Plotly hovertemplate (or SVG `<title>` if going pure-SVG):

```
Week of 2024-09-12 (W37 2024)
TE: 5.40%  (ΔTE: +0.62 vs prior wk ↑)
Click to jump →
```

Show:
- Full date (`isoDate(d)`)
- ISO week number for context
- TE value
- Signed ΔTE with arrow + comparison phrasing
- Click affordance hint

### Click behavior

```javascript
onclick → changeWeek(cellDate)
```

`changeWeek()` is the existing global. It updates `_selectedWeek`, calls `upd()` (full re-render), the week selector reflects, the amber banner renders. The calendar tile itself re-renders, drawing the new outline on the freshly-selected cell.

Click on an empty cell: no-op.

### Header polish — match cardFacRisk gold standard

```
TE Calendar Heatmap                                     [ ⓘ ]
weekly Δ TE intensity · click to jump · {N} weeks
[ pill: |ΔTE| · TE level ]
```

- Title with tooltip helper (`tip` class) explaining what each cell means.
- Right-click → showNotePopup
- ⓘ button → `aboutBtn('cardCalHeat')`
- Subtitle line — quiet, matches `cardScatter` / `cardChars` subtitle styling.
- Pill toggle for metric mode (|ΔTE| default; TE level alternate). Persists in `localStorage` under `rr.calheat.metric` (preferences-only per CLAUDE.md hard rule #3).
- Legend swatches inline beneath grid (5 bins + label).

## Plotly trace config (sketch)

```javascript
function rCalHeat(){
  const hist = (cs && cs.hist && cs.hist.sum) || [];
  if(hist.length < 2){
    document.getElementById('calHeatDiv').innerHTML =
      '<div style="display:flex;align-items:center;justify-content:center;height:140px;color:var(--txt);font-size:11px">Need ≥2 weeks of TE history</div>';
    return;
  }
  const metric = (localStorage.getItem('rr.calheat.metric') || 'dte');
  // Build z-matrix: rows = years, cols = ISO weeks 1..53
  const years = [...new Set(hist.map(h => +isoDate(h.d).slice(0,4)))].sort();
  const wkMap = new Map(); // (year,week) -> {te, dte, d}
  hist.forEach((h,i) => {
    const dt = parseDate(h.d);
    const yr = dt.getFullYear();
    const wk = isoWeekNum(dt);                    // 1..53
    const dte = i>0 ? +(h.te - hist[i-1].te).toFixed(3) : null;
    wkMap.set(`${yr}-${wk}`, {d:h.d, te:h.te, dte, dteAbs:dte==null?null:Math.abs(dte)});
  });
  const z = years.map(yr => {
    const row = new Array(53).fill(null);
    for(let w=1; w<=53; w++){
      const e = wkMap.get(`${yr}-${w}`);
      if(e) row[w-1] = (metric==='dte' ? e.dteAbs : e.te);
    }
    return row;
  });
  const customdata = years.map(yr => {
    const row = new Array(53).fill(null);
    for(let w=1; w<=53; w++){
      const e = wkMap.get(`${yr}-${w}`);
      if(e) row[w-1] = [e.d, e.te, e.dte];
    }
    return row;
  });
  const colorscale = metric==='dte'
    ? [[0,'rgba(99,102,241,0.10)'],[0.25,'rgba(99,102,241,0.30)'],[0.5,'rgba(99,102,241,0.55)'],[0.75,'rgba(99,102,241,0.80)'],[1,'rgba(99,102,241,1.0)']]
    : [[0,'rgba(245,158,11,0.20)'],[0.5,'rgba(245,158,11,0.65)'],[1,'rgba(239,68,68,1.0)']];
  Plotly.newPlot('calHeatDiv',[{
    type:'heatmap', z, customdata,
    x: Array.from({length:53},(_,i)=>'W'+String(i+1).padStart(2,'0')),
    y: years.map(String),
    colorscale, showscale:false,
    xgap:2, ygap:2,
    hovertemplate: metric==='dte'
      ? '<b>Week of %{customdata[0]}</b><br>TE: %{customdata[1]:.2f}%<br>ΔTE: %{customdata[2]:+.2f}<br><i>Click to jump</i><extra></extra>'
      : '<b>Week of %{customdata[0]}</b><br>TE: %{customdata[1]:.2f}%<br>ΔTE: %{customdata[2]:+.2f}<br><i>Click to jump</i><extra></extra>',
    hoverongaps:false
  }],{
    paper_bgcolor:'transparent', plot_bgcolor:'transparent',
    font:{color:'#cbd5e1', family:'DM Sans, system-ui'},
    margin:{l:42, r:8, t:6, b:32},
    xaxis:{
      tickmode:'array',
      tickvals:['W01','W05','W09','W14','W18','W23','W27','W31','W36','W40','W44','W49'],
      ticktext:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
      showgrid:false, fixedrange:true, side:'bottom', tickfont:{size:9}
    },
    yaxis:{showgrid:false, fixedrange:true, tickfont:{size:10}, autorange:'reversed'}
  },{displayModeBar:false, responsive:true});
  // Click handler — jump global week selector
  document.getElementById('calHeatDiv').on('plotly_click', evt => {
    const cd = evt.points[0].customdata;
    if(cd && cd[0]) changeWeek(cd[0]);
  });
  // Selected-week outline overlay (Plotly shape)
  if(_selectedWeek){
    const dt=parseDate(_selectedWeek);
    Plotly.relayout('calHeatDiv',{shapes:[{
      type:'rect', xref:'x', yref:'y',
      x0:'W'+String(isoWeekNum(dt)).padStart(2,'0'), x1:'W'+String(isoWeekNum(dt)).padStart(2,'0'),
      y0:String(dt.getFullYear()), y1:String(dt.getFullYear()),
      line:{color:'#fff', width:1.5}
    }]});
  }
}
```

Helper to add (~10 lines, near other date helpers around line 10017):

```javascript
function isoWeekNum(d){
  const t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));
  const dn=t.getUTCDay()||7; t.setUTCDate(t.getUTCDate()+4-dn);
  const ys=new Date(Date.UTC(t.getUTCFullYear(),0,1));
  return Math.ceil(((t-ys)/86400000+1)/7);
}
```

## Implementation recommendation — Plotly heatmap (not inline SVG)

**Recommend Plotly.** Reasons:

1. **Hover infrastructure already there.** `hovertemplate`, `customdata`, click handlers — pre-built. SVG version reinvents tooltips.
2. **Quantile coloring** is one-liner via `colorscale` array. SVG needs manual bin math + repaint logic.
3. **Selected-week outline** uses Plotly `shapes` — re-renders cleanly when `_selectedWeek` changes. SVG needs manual DOM diff.
4. **Comparable size to recommendation.** Plotly version ~120 lines incl. helper; SVG version ~80 lines but missing hover and selected-week reactivity. Net cost roughly equal once SVG version is feature-complete.
5. **Consistent with cardRiskHistTrends, cardTEStacked, cardBetaHist** — all use Plotly heatmap or scatter. Style consistency wins here.

The one place inline SVG wins (table-cell sparklines, where Plotly overhead per cell is too high) doesn't apply at tile scale.

**Function name:** `rCalHeat` (matches existing `rRisk`, `rRiskHistMinis` style).
**DOM container id:** `calHeatDiv` (matches `scatDiv`, `treeDiv`, `mcrDiv` style).
**Card wrapper id:** `cardCalHeat` (matches `cardScatter`, `cardMCR`).

## Where to insert in the page layout

**Recommendation: Risk tab, immediately above `cardRiskHistTrends`.**

Reasons:
- The Risk tab is the analyst-time-axis tab. Calendar belongs there with TE Stacked + Beta History + Historical Trends — they share the time dimension as a primary axis.
- Sticking it on Exposures (between Row 6 and Row 7) breaks the "snapshot of right now" theme of that tab.
- Above `cardRiskHistTrends` makes the tile pair: calendar (long-horizon overview) → trend minis (4-metric current state) → drilldowns. Reading order: macro → meso → micro.

**Wire-up:**
- Insert `<div class="card" id="cardCalHeat" style="margin-bottom:16px">` directly before the `cardRiskHistTrends` card in the Risk tab's HTML template.
- Add `rCalHeat()` call in the Risk-tab render path (wherever `rRiskHistMinis(s)` is invoked).
- Add `rCalHeat()` call to `changeWeek()` so the selection outline re-renders without rebuilding the whole tab.
  - Or simpler: rely on the full `upd()` re-render and accept one extra heatmap repaint per week click (~30ms — negligible).

## Header HTML sketch

```html
<div class="card" id="cardCalHeat" style="margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
    <div class="card-title tip"
         data-tip="Calendar of weekly TE intensity. Each cell = one week; color = magnitude of ΔTE (default) or absolute TE level. Click any cell to jump the dashboard to that week. Right-click for notes."
         oncontextmenu="showNotePopup(event,'cardCalHeat');return false"
         style="margin-bottom:0">
      TE Calendar Heatmap
      <span style="font-size:10px;color:var(--txt);font-weight:400;margin-left:8px">
        ${hist.length} week${hist.length===1?'':'s'} · click to jump
      </span>
    </div>
    ${aboutBtn('cardCalHeat')}
    <div style="margin-left:auto;display:flex;align-items:center;gap:6px">
      <span style="font-size:9px;color:var(--textDim);font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Color by</span>
      <button class="pill ${metric==='dte'?'active':''}" onclick="setCalHeatMetric('dte')">|ΔTE|</button>
      <button class="pill ${metric==='te'?'active':''}" onclick="setCalHeatMetric('te')">TE level</button>
    </div>
  </div>
  <div id="calHeatDiv" style="height:160px;min-height:120px"></div>
  <div id="calHeatLegend" style="display:flex;gap:6px;align-items:center;margin-top:6px;font-size:10px;color:var(--txt)"></div>
</div>
```

`setCalHeatMetric(m)` — small helper that writes to `localStorage.rr.calheat.metric`, then calls `rCalHeat()`.

## Edge cases

- **<2 weeks of data:** render placeholder text "Need ≥2 weeks of TE history" (matches cardRiskHistTrends pattern).
- **Single year, partial:** still render — empty week cells transparent.
- **Multi-year file with gaps:** transparent for missing weeks; year row still labeled.
- **TE = null for a week:** treat as missing data; no cell. (Should never happen — `te` is in the Data row.)
- **First week of series:** `dte` is null; in |ΔTE| mode the cell is rendered but coloring uses `te` value as fallback OR the cell is left transparent. Recommend transparent — clearer signal that there's no comparison baseline.
- **Strategy switch / data reload:** `rCalHeat()` is called from `upd()`, so it re-runs naturally.
- **Theme toggle (dark ↔ light):** colorscale is fixed RGBA; works on both. Title uses CSS vars.

## Validation plan

- [ ] Renders correctly under GSC (~69 weeks)
- [ ] Renders correctly under any 1-year strategy (~52 weeks, single row)
- [ ] Renders correctly with multi-year sample when available (3 rows)
- [ ] Switching strategies updates the heatmap
- [ ] Clicking a cell jumps the week selector + amber banner appears
- [ ] Clicking the same cell again is idempotent (re-jumps to same week)
- [ ] |ΔTE| ↔ TE level pill swaps the palette + hovertemplate text
- [ ] Selected-week outline renders + moves on every `changeWeek()`
- [ ] Hover shows date + TE + ΔTE + click hint
- [ ] About-popup shows correct What/How/Source/Caveats
- [ ] No console errors
- [ ] B115 integrity check still passes
- [ ] Theme toggle (dark/light) — palette readable on both
- [ ] localStorage `rr.calheat.metric` persists across reload

## About-popup entry

Add to `_ABOUT_REG` (currently at line 661 of dashboard_v7.html):

```javascript
cardCalHeat:{
  title:'TE Calendar Heatmap',
  what:'GitHub-style calendar of weekly tracking-error intensity across the strategy\'s entire history. Each cell is one week; color shows magnitude of week-over-week TE change (|ΔTE|, default) or absolute TE level. Pattern-detects clusters of high-volatility weeks, dead periods, and regime shifts. Doubles as a navigation device — click any cell to jump the global week selector to that week.',
  how:'Cells laid out as years (rows) × ISO weeks 1-53 (cols). |ΔTE| computed as |te[i] − te[i−1]| from cs.hist.sum (marked ᵉ — derived). TE-level mode shows raw te value. Color scale uses 5 quantile bins computed from the visible series so outliers don\'t flatten the rest. Selected week gets a white outline. Click handler calls changeWeek(cellDate) which updates _selectedWeek and triggers a full re-render.',
  source:'cs.hist.sum[].d (week date) + cs.hist.sum[].te (tracking error). Same primitive series that powers cardRiskHistTrends miniTE. ΔTE is computed in this tile only — synth-marked.',
  caveats:'Requires ≥2 weeks for any visible cells. First week always blank in |ΔTE| mode (no prior to diff against). Long-tail outlier weeks compressed by quantile binning — hover for exact value. ISO week numbering may put a few late-December weeks in W53 (rare). Click-to-jump is the only interactive — pan/zoom disabled.',
  related:'cardRiskHistTrends (same metric, line view) · cardTEStacked (TE decomposition over time) · cardBetaHist · TE drill modal'
}
```

## Implementation notes for coordinator

1. **Insertion point:** Risk tab HTML, immediately before the existing `cardRiskHistTrends` card (function `rRiskHist` returns the card; insert `cardCalHeat` block above it in the same template literal).
2. **New functions:** `rCalHeat()`, `setCalHeatMetric(m)`, `isoWeekNum(d)`. All near line 5489 (next to other Risk-tab renders) except `isoWeekNum` which goes next to `parseDate`/`isoDate` around line 10017.
3. **Re-render hook:** In the Risk-tab render path, call `rCalHeat()` after `rRiskHistMinis(s)`. Also called from `upd()` because the whole Risk panel re-renders on every `changeWeek()`.
4. **localStorage key:** `rr.calheat.metric` — value is `'dte'` or `'te'`. Per CLAUDE.md rule #3 this is preferences-only, never data.
5. **Anti-fabrication:** ΔTE is a derived value. Add `ᵉ` marker to ΔTE in the hover tooltip. Document the derivation in `SOURCES.md` under a new entry for `cardCalHeat`.
6. **B115 integrity check:** No new asserts needed — `te` is already covered.
7. **Smoke test:** before commit, `./smoke_test.sh --quick` to ensure no template-literal regressions.
8. **Performance:** ~150 cells per year × 3-4 years = ~600 cells. Plotly heatmap handles this trivially. No virtualization needed.

## Alternative designs considered

### Option B — calendar-month grid (one row per month, 7 cols for weekdays-of-month)
**Pros:** True GitHub-style; one cell per day.
**Cons:** We have weekly data, not daily. Would force fake daily expansion. Anti-fabrication violation.
**Reject reason:** Source data is weekly Friday closes — no daily resolution exists. Don't fabricate.

### Option C — single-row strip (all weeks in one long horizontal track)
**Pros:** Simpler markup. No year axis.
**Cons:** Loses year-over-year alignment. Can't compare "Q1 of 2024 vs Q1 of 2025" — the whole point of seasonal pattern detection. With 150+ weeks, becomes a 2000px scroll-strip.
**Reject reason:** Defeats the seasonal-comparison advantage of the calendar metaphor.

### Option D — overlay TE line on the heatmap
**Pros:** Combines absolute level + intensity in one view.
**Cons:** Visual clutter; TE level is already covered by the metric-toggle pill. Cardinal sin: two encodings of the same variable in one frame.
**Reject reason:** Pill-toggle is cleaner. Users get the line view in `cardRiskHistTrends` already.

## Hand-off summary

- **One new tile, one new function (`rCalHeat`), one new helper (`isoWeekNum`), one preferences key.**
- **No parser changes.**
- **No new data primitives** — uses existing `cs.hist.sum[].te` already shipped.
- **Insertion point:** Risk tab, above `cardRiskHistTrends`.
- **Effort:** ~120 lines incl. helper + About entry. ~1 day end-to-end (build + smoke + manual test on multi-strategy).
