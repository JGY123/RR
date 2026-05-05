# RR — Alger Deployment Architecture

**Drafted:** 2026-05-05
**Audience:** Alger's tech / engineering team (the people who will build the automated ingest + host the dashboard) plus the user as the product owner / point of contact.
**Scope:** how RR runs at Alger — hosting, ingest pipeline, backups, access control, monitoring. The directive doc the user hands to Alger IT.

> **Note:** the user is the product owner and the only "caretaker" of the dashboard from a content / configuration perspective. Alger engineers own the infrastructure (VM, network, scheduler) but should not modify dashboard code or data unless coordinated with the user.

---

## 1. TL;DR — what Alger needs to build

A small set of well-scoped infrastructure pieces:

1. **A virtual machine** (Linux preferred; Windows acceptable) inside Alger's environment, accessible to PMs via standard internal Chrome/Edge browsers.
2. **Storage volume** with at least **50 GB free** for RR's canonical state (today's data is 1.6 GB; with 25 strategies + 3 years of weekly history it grows to ~5 GB; a 50 GB allocation gives 10× runway).
3. **Network access** — the VM needs to be reachable on a port (default 3099) from the internal PM workstations / VDI sessions.
4. **A scheduled job** that picks up the weekly FactSet CSV, runs the ingest pipeline (one command), and stores the inputs + outputs in a backup folder. **Daily or weekly cadence depending on FactSet's update rhythm.**
5. **A backup of two folders** to Alger's standard backup tier:
   - `/srv/rr/data/strategies/` — the canonical per-strategy JSON state (everything the dashboard reads from)
   - `/srv/rr/archive/csv/` — every CSV that's ever been ingested, indexed by date
6. **Firewall / access control** to limit dashboard access to PMs + the user + designated Alger engineers.

The dashboard itself (the HTML file) is static; deployment is "serve a folder over HTTP." No application server, no database, no Node. The interesting infra is the **ingest pipeline + backup**, not the rendering.

---

## 2. Why this architecture (not alternatives)

The user has confirmed: **stay HTML, no rewrite to a desktop app or single-page React app** (see `ROADMAP.md` §2 for the full reasoning). Net effect on hosting:

- **No Node / npm** — there's no build step. The dashboard is one `dashboard_v7.html` file plus a `data/strategies/` folder.
- **No application server** — Python's stdlib `http.server` is sufficient (or any static-file webserver: nginx, Apache, IIS).
- **No database** — per-strategy JSON files are the data layer. Easy to backup, easy to restore, easy to inspect.
- **No auth at the application layer** — access control is handled by the network (firewall/VPN/internal-only). For multi-firm or external use we'd revisit; for Alger-internal it's standard.

**Trade-off accepted:** PMs will always be on Alger's internal network (or VPN'd in). No public-internet access. This is fine for a PM dashboard.

---

## 3. Hosting topology

```
                   ┌──────────────────────────────────────────┐
                   │ Alger Virtual Server (Linux preferred)   │
                   │   (e.g., RHEL 9 / Ubuntu 22.04 LTS)      │
                   │                                          │
                   │  /srv/rr/                                │
                   │    dashboard_v7.html  ← static page      │
                   │    data/                                 │
                   │      strategies/                         │
                   │        index.json     ← slim summaries   │
                   │        ACWI.json.gz   ← per-strategy     │
                   │        IDM.json.gz    ← (gzipped, ~80MB) │
                   │        ...            ← 6-25 strategies  │
                   │    archive/                              │
                   │      csv/             ← every ingested CSV│
                   │        2026-04-30_factset_export.csv.gz │
                   │        2026-05-07_factset_export.csv.gz │
                   │        ...                               │
                   │      json/            ← parser outputs   │
                   │        2026-04-30_latest_data.json.gz   │
                   │        ...                               │
                   │                                          │
                   │  Service: nginx or python http.server    │
                   │           on port 3099 (internal only)   │
                   │                                          │
                   │  Cron: weekly ingest job (Python)        │
                   │                                          │
                   └──────────────────────────────────────────┘
                                       │
                                       │ HTTP (port 3099)
                                       ▼
                              ┌────────────────────┐
                              │ PM workstations /  │
                              │ VDI Chrome/Edge    │
                              │ (internal network) │
                              └────────────────────┘
```

