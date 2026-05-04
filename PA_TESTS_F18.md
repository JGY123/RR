# PA-Side Tests — F18 Per-Holding %T Investigation

**Goal:** experiments we run **inside FactSet PA** (the source system) ourselves, before / alongside the FactSet expert reply. The point is to eliminate hypotheses we can rule out, isolate the cause, and arrive at the FactSet expert call with sharp questions instead of vague ones.

**Audience:** whoever has PA access on our side (analyst / PM with login).

---

## Hypotheses to test

From FACTSET_FEEDBACK F18 + cardRiskByDim audit:

1. **H1: CSV-export ≠ PA-display** — the column we read in the CSV (`%T`) shows a different value than what PA shows on screen for the same holding.
2. **H2: `%T_Check` filters rows** — some holdings in PA aren't emitted to the CSV; the surviving ones don't sum to 100%.
3. **H3: Bench-only %T behaves differently** — port-held holdings sum cleanly; bench-only contribute the deviation.
4. **H4: Universe / threshold parameter** — PA has a "minimum %T to include" parameter that's been set to a value other than 0; surviving rows don't normalize.
5. **H5: Period-handling artifact** — `%T` for a single weekly period vs cumulative across periods aggregates differently than we assume.
6. **H6: `%T` is intentionally non-normalizing** — the documented "~100%" is just wrong; %T was never meant to sum to 100%.

---

## Tests to run

### Test 1 — Single-strategy single-week sanity check (15 min)

**Why:** rule out CSV ≠ PA display (H1).

1. In PA, open EM strategy, set period to **2026-04-30 ending week**.
2. Pull the **Security** section to the screen (NOT export to CSV).
3. Pick **3 specific holdings** — one large port-held (e.g., top 5 by weight), one medium port-held, one bench-only.
4. **Read the `%T` value on screen for each.**
5. Open the CSV we exported the same week. Find the same 3 holdings (by SEDOL).
6. **Compare side-by-side:**
   - Do the on-screen values match the CSV values?
   - If yes → H1 ruled out. Move to Test 2.
   - If no → ROOT CAUSE FOUND. Either (a) export step shifts the column, (b) parser misreads, (c) PA shows different value than emits.

**Document:** in this file, append `### Test 1 results (YYYY-MM-DD)` with screenshots / numbers.

---

### Test 2 — Σ %T inside PA itself (10 min)

**Why:** rule out H6 (intentionally non-normalizing) by reading what PA itself shows as the sum.

1. In PA, on the same EM 2026-04-30 view, look for an **aggregate row / footer** showing total %T or "Sum of %T".
2. **Does PA show 100.00%?** Or does it show 94.6% (matching our observation)?
3. If PA's own footer shows ≠100%, that's the on-screen confirmation that the doc's "~100%" claim is wrong, not our parser. → H6 supported.
4. If PA shows 100.00% but the rows on display only sum to 94.6% → some rows are being filtered for display, supporting H2 or H4.

**Document:** screenshot of PA's footer (or note that PA doesn't show such a footer).

---

### Test 3 — `%T_Check` flag inspection (15 min)

**Why:** test H2 directly.

