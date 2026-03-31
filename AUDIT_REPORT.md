# RR Dashboard — Deep Audit Report
**Generated:** 2026-03-26
**Dashboard:** dashboard_v7.html (4265 lines)
**Test data:** risk_reports_s2_randomized.csv → /tmp/rr_parsed.json
**Auditor:** Risk Reports Specialist agent

---

## A. Every Table in the Dashboard

### A1. Holdings Table (`rHold()` / `renderHoldTab()`)
**Tab:** Holdings
**Trigger:** `rHold()` → `renderHoldRows()`
**Columns (rendered):**
| # | Column | Source Field | Sortable | Notes |
|---|--------|-------------|----------|-------|
| 1 | Ticker | `h.t` | Yes | Sort button in header |
| 2 | Name | `h.n` | No | Truncated at ~24 chars |
| 3 | Port Wt | `h.p` (mapped ← `h.w`) | Yes | % with 2 dp |
| 4 | BM Wt | `h.b` (mapped ← `h.bw`) | Yes | % with 2 dp |
| 5 | Active Wt | `h.a` (mapped ← `h.aw`) | Yes | % with 2 dp |
| 6 | %T | `h.tr` (mapped ← `h.pct_t`) | Yes | % TE contribution bar |
| 7 | %S | `h.mcr` (mapped ← `h.pct_s`) | Yes | Stock-specific TE |
| 8 | Rank | `h.r` (mapped ← `h.over`) | Yes | Pill + R·V·Q sub-line |

**Sort:** Functional for all listed columns via click on column header buttons.
**Filter:** Sector dropdown, rank dropdown (Q1–Q5), search box (ticker/name substring).
**Pagination:** 25 rows/page, prev/next buttons; page info "Showing X–Y of Z".
**%T bar:** Inline green bar, width = `Math.min(h.tr*8, 100)` — calibrated for ~12% max %T.
**Rank display:** `renderHoldRows()` generates `Q${h.r}` pill; sub-line shows `R${rev} V${val} Q${qual}` where rev=`h.rev`, val=`h.val`, qual=`h.qual`.
**Broken:**
- Sub-label for "R" should be "Revision" not "Revenue" (only matters in tooltips/modal, not inline label).
- `h.r` sourced from `h.over` (Overall Quintile) — correct per CLAUDE.md.
- If `h.over` is null/undefined, pill shows `Q` with no number.

---

### A2. Sector Weights Table (`rWt(data, 'sec', hold)`)
**Tab:** Exposures
**Columns:** Sector | Port % | BM % | Active % | TE Contrib
**Source fields:** `s.n, s.p, s.b, s.a` for weights; TE Contrib computed from holdings sum.
**TE Contrib computation:** `hold.filter(h=>h.sec===s.n).reduce((acc,h)=>acc+(h.mcr||0), 0)` — **BUG: uses `h.mcr` (%S stock-specific) instead of `h.tr` (%T actual TE contrib)**. The column is labeled "TE Contrib" but sums stock-specific risk (%S), not tracking error contribution (%T).
**Sortable:** No sort buttons.
**Color coding:** Active weight cell colored green (OW) or red (UW); TE Contrib bar in orange.
**Broken:** TE Contrib column values are wrong (uses %S not %T).

---

### A3. Region Weights Table (`rWt(data, 'reg', hold)`)
**Tab:** Exposures
**Columns:** Region | Port % | BM % | Active % | (no TE Contrib for regions)
**Source fields:** `r.n, r.p, r.b, r.a`
**Region disclaimer:** Shown when coverage < 50% (sum of region port weights).
**Sortable:** No.
**Broken:** None identified beyond the shared rWt() path issues.

---

### A4. Country Weights Table (`rWt(data, 'co', hold)` or similar)
**Tab:** Exposures
**Columns:** Country | Port % | BM % | Active %
**Source fields:** `c.n, c.p, c.b, c.a` from `strat.countries`
**Sortable:** No.
**Broken:** None identified.

---

