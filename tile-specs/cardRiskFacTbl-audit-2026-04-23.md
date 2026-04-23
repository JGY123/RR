# Tile Audit — cardRiskFacTbl

**Audit date:** 2026-04-23
**Auditor:** tile-audit subagent
**Tag target:** `tileaudit.cardRiskFacTbl.v1`
**Batch:** 4 (continuation — Risk-tab sweep after cardMCR/cardAttrib/cardCorr)
**CRITICAL CONSTRAINT:** Audit-only. No edits to dashboard_v7.html.

---

## Section 0 · Identity

| Field | Value |
|---|---|
| Tile name | **Factor Exposures — click row for time series drill** (Risk tab) |
| Card DOM id | `#cardRiskFacTbl` |
| Shell location | dashboard_v7.html L3137 |
| Table id | `#tbl-risk-fac` |
| Render function | inline inside `rRisk()` at L2983 (no dedicated renderer fn) |
| Row producer | `facMCR` at L2994–L2999 |
| Drill handler | `oDrFRisk(name)` at L3513 |
| Data source | `cs.factors[]` (parser `_build_factor_list`, factset_parser.py L847–865) |
| Sparkline source | `cs.hist.fac[f.n]` (parser `_build_hist_fac`, factset_parser.py L938–949) |
| Tab | Risk (7th tab) |
| Width | full (single column — sits stacked below the Factor Contributions bars card at L3087) |
| Sibling tiles on Risk tab | Risk-tab factor cards: **Factor Contributions bars** (L3087, no id), **Factor Exposure History** (L3164, no id), **Factor Correlation Matrix** (L3177, **this is the live cardCorr** — audit 2026-04-23), **Risk Decomp Tree**, **TE Stacked Area**, **Beta Multi** |
| Sibling cardFacDetail (Attribution tab) | L1163 — separate factor-detail tile with Primary/All toggle, group pills, full-screen, PNG/CSV dropdown |

---

## Section 1 · Data accuracy — **RED**

### 1.1 Field inventory

| # | Column | Source | Format | Sort | What it actually is |
|---|---|---|---|---|---|
| 0 | Factor (n) | `f.n` | text | yes (alpha) | factor name |
| 1 | Exposure | `facMCR.e` ← **`f.a` at L2998** | `fp(_,3)` | yes (data-sv) | **ACTIVE exposure (e−bm)** — but header says "Exposure", ambiguous |
| 2 | Contrib % | `facMCR.c` = `f.c` | `f2(_,1)` | yes | `f.c` is *% of portfolio TE* (per CLAUDE.md + cardFRB audit), but header says "Contrib %" with no `%` of what denominator |
| 3 | MCR to TE | `facMCR.mcrTE = totalTE * \|f.c\| / 100` L2996 | `f2(_,3)` | yes | **sign-collapsed** via `Math.abs(f.c)`; TE attributed to factor — units: TE units |
| 4 | Return % | `f.ret` | `fp(_,2)` | yes | factor return period — green/red by sign via inline style |
| 5 | Impact | `f.imp` | `fp(_,2)` | yes | return impact (`imp = ret × exposure_like`, snap field) — green/red by sign |
| 6 | Trend | `mkSparkline(sparkVals,60,22,null)` | SVG | **no sort** (correct — non-sortable) | **See 1.3 below — this is the bug** |

### 1.2 Cell coloring

Row-level color at L3147: `let cls=f.e!=null?(f.e>0?'pos':'neg'):''` — applied to the Exposure cell (td.r.pos / td.r.neg via global CSS). Because `f.e` here is the object field `facMCR.e` which was aliased from `f.a` (active), the coloring correctly reflects active positive/negative — but the **column header still says "Exposure" which reads as *raw* in every other risk context**. Label is the issue, not the value.

Return % and Impact cells do sign-coloring inline via `style="color:var(--pos|neg)"` — redundant with the .pos/.neg class pattern used on the Exposure cell. Two mechanisms for the same job.

### 1.3 **Active-vs-raw conflation — 3rd site confirmed**

