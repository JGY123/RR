# Onboarding + Contextual Help System

## What it does
First-time users see a brief guided tour. Returning users get contextual help on demand. Every metric has a plain-English explanation.

## 1. First-run guided tour
On first load (check localStorage flag `rr_toured`):
- Step 1: Highlight hero card → "This shows your overall risk profile. TE = how much you differ from benchmark."
- Step 2: Highlight sector table → "Your sector bets. Green = overweight, red = underweight. Click any row for detail."
- Step 3: Highlight factor map → "Each bubble is a risk factor. Bigger = more tracking error. Click to explore."
- Step 4: Highlight holdings tab → "Every position in your portfolio. Expand for factor breakdown."
- "Got it" button dismisses, sets localStorage flag

Implementation: spotlight overlay (dark everything except the highlighted card) + tooltip next to it

## 2. Metric glossary
Every metric abbreviation gets a ? icon or hover tooltip:
- TE = Tracking Error: how different your returns are from the benchmark (annualized std dev of excess returns)
- AS = Active Share: % of portfolio that differs from benchmark by weight
- Beta = sensitivity to benchmark moves (1.0 = moves in lockstep)
- MCR = Marginal Contribution to Risk: how much each holding adds to total TE
- RBE = Risk Budget Efficiency: |active weight| / TE contribution (higher = getting more tilt per unit of risk)
- %S = Stock-specific TE component (idiosyncratic, not driven by factors)
- %T = Total TE contribution (stock-specific + factor-driven)
- Factor Exposure = portfolio's tilt relative to benchmark on that factor dimension
- ORVQ = Overall / Revision / Value / Quality quant scores (1=best, 5=worst)

## 3. Contextual "Why does this matter?" tooltips
On each tile's title, add a subtle (?) that expands to explain:
- Sector table: "Shows where you're taking active bets vs the benchmark. Large active weights drive tracking error."
- Factor map: "Plots your factor exposures by volatility. Top-right bubbles are your biggest risk drivers."
- Country map: "Geographic distribution of risk. Color intensity shows the selected metric per country."
- Holdings: "Every position with its risk contribution. The FC column shows net factor risk per holding."

## 4. Glossary modal
"?" keyboard shortcut (already in keyboard-shortcuts-patch) also opens a glossary modal listing all metrics with definitions, organized by category (Risk, Weight, Factor, Rank).
