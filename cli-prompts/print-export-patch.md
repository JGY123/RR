# Print / Export Report Mode

## What it does
A "Report" button in the header that generates a clean, printable summary of the current strategy. Opens in a new window or print dialog with optimized layout for PDF/paper.

## Trigger
The "Report" button already exists in the header. Wire it to generate a clean report.

## Report content (single-page summary):

### Section 1: Header
- Strategy name, benchmark, report date
- Generated timestamp

### Section 2: Risk Summary (one row)
- TE, Active Share, Beta, Cash, Holdings count, Specific/Factor split
- All from cs.sum

### Section 3: Key Insights (from exec summary)
- 3-4 auto-generated bullet points
- Same as the Weekly Insights card

### Section 4: Sector Allocation (compact table)
- Sector | Port% | Bench% | Active | TE Contrib — no ORVQ (too wide for print)
- Sorted by TE contribution

### Section 5: Top 10 Holdings (compact table)
- Ticker | Name | Sector | Port% | Active | TE% | Rank
- Sorted by TE contribution

### Section 6: Factor Profile (compact)
- Style factors only (12 rows): Factor | Exposure | TE% | Return | Impact
- Sorted by TE%

### Section 7: Country Allocation (top 10)
- Country | Port% | Active | TE%

## Print CSS:
```css
@media print {
  body { background: white !important; color: black !important; }
  .header, .tabs, .qnav, #riskAlerts, .toggle-btn, .export-btn, .search-box,
  .dl-wrap, .dl-drop, button:not(.print-keep) { display: none !important; }
  .card { break-inside: avoid; border: 1px solid #ddd !important; background: white !important; }
  .hero-risk { background: #f8f9fa !important; }
  table { font-size: 10px; }
  th, td { padding: 2px 6px; border-bottom: 1px solid #e5e7eb; }
}
```

## Implementation
`openReport()` function that:
1. Generates HTML string with the 7 sections
2. Opens a new window with just the report content + print CSS
3. Auto-triggers `window.print()` after render
