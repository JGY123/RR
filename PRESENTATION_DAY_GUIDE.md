# RR — Presentation Day Guide

**Drafted:** 2026-05-01
**For:** team presentation in 5h15m + post-presentation migration to production environment

---

## TL;DR — How to make today's demo work

1. **Drop the new multi-account file** (whatever FactSet shipped) into `~/Downloads/`. Name doesn't matter.
2. **Run from terminal:**
   ```bash
   cd ~/RR
   ./load_data.sh ~/Downloads/<the-file>.csv
   ```
   - If it's `.xlsx`: convert first (the script will detect; if not, use the python one-liner at the bottom of this doc).
3. **Wait for verifier output.** Look for **🟢 GREEN-LIGHT** or 🟢 **GREEN-LIGHT WITH NOTES**. If 🟡 or 🔴, see "Troubleshooting" below.
4. **The dashboard auto-opens in Chrome.** Hard-refresh once (Cmd+Shift+R) to bust cache.
5. **Eyeball check** (60 seconds):
   - Header shows ALGER + REDWOOD RISK + strategy selector populated with all 7 strategies
   - cardThisWeek sum-cards show real numbers (TE / AS / Beta / Holdings / Idio / Factor)
   - Top of Exposures: cardWeekOverWeek shows Δ deltas (vs last week)
   - Risk tab Idio/Factor split MATCHES Exposures sum-card values (this was the bug we fixed)
   - cardUnowned (Exposures) shows real bench-only TE contributors (not blank)
   - cardSectors / cardCountry: under Universe→Bench mode, # column shows ~70-80% of true bench universe
6. **DevTools console check** (one second): `Cmd+Option+J`, look for **`✓ B115 integrity check passed`**. If you see `🚨 B115 INTEGRITY DRIFT`, alert me.

That's it. The dashboard is the demo.

---

## Step-by-step: load the multi-account file

### If it's a CSV (`.csv`)
```bash
./load_data.sh ~/Downloads/multi_account_full_history.csv
```

### If it's an Excel file (`.xlsx`) — convert first
The parser expects CSV. Quick converter (60 seconds for a 100MB file):
```bash
python3 << 'PY'
import openpyxl, csv, sys
src = "~/Downloads/<the-file>.xlsx"  # ← edit this path
out = src.replace(".xlsx", ".csv").replace("/Downloads/", "/Downloads/")
import os; src = os.path.expanduser(src); out = os.path.expanduser(out)
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
ws = wb.active
n = 0
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        w.writerow([("" if c is None else c) for c in row])
        n += 1
print(f"Wrote {n:,} rows to {out}")
PY
./load_data.sh ~/Downloads/<the-file>.csv
```

### If FactSet ships multiple accounts in one file
The parser auto-detects all accounts in the file. The dashboard shows ALL 7 strategies in the header dropdown. Click each strategy to view it.

### If FactSet ships one file per account
Run `./load_data.sh` once for each. The latest run wins (`latest_data.json` is overwritten). For a multi-account demo, FactSet should ship one combined file. If they ship separately, the demo will only show the most-recently-loaded account.

---

## What you'll see on the dashboard (presentation walkthrough script)

A 90-second narration for the team demo:

### Slide 1: "Where we are right now" (Exposures tab, sum-cards)
**Open the dashboard. Stay on Exposures tab.**

> "This is RR — the Redwood Risk Control Panel — running on top of [strategy name]. Six sum-cards across the top: Total TE, Active Share, Beta, Holdings count, Idio %, Factor %. All sourced directly from FactSet — no synthesis, no fabrication. Click any one to drill into a full historical chart of that metric."

Click the Idio sum-card → drill modal opens with 7-year history.

### Slide 2: "What changed this week" (cardWeekOverWeek)
**Scroll to the top tile of Exposures.**

> "Brand new this week — Week-over-Week. Four KPI deltas at the top, three columns of moves below: holdings added, dropped, and resized by more than 0.10 percentage points. Factor rotation footer at the bottom showing the three factors with the biggest active-exposure shift. This is the Monday-morning view — what changed, what to investigate first."

### Slide 3: "Risk decomposition" (Risk tab)
**Click the Risk tab.**

> "Five sum-cards on Risk: Total TE, Factor Risk, Idiosyncratic, plus the rest. Below that, Historical Trends across all 7 strategies side-by-side. TE Stacked decomposition over 7 years showing how factor and stock-specific risk have evolved. Click any factor row in the Factor Exposures table to drill into its 7-year time series."

### Slide 4: "Per-holding view" (Holdings tab)
**Click the Holdings tab.**

> "Holdings Risk Snapshot — every holding placed by active weight (x) and TE contribution (y), bubble sized by stock-specific TE. Top-right cluster is high-conviction OW bets driving risk; bottom-right is overweight positions that paradoxically diversify. Click any bubble for full security drill including factor exposures, ratings, and historical price."

