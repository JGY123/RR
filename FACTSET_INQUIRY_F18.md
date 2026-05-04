# Letter to FactSet — Inquiry F18

**Subject candidates** (pick whichever lands best with their team):
- _Question on per-holding %T summing behavior in PA exports_
- _Help us understand: %T per-holding vs portfolio total in Portfolio Attribution_
- _Per-holding %T sums 94→134% across our strategies — guidance requested_

---

## Recipient

`<insert FactSet PA contact name>` — ideally a **Portfolio Attribution / quant analyst** at FactSet, not a generic support rep. A subject-matter expert who knows the math and the data layer.

If you don't have a named contact: ask your FactSet account manager to route to "the quantitative attribution team — we have a specific question about how %T values aggregate."

---

## Letter draft

> Hi [name],
>
> We're building an internal portfolio risk dashboard called Redwood Risk, sourced entirely from FactSet Portfolio Attribution CSV exports across 6 strategies (ACWI, ACWIXUS / IOP, EM, IDM, ISC, GSC), with weekly history going back as far as 2014 (~3,000 weekly snapshots in total). The dashboard is built around a strict no-fabrication policy: every numeric cell traces back to a documented source path, and we'd rather show "missing" than guess. That's the lens behind this question.
>
> Our internal documentation has long stated that **`%T` (the per-holding "Percentage of tracking error" column in the Security section) sums to ~100% per portfolio per week** — i.e., that each holding's %T value is its share of total portfolio TE, and the column normalizes across the universe.
>
> We've now run a full reconciliation across all 6 strategies on the latest weekly snapshot (2026-04-30) and observed the following:
>
> | Strategy | `cs.sum.te` | **Σ h.%T** | Σ h.%S | N holdings | Deviation |
> |---|---|---|---|---|---|
> | EM | 5.51 | **94.6** | 60.0 | 914 | −5.4 |
> | ISC | 6.25 | 107.0 | 70.6 | 2,209 | +7.0 |
> | GSC | 6.98 | 109.8 | 68.7 | 1,002 | +9.8 |
> | IDM | 6.47 | 115.9 | 62.6 | 775 | +15.9 |
> | ACWI | 6.65 | 125.3 | 56.2 | 2,048 | +25.3 |
> | IOP | 7.11 | **134.4** | 52.6 | 1,703 | +34.4 |
>
> Range: **94.6 → 134.4** — a ±35% deviation from the documented "~100%" claim. The deviation is non-uniform across strategies, which suggests it's not a uniform sampling issue but something portfolio- or universe-specific.
>
> **What's clean and reassuring:** the **section-aggregate** rows (Sector Weights / Country / Region / Group) DO sum to ~100% — we verified 3,082 of 3,082 sector-weeks across all 6 strategies fall within ±5% of 100%, with averages dead-on 100%. We've now baked this into a Layer-2 automated monitor (`verify_section_aggregates.py`, wired into our pre-flight smoke test) so any drift would be caught immediately. So at the section-aggregate level the math holds; the deviation appears specifically in the per-holding Security-section `%T` column.
>
> **What we've already disciplined ourselves on:** to make sure this isn't a parser bug on our side, we audited the parser for related issues. We did find one — per-week `pct_specific` / `pct_factor` in the historical summary was being silently dropped; the parser DID extract them per RiskM period but never wrote them through to `hist.summary[]`. Fixed (FORMAT_VERSION 4.3, May 2026). We mention this so you know we've cleaned our own house before bringing this to you.
>
> Could you help us understand:
>
> 1. **Is `%T` per-holding intended to sum to ~100% per portfolio per week?**
>    Our docs say yes; observed data says no. Which is correct?
>
> 2. **If approximate (not exact 100%), what's the expected tolerance?**
>    A ±5% range we'd accept as rounding; ±35% suggests something structural.
>
> 3. **Is `%T_Check` (the inclusion flag in the Security section) filtering some rows from the export?**
>    We see this flag in your output but don't fully understand its semantics. Could it be filtering bench-only or below-materiality rows in a way that affects the sum?
>
>    Related observation that may be a clue: on a recent audit of bench-only holdings, we found that **76% of bench-only constituents on EM** ship `%T = null` (623 of 819 bench-only holdings). Only the 196 with shipped `%T` are slim-Security entries; the 623 long-tail constituents come through Raw Factors with no `%T_implied`. If `%T_Check` is the gate that decides which BM-only rows make the Security section, that filter behavior may also explain part of the per-portfolio deviation. (We're tracking this separately as inquiry F12 — an enhancement request to ship `%T_implied` on the long-tail; it's a related but distinct conversation.)
>
> 4. **Does the per-strategy variance hint at a known cause?**
>    EM under-reports (94.6%); IOP / ACWI heavily over (125-134%). Both ACWI and IOP have very large bench universes (~2,000+ names). Is there a relationship between universe size or %T_Check inclusion logic and the sum behavior?
>
> 5. **Are there other Security-section columns we should be aware of that aggregate differently or might inform this?**
>    We use `%T`, `%S`, `OVER_WAvg`, `REV_WAvg`, `VAL_WAvg`, `QUAL_WAvg`, `MOM_WAvg`, `STAB_WAvg`, plus the Raw Factor Exposure block. We'd love to understand if any other columns (compounded factor return, hit rate, etc.) would deepen our risk attribution.
>
> 6. **Documentation request:** if there's a quantitative methodology white paper for Portfolio Attribution that explains `%T` derivation, the inclusion logic, and the aggregation conventions, we'd love a copy for internal training.
>
> We're happy to share:
> - A python notebook / script that reproduces the table above on our data so you can verify the observation (or point out an error in our aggregation).
> - The exact CSV slice from one strategy + week (e.g., EM 2026-04-30) so you can compare to your reference values.
> - A 30-minute video call to walk through what we're seeing.
>
> This is part of an internal effort to build deep expertise on the metrics we depend on — we'd rather understand the math than work around the symptom. Any time you can spare to teach us about the underlying mechanics is appreciated.
>
> Thanks,
> [Your name]
> [Title / context]

