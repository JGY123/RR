# Tile Audit: cardChars — Portfolio Characteristics

> **Audit date:** 2026-04-30
> **Auditor:** Tile Audit Specialist
> **Dashboard:** dashboard_v7.html (9,937 lines)
> **Prior audit:** `cardChars-audit-2026-04-21.md` (10 days ago).
> **Gold standard for header pattern:** cardFacRisk (L1449–1458) + cardFacButt (L1542–1559).
> **Methodology:** 3-track audit (data accuracy / functionality parity / design consistency).

---

## VERDICT: RED

Two changes since the prior audit have shifted the assessment from YELLOW to RED:

1. **The Python parser now ships ~39 chars rows for GSC** (TE / Beta / Active Share / Market Cap + every :P/:B fundamental pair from the FactSet `_extract_port_chars` block). Verified against latest_data.json. The dashboard render path handles this fine (it iterates whatever cs.chars contains), **but the in-browser CSV-side parser at L9749 still hardcodes 8 metrics** — meaning if a user ever loads a CSV via the legacy in-browser path (now-blocked per CLAUDE.md anti-fabrication rule, but the code is still there) they'd silently get a smaller set than the Python pipeline. Schema duplication is exactly the kind of drift the integrity rules forbid.
2. **The drill modal `oDrChar` (L8807–8821) was untouched by the recent factor-tile rebuilds** and still terminates with `<p>No historical data available for this characteristic.</p>` — flatly contradicting the card-title tooltip ("Click a metric for details") and the user's reasonable expectation given that every other drill modal on the dashboard shows a time series.

Plus the carry-over: missing per-metric tooltips, no header polish, no inverted color semantic for valuation metrics, and no surfacing of holdings-level rank context now that mcap/over fields are populated on every portfolio holding.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | Portfolio Characteristics |
| Card DOM id | `#cardChars` (L1654) |
| Render fn | `rChr(chars)` at L3218–3226 |
| Drill fn | `oDrChar(metric)` at L8807–8821 |
| Drill modal id | `#charModal` (registered in `ALL_MODALS`) |
| Tab / row | Exposures Row 6 (paired with cardRanks, half-width `g2`) |
| CSV export | inline button at L1656 → `exportCSV('#cardChars table','characteristics')` |
| Data source | `cs.chars[]` shipped by Python parser `_build_chars()` (factset_parser.py L1239) |

---

## 1. DATA ACCURACY — FINDINGS

### 1.1 [SEV-2] Hardcoded chars schema in JS-side CSV parser drifts from Python parser

**Python `_build_chars()`** (factset_parser.py L1239–1293): builds dynamic list — TE / Beta / Active Share / Market Cap + every :P/:B pair from `pc_metrics`. GSC currently ships **39 rows** (verified). New rows appear automatically when FactSet adds a metric column.

**JS-side parser** (dashboard_v7.html L9749): hardcodes **8 rows** with raw row offsets `r2(mc)`, `r2(ro)`, `r2(fc)`, `r2(dy)`, `r2(ep)`, `r2(om)` plus the bench equivalents. If anyone re-introduced a CSV-in-browser path or copy-pastes this constant elsewhere, the schema would silently drift.

CLAUDE.md hard rule #1 says CSV in browser = error and `parseFactSetCSV()` should throw — confirm this rule is actually enforced (the L9749 logic looks dormant but is still callable). **Recommend deleting the JS-side chars build entirely; if someone ever loads via the legacy path, fail loud.** Two-source schema is exactly what the April 27 anti-fabrication rules forbid.

### 1.2 [SEV-3] Diff field provenance: `c.a` is shipped but ignored; rChr recomputes

Python parser (L1291) ships `chars[].a = _sub(p,b)` for every row. The dashboard's `rChr` at L3221 ignores it and recomputes `diff = c.p - c.b` locally. Two sources of truth, no diff-validation. Either (a) trust `c.a` and remove the local computation, or (b) keep recomputing and assert `c.a === c.p - c.b` so any silent corruption shows up. Right now if the parser-side and dashboard-side ever disagree, no one notices.

### 1.3 [SEV-3] `c.p`/`c.b` null-handling silently masks Tracking Error / Active Share rows

Parser ships `b: null` for Tracking Error (L1252) and Active Share (L1259) — these are portfolio-only metrics with no benchmark equivalent. Dashboard renders them with `—` in the Benchmark cell and `—` in Diff. Visually OK, but **a row labeled "Tracking Error (%) | 6.65 | — | —" looks like a data error, not a deliberate "BM has no equivalent" decision.** Either: hide the Diff cell entirely (colspan trick), or render a neutral chip "n/a — portfolio-only metric" in the Benchmark cell. The risk-PM reading the screenshot needs the explanation in the cell.

### 1.4 [SEV-3] Field shape mismatch — Python ships `Market Cap ($B)`, dashboard old data shipped `Market Cap ($M)`

