# RR Roadmap — 2026-05-05

**Drafted:** 2026-05-05 morning, post-showing
**Status:** strategic plan; review with user before committing to dates
**Companion docs:** `STRATEGIC_REVIEW.md` (May 1 baseline) · `STRATEGIC_REVIEW_NEXT.md` (May 4 follow-on) · `ARCHITECTURE.md` (current state) · `HISTORY_PERSISTENCE.md` (B114 design) · `MIGRATION_PLAN.md` (deployment paths)

---

## TL;DR

Three big questions to land in the next 1-3 months:

1. **Software vs HTML?** Recommendation: **stay HTML for the dashboard, add a Python ingest service**. The single-file HTML model is one of RR's strengths (anti-fabrication discipline, no framework opacity, easy to deploy). The scaling problem is the data layer, not the UI. Solve it with a thin backend + compressed data, not a full rewrite. Concrete roadmap below.
2. **6 → ~25 accounts (1.6 GB → ~5 GB) — does it scale?** Yes, with three changes: gzip the per-strategy files (7.5× compression on a sample → 5 GB becomes ~700 MB), formalize the weekly ingest pipeline (B114 cumulative-merge already shipped, just needs scheduling), and make the dashboard tolerate variable strategy counts (currently asserts "6 worldwide" in places).
3. **What about the firm rollout side?** PMs, desks, training, presentations, reading materials — covered in §7 below. Firm-wide rollout depends on a small set of shippable artifacts plus quarterly cadence rituals. None of them are blocking; all of them compound.

This doc is the strategic frame. It doesn't make decisions you haven't OK'd; it surfaces them.

---

## 1. Where we are today (concrete numbers)

| Dimension | Current state |
|---|---|
| Strategies in production | 6 (ACWI, IDM, IOP, EM, GSC, ISC) |
| Per-strategy file sizes | 19 MB (GSC) → 526 MB (ISC); avg 281 MB |
| Total `data/strategies/*.json` | **1.6 GB** uncompressed |
| Per-strategy week count | 383–618 weeks (7-12 yrs) |
| Total weekly snapshots | ~3,082 sector-weeks across 6 strategies |
| Parser version | 3.1.1 / FORMAT 4.3 |
| Dashboard size | 880 KB (single HTML file) |
| Tests | 26 active passing (13 B114 + 7 F19 + 6 legacy) |
| Smoke test | 🟢 21/21 ALL PASS (just closed the parse-bomb) |
| Tile audits filed | 14 of ~30 tiles have audit docs; cycle ongoing |
| Open inquiries to FactSet | F18 (per-holding %T sums non-100%; letter ready) · F12 (long-tail bench-only %T_implied) · several smaller |
| Cumulative merge architecture (B114) | shipped + tested + CLI + `--merge` flag in load_multi_account.sh; first production run pending |
| F19 parser fix | shipped; verified end-to-end on real data — keys now present, but FactSet stopped shipping per-period values; F12(a) MCR-derived fallback is canonical today |
| F18 disclosure footers | 5 tiles (cardRiskByDim · cardRanks · cardRiskDecomp · cardTreemap · cardUnowned) |
| Documentation | ARCHITECTURE.md · STRATEGIC_REVIEW + _NEXT · PM_ONBOARDING · DRILL_MODAL_MIGRATION_SPEC · LESSONS_LEARNED (16 lessons) · SOURCES.md · FACTSET_FEEDBACK · HISTORY_PERSISTENCE · MIGRATION_PLAN · CHANGELOG · BACKLOG |

Everything in this list is good. None of it is broken. The roadmap is about scaling what works, not fixing what's broken.

---

## 2. The big question — software vs HTML

### The argument for "real software" (full web app)

A typical PM-facing dashboard at scale is a React/Vue/Svelte app with a Python/Node backend, a database, auth, and shared state. Industry default. Reasons people do it:
- Component reuse (true components, not template literals)
- Real type system (TypeScript)
- Backend processing (heavy data transforms server-side)
- Multi-user features (shared notes, watchlists, comments)
- Auth/SSO
- Better tooling for testing (Jest, Playwright, Storybook)

