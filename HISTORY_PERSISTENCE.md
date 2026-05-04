# History Persistence Architecture — Append-Only Model

**Drafted:** 2026-04-27
**Origin:** user direction during marathon — "we are building everything to be ready to ingest and show the full history which is long. Many would have 15 years of data. Once the massive run lands and is confirmed parsed, history doesn't change. Future uploads are appends. Anyone opening the dashboard should see all of it pre-populated."
**Status:** **proposal — needs design review before implementation.** Not in scope for the current marathon; logged here so it isn't lost.

---

## The principle in one sentence

**A loaded JSON is the cumulative state of the universe; subsequent uploads add new periods to the existing state, never replace it.** Anyone who opens the dashboard sees the full historical depth that's ever been ingested.

---

## Today's behavior (the gap)

- User drags a JSON onto the page.
- `parseFactSetCSV` (or direct JSON load) replaces `_data` entirely with the new file's content.
- If the new file covers fewer weeks than the previous one, the old depth is **lost from view**.
- There's no "merge" path — every load is a full replace.
- localStorage holds toolbar/notes/flag state but NOT data.

Implication today: if user drops a 1-week incremental CSV onto a tab that previously had 156 weeks loaded, those 156 weeks vanish from the rendered dashboard until the user finds and re-drops the larger file.

---

## What "append-only" means concretely

Three sub-questions, each with a recommended answer:

### Q1 — Where does persistent history live?

**Option A: localStorage** (browser-only)
- Pro: zero infra. Persists across tabs/sessions.
- Con: ~5–10 MB cap per origin; a 15-year × 7-strategy file would be 100 MB+. Doesn't survive cache clear or different browser.
- Verdict: insufficient on its own.

**Option B: IndexedDB** (browser-only, larger cap)
- Pro: same browser-only model, but ~50% of free disk available — easily handles 100 MB+.
- Con: async API, slightly more involved storage code. Still browser-bound.
- Verdict: workable as a tier-1 layer; does NOT solve cross-machine sharing.

**Option C: Local file** at a known path (e.g., `~/RR/data/cumulative.json.gz`)
- Pro: durable, shareable, version-controllable.
- Con: requires a small server endpoint (or filesystem write via `electron`/`tauri`/`File System Access API`) to write back. Browsers can read user-dropped files but can't write to disk without explicit save.
- Verdict: best for a desktop-app future. SurpriseEdge uses this exact pattern (`appDataDir/universes/*.json.gz` with manifest).

**Option D: Cumulative JSON committed to repo** (what RR could do today, low-tech)
- Pro: zero code change. User runs the parser on every new CSV, the parser MERGES into `data/cumulative_history.json` (gzipped), commits it, dashboard loads that file by default.
- Con: requires parser-side merge logic + git commit discipline; a 15-year/7-strategy file gzipped will be ~50 MB which is large but tractable for git.
- Verdict: simplest path that achieves the goal, fits RR's current single-file static-HTML model.

**Recommendation: Option D + Option B as cache.** Parser merges new periods into `data/cumulative_history.json.gz`; dashboard loads it on init from a relative URL; subsequent in-session uploads merge in IndexedDB (so user can preview a new CSV before promoting it to the canonical repo file).

### Q2 — How does the merge work?

The parser's output has these per-strategy arrays of time-keyed entries:
- `hist.summary[]` — weekly TE/AS/Beta/Holdings rollup
- `hist.fac{}` — per-factor weekly exposure history
- `hist.sec{}` / `hist.reg{}` / `hist.country{}` — currently empty (B6 backlog) but will be populated
- `snap_attrib[].hist[]` — 18 Style Snapshot weekly rows per attribution item
- `raw_fac[sedol].hist[]` — per-security weekly raw factor exposures

For each, merge logic is:
```python
# In factset_parser.py — new function _merge_into_cumulative(new_strategy, old_strategy)
# For each per-strategy time-keyed array:
for entry in new_strategy["hist"]["summary"]:
    if not any(e["d"] == entry["d"] for e in old_strategy["hist"]["summary"]):
        old_strategy["hist"]["summary"].append(entry)
old_strategy["hist"]["summary"].sort(key=lambda e: e["d"])
# (same dedupe-by-date pattern for every other time-keyed structure)

# For "current state" fields (sectors[], countries[], factors[]) — REPLACE with newest, since these are point-in-time snapshots that get superseded:
old_strategy["sectors"] = new_strategy["sectors"]
old_strategy["factors"] = new_strategy["factors"]
old_strategy["current_date"] = max(old_strategy["current_date"], new_strategy["current_date"])
old_strategy["available_dates"] = sorted(set(old_strategy["available_dates"] + new_strategy["available_dates"]))
```

**Two storage classes per data field:**
- **Time-keyed history** (append, dedupe by date) — `hist.*`, `snap_attrib[].hist[]`, `raw_fac[].hist[]`
- **Current state** (replace with newest) — `sectors`, `factors`, `countries`, `regions`, `groups`, `industries`, `hold[]`, `unowned[]`, `sum`, `chars`

