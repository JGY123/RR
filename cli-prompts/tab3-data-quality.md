DATA QUALITY AND CONTENT POLISH on ~/RR/dashboard_v7.html.

CHARACTERISTICS FIXES:
1. CHR_GROUPS classification: Market Cap is in "OTHER" but should be in "Size and Concentration". EPS Revisions (3M and 6M) are in "OTHER" but should be in "Growth". Fix the keyword arrays in the CHR_GROUPS const — add 'market cap' and 'capitalization' to the size group keys, and 'eps revisions' and 'revisions' to the growth group keys
2. Long metric names overflow their cells: "Axioma- Historical Beta", "EPS Growth - Hist. 3Yr". Create an abbreviation map: {"Axioma- Historical Beta":"Historical Beta", "Axioma- Predicted Beta to Benchmark":"Predicted Beta", "Port. Ending Active Share":"Active Share", "Port. MPT Beta":"MPT Beta", "EPS Growth - Hist. 3Yr":"EPS Growth 3Y", "EPS Growth - Est. 3-5Yr":"EPS Growth 5Y Est", "3M EPS Revisions - FY1":"3M EPS Rev", "6M EPS Revisions - FY1":"6M EPS Rev", "FCF Yield - NTM":"FCF Yield", "Dividend Yield - Annual":"Div Yield", "ROE - NTM":"ROE", "Operating Margin - NTM":"Op Margin"}. Apply in rChr() before rendering

HOLDINGS TAB:
3. Quant Ranks table columns get cut off. Abbreviate headers: "TE%" to "TE", "Stock" to "Stk", "Factor" to "Fac". Also reduce font-size on those 3 cells to 10px
4. Unowned Risk Contributors has only 1 row — add a contextual message below: "Minimal unowned risk — only 1 benchmark-only name has material TE contribution" when row count is under 3
5. Redwood Groups table: verify it has a summary TOTAL footer row matching the sector pattern. If missing, add it (sum Port%, Bench%, Active%, TE%, Stock%, Factor%)

RISK TAB:
6. Risk tab 5 summary cards text is truncated ("TOTA RISK" etc). The cards use a 5-column grid that's too narrow. Fix: change the card labels to shorter text — "Total TE" / "Factor" / "Idio" / "Beta" / "Active". Search for the risk tab rRisk() function where these are defined
7. TE Stacked Area: verify the WoW +0.14 badge is styled correctly (should be red for rising risk, green for falling). Also verify clicking a data point loads that week

SCATTER:
8. Sector filter "Spotlight" chips overflow horizontally. Fix: add flex-wrap:wrap to the chips container, or abbreviate long names: "Comm Services" instead of "Communication Services", "Cons Disc" instead of "Consumer Discretionary"

When done: report fixes, propose next prompt.