This tile is the third confirmed site of the active-vs-raw conflation AUDIT_LEARNINGS flagged at cardFacDetail L1764 and cardCorr L2168. The conflation here is **within a single row**:

**Exposure cell (L3152):** value is `f.a` (active), header reads "Exposure".

**Trend sparkline cell (L3149):**
```js
let sparkVals = facHist ? facHist.map(h => h.bm!=null ? +(h.e-h.bm).toFixed(4) : (h.e||0)) : [];
```
— computes active if `h.bm != null`, falls through to raw `h.e` otherwise.

**But** `_build_hist_fac` at factset_parser.py L938–949 always writes `"bm": exp.get("bm")` where `exp` comes from riskm_rows at L460–469. And the riskm path at L468 sets `entry["exposures"][fname] = {"c": c_val, "a": a_val, "e": c_val, "bm": None}` — **`bm` is hardcoded `None` in the riskm path**. So for every factor whose history comes from riskm rows (which is the path used for Risk-tab data), `h.bm` is `None` and the sparkline falls through to the `h.e||0` branch — which is the **raw port exposure**, *not* active.

**Net:** the Exposure column shows **active**, the Trend sparkline right next to it shows **raw**. They will diverge any week the benchmark has non-zero exposure to the factor (which is every week for primary factors). No user can tell from the UI.

**Second-order bug at L3573 inside `oDrFRisk`:**
```js
let rfAnno=[{..., y:last.e||last.a, text:'Current: '+(last.e||last.a).toFixed(3), ...}];
```
Uses `last.e` (raw) with `||last.a` (active) fallback — same conflation carried into the drill annotation. And the y-axis title is `'Exposure'` at L3585 while the trace name at L3583 is `'Active Exposure'`. Self-contradicting within the same chart.

### 1.4 **Sign-collapse on MCR to TE (same shape as cardFRB bug)**

L2996:
```js
let mcrTE=+(totalTE*contrib/100).toFixed(3);   // contrib = Math.abs(f.c||0)
```
Every MCR-to-TE cell in the table loses the sign of `f.c`. A factor diversifying the portfolio (negative TE contribution) reads identical to a risk-adding factor of the same magnitude. Same anti-pattern AUDIT_LEARNINGS flagged at cardFRB L2696 + `oDrRiskBudget` L5389 + Risk Decomp Tree L2770. **This is the fourth site.** The row-click drill at `oDrFRisk` L3526 repeats the `Math.abs(factor.c||0)` on the KPI card.

### 1.5 Devs-over-TE (computed but unused in table)

L2997: `devPct = f.dev/totalTE*100` is computed, attached to `facMCR[].devPct`, but never rendered in this table. It's consumed only by `rRiskFacBarsMode` shadow-bar (L3313–3320). Harmless but worth noting as dead payload here.

### 1.6 Empty-state missing

No empty-state fallback if `s.factors` is empty. `facMCR.map(...)` produces an empty `<tbody>` and the card renders with just headers and no "No factor data" message. Every other factor table in the file has one (L1725, L1730, L2415, L2815, L3471, L5658). One-line fix.

### 1.7 Week-selector silence

`rRisk()` L2984 reads `cs` directly (`let s=cs`), never consults `getSelectedWeekSum()`. `cs.factors` is always the latest-week list; `cs.hist.fac` is populated but `cs.factors` itself has no per-week snapshot. When a user selects a historical week via the header chevrons, the amber banner promises historical data but **this tile silently keeps showing latest factor exposures and latest TE**. Same divergence AUDIT_LEARNINGS flagged cross-tile (per "Factor-family patterns" entry — confirmed now for this tile).

### 1.8 Spot-check pending

Spot-check of 3–5 factor rows against FactSet raw requires a loaded JSON. Flag as pending per known-blocker convention.

**Section 1 verdict: RED.** Two distinct correctness bugs in the same row (active-vs-raw between Exposure and Trend cells, sign-collapse on MCR to TE) + header mislabel + silent week-selector divergence.

