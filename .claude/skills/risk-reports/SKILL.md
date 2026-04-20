---
name: risk-reports
description: "Load RR-specific (Redwood Risk) domain knowledge when working on the Redwood Risk Control Panel — dashboard_v7.html, factset_parser.py, any *.csv from FactSet, any RR tile (cardSectors, cardHoldings, cardFactors, etc.), any RR strategy (IDM, IOP, EM, ISC, SCG, ACWI, GSC), or any mention of tracking error, active share, FactSet fields like %T / %S / OVER_WAvg / REV_WAvg. Points Claude at the specialist agent file (96% confidence) and CLAUDE.md before making changes. Auto-fires inside ~/RR/. Prevents the #1 RR failure mode: wrong field mapping because the specialist file wasn't consulted."
---

# RR — Risk Reports Context Loader

Auto-fires when working inside `~/RR/` or when conversation context mentions Redwood Risk / FactSet / any RR strategy / dashboard_v7.html / factset_parser.py.

## Mandatory first step

**Before making ANY change to RR code**, read the specialist agent file:

```bash
cat ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md
```

It's 586 lines containing:
- Every FactSet field definition (%T, %S, %T_Check, OVER_WAvg, _WAvg vs _Avg)
- Every column position in each of the CSV schemas (42-col / 96-col / 101-col / 9-col / 31-col)
- Every strategy mapping (file code → dashboard ID → benchmark)
- Every PM preference (sort orders, default views, color semantics)
- Every known edge case (CASH_USD handling, multi-month 30% threshold, comma-in-name repair)
- Every pending FactSet item (what's blocked on them, what arrived)

Then skim `~/RR/CLAUDE.md` for the project scope + file layout.

**This is not optional.** The #1 failure mode on RR is wrong field mapping from skipping this read.

## Quick-reference (hot path)

For fast-recall items that don't need the full specialist file:

### The 7 strategies
| File | Dashboard | Name | Benchmark |
|---|---|---|---|
| IDM | IDM | International Developed Markets | MSCI EAFE |
| ACWIXUS | IOP | International Opportunities | MSCI ACWI ex USA |
| EM | EM | Emerging Markets | MSCI EM |
| ISC | ISC | International Small Cap | MSCI World ex USA Small Cap |
| SCG | SCG | Small Cap Growth | Russell 2000 Growth |
| ACWI | ACWI | All Country World | MSCI ACWI |
| GSC | GSC | Global Small Cap | MSCI ACWI Small Cap |

### Core field cheat-sheet
- `%T` — holding's % contribution to total portfolio TE (sums ~100%)
- `%S` — stock-specific component of that holding's TE (subset of %T)
- `%T_Check` — inclusion flag for benchmark holdings; at Data-row level = Active Share
- `OVER_WAvg` — overall weighted quintile rank, **1=best, 5=worst**
- `_WAvg` vs `_Avg` — weighted average vs simple average (both present per group)
- Q1 distribution ~55.6% across strategies is **correct** for actively managed portfolios (don't flag as wrong)

### Data shape (FORMAT_VERSION 3.0)
```
strategy.sum            ← latest week summary
strategy.hist.summary   ← all weeks: [{d, te, as, beta, h, sr}, ...]
strategy.hist.sec       ← monthly sector snapshots
strategy.hist.fac       ← factor exposure history
strategy.available_dates
strategy.current_date
```

Two-layer design: summary layer (tiny, all weeks) + detail layer (large, current week only). Do **not** duplicate detail across weeks.

### Multi-month detection
30% threshold on row count per date → dates ≥ 30% of max = "main dates" (holdings/sectors ~14k rows); others = "factor dates" (~50-1300 rows). Works single-month and 3-year.

## Safety rules for RR edits

1. **Consult specialist agent file first** (the one referenced above)
2. **Single file, high blast radius** — dashboard_v7.html is ~6,100 lines. Use the `regression-checkpoint` skill (tag before every edit)
3. **Plotly category-axis trap** — ticker strings like `"688910"` must have `type: 'category'` on the axis (see `defensive-data-filtering` skill)
4. **THEME() resolver** — don't hardcode hex colors in charts; use `THEME()` helper (converts CSS vars at runtime for dark/light)
5. **Field names are position-sensitive** in CSV parsing — adding a column shifts everything after. Re-check `factset_parser.py` column offsets after any schema change from FactSet
6. **Rely on `available_dates` + `current_date`** — never assume "latest" from the raw CSV order

## When to escalate to another resource

- **Tile-level audit requested** → spawn `tile-audit` subagent
- **"Where did feature X go?"** → spawn `gap-discovery` or `feature-reconciliation` subagent
- **End of session on RR** → `session-continuity` skill auto-fires
- **Before a risky RR refactor** → `regression-checkpoint` skill auto-fires

## Pending from FactSet (stale check before using)

Before citing these as "blocked," re-read the specialist file — items get resolved.

- Compounded Factor Return column (present but blank)
- Benchmark P/E and P/B
- Per-holding sector/country/industry/region columns
- CSV quoting fix for names with commas
- Hit rate / batting average metric
- Date labels on weekly column groups
- Clarification on `@NA` and `[Unassigned]` rows
- Confirmation of OVER_WAvg scale direction

## Why this skill exists

Project-scoped Layer 2 promotion of the `risk-reports-specialist` persona (Layer 3). The persona is 586 lines — too heavy to inline. This skill is the **lean auto-loader**: it points Claude at the specialist file rather than duplicating it, plus the hot-path quick-reference above.

Activation rate should jump from ~manual (when user remembers to paste) to ~100% (auto-fires on any RR work).

## Companion skills (loaded via description match)

- `defensive-data-filtering` — applies to RR data consumers (isFinite, axis type, null-safe)
- `regression-checkpoint` — tag before editing dashboard_v7.html
- `session-continuity` — RR SESSION_STATE.md hygiene
