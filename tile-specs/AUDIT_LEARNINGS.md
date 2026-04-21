# Tile Audit — Cross-Tile Learnings

**Purpose:** running ledger of patterns, gaps, and conventions discovered during per-tile audits. Every audit agent reads this FIRST (after the template). Every audit appends any insight that could apply to other tiles.

> Keep entries tight. If something applies to ≥2 tiles, it belongs here.

---

## Data shapes (canonical)
- `cs.sectors[]`, `cs.countries[]`, `cs.regions[]`, `cs.groups[]` — all share the 19-col aggregate layout: `{n, p, b, a}` + ORVQ ranks. Per SCHEMA_COMPARISON.md L66–L97, offsets are stable.
- `cs.hold[]` — per-holding; carries `{t, n, sec, co, p, b, a, mcr, tr, over, rev, val, qual, factor_contr}`.
- Weighted-rank aggregation uses shared `rankAvg3(_secRankMode, ...)`. The mode is GLOBAL — toggling in one tile re-renders all ORVQ tiles.

## Shared state traps
- `_secRankMode` (Wtd / Avg / BM) is shared across cardSectors, cardCountry, cardGroups, cardRegions. Per-tile state would require splitting into `_secRankMode`, `_coRankMode`, `_grpRankMode`, `_regRankMode`. Deferred until a PM asks.

## Primitives checklist (per ship-readiness sweep, 2026-04-20)
All data tables should have:
- [ ] `<table id="tbl-XXX">` (stable id, no generic `<table>`)
- [ ] Every `<th>` wired with `sortTbl('tbl-XXX',N)`
- [ ] Numeric cells carry `data-sv="${value}"` for correct sort
- [ ] Rows are `class="clickable"` + `onclick="oXxx(...)"` if drillable
- [ ] Empty-state fallback: `<p>No X data</p>` when input array is empty
- [ ] CSV button (`exportCSV('#tbl-XXX','name')`) — no PNG buttons (user preference, verified 2026-04-20)

## Viz-renderer pattern (no table)
- Plotly target divs (scatDiv, treeDiv, mcrDiv, frbDiv, facButtDiv, etc.): guard `if(!data.length){ el.innerHTML='<p>No X data</p>'; return; }` — must write to the div, not silent return.
- Use `THEME().pos` / `THEME().neg` (extended 2026-04-20) instead of hardcoded `#10b981` / `#ef4444`.

## Design conventions (cardSectors = gold standard, cardHoldings = gold standard)
- Threshold row classes: `|active|>5` → `thresh-alert`; `|active|>3` → `thresh-warn`
- Rank cells: right-aligned (`class="r"`), not center
- Spotlight (ORVQ) group: indigo tint `rgba(99,102,241,0.07)` background, left-border on first col
- Header tooltips: every numeric column should have `class="tip" data-tip="..."`
- Density: `<th>`=10px, `<td>`=11px, rank cells tighter (`padding:4px 6px`)

## Completed audits
- ✅ cardSectors (2026-04-19, tag `tileaudit.cardSectors.v1`)
- ✅ cardHoldings (2026-04-19, tag `tileaudit.cardHoldings.v1`)
- ✅ cardCountry (2026-04-20, tag `tileaudit.cardCountry.v1` + `.v1.fixes`) — trivial fixes applied (theme colors, tooltips, rank alignment, threshold classes, TE columns)

## Known blockers (not auditable without data)
- Section 1.4 spot-check requires a loaded JSON/CSV reference. In CI-less env, flag as "pending" rather than fail the section.
- Trend sparklines on countries / groups / regions: require `hist.country` / `hist.grp` / `hist.reg` — parser doesn't collect. Medium-effort parser change needed.

## How to append to this file
When your audit surfaces something ≥2 tiles will face, add a ≤2-line entry to the appropriate section above. Do not copy entire audit sections here.
