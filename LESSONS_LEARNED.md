# Lessons Learned — RR Data Integrity Crisis (April 2026)

**Drafted:** 2026-04-27 (immediately after B115 stabilization)
**Trigger:** Hours of "wacky number" debugging that traced to silent fabrication and parsing-path drift accumulated over a month.
**Audience:** anyone working on RR — and also anyone building any data-pipeline-backed dashboard.

> User's words at the breaking point: *"this is painful — not sure why so many things look so way off — so many things that we worked so hard to get right!!!!!!!"*

This document exists so that pain isn't repeated.

---

## What actually went wrong

A short story so the lessons land.

### Symptoms (what the user saw)
- Idiosyncratic Risk box showed `60%`, then `-100%`, depending on tab/state
- TE drill card showed `58.82 / 58.74 / 58.19 / 59.21` — looked like TE values, were actually `pct_specific` values
- "Wacky" numbers appeared after a fresh CSV upload, with no recent code change to the parser
- Hard refresh didn't fix it

### Root cause (what was actually happening)
**Four parallel parsing paths in `dashboard_v7.html` had drifted from each other:**

1. `parseFactSetCSV()` — JS-based CSV parser using **hardcoded column positions**. When user dragged the new CSV directly, this fired. Col 15/16 were `total_risk/bm_risk` in the Apr-10 format but `pct_specific/pct_factor` in the Apr-23 format. The JS parser wasn't updated, so it read pct_specific into the TE field. **Silent cross-wire.**
2. `normalizeFactSet()` — for an API-shape FactSet response that never shipped. Auto-detected by a wrapper at L6863. Fired on JSON inputs whose field names happened to overlap the API shape — corrupting values.
3. `normalize()` at L609 — the legitimate path, but contained "smart" fallbacks: when `pct_specific` was null, computed `idioSum/te*100` and presented it as real. When `f.c` was null, computed `|f.a| × f.dev × scale` and presented it as real. When `hist.sum` was empty, fabricated entries by stamping the current week's values onto every date pulled from `hist.fac`.
4. localStorage `rr_*` keys carried stale state from previous sessions — old dates polluted current cs.hist.sum.

The Python parser (`factset_parser.py`) was **correct**. Header-driven. Section-aware. Bulletproof. It produced correct JSON from the CSV every time. But the dashboard had three parallel JS paths trying to do the same parsing job, all stale, all silently wrong, all colliding.

### Why this rotted unnoticed
Each path was added at a different time, for a different reason:
- `parseFactSetCSV` — Mar 25 ship, "v3 in-browser parser" for drag-drop CSV convenience
- `normalizeFactSet` — much earlier, for a never-shipped API integration
- `normalize()` synthesis paths — accreted gradually as "robustness" tweaks
- localStorage `rr_history` — for upload history sidebar

Each was reasonable in isolation. None had a clear ownership boundary. None had integrity assertions. The dashboard treated them as additive layers when they were actually **competing sources of truth** for the same fields.

When the CSV format shifted on Apr 23, the in-browser parser silently broke. No error fired — it just produced wrong numbers that LOOKED real because the rest of the dashboard was designed to fall back to "smart" fabrication when fields were null.

---

## Pattern catalog — what to avoid, what to do instead

### Anti-patterns (what produced this crisis)

#### 1. Silent fabrication
**Pattern:** `let x = source.x ?? compute_x_from_other_fields()`
**Failure mode:** when source.x is null, the computed value LOOKS real, gets rendered as real, gets sanity-checked by humans against expectations, and only catches when the computation goes off-the-rails (-100%) or contradicts a known-good number elsewhere.
**Right way:** show `—` and a tooltip explaining why. If you must compute, **mark the cell visibly** (e.g., `8.3%ᵉ` superscript) and document the derivation chain in a tooltip. Surfacing missing data is more valuable than hiding it.