### A5. Factor Detail Table (`rFac(factors, hold)`)
**Tab:** Exposures
**Columns:** Factor | Portfolio | Benchmark | Active | Ret | Impact | TE Contrib
**Source fields:** `f.n, f.e, f.bm, f.a, f.ret, f.imp, f.c`
**Primary factors (FAC_PRIMARY):** Always visible — Value, Quality, Growth, Momentum, Volatility, Leverage, Liquidity, Size, Profitability.
**Secondary factors:** Collapsible via "Show More" toggle.
**TE Contrib (`f.c`):** NOT in Python parser output. Dashboard uses proxy: `Math.abs(f.a) * (f.dev||0)` where `f.dev` is a volatility/dispersion measure. This is an approximation, not the real TE contribution.
**Profitability:** Green-tinted row; alert threshold reversed (high exposure = good).
**Sparklines:** Inline SVGs rendered from `hist.fac[name]` — only 1 entry in test file → single-dot sparkline renders as "—".
**Broken:**
- `f.c` proxy computation is not real TE contribution.
- FAC_PRIMARY set in dashboard uses both `'Momentum (Medium-Term)'` and `'Momentum'` — only one will match Python parser's factor name.

---

### A6. Factor Attribution Table/Waterfall (`rAttr()`)
**Tab:** Exposures
**Columns/Data:** Factor-level attribution bars in a waterfall chart
**Source:** `genAttrib()` — **100% SYNTHETIC** random data. NOT sourced from the parsed CSV.
**Broken:** All values fabricated. The real Brinson/factor attribution data exists in the CSV (factret/factimp columns in factors section) but the waterfall uses mock data instead.

---

### A7. Factor Exposures Table (Risk tab, `rRisk()`)
**Tab:** Risk
**Columns:** Factor | Exposure | BM | Active | Contrib
**Source fields:** Same `strat.factors` array
**Toggle:** "By Factor" / "By Group" toggle above the table changes grouping display.
**Sortable:** No.
**Broken:** Same TE Contrib proxy issue as A5.

---

### A8. Quant Ranks Table (`rRnk()`)
**Tab:** Exposures
**Expected columns:** Quintile | Port Wt | BM Wt | Active Wt
**Source:** `strat.ranks` array — expected format `{r, l, ct, p, a}[]`
**Actual from Python parser:** `{overall:[{q,w,bw,aw}], rev:[...], qual:[...], val:[...]}` nested dict
**Result:** `rRnk()` receives `null` or empty → renders "No rank data available"
**Broken:** Complete mismatch between parser output format and dashboard expectation. The ranks section is non-functional for Python-parsed JSON.

---

### A9. Characteristics Table / Cards (`rChars()` or inline in `rExp()`)
**Tab:** Exposures
**Fields shown:** P/E, P/B, ROE, FCF Yield, Div Yield, EPS Growth, Op Margin, MCap
**Source:** `strat.sum.pe, strat.sum.pb, strat.sum.roe, strat.sum.fcfy, strat.sum.divy, strat.sum.epsg, strat.sum.opmgn, strat.sum.mcap`
**BM comparison:** `strat.sum.bpe, strat.sum.bpb` for benchmark P/E and P/B
**Broken:** If `bpe`/`bpb` are null (pending from FactSet per CLAUDE.md), BM comparison columns show null/—.

---

### A10. MCR Table (`rMCR()` or inline in `rExp()`)
**Tab:** Exposures
**Columns:** Ticker | MCR % | %S | %T
**Source:** Top holdings sorted by `h.mcr` (marginal contribution to risk / stock-specific)
**Shows:** Top 10 risk contributors
**Broken:** If `pct_s`/`pct_t` are null from parser, cells show null.

---

### A11. Stress Scenarios Table
**Tab:** Exposures
**Source:** `strat.stress` or `genStress()` — using synthetic data
**Columns:** Scenario | Portfolio Impact | BM Impact | Active
**Broken:** Synthetic data. Not sourced from FactSet CSV.

---

### A12. Factor Correlation Table — Exposures Tab (`rFCorr()`)
**Tab:** Exposures
**Source:** `genFCorr()` — **100% SYNTHETIC** random correlation matrix
**Broken:** All values fabricated. The Risk tab correlation matrix (`rUpdateCorr()`) computes real Pearson correlations from `hist.fac` data; this Exposures tab version does not.

---

### A13. Correlation Matrix — Risk Tab (`rUpdateCorr()`)
**Tab:** Risk
**Source:** Computed from `hist.fac[name]` arrays using real Pearson correlation formula
**Rendering:** Interactive Plotly heatmap
**Broken:** With only 1 week of `hist.fac` data in test file, correlations are undefined (division by zero in std dev). With 3+ years of data this would work correctly.

