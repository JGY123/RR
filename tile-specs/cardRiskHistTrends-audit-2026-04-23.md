# Tile Audit — cardRiskHistTrends

**Date:** 2026-04-23
**Auditor:** tile-audit subagent (Batch 4 / Risk tab continuation)
**Audit mode:** audit-only; no edits to dashboard_v7.html.
**Scope:** Risk-tab "Historical Trends" synthesis tile — 4 mini-sparklines (TE / Active Share / Beta / Holdings) rendered via Plotly above the TE stacked-area hero.

---

## Section 0 · Identity

| Field | Value |
|---|---|
| Tile name | Historical Trends (Risk tab) |
| Card DOM id | `#cardRiskHistTrends` |
| Card shell | dashboard_v7.html L2948 (template string inside `riskHistoricalTrends(s)`) |
| HTML builder | `riskHistoricalTrends(s)` L2920 |
| Mini-chart renderer | `rRiskHistMinis(s)` L2954 |
| Called from | `rRisk()` L3065 (HTML inject) + L3199 (setTimeout post-inject render) |
| Tab | Risk (`#tab-risk`) |
| Width | full (margin-bottom:16px; grid of 4 columns inside) |
| Data source | `s.hist.summary` (alias `s.hist.sum` post-normalize — dashboard_v7.html L590 accepts both keys) |
| Parser source | `factset_parser.py` L835 `_hist_entry(pc)` → `{d, te, beta, h, as, sr:null, cash:null}` |
| Spec status | first-time audit |

---

## Section 1 · Data accuracy — **YELLOW**

### 1.1 Field inventory

| Metric | Source | Parser emits? | Format | Trend-arrow logic | Drill | Status |
|---|---|---|---|---|---|---|
| TE | `h.te` | yes (`Predicted Tracking Error (Std Dev)`) | `f2(v,1)%` | dir=`neg` → rising = red | `oDrMetric('te')` | ✅ |
| Active Share | `h.as` | yes (`Port. Ending Active Share`) | `f2(v,1)%` | dir=`neutral` → always grey | `oDrMetric('as')` | ⚠ direction semantics (see 1.4) |
| Beta | `h.beta` | yes (`Axioma- Predicted Beta`) | `f2(v,2)` | dir=`neutral` → always grey | `oDrMetric('beta')` | ⚠ (see 1.5) |
| Holdings | `h.h` | yes (`# of Securities`) | integer | dir=`neutral` | **null — no drill** | ⚠ inconsistency |

### 1.2 `hist.summary` completeness

Parser unconditionally emits `"summary": [self._hist_entry(pc) for pc in pc_rows]` (factset_parser.py L835) — one entry per weekly portchars row. Normalize layer (L588-605) accepts `h.sum` OR `h.summary`, falls back to synthesizing from factor-history dates if both are empty (L595-602). **Empty-state `if(!hist.length)return ''` at L2922 is correct** — tile silently omits itself when history is totally missing.

Spot-check pending: no CSV load captured in this session. Cross-reference: cardThisWeek audit verified `s.hist.sum` populates correctly across all 7 strategies — no reason to suspect this tile differs.

### 1.3 Empty / degenerate histories

- `hist.length === 0` → whole tile returns `''` (L2922). Good.
- `hist.length === 1` → rendered with single-point card, BUT `rRiskHistMinis` guards `hist.length<2` (L2956) and returns without drawing. Result: label + value visible but mini-chart div stays empty height:48px. L2949 template already includes a warning strip `· Need ≥2 weeks for sparklines`. **Good handling — small UX polish opportunity (§4 T4).**
- `hist.length >= 2` and a given metric is all-null (e.g. `sr` / `cash` in current schema) → `rRiskHistMinis` L2968 skips the Plotly call silently, leaving empty div. Not user-visible for the 4 current metrics since the parser always populates te/as/beta/h, but if a future metric is added without parser backfill, the dead chart div is invisible. Minor — covered by Half-built data pipelines pattern (AUDIT_LEARNINGS).

### 1.4 AS direction semantics

`{key:'as', dir:'neutral'}` (L2927). Reasonable PM call — AS rising or falling is narratively ambiguous. But note that **cardThisWeek + watchlist bullets do treat AS drift as directional** (against mandate limits). Inconsistency is minor; document if the PM wants bulletized interpretation here.

