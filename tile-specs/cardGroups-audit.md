# Tile Audit: cardGroups — Redwood Groups (Treemap / Table)

> **Audit date:** 2026-04-30
> **Auditor:** Tile Audit Specialist
> **Dashboard:** dashboard_v7.html (10,989 lines)
> **Prior audit:** `cardGroups-audit-2026-04-23.md` (1 week ago) — RED on data accuracy due to render-side rank recompute via non-exclusive GROUPS_DEF; cited dead `oDrGroup` drill (`h.sec` full-name vs `gd.secs` abbreviated mismatch); identified `h.subg` as authoritative.
> **Gold standard for header pattern:** cardFacRisk (L1795–1809) — title + small grey subtitle + KPI strip + `class="export-btn"` ⛶.
> **Methodology:** 3-track audit (data accuracy / functionality parity / design consistency).

---

## VERDICT: RED

The treemap rebuild (chart-default view, parent→sub-group hierarchy, white labels with TE on each cell) is genuinely beautiful and visually clear. The 2026-04-30 batch closed the dead drill (`oDrGroup` now filters by `h.subg`, L9651), shipped the About entry, threshold row classes, view-aware FS, plotly_click drill on the chart, contextmenu note hook on the title, R/V/Q tooltips, and B116 Universe-pill TE invariance. **But the highest-severity finding from the 2026-04-23 audit was NOT closed — it was widened.** The render-side TE / count / factor-breakdown / rank cells in `rGroupTable` still aggregate via `secToSg2[h.sec]` (sector→sub-group with *deliberate overlap* via `GROUPS_DEF`), producing user-facing numbers that are **5–7× wrong** for sub-groups whose constituent sectors appear in multiple `GROUPS_DEF` rows.

Concretely (GSC, 1Y file, verified against `latest_data.json` + `cs.groups[]`):

| Sub-group | Rendered TE Contrib (table) | Parser g.tr (FactSet authoritative) | Δ | Direction |
|---|---|---|---|---|
| **GROWTH** | **40.10** | **6.00** | **+34.10** | **6.7× overstated** |
| **SOFT CYCLICAL** | **44.70** | **8.40** | **+36.30** | **5.3× overstated** |
| GROWTH CYCLICAL | 36.00 | 37.90 | −1.90 | accurate |
| DEFENSIVE | 5.60 | 7.70 | −2.10 | understated |
| HARD CYCLICAL | 10.30 | 13.10 | −2.80 | understated |
| COMMODITY | 10.30 | 14.00 | −3.70 | understated |
| BANKS | 9.70 | 10.20 | −0.50 | accurate |
| BOND PROXIES | 0.90 | 1.50 | −0.60 | small absolute |

Sum of displayed TE = **157.6**, which is mathematically impossible (TE share is bounded ≤ 100%) — a numeric red-flag the verifier should be catching. Same overlap distorts the holdings count (SOFT CYCLICAL displayed n=20 vs 12 actual h.subg matches; GROWTH n=14 vs 3 portfolio-owned with h.subg=GROWTH), the factor-contribution breakdown (purple cells right-of-table), and the weighted-rank columns (O/R/V/Q).

The treemap (chart view) uses the **correct** exclusive parent rollup from `cs.groups[]`. So a user toggling Chart→Table sees `cs.groups[].p` match (12.8%, 22.2%, etc.) but `TE Contrib` jumps from "GROWTH share of TE = 6%" implied by treemap colors to "GROWTH = 40 of 100 TE" in the table, with no caveat. **Two columns side-by-side from different taxonomies, no disclosure.**

The tooltip at L3913 admits "Holdings can belong to multiple subgroups" — but FactSet's `cs.groups[].n` is exclusive and `h.subg` is exclusive. The overlap is **render-only**, introduced by GROUPS_DEF, and the tooltip codifies the wrong story.

