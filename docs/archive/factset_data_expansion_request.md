# FactSet Data Expansion Request

## Background

We've successfully integrated the new CSV format (with Section column, explicit dates, per-holding groupings) into our risk dashboard. The parser handles all 14 section types across all 7 strategies. Thank you for the improvements — the explicit section labels and date columns are much cleaner to work with.

We're now building out deeper analytics capabilities and have identified specific data points that would significantly enhance our factor risk attribution and portfolio transparency. These fall into three categories.

---

## Request 1: RiskM Section — Full Factor Breakout

**Current state:** The RiskM section provides % of Variance (TE contribution) for 12 style factors + Market, Industry (aggregate), Country (aggregate), Currency (aggregate) = 17 total.

**Requested:** Break out the Industry, Country, and Currency aggregates into their individual components. Instead of one "Industry = 12.2%" row, provide individual rows:

```
RiskM, IDM, ..., 2/27/2026, Semiconductors, [% of variance], [active exposure]
RiskM, IDM, ..., 2/27/2026, Banks, [% of variance], [active exposure]
RiskM, IDM, ..., 2/27/2026, Capital Goods, [% of variance], [active exposure]
... (all industries with non-zero contribution)
```

Same for Country and Currency individual components.

**Why:** We need to identify which specific industry, country, or currency bet is driving risk. The aggregate "Industry = 12.2%" tells us industry bets matter, but not which industry. The 18 Style Snapshot provides factor impact and return at the individual level, but not the precise % of variance (TE contribution) that the RiskM section provides. Having both allows us to:
- Rank individual industries by their risk contribution
- Identify if a large country overweight is actually contributing to or diversifying risk
- Decompose currency risk into specific currency pair contributions

**Impact on file:** Since RiskM is vertical (one row per item), this adds approximately 120 rows per date per strategy. For 4 weekly dates × 7 strategies = ~3,360 additional rows. Negligible compared to the current file size.

---

## Request 2: Per-Holding Axioma Factor Exposures on the Security Table

**Current state:** The Security table provides per holding: weights (W, BW, AW), risk contributions (%S, %T), and Spotlight ranks (OVER, REV, VAL, QUAL, MOM, STAB). Holdings also have grouping columns (Sector, Region, Country, Industry, Subgroup).

**Requested:** Add per-holding Axioma factor exposures (z-score loadings) for the 12 style factors:

```
Additional columns per weekly group in Security section:
Momentum_Exp, Volatility_Exp, Growth_Exp, Value_Exp,
Dividend_Yield_Exp, Profitability_Exp, Size_Exp, Leverage_Exp,
Liquidity_Exp, Market_Sensitivity_Exp, Earnings_Yield_Exp, FX_Sensitivity_Exp
```

**Why:** Currently we can see that a holding contributes 6.9% to total TE (%T) and 3.6% is stock-specific (%S), meaning 3.3% comes from factor exposure. But we cannot determine WHICH factors that 3.3% flows through. With per-holding factor exposures we can:
- Answer "which holdings drive our Momentum tilt?" precisely
- Identify if a single stock is responsible for an outsized factor bet
- Build factor-aware position sizing (e.g., "adding to TSMC would increase our Volatility exposure by X")
- Support drill-downs from factor view → contributing holdings

**Note:** These are the Axioma risk model factor loadings, NOT the Spotlight/Redwood proprietary ranks (OVER/REV/VAL/QUAL) which are already on the table and serve a different purpose (stock selection vs risk decomposition).

**Impact on file:** +12 columns per weekly group in the Security section. With 5 weekly groups, that's +60 columns per holding row. For ~40 holdings × 7 strategies = 280 rows, this adds approximately 16,800 data points. Memory impact: ~0.4 MB. Negligible.

---

## Request 3: Per-Group Factor Contributions on Sector/Country/Industry Tables

**Current state:** Group tables (Sector Weights, Country, Industry, Group) provide weights (W, BW, AW), risk contributions (%S, %T), and Spotlight MFR ranks.

**Requested:** Add per-group Axioma factor risk contributions — how much does each sector/country/industry contribute to each style factor's total risk:

```
Additional columns per weekly group:
Momentum_Contrib, Volatility_Contrib, Growth_Contrib, Value_Contrib,
Dividend_Yield_Contrib, Profitability_Contrib, Size_Contrib, Leverage_Contrib,
Liquidity_Contrib, Market_Sensitivity_Contrib, Earnings_Yield_Contrib, FX_Sensitivity_Contrib
```

**Why:** This answers questions like:
- "How much of our Growth factor risk comes from the Technology sector?"
- "Is our Volatility exposure concentrated in one country or diversified?"
- "Which sectors contribute most to our intentional Profitability tilt?"

These are cross-dimensional questions that neither the Security table nor the factor tables can answer alone.

**Impact on file:** +12 columns per weekly group on each group table. Moderate increase but manageable.

---

## Priority Order

1. **Request 1 (RiskM breakout)** — highest value, lowest file impact (just more rows)
2. **Request 2 (Per-holding factor exposures)** — enables the deepest analytics
3. **Request 3 (Per-group factor contributions)** — nice to have, can be approximated from Request 2

If all three increase file size concerns, Request 1 alone would be a significant improvement. Request 2 can be delivered as a separate supplementary file if adding columns to the existing Security table is problematic.

---

## Additional Characteristics (Lower Priority)

If convenient to include in the Portfolio Characteristics section, these additional metrics would enhance our fundamental analysis:

- Revenue Growth 3Yr
- Net Debt/EBITDA
- ROIC (Return on Invested Capital)
- EV/EBITDA
- Total Shareholder Yield (Dividend + Buyback)
- Earnings Revision 3M (raw signal behind our Revision MFR)
- Realized Volatility 1Y
- PEG Ratio
- Gross Margin
- Average Daily Volume ($)

These can be added to the existing Portfolio Characteristics vertical structure without changing the file layout.

---

## Confirmation

The current file format works well. All requested additions are backward-compatible — existing columns and sections remain unchanged. We're ready to receive the 3-year historical file at any time.

Please let me know if any of these requests need clarification or if there are technical constraints I should be aware of.
