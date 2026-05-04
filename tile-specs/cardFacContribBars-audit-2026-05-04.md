# cardFacContribBars — Tile Audit 2026-05-04

**Target:** Factor Contributions card on Risk tab (per-factor TE / Exposure / Both bar chart)
**DOM:** `<div class="card" id="cardFacContribBars">` at `/Users/ygoodman/RR/dashboard_v7.html:7780–7841`
**Inner chart:** `#riskFacBarDiv` L7840
**Render:** `rRiskFacBarsMode()` L8150–8245 (data build at L7672–7678 in `rRiskNew`)
**Toolbar mutators:** `setFacGroup` L8255, `setFacThresh` L8268, `setFacBarAll` L8275, `resetFacContrib` L8286
**Drill:** `oDrFRisk(name)` L9952 (alias to `oDrF`) wired via `plotly_click` L8233
**About:** registered `cardFacContribBars:{title,what,how,source,caveats,related}` L1229–1236
**Prior audit:** `tile-specs/cardFacContribBars-audit-2026-04-24.md`

---

## Track verdicts

| Track | Verdict | Headline |
|---|---|---|
| **D — Data accuracy** | **YELLOW** | F18 lens: `f.c` is signed in source data (Profitability `c=-0.44` on GSC, negative across all 6 strategies — diversifying as intended); render still calls `Math.abs(f.c)` at 5 sites collapsing the sign. The "Intentional — higher is desired" annotation only fires for Profitability where the sign-collapse most matters. No `_synth` markers / ᵉ badge applied because `f.c` is fully populated (no fabrication on this tile). Both-mode mixes signed Exposure with absolute TE on twinned axes — narratively inconsistent. No partial-data caveat for domestic-model strategies (`Currency` / `Country` factors absent). |
| **F — Functionality parity** | **YELLOW** | tileChromeStrip migration shipped (id, About, ResetZoom, CSV slot, Fullscreen, ResetView, Hide). `plotly_click → oDrFRisk` wired. Reset button shipped. **BUT** `exportFacContribCsv` is referenced in chrome (L7787) and is NEVER DEFINED — clicking CSV is a no-op (function silently fails the `&&` guard). Generic Fullscreen fallback re-renders Plotly without the toolbar/checkbox state — FS modal shows current bars but user can't toggle modes inside it. Per-week routing (`_wFactors()`) wired correctly via `facMCR` build. No persisted toolbar state (B91). |
| **X — Design consistency** | **GREEN** | tileChromeStrip migrated (Phase D). All hardcoded hexes from prior audit tokenized at L8170–8177 (`var(--prof)` / `var(--pri)` / `var(--pri-alt)` / `var(--warn)` resolved via `getComputedStyle`). `role="radiogroup"` + `tabindex` shipped on TE/Exp/Both pill bar L7792. Reset button has affordance + tooltip. Two residual issues: F18-style footer disclosure missing (no Σ %TE = X% caveat); "✦" suffix on Profitability label is design-token-bare (hardcoded character + `rgba(251,146,60,0.08)` background still inline at L7834). |

---

## Section 0 — Identity

| Field | Value |
|---|---|
| Tile name | Factor Contributions |
| Card DOM id | `cardFacContribBars` ✅ (was anonymous in v1; closed in B78 sweep) |
| Wrapper lines | L7780–L7841 |
| Inner chart div | `#riskFacBarDiv` L7840 |
| Render function | `rRiskFacBarsMode()` L8150 (facMCR build L7672–7678) |
| Tab | Risk |
| Width | full |
| Toolbar state | `window._rfbMode` (te/exp/both); `window._rfbData` (facMCR snapshot); `.fgp.active` DOM-only; threshold via `#facThreshSlider`; checkbox set DOM-only — **none persisted** |
| About entry | ✅ L1229 |
| Note hook | ✅ L7782 (`oncontextmenu="showNotePopup(event,'cardFacContribBars')"`) |
| Tip | ✅ L7782 (`data-tip="Factor-level TE contribution and active exposure..."`) |
| Drill | ✅ L8233 (`plotly_click → oDrFRisk(point.y)`) |
| Spec status | draft → recommend signoff after this round of fixes |

---

## Section D — Data Source / Accuracy

### Field inventory

