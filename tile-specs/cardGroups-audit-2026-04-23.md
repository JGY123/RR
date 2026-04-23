# Tile Audit — cardGroups (Redwood Groups)

**Date:** 2026-04-23  
**Auditor:** tile-audit subagent  
**Card shell:** `dashboard_v7.html` L1228–L1236 (Exposures tab, full-width, Row 5)  
**Renderers:**
- Table: `rGroupTable(groups, hold)` at L1891–L1939 (NOT the shared `rWt` — cardGroups is the one sibling that has its own renderer)
- Chart: `rGroupChart(s)` at L2613–L2644
- Toggle: `toggleGrpView(v, btn)` at L2842–L2847
- Drill modal: `oDrGroup(groupName)` at L5460–L5490

**Data shape:** `cs.groups[] = {n, p, b, a, mcr, tr, over, rev, val, qual, mom, stab}` — parser `_extract_group_table('Group', acct)` at `factset_parser.py:747`. 19-col aggregate layout shared with sectors/countries/regions (per SCHEMA_COMPARISON.md L66–L97).

**Ground-truth probe:** Spot-check run against `/Users/ygoodman/RR/latest_data.json` (7 strategies, ACWI used as representative case). Key findings confirmed with numeric comparison (§1.3 below).

---

## Section 1 · Data accuracy — **RED**

### 1.1 Data path (correct, but partially bypassed)

Parser writes `s.groups` at `factset_parser.py:828` from FactSet "Group" section. Dashboard normalize() does not touch `s.groups` (RULE: parser data is SACRED). Render at L1235 calls `rGroupTable(s.groups, s.hold)` with cs.groups authoritative. **So far so good.**

### 1.2 `h.subg` IS populated (update to AUDIT_LEARNINGS.md!)

Contradicts current ledger claim (AUDIT_LEARNINGS.md L13, L63). In `latest_data.json` `h.subg` is populated for ~85% of holdings (all non-cash). Distribution on ACWI:
```
GROWTH:           382
None (cash etc): 379
BOND PROXIES:    304
COMMODITY:       303
GROWTH CYCLICAL: 293
BANKS:           257
DEFENSIVE:       246
HARD CYCLICAL:   224
SOFT CYCLICAL:   131
```

This means `h.subg` is **authoritative** and exclusive: each holding lives in exactly one subgroup. **This is the single most important finding** — it reshapes both the current bug and the cardTreemap Group-by toggle blocker.

### 1.3 RED: Render recomputes weighted-avg ranks and gets WRONG answers

`rGroupTable` L1895–L1918 ignores the parser-provided `g.over / g.rev / g.val / g.qual` and re-aggregates from `cs.hold[]` via a `secToSg` map built from `GROUPS_DEF + SEC_ALIAS`. Because GROUPS_DEF is non-exclusive (Info Technology maps to BOTH `GROWTH CYCLICAL` and `GROWTH`; Materials & Energy to BOTH `HARD CYCLICAL` and `COMMODITY`; Health Care to BOTH `DEFENSIVE` and `GROWTH`), every Info-Tech / Materials / Energy / Health-Care holding gets **double-counted** into two subgroup accumulators.

Empirical comparison (ACWI, Overall rank `O`, weighted mode — the displayed column):

| Subgroup | Render shows (current code) | FactSet authoritative (`g.over`) | Δ | Implication |
|---|---|---|---|---|
| GROWTH | **1.72** | **2.88** | −1.16 | Q2 (green) → displayed as Q2; should be Q3 (amber) |
| GROWTH CYCLICAL | 1.72 | 1.26 | +0.46 | Q2 correct either way |
| DEFENSIVE | 2.21 | 2.05 | +0.16 | Q2 both |
| BANKS | 2.86 | 3.02 | −0.16 | Q3 both |
| **HARD CYCLICAL** | **1.0** | **3.18** | **−2.18** | **Q1 (green, "best") displayed; actually Q3 (amber, "mid")** |
| **COMMODITY** | **1.0** | **2.24** | **−1.24** | **Q1 displayed; actually Q2** |
| BOND PROXIES | 2.0 | None (null) | — | Renders a rank where parser correctly shows no data |
| SOFT CYCLICAL | 2.6 | None (null) | — | Renders a rank where parser correctly shows no data |

