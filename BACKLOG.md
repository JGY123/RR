---
name: RR Backlog
purpose: Append-only feature/work queue. Non-trivial items surfaced from audits, specs, and user direction. Not a roadmap — a capture surface. Priority is assigned when items get scheduled.
last_updated: 2026-04-23 (Batch 4 audited + fixes applied, pending review)
---

# RR Backlog

Non-trivial work items (anything that isn't a ≤5-line trivial fix). Trivial fixes are applied inline during their audit pass and closed via tag; they do not appear here.

**Conventions:**
- Append-only. Newest at top.
- Each item has: ID · title · origin · rough size · blockers · notes.
- When an item ships, move to "Shipped" section at bottom.
- When a batch of audits produces many items, group them under one header to avoid bureaucracy.

---

## B53–B60 · cardCorr non-trivials
Origin: `tile-specs/cardCorr-audit-2026-04-23.md`. Trivial fixes (themed colorscale via `--pri`/`--neg`/`--txth`, CSV export `exportCorrCsv()`, threshold externalization to `_thresholdsDefault.corrHigh/corrDiversifier`, pearson null-when-n<3 + "—" cell text, insight-factor `oDrF` drill links, localStorage save/restore of period/freq/facs, monthly dedupe inline-comment, min-history filter `>=3`, note popup, data-tip on live card-title, ghost `screenshotCard` PNG button removed) applied inline.

- **B53 · Active-vs-raw exposure policy (cross-tile)** — `rUpdateCorr` L2168 correlates raw exposure `e` but the Risk-tab UX implies **active** exposure (`e−bm`). Same conflation already confirmed at cardFacDetail L1764. PM gate: unify on one field, or expose `[Active|Raw]` toggle on both tiles. Whichever lands, the tile rename (B60) follows.
- **B54 · Date-aligned pearson** — current pearson aligns by array index, not by date. Any factor with missing observations on some weeks shifts the alignment for that pair. Build per-factor `{date→value}` Maps, intersect dates pairwise, then compute. ~25 LOC.
- **B55 · Half-triangle toggle** — symmetric matrix redundantly renders both halves. Add `[Full | Upper]` toolbar toggle; upper-triangle view halves visual noise on 20+ factor grids. ~10 LOC.
- **B56 · Factor-pair drill** — click a cell → open a modal with the two factors' exposure series + correlation over time. Re-uses `oDrF` rendering patterns. ~60 LOC + PM call on modal layout.
- **B57 · Full-screen variant (`renderFsCorr`)** — 20+ factors cramped at tile size. Mirror `renderFsScatter`. ~50 LOC.
- **B58 · Id on live Risk-tab card** — anonymous card at L3096 wraps the real heatmap; `id="cardCorr"` currently belongs to the ghost placeholder (L1299). Deferred pending B59 disposition. ~2 LOC once B59 lands.
- **B59 · Ghost tile disposition (PM gate)** — `#cardCorr` at L1299 is a named placeholder whose innerHTML is never set. Options: (a) delete, (b) promote to a second (Exposures-tab) correlation view, (c) rename ghost + give live card its own id. Blocks B58.
- **B60 · Tile rename (post B53)** — once active-vs-raw resolves, rename card title to match ("Active Factor Correlations" vs "Factor Exposure Correlations"). ~2 LOC.

---

## B45–B52 · cardAttrib non-trivials
Origin: `tile-specs/cardAttrib-audit-2026-04-23.md`. Trivial fixes (waterfall card id `cardAttribWaterfall`, tip+oncontextmenu on both card titles, `isFinite(f.imp)` filter, waterfall height cap `min(900,max(160,N*32)+20)` + overflow-y, themed bar colors via `--pos`/`--neg`, `data-col`/`data-sv` on attrib table, `plotly_click → oDrAttrib` on attrib bar, subtitle "Click any row or bar for time series") applied inline.

- **B45 · `full_period_imp` semantics** — parser emits a single "full period" impact column whose window is implicit. Surface the window (e.g. "trailing 13 weeks") in the subtitle + tooltip. PM gate on exact phrasing.
- **B46 · Week-selector awareness** — `rAttribTable` and `rFacWaterfall` silently show latest when `_selectedWeek` is set. Either hide with banner or render the selected-week slice. Same shape as B19/B43.
- **B47 · `classifyAttrib` heuristic → explicit enumeration** — regex-based factor-family classifier is fragile; move to explicit `FAC_GROUP_DEFS` lookup. Parallel to B10.
- **B48 · Two bar charts visual distinguishability** — `cardAttribWaterfall` (bars by factor contribution) and attrib bar inside `cardAttrib` render nearly identically. PM call: retitle, reorder, or merge. ~15 LOC + PM.
- **B49 · Factor-name escaping in onclick handlers** — `oDrAttrib('${name}')` breaks on names with apostrophes. Use `data-factor` attribute + delegated listener. ~10 LOC.
- **B50 · Top-20 / top-10 cap policy** — waterfall caps at 20, table caps at 10, tile-subtitle implies "full". Expose as `[Top 10 | Top 20 | All]` toggle. ~15 LOC.
- **B51 · Keyboard handler on attrib modal** — Esc-to-close + arrow-key nav through factor rows. Mirror holdings modal pattern. ~15 LOC.
- **B52 · Per-week drill on weekly-bars chart** — bars are clickable at week level but drill isn't wired. `plotly_click → selectWeek(bar.x)`. ~10 LOC.

---

## B39–B44 · cardMCR non-trivials
Origin: `tile-specs/cardMCR-audit-2026-04-23.md`. Trivial fixes (themed `--pri`/`--pos` via getComputedStyle, zeroline, PNG removed + `exportMcrCsv()` added, `plotly_click → oSt(ticker)`, tip+oncontextmenu note popup, top-bottom disclaimer in subtitle) applied inline.

- **B39 · MCR domain rename — paired with B20 (cardScatter)** — `h.mcr` is FactSet `%S` (stock-specific TE), not true marginal contribution to risk. Must land atomically across cardMCR + cardScatter + full-screen `renderFsScatter` + any sibling drill. PM gate: (a) rename to "Stock-Specific TE" / "Idiosyncratic Risk" end-to-end, or (b) document "MCR = stock-specific TE contribution" as PM shorthand. Recommend (a). Highest-value Batch 4 PM gate.
- **B40 · Negative %S narrative** — some holdings have negative `h.mcr` (short/hedge). Current tile renders them in green but without explanation. Add hover-text line "Negative MCR = position reduces portfolio TE (hedge/short)." ~5 LOC + PM copy.
- **B41 · Color-semantic unification** — tile colors top bars indigo (positive MCR) and bottom bars green (negative/risk-reducing); full-screen sibling inverts green/red. Same class of tile↔FS drift as cardScatter (B21). Unify or expose mode toggle.
- **B42 · Full-screen variant (`renderFsMCR`)** — 10 bars cramped on large monitors; siblings all have ⛶. Preserve ordering + axis labels. ~60 LOC.
- **B43 · Week-selector disclaimer** — MCR always renders latest holdings (no per-week MCR history). Subtitle hints at this but not visibly during historical week view. Add banner when `_selectedWeek` ≠ latest. ~10 LOC.
- **B44 · CSV extension beyond top-10** — `exportMcrCsv()` currently emits only the rendered top-10+bottom-10. Extend to full holdings MCR table with opt-in via second button or modal. ~10 LOC.

---

## B34–B38 · cardTreemap non-trivials
Origin: `tile-specs/cardTreemap-audit-2026-04-21.md` §7. Trivial fixes (note popup, theme tokens for active-sign color, `_treeDrill=null` on strategy switch) applied inline; toolbar-class adoption (B27 in audit) deferred as low-risk visual change for review marathon.

- **B34 · Full-screen variant** — 360px is cramped for Country/80-bucket views; siblings all have ⛶. Must preserve Dim/Size/Color/Drill state. ~60–100 LOC mirroring `renderFsCountryMap`.
- **B35 · Bucket → sector/country detail modal (`oDr`) route** — user clicking "Financials" expects the gold-standard sector drill. Needs PM UX call (shift-click? breadcrumb button? context menu?). ~20 LOC + PM decision.
- **B36 · CSV export of bucket table** — `{label, count, wt, active, te, avgRank}`. ~15 LOC + new `exportTreeBuckets()` helper.
- **B37 · Toolbar state persistence to localStorage** — `_treeDim/_treeSize/_treeColor/_treeDrill`. Pattern: `rr.tree.*`. PMs using daily expect sticky. ~10 LOC.
- **B38 · Populate `h.subg` in `enrichHold` using GROUPS_DEF** — the "Group" toggle button is silently dead because `h.subg` is never populated (parser maps from a non-existent `SEC_SUBGROUP` column). PM gate on GROUPS_DEF overlap resolution (first-match heuristic vs multi-attribution). ~6 LOC + PM call.

---

## B29–B33 · cardRanks non-trivials
Origin: `tile-specs/cardRanks-audit-2026-04-21.md` §7.

- **B29 · Consume FactSet pre-aggregated rank tables as source-of-truth** — parser extracts `ranks.{overall,rev,val,qual}[{q,w,bw,aw}]`; `normalize()` L612 discards and rebuilds from holdings. Unblocks REV/VAL/QUAL sibling tiles (high value). Adds holdings-vs-FactSet divergence telemetry. ~30–50 LOC across parser + normalize + rRnk. Highest-value cardRanks item.
- **B30 · "Unranked holdings" affordance** — holdings with `h.r==null` silently fall out of every quintile. Surface as 6th row or subtitle. ~10 LOC + PM call on format.
- **B31 · Robust tab navigation in `filterByRank`** — replace magic `querySelectorAll('.tab')[2]` + `setTimeout(100)` with symbolic lookup + proper render callback. ~15 LOC.
- **B32 · Filter preservation on rank-drill** — current `ah=[...cs.hold]` clobbers any pre-existing Holdings-tab sector/search filter. PM call on whether preserve or intentional reset. ~20 LOC.
- **B33 · Drill breadcrumb / exit affordance** — visible "Filtered: Q3 (clear)" chip on Holdings tab when navigated from rank-drill. ~15 LOC.

---

## B20–B28 · cardScatter non-trivials
Origin: `tile-specs/cardScatter-audit-2026-04-21.md` §11. Trivial fixes (isFinite filter, theme-aware colors, opacity, 9px label, zeroline, widen right margin, plotly_click→oSt drill, CSV export replacing PNG, note popup, rewritten hover + axis + tooltip text) applied inline. T11 "MCR" rename deferred as PM-gated.

- **B20 · "MCR" axis-label domain rename** — `h.mcr` is FactSet `%S` (stock-specific TE), NOT marginal contribution to risk. PM gate: (a) rename to "Stock-Specific TE" / "Idiosyncratic Risk" end-to-end, or (b) keep "MCR" as PM shorthand + document. Recommend (a). Ripples: card title L1254, tooltip, `renderFsScatter` L5632. Same bug likely on cardMCR — audit next.
- **B21 · Color-semantic unification tile ↔ full-screen** — tile colors by continuous active weight; full-screen colors by quintile rank. Two legit views but inconsistent. Add color-mode toggle `[Active|Rank|Sector]` in both. ~30–50 LOC.
- **B22 · Historical scatter (per-holding history)** — blocked: parser doesn't persist per-holding history. No week-selector drill possible. Parser change needed.
- **B23 · Quadrant annotations + portfolio-average crosshair** — requested in phantom spec 2026-04-13, never landed. Highest-PM-value chart addition. ~80 LOC.
- **B24 · Axis toggle (MCR/Return, Exp/Vol, ActWt/TE)** — blocked on per-holding return from FactSet. Phantom-spec item.
- **B25 · Label thinning + sizeref normalization** — `mode:'markers+text'` overlaps into mush on 80+ holdings. Thin to top-N by `|tr|`. PM call on N (~20–30). ~15 LOC.
- **B26 · Full-screen panel table → standard primitives** — `<table id>`, sortable `<th>`, CSV export. Primitives checklist applied to modal panel. ~20 LOC.
- **B27 · Shared `RANK_COLORS` palette helper** — `[#10b981, #34d399, #f59e0b, #fb923c, #ef4444]` duplicated in cardTreemap L2597 + FS scatter L5623 + FS panel L5659. Zero-behavior refactor. Folds into / supersedes earlier B9 (factor-palette canonicalization) — consolidate under one ticket when scheduled.
- **B28 · Phantom-spec quarantine rule** — institutionalize in AUDIT_LEARNINGS: any `tile-specs/*.md` whose contents begin with JSONL gets renamed `*.phantom-DATE.md` on sight. Two phantom specs identified so far (cardChars, cardScatter).

---

## B19 · cardFRB — week-selector awareness
- **Origin:** `tile-specs/cardFRB-audit-2026-04-21.md` §7
- **Size:** S (~20 lines)
- **Blockers:** none on latest week; historical weeks only have `hist.sum` — factor-contribution slices unavailable pre-current-week.
- **Notes:** When `_selectedWeek` ≠ latest, either hide FRB with a "(latest week only)" banner or render a greyed-out snapshot. Parallel to B4.

## B18 · cardFRB — hover/focus affordance on clickable card
- **Origin:** cardFRB audit §7
- **Size:** XS (~5 lines CSS)
- **Blockers:** none
- **Notes:** `.card[role=button]:hover{box-shadow:...}` + focus ring. Applies to cardFacButt too (same pattern).

## B17 · cardFRB / factor drill — sortable + drillable detail table
- **Origin:** cardFRB audit §7
- **Size:** S–M (~60 lines)
- **Blockers:** none
- **Notes:** `oDrRiskBudget()` currently renders static summary. Upgrade: sortable table with factor name / TE contribution / direction / share-of-factor-risk; row click → `oDrF(factorName)`. Pattern mirrors existing `rFacTable`.

## B16 · cardFRB — CSV export
- **Origin:** cardFRB audit §7
- **Size:** XS (~10 lines)
- **Blockers:** none
- **Notes:** Add `CSV` export button pattern from neighbor tiles; export `[factor, contribution, direction]`. Hidden-table + `exportCSV` pattern.

## B15 · cardRegions — Spotlight two-row header parity
- **Origin:** `tile-specs/cardRegions-audit-2026-04-21.md` §7
- **Size:** S (~25 lines)
- **Blockers:** decision on whether to expose `rankToggleHtml3` for regions (shared `_secRankMode` with sectors — may be appropriate or may be confusing).
- **Notes:** The reg-branch table at rWt renders R/V/Q as plain columns. The sec-branch wraps them with a "Spotlight / Wtd·Avg·BM" two-row header. Parity would make the ranks discoverable and mode-switchable.

## B14 · Region column-picker
- **Origin:** cardRegions audit §7
- **Size:** S (~30 lines)
- **Blockers:** none
- **Notes:** Regions table has no column-visibility toggle (unlike sectors). Add `applyRegColVis()` + a small gear/eye toggle. Low priority — regions have fewer columns.

## B13 · CMAP drift telemetry
- **Origin:** cardRegions + cardFacDetail audits (cross-tile)
- **Size:** S (~20 lines)
- **Blockers:** none
- **Notes:** Multiple tiles read CSS vars in JS (`getComputedStyle(...).getPropertyValue('--pos')`). If a token is removed/renamed the fallback silently activates. Add a startup check that warns to console if any expected var is empty.

## B12 · Sparkline active-vs-raw mode when no bench
- **Origin:** cardRegions audit §6 (inlineSparkSvg)
- **Size:** XS (~10 lines)
- **Blockers:** none
- **Notes:** `inlineSparkSvg` plots `.a` (active weight). For strategies with no/low bench coverage, `.a` ≈ `.p`. Tooltip or line styling could indicate this. Low priority.

## B11 · Profitability-decrease threshold → `_thresholds`
- **Origin:** cardFacDetail audit §7
- **Size:** XS (~3 lines)
- **Blockers:** none
- **Notes:** Hardcoded `-0.05` σ threshold for Profitability-warn span lives in `facRow`. Should move to `_thresholdsDefault` as `profitabilityWarnSigma`.

## B10 · Factor primary/secondary regex → explicit enumeration
- **Origin:** cardFacDetail audit §7 (AUDIT_LEARNINGS cross-tile)
- **Size:** XS (~5 lines)
- **Blockers:** none
- **Notes:** `/momentum/i.test(f.n)` in `rFacTable` is a regex workaround for FAC_PRIMARY set miss. Replace with explicit `FAC_PRIMARY` population at config time. Fragile as-is.

## B9 · Factor-group palette canonicalization
- **Origin:** cardFacDetail + cardFRB + cardFacButt audits (cross-tile)
- **Size:** S (~25 lines CSS + JS)
- **Blockers:** none
- **Notes:** Factor-group hex colors (indigo, amber/prof, etc.) are duplicated across `FAC_GROUP_DEFS`, `.fgp` CSS, cardFacDetail row borders, FRB labels. Consolidate into a `--fac-*` CSS-var suite + single source of truth in `FAC_GROUP_DEFS`. Shared CSS additions in this batch (`--prof`, `--fac-bar-pos/neg`) are a first step; finish the job.

## B8 · Weekly-append ingestion automation
- **Origin:** HANDOFF.md §7, user direction 2026-04-20
- **Size:** M (parser change + trigger wiring)
- **Blockers:** Redwood IT confirmation of server layout + drop-folder path
- **Notes:** `factset_parser.py --append existing.json new_week.csv`. Idempotent by `report_date`. Trigger TBD (file-watcher vs cron). Dashboard side auto-updates via existing `refreshDataStamp()` at dashboard_v7.html:709.

## B7 · Frontend Playwright smoke test
- **Origin:** HANDOFF.md §9 (gotchas / test coverage gap), SurpriseEdge lessons extraction
- **Size:** ~1 day
- **Blockers:** none
- **Notes:** Load a known `portfolio_data.json`, assert every `.card[id]` renders, assert zero console errors, assert every Plotly div has content. Unblocks confident auto-append rollout.

## B6 · Trend sparklines on countries / groups / regions
- **Origin:** AUDIT_LEARNINGS.md Known blockers
- **Size:** M (parser change)
- **Blockers:** parser doesn't persist `hist.country` / `hist.grp` / `hist.reg`
- **Notes:** Parallel blocker structure to B2. When one is unblocked, both should ship together.

## B5 · cardFacButt polish pass
- **Origin:** `tile-specs/cardFacButt-audit-2026-04-21.md` §7 non-trivial queue
- **Size:** S–M (~100 lines total)
- **Blockers:** none (PM preference on a couple)
- **Items:**
  - CSV / Copy-to-clipboard export (hidden-table + exportCSV pattern)
  - Honor sibling `cardFacDetail` Primary/All toggle (tile-to-tile state sync)
  - Factor-group coloring mode toggle (`facGrpColor(f.n)` already exists)
  - Duplicate or move full-screen ⛶ button onto this card (currently lives on neighbor)
  - PM call: within-card color scheme — bars+strip indigo/violet, or both pos/neg?

## B4 · cardThisWeek — week-selector-aware "Picked week" narrative
- **Origin:** User decision 2026-04-21 (Q2), cardThisWeek-audit §7 #3
- **Size:** S–M (~50–80 lines)
- **Blockers:** Two-layer history architecture — historical weeks only have `hist.sum` (TE/AS/Beta/H/cash), no sectors/holdings/factors. S2/S3/S4/S5 bullets can't render fully for historical weeks.
- **Notes:** User direction: "keep the current week up top and then show the picked week narrative in a way that is clearly marked". Approach: render existing `thisWeekCardHtml(s)` as always (latest). When `_selectedWeek` is set and is NOT the latest, render a second narrative block below, clearly banner-labeled "Picked week: April 14" or similar, with whatever subset of bullets the historical data supports (C1–C4 deltas, S1/S6 from `hist.sum`, skip S2–S5 or show as "(latest week only)").

## B3 · cardThisWeek — inline drill links on all 11 bullets
- **Origin:** `tile-specs/cardThisWeek-audit-2026-04-21.md` §7 #1
- **Size:** S (~30 lines)
- **Blockers:** none
- **Notes:** Every bullet subject has a natural existing modal. Pattern: wrap `<strong>` in `<a onclick="oSt(ticker)">` etc. with `cursor:pointer;text-decoration:underline dotted`.
  - S1 / C1 → `oDrMetric('te')`
  - S2 / S3 → `oDr('sec', name)`
  - S4 / C5 → `oSt(ticker)`
  - S5 → `oDrFacRiskBreak()`
  - S6 → `oDrMetric('cash')`
  - C2 → `oDrMetric('as')`
  - C3 → `oDrMetric('beta')`

## B2 · cardChars — historical sparklines
- **Origin:** Phantom spec salvage (task 5), `cardChars-audit-2026-04-21.md` §11 non-trivial #15
- **Size:** M (parser change + UI)
- **Blockers:** parser overwrites `sum.mc/roe/...` each pass. Needs per-week chars persistence: `s.hist.chars[metricName] = [{d,p,b},...]`
- **Notes:** Ships together with B6 if both unblocked by the same parser change.

## B1 · cardChars — grouping + deviation bars + top-3 + profile pills
- **Origin:** Phantom spec salvage (user direction 2026-04-21 Q1 — "take the main stuff that would still be applicable and add it to the queue then delete")
- **Size:** S (~165 lines total, all CSS+JS, no data change)
- **Blockers:** none
- **Items (still-applicable features extracted from deleted phantom spec):**
  - **Metric grouping** (Risk / Valuation / Growth / Quality) — add `CHR_GROUPS` config + classifier + group-header rows (~60 lines)
  - **Inline deviation bars** in Diff column (`.chr-devbar` CSS + bar-render inside cell, driven by `maxAbsDiff`) (~40 lines)
  - **Top-3 highlighting** (sort by `|diff/b|`, tag top 3 rows with `.chr-top3`) (~15 lines)
  - **Portfolio Profile summary pills** above table ("Growth-tilted · Small-cap bias · Quality overweight") — threshold-based classifier emitting 2–4 colored pills (~50 lines)
- **Discarded from phantom spec:**
  - Historical sparklines → separate item B2 (blocked on parser)
  - Misleading card-title tooltip → handled as trivial in Batch 1 fixes
  - `screenshotCard('#cardChars')` PNG button → removed as trivial in Batch 1 fixes

---

## Shipped
*(move items here with date + commit hash when they close)*
