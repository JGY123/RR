---
name: RR Dashboard Handoff
version: v1.0
last_updated: 2026-04-21
---

# RR — Redwood Risk Dashboard · Handoff

Single source of truth for running, shipping, and extending the RR dashboard. If anything in this file conflicts with code, **the code wins and this file is stale — update it**.

---

## 1. What this is

A single-file HTML portfolio risk dashboard for Redwood Investment Management. Ingests weekly FactSet Portfolio Attribution CSVs, renders ~29 analysis tiles across 7 tabs for 7 strategies (IDM, IOP, EM, ISC, SCG, ACWI, GSC).

- **Users:** Redwood PM team (internal)
- **Deployment target:** Internal web server, first CSV preloaded, weekly appends automated later (see §7)
- **Current release:** `v1.0` (tag `v1.0`, 2026-04-20)

---

## 2. Tech stack

| Layer | Tool | Version |
|---|---|---|
| Frontend | Vanilla JS (no framework) | — |
| Charts | Plotly | 2.27.0 |
| Export | html2canvas | 1.4.1 |
| Styling | Custom CSS, dark theme | — |
| State | `localStorage` | — |
| Parser | Python 3 | `factset_parser.py` PARSER_VERSION 3.0.0, FORMAT_VERSION 4.1 |
| Parser tests | pytest | 89 tests, all passing |

Static HTML. No build step. Open file → works.

---

## 3. Quick start

```bash
# Parse a FactSet CSV and open the dashboard
./load_data.sh ~/Downloads/factset_export.csv

# Or open the dashboard directly and drag-drop a JSON
open dashboard_v7.html

# Run parser tests
pytest test_parser.py -v
```

---

## 4. File layout

```
RR/
├── dashboard_v7.html              ← ~6,500 lines, entire app
├── factset_parser.py              ← CSV → JSON transformer (v3.0.0 / format 4.1)
├── test_parser.py                 ← 89 pytest tests
├── load_data.sh                   ← parse + open
├── HANDOFF.md                     ← this file
├── CLAUDE.md                      ← AI assistant project instructions
├── sample_data.json               ← old-format sample
├── factset_team_email.md          ← open questions to FactSet
├── factset_extraction_notes.md    ← technical extraction notes
└── tile-specs/
    ├── AUDIT_LEARNINGS.md         ← cross-tile patterns + gotchas (READ FIRST during audits)
    ├── TILE_AUDIT_TEMPLATE.md     ← audit template
    ├── cardSectors-audit-*.md     ← signed-off audits
    ├── cardHoldings-audit-*.md
    └── cardCountry-audit-*.md
```

---

## 5. Data flow

```
FactSet CSV (weekly export)
    ↓
factset_parser.py — detects column schemas (96/101/42/9/31), multi-month (30% threshold),
                    maps file codes → strategy IDs (ACWIXUS→IOP, etc.)
    ↓
portfolio_data.json (FORMAT_VERSION 4.1)
    ↓
dashboard_v7.html drag-drop / fetch
    ↓
Per-strategy: strategy.sum (latest-week summary)
              strategy.hist.summary (all weeks, small)
              strategy.hist.sec (monthly sector snapshots)
              strategy.hist.fac (factor history)
              strategy.hold[] / sectors[] / countries[] / regions[] / factors[] (current week)
```

**Two-layer history:** summary layer is always loaded (tiny); detail layer is per-week and never duplicated. This keeps 3-year files fast.

---

## 6. Tile inventory (29 tiles)

| Tab | Tile | Audit status |
|---|---|---|
| Overview | cardThisWeek, cardKeyStats, cardChars, cardHoldGrowth | ☐ pending batch 1 |
| Sectors | **cardSectors**, cardSectorCompare, cardBenchOnly, cardTreemap | ✅ cardSectors (v1) |
| Regions | cardRegions, cardGroups | ☐ |
| Countries | **cardCountry** | ✅ v1 + v1.fixes |
| Holdings | **cardHoldings**, cardRating, cardMCR | ✅ cardHoldings (v1) |
| Factors | cardFacExp, cardFacButt, cardFacAttrib, cardFRB | ☐ |
| Risk | cardRiskHistTrends, cardRiskFac, cardScat, cardDrill, cardTimeSeries, cardCorr, cardAttrib | ☐ partial (sweep) |

**Gold-standard references:** `cardSectors` and `cardHoldings`. When in doubt about a tile pattern, copy those.

