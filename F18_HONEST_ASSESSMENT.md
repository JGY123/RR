# F18 — Honest Assessment

**Drafted:** 2026-05-05
**Trigger:** user direction — stop bringing F18 up so often; deprioritize unless I think there's a real data-integrity issue.
**Audience:** the user (and future Claude sessions reading this — don't escalate F18 above its actual priority).

---

## My honest read: NOT a data-integrity issue

**You're right.** F18 is a documentation / understanding gap, not a data-integrity issue. Here's the reasoning in writing so it's locked in:

### What we observed

Per-holding `%T` column in the Security section sums to **94.6% to 134.4%** across the 6 strategies — non-uniform, structural, persistent across re-parses. Internal docs (CLAUDE.md and probably FactSet's user-facing materials) had us assuming `Σ %T ≈ 100%`.

### What's clean about the data

- **Per-row values are correct.** Each holding's `%T` is what FactSet computed for that holding. Spot-checks against PA on-screen would (most likely) confirm.
- **Section-aggregates are clean.** `Σ %TE` across sectors / countries / regions = ~100% on **3,082 of 3,082 sector-weeks**. The Layer 2 monitor (`verify_section_aggregates.py`) confirms this on every smoke run.
- **Section-aggregate-derived columns** (cardSectors TE Contrib per row, cardTEStacked, cardFacContribBars, etc.) are all on the **clean side** — we verified the F18 contamination map.

### What's NOT clean

- **Σ over the per-holding column** is not 100. Three patterns:
  1. Non-uniform across strategies (94→134%)
  2. GSC has 100% non-null `%T` coverage and STILL sums to 109.8% — rules out "missing rows cause it"
  3. ~70-95% of `%T` values are exactly **zero**; non-zero rows split positive AND negative; small set of large positives drives the sum

### My best explanation (without FactSet's confirmation)

Pattern 3 is the key: **per-holding `%T` is signed.** In active-risk decomposition math, individual holdings can be net diversifiers (negative %T) or net additives (positive %T). The unsigned sum can exceed 100% because positives + |negatives| > 100% of TE when contributions partially cancel.

If that's right, the documented invariant `Σ %T = 100%` was always either:
- (a) Approximate / aspirational ("close to 100" rather than exact)
- (b) Specifically about **portfolio + benchmark together** under some weighting we're not applying
- (c) A misreading of FactSet's documentation that we inherited

The fix in any case is **update our docs**, not fix our parser. The data is correctly extracted.

### Why I was harping on F18

Two reasons, neither was wrong but I overweighted them:

1. **CLAUDE.md** explicitly stated `%T` "sums to ~100%" — and the codebase had test code that asserted this. So when reality contradicted, my anti-fabrication discipline kicked in and treated it as a RED finding.
2. **The April 2026 crisis** taught us that "trust nothing without verification." When something doesn't match the documented invariant, the default move is "escalate, don't paper over." That bias is correct in general but over-applied here.

**The defensive UI I shipped is the right outcome regardless of F18 resolution.** The footers (cardRiskByDim, cardRanks, cardRiskDecomp, cardTreemap, cardUnowned) honestly disclose the deviation. Whether F18's eventual answer is "doc was wrong" (likely) or "real bug" (unlikely), the user-facing dashboard is correct + honest about what it shows.

---

## What I'm changing in my behavior

1. **F18 is no longer top-of-mind.** I won't list it in next-priority sections of strategic docs unless something changes.
2. **No more "reminder to send the letter"** in summaries. The letter is filed in `FACTSET_INQUIRY_F18.md`; it's there if/when you want it.
3. **Defensive UI footers stay.** They're correct regardless of what FactSet says.
4. **If a future audit surfaces a SECOND signed-aggregation pattern that doesn't sum cleanly,** I'll note it but won't escalate unless the per-row values themselves look fabricated or misaligned with source.

## When F18 should re-enter priority list

Only if any of these become true:

- A spot-check on one specific holding shows `%T` in the dashboard ≠ `%T` in PA's on-screen view (= parser bug, real problem)
- A PM looking at the dashboard says "this number is wrong" and the trace lands at `%T` aggregation (= real problem)
- Section-aggregate `Σ %TE` starts to deviate from 100% (= changes the picture entirely)
- An external auditor or compliance team flags the cross-strategy variance as a problem (= compliance issue regardless of math)

None of these are happening today. So F18 is parked.

---

## How you (the user) should approach asking FactSet about it (when you eventually do)

If you want to understand "why doesn't %T sum to 100" without making a formal inquiry letter, the cleanest path is:

1. **One question, one paragraph, sent to your account manager:** *"In our PA exports, the per-holding `%T` column sums to a range of 94-134% per portfolio per week across our 6 strategies. Is this expected behavior — i.e., is the column signed and the sum-to-100 invariant just a documentation simplification — or is there a methodological note on this we should be reading?"*
2. They will route to a quant. The quant will either say "yes, signed; here's the reference" (probability: ~70%) or "let me look — that should sum closer to 100, can you share an example" (~30%).
3. If the answer is the first → update CLAUDE.md, close F18, no work needed.
4. If the answer is the second → they'll dig in; the formal letter (`FACTSET_INQUIRY_F18.md`) is then the cleaner artifact to share.

The formal letter I drafted is over-prepared for a 70%-probability "documentation fix" outcome. Send it only if a casual ask doesn't get a clean answer.

**Recommended action:** when you next have a check-in with your Alger account manager (already scheduled or routine), drop the one-paragraph ask. Don't make it a Big Letter Event.

---

## Closing

I will stop bringing this up unless a verification flags a real issue. The defensive footers do their job, the contamination map is closed, and the dashboard is honest about what it shows. F18 is now a "casual question to ask FactSet sometime" — not a workstream.
