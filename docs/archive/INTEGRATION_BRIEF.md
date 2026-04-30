# Data-Foundation Integration Brief — 2026-04-24

**Status:** Foundation prep complete. Ready for a fresh CLI thread to execute parser + dashboard changes.
**Context:** This brief lives at project root so a new session can `cat ~/RR/INTEGRATION_BRIEF.md` and have full context.
**Prerequisite reading (in order):**
1. This file.
2. `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md` (mandatory RR context per `CLAUDE.md`).
3. `CLAUDE.md` for project conventions.
4. `tile-specs/AUDIT_LEARNINGS.md` closing section ("ALL 21 TIER-1 TILES AUDITED") for the tile landscape.

---

## What the user asked for

Two new Downloads files (`ls ~/Downloads/ | head`):
- `Stocks country cueensy indusy flag exposure.xlsx` — **static** per-security country/currency/industry lookup. Doesn't change week-to-week. Must be baked ("hardcoded") into the system.
- `risk_reports_sample (5).csv` — **final CSV format** for the upcoming massive production run. Smaller sample, but adds more characteristics and (critically) a new per-security raw factor exposure table.

User intent: "make sure everything can be loaded correctly — solid foundation before the review marathon."

---

## Work already completed (ship-ready)

### ✅ `data/security_ref.json` — Excel baked to JSON

- Location: `~/RR/data/security_ref.json` (1.1 MB, committed)
- 6,390 unique securities, keyed by SEDOL
- Schema: `{by_sedol: {SEDOL: {n, ccy, country, industry, tkr, isin}}}`
- **97% coverage** of the new-format CSV's Security-section SEDOLs (13,317 of 13,722 matched via direct SEDOL or name fallback). 3% miss are mostly US stocks that weren't in the 6-strategy Excel universe — acceptable fall-through.
- The source Excel had 40 currencies + 66 industries + 52 countries as one-hot flag columns. Deduped across 6 strategies (EM, IDM, IOP, ACWI, SCG-variant, ISC) — zero ambiguity (same SEDOL → same classification every time).
- Rebuild script (if the Excel gets updated):
  ```python
  # Pattern is in the commit message for the bake commit; use same heuristics:
  # - Col 9 header row
  # - Col 1 = name; 2 = SEDOL; 4 = Ticker-Region; 5 = CUSIP; 6 = ISIN; 7+ = flag cols
  # - Classify each flag col by header: 3-letter ALLCAPS = ccy, known-country-list = country, else industry
  # - Skip rows where col 1 starts with 'Redwood ' (strategy section breaks)
  ```

### ✅ Parser tested against new CSV — mostly works

Ran `python3 factset_parser.py "risk_reports_sample (5).csv" /tmp/new_fmt_test.json`:
- Parses all 7 strategies cleanly (ACWI, IOP, EM, GSC, IDM, ISC, SCG)
- Auto-discovered schemas: `Sector Weights`, `RiskM`, `Portfolio Characteristics`, `Industry` (new section), `Region`, `Country`, `Security`, `Group`, `Overall`, `Raw Factors` (new), `REV/QUAL/VAL`, `18 Style Snapshot`
- `strategy.industries` now populated (15 rows for IDM sample) — **but dashboard doesn't render industries yet**
- `hist.fac` populated correctly (17 factor keys for IDM) ✅
- `hist.sec` / `hist.reg` still empty (existing B6 backlog — not a new-format regression)
- TE/AS/Beta/Holdings all populated for 6/7 strategies (SCG has `te=None` in this sample — probably just missing from the sample, not a format issue)
- **`Raw Factors` section is schema-discovered but silently discarded** — no downstream capture in the strategy dict. This is the main parser gap.

### ✅ Safety tag

`working.20260424.1009.pre-data-foundation` at HEAD. Before you start parser edits, tag again: `working.YYYYMMDD.HHMM.pre-data-integration`.

---

## Work the fresh thread needs to do

### Phase 1 — Parser: capture Raw Factors (P0, blocking)

The "Raw Factors" section has **13,722 rows** (1:1 with Security section). Row shape:
- col 0: `Raw Factors`
- col 1: ACCT (IDM)
- col 2: DATE (20260403)
- col 3: PortfolioCurCode
- col 4: Level (1)
- col 5: Level2 = security identifier (SEDOL/ticker, same key format as Security section col 5)
- col 6: SecurityName
- Groups of 13 cols per period: [Period Start Date, **12 factor exposure z-scores**]
- 4 periods in this sample (~monthly cadence or weekly over 4 weeks)

