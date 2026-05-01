# RR Documentation Index

**Updated:** 2026-05-01 (post-presentation refactor sweep)
**Purpose:** Single navigator for all RR documentation. Anything not listed here is in `docs/archive/`.

---

## 🎯 Start here (any new session)

| File | What it is |
|---|---|
| `CLAUDE.md` | Project instructions (cwd-rooted; Claude Code reads this on every session) |
| `SESSION_GUIDE.md` | **NEW 2026-05-01.** Operational checklist for the first 5 minutes of any new RR session — what to read, what to verify, what to commit. |
| `SESSION_STATE.md` | Live "where are we right now" file. Updated at every checkpoint. |
| `REFACTOR_PLAN.md` | **NEW 2026-05-01.** Active refactor — 11 phases (A–K), checkpoint log, ground rules. Read before any architectural change. |
| `BACKLOG.md` | Append-only feature/work queue. 22 active items, structured by ID. |
| `CHANGELOG.md` | High-level user-visible changes (per release tag) |
| `dev_dashboard.html` | **NEW 2026-05-01.** Visual project state — open `python3 -m http.server 8765` then `http://localhost:8765/dev_dashboard.html` |

---

## 📖 Strategic & planning docs

| File | When to open it |
|---|---|
| `STRATEGIC_RECOMMENDATIONS_2026-04-30.md` | The "long hard look" — Tier 1 strategic shifts (S1/S2/S3), Tier 2 shippable wins, Tier 3 housekeeping. Picked picks from this drove the post-2026-04-30 work. |
| `MIGRATION_PLAN.md` | Path A (local Mac) vs Path B (workstation) migration runbook. |
| `HISTORY_PERSISTENCE.md` | Append-only history architecture (B114 backlog). |
| `MARATHON_PROTOCOL.md` | Per-tile review protocol with data-first ordering. |
| `NEW_TILE_CANDIDATES.md` | 10 ranked new-tile candidates, prioritized by PM impact ÷ cost. |

---

## 🛡️ Data integrity & sources

| File | When to open it |
|---|---|
| `LESSONS_LEARNED.md` | The April 2026 data-integrity crisis story + the 8 anti-patterns + the 8 right ways. **Read before touching the parser or render code.** |
| `SOURCES.md` | Per-cell provenance index. Update when render code changes. |
| `DATA_SPOT_CHECK_2026-04-30.md` | Most recent data-integrity audit — 5 derived-value classes, FactSet vs dashboard math comparison. |
| `FACTSET_FEEDBACK.md` | Open issues to relay to FactSet (F1–F17). |
| `UNIVERSE_AUDIT.md` | **NEW 2026-05-01.** "Both" pill audit — no double-counting bug, 5 UX options for relabeling. |
| `lint_week_flow.py` | **NEW 2026-05-01.** Static lint catches direct `cs.X` access in render functions. Runs in smoke_test.sh. |

---

## 💬 Inquisitor (decision queue)

| File | When to open it |
|---|---|
| `INQUISITOR_QUEUE_R2_2026-04-30.md` | Round 2 questions (30 items) — most have safe defaults, marked "everything can ship" by user 2026-04-30. |
| `INQUISITOR_DECISIONS_2026-04-30.md` | Round 1 answers + decisions logged. |

---

## 🎨 Design & viz

| File | When to open it |
|---|---|
| `TABLEAU_AND_MOCKUP_NOTES.md` | Tableau policy (sketchbook only) + the `viz-specs/{tile}-mockup.html` mechanism for previewing new tiles. |
| `viz-specs/cardWeekOverWeek-mockup.html` | Worked example — three Option-A/B/C candidate designs side-by-side. |
| `viz-specs/cardCalendarHeatmap-spec.md` | Spec preserved after cardCalHeat removal — pattern reusable for cyclic time-series tiles. |
| `viz-specs/cardSectors-spec.md` | Sector spec. |
| `viz-specs/cardCountry-chart-spec.md` | Country chart spec. |

---

## 🧩 Tile-specs (audits + design specs)

`tile-specs/` contains a per-tile audit doc for every Tier-1 + Tier-2 tile audited so far. Most recent:

- `tile-specs/TAB_QUALITY_AUDIT_2026-04-30.md` — Risk + Holdings vs Exposures gold-standard comparison.
- `tile-specs/cardChars-audit.md`, `cardCountry-audit.md`, `cardGroups-audit.md`, `cardMCR-audit.md`, `cardScatter-audit.md` — current audits.
- Older dated audits (`cardX-audit-2026-04-XX.md`) preserved for history.

