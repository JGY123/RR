# RR — Master TODO List

**Owner:** Yuda (product owner)
**Updated:** 2026-05-05
**Open in:** VS Code (`code TODO.md`) — checkboxes are clickable in the Markdown preview.

> **How this is organized.** Buckets by time horizon, not priority. Most things wait until launch. The `NOW` list is the only one that wants attention this week. Each item links to the source doc that has the detail — this file is the index, not the spec.

---

## 🔥 NOW (this week, pre-launch — small, useful, do them while waiting)

These are the things you can make progress on before Alger eng comes back with VM specs / a deployment slot. None block launch; all reduce launch-week stress.

- [ ] **Send Alger eng the launch package** — `LAUNCH_PLAN.md` + `ALGER_DEPLOYMENT.md` + the cron template + your answers to the 8 open decisions in `LAUNCH_PLAN.md` §"Open decisions you need to make"
- [ ] **Decide the 8 launch open decisions** (so the email is complete) — hostname · notification channel · distribution list · cron cadence · backup retention · initial PM list · office hours cadence · incident response owner. Source: `LAUNCH_PLAN.md` §Open decisions
- [ ] **Tag a launch candidate** — `git tag launch-candidate-2026-05-05 && git push origin launch-candidate-2026-05-05` (Step A in `LAUNCH_PLAN.md`)
- [ ] **Write the PM-facing announcement email draft** — 2 sentences + URL placeholder + link to `PM_ONBOARDING.md` + office-hours offer. Don't send yet; just have it ready
- [ ] **Vote on chart upgrades** — open `CHART_UPGRADE_CANDIDATES.md`, check the boxes; I ship the YES items next session (no launch dependency)
- [ ] **Decide on CLAUDE.md `anchor: true`** line in your unstaged diff — keep or revert (leftover from orginize sync; not mine)

---

## 🚀 LAUNCH WEEK (when Alger eng has a VM ready — ~2-3 weeks calendar from now)

### Part 1 — PM Access (`LAUNCH_PLAN.md` §Part 1)

- [ ] **Step A — User pre-flight** (~1 hr, you) — bundle bootstrap tarball, email Alger eng with launch package
- [ ] **Step B — Alger eng provisioning** (~2-4 hr, them) — VM, Python, nginx, clone repo, restore bootstrap data, port 3099 open
- [ ] **Step C — Smoke from VM URL** (~30 min, you + Alger eng pair) — 11-point checklist in `LAUNCH_PLAN.md` §1.2 Step C
- [ ] **Step D — Final wiring** (~1 hr, Alger eng) — firewall, DNS, backup tier enrollment, health-check endpoint
- [ ] **Step E — PM communication + office hours** (~1 hr, you) — send the announcement, hold first office hours

### Part 2 — Weekly Automation (`LAUNCH_PLAN.md` §Part 2)

- [ ] **Step F — User adapts cron template** (~30 min, you) — fill in the 4 [TODO] markers in `tools/cron_weekly_ingest.py.template`
- [ ] **Step G — Alger eng installs cron** (~1 hr, them) — drop in `/srv/rr/tools/`, manual test, wire to firm scheduler
- [ ] **Step H — First-week dry run** (~30 min, you + Alger eng) — Monday morning the cron fires for real, verify notification + dashboard freshness
- [ ] **Step I — Cadence settles** (ongoing) — tweak notification wording, add weekly diff email, calendar reminder for monthly merge_history audit

---

## 📅 POST-LAUNCH (June+ — after PMs are using it daily)

### FactSet / Claude integration (`FACTSET_CLAUDE_INTEGRATION.md`)

- [ ] **Get a FactSet contact** for the integration — relationship-management ask, no code yet
- [ ] **8 questions for FactSet** (`FACTSET_CLAUDE_INTEGRATION.md` §7) — 30-min call agenda · deployment model · data API · auth · freshness · custom code · off-FDS · June scope · pricing
- [ ] **Decide track** based on answers — stay on Track A (Alger VM v1) · pivot to Track B (FactSet hosting v2) · hybrid · monitor longer
- [ ] **If Track B:** 1-2 week design sprint to evaluate migration effort

### F18 / methodology questions for FactSet (`F18_HONEST_ASSESSMENT.md`)

- [ ] **Ask FactSet for the per-holding %T methodology doc** — unsigned sums of 94→134% across 6 strategies don't fit clean signed-decomposition theory. Need their math doc to know whether this is rounding / methodology / data issue
- [ ] **After their answer:** decide if F18 footers stay, get refined, or get removed

### Domestic-model file (`CLAUDE.md` §Strategy Account Mapping)

- [ ] **Wait for the domestic-model CSV file** (SCG + Alger US accounts) to land
- [ ] **First load:** verifier auto-flags schema fingerprint; delete `.schema_fingerprint.json` to acknowledge
- [ ] **Verify:** factor list adapts (no Currency / Country / FX macros in domestic mode); PARTIAL not FAIL classification
- [ ] **Update strategy mapping table** in `CLAUDE.md` with new account IDs / names / benchmarks

### Backlog / chart upgrades

