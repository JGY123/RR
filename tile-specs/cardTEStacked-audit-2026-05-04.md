# cardTEStacked — Tile Audit (2026-05-04)

**Tile:** Tracking Error — Decomposition Over Time (stacked area: Idio + Factor = Total TE, with rangeslider)
**Card DOM id:** `#cardTEStacked` — assigned at L7755
**Render fn:** `rTEStackedArea(s,factorRisk,idioRisk)` at L8027 (Plotly target `teStackedDiv`, L8029)
**Color helper:** `_teStackColors()` at L8015 (tokenized — was hardcoded rgba in v1)
**Inputs:**
- `s.hist.sum[]` — per-week `{d,te,as,beta,h,sr,pct_specific?,pct_factor?}` — primary x/y source
- `factorRisk` / `idioRisk` — passed in from `rRisk()` L7652–7666: now sourced from `cs.sum.pct_specific/pct_factor × te` when present, with a legacy heuristic (`* min(Σ|f.c|/100×1.2, 0.85)`) only as fallback for legacy files
- `_pct_specific_source` synth marker propagates through to a sum-card ᵉ badge (L7724/L7729)
**Tab:** Risk (hero, full-width)
**Width:** full
**Spec status:** v2 audit (succeeds 2026-04-24 v1) — substantial fixes shipped between v1 and v2; new findings center on the data-flow gap exposed by the May data-integrity-monitor lens.

---

## Verdict

| Track | Color | One-liner |
|---|---|---|
| **T1 Data accuracy** | **RED** (load-bearing data missing) | `s.hist.sum[]` is **empty (0 entries)** on every strategy in the current `latest_data.json` — verified via streaming probe of all 6 strategies. The chart consequently renders the "No TE history" empty-state for every strategy on a real load. The math sits on top of unverified per-week `pct_specific`/`pct_factor` (when present), not the L2-verified section-aggregate. F18 per-holding contamination does not flow into this tile (it does not aggregate per-holding %T) — but the parser hist.sum gap is functionally equivalent: zero data renders. |
| **T2 Functionality parity** | **YELLOW** | Most v1 trivials shipped (id, note-hook, drill, CSV, empty-state, theme tokens). Still missing: 3M/6M/1Y/3Y/All quick-range pills (peer drills have these), `_selectedWeek` vertical marker, range-state persistence, hover doesn't show component shares (only TE-pp). Universe-pill (Port-Held / In-Bench / All) does not affect this tile but no footer note clarifies that. |
| **T3 Design consistency** | **YELLOW** | Card-title tooltip says "stock-specific (purple, bottom) + factor (indigo, top)" but the chart actually paints amber (`--warn`) for stock-specific and cyan (`--cyan`) for factor. **Tooltip lies about colors that are 3 lines below it.** Sum-cards directly above the chart use a *third* palette — `--pri` indigo (factor) + `--acc` purple (idio). Three different color systems for the same two concepts on the same tab. |

---

## Trivial fixes (8) — agent can apply

1. **F1** — Tooltip-vs-chart color mismatch (L7758 + L7760 vs L8015–8025).
2. **F2** — Helper-copy color references undefined `--textDim` (L7760).
3. **F3** — Hovertemplate unit ambiguity persists (`%{y:.2f}%` reads as share, is actually pp-of-TE).
4. **F4** — Add `_selectedWeek` vertical marker shape in the layout.
5. **F5** — Footer disclaimer: "Universe pill does not affect this tile" + per-week pct provenance note.
6. **F6** — Empty-state message should explicitly call out the parser gap, not just "No TE history" (it's not "no" — it's "not yet shipped per-week").
7. **F7** — `legend.y:1.12` overlaps card-title on narrow viewports.
8. **F8** — `gt(s.hist.sum,'as')` is called on the sum-card but `s.hist.sum=[]` returns "—" — this is silently passed through. Wrap with explicit empty-state copy.

## Larger fixes (3) — coordinator/PM gate

9. **F9** — **Reconcile cross-tile palette.** Pick ONE pair for {factor, idio} across cardTEStacked + sum-cards + riskDecompTree + cardFacContribBars. Current: 3 different palettes for the same domain pair. Backlog as B88 (idio/factor tokens).
10. **F10** — Range-pill row (3M / 6M / 1Y / 3Y / All) above the rangeslider, mirroring drill-modal pattern (`oDr`, `oDrF`, `oDrS` at L9386, L9754, L10020). Plus rangeslider state persistence per-strategy.
11. **F11** — **Per-week pct_specific / pct_factor pipeline.** Today the chart's idio/factor split fundamentally requires per-week pct_specific values from the parser. They are sometimes missing in the latest format, in which case the chart falls back to broadcasting the latest week's split. This is a load-bearing data dependency that needs an explicit decision in the F18 inquiry track.

