# Orginize + Agent Ecosystem Review

**Written:** 2026-04-19, end of autonomous overnight session on RR.
**Purpose:** Record findings from looking at ~/orginize/ and ~/projects/apps/ai-talent-agency/ after a long stretch of RR work. Per PM ask: "the link between the app is not the way I want it... the agent roster has been expanded further and it's not there much more should be including a focus on learnable skills that we can implement from one project to another."

---

## What's healthy

### Orginize as a master orchestrator
- 40+ projects registered with canonical paths + GitHub URLs + account assignments
- `~/orginize/knowledge/patterns.md` — code-pattern library (SDK usage, auth flows, etc.) at decent maturity
- `~/orginize/knowledge/development-rules.md`, `cli-prompt-engineering.md`, `gotchas.md`, `agent-routing.md` — foundational docs exist
- `~/orginize/status/project-status.md` — auto-updates commit state across all projects (scan-projects.sh)
- `~/orginize/dna/` — per-project JSON profiles (not yet fully populated but scaffold present)
- `~/orginize/app/` — Next.js dashboard app exists; unclear current state

### Agent roster at `~/projects/apps/ai-talent-agency/agents/`
Confirmed 24 existing agents (alphabetical):
```
agent-of-agents, agent-ops-manager, agent-social-protocol,
ai-coach-architect, analytics-engineer, connector, data-transformer,
deep-thinker, design-director, desktop-app-dev, devops-orchestrator,
factset-parser-engineer, full-stack-builder, gamification-specialist,
inquisitor, knowledge-curator, landing-page-designer, marketing-guerrilla,
mobile-app-developer, qa-agent, risk-reports-specialist, storyteller,
tile-design-agent, training-agent
```

Breadth is good. Coverage ranges across dev, design, content, ops.

---

## What's missing (per PM observation)

### 1. Methodology patterns weren't captured as transferable skills
Everything in `patterns.md` is code-snippet-level (paste this SDK init, use this auth pattern). Missing: **methodological patterns** (how to run a multi-session project, how to recover lost work, how to do an audit).

**Fix shipped this session:** new directory `~/orginize/knowledge/skills/` with 6 skill files:
- `jsonl-gap-discovery.md` — recovering lost features from session transcripts
- `tile-audit-framework.md` — three-track per-component audits
- `theme-aware-helper.md` — CSS-var + runtime-resolver pattern for chart libs
- `regression-checkpoint.md` — tag-and-push discipline for multi-session work
- `session-continuity.md` — SESSION_STATE + TRANSITION_PROMPT artifacts
- `single-file-app.md` — when/how to ship single-HTML-file internal tools

### 2. Agents focused on executing code, not running process
Existing agents skew toward "build X" (full-stack-builder, mobile-app-developer) or "design X" (design-director, landing-page-designer). Thin on "orchestrate process across sessions."

**Fix shipped this session:** 3 new agent profiles at `~/projects/apps/ai-talent-agency/agents/`:
- `gap-discovery-specialist.md` — runs JSONL mining + gap reconciliation
- `session-continuity-specialist.md` — maintains SESSION_STATE / TRANSITION_PROMPT / specialist agent files
- `tile-audit-specialist.md` — runs formal component audits

Each has: identity, why-it-exists, how-it-works, spawn template, proven output, collaboration notes. Format matches existing `tile-design-agent.md`.

### 3. "Link between apps" (PM ask — ambiguous, needs follow-up)
Possible interpretations:
- **Shared-library / design-system integration** across projects — no evidence yet of a shared UI-kit or component library
- **Data interop** — is there a pattern for projects to read each other's state? (e.g., RR's `GAP_INVENTORY.md` being visible to other sessions)
- **Orginize dashboard app not reflecting all projects properly** — `~/orginize/app/` is a Next.js app, state unclear

Worth a 30-minute directed conversation with PM to pin down which of these is the concern. Shipping fixes without that clarity risks building wrong thing.

---

## Proposed next moves (deferred decisions — need PM input)

### Priority A — Fill `~/orginize/dna/` with project profiles
Every project has a scaffolded `{slug}.json` expected. Most likely empty. A one-liner Python script scanning each project's CLAUDE.md + package.json could auto-populate basic fields (name, stack, status, GH URL, key files). Then Orginize app has real data to render.

### Priority B — Run one of the 3 new agents end-to-end to validate
Spawn the tile-audit-specialist on RR's `cardSectors` as first real use. Confirm it produces a quality audit doc. Iterate the agent profile based on first-run learnings.

### Priority C — Cross-project gotcha propagation
When a gotcha is discovered on project X (example: RR's "numeric ticker string triggers Plotly category-axis bug"), it should auto-surface to other projects using the same libraries. Current `gotchas.md` is manually maintained. An agent could watch for new patch commits with "fix:" prefix and suggest gotchas-file entries.

### Priority D — Skills library second-pass
The 6 skills shipped today are the low-hanging fruit from RR. More to come as we do similar multi-session work elsewhere:
- "Debug-when-AI-reports-false-success" — broader version of the write-verification pattern
- "Multi-CLI parallelization" — one-CLI-per-tile rule, CoS serialization
- "Data-schema-versioning in localStorage" — the `rr_*_v1` pattern
- "PM/user preference observation" — when to codify a preference vs ask again

### Priority E — Agent-to-skill linking
Each agent's "See Also" currently links to a skill file. Could be bidirectional: each skill file should list which agents implement it. Small curation task, pays off.

---

## What actually shipped this session (cross-project)

| File | Repo | Status |
|---|---|---|
| `~/orginize/knowledge/skills/README.md` | orginize | ✅ committed local |
| `~/orginize/knowledge/skills/jsonl-gap-discovery.md` | orginize | ✅ |
| `~/orginize/knowledge/skills/tile-audit-framework.md` | orginize | ✅ |
| `~/orginize/knowledge/skills/theme-aware-helper.md` | orginize | ✅ |
| `~/orginize/knowledge/skills/regression-checkpoint.md` | orginize | ✅ |
| `~/orginize/knowledge/skills/session-continuity.md` | orginize | ✅ |
| `~/orginize/knowledge/skills/single-file-app.md` | orginize | ✅ |
| `~/orginize/knowledge/patterns.md` (pointer added) | orginize | ✅ |
| `~/projects/apps/ai-talent-agency/agents/gap-discovery-specialist.md` | agency | ✅ committed local |
| `~/projects/apps/ai-talent-agency/agents/session-continuity-specialist.md` | agency | ✅ |
| `~/projects/apps/ai-talent-agency/agents/tile-audit-specialist.md` | agency | ✅ |

**Note:** Orginize has no remote configured, so commits are local-only (by design, per its repo setup). Agency push failed with `Repository not found` — either the remote needs to be re-created on GitHub or auth switched to the correct account. Commit is local and pushes cleanly once remote is sorted.

---

## Big-picture observation

The PM is building a knowledge-worker multiplier — 40+ projects, dozens of agents, multiple Claude sessions in parallel. The bottleneck is no longer writing code (Claude writes plenty). The bottleneck is **coordination, recovery, transferring learning between projects, not losing state across sessions.** Every skill shipped today addresses that layer.

The operational move is to keep running at this altitude: for every hard problem solved in one project, ask "what's the transferable pattern?" Codify in `skills/` or agents. Next project saves the cost.
