# RR Parser — Schema Comparison

**Generated:** 2026-04-09 18:45

**Purpose:** Compare CSV section schemas between old (3-year, pre-expansion) and new (April sample) files. The new parser will use this schema as its source of truth, reading column positions by name from the `Section` header rows instead of hard-coding them.

**Files:**
- **Old:** `/Users/ygoodman/Downloads/risk_reports_3yr.csv` — 3-year historical file, ~30MB, wide format, 158 weekly periods
- **New:** `/Users/ygoodman/Downloads/risk_reports_csv.csv` — April sample file, ~18MB, 4 weekly periods, includes new factor contribution columns

**Status legend:**
- ✅ Structure unchanged between old and new
- ⚠️ Column offset shifted
- ➕ New column in new file
- ➖ Removed in new file

---

## Quick Summary

| Section | Old group_size | New group_size | Old groups | New groups | Notes |
|---|---|---|---|---|---|
| ⚠️ 18 Style Snapshot | 7 | 8 | 158 | 4 | size 7→8, periods 158→4, +1 new cols |
| ✅ Country | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ Group | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ Industry | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ Overall | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ Portfolio Characteristics | 0 | 0 | 0 | 0 | — |
| ✅ QUAL | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ REV | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ Region | 19 | 19 | 158 | 4 | periods 158→4 |
| ✅ RiskM | 53 | 53 | 1 | 1 | — |
| ✅ Sector Weights | 19 | 19 | 158 | 4 | periods 158→4 |
| ⚠️ Security | 24 | 40 | 158 | 4 | size 24→40, periods 158→4, +16 new cols |
| ✅ VAL | 19 | 19 | 158 | 4 | periods 158→4 |

## 18 Style Snapshot

| Property | Old | New |
|---|---|---|
| Total columns | 1113 | 39 |
| Group start col | 7 | 7 |
| Group size | 7 | 8 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `Period End Date` | +1 | +1 | ✅ |
| `Average Active Exposure` | +2 | +2 | ✅ |
| `Compounded Factor Return` | +3 | +3 | ✅ |
| `Compounded Factor Impact` | +4 | +4 | ✅ |
| `Factor Standard Deviation` | +5 | +5 | ✅ |
| `Cumulative_Factor_Impact` | +6 | +6 | ✅ |

**➕ New columns added in new file:**

| Column | New offset |
|---|---|
| `% Factor Contr. to Tot. Risk` | +7 |

---

## Country

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T-filter` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Group

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Industry

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `Over_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Overall

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Portfolio Characteristics

| Property | Old | New |
|---|---|---|
| Total columns | 45 | 45 |
| Group start col | None | None |
| Group size | 0 | 0 |
| Number of groups (weekly periods) | 0 | 0 |

**Non-repeating (vertical) columns:**

| Column | Old col | New col | |
|---|---|---|---|
| `Period Start Date:P` | 7 | 7 | ✅ |
| `Portfolio:P` | 8 | 8 | ✅ |
| `Predicted Tracking Error (Std Dev):P` | 10 | 10 | ✅ |
| `Axioma- Predicted Beta to Benchmark:P` | 11 | 11 | ✅ |
| `# of Securities:P` | 12 | 12 | ✅ |
| `Port. Ending Active Share:P` | 13 | 13 | ✅ |
| `Market Capitalization:P` | 14 | 14 | ✅ |
| `Axioma World-Wide Fundamental Equity Risk Model MH 4:P` | 15 | 15 | ✅ |
| `Axioma- Historical Beta:P` | 16 | 16 | ✅ |
| `Port. MPT Beta:P` | 17 | 17 | ✅ |
| `EPS Growth - Hist. 3Yr:P` | 18 | 18 | ✅ |
| `EPS Growth - Est. 3-5Yr:P` | 19 | 19 | ✅ |
| `3M EPS Revisions - FY1:P` | 20 | 20 | ✅ |
| `6M EPS Revisions - FY1:P` | 21 | 21 | ✅ |
| `FCF Yield - NTM:P` | 22 | 22 | ✅ |
| `Dividend Yield - Annual:P` | 23 | 23 | ✅ |
| `ROE - NTM:P` | 24 | 24 | ✅ |
| `Operating Margin - NTM:P` | 25 | 25 | ✅ |
| `Period Start Date:B` | 26 | 26 | ✅ |
| `Portfolio:B` | 27 | 27 | ✅ |
| `Predicted Tracking Error (Std Dev):B` | 29 | 29 | ✅ |
| `Axioma- Predicted Beta to Benchmark:B` | 30 | 30 | ✅ |
| `# of Securities:B` | 31 | 31 | ✅ |
| `Port. Ending Active Share:B` | 32 | 32 | ✅ |
| `Market Capitalization:B` | 33 | 33 | ✅ |
| `Axioma World-Wide Fundamental Equity Risk Model MH 4:B` | 34 | 34 | ✅ |
| `Axioma- Historical Beta:B` | 35 | 35 | ✅ |
| `Port. MPT Beta:B` | 36 | 36 | ✅ |
| `EPS Growth - Hist. 3Yr:B` | 37 | 37 | ✅ |
| `EPS Growth - Est. 3-5Yr:B` | 38 | 38 | ✅ |
| `3M EPS Revisions - FY1:B` | 39 | 39 | ✅ |
| `6M EPS Revisions - FY1:B` | 40 | 40 | ✅ |
| `FCF Yield - NTM:B` | 41 | 41 | ✅ |
| `Dividend Yield - Annual:B` | 42 | 42 | ✅ |
| `ROE - NTM:B` | 43 | 43 | ✅ |
| `Operating Margin - NTM:B` | 44 | 44 | ✅ |

