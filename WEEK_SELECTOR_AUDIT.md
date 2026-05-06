# Week Selector Flow — Audit Report

**Drafted:** 2026-05-06
**Trigger:** user has flagged 4× across the session arc that "the selector changes weights but risk stays static" and "factor TE breakdown in sector is empty for historical weeks." `lint_week_flow.py` reports clean (no direct `cs.X` access in render functions), so the bug must lie elsewhere. This audit reconciles the lint result with the user's reality.

**Method:** catalogued all 40 tile-level render functions; cross-checked each against (a) the available week-aware helpers (`_wSec`, `_wReg`, `_wCtry`, `_wGrp`, `_wInd`, `_wChars`, `_wFactors`, `getSelectedWeekSum`, `getPctSpecificForWeek`) and (b) the underlying data architecture in `data/strategies/<ID>.json`.

---

## TL;DR

The lint is correct — the code IS using week-aware helpers wherever the data architecture allows it. The user's complaint is also correct — there's a real UX gap. **Reconciliation:** roughly 1/3 of the dashboard's tiles SHOW values that genuinely cannot change per-week because the underlying data shape doesn't support it (holdings-based decompositions). Today these tiles silently render latest data when historical week is selected, with no per-tile signal to the user. The global hist-week banner says "summary metrics only" but it's at the top of the tab — easy to miss when scrolling through 10 tiles.

**The fix is UX, not data flow:** add a small "Latest holdings" pill to every tile whose values can't legitimately follow the week selector, so users see at a glance which numbers refreshed and which didn't.

---

## 1. Three categories of tile

### Category A — Per-week aware (data + code) ✅

Data is shipped per-week; code uses week-aware helpers; selector flows correctly.

| Tile | Helper used | Underlying data |
|---|---|---|
| TE / AS / Beta / Holdings sum cards | `getSelectedWeekSum()` | `cs.hist.sum[]` |
| Idio / Factor % sum cards | `ws.pct_specific` + `getPctSpecificForWeek()` (Σ\|sector mcr\|) | `cs.hist.sec[*].mcr` per week |
| cardSectors (Sector Active Weights) | `_wSec()` → `getDimForWeek('sec')` | `cs.hist.sec` per week |
| cardSectors TE / Stock TE / Factor TE columns | `d.tr` / `d.mcr` from per-week dim entry | Section-aggregate per week |
| cardRegions | `_wReg()` | `cs.hist.reg` per week |
| cardCountry table + map | `_wCtry()` | `cs.hist.ctry` per week |
| cardGroups | `_wGrp()` | `cs.hist.grp` per week |
| cardIndustries | `_wInd()` | `cs.hist.ind` per week |
| cardChars | `_wChars()` | `cs.hist.chars` per week |
| cardFacDetail (Factor table) | `_wFactors()` | `cs.snap_attrib[*].hist` per week |
| cardFacContribBars | `_wFactors()` | same |
| cardFacHist (factor exposure history) | reads `cs.hist.fac` directly | `cs.hist.fac` per week |
| cardTEStacked (TE decomposition over time) | `getPctSpecificForWeek` per week + F12(a) 3-tier resolver | `cs.hist.sum` + `cs.hist.sec` |
| cardBetaHist | `_selectedWeek` for marker | `cs.hist.sum.beta` |
| cardCashHist | `_selectedWeek` for marker | `cs.hist.sum.cash` |
| cardRiskHistTrends | uses full `cs.hist.sum` (time series tile — period-spanning by design) | `cs.hist.sum` |
| cardWeekOverWeek | finds `_selectedWeek` in `cs.hist.sum`, shows that week vs prior | `cs.hist.sum` |
| cardThisWeek (state alerts) | `getSelectedWeekSum()` | `cs.hist.sum` per week |
| cardCorr (factor correlation matrix) | computes from `cs.hist.fac` (always full history; period selector independent of week) | `cs.hist.fac` |

**Verdict:** these all flow correctly. No code changes needed.