Plus header polish gaps and an inert Wtd/Avg toggle that the tile inherits from `_secRankMode` shared state.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | Redwood Groups |
| Card DOM id | `#cardGroups` (L1893) |
| Render fns | `rGroupTable(s.groups, s.hold)` L3824–3923 (table view, hidden by default); `rGroupChart(s, divId?)` L5281–5394 (treemap, default view) |
| Drill fn | `oDrGroup(groupName)` L9646–9674 — drill modal: subgroup roll-up + holdings (top 15) filtered via `h.subg===groupName` |
| Drill modal id | `#groupModal` |
| FS opener | `openGrpFullscreen()` L2689 — view-aware: Chart → `openGrpChartFullscreen()` L2696; Table → `openGrpTableFullscreen()` L2713 (both reuse `#secFsModal`) |
| About entry | `_ABOUT_REG.cardGroups` L732–738 — claims "exclusive bucketing — every holding in exactly one group", consistent with parser/h.subg, but **inconsistent with the render's actual GROUPS_DEF overlap path** |
| Tab / row | Exposures Row 5 (full-width via `<div class="card">` in flat block, line 1893) — visible regardless of `isUSOnly` |
| Filter chip | `#grpFilterChip` (per-column tile filters, shared infra with sectors via `TILE_REG.grp` L2365) |
| Universe (Aggregator) | global `_aggMode` (portfolio / benchmark / both) — drives factorAgg.count + factorAgg.avg ranks (NOT TE/MCR/factor — B116 invariant ✓) |
| Rank-avg method | global `_avgMode` ('wtd' / 'avg') + `_secRankMode` (legacy 'wtd'/'avg'/'bm', shared with cardSectors) |

---

## 1. DATA ACCURACY — FINDINGS

### 1.1 [SEV-1] Render uses GROUPS_DEF overlap when authoritative `h.subg` exists — TE 5–7× wrong

**Verified against `latest_data.json` (GSC, 1Y file, 131 holdings, 8 sub-groups).**

The legacy `GROUPS_DEF` constant at L546–555 maps GICS sectors to Redwood sub-groups using **deliberate overlap**:

```
Materials,Energy   → HARD CYCLICAL (and also COMMODITY)
Info Technology    → GROWTH CYCLICAL (and also GROWTH)
Health Care        → DEFENSIVE (and also GROWTH)
Consumer Disc.,Industrials → SOFT CYCLICAL
```

The render at L3866 builds `secToSg2 = {fullSec: [sg, sg, ...]}` — so a single Materials holding (e.g., Wienerberger AG, port=1.2%, tr=0.6) gets dispatched into BOTH `HARD CYCLICAL` AND `COMMODITY` accumulators inside `aggregateHoldingsBy(...)` (multi-key form). Same for every Info Tech / Comm Services holding (→ both GROWTH CYCLICAL and GROWTH); every Health Care holding (→ both DEFENSIVE and GROWTH).

This is the multi-key path (the parser ships `cs.groups[]` with **exclusive** sub-group totals from FactSet directly, and per-holding `h.subg` is **exclusive**). The render constructs a 3rd taxonomy that disagrees with both.

Symptoms (from `latest_data.json`, GSC, after normalize w→p, bw→b, pct_t→tr):

```
                  TE Contrib                 Holdings count
Sub-group     Render  Parser  Truth(h.subg)   Render  h.subg-direct
GROWTH         40.10    6.00      7.60          14         3 (port-owned)
GROWTH CYCLICAL 36.00  37.90     42.40           9         9
SOFT CYCLICAL  44.70    8.40      8.40          20         3 (port-owned)
DEFENSIVE       5.60    7.70      7.60           7         5 (port-owned)
HARD CYCLICAL  10.30   13.10     15.10           4         3 (port-owned)
COMMODITY      10.30   14.00     15.20           4         3 (port-owned)
BANKS           9.70   10.20      9.70           7         7
BOND PROXIES    0.90    1.50      0.00           1         0
                                                ─────       ─────
Σ TE displayed = 157.6%   — IMPOSSIBLE (must be ≤ 100%)
```

The same overlap bites:
- `# (count)` column at L3905 (`factorAgg[gn]?.count`)
- `Stock TE` column at L3888 (`aggMcr(gn)`)
- `Factor TE` column at L3889 (computed `teTotal − teMCR`)
- 12-column `Factor TE Breakdown` at L3898–3903 (`factorAgg[gn]?.factor[fname]`)
- `O / R / V / Q` weighted-rank cells at L3893–3896 (S/C/W/PW accumulators ALL multi-bucket)

