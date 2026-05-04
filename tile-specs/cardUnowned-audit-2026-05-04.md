# Tile Audit — cardUnowned (2026-05-04)

**Render fns:**
- Card shell: `dashboard_v7.html` L3263–3266 (Exposures tab — `tab-exposures`, NOT Holdings as user-spec stated)
- Inline projector: `_unownedFromHold(s)` at L5557–5575
- Renderer: `rUnowned(unowned)` at L5577–5609
- Drill: `oDrUnowned(ticker)` at L12112–12146

**Card id:** `#cardUnowned`
**Table id:** `#tbl-unowned`
**About-registry entry:** L1181–1188 — present, but `how:` field is wrong (claims `h.b > 0 AND (h.p == null || h.p < 0.01)` but the actual code uses `h.b ?? h.bw > 0 AND h.p ?? h.w <= 0`).

**Tab placement:** Exposures (L3362 `$('tab-exposures').innerHTML=html`). The user-spec described it as "Holdings tab"; not the case. Worth confirming whether the user wants it moved or whether the spec is stale.

**Status:** First audit on file. Three-track triage below.

---

## Verdict

| Track | Color | Headline |
|---|---|---|
| **T1 — Data accuracy** | **RED** | `normalize()` `?? 0` fallback fabricates `tr=0` on 76% of bench-only entries (623 of 819 on EM); the "showing top 10 of 819" footer claim implies a 819-item ranked universe but only ~196 of those entries actually have real `pct_t`. The top-10 user sees IS correct (real values float to top), but the rank-tail and the footer count are fabricated. CLAUDE.md hard rule #2 violated. |
| **T2 — Functionality parity** | **YELLOW** | Tile chrome strip used (good); inline `oDrUnowned` drill instead of `oSt` (acceptable but divergent — no time-series); `oDrUnowned` predicate uses `x.w` only at L12121 instead of `x.w ?? x.p`, asymmetric with `_unownedFromHold` (L5561 uses `h.p ?? h.w`). Drill modal references `u.reg` which isn't shipped on synth holdings → "Holdings in —" rendering. No universe-pill awareness (correct — the tile IS a universe-defining concept). No per-week routing — synthronously reads `s = cs` (latest) so historical-week selection silently shows latest data. |
| **T3 — Design consistency** | **YELLOW** | Plain `<p>` empty state instead of `.empty-state` class. No footer/hairline disclosing the synth path (`pct_t` only shipped for slim-Security entries, ~196 of 819 bench-only have real values — the rest are sourced from Raw Factors long-tail synthesis with `pct_t: None`, which `normalize()` then `?? 0`'d). Double tooltip (card-title `data-tip` + th `data-tip`). Color tokens used throughout (good). |

---

## T1 — Data accuracy

### T1.1 — `normalize()` `?? 0` fallback fabricates TE-contribution → **RED**

**Location:** L1872–1881 in `normalize()`:
```js
st.hold=st.hold.map(h=>{
  let hn={...h};
  hn.p=hn.p??hn.w??0;
  hn.b=hn.b??hn.bw??0;
  hn.a=hn.a??hn.aw??(hn.p-hn.b);
  hn.mcr=hn.mcr??hn.pct_s??0;
  hn.tr=hn.tr??hn.pct_t??0;     // ← FABRICATION POINT
  ...
});
```

**Empirical impact (measured on `data/strategies/EM.json`, 914 holdings, 2026-05-04):**

| Quantity | Value |
|---|---|
| Total holdings | 914 |
| Bench-only (post-normalize: `p<=0 && b>0`) | 819 |
| Bench-only with **real** `pct_t` from Security section | 196 |
| Bench-only where parser shipped `pct_t: None` (long-tail synth from Raw Factors) | 623 |
| Bench-only where `normalize()` fabricated `tr = 0` | **623 / 819 = 76%** |

**What the user sees in cardUnowned:**
- The top 10 displayed ARE correct (real-value entries float to the top via `Math.abs(b.tr||0)` sort).
- The footer note "Showing top 10 of 819 unowned BM-only holdings by |TE| contribution" implies a ranked-universe of 819 items, but only 196 are ranked by real values — the remaining 623 sit at `tr=0` (fabricated, indistinguishable from real-zero contributors).
- The audit's stated worry ("if the tile aggregates %T to a total at the bottom, that aggregate is F18-contaminated") — confirmed: **the tile does NOT aggregate** (no total/footer row), so F18 contamination is per-row only, not aggregate-amplified. Σ |pct_t| over all bench-only is only 8.10% on EM (real coverage of the 196 contributors).

**Why this is the most important T1 finding:** the same `?? 0` fabrication pattern produced the April 2026 crisis (LESSONS_LEARNED §1, anti-pattern #1). This `tr ?? pct_t ?? 0` line is the *current-day* version of that pattern. Per CLAUDE.md hard rule #2: "If a field is null in source, leave it null." This line writes `0` when both source fields are null — which (a) lies about the value, (b) makes a fabricated zero rank-equivalent to a real zero contributor, and (c) means the integrity assertion at L2017 doesn't catch it (it only checks 6 sum-level fields, not per-holding `tr`).

**The same fabrication is on `mcr` at the line above** — same pattern, different field. Both should be `??` chained but stop at `?? null` (or just `??`), not `?? 0`.

**Proposed fix (1 line each — coordinator territory):**
```js
hn.mcr = hn.mcr ?? hn.pct_s ?? null;   // was: ?? 0
hn.tr  = hn.tr  ?? hn.pct_t ?? null;   // was: ?? 0
```
Plus downstream sites that read `h.tr` and assume it's always numeric must guard. Quick grep in dashboard:
```bash
grep -nE "h\.tr\b|\.tr\s*\*|\.tr\s*\)" dashboard_v7.html | wc -l
```
~50 sites. Each needs `h.tr != null` guard before arithmetic. Most already use `Math.abs(b.tr||0)` patterns which work fine on null. Aggregations would need `(h.tr ?? 0)` explicitly to *count* as zero, with a sidecar count of `null` entries surfaced in any total-row context.

Same applies to `h.p`, `h.b`, `h.a` if those are sourced as null — but for portfolio context, port-weight-null means "not in portfolio" and treating as 0 is semantically correct (covered by the fact that synth-bench-only entries explicitly set `w: None` for "not held" per parser L1277). The fabrication risk is concentrated on `tr` and `mcr` (the risk-contribution fields).

`[NEEDS_PM_DECISION]` — fixing `?? 0` ripples through ~50 read sites. Coordinator should plan this as a small dedicated PR, not a tile-audit inline edit.

### T1.2 — About-registry's `how:` is stale → **YELLOW**

**Location:** L1184 — the entry says:
> `how:'Filter cs.hold[] for h.b > 0 AND (h.p == null || h.p < 0.01). Sort descending by |%T|. Implicit active wt = -h.b.'`

The actual filter at L5559–5563 is:
```js
const portW = +(h.p ?? h.w ?? 0);
const benchW = +(h.b ?? h.bw ?? 0);
return portW <= 0 && benchW > 0;
```

There is no 0.01 threshold. Source field names also include `bw` and `w` fallbacks not mentioned. **PM-facing About popup currently misrepresents the filter.** Trivial fix.

### T1.3 — `bench wt` provenance is correctly handled → **GREEN**

L5583: `bVal = u.b != null ? u.b : (u.bw != null ? u.bw : null)`. Returns null when both are null (good — the cell renders `—`). This is the *correct* anti-fabrication pattern; should be the model for T1.1's fix. The same pattern on L5584 for `trVal` works at the renderer level — the problem is upstream at `normalize()` which already converted null → 0.

### T1.4 — F18 contamination assessment → **GREEN (per-row only)**

cardUnowned does NOT aggregate `pct_t` to any displayed total. The footer note is a count, not a sum. Therefore F18 (per-holding %T sums 94→134%) does not directly contaminate the tile's displayed numbers — each row's `pct_t` is shown verbatim, and the user gets accurate per-holding TE contributions for the ones with real values. The MISSING %T values (623 / 819 on EM) are an F12-class problem (FactSet doesn't ship `%T_implied` for long-tail bench-only constituents), not an F18 problem.

**Recommended footer disclosure** (T3.1 below) should mention BOTH F12 and the `?? 0` consequence: "TE contribution shown for 196 of 819 bench-only holdings; the remaining 623 are sourced from Raw Factors and lack per-holding %T (pending FactSet F12)."

### T1.5 — Implied active position label is correct → **GREEN**

The Bench Wt th tooltip (L5604) says "Implied active position is the negative of this." Mathematically correct (since portfolio doesn't own → active = 0 - bench_wt). No fabrication; just exposition.

### T1.6 — Aggregation behavior in `_unownedFromHold` → **GREEN**

Maps each holding 1:1 with no aggregation. No bucket sums. No section invariants to verify.

---

## T2 — Functionality parity

### T2.1 — Tile chrome strip used → **GREEN**

L3264: uses `tileChromeStrip({...})` per Phase D contract. Includes about, csv, fullscreen, resetView, hide. Correctly omits `cols`, `view`, `resetZoom` (none applicable).

### T2.2 — Drill function divergent from `oSt` → **YELLOW [PM_DECISION]**

cardUnowned uses `oDrUnowned(ticker)` instead of the standard `oSt(ticker)` per-holding drill. **Functionality gap:**
- `oSt` opens `stockModal` with full per-ticker time series, factor breakdown, MCR, etc. (rich)
- `oDrUnowned` opens `unownedModal` with 3 sum cards (Bench Wt, TE Contrib, Region) + 1 paragraph + an in-region peer-holdings table. No time series. No factor breakdown.

For a bench-only stock that is NOT in your portfolio, `oSt`'s portfolio-centric view doesn't quite fit. But `oDrUnowned` is a thinner experience — and `u.reg` is `'—'` for synth-from-Raw-Factors entries (which is the majority — see T1.1). The drill page header would say "Holdings in —" which is broken UX.

**Options:**
- (a) Replace `oDrUnowned` with `oSt` (uniform drill across all holdings tiles); accept that bench-only stocks render with mostly-empty portfolio cards.
- (b) Keep `oDrUnowned` but fix the `u.reg` fallback to use `u.co` / "no region" instead of `'—'`, and enrich the modal with Spotlight ranks (which ARE shipped on synth entries — `over`, `rev`, `val`, `qual` come from Raw Factors).
- (c) Hybrid: route to `oSt` when ticker has full data; show a lighter `oDrUnowned`-style modal otherwise.

`[PM_DECISION]` — this is a UX call. Recommend (b) for now (low surgery) and queue (c) as an enhancement.

### T2.3 — `oDrUnowned` predicate is asymmetric with `_unownedFromHold` → **YELLOW [TRIVIAL]**

**Location:** L12119–12123 vs L5559–5563.

`_unownedFromHold` (L5561): `portW = +(h.p ?? h.w ?? 0)`
`oDrUnowned` (L12121): `!((x.w || 0) > 0)`

The drill predicate ignores `x.p` entirely. It works in practice today because the parser ships `w` on every synth entry (`w: None` for synth-bench-only at parser L1277, then `?? 0` in normalize), so the `x.w` check picks up null-as-zero. But if a future parser path ships `p` instead of `w` on some entry, the drill click would silently no-op (ticker present in table → click → nothing happens).

**Fix (1 line):**
```js
let u = cs.hold.find(x =>
  x.t === ticker &&
  !(((x.p ?? x.w) || 0) > 0) &&
  ((x.b || x.bw || 0) > 0)
);
```

`[TRIVIAL]` — same fix applied symmetrically.

### T2.4 — Drill modal `u.reg` is `'—'` for synth holdings → **YELLOW [TRIVIAL]**

**Location:** L12129 `const uReg = u.reg || '—';` and L12132 filter `cs.hold.filter(h=>h.reg===u.reg ...)`.

When `u.reg` is null (the majority case for synth bench-only — verified empirically: parser ships `reg` for slim-Security holdings via `enrichHold`, but synth entries get `reg` from `_enrich_holding(synth)` at L1302 only if security_ref has a SEDOL match, which is variable coverage), the drill modal renders:
- Header sub-strip: "Region: —"
- Body callout: "Your Holdings in — (N)"
- Peer table: filtered by `h.reg === '—'` — likely 0 matches, so the section vanishes (the conditional `${secHold.length?...:''}` saves it).

**Fix:** fall back from `reg` to `co` (country, much higher coverage) → header chip says "Region: <country>". Or treat `u.reg == null` as a hide-section.

`[TRIVIAL]` — 2-3 lines.

### T2.5 — No per-week routing → **YELLOW [PM_DECISION]**

L3265 calls `${rUnowned(_unownedFromHold(s))}` synchronously inside `rExp()` template, where `s = cs` (latest detail layer). Per ARCHITECTURE.md §4.4, render fns reading per-week dimensions should go through accessors. cardUnowned reads `cs.hold[]` directly.

For a historical week (`_selectedWeek != null`), the user sees the LATEST week's bench-only list, regardless of which week they selected from the header chevron. This is **silently wrong** — the bench universe + per-holding %T values change week to week.

The lint at `lint_week_flow.py --strict` should be flagging this. Verify — and if not flagged, the lint may be missing this site (cs.hold inside `_unownedFromHold` is somewhat indirect).

**Options:**
- (a) Wire `_unownedFromHold(s)` through a `getHoldForWeek(weekDate)` accessor (not yet implemented per the accessor table in ARCHITECTURE §4.4 — there is no `getHold` accessor yet).
- (b) Hide cardUnowned with an "historical-week not available" banner when `_selectedWeek != null`, similar to other detail-layer-only tiles.
- (c) Suppress only the table rows but leave header (consistent with cardThisWeek's idio pattern).

`[PM_DECISION]` — preference: (b) until per-week holdings detail is shipped (B114).

### T2.6 — Universe-pill behavior → **GREEN**

The audit asked: "Universe pill behavior — should cardUnowned even respond to it (it IS a universe-defining concept)?" Inspecting L723 (the universe-pill `<button id="agg-pill-benchmark">`):
> `title="In Benchmark: every constituent of the benchmark (h.b > 0). INCLUDES the portfolio overlap. For pure bench-not-port, see the cardUnowned tile."`

The dashboard's own UI text routes users to cardUnowned as the "pure bench-not-port" view. **cardUnowned correctly does NOT respond to `_aggMode`** — it is the universe-defining tile for "bench minus port". This is intentional per the universe-pill tooltip design.

### T2.7 — Sort wiring → **GREEN**

Every `<th>` (L5600–5605) has `onclick="sortTbl('tbl-unowned',N)"`. Every `<td>` (L5589–5594) has `data-sv` for sort-by-value. Sort behavior should work on all 6 columns including text (Sector, Country, Name).

Minor: L5589 ticker `data-sv="${u.t||''}"` sorts by SEDOL not by ticker-region label. Probably fine since the user-visible text and sort-key both reflect "ticker identity" (SEDOL is parser-canonical). Same pattern as cardHoldings.

### T2.8 — CSV export → **GREEN**

L3264: `csv:"exportCSV('#cardUnowned table','unowned_risk')"`. Stable selector, stable filename. Captures all visible rows (top 10 only — sorted bench-only set). If the user wants the full 819-row list including the 623 with `tr=0`, the cap-to-top-10 hides it; consider a "download full CSV" alternative or remove the slice on the export path. `[PM_DECISION]`.

### T2.9 — `data-col` attributes complete → **GREEN**

All 6 cells have `data-col`. cardUnowned's `data-col` set: `t, n, sec, co, bw, tr`. (Note `bw` not `b` — that's fine since the displayed column is bench-weight per L5604 label "Bench Wt".)

### T2.10 — Right-click note hook → **GREEN**

L3264 card-title: `oncontextmenu="showNotePopup(event,'cardUnowned');return false"`. Present.

### T2.11 — Fullscreen → **GREEN**

L3264: `fullscreen:"openTileFullscreen('cardUnowned')"`. Standard pattern.

### T2.12 — `cs.hold.find` direct vs accessor → **YELLOW (cross-tile)**

L12119: `cs.hold.find(...)` — direct read. Per ARCHITECTURE.md §4.4 lint, this should go through an accessor for per-week safety. The drill is for the latest week regardless of `_selectedWeek` (consistent with the same gap in T2.5). Once a `getHoldForWeek(weekDate)` accessor lands, this changes.

---

## T3 — Design consistency

### T3.1 — Empty state uses `<p>` not `.empty-state` → **YELLOW [TRIVIAL]**

L5578: `return '<p style="color:var(--txt);font-size:12px">No unowned risk data</p>';`

ARCHITECTURE §4.3 lists `.empty-state` as one of the 10 canonical CSS classes, with `.empty-state-hint` for explanatory subtitle. Other audited tiles (cardWeekOverWeek L2769) use the canonical class.

**Fix:**
```html
<div class="empty-state">No unowned risk data
  <div class="empty-state-hint">All benchmark holdings are also held in the portfolio (or no benchmark loaded).</div>
</div>
```

`[TRIVIAL]`.

### T3.2 — No footer hairline disclosing synth path → **YELLOW [TRIVIAL but PM-facing]**

The tile silently presents the top-10 ranking as if it were a top-10 of the FULL bench-only universe. The truth is more nuanced and worth disclosing in a hairline footer (consistent with cardRiskByDim's F18 honest-math pattern):

> Source: cs.hold[] filtered to (port=0, bench>0). 196 of 819 bench-only holdings carry per-holding %T; the remaining 623 (long-tail bench constituents from Raw Factors) ship without %T per FactSet inquiry F12. Top 10 ranked by |%T| over the 196 with shipped values.

This puts the limitation in front of the user. Same posture as the cardTEStacked footer caveat described in SOURCES.md L170.

`[TRIVIAL but coordinate]` — wording is PM-facing; recommend a 1-line footer with these numbers computed at render time (so it's accurate per strategy).

### T3.3 — Theme tokens → **GREEN**

L5589 `var(--txth)`, L5590 inherits, L5591 `var(--txt)`, L5594 `var(--neg)` — all themed. No hardcoded hex.

### T3.4 — Double tooltip on title → **YELLOW [TRIVIAL]**

L3264 has both `class="card-title tip" data-tip="..."` AND the `tileChromeStrip({about: true, ...})` (which adds an `aboutBtn` with full What/How/Source/Caveats). The tooltip is short ("Benchmark stocks not held that contribute most to tracking error. Click for detail. Right-click for notes.") and the about popup is more detailed. They overlap somewhat.

This is a cross-tile pattern (most tiles have both) — not a cardUnowned-specific issue, but worth noting. Probably leave alone; the card-title `data-tip` provides immediate hover affordance, the about button provides the deeper view.

`[NO ACTION]` — not specific to cardUnowned, leave as-is.

### T3.5 — Alignment / numeric tabular → **GREEN**

Numeric cells (`bw`, `tr`) carry `class="r"` which inherits the global `td.r { font-family: monospace; font-variant-numeric: tabular-nums }` per SOURCES.md L180. Text cells (sector, country) use default body font.

### T3.6 — Truncation on Name column → **GREEN**

L5590: `style="max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"`. Sensible. No tooltip on truncated names — the user can hover but no `title=` attr is set. Minor polish: add `title="${u.n}"` to the `<td>` so hover shows full name on truncated rows.

`[TRIVIAL but optional]`.

### T3.7 — Negative-value styling on TE column → **GREEN**

L5594 hardcodes `color:var(--neg)` for the TR cell regardless of sign. Most rows ARE positive (a not-owned bench stock contributes to TE), but a small minority can be negative (negative-correlation bench stock = diversifying-by-omission). Today the negative values render in red (the --neg color), which is misleading — they're "good" diversifying contributions. Consider `style="color:${trVal<0?'var(--pos)':'var(--neg)'};font-weight:600"`. Per SOURCES.md "negative active is good = pos color" semantic established elsewhere.

`[TRIVIAL but PM-facing]` — confirm with PM whether their intuition is "TE contribution = always red" or "negative TE contribution = green". The drill modal at L12138 has the same hardcoded `var(--neg)` for the TE Contribution stat card.

---

## Cross-tile observations

- **`?? 0` is a recurring pattern at L1872–1880.** Same fabrication for `mcr` and `tr` per holding. Worth a separate cross-tile sweep beyond cardUnowned. cardHoldRisk audit (cardHoldRisk-audit-2026-05-04.md) and cardRiskByDim-audit may overlap on this; coordinator should plan a dedicated `normalize()` discipline pass.
- **F12 (per-holding %T_implied for long-tail bench-only synth) is the upstream block.** If FactSet ships `%T_implied` per Raw Factors row, cardUnowned would gain ~620 ranked entries and the footer disclosure becomes "all 819 ranked" instead of "196 of 819". This is the highest-value F-item for this tile.
- **F18 (per-holding %T sums 94→134%) does NOT directly contaminate cardUnowned.** No aggregation on the tile. Per-row %T is what FactSet ships.
- **Tab placement.** Tile is on Exposures (verified), not Holdings as the audit task stated. Leave alone unless user wants a move.

---

## Triage queue

### `[TRIVIAL]` — coordinator can apply inline (5 items)
1. **T1.2** — Update About-registry `how:` (L1184) to match the actual filter: `Filter cs.hold[] for (h.p ?? h.w) <= 0 AND (h.b ?? h.bw) > 0. Sort descending by |tr|. Cap at top 10.`
2. **T2.3** — Symmetrize `oDrUnowned` predicate (L12119–12123): use `(x.p ?? x.w)` not just `x.w`.
3. **T2.4** — Drill modal region fallback (L12129): `const uReg = u.reg || u.co || '—';` and either hide the "Holdings in <region>" section when `u.reg == null` or rebase the filter to `h.co === u.co`.
4. **T3.1** — Replace empty-state `<p>` (L5578) with `.empty-state` canonical class.
5. **T3.6** — Add `title="${(u.n||'').replace(/"/g,'&quot;')}"` to the Name `<td>` for hover-on-truncation (L5590).

### `[PM_DECISION]` — defer to user review (4 items)
1. **T1.1** — RED: remove `?? 0` fallback on `tr` and `mcr` at L1877–1878. ~50 downstream sites need null-tolerance audit. Coordinator-scoped PR.
2. **T2.2** — Drill divergence: `oDrUnowned` vs `oSt` — keep, replace, or hybrid? Need PM call.
3. **T2.5** — Per-week routing: hide cardUnowned for historical weeks vs route through accessor (B114-blocked).
4. **T3.7** — Negative-TE cell color semantics: always red, or green-when-negative? PM convention check.

### `[BLOCKED]` — upstream / parser side (2 items)
1. **F12** — FactSet ship `%T_implied` for long-tail bench-only Raw Factors entries. Letter draft pending. (Promotes cardUnowned from 196/819 ranked to all 819 ranked.)
2. **F18** — Per-holding %T sum invariance — does not block cardUnowned directly but informs the footer disclosure wording.

### `[TRIVIAL but PM-coordinated]` (1 item)
1. **T3.2** — Add hairline footer disclosing the 196/819 truth. Wording is PM-facing.

---

## Verification checklist

- [x] Data accuracy: per-row provenance maps to `cs.hold[].pct_t` / `bw`. **Aggregate-level T1 (no aggregate row → no F18 contamination)** — confirmed.
- [ ] Data accuracy: `?? 0` fallback fabrication on `tr`/`mcr` — **RED**, fix queued (T1.1).
- [x] Empty state: returns string but uses non-canonical class. (T3.1)
- [x] Sort wired on all 6 columns; `data-sv` correct on all numeric.
- [x] CSV export wired and stable.
- [x] Row click drill: `oDrUnowned(ticker)` opens. Predicate has minor `w`-only asymmetry (T2.3).
- [ ] Per-week routing: **broken** — synchronous read of `s = cs`. (T2.5)
- [x] Theme tokens: clean, no hardcoded hex.
- [x] Right-click note hook: present (L3264).
- [x] Fullscreen + reset + hide: chrome strip wired.
- [x] Tile chrome strip in canonical Phase D pattern.
- [x] Universe-pill awareness: correctly does NOT subscribe (intentional — cardUnowned defines its own universe).
- [ ] About-registry `how:` field accurate — **wrong** (T1.2).

---

## Summary

cardUnowned is a Tier-2 insight tile (single table, top-10 by |TE|) with a clean structural design but a **RED-grade T1 data fabrication** in the upstream `normalize()` step that fabricates `tr=0` for 76% of bench-only entries (623 of 819 on EM). The tile's display is *practically* correct (top 10 are real values), but the footer's "819" count + ranked-tail are fabricated. This is the same anti-pattern that produced the April 2026 crisis — the highest-priority finding in this audit.

T2 has 4 minor functional wrinkles (about-registry stale, drill predicate asymmetric, drill region fallback broken on synth, no per-week awareness) — none cause incorrect numbers TODAY but each is a latent bug.

T3 has 4 design polish items (empty-state class, footer disclosure, neg-TE color, optional title-hover) — none data-relevant but all visible.

**Recommendation:** ship the 5 `[TRIVIAL]` fixes inline as a single commit (coordinator). Open a dedicated PR for T1.1 (the `normalize()` `?? 0` cleanup) — it touches multiple tiles, needs a downstream null-tolerance audit, and is the discipline-defining item.
