Subject: Redwood Risk — Data Questions + Expansion Request for Portfolio Attribution Export

---

Hi [FactSet contact],

I spent the past several days going through the data, validating every field across all 14 section types, 7 strategies, and 158 weekly periods. This validation was quite challenging, and several data questions and expansion requests emerged.

I've organized them by priority below.

---

## 1. ⭐ SECURITY SECTION — MOST IMPORTANT TOPIC

This is the highest-priority item. The Security section is the foundation of the per-holding analytics — every drill-down, factor attribution, and risk decomposition depends on it being complete and enriched.

### 1A. Incomplete Holdings List (Critical)

The Security section contains significantly fewer holdings than the actual portfolio holdings, and I'm wondering how come it's such a partial list?

| Strategy | Actual # Securities | Security rows with W | W Sum | % Missing |
|----------|-------------------|---------------------|-------|-----------|
| IDM | 43 | 19 | 47.7% | 56% |
| ACWI | 39 | 13 | 33.3% | 67% |
| IOP | — | 13 | 34.1% | ~65% |
| EM | 41 | 17 | 52.5% | 48% |
| GSC | 50 | 9 | 18.7% | 81% |
| ISC | 49 | 10 | 21.0% | 79% |
| SCG | 42 | 17 | 40.1% | 60% |

GSC for example has in one period only 9 out of 50 holdings — missing 81% of the portfolio at the holding level. I verified this is not a parsing issue — the CSV genuinely has this many rows with weight data in the latest weekly group.

**I need ALL current portfolio holdings in the Security section.** This is the single most important fix for the expanded run. Without the full holdings list, I cannot:
- Build a complete holdings table
- Reconcile per-holding %T with group table %T (e.g., IDM Industrials shows 8.3% from holdings but 25.6% in the Sector table)
- Do per-holding factor analysis on the full portfolio

### 1B. Benchmark Securities

Zero benchmark-only rows exist in the current file — every Security row is or was a portfolio holding. BW is only populated for the few portfolio holdings that overlap with the benchmark (sums to 0.2–21.7% instead of ~100%).

**Request:** Include benchmark securities as well, with the %T_Check flag set to 1 (which I understand is the inclusion flag for contributing to risk), or just include all of the benchmark if the data limit isn't an issue. This would:
- Ensure group tables (Sector, Country, Industry) have rows for all benchmark sectors/countries
- Enable benchmark-side Spotlight rank averages
- Show which benchmark holdings I'm implicitly underweight

### 1C. Requested Additional Columns on Security

For the expanded run, I'd like to enrich the Security section with columns that enable per-holding factor analysis. Currently each weekly group has 24 columns. In priority order:

**A. Factor Contribution to Risk (Highest Priority):**

Per-holding marginal contribution to each factor's TE — "how much of this holding's %T flows through each factor?" These should sum to the holding's %T.

If data isn't an issue, then ideally include ALL factors — meaning list every country, currency, and industry and their contribution to tracking error inside the Security section. The full expanded list would be the 12 style factors + Market + every individual industry + every individual country + every individual currency.

If that's too many columns, at minimum the 16 grouped factors:
```
Momentum_TE%, Volatility_TE%, Growth_TE%, Value_TE%,
DivYield_TE%, EarningsYield_TE%, FXSens_TE%,
Profitability_TE%, Size_TE%, Leverage_TE%,
Liquidity_TE%, MarketSens_TE%,
Market_TE%, Industry_TE%, Country_TE%, Currency_TE%
```

**B. Raw Factor Exposures (High Priority but lower than A):**

Per-holding Axioma z-score factor loadings. Same logic — if data allows, include the full expanded list (12 style factors + individual industries + individual countries + individual currencies). The exposure for country/industry/currency is essentially a flag (1 or 0) showing which specific country/industry/currency that security belongs to, which is useful for verification and grouping.

If using the narrow version (12 style factors only):
```
Momentum_Exp, Volatility_Exp, Growth_Exp, Value_Exp,
DivYield_Exp, EarningsYield_Exp, FXSens_Exp,
Profitability_Exp, Size_Exp, Leverage_Exp,
Liquidity_Exp, MarketSens_Exp
```

The idea is to add all of these columns on the Security table so I can skip adding them on all of the other tables and compute group-level factor tilts myself. If data isn't an issue, adding them everywhere too would be even better — I can figure out which way is more data-efficient.

