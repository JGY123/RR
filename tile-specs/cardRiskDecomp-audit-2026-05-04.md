# cardRiskDecomp — Tile Audit (2026-05-04, v1)

**Tile:** Risk Decomposition Tree — total TE → {Factor Risk, Stock-Specific Risk} → top contributors
**Card DOM id:** `#cardRiskDecomp` (assigned at L7525)
**Render fn:** `riskDecompTree(s, factorRisk, idioRisk)` at L7494, called from `rRisk()` at L7756
**Helpers:** `mkNode(id,label,val,pct,color,kids)` L7485, `toggleDtNode(id)` L7478
**Inputs:**
- `s.sum.te` — total tracking error (header big-number)
- `factorRisk`, `idioRisk` (passed in from `rRisk()` L7656–7670; sourced from `cs.sum.pct_factor` × `cs.sum.te` / `cs.sum.pct_specific` × `cs.sum.te`, with legacy heuristic fallback for files lacking those fields)
- `s.factors[]` — factor list with `n` (name), `a` (active exp), `c` (TE %, scaled in `normalize()` L1900–1903 to sum to `pct_factor`)
- `s.hold[]` — `tr` (= `pct_t` after `normalize()` L1878), `n`, `t`
- `FAC_GROUPS` registry at L8532 — substring-matched against factor names
**Tab:** Risk (mid-stack, full width — sits between `riskHistoricalTrends` and `cardTEStacked`)
**About registry:** PRESENT (L1275–1282), 5-field complete — title / what / how / source / caveats / related
**SOURCES.md entry:** **MISSING** (caught — there is no cardRiskDecomp section in `SOURCES.md`)
**Spec status:** v1 (FIRST audit on file)

---

## Verdict

| Track | Color | One-liner |
|---|---|---|
| **T1 Data accuracy** | **RED** | Idio side displays `h.tr` (renamed from `pct_t`) as a label like "5.20%" — the SAME data the F18 inquiry just exposed as summing to 94–179% across strategies (NOT the ~100% the column name implies). Top-7 holdings sum to 41.8%–71.8% under an "Idio Risk" parent labeled e.g. "63.2%" with NO unit clarification. The factor side renormalizes via `normalize()` so its sum-of-children equals its parent — but the idio side does not. Per-week (`_selectedWeek`) routing is missing entirely (`cs.factors`/`cs.hold` read directly; should use `_wFactors()` / per-week analog). One unmapped factor (`Exchange Rate Sensitivity`) silently lands in an "Other" bucket because of an `'FX Sensitivity'` substring miss in `FAC_GROUPS`. |
| **T2 Functionality parity** | **YELLOW** | Tile contract done well: chrome strip migrated, About registered, right-click note hook present, generic fullscreen via `openTileFullscreen`. Click-to-drill missing (caveats own-document this); no controls (sort / threshold / N picker / signed-vs-absolute toggle); no CSV export; no toggle for "Top 7" depth (hardcoded `.slice(0,7)`); no footer block / sum-row caveat (peer tiles like cardRiskByDim now have one). Same surface quality as cardTEStacked v2 minus the CSV button. |
| **T3 Design consistency** | **YELLOW** | Color palette is **inconsistent with peers on the same tab**: tree uses cyan `#06b6d4` for factor + amber `#f59e0b` for idio (matches cardTEStacked area chart). But the sum-cards two `<div>`s above the tree (L7727, L7732) use indigo `--pri` for factor + purple `--acc` for idio. Two color systems, same domain pair, same tab, separated by 30 lines. All values are inline hex / inline styles (not tokenized). Tooltips on the tile-title only — leaf nodes have no hover information. No empty-state, no footer caveat, no "as-of" label. Bar widths use a magic-number scale (`Math.min(|h.tr|*10, 100)`) and saturate at 100% for any h.tr ≥ 10pp, which is most of the top-7 in IDM/ISC. |

---

## Triage queue

### TRIVIAL (≤10 LOC each, coordinator-shippable, no PM gate)

