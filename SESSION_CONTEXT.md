# RR Session Context — Complete State Transfer
**Last updated:** 2026-04-01
**Purpose:** Feed this file to Claude at the start of any RR session to restore full context.

## MANDATORY FIRST STEPS
1. Read `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md` — field definitions, column positions, strategy mappings
2. Read this file completely
3. Read `~/RR/DATA_FLOW_MAP.md` — section-by-section data flow diagram
4. **VERIFY claims against actual CSV data before stating them.** No "this works" without showing proof from multiple periods.
5. **One change at a time.** תפסת מרובה לא תפסת — if you grab too much, you grab nothing.

## KEY FILES
| File | What | Lines |
|------|------|-------|
| `~/RR/factset_parser_v2.py` | Python CSV→JSON parser | ~700 |
| `~/RR/dashboard_v7.html` | Single-file dashboard (JS/CSS/HTML) | ~4,200 |
| `~/RR/latest_data.json` | Parsed output from real 3-year file | ~30MB |
| `~/RR/DATA_FLOW_MAP.md` | Every section→field→dashboard mapping | ~200 |
| `~/RR/AUDIT_REPORT.md` | 14-issue audit from March 26 (partially outdated) |
| `~/RR/factset_email_READY_TO_SEND.md` | Email to FactSet (SENT 2026-04-01) |
| `~/RR/factset_email.html` | HTML version for copy-paste |
| `~/RR/risk_reports_last2weeks.csv` | Trimmed CSV (last 2 periods only, 0.8MB) |
| `/Users/ygoodman/Downloads/risk_reports_3yr.csv` | Real 3-year FactSet file (29.7MB) |

## REAL DATA FILE DETAILS
- **File:** `/Users/ygoodman/Downloads/risk_reports_3yr.csv`
- **Size:** 29.7MB, 3,981 rows, up to 3,799 columns
- **Encoding:** UTF-8 with BOM (utf-8-sig)
- **Date range:** 2023-01-31 to 2026-01-30 (158 weekly periods)
- **Strategies:** IDM, ACWI, ACWIXUS (=IOP on dashboard), EM, GSC, ISC, SCG
- **Date format:** YYYY-MM-DD (not M/D/YYYY like the old randomized file)

## CSV SECTION LAYOUT
| Section | Rows | Max Cols | Group Size | Layout |
|---------|------|----------|-----------|--------|
| Sector Weights | 68 | 3009 | 19 | Horizontal: 158 groups |
| Industry | 123 | 3009 | 19 | Horizontal: 158 groups |
| Region | 48 | 3009 | 19 | Horizontal: 158 groups |
| Country | 95 | 3009 | 19 | Horizontal: 158 groups |
| Group | 64 | 3009 | 19 | Horizontal: 158 groups |
| Security | 253 | 3799 | 24 | Horizontal: 158 groups (extra 5 classification cols) |
| Overall | 70 | 3009 | 19 | Horizontal: 158 groups |
| REV | 32 | 3009 | 19 | Horizontal: 158 groups |
| QUAL | 30 | 3009 | 19 | Horizontal: 158 groups |
| VAL | 30 | 3009 | 19 | Horizontal: 158 groups |
| RiskM | 1099 | 60 | — | Vertical: 1 row per date per strategy |
| Portfolio Characteristics | 1099 | 45 | — | Vertical: :P side + :B side |
| 18 Style Snapshot | 957 | 1113 | 7 | Horizontal: 158 groups, 1 row per factor/country/industry |
| Section (headers) | 12 | varies | — | Column name definitions before each section |

## GROUP TABLE COLUMN LAYOUT (19 cols per group)
```
+0  Period Start Date
+1  W (portfolio weight)
+2  Bench. Weight
+3  AW (active weight)
+4  %S (stock-specific TE contribution)
+5  %T (total TE contribution)
+6  %T_Check (inclusion flag, always 1.00)
+7  OVER_WAvg
+8  REV_WAvg
+9  VAL_WAvg
+10 QUAL_WA (truncated header)
+11 MOM_WAvg
+12 STAB_WAvg
+13 OVER_Avg
+14 Val_Avg (NOTE: header says Val_Avg, not VAL_Avg)
+15 Qual_Avg
+16 MOM_Avg
+17 REV_Avg
+18 STAB_Avg
```