---

## Section 2 · Functionality parity — **YELLOW**

Benchmark: cardFacDetail (L1163) as the feature-rich factor-table sibling.

| Capability | cardFacDetail | cardRiskFacTbl | Gap? |
|---|---|---|---|
| Stable card id | yes (`#cardFacDetail`) | yes (`#cardRiskFacTbl`) | — |
| Stable table id | yes | yes (`#tbl-risk-fac`) | — |
| Every sortable `<th>` wired | yes | yes (6 cols; Trend intentionally not sortable) | — |
| `data-sv` on numeric cells | yes (also affected by `??0` anti-pattern, flagged at cardFacDetail audit) | yes, uses `??''` (correct anti-anti-pattern) | — **good** |
| Row clickable → drill | yes → `oDrF` | yes → `oDrFRisk` | Two drill fns for the same factor object — PM-facing risk drill vs attribution drill — could consolidate |
| `class="clickable"` on row | yes | yes | — |
| Empty-state fallback | yes (L1725/L1730) | **no** | yes |
| CSV export | yes | yes (`CSV` button L3140) | — |
| PNG download | yes (⬇ dropdown) | **no** (user prefers no PNG per MEMORY) | not a gap |
| Card-title note (right-click) | yes (`showNotePopup(...,'cardFacDetail')`) | **no** | yes |
| Card-title `class="tip" data-tip` | yes | **no** | yes |
| Primary / All toggle | yes (`_facView`) | **no** — shows all factors | PM question: is "all factors" the intent on Risk tab? Most Risk-tab sibling bars filter to `FAC_PRIMARY` (L3332, L3342) |
| Group pills (Val/Growth / MktBehavior / Prof / Secondary) | yes (`facGroupPillsHtml()`) | **no** | yes if PM wants filtering |
| Full-screen (⛶) | yes (`openFullScreen('facmap')`) | **no** | yes (cross-tile sweep item) |
| Column picker | yes (`facColDropHtml()`) | **no** | lower priority |
| Threshold slider (min \|c\| filter) | bars only | **no** | lower priority |
| Hover tooltip rows | — | — | — |
| `data-col` on th/td | yes | **no** — prerequisite for future column-picker | yes |
| Keyboard access on clickable rows | no | no | cross-tile concern, not tile-specific |
| Mutli-week aware (consumes `_selectedWeek`) | no | **no** | yes (cross-tile) |

### 2.x Drill semantics

`oDrF` (Attribution-tab drill at L4216) and `oDrFRisk` (Risk-tab drill at L3513) are nearly identical modals. `oDrFRisk` adds a TE context (mcrTE KPI tile, "Factor Return & Impact" panel, active-vs-raw-mixed current annotation). The overlap is material. PM should clarify: two drills keeps Risk-tab sovereign; one unified drill is simpler. Both drills hardcode `FAC_PRIMARY` differently and both suffer the same sign-collapse at L3526 / L5389. **Consolidation is a non-trivial item.**

### 2.y Redundancy with Factor Contributions bars (sibling L3087)

The Factor Contributions bars card on the same tab renders `facMCR` as horizontal bars with a TE/Exposure/Both toggle and a Min \|contrib\| threshold slider. This table shows the same `facMCR` rows in table form. PM should confirm they are intended as *complementary* (bars = visual, table = precise values + return/impact + trend) — current state is fine but the two should cross-reference each other. Neither tile mentions the other.

**Section 2 verdict: YELLOW.** Good primitive wiring (id, sort, CSV, data-sv with `??''`), but missing card-title note, tip, data-col, empty-state; Primary/All filter and week-selector awareness depend on PM intent.

---

## Section 3 · Design consistency — **YELLOW**

### 3.1 Card-title affordances

L3139: `<div class="card-title" style="margin:0">Factor Exposures — click row for time series drill</div>`

