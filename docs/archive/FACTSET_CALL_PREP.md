# FactSet Call — Final Pre-Massive-Run Checklist

**Drafted:** 2026-04-27
**Purpose:** consolidate every open data-extraction question/ask into one prioritized list so by end of call the spec is "good to go" and the next sample (then the 15+ account massive run) ships clean. References every prior FactSet-related doc; nothing duplicated unless emphasis matters.

**Acceptance criterion for green-light:** every item in §A and §B has a yes/no answer + a confirmed sample-file deliverable date. §C items are nice-to-have and can land in a follow-up.

---

## A. CRITICAL — must resolve before massive run

### A1 · Security section completeness
**Source:** factset_email_READY_TO_SEND §1A·1B
**Ask, plain:** Every weekly Security row block must contain ALL portfolio holdings AND all benchmark constituents passing the materiality filter. Today most strategies show only 19–50% coverage (GSC = 19% — 9 of 50 holdings).
**Acceptance:** in the sample file, count of Security rows per strategy = (port holdings) + (bench holdings with `BW ≥ 0.5%` OR `%T ≥ 1%`). Verify against the strategy's reported holdings count in the summary.
**Why it blocks everything:** every drill-down, factor attribution, and risk decomposition assumes the Security section is complete. Group-table %T won't reconcile with security-summed %T until this lands.

### A2 · Per-holding RiskM-style fields on the Security row (factor TE contribution + raw factor exposures)
**Source:** factset_email_READY_TO_SEND §1C-A and §1C-B + factset_data_expansion_request §2
**Ask, plain:** For each holding, two new column blocks:
1. **Factor TE contribution** — how much of this holding's `%T` flows through each factor. Should sum to the holding's total `%T`. **Highest priority** of the two.
2. **Raw factor exposures (z-score loadings)** — the Axioma loadings for the 12 style factors per holding.
**Coverage preference:** if data permits, ALL factors (12 style + Market + every individual industry + every individual country + every individual currency). If too wide, the 12-style + 4-aggregate (Market/Industry/Country/Currency) version is the floor.
**Why it matters:** unlocks the Spotlight / Quadrant / cardRiskByDim tiles to flip universe (Port vs Bench) without synthesis. Removes the `ᵉ` derived markers in the current dashboard.

### A3 · RiskM section header alignment
**Source:** FACTSET_FEEDBACK F2
**Ask, plain:** Today's RiskM section has cells where the column headers don't match the cell content (numeric values appearing under date-label headers, missing factor-name columns, blank `% of Variance` and `Active Exposure` cells). Anchors the parser uses (`% of Variance`, `Active Exposure`) are absent.
**Acceptance:** every factor row populated for both `% of Variance` AND `Active Exposure` columns. Headers match cell content; no off-by-one shifts. Sample to be verified end-to-end before massive run.

### A4 · Per-factor TE contribution (`f.c`) — never synthesize again
**Source:** FACTSET_FEEDBACK F5 + SOURCES.md (15.1% Size case is currently synthesized `|a|×σ → normalized`)
**Ask, plain:** For each factor, ship the actual % of total tracking error attributable to it. Today this is null on Growth and most others — dashboard is computing a placeholder value with `ᵉ` marker but the user has banned this practice (anti-fabrication).
**Acceptance:** every factor in every weekly snapshot has a non-null `% TE contribution` cell sourced from FactSet, sums to ~100% across the factor set.

### A5 · Group-table completeness — include zero-weight rows
**Source:** factset_email_READY_TO_SEND §3A
**Ask, plain:** Sector / Country / Industry / Group / Region tables today exclude rows where the portfolio has zero weight. That hides active underweights. Benchmark sums currently 60–95% instead of 100%.
**Acceptance:** all 11 GICS L1 sectors appear for every strategy; benchmark weight sum ≈ 100%. Same for Industry, Country, Region, and Group tables. Zero-W rows show `W=0, BW=X, AW=−X`.

### A6 · Overall rank table grouping logic
**Source:** factset_email_READY_TO_SEND §2 Issue 2
**Ask, plain:** Overall quintile groups are mis-bucketed (Q1 OVER_WAvg = 1.78 instead of 1.00). Sub-rank tables (REV/VAL/QUAL) bucket correctly — Q1 self-rank-avg = 1.00 exactly. Align Overall to the same logic.

