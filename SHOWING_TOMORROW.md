# Showing Tomorrow — Prep Doc

**Drafted:** 2026-05-04 evening, ahead of 2026-05-05 showing
**Compared to:** Friday's version (`presentation-2026-05-01-shipped`, May 1 2026)
**Tag for tomorrow:** `working.20260504.2030.pre-showing` (current state) — push a `presentation-2026-05-05` tag right before the showing if all goes well

This doc is the "what to demo + what's better + what to avoid" cheat sheet. Read this in the 5 minutes before the showing.

---

## TL;DR — Why this version is better than Friday

In one sentence: **the dashboard is now honest about what it doesn't know, and that honesty is visible to the PM at every relevant tile.** Friday's version had silent fabrications + fewer disclosures; tonight's version has been audited end-to-end, has 5 F18 disclosure footers, and exposes data provenance per-week on the Risk-tab hero.

Three concrete things to point to during the showing:

1. **cardTEStacked provenance footer** (Risk tab, top hero tile) — three-tier color-coded dots (● green source-direct · ● indigo MCR-derived ᵉ · ● amber broadcast ᵉ) tell the PM at a glance which weeks the data came from clean. Friday's version painted a flat split with no transparency.

2. **F18 disclosure footers across 5 tiles** — cardRiskByDim, cardRanks, cardRiskDecomp, cardTreemap, cardUnowned now show `Σ %T = X% (expected ~100%; FactSet inquiry F18)`. Friday's version aggregated silently; tonight's version surfaces the deviation honestly.

3. **PM_ONBOARDING.md** — a "first Monday morning" cheat sheet for new PMs (FAQ, glossary, "when something looks wrong" path). Friday had EXECUTIVE_SUMMARY but nothing PM-facing.

---

## What's in this version that wasn't in Friday's

### Code-side improvements (visible in the dashboard)

| Tile | Friday | Now |
|---|---|---|
| **cardTEStacked** | Flat broadcast of latest-week split when per-week pct_specific was null (silent) | Three-tier resolver: source-direct → MCR-derived (L2-verified Σ\|sector mcr\|) → broadcast. Footer discloses which tier each week used. Console-warn on Σ-shares deviation > 5pp. |
| **cardRiskByDim** | Σ %T shown without disclosure | Σ %T = X% footer with F18 link. Σ %T AND Σ \|%T\| shown side by side. |
| **cardRanks** | TE Contrib column per quintile, no disclosure | Same column + footer disclosing Σ Q1..Q5 may not equal 100% per F18 |
| **cardRiskDecomp** | Idio sub-tree with no markers | Each idio leaf carries ᵉ marker + tooltip; footer discloses Σ \|top-7\| vs idio parent + count badge ("N factors · top M idio") |
| **cardTreemap** | F18 contamination silent on TE-size mode | Footer surfaces F18 disclosure ONLY when Size=TE is active (clean path on Weight/Count) |
| **cardUnowned** | "Showing top 10 of 819" without context | Footer: "Bench-only universe: 819 · 196 carry %T from FactSet · 623 long-tail without %T (F12 pending)" |
| **cardBetaHist** | Hardcoded hex colors, copy lied about "all 7 strategies" | Token-resolved colors, accurate copy ("for the active strategy"), footer caption (`N wk · since YYYY-MM`), week-marker on chart, KPI strip |
| **cardFacHist** | Cum Return shown as if compounded | ᵉ marker on Cum Return pill + tooltip + metric-aware footer caveat ("simple sum approx · ~25% under-report on high-vol") |
| **cardCorr** | No universe-invariance disclosure | Footer: "Active-exposure correlations are universe-invariant — Universe pill does not change this matrix" |
| **cardCashHist** | No tile chrome, hardcoded hex | Now uses tileChromeStrip (about, CSV, fullscreen, hide), token-resolved colors, hairline footer |
| **All Risk-tab time-series tiles** | Inconsistent week-marker handling | All 4 (cardTEStacked, cardBetaHist, cardCashHist, cardFacHist) now show vertical "selected wk" marker when global selector is on a historical week |
| **3 CSV exporters** | Chrome buttons referenced undefined functions (silent no-op) | Defined: exportBetaMultiCsv, exportFacHistCsv, exportFacContribCsv, exportTop10Csv. exportTEStackedCsv hardened to drop `?? 50` fab + add Source column |

### Parser-side improvements

