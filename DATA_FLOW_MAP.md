# RR Dashboard — Complete Data Flow Map

## CSV Sections → Parser → Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FACTSET CSV (14 Sections)                           │
│                     3,981 rows × up to 3,799 cols                          │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 1: Portfolio Characteristics (1 row/date/strategy, 45 cols)        │
│ Layout: vertical — :P side (cols 7-25) + :B side (cols 26-44)             │
│                                                                            │
│ FIELDS:                                                                    │
│  :P  Date, TE, PredBeta, #Securities, ActiveShare, MCap                   │
│      HistBeta, MPTBeta, EPSGrowth3Y, EPSGrowthEst, EPS3M, EPS6M          │
│      FCFYield, DivYield, ROE, OpMargin                                    │
│  :B  Same fields for benchmark                                            │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Summary Cards: TE, Beta, ActiveShare, Holdings, Cash                 │
│  ├─→ Characteristics Table: all P vs B with diffs                         │
│  ├─→ Beta Multi-line Chart: predicted + historical + MPT (3 lines)        │
│  ├─→ hist.sum[]: weekly time series of TE/AS/Beta/Holdings                │
│  └─→ Available Dates: 157 weekly periods                                  │
│                                                                            │
│ PARSED:  ✅ TE, Beta, H, AS, MCap, EPSG, FCF, Div, ROE, OpMgn, BH, BMcap│
│          ✅ HistBeta, MPTBeta, EPSGrowthEst, EPS3M, EPS6M (JUST ADDED)   │
│          ✅ All benchmark equivalents                                      │
│ MISSING: ❌ Selection Rate (computable: H/BH)                             │
│ NOT IN FILE: Revenue Growth, NetDebt/EBITDA, ROIC, EV/EBITDA (requested)  │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 2: RiskM (1 row/date/strategy, 60 cols, vertical)                 │
│ Layout: Fundamentals | Risk | % of Variance | Active Exposure             │
│         (empty cols as section dividers)                                    │
│                                                                            │
│ FIELDS:                                                                    │
│  Fundamentals:  P/E, P/B, BMK P/E, BMK P/B                               │
│  Risk:          TotalRisk, BenchmarkRisk, PredictedBeta                   │
│  % of Variance: %AssetSpecific, %FactorRisk,                              │
│                 12 style factors + Market + Industry(agg) +                │
│                 Country(agg) + Currency(agg)                               │
│  Active Exp:    Same 12+4 factors as z-score active exposures             │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Summary: P/E, P/B (from here, not PortChars)                        │
│  ├─→ Risk Tab: Idio/Factor split pie, TotalRisk, BMRisk                  │
│  ├─→ Factor Table: c=% of Variance, a=Active Exposure per factor         │
│  ├─→ Factor TE Bars: sized by % of Variance                              │
│  ├─→ Risk Stacked Area: factor vs idio TE over time                      │
│  └─→ hist.fac[]: weekly factor exposure time series                       │
│                                                                            │
│ PARSED:  ✅ All fields correctly mapped                                    │
│ GAP:     ⚠️  Industry/Country/Currency only AGGREGATE % of Variance       │
│          Individual breakout requested (B1 in email)                       │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 3: 18 Style Snapshot (1 row/factor-or-group/strategy, 1113 cols)  │
│ Layout: horizontal — 7 cols/group × 158 groups                            │
│ One row per: style factor, country, industry, currency                    │
│                                                                            │
│ FIELDS PER GROUP:                                                          │
│  PeriodStart, PeriodEnd, AvgActiveExposure, CompoundedFactorReturn,       │
│  CompoundedFactorImpact, FactorStdDev, CumulativeFactorImpact            │
│                                                                            │
│ LEVEL2 VALUES (119 for IDM):                                              │
│  12 style factors (Volatility, Momentum, Growth, Value, etc.)             │
│  ~30 countries (France, Japan, UK, US, etc.)                              │
│  ~60 industries (Banks, Insurance, Pharmaceuticals, etc.)                 │
│  ~15 currencies (EUR, JPY, USD, GBP, etc.)                               │
│  Global Market                                                             │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Factor Table: exposure, return, impact, stddev (per style factor)    │
│  ├─→ Factor Sparklines: weekly exposure history per factor                │
│  ├─→ Factor Drill Modal: time series of exposure + return for one factor  │
│  ├─→ [POTENTIAL] Country attribution drill                                │
│  └─→ [POTENTIAL] Industry attribution drill                               │
│                                                                            │
│ PARSED:  ✅ Style factor rows (exposure, return, impact, dev, cum_impact) │
│ GAP:     ⚠️  Country/Industry/Currency rows NOT parsed into dashboard     │
│          The data IS there — parser just doesn't extract it yet           │
│ MISSING: ❌ % of Variance per individual country/industry/currency        │
│          (only in RiskM at aggregate level — requested in B1)             │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 4: Sector Weights (1 row/sector/strategy, 3009 cols)              │
│ Layout: horizontal — 19 cols/group × 158 groups                           │
│                                                                            │
│ FIELDS PER GROUP:                                                          │
│  Date, W, BenchW, AW, %S, %T, %T_Check,                                  │
│  OVER_WAvg, REV_WAvg, VAL_WAvg, QUAL_WA, MOM_WAvg, STAB_WAvg,          │
│  OVER_Avg, Val_Avg, Qual_Avg, MOM_Avg, REV_Avg, STAB_Avg                │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Exposures Tab: Sector table (W, BM, AW, %T, ranks)                 │
│  ├─→ Sector Drill Modal: holdings in sector, time series                  │
│  ├─→ Sector Sparklines: weekly weight history                             │
│  ├─→ Treemap: sector active weight visualization                         │
│  └─→ hist.sec[]: weekly sector weight time series                         │
│                                                                            │
│ PARSED:  ✅ n, p, b, a, mcr(%S), tr(%T), over, rev, val, qual            │
│ GAP:     ⚠️  Zero-weight sectors EXCLUDED from CSV (hides BM allocation)  │
│          ⚠️  BM weight doesn't sum to 100% (missing sectors)              │
│          Requested: include all 11 GICS L1 sectors always                  │
│ NOT PARSED: MOM_WAvg, STAB_WAvg, all _Avg variants (simple avg ranks)    │
│          Can add if dashboard needs them                                   │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 5: Industry (same layout as Sector Weights, 3009 cols)            │
│                                                                            │
│ Same fields: Date, W, BenchW, AW, %S, %T, %T_Check, 6 rank WAvgs        │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Exposures Tab: Industry table                                        │
│  └─→ Industry Drill Modal                                                 │
│                                                                            │
│ PARSED:  ✅ Same as Sector                                                │
│ GAP:     ⚠️  Zero-weight industries excluded (worse than sectors)         │
│          ⚠️  ISC BM only 59.5% — ~40% of benchmark hidden                │
│          ⚠️  GICS name changes mid-file (Retailing → Consumer Disc D&R)   │
│          Requested: all industries, unified naming                         │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 6: Region (same layout, 3009 cols)                                │
│ SECTION 7: Country (same layout, 3009 cols)                               │
│ SECTION 8: Group (same layout, 3009 cols) — RWOOD custom style groups     │
│                                                                            │
│ Same fields: Date, W, BenchW, AW, %S, %T, ranks                          │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Exposures Tab: Region/Country/Group tables                           │
│  ├─→ Country Choropleth Map                                               │
│  ├─→ Country Drill Modal                                                  │
│  └─→ hist.reg[]: weekly region weight time series                         │
│                                                                            │
│ PARSED:  ✅ All fields                                                     │
│ NOTE:    Region sums low for US-heavy strategies (expected — no US region) │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 9: Security (1 row/holding/strategy, 3799 cols)                   │
│ Layout: horizontal — 24 cols/group × 158 groups                           │
│                                                                            │
│ FIELDS PER GROUP:                                                          │
│  Date, Sector, Region, Country, Industry, Subgroup,                       │
│  W, BenchW, AW, %S, %T, %T_Check,                                        │
│  OVER, REV, VAL, QUAL, MOM, STAB (weighted avg ranks),                   │
│  OVER_avg, VAL_avg, QUAL_avg, MOM_avg, REV_avg, STAB_avg                │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Holdings Tab: full holdings table with sort/filter/search            │
│  ├─→ Stock Detail Modal: per-holding deep dive                            │
│  ├─→ Holdings in Sector/Country Drill: filtered by category               │
│  ├─→ MCR Scatter: %S vs %T bubble chart                                  │
│  ├─→ Quant Ranks: aggregated Q1-Q5 distribution                          │
│  └─→ Top 10 Risk Contributors bar chart                                   │
│                                                                            │
│ CATEGORY COLUMNS (per holding, per week):                                  │
│  Sector, Region, Country, Industry, Subgroup                              │
│  → These are the JOIN keys for rolling up to group tables                 │
│  → With B2 (factor exposures), we can compute:                            │
│     sum(holding_W × factor_exp) grouped by Sector/Country/Industry        │
│                                                                            │
│ PARSED:  ✅ All fields for latest weekly group                             │
│ GAP:     ⚠️  Only ~50% of holdings have data (others are sold positions)  │
│          ⚠️  PortChars says h=43, Security has 19 non-zero (IDM)          │
│          ⚠️  Weight sums to 50-95% instead of ~100%                       │
│          Requested: include all current holdings regardless of threshold   │
│ NOT IN FILE: ❌ Per-holding Axioma factor exposures (requested as B2)     │
│          This is the HIGHEST PRIORITY addition                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 10-13: Rank Tables (Overall, REV, QUAL, VAL)                      │
│ Layout: horizontal — same 19 cols/group × 158 groups                      │
│ One row per quintile (1-5) per strategy                                    │
│                                                                            │
│ FIELDS PER GROUP:                                                          │
│  Date, W(quintile weight), BenchW, AW, %S, %T, rank avgs                 │
│                                                                            │
│ MAPS TO:                                                                   │
│  ├─→ Quant Ranks section: Q1-Q5 weight distribution bar chart             │
│  └─→ Rank Drill: filter holdings by quintile                              │
│                                                                            │
│ PARSED:  ✅ As dict: {overall:[{q,w,bw,aw}], rev:[], val:[], qual:[]}     │
│ NOTE:    Dashboard rebuilds ranks from holdings (more accurate)            │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECTION 14: Section Headers (metadata rows between data sections)         │
│ These define column names for each section that follows                    │
│ Parser uses them to validate column positions                              │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                    DATA AGGREGATION PATHS
═══════════════════════════════════════════════════════════════════════════════

