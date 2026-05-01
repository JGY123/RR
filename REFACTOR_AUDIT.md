# Dashboard v7 Refactor Audit

**Scope:** 30 tiles, 12 primary tables, ~13K LOC  
**Generated:** 2026-05-01

---

## 1. TABLE INVENTORY

| Tile ID | Renderer Function | Data Source | Table ID | Primary Columns | Features |
|---------|-------------------|-------------|----------|-----------------|----------|
| **cardSectors** | `rWt(_wSec(), 'sec', cs.hold)` | `cs.sectors` (latest) | `tbl-sec` | Sector, #, Port%, Bench%, Active, TE Contrib, Stock TE%, Factor TE%, O/R/V/Q, Factor TE breakdown, Trend | Sort, Sparkline window toggle (2/4/6/13 week), Hide/Show columns, Drill-down |
| **cardCountry** | `rCountryTable(_wCtry(), cs.hold)` | `cs.countries` (latest) | `tbl-ctry` | Country, #, Port%, Bench%, Active, TE Contrib, Stock TE%, Factor TE%, O/R/V/Q, Factor TE breakdown | Sort, Drill, Map/Chart/Table toggle, Region zoom (World/Eur/Asi/Amer), Top \|TE\| filter |
| **cardGroups** | `rGroupTable(_wGrp(), cs.hold)` | `cs.groups` (latest) | `tbl-grp` | Group, #, Port%, Bench%, Active, TE Contrib, Stock TE%, Factor TE%, O/R/V/Q, Factor TE breakdown | Sort, Drill, Chart/Table toggle |
| **cardRegions** | `rWt(_wReg(), 'reg', cs.hold)` | `cs.regions` (latest) | `tbl-reg` | Region, #, Port%, Bench%, Active, TE Contrib, Stock TE%, Factor TE%, Trend | Sort, Sparkline window toggle (2/4/6/13 week), Table/Chart toggle, Drill |
| **cardAttrib** | `rAttribTable()` | `cs.snap_attrib` | `tbl-attrib` | Factor, Exposure, σ (volatility), 1M, 3M, 6M, 1Y, Full (period impact) | Sort, Category filter (Country/Industry/Currency/All), Sort selector (Impact/Exposure/Dev), Click row for time series |
| **cardChars** | `rChr(_wChars())` | `cs.chars` (39 metrics grouped by CHAR_GROUP_ORDER) | `tbl-chr` | Metric, Portfolio, Benchmark, Diff | Sort, Group headers, Inverted-rank markers, History dots for per-metric time series |
| **cardRiskFacTbl** | Inline generator | `cs.factors` + risk decomp | `tbl-risk-fac` | Factor, Exposure, TE Contrib, TE %, Return impact, MCR | Sort, Drill on factor for time-series modal |
| **cardUnowned** | Inline from benchmark holdings | `cs.bench` - `cs.hold` | (dynamic) | Ticker, Name, Port%, Active%, %T | Sort, Drill on ticker |
| **cardRanks** | Inline from holdings bucketing | `cs.hold` (by quintile per rank type) | (dynamic) | Ticker, Name, Sector, Port%, Active%, %S, Total TE%, [6 Factor TEs], Peer rank | Sort, Drill on ticker, O/R/V/Q rank pills |
| **cardBenchOnlySec** | Inline from benchmark agg | `cs.bench` (sector aggregate) | `tbl-bo-sec` | Sector, # (missing count), Bench%, Implied Active% | (No sort/search — static summary) |
| **cardHoldings** | Inline from drill/sector detail | `cs.hold` filtered by sector/drill | (dynamic) | Ticker, Name, Sector, Port%, Active%, %S, Total TE%, [Factor TEs], [Sector rank via peer stats] | Sort, Drill on ticker, View toggle (Table/Cards) |
| **cardTop10** | Inline from top holdings query | `cs.hold` sorted desc by weight | (dynamic) | Ticker, Name, Port%, Active%, %T | (No interaction — static list, click to drill) |

---

## 2. TILE CHROME INVENTORY

