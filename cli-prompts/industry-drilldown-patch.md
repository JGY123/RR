# Industry Deep Drill Enhancement

## What it does
The Factor Attribution table shows 65 industries but clicking one gives limited info. Enhance the industry drill-down to match the depth of sector/country drills.

## Current state:
oDrAttrib() opens a modal with: cumulative impact, current exposure, factor std dev, and a time series chart. Basic.

## Enhanced industry drill should show:

### 1. Stat cards (g4 grid):
- Active Exposure (from snap_attrib[industry].exp)
- Return Impact (from snap_attrib[industry].imp) 
- Risk Contribution (from snap_attrib[industry].risk_contr)
- Std Dev (from snap_attrib[industry].dev)

### 2. Holdings in this industry
Filter cs.hold where h.ind matches the industry name (or closest match).
Show top 10 holdings by TE contribution as a bar chart.
Table below with: Ticker, Name, Country, Port%, Active%, TE%, Rank.

### 3. Time series
Already exists from snap_attrib[industry].hist — exposure + impact over time.
Enhance: add a dual-axis chart with exposure (left) and cumulative impact (right).

### 4. Related industries
Show 3-5 industries with the most correlated exposure patterns.
Computed from snap_attrib[industry].hist correlation with other industries.

### 5. Sector context
"This industry (Banks) is part of Financials sector. Sector active weight: -4.9%"
Link to the sector drill.

## Also enhance the Factor Attribution table:
- Add an "Industry" filter dropdown (show only industries in a specific sector)
- Add a "Country" filter (show only entries for a specific country)
- Add Risk Contribution column (from snap_attrib[].risk_contr) — currently missing
- Add a sparkline showing 3-week exposure trend per row