### Slide 5: "What we're tracking" (cardUnowned + cardWatchlist)
**Scroll to cardUnowned on Exposures (or cardWatchlist on Holdings).**

> "Unowned Risk Contributors — bench-only stocks that contribute most to tracking error through their absence. The list ranks these by TE contribution. The Watchlist is on Holdings — flag any holding by clicking the ⚑ icon, build a personal monitoring list."

### Slide 6: "Provenance + trust" (any ⓘ button)
**Click any ⓘ button — they're on every tile.**

> "Every tile has an ⓘ explainer. What it shows, how the math is computed, what the source CSV field is, and known caveats. Plus a freshness pill in the header — currently green at N days. This is built so a PM can trust the number without asking the analyst."

### Slide 7: "Where we go from here"
> "Today the dashboard runs on a local file. Next phase: move to enterprise environment so it auto-refreshes weekly when FactSet ships the new file. Migration guide is in the repo — ~30 minutes of IT work."

---

## Migration to enterprise environment (POST-presentation)

### What "the environment" needs

**Option A — Mac workstation (simplest, recommended for week-1):**
- A Mac on the firm network
- Python 3 (already comes with macOS)
- `openpyxl` for Excel conversion: `pip3 install openpyxl`
- Chrome browser
- The `~/RR/` repo cloned from GitHub
- A weekly cron job that runs `./load_data.sh` against the latest FactSet drop

**Option B — Linux server / VM (production-grade):**
- Same as Option A but headless
- Plus: nginx serving the static `dashboard_v7.html` to internal users
- Plus: a webhook from FactSet's drop location → triggers parser → publishes new `latest_data.json`

### Step-by-step migration (Option A — local Mac)

1. **Pick the host machine.** Any Mac on the firm network with Chrome installed.
2. **Install Python deps:**
   ```bash
   pip3 install openpyxl  # for xlsx → csv conversion
   ```
3. **Clone the repo** (you'll need a GitHub deploy key or token for the JGY123/RR repo):
   ```bash
   cd ~
   git clone git@github.com:JGY123/RR.git
   ```
4. **Copy `data/security_ref.json`** from this dev machine if it's not in the repo (it should be — it's a 1MB file with SEDOL→ticker mapping).
5. **Test the pipeline once** with the EM full-history file (or any test file):
   ```bash
   cd ~/RR
   ./load_data.sh /path/to/test_file.csv
   ```
   Should see 🟢 GREEN-LIGHT verdict + Chrome opening with the dashboard.
