# cardFacContribBars — Tile Audit 2026-04-24

**Target:** Factor Contributions card on Risk tab
**DOM:** `<div class="card">` at `/Users/ygoodman/RR/dashboard_v7.html:3114–3160` (anonymous wrapper)
**Inner chart:** `#riskFacBarDiv` L3159
**Render:** `rRiskFacBarsMode()` L3319–3404; data build at L3020–3025 (in `rRiskNew`); toolbar state mutators `setFacGroup` L3414, `setFacThresh` L3424, `setFacBarAll` L3431
**Batch:** Tier 1, Batch 7 (final)
**Proposed id:** `cardFacContribBars` (per B78 anonymous-Risk-tab-card sweep)

---

## Track verdicts

| Track | Verdict | Headline |
|---|---|---|
| **T1 Data accuracy** | **RED** | 4th site of B73 active-vs-raw conflation (within-tile between Exposure mode and Both mode's overlay); 6th site of B74 sign-collapse; threshold slider contradicts group-pill (setFacGroup overrides threshold without re-applying it); Profitability alert compares `prev.a` vs `curr.a` on `hist.fac` whose `a` field is reliable per AUDIT_LEARNINGS but parser-side `bm:None` makes delta-interpretation fragile. |
| **T2 Functionality parity** | **RED** | No card `id` (blocks note-hook, screenshotCard, CSV-export targeting); no `oncontextmenu` note-hook on card-title; no `plotly_click` → `oDrFRisk(factor)` drill (sibling `cardRiskFacTbl` has it at L3180); no CSV export ("export as visible" especially valuable here given toggle+threshold state); no full-screen (⛶) button; no `rr.facContrib.*` localStorage for toolbar state. |
| **T3 Design consistency** | **YELLOW** | `--prof` token exists (L15) but `#fb923c` is hardcoded at 4 sites inside this tile (L3134 class-inline, L3153 checkbox border, L3339 bar color, L3340 shadow); `#6366f1`/`#a78bfa` hardcoded at L3339 should be `var(--pri)`/`var(--pri-alt)`; Both-mode `rgba(99,102,241,0.75)` + `rgba(245,158,11,0.75)` hardcoded at L3375/L3379; radio-toggle group lacks `role="radiogroup"` / visible focus outline; threshold slider lacks `aria-valuetext`. |

---

## Section 0 — Identity

| Field | Value |
|---|---|
| Tile name | Factor Contributions |
| Card DOM id | **(none — propose `cardFacContribBars`)** |
| Wrapper lines | L3114–L3160 |
| Inner chart div | `#riskFacBarDiv` L3159 |
| Render function | `rRiskFacBarsMode()` L3319 (data source `facMCR` built in `rRiskNew` L3020) |
| Tab | Risk |
| Width | full (parent layout) |
| Toolbar state globals | `window._rfbMode` (te/exp/both, L3119/3122/3125, init L3232); `window._rfbData` (L3233); `.fgp.active` (DOM-only, no JS var); threshold value read live from `#facThreshSlider` (L3425); no persisted state |
| Spec status | draft |

---

## Section 1 — Data Source (T1)

### Field inventory

| # | Element | Source path | Formatter | Sign? | Confirmed |
|---|---|---|---|---|---|
| 1 | Checkbox label | `f.n` | — | — | ✅ `cs.factors[].n` |
| 2 | Checkbox `data-c` | `Math.abs(f.c\|\|0)` | `toFixed(2)` | **absolute** | ⚠️ B74 — checkbox threshold uses \|c\|; invisible to user that diversifying factors are lumped with risk-adding ones at the same threshold |
| 3 | TE-mode bar x | `Math.abs(f.c\|\|0)` L3353 | `f2(,1)%` | **absolute** | ⚠️ B74 6th site |
| 4 | TE-mode shadow bar | `Math.max(f.devPct, \|f.c\|)` L3347 | — | **absolute** | overlay of "factor-σ-share-of-TE" behind "\|contrib\|-share-of-TE"; two different denominators (σ → absolute TE, c → % of TE) plotted on same axis |
| 5 | Exp-mode bar x | `f.e` L3364 (which is `f.a` from L3024) | `fp(,2)` | **signed** | ✅ correctly signed (renamed as `e` in facMCR but holds active) |
| 6 | Both-mode exposure bar | `f.e` L3374 signed | — | signed | ⚠️ filtered via `FAC_PRIMARY.has(f.n)` L3372, so Both-mode silently drops Market Sensitivity, Size, Leverage, Liquidity, FX Sensitivity, Mid Cap, Earnings Variability — i.e. the "Secondary" and "Market Behavior (subset)" pill groups become invisible when user lands on Both |
| 7 | Both-mode TE bar | `Math.abs(f.c)` L3378 | — | **absolute** | ⚠️ this is the apples-to-oranges risk — exposure bar is signed±, TE bar is magnitude-only, overlaid without visual differentiation of sign |
| 8 | Profitability alert trigger | `hist.fac['Profitability'][].a ?? .e` L3400 | — | signed | ⚠️ `a??e` fallback — on riskm path parser sets `bm:None` so `hist.fac[].a` should be populated per parser L857; if `a` absent falls back to raw `e`, triggering spurious alerts (adjacent to B73 root cause) |

### Findings — data

**F1 [RED, B74 6th site]** — Sign collapse inside this tile at 6 distinct call sites (L3153 checkbox data-c, L3347 shadow-max, L3353 TE bar x, L3355 TE text, L3378 Both-mode TE bar, L3380 Both-mode TE text). Escalates B74: a diversifying Profitability (negative `f.c`) and a risk-adding Profitability of equal magnitude render identically, contradicting the tile's explicit "Intentional — higher is desired" narrative annotation at L3357 (which can be true only when exposure is positive). **[PM gate]** — resolve under B74 shared `mcrSigned()` + color-by-sign convention.

**F2 [RED, B73 4th site]** — Active-vs-raw within-tile overlay conflation. TE mode plots `|f.c|` (% of TE, sign-collapsed). Exp mode plots `f.a` (active). Both mode overlays them on twinned x-axes with no unit disclaimer. User reading Both mode sees two bars labeled simply "Active Exposure" + "TE Contrib %" side-by-side for the same factor but the TE bar's magnitude is already `|sign-collapsed|` while the Exposure bar is signed — they narratively disagree whenever `f.c` is negative (diversifying) and `f.a` is negative. **[PM gate]** — adopt B74 signed-MCR or add an explicit legend note "|TE %| regardless of direction".

**F3 [RED]** — Threshold slider is overridden silently by group pill. `setFacGroup` L3418 unconditionally rewrites every `.fac-bar-chk.checked` based on group membership, ignoring the current `facThreshSlider.value`. User sets threshold=5% (filters to 4 factors), clicks "Value / Growth" pill → 5 factors check on including ones below 5%. The displayed slider still says 5.0. Fix: `setFacGroup` should intersect: `chk.checked = inGroup(chk) && parseFloat(chk.dataset.c)>=thresh`. **[trivial, 1-line]**

**F4 [YELLOW]** — `setFacBarAll(true)` L3431 also ignores threshold — "All" button re-checks boxes below threshold. Same fix pattern. **[trivial]**

**F5 [YELLOW]** — Both-mode silently drops non-primary factors (L3372 `FAC_PRIMARY.has` filter) — "Secondary" pill group produces ZERO bars in Both mode regardless of how many checkboxes the user selects. The pill keeps its "active" state but the chart is empty or shows only the handful of primaries that overlap. Neither a disclaimer nor a pill-disable is rendered. Either disable the "Secondary" pill when in Both mode, or remove the `FAC_PRIMARY` gate (let Both mode show all selected factors). **[trivial]**

**F6 [YELLOW]** — Profitability alert (L3394–3403) compares `curr.a ?? curr.e` vs `prev.a ?? prev.e`. Per AUDIT_LEARNINGS, parser `_collect_riskm_data` L468 hardcodes `bm:None`, so `hist.fac[*][].a` derivation depends on whether `_build_factor_list` populates `a` at the hist-entry level. If any fall through to `.e` (raw exposure), a rising raw exposure with flat active would suppress the alert or fire it spuriously. **[pending data probe, couples to B73/B77]**

**F7 [YELLOW]** — `facMCR.sort` at L3025 sorts by `|f.c|` (sign-collapsed), so Exp mode's bar order is "loudest risk contributor first" not "largest active exposure first" — a user toggling from TE to Exp sees ordering that doesn't match the x-axis semantic. Consider per-mode sort. **[PM gate]**

**F8 [GREEN]** — `devPct` (factor-σ shadow bar) derivation `(f.dev/totalTE*100)` L3023 is arithmetically sound; the overlay is visually ambiguous but the computation is correct.

---

## Section 4 — Functionality (T2)

| Capability | Benchmark | This tile | Gap |
|---|---|---|---|
| Stable card `id` | ✅ | ❌ | **YES** — blocks note-hook, screenshotCard, CSV helper targeting (B78) |
| Card-title note-hook `oncontextmenu` | ✅ sibling tiles | ❌ L3116 | **YES** |
| Card-title `tip` / `data-tip` | ✅ | ❌ | **YES** |
| `plotly_click` → drill | cardRiskFacTbl row click ✅ | ❌ | **YES** — wire `plotly_click → oDrFRisk(point.y)` |
| CSV export (of visible bars) | cardRiskFacTbl has it L3166 | ❌ | **YES** |
| Full-screen (⛶) | cardCountry/cardScatter have it | ❌ | YES — nice-to-have |
| Toolbar state persisted `rr.facContrib.*` | — | ❌ | **YES** |
| Theme-aware colors | partial | partial | YES — bar colors hardcoded |
| Keyboard-accessible mode toggle | — | ❌ | YES |

### Findings — functionality

**F9 [RED, B78]** — Add `id="cardFacContribBars"` to wrapper at L3114. **[trivial]** — 1-line. Unlocks F10, F11, F14.

**F10 [RED]** — Add `class="card-title tip"`, `data-tip="..."`, and `oncontextmenu="showNotePopup(event,'cardFacContribBars');return false"` on L3116 title div. Depends on F9. **[trivial]**

**F11 [RED]** — No `plotly_click` wired. `oDrFRisk(name)` already exists L3540 and is invoked from the sibling table at L3180. Add after L3392. **[trivial — 3 lines]**

**F12 [RED]** — No CSV export. Snapshot currently-rendered bars as `[Factor, Active Exposure, TE Contrib %, MCR to TE, Return, Impact]`. Using generic `exportCSV` won't work (no `<table>`) — need `exportFacBarVisible()`. **[trivial — ~15 lines]**

**F13 [YELLOW]** — Toolbar state not persisted. Wire `_rfbMode`, threshold slider value, group-pill selection, checkbox set to `localStorage['rr.facContrib.*']` and restore on `rRiskNew`. **[trivial — ~20 lines]**

**F14 [YELLOW]** — No full-screen button. **[PM gate]**

**F15 [YELLOW]** — Radio group accessibility. Inputs `display:none`; visible labels have `cursor:pointer` but no `tabindex`, no `:focus`, no `role="radiogroup"`. **[trivial]**

**F16 [YELLOW]** — `setFacGroup` "Secondary" pill activates but Both mode silently empty-renders (see F5). **[trivial]**

---

## Section 6 — Design (T3)

| Site | Hardcoded | Should be |
|---|---|---|
| L3134 `class="fgp prof"` — pill itself | via class L173 | ✅ OK |
| L3153 checkbox border `#fb923c` + `rgba(251,146,60,0.08)` | hex + rgba | `var(--prof)` |
| L3153 span color `#fb923c` | hex | `var(--prof)` |
| L3339 bar color `'#fb923c'` (both sides of ternary) | hex | `var(--prof)` |
| L3339 non-prof bar `'#6366f1'` / `'#a78bfa'` | hex | `var(--pri)` / `--pri-alt` |
| L3340 shadow colors | rgba | hex2rgba with tokens |
| L3375 Both-mode exposure `rgba(99,102,241,0.75)` | rgba | hex2rgba(var(--pri),.75) |
| L3379 Both-mode TE `rgba(245,158,11,0.75)` | rgba | hex2rgba(var(--warn),.75) |

**F17 [YELLOW]** — Tokenize `#fb923c` → `var(--prof)` at L3153 (×2), L3339 (×2), L3340 (×1). **[trivial]**

**F18 [YELLOW]** — Non-prof bar colors `#6366f1`/`#a78bfa` L3339 — introduce `--pri-alt` token OR use THEME().pos/THEME().neg. **[trivial once token exists]**

**F19 [YELLOW]** — Both-mode colors L3375, L3379 — move behind `hex2rgba(getComputedStyle…)` helper. **[trivial]**

**F20 [YELLOW]** — L3118 `background:var(--riskFacMode,var(--pri))` references undefined custom property `--riskFacMode` — dead code, resolves to default. Simplify to `var(--pri)`. **[trivial]**

**F21 [YELLOW]** — Legend at `y:1.18` may overlap group-pill row on narrow viewports. **[PM gate]**

---

## Fix queue

### TRIVIAL (agent can apply, low risk)
1. **F9** — Add `id="cardFacContribBars"` to wrapper L3114 (B78)
2. **F10** — Note-hook + `tip` + `data-tip` on card-title L3116
3. **F11** — Wire `plotly_click` → `oDrFRisk` after L3392
4. **F17** — Tokenize `#fb923c` → `var(--prof)` at 4 sites
5. **F19** — Tokenize hardcoded rgba at L3340, L3375, L3379
6. **F20** — Remove dead `--riskFacMode` custom-prop at L3118
7. **F3** — `setFacGroup` respects threshold (intersect)
8. **F4** — `setFacBarAll(true)` respects threshold
9. **F5/F16** — Drop `FAC_PRIMARY` filter in Both mode OR disable Secondary pill
10. **F15** — Add `role="radiogroup"` + `tabindex` + `:focus` outline

### TRIVIAL BUT LARGER (≤20 lines each)
11. **F12** — CSV export `exportFacBarVisible()`
12. **F13** — Persist toolbar state to `rr.facContrib.*`
13. **F18** — Introduce `--pri-alt` token OR tokenize palette

### PM GATE
14. **F1 / F2 (B74 / B73)** — Sign-decollapse decision
15. **F6** — Data probe of `hist.fac['Profitability'][].a` completeness
16. **F7** — Per-mode sort order
17. **F14** — Full-screen variant

### BACKLOG (new)
- **B90** — TE-mode shadow-bar (`devPct` overlay) ambiguous hover — remove shadow or clarify hovertemplate denominators
- **B91** — `setFacGroup` case-insensitive substring match (L3419) — "Momentum" and "Momentum (Medium-Term)" both match "Momentum" — switch to explicit-list membership

---

## Summary

**Verdicts:** Data **RED** / Functionality **RED** / Design **YELLOW**

**Top 3 findings:**
1. Card is anonymous — `id="cardFacContribBars"` blocks note-hook + screenshotCard + is the last B78 sweep tile.
2. Sign-collapse on TE mode (6th tile in B74 ledger); Both mode overlays signed Exposure with sign-collapsed TE, narratively inconsistent.
3. Threshold slider silently overridden by group-pill clicks — filters re-applied without threshold intersect.

**Relevant paths:**
- `/Users/ygoodman/RR/dashboard_v7.html:3114–3160` — tile wrapper
- `/Users/ygoodman/RR/dashboard_v7.html:3319–3404` — `rRiskFacBarsMode`
- `/Users/ygoodman/RR/dashboard_v7.html:3414–3434` — toolbar mutators
- `/Users/ygoodman/RR/dashboard_v7.html:3540` — `oDrFRisk`
- `/Users/ygoodman/RR/tile-specs/AUDIT_LEARNINGS.md` — B73/B74/B78
