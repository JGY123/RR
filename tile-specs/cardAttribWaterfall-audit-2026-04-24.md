# Tile Spec: cardAttribWaterfall — Audit v1

> **Audited:** 2026-04-24 | **Auditor:** Tile Audit Specialist (CLI) | **Batch:** 7 (final Tier 1)
> **Status:** 🟡 YELLOW overall — T1 GREEN, T2 YELLOW, T3 YELLOW
> **Scope:** the "Factor Attribution — Return Impact" card rendered by `rFacWaterfall(s)`. Historically anonymous; an id was assigned and a note-hook added in Batch 4 (cardAttrib audit). This is the first standalone 3-track audit.
> **Numbering:** cross-tile findings numbered **B88–B91** (continuing from cardWatchlist B87).

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name (human) | Factor Attribution — Return Impact (horizontal bar, misnamed "Waterfall") |
| Card DOM id | `#cardAttribWaterfall` (dashboard_v7.html:1182) |
| Render function | `rFacWaterfall(s)` at `dashboard_v7.html:1348–1382` |
| Render target | `#facWaterfallDiv` (L1184), dynamic height `min(900, max(160, N×32+20))` with `overflow-y:auto` |
| Tab | Exposures (`tab-exposures`) — sits directly after cardFacButt/cardFacDetail grid (L1182, immediately below L1179 closing `</div>` of the g2 grid) |
| Grid width | Full-row (not wrapped in `g2`/`g3`) |
| Data source | `s.factors[]` filtered by `isFinite(f.imp)` |
| Parser path | `_build_factor_list` (factset_parser.py:847–865) → `snap_item = snap.get(fname)` → `imp = SNAP_IMP` (factset_parser.py:697, latest weekly period) |
| Drill | `plotly_click → oDrF(factor)` wired at L1381 |
| Week-selector aware | ❌ always-latest; `s.factors` is not re-derived from `_selectedWeek` (per AUDIT_LEARNINGS.md L110: no factor tile reads `hist.fac`) |
| Note-hook | ✅ L1183 (Batch 4 fix) |

**Relationship to cardAttrib:** Despite the naming, this tile and `cardAttrib` (L1305) consume DIFFERENT data:
- `cardAttribWaterfall` → `s.factors[].imp` (the 18 style factors: Value, Momentum, Size, Beta, etc.)
- `cardAttrib` → `cs.snap_attrib[]` (countries / industries / currencies classified by name)

Both come from FactSet's "18 Style Snapshot" parser pathway (factset_parser.py:646–705) but `_extract_snapshot` is called twice — once over the full snap table (→ `cs.snap_attrib`, countries/industries/currencies), and the style-factor subset is folded into `s.factors` via `_build_factor_list`. This is the 6th tile in the factor-attribution family.

---

## 1. TRACK 1 — Data accuracy (🟢 GREEN)

### 1.1 Field inventory

| Axis | Field | Source | Formatter | Notes |
|---|---|---|---|---|
| y (label) | `f.n` | parser `factor_names` set (L462, union of port+active factor col keys) | raw string | — |
| x (value) | `f.imp` | `snap_item.imp` = `SNAP_IMP` from 18-Style snap, **latest weekly period** (parser L693–L697) | `%{x:+.3f}%` hovertemplate | Signed — parser does not abs. Units already "percent" per FactSet convention. |
| color | sign of `x` | `v>=0 ? --pos : --neg` (L1366) | — | Zero maps to `--pos` (green) — cosmetic edge; trivially zero impact is rare but would mis-color green. [T1.4] |

### 1.2 Sign-convention sanity

- `f.imp` = port return impact **already signed**. Parser does no transformation (factset_parser.py:676 `"imp": gv("SNAP_IMP")`).
- FactSet's SNAP_IMP is the per-factor contribution to portfolio return vs the benchmark over the period (active return attribution). Positive = factor added return, negative = detracted.
- Hovertemplate uses `%{x:+.3f}%` — signed display. ✅ Consistent with underlying.