Python at L1260 emits `Market Cap ($B)` with mcap/1000. Dashboard CSS / sort logic doesn't care, but any cached spec or doc referencing `$M` is stale. CLAUDE.md FactSet schema notes still say `Market Cap ($M)` (col[12]) — that's the pre-divide raw value; ship'd label is `$B`. Confirm with PM what the preferred unit is, then make sure parser, render, and CSV export all agree.

### 1.5 [INFO] Holdings-side mcap/over now richly populated — but unused on cardChars

The new Raw Factors merge populates `h.mcap`, `h.over`, `h.adv` for every portfolio holding. cardChars is a portfolio-aggregate tile and could legitimately surface the holdings-weighted distribution of these (e.g. "60% of port held in mcap > $5B names; 35% in Q1 names"). Currently doesn't. Not a bug — just an opportunity now that the data is there.

---

## 2. FUNCTIONALITY PARITY — FINDINGS

### 2.1 [SEV-1] Drill modal `oDrChar` terminates in dead-end "No historical data available"

L8807–8821:
```js
function oDrChar(metric){
  ...
  $('charContent').innerHTML=`
    <h2>${metric}<button class="close">×</button></h2>
    <div class="grid g3">...3 stat cards (Portfolio / Benchmark / Difference)...</div>
    <p>No historical data available for this characteristic.</p>`;
}
```

The card-title tooltip at L1655 promises "Click a metric for details." The actual modal shows the same three numbers already visible in the row, then a "no history" disclaimer. **This is the worst kind of UI promise — it tricks the PM into clicking, then offers nothing.**