**C. Market Cap — 1 column:**

Per-holding market capitalization in dollars. Enables size bucketing, cap-weighted analysis, and size distribution charts.

---

## 2. RANK TABLES — Two Separate Issues

**Issue 1: Overall Table — Expand/Collapse.** The Overall rank table has individual security tickers appearing as separate rows alongside the quintile groups. For example, IDM has ticker "2875" as its own row, ACWI has AMZN, ALAB, BWXT, EXEL, NU, and 688910. GSC is worst — only 3 quintile rows with 4 ticker rows, meaning two quintiles are missing entirely. Could the Overall section be set to fully collapsed (aggregated only)? The Overall grouping logic itself works correctly — Q1 has OVER_WAvg = 1.00, Q5 = 5.00, exactly as expected.

**Issue 2: Overall Table — Grouping Logic.** Beyond the expand/collapse, the Overall table has a grouping problem that the sub-rank tables don't. In the REV, VAL, and QUAL tables, the self-rank weighted average within each quintile is exactly what it should be — REV Q1 has REV_WAvg = 1.00, Q2 = 2.00, Q3 = 3.00, and so on, all exact integers across every strategy and every period. This is correct: every holding in REV Q1 has REV rank 1, so the average is 1.00. The Overall table doesn't behave this way. Overall Q1 shows OVER_WAvg = 1.78 (should be 1.00), Q3 shows 2.43 (should be 3.00), Q5 shows 2.91 (should be 5.00). Non-integer averages mean holdings with different Overall ranks are mixed into the same quintile group. Since REV/VAL/QUAL all group correctly, the issue seems specific to how the Overall rank quintiles are constructed. Can we align the Overall grouping logic with the sub-rank tables?

Also, across all sections, please make sure benchmark-only groups are not hidden — I'm finding missing data everywhere from sectors to industries to ranks.

---

## 3. GROUP TABLES — Missing Rows, Naming, and Style Groups

### 3A. Zero-Weight Groups Excluded

Across Sector Weights, Industry, Country, and Region: **groups where the portfolio has zero weight are excluded entirely**, hiding the benchmark allocation. Benchmark weights don't sum to 100%:

| Strategy | Sector BM Sum | Industry BM Sum | Country BM Sum |
|----------|--------------|-----------------|----------------|
| IDM | 94.7% | 79.6% | 86.2% |
| ACWI | 86.7% | 70.9% | 81.4% |
| IOP | 95.3% | 75.0% | 64.5% |
| EM | 89.2% | 72.4% | 87.0% |
| GSC | 95.4% | 80.1% | 91.6% |
| ISC | 71.2% | 59.5% | 73.7% |
| SCG | 94.1% | 80.2% | 99.0% |

**Request:** Include ALL groups in every table regardless of portfolio weight. A row with W=0, BM=3.7, AW=-3.7 shows the active underweight — a missing row hides it.

For reference, the full GICS L1 sector universe (all 11 should appear for every strategy):

| Sector | IDM | ACWI | IOP | EM | GSC | ISC | SCG |
|--------|-----|------|-----|-----|-----|-----|-----|
| Communication Services | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Consumer Discretionary | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Consumer Staples | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Energy | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Financials | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Health Care | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Industrials | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Information Technology | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Materials | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| Real Estate | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Utilities | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

The same issue applies to the **Group (RWOOD style groups)** section — 8 possible groups (GROWTH, DEFENSIVE, GROWTH CYCLICAL, HARD CYCLICAL, SOFT CYCLICAL, BANKS, COMMODITY, BOND PROXIES) but zero-weight groups are excluded. All group tables need the same treatment: include all groups always.

### 3B. Industry Naming Inconsistency

The 3-year history has GICS reclassification splits — the same industry appears under two names as separate rows. This is an issue that predates this project, but if we can address and fix it, it would be helpful. Combine these into a single row per industry using the current GICS classification retroactively applied to the full history. Split rows break time-series tracking.

| Old Name (pre-reclassification) | Current Name |
|---|---|
| Retailing | Consumer Discretionary Distribution & Retail |
| Media | Media & Entertainment |
| Commercial Services & Supplies | Commercial & Professional Services |
| Pharmaceuticals, Biotechnology & Life Sciences | Pharmaceuticals Biotechnology & Life Sciences |

