---
name: RR Session State
purpose: Live "where are we right now" file. Updated at every meaningful checkpoint. If a thread ends suddenly, this is how the next thread picks up mid-stride.
last_updated: 2026-04-23 (Batch 6 closed)
---

# Session State — Live

> **Rule:** Update this file at every checkpoint (finished a batch, about to spawn agents, hit a blocker, context getting long). The goal: any successor thread or subagent can read this + `LIEUTENANT_BRIEF.md` + `HANDOFF.md` and know exactly what to do next with zero guesswork.
>
> **Historical session logs** (pre-2026-04-21) archived at `archive/session-states/`.

---

## Current phase
**Tier 1 tile audits, Batch 6 closed.** 18 of ~21 tiles audited + trivial fixes applied + tagged. **None signed off yet** — user elected Option 3 cadence (2026-04-21): audit all tiles first, then run a single batch-review marathon at the end where user reviews each tile in-browser and gives explicit OK.
Production deployment planning paused pending Redwood IT confirmation of server layout.

> **Language discipline:** `.v1` / `.v1.fixes` tags = "audit complete" / "trivial fixes applied". These are NOT signoff. Signoff happens in the review marathon. Never write "signed off" in checkpoints, commits, or docs until user has explicitly OK'd the tile in-browser.

---

## Just finished (this session, 2026-04-23)
- **Batch 6 fixes committed + pushed** — `ef0cac3` on main; tags `tileaudit.{cardBenchOnlySec,cardUnowned,cardWatchlist}.v1` + `.v1.fixes` pushed (6 tags)
- Holdings trio sweep — 25 trivial fixes; 1 RED (cardUnowned no-data-source); 5 new cross-tile patterns
- cardBenchOnlySec (GREEN/YELLOW/GREEN): note-hook, PNG button removed, data-col ×4, sort wiring + data-sv on Biggest Missed col 3, col-3 tooltip. PM gate: B79 "% of benchmark missed" label rename.
- cardUnowned (RED/YELLOW/YELLOW): note-hook, data-col ×5, data-sv null-guards, sort null-guard, ticker escaping, region label normalization (Usa→USA · English→UK · Far East→Asia Pacific ex-Japan), header tooltips, defensive Pattern B fallback (`u.b??u.bw`), 4th sign-collapse site softened to neutral pending B74. **RED T1:** tile has NO data — `bw=pct_t=None` on 100% of 22 rows across 7 strategies because parser bucket is "orphan securities" not "unowned benchmark TE contributors". Deferred as **B80** PM gate: parser change / rename / hide.
- cardWatchlist (YELLOW/RED/YELLOW): FLAG_COLORS tokenized, ghost-holding detection with EXITED chip + muted opacity, isCash filter, per-section `<table id>` + `<thead>` with sortable `<th>` + tooltips, data-col/data-sv on every cell, CSV export (new `exportWatchlistCsv`), empty-state card with onboarding copy, `cycleFlag` now re-renders tile in place, note-hook + card-title tooltip, ticker escaping.
- `BACKLOG.md` extended **B79–B87** (B80 highest-leverage tile-level blocker — entire tile depends on source-of-truth decision).
- `AUDIT_LEARNINGS.md` extended with **5 new cross-tile patterns**: (1) normalize() remap skips non-holdings collections (`st.unowned` etc.), (2) parser bucket semantics ≠ tile semantics (read partition condition not bucket name), (3) sign-collapse 4th site (neutral softening as trivial, policy via B74), (4) synthesis tiles invisible-until-populated (empty-state card required), (5) mutation handlers that don't re-render dependent tiles (cycleFlag pattern), (6) ghost-data anti-pattern for localStorage refs to removed entities.
- Disk-verified (wc -l=6714 +50, PNG refs 5 ↓1, showNotePopup on card-titles=16 +4 [cardBenchOnlySec+cardUnowned+cardWatchlist×2 incl empty-state], data-col=76 +12, `exportWatchlistCsv`=2 [defn+call]) + node syntax check (all 3 `<script>` blocks parse clean). Browser verification deferred to review marathon.

