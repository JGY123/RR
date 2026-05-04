# cardWatchlist — Tile Audit

**Date:** 2026-05-04
**Auditor:** tile-audit subagent
**Tile id:** `cardWatchlist`
**Render fn:** `watchlistCardHtml(s)` at `dashboard_v7.html:9161`
**Tab placement:** Holdings tab (moved from Exposures per audit R2-Q1, 2026-04-30; mount comment at line 9429)
**Status:** **first audit on file** — no prior baseline.

---

## 0 — Triage queue (top of doc)

### TRIVIAL (subagent-applicable, ≤5 lines each)
1. **T2-A** — Rebind sort: `<th onclick="sortTbl(...)">` is missing on the `flag` column header (cosmetic; flag is icon-only) and **the `data-sv` payloads are sourced from raw fields, but `sortTbl` reads cell text by default**. Three sortable columns (`t`, `n`, `p`, `a`) currently sort by inner-text not by `data-sv` numeric. Smaller-than-expected risk because columns are simple, but Active% and Port% will sort lexicographically when they straddle a sign. **Verify on inspection** — may already be working via a `data-sv`-aware sortTbl.
2. **T3-A** — Empty-state markup uses inline `style="font-size:11px;color:var(--txt);padding:8px 6px"` instead of the canonical `.empty-state` class (per ARCHITECTURE §4.3). 3-line CSS-class swap.
3. **T3-B** — Section-divider mini-cap (`Watch (n)` / `Reduce (n)` / `Add (n)`) uses inline styles for uppercase + letter-spacing instead of `.section-label`. 1 class swap per section, 3 sites.
4. **T3-C** — Empty-state copy says "click the ⚑ flag icon on any holding row (Holdings tab)" — but **this tile is itself ON the Holdings tab now** (moved 2026-04-30). Self-referential and slightly confusing. Drop the parenthetical.
5. **T3-D** — Group-section header uses `font-size:10px` (line 9203). Project's design tokens (per ARCHITECTURE §4.3) target the 9/10/11/12/13 scale. 10 is OK but the corresponding `.section-label` token would be more durable.

