# RR Refactor Plan — Uniform Feature Flow

**Started:** 2026-05-01 (post-presentation)
**Baseline tag:** `presentation-2026-05-01-shipped` (commit `3b10805`)
**North-star goal:** features ship from one place, not N places.

---

## Why we're doing this

After the May 1 presentation, the user observed that "many tables / cards / tiles don't have all the functionality we spoke about" and asked whether the code could be organized better. The honest answer is yes:

- 6+ table renderers (`rWt`, `rCountryTable`, `rGroupTable`, `rChr`, …) each ~100 lines, each with its own column-picker, filter-chip, sparkline, fullscreen path
- 30+ tiles, each assembling its own chrome (About + Notes + Reset View + Hide + Full Screen + CSV) inline
- Per-tile fullscreen functions (`openSecFullscreen`, `openCtryFullscreen`, …) instead of one generalized opener
- Render functions reading `cs.sectors` / `cs.hold` / `cs.countries` directly, instead of going through the per-week-aware accessors `getDimForWeek` / `getSelectedWeekSum`

Result: when we add a feature, it ships to whatever I touched and stays broken everywhere else. That's the pattern the user is calling out.

## The four abstractions

### 1. `TableSpec` — declarative table definition
Each table declares once: `{ id, data, columns, filterable, sortable, drillFn, csvName, fullscreen }`. One renderer (`renderTable(spec)`) produces HTML. One filter panel (`tableFilterPanel(spec)`) produces column-hide/show controls. Every table behaves identically.

### 2. `tileChrome({…})` — single source of truth for buttons
Replaces inline assembly of About / Notes / Reset View / Hide / Full Screen / CSV / View Toggle in every card. Add a button → it ships everywhere.

### 3. `getDimForWeek` enforcement
Already exists. Add a render-time linter that warns when a renderer reads `cs.sectors` / `cs.hold` / `cs.countries` directly instead of going through the accessor. Catches "forgot to swap" leaks before they ship.

### 4. `OpenFullscreen(tileId, opts)` — uniform fullscreen
Each tile registers `{ preserveCurrentView, richFeatures }`. Country gets Map / Heat / Chart / Table tabs. Sector gets KPI summary tiles above the table.

---

## Phase plan + checkpoints

**Updated 2026-05-01 14:00 — pivoted to lower-risk approach.** Audit revealed every existing renderer (`rWt`, `rCountryTable`, `rGroupTable`, `rChr`, `rAttribTable`) already emits `data-col="X"` on `<th>` and `<td>`. 146 such annotations across the file. That means we can ship **uniform column hide/show via CSS attribute selectors** without rewriting any renderer. This dramatically lowers risk: existing rendering stays exactly as-is, we add a sidecar layer.

| Phase | Scope | Est. | Status |
|---|---|---|---|
| **A** | Audit — DONE. See `REFACTOR_AUDIT.md`. | — | ✅ |
| **B** | Build `tableColHide` framework: (1) auto-discover columns from rendered DOM via `th[data-col]`, (2) build a sidecar panel listing them as checkboxes, (3) hide via CSS rule `td[data-col="X"], th[data-col="X"] { display:none }`, (4) state persists in `rr.tableColHide.v1`. Apply to cardSectors as canary. | 1 hr | ☐ |
| **C** | Apply `tableColHide` to every table that has `data-col` attrs: cardSectors, cardCountry, cardGroups, cardRegions, cardChars, cardAttrib, cardFacDetail, cardRiskFacTbl. One button placement, identical UX everywhere. | 30 min | ☐ |
| **D** | Build `tileChrome()` contract. Migrate Tier-1 tiles to use it (drops ~800 lines of inline chrome assembly). Then Tier-2/3 sweep. | 2 hrs | ☐ |
| **E** | `openTileFullscreen` improvements: per-tile registration so Country preserves Map view + adds Heat/Chart/Table tabs; Sector adds KPI summary tiles above table. | 2 hrs | ☐ |
| **F** | Universe-selector audit — does "Both" double-count? Report findings before touching code. | 30 min | ☐ |
| **G** | Scroll preservation on `changeWeek` (snapshot scrollY before render, restore after). | 30 min | ☐ |
| **H** | Factor Detail per-week wiring + period selector + scroll-preserving update. | 1 hr | ☐ |
| **I** | Known data bug: Kongsberg false-exit in cardWeekOverWeek (hold_prev shorter than hold — tickers in hold but missing from hold_prev get flagged "exited" wrongly). | 30 min | ☐ |
| **J** | Render-time `console.warn` linter for direct `cs.sectors` / `cs.countries` / `cs.hold` access in render paths. Catches week-flow leaks. | 1 hr | ☐ |
| **K** | Visual polish pass — once architecture is uniform, design polish across tiles. Spacing, typography, color harmony. | 1-2 hrs | ☐ |

**Total: ~13 hrs.** Ships incrementally — each phase is a checkpoint with a working dashboard.

