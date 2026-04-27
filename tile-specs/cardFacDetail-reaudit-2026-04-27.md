# Tile Re-Audit: cardFacDetail — 2026-04-27 (Marathon Post-Fix)

> **Audited:** 2026-04-27 | **Auditor:** Tile Audit Specialist
> **Trigger:** User-reported regressions during marathon-session live review after commit `0fbb320` ("fix(B109+marathon): Impact-period selector + cardFacDetail refinement")
> **Prior audit:** `tile-specs/cardFacDetail-audit-2026-04-21.md`
> **File audited:** `/Users/ygoodman/RR/dashboard_v7.html` @ commit `0fbb320`
> **Verdict:** **🔴 RED — 6 confirmed bugs, 3 of them user-blocking**. The marathon's intent landed in code, but several wiring-level mistakes mean the tile is materially broken in the user's actual viewing context. Three are 1-3-line fixes; one is a CSS-cascade trap that affects every sortable header in the app; one is a Plotly-config violation that affects 9 sites globally.

---

## Executive Summary

The marathon work delivered five new pieces of functionality (period selector + state, Impact-by-period helper, "Active Exp" tooltip, removed columns, multi-line tooltip CSS). All five are present in the file. **The wiring around them is broken**:

| User complaint | Root cause | Severity | Fix size |
|---|---|---|---|
| "Header Impact selector isn't there" | `initImpactPeriodSelector()` is called only inside `initWeekSelector()` after the `_availDates.length<=1` early-return — silently dies on single-week data; also dies if `nWeeks=0` from `snap_attrib` | 🔴 blocking | 5-line move |
| "Hover that shows the data on Impact has been applied? I'm not sure what's happening" | Cell `title=` attr is set, but tooltip CSS (`.tip::after`) is class-based, not native. Native `title=` shows ~500ms native tooltip — easy to miss; also confusing because every other tooltip uses the styled `.tip` class | 🟡 partial | rewrap as `.tip` |
| "Translucent mostly empty box with a tiny triangle on sort" | CSS cascade collision: `.tip::after` (the giant tooltip) and `.sa::after` (the sort arrow) both target the same `::after` pseudo-element on a `<th class="tip">` — `.sa::after` overrides only `content`, leaving `.tip::after` background/padding/box-shadow rendering as a **floating empty card with just `▲` inside** | 🔴 blocking, ALL sortable headers app-wide | 1-line CSS scope fix |
| "Cells appear chipped from the side" | Table is `width:100%` with `<colgroup>` widths that **sum to less than realistic content width** when factor names are long ("Momentum (Medium-Term)" = ~22 chars). With `white-space:nowrap` and `td{padding:7px 10px}`, columns expand past 100% of card. Body has `overflow-x:hidden` → right edge clipped. Most acute when card width < 520px (small viewport / config drawer open) | 🟡 user-visible | colgroup retune |
| "Plotly toolbar in oDrF that we removed everywhere" | `oDrF` calls `Plotly.newPlot(..., modalPlotCfg)` and `modalPlotCfg = {displayModeBar:true, ...}`. There are **9 `modalPlotCfg` call-sites** that all show a toolbar contradicting the user's stated preference | 🔴 blocking, app-wide | 1-line constant change |
| "'Latest' label is unclear" | The label "Latest" comes from `IMPACT_PERIOD_LABELS.latest='Latest'`. It does NOT carry a date. The cell `title=` carries the actual date range but it's fired by native browser tooltip (slow + ugly). User wants the date visible without a hover OR with the styled tooltip | 🟡 UX | 1-line label change |

Also found two **non-complaint** bugs while auditing:

| # | Issue | Severity |
|---|---|---|
| F7 | Column-picker's `FAC_COLS` still has `'exp'` and `'spark'` entries that don't match the new `data-col="exp_active"`. Result: the ⚙ Cols dropdown shows toggles for "Exposure" and "12wk" that **do nothing** — and there's no way to hide the new "Active Exp" column at all | 🟠 medium |
| F8 | `oDrF` "Factor Return & Impact" chart reads `histSlice.map(h=>h.ret)` from `cs.hist.fac[name]`, but the parser puts only `{d,e,bm,a}` in `cs.hist.fac` — `ret`/`imp` live on `cs.snap_attrib[name].hist[]`. Net result: the inner-modal Return/Impact chart **never appears** because `hasRetData` is always false | 🟠 architectural — feature silently dead |