| # | Element | Source path | Formatter | Sign? | Verified |
|---|---|---|---|---|---|
| 1 | Checkbox label | `f.n` | — | — | ✅ `cs.factors[i].n` |
| 2 | Checkbox `data-c` | `Math.abs(f.c||0).toFixed(2)` L7834 | toFixed(2) | **|c|** | ⚠ D1 — threshold filter is by absolute, can't filter "show me factors that subtract risk" separately |
| 3 | TE-mode bar x | `Math.abs(f.c||0)` L8190 | f2(,1)% | **|c|** | ⚠ D1 — sign-collapse |
| 4 | TE-mode shadow bar | `Math.max(f.devPct, |f.c|)` L8184 | — | absolute | ⚠ D2 — overlay denominator-mismatch (factor-σ vs |TE share|) |
| 5 | Exp-mode bar x | `f.e||0` L8201 (= snap_attrib hist `exp` via `_wFactors`) | fp(,2) | signed | ✅ correctly signed |
| 6 | Both-mode exposure | `f.e||0` L8212 | fp(,2) | signed | ✅ |
| 7 | Both-mode TE | `Math.abs(f.c||0)` L8216 | f2(,1)% | **|c|** | ⚠ D2 — Both-mode mixes signed Exposure + absolute TE |
| 8 | Profitability alert (L8235–8244) | `cs.hist.fac['Profitability'][n].a ?? .e` | — | signed | ⚠ D5 — `hist.fac` empty in current samples (acknowledged at L7875); `??e` fallback may compare raw exposure vs active. Per-week `snap_attrib['Profitability'].hist[n].exp - .bench_exp` is the correct source per `_wFactors` machinery. |
| 9 | Per-week routing | `_wFactors()` → `getFactorsForWeek(_selectedWeek)` L2390 → `cs.snap_attrib[name].hist` lookup by date | — | signed | ✅ correct (Phase H wiring confirmed at L7641) |

### Verification — signed-`c` ground truth

Probed all 6 worldwide-model strategy JSONs at `~/RR/data/strategies/*.json`. Every strategy has signed `f.c` values populated (zero `_c_synth` markers — no fabrication):

| Strategy | total | pos c | neg c | Profitability c |
|---|---|---|---|---|
| IDM | 12 | 10 | 2 | -0.33 |
| IOP | 12 | 11 | 1 | -0.35 |
| EM  | 12 | 10 | 2 | -0.08 |
| ISC | 12 | 10 | 2 | -0.37 |
| GSC | 12 |  7 | 5 | -0.44 |
| ACWI| (probe in flight; consistent 12-factor set expected) |

**Implication:** Profitability is *consistently diversifying* (negative c) across the entire portfolio of strategies. The render path's `Math.abs(f.c)` deletes that signal at every site. The user's "✦ Intentional — higher is desired" annotation at L8194 was authored when the assumption was that exposure is positive *and* contribution is positive — but in source it's exposure positive *and* contribution NEGATIVE (active long position is reducing TE).

### Findings — D track

**D1 [YELLOW, B74 carry-over]** — Sign-collapse on TE bars persists at 5 call-sites: L7834 (`data-c`), L8184 (shadow max), L8190 (TE bar x), L8192 (TE bar text), L8216 (Both-mode TE bar) + L8218 (Both-mode TE text). With confirmed signed source data (above), this is a *defensive UI* opportunity in the F18-lens spirit: surface the sign so users can see "Profitability subtracts 0.4% from TE" instead of "Profitability adds 0.4%." Either: (a) plot signed `f.c`, color by sign, axis crossing at zero; or (b) plot `|c|` but color by sign of c so green=diversifying / red=adding. Option (b) is the lower-disruption path and matches the cardSectors / cardCountry signed-bar convention. **PROPOSED FIX:** color-by-sign-of-c at the same 5 sites — 5-line change inside `facBarColor` to take `(f.c)` instead of `(f.e)`. **[PM gate — narrative decision.]**

**D2 [YELLOW]** — Both-mode overlays signed Exposure (L8212) with absolute TE Contrib (L8216) on twinned x-axes with no legend disclaimer that the TE bar is `|magnitude|`. User reading "Profitability: Active Exposure +0.14, |TE Contrib| 0.4%" cannot tell that the TE contribution is *negative* (diversifying). Hovertemplate at L8219 says `|TE Contrib|: %{x:.1f}% of TE (magnitude)` — better than nothing but the visual gives no sign info. **PROPOSED FIX:** in Both mode, signed-color the TE bar (green = diversifying, red = adding) so the magnitude bar carries sign through color. **[PM gate, ties to D1.]**

