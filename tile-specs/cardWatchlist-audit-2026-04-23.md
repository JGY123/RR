# cardWatchlist — Audit (2026-04-23)

**Tile ID:** `cardWatchlist`
**Render fn:** `watchlistCardHtml(s)` — dashboard_v7.html L3683–L3713
**Mounted in:** `rExp()` Overview tab via `${watchlistCardHtml(s)}` L1140 (below what-changed banner, above Sector Weights)
**Auditor:** tile-audit subagent
**Batch:** 6 (cross-tile batch of Overview synthesis tiles)

---

## Verdict

| Track | Status | One-line |
|-------|--------|----------|
| T1 Data accuracy | **YELLOW** | Source is correct (`cs.hold[]` lookup by ticker via localStorage `rr_flags_<strategyId>`); but flagged ticker no longer held silently renders as 0.00% weight / 0.00 active — no visual "exited" state. |
| T2 Functionality parity | **RED** | No table id, no `<th>`, no `data-col`, no `data-sv`, no sort, no CSV export, no empty-state copy, no remove affordance in-tile, cycleFlag does not re-render watchlist. |
| T3 Design consistency | **YELLOW** | Hardcoded `#f59e0b/#ef4444/#10b981` in FLAG_COLORS (not `--warn/--neg/--pos`); section sub-headers OK; no header tooltip; width clamps (80/60/60px) fine but inline-styled, not class-driven. |

Three-word summary: **no sort, no CSV, color drift** — plus a subtle T1 "ghost holding" data risk.

---

## T1 — Data accuracy

### T1.1 [trivial] Ghost holding (flagged ticker no longer in `s.hold[]`)
**L3693–3694:**
```js
let h=holdMap[t]||{};
groups[f].push({t,f,n:h.n||t,p:+(h.p||0),a:+(h.a||0)});
```
If a user flagged `XYZ` last week and the PM exited, `holdMap[t]` is `undefined` and the row silently renders `p=0.00 / a=0.00`. Indistinguishable from an existing 0-weight position. No "exited" badge, no strike-through, no italic.

**Fix:** detect `!holdMap[t]` and render a muted row with badge `exited` and `—` placeholders instead of `0.00`. Example:
```js
let exited = !holdMap[t];
groups[f].push({t,f,n:h.n||t,p:exited?null:+(h.p||0),a:exited?null:+(h.a||0),exited});
```
Then in `mkRow`: `item.exited ? '—' : f2(item.p)`; add `<span style="color:var(--txt);font-size:9px">EXITED</span>` chip.

### T1.2 [trivial] Pattern A/B/C check: clean
- Pattern A (hist.X:{}): N/A — no sparkline / trend.
- Pattern B (parser → normalize-discarded): N/A — source is localStorage, not parser.
- Pattern C (render-side re-derivation): N/A — watchlist groups come from localStorage flag value (`watch`/`reduce`/`add`), not reconstructed.

### T1.3 [trivial] Cash flagged: silently included
No `isCash(h)` filter. If a user ever flags `USD` or `CASH`, it renders in Watch/Reduce/Add with whatever weight cash carries. Low-probability but worth a one-line guard matching cardHoldings' equity filter.

### T1.4 [PM gate] Cross-strategy leak-across / state scope
LocalStorage key is **per-strategy**: `rr_flags_<s.id>` (L3686). Switching IDM → ISC means a fresh flag set. This is intentional per-strategy scoping, but one could argue a ticker watched in IDM often deserves watching in a related mandate. **Leave as-is without explicit PM ask.** Flag for user to confirm.

---

## T2 — Functionality parity

### T2.1 [trivial] No stable `<table id>`
L3710: `<table style="width:100%...">` — three anonymous tables (one per section). Blocks `sortTbl()`, `exportCSV('#tbl-watchlist')`, screenshotCard targeting. Give each section-table a stable id: `tbl-watch-${g.key}`.

### T2.2 [trivial] No `<thead>` / column headers
No header row at all. User sees icon, ticker, name, port%, active%. Even the 4 numeric columns are unlabeled. Compare to cardHoldings top-N where column headers + tooltips are present.

**Fix:** add a tiny `<thead>` with `<th>Ticker</th><th>Name</th><th class="r">Port %</th><th class="r">Active %</th>` above each group's `<tbody>`, with `class="tip" data-tip="..."` per numeric col.

### T2.3 [trivial] No `data-col` / no `data-sv`
Every `<td>` is raw text / inline-styled. Prereq for future column picker and correct sort. Same class of gap as cardRegions' `type==='reg'` branch in the Primitives checklist.

### T2.4 [trivial] No sort wiring
No `onclick="sortTbl(...)"` anywhere. For a ≤N-row watchlist this is survivable, but every other tabular tile in the app supports click-to-sort. Expected: sort Port/Active columns at minimum.

