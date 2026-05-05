# RR Launch Plan — Two Parts, Sequenced

**Drafted:** 2026-05-05
**Audience:** the user (product owner) — sequenced action plan to get RR live at Alger
**Companion:** `ALGER_DEPLOYMENT.md` (the directive doc for Alger's tech team — comprehensive reference) · `FACTSET_CLAUDE_INTEGRATION.md` (the v2 watch — orthogonal)
**This doc:** the actionable, sequenced "do this then that" launch checklist.

---

## TL;DR

Launch = two parts. Done sequentially:

**Part 1 — PM Access:** PMs at Alger can open RR in their browser and see their portfolio data. Target: **2-4 hr of Alger eng time + 1-2 hr of yours.** This is the bigger lift because it involves Alger IT.

**Part 2 — Weekly Automation:** the dashboard auto-updates with each new FactSet CSV without anyone running a command manually. Target: **2-3 hr of Alger eng time + ~30 min of yours.** Done after Part 1 lands.

Both parts use only the architecture we've already designed (Linux VM, static HTML, Python ingest pipeline, B114 cumulative merge). Nothing new to build — just deploy.

---

# PART 1 — PM Access

## 1.1 What "PM Access" means concretely

A PM at Alger sits at their desk, opens Chrome (or Edge), types a URL like `https://rr.alger.internal:3099/dashboard_v7.html` (or whatever Alger names it), and the dashboard loads. They can:

- See their portfolio's TE / Active Share / Beta / Holdings count
- Click through 4 tabs (Overview / Exposures / Risk / Holdings)
- Drill into any tile
- Export CSVs / take screenshots
- Set notes + watchlist (per-user via localStorage)
- Switch strategies via the header picker
- View historical weeks via the `‹ date ›` arrows

They do NOT need to:
- Run any scripts
- Have FactSet credentials
- Have admin access to anything
- Touch the terminal

That's the bar. Now the steps to get there.

## 1.2 Sequence — what happens in what order

```
Step A → Step B → Step C → Step D → Step E
(you)    (Alger    (you +    (Alger    (you)
         IT)       Alger)    IT)
```

### Step A — User pre-flight (you, ~1 hr)

Before Alger eng can do anything, you need to give them an artifact + answers.

- [x] Confirm latest local state is push-clean: `git status` shows nothing pending, `git rev-list --count origin/main..HEAD` returns 0 ✓
- [x] Confirm smoke + tests pass: `./smoke_test.sh --quick` returns 🟢, `pytest test_parser.py` 26/26 ✓
- [ ] **Tag a launch candidate:** `git tag launch-candidate-2026-05-05 && git push origin launch-candidate-2026-05-05`. This is the version Alger eng will deploy.
- [ ] **Bundle the bootstrap data** for first-time deploy:
  ```bash
  cd ~/RR
  tar czf rr-bootstrap-2026-05-05.tar.gz \
      data/strategies/index.json \
      data/strategies/*.json \
      latest_data.json \
      em_full_history.json
  ls -lh rr-bootstrap-2026-05-05.tar.gz
  ```
  Result: ~1.6 GB tarball. This is the "first-time data" Alger uploads to the VM.
- [ ] **Email Alger eng with:** the launch-candidate tag · the bootstrap tarball link (Box / SharePoint / SFTP / whatever your firm uses to send 1.6 GB) · `ALGER_DEPLOYMENT.md` · the answers below to their open questions

**Answers to Alger IT's likely first questions:**

| Question | Answer |
|---|---|
| What VM specs? | 4 vCPU, 32 GB RAM (parser peaks ~23 GB), 100 GB SSD, internal network, port 3099 open to PMs. RHEL 9 / Ubuntu 22.04 LTS preferred. |
| Python version? | 3.9+ (3.11 recommended). Only stdlib — no pip dependencies. |
| Web server? | nginx with `gzip_static on` + `Cache-Control: no-cache` for `*.html` and `*.json`. Or Python's stdlib `http.server` for v1 if nginx is overkill. |
| Where do users access? | Internal URL — they pick the hostname. Suggestion: `rr.alger.internal` or `redwood-risk.alger.internal`. Internal-only (no public IP, no VPN required for users on Alger network). |
| Browser support? | Chrome / Edge both work (Chromium-based). Safari / Firefox should work but aren't actively tested. |
| Auth? | None at the application layer in v1 — gated by being on Alger's internal network. SSO is a v2 conversation. |
| Compliance / audit log? | Standard nginx access log writes who-accessed-what-when. No app-level audit log in v1. |
| Backup? | Two folders enrolled in Alger's standard backup tier: `/srv/rr/data/strategies/` + `/srv/rr/archive/` (created by the ingest in Part 2). See `ALGER_DEPLOYMENT.md` §5. |

### Step B — Alger eng provisioning (~2-4 hr, them)

Alger eng follows `ALGER_DEPLOYMENT.md` §10 day-zero checklist:

1. Provision VM (specs above)
2. Install Python 3.9+, nginx, git
3. Set up service account `rr-svc` with sudo for `/srv/rr` only
4. Clone RR repo: `git clone https://github.com/JGY123/RR.git /srv/rr` — public repo, no auth needed
5. Restore bootstrap data: extract the `rr-bootstrap-2026-05-05.tar.gz` you sent into `/srv/rr/data/strategies/` and `/srv/rr/`
6. Configure nginx — root `/srv/rr/`, port 3099 internal, `Cache-Control: no-cache, no-store, must-revalidate` for `*.html` + `*.json`
7. Create folders: `/srv/rr/inbox/` + `/srv/rr/processed/` + `/srv/rr/archive/csv/` + `/srv/rr/archive/json/` + `/srv/rr/logs/`
8. Confirm via `curl http://localhost:3099/dashboard_v7.html` that the page serves
9. **Tell you the URL** — that's your handoff signal

### Step C — User smoke from the VM URL (you + Alger eng pair, ~30 min)

You + an Alger engineer screen-share. Open the URL on a representative PM's laptop (NOT yours — yours is too well-tuned).

Things to check:

- [ ] Page loads in <3 seconds
- [ ] Strategy picker (top of header) lists all 6 strategies (ACWI · IDM · IOP · EM · GSC · ISC)
- [ ] Click each tab: Overview / Exposures / Risk / Holdings — all render without errors
- [ ] Open DevTools console (Cmd+Option+J): look for `✓ B115 integrity check passed`. NO red errors.
- [ ] Risk tab → cardTEStacked: the chart renders with the three-tier provenance footer (mostly indigo MCR-derived ᵉ today)
- [ ] Holdings tab → cardHoldings: table renders, sortable, click a row to drill
- [ ] ⚙ → Theme → Alger: theme toggles cleanly
- [ ] Footer at the bottom shows: Parser 3.1.1 · Format 4.3 · Data through 2026-04-30
- [ ] Strategy switch via header picker: switching loads new data within ~2s
- [ ] Week selector: ‹ date › changes work, amber banner appears for historical weeks
- [ ] No JS errors after 2 minutes of clicking around

If anything fails: roll back to `presentation-2026-05-04-shipped` tag, debug, retry. Don't proceed until clean.

### Step D — Alger eng final wiring (~1 hr, them)

After your sign-off:

1. **Firewall rule:** allow port 3099 from PM workstation subnet to the RR VM. Block from elsewhere.
2. **DNS:** `rr.alger.internal` (or chosen hostname) → VM internal IP
3. **Backup tier enrollment:** `/srv/rr/data/strategies/` and `/srv/rr/archive/` added to standard backup
4. **Health-check endpoint:** see `ALGER_DEPLOYMENT.md` §7 — a 5-line `health.py` that pings up if data is fresh
5. **Hand off URL** to the user: e.g., `https://rr.alger.internal:3099/dashboard_v7.html`

### Step E — User communication to PMs (you, ~1 hr)

This is the "launch announcement" piece. Suggested:

1. **Email to PMs** with:
   - 2-sentence pitch ("Redwood Risk is now live on the firm network — single-pane portfolio risk for our 6 strategies, with discipline you can verify cell-by-cell.")
   - The URL (bookmark it)
   - Link to `PM_ONBOARDING.md` (or a hosted copy) — the cheat sheet you wrote
   - Office-hours offer ("I'm available Wednesday 1-2pm to walk through it with anyone who wants")
2. **Optionally:** a 5-min video walkthrough using the Gamma deck templates in `GAMMA_PROMPT.md`
3. **Office hours:** show up, answer questions live, take notes on what surprised people

Day 1: 5-10 PMs poke around. Day 2-7: questions surface. Week 2: cadence settles. **Resist the urge to ship features in the first 2 weeks** — let usage drive the next priority list.

## 1.3 Done = these are all true

- [ ] PMs can open the dashboard from their workstations
- [ ] Strategy + week + universe pill all work
- [ ] No console errors visible in normal use
- [ ] PM_ONBOARDING.md is accessible (linked from dashboard footer or sent in announcement)
- [ ] At least 3 PMs have used it for a real morning workflow
- [ ] First "I noticed something" feedback has been captured

When all 6 are checked, **Part 1 is launched.**

---

# PART 2 — Weekly Automation

## 2.1 What "Weekly Automation" means concretely

Every Monday morning (or whatever cadence FactSet pushes data), a fresh CSV lands somewhere on Alger's storage. The pipeline picks it up, parses it, merges into the cumulative state, archives the CSV + parser output, and the dashboard reflects the new data on next refresh. PMs don't run anything; the user gets a "here's what changed" email.

## 2.2 What's already built (the heavy lifting)

✅ **factset_parser.py** — 13K-LOC parser, header-driven, 89-test suite, FORMAT 4.3
✅ **load_data.sh** — parse + verify + open in browser
✅ **load_multi_account.sh --merge** — multi-account ingest + B114 cumulative merge
✅ **merge_cumulative.py** — the merge primitives + CLI (13 unit tests passing)
✅ **verify_factset.py** — 22+ pass/fail checks against the parsed JSON
✅ **verify_section_aggregates.py** — Layer 2 cross-week invariant monitor
✅ **smoke_test.sh** — pre-flight gate, 21/21 ALL PASS

What's missing for "Weekly Automation": **scheduling + notifications.** That's it. ~30 min of script + ~1 hr of Alger eng time wiring it to their cron + email/Slack.

## 2.3 The cron skeleton (template)

The script Alger eng adapts. **It already exists** in `ALGER_DEPLOYMENT.md` §4. Reproduced here as a standalone file (next commit will add it to the repo as `tools/cron_weekly_ingest.py`).

What it does, in plain English:

1. Watches `/srv/rr/inbox/` for new `*.csv` files
2. For each new CSV:
   a. Tag a `pre-ingest.YYYY-MM-DD` git tag (rollback safety)
   b. Run `./load_data.sh <csv>` (parse + verify)
   c. Run `merge_cumulative.py --new --dry-run` (sanity check)
   d. If dry-run clean: run real merge
   e. If anything fails: roll back via git, send alert
   f. Archive the CSV (gzip → `/srv/rr/archive/csv/YYYY-MM-DD_*.csv.gz`)
   g. Archive the parser output (gzip → `/srv/rr/archive/json/YYYY-MM-DD_latest_data.json.gz`)
   h. Run `verify_section_aggregates.py --latest` (L2 monitor)
   i. Move processed CSV out of inbox
   j. Send "ingest complete" notification with diff summary
3. Tag a `post-ingest.YYYY-MM-DD`

## 2.4 Sequence — Part 2 steps

### Step F — User adapts cron template (you, ~30 min)

After Part 1 is live:

- [ ] Pull `tools/cron_weekly_ingest.py.template` from the repo (next commit will add it)
- [ ] Customize:
  - Notification function (email vs Slack webhook vs Teams)
  - Distribution list for alerts (you + 1-2 Alger eng + analyst)
  - Inbox path (`/srv/rr/inbox/` typically)
- [ ] Send adapted version to Alger eng

### Step G — Alger eng installs cron (~1 hr, them)

1. Drop adapted script into `/srv/rr/tools/cron_weekly_ingest.py`
2. Test manually: drop a known-good CSV in `/srv/rr/inbox/` and run the script. Verify it parses + merges + archives + sends notification.
3. Wire to cron:
   ```cron
   0 6 * * MON /usr/bin/python3 /srv/rr/tools/cron_weekly_ingest.py >> /var/log/rr_cron.log 2>&1
   ```
   (Or whatever cadence Alger / FactSet's CSV-push schedule uses.)
4. Set up log rotation on `/var/log/rr_cron.log`

### Step H — First-week dry run (you + Alger eng, ~30 min)

Don't trust it until it's run for real once. The first weekly cycle:

- [ ] On Monday morning, FactSet CSV lands in `/srv/rr/inbox/`
- [ ] Cron job fires at 6am (or whenever)
- [ ] Notification arrives ("ingest complete" or alert)
- [ ] You confirm via dashboard refresh: footer shows "Data through {new date}" + "Last ingest YYYY-MM-DD" updates
- [ ] Spot-check: pick 1 KPI, eyeball "did this move sensibly week-over-week?"
- [ ] If alert fired or anything looks off: investigate, fix, run again next week

### Step I — Cadence settles (ongoing)

After 2-3 successful weekly cycles, the system is on autopilot. Adjustments:

- Tweak notification wording ("ingest complete with N new weeks added · M overwritten · diff: TE +X / AS −Y / etc.")
- Add weekly diff summary email (auto-generated from `merge_history[]`)
- Add post-merge L3 trend monitor email if drift detected
- Set up calendar reminder: monthly review of `merge_history[]` audit trail to spot issues

## 2.5 Done = these are all true

- [ ] Cron script installed + tested with a real CSV
- [ ] First weekly cycle ran successfully without manual intervention
- [ ] Notification arrived and was readable
- [ ] Dashboard reflects new data (footer freshness updates)
- [ ] Backup tier ingested the new archive files (verify with Alger eng)
- [ ] Failure mode tested at least once (manual: drop a malformed CSV, confirm rollback + alert)

When all 6 are checked, **Part 2 is launched** and the system is on autopilot.

---

# RUNBOOK — when things go wrong

## Cron alert fired ("INGEST FAILED")

1. SSH to VM: `ssh rr-svc@rr.alger.internal`
2. Read the log: `tail -100 /var/log/rr_cron.log`
3. Most likely causes:
   - CSV format change (FactSet shipped a new schema) → re-run parser, expect schema-fingerprint flag, acknowledge with `rm ~/RR/.schema_fingerprint.json`, re-run
   - File system full → check `/srv/rr/`; archive folders should be auto-managed but verify
   - Parse error → manually run `./load_data.sh /srv/rr/inbox/<file>.csv` and read the verifier output
4. Once fixed: manually run `python3 /srv/rr/tools/cron_weekly_ingest.py` to retry
5. If recurring: investigate root cause, log lesson in `LESSONS_LEARNED.md`

## Rollback ("the merge made things worse")

```bash
cd /srv/rr
git tag -l 'pre-ingest.*' | tail -5      # find recent rollback points
git reset --hard pre-ingest.2026-05-12   # roll back to chosen point
# Restore data/strategies/ from backup tier (Alger IT)
```

The cron script writes pre-ingest tags before each merge for exactly this case.

## Dashboard shows stale data

1. Browser cache: hard-refresh (Cmd+Shift+R) — fixes 90% of cases
2. nginx cache: `sudo systemctl reload nginx` on the VM
3. Underlying file: check `data/strategies/index.json`'s `current_date` field — should match the latest week
4. If stale: ingest didn't run / failed silently. Check `/var/log/rr_cron.log` and last 5 cron runs

---

# Estimated total launch time

| Part | Sub-step | Owner | Time |
|---|---|---|---|
| 1 | A — pre-flight | You | 1 hr |
| 1 | B — VM provision + bootstrap | Alger eng | 2-4 hr |
| 1 | C — smoke from VM | You + Alger eng | 30 min |
| 1 | D — final wiring (firewall, DNS, backup) | Alger eng | 1 hr |
| 1 | E — PM communication | You | 1 hr |
| 2 | F — cron template adapt | You | 30 min |
| 2 | G — cron install + test | Alger eng | 1 hr |
| 2 | H — first-week dry run | You + Alger eng | 30 min |
| **Total** | | | **~7-9 hr split between you + Alger eng** |

Realistic calendar: **2-3 weeks** assuming Alger eng has bandwidth + you have 1-2 days/week to push it forward.

---

# Open decisions you need to make

These should be answered before Step A:

1. **Hostname for the VM** — `rr.alger.internal` is illustrative; Alger picks
2. **Notification channel** — email / Slack / Teams / ServiceNow
3. **Distribution list for alerts** — who gets paged when ingest fails
4. **Cron cadence** — Monday 6am Alger time? Or different?
5. **Data backup retention** — 90 days / 1 year / indefinitely? (CSVs are small gzipped; "indefinitely" is fine.)
6. **Initial PM list** — who gets the launch announcement first? Some firms prefer phased rollout (1-2 PMs Week 1, expand over time).
7. **Office hours cadence** — once / weekly / on-demand?
8. **Incident response** — when an ingest fails on a Monday morning, who triages? You alone, or you + an Alger engineer?

Most of these are 30-second decisions you make in the next email to Alger eng.

---

# What this plan doesn't cover (defer to v2)

- **Multi-firm rollout** — only Alger today; multi-firm is a v2 conversation tied to FactSet/Claude integration possibilities
- **Auth/SSO** — internal-network gate is sufficient v1
- **Real-time data** — weekly cadence is the FactSet ship rhythm anyway
- **Mobile** — works on phones but not optimized; v2 if PMs want it
- **Custom theming per-firm** — Alger theme exists; per-firm theming is v3 if multi-firm happens

---

# Closing

Both parts are well-scoped, low-risk, and use only the architecture we've already shipped. The bottleneck is calendar coordination with Alger eng — none of this is technically hard.

When Part 1 lands: **PMs use RR.** When Part 2 lands: **PMs trust RR is fresh without thinking about it.**

Then the next chapter starts: PM feedback drives the priority list. The audit cadence keeps shipping. The dashboard becomes a quiet daily tool.
