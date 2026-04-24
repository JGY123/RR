# SurpriseEdge Design Study — 2026-04-24

**Reference file:** `~/Downloads/surpriseedge_report_65080rows_2026-02-17.html` (21 MB, single-file HTML dashboard; 65,080 securities analyzed)
**Why this file:** user flagged it as "very clean and sharp — take whatever you can learn to get RR to look super amazing."

This doc catalogs the **15 adoptable design patterns** extracted from SurpriseEdge's CSS, layout, and rendering code, ranked by impact × risk. Code snippets are ready to paste.

---

## Tier A — Global polish (low risk, high payoff, ship as one commit)

### A1. Deeper dark palette — 5-tone gray ramp + cyan accent

```css
/* Replace the RR palette tokens (currently --bg, --surf, --grid, --txt, --txth, --pri, --pos, --neg) with a tighter ramp */
--bg:           #0b0e14;   /* body — noticeably deeper than RR's current */
--surf:         #12161f;   /* card body */
--grid:         #1e2433;   /* borders, dividers, scrollbar thumb */
--txt:          #c8cdd8;   /* body copy */
--txth:         #e2e8f0;   /* headings/emphasis */
--dim:          #5a6178;   /* muted, captions, labels */
--pri:          #22d3ee;   /* accent — fresh cyan, NOT indigo */
--pos:          #10b981;   /* green (same) */
--neg:          #ef4444;   /* red (same) */
--warn:         #f59e0b;   /* amber (same) */
```

**Impact:** SurpriseEdge reads as "enterprise fintech" — RR currently reads as "consumer dark mode". Deeper `#0b0e14` body + cooler accents flips the register. The cyan accent (`#22d3ee`) is especially distinctive — indigo (`#6366f1`, RR's current `--pri`) is everywhere; cyan is rare and feels sharp.

**Migration:** token swap only — no component changes needed. Every tile that uses `var(--pri)` etc. inherits automatically. Visual regression on the 24 audited tiles would be zero-structural, just a palette shift.

**Caveat:** if we swap `--pri` to cyan, the purple+pink tones in cardFRB, cardFacContribBars (`#a78bfa` etc.) may clash. Recommend keeping `--pri-alt` as a purple fallback OR migrating palette holistically.

---

### A2. Custom scrollbars — immediate polish, 4 lines

```css
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--grid);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--dim)}
```

**Impact:** Default Chrome/Safari scrollbars are chunky (17px) and clash with any dark theme. 6px themed thumbs read as designed. Applied globally — every table, every overflow panel inherits.

**Migration:** drop into the existing `<style>` block at the top of dashboard_v7.html. Zero functional change.

---

### A3. Monospace numeric cells — uniform decimal alignment

```css
.mono { font-family: 'SF Mono', Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }
```

Then: every `<td>` that holds a number gets `class="r mono"` (right-align + mono). SurpriseEdge applies it to every numeric cell across every table.

**Impact:** Decimal points line up perfectly across rows. `24.6%` / `-4.7%` / `15.2%` column looks like a data grid, not a sentence. Huge professionalism gain on tables like cardSectors, cardHoldings, cardCountry.

**Migration:** add `.mono` class, then sweep every `data-col` numeric cell in dashboard_v7.html (cardSectors, cardHoldings, cardCountry, cardGroups, cardRegions, cardRanks, cardWatchlist, cardBenchOnlySec, cardUnowned, cardRiskFacTbl, etc.). ~30-50 Edit operations. Safe — cosmetic only, pure CSS class addition.

**Alternative lower-effort:** add `td.r { font-family: monospace; }` to catch every right-aligned cell globally. One line; may catch non-numeric cells too (rare in RR).

---

### A4. Card-title typography tightening

SurpriseEdge:
```css
.card-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--txth);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

RR currently uses ~13px sentence-case for `.card-title`. The SurpriseEdge version feels tighter, more enterprise, more Bloomberg-terminal.

**Impact:** every card instantly reads as "dashboard panel" vs "web card". Uniform across 24 tiles.

**Migration:** swap the `.card-title` CSS rule in dashboard_v7.html. Test on 2-3 tiles first — uppercase can make long titles (like "Marginal Contribution to Risk (Top & Bottom)" on cardMCR) feel aggressive. If so, retain sentence case but keep the 11px size + letter-spacing.

**My lean:** 11px + letter-spacing 0.5px, but keep sentence case. Best of both.

---

### A5. Subtle row separators with hex-alpha

```css
/* SurpriseEdge uses this for every table row border: */
border-bottom: 1px solid #1e243315;   /* 15 hex = ~8% alpha — almost invisible but gives rhythm */

/* Equivalent in RR-token form: */
border-bottom: 1px solid color-mix(in srgb, var(--grid) 15%, transparent);
```

**Impact:** table rows separate without being "loud". Current RR table rows use `1px solid var(--grid)` at full alpha — reads heavier. SurpriseEdge's 8% alpha is more modern.

**Migration:** update the `table td` border rule in dashboard_v7.html's style block. Every table inherits.

---

### A6. Pill pattern with hex-alpha background

```css
.pill {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--grid);
  background: transparent;
  color: var(--dim);
}
.pill.active {
  border-color: var(--pri);
  background: color-mix(in srgb, var(--pri) 12%, transparent);
  color: var(--pri);
}
.pill.pos  { border-color: var(--pos);  background: color-mix(in srgb, var(--pos) 12%, transparent);  color: var(--pos); }
.pill.neg  { border-color: var(--neg);  background: color-mix(in srgb, var(--neg) 12%, transparent);  color: var(--neg); }
.pill.warn { border-color: var(--warn); background: color-mix(in srgb, var(--warn) 12%, transparent); color: var(--warn); }
```

**Impact:** uniform "chip" look across every toggle/filter/status pill. RR currently varies pill styling per tile (cardFacContribBars toggle vs cardTreemap dim picker vs cardRanks rank pills). One convention = one visual register.

**Migration:** refactor the 5-6 pill variants currently scattered through the CSS block into this single convention. Per-tile inline `style=` overrides can be removed. Medium touch; high payoff.

**Pre-existing good news:** cardFacContribBars (Batch 7) already uses `var(--riskFacMode, var(--pri))` for its mode-toggle — easy to migrate.

---

## Tier B — Targeted tile wins (moderate effort, specific tiles benefit)

### B1. Live result count in header — "I know what I'm looking at"

SurpriseEdge's header has:
```html
<span style="font-size:10px;color:var(--pri);font-weight:700;font-family:monospace">
  3247<span style="color:var(--dim);font-weight:400">/65080</span>
