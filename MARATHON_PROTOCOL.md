# Review Marathon — Operating Protocol

**Purpose:** systematic per-tile review of the 24 audited Tier-1 tiles in the polished `design-polish-v1` dashboard. Replaces the ad-hoc back-and-forth with a repeatable process.

---

## Setup (one-time)

1. **Preview server running** at `http://localhost:3099/dashboard_v7.html` (started by advisor; see `.claude/launch.json`)
2. **Chrome window open** to that URL
3. **Drag `~/RR/sample_data.json` onto the Chrome window** to load the new-format data (7 strategies + Raw Factors + security_ref enrichment)
4. **This protocol doc** + `REVIEW_MARATHON_DOSSIER.md` open in another tab/window for reference

---

## Per-tile loop (the systematic part)

For every tile, advisor and user follow this 4-step loop:

### Step 1 — Advisor posts a "Tile Card"

A standardized block with these sections:

```
## Tile #N of 24 — {tileId}
Verdict at audit | Tag | Batch | Commit
DOM location | What tab | Where to scroll
What you're looking at: {1-2 sentences plain English}
Trivials applied at audit: {bullet summary}
PM gate (if any): {plain-English explanation, NOT just B-id jargon}
Specific things to verify in-browser:
  □ {check 1}
  □ {check 2}
  □ {check 3}
Recommendation: OK | OK pending B{X} | hold
```

### Step 2 — User does in-browser verification

User clicks/scrolls to the tile in their Chrome window. Walks the verification checklist. Spends 30–90 seconds per tile. If anything looks broken or wrong, user calls it out before deciding.

### Step 3 — User responds with one of:

| Response | Meaning | What advisor does |
|---|---|---|
| `OK` | Sign off on current state, no PM gate concerns | Tag `tileaudit.{id}.signedoff`, push, move to next |
| `OK pending B{X}` | Sign off on trivials applied; PM gate tracked but not blocking | Tag `tileaudit.{id}.signedoff`, push, log B-id as carried-forward |
| `hold` | Don't sign off — needs work or clarification | Pause, address the issue, re-pose decision after |
| `explain B{X}` | Wants the PM gate explained in more depth before deciding | Advisor expands the explanation; loop back to Step 3 |

### Step 4 — Advisor cuts tag + posts next Tile Card

Tag at current HEAD `1bd1d09` (the polished-dashboard commit). Push immediately. Move to next tile in dossier order.

---

## Plain-English PM-gate explanations

When a tile has a PM gate, advisor MUST explain it in plain English using THIS data, not just point at the B-id. The dossier uses B-ids; the protocol uses prose.

Example pattern:

> **B{X} affects this tile because:** {what's actually wrong} → {what the user sees that's misleading} → {what the fix would be} → {why deferred}.

If the user can't follow the explanation, the gate hasn't been explained well — re-write it.

---

## Decision posture

The default mental model:
- **GREEN tiles:** signed off in batch — user trust earned, no PM gates worth raising.
- **YELLOW tiles:** "OK pending B{X}" is the expected answer for most. The fix is real but cross-tile, decoupled from per-tile correctness.
- **RED tiles:** carefully read the gate. Two RED tiles (`cardUnowned` B80, `cardTEStacked` B96) may genuinely warrant `hold` because the data itself is wrong, not just stylistically deferred.

---

## Marathon close-out (at the end)

When all 24 are decided:

1. Cut milestone tag `tier1-review-signoff` at HEAD.
2. Update `SESSION_STATE.md` checkpoint log with N signed-off / M held tiles.
3. List of remaining PM gates → moved to "Marathon-blocking" section in BACKLOG with priority.
4. `BACKLOG.md` "Shipped" section gets the signed-off entries with date.
5. Then either: B105 Phase 2 polish OR Tier 2 tile builds (B102/B103/B104) per user direction.

---

## Communication discipline

- Advisor uses 11px-uppercase-style "Tile Card" format every time. Predictable rhythm = fast scanning.
- User uses one of the canonical responses (`OK` / `OK pending B{X}` / `hold` / `explain B{X}`). Avoid free-form ambiguity.
- If either side breaks rhythm, the other resets it.
- One tile at a time. No batching unless explicitly noted (GREEN block was the one exception).