---

### A14. Holdings in Sector/Region Drill (`oDr()`)
**Tab:** Modal — triggered from Sector or Region weight table row click
**Columns:** Ticker | Name | Port Wt | Active Wt | Rank | %T
**Source:** `hold.filter(h=>h.sec===name)` or region equivalent
**Rank column:** Shows `R${h.r}` — uses Overall quintile, not the sub-ranks
**Broken:**
- `teContrib` computation uses `h.mcr` (%S) instead of `h.tr` (%T) — same bug as A2.
- Rank shows `R${h.r||'--'}` — if `h.r` is null, shows `R--`.

---

### A15. Groups / Industry Table
**Tab:** Exposures
**Source:** `strat.groups` or `strat.industries`
**Columns:** Group/Industry | Port % | BM % | Active %
**Broken:** None identified beyond data availability.

---

## B. Every Popup/Modal

### B1. Stock Detail Modal (`oSt(ticker)`)
**Trigger:** Click on holding row in Holdings tab
**Expected content:**
- Ticker, Name, Sector, Country
- 6 quant score cards: Overall, Revision, Value, Quality, Momentum, Stability
- Weight fields: Port Wt, BM Wt, Active Wt
- Risk fields: %T (TE contrib), %S (stock-specific)
- Quintile ranks displayed
**Actual content:** 6 cards labeled "Overall, **Revenue**, Value, Quality, Momentum, Stability"
**Broken:**
- **"Revenue" should be "Revision"** — label bug in `oSt()` HTML template, line showing `rev` score.
- If `h.over`, `h.rev`, `h.val`, `h.qual`, `h.mom`, `h.stab` are null, cards show "—".
- `h.mcr` and `h.tr` show correct values when parser populates `pct_s` and `pct_t` correctly.

---

### B2. Sector Drill Modal (`oDr('sec', name)`)
**Trigger:** Click on sector row in Sector Weights table
**Expected content:**
- Sector name header
- Holdings list within sector (ticker, weight, active wt, rank, %T)
- 4 quant score averages (OVER, REV, VAL, QUAL) shown as cards
- Sector attribution history chart
- Factor exposure breakdown for this sector
**Actual content:** Shows 6 score cards including MOM and STAB
**Broken:**
- **Shows 6 score cards (including MOM and STAB) instead of 4** — PM preference is OVER/REV/VAL/QUAL only.
- TE Contrib in holdings list uses `h.mcr` (%S) instead of `h.tr` (%T).
- Attribution history uses synthetic data if `hist.sec` is empty/single-point.

---

### B3. Region Drill Modal (`oDr('reg', name)`)
**Trigger:** Click on region row
**Same issues as B2** but for regions. Rank scores averaged across regional holdings.

---

### B4. Factor Drill Modal — Exposures Tab (`oDrF(name)`)
**Trigger:** Click on factor name in Factor Detail table (Exposures tab)
**Expected content:**
- Factor name, exposure vs BM, active exposure
- Holdings contributing most to factor exposure (top 10)
- Factor exposure time series chart
**Broken:**
- Time series uses `hist.fac[name]` — with single week, chart shows one point.
- Holdings breakdown requires per-holding factor loadings which are not in the CSV/parser output.

---

### B5. Factor Risk Drill Modal — Risk Tab (`oDrFRisk(name)`)
**Trigger:** Click on factor in Risk tab factor table
**Similar to B4** — same single-point sparkline issue with limited history.

---

### B6. Factor Risk Breakdown Modal (`oDrFacRiskBreak()`)
**Trigger:** Click on "Factor Risk" card in Risk tab summary cards
**Expected content:** Top 5 factors by |TE contribution|
**Source:** `strat.factors` sorted by `Math.abs(f.c)`
**Broken:** `f.c` is the proxy value, not real TE contribution. Top 5 ranking may be inaccurate.

---

### B7. Idiosyncratic Risk Modal (`oDrMetric('idio')`)
**Trigger:** Click on "Idio Risk" card in Exposures tab
**Expected content:** Top 5 holdings by idiosyncratic risk contribution
**Columns:** Ticker | Name | %S | Rank
**Broken:**
- Rank displays as `Q${h.r||'--'}` → shows `Q--` when `h.r` is null/undefined
- Should show quintile rank as just the number or a colored pill, not `Q--`