1. In PA, find the **`%T_Check`** column (it's in the same Security section).
2. **Inspect a few rows:** what value does it carry? Is it boolean? Is it a percentage? Does it correlate with whether a row's `%T` is included or excluded somewhere?
3. **Test:** filter the on-screen view to `%T_Check = "Y"` (or whatever the inclusion flag value is). Does the surviving subset's `%T` sum to 100%?
4. Do the same for `%T_Check = "N"`. Does that subset have meaningfully different behavior?

**Document:** the semantic of `%T_Check` you observe (it's documented in the project's CLAUDE.md but only loosely — confirm by direct PA inspection).

---

### Test 4 — Bench-only specifically (10 min)

**Why:** test H3.

1. Filter the EM 2026-04-30 Security section to **port-held only** (`W > 0`).
2. Sum `%T` across those rows. **Does it sum cleanly?** (Closer to 100%?)
3. Now sum `%T` across **bench-only rows** (`W = 0` AND `Bench Wt > 0`).
4. **Are those values being included incorrectly?** A bench-only stock has zero portfolio weight — should it have a non-zero %T contribution? If yes, what does that mean conceptually?

This test is the most likely to surface the truth: bench-only %T values are conceptually weird (a stock you don't own contributing to your TE) and may have a sign convention or normalization we're misreading.

**Document:** the port-held subset Σ%T vs the bench-only subset Σ%T for EM. If port-held sums to ~100% and bench-only adds the remainder, the answer is "%T as we get it = port + |bench| together, where the two halves don't share a common denominator."

---

### Test 5 — Cross-strategy uniformity (10 min)

**Why:** see if PA shows the same per-strategy variance pattern we see in the CSV.

1. In PA, repeat Test 2 for **all 6 strategies** in our scope (or at least 3: EM, IDM, IOP — covering the range from −5.4 to +34.4 deviation).
2. **Does PA's footer (if it has one) show the same per-strategy variance?**
3. If yes → the variance is real, not an export artifact. Confirms the question for FactSet.
4. If no → export step is doing something different per strategy.

**Document:** table mirroring our CSV table, populated with on-screen PA values.

---

### Test 6 — Period sanity (5 min)

**Why:** test H5. We're treating each weekly snapshot as independent; PA might have running / cumulative aggregations.

1. In PA, change the period from **single week (2026-04-30 ending)** to **last 4 weeks**.
2. Note whether `%T` columns shift, multiply, or behave additively.
3. Cross-check with our parser: does our extractor pick the per-period `%T` correctly when the CSV has multiple periods (the multi-month format)?

This is a parser-side check too. The 30%-threshold multi-month detection in `factset_parser.py` is the relevant code path.

---

### Test 7 — Documentation excavation (15 min, parallel to other tests)

**Why:** rule out H6 (doc just wrong) and find authoritative reference.

1. **Search PA's help / documentation** for "Percentage of tracking error" or "%T".
2. Pull any methodology white paper or column-glossary entry.
3. Note: does the doc claim 100% sum? Does it explain the per-holding derivation? Does it mention `%T_Check`?
4. If you find a contradicting doc inside PA → bring it to the FactSet call.

**Document:** copy the relevant doc snippet here.

---

## How to execute these tests organized

Pick a **single 1-hour PA session**. Do tests in this order:

1. Test 7 first (docs) — sets context.
2. Test 1 (one strategy on-screen vs CSV) — the cheapest test that could rule out everything.
3. Test 4 (port vs bench) — likeliest to surface the cause.
4. Test 3 (`%T_Check`) — semantic.
5. Test 2 + 5 (PA's own sum) — confirms or denies H6.
6. Test 6 (period) — last; only relevant if other tests didn't conclude.

After each test, add a short results section here. Even a single negative finding ("Test 1: PA matches CSV") is valuable — it eliminates a hypothesis.

---

## What the results buy us

| Outcome of tests | What we know | What's next |
|---|---|---|
| All hypotheses ruled out | Mystery — pure FactSet question | Send the letter, wait for reply |
| H1 confirmed (CSV ≠ PA) | Parser or export bug | Fix the parser; close F18 internally |
| H2 / H4 confirmed (filter active) | `%T_Check` or threshold filtering rows | Update parser to handle filter; surface in dashboard |
| H3 confirmed (bench-only vs port-held split) | Two different semantics | Document it clearly; update About copy |
| H6 confirmed (doc is wrong) | "~100%" was always aspirational | Update CLAUDE.md; close F18 with explanation |

---

## Logging template (copy + fill per test)

```
### Test N results — YYYY-MM-DD

**Operator:** [name]
**PA version / strategy / week:** [...]
**Hypotheses tested:** H[X], H[Y]

**Observation:** [what we saw on screen, with numbers]

**Conclusion:** [hypothesis ruled out / supported / inconclusive]

**Next step:** [follow-up needed, or move to next test]

**Screenshots / artifacts:** [paths or links]
```