**Audit workflow:** spawn the `tile-audit` subagent. Every audit agent **reads `tile-specs/AUDIT_LEARNINGS.md` first** and appends cross-tile insights on exit.

---

## 7. Ingestion contract

### Current (manual)
```bash
./load_data.sh ~/Downloads/factset_export.csv
```
Produces `portfolio_data.json` and opens the dashboard. CSV must contain at least one "main date" (row count ≥ 30% of max date).

### Future (weekly automated append) — placeholder
**Not yet built.** The expected interface:

```bash
factset_parser.py --append existing.json new_week.csv → existing.json
```

**Idempotency rule:** re-running with the same CSV is a no-op. Identified by `report_date` per strategy.

**Trigger (TBD):** file-watcher on a shared drop folder, or cron polling `~/FactSetDrop/`. Decision deferred until Redwood IT confirms server layout.

**Contract for the dashboard side:** when the JSON's `report_date` changes, the "Report: ... Xd ago" badge in the header (`refreshDataStamp` at dashboard_v7.html:709) updates automatically. Badge turns amber at 8d, red at 21d (see `_thresholds.freshAmberDays` / `freshRedDays`).

---

## 8. Release procedure

Currently manual. One-command release script is a v1.1 todo.

```bash
# 1. Pre-flight
pytest test_parser.py -v                           # 89 tests must pass
git status                                         # clean working tree
git tag working.YYYYMMDD.HHMM.pre-release          # safety checkpoint

# 2. Bump version in dashboard_v7.html (header badge) and HANDOFF.md
# 3. Commit + tag
git add dashboard_v7.html factset_parser.py HANDOFF.md
git commit -m "release: vX.Y.Z — <summary>"
git tag vX.Y.Z
git push origin main --tags

# 4. Deploy (internal server — TBD, see §7)
```

---

## 9. Known gotchas

| # | Gotcha | Where |
|---|---|---|
| 1 | `_secRankMode` (Wtd/Avg/BM) is **global** — toggling in cardSectors re-renders cardCountry/cardGroups/cardRegions simultaneously. Splitting requires per-tile state vars. | rankAvg3() |
| 2 | Numeric sort breaks if `<td>` lacks `data-sv="..."`. Every numeric cell must carry it. | `sortTbl()` |
| 3 | Plotly empty-state: must `el.innerHTML = '<p>No X data</p>'`, not silent return — otherwise the prior chart persists on strategy switch. | scatDiv/treeDiv/mcrDiv/frbDiv/facButtDiv |
| 4 | `THEME().pos` / `THEME().neg` — use these for up/down colors. Hardcoded `#10b981` / `#ef4444` will desync from theme tokens. | THEME() at ~L2181 |
| 5 | **No PNG export buttons.** User removed them multiple times. CSV export only. | — |
| 6 | Strategy code mapping: `ACWIXUS` in the CSV maps to dashboard ID `IOP`. Others are 1:1. | factset_parser.py |
| 7 | 101-col holdings schema has an extra "Overall Rank" at position 5 of each 19-col group. Parser drops it to restore the standard 18-col layout. | factset_parser.py `SectionSchema` |
| 8 | Multi-month detection: dates with row count ≥ 30% of max are "main dates" (holdings/sectors). Below that are factor-only dates. | factset_parser.py |
| 9 | Subagents (tile-audit, etc.) **never edit `dashboard_v7.html` directly**. Main session serializes all edits to prevent overlapping writes on the single-file codebase. | project convention |
| 10 | After any Edit/Write, verify: `wc -l dashboard_v7.html`, `grep -c "marker"`, `git status`. Phantom-writes crisis 2026-04-16 taught us not to trust tool-success alone. | — |

---

## 10. Open questions for FactSet

Tracked in `factset_team_email.md`. Highlights:
- Compounded Factor Return column (present but blank)
- Benchmark P/E and P/B
- Per-holding sector/country/industry/region columns
- CSV quoting fix for names with commas
- Hit rate / batting average metric
- Clarification on `@NA` and `[Unassigned]` rows

---

## 11. Pointers

- **Project instructions for AI assistants:** `CLAUDE.md`
- **AI specialist agent:** `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md` (96% confidence, canonical field definitions)
- **Cross-tile patterns ledger:** `tile-specs/AUDIT_LEARNINGS.md`
- **GitHub:** `JGY123/RR` (push requires JGY123 account — `gh auth switch --user JGY123`)