### The argument for staying single-file HTML

- **Anti-fabrication discipline is enforced by the architecture.** One source of truth (Python parser) → one render target (the HTML). The April 2026 crisis happened because we had FOUR parsing paths colliding. Going to a framework means more paths, more abstractions, more places for drift.
- **Zero opacity.** Every cell on screen traces to a documented field via `SOURCES.md`. With React + a state library, that traceability is harder to maintain without discipline that doesn't yet exist in this codebase.
- **Deployment is trivial.** Currently: serve a static folder, open a URL. With backend + DB: deployment runbook, restart procedures, monitoring, secrets management, etc.
- **The 13K LOC is manageable.** It's not 130K. The Phase A-K refactor showed the codebase responds well to discipline (`tileChromeStrip`, design tokens, lint enforcement). A rewrite would throw that away.
- **The user's framing is correct: "make it right, scale it slowly, become more expert each cycle."** A rewrite breaks that bias. It's a "ship fast, regress everywhere" move dressed up as scaling.

### The recommendation

**Stay HTML for the dashboard. Add a small Python ingest service for everything that doesn't belong in the browser.** Concretely:

- **What stays in the browser:** rendering, interaction, drill modals, exports, watchlist state in localStorage. The dashboard becomes a presentation layer. ~13K lines of JS, no rewrite.
- **What moves to a Python service:** weekly CSV ingest, B114 cumulative merge, `verify_*.py` continuous monitoring, history persistence, scheduled jobs, integrity assertions across the corpus. All this is already mostly Python; the service just gives it a cron schedule + a simple HTTP API for the dashboard to read instead of static files.
- **Data layer:** keep per-strategy JSON for now (compressed via gzip — see §4); migrate to DuckDB only if/when query patterns become complex enough that JSON loads are the bottleneck.

The end state is "static HTML + thin Python backend" — not "full web app." Industry term: "lightweight backend, smart frontend."

### When to revisit this decision

Revisit if any of these become true:
1. Multi-user collaborative features (shared notes editable by multiple PMs simultaneously) become a hard requirement
2. Auth/SSO becomes a hard requirement (today: dashboard runs locally, no auth)
3. The dashboard needs to render >10 GB of data per session
4. Per-firm theming + branding becomes a sales requirement
5. PM headcount growth (say, 50+ daily users) means per-user state can't live in localStorage

None of these are true today. None look likely in the next 6-12 months. So: HTML stays.

---

## 3. Scale plan — 6 → ~25 accounts, 1.6 GB → ~5 GB

### Where the scaling pain shows up

| Bottleneck | Today (6 strategies) | At 25 strategies | Mitigation |
|---|---|---|---|
| Total `data/strategies/*.json` | 1.6 GB | ~5 GB linear | gzip → 700 MB |
| Largest single file (ISC) | 526 MB | ~600 MB if scale linear | per-strategy lazy-load already handles this; browser fetches only the active strategy |
| `latest_data.json` monolith | 1.97 GB | ~6 GB | **stop using it as the dashboard source** (already done — dashboard reads split files); keep monolith only as a parser intermediate, gzip + archive |
| Parse time on full multi-account CSV | ~5-15 min wall (1.83 GB → JSON) | could be 10-30 min | parser already uses streaming-friendly patterns; profile if it becomes a problem |
| Schema fingerprint drift | every quarter on average | same | already handled by `verify_factset.py` |
| Strategy picker hardcoded counts | smoke asserts "6 worldwide accounts" | breaks at 7+ | **fix needed** — make the smoke + verify scripts data-driven |
| Git repo size | 1.6 GB committed (likely via .gitignore exclusions) | ~5 GB | commit gzipped split files only; uncompressed is gitignored |
| Dashboard initial load time | ~1-2s on local | same (fetches 1 strategy at a time) | unchanged |
| Memory footprint (parser) | 23 GB peak on full parse (per F19 re-parse profile) | could be 30-40 GB | profile + optimize when needed; today this happens off-line in batch |