---

### B8. Metric Time Series Modal (`oDrMetric(metric)`)
**Trigger:** Click on summary card (TE, Beta, Active Share, Holdings, SR, Cash)
**Metrics:** `'te'`, `'beta'`, `'as'`, `'h'`, `'sr'`, `'cash'`
**Source:** `strat.hist.summary` array (called `hist.sum` in the render code)
**Date parsing issue:** `new Date('20260206')` = **Invalid Date** in JavaScript
**Broken:**
- **CRITICAL: X-axis labels show "Invalid Date"** for all data points when JSON comes from Python parser (YYYYMMDD format without dashes).
- The in-browser JS parser generates ISO format dates (`2026-02-06`) which parse correctly.
- `hist.summary` `h` field is a float (e.g., 4.593) in Python parser — should be an integer count. Holdings count shown as "4.6" instead of "5".

---

### B9. Correlation Scatter Drill (`oDrCorr(f1, f2)`)
**Trigger:** Click on cell in Exposures tab Factor Correlation table
**Source:** Synthetic `genScatter()` data — NOT real factor exposure scatter
**Broken:** All plotted points are fabricated. Real scatter would require per-holding factor loadings (not available in current parser output).

---

### B10. Cross-Strategy Comparison Modal (`openComp()`)
**Trigger:** "Compare" button (if present) or keyboard shortcut
**Content:** All 7 strategies' TE, AS, Beta, Holdings side by side
**Source:** Each strategy's `sum` fields
**Broken:** None identified — uses summary data which is fully populated.

---

### B11. Factor Risk Budget Modal (`oDrRiskBudget()`)
**Trigger:** Click on Risk Budget section
**Source:** `strat.factors` — shows allocation of risk budget by factor
**Broken:** Same `f.c` proxy issue — values are approximate.

---

### B12. Historical Trend Drills (`oDrMetric` called from sparklines)
**Trigger:** Click on mini sparkline charts in Risk tab
**Same as B8** — YYYYMMDD date parsing issue applies here too.

---

## C. Spotlight Ranks (R·V·Q) — Where They Should Appear vs. Where They Do

### C1. Definitions (from CLAUDE.md / specialist agent)
| Label | Field | Python Parser | V1 Name | Scale |
|-------|-------|--------------|---------|-------|
| OVER | `h.over` ← `h.r` | populated | Overall quintile | 1=best, 5=worst |
| REV | `h.rev` | populated | Revision quintile | 1=best, 5=worst |
| VAL | `h.val` | populated | Value quintile | 1=best, 5=worst |
| QUAL | `h.qual` | populated | Quality quintile | 1=best, 5=worst |
| MOM | `h.mom` | populated | Momentum quintile | 1=best, 5=worst |
| STAB | `h.stab` | populated | Stability quintile | 1=best, 5=worst |

**PM preference:** Display OVER, REV, VAL, QUAL primary. MOM and STAB are secondary.

### C2. Where R·V·Q appears correctly
| Location | What Shows | Status |
|----------|-----------|--------|
| Holdings table row | `Q{over}` pill + `R{rev} V{val} Q{qual}` sub-line | ✅ Correct labels, correct fields |
| Holdings sort buttons | Sort by R/V/Q rank | ✅ Functional |
| Holdings filter dropdown | Filter Q1–Q5 by Overall rank | ✅ Functional |

### C3. Where R·V·Q appears incorrectly or is missing
| Location | What Shows | Should Show | Status |
|----------|-----------|-------------|--------|
| Stock detail modal (B1) | "Revenue, Value, Quality, Momentum, Stability" labels | "Revision, Value, Quality, Momentum, Stability" | ❌ Label bug |
| Sector drill modal (B2) | 6 cards: OVER, REV, VAL, QUAL, MOM, STAB | 4 cards: OVER, REV, VAL, QUAL | ❌ Extra MOM/STAB |
| Region drill modal (B3) | Same as B2 | Same correction needed | ❌ Extra MOM/STAB |
| Idio Risk modal (B7) | `Q${h.r\|\|'--'}` | Quintile pill or just number | ❌ Shows `Q--` for nulls |
| Sector drill holdings list | `R${h.r}` (Overall only) | Should show R·V·Q sub-ranks | ⚠️ Partial — only overall rank |
| Quant Ranks table (A8) | "No rank data available" | Distribution table by quintile | ❌ Parser format mismatch |