</span>
```

Shows count of filtered results / total, using the accent color for the live number. Updated on every filter change.

**Adopt for RR:** the top-header bar (currently has strategy selector + week selector + export). Add a filtered-holdings counter when any filter is active (e.g., cardHoldings has a rank-quintile filter applied → header shows `88/775` in cyan). Especially valuable on EM (1219 holdings) and GSC (3874 holdings).

**Where:** `rHeader()` / `rTopBar()` — find the existing header render in dashboard_v7.html.

---

### B2. Stat cards — big numbers, punchy

SurpriseEdge overview tab:
```html
<div class="card">
  <div class="card-title">Portfolio Beat Rate</div>
  <div style="font-size:26px;font-weight:800;color:var(--pos);font-family:monospace">78.1%</div>
  <div style="font-size:9px;color:var(--dim);margin-top:2px">234 / 300 portfolio</div>
</div>
```

**26px monospace 800** for the hero number, with a 9px muted caption underneath giving denominator/context.

**Adopt for RR:** cardThisWeek's TE/AS/Beta/Holdings hero row could use this treatment. Currently 18-22px Inter — upgrade to 26px mono + tiny caption with period-over-period delta reference. Much more "terminal dashboard" feel.

---

### B3. Side-panel detail view (alternative to modal for stock drill)

```css
.detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 360px;
  height: 100vh;
  background: var(--surf);
  border-left: 2px solid var(--pri);
  z-index: 100;
  overflow-y: auto;
  padding: 20px;
  box-shadow: -4px 0 20px rgba(0,0,0,0.5);
}
```

**Compared to RR's modal-overlay** for `oSt(ticker)`: SurpriseEdge's side-panel leaves the main table visible, so user can compare row-by-row without modal flicker. Click another row → panel updates, no close+reopen.

**Adopt for RR:** this is a bigger UX decision. **Recommend deferring to Tier 2 build phase** (B103 per-security raw factor drill would be a natural place to try it). Don't touch modal pattern before marathon.

---

### B4. Filter bar with thin vertical separators

```html
<div style="display:flex;gap:4px;flex-wrap:wrap;align-items:center">
  <span style="font-size:9px;color:var(--dim);font-weight:600">SCOPE</span>
  <button class="pill active">All</button>
  <button class="pill">Portfolio</button>
  <span style="width:1px;height:16px;background:var(--grid);margin:0 4px"></span>
  <span style="font-size:9px;color:var(--dim);font-weight:600">BIM</span>
  <button class="pill">Beat</button>
  <!-- ... -->
