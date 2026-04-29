# Responsive + Tablet/Mobile Polish

## What it does
Make the dashboard usable on iPad (1024px) and decent on phone (375px). Currently it works on desktop only — tables overflow, charts are too wide, hero card truncates.

## Breakpoint strategy:
- Desktop (>1200px): current layout, all features
- Tablet (768-1200px): stack g2 grids, reduce chart heights, abbreviate table headers
- Mobile (<768px): single column, simplified hero card, card view default for holdings

## Key fixes by breakpoint:

### Tablet (768-1200px):
```css
@media(max-width:1200px){
  .hero-risk .metrics-row { flex-wrap:wrap; }
  .hero-risk .secondary-metrics { flex-wrap:wrap; gap:10px; }
  .grid.g2 { grid-template-columns:1fr; }
  #cardSectors .sec-risk-callout { flex-wrap:wrap; }
  .qnav { display:none; }
}
```

### Mobile (<768px):
```css
@media(max-width:768px){
  .hero-risk { padding:12px; }
  .hero-risk .te-number { font-size:28px; }
  .hero-risk .secondary-metrics { display:none; } /* Beta/AS/Cash hidden, in drill */
  #tab-exposures .card { margin-bottom:10px; }
  table { font-size:10px; }
  th, td { padding:3px 4px; }
  /* Force card view on holdings */
  #holdViewTable { display:none; }
}
```

## Hero card mobile version:
Show only: TE number + Specific% + Factor% + sparkline
Hide: Beta, Active Share, Cash (accessible via drill-down)
Reduce font sizes by 20%

## Table mobile strategy:
- Hide ORVQ columns by default on <900px
- Abbreviate all headers to 2-3 chars
- Sticky first column (name/sector) with horizontal scroll for the rest

## Chart mobile strategy:
- Reduce all chart heights by 30%
- Bubble chart: hide text labels, show on hover only
- Country map: start in EU zoom (smaller projection works better)
- Treemap: increase to full-width, remove side margins
