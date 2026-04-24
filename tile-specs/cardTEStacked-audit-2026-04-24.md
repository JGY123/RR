# cardTEStacked — Tile Audit (2026-04-24, Batch 7)

**Tile:** Tracking Error — Factor vs Stock-Specific Decomposition (stacked-area + rangeslider)
**DOM shell:** `<div class="card">` at dashboard_v7.html L3096–L3102 — **anonymous, no id** (per B78 anonymous-Risk-tab-card sweep)
**Proposed id:** `cardTEStacked` (wrapper), inner chart div stays `teStackedDiv`
**Render fn:** `rTEStackedArea(s,factorRisk,idioRisk)` L3240; `Plotly.newPlot('teStackedDiv',...)` L3256
**Call site:** `rRisk()` L3230 inside `setTimeout(…,50)`
**Inputs:** `s.hist.sum` (per-week `{d,te,as,beta,h,sr,pct_specific?,pct_factor?}`); `factorRisk` / `idioRisk` derived in `rRisk()` L3014–L3015 from `totalTE * min(Σ|f.c|/100*1.2, 0.85)`.
**Tab:** Risk (hero, full width)
**Width:** full

---

## Verdict

| Track | Color | Headline |
|---|---|---|
| T1 Data accuracy | **RED** | The `factorRisk`/`idioRisk` inputs passed in from `rRisk()` (L3014) are a **heuristic fudge**, not a measured decomposition — `factorRisk = te * min(Σ|f.c|/100 * 1.2, 0.85)` — and they are only used as fallback (line 3244-3245) because the real per-week series `h.pct_specific` / `h.pct_factor` are in fact populated by the parser (L819-820). When fallback fires on a week missing both, the chart silently paints the 50% idio / 50% factor split at the very first data point's cap, not the true split. Plus hovertemplates advertise `Factor: X%` but `y` is the TE component in **pp of TE** (factor-risk TE share scaled to `h.te`) not `% of TE` — label ambiguity worse than cardRiskFacTbl B74. |
| T2 Functionality parity | **RED** | No card id; no note-hook on card-title (B78); no `plotly_click` drill to `oDrMetric('te')`; no CSV export of the decomposition series; no `_selectedWeek` vertical marker; rangeslider state not persisted to localStorage; no full-screen (⛶) variant despite being the Risk-tab hero; empty-state is a silent `return` at L3242 which leaves the `300px` div blank on short / missing `hist.sum`. |
| T3 Design consistency | **YELLOW** | Two of three traces use hardcoded `rgba(245,158,11,...)` (amber) and `rgba(6,182,212,...)` (cyan) fill+line — no `THEME()` token wiring. Rangeslider border hardcodes `#6366f1` (L3267). Total TE line correctly uses `THEME().tickH`. Card-title lacks `class="tip" data-tip="..."`. 10px right-side helper copy is correctly muted but uses `var(--txt)` rather than `var(--txth)`. |

---

## T1 — Data accuracy (RED)

### Field inventory

| # | Trace | y-source | Label as rendered | What it actually is |
|---|---|---|---|---|
| 1 | Idiosyncratic | `h.te * (raw_s / (raw_s+raw_f))`, L3249-L3253 | `Stock-Specific: %{y:.2f}%` | TE-pp attributable to stock-specific (i.e. `h.te × idio-share`) |
| 2 | Factor | `h.te - idioVals[i]`, L3255 | `Factor: %{y:.2f}%` | TE-pp attributable to factor (complement of idio) |
| 3 | Total TE | `h.te` | `TE: %{y:.2f}%` | Total TE, pp |

### Findings

