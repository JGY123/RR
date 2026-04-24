---
name: RR Session State
purpose: Live "where are we right now" file. Updated at every meaningful checkpoint. If a thread ends suddenly, this is how the next thread picks up mid-stride.
last_updated: 2026-04-24 (SurpriseEdge deep-study complete — B105/B106/B107 ambition ladder registered)
---

# Session State — Live

> **Rule:** Update this file at every checkpoint (finished a batch, about to spawn agents, hit a blocker, context getting long). The goal: any successor thread or subagent can read this + `LIEUTENANT_BRIEF.md` + `HANDOFF.md` and know exactly what to do next with zero guesswork.
>
> **Historical session logs** (pre-2026-04-21) archived at `archive/session-states/`.

---

## Current phase
**🎯 Tier 1 tile-audit phase COMPLETE (Batch 7 closed 2026-04-24).** 21/21 tiles audited + trivial fixes applied + tagged. **None signed off yet** — user elected Option 3 cadence (2026-04-21): audit all tiles first, then run a single batch-review marathon where user reviews each tile in-browser and gives explicit OK. We are now at that marathon-entry point. Milestone tag: `tier1-audit-complete` at commit `01cbba0`.
Production deployment planning paused pending Redwood IT confirmation of server layout.

> **Language discipline:** `.v1` / `.v1.fixes` tags = "audit complete" / "trivial fixes applied". These are NOT signoff. Signoff happens in the review marathon. Never write "signed off" in checkpoints, commits, or docs until user has explicitly OK'd the tile in-browser.

---