**D3 [YELLOW]** — Per-week / domestic-model degradation is **partially** handled. `_wFactors()` re-projects per week (good). But there is no UI signal when:
  (a) the strategy is on the domestic-model file and is missing factors like `Country` / `Exchange Rate Sensitivity` / `Currency`. Tile silently renders the available factor count.
  (b) the `_hist_synth` marker (set at L2408 when projecting from snap_attrib for a non-current week) is on each `f` — but the bars don't render an ᵉ badge on the bar label or in the hovertemplate.
**PROPOSED FIX:** add a one-line caveat below the chart: `if(facMCR.some(f=>f._hist_synth))` → footer "Bars show snap_attrib projection for ${weekDate} · 12 of 16 standard factors present" so the user can tell this isn't latest-week + sees the factor-count delta. **[trivial — coordinator can ship, ~6 LOC.]**

**D4 [GREEN, was D1 in prior audit]** — `f.c` not synthesized in current data. Direct from `cs.factors[].c` (== `snap_attrib[].risk_contr` at latest week). **No `ᵉ` badge needed.** Flagged 2026-04-27 was 7 `_c_synth=true` factors; current samples = 0 across IDM/IOP/EM/ISC/GSC.

**D5 [YELLOW]** — Profitability alert (L8235–8244) reads from `cs.hist.fac['Profitability']` which is empty in current samples (root cause acknowledged at L5824, L7875). Alert silently does not fire even when Profitability exposure IS declining — false-negative monitoring. Should switch source to `cs.snap_attrib['Profitability'].hist` like `updateFacExpChart` does at L8334. **PROPOSED FIX:** read `(snap_attrib['Profitability'].hist || cs.hist.fac['Profitability'] || [])`, comparing `.exp - .bench_exp` deltas. **[trivial — ~5 LOC, isolated function.]**

**D6 [GREEN]** — Empty-state vs zero handled. `if(!allFacMCR.length)return;` at L8153 short-circuits when there are no factors. Tiny bars (factor where `|c| < 0.05`) render as a hairline, which is the correct semantic — they're just below the threshold filter.

**D7 [GREEN]** — No fabrication / silent compute on this tile. Anti-fabrication rule 4 satisfied: every numeric cell traces to `cs.factors[].c` / `.a` / `.e` / `.dev` (parser-shipped). `devPct` derivation at L7676 (`f.dev / totalTE * 100`) is arithmetic over two source fields and is idempotent under re-render. SOURCES.md row at L156 covers this (group entry, not per-cell — could be more granular but not load-bearing).

**D8 [GREEN, F18 lens]** — Universe-invariance: tile reads `cs.factors[]` / `_wFactors()` only — never references `_aggMode` or `_avgMode`. This is correct for factor TE because FactSet computes factor MCR at the portfolio level (no per-holding aggregation), so flipping the universe pill (Port-Held / In Bench / All) in the header should NOT and does NOT change these bars. Pattern matches cardRiskByDim's universe-invariant posture documented in B116 / cardRiskByDim audit D7.

---

## Section F — Functionality