## PM-decision (2)

12. **F12** — Empty `hist.sum` is the dominant case today (B114 history-persistence backlog). The tile is rendering "No TE history" for every strategy. Decision: do we (a) wire to `hist.sec` aggregate-from-MCR (which `getPctSpecificForWeek()` already does for *one* week and L2 verifier confirmed sums to ~100%) so weekly history populates from sector-MCR aggregation rather than parser-direct, (b) gate the tile behind an explicit "history not yet ingested" empty-state with link to HISTORY_PERSISTENCE.md, or (c) hide the tile until B114 ships. **Recommendation: (a)** — leverages L2-verified aggregate, sidesteps F18 per-holding issue, and unlocks the most informative tile on the Risk tab. (b) is the safe interim.
13. **F13** — Should clicking a point set `_selectedWeek` to that x-date BEFORE opening the TE drill, so the drill reflects the clicked week? Today the click opens `oDrMetric('te')` at the *currently selected* week, not the clicked week.

---

## T1 — Data accuracy (RED)

### Field inventory

| # | Trace | y source | Label | Provenance |
|---|---|---|---|---|
| 1 | Idiosyncratic (stack bottom) | `h.te × (raw_s/(raw_s+raw_f))` L8042 | `Stock-Specific: %{y:.2f}%` | Per-week `h.pct_specific` if present, else broadcast `idioFrac=idioRisk/te` from latest-week split L8033 |
| 2 | Factor (stack top) | `h.te − idioVals[i]` L8044 | `Factor: %{y:.2f}%` | Implicit complement |
| 3 | Total TE (overlay line) | `h.te` L8036 | `TE: %{y:.2f}%` | Source-direct from `hist.sum[].te` |
| x-axis | week date | `isoDate(h.d)` L8035 | `%b %Y` | Source-direct |

### Findings

**T1-F1 [RED] — `hist.sum` is empty in production data; chart renders empty-state on every strategy.**
Streaming probe of `latest_data.json` (1.88 GB, 6 strategies) confirmed:
```
ACWI hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
IOP  hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
GSC  hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
IDM  hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
ISC  hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
EM   hist.sum=0 ps=0 pf=0 te=0 ps_cov=0.0%
```
The chart's L8031 empty-state fires immediately and prints "No TE history". The tile has been asserting visual presence on the Risk tab via the empty-state placeholder for an unknown duration — no data has flowed into it. Per `HISTORY_PERSISTENCE.md`, this is the B114 architectural gap (the parser produces single-snapshot files, not the multi-period merged files this tile assumes). Per `CLAUDE.md` "Two-Layer History Architecture", `hist.summary` is supposed to "always [be] loaded — all 144+ weekly entries" — but in current data, it's empty.
- **Why it matters:** the entire Risk-tab hero is non-functional. It's not wrong; it's blank. PM looking at the Risk tab today sees an empty chart slot where the most-informative TE history is supposed to live.
- **Proposed fix path:** F12 (a) — derive per-week `pct_specific` / `pct_factor` from `hist.sec` MCR aggregation (`getPctSpecificForWeek()` already does this for the selected week). This sits on top of the **L2-verified** section-aggregate path (sum to ~100% on 3,082/3,082 sector-weeks per `STRATEGIC_REVIEW.md`), not the F18-contaminated per-holding path. Plus: build `hist.sum` per-week TE values from `hist.sec` aggregate where feasible, OR hide the tile.