**F1 [RED] — `factorRisk`/`idioRisk` passed in as fn args are a heuristic, not a measurement.**
`rRisk()` L3014: `factorRisk = +(totalTE * Math.min(Σ|f.c|/100 * 1.2, 0.85)).toFixed(2)`.
- `Σ|f.c|` sums **signs-collapsed** factor contributions (B74 sign-collapse pattern — 5th site).
- The `* 1.2` fudge + `0.85` cap is an unlabeled heuristic — nothing in the parser or FactSet schema produces this coefficient.
- The values are then used ONLY as a fallback `idioFrac = idioRisk/te` when `h.pct_specific` and `h.pct_factor` are both missing on a given week (L3244-L3245).
- **Consequence:** for any week where FactSet omits `pct_specific` + `pct_factor`, the chart paints a fake decomposition derived from the **latest-week** factor sign-collapsed Σ, projected flat onto that past week's `h.te`. This is a lie-by-default when `hist.sum` predates the riskm-data coverage.
- `factset_parser.py` L819–L820 DOES populate `pct_specific` / `pct_factor` per-hist-week from `current_rm` snapshots. Data probe (not run in this env; flag for verification) to confirm: what fraction of `hist.sum[]` rows actually carry both fields across the 7 strategies?
  - Fix path: if fraction ≈ 100%, drop the `idioFrac`/`facFrac` fallback entirely and render `'No decomp data'` empty-state for missing weeks. If fraction < 100%, make the fallback explicit in UI — render those weeks dashed or with a banner.

**F2 [RED] — Hovertemplate label semantics ambiguous.**
`Stock-Specific: %{y:.2f}%` at L3259, `Factor: %{y:.2f}%` at L3262. The `%` unit suffix is ambiguous: reader cannot tell whether `1.83%` means "1.83% of portfolio TE" or "1.83pp of tracking error". It is the latter (absolute TE-pp) but the bare `%` reads as a share. Fix: `Stock-Specific: %{y:.2f}pp (of TE)` or `Stock-Specific: %{y:.2f}% TE`.

**F3 [RED] — Stack math collapses to a normalization tautology when both `pct_*` present.**
L3252: `tot = raw_s + raw_f || 100`. When parser supplies `pct_specific + pct_factor ≠ 100` (e.g. rounding, or they are % of **Total Risk** not TE — see CSV_STRUCTURE_SPEC.md L184: "pct_specific/pct_factor are % of Total Risk, not % of TE"), the code silently renormalizes to 100% of TE. That is algebraically fine for the stack, but it means the tile is **not** showing the Total-Risk vs TE distinction that the underlying fields encode. Audit implication: `pct_factor` + `pct_specific` are per-parser docs **Total Risk** shares, not TE shares — using `h.te * (raw_s/tot)` is a conceptual mismatch. Same class of error as cardFRB's `% of factor risk` vs `% of TE` confusion (B74).

**F4 [YELLOW] — `_selectedWeek` not marked.**
No vertical line at the user-selected week (same pattern as cardRiskHistTrends pre-B72 fix). Add a `shapes:[{type:'line', x0:_selectedWeek, x1:_selectedWeek, ...}]` when `_selectedWeek` is set. The historical-week amber banner promises a focused view, chart silently doesn't acknowledge.

**F5 [YELLOW] — Week-selector-trap on fallback constants.**
Even if `_selectedWeek`-aware, the `idioFrac`/`facFrac` fallback is computed from `s.sum` (latest week) not from `getSelectedWeekSum()`. If user picks a week predating the riskm-data coverage AND the chart falls back, the fallback is based on the wrong week's factor breakdown. Secondary to F1; fully fixed by dropping the fallback.

**F6 [YELLOW] — Empty-state silent return.**
L3242: `if(!hist.length) return;`. Leaves the 300px div blank + no message. Should write `'<p style="padding:20px;color:var(--txt)">No TE history</p>'` into `teStackedDiv`.

---

## T2 — Functionality parity (RED)

### Checklist vs Risk-tab chart-tile standard

| Capability | Status | Line |
|---|---|---|
| Card id (`cardTEStacked`) | ❌ anonymous | L3096 |
| Card-title tooltip (`class="tip" data-tip="..."`) | ❌ | L3098 |
| Card-title note-hook (`oncontextmenu=showNotePopup`) | ❌ | L3098 |
| `plotly_click` drill → `oDrMetric('te')` | ❌ none | L3256 |
| CSV export of decomposition series | ❌ | — |
| Rangeslider persistence (`localStorage.rr.te.range`) | ❌ | L3267 |
| `_selectedWeek` vertical marker | ❌ | L3256-3271 |
| Full-screen (⛶) variant | ❌ | — |
| Empty-state fallback | ❌ silent return | L3242 |
| Theme-tokenized colors (fill + line) | partial — only Total TE line uses `THEME().tickH` | L3258-L3264 |
| Helper copy ("X weeks · drag range slider to zoom") correctly signals affordance | ✅ | L3099 |

