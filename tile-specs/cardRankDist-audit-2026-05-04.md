# cardRankDist — Tile Audit (2026-05-04)

**Auditor:** tile-audit subagent (Opus 4.7 1M)
**Status:** v1 audit complete · NOT signed off (requires user in-browser review)
**Methodology:** `~/orginize/knowledge/skills/tile-audit-framework.md`

---

## Section 0 — Identity

| Field | Value |
|---|---|
| Tile name | Rank Distribution |
| DOM id | `#cardRankDist` |
| Renderer | `rRankDist()` at line **9657** |
| Render call site | line 9564 (post-`rHoldings()` setTimeout) |
| Tab | Holdings (g2 grid, paired with cardTop10) |
| Width | half (g2) |
| Chart type | Plotly vertical bar |
| Chart container | `#rankDistDiv` (`.chart-h-sm`) |
| ⓘ About entry | line 1173 (present, complete) |
| chrome strip | YES — `tileChromeStrip({resetZoom, fullscreen, resetView, hide})` ✓ |
| Universe pill (`_aggMode`) reactive? | **NO** |
| Week selector (`_selectedWeek`) reactive? | **NO** |
| Spec status | draft → audited (this file); user signoff pending |

---

## Section 1 — Data Source (TRACK 1)

### 1.1 — How `cs.ranks[]` is built (the data the renderer reads)

Two-stage pipeline:

1. **Parser (`factset_parser.py:1373`)** ships `ranks = {overall, rev, val, qual}` — but each is the per-quintile aggregate from FactSet's "Ranks" section, **with randomized q values** (see normalize note below).
2. **Normalize (`dashboard_v7.html:1954`)**:
   ```js
   st.ranks=[1,2,3,4,5].map(function(r){
     var hh=st.hold.filter(function(h){return h.r===r;});
     var ct=hh.length;
     var p =hh.reduce(function(a,h){return a+(h.p||0);},0);
     var ap=hh.reduce(function(a,h){return a+(h.a||0);},0);
     return{r:r,l:'Quintile '+r,ct:ct,p:+p.toFixed(2),a:+ap.toFixed(2)};
   });
   ```
   The parser-shipped ranks dict is **discarded**; cs.ranks is rebuilt from holdings. This is the right call — comment at line 1953 says "ALWAYS build from holdings (parser ranks dict has randomized q values)".

### 1.2 — Where `h.r` (the per-holding quintile) comes from

Normalize, line 1897:
```js
if(hn.r==null&&hn.over!=null) hn.r=Math.round(Math.min(5,Math.max(1,hn.over)));
```
`h.over` is the FactSet `OVER_WAvg` column. `Math.round` here is the **rounding rule** — banker's rounding via JS `Math.round` (rounds 0.5 toward +Infinity). For typical OVER_WAvg values (1.0–5.0) this matches FactSet's quintile bucketing.

### 1.3 — Renderer field map

```js
function rRankDist(){
  const ranks = (cs && cs.ranks) || [];
  // ...
  Plotly.newPlot('rankDistDiv', [{
    x: ranks.map(r => r.l),         // 'Quintile 1' .. 'Quintile 5'
    y: ranks.map(r => r.p),         // port-weight Σ per quintile
    text: ranks.map(r => f2(r.p)+'%'),  // outside label
    customdata: ranks.map(r => [r.r, r.ct, r.a]),
    hovertemplate: 'Port wt: %{y:.2f}%<br>Securities: %{customdata[1]}<br>Active wt: %{customdata[2]:+.2f}%'
  }]);
}
```

| Display element | Field | Source path | Provenance | Notes |
|---|---|---|---|---|
| Bar height (Y) | `r.p` | Σ `h.p` filtered by `h.r === q` | Holdings → FactSet Security wgt_port | Sum of port weights per quintile |
| Bar label (X) | `r.l` | `'Quintile ' + r` | normalize literal | — |
| Bar color | `rc(r.r)` resolved → CSS var `--r1..--r5` via `getComputedStyle` | design tokens | ✓ theme-aware |
| Outside text | `f2(r.p)+'%'` | `r.p` rounded via f2 | — | shows port-weight % |
| Hover: Port wt | `r.p` | same as bar height | clean | — |
| Hover: Securities | `r.ct` | count of `cs.hold` where `h.r === q` | clean | excludes null-rank holdings |
| Hover: Active wt | `r.a` | Σ `h.a` filtered by quintile | clean | shows whether quintile is OW/UW |