The honest read: **the scaling problem is mostly the disk footprint of JSON files.** Everything else is either already lazy or already handled. gzip + a slightly more dynamic strategy picker closes most of the gap.

### Concrete scale changes (in priority order)

**A. gzip per-strategy files** (~2 hours)
- Compress `data/strategies/<ID>.json` → `<ID>.json.gz`
- Modify `merge_cumulative.py` and `load_multi_account.sh --merge` to write gzipped
- Modify dashboard's fetch path to read gzipped (browser handles `Content-Encoding: gzip` natively when served)
- Effect: 1.6 GB → 200 MB on disk, 5 GB → 700 MB at 25 strategies. **Single biggest win.**

**B. Make scripts data-driven over the strategy list** (~1 hour)
- `smoke_test.sh` line 81 currently asserts: "all 6 worldwide accounts present"
- `verify_factset.py` and `verify_section_aggregates.py` should iterate `data/strategies/index.json` instead of hardcoded names
- The dashboard's strategy picker already auto-discovers from `index.json` — confirmed already data-driven
- Effect: dashboard works at 6, 7, 25, 50 strategies without code changes

**C. Per-strategy schema fingerprinting** (~2 hours)
- Currently `~/RR/.schema_fingerprint.json` is one file for the whole CSV
- With multiple files (worldwide + domestic + future), each file has its own schema
- Track fingerprints per-source-file, not per-codebase
- Effect: when SCG/Alger domestic file lands, doesn't trigger false-positive drift on the worldwide model

**D. Memory profile the parser** (~3 hours)
- 23 GB peak on a 1.83 GB CSV is high. With 5 GB CSVs, may hit 50+ GB peak (problem on a 16 GB laptop).
- Profile with `tracemalloc` or `memory_profiler`
- Likely culprits: holding all rows in memory before assembly; building per-period dicts that grow with strategy count
- Mitigation: stream parsing where possible; per-strategy-section processing
- Defer until it actually breaks something (today: 1.83 GB CSV runs fine on 16 GB Mac)

**E. CSV parse parallelism** (~4-6 hours, optional)
- Today: `factset_parser.py` is single-threaded
- For 25 strategies of historical depth, could parallelize per-strategy assembly
- Likely 3-5× wall-time speedup on multi-core
- Defer until parse time crosses ~30 min threshold

---

## 4. Weekly update pipeline — operational design

### What the weekly cadence looks like

PM uploads a fresh CSV every Monday morning (or however often). The pipeline:

```
1. CSV lands at ~/Downloads/factset_export_YYYY-MM-DD.csv
   (or in a watched folder, or via a UI upload)
              │
              ▼
2. ./load_multi_account.sh --merge ~/Downloads/<file>.csv
   (already exists post-B114)
              │
              ▼
   ┌──────────┴──────────┐
   ▼                     ▼
factset_parser.py   verify_factset.py
(parse to JSON)     (22+ pass/fail checks)
   │                     │
   ▼                     ▼
   └──────────┬──────────┘
              ▼
3. merge_cumulative.py --new latest_data.json --source-csv <file>
   (B114 — append-only into data/strategies/<ID>.json.gz)
              │
              ▼
4. verify_section_aggregates.py --latest
   (L2 monitor — confirms section-aggregate invariants on new data)
              │
              ▼
5. data/strategies/index.json rebuilt with fresh slim summaries
              │
              ▼
6. Dashboard auto-loads the new state on next refresh
```

This is 95% built today. Steps 1, 2, 3 are wired (post-B114). Step 4 is wired in `smoke_test.sh`. Step 5 is wired in `merge_cumulative.py`. Step 6 works.

### What's missing for "weekly cadence"

