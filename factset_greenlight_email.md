# Email: Green-light for the massive run

**To:** [FactSet contact]
**From:** Yuda
**Sent:** 2026-04-28 (morning)
**Subject:** Green-light for the massive run

---

## AS-SENT VERSION

Hi,

First — thank you. The work to get to this point has been substantial, and we really appreciate it. The output is clean, the parser sings, and we're ready to go.

**We're green-light. Please proceed with the full multi-year extraction for the six worldwide-model accounts (ACWI, IOP, EM, GSC, IDM, ISC). Goal is to have the data in RR today.**

A structural recommendation and a couple of quick-confirm items below. None should hold up the run — please address whichever are cheap (minutes-to-hour) and ship the rest as-is.

---

## Phased start (recommended)

Run **GSC since inception** first as a single-strategy test pull. A few reasons it makes sense to start with one before going wide:

- It validates that the multi-year history layout — which will have an enormous column count — parses cleanly on our side before we commit extraction time on the rest of the accounts (some with even longer history).
- Any structural surprise gets caught on a small file rather than one we'd have to re-extract.
- We expect a clean pass — the latest sample already confirmed the per-period column structure works — but inception-depth is the first time we'd see the wide format at full scale.

After GSC clears our integrity check (~5 min on our end), trigger the remaining five accounts in the same shape.

---

## Quick cleanup before GSC (very fast — please do these now)

1. **Hidden Industry rows.** Industry table has incomplete benchmark coverage. About a quarter of the bench is hidden. Please unhide and save before the GSC run. I tried it this morning without saving so I know it's a quick fix — just unhide, save, and run.

2. **`%T_Check` column on the group tables** — Sector Weights, Industry, Country, Region, Overall, REV. The column is constant 1.00 (or empty) for every row across all 6 periods. Country shows it as something like `%T filter` — same idea, please remove. Save once, apply to every group table.

These 2 should each be a matter of minutes — please do them ahead of GSC.

---

## Two confirm items — GSC can run ahead of these

1. **Currency on Market Cap and Vol 30D Avg.** Confirm both are in **USD** as discussed yesterday.
2. **Price Volatility appears static per holding in the sample — why is that?**
3. **Five static per-holding fields are repeated 6× per row in the Security section.** They live inside the weekly column block but never change week-to-week:
   - Redwood GICS Sector / Redwood Region1 / Redwood Country / Industry Rollup / RWOOD_SUBGROUP

   Three options, ordered by preference:
   - **(a) Move them to a fixed-prefix block** (single occurrence per row). ~10% file-size reduction.
   - **(b) Ship them as a separate one-time / annual file** keyed by SEDOL. Weekly massive file omits them; I run them separately — same pattern as our existing reference-mapping setup. Happy to take this approach if (a) isn't easy and the saving is worthwhile.
   - **(c) Leave as-is.** Not a blocker.

If any can be turned around in an hour, push them through first. Otherwise, we can change these ahead of the **five other international runs** (after GSC) — the goal is to have all of the international strategies fully run by today, and this is a polish item that'd compound on a 20-year file size.

---

## Re-confirming items from earlier calls

- All 6 should run **inception-to-date** — please let me know ASAP if you need any help with the dates.
- 6 worldwide-model accounts in this run. SCG + Alger ship in a separate **domestic-model file** later (placeholder ready in the dashboard).
- **Schema doc alongside the file** — short data-dictionary, one row per column. We talked yesterday this might be possible; don't let it hold anything up.
- **Anchor strings stable**: parser uses section labels to identify boundaries. This shouldn't be a problem — we're not changing anything here, just flagging it for the record.
- **Append-only weekly cadence** is a future-state thing — we'll deal with that once everything in the history is there.

---

## Process

Please notify me as soon as the run completes so I can run our verification pass right away (~5 min). If anything in the output looks off on your QA, flag it before delivery — much cheaper to catch on your side.

Thanks again — really appreciate all the work getting us to this point. Looking forward to having the data in RR today.

Best,
Yuda