### C4. Rank Data Flow Bug
The `ranks` section in the Python parser output is:
```json
{"overall": [{"q":1,"w":32.1,"bw":20.4,"aw":11.7}, ...], "rev": [...], "val": [...], "qual": [...]}
```
The dashboard `rRnk()` function expects:
```json
[{"r":1,"l":"Quintile 1","ct":12,"p":32.1,"a":11.7}, ...]
```
These formats are completely incompatible. The Quant Ranks distribution table never renders real data.

---

## D. Factor Display — Every Location, Render Status, Toggle Working

### D1. Factor Detail Table (Exposures Tab) — `rFac()`
**Location:** Middle section of Exposures tab
**Factors shown:** 16 Axioma risk factors
**Primary always visible:** Value, Quality, Growth, Momentum, Volatility, Leverage, Liquidity, Size, Profitability
**Secondary collapsible:** Remaining 7 factors via "Show More" button
**Toggle:** ✅ Working — "Show More" / "Show Less" toggle functional
**Columns:** Factor | Portfolio | BM | Active | Ret | Impact | TE Contrib
**TE Contrib column:** Uses proxy `|a| × dev` — NOT real TE contribution
**Sparklines:** Inline SVG from `hist.fac` — single point with test data → renders as "—"
**Profitability row:** Green-tinted, reversed alert logic ✅
**FAC_PRIMARY mismatch:** Dashboard checks for `'Momentum (Medium-Term)'` in FAC_PRIMARY set but Python parser may output `'Momentum'` — one factor always in "secondary" section incorrectly

### D2. Factor Butterfly Chart (Exposures Tab)
**Location:** Above Factor Detail table
**Source:** `strat.factors` — portfolio vs BM exposure bars
**Toggle:** None — always shown
**Status:** ✅ Renders if factors array is populated

### D3. Factor Attribution Waterfall (Exposures Tab) — `rAttr()`
**Location:** Below Factor Detail table (renders into `facAttribArea`)
**Source:** `genAttrib()` — **SYNTHETIC DATA**
**Status:** ❌ Shows fabricated values. Not connected to real CSV attribution data.

### D4. Factor Exposures Table (Risk Tab) — `rRisk()`
**Location:** Risk tab, below TE history chart
**Toggle:** "By Factor" / "By Group" toggle
**By Factor:** Lists all factors with exposure/BM/active
**By Group:** Groups factors into categories (Style, Risk, Quality, etc.)
**Toggle:** ✅ Working
**Status:** Renders correctly when `strat.factors` is populated

### D5. Factor Exposure History (Risk Tab)
**Location:** Risk tab, time series chart for selected factors
**Source:** `hist.fac[name]` arrays — YYYYMMDD dates
**Checkbox selection:** Individual factor checkboxes control which factors plot
**Toggle checkboxes:** ✅ Working
**Date issue:** Same YYYYMMDD parsing problem as B8 — x-axis shows "Invalid Date"
**Single-point issue:** With 1 week of `hist.fac` data, all series are single dots

### D6. Factor Correlation Table (Exposures Tab) — `rFCorr()`
**Location:** Bottom of Exposures tab
**Source:** `genFCorr()` — **SYNTHETIC DATA**, random values seeded by strategy name
**Status:** ❌ All values fabricated

### D7. Factor Correlation Matrix (Risk Tab) — `rUpdateCorr()`
**Location:** Risk tab, bottom section
**Source:** Real Pearson correlation from `hist.fac` — ✅ Real computation
**Status:** ⚠️ Correct algorithm but requires 3+ weeks of history; single-week test = NaN/undefined
**Rendering:** Interactive Plotly heatmap — ✅ Correct tool

### D8. Factor Risk Contribution Cards (Risk Tab)
**Location:** 5 summary cards at top of Risk tab
**Source:** `strat.sum.total_risk, strat.sum.bm_risk, strat.sum.pct_specific, strat.sum.pct_factor`
**Status:** ✅ Renders if sum fields populated