### Findings

**F7 [trivial] — Missing `id="cardTEStacked"` on wrapper.** L3096 `<div class="card" style="margin-bottom:16px">` → `<div class="card" id="cardTEStacked" style="margin-bottom:16px">`. Unblocks note-hook, screenshot-by-id, cross-ref in tile-spec index.

**F8 [trivial] — Add note-hook + tooltip on card-title.** L3098: replace `<div class="card-title" style="margin:0">Tracking Error — Factor vs Stock-Specific Decomposition</div>` with
```
<div class="card-title tip" style="margin:0" data-tip="Weekly decomposition of tracking error into factor-model-explained (cyan) and stock-specific residual (amber) components. Total TE line overlays both. Drag the rangeslider to zoom." oncontextmenu="showNotePopup(event,'cardTEStacked');return false">Tracking Error — Factor vs Stock-Specific Decomposition</div>
```

**F9 [trivial] — Wire `plotly_click` drill.** After `Plotly.newPlot('teStackedDiv', ...)` at L3256-L3271:
```
document.getElementById('teStackedDiv').on('plotly_click',()=>oDrMetric('te'));
```
Preferred: clicking any point opens the TE drill modal at the clicked x-date — would require `setWeek(pt.x)` before `oDrMetric('te')`. Start with plain drill, enhance with week-set in follow-up.

**F10 [trivial] — Add CSV export button.** In the flex-between right side at L3099, add alongside the helper-copy span:
```
<button class="export-btn" onclick="exportTEStackedCsv()" style="font-size:10px" title="Download decomposition series">CSV</button>
```
Plus helper `exportTEStackedCsv()` emitting columns `date,total_te,factor_te_pp,specific_te_pp` for all weeks in `cs.hist.sum`.

**F11 [non-trivial, PM gate] — Full-screen variant.** cardTEStacked is the Risk-tab hero (full-width, 300px). A ⛶ button opening a 90vh modal is consistent with cardScatter / cardCountry / cardRegions conventions. Deferred — needs PM green-light + a reusable `openFsChart(renderFn, args)` helper to avoid code duplication with 4 other FS variants.

**F12 [non-trivial] — Rangeslider state persistence.** Plotly fires `plotly_relayout` with `xaxis.range[0]` / `xaxis.range[1]` when user drags. Write `{range0, range1}` to `localStorage['rr.teStacked.range']` on relayout; restore on render. Trivial code, non-trivial because it interacts with strategy switch (must reset or scope per-strategy) — flag for PM decision.

**F13 [trivial] — `_selectedWeek` vertical line.**
Inside the `Plotly.newPlot` layout object (L3266-L3271) add:
```
shapes: (typeof _selectedWeek!=='undefined' && _selectedWeek) ? [{
  type:'line', xref:'x', yref:'paper',
  x0:_selectedWeek, x1:_selectedWeek, y0:0, y1:1,
  line:{color:THEME().tickH, width:1, dash:'dot'}
}] : []
```

**F14 [trivial] — Empty-state write-through.** L3242: replace `if(!hist.length) return;` with
```
if(!hist.length){document.getElementById('teStackedDiv').innerHTML='<p style="padding:20px;color:var(--txt)">No TE history</p>';return;}
```

---

## T3 — Design consistency (YELLOW)

### Findings

**F15 [trivial] — Hardcoded fill+line colors (2 traces).** L3258 `fillcolor:'rgba(245,158,11,0.25)', line:{color:'rgba(245,158,11,0.8)'}` (amber idio) and L3261 `fillcolor:'rgba(6,182,212,0.22)', line:{color:'rgba(6,182,212,0.65)'}` (cyan factor). Colors match riskDecompTree's idio (`#f59e0b` L2915) and factor (`#06b6d4` L2914) — but those are *also* hardcoded. Either:
- (a) introduce `THEME().idio` / `THEME().factor` tokens (preferred, tokenizes the two domain-concept colors for re-use across cardTEStacked + riskDecompTree + future tiles), OR
- (b) extract module-level constants `IDIO_COLOR = '#f59e0b'`, `FACTOR_COLOR = '#06b6d4'` with alpha helpers.
Low-risk patch = (b), strategic fix = (a).