CURRENT (what we can compute today):

  Security holdings ──[group by sec]──→ Sector table (%T sum per sector)
  Security holdings ──[group by co]───→ Country table (%T sum per country)
  Security holdings ──[group by ind]──→ Industry table (%T sum per industry)
  Security holdings ──[group by subg]─→ Group table (%T sum per style group)

  These give us: "How much total TE comes from each sector/country?"
  ✅ WORKS but incomplete (Security section missing ~50% of holdings)


WITH B2 (per-holding factor exposures — REQUESTED):

  Security holdings ──[W × FactorExp, group by sec]──→ Sector factor tilts
  Security holdings ──[W × FactorExp, group by co]───→ Country factor tilts
  Security holdings ──[W × FactorExp, group by ind]──→ Industry factor tilts

  These give us: "How much of our Momentum tilt comes from Tech?"
  "Which country drives our Volatility exposure?"
  ❌ NOT POSSIBLE WITHOUT B2


ALREADY AVAILABLE (18 Style Snapshot — not yet parsed for groups):

  18 Style Snapshot ──[country rows]──→ Per-country: exposure, return, impact
  18 Style Snapshot ──[industry rows]─→ Per-industry: exposure, return, impact
  18 Style Snapshot ──[currency rows]─→ Per-currency: exposure, return, impact

  These give us: "What was France's active exposure and return attribution?"
  ✅ DATA EXISTS — parser needs to extract country/industry/currency rows
  ❌ Missing: % of Variance (risk contribution) — only in RiskM aggregate


═══════════════════════════════════════════════════════════════════════════════
                    HOLES SUMMARY
═══════════════════════════════════════════════════════════════════════════════

PARSER HOLES (fix ourselves):
  1. 18 Style Snapshot: country/industry/currency rows not extracted yet
  2. MCap displayed in millions — dashboard should show billions
  3. Selection Rate: compute h/bh
  4. GICS name mapping for legacy → current industry names
  5. MOM_WAvg, STAB_WAvg on group tables not parsed (available in CSV)

FACTSET HOLES (need from expanded run):
  1. Zero-weight sectors/industries excluded — need all rows always
  2. Security section incomplete — need all current holdings
  3. GICS name inconsistency — need retroactive unification
  4. Per-holding factor exposures (B2) — highest priority addition
  5. Individual % of Variance for country/industry/currency (B1)
  6. Additional characteristics (B4) — valuation, quality, yield metrics

UNFILLABLE HOLES (cannot compute, not in file, not requested):
  1. Per-holding factor TE contribution (% of total TE from each factor per holding)
     → Would need Axioma's marginal contribution to risk per factor per holding
     → This is extremely granular — probably not available in standard exports
```
