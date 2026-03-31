# RR Data Directory

## Structure
```
data/
├── latest.json          ← Dashboard-optimized (lean, current week + summary history)
├── full/                ← Complete parsed data (every holding, every week, nothing discarded)
│   ├── 2026-03-28.json  ← Full parse output by date
│   ├── 2026-04-04.json
│   └── ...
├── archive/             ← Raw CSV files preserved
│   ├── 2026-03-28.csv
│   └── ...
└── README.md
```

## Workflow
1. New CSV arrives from FactSet
2. Parser runs twice:
   - `factset_parser_v2.py input.csv data/full/YYYY-MM-DD.json --full`  (keeps EVERYTHING)
   - `factset_parser_v2.py input.csv data/latest.json`                   (lean for dashboard)
3. Raw CSV archived: `cp input.csv data/archive/YYYY-MM-DD.csv`
4. Dashboard auto-loads data/latest.json

## What "full" includes that "lean" discards:
- Every holding for EVERY week (not just current week)
- Every sector/country/region/group breakdown per week
- All factor scores per holding per week
- Raw quintile distributions
- All 5 weekly groups (not just the latest)