HARD CYCLICAL is the worst single regression: PM sees a green-coded "best rank" column where FactSet's own computation says it's mid. COMMODITY same. BOND PROXIES and SOFT CYCLICAL render values that FactSet says are unknowable. **This is a PM-facing risk-domain data accuracy bug — same severity class as cardScatter's `h.mcr` mislabel.**

Root cause: 2018-era GROUPS_DEF predates FactSet shipping `SEC_SUBGROUP`. When `h.subg` started populating, the render wasn't updated to use it, and the non-exclusive GROUPS_DEF overlap was never reconciled with FactSet's exclusive bucketing.

**Verified fix direction** (simulated in audit workbench): replacing the `secToSg[h.sec]` loop with a direct `h.subg === gn` filter reproduces parser values exactly (2.88 / 1.26 / 2.05 / 3.02 / 3.18 / 2.24 / null / null — all match to 2 decimals).

### 1.4 MEDIUM: Parser-authoritative pre-aggregated ranks silently discarded (Pattern B)

Even simpler than the re-aggregation fix: `cs.groups[].over/rev/val/qual` are already computed by FactSet (weighted average via Group section). The render could consume them directly and skip the hold-loop entirely — same pattern as cardRanks audit finding (parser→normalize discard). The only reason to recompute would be to support per-tile `_grpRankMode` toggling (Wtd/Avg/BM) independently — but that's a PM-deferred concern (AUDIT_LEARNINGS.md "Shared state traps"). For now, **consume parser's weighted value** and drop the recompute.

If Wtd/Avg/BM toggle must still work against groups: use `h.subg` in the recompute (not GROUPS_DEF) — same loop, one-line swap.

### 1.5 Half-built pipeline: `hist.grp` is NOT declared by parser

Parser factset_parser.py:834–839 writes `hist:{summary, fac, sec:{}, reg:{}}` — no `grp`. Confirmed: `hist` keys in latest_data.json are `['summary','fac','sec','reg']`. No tile or drill currently reads `cs.hist.grp` so there's no live dead-column visible today, but:
- `oDrGroup` drill modal has no historical chart (L5478 onward is static-only). Siblings cardSectors / cardCountry drill to `oDr('sec',n)` which DOES render historical active weight series via `hist.sec[name]`. cardGroups drill is **history-less by design** because the pipeline wasn't built. Same class as cardRegions B6 blocker.
- No sparkline column in cardGroups table. Siblings cardSectors/cardRegions have inline sparklines. cardGroups does not.
- If cardGroups ever gets a sparkline column, it will be shell-only until parser produces `hist.grp`.

### 1.6 LOW: `isCash(h)` guard present, correct. Cash `[Cash]` row filtered at L1893 + L2615. ✅

### 1.7 LOW: Week-selector divergence

Like its siblings, `rGroupTable` silently renders latest data even when `_selectedWeek` is set. This is the two-layer-history architecture working as designed (consistent with cardSectors / cardCountry / cardRegions).

### 1.8 Aggregation quirk (LOW)

L1910 `let w=h.p>0?h.p:0` — correctly uses 0 fallback (not 1), unlike cardTreemap's `(h.p>0?h.p:1)` anti-pattern. Bench-weighted mode uses separate `bw` accumulator. ✅

### Verdict §1: **RED** — displayed ranks differ from FactSet's authoritative values by up to 2 quintile points, with HARD CYCLICAL reading "Q1 best" when it's actually Q3. PM-gated risk-domain accuracy bug.

---

## Section 2 · Functionality parity — **YELLOW**

Baseline: cardSectors (gold standard). Checklist (cardGroups vs cardSectors):

