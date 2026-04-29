Holdings and Characteristics polish on ~/RR/dashboard_v7.html. Fix these 7 items:

CHARACTERISTICS:
1. Portfolio Characteristics OTHER group contains Market Cap and 3M/6M EPS Revisions — these are misclassified. Move Market Cap to Size and Concentration group and EPS Revisions to Growth group. Fix the CHR_GROUPS keyword lists (search for CHR_GROUPS const) — add market cap and capitalization to size keys and eps revisions or 3m eps or 6m eps to growth keys
2. Portfolio Characteristics tooltip icons are present — verify they show meaningful text on hover for each metric (TE, Beta, Active Share, P/E, etc.)

HOLDINGS POLISH:
3. Quant Ranks table: TE%/Stock/Factor columns hidden without horizontal scroll on narrow view. Consider making the card wider (colspan 1/-1 like country card) OR abbreviate column headers (TE instead of TE%, Stk instead of Stock, Fac instead of Factor)
4. Unowned Risk Contributors: Only 1 row (JDE Peets) looks sparse. Add a message below: Low unowned risk exposure — only 1 benchmark name contributes material tracking error if rows under 3
5. Holdings expanded row: When expanding, factor bars should slide down smoothly. Verify CSS keyframes expandDown exists and is applied to the expanded content div. If close snaps, add a collapse animation too

MINOR:
6. Holdings By Sector sort: Verify sector group headers show count + total TE% (should read like Industrials - 11 holdings - 31.4% TE)
7. Holdings Card view: Verify Group by pills (None/Sector/Country/Rank) appear and render section headers with sector TE in the headers

When done: report what you fixed, propose next prompt.
