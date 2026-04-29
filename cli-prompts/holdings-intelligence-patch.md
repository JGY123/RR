# Holdings Intelligence Layer

## What it does
Transforms the Holdings tab from a data table into an intelligence tool that surfaces actionable insights about each position.

## 1. Risk Budget Efficiency Score per Holding
Add a computed column: RBE = |active weight| / |TE contribution|
- Green (>1.5): "Getting more tilt than risk — efficient bet"
- Amber (0.8-1.5): "Proportional risk/reward"
- Red (<0.8): "Risk exceeds tilt — consider if the position justifies its risk"
This already exists on sectors — apply same pattern to individual holdings.

## 2. Factor Profile Classification
Auto-classify each holding into a style archetype based on its factor_contr:
- "Growth Engine" — top factor is Growth or Momentum
- "Value Play" — top factor is Value or Dividend Yield
- "Volatility Driver" — top factor is Volatility or Market Sensitivity  
- "Quality Compounder" — top factor is Profitability
- "Market Beta" — top factor is Market (just riding market exposure)
- "Diversifier" — no single dominant factor, small individual contributions

Show as a colored pill next to the holding name. Filter chips to filter by archetype.

## 3. Peer Comparison Percentile
For each holding, compute where it ranks among its sector peers on key metrics:
- Weight percentile: "Top 20% by weight in Financials"
- TE percentile: "Highest TE contributor in Health Care"
- Rank percentile: "Q1 ranked — better than 80% of sector peers"
Show as a tiny bar (0-100%) in the expanded row.

## 4. Holding Risk Scorecard
In the expanded row (or stock detail popup), add a 5-metric scorecard:
| Metric | Value | Signal |
|--------|-------|--------|
| RBE | 0.45 | 🔴 Inefficient |
| Factor Concentration | 78% Market | ⚠️ Single-factor |
| Sector Peer Rank | Top 15% TE | ⚠️ High risk vs peers |
| Weight vs BM | +2.8% OW | ✅ Intentional |
| Rank Quality | Q2 | ✅ Above average |

## 5. Auto-Generated Holding Notes
For each holding, auto-generate a one-sentence summary:
"NBIS (Nebius) is a Q2-ranked IT stock contributing 16.3% of portfolio TE — the largest single-name risk. Factor profile is dominated by Market (+1.25) and Volatility (-0.33). Risk budget efficiency is low (0.18) — the position generates more TE than its active weight justifies."

Show in the stock detail popup as an "AI Summary" section.

## Implementation: 
Most of this is computed on the fly from existing cs.hold data + cs._sectorAgg.
The archetype classification is a simple max(|factor_contr|) lookup.
The peer comparison uses sector-filtered holdings sorted by the metric.
