# Tile Audit — Cross-Tile Learnings

**Purpose:** running ledger of patterns, gaps, and conventions discovered during per-tile audits. Every audit agent reads this FIRST (after the template). Every audit appends any insight that could apply to other tiles.

> Keep entries tight. If something applies to ≥2 tiles, it belongs here.

---

## Data shapes (canonical)
- `cs.sectors[]`, `cs.countries[]`, `cs.regions[]`, `cs.groups[]` — all share the 19-col aggregate layout: `{n, p, b, a}` + ORVQ ranks. Per SCHEMA_COMPARISON.md L66–L97, offsets are stable.
- `cs.hold[]` — per-holding; carries `{t, n, sec, co, p, b, a, mcr, tr, over, rev, val, qual, factor_contr}`. Region is derived at normalize-time: `h.reg = CMAP[h.co]||'Other'` (dashboard_v7.html:512) — any holding with `h.co` not in `CMAP` silently buckets to "Other" (same class of drift as cardCountry's COUNTRY_ISO3).
- Weighted-rank aggregation uses shared `rankAvg3(_secRankMode, ...)`. The mode is GLOBAL — toggling in one tile re-renders all ORVQ tiles.
- ~~`h.subg` is **declared** by the parser (factset_parser.py:544 `SEC_SUBGROUP→subg`) but FactSet CSV does not currently ship that column → `h.subg` is `undefined` in every strategy.~~ **UPDATED 2026-04-23 (cardGroups audit):** `h.subg` **IS populated** (~85% of non-cash holdings carry it on all 7 strategies in current data). FactSet's `SEC_SUBGROUP` column IS shipping. `h.subg` is authoritative and exclusive (each holding in exactly one subgroup, labels match `cs.groups[].n`). This unblocks cardTreemap Group-by toggle (one-line fix: `buckets[h.subg||'Other']`) and simplifies cardGroups rank aggregation + drill filtering (see Pattern C below).

## Shared state traps
- `_secRankMode` (Wtd / Avg / BM) is shared across cardSectors, cardCountry, cardGroups, cardRegions. Per-tile state would require splitting into `_secRankMode`, `_coRankMode`, `_grpRankMode`, `_regRankMode`. Deferred until a PM asks.
- **Hidden control trap:** cardRegions does NOT surface `rankToggleHtml3()` in its header — users must flip the toggle in cardSectors for it to affect cardRegions. The shared state is invisible from the tile's own UI. Verify each tile with rank columns either (a) renders its own toggle or (b) carries an inline hint explaining the shared control.
- **Drill-state leak across strategy/week switches:** `_treeDrill` (cardTreemap, L2589) is module-global and never reset by `normalize()`. If user drills into a bucket then switches strategy, stale state survives — guarded only by a `buckets[_treeDrill]` existence check (silent fallthrough to top-level + breadcrumb stays hidden). Audit every module-global UI-state var (e.g. `_treeDrill`, `_facView`, `_selectedWeek`, `_treeDim/Size/Color`) for reset semantics on strategy switch.
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

## Viz-tile (chart) checklist (derived 2026-04-21, cardTreemap)
Chart-only tiles (cardTreemap, cardScatter, cardMCR, cardFRB donut, cardFacButt) should have:
- [ ] Full-screen (⛶) button — cardScatter L1256, cardCountry L1199 are the model. cardTreemap is **missing** this. If the tile has a dense toolbar, the fs variant must preserve toolbar state.
- [ ] CSV export of underlying aggregate/bucket data (not just PNG) — cardTreemap, cardMCR currently offer PNG only.
- [ ] `plotly_click` / `plotly_treemapclick` wired to `oDr...` OR `oSt...` drill. Where a tile has multiple drill flavors (bucket-drill vs stock-drill), prefer modifier-key convention: plain click = in-tile drill, shift/alt-click = open sibling modal.
- [ ] `oncontextmenu="showNotePopup(event,'cardXxx');return false"` on the card-title. 3+ factor tiles have it; most chart tiles don't.
- [ ] Toolbar state (toggle groups, drill stack) persisted to localStorage under a `rr.<tile>.*` namespace. Every reload resetting toolbar state is a daily-user irritant.
- [ ] `THEME()` tokens (no hardcoded `#10b981`/`#ef4444`).

## Sort anti-patterns (found ≥3 tiles)
- `data-sv="${x??0}"` coerces null to 0 — sort collapses "no data" with "actual zero". Use `data-sv="${x??''}"` so nulls sort as empty strings. Seen in cardChars L1800, cardFactors L1761/1763/1764, cardRanks L1782.
- **Missing `data-sv` entirely** on region rank cells at dashboard_v7.html:1581. `sortTbl` silently falls back to `textContent` parsing — works for clean numbers but not for "—" placeholders. Re-check every `rankCell` helper for this when auditing sibling aggregation tiles.

## Viz-renderer pattern (no table)
- Plotly target divs (scatDiv, treeDiv, mcrDiv, frbDiv, facButtDiv, **regChartDiv**, etc.): guard `if(!data.length){ el.innerHTML='<p>No X data</p>'; return; }` — must write to the div, not silent return. `rRegChart` (L2283-2285) silent-returns and leaves stale prior render on strategy switch.
- Use `THEME().pos` / `THEME().neg` (extended 2026-04-20) instead of hardcoded `#10b981` / `#ef4444`. ~~Also `inlineSparkSvg` (L1438) hardcodes `#10b981`/`#ef4444` at L1451~~ **RESOLVED 2026-04-23:** `inlineSparkSvg` is tokenized at L1456-1457 (verified during cardRiskHistTrends audit). `rRegChart` hardcodes `rgba(99,102,241,0.85)` / `rgba(75,85,99,0.85)` port/bench colors (L2298/2301) — no `--pri`/`--bench` tokens currently exist. **cardTreemap** hardcodes both `#10b981`/`#ef4444` (L2629, L2644) and a 5-color rank palette at L2597.
- Click-to-drill parity: if a full-screen sibling wires `plotly_click → oDrX(name)`, the half-size tile should too. Seen missing on cardFacButt; full-screen `renderFsFactorMap` has it (L5542). `rRegChart` has NO click handler — regions chart is read-only, unlike sector/country charts.
- Apply `.filter(f => isFinite(f.a))` (or equivalent) before mapping chart inputs — Plotly silently coerces NaN/null to 0, hiding missing data.

## Palette fragmentation (escalating — surfaced 2026-04-21 cardFRB + cardTreemap)
Quintile rank coloring now has **four independent palettes**:
1. `rc(r)` helper → `var(--r1..--r5)` (design-tokenized, used by cardSectors, cardHoldings, stock modal).
2. `_treeRankColor(q)` (cardTreemap, L2595) → hardcoded `#10b981 / #34d399 / #f59e0b / #fb923c / #ef4444` — 5-step gradient.
3. cardFacButt factor-family palette (distinct purpose but same type of drift).
4. cardFRB 7-color slice palette (L2699 + duplicated at L5422 in drill).
Fix direction: expose a single `RANK_PALETTE = {1:'var(--r1)', ...}` consumed by `rc()` and any tile that hand-rolls quint colors. Any palette refactor must touch all sites — grep before landing.

## Half-built data pipelines (high-impact audit flag)
**Pattern:** render-side code reads `cs.hist.X[name]` or `h.X`, parser-side declares the key but never populates. Result: a column/chart/selector/dimension that is silently dead on every run. Found in:
- `cs.hist.reg` — read by `rWt` (L1589) and `oDr` (L3946); parser writes `{}` (factset_parser.py:838). Breaks: cardRegions sparkline column, cardRegions drill historical chart, drill range selector.
- `cs.hist.sec` (partial — parser writes `{}` at L837; populated only via monthly snapshots in some flows)
- `cs.hist.country`, `cs.hist.grp` — never declared, never populated; also block their tiles' trend features.
- `h.subg` — parser maps `SEC_SUBGROUP→subg` (L544) but FactSet CSV doesn't carry that column → cardTreemap Group toggle silently empty (L2610).
When auditing any tile with a sparkline / trend / historical drill / sub-category toggle, grep both the render-side access path AND the parser's output dict. If the dict is empty, the feature is shell-only. Treat as BACKLOG unless trivially bridgeable from existing data (e.g. `h.subg` can be derived client-side from GROUPS_DEF+SEC_ALIAS).

## Synthesis / insight tiles (narrative bullet cards)
- Pattern: `thisWeekCardHtml`, `riskAlertsBannerHtml`, `whatChangedBannerHtml`, `watchlistCardHtml`. Shared traits: rule-driven bullets, read `_thresholds`, silent-suppress when empty. Audit checklist: (1) every bullet subject should link to an existing drill modal (cardThisWeek currently has zero drill links — high-value gap); (2) fallback thresholds should read from `_thresholdsDefault`, not re-hardcoded `|| 8` / `|| 6` etc.; (3) add a tiny header tooltip linking to Settings so users can see what thresholds drove the bullet.

## Design conventions (cardSectors = gold standard, cardHoldings = gold standard)
- Threshold row classes: `|active|>5` → `thresh-alert`; `|active|>3` → `thresh-warn`
- Rank cells: right-aligned (`class="r"`), not center. **Unresolved delta across geographic tiles**: cardCountry + cardRegions both center-align ranks, cardSectors right-aligns. Flagged in cardCountry-audit §7 #5 and cardRegions-audit §7 #13. Either unify to right (sectors style) or document as intentional for geographic tiles.
- Spotlight (ORVQ) group: indigo tint `rgba(99,102,241,0.07)` background, left-border on first col. Region rank cells use `0.04` (lighter) — minor inconsistency.
- Spotlight header row: cardSectors has a two-row `<thead>` with `colspan`-grouped "Spotlight" header + inline `rankToggleHtml3()`. cardRegions/cardGroups lack this pattern — single-row thead, no inline toggle. Worth unifying if the shared `rWt` is ever refactored.
- Header tooltips: every numeric column should have `class="tip" data-tip="..."`. Region R/V/Q headers lack `data-tip` (dashboard_v7.html:1631) — only O has one.
- Density: `<th>`=10px, `<td>`=11px, rank cells tighter (`padding:4px 6px`)
- **Toggle-btn sizing floor:** 11px font-size, 4px 12px padding (global `.toggle-btn` class). cardTreemap toolbar inline-overrides to 9px/1px 6px — below the app's visual-density floor (L1266–1270). Audit every tile's toolbar for inline `font-size:` / `padding:` overrides of the shared class.

## Aggregation quirks (surfaced 2026-04-21, cardTreemap)
- Weighted-average formulas that fall back to `w=1` when a holding has `p<=0` (bench-only or short) silently mix weighted + simple aggregation within the same bucket. Seen in cardTreemap L2624 `(h.p>0?h.p:1)`. Same pattern risk in every tile computing weighted-avg ranks across `cs.hold[]` — prefer `Math.max(h.p,0)` and exclude zero-weight rows, OR use `h.b` as the bench-weight for weight-less rows.

## Redundant / clutter UX patterns
- Persistent header-text disclaimers that duplicate conditional ones: cardRegions renders "Region coverage may be low for US-focused strategies" ALWAYS at L1330, even though (a) for US-only strategies the card is hidden entirely, and (b) an amber <50%-coverage disclaimer already renders below the table (L1636) when actually relevant. Audit each tile for header text that repeats information already shown conditionally.

## Phantom-specs (audit trap)
- Some files in `tile-specs/` are raw JSONL transcripts of prior agent sessions, not hand-authored specs. They describe features an agent *claimed* to ship; many never landed. Always grep code for promised artifacts (CSS class names, helper fns) before treating the spec as live. Examples:
  - `portfolio-characteristics-spec.md` (2026-04-13) — 6/6 promises missing from code as of 2026-04-21.
  - `active-weight-treemap-spec.md` (2026-04-13) — is a raw JSONL transcript; its claimed "ghost benchmark overlay", "factor heat-layer inside sectors", and multi-level hierarchy (country→sector→holding) are NOT in production code. Treat as wishlist, not spec.

## Completed audits
- ✅ cardSectors (2026-04-19, tag `tileaudit.cardSectors.v1`)
- ✅ cardHoldings (2026-04-19, tag `tileaudit.cardHoldings.v1`)
- ✅ cardCountry (2026-04-20, tag `tileaudit.cardCountry.v1` + `.v1.fixes`) — trivial fixes applied (theme colors, tooltips, rank alignment, threshold classes, TE columns)
- ✅ cardChars (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; 6/6 spec-drift findings; trivial fix queue of 7 pending)
- ✅ cardThisWeek (2026-04-21, audit only — GREEN/YELLOW/GREEN; top gap = no inline drill links on any bullet; trivial fix queue of 5, non-trivial 4)
- ✅ cardRegions (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = B6 blocker still valid, parser L837-838 hardcodes `hist.reg:{}`; trivial fix queue of 8, non-trivial 4)
- ✅ cardFRB (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = `Math.abs(f.c)` collapses sign on a risk-budget view; trivial fix queue of 9, non-trivial 5)
- ✅ cardTreemap (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = D1 "Group" toggle silently dead (`h.subg` never populated); trivial fix queue of 4, non-trivial 6)

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

## Domain-term labeling errors (surfaced 2026-04-21, cardScatter audit)
- **`h.mcr` is mislabeled as "MCR" / "Marginal Contribution to Risk".** Per CLAUDE.md and factset_parser.py L501, `h.mcr` is the FactSet `%S` column — **stock-specific TE component**. "Marginal Contribution to Risk" (∂σ_portfolio/∂w_i) is a *different* quantity that FactSet does not provide in this column. Mislabeled on cardScatter card title (L1254), axis title (L2585), full-screen axis (L5632 — partial: "MCR (Stock-Specific TE)" at least hints), and card-title tooltip (L1254). Very likely also wrong on cardMCR — verify on next audit. PM-facing risk-domain accuracy bug, not a styling issue.
- **Tile↔full-screen color-semantic drift:** cardScatter tile colors dots by continuous `h.a` (active weight); `renderFsScatter` colors by discrete `h.r` (quintile rank). Two views of the same data, two different narratives. Worse than palette drift — this is *semantic* drift. Either unify source field or expose an explicit color-mode toggle in both.
- **Bubble-size drift:** `rScat` uses linear `h.p*3`; `renderFsScatter` uses `sqrt(h.p)*9`. Extract a shared `bubbleSize(p)` helper. Neither caps outliers — one 30%-weight holding visually dominates in both.
- **Rank-palette duplication (third site found):** `[#10b981, #34d399, #f59e0b, #fb923c, #ef4444]` at cardTreemap L2597 (`_treeRankColor`), FS scatter L5623, FS panel L5659. Extract shared `RANK_COLORS` constant — zero-behavior-change refactor, best candidate for first shared constant to introduce.
- **Missing `plotly_click` drill on `rScat`** while `renderFsScatter` has it (L5637 → `_fsScat_selectHold`). Same click-parity anti-pattern already surfaced in cardFacButt and cardRegions (`rRegChart`).

## Panel tables inside modals (surfaced 2026-04-21, cardScatter FS)
- `renderFsScatter` renders a holdings table inside the FS side panel at L5666 with no `<table id>`, no sortable `<th>`, no CSV export — the standard primitives checklist stops at the tile boundary but should cascade into modal panels too. Apply primitives to any modal that renders tabular data.

## Completed audits (append-only — 2026-04-21 batch 3)
- ✅ cardScatter (2026-04-21, audit only — **RED/RED/YELLOW**; top finding = `h.mcr` mislabeled as "MCR" across card title + axis + FS axis + tooltip; missing `plotly_click` drill; color-semantic drift tile↔FS; 2nd phantom spec found (risk-return-scatter-spec.md, 6/7 promises missing); trivial fix queue of 11, non-trivial/backlog 9 (B20–B28))

## Parser-populated / normalize-discarded pattern (NEW — surfaced 2026-04-21, cardRanks)
New shape of half-built pipeline distinct from the `hist.X:{}` pattern: parser writes real data → `normalize()` in dashboard overwrites it with a locally-computed derivation. Found in:
- `s.ranks` — parser produces `{overall:[{q,w,bw,aw}],rev:[...],val:[...],qual:[...]}` (factset_parser.py:L751–L756) carrying FactSet's pre-aggregated quintile W/BW/AW. `normalize()` L612–L613 discards the dict and rebuilds `s.ranks` as `[1..5].map(re-aggregate from st.hold)`. Net effects: (1) FactSet's authoritative quintile totals never displayed, (2) REV/VAL/QUAL quintile data wholly unused (no tile consumes it), (3) holdings with `h.over==null` silently drop out of all quintiles because `h.r` stays null. See cardRanks audit B29.

Audit heuristic: after tracing a tile's `cs.X` path, grep `normalize()` (and `loadData` / `_origNormalize`) for any `st.X =` assignment. A match = Pattern B; check whether the parser's version would have been richer/more-authoritative than the recomputation.

## Filter-navigation drill pattern (fragile — surfaced 2026-04-21, cardRanks)
cardRanks is the only audited tile that drills by **tab-navigation-with-filter** rather than opening a modal. `filterByRank(rank)` at L1802 activates the Holdings tab via magic index `document.querySelectorAll('.tab')[2]` and sets the rank dropdown via `setTimeout(100)`. Three fragilities:
1. **Magic tab index** — silently filters wrong tab if tab order changes.
2. **setTimeout race** — if Holdings render > 100ms, dropdown value-set fires against a missing node; filter still correct but visible dropdown desyncs.
3. **Filter-clobber** — `ah=[...cs.hold]` resets any pre-existing sector/search filter on Holdings, silently losing user context.
If other tiles adopt this pattern (cardScatter click → filter Holdings by ticker, etc.), centralize a `navigateToHoldings({rank?,sector?,ticker?,preserve:boolean})` helper. Also add a "Filtered by: X (clear)" chip on Holdings tab so users see + exit the filter state.

## Rank-color palette fragmentation (escalating — now 5+ sites, surfaced 2026-04-21 cardRanks + prior cardScatter/Treemap)
Updated tally — quintile rank coloring has at least 5 independent palettes:
1. `rc(r)` helper L492 → `var(--r1..--r5)` tokenized (cardSectors, cardHoldings, cardRanks label, stock modal some rows).
2. `_treeRankColor` L2595 → hardcoded 5-color gradient.
3. `rRankDist` L3926 — reads tokens via getComputedStyle-on-var, OK but fragile (if a user renames a var it breaks).
4. `rScat` / `renderFsScatter` L5623 — hardcoded 5-color, same hexes.
5. `renderHoldTab` L5954 — hardcoded 3-step (`#059669 / #dc2626 / #d97706`, non-token).
6. Stock-detail modal L5659/L5724 — hardcoded 3-step different hexes.
Fix direction: one `RANK_COLORS = [null,'var(--r1)','var(--r2)','var(--r3)','var(--r4)','var(--r5)']` consumed everywhere. Any palette refactor must touch all 5+ sites — grep before landing.

## Completed audits (append-only — 2026-04-21 batch 3 continued)
- ✅ cardRanks (2026-04-21, audit only — YELLOW/YELLOW/YELLOW; top finding = parser `ranks.{overall,rev,val,qual}` discarded in normalize() L612; REV/VAL/QUAL tiles never exist; unranked holdings drop silently; fragile tab-nav drill; trivial fix queue of 9, non-trivial 5 → B29–B33)

## Ghost-tile anti-pattern (NEW — surfaced 2026-04-23, cardCorr)
Named card with `id="..."` exists in the DOM but its innerHTML is never set by any renderer — a visible placeholder that silently renders empty. The live version of the tile renders inside a neighbor card (often an anonymous Risk-tab container with no id). Seen: `#cardCorr` at L1299 (placeholder, never populated) while the real factor-correlation heatmap renders at L3096 inside an anonymous Risk-tab `<div class="card">`. Consequence: (a) users see an empty-looking card; (b) audits mis-target the placeholder assuming id = live tile; (c) `screenshotCard('#cardCorr')` + any other id-addressed helpers hit the wrong element.
Detection heuristic: after locating a tile's render function, grep for `getElementById('<tileId>')` or `#<tileId>` in JS; if none of the render functions write to the id-addressed node, it's a ghost. Audit next: any tile whose card shell sits in a different tab than where its data renders.

## Anonymous Risk-tab cards (NEW — surfaced 2026-04-23, cardCorr)
Multiple Risk-tab cards have no `id` at all — the real renderer targets a child chart div (e.g. `corrChartDiv`, `mcrDiv`) rather than the card wrapper. Makes tile-audit targeting ambiguous, blocks `oncontextmenu="showNotePopup(event,'...')"` on the card-title (needs a card id to key notes), and hides tile identity from `screenshotCard` / CSV-export helpers. Assign stable `id="cardXxx"` to every live card on the Risk tab as a follow-up sweep.

## Active-vs-raw series conflation (NEW — surfaced 2026-04-23, cardCorr; now ≥2 sites)
Confirmed at **two** sites:
1. cardFacDetail L1764 — `facRow` reads `f.e` (raw exposure) for some computations while the tile narrative implies `f.a` (active `e−bm`).
2. cardCorr L2168 — `rUpdateCorr` correlates raw exposure `e` but Risk-tab UX implies active.
Both tiles are PM-gated on the same decision: policy of "active" vs "raw" for factor-exposure-derived views. Either unify globally or expose `[Active|Raw]` toggle. Cross-tile: any factor tile reading `f.e` directly deserves an audit checkmark for this conflation.

## Completed audits (append-only — 2026-04-23 batch 4)
- ✅ cardMCR (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top finding = same `h.mcr` = stock-specific TE mislabel as cardScatter, paired rename PM gate (B39 ↔ B20); 6 trivial applied, 6 non-trivial → B39–B44)
- ✅ cardAttrib (2026-04-23, audit only — YELLOW/YELLOW/YELLOW; top finding = waterfall card id-less (fixed), Impact column sort broken (fixed via data-sv), no `plotly_click` on either bar chart (fixed on attrib bar, weekly-bars deferred); 10 trivial applied, 8 non-trivial → B45–B52)
- ✅ cardCorr (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top finding = ghost tile at `#cardCorr` L1299 while live heatmap renders in anonymous Risk-tab card L3096; active-vs-raw conflation 2nd site; 9 trivial applied, 8 non-trivial → B53–B60)

## Data-pipeline layering patterns (codified — surfaced 2026-04-23, cardGroups)
Three distinct layering anti-patterns in the parser↔normalize↔render chain. Every future audit should grep for all three:
1. **Pattern A — "`hist.X:{}`":** parser writes empty dict; render can't display. Sites: `hist.reg`, `hist.grp`, `hist.country` (never declared); `hist.sec` partial. Result: sparkline / trend / historical-drill columns are shell-only. Flagged in Known Blockers.
2. **Pattern B — "parser-populated → normalize-discarded":** parser fills a field; dashboard `normalize()` overwrites with a local recomputation. Site: `s.ranks` — parser emits pre-aggregated FactSet quintile totals, `normalize()` L612 discards and rebuilds from holdings. Symptoms: FactSet authoritative values never displayed; parallel subfields (REV/VAL/QUAL quintiles) become orphaned.
3. **Pattern C — "render-side re-derivation from wrong config" (NEW):** parser fills correctly AND holdings carry authoritative labels, yet render reconstructs the mapping locally via a legacy config that disagrees with source. Site: `rGroupTable` L1895–L1918 recomputes ORVQ ranks via `GROUPS_DEF + SEC_ALIAS` (non-exclusive: Info Tech → both GROWTH CYCLICAL and GROWTH) while holdings carry `h.subg` (exclusive bucketing matching `cs.groups[].n`). Detection heuristic: if render-side code has a config constant whose entries overlap with fields already on the data model (here GROUPS_DEF vs `h.subg`), grep every usage for consistency with source. Decide which is truth and enforce.

## Active-vs-raw factor-exposure conflation (ESCALATED — 3 sites, surfaced 2026-04-23 cardRiskFacTbl)
Now confirmed at **3 sites**:
1. cardFacDetail L1764 — `facRow` reads raw `f.e` while tile narrative implies active `f.a`.
2. cardCorr L2168 — `rUpdateCorr` correlates raw `e` while Risk-tab UX implies active.
3. cardRiskFacTbl (WITHIN-ROW divergence): Exposure cell L3152 renders `f.a` (active), Trend sparkline L3149 falls through to raw `h.e` whenever `h.bm==null` — **which is always on the riskm path** because parser `_collect_riskm_data` L468 hardcodes `bm: None`. Same row, two different readings. Drill annotation at L3573 self-contradicts with trace (annotation used `last.e||last.a`, trace plots `e−bm`).
Escalation: 3 sites moves this from "watch" to **cross-tile refactor** (BACKLOG B73, supersedes B53). Parser-side complementary fix: populate `bm` in riskm path via `bm = e − a` algebra (one-line parser change at L468).

## Sign-collapse on risk-budget / MCR views (ESCALATED — 4 sites, surfaced 2026-04-23 cardRiskFacTbl)
`Math.abs(f.c || 0)` erases direction of factor TE contribution. Confirmed at **4 sites**:
1. cardFRB L2696
2. `oDrRiskBudget` L5389
3. Risk Decomp Tree L2770
4. cardRiskFacTbl MCR-to-TE L2996 + drill KPI L3526
Pattern is now widespread enough that a shared helper (`mcrSigned(f, totalTE)`) and a shared "colorize risk-add vs diversifier" convention should be adopted. `Math.abs` reserved only for strict-magnitude views (Top-|MCR| bars). BACKLOG B74 (supersedes scope of earlier cardFRB items).

## Parser dual-path for factor exposures (NEW — surfaced 2026-04-23, cardRiskFacTbl)
`factset_parser.py` has two paths that populate `exposures[fname]`:
1. `_collect_riskm_data` L460-469 — always sets `bm: None`, stores `c_val` as both `c` and `e` (port exposure).
2. `_build_factor_list` L847-865 — relies on whatever `exposures` was set to for the current riskm entry, so `bm` stays None. But `f.a` (active) DOES get populated (L857) from `active_factor_cols`.
Net: `f.a` reliable; `hist.fac[*][*].bm` unreliable (always None on riskm path). Any render consuming `hist.fac[*][].bm` silent-falls-through to raw. **One-line parser fix** (L468): `bm = e - a if a is not None else None`. Lands with B73 active-vs-raw refactor.

## Week-selector trap — extends to synthesis/trend tiles (surfaced 2026-04-23, cardRiskHistTrends)
Beyond detail tables (cardSectors/Regions/Countries silently-latest by two-layer-history design), **any tile computing `cur = hist[length-1]` / WoW deltas against `hist[length-2]` silently ignores `_selectedWeek`**. Seen: cardRiskHistTrends L2923 (value row + delta arrow) — fixed by index lookup `idx = _selectedWeek ? hist.findIndex(h=>h.d===_selectedWeek) : hist.length-1`. Even when the underlying chart shows all history, a vertical marker at `_selectedWeek` is still missing. Audit every new tile with `hist.sum` access for this.

## Mini-chart (sparkline) sub-checklist (NEW — surfaced 2026-04-23, cardRiskHistTrends)
Supplements "Viz-tile chart checklist" for the sparkline subset:
- [ ] Per-metric `hovertemplate` with units (`%{y:.2f}%` for TE/AS, `%{y:.3f}` for Beta, `%{y:d}` for count metrics).
- [ ] `rangemode` reviewed per-metric — `'tozero'` crushes ref-1-centered metrics like Beta to a flat line; prefer `'normal'` for Beta/AS, keep `'tozero'` for TE/Holdings.
- [ ] Keyed child chart div ids (not anonymous) — enables targeted re-render.
- [ ] Delta-arrow noise floor calibrated — `>0.05` on pp metrics, `>0.005` on Beta. `>0.01` always fires.
- [ ] Theme-token fills via `getComputedStyle(document.body).getPropertyValue('--x')` + a tiny `hex2rgba()` for alpha-layered fills.

## Drill symmetry across metric cards (NEW — surfaced 2026-04-23, cardRiskHistTrends)
When a multi-metric card wires 3-of-N metrics to drill modals and leaves 1 undrillable (`drill:null`), the asymmetry (some cursor:pointer, some cursor:default) reads as broken. Either add the missing drill (generic `oDrMetric(key)` usually accepts arbitrary keys with `hist[key]` if `labels[key]` + `units[key]` exist) or make the intentional omission visible (annotate the undrillable card `title="Drill not available"`). Seen fixed on cardRiskHistTrends Holdings card (`drill:"oDrMetric('h')"`).

## Dataset-driven audits are high-ROI (NEW — surfaced 2026-04-23, cardGroups)
The cardGroups RED finding (ranks off by up to 2 quintile points) was ONLY visible by running numeric comparison against `latest_data.json`. Prior aggregate-tile audits (sectors/country/regions) did not run a data probe and did not catch analogous issues. **Heuristic:** always run at least one "parser value vs rendered value" spot-check when the render re-computes from holdings data that parser already aggregated. Add to the audit skill template.

## Completed audits (append-only — 2026-04-23 batch 5)
- ✅ cardGroups (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top finding = render recomputes ORVQ ranks via non-exclusive `GROUPS_DEF + SEC_ALIAS` taxonomy, silently mis-reporting HARD CYCLICAL as Q1 when FactSet says Q3; dead `oDrGroup` drill filter fixed inline via `h.subg` switch; `h.subg` populated (contradicts earlier ledger — now corrected); 10 trivial applied, 8 non-trivial → B61–B68)
- ✅ cardRiskHistTrends (2026-04-23, audit only — YELLOW/YELLOW/YELLOW; top finding = `_selectedWeek`-blind cur/prev (fixed via idx lookup) + 4 tokenizable Plotly colors (fixed) + Holdings drill asymmetry (fixed via `oDrMetric('h')`); 8 trivial applied, 4 non-trivial → B69–B72)
- ✅ cardRiskFacTbl (2026-04-23, audit only — **RED/YELLOW/YELLOW**; top findings = active-vs-raw 3rd site in-row between Exposure cell and Trend sparkline (parser L468 `bm: None` root cause); sign-collapse 4th site on MCR-to-TE; header mislabel Exposure → Active Exposure (fixed inline); 7 trivial applied, 3 deferred pending B73/B74 PM policy, 6 non-trivial → B73–B78)