The drill fn `oDrGroup` at L9651 was correctly fixed to use `h.subg===groupName` (per prior audit T3 — "ship-blocking dead drill"). So **drill** is right. **Table cells** are wrong. Same tile, two taxonomies.

The card-title tooltip at L1898 says "exclusive bucketing — each holding in exactly one group" — **directly contradicts what the table is computing**. The TE column tooltip at L3913 ("Holdings can belong to multiple subgroups") tries to defend the render path, but it's not the actual ground truth; it's just describing a bug.

**Proposed fix.** Two parts (combine):

**(a)** For the TE / MCR / Stock-TE / Factor-TE / Factor-Breakdown columns: use `cs.groups[]` parser-authoritative values directly. `cs.groups[].tr / .mcr` are FactSet-computed and exclusive. Drop `aggregateHoldingsBy(hold, h=>secToSg2[h.sec], ...)` for these columns. ~15 lines.

**(b)** For the count / weighted-rank columns: switch the groupKeyFn to `h => h.subg || null` (single key, exclusive). The count drops from "20 with sector membership" to "12 actual h.subg holdings" — matches drill, matches treemap. Per-bucket O/R/V/Q simple-mean and weighted average then come from the right population. ~3 lines (just swap the lambda).

Verified empirically: applying (b) reproduces the exclusive treemap parent rollups and matches `h.subg` distinct-holding counts to within ±1 (cash filtering edge case).

This is the primary blocker preventing GREEN. The numeric distortion is on the order of cardScatter's `h.mcr` mislabel from the 2026-04-12 crisis — same severity class. The April-27 anti-fabrication policy is binding here: parser ships an exclusive answer; render fabricates a non-exclusive answer with no `_X_synth=true` marker, no SOURCES.md entry, no on-screen disclaimer.

### 1.2 [SEV-2] Parent treemap rectangles + sub-group child cells use the EXCLUSIVE rollup — already correct, but inconsistent with table

`rGroupChart` at L5281 builds the treemap from `cs.groups[]` (exclusive subg sums) with `branchvalues:'total'`. Verified parent rollups (GSC):

```
GROWTH           port=12.80%  bench=16.45%  active=−3.70%  (1 sg)
CYCLICALS        port=42.00%  bench=39.10%  active=+3.00%  (3 sg: GC, HC, SC)
DEFENSIVE        port=17.90%  bench= 7.55%  active=+10.30%  (1 sg)
COMMODITY        port=10.80%  bench=14.66%  active= −3.90%  (1 sg)
RATE SENSITIVE   port=14.50%  bench=21.85%  active= −7.30%  (2 sg: BANKS, BP)
                 ──────       ──────
Σ ALL parents =  98.00%       99.61%        ← within 100% (correct exclusive rollup)
```

This rollup is the ONLY way to use the treemap because `branchvalues:'total'` requires children sum ≤ parent. So the chart-side math is correct.

But it makes the table-side overlap wronger by direct contrast: when user toggles Chart→Table, the visible quantum of "GROWTH" shifts — chart says GROWTH=12.8% port owned, table says GROWTH has TE=40.1% with count=14. No reconciliation.

**Proposed fix.** F1 above (lift table to exclusive) closes this; no separate treemap fix needed.

### 1.3 [SEV-2] B116 fix correctly applied — Universe pill does NOT change TE/MCR ✓

Verified by simulating both modes against the same dataset. TE is portfolio-invariant (B116 contract holds). Count, port-wt, bench-wt, weighted-rank cells DO change under Universe toggle, which is correct.

**No action.** This is the property the user asked the audit to verify — confirmed.

### 1.4 [SEV-3] `cs.groups[]` ships 8 sub-groups; `GROUPS_DEF` defines 8 sub-groups; mapping is 1:1 in practice today

Probed across all 7 strategies (sample_data.json: ACWI, IOP, EM, GSC, IDM, ISC, SCG) — every shipped sub-group label (`GROWTH`, `GROWTH CYCLICAL`, `DEFENSIVE`, `COMMODITY`, `HARD CYCLICAL`, `BOND PROXIES`, `BANKS`, `SOFT CYCLICAL`) appears in `GROUPS_DEF[].sg`. So today the treemap's `(Unmapped)` parent fallback (L5340) is not triggered.

