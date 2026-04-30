# Inquisitor Question Queue — Decisions
**Captured:** 2026-04-30 · From the 135-question commute review.
**Convention:** ✓ = user answered or default-accepted · ⚠ = needs explanation/discussion · 🔥 = high-priority action · 📋 = deferred for spec.

## P0 Parser & data layer

- **Q1** ✓ Missing strategy: alert with red pill (default A).
- **Q2** ⚠ Column-count drift: warn-and-load AND parser auto-adapts. **It already does** — the parser is header-driven (no hard-coded columns), so additions/removals/renames don't break ingestion. The schema fingerprint warns about drift; data still loads. We treat the warning as "review what changed, not freeze the build."
- **Q3** ✓ Drift threshold permissive (additions OK, removals alert) — default B.
- **Q4** ✓ Store both raw + normalized in JSON (default A — provenance).
- **Q5** ✓ ADRs use country-of-RISK (issuer domicile) — yes.
- **Q6** ✓ Missing factor: emit null + warn banner (C). Time-series interpolates between points (smooth visual line) but ALERTS on null gap so user knows.
- **Q7** ✓ report_date: filename + CSV with mismatch warning (default C).
- **Q8** ✓ @NA / [Unassigned]: separate "Unclassified" bucket (default B).
- **Q9** ✓ CSV quoting recovery via column-count (default A).
- **Q10** ⚠ PARSER_VERSION bump policy: **bump on every JSON output change** (default B). Reasoning: the version exists so dashboard JS can refuse to load incompatible JSON. CSV schema can change without changing JSON output (parser absorbs it). Bumping on JSON-shape changes only is what JS actually needs to gate on.
- **Q11** ✓ Partial week: append flagged "intra-week" (default C).
- **Q12** ✓ Stale-data alert > 7 days (default A).
- **Q13** ⚠ Emit manifest.json per run: **yes**. Reason: an audit trail proving "we parsed file X (hash Y), got Z rows, found these accounts, on this date" — invaluable for debugging "why does this number look wrong".
- **Q14** ⚠ Append-only history: **single `history.jsonl` per strategy** (default A). Reason: a JSONL file is one entry per line, easy to append, easy to grep, easy to slice by date. Per-week files would mean hundreds of tiny files. JSONL = "JSON Lines" → standard append-only format.
- **Q15** ✓ Multi-month misclassification: CLI flag override (default A).

## P0 cardSectors

