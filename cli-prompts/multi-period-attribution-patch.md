# Multi-Period Attribution Dashboard

## What it does
A dedicated "Attribution" view (accessible from Factor Attribution section) that shows cumulative return attribution across any selectable time window, with drill-down to individual periods.

## 1. Period-over-Period Attribution Table
Like the current Factor Attribution table but with period columns:

| Factor | Wk1 | Wk2 | Wk3 | Cumulative |
|--------|-----|-----|-----|-----------|
| Market Sensitivity | +0.12 | +0.08 | +0.20 | +0.40 |
| Momentum | +0.05 | +0.04 | +0.05 | +0.14 |

Data source: cs.snap_attrib[factorName].hist[] has per-period imp values.
Each cell colored by sign (green/red). Cumulative column matches the existing cimp values.

## 2. Cumulative Attribution Area Chart
Stacked area showing cumulative return attribution over time for top 5 factors.
X-axis = weeks, Y-axis = cumulative impact %, one colored area per factor.
Shows how each factor's contribution built up or reversed over time.

## 3. Rolling Window Selector
Choose attribution window: 1W | 4W | 13W | 26W | 52W | YTD | All
Changing window re-computes the table and chart for that period.

## 4. Attribution by Category
Toggle between: Style Factors | Countries | Industries | Currencies
Each category uses the matching entries from snap_attrib.
Countries shows: "Japan contributed +0.02% this week, cumulative -0.05% over 3 weeks"

## 5. Winner/Loser Summary
Above the table, show:
- "Best contributor: Market Sensitivity (+0.40% cumulative)"
- "Worst contributor: Metals & Mining (-0.34% cumulative)"  
- "Most volatile: AUD (std dev 8.83)"

## Data source detail:
```javascript
// cs.snap_attrib['Market Sensitivity'].hist = [
//   {d:'20260327', exp:-0.24, ret:-0.22, imp:0.05, dev:0.93, cimp:0.05, risk_contr:0.53},
//   {d:'20260403', exp:-0.23, ret:-0.14, imp:0.03, dev:0.93, cimp:0.09, risk_contr:0.51},
//   {d:'20260408', exp:-0.22, ret:0.05, imp:-0.01, dev:0.93, cimp:0.08, risk_contr:0.47}
// ]
```
Each period has: exposure change, factor return, attribution impact, cumulative impact, risk contribution.
This is the richest dataset in the file — 122 entries × 3 periods × 6 fields = 2,196 data points.