- [ ] **Ship YES-voted chart upgrades** from `CHART_UPGRADE_CANDIDATES.md` once you've voted
- [ ] **Resume tile-audit cadence** — Tier-1 tiles 3+ remaining (cardCountry next per session memory)
- [ ] **Drill modal migration** (B-spec) — `DRILL_MODAL_MIGRATION_SPEC.md` ~6-7 hours when ready (deferred pending PM signoff on 3 open questions)
- [ ] **Backlog ID items** — see `BACKLOG.md`. Most relevant: B117 corr pre-cache · B118 period-aware return · B119 mockup framework · B120 tile chrome sweep · B121 drill modal period sweep

---

## 🔁 ONGOING / CADENCE (no due date; recurring)

- [ ] **Quarterly tile-audit subagent run** — `tile-audit` subagent on a cycling tile each quarter
- [ ] **Per-tile review per `MARATHON_PROTOCOL.md`** — data-first ordering, structured output
- [ ] **`LESSONS_LEARNED.md` maintenance** — add new entries when crisis patterns surface
- [ ] **Monthly review of `merge_history[]`** in `data/strategies/index.json` — spot drift / unexpected overwrites
- [ ] **PM feedback intake** — capture in a "PM_FEEDBACK.md" file (doesn't exist yet — create on first feedback)

---

## 👀 WATCH (no action; just monitor — re-read trigger doc when these fire)

- [ ] **FactSet/Claude June 2026 rollout** — concrete details (`FACTSET_CLAUDE_INTEGRATION.md` §Decision triggers)
- [ ] **A 2nd firm asks about RR** — multi-firm value of FDS hosting becomes too good to pass up
- [ ] **CSV export becomes harder** (FactSet deprecates / pricing changes) — forces the API path
- [ ] **Alger IT proposes a different deployment** model than VM
- [ ] **Domestic-model file** lands (covered above; flagged here too as a data-model trigger)
- [ ] **VDI memory profile** comes back from Alger IT — if peak > 70% of VDI RAM, ship strategy-switch cleanup pre-rollout (`ALGER_DEPLOYMENT.md` §8)

---

## 📎 Reference — the docs that drive each bucket

| Bucket | Source doc(s) | Open with |
|---|---|---|
| NOW + LAUNCH WEEK | `LAUNCH_PLAN.md` · `ALGER_DEPLOYMENT.md` · `tools/cron_weekly_ingest.py.template` | `code LAUNCH_PLAN.md ALGER_DEPLOYMENT.md tools/cron_weekly_ingest.py.template` |
| FactSet/Claude v2 | `FACTSET_CLAUDE_INTEGRATION.md` | `code FACTSET_CLAUDE_INTEGRATION.md` |
| Big-picture plan | `ROADMAP.md` · `STRATEGIC_REVIEW.md` · `STRATEGIC_REVIEW_NEXT.md` | `code ROADMAP.md STRATEGIC_REVIEW.md STRATEGIC_REVIEW_NEXT.md` |
| Chart upgrades | `CHART_UPGRADE_CANDIDATES.md` | `code CHART_UPGRADE_CANDIDATES.md` |
| F18 | `F18_HONEST_ASSESSMENT.md` · `FACTSET_FEEDBACK.md` | `code F18_HONEST_ASSESSMENT.md FACTSET_FEEDBACK.md` |
| PM-facing | `PM_ONBOARDING.md` · `SHOWING_TOMORROW.md` | `code PM_ONBOARDING.md SHOWING_TOMORROW.md` |
| Engineering backlog | `BACKLOG.md` · `DRILL_MODAL_MIGRATION_SPEC.md` | `code BACKLOG.md DRILL_MODAL_MIGRATION_SPEC.md` |
| Project rules | `CLAUDE.md` · `LESSONS_LEARNED.md` · `MARATHON_PROTOCOL.md` | `code CLAUDE.md LESSONS_LEARNED.md MARATHON_PROTOCOL.md` |
| Master nav | `docs/INDEX.md` | `code docs/INDEX.md` |

---

## 🧭 How to use this file

1. **Daily / weekly check-in:** open `TODO.md`. Skim NOW. Check off what you did. Move anything that's drifted into the next bucket.
2. **Pre-launch (the next ~3 weeks):** the only bucket that matters is NOW + LAUNCH WEEK. Everything else is asleep until June.
3. **Add new items** by appending to the right bucket — don't delete items, check them off (audit trail).
4. **Update the `Updated:` date** at the top when you make a meaningful pass.
5. **Don't let this become a graveyard.** If a bucket grows past ~10 items, audit + prune. Quarterly review minimum.

---

## 🎯 The point of this file

Most product-owner TODO lists die because they conflate "things I might do" with "things I will do." This one is structured so:

- The **NOW** bucket is short and actionable — if it stays empty for >1 week, RR isn't progressing
- The **LAUNCH WEEK** bucket is the bridge to the goal — the only thing that matters until June
- The **POST-LAUNCH** bucket is the parking lot — items wait there without nagging you
- The **WATCH** bucket is your alert list — no action, just signal capture

When the launch lands and PMs are using RR, this file gets a new bucket: **PM-DRIVEN** (items surfaced from real usage). That's when RR stops being a build project and becomes a tool.

Until then: NOW + LAUNCH WEEK. The rest will keep.
