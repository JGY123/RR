# Handoff to Executor Thread — Data-Foundation Integration

**Date:** 2026-04-24
**From:** Advisor (prior Claude session in a different tab — has full context on all 21 tile audits, the new CSV inspection, and the Excel bake)
**To:** You (a fresh Claude Code session in `~/RR`)
**Relationship:** I am the **advisor**, you are the **executor**. I will be available in my other tab to answer clarifying questions. When you're stuck or need a judgment call, ask the user to relay your question to me and paste my response back into your thread. Don't guess on ambiguity — ask.

---

## First 60 seconds — orient yourself

Run these in order:

```bash
cat ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md   # mandatory RR context per CLAUDE.md
cat ~/RR/CLAUDE.md                                                        # project conventions
cat ~/RR/INTEGRATION_BRIEF.md                                             # the detailed 5-phase plan
cat ~/RR/SESSION_STATE.md                                                 # where the project stands
git -C ~/RR log --oneline -10                                            # recent commits
git -C ~/RR tag -l | tail -20                                            # see the tile-audit tag landscape
```

After reading those, you'll know: 21 tiles audited + at `.v1.fixes` (review-marathon pending), security_ref.json baked, new CSV tested against current parser, Raw Factors section unhandled.

**Your job:** execute Phases 1–5 of `INTEGRATION_BRIEF.md`. Do not touch the 21 audited tiles' existing logic — additive work only. When you finish, we run the review marathon.

---

## The information you asked about — factor label order (user-confirmed)

