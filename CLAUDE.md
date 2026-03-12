# RR — Redwood Risk Control Panel

## Project Scope
Single-file portfolio risk analysis and visualization dashboard. Monitors investment strategies, tracks risk metrics, analyzes sector/regional/country exposures, and manages factor tilts.

## Tech Stack
- Vanilla JavaScript (no framework)
- Plotly.js 2.27.0 (charting)
- html2canvas 1.4.1 (export)
- Custom CSS (dark theme)
- localStorage for configuration
- Static HTML — no build process

## Key Files
```
RR/
├── dashboard_v7.html   ← Complete dashboard (2,899 lines, all-in-one)
└── sample_data.json    ← Sample ISC strategy data
```

## Quick Start
```bash
# No build needed — just open in browser
open dashboard_v7.html
```

## Dashboard Tabs
1. **Overview** — Tracking Error, Active Share, Beta, Holdings
2. **Sectors** — Sector allocation vs. benchmark
3. **Regions** — Geographic exposure analysis
4. **Countries** — Country-level positioning
5. **Holdings** — Individual stock details with ratings
6. **Factors** — Factor exposure and contribution
7. **Risk** — Risk decomposition, factor correlations, time-series

## Data Format
Expects JSON with: `strategies[]`, `sum` (summary metrics), `sectors/regions/countries[]`, `factors[]`, `hold[]` (holdings)

## Features
- Multi-strategy support (IDM, IOP, EM, ISC)
- FactSet API integration for live data
- Email snapshot generation
- Right-click context menu for cell values
- Responsive grid layouts

## Cross-Project Reference
- Shared patterns: ~/orginize/knowledge/patterns.md
- Master registry: ~/orginize/CLAUDE.md

## GitHub
- Repo: JGY123/RR
- Push requires: default JGY123 account