## Just finished (this session, 2026-04-24 — data-foundation integration)
- **Tagged `data-foundation-v1` at `85c83a2`** — 4 commits pushed to origin (JGY123). Parser bumped to `PARSER_VERSION=3.1.0` / `FORMAT_VERSION=4.2`. Safety tag `working.20260424.1513.pre-phase1` preserved at pre-edit HEAD.
- **Phase 1 — Raw Factors capture** (`7bef572`): added `RAW_FACTOR_ORDER` (12 alphabetical factor names, positional fallback), `_extract_raw_factors()` method on `FactSetParserV3` (detects distinct per-period headers for future-proofing, else uses positional order), wired into `_assemble()` to emit `strategy.raw_fac` (≥700 entries/strategy, each with 12-float `e[]` and ascending `hist[]`) + `strategy.raw_fac_labels`.
- **Phase 2 — security_ref enrichment** (`fc2a8b5`): module-level load of `data/security_ref.json` (6,390 SEDOLs from baked Excel); `_enrich_holding()` function with SEDOL-exact → zero-stripped → name-fallback (lowercase-alnum-first-30) chain; populates `country`/`currency`/`industry` on every holding. Coverage: 100% on 4 of 7 strategies, ≥90% on all 7 (better than brief's 93-98% estimate). `strategy.security_ref_version` emitted per strategy.
- **Phase 3 — test suite replacement** (`33b6618`): prior `test_parser.py` imported 14 symbols from the retired positional 96/101-col parser (architectural replacement, not rename — forensic SHA `0d6699a`). Wrote new 17-test suite across 7 classes: TestRawFactorOrder (2), TestRawFacShape (4), TestEnrichHolding (4 unit), TestEnrichmentCoverage (2 integration), TestStrategyInvariant (2 regression), TestLegacyBehavior (3 — cash filter / comma-in-name / GICS full label). All green against the new-format sample. BACKLOG **B101** logs the legacy-coverage recovery option.
- **Phase 4 — regenerate sample_data.json** (`85c83a2`): 21KB ISC-only stale sample → 19MB full 7-strategy new-format. Browser regression via preview server (`port 3099`): all 24 audited tiles render, zero console errors, raw_fac + enrichment fields carry through `normalize()` spread intact. Dashboard unchanged — no edits to `dashboard_v7.html` or tile render fns.
- **Phase 5 — commit + tag + push** (this checkpoint): 4 commits landed on main; tag `data-foundation-v1` annotated "Raw Factors captured, security_ref enrichment live, all tests green, all 21 tiles render."; pushed via `gh auth switch --user JGY123`.
- **Invariant preserved:** `.v1.fixes` state across all 21 Tier-1 tiles is untouched. Review marathon still the next phase.

### Previously (2026-04-24 Batch 7)
- **Batch 7 fixes committed + pushed** — `01cbba0` on main; tags `tileaudit.{cardAttribWaterfall,cardFacContribBars,cardTEStacked}.v1` + `.v1.fixes` (6 tags) + milestone tag `tier1-audit-complete` all pushed
- **🎯 Initial Tier-1 tile-audit phase closed.** 21/21 tiles at `.v1.fixes`. Review marathon is the next phase.
- cardAttribWaterfall (GREEN/YELLOW/YELLOW): CSV export button + `exportFacAttribCsv()` helper, flex-between header chrome. Explicitly confirmed **NOT a B73/B74 site** (tile consumes only signed `f.imp` — no sign-collapse, no active-vs-raw). Non-finding discipline: 2 PM gates → B88 factor-family week-selector sweep + B89 waterfall naming.
- cardFacContribBars (RED/RED/YELLOW, was anonymous Risk-tab card → id assigned per B78): id + note-hook + plotly_click wired; `#fb923c` × 4 tokenized to `var(--prof)`; non-prof bar palette tokenized via getComputedStyle + `hex2rgba`; dead `--riskFacMode` custom-prop removed; radio-group a11y (`role="radiogroup"` + tabindex + focus); `setFacGroup`/`setFacBarAll` now intersect threshold slider (was silently overriding); `FAC_PRIMARY` filter dropped from Both mode (Secondary selections now visible); Both-mode label relabeled `|TE Contrib %|` as narrative disclaimer until B74 lands. **6th B74 sign-collapse site** + **4th B73 active-vs-raw site** confirmed.
- cardTEStacked (RED/RED/YELLOW, was anonymous Risk-tab card → id assigned per B78): id + note-hook + `plotly_click → oDrMetric('te')` wired; empty-state write-through; rangeslider border + fill/line rgba tokenized via new `_teStackColors()` helper using `--warn`/`--cyan`/`--pri`; CSV export `exportTEStackedCsv()` helper. **RED T1:** `pct_specific`/`pct_factor` interpreted as TE-shares but `CSV_STRUCTURE_SPEC.md` L184 says "% of Total Risk not TE" — mathematically dubious stacked decomposition. Deferred as **B96 — highest-impact Risk-tab data finding this batch.** Also synthesized `factorRisk`/`idioRisk` heuristic at `rRisk()` L3014 (`Σ|f.c|/totalTE * 1.2`, capped 0.85) silently pollutes 3 consumer tiles — new cross-tile pattern "Synthesized fallback leakage" → B99.
- `BACKLOG.md` extended **B88–B100** (13 new non-trivials). **B96 joins B80** as highest-leverage tile-level blockers (both PM-gated, both block correctness on a specific tile).
- `AUDIT_LEARNINGS.md` extended with **5 new entries**: (1) Sign-collapse escalated to 6 tiles (B74 graduates from "recommended" to "required"), (2) B78 anonymous-Risk-tab sweep 2-of-4 converted (cardBetaHist + cardFacHist pending post-closeout structural commit), (3) Non-finding discipline (explicit not-a-site findings prevent silent scope creep), (4) Synthesized fallback leakage — render-synthesized heuristics pollute downstream tiles (distinct pattern class from A/B/C), (5) FactSet `pct_X` denominator ambiguity — `pct_specific`/`pct_factor` = "% of Total Risk" not "% of TE".
- Disk-verified (wc -l=6777 +63, 2 new card ids, note-hooks 18 ↑2, 4 export helpers, 0 hardcoded-hex net increase) + node syntax check (3 `<script>` blocks clean). Browser verification deferred to review marathon.

### Previously
- **2026-04-23 Batch 6** — `ef0cac3`; cardBenchOnlySec/cardUnowned/cardWatchlist; 25 trivials + BACKLOG B79–B87; normalize-skips-unowned + parser-bucket-semantics-mismatch + synthesis-invisible-until-populated + mutation-handlers-dont-rerender + ghost-data-anti-pattern learnings.
- Holdings trio sweep — 25 trivial fixes; 1 RED (cardUnowned no-data-source); 5 new cross-tile patterns
- cardBenchOnlySec (GREEN/YELLOW/GREEN): note-hook, PNG button removed, data-col ×4, sort wiring + data-sv on Biggest Missed col 3, col-3 tooltip. PM gate: B79 "% of benchmark missed" label rename.
- cardUnowned (RED/YELLOW/YELLOW): note-hook, data-col ×5, data-sv null-guards, sort null-guard, ticker escaping, region label normalization (Usa→USA · English→UK · Far East→Asia Pacific ex-Japan), header tooltips, defensive Pattern B fallback (`u.b??u.bw`), 4th sign-collapse site softened to neutral pending B74. **RED T1:** tile has NO data — `bw=pct_t=None` on 100% of 22 rows across 7 strategies because parser bucket is "orphan securities" not "unowned benchmark TE contributors". Deferred as **B80** PM gate: parser change / rename / hide.
- cardWatchlist (YELLOW/RED/YELLOW): FLAG_COLORS tokenized, ghost-holding detection with EXITED chip + muted opacity, isCash filter, per-section `<table id>` + `<thead>` with sortable `<th>` + tooltips, data-col/data-sv on every cell, CSV export (new `exportWatchlistCsv`), empty-state card with onboarding copy, `cycleFlag` now re-renders tile in place, note-hook + card-title tooltip, ticker escaping.
- `BACKLOG.md` extended **B79–B87** (B80 highest-leverage tile-level blocker — entire tile depends on source-of-truth decision).
- `AUDIT_LEARNINGS.md` extended with **5 new cross-tile patterns**: (1) normalize() remap skips non-holdings collections (`st.unowned` etc.), (2) parser bucket semantics ≠ tile semantics (read partition condition not bucket name), (3) sign-collapse 4th site (neutral softening as trivial, policy via B74), (4) synthesis tiles invisible-until-populated (empty-state card required), (5) mutation handlers that don't re-render dependent tiles (cycleFlag pattern), (6) ghost-data anti-pattern for localStorage refs to removed entities.
- Disk-verified (wc -l=6714 +50, PNG refs 5 ↓1, showNotePopup on card-titles=16 +4 [cardBenchOnlySec+cardUnowned+cardWatchlist×2 incl empty-state], data-col=76 +12, `exportWatchlistCsv`=2 [defn+call]) + node syntax check (all 3 `<script>` blocks parse clean). Browser verification deferred to review marathon.

### Before Batch 6
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

### New cross-tile learnings appended (Batch 7)
- **Sign-collapse escalated to 6 tiles** — cardFacContribBars added 4 inline `Math.abs(f.c)` sites + dual-axis Both-mode overlay of signed vs magnitude-only. B74 shared-helper graduates from "strongly recommended" to "required before next Risk-tab UX pass".
- **B78 anonymous-Risk-tab-card sweep: 2-of-4 done** — `cardFacContribBars` + `cardTEStacked` now have stable ids + note-hooks. `cardBetaHist` + `cardFacHist` (Factor Exposure History) remaining; close via a single post-closeout structural commit (id+note-hook only, no full audits).
- **Non-finding discipline** — `cardAttribWaterfall` explicitly NOT a B73/B74 site. Recording negative findings bounds the scope of open refactors and prevents silent scope creep.
- **Synthesized fallback leakage (new pattern class)** — render-synthesized heuristics like `factorRisk`/`idioRisk` at L3014 (`Σ|f.c|/totalTE * 1.2` with fudge coefficient) silently pollute downstream consumers. Distinct from Pattern C (render-side re-derivation from wrong config) because here there's no config to derive from; the value is made up. Any var computed at top of render fn via filter/reduce/Math.min/max needs PARSER vs RENDER-SYNTH classification + optional `/* synthesized */` comment + UI disclaimer.
- **FactSet `pct_X` denominator must be identified** — `pct_specific`/`pct_factor` per `CSV_STRUCTURE_SPEC.md` L184 are "% of Total Risk, not % of TE", but cardTEStacked multiplies by `h.te` as if TE-shares. Variance decomposition ≠ linear TE decomposition under sqrt. Audit heuristic: never assume `pct_X` → `X%`. Always locate the denominator before rendering as a share.

### Carried from prior batches
- normalize() remap skips non-holdings collections (Pattern B variant, Batch 6)
- Parser bucket semantics ≠ tile semantics (Batch 6)
- Synthesis tiles invisible-until-populated / Mutation handlers that don't re-render / Ghost-data anti-pattern (Batch 6)
- Pattern C render-side re-derivation (Batch 5)
- Parser dual-path `bm:None` in riskm path (Batch 5; one-line parser fix pending)
- Mini-chart sub-checklist (Batch 5)
- Active-vs-raw conflation — **4 sites** (B73, now includes cardFacContribBars Both-mode overlay)
- Sign-collapse — **6 sites** confirmed (B74, required)
- Ghost-tile anti-pattern (cardCorr L1299 placeholder vs live heatmap at L3096; retire decision B59)
- Anonymous Risk-tab cards — **2 of 4 done** (cardBetaHist + cardFacHist remaining)
- PNG-button sweep: 5 refs remain; cardRegions L1331 still flagged
- Dataset-driven spot-checks catch RED findings pure-code-reading misses

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
1. **🎯 Review marathon of the 21 Tier-1 tiles** — dossier at `REVIEW_MARATHON_DOSSIER.md` (committed separately). User walks tiles in-browser; each tile → `.signedoff` tag at current HEAD, or deferred with PM-gate reference. Expected 60–90 min total.
2. **🎨 SurpriseEdge adoption — 3-phase ambition ladder** (full study at `design/SURPRISEEDGE_LESSONS.md` after direct source inspection of the v3.2.0 Tauri app on desktop, NOT just the HTML report):
   - **B105 · Phase 1 "Look as sharp"** (~2 hours, single commit, zero risk): palette swap to `--accent:#22d3ee` cyan + bundle DM Sans/JetBrains Mono woff2 + `.mono` everywhere + 11px uppercase card-titles + 6px scrollbars + 8%-alpha row separators + hex-alpha pill convention + gradient-bar wordmark. **Ships PRE-marathon on user greenlight** — every `.v1.fixes` state preserved at behavior level. Tag `design-polish-v1`.
   - **B106 · Phase 2 "Feel as sharp"** (~3–4 hours, POST-marathon): card toolbar (⛶/💡/ℹ) + left-border-accent-on-notes + smart filter bar with separators/chips/counter + multi-select filter panel + Key Takeaways tile with pin-to-persist. Tag `feel-parity-v1`.
   - **B107 · Phase 3 "Meta-layer depth"** (~1–2 days, POST-Phase 2): insight panels per card with data-lineage chips + Ask AI integration with tile-specific prompts pulling from AUDIT_LEARNINGS + PDF manual auto-generated with deep links + winsorize controls + lazy tile placeholders + Claude API key settings. Tag `depth-v1`.
   - **Phase 4 "Exceed" (post-depth-v1):** time-travel banner on `_selectedWeek`, strategy comparison overlay, B102–B104 raw-factor decomposition tiles, historical heartbeat animation. Features RR has that SurpriseEdge can't.
3. **🧩 Tier 2 tile build queue — deferred pending marathon + B105 polish (B102–B104 in BACKLOG)**. These CONSUME data-foundation-v1 (raw_fac + security_ref enrichment):
   - **B102 · `cardRiskByDim`** — risk decomposed by Country / Currency / Industry. **User's key 2026-04-24 ask** ("when security has 2% contribution to risk from country you'll be able to map which country etc."). M-size build on Risk tab.
   - **B103 · Per-security raw factor drill** — inside `oSt(ticker)` modal, 12-factor z-score bar chart + 4-period sparklines. S-size modal extension.
   - **B104 · Portfolio raw-exposure aggregate** — synthesis hero reconciling weighted-sum of security exposures against `cs.factors[].a`. M-size; depends on B103. All three together = "second mini-marathon" after the Tier-1 marathon closes.
3. **Post-closeout B78 structural commit** — close remaining 2 anonymous Risk-tab cards (`cardBetaHist` at L3105, `cardFacHist` at L3194) in one id+note-hook structural pass. Not a full audit — just addressability. ~15 LOC. Sequence-free — could ride with B102–B104 or stand alone.
4. **PM-gate queue — priority-ranked for the marathon** (block a tile's signoff until resolved):
   - **B80** · cardUnowned data-source decision — whole tile dead without it (parser change / rename / hide)
   - **B96** · cardTEStacked `pct_specific`/`pct_factor` denominator — mathematically dubious stacked decomposition
   - **B73** · active-vs-raw unification (4 sites) — Risk-tab-wide policy
   - **B74** · sign-collapse shared `mcrSigned()` helper (6 sites) — graduated to required
   - **B61** · cardGroups ORVQ rank taxonomy
   - **B20/B39** · MCR + Scatter label rename pair
   - Secondary: B59 ghost-tile retire, B79 benchOnly label, B86/B87 watchlist UX, B89 waterfall naming, B88/B97/B70 week-selector sweep, B99 heuristic audit, B100 palette tokens, B90–B95 cardFacContribBars follow-ups
5. **Parser-side one-liner pending** — `factset_parser.py:468` `bm: None` → `bm = e - a if a is not None else None`. Unblocks B73 for the riskm path. Ships with next parser release or as a standalone commit before review marathon.
6. **Production deployment target** — still blocked on Redwood IT confirmation of server layout. Unrelated to marathon.

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
- `tileaudit.cardAttribWaterfall.v1`(+`.fixes`), `cardFacContribBars.v1`(+`.fixes`), `cardTEStacked.v1`(+`.fixes`) — Batch 7 audited + fixes applied, pending review
- **🎯 `tier1-audit-complete`** at `01cbba0` — milestone tag marking all 21 Tier-1 tiles audited
- `working.20260424.1009.pre-batch7` — most recent pre-risk safety tag

---

## Checkpoint log (append-only, newest on top)
- **2026-04-24 · 🎯 Batch 7 closed — ALL 21 TIER-1 TILES AUDITED** — 20 trivial fixes across cardAttribWaterfall (GREEN/YELLOW/YELLOW; confirmed NOT a B73/B74 site) / cardFacContribBars (**RED/RED/YELLOW**; was anonymous, id assigned, 6th B74 + 4th B73 site, threshold-override bug fixed, FAC_PRIMARY filter dropped from Both mode, `#fb923c` × 4 tokenized) / cardTEStacked (**RED/RED/YELLOW**; was anonymous, id assigned, `pct_specific`/`pct_factor` semantic mismatch → B96 highest-impact data finding; synthesized `factorRisk`/`idioRisk` heuristic leakage → B99 new pattern). 5 new cross-tile patterns (sign-collapse → 6 tiles, B78 sweep 2-of-4, non-finding discipline, synthesized fallback leakage, FactSet pct_X denominator discipline). Verified via disk greps (6777 lines +63, 2 new card ids, note-hooks 18, 4 export helpers) + node syntax check (3 script blocks clean). Committed `01cbba0`, tagged ×6 + milestone `tier1-audit-complete`, pushed. BACKLOG extended B88–B100. **Tile count 21 of 21. Next phase: review marathon.**
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