### Category B — Cannot flow per-week (data architecture) 🔴

The dashboard architecture (`CLAUDE.md` §"Two-Layer History Architecture") explicitly documents: per-holding details (`hold[]`, `factor_contr` per holding, `ranks`) are **latest-only** — there is no per-week per-holding ledger. This is by design: a 3-year per-holding ledger across 6 strategies would be 50-100GB of JSON.

When user picks historical week, these tiles silently render latest data:

| Tile | Latest-only fields used | Why no per-week data |
|---|---|---|
| cardHoldings | `cs.hold[]` directly | no historical holdings ledger |
| cardWatchlist | `cs.hold[]` | same |
| cardHoldRisk | `cs.hold[]` (active wt + idio MCR) | same |
| cardScat (TE × Active Wt scatter) | `cs.hold[]` | same |
| cardTreemap (holdings treemap) | `cs.hold[]` | same |
| cardTop10 (concentration) | `cs.hold[].p` (port wt) | same |
| cardRanks (Spotlight quintile dist) | `cs.hold[].r` + per-quintile factor contribs from `cs.hold[].factor_contr` | per-holding `factor_contr` is latest-only |
| cardRankDist | `cs.ranks` (derived from cs.hold) | same |
| cardHoldConc | `cs.hold[]` top-10 by weight | same |
| cardRiskByDim (TE by Country/Currency/Industry) | `cs.hold[]` bucketed by classification | per-holding `tr` × per-holding classification — both latest only |
| cardUnowned (top BM-only contributors) | `cs.hold[]` filter | same |
| **Per-factor breakdown columns** in cardSectors / cardRegions | `cs.hold[].factor_contr` aggregated per bucket | per-holding `factor_contr` = latest only |

This is what the user observes as "risk stays static." It's **honest** — the data isn't there — but currently the user has no per-tile signal explaining why.

**Specific to the user's L12122 complaint** ("factor te breakdown in sector is empty for historical weeks"): the per-sector factor-contribution columns explicitly render `—` (em-dash) in hist mode with a tooltip "Per-holding factor breakdown only available for the latest week" (verified at L4550-4551). So the BEHAVIOR is correct (no fabrication); the COMMUNICATION is too quiet.

**Verdict:** code is right; UX is the gap. Two options:
- **B-fix.1 (light touch):** add a small "Latest holdings" pill near each Category-B tile's title when `_selectedWeek` is active
- **B-fix.2 (architectural):** ask FactSet for per-week per-holding history → ingest pipeline expansion → ~1-2 weeks of work + larger storage. Not recommended pre-launch.

### Category C — Hybrid (latest + historical) ✅

| Tile | Behavior |
|---|---|
| Factor Performance bubble (cardFacButt) | shows period impact (3M / 1Y / All) — period selector is INDEPENDENT of week selector. The two should not interact. |
| Factor Performance waterfall | same |
| cardAttrib (Risk attribution table) | period-aware via `getImpactForPeriod` for impact column |
| cardWeekOverWeek | week-aware (Category A) but compares selected week vs ITS prior, not vs latest |

**Verdict:** these correctly show period-aware OR week-aware values; no fix needed.

---

## 2. Specific findings — drift / staleness / lint-ignore exemptions

I checked each `lint-week-flow:ignore` comment to verify it's a legitimate exemption, not a covered-up bug:

| L# | Function | Reason given | Verdict |
|---|---|---|---|
| 6545 | rFacRisk fallback | "fallback path for environments without `_wFactors`" | ✅ legit defensive code |
| 7900 | rRisk `_facsForWeek` fallback | "fallback path" | ✅ legit |
| 7919 | rRisk legacy heuristic | "Legacy fallback only" — for files predating `pct_specific` field | ✅ legit |
| 7956 | rRisk facToggle list | "sector/country name list for checkbox labels — list doesn't change per week" | ✅ legit (the LIST of names is stable; user toggles which to plot) |
| openTileFullscreen 2× | various fallbacks | ✅ legit |
| rRiskFacBarsMode `cs.hold` | reads holdings for factor bar bucketing | 🟡 holdings-based — Category B by data shape |
| rWeekOverWeek 1× | reads holdings | ✅ legit (intentional latest-vs-prior comparison) |