1. **D1** — Remove the trailing `'%'` on idio leaf node `val` strings until D2 lands; replace with `'pp'` or `' TE'` to remove the false "% of TE" reading.
2. **D2** — Add `Σ-of-children = X.X% (parent {ps}%)` console.warn assertion when `|Σ|f.c| − pct_factor|>1` or `|Σ|h.tr|/te*100 − pct_specific|>10` (mirrors layered-monitoring lens from Lesson 13).
3. **D3** — Add `Exchange Rate Sensitivity` to `FAC_GROUPS.secondary` (single line in L8537), or rename `'FX Sensitivity'` → `'Exchange Rate'` so the substring matches.
4. **D4** — Surface synth marker on the parent nodes when `cs.sum._pct_specific_source !== 'native'`: append `<span style="color:var(--warn);font-size:11px;margin-left:4px">ᵉ</span>` to the parent labels (mirror sum-cards L7728/L7733).
5. **D5** — Honor `_selectedWeek`: replace `s.factors` with `_wFactors()` (L7500) and replace `s.sum.te` reading at L7495 with `getSelectedWeekSum().te`.
6. **F1** — Add tile-title `<span style="font-size:10px;color:var(--txt);font-weight:400;margin-left:8px">${facKids.length+1} factor groups · top-7 holdings</span>` count badge; matches `cardRiskHistTrends` (L7582).
7. **F2** — Add a hairline footer block: `<div id="rdtFooter" style="font-size:10px;color:var(--textDim);padding:6px 4px 0;border-top:1px solid var(--grid);margin-top:8px">…</div>` with the unit caveat: "Idio leaves are |%T| (FactSet `pct_t`) — same column under inquiry F18; Σ may not equal parent."
8. **F3** — Make Top-N configurable: hard `7` → `_rdtTopN` localStorage (`'rr.cardRiskDecomp.topN'`, default 7), with a tiny inline `<select>` in the chrome row (mirrors `_rbdThresh` pattern L7894 in cardRiskByDim).
9. **F4** — Add `oSt(h.t)` click handler to idio leaves (drill to single-stock modal — `oSt` already exists, used in cardThisWeek L4269 etc.).
10. **F5** — Add `oDrF(f.n)` click handler to factor leaves (drill to single-factor modal — used in cardFacContribBars).
11. **F6** — Add `aria-expanded`/`role="button"` on the toggle div + keyboard support (Enter/Space). Currently mouse-only.
12. **X1** — Token-ize colors: cyan `#06b6d4` → `var(--cyan)` (L7523), amber `#f59e0b` → `var(--warn)` (L7521 + L7524), `#818cf8` → `var(--pri)` (L7515), `#6366f1` → `var(--pri)` (L7517). All four are theme-aware; current inline hex breaks light theme.
13. **X2** — Add tooltip `title` / `data-tip` to every leaf node `mkNode` call (currently only the title bar has a tooltip).
14. **X3** — Replace bar-saturation magic `Math.min(|h.tr|*10, 100)` (L7521) with a proportional scale: `(|h.tr|/maxAbsTr)*100` (max over the 7 displayed). Avoids the "everything is full bar" effect on Nebius-like outliers.

### TRIVIAL-BUT-LARGER (5–25 LOC; coordinator + brief sanity check)

15. **D6** — Add cardRiskDecomp section to `SOURCES.md` with the 5-row provenance table (Total TE / Factor parent / Idio parent / Factor leaves / Idio leaves), including the F18 anti-pattern callout for Idio leaves.
16. **D7** — Wire **Σ idio = pct_specific** sanity at the **render boundary**: when `Σ|h.tr|` (over non-cash holdings) deviates from `pct_specific × te / 100` by >5pp, render an inline warning row above the idio sub-tree: "⚠ Top-N |%T| sum (X.X%) ≠ pct_specific × TE (Y.Y%) — see inquiry F18". This is the cardRiskByDim footer pattern (8606) applied here.
17. **F7** — CSV export: tree-flattened with columns {level, label, value, pct, parent}. Implement as `exportRiskDecompCsv()` — mirrors `exportTEStackedCsv()` shape. Wire to `tileChromeStrip` `csv:` slot. ~25 LOC.
18. **F8** — Empty-state: when `s.factors.length===0 && topH.length===0`, render the same "—" placeholder cardRiskHistTrends uses (L7598). Today the function returns `''` if `!te`, but does NOT defend against empty factor list (L7500: `s.factors.forEach` on undefined throws when a brand-new strategy is loaded with no factor data).

### PM-GATE (decision required, design or product call)

19. **D8** — **What does the idio sub-tree promise the user?** Three options:
    - **(a)** Continue showing top-7 by `|h.tr|` (today). Document the non-100% caveat in footer + tooltip.
    - **(b)** Show top-7 by `|h.pct_s|` (FactSet stock-specific MCR) — these DO sum to `pct_specific` at the section-aggregate level (per L2 verifier `verify_section_aggregates.py` — 3,082/3,082 sector-weeks match). Aligns the idio sub-tree's children with the parent label. Requires renaming the leaf-level metric.
    - **(c)** Move idio sub-tree to a **sector** breakdown (Σ |sec.mcr| — already L2-verified) instead of per-holding. Cleaner provenance, fewer lines, parent = sum-of-children exact. **Recommendation: (c)** for parent-children math integrity; (a)+(b) both leak the F18 anomaly into a high-visibility hero tile.

