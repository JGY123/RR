# Gap Discovery Methodology

> **The problem:** The PM keeps noticing that features they remember from pre-crisis (2026-04-16) are missing in the current code. So far, every gap has been found ad-hoc ("wait, the inline map used to have region zoom", "wait, sector ranks used to have a BM-avg toggle"). This is not a sustainable way to reach parity.
>
> **The root cause:** Work done after the `24b4353` baseline but before yesterday's crisis exists **only in JSONL conversation transcripts** (239MB across ~25 files at `~/.claude/projects/-Users-ygoodman-RR/*.jsonl`). Some of those sessions wrote code that never made it to a git commit. Some wrote code that did commit but got rolled back. Either way, the only complete record is the transcripts.
>
> **The fix:** systematically mine every source of pre-crisis state, cross-reference against current code, produce a single reconciled gap list. Once we have that list, gap-fixing becomes a deterministic workstream instead of a scavenger hunt.

---

## Sources to search (in priority order)

### 1. JSONL conversation transcripts
- **Path:** `~/.claude/projects/-Users-ygoodman-RR/*.jsonl` (plus subagent dirs)
- **Size:** ~239MB, ~25 main files, date range ~2026-03-25 → 2026-04-17
- **Format:** one JSON object per line; each line is a user message, assistant message, or tool call/result
- **Target content:**
  - `tool_use` blocks with `tool_name: "Write"` or `"Edit"` targeting `dashboard_v7.html`
  - Function definitions written: `function xxx(...)` bodies
  - UI element additions: `<div id="...">`, `<button onclick="...">`, card titles
  - Decision points where the user approved a feature being built
- **Searching challenge:** each line can be very large (tool outputs). Grep sees them as "[Omitted long matching line]". Need line-level JSON parsing, not naive grep.

### 2. Backup git branches
- `backup-all-today-work` @ `24b4353` — baseline, 4,322 lines
- `backup-today-all-work` @ `24b4353` — identical paired copy
- **What they have:** older baseline. Useful for comparison (diff against current to see what's been added/removed since), but NOT a complete pre-crisis state.

### 3. Pre-crisis doc files (now tracked in e6e33f4)
- `TILE_SPEC.md` — 29-tile inventory with status column
- `DASHBOARD_SPEC.md` — (if present, read it)
- `SCHEMA_COMPARISON.md` — FactSet field reference
- `tile-specs/*-spec.md` — 5 completed design specs including "Before/After" code blocks that describe features
- `CLAUDE.md` — project overview

### 4. User memory
- Slow, imperfect, but produces real signal. Documented reminders should be captured once observed.

### 5. Orphaned untracked files
- `archive/` — unclear contents, peek
- `cli-prompts/` — unclear, peek
- `dashboard_v7_partial.html` — possibly a snapshot worth diffing
- `tile_spec.html` — possibly a prior version of tile inventory

---

## Output: `GAP_INVENTORY.md`

A single file listing every feature / function / UI element ever mentioned in any source, categorized by status:

| Feature / function / ID | Source(s) | Status | Priority | Notes |
|---|---|---|---|---|
| `setMapRegion` on inline map | JSONL session 0306b5a0 line 8423; CLAUDE.md | ✅ present (as of `0c606cd`) | n/a | Verified |
| `spotlightRanksToggle` (W / Avg / BM) | user memory + tile-specs/sector-active-weights-spec.md | ❌ missing | high | Requires per-row BM-weighted avg calc |
| `rHistoricalTrends` mini-charts | CLAUDE.md | ❌ missing | high | TE / AS / Beta / Holdings |
| … | … | … | … | … |

**Status values:**
- ✅ present — exists in current `dashboard_v7.html`
- ❌ missing — mentioned in a source but not in current code
- ⚠️ partial — some elements present, some missing (e.g., function exists but not wired to UI)
- 🤷 unclear — mention ambiguous, needs PM confirmation
- 📦 deferred — explicitly decided not to build (e.g., color-blind mode, Currency tile)

---

## Execution plan

### Phase 1 — Automated JSONL mining (background agent)
Agent runs unattended, produces a raw extract:
- Every `tool_use: Write/Edit` targeting `dashboard_v7.html` with the old_string / new_string content
- Every function name defined in those writes
- Every DOM id / button / card title introduced
- Every time the user approved a build

### Phase 2 — Cross-reference against current code
For each extracted feature, grep current `dashboard_v7.html` to classify as present/missing/partial.

### Phase 3 — Enrich with prior docs
Merge with features mentioned in TILE_SPEC.md, tile-specs/, CLAUDE.md, DASHBOARD_SPEC.md. Some features may not be in JSONL but are in docs.

### Phase 4 — PM review
Produce `GAP_INVENTORY.md`. PM reads it and confirms priorities. The list becomes the authoritative roadmap.

### Phase 5 — Systematic rebuild
Work the gap list top-down by priority. Each gap gets a patch, a tag, and an update to the inventory.

---

## Why not just search the JSONLs with grep?

Tried. The transcripts are structured as `[{"type":"...", "content":[{...}, {...}]}]` with each line being a large JSON object. Grep matches but marks every line as "[Omitted long matching line]" because the surrounding context is hundreds of KB. Plus a single search term (`function`) returns thousands of hits with no way to focus on the meaningful ones.

Need actual JSON line-parsing with filters on `tool_use` blocks. A general-purpose agent with code execution can do this. Shell `jq` could too but the schema is messy.

---

## Sign-off criteria

Gap discovery is "done" when:
- Every source in Section 1–5 has been systematically checked, not just spot-checked
- `GAP_INVENTORY.md` exists with at least 50 entries (my rough estimate based on how many regressions have surfaced so far)
- The PM has reviewed and prioritized
- Every ❌ missing gap has either a ticket or a deferred decision

Without this, we keep finding regressions by accident for weeks, and the dashboard never reaches true parity.
