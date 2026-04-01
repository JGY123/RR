# FactSet Call Notes — Follow-up Questions
**For call: April 2, 2026 (morning)**

## Questions to Ask (in addition to the email sent April 1)

### 18 Style Snapshot — Compounding Methodology
"For the Cumulative Factor Impact column in the 18 Style Snapshot: is this computed by compounding the weekly figures together (week-over-week), or does it go back to the underlying daily returns and compound through all individual days from the start date? The distinction matters because with 20 years of history, we'll need to compute attribution for arbitrary sub-periods (e.g., 2020-2022 only), and we need to know whether chaining weekly figures gives the same result as the true daily-compounded path."

Context for us: 0.03 = 0.03% = 3 bps. The weekly figure is already compounded from daily returns within that week. The question is only about how the cumulative chains those weeks.

### If Daily Compounding
If the cumulative uses daily returns, then our sub-period computation from weekly figures will have small rounding vs the true daily chain. We'd want to understand the magnitude of that drift over a 20-year window. Or ideally, get daily-frequency data for attribution (may not be feasible given file size).

### If Weekly Compounding
If cumulative = (1+w1)(1+w2)...(1+wN) - 1 using weekly figures, then we can exactly reproduce any sub-period by selecting the relevant weeks and compounding them. This is the simpler case.

## Other Call Topics
- Walk through the email items — prioritize Security completeness (1A, 1B)
- Overall rank table expand/collapse issue — quick fix?
- Timeline for the expanded run
- Confirm 20-year history is feasible with the requested additions
