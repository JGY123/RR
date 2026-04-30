# Email: FactSet Data Pull — Notes Before Monday

---

**Subject:** Quick Notes Before Monday's Big Pull — Questions, Clarifications, and Suggestions

---

Hi [Name],

Thank you for setting up the sample export — it was incredibly helpful. I've spent considerable time reviewing the file and building an automated parsing pipeline against it. The good news is that the majority of the data is mapping correctly and the pipeline is working. Before you run the full production pull on Monday, I wanted to flag observations, ask clarifying questions, and suggest a few adjustments that would make the output cleaner and more reliable for daily use. Nothing here is a blocker, but getting these right upfront will save back-and-forth later.

I've organized this into: (1) structural suggestions, (2) field clarifications, (3) missing data requests, and (4) a summary checklist at the end.

---

## Part 1 — Structural Suggestions

**1. Date Labels on the Weekly Column Groups**

The current file has five repeating column groups (one per week within the month). The structure works well, but there's no date label identifying which group corresponds to which week. Right now I have to infer the dates by walking backward from the end-of-month report date to find the five Fridays — which works but is fragile.

It would be much more reliable if each column group had a date header — even just `W_20260103`, `W_20260110`, etc. — so the weekly snapshots are self-identified.

---

**2. Section Delimiters Between Tables**

