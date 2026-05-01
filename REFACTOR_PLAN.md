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

| Phase | Scope | Est. | Status |
|---|---|---|---|
| **A** | Audit current state — every tile + every table + their chrome. Update `TILE_CHROME_MATRIX.md` with truth. | 30 min | ☐ |
| **B** | Build `TableSpec` + `renderTable` + `tableFilterPanel`. Migrate `cardSectors` as canary. Smoke test. | 2 hrs | ☐ |
| **C** | Migrate `cardCountry`, `cardGroups`, `cardRegions`, `cardChars`, `cardAttrib`, `cardFacDetail` to TableSpec. Each ~30 min: declare spec, replace renderer call, remove old function. Net: −800 lines. | 3 hrs | ☐ |
| **D** | Build `tileChrome()` contract. Migrate Tier-1 tiles. Then Tier-2/3 sweep. | 2 hrs | ☐ |
| **E** | Build `OpenFullscreen` + Country (Map+Heat+Chart+Table tabs). Sector fullscreen + KPI summary tiles above. | 2 hrs | ☐ |
| **F** | Universe-selector audit. "Both" double-counting check. | 1 hr | ☐ |
| **G** | Scroll preservation on `changeWeek` / `setImpactPeriod`. | 30 min | ☐ |
| **H** | Factor Detail per-week wiring + period selector. | 1 hr | ☐ |
| **I** | Known data bug: Kongsberg false-exit in cardWeekOverWeek (hold_prev shorter than hold). | 30 min | ☐ |
| **J** | Render-time linter for direct `cs.X` access in render paths. | 1 hr | ☐ |

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