## SECURITY COLUMN LAYOUT (24 cols per group)
```
+0  Period Start Date
+1  Redwood GICS Sector
+2  Redwood Region1
+3  Redwood Country
+4  Industry Rollup
+5  RWOOD_SUBGROUP
+6  W
+7  Bench. Weight
+8  AW
+9  %S
+10 %T
+11 %T_Check
+12 OVER_WAvg
+13 REV_WAvg
+14 VAL_WAvg
+15 QUAL_WAvg
+16 MOM_WAvg
+17 STAB_WAvg
+18 OVER_Avg
+19 REV_Avg
+20 VAL_Avg
+21 QUAL_Avg
+22 MOM_Avg
+23 STAB_Avg
```

## RISKM COLUMN LAYOUT (60 cols, vertical)
```
0-6:   Section, ACCT, DATE, Currency, Level, Level2("Data"), SecurityName
7:     Period Start Date
8:     (empty — section divider)
9:     P/E
10:    P/B
11:    BMK P/E
12:    BMK P/B
13-14: (empty — section divider)
15:    Total Risk
16:    Benchmark Risk
17:    Predicted Beta
18-19: (empty — section divider)
20:    % Asset Specific Risk
21:    % Factor Risk
22:    (empty — section divider)
23-34: % of Variance: DivYield, EarningsYield, FXSens, Growth, Leverage, Liquidity, MarketSens, Momentum, Profitability, Size, Value, Volatility
35:    Market
36:    Local (skip — not used)
37:    Industry (AGGREGATE)
38:    Country (AGGREGATE)
39:    Currency (AGGREGATE)
40-42: (empty — section divider)
43-54: Active Exposure: same 12 style factors
55:    Market
56:    Local
57:    Industry (AGGREGATE)
58:    Country (AGGREGATE)
59:    Currency (AGGREGATE)
```

## 18 STYLE SNAPSHOT LAYOUT (7 cols per group)
```
+0  Period Start Date
+1  Period End Date
+2  Average Active Exposure (our tilt vs benchmark)
+3  Compounded Factor Return (pure factor return — same for all portfolios)
+4  Compounded Factor Impact (Exposure × Return = OUR attribution)
+5  Factor Standard Deviation (how volatile this factor is)
+6  Cumulative Factor Impact (running sum — sanity check)
```
Level2 = factor name. 119 items for IDM: 12 style factors + 25 countries + 16 currencies + 65 industries + Global Market

## VERIFIED FIELD MAPPING (parser → JSON → dashboard)

### What's Correct ✅
- PortChars: TE, Beta (predicted), Holdings, Active Share, MCap, EPS Growth, FCF Yield, Div Yield, ROE, Op Margin — all match CSV
- PortChars: HistBeta, MPTBeta, EPSGrowthEst, EPS3M, EPS6M — ADDED this session, verified
- PortChars: All benchmark equivalents (BH, BMcap, B_EPSG, B_FCF, B_Div, B_ROE, B_OpMgn, etc.)
- RiskM: P/E, P/B, BMK P/E, BMK P/B, Total Risk, BM Risk, % Specific, % Factor — all match
- RiskM: Factor % of Variance (cols 23-34) correctly stored as `c` (TE contribution)
- RiskM: Factor Active Exposure (cols 43-54) correctly stored as `a`
- Sector/Country/Region/Industry/Group: n, p(W), b(BW), a(AW), mcr(%S), tr(%T), ranks — all match latest period
- Security: column offsets verified (W=+6, BW=+7, AW=+8, %S=+9, %T=+10, OVER=+12)
- Security: category names (Sector, Region, Country, Industry, Subgroup) match group table names
- Security: parser reads LAST group ([-1]) for current holdings — verified correct
- 18 Style Snapshot: style factor rows parsed (exposure, return, impact, dev, cum_impact)
- Sector rows consistent across all 158 weekly groups (no rows appear/disappear)

