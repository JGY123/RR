---
name: factset-parser
description: "Load FactSet CSV parsing domain knowledge when touching ~/RR/factset_parser.py, ~/RR/test_parser.py, or any FactSet CSV (~/Downloads/*.csv). Triggers when the user says 'parse a new CSV', 'add a column to the parser', 'fix a parser bug', 'handle a new account', 'ingest a new FactSet file', or mentions CSV schemas (42-col / 96-col / 101-col / 9-col / 31-col), the 30% multi-month threshold, comma-in-name repair, or PARSER_VERSION/FORMAT_VERSION. Points Claude at the parser engineer specialist file plus the quick-reference below. Scoped to the RR data-ingestion layer only — dashboard work routes to the risk-reports skill instead."
---

# FactSet Parser — Ingestion Context Loader

Auto-fires when touching the RR data-ingestion layer: `factset_parser.py`, `test_parser.py`, `load_data.sh`, or any FactSet CSV. Does **not** fire on dashboard work — that's `risk-reports` skill territory.

## Mandatory first step

Before editing the parser, read the specialist file:

```bash
cat ~/projects/apps/ai-talent-agency/agents/factset-parser-engineer.md
```

586-line persona covering:
- Every CSV section type and its column layout
- Every column index mapped to its semantic meaning
- Every detected edge case (comma-in-name, @NA rows, [Unassigned], empty weekly columns)
- Encoding fallback chain and quoting quirks
- Multi-month 30% threshold detection
- Append/merge workflow
- Test-suite architecture (89 tests, all passing)

## Quick-reference

### Section types (identify by column 0)

**Horizontal sections** (5 weekly groups × 19 cols each):
- Sector Weights, Country, Region, Industry, Group
- Overall / REV / VAL / QUAL / MOM / STAB (quintile distributions)

**Security (Holdings)** — same horizontal shape but 24-col groups (extra grouping cols 8-12: Redwood GICS Sector, Region1, Country, Industry Rollup, RWOOD_SUBGROUP)

**Vertical sections** (one row per date):
- Portfolio Characteristics (TE, Beta, AS, fundamentals)
- RiskM (Total/BM Risk, P/E, P/B, pct_specific, pct_factor, per-factor risk)
- 18 Style Snapshot (factor exposure/return/impact/stddev)

### Column-count quick ID

| Cols | Section type | Notes |
|---|---|---|
| 42 | Portfolio characteristics | Vertical |
| 96 | Group aggregates | 6 prefix + 5 × 18 metrics |
| 101 | Holdings | 6 prefix + 5 × 19 (Overall Rank extra at pos 5) |
| 9 | Factor exposure | Vertical per-factor |
| 31 | Factor attribution | 5 periods × 5 cols + prefix |

### Multi-month detection (30% threshold)

Count rows per unique date. Dates with row count ≥ 30% of max = "main dates" (holdings/sectors, ~14k rows). Others = "factor dates" (~50-1300 rows). Works on single-month and 3-year files. Do NOT hardcode month count.

### Two-layer output (FORMAT_VERSION 3.0)

Never duplicate detail across weeks. One normalization per parse:

```python
strategy.sum            # latest week only
strategy.hist.summary   # [{d, te, as, beta, h, sr}, ...] — all weeks, tiny
strategy.hist.sec       # {SectorName: [{d, p, b, a}, ...]} — monthly
strategy.hist.fac       # {FactorName: [{d, e, bm}, ...]} — all weeks
strategy.available_dates  # sorted
strategy.current_date     # = available_dates[-1]
```

### Encoding fallback chain

```python
for enc in ('utf-8-sig', 'utf-8', 'latin-1', 'cp1252'):
    try:
        return open(path, encoding=enc)
    except UnicodeDecodeError:
        continue
```

### Comma-in-name repair

FactSet unquoted CSVs with commas inside security names shift all subsequent columns. Detection + repair rule lives in the parser. **Do not touch without reading the current implementation and the test regression cases** (`TestRegressionCommaRepair`).

### Account mapping (file code → dashboard ID)

| File | Dashboard | Benchmark |
|---|---|---|
| IDM | IDM | MSCI EAFE |
| ACWIXUS | IOP | MSCI ACWI ex USA |
| EM | EM | MSCI EM |
| ISC | ISC | MSCI World ex USA Small Cap |
| SCG | SCG | Russell 2000 Growth |
| ACWI | ACWI | MSCI ACWI |
| GSC | GSC | MSCI ACWI Small Cap |

New accounts expected — structure unchanged. Fall back to "unknown account → skip with warning," never crash.

## Safety rules

1. **PARSER_VERSION bump** whenever behavior changes. `FORMAT_VERSION` bump only when output JSON shape changes.
2. **Never commit** a parser change without running `pytest test_parser.py` first — 89 tests, all must pass.
3. **Add a regression test** for any bug you fix.
4. **Never hardcode dates, account codes, or factor names** — read them from the CSV.
5. **Trust `Period Start Date`** — never infer date from row position or order.
6. **When a new column appears in FactSet output**, add it to the column layout docs in the specialist file, bump PARSER_VERSION, write a test.

## Pending from FactSet

Check the specialist file for the latest list — items arrive and get resolved. Currently:
- Compounded Factor Return (column exists, empty)
- Benchmark P/E and P/B (missing)
- Per-holding sector/country/industry (missing — dashboard uses Redwood overrides)
- CSV quoting fix for names with commas
- Hit rate / batting average
- Date labels on weekly column groups
- `@NA` and `[Unassigned]` semantics

When you add a new blocker here, also add it to `~/RR/factset_team_email.md` and `~/RR/CLAUDE.md`.

## When to escalate

- **Dashboard rendering** of a new field → switch to `risk-reports` skill (don't modify dashboard from this context)
- **New FactSet email needed** → draft into `~/RR/factset_team_email.md`
- **Tests failing that aren't parser bugs** → investigate, don't silence
- **Risky rewrite of parsing logic** → `regression-checkpoint` skill auto-fires

## Why this skill exists

Project-scoped Layer 2 promotion of `factset-parser-engineer` persona. The persona is deep on column layouts; this skill keeps the hottest-path reference inline and directs to the full spec for anything else.

Tight scope is on purpose: RR has TWO distinct bodies of knowledge — ingestion (this skill) and display (`risk-reports` skill). Keeping them separate prevents ingestion edits from drifting into display assumptions and vice versa.

## Companion skills

- `risk-reports` — dashboard-side domain knowledge (sibling skill, never load together for single edits)
- `regression-checkpoint` — tag before touching the parser
- `defensive-data-filtering` — applies to the JSON output as consumed by the dashboard