### 1.5 Beta direction semantics

`{key:'beta', dir:'neutral'}` (L2928). Beta has a canonical reference at 1.0 — rising beta above 1 means procyclical / higher-beta portfolio. Many PMs track `|beta-1|` as a directional guideline distance. Current UI shows the Δ WoW but always in grey. **Consider `dir:'from1'`** — render red when the Δ moves further from 1, green when it moves toward 1. Defer to PM call; flagged §5 B61.

### 1.6 `h` (Holdings count) integer rounding

Normalize L611 rounds `e.h` to integer for all `hist.sum` rows. The `fmt: v=>String(v)` path (L2929) is therefore safe. The WoW delta `d=+(cv-pv).toFixed(2)` (L2933) can produce non-integer deltas that are then displayed via `Math.round(d)` (L2937) — readable, but the compute could be simpler `Math.round(cv-pv)`. Cosmetic.

### 1.7 Threshold for "show delta"

L2934: `showD = d!=null && Math.abs(d) > (m.key==='beta'?0.001:0.01)`. So for TE, any WoW change ≥0.01% triggers an arrow. That is ~0.01 percentage-point TE movement WoW — in practice almost always triggered. Effectively always-on for TE/AS; beta threshold 0.001 is also low. Consider raising to `0.05` (TE/AS) and `0.005` (beta) to suppress near-zero noise. Minor.

### 1.8 Week-selector awareness — **YELLOW**

`cur=hist[hist.length-1]` L2923 — **always the latest entry**, never the selected week. When the user picks a historical week via the header week-selector (`_selectedWeek` ≠ null), this tile silently shows latest values on the value-display row and no vertical marker on the mini-chart. This is the same AUDIT_LEARNINGS "week-selector awareness" trap flagged for cardThisWeek, sector detail tables, etc. Two fixable components:
1. Replace `cur` with `getSelectedWeekSum()` (helper at L813) or the matching `hist.sum` entry at `_selectedWeek`. The WoW delta becomes selected-week-minus-prior-week, not latest-minus-prior.
2. Draw a vertical marker/line on each mini-chart at the `_selectedWeek` date so the user sees where "now" sits in history (documentation effect, not just data).

Fix (1) is trivial (§4 T5). Fix (2) is non-trivial (§5 B62).

---

## Section 2 · Functionality parity — **YELLOW**

Benchmark = cardThisWeek (synthesis-tile sibling, audited 2026-04-21, GREEN/YELLOW/GREEN) + cardAttrib time-series helpers (audited 2026-04-23).

| Capability | Benchmark | This tile | Gap |
|---|---|---|---|
| Drill modal on click | cardThisWeek: none; sum-cards in rRisk: yes | 3 of 4 wired (`oDrMetric` for te/as/beta), Holdings = no | **yes (minor)** |
| Range buttons (3M/6M/1Y/3Y/All) | `oDrMetric` drill has it; tile does not | No | **yes** |
| CSV export of underlying series | cardThisWeek: none (bullets); cardAttrib: yes | No | **yes** |
| Card-title tooltip (`class="tip" data-tip="…"`) | cardFRB/cardMCR/cardScatter: yes | **No** (L2949 plain `.card-title`) | **yes** |
| Card-title right-click note (`oncontextmenu="showNotePopup(…)"`) | ~10 tiles have it | **No** | **yes** |
| Week-selector vertical marker | cardThisWeek: N/A (bullets); rMultiBeta / teStackedArea: range slider covers latest-vs-history but no _selectedWeek marker anywhere | No | shared gap, tracked cross-tile |
| Full-screen ⛶ expand | Viz tiles often have it | No | **yes (minor)** — mini-chart is meant to be glanceable |
| `rangemode:'tozero'` on y-axis | — | yes on all 4 (L2977) | visual drawback for Beta / Holdings (see §3) |
| `plotly_click` on mini-chart points | — | **No** — click-to-drill lives on the outer `<div onclick=…>`, hover-tooltip on the plot is non-interactive | minor |
| Hover tooltip | all viz tiles | yes (`hovertemplate:'%{x|%b %d}: %{y}<extra></extra>'` L2972) — but no units; Beta shows bare number, TE/AS show bare number (no `%` suffix) | **yes (minor)** |
| Theme-aware colors | cardTreemap / cardFRB drift; cardSectors good | Plotly line colors hardcoded (§3) | **yes** |
| Child chart divs keyed | AUDIT_LEARNINGS "Anonymous Risk-tab cards" | yes (`miniTE`, `miniAS`, `miniBeta`, `miniH`) | ✅ already good |

