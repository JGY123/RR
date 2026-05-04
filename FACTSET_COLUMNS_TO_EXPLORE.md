# FactSet Columns We Don't Currently Use

**Purpose:** inventory of columns that FactSet ships in our PA exports but RR doesn't currently consume — alongside columns we use but don't fully understand. Companion to FACTSET_FEEDBACK.md (which is asks) and FACTSET_INQUIRY_TEMPLATE.md (which is method).

**Why:** the user's framing — _"trying to find ways to actually become more of an expert on all of these metrics including other columns that might be available to consume that are outside the scope of this project."_ The dashboard uses ~30 columns; the CSV ships ~100. The other ~70 might unlock real value if we knew what they meant.

---

## Three categories

1. **In CSV, not in dashboard** — columns that exist in the export but we haven't wired up yet.
2. **In CSV, partially used** — columns we read for one tile but might apply elsewhere.
3. **Not in CSV but available in PA** — features we could request to be added to the export.

---

## Category 1 — In CSV, not in dashboard

| Column / section | Where it ships | What we think it is | Worth investigating? | F-item if opened |
|---|---|---|---|---|
| `Compounded Factor Return` | RiskM section, currently always blank | Geometric link of period factor returns over the full horizon. If populated, would let cardFacButt show "true" multi-period impact (vs the simple-sum approximation we currently flag with ᵉ). | **HIGH** — flagged in FACTSET_FEEDBACK F5 already. | F5 |
| `Hit Rate` / batting average | Mentioned in PA UI, may be derivable | % of weeks where active return was positive. PM-friendly metric. | Medium — useful but easy to compute locally. | (would be F##) |
| `Sharpe / Information Ratio` per period | Possibly in PortChars section | Risk-adjusted return. We compute Sharpe from sum (`sr`), but a per-period version would let us trend it. | Medium | (would be F##) |
| Bench-only `%T_implied` for the long-tail | Raw Factors section partially | What the bench-only stocks WOULD contribute to TE if held at 0. Helps cardUnowned be complete. | High — already filed as F12. | F12 |
| `Country of risk` (vs domicile) for ADRs | Possibly an extra column we haven't surfaced | Tells us where the underlying business risk sits. Affects cardCountry accuracy. | High — F15. | F15 |
| `Sector` per holding (FactSet vs GICS) | Possibly two columns we conflate | If FactSet ships both, we should pick one + label it. | Low | (would be F##) |
| `Risk Forecast Horizon` | Maybe in RiskM | Whether the factor model is 1-year, 3-month, etc. Affects how we interpret σ. | Medium — methodology question. | (would be F##) |
| `Date stamps` per period | Multi-period files | Currently we infer week-end from `Period Start Date`. Explicit period-end might be cleaner. | Low — works today. | F13 |
| `_Avg` (simple) vs `_WAvg` (weighted) for OVER/REV/VAL/QUAL | Both ship; we use `_WAvg` mostly | Confirm the difference matters. PM could prefer simple averages in some views. | Medium — partial use today. | (would be F##) |

---

## Category 2 — In CSV, partially used

| Column | Where used today | Could also be used for | F-item if needed |
|---|---|---|---|
| `MOM_WAvg` / `STAB_WAvg` | Not currently surfaced (we use OVER/REV/VAL/QUAL only) | A "Momentum quintile" pill on cardSectors / cardCountry — exact parallel to the existing 4 ranks. PM might find it useful for risk-on/risk-off framing. | (would be F##) |
| `OVER_WAvg` itself | Surfaced as "O" rank | Could also drive a strategy-level "average MFR rank" headline KPI. | None (no FactSet question) |
| `factor_contr` per holding (16 factors) | Used for cardFacRisk and cardSectors factor-breakdown columns | Could drive a per-holding "what's driving this name's TE" pill on cardHoldings rows. | None |
| `Period Start Date` | Used for week labeling | Period-aware analytics (rolling 13-week, etc.) | None |

---

## Category 3 — Available in PA, not (yet) in CSV

We'd need to ask FactSet to add these to the export config:

| Feature | What it would unlock | Effort |
|---|---|---|
| Per-holding **period return** (week's return for each stock) | Brinson attribution at holding level. cardWeekOverWeek could show "trimmed BMZ but it had a +12% week" — alpha narrative. | Medium — F11 already filed. |
| **Active currency** by holding | A "currency tilt" tile that's not just the implicit exposure. | Low |
| **Risk-model-version** stamp | Track when FactSet ships an Axioma model update; helps explain WoW factor σ shifts. | Low |
| **Regime classification** (e.g. risk-on/off) | If FactSet has a regime indicator, mapping it to weeks would let us label "QE era" vs "tightening era" on time series. | Speculative |
| **Brinson decomp output** from PA | Stock selection / allocation / interaction breakdown by sector/country. Powerful for narrative. | High — F11 dependency |

---

## How to investigate column by column

Use the **FACTSET_INQUIRY_TEMPLATE.md** sequence:

1. Pick one column from this doc that looks high-value or confusing.
2. Open a new F-item (F19 if F18 is current).
3. PA-test: read the column's actual values for 5 representative holdings/weeks.
4. Hypothesize what it means.
5. Letter to FactSet — same template — focus on "could you teach us what `<column>` is for?"
6. Capture reply, fold in.

We're effectively running a knowledge-extraction loop with FactSet. Done well, after 6-12 months we know the export columns better than most of FactSet's other clients.

---

## Quick wins — easy first asks

If you want to pilot the inquiry workflow on something less weighty than F18:

- **`STAB_WAvg`** — we ship it, never use it. Ask: "Is this stability rank conceptually parallel to OVER/REV/VAL/QUAL? Should it appear in the same rank cluster?"
- **`90D_ADV` and `52w_Vol`** — we use these for one tile. Ask: "Are these average daily $ volume and 52-week realized volatility? Any methodology nuances we should know?"
- **`Compounded Factor Return`** — currently blank. Ask: "Why is this column shipping empty? Is there a config option?"

Each of these is a 30-min round-trip with FactSet that produces a tangible improvement.

---

## Maintenance

- When a new column shows up in a CSV header (schema-fingerprint catches it), add it to **Category 1** here for review.
- When we wire up a previously-unused column, move it to a "used in dashboard" registry in `SOURCES.md`.
- Quarterly: re-read this doc, scan for items that have aged into "we should ask now."

---

This doc is meant to be a living inventory of curiosity. Each row is a future question. The faster we work through them — methodically, one inquiry at a time — the deeper our expertise gets.