| Capability | cardSectors | cardGroups | Gap |
|---|---|---|---|
| Table render | ✅ via `rWt('sec',…)` | ✅ via `rGroupTable` | — |
| Chart/Table toggle | ❌ (always table) | ✅ (chart default, table alt) | cardGroups stronger |
| Download dropdown (PNG+CSV) | ✅ | ✅ | — |
| CSV button alone | ✅ | ✅ (via dropdown) | — |
| Sort on every column | ✅ `sortTbl('tbl-sec',N)` | Partial — `sortTbl('tbl-grp',N)` on cols 0–7 when ranks visible; **no `data-sv` on the rank-mode "—" sentinel** at L1921 (it does carry one at L1922). Sort works on filled cells. | tiny |
| `data-col="..."` on th/td | ✅ | ❌ entirely missing | YELLOW |
| Header tooltips (`class="tip" data-tip`) | ✅ on all numeric cols | Only on O (L1936 via `class="tip" data-tip="Avg Overall MFR rank"`); **R/V/Q have no tooltip** | YELLOW |
| TE Contrib + Stock TE + Factor TE columns | ✅ | ❌ | PM call — maybe worth adding parallel cols from `g.mcr` (%S) and `g.tr` (%T) since parser populates both |
| Sparkline / Trend column | ✅ | ❌ | blocked by hist.grp |
| Spotlight 2-row thead w/ inline rankToggleHtml3 | ✅ | ✅ (L1937) — matches sectors pattern | ✅ better than cardRegions |
| Row click → drill | `oDr('sec',n)` → historical chart | `oDrGroup(n)` → static modal | YELLOW (no history in drill) |
| `event.stopPropagation()` on download btn | ✅ (L1231 `onclick="event.stopPropagation()"` wrapping dl-wrap) | ✅ | — |
| `oncontextmenu="showNotePopup(event,'cardGroups')"` | ✅ on card-title | **❌ missing** — L1229 `<div class="card-title">Redwood Groups</div>` has no note hook | YELLOW |
| Card-title tooltip | ✅ (data-tip) | **❌** | trivial |
| Full-screen (⛶) button | ✅ for chart-heavy tiles | ❌ | low priority |
| `plotly_click` on chart → drill | cardSectors uses table not chart, but cardFacButt/cardScatter wire it | `rGroupChart` L2627 has **no** `plotly_click` handler → bar clicks don't drill | YELLOW |
| Theme-aware (THEME().grid/tick/zero) | ✅ | ✅ (L2635-2641) | — |
| Toolbar state persisted to localStorage | — | Chart/Table toggle resets to default "Chart" on every re-render | low (consistent with sibling defaults) |
| Keyboard a11y on tile-wide onclick | N/A | N/A (tile is not wide-click) | — |
| `tabindex` / role on drillable rows | ❌ | ❌ | consistent gap across siblings |
| Empty-state fallback | ✅ `<p>No group data</p>` at L1892 + L1894 | ✅ | — |
| `<table id>` | `tbl-sec` | `tbl-grp` ✅ stable id | — |
| CSV export selector | `#secTable table` | `#grpTable table` ✅ | — |

### 2.1 Drill parity gap (YELLOW)

`oDrGroup` at L5460 shows subgroup breakdown + top 15 holdings. Compared to `oDr('sec',...)` (L3946+) it is missing:
- Historical active-weight chart (no `hist.grp` pipeline)
- Range selector (3M|6M|1Y|3Y|All)
- Rank distribution histogram
- Factor tilt summary
- "Bench-only holdings in this group" section (useful because BOND PROXIES and SOFT CYCLICAL show p=0 b>0)

Smallest uplift: add **bench-only holdings** (no hist.grp dep needed) — matters because current drill shows only `hold.filter(h => groupSecs.has(h.sec))` which includes bench-only but sorts by `b.p` and truncates at top 15, so bench-only rows fall off. This conflates "we don't own anything in BOND PROXIES" with "we own some in BOND PROXIES".

### 2.2 `oDrGroup` sector matching bug (LOW)

L5464 `GROUPS_DEF.filter(gd => gd.sg === groupName || gd.sg === groupName.toUpperCase())` — the `||toUpperCase()` branch is dead because all `GROUPS_DEF[].sg` values are already upper-case and cs.groups[].n echo them upper-case. Harmless but dead code.