### Previously
- **2026-04-23 Batch 5** — `f709e6e`; cardGroups/cardRiskHistTrends/cardRiskFacTbl; 25 trivials + BACKLOG B61–B78; Pattern C render-side re-derivation + parser dual-path `bm:None` + mini-chart sub-checklist learnings
- Risk-tab sweep — 25 trivial fixes; 2 RED verdicts with PM gates deferred; 3 new cross-tile patterns; 2 ledger corrections
- cardGroups (RED): fixed dead drill (oDrGroup now uses h.subg direct match, was broken GROUPS_DEF+SEC_ALIAS filter where "Info Technology"≠"Information Technology"); plotly_click → oDrGroup; data-col/data-sv/R·V·Q tooltips/themed colors/thresh-alert/warn row classes on table; PNG+CSV dropdown → single CSV; note-hook. RED: ORVQ rank-aggregation taxonomy deferred as **B61** PM gate.
- cardRiskHistTrends (YELLOW): fixed `_selectedWeek`-blind cur/prev lookup (was always last week); Holdings metric drill:null → oDrMetric('h'); 4 hardcoded colors tokenized via getComputedStyle + hex2rgba helper; per-metric hovertemplate/rangemode; short-history placeholder; noise floor 0.05/0.005; note-hook.
- cardRiskFacTbl (RED): card-title note-hook; "Exposure" → "Active Exposure" (header + oDrFRisk y-axis); per-column data-tips; data-col on all th/td; empty-state fallback; oDrFRisk annotation uses `a` when present; dead `rRiskFacBars` alias removed (0 callers). RED: active-vs-raw 3rd site (B73, supersedes B53) + sign-collapse 4th site (B74) escalated as cross-tile refactor — deferred.
- `BACKLOG.md` extended B61–B78 across 3 sections (B73 supersedes B53; B74 supersedes prior cardFRB sign-collapse scope; B65 supersedes B38).
- `AUDIT_LEARNINGS.md` extended with **3 new cross-tile patterns** (Pattern C render-side re-derivation from wrong config; parser dual-path — `_collect_riskm_data` hardcodes `bm:None` vs `_build_factor_list` populates `a`; mini-chart sub-checklist) + **2 ledger corrections** (h.subg populated ~85% non-cash; inlineSparkSvg tokenized L1456-1457) + active-vs-raw escalation to 3 sites + sign-collapse escalation to 4 sites with shared-helper recommendation.
- Disk-verified (wc -l=6664 +20, PNG refs 6 ↓1, showNotePopup refs 15 ↑3, rRiskFacBars=0, data-col=64) + node syntax check (all 3 `<script>` blocks parse clean). Browser verification deferred to review marathon — preview session stale post-compaction.

### Previously
- **2026-04-23 Batch 4** — `3052d69`; cardMCR/cardAttrib/cardCorr; 25 trivials + BACKLOG B39–B60; ghost-tile anti-pattern + anonymous Risk-tab cards + active-vs-raw 2nd site learnings
- Applied 25 trivial fixes across 3 tiles; deferring PM gates for review marathon
- cardMCR (RED): themed `--pri`/`--pos` via getComputedStyle, zeroline, PNG removed + exportMcrCsv(), plotly_click → oSt, note popup. MCR domain rename deferred as **B39** (paired with cardScatter B20)
- cardAttrib (YELLOW): waterfall card id added, tip+oncontextmenu both titles, isFinite filter, height cap min(900,max(160,N*32)+20), themed bar colors, data-col/data-sv on table, plotly_click → oDrAttrib
- cardCorr (RED): themed colorscale, custom exportCorrCsv(), thresholds → _thresholdsDefault.corrHigh/corrDiversifier, pearson null-n<3 + "—", oDrF drill on insight factors, localStorage rr.corr.*, min-history filter >=3, ghost PNG button removed
- `BACKLOG.md` extended B39–B60 across 3 sections (cardMCR B39–B44 with RED MCR rename as B39 PM gate paired with B20; cardAttrib B45–B52; cardCorr B53–B60 with B59 ghost-tile disposition + B53 active-vs-raw policy as PM gates)
- `AUDIT_LEARNINGS.md` extended with 3 new cross-tile patterns: ghost-tile anti-pattern, anonymous Risk-tab cards lacking ids, active-vs-raw series conflation (2nd site confirmed — now cardFacDetail L1764 + cardCorr L2168)
- Disk-verified (wc -l=6644, 7 PNG refs down from 9, 12 showNotePopup refs up from 9) + browser-verified (all 3 tiles render, 0 console errors, themed colors resolve to `#6366f1`/`#ef4444`/`#10b981`, thresholds loaded {hi:0.7, div:-0.5})