### 1.3 Pattern A/B/C check (per AUDIT_LEARNINGS.md parser-normalize-render layering)

- **Pattern A (`hist.X:{}`):** N/A — this tile reads `s.factors[].imp`, a scalar; no sparkline column.
- **Pattern B (parser→normalize discard):** ❌ `normalize()` does not touch `s.factors`. Parser value flows through untouched.
- **Pattern C (render re-derivation from legacy config):** ❌ no client-side recomputation. `f.imp` rendered as-is.

### 1.4 Active-vs-raw conflation (B73 scope)

**NOT a B73 site.** `f.imp` is a return-attribution number (SNAP_IMP), not an exposure (SNAP_EXP / `f.e` / `f.a`). B73 concerns views that conflate raw exposure `f.e` with active `f.a`. The waterfall consumes only `f.imp`, which is definitionally active (per-factor attribution of active return over the period). No raw-vs-active ambiguity surface here. **B73 scope does not extend to this tile.**

### 1.5 Sign-collapse (B74 scope)

**NOT a B74 site.** `Math.abs` appears only at L1355 for x-axis range computation (`xmax = ceil(maxAbs*10)/10 + 0.1`). Bar values `vals` are signed (L1354 `+(f.imp||0)`), marker color is sign-driven (L1366), hovertemplate prints signed values. The sign is preserved end-to-end. **B74 scope does not extend to this tile** — the 6th site suspected by the ask is confirmed absent.

### 1.6 Spot-check

Not run (CI-less env; user-loaded JSON required). Recommended probe when live: pick one strategy with ≥1 positive and ≥1 negative impact factor, cross-check `cs.factors.find(f=>f.n==='Value').imp` against the corresponding SNAP_IMP cell in the FactSet CSV's 18 Style Snapshot section. Sign and magnitude should match exactly (no scaling).

### 1.7 Edge cases

- **Null `f.imp`:** filter `isFinite(f.imp)` (L1350) drops them. Empty-state renders at L1353. ✅
- **All-zero impacts:** `maxAbs = Math.max(0, 0.1)` floors x-axis range at ±0.1% (L1355). Chart renders flat. Acceptable but unusual; could show an advisory.
- **Factor with `imp === 0`:** `v>=0` → colored green. Cosmetic. [T1.4 below]

### Findings (T1)

- **T1.1** [trivial] L1366: `v>=0?posC:negC` colors exact-zero impact green. Use `v>0?posC:v<0?negC:T.tickH` for a neutral zero. Low-impact; flag.
- **T1.2** [PM gate] Title says "Waterfall" but this is a diverging bar chart, not a waterfall (no running cumulative). A true waterfall would show `running_sum = Σ f.imp` stepping from 0 to total active return. PM may have intended the latter — verify intent; currently labeling mismatches visualization. If diverging bar is intended, rename tile to "Factor Return Impact" (matches subtitle).

---

## 2. TRACK 2 — Functionality parity (🟡 YELLOW)

### 2.1 Primitives scorecard (viz-tile checklist)

| Primitive | Status | Evidence |
|---|---|---|
| `plotly_click` → drill | ✅ | L1381 → `oDrF(n)` |
| Empty-state fallback | ✅ | L1353 |
| Note-hook (`oncontextmenu showNotePopup`) | ✅ | L1183 (Batch 4) |
| Card-title tooltip (`tip`/`data-tip`) | ✅ | L1183 |
| Card DOM id | ✅ | L1182 (Batch 4) |
| CSV export | ❌ **missing** | no button, no helper |
| Full-screen (⛶) button | ❌ **missing** | no `openFullScreen(...)` wiring for factor-impact view |
| Toolbar state persisted (`rr.<tile>.*` localStorage) | N/A | no toolbar controls |
| Theme-tokenized colors | ✅ | L1362–1363 (`--pos`/`--neg` via getComputedStyle), `T.grid / T.zero / T.tick / T.tickH` via `THEME()` L1361 |
| Week-selector aware | ❌ | reads `s.factors` (always-latest) and `s.current_date` for period label; if `_selectedWeek` set, banner says historical but tile shows latest. Same class as B72 on cardRiskHistTrends. [T2.3] |
| No PNG button | ✅ | none present |