| Item | Friday | Now |
|---|---|---|
| **PARSER_VERSION** | 3.1.0 | 3.1.1 |
| **FORMAT_VERSION** | 4.2 | 4.3 |
| **F19 — per-week pct_specific** | Parser dropped pct_specific from hist.summary; chart broadcast a flat split | Parser writes per-week pct_specific source-direct (when shipped). Verified end-to-end on 1.83 GB CSV — keys present, FactSet doesn't ship the values per-period (documented), so Tier 2 (MCR-derived) is canonical today |
| **normalize() `?? 0` fabrication** | normalize() set tr/mcr to 0 when source ships null. 76% of bench-only EM holdings had fabricated zeros. Same anti-pattern that produced April 2026 crisis | `?? null` — null preserved. Display sites render `—` (already null-safe via f2/fp helpers). Aggregations still treat null as 0 via `\|\| 0`. |
| **B114 cumulative-merge architecture** | Not yet built. Each ingest replaced production data | Built. `merge_strategy_into_existing()` + 13 tests + `merge_cumulative.py` CLI + `--merge` flag in `load_multi_account.sh`. Conflict policy: new-wins. Audit trail in `merge_history[]`. |
| **Test coverage** | 6 active tests | 26 active tests (13 B114 + 7 F19 + 6 legacy) — all pass |

### Documentation added

- `ARCHITECTURE.md` (433 lines) — contributor-facing intro. Data flow, tile contract, design system, integrity model, the 5 operational loops, "how to add a tile" worked example.
- `STRATEGIC_REVIEW.md` (May 1 baseline) + `STRATEGIC_REVIEW_NEXT.md` (May 4 follow-on) — periodic re-baselining.
- `PM_ONBOARDING.md` — "first Monday morning" cheat sheet for new PMs. FAQ, glossary, conventions, "when something looks wrong" path.
- `DRILL_MODAL_MIGRATION_SPEC.md` — spec for the next refactor wave (8 drills → unified `drillChrome` helper, 7 phases, ~6-7 hr total). Awaits PM signoff on 3 open questions.
- `FACTSET_INQUIRY_F18.md` — polished, high-ops ready letter to FactSet's PA quant team. Empirical findings strengthened with 3 patterns FactSet can't easily deflect.
- `PA_TESTS_F18.md` — companion: 8 tests (Test 8 added today, with CSV-side probe pre-walk-through), reordered priority based on the GSC counter-example.
- `LESSONS_LEARNED.md` — 16 lessons total (added 15: `?? 0` is fab; 16: contamination map).
- `SOURCES.md` — F18 contamination map across all known tiles. Definitive answer to "which tiles aggregate per-holding %T."

### Knowledge base / persona system

- `risk-reports-specialist` — confidence 96% → 98%
- `data-integrity-specialist` — 3 new RED anti-patterns added (13: `?? 0` in normalize; 14: aggregate-Σ without disclosure; 15: multiple palettes for same domain pair)

---

## Pre-showing checklist (do this in the next 30 min)

1. ✅ Pre-flight: smoke 20/21 (parse-bomb pre-existing, cosmetic), 26/26 parser tests pass, baseline tagged `working.20260504.2030.pre-showing`, 0 commits ahead of origin.
2. ✅ Dashboard already open in Chrome at `http://localhost:3099/dashboard_v7.html`.
3. **Visual smoke check (you, ~5 min):**
   - Open DevTools console (Cmd+Option+J). Look for `✓ B115 integrity check passed` line on load. Should be there. NO red errors.
   - Click through all 4 tabs (Overview / Exposures / Risk / Holdings). Each tab should render without flashing or visible errors.
   - Switch strategies via the header picker (cycle through ACWI / IDM / IOP / EM / GSC / ISC). Each should load.
   - Pick a historical week via the `‹ date ›` arrows. Amber banner should appear. The vertical "selected wk" marker should appear on cardTEStacked, cardBetaHist, cardCashHist, cardFacHist.
   - On the Risk tab: scroll to cardTEStacked. Check its footer (under the chart). Should show provenance breakdown like "Provenance over N wks: ● XYZ source-direct · ● ABC MCR-derived ᵉ".
   - On the Risk tab: scroll to cardRiskByDim. Footer should show `Σ %T = X% · Σ |%T| = Y%`.
   - On the Holdings tab: scroll to cardUnowned. Footer should show "Bench-only universe: N · M carry %T..."
4. **If anything looks broken:** roll back with `git reset --hard working.20260504.2030.pre-showing` and refresh the dashboard. (Unlikely; the smoke is clean.)
5. **Tag a presentation-2026-05-05 right before the showing:**
   ```bash
   git tag presentation-2026-05-05 && git push origin presentation-2026-05-05
   ```

---

## What to demo (suggested 5-minute walk-through)

If you have 5 minutes for the showing, this is the order:

### Minute 1 — Open + the headline KPIs

- Open the dashboard. Land on Overview tab.
- Point at `cardThisWeek`: TE / Active Share / Beta / Holdings — the 4 numbers every PM checks daily.
- Point at the Universe pill in the header: "Port-Held / In Bench / All — affects which holdings universe drives sector / country aggregations."
- Point at the week selector `‹ date ›`: "Time-travel to any historical week. Tiles update. Anything that's per-week aware shows a 'selected wk' marker."