---

## Ground rules

1. **The working dashboard never breaks.** After each phase: smoke test + visual diff vs `presentation-2026-05-01-shipped`. If anything regresses, fix before moving on.
2. **Tag every checkpoint.** `refactor.YYYYMMDD.HHMM.phase-X-complete` so we can roll back at any point.
3. **No new features during refactor.** Only the migration. New features go in a separate phase after the architecture is solid.
4. **Visual + functional parity first, design polish second.** Don't try to redesign while migrating. Migrate to spec, then a separate pass for design.
5. **Anti-fabrication policy stays sacred.** No new "if X is null compute Y" patches. Per-tile data integrity carries forward.
6. **Smoke test gates every commit.** `node` parse check + `python3` JSON check + sample render of cardSectors / cardCountry / cardWeekOverWeek.

---

## Checkpoint log

| Date | Phase | Commit | Tag | Notes |
|---|---|---|---|---|
| 2026-05-01 12:30 | baseline | `3b10805` | `presentation-2026-05-01-shipped` | TE bug fixed live during demo. ACWI/IDM full-history recovered. |
| 2026-05-01 14:30 | A audit | — | — | REFACTOR_AUDIT.md ships full inventory. 12 tables × 30 tiles. |
| 2026-05-01 15:00 | B tableColHide canary | — | `refactor.20260501.1500.phase-B-canary` | Sidecar framework: data-col CSS rules + checkbox panel + persisted state. cardSectors as canary. |
| 2026-05-01 15:30 | C tableColHide sweep | — | `refactor.20260501.1530.phase-C-complete` | Applied to all 8 tables. Uniform UX across cardSectors/Country/Groups/Regions/Chars/Attrib/FacDetail/RiskFacTbl. |
| 2026-05-01 15:45 | G scroll preservation | — | `refactor.20260501.1545.phase-G-scroll` | `_withScrollPreserved` wrapper. changeWeek + jumpToLatest + setImpactPeriod no longer jump to top. |
| 2026-05-01 16:00 | I WoW tooltips | — | `refactor.20260501.1600.phase-I-wow-tooltips` | Diagnosed Kongsberg "false-exit" — actually correct (two Kongsbergs). Added full-name+ticker+sector tooltip to disambiguate. |
| 2026-05-01 16:10 | F universe audit | — | — | UNIVERSE_AUDIT.md: no double-counting bug. UX/labeling proposed (5 options A-E). Awaiting user direction. |
| 2026-05-01 16:20 | H Factor flows per-week | — | `refactor.20260501.1620.phase-H-factor-detail` | `getFactorsForWeek` + `_wFactors` accessor. Wired into cardFacDetail + cardFacRisk + Risk-tab factor table. |
| 2026-05-01 16:40 | E.1 Country FS Map fix | — | `refactor.20260501.1640.phase-E-country-map-fix` | Detect view via toggle .active class, not chart-div display. Map FS now opens correctly. |
| 2026-05-01 16:55 | E.2 Country FS view tabs | — | `refactor.20260501.1655.phase-E2-country-fs-tabs` | Map / Heat / Table tabs inside FS modal — flip without exiting. |
| 2026-05-01 17:15 | J week-flow lint | — | `refactor.20260501.1715.phase-J-lint` | Static lint catches direct cs.X access in render fns. Wired into smoke_test.sh. Annotated 7 false-positives, fixed 1 real issue. |
| 2026-05-01 17:45 | org spine | — | `refactor.20260501.1745.org-spine` | SESSION_GUIDE.md + AGENTS.md (subagent runbook) + dev_dashboard.html (project state at a glance) + docs/INDEX.md update. |
| 2026-05-01 17:55 | F UX shipping | — | `refactor.20260501.1755.phase-F-universe-ux` | Universe pill: rename (Port-Held / In Bench / All) + per-pill tooltips + persistent count strip. Backend logic unchanged. |
| 2026-05-01 18:10 | item 2A | — | `refactor.20260501.1810.item-2A-sector-fs-summary` | Sector fullscreen: 9 summary stat tiles (Top Risk, Top Diversifier, Largest OW, Largest UW, Biggest Port, Biggest Bench, Σ \|Active\|, etc.). Flows per-week. |
| 2026-05-01 18:20 | item 4 | — | `refactor.20260501.1820.item-4-fac-perf-yaxis` | Factor Performance y-axis: smart tick decimals based on value range, % suffix matches title unit. |
| 2026-05-01 18:30 | D helper | — | `refactor.20260501.1830.phase-D-helper` | tileChromeStrip() helper — single source of truth. Migrations gradual (per-tile as touched). |
| 2026-05-01 18:40 | session wrap | — | `refactor.20260501.1840.session-wrap` | REFACTOR_PLAN + SESSION_STATE + dev_dashboard final updates. |
| 2026-05-01 19:00 | K.1-3 design tokens | — | `refactor.20260501.1900.phase-K1-design-tokens` | --space-*, --text-*, --w-*, --radius-*, washes, hairline, shadows added to :root. .tile-btn / .export-btn unified. 5 chrome helpers + tableColHide + tileChromeStrip swept to .tile-btn class. DESIGN_AUDIT.md from subagent. |
| 2026-05-01 19:20 | K.4-5 empty + stat | — | `refactor.20260501.1920.phase-K-empty-stat` | .empty-state class swept across 9 inline empty-state strings. .stat-card class swept across 2 inline stat() helpers (sector full-page summary). |
| 2026-05-01 19:35 | K.6 polish final | — | `refactor.20260501.1935.phase-K-final-polish` | .modal-close-btn (10 occurrences), .section-label (16 occurrences) swept. Phase K complete. |
| 2026-05-03 09:00 | D-canary | — | `refactor.20260503.0900.phase-D-canary` | tileChromeStrip enhanced with `download` + `view` slots. cardSectors migrated as canary. Bug caught: backticks in HTML comments close parent template literal — fixed. |
| 2026-05-03 09:30 | D-tier1-sweep | — | `refactor.20260503.0930.phase-D-tier1-sweep` | cardGroups + cardRegions + cardCountry + cardAttrib migrated to tileChromeStrip. ~140 lines of inline chrome → ~50 lines declarative config. |
| 2026-05-03 09:45 | design color sweep | — | `refactor.20260503.0945.design-color-sweep` | 17 HTML-context `color:#94a3b8` → `color:var(--textDim)`. Plotly traces left untouched (separate refactor). |

