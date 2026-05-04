# FactSet Inquiry Template — Use for F19, F20, F21, …

**Purpose:** every time we discover a metric we depend on but don't fully understand, we follow this template. It produces:
- A clean letter we can send to FactSet
- An internal record of what we knew before vs after
- Updated automated monitoring
- A more-expert RR over time

**Inspired by:** the F18 inquiry (per-holding %T sums 94→134%, escalated 2026-05-04).

---

## When to open a new F-item

Trigger any of these:

- A tile audit finds a value that "doesn't match expectation" and it's not explained by our code.
- Σ-of-some-thing doesn't match what the documented behavior implies.
- A FactSet column has been blank for long enough that we wonder if it should have data.
- We discover a column in the CSV header we don't currently use, and we can't tell what it means.
- A PM asks "where does X come from?" and we don't have a clean answer.

## Sequence

```
1. Observe         → write down WHAT you saw, with numbers
2. Hypothesize     → list reasons it could be
3. PA-test         → run experiments inside FactSet PA to rule out hypotheses
4. Inquiry letter  → ask FactSet expert with sharp questions
5. Reply captured  → fold the answer back into the system
6. Monitor added   → automated check so the question won't sneak up again
```

Each step has a deliverable. Don't skip steps.

---

## Step 1 — Observe (file: `FACTSET_FEEDBACK.md` entry)

Append a new section to `FACTSET_FEEDBACK.md`:

```markdown
### F## — [one-line description]

**Finding date:** YYYY-MM-DD (source: tile audit / PM feedback / etc.)
**Severity:** RED / YELLOW / GREEN
**Affects:** [which tiles / paths / dashboards]

[2-4 sentence description of what was observed]

[A table or chart with concrete numbers if applicable]

**Possible causes:**
1. [hypothesis A]
2. [hypothesis B]
3. [hypothesis C]

**Workaround in dashboard (if any):** [what we did defensively]
```

Numbers are non-negotiable. "It looks weird" is not a finding; "Σ%T = 94.6 on EM, 134.4 on IOP" is.

## Step 2 — Hypothesize

In the F-item entry above, list every reasonable cause. Even ones you think are unlikely. The PA tests (Step 3) will rule them out one by one.

Tip: include "documentation is wrong" as a hypothesis — sometimes the doc IS the bug.

## Step 3 — PA-side tests (file: `PA_TESTS_F##.md`)

Copy `PA_TESTS_F18.md` as starting point. Adapt for your specific F-item:

- Each test takes 5-15 min in PA.
- Each test rules out ≥1 hypothesis or supports a specific cause.
- Document results in the same file (the "## Test N results" sections).

If a test confirms the cause locally, you may not need to send the letter — just close the loop internally + add monitoring (Step 6).

## Step 4 — Inquiry letter (file: `FACTSET_INQUIRY_F##.md`)

Copy `FACTSET_INQUIRY_F18.md` as starting point. Adapt:

- **Subject** — specific to the metric, mention the strategy / period if relevant
- **Greeting** — warm, named recipient if possible
- **Context** — 2-3 sentences: who we are, why we depend on this column
- **Observation** — table of numbers from Step 1
- **What's clean** — show what we've already verified is OK; narrows their investigation
- **Specific questions** — 4-6 numbered questions, sharp, answerable
- **Offer to do work** — share script / data / do a call
- **Tone** — they're the expert, we want to learn

Send. Log the send date in the F-item.

## Step 5 — Reply captured (back in the F-item entry)

When FactSet replies:

- Promote F-item from `OPEN` to `ANSWERED`
- Append the relevant reply quote / summary
- Decide: was our docs wrong, our parser wrong, or our understanding wrong?
- Update CLAUDE.md or SOURCES.md if the documented behavior was wrong
- Update parser if extraction was wrong

If they don't reply for 2 weeks, follow up. If they don't reply for 4 weeks, escalate to your account manager. Don't let the F-item rot.

## Step 6 — Monitoring added (file: `verify_section_aggregates.py` or similar)

Once we understand the metric:

- Add an automated check that catches the next deviation. Per `DATA_INTEGRITY_MONITOR.md`.
- Decide the threshold (95-105? 80-120? always exactly?). Document why.
- Wire into `smoke_test.sh`.

The whole point of the loop: F18 was caught manually. F19 should be caught by Layer 2 monitoring before a PM ever sees it.

---

## What gets re-used across inquiries

Every inquiry produces three files:
- `FACTSET_FEEDBACK.md` (single shared file — append-only)
- `PA_TESTS_F##.md` (one per F-item)
- `FACTSET_INQUIRY_F##.md` (one per F-item)

And updates one file:
- `verify_section_aggregates.py` — gains a new check

---

## Knowledge accumulation

After 5-10 cycles of this loop, we'll have:

- A nuanced understanding of every column we use
- A FactSet relationship that returns calls
- A monitoring layer that surfaces drift on day 1
- A systematic record of "what we asked, what they said, what changed"
- A team that's noticeably more expert than 6 months prior

That's the point. The metrics are not a black box — they're tools we should master.

---

## Inquiry register (running list)

| F# | Subject | Status | Letter sent | Reply | Closed |
|---|---|---|---|---|---|
| F1-F17 | (older items — see FACTSET_FEEDBACK.md) | mixed | various | various | various |
| **F18** | Per-holding %T sums 94→134% (not 100%) | **OPEN** | (drafted, not sent) | — | — |

(Append F19, F20, … here as new inquiries open.)
