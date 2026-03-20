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
├── dashboard_v7.html        ← Complete dashboard (2,899 lines, all-in-one)
├── factset_parser.py        ← CSV → JSON transformer (714 lines, handles all 7 strategies)
├── factset_team_email.md    ← Email to FactSet team with questions/requests
├── factset_extraction_notes.md ← Detailed technical extraction notes
└── sample_data.json         ← Sample ISC strategy data (old format)
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
- Multi-strategy support (IDM, IOP, EM, ISC, SCG, ACWI, GSC — 7 total)
- FactSet Portfolio Attribution CSV ingestion via factset_parser.py
- Email snapshot generation
- Right-click context menu for cell values
- Responsive grid layouts

## FactSet CSV Field Definitions (CONFIRMED)
- `%T` = Percentage of tracking error — each holding's % contribution to total portfolio TE (sums to ~100%)
- `%S` = Stock-specific component — the stock-specific portion of that holding's tracking error
- `%T_Check` = Inclusion flag for benchmark holdings — signals which BM-only holdings pass the materiality threshold for TE contribution. At portfolio "Data" row level, this is Active Share.
- `OVER_WAvg` = Overall weighted-average quintile rank (1=best, 5=worst). Portfolio holdings skew toward Q1 (~56%) because PM selects top-ranked stocks by design.
- `REV_WAvg, VAL_WAvg, QUAL_WAvg` = Primary sub-factor quintile ranks (Revision, Value, Quality)
- `MOM_WAvg, STAB_WAvg` = Secondary sub-factor quintile ranks (Momentum, Stability) — less used but available
- `_WAvg` = weighted average scores; `_Avg` = simple average scores (both present in each group)
- `Overall Rank` = Extra column in 101-col holdings sections only (position 5 in each 19-col group). Dropped during parsing to restore standard 18-col layout.

## Strategy Account Mapping
| File Code | Dashboard ID | Full Name | Benchmark |
|-----------|-------------|-----------|-----------|
| IDM | IDM | International Developed Markets | MSCI EAFE |
| ACWIXUS | IOP | International Opportunities | MSCI ACWI ex USA |
| EM | EM | Emerging Markets | MSCI Emerging Markets |
| ISC | ISC | International Small Cap | MSCI World ex USA Small Cap |
| SCG | SCG | Small Cap Growth | Russell 2000 Growth |
| ACWI | ACWI | All Country World | MSCI ACWI |
| GSC | GSC | Global Small Cap | MSCI ACWI Small Cap |
More accounts expected in future — same file structure.

## CSV Column Schemas (from factset_parser.py)
- 96-col: 6 prefix + 5 groups × 18 metrics (sector/country/region/group aggregates)
- 101-col: 6 prefix + 5 groups × 19 metrics (holdings — has Overall Rank at position 5)
- 42-col: Portfolio stats section (TE, Beta, Active Share, fundamentals)
- 9-col: Factor exposure section
- 31-col: Factor attribution section (5 periods × 5 cols + prefix)

## Pending from FactSet (awaiting response)
- Compounded Factor Return column (present but blank)
- Benchmark P/E and P/B
- Per-holding sector/country/industry/region columns
- CSV quoting fix for names with commas
- Hit rate / batting average metric
- Historical monthly data format (separate files or concatenated)
- Date labels on weekly column groups
- Clarification on @NA and [Unassigned] rows
- Confirmation of OVER_WAvg scale direction and _WAvg vs _Avg

## Dedicated Agent
This project has a **full-time virtual specialist**: `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`
- 96% confidence — highest in the roster
- Contains: every field definition, column position, strategy mapping, edge case, pending FactSet item
- Include the agent file as context at the start of any RR session for maximum accuracy
- After significant RR work, update the agent file with new learnings

## Cross-Project Reference
- Shared patterns: ~/orginize/knowledge/patterns.md
- Master registry: ~/orginize/CLAUDE.md

## GitHub
- Repo: JGY123/RR
- Push requires: default JGY123 account