## Status summary (post-2026-05-01 session)

**Shipped:**
- All 8 dashboard tables have uniform "⚙ Cols" hide/show panel (Phase B+C).
- Scroll position preserved on week / period change (Phase G).
- WoW row tooltips disambiguate similarly-named holdings (Phase I).
- Universe selector audited; no bug; UX options proposed (Phase F).
- Factor Detail / Factor Risk Snapshot / Risk-tab factor table all flow per-week (Phase H).
- Country fullscreen — Map view now opens correctly + tabs Map/Heat/Table inside FS (Phase E).
- Static lint prevents future direct-cs.X regressions (Phase J).

**Outstanding:**
- Phase D — `tileChromeStrip()` helper SHIPPED (2026-05-01 18:30). Tile-by-tile migration is gradual (each commit that touches a tile's chrome can swap to the helper).
- ~~Phase K — design polish~~ — SHIPPED 2026-05-01 19:00–19:35. Tokens + 10 canonical classes + ~40 inline styles eliminated.
- Per-holding factor TE breakdown for historical weeks — data not shipped per-week from FactSet, currently shows "—" with explanation. Would require parser-side per-week per-holding factor_contr extraction (would balloon file size). Deferred to FactSet conversation.
- Phase F UX (combo A+D+E) — SHIPPED 2026-05-01 17:55.
- Item #2A sector full-page summary tiles — SHIPPED 2026-05-01 18:10.
- Item #4 Factor Performance y-axis — SHIPPED 2026-05-01 18:20.

**Next session priorities (ordered by leverage):**
1. **Continue tileChromeStrip migration** — remaining Tier-1: cardThisWeek (no view toggle, simpler), cardWeekOverWeek, cardFacRisk (Risk-tab Tier-1), cardChars, cardFacDetail, cardRiskFacTbl. Defer cardHoldings (most complex — dedicated commit).
2. **Per-tile audit cadence resume** — pick 2-3 Tier-2 tiles for a `tile-audit` subagent sweep.
3. **Plotly THEME() per-trace cleanup** — 5 remaining `color:'#94a3b8'` Plotly object-literal occurrences. Replace with `THEME().tick` accessor for full theme-flip support.
4. **Spacing scale adoption** — sweep remaining hardcoded `padding: Xpx` / `gap: Xpx` to `var(--space-*)` tokens.
5. **Per-tile design pass** — apply `.stat-card` / `.empty-state` / `.section-label` to remaining inline-styled patterns (cardThisWeek bullets, cardWeekOverWeek headers, drill modals).

---

## Wider rollout (post-refactor)

The user said: "we need to start thinking about how to roll it to wider use." After the refactor is done, the architecture will be ready for:

- **Multi-user deployment** — Linux server + nginx + systemd timer. Per-user preferences in localStorage already isolated.
- **Per-firm theming** — CSS variables already drive colors. Add a theme picker.
- **API mode** — switch between FactSet CSV and a future API endpoint by changing one accessor.
- **Onboarding** — declarative TableSpec + TileSpec means a new strategy / new tile is "write a config", not "copy 200 lines of inline JS."

Tracking these in a separate `ROLLOUT.md` post-refactor.

---

## How to use this doc

- Update the Phase status when starting / finishing each phase.
- Append to the Checkpoint log after each commit.
- If a phase changes scope, edit it here BEFORE starting work.
- This file is the single source of truth for refactor progress.
