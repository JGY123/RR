# RR Strategic Review — 2026-05-04

**Drafted:** 2026-05-04 PM
**Purpose:** zoom out from the day-to-day fixes and look at where RR is, what we're actually building, and the loops we now have running. Periodic re-baselining so future sessions don't lose the forest for the trees.

---

## What RR is, in one paragraph

A **single-pane portfolio risk Control Panel** for 6+ investment strategies, built directly on FactSet Portfolio Attribution CSV exports, rendered as a single-file HTML dashboard (Vanilla JS + Plotly + html2canvas). 7+ years of weekly history, ~3,000 weekly snapshots, ~30 tiles across 4 tabs (Overview / Exposures / Risk / Holdings). Used by PMs daily; intended for the Alger team, with eventual firm-wide rollout. Built around a strict anti-fabrication policy after the April 2026 data-integrity crisis.

## What we're actually trying to do

Three layers, in order of importance:

1. **Get every number right.** PMs make decisions from these. A wrong cell once = lost trust, hard to recover. Anti-fabrication policy + integrity monitor + audit cadence all serve this.
2. **Make features ship from one place.** Refactored 30/30 tiles to declarative `tileChromeStrip` so adding a button is one edit, not 30. Same idea: column hide/show via CSS attributes, design tokens, lint-enforced week-flow.
3. **Become genuinely expert on the underlying metrics.** Not just "use what FactSet ships" — understand it, verify it, ask deepening questions, document everything we learn. The FACTSET_INQUIRY_TEMPLATE.md is this aspiration codified.

Stretch goal: launch-ready for daily team use, then firm-wide deployment.

## Where we are right now (state of the dashboard)

| Layer | State |
|---|---|
| **Code architecture** | 30/30 tiles use `tileChromeStrip`. 8/8 dashboard tables use `tableColHidePanelHtml`. 10 canonical CSS classes + design-token system. ~40 inline-style copies eliminated. Phase A-K refactor COMPLETE. |
| **Data accuracy** | Section-aggregate %TE sums to ~100% on 3,082 of 3,082 sector-weeks (verified). Per-holding %T (F18) ranges 94→134% — RED, escalated to FactSet, defensive UI shipped, automated monitor flagging. |
| **Tile audits** | 14 of 30 tiles audited current; 11 audit-driven fixes shipped this session. Tier-2 cadence ongoing. |
| **Documentation** | EXECUTIVE_SUMMARY (90-sec pitch) + PRESENTATION_DECK (12 slides) + PRESENTATION_DAY_GUIDE + MIGRATION_PLAN + LAUNCH_READINESS exist. ARCHITECTURE.md still missing (queued). |
| **Operational** | `load_data.sh` (parse + verify + open) + `load_multi_account.sh` (with EM-history merge) + `smoke_test.sh` (now 1.76s, 22MB peak after the memory fix) + `verify_section_aggregates.py` (Layer 2 monitor) all working. |
| **Recovery posture** | Push discipline now in SESSION_GUIDE. 72 commits + all session tags pushed. Daily scan caught the 71-commit drift; SESSION_GUIDE updated so it shouldn't recur. |
| **Memory profile** | 1.8 GB monolithic JSON + 1.69 GB per-strategy split files exist alongside. Smoke test loads slim summaries (~500 KB) for cheap checks; heavy ops use per-strategy files (peak ~1.5 GB single-strategy). 16 GB Mac is workable but not generous. |

## The loops we have running

This is the most important section. RR is not just a dashboard anymore — it's a set of recurring loops that make it more correct + more expert over time.

### Loop 1 — Tile audit cadence

`tile-audit` subagent → `tile-specs/cardX-audit-YYYY-MM-DD.md` → trivial fixes shipped, larger fixes queued, PM-decision items flagged. 14 of 30 tiles current; aim for full coverage at quarterly cadence.

### Loop 2 — Data integrity monitor

Layer 1 (verifier on every parser run) + Layer 2 (`verify_section_aggregates.py` on every smoke run, `--latest` mode 16 MB / 0.06s) + Layer 3 (trend monitoring, manual today, dashboard-tile someday) + Layer 4 (inquiry log = `FACTSET_FEEDBACK.md`).

### Loop 3 — FactSet inquiry workflow

`FACTSET_INQUIRY_TEMPLATE.md` six-step flow: observe → hypothesize → PA-test → letter → reply → monitor. F18 is the pilot. Each cycle deepens our expertise on a specific metric and adds an automated check so the question won't recur.

### Loop 4 — Refactor + lint enforcement

