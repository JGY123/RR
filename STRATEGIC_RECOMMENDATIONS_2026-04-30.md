# RR — Strategic Recommendations · Long, Hard Look

**Drafted:** 2026-04-30 (post tab-audit batch + data-viz mockup mechanism)
**Author:** main session, after re-reading 41 docs + 11,572 lines of dashboard + 1,459 lines of parser
**Audience:** Yuda (product owner) — review on commute, pick the 2-3 you want to act on

---

## How I framed this review

I asked myself: **if I came back to RR cold tomorrow, what would I think the project is missing?** Not "what's the next backlog item" — that's the same incremental drain we've been doing. Bigger questions:
- What problem is the dashboard *not* solving for the PM today?
- What risk is hidden that won't show until the multi-year file lands?
- What part of the current system will rot if we don't address it now?
- Where is the highest-ROI big move we *haven't* taken?

I then sorted everything I saw into **3 tiers**: strategic shifts → shippable wins → housekeeping. The first tier matters most.

---

## TIER 1 — Three strategic shifts to consider (pick 1–2 to act on)

### S1. **Re-anchor the dashboard around "what changed since last review" instead of "what is the portfolio now"**

**The observation:** Today the dashboard is **excellent** at telling you the current state of the portfolio. Sum cards, tile after tile, drill modals — all snapshot views. **It's mediocre at telling you what changed.** A PM walking in Monday morning has to mentally diff today vs Friday. They don't have a bad memory; they're juggling 7 strategies. That's a tool's job.

**The evidence:**
- `cardWeekOverWeek` is **#1** in `NEW_TILE_CANDIDATES.md` ("the single most-asked-for view by every PM I've seen use a risk tool")
- A mockup is *already built* (`viz-specs/cardWeekOverWeek-mockup.html`, opened in your browser earlier today)
- Despite this, we keep iterating on snapshot tiles instead of shipping the diff tile
- Backlog has B114 (history persistence) which is a *prerequisite* for the diff view but isn't sequenced as such
- Once the multi-year file lands, we'll have rich history but **still no tile that surfaces "what changed"**

**The wise move:**
1. Pick a candidate from the cardWeekOverWeek mockup (R2-Q16) — Option A is recommended by the data-viz agent
2. Land cardWeekOverWeek as the **next major feature**, in front of any new audit work
3. Place it as the **first tile on the Exposures tab** (above This Week)
4. Re-anchor weekly PM workflow: "open RR Monday, scan cardWeekOverWeek for 90 seconds, drill into the 1–2 things that surprised you"

**Cost:** Medium — ~150 lines + parser update to persist `hold_prev`.
**Why now:** The mockup is ready. The data is in `cs.hist.summary`. The PM is iterating on the dashboard with you and is the right person to validate it within hours, not weeks. **Every week we delay is a week the dashboard doesn't earn its morning slot.**
**Why not:** If F9 / multi-year run blocks soon, this might land before we have rich history. That's fine — the diff is between THIS WEEK and LAST WEEK, both of which we have today.

---

### S2. **Stand up a "data quality" sidebar — formalize the trust layer**

**The observation:** The April data-integrity crisis taught us that *every numeric cell needs provenance*. We have:
- ᵉ markers on derived values (good)
- `_ABOUT_REG` per-tile entries with `caveats` (good)
- `SOURCES.md` index (good but rarely opened)
- `DATA_SPOT_CHECK_2026-04-30.md` (excellent, but a one-shot doc, not surfaced in UI)

**What we don't have:** a single place in the UI where the PM can see, in 10 seconds, **"how trustworthy is what I'm looking at right now?"** Today they have to know where the ᵉ flags are, hover the right cell, and parse the tooltip.

**The wise move:**
- A small "Data Quality" pill in the header, next to the week selector. Color-coded:
  - 🟢 Green: All visible values are sourced + verified.
  - 🟡 Yellow: N derived values on this tab (click to see).
  - 🔴 Red: Last data integrity assertion failed, or schema fingerprint drifted.
- Click it → modal listing every ᵉ value visible on the current tab + its derivation rule + link to the relevant spec section.
- Auto-update on tab switch.
- **Bonus:** the same modal shows "last data refresh" time and "verifier last run" status — answering the stale-data question (R-Q12 default: alert at 7d).

**Cost:** Small to Medium — ~80 lines + a per-tab derivation index. Most of the work is already done in `_ABOUT_REG.caveats` — needs aggregation logic.
**Why now:** We're days away from the multi-year run. When that file lands, the PM will be making real bets off the numbers. **The trust layer needs to be visible BEFORE the first real-money decision happens.**
**Why not:** Adds visual chrome to a header that's already busy. Counter: the existing chrome includes a cute REDWOOD wordmark — re-designing the header to make room is normal evolution.

---

### S3. **Split `dashboard_v7.html` — but only in one place, and only when we feel the pain**

