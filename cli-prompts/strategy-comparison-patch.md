# Strategy Comparison Mode

## What it does
A new "Compare" button in the header that opens a full-width comparison dashboard showing all 7 strategies side by side. Key metrics, risk profiles, factor tilts, and sector bets at a glance.

## Trigger
Add a "Compare" button next to the strategy dropdown in the header bar. Opens a modal-style overlay.

## Comparison Dashboard Layout (full-screen modal):

### Row 1: Strategy Scorecards (7 columns)
Each strategy gets a mini-card showing:
- Strategy name + benchmark
- TE (color-coded: green <5, amber 5-7, red >7)
- Active Share
- Beta
- Holdings count
- Cash %
- Top sector bet (name + active weight)
- Factor/Idio split as mini stacked bar

### Row 2: TE Comparison Bar Chart
Horizontal bars for all 7 strategies sorted by TE, colored by threshold.
Each bar annotated with the TE value. The selected strategy highlighted.

### Row 3: Factor Exposure Heatmap
Matrix: 7 strategies (columns) × 12 style factors (rows)
Cell color = active exposure intensity (diverging green/red)
Cell text = exposure value
Instantly shows which strategies share factor tilts and which diverge.

### Row 4: Sector Bet Comparison
Matrix: 7 strategies (columns) × 11 sectors (rows)
Cell = active weight, colored green (OW) / red (UW)
Highlights the biggest bets across the firm.

### Row 5: Holdings Overlap
Table showing holdings owned by 2+ strategies:
Ticker | Name | Strategies (pills) | Avg Weight | Avg Active | Avg TE Contrib
Sorted by number of strategies (most shared first).

## Data source
All data comes from the global `A` object which has all 7 strategies pre-loaded:
```javascript
let strats = Object.keys(A).map(sid => ({
  id: sid, s: A[sid],
  te: A[sid].sum.te, beta: A[sid].sum.beta, as: A[sid].sum.as,
  h: A[sid].sum.h, cash: A[sid].sum.cash,
  pctSpec: A[sid].sum.pct_specific, pctFac: A[sid].sum.pct_factor
}));
```

## Implementation approach
- New function `openCompare()` renders a full-screen modal
- Reuse `plotBg` and chart patterns for consistency
- The comparison modal should also work as a printable report
- Close with X or Escape

## Key insight from the data
All strategies except GSC and ISC have "Industrials" as their biggest sector bet. That's a firm-wide concentration risk that only the comparison view surfaces.