### Previously
- **2026-04-23 Batch 3** — `875ea84`; cardRanks/cardScatter/cardTreemap; 20 trivials + BACKLOG B20–B38. Themed Plotly colorscale pattern. exportScatCsv() replacing PNG.
- **2026-04-23 Batch 4** — `3052d69`; cardMCR/cardAttrib/cardCorr; 25 trivials + BACKLOG B39–B60; ghost-tile + anonymous Risk-tab + active-vs-raw 2nd site learnings.
- **2026-04-23 Batch 5** — `f709e6e`; cardGroups/cardRiskHistTrends/cardRiskFacTbl; 25 trivials + BACKLOG B61–B78; Pattern C + parser dual-path `bm:None` + 2 ledger corrections.
- **2026-04-21 Batch 2** — `3dcdae8`; cardFacDetail/cardFRB/cardRegions; ~20 trivials + PM-gated sign-colorize on cardFRB. Shared CSS tokens `--prof`, `--fac-bar-pos/neg`.
- **2026-04-21 Batch 1** — `e50409a`; cardChars/cardFacButt/cardThisWeek; ~17 trivials.

---

## In flight
Nothing in flight. Ready to scope Batch 5.

### New cross-tile learnings appended (Batch 6)
- **normalize() remap skips non-holdings collections** — L562–L573 maps field names (`bw→b`, `pct_t→tr`) on `st.hold` only; `st.unowned`/`st.watchlist`/etc. retain parser's original keys. Render reading normalized names silently gets `undefined`. Defensive render fallback `u.b ?? u.bw` works; permanent fix mirrors the remap.
- **Parser bucket semantics ≠ tile semantics** — `st.unowned` is partitioned by "rows with no weight data" (orphans/rights/cash), not "benchmark-unowned TE contributors". Audit heuristic: for every parser collection, read the PARTITION CONDITION from source, not the name. Cross-check narrative.
- **Sign-collapse 4th site** — cardUnowned static `color:var(--neg)` regardless of sign. Adds another member to B74 shared-helper scope. Detection grep: `color:var(--neg)` without surrounding `?:` ternary.
- **Synthesis tiles invisible-until-populated** — tiles that early-return `''` on empty user-generated state silently hide the feature from new users. Fix: empty-state shell with onboarding copy. Affects cardWatchlist, cardThisWeek, riskAlerts (≥4 sites).
- **Mutation handlers that don't re-render dependent tiles** — `cycleFlag` wrote to `_holdFlags` but only patched one button; `cardWatchlist` stayed stale until next `upd()`. Audit: grep every `onclick` that writes to a shared state var, grep every reader of that var, confirm mutation triggers re-render.
- **Ghost-data anti-pattern for localStorage refs** — user-generated state (flags, notes, alerts) keyed by entity ID that may have left the dataset. Watchlist ticker exits → row silently renders 0.00/0.00. Fix: presence-check at render, show EXITED chip + muted opacity.

### Carried from prior batches
- Pattern C render-side re-derivation (cardGroups)
- Parser dual-path `bm:None` in riskm path (cardRiskFacTbl; one-line parser fix pending)
- Mini-chart sub-checklist (cardRiskHistTrends)
- Active-vs-raw conflation — 3 sites (B73)
- Sign-collapse — now 5 sites confirmed (B74, escalating)
- Ghost-tile anti-pattern (cardCorr L1299 placeholder vs live heatmap at L3096)
- Anonymous Risk-tab cards lacking ids (sweep pending — B78)
- PNG-button sweep: 5 refs remain after cardBenchOnlySec removed; `cardRegions` L1331 still flagged
- Dataset-driven spot-checks catch RED findings pure-code-reading misses (cardGroups, cardUnowned)
- Parser-populated-then-discarded (Pattern B) — cardScatter L1254 / cardMCR same field
- Themed Plotly colorscales via getComputedStyle(--pos/--neg/--txt)
- Treemap drill-state reset (_treeDrill=null on strategy switch)
- Week-selector trap (s.sum vs getSelectedWeekSum())
- Sort-null anti-pattern (data-sv="${v??0}" corrupts numeric sort; use `??''`)
- Plotly click-drill parity gap
- Synthesis/insight tile checklist

---