**P1 (do soon):**
- **First production exercise of `--merge`** — the CSV from May 1 is still the latest. Run `./load_multi_account.sh --merge ~/Downloads/risk_reports_sample.csv` to validate the pipeline + lay down the first `merge_history[]` entry in production data. **This is item A2 from STRATEGIC_REVIEW_NEXT.**
- **Notification on parser failure** — today, if parse fails, you find out by opening the dashboard and seeing nothing. Add a desktop notification (macOS: `osascript -e 'display notification ...'`) or an email when verify_factset throws RED.
- **Pre-flight check before merge** — `merge_cumulative.py --dry-run` already exists; wire `load_multi_account.sh --merge` to run dry-run first and abort if anomalies (e.g., a strategy disappears from the new ingest).

**P2 (do after first 1-2 weekly cycles):**
- **Scheduled run** — `launchd` (macOS) or `cron` job that watches `~/Downloads/` for new factset_export*.csv and runs the pipeline. Or polls a network share if the firm provides CSVs centrally.
- **Update audit trail** — every merge stamps `merge_history[]` (already shipped). Add a "what changed this week" summary that's auto-generated.
- **Post-merge integrity sweep** — run `verify_section_aggregates.py` (full mode, not just `--latest`) and email a summary to the PM.

**P3 (later):**
- **Multi-source ingest** — if SCG + Alger ship in a separate "domestic" CSV, the pipeline merges both into the same per-strategy split files. The merge function handles this already; just needs orchestration.
- **Web-based upload UI** — drop CSV into a browser tab, kick off the pipeline. Avoids terminal usage. Implies the lightweight backend service from §2.

### Weekly cadence ritual (process, not code)

- **Monday morning:** new CSV arrives. Run the pipeline (one command). Confirm the verifier output is green. Spot-check 1-2 KPIs against last week.
- **First in-browser open of the week:** check console for `_b115AssertIntegrity` pass. Verify the strategy you're showing has the latest week.
- **Friday end-of-week:** tag the state (`weekly.YYYY-MM-DD`). Push to remote.
- **Monthly:** open `STRATEGIC_REVIEW_NEXT.md` (or a fresh re-baseline), review what shipped + what's queued. Pick next month's priorities.
- **Quarterly:** run the full audit cycle (parallel `tile-audit` subagents on every tile). Refresh `LESSONS_LEARNED.md` with new pain points.

---

## 5. Other technical work — fixes/adds/cleanups in priority order

Surfaced from this week's audits + while writing this doc.

### Tier 1 — accuracy / correctness (before next showing)

| # | Item | Source | Estimate |
|---|---|---|---|
| T1.1 | First production `--merge` run (validates B114 end-to-end) | STRATEGIC_REVIEW_NEXT A2 | 5 min |
| T1.2 | Send F18 letter (or schedule the send) | STRATEGIC_REVIEW_NEXT A1 | 1-2 hr human |
| T1.3 | Run Tier-3 audit fix sweep round 2 (~30 YELLOW polish items) | various audit docs | 2-3 hr |
| T1.4 | Audit cardFacRisk + cardCalHeat (Tier-2, never re-audited this week) | new audit | 2 hr |
| T1.5 | Audit drill modals (oDr / oSt / oDrCountry / oDrChar / oDrAttrib) for data-integrity | new audit | 3 hr |
| T1.6 | Verify cardCorr fullscreen path (audit F2 — needs in-browser test) | cardCorr-audit-2026-05-04 F2 | 15 min |

### Tier 2 — scale + ops (next 2-4 weeks)

