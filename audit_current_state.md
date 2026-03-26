# RR Dashboard — Audit (2026-03-26)

## Audit Method
Code inspection of dashboard_v7.html (4,151 lines) against STEP 5 specifications.
CSV tested: risk_reports_s2_randomized.csv

---

## OVERVIEW / EXPOSURES TAB

### ✅ CORRECT
- Strategy selector: `<select>` dropdown, format "EM — Emerging Markets" ✅
- 3 summary cards: TE (number only, no %), Idiosyncratic Risk (% of TE), Factor Risk (% of TE) ✅
- Idio card click → `oDrMetric('idio')` → top 5 by |h.mcr|, shows ticker/name/%S/Q badge ✅
- Factor card click → `oDrFacRiskBreak()` → top 5 by |f.c|, shows name/contrib%/active exp ✅
- Cash + benchmark strip below cards ✅
- Sectors table: sorted by TE contrib desc ✅, columns: Sector/Port%/Bench%/Active/TE Contrib ✅, bar visual ✅
- Click sector → `oDr('sec', name)` → shows factor scores + holdings list ✅
- Factor detail: primary sorted by |f.c| ✅, Profitability green tint + tooltip ✅, secondary collapsed ✅
- Factor attribution waterfall below ✅
- Country weights ✅
- Regions at page bottom ✅
- Tab preserved on strategy switch ✅ (line 700: `go()` does not reset `activeTab`)

### ❌ NOT NEEDED / ALREADY REMOVED
- Holdings Count box in Risk tab: already absent ✅
- Stress scenarios in Risk tab: already absent ✅
- Regime bars: already absent ✅

---

## RISK TAB

### ✅ CORRECT
- Risk summary cards (5 cards: Total TE, Factor Risk%, Idio%, Beta, Active Share) — useful, keep
- TE Stacked Area: data values correct (gold+teal sum to white line via normalize) ✅
- Factor Contribution Bars: toggle TE/Exposure/Both ✅, threshold slider ✅, checkboxes ✅
- Shadow bars showing f.dev at 0.15 opacity ✅
- Factor Exposure History: checkbox toggles ✅, Select All / Clear All ✅, synthetic fallback ✅
- Correlation Matrix: period/freq dropdowns ✅, Pearson recompute ✅
- Correlation: ALL factors in checkbox list ✅
- Correlation: overflow-x auto ✅
- Range slider on TE chart ✅, scrollZoom ✅

### ❌ NEEDS FIX

**1. TE Stacked Area — WRONG COLORS**
- Current: Teal fill = stock-specific, Blue fill = factor
- Spec: Gold = idiosyncratic (stock-specific), Teal = factor
- Location: `rTEStackedArea()` lines 1585-1593
- Fix: swap colors — stock-specific → gold (#f59e0b), factor → teal (#06b6d4)

**2. Risk Tab Layout — Beta not side-by-side**
- Current: Beta chart is full-width card
- Spec: "Beta + empty space side by side"
- Location: `rRisk()` HTML template line 1456-1463
- Fix: Wrap in `<div class="grid g2">` with Beta left, key stats (Holdings, Active Share) right

**3. Correlation Matrix — uses HTML table not Plotly heatmap**
- Current: `rFCorr()` renders plain HTML table with basic threshold colors (>0.5=green, <-0.5=red)
- Spec: red(-1) → white(0) → blue(+1) continuous gradient, "Insight row: ⚠ r>0.7, ✓ r<-0.5"
- Location: `rUpdateCorr()` line 1179, `rRisk()` initial render line 1554
- Fix: Use `Plotly.newPlot()` with heatmap trace + proper colorscale

**4. Correlation active exposure computation — BUG**
- Current: `sliced[fn]=arr.map(h=>+(h.e||0))` uses raw exposure, NOT active
- Spec: Pearson on hist.fac ACTIVE exposures (e - bm)
- Location: `rUpdateCorr()` line 1216
- Fix: `arr.map(h=>h.bm!=null?+(h.e-h.bm).toFixed(4):(h.e||0))`

---

## HOLDINGS TAB

### ✅ CORRECT
- Default sort: %T descending ✅
- Columns: Ticker, Name, Sector, Country, Port%, Bench%, Active%, %S, %T, Rank ✅
- Industry column toggleable with button ✅
- %T column: horizontal bar visual ✅
- BM-only holdings where b > 0.5 or |tr| > 1 ✅
- Q1-Q5 colored badge ✅

---

## FACTORS (Exposures Tab)

### ✅ CORRECT
- Primary factors sorted by |f.c| ✅
- Profitability: green tint + ✦ marker + tooltip "Intentional — higher is desired" ✅
- Secondary factors collapsed by default ✅
- Factor attribution waterfall chart below ✅

---

## GLOBAL

### ✅ CORRECT
- Precision: 1 dec for TE/AS/weights, 2 dec for beta/exposures ✅
- Colors: blue=port, grey=bm, green=OW, red=UW ✅
- Regions at bottom ✅
- All time series: avg line (dashed) + ±1σ bands + range slider ✅ (see `oDrMetric`)
- Factor drill: dual chart (exposure top, return+impact bottom) ✅ (in `oDrF`)
- Week selector ✅, historical banner ✅
- Loading shimmer ✅, toast errors ✅

---

## CHECKLIST — Phase 1 Fixes

- [ ] Fix TE stacked area colors (gold=idio, teal=factor)
- [ ] Fix Beta layout (2-column with Holdings/AS stats on right)
- [ ] Upgrade Correlation to Plotly heatmap with proper colorscale
- [ ] Fix correlation active exposure computation (e - bm)
- [ ] Add `rUpdateCorr()` call to Risk tab setTimeout