### 2.1 Holdings not drillable

`{key:'h', drill:null}` L2929 intentionally omits a drill target — there is no `oDrMetric('h')` or holdings-count modal. This creates visible asymmetry: 3 cards cursor:pointer, 1 card cursor:default. Either:
- (a) Add an Holdings-count drill modal (mini, since the data is already in `oDrMetric`'s switch — L5125 labels `h:'Holdings Count'` — let it fall through by removing the `drill:null` guard and adjusting `oDrMetric` to accept `'h'`).
- (b) Keep as-is; document consistently.

`oDrMetric` at L5092 appears to handle generic metrics via `hist.map(h=>h[metric])` and a `labels{}` dict that already includes `h:'Holdings Count'` (L5125). Flipping `drill:null` to `"oDrMetric('h')"` likely works with zero other changes. **Trivial fix (§4 T6).**

### 2.2 No range buttons

The drill modal (`oDrMetric`) exposes 3M/6M/1Y/3Y/All (L5119-5123). The in-tile mini-chart is fixed "all history". Cross-tile: cardThisWeek bullets similarly have no range; sector / country / regions detail tables similarly all-latest. Given the tile's role (glance at trend), range buttons might be overkill — but a simple **fixed "last 52w / All" toggle** (one button, two states) would address the "3-year files dilute recent spikes" visual problem. Flagged §5 B63 (PM call).

### 2.3 No CSV export

All 4 metrics are trivially serializable: `d, te, as, beta, h`. `exportCSV` helper exists globally. No `<table>` in this tile, so the helper's `#tbl-…` pattern doesn't apply directly — would need a small inline path (e.g. `exportHistSummaryCSV()` or pass an array to a generic helper). Non-trivial only because the helper needs a tweak. Flagged §5 B64.

### 2.4 Card-title missing tip + note-popup

L2949:

```html
<div class="card-title" style="margin-bottom:10px">Historical Trends …</div>
```

No `class="tip" data-tip="…"` (every other Risk-tab card-title with a tip has one — cardFRB L1285, cardMCR L1280, cardTreemap L1263 etc.) and no `oncontextmenu="showNotePopup(event,'cardRiskHistTrends');return false"`. Straight primitives gap. **Trivial fix (§4 T1).**

### 2.5 `hovertemplate` missing units

`'%{x|%b %d}: %{y}<extra></extra>'` L2972 is shared across all 4 metrics. TE hover shows "Jan 05: 4.73" (no `%`), Beta "Jan 05: 0.98" (fine), Holdings "Jan 05: 162" (fine), AS "Jan 05: 89.3" (no `%`). Per-metric `hovertemplate` with `%{y:.2f}%` for TE/AS and `%{y:.3f}` for beta would match the big-label formatter. **Trivial fix (§4 T2).**

---

## Section 3 · Design consistency — **YELLOW**

### 3.1 Hardcoded hex colors (token drift)

`rRiskHistMinis` L2959-2962:

```js
{id:'miniTE',   vals:…, color:'#6366f1', fill:'rgba(99,102,241,.12)'},
{id:'miniAS',   vals:…, color:'#8b5cf6', fill:'rgba(139,92,246,.12)'},
{id:'miniBeta', vals:…, color:'#38bdf8', fill:'rgba(56,189,248,.12)'},
{id:'miniH',    vals:…, color:'#94a3b8', fill:'rgba(148,163,184,.12)'}
```

These map exactly to the CSS tokens defined at L13-14: `--pri:#6366f1`, `--acc:#8b5cf6`, `--cyan:#38bdf8`, `--txt:#94a3b8`. Label big-values at L2942 use `var(--pri)`, `var(--acc)`, `var(--cyan)`, `var(--txth)` — the stroke colors in the sparkline should match. Same class of drift as `inlineSparkSvg` (AUDIT_LEARNINGS §Viz-renderer pattern — now FIXED at L1456-1457 but this sibling was never migrated).

**Trivial fix (§4 T3):** replace each hardcoded color with `getComputedStyle(document.body).getPropertyValue('--pri').trim()` pattern (Batch 3/4 established convention) — 4 lines. Fill colors (rgba with alpha) are harder to token-ize; leave as fixed-alpha-matching-stroke or derive via a small helper.

### 3.2 `rangemode:'tozero'` on all 4 mini-charts — **visual drawback for Beta/Holdings**

L2977. TE hovers 3-8% (tozero is fine, plot uses meaningful floor). AS hovers 75-98% (tozero wastes ~75% of the plot area). Beta hovers 0.85-1.15 (tozero crushes the variation to a flat line). Holdings 50-250 count (tozero OK-ish).

Recommend `rangemode:'normal'` for Beta + AS (let Plotly fit the data range). TE/Holdings can keep tozero to preserve the "absolute risk" framing. Trivial fix §4 T7; PM sensitivity — some PMs want fixed-axis comparability across weeks (tozero gives that), in which case keep. Flag as PM-review.

### 3.3 Trend-arrow threshold too loose

§1.7 above — `Math.abs(d) > 0.01` on TE/AS always triggers (WoW movements are rarely < 0.01 pp). Effectively always shows an arrow. Consider 0.05 for TE/AS and 0.005 for beta — same feel as cardThisWeek bullet thresholds. Trivial §4 T8.

### 3.4 Y-axis scaling across mini-charts — **independent is correct**

All 4 axes are independent (no shared scale). This is the right call — TE% and Holdings-count cannot share a Y axis. No change needed.

### 3.5 Card-title 'weeks' inline stat

L2949 `<span style="font-size:10px;color:var(--txt);font-weight:400">${hist.length} week${…}</span>` — using tokens, good. Matches cardAttrib + cardFRB subtitle pattern. No change.

### 3.6 Grid layout

`grid-template-columns:repeat(4,minmax(180px,1fr))` L2950. On narrow viewports (<800px) this wraps oddly. The rest of the Risk tab uses `sum-cards` at 5-column. The 4-column choice is fine but could use `repeat(auto-fit, minmax(180px,1fr))` for responsive wrap. Cosmetic.

### 3.7 Mini-chart height 48px

L2945 `style="height:48px"`. Consistent with glanceable-sparkline convention. Good.

### 3.8 Value font sizes

L2940 label: 9px uppercase (within token scale floor — 9 is the absolute minimum used project-wide). L2942 value: 18px (big-but-not-huge). L2943 delta: 10px. All within the app's density scale. Good.

---

## Section 4 · Trivial fix queue (T1..T8)

Applicable to a coordinator who will serialize a batch of small edits on dashboard_v7.html.

| ID | Fix | Location | Lines |
|---|---|---|---|
| **T1** | Add `class="tip" data-tip="…"` + `oncontextmenu="showNotePopup(event,'cardRiskHistTrends');return false"` to the card-title at L2949. Suggested tooltip: _"Four-metric trend glance across all available weeks. Click a card for detailed time-series drill with threshold bands. Right-click for notes."_ | L2949 | 1 |
| **T2** | Per-metric `hovertemplate` in `rRiskHistMinis` (pass `unit`/`dec` through the `specs` array): `te/as → %{y:.2f}%`, `beta → %{y:.3f}`, `h → %{y:d}`. | L2958-2979 | ~6 |
| **T3** | Replace hardcoded `#6366f1 / #8b5cf6 / #38bdf8 / #94a3b8` at L2959-2962 with `getComputedStyle(document.body).getPropertyValue('--pri/--acc/--cyan/--txt').trim()`. Derive fill via a tiny hex-to-rgba helper or hand-alpha. | L2959-2962 | 4-8 |
| **T4** | When `hist.length===1`, render an inline "—" placeholder inside the `miniXxx` div instead of leaving it empty (0 height but visible blank). Matches `inlineSparkSvg` convention L1446. | L2956 | 3 |
| **T5** | Make `cur`/`prev` `_selectedWeek`-aware: replace `cur=hist[hist.length-1]` with `let idx=_selectedWeek?hist.findIndex(h=>h.d===_selectedWeek):hist.length-1; if(idx<0)idx=hist.length-1; let cur=hist[idx], prev=idx>0?hist[idx-1]:null;`. Pairs with vertical marker B62 but this value-display fix is standalone. | L2923-2924 | 3 |
| **T6** | Flip `{key:'h', drill:null}` L2929 to `drill:"oDrMetric('h')"` (helper at L5092 already handles generic metrics via `labels.h:'Holdings Count'` L5125 — verify the switch accepts `metric==='h'` path for the plain case; if so zero extra changes). | L2929 | 1 |
| **T7** | Beta + AS mini-charts: `yaxis.rangemode:'normal'` (let Plotly fit data range). Keep `'tozero'` for TE + Holdings. Requires a per-spec override in the `specs` array. | L2977 | 2-3 |
| **T8** | Raise the "show arrow" noise floor: TE/AS `>0.05` (from `>0.01`), beta `>0.005` (from `>0.001`). | L2934 | 1 |

**Total trivial queue: 8 items, all ≤ 8 lines each.**

---

## Section 5 · Non-trivial queue (append to BACKLOG as B61..B64)

| ID | Item | Rationale | Dependency |
|---|---|---|---|
| **B61** | PM call on Beta directional coloring — `dir:'from1'` (red as \|beta-1\| grows, green as it shrinks) vs. current `dir:'neutral'`. | §1.5 — Beta has a canonical reference at 1.0 different from TE's "rising = bad" framing. | PM |
| **B62** | Vertical week-selector marker on all 4 mini-charts when `_selectedWeek !== null`. Plotly shape overlay is trivial mechanically; the design question is whether to marker-only, marker-plus-faded-future-region, or full-range-dimming. | §1.8 + cross-tile "week-selector awareness" backlog entry. | design-lead review; consistent treatment across rMultiBeta + teStackedArea + these minis. |
| **B63** | Recent-vs-All toggle (single button, two states: "Last 52w" / "All"). Addresses the 3-year-file visual dilution where a recent TE spike gets flattened against 156 weeks of history. Alternative: full 3M/6M/1Y/3Y/All bar matching `oDrMetric`. PM call on which. | §2.2 | PM; code is ~20 lines (slice in `rRiskHistMinis`). |
| **B64** | CSV export of `hist.summary` — add a small "CSV" button in the card header (or expose via a modal-anchored button). Helper tweak to `exportCSV` to accept a data array without a `<table>`, or render a hidden `<table id="tbl-risk-hist">` in the tile and wire existing `exportCSV('#tbl-risk-hist','risk_hist')`. | §2.3 | Low-risk; ~15 lines. |

---

## Section 6 · Cross-tile learnings (append to AUDIT_LEARNINGS.md)

### Proposed additions

**Update the `inlineSparkSvg` bullet under "Viz-renderer pattern":** it is already tokenized at L1456-1457 — the stale claim in AUDIT_LEARNINGS §Viz-renderer ("`inlineSparkSvg` (L1438) hardcodes `#10b981`/`#ef4444` at L1451") should be struck or marked "resolved 2026-04-22" after verifying. (This audit confirms it is tokenized; whoever reads the learning might waste time chasing a fixed issue.)

**New bullet under "Shared state traps" (extend week-selector trap):**

> - **Week-selector trap on synthesis/trend tiles:** beyond detail tables, any tile that computes `cur = hist[hist.length-1]` / WoW deltas against `hist[length-2]` silently ignores `_selectedWeek`. Seen: cardRiskHistTrends L2923 (value display + delta arrow), cardThisWeek (previously flagged). Even when the underlying chart shows all history, a vertical marker at `_selectedWeek` is missing — audit every new tile with `hist.sum` access for this. Fix pattern: `let idx = _selectedWeek ? hist.findIndex(h=>h.d===_selectedWeek) : hist.length-1` before extracting `cur`/`prev`.

**New bullet under "Viz-tile (chart) checklist" (mini-chart sub-checklist):**

> - **Mini-chart (sparkline) tiles** need: (a) per-metric `hovertemplate` with units, (b) `rangemode:'tozero'` reviewed per-metric — crushing for ref-1-centered metrics like Beta, (c) keyed child chart div ids (cardRiskHistTrends: good — `miniTE`/`miniAS`/`miniBeta`/`miniH`), (d) delta-arrow noise floor calibrated (`>0.05` on pp metrics, not `>0.01`).

**New bullet under "Synthesis / insight tiles":**

> - **Drill symmetry across metric cards:** when a multi-metric card wires 3-of-N metrics to drill modals and leaves 1 undrillable (`drill:null`), the visual asymmetry (some cursor:pointer, some cursor:default) reads as broken. Either add the missing drill (most generic `oDrMetric(key)` patterns accept arbitrary keys with `hist[key]`) or make the intentional omission visible (e.g. annotate the undrillable card `title="Drill not available"`).

---

## Section 7 · Verification checklist

- [x] Data source traced to parser (L835 `_hist_entry`) + normalize alias handling (L590)
- [x] Empty-history fallback correct (L2922 returns `''`)
- [x] Short-history fallback exists (L2949 warns; L2956 skips rendering; T4 would improve)
- [x] Card has stable `id="cardRiskHistTrends"` (L2948)
- [x] Child mini-chart divs have stable ids (`miniTE`/`miniAS`/`miniBeta`/`miniH`)
- [ ] Card-title tooltip / note-popup (MISSING — T1)
- [x] Theme tokens on big-value labels (L2942 uses `var(--pri)`, etc.)
- [ ] Theme tokens on Plotly stroke/fill (MISSING — T3)
- [ ] `_selectedWeek` awareness (MISSING — T5 + B62)
- [ ] CSV export (MISSING — B64)
- [ ] `plotly_click` per-point drill (MISSING; acceptable here since outer `<div onclick>` covers drill intent)
- [x] No PNG buttons (confirmed)
- [x] No hardcoded red/green (uses `var(--pos)/var(--neg)` at L2935)
- [x] `hist.summary` vs `hist.sum` alias handled (L590)
- [ ] Spot-check against loaded strategy (pending — env without CSV/JSON)

---

## Section 8 · Summary (for coordinator)

**Color status:**
- Section 1 (Data): **YELLOW** — data itself is clean; two directional-semantics questions (Beta `dir:'neutral'` defensible, AS `dir:'neutral'` defensible, but the `_selectedWeek`-blind `cur` / `prev` is a real silent bug).
- Section 2 (Functionality): **YELLOW** — missing primitives (tip + note-popup, Holdings drill, CSV), but core drill on 3-of-4 cards + hover tooltip present.
- Section 3 (Design): **YELLOW** — 4 hardcoded hexes that map exactly to existing tokens; `rangemode:'tozero'` flattens Beta + AS visually.

**Top findings (3):**
1. **Token drift on 4 Plotly stroke/fill colors at L2959-2962** — exact matches to existing `--pri/--acc/--cyan/--txt` tokens. Trivial 4-8 line fix (T3).
2. **`_selectedWeek`-blind `cur` / `prev`** — when the user picks a historical week in the header, this tile still shows latest values with latest WoW delta. Silent divergence from the amber week banner. Trivial standalone fix (T5); vertical-marker polish is B62.
3. **Holdings card has `drill:null` while the other 3 drill** — visible asymmetry (cursor:default vs cursor:pointer). `oDrMetric` labels dict already includes `h:'Holdings Count'` (L5125), so flipping to `drill:"oDrMetric('h')"` almost certainly just works. Trivial (T6).

**Fix queue:**
- TRIVIAL (8 items, coordinator can batch): T1 tooltip+note-popup, T2 per-metric hover units, T3 tokenize 4 colors, T4 short-history placeholder, T5 `_selectedWeek`-aware cur/prev, T6 Holdings drill, T7 rangemode per-metric, T8 noise-floor thresholds.
- NEEDS PM DECISION (2 items): B61 Beta `dir:'from1'`, B63 Recent-vs-All range toggle.
- BACKLOG (2 items): B62 vertical week-selector marker (design-lead gate), B64 CSV export of `hist.summary`.

**Not touched (good as-is):**
- Empty-history guard, child-div ids, theme tokens on big-value labels, WoW-delta red-on-rising-TE direction logic, grid layout, 48px mini-chart height, font-size scale.

---

**End of audit.**
