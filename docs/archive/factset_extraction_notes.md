# FactSet Portfolio Attribution Export — Technical Notes & Questions
**To:** FactSet Extraction Team
**From:** Redwood Risk
**Re:** Upcoming production data pull (Monday) — format clarifications and data gaps
**Date:** 2026-03-20

---

## Context

We have reviewed the sample export (`risk_reports_sample.csv`) in detail and built a parsing pipeline against it. Before the full production pull, we need to align on a few design questions and flag several data gaps that will affect what we can and cannot derive from the output.

---

## Section 1 — Design Questions (Decisions Needed)

### 1.1 Benchmark Holdings — By Design?

The current export includes **all benchmark constituent holdings**, not just the portfolio positions. For strategies with large benchmarks (e.g. ACWI with 2,514 benchmark members), this results in thousands of rows per account where `W` (portfolio weight) is zero and only `Bench. Weight` is populated. This inflates the file significantly.

**Question:** Is this inclusion of benchmark-only holdings intentional, or can the export be filtered to portfolio holdings only?

**Our preference if it is by design (or cannot be changed):**
We are fine retaining benchmark-only holdings as long as a filter is applied so that a security is included *only if at least one of the following is true*:

- `Bench. Weight ≥ 0.5%` (meaningful benchmark position), **OR**
- The security contributes **more than 1% of tracking error** to the portfolio (i.e., it is a meaningful risk driver even if not held)

Holdings below both thresholds should be suppressed — they add no analytical value and materially inflate file size. If implementing this filter at the extraction level is not feasible, please let us know and we will apply it at the parsing layer.

---

### 1.2 Weekly Data — One Row or One Row Per Week?

The current format encodes **5 weekly snapshots as repeating column groups** within a single row (columns 7–24 = week 1, 25–42 = week 2, … 79–96 = week 5). This works for the current single-month export.

**Question:** For the full history pull, will each monthly file contain a fresh set of 5 columns representing that month's weeks, or will the file concatenate multiple months with each month as a separate block of rows?

**Our preference:** One row per security per week (i.e., flatten the 5 column groups into separate rows, each with a `WEEK_DATE` column). This makes time-series analysis far simpler and avoids hardcoding column-group offsets in the parser. If the current wide format is fixed, please confirm the column structure so we can handle it correctly.

---

## Section 2 — Missing Fields (Data Gaps)

The fields below were either absent from the sample or could not be reliably mapped. Providing them in the production pull would directly enable the corresponding dashboard tiles.

### 2.1 Per-Holding Sector & Country Classification

**Status:** Not present per holding. Sector and country are only available as aggregate grouping rows (e.g., a row for "Industrials" with the total portfolio weight). Individual holding rows (`Level2 = *ARX`, `BNGN9Z`, etc.) contain no sector or country field.

**Impact:** The Holdings tab cannot display sector or country alongside each position.

**Request:** Add `Sector` and `Country` columns to each individual security row, or provide a separate mapping file (ticker → sector, country).

---

### 2.2 Factor Return Column Empty

**Status:** Factor attribution IS present in the file. The `DATE=20260206` section contains a separate table (near the end of the file) with header columns: `Average Active Exposure`, `Compounded Factor Return`, `Compounded Factor Impact`, `Factor Standard Deviation`, `Cumulative_Factor_Impact` — repeating for 5 weekly periods.

We are successfully parsing:
- `c` — `Compounded Factor Impact` (period 5 = most recent week) ✓
- `imp` — `Cumulative_Factor_Impact` (running total through week 5) ✓
- `ret` — `Compounded Factor Return`: **column is present but ALL VALUES ARE BLANK** across all factors and all strategies

**Impact:** `c` and `imp` are parsed correctly. `ret` is null everywhere in the current sample.

**Request:** Confirm whether `Compounded Factor Return` is intentionally empty in this export configuration, or if it can be switched on. If factor return is available in a different field or tile, please indicate where.

---

### 2.3 Portfolio Beta

**Status:** ✅ Present. The portfolio stats section (the table with header `Predicted Tracking Error (Std Dev):P`, `Axioma- Predicted Beta to Benchmark:P`, etc.) contains weekly predicted beta values. We are parsing this correctly (IDM sample: 1.03–1.05 across the 4 January weeks).

No action needed on this field.

---

### 2.4 Success Rate / Hit Rate

**Status:** Not present. No column maps to success rate (% of active positions contributing positively to return).

**Impact:** The Overview tab "Success Rate" card will remain blank.

**Request:** Add hit rate (or batting average) as a portfolio-level summary metric in the `Data` rows if available.

---

### 2.5 Per-Holding Characteristics (Fundamentals)

**Status:** Mostly present. The portfolio stats section (same section as beta/TE) contains portfolio and benchmark weighted-average fundamentals:

| Metric | Status |
|---|---|
| Market Cap ($M) | ✓ Present |
| ROE NTM (%) | ✓ Present |
| FCF Yield NTM (%) | ✓ Present |
| Dividend Yield Annual (%) | ✓ Present |
| EPS Growth Hist 3Yr (%) | ✓ Present |
| Operating Margin NTM (%) | ✓ Present |
| Price/Earnings | ✓ Present (portfolio only) — found in Fundamental Characteristics tile |
| Price/Book | ✓ Present (portfolio only) — found in Fundamental Characteristics tile |
| Price/Earnings (benchmark) | ✗ Not available in any tile in current export |
| Price/Book (benchmark) | ✗ Not available in any tile in current export |