### D9. Factor Contribution Bars (Risk Tab)
**Location:** Stacked bar chart below Risk summary cards
**Source:** `strat.factors` contributions
**Toggle:** "Absolute" / "Relative" view toggle
**Toggle:** ✅ Working

---

## E. Cross-Cutting Patterns

### E1. Date Formatting — CRITICAL
**Pattern:** Python parser outputs YYYYMMDD (e.g., `'20260206'`). JS parser outputs ISO (e.g., `'2026-02-06'`).
**Impact locations:**
- Week selector header (`‹ date ›`) — calls `new Date(d)` on YYYYMMDD → Invalid Date
- `oDrMetric()` modal x-axis labels — same bug
- `hist.fac` / `hist.sec` date labels in all time series drills
- `hist.summary` week selector dropdown options
**Root cause:** `new Date('20260206')` returns Invalid Date in JavaScript. `new Date('2026-02-06')` is valid.
**Fix pattern:** Add a `parseDate(d)` helper: `d.length===8 ? new Date(d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6)) : new Date(d)`

### E2. Sort Buttons
**Where implemented:** Holdings table (all columns), MCR table
**Where missing:** Sector table, Region table, Country table, Factor Detail table, Quant Ranks table
**Pattern:** Only the Holdings tab has interactive sort. All other tables are display-only in insertion order.

### E3. Precision / Number Formatting
**Percentages:** Most show 2 decimal places (e.g., "32.14%") — consistent
**Holdings count:** `hist.summary[].h` is a float from Python parser (e.g., 4.593) — displays as "4.6" in week selector. Should be integer: `Math.round(h)`.
**Active Share:** `sum.as` = 9.27 in test data — suspiciously low (typical range 40–100%). Either the parser is outputting active weight instead of active share, or the test data is anomalous.

### E4. Color Coding
**OW (overweight active):** Green
**UW (underweight active):** Red
**Q1 rank:** Gold/yellow pill
**Q5 rank:** Red pill
**Q2-Q4:** Gradient
**Profitability factor:** Green-tinted row (reversed logic)
**Consistent:** Yes, the color coding is consistent across tables and modals.

### E5. Hover Tooltips
**Holdings table:** Hover shows full company name (truncation workaround)
**Factor table:** Hover shows factor description (from FAC_DESCRIPTIONS map)
**Charts:** Plotly default tooltips — adequate
**Missing:** No hover tooltip on rank pills explaining the scale (1=best, 5=worst).

### E6. Empty State Handling
**"No rank data available":** Shown when `ranks` is null/empty — triggered by parser format mismatch
**"No unowned risk data":** Always shown — `unowned` field not populated by Python parser
**"No attribution data":** NOT shown — synthetic data fills this, masking the real issue
**Factor sparklines:** Shows "—" when single data point — correct empty state behavior

### E7. Strategy Selector
**Pattern:** Dropdown in header; calling `upd()` re-renders all tabs for selected strategy
**Status:** ✅ Functional
**Tab count badges:** Holdings count and factor count updated on strategy change

### E8. Historical Week Selector
**Pattern:** `‹ date ›` in header; calls `setWeek(d)` → `upd()`
**Source:** `strat.available_dates` array (YYYYMMDD from Python parser)
**Bug:** Displayed dates are "Invalid Date" (YYYYMMDD parsing failure)
**JS parser limitation:** Does not populate `available_dates` → selector disabled/empty for direct CSV uploads

### E9. Range Buttons (3M|6M|1Y|3Y|All)
**Location:** Time series charts in Risk tab and metric modals
**Pattern:** Filters `hist.summary` array by date range
**Status:** ✅ Functional in principle
**But:** With only 5 weeks of test data, all range buttons show the same 5 points.

---

## F. What's Broken Right Now

### F1. CRITICAL — Week Selector Shows "Invalid Date"
**Symptom:** Week selector header (`‹ date ›`) shows "Invalid Date ‹ Invalid Date ›"
**Root cause:** `new Date('20260206')` = Invalid Date in JavaScript
**Affected:** All time series drills, metric modals (x-axis), week selector dropdown
**Scope:** Only affects Python parser JSON; JS parser (in-browser CSV upload) uses ISO dates
**Fix:** One-line date normalizer before all `new Date()` calls on history dates

