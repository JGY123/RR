---
name: RR Backlog
purpose: Append-only feature/work queue. Non-trivial items surfaced from audits, specs, and user direction. Not a roadmap — a capture surface. Priority is assigned when items get scheduled.
last_updated: 2026-04-21
---

# RR Backlog

Non-trivial work items (anything that isn't a ≤5-line trivial fix). Trivial fixes are applied inline during their audit pass and closed via tag; they do not appear here.

**Conventions:**
- Append-only. Newest at top.
- Each item has: ID · title · origin · rough size · blockers · notes.
- When an item ships, move to "Shipped" section at bottom.

---

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