---

## QUAL

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## REV

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Region

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## RiskM

| Property | Old | New |
|---|---|---|
| Total columns | 60 | 60 |
| Group start col | 7 | 7 |
| Group size | 53 | 53 |
| Number of groups (weekly periods) | 1 | 1 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `Fundamental Characteristics` | +1 | +1 | ✅ |
| `Price/Earnings` | +2 | +2 | ✅ |
| `Price/Book` | +3 | +3 | ✅ |
| `BMK Price/Earnings` | +4 | +4 | ✅ |
| `BMK Price/Book` | +5 | +5 | ✅ |
| `Risk Characteristics` | +6 | +6 | ✅ |
| `Total Risk` | +8 | +8 | ✅ |
| `Benchmark Risk` | +9 | +9 | ✅ |
| `Predicted Beta` | +10 | +10 | ✅ |
| `Risk (%)` | +11 | +11 | ✅ |
| `% Asset Specific Risk` | +13 | +13 | ✅ |
| `% Factor Risk` | +14 | +14 | ✅ |
| `% of Variance` | +15 | +15 | ✅ |
| `Exposure` | +33 | +33 | ✅ |
| `Axioma World-Wide Fundamental Equity Risk Model MH 4` | +34 | +34 | ✅ |
| `Active Exposure` | +35 | +35 | ✅ |
| `Dividend Yield` | +36 | +36 | ✅ |
| `Earnings Yield` | +37 | +37 | ✅ |
| `Exchange Rate Sensitivity` | +38 | +38 | ✅ |
| `Growth` | +39 | +39 | ✅ |
| `Leverage` | +40 | +40 | ✅ |
| `Liquidity` | +41 | +41 | ✅ |
| `Market Sensitivity` | +42 | +42 | ✅ |
| `Medium-Term Momentum` | +43 | +43 | ✅ |
| `Profitability` | +44 | +44 | ✅ |
| `Size` | +45 | +45 | ✅ |
| `Value` | +46 | +46 | ✅ |
| `Volatility` | +47 | +47 | ✅ |
| `Market` | +48 | +48 | ✅ |
| `Local` | +49 | +49 | ✅ |
| `Industry` | +50 | +50 | ✅ |
| `Country` | +51 | +51 | ✅ |
| `Currency` | +52 | +52 | ✅ |

---

## Sector Weights

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WA` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `Val_Avg` | +14 | +14 | ✅ |
| `Qual_Avg` | +15 | +15 | ✅ |
| `MOM_Avg` | +16 | +16 | ✅ |
| `REV_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Security

| Property | Old | New |
|---|---|---|
| Total columns | 3799 | 167 |
| Group start col | 7 | 7 |
| Group size | 24 | 40 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `Redwood GICS Sector` | +1 | +1 | ✅ |
| `Redwood Region1` | +2 | +2 | ✅ |
| `Redwood Country` | +3 | +3 | ✅ |
| `Industry Rollup` | +4 | +4 | ✅ |
| `RWOOD_SUBGROUP` | +5 | +5 | ✅ |
| `W` | +6 | +6 | ✅ |
| `Bench. Weight` | +7 | +7 | ✅ |
| `AW` | +8 | +8 | ✅ |
| `%S` | +9 | +9 | ✅ |
| `%T` | +10 | +10 | ✅ |
| `%T_Check` | +11 | +11 | ✅ |
| `OVER_WAvg` | +12 | +12 | ✅ |
| `REV_WAvg` | +13 | +13 | ✅ |
| `VAL_WAvg` | +14 | +14 | ✅ |
| `QUAL_WAvg` | +15 | +15 | ✅ |
| `MOM_WAvg` | +16 | +16 | ✅ |
| `STAB_WAvg` | +17 | +17 | ✅ |
| `OVER_Avg` | +18 | +18 | ✅ |
| `REV_Avg` | +19 | +19 | ✅ |
| `VAL_Avg` | +20 | +20 | ✅ |
| `QUAL_Avg` | +21 | +21 | ✅ |
| `MOM_Avg` | +22 | +22 | ✅ |
| `STAB_Avg` | +23 | +23 | ✅ |

