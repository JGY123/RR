# RR Subagent Runbook

**Updated:** 2026-05-01
**Purpose:** when to spawn which subagent, how to brief them, how to handle their output. Single source of truth so subagent work stays organized session-to-session.

---

## The triage rule

Before spawning ANY subagent, ask:
1. **Can I answer this in <5 tool calls myself?** → don't spawn. Just do it.
2. **Does this task touch numbers I'm not sure about?** → spawn `data-integrity` first.
3. **Is this a per-tile review?** → spawn `tile-audit`.
4. **Do I need to find something across the codebase?** → spawn `Explore`.

A subagent costs ~30s of latency + ~50K tokens. Use them for work that genuinely benefits from focused, isolated investigation. Don't use them for one-line lookups.

---

## Roster

### `tile-audit` — Tile-level review with structured output

**Spawn when:**
- User says "audit cardX" / "verify cardX matches the spec" / "check if cardX is consistent"
- Doing a planned per-tile sweep (Tier-1 marathon, Tier-2 audit cadence)
- Before signing off a tile change

**Brief with:**
- Specific tile id (`cardSectors`, `cardCountry`, etc.)
- The three tracks: data accuracy / functionality parity / design consistency
- Reference to `tile-specs/{id}-audit.md` if a prior audit exists

**Output:** `tile-specs/{id}-audit.md` with sections per track + numbered findings + proposed fixes.

**Coordinator action after receipt:** read the doc, decide which findings to act on, edit the dashboard yourself (subagent is read-only on `dashboard_v7.html`).

---

### `data-integrity` — Audit for fabrication, drift, silent corruption

**Spawn when:**
- User reports "wacky number" / "this value looks wrong" / "I can't tell where this number comes from"
- Before any release that touches data parsing/normalization/rendering
- After a CSV format change ships
- As periodic sanity sweep on long-running data work

**Brief with:**
- Specific symptom (which strategy, which tile, which cell, what user expected vs what showed)
- File paths to inspect (parser, normalize, render fn for that tile)
- Reference to `LESSONS_LEARNED.md` (April 2026 crisis catalog)

**Output:** GREEN/YELLOW/RED audit report with numbered findings + concrete code-level fixes.

**Coordinator action:** edit code yourself. Subagent is read-only on production code. Findings tagged RED block release; YELLOW need a triage call; GREEN are clean.

---

### `data-viz` — Design / audit a sophisticated visualization

**Spawn when:**
- User says "this chart is too simple" / "make this chart more useful" / "design a viz for X"
- Building a new tile from scratch
- Major redesign of an existing chart

**Brief with:**
- Tile id (existing or proposed `cardX`)
- The PM-question the viz should answer ("which factors moved most this week?")
- Existing viz inventory: cardSectors / cardCountry / cardFacRisk / cardFacButt / cardTreemap / etc.

**Output:** `viz-specs/{chart-id}-spec.md` with chart options A/B/C, recommended pick, mock-up references.

**Coordinator action:** read spec, build the chart yourself in `dashboard_v7.html`.

---

### `Explore` — Fast codebase question

**Spawn when:**
- "How does feature X work in this codebase?"
- "Where is the renderer for cardY?"
- "Find all files that touch CMAP"

**Brief with:**
- Specific question
- Thoroughness level: quick / medium / very thorough
- Files to skip if irrelevant

**Output:** inline answer. Use it as research input, not as code to ship.

---

### `feature-reconciliation` — "What features do we actually have?"

**Spawn when:**
- "What features do we actually have?"
- "Reconcile code vs docs"
- Quarterly feature review
- Multiple sources disagree (code vs docs vs git history vs JSONL transcripts)

**Brief with:**
- Time window to reconcile
- Sources to cross-check (code, git history, JSONL transcripts, docs)

**Output:** `FEATURE_RECONCILIATION.md` with a feature × source × status table.

---

### `gap-discovery` — Recover features lost before commit

**Spawn when:**
- "Where did feature X go?" / "What did we lose?"
- After a crisis where uncommitted work was wiped
- After 1+ month of work where feature memory has drifted from reality

**Brief with:**
- Suspect feature names
- Time window to mine
- Specific JSONL transcripts at `~/.claude/projects/<encoded-cwd>/`

**Output:** `GAP_INVENTORY.md` with a feature × source × status table.

---

### `thread-archiver` — Save a conversation for future search

**Spawn when:**
- User says "archive this thread / session"
- Wrapping up a long session worth referencing later
- Need a searchable record of decisions made

**Brief with:**
- Session JSONL transcript path or a pasted summary
- Session topics / decisions / files touched

**Output:** markdown file in `~/orginize/archive/session-logs/` indexable by `search_knowledge`.

---

### `feature-dev:code-architect` — Design a feature blueprint

**Spawn when:**
- Designing a non-trivial new feature that needs a comprehensive plan
- "Build me a blueprint for adding X"

**Brief with:**
- Feature description
- Existing patterns to follow

**Output:** comprehensive implementation blueprint with files to create/modify, component designs, data flows, build sequences.

---

### `feature-dev:code-explorer` — Deep-dive existing feature

**Spawn when:**
- "How does X actually work?"
- Need to understand a complex existing feature before extending it

**Brief with:**
- Feature in question
- Specific subsystems to trace

**Output:** documented architecture map + execution paths + dependencies.

---

### `feature-dev:code-reviewer` — Independent review

**Spawn when:**
- Want a second opinion on a tricky migration
- Pre-release code review

**Brief with:**
- File paths + commit hash to review
- Specific concern to verify

**Output:** code review with confidence-tagged findings (only high-priority issues reported).

---

## Briefing template

When spawning ANY subagent, use this template:

```
TASK: <one-line goal>

CONTEXT:
- Project: RR (Redwood Risk Control Panel) at ~/RR/
- Symptom (if bug): <user complaint, exact words>
- File paths to inspect: <list>
- Expected vs actual: <if numeric>

CONSTRAINTS:
- Read-only on dashboard_v7.html (coordinator serializes edits)
- Anti-fabrication policy: see LESSONS_LEARNED.md
- Output format: <markdown / report / inline answer>

DELIVERABLE:
- File path or inline answer
- Length cap: <under N lines>
```

This format keeps the subagent focused. Without it, subagents over-investigate or under-deliver.

---

## What subagents must NOT do

- Edit `dashboard_v7.html` (single-file dashboard — coordinator serializes all edits)
- Edit `factset_parser.py` without explicit go-ahead
- Run `git push` (only the coordinator pushes)
- Make commits without an explicit instruction in the brief
- Rewrite `latest_data.json` (data layer is sacred)
- Touch FactSet source CSVs in `~/Downloads/`

If a subagent wants to do any of the above, it should report in its output what it would have changed, and the coordinator decides.

---

## Frozen-roster note (from MEMORY.md)

> Subagent roster is frozen at session start. Newly-scaffolded subagents are NOT spawnable until a fresh session. Fall back to reading the agent definition + executing inline.

Practical implication: if you create a new subagent file mid-session, you can't spawn it. Use the existing roster, OR write inline code that does what the new agent would do, then formalize the agent for the next session.

---

## When in doubt

Default agent for unknown work: `Explore` for read-only research, `tile-audit` for tile work, `data-integrity` for numeric anomalies. Don't spawn for one-line lookups — just use Read / Grep / Bash directly.