The PM's browser fetches `dashboard_v7.html` once + the active strategy's `<ID>.json.gz` (browser handles `Content-Encoding: gzip` natively). That's the only network traffic during normal use.

**VM sizing recommendation:**
- **CPU:** 4 vCPUs (parser is single-threaded today; 4 gives headroom for parser + nginx + cron)
- **RAM:** 32 GB (parser peaks at ~23 GB on a 1.83 GB CSV today; future 5 GB CSVs may peak at 30-50 GB)
- **Disk:** 100 GB on a fast SSD (today: 1.6 GB; future: 5-10 GB; archive grows ~80 MB per week per strategy = ~10 GB/year of CSVs)
- **Network:** internal-only; standard 1 Gbps suffices

The "32 GB RAM" is the only spec that matters — driven by the parser's peak memory during ingest. Could be reduced to 16 GB if Alger profiles + optimizes the parser, but 32 GB is the safe path.

---

## 4. The ingest pipeline contract

This is the spec for what Alger's tech team automates. Today everything below is wired in scripts already in the repo; their job is to put it on a schedule + add notifications.

### Inputs

- **A FactSet CSV export.** Filename convention recommended: `factset_export_YYYY-MM-DD.csv` (where date is the report date, not the export date). Lands in a watched folder, e.g., `/srv/rr/inbox/`.
- **Optionally a domestic-model CSV** (separate file with SCG + Alger US accounts; same column structure). Same naming convention, recognizable by content.

### Pipeline (five steps; two commands total)

```bash
# Step 1: parse + verify (existing)
cd /srv/rr
./load_data.sh /srv/rr/inbox/factset_export_YYYY-MM-DD.csv
# This writes: latest_data.json (~2 GB) + last_verify_report.log

# Step 2: cumulative-merge into per-strategy state (existing, B114)
python3 merge_cumulative.py --new latest_data.json \
    --source-csv /srv/rr/inbox/factset_export_YYYY-MM-DD.csv
# This: merges new into data/strategies/<ID>.json.gz · stamps merge_history[] ·
#        rebuilds index.json · writes atomically (no partial-write risk)
```

After both steps, the dashboard auto-loads new state on next browser refresh.

### What Alger's automation script needs to do (~30 lines of Python or shell)

```python
# Pseudocode for the cron job
import subprocess, glob, os, datetime, shutil, gzip

INBOX = "/srv/rr/inbox"
ARCHIVE_CSV = "/srv/rr/archive/csv"
ARCHIVE_JSON = "/srv/rr/archive/json"
RR_HOME = "/srv/rr"

# 1. Find new CSV(s)
new_csvs = sorted(glob.glob(f"{INBOX}/*.csv"))
if not new_csvs:
    log("No new CSV in inbox; nothing to do.")
    exit(0)

# 2. Tag pre-ingest baseline (for rollback)
subprocess.run(["git", "-C", RR_HOME, "tag",
    f"pre-ingest.{datetime.date.today().isoformat()}"], check=True)

# 3. Run the existing pipeline
for csv in new_csvs:
    # Parse + verify
    result = subprocess.run([f"{RR_HOME}/load_data.sh", csv],
                           cwd=RR_HOME, capture_output=True, text=True)
    if result.returncode != 0:
        notify_alert(f"PARSE FAILED on {csv}", result.stderr)
        continue

    # Dry-run merge first (safety)
    dry = subprocess.run(["python3", f"{RR_HOME}/merge_cumulative.py",
                          "--new", f"{RR_HOME}/latest_data.json",
                          "--source-csv", csv, "--dry-run"],
                         cwd=RR_HOME, capture_output=True, text=True)
    if "ERROR" in dry.stdout or dry.returncode != 0:
        notify_alert(f"MERGE DRY-RUN FAILED", dry.stdout + dry.stderr)
        continue

    # Real merge
    real = subprocess.run(["python3", f"{RR_HOME}/merge_cumulative.py",
                           "--new", f"{RR_HOME}/latest_data.json",
                           "--source-csv", csv],
                          cwd=RR_HOME, capture_output=True, text=True)
    if real.returncode != 0:
        notify_alert(f"MERGE FAILED", real.stderr)
        # Roll back
        subprocess.run(["git", "-C", RR_HOME, "reset", "--hard",
                       f"pre-ingest.{datetime.date.today().isoformat()}"], check=True)
        continue

    # 4. Archive the CSV + the parsed JSON (canonical backup)
    csv_basename = os.path.basename(csv)
    archive_csv_path = f"{ARCHIVE_CSV}/{csv_basename}.gz"
    with open(csv, 'rb') as f_in, gzip.open(archive_csv_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    json_archive_name = csv_basename.replace(".csv", "_latest_data.json.gz")
    archive_json_path = f"{ARCHIVE_JSON}/{json_archive_name}"
    with open(f"{RR_HOME}/latest_data.json", 'rb') as f_in, gzip.open(archive_json_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    # 5. Move CSV from inbox to archive (or delete)
    os.rename(csv, f"/srv/rr/processed/{csv_basename}")

    # 6. Run the L2 monitor for confirmation
    monitor = subprocess.run(["python3", f"{RR_HOME}/verify_section_aggregates.py",
                             "--latest"], cwd=RR_HOME, capture_output=True, text=True)
    if "RED" in monitor.stdout:
        notify_alert(f"L2 MONITOR FLAGGED on {csv_basename}", monitor.stdout)

    # 7. Notify success
    notify_success(f"Ingest complete: {csv_basename}",
                   f"Pipeline succeeded; dashboard reflects new data on next refresh.")

# 8. Tag the post-ingest state
subprocess.run(["git", "-C", RR_HOME, "tag",
    f"post-ingest.{datetime.date.today().isoformat()}"], check=True)
```