### F2. CRITICAL — Quant Ranks Table Broken (Parser Format Mismatch)
**Symptom:** "No rank data available" shown in Quant Ranks section
**Root cause:** Python parser outputs `{overall:[{q,w,bw,aw}], rev:[...]}` but dashboard `rRnk()` expects `[{r,l,ct,p,a}]`
**Fix options:** (a) Update Python parser to output the expected format, OR (b) Update `rRnk()` to accept the nested dict format

### F3. CRITICAL — Unowned Risk Always Empty
**Symptom:** "No unowned risk data" always shown
**Root cause:** Python parser does not populate the `unowned` field
**The `unowned` field** should list BM holdings not in the portfolio that contribute to TE
**Fix:** Add `unowned` computation to Python parser (filter benchmark-only holdings with significant TE contribution)

### F4. HIGH — Sector TE Contrib Uses Wrong Field (%S instead of %T)
**Symptom:** "TE Contrib" column in Sector Weights table shows stock-specific risk, not TE contribution
**Root cause:** `rWt()` sums `h.mcr` (`pct_s` = %S) instead of `h.tr` (`pct_t` = %T)
**Affected:** Sector Weights table (A2), Sector Drill modal holdings list (B2/B14)
**Fix:** Change `h.mcr` to `h.tr` in the sector TE contrib accumulator

### F5. HIGH — Stock Modal "Revenue" Should Be "Revision"
**Symptom:** Stock detail popup shows "Revenue" as label for the `rev` sub-rank score
**Root cause:** Typo in `oSt()` HTML template
**Fix:** One-line label change

### F6. HIGH — Sector/Region Drill Shows MOM+STAB Score Cards
**Symptom:** Drill modals show 6 quant score cards; PM preference is 4 (OVER/REV/VAL/QUAL only)
**Root cause:** Loop in drill modal renders all 6 rank types
**Fix:** Filter to only render OVER, REV, VAL, QUAL cards in sector/region drills

### F7. MEDIUM — Factor Correlation (Exposures Tab) Is Synthetic
**Symptom:** Correlation values change on every page load; not reproducible
**Root cause:** `genFCorr()` generates random values seeded by strategy name
**Fix:** Replace `rFCorr()` call with `rUpdateCorr()` output (which computes real Pearson from hist.fac) OR remove the Exposures tab correlation table entirely

### F8. MEDIUM — Brinson Attribution Waterfall Is Synthetic
**Symptom:** Attribution numbers are fabricated
**Root cause:** `rAttr()` uses `genAttrib()` random data
**Fix:** Connect to real attribution data — `f.ret` and `f.imp` fields in the factors array contain real return/impact values

### F9. MEDIUM — Holdings Count Shows as Float
**Symptom:** Week selector shows "Holdings: 4.6" instead of "Holdings: 5"
**Root cause:** `hist.summary[].h` is `4.593` (float) from Python parser
**Fix:** `Math.round(h.h)` in week selector display and `rSumCards()` render

### F10. MEDIUM — FAC_PRIMARY Set Name Mismatch
**Symptom:** Momentum factor sometimes classified as secondary (hidden behind "Show More") depending on which parser produced the data
**Root cause:** FAC_PRIMARY set in dashboard contains `'Momentum (Medium-Term)'`; Python parser may output `'Momentum'`
**Fix:** Normalize factor names in FAC_PRIMARY check or in the parser output

### F11. LOW — Idio Risk Modal Rank Shows "Q--"
**Symptom:** Idiosyncratic Risk modal shows `Q--` for holdings with null rank
**Root cause:** Template `Q${h.r||'--'}` — the "Q" prefix is always added
**Fix:** Conditional: `h.r ? \`Q${h.r}\` : '--'`

### F12. LOW — Factor TE Contrib Is Approximate
**Symptom:** TE Contrib column in factor tables uses proxy calculation `|a| × dev` instead of real TE contribution
**Root cause:** `f.c` field not output by Python parser
**Fix:** Add TE contrib calculation to Python parser (if available in source data), or document clearly as "approximate"

### F13. LOW — Available Dates Not Computed by JS Parser
**Symptom:** Week selector disabled/empty when data loaded via in-browser CSV drag-drop
**Root cause:** `parseFactSetCSV()` in-browser parser does not compute `available_dates` array
**Fix:** Add `available_dates` population to in-browser parser's post-processing step

