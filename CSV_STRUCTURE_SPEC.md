# FactSet CSV Structure Specification
## Based on: risk_reports_s2_randomized.csv (v2 format)

### File Basics
- 514 total columns (header), 1,964 data rows
- 12 distinct section headers
- 7 strategies: IDM, ACWIXUS, EM, ISC, SCG, ACWI, GSC
- 4 weekly dates: 1/30/2026, 2/6/2026, 2/13/2026, 2/20/2026, 2/27/2026

### Section Layout Summary

| Section | Rows | Date Layout | Weekly Groups | Has Data Row |
|---------|------|-------------|---------------|-------------|
| Sector Weights | 66 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| Region | 48 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| Country | 105 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| Industry | 111 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| Group | 64 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| Security | 294 | Horizontal (5 groups × 24 cols) | ✅ (24 = date+5grouping+18metrics) | ❌ for most accounts |
| Overall | 134 | Horizontal (5 groups × 19 cols) | ✅ (quintile+ticker rows) | ❌ |
| REV | 42 | Horizontal (5 groups × 19 cols) | ✅ (quintile rows only) | ❌ |
| QUAL | 42 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| VAL | 39 | Horizontal (5 groups × 19 cols) | ✅ | ❌ |
| RiskM | 28 | Vertical (1 row per date) | N/A | ✅ (Level2="Data") |
| Portfolio Characteristics | 28 | Vertical (1 row per date) | N/A | ✅ (Level2="Data") |
| 18 Style Snapshot | 951 | Per-factor (1 row per factor, 5 periods × 7 cols) | N/A | ❌ |

### RiskM Column Map (COMPLETE)
```
col[7]  = Period Start Date
col[8]  = (Fundamental Characteristics label)
col[9]  = Price/Earnings (portfolio)
col[10] = Price/Book (portfolio)
col[11] = BMK Price/Earnings
col[12] = BMK Price/Book
col[13] = (Risk Characteristics label)
col[14] = (Axioma model label)
col[15] = Total Risk (total portfolio volatility, NOT tracking error)
col[16] = Benchmark Risk
col[17] = Predicted Beta
col[18] = (Risk % label)
col[19] = (Axioma model label)
col[20] = % Asset Specific Risk (of total risk)
col[21] = % Factor Risk (of total risk)
col[22] = (% of Variance label)
--- % of Variance per style factor (TE contribution) ---
col[23] = Dividend Yield
col[24] = Earnings Yield
col[25] = Exchange Rate Sensitivity
col[26] = Growth
col[27] = Leverage
col[28] = Liquidity
col[29] = Market Sensitivity
col[30] = Medium-Term Momentum
col[31] = Profitability
col[32] = Size
col[33] = Value
col[34] = Volatility
col[35] = Market
col[36] = Local
col[37] = Industry (aggregate)
col[38] = Country (aggregate)
col[39] = Currency (aggregate)
col[40] = (Exposure label)
col[41] = (Axioma model label)
col[42] = (Active Exposure label)
--- Active Exposure per style factor ---
col[43] = Dividend Yield
col[44] = Earnings Yield
col[45] = Exchange Rate Sensitivity
col[46] = Growth
col[47] = Leverage
col[48] = Liquidity
col[49] = Market Sensitivity
col[50] = Medium-Term Momentum ← PARSER WAS MISSING THIS
col[51] = Profitability ← MISSED
col[52] = Size ← MISSED
col[53] = Value ← MISSED
col[54] = Volatility ← MISSED
col[55] = Market ← MISSED
col[56] = Local ← MISSED
col[57] = Industry (aggregate) ← MISSED
col[58] = Country (aggregate) ← MISSED
col[59] = Currency (aggregate) ← MISSED
col[60+] = Individual industry/country/currency factor breakdowns (hundreds of cols)
```

### Portfolio Characteristics Column Map (P and B)
```
PORTFOLIO (:P) section:
col[7]  = Period Start Date
col[8]  = (Portfolio label)
col[9]  = (Axioma model label)
col[10] = Predicted Tracking Error (Std Dev) ← THIS IS TE
col[11] = Axioma Predicted Beta to Benchmark
col[12] = # of Securities
col[13] = Port. Ending Active Share
col[14] = Market Capitalization
col[15] = (Axioma model label)
col[16] = Axioma Historical Beta
col[17] = Port. MPT Beta
col[18] = EPS Growth - Hist. 3Yr
col[19] = EPS Growth - Est. 3-5Yr
col[20] = 3M EPS Revisions - FY1
col[21] = 6M EPS Revisions - FY1
col[22] = FCF Yield - NTM
col[23] = Dividend Yield - Annual
col[24] = ROE - NTM
col[25] = Operating Margin - NTM

BENCHMARK (:B) section (offset +19):
col[26] = Period Start Date (benchmark)
col[27-44] = Same fields as col[8-25] but for benchmark
```

### Security Section Column Map (per weekly group = 24 cols)
```
col[0]  = "Security" (section label)
col[1]  = ACCT
col[2]  = DATE (randomized)
col[3]  = PortfolioCurCode
col[4]  = Level
col[5]  = Ticker (Level2)
col[6]  = SecurityName

Per weekly group (5 groups, each 24 columns):
  +0  = Period Start Date
  +1  = Redwood GICS Sector
  +2  = Redwood Region1
  +3  = Redwood Country
  +4  = Industry Rollup
  +5  = RWOOD_SUBGROUP
  +6  = W (Portfolio Weight)
  +7  = Bench. Weight
  +8  = AW (Active Weight)
  +9  = %S (Stock-Specific TE)
  +10 = %T (Total TE Contribution)
  +11 = %T_Check
  +12 = OVER_WAvg
  +13 = REV_WAvg
  +14 = VAL_WAvg
  +15 = QUAL_WAvg
  +16 = MOM_WAvg
  +17 = STAB_WAvg
  +18 = OVER_Avg
  +19 = REV_Avg
  +20 = VAL_Avg
  +21 = QUAL_Avg
  +22 = MOM_Avg
  +23 = STAB_Avg
```

### Rank Sections (Overall, REV, VAL, QUAL)
```
Overall section has BOTH:
  - Quintile summary rows (Level2 = float like "1.239" → round to 1)
  - Individual holding rows within each quintile (Level2 = ticker)

REV/VAL/QUAL sections have ONLY:
  - Quintile summary rows (no individual holdings)

Special rows:
  - @NA = unassigned holdings
  - Level2 as float (randomized from integer 1-5)
```

### 18 Style Snapshot Column Map (per period = 7 cols)
```
5 periods, each 7 columns:
  +0 = Period Start Date
  +1 = Period End Date
  +2 = Average Active Exposure
  +3 = Compounded Factor Return
  +4 = Compounded Factor Impact
  +5 = Factor Standard Deviation
  +6 = Cumulative Factor Impact

128 factors per strategy:
  12 style + 26 countries + 70 industries + 19 currencies + 1 Global Market
```

### Key Gotchas
1. TE is in PortChars col[10], NOT RiskM col[15] (which is Total Risk)
2. pct_specific/pct_factor are % of Total Risk, not % of TE
3. Security groups are 24 cols (not 19) because of 5 grouping columns
4. Rank Level2 values are FLOATS in randomized data (round to int)
5. Overall section mixes quintile rows and ticker rows
6. Sector/Region/Country/Industry/Group have NO Data summary rows
7. Security section may have NO Data row for some accounts
8. Variable non-empty column counts across holdings (37-79)
9. RiskM active exposures go to col[59], not col[49]
10. RiskM cols 60+ have individual industry/country/currency breakdowns