**F16 [trivial] — Rangeslider border hardcodes `#6366f1`.** L3267 `bordercolor:'#6366f1'`. Replace with `THEME().tickH` or a new `--pri` token. Matches the fragmentation already logged in learnings (`rRegChart` port/bench hardcodes, `rMultiBeta` L3282 `#6366f1`).

**F17 [trivial] — Helper copy color.** L3099 `color:var(--txt)` for the "X weeks · drag range slider to zoom" span — should be `var(--txth)` to match the helper-copy convention on other Risk-tab cards (e.g. L3108 click-hint uses `var(--pri)`; muted helper text elsewhere uses `var(--txth)`). Minor.

**F18 [YELLOW — PM gate] — Legend position.** `legend.orientation:'h', y:1.12` (L3269). On narrow viewports the legend overflows the card-title above. Consider `y:-0.22` (below chart) or `y:1.02` with smaller font. Cross-tile pattern — worth unifying across all chart cards.

---

## Fix queue

### TRIVIAL — agent can apply (8 items)

1. **F7 — Add `id="cardTEStacked"`** on wrapper L3096. *(B78 sweep.)*
2. **F8 — Add `class="tip" data-tip="..." oncontextmenu="showNotePopup(event,'cardTEStacked');..."`** on card-title L3098.
3. **F9 — Wire `plotly_click` → `oDrMetric('te')`** after L3271.
4. **F10 — Add CSV button + `exportTEStackedCsv()` helper** (header `date,total_te,factor_te_pp,specific_te_pp`).
5. **F13 — Add `_selectedWeek` vertical marker shape** in layout.
6. **F14 — Empty-state write-through** at L3242.
7. **F15b — Extract `IDIO_COLOR` / `FACTOR_COLOR` module constants**; replace hardcoded rgba at L3258 + L3261.
8. **F16 — Replace rangeslider `bordercolor:'#6366f1'`** with `THEME().tickH` at L3267.

### PM-GATE / NON-TRIVIAL (5 items)

9. **F1 / F3 — Resolve `pct_specific` + `pct_factor` semantics.** Are they % of Total Risk (per CSV_STRUCTURE_SPEC.md L184) or % of TE? If Total Risk: using `h.te * (raw_s/tot)` is wrong — needs a rescale by `h.total_risk / h.te` or the trace needs to be re-labeled "Total Risk decomposition (%)" on a 0-100 axis. **PM decision: what is this chart actually showing?** Ties into B74 (sign-collapse) and B73 (active-vs-raw) as part of a broader "factor tile semantics" cleanup.
10. **F1 — Drop heuristic `factorRisk`/`idioRisk` fallback.** Replace with either: (a) explicit "no decomp data" empty-state for weeks missing `pct_*`, or (b) linear interpolation from nearest covered week. Requires data-probe to learn coverage first.
11. **F11 — Full-screen (⛶) variant.** Needs reusable modal wrapper; one-off code bloats single-file dashboard.
12. **F12 — Rangeslider state persistence to localStorage.** Fine-grained but interacts with strategy switch — needs policy decision (per-strategy vs global, reset-on-load vs restore).
13. **F18 — Legend position sweep** across Risk-tab cards.

### BACKLOG (cross-tile, new)

14. **B88 (new) — `THEME().idio` / `THEME().factor` tokens.** Single token pair for the factor-vs-idio semantic pair, consumed by cardTEStacked traces (L3258, L3261), riskDecompTree nodes (L2914, L2915), and any future tile decomposing factor vs stock-specific. Extends `THEME().pos`/`neg` pattern.

15. **B89 (new) — Unified "weekly TE heuristic" audit.** `rRisk()` L3014 synthesizes `factorRisk` via a heuristic coefficient (`*1.2`, capped at 0.85). This value flows to riskDecompTree, cardTEStacked, and `rRiskFacBarsMode`. **Grep every consumer of `factorRisk`/`idioRisk` computed in `rRisk()`** — anywhere it is treated as ground truth is suspect. Likely overlaps with F1.

---

## Verification checklist (from template)

