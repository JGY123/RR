# RR Refactor — Cumulative Impact Summary

**Span:** 2026-05-01 → 2026-05-04 (4 days)
**Baseline:** `presentation-2026-05-01-shipped` (commit `3b10805`)
**Latest:** `refactor.20260504.1115.kpi-stat-card`

---

## TL;DR

Started: dashboard with critical TE bug, ACWI/IDM 27/92-week parsing gaps, scattered inline chrome, no design system, week-selector partially flowed.

Ended: data-correct, 4-year ACWI history recovered, 30/30 tiles using uniform chrome helper, 10 canonical CSS classes, design tokens, lint-enforced week-flow, scroll preservation, Universe pill UX, Country fullscreen with Map/Heat/Table tabs, 3 tile audits in progress.

**Total commits: 50+ · Total tags: 25+**

---

## Day 1 (2026-05-01) — Live during presentation

### 4 critical fixes during the demo
1. Sector/Country/Group **TE Contrib** = section-aggregate (was double-counting holdings sum, summed to 137% > 100% on ACWI)
2. **Week-flow propagation** to TE/MCR/ORVQ ranks (was: weights changed but risk stayed static)
3. **Parser jagged-CSV fix** — recovered ACWI +27wk, IDM +92wk of historical data (header-undercount of "Period Start Date" markers)
4. **Per-week sector/country/region/group/chars** flow (parser bug that silently dropped trailing weekly data)

### 11 refactor phases (A–K) shipped same day post-demo
- **A** Audit (REFACTOR_AUDIT.md)
- **B** `tableColHide` framework + cardSectors canary
- **C** Sweep `tableColHide` across 8 tables (uniform ⚙ Cols)
- **D** `tileChromeStrip()` helper (then incremental migration over Days 2-4)
- **E** Country fullscreen Map fix + Map/Heat/Table tabs
- **F** Universe selector audit + UX shipping (Port-Held / In Bench / All)
- **G** Scroll preservation on `changeWeek` / `setImpactPeriod`
- **H** Factor Detail + Risk + ContribBars + RiskFacTbl flow per-week
- **I** WoW row tooltips for name disambiguation
- **J** `lint_week_flow.py` static lint (wired into smoke_test.sh)
- **K** Design polish — tokens + 10 canonical CSS classes

### Organization spine built
- `SESSION_GUIDE.md` — first-5-min checklist for any new session
- `AGENTS.md` — subagent runbook + briefing template
- `dev_dashboard.html` — visual project state at a glance
- `REFACTOR_PLAN.md` — phase plan + checkpoint log
- `UNIVERSE_AUDIT.md` — Phase F findings
- `DESIGN_AUDIT.md` — visual inconsistency audit (subagent output)

---

## Day 2 (2026-05-03) — Tier-1 migration sweep

- 5 Tier-1 tiles migrated to `tileChromeStrip` (cardSectors canary + cardGroups + cardRegions + cardCountry + cardAttrib)
- 17 HTML-context `#94a3b8` greys swept to `var(--textDim)`
- Backtick-in-HTML-comment bug pattern memorialized

---

## Day 3 (2026-05-04 morning) — Phase D MIGRATION COMPLETE

- 25 more tile migrations: cardThisWeek, cardWeekOverWeek, cardChars, cardFacRisk, cardFacDetail, cardRiskFacTbl, cardTreemap, cardUnowned, cardWatchlist, cardTEStacked, cardBetaHist, cardFacContribBars, cardRiskByDim, cardFacHist, cardCorr, cardRiskHistTrends, cardRiskDecomp, cardHoldRisk, cardRankDist, cardTop10, cardFacButt, cardRanks, cardHoldings, plus empty-watchlist branch
- **Total: 30/30 tiles using `tileChromeStrip`**
- Plotly `color:'#94a3b8'` → `THEME().tick` (5 occurrences)
- cardFacRisk KPI strip → `.stat-card` (6 inline boxes)

---

## Day 4 (2026-05-04 afternoon) — Tile audit cadence resume

- 3 parallel `tile-audit` subagents (cardWeekOverWeek / cardHoldRisk / cardRiskByDim)
- REFACTOR_AUDIT.md updated with post-migration state
- This document (REFACTOR_IMPACT.md)

---

## What features now ship from one place

| Feature | One-line edit point | Tile reach |
|---|---|---|
| Standard chrome cluster | `tileChromeStrip()` (line ~1503) | 30 tiles |
| Column hide/show | `tableColHidePanelHtml()` (line ~1342) | 8 tables |
| Tile-level Hide × | `toggleTileHide()` + `.tile-btn` | 30 tiles |
| Reset View ↺ | `resetTileToDefaults()` + `.tile-btn` | 30 tiles |
| Full Screen ⛶ | `openTileFullscreen()` + per-tile registration | 30 tiles |
| Reset Zoom ⤾ | `resetPlotZoom()` + `.tile-btn` | All chart tiles |
| Universal "no data" | `.empty-state` | 9 places |
| KPI/stat tile | `.stat-card` + sub-classes | 8 places |
| Section eyebrow label | `.section-label` | 17 places |
| Modal close button | `.modal-close-btn` | 10 places |
| Universe filter pill | `setAggMode` + status strip | Header |
| Per-week data flow | `_wSec`, `_wCtry`, `_wReg`, `_wGrp`, `_wInd`, `_wChars`, `_wFactors`, `getSelectedWeekSum`, `getDimForWeek` | All tiles via lint enforcement |
| Scroll preservation | `_withScrollPreserved()` | Week + period selectors |

---

## What's enforced (won't silently regress)

- **`lint_week_flow.py`** — wired into smoke_test.sh, fails CI on any direct `cs.X` access in render functions
- **JS parse check** — Node-based syntax check on every commit (caught backtick-in-comment bugs)
- **Anti-fabrication policy** — lessons from April crisis carried forward (LESSONS_LEARNED.md)
- **Git tag discipline** — `working.YYYYMMDD.HHMM.<descriptor>` before risky edits, `refactor.YYYYMMDD.HHMM.phase-X` after each phase

---

## Outstanding (queued for future sessions)

1. **Per-tile audit cadence** — Tier-2 tiles via `tile-audit` subagent (3 in progress as of 2026-05-04)
2. **Drill modal migration** — `oDr`, `oDrMetric`, `oDrCountry`, `oSt` etc. still have inline chrome
3. **Spacing scale adoption** — sweep remaining hardcoded `padding: Xpx` to `var(--space-*)` (low priority)
4. **Plotly theme-flip support** — auxiliary chart configs that still use hardcoded hex (intentional sentinel colors mostly)
5. **Stage tag for stakeholder review** — `presentation-2026-05-XX` tag whenever stable

---

## Wider rollout readiness

The design system + organization spine is in place. Next moves for production:

- **Multi-user deployment** — Linux server + nginx + systemd timer. localStorage prefs are already isolated.
- **Per-firm theming** — CSS variables drive the palette. Add a theme picker.
- **API mode** — switch FactSet CSV ↔ API endpoint via one accessor.
- **New-tile onboarding** — declarative `tileChromeStrip` config means a new tile is "write a config" not "copy 200 lines."

---

**The dashboard is now organized for change.** Future feature work compounds rather than fragments.