#### 2. Hardcoded column positions in a header-driven CSV
**Pattern:** `let pct_specific = pf(row[20])` when the CSV section's column-20 meaning depends on the file format version.
**Failure mode:** new CSV version → same code reads different field → cross-wired data, no error.
**Right way:** detect column meaning from the section's header row. If header lacks the anchor, refuse to extract the field rather than guess. (Python parser does this correctly via `schema.between_raw`.)

#### 3. Multiple parsing paths for the same input
**Pattern:** dashboard has both `parseFactSetCSV` (JS) and `factset_parser.py` (Python) — both can produce internal data. Plus `normalizeFactSet` for an API shape, plus `normalize()` for everything else, plus a wrapper that auto-detects which to use.
**Failure mode:** one path gets updated, others lag. Drift goes undetected because all paths populate the same fields. Different inputs follow different code paths and produce different field values.
**Right way:** ONE source of truth. The Python parser. Dashboard is a pure renderer. Other paths get deleted (with safety tag) or stubbed with throw.

#### 4. Recompute in normalize()
**Pattern:** `normalize()` is supposed to rename fields, but contains `if X null compute Y` branches that re-derive values from other fields.
**Failure mode:** parser produces correct value → normalize() overwrites with derived value → dashboard renders the derived value, claiming it's the parser's value.
**Right way:** `normalize()` is rename-only. No transformations. No "smart" fallbacks. If a field is null in source, leave it null in output. (The dashboard's render layer can choose to show `—` or a marked derivation, but the data layer must not lie.)

#### 5. localStorage as a side-channel data source
**Pattern:** localStorage stores user state (flags, preferences) AND data state (history arrays, cache).
**Failure mode:** old data state from a previous session pollutes the current load. User can't trust what they're seeing because some fields come from the file and some from "memory."
**Right way:** localStorage is for user preferences only (toolbar state, flagged tickers, notes). Data state lives in JSON, period. On every page load: aggressive `rr_*` wipe except prefs. Aggressive cache-control headers.

#### 6. No integrity assertion at load
**Pattern:** load JSON → run normalize() → render. No check that "what's rendered" still matches "what was loaded."
**Failure mode:** normalize() drift goes undetected for weeks until a human notices a wacky number.
**Right way:** at load time, run an assertion: every critical field on `cs` must equal the corresponding field in the raw JSON. Console-error on any mismatch, listing field-by-field drift. Caught in seconds instead of weeks.

### Patterns to keep

#### A. Header-driven section parsing (Python parser)
The Python parser inspects each section's local header row, builds a column-name → index map, and extracts by canonical name. When FactSet adds/removes/reorders columns, the parser adapts automatically. This is the only reason RR survived the Apr 23 format shift — the Python parser was robust.

#### B. Per-cell provenance index (`SOURCES.md`)
Every numeric cell on the dashboard has a documented source path (which CSV section, which column, what derivation if any). When user spots a wacky number, they hover the cell or read SOURCES.md and see exactly where it came from. Sanity check is one click instead of an hour of investigation.

#### C. Visible derivation markers
When a value IS computed (legitimately — TE = Σ of holding contributions, etc.), the cell shows `ᵉ` superscript with a tooltip explaining the formula. The user can tell at a glance which numbers are sourced vs derived.

#### D. FactSet-side tracker (`FACTSET_FEEDBACK.md`)
When the CSV is missing fields the dashboard needs, log it as `F#` in the tracker. Never silently work around it via fabrication. The tracker becomes the relay channel to FactSet — clean asks, clear specifications, no surprise.

#### E. Single command: `./load_data.sh path/to/csv`
One canonical path to get from raw CSV to live dashboard. No drag-drop CSV. No browser parsing. No ambiguity.

---

## RR-specific architecture going forward

```
┌──────────────────────────────────────────────────────────┐
│  FactSet emails CSV  →  ~/Downloads/<file>.csv           │
└──────────────────────────────────────────────────────────┘
                          ↓
                          ↓  user runs:
                          ↓  ./load_data.sh "~/Downloads/<file>.csv"
                          ↓
┌──────────────────────────────────────────────────────────┐
│  factset_parser.py — header-driven, header-aware,        │
│  section-aware, deterministic                            │
│  - Single source of truth for parsing logic              │
│  - 1,200+ lines of battle-tested Python                  │
│  - Outputs: ~/RR/sample_data.json (or latest_data.json)  │
└──────────────────────────────────────────────────────────┘
                          ↓
                          ↓  open dashboard_v7.html
                          ↓  (browser fetches latest_data.json
                          ↓   with cache-bust + no-store)
                          ↓
┌──────────────────────────────────────────────────────────┐
│  dashboard_v7.html — pure renderer                       │
│  - normalize() = rename-only, no synthesis               │
│  - Integrity assertion runs on every load                │
│  - parseFactSetCSV() = stub (throws clear error)         │
│  - normalizeFactSet = deleted                            │
│  - localStorage wiped on every page load (prefs only)    │
│  - <meta> cache-control: no-cache, no-store              │
└──────────────────────────────────────────────────────────┘
                          ↓
                          ↓  Tile renderers read cs.X directly
                          ↓
                          ↓  Cells display source data with
                          ↓  ᵉ markers on derived values
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Dashboard — every visible number = sourced from CSV via │
│  Python parser, OR explicitly marked as derived          │
└──────────────────────────────────────────────────────────┘
```

### Rules going forward

1. **CSV in browser = error.** `parseFactSetCSV()` throws. User runs `./load_data.sh`.
2. **`normalize()` is rename-only.** Any new "if X is null, compute Y" patch must instead: (a) leave it null, OR (b) compute it AND add a `_X_synth=true` marker AND add a render-side ᵉ badge AND document in SOURCES.md.
3. **localStorage is for preferences only.** Never cache data. Every page load wipes `rr_*` except `PREFS_KEY`.
4. **Every numeric cell has provenance.** SOURCES.md is updated when render code changes.
5. **Integrity assertion runs on every load.** Catch drift in seconds.
6. **CSV format shift = audit every parser path.** When FactSet changes the CSV, the Python parser adapts (header-driven), but every JS path that touches the same data MUST be re-audited or deleted.

---

## Reference: file map

| File | Purpose | Status |
|---|---|---|
| `factset_parser.py` | Source of truth — CSV → JSON | Active, well-tested |
| `dashboard_v7.html` | Pure renderer over JSON | Active, B115-cleaned |
| `load_data.sh` | One-command pipeline | Active |
| `data/security_ref.json` | Static security → country/currency/industry lookup | Active |
| `SOURCES.md` | Per-cell provenance index | Active, must be kept current |
| `FACTSET_FEEDBACK.md` | CSV-side issues to relay to FactSet | Active, append-only |
| `BACKLOG.md` | Non-trivial work queue | Active |
| `LESSONS_LEARNED.md` | This file | Active |
| `HISTORY_PERSISTENCE.md` | Append-only history architecture proposal (B114) | Backlog |
| `MARATHON_PROTOCOL.md` | Per-tile review protocol | Active |
| `CLAUDE.md` | Project instructions | Active |
| `data-integrity-specialist.md` | Cross-project agent (~/projects/apps/ai-talent-agency/agents/) | NEW — see below |

---

## When to re-read this doc

- Anytime you're about to add a `?? fallback` in normalize() or render code
- Anytime you're tempted to add a second parsing path for "convenience"
- Anytime you see a "wacky number" — first stop, read this, then investigate
- Anytime CSV format changes — re-read the "CSV format shift" rule
- Quarterly review — sanity check that no new fabrication paths have crept in

---

## What went well in the recovery

- Python parser was correct from the start — never had to rebuild it
- Git history was committed often enough to bisect cleanly
- Safety tags before risky edits enabled instant rollback
- Subagent re-audit caught issues main session missed
- User's domain expertise on what "wacky" means caught problems automated tests would have missed

---

**The hope this doc represents:** a "new slate." Not in the sense that everything is perfect — in the sense that the foundation is sound, the failure modes are documented, and future work builds on something verifiable.

---

# Addendum — 2026-04-27 (post-FactSet finalization call)

The previous sections cover the April crisis. The day after that crisis (4/27), three things happened in parallel: a deep marathon-style rebuild of cardSectors and the 4 sibling aggregation tiles; a 3-hour FactSet call to finalize the data-extraction spec; and protective infrastructure to make the next crisis preventable. This addendum captures what was learned during that day so future sessions inherit it.

## Patterns that proved out (keep doing)

### 1. Marathon-style review with concrete questions per tile

cardSectors was reviewed across 4 rounds of focused gut-check questions (5 max per round). User answered with one-character answers ("1 a b") or short fragments because the questions were narrow. Each round produced 3–7 commits of incremental shipping. Total: ~25 commits of cardSectors evolution in a single session, every commit verified in browser before moving on.

The pattern is documented in `MARATHON_PROTOCOL.md` but the execution detail that matters: **never ask more than 5 questions per round**, and **wait for the user's reply before assuming the answer**. The first instinct of "let me preempt by also implementing the obvious next step" produces churn the user has to undo.

### 2. Pattern-replication after one tile lands

cardSectors got the unified Universe + Wtd/Avg pills, the column picker, the per-column filtering, the layered sparkline, the signed TE bar — and then the SAME state structure rolled to cardCountry / cardRegions / cardGroups via a `TILE_REG` registry + generic `setTileFilter` / `applyTileFilters` / `tileFilterIcon` helpers. Back-compat shims (`setSecFilter` → `setTileFilter('sec', …)`) preserved the cardSectors integration while opening the door for siblings.

Lesson: **build the prototype tile-specific, then refactor to a generic registry once the second tile asks for the same thing.** Don't try to design the generic version up-front — the first tile is the spec.

### 3. Anti-fabrication policy held under pressure

When `f.c` (per-factor TE %) was null on most factors, the dashboard previously silently synthesized a value. User banned that mid-session. Instead of panicking, the existing 4 tiles using the synthesized value were marked with `ᵉ` and SOURCES.md was updated, leaving the data visible but flagged. This pattern caught silent corruption AGAIN during this session: the verifier baseline reports `_c_synth=true` count = 7 — surfaced cleanly in the report instead of hidden.

**Rule:** show `—` rather than substitute a plausible-looking number. Failing-to-display is more useful than failing-silently.

### 4. Per-cell provenance in `SOURCES.md` continues to pay back

The discipline of documenting every numeric cell as 🟢 sourced / 🟡 derived / ⚫ empty made the FactSet call agenda writing trivial — every gap was already named with its derivation path. The call deck wrote itself in <2 hours instead of needing investigation.

### 5. Verification harness as the green-light gatekeeper

After the call, the test pull is verified via `verify_factset.py` which runs 22+ checks per strategy and produces a 🟢/🟡/🔴 verdict. The user doesn't have to scan rows of JSON — they get one line. **This pattern (structured pass/fail per ask, single verdict at the bottom) is generally applicable to any "is the new data complete?" question.**

## New protective infrastructure shipped this day

### A. Schema fingerprint on every parse

`verify_factset.py` now writes/compares `~/RR/.schema_fingerprint.json` on every run. If the section anchors or column counts in the source CSV drift from the baseline, the verifier refuses to green-light — the exact prevention for the April crisis where 4 different parser paths silently misinterpreted column 15.

The user must explicitly delete the baseline file to acknowledge a schema change. This is intentional friction.

### B. Auto-run verifier in `load_data.sh`

Every parse now writes the verifier output to `last_verify_report.log`. The dashboard still opens (so the user can browse), but the report is one command away (`cat last_verify_report.log`). Future sessions inherit this — they don't need to know about verify_factset.py to benefit from it.

### C. Identifier flexibility added to A2 check

The verifier expects 16 factor keys in `factor_contr` per holding, but doesn't fail if a strategy has 15 with a specific named missing factor. Partials are surfaced; outright failures are isolated. This was an explicit design choice after observing in the baseline run that ACWI shows 15/16 (missing Currency) — a model-vs-universe issue likely, not a parser bug.

## Anti-patterns that emerged this day (don't repeat)

### 1. Backslash-escape bombs in template literals

`'${(h.t||'').replace(/'/g,'\\\\\\'')}'` parsed wrong. The `\\\\\\''` looked like 6 backslashes then a single-quote, but JS interpreted it as `\\` `\\` `\\` `'` `'` — closing the first string and opening a second. Result: the entire script file failed to parse silently (no console error in the test code).

**Rule:** when injecting a string into an HTML attribute, prefer entity escapes (`&apos;`, `&quot;`) over backslash escapes. The template literal context is its own escape-management problem; HTML's is more uniform.

### 2. CSS variables passed to Plotly's `marker.color`

`rc(rank)` returned `var(--r1)` — Plotly doesn't resolve CSS vars and rendered all dots black. Had to resolve to literal hex via `getComputedStyle` before passing.

**Rule:** Plotly's `marker.color`, `line.color`, and `paper_bgcolor` need literal RGB / hex / rgba — never CSS vars. Resolve up-front.

### 3. Stale subagent roster at session start

After writing `.claude/agents/data-viz.md`, attempting to spawn it via Agent failed because the subagent roster is frozen at session start. This is a known limitation but easy to forget. The work-around was to read the agent definition and execute the framework inline.

**Rule:** when writing a new subagent, plan to spawn it from a fresh session next time. For the current session, execute inline.

### 4. `cs.hist.sec` is empty in current data

The Trend column on the 4 aggregation tiles falls back to a static current-TE indicator because `hist.sec` (per-sector weekly history) is not yet populated by the parser. This is the B6 backlog item. The layered sparkline V2 was designed to handle the fallback gracefully — the lesson is **assume backlog gaps will surface; don't crash**, fall back with a useful degraded rendering.

### 5. The `r` field on holdings has 735/1217 coverage but unknown semantics

This is exactly the "named field, unclear meaning" problem the protective infrastructure exists to prevent. The current sample has it; we don't know if it's `period_return` (Brinson input), some other return measure, or noise. The verifier flags it as "verify what `r` represents." **Action item for the next FactSet conversation:** lock the schema doc.

## Process improvements that compounded

- **Commit per logical change.** 25+ commits in one day; every revert is fine-grained.
- **Verify in browser before committing.** Every Edit was followed by `preview_eval` to confirm the change rendered. Caught the backslash-escape bomb (script wouldn't load) before committing.
- **Status badges on the call deck.** The deck showed ✓/◐/● for each ask so the user could scan resolved vs partial vs open in 5 seconds. Same pattern in the verifier output. **Visual triage scales when the list of asks gets to 30+.**
- **Always-include `data-col` attribute on cells.** Filtering relies on `[data-col=X]` selectors. Adding the attribute on every render helped column-vis AND filtering for free.

## Specific things to check on the next FactSet pull

When the test-pull file lands:
1. Run `./load_data.sh ~/Downloads/<new>.csv` — verifier runs automatically
2. Verdict at bottom: 🟢 / 🟡 / 🔴
3. If 🔴 SCHEMA DRIFT → review drift list before doing anything else
4. If 🟢 → green-light the massive 15+ account run
5. If 🟡 → manual review of partials; user judgment on whether they're blockers

## Patterns to roll out elsewhere when relevant

- The full-screen modal pattern (cardSectors only today) — every tile that's "important enough" probably gets one
- The 4D quadrant scatter pattern — only on cardSectors per user direction; "different tiles may need different visualizations"
- The TILE_REG registry — could expand to include drill-modal config, export config, etc., once a second tile needs the same surface
- The Universe + Wtd/Avg global pills — already global; if other parts of the dashboard need universe-aware rendering, they read from `_aggMode` / `_avgMode` directly