No `class="tip"`, no `data-tip`, no `oncontextmenu="showNotePopup(...)"`. cardFacDetail, cardAttribWaterfall, cardThisWeek, cardRanks, cardChars, cardCountry, cardFRB, cardTreemap all have at least the notes hook. This is the most-ignored factor table in the file for annotation/tooltip affordances.

### 3.2 Header tooltip drift

Every numeric `<th>` should carry `class="tip" data-tip="..."` per the AUDIT_LEARNINGS "cardSectors = gold standard" rule. None do on this tile. Candidate text:

- **Exposure** → "Active factor exposure (portfolio − benchmark), in factor-std-dev units."
- **Contrib %** → "Percent of total portfolio tracking error attributable to this factor."
- **MCR to TE** → "Marginal contribution to TE = Total TE × \|Contrib%\|. Units: TE (bps or %)."
- **Return %** → "Factor return over the selected period."
- **Impact** → "Per-factor return impact on the portfolio = factor return × exposure."
- **Trend** → "Weekly active-exposure history for this factor."

### 3.3 Header label mislabels (semantic)

- **Exposure** → should be "Active Exposure" (value is `f.a`, and the drill KPI at L3545 already uses "Active Exposure"). Single most impactful rename on this tile.
- **MCR to TE** → consistent with `oDrFRisk` drill KPI ("MCR to TE" L3547) — good.
- **Contrib %** → should be "% of TE" to match drill KPI ("Risk Contrib") semantics and match `oDrFRisk` L3547 wording. Denominator still ambiguous.

### 3.4 Color-coloring: two mechanisms for sign

- `cls=f.e!=null?(f.e>0?'pos':'neg'):''` produces `.pos`/`.neg` class on Exposure cell (L3152).
- Return % (L3155) and Impact (L3156) cells use inline `style="color:var(--pos)"`.
  Two equivalent mechanisms. Inline styles are slightly harder to theme-override. Prefer the class-based approach across all three cells.

### 3.5 `data-col` attributes missing

Per primitives checklist, every `<th>` and `<td>` should carry stable `data-col="n"/"exposure"/...` for column-picker retrofit. Absent here. Same pattern gap as cardRegions.

### 3.6 Threshold classes (`thresh-alert`, `thresh-warn`) absent

Per AUDIT_LEARNINGS design conventions: `|active|>5 → thresh-alert`, `|active|>3 → thresh-warn`. The Exposure column currently only does pos/neg coloring by sign, not by magnitude. Factor exposures are in z-score-like units (not %) so the 5/3 thresholds don't translate literally — PM should name factor-std-dev thresholds (e.g., `|e|>1.5σ` alert, `|e|>1σ` warn) or omit for this tile.

### 3.7 Trend sparkline — shared `mkSparkline`

Uses global `mkSparkline` (L3493). Passes `color=null` → sparkline color defaults to `var(--pos)` or `var(--neg)` based on first-vs-last direction (L3505). Consistent with other tiles using `mkSparkline`. Good. Not a source of palette drift here (the drift lives in the Factor Contributions bars sibling card at L3309).

### 3.8 Density

Rows use default `<td>` padding. No inline overrides. Good — matches cardSectors / cardHoldings floor.

### 3.9 Spacing / layout

- Card sits alone in its slot on Risk tab (full width). Fine.
- Inline style on shell: `style="margin-bottom:16px"` — consistent with other Risk-tab cards.
- Table height is unbounded — for strategies with ~30+ factors (all-not-just-primary) this becomes a long scroll inside the tab. cardFacDetail gets away with this because it has a Primary filter; this tile has none.

**Section 3 verdict: YELLOW.** No design catastrophes but four medium gaps (card-title affordances, header tips, semantic rename Exposure→Active Exposure, data-col), any of which is trivial to fix.

---

## Section 4 · Trivial fix queue (T1..Tn)

Each ≤10 lines. Ordered by impact.