20. **F9** — **Should this tile have a "Top-N depth" picker for both branches** (factor groups + idio), versus `1 + 7` hardcoded? Today factor side shows ALL factor groups (~5) and idio side shows top-7. Asymmetry is unstated.

21. **X4** — **Reconcile cross-tile palette for {factor, idio}.** Same as cardTEStacked v2 F9. Three palettes for the same domain pair on the same tab:
    - sum-cards: indigo `--pri` (factor) + purple `--acc` (idio)
    - cardTEStacked area: cyan `--cyan` (factor) + amber `--warn` (idio) — **same as the tree**
    - tree: cyan `#06b6d4` + amber `#f59e0b` — also same intent
    - 2 of 3 already aligned. Tree could match sum-cards by switching to `--pri`/`--acc`, but then the tree would no longer match the area chart immediately below it. Backlog as **B88 idio/factor tokens** (per cardTEStacked v2 audit).

---

## T1 — Data accuracy (RED)

### Field inventory

| # | Element | Source | Math | Provenance class | Verified? |
|---|---|---|---|---|---|
| D1 | Total Risk (TE) banner — value | `s.sum.te` (L7495, L7533) | direct | 🟢 sourced | yes (load-bearing single sum number) |
| D2 | Total Risk (TE) banner — color | `te>7?neg : te>5?warn : default` (L7533) | threshold | n/a | yes |
| D3 | Factor Risk parent — value | `f2(factorRisk,2)+'%'` (L7523) | `cs.sum.pct_factor × cs.sum.te / 100` | 🟡 derived (synth marker `_pct_specific_source`) | YES — but the **synth marker is silently dropped** entering the tree (D4) |
| D4 | Factor Risk parent — pct | `facPct = factorRisk/te × 100` (L7496) | identity | 🟡 derived | YES |
| D5 | Idio Risk parent — value | `f2(idioRisk,2)+'%'` (L7524) | `cs.sum.pct_specific × cs.sum.te / 100` | 🟡 derived | same caveat as D3 |
| D6 | Idio Risk parent — pct | `idioPct = idioRisk/te × 100` (L7497) | identity | 🟡 derived | YES |
| D7 | Factor group label | `grpLabels[grp]` (L7517) | direct from `FAC_GROUPS` | 🟢 sourced | static map |
| D8 | Factor group value | `grpC = Σ|f.c|` over factors in group (L7513) | sum | 🟢 sourced (post-renormalize) | yes — and Σ over groups = pct_factor exactly because of `normalize()` L1900–1903 |
| D9 | Factor leaf — name | `f.n` (L7515) | direct | 🟢 sourced | yes |
| D10 | Factor leaf — exposure label | `fp(f.a,2)+' exp'` (L7515) | direct | 🟡 partly synth (when `f._a_synth` flag is set) | YES — but the synth flag is NOT surfaced in the tree |
| D11 | Factor leaf — bar pct | `Math.abs(f.c||0)` after rescale | direct | 🟡 derived (synth flag hidden) | YES |
| D12 | Idio leaf — name | `(h.t||'?')+' — '+(h.n||'').slice(0,25)` (L7521) | direct | 🟢 sourced | yes |
| D13 | Idio leaf — value label | **`f2(h.tr,2)+'%'`** (L7521) | **direct h.tr (= pct_t after normalize)** | 🔴 **CONTAMINATED — F18 anomaly flows here** | **NO — see D1 finding** |
| D14 | Idio leaf — bar pct | `Math.min(|h.tr|*10,100)` (L7521) | magic-multiply with saturation | 🟡 derived (cosmetic) | NO — saturates for ANY |h.tr|>=10pp |

### Findings

**D1 [RED] — Idio sub-tree displays raw `h.tr` (= `pct_t`) as `f2(h.tr,2)+'%'`. The F18 anomaly flows directly into a high-visibility hero tile.**
Math walk across all 6 strategies (live data, `data/strategies/<ID>.json`, post-`normalize()`):

