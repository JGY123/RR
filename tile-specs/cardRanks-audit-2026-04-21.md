# Tile Audit: cardRanks — Quant Ranks

> **Audited:** 2026-04-21 | **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html` (6,501 lines) | **Parser:** `factset_parser.py`
> **Methodology:** 3-track audit per `tile-audit-framework` + `AUDIT_LEARNINGS.md`
> **Sibling context:** Batch 3 — pairs with `cardChars` (already audited) in the same `g2` row; neighbors `cardScatter` + `cardTreemap` on Row 7

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Quant Ranks |
| **Card DOM id** | `#cardRanks` |
| **Render function** | `rRnk(s.ranks)` at `dashboard_v7.html:L1797–L1801` |
| **Inline HTML** | `L1239–L1243` |
| **Drill function** | **None** — click calls `filterByRank(rank)` at L1802–L1811 which navigates to the Holdings tab and sets the rank filter dropdown |
| **Companion chart** | `rRankDist()` at L3922–L3929 → `#rankDistDiv` on the Holdings tab (uses same `cs.ranks`, different tile) |
| **Tab** | Exposures (first tab) |
| **Grid row** | Row 6 of Exposures — paired with `cardChars` in `g2` |
| **Width** | Half (`g2`) |
| **Owner** | CoS / main session |
| **Spec status** | `draft` → this audit promotes to signed-off once trivial queue applied |

---

## 1. Data Source & Schema — TRACK 1 (Data Accuracy)

**Section grade: YELLOW** — rendered values are internally consistent, but the tile ignores FactSet's authoritative pre-aggregated rank table and re-aggregates from holdings with a lossy derivation. Two silent data-drop paths identified.

### 1.1 Primary data source (rendered)

- **Rendered path:** `cs.ranks[]` — 5-element array, one entry per quintile 1..5.
- **Shape:** `[{r:int(1-5), l:'Quintile N', ct:int, p:float, a:float}, ...]`
- **Construction site:** `normalize()` at `dashboard_v7.html:L613` — NOT the parser.
- **How it's built:**
  ```js
  st.ranks = [1,2,3,4,5].map(r => {
    let hh = st.hold.filter(h => h.r === r);
    return {
      r, l: 'Quintile ' + r,
      ct: hh.length,
      p:  +hh.reduce((a,h)=>a+(h.p||0), 0).toFixed(2),
      a:  +hh.reduce((a,h)=>a+(h.a||0), 0).toFixed(2),
    };
  });
  ```
- **Upstream field — `h.r` on holdings:** set in `normalize()` L571:
  `if(hn.r==null && hn.over!=null) hn.r = Math.round(Math.min(5,Math.max(1, hn.over)));`
  — a rounding of the continuous `OVER_WAvg` (1.0–5.0 quintile score) to nearest integer.

### 1.2 FactSet source-of-truth — NOT USED

- The FactSet CSV ships a dedicated **Overall rank section** (SCHEMA_COMPARISON.md L171–L202): 5 quintile rows carrying `W`, `BW`, `AW` pre-aggregated by FactSet.
- The parser extracts this correctly into `ranks.overall[{q,w,bw,aw}]` (factset_parser.py:L709–L730), plus separate `rev/val/qual` rank tables.
- **`normalize()` throws this entire dict away** (L612 comment: "parser ranks dict has randomized q values") and rebuilds from holdings.
- The "randomized q values" comment refers to FactSet's Level2 being a decimal like `"1.239"` rather than a clean `"Q1"`; that's a 1-line rounding fix in the parser, not a reason to discard the whole pre-aggregated table.

**Impact of ignoring the parser table:**
1. `REV / VAL / QUAL` rank distributions never land on the dashboard at all — the parser extracts them, no tile consumes them.
2. Any holding with `h.over == null` has `h.r` stay `null` and silently falls out of the quintile totals (rank column in `Port%` + `Count` + `Active%` will be short the unranked rows).
3. `W`, `BW`, `AW` from FactSet are never cross-checked against the holdings-based aggregation — if they diverge, we have no telemetry.

### 1.3 Field inventory (4 rendered columns)