</div>
```

Groups of pills separated by thin 1px vertical rules, each group labeled with a 9px uppercase label in dim color. Very readable, very compact.

**Adopt for RR:** ideal for B102 `cardRiskByDim` when built (dimension toggle + threshold slider + reset). Also a candidate retrofit for cardFacContribBars' toolbar (currently has group pills + checkboxes + slider in one row without visual grouping).

---

### B5. Reset-filter pill (conditional visibility)

```js
if (anyFilterActive) {
  html += '<button class="pill" style="background:color-mix(in srgb, var(--neg) 13%, transparent);color:var(--neg);border-color:color-mix(in srgb, var(--neg) 38%, transparent)" data-reset="1">✕ Reset</button>';
}
```

Only appears when a filter is active. Clicking it clears all filters. Clean.

**Adopt for RR:** any tile with multiple filter dimensions (cardFacContribBars group-pill + threshold + checkboxes). User currently has to click each filter to clear — one-click reset is a real QoL win.

---

## Tier C — Heavy lift (don't do without explicit ask)

### C1. Custom SVG charts instead of Plotly for small tiles
SurpriseEdge writes inline SVG for bar/line charts (60 LOC each). No Plotly dependency. For tiles where Plotly is overkill (cardChars metric bars, cardRanks quintile distribution, cardBenchOnlySec rows), inline SVG would cut weight + render instantly. But: loses Plotly's built-in interactivity (hover tooltips, zoom, CSV export). **Don't adopt unless we hit a real performance ceiling.**

### C2. Full layout refactor to `grid-template-columns: repeat(4, 1fr)` with span
SurpriseEdge's overview tab uses a clean 4-column grid with `grid-column: span N` per card. RR's Overview tab is mostly `grid g2` / `grid g3` — functional but rigid. Refactoring to a 4-col base with spans would give more layout flexibility but touches every card wrapper. Big diff. **Defer.**

### C3. Tab-based navigation within Risk tab
SurpriseEdge's 4-tab structure (Overview / Analytics / Returns / Detail) works because their data is simpler. RR's tabs are by domain (Overview / Sectors / Regions / Factors / Risk) — correct for the data model. **Don't refactor.**

---

## Adoption priority ladder

### **Stage 1 — Pre-marathon (optional, 30 min, zero risk)**
- A2 custom scrollbars (4 lines CSS)
- A5 subtle row separators (1 line CSS)
- A3 `.mono` helper class + apply to the 3-4 most prominent tables (cardHoldings, cardSectors, cardCountry)

If we do this, marathon reviews happen against the polished version. User sees a nicer dashboard while walking through tile signoffs. But risk: any per-tile visual change could trigger "wait that looks different than at audit time" confusion. **Only do Stage 1 if user explicitly asks.**

### **Stage 2 — Post-marathon design polish pass (1–2 hours)**
Apply A1–A6 as a single commit. Tag `design-polish-v1`. Run browser regression on all 24 tiles. Commit message references this doc.

### **Stage 3 — Tier 2 tile builds (B102/B103/B104) adopt polish from day 1**
All three new tiles use the new palette, pills, stat cards, filter-bar patterns, and — if the user likes it — the side-panel detail pattern for B103.

### **Stage 4 — Selective B-tier adoption**
B1 live count, B2 stat cards, B4/B5 filter bar patterns, applied per-tile based on where they most help.

---

## What to NOT copy

- **SurpriseEdge is view-only**; RR is interactive (note-hook right-click, drill modals, week selector, sort/filter persistence). Don't trade RR's richer interactivity for SurpriseEdge's cleaner read-only layout.
- **SurpriseEdge has no week-selector or historical state.** RR's `_selectedWeek` banner + multi-week `hist.summary` is a capability SurpriseEdge doesn't have.
- **SurpriseEdge shows data density via pagination** (`PER_PAGE=50`). RR shows density via Top-N + full-list drill. RR's approach is better for the "review every position" workflow.

---

## Where this doc lives

- `design/SURPRISEEDGE_LESSONS.md` (this file, committed to repo).
- `SESSION_STATE.md` "Next up" — add pointer after marathon.
- `BACKLOG.md` — register **B105 · Design polish pass — SurpriseEdge palette + typography adoption** as the tracker for Stage 2.

---

**Summary:** SurpriseEdge is not a revolution — it's six small disciplined choices (palette depth, custom scrollbars, mono numerics, card-title letterspacing, subtle row borders, hex-alpha pills) that compound into "professional" vs "web". All adoptable in one afternoon. The user's instinct is right — RR can look super amazing with surgical work, no rewrite required.