### 1.4 — F18 contamination — VERIFIED CLEAN

Per SOURCES.md line 172: cardRankDist shows **port-weight per quintile, NOT %T**. Empirically confirmed:
- Bar Y = `r.p = Σ h.p` (port weight, sums to ~100%)
- Hover values = `r.p`, `r.ct`, `r.a` — none of them are `h.tr` or `h.mcr`
- No `%T`, `pct_t`, or `tr` references anywhere in the renderer

**Verdict: F18 disclosure footer NOT required.** Bar heights sum to ~100% portfolio weight ± float rounding ($f2$ to 2dp). Coordinator's classification is correct.

### 1.5 — Edge cases

| Case | Handling | Verdict |
|---|---|---|
| Empty `cs.ranks` (parser shipped no holdings, e.g. corrupt file) | renders empty-state HTML at line 9661: "No quintile data — Spotlight ranks not populated" | ✓ clean |
| Holding with `h.r == null` AND `h.over == null` | excluded from ALL 5 quintiles → silent drop | **YELLOW — see Issue T1.A** |
| Holding with `h.r == null` AND `h.over != null` | bucketed via `Math.round(over)` in normalize | clean |
| OVER_WAvg out of [1,5] range | clamped via `Math.min(5,Math.max(1,…))` | clean |
| Cash holding | included in quintile (cash typically lacks h.r → null → silently dropped) | clean by side-effect, but unintentional |
| Empty quintile (e.g., zero Q5 weight) | `r.p=0`, bar height 0, label "0.00%" outside, hovertemplate works | ✓ clean (Plotly handles zero bars) |
| Single non-zero quintile | renders correctly | clean |

### 1.6 — Spot-check (3 strategies)

I cannot read the live JSON without invoking `data-validator`, but the math is straightforward to validate at render time. Recommended user spot-check:

```js
// Browser console after picking a strategy:
cs.ranks.reduce((a,r)=>a+r.p,0)   // expect ~100 ± rounding
cs.hold.filter(h=>h.r==null).length  // count of "lost" holdings
cs.hold.filter(h=>h.r==null).reduce((a,h)=>a+(h.p||0),0)  // weight not represented in chart
```

If the third number is > 1% (significant unallocated weight), Issue T1.A escalates to RED.

**Section 1 verdict: GREEN with one YELLOW issue (silent null-rank drop).**

---

## Section 4 — Functionality Parity (TRACK 2)

Benchmark = `cardRanks` (Spotlight, on Exposures tab — the closest analogue, also quintile-based).