| Strategy | TE | pct_specific (parent) | Σ|h.tr| ALL non-cash | Σ|h.tr| top-7 (children) | Top contributor |
|---|---|---|---|---|---|
| IDM | 6.47 | 64.1 | **150.9** | 71.0 | Nebius `pct_t = 25.1` (single holding > parent) |
| EM | 5.51 | 63.2 | 96.8 | 41.8 | Zhongji Innolight 10.0 |
| ISC | 6.25 | 72.2 | 110.6 | 50.1 | Silicon Motion 18.6 |
| GSC | 6.98 | 69.9 | 111.8 | 49.7 | Silicon Motion 16.7 |
| ACWI | 6.65 | 57.2 | 153.7 | 63.6 | (similar shape) |
| IOP | 7.11 | 53.8 | 179.0 | 71.8 | (similar shape) |

The tile renders, e.g., for IDM: `Stock-Specific Risk 4.15% [64%]` as the parent, with `Nebius — 25.10%` immediately under it. A user reading this naturally infers Nebius alone contributes 25% of the portfolio's tracking error, more than the 4.15% parent total. The numbers don't lie — they're the FactSet `%T` column verbatim — but the framing makes them look like child-of-parent shares. This is the same data column under inquiry F18 (CLAUDE.md: "Σ %T = X% expected ~100%"); the inquiry itself was opened because this column does not behave as a share. **Per Lesson 12 (escalate, don't paper over): the tree should not consume this column without honoring the inquiry's footer pattern.**
- **Why it matters:** the Risk tab's two hero tiles (cardTEStacked + cardRiskDecomp) both rely on the L2-verifiable section-aggregate path for the parent number, but cardRiskDecomp drops to per-holding `%T` for the children — landing it **on the unverified side of the F18 split** (LESSONS_LEARNED.md, Lesson 13). The PM reads a parent that is L2-verified and children that are not, with no on-screen indicator that the units differ.
- **Proposed fix:** prefer **D8 (c)** (move idio sub-tree to sector breakdown — already L2-verified — Σ|sec.mcr| = pct_specific to within rounding) OR (b) (use `pct_s` for idio leaves — at least the column matches the parent semantically). If the per-holding `pct_t` view is kept (option a), add an inline ⚠ row above the idio sub-tree calling out the unit-mismatch, mirroring the cardRiskByDim footer pattern. **Until then, change the leaf label format from `f2(h.tr,2)+'%'` to `f2(h.tr,2)+' pp'` (D1 trivial)** so it doesn't read as a share.

**D2 [RED] — Σ-of-children-equals-parent integrity is asymmetric across the two sub-trees and silent on failure.**
- **Factor side:** `normalize()` L1900–1903 explicitly rescales `f.c` so that `Σ|f.c| === sum.pct_factor` after factor synthesis. The tree faithfully sums these into group totals (`grpC`, L7513), and Σ of group totals === `factorPct`. **Math is sound.**
- **Idio side:** no analogous renormalization. The 7 holdings are picked by `|h.tr|` desc, summed by FactSet `%T` raw, displayed under a parent labeled `idioPct%` (the L2 path). **No relationship.**
- The user infer-by-symmetry that the two sides have equivalent semantics. They do not.
- **Proposed fix:** add a render-time assertion (`console.warn`) when `|Σ|f.c| − pct_factor| > 1` (factor side) or `|Σ|h.tr| − pct_specific| > 10` (idio side, looser tolerance per F18) — patterned on `_b115AssertIntegrity()` (Lesson 13 layered monitoring). The warn fires per-strategy on render, surfaces in the same console pipeline as the existing integrity checks.

**D3 [YELLOW] — Per-week routing is absent. Tree always reads latest-week data even when `_selectedWeek` is set.**
- L7495: `s.sum.te` is read directly from `cs.sum`, not via `getSelectedWeekSum()` (which `rRisk()` already computes at L7641 for the sum-cards above the tree).
- L7500: `s.factors.forEach(...)` reads `cs.factors` directly. `_wFactors()` is the standard per-week getter (already in use at L7645/L7677/L7685).
- L7519: `s.hold` — there is NO per-week analog for holdings (the parser does not ship `hist.hold[]` per the two-layer architecture in CLAUDE.md). When `_selectedWeek` is set, the idio sub-tree shows latest-week holdings under a historical-week parent.
- The amber "viewing historical week" banner does NOT explain that a sub-tree's data is mixed-period.
- **Why it matters:** subtle integrity hole when a PM rewinds the week selector. The factor sum in the tree's parent reflects historical week (good); the idio leaves do not (bad). User can't tell.
- **Proposed fix:** D5 (use `getSelectedWeekSum().te` + `_wFactors()`); add an "as-of" caveat in the footer explaining holdings are always latest-week per CLAUDE.md two-layer architecture; suppress the idio sub-tree (or render it dimmed) when `_selectedWeek` is non-null.