**The observation:** The single-file architecture has been a feature, not a bug. Drag JSON, open HTML, done. **But:** 11,572 lines is the high end of what's pleasant to maintain in one file. The next phase will add cardWeekOverWeek (~150 lines), cardRegimeDetector (~250), cardWhatIf (~300). At ~12,500 lines we cross into territory where:
- Search-and-replace becomes risky (the "parse bomb" smoke check exists for a reason)
- New tile additions touch 4-5 regions of the file (markup + render fn + ABOUT entry + drill modal handler + CSS class)
- New session arrivals spend 30+ minutes orienting

**The wise move (NOT a full module split):**
- Keep the dashboard a **single deployed HTML file** — that's a real product feature
- BUT extract the `_ABOUT_REG` registry into a separate `dashboard_about_registry.js` file, included via `<script src="...">` from the main HTML
- This single split:
  - removes ~600 lines of registry code from the hot path
  - makes the registry editable as JSON-like data, not embedded in markup
  - decouples "tile semantics knowledge" from "tile rendering"
  - costs <1 hour to do, zero behavior change
- Bigger splits (e.g., per-tab JS) are deferred until we hit ~15k lines

**Cost:** Tiny — 30 minutes including verifier check.
**Why now:** Cheap insurance for the next round of growth. Avoids the day where someone says "we should split this file" mid-feature and gets bogged down.
**Why not:** It violates the "open one HTML file, drag JSON, done" mental model — but only marginally (the registry file ships in the same directory). Counter: the tradeoff is paid back the moment registry edits become trivial.

---

## TIER 2 — Five shippable wins (concrete and ready)

### W1. cardFreshness pill in header (subset of S2)
A tiny version of S2 — just the freshness indicator, no derivation modal. ~25 lines. Reads `cs.report_date` against today. Renders 🟢 / 🟡 / 🔴 dot. Hover shows last-pull date + days-ago. **Ship this regardless of S2** — it's cheaper than a separate decision.

### W2. Period-aware sweep across drill modals (B109 finish)
I made `cardRiskFacTbl` Impact period-aware in this batch. **The remaining tiles where Impact column is mislabeled or stale-snapshot-only:** drill modal stat rows in `oDrMetric`, `cardThisWeek` narrative bullets, `cardAttrib` Impact rows, `cardAttribWaterfall` return-impact bars. ~3 hours. **High consistency win for zero new tile work.**

### W3. cardWeekOverWeek (the diff tile) — see S1
Ship the mockup-approved variant. Place it as Exposures-tab-first. **Alone, this is the highest-ROI feature item left in the backlog.**

### W4. Doc-layer cleanup (consolidate or delete)
- 41 markdown files at repo root. Many are stale handoffs from earlier sessions (`CONTINUATION_PROMPT.md`, `HANDOFF_B105_EXECUTOR.md`, `HANDOFF_TO_EXECUTOR.md`, `SESSION_CONTEXT.md`, `INTEGRATION_BRIEF.md`).
- Four FactSet docs overlap (`FACTSET_CALL_PREP.md` / `FACTSET_FEEDBACK.md` / `factset_team_email.md` / `factset_email_READY_TO_SEND.md`) — pick one source of truth, mark the rest as archived.
- **Move stale docs to `docs/archive/`. Add a `docs/INDEX.md` so the next session arrival sees the map.** ~30 min sweep, big cognitive-load drop.
- This is the single highest-leverage cleanup of the project.

### W5. Apply audit-deferred PM-decision items as soon as you reply to R2-Q1, Q2, Q3
- **R2-Q1** (move cardWatchlist Exposures→Holdings): 10 min if yes
- **R2-Q2** (move cardBetaHist Risk→Exposures): 15 min if yes
- **R2-Q3 + Q4** (Rank Distribution + Top 10 fate): 10 min if delete, 30 min if upgrade
- **All three are queued in `tile-specs/TAB_QUALITY_AUDIT_2026-04-30.md`.** Just need your call.

---

## TIER 3 — Housekeeping that prevents future pain (do over time)

### H1. JS dashboard test harness
The Python parser has 89 pytest tests. The dashboard has zero JS-side tests. We rely on smoke_test.sh (script-syntax bombs) + verify_factset.py (data-side checks) + manual walkthrough. **Build a 20-test Playwright (or simple jsdom) harness** that asserts:
- Latest data loads without console error
- Each tab renders the expected tiles
- TE on the Risk-tab sum-card matches `cs.sum.te`
- Each ᵉ-marked cell has a tooltip
- Period selector toggle changes the right cells (synced after W2)

~3 hours. Pays back the moment a future "wacky number" lands.

### H2. CSS token sync between dashboard and mockups
Per the data-viz agent: "manual today, scriptable later." A 20-line `tokens-sync.sh` that diffs `:root` blocks across `dashboard_v7.html` and every `viz-specs/*-mockup.html`. Run on every commit (or via pre-commit hook).