| # | Label | Field | Type | Source | Formatter | Sort | Click |
|---|---|---|---|---|---|---|---|
| 1 | Rank | `r.l` ("Quintile N") + colored text via `rc(r.r)` | string | `normalize()` literal | — | `sortTbl('tbl-rnk',0)` via `data-sv="${r.r}"` | row → `filterByRank(r.r)` |
| 2 | Count | `r.ct` | int | `hh.length` | raw int | col 1 via `data-sv="${r.ct}"` | row |
| 3 | Port% | `r.p` | number | Σ `h.p` for `h.r === r` | `f2(v) + '%'` (2 dp implied, f2 default) | col 2 via `data-sv="${r.p}"` | row |
| 4 | Active% | `r.a` | number \| null | Σ `h.a` for `h.r === r` | `f2(v)+'%'` or `'—'` | col 3 via `data-sv="${r.a??0}"` | row |

### 1.4 Ground truth verification

- [x] Parser writes `s.ranks.overall/rev/val/qual` with Level2 as decimal quintile string (factset_parser.py:L709–L730). Traced.
- [x] `normalize()` OVERWRITES `s.ranks` on every load, so the parser-side dict is unreachable from rendering.
- [x] `h.r` derivation from `h.over` via `round(clamp(over,1,5))` — loses sub-quintile resolution; a 1.45 and a 2.35 both collapse to Q2.
- [x] `rc(r)` at L492 uses tokenized `--r1..--r5` CSS vars — design-token clean.
- [x] `rankDistDiv` on Holdings tab uses same `cs.ranks` — no parallel rebuild, good.
- [ ] **Spot-check against raw CSV pending loaded JSON** (see AUDIT_LEARNINGS §Known blockers). Particularly: does the holdings-based `Σ h.p` for Q1 match FactSet's `Overall` section `W` for Q1? If yes, the trashing is cosmetically forgivable. If no, we're shipping silently wrong data.

### 1.5 Missing / null handling