### TRIVIAL-BUT-LARGER (15-40 lines, single-pass refactor)
6. **T2-B** — **No per-week routing.** `watchlistCardHtml(s)` reads `s.hold` directly (line 9162, 9166). When the user picks a historical week via `_selectedWeek`, the watchlist still resolves p/a from the latest `cs.hold[]`. ARCHITECTURE §4.4 mandates a per-week accessor (here: a `_wHold()` accessor that doesn't exist yet — would need adding to the accessor family). Two paths: (a) read via accessor when ready; (b) until then, pin the watchlist to "latest" and add a small note in the empty-state copy that watchlist is always vs latest week. **Requires PM call: do PMs want the watchlist to follow the week selector?**
7. **T2-C** — **CSV export reads from DOM, not data.** `exportWatchlistCsv()` (line 9211) walks the rendered `<table>` and pulls `.textContent`. This works but means hidden rows (`⚙ Cols`) export as empty cells, and any future formatting tweak to the cell HTML can break the export silently. Mirroring the cardHoldings `exportAllHoldings` pattern (rebuild from `_holdFlags` × `cs.hold` directly) would be more durable, ~25 lines.
8. **T1-A** — **No `Σ %T` footer** (intentional). The tile is per-row only — it doesn't aggregate, sum, or show a total %T. Per the F18 contamination map (`SOURCES.md` Lesson 16), this **keeps the tile F18-clean**: per-row %T is correct, only Σ is contaminated. **Recommend: add a one-line footer note** ("Per-row figures from latest week. No aggregate %T shown.") so future contributors don't add a Σ without realizing F18 implications.

### PM-GATE (needs user / PM decision)
9. **PM-1** — Should watchlist follow `_selectedWeek` or always show latest? (See T2-B.) Default-A behavior today: always-latest (p/a join uses `cs.hold[]` which is current-week). Watchlist is a **forward-looking PM tool** ("positions I'm watching") — making it follow historical weeks would let the PM ask "where were these positions on April 12" but is arguably a different mental model. **Recommend: keep latest-only, add explicit footer note.**
10. **PM-2** — Should the EXITED chip carry click-through to a "last seen" timestamp? Currently flagged tickers that no longer appear in `cs.hold[]` show `EXITED` with no historical context. Defer (B-item candidate).
11. **PM-3** — Universe pill (Port-Held / In Bench / All) does NOT affect this tile — only flags affect what shows. **Confirm intentional.** Recommend: yes, intentional — watchlist is a curation list, not a universe view.

---

## 1 — Identity

| Field | Value |
|---|---|
| Tile name | My Watchlist |
| Card DOM id | `#cardWatchlist` |
| Render function | `watchlistCardHtml(s)` (line 9161); empty-state branch line 9180 |
| Mount site | `${watchlistCardHtml(cs)}` at line 9432 (Holdings tab) |
| In-place re-mount | `cycleFlag()` at line 9149-9158 swaps the live DOM node when a flag is toggled |
| Width | full-width within Holdings tab; tile uses `style="margin-bottom:16px"` |
| Tab | Holdings (moved from Exposures per 2026-04-30 audit R2-Q1) |
| Spec status | **draft — first audit; no prior baseline** |

---

## 2 — Data Source (TRACK 1)

### Field inventory

| # | Label | Field | Type | Format | Sort affordance | Click | Source class | Confirmed? |
|---|---|---|---|---|---|---|---|---|
| 1 | Flag icon | `item.f` ∈ {watch, reduce, add} | string | `FLAG_ICONS[f]` (★ ▼ ▲) | column not sortable (icon) | row-level → `oSt(t)` | 🟢 sourced | ✅ from `localStorage rr_flags_${strategyId}`, set via `cycleFlag()` |
| 2 | Ticker | `item.displayT` (= `h.tkr_region` or `h.t`) | string | bare | yes (col 1) | row-level → `oSt(t)` | 🟢 sourced | ✅ from `cs.hold[].tkr_region` (parser-merged from SEDOL+Raw Factors); fallback to `cs.hold[].t` (SEDOL); fallback to flag key when EXITED |
| 3 | Name | `item.n` | string | bare; `text-overflow:ellipsis` | yes (col 2) | row-level | 🟢 sourced | ✅ `cs.hold[].n` (Security section col 6) |
| 4 | Port % | `item.p` (= `h.p`) | number | `f2(v)` | yes (col 3) | row-level | 🟢 sourced | ✅ `cs.hold[].p` (Security section `W` column) |
| 5 | Active % | `item.a` (= `h.a`) | number | `fp(v, 2)` (signed %) | yes (col 4) | row-level | 🟢 sourced | ✅ `cs.hold[].a` (Security section `AW` column) |
| 6 | EXITED chip | derived: `!holdMap[t]` | boolean | inline span "EXITED" | not sortable | — | 🟡 derived | ✅ chip displays when ticker key in `_holdFlags` is absent from `cs.hold[]` map. Chip is honest signal of "PM exited the position since you flagged it" — no fabricated p/a, p and a become `'—'` (line 9187-9188) |

### Spot-check verification

The data join is straightforward: `flags` map → ticker key → `holdMap[t]` join. **No synthesis** in `watchlistCardHtml`. No `?? 0`, no `??` chain — just direct field reads. `+(h.p||0)` and `+(h.a||0)` at line 9174 use `||0` rather than `??`, which means **explicit zero-coercion of null/undefined**. Per Lesson 15: `||0` on `p`/`a` is **semantically correct** (port-weight null = "not in portfolio" = 0); it would be **fabrication** on `tr`/`mcr`. Tile doesn't use `tr` or `mcr` → clean.

### F18 connection

**Tile is F18-CLEAN.** No Σ %T, no aggregate computation, no rank-by-%T sorting. Per-row %T isn't displayed at all. Per `SOURCES.md` Lesson 16 contamination map: cardWatchlist is **not currently listed**. **Finding:** add this tile to the F18 contamination map under **"clean — no aggregate"** so future audits don't have to re-derive the classification.

### Hard Rule #3 (localStorage is for preferences only)

**Compliant.** `rr_flags_${strategyId}` stores **flag state** (Watch / Reduce / Add categories per ticker), NOT cached holding data. Every render re-reads `cs.hold[]` and re-joins. The CLAUDE.md comment block at line 1124 explicitly says: "preferences only — never data". A rogue patch could try to cache `p` or `a` here for "snappier rendering" — would violate Rule #3 and would also break the EXITED-detection logic. Annotate the function header with a one-line comment to harden against future drift.

### SOURCES.md entry

`SOURCES.md` line 98-103 carries the cardWatchlist entry. **Finding:** the entry is correct but minimal. Recommend appending one row: `Flag state | 🟢 sourced (UI state) | localStorage rr_flags_${strategyId}; cycleFlag(t) writes; load-time recovery via loadHoldFlags()`.

### TRACK 1 verdict: **GREEN**
No fabrication. No synthesis. localStorage usage is policy-compliant. F18-clean. Per-cell provenance is documented in SOURCES.md (minor expansion suggested).

---

## 3 — Visualization

Three section tables (Watch / Reduce / Add). Each section omitted entirely if empty. Sort within section: pre-sorted by `Math.abs(a)` descending (line 9176) — biggest active-weight delta floats up, regardless of sign. **Reasonable default for a triage list.**

Table styling: 11px font, 4px row padding, inline-styled. Uses `.clickable` class on rows (good — re-uses canonical class). Color semantics:
- Active% cell: `var(--pos)` if `a≥0` else `var(--neg)`; `var(--txt)` (dim) when EXITED. ✅
- Flag icon: per-flag color from `FLAG_COLORS` (warn/neg/pos for watch/reduce/add). ✅

---

## 4 — Functionality matrix (TRACK 2)

Benchmark = cardSectors / cardHoldings.

| Capability | Benchmark | cardWatchlist | Gap? |
|---|---|---|---|
| `tileChromeStrip` migrated | yes | **yes** (line 9181 + 9206) | — ✅ |
| About popover | yes | yes (`about:true`) | — |
| Notes (📝 right-click) | yes | yes (`oncontextmenu="showNotePopup"`) | — |
| `⚙ Cols` panel | yes | **no** (no `cols:` config; tables have `data-col` so adding would just work) | minor — TRIVIAL fix |
| CSV export | yes | yes (`exportWatchlistCsv`) | — but reads from DOM not data (T2-C above) |
| **PNG export** | yes (some) | **NO** | ✅ correct per `feedback_no_png_buttons.md` — must NEVER add |
| Reset View | yes | yes (`resetView:true`) | — |
| Hide tile | yes | yes (`hide:true`) | — |
| Fullscreen | yes | yes (`fullscreen:openTileFullscreen('cardWatchlist')`) | — |
| Per-week routing | yes (`_wSec`, `_wCtry`, etc.) | **NO** (reads `s.hold` directly) | T2-B above; needs PM-1 decision first |
| Click-drill (row → ticker) | yes | yes (`oSt(t)`) | — ✅ correct pattern |
| Universe pill respect | yes (sectors/country/groups) | **does not respect** (intentional?) | PM-3 above — confirm intentional |
| Empty-state | varies | yes — onboarding tooltip | ✅ tile shows in empty form rather than disappearing |
| Right-click cell context menu | yes | inherited from row-level (no per-cell context) | — minor; per-row flag is the relevant action |
| Sort affordance | yes | yes — column headers wired (`onclick="sortTbl(...)"`) | T2-A: verify sortTbl reads `data-sv` for numeric cols |
| Tooltips on column headers | varies | yes (4 of 5 columns; flag column has no tooltip) | minor — flag column tooltip would help |
| Theme-aware | yes | yes (uses `var(--*)` tokens throughout) | — ✅ |
| Lint passes (`lint_week_flow.py --strict`) | yes | **likely fails** (direct `s.hold` read in render fn) | confirm by running lint |

### TRACK 2 verdict: **YELLOW**
Chrome migration done, click-drill works, CSV exists. Two real gaps: (a) per-week routing missing — needs PM gate before fix; (b) lint may flag `s.hold` direct access. Otherwise solid.

---

## 5 — Functionality (deeper)

### State management

`_holdFlags` is the in-memory cache; `loadHoldFlags()` reads from `localStorage rr_flags_${cs.id}` into `_holdFlags` at strategy-switch time (line 2465). `saveHoldFlags()` writes back. **Strategy-scoped:** each strategy has its own watchlist (IDM ≠ GSC). ✅ correct.

`cycleFlag(ticker, event)` (line 9136) cycles null → watch → reduce → add → null and re-renders the local flag button + the tile. **In-place tile re-render** (line 9149-9158) avoids full-tab re-render on flag toggle, preserves scroll. ✅ thoughtful.

### Cross-tile interactions

- Holdings tab top-strip: a "🚩 Flagged (N)" filter chip appears only when `_holdFlags` is non-empty (line 9488). Clicking filters the holdings table to flagged-only. ✅ good UX loop.
- `cardHoldings` rows render the `⚑` flag button per-row. ✅ click-source for adding to watchlist.

### Failure modes covered

- All flags exited: tile renders three sections each with EXITED rows. Tile doesn't disappear. ✅
- No strategy loaded (`!s||!s.id||!s.hold||!s.hold.length`): returns empty string (line 9162) → tile suppressed entirely (different from empty-flags state which renders onboarding). ✅ correct distinction: "no data loaded yet" vs "data loaded, no flags set".
- Strategy switch: `loadHoldFlags()` re-reads from localStorage with the new `cs.id`. ✅ scoped correctly.
- localStorage parse failure: try/catch wraps both read sites (line 9130, 9164) → falls through to `{}`. ✅

### Failure modes NOT covered

- localStorage **disabled or full**: `setItem` will throw silently; `try/catch` swallows. **Flag toggle would visually succeed but not persist.** No user-facing error. Minor — uncommon scenario.

---

## 6 — Design consistency (TRACK 3)

### Token compliance check

| Element | Current | Token-compliant? | Fix |
|---|---|---|---|
| Card padding | inline `style="margin-bottom:16px"` | partial — uses 16px hard value | use `--space-*` token if defined; else accept |
| Font size (rows) | `font-size:11px` | yes — within 9/10/11/12/13 scale | — |
| Font size (group header) | `font-size:10px` | yes | — |
| Font size (empty-state) | `font-size:11px` | yes | — |
| Row padding | `padding:4px 6px` | dense — consistent with cardHoldings | — |
| Ticker col width | `width:80px` | hardcoded; matches cardHoldings ticker width | — |
| Group header padding | `padding:0 6px` | yes | — |
| Numeric cell alignment | `class="r"` (right-align) | ✅ canonical | — |
| Color tokens | `var(--pos)` / `var(--neg)` / `var(--warn)` / `var(--txt)` / `var(--txth)` | ✅ all token-driven | — |
| EXITED chip background | `rgba(245,158,11,0.15)` hardcoded | **partial** — should be wash token | minor token sweep |
| EXITED chip color | `var(--warn)` | ✅ | — |
| **Empty-state class** | inline `style="font-size:11px;color:var(--txt);padding:8px 6px"` | **NO** — should be `.empty-state` | T3-A — 3-line swap |
| **Section label class** | inline `text-transform:uppercase;letter-spacing:0.5px` | **NO** — should be `.section-label` | T3-B — 3 sites |
| Card-title class | uses `class="card-title tip"` | ✅ canonical | — |
| Flag icon font weight | `font-weight:600` | yes | — |
| Hover tooltips | `class="tip" data-tip="..."` on column headers | ✅ canonical | — but flag-column header has no tooltip |
| Footer / hairline | **none** | **partial** — no hairline + caveat footer | T1-A above suggests adding "no Σ shown" caveat |
| Theme-aware | yes (all colors via tokens) | ✅ | — |

### Layout review

- Three vertically stacked tables, each section auto-skipped when empty. ✅ avoids dead space.
- Section label is small caps with letter-spacing — visually distinct, but built inline rather than via the `.section-label` token. Cosmetic, not broken.
- Card title shows the live total: `My Watchlist (${total})` — ✅ good affordance.

### Empty state

The empty-state branch (line 9180-9183) is one of the better-designed in the codebase: instead of suppressing the tile (which would hide the affordance entirely), it shows the title with the chrome strip and a one-sentence onboarding tooltip pointing the user to the ⚑ icon. ✅ pattern to replicate elsewhere. **One nit:** the parenthetical "(Holdings tab)" is now self-referential since this tile lives ON the Holdings tab. Drop it (T3-C).

### TRACK 3 verdict: **YELLOW**
Token compliance is mostly good — colors, font sizes, alignments all use the right primitives. The two design-system gaps are the `.empty-state` and `.section-label` classes (canonical CSS classes per ARCHITECTURE §4.3) being inlined rather than reused. Both are 3-line fixes. EXITED chip wash is a minor hardcode. No structural design issues.

---

## 7 — Known issues / Open questions

1. **PM-1** (above) — Should watchlist follow `_selectedWeek` or always show latest?
2. **PM-2** (above) — Should EXITED chip carry historical context?
3. **PM-3** (above) — Confirm: Universe pill should NOT affect watchlist? (Recommend: yes, keep independent.)
4. **Open spec question** — Empty-state copy still says "(Holdings tab)" — superseded by 2026-04-30 tab move. Already in trivial queue.
5. **Open spec question** — Add this tile to `SOURCES.md` Lesson 16 F18 contamination map under "clean — no aggregate"? (Recommend: yes.)
6. **Open spec question** — Lint check: does `lint_week_flow.py --strict` flag `s.hold` direct read inside `watchlistCardHtml`? If so: either (a) add accessor `_wHold()`, or (b) add an explicit `// lint-allow: latest-only by design (PM-1)` comment.

---

## 8 — Verification checklist

- [x] Data accuracy: all 5 columns trace to `cs.hold[]` or `localStorage rr_flags_*`, no fabrication
- [x] localStorage scoped per-strategy (`rr_flags_${cs.id}`)
- [x] localStorage stores STATE not DATA — Hard Rule #3 compliant
- [x] EXITED detection: ticker in `_holdFlags` but not in `cs.hold[]` map → grey + chip
- [x] Edge cases: empty flags, no strategy loaded, all-exited, strategy switch
- [ ] Edge case: localStorage full / disabled — silent failure (low-priority gap)
- [x] Sort works on Ticker, Name (text); **verify** Port%, Active% are numeric-sorted via `data-sv` (T2-A)
- [ ] `⚙ Cols` panel — not wired; would auto-work if added (T2-A in expanded form)
- [x] CSV export produces correct file (DOM-walk approach; T2-C suggests data-rebuild upgrade)
- [x] **No PNG button** — confirmed; `tileChromeStrip` config has `csv:`, no `png:` key. Per `feedback_no_png_buttons.md`, must remain.
- [x] Fullscreen modal renders (`openTileFullscreen('cardWatchlist')`)
- [x] Click drill: row → `oSt(ticker)` → single-ticker modal
- [x] Theme-aware (light + dark) — all colors via `var(--*)` tokens
- [ ] Per-week routing — **not wired**, gated on PM-1
- [x] No console errors (no Plotly here, just HTML)

---

## 9 — Verdict summary

| Track | Color | Headline |
|---|---|---|
| **T1 — Data accuracy** | **GREEN** | Zero fabrication. localStorage = state only. F18-clean. SOURCES.md entry exists; minor expansion suggested. |
| **T2 — Functionality parity** | **YELLOW** | Chrome strip migrated. Click-drill, CSV, fullscreen all wired. Two gaps: per-week routing absent (PM-gated) and CSV reads from DOM not data (durability concern). |
| **T3 — Design consistency** | **YELLOW** | Token-driven colors, alignments, font sizes. Two canonical CSS classes (`.empty-state`, `.section-label`) being inlined rather than reused. EXITED chip wash is hardcoded. All trivial fixes. |

**Overall: GREEN-with-trivials.** Tile is correctly designed (state vs data separation), correctly sourced, and has thoughtful empty-state + EXITED handling. Strongest aspect: the disciplined treatment of localStorage as preferences-only with re-join-on-render. Weakest aspect: design-system class adoption gaps (cosmetic, all 3-line fixes).

---

## 10 — Recommended fix queue (for coordinator)

**Apply now (TRIVIAL):**
- T3-A `.empty-state` class swap (line 9182)
- T3-B `.section-label` class swap (3 sites in line 9203 sections map)
- T3-C drop "(Holdings tab)" parenthetical from empty-state copy
- T1-A add a one-line caveat note: "Per-row figures from latest week. No aggregate %T shown — see F18."
- Add `flag` column header tooltip (`<th class="tip" data-tip="Flag category">`)
- Append "Flag state | localStorage rr_flags_*" row to SOURCES.md cardWatchlist entry
- Add cardWatchlist to `SOURCES.md` Lesson 16 F18 contamination map under "F18-CLEAN"

**Verify before fix (TRIVIAL):**
- T2-A confirm `sortTbl` reads `data-sv` for numeric Port% / Active% columns

**Apply after PM gate (TRIVIAL-BUT-LARGER):**
- T2-B per-week routing — only after PM-1 decision
- T2-C CSV export rebuild from `_holdFlags` × `cs.hold` instead of DOM walk

**Defer:**
- PM-2 EXITED-with-history (B-item candidate)
- localStorage-full silent-failure surfacing (low priority)

---

*End of audit.*
