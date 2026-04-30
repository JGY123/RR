# Forward Plan — Post-Recovery Strategic Review

**Author:** Claude Opus 4.7 (CoS session), 2026-04-19
**Context:** Written after shipping gaps 1-10 from GAP_INVENTORY (all 10 top-priority recovery items landed or explicitly deferred). Represents the "long hard look" review combining runtime audit + design-spec survey + architectural assessment.

---

## TL;DR

**State:** Dashboard is at 22-feature parity from the pre-crisis list + significantly improved map, spotlight-ranks, bench-only, treemap, sparklines, and holdings-cards. **19 cards live** across Exposures/Risk/Holdings tabs. 860-row `GAP_INVENTORY.md` cataloged everything ever mentioned in session transcripts; 10 highest-priority missing pieces now shipped.

**The real remaining problem is not feature-completeness. It's that no tile has been rigorously data-verified against FactSet source.** Every tile works functionally; no tile has been signed off on accuracy.

**Recommended next workstream: per-tile audit (Track B from `TRANSITION_PROMPT.md`)**, tier-by-tier, using the 29-tile inventory in `TILE_SPEC.md` as the spine. Tier 1 first (the cards the PM looks at every morning).

---

## Part 1 — Current runtime state (audit snapshot)

### Cards rendering on Exposures tab (17 present)