**This is fragile.** If FactSet ever ships a new sub-group label (a Redwood taxonomy revision), it silently lands in `(Unmapped)` parent — visible only as a grey box with no parent header. No verifier check exists today.

**Proposed fix.** Verifier (`verify_factset.py`) should add a check: every `s.groups[].n` value must be in JS-side `GROUPS_DEF[].sg` list. Mismatch = WARN. ~10 lines. Long-term: move `GROUPS_DEF` to a JSON file the parser owns + ships.

Same shape as the COUNTRY_ISO3 / CMAP coverage gap raised in cardCountry-audit §1.5.

### 1.5 [SEV-3] BOND PROXIES has port=0.00% but renders a row — confusing without context

GSC's BOND PROXIES sub-group: parser ships `g.p=0.00, g.b=2.10, g.a=−1.6, g.tr=1.50`. We own zero, benchmark holds 2.1%; this represents an active short bet. The row renders normally in the table, with `f2(g.a)=−1.6` styled red (under-weight). 

But the treemap at L5345 does `values.push(+(g.p||0).toFixed(2))` — for a 0-port-wt sub-group the cell is invisible (0 area). The user can't see "we don't own anything in BOND PROXIES" from the chart. The row in the table is the only signal.

This isn't a bug per se but a missed surface. Treemap cell-area encoding is "what we own" — fine. But a small "Bench-only sub-groups" annotation strip below the treemap would surface BOND PROXIES (and any future zero-port subgroup) explicitly.

**Proposed fix.** ~10 lines to render a tiny strip below the treemap: "Not owned: BOND PROXIES (b=2.1%, a=−1.6%) — click for benchmark exposure." Trivial; defer to backlog.

---

## 2. FUNCTIONALITY PARITY — FINDINGS

### 2.1 [SEV-2] Chart/Table toggle state is not persisted — every re-render snaps back to Chart

`toggleGrpView(v, btn)` at L5703–5708:

```js
function toggleGrpView(v,btn){
  btn.parentElement.querySelectorAll('.toggle-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  $('grpChart').style.display=v==='chart'?'block':'none';
  $('grpTable').style.display=v==='table'?'block':'none';
  if(v==='chart')rGroupChart(cs);
}
```

No `localStorage.setItem('rr.grpView', v)`. No global state. On the next `upd()` re-render (Universe pill flip, week change, strategy switch, return from drill modal close), the static template at L1893 reasserts `class="toggle-btn active"` on the Chart button and `display:none` on `#grpTable` — user's table view choice is gone.

cardSectors has the same pattern but in reverse (Table is the default; chart toggle resets). cardCountry has the same pattern with three views. This is a cross-tile pattern, not a cardGroups-specific bug — but the audit asked specifically about it.

**Proposed fix.** Add `_grpView` global: `let _grpView=(localStorage.getItem('rr.grpView'))||'chart';`. In the static render template, branch the `display:none / block` and `class="toggle-btn active"` on `_grpView`. In `toggleGrpView`, persist + set the global. ~6 lines. Same fix shape needed on cardSectors and cardCountry.

### 2.2 [SEV-2] Chart-view full-screen treemap — minor sizing quirk

`openGrpChartFullscreen()` at L2696 sets `min-height:600px` on `#grpFsChartDiv` and calls `rGroupChart(cs, 'grpFsChartDiv')`. The treemap renderer at L5353 sets `div.style.height = h+'px'` where `h=Math.min(560, Math.max(280, parents.length*60+subgroups.length*22+80))` — a max of 560px, capped, regardless of the FS container. So in FS the treemap renders at 560px max while the FS panel offers 600px+ — there's wasted space at the bottom.

**Proposed fix.** When `divId !== 'grpChartDiv'` (i.e., FS context), bypass the cap. ~3 lines.

### 2.3 [SEV-2] CSV export reads from `#grpTable table` while user is on Chart view

`exportCSV('#grpTable table','groups')` at L1896 reads from the table-view DOM. Chart view doesn't render or hide the table — but the table still rendered server-side at initial mount (`<div id="grpTable" style="display:none;overflow-x:auto">${rGroupTable(...)}</div>` at L1901). So CSV download succeeds while user is on chart, returning a snapshot of the (currently-hidden) table. Same UX quirk as cardCountry §2.8.

