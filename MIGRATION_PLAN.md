# RR Migration Plan — From local laptop → professional environment + multi-account massive run

**Drafted:** 2026-04-30 · Owner: Yuda + Claude · Source: Q82 from the Inquisitor queue.

This is the runbook for getting RR ready for production use.

---

## Phase 0 — Where we are right now

✅ **Parser** is header-driven, handles the new Raw Factors layout (group_size=23) including the moved fields (mcap, ADV, vol_52w, OVER, REV, VAL, QUAL, MOM, STAB).
✅ **SEDOL → ticker_region merge** working — dashboard shows proper tickers (SIMO-US, WIE-AT, 5706-JP) instead of SEDOLs.
✅ **GSC quick sample** (5 weekly periods) flows end-to-end: 54 holdings, 52 SEDOL-matched, all factor data populated. Verifier: GREEN-LIGHT WITH NOTES.
✅ **Anti-fabrication policy** in place — every synth value carries a marker; no silent computed values.
✅ **Repo on GitHub** (JGY123/RR), clean history (latest_data.json scrubbed), ~22 MB.

⏳ **Outstanding:** per-holding period return + Brinson inputs (C-tier from FactSet, not blocking).
⏳ **Pending data:** 1-year GSC test sample (in the works), then full multi-year multi-account run.

---

## Phase 1 — Validate GSC full history (one-account smoke test)

### Goal
Confirm the parser + dashboard handle a long-history single-strategy file end-to-end before risking the multi-account run.

### Steps when 1-year GSC sample arrives

1. **Drop the CSV in `~/Downloads/`** with a clear name (e.g., `gsc_1yr_test.csv`).
2. **Run** `./load_data.sh ~/Downloads/gsc_1yr_test.csv`.
3. **Watch the verifier output** — should see:
   - `🟢 GREEN-LIGHT` ideally, or `🟢 GREEN-LIGHT WITH NOTES` (C-tier nice-to-haves can stay open).
   - If `🔴 SCHEMA DRIFT` warning → the CSV format changed again. Inspect the diff section, decide if intentional, then `rm ~/RR/.schema_fingerprint.json` to acknowledge.
   - If `🔴 N CHECK(S) FAILED` on A-tier → STOP. Investigate. Likely the parser merge didn't pick up something. Check `last_verify_report.log`.
4. **Open the dashboard** (auto-opens via `load_data.sh`).
5. **Walk every tab and tile** with this checklist:
   - [ ] Exposures: This Week, sum-cards (TE/Idio/Factor), cardSectors (table + chart), cardCountry (map + chart + table), cardGroups (treemap), cardRegions (heatmap), cardFacRisk + cardFacButt, cardFacDetail, cardChars, cardScatter, cardWatchlist
   - [ ] Risk: 5 sum-cards, Historical Trends, TE Stacked, Beta History, Factor Contribution Bars, Factor Exposures table, Risk by Dimension, Country×Factor heatmap, Factor Exposure History, Correlation Matrix
   - [ ] Holdings: tickers display as TKR-REGION (not SEDOL), spotlight ranks populated, MCR populated, market cap populated
   - [ ] Drill modals: TE / Idio / Factor / Beta / AS / Holdings — all open without error, multi-period impact panel shows accurately
   - [ ] Date selector works — switching weeks updates factor charts
   - [ ] No console errors (DevTools → Console)
6. **Smoke test in script form:** `./smoke_test.sh` should show 19/19 pass once strategies field is correct.
7. **Document any new issues** in `~/RR/FACTSET_FEEDBACK.md` immediately so they don't get lost.

### Sign-off criterion
All visible tiles render. All numbers in the dashboard match what FactSet workstation shows for GSC. Spot-check 5-10 numbers against FactSet workstation directly.

---

## Phase 2 — Move RR to your professional environment

### Goal
Get RR off the laptop and into a stable, backed-up workspace where you can rely on it daily.

### Decision: which professional environment?

You have two paths:

**Path A — Stay on local Mac, add stronger backups + automation.**
- Pro: zero migration friction, existing repo + scripts work as-is.
- Con: relies on one machine. Laptop dies → recovery is painful.
- Best for: keeping things simple while validating the full workflow.