### 2.2 Drill mirroring

- `oDrF(name)` opens the factor drill modal with exposure + return/impact sparkline (L4288). Same drill used by cardFacButt, cardFacDetail, and cardFRB. Good parity. ✅
- No modifier-key convention (shift-click, alt-click). Given the waterfall has ONE drill meaning per bar, not required. ✅

### 2.3 Parent-tile tab context

- Tile sits directly after the cardFacButt/cardFacDetail grid on Exposures tab (L1179 closes the g2 grid, L1182 opens this card). Position makes sense narratively (exposure → return impact of exposure). ✅
- No visual linking to `cardAttrib` (L1305, far below at "row 12"). Parent audit B60 already flagged for co-location — out of scope here.

### Findings (T2)

- **T2.1** [trivial] Add CSV export. The underlying data is trivially serializable (two columns: factor name, impact %). Pattern:
  ```html
  <div class="flex-between"><div class="card-title tip" ...>...</div>
    <button class="export-btn" onclick="exportFacImpactCsv()">CSV</button>
  </div>
  ```
  Helper (~6 lines): iterate `cs.factors.filter(f=>isFinite(f.imp))`, sort desc by imp, emit `Factor,Impact(%)`. Same pattern as `exportMcrCsv()` introduced in Batch 4.
- **T2.2** [trivial] Add a full-screen (⛶) button. Pattern: `<button onclick="openFullScreen('facimpact')" title="Full screen">⛶</button>`. `openFullScreen` currently dispatches to `renderFs*` handlers — a new `renderFsFacImpact(s)` would mirror `renderFsFactorMap` (already used by cardFacButt full-screen); both read `s.factors`. Small wiring addition.
- **T2.3** [trivial] Week-selector blindness. At L1359 period label reads `s.current_date`; at L1354 values read `s.factors[].imp` (always latest). When `_selectedWeek` is set, banner promises historical but this tile silently shows latest. Either (a) show a `cur = _selectedWeek || s.current_date` period label AND a muted inline note "Factor impact shown for latest week only"; or (b) index into `cs.hist.fac[name]` per the selected week. Option (a) is 2 lines; option (b) is deferred (parser-side readiness unclear, same shape as B73/B6 blockers). **Apply (a) inline as the trivial fix; (b) rolls into B73 policy.**
- **T2.4** [trivial] Header has `class="tip"` with `data-tip` but the `class="tip"` is set on the title element itself — standard pattern. Verified (L1183). No action needed; noting for template completeness.

---

## 3. TRACK 3 — Design consistency (🟡 YELLOW)

### 3.1 Plotly styling scorecard

| Aspect | Status | Evidence |
|---|---|---|
| `--pos` / `--neg` tokens (not hardcoded) | ✅ | L1362–1363 |
| `T.grid / T.zero / T.tick / T.tickH` via `THEME()` | ✅ | L1361, L1370, L1372, L1374 |
| `zeroline: true` on the axis where zero matters | ✅ | L1374 `zeroline:true, zerolinecolor:T.zero, zerolinewidth:2` |
| `paper_bgcolor / plot_bgcolor` transparent | ✅ | L1369 |
| Symmetric x-range around zero | ✅ | `range:[-xmax,xmax]` L1375 — good for diverging bars |
| Period annotation | ✅ | L1376 renders "Period ending …" when `current_date` set |
| `autorange:'reversed'` on y-axis | ✅ | L1372 — positives at top (narratively correct after desc sort at L1350) |

### 3.2 Label overlap handling