Per-week data flow lint-enforced (`lint_week_flow.py`, smoke-test gate). Smoke test catches script parse bombs, missing render fns, schema drift. Tag-and-push discipline at session boundaries. SESSION_GUIDE.md is the operator's spine.

### Loop 5 — Persona / agent training

`risk-reports-specialist.md` (96% confidence specialist agent for RR-specific work) + `data-integrity-specialist.md` (cross-project audit agent) + `factset-parser-engineer.md` (parser-specific). Updated when significant patterns emerge so future sessions inherit the lessons. **This document + the updates below are exactly that — the May 1-4 update.**

## What's NOT in good shape (honest)

1. **F18** — per-holding %T deviation 94→134% across strategies. Letter drafted, monitor wired, awaiting human send + FactSet reply. Until resolved, anything aggregating per-holding %T (cardRiskByDim, cardHoldRisk) carries an asterisk.
2. **Tier-2 audit coverage** — 16 of 30 tiles still on stale (April) audits. Especially cardCorr, cardFacContribBars, cardTEStacked, cardBetaHist, cardFacHist. Each is ~30 min of subagent work.
3. **ARCHITECTURE.md missing** — there's a REFACTOR_AUDIT, REFACTOR_IMPACT, REFACTOR_PLAN, but no single doc that introduces RR's data flow + tile contract + design system to a fresh contributor. Important for handoff / scale.
4. **Drill modal migration deferred** — `oDr`, `oDrMetric`, `oDrCountry`, `oSt` etc. still have inline chrome. Phase D ended at the tile level; the drills are next.
5. **PM-facing onboarding material is thin** — EXECUTIVE_SUMMARY exists but no screenshot tour, no FAQ, no "first Monday morning" cheat sheet. Needed before firm-wide rollout.
6. **Mac hardware running hot** — 16 GB / 3-day uptime / 83% swap. Work environment is workable but not robust to multi-task. Not a code problem; flagged here for completeness.

## Strategic priorities (next 1-3 weeks)

Ordered by leverage, not urgency (per "doing it right" framing):

### Highest leverage (do first)

1. **Run F18 PA-tests + send the letter** (1-2 hours of human work — FactSet relationship is unique). Closes the loop on a RED data finding.
2. **Continue Tier-2 audit cadence** — 5 tiles × 3 batches × 1 hour each = 5 hours total to reach full Tier-2 coverage. Makes the dashboard PM-trustable end-to-end.
3. **Write ARCHITECTURE.md** — 1-2 hours. Unblocks future contributors and handoff. Long-shelf-life doc.

### Medium leverage (when above is done)

4. Pending audit fixes (cardWeekOverWeek F4 CSV, cardHoldRisk F2 fullscreen, cardRiskByDim G1+G2 chip-card + threshold presets).
5. Drill modal migration (1-2 hours).
6. PM-facing onboarding (FAQ, cheat sheet, screenshot tour).
7. Linux server deployment runbook (Path B in MIGRATION_PLAN, currently sketched not battle-tested).

### Long-tail (post first PM rollout)

8. End-to-end browser test harness (Playwright).
9. Per-firm theming + auth/SSO (only if multi-firm demand emerges).
10. DR / backup strategy formalized.

## What changes our trajectory

- **F18 reply** — could reveal a parser bug (changes "fix code" path) OR confirm the doc is wrong (changes "update doc + close" path).
- **First PM using it daily** — first real-world feedback. Probably surfaces 2-3 issues we haven't anticipated.
- **Multi-firm interest** — would prioritize auth + theming + Linux deployment.
- **Quarterly FactSet model update** — schema fingerprint catches it; verify_section_aggregates flags drift; we run a verification sweep.

## How we know we're winning

Not "ship date." The metrics are quality + cadence:

- **Σ %TE within ±5%** on every (strategy × dim × week) cell that PMs see → currently 99.7% across section aggregates; per-holding F18 escalated.
- **0 RED findings on smoke test** for any session start.
- **<2 second smoke test** wall time → currently 1.76s (was hanging).
- **All Tier-1 + Tier-2 tiles audited within rolling quarter.**
- **Every F-item either resolved or has an active inquiry letter out.**
- **No commit accumulates more than 1 session's worth before push.**
- **PM survey post-rollout**: "I trust the numbers" / "I find what I need" / "I haven't been surprised by a wrong cell."

If those metrics hold, the dashboard is doing its job and we're earning the right to scale it.

## Closing thought

The user's framing has been consistent: **make it right, scale it slowly, become more expert each cycle.** Not "ship fast." That bias has produced a dashboard with rare data discipline, an audit cadence that compounds, and a knowledge base that future contributors can stand on.

The next 2-3 weeks should preserve that bias.
