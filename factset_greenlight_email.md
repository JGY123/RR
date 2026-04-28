# Email: Green-light for the massive run

**To:** [FactSet contact]
**From:** Yuda
**Subject:** Green-light for the massive run — phased start + quick confirms

---

Hi [name],

**We're green-light. Please proceed with the full multi-year extraction for the six worldwide-model accounts (ACWI, IOP, EM, GSC, IDM, ISC).** Sample-3 verified end-to-end against our pipeline yesterday — parser, dashboard, integrity checks all clean. Goal is to have the data in RR today.

A structural recommendation and a couple of quick-confirm items below. None of them should hold up the run; please address whichever are cheap (minutes-to-hour) and ship the rest as-is.

---

## Phased start (recommended)

Run **GSC since inception** first as a single-strategy test pull. Reasons:

- It's the smallest worldwide account, so we'd validate that the multi-year history layout (>10,000 columns) parses cleanly on our side without committing extraction time on the bigger accounts.
- Any structural surprise gets caught on a small file rather than one we'd have to re-extract.
- We expect a clean pass — sample-3 already confirmed the per-period column structure works — but inception-depth history is the first time we'd see the wide format at full scale.

After GSC clears our integrity check (~5 min on our end), trigger the remaining five accounts in the same shape. If "since inception" is too aggressive for a first run, 10 years on GSC works the same way.

---

## Two quick-confirm items (resolve before extraction starts if cheap)

**1. Currency on Market Capitalization and Vol 30D Avg.** Per yesterday's call, confirm both are exported in **USD**. Sample-3 has the values but no unit indicator. Just need a yes.

**2. Five static per-holding fields are repeated six times per row in the Security section.** They live inside the weekly column block but never change week-to-week:

- Redwood GICS Sector
- Redwood Region1
- Redwood Country
- Industry Rollup
- RWOOD_SUBGROUP

Three options, ordered by preference:

**(a) Move them to a fixed-prefix block** (single occurrence per row, not per period). About a 10% file-size reduction; cleaner to ingest. If straightforward in your tooling, do this.

**(b) Ship them in a separate one-time / annual file** keyed by SEDOL. We'd run the static file once, refresh annually. The weekly massive file would omit them entirely and we join client-side — same pattern I already use on my end for the industry / country / currency reference mappings. Less file-size churn week-to-week.

**(c) Leave as-is.** Not a blocker — just noise in the file. We'd compress it on our side.

If any of these can be turned around in an hour or so, my preference is (a) for the massive run and (b) going forward. If not, ship as-is and we iterate.

---

## Re-confirming items locked in earlier calls (so nothing falls through)

- **Six worldwide-model accounts** in this run: ACWI, IOP, EM, GSC, IDM, ISC. SCG and the new Alger accounts will ship in a separate **domestic-model file**. Placeholder is already in the dashboard for them.
- **History depth**: maximum available per account (since inception preferred; otherwise the longest consistent series).
- **Schema doc alongside the file**: a short data-dictionary — one row per column with name, units, value type, edge-case behavior. Avoids "what does column 47 mean" debates later. Even a CSV-of-headers format works.
- **Anchor strings stable**: our parser uses section anchor labels ("Security", "Raw Factors", "18 Style Snapshot", "% Specific Risk", etc.) to identify section boundaries. Please don't rename them silently in future pulls. If a rename is unavoidable, give us 30 days' notice.
- **Append-only weekly cadence** post-run: future weekly updates should ship just the new week's data, not a re-pull of full history. SFTP preferred, posted Tuesday morning ET. File naming `worldwide_YYYYMMDD.csv` works.
- **Backwards-compat**: once a column ships, it doesn't get dropped or renamed in a future weekly without notice.

---

## One observation from sample-3 verification (not a blocker)

The Industry table has incomplete benchmark coverage (Σ bench weight = 68–79% across strategies, vs 100% on Sector / Country / Region). About a quarter of benchmark holdings don't carry an Industry classification. If that's a quick lookup-table fix on your side, great; otherwise I'll work around it.

---

## Two follow-up items for the next iteration (no rush)

These didn't ship in sample-3 and aren't blocking. Calling them out so they're queued for the next run after the massive one:

1. **Per-holding period return** (a single `PERIOD_RETURN` column on each Security row). Unlocks Brinson attribution client-side without a separate per-sector return table.
2. **Sector / Country / Industry historical fields** (`%T`, `%S`, `W`, `BW` per period at group level). Currently the per-period history exists at the holding level but not at the rolled-up group level. Would let us draw multi-week trend lines per sector.

Neither is critical for the green-light, but worth tracking so they don't get lost.

---

## Process

- **Notification when complete**: please email me as soon as the run finishes so I can run our verification pass right away (~5 min). If anything in the output looks off on your QA, flag it before delivery — much cheaper to catch on your side.
- **Domestic-model file (SCG + Alger)**: when can we expect it? I have a placeholder in the dashboard ready and the parser is built to handle a smaller factor list (no FX/Country/Currency macros) gracefully.
- **Estimated extraction time**: please share an ETA so I can plan around it.

Thanks — really appreciate the work to get sample-3 in this shape. Looking forward to having the data in RR today.

Best,
Yuda
