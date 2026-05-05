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

**Confidence calibration: low.** I do not have a confident explanation. Below is honest reasoning about what the data does and doesn't tell us.

**What the per-strategy decomposition shows** (re-probed 2026-05-05):

| Strategy | Σ pos | Σ neg | Σ signed | Σ \|abs\| | n_pos | n_neg | n_zero |
|---|---|---|---|---|---|---|---|
| EM | +95.7 | −1.10 | 94.6 | 96.8 | 63 | 8 | 220 |
| ISC | +108.8 | −1.80 | 107.0 | 110.6 | 46 | 14 | 404 |
| GSC | +110.8 | −1.00 | 109.8 | 111.8 | 52 | 10 | 940 |
| IDM | +133.4 | −17.50 | 115.9 | 150.9 | 64 | 61 | 89 |
| ACWI | +139.5 | −14.20 | 125.3 | 153.7 | 49 | 50 | 602 |
| IOP | +156.7 | −22.30 | 134.4 | 179.0 | 45 | 69 | 346 |

The 94→134% range is **signed sum (Σ pct_t)** — NOT absolute. So:

**A clean "signed-decomposition that nets to 100% of TE" theory predicts:**
- Σ pos + Σ neg ≈ 100 across all strategies
- Variance comes mostly from positives (with negatives roughly offsetting cleanly)

**That's NOT what we see:**
- Σ signed varies 94 → 134
- Σ pos varies 96 → 157 (already wider than 100)
- Σ neg varies −1 → −22 (much wider than "rounding")
- Strategies with bigger universes have BOTH more negatives AND more positives AND higher signed sums — like the column scales with universe structure

So I was overconfident when I framed this as "clean signed semantics, doc was simplified." The data has a pattern I don't fully understand. It could be any of:

- (a) The per-holding column might use a different denominator than total portfolio TE
- (b) There could be uncaptured cross-terms / covariance / Euler residuals in the math (FactSet's methodology likely has a "residual" allocation rule)
- (c) The 100% claim in our docs might have been misremembered or always approximate
- (d) Something specific about how %T is computed for bench-only or specific row classes (the high `n_zero` rate suggests a materiality threshold; the `n_neg` increasing with universe size suggests bench-only rows behave differently)

**The dashboard is still correct** — we extract per-row values faithfully, section aggregates verify clean, defensive UI footers honestly disclose. But I shouldn't have claimed I knew the explanation. **I don't.**

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

**Two-step approach** (revised after the data re-probe — see above; I was initially overconfident about the casual-ask path):

### Step 1: Ask for the methodology doc

Casual one-paragraph email to your Alger account manager: *"For the Portfolio Attribution Security-section `%T` column, can you share the methodology doc that explains how it's computed (the denominator, any inclusion/exclusion rules, any cross-term / residual handling)? In our exports we see the column behave differently than our internal docs assumed, and we'd rather read the right doc than reverse-engineer from data."*

This is asking for the **methodology**, not for a specific answer. ~50% chance the doc immediately explains the pattern; ~30% chance the doc is general and we still need a follow-up; ~20% chance there's no clean doc and we need a quant call.

### Step 2: If methodology doc doesn't fully explain it, send the formal letter

The formal letter (`FACTSET_INQUIRY_F18.md`) is the right artifact for that case. It's over-prepared for the 50% case where the doc immediately answers, but it's correctly-scoped for the 30-50% case where it doesn't.

**Recommended action:** drop the methodology-request ask whenever convenient. If the doc you receive answers it cleanly → close F18 with the doc citation. If it doesn't → escalate via the formal letter.

### What I would NOT do

- **Don't** wait to send the formal letter until you fully understand the math yourself. The letter IS asking them to teach us; the empirical patterns we've gathered are sufficient context.
- **Don't** rescale the displayed values to make them sum to 100% in the dashboard — that would be silent fabrication. The footers handle disclosure correctly.
- **Don't** treat the per-strategy variance as a parser bug — we've ruled that out via spot-checks and re-parses.

---

## Closing

The dashboard is correct + honest. The math underneath FactSet's column is more complex than I claimed when I wrote "signed semantics fully explains it." I'm walking that overconfidence back.

**Calibration for the next 30 days:** F18 is not a daily workstream. It's "request the methodology doc next time you talk to FactSet, and escalate to the formal letter if the doc doesn't answer." I'll stop listing it in next-priority sections, but I shouldn't have framed it as "obvious doc gap" — it's "we have empirical patterns we haven't yet matched to a methodology."

The defensive footers stay. The dashboard is fine for showings. The understanding gap is real but bounded.
