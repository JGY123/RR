Visual consistency pass on ~/RR/dashboard_v7.html. Fix these 11 items:

CRITICAL TRUNCATION FIXES:
1. Hero card right-side metrics (Beta, Active, Cash) truncate on narrow viewports — add min-width or allow wrapping with smaller font at breakpoint
2. Risk tab 5 summary cards text truncated ("TOTA RISK", "FACT RISK", "IDIOS") — same issue, cards too narrow for text. Abbreviate labels: "Total TE", "Factor", "Idio", "Beta", "Active"
3. Sector title "SECTOR ACTIVE WEIGHTS" wraps awkwardly with period buttons (2M 4M 6M 12M) — move period buttons to a second row or shrink title font

GLOBAL STANDARDS:
4. Card border-radius inconsistent (8px, 10px, 12px across tiles). Search for border-radius in .card, .sum-card, .hero-risk and standardize ALL to 10px
5. Card title font-weight mixed (some 600, some 700). Standardize all .card-title to font-weight:700
6. Inter-tile gaps: reduce excessive margin/padding after country map card and after treemap card. Target 14-16px gap between cards consistently
7. Download dropdown appears on some tiles but not others. Make it consistent — keep it on data tables (sector, country, groups, region, holdings) and remove from chart-only tiles

SMALL POLISH:
8. Hero sparkline area colors barely visible with 3 data points — increase fill opacity from 0.22/0.3 to 0.35/0.45
9. Hero idio section NBIS badge needs 2px more horizontal padding
10. Holdings expanded row close animation snaps shut — add CSS transition: max-height 0.2s ease, opacity 0.15s
11. Country map brief flash when switching regions — add a loading placeholder or transition

When done: report what you fixed, propose next prompt.