- **Q16** ✓ Trend column when port-history empty: TE-sign indicator (default B).
- **Q17** ✓ Bench-only sectors in Port mode: **A — visible greyed-out**.
- **Q18** ✓ Quadrant Q3: **B — muted grey**.
- **Q19** ✓ FS view-aware (table-view → table FS, chart-view → chart FS) **already implemented**. Plus FS now has a toggle to switch view types from inside FS — already works on cardSectors / cardCountry / cardGroups / cardRegions.
- **Q20** ✓ Sparkline range matches global (default A).
- **Q21** ✓ Sort default: abs TE contribution (default A).
- **Q22** ⚠ "% of total active risk" column: **already exists as `% TE`** (factor's contribution to total tracking error, signed). The "% of Factor" column we added recently is the relative dominance within Factor Risk only. So we have both — they're different ratios per the dual-ratio rule we landed.
- **Q23** ✓ Sector header click → drill into holdings AND show "Top 10 BM weights not owned" panel.

## P0 cardCountry

- **Q24** ✓ Map color default: TE Contribution (default B).
- **Q25** ✓ Country-of-risk vs listing toggleable (default A).
- **Q26** ⚠ **Map projection explainer:**
  - **Equirectangular** (current) — flat lat/long grid. Simple, country shapes look stretched near poles.
  - **Mercator** — Google Maps style. Preserves angles. Greenland looks huge.
  - **Robinson** — compromise projection. Looks "nice" for world maps; minimal distortion. Often used by National Geographic.
  - 🔥 **Recommendation: Robinson + add reset-zoom button.** Cleanest for a global PM view.
- **Q27** ✓ Zero-exposure countries: grey (default A).
- **Q28** ✓ Add country search box: yes.
- **Q29** ⚠ EM strategy + DM countries: greyed (A). **Saturation** = how vivid/intense a color is. Greyed = low saturation. The point: when viewing EM, US/UK/JP shouldn't be vivid red since they're not in the universe — desaturating reminds you they're out of scope.

## P0 cardRegions / cardGroups

- **Q30** ✓ Region taxonomy: both with toggle (default C).
- **Q31** ⚠ "% coverage" pill confirm KEEP. **Reason:** when only 40% of holdings have a region tag, showing "regional analysis" without that disclosure is misleading. Pill is honest.
- **Q32** ✓ Strict one-stock-one-group (default B).
- **Q33** ✓ Group definitions: Redwood internal (default B).
- **Q34** ✓ Add Region × Sector cross-tab: yes.

## P0 cardHoldings

- **Q35** ✓ Primary identifier: ticker-region (default A) — **already shipped via tk(h) helper**.
- **Q36** ✓ Bench-only: **B + C** — separate "Unowned" subtab AND filter pill on main holdings view.
- **Q37** ✓ Sort default: abs TE contribution (default A).
- **Q38** ✓ Track SEDOL change continuity: yes.
- **Q39** ✓ Sparkline of port weight history: yes.
- **Q40** ✓ Exited holdings: tag "EXITED" for one week (default A).
- **Q41** ⚠ Tab badge: **B — active count**. Reason: a "holding" includes cash baskets, currency hedges, near-zero residuals — the PM cares about real equity positions. Saying "1218 holdings" when 1170 are bench-only inflation is misleading. "Active count" = positions where you have a real allocation.
- **Q42** ✓ Top-10 TE pill at top of tile: yes.

## P0 cardRisk

- **Q43** ✓ TE math fix now with disclaimer (default A). User noted **synonym confirmation needed**:
  - "% Total Risk" — share of TOTAL risk (portfolio standalone)
  - "% Active Risk" / "% TE" — share of TRACKING error (vs benchmark)
  - "Contribution to TE" / "TE Contribution" — same as % TE for a holding
  - 📋 **Need to verify from data which fields mean which** and document as project canon.
- **Q44** ✓ FRB many-factors: top-8 + Other (default C). **Note: cardFRB was already removed as redundant — this answer is now moot.**
- **Q45** ✓ Correlation: heatmap + network toggle (default C).
- **Q46** ✓ Range buttons: add 5Y, since-inception, rolling-12M (default D) — and more. 🔥 Build out a "range chip rack" for time-series tiles.
- **Q47** ✓ Variance vs std: both with toggle, with explainer when toggling. Variance = TE² (additive across factors); Std = TE (units the user thinks in). Toggle helps for risk decomposition arithmetic.
- **Q48** ⚠ TE history vs benchmark TE: **bm has no TE by definition** (TE is the spread vs bm; bm vs itself = 0). User intuition correct. **Skip the overlay** — it'd be a flat zero line, not informative.

## P0 cardFactors

- **Q49** ⚠ Synth markers: **the ᵉ superscript** we put on values that were SYNTHESIZED (e.g., when FactSet shipped null %T but we computed it from |a|×σ as a placeholder). Per the anti-fabrication policy from April 27 crisis, every synth value must be marked. **Once FactSet ships real values, REMOVE the markers** — and the project's hard rule is "never fabricate; null is OK, marked synth is OK, silent fabrication is not." User confirms this is the rule. ✓
- **Q50** ⚠ Default factor view: **active exposures only** (default A). "Active exposure" = portfolio's σ position vs benchmark (e.g., +0.27σ overweight Momentum). "Raw exposure" = absolute exposure (e.g., portfolio is +1.2σ Momentum vs market average of +0.93σ — bench is the difference). PMs care about active first, raw is reference. Split-tab adds clutter.
- **Q51** ✓ Sparkline range matches global (default A).
- **Q52** ✓ Highlight sign flips on sparkline: yes.
- **Q53** ✓ Factor buttons: keep + add "All" toggle (default B).
- **Q54** ✓ Attribution by period: one table (default A).

## P0 cardWatchlist

- **Q55** ✓ Auto-watch: both with toggle (default C).
- **Q56** ✓ EXITED notification: chip only (A).
- **Q57** ✓ Multi-strategy watchlist: per-strategy by default + prompt "this stock is also in IDM, IOP — flag there too?" when adding.
- **Q58** ✓ Notes/tags per stock: yes — pre-populate with last-known reason, allow editing.
- **Q59** ✓ Watchlist count badge on tab: yes.

## P1 Drill modals

- **Q60** ✓ Drill rows: top-20 default + "Show all" link (default C).
- **Q61** ✓ Drill nesting: **A — infinite**.
- **Q62** ⚠ Right-click menu: **B — copy-only** (current has Copy Value / Copy Row / Copy Column / Show as % / Add Note). Plus 🔥 **every table needs a "Download CSV" button** — extending to all tables.
- **Q63** ✓ Esc to close, arrows to navigate: yes.
- **Q64** ✓ Drill export: CSV (no PNG buttons per project rule).

## P1 Charts and visualization

- **Q65** ✓ FS chart priorities: B (animated time-series), C (sector × factor heatmap), E (candlestick). User asks: "way to see explainer per tile". 🔥 **"About this tile" button** with provenance + math + caveats — already a P1 (Q88).
- **Q66** ⚠ Plotly vs custom canvas: **stay Plotly unless perf measurable** (default C). Plotly: free, battle-tested, exports SVG/PNG, hover/zoom built in, declarative. Custom canvas: faster for >10k points but every interaction (hover, click, zoom, tooltip) is hand-coded. For our scale (≤1218 holdings, ≤526 weeks) Plotly is fine. Path to "creative crisp UI": layered Plotly with our own annotations / shapes / custom hover, not canvas rebuild. 🔥 **Theme polish + custom logo + header refresh** is the visible-quality move; we can do that without leaving Plotly.
- **Q67** ✓ Sparkline cells: hover expand (default B).
- **Q68** ✓ Chart export: global ⬇ menu only (default A).
- **Q69** ⚠ Palette: **keep current dark + iterate** (A). "Tableau-10" = a 10-color palette designed by Tableau Software for categorical data; great for distinguishing 10 categories without clashing. We could borrow it for multi-line charts. **For RR specifically** — current palette is good; the bigger lift is **header polish + logo**. 🔥 **Add to backlog: design a "Redwood Risk" wordmark/logo** (you mentioned "Surprise Edge" precedent).
- **Q70** ✓ Colorblind-safe mode: **no** per user.
- **Q71** ⚠ Heatmap normalization: per-strategy. **Reason:** if EM has TE 8% and SCG has 4%, symmetric color scale makes EM look red and SCG look pale — but SCG might have a more concentrated risk profile that's HIGH within SCG context. Per-strategy normalization shows relative within each strategy, which is what a PM compares. Symmetric is better for absolute size questions only. 📋 **PDF/diagram of color-scale tradeoffs** — defer to a write-up later.

## P1 Performance / UX

- **Q72** ⚠ Holdings table virtual-scroll vs paginate: **only if perf complaint** (default C). **Pagination** = "page 1 of 25, click Next." Like Google search results. Virtual scroll = looks like one infinite list but only renders visible rows. We have pagination today (PPG=20 per page). Stays fine for 1218 rows.
- **Q73** ✓ Light mode: no.
- **Q74** ✓ Tablet view: **deferred** until everything else is ready (user direction). 📋 added to backlog.
- **Q75** ✓ Cmd+K: **no** per user.
- **Q76** ✓ Ctrl+F to find specific sectors/factors: yes — wire up a section-search.
- **Q77** ✓ Date picker on week selector: yes.
- **Q78** ✓ Strategy switcher: dropdown stays, but split into "Domestic" and "International" sub-groups inside the dropdown.
- **Q79** ✓ Strategy switch preserves tab + week: yes.
- **Q80** ⚠ Error states: **B — banner**. Definitions:
  - **Toast** = small notification that fades out (e.g., "Saved" appearing top-right for 3s)
  - **Modal** = blocking dialog you must dismiss before continuing
  - **Banner** = persistent strip across top of card/page until dismissed (what we use for week-banner today)
  Banner wins for data issues — they're not transient (toast) and shouldn't block work (modal).

## P1 Data delivery

- **Q81** ✓ Strategy mapping: shared with overrides (default C).
- **Q82** 🔥 **Critical action plan, captured separately as `MIGRATION_PLAN.md`** — first GSC full-history validation, then move RR to professional environment, then upload all account histories. **Need to document this end-to-end with full instructions.**
- **Q83** ⚠ **Slack** = a chat app teams use for messaging. Like Discord/Teams. **B (slack)** assumed you have Slack; if not, A (email) is the right fallback. 🔥 default to email if no Slack workspace exists.
- **Q84** ✓ Append-only retention: keep all weeks forever (modified from default C). 🔥 **Build append-only weekly upload + "additional account" upload paths** — explicit goal: no overwrite of existing data ever.
- **Q85** ✓ Date overlap: alert and ask (modified from default A → C).
- **Q86** ✓ Backup JSON to S3/Drive: yes.

## P1 Documentation

- **Q87** ✓ Render fn docstrings on all (default A).
- **Q88** ✓ Per-tile "About this tile" popup: yes.
- **Q89** ⚠ Smoke_test exit code in commit messages: yes. **Reason:** every commit's message would carry e.g., "smoke: 18/19 pass" — instant proof at the commit moment that the change didn't break the build. Future-you scans `git log` and sees green/red.
- **Q90** ✓ SOURCES.md auto-update with manual review (default C).
- **Q91** ✓ FACTSET_FEEDBACK resolved-archive section: yes.
- **Q92** ✓ LESSONS_LEARNED append-only (default A).

## P1 Workflows

- **Q93** ✓ Screenshot-diff regression: yes.
- **Q94** ✓ Auto-create GH issue per FAIL: yes.
- **Q95** ✓ Pre-commit hook smoke: yes.
- **Q96** ✓ Pre-push integrity assertion: yes.
- **Q97** ⚠ Tag-before-risky-edit hook: yes. **Mechanic:** a git pre-commit hook detects when `dashboard_v7.html` or `factset_parser.py` are modified, automatically creates a `working.YYYYMMDD.HHMM.pre-X` tag pointing at HEAD, then proceeds with the commit. So every risky edit has an instant rollback point. Already partly enforced via `regression-checkpoint` Skill — making it a hook automates it.
- **Q98** ✓ Session-end auto-update of LIEUTENANT_BRIEF + SESSION_STATE: yes. 🔥 Plus build a "session-resume" pattern that pulls relevant context when starting a new Claude thread.

## Naming

- **Q99** ✓ "Spotlight" name: keep.
- **Q100** ✓ Strategy codes: abbrev + tooltip (default C).
- **Q101** ✓ Tile naming: **B — drop "card" prefix**. 📋 needs a sweep — rename every `cardX` → `tileX` across HTML + JS.
- **Q102** ✓ "TE" abbreviation: TE (default A).
- **Q103** ✓ "Active Share": **C — full word**.

## P2 Wishlist

- **Q104** ✓ Anomaly detection overlay: yes.
- **Q105** ⚠ User correctly identified: TE of bench vs bench = 0 by definition. **Skipping this question entirely** — bench-only TE attribution is meaningless.
- **Q106** ✓ Brushable time-series filter: yes.
- **Q107** 🔥 Risk-budget mode: **needs full spec.** Build out: definition, methodology, parameters, alerts. 📋 dedicated session needed.
- **Q108** ✓ Compare 2 weeks side-by-side: yes.
- **Q109** ✓ Compare strategies side-by-side — **multi-select up to N** (not just 2).
- **Q110** ✓ Stress-test: out of scope — no.
- **Q111** ✓ Presenter mode: yes.
- **Q112** ✓ Cross-asset extension: hard no.
- **Q113** ✓ User annotations on chart points: yes.
- **Q114** ✓ Per-holding fundamentals: yes.

## P2 FactSet pending

- **Q115** ⚠ User picked C, asks about D and F:
  - **D = CSV quoting fix** for names with commas (e.g., "Berkshire Hathaway, Inc." breaks naive CSV parsers — FactSet should quote these properly).
  - **F = Date labels on weekly column groups** in the CSV header (right now multi-period sections have repeating "Period Start Date" labels; would help if dates were in the header for human readability).
  - Top 3 by impact: **C (per-holding sector/country) — D (CSV quoting) — E (hit rate)**.
- **Q116** 🔥 keep adding to FACTSET_FEEDBACK.md as items surface.
- **Q117** ✓ Separate reference file accepted.

## P2 Open-ended

- **Q118** 📋 **"Simulate selling a position, see risk impact"** — out of strict scope (factor risk model is FactSet-side), but a "lite simulation that flags the impact and prompts user to confirm in FactSet" would be valuable. Worth scoping.
- **Q119** 📋 **Visualization upgrade is a HUGE emphasis.** All visuals: creative + easy + legend/info button + crisp + professional + informative + relevant. 🔥 Action: enumerate visualization tools/libraries available; instruct user how to enable any not currently in use.
- **Q120** 📋 **Audit for redundancy.** Recommend mergers / removals. *(Already started — cardFRB removed.)*
- **Q121** 📋 **10 candidate new-tile ideas** — separate brainstorm. Will deliver on next session.
- **Q122** ✓ Attribution = out of scope (FactSet-only).
- **Q123** 🔥 **Per-security spider chart for ranks** — already exists, sharpen it.
- **Q124** *(unanswered — likely will inform later)*
- **Q125** ✓ Numbers must match FactSet 100%. Particular concern: equity count vs total holdings (excluding cash baskets).
- **Q126** 📋 **List candidate confusing labels** — separate audit.
- **Q127** ⚠ "Copy Summary" = the executive-summary text generator. User wants editable bullets (add/remove before sending).
- **Q128** ✓ Mission statement: **"understand portfolio drivers with goal of maximizing idiosyncratic risk so fundamental selection matters most."** Bake into RR onboarding doc.
- **Q129** ✓ Robust audit system to catch silent breakage / drift / fabrication. **Continue building B115 integrity checks.**
- **Q130** ✓ 6-month vision: looks like a commercial product, design quality matches Bloomberg/FactSet workstation level.

## P2 Process

- **Q131** ✓ Weekly cadence: Mon AM (default A). **Critical:** automation so data is never > 1 week old.
- **Q132** ✓ Per-tile signoff (default A).
- **Q133** ✓ Snapshot folder for rollback after signoff: yes.
- **Q134** ✓ Quarterly schema review with FactSet: calendar invite.
- **Q135** ✓ CHANGELOG.md visible in dashboard footer: yes.

---

## 🔥 Top action items from this queue

| # | Action | Why |
|---|---|---|
| 1 | **MIGRATION_PLAN.md** end-to-end (GSC full-history → professional env → multi-account upload) | Q82 — blocks the massive run rollout |
| 2 | **Append-only weekly upload + additional-account upload pipelines** | Q84 — preserves history, enables continuous data accumulation |
| 3 | **Risk-budget spec & build** (definition / methodology / params / alerts) | Q107 — net-new PM workflow capability |
| 4 | **Visualization tools enumeration + setup instructions** | Q119 — design quality is the 6-month vision |
| 5 | **Compare-multiple-strategies side-by-side** | Q109 — frequently requested PM workflow |
| 6 | **Per-tile "About" popups + provenance + caveats** | Q88 — anti-fabrication / trust |
| 7 | **Session-resume / cross-thread context loading** | Q98 — fluency across sessions |
| 8 | **Redwood Risk wordmark/logo + header refresh** | Q69 — commercial polish |
| 9 | **Audit for tile redundancies** | Q120 — keep the dashboard tight |
| 10 | **TE/Total Risk/Active Risk synonym audit + canon doc** | Q43 — fundamental data correctness |
