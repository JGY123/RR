# Tile Audit: cardChars — Portfolio Characteristics

> **Audit date:** 2026-04-21
> **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html` (6,501 lines)
> **Methodology:** 3-track audit per `tile-audit-framework` + `AUDIT_LEARNINGS.md`
> **Special lens:** Spec-vs-code drift (prior spec at `portfolio-characteristics-spec.md`)

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Portfolio Characteristics |
| **Card DOM id** | `#cardChars` |
| **Render function(s)** | `rChr(s.chars)` at `dashboard_v7.html:L1796` (table) + inline HTML at L1233–L1237 |
| **Drill function** | `oDrChar(metric)` at `dashboard_v7.html:L5354` |
| **Modal DOM id** | `#charModal` (registered in `ALL_MODALS` L4655) |
| **Tab** | Exposures (first tab) |
| **Grid row** | Row 6 of Exposures — paired with cardRanks in `g2` grid |
| **Width** | Half (`g2`) |
| **Owner** | CoS / main session |
| **Spec status** | `draft` → this audit promotes to signed-off once trivial fixes applied |

---

## 1. Data Source & Schema — TRACK 1 (Data Accuracy)

**Section grade: YELLOW** — data path is clean and traceable, but the list is static and narrower than spec promises. Ground-truth spot-check pending a loaded JSON.

### 1.1 Primary data source
- **Object path:** `cs.chars[]` — array of `{m, p, b}` objects
- **Array length:** **fixed at 8 metrics** (hardcoded in parser L6179). Not driven by data shape.
- **Normalization at load:** `loadData()` L558 ensures `st.chars=[]` if missing.
- **Sum field fallback:** L534–537 maps legacy keys (`pe`→`pe_p`, `bpe`→`pe_b`, `pb`→`pb_p`, `bpb`→`pb_b`, `mcap`→`mc`) for v2 JSON files.

### 1.2 Field inventory

| # | Label | Field | Source in `cs.sum` | FactSet origin | Type | Example | Formatter | Tooltip |
|---|---|---|---|---|---|---|---|---|
| 1 | Market Cap ($M) | `c.p` / `c.b` | `sum.mc` / (derived bMc row[33]) | 42-col "Portfolio Characteristics" row[14] / row[33] | number | 4215.2 | `f2(v,1)` | none |
| 2 | P/E Ratio | `c.p` / `c.b` | `sum.pe_p` / `sum.pe_b` | 42-col "RiskM" row[9] / row[11] | number | 18.3 | `f2(v,1)` | none |
| 3 | P/B Ratio | `c.p` / `c.b` | `sum.pb_p` / `sum.pb_b` | 42-col "RiskM" row[10] / row[12] | number | 2.4 | `f2(v,1)` | none |
| 4 | ROE NTM (%) | `c.p` / `c.b` | `sum.roe` / (bRo row[40]) | row[24] / row[40] | number (%) | 15.1 | `f2(v,1)` | none |
| 5 | FCF Yield (%) | `c.p` / `c.b` | `sum.fcfy` / (bFc row[38]) | row[22] / row[38] | number (%) | 4.8 | `f2(v,1)` | none |
| 6 | Div Yield (%) | `c.p` / `c.b` | `sum.divy` / (bDy row[39]) | row[23] / row[39] | number (%) | 2.1 | `f2(v,1)` | none |
| 7 | EPS Growth 3Y (%) | `c.p` / `c.b` | `sum.epsg` / (bEp row[42]) | row[18] / row[42] | number (%) | 9.3 | `f2(v,1)` | none |
| 8 | Op Margin (%) | `c.p` / `c.b` | `sum.opmgn` / (bOm row[41]) | row[25] / row[41] | number (%) | 14.0 | `f2(v,1)` | none |

Derived "Diff" column: `diff = c.p - c.b` (computed in `rChr()` L1799).

### 1.3 Derived / computed fields
- **Diff:** `c.p - c.b` (not persisted on `c`, recomputed each render). `null` if `c.b == null`.
- **Color class:** `pos` (green) if diff > 0, `neg` (red) if diff < 0, empty if diff == null.

### 1.4 Ground truth verification
- [x] Parser mapping traced to FactSet row offsets (L6172–L6179). Row offsets match SCHEMA documentation for 42-col "Portfolio Characteristics" section.
- [x] Pe/Pb pulled from the separate 42-col "RiskM" section (L6155), then attached to `sum.pe_p/b` before `cs.chars` is constructed. L6175 checks `_cd` date ordering — ensures latest week wins.
- [ ] **Spot-check pending:** requires loaded JSON. Flagged per AUDIT_LEARNINGS.md convention.
- [ ] **FactSet team question still open:** "Benchmark P/E and P/B" listed in CLAUDE.md pending items. If FactSet returns blank, current benchmark P/E / P/B will render `—` via `f2(null,1)`. **Verify on current data.**

