# New FactSet CSV Format Specification (Format v2)

**Sample file:** `~/Downloads/risk_reports_s2_randomized.csv` (values randomized, layout exact)
**Dimensions:** 514 columns × 1,965 rows · 7 strategies (IDM, ACWIXUS, EM, ISC, SCG, ACWI, GSC)
**Key change:** `col[0]="Section"` explicitly identifies every row's section type — column-count detection is obsolete.

---

## Global Layout

Every row has:

| col | field | notes |
|-----|-------|-------|
| 0 | Section | Section type string (see below) or "Section" for header rows |
| 1 | ACCT | Strategy account code (IDM, ACWIXUS, EM, ISC, SCG, ACWI, GSC) |
| 2 | DATE | Numeric account identifier (not a date — ignore) |
| 3 | PortfolioCurCode | Base currency (USD) |
| 4 | Level | Float (was integer level in old format — do NOT use for row classification) |
| 5 | Level2 | Row identifier: sector name / ticker / "Data" / "@NA" / "[Cash]" / "[Unassigned]" |
| 6 | SecurityName | Company name (empty for aggregate rows) |
| 7+ | data | Section-specific columns (see below) |

**Row classification** (by Level2, not Level):
- `Level2 == "Data"` → portfolio summary/total row
- `Level2 == "[Cash]"` → cash aggregate row
- `Level2 == "@NA"` or `"[Unassigned]"` → unclassifiable aggregate
- `Level2.startswith("CASH_")` → currency cash row (e.g., CASH_USD) — **exclude from holdings**
- Otherwise → named sector/country/region/factor/holding row

**Section header rows** (`col[0] == "Section"`): appear once before each section block. Skip these rows — they define column labels but are not data.

**Date format:** All `Period Start Date` values use `M/D/YYYY` format (e.g., `1/30/2026`). Convert to `YYYYMMDD` for JSON output.

---

## Section Types (13 data sections + 1 header type)

Sections appear in this fixed order for every file:

1. **Sector Weights** — GICS L1 sector allocation
2. **RiskM** — Fundamental chars + factor exposures (snapshot)
3. **Portfolio Characteristics** — TE, Beta, Active Share, fundamentals (one row per period)
4. **Industry** — Industry-level allocation
5. **Region** — Geographic region allocation
6. **Country** — Country-level allocation
7. **Security** — Individual holdings (NEW: per-holding sector/region/country/industry)
8. **Group** — Custom style group allocation
9. **Overall** — OVER quintile distribution + top Q1 holdings
10. **REV** — REV_WAvg quintile distribution
11. **QUAL** — QUAL_WAvg quintile distribution
12. **VAL** — VAL_WAvg quintile distribution
13. **18 Style Snapshot** — Factor attribution (style + country + industry + currency)

---

## Section Details

### 1. Sector Weights, Industry, Region, Group, Overall, REV, QUAL, VAL
**"Standard" layout — 5 horizontal weekly groups**

Prefix: cols 0–6 (Section, ACCT, DATE, Currency, Level, Level2, SecurityName)

| Group | Date col | W col | BW col | AW col | … | STAB_Avg col |
|-------|----------|-------|--------|--------|---|-------------|
| 1 (oldest) | 7 | 8 | 9 | 10 | … | 25 |
| 2 | 26 | 27 | 28 | 29 | … | 44 |
| 3 | 45 | 46 | 47 | 48 | … | 63 |
| 4 | 64 | 65 | 66 | 67 | … | 82 |
| 5 (current) | 83 | 84 | 85 | 86 | … | 101 |

**Within each group (19 cols = 1 date + 18 metrics), relative offsets:**

| +0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 | +11 | +12 | +13 | +14 | +15 | +16 | +17 | +18 |
|----|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-----|-----|-----|
| Period Start Date | W | BW | AW | %S | %T | %T_Check* | OVER_WAvg | REV_WAvg | VAL_WAvg | QUAL_WAvg | MOM_WAvg | STAB_WAvg | OVER_Avg | Val_Avg | Qual_Avg | MOM_Avg | REV_Avg | STAB_Avg |