### F14. LOW — Factor Sparklines Show Single Point
**Symptom:** All factor sparklines in Exposures and Risk tabs show "—" or a single dot
**Root cause:** Test file has only 5 weeks of data; `hist.fac` populated with 1 entry per factor
**Note:** This is a data volume issue, not a code bug. Will resolve with production 3-year files.

---

## G. Priority Fix List

### Priority 1: CRITICAL — Must Fix Before Production Use

| ID | Issue | File | Fix |
|----|-------|------|-----|
| G1 | YYYYMMDD dates show "Invalid Date" in all time series / week selector | dashboard_v7.html | Add `parseDate()` helper; replace all `new Date(d)` on history dates |
| G2 | Quant Ranks table broken — parser format mismatch | factset_parser_v2.py + dashboard | Align `ranks` output format: `[{r,l,ct,p,a}]` per quintile level |
| G3 | Unowned risk always empty | factset_parser_v2.py | Compute `unowned` array in parser (BM-only holdings with `pct_t > threshold`) |

### Priority 2: HIGH — Data Integrity Errors

| ID | Issue | File | Fix |
|----|-------|------|-----|
| G4 | Sector TE Contrib column uses %S (wrong field) | dashboard_v7.html | Change `h.mcr` → `h.tr` in `rWt()` TE contrib accumulator |
| G5 | Stock modal label "Revenue" → "Revision" | dashboard_v7.html | One-line label fix in `oSt()` template |
| G6 | Sector/Region drill shows 6 score cards (should be 4) | dashboard_v7.html | Filter drill card loop to OVER/REV/VAL/QUAL only |

### Priority 3: MEDIUM — Missing Real Data

| ID | Issue | File | Fix |
|----|-------|------|-----|
| G7 | Factor Correlation (Exposures) is synthetic | dashboard_v7.html | Remove `genFCorr()` / use `rUpdateCorr()` output or hide when insufficient history |
| G8 | Attribution waterfall is synthetic | dashboard_v7.html | Connect `rAttr()` to real `f.ret`/`f.imp` values, remove `genAttrib()` |
| G9 | Holdings count shown as float | dashboard_v7.html | Wrap `h.h` in `Math.round()` in week selector and summary cards |
| G10 | FAC_PRIMARY set name mismatch for Momentum | dashboard_v7.html | Normalize `'Momentum (Medium-Term)'` → `'Momentum'` in FAC_PRIMARY or accept both |

### Priority 4: LOW — Polish and Minor Bugs

| ID | Issue | File | Fix |
|----|-------|------|-----|
| G11 | Idio Risk modal shows `Q--` for null rank | dashboard_v7.html | Conditional render: `h.r ? \`Q${h.r}\` : '--'` |
| G12 | Factor TE Contrib is approximate (not labeled as such) | dashboard_v7.html | Add "~" prefix or "(est.)" label to TE Contrib column header |
| G13 | Available dates not computed by in-browser JS parser | dashboard_v7.html | Add `available_dates` computation to `parseFactSetCSV()` post-processing |
| G14 | Stress Scenarios table is synthetic | dashboard_v7.html | Remove or clearly label as "Illustrative" until real stress data available |

---

## Summary Scorecard

| Category | Count | Status |
|----------|-------|--------|
| Critical bugs (blocks production) | 3 | G1, G2, G3 |
| High bugs (data integrity) | 3 | G4, G5, G6 |
| Medium (missing real data, showing synthetic) | 4 | G7, G8, G9, G10 |
| Low (polish, labels, edge cases) | 4 | G11, G12, G13, G14 |
| **Total issues** | **14** | |

**Tables rendering correctly:** Holdings, Sector Weights (OW/UW color), Region, Country, Factor Detail (structure), Factor Exposures (Risk tab), Characteristics, Risk Summary Cards
**Tables broken or synthetic:** Quant Ranks, Factor Correlation (Exposures), Attribution Waterfall, Stress Scenarios, Unowned Risk
**Modals with bugs:** Stock Detail (label), Sector Drill (field + extra cards), Idio Risk (null display), all time series (Invalid Date)

---

*End of audit. No code was modified during this analysis.*