| Scenario | Current behavior | Adequate? |
|---|---|---|
| `ranks` is `[]` (shouldn't happen — always length 5) | Renders "No rank data" | defensive OK |
| A quintile has zero holdings | Renders row with `Count=0`, `Port%=0.00%`, `Active%=0.00%` | **minor** — renders "0.00%" rather than em-dash; could look misleadingly "present" |
| `h.r == null` (holding has no `over`) | Holding is silently excluded from all 5 quintiles — counts/weights **under-sum** | **GAP** — no "Unranked: N holdings" row; user has no way to see how many holdings are off-the-grid |
| `h.p` is NaN | `(h.p \|\| 0)` coerces to 0 | OK |
| `h.a == null` (cash-only rank?) | `r.a` accumulates 0s; the per-row `r.a??0` shows as 0.00% not em-dash | inconsistent with per-holding convention elsewhere |

---

## 2. Columns & Dimensions Displayed

4 columns, 5 rows (always). No pagination, no filtering, no column picker.

| # | Label | Data-sv | Sort | Filter | Hide | Tooltip | Click target |
|---|---|---|---|---|---|---|---|
| 1 | Rank | `r.r` | yes | — | no | **none** | row → holdings tab filtered to this rank |
| 2 | Count | `r.ct` | yes | — | no | **none** | row |
| 3 | Port% | `r.p` | yes | — | no | **none** | row |
| 4 | Active% | `r.a??0` | yes | — | no | **none** | row |

Notable: **zero `data-col` attributes** on any `<th>` / `<td>` (prerequisite for a future column-picker per AUDIT_LEARNINGS primitives checklist). Zero header tooltips — `cardSectors` gold standard has every numeric header wired with `class="tip" data-tip="..."`.

---

## 3. Visualization Choice

### 3.1 Layout
Simple 4-col HTML table. The visual encoding lives in the colored quintile label (Q1 green → Q5 red via `rc()`).

### 3.2 Color semantics
- Rank label color: `--r1` (green) → `--r5` (red). **Tokenized, theme-aware.** Good.
- Count / Port% / Active% cells: default text color. No positive/negative coloring on Active% even though it clearly can be negative. Inconsistent with e.g. `cardSectors` Active% which colors by sign.

### 3.3 Empty state
`<p style="color:var(--txt);font-size:12px">No rank data</p>` — present. Same convention as cardChars, cardSectors. Good.

### 3.4 Responsive
Table inherits base responsive behavior; grid collapses `g2` → single column on narrow viewports.

### 3.5 No visual encoding of weight magnitude
`cardSectors` draws an inline gradient bar on the TE% column to visualize magnitude. `cardRanks` has no such bar for `Port%` — the data is **very** well-suited to a bar-in-cell treatment since weights sum to ~100% and ordering is inherent.

---

## 4. Functionality Matrix — TRACK 2 (Parity)

**Section grade: YELLOW** — basic primitives present, but tooltips / sort-correctness / Active% coloring / note-badge wiring / data-col attrs all missing vs cardSectors gold standard.

| Capability | cardSectors (gold) | cardRanks (current) | Gap? |
|---|---|---|---|
| Stable `<table id>` | `tbl-sec` | `tbl-rnk` | — |
| `<th>` sortable | all columns | all 4 | — |
| `data-sv` on numeric cells | yes, clean | yes — but `r.a??0` coerces nulls | minor (nulls don't occur in practice since `r.a` is a sum, but convention) |
| `data-col` on `<th>` + `<td>` | partial (sectors branch only) | **none** | **GAP** — prerequisite for future column-picker |
| `class="clickable"` + onclick | yes → `oDr('sec',n)` | yes → `filterByRank(r.r)` | — different drill target but present |
| Row drill opens modal | yes (modal) | **no — navigates to Holdings tab** | intentional divergence (see §5) |
| Empty-state fallback | yes | yes | — |
| Header tooltips (`tip` + `data-tip`) | all numeric cols | **none** | **GAP** — Port%, Active%, Count, Rank all bare |
| Card-title tooltip | yes | yes ("Click a rank to filter the Holdings tab") — accurate | — |
| Right-click note on card title (`oncontextmenu="showNotePopup(event,'cardRanks')"`) | yes (cardFacButt, cardFacDetail, cardFRB) | **none** | trivial missing wire |
| CSV export | yes | yes (`exportCSV('#cardRanks table','ranks')`) | — |
| PNG export | yes | **yes — violates `feedback_no_png_buttons`** (L1241 `screenshotCard('#cardRanks')`) | **REMOVE** |
| Active% sign color (pos/neg) | yes on cardSectors Active col | **no** — plain default text | GAP |
| Threshold row classes (`thresh-alert` / `thresh-warn`) | yes | none | **N/A** for rank rows — rank itself encodes risk via color; active-% overweight on Q5 already surfaced by the cardThisWeek Q5 alert (L860) |
| Inline magnitude bar on Port% | yes on TE% in countries/sectors | **none** | nice-to-have |
| Drill-modal | yes | no (filter navigation instead) | see §5 |
| Full-screen modal | N/A for a 5-row table | N/A | — |
| Count of unranked holdings | N/A | **none** | new gap — a "Q? / Unranked: N" footer row would surface data-drop honestly |
| Theme-aware colors | yes | yes (`--r1..--r5`, `--txt`) — clean | — |

### 4.1 Sort anti-pattern check (per AUDIT_LEARNINGS)

- `data-sv="${r.r}"` — OK (integer 1..5, never null).
- `data-sv="${r.ct}"` — OK (integer, ≥ 0).
- `data-sv="${r.p}"` — OK (non-null by construction; reduce on `(h.p||0)`).
- `data-sv="${r.a??0}"` — same ??0-coerces-null pattern as cardChars / cardFactors / cardRanks-factors line flagged in AUDIT_LEARNINGS §Sort anti-patterns. In practice `r.a` is never null here (it's a reduce), but the pattern should be `??''` for consistency. Trivial.

### 4.2 Drill behavior review

Click target: **`filterByRank(rank)`** (L1802–L1811). Unlike every sibling tile, this does NOT open a modal. Instead:
1. Sets `activeTab='holdings'`.
2. Activates the Holdings tab DOM (hardcoded index `document.querySelectorAll('.tab')[2]` — fragile, breaks if a tab is reordered or inserted).
3. Filters `fh` client-side to `h.r === rank`.
4. Resets pagination `hp=1`, re-renders.
5. `setTimeout(100)` to set `$('rankFilter').value = rank` — timing hack for a dropdown that already exists on the rendered Holdings tab.

**Gotchas:**
- **Magic tab index `[2]`** — if a PM ever inserts a tab before Holdings, this silently filters the wrong tab. Symbolic lookup (`document.getElementById('tab-holdings-btn')` or filtering by text) would be safer.
- **`setTimeout(100)` is a race** — if the Holdings tab's render takes >100ms (e.g., large holdings table + sparklines), the dropdown's value set-call fires before the DOM node exists. Fail-silent; the filter still works because `fh` is already filtered, but the dropdown's visible value desyncs.
- **`ah=[...cs.hold]`** (L1808) resets the Holdings tab's local "all holdings" state but also clobbers any active sector/search filter the user had set on that tab. Feels like a filter-navigation bug (worth flagging to PM): user clicks Q5 from Exposures tab → their Holdings sector filter silently disappears.
- **No way to clear** — once filtered by rank, the user has to manually blank the `rankFilter` dropdown; the rank row's visual state doesn't persist or indicate "you are filtered by this".

**Compared to modal drills (cardSectors, cardFRB):** different paradigm, both valid. The filter-navigation approach has merit — rank = a real dimension in the Holdings table — but it needs: (a) keyboard accessibility, (b) a way to return to the previous tab context, (c) a visible "filtered by rank Q3" breadcrumb. None present.

---

## 5. Popup / Drill / Expanded Card

No modal. The tile's "drill" is tab navigation to Holdings with `rankFilter` set. See §4.2.

**Not wired that siblings have:**
- `oncontextmenu` for the card-title right-click note popup.
- Keyboard access (rows are `<tr class="clickable">` with `onclick` but no `tabindex` or `onkeydown` — Enter/Space can't trigger them).

---

## 6. Design Guidelines — TRACK 3 (Consistency)

**Section grade: YELLOW** — visual base is clean and token-aware, but lacks the depth (tooltips, sign color, inline magnitude bar) of gold-standard tiles.

### 6.1 Density
Inherits base table (`<th>` 10px, `<td>` 11px). Consistent with cardSectors / cardHoldings / cardChars.

### 6.2 Color tokens
- Rank labels: `var(--r1..--r5)` — clean tokens. Good.
- Every other cell: `var(--txt)` default — consistent.
- **No hardcoded hex in rRnk.** Win.

(Contrast: `renderHoldTab` L5954 still hardcodes `#059669 / #dc2626 / #d97706` for rank column in rendered holdings rows. Not this tile's problem but worth queuing under a sweep — same `h.r` data, should use `rc()` too.)

### 6.3 Alignment
- Rank label: default (left). Count / Port% / Active%: right (`class="r"`). Consistent with table convention.
- Rank label `<span>` has `font-weight:600` inline. cardSectors' "name" column uses `color:var(--txth)` (heading color) for emphasis. Minor inconsistency — rank label uses color for emphasis (the quintile-color gradient), cardSectors uses weight + `--txth`. Both valid; not worth harmonizing.

### 6.4 Whitespace / spacing
Card padding consistent with sibling cardChars in the same `g2` row.

### 6.5 Tooltips
**Zero header tooltips.** Every numeric column should have `class="tip" data-tip="..."` per AUDIT_LEARNINGS §Design. Missing on Count, Port%, Active%, Rank. Trivial.

### 6.6 Motion / interaction feedback
- Rows are `.clickable` (inherits hover bg, cursor:pointer) — OK.
- No focus ring (no `tabindex`); keyboard a11y is zero.

### 6.7 Hardcoded hex audit
Clean inside `rRnk`. One flag in the related holdings table at L5954 (`#059669` / `#dc2626` / `#d97706`) — out of scope for this audit but documented for cross-tile sweep.

---

## 7. Known Issues & Open Questions

| # | Finding | Class | B-id |
|---|---|---|---|
| 1 | **Parser ranks dict is completely discarded** (factset_parser.py:L751–L756 → normalize L612). FactSet's pre-aggregated `Overall / REV / VAL / QUAL` `{q,w,bw,aw}` never reaches any tile. | non-trivial | **B29** |
| 2 | Rebuild-from-holdings silently drops holdings where `h.r == null` (no `over`). No "Unranked: N" footer or warning. | non-trivial | **B30** |
| 3 | `filterByRank` uses magic tab index `[2]` + `setTimeout(100)` race. Fragile on tab reorder and async Holdings-render. | non-trivial | **B31** |
| 4 | `filterByRank` clobbers any pre-existing sector/search filter on the Holdings tab (`ah=[...cs.hold]`). User loses context. | non-trivial | **B32** |
| 5 | No `REV / VAL / QUAL` quintile tiles exist — parser extracts them, tiles don't consume. | non-trivial | **B29** (folds into #1) |
| 6 | No drill modal / no "filtered by rank" breadcrumb once Holdings view is filtered. User has no visible exit path other than manually clearing the dropdown. | non-trivial | **B33** |
| 7 | Header tooltips missing on all 4 columns. | trivial | — |
| 8 | PNG export present in the download dropdown (L1241) — violates `feedback_no_png_buttons`. | trivial | — |
| 9 | No `oncontextmenu="showNotePopup(event,'cardRanks')"` on card-title. | trivial | — |
| 10 | `data-sv="${r.a??0}"` uses `??0` (sort anti-pattern per AUDIT_LEARNINGS). | trivial | — |
| 11 | No `data-col` on `<th>` or `<td>` (blocks future column-picker). | trivial | — |
| 12 | No keyboard a11y on rows (`tabindex="0"` + `onkeydown`). | trivial | — |
| 13 | Active% column doesn't sign-color (positive green / negative red) like cardSectors does. | trivial | — |
| 14 | Empty quintiles render as "0.00%" not "—", can look like a filled row. | trivial | — |
| 15 | Card is not `tabindex="0"` / keyboard-activatable at the card level, but it's not a whole-tile click target either — rows are — so this is low priority. | info | — |

---

## 8. Verification Checklist

- [x] Data path traced (parser → normalize → render).
- [x] Data shape confirmed: 5-element array `{r,l,ct,p,a}`.
- [ ] **Spot-check vs loaded JSON pending** — specifically: does `Σ h.p for h.r===1` match the parser's `ranks.overall[]` row where `round(q)===1`'s `w`?
- [x] Empty state: `No rank data` present (defensive — array is always length 5).
- [x] CSV export: `exportCSV('#cardRanks table','ranks')`.
- [ ] PNG export present — must be removed.
- [x] Rank color via `rc()` → `--r1..--r5` tokens: theme-aware.
- [ ] No `oncontextmenu` wired on card-title for notes.
- [ ] Sort on Active% uses `??0` fallback.
- [ ] No `data-col` / column-picker infra.
- [ ] No header tooltips.
- [ ] No `tabindex` / keyboard on rows.
- [x] Drill navigates to Holdings tab with filter set (works, modulo race + filter-clobber).
- [x] Rank distribution companion chart (`rRankDist`) uses same `cs.ranks` — no data drift.
- [ ] No console errors — not testable in audit env.

---

## 9. Related Tiles

- **cardChars** — paired in same `g2` row; independent data source (`cs.chars`).
- **cardThisWeek** — renders a **Q5 overweight alert** (L860) using the same `h.r===5` derivation. If #2 above is fixed by preferring parser data, that alert should too.
- **Holdings tab → `rankDistDiv`** — bar-chart companion of `cs.ranks`. Same data, different encoding. No divergence.
- **`renderHoldTab` / holdings row** — renders `Q{h.r}` cell with hardcoded hex colors (L5954). Cross-tile color-consistency sweep candidate.
- **cardTreemap** — has a `Group: Rank` dim option that buckets holdings by `h.r` (L1266). Same derivation; same data-drop risk for unranked holdings.
- **cardScatter** (L5623): hardcoded rank color palette (`#10b981 / #34d399 / #f59e0b / #fb923c / #ef4444`) — should use `rc()` tokens. Flag for cross-tile sweep.

---

## 10. Proposed Fix Queue

### TRIVIAL (agent can apply in one sweep, < 20 min total)

1. **Remove PNG export** — L1241: drop `screenshotCard('#cardRanks')` and collapse the download dropdown to a single CSV button.
2. **Add header tooltips** on all 4 `<th>`. Suggested copy:
   - Rank: "Quintile bucket. Q1 = best-ranked by overall quant score, Q5 = worst."
   - Count: "Number of portfolio holdings in this quintile."
   - Port%: "Sum of portfolio weights in this quintile."
   - Active%: "Sum of active weights (portfolio − benchmark) in this quintile."
3. **Add `oncontextmenu="showNotePopup(event,'cardRanks');return false"`** on the card-title `<div>` — matches cardFacButt / cardFacDetail / cardFRB convention.
4. **Fix `data-sv="${r.a??0}"` → `data-sv="${r.a??''}"`** per AUDIT_LEARNINGS sort anti-pattern.
5. **Add `data-col="rank|count|port|active"`** on all `<th>` + `<td>` — prereq for column-picker.
6. **Sign-color the Active% cell** — `class="r pos"` if `r.a > 0`, `class="r neg"` if `r.a < 0`. Use existing `.pos / .neg` CSS classes.
7. **Em-dash empty quintiles** — if `r.ct===0`, render `Port%` and `Active%` as `—` rather than `0.00%`.
8. **Add row `tabindex="0"` + `onkeydown` for Enter/Space** → `filterByRank(r.r)`. Keyboard parity.
9. **Fix magic-index `document.querySelectorAll('.tab')[2]`** → look up Holdings tab by a stable selector (e.g. `document.querySelector('[data-tab-id="holdings"]')` if one is added, or a querySelectorAll → find by text). 2-line change; avoids fragility when tabs get reordered.

### NEEDS PM DECISION

10. **Should `filterByRank` preserve existing Holdings-tab filters** (sector search + text), or intentionally reset? Current behavior quietly resets — PM call on whether that's the product intent.
11. **"Unranked: N" row** — when some holdings have `h.r == null`, should the tile surface them as a 6th row or a small sub-caption? Hiding them is currently lossy.
12. **REV / VAL / QUAL quintile tiles** — should we add sibling tiles for the other three rank dimensions (FactSet already ships the data), or is Overall sufficient for the PM workflow?

### NON-TRIVIAL (backlog-worthy)

- **B29** — Use FactSet's pre-aggregated rank tables as source-of-truth. Parser returns `ranks.overall/rev/val/qual` with `{q,w,bw,aw}`; round `q` to int and consume directly. Adds a check: holdings-derived aggregation should match parser `overall.w` per quintile; surface divergence as a data-quality warning. Also unblocks REV/VAL/QUAL tiles (item 12). ~30–50 LOC across parser + normalize + rRnk. Est. 1–2 hours.
- **B30** — "Unranked holdings" affordance. Surface `hold.filter(h=>h.r==null).length` either as a 6th row or as a subtitle under the card. ~10 LOC. Depends on PM call (item 11).
- **B31** — Robust tab navigation in `filterByRank`. Replace magic index + `setTimeout(100)` with symbolic lookup + a proper Promise/callback from `renderHoldTab`. ~15 LOC. Low risk.
- **B32** — Filter preservation on rank-drill. If PM chooses "preserve", change `ah=[...cs.hold]` → leave `ah` alone; or snapshot + restore via a "Back to previous view" chip. ~20 LOC.
- **B33** — Drill breadcrumb / exit affordance on the Holdings tab when navigated from rank filter. Visible chip "Filtered: Q3 (clear)". ~15 LOC.

---

## 11. One-line overall rating

**YELLOW / YELLOW / YELLOW** — data path works but throws away FactSet's authoritative pre-aggregated ranks; functional parity trails cardSectors on tooltips / data-col / a11y / note badge; design tokens clean but Active% column doesn't sign-color. Five non-trivial items queued as **B29–B33**.

---

## 12. Sign-off

**Status:** `draft` — promote to `signed-off` after trivial items 1–9 applied. Non-trivial items are backlog (B29–B33); B29 is the highest-value since it both fixes lossy aggregation AND unblocks REV/VAL/QUAL tiles.

**Grades:**
- §1 (Data Accuracy): **YELLOW** — rendered path is consistent but ignores source-of-truth; two silent data-drop paths.
- §4 (Functionality Parity): **YELLOW** — basics present, 9 trivial gaps vs gold standard, drill-as-tab-nav has fragility.
- §6 (Design Consistency): **YELLOW** — tokens clean, but zero header tooltips, no sign-color on Active%, no keyboard a11y.