---

## 🛠️ Operational / FactSet-side

| File | When to open it |
|---|---|
| `UPCOMING_FORMAT_CHANGE.md` | Active CSV format change notes (parser updates pending). |
| `FACTSET_FEEDBACK.md` | F-items list (CSV format issues to ask FactSet). |

---

## 📦 Archived (`docs/archive/`)

37 stale handoffs, deprecated specs, old FactSet emails, and superseded planning docs. Move there:
- `CONTINUATION_PROMPT.md`, `SESSION_CONTEXT.md`, `TILE_AGENT_CONTEXT.md` (early-April session bootstraps — superseded by current SESSION_STATE.md flow)
- `HANDOFF.md`, `HANDOFF_TO_EXECUTOR.md`, `HANDOFF_B105_EXECUTOR.md`, `LIEUTENANT_BRIEF.md` (executor handoffs no longer needed)
- `INTEGRATION_BRIEF.md`, `AGENT_TRAINING_ADDENDUM.md`, `TRANSITION_PROMPT.md` (mid-April plan documents superseded by FORWARD_PLAN → STRATEGIC_RECOMMENDATIONS)
- `FACTSET_CALL_NOTES.md`, `FACTSET_CALL_PREP.md`, `B102_QUESTIONS.md`, `factset_*` (5 emails — point-in-time correspondence; FACTSET_FEEDBACK.md is the live tracker)
- `DASHBOARD_SPEC.md`, `new_format_spec.md`, `CSV_STRUCTURE_SPEC.md`, `production_prompts.md`, `DATA_FLOW_MAP.md`, `SCHEMA_COMPARISON.md` (March-era specs superseded by current code)
- `CURRENCY_MEMO.md`, `OBSERVATION_LOG.md`, `ORGINIZE_REVIEW.md`, `audit_current_state.md`, `AUDIT_REPORT.md`, `GAP_DISCOVERY.md`, `GAP_INVENTORY.md` (early-April audits — recovered features now live; inventory was the input to FORWARD_PLAN)
- `INQUISITOR_QUEUE.md` (round 1 — superseded by R2)
- `REVIEW_MARATHON_DOSSIER.md` (one-shot pre-marathon prep doc)
- `FORWARD_PLAN.md` (mid-April strategic doc — superseded by STRATEGIC_RECOMMENDATIONS_2026-04-30.md)
- `TILE_SPEC.md` (early-April tile inventory — superseded by per-tile audits in tile-specs/)

If you need any archived doc, it's still in git history + `docs/archive/`.

---

## 🛠️ Templates

| File | What it is |
|---|---|
| `docs/templates/tile_audit_template.md` | Skeleton for `tile-audit` subagent output. |

---

## 🚀 Quick-start commands

```bash
./load_data.sh ~/Downloads/<file>.csv          # parse → verify → open dashboard
./smoke_test.sh --quick                        # ~1.5s pre-flight check (now includes week-flow lint)
python3 verify_factset.py                      # FactSet asks audit (auto-runs in load_data.sh)
python3 lint_week_flow.py                      # NEW: catches direct cs.X access in render functions
python3 lint_week_flow.py --strict             # NEW: exits 1 on findings (CI gate)
python3 -m pytest test_parser.py -x -q         # parser regression suite (89 tests)

# Local dashboard server (Safari-compatible)
python3 -m http.server 8765                    # serve via http://localhost:8765
open http://localhost:8765/dashboard_v7.html   # main dashboard
open http://localhost:8765/dev_dashboard.html  # NEW: project-state view
```

---

## 🤖 Subagent runbook

See `AGENTS.md` (NEW 2026-05-01) for the full subagent roster + when to spawn each.

Quick reference for the most-used:
| Agent | Spawn when | Output |
|---|---|---|
| `tile-audit` | Tier-1/2 tile review | `tile-specs/{id}-audit.md` |
| `data-integrity` | Numeric anomaly, parser/normalize/render touch | GREEN/YELLOW/RED audit report |
| `data-viz` | "make this chart more useful" | `viz-specs/{chart-id}-spec.md` |
| `Explore` | Quick codebase question | Inline answer |
| `feature-reconciliation` | "what features do we actually have" | `FEATURE_RECONCILIATION.md` |
| `gap-discovery` | "where did feature X go" (after lost work) | `GAP_INVENTORY.md` |