### Q3 — How does the dashboard load it?

Step 1: dashboard tries `fetch('/data/cumulative_history.json.gz')` on init. If 200, decompress + load.
Step 2: if user drops a new CSV/JSON, dashboard tries to MERGE it (in IndexedDB-backed local-only state) instead of REPLACE.
Step 3: a small status pill in header shows "📦 Loaded from data/cumulative — 156 weeks (Mar 2025 → Mar 2026)" — gives confidence about depth.
Step 4: the in-session merged state can be promoted to the canonical file via a new "Save merged history" button → triggers parser to rewrite the cumulative file + git commit.

---

## What this enables

- The dashboard becomes self-contained: anyone receives the HTML + the cumulative.json.gz, has the full history.
- Email-snapshot exports preserve the full multi-year context.
- Time-series tiles (cardRiskHistTrends mini-charts, cardTEStacked area, factor drill modal hist chart) actually populate at full depth.
- Period selectors (B109 Impact period 1Y/6M/3M etc.) start showing all options instead of only "Latest"/"Full Period".
- B102 cardRiskByDim, B103 per-security factor drill, B104 portfolio raw aggregate — all benefit because their historical companion charts will populate from real history.

---

## Risk and edge cases

| Risk | Mitigation |
|---|---|
| User drops CSV with a date that already exists in cumulative — which value wins? | Default: NEW file's value wins (user just downloaded fresh data). Make this configurable via a `merge_policy` flag — `keep_existing` for audit-trail use cases. |
| Universe SHIFTS over time (a stock added to/removed from benchmark) — how does that show up? | Each `hold[]`, `factors[]`, `sectors[]` is keyed by current date. The TIME-KEYED histories (per-factor / per-security) carry the period each entry was valid. Stocks dropped from universe stay in older `hist.fac.X[]` entries but disappear from current `factors[]`. |
| `data/cumulative_history.json.gz` becomes >100 MB | Split per-strategy: `data/cumulative_IDM.json.gz`, `data/cumulative_EM.json.gz`, etc. Manifest file lists which are present. SurpriseEdge does this. |
| Parser change midway through a multi-year ingest creates schema drift | Parser version tag in JSON header. On merge: if `old.parser_version` != `new.parser_version`, run a migration step (per-version function). Same pattern as data-foundation-v1's PARSER_VERSION bump. |
| Data integrity — how do we know the cumulative is correct? | New `pytest test_cumulative_merge.py` test suite: ingest two non-overlapping CSVs, merge, verify all dates present + no duplicates. Add to B101 deferred-test-coverage scope. |

---

## Sequencing — when to build this

This is a major architecture change. **Do NOT build during marathon.** Sequencing:

1. Marathon → close all tile signoffs at current state (no history changes).
2. After tier1-review-signoff: B105/B106 design-polish post-marathon items (visual).
3. **B114 (new) — History persistence architecture** — implement Option D + Option B per this doc. ~6–10 hours.
4. Once B114 lands: parse the production massive-run CSV THROUGH THE NEW MERGE PATH; this makes the cumulative file the authoritative state going forward. Every future CSV upload appends.
5. Tier 2 tiles (B102/B103/B104) build against full history.

**B114 must land BEFORE the massive-run ingest** so the first ingest establishes the cumulative file rather than being a one-shot replace.

---

## Open questions for the user

- Q1: confirm the merge-conflict default ("new wins" — when same date is in both old and new, take new). Or "keep existing" — old date never overwritten? Or split-by-source-of-truth where some fields are old-wins and some new-wins?
- Q2: how often does a date's data legitimately change? (Q4 2025 reported in Jan 2026 — but in May 2026 someone re-runs and the data changes. Is that a thing?)
- Q3: is single-file `cumulative_history.json.gz` acceptable, or do we want per-strategy files from day 1? Performance of a 100 MB JSON load on a slow connection is the gating concern.
- Q4: any compliance / audit-trail requirement that we keep an immutable record of every weekly upload separately, even after merge?

---

## Where this doc lives

`HISTORY_PERSISTENCE.md` at repo root. Linked from `BACKLOG.md` under future B114 entry. Reviewed and updated when B114 schedule comes up.

---

## 2026-05-04 update — what's changed since the original draft

### State of play (post audit cycle)

The original draft (April 2026) framed B114 as a single architectural project gated on multiple unknowns. After the May 2026 audit cycle and the cardTEStacked T1 RED finding, the picture is sharper:

1. **`hist.summary` IS populated in current production data** — 383-618 weeks per strategy across all 6 (probed via `data/strategies/<ID>.json`). The split-file pipeline (`load_multi_account.sh` + `merge_em_history.py`) already produces multi-year per-strategy files. The "file replace = history wipe" risk in the original draft (Q23) is partially mitigated today by always loading from the split files, not the monolithic file.