The "Raw Factors" CSV section ships **12 per-security z-score columns per period** with NO column labels (the header row uses holdings-schema names that don't apply to this section). The positional order is **alphabetical** and stable:

```python
RAW_FACTOR_ORDER = [
    "Dividend Yield",
    "Earnings Yield",
    "Exchange Rate Sensitivity",
    "Growth",
    "Leverage",
    "Liquidity",
    "Market Sensitivity",
    "Medium-Term Momentum",
    "Profitability",
    "Size",
    "Value",
    "Volatility",
]
```

**This is authoritative for the current sample. The user (goodman.yuda@gmail.com) confirmed this order at 2026-04-24.** For the massive production run, FactSet may ship explicit labels per column — design the parser so it USES `RAW_FACTOR_ORDER` when labels are absent, but honors explicit header labels if ever present. Keep the constant in one place (top of `factset_parser.py`) and document both sides of the fallback.

Cross-check that bolsters confidence in the order: the existing `strategy.hist.fac` dict (populated today via the `_collect_riskm_data` path) contains keys that overlap these names exactly — so these 12 labels are the project's canonical style-factor vocabulary.

---

## Phases — exact execution order

### Phase 0 — Safety tag + branch discipline

```bash
cd ~/RR
NOW=$(date +%Y%m%d.%H%M)
git tag "working.${NOW}.pre-phase1"
```

Work on `main`. Do not create a feature branch unless the advisor tells you to. Commit in small logical units per phase. Stage by filename (`git add <file>` — never `git add .`).

### Phase 1 — Parser: Raw Factors capture [P0 blocking]

**File:** `factset_parser.py`

1. At the top (near `SEC_SUBGROUP`, `CMAP`, etc.), add:
   ```python
   RAW_FACTOR_ORDER = [
       "Dividend Yield", "Earnings Yield", "Exchange Rate Sensitivity",
       "Growth", "Leverage", "Liquidity", "Market Sensitivity",
       "Medium-Term Momentum", "Profitability", "Size", "Value", "Volatility",
   ]
   ```

2. Locate the section-dispatch logic (search for where `"Raw Factors"` would land — likely the schema-auto-discovery path prints it but nothing consumes it).

3. Add `_collect_raw_factors(rows, strategy_obj)`:
   - For each row in section `"Raw Factors"`:
     - Identifier = col 5 (`Level2` — SEDOL/ticker, same key as `Security` section col 5)
     - Name = col 6
     - Per-period block = 13 cols starting at col 7: `[Period Start Date, v0, v1, ..., v11]`
     - Parse each period block; skip a block if the date cell is blank.
   - Emit:
     ```python
     strategy["raw_fac"] = {
         "<identifier>": {
             "n": name,
             "e": [v0, ..., v11],          # latest period (most recent date wins)
             "hist": [
                 {"d": "YYYYMMDD", "e": [v0, ..., v11]},
                 ...sorted ascending by date...
             ]
         },
         ...
     }
     ```
   - Use `RAW_FACTOR_ORDER` in the JSON schema metadata so the dashboard can look up labels:
     ```python
     strategy["raw_fac_labels"] = RAW_FACTOR_ORDER   # only emit once per strategy
     ```

4. Bump `FORMAT_VERSION` from `"3.0"` to `"3.1"`. Bump `PARSER_VERSION` to `"1.2.0"`.

5. Make sure the new hook runs during the existing per-strategy parse pass. Don't parallel-iterate the CSV twice.

6. Deliverable test command:
   ```bash
   python3 factset_parser.py "/Users/ygoodman/Downloads/risk_reports_sample (5).csv" /tmp/phase1.json
   python3 -c "
   import json
   d=json.load(open('/tmp/phase1.json'))
   idm = d[0]['IDM']
   rf = idm.get('raw_fac', {})
   print(f'raw_fac entries: {len(rf)}')
   print(f'labels: {idm.get(\"raw_fac_labels\", [])}')
   # Sample one
   for k, v in list(rf.items())[:2]:
       print(f'{k}: n={v[\"n\"]!r} e={v[\"e\"]} hist_len={len(v[\"hist\"])}')
   "
   ```
   Expected: ~775 raw_fac entries for IDM, each with `e` = list of 12 floats, `hist` with 4 periods.

### Phase 2 — Parser: security_ref enrichment [P0]

**File:** `factset_parser.py`

1. At module top, load once:
   ```python
   import os, re
   _SECURITY_REF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "security_ref.json")
   try:
       with open(_SECURITY_REF_PATH) as _f:
           _SECURITY_REF = json.load(_f).get("by_sedol", {})
   except (FileNotFoundError, json.JSONDecodeError):
       _SECURITY_REF = {}
   # Also build a name-fallback index
   _SECURITY_REF_BY_NAME = {}
   for _k, _v in _SECURITY_REF.items():
       nn = re.sub(r"[^a-z0-9]", "", (_v.get("n") or "").lower())[:30]
       if nn:
           _SECURITY_REF_BY_NAME.setdefault(nn, _v)
   ```

2. Add `_enrich_holding(h)`:
   ```python
   def _enrich_holding(h):
       key = (h.get("t") or "").upper()
       ref = _SECURITY_REF.get(key) or _SECURITY_REF.get(key.lstrip("0"))
       if not ref:
           nn = re.sub(r"[^a-z0-9]", "", (h.get("n") or "").lower())[:30]
           ref = _SECURITY_REF_BY_NAME.get(nn)
       if ref:
           h["country"] = ref.get("country")
           h["currency"] = ref.get("ccy")
           h["industry"] = ref.get("industry")
       return h
   ```

3. Call `_enrich_holding(h)` once per holding during the Security-section parse (both `hold[]` and `unowned[]` paths, in case unowned is ever populated for real).

4. Log coverage at the end of each strategy's parse:
   ```python
   enriched = sum(1 for h in strategy["hold"] if h.get("country"))
   total = len(strategy["hold"])
   print(f'  {strategy["id"]}: security_ref enrichment {enriched}/{total} ({100*enriched/max(1,total):.1f}%)')
   ```
   Expected: 93–98% coverage per strategy.

5. Emit `strategy["security_ref_version"]` using `_SECURITY_REF` meta if available. Keeps the JSON self-describing.

### Phase 3 — Fix the broken test suite FIRST, then add new tests [P0]

**File:** `test_parser.py`

1. Reproduce: `python3 -m pytest test_parser.py -q`. Expected failure: `ImportError: cannot import name 'classify_row' from 'factset_parser'`.

2. Diagnose: grep `factset_parser.py` for a likely successor name (could be `_classify_row`, `classify_section_row`, `_section_for_row`, etc.). Update the test import accordingly, OR re-export the symbol from the parser module if the rename was intentional.

3. Confirm all pre-existing tests green BEFORE adding new tests for Raw Factors and enrichment.

4. Add ~6 new tests covering:
   - `_collect_raw_factors` output shape (keys, length of `e`, ordering of `hist` by date).
   - `RAW_FACTOR_ORDER` exposed in output per strategy.
   - `_enrich_holding` success case (look up a known HSBC/Weichai from security_ref.json).
   - `_enrich_holding` fallback via name.
   - `_enrich_holding` miss case leaves fields null.
   - Full-pipeline: parse the sample CSV and assert the IDM strategy has ≥700 `raw_fac` entries and ≥90% enrichment coverage.

### Phase 4 — Regenerate sample data, browser regression check [P0]

1. Regenerate the dev sample:
   ```bash
   python3 factset_parser.py "/Users/ygoodman/Downloads/risk_reports_sample (5).csv" sample_data.json
   ```
   (If `sample_data.json` is committed — check — only overwrite if it's gitignored or a stale file the user expects to refresh.)

2. Open the dashboard:
   ```bash
   open dashboard_v7.html
   ```
   Drag-drop the regenerated JSON. Click through every tab. **None of the 21 audited tiles should throw console errors or render differently.** If anything breaks, that's a regression — bisect by temporarily reverting the parser changes to confirm the cause.

3. Right-click → Inspect → Console: zero red errors is the bar.

### Phase 5 — Commit discipline + tagging

Commit each phase separately. Example messages:

```
feat(parser): Phase 1 — capture Raw Factors section into strategy.raw_fac
feat(parser): Phase 2 — security_ref enrichment hook (country/currency/industry)
test(parser): Phase 3 — fix classify_row import + add raw_fac/enrichment coverage
chore: Phase 4 — regenerate sample_data.json from new format
```

After Phase 4 is green in the browser:

```bash
git tag data-foundation-v1 <HEAD_SHA> -m "Raw Factors captured, security_ref enrichment live, all tests green, all 21 tiles render."
gh auth switch --user JGY123
git push origin main
git push origin data-foundation-v1
```

Then update `SESSION_STATE.md` with a new checkpoint-log entry describing what shipped.

### Phase 6 (optional, only if advisor greenlights) — New tiles

`INTEGRATION_BRIEF.md` Phase 3 details three new dashboard tile opportunities:
- 3a: per-security raw factor exposure drill inside `oSt(ticker)` modal
- 3b: `cardRiskByDim` — the user's key ask, risk decomposed by country/currency/industry
- 3c: portfolio aggregate raw-exposure synthesis

**Do NOT start Phase 6 without explicit advisor greenlight.** These are Medium-size tile builds and should each follow the Batch 1–7 tile-audit cadence (spawn audit subagent if the advisor directs you to). The user may want to do the review marathon first before adding new tiles. Ask.

---

## Back-channel to advisor

When you hit ambiguity or a judgment call, do this:

1. Don't commit anything partial or speculative.
2. Ask the user to relay your question. Draft it as a single block starting with `ADVISOR QUESTION:` so it's easy to copy-paste. Example:
   ```
   ADVISOR QUESTION: In Phase 1, the CSV shows identifier col 5 = "CASH_USD" for cash rows. Do you want me to skip these in raw_fac (they have no factor exposures) or keep them with e=[None]*12 as placeholders? Current leaning: skip, matching the Security section which filters cash via isCash(). Confirm?
   ```
3. The user will paste it to me in the advisor tab; I'll respond; you'll get my reply back.

Good reasons to ask:
- Ambiguity in the data (factor order, missing labels, dual-key identifiers)
- Architectural choices (parser-side vs dashboard-side enrichment — I already recommend parser-side but if you hit a blocker, say so)
- Anything in the brief that seems contradictory to something you see in code

Don't ask about:
- Things clearly spelled out in this doc or `INTEGRATION_BRIEF.md`
- Standard project conventions (they're in `CLAUDE.md` + `~/.claude/projects/-Users-ygoodman-RR/memory/MEMORY.md`)

---

## Hard rules (standing user preferences — these come from memory files)

- **No PNG buttons.** Ever. The user has removed them multiple times.
- **No `git add .`** — stage by filename only (`.DS_Store`, `.claude/`, and other detritus creeps in).
- **`gh auth switch --user JGY123`** before any push to `JGY123/RR`. Default `gh` account is `yuda420-dev`.
- **Verify writes hit disk** after every Edit/Write: `wc -l <file>` + `grep -c <pattern>` + `git status`. Never trust tool-success alone.
- **Safety-tag before risky edits:** `working.YYYYMMDD.HHMM.pre-<name>`.
- **`.v1` / `.v1.fixes` tags ≠ signoff.** Signoff is the user's explicit in-browser OK, and only happens in the review marathon.
- **Tile-audit subagents never edit `dashboard_v7.html`** — the main session serializes all edits. (Only relevant for Phase 6.)

---

## What you are NOT allowed to change

- Any render function for the 21 audited tiles (cardSectors, cardHoldings, cardCountry, cardThisWeek, cardChars, cardFacButt, cardFacDetail, cardFRB, cardRegions, cardRanks, cardScatter, cardTreemap, cardMCR, cardAttrib, cardCorr, cardGroups, cardRiskHistTrends, cardRiskFacTbl, cardBenchOnlySec, cardUnowned, cardWatchlist, cardAttribWaterfall, cardFacContribBars, cardTEStacked).
- `BACKLOG.md` — additive only; don't reorder or edit existing entries.
- The 7 milestone tags (`tier1-audit-complete`, `data-foundation-prep`, and the 42 tile `.v1`/`.v1.fixes` tags).
- `CLAUDE.md`, `HANDOFF.md`, `LIEUTENANT_BRIEF.md` — read but don't edit without advisor go-ahead.

Parser, test file, new dashboard code (Phase 6 only) are fair game.

---

## First 3 actions

1. Read all files from "First 60 seconds — orient yourself" above, in order.
2. Safety-tag: `cd ~/RR && git tag "working.$(date +%Y%m%d.%H%M).pre-phase1"`.
3. Start Phase 1. When you get to the `_collect_raw_factors` function signature, ask yourself: does the existing parser have a pattern for per-security-per-period structured data? (Hint: look at how `hist.summary` is built.) Follow the existing pattern — consistency matters.

When Phase 1's smoke test (the `python3 -c "…"` block at the end of Phase 1) shows ~775 raw_fac entries for IDM with 12-element `e` arrays, commit Phase 1, move to Phase 2.

**Target:** Phases 1–5 done and tagged `data-foundation-v1` within this session. Phase 6 on advisor's call.

Good luck. I'm in the other tab.
— Advisor (2026-04-24)