**➕ New columns added in new file:**

| Column | New offset |
|---|---|
| `% Factor Contr. to Tot. Risk:Country` | +38 |
| `% Factor Contr. to Tot. Risk:Currency` | +39 |
| `% Factor Contr. to Tot. Risk:Dividend Yield` | +24 |
| `% Factor Contr. to Tot. Risk:Earnings Yield` | +25 |
| `% Factor Contr. to Tot. Risk:Exchange Rate Sensitivity` | +26 |
| `% Factor Contr. to Tot. Risk:Growth` | +27 |
| `% Factor Contr. to Tot. Risk:Industry` | +37 |
| `% Factor Contr. to Tot. Risk:Leverage` | +28 |
| `% Factor Contr. to Tot. Risk:Liquidity` | +29 |
| `% Factor Contr. to Tot. Risk:Market` | +36 |
| `% Factor Contr. to Tot. Risk:Market Sensitivity` | +30 |
| `% Factor Contr. to Tot. Risk:Medium-Term Momentum` | +31 |
| `% Factor Contr. to Tot. Risk:Profitability` | +32 |
| `% Factor Contr. to Tot. Risk:Size` | +33 |
| `% Factor Contr. to Tot. Risk:Value` | +34 |
| `% Factor Contr. to Tot. Risk:Volatility` | +35 |

---

## VAL

| Property | Old | New |
|---|---|---|
| Total columns | 3009 | 83 |
| Group start col | 7 | 7 |
| Group size | 19 | 19 |
| Number of groups (weekly periods) | 158 | 4 |

**Repeating-group columns present in both files:**

| Column | Old offset | New offset | |
|---|---|---|---|
| `Period Start Date` | +0 | +0 | ✅ |
| `W` | +1 | +1 | ✅ |
| `Bench. Weight` | +2 | +2 | ✅ |
| `AW` | +3 | +3 | ✅ |
| `%S` | +4 | +4 | ✅ |
| `%T` | +5 | +5 | ✅ |
| `%T_Check` | +6 | +6 | ✅ |
| `OVER_WAvg` | +7 | +7 | ✅ |
| `REV_WAvg` | +8 | +8 | ✅ |
| `VAL_WAvg` | +9 | +9 | ✅ |
| `QUAL_WAvg` | +10 | +10 | ✅ |
| `MOM_WAvg` | +11 | +11 | ✅ |
| `STAB_WAvg` | +12 | +12 | ✅ |
| `OVER_Avg` | +13 | +13 | ✅ |
| `REV_Avg` | +14 | +14 | ✅ |
| `VAL_Avg` | +15 | +15 | ✅ |
| `QUAL_Avg` | +16 | +16 | ✅ |
| `MOM_Avg` | +17 | +17 | ✅ |
| `STAB_Avg` | +18 | +18 | ✅ |

---

## Column Name Aliases Detected

These are names that are semantically the same but spelled differently across sections. The new parser will normalize all of them to one canonical name.

- **Canonical `OVERWAVG`**: `OVER_WAvg`, `Over_WAvg`
- **Canonical `QUALAVG`**: `QUAL_Avg`, `Qual_Avg`
- **Canonical `VALAVG`**: `VAL_Avg`, `Val_Avg`

## Proposed Canonical Field Map

The parser will look up fields by these canonical keys. This lets us handle any future column additions without changing the parser — just add a new canonical entry.