Per CLAUDE.md `hist.summary` already carries `te`, `as`, `beta`, `h` per week. So at minimum the **first 3 metrics** (Tracking Error, Beta, Active Share — and #4 implicitly: holdings count via `h`) DO have history shipped. The modal could plot a Plotly time series for those four right now without any parser change. The remaining 35 fundamental metrics need parser-side persistence (HISTORY_PERSISTENCE.md backlog item B114) — but the modal should at least handle the four that exist correctly.

**Fix:** branch `oDrChar` on metric name. If `metric in {'Tracking Error (%)','Beta','Active Share (%)','Market Cap ($B)'}` → render time series from `cs.hist.sum`; else → render the "Awaiting parser-side history (B114)" disclaimer (more honest than the current).

### 2.2 [SEV-2] No header polish vs cardFacRisk gold standard

cardChars header L1654–1656 is a plain title + CSV button. Compare cardFacRisk (L1449–1458):
- Subtitle (small grey caption: "exposure × risk · bubble = factor σ")
- KPI strip (#facRiskKpi)
- ⛶ button using `class="export-btn"`

Suggested cardChars subtitle: "portfolio vs benchmark · click a row for history". KPI strip could surface: largest |diff/b|% deviation (e.g. "P/E +28% vs BM"), and a quick valuation/quality/growth/risk profile classification.

### 2.3 [SEV-2] No per-metric tooltip on `c.m` cell

`rChr` L3223 renders `<td>${c.m}</td>` plain — no `data-tip` even though some metric names ("Redwood ROIC - NTM", "Sales Revision 6 Months - FY1", "Price/Earnings (P/E)") need explanation. Sibling tile cardSectors decorates every numeric `<th>` with `class="tip" data-tip` (L2784–2790) — chars is the only tile in the Exposures section without per-row tooltips. Trivial.

### 2.4 [SEV-2] No metric grouping (Risk / Valuation / Growth / Quality)

39 flat rows is hard to scan. Phantom-spec drift item (#3 in prior audit) — was promised, never landed. Now more urgent because the parser ships ~5x more rows than before. Group headers + collapse/expand per group is a ~40-line change.

### 2.5 [SEV-3] Color semantic universal "higher = green" still wrong for valuation metrics

L3222: `cls = diff > 0 ? 'pos' : 'neg'` — green for higher P/E (which is bad), green for higher EV/SALES (also bad). Phantom-spec drift; PM-decision item from prior audit (P8). Still unresolved.

### 2.6 [SEV-3] No threshold row classes for outlier deviations

cardSectors highlights `|active|>3 → thresh-warn`, `|active|>5 → thresh-alert`. cardChars has zero. Could adopt `|diff/b|>0.10 → warn`, `>0.25 → alert` for fundamentals. Sibling-parity gap.

### 2.7 [SEV-3] No ⛶ full-screen modal — but 39 rows now warrants it

When the parser shipped 8 rows, no FS modal was needed. With 39 rows now, FS would let the user see all metrics + grouping + sortable headers without scrolling a half-tile. Cardiology change: copy the cardSectors FS modal pattern.

---

## 3. DESIGN CONSISTENCY — FINDINGS

### 3.1 Header doesn't match cardFacRisk pattern (subtitle + KPI strip + ⛶)

Same parity gap as on cardScatter. Currently L1654–1656 has only `<div class="card-title tip" ...>...</div><button class="export-btn">⬇ CSV</button>`.

### 3.2 Card-title tooltip lies

L1655 says "Click a metric for details." Modal shows nothing new. Either fix the modal (preferred) or fix the tooltip ("Drill is in development").

### 3.3 No section header pattern between metric groups

Per AUDIT_LEARNINGS.md design rule, section headers use uppercase mini-cap with letter-spacing (e.g. cardThisWeek's "TOP TE CONTRIBUTORS"). chars has no section dividers — all 39 rows look identical.

### 3.4 Diff column sign rendering inconsistent with sectors

cardChars Diff cell uses `fp(diff,1)` which prints `+` for positive, `−` for negative. cardSectors "Active" uses the same `fp` helper. OK — consistent. (Confirming a non-issue.)

### 3.5 Numbers lack units in cells

P/E row shows `18.3` not `18.3x`. Market Cap shows `4215.2` not `$4.2B`. Some metric labels have units (P/E parenthetical), some don't. The render path is `f2(c.p,1)` blindly — could route via a per-metric formatter map. Phantom-spec design point.

### 3.6 No tooltip provenance ("source:" tags)

PM has no way to know whether `Hist 3Yr Sales Growth = 15.2` is sourced from `pc_metrics.get('Hist 3Yr Sales Growth').p` (FactSet col offset N) or computed locally. Same hover-provenance gap flagged on cardScatter.

---

## 4. PROPOSED FIXES (PRIORITIZED, MAX 5)

| # | Severity | Effort | Description |
|---|---|---|---|
| **F1** | SEV-1 | ~50 lines | **Make `oDrChar` actually drill.** For metrics where history exists in `cs.hist.sum` (TE, Beta, Active Share, Holdings count), render a Plotly line chart of port vs implicit BM with range buttons (3M/6M/1Y/3Y/All) — match the existing `oDrMetric` modal pattern. For the other ~35 metrics, render an honest "Per-week history not yet persisted (B114)" notice instead of the current ambiguous "No historical data available". Removes the worst PM-facing UX promise the dashboard makes today. |
| **F2** | SEV-2 | ~25 lines | **Adopt the cardFacRisk header pattern.** Add subtitle ("portfolio vs benchmark · click a row to drill"), small KPI strip (largest abs % deviation among rows; profile chip "growth tilt / value tilt / quality" derived from a deterministic classifier on 5–6 known fundamental rows), and a ⛶ button (route to a full-screen modal listing all 39 rows with sortable headers and row grouping). |
| **F3** | SEV-2 | ~10 lines + 1 metric→meaning map | **Add per-row tooltips and unit-aware formatters.** `data-tip` on each metric name cell sourced from a static `CHAR_METRIC_DOCS` object (one-line description per known metric, "—" for unknowns). Wrap `f2(c.p,1)` in a `formatChar(c.m, v)` that picks `${v}x` for P/E, `$${f2(v/1000,1)}B` for Market Cap ($B), `${f2(v,1)}%` for percentage rows. ~10 metric-name regex matches. |
| **F4** | SEV-2 | ~30 lines | **Group metrics into Risk / Valuation / Growth / Quality / Other.** Add a `CHAR_GROUPS` config mapping metric name → group; emit a sticky-style sub-row `<tr class="group-hdr">` between groups (matches the `style="font-size:9px"` mini-cap pattern in cardSectors L3315). Optional: pill-toggle to filter to just one group. Phantom-spec recovery item. |
| **F5** | SEV-3 | ~5 lines + PM call | **Inverted color semantic for valuation metrics.** Build a `INVERTED_DIRECTION` set (P/E rows, P/B, EV/SALES, EV/EBITDA — these should render `diff > 0 → neg/red`, `diff < 0 → pos/green`). Trivial code, but blocked on PM confirmation that this is the desired semantic. Worth getting the answer this week. |

**Out of scope for this round:** parser-side full chars history (B114, blocked on JSON size budget), holdings-weighted rank/mcap distribution chips on chars tile (sev-4 nice-to-have), full FS modal with column picker (deferred until F1–F4 done).

---

## 5. CARRY-OVER FROM PRIOR AUDIT

- **Closed:** PNG button removed (L1656 is CSV-only now), `data-sv="${c.b??''}"` (already `??''` not `??0` — L3223), `isFinite` guard via `isFinite(c.p)&&isFinite(c.b)` (L3221), card-title tooltip text ("Click a metric for details" vs prior longer phrasing).
- **Still open:** F1 (drill), F2 (header), F3 (tooltips), F4 (grouping), F5 (color), threshold row classes, units in cells.
- **New (introduced by parser change since 2026-04-21):** the chars schema is now ~5x larger than at the prior audit and outpaced the tile's UX. Grouping was a nice-to-have at 8 rows; at 39 it is required for usability.
- **New (introduced by Raw Factors merge):** holdings-side mcap/over/adv data could feed a future "portfolio composition" sub-section. Tracked as a future spec item, not in F1–F5.