---

## 4. 18 STYLE SNAPSHOT — Add % of Variance Column

**Request:** Add a **% of Variance** column to the 18 Style Snapshot for every item. This would put return attribution and risk contribution in one place:

```
Current (5 cols):  Exposure | Factor Return | Factor Impact | Factor StdDev | Cumulative Impact
Requested (6 cols): Exposure | Factor Return | Factor Impact | Factor StdDev | Cumulative Impact | % of Variance
```

Currently % of Variance is only available in RiskM at the aggregate level (Industry = 11.13%, Country = 3.05%). With this addition, I'd see the individual breakdown — which specific industry, country, or currency is contributing to tracking error — alongside the existing return attribution.

This is a more efficient solution than breaking out RiskM into individual rows. One extra column on existing rows vs. ~132K new rows.

---

## 5. PORTFOLIO CHARACTERISTICS — Additional Metrics

The current PortChars section is excellent — TE, Beta variants (predicted, historical, MPT), Active Share, MCap, P/E, P/B, ROE, FCF Yield, Div Yield, EPS Growth (historic + estimated), EPS Revisions (3M + 6M), Operating Margin. All with portfolio and benchmark. I'm parsing all of them successfully.

For the expanded run, if straightforward to add in the same `:P` / `:B` format — the idea is to get all the easy ones added since we're doing the big pull so I have them in the data:

**Valuation:** EV/EBITDA, PEG Ratio, FCF/EV, Price/Sales, Price/Cash Flow
**Quality / Balance Sheet:** Net Debt/EBITDA, ROIC, Gross Margin, Interest Coverage, Current Ratio, Debt/Equity
**Growth / Momentum:** Revenue Growth 3Yr, Revenue Growth Est (forward), 12M EPS Revisions FY1, Sales Growth Est, Earnings Surprise %, Price Momentum 12M
**Yield / Capital Return:** Total Shareholder Yield (Dividend + Buyback), Buyback Yield, Payout Ratio
**Risk / Liquidity:** Realized Volatility 1Y, Average Daily Volume ($), Beta (raw, not Axioma), Short Interest Ratio
**Size:** Weighted Median Market Cap, Number of Securities by Cap Bucket

Don't need to spend time coming up with new custom metrics at this point — just the standard ones that are easy to add to the export.

---

## 6. ROW CONSISTENCY

I confirmed that Sector Weights rows are consistent across all 158 weekly groups (no rows appear/disappear mid-file). Can you confirm this applies to all section types?

If there's any doubt, similar to the way the data is populated at the beginning of each period, it might help to also populate the strategy and the group name on each period — so I can verify that all the numbers are really assigned properly. That may be overkill if we're sure that rows don't shift when a group disappears for a week. However, since we're going to unhide all groups, the odds of that happening are even lower. Yet if this isn't too data-inefficient and has even a tiny bit of advantage in your view, let's implement the extra sanity columns.

---

## Summary Table

| # | Item | Type | Priority |
|---|------|------|----------|
| 1A | Security: all portfolio holdings | Fix | **Critical** |
| 1B | Security: include benchmark securities | Fix | **Critical** |
| 1C-A | Security: per-holding factor TE contribution | New | **Highest** |
| 1C-B | Security: per-holding raw factor exposures | New | **High** |
| 1C-C | Security: market cap column | New | High |
| 2A | Overall rank table: collapse all quintiles | Fix | **High** |
| 3A | Group tables: include all groups (zero-weight rows) | Fix | **High** |
| 3B | Industry: combine GICS name changes | Fix | High |
| 4 | 18 Style Snapshot: add % of Variance column | New | High |
| 5 | PortChars: additional fundamentals | New | Medium |
| 6 | Row consistency / sanity columns | Question | Medium |

Items 1A and 1B are the most important — everything else builds on having a complete Security section. I'd like to resolve those before the expanded run so the output captures the full picture from day one.

I'm still going through the data and may uncover more issues — a few of them took a while to figure out that they were missing. However, I wanted to bring you into the loop again since it has been a while since we spoke and that's plenty to start with.

If you are open to having a call tomorrow morning as a work session to review and perhaps even solve some of these issues together, it would help — since I'm out Thursday and Friday is Good Friday, so it would be good to get something going.

Thanks,
Yuda
