OVERFLOW AND TRUNCATION FIX PASS on ~/RR/dashboard_v7.html.

The DOM audit found text overflow on nearly every tile. Most are Plotly annotation text that gets clipped by the card container. Fix systematically:

HERO CARD (y=79, h=228):
1. "5.69 Tracking Error" overflows — the hero grid columns may be too tight. Check the grid-template-columns and add overflow:visible or reduce font sizes at narrow widths

SECTOR TABLE (y=362, h=728):
2. "Bench%" header text overflows — column too narrow. Either abbreviate to "BM%" or widen
3. RBE Outliers callout overflows — long sector names like "Communication Services" push past card edge. Add text-overflow:ellipsis or wrap

FACTOR RISK MAP (y=1094):
4. "Dividend Yield" label overflows from the Plotly chart area — the left margin is too tight for long factor names. Increase plotly margin.l from current value to 140
5. X-axis label "Underweight Active Exposure Overweight" is clipped — shorten to "Underweight ← Exposure → Overweight"

FACTOR DETAIL TABLE (y=1507):
6. "Factor Efficiency" callout text overflows — add word-wrap or reduce font
7. Column headers (Factor, Exposure, TE%, etc.) overflow — table width exceeds card. Ensure table has max-width:100% and overflow-x:auto on wrapper

PORTFOLIO CHARACTERISTICS (y=4576):
8. Long metric names overflow: "Axioma- Historical Beta", "EPS Growth - Hist. 3Yr", "EPS Growth - Est. 3-5Yr" — add text-overflow:ellipsis on the metric name cell with max-width:200px, or abbreviate in code (remove "Axioma- " prefix, shorten "Hist." to "H.")

SCATTER (y=5300):
9. Plotly text labels for holdings overflow card — this is Plotly internal, add cliponaxis:true to the trace config

MCR TOP 10 (y=6197):
10. "16.30 ⚠" value + warning icon overflow — the text-outside positioning pushes past chart area. Add margin-right to the Plotly layout

FACTOR RISK BUDGET (y=6600):
11. Donut slice labels "31.2%", "27.0%" overflow — use Plotly textposition:'inside' for large slices

REGION TABLE (y=8096):
12. "RBE Outliers" callout text overflow — same as sector, long region names

FACTOR ATTRIBUTION TABLE (y=7049):
13. "Factor / Country / Industry" header overflows — abbreviate or add overflow-x:auto

When done: report fixes, propose next prompt.
