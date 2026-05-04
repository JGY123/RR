# RR Data Integrity Monitor

**Purpose:** systematic, automated verification of the data the dashboard depends on. Catches drift between FactSet exports and our expectations BEFORE the user sees a wrong number.

**Why it exists:** the F18 finding (per-holding %T sums 94→134%) was caught by manual audit, not by automation. We should have caught it on day 1 of the export, not on May 4 from a Tier-2 tile audit. This framework prevents the next F18 from going unnoticed.

---

## Layers of monitoring

### Layer 1 — Pre-flight (every parser run)

Already exists: `verify_factset.py` runs inside `load_data.sh`. 22 pass/fail checks. Output: 🟢 / 🟡 / 🔴.

**What it covers:** parser-shipped fields, schema fingerprint, holding count, factor coverage, P/E populated.

**Gaps surfaced by F18:** doesn't currently check section-aggregate sums. Doesn't check per-holding `%T` total. Adding both is the first concrete improvement.

### Layer 2 — Cross-section reconciliation (NEW — `verify_section_aggregates.py`)

Per-week, per-strategy, per-dimension: compute Σ %T and flag deviations.

```bash
python3 verify_section_aggregates.py             # ~3 sec — checks all 6 strategies × 5 dims × all weeks
python3 verify_section_aggregates.py --latest    # check just the latest week (faster)
python3 verify_section_aggregates.py --tolerance 5  # set what counts as "deviation" (default ±5%)
```

Output: a table per strategy × dimension with min / max / avg / deviation count, plus a roll-up "data integrity score." Wired into `smoke_test.sh` so it runs alongside parser regression + week-flow lint.

### Layer 3 — Trend monitoring (week-over-week)

For each (strategy, dimension), keep a rolling history of Σ %T per week. Plot it. **Anomaly = sudden change in the deviation pattern**.

E.g., if EM's sector Σ%TE has been 99-100% for 6 months and suddenly drops to 92%, that's a signal that FactSet's data shape changed. We catch it the week it happens, not 6 weeks later.

Implementation: a single-page HTML view (`data_integrity.html`) that reads `latest_data.json` and renders trend lines. Or — simpler — a CSV log that the verifier writes to per run; spot-check weekly.

### Layer 4 — Inquiry log

Every F-item in `FACTSET_FEEDBACK.md` represents a question we have for FactSet. The log structure:

| F# | Date opened | Status | Severity | Affects | Description | Resolution |
|---|---|---|---|---|---|---|
| F1-F17 | various | mixed | various | various | (existing) | (existing) |
| F18 | 2026-05-04 | OPEN | RED | cardRiskByDim, cardHoldRisk, any per-holding %T aggregation | Σ%T = 94→134% across strategies | (awaiting FactSet reply) |

Future inquiries (F19, F20, ...) follow the FACTSET_INQUIRY_TEMPLATE.md structure.

---

## What "right" looks like for monitoring

| Metric | Threshold | Action if breached |
|---|---|---|
| Section-aggregate Σ%T (sector / region / group) | 95-105% per (strategy, week) | YELLOW alert; investigate |
| Section-aggregate Σ%T (country, industry) | 90-110% per (strategy, week) — looser due to thin-tail historical | YELLOW alert; investigate |
| Per-holding Σ%T | (currently) 80-140% — F18 escalated | RED logged, defensive UI, awaiting FactSet |
| Holding count week-over-week | ±20% | YELLOW alert; verify CSV not truncated |
| Factor count | exactly 12 (worldwide) or 6 (domestic) | RED if drifts; schema-fingerprint catches this |
| `cs.sum.te` is finite + > 0 | always | RED alert; render-time integrity assert catches |

Anything RED blocks dashboard release until investigated. YELLOW logs for review at next session start.

---

## How to add a new check

When we discover a new metric we depend on (either via tile audit, F-item, or PM feedback):

1. Add a function to `verify_section_aggregates.py` that returns `(name, status, details)`
2. Add a row to the threshold table above
3. Wire into `smoke_test.sh` if the check is fast (< 1 sec)
4. Document in this file: what the check is, why we care, what failure means

Goal: every important data property has at least one automated check.

---

## Connection to FactSet Inquiry workflow

The monitor + the inquiry workflow form a feedback loop:

```
    ┌─────────────────────────────────────────────────────┐
    │   Layer 1 verifier (every load)                     │
    │   Layer 2 section-aggregate checks (every smoke run)│
    │   Layer 3 trend monitoring (weekly review)          │
    └────────────────────┬────────────────────────────────┘
                         │
              detects anomaly / new question
                         │
                         ▼
    ┌─────────────────────────────────────────────────────┐
    │  Open new F-item using FACTSET_INQUIRY_TEMPLATE.md  │
    │  Run PA-side tests (PA_TESTS_F##.md)                │
    │  Send letter to FactSet (FACTSET_INQUIRY_F##.md)    │
    └────────────────────┬────────────────────────────────┘
                         │
              FactSet replies / educates us
                         │
                         ▼
    ┌─────────────────────────────────────────────────────┐
    │  Update CLAUDE.md with corrected understanding      │
    │  Update SOURCES.md with new provenance              │
    │  Add new automated check to Layer 1/2               │
    │  Close F-item                                       │
    └─────────────────────────────────────────────────────┘
```

This is how RR becomes more expert over time. Every cycle of the loop deepens our understanding of the data + tightens the monitoring. The user's framing was exactly right: "we are trying to find ways to actually become more of an expert on all of these metrics."

---

## Roadmap

| Stage | Item | Effort |
|---|---|---|
| 1 | `verify_section_aggregates.py` — Layer 2 batch check | 30 min |
| 2 | Wire into smoke_test.sh + add 90/95/110/etc. thresholds | 15 min |
| 3 | Re-run on full data; capture baseline; commit | 5 min |
| 4 | `data_integrity.html` — Layer 3 trend view | 1 hour |
| 5 | Add to dev_dashboard.html as a new section | 15 min |
| 6 | Document: which check covers which F-item | 30 min |
| 7 | Pilot the inquiry-loop with F18 — actually send the letter, log the reply, close the loop, document learnings | depends on FactSet reply time |

Stages 1-3 are the immediate priority — they're the foundation. Stage 4-7 are the harvest.
