---
slug: rr
name: Redwood Risk
path: ~/RR/
github: JGY123/RR
account: JGY123
priority: P1
category: Analytics
techStack:
  - JavaScript
  - Plotly
  - Python
  - FactSet
description: Portfolio risk analytics dashboard for Redwood Investments.
launchCmd: open ~/RR/dashboard_v7.html
launchLabel: Open Dashboard
---
# RR — Redwood Risk Control Panel

## ⚠️ MANDATORY: READ THE SPECIALIST AGENT FIRST
**Before making ANY changes to this project, read the Risk Reports Specialist agent file:**
```
cat ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md
```
**This file contains every field definition, column position, strategy mapping, PM preference, and known edge case. Working without it leads to field mapping errors and broken data. This is not optional.**

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
├── dashboard_v7.html        ← Complete dashboard (~3,320 lines, all-in-one)
├── factset_parser.py        ← CSV → JSON transformer (PARSER_VERSION="1.1.0", FORMAT_VERSION="3.0")
├── test_parser.py           ← pytest suite (89 tests: unit + integration + edge case, all passing)
├── load_data.sh             ← Parse CSV and open dashboard (Usage: ./load_data.sh [file.csv])
├── factset_team_email.md    ← Email to FactSet team with questions/requests
├── factset_extraction_notes.md ← Detailed technical extraction notes
└── sample_data.json         ← Sample ISC strategy data (old format)
```

## Quick Start
```bash
# Parse a FactSet CSV export and open the dashboard
./load_data.sh ~/Downloads/factset_export.csv

# Or just open the dashboard (load JSON via drag-drop)
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

## Data Format (FORMAT_VERSION 3.0)
Per-strategy JSON structure:
```
strategy.sum            ← Latest-week summary (te, as, beta, h, bh, sr, cash, ...)
strategy.hist.summary   ← ALL weeks: [{d, te, as, beta, h, sr}, ...]
strategy.hist.sec       ← Monthly sector snapshots: {SectorName: [{d, p, b, a}, ...]}
strategy.hist.fac       ← Factor exposure history: {FactorName: [{d, e, bm}, ...]}
strategy.available_dates ← Sorted list of all weekly dates (from hist.summary)
strategy.current_date   ← Latest available date (= available_dates[-1])
```

## Two-Layer History Architecture
**Critical design principle** — keeps the JSON fast for 3-year files:
- **Summary layer** (tiny): `hist.summary` always loaded — all 144+ weekly entries, only TE/AS/Beta/Holdings. Powers week selector and time series charts.
- **Detail layer** (large): `hold[]`, `sectors[]`, `countries[]`, `regions[]`, `factors[]` — only for the current/selected week. Never duplicated across weeks.
- **Sector history** (monthly): `hist.sec` stores monthly sector weights for trend views.
- Week selector shows historical summary stats (TE/AS/Beta/Holdings) but holdings/sectors always reflect the latest data.

## Multi-Month Detection (30% threshold)
FactSet CSVs may contain multiple report dates. Dates with row count ≥ 30% of the max are "main dates" (holdings/sectors, ~14k rows/month); the rest are "factor dates" (~50-1300 rows). This works for single-month and 3-year files alike.

## Features
- Multi-strategy support (IDM, IOP, EM, ISC, SCG, ACWI, GSC — 7 total)
- FactSet Portfolio Attribution CSV ingestion via factset_parser.py (supports multi-year files)
- Week selector in header (‹ date ›) — select any historical week from `available_dates`
- Range buttons (3M|6M|1Y|3Y|All) on all time series drill charts
- Historical week banner (amber) when viewing a past week
- Email snapshot generation (with holdings, factor tilts, sector OW/UW tables)
- Copy Summary button (formatted text to clipboard)
- Export All Holdings CSV (complete holdings list)
- Right-click context menu for cell values
- Responsive grid layouts
- Tab count badges (Holdings: equity count, Attribution: factor count)
- Report date from JSON (`report_date` YYYYMMDD field)
- Region disclaimer when coverage < 50%
- Sector heatmap comparison across all 7 strategies
- Historical Trends mini-charts in Risk tab (TE, Active Share, Beta, Holdings)
- Factor exposure sparklines (inline SVG)

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

**Two-file model split** (confirmed 2026-04-28 by user during sample-3 review):
- **Worldwide risk model** file → 6 international strategies, larger factor set including Currency, Country, Exchange Rate Sensitivity macro factors.
- **Domestic risk model** file → SCG + Alger accounts (US-only), smaller factor set (no FX/country macros). Will land in a separate file with its own column structure.

The parser is header-driven and adapts to factor-list differences automatically. Verifier classifies missing factors as PARTIAL not FAIL when in domestic mode.