| Tile ID | Title | ⓘ About | • Notes | 🔍 Zoom Reset | ↺ View Reset | × Hide | ⛶ FS | CSV | View Toggle | Other Controls |
|---------|-------|---------|---------|---------------|-------------|--------|-------|-----|-------------|-----------------|
| **cardThisWeek** | This Week KPIs | ✓ | ✓ | | | ✓ | ✓ | | | |
| **cardWeekOverWeek** | Week over Week | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ Move tabs | |
| **cardSectors** | Sector Active Weights | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | Table/Chart | Sparkline window (2/4/6/13) |
| **cardFacRisk** | Factor Risk Snapshot | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Bubble/Waterfall | Period selector |
| **cardFacButt** | Factor Performance | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Bubble/Waterfall | Period selector |
| **cardFacDetail** | Factor Detail | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | Primary/All | |
| **cardCountry** | Country Exposure | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | Map/Chart/Table | Region zoom, Top \|TE\| (All/10/20/30) |
| **cardGroups** | Redwood Groups | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | Chart/Table | |
| **cardRanks** | Spotlight [Rank Type] | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | O/R/V/Q rank pills |
| **cardTreemap** | Holdings Treemap | ✓ | ✓ | | ✓ | ✓ | ✓ | | Dimension (Sec/Co/Grp/Rank) | Size (Weight/TE/Count), Color (Active/Rank) |
| **cardUnowned** | Unowned Risk Contributors | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | |
| **cardAttrib** | Factor Attribution | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Table/Chart | Category filter, Sort selector |
| **cardRegions** | Region Active Weights | ✓ | ✓ | | ✓ | ✓ | | ✓ | Table/Chart | Sparkline window (2/4/6/13) |
| **cardCashHist** | Cash Weight Over Time | ✓ | ✓ | | | | | | | |
| **cardBenchOnlySec** | Benchmark-Only Sectors | ✓ | ✓ | | | | | ✓ | | |
| **cardRiskDecomp** | Risk Decomposition Tree | ✓ | ✓ | | ✓ | ✓ | ✓ | | | |
| **cardRiskHistTrends** | Historical Trends | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | Click card → drill modal |
| **cardTEStacked** | TE — Decomposition Over Time | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Range slider (zoom) |
| **cardBetaHist** | Beta History — Predicted | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Click for detail |
| **cardFacContribBars** | Factor Contributions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | TE/Exposure/Both | |
| **cardRiskFacTbl** | Factor Exposures (table) | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | Click row → time series modal |
| **cardRiskByDim** | Risk by Dimension | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Country/Currency/Industry | Click bar → drill modal |
| **cardFacHist** | Factor History | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Active Exp / Factor Return / Cumulative | Multi-select factors |
| **cardCorr** | Factor Correlation Matrix | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | Heatmap (red=anti, indigo=co-moving) |
| **cardWatchlist** | My Watchlist | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | Flag icon cycles Watch/Reduce/Add |
| **cardHoldRisk** | Holdings Risk Contribution (%) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Bubble/Bars | Click for drill |
| **cardHoldings** | Holdings Detail | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Table/Cards | Sector drill breadcrumb |
| **cardRankDist** | Ranking Distribution | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Quintile bars |
| **cardTop10** | Top 10 Holdings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | Click row → detail |
| **cardChars** | Characteristics (39 metrics) | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | Grouped by CHAR_GROUP_ORDER |

---

## Key Patterns for Refactor

1. **Renderer Functions:** `rWt()` is the workhorse — handles sectors, regions; `rCountryTable()`, `rGroupTable()`, `rChr()`, `rAttribTable()` are single-use. All read from `cs.*` data.

2. **Data Flow:** 
   - Latest holdings: `cs.hold` (portfolio) + `cs.bench` (benchmark)
   - Dimensions: `cs.sectors`, `cs.countries`, `cs.groups`, `cs.regions`, `cs.chars`, `cs.factors`, `cs.snap_attrib`
   - Historical: `cs.hist` (per-dimension per-week snapshots)

3. **Historical Mode:** Toggled via `_selectedWeek`. In hist mode, `getDimForWeek()` supplies per-week dimension data; `rWt()` / `rCountryTable()` / `rGroupTable()` skip holdings aggregation to avoid mixing latest-only risk data with historical weights.

4. **Chrome Consistency:**
   - About (ⓘ): All except two (cardCashHist, cardBenchOnlySec minimal)
   - Notes: All support `oncontextmenu="showNotePopup()"`
   - Reset View (↺): All tables + most charts; use `resetViewBtn()`
   - Reset Zoom (🔍): Factor/Risk charts only
   - Hide/Show (×): All major tiles
   - Full Screen (⛶): All except cardCashHist, cardBenchOnlySec, cardRegions
   - CSV: All tables + some charts
   - View Toggle: ~15 tiles (Table/Chart, Map/Chart, Bubble/Waterfall, etc.)

5. **Sort/Search:** Tables use `sortTbl('tbl-id', col#)` onclick; no built-in search (user relies on browser find).

6. **Drill Pattern:** Click row → `oDr()` / `oDrChar()` / `oDrAttrib()` → modal with time-series chart or detail.

---

**Migration Priorities:**
- Phase 1: Migrate `rWt()` (3 tables), `rCountryTable()`, `rGroupTable()` → component system with shared TE/ORVQ/Factor calc
- Phase 2: Migrate chart-based tiles (Factor Risk, Factor Perf, etc.) to Plotly/Recharts wrapper
- Phase 3: Drill modals and full-screen views
- Phase 4: Historical week mode & data flow refactoring