\* Country section uses `%T-filter` (col+6) instead of `%T_Check` — same position.

**"Data" row** (Level2="Data"): portfolio-level totals. `%T_Check` = Active Share at this level.

**Current snapshot** = Group 5 (date at col 83).

**Skip rows:** Level2 in `{Data, @NA, [Unassigned]}` for sector/region/industry/group display (include totals separately).

**`[Cash]` row in Sector Weights:** capture `W` from group 5 → `sum.cash`.

**Dates across all strategies:** 5 Fridays per month (e.g., 1/30, 2/6, 2/13, 2/20, 2/27 for Feb 2026).

---

### 2. Country
**Standard layout** but with `%T-filter` at group offset +6 (same column position as `%T_Check`). Treat identically to Sector Weights.

---

### 3. Security (Holdings)
**Extended layout — 5 groups, each 24 cols (1 date + 5 classification + 18 metrics)**

| Group | Date col | Sector col | W col | BW col | STAB_Avg col |
|-------|----------|-----------|-------|--------|-------------|
| 1 | 7 | 8 | 13 | 14 | 30 |
| 2 | 31 | 32 | 37 | 38 | 54 |
| 3 | 55 | 56 | 61 | 62 | 78 |
| 4 | 79 | 80 | 85 | 86 | 102 |
| 5 (current) | 103 | 104 | 109 | 110 | 126 |

**Within each group (24 cols), relative offsets:**

| +0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 | +11 | +12 | +13 | +14 | +15 | +16 | +17 | +18 | +19 | +20 | +21 | +22 | +23 |
|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Period Start Date | Redwood GICS Sector | Redwood Region1 | Redwood Country | Industry Rollup | RWOOD_SUBGROUP | W | BW | AW | %S | %T | %T_Check | OVER_WAvg | REV_WAvg | VAL_WAvg | QUAL_WAvg | MOM_WAvg | STAB_WAvg | OVER_Avg | REV_Avg | VAL_Avg | QUAL_Avg | MOM_Avg | STAB_Avg |

**Current snapshot** = Group 5 (date at col 103).

**Skip rows:** Level2.startswith("CASH_") — currency cash positions.

**Active Share** from Level2="Data" row → `%T_Check` at group 5 offset +11 (col 114).

**"Data" row** (Level2="Data"): Portfolio-level Active Share is in col[114] (group 5, offset +11).

---

### 4. Portfolio Characteristics (Vertical — one row per period)

**One row per week per strategy** (4 rows in sample, dates: 2/6, 2/13, 2/20, 2/27 — one week behind Sector Weights).

