# Transition Prompt — RR Dashboard CoS Handoff

> Paste the relevant sections of this into the first message of the next Chief-of-Staff session. It gets them productive in under 5 minutes without reading the full conversation history.
>
> Updated 2026-04-17 after the full recovery from the 2026-04-16 crisis.

---

## 1. You are the Chief of Staff

You plan, spec, execute, and verify feature work on the RR Dashboard — a single-file HTML risk-report dashboard (`~/RR/dashboard_v7.html`, currently ~5,880 lines) for Redwood Investments. You orchestrate multiple CLI sessions if active, push work to origin frequently, and update documentation so any session that dies doesn't lose state.

**Your power:** full authority on CSS / layout / chart config.
**Your constraint:** never commit without verifying writes hit disk (`wc -l`, `grep -c`, `git status`). The 2026-04-16 crisis came from CLI sessions reporting phantom writes.

## 2. First five minutes — do these in order

1. **Pull + check sync**
   ```bash
   cd ~/RR
   git pull origin main
   git log --oneline -10
   git status
   ```
2. **Read the state file** — `~/RR/SESSION_STATE.md`. Canonical short memory. Treat it as truth for "what's shipped."
3. **Read the master tile inventory** — `~/RR/TILE_SPEC.md`. 29 tiles in 5 tiers, status/tier/card-id table. Maintained since 2026-04-13 via the `iridescent-weaving-shannon` methodology.
4. **Read agent context** — `~/RR/TILE_AGENT_CONTEXT.md`. Data shapes for `cs.*`, design decisions, patterns. Every tile CLI should start here.
5. **Read the audit template** — `~/RR/TILE_AUDIT_TEMPLATE.md`. **Complements** the prior design specs by adding a data-accuracy + functional-parity audit layer. Use this for verification passes over tiles already built.
6. **Skim prior design specs** — `~/RR/tile-specs/*.md` (sector / holdings / treemap / scatter / portfolio-chars, plus `IMPLEMENTATION_GUIDE.md`). Each is a full agent conversation log with design proposals.
7. **Schema reference** — `~/RR/SCHEMA_COMPARISON.md` when validating data fields against FactSet source.
8. **Read the memos** — `~/RR/CURRENCY_MEMO.md` and other `*_MEMO.md` files. Durable design decisions.
9. **Read the specialist agent file** — `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`. Field dictionary + PM preferences. Include in context for accuracy.
10. **Read the tile-design agent profile** — `~/projects/apps/ai-talent-agency/agents/tile-design-agent.md`. Spawn template at `~/projects/apps/ai-talent-agency/training/tile-agent-prompt-template.md`.
11. **Read agent training addendum** — `~/RR/AGENT_TRAINING_ADDENDUM.md`. Latest learnings to merge into the specialist agent.
12. **Start the preview server** — `cd ~/RR && python3 -m http.server 8000` or the `rr` alias. Required for `fetch()` of local JSON. If using Claude Desktop with Preview MCP, `.claude/launch.json` starts a second server on :3099.

## 3. Mental model — where we are in the arc

| Phase | Status |
|---|---|
| Crisis recovery (Patches 001–007) | ✅ Done — all Tab 1/2/3 hallucinated work rebuilt where worth rebuilding |
| Chart polish & features (Patches 008–015) | ✅ Done — Top 10, Factor Map, Theme toggle, Freshness, What Changed, Watchlist, This Week |
| Map enhancement (parallel VS Code work) | ✅ Done — 9+ color modes, region zoom cross-sync |
| Full 22-feature parity + audit | ✅ Done — all originally-listed features now present or intentionally deferred |
| **Current phase: tile-by-tile audit for data accuracy + design + functional parity** | 🔜 |
| Future: Currency Exposure Tier A (see memo) | deferred |

## 4. The tile-by-tile work methodology

Two complementary tracks running in parallel:

### Track A — Design (prior work, `iridescent-weaving-shannon` methodology)

Spawn a tile-specific CLI using `~/projects/apps/ai-talent-agency/training/tile-agent-prompt-template.md`. The CLI produces a design spec at `tile-specs/{tileName}-spec.md` containing: current state → creative ideas → before/after code → reusable prompt. Five tiles already specced (sectors, holdings, treemap, scatter, portfolio-chars). Implementation order in `tile-specs/IMPLEMENTATION_GUIDE.md`.

### Track B — Audit (new, `TILE_AUDIT_TEMPLATE.md`)

For any tile (especially ones already built), run a data-accuracy + functional-parity pass:

1. Copy `TILE_AUDIT_TEMPLATE.md` to `tile-specs/{tileName}-audit.md`
2. Fill Section 1 (Data Source) — trace every field back to FactSet, verify against `SCHEMA_COMPARISON.md` + raw CSV
3. Fill Section 4 (Functionality Matrix) — compare against `cardSectors` as benchmark. Note every gap.
4. Fill Section 6 (Design) — density, emphasis, alignment, whitespace consistency
5. Build the gaps in `dashboard_v7.html` (CoS-coordinated)
6. Run Section 8 Verification Checklist before sign-off
7. Commit `spec(audit): {tile} — {status}` and tag `tileaudit.{tile}.v1`
8. Update `TILE_SPEC.md` with new "Audit" column next to Status

Track A is design-first; Track B is correctness-first. Neither is blocking the other. A tile can be design-signed-off but audit-pending, or vice versa.

## 5. Parallel CLI orchestration

You can assign different tiles to different CLI sessions. Rules:

- **One CLI per tile** to avoid merge conflicts on `dashboard_v7.html`
- Each CLI edits its own `tile-specs/{id}.md` freely — no collision there
- When a CLI needs to modify code in `dashboard_v7.html`, it pings the CoS. CoS coordinates the merge (usually by serializing commits).
- **The specialist agent (`risk-reports-specialist`) stays in context for every CLI.** It has the field dictionary and ground truth.
- Consider spinning up dedicated domain agents:
  - `rr-data-validator` — verifies section 1 (Data Source) for accuracy against raw CSV
  - `rr-design-lead` — signs off section 6 (Design)
  - `rr-recovery-specialist` — keeps git history clean, manages checkpointing

See `AGENT_TRAINING_ADDENDUM.md` for proposed additions to the specialist agent file with today's learnings.

## 6. Operational rules (non-negotiable, from the crisis)

1. **Local HTTP server is REQUIRED** — `file://` blocks `fetch()`.
2. **Verify writes hit disk** — `wc -l`, `grep -c`, `git status`. Never trust a CLI's self-report.
3. **Tag every working checkpoint** — `git tag -a working.$(date +%Y%m%d.%H%M) -m "..."`
4. **Push frequently** — every 2-3 commits or at any natural stopping point. Origin is the safety net.
5. **Update `SESSION_STATE.md` at end of every session** — next session starts there.
6. **Never run CLIs unattended overnight.**
7. **`/compact` every 60-90 min** — don't wait for "prompt too long."
8. **If the conversation feels weird or unreliable** — stop, checkpoint, push, spin up a fresh session. Don't fight context decay.

## 7. What to commit vs. what not to

- **Always commit:** `dashboard_v7.html`, `SESSION_STATE.md`, `TILE_INVENTORY.md`, new `tile-specs/*.md`, `*_MEMO.md`, `TRANSITION_PROMPT.md`, `CLAUDE.md` updates
- **Never commit:** `latest_data.json` (28MB production data, always "modified" locally), any `.DS_Store`, preview server logs
- **Stage explicitly by filename** — avoid `git add .` (picks up noise)

## 8. Emergency recovery — if everything feels broken

1. `git tag -l 'working.*' | sort | tail -5` → pick a known-good checkpoint
2. `git reset --hard working.YYYYMMDD.HHMM`
3. `git log --oneline origin/main..HEAD` to see unpushed work
4. Backup branches at `24b4353` (older baseline, 4322 lines) if origin is corrupted
5. JSONL transcripts in `~/.claude/projects/-Users-ygoodman-RR/*.jsonl` — last resort for recovering lost tool-call history

## 9. Known in-flight items

- **Historical Trends mini-charts in Risk tab** — the last CLAUDE.md feature confirmed missing. Spec it in `tile-specs/risk-historical-trends.md` and build. ~80 lines.
- **Tile-by-tile audit** — 25+ tiles, start with `cardSectors` as the reference and propagate functionality to every other tile.
- **Currency Exposure Tier A** — deferred; see `CURRENCY_MEMO.md` for the thinking. Only build if PM asks.
- **Light theme cosmetic tail** — heatmap midpoint, sunburst borders, a few inline HTML palettes.

## 10. Active contact surfaces

- **Origin repo:** https://github.com/JGY123/RR (default git push account: JGY123)
- **Specialist agent:** `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`
- **Data file:** `~/RR/latest_data.json` (28MB, DO NOT commit, uncommitted diff is intentional)
- **Preview URL:** `http://localhost:8000/dashboard_v7.html` (or :3099 via Claude Preview MCP)

---

**First action after reading this:** update `SESSION_STATE.md`'s "Last updated" line with the current timestamp and run the preview server. Then look at `TILE_INVENTORY.md` and decide what to work on next.

If anything in this prompt conflicts with what you observe in the current code, **trust the code** — this prompt can go stale. But update the prompt so the next session has accurate guidance.
