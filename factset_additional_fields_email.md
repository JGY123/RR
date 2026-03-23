# Email to FactSet — Additional Fundamental Fields Request

**Subject: Additional Fundamental Metrics for Risk Reports Export**

Hi,

Following up on our call — thank you for the updates coming in the next sample file. Before the large production pull, I'd like to request adding the following fundamental characteristics to the portfolio stats section of the export. These would significantly enhance our risk dashboard's analytical depth.

For each metric below, I need both **portfolio weighted-average** and **benchmark weighted-average** values (same format as the current Market Cap, ROE, FCF Yield, etc.).

---

## VALUATION (highest priority — currently only have trailing P/E, P/B)

| # | Metric | Notes |
|---|--------|-------|
| 1 | **Forward P/E (NTM)** | Forward-looking valuation — the most important valuation metric we're missing |
| 2 | **Price/Sales (P/S)** | Essential for growth companies where earnings are negative |
| 3 | **EV/EBITDA** | Enterprise value metric — better cross-capital-structure comparison than P/E |
| 4 | **EV/Sales** | Enterprise value version of P/S |
| 5 | **Price/Cash Flow** | Cash-based valuation |
| 6 | **Earnings Yield (%)** | Inverse P/E — easier to compare across strategies |
| 7 | **Free Cash Flow Yield (TTM)** | We have NTM, would also like trailing for comparison |

## PROFITABILITY & MARGINS

| # | Metric | Notes |
|---|--------|-------|
| 8 | **Gross Margin (%)** | Profitability before SG&A — shows business model quality |
| 9 | **EBITDA Margin (%)** | Operating profitability excluding D&A |
| 10 | **Net Margin (%)** | Bottom-line profitability |
| 11 | **Return on Assets (ROA %)** | Capital efficiency — complements ROE |
| 12 | **Return on Invested Capital (ROIC %)** | Best measure of capital allocation quality |
| 13 | **Return on Equity (TTM)** | We have NTM, would also like trailing |

## GROWTH

| # | Metric | Notes |
|---|--------|-------|
| 14 | **Revenue Growth 1Y (%)** | Short-term top-line momentum |
| 15 | **Revenue Growth 3Y CAGR (%)** | Longer-term growth trajectory |
| 16 | **EPS Growth 1Y (%)** | Short-term earnings growth (we have 3Y) |
| 17 | **EPS Growth NTM (%)** | Forward expected earnings growth |
| 18 | **EBITDA Growth 1Y (%)** | Operating growth |
| 19 | **Free Cash Flow Growth 1Y (%)** | Cash generation momentum |
| 20 | **Book Value Growth 3Y (%)** | Long-term equity accumulation |

## LEVERAGE & BALANCE SHEET

| # | Metric | Notes |
|---|--------|-------|
| 21 | **Debt/Equity Ratio** | Basic leverage |
| 22 | **Net Debt/EBITDA** | Quality of leverage — how quickly can they pay it off |
| 23 | **Interest Coverage Ratio** | Can they service their debt |
| 24 | **Current Ratio** | Short-term liquidity |
| 25 | **Quick Ratio** | Stricter liquidity (excludes inventory) |
| 26 | **Total Debt/Total Assets** | Leverage relative to asset base |

## RETURNS & PERFORMANCE

| # | Metric | Notes |
|---|--------|-------|
| 27 | **Total Return 1M (%)** | Recent performance |
| 28 | **Total Return 3M (%)** | Quarterly performance |
| 29 | **Total Return 6M (%)** | Half-year performance |
| 30 | **Total Return 1Y (%)** | Annual performance |
| 31 | **Total Return YTD (%)** | Year-to-date |
| 32 | **Price Return 1Y (%)** | Excluding dividends |
| 33 | **Excess Return vs BM 1Y (%)** | Alpha over trailing year |
| 34 | **Volatility (1Y annualized)** | Realized vol |
| 35 | **Sharpe Ratio (1Y)** | Risk-adjusted return |
| 36 | **Max Drawdown (1Y)** | Worst peak-to-trough |

## DIVIDENDS & INCOME

| # | Metric | Notes |
|---|--------|-------|
| 37 | **Dividend Payout Ratio (%)** | Sustainability of dividends |
| 38 | **Dividend Growth 3Y (%)** | Dividend trajectory |
| 39 | **Buyback Yield (%)** | Share repurchase activity |
| 40 | **Total Shareholder Yield (%)** | Dividends + buybacks combined |

## SIZE & QUALITY

| # | Metric | Notes |
|---|--------|-------|
| 41 | **Median Market Cap ($M)** | Complements weighted-average |
| 42 | **Weighted Avg Market Cap ($M)** | Already have this, confirming |
| 43 | **Number of Holdings (Active > 0)** | Just portfolio, excluding BM-only |
| 44 | **Active Share (%)** | Already have this, confirming |
| 45 | **Turnover (annualized %)** | Trading activity |
| 46 | **R&D as % of Revenue** | Innovation intensity |

---

## Priority Tiers

**Must have (top 10 — these transform the dashboard):**
1. Forward P/E (NTM)
2. EV/EBITDA
3. Price/Sales
4. Revenue Growth 1Y
5. ROIC
6. Net Debt/EBITDA
7. Total Return 1Y
8. Excess Return vs BM 1Y
9. Gross Margin
10. EPS Growth NTM

**Very useful (next 10):**
11. EV/Sales
12. EBITDA Margin
13. Net Margin
14. Revenue Growth 3Y CAGR
15. Interest Coverage
16. Total Return YTD
17. Volatility 1Y
18. Sharpe Ratio 1Y
19. Total Shareholder Yield
20. Earnings Yield

**Nice to have (remaining):**
Everything else — if it's easy to include, great. If not, the top 20 above cover 90% of what I need.

---

**Confirming from our call:**
- Benchmark P/E and P/B will be included ✅
- Date columns added to each table ✅
- CompoundedFactorReturn enabled ✅
- Overall Rank extra columns removed from holdings ✅

If you can include even the top 10 in the next sample, that would be fantastic. I can handle any column layout — my parser adapts dynamically.

Thanks,
Yuda