```python
CANONICAL = {
    # Fixed prefix (same in both files)
    'SECTION': 'Section',
    'ACCT': 'ACCT',
    'DATE': 'DATE',
    'LEVEL2': 'Level2',          # item name (sector/country/industry/etc)
    'SECURITY_NAME': 'SecurityName',
    'PERIOD_START': 'Period Start Date',
    'PERIOD_END': 'Period End Date',
    
    # Group/rank table fields (repeating per weekly group)
    'W': 'W',                     # portfolio weight
    'BW': 'Bench. Weight',        # benchmark weight
    'AW': 'AW',                   # active weight
    'PCT_S': '%S',                # stock-specific TE
    'PCT_T': '%T',                # total TE contribution
    'T_CHECK': '%T_Check',        # inclusion flag (also '%T-filter' in Country section)
    
    # Rank WAvg (weighted average)
    'OVER_WAVG': 'OVER_WAvg',     # also 'Over_WAvg' in Industry
    'REV_WAVG': 'REV_WAvg',
    'VAL_WAVG': 'VAL_WAvg',
    'QUAL_WAVG': 'QUAL_WAvg',     # also 'QUAL_WA' in Sector Weights (old file only)
    'MOM_WAVG': 'MOM_WAvg',
    'STAB_WAVG': 'STAB_WAvg',
    
    # Rank Avg (simple average)
    'OVER_AVG': 'OVER_Avg',
    'REV_AVG': 'REV_Avg',
    'VAL_AVG': 'VAL_Avg',         # also 'Val_Avg' in Sector Weights (old file)
    'QUAL_AVG': 'QUAL_Avg',       # also 'Qual_Avg' in Sector Weights (old file)
    'MOM_AVG': 'MOM_Avg',
    'STAB_AVG': 'STAB_Avg',
    
    # Security-only classification cols
    'SEC_GICS': 'Redwood GICS Sector',
    'SEC_REGION': 'Redwood Region1',
    'SEC_COUNTRY': 'Redwood Country',
    'SEC_INDUSTRY': 'Industry Rollup',
    'SEC_SUBGROUP': 'RWOOD_SUBGROUP',
    
    # Security per-holding factor contribution (NEW in April file)
    'FC_DIV_YIELD': '% Factor Contr. to Tot. Risk:Dividend Yield',
    'FC_EARN_YIELD': '% Factor Contr. to Tot. Risk:Earnings Yield',
    'FC_FX': '% Factor Contr. to Tot. Risk:Exchange Rate Sensitivity',
    'FC_GROWTH': '% Factor Contr. to Tot. Risk:Growth',
    'FC_LEVERAGE': '% Factor Contr. to Tot. Risk:Leverage',
    'FC_LIQUIDITY': '% Factor Contr. to Tot. Risk:Liquidity',
    'FC_MKT_SENS': '% Factor Contr. to Tot. Risk:Market Sensitivity',
    'FC_MOMENTUM': '% Factor Contr. to Tot. Risk:Medium-Term Momentum',
    'FC_PROFIT': '% Factor Contr. to Tot. Risk:Profitability',
    'FC_SIZE': '% Factor Contr. to Tot. Risk:Size',
    'FC_VALUE': '% Factor Contr. to Tot. Risk:Value',
    'FC_VOLATILITY': '% Factor Contr. to Tot. Risk:Volatility',
    'FC_MARKET': '% Factor Contr. to Tot. Risk:Market',
    'FC_INDUSTRY': '% Factor Contr. to Tot. Risk:Industry',
    'FC_COUNTRY': '% Factor Contr. to Tot. Risk:Country',
    'FC_CURRENCY': '% Factor Contr. to Tot. Risk:Currency',
    
    # 18 Style Snapshot (NEW column at end of group in April file)
    'SNAP_AVG_EXP': 'Average Active Exposure',
    'SNAP_RET': 'Compounded Factor Return',
    'SNAP_IMP': 'Compounded Factor Impact',
    'SNAP_STD': 'Factor Standard Deviation',
    'SNAP_CIMP': 'Cumulative_Factor_Impact',
    'SNAP_RISK_CONTR': '% Factor Contr. to Tot. Risk',   # NEW
}

# Aliases: multiple raw names → one canonical key
ALIASES = {
    '%T-filter': 'T_CHECK',
    'Over_WAvg': 'OVER_WAVG',
    'QUAL_WA': 'QUAL_WAVG',
    'Val_Avg': 'VAL_AVG',
    'Qual_Avg': 'QUAL_AVG',
}
```

## Parser Design

The new parser (`factset_parser_v3.py`) will:

1. **First pass — schema discovery:** Iterate the file once, find every `Section` header row, and build a per-section schema dict keyed by canonical field name.
2. **Second pass — data extraction:** Iterate again, and for each data row look up fields by canonical name via the schema, applying alias mapping when needed.
3. **No hard-coded column positions anywhere.** If FactSet adds a column in the future, the schema auto-adapts.
4. **Per-holding factor contributions** become a dict on each holding: `h.factor_contr = {dividend_yield: -0.05, earnings_yield: -0.04, ...}`.
5. **Backward compatible** — works on both old 3-year file (158 periods, no factor contribs) and new April sample (4 periods, with factor contribs).

