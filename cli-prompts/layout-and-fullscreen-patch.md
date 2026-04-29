# Layout Rearrangement + Full-Screen Chart Modals + Table Column Consistency

## KEY FINDINGS FROM AUDIT:

### Table column inconsistency:
| Table | Columns | Has ORVQ | Has RBE | Has TE/Stock/Factor | Overflow |
|-------|---------|----------|---------|---------------------|----------|
| Sector | 12 | Yes (Port/BM toggle) | Yes | Yes (gradient bars) | YES |
| Country | 8 | No (has column chooser) | Yes | Yes | No |
| Groups | 12 | Yes | Yes | Yes | YES |
| Region | 12 | Yes | Yes | Yes | YES |
| Factor | 7 | N/A | Has FBE | Has TE% | No |
| Quant Ranks | 7 | N/A | N/A | Yes | No |
| Chars | 5 | N/A | N/A | N/A | No |
| Attribution | 4 | N/A | N/A | Has Impact | YES |

### Layout issues:
- Factor Risk Map (385px) paired with Factor Detail (1000px) in g2 grid — massive height mismatch, Factor Risk Map has 600px empty below it
- Quant Ranks (390px) paired with Characteristics (720px) — 330px wasted space
- MCR (375px) paired with Risk Budget (301px) — ok, close match
- Scatter (416px) paired with Treemap (449px) — ok, close match

## PATCH 1: Table column consistency

### Country table: add ORVQ + Port/BM toggle (matching sector/groups)
The country table currently uses a column chooser (Risk/Ranks/Style/NonStyle). Add ORVQ as default visible columns alongside Risk columns, with the Port/BM toggle in the header:
- Add `_ctryRankSrc` state var (default 'port')
- Compute benchmark-weighted ORVQ averages per country (same pattern as sector)
- Add Port/BM toggle buttons to the country table header
- This makes country table 12 columns (matching sector/groups/region)
- The column chooser switches the EXTRA columns (Style Factors / Non-Style) but ORVQ stays visible by default

### All tables: standardize overflow handling
For tables with >8 columns that overflow their card:
- Add `overflow-x:auto` wrapper with a subtle scroll shadow indicator on the right edge
- Add CSS: `.table-scroll{overflow-x:auto;position:relative}` + `.table-scroll::after{content:'';position:absolute;right:0;top:0;bottom:0;width:20px;background:linear-gradient(to right,transparent,var(--card))}`

## PATCH 2: Fix grid height mismatches

### Factor Risk Map + Factor Detail
Currently in g2 grid causing 600px waste. Fix options:
- A) Make Factor Risk Map taller (increase from 340px to match Factor Detail ~600px with more visual content)
- B) Move Factor Detail out of the grid — make it full-width below the Factor Risk Map
RECOMMEND A: Make Factor Risk Map taller (500px) and add a mini legend/guide panel below the chart showing top 3 factors by TE contribution with their values. This fills the empty space with useful content.

### Quant Ranks + Characteristics
Quant Ranks is 390px with 330px wasted. Fix:
- Add more content to Quant Ranks: a mini stacked bar below the table showing quintile weight distribution as proportional colored segments
- Or swap position: put Characteristics first (taller, more important) on the left

## PATCH 3: Full-screen chart modals

Create a reusable `openFullScreen(chartType, data)` function that:
1. Opens a 90%-viewport dark overlay modal
2. Renders the chart at full size on the left (70% width)
3. Shows a data summary panel on the right (30% width)
4. Has a close button (X) and click-outside-to-close

### Factor Risk Map full-screen:
- Left: Bubble scatter at 800x500px (much bigger, no label overlap)
- Right: Factor list with exposure, TE%, std dev, sorted by TE contribution
- Interactive: hover a factor in the list → highlight it on the chart
- Title: "Factor Risk Map — [Strategy]"

### Risk/Return Scatter full-screen:
- Left: Scatter at 800x500px (labels readable, no overlap)
- Right: Holdings list with port%, active%, TE%, sector, country
- Interactive: click a point → highlight it and show factor_contr breakdown
- Search bar to find a specific holding
- Title: "Risk/Return Analysis — [Strategy]"

### Country Globe full-screen:
- Left: Map at 800x500px (bigger projection, more detail visible)
- Right: Top 10 countries table by selected metric
- Region zoom buttons at bottom
- Color mode selector in the panel
- Title: "Country Exposure — [Strategy]"

### How to trigger:
- Add a small "⛶" expand icon in the top-right corner of each chart card (next to any existing buttons)
- Clicking the expand icon opens the full-screen modal
- The existing click-on-data interactions (bubble → drill, country → drill) still work within the full-screen view

### CSS for full-screen modal:
```css
.fs-modal{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,0.85);display:none;padding:24px}
.fs-modal.show{display:flex;gap:20px}
.fs-modal .fs-chart{flex:2;background:var(--card);border-radius:12px;padding:16px;display:flex;flex-direction:column}
.fs-modal .fs-panel{flex:1;background:var(--card);border-radius:12px;padding:16px;overflow-y:auto;max-width:400px}
.fs-modal .fs-close{position:absolute;top:16px;right:20px;font-size:24px;color:var(--txt);cursor:pointer;z-index:201}
.fs-modal .fs-title{font-size:16px;font-weight:700;color:var(--txth);margin-bottom:12px}
```

## PATCH 4: Chart explanations

Every chart card should have a brief explanation visible (not just tooltip):

### Factor Risk Map:
Below the chart, add a single line: "Each bubble = one factor. Position = exposure × volatility. Size = tracking error contribution. Click to explore."

### Risk/Return Scatter:
Below the chart: "Each dot = one holding. Ideal: top-left (high return, low risk). Click any dot for detail."

### Active Weight Treemap:
Below the chart: "Rectangle size = portfolio weight. Green = overweight vs benchmark. Red = underweight. Click to drill."

### Country Globe:
Below the map: "Color intensity = selected metric. Click any country for full analysis."

Use consistent styling: `font-size:9px; color:var(--txt); opacity:0.6; text-align:center; padding:4px 0`
