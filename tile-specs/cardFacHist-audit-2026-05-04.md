# Tile Spec: cardFacHist — Audit v1 (FRESH FIRST-PASS)

> **Audited:** 2026-05-04 | **Auditor:** Tile Audit Specialist
> **Scope:** First formal three-track audit on `cardFacHist` (Risk tab, line 7935). No prior audit on file.
> **Status:** **YELLOW — FUNCTIONALLY USABLE, with one RED data-integrity item (D1 — undeclared simple-sum on Cum Return) and several broken-feature items (F1 — CSV export wired but undefined function; F2 — chart-click drill missing; F3 — silent metric/data-source mismatch).**
> **Verdict at a glance:** Track 1 (Data) = YELLOW (one RED, one GREEN); Track 2 (Functionality) = YELLOW (CSV broken, no chart-click, no peer parity for period selector); Track 3 (Design) = YELLOW (one missing Plotly-color theme leak, missing footer, mixed inline styling).

---

## Triage queue (top of file by design — coordinator can lift directly)

### Trivial fixes (subagent-able, ≤10 LOC each)
- **T1.** Add `exportFacHistCsv()` function (referenced at L7950, never defined) — silent no-op today; user clicking ⬇ on this tile sees nothing happen.
- **T2.** Add hairline footer `<div id="facHistFooter">` with metric-aware caveat string (parallels `rbdFooter` / `attribFooter` pattern).
- **T3.** Add `ᵉ` badge to "Cum Return" pill label OR yTitle when active, with tooltip pointing at the derived-simple-sum caveat (mirror cardFacContribBars' L4811 pattern verbatim).
- **T4.** Wire `plotly_click` handler on `riskExpHistDiv` → `oDrF(d.points[0].data.name)` (one-liner; precedent at L3500, L5715, L6520).
- **T5.** Fix mixed inline styling on `<button class="pill">` (L7942-7944) — three pills inline-override `font-size:10px;padding:2px 7px` whereas the canonical `.pill` class already sets these. Removes 3× 26-char duplication.
- **T6.** Suppress factor lines that have <2 weeks of data with a small "(<2 obs, hidden)" hint (today they silently vanish — user can't tell whether Volatility was deselected or had no data).
- **T7.** `label.style.cursor:pointer` is set inline on each toggle (L7687, L7698) — fold into `.fac-toggle` CSS class.

### Larger fixes (queue with PM review)
- **L1.** Period range selector (3M | 6M | 1Y | 3Y | All) — peer cardCorr has it (L7977-7978), cardTEStacked has it via rangeslider (L8057), but cardFacHist's only periodicity control is "Select All / Clear All" factors. With multi-year files now supported, looking at last-3M factor active-exposure is one click away on cardCorr but requires manual zoom on cardFacHist.
- **L2.** Custom fullscreen handler (`window._tileFullscreen.cardFacHist`) — generic clone fallback at L1445 works but does NOT preserve metric pill / factor-toggle state in the cloned chrome. Compare cardCountry's view-aware FS (LESSONS_LEARNED L298+). Single-line fix: clone state into FS modal before re-Plotly.
- **L3.** Suppress empty/sparse factors at toggle-list level. Currently `allFacs` is built from `_facsForWeek` (the union of factors known at the selected week). For factors that are PRESENT in `cs.factors` but have no `snap_attrib[name].hist` and no `hist.fac[name]`, the toggle is selectable but produces zero traces. Domestic-model files (when they land — see CLAUDE.md) will exhibit this for the 6 worldwide-only factors. Filter the toggles to only-renderable-factors, with a "(N hidden — no history)" footer hint.
- **L4.** Migrate the entire factor-toggle row + per-group dropdown (`facToggleHtml` block, 28 lines L7683-7710) into a reusable `factorPickerHtml(facs, opts)` helper — 4+ tiles will need similar pickers as the audit cadence rolls out.

### PM-decision items
- **P1.** Should "Cum Return" be removed entirely until FactSet ships `cumulative_factor_return` per period? The simple-sum approximation may under-report by ~25% on volatile factors over long windows (per cardFacContribBars audit notation, L4811). Two options: (a) remove until FactSet ships authoritative, (b) keep with `ᵉ` + clear caveat in tooltip + footer. Current state is the worst of both: it ships, but with no marker.
- **P2.** Should the metric pills support a fourth mode "Raw Exposure (e)" — i.e., portfolio exposure absolute, not active? cardCorr operates only on active (`e − bm`). cardFacHist today silently does the same when `bm` is null (`(h.e||0)`). PMs sometimes need raw-portfolio-exposure for the Volatility / Profitability "are we tilted at all in absolute terms" question.
- **P3.** Should week selector highlight the picked week on the time-series with a vertical line / dot marker? cardTEStacked, cardBetaHist, cardRiskHistTrends do NOT do this either, so this is a tab-wide decision not just cardFacHist.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor History |
| **Card DOM id** | `#cardFacHist` (Risk tab, line 7935) |
| **Render function** | `updateFacExpChart()` at `dashboard_v7.html:8313–8408` |
| **Render entry from rRisk** | `riskFns` array at L8002 — try/catch wrapped (B115-style defensive) |
| **CSV exporter** | `exportFacHistCsv` — **REFERENCED BUT NEVER DEFINED** (see F1) |
| **About entry** | `_ABOUT_REG.cardFacHist` at `dashboard_v7.html:1257–1264` |
| **Inner plot id** | `#riskExpHistDiv` (chart-h-md) |
| **Controls** | 3 metric pills (Active Exp / Factor Return / Cum Return), `Select All` / `Clear All` buttons in chrome strip, primary-factor toggles + non-primary expandable dropdowns (Industry / Country sub-checkboxes) |
| **Right-click → note** | wired (L7938 — `oncontextmenu="showNotePopup(event,'cardFacHist')"`) |
| **Data sources** | (a) `cs.hist.fac[name][i].e` and `.bm` (legacy path, empty in current samples), (b) `cs.snap_attrib[name].hist[i].exp` / `.bench_exp` / `.ret` (live path), (c) `cs.hist.sec[item][i].a` for Industry sub-checkboxes, (d) `cs.sectors[].a` and `cs.countries[].a` for synthetic-current fallback when hist absent |
| **Tab** | Risk |
| **Width** | Full-width |
| **Full-screen path** | Generic fallback at `openTileFullscreen` L1439 — clones outerHTML, no state-aware handler registered (see L2) |
| **Drill path** | None on the chart (see F2). Per-factor drill via `oDrF(name)` exists but is not wired here. |
| **Spec status** | `audit-only` — coordinator serializes any code fixes |
| **Persistence** | `localStorage['rr.facHistMetric']` for the selected metric pill (L8306). Factor checkbox state NOT persisted (intentional — toggles default to all-primary-checked on every render, consistent with sibling tiles). |
| **Universe / Avg invariance** | Tile reads only from `_facsForWeek` (which is `_wFactors() = getFactorsForWeek(_selectedWeek)`), `cs.hist.fac`, `cs.snap_attrib`. Does **not** consume `_aggMode` / `_avgMode` — correctly so, since active exposure is portfolio-vs-bench by definition (no Wtd/Avg dimension). **GREEN.** |

---

## 1. Data Accuracy — Track 1

### 1.1 Active Exposure path — VERIFIED CORRECT for primary factors (GREEN)

The metric `'exp'` reads from `s.hist.fac[name]` (parser-shipped, see `_build_hist_fac` at `factset_parser.py:1642–1653`), with `e = exp.c` (current exposure) and `bm = exp.bm` (bench exposure). Active exposure = `h.e − h.bm`.

- **Parser source confirmed**: `factset_parser.py:1642` builds `hist.fac` from `riskm_rows` → `exposures.c` (current) and `.bm` (bench). Same field semantics as `cs.factors[].e` / `.bm` at the latest week, just sliced across history.
- **Render math at L8337**: `y: hist.map(h => h.bm!=null ? +(h.e-h.bm).toFixed(4) : (h.e||0))` — correct subtraction with null-safe fallback to raw exposure.
- **Latest-week consistency check**: at the latest week, `hist.fac[Volatility][last].e − .bm` should equal `cs.factors[name].e − cs.factors[name].bm` (= `cs.factors[name].a` by parser convention). Spot-check trustworthy because both consume the same FactSet exposure source. This is the same correctness path as `cardCorr` (audit 2026-05-01, item 1.1 GREEN).

### 1.2 Active Exposure with empty `hist.fac` (D2 — silent fallback drift)

**Severity: YELLOW.**

`cardCorr` at L5826-5838 has a fallback: if `s.hist.fac` is empty, synthesize from `s.snap_attrib[name].hist` (using `p.exp − p.bench_exp`). **`cardFacHist` does NOT have this fallback.** At L8334-8335:

```js
let hist=facHist[f.n];
if(!hist||!hist.length)return;   // silently skips factor
```

So if the user opens cardFacHist on a sample where `cs.hist.fac` is empty (which IS the case in current samples per the cardCorr-audit observation at L5822-5825), every primary-factor checkbox is checked but **no traces render** and the user sees the fallback "No factors selected" message — implying their selection is wrong, when actually the data path is silently failing.

The cardCorr audit noted this exact issue and shipped the snap_attrib fallback. **cardFacHist is missing the same fix and is the broken-paired-tile.**

**Why-matters:** F18 inquiry workflow + anti-fabrication policy say: surface missing data, don't pretend it's user error. Today this tile silently shows "No factors selected" when the user has 8 factors selected with no data behind them.

**Proposed fix (≤15 LOC):** Mirror cardCorr's fallback at L8334:
```js
let hist=facHist[f.n];
if(!hist||!hist.length){
  const sa=snap[f.n];
  if(sa&&sa.hist&&sa.hist.length){
    hist=sa.hist.map(p=>({d:p.d,e:p.exp,bm:p.bench_exp}));
  }
}
if(!hist||!hist.length)return;
```

### 1.3 Cum Return — UNDECLARED SIMPLE-SUM APPROXIMATION (D1 — RED)

**Severity: RED.** This is a fabrication-marker miss exactly of the kind LESSONS_LEARNED Anti-Pattern 1 (L48-54) prohibits.

At L8349-8353:
```js
if(metric==='cret'){
  let cum=0;
  yvals=rets.map(r=>{cum+=r;return +cum.toFixed(3);});
  lbl='Cum Return';
}
```

This is a **simple sum** of per-week factor returns presented as "Cumulative Return." The codebase already documents (at L991-1002, L4811, L5663-5694, and `_ABOUT_REG.cardFacContribBars` at L1198-1202) that:

1. FactSet's authoritative cumulative is `full_period_imp` — **a compounded** value
2. The simple-sum approximation can under-report by ~25% on high-volatility factors over long windows
3. Wherever the dashboard simple-sums, it ships an `ᵉ` superscript badge with explanatory tooltip

**cardFacHist ships the same approximation with NO marker.**

**Three paths to remediation (PM-decision P1):**

(a) Remove `cret` mode entirely. (Cleanest. Removes a feature PMs may use.)
(b) Keep with `ᵉ` badge on the metric pill + footer note. (Honest — same pattern as cardFacContribBars.)
(c) Wire to `cs.snap_attrib[name].full_period_imp` for the "All" period (authoritative compounded), keep simple-sum for trailing windows with `ᵉ`. Requires a period selector first (item L1).

**My recommendation:** ship (b) immediately as a 5-line fix (yTitle + tooltip + pill aria-label), queue (c) once the period selector lands.

**Why-matters:** PMs use the Cum Return chart to gauge factor-return rotation. A 25% under-report on Volatility over a 3Y window is exactly the kind of "looks plausible but wrong" pattern that triggered the April 2026 crisis.

### 1.4 Factor Return path — semantically OK, time alignment unverified (YELLOW)

`'ret'` reads from `s.snap_attrib[name].hist[].ret`. The values are FactSet-shipped per-week factor returns — **authoritative** (no derivation).

- **Parser confirmed**: `snap_attrib[name].hist` ships per-week `ret` from FactSet's `Factor Return %` column (verified via cardFacContribBars audit context).
- **Date alignment**: `dates = sa.hist.map(h=>isoDate(h.d))` and `rets = sa.hist.map(h=>+(h.ret||0))` are zipped index-by-index. **Unverified for** the case where `snap_attrib[name].hist[i]` and `snap_attrib[other_name].hist[i]` have different dates (i.e., partial coverage). Today the chart trusts that snap_attrib hist arrays are date-aligned across factors — likely true for worldwide-model files (single Axioma model emits one row per (week × factor)), but could break with the upcoming domestic-model merge (CLAUDE.md "Strategy Account Mapping" — domestic + worldwide accounts in one cs).
- **Mitigation**: when domestic file lands, add an integrity check: assert `snap_attrib[f1].hist[i].d === snap_attrib[f2].hist[i].d` for all overlapping (i, f1, f2). Same family of check as the integrity assertion in HARD-RULE 5 (CLAUDE.md).

### 1.5 Empty bm (null benchmark exposure) silently coerced (D3 — YELLOW)

At L8337: `h.bm!=null ? +(h.e-h.bm).toFixed(4) : (h.e||0)`. When `bm` is null, the y-value is `e` (raw exposure), **not active exposure**. The trace is labeled "Active Exposure" in yTitle. **The line is semantically a different metric** than its label.

The cardCorr audit (item 1.2 at L62) flagged the parallel issue: nulls coerced to 0, biasing math. Here it's worse — nulls cross-wire two distinct metrics on the same y-axis silently.

**Proposed fix:** if `bm == null`, drop the point (don't fall back to raw `e`). Add a footer note `Series with null bench-exp dropped: <list>`.

**Why-matters:** The whole tile sells itself as "Active Exposure (e − bm)." A line that quietly is `e` only and labeled "Active Exposure" is a definitional fabrication.

### 1.6 Industry / Country sub-checkbox path — synthetic current-only (D4 — YELLOW)

L8369-8391: when user expands a non-primary factor group (Industry, Country) and ticks a sub-item:

- **Industry**: prefers `cs.hist.sec[item]` (per-sector weekly history). When empty, **synthesizes a flat horizontal line at the current `cs.sectors[name].a` (active weight)** repeated across `cs.hist.sum` dates. Labels "(current)".
- **Country**: ALWAYS synthesizes a flat horizontal line at the current `cs.countries[name].a`. NO per-week history check — even if `cs.hist.ctry` were populated, it's never consulted.

The synthetic flat line is labelled `(current only)` in hovertemplate but this is rendered as a faint dashed line on the same chart with no further banner. PMs eyeballing the chart may not realize a line is a constant placeholder.

**Why-matters:** The MARATHON_PROTOCOL principle "fall back with a useful degraded rendering" is honored, but the visual signal could be stronger. A flat line on a "Factor History" chart is a confusing rendering.

**Proposed fix (after L3 lands):** suppress these synthetic flat lines from the chart entirely; surface them in the toggle-list as disabled (greyed out) with tooltip "no history — current weight only".

### 1.7 Domestic-model graceful degrade — UNVERIFIED (D5 — YELLOW)

CLAUDE.md "Strategy Account Mapping" (post 2026-04-28 update) plans for SCG + Alger accounts under the domestic risk model with a smaller factor set. The toggle list at L7683 iterates `_facsForWeek` (parser-extracted), so the list shrinks naturally for domestic strategies — **GREEN on the picker.**

But: `FAC_PRIMARY` is hardcoded at L4595 and includes worldwide-specific factors (`Dividend Yield`, etc.). On a domestic-model strategy, fewer of these will be in `_facsForWeek`, so `Select All` will check fewer pills (correct), but the chart will silently render fewer lines (also correct). **No visible warning that "this factor doesn't exist in the domestic model — that's why it's missing."**

**Proposed fix:** when a strategy is loaded, compute `missingPrimaryFacs = FAC_PRIMARY - _facsForWeek_names`. If any, render a one-line dim notice in the chrome strip: `Missing in this model: Dividend Yield, …`.

This is the same family as `verify_factset.py` PARTIAL classification (per CLAUDE.md). Surface, don't hide.

---

## 2. Functionality Parity — Track 2

Comparison set: cardCorr (Risk tab peer), cardTEStacked (Risk tab hero), cardFacContribBars (Risk tab peer), cardBetaHist (drill peer).

| Capability | cardFacContribBars | cardCorr | cardTEStacked | **cardFacHist (this)** | Gap? |
|---|---|---|---|---|---|
| Multi-line chart | n/a (bars) | n/a (heatmap) | yes (3 stacked) | **yes** | — |
| Period selector (3M\|6M\|1Y\|3Y\|All) | shared global Impact-period | yes (`#corrPeriod`) | rangeslider | **NO** | **F4 — missing — see L1** |
| Factor multi-select | none | yes (`#corrFactorSel`) | n/a | **yes (toggles + groups)** | — better than peers actually |
| Select-All / Clear-All | n/a | n/a | n/a | **yes (chrome strip extras)** | — |
| Metric toggle | yes (TE / Exp / Both) | n/a | n/a | **yes (Exp / Ret / CumRet)** | — peer parity |
| Right-click note | yes | yes | yes | **yes (L7938)** | — |
| About (`ⓘ`) entry | yes | yes | yes | **yes (`aboutBtn` L7939)** | — |
| Reset Zoom | yes | yes | yes | **yes (L7949)** | — |
| Reset View | yes | yes | yes | **yes (L7952)** | — |
| Hide tile | yes | yes | yes | **yes (L7953)** | — |
| Full-screen | yes (custom) | none | yes | **generic fallback** | **F5 — see L2** |
| CSV export | yes (`exportFacContribBars…`) | yes (`exportCorrCsv`) | yes (`exportTEStackedCsv`) | **REFERENCED + UNDEFINED** | **F1 — RED** |
| PNG export | n/a (per "no PNG buttons") | n/a | n/a | n/a | — (per user pref MEMORY.md) |
| Click chart → drill | yes (bar → `oDrF`) | n/a (heatmap) | yes (chart → `oDrMetric('te')` L8062) | **NO** | **F2 — missing — see T4** |
| Hover line tooltip | yes | yes (cell) | yes | **yes (`hovertemplate`)** | — |
| Universe/Avg invariance | n/a | n/a | n/a | **n/a — correctly invariant** | — GREEN |
| Week-selector follows | yes (factors per-week) | yes (period slice ends at week) | yes (rangeslider includes week) | **YES via `_facsForWeek`** | — GREEN |
| Empty-state suppression | yes | yes | yes | **partial (L8398 message)** | — adequate, see L3 |
| Theme-aware Plotly | yes (tokenized) | yes (cardCorr 2026-05-01 fix) | yes (`_teStackColors()`) | **NO — hardcoded hex array L7682, L8316** | **F6 — see Track 3 design** |

### F1 — `exportFacHistCsv` referenced but undefined (RED)

**Location:** L7950 `csv:'exportFacHistCsv&&exportFacHistCsv()',`. There is no `function exportFacHistCsv` anywhere in `dashboard_v7.html` (verified via `grep -n "function exportFacHistCsv|exportFacHistCsv\s*="`).

The `&&` short-circuit hides the bug: when `tileChromeStrip` builds the CSV button, the inline JS evaluates `exportFacHistCsv` — which is `undefined` — and the `&&` returns `undefined` without throwing. **Click does nothing. No error. No telemetry.**

**Why-matters:** L1-L4 launch readiness depends on every visible button doing what it says.

**Proposed fix:** add a simple CSV exporter mirroring `exportTEStackedCsv` (L8087-8103):

```js
function exportFacHistCsv(){
  if(!cs)return;
  const facs=window._riskAllFacs||[];
  const checked=[...document.querySelectorAll('.fac-exp-chk:checked')].map(c=>c.dataset.fac);
  const metric=_facHistMetric;
  const facHist=cs.hist.fac||{};
  const snap=cs.snap_attrib||{};
  // Union of all dates across selected factors
  const dateSet=new Set();
  // ... build matrix [Date, Factor1_metric, Factor2_metric, ...]
  // emit CSV with caveat header row when metric==='cret'
}
```

Roughly 25-40 LOC. Mirrors the pattern in `exportTEStackedCsv` and `exportHoldRiskCsv` (L8068+).

### F2 — No chart-click drill (YELLOW)

**Location:** L8402-8407 — Plotly newPlot finishes, no `el.on('plotly_click', …)` is attached. Compare cardTEStacked at L8062 which wires `oDrMetric('te')` on chart click.

**User flow today:** PM looks at the time-series, spots Volatility spiking in Mar 2026, wants to drill into "what holdings drove this" — has to leave this tile, find the factor in cardRiskFacTbl, click that row.

**Proposed fix (T4):** ≤3 LOC at L8407:
```js
const el2=document.getElementById('riskExpHistDiv');
if(el2&&el2.on)el2.on('plotly_click',function(d){
  const n=d&&d.points&&d.points[0]&&d.points[0].data&&d.points[0].data.name;
  if(n&&typeof oDrF==='function')oDrF(n);
});
```

Precedent: L3500, L5715, L6520, L6666.

### F3 — Metric pills don't gate visibility of unsupported factors (LOW)

When user selects metric `Factor Return` or `Cum Return`, the data source changes from `cs.hist.fac` to `cs.snap_attrib[name].hist`. The factor toggle list does NOT update — toggles for factors that exist in `hist.fac` but not in `snap_attrib` (or vice versa) appear interactive but produce no trace.

**Why-matters:** PMs see a checkbox, tick it, get nothing. Mid-grade UX leak.

**Proposed fix (deferred):** when metric changes, re-style toggle labels: `opacity: 0.4` + tooltip "no data in this metric for this factor." Defer to L3 batch fix.

### F4 — Period selector missing (YELLOW — see L1)

Long-history files (3-year+) make this prominent. Plotly's drag-zoom is a workaround, but pre-set ranges are 1-click.

### F5 — Fullscreen handler missing (LOW — see L2)

Generic clone works. State preservation incomplete.

### F6 — Color palette hardcoded hex, not tokenized (YELLOW — see Track 3)

---

## 3. Design Consistency — Track 3

| Item | Status | Note |
|---|---|---|
| `tileChromeStrip` used | ✅ GREEN (L7947-7955) | About / Reset Zoom / CSV / Reset View / Hide all routed through canonical helper. |
| Card-title with `tip` class | ✅ GREEN | L7938 — explanation tooltip on header. |
| About button | ✅ GREEN | `${aboutBtn('cardFacHist')}` L7939. |
| Right-click → note popup | ✅ GREEN | `oncontextmenu="showNotePopup(event,'cardFacHist')"` |
| Section labels | ✅ GREEN | "Metric" uses `.section-label` (L7941), tokens applied. |
| Pill class | ✅ GREEN | `.pill` class used (L7942-7944). |
| Pill inline style overrides (T5 — YELLOW) | ⚠️ | Three pills each redeclare `style="font-size:10px;padding:2px 7px"` — fold into a `.pill-sm` modifier (already exists per cardFacContribBars). |
| Factor-toggle inline styling (T7 — LOW) | ⚠️ | L7687-7705 inline-styles every label and dropdown — ~28 lines that should be a `.fac-toggle` + `.fac-toggle-group` CSS pair. cardCorr's L7986 has the same anti-pattern (one big `<label>` with 7 CSS props inline). When it ships, roll out across both tiles in one commit. |
| Plotly hardcoded hex colors (F6 — YELLOW) | ⚠️ | L7682 `facColors=['#6366f1','#10b981','#a78bfa', …]` — ten hex literals. Compare cardTEStacked's `_teStackColors()` (L8014-8026) which reads from `--warn`, `--cyan`, `--pri` tokens. For the user's planned light theme, these hardcoded hex values are NOT theme-responsive. Hex `#a78bfa` is `--pri-alt`, `#6366f1` is `--pri`, `#10b981` is `--pos`. **Tokenizable in 8 LOC.** |
| Hairline footer + caveat (T2 — YELLOW) | ⚠️ | No footer at all on this tile. Compare `rbdFooter` (L7924), `attribFooter` (L5694). Footer should carry: source ("cs.snap_attrib • cs.hist.fac"), metric-aware caveat (especially Cum Return → simple-sum disclaimer), week count, and missing-factors note (D5). |
| Chart height token | ✅ GREEN | `chart-h-md` class (L7958). |
| Empty-state styling | ⚠️ MIXED | "No factors selected" uses inline `<p style="…padding:20px;text-align:center">` (L8398) instead of an `.empty-state` class. Six other tiles emit the same inline pattern; ripe for a one-line CSS class extraction. Track 3 nit, deferred. |
| Hover tooltip on header | ✅ GREEN | `data-tip` populated (L7938). |
| Card padding | ✅ GREEN | Uses `.card` defaults — no inline override on the wrapper. |
| Color semantics consistent with peer tiles | ⚠️ | Peer cardFacContribBars uses `--pri` (positive exp) / `--pri-alt` (negative exp) (L8175-8177). cardFacHist assigns colors **by index order** (`facColors[colorIdx++%facColors.length]`) — Volatility might be indigo today, green tomorrow as factor list re-sorts. **Predictable color → factor mapping** would let PMs do at-a-glance recognition across tiles. Recommend a `FAC_COLOR_REG` keyed by factor name (Volatility → `--warn`, Value → `--pri`, Growth → `--pos`, etc.) for cross-tile consistency. **Larger fix — defer to L4 or new ticket.** |
| Numeric-axis font / tick scale | ✅ GREEN | Uses `plotBg.yaxis` defaults (themed). |

---

## 4. Findings index (consolidated)

| # | Severity | Track | Location | One-line |
|---|---|---|---|---|
| **D1** | 🔴 RED | Data | L8349-8353 | Cum Return is a simple-sum, presented as compounded — no `ᵉ` marker (anti-fab violation). |
| **D2** | 🟡 YELLOW | Data | L8334-8335 | Missing snap_attrib fallback for empty hist.fac (cardCorr has it; cardFacHist doesn't). |
| **D3** | 🟡 YELLOW | Data | L8337 | When `bm` is null, falls back to raw `e` while still labeled "Active Exposure." |
| **D4** | 🟡 YELLOW | Data | L8369-8391 | Industry / Country sub-checkboxes synthesize flat-line "current weight" placeholders silently. |
| **D5** | 🟡 YELLOW | Data | L7681 | Domestic-model factor absences not visibly flagged. |
| **F1** | 🔴 RED | Func | L7950 | `exportFacHistCsv` referenced but never defined — silent no-op. |
| **F2** | 🟡 YELLOW | Func | L8402-8408 | No chart-click drill — peers have it. |
| **F3** | 🟢 LOW | Func | L8326-8392 | Metric change doesn't disable toggles for factors with no data in that metric. |
| **F4** | 🟡 YELLOW | Func | (missing) | No period selector (3M / 6M / 1Y / 3Y / All) — peers have it. |
| **F5** | 🟢 LOW | Func | L7951 | Generic fullscreen fallback — state not preserved through clone. |
| **F6** | 🟡 YELLOW | Design | L7682 | Hardcoded Plotly hex palette, not tokenized — not theme-responsive. |
| **T2** | 🟡 YELLOW | Design | (missing) | No hairline footer with source / caveat / week-count. |
| **T5** | 🟢 LOW | Design | L7942-7944 | Inline pill styles duplicate `.pill` class. |
| **T7** | 🟢 LOW | Design | L7687-7710 | Inline label / dropdown styles — fold to CSS classes. |

---

## 5. Verification checklist

- [x] Data source identified (cs.hist.fac primary; cs.snap_attrib for ret/cret; cs.hist.sec for industry sub-checkboxes; cs.sectors / cs.countries for synthetic-current fallback)
- [x] Active Exposure math verified at code level (h.e − h.bm)
- [x] Cum Return derivation traced (simple sum — RED finding D1)
- [x] Factor Return path traced to FactSet-shipped `ret` field (authoritative)
- [x] Edge cases — empty hist.fac (D2), null bm (D3), missing factors (D5), <2 obs filter (T6 trivial — actually NOT filtered today, factors silently disappear)
- [x] Sort / filter — multi-factor toggles work; metric pills work; persistence works (`rr.facHistMetric`)
- [x] Chart-click drill — **MISSING (F2)**
- [x] CSV export — **BROKEN (F1)**
- [x] Full-screen — generic clone fallback, no custom handler
- [x] Universe/Avg invariance — GREEN (correctly does not consume agg/avg)
- [x] Week-selector flow — GREEN via `_facsForWeek` / re-render through `upd()` → `rRisk()`
- [x] Theme-awareness — partial (Plotly palette hardcoded F6)
- [x] Console errors — none expected from this tile (no syntax / template-literal traps observed in render path)

---

## 6. Top 3 findings (for parent agent)

1. **D1 (RED): Cum Return ships an undeclared simple-sum approximation.** No `ᵉ` marker, no caveat tooltip, no footer note. This is the same anti-pattern that triggered the April 2026 crisis (LESSONS_LEARNED Anti-Pattern 1). Fix path: PM-decision P1 between (a) remove the mode, (b) add `ᵉ` + tooltip, (c) wire to `full_period_imp` once a period selector lands.
2. **F1 (RED): CSV export button silently no-ops.** `exportFacHistCsv` is referenced in `tileChromeStrip` but never defined. The `&&` short-circuit masks the missing function. Fix: 25-40 LOC mirror of `exportTEStackedCsv`.
3. **D2 (YELLOW): Missing `snap_attrib` fallback for empty `hist.fac`.** cardCorr (peer Risk-tab tile, audit 2026-05-01) shipped this fallback at L5826-5838. cardFacHist needs the same — without it, the tile silently shows "No factors selected" on samples where the legacy hist.fac path is empty (which is the case in current samples per the cardCorr audit observation).

---

## 7. Notes / open questions

- **Q1 — PM-decision P1:** which Cum Return path? My recommendation: ship `ᵉ` + tooltip immediately as the "honest math" version, then upgrade to FactSet compounded once L1 (period selector) lands.
- **Q2 — PM-decision P2:** is there value in a "Raw Exposure" mode? Probably yes for Volatility / Profitability where absolute tilt matters, but defer until a PM asks.
- **Q3 — PM-decision P3:** week-selector vertical-line annotation across all Risk-tab time-series tiles? Tab-wide question.
- **Q4 — for FactSet inquiry log (FACTSET_FEEDBACK.md):** does FactSet ship a `cumulative_factor_return` / `compounded_period_return` per (factor × week × window)? If yes, F19+. If no, P1 collapses to (a) or (b).
- **Q5 — domestic-model file timing:** when does CLAUDE.md "domestic file forthcoming" land? D5 (missing-factor notice) becomes important the moment SCG flips to domestic.

---

**Audit complete.** No code changes made (auditor role per project rules). Coordinator to serialize T1-T7 trivial fixes and queue L1-L4 + P1-P3.
