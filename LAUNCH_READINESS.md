# RR Launch Readiness — Doing it Right

**Drafted:** 2026-05-04
**Context:** Post-presentation (May 1 demo went well). User direction: _"there's no sense of urgency anymore — this is about making things RIGHT."_
**Goal:** structured inventory of what's needed for the dashboard to be **complete, correct, and considered** — not "minimum-shippable."

---

## Working principle (REVISED 2026-05-04 PM)

> **No urgency. Quality over speed.** Do every item to the standard the project deserves — don't take shortcuts. F18 gets investigated properly, not deferred. Tile audits get finished, not stopped at 14 of 30. Docs get written carefully. Runbooks get battle-tested. The dashboard is for daily PM use; treat it like a daily-use tool, not a demo prop.

---

## How to read this doc

For each launch category:
- ✅ **DONE** = exists + battle-tested
- ⚠️ **PARTIAL** = exists but stale or incomplete; needs work
- ❌ **MISSING** = nothing exists yet

The user picks which gaps to close first. We then execute methodically, one section at a time, with smoke tests + git tags between each.

---

## 1. CODE QUALITY

| Item | Status | Evidence |
|---|---|---|
| All tiles use uniform chrome (`tileChromeStrip`) | ✅ DONE | 30/30 tiles migrated, `refactor.20260504.1030.phase-D-complete` |
| All tables have column hide/show | ✅ DONE | 8/8 dashboard tables, `refactor.20260501.1530.phase-C-complete` |
| Design system (tokens + canonical classes) | ✅ DONE | 10 classes, ~40 inline styles eliminated |
| Per-week data flow lint-enforced | ✅ DONE | `lint_week_flow.py` wired into smoke_test.sh |
| Smoke test (parse + lint + verify) | ✅ DONE | `./smoke_test.sh --quick` ~2s |
| Parser regression suite | ✅ DONE | 89 pytest tests, all passing |
| Anti-fabrication policy enforced | ✅ DONE | `_synth` markers + ᵉ render badges |
| Tile-audit cadence (3 tiles audited recently) | ⚠️ PARTIAL | 14 of 30 tiles have current audits; ~16 stale or missing |
| **F18 — per-holding %T deviation 94→134%** | ❌ **OPEN** | RED finding, escalated to FactSet, blocking PM trust on cardRiskByDim / cardHoldRisk |
| End-to-end browser test (loads, all tabs render) | ❌ MISSING | Manual only; no Playwright/Cypress harness |

**Gaps blocking launch:** F18 needs FactSet response. Tile-audit cadence should reach Tier-2 coverage before launch.

---

## 2. DATA INTEGRITY

| Item | Status | Evidence |
|---|---|---|
| Single Python parser (no JS-side parsing) | ✅ DONE | `parseFactSetCSV` throws; `factset_parser.py` is the only path |
| Verifier (`verify_factset.py`) | ✅ DONE | 22+ pass/fail checks, schema fingerprint, last_verify_report.log |
| `_b115AssertIntegrity()` runs on every load | ✅ DONE | catches drift between raw JSON and normalized state |
| Per-cell provenance index | ⚠️ PARTIAL | SOURCES.md exists but ~3 weeks old; needs refresh after Phase D + audits |
| Section-aggregate %TE sums to ~100% | ✅ VERIFIED | 3,082/3,082 sector-weeks ±5%; Region/Group ~99% |
| Per-holding %T sums to ~100% | ❌ **F18** | Range 94→134% across 6 strategies; blocks normalization claims |
| Latest week always green-light | ✅ DONE | latest verifier run: 🟢 GREEN-LIGHT |
| Historical data (multi-year) | ✅ DONE | ACWI 553wk, EM 383wk, IDM 618wk, GSC 526wk, IOP 470wk, ISC 526wk |
| **Schema-drift detection** | ✅ DONE | fingerprint at `.schema_fingerprint.json`, smoke test catches drift |

**Gaps blocking launch:** F18 is the only data-integrity item. SOURCES.md refresh is housekeeping, not blocking.

---

## 3. OPERATIONAL RUNBOOK