---

## Attachments to include

1. **The cross-strategy table** (above, formatted as PDF or screenshot for the email body)
2. **A small reproducer script** — `verify_section_aggregates.py` (we'll write this — see DATA_INTEGRITY_MONITOR.md). Output is the table itself.
3. **One representative CSV slice** — e.g., EM 2026-04-30 Security section, ~914 rows. They can compare line-by-line to whatever PA shows internally.
4. **Link to FACTSET_FEEDBACK.md F18 entry in the repo** — full archival record of the finding, hypotheses, and our defensive UI workaround.

---

## Tone notes

- **Lead with respect for their expertise** — we're asking them to teach, not to fix.
- **Be specific** — concrete numbers, named strategies, observed range. Vague "the data looks weird" gets vague replies.
- **Acknowledge what's clean** — section-aggregates sum cleanly. This narrows their investigation and shows we've already done the obvious checks.
- **Open the door for ongoing dialogue** — questions 5 and 6 invite them to broaden into education / column discovery, not just answer the narrow F18 question.
- **Offer to do work** — sharing the reproducer script + CSV slice + offering a call lowers their effort to engage.
- **Don't bluff** — if we don't know what `%T_Check` does, we should say so (we did, in question 3). Honesty earns the right answer.

---

## Internal next steps before sending

1. ✅ DONE — `verify_section_aggregates.py` shipped + wired into smoke test. Section-aggregate invariant confirmed clean on 3,082/3,082 sector-weeks. The cross-strategy table in the letter is reproducible at any time via this verifier.
2. Run the PA-side tests (`PA_TESTS_F18.md`) — eliminates "did we read the column wrong" as a hypothesis. Plan ~1 hour at a desktop with PA access.
3. **Have a real human review the letter** before send. Tone, recipient, attachments. Specifically check that question 3's F12 cross-reference reads as "additional context" not "scope creep" — we want to keep F18 narrow.
4. **Decide whether to send by email vs raise a support ticket** — the letter format works for a relationship contact; for a ticket, condense to questions 1-4 and link to the repo doc.
5. Update FACTSET_FEEDBACK.md F18 entry with "letter sent YYYY-MM-DD to [recipient]" once it goes out.

**Pre-send readiness checklist (2026-05-04):**
- [x] `verify_section_aggregates.py` confirms the cross-strategy table reproducibly
- [x] Parser-side hygiene fixes (F19) shipped — letter mentions this to demonstrate due diligence
- [x] F18 contamination map filed in `SOURCES.md` — every tile that displays a Σ %T now has a defensive disclosure footer (cardRiskByDim · cardRanks · cardRiskDecomp · cardTreemap · cardUnowned all done)
- [ ] PA-side experiments run (recommend ~1 hr human session at PA desktop)
- [ ] Recipient name confirmed (FactSet account manager → quant attribution lead)
- [ ] Letter human-reviewed for tone + factual accuracy
- [ ] CSV slice + reproducer script attached or linked

When all checkboxes filled, the letter is ready to send.

---

## When the reply comes back

1. **Capture the answer in FACTSET_FEEDBACK.md F18** — promote from "open" to "answered" with the reply summary.
2. **If they confirm 100% should hold** → there's a parser bug; investigate where %T is being mishandled.
3. **If they confirm the deviation is expected** → update CLAUDE.md line 108 to remove the "~100%" claim. Update the cardRiskByDim about-caveat to reference their explanation. Close F18.
4. **If they teach us something new** → fold into FACTSET_INQUIRY_TEMPLATE.md so future inquiries follow the same pattern.

This letter is the start of a relationship, not a one-shot fix request.