### A7 · CSV quoting fix for security names with commas
**Source:** factset_team_email §5 + still flagged
**Ask, plain:** Fields containing commas (legal entity names: "ABC Corp., Ltd.") shift columns and corrupt rows. Force double-quoting on all string fields.
**Acceptance:** verify by searching sample for any name-field comma; row count and column alignment unaffected.

---

## B. CONFIRMATION — yes/no items needed before signing off the spec

### B1 · Multi-strategy file delivery for 15+ new accounts
**Question:** the upcoming massive run includes 15+ additional accounts beyond today's 7. Confirm:
1. All accounts ship in a single concatenated file with `ACCT` column distinguishing them, OR each in a separate file with identical schema?
2. Will the column structure remain bit-identical across all accounts, including ones with different benchmark types (custom blends, fund-of-funds)?
3. Any account-specific schema variation (e.g., a fund-of-funds with sleeves) needs flagging upfront.

### B2 · 20-year history schema stability
**Question:** Going back 20 years (2006-ish), the Axioma model has shipped multiple versions, factor names have changed (e.g. "Medium-Term Momentum" used to be "Momentum (Medium-Term)" — note the space/parens difference; "Profitability" used to be split). Confirm:
1. Will FactSet retroactively apply the **current** Axioma model + factor names across the full history, OR will historical periods carry their period-correct names?
2. Same question for GICS reclassifications (per §3B of email — Retailing → Consumer Discretionary Distribution & Retail, Media → Media & Entertainment, Pharmaceuticals split, etc.). Apply current GICS retroactively or preserve point-in-time names?
**Strong preference:** apply current names retroactively. Time-series tracking breaks otherwise.

### B3 · Append-only weekly delivery mechanism (post-massive-run)
**Question:** After the 20-year baseline lands, future weekly pulls — confirm:
1. Will each weekly file contain ONLY the new week (append-friendly), OR re-ship the full history?
2. If only new week: what's the file structure? What guarantees row identity stability week-over-week?
3. Delivery channel: SFTP / S3 / API / email? On what schedule (Tuesday morning of next week)?
**Why:** RR has an append-only persistence architecture (HISTORY_PERSISTENCE.md). Re-pulling 20 years every week is expensive and breaks the delta model.

### B4 · Date timestamp convention
**Question:** weekly snapshots — represent which day's close? Friday close T+0? T+1? End-of-day vs intraday? Confirm so the dashboard's date labels are right.

### B5 · Currency / country mapping for ADRs
**Question:** for EM and ACWIxUS, country_of_risk vs country_of_listing differ for ADRs (e.g., a TSMC ADR listed on NYSE in USD, but country-of-risk = Taiwan, currency-of-risk = TWD). Today the Security section's Country / Currency columns — do they reflect country-of-risk, country-of-listing, or country-of-incorporation? Same for Currency.
**Acceptance:** confirm convention; document in the schema spec the team will share.

### B6 · Anchor invariants
**Question:** the parser uses several text-anchor strings to locate sections (e.g. `% of Variance`, `Active Exposure`, section headers like "RiskM", "Sector Weights", "Security"). Are these anchors stable across:
1. All 15+ new accounts?
2. All 20 years of history?
3. Future format updates that may add columns?
**Why:** parser breaks silently if anchors drift. We've already had one parser-drift incident (April 2026 wacky-numbers crisis).

### B7 · `@NA` / `[Unassigned]` / `[Cash]` semantics
**Source:** factset_team_email §9
**Question:** confirm:
1. `[Cash]` = portfolio's cash allocation (already assumed)
2. `@NA` = holdings unclassified into a grouping dimension (sector/country)?
3. `[Unassigned]` = same as `@NA` or different?
4. Are `@NA`/`[Unassigned]` weights INCLUDED in named-group totals, or separate?
**Why:** affects whether we double-count or under-count weights when summing.

### B8 · Compounding methodology for Cumulative Factor Impact
**Source:** FACTSET_CALL_NOTES — already asked but answer needed in writing
**Question:** Cumulative Factor Impact in the 18 Style Snapshot — compounded weekly-over-weekly, OR daily-compounded then aggregated? Affects whether sub-period reconstruction from weekly figures is exact or approximate.