### 1.5 Missing / null handling
| Scenario | Current behavior | Adequate? |
|---|---|---|
| `chars` is `[]` | Renders `<p style="color:var(--txt);font-size:12px">No characteristic data</p>` | YES |
| `c.b == null` (e.g., BM P/E blank) | Displays `—` in Benchmark column; Diff shows `—`; row still clickable | YES — but diff cell has no class, silent "no comparison" |
| `c.p == null` | Displays `—`; Diff also `—` | YES |
| `c.p` is NaN / Infinity | `f2` handles NaN → `—`; no isFinite guard for Infinity | **Minor gap** — same as cardSectors before audit |
| Single row | Renders normally | YES |

---

## 2. Columns & Dimensions Displayed

| # | Label | Field | Format | Sort | Filter | Hide | Tooltip | Click |
|---|---|---|---|---|---|---|---|---|
| 1 | Metric | `c.m` | — | `sortTbl('tbl-chr',0)` | — | no | — | `oDrChar(m)` (whole row) |
| 2 | Portfolio | `c.p` | `f2(v,1)` | yes col 1 | — | no | none | row |
| 3 | Benchmark | `c.b` | `f2(v,1)` (null → `—`) | yes col 2 | — | no | none | row |
| 4 | Diff | `c.p - c.b` | `fp(v,1)` with `+`/`-` sign | yes col 3 | — | no | none | row |

Notable: **no units are visible in cell values.** "Market Cap ($M)" shows as `4215.2` with no $ or M. "P/E Ratio" shows as `18.3` with no "x". Users must look at the row label for context.

---

## 3. Visualization Choice

### 3.1 Layout type
Simple 4-column HTML table. No charts, no bars, no sparklines.

### 3.2 Axis scaling
N/A — table only.

### 3.3 Color semantics
- Green (`pos` class) = portfolio > benchmark on the metric. Uses `var(--pos)`.
- Red (`neg` class) = portfolio < benchmark. Uses `var(--neg)`.
- **Semantic problem:** "green = above benchmark" is meaningful for growth/quality metrics (ROE higher is good) but misleading for valuation metrics (P/E higher is usually worse) and ambiguous for Div Yield. Currently green simply means "higher" with no value judgment. Same gotcha the Characteristics spec flagged.

### 3.4 Responsive behavior
- Narrow viewport: grid collapses `g2` to single column (inherits base grid behavior); table itself doesn't wrap metric names but stretches on very narrow.
- No column picker — all 4 columns always shown.

### 3.5 Empty state
Good — renders `No characteristic data` (L1797).

### 3.6 Loading state
N/A — single-file dashboard; data loaded synchronously post-upload.

---

## 4. Functionality Matrix — TRACK 2 (Parity)

**Section grade: YELLOW** — basic primitives present, but missing most of what the spec promised and what sibling tiles have.

Benchmark comparison: **cardSectors** is gold standard per `AUDIT_LEARNINGS.md`.

| Capability | cardSectors (gold) | cardChars (current) | Gap? |
|---|---|---|---|
| Stable `<table id>` | `tbl-sec` | `tbl-chr` | — |
| `<th>` sortable | all columns | all 4 columns | — |
| `data-sv` on numeric cells | yes | **yes** (L1800 — `data-sv="${c.p}"` etc., `c.b??0` as fallback) | minor: `??0` falsifies nulls for sort (null treated as 0) |
| `class="clickable"` + `onclick` | yes → `oDr('sec',n)` | yes → `oDrChar(m)` | — |
| Empty-state fallback | yes | yes (`No characteristic data`) | — |
| CSV export | yes | yes (`exportCSV('#cardChars table','characteristics')`) | — |
| PNG export | yes (button) | yes (dropdown — **violates no-PNG rule per feedback_no_png_buttons**) | **REMOVE** |
| Row threshold classes (`thresh-alert` / `thresh-warn`) | yes (`|active|>5 / >3`) | none | `AUDIT_LEARNINGS.md` default — could adopt based on `\|diff/b\|` %-deviation |
| Header tooltips (`class="tip" data-tip`) | every numeric col | **zero** | per AUDIT_LEARNINGS.md Design section — "every numeric column should have tip" |
| Card-title tooltip | yes | yes (L1234 "Click a metric for historical comparison") | — |
| Note badge (📝) wire-up | via `refreshCardNoteBadges` on `card-title` right-click | **yes** (auto via global sweep L842 / L3484, no code needed in tile) | — |
| Filter bar | N/A | none | N/A — 8 rows doesn't need it |
| Column picker | yes | none | low priority (only 4 cols) |
| Full-screen modal button | yes (`openFullScreen`) | none | low priority |
| Toggle views (Table/Chart) | yes (groups) | none | **spec asked for inline deviation bars — gap** |
| Trend sparkline column | yes (cardSectors added one) | none | **spec asked for "benchmark comparison sparklines" — gap** |
| Theme-aware colors | reads `THEME()` / `var(--pos)` | reads `var(--pos)` / `var(--neg)` | — |
| Right-click context menu | global (via right-click handler) | inherits | — |