This is a starting point; Alger's engineers should adapt to their notification/secrets/scheduler conventions.

### Notification channel

Alger picks (any of): email, Slack webhook, MS Teams, ServiceNow ticket. The script just needs `notify_success()` and `notify_alert()` — both take title + body and route appropriately.

For early days: an email to a small distribution list (the user, the user's analyst, 1-2 Alger engineers) is sufficient.

### Schedule

Recommended: **weekly on Mondays at 6 AM Alger time** (or whenever FactSet's overnight job has reliably finished). Cron entry:

```
0 6 * * MON /usr/bin/python3 /srv/rr/cron_weekly_ingest.py >> /var/log/rr_cron.log 2>&1
```

Alger may prefer a "watch the inbox folder" pattern instead of a strict schedule — that's fine; either works.

---

## 5. Backup strategy

**The principle:** because re-extracting from FactSet is resource-intensive (and potentially gated), Alger's RR deployment is the **canonical archive**. Lose this, and we may not be able to rebuild without significant FactSet engagement.

### What gets backed up (in priority order)

| Path | What it is | Why critical | Backup frequency |
|---|---|---|---|
| `/srv/rr/data/strategies/` | Per-strategy cumulative state (the dashboard's source of truth) | Loss = full rebuild from CSVs (next priority) | **Daily incremental** to Alger's standard backup tier; **weekly full snapshot** retained 90 days |
| `/srv/rr/archive/csv/` | Every CSV that's ever been ingested (gzipped) | Loss = cannot rebuild data/strategies/; would need FactSet re-extract | **Daily incremental**; **monthly full snapshot** retained ≥ 1 year (or "indefinitely" — they're tiny gzipped) |
| `/srv/rr/archive/json/` | Parser outputs (gzipped `latest_data.json` per ingest) | Loss = recoverable from CSV but recomputes the parser run; saves ~15 min/strategy on disaster recovery | **Daily incremental** retained 90 days |
| Git repo (`/srv/rr/.git`) | Code + small docs (no large data; data is gitignored) | Loss = re-clone from JGY123/RR (already on GitHub) | **Hourly** if Alger has continuous backup; otherwise daily |
| `/srv/rr/dashboard_v7.html` | The dashboard itself | Loss = git clone restores | Inherits from git repo backup |

### Folder structure (proposed)

```
/srv/rr/
├── dashboard_v7.html              ← shipped from git
├── factset_parser.py              ← shipped from git
├── ... other code files ...
├── inbox/                         ← incoming CSVs (Alger's automation drops here)
├── processed/                     ← CSVs that have been ingested (1-day grace then move to archive)
├── archive/
│   ├── csv/
│   │   ├── 2026-04-30_factset_export.csv.gz
│   │   ├── 2026-05-07_factset_export.csv.gz
│   │   └── INDEX.md               ← what each CSV covered (auto-generated)
│   └── json/
│       └── 2026-04-30_latest_data.json.gz
├── data/
│   └── strategies/                ← canonical state (gzipped per-strategy)
│       ├── ACWI.json.gz
│       ├── IDM.json.gz
│       ├── ... 25+ strategies ...
│       └── index.json             ← slim summary, NOT gzipped (loaded first)
├── logs/
│   ├── rr_cron.log                ← ingest run log
│   ├── rr_http.log                ← server log
│   └── verify_*.log               ← integrity monitor outputs
└── .schema_fingerprint/           ← per-source-file (RR-side change pending)
```

### Restore procedure (disaster recovery runbook)

If `/srv/rr/data/strategies/` is corrupted or wiped:

```bash
# 1. Restore from latest good backup
sudo rsync -av /backup/rr/data/strategies/ /srv/rr/data/strategies/

# 2. Verify
cd /srv/rr
python3 verify_section_aggregates.py --latest
./smoke_test.sh --quick

# 3. If verifier flags issues, rebuild from CSV archive instead
mkdir -p /tmp/rr_rebuild
for csv in $(ls -t /srv/rr/archive/csv/*.csv.gz); do
    gunzip -c "$csv" > /tmp/rr_rebuild/$(basename "$csv" .gz)
    python3 merge_cumulative.py \
        --new <parsed-output-from-this-csv> \
        --source-csv "$csv"
done
```

Rebuild from CSV archive: ~5-15 min per CSV × number of CSVs. For 1 year of weekly ingests = ~52 CSVs × 10 min avg = ~9 hours. Long but tractable.

### Off-site backup

Alger's standard backup tier should already include off-site replication (DR site, cloud). The user does NOT need to add extra off-site backup beyond what Alger provides for any /srv volume.

---

## 6. Access control + roles

| Role | Who | What they can do |
|---|---|---|
| **Caretaker / product owner** | The user | Full SSH + git push to /srv/rr/.git; can ship dashboard updates; coordinates with FactSet on inquiries |
| **Alger engineer (DevOps)** | 1-2 people | Full SSH; manages VM, cron, networking, backups; can roll back if ingest fails; does NOT ship code changes without coordination |
| **PM (read user)** | All firm PMs | HTTP-only access to dashboard; can write to localStorage (their own browser, isolated); cannot SSH or modify state |
| **Read-only auditor** | Risk team / compliance | HTTP-only access to dashboard; same surface as PM but no write to localStorage (informally; technically same browser model) |
| **External (FactSet, vendor)** | None today | No access. F-letters and CSV slices shared via secure email/SFTP, not via dashboard access. |

**Network gate:** the VM should be inside Alger's internal subnet (or behind VPN). No public IPv4. Authentication is by network presence, which is the standard PM-tool pattern at financial firms.

If/when external access becomes a requirement (joint venture, multi-firm), revisit and add SSO. Today: don't.

---

## 7. Monitoring + alerting

### What to monitor

| Signal | Where it surfaces today | What Alger's monitoring should alert on |
|---|---|---|
| Ingest pipeline failure | `notify_alert()` from cron script | Email/Slack on every failure |
| L2 monitor (verify_section_aggregates) RED | stdout of cron + `verify_*.log` | Email/Slack within 1 hour |
| HTTP server down | (nothing today) | standard server-up check (Pingdom / Datadog / whatever Alger uses) |
| Disk space < 20% | (nothing today) | standard disk-watch alert |
| RAM > 85% during ingest | (nothing today) | metric to inform future profiling |
| Parser version drift (CSV format change → schema fingerprint) | `verify_factset.py` output | warning email, NOT a hard fail |

### What NOT to monitor

- The dashboard's per-PM behavior (clicks, scroll, etc.) — privacy + complexity for no value
- localStorage state — per-user, not server-side
- Per-tile render success — the integrity assertion in browser handles this; if it fires console errors the PM will report it

### Health-check endpoint (recommended add)

A 5-line Python script `/srv/rr/health.py` that returns 200 OK if:
- `data/strategies/index.json` is < 7 days old
- All 6+ strategies in index.json have `current_date` within last 14 days
- No `*.error` files in `/srv/rr/inbox/`

Alger's standard health-check polls this URL.

---

## 8. Memory capacity — investigation for Alger IT

The user asked: "PMs' browsers running on Alger's virtual server — local memory capacity could be an issue. Need to find out what it is."

**Questions for Alger IT:**

1. **What's the per-user RAM allocation on the PM VDI sessions?** (Common: 4 GB or 8 GB. Tight: 2 GB. Generous: 16 GB.) Most pessimistic case to plan for: 4 GB.
2. **What browser do PMs use?** Chrome / Edge / Firefox? The dashboard is tested on Chrome; should work on Edge (Chromium-based). Safari and Firefox should also work but aren't actively tested.
3. **Is the VDI session "persistent" or "non-persistent"?** Persistent = localStorage survives logoff (PM's notes/watchlists persist). Non-persistent = wipes on logoff (state would need to be exported by the PM at end of day).
4. **What's the local disk allocation per user?** (For browser cache + downloaded CSVs.) 1 GB minimum recommended.

**Dashboard memory footprint (measured today, 2026-05-04):**
- **Idle (just opened, no strategy selected):** ~80 MB
- **One strategy loaded (e.g., GSC, ~19 MB JSON):** ~250 MB
- **Largest strategy (ISC, 526 MB JSON):** ~1.4 GB peak during initial parse, settles to ~900 MB resident
- **All Plotly charts rendered:** adds ~300 MB
- **Switching strategies:** the OLD strategy is not garbage-collected today (held in `cs` global); switching can briefly peak at 2× one strategy's footprint

**Worst case (PM on 4 GB VDI viewing ISC):** ~2.2 GB browser process. Tight but workable; other processes (OS + VDI client + Office) have ~1.5 GB headroom.

**Worst case (after gzip ROADMAP T2.1):** browser fetches ~70 MB compressed, decompresses to ~526 MB in memory — same in-memory footprint, but FAR less network and disk. Network speedup more than memory.

### Mitigations if memory becomes a problem

1. **Implement strategy-switch cleanup** (~1 hour engineering): when user switches strategies, explicitly null out `cs` and call `Plotly.purge` on every chart div before loading the new strategy. ~50% memory reclaim.
2. **Lazy-load detail layer** (~3 hours): only load `hist.fac`, `hist.sec`, `hold[]` when the relevant tab is active. Initial load drops to ~150 MB.
3. **Switch to DuckDB-WASM** (~1-2 weeks): much smaller in-memory footprint, queryable. Premature today.

### Test plan for Alger IT

Before firm-wide rollout, ask Alger to:

1. Spin up a representative PM VDI session
2. Open the dashboard
3. Cycle through all 6 strategies, click through every tab
4. Open Chrome DevTools → Performance tab → record memory
5. Report: peak browser RAM + steady-state RAM + any slowdowns

If peak > 70% of VDI RAM, ship strategy-switch cleanup before rollout.

---

## 9. Pipeline + dashboard interaction summary (for the user)

For the user — what changes vs. current local laptop workflow:

| Today | At Alger |
|---|---|
| User runs `./load_multi_account.sh ~/Downloads/file.csv` manually | Cron picks up file from `/srv/rr/inbox/`; user gets email "ingest complete" |
| User opens `dashboard_v7.html` in Chrome on the laptop | PM opens `https://rr.alger.internal:3099/dashboard_v7.html` in Chrome on their VDI |
| Backup is "git push origin main" | Backup is Alger's standard `/srv/` backup tier; user keeps git push for code; data is on Alger's backup |
| Memory ceiling = laptop's 16 GB | Memory ceiling = whatever Alger's VDI provides (likely 4-8 GB; investigate) |
| Code changes happen on local + push | Code changes happen on local + push + Alger pulls (or auto-deploy on push) |
| Single user (the user) | Multi-user (PMs read; user + Alger eng admin) |

**Critical:** the user remains the only person who pushes dashboard code changes to git. Alger engineers may pull + restart but should not push without coordination.

---

## 10. Day-zero deployment checklist (for Alger IT)

When Alger is ready to spin up the VM:

- [ ] Provision Linux VM (32 GB RAM, 100 GB disk, internal network only, port 3099 open to PMs)
- [ ] Install Python 3.9+ (3.11 recommended); confirm: `python3 --version`
- [ ] Install nginx (or use Python's stdlib http.server in non-production-grade mode)
- [ ] Clone repo: `git clone https://github.com/JGY123/RR.git /srv/rr` (read-only access for engineers; user retains push)
- [ ] Copy initial `data/strategies/*.json.gz` from user's local laptop to `/srv/rr/data/strategies/` (one-time bootstrap)
- [ ] Create folders: `/srv/rr/inbox/`, `/srv/rr/processed/`, `/srv/rr/archive/csv/`, `/srv/rr/archive/json/`, `/srv/rr/logs/`
- [ ] Set up cron: weekly Monday 6 AM ingest job (template in §4)
- [ ] Wire `notify_alert` / `notify_success` to Alger's email/Slack
- [ ] Set up nginx with: `root /srv/rr/`, `gzip_static on`, `Cache-Control: no-cache, no-store, must-revalidate` for `*.html` + `*.json` + `*.json.gz`
- [ ] Add `/srv/rr/data/strategies/` and `/srv/rr/archive/` to standard backup tier
- [ ] Test from a representative PM VDI: open dashboard, switch strategies, click through tabs
- [ ] Memory profile per §8 test plan; report findings
- [ ] Set up health-check endpoint per §7
- [ ] Document the deployment internally (Alger's standard runbook)
- [ ] Hand off URL + access list to the user; user notifies PMs

**Estimated wall-clock to first-PM-loads-dashboard:** 2-4 hours of focused engineer time.

---

## 11. Open questions for Alger IT (the user can ask these)

1. **VDI memory allocation per PM session?** (Drives whether we need strategy-switch cleanup.)
2. **VDI persistence model — persistent or non-persistent profile?** (Drives whether localStorage state survives logoff.)
3. **Browser standardization?** (Chrome / Edge / both / Firefox?)
4. **Internal hostname for the VM** — `rr.alger.internal` is illustrative; what's the firm's convention?
5. **Notification channel preference** — email / Slack / Teams / ServiceNow?
6. **Existing Python environment for cron jobs?** (Are there standard service-account paths Alger uses?)
7. **Existing backup tier** — what's the SLA + retention?
8. **Existing monitoring stack** — Datadog / Grafana / Splunk / something else?
9. **Code-deployment cadence** — does Alger want auto-pull on git push, or manual review + pull?
10. **Compliance / audit trail** — does the firm require an audit log of who accessed the dashboard when? (Today: zero auth = zero access log. Apache/nginx access logs are server-side standard.)

---

## 12. What stays with the user (does not delegate)

- Dashboard code changes (push to git only by user)
- F-letter inquiries to FactSet (relationship + content)
- PM communication / onboarding / training
- Strategic roadmap decisions (the priorities in `ROADMAP.md`)
- Audit cadence (running `tile-audit` subagent quarterly)
- LESSONS_LEARNED maintenance
- Coordination with Alger eng on infrastructure changes

## 13. What goes to Alger eng (delegates)

- VM lifecycle (provisioning, patching, reboots)
- Cron orchestration + notification wiring
- Backup execution (just standard /srv/ tier inclusion)
- Network / firewall / VPN config
- nginx / web server config
- Monitoring + alerting setup
- VDI memory profile testing
- Day-to-day "the cron failed last night" triage
- Pulling new code when user pushes (or auto-pull config)

---

## 14. Closing

This deployment is intentionally simple: static HTML + Python ingest + standard infrastructure. Alger's engineers should not need anything fancy. If they're proposing Kubernetes / microservices / event sourcing — that's overkill; point them at `ROADMAP.md` §2 for the architectural reasoning.

The biggest risk is **NOT** the dashboard or the parser (both are stable); it's **the backup of CSV archives + per-strategy state**. Lose those and the canonical history of the firm's risk dashboard goes with them. Alger's standard backup tier handles this if the folders are explicitly enrolled — make sure they are.