**D4 [YELLOW] — Synth-derivation marker `cs.sum._pct_specific_source` exists but is dropped silently entering the tree.**
- L7656–7670 (`rRisk()`) computes `factorRisk`/`idioRisk` from `ws.pct_specific`/`ws.pct_factor` and surfaces the `ᵉ` derived-marker on the sum-cards (L7728, L7733).
- L7494 (`riskDecompTree`) receives the same `factorRisk`/`idioRisk` as plain numbers — the synth marker does not pass through the function signature.
- The two parent nodes display `f2(factorRisk,2)+'%'` and `f2(idioRisk,2)+'%'` with NO superscript ᵉ.
- **Why it matters:** identical numbers, identical synth status, two different transparency stories. Sum-card on top of the tree shows ᵉ; tree below it does not. Inconsistent provenance signal.
- **Proposed fix:** D4 (add `ᵉ` to both parent nodes when `s.sum._pct_specific_source && _pct_specific_source !== 'native'`).

**D5 [YELLOW] — `FAC_GROUPS` substring matcher silently misclassifies `'Exchange Rate Sensitivity'`.**
- L8537: `secondary: ['Size','Leverage','Liquidity','FX Sensitivity','Mid Cap','Earnings Variability']`
- L7504: `if (v.some(g => f.n.toLowerCase().includes(g.toLowerCase()) || g.toLowerCase().includes(f.n.toLowerCase())))`
- For factor `'Exchange Rate Sensitivity'`: `'fx sensitivity' in 'exchange rate sensitivity'` = false; `'exchange rate sensitivity' in 'fx sensitivity'` = false (longer needle in shorter haystack). Falls into `other` (L7508–7510).
- Confirmed against IDM live data — Exchange Rate Sensitivity is the only factor in the catch-all "Other" bucket.
- **Why it matters:** "Other" appears as a fifth, often-tiny group at the bottom of the factor sub-tree, semantically equivalent to "we don't know what this is" — but the factor IS a known macro factor. PM seeing "Other = X%" on the Risk tab can't tell if it's a hidden factor or a misclassification.
- **Proposed fix:** D3 — single line: change `'FX Sensitivity'` → `'Exchange Rate'` (the substring). Or add `'Exchange Rate Sensitivity'` and `'Currency'` to `secondary` (the worldwide-model factors per CLAUDE.md L120).

**D6 [YELLOW] — Magic-multiply bar scale `|h.tr|*10` saturates for outliers, hiding the very ranking the bar exists to show.**
- L7521: `Math.min(Math.abs(h.tr||0)*10, 100)` — designed to show "h.tr=10pp ⇒ full bar."
- Across all 6 strategies, the top-1 idio holding has `|h.tr|` ≥ 10 in 4 of 6 (IDM 25.1, ISC 18.6, GSC 16.7, EM 10.0). Top-7 in IDM has 4 holdings ≥ 10pp — all four bars render at 100%, visually identical.
- **Why it matters:** the bar is supposed to communicate relative magnitude. Saturation collapses the signal exactly where it matters most (high-conviction, high-risk positions).
- **Proposed fix:** X3 (proportional scale relative to `maxAbsTr` over the displayed 7).

**D7 [YELLOW] — `SOURCES.md` has no cardRiskDecomp section.**
- Hard rule #4 (CLAUDE.md L186): "Every numeric cell has provenance. SOURCES.md is the index."
- All 14 inventoried elements above (D1–D14) are absent from SOURCES.md.
- Without SOURCES.md, the F18 contamination on D13 cannot be documented in the canonical place; the next auditor (or a new agent) starts from zero.
- **Proposed fix:** D6 (add the section — 5-row provenance table mirroring the cardSectors section template).

**D8 [GREEN] — Cross-strategy probe of source paths confirms the tree's inputs populate cleanly on all 6.**
Verified directly against `data/strategies/{IDM,EM,ISC,GSC,ACWI,IOP}.json`:
- `s.sum.te` populated (4.15–7.11)
- `s.sum.pct_factor`, `s.sum.pct_specific` both populated, sum to ~100 ± 0.1
- `s.factors[].c`, `s.factors[].a`, `s.factors[].n` all populated, factor count = 12 across all 6
- `s.hold[].pct_t` populated (will be aliased to `h.tr` by `normalize()` L1878 in browser); `s.hold[].t`, `s.hold[].n` populated
- No `null`/`undefined` in any required field for any of the 6 strategies. The tree will render a non-empty result on all current strategies.
- The data plumbing **works**; the *interpretation* is what's broken (D1, D2, D5).