| id | Area | Fix | Lines touched |
|---|---|---|---|
| T1 | Section 3.3 | Rename header `Exposure` → `Active Exposure` at L3143. | L3143 |
| T2 | Section 3.1 | Add card-title affordances: `class="card-title tip" data-tip="Factor-level active exposure, TE contribution, and return impact. Click row for time-series drill." oncontextmenu="showNotePopup(event,'cardRiskFacTbl');return false"` | L3139 |
| T3 | Section 3.2 | Wrap each numeric `<th>` with `class="r tip" data-tip="..."` using the six candidate strings above. | L3143–L3145 |
| T4 | Section 1.6 | Add empty-state fallback: `${facMCR.length?'': '<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--txt);font-size:11px">No factor data</td></tr>'}` before the closing `</tbody>`. | L3160 |
| T5 | Section 1.4 | Preserve sign on MCR to TE. Two parts: (a) compute signed `mcrTE=+(totalTE*(f.c||0)/100).toFixed(3)` at L2996 (drop `Math.abs`). (b) Apply pos/neg class via `class="r ${f.mcrTE==null?'':f.mcrTE>0?'neg':'pos'}"` on the cell at L3154 (note polarity — a *positive* TE contribution ADDS risk so it reads as *neg* for the "good/bad" narrative; **defer to PM** on whether positive-TE-add should color red or stay neutral). | L2996, L3154 |
| T6 | Section 3.4 | Replace inline sign styles on Return % and Impact cells with `.pos`/`.neg` classes to match Exposure cell mechanism. | L3155–L3156 |
| T7 | Section 3.5 | Add `data-col="n"`, `data-col="e"`, `data-col="c"`, `data-col="mcrTE"`, `data-col="ret"`, `data-col="imp"`, `data-col="trend"` on `<th>` and matching `<td>`. | L3142–L3157 |
| T8 | Section 1.3 (tile side) | Fix sparkline fallback to pull active from the right field. Since `hist.fac[name][i].a` is populated by the parser L947, prefer `h.a` first: `let sparkVals = facHist ? facHist.map(h => h.a!=null ? +h.a.toFixed(4) : (h.bm!=null ? +(h.e-h.bm).toFixed(4) : null)) : [];` and let `mkSparkline` filter nulls (it already does, L3495). **Verify `hist.fac[n][].a` carries data in a real file** before shipping — under the riskm path L468 `a_val = g(row, ac)` which is populated when the CSV has the active-exposure column; under some CSV layouts this may be null. If `h.a` is null everywhere, this downgrades to B-level backlog not trivial. | L3149 |
| T9 | Section 1.3 (drill side) | In `oDrFRisk` at L3573: replace `last.e||last.a` with `last.a ?? (last.bm!=null ? last.e-last.bm : last.e)` so the "Current: …" annotation matches the y-axis (which is labeled "Exposure" at L3585 but plotted as `e−bm` at L3567). Then relabel the y-axis "Active Exposure". | L3573, L3585 |
| T10 | Redundant fn | Remove the legacy alias `rRiskFacBars` at L3377 — now only sets state and calls the real fn; unused call sites (grep confirms). | L3377 |

**Estimated lift:** ~40 lines of diff across ~8 locations. No backend / parser change needed for T1–T7, T9, T10. T8 depends on parser-side verification (active-exposure column present in the `active_factor_cols` map — likely true but untested in this audit).

---

## Section 5 · Non-trivial queue (→ BACKLOG as B61..B6N)