| col | header | use |
|-----|--------|-----|
| 7 | Period Start Date:P | Week date (Portfolio) |
| 8 | Portfolio:P | (group label — skip) |
| 9 | Axioma...:P | (model label — skip) |
| 10 | Predicted Tracking Error (Std Dev):P | `sum.te` |
| 11 | Axioma- Predicted Beta to Benchmark:P | `sum.beta` |
| 12 | # of Securities:P | `sum.h` |
| 13 | Port. Ending Active Share:P | `sum.as` |
| 14 | Market Capitalization:P | `sum.mcap` |
| 15 | Axioma...:P | (model label — skip) |
| 16 | Axioma- Historical Beta:P | (skip) |
| 17 | Port. MPT Beta:P | (skip) |
| 18 | EPS Growth - Hist. 3Yr:P | `sum.epsg` |
| 19 | EPS Growth - Est. 3-5Yr:P | (skip or store as epsg_fwd) |
| 20 | 3M EPS Revisions - FY1:P | (skip or store as eps3m) |
| 21 | 6M EPS Revisions - FY1:P | (skip or store as eps6m) |
| 22 | FCF Yield - NTM:P | `sum.fcfy` |
| 23 | Dividend Yield - Annual:P | `sum.divy` |
| 24 | ROE - NTM:P | `sum.roe` |
| 25 | Operating Margin - NTM:P | `sum.opmgn` |
| 26 | Period Start Date:B | Week date (Benchmark) |
| 27 | Portfolio:B | (group label — skip) |
| 28 | Axioma...:B | (model label — skip) |
| 29 | Predicted Tracking Error (Std Dev):B | (skip — benchmark TE not used) |
| 30 | Axioma- Predicted Beta to Benchmark:B | (skip) |
| 31 | # of Securities:B | `sum.bh` |
| 32 | Port. Ending Active Share:B | (skip) |
| 33 | Market Capitalization:B | `sum.bmcap` |
| 34 | Axioma...:B | (skip) |
| 35 | Axioma- Historical Beta:B | (skip) |
| 36 | Port. MPT Beta:B | (skip) |
| 37 | EPS Growth - Hist. 3Yr:B | `chars` benchmark EPS Growth |
| 38 | EPS Growth - Est. 3-5Yr:B | (skip) |
| 39 | 3M EPS Revisions - FY1:B | (skip) |
| 40 | 6M EPS Revisions - FY1:B | (skip) |
| 41 | FCF Yield - NTM:B | `chars` benchmark FCF Yield |
| 42 | Dividend Yield - Annual:B | `chars` benchmark Dividend Yield |
| 43 | ROE - NTM:B | `chars` benchmark ROE |
| 44 | Operating Margin - NTM:B | `chars` benchmark Op Margin |

**Level2 filter:** Only rows where `Level2 == "Data"`.

**Current snapshot** = last row (highest date). **hist.summary** = all rows sorted by date.

---

### 5. RiskM (Fundamental chars + Risk + Factor Exposures, single row per period)

**One row per week per strategy** (4 rows in sample, Level2="Data").

| col | field |
|-----|-------|
| 7 | Period Start Date |
| 8 | "Fundamental Characteristics" (label — skip) |
| 9 | Price/Earnings → `sum.pe` |
| 10 | Price/Book → `sum.pb` |
| 11 | BMK Price/Earnings → `sum.bpe` ← **NEW** (was missing in old format) |
| 12 | BMK Price/Book → `sum.bpb` ← **NEW** |
| 13 | "Risk Characteristics" (label — skip) |
| 14 | "Axioma..." (model label — skip) |
| 15 | Total Risk (%) → `sum.total_risk` |
| 16 | Benchmark Risk (%) → `sum.bm_risk` |
| 17 | Predicted Beta → (also in Portfolio Characteristics — use Portfolio Characteristics) |
| 18 | Risk (%) → (same as Total Risk?) |
| 19 | "Axioma..." (model label — skip) |
| 20 | % Asset Specific Risk → `sum.pct_specific` |
| 21 | % Factor Risk → `sum.pct_factor` |
| 22 | % of Variance → (skip) |
| 23–39 | Portfolio factor exposures (17 factors, see table below) |
| 40 | "Exposure" (label — skip) |
| 41 | "Axioma..." (label — skip) |
| 42 | "Active Exposure" (label — skip) |
| 43–59 | Active factor exposures (same 17 factors) |

**Factor order** (cols 23–39 = portfolio, cols 43–59 = active):

| Offset from 23 | Factor | Old name |
|----------------|--------|---------|
| 0 | Dividend Yield | Dividend Yield |
| 1 | Earnings Yield | Earnings Yield |
| 2 | Exchange Rate Sensitivity | FX Sensitivity (Exchange Rate) |
| 3 | Growth | Growth |
| 4 | Leverage | Leverage |
| 5 | Liquidity | Liquidity |
| 6 | Market Sensitivity | Market Sensitivity |
| 7 | Medium-Term Momentum | Momentum (Medium-Term) |
| 8 | Profitability | Profitability |
| 9 | Size | Size |
| 10 | Value | Value |
| 11 | Volatility | Volatility |
| 12 | Market | Market |
| 13 | Local | (new — not in old 16-factor list, skip) |
| 14 | Industry | Industry |
| 15 | Country | Country |
| 16 | Currency | Currency |