---

## T2 — Functionality parity (YELLOW)

### Tile contract checklist

| Capability | Standard (per cardTEStacked v2 + cardRiskByDim peer) | This tile | Gap? |
|---|---|---|---|
| Card id | required | `cardRiskDecomp` ✓ | — |
| Card-title tooltip | yes | yes (L7527 `data-tip`) ✓ | — |
| Right-click note hook | yes | yes (`oncontextmenu="showNotePopup(event,'cardRiskDecomp')"`) ✓ | — |
| About btn (registry-driven) | yes | YES — `aboutBtn` via `tileChromeStrip({about:true})` ✓; registry entry complete (L1275–1282) | — |
| `tileChromeStrip` chrome | yes | yes (L7528) ✓ | — |
| Generic full-screen ⛶ | yes | yes (`openTileFullscreen('cardRiskDecomp')`) ✓ — but the tree has no canvas/Plotly, so the generic fullscreen falls back to outerHTML clone; works but never visually tested | — (works) |
| Reset view | yes (per `tileChromeStrip`) | yes ✓ | — |
| Hide tile | yes | yes ✓ | — |
| CSV export | yes (peer cardTEStacked, cardRiskByDim) | **NO** | YES (F7) |
| Reset zoom | n/a (no plot) | n/a | — |
| Click-to-drill | yes | **NO** — caveats explicitly own this gap ("Tree is read-only — no click-to-drill yet") | YES (F4 idio→`oSt`, F5 factor→`oDrF`) |
| Empty state | yes | partial — early return on `!te` only, fails on `s.factors=[]` | YES (F8) |
| Footer / caveats | yes (cardRiskByDim has one for the F18 footer) | NO | YES (F2) |
| Top-N selector | n/a / configurable | hardcoded `slice(0,7)` (L7519) | YES (F3) |
| Threshold slider | n/a (peer cardRiskByDim has one for stability) | none | optional |
| Sort control | n/a (sorted by |c| desc inherently) | inherent | — |
| Signed-vs-absolute toggle | n/a | not exposed (always absolute) | optional |
| Theme-aware | yes | no — inline hex (X1) | YES |
| Hover tooltips on leaves | yes | none (only title bar) | YES (X2) |
| Per-week (`_selectedWeek`) honoring | yes | partial (uses `factorRisk`/`idioRisk` from `rRisk()` — which are per-week ✓ — but reads `s.factors`/`s.hold` directly = latest-week always) | YES (D5) |
| `_b115AssertIntegrity` style assertion | yes (Lesson 13) | NO | YES (D2) |
| Synth marker `ᵉ` | yes (sum-cards) | NO | YES (D4) |

### Findings

**F1 [YELLOW] — No click-to-drill on leaf nodes.**
- Caveat L1280 owns this gap explicitly. Trivial to wire: idio leaves have `h.t` (ticker) — single-stock drill `oSt(h.t)` already exists and is used at L4269. Factor leaves have `f.n` — single-factor drill `oDrF(f.n)` already exists and is used in cardFacContribBars.
- **Proposed fix:** F4 + F5. `mkNode` would need an additional `clickHandler` param threaded through. ~6 LOC.

**F2 [YELLOW] — No CSV export despite tree being inherently tabular (level / label / value / parent).**
- Standard peer Risk-tab tiles all have CSV (cardTEStacked, cardRiskByDim).
- **Proposed fix:** F7 — `exportRiskDecompCsv()` flattens the tree into 4 columns. ~25 LOC.

**F3 [YELLOW] — Hard-coded top-N (=7) with no UI control.**
- `topH = ... .slice(0,7)` (L7519). For wider strategies (ISC has 2,209 holdings), 7 is a thin slice; for narrower (IDM 775), 7 may be appropriate. The choice is opaque.
- **Proposed fix:** F3 — `_rdtTopN` localStorage with inline `<select>` (5 / 7 / 10 / 15 / 25).

**F4 [YELLOW] — Empty-state fragile.**
- L7495 early-returns on `!s.sum.te`. But `s.factors.forEach` (L7500) on an empty/undefined factor list is fine (forEach on `[]`); however if `s.factors` is undefined entirely (legacy file pre-`normalize()`), it throws TypeError. `normalize()` L1865 sets `st.factors=[]` if missing, so this path is mostly defended. Top-7 holdings (L7519) on an empty `s.hold` returns `[]` and renders an empty idio sub-tree silently — **no message** indicating the empty state.
- **Proposed fix:** F8 — render explicit "no factor contributions" / "no holdings" placeholder leaves when those arrays are empty.