| id | Title | Scope | PM gate? |
|---|---|---|---|
| **B61** | Unify active-vs-raw policy across factor-exposure tiles (3rd site escalates to cross-tile refactor) | cardFacDetail L1764, cardCorr L2168, cardRiskFacTbl sparkline L3149 + drill L3573 — decide globally: always active (`e−bm`), always raw (`e`), or expose a `[Active\|Raw]` toggle surfaced on every factor-family tile. Touches 3 tile renders + 1 drill + parser labelling. | **yes** — PM policy call. Highest leverage single decision remaining on the Risk tab. |
| **B62** | Unify sign-collapse policy across risk-budget views (4th site: now includes cardRiskFacTbl MCR-to-TE L2996 + drill KPI L3526) | Already B-level from cardFRB. Now four sites: cardFRB L2696, `oDrRiskBudget` L5389, Risk Decomp Tree L2770, cardRiskFacTbl L2996. If keeping magnitude, colorize direction separately (stripes, icon, sign prefix). | yes — semantic decision for risk-budget narrative. |
| **B63** | Consolidate `oDrF` (Attribution-tab drill) and `oDrFRisk` (Risk-tab drill) into one modal with a "Risk context" section toggle | L3513 vs L4216 — ~150 LoC duplication. Current state: two nearly-identical modals with slightly different KPI cards. | yes — PM needs to confirm Risk-tab drill is really different, or whether one unified drill suffices. |
| **B64** | Add `_selectedWeek` awareness to `rRisk()` and every Risk-tab tile | Similar shape to the divergence on cardThisWeek and cardSectors flagged in prior audits. Requires pulling `{factors, hist, sum}` for the selected week; simplest path: re-parse `cs.factors` from `cs.hist.fac[*][week]` when `_selectedWeek` is set. Needs the parser-side `hist.fac.*.c` (contrib) populated at historical weeks — verify before promising. | yes — also requires PM to clarify whether Risk-tab historical state should replay or stay latest. |
| **B65** | Add Primary / All filter toggle (mirror cardFacDetail `_facView`) with shared state | If PM wants: wire to existing `_facView` module-global and honor group pills (`setFacGroup`). Would reuse `FAC_PRIMARY` and cardFacDetail's group definitions. Cross-tile shared state — surface caveat per AUDIT_LEARNINGS "shared state traps". | yes — PM confirms default view (all vs primary). |
| **B66** | Standardize factor-tile note-hook pattern | Every card on the Risk tab should have a stable `id` + `class="tip" data-tip` + `oncontextmenu="showNotePopup(...)"`. The Risk tab has at least 4 anonymous cards (Factor Contributions L3087, Factor Exposure History L3164, Factor Correlation Matrix L3177, TE Stacked Area L3070). This echoes the "Anonymous Risk-tab cards" item AUDIT_LEARNINGS added from the cardCorr audit. | no — mechanical sweep. |

---

## Section 6 · Cross-tile learnings (append to AUDIT_LEARNINGS)

### 6.1 Active-vs-raw conflation — **3rd site confirmed, escalates to cross-tile refactor (B61)**

Previous sites (per learnings file): cardFacDetail L1764, cardCorr L2168. Third site within a single tile — cardRiskFacTbl:
- **Exposure cell** at L3152 reads `f.a` (active) but is labeled "Exposure"
- **Trend sparkline** at L3149 falls through to raw `h.e` whenever `h.bm==null`, which is **always** on the riskm path (factset_parser.py L468 hardcodes `bm: None`)
- **Drill annotation** at L3573 uses `last.e||last.a` (raw with active fallback) while the chart trace plots `e−bm` — self-contradicting inside one chart.
Confirms the cross-tile pattern is a parser+render joint decision, not a per-tile render bug. Parser sets `bm: None` in one code path but populates `bm` in another — renders have to hedge. Fix needs to land at parser + render simultaneously.

### 6.2 Sign-collapse on risk-budget views — **4th site confirmed**

Previous sites: cardFRB L2696, `oDrRiskBudget` L5389, Risk Decomp Tree L2770. Fourth site: cardRiskFacTbl's MCR-to-TE column L2996, and its drill KPI L3526. Pattern is now widespread enough that a shared helper (e.g. `mcrSigned(f, totalTE)`) and a shared "colorize risk-add vs diversifier" convention should be the norm, with `Math.abs` reserved for strict-magnitude views (Top-|MCR| bars).

### 6.3 Parser dual-path for factor exposures (NEW)