### T2.5 [trivial] No CSV export
No `⬇` button. User cannot export their watchlist to paste into an email/Slack/spreadsheet. Single `exportCSV('#tbl-watch-*','watchlist-' + cs.id)` concatenating all three sections. **No PNG button** (per standing user preference).

### T2.6 [trivial] No empty-state fallback copy
L3684 and L3688 both early-return `''` (tile entirely hidden) when no ticker is flagged. Per Primitives checklist an empty-state should render a small placeholder: "No tickers watchlisted — click the ⚑ icon on any holding row to add."

This is arguably the **single biggest affordance gap**: a new user has no discovery path to the watchlist feature because the tile is invisible until populated. The flag button (`⚑` on Holdings rows) is the only entry point and has no on-boarding cue.

### T2.7 [trivial] cycleFlag does not re-render the watchlist
L3667–3681: `cycleFlag()` updates `_holdFlags`, saves to localStorage, and patches the single `.flag-btn` element that was clicked. It does **not** re-render `cardWatchlist`. If the user flags a 6th ticker while the Overview tab is visible, the new row never appears until next `upd()` cycle (strategy switch, week change, etc.).

**Fix:** after `saveHoldFlags()`, if Overview tab is active, locate `#cardWatchlist`, replace its outerHTML with `watchlistCardHtml(cs)` — or, more robustly, re-render a scoped region. Current `setTimeout(refreshCardNoteBadges,200)` on `upd()` doesn't help here.

### T2.8 [trivial] No remove affordance in-tile
To remove a ticker from the watchlist, user must leave Overview → go to Holdings → find the row → click `⚑` 3 times to cycle back to unflagged. Add a small `×` button on hover for each row that calls `delete _holdFlags[item.t]; saveHoldFlags(); re-render`.

### T2.9 [trivial] `oSt('${item.t}')` drill parity: OK
L3700 uses same `oSt(ticker)` drill as Holdings table L3999 — consistent. Exited-ticker rows (T1.1) will `oSt()` into a missing holding, though, and `oSt()` early-returns silently on `!h` (L4360). Confirm: clicking an exited row appears to do nothing — a minor UX dead-end.

### T2.10 [trivial] No right-click note popup on card-title
Card has `id="cardWatchlist"`, so `refreshCardNoteBadges` L3645–3657 auto-adds a note badge IF a note exists. But there is no `oncontextmenu="showNotePopup(event,'cardWatchlist');return false"` on the `.card-title` (L3712) to create a new note in the first place. User can never right-click to open the note-popup on this tile — can only discover notes via the Settings panel's note list.

Same pattern missing across most synthesis tiles (cardThisWeek, what-changed banner, riskAlerts). Worth a cross-tile sweep: ensure every `card-title` that has `id` accepts right-click → `showNotePopup`.

### T2.11 [trivial] Persistence across strategy switches
Strategy switch → `upd()` L838 → `_holdFlags=loadHoldFlags()` L839 → re-reads correct per-strategy flags → `rExp()` re-renders Overview → `watchlistCardHtml(s)` reads `rr_flags_${s.id}`. **Works as designed.** Per-strategy isolation confirmed.

### T2.12 [PM gate] Merge Watch/Reduce/Add into unified sortable table?
Current layout = three sections. Alternative = single table with a "Flag" column (⚑ ▼ ▲ icons) sortable/filterable. Denser, fits more tickers on-screen. Current grouping prioritizes narrative scanning. **PM call.**

---

## T3 — Design consistency

### T3.1 [trivial] Hardcoded FLAG_COLORS
L3666: `{watch:'#f59e0b',reduce:'#ef4444',add:'#10b981'}` — should be:
```js
const FLAG_COLORS={watch:'var(--warn)',reduce:'var(--neg)',add:'var(--pos)'};
```
Currently theme-aware because FLAG_COLORS is only used inline-styled; does NOT respond to light-mode token overrides. Aligns with the standing pattern from cardRiskHistTrends fixes (tokenize hex).

### T3.2 [trivial] Section sub-header styling: OK but non-shared
L3710: `font-size:10px;color:${col};text-transform:uppercase;letter-spacing:0.5px;font-weight:600` — matches the app's spotlight-header convention (cardSectors "Spotlight"). Acceptable inline. Consider a shared `.sub-section-head` class if this pattern propagates to ≥3 tiles.

### T3.3 [trivial] No header tooltip on card-title
"My Watchlist (N)" has no `tip data-tip="..."` explaining how flags get set or what Watch/Reduce/Add mean. Add: `<span class="tip" data-tip="Click the ⚑ flag icon on any holding to add it here. Cycle through Watch/Reduce/Add categories.">`.

### T3.4 [trivial] Active-weight color hardcoded via fallback chain
L3699: `let actCol=item.a>=0?'var(--pos)':'var(--neg)';` — **already tokenized**, good. But the color applies to the entire `a` cell including ticker EXITED state (T1.1), which muddies signal. Apply threshold classes `thresh-alert` / `thresh-warn` from the cardSectors gold standard (|active|>5 red, >3 amber) for consistency with other tables.

