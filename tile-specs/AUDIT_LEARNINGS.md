# Tile Audit — Cross-Tile Learnings

**Purpose:** running ledger of patterns, gaps, and conventions discovered during per-tile audits. Every audit agent reads this FIRST (after the template). Every audit appends any insight that could apply to other tiles.

> Keep entries tight. If something applies to ≥2 tiles, it belongs here.

---

## Data shapes (canonical)
- `cs.sectors[]`, `cs.countries[]`, `cs.regions[]`, `cs.groups[]` — all share the 19-col aggregate layout: `{n, p, b, a}` + ORVQ ranks. Per SCHEMA_COMPARISON.md L66–L97, offsets are stable.
- `cs.hold[]` — per-holding; carries `{t, n, sec, co, p, b, a, mcr, tr, over, rev, val, qual, factor_contr}`. Region is derived at normalize-time: `h.reg = CMAP[h.co]||'Other'` (dashboard_v7.html:512) — any holding with `h.co` not in `CMAP` silently buckets to "Other" (same class of drift as cardCountry's COUNTRY_ISO3).
- Weighted-rank aggregation uses shared `rankAvg3(_secRankMode, ...)`. The mode is GLOBAL — toggling in one tile re-renders all ORVQ tiles.

## Shared state traps
- `_secRankMode` (Wtd / Avg / BM) is shared across cardSectors, cardCountry, cardGroups, cardRegions. Per-tile state would require splitting into `_secRankMode`, `_coRankMode`, `_grpRankMode`, `_regRankMode`. Deferred until a PM asks.
- **Hidden control trap:** cardRegions does NOT surface `rankToggleHtml3()` in its header — users must flip the toggle in cardSectors for it to affect cardRegions. The shared state is invisible from the tile's own UI. Verify each tile with rank columns either (a) renders its own toggle or (b) carries an inline hint explaining the shared control.
- Week-selector awareness: most sibling tiles read `getSelectedWeekSum()`; some read `s.sum` directly (e.g. cardThisWeek L946+, also the cash strip at L1117 when non-hist). When `_selectedWeek` is set, the banner promises a historical view but these tiles silently stay on latest — audit every new tile for this divergence. Detail tables (sectors/regions/countries/groups) ALWAYS silently show latest data; this is the two-layer history architecture working as designed, not a bug.

## Primitives checklist (per ship-readiness sweep, 2026-04-20)
All data tables should have:
- [ ] `<table id="tbl-XXX">` (stable id, no generic `<table>`)
- [ ] Every `<th>` wired with `sortTbl('tbl-XXX',N)`
- [ ] Numeric cells carry `data-sv="${value}"` for correct sort
- [ ] Every `<th>` + `<td>` carries a stable `data-col="..."` — prerequisite for any future column-picker. Seen missing in the `type==='reg'` branch of `rWt` (cardRegions) — `data-col` infrastructure exists for sectors but not for regions or groups. Retrofitting requires touching both th and td.
- [ ] Rows are `class="clickable"` + `onclick="oXxx(...)"` if drillable
- [ ] Empty-state fallback: `<p>No X data</p>` when input array is empty
- [ ] CSV button (`exportCSV('#tbl-XXX','name')`) — no PNG buttons (user preference, verified 2026-04-20). cardRegions still offers "Download PNG" in its ⬇ menu (dashboard_v7.html:1331) — flag for removal on next cross-tile sweep.

## Sort anti-patterns (found ≥3 tiles)
- `data-sv="${x??0}"` coerces null to 0 — sort collapses "no data" with "actual zero". Use `data-sv="${x??''}"` so nulls sort as empty strings. Seen in cardChars L1800, cardFactors L1761/1763/1764, cardRanks L1782.
- **Missing `data-sv` entirely** on region rank cells at dashboard_v7.html:1581. `sortTbl` silently falls back to `textContent` parsing — works for clean numbers but not for "—" placeholders. Re-check every `rankCell` helper for this when auditing sibling aggregation tiles.

## Viz-renderer pattern (no table)
- Plotly target divs (scatDiv, treeDiv, mcrDiv, frbDiv, facButtDiv, **regChartDiv**, etc.): guard `if(!data.length){ el.innerHTML='<p>No X data</p>'; return; }` — must write to the div, not silent return. `rRegChart` (L2283-2285) silent-returns and leaves stale prior render on strategy switch.
- Use `THEME().pos` / `THEME().neg` (extended 2026-04-20) instead of hardcoded `#10b981` / `#ef4444`. Also `inlineSparkSvg` (L1438) hardcodes `#10b981`/`#ef4444` at L1451 — affects both sector and region sparklines. `rRegChart` hardcodes `rgba(99,102,241,0.85)` / `rgba(75,85,99,0.85)` port/bench colors (L2298/2301) — no `--pri`/`--bench` tokens currently exist.
- Click-to-drill parity: if a full-screen sibling wires `plotly_click → oDrX(name)`, the half-size tile should too. Seen missing on cardFacButt; full-screen `renderFsFactorMap` has it (L5542). `rRegChart` has NO click handler — regions chart is read-only, unlike sector/country charts.
- Apply `.filter(f => isFinite(f.a))` (or equivalent) before mapping chart inputs — Plotly silently coerces NaN/null to 0, hiding missing data.

## Half-built data pipelines (high-impact audit flag)
**Pattern:** render-side code reads `cs.hist.X[name]`, parser-side declares `"X": {}` but never populates. Result: a column/chart/selector that is silently dead on every run. Found in:
- `cs.hist.reg` — read by `rWt` (L1589) and `oDr` (L3946); parser writes `{}` (factset_parser.py:838). Breaks: cardRegions sparkline column, cardRegions drill historical chart, drill range selector.
- `cs.hist.sec` (partial — parser writes `{}` at L837; populated only via monthly snapshots in some flows)
- `cs.hist.country`, `cs.hist.grp` — never declared, never populated; also block their tiles' trend features.
When auditing any tile with a sparkline / trend / historical drill, grep both the render-side access path AND the parser's output dict. If the dict is empty, the feature is shell-only. Treat as BACKLOG unless trivial to wire.

## Synthesis / insight tiles (narrative bullet cards)
- Pattern: `thisWeekCardHtml`, `riskAlertsBannerHtml`, `whatChangedBannerHtml`, `watchlistCardHtml`. Shared traits: rule-driven bullets, read `_thresholds`, silent-suppress when empty. Audit checklist: (1) every bullet subject should link to an existing drill modal (cardThisWeek currently has zero drill links — high-value gap); (2) fallback thresholds should read from `_thresholdsDefault`, not re-hardcoded `|| 8` / `|| 6` etc.; (3) add a tiny header tooltip linking to Settings so users can see what thresholds drove the bullet.

## Design conventions (cardSectors = gold standard, cardHoldings = gold standard)
- Threshold row classes: `|active|>5` → `thresh-alert`; `|active|>3` → `thresh-warn`
- Rank cells: right-aligned (`class="r"`), not center. **Unresolved delta across geographic tiles**: cardCountry + cardRegions both center-align ranks, cardSectors right-aligns. Flagged in cardCountry-audit §7 #5 and cardRegions-audit §7 #13. Either unify to right (sectors style) or document as intentional for geographic tiles.
- Spotlight (ORVQ) group: indigo tint `rgba(99,102,241,0.07)` background, left-border on first col. Region rank cells use `0.04` (lighter) — minor inconsistency.
- Spotlight header row: cardSectors has a two-row `<thead>` with `colspan`-grouped "Spotlight" header + inline `rankToggleHtml3()`. cardRegions/cardGroups lack this pattern — single-row thead, no inline toggle. Worth unifying if the shared `rWt` is ever refactored.
- Header tooltips: every numeric column should have `class="tip" data-tip="..."`. Region R/V/Q headers lack `data-tip` (dashboard_v7.html:1631) — only O has one.
- Density: `<th>`=10px, `<td>`=11px, rank cells tighter (`padding:4px 6px`)

## Redundant / clutter UX patterns
- Persistent header-text disclaimers that duplicate conditional ones: cardRegions renders "Region coverage may be low for US-focused strategies" ALWAYS at L1330, even though (a) for US-only strategies the card is hidden entirely, and (b) an amber <50%-coverage disclaimer already renders below the table (L1636) when actually relevant. Audit each tile for header text that repeats information already shown conditionally.

## Phantom-specs (audit trap)
- Some files in `tile-specs/` are raw JSONL transcripts of prior agent sessions, not hand-authored specs. They describe features an agent *claimed* to ship; many never landed. Always grep code for promised artifacts (CSS class names, helper fns) before treating the spec as live. Example: `portfolio-characteristics-spec.md` (2026-04-13) — 6/6 promises missing from code as of 2026-04-21.

## Completed audits
- ✅ cardSectors (2026-04-19, tag `tileaudit.cardSectors.v1`)
- ✅ cardHoldings (2026-04-19, tag `tileaudit.cardHoldings.v1`)
- ✅ cardCountry (2026-04-20, tag `tileaudit.cardCountry.v1` + `.v1.fixes`) — trivial fixes applied (theme colors, tooltips, rank alignment, threshold classes, TE columns)
- ✅ cardChars (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; 6/6 spec-drift findings; trivial fix queue of 7 pending)
- ✅ cardThisWeek (2026-04-21, audit only — GREEN/YELLOW/GREEN; top gap = no inline drill links on any bullet; trivial fix queue of 5, non-trivial 4)
- ✅ cardRegions (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = B6 blocker still valid, parser L837-838 hardcodes `hist.reg:{}`; trivial fix queue of 8, non-trivial 4)

## Known blockers (not auditable without data)
- Section 1.4 spot-check requires a loaded JSON/CSV reference. In CI-less env, flag as "pending" rather than fail the section.
- Trend sparklines on countries / groups / regions: require `hist.country` / `hist.grp` / `hist.reg` — parser doesn't collect. Medium-effort parser change needed. **Re-confirmed 2026-04-21** during cardRegions audit — parser factset_parser.py:837-838 hardcodes `"sec": {}, "reg": {}` and never populates. BACKLOG B6 is the single highest-impact non-trivial item across all three sibling tiles.
- Trend sparklines on chars: parser overwrites `sum.mc/roe/fcfy/…` each week (L6177). Per-week chars history would need `s.hist.chars[metric]=[{d,p,b},…]`.

## How to append to this file
When your audit surfaces something ≥2 tiles will face, add a ≤2-line entry to the appropriate section above. Do not copy entire audit sections here.

## Factor-family patterns (surfaced 2026-04-21, cardFRB audit)
- `cs.factors[]` = per-factor object `{n, e, bm, a, c, ret, imp, dev, cimp, risk_contr}` from parser `_build_factor_list` (factset_parser.py:L847-L865). The identity `MCR = f.c * te / 100` in `oDrRiskBudget` L5394 confirms **`f.c` is "% of portfolio TE"**, not "% of factor risk". Tiles that normalize `Σ|f.c|` to 100 (cardFRB donut L2696, Risk Decomp Tree L2770) therefore show **share of factor risk**, not share of TE — state the denominator in hovertemplates (cardFRB's bare "Contrib: %{value:.2f}%" is ambiguous).
- **Sign-collapse anti-pattern:** `Math.abs(f.c || 0)` erases direction. Acceptable on pure magnitude views (Top |MCR|); **not** acceptable on a risk-budget donut where a diversifying (negative-contribution) factor must read differently from a risk-adding one. Seen in cardFRB L2696 + `oDrRiskBudget` L5389 + Risk Decomp Tree L2770. If keeping abs, colorize the sign separately.
- No tile reads `hist.fac`. Every factor tile (cardFRB + drill, cardFacButt, cardFacDetail, Risk Decomp Tree) silently shows latest when `_selectedWeek` is set. Same shape as the cardRegions `hist.reg` blocker but for factors — parser-side readiness unclear; verify before promising the fix.

## Tile-wide `onclick` pattern (accepted, but fragile — surfaced 2026-04-21, cardFRB)
- `.card` with `onclick=...; cursor:pointer` opening a detail modal is an established pattern (summary cards L1110+, cardFRB L1282). Three checks every audit must run:
  1. **Keyboard access:** needs `tabindex="0" role="button" aria-label="..." onkeydown="..."` — summary cards have it, cardFRB does not.
  2. **Bubbling on child controls:** any in-card button (PNG/CSV/toggle) needs `event.stopPropagation()` in its own handler — cardFRB's PNG button has this (L1284) but the guard becomes dead once PNG is removed.
  3. **Slice/row click parity:** if the card contains a Plotly chart inside a tile-wide-click card, users will click a specific slice expecting per-item drill. Bubbling to tile-level modal is a UX trap. Wire `plotly_click → oDrX(label)` even when tile-level onclick exists. cardFRB donut currently bubbles every slice click to `oDrRiskBudget` instead of drilling into `oDrF(slice.label)`.
- Hover-state almost always missing on tile-wide-click cards. Global `.card[onclick]:hover { border-color:var(--pri); transform:translateY(-1px) }` would fix across all — design-lead review required before landing.

## Hardcoded heuristic thresholds inside drill modals (surfaced 2026-04-21, cardFRB drill)
- `oDrRiskBudget` hardcodes `abs(f.a) > 0.2` as "intentional" cutoff (L5393). `_thresholds` global exists (cardThisWeek audit) — this kind of heuristic should read from `_thresholds.intentionalFactorSigma ?? 0.2` so it is tunable + consistent. Grep every drill modal for orphan constants on the next sweep.

## Palette duplication across tile + drill (surfaced 2026-04-21, cardFRB)
- cardFRB's 7-color palette `['#6366f1','#10b981','#a78bfa','#ef4444','#8b5cf6','#38bdf8','#ec4899']` is duplicated verbatim between tile (L2699) and drill (L5422). Any palette refactor must touch both sites together. Check other tile/drill pairs for the same duplication (likely candidates: cardMCR + its drill, cardUnowned + its drill).

## Completed audits (append-only — 2026-04-21 cardFRB)
- ✅ cardFRB (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = `Math.abs(f.c)` collapses sign on a risk-budget view; trivial fix queue of 9, non-trivial 5)