### 4.1 Functionality gaps vs cardSectors benchmark

1. **Header tooltips missing** — every numeric column `<th>` in sectors has `class="tip" data-tip="…"`. Chars has zero. Trivial.
2. **No threshold row classes** — sectors highlights rows where `|active|>3` / `>5`. Chars could do same with `|diff%|>10` / `>25`. Trivial if we settle on thresholds.
3. **PNG export present** — violates user rule "no PNG buttons on RR tiles" (feedback_no_png_buttons.md). Should be removed. The dropdown wrapper still makes sense for a CSV-only action if we want to keep it lightweight. Trivial.
4. **`data-sv="${c.b??0}"`** uses `??0` fallback which breaks sort semantics when benchmark is null (null rows will intersperse with real zeros). Should be `data-sv="${c.b??''}"` so sort treats them as empty strings at the end/start. Trivial.
5. **No `isFinite` guard** — if future data has Inf (e.g., P/E when earnings are zero), display will be `Infinity.toFixed(1)` → `"Infinity"`. Trivial guard. (Same pattern as Patch 003 elsewhere.)

### 4.2 Drill modal (`oDrChar`) parity review

Modal at L5353–L5367 opens `#charModal` with 3 cards (Portfolio / Benchmark / Difference). Parity issues:
- [ ] **Hardcoded "No historical data available"** (L5365). Spec asked for benchmark comparison sparklines; data `cs.hist.sum` contains `te/beta/pct_specific/pct_factor` but **not** `pe/pb/roe/fcfy/divy/epsg/opmgn/mc` over time. The parser stores latest-snapshot values only (L6177 overwrites `s.sum.mc/roe/…` each week). **To add trend, parser would need per-week characteristics persisted — non-trivial data change.**
- [ ] No close-on-Escape — but modal is registered in `ALL_MODALS` L4655 so global Escape handler should catch it. OK.
- [ ] No drill-back-to-table CTA, no export, no note badge. Low priority.
- [ ] `char.p` / `char.b` not null-guarded in modal — `f2(char.p,1)` handles null fine; `fp(char.p-char.b,1)` returns `—` for null arithmetic. OK.

---

## 5. Popup / Drill / Expanded Card

See 4.2. Modal is minimal (3 summary cards + placeholder text). Reuses the same field values — no independent data source.

---

## 6. Design Guidelines — TRACK 3 (Consistency)

**Section grade: YELLOW** — visually clean and consistent with the base table style, but flatter than sibling tiles and devoid of the richer encoding promised by spec.

### 6.1 Density
- Table inherits base `<table>` styling (11px `<td>`, 10px `<th>`) — consistent with cardSectors / cardHoldings / cardCountry.
- Padding: standard card (16px).

### 6.2 Emphasis & contrast
- Metric column: default text color (not `--txth`). Sibling tiles use `--txth` for the primary categorical column (e.g., holding ticker). **Minor inconsistency** — trivial.
- Diff column: green/red based on sign. Portfolio and Benchmark columns: no color. Consistent with cardSectors "Active" column.

### 6.3 Alignment
- Metric (col 0): left. Portfolio/Benchmark/Diff (cols 1–3): right (`class="r"`). Consistent with standard.

### 6.4 Whitespace
- Card padding matches peer (cardRanks). In `g2` grid on Row 6.

### 6.5 Motion / interaction feedback
- `.clickable` class → cursor:pointer + hover bg (inherited). OK.
- No loading state; no empty-state illustration. Empty text is bare but acceptable.

### 6.6 Consistency issues to flag
- **No header tooltips** (carried from §4). Trivial.
- **Metric label not visually grouped** — spec asked for grouping into Risk / Valuation / Growth / Quality. Current list is flat. Non-trivial visual refactor.
- **No units in cells** — "P/E Ratio" values shown as bare numbers like `18.3`. Could add unit to header or cell via formatter wrapper. Trivial-to-medium.
- **"Market Cap ($M)" label contains a comma-safe unit**, good.
- Card-title tooltip promises "historical comparison" but drill modal literally says "No historical data available". Trivial — either remove the promise or add the data.