### T3.5 [trivial] Row heights / density: fine but inline
`padding:4px 6px` matches the 22px-dense rank-cell convention from AUDIT_LEARNINGS (11px font, 4px 6px padding). Consistent — but declared inline on every cell rather than via a class. Low-priority cleanup.

### T3.6 [trivial] Name column truncation
L3700: `max-width:260px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis` on name — inconsistent with cardHoldings which uses 200px. Minor. Unify to one value via a `.hold-name` class.

---

## Known issues / open questions

1. **Ghost holdings on stale watchlist** (T1.1) — user flags, PM exits next week, row silently shows 0.00. Highest-priority data-correctness fix.
2. **Feature invisible until populated** (T2.6) — new user has no on-boarding surface.
3. **Stale tile after cycleFlag** (T2.7) — add/remove in Holdings tab doesn't reflect on Overview until navigation.
4. **Merge vs sections** (T2.12) — PM gate on UX direction.

---

## Verification checklist (sign-offable items)

- [x] Tile renders when `_holdFlags` non-empty
- [x] Per-strategy persistence verified (`rr_flags_${s.id}`)
- [x] Row-click drills to `oSt(ticker)` same as Holdings
- [ ] Sort works on Port / Active — **missing**
- [ ] CSV export — **missing**
- [ ] Empty-state copy — **missing**
- [ ] Stable `<table id>` / `data-col` / `data-sv` — **missing**
- [ ] Right-click card-title → note popup — **works only after note exists (can't create one)**
- [x] Theme (dark + light) — partial: section headers use tokenized `${col}` (fine); FLAG_COLORS hex needs tokens (T3.1)
- [ ] No-longer-held ticker visual signal — **missing** (T1.1)
- [ ] Remove ticker in-tile — **missing** (T2.8)

---

## Fix queue

### TRIVIAL (agent-appliable)
1. T1.1 exited-state detection + visual muting
2. T1.3 isCash filter
3. T2.1 stable `<table id="tbl-watch-${key}">`
4. T2.2 `<thead>` with sortable `<th>` + tooltips
5. T2.3 `data-col` + `data-sv` on every cell
6. T2.4 wire `sortTbl` on Port/Active columns
7. T2.5 CSV export button (concatenate all three sections or one per section)
8. T2.6 empty-state fallback ("No tickers watchlisted — click ⚑ on any holding")
9. T2.7 re-render `#cardWatchlist` in cycleFlag if Overview is active
10. T2.8 row-hover remove `×` button
11. T2.10 add `oncontextmenu` on card-title for note popup
12. T3.1 tokenize FLAG_COLORS to `var(--warn/--neg/--pos)`
13. T3.3 header tooltip
14. T3.4 apply `thresh-alert`/`thresh-warn` classes
15. T3.5/3.6 class-driven row padding + name-width (cleanup)

### NEEDS PM DECISION
- T1.4 cross-strategy flag-sharing scope
- T2.12 merge Watch/Reduce/Add into one sortable table vs keep sections

### BLOCKED
- None. Data is 100% localStorage; no parser blockers.

---

## Cross-tile learnings to append to AUDIT_LEARNINGS.md

1. **Synthesis tiles invisible-until-populated** — cardThisWeek, what-changed, cardWatchlist, riskAlerts. All early-return `''` when data is empty → new user has no discovery path to the feature. Consider a single "setup hint" tile mode that shows a one-line tutorial while the underlying data is empty. Applies to ≥4 tiles.

2. **Mutation handlers that don't re-render their own tile** — `cycleFlag` (L3667) updates localStorage + patches one button but leaves the dependent `cardWatchlist` stale. Same class as: any tile whose state is set by an out-of-tile button. Audit every `onclick` handler that writes to `_holdFlags`, `_treeDrill`, `_facView`, `_selectedWeek`, etc., for "does this invalidate a dependent tile, and if so does the handler trigger its re-render?".

3. **Per-strategy localStorage scoping pattern** — `rr_flags_<strategyId>` is the correct namespace for PM-preference state that should NOT leak across mandates. Cross-check with `rr.<tile>.*` toolbar-state pattern flagged earlier: tile toolbar state is typically global, PM preference state is per-strategy. Distinct namespaces avoid collisions (e.g. `rr_flags_IDM` vs `rr.treemap.drill`).

4. **Ghost-data anti-pattern (new shape)** — flagged/saved user-generated state that references an entity (ticker) that may have left the underlying dataset. Watchlist is first site. Others likely: saved note keys referencing removed tickers, saved custom-alerts tied to deprecated factor names. Heuristic: any localStorage key referencing an entity from `cs.hold[]`/`cs.factors[]` needs a presence-check at render time.