The CSV contains approximately 14 separate tables concatenated into one file (sector groupings, country groupings, region groupings, custom groups, holdings, portfolio stats, factor exposures, factor attribution, etc.). Each table is preceded by a re-embedded header row where the ACCT column literally says "ACCT". This works as a delimiter, but it would be even cleaner if each section had a label row — something like `SECTION=SECTORS`, `SECTION=HOLDINGS`, `SECTION=FACTOR_ATTRIBUTION` — so the parser can identify each table explicitly rather than relying on column-count heuristics (I'm seeing 96-column, 101-column, 42-column, 9-column, and 31-column sections that each need different parsing logic).

If adding section labels isn't feasible, this is fine — the column-count detection is working. Just flagging it as a nice-to-have for reliability.

---

**3. Column Count Inconsistency — "Overall Rank" Column**

Most data sections have 96 columns (6 prefix + 5 groups × 18 metrics). However, the holdings section has 101 columns — there's an extra "Overall Rank" column inserted at position 5 within each group, making each group 19 columns instead of 18.

Can you confirm: is "Overall Rank" intentional in the holdings section? What does it represent — is it the composite quintile rank across all sub-factor scores (REV, VAL, QUAL, MOM, STAB)? My parser handles both schemas automatically, but I want to make sure I'm not misaligning columns in other sections that might also have this extra field.

---

**4. Add Grouping Columns Directly to Security Rows**

This is the single most impactful structural improvement. Right now, a security's sector, country, industry, region, and custom style group are only visible by looking at the aggregate grouping rows (the "Industrials" row, the "Japan" row, etc.). The individual security rows don't carry those labels.

If you could add these as explicit columns on each security row — **GICS Sector, Country, GICS Industry, Region, Custom Group** — it would make the security-level data fully self-contained. I could derive every breakdown (sector, country, regional, custom group) directly from the holdings table without needing the separate aggregate sections at all. This would:
- Reduce redundancy in the file
- Eliminate the risk of aggregate rows and holding-level data being inconsistent
- Make the holdings table the single source of truth for the dashboard

If this isn't feasible, a separate mapping file (ticker → sector, country, industry, region, custom group) would also work.

---

**5. Security Names with Commas — Please Quote All Fields**

I found at least two holdings in the export (CASH = Pathward Financial, Inc.) where the company name contains a comma and the CSV field is not quoted. This causes a column-shift for that row — the weight columns are misread and the position is effectively lost from the data.

Please ensure that all security name fields in the CSV are properly quoted (double-quoted) so embedded commas don't split the field. This is especially relevant for legal company names like "ABC Corp., Ltd." or "XYZ Holdings, Inc."

---

**6. Benchmark Holdings Filtering**

The file includes all benchmark constituent holdings, not just portfolio positions. That's useful — I want to keep benchmark-only holdings for the "unowned risk" analysis. I understand that the `%T_Check` column serves as an inclusion flag indicating which benchmark holdings pass a materiality threshold for tracking error contribution.

If you want to slim the file: you could use that same threshold to only include benchmark-only holdings that are flagged as material risk contributors. Otherwise I'll filter on my end — entirely your call.

---

## Part 2 — Field Clarifications

**7. The `OVER_WAvg` Quintile Rank — Confirming Interpretation**

I understand that `OVER_WAvg` is the overall weighted-average quintile rank (1–5 scale), and the sub-factor scores (`REV_WAvg`, `VAL_WAvg`, `QUAL_WAvg`, `MOM_WAvg`, `STAB_WAvg`) are the individual factor quintile ranks that feed into it.

The portfolio holdings skew heavily toward Q1 (about 56% across all strategies), which makes sense — the PM is selecting top-ranked stocks by design. Can you confirm:
- The scale direction: **1 = best (top quintile), 5 = worst (bottom quintile)**?
- Are the `_WAvg` versions the weighted averages and the `_Avg` versions the simple averages of the same underlying scores?
- Are there any securities where the quintile scores are not populated (i.e., would show as blank rather than a valid 1–5 value)?

---

**8. Currency — `PortfolioCurCode` Column**

The third column in every row is `PortfolioCurCode`. Can you confirm that all weights, returns, and attribution values in the file are already expressed in the portfolio's base currency? I want to make sure I'm not mixing currencies when comparing across strategies with different base currencies.

---

**9. Special Rows — `[Cash]`, `@NA`, `[Unassigned]`**

The file contains rows where Level2 is `[Cash]`, `@NA`, or `[Unassigned]`. I'm treating `[Cash]` as the portfolio's cash allocation. For the others:
- Do `@NA` rows represent holdings that could not be classified into a grouping dimension (sector, country, etc.)?
- Is `[Unassigned]` the same concept, or a different category?
- Should I include `@NA` / `[Unassigned]` weights in the totals, or are they already included in one of the named groups?

Confirming so I don't double-count or miss positions in the weight sums.

---

## Part 3 — Missing Data Requests

**10. Compounded Factor Return — Column Is Blank**

The factor attribution section has the right column header for "Compounded Factor Return" and it repeats correctly across all 5 weekly periods. However, **every value is blank** — across all 16 factors and all strategies in the sample.

Is this a configuration toggle that needs to be switched on for this export? I need factor return to complete the attribution identity: **Factor Impact = Active Exposure × Factor Return**. Without it, I can display impact but can't decompose it.

---

**11. Benchmark P/E and P/B Ratios**

I found portfolio-level Price/Earnings and Price/Book in the Fundamental Characteristics section — those are mapping correctly. What's missing is the **benchmark-side P/E and P/B** (i.e., the weighted-average P/E and P/B of the benchmark index for comparison).

If benchmark P/E and P/B are available in a separate tile, I'd appreciate adding them to the export. Without them the valuation comparison card in the dashboard will show portfolio-only values with no benchmark reference.

---

**12. Hit Rate / Success Rate**

Is there a hit rate or "batting average" metric available — i.e., what percentage of active positions contributed positively to relative return over the period? I'd like this as a portfolio-level summary stat if the data exists in FactSet.

---

**12b. Sector-Level Returns for Brinson Attribution**

The dashboard is ready to display a classic Brinson attribution breakdown (Allocation / Selection / Interaction effects by sector), which is a standard PM view, but the current export doesn't include the inputs needed to compute it. We have sector-level **weights** (portfolio, benchmark, active) but no sector-level **returns**.

To enable Brinson, we'd need, per period (weekly is ideal), **three fields**:

1. `sector_port_return` — total return contribution of the portfolio holdings in each GICS sector
2. `sector_bench_return` — total return contribution of the benchmark holdings in each GICS sector
3. `bench_total_return` — the benchmark's total period return (single number, used as the baseline against which sector returns are compared)

If FactSet already produces a Brinson or BHB-style attribution report that includes these, the cleanest path would be: append one row per sector per period with columns `SECTION_PORT_RET`, `SECTION_BENCH_RET` (plus a single `TOTAL_BENCH_RET` in the summary stats section of the file).

Alternatively, holding-level period returns on every line of the holdings section (one new column `PERIOD_RETURN`) would let us aggregate up to any breakdown — sector, country, industry, custom group — and we could compute Brinson client-side. That would be more flexible and future-proof if the preference is for a single data addition rather than a new report structure.

Either path works; I can adapt the parser to whichever is easier to produce.

---

**13. Historical Monthly Data**

The sample contains one month (January 2026). For the production pull, I need as many trailing months as available — ideally 36 months — for trend analysis (trailing TE, Active Share, Beta, factor exposures over time).

Can you confirm:
- Will each month be delivered as a **separate file** in the same format?
- Or will multiple months be **concatenated into a single file** with different DATE values?
- Is the column structure guaranteed to be identical across all monthly files?

Either format works. I just need to know before Monday so the pipeline handles it correctly from the start.

---

## Part 4 — Strategy / Account Confirmation

**14. Account Code Mapping**

In the sample, I see the following account codes. Can you confirm my mapping is correct?

| Account Code in File | My Mapping | Benchmark |
|---|---|---|
| IDM | International Developed Markets | MSCI EAFE |
| ACWIXUS | International Opportunities (IOP) | MSCI ACWI ex USA |
| EM | Emerging Markets | MSCI Emerging Markets |
| ISC | International Small Cap | MSCI World ex USA Small Cap |
| SCG | Small Cap Growth | Russell 2000 Growth |
| ACWI | All Country World | MSCI ACWI |
| GSC | Global Small Cap | MSCI ACWI Small Cap |

I understand that additional accounts may be added in the future. Will the file structure and column layout remain identical for new accounts, or could new accounts have different report configurations?

---

## Part 5 — Suggestion: Run a Short Test Pull First

Before committing to the full multi-strategy, multi-month extraction on Monday, I'd recommend a small test run — one or two strategies, two months — with any configuration changes from above (date headers, security-level grouping columns, CSV quoting fix, factor return enabled). That way if something looks off, I can catch it quickly and provide feedback before the full pull runs.

---

## Summary Checklist

For quick reference, here's everything in one list:

**Structural (nice-to-have):**
- [ ] Add date labels to weekly column groups (§1)
- [ ] Add section delimiter labels between tables (§2)
- [ ] Confirm "Overall Rank" column intent in 101-col sections (§3)

**Structural (high impact):**
- [ ] Add per-holding Sector, Country, Industry, Region, Custom Group columns (§4)
- [ ] Fix CSV quoting for security names containing commas (§5)
- [ ] Confirm benchmark holdings filtering preference (§6)

**Field clarifications (required — affects data accuracy):**
- [ ] Confirm OVER_WAvg scale direction and _WAvg vs _Avg distinction (§7)
- [ ] Confirm all values are base-currency-adjusted (§8)
- [ ] Clarify `@NA` and `[Unassigned]` row meanings and weight treatment (§9)

**Missing data (if available):**
- [ ] Enable Compounded Factor Return column (§10)
- [ ] Add benchmark P/E and P/B to export (§11)
- [ ] Add Hit Rate / Batting Average metric (§12)
- [ ] Add sector-level portfolio return, benchmark return, and total benchmark return — to enable Brinson attribution (§12b). Alternative path: add a single `PERIOD_RETURN` column at the holding level.

**Logistics:**
- [ ] Confirm historical data format: separate files or concatenated (§13)
- [ ] Confirm account code mapping and future account structure (§14)
- [ ] Run test pull before Monday's full extraction (§15)

**Already working (no action needed):**
- ✅ Sectors (11 GICS L1), Countries, Regions (7), Custom Groups (8)
- ✅ Factor Exposures (16 factors, portfolio + benchmark + active)
- ✅ Factor Attribution (Compounded Impact + Cumulative Impact)
- ✅ Holdings (ticker, name, weights, quintile ranks, sub-factor scores)
- ✅ Summary Stats (TE, Active Share, Beta, Holdings count, Cash)
- ✅ Characteristics (Market Cap, P/E, P/B, ROE, FCF Yield, Div Yield, EPS Growth, Op Margin)
- ✅ Weekly History (4 of 5 weekly snapshots)
- ✅ %T (percentage of tracking error per holding)
- ✅ %S (stock-specific component of tracking error per holding)

---

Let me know if any of this raises questions. Happy to jump on a quick call before Monday if that's easier.

Thanks again — really appreciate the work getting the sample together.

Best,
Yuda