**T1-F2 [RED] — When `hist.sum` IS populated, the per-week `pct_specific`/`pct_factor` provenance is unverified.**
L8038–8040: when `h.pct_specific` is null on a per-week entry, the chart broadcasts the **latest-week** `idioFrac = idioRisk/te` onto every historical week. This is the same anti-pattern the April crisis surfaced (LESSONS_LEARNED.md "fabrication paths"): fall-through-on-null produces a flat fake decomposition. The legitimate sister function `getPctSpecificForWeek()` (L2328) recomputes from `hist.sec` MCR and tags `_synth:'sum_sector_mcr'` — but **this tile bypasses it.** Even when `h.pct_specific` is populated, no synth marker is rendered (the sum-cards above it DO show ᵉ when synthesized; the chart silently does not).
- **Why it matters:** asymmetric provenance on the same tab. The sum-card on L7724 reports "ᵉ Derived" when split is synth-derived; the chart immediately below does not, even when consuming the same potentially-derived data.
- **Proposed fix:** route `rTEStackedArea` through `getPctSpecificForWeek(h.d)` per-week (analog of `_wSec`/`_wCtry` per-week getters at L2377+) and surface a per-trace ᵉ badge in the legend or in the hover when synth.

**T1-F3 [RED] — Tile sits on the unverified per-holding side of the F18 split.**
This tile does NOT aggregate per-holding `%T` — it relies on portfolio-level `pct_specific`/`pct_factor`. So the F18 per-holding 94→134% deviation does NOT flow here. **However**, the tile's per-week split, when present, is parser-direct from CSV's `pct_specific`/`pct_factor` columns — and the L2 verifier (`verify_section_aggregates.py`) covers the section aggregate (Σ over sectors == pct_specific) but does NOT independently verify the per-week pct_specific column itself. The split is taken on faith. Per `LESSONS_LEARNED.md` "every numeric cell has provenance" rule (Lesson 4): the chart needs an L2-style assertion that `(idioVal[i] + facVal[i]) ≈ teVal[i]` on every week. It currently has L8042–L8044 (`tot=raw_s+raw_f||100`) which silently renormalizes — same renormalization tautology v1 caught.
- **Why it matters:** if `pct_specific + pct_factor ≠ 100` in a week (e.g., FactSet rounding, or they're *Total Risk* shares not TE shares per CSV_STRUCTURE_SPEC.md L184), the tile silently rescales. No surface artifact. No console warning.
- **Proposed fix:** add a console-warn on render if `|raw_s+raw_f − 100| > 5` on any week. Add the F18-style "Σ shares = X% (expected ~100%)" footer line that cardRiskByDim now has.

**T1-F4 [YELLOW] — `factorRisk`/`idioRisk` heuristic-fallback path is no longer a primary issue but still latent.**
v1's primary RED was the heuristic `factorRisk = totalTE × min(Σ|f.c|/100×1.2, 0.85)`. v2 of `rRisk()` (L7652–7666) now prefers parser-shipped `pct_specific`/`pct_factor` and only falls back to the heuristic when both are null. In current data, `cs.sum.pct_specific` IS populated (per `last_verify_report.log` GSC strategy) — so the primary path fires, not the heuristic. **But** the heuristic still executes for any future legacy file or any strategy where the parser drops the field. Recommend deleting the heuristic path entirely (per Hard Rule #2: "normalize() is rename-only; if X is null, leave it null") rather than keeping it as a fall-through.

**T1-F5 [YELLOW] — Hovertemplate `%{y:.2f}%` is unit-ambiguous (carry-over from v1 F2).**
L8049/L8052/L8055 still use bare `%`. Reader cannot tell "1.83%" means "1.83% of TE" or "1.83 pp tracking error." It is the latter. v1 flagged this; not yet shipped. Trivial: change to `%{y:.2f} pp` or `%{y:.2f}% TE`.

---

## T2 — Functionality parity (YELLOW)

### Checklist vs Risk-tab time-series standard (`riskHistoricalTrends`, drill modals)

| Capability | Standard | This tile | Gap? |
|---|---|---|---|
| Card id | required | `cardTEStacked` ✓ | — |
| Note-hook + tooltip on title | yes | yes ✓ | — |
| About btn (registry-driven) | yes | `aboutBtn('cardTEStacked')` ✓ | — |
| `tileChromeStrip` chrome | yes | yes ✓ | — |
| CSV export | yes | `exportTEStackedCsv()` ✓ L8087 | — |
| Reset zoom | yes | yes (via chrome) | — |
| Full screen ⛶ | yes | generic FS via chrome ✓ | — |
| Hide tile | yes | yes ✓ | — |
| Empty-state copy | yes | "No TE history" L8031 ✓ | improve message |
| 3M/6M/1Y/3Y/All quick-range pills | YES (drill modals: L9386, L9754, L10020) | ❌ rangeslider only | **YES** |
| `_selectedWeek` vertical marker | YES (per cross-tile pattern) | ❌ | **YES** |
| Plotly_click drill → `oDrMetric('te')` | yes | yes L8062 ✓ | — |
| Universe-invariance documentation | required (per cardRiskByDim pattern) | ❌ | YES (footer note) |
| Hover tooltip with breakdown | yes | partial — shows TE-pp not "X% of TE" | YES (label) |
| Range state persistence | YES (drill modals do this) | ❌ | YES |
| Footer with caveats | yes (per `tileChromeStrip` standard) | ❌ | YES |

### Findings

**T2-F1 [trivial] — Add 3M/6M/1Y/3Y/All quick-range pills.**
The rangeslider is necessary but not sufficient. Drill modals (TE drill, Factor drill, Sum drill) all expose quick-period pills. cardTEStacked is the *parent* of those drills — it should expose the same pill row. Pattern at L10020:
```js
let rangeBtns=['3M','6M','1Y','3Y','All'].map(r=>`<button class="range-btn${_teStackedRange===r?' active':''}" onclick="setTEStackedRange('${r}')">${r}</button>`).join('');
```
Place above the chart, in the existing `flex-between` row at L7756. State `window._teStackedRange` defaults to "All".

**T2-F2 [trivial] — Add `_selectedWeek` vertical marker.**
v1 F4 — still open. Inside the `Plotly.newPlot` layout (L8056–8061) add:
```js
shapes: (typeof _selectedWeek!=='undefined' && _selectedWeek) ? [{
  type:'line', xref:'x', yref:'paper',
  x0:isoDate(_selectedWeek), x1:isoDate(_selectedWeek), y0:0, y1:1,
  line:{color:THEME().tickH, width:1.5, dash:'dot'}
}] : []
```

**T2-F3 [trivial] — Universe-pill invariance footer.**
cardRiskByDim recently shipped a footer note: "Universe pill … does NOT filter this tile — TE contributions are universe-invariant per B116." Same applies to cardTEStacked: the chart shows portfolio TE decomposition over time, which is universe-invariant. Add a one-line footer below the chart in the small-text style:
```html
<div style="font-size:10px;color:var(--txt);margin-top:6px">
  TE history is portfolio-level (Total / Idio / Factor) — not universe-filtered.
  ${_pctSynth?'Idio/Factor split derived from sector-MCR aggregation (ᵉ).':''}
</div>
```

**T2-F4 [trivial] — Hover unit clarity (carry-over T1-F5).**
Standard fix: change `%{y:.2f}%` → `%{y:.2f}% TE`. Plus: add a 3rd line to the hover showing the SHARE: `Stock-Specific: %{y:.2f}% TE  (Z% of total)`. Plotly supports computed customdata for this.

**T2-F5 [trivial] — Better empty-state copy.**
L8031 says "No TE history" — but `hist.sum=[]` is the current production state, and the cause is a known parser-side gap (B114), not "data missing." Suggested copy:
```html
<p style="color:var(--txt);font-size:12px;text-align:center;padding:40px">
  Per-week TE history not yet ingested (B114 — parser writes single-snapshot files;
  cumulative history pending). When history is restored, this chart will show
  the Idio + Factor decomposition over time.
</p>
```

**T2-F6 [larger] — Range state persistence per-strategy.** v1 F12 — still open. Plotly fires `plotly_relayout` with `xaxis.range[0]` / `xaxis.range[1]`. Persist as `localStorage['rr.teStacked.range.'+cs.id]`; restore on render. Caveat per Hard Rule #3: localStorage is preferences only — a UI range is preference-class so this is allowed.

**T2-F7 [larger] — Click-to-set-week drill.** Today click opens `oDrMetric('te')` at the *currently selected week*. PM expectation: clicking a specific week's bar opens the drill at THAT week. Patch: capture `pt.x` from the Plotly click event, call `setWeek(pt.x)` first, then `oDrMetric('te')`.

---

## T3 — Design consistency (YELLOW)

### Findings

**T3-F1 [RED — but trivial fix] — Tooltip lies about colors.**
L7758 card-title `data-tip` says: "stock-specific (**purple**, bottom) + factor (**indigo**, top)".
L7760 helper-copy says: "stock-specific (**purple**) + factor (**indigo**) = total TE".

But `_teStackColors()` L8015–8025 actually paints:
- idio = `--warn` = `#f59e0b` (**amber/orange**)
- factor = `--cyan` = `#22d3ee` (**cyan**)

Three lines below the lying tooltip, the actual chart renders amber + cyan. **Tooltip is wrong.** Either (a) update tooltip text to "stock-specific (amber, bottom) + factor (cyan, top)" — minimal change, OR (b) repaint the chart in purple + indigo to match the sum-cards above it — strategic change. Recommendation: (a) is the trivial fix; flag (b) for the broader palette reconciliation (T3-F2).

**T3-F2 [YELLOW — strategic] — Three-palette inconsistency for the same domain pair.**
Inside one tab, three different color systems represent {factor, idio}:

| Surface | Factor color | Idio color | Source |
|---|---|---|---|
| Sum-card (L7723) | `--pri` (#6366f1 indigo) | `--acc` (#8b5cf6 purple) | L7724 / L7729 |
| cardTEStacked chart | `--cyan` (#22d3ee) | `--warn` (#f59e0b amber) | L8022–8023 |
| riskDecompTree | `#06b6d4` (cyan) | `#f59e0b` (amber) | L7519–7520 |
| cardFacContribBars | `--pri` (indigo) for positive, `--pri-alt` for negative | n/a (factor-only) | L8202 |

A PM scanning the Risk tab sees: indigo+purple sum-cards → amber+cyan stacked chart → cyan+amber decomposition tree → indigo bars. The brain has to remap "what does each color mean" three times. Cross-tile B88 ticket: introduce `--idio-color` + `--factor-color` tokens (or `THEME().idio` / `THEME().factor`), pick once, propagate. v1 of this audit also recommended this (B88).

**T3-F3 [trivial] — `var(--textDim)` is undefined.**
L7760 uses `color:var(--textDim)`. Grep of CSS variable definitions shows `--textDim` does NOT exist (the standard is `--txt` for text, `--txth` for high-emphasis text). The browser falls back to inherited color. Replace with `var(--txt)`.

**T3-F4 [trivial] — Legend overlap on narrow viewports.**
L8059 `legend:{orientation:'h',y:1.12,...}` puts the legend ABOVE the chart at y=1.12 — which on narrow viewports overlaps the card-title and helper-copy row. Cross-tile pattern (cardFacContribBars) puts legends below the chart. Fix: `y:-0.18` and adjust margin top/bottom accordingly.

**T3-F5 [trivial] — `gt(s.hist.sum,'as')` calls in sum-cards on empty hist.sum.**
Not strictly a cardTEStacked finding but adjacent and on the same tab. L7740 `${gt(s.hist.sum,'as')} trend` — when `hist.sum=[]`, the helper `gt` returns "—" silently. Same pattern as cardWeekOverWeek empty-state issue. Trivial: explicit empty-state.

**T3-F6 [trivial] — Helper-copy hardcoded weekly count.**
L7760 `${s.hist.sum.length} wk` — when `hist.sum=[]` this prints "0 wk", which reads as "you have data for 0 weeks" (not informative; redundant with empty-state). Hide when length=0.

---

## Section 7 — Known issues / open questions

- **Q1 — Per-week `pct_specific` / `pct_factor` provenance.** When parser ships these, are they CSV-direct columns or derived from sector-MCR aggregation? F18-style inquiry letter could attach this question. Per `last_verify_report.log`, ACWI ships pct_specific/pct_factor cleanly; IOP ships `pct_specific=null / pct_factor=null`. Inconsistent across strategies — needs explanation.
- **Q2 — Should idio/factor color match sum-cards or stay amber/cyan?** PM judgment call. The sum-card colors (indigo/purple) are the global canon; the chart colors (amber/cyan) match riskDecompTree. Picking one breaks the other.
- **Q3 — When `hist.sum=[]`, should the tile self-hide rather than show empty-state?** Per `LESSONS_LEARNED.md` Lesson 11 (cadence, not sprints), the tile is currently broken in production and shouldn't ship-as-is.
- **Q4 — F18 connection.** Per the audit's narrow brief: this tile sits on the **section-aggregate** side (verified to ~100% per L2). It does NOT aggregate per-holding %T. So F18's 94→134% does not contaminate this tile *directly*. But the tile depends on per-week pct_specific from a yet-unverified parser pipeline that the L2 monitor hasn't yet swept.

---

## Section 8 — Verification checklist

- [x] Card has a stable id (`cardTEStacked`)
- [ ] Data accuracy verified — **fails** because hist.sum=[] in production
- [ ] Per-week pct_specific provenance verified — **deferred** (needs probe with non-empty hist.sum)
- [x] L2 verifier covers the data this tile sits on (section aggregates ~100%) — **independently of this tile**
- [x] CSV export exists (`exportTEStackedCsv()` L8087)
- [x] Note-hook on title (`oncontextmenu="showNotePopup..."`)
- [x] Plotly_click drill (→ `oDrMetric('te')` L8062)
- [x] Theme-tokenized colors (was hardcoded in v1, now via `_teStackColors()`)
- [ ] `_selectedWeek` marker — open (T2-F2)
- [ ] Range pills (3M/6M/1Y/3Y/All) — open (T2-F1)
- [ ] Tooltip-color match — **fails** (T3-F1)
- [ ] Empty-state copy informative — **fails** (T2-F5; current "No TE history" reads as data-missing not architecture-pending)
- [ ] Universe-pill footer note — open (T2-F3)
- [ ] Hover unit clarity — **fails** (T1-F5 / T2-F4)
- [ ] Light theme renders — **untested**
- [ ] Narrow viewport — **untested** (legend overlap suspected, T3-F4)

---

## Cross-tile learnings to append

1. **Empty `hist.sum` is silently degrading every time-series tile on the Risk tab.** Not just cardTEStacked — cardBetaHist (`riskBetaMultiDiv`), cardRiskHistTrends, cardFacHist all consume `hist.sum`. Each tile has its own empty-state but they all emit non-informative copy. **Action: project-wide empty-state audit for hist.sum consumers.** B114 history-persistence is the single root cause; until it ships, every tile downstream paints empty-state silently.

2. **Tooltip-vs-render color drift.** When a card-title tooltip describes the chart's colors, and the chart's colors live in a separate helper function, drift is inevitable. **Pattern:** card-title tooltips should NOT call out specific colors; they should call out *concepts* ("idio at bottom, factor stacked above"). Color is a render concern, not a tooltip concern.

3. **Three-palette inconsistency for the same domain pair.** Cross-tile finding: `--idio-color` and `--factor-color` (or `THEME().idio` / `THEME().factor`) need to be canonized. Today the same domain pair has 3 palettes within one tab. B88 in v1 — still open.

4. **Time-series tiles need range pills + rangeslider, not just one.** Drill modals consistently expose both. Hero tiles (cardTEStacked, cardBetaHist) currently expose only the rangeslider. Pattern propagation needed.

5. **Per-tile L2 verification.** The L2 verifier confirms section-aggregates sum to ~100%. It does NOT yet verify time-series tile inputs (each week's `pct_specific + pct_factor ≈ 100`, each week's `te ≥ idio + fac − 0.05`). A new layer (call it L2.5 — per-week per-tile invariants) would catch this.

---

## Summary

**3-track verdict: RED / YELLOW / YELLOW.**

Top 3 findings:
1. **`hist.sum` is empty across all 6 strategies in production data — the chart has been silently rendering empty-state.** Not a bug in this tile; a B114 architectural gap. But the tile is the most visible symptom.
2. **Tooltip text describes "purple + indigo" colors but the chart actually paints "amber + cyan".** And both differ from the sum-cards directly above (indigo + purple). Three-palette inconsistency for one domain pair.
3. **Per-week `pct_specific`/`pct_factor` provenance is unverified and inconsistent across strategies** (`last_verify_report.log`: ACWI ships them, IOP doesn't). When missing, the chart broadcasts the latest-week split onto every historical week — same fall-through-on-null anti-pattern that triggered the April crisis. F18 is per-holding contamination; this is per-week-pct contamination — same family, different tile.

**Recommended next action:** decide F12 (empty-state strategy for B114-pending hist.sum) and F11 (per-week pct_specific source) FIRST — these unblock T1. Then ship the 8 trivial fixes (tooltip text, range pills, `_selectedWeek` marker, hover units, footer note, empty-state copy, legend position, weekly-count helper). T3 palette reconciliation (B88) is strategic and should be separate PR with cross-tile sweep.

---

*Audit by tile-audit subagent, 2026-05-04. Author did not modify dashboard_v7.html. Coordinator should serialize the trivial fixes; F11/F12 paired PM-gate items; B88 cross-tile palette work as separate ticket.*