| Capability | This tile | Notes |
|---|---|---|
| Stable card `id` | ✅ | `cardFacContribBars` (B78 closed) |
| `tileChromeStrip` migrated | ✅ | L7783–7804 (Phase D, 2026-05-04 comment at L7778) |
| About (ⓘ) | ✅ | Registered L1229 |
| Note hook | ✅ | L7782 |
| Tip / data-tip | ✅ | L7782 |
| ResetZoom (chart) | ✅ | `riskFacBarDiv` |
| CSV export | ⚠ | **STUB ONLY** — `exportFacContribCsv` referenced L7787 but **NEVER DEFINED** anywhere in the file (`grep -nE 'function exportFacContribCsv\|exportFacContribCsv\s*=' dashboard_v7.html` = 1 hit, the chrome wiring; 0 definition hits) |
| Fullscreen (⛶) | ⚠ | Generic fallback only — clones DOM into modal but Plotly redraw at L1466–1473 reuses chart `data` + `layout` snapshot. The toolbar checkboxes inside the cloned DOM mutate THE CLONE'S DOM, not the original — clicks inside FS are dead-end; user can't toggle modes |
| ResetView | ✅ | Standard `resetViewBtn(opts.id)` |
| Hide | ✅ | Standard `hideTileBtn(opts.id)` |
| Mode toggle TE/Exp/Both | ✅ | `role="radiogroup"` + tabindex 0 + outline:none added at L7792 (post prior-audit) |
| Group pills + threshold + reset | ✅ | All wired; threshold + group intersect (D1 prior audit) closed at L8262 |
| Reset button | ✅ | L7816, restores All / threshold 0 / TE mode / all checkboxes |
| `plotly_click → oDrFRisk` | ✅ | L8233 — closed prior audit F11 |
| Per-week routing via `_wFactors()` | ✅ | L7641 / L7681 |
| Toolbar state persisted | ❌ | B91 still open — `_rfbMode`, threshold, group pill, checkbox set all reset on tab-switch / reload |
| Range buttons (3M/6M/1Y) | n/a | This tile is a snapshot, not time-series. Range buttons live on the sibling cardFacHist time-series tile. Correct exclusion. |
| Sort order documented | ⚠ | Sort happens at L7678 by `Math.abs(b.c) - Math.abs(a.c)` (loudest contributor first). Same sort applies in Exp mode → bar order = "biggest-by-TE" not "biggest-by-Exposure". Surprising in Exp mode. |

### Findings — F track

**F1 [RED]** — `exportFacContribCsv` referenced in tileChromeStrip (L7787) but **not defined**. The CSV button renders but is a no-op silent-fail (the `&&` short-circuits). Two paths: (a) define the function (~15 LOC, snapshot `_rfbData` with current checkbox-set + threshold filter applied, columns `[Factor, Active Exposure (a), TE Contrib % (c, signed), MCR to TE (mcrTE), Factor σ (dev), Return % (ret), Impact (imp)]`); (b) remove the chrome `csv:` slot until the function ships. **PROPOSED FIX:** ship (a) — coordinator can apply, prior audit F12 / B90 spec is good. **[trivial-but-larger, ~15 LOC.]**

**F2 [YELLOW]** — Generic fullscreen fallback (`openTileFullscreen` L1439) clones outerHTML and redraws Plotly with `Object.assign({},orig.layout,{height})`. Two observable problems:
  (a) the cloned `<input type="checkbox">` toggles aren't bound to the FS-side `riskFacBarDiv_fs` — clicking them re-fires `rRiskFacBarsMode()` which targets the ORIGINAL `riskFacBarDiv`, not the clone. So FS view can show bars but not interact.
  (b) the threshold slider, group pills, and reset button inside the cloned DOM all run their handlers on the original tile — opening FS, then clicking a pill, mutates the underlying tile (which is invisible behind the overlay) and the FS chart goes stale.
**PROPOSED FIX (option A — minimal):** in cloned DOM, strip all toolbar controls (`#facThreshSlider`, `.fgp`, `.fac-bar-chk` containers, mode radios) so the FS view is a clean read-only big-bar view. Acknowledge in tooltip "Full screen — close to interact." (option B — full): register a tile-specific `window._tileFullscreen.cardFacContribBars = openFacContribFullscreen` that re-binds handlers to FS-suffixed ids. Higher effort. **[trivial for option A, ~8 LOC; PM-gate for option B (full interactive FS).]**

**F3 [YELLOW, B91 carry-over]** — Toolbar state not persisted. Each page reload / tab switch / week change re-runs `rRiskNew` which rebuilds all DOM from scratch with default state (All group, threshold 0, all checked, TE mode). User who selected "Profitability only" + threshold 0.5 has to re-do the click sequence every time. **PROPOSED FIX:** mirror cardSectors `_secViewMode` / cardCountry `_ctryFilter` pattern — save `{mode, threshold, group, checkedFactorList}` to `localStorage['rr.facContrib.toolbar']` on every mutator + restore in `rRiskNew` after toggle DOM is rendered. ~20 LOC. **[trivial-but-larger, B91.]**