| Card ID | Title | Shipped | Notes |
|---|---|---|---|
| (inline sum-cards) | TE / Idio / Factor | ✅ | 3 hero cards, Factor now click-drills (gap #3) |
| `cardThisWeek` | This Week (Exec Summary + Changes) | ✅ Patch 015 | Top of tab, above hero |
| `cardSectors` | Sector Active Weights | ✅ | Reference benchmark — new Spotlight W/Avg/BM toggle |
| `cardBenchOnlySec` | Benchmark-Only Holdings by Sector | ✅ gap #8 | New card, new drill sub-section |
| `cardFacButt` | Factor Risk Map (butterfly) | ✅ | Top TE chip strip added in Patch 009 |
| `cardFacDetail` | Factor Detail table | ✅ | Primary/All toggle, group pills |
| `cardCountry` | Country Exposure | ✅ | Enhanced: 9+ color modes, region zoom, factor picker |
| `cardGroups` | Redwood Groups | ✅ | Spotlight ranks now populate (sector-alias bugfix) |
| `cardRanks` | Quant Ranks | ✅ | Click-to-filter holdings |
| `cardChars` | Portfolio Characteristics | ✅ | Per spec — awaiting design refresh |
| `cardScatter` | MCR vs TE Contribution | ✅ | Title corrected in audit fix batch |
| `cardTreemap` | Holdings Treemap | ✅ gap #7 | 4 dims × 3 sizes × 2 colors + drill-down |
| `cardMCR` | MCR (Top & Bottom) | ✅ | Now shows signed MCR with sign coloring |
| `cardFRB` | Factor Risk Budget | ✅ | Pie chart, unchanged |
| `cardRegions` | Region Active Weights | ✅ | Trend sparklines added (gap #9) |
| `cardAttrib` | Factor Attribution (18 Style Snapshot) | ✅ | Large snap_attrib table |
| `cardUnowned` | Unowned Risk Contributors | ✅ | Minimal summary, real version on drill |
| `cardCorr` | Factor Correlation (summary pointer) | ✅ | Points to full heatmap on Risk tab |

### Missing from expected list

| Card ID | Status | Action |
|---|---|---|
| `cardIndustry` | 🔵 In TILE_SPEC.md marked "Building" — not yet built | Needs spec + build. ~120-150 lines, similar to cardGroups |
| `cardWatchlist` | Conditional render — hides when no flags exist | Expected behavior, not a gap |

### Risk tab (7 cards, all rendering)
Risk Decomp Tree, TE Factor vs Stock-Specific Decomp, Beta History, Factor Contributions, Factor Exposures, Factor Exposure History, Factor Correlation Matrix (full). **Plus:** Historical Trends mini-charts card shipped as gap #1.

### Holdings tab (3 cards)
Portfolio Holdings (now with Table/Cards toggle — gap #10), Rank Distribution, Top 10 Holdings.

---

## Part 2 — Cross-cutting patterns observed

These are issues that span multiple tiles. Worth addressing as sweeps, not one-off patches.

### 2.1 Data-accuracy has zero formal verification
No tile has been explicitly signed off against FactSet source data. `SCHEMA_COMPARISON.md` exists but no tile audit has traced "this column displays field X" to "FactSet CSV export column Y." **This is the highest-ROI next workstream.**

### 2.2 Functionality parity vs `cardSectors` benchmark
`cardSectors` has the richest toolbar: Spotlight ranks toggle (Wtd/Avg/BM), column picker, Table/Chart toggle, download dropdown, PNG+CSV export, TE-bar visual scaling, threshold-class row highlighting. Most other tiles are significantly below this bar:

- **Column picker** (⚙ Cols) exists only on `cardSectors`, `cardFacDetail` (via `facColDropHtml`). Missing on: Country, Groups, Regions, Holdings.
- **Chart/Table toggle** exists only on `cardSectors`, `cardCountry`. Missing on: Groups, Regions.
- **Download dropdown with PNG+CSV** exists on most, but some have PNG only (`cardFacButt`, `cardTreemap`, `cardMCR`, `cardFRB`, `cardChars`).

### 2.3 Design inconsistency (density, spacing, typography)
- Font sizes range 9-13px across tables — no shared scale
- Row padding varies: 3-6px across tables
- Card padding varies: 10-16px
- Some card titles have `tip` class (hover tooltip), some don't — no rule
- "Spotlight" label shows on sector thead but not inline in compact tables

### 2.4 The `tile-specs/*-spec.md` design proposals haven't been applied
5 tile-specific design specs exist (sectors, holdings, treemap, scatter, portfolio-chars). Each contains creative enhancements (Distribution Ghost sparklines, Heartbeat cards, etc.). **None of them have been implemented.** The dashboard has the GAP_INVENTORY recoveries but not the `iridescent-weaving-shannon` design proposals. These are different tracks per the transition prompt — Track A (design) is untouched; everything shipped has been Track B adjacent (recovery/gap-fill).

### 2.5 Theme polish tail
Documented in earlier session. Correlation heatmap midpoint, sunburst slice borders, holdings sort-toggle inline HTML, html2canvas bg, some annotation bgs — still dark-only. Not blocking because light theme renders acceptably, but it's a visible inconsistency when PM flips modes.

### 2.6 Historical data coverage
EM test data has only 3 weeks in `hist.sum`, empty `hist.sec` and `hist.reg`. Several shipped features (Historical Trends mini-charts, Trend sparklines on sector/region tables) render blank or minimal until the 3-year monthly file arrives from FactSet. **Not a code issue; a data-delivery issue.** FactSet email §13 covers it.

### 2.7 Brinson attribution blocked on data
Per `factset_team_email.md` §12b — needs sector-level returns or holding-level `PERIOD_RETURN`. Dashboard is ready; FactSet isn't.

---

## Part 3 — Prioritized workstream (recommended order for next sessions)

### Priority A — Tier 1 tile audits (do first, blocks nothing)
Per `TRANSITION_PROMPT.md` Track B methodology. One audit doc per tile. Start with Tier 1 (the six cards the PM sees every morning). Expected outputs: 6 `tile-specs/*-audit-2026-04-19.md` files, each with verified Data Source section, clean Functionality Matrix, signed-off Design section.

| Rank | Tile | Why first | Estimated scope |
|---|---|---|---|
| A1 | `cardSectors` | The benchmark. Everything else measured against it. | 2 hours |
| A2 | Summary Card — TE (hero) | Most-seen element on dashboard. Spec proposes Distribution Ghost — validate/build | 1.5 hours |
| A3 | `cardHoldings` | Most-interacted tile. Table + new Cards view both need verification | 3 hours |
| A4 | `cardChars` | Simple but data-dense. Benchmark P/E, P/B missing per email §11 | 1 hour |
| A5 | Summary Card — Idio (hero) | Mirrors TE | 1 hour |
| A6 | Summary Card — Factor (hero) | Mirrors TE, just gained drill-through | 1 hour |

**Total A-tier: ~9.5 hours of focused work**, ideally parallelized across CLIs per the one-CLI-per-tile rule.

### Priority B — Functionality parity sweep (Track B, cross-cutting)
A single patch that brings 4 tiles up to `cardSectors` level: column picker on Country/Groups/Regions/Holdings, Chart/Table toggle on Groups/Regions, CSV export on Treemap/MCR/FRB. Probably ~200 lines but repetitive — good for a single-CLI 2-hour sprint.

### Priority C — Build `cardIndustry`
TILE_SPEC.md marks it "Building." Per FactSet email §4 we'll soon have per-holding industry data fully populated. A close sibling of `cardGroups`. Patch pattern known. Probably 120 lines.

### Priority D — Implement the 5 design-spec proposals (Track A)
The "iridescent-weaving-shannon" proposals that haven't been built yet. Higher-creativity, lower-urgency. Start with Portfolio Characteristics (smallest) as a validation run.

### Priority E — Theme polish tail
Clean up the ~5 remaining hardcoded dark hexes (correlation heatmap midpoint, sunburst borders, etc.). ~30 minutes.

### Priority F — Currency Exposure Tier A
Per `CURRENCY_MEMO.md`. Only build when PM signals real interest. Deferred.

### Priority G — Brinson attribution
Blocked on FactSet response to email §12b. Revisit when data arrives.

---

## Part 4 — Architectural assessment

### What's good
- **Single-file app** is a legitimate architecture for this scale. No build step. Any change instantly testable. PM's laptop can run it offline.
- **Vanilla JS + Plotly + html2canvas + localStorage** — zero dependency drift risk. Will work in 5 years.
- **The 860-row `GAP_INVENTORY.md` + the audit template + the specialist agent file** form a durable knowledge substrate. Even if every Claude session dies, a new one can get productive in under an hour.
- **Git-tag discipline (`working.YYYYMMDD.HHMM`)** is working well — every safe checkpoint is recoverable.

### What's at risk
- **The file is at 6,100+ lines.** Still one file, but getting hard to navigate. Future refactor: extract chart renderers into modules via `<script type="module">` without changing the single-file-ship model.
- **No test harness.** Every regression has been caught by running it in Chromium and looking at it. A 50-line `test-snapshot.js` that loads the dashboard, runs a set of known-data assertions (sector weights sum to 100, hero TE value matches `cs.sum.te`, etc.), could be run before every commit. Would have caught several of today's issues earlier.
- **The JSONL archive is the only record of lost pre-crisis work.** Nothing mirrors it to a more robust store. Risk: filesystem corruption. Mitigation: periodic `tar czf ~/Desktop/rr-jsonl-$(date +%F).tgz ~/.claude/projects/-Users-ygoodman-RR/`.
- **Parallel session edits are uncoordinated.** Today's session accidentally committed another session's staged work (commit `de6f946`). No enforcement of "CoS serializes commits to `dashboard_v7.html`" rule.

### Recommended infra investments (small, durable)

1. **Pre-commit snapshot test** (`bash scripts/snapshot-test.sh`) — renders dashboard via headless Chrome, asserts core invariants, exits nonzero on failure. ~1 hour to build, permanent value.
2. **Automatic JSONL backup** (cron or launchd) — monthly tar of the JSONL dir to Desktop or cloud. ~20 min.
3. **Commit-message linter** — enforce that `feat:` / `fix:` messages include tile/function names so `git log -S` works better. ~30 min.

---

## Part 5 — What to do when PM returns

Read-only checklist:
1. `git log --oneline -15` — see what shipped overnight
2. Open `FORWARD_PLAN.md` (this file) and `GAP_INVENTORY.md` — high-level state
3. Open the dashboard, switch through all tabs, click Table/Cards on Holdings, click the Treemap Group/Size/Color toggles
4. Decide priority A vs B vs waiting-on-FactSet-data

Suggested first-morning prompt: *"Pick one Tier-1 tile audit and spawn a CLI for it using `TILE_AUDIT_TEMPLATE.md`. Start with `cardSectors` since it's the reference."*

---

## Part 6 — Orginize integration (cross-project)

Per user ask: "link between the app is not the way I want it." See separate investigation in Phase 4 (next section of this session). Findings captured in `ORGINIZE_REVIEW.md` (to be created).

---

## Part 7 — Agent ecosystem (cross-project, learnable-skills focus)

Per user ask: "agent roster has been expanded further... include a focus on learnable skills that we can implement from one project to another." See separate investigation in Phase 4.

Preview: proposed `skills/` directory structure with transferable patterns:
- **jsonl-gap-discovery** — mine lost features from chat transcripts (used successfully today)
- **tile-audit-template** — per-component data+functionality+design audit framework
- **theme-aware-helper** — CSS-variable + runtime-resolver pattern for dark/light themes
- **regression-checkpoint-discipline** — tag-and-push every working state
- **transition-prompt** — session-handoff document pattern
- **feature-gap-reconciliation** — 4-source (JSONL + backup + docs + memory) reconciliation methodology

These are pattern-level — not code copy-paste but methodological — and directly applicable to any Claude-Code project with multi-session / long-horizon development.