| # | Item | Source | Estimate |
|---|---|---|---|
| T2.1 | gzip per-strategy files (7.5× compression) | §3.A above | 2 hr |
| T2.2 | Data-drive smoke + verify scripts over strategy list | §3.B above | 1 hr |
| T2.3 | Per-strategy schema fingerprinting | §3.C above | 2 hr |
| T2.4 | Pre-flight `--dry-run` gate in load_multi_account.sh `--merge` | §4 P1 above | 1 hr |
| T2.5 | Desktop notification on parser failure | §4 P1 above | 1 hr |
| T2.6 | Drill modal migration Phase A (helpers) + Phase B (oDrMetric canary) | DRILL_MODAL_MIGRATION_SPEC | 3 hr |
| T2.7 | Tier-3 audit fix sweep round 2 (cardCashHist remaining, cardWatchlist remaining, etc.) | various audit docs | 3 hr |

### Tier 3 — quality (next 1-3 months)

| # | Item | Source | Estimate |
|---|---|---|---|
| T3.1 | Drill modal migration Phases C-G | DRILL_MODAL_MIGRATION_SPEC | 4-5 hr |
| T3.2 | Playwright e2e harness | STRATEGIC_REVIEW_NEXT C1 | 3-4 hr |
| T3.3 | PM_ONBOARDING screenshots + walk-through video | PM_ONBOARDING | 1-2 hr |
| T3.4 | "first Monday" cheat sheet — printable 1-pager | new | 1 hr |
| T3.5 | Lightweight Python service (FastAPI) — see §2 recommendation | §2 above | 6-8 hr |
| T3.6 | Auto-generated "what changed this week" summary | §4 P2 above | 2 hr |
| T3.7 | Memory profile the parser | §3.D above | 3 hr |

### Tier 4 — long-shelf (post first firm-wide rollout)

| # | Item | Source | Estimate |
|---|---|---|---|
| T4.1 | DuckDB migration (only if JSON loads become a bottleneck) | §3 mitigation | 1-2 weeks |
| T4.2 | Linux server deployment runbook | MIGRATION_PLAN | 1 day |
| T4.3 | Per-firm theming + auth/SSO (only if multi-firm demand) | STRATEGIC_REVIEW C3 | 1-2 weeks |
| T4.4 | DR / backup strategy formalized | STRATEGIC_REVIEW C4 | 1 day |
| T4.5 | CSV parse parallelism | §3.E above | 4-6 hr |

---

## 6. Things I noticed / recommend fixing along the way

(Surfaced while writing this doc; small enough to commit alongside the roadmap or in the next batch.)