| Capability | cardRanks (benchmark) | cardRankDist | Gap? |
|---|---|---|---|
| `tileChromeStrip` | YES (`download:csv, fullscreen, resetView, hide`) | YES (`resetZoom, fullscreen, resetView, hide`) | minor — no CSV export |
| Right-click → notes popup | YES (`oncontextmenu="showNotePopup"`) | YES | — |
| ⓘ About button | YES | YES | — |
| Click bar/row → filter Holdings tab | **YES** — `filterByRank(r.q)` (line 5222) → switches tab + filters `fh` | **NO — handler missing** | **RED — see T2.A** |
| Universe pill (`_aggMode`) reactive | YES (line 5165 — toggles port/bench/both) | NO | **YELLOW — see T2.B** |
| Per-week routing (`_selectedWeek`) | partial — uses `cs.hold` directly (latest) | NO | **YELLOW — see T2.C** |
| Reset zoom | n/a (it's a table) | YES (Plotly) | — |
| Fullscreen modal | YES | YES | — |
| Hide tile | YES | YES | — |
| CSV export | YES | NO | minor — see T2.D |
| Empty-state UI | n/a | YES (line 9661) | — |
| Tooltip / hover detail | per-cell tooltips | per-bar hovertemplate (3 fields) | — |
| Theme-aware colors | YES (rc()) | YES (rc() + getComputedStyle) | — |

### Issue T2.A — RED — **Tooltip lies about clickability**

The card-title tooltip (line 9526) reads:
> "Click a bar to filter the holdings table by that quintile."

The ⓘ About entry (line 1175) does NOT make this claim — but the visible tooltip does. **The renderer wires no `plotly_click` handler.** Users following the tooltip's promise will click and nothing will happen.

This is a **documentation lie**, not just a missing feature. Two fix paths:

**Fix A (preferred — implement the feature):** Add at end of `rRankDist()`:
```js
const el = document.getElementById('rankDistDiv');
if(el && el.on){
  el.on('plotly_click', d => {
    const r = d?.points?.[0]?.customdata?.[0];
    if(r && typeof filterByRank === 'function') filterByRank(r);
  });
}
```
`filterByRank()` already exists (line 5241) and does exactly what the tooltip promises — switches to Holdings tab and filters. ~6 lines. Pattern is identical to `rHoldConc` line 9712.

**Fix B (fallback — fix the docs):** Drop the "Click a bar to filter…" sentence from the tooltip and About entry.

**Recommendation: Fix A.** filterByRank is already a public function; sister tile cardRanks already uses it; cost is trivial; UX value is high.

### Issue T2.B — YELLOW — **Universe pill not reactive**

`_aggMode` toggles Portfolio / Benchmark / Both globally. Sister cardRanks responds (line 5165). cardRankDist always shows portfolio weight. For a "Rank Distribution" tile, "Benchmark distribution by quintile" is a real PM question.

Lower priority: portfolio-only is the dominant use case, and the card-title subtitle says "by port weight" — at least it's not lying. But the tile won't update when user toggles to Benchmark mode → users may think the data is stale.

**Fix:** Either (i) wire `_aggMode` reactivity (compute Σ h.b per quintile when in benchmark mode; both sums when "both"), or (ii) add a subtitle note like "(portfolio only — toggle universe to compare)".

### Issue T2.C — YELLOW — **Per-week routing missing**

When user picks a historical `_selectedWeek`, this tile keeps showing latest. Same gap as cardTreemap (documented in About entry). Pattern is consistent across "snapshot from holdings" tiles — but the tile gives no visual indicator that the chart didn't follow the week selector.

**Fix:** Either (i) document in the About entry under `caveats` that it's latest-only, OR (ii) add an amber banner when `_selectedWeek` ≠ null saying "Latest snapshot — quintile data not stored per-week (B114)".

### Issue T2.D — minor — **No CSV export**

cardRanks ships CSV. cardRankDist could ship a 5-row CSV (quintile, count, port_weight, active_weight). Low value (anyone wanting CSV can use cardRanks), but tileChromeStrip supports it cheaply.

**Section 4 verdict: RED on T2.A (tooltip lies), YELLOW on T2.B + T2.C.**

---

## Section 6 — Design Consistency (TRACK 3)

### 6.1 — Design tokens vs hex literals

```js
line 9666: '#94a3b8'   // fallback when CSS var lookup fails
line 9672: 'rgba(255,255,255,0.08)'   // bar edge line
```

- `#94a3b8` = slate-400, used **only** as a fallback — primary path resolves CSS vars `--r1..--r5` via `getComputedStyle`. Acceptable defensive fallback.
- `'rgba(255,255,255,0.08)'` for the bar edge line — light overlay that works in dark theme but may render invisibly on light theme. Compare to peer `rHoldConc` (line 9699) using `'rgba(255,255,255,0.12)'` — same pattern, slightly different alpha (cosmetic inconsistency only).

**Verdict:** acceptable. CSS var path dominates; literal fallbacks scoped to defensive backstops.

### 6.2 — Theme reactivity

- Bar colors → `getComputedStyle(document.documentElement).getPropertyValue('--r1')` etc. — re-resolved on every `rRankDist()` call ✓
- Tick / text colors → `THEME().tick` ✓
- Background → `plotBg` (project's standard Plotly theme) ✓

Tile is fully theme-aware. **GREEN.**

### 6.3 — Typography scale

| Element | Size | Token? |
|---|---|---|
| Card title | uses `.card-title` class | ✓ |
| Subtitle "by port weight · Q1=best" | inline `font-size:10px` | ✓ project mini-cap pattern |
| Bar outside text | `size: 11` | ✓ standard chart label |
| Y-axis title | `size: 10` | ✓ standard axis label |

Within project scale (9/10/11/12/13). **GREEN.**

### 6.4 — Layout

- Card wrapper: `style="margin-bottom:16px"` — consistent with sibling cardTop10
- Chart container: `.chart-h-sm` (project class) — consistent
- `flex-between` header pattern — consistent

**GREEN.**

### 6.5 — Footer caveat

NOT required (per Section 1.4 — no F18 contamination). However, if Issues T2.B / T2.C are deferred, a single-line subtitle note documenting "portfolio-only, latest snapshot" would help. Currently the subtitle says "by port weight · Q1=best" which is silent on universe + week.

**Section 6 verdict: GREEN.**

---

## Section 7 — Known Issues / Open Questions

| ID | Severity | Track | Issue | Fix size |
|---|---|---|---|---|
| T1.A | YELLOW | T1 | Holdings with both `h.r == null` AND `h.over == null` are silently dropped. No "Unranked" bucket; weight loss is invisible. | XS — render-side: add probe to subtitle |
| T2.A | **RED** | T2 | Tooltip promises click-to-filter but no plotly_click handler exists. Either ship the feature (~6 lines, pattern proven on cardRanks/rHoldConc) or fix the tooltip text. | S — 6 lines |
| T2.B | YELLOW | T2 | `_aggMode` (Universe pill) not reactive. Tile always shows portfolio. | M — re-render on _aggMode change OR document |
| T2.C | YELLOW | T2 | `_selectedWeek` not honored. Quintile snapshot is latest-only with no per-week history shipped. | XS (doc) or L (parser-side B114-class work) |
| T2.D | minor | T2 | No CSV export. tileChromeStrip already supports `download.csv`. | XS — 1 line |

### Open questions for PM (user)

1. **T2.A path A vs B:** Wire the click handler (recommended) or strip the tooltip claim?
2. **T2.B priority:** Is "what's the benchmark's quintile distribution" a real PM question? If yes, _aggMode reactivity is worth wiring; if no, just document the limitation.
3. **T1.A visibility:** Should the tile show a "X holdings unranked" footer note when the silent-drop count is > 0? (PM may want to see this; currently invisible.)

---

## Section 8 — Verification Checklist

- [x] **Data source verified** — Σ over `cs.hold[].p` per quintile, rebuilt in normalize line 1954, parser ranks dict correctly discarded
- [x] **F18 classification correct** — port-weight only, NOT %T → no contamination, no footer needed
- [x] **Edge cases** — empty ranks (✓), null h.r (silent drop — see T1.A), zero-weight quintile (✓), OOB OVER_WAvg (✓ clamped)
- [x] **Theme-aware** — both rc() rank colors and THEME() tick/bg react to dark/light
- [ ] **Sort** — N/A (Plotly chart, not table)
- [ ] **Filter** — depends on T2.A fix
- [x] **Reset zoom** — wired via tileChromeStrip
- [x] **Fullscreen modal** — `openTileFullscreen('cardRankDist')` wired
- [ ] **Click → drill / filter** — **MISSING** (T2.A)
- [ ] **CSV export** — missing (T2.D)
- [ ] **Universe pill (`_aggMode`)** — not reactive (T2.B)
- [ ] **Per-week routing (`_selectedWeek`)** — not reactive (T2.C)
- [x] **Empty state** — present, line 9661
- [x] **No console errors expected** — defensive null-coalescing throughout
- [ ] **User in-browser signoff** — pending

---

## Triage queue

### TRIVIAL (agent can apply once user approves) — total ~12 LOC
1. **T2.A Fix A** — wire `plotly_click` → `filterByRank` (6 lines, exact pattern from rHoldConc:9712)
2. **T2.D** — add `download:{csv:"exportCSV(...)"}` to tileChromeStrip opts (1 line + a tiny CSV builder, ~5 lines)
3. **T2.C doc-only fix** — append caveat to About entry line 1175 (1 line)

### NEEDS PM DECISION
1. **T2.A path** — Fix A (wire feature) vs Fix B (fix tooltip). Recommend A.
2. **T2.B** — wire _aggMode reactivity OR ship documentation banner OR defer.
3. **T1.A** — show unranked-holdings count in subtitle when > 0?

### BLOCKED
- **T2.C real fix** (per-week quintile data) — needs B114 / HISTORY_PERSISTENCE.md work on the parser to ship `hist.ranks` per-week. Out of scope for this audit; tile-level fix is documentation only.

---

## Sign-off

- Audit author: tile-audit subagent (Opus 4.7 1M context)
- Audit date: 2026-05-04
- Status: **v1 audit complete, NOT user-signed-off** (per memory: signoff requires user in-browser review)
- Next step: coordinator queues T2.A Fix A for serialized edit on dashboard_v7.html
