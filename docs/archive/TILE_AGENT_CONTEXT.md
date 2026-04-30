# RR Dashboard Tile Agent Context

## What This Is
You are a tile-specific agent working on the Redwood Risk (RR) portfolio analytics dashboard.
The dashboard is a single-file HTML app at `~/RR/dashboard_v7.html` (~5000 lines).
It loads FactSet portfolio attribution data and renders 25+ interactive tiles across 3 tabs.

## Tech Stack
- Single HTML file with inline CSS + JS
- Plotly.js for charts (loaded via CDN)
- No framework — vanilla JS, template literals for HTML generation
- Dark theme: `--card:#1e293b`, `--pri:#6366f1`, `--acc:#8b5cf6`, `--pos:#10b981`, `--neg:#ef4444`
- All tables auto-wired with sortTbl() (click header to sort, double-click to filter)

## Data Available Per Strategy (`cs` = current strategy object)
- `cs.hold[]` — holdings array, each has: t(ticker), n(name), sec(sector), co(country), reg(region), ind(industry), subg(group), p(port%), b(bench%), a(active%), mcr(stock-specific TE), tr(total TE%), over/rev/val/qual(rank scores), factor_contr{} (16 per-factor contributions)
- `cs.sectors[]`, `cs.countries[]`, `cs.regions[]`, `cs.groups[]` — weight tables with _tr, _mcr, _fc_total, _fc{} enriched fields
- `cs.factors[]` — factor array: n(name), a(active exposure), c(TE contrib%), dev(std dev), ret(return), imp(impact)
- `cs.chars[]` — characteristics: m(metric name), p(portfolio), b(benchmark)
- `cs.hist.sum[]` — weekly time series: d(date), te, beta, as, h, cash
- `cs.ranks[]` — quintile breakdown: r(1-5), ct(count), p(port%), a(active%)
- `cs._countryAgg`, `cs._regionAgg`, `cs._groupAgg`, `cs._sectorAgg` — pre-computed aggregations from enrichAllGroupings()

## Design Decisions (from user review sessions)
- Single number cards are fine — detail goes in drill-down popups
- All tables must be sortable (autoWireTables handles this)
- Company names preferred over tickers in charts
- Color by factor group: Value·Growth=#6366f1, Market Behavior=#a855f7, Profitability=#fb923c, Secondary=#94a3b8
- Period/time labels must be explicit (not "3Y" when only 3 weeks of data)
- The enrichAllGroupings() pattern: aggregate from holdings once, consume everywhere

## When You're Done
1. List what you changed with before/after descriptions
2. Propose 3-5 CREATIVE ideas for what could be done next on your tile
3. Generate a prompt that could be used to apply similar design/methodology improvements to OTHER tiles
4. Note any patterns or utilities you created that other tiles could reuse