Parser has **two** paths populating `exposures[fname]`:
1. `_collect_riskm_data` L460–469 — always sets `bm: None`, stores `c_val` as both `c` and `e` (i.e., port exposure).
2. `_build_factor_list` L847–865 — relies on whatever `exposures` was set to for the *current* riskm entry, so `bm` stays None here too. But `f.a` DOES get populated (L857) when `active_factor_cols` has the factor.
Net: the factor list exposes `a` (active) reliably; `hist.fac[][].bm` is unreliable (always None on riskm path). Any tile consuming `hist.fac[][].bm` falls into silent fallthrough. **Fix direction (backend):** populate `bm` in riskm path by differencing `c - a` (algebra: `a = e - bm → bm = e - a`) so downstream renders have a consistent `{e, bm, a}` triple. One-line parser change at L468.

### 6.4 Completed audits (append-only — 2026-04-23 batch 4 continued)

- ✅ cardRiskFacTbl (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top findings = (1) active-vs-raw 3rd site in-row between Exposure cell and Trend sparkline, (2) sign-collapse 4th site on MCR-to-TE, (3) header mislabel Exposure → should be Active Exposure, (4) parser dual-path asymmetry for `bm`; trivial fix queue 10, non-trivial → B61–B66)

---

## Section 7 · Verification checklist

- [ ] Data accuracy verified on a real file (3–5 factor spot-check) — **pending** (known blocker)
- [x] Sort works on 6 of 7 columns (Trend intentionally non-sortable)
- [x] `data-sv` uses `??''` (avoids the 0/null coercion anti-pattern)
- [ ] Empty-state fallback renders "No factor data" — **missing**
- [ ] Card-title note-hook / tip — **missing**
- [ ] Header `data-tip` on every numeric column — **missing**
- [x] Stable card id + table id
- [x] Row-click drill wired (`oDrFRisk`)
- [x] CSV export wired (no PNG — correct per user preference)
- [ ] Week-selector awareness — **silent-latest**
- [ ] Active-vs-raw consistency within the row — **broken** (see 1.3)
- [ ] Sign preserved on MCR-to-TE — **collapsed** (see 1.4)
- [x] No console errors expected (pure template render, no runtime fetch)
- [ ] Keyboard access on clickable rows — cross-tile gap; not tile-specific

---

## Summary for spawner

Tile audit shipped: `/Users/ygoodman/RR/tile-specs/cardRiskFacTbl-audit-2026-04-23.md`

Color status by section:
- Section 1 (Data): **RED** — active-vs-raw in-row divergence + sign-collapse on MCR-to-TE + header mislabel
- Section 2 (Functionality): **YELLOW** — good primitives, missing note-hook/tip/filter/empty-state
- Section 3 (Design): **YELLOW** — four trivial gaps, no catastrophes

Top findings (3):
1. **Active-vs-raw conflation is now 3-of-3 audited factor-exposure-reading tiles** (cardFacDetail, cardCorr, cardRiskFacTbl). Inside this tile the divergence is visible side-by-side: the Exposure cell shows active, the Trend sparkline in the same row shows raw. Parser L468 hardcodes `bm: None` in the riskm path — every hist.fac sparkline that depends on `bm` silently falls through to raw. Escalates B53 → cross-tile refactor **B61**.
2. **Sign-collapse on MCR-to-TE is the 4th site of the cardFRB bug** (L2996 + drill KPI L3526). A diversifying factor reads identically to a risk-adder of equal magnitude. Becomes B62.
3. **Header says "Exposure" but the value is active.** Drill modal KPI at L3545 already correctly labels it "Active Exposure" — the tile table is the last place using the ambiguous label. Single-word T1 trivial fix.

Fix queue:
- TRIVIAL (10 items, agent can apply): T1–T10 listed above. Net ~40 LoC diff. T8 depends on verifying `hist.fac[n][].a` is populated in a real file; otherwise drop to backlog.
- NEEDS PM DECISION (6 items): B61 active-vs-raw policy, B62 sign-collapse policy, B63 oDrF/oDrFRisk consolidation, B64 week-selector awareness, B65 Primary/All toggle, B66 standardize Risk-tab card note-hooks.
- BLOCKED (1 item): Section 1.8 spot-check — requires loaded JSON, deferred per known-blocker convention.
