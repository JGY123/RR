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
- Week-selector awareness: most sibling tiles read `getSelectedWeekSum()`; some read `s.sum` directly (e.g. cardThisWeek L946+, also the cash strip at L1117 when non-hist). When `_selectedWeek` is set, the banner promises a historical view but these tiles silently stay on latest — audit every new tile for this divergence.

## Primitives checklist (per ship-readiness sweep, 2026-04-20)
All data tables should have:
- [ ] `<table id="tbl-XXX">` (stable id, no generic `<table>`)
- [ ] Every `<th>` wired with `sortTbl('tbl-XXX',N)`
- [ ] Numeric cells carry `data-sv="${value}"` for correct sort
- [ ] Rows are `class="clickable"` + `onclick="oXxx(...)"` if drillable
- [ ] Empty-state fallback: `<p>No X data</p>` when input array is empty
- [ ] CSV button (`exportCSV('#tbl-XXX','name')`) — no PNG buttons (user preference, verified 2026-04-20)

## Sort anti-patterns (found ≥3 tiles)
- `data-sv="${x??0}"` coerces null to 0 — sort collapses "no data" with "actual zero". Use `data-sv="${x??''}"` so nulls sort as empty strings. Seen in cardChars L1800, cardFactors L1761/1763/1764, cardRanks L1782.

## Viz-renderer pattern (no table)
- Plotly target divs (scatDiv, treeDiv, mcrDiv, frbDiv, facButtDiv, etc.): guard `if(!data.length){ el.innerHTML='<p>No X data</p>'; return; }` — must write to the div, not silent return.
- Use `THEME().pos` / `THEME().neg` (extended 2026-04-20) instead of hardcoded `#10b981` / `#ef4444`.
- Click-to-drill parity: if a full-screen sibling wires `plotly_click → oDrX(name)`, the half-size tile should too. Seen missing on cardFacButt; full-screen `renderFsFactorMap` has it (L5542).
- Apply `.filter(f => isFinite(f.a))` (or equivalent) before mapping chart inputs — Plotly silently coerces NaN/null to 0, hiding missing data.

## Synthesis / insight tiles (narrative bullet cards)
- Pattern: `thisWeekCardHtml`, `riskAlertsBannerHtml`, `whatChangedBannerHtml`, `watchlistCardHtml`. Shared traits: rule-driven bullets, read `_thresholds`, silent-suppress when empty. Audit checklist: (1) every bullet subject should link to an existing drill modal (cardThisWeek currently has zero drill links — high-value gap); (2) fallback thresholds should read from `_thresholdsDefault`, not re-hardcoded `|| 8` / `|| 6` etc.; (3) add a tiny header tooltip linking to Settings so users can see what thresholds drove the bullet.

## Design conventions (cardSectors = gold standard, cardHoldings = gold standard)
- Threshold row classes: `|active|>5` → `thresh-alert`; `|active|>3` → `thresh-warn`
- Rank cells: right-aligned (`class="r"`), not center
- Spotlight (ORVQ) group: indigo tint `rgba(99,102,241,0.07)` background, left-border on first col
- Header tooltips: every numeric column should have `class="tip" data-tip="..."`
- Density: `<th>`=10px, `<td>`=11px, rank cells tighter (`padding:4px 6px`)

## Phantom-specs (audit trap)
- Some files in `tile-specs/` are raw JSONL transcripts of prior agent sessions, not hand-authored specs. They describe features an agent *claimed* to ship; many never landed. Always grep code for promised artifacts (CSS class names, helper fns) before treating the spec as live. Example: `portfolio-characteristics-spec.md` (2026-04-13) — 6/6 promises missing from code as of 2026-04-21.

## Completed audits
- ✅ cardSectors (2026-04-19, tag `tileaudit.cardSectors.v1`)
- ✅ cardHoldings (2026-04-19, tag `tileaudit.cardHoldings.v1`)
- ✅ cardCountry (2026-04-20, tag `tileaudit.cardCountry.v1` + `.v1.fixes`) — trivial fixes applied (theme colors, tooltips, rank alignment, threshold classes, TE columns)
- ✅ cardChars (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; 6/6 spec-drift findings; trivial fix queue of 7 pending)
- ✅ cardThisWeek (2026-04-21, audit only — GREEN/YELLOW/GREEN; top gap = no inline drill links on any bullet; trivial fix queue of 5, non-trivial 4)

## Known blockers (not auditable without data)
- Section 1.4 spot-check requires a loaded JSON/CSV reference. In CI-less env, flag as "pending" rather than fail the section.
- Trend sparklines on countries / groups / regions: require `hist.country` / `hist.grp` / `hist.reg` — parser doesn't collect. Medium-effort parser change needed.
- Trend sparklines on chars: parser overwrites `sum.mc/roe/fcfy/…` each week (L6177). Per-week chars history would need `s.hist.chars[metric]=[{d,p,b},…]`.

## How to append to this file
When your audit surfaces something ≥2 tiles will face, add a ≤2-line entry to the appropriate section above. Do not copy entire audit sections here.