**No covered-up bugs found.** The ignore comments are honest.

---

## 3. The root cause of the user's recurring complaint

The user has flagged this 4× because:

1. **Visual cue is too subtle.** The "Viewing week of {date} — summary metrics only" banner appears once at the top. After scrolling past it, the user sees holdings-based tiles showing numbers and assumes they reflect that week.
2. **Data architecture trap.** Per-holding factor decomposition + per-holding TE attribution genuinely cannot follow the week selector without a ~50GB ledger we haven't ingested.
3. **No per-tile signal.** Users see numbers and trust they refreshed; in hist mode, ~1/3 of the dashboard is silently latest.

The cumulative effect: user picks April 2024 week, expects every cell to refresh, sees the holdings tab unchanged, concludes "the selector is broken." It's not broken — but the silence is the bug.

---

## 4. Recommended fix — `latestOnlyPill()` helper

Add a centralized helper that emits a small pill when `_selectedWeek` is set:

```js
function latestOnlyPill(){
  if(!_selectedWeek)return '';
  return `<span class="latest-only-pill" title="This tile shows latest holdings — historical per-holding data is not shipped (per architecture). Historical sectors / factors / TE / etc. above DO follow the week selector.">Latest holdings</span>`;
}
```

CSS:
```css
.latest-only-pill {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 9px; font-weight: 600; letter-spacing: 0.4px;
  text-transform: uppercase;
  padding: 2px 7px; border-radius: 999px;
  background: rgba(245, 158, 11, 0.12);
  color: var(--warn);
  border: 1px solid rgba(245, 158, 11, 0.3);
  margin-left: 8px; cursor: help;
}
```

**Inject into 11 tile titles:**
- cardHoldings · cardWatchlist · cardHoldRisk · cardScat · cardTreemap · cardTop10 · cardRanks · cardRankDist · cardHoldConc · cardRiskByDim · cardUnowned

Effort: ~30 min. Low-risk (additive only; no data flow changes).

After the fix, when historical week is selected:
- 18 Category A tiles render their per-week values normally (no pill)
- 11 Category B tiles render latest values + show the "Latest holdings" pill
- The 1 user-reported confusion is resolved by signal, not by impossible data

---

## 5. Doc updates needed

- `CLAUDE.md` already documents the Two-Layer History Architecture; add a paragraph clarifying which tiles are Category A vs B
- `LESSONS_LEARNED.md` — add an entry: "When users say 'X stays static,' first check whether X CAN vary by week given the data shape. If no, the bug is communication, not flow."
- `SOURCES.md` — already per-cell; consider adding a "week-aware?" column to flag at a glance

---

## 6. What this audit explicitly did NOT find

- No fabrication anywhere in the week-aware code paths
- No double-rendering / phantom-write bugs
- No tile that has per-week data shipped but ignores it (the lint catches that pattern; lint passes)
- No race condition in `upd()` / `changeWeek()` flow

This is reassuring. The architecture is sound; the gap is UX clarity.

---

## 7. Action items

| # | Action | Owner | Effort |
|---|---|---|---|
| 1 | Implement `latestOnlyPill()` helper + CSS | Claude | 15 min |
| 2 | Inject into 11 Category B tile titles | Claude | 15 min |
| 3 | Update `CLAUDE.md` with per-tile classification | Claude | 10 min |
| 4 | Add LESSONS_LEARNED entry | Claude | 5 min |
| 5 | Validate visually: open dashboard, pick historical week, confirm pill renders on the 11 tiles | User | 5 min |
| 6 | Decide whether to pursue per-week per-holding ledger (Category B-fix.2) | User | strategic decision |

I'll execute 1-4 in this batch and queue 5-6 for your visual confirm + future direction.