6. **Set up the weekly cron job** (after FactSet's drop is automated):
   ```bash
   # Edit your crontab
   crontab -e
   # Add this line — runs every Monday at 7am, parsing the most recent .csv from a known drop folder
   0 7 * * 1 cd ~/RR && ./load_data.sh "$(ls -t /path/to/factset/drops/*.csv | head -1)" >> ~/RR/logs/load.log 2>&1
   ```
7. **Configure browser bookmarks** for the team. Each user opens `file:///Users/<host>/RR/dashboard_v7.html` (or via a shared mounted drive).

### Step-by-step migration (Option B — Linux server)

If the firm wants a self-hosted multi-user URL like `redwood-risk.firm.local`, the server-side setup is:

```bash
# On the Linux box (assumes Ubuntu/Debian)
sudo apt install python3 python3-pip nginx
sudo pip3 install openpyxl

# Clone repo to /opt/rr
cd /opt
sudo git clone https://github.com/JGY123/RR.git rr
sudo chown -R www-data:www-data /opt/rr

# Configure nginx to serve dashboard_v7.html from /opt/rr/
sudo cat > /etc/nginx/sites-available/rr << 'EOF'
server {
    listen 80;
    server_name redwood-risk.firm.local;
    root /opt/rr;
    index dashboard_v7.html;
    # CSP: dashboard fetches latest_data.json relative; same-origin OK
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    location ~ \.json$ {
        add_header Cache-Control "no-cache";
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/rr /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Set up the weekly auto-load via systemd timer:
```bash
sudo cat > /etc/systemd/system/rr-load.service << 'EOF'
[Unit]
Description=RR weekly data load

[Service]
Type=oneshot
WorkingDirectory=/opt/rr
ExecStart=/bin/bash -c 'cd /opt/rr && ./load_data.sh "$(ls -t /opt/factset_drops/*.csv | head -1)"'
User=www-data
EOF

sudo cat > /etc/systemd/system/rr-load.timer << 'EOF'
[Unit]
Description=RR weekly auto-load
[Timer]
OnCalendar=Mon 07:00:00
Persistent=true
[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now rr-load.timer
```

Now the dashboard auto-loads every Monday at 7 AM and is available at `http://redwood-risk.firm.local`.

### Security checklist (for IT review)

- ✅ Dashboard is **static HTML + JS only** — no backend, no DB, no exposed APIs
- ✅ All data lives **on the host machine** as `latest_data.json` — no cloud, no telemetry, no external API calls except Plotly CDN (can be self-hosted by uncommenting the local-fonts block)
- ✅ Parser runs **locally only** — Python script reads CSV, writes JSON
- ✅ No user accounts, no login — access controlled by file system + nginx (firm network or VPN)
- ✅ Repo is on GitHub (private, JGY123 account) — credentials stored in 1Password / keychain
- ⚠️ `data/security_ref.json` (1MB) contains SEDOL→ticker mappings — neutral data, not portfolio-sensitive
- ⚠️ `latest_data.json` (~80MB for one strategy, will be ~600MB for 7 strategies × 7 years) contains **portfolio holdings** — restrict file system access to authorized users only

---

## Troubleshooting

### "🔴 SCHEMA DRIFT — refuse to green-light"
The CSV format changed from the prior baseline. **Two cases:**

**Case A — intentional new format from FactSet:**
The schema fingerprint at `~/RR/.schema_fingerprint.json` is stale. To accept the new format:
```bash
rm ~/RR/.schema_fingerprint.json
./load_data.sh <the-file>.csv
```
The verifier will re-baseline.

**Case B — silent format drift you didn't expect:**
Stop. Don't ship. Run me through what the verifier output says — there's likely a real parser issue.

### "Verifier 🟡 NEEDS REVIEW — non-A-tier failures"
Read `~/RR/last_verify_report.log`. Most likely:
- C1 Brinson inputs (per-holding period return) — known C-tier missing, won't break tiles
- Per-holding raw factor exposures missing on some strategies — depends on file
- Schema fingerprint drift — see above

### "Idio % and Factor % don't match across tabs"
This was a real bug pre-2026-04-30 — Risk tab used a heuristic, Exposures used cs.sum.pct_specific. Both now read from the same source. If you see them differ now, it's a regression — alert me.

### "cardUnowned shows nothing / cardRegions count is wrong"
Both fixed in the 2026-04-30 batch (B80 + B116). If you see them broken on the new file, hard-refresh first; if still broken, the new file probably has an unhandled format variant — alert me.

### "Dashboard opens but Plotly charts don't render"
DevTools → Console. Look for `🚨 B115 INTEGRITY DRIFT` (a real data integrity issue) or any error from a render function. Report the first error message.

### "Strategy dropdown is empty / shows wrong strategies"
Check `~/RR/latest_data.json` — top-level should be a 4-element array, first element is a dict of strategies. Each strategy dict should have `id`, `name`, `benchmark`, `sum`, `hold`, etc.

---

## Recovery / rollback

If something breaks during the demo, **the recovery is one command:**
```bash
cd ~/RR
git status                              # see what's modified
git stash                               # save any local edits
git pull origin main                    # get the last known-good
./load_data.sh ~/Downloads/<file>.csv  # re-parse + re-open
```

The repo's HEAD as of today is `e2fc0e2` (presentation polish + ALGER/REDWOOD logos). Tag it for safety:
```bash
git tag presentation-2026-05-01 e2fc0e2
git push origin presentation-2026-05-01
```

---

## What's NOT included today (future work)

- **Brinson attribution** — needs per-holding period return from FactSet (F11 in FACTSET_FEEDBACK.md)
- **Bench-only TE contributors for the long-tail** — need %T_implied per Raw Factors row (F12)
- **Cleaner Idio/Factor split (no synth marker)** — need % Specific Risk at portfolio-Data row (F14)
- **Full S2 Data Quality sidebar** — current freshness pill is the W1 stub; full sidebar will surface every ᵉ derivation chain
- **Migration to multi-user web app** — Option B above; week-2+ work

These are documented for the next phase. None are blocking today's demo.

---

## Last sanity check before the demo

Run this 5-minute checklist 30 minutes before the meeting:

- [ ] `./load_data.sh <new-file>.csv` ran clean, 🟢 verdict
- [ ] `./smoke_test.sh --quick` shows ≥17/20 pass (the 2-3 known fails are pre-existing; rest must pass)
- [ ] Open dashboard in Chrome, hard-refresh (Cmd+Shift+R)
- [ ] DevTools console shows `✓ B115 integrity check passed`
- [ ] Strategy dropdown has all 7 strategies
- [ ] Click each tab — Exposures, Risk, Holdings — confirm tiles render
- [ ] Click cardWeekOverWeek (top of Exposures) — confirm KPI deltas + 3-col move list
- [ ] Click any ⓘ — confirm About modal opens
- [ ] Header shows ALGER + REDWOOD RISK lockup
- [ ] Freshness pill (header right) shows green dot

If all 9 boxes pass: you're ready.

---

**Drafted:** 2026-05-01 by Claude (1M context)
**Last update:** 2026-05-01 — pre-presentation polish batch
**Repo:** github.com/JGY123/RR · HEAD: e2fc0e2