Bar count × 32 px row height caps at 900 px (L1184). Typical strategy has 18–40 factors in `s.factors[]`. Worst case: ~40 factors × 32 = 1280 px requested, but height clamps at 900 px → Plotly compresses bar spacing to fit, label y-axis `automargin:true` (L1373) accommodates long factor names. **However:** the outer div has `overflow-y:auto` but Plotly fills the div's set height — scrolling does nothing. With 40 factors in 900 px, bars are ~18 px tall, labels may overlap. **Heuristic fix:** drop the clamp and let the div expand (`height: Nfactors * 32 + 40 px` with no max), letting outer page scroll naturally. Or keep the clamp but remove the misleading `overflow-y:auto`. [T3.2]

### 3.3 Card chrome consistency

- Card-title class `tip` with `data-tip` + `oncontextmenu` note-hook: ✅ (L1183).
- No export bar / toolbar row — the card-title is the only header element. Sibling chart tiles (cardMCR, cardFRB) have a `flex-between` header with CSV / ⛶ buttons. Missing here. [T3.1]
- No period label inside the card chrome (only inside the Plotly annotation). Minor — the annotation suffices.

### 3.4 Hovertemplate

`'<b>%{y}</b><br>Impact: %{x:+.3f}%<extra></extra>'` — good sign display, good label emphasis, no ambiguity. ✅ Matches the sibling mini-chart sub-checklist added in Batch 5 (AUDIT_LEARNINGS.md L213).

### 3.5 Color-zero edge

Exact-zero impact rendered green (`v>=0` at L1366). On a diverging chart this is minor; for sign-sensitive financial displays prefer `v>0 ? pos : v<0 ? neg : neutral`. Low-impact. [T1.1]

### Findings (T3)