## Next up (in order)
1. **Plan Batch 7 (final audit batch)** — ~3 tiles remaining. Candidates: `cardRating`, `cardFacWaterfall`, plus the anonymous Risk-tab card sweep (B78 — assign stable ids to `factorContribBarsDiv`/`teStackedArea`/`corrChartDiv`/`facHistDiv` wrappers, converting each into a tile-audit target in one pass). Three-audit natural cluster.
2. **Alternative** — if user wants to prep for review marathon before closing Batch 7, we could pause tile audits and generate the review-marathon dossier for the 18 tiles at `.v1.fixes` (per-tile screenshot spec + changes made + outstanding PM gates). PM gates queue is now: B20/B39 (MCR+Scatter rename pair), B53 (cardFRB sign-collapse context now folded into B74), B59 (ghost-tile disposition), B61 (cardGroups ORVQ taxonomy), B73 (active-vs-raw policy), B74 (sign-collapse shared helper), B79 (benchOnly label), B80 (cardUnowned source-of-truth — **highest-leverage**), B86/B87 (watchlist PM UX calls).
3. **Ask user** re: Batch 7 vs marathon-prep OR greenlight Batch 7 by judgment.
4. **Continue cadence**: spawn tile-audit subagents → review audits → apply trivial fixes → tag `.v1` + `.v1.fixes` → push.
5. **End-game**: once all ~21 tiles at `.v1.fixes`, prep review marathon — surface each tile with screenshot + changes made + outstanding PM gates for explicit in-browser OK.

---

## Open questions for the user
- Production deployment target: hostname/path/access for the internal Redwood server? (blocks automation spec)
- Weekly-append automation: shared drop folder path, or still TBD?
- Any tile the user wants prioritized out of normal batch order?

---

## Known blockers
- **Production deployment target** — "internal server" named but no concrete details. Weekly-append trigger mechanism deferred.
- **Frontend tests** — zero coverage on `dashboard_v7.html`. Playwright smoke test (load known JSON, assert all tiles render without console errors) ~1 day of work. Blocks confident auto-append later.
- **Trend sparklines on countries/groups/regions** — parser doesn't collect `hist.country` / `hist.grp` / `hist.reg`. Medium-effort parser change. Logged in `AUDIT_LEARNINGS.md`.

---

## Context-length tripwire
If this thread shows signs of compaction (recall drops, autocompact warning, context feels saturated), the next message to the user must be:

> **Heads up** — this thread is getting long. I've just refreshed `SESSION_STATE.md` so the transition is clean if you want to start a new one. I'll keep going here until you say switch. A fresh thread should read `LIEUTENANT_BRIEF.md` → `SESSION_STATE.md` → `HANDOFF.md` in that order.

Do not wait for auto-compact. Surface the option; let the user choose.

---

## Current tags / markers
- `v1.0` — ship-readiness sweep, pushed to origin
- `docs.governance.v1` — HANDOFF + LIEUTENANT_BRIEF + SESSION_STATE triad
- `tileaudit.cardSectors.v1`, `cardHoldings.v1`, `cardCountry.v1`(+`.fixes`)
- `tileaudit.cardThisWeek.v1`(+`.fixes`), `cardChars.v1`(+`.fixes`), `cardFacButt.v1`(+`.fixes`) — Batch 1
- `tileaudit.cardFacDetail.v1`(+`.fixes`), `cardFRB.v1`(+`.fixes`), `cardRegions.v1`(+`.fixes`) — Batch 2
- `tileaudit.cardRanks.v1`(+`.fixes`), `cardScatter.v1`(+`.fixes`), `cardTreemap.v1`(+`.fixes`) — Batch 3
- `tileaudit.cardMCR.v1`(+`.fixes`), `cardAttrib.v1`(+`.fixes`), `cardCorr.v1`(+`.fixes`) — Batch 4 audited + fixes applied, pending review
- `tileaudit.cardGroups.v1`(+`.fixes`), `cardRiskHistTrends.v1`(+`.fixes`), `cardRiskFacTbl.v1`(+`.fixes`) — Batch 5 audited + fixes applied, pending review
- `tileaudit.cardBenchOnlySec.v1`(+`.fixes`), `cardUnowned.v1`(+`.fixes`), `cardWatchlist.v1`(+`.fixes`) — Batch 6 audited + fixes applied, pending review
- `working.20260423.1654.pre-batch6` — most recent pre-risk safety tag

---

