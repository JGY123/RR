# RR Dashboard Specification
> Source: User interview 2026-03-23. Authoritative — overrides any parser assumptions.

## File Structure
- **Format:** Very large CSV, weekly data (every Friday)
- **Date labels:** Next version will have a DATE column in each table (currently missing)
- **Frequency:** Weekly delivery
- **Multi-date file:** One file contains MANY weeks of data — same tables repeated with different data points
- **History display:** Clicking any data point shows a time-series chart of that metric over all available weeks

## Strategies
- **Current 7:** IDM, IOP (ACWIXUS in file), EM, ISC, SCG, ACWI, GSC
- **More coming:** Unknown which, mostly same column structure
- **US-specific strategies** (like SCG): Skip country/region analysis, keep sector/industry
- **Multiple PMs** per strategy
- **All equal importance**, SCG slightly less
- **Default on open:** EM

## Grouping Dimensions (per strategy, in priority order)
1. **Sector** (GICS Level 1, 11 sectors) — PRIMARY
2. **Custom Group** (proprietary: Hard Cyclical, Growth Cyclical, Soft Cyclical, Defensive, Growth, Commodity, Banks, Bond Proxies) — VERY IMPORTANT
3. **Industry** — important
4. **Securities** (holdings grouped by a flag — portfolio + BM-only meeting criteria. NOT a real group, used as a FILTER for the holdings table)
5. **Overall Rank** (quintile grouping)
6. **REV, VAL, QUAL** (sub-factor quintile groupings)
7. **Region** — LESS IMPORTANT, push to bottom of page
8. **Characteristics tiles** — behave differently, separate handling
9. **Attribution tiles** — factor attribution, behave differently

## Column Layout (18 per weekly group)
| Pos | Label | Confirmed |
|-----|-------|-----------|
| 0 | W (Portfolio Weight %) | ✅ |
| 1 | BW (Benchmark Weight %) | ✅ |
| 2 | AW (Active Weight %) | ✅ |
| 3 | %S (Stock-specific TE component) | ✅ |
| 4 | %T (% of total tracking error) | ✅ |
| 5 | %T_Check (BM inclusion FLAG only — can mostly ignore) | ✅ |
| 6 | OVER_WAvg (Overall quintile rank, weighted avg) | ✅ ALWAYS rank, NEVER market cap |
| 7 | REV_WAvg | ✅ |
| 8 | VAL_WAvg | ✅ |
| 9 | QUAL_WAvg | ✅ |
| 10 | MOM_WAvg | ✅ |
| 11 | STAB_WAvg | ✅ |
| 12-17 | Same 6 as simple averages (_Avg) | ✅ |

### ⚠️ CRITICAL: Data Row Interpretation
- **%T_Check (pos 5) at Data row:** Just a flag — NOT Active Share. Ignore it.
- **OVER_WAvg (pos 6) at Data row:** Still the overall rank — NOT Market Cap.
- **Market Cap comes from the 42-col portfolio stats section (col[12])** — not from the 96-col Data row.
- **Active Share comes from the 42-col section (col[11])** — not from %T_Check.

### 101-col Sections (Holdings)
- Next version will NOT have the extra 5 columns — will become standard 96-col
- No more "Overall Rank" column at position 5 in each group

## Holdings Display Rules
- Show ALL portfolio holdings (W > 0)
- BM-only holdings: include ONLY if they meet ANY of:
  - %T_Check flag is set (the inclusion flag)
  - Benchmark weight > 50 bps (0.50%)
  - TE contribution (%T) > 1%
- Default sort: by %T (tracking error contribution), descending
- Show ALL qualifying holdings (no pagination cutoff)

## Portfolio Stats (42-col section)
| Col | Metric | Status |
|-----|--------|--------|
| 8 | Predicted Tracking Error | ✅ Confirmed |
| 9 | Predicted Beta | ✅ Confirmed |
| 10 | # of Securities | ✅ Confirmed |
| 11 | Active Share | ✅ Confirmed |
| 12 | Market Cap ($M) | ✅ Confirmed |
| 16 | EPS Growth 3Yr | ✅ Confirmed |
| 20 | FCF Yield NTM | ✅ Confirmed |
| 21 | Dividend Yield | ✅ Confirmed |
| 22 | ROE NTM | ✅ Confirmed |
| 23 | Operating Margin | ✅ Confirmed |
| ?? | P/E Ratio | Will be fixed in next sample |
| ?? | P/B Ratio | Will be fixed in next sample |

**Request:** Extract ALL fundamentals available. User wants a list of additional metrics to request from FactSet.

## Factor Model
- **Model:** Axioma
- **16 factors:** Growth, Medium-Term Momentum, Volatility, Market Sensitivity, Liquidity, Exchange Rate Sensitivity, Profitability, Currency, Size, Market, Industry, Country, Leverage, Earnings Yield, Value, Dividend Yield
- **Values:** Raw factor loadings (z-scores)
- **Display:** Individual factor AND grouped by factor type
- **Factor attribution:** On the SAME tab as factor exposures (no separate attribution tab)
- **CompoundedFactorReturn:** Will be enabled in next sample
- **Goal:** Decompose returns by individual factor bets AND by factor groups

## Dashboard Layout

### Tab Order (user preference)
1. **Exposures** (default tab on open)
2. **Sectors** (with Custom Groups prominently featured)
3. **Holdings**
4. **Factors + Attribution** (combined, NOT separate tabs)
5. **Risk**
6. **Countries** (lower priority)
7. **Regions** (lowest priority — push to bottom)

### Overview/Summary Cards (priority ranking)
| Metric | Priority | Notes |
|--------|----------|-------|
| Tracking Error | 1 | Must see immediately |
| Active Share | 1 | Must see immediately |
| Beta | 1 | Must see immediately |
| Holdings Count | 1 | Must see immediately |
| Factor Scores (OVER, REV, VAL) | 2 | Important |
| Cash % | 2 | Important |
| P/E Ratio | 5 | Nice to have |

### History / Time Series
- Every data point should be clickable → shows time-series chart
- Chart shows how that metric fluctuated over all available weekly snapshots
- This applies to: TE, Active Share, Beta, factor exposures, sector weights, etc.

### US-Specific Strategy Handling
- For US strategies (SCG and any future US accounts):
  - SKIP: Country analysis, Region analysis
  - KEEP: Sector, Industry, Custom Group, Holdings, Factors
- Detection: if strategy benchmark contains "Russell" or is US-only

### Email Snapshot
- Build template first, revise from there
- Should include the most important metrics from the summary view

## Additional Fundamental Metrics to Request from FactSet
Suggested additions to make the dashboard more useful:
1. **Debt/Equity Ratio** — leverage assessment
2. **Revenue Growth (1Y, 3Y)** — growth trajectory
3. **Free Cash Flow per Share** — cash generation
4. **Earnings Yield** — valuation (inverse P/E)
5. **Price/Sales** — valuation for growth companies
6. **Return on Assets (ROA)** — efficiency
7. **Current Ratio** — liquidity
8. **Gross Margin** — profitability
9. **R&D as % of Revenue** — innovation intensity
10. **Dividend Payout Ratio** — sustainability of dividends
11. **Net Debt/EBITDA** — leverage quality
12. **Forward P/E (NTM)** — forward valuation