### Known Issues ❌
- **Holdings incomplete:** Security section has ~40-80% of holdings missing per strategy. PortChars says h=43 for IDM but Security has only 19 non-zero. This is a FactSet export configuration issue, not a parser bug. REPORTED IN EMAIL.
- **BM weights don't sum to 100%:** Zero-weight sectors/industries/countries excluded from export. REPORTED.
- **Overall rank table:** Two issues: (1) tickers leaking as expanded rows, (2) grouping broken — OVER_WAvg doesn't match quintile across 156 of 158 periods. Period 158 shows exact integers (1,2,3,4,5) which is anomalous. REPORTED.
- **REV/VAL/QUAL rank tables:** Grouping works correctly (self-rank = exact integer). No expand/collapse issues.
- **GICS industry name changes:** Legacy names (Retailing, Media, etc.) appear as separate rows from current names. REPORTED.
- **18 Style Snapshot country/industry/currency rows:** Data exists but parser doesn't extract them yet.
- **MCap in millions:** Parser stores correctly but dashboard should display in billions.
- **Selection Rate:** Not in CSV, computable as h/bh.
- **Factor `e` = `c`:** Parser sets exposure=contribution as backward compat. Not ideal but functional.

### CRITICAL LESSON: Always verify against FIRST period AND last period
The Overall rank table appeared to "work" in period 158 (exact integers) but was broken in all other periods. Always check multiple periods before claiming something works.

## PARSER CONSTANTS
```python
STD_GROUP_SIZE = 19    # Sector, Industry, Region, Country, Group, Rank tables
SEC_GROUP_SIZE = 24    # Security (extra 5 classification cols + 1 extra rank)
SNAP_GROUP_SIZE = 7    # 18 Style Snapshot

RISKM_PE = 9           # P/E in RiskM
RISKM_PB = 10
RISKM_BPE = 11
RISKM_BPB = 12
RISKM_TOTAL_RISK = 15
RISKM_BM_RISK = 16
RISKM_PCT_SPEC = 20
RISKM_PCT_FACTOR = 21
RISKM_PORT_EXP_START = 23   # % of Variance starts here
RISKM_ACTIVE_EXP_START = 43 # Active Exposure starts here

PC_TE = 10, PC_BETA = 11, PC_H = 12, PC_AS = 13, PC_MCAP = 14
PC_HIST_BETA = 16, PC_MPT_BETA = 17
PC_EPSG = 18, PC_EPSG_F = 19, PC_EPS3M = 20, PC_EPS6M = 21
PC_FCFY = 22, PC_DIVY = 23, PC_ROE = 24, PC_OPMGN = 25
PC_BH = 31, PC_BMCAP = 33
```

## NORMALIZE FUNCTION (dashboard_v7.html ~line 520)
Maps parser v2 field names to dashboard v1:
- `w → p` (portfolio weight)
- `bw → b` (benchmark weight)
- `aw → a` (active weight)
- `pct_s → mcr` (stock-specific TE)
- `pct_t → tr` (total TE contribution)
- `over → r` (overall rank, clamped 1-5)
- `hist.summary → hist.sum` (history array)

## FACTSET EMAIL STATUS
**SENT 2026-04-01.** Key requests:
1. Security: all portfolio holdings (CRITICAL)
2. Security: include benchmark securities (CRITICAL)
3. Security: per-holding factor TE contribution columns (HIGHEST)
4. Security: per-holding raw factor exposure columns (HIGH)
5. Security: market cap column
6. Overall rank table: collapse + fix grouping
7. Group tables: unhide all zero-weight groups
8. Industry: combine GICS name changes
9. 18 Style Snapshot: add % of Variance column
10. PortChars: additional fundamentals
11. Row consistency / sanity columns

Awaiting response. Call requested for tomorrow morning.

## REMAINING WORK (Priority Order)
1. Parse 18 Style Snapshot country/industry/currency rows into dashboard
2. Fix MCap display (millions → billions)
3. Compute Selection Rate (h/bh)
4. GICS name mapping in parser (legacy → current)
5. TE y-axis 3-10 (fix didn't take — check browser cache vs code)
6. Continue data validation tile-by-tile on dashboard
7. When FactSet responds: re-parse with expanded file, verify fixes

## PM PREFERENCES (from specialist agent)
- Bloomberg terminal aesthetic (dark theme, data-dense)
- Functionality first, design last
- Small incremental changes — verify each before moving on
- No fake/synthetic data ever
- OVER/REV/VAL/QUAL ranks — always display in that order
- Spotlight ranks = Redwood proprietary (stock selection)
- Axioma factors = risk model (risk decomposition)
- These are DIFFERENT systems — never confuse them