**Task:** In `factset_parser.py`, add a `_collect_raw_factors` hook similar to `_collect_riskm_data`. Output schema:

```python
strategy["raw_fac"] = {
    "<SEDOL>": {
        "name": "HSBC Holdings Plc",
        "e": [z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12],   # latest period's 12 values
        "hist": [
            {"d": "20260403", "e": [z1..z12]},
            {"d": "20260410", "e": [z1..z12]},
            ...
        ]
    }
}
```

**Factor order confirmation needed from user or by inspection** — the 12 values per row are factor z-scores but their labels are NOT in the CSV (the header-row columns are holdings-schema names like `OVER_WAvg` that get reinterpreted under each section's native layout). Proposed ordering based on typical Barra/Axioma style factor bundles:

```
["Market Sensitivity", "Size", "Volatility", "Momentum", "Momentum (Medium-Term)",
 "Value", "Growth", "Profitability", "Leverage", "Liquidity",
 "FX Sensitivity", "Earnings Variability"]
```

**Ask the user to confirm** before committing the ordering (or request FactSet to provide a factor-column-header mapping).

Parser deliverables:
- Bump `FORMAT_VERSION` to `"3.1"`.
- Add `_collect_raw_factors()` function.
- Add `raw_fac` to strategy output.
- Update `test_parser.py` with fixtures covering the new section (89 tests → ~95). Run `pytest test_parser.py -v` until all green.

### Phase 2 — Parser: attach security_ref enrichment (P0)

In `normalize()` (dashboard side) OR in the parser (better — do it once):

```python
# Load once at parser module load time
import json, os
SECURITY_REF = json.load(open(os.path.join(os.path.dirname(__file__), 'data', 'security_ref.json')))['by_sedol']

def enrich_holding(h):
    # h already has {t, n, sec, co (raw region), ...} from CSV
    # Look up by multiple keys
    key = h.get('t', '').upper()
    ref = SECURITY_REF.get(key) or SECURITY_REF.get(key.lstrip('0'))
    if not ref:
        # Name fallback (lowercase alphanumeric, first 30 chars)
        nname = re.sub(r'[^a-z0-9]','', (h.get('n') or '').lower())[:30]
        ref = NAME_IDX.get(nname)  # pre-built once
    if ref:
        h['country'] = ref.get('country')
        h['currency'] = ref.get('ccy')
        h['industry'] = ref.get('industry')
    return h
```

Choice — parser vs dashboard side enrichment:
- **Parser side (recommended):** adds bytes to JSON output but the enrichment logic lives with the data. JSON becomes self-describing.
- **Dashboard side:** keeps JSON small, but `normalize()` has to load `security_ref.json` separately.

Either is fine; parser-side is simpler for the dashboard and aligns with "hardcode into the system".

**Coverage note:** 97% match expected. Log the miss rate. The remaining 3% will have `country/currency/industry = null` and the dashboard must fall back to CSV-native fields (`h.sec` for sector, `h.co` raw region) — same as today.

### Phase 3 — Dashboard: tile surface for new data (P1 — sized Medium)

Three new tile opportunities that the user flagged:

#### 3a. Per-security raw factor exposure drill-down
In the stock-detail modal `oSt(ticker)`, add a new section showing the security's 12 raw factor z-scores as a horizontal bar chart — color bars by sign. Source: `strategy.raw_fac[sedol].e`. Also show a tiny sparkline of each factor over the 4 historical periods from `raw_fac[sedol].hist`. This answers: "why is this stock in the portfolio? Because it's +2σ on Momentum and +1.5σ on Profitability."

#### 3b. Risk-attribution decomposition by country / currency / industry (THE user's key ask)
New tile (proposed `cardRiskByDim`) on the Risk tab. For a given dimension (Country / Currency / Industry, toggleable), aggregate each holding's `%T` (TE contribution) using the `security_ref` lookup:

```js
// For the Currency dimension:
let byCcy = {};
cs.hold.forEach(h => {
    let ccy = h.currency || 'Unknown';
    if (!byCcy[ccy]) byCcy[ccy] = {te_contrib: 0, names: []};
    byCcy[ccy].te_contrib += (h.tr || 0);
    byCcy[ccy].names.push(h.t);
});
// Render as a sorted horizontal bar chart.
```

User literally said: "when security has 2% contribution to risk from country you will be able to using that data to map which country etc." — this is that tile.

Three bars (one per dimension Country/Ccy/Industry) in a toggleable pill group. Click a bar → drill into the list of contributing stocks. Sibling pattern to cardRiskFacTbl.

#### 3c. Portfolio raw-factor-exposure hero chart (synthesis)
Sum the raw factor exposures weighted by portfolio weight to get the portfolio's aggregate raw factor tilt. Compare to benchmark's weighted raw exposure. The *difference* is the portfolio's active factor tilt — which should match `cs.factors[].a` (already displayed in cardFacButt / cardFacDetail / cardRiskFacTbl) but now shown as a DECOMPOSITION: "this 0.8σ Momentum tilt is driven 55% by these 5 stocks". Depends on Phase 1 + 3a landing first.

#### 3d. Update industries consumer
`strategy.industries` is already populated by the parser. Nothing in the dashboard reads it yet. Since we now also have per-holding `industry` from `security_ref`, we could either:
- Render `cs.industries` as a standalone tile (parallels cardSectors at more granular level)
- OR fold it into 3b's industry-dimension drill

Recommend 3b's drill as the primary surface; keep `cs.industries` as a data-model byproduct.

### Phase 4 — Testing + verification (P0 before user review)

- Regenerate `sample_data.json` from the new CSV for dev use.
- Open `dashboard_v7.html` and load the new JSON via drag-drop. All 21 audited tiles must still render without console errors (this is the implicit regression check — we already have safety tag `tier1-audit-complete`).
- Run parser tests: `python3 -m pytest test_parser.py -v`. **⚠ Pre-existing issue:** as of 2026-04-24 the test module fails at import: `ImportError: cannot import name 'classify_row' from 'factset_parser'`. This is NOT a regression from the Batch 7 work or the new CSV — the test suite has drifted from the parser's public API. First sub-task in Phase 4: fix the test import (likely `classify_row` was renamed or became internal; look for equivalent helper and re-export, or update test imports). CLAUDE.md asserts 89 passing tests — that claim is stale.
- Spot-check a few securities in the stock modal to verify country/currency/industry enrichment landed.

### Phase 5 — Commit + tag

- Tag `data-foundation-v1` at the commit where Phase 1+2 land.
- Separate tags for each dashboard tile added: `tileaudit.cardRiskByDim.v1` etc.
- Update `SESSION_STATE.md` checkpoint log.
- Then and only then — start the review marathon.

---

## Files touched / created by this prep session

- ✅ `data/security_ref.json` (new, 1.1 MB)
- ✅ `INTEGRATION_BRIEF.md` (this file, new)
- Safety tag: `working.20260424.pre-data-foundation` (no new changes to dashboard_v7.html, parser, or tests yet)

---

## Critical path summary for the fresh thread

```
read_this_brief
→ read risk-reports-specialist.md + CLAUDE.md
→ safety tag working.YYYYMMDD.HHMM.pre-data-integration
→ Phase 1 (parser: raw_fac capture)
   → ASK USER for factor order (12 labels in positional order)
   → implement _collect_raw_factors + test fixtures
   → pytest green
→ Phase 2 (parser: security_ref enrichment hook, log coverage)
→ regenerate sample_data.json
→ commit parser changes, tag data-foundation-v1
→ Phase 3 (dashboard tiles: 3a drill, 3b cardRiskByDim, 3c synthesis)
   → one tile at a time, same tile-audit cadence as Batches 1-7 if wanted
→ browser verify all 21 prior tiles still render
→ commit, tag, push as JGY123
→ update SESSION_STATE, hand back to user for review marathon
```

## One-shot commands the fresh thread can run

```bash
# Quick verify parser still works on current production JSON
cd ~/RR && python3 factset_parser.py latest_data.json /tmp/check.json

# Run parser on new CSV
python3 factset_parser.py "/Users/ygoodman/Downloads/risk_reports_sample (5).csv" /tmp/new_fmt.json

# Compare JSON shape before/after parser changes
python3 -c "import json; d=json.load(open('/tmp/new_fmt.json')); print(sorted(d[0]['IDM'].keys()))"

# Regression baseline
pytest test_parser.py -v
```

## What NOT to do in the fresh thread

- Don't touch the 21 `.v1.fixes`-tagged tiles' existing logic — they're all pending review-marathon signoff. Additive only.
- Don't add PNG export buttons (standing user preference).
- Don't `git add .` — stage by name. Don't push until `gh auth switch --user JGY123`.
- Don't rebuild `security_ref.json` from scratch unless the Excel file changes — it's deterministic.

---

**End of brief.** Full data-model diff between current and new CSV formats is in the parser's schema-discovery log output (re-run the parse if in doubt).
