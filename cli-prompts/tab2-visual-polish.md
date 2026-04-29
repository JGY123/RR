VISUAL POLISH PASS on ~/RR/dashboard_v7.html.

Focus on making every chart and visualization look premium and intentional:

FACTOR RISK MAP:
1. The bubble chart has a "How to read" box in bottom-left plus a dashed median line — good context. But the chart feels empty in the upper-left quadrant. Add a subtle watermark or gradient showing "Low Exposure / High Volatility = Inefficient" context
2. Factor group legend at top gets cut off ("Mar..." instead of "Market Behavior"). Use abbreviated labels: "Val-Grw" "Mkt Behav" "Prof" "Other" to fit. Set annotation font size to 8
3. Add click handler: clicking a bubble should call oDrF(factorName) — if not already done

FACTOR ATTRIBUTION RETURN IMPACT:
4. The "Net +0.50%" top bar overlaps the first factor bar when both are near the center. Move the Net annotation to x=0.95 xref=paper (right-aligned) instead of inline
5. The bar chart bars for tiny values (Growth +0.00, Leverage -0.01) are invisible. Set a minimum marker line width of 2px so every factor is at least a thin line
6. Add "Hit Rate" stat: Count periods where each factor had positive impact / total periods. Show as a small % next to each factor name (e.g., "Market Sensitivity 67%")

FACTOR RISK BUDGET DONUT:
7. Small slice labels cluster and overlap. For slices < 4% of total, use textposition:'none' and add them to a legend list below the donut instead. Keep labels on slices > 4%
8. The center text "35% factor risk" is good — also show "65% stock-specific" in smaller text below it

REDWOOD GROUPS:
9. The butterfly chart (Chart view) is basic. Either:
   A. Remove and keep Table only (simpler, data is same)
   B. Upgrade to add TE contribution bars alongside weight bars (dual-trace butterfly)
   Recommend B — add a third trace showing TE contribution in amber/orange behind the weight bars

10. Table view: Verify Groups table has summary footer (TOTAL row). If not, add it matching sector footer pattern

When done: report fixes, propose next prompt.
