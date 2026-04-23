---
name: RR Backlog
purpose: Append-only feature/work queue. Non-trivial items surfaced from audits, specs, and user direction. Not a roadmap — a capture surface. Priority is assigned when items get scheduled.
last_updated: 2026-04-21 (Batch 3 audited + fixes applied, pending review)
---

# RR Backlog

Non-trivial work items (anything that isn't a ≤5-line trivial fix). Trivial fixes are applied inline during their audit pass and closed via tag; they do not appear here.

**Conventions:**
- Append-only. Newest at top.
- Each item has: ID · title · origin · rough size · blockers · notes.
- When an item ships, move to "Shipped" section at bottom.
- When a batch of audits produces many items, group them under one header to avoid bureaucracy.

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