- **`smoke_test.sh` parse-bomb** — fixed today (was line 11597, replaced bad `\\\'` escape with `&apos;` HTML entity). 21/21 ALL PASS now.
- **Strategy hardcodes** — at least three places assume "6 worldwide" (smoke_test.sh:81 · parts of verify_factset.py · maybe others). Make all data-driven.
- **`latest_data.json` 1.97 GB sitting around** — gitignored but consumes disk. Document in MIGRATION_PLAN that it can be safely deleted after a successful merge (it's a parser intermediate; the canonical state is `data/strategies/*.json.gz`).
- **No "version" badge on the dashboard** — the user has to dig into JSON to know what FORMAT_VERSION is loaded. Add a tiny version stamp in the footer or About-the-app dialog: "Dashboard 2026-05-05 · Parser 3.1.1 · Format 4.3 · Last ingest YYYY-MM-DD."
- **`merge_history[]` not surfaced anywhere in the dashboard** — once B114 starts running, the audit trail is in JSON but not visible. A small "data freshness" indicator + "history" tooltip would help PMs trust the data.
- **No automated weekly diff** — when a new ingest lands, what changed? Today PMs have to compare by eye. A quick `weekly_diff.py` that emits "TE moved from X to Y · 5 new holdings · etc." would be high-leverage.
- **Universe pill count strip is great but only updates after pill click** — should also update on strategy switch + week switch.
- **No "what would FactSet's documented invariant give us if we corrected for F18" toggle** — debatable; might be premature given F18 is unresolved. Note for later.

---

## 7. Organizational / firm-rollout track

You asked about reading materials, desks, presentations. Here's the org-side roadmap.

### 7.1 Reading materials — for PMs and analysts using RR

**Existing internal:**
- `EXECUTIVE_SUMMARY.md` — 90-second pitch
- `PRESENTATION_DECK.md` — 12-slide walk-through
- `PM_ONBOARDING.md` — first Monday morning cheat sheet
- `PRESENTATION_DAY_GUIDE.md` — operator's manual for showings
- `LAUNCH_READINESS.md` — readiness checklist

**To add:**
- **"Why we built RR" — 2-page primer** for new PMs joining the firm. Origin story + how it differs from FactSet PA + what discipline we hold (anti-fabrication, audit cadence, F-item tracking).
- **Factor primer** — short reader explaining Axioma factors (Volatility, Value, Growth, Profitability, etc.). What each means, how they're orthogonalized, why the dashboard shows them. Lets PMs understand the Risk tab without consulting external docs.
- **"%T / %S in plain English"** — one-pager. We've been deep in this all week (F18 inquiry). The PM needs a clean explanation: %T = per-holding share of portfolio TE; %S = stock-specific component; their sum behavior is documented but observed range is wider (see F18). When F18 resolves, update.
- **Quarterly "state of the dashboard" memo** — what changed, what's queued, what's escalated to FactSet. Auto-generated from CHANGELOG + STRATEGIC_REVIEW. Sent to PMs + risk team quarterly.

### 7.2 Desks — different desks have different needs

The current dashboard targets the international desk (6 worldwide-model strategies). Other desks the firm runs (or will run):

- **International equity (current)** — ACWI, IDM, IOP, EM, GSC, ISC. Worldwide risk model. Current dashboard is already shaped around their needs.
- **Domestic equity (forthcoming)** — SCG + Alger accounts, US-only. Domestic risk model (smaller factor set, no FX/Country/Currency macros). Per CLAUDE.md, the parser is header-driven and adapts; dashboard will work but factor heatmap will look thinner.
- **Fixed income** — different metrics entirely (duration, OAS, key-rate exposures). Out of scope for v1 but the architecture (parser + JSON + tile contract) is general enough that an FI variant could fork the codebase.
- **Multi-asset / asset allocation** — would need yet a different metric set. Same comment: forkable.

**Per-desk customization** is light today. Universe pill, strategy picker, factor cols, watchlist all per-user. Per-DESK customization (different default tabs, different KPI layout) is a future feature — could ship via a `desk` query parameter or a per-firm config file.

### 7.3 Presentations — stakeholder communication cadence

| Audience | Frequency | What they want | What we ship |
|---|---|---|---|
| **PMs (daily users)** | Daily | "What changed this week, what's escalated, what should I look at first?" | Dashboard + PM_ONBOARDING + email-snapshot button |
| **Risk team** | Weekly / Monthly | "Are the numbers verified? Any open data inquiries?" | verify_*.py output + FACTSET_FEEDBACK + L2 monitor green |
| **Senior leadership / firm ops** | Quarterly | "How is the dashboard adoption + ROI? What's the roadmap?" | Quarterly memo (TBD) + STRATEGIC_REVIEW |
| **External (FactSet, vendors)** | Per inquiry | "We have a question about your data layer." | F-letters (F18, F12 templates ready) |
| **Board / investment committee** | Semi-annual | "Show us the dashboard; explain the discipline." | Live demo using `PRESENTATION_DAY_GUIDE` + `SHOWING_TOMORROW` template |

**To add:**
- **Quarterly memo template** — auto-fillable from CHANGELOG + STRATEGIC_REVIEW. ~1 hr to draft once.
- **Demo script library** — one per audience type. The 5-min PM demo (in `SHOWING_TOMORROW`) is the canary; need a 10-min senior-leadership variant + a 30-min deep-dive.
- **Recorded walkthrough video (~5 min)** — for asynchronous onboarding. Would replace the "schedule a 30-min walkthrough" follow-up with most new users. Once recorded, ships forever.

### 7.4 Training / certification

Today: zero formal training. PMs learn by trial. That's fine at 6 daily users; at 25+ it stops scaling.

**To add (when daily users pass ~10):**
- **30-minute orientation session** — recorded video + live Q&A by an analyst who's been using RR for a quarter
- **Certification quiz** — 10 multiple-choice questions on conventions (em-dash means missing, ᵉ means derived, MCR is not a percent, F18 is the open inquiry on per-holding %T, etc.). Pass = unlocked watchlist write access (or some similar carrot).
- **Office hours** — once a week, 30-min, the dashboard maintainer answers questions live. Lowers the "who do I ask" friction.

### 7.5 Knowledge management — keeping it organized

We've built up ~25 active markdown docs in this repo. They're navigated via `docs/INDEX.md` but the structure is flat. As we add roadmap, training, presentation materials:

**Proposed reorganization:**
```
docs/
├── INDEX.md
├── strategy/
│   ├── ROADMAP.md           ← this doc
│   ├── STRATEGIC_REVIEW.md
│   ├── STRATEGIC_REVIEW_NEXT.md
│   ├── HISTORY_PERSISTENCE.md
│   └── MIGRATION_PLAN.md
├── operations/
│   ├── SESSION_GUIDE.md
│   ├── SESSION_STATE.md
│   ├── CHANGELOG.md
│   ├── BACKLOG.md
│   ├── REFACTOR_PLAN.md (frozen)
│   └── REFACTOR_AUDIT.md (frozen)
├── data-integrity/
│   ├── LESSONS_LEARNED.md
│   ├── SOURCES.md
│   ├── FACTSET_FEEDBACK.md
│   ├── FACTSET_INQUIRY_F18.md
│   ├── PA_TESTS_F18.md
│   ├── FACTSET_INQUIRY_TEMPLATE.md
│   └── DATA_INTEGRITY_MONITOR.md
├── presentations/
│   ├── SHOWING_TOMORROW.md
│   ├── PRESENTATION_DAY_GUIDE.md
│   ├── PRESENTATION_DECK.md
│   ├── EXECUTIVE_SUMMARY.md
│   └── LAUNCH_READINESS.md
├── pm-facing/
│   ├── PM_ONBOARDING.md
│   ├── (factor primer — to write)
│   ├── (%T-in-plain-english — to write)
│   └── (quarterly memo template — to write)
└── architecture/
    ├── ARCHITECTURE.md
    └── DRILL_MODAL_MIGRATION_SPEC.md
```

Today: flat. Future: hierarchical, with INDEX.md as the navigator. Migration cost: ~1 hr to move + update internal links + git mv to preserve history.

**Defer this** until docs/ count reaches ~40+. Premature reorganization is its own kind of friction.

---

## 8. Phased roadmap by horizon

### Next 1-2 weeks (showing follow-ups + "do tomorrow")

**This week (after today's showing):**
1. Send F18 letter (1-2 hr human work)
2. First production `--merge` run (5 min)
3. Tier-3 audit fix sweep round 2 (3 hr) — closes the YELLOW polish backlog from May audit cycle
4. **Quick wins from §6:** version badge in dashboard footer · data freshness indicator · weekly_diff.py prototype

**Next week:**
1. gzip per-strategy files (T2.1) — biggest scaling win
2. Data-drive smoke + verify scripts (T2.2)
3. Pre-flight `--dry-run` gate (T2.4)
4. Drill modal migration Phase A canary (T2.6)

### Next 1-3 months (scale + new desks)

1. Per-strategy schema fingerprinting (T2.3)
2. Drill modal migration Phases B-G (~6 hr)
3. SCG + Alger domestic file ingest (when CSV lands) — exercise the schema-fingerprint path
4. **Lightweight FastAPI ingest service** (T3.5) — replaces `load_multi_account.sh` orchestration; gives us notifications, scheduled runs, web upload
5. Playwright e2e harness (T3.2)
6. Quarterly memo template (§7.3)
7. PM_ONBOARDING screenshots + walk-through video (T3.3)

### Next 3-6 months (firm-wide rollout if/when greenlit)

1. Linux server deployment (MIGRATION_PLAN Path B, formalized)
2. Quarterly tile-audit cadence (calendar reminder + structured run)
3. Multi-desk variants (when fixed income / multi-asset desks express interest)
4. DR / backup strategy formalized (T4.4)
5. **Decision point:** auth/SSO needed? Per-firm theming needed? If yes → spend the 1-2 weeks. If no → skip indefinitely.
6. **Decision point:** DuckDB migration? Only if JSON loads in browser cross 5 GB and load times exceed 2-3 seconds.

---

## 9. Risks and watchpoints

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| FactSet ships a CSV format change | Quarterly average | Medium | Schema fingerprint catches it; verify_factset.py classifies as PARTIAL not FAIL; manual delete-fingerprint to acknowledge. **Already shipped.** |
| First B114 production merge surfaces edge cases | First-time risk | Low | Tested on synthetic + real data dry-run. Roll back via `git reset` + restore from `working.YYYYMMDD.HHMM.pre-X` tags. |
| F18 reply contradicts our assumption (e.g., "Σ %T should be 100%, you have a bug") | 30% | Medium-High | If parser bug: fix it, ship, close F18. If subtle (signed math): fold into docs + update About copy. **Defensive UI footers stay until F18 closes.** |
| Multi-account CSV adds a new strategy with unfamiliar shape | Possible | Low-Medium | parser is header-driven; verify_factset auto-runs; fingerprint flags drift. Manual audit needed once when SCG+Alger lands. |
| 16 GB Mac runs out of memory on a future 5 GB CSV | Likely at scale | Medium | Profile parser memory now; defer optimization until needed; worst case → rent a 32 GB workstation for ingest only |
| Daily users exceed localStorage quota (5-10 MB) | Unlikely (state is light) | Low | Move heavy preferences to IndexedDB if it ever happens (already designed in HISTORY_PERSISTENCE Option B) |
| Dashboard ships a regression | Daily risk | Medium | smoke_test.sh + 26 parser tests + push-discipline + tag-before-risky-edits. Tracked + manageable. |
| Audit cadence lapses | Quarterly risk | Medium | Calendar reminder + STRATEGIC_REVIEW refresh. Not yet formalized; T3.3 covers. |
| Documentation drift (docs say one thing, code does another) | Ongoing | Medium | Tile audits catch it (cardUnowned about-registry was stale + fixed in cycle 4). Quarterly audit cadence formalizes. |

---

## 10. Open questions for user

1. **Software vs HTML?** I've recommended HTML stays. Confirm or push back.
2. **gzip per-strategy files?** (T2.1) — biggest scaling win, ~2 hr work, breaks browser-cache for old uncompressed files (one-time pain). OK to proceed?
3. **F18 letter recipient name?** Letter is ready; need a person.
4. **Preferred weekly cadence ritual?** (Monday upload + Friday tag, or different?)
5. **When does SCG + Alger domestic CSV arrive?** Triggers the per-strategy schema fingerprint work.
6. **Daily user count target for next quarter?** (Drives whether T3.4 quiz/cert + T3.5 backend service get prioritized.)
7. **Recorded walkthrough video — is anyone available to record + iterate?** (T3.3, defers if no.)

---

## 11. Closing thought

The hardest engineering work on RR was done in April + early May — anti-fabrication discipline, the parser, the tile contract, F12(a)+F19, B114. **That work compounds.** The next 3-6 months are mostly about scaling what works (more accounts, weekly cadence, more PMs) and avoiding the temptation to rewrite what's working.

The dashboard is ready for tomorrow's showing. After the showing, the priority list above unblocks the next 30 days. Beyond that: revisit when something forces a decision.

**The bias holds: make it right, scale it slowly, become more expert each cycle.**
