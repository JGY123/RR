# Risk Decomposition Tree — Premium Feature

## What it does
A new "Risk Tree" view (4th tab after Exposures/Risk/Holdings) showing the complete TE decomposition as an interactive tree/sankey diagram.

## The tree structure:
```
Total TE (5.69%)
├── Factor Risk (35%, 2.0% TE)
│   ├── Style Factors (from cs.factors)
│   │   ├── Volatility: 8.2% of TE
│   │   ├── Market Sensitivity: 6.7%
│   │   ├── Momentum: 5.1%
│   │   ├── Value: 3.2%
│   │   └── ... (12 total)
│   └── Non-Style Factors
│       ├── Industry: 0% (aggregate from snap_attrib)
│       │   ├── Banks: -0.34%
│       │   ├── Metals & Mining: +0.18%
│       │   └── ... (65 industries)
│       ├── Country: 0%
│       │   ├── Japan: +0.86%
│       │   ├── Germany: +0.42%
│       │   └── ... (27 countries)
│       └── Currency: 0%
│           ├── JPY: -0.29%
│           ├── EUR: +0.15%
│           └── ... (18 currencies)
└── Stock-Specific Risk (65%, 3.7% TE)
    ├── By Sector
    │   ├── Information Technology: 26.9% of TE
    │   │   ├── NBIS (Nebius): 16.3%
    │   │   ├── 6857 (Advantest): 4.9%
    │   │   └── ...
    │   ├── Industrials: 12.8%
    │   └── ...
    └── By Holding (top 10)
        ├── NBIS: 16.3%
        ├── 6857: 4.9%
        └── ...
```

## Visualization options:

### Option A: Sankey diagram (Plotly)
Left: Total TE → Middle: Factor/Specific split → Right: individual factors/sectors/holdings
Flow widths proportional to TE contribution
Color: factor risk = purple, specific = amber

### Option B: Collapsible tree (HTML/CSS)
Indented tree with expand/collapse toggles
Each node shows: name, TE contribution, % of total, color bar
Click any node → opens the relevant drill-down popup

### Option C: Sunburst chart (Plotly)
Concentric rings: center = total TE, ring 1 = factor/specific, ring 2 = factor groups/sectors, ring 3 = individual items
Click to zoom into a ring

## Recommend: Option B (collapsible tree) as primary, Option C (sunburst) as visual alternative toggle.

## Data sources:
- Total TE: cs.sum.te
- Factor/Specific split: cs.sum.pct_factor, cs.sum.pct_specific
- Style factors: cs.factors (12 style) with c values
- Non-style breakdown: cs.snap_attrib (27 countries, 18 currencies, 65 industries)
- Stock-specific by sector: cs._sectorAgg[].mcr
- Stock-specific by holding: cs.hold[].mcr

## Why this matters:
This is the ONE view that answers "WHERE is my tracking error coming from?" in a single glance. Currently a PM has to mentally piece together factor table + sector table + holdings table to build this picture. The tree does it automatically.