## Checkpoint log (append-only, newest on top)
- **2026-04-23 · Batch 6 audited + fixes applied, pending review** — 25 trivial fixes across cardBenchOnlySec (GREEN/YELLOW/GREEN; "% bench missed" label B79) / cardUnowned (**RED**/YELLOW/YELLOW; tile has NO data — bw=pct_t=None on 100% of 22 rows across all 7 strategies because parser bucket is orphan securities not benchmark-unowned TE contributors; B80 blocks full remediation, 4 cosmetic fixes deferred) / cardWatchlist (YELLOW/**RED**/YELLOW; RED T2 = no `<thead>`, no sort, no CSV, no empty-state, `cycleFlag` didn't re-render — all fixed; ghost-holding EXITED chip added; FLAG_COLORS tokenized). 5 new cross-tile patterns (normalize skips non-holdings collections, parser bucket semantics ≠ tile semantics, sign-collapse 4th site, synthesis invisible-until-populated, mutation handlers that don't re-render dependent tiles, ghost-data anti-pattern for localStorage refs). Verified via disk greps (6714 lines, PNG refs 5↓1, note-hooks 16↑4, data-col 76↑12) + node syntax check (3 script blocks clean). Committed `ef0cac3`, tagged ×6, pushed. BACKLOG extended B79–B87. Tile count 18 of ~21.
- **2026-04-23 · Batch 5 audited + fixes applied, pending review** — 25 trivial fixes across cardGroups (RED; ORVQ rank taxonomy B61 PM gate + dead-drill FIXED via `h.subg` direct match) / cardRiskHistTrends (YELLOW; `_selectedWeek`-blind cur/prev fixed, 4 colors tokenized, Holdings drill added) / cardRiskFacTbl (RED; active-vs-raw 3rd site + sign-collapse 4th site deferred as B73/B74 cross-tile refactor; header "Exposure"→"Active Exposure"). 3 new cross-tile patterns (Pattern C render-side re-derivation, parser dual-path `bm:None`, mini-chart sub-checklist) + 2 ledger corrections (h.subg populated ~85%, inlineSparkSvg tokenized). Verified via disk greps + node syntax check (all 3 `<script>` blocks clean). Committed `f709e6e`, tagged ×6, pushed. BACKLOG extended B61–B78 (B73 supersedes B53; B74 supersedes prior cardFRB sign-collapse scope; B65 supersedes B38). Tile count 15 of ~21.
- **2026-04-23 · Batch 4 audited + fixes applied, pending review** — 25 trivial fixes across cardMCR (RED; MCR rename deferred as PM gate B39 paired with cardScatter B20) / cardAttrib (YELLOW) / cardCorr (RED; ghost-tile B59 + active-vs-raw B53 deferred as PM gates). 3 new cross-tile learnings (ghost-tile anti-pattern, anonymous Risk-tab cards, active-vs-raw conflation 2nd site). Verified via disk greps + browser (0 console errors). Committed `3052d69`, tagged ×6, pushed. BACKLOG extended B39–B60. Tile count 12 of ~21.
- **2026-04-23 · Batch 3 audited + fixes applied, pending review** — 20 trivial fixes across cardRanks (YELLOW) / cardScatter (RED; MCR label bug deferred as PM gate B20) / cardTreemap (YELLOW). Themed Plotly colorscale pattern adopted. exportScatCsv() replaces Scatter PNG. Committed `875ea84`, tagged ×6, pushed. BACKLOG extended B20–B38.
- **2026-04-21 · Review cadence set to Option 3** — user clarified: `.v1.fixes` tags ≠ signoff. All tiles await in-browser review once auditing is complete. Audit-all-first, then batch-review marathon.
- **2026-04-21 · Batch 2 audited + fixes applied, pending review** — ~20 trivial fixes across cardFacDetail/cardFRB/cardRegions + PM-gated sign-colorize on cardFRB. Shared CSS tokens added. Committed `3dcdae8`, tagged ×6, pushed. BACKLOG extended B9–B19.
- **2026-04-21 · Batch 1 audited + fixes applied, pending review** — 9 Edits (~17 trivial fixes) across cardChars/cardFacButt/cardThisWeek applied. Committed `e50409a`, tagged ×6, pushed. Phantom spec deleted; `BACKLOG.md` created with B1–B8.
- **2026-04-21 · Chief of Staff handoff** — user formalized Chief of Staff role, asked for context-length alert discipline + lieutenant training. Created `LIEUTENANT_BRIEF.md` + fresh `SESSION_STATE.md`. Archived prior state log to `archive/session-states/`.
- **2026-04-20** — `v1.0` shipped. cardCountry v1 audit + fixes. `AUDIT_LEARNINGS.md` + `HANDOFF.md` created.
- **2026-04-19** — cardSectors v1 + cardHoldings v1 audits signed off. Cross-project ecosystem sync.
- Earlier history → `archive/session-states/SESSION_STATE-2026-04-19.md`.