### B9 · Factor-availability matrix
**Source:** FACTSET_CALL_NOTES — Earnings Yield/FX Sens null active exposure for some strategies
**Question:** is the systematic null pattern in RiskM (Earnings Yield / FX Sens / Market Sens / Momentum have empty active exposure for 6/7 strategies; Leverage / Liquidity / Profitability / Volatility have empty `% of Variance` for same) a model-vs-universe phenomenon (some Axioma factors not estimated for EM stocks?) or a report-config issue?

### B10 · Failure-mode handling for new IPOs / illiquid securities
**Question:** when a security has no Axioma factor exposure (recent IPO with insufficient history, illiquid OTC), what does the cell show? Blank? Zero? Some sentinel? Need to know to distinguish "intentionally zero" from "data missing".

### B11 · Numeric precision
**Question:** weights, returns, TE contributions — what decimal precision is exported? 2dp / 4dp / native? Are values rounded at write-time, or pass-through from source? Affects how small bench-only contributions get rounded out.

---

## C. DATA ADDITIONS — priority-tagged for the massive run if straightforward

### C1 · Brinson attribution inputs (`sector_port_return`, `sector_bench_return`, `bench_total_return`)
**Source:** factset_team_email §12b — strongly worth re-emphasizing
**Why:** unlocks classic Allocation/Selection/Interaction breakdown — a standard PM view. Either per-sector returns OR a single per-holding `PERIOD_RETURN` column works.
**Priority:** **HIGH** — single biggest net-new analytical capability if shipped.

### C2 · 18 Style Snapshot — add `% of Variance` per row
**Source:** factset_email_READY_TO_SEND §4
**Why:** efficient alternative to broken-out RiskM rows (one extra column on existing rows vs +130k new rows). Lets us see which specific industry/country/currency contributes to TE alongside return attribution.

### C3 · Sector / Industry / Country level history fields (`%T_HIST`, `%S_HIST`, `W_HIST`, `BW_HIST` per period)
**Source:** B6 backlog — needed for cardSectors / cardCountry / cardGroups Trend column to show dual-encoded history
**Why:** today `cs.hist.sec` is empty in parsed JSON — sector-level historical %T isn't shipped per period. With it, the layered sparkline (B106) shows full TE history alongside active-weight history. Without it, falls back to current-TE indicator only.
**Priority:** MEDIUM — Trend column degrades gracefully without it but shines with it.

### C4 · Top-tier fundamental metrics (10 most-impactful)
**Source:** factset_additional_fields_email — 46 metrics listed, top-10 below
1. Forward P/E (NTM) — port + bench
2. EV/EBITDA — port + bench
3. Price/Sales — port + bench
4. Revenue Growth 1Y — port + bench
5. ROIC — port + bench
6. Net Debt/EBITDA — port + bench
7. Total Return 1Y — port + bench
8. Excess Return vs BM 1Y
9. Gross Margin — port + bench
10. EPS Growth NTM — port + bench
**Why:** transforms the Characteristics tile from 8 metrics to 18; keeps current vertical layout.

### C5 · Hit Rate / Batting Average
**Source:** factset_team_email §12
**Why:** % of active positions contributing positively to relative return. Simple summary stat the dashboard has a slot for.

### C6 · Trailing returns at portfolio level by horizon
**New ask:** 1M / 3M / 6M / 1Y / 3Y / 5Y / SI for each strategy (port + bench + active). Today we have weekly + cumulative impact in factor attribution but no clean strategy-level trailing-period returns.

### C7 · Currency hedging exposure (for hedged share classes)
**New ask:** if any of the 15+ new accounts run with currency hedging, expose the hedge ratio per currency / net hedged exposure. Don't currently have this surfaced.

### C8 · Holdings turnover (port % traded per period)
**New ask:** the dashboard can show "how much did the portfolio change last period?" only roughly today (compare consecutive weekly snapshots). A direct turnover field per period would be cleaner.

### C9 · Daily data option for recent month
**New ask:** for the most recent month, can a daily-frequency file accompany the weekly bulk? Improves attribution accuracy on intra-week events (earnings days, tariff announcements, etc.). Doesn't need to be retroactive — just current month.

---

## D. LOGISTICS — confirm before signing off