### H3. Update the Risk Reports Specialist agent file
`~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md` is supposed to be the source of truth on field meanings. After every batch, decisions drift but the agent file isn't updated. **Sweep it after every 5 commits.** Today's batch (period-aware Impact, FacRisk Top OW/UW, cardCorr first-class, B116 Universe-mode SEV-1 workaround) needs to land in the agent file. ~20 min.

### H4. Telemetry "what does the PM actually use"
Add a tiny per-session counter (in localStorage, NOT data — same rules) that increments when each tile is interacted with. Surface in a "you opened cardSectors 14 times this week" debug view. **Privacy-friendly, all-local, no external calls.** When you start prioritizing among 10 candidate tiles, telemetry beats vibes.

### H5. Watchlist + flag persistence migration plan
When you move to Path B (workstation/server), localStorage flag state is lost. Pre-empt: add an `Export Flags` / `Import Flags` button pair to the Watchlist tile. Cheap insurance.

### H6. Drill-modal naming / convention sweep
We have `oDr`, `oDrF`, `oDrFRisk`, `oDrMetric`, `oDrCountry`, `oDrChar`, `oDrUnowned`, `oDrFacRiskBreak`, `oSt`, `oDrRiskByDim`, `openFacRiskFullscreen`. **Each is a slightly different convention.** A 1-hour pass to rename + document. Won't change behavior but will make new-tile additions cleaner.

### H7. Holding-level performance budget
The Holdings table renders 100+ rows with sparkline SVGs + factor pills + flag controls + ORVQ cells. On EM (which has more bench-only) this could become slow. **No virtualization yet.** Profile on the next sample with full holdings; add virt only if measured.

---

## What NOT to do (opinionated)

I want to flag two things I'd push back on if they came up:

### ❌ Don't add more snapshot tiles
The dashboard is dense at 25+ tiles. **Adding a 26th snapshot view is negative ROI.** Every new tile competes for screen real estate and PM attention. New tiles should answer questions no current tile answers — that means **diff** tiles (S1), **counterfactual** tiles (cardWhatIf), **regime-detection** tiles, **alert** tiles. Not "another way to look at the same exposure."

### ❌ Don't try to make the dashboard work without FactSet
Whenever we hit a missing field, the temptation is to compute it from what we have. The April crisis happened because we did this 4 times. The discipline is: **"missing data → ᵉ flag + tooltip + push back to FactSet."** Don't reverse-compromise this just to hit a tile completeness target.

---

## Suggested sequence (one possible execution path)

If you want a single answer to "what should we do next," here's my opinionated picking:

**Week 1 (this week):**
- Reply to R2 questions (especially Q1-Q5 + Q16) → I land tile moves + cardWeekOverWeek
- W1 ship freshness pill (cheap, high-visibility)
- W4 doc-layer cleanup (gets us out of the swamp)

**Week 2 (next week):**
- W2 period-aware sweep (consistency win across drill modals)
- S3 _ABOUT_REG split (cheap insurance for growth)
- H3 agent-file refresh (after Week 1's batch lands)

**Week 3 (data permitting):**
- S2 full data-quality sidebar (only after W1 proves the freshness-pill UX)
- H1 JS test harness scaffolding (small, then grow)

**On hold until F9 lands:**
- B116 real fix (vs current workaround)
- Multi-account run validation
- cardRegimeDetector (needs multi-year history)

---

## A short note on rhythm

We've been heads-down in audit + polish mode for ~2 weeks. The work is solid — Risk + Holdings tabs are now at parity with Exposures, the data-integrity foundation is hardened, the trust layer (`_ABOUT_REG` + ᵉ markers) is more rigorous than most production dashboards.

**But:** an audit-only rhythm depletes feature momentum. The PM is still reading the same 25 tiles every Monday. **Shipping cardWeekOverWeek (S1) breaks that pattern** — a new view that earns its slot in the morning workflow does more for PM trust than three more polish passes.

I'd suggest a deliberate cadence shift after this batch: **one batch of 4-5 polish items → ship one new feature → repeat.** Not "polish until everything is perfect, then build features." The latter never converges.

---

## Open questions for you (won't ship without your call)

These are the strategic-level questions that wouldn't get answered by R2:

- **A.** Is the dashboard a daily/weekly tool, or a sometimes-reference? (This determines whether S1 is critical or optional.)
- **B.** How many PMs will eventually use this — just you, or 3-5 colleagues? (Determines Migration Path A vs B and the priority of H4 telemetry.)
- **C.** When the multi-year run lands, do you commit to a 1-day "validate every spot-check value vs FactSet workstation" sprint? (DATA_SPOT_CHECK round 2 — recommended in the original report.)
- **D.** Are you OK with me proactively shipping the Tier 2 wins without checkpoint asks? (Specifically W1 freshness pill + W2 period sweep + W4 doc cleanup — none of these have UX-affecting decisions, just code work.)

---

**Bottom line:** stop rebuilding the same scaffolding. Pick S1 + 2 Tier-2 items + 1 Tier-3 item, sequence them across 3 weeks, and the dashboard goes from "thorough snapshot tool" to "Monday morning workflow tool." That's the wise move I'd make.