**Path B — Move to a workstation / server with cloud backup.**
- Pro: machine-independent, daily auto-pulls, easier multi-user.
- Con: setup time, may need IT involvement at Redwood.
- Best for: if RR is going to become PM-team standard.

**Recommendation:** start with Path A. Migrate to Path B only when (1) you've used RR for ≥4 weeks daily without issue and (2) someone else needs access.

### Path A — local Mac hardening checklist

1. **Confirm GitHub backup is current.** Run from `~/RR/`:
   ```bash
   git status                # should be clean
   git push                  # syncs to JGY123/RR
   ```
2. **Set up automatic backups.** Time Machine on your Mac, plus the GitHub remote, plus an optional iCloud/Dropbox snapshot of `~/RR/` weekly (script provided in Phase 4).
3. **Pin the working dependencies.** Run once and capture:
   ```bash
   python3 --version > ~/RR/.python-version
   ```
4. **Document the "happy path" for daily use** in `~/RR/RUNBOOK.md` (separate file — see Phase 4).

### Path B — workstation/server setup (when ready)

1. Install Python 3.11+ on target machine.
2. Clone the repo: `git clone https://github.com/JGY123/RR.git`.
3. Set up `gh` CLI auth (JGY123 account) so pushes work.
4. Test parse: `./load_data.sh sample_file.csv`.
5. If using a remote machine, pick a way to view the dashboard:
   - **Local browser via SSH tunnel** — works for one user.
   - **Hosted internal URL** — needs IT to provision.
   - **Docker + nginx** — works but adds complexity.
6. Set up a cron / scheduled task for weekly pulls (Phase 4).

---

## Phase 3 — Massive run (full multi-year, multi-account)

### Pre-flight

Before the FactSet operations team runs the full multi-year multi-account export:

1. **GSC full-history validated** (Phase 1 complete).
2. **`UPCOMING_FORMAT_CHANGE.md` confirmed implemented** in the parser — check that mcap/adv/ranks merge from Raw Factors works.
3. **`./smoke_test.sh` is green** (`19/19 pass`).
4. **`.schema_fingerprint.json` is current** (re-baselined after the GSC quick sample).
5. **GitHub remote is in sync** with local (`git status` shows nothing ahead/behind).
6. **`load_data.sh` runs cleanly** end to end on the GSC sample without manual intervention.

### Receiving the full-history file

1. **File expected size:** 6 strategies × ~10 years weekly history × 1218 holdings ≈ **3-5 GB CSV**.
2. **Place in** `~/Downloads/` (rename to clarify, e.g., `factset_full_history_2026-05-XX.csv`).
3. **DO NOT commit it** — it's runtime data; .gitignore already excludes `latest_data.json` and similar patterns.
4. **Run the parser:**
   ```bash
   ./load_data.sh ~/Downloads/factset_full_history_2026-05-XX.csv
   ```
   Expect ~3-10 minutes parse time depending on machine.
5. **Verifier should be 🟢 GREEN-LIGHT** for all 6 strategies. If any single strategy shows A-tier failures, STOP and investigate before trusting any data.
6. **Walk every tile per Phase 1 checklist**, this time switching across all 6 strategies (IDM, IOP, EM, ISC, ACWI, GSC) and verifying:
   - Each strategy's TE / Idio% / Factor% match FactSet workstation
   - Holdings counts match
   - Sector/country exposures look right per strategy

### Sign-off criterion
Every strategy ships data through every tile. Spot-check ≥10 numbers per strategy against FactSet. Sign off in `~/RR/SESSION_STATE.md` with date + verifier output snapshot.

---

## Phase 4 — Steady state (weekly updates + new accounts)

### Weekly update flow

The FactSet team will ship a fresh CSV approximately weekly (Mon AM ideally per Q131). The pattern:

1. **Receive new CSV** (could be incremental "this week only" or a fresh full history).
2. **For incremental files:** `./load_data.sh ~/Downloads/this_week.csv`. The parser detects new dates, appends them to `hist.*` arrays, leaves old data intact. *(Append-only behavior — Q84.)*
3. **For full-history refreshes** (if FactSet re-sends everything): same command. Parser overwrites with the latest, but since each refresh contains the full historical record, no data is lost.
4. **Verifier runs automatically.** If green, dashboard is updated. If red, investigate.
5. **If `.schema_fingerprint.json` warns of drift:** review the diff, decide if intentional, delete to acknowledge.

### Adding a new account / strategy

When FactSet adds a new account (e.g., Alger domestic):

1. **Receive the new account CSV** (could be standalone or merged with existing).
2. **If standalone:** parse it once to verify the account's data shape works. Then merge into the main `latest_data.json` workflow.
3. **Update `~/RR/CLAUDE.md`** — add the new strategy to the Strategy Account Mapping table:
   ```
   | File Code | Dashboard ID | Full Name | Benchmark |
   | NEWCODE | NEW | New Strategy Name | Benchmark Index |
   ```
4. **Update the dropdown** — currently the strategy switcher reads from `latest_data.json` automatically, so no UI change needed.
5. **Run smoke test** to confirm.

### Filling historical gaps in an existing account

Rare scenario — if an existing account needs more history backfilled:

1. **Stop and consult.** This is a one-off operation; better to walk through it with Claude in a session.
2. **Generally:** run the gap-filler CSV through `load_data.sh`, parser appends.
3. **Verify the gap is filled** by checking `cs.hist.sum.length` for that strategy.

### Backup cadence

- **Every parse:** automatic write of `latest_data.json` (gitignored — local only).
- **Every commit:** GitHub remote auto-syncs on `git push`.
- **Weekly snapshot:** copy of `latest_data.json` archived elsewhere (S3/Drive/external drive). Recommended script (run via cron):
  ```bash
  # ~/RR/backup_weekly.sh
  TS=$(date +%Y%m%d)
  cp ~/RR/latest_data.json ~/Backups/RR_snapshots/data_$TS.json
  ```

### Q84 confirmed retention policy

**Keep all weeks forever.** No pruning. Storage cost is negligible (~50 MB per year × 6 strategies = ~300 MB after 10 years, far under any sane storage limit).

---

## Phase 5 — Disaster recovery

### If the laptop dies / `latest_data.json` is lost

1. **Re-clone the repo** on a working machine: `git clone https://github.com/JGY123/RR.git`.
2. **You have:** all code, all docs, all parsers, all decisions. **You don't have:** the latest parsed JSON.
3. **Re-parse from the latest CSV** — if you have it. If not, ask FactSet to re-send.
4. **For older data:** if you set up the weekly backup script (Phase 4), restore from there. Otherwise, FactSet should be able to re-export.

### If a parser change introduces a regression

1. **Check tags first** — every risky edit is tagged `working.YYYYMMDD.HHMM.pre-X`. Roll back via:
   ```bash
   git reset --hard working.YYYYMMDD.HHMM.pre-X
   ```
2. **Re-run the parser** and verify the issue is gone.
3. **Investigate the regression** before pushing again.

### If FactSet ships a CSV that breaks parsing

1. **Don't panic** — the parser is header-driven and warns rather than fails.
2. **Check `.schema_fingerprint.json` diff** to see what changed.
3. **Update the parser** to handle the new shape (similar to the 2026-04-30 group_size=23 update).
4. **Delete the schema fingerprint** and re-baseline.

---

## Open items / things still to do (per Inquisitor queue)

These weren't blocking the migration but should be tracked:

1. **Append-only history pipelines** — formalize in code (currently relies on parser doing the right thing each run).
2. **Auto-fetch from SFTP/S3** when FactSet sets up delivery (currently manual download from email).
3. **Auto-screenshot regression diffs** after each pull (Q93).
4. **Email/Slack notifications** when verifier fails (Q83).

---

**TL;DR:** when the 1-year GSC sample arrives → run `./load_data.sh` → walk through tabs → spot-check numbers vs FactSet. If green, ask for the multi-year multi-account file. Same flow. Sign off, then production weekly cadence.