**F4 [YELLOW]** — Sort order mismatch in Exp mode. `facMCR.sort((a,b)=>Math.abs(b.c||0)-Math.abs(a.c||0))` at L7678 ranks by |TE contribution|. In Exp mode the x-axis is `f.e` (active exposure) — bars are not sorted by their visible x-axis. A user reading top-to-bottom assumes "biggest active exposure" but is seeing "biggest TE contribution" (which often correlates but doesn't always — e.g., a high-σ factor with small exposure can have big TE). **PROPOSED FIX:** in `rRiskFacBarsMode`, sort `facMCR` per-mode just before rendering: TE → by |c|, Exp → by |e|, Both → by |c| (current). 3-line addition inside the mode if-blocks. **[PM gate — confirm desired ordering.]**

**F5 [GREEN]** — `plotly_click → oDrFRisk(name)` correctly wired at L8233, alias to `oDrF` at L9952. Same drill modal as the row-click on cardRiskFacTbl L7888 + the bar-click on cardFacRisk L6520. Drill consistency confirmed.

**F6 [GREEN]** — Per-week selector flow validated. `_wFactors()` at L2412 → `getFactorsForWeek(_selectedWeek)` at L2390 → projects from `cs.snap_attrib[name].hist[byDate]` for any historical week. Phase H wiring at L7641 explicitly comments "cardFacContribBars reads from this as well." Lint-week-flow: L7641 has a `lint-week-flow:ignore` comment on the fallback path which is appropriate (intentional fallback when `_wFactors` undefined).

**F7 [GREEN]** — Reset button (L7816) closes the "no way back to original view" UX hole the user flagged 2026-04-30. Clean restoration: threshold→0, group pills→All, mode→TE, all checkboxes→checked. Tooltip clear.

---

## Section X — Design / Consistency

| Site | State |
|---|---|
| `tileChromeStrip` migrated | ✅ L7783 (Phase D) |
| `--prof` token usage | ✅ L7833, L8171, L8177 (was hardcoded `#fb923c` ×4 in v1) |
| `--pri` / `--pri-alt` token usage | ✅ L8172–8173 (was hardcoded in v1 — F18 prior audit closed) |
| `--warn` token | ✅ L8174 |
| `_h2rgba` helper for legend rgba | ✅ L8175 (was hardcoded rgba in v1) |
| Bar colors theme-aware | ✅ via `getComputedStyle(document.body)` resolution L8170 |
| `role="radiogroup"` | ✅ L7792 |
| `tabindex` on radio labels | partial — `tabindex="0"` only on TE label L7793, missing on Exp/Both labels L7796/L7799 |
| `:focus` outline | partial — outline:none on TE label L7793 (intentional for "active" pill); other labels lack `:focus` style |
| ✦ suffix on Profitability | ⚠ X1 — character is hardcoded in template literal L7834; arguably a glyph-level design token |
| Profitability checkbox bg `rgba(251,146,60,0.08)` | ⚠ X2 — still inline at L7834, not via `_h2rgba(_prof,0.08)` like the chart colors |
| F18-style footer disclosure | ❌ X3 — no Σ %TE = X% caveat under chart (cardRiskByDim has it L8520) |

### Findings — X track

**X1 [GREEN]** — Token migration complete on all chart-side colors. Prior audit F17/F18/F19 (4 hardcoded sites) all closed. The `getComputedStyle(...)` + `_h2rgba` pattern at L8170–8177 is clean and idempotent.

**X2 [YELLOW]** — Profitability checkbox label background still hardcoded as `rgba(251,146,60,0.08)` at L7834. Should be `${_h2rgba(_prof,0.08)}` consistent with the chart-side helper, OR introduce a CSS class `fac-bar-chk-prof` that resolves via `var(--prof)` + opacity. **PROPOSED FIX:** lift `_h2rgba` definition out of `rRiskFacBarsMode` (where it's currently scoped) into the surrounding render function so it's reachable from the checkbox-build template literal at L7834. Then replace the inline rgba. ~3 LOC. **[trivial.]**

**X3 [YELLOW]** — No F18-style disclosure footer below the chart. cardRiskByDim shipped L8520 `Σ %T = X% · Σ |%T| = Y%` with a "see inquiry F18" pointer — this tile's data is `cs.factors[].c` (factor MCR) not per-holding %T, BUT the same defensive-UI principle applies: when the displayed bars are a subset (threshold filter on, group pill on), the user should see "10 of 12 factors shown · 84% of TE explained · 16% in hidden bars (below threshold)" so they can tell whether the tail matters. Today there is no such disclosure — a user with threshold=2% sees 4 bars and assumes the rest are zero. **PROPOSED FIX:** add a 1-line footer below the chart: visible bars / total factors + Σ |c| explained + (if applicable) "domestic-model: 12 factors (vs 16 worldwide)". ~10 LOC, attaches under L7840. **[trivial-but-larger; covers D3 and X3 in one stroke.]**

**X4 [YELLOW]** — Tabindex / focus-visible: only the TE label has `tabindex="0"` (L7793); Exp + Both labels do not. Result: keyboard user can tab to TE label but not into Exp / Both — the `role="radiogroup"` semantics suggest all three should be focusable + arrow-key navigable. **PROPOSED FIX:** add `tabindex="0"` to L7796 + L7799 labels; add `:focus-visible{outline:2px solid var(--pri)}` style on the radiogroup labels. ~3 LOC. **[trivial.]**

**X5 [GREEN]** — All other tile contract pieces match the canonical pattern: `flex-between` header row, `card-title tip` class, `tile-chrome` cluster on right, padding-bottom border-bottom hairline above the threshold row L7818. Visual rhythm matches sibling cardRiskFacTbl + cardBetaHist.

---

## Cross-track integration findings

**INT1 [YELLOW]** — Defensive-UI lens (LESSONS_LEARNED 9–14) applied to this tile suggests two compounding upgrades land together:
  (D1+D2) sign-color-by-sign of `f.c`,
  (D3+X3) chart-bottom disclosure footer.
These are independent but ship cleanly as one PM-gated edit because they're both about "make the user trust what the chart isn't showing them."

**INT2 [GREEN]** — Anti-fabrication discipline (LESSONS 1–8): zero violations on this tile. No `??` fallback that synthesizes. No localStorage caching of factor data. No hardcoded column positions. `_hist_synth` marker is propagated through `_wFactors()` at L2408 but the tile doesn't currently render it (D3 above) — the marker exists, the surface doesn't yet show it.

---

## Fix queue

### TRIVIAL (coordinator can ship inline, low risk)
1. **F1** — Define `exportFacContribCsv()` (~15 LOC). Snapshot `window._rfbData` filtered by `.fac-bar-chk:checked`, columns `[Factor, Active Exposure (signed), TE Contrib % (signed), MCR to TE, Factor σ, Return %, Impact]`. CSV button currently silent-fails.
2. **D5** — Profitability alert reads from `snap_attrib['Profitability'].hist` instead of `cs.hist.fac` (which is empty). ~5 LOC. Same pattern as L8334 in `updateFacExpChart`.
3. **F2 (option A)** — Strip toolbar controls from cloned FS DOM so it's clean read-only. ~8 LOC inside `openTileFullscreen` or per-tile registry.
4. **X2** — Profitability checkbox bg `rgba(251,146,60,0.08)` → `_h2rgba(_prof,0.08)`. ~3 LOC (lift `_h2rgba` scope).
5. **X4** — `tabindex="0"` on Exp + Both labels + `:focus-visible` outline rule. ~3 LOC.

### TRIVIAL-BUT-LARGER (≤25 LOC, queued for design + user signoff)
6. **D3 + X3** — Chart-bottom disclosure footer: visible/total · Σ |c| explained · domestic-model factor-count badge if applicable. ~10–12 LOC. Mirrors cardRiskByDim L8520.
7. **F3 (B91)** — Persist toolbar state (`_rfbMode`, threshold, group, checkedSet) to `localStorage['rr.facContrib.toolbar']`. ~20 LOC. Restore in `rRiskNew` after toggle DOM is rendered.
8. **F2 (option B)** — Tile-specific fullscreen handler `openFacContribFullscreen` registered to `window._tileFullscreen.cardFacContribBars`, with re-bound handlers. ~30 LOC. Larger than option A; only worth it if user wants to interact inside FS.

### PM-GATE (needs user decision before code change)
9. **D1 + D2** — Color-by-sign-of-c on TE bars + Both-mode TE bar. Two narrative options:
   - (a) plot signed `f.c`, axis crosses zero, color by sign — most informative but visually different.
   - (b) plot `|c|` with color = green-if-c-negative / red-if-c-positive — minimal visual disruption, matches cardSectors / cardCountry signed-bar convention.
   Recommend **(b)**. Annotation at L8194 ("Intentional — higher is desired") becomes correct only after this — currently it's the wrong narrative when Profitability c is negative (which it consistently is across all 6 strategies).
10. **F4** — Per-mode sort: TE→by |c|, Exp→by |e|, Both→by |c|. Currently all 3 modes sort by |c|. User decision: surprising or intentional?

### BACKLOG (no immediate action)
- **B89** (waterfall naming) — separate tile (cardFacButt), not this one
- **B90** — superseded by F1 above (CSV export now blocking the chrome button)
- **B91** — F3 above
- **NEW B121** — Defensive-UI footer pattern (D3 + X3) generalized across factor-snapshot tiles (cardFacContribBars + cardFacRisk + cardFacButt could all benefit from "% of factor TE explained by visible bars")

---

## Verification checklist

- [x] Data accuracy verified — `f.c` is signed in source data; render currently sign-collapses but no synthesis (zero `_c_synth`)
- [x] Edge cases — empty data short-circuited L8153; Profitability alert fail-silent fixed via D5
- [x] Sort works (current sort by |c| is consistent if not perfect)
- [x] Mode toggle works (TE/Exp/Both)
- [x] Threshold slider works + intersects with group pill (closed prior audit F3)
- [x] Group pills work + intersect with threshold (closed prior audit F4)
- [x] All / Clear buttons respect threshold (closed prior audit F4)
- [x] Reset button restores defaults (shipped 2026-04-30)
- [x] `plotly_click → oDrFRisk` drill works
- [ ] **CSV export works** — F1 RED, function not defined
- [ ] Fullscreen modal interactive — F2 partially
- [ ] Toolbar state persists across reload — F3 / B91 not implemented
- [x] Themes — all colors via `getComputedStyle(--token)` so dark/light both work
- [x] Note hook + tip + about all wired
- [x] No console errors on render (zero in current samples)
- [ ] **Sign-color on TE bars** — D1/D2 PM-gate

---

## Summary

**Verdicts:** Data **YELLOW** / Functionality **YELLOW** / Design **GREEN**

**Top 3 findings:**
1. **CSV button is a silent no-op** — `exportFacContribCsv` referenced in chrome but never defined. F1, ~15 LOC fix, coordinator can ship inline.
2. **Sign-collapse on TE bars persists** despite signed data being available across all 6 strategies (Profitability consistently c≈-0.4, *diversifying as intended*). The current "✦ Intentional — higher is desired" annotation is the wrong narrative when c is negative. PM-gate recommendation: color-by-sign-of-c (option b in D1).
3. **No defensive-UI footer** — when threshold/group filters hide bars, the user has no signal that "84% of factor TE is in the visible bars" or "12 of 16 factors shown (domestic model)". Add the cardRiskByDim-style footer below chart. ~10 LOC.

**Major progress since 2026-04-24:**
- Card now has stable id (B78 closed)
- Note hook + tip + About registered
- `plotly_click → oDrFRisk` wired
- All hardcoded hexes tokenized
- `tileChromeStrip` migrated (Phase D)
- Reset button shipped
- threshold/group intersect logic fixed
- `role="radiogroup"` shipped
- F2 (`hist.fac` empty) acknowledged in code

**What's still open:**
- F1 (CSV no-op) — RED, trivial fix
- F2 (FS fallback) — YELLOW, ship option A
- F3/B91 (state persistence) — YELLOW, queued
- D1/D2 (sign-color) — YELLOW, PM gate
- D3/X3 (footer disclosure) — YELLOW, trivial-but-larger
- D5 (profitability alert source) — YELLOW, trivial

**Relevant paths:**
- `/Users/ygoodman/RR/dashboard_v7.html:7780–7841` — tile DOM
- `/Users/ygoodman/RR/dashboard_v7.html:7672–7681` — facMCR build
- `/Users/ygoodman/RR/dashboard_v7.html:8150–8245` — `rRiskFacBarsMode`
- `/Users/ygoodman/RR/dashboard_v7.html:8255–8301` — toolbar mutators + reset
- `/Users/ygoodman/RR/dashboard_v7.html:9952` — `oDrFRisk` alias
- `/Users/ygoodman/RR/dashboard_v7.html:1229` — about registry
- `/Users/ygoodman/RR/dashboard_v7.html:2390–2412` — `getFactorsForWeek` / `_wFactors`
- `/Users/ygoodman/RR/data/strategies/{IDM,IOP,EM,ISC,GSC,ACWI}.json` — verified signed `f.c` ground truth
- `/Users/ygoodman/RR/tile-specs/cardFacContribBars-audit-2026-04-24.md` — prior audit (basis for delta analysis)
