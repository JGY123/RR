# RR Session Guide — open every new session with this

**Purpose:** consistent, organized start to every RR development session. ~5 minutes to align on state before doing any work.

---

## 1. Verify the working state (30 sec)

```bash
cd ~/RR
git log --oneline -5                    # last 5 commits — recognize the latest tag
git tag --list 'refactor.*' | tail -5   # most recent refactor checkpoints
git tag --list 'presentation*' | tail -5  # most recent presentation tags
git status -sb                           # uncommitted changes + remote sync state
./smoke_test.sh --quick                  # ~2 sec — confirms parse + lint clean
```

Expected outcome: smoke test green, working tree clean, **`## main...origin/main`** (in sync).

If smoke test is RED → STOP. Read the failure, fix or roll back to last green tag before continuing.

**If `## main...origin/main [ahead N]` shows N > 5** → push first before doing other work:
```bash
git push origin main && git push origin --tags
```
This catches the recovery-risk drift the daily scan flags. Push discipline is part of the workflow, not optional.

## 2. Read the state docs (2 min)

In this order:

1. `REFACTOR_PLAN.md` — what phases shipped, what's next, what's blocked on user direction
2. `SESSION_STATE.md` — the live "where are we right now" pointer
3. `BACKLOG.md` — open backlog items (B1xx series)
4. `FACTSET_FEEDBACK.md` — F-items the parser team is waiting on

## 3. Understand the user's ask (1 min)

Apply the **triage rule**:

- **Hot bug** ("X is showing wrong number") → start with `data-integrity` subagent. Don't write code first. Audit, then fix.
- **Tile-level work** ("audit cardX", "fix cardX") → spawn `tile-audit` subagent. Reads the tile, produces a structured audit doc. Coordinator (you) serializes the actual edits.
- **Architectural** ("make features flow everywhere", "consolidate") → REFACTOR_PLAN.md is the source of truth. Add a new phase if the work doesn't fit existing phases.
- **Quick patch** (tooltip, label, color) → just patch + smoke test + commit + tag with `working.YYYYMMDD.HHMM.<short-name>`.

## 4. Start serving the dashboard (10 sec)

```bash
# In a background terminal:
python3 -m http.server 8765 &
open http://localhost:8765/dashboard_v7.html

# OR for the project-state view:
open http://localhost:8765/dev_dashboard.html
```

Safari hard-refresh: `Cmd + Option + R`. Chrome: `Cmd + Shift + R`.

## 5. Pre-flight before risky edits

Anything touching the parser, render code, or the single-file dashboard >100 lines:

```bash
# 1. Tag a safety checkpoint
git tag working.$(date +%Y%m%d.%H%M).pre-<feature>

# 2. Run full smoke test (not --quick)
./smoke_test.sh

# 3. Run the week-flow lint
python3 lint_week_flow.py --strict
```

## 6. End-of-session ritual (5 min) — **MANDATORY**

When wrapping up:

1. **Update REFACTOR_PLAN.md checkpoint log** with the phase + tag + outcome
2. **Update SESSION_STATE.md** with the next-session pointer
3. **Tag the working state**: `git tag working.$(date +%Y%m%d.%H%M).<descriptor>`
4. **Verify the tag list looks clean**: `git tag --list 'working.*' | tail -10`
5. If anything was blocked on user direction, add a clear note to REFACTOR_PLAN.md "Awaiting" section
6. **Pre-push smoke test**: `./smoke_test.sh && python3 lint_week_flow.py --strict`
7. **Push to origin/main + tags** — recovery-risk discipline:
   ```bash
   git push origin main
   git push origin --tags
   git status -sb        # confirms ## main...origin/main (no [ahead N])
   ```

**Why mandatory:** if disk fails between this session and the next, only what's on `origin/main` survives. Local tags + commits do not. The daily scan flags drift, but the operator (you / me) should never let drift accumulate to begin with. **A session is not complete until `git status -sb` shows clean against origin.**

**Push at intra-session checkpoints too**: anytime you've shipped a phase + tag and the smoke test is green, push. Cost: ~3 seconds. Benefit: shorter recovery window if anything goes wrong.

---

## Quick references

### When something looks wrong with a number
- Open the user's PA reference + the dashboard side-by-side
- Pick a SPECIFIC strategy (EM is best — full source available locally)
- Pick a SPECIFIC week (April 30 latest, April 17 known good historical)
- Pick a SPECIFIC tile + cell
- Check `lint_week_flow.py --strict` — does the renderer go through `_wSec()` / `_wFactors()` / `getSelectedWeekSum()`?
- If the value comes from `cs.X` directly in a render context, that's the bug.

### When the parser produced unexpected output
- Check `parse_stats.jagged_section_bump` in `latest_data.json` — confirms jagged-CSV fix engaged
- Run `python3 verify_factset.py latest_data.json` — checks 22+ pass/fail criteria
- Check `.schema_fingerprint.json` — has the format changed silently?

### When the dashboard fails to load data
- Are you using `file://` (Safari blocks fetch) or `http://localhost:8765/`? Use the latter.
- Is `data/strategies/index.json` present? If not, run `python3 split_for_demo.py`.

### When a subagent is needed
- See `AGENTS.md` for the full roster
- Default for tile reviews: `tile-audit`
- Default for "where did this number come from": `data-integrity`
- Default for codebase questions: `Explore`

---

## Hard rules (carried forward from CLAUDE.md)

1. **CSV in browser = error.** `parseFactSetCSV()` throws. Single Python parser is authoritative.
2. **`normalize()` is rename-only.** No new "if X is null compute Y" without a `_X_synth=true` marker + ᵉ render badge + SOURCES.md update.
3. **localStorage is for preferences only.** Never cache data.
4. **Every numeric cell has provenance.** SOURCES.md is the index.
5. **Integrity assertion runs on every load.** `_b115AssertIntegrity()` catches drift.
6. **CSV format shift = audit every parser path.** Header-driven parser adapts; ALL JS paths get re-audited.
7. **Verify writes hit disk.** After every Edit/Write, run `wc -l` + `grep -c` + `git status`.
8. **Tag before risky edits.** `working.YYYYMMDD.HHMM.pre-X` safety tags.
9. **Never `git add .`** — stage by filename only.
10. **No PNG buttons** on RR tiles (user has removed them multiple times). CSV is fine.

---

**This guide is intentionally short.** If it grows past 200 lines, extract sub-sections to dedicated docs and link.
