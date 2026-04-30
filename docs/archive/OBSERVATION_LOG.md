# RR Dashboard Observation Log — 2026-04-19 (overnight pass)

**Scope:** programmatic click-through of all 3 tabs + all primary cards + chart rendering check + console error scan.
**Runtime:** `cs.id === 'EM'` (1218 holdings, 17 factors, 11 sectors, 27 countries, 4 regions, 3 historical weeks).

## Exposures tab ✅

### All 17 expected cards present:
`cardThisWeek`, `cardSectors`, `cardBenchOnlySec`, `cardFacButt`, `cardFacDetail`, `cardCountry`, `cardGroups`, `cardRanks`, `cardChars`, `cardScatter`, `cardTreemap`, `cardMCR`, `cardFRB`, `cardRegions`, `cardAttrib`, `cardUnowned`, `cardCorr`.

### All 7 primary charts rendered:
`secChartDiv` (sector butterfly), `facButtDiv` (factor risk map), `countryMapDiv` (choropleth), `scatDiv` (MCR-vs-TE scatter), `treeDiv` (treemap), `mcrDiv` (MCR bars), `frbDiv` (factor risk budget pie).

### 3 hero sum-cards present: TE, Idio, Factor Risk — Factor now click-drills (gap #3).

### Other heads-up elements:
- Risk alerts banner — conditional, rendered when alerts exist
- What Changed banner — conditional, rendered when prior-week snap exists and not dismissed
- Watchlist card — conditional, rendered when any flags exist (hidden on fresh EM)

## Risk tab ✅

### 8 cards present (up from 7 pre-gap-1):
1. Historical Trends mini-charts (NEW, 4 minis: TE / AS / Beta / H) — `miniTE`, `miniAS`, `miniBeta`, `miniH` all present
2. Risk Decomposition Tree
3. Tracking Error — Factor vs Stock-Specific Decomposition
4. Beta History — Predicted
5. Factor Contributions
6. Factor Exposures — click row for time series drill
7. Factor Exposure History (drill-rendered only)
8. Factor Correlation Matrix

### Primary charts rendered:
`riskBetaMultiDiv`, `riskFacBarDiv`, `riskExpHistDiv`, `corrHeatPlot` — all ✅.

`riskFacHistDiv` and `riskFacRetDiv` are drill-rendered only (fire when user clicks a factor row). Not an issue — expected behavior.

## Holdings tab ✅

- Table view renders 20-row page of 1218 holdings
- Cards view renders 30 cards via `renderHoldCards` (gap #10)
- Toggle Table/Cards switches cleanly
- Top 10 Holdings chart (gap #9 post-patch 008)
- Rank Distribution chart

## Console

Zero errors across full click-through of all tabs and both holdings views.

## Recently-changed tile smoke tests

| Tile | Change | Verification |
|---|---|---|
| Treemap (gap #7) | 4 dims × 3 sizes × 2 colors + drill | Switched dim to `co` (country): top buckets China/Taiwan/Korea/India ✅. Drill into Financials showed 11 holdings ✅. |
| Bench-Only Sector (gap #8) | Card + drill sub-section | 1000 bench-only names, 67% of bench missed, Financials 218 ✅ |
| Inline sparklines (gap #9) | Sector + region tables | Trend column added to both thead, 11 trend cells in sector table, default window = 6 ✅ |
| Holdings Cards (gap #10) | Full card renderer | 30 cards render, expand/collapse works ✅ |
| Spotlight Ranks 3-way | Wtd / Avg / BM across 3 tables | All three modes produce distinct values, group sector-alias bugfix working ✅ |
| Country map 9+ modes | Per gap 0c606cd | Country dim: 26 countries, setMapRegion('asia') correctly zooms, factor Volatility now populated via h.factor_contr ✅ |

## No open blocker bugs

All cards render. All toggles function. Click-drills open their modals. Full-screen modals (factmap, scatter, country) all open cleanly per earlier audits.

## Latent concerns (not bugs, but worth future attention)

1. **`~/RR/archive/`, `~/RR/cli-prompts/`, `~/RR/tile_spec.html`, `~/RR/.DS_Store`** — untracked files at repo root, sit in `git status` every commit. Consider .gitignore additions for `.DS_Store` + `archive/`. cli-prompts and tile_spec.html could be committed or moved.
2. **Preview server is project-only :3099** — if PM opens dashboard without running server, fetch() fails silently. Non-technical users won't diagnose. Low-priority.
3. **No automated snapshot test** — every check tonight was manual. A 50-line `test-snapshot.js` (see `FORWARD_PLAN.md` §4) would catch regressions before they ship. Architectural recommendation.
4. **EM test data has only 3 weeks in `hist.sum`** — several new features (Historical Trends mini-charts, Inline sparklines) render minimally until fuller data arrives. Expected; FactSet email §13 requests 36 months.

## Commits that landed this overnight

14 commits on RR main, cleanly pushed to origin/JGY123/RR. Full list in `SESSION_STATE.md`.

---

**Bottom line:** dashboard is in the best state of the project's history. All 22 original features + 10 recovered gaps + the 2026-04-19 cross-project scaffolding in place. Zero known regressions. Safe to hand to a PM on Monday morning.