L5466 `groupDef.forEach(gd => gd.secs.forEach(s => groupSecs.add(s)))` pushes the **abbreviated** names (`Info Technology`, `Comm Services`, `Consumer Disc.`) from GROUPS_DEF without SEC_ALIAS normalization. Then L5467 filters `cs.hold.filter(h => groupSecs.has(h.sec))` where `h.sec` is the **full** name (`Information Technology`). **Result:** `oDrGroup('GROWTH CYCLICAL')` drill currently matches ZERO holdings from Info Technology or Comm Services (they're normalized to full names in `h.sec`). Consumer Disc. → Consumer Discretionary: same issue.

Empirically verifiable: drill into GROWTH CYCLICAL today → top 15 holdings shown are filter-empty. This is a dead drill, SHIP-BLOCKING as a UX bug. (T3 below.)

### 2.3 Chart `plotly_click` missing

Bars don't drill — user expectation set by cardSectors + cardFacButt drills. Wire `grpChartDiv.on('plotly_click', d => oDrGroup(d.points[0].y))`.

### 2.4 Primitives — `data-sv` on "—" cell

L1921 rank cell for `avg==null` has **no `data-sv`**. `sortTbl` falls back to textContent parsing → `parseFloat('—')` = NaN. Sort breaks if any column has mixed null + filled cells (which is always, for BOND PROXIES / SOFT CYCLICAL today). Fix: add `data-sv=""`.

### Verdict §2: **YELLOW** — strong table↔chart toggle (better than siblings), but dead drill (2.2), missing plotly_click, no `data-col` infrastructure, no contextmenu note hook, rank `—` sort breaks.

---

## Section 3 · Design consistency — **YELLOW**

Baseline: cardSectors gold standard.

| Design attr | cardSectors | cardGroups | Drift |
|---|---|---|---|
| Threshold row classes (`thresh-alert` / `thresh-warn`) | ✅ | **❌** — L1934 uses `activeStyle(g.a)` for cell coloring but doesn't add `thresh-alert` / `thresh-warn` to the `<tr>`. cardRegions has same gap. | YELLOW |
| Rank cell alignment | right (`class="r"`) | **center** (`text-align:center` at L1921, L1922) | YELLOW drift vs sectors — matches cardCountry + cardRegions. Unresolved cross-tile question (see AUDIT_LEARNINGS.md "Design conventions"). Flag to PM. |
| Rank cell bg tint | `rgba(99,102,241,0.07)` | **`rgba(99,102,241,0.04)`** (L1921, L1922) — lighter, matches cardRegions (NOT cardSectors) | YELLOW consistent with regions but drift vs sectors |
| Rank font weight | 600 | **700** (L1922) — heavier than sectors | low |
| Rank color | tokenized via `rc()` → var(--r1..--r5) | ✅ uses `rc(Math.round(avg))` | — |
| Null rank color | var(--txt) or similar | **hardcoded `#334155`** (L1921) — non-token | YELLOW (palette drift, adds site #6 to rank-color ledger) |
| Spotlight header colspan | ✅ | ✅ matches — L1937 `colspan="4"` for O/R/V/Q group, `rankToggleHtml3()` inline | ✅ |
| Card title note hook | ✅ `oncontextmenu="showNotePopup(..."` | **❌** | YELLOW |
| Card title tooltip (`tip` class + data-tip) | ✅ | **❌** (L1229) | trivial |
| Chart Portfolio color | shared token `var(--pri)` via `rgba(99,102,241,0.85)` | ✅ same hardcoded rgba — matches convention but token-missing | low (same as rRegChart — existing drift) |
| Chart Benchmark color | convention: muted grey | hardcoded `rgba(75,85,99,0.85)` — matches rRegChart at L2298/2301 | low (existing drift, see AUDIT_LEARNINGS.md "Viz-renderer pattern") |
| Chart legend position | tile-bottom | L2642 `y:1.05` (top) — inconsistent with some tiles; matches chart-above-table layout | low |
| Chart hover template | `<b>%{y}</b><br>Portfolio: %{customdata:.1f}%` | Portfolio trace OK (`customdata` = un-negated value); Benchmark uses `%{x:.1f}%` which is the positive x — ✅ correct | — |
| Table density (th/td padding) | 10px/11px | L1921/1922 `padding:4px 6px` for rank cells (tighter, consistent with sectors rank convention); regular cells use default | — |
| Click cursor | `class="clickable"` | ✅ L1934 `class="clickable"` | — |
| Hover state on chart bars | default Plotly | same | — |
| Download-dropdown PNG option | removed per user pref | **still present** at L1231 `Download PNG` — user repeatedly removed PNG buttons; cardRegions also still has one (AUDIT_LEARNINGS.md note) | YELLOW — remove PNG menu entry |
| chip (`<span class="chip">`) on first column | sectors uses plain text | **uses chip** at L1934 — subgroup names are bucket labels so chip is semantically correct (mirrors cardHoldings sector chip). Not a drift, a deliberate choice. | ✅ |
| Threshold class on `<tr>` for |a|>5 → alert, |a|>3 → warn | ✅ | **❌** | YELLOW (see row 1 of this table) — and DEFENSIVE has a=+13 in sample data, would otherwise glow alert |

### 3.1 Card-title tooltip missing explaining taxonomy (YELLOW)

Users see "HARD CYCLICAL", "GROWTH CYCLICAL", "BOND PROXIES" with no explanation. Unlike sectors (self-evident), Redwood's proprietary taxonomy needs a tip. Add `class="tip" data-tip="Redwood's proprietary sector groupings: CYCLICALS (Hard/Growth/Soft), DEFENSIVE, GROWTH, COMMODITY, RATE SENSITIVE (Banks, Bond Proxies). Subgroups may overlap by sector — see Factor Risk tab for exclusive bucketing."` or similar.

### 3.2 Overlap warning (disclaimer) missing

If we keep the GROUPS_DEF non-exclusive view, we owe users a "note: some sectors appear in multiple groups" disclaimer. If we switch to `h.subg` exclusive (the fix), we don't need one. PM call.

### Verdict §3: **YELLOW** — 5 concrete drifts from cardSectors gold standard + 1 PNG button still present + 1 null-rank palette drift. No single blocker. The threshold-class-on-row gap is the most visible (DEFENSIVE at +13 pp active misses alert highlight).

---

## Section 4 · Trivial fix queue

Numbered T1..TN. Each ≤ 5 lines, ready for inline application by main session. **None touch Python.**

**T1.** Add `class="tip" data-tip="..."` + `oncontextmenu="showNotePopup(event,'cardGroups');return false"` to card-title at L1229.
```html
<div class="card-title tip" data-tip="Redwood's proprietary sector groupings. Subgroups defined by Redwood, sourced directly from FactSet. Click a row to drill." oncontextmenu="showNotePopup(event,'cardGroups');return false">Redwood Groups</div>
```

**T2.** Add threshold row classes + tooltips on `<tr>` at L1934. Mirror cardSectors L1599.
```js
let threshCls=Math.abs(g.a)>5?'thresh-alert':Math.abs(g.a)>3?'thresh-warn':'';
return`<tr class="clickable ${threshCls}" onclick="oDrGroup('${g.n}')"> ... </tr>`;
```

**T3. [FIXES DEAD DRILL — ship-blocking UX bug]** `oDrGroup` L5464–L5467: normalize `GROUPS_DEF[].secs` with `SEC_ALIAS` before matching `h.sec`.
```js
const SEC_ALIAS={'Info Technology':'Information Technology','Comm Services':'Communication Services','Consumer Disc.':'Consumer Discretionary'};
let groupSecs=new Set();
groupDef.forEach(gd=>gd.secs.forEach(sec=>groupSecs.add(SEC_ALIAS[sec]||sec)));
// …existing filter now correctly matches h.sec
```
OR (cleaner): switch to `cs.hold.filter(h => h.subg === groupName)` — single-line swap, no SEC_ALIAS needed.

**T4.** Add `data-sv=""` to the null-rank cell at L1921 so `sortTbl` doesn't NaN on "—".
```js
return`<td data-sv="" style="text-align:center;...">—</td>`;
```

**T5.** Replace hardcoded `#334155` at L1921 with `var(--txt)` (same null-rank color convention as region rank cells when sectors were tokenized).

**T6.** Remove the "Download PNG" item from the download dropdown at L1231. Keep only CSV (per user preference — see AUDIT_LEARNINGS.md + MEMORY: "No PNG buttons on RR tiles"). Same fix applies to cardRegions (already flagged).

**T7.** Wire `plotly_click` on chart to drill. After `Plotly.newPlot(...)` at L2643, add:
```js
let el=$('grpChartDiv');
if(el&&el.on)el.on('plotly_click',d=>{let n=d&&d.points&&d.points[0]&&d.points[0].y;if(n)oDrGroup(n);});
```

**T8.** Add `data-col="group|port|bench|active|o|r|v|q"` to every `<th>` and `<td>` in `rGroupTable` — prerequisite for a future column picker. ≤ 8 attribute additions, zero behavior change.

**T9.** Add `class="tip" data-tip="..."` to R, V, Q header cells at L1936 (O already has one).
```js
'...<th ... class="tip" data-tip="Avg Revision MFR rank">R</th><th ... class="tip" data-tip="Avg Value MFR rank">V</th><th ... class="tip" data-tip="Avg Quality MFR rank">Q</th>'
```

**T10.** Dead-code cleanup: remove `||gd.sg===groupName.toUpperCase()` at L5464 (subgroup names are already upper-case). Trivial, but commit alongside T3.

---

## Section 5 · Non-trivial queue (B61+)

Propose adding to BACKLOG.md at the next B-series allocation (sibling batch used up through B60 per cardCorr audit — cardGroups starts at **B61**).

**B61 — Rank aggregation uses wrong taxonomy (RED data accuracy).**  
Size: M (1–2h).  
Scope: `rGroupTable` L1895–L1918 recomputes weighted-avg O/R/V/Q using `GROUPS_DEF + SEC_ALIAS` which is non-exclusive; FactSet's `h.subg` and `cs.groups[].over` use an exclusive bucketing. Result: HARD CYCLICAL reads Q1 (best) when it's actually Q3; COMMODITY similar. See §1.3 for full delta table.  
Fix options:  
**(a)** Consume `cs.groups[].over/rev/val/qual` directly (simplest — drops hold-loop entirely; Wtd/Avg/BM toggle becomes static-Wtd-only unless we keep the loop).  
**(b)** Keep loop but filter by `h.subg === gn` (enables the toggle; produces identical values to parser in Wtd mode; ~5-line change).  
Blocker: PM decision on whether Wtd/Avg/BM must remain toggleable for groups. Recommend (b).  
Notes: adds 4 sites to the "parser populated / render discarded" ledger (over, rev, val, qual per group × 8 subgroups).

**B62 — `hist.grp` pipeline (companion to B6 `hist.reg` blocker).**  
Size: M parser + S render.  
Currently parser writes `hist:{summary, fac, sec:{}, reg:{}}` — no `grp` key. Blocks:  
- cardGroups sparkline column  
- `oDrGroup` historical active-weight chart + range selector  
Batch with B6 as "hist.geo/grp/reg parser pass" — same shape, same cost.

**B63 — `oDrGroup` drill parity uplift.**  
Size: M.  
Mirror `oDr('sec',n)` drill: historical chart (needs B62), range selector, rank dist, factor tilt summary, bench-only holdings section. Bench-only table addable today (no deps).

**B64 — Rank-mode toggle per tile (global state split).**  
Size: S. Parent item already tracked for sectors+country+groups+regions shared `_secRankMode`. If PM wants cardGroups to bucket by FactSet's exclusive subgroups while cardSectors stays weighted-portfolio, toggle needs per-tile state. Re-raise only if B61 is resolved via (b).

**B65 — Cross-tile sweep: carry forward `h.subg` as authoritative for cardTreemap's Group-by toggle.**  
Size: S.  
cardTreemap L2610 currently silent-dead on Group-by because audit team believed `h.subg` was unpopulated. New finding here contradicts that (see §1.2). Unblocks cardTreemap D1 trivially. Batch with T-series cardTreemap fixes on next Treemap touch.

**B66 — PNG removal audit across all tiles.**  
Size: XS. User pref "no PNG on RR tiles" (MEMORY). Known offenders: cardRegions, cardGroups, probably cardTreemap + cardCorr. Sweep + remove. Low-risk single-session edit.

**B67 — cardGroups drill `plotly_click` + row `tabindex`/`role` for keyboard a11y.**  
Size: S. Tile-wide keyboard hook same shape as cardFRB pattern. Batch with B67-class a11y sweep when PM prioritizes.

**B68 — GROUPS_DEF vs h.subg reconciliation (config truth).**  
Size: S.  
Document decision: is Redwood's taxonomy **the GROUPS_DEF overlap view** (Info Tech contributes to both GROWTH and GROWTH CYCLICAL) or **FactSet's exclusive subg view** (each holding in one bucket)? Current code is schizophrenic: the rank loop uses overlap, the drill holdings-list uses the sector membership of overlap groups (actually broken per T3), and the `cs.groups[].p/b/a` values are exclusive (sum to ~97%). This config ambiguity is the upstream cause of B61 + T3. Needs a PM decision memo before B61 lands.

---

## Section 6 · Cross-tile learnings (append to AUDIT_LEARNINGS.md)

### (a) Update: `h.subg` IS populated in current FactSet exports

AUDIT_LEARNINGS.md L13 + L63 state `h.subg` is undefined. **Contradicted by latest_data.json** (2026-04-23 probe, all 7 strategies, ~85% of non-cash holdings have `h.subg`). FactSet's `SEC_SUBGROUP` column IS shipping. This reshapes:
- cardTreemap D1 Group-by toggle (blocker removed — B65)
- cardGroups rank aggregation (new B61 fix path)
- General: any tile that needs "Redwood bucketing" can read `h.subg` directly instead of reconstructing from GROUPS_DEF.

Recommend the main session verify on its own browser open and update the ledger.

### (b) New anti-pattern: client-side-reconstructed taxonomy diverging from source taxonomy

Related to but distinct from Pattern B (parser-populated → normalize-discarded). Here the parser populates correctly AND the holdings carry authoritative labels (`h.subg`), yet the render reconstructs the mapping locally via a legacy config (`GROUPS_DEF + SEC_ALIAS`) that disagrees with source. Symptoms:
1. Sector-alias-normalization can be forgotten in one spot but not another (cf. `oDrGroup` drill, T3 above).
2. Overlap vs exclusive bucketing silently diverges.
3. Numeric ranks (or counts, sums, active weights) come out wrong without any visible error.
Detection heuristic: if render-code has a config constant whose entries overlap with fields already on the data model (here: `h.subg` vs GROUPS_DEF), grep every usage for consistency with source. Decide which is truth and enforce.

### (c) Data pipeline layering clarification

Revised per this audit: the three layering patterns are now:
1. **Pattern A — "`hist.X:{}`"** — parser writes empty dict, render can't display. (hist.reg, hist.grp, hist.country; only hist.sec partially populated.)
2. **Pattern B — "parser-populated, normalize-discarded"** — parser fills, normalize() overwrites. (cardRanks: `s.ranks`.)
3. **Pattern C — "render-side re-derivation from wrong config"** — parser fills, render ignores and recomputes via legacy lookup that disagrees with source. (cardGroups: ORVQ ranks, this audit.)

### (d) Groups-of-groups naming collision

`GROUPS_DEF` defines 5 top-level groups (CYCLICALS, DEFENSIVE, GROWTH, COMMODITY, RATE SENSITIVE) and 8 subgroups. "GROWTH" and "DEFENSIVE" appear as BOTH a top-level group and a subgroup. `cs.groups[].n` (from FactSet) contains subgroup-level names. Code like `GROUPS_DEF.filter(gd => gd.sg === groupName || gd.g === groupName)` would match ambiguously. cardGroups drill today only tests `gd.sg` (L5464), which disambiguates correctly; no bug, but future-fragile. Flag for any refactor that wants to support the 5-group parent taxonomy.

### (e) Dataset-driven audits are high-ROI

This audit's RED finding (§1.3) was only visible by running numeric comparison against latest_data.json. Previous siblings audited without a data probe missed this class. Suggestion for future audits: always run at least one "parser value vs rendered value" spot-check when the render re-computes from holdings data that parser already aggregated. Add as a step in the audit skill.

### (f) Completed audits entry

- ✅ cardGroups (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top finding = render recomputes ORVQ ranks via wrong (non-exclusive) GROUPS_DEF taxonomy, silently mis-reporting HARD CYCLICAL as Q1 when FactSet says Q3; dead `oDrGroup` drill filter for Info Tech/Comm Services/Consumer Disc. (T3); `h.subg` populated contradicts earlier ledger; trivial fix queue of 10 (T1–T10), non-trivial 8 (B61–B68))

---

## Fix queue summary (for coordinator)

**TRIVIAL (10, agent can apply inline):** T1 (note hook + card-title tip), T2 (threshold row classes), **T3 (dead-drill fix — ship-blocking)**, T4 (data-sv on null cell), T5 (tokenize null color), T6 (remove PNG item), T7 (plotly_click on chart), T8 (data-col sweep), T9 (R/V/Q tooltips), T10 (dead-code cleanup).

**NEEDS PM DECISION (4):** B61 (which taxonomy = truth), B64 (split rank-mode state), B68 (GROUPS_DEF reconciliation memo), §3.2 (overlap disclaimer).

**BLOCKED / BACKLOG (4):** B62 (hist.grp parser), B63 (drill parity — depends on B62), B65 (cardTreemap Group-by unblock), B66 (PNG sweep), B67 (a11y sweep).

---

**File:** `/Users/ygoodman/RR/tile-specs/cardGroups-audit-2026-04-23.md`  
**Dashboard untouched.** Main session serializes all code changes.