---

## 7. Known Issues & Open Questions

1. **FactSet pending** (CLAUDE.md): "Benchmark P/E and P/B" — if still not populated, all chart diffs for P/E and P/B will render `—`. Verify on current JSON.
2. **Only 8 metrics persist to `cs.chars`** but parser pulls many more from FactSet (total_risk, active_share, predicted/historical/mpt betas, etc.). A richer metric list is available in `cs.sum` but not surfaced on this tile. PM decision: should Active Share / TE / Beta appear here (they appear on `cardThisWeek` already) or stay exclusive to the Overview snapshot?
3. **Two inputs for Diff direction semantics**: for P/E higher = worse, for ROE higher = better. Currently all-metrics use `diff > 0 → green`. PM input needed on whether to invert the color for valuation metrics (e.g., lower P/E = green).
4. **Historical data for chars**: parser overwrites `sum.mc/roe/…` each pass and does not append to `hist.sum` except for te/as/beta/h/cash (L6181). Persisting weekly chars history is a medium parser change — enables drill-modal sparklines that the spec asked for.

---

## 8. Verification Checklist

- [x] Data accuracy: field path traced from CSV row offsets to `cs.chars[]` — correct.
- [ ] Edge cases: empty array OK; isFinite guard missing (minor).
- [x] Sort: all 4 columns sortable via `sortTbl('tbl-chr',N)`.
- [ ] Sort of null benchmark: `data-sv="${c.b??0}"` treats null as 0 — incorrect. Trivial fix.
- [x] Empty state: "No characteristic data" present.
- [x] CSV export works (invokes `exportCSV('#cardChars table','characteristics')`).
- [ ] PNG export present — must be removed (user rule).
- [x] Drill modal opens.
- [ ] Drill modal shows "No historical data available" — matches reality but contradicts card-title tooltip.
- [x] Theme-aware (via `var(--pos)` / `var(--neg)` / `var(--txt)`).
- [x] Full-screen modal: N/A (not required for simple table).
- [ ] Header tooltips missing on all 3 numeric columns.
- [x] `<table id="tbl-chr">` stable.
- [x] Rows are `class="clickable"`.
- [ ] No console errors — not testable in this audit; defer to ship-readiness sweep.

---

## 9. Related Tiles

- **cardThisWeek** (overview snapshot) — displays a subset of the same `cs.sum` fields (TE, Active Share, Beta, Holdings count). Risk of duplication; risk of inconsistency if one tile updates and the other doesn't.
- **cardScatter / cardMCR** — also read `cs.sum` for aggregate risk figures.
- **cardRanks** — paired with chars in same `g2` grid row. Reads `cs.ranks[]` (independent data).

---

## 10. SPEC-VS-CODE DRIFT — CALLED OUT PER MAIN-SESSION ASK

The "spec" at `tile-specs/portfolio-characteristics-spec.md` is a 281KB JSONL transcript (not a markdown spec) of a prior Claude agent session dated **2026-04-13** that was tasked with enhancing this tile. The agent reported it had implemented all 6 tasks. **None of those enhancements are present in the current `dashboard_v7.html`**. Either (a) the agent's edits landed in a worktree that was never merged, (b) they were rolled back, or (c) the agent's reports didn't match the phantom-writes reality (echoes the 2026-04-16 phantom-writes crisis; see `feedback_verify_writes.md`).

| # | Spec promise (task from 2026-04-13 agent) | Status in code today |
|---|---|---|
| 1 | Read current code / understand `cs.chars` | N/A — audit-only |
| 2 | **Inline visual bars in Diff column** showing deviation magnitude | **NOT PRESENT.** Diff is bare number only. |
| 3 | **Group metrics visually** (Risk / Valuation / Growth / Quality) | **NOT PRESENT.** Flat list of 8 rows. |
| 4 | **"Portfolio Profile" summary line** above table ("Growth-tilted, small-cap bias, quality overweight") | **NOT PRESENT.** |
| 5 | **Benchmark comparison sparklines if historical data exists** | **NOT PRESENT.** No historical chars data anyway — parser drops it. |
| 6 | **Highlight top 3 largest deviations** | **NOT PRESENT.** |
| — | CSS classes (`.chr-profile`, `.chr-tag`, `.chr-group-hdr`, `.chr-top3`, `.chr-devbar`, etc.) | **NONE FOUND** via grep. |
| — | JS helpers (`CHR_GROUPS`, `_chrGroup`, `_chrProfile`) | **NONE FOUND** via grep. |
| — | Card tooltip text "Dot = top 3 deviation. Bars show relative magnitude." | **NOT PRESENT.** Tooltip still reads "Click a metric for historical comparison." |