| Item | Status | Evidence |
|---|---|---|
| Load CSV → run dashboard one-liner | ✅ DONE | `./load_data.sh ~/Downloads/<file>.csv` |
| Multi-account loader (1.7GB+ files) | ✅ DONE | `./load_multi_account.sh`, per-strategy split, lazy-load architecture |
| EM full-history merge | ✅ DONE | `merge_em_history.py` + workflow documented |
| Pre-flight before risky edit | ✅ DONE | smoke_test.sh + lint_week_flow.py + git tag discipline |
| HTTP server for Safari (file:// fetch blocked) | ✅ DONE | `python3 -m http.server 8765` documented in SESSION_GUIDE |
| Hard-refresh procedure (Safari + Chrome) | ✅ DONE | SESSION_GUIDE has both shortcuts |
| Recovery procedure if dashboard hangs | ⚠️ PARTIAL | No formal "if X happens, run Y"; ad-hoc |
| Weekly data-load runbook (PM-facing) | ❌ MISSING | PRESENTATION_DAY_GUIDE has demo-day version; weekly cadence not yet documented |
| Backup / rollback procedure | ⚠️ PARTIAL | git tags catch code; data backup not formalized |

**Gaps blocking launch:** weekly data-load runbook for PMs. Rollback procedure should be documented.

---

## 4. DOCUMENTATION

### For PMs / Analysts (end users)

| Item | Status | Evidence |
|---|---|---|
| What is RR? (90-second pitch) | ✅ DONE | EXECUTIVE_SUMMARY.md |
| Tab-by-tab walkthrough | ⚠️ PARTIAL | EXECUTIVE_SUMMARY has table; full screenshot-walkthrough missing |
| FAQ (common questions) | ❌ MISSING | Only PRESENTATION_DAY_GUIDE has demo Q&A |
| Quirks / known limitations | ⚠️ PARTIAL | scattered across LESSONS_LEARNED, SOURCES.md, audit docs |
| Tile reference (every tile, what it shows) | ⚠️ PARTIAL | About registry has it (`_ABOUT_REG`), but no exported PM-facing version |

### For IT / Deployment

| Item | Status | Evidence |
|---|---|---|
| Local Mac install (Path A) | ✅ DONE | MIGRATION_PLAN.md Path A |
| Linux server install (Path B) | ⚠️ PARTIAL | MIGRATION_PLAN.md Path B is sketched, not battle-tested |
| systemd timer for weekly cron | ❌ MISSING | conceptually in MIGRATION_PLAN but no actual timer file shipped |
| nginx reverse proxy config | ❌ MISSING | mentioned in plan, not written |
| Auth / SSO integration | ❌ MISSING | not scoped yet — internal-only assumed |
| DR / backup strategy | ❌ MISSING | git is the source of truth but `latest_data.json` regen takes a CSV pull |

### For handoff / new contributor

| Item | Status | Evidence |
|---|---|---|
| Codebase architecture overview | ⚠️ PARTIAL | REFACTOR_PLAN + REFACTOR_AUDIT cover state; no clean ARCHITECTURE.md |
| Subagent runbook | ✅ DONE | AGENTS.md (2026-05-01) |
| Session start guide | ✅ DONE | SESSION_GUIDE.md (2026-05-01) |
| Hard rules (anti-fabrication, etc.) | ✅ DONE | CLAUDE.md + LESSONS_LEARNED.md |
| Tile-audit template | ✅ DONE | docs/templates/tile_audit_template.md |
| ARCHITECTURE.md (data flow + tile contract + design system) | ❌ MISSING | Would consolidate REFACTOR_AUDIT + IMPACT + design tokens for new contributors |

**Gaps blocking launch:** PM-facing tile reference (probably auto-generate from About registry); systemd timer + nginx config for Linux deployment; DR/backup strategy.

---

## 5. ONBOARDING

| Item | Status | Evidence |
|---|---|---|
| First-time PM session: 5-minute productive | ⚠️ PARTIAL | EXECUTIVE_SUMMARY plays this role but not field-tested |
| Sample data for demo (no FactSet access required) | ✅ DONE | `latest_data.json` ships with repo (1.97 GB, gitignored — but `data/strategies/*.json` are present) |
| Walkthrough video / screenshots | ❌ MISSING | Static doc only |
| In-product tour / first-load welcome | ❌ MISSING | Currently lands on tab 1 with no intro |

**Gaps blocking launch:** at minimum a screenshot-tour PDF or in-product welcome.

---

## 6. RISK REGISTER

| Item | Status | Evidence |
|---|---|---|
| F-items list (CSV-side asks to FactSet) | ✅ DONE | FACTSET_FEEDBACK.md (F1–F18) |
| Lessons learned from past crises | ✅ DONE | LESSONS_LEARNED.md |
| Backlog of in-progress work | ✅ DONE | BACKLOG.md (22 active items) |
| **Production risk register** (what could go wrong, and what's the mitigation) | ❌ MISSING | Lessons-learned is retrospective; no forward-looking risk register exists |
| Escalation paths (who to call) | ❌ MISSING | No documented "if data fails to load on Monday, contact X" |

**Gaps blocking launch:** production risk register + escalation paths. ~30 minutes to draft from existing lessons.

---

## 7. STAKEHOLDER COMMUNICATION

| Item | Status | Evidence |
|---|---|---|
| Executive summary (90-sec pitch) | ✅ DONE | EXECUTIVE_SUMMARY.md |
| Presentation deck | ✅ DONE | PRESENTATION_DECK.md (12 slides) |
| Demo flow / talk track | ⚠️ PARTIAL | PRESENTATION_DAY_GUIDE has demo-day version, not generic |
| Internal launch announcement (1-page) | ❌ MISSING | "RR is now live for the team. Here's how to access it." |
| First-week PM cheat sheet | ❌ MISSING | "5 things to check Monday morning" |

**Gaps blocking launch:** launch announcement + cheat sheet. Both ~1 hour to draft.

---

## 8. LIFECYCLE / VERSIONING

| Item | Status | Evidence |
|---|---|---|
| Semantic version | ⚠️ PARTIAL | `PARSER_VERSION="3.1.0"` + `FORMAT_VERSION="4.2"` (parser); dashboard has no explicit version label |
| CHANGELOG.md | ✅ DONE | `CHANGELOG.md` exists |
| Tagged releases | ✅ DONE | 30+ tags including `presentation-2026-05-01-shipped` (current launch candidate baseline) |
| Update cadence (weekly data, monthly code, quarterly review) | ❌ MISSING | Implicit; not formalized |

**Gaps blocking launch:** dashboard version label visible in UI (~5 min); update cadence doc.

---

## What "right" looks like — by category

Each item is what we'd ship if we had unlimited time and were doing it properly. The point isn't "do everything" — the point is to know what _good_ looks like for each, then choose where to invest.

### Code quality

- **F18** — investigate properly. Spot-check FactSet CSV column directly; reach FactSet team; either confirm 94→134% is correct (and update CLAUDE.md's "~100%" claim accordingly) OR find the parser bug. Don't leave it as a YELLOW caveat.
- **Tile audits — finish all 30.** Currently 14 audited. Schedule 16 more across upcoming sessions, 2-3 at a time, parallel subagents. Each audit's RED/YELLOW findings get either shipped or filed with reasoning.
- **End-to-end browser test harness** — Playwright or Cypress. Catches regressions before users do. Should run in CI alongside `smoke_test.sh`.
- **CSS / layout consistency final sweep** — many `style="margin:Xpx"` / `style="padding:Y"` still off the design-token scale. Polish pass through every renderer.

### Data integrity

- **F18 resolved + documented** — see above.
- **SOURCES.md refresh** — every numeric cell on the dashboard cross-referenced to its parser source + render path + any synth markers. Currently ~3 weeks stale.
- **Verifier expansion** — 22 checks today. Should cover every F-item (F1-F18) once-through, and every section-aggregate sum (sector/country/region/group/industry × all strategies).
- **Cross-strategy reconciliation tests** — periodic pytest that loads `latest_data.json` and asserts the section-aggregate sums (proven 100% in this session) + flags any drift.

### Operational runbook

- **Weekly data-load runbook for PMs** — Monday-morning script: drop CSV, run loader, what to look for, what to do if verifier yellow/red, who to call.
- **Recovery runbook** — every plausible failure (file missing, parser error, browser fetch blocked, verifier red, dashboard hangs, JSON corrupt) has a documented remedy.
- **Backup / rollback** — formalized procedure. `latest_data.json` snapshots on a rolling schedule. Tag-based code rollback already works; data rollback isn't documented.
- **Schema-drift response** — what to do when FactSet ships a format change (the fingerprint catches it; what's the fix workflow?).

### Documentation

- **ARCHITECTURE.md** — single canonical doc covering: data flow (CSV → parser → JSON → normalize → render), tile contract (chrome / week-flow / About registry), design system (tokens / canonical classes), week-flow lint enforcement, anti-fabrication policy.
- **PM-facing tile reference** — every tile's About entry exported as a clean PDF or HTML page. Auto-generate from `_ABOUT_REG`. Print-friendly.
- **IT deployment runbook** — Linux server setup, nginx config, systemd timer, log rotation, monitoring. Battle-tested, not just sketched.
- **FAQ** — common PM questions ("what's the universe pill?" / "why does cardRiskByDim sum > 100?" / "where do I find historical Beta?"). Living doc, grows from usage.

### Onboarding (PM/analyst first-time experience)

- **First-load welcome** — guided tour highlights 3-5 key tiles. Persists "seen welcome" flag. Skippable.
- **Screenshot tour or 3-minute Loom** — visual reference for users who prefer pictures over docs.
- **Demo data shipped** — sample `latest_data.json` (or `data/strategies/`) so a new install Just Works for evaluation.
- **First-week cheat sheet** — "5 things to check Monday morning." 1 page, printable.

### Risk register

- **Production risk register** — forward-looking ("what could go wrong"), not retrospective ("what went wrong"). Known-issue table with severity / probability / mitigation / escalation.
- **Escalation paths** — who's on point if data fails, if dashboard fails, if FactSet ships a bad file.

### Stakeholder communication

- **Internal launch announcement** — 1-page "RR is live. Here's how to use it. Here's the support path."
- **Demo flow / talk track** — generic (not demo-day-specific) so anyone can demo it.
- **First-week cheat sheet** — see Onboarding above.

### Lifecycle / versioning

- **Dashboard version label in UI** — `v1.0.0 · data 2026-04-30` in header. PMs always know what version they're using.
- **Update cadence** — formalized: weekly data, monthly code (or as needed), quarterly review.
- **CHANGELOG.md cadence** — every release tag gets a CHANGELOG entry. Currently sporadic.

---

## How to choose what to work on

Without urgency, the question isn't "what's MUST-HAVE." It's:

1. **What's the highest-quality / most-foundational item that's currently incomplete?**
2. **What unblocks the most other items if done?**

Some candidates by that lens:

- **F18 investigation** unblocks confidence in cardRiskByDim, cardHoldRisk, and any future tile that aggregates per-holding %T. Likely the single highest-leverage item.
- **ARCHITECTURE.md** unblocks future contributors (and future-you re-orienting after a long break).
- **Tile-audit completion** unblocks signoff on the dashboard as a whole.
- **PM weekly runbook** unblocks the PM team using it without hand-holding.

---

## Recommendation for next session

Pick **one** of these and do it properly to a high standard, before moving to the next:

1. **F18 investigation** — read raw CSV column for %T, compare parser output, escalate cleanly to FactSet with concrete numbers + a hypothesis. Update CLAUDE.md if the documented invariant is wrong. ~1-2 hours.
2. **ARCHITECTURE.md** — consolidate REFACTOR_AUDIT + REFACTOR_IMPACT + design tokens + lint rules into one canonical doc. ~1-2 hours.
3. **Continue tile-audit cadence** — pick 2-3 more Tier-2 tiles, run parallel subagents, ship trivial fixes. ~1-2 hours per batch.

User picks. We execute properly. No shortcuts.