- [x] Card wrapper has a stable id proposal (cardTEStacked)
- [ ] Data accuracy verified via probe (**deferred — needs `latest_data.json` loaded**; critical F1/F3 unresolved without it)
- [ ] Edge cases handled (empty hist.sum → F14; missing `pct_*` → F1; single-week → untested)
- [x] Stack stacks correctly when both fields present (L3248-L3255 math is sound *within* its semantic frame)
- [ ] CSV export exists (F10)
- [ ] Full-screen variant (F11, deferred PM gate)
- [ ] `_selectedWeek` marker (F13)
- [ ] Note-hook on title (F8)
- [x] Plotly Total-TE trace uses `THEME().tickH` (only tokenized trace)
- [ ] Plotly idio + factor traces tokenized (F15)
- [ ] Rangeslider border tokenized (F16)
- [ ] Theme (dark + light) both render correctly — **untested in this audit** (hardcoded rgba values are dark-theme-tuned; likely suboptimal on light)
- [ ] Responsive (narrow viewport) — **untested**
- [ ] Drill on click — F9 pending

---

## Cross-tile learnings to append to AUDIT_LEARNINGS.md

- **Heuristic-derived inputs flowing into multiple chart tiles.** `rRisk()` L3014 synthesizes `factorRisk` / `idioRisk` from `Σ|f.c|/100 * 1.2` capped at `0.85` — an unlabeled fudge that is then passed to `riskDecompTree`, `rTEStackedArea`, and used as implicit fallback when real per-week fields are missing. Audit heuristic: **any multi-tile render helper that synthesizes a value not traceable to parser output deserves a skeptic's review** — the synthesized value likely has a policy question (coefficient/cap) that should be user-visible or sourced from the parser.
- **Hovertemplate unit ambiguity on decomposition charts.** When a stacked trace's `y` is in data-units (pp of TE) but the `%` suffix reads as a share, users misread the chart. Standard: label decomposition chart y-values with explicit `pp` or `%-of-total` suffix. Extends to cardFRB donut and riskDecompTree.
- **Parser-doc vs render-site semantic mismatch on `pct_specific` / `pct_factor`.** CSV_STRUCTURE_SPEC.md L184 explicitly states these are "% of Total Risk, not % of TE", yet `rTEStackedArea` L3253 uses them as if they were TE-shares. Any render reading these fields deserves a check that it rescales to TE before multiplying by `h.te`. Cross-tile — also used in dashboard_v7_partial.html:6026-6027 (unclear if active in current `dashboard_v7.html`).
- **Anonymous-Risk-tab-card sweep (B78) continues:** cardTEStacked joins cardCorr, cardRiskFacTbl, etc. as a no-id hero-tile. After this batch, run a full grep for `<div class="card">` (no id, no `tile-` class) inside `#tab-risk` to close out B78.

---

## Summary

**3-track verdict: RED / RED / YELLOW.**

Top 3 bullets:
- T1 RED = heuristic-derived `factorRisk`/`idioRisk` inputs + semantic mismatch between parser-doc (`pct_*` = % of Total Risk) and render-site multiplication (`h.te × share`) + sign-collapse on source `Σ|f.c|`. Chart is structurally mis-decomposing whenever the heuristic fallback fires AND mis-scaling even when it doesn't.
- T2 RED = no card id, no note-hook, no drill, no CSV, no `_selectedWeek` marker, no empty-state, no full-screen. Most-comprehensive functionality gap across the Batch 7 audit.
- T3 YELLOW = 2-of-3 Plotly traces hardcode rgba colors; rangeslider border hardcodes `#6366f1`. Ticket for `THEME().idio`/`THEME().factor` tokens (B88).

Recommended next action: land 8 trivial fixes together (id assignment + note-hook + tooltip + drill + CSV + `_selectedWeek` marker + empty-state + theme tokens). Then escalate F1 + F3 + B89 as paired PM-gate items — they are semantically linked and should not be fixed piecemeal.

---

*Audit by tile-audit subagent, 2026-04-24. Author did not modify dashboard_v7.html. Coordinator should serialize the 8 trivial fixes on main; defer F11/F12 pending PM confirmation; run data probe on `cs.hist.sum[].pct_specific` coverage before landing F1.*