**Drift count: 6 of 6 spec promises are missing.** The tile today is the "Before" state the spec document described.

**Recommendation for CoS:**
- Do **not** treat `portfolio-characteristics-spec.md` as a live spec. It is a phantom artifact. Rename it to `portfolio-characteristics-spec.phantom-2026-04-13.md` or archive it.
- Rewrite a real markdown spec describing the desired end state (can draw from the transcript's ideas 1–6 since they are sound).
- Decide which of the 6 features are in scope for the current ship-readiness push:
  - Tasks 2, 3, 6 are trivial visual enhancements (CSS + one function rewrite).
  - Task 4 (Profile summary) is trivial (classifier function on 8 data points).
  - Task 5 (sparklines) is **non-trivial** — requires parser change to persist per-week chars to `hist.chars` or similar.

---

## 11. Proposed Fix Queue

### TRIVIAL (agent can apply in one sweep — est. <30 min total)

1. **Remove PNG export** from the download dropdown at L1235. Either collapse to a single CSV button or keep the dropdown with only CSV. (User rule; also scrub the `screenshotCard('#cardChars')` reference.)
2. **Add header tooltips** (`class="tip" data-tip="…"`) on all 3 numeric `<th>` (Portfolio / Benchmark / Diff) — matches cardSectors convention per AUDIT_LEARNINGS.md.
3. **Fix `data-sv` null fallback**: change `data-sv="${c.b??0}"` and `data-sv="${diff??0}"` to `data-sv="${c.b??''}"` / `data-sv="${diff??''}"` so sort treats nulls as empty not zero.
4. **Add isFinite guard** in `rChr` diff computation (defends against Inf when `c.b` is 0 upstream).
5. **Bold the metric name cell** with `color:var(--txth)` or `class="name"` for visual hierarchy parity with other tiles.
6. **Fix misleading card-title tooltip** — change "Click a metric for historical comparison" to "Click a metric for details" until historical data actually exists.
7. **Add threshold row classes** using %-normalized deviation — e.g., `|diff/b|>0.25 → thresh-alert`, `>0.10 → thresh-warn`. (Adopt cardSectors pattern; thresholds tuned for ratios not weights.)

### NEEDS PM DECISION

8. **Color semantic for valuation metrics** — should "lower P/E = green" (value-tilt positive) be inverted per-metric? Or keep current "higher = green" universal rule?
9. **Which metrics belong on this tile vs cardThisWeek** — TE / AS / Beta currently live elsewhere. Should chars be fundamentals-only or a fuller portfolio-vs-benchmark snapshot?
10. **Units in cells** — bare `18.3` for P/E vs `18.3x`? `4215.2` for Market Cap vs `$4,215M`? Needs PM call.

### NON-TRIVIAL (spec-drift recovery — queue separately)

11. **Metric grouping (spec task 3)** — add `CHR_GROUPS` config + classifier + group header rows. CSS + JS, ~60 lines. No data change.
12. **Inline deviation bars (spec task 2)** — add `.chr-devbar` CSS + bar-rendering inside Diff cell. Requires `maxAbsDiff` computation up front. ~40 lines.
13. **Top-3 highlighting (spec task 6)** — sort by `|diff/b|`, tag top 3 with `.chr-top3` row class. ~15 lines.
14. **Portfolio Profile summary (spec task 4)** — threshold-based classifier emitting 2–4 colored pills. ~50 lines.
15. **Historical sparklines (spec task 5) — BLOCKED** — requires parser change to persist per-week chars snapshots (probably `s.hist.chars[metricName] = [{d,p,b},...]`). Medium parser change + JSON bloat consideration. Mirrors the blocker noted in AUDIT_LEARNINGS.md for countries/groups/regions trend sparklines.

---

## 12. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Audit completed; 3-track methodology; spec-drift called out (6/6 promises unfulfilled) | tile-audit CLI |

---

## 13. Sign-off

**Status:** `draft` — do not promote to `signed-off` until trivial fix queue (items 1–7) is applied and PM decides on items 8–10. Non-trivial items (11–15) belong on a separate spec/implementation track.

**Grades:**
- Section 1 (Data Accuracy): **YELLOW** — clean path, narrow scope, spot-check pending, FactSet items still open.
- Section 4 (Functionality Parity): **YELLOW** — basics in place, several trivial gaps, spec-drift features missing.
- Section 6 (Design Consistency): **YELLOW** — correct but flatter than siblings; missing tooltips and grouping.