**Request:** Confirm whether benchmark P/E and P/B can be added to the export. Portfolio-side values are already mapping correctly.

---

### 2.6 Tracking Error Per Holding (Marginal Contribution to Risk)

**Status:** The `%T` column in holding rows appears to contain something (values like `0.7` for a 2.1% position), but its exact definition is unclear. Is this:
- Marginal contribution to tracking error (%), or
- Percent of total tracking error attributable to this holding?

**Request:** Confirm the definition of `%T` at the holding level. If MCR (marginal contribution to risk) is available separately, please include it.

---

### 2.7 OVER_WAvg Field — Clarification Needed

**Status:** In holding rows, `OVER_WAvg` contains values between 1.0 and 5.0. Our analysis found that ~84% of holdings show a value of exactly `1.0`.

**Question:** Is this column an analyst overall rating (1=Sell, 5=Buy on a 1–5 scale), or something else (e.g., quintile rank, Z-score)? The high concentration at `1.0` is unusual if it represents a distribution across 1–5. Please clarify the scale, direction, and source.

---

### 2.8 Historical Monthly Data

**Status:** The sample contains one month (January 2026). The dashboard includes a historical trend panel that displays trailing 36-month time series for TE, Active Share, Beta, and factor exposures.

**Request:** For the production pull, include as many trailing months as available in the same format. Confirm whether historical months will be included as additional date-partitioned rows in the same file, or as separate monthly files.

---

## Section 3 — What Is Mapping Correctly

For confidence, the following is fully parsed and validated from the current export:

| Dashboard Section | Status | Notes |
|---|---|---|
| Sectors (GICS L1) | ✅ Clean | 11 sectors, weight sums ~100% |
| Countries | ✅ Clean | Deduplicated (USA/Usa normalization applied) |
| Regions | ✅ Clean | 7 buckets match dashboard exactly |
| Custom Groups | ✅ Clean | 8 buckets (CYCLICALS, DEFENSIVE, GROWTH, COMMODITY, RATE SENSITIVE) |
| Factor Exposures | ✅ Clean | 16 factors, portfolio + benchmark loading |
| Holdings (portfolio) | ✅ Clean | Ticker, name, weight, active weight, factor scores |
| Unowned Risk | ✅ Partial | BM-only holdings captured; sector/country per holding missing |
| Summary Stats | ✅ Clean | TE, Active Share, Holdings count, BH count, Cash |
| Portfolio Beta | ✅ Clean | `Predicted Beta to Benchmark` from portfolio stats section; See §2.3 |
| Market Cap | ✅ Clean | Portfolio and benchmark from portfolio stats section |
| Fundamentals (ROE, FCF, Div, EPS, OpMargin) | ✅ Clean | Portfolio vs benchmark from stats section; See §2.5 |
| P/E and P/B (portfolio) | ✅ Clean | Found in Fundamental Characteristics tile; See §2.5 |
| Weekly History | ✅ Partial | 4 of 5 weekly points recovered from portfolio stats rows |
| Factor attribution (c, imp) | ✅ Partial | CompoundedFactorImpact and CumulativeFactorImpact mapped; See §2.2 |
| Factor return (ret) | ❌ Empty | CompoundedFactorReturn column present but blank; See §2.2 |
| Per-holding sector/country | ❌ Missing | See §2.1 |
| Benchmark P/E and P/B | ❌ Missing | Portfolio side found; benchmark not in export; See §2.5 |
| Success rate | ❌ Missing | See §2.4 |

---

## Section 4 — Summary of Requests for Monday Pull

1. **Benchmark holdings filter**: include BM-only rows only if BW ≥ 0.5% or TE contribution > 1%
2. **Clarify/confirm weekly format**: wide (5 col groups) vs. long (one row per week)
3. **Add per-holding sector and country columns**
4. **Confirm `Compounded Factor Return` column**: currently blank — can it be enabled?
5. **Add hit rate / success rate** to summary/Data rows (if available)
6. **Confirm benchmark P/E and P/B availability**: portfolio P/E/P/B found; benchmark side missing
7. **Clarify `OVER_WAvg` definition and scale** at the holding level
8. **Clarify `%T` definition** at the holding level (MCR vs. % of total TE)
9. **Include trailing monthly history** (as many months as available)
10. **Fix CSV quoting for security names with embedded commas** (e.g. "Pathward Financial, Inc." causes column shift; CASH ticker position lost in GSC/SCG)

*Items resolved (no action needed): Portfolio Beta ✓, TE/Active Share/Holdings count ✓, Market Cap ✓, ROE/FCF/Dividend/EPS/Operating Margin ✓, Portfolio P/E and P/B ✓, Factor Impact/Cumulative Factor Impact ✓*

---

*If any of the above fields are available in a different FactSet report tile not currently included in the export, please indicate which tile to add to the pull configuration.*