Today this **silently exports the buggy GROUPS_DEF-overlap TE numbers**. So the CSV download propagates 1.1's wrongness to the user's analysis spreadsheets. After F1 lands, this is moot.

### 2.4 [SEV-3] No range selector or historical chart in `oDrGroup` drill modal

`oDrGroup` at L9646–9674 shows: 3 KPI cards (Port / Bench / Active aggregate of all sub-groups matching name — collapses to single sub-group's value since `cs.groups.filter(g=>g.n===groupName)` returns 1 row), then a sub-group breakdown table (always 1 row, redundant with KPIs), then top-15 holdings sorted by `h.p`.

Compared to `oDr('sec',name)` (sectors drill): no historical active-weight chart, no range selector, no "bench-only holdings" callout, no factor tilt summary. This was flagged in the 2026-04-23 audit (B62, B63) as blocked on `hist.grp` parser pipeline.

`hist.grp` IS NOW present in `cs.hist` per L1103 (`grp: h.grp || h.industries || {}` — wait, that's `h.industries`, looks like a copy-paste fallback bug; verify). Actual presence: `cs.hist.grp` is `{}` in `latest_data.json` (parser doesn't populate it yet).

So drill is still history-less. `cs.hist.grp` populated by parser is the gating dependency.

### 2.5 [SEV-3] plotly_click on chart drills correctly — but parent-group rectangle clicks are silently dropped

Wired at L5384: `if(id.startsWith('sg:')){...oDrGroup(sgName);}` — only sub-group cells drill. Parent rectangles (CYCLICALS, RATE SENSITIVE) are clickable but do nothing. Cursor doesn't change to indicate "this isn't a drill target."

A PM who clicks CYCLICALS expecting "show me all 3 sub-groups consolidated" gets… nothing. No feedback.

**Proposed fix.** Either:
- (a) Add a parent-group drill modal that lists all child sub-groups with combined KPIs ("CYCLICALS = HARD + GROWTH + SOFT, total port=42%, top 30 holdings across all 3"). ~30 lines.
- (b) Add a Plotly hover-template fallback message: "(Click a sub-group cell to drill — parent groups roll up)" inline in the parent's hover.
- (c) Leave a brief inline annotation in the chart subtitle: "click sub-group cells to drill (parents are rollups)". One-line fix.

(c) is the lowest-cost honesty.

### 2.6 [SEV-3] Sort works on cells with `data-sv` — confirmed across 8 columns. But Wtd/Avg toggle has no per-tile state

Per-cell `data-sv` is wired at L3854–3855 (rank cells), L3887 / 3888 / 3889 (TE cells), L3902 (factor cells), L3905 (count). All numeric sortable. Null-rank fallback uses `data-sv=""` per the prior audit T4 fix.

But the Wtd/Avg toggle (`_avgMode`) is global state shared with cardSectors. There's no on-tile pill (it lives on the page header). And `_secRankMode` (Wtd/Avg/BM) is *also* shared — three different values for what "averaged rank" means, all controlled outside the tile. This creates surprises: a user looking at cardGroups expecting Wtd would see Avg if they last clicked Avg on cardSectors.

**Proposed fix.** Either add an inline mini-pill on cardGroups itself ("Rank: Wtd|Avg") or document the cross-tile dependency in the tooltip. The former is cleaner.

### 2.7 [SEV-3] Spotlight rank context (top-rank stocks per sub-group) not surfaced anywhere

The 2026-04-30 brief asked: "Spotlight/rank context surfaced anywhere?" Answer: weighted-avg O/R/V/Q columns are at the right of the table (cells), and the drill modal shows ORVQ per holding (`rORVQCells(h)` at L9659). But there's no inline "best 3 by Overall rank in this sub-group" callout — the kind of "spotlight summary" the user might expect from a tile titled with proprietary categorization.

Today: to find "what are my best Spotlight names in DEFENSIVE", PM clicks DEFENSIVE row → drill modal → manually scans top-15. ~3 clicks.

**Proposed fix.** Tooltip on the cardGroups row could show top 3 names by Overall rank within sub-group. ~10 lines. Defer; nice-to-have.

### 2.8 [SEV-4] No filter chip / filter icon on the Chart view

`grpFilterChip` is rendered in the title row but it only governs the table filter state. The chart treemap doesn't honor any filter (Universe pill aside). If a user filters "GROWTH only" on the table and toggles to Chart, they see all 8 sub-groups again. Tile filter state is view-orthogonal.

This is the same UX quirk as cardSectors / cardCountry. Defer.

---

## 3. DESIGN CONSISTENCY — FINDINGS

### 3.1 Header pattern doesn't match cardFacRisk gold

cardFacRisk (L1795–1809):
- title (`class="card-title tip"`)
- small grey subtitle ("exposure × risk · bubble = factor σ")
- KPI strip below title (`#facRiskKpi`, populated post-render)
- ⛶ button using `class="export-btn"`

cardGroups (L1893–1899):
- title + ⓘ + filter chip ✓ ✓ ✓
- ⬇ CSV button + Chart/Table toggle + ⛶ ✓
- **NO subtitle** (vs cardFacRisk's "exposure × risk · bubble = factor σ")
- **NO KPI strip** ("Largest |active| sub-group / Largest |TE| sub-group / 8 sub-groups · 5 parents · 98% covered")

Suggested subtitle (rotates based on data): `proprietary sector taxonomy · 8 sub-groups under 5 parents · Σ port = 98%`

Suggested KPI strip:
- Largest |active|: "DEFENSIVE +10.3% OW"
- Largest |TE| share: "GROWTH CYCLICAL 38% of TE"
- Coverage: "98% of port covered (2% in [Cash])"

This is the pattern the 2026-04-30 audits of cardScatter, cardChars, cardCountry all flagged (consistent gap across non-cardFacRisk tiles). ~25 lines.

### 3.2 The "click sub-group to drill (parents are rollups)" hint is buried in the subtitle annotation at L5382

The chart's annotation is too long and reads as a single run-on caption: "Parent group → sub-group hierarchy · cell size = port wt · color = active wt · click sub-group to drill". Three pieces of info compressed into one line; on narrow viewports it can wrap awkwardly.

**Proposed fix.** Split into two annotations: one centered above the chart with the legend semantics ("size = port · color = active wt"), one inline at the bottom-right ("click sub-group to drill"). ~5 lines.

### 3.3 No color-bar legend visible on the table view's TE bars OR the treemap's color encoding

The treemap has a `colorbar` at L5365 (Active Wt %), but it sits inside Plotly's color bar — small, easy to miss. The table view has signed-magnitude TE bars (L3884–3886) with NO legend at all — the user has to discover that "right-of-axis red bar = adds risk, left-of-axis green = diversifies" via tooltip on individual cells (L3887 reads "Bar shows signed magnitude").

**Proposed fix.** Add a tiny legend strip below the table header for the TE Contrib column: `↤ diversifies · adds risk →` with green/red mini-bars. ~8 lines. Same pattern lift opportunity for cardCountry, cardSectors.

### 3.4 Treemap text contrast is fixed white — works on saturated colors, fails on near-zero active wt cells

Per the 2026-04-30 commit ec1f4fc, text was forced to `#ffffff` (L5373) with white text against a heatMid (`#1e293b` dark slate from theme) backdrop for cells with active wt ≈ 0. That's fine for dark theme. **In light theme**, the heatMid value is light grey-ish — white text on light grey is unreadable.

Theme-test command: `THEME().heatMid` returns dark-theme `#1e293b` always today (no light-theme branch). Need to verify against the light theme.

**Proposed fix.** Make text color theme-aware: `T.textHigh` (= var(--txth) probably). Or keep white and add a text-shadow with theme-aware shadow color. ~3 lines.

### 3.5 ⓘ About entry's "exclusive bucketing" claim contradicts the render code

L734–735 says "Group membership from FactSet SEC_SUBGROUP field on each holding (exclusive — every holding is in exactly one group). Group active weight = Σ h.a for holdings in group. |TE| share = Σ |h.tr| / total |TE|."

But the render at L3866 maps `h.sec` (GICS sector) → multiple sub-groups via GROUPS_DEF, NOT `h.subg`. So "Σ h.a for holdings in group" is *what the About claims*, not *what the table shows*. After F1 lands, this contradiction resolves; before then, the About is misleading.

**Proposed fix.** Either fix the About copy ("Render aggregates by GICS sector membership across all parent groups; treemap uses exclusive sub-group rollup"), OR ship F1 to align render with the doc. F1 is correct — fix the code, keep the doc honest.

### 3.6 No PNG button — ✓ (per user pref)

The 2026-04-23 audit T6 flagged a "Download PNG" item in the dropdown. Confirmed REMOVED — no PNG button on cardGroups today (only ⬇ CSV at L1896). Per MEMORY: "No PNG buttons on RR tiles." ✓

### 3.7 Filter chip rendered in title row but only governs the table — silent no-op on chart

The `<span id="grpFilterChip">` at L1898 displays active filter chevrons in chart-view contexts where they don't apply. Same UX inconsistency as the Top-N pill on cardCountry-map (per cardCountry-audit §3.2). 

**Proposed fix.** When the chart is the active view, hide the chip. Or scope filters to apply to the chart's parent/sub-group rectangle visibility (drop unmatched cells). Defer.

---

## 4. PROPOSED FIXES (PRIORITIZED, MAX 5)

| # | Severity | Effort | Description |
|---|---|---|---|
| **F1** | **SEV-1** | ~30 lines (delete + replace) | **Switch table TE/MCR/factor/count/rank columns from GROUPS_DEF overlap to `h.subg` exclusive.** Inside `rGroupTable` at L3863–3864, replace `groupKeyFn = h => secToSg2[h.sec] \|\| null` with `h => h.subg \|\| null` (single-key, exclusive). Drop the SEC_ALIAS2 / secToSg2 construction at L3860–3862 (dead). Drop the multi-bucket loop at L3839–3850 (dead). For TE Contrib + Stock TE + Factor TE columns specifically: source from `cs.groups[g.n].tr / .mcr` directly when `_aggMode==='portfolio'\|\|'both'` (parser-authoritative); fall back to factorAgg when in benchmark mode (where parser g.tr doesn't apply since g.tr is a portfolio property). Update tooltip at L3913 to drop "Holdings can belong to multiple subgroups" — that line is now wrong. Update About copy at L734–735 to match. **Eliminates the 5–7× TE distortion that's the highest-severity finding in this audit and the prior one.** |
| **F2** | SEV-2 | ~6 lines + 4 template branches | **Persist Chart/Table toggle state.** Add `let _grpView=(localStorage.getItem('rr.grpView'))\|\|'chart';` near L546. In template L1900–1901, branch `display:` and `class="toggle-btn active"` on `_grpView`. In `toggleGrpView` at L5703, write to localStorage and set global. Apply the same pattern to cardSectors's `_secView` (already a backlog item in cardSectors's audit). |
| **F3** | SEV-2 | ~25 lines | **Adopt cardFacRisk header pattern.** Add (a) subtitle row: `proprietary sector taxonomy · ${subgroupCount} sub-groups under ${parentCount} parents · ${ΣpFmt}% covered`; (b) inline KPI strip: 3 cards for Largest |active| sub-group, Largest |TE| sub-group, Coverage %. Lift skeleton from cardFacRisk's `#facRiskKpi`. Same gap as cardScatter / cardChars / cardCountry — cross-tile pattern. |
| **F4** | SEV-2 | ~8 lines + verifier hook | **Verifier check for GROUPS_DEF coverage.** In `verify_factset.py`, add a check: every `s.groups[].n` value across all strategies must be in the dashboard's JS-side `GROUPS_DEF[].sg` list. Mismatch = WARN with diff. Same pattern as the COUNTRY_ISO3 / CMAP coverage gap in cardCountry-audit §1.5. Future-proofs against silent (Unmapped) parents in the treemap when FactSet ships taxonomy revisions. |
| **F5** | SEV-3 | ~10 lines | **TE bar legend strip** + **theme-aware treemap text color**. Add a 1-line legend below the table header for the TE Contrib column (`↤ diversifies · adds risk →` with green/red mini-bars; ~8 lines). Make treemap text color theme-aware: `T.textHigh \|\| '#ffffff'` instead of hardcoded `#ffffff` at L5373 (~2 lines). |

**Out of scope for this round (next backlog):**
- B62/B63 successor: hist.grp parser population (still empty `{}` in latest_data.json — per L1103 the dashboard reads it but parser doesn't populate)
- Parent-group rectangle drill (audit §2.5 option (a) — 30 lines, defer)
- Bench-only sub-group strip below treemap (audit §1.5)
- Inline Wtd/Avg pill on cardGroups (audit §2.6) — cross-tile cleanup, defer
- "Top 3 by Overall rank" tooltip (audit §2.7)
- FS chart sizing fix beyond 560px cap (audit §2.2)
- Filter chip scope-to-active-view (audit §3.7)

---

## 5. CARRY-OVER FROM PRIOR AUDIT (2026-04-23)

**Closed since prior audit:**
- ✅ T1 (note hook + card-title tooltip on title L1898) — `class="card-title tip" data-tip="..." oncontextmenu="showNotePopup(...)"` shipped
- ✅ T2 (threshold row classes `thresh-warn` / `thresh-alert` on `<tr>`) — L3872 implements `Math.abs(g.a)>5 → alert, >3 → warn`
- ✅ T3 (dead drill — `oDrGroup` returning 0 holdings due to sec-name normalization mismatch) — L9651 now uses `h.subg===groupName` ✓
- ✅ T4 (data-sv on null rank cell) — L3854 shipped `data-sv=""` for the `—` case
- ✅ T6 (PNG removal) — confirmed: no PNG dropdown item; only ⬇ CSV
- ✅ T7 (plotly_click on chart) — L5384–5393 wires sub-group drill on treemap
- ✅ T8 (data-col attributes) — present on every `<th>` and `<td>` (group, count, port, bench, active, te_contrib, stock_te, factor_te, o, r, v, q, f_0..f_11)
- ✅ T9 (R/V/Q tooltips) — L3911 shipped `data-tip="Avg Revision MFR rank"` etc. on all 4 rank columns
- ✅ T10 (dead code `||gd.sg===groupName.toUpperCase()`) — drill-fn rewrite removed it
- ✅ ⓘ About entry (`_ABOUT_REG.cardGroups` L732–738) — shipped
- ✅ View-aware FS dispatcher (`openGrpFullscreen` L2689 → chart-FS or table-FS)
- ✅ Chart rebuild from bar to treemap (L5281) — vastly improved visual; plus the 2026-04-30 white labels + 3-line cell text + per-group TE
- ✅ B116 Universe-pill TE invariance — verified empirically (§1.3 above)

**Still open (escalated severity):**
- 🔴 **B61 (rank aggregation taxonomy)** — NOT closed. Render still uses GROUPS_DEF overlap. Scope WIDENED beyond ranks: the same overlap now bites TE Contrib (5–7× wrong on 2 sub-groups), Stock TE, Factor TE, Factor Breakdown columns, count column, weighted-rank cells. **This is F1 above — primary blocker.** Worsens the consequence: the visible TE numbers sum to 157.6%, mathematically impossible.

**Still open:**
- B62 (hist.grp parser pipeline) — `cs.hist.grp` empty `{}` in latest_data.json. Drill modal still history-less.
- B63 (drill parity uplift — historical chart, range selector, bench-only callout) — depends on B62.
- B64 (per-tile rank-mode state vs shared `_secRankMode`) — still a global; PM-deferred.
- B68 (GROUPS_DEF vs h.subg reconciliation memo) — F1's resolution makes this moot.

**New (introduced by 2026-04-30 round 1 treemap rebuild):**
- §1.4 (GROUPS_DEF coverage fragility — silent (Unmapped) parent if FactSet ships new sub-group label)
- §3.4 (treemap text-color theme dependency — hardcoded white)
- §3.2 (chart annotation density — multiple semantics in one line)
- §2.5 (parent-rectangle clicks no-op silently)

**New (introduced by 2026-04-30 commit ec1f4fc — 3-line cell text):**
- §1.5 (BOND PROXIES with port=0 invisible in treemap, only visible in table)

**New from cross-tile policy work (April 27–30):**
- §1.1's anti-fabrication framing ties to the April 27 hard rules. The render is creating a third taxonomy that disagrees with both parser and h.subg, with no `_X_synth=true` markers, no SOURCES.md entry, no on-screen disclaimer. This is the canonical pattern the data-integrity specialist exists to prevent.

---

**File:** `/Users/ygoodman/RR/tile-specs/cardGroups-audit.md`
**Dashboard untouched.** Main session serializes all code changes.