History readiness assessment: `getImpactForPeriod` correctly indexes `cs.snap_attrib[name].hist[]` and the parser populates `d_start`, `d_end`, `imp`, `cimp`, `full_period_imp`. **The Impact-period machinery is multi-year-ready as soon as a 156-week file lands**. The only reason '1Y'/'6M'/'3M'/'1M' don't show up today is the `nWeeks>=min` filter in `initImpactPeriodSelector` — which is correct behaviour, just not what the user expected without explanation.

---

## Section A — Verify intended changes landed

### A1. "12wk" sparkline column removed
**Status:** ✅ landed. `rFacTable` (L1841-1910) renders 5 cells per row with `data-col` values `name`, `exp_active`, `te`, `ret`, `imp`. No `spark` column. No `mkSparkline` invocation in this function.

### A2. "Port Exp" column removed
**Status:** ✅ landed. No `port` data-col in the new `<thead>` or `facRow`. Aligns with commit message rationale (raw_fac diverges from Axioma's a-value).

### A3. Renamed main exposure column to "Active Exp" with explanatory tooltip
**Status:** ✅ landed at L1904. Tooltip text reads:
> ACTIVE exposure = portfolio − benchmark (in σ units). Positive = portfolio overweight; negative = underweight. Source: Axioma factor model (already orthogonalized). Absolute portfolio & benchmark exposures are not shipped in the current CSV format — to derive them you'd need the per-factor 'Variance' columns FactSet used to provide. Synthesis tile (B104) will derive approximate absolute exposures from per-security raw factor data.

**Caveat:** the new `data-col="exp_active"` does NOT match the old col-picker entry `id:'exp'` (see Finding F7).

### A4. Added "Impact (Latest)" column wired to `_impactPeriod` + `getImpactForPeriod`
**Status:** ✅ landed at L1907 (header) and L1891-1898 (cell). Header label is dynamic:
```
Impact <span style="opacity:0.6;font-weight:400">(${getImpactPeriodLabel()})</span>
```
which means it'll re-render as "Impact (1M)" / "Impact (Full Period)" etc. when the period selector changes — assuming `upd()` runs on selector change. **Confirmed: `setImpactPeriod` calls `upd()` on L532**, so re-render is wired.

`getImpactForPeriod` is at L536-565 and looks correct:
- `latest` → reads last hist entry's `imp` and date range
- `all` → uses `full_period_imp` if present, else sums all hist entries
- trailing N weeks → slices last N from hist, sums their `imp`
All three branches return `{v, note}` with note formatted as `Period: YYYYMMDD→YYYYMMDD`.

### A5. Added `#impactPeriodWrap` header element + `#impactPeriodSel` dropdown
**Status:** ⚠️ HTML landed at L362-365 but **JS init is gated incorrectly** (Finding F1).

The wrap element is rendered inline-styled `display:flex` and is **always visible** in the DOM. The `<select>` inside is empty until `initImpactPeriodSelector()` runs. The function at L870-889 IS correct on its own — but it's only called from one place (L867, inside `initWeekSelector`), AFTER an early-return on `_availDates.length<=1`. See Finding F1.

### A6. Each Impact `<td>` carries `title="Period: ..."`
**Status:** ✅ landed at L1898 — `title="${impData.note}"`. **But uses native browser tooltip**, not the styled `.tip` class — see Finding F2.

### A7. Tooltip CSS upgraded for natural multi-line wrapping
**Status:** ✅ CSS at L146-150. Confirmed: `width:max-content; min-width:180px; max-width:340px; word-break:normal; overflow-wrap:break-word; line-height:1.55; padding:10px 14px; box-shadow:0 8px 24px rgba(0,0,0,.45); transition-delay:.25s` — all present and reasonable.
**Side effect:** introduced Finding F3 (sort-arrow CSS collision).

---

## Section B — Findings (root-cause + fix)

### F1. **[immediate fix]** Period selector dies on single-week data and on missing `snap_attrib`

**File:** `dashboard_v7.html:L848-889`
**User complaint match:** "Header Impact selector isn't there"

**Root cause #1 — gated init:**
```js
function initWeekSelector(){
  ...
  _availDates=dates||[];
  if(_availDates.length<=1){wrap.style.display='none';return;}  // ← EARLY RETURN
  ...
  initImpactPeriodSelector();   // ← only reached when >1 week
}
```
On a single-week CSV upload, `initImpactPeriodSelector` never runs → the `<select>` stays empty → the `Impact ▾` chip in the header has nothing to click → user perceives it as "not there".

**Root cause #2 — empty-options trap:**
Even if `initImpactPeriodSelector` runs, when `nWeeks=0` (because `cs.snap_attrib` is absent or empty), `visible=opts.filter(o=>nWeeks>=o.min)` returns `[]`. Result: `<select>` has no `<option>` children and renders as a **tiny empty box with no visible label** — exactly what the user describes.

**Root cause #3 — silent label desync:**
Even with options, the `<option>` for the persisted `_impactPeriod` may not be present in the filtered list (e.g., user previously chose 'm6' but new file only has 4 weeks). `<select>` then displays the first available option but `_impactPeriod` retains 'm6' until something writes it.

**Fix (3 layers, all immediate):**

1. Move `initImpactPeriodSelector()` OUT of `initWeekSelector` and call it independently at the same call sites (`init()` L783, `go()` L833) AND from `upd()` so it stays in sync after period changes:
```js
function initWeekSelector(){
  ...
  if(_availDates.length<=1){wrap.style.display='none';return;}
  ...
  // remove the call to initImpactPeriodSelector() from here
}
// call separately from init() and go() — and from setImpactPeriod() so the selected option syncs after each pick
```

2. In `initImpactPeriodSelector`, ALWAYS render at least the 'latest' and 'all' options regardless of `nWeeks`. Hide the WRAP only if `cs.snap_attrib` is fully absent:
```js
function initImpactPeriodSelector(){
  const sel=$('impactPeriodSel'), wrap=$('impactPeriodWrap');
  if(!sel||!wrap)return;
  if(!cs||!cs.snap_attrib||!Object.keys(cs.snap_attrib).length){
    wrap.style.display='none';return;
  }
  wrap.style.display='flex';
  let nWeeks=0;
  Object.values(cs.snap_attrib).forEach(item=>{if(item&&item.hist)nWeeks=Math.max(nWeeks,item.hist.length);});
  const opts=[
    {key:'latest',label:'Latest week',min:1},
    {key:'m1',label:'1 month (4w)',min:4},
    {key:'m3',label:'3 months (13w)',min:13},
    {key:'m6',label:'6 months (26w)',min:26},
    {key:'y1',label:'1 year (52w)',min:52},
    {key:'all',label:'Full period',min:1},
  ];
  let visible=opts.filter(o=>nWeeks>=o.min);
  if(!visible.length)visible=[opts[0]];   // safety: always show 'Latest'
  // If the persisted choice isn't in visible, fall back to 'latest' and persist
  if(!visible.find(o=>o.key===_impactPeriod)){
    _impactPeriod='latest';
    try{localStorage.setItem('rr.impactPeriod','latest');}catch(e){}
  }
  sel.innerHTML=visible.map(o=>`<option value="${o.key}"${o.key===_impactPeriod?' selected':''}>${o.label}</option>`).join('');
}
```

3. After `setImpactPeriod` re-renders, call `initImpactPeriodSelector()` to keep the dropdown's selected value in sync (or simply set `sel.value=_impactPeriod` directly).

---

### F2. **[immediate fix]** Impact cell hover uses native `title=` attr instead of styled tooltip

**File:** `dashboard_v7.html:L1898`
**User complaint match:** "Hover that shows the data on Impact has been applied? I'm not sure what's happening"

**Root cause:**
```js
<td class="r" data-col="imp" data-sv="..." title="${impData.note}">${fp(impVal,2)}</td>
```
The `title=` attribute is the native HTML tooltip. It takes ~500ms to appear, has OS-default styling (gray pill, no theme), and is easy to miss. Every OTHER tooltip in the dashboard uses `class="tip" data-tip="..."` and the slick `.tip::after` styled box (recently upgraded for multi-line). Net: this single cell type stands alone with a worse tooltip.

**Fix (single-line change):**
```js
<td class="r tip" data-col="imp" data-sv="${impVal??''}" data-tip="${impData.note.replace(/"/g,'&quot;')}" style="${impVal!=null?(impVal>0?'color:var(--pos)':'color:var(--neg)'):''}">${fp(impVal,2)}</td>
```
Drop `title=`, add `class="r tip"` + `data-tip="..."`. Now the per-cell hover gets the same multi-line styled tooltip as everything else.

**Caveat:** the dotted-underline that `.tip` adds to text might look weird on a numeric `<td>`. Consider a `.tip-cell` variant in CSS that drops the `border-bottom: 1px dotted var(--grid)` rule:
```css
td.tip-cell{position:relative;cursor:help}  /* no underline on table cells */
td.tip-cell::after{...same as .tip::after...}
```
Apply `class="r tip-cell"` instead. That way data cells get the styled tooltip without the unwanted underline noise.

---

### F3. **[immediate fix]** "Translucent box with tiny triangle" on sorted columns — CSS cascade collision

**File:** `dashboard_v7.html:L146-150` (tip CSS) and `L191-193` (sort-indicator CSS)
**User complaint match:** "Sorting any column there's a weird translucent mostly empty box above the tile that has only a tiny triangle arrow"

**Root cause:**
Every sortable `<th>` in the factor table also has `class="tip"`. After the user clicks a header, `sortTbl` adds `.sa` or `.sd` to the `<th>` (L1504). The CSS:

```css
.tip::after{
  content:attr(data-tip);
  position:absolute; bottom:calc(100% + 8px); left:50%; transform:translateX(-50%);
  background:#0f1623; padding:10px 14px; border-radius:8px;
  width:max-content; min-width:180px; max-width:340px;
  opacity:0; transition:opacity .15s; box-shadow:0 8px 24px rgba(0,0,0,.45);
  ...
}
.tip:hover::after{opacity:1; transition-delay:.25s}

th.sa::after{content:' ▲'; font-size:9px; opacity:0.7}
```

Both rules target the **same `::after` pseudo-element** when a `<th>` has BOTH classes. Specificity is equal (one class each), so cascade order wins: the LATER rule (`th.sa::after`) overrides only `content` and `font-size`, **but it doesn't override `position`, `padding`, `min-width`, `max-width`, `background`, `box-shadow`, or `opacity:0`**.

**Result:** the rendered `::after` is the giant tooltip box (180×~50px, `position:absolute`, dark `#0f1623` background, padded, shadowed) — but with `content:' ▲'` instead of the long tooltip text. The opacity stays at `0` (from `.tip::after`) so it's invisible — UNTIL the user hovers, which triggers `.tip:hover::after{opacity:1}`. **The "translucent mostly empty box with a tiny triangle" IS the tooltip card with just a `▲` for content.**

This affects **every sortable header in the entire app that also has `class="tip"`** — that's most of them.

**Fix (1-line CSS — narrows tip styles to non-sort state):**

Either Option A (preferred — narrow `.tip` selector):
```css
.tip:not(.sa):not(.sd)::after{ ... existing tip styles ... }
.tip:not(.sa):not(.sd):hover::after{opacity:1; transition-delay:.25s}
```

Or Option B (use a separate pseudo-element for the arrow):
```css
th.sa::before{content:' ▲'; font-size:9px; opacity:0.7; position:relative; margin-left:4px; left:auto; transform:none; background:none; padding:0; box-shadow:none; border:none}
th.sd::before{content:' ▼'; ... same overrides ...}
```
But Option B may collide with `.tip::before` (the arrow indicator at L149).

**Recommended: Option A** — minimal change, easy to reason about, fully preserves existing tip behaviour for non-sorted state.

Alternative quick patch (most local):
```css
th.sa::after, th.sd::after{
  position:static; background:none; padding:0; box-shadow:none;
  border:none; min-width:0; max-width:none; width:auto;
  opacity:0.7; transition:none;
}
th.sa::after{content:' ▲'; font-size:9px}
th.sd::after{content:' ▼'; font-size:9px}
```
This explicitly resets every tooltip property the sort indicator inherits from `.tip::after`.

---

### F4. **[immediate fix]** Cells appear "chipped" — table overflows half-width card on small viewports / long factor names

**File:** `dashboard_v7.html:L1910` (colgroup) + `L77-78` (`th/td{white-space:nowrap}`)
**User complaint match:** "Some of the cells appear chipped from the side"

**Root cause:**
- Table is in `cardFacDetail`, which lives in a `grid g2` (50% column).
- On a 1440-wide viewport: card inner width ≈ 656px. On a 1280-wide viewport: ≈ 588px. On a 1024-wide viewport: ≈ 456px.
- Colgroup widths: `min-width:140 + 100 + 60 + 70 + 100 = 470px` minimum.
- `th{white-space:nowrap}` and `td{white-space:nowrap}` force columns to grow if content > col width.
- "Momentum (Medium-Term)" at 12px font ≈ 165-175px — pushes Factor col past 140 to ~175.
- "Impact (Latest)" header in caps + sort arrow + tip underline ≈ 110-120px — pushes Impact col past 100.
- Realistic total: ~525-550px.
- On 1280-viewport: 525 > 588? No, fits. On 1024-viewport: 525 > 456 → **overflows by ~70px**.
- `body{overflow-x:hidden}` (L31) clips the right edge → "chipped from the side".

The "chip" effect is most visible on **long factor names overflowing left edge of next column** OR on the **right edge of the Impact column getting clipped** at the card border.

**Secondary cause — sticky thead clipping:**
`thead th{position:sticky; top:0; z-index:1}` (L195). When the table scrolls inside its parent, the sticky thead can paint over neighbouring cells if the parent has any overflow. Check `cardFacDetail` parent has no `overflow:hidden` (it has `overflow:visible` from `.card`), so this is probably fine — but worth flagging as a related vector.

**Fix (combined — 2 changes):**

1. Adjust colgroup so total min-width fits half a 1024-viewport (~440px usable):
```html
<colgroup>
  <col style="min-width:130px">  <!-- Factor: 130 (was 140) -->
  <col style="width:80px">       <!-- Active Exp: 80 (was 100) -->
  <col style="width:55px">       <!-- TE%: 55 (was 60) -->
  <col style="width:65px">       <!-- Return: 65 (was 70) -->
  <col style="width:90px">       <!-- Impact (Latest): 90 (was 100) -->
</colgroup>
```
Total: 420px min — fits 1024 viewports comfortably.

2. Truncate long factor names in the first column with `text-overflow:ellipsis`:
```html
<td data-col="name" style="max-width:160px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap" title="${f.n}">...</td>
```
Add `title="${f.n}"` so the full name stays accessible on hover.

3. (Optional) Wrap the table in a horizontal-scroll container as a last-resort safety net:
```html
<div style="overflow-x:auto"><table id="tbl-fac">...</table></div>
```
But truncation is preferable to scrolling for a small table — scroll feels broken in a card.

---

### F5. **[immediate fix]** `oDrF` factor drill modal shows Plotly toolbar — violates "no toolbar anywhere" rule

**File:** `dashboard_v7.html:L2431` (constant) and 9 call sites
**User complaint match:** "The factor drill (oDrF modal) has a Plotly toolbar that we previously decided to remove from everywhere"

**Root cause:**
```js
const plotCfg={displayModeBar:false, responsive:true};                 // OK
const modalPlotCfg={displayModeBar:true, responsive:true, scrollZoom:true};  // ← BUG
```

`oDrF` calls `Plotly.newPlot('facDrillHistDiv', ..., modalPlotCfg)` at L4527 and again at L4536. Both render with the Plotly modebar in the upper-right.

**Other callers of `modalPlotCfg`** (all show toolbars and presumably should NOT):
- L2249 — `attribDrillBars`
- L3778 — `riskFacHistDiv`
- L3784 — `riskFacRetDiv`
- L4445/4448 — `drillHistDiv` (sector/region/country drill)
- L4527 — `facDrillHistDiv`
- L4536 — `facDrillRetDiv`
- L5597 — `metricChartDiv`
- L5673 — (one more chart in oDrMetric)

**Fix (1-line — applies app-wide):**
```js
const modalPlotCfg={displayModeBar:false, responsive:true, scrollZoom:true};
```

**Caveat:** if any of those 9 charts WAS intentionally meant to keep the toolbar (for export/zoom UX in a deeper drill), this constant change removes it everywhere. Spot-check before flipping. **Recommendation:** flip the constant; if scrollZoom alone is insufficient for some charts, add `responsive:true, scrollZoom:true, displayModeBar:false` per-call where deeper UX is needed and re-introduce a toolbar narrowly.

---

### F6. **[immediate fix]** "Latest" label is opaque — user doesn't know what date range it covers

**File:** `dashboard_v7.html:L525`, `L1907`
**User complaint match:** "'Latest' label is unclear — what date range does it actually mean?"

**Root cause:**
```js
const IMPACT_PERIOD_LABELS={latest:'Latest', m1:'1M', m3:'3M', m6:'6M', y1:'1Y', all:'Full Period'};
```

The header shows "Impact (Latest)" with no date. The user has to hover an individual cell to see the actual `Period: 20260403→20260408` from the cell `title=`. That's two information layers when one would do.

**Fix (label inlines the actual latest week date):**

Option A — show the latest period's end date in the header:
```js
function getImpactPeriodLabel(){
  if(_impactPeriod==='latest'&&cs&&cs.snap_attrib){
    const sa=Object.values(cs.snap_attrib)[0];
    const last=sa&&sa.hist&&sa.hist[sa.hist.length-1];
    if(last&&last.d_end){
      const dt=parseDate(last.d_end);
      if(dt)return'Latest · '+dt.toLocaleDateString('en-US',{month:'short',day:'numeric'});
    }
  }
  return IMPACT_PERIOD_LABELS[_impactPeriod]||'Latest';
}
```

Option B — also expose the global selected period date in a small hint below the dropdown in the header.

Option C (cheapest) — just rename the label "Latest" → "Latest week" and rely on the cell `title` for the date, but **fix F2 first** so the cell hover is the styled tooltip.

**Recommended: Option A** for the cardFacDetail header label + F2 fix for cell hover. User gets one always-visible date AND a precise per-cell range on hover.

---

### F7. **[immediate fix]** Column-picker desync — toggles for ghost columns + new "Active Exp" column has NO toggle

**File:** `dashboard_v7.html:L1772-1788`

**Root cause:**
```js
const FAC_COLS=[
  {id:'name',label:'Factor'},{id:'exp',label:'Exposure'},{id:'te',label:'TE%'},
  {id:'spark',label:'12wk'},{id:'ret',label:'Return'},{id:'imp',label:'Impact'}
];
```
But `rFacTable` writes data-cols `name`, `exp_active`, `te`, `ret`, `imp`. So:
- Toggle "Exposure" controls `[data-col="exp"]` — **no such element exists** → toggle does nothing.
- Toggle "12wk" controls `[data-col="spark"]` — **no such element exists** → toggle does nothing.
- New "Active Exp" column with `data-col="exp_active"` — **no toggle wires to it** → cannot be hidden.

**Fix:**
```js
const FAC_COLS=[
  {id:'name',label:'Factor'},
  {id:'exp_active',label:'Active Exp'},
  {id:'te',label:'TE%'},
  {id:'ret',label:'Return'},
  {id:'imp',label:'Impact'}
];
```
Drop `'exp'` and `'spark'`. Rename to match the new data-col. Side effect: if any user previously persisted `_facColVis.exp=false` to localStorage, that key is now orphaned but harmless (the loader at L1780 only adopts keys that exist in the current `FAC_COLS`).

---

### F8. **[architecture]** `oDrF`'s "Factor Return & Impact" sub-chart silently never renders

**File:** `dashboard_v7.html:L4457` (data source) + L4472 (presence check) + L4530-4537 (render)

**Root cause:**
```js
let hist=cs.hist.fac[name]||[];        // ← {d, e, bm, a} only — NO ret/imp
let hasRetData=histSlice.some(h=>h.ret!=null||h.imp!=null);  // ← always false
let retChartHtml=hasRetData?`<div class="card-title">Factor Return & Impact</div><div id="facDrillRetDiv" style="height:160px"></div>`:'';
```

The parser puts factor-exposure history in `cs.hist.fac` and factor-attribution history in `cs.snap_attrib[name].hist[]`. They are different structures. The drill modal mixes them up: it reads exposure history but expects return/impact fields that only live in `snap_attrib`.

**Net result:** `hasRetData` is always `false` → `retChartHtml` is always empty → the second chart inside `oDrF` **never renders**, regardless of how rich the data is. User never sees this functionality even when fully populated multi-year data is loaded. **It's a silent dead feature.**

**Fix (architecture-level):**

Restructure `oDrF` to use `snap_attrib` for the time series:
```js
let snapHist=(cs.snap_attrib&&cs.snap_attrib[name]&&cs.snap_attrib[name].hist)||[];
let expHist=cs.hist.fac[name]||[];
// Build a unified series keyed by date:
let dateMap=new Map();
expHist.forEach(h=>dateMap.set(h.d,{...dateMap.get(h.d),d:h.d,e:h.e,bm:h.bm,a:h.a}));
snapHist.forEach(h=>dateMap.set(h.d,{...dateMap.get(h.d),d:h.d,ret:h.ret,imp:h.imp,cimp:h.cimp,d_start:h.d_start,d_end:h.d_end}));
let hist=[...dateMap.values()].sort((a,b)=>parseDate(a.d)-parseDate(b.d));
```
Then `hasRetData` becomes:
```js
let hasRetData=hist.some(h=>h.ret!=null||h.imp!=null);
```
which will be `true` whenever `snap_attrib` is populated.

This is a non-trivial refactor — flag for the dedicated B111 ("oDrF rebuild") backlog item if not in scope for the immediate fix pass.

---

### F9. **[backlog]** `cardAttribWaterfall` ignores the global `_impactPeriod` selector

**File:** `dashboard_v7.html:L1450-1483`

**Status:** comment at L361 lists `cardAttribWaterfall` as one of the targets of the period selector, but `rFacWaterfall` reads `f.imp` directly (latest only) at L1452 and L1456.

**Fix (when this tile is in marathon focus):**
```js
let facs=(s.factors||[]).map(f=>{
  let impData=getImpactForPeriod(f.n,_impactPeriod);
  return {...f, imp:impData.v};
}).filter(f=>isFinite(f.imp)).sort((a,b)=>(b.imp||0)-(a.imp||0));
```

Defer to backlog (B109 follow-up) — not part of cardFacDetail scope.

---

### F10. **[backlog]** `cardAttrib` rolling Impact rows + `oDrF` Impact stat tile also bypass period selector

**File:** L2128 (cardAttrib) + L4490 (oDrF stat card use `factor.imp` directly)

**Status:** same root cause as F9 — they read `f.imp` (latest) instead of going through `getImpactForPeriod`. Apply same pattern when those tiles come up in the marathon, or batch-sweep with F9.

---

## Section C — Column clipping deep-dive

Confirmed root cause analyzed in F4. Width math:

| Col | colgroup | Likely actual (long content) | th text |
|---|---|---|---|
| Factor | `min-width:140` | 175 (Momentum (Medium-Term) at 12px) | `Factor` (49px) |
| Active Exp | `width:100` | 110-115 (header dominates: "ACTIVE EXP" + ▲ + dotted) | `Active Exp` |
| TE% | `width:60` | 55 OK | `TE%` |
| Return | `width:70` | 65 OK | `Return` |
| Impact (Latest) | `width:100` | 115-125 ("IMPACT (LATEST)" 15ch × ~7px + arrow) | `Impact (Latest)` |

Total likely actual ≈ 525-550px.

| Viewport | Card inner width | Fits? |
|---|---|---|
| 1920 | 920 | ✅ |
| 1440 | 656 | ✅ (with margin) |
| 1280 | 588 | ✅ (tight) |
| 1100 | 488 | ⚠️ (40-60px overflow) |
| 1024 | 456 | ❌ (~80px overflow → "chipped") |

User very likely browsing at 1100-1280 with config drawer or sidebar reducing effective width. Fix per F4.

---

## Section D — `oDrF` modal Plotly + history readiness

Confirmed in F5 and F8. Two distinct issues in the same function:
- F5 (toolbar) — flip `modalPlotCfg`, applies app-wide.
- F8 (return/impact chart silently dead) — refactor data source to merge `cs.hist.fac` + `cs.snap_attrib[name].hist`.

The exposure time-series (the FIRST chart) at L4527 reads `cs.hist.fac[name]` and computes `expVals = histSlice.map(h => h.bm!=null ? +(h.e-h.bm).toFixed(4) : h.e)`. **This IS history-ready** — when a 156-week file lands, this chart will populate fully. The `expSd`/avg shading + range slider are all good.

The SECOND chart (return/impact) is NOT history-ready as currently wired (F8) — it would silently stay empty even with full data.

---

## Section E — History readiness verification

| Component | Reads from | Multi-year ready? |
|---|---|---|
| `getImpactForPeriod(latest)` | `snap_attrib[name].hist[last]` | ✅ |
| `getImpactForPeriod(all)` | `snap_attrib[name].full_period_imp` (parser-derived from summary row) OR sum of `hist[]` | ✅ |
| `getImpactForPeriod(m1/m3/m6/y1)` | `snap_attrib[name].hist[].slice(-N)` | ✅ |
| `initImpactPeriodSelector` filter | `Object.values(cs.snap_attrib).map(item=>item.hist.length).max()` | ✅ |
| `oDrF` exposure chart | `cs.hist.fac[name]` | ✅ |
| `oDrF` return/impact chart | (currently) `cs.hist.fac[name]` | ❌ — needs F8 fix to use `snap_attrib` |
| `cardAttribWaterfall` | `f.imp` (latest only) | ❌ — F9 |
| `cardAttrib` rolling rows | `i.full_period_imp` | ⚠️ partially — only respects 'all' period, not custom slices |

---

## Section F — Verification checklist (post-fix targets)

- [ ] Open dashboard with a 1-week JSON: Impact selector renders with 'Latest week' AND 'Full period' options, defaults to 'Latest', dropdown is visible
- [ ] Open dashboard with 3-week JSON: 'Latest' and 'Full period' show, others filtered
- [ ] Open dashboard with 156-week JSON: all 6 options show
- [ ] Switch period: header text re-renders ("Impact (1Y)" etc.), every Impact column in cardFacDetail / cardAttrib / cardAttribWaterfall updates synchronously
- [ ] Hover an Impact cell: styled multi-line tooltip shows "Period: YYYYMMDD→YYYYMMDD"
- [ ] Sort cardFacDetail by any column: only a small triangle ▲/▼ next to the header text — NO floating translucent box
- [ ] Resize viewport down to 1024: no cells clipped at right edge of cardFacDetail
- [ ] Click any factor row → drill opens; NO Plotly toolbar in the upper-right of either inner chart
- [ ] When data is full, the "Factor Return & Impact" chart inside oDrF actually renders (post F8)
- [ ] Column picker: only 5 toggles (Active Exp, TE%, Return, Impact); each toggle hides/shows the right column

---

## Section G — Fix queue (for coordinator)

### Immediate (apply this turn — single session)
1. **F1** — move/widen `initImpactPeriodSelector`, harden empty-options branch (~10 lines)
2. **F2** — switch Impact cell hover from `title=` to styled `.tip-cell` class (~3 lines + 4-line CSS)
3. **F3** — scope `.tip::after` to `:not(.sa):not(.sd)` OR explicitly reset sort `::after` properties (~3 lines CSS)
4. **F4** — retune colgroup widths + ellipsis on Factor name (~5 lines)
5. **F5** — flip `modalPlotCfg.displayModeBar` to `false` (1 line — affects app-wide, intentional)
6. **F6** — append latest week date to "Latest" label (~6 lines)
7. **F7** — sync `FAC_COLS` to new `data-col` set (~3 lines)

Total: ~30 lines of code changes, all in `dashboard_v7.html`. Single commit.

### Architecture (needs design decision before applying)
8. **F8** — `oDrF` return/impact chart data source refactor (~15-20 lines + risk of touching adjacent logic)

### Backlog (defer)
9. **F9** — `cardAttribWaterfall` global period adoption — apply during cardAttribWaterfall marathon visit
10. **F10** — `cardAttrib` Impact rows + `oDrF` Impact stat — apply during cardAttrib marathon visit / B111 oDrF rebuild

---

## Section H — Commit message draft for the immediate fix bundle

```
fix(B109+marathon): cardFacDetail re-audit fixes — period selector visibility, sort indicator, tooltip wiring, colgroup, Plotly toolbar

User-reported regressions during 2026-04-27 review of commit 0fbb320:
1. F1: period selector dropped on single-week data — initImpactPeriodSelector now
   called independently of initWeekSelector + hardened empty-options branch.
2. F2: Impact cell hover now uses styled .tip-cell tooltip (was native title=).
3. F3: sort indicator no longer renders the .tip::after tooltip card —
   .tip::after scoped to :not(.sa):not(.sd). Affects every sortable header in
   the app.
4. F4: cardFacDetail colgroup retuned (470→420 min); long factor names truncate
   with ellipsis + title.
5. F5: modalPlotCfg.displayModeBar flipped to false. Removes Plotly toolbar
   from all 9 modal call-sites (oDrF, oDrMetric, riskFacHist, etc.) — matches
   user's stated "no toolbar anywhere" preference.
6. F6: "Latest" header label now reads "Latest · MMM D" using the actual end
   date from snap_attrib.hist[last].d_end.
7. F7: FAC_COLS aligned to new schema — drops ghost 'exp'/'spark' toggles,
   adds 'exp_active' so Active Exp column can be hidden.

Deferred to follow-ups:
- F8: oDrF return/impact chart data-source refactor (architecture).
- F9: cardAttribWaterfall global period adoption.
- F10: cardAttrib + oDrF Impact stat global period adoption.

Safety tag: working.20260427.<HHMM>.pre-cardFacDetail-reaudit
```

---

## Section I — Color status

| Section | Status |
|---|---|
| Section 1 (Data accuracy / source) | 🟢 GREEN — `getImpactForPeriod` is correct, `snap_attrib` schema confirmed against parser |
| Section 4 (Functionality) | 🔴 RED — period selector dies on common cases, col-picker desynced, drill chart silently dead |
| Section 6 (Design) | 🔴 RED — sort indicator broken visually, cells clip on small viewports, Plotly toolbar present where it shouldn't be |

---

## Notes for next session

- The marathon protocol is working — this re-audit caught all 6 user complaints + 2 latent bugs in one pass via structured diff.
- F3 (sort-indicator tooltip-collision) is a TRAP that has been latent in the codebase since `.tip` and `.sa` first coexisted on the same element. The recent tooltip CSS upgrade (commit `0fbb320`) made it visually obvious because the tooltip box got bigger/denser. Fix this once, app-wide benefit.
- F5 (Plotly toolbar) similarly is a global lever — flipping `modalPlotCfg` removes the toolbar from 9 sites at once. Worth a brief sanity-check that none of those 9 actually NEED the toolbar.
- Recommend running an analogous re-audit against `cardAttrib` and `cardAttribWaterfall` once they get marathon focus, since they share the period-selector wiring.

---

> **Auditor signature:** Tile Audit Specialist, 2026-04-27
> **Output for coordinator:** apply F1-F7 in a single commit, F8 in a follow-up architecture pass, F9-F10 to backlog with B-IDs.