2. **Per-week `pct_specific` / `pct_factor` was the missing piece.** F19 (parser fix shipped 2026-05-04, FORMAT_VERSION 4.3) closes this — `_hist_entry()` now joins per-week riskm rows and includes pct_specific/pct_factor in `hist.summary[]`. Verified by 7 unit tests + manual probe (GSC latest week: Σ|sector mcr| = 69.9 = sum.pct_specific exactly).

3. **F12(a) — the runtime fallback** — cardTEStacked now resolves per-week split via three tiers: source-direct (after F19) → MCR-derived (Σ|sector mcr| via L2-verified path) → broadcast (last-resort). The chart renders correctly today even on pre-F19 data because tier 2 uses sector MCR which IS populated in current files.

4. **Cross-tile week-marker sweep** (2026-05-04): cardTEStacked, cardBetaHist, cardCashHist, cardFacHist all now show a vertical marker at `_selectedWeek` for week-flow consistency. (Was only on cardRiskHistTrends mini-charts before.)

### Implications for B114 scope

**What B114 still needs to do** (size estimate revised):

| Item | Original estimate | 2026-05-04 status | Revised |
|---|---|---|---|
| Parser merge logic (`merge_into_cumulative(new, existing)`) | 2-3 hrs | **Still TODO**. F19 + split-file pipeline are independent of merge. | 2-3 hrs |
| Cumulative file format + naming convention | 1-2 hrs | Per-strategy split-file convention already exists at `data/strategies/<ID>.json` — this IS the cumulative format. Merge logic just appends new weeks to each. | **0.5-1 hr** (just the merge entry-points + manifest stamp) |
| Dashboard fetch path | 1-2 hrs | Already loads from `data/strategies/index.json` + per-strategy. No new fetch path needed. | **0 hrs** (no change) |
| IndexedDB cache for in-session preview | 1-2 hrs | Optional — current architecture already supports preview via drag-drop JSON. Not blocking. | **deferred to post-B114** if at all |
| Cumulative-save UI button | ~30 min | Optional — `load_data.sh` + commit pattern is the current promotion path. | **deferred** |
| Test suite (`test_cumulative_merge.py`) | ~30 min | Net new. | 30-60 min |

**Revised B114 size: 3-5 hrs** (down from 6-10 hrs). The split-file pipeline + F19 already did the heaviest lifts.

### B114 next-steps inventory (when scheduled)

1. Define the merge contract:
   - Input A: existing `data/strategies/<ID>.json` (cumulative)
   - Input B: new ingest output for `<ID>` (single CSV / multi-week CSV)
   - Output: merged `<ID>.json` where every (week × field) is the union, with conflict policy (default: new-wins, configurable).
2. Implement `merge_strategy_into_existing(new_strategy, existing_path) -> merged` in `factset_parser.py`:
   - Merge `hist.summary[]` by date (deduplicate, new-wins on conflict)
   - Merge `hist.fac[name][]`, `hist.sec[name][]`, `hist.ctry[name][]`, `hist.reg[name][]`, `hist.grp[name][]`, `hist.ind[name][]`, `hist.chars[metric][]` — same date-keyed dedupe per name.
   - Replace top-level "current" arrays (`sum`, `sectors`, `countries`, etc.) with new-ingest values (current state always reflects latest CSV).
   - Stamp `parser_version`, `format_version`, `merge_history[]` (audit trail of which CSVs contributed which date ranges).
3. Wire into `load_multi_account.sh`: optional `--merge` flag that does the union instead of replace.
4. Test suite:
   - `test_merge_idempotent` — merging the same ingest twice produces identical output
   - `test_merge_appends_new_weeks` — non-overlapping ingests union to full coverage
   - `test_merge_conflict_new_wins` — overlapping date → newer ingest's value
   - `test_merge_preserves_unrelated_strategies` — merging IDM doesn't touch ACWI
5. Update CLAUDE.md + ARCHITECTURE.md with the merge workflow.
6. First production run: parse the next FactSet CSV through the new merge path; this establishes the cumulative file as the authoritative state going forward.

### Open questions for user (still pending from original draft)

- **Q1 — merge-conflict policy.** Default "new-wins" recommended (user just downloaded fresh data). User may want "keep_existing" for audit-trail use cases — confirm.
- **Q2 — date legitimacy.** How often does a date's data legitimately change after first publication? (E.g., Q4-2025 reported in Jan-2026 but a re-run in May-2026 changes the data — is that a real workflow?)
- **Q3 — per-strategy split.** Confirmed via 2026-05 split-file pipeline — answered.
- **Q4 — audit-trail.** Should the cumulative file carry a `merge_history[]` array recording every CSV that contributed which weeks? Recommended yes; ~10 KB overhead.

When user is ready to schedule: open this doc + answer Q1, Q2, Q4. The implementation itself is now ~3-5 hrs of focused work.