### Worldwide-model accounts (current 6)
| File Code | Dashboard ID | Full Name | Benchmark |
|-----------|-------------|-----------|-----------|
| IDM | IDM | International Developed Markets | MSCI EAFE |
| ACWIXUS | IOP | International Opportunities | MSCI ACWI ex USA |
| EM | EM | Emerging Markets | MSCI Emerging Markets |
| ISC | ISC | International Small Cap | MSCI World ex USA Small Cap |
| ACWI | ACWI | All Country World | MSCI ACWI |
| GSC | GSC | Global Small Cap | MSCI ACWI Small Cap |

### Domestic-model accounts (SCG + Alger, separate file forthcoming)
| File Code | Dashboard ID | Full Name | Benchmark | Notes |
|-----------|-------------|-----------|-----------|-------|
| SCG | SCG | Small Cap Growth | Russell 2000 Growth | Was in worldwide file; moved to domestic per 2026-04-28 user direction |
| (alger accounts) | TBD | (user to provide list + descriptions) | (TBD) | Domestic risk model |

When the domestic file lands: run `./load_data.sh <file.csv>` → verifier auto-runs → schema fingerprint will flag drift → user deletes baseline to acknowledge new model shape.

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
- Date labels on weekly column groups
- Clarification on @NA and [Unassigned] rows
- Confirmation of OVER_WAvg scale direction and _WAvg vs _Avg
- **Resolved**: Multi-year file support is ready — send a 3-year weekly file when available

## Dedicated Agent
This project has a **full-time virtual specialist**: `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`
- 96% confidence — highest in the roster
- Contains: every field definition, column position, strategy mapping, edge case, pending FactSet item
- Include the agent file as context at the start of any RR session for maximum accuracy
- After significant RR work, update the agent file with new learnings

## Data Integrity Specialist (cross-project, born from RR crisis 2026-04-27)
**MANDATORY** invocation before any change that touches the data layer (parser, normalize, render of numeric values, localStorage, cache):
`~/projects/apps/ai-talent-agency/agents/data-integrity-specialist.md`
- Audits for fabrication, drift, silent corruption — the patterns that produced the April 2026 crisis
- 8 RED anti-patterns auto-flagged: hardcoded column positions, multiple parsers for the same input, normalize() synthesis without markers, hardcoded numeric fallbacks, localStorage-as-data, missing integrity assertion, fabricated dates, tooltips without source paths
- Always invoke when user reports "wacky number"

## Critical Lessons (READ BEFORE TOUCHING DATA LAYER)
- `~/RR/LESSONS_LEARNED.md` — the story of the April 2026 data-integrity crisis + the patterns that prevent it
- `~/RR/SOURCES.md` — per-cell provenance index; UPDATE when render code changes
- `~/RR/FACTSET_FEEDBACK.md` — CSV-side issues to relay to FactSet; never silently work around via fabrication
- `~/RR/HISTORY_PERSISTENCE.md` — append-only history architecture (B114 backlog)
- `~/RR/MARATHON_PROTOCOL.md` — per-tile review protocol with data-first ordering

## Hard rules (anti-fabrication policy, established 2026-04-27)
1. **CSV in browser = error.** `parseFactSetCSV()` throws. User runs `./load_data.sh`. Single-source-of-truth pipeline only.
2. **`normalize()` is rename-only.** Any new "if X is null, compute Y" patch must instead: (a) leave it null, OR (b) compute it AND add a `_X_synth=true` marker AND add a render-side ᵉ badge AND document in SOURCES.md.
3. **localStorage is for preferences only.** Never cache data. Every page load wipes `rr_*` except `PREFS_KEY`.
4. **Every numeric cell has provenance.** SOURCES.md is the index.
5. **Integrity assertion runs on every load.** `_b115AssertIntegrity()` catches drift in console.
6. **CSV format shift = audit every parser path.** Python parser is header-driven (adapts); ALL JS-side paths get re-audited or deleted.

## Pre-flight checks before risky edits
Two scripts protect against the categories of failures that escalated in past sessions:

```bash
./smoke_test.sh           # ~1.5s — script-syntax bombs, missing render fns, schema drift, JSON validity
./smoke_test.sh --quick   # skip pytest (saves ~10s)
python3 verify_factset.py # ~3s — 22+ pass/fail checks against every FactSet ask + schema fingerprint
```

`verify_factset.py` runs automatically inside `load_data.sh` and writes its output to `last_verify_report.log`. Schema fingerprint at `~/RR/.schema_fingerprint.json` — delete to acknowledge an intentional CSV format change.

`smoke_test.sh` should be run before any risky multi-file edit. Catches:
- Backslash-bomb-style template-literal parse failures (one such regression cost ~1h on 4/27)
- Missing critical render functions (rWt, rCountryTable, etc.)
- Schema fingerprint drift since the last good baseline
- Missing strategies in latest_data.json

## Cross-Project Reference
- Shared patterns: ~/orginize/knowledge/patterns.md
- Master registry: ~/orginize/CLAUDE.md

## GitHub
- Repo: JGY123/RR
- Push requires: default JGY123 account