**F5 [GREEN] — About registry entry is complete (L1275–1282) and accurate.**
- title / what / how / source / caveats / related — all 5 fields populated.
- The caveats field correctly self-documents the click-to-drill gap, the top-7 heuristic, the FAC_GROUPS dependency, and the bench-only sector exclusion.
- The `how:` line says "Per-holding contribution from cs.hold[].tr" — this is technically true but understates the F18 issue. **Recommend updating** when D1 fix lands.

---

## T3 — Design consistency (YELLOW)

### Findings

**X1 [YELLOW] — Inline hex colors instead of design tokens (L7515, L7517, L7521, L7523, L7524).**
- `'#818cf8'` (L7515) ≈ `var(--pri)` (light variant) — used for factor leaves
- `'#6366f1'` (L7517) = `var(--pri)` exact — used for factor groups
- `'#f59e0b'` (L7521, L7524) = `var(--warn)` exact — used for idio
- `'#06b6d4'` (L7523) close to `var(--cyan)` (`#22d3ee`) but **not equal** — used for factor parent
- **Why it matters:** breaks light theme, breaks any future palette change (vs the project's standard practice of always going through tokens).
- **Proposed fix:** X1 — token-ize all 4. Note: the `#06b6d4`-vs-`#22d3ee` mismatch hints this tile predates the tokenization pass.

**X2 [YELLOW] — Cross-tile palette inconsistency for {factor, idio} on the SAME tab.**
- Three palettes for the same domain pair, separated by ~30 lines of code:
  - **Sum-cards** (L7727 `Factor Risk` + L7732 `Idiosyncratic`): `--pri` (indigo) for factor + `--acc` (purple) for idio
  - **cardTEStacked** area chart: `--cyan` for factor + `--warn` (amber) for idio
  - **cardRiskDecomp** tree: `#06b6d4` cyan for factor + `#f59e0b` amber for idio (= matches cardTEStacked)
- The tree matches the area chart (good — they're stacked vertically) but contradicts the sum-cards directly above (bad — same words, different colors).
- This is the **same finding as cardTEStacked v2 F9** (B88 idio/factor tokens in the backlog).
- **Proposed fix:** X4 (PM gate) — pick one. Recommendation: keep tree+area-chart on cyan/amber (it's the more memorable pair); migrate sum-cards to match. Single source of truth as `--factor` and `--idio` CSS vars.

**X3 [YELLOW] — Bar saturation (`Math.min(|h.tr|*10, 100)`) collapses the very ranking the bar communicates.**
Same as D6.

**X4 [YELLOW] — No leaf-level tooltips. Hovering a row reveals nothing.**
- Title-bar tooltip (L7527) explains the tile concept. Leaf rows have no `title` / `data-tip`.
- For a tree where the entire information unit is "this leaf is X% of TE because Y", missing leaf tooltips means the explanation is one tooltip-per-tile, not one tooltip-per-data-point.
- **Proposed fix:** X2 — add `title="..."` to each leaf with the relevant `_synth` marker, FactSet field path, and (when applicable) sector / country.

**X5 [YELLOW] — No empty-state UI, no footer, no "as-of" date label.**
- Per the project's standard template (peer tiles have all 3): `cardTEStacked` has a footer (`teStackedFooterCap` L7768), `cardRiskByDim` has `rbdFooter`, etc.
- `cardRiskDecomp` ends after the last node and immediately closes its outer card div.
- **Proposed fix:** F2 — add a hairline footer block.

**X6 [GREEN] — Layout structure is clean.**
- `padding:4px 0` on each leaf (L7491) is too tight for hover affordance but otherwise readable.
- The `▸` / `▾` arrow toggle is consistent with peer collapsibles.
- Indent (`margin-left:20px` on `kidsHtml`, L7480) is shallow but workable for 2 levels.

---

## Cross-track integration findings (Lessons 9–14 lens)

**Lesson 13 lens (layered monitoring) — D2 finding is the load-bearing one.**
Per Lesson 13, every numeric cell on the dashboard should have **a parser-side check, a render-time check, AND a UI surface assertion** when it can drift. The Risk Decomposition Tree currently has zero render-time checks. Both the factor side (L1900–1903 renormalization is a parser-side guarantee, but no UI assertion that `Σ|f.c|` post-render equals what was asserted on load) and the idio side (no upstream nor downstream assertion) cross all three layers as silent.

The proposed D2 fix (`console.warn` when child-sum diverges from parent) is the cheapest possible render-time check; it costs ~6 LOC and would have caught the F18 anomaly the moment the tree consumed its data, not on a forensic dive. **The pattern from Lesson 13 — "noisy on render, silent on green" — is what this tile lacks.**

**Lesson 12 lens (escalate; don't paper over) — D8 (PM gate) is the principled call.**
The F18 inquiry letter (`FACTSET_INQUIRY_F18.md`) and the source-side test pack (`PA_TESTS_F18.md`) exist precisely to resolve the meaning of `pct_t`. The cardRiskDecomp tree consumes `pct_t` as if F18 were already resolved (and resolved with the answer "it's a share of TE"). It is not resolved. The honest read is: the tree's idio branch should NOT lean on the column under inquiry until F18 lands. **Recommendation: switch to D8 (c) [sector-MCR breakdown] as a temporary remediation; revisit when F18 reply is in.**

**Lesson 14 lens (`index.json` summaries) — adjacent opportunity.**
Layered-monitoring Lesson 14 added `index.json` per-strategy summaries to enable cheap cross-strategy probes. The same probe shape used in this audit (Σ|h.tr| across all 6 strategies, comparing to pct_specific) is ~10 lines and could live in `index.json` build (`{strategy, sum_abs_pct_t, pct_specific, ratio}`). Then any future tile-audit-monitor would have one-line evidence whether F18 has resolved per-strategy. **Backlog note** rather than fix.

**Lesson 9 lens (push discipline) — neutral.**
This audit is a markdown read; coordinator serializes any fix push.

**Lesson 10 lens (verifier perf) — neutral.**
No verifier added; the proposed D2 console.warn is render-time, not load-time, so does not gate the smoke test.

**Lesson 11 lens (cadence beats sprints) — meta.**
This is the **first** audit on cardRiskDecomp despite the tile being on a Tier-1 hero tab and consuming the same data column under formal inquiry F18. The 14-tile catch-up sprint surfaced the gap; per Lesson 11, the steady cadence forward should re-audit cardRiskDecomp inside ~2 weeks of any data-flow change to the idio side (D8 fix or F18 reply).

---

## Verification checklist

- [x] Data accuracy verified — RED, see D1/D2/D8 (math walked across all 6 strategies)
- [x] Edge cases checked (empty s.factors, empty s.hold) — F8 RED-adjacent (silent), F4 partial
- [ ] Sort works — n/a (sorted by |c| / |tr| desc inherently)
- [ ] Filter works — n/a (no filter today)
- [ ] Column picker — n/a (no columns; tree)
- [ ] Export produces correct file — F2 NO (no CSV)
- [ ] Full-screen modal renders — works via generic fallback (1457 outerHTML clone); not visually tested per audit time
- [ ] Drill / popup mirrors — F4/F5 NO (no click-drill anywhere)
- [ ] Responsive (narrow viewport) — works (flex layout, but bar `width:60px` becomes a major fraction on mobile)
- [ ] Themes (dark + light) — NO (X1 inline hex)
- [ ] No console errors — likely yes on current data; F8 risk on legacy/empty
- [ ] Per-week routing honored — D5 NO (partial)
- [ ] About entry registered — yes ✓
- [ ] SOURCES.md entry — D7 NO

---

## Summary

`cardRiskDecomp` is structurally sound — chrome / About / note-hook are all correct, and the helper `mkNode` is clean enough to fix in place. The primary finding is **D1 (RED)**: the idio sub-tree consumes the same `pct_t` column under formal FactSet inquiry F18, and renders it with a `'%'` suffix that frames it as a share of total TE — which (per F18) it is not. Math walk across all 6 strategies confirms top-of-tree contradicts top-of-leaves on every strategy.

**Highest leverage path:** PM-gate D8 (move idio sub-tree to sector-MCR breakdown) + trivials D1 (label '%' → ' pp') and D2 (render-time assertion). Three of these four together (D1+D2+D8c) restore parent–children math integrity AND surface the F18 caveat AND tokenize-color, in <50 LOC of changes. Companion trivials (X1 colors, F2 footer, F4/F5 click-drill) bring the tile to peer parity in another <30 LOC.

**Blocked items:** D8 needs PM call. F18 reply (external) shifts which path is correct on the idio side. X4 cross-tile palette is a B88 backlog item unchanged from the cardTEStacked v2 audit.

**Sign-off requires user review** (per memory note): the D1 framing fix is straightforward; the D8 path choice is product-level.
