Chart and Factor section polish on ~/RR/dashboard_v7.html. Fix these 10 items:

LABEL OVERLAP FIXES:
1. Factor Risk Map legend at top: "Mar..." is cut off — should show full "Market Behavior". Ensure all 4 group names show completely or abbreviate consistently (Val-Grw | Mkt | Prof | Other)
2. Factor Risk Map: Bubbles for Leverage, Earn. Yield, Profitability cluster and overlap labels. Add textposition logic: if bubbles are within 0.15 units of each other vertically, alternate "top center" and "bottom center"
3. Factor Attribution Return Impact chart: "Net" label overlaps with "Full period" annotation — move Net to right side or add 20px vertical offset
4. Factor Attribution chart: Very thin bars for Leverage, FX Sensitivity, Volatility — add minimum bar width of 3px
5. Factor Risk Budget donut: Small slice labels overlap (Earnings Y., Profitab., Liquid., Leverag.) — use Plotly textposition outside for slices under 5% and abbreviate names

FACTOR DETAIL POLISH:
6. Factor Detail table: Non-style factors (Country, Currency, Industry, Local, Market) show dashes for TE%/12wk/Return/Impact. Visually dim these rows (opacity:0.5 or lighter text color) to distinguish from active style factors
7. Factor Detail: Profitability row has amber left border + star — this intentional factor highlighting should be documented in a tooltip on the star

CHART UPGRADES:
8. Redwood Groups butterfly chart is still basic — at minimum add TE contribution per group as bar annotation text (e.g., "GROWTH 45.1% TE" on the bar)
9. Redwood Groups table needs summary footer row (TOTAL with Port/Bench/Active sums) — same pattern as sector table footer
10. Scatter sector filter chips overflow: "Communication Services", "Consumer Discretionary" get cut off. Either wrap to 2 rows, abbreviate ("Comm Svc", "Cons Disc"), or make scrollable

When done: report what you fixed, propose next prompt.
