# Email: GSC pull — Security + consumption concern

**To:** [FactSet contact]
**From:** Yuda
**Sent:** 2026-04-29 (morning, after sample-4 verification)
**Subject:** GSC pull — let's get on a call today

---

## AS-SENT VERSION

Hi,

The bulk pull didn't complete — the Security section is missing entirely. There are also other gaps in the output: the Spotlight tables (Overall / REV / VAL / QUAL) shipped only the portfolio-aggregate row — the quintile-level breakdowns are missing.

In order to be cognizant of consumption costs, we all worked really hard upfront — probably spent weeks extra crossing every t and dotting every i — specifically so we wouldn't need to re-run the whole history multiple times. The last thing that should be done now is start tweaking here and there and re-running through trial and error; that will only inflate the consumption metrics. We need to figure out systematically what's happening and how to bypass it — not iterate blindly.

The Security table is by far the most important one — by design. Instead of enriching every grouping table (which would have driven up consumption), we deliberately chose to make Security the centerpiece — the place that holds the data that completes everything missing from the other tiles. Losing Security isn't just losing a section; it's losing the spine of the architecture we agreed on.

I'm glad we ran only one account first. But if a single account on a shorter history than most of the others didn't make it through the way you'd suggested it might, scaling to many more accounts with longer histories along this path doesn't look realistic — and I'm not sure where that leaves us.

Let's start troubleshooting and come up with a plan. One thought to start with — though I'm not sure it would move the needle, and I wouldn't know how to test without rerunning and driving up consumption. So we need more than that, but maybe it could get us started: could a few essential columns from Security move into the Raw Factors table? Raw Factors clearly did scale (527 weekly periods). Adding columns there might lighten the load from the Security section. But I'd rather hear your take on the root cause first.

I'd like to connect as early as possible today to troubleshoot and lock in a plan.

Thank you.

---

## Notes for the call (if asked)

### What's confirmed missing from sample-4 (GSC inception-to-date, 395 MB)

| Section | Expected | Actual |
|---|---|---|
| Security | ~9,000 holdings × 271 cols × 527 wk | **0 rows** |
| Spotlight: Overall | per-holding × 18 cols × 527 wk | **1 row** (portfolio total only) |
| Spotlight: REV | per-holding × 18 cols × 527 wk | **1 row** |
| Spotlight: VAL | per-holding × 18 cols × 527 wk | **1 row** |
| Spotlight: QUAL | per-holding × 18 cols × 527 wk | **1 row** |

### What worked

| Section | Rows | Cols | Periods |
|---|---|---|---|
| Raw Factors | 8,389 | 7,385 | 527 |
| Sector Weights | 14 | 9,493 | 527 |
| Country | 31 | 9,493 | 527 |
| Industry | 34 | 9,493 | 527 |
| Region | 10 | 9,493 | 527 |
| Group | 10 | 9,493 | 527 |
| 18 Style Snapshot | 126 | 5,804 | 527 |
| Portfolio Characteristics | 526 | 95 | — |

Group-level rank columns (over / rev / val / qual / mom / stab) ARE present — they're embedded in the by-dimension sections, so we have sector- and country-level Spotlight aggregates. It's specifically the **per-holding** Spotlight + the **per-holding** Security layer that didn't ship.

### Path-A proposal: merge essentials into Raw Factors

If FactSet wants specifics on what to add to Raw Factors so we don't need a separate Security section:

**Minimum viable per-holding columns (5):**
- `W` (portfolio weight)
- `BW` (benchmark weight)
- `AW` (active weight) — derivable from W − BW, but cheaper to ship
- `%T` (TE contribution)
- `%S` (stock-specific TE)

These plus the existing 12 z-score loadings already in Raw Factors give us essentially the full per-holding analytic surface.

**What we'd live without:**
- Per-holding ORVQ ranks (we get them at group level)
- Per-holding factor_contr (the 16 % Factor Contr to Tot Risk cols) — derivable client-side from W × raw_exp if needed
- Per-holding sector/region/country grouping cols (we already have a static reference mapping)

### Feasibility math

- Raw Factors today: ~7,385 cols × 8,285 rows ≈ 60M cells (shipping fine)
- Adding 5 cols × 527 periods = ~2,635 extra cols per row
- New size: ~9,020 cols × 8,285 rows ≈ 75M cells
- ~25% bigger than current Raw Factors — should be tractable

### Compared to full Security section

- 271 cols × ~9,000 holdings × 527 periods ≈ ~1.4 GB per strategy
- × 6 strategies = ~8.4 GB total
- Vs. Raw-Factors-with-extra-cols path: ~75 MB extra per strategy