### D1 · Test-pull-first cadence
**Ask:** before the 15+ account massive run, ship a SHORT verification file:
- 1–2 weeks of data
- 2–3 representative strategies (one DM, one EM, one small-cap)
- All A1–A7 fixes applied
- All B1–B11 confirmations documented in a schema doc

**Why:** parser regression test runs in <5 min on this size; catches column-shift / anchor-drift issues before wasting compute on the bulk extraction.

### D2 · Delivery channel + schedule
- Sample-file delivery mechanism (today): email / SFTP / shared drive
- Massive-run delivery mechanism: same or different
- Ongoing weekly: SFTP / S3 / API / email
- Day-of-week + time-of-day for ongoing weeklies

### D3 · Schema documentation
**Ask:** alongside the next sample, FactSet ships a brief schema doc listing every section, every column, the value type, units, and any edge-case behavior. Living document we both reference. Avoids "who knows what column 47 means" debates.

### D4 · Backwards-compatibility commitment
**Ask:** once a column ships in a delivered file, it doesn't get removed or renamed in future pulls without 30 days of notice. We can absorb additions but silent removals or renames break the parser.

### D5 · Account code mapping confirmation for new 15+
**Source:** factset_team_email §14 covers current 7. New ask covers the 15+.
**Ask:** as soon as the new account list is ready, share the mapping table (account code → strategy name → benchmark) so we can pre-register each in the dashboard's strategy mapping (CLAUDE.md table) and update `data/security_ref.json` if any new identifiers appear.

---

## E. ALREADY CONFIRMED FROM PRIOR CALL — verify it survives the massive run

From `factset_additional_fields_email.md` post-call notes:
- ✅ Benchmark P/E and P/B will be included
- ✅ Date columns added to each table
- ✅ CompoundedFactorReturn enabled (was blank in §10 of `factset_team_email.md`)
- ✅ Overall Rank extra columns removed from holdings (was §3 of `factset_team_email.md`)

**Verify in the next sample:** all four shipped + survived the RiskM-section work above.

---

## F. STRUCTURAL CHANGES ALREADY CONFIRMED IN NEW FORMAT — re-validate

From `factset_data_expansion_request.md` and current parser:
- ✅ Section column with explicit labels (RiskM, Security, Sector Weights, etc.)
- ✅ Date column on every row
- ✅ Per-holding Sector / Region / Country / Industry / Subgroup grouping columns on Security rows (per `factset_team_email.md §4`)

**Verify in the next sample:** all three preserved + section anchors stable.

---

## G. WHAT THE DASHBOARD NEEDS THAT THE CSV CAN'T PROVIDE

Not asks for FactSet — recording for completeness so the user knows what they're separately responsible for:
- Strategy-level commentary / commentary corpus → user-edited
- Custom benchmark blends defined → strategy-mapping config
- Watchlist tickers (per-PM) → localStorage `rr_flags_*`
- Notes per tile / per security → localStorage `rr_notes_*`
- Glossary definitions → in-app curated

---

## H. CONVERSATION OPENING SUGGESTION

> "We've parsed and validated against the latest sample. Before the massive run, want to align on what fixes have shipped, what's still in flight, and confirm a few things about how the 15+ new accounts and 20-year history will land. I'll send this doc as the agenda — we can go through §A (must-resolve) first, then §B (confirmations), then §C (additions if straightforward). Goal: by end of call we both sign off on the spec for the next short test pull. Then I verify in the dashboard and you green-light the massive run."

---

## I. POST-CALL NEXT STEPS (your side)

1. Receive the short verification sample
2. Run `./load_data.sh <sample>.csv` → check B115 integrity assertion passes
3. Spot-check each A-item per Acceptance criterion above
4. Verify §B confirmations match what shipped in §A
5. Audit a representative subset of cardSectors / cardCountry / cardRiskByDim against the new fields
6. Mark FACTSET_FEEDBACK.md F-items as Closed/Resolved with sample-file SHA
7. **Green-light** the massive 15+ account run

---

## How to use this doc

- Open during the call
- Mark each item ✅ / ❌ / ⚠️ inline
- Items with ❌ need follow-up → add to FACTSET_FEEDBACK.md as new F-items
- Save call output to `FACTSET_CALL_NOTES_<YYYYMMDD>.md` so we have a record