- **T3.1** [trivial] Add a `flex-between` header wrapping the card-title and a toolbar holding CSV + ⛶ buttons (see T2.1/T2.2). Pattern is identical to cardFacDetail (L1164–1178).
- **T3.2** [trivial] Resolve the height-clamp-vs-overflow-auto contradiction at L1184. Either (a) drop `Math.min(900, ...)` and let the container grow (outer page scrolls), or (b) keep the clamp but drop `overflow-y:auto`. Current combination is inert (Plotly doesn't scroll inside the fixed-height div). Preferred: (a) — factor impact lists stay readable at full density.
- **T3.3** [trivial] `y>=0` color branch colors zero green. Replace with signed ternary (1-line change) for sign-faithful coloring. See T1.1 — same code site, same fix.

---

## 4. Summary

| Track | Verdict | Top finding |
|---|---|---|
| T1 — Data accuracy | 🟢 GREEN | `f.imp` flows through parser unchanged; sign preserved; not a B73 or B74 site. |
| T2 — Functionality | 🟡 YELLOW | No CSV, no full-screen, no week-selector awareness. Drill + empty-state + note-hook ✅. |
| T3 — Design | 🟡 YELLOW | Themed tokens ✅, zeroline ✅. Missing export-bar chrome; height-clamp vs overflow-auto contradiction; exact-zero color edge. |

**3-bullet takeaway:**
- **Not a 6th B73 site.** `cardAttribWaterfall` consumes only `f.imp` (return attribution, definitionally active) — no raw-vs-active ambiguity. Closes the factor-family suspicion the ask raised.
- **Not a 6th B74 site.** Signed values end-to-end; `Math.abs` used only for x-axis range computation. Sign-preservation is correct.
- **YELLOW T2/T3 is primitives-parity, not correctness.** Missing CSV + full-screen + week-selector awareness + header chrome. All fixes are trivial (≤5 lines each, ≤40 total).

---

## 5. Fix queue

### TRIVIAL (all safe inline, main session can apply):

1. **T2.1** — Add CSV export button + `exportFacImpactCsv()` helper (~6 lines).
2. **T2.2** — Add ⛶ full-screen button + minimal `renderFsFacImpact` (can reuse the same Plotly config with a larger div; ~15 lines).
3. **T2.3** — Period label reads `_selectedWeek || s.current_date` + inline muted note "Factor impact shown for latest week only" when `_selectedWeek` set (~3 lines, 1 condition).
4. **T3.1** — Wrap card-title in `flex-between` with right-side toolbar (~4 lines CSS/HTML).
5. **T3.2** — Drop `Math.min(900,...)` OR drop `overflow-y:auto`; prefer dropping the clamp (1-line edit at L1184).
6. **T1.1 / T3.3** — Signed ternary on bar color (`v>0 ? posC : v<0 ? negC : T.tickH`) at L1366 (1-line edit).

**Total: 6 items, ~35 lines of code, zero behavior risk.**

### PM GATE:

7. **T1.2** — Title says "Waterfall", visualization is diverging bar. PM to decide: rename card to "Factor Return Impact" OR implement true running-sum waterfall. No code change until decision.

### BACKLOG (new, cross-tile-relevant):

- **B88** — factor-attribution family week-selector awareness. Every factor tile (cardFacButt, cardFacDetail, cardFRB, cardAttribWaterfall, Risk Decomp Tree) silently reads latest `s.factors`. Requires parser-side `hist.fac[name].imp` (may or may not already be shipped; `_extract_snapshot` preserves `weekly` periods at L683, so the data exists — the exposure to the render layer is what's missing). One-line parser edit if needed: confirm `cs.hist.fac[name][].imp` is populated (grep-confirmed factset_parser.py already preserves per-period `imp` in the snap history). **Trivial to expose** — consider promoting to the Batch-7 polish PR as a cross-tile upgrade.
- **B89** — "Waterfall" naming: if PM wants a real running-sum waterfall, spec + implement. Currently misleads the tile name.

### BLOCKED: none.

---

## 6. Primitives checklist (end-state)

- [x] Card id (`cardAttribWaterfall`) — L1182 (Batch 4)
- [x] Note-hook on card-title — L1183 (Batch 4)
- [x] `tip` + `data-tip` on card-title — L1183
- [x] Empty-state fallback — L1353
- [x] Theme-tokenized colors — L1361–1363
- [x] `plotly_click` → `oDrF` drill — L1381
- [x] `zeroline:true` — L1374
- [ ] CSV export — **T2.1 pending**
- [ ] Full-screen (⛶) — **T2.2 pending**
- [ ] Week-selector awareness — **T2.3 pending** (rolls into B88 across factor family)
- [ ] Export-bar chrome — **T3.1 pending**
- [ ] Height-clamp sanity — **T3.2 pending**

---

## 7. Cross-tile learnings to append to AUDIT_LEARNINGS.md

**Proposed new entry (short):**

> **Factor-family week-selector trap (NEW — surfaced 2026-04-24, cardAttribWaterfall; now 6 sites):** cardFacButt, cardFacDetail, cardFRB, Risk Decomp Tree, cardRiskFacTbl, and cardAttribWaterfall all read `s.factors[]` directly and silently show latest even when `_selectedWeek` is set. Parser DOES preserve per-period factor data in `snap_item.hist` (factset_parser.py:703) — exposing to render is a cross-tile sweep (B88). Same shape as the mini-chart sub-checklist trap (AUDIT_LEARNINGS.md L210).

**Proposed closure of open items:**

> **B73 active-vs-raw scope (confirmed):** cardAttribWaterfall is NOT a 6th site. Waterfall consumes `f.imp` (return-impact, definitionally active), not exposure. B73 stays at 3 sites (cardFacDetail, cardCorr, cardRiskFacTbl).
> **B74 sign-collapse scope (confirmed):** cardAttribWaterfall is NOT a 6th site. Signed end-to-end; `Math.abs` used only for axis-range. B74 stays at 5 sites (cardFRB, oDrRiskBudget, Risk Decomp Tree, cardRiskFacTbl×2, cardUnowned).

---

**Auditor note (per protocol):** No edits to `dashboard_v7.html` applied. Fix queue handed to main session for serialization.