### Minute 2 — The Risk tab hero (cardTEStacked)

- Switch to Risk tab.
- cardTEStacked at top: "Total TE decomposed into stock-specific (amber) + factor (cyan) over time."
- **Point at the footer below the chart:** "Three-tier provenance — every week's data comes from one of these: source-direct (green), MCR-derived (indigo), or broadcast (amber). Today, FactSet's CSV format dropped per-period pct_specific, so we use the L2-verified MCR-derived path. The footer tells the PM that, in plain English, instead of pretending."
- This is the **biggest differentiator from Friday**. Friday's version painted a flat split with zero transparency.

### Minute 3 — Honest disclosure on F18

- Scroll down on Risk tab to cardRiskByDim.
- "FactSet's per-holding %T column doesn't sum to 100% per portfolio — varies 94→134% across our strategies. Documented invariant says it should sum to 100%. We've escalated as inquiry F18, letter is drafted, going to FactSet's PA quant team."
- **Point at the footer:** `Σ %T = 134% · Σ |%T| = 156% · expected ~100%; F18 link`. "This is what 'doing it right' looks like — we'd rather show the deviation than rescale and hide it."
- Repeat for cardUnowned (Holdings tab): "Bench-only universe: 819 · 196 carry shipped %T · 623 long-tail without %T (F12 pending)."

### Minute 4 — The audit cadence

- Open `~/RR/tile-specs/` in Finder OR show in terminal: `ls -la tile-specs/ | tail -20`
- "14 tile audits filed in May. Every Risk-tab + Holdings-tab tile has been audited end-to-end. F18 contamination map is closed across all known tiles. The cadence compounds."
- Mention: "We caught a `?? 0` fabrication in normalize() — same anti-pattern that produced the April 2026 crisis. 76% of bench-only EM holdings were silently fabricated to zero. De-fabricated as part of the cycle."

### Minute 5 — Roadmap

- "Next moves: F18 letter to FactSet (sending tomorrow). B114 cumulative-merge architecture (shipped, ready for first production exercise). Drill modal migration (spec'd, awaiting PM signoff). PM_ONBOARDING screenshots (your input). Linux deployment runbook + Playwright e2e (long-shelf, post first PM rollout)."
- Show `STRATEGIC_REVIEW_NEXT.md`: "Tier A / B / C of what's next, ordered by leverage × accuracy-impact."

---

## What to AVOID showing (incomplete features / known caveats)

- **Don't switch to the SCG strategy** — SCG is not in the current data (it's the domestic-model file forthcoming per CLAUDE.md "Strategy Account Mapping"). The dashboard handles its absence cleanly but it's not part of the demo.
- **Don't open the cardTEStacked drill modal** if the strategy you've selected doesn't have rich `hist.fac['te']` data — the drill is fine but the audit's open larger items (range pills, click-to-set-week) aren't shipped yet. The tile itself is the showcase, not the drill.
- **Don't dive into DevTools console** in front of the audience — there are zero ERRORs but there ARE intentional `console.warn` messages from the integrity layer (e.g., cardTEStacked's "N/M weeks: Σ shares deviate from invariant"). These are FEATURES (defensive logging) but read as "warnings" to a non-technical audience.
- **Don't promise B114 is in production today** — it's shipped + tested but not yet exercised on a real new ingest. Promise: "the next CSV ingest will exercise it; current state is May 1 data."

---

## After the showing — follow-up actions

When the showing closes, regardless of outcome:

1. **Send the F18 letter** (you, ~10 min). Pre-send checklist in `FACTSET_INQUIRY_F18.md`.
2. **Run `./load_multi_account.sh --merge ~/Downloads/risk_reports_sample.csv`** (5 min wall) — first production exercise of B114. Validates the pipeline + lands FORMAT 4.3 in production data.
3. **Tag `presentation-2026-05-05-shipped`** if the showing went well; capture the demo state.
4. **Capture audience feedback** in `LESSONS_LEARNED.md` — every showing surfaces 2-3 things you didn't anticipate.

---

## Bottom line

You have **0 commits ahead of origin** (clean push state). Smoke is clean (20/21, the 1 failure is cosmetic and pre-existing for weeks). 26 parser tests pass. The dashboard is open in Chrome at `http://localhost:3099/dashboard_v7.html`.

**You are demonstrably ahead of the Friday version on data discipline + defensive UI + documentation.** The audience will see a dashboard that's not just shipping numbers, but shipping numbers + the mechanics behind them, in plain English.

If anything goes wrong tonight or tomorrow morning, roll back to `working.20260504.2030.pre-showing`. Tag is on local; if you want it on origin: `git push origin working.20260504.2030.pre-showing`.