**Current snapshot** = last row (highest date).

**Benchmark exposure** = portfolio_exposure − active_exposure.

---

### 6. 18 Style Snapshot (Factor Attribution)

**One row per factor** (style, country, industry, currency dimensions). Level2 = factor/dimension name.

**5 periods per row** (periods 1–4 = weekly, period 5 = full-month cumulative):

| Period | Date Start col | Date End col | Avg Active Exp | Compounded Return | Compounded Impact | Factor StdDev | Cumulative Impact |
|--------|---------------|-------------|----------------|------------------|--------------------|--------------|-----------------|
| 1 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
| 2 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
| 3 | 21 | 22 | 23 | 24 | 25 | 26 | 27 |
| 4 | 28 | 29 | 30 | 31 | 32 | 33 | 34 |
| 5 (cumul) | 35 | 36 | 37 | 38 | 39 | 40 | 41 |

**Style factors** (match to RiskM factors): Growth, Medium-Term Momentum, Volatility, Market Sensitivity, Liquidity, Exchange Rate Sensitivity, Profitability, Currency, Size, Market, Industry, Country, Leverage, Earnings Yield, Value, Dividend Yield.

**Use period 5** (cumulative) for `factor.ret`, `factor.imp`, `factor.dev`, `factor.cimp`.

**hist.fac exposure** per week: use period 1–4 `avg_active_exp` + factor exposure from RiskM for the current snapshot.

---

## Output JSON Mapping

```
Section               → JSON key(s)
──────────────────────────────────────────────────────────
Sector Weights        → strategy.sectors[]  +  strategy.hist.sec{}
Security (grp 5)      → strategy.hold[]      (with sec, reg, co, ind, subg NEW)
Portfolio Chars       → strategy.sum (te, as, beta, h, bh, mcap, epsg, fcfy, divy, roe, opmgn)
                        + strategy.hist.summary[]
                        + strategy.chars[]  (now with full benchmark data!)
RiskM                 → strategy.sum (pe, pb, bpe, bpb, total_risk, bm_risk, pct_specific, pct_factor)
                        + strategy.factors[] (exposure: e, bm, a)
Country               → strategy.countries[]
Region                → strategy.regions[]
Industry              → strategy.industries[]  ← NEW section
Group                 → strategy.groups[]
Overall               → strategy.ranks.overall{}  ← NEW (quintile distributions)
REV/VAL/QUAL          → strategy.ranks.rev/val/qual{}  ← NEW
18 Style Snapshot     → strategy.factors[] (attribution: ret, imp, dev, cimp)
                        + strategy.hist.fac{}  (per-period active exposure)
```

## Key Differences from Old Format

| Old | New |
|-----|-----|
| Column-count based routing (96/101/42/9/31) | Section name in col[0] |
| Level=1/2/3 integer hierarchy | Level = float (don't use for routing) |
| Date labels inferred from report date (5 Fridays back) | Explicit "Period Start Date" per group column |
| No per-holding sector/region/country | Security section: Redwood GICS Sector, Redwood Region1, Redwood Country, Industry Rollup, RWOOD_SUBGROUP per group |
| BMK P/E and P/B missing | RiskM col[11]=BMK P/E, col[12]=BMK P/B |
| Only partial benchmark characteristics | Portfolio Characteristics has full P+B columns |
| Security names with commas require repair | CSV properly quoted (no repair needed) |
| 16 factors in separate 9-col section | 17 factors in RiskM (add "Local") + all dimensions in 18 Style Snapshot |
| "Overall Rank" extra column in 101-col | No extra column — clean 18-metric layout |
