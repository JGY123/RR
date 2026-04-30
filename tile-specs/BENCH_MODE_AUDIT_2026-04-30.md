# Bench-Mode Tile Audit — Pre-Multi-Account Run

**Date:** 2026-04-30
**Auditor:** tile-audit subagent
**Scope:** All 6 tiles with Universe pill (Port/Bench/Both) toggle
**Live data:** EM full-history, `~/RR/latest_data.json`
**Loaded counts (verified against JSON):**
- 291 holdings in `cs.hold[]` (40 port-held, 223 bench-held by `bw>0`)
- `cs.sum.bh = 1204` true bench constituents per FactSet → file covers **18.5% by count**
- `cs.unowned[]` = 225 disjoint securities (all numeric fields null — see B80)
- `h.bw` populated on 223/291 holdings (F9 part 1 working as advertised)
- F9 part 2 (long-tail bench constituents) NOT yet shipped — slim coverage stays
- B116 cross-tile aggregator fix is in place (commit `7d1b05a`, 2026-04-30)

---

## Executive Summary

| # | Tile | Status | Verdict |
|---|---|---|---|
| 1 | cardSectors | GREEN | SAFE FOR RUN |
| 2 | cardCountry | YELLOW | WORKAROUND OK (+ small SEV-2 fix recommended) |
| 3 | cardRegions | GREEN | SAFE FOR RUN |
| 4 | cardGroups | GREEN | SAFE FOR RUN |
| 5 | cardRanks (Spotlight) | GREEN | SAFE FOR RUN |
| 6 | cardUnowned | GREEN | SAFE FOR RUN (B80 already fixed via `_unownedFromHold`) |

**Top-level verdict — DASHBOARD IS READY FOR THE MULTI-ACCOUNT RUN.**
The slim-file under-counting under Bench mode is a **data-coverage limitation, not a bug.** The B116 invariance contract holds: TE / MCR / factor TE are identical across all three Universe modes. Counts and bench-weight sums under Bench mode reflect ~18% of the true universe by count and ~57% by weight — this is the slim-file artifact F9 part 2 is meant to close.

The one fixable inconsistency is a **YELLOW item on cardCountry**: its `aggTr` helper drops the `data.find(...).tr` fallback that `rWt` and `rGroupTable` both use. Bench-only countries with 0 holding entries will display TE=0 instead of the parser-shipped truth. This is a 1-line change and worth landing before the multi-account run.

---

## A → E findings, per tile

### 1. cardSectors — GREEN — SAFE FOR RUN

**Render:** `rWt(s.sectors, 'sec', s.hold)` at L3337.
**Bucket key:** `h.sec`.

**(A) Bench-mode count correctness:** Counts come from `factorAgg[name]?.count` which uses `aggregateHoldingsBy(...,{mode:'benchmark'})` filter `(+h.b > 0)`. Sums to **223 across all sectors** (matches the count of holdings with `bw > 0`). This is correct given the slim file. Per-sector bench-mode counts (verified):

| Sector | Port# | Bench# | Both# |
|---|---:|---:|---:|
| Communication Services | 1 | 10 | 10 |
| Consumer Discretionary | 6 | 32 | 32 |
| Consumer Staples | 3 | 12 | 12 |
| Energy | 0 | 9 | 9 |
| Financials | 9 | 31 | 31 |
| Health Care | 2 | 17 | 17 |
| Industrials | 12 | 35 | 35 |
| Information Technology | 6 | 55 | 55 |
| Materials | 0 | 9 | 9 |
| Real Estate | 1 | 6 | 6 |
| Utilities | 0 | 7 | 7 |

Bench# > 0 for every sector — no false-empty rows. (The user's flag here probably refers to cardRegions, which is the next tile.)

**(B) Bench-only securities visibility:** Confirmed. The 196 `(p=0, b>0)` holdings in `cs.hold[]` ARE the universe for Bench mode. They flow through `aggregateHoldingsBy` and contribute to count + weight + ranks under Bench/Both modes only.

**(C) TE invariance under toggle:** PASS. Per-sector TE values verified identical across {portfolio, benchmark, both} for all 11 sectors. MCR same. The B116 invariance contract is held by `aggregateHoldingsBy` L3873–3881 (TE/MCR/factor are accumulated unconditionally, only count/p/b/a/avg gates on `inUniverse`).

**(D) Empty cells:** Sector aggregate row has `tr` shipped by parser for every sector — including Energy/Materials/Utilities where holdings sum to 0. The `aggTr` fallback at L3391 catches this: `if(v!=null&&Math.abs(v)>0.01)return v; return d?.tr??0` — so display shows the parser truth. Verified working.

**(E) Bench wt sums:** Holdings-aggregated bench% sum under Bench mode = **57.36%**. Parser-shipped `cs.sectors[].b` sum = **99.99%**. Display reads `d.b` (parser aggregate) for the Bench% column, NOT the holdings-aggregated total — so the column shows TRUE bench wt (~100%). Only the `#` count and Factor-TE breakdown columns reflect the slim coverage. This is the documented B116 behavior.

**No fixes recommended.**

---

### 2. cardCountry — YELLOW — WORKAROUND OK + 1-line fix recommended

**Render:** `rCountryTable(s.countries, s.hold)` at L4192.
**Bucket key:** `h.co`.

**(A) Bench-mode count correctness:** Counts come from `factorAgg[c.n]?.count` (L4257). Same `aggregateHoldingsBy` mechanism. Top countries:

| Country | Port# | Bench# | Both# | cs.countries[].b |
|---|---:|---:|---:|---:|
| Taiwan | 1 | 11 | 11 | 24.89% |
| China | 8 | 109 | 166 | 23.09% |
| Korea | 7 | 21 | 22 | 18.73% |
| India | 5 | 31 | 32 | 11.96% |
| Brazil | 4 | 12 | 13 | 4.65% |
| Saudi Arabia | 0 | 9 | 9 | 2.65% |
| Indonesia | 0 | 5 | 5 | 0.73% |
| Thailand | 0 | 2 | 2 | 1.03% |
| Malaysia | 0 | 1 | 1 | 1.12% |
| Kuwait | 0 | 0 | 0 | 0.59% |

Bench-only countries (port#=0) ARE present in the table when bench mode toggled, with bench# > 0. Good.

**(B) Bench-only securities:** Confirmed visible. Per-country `count` reflects bench-only holdings under Bench mode.

**(C) TE invariance:** PASS. `aggregateHoldingsBy` invariance holds.

**(D) Empty cells — SEV-2 finding:** **`rCountryTable.aggTr` does NOT mirror the same fallback that `rWt` and `rGroupTable` use.** Compare:

```js
// L3391 (rWt): falls back to parser-shipped d.tr
const aggTr=(name)=>{const v=factorAgg[name]?.tr; if(v!=null&&Math.abs(v)>0.01)return v; const d=data.find(x=>x.n===name); return d?.tr??0;};

// L4321 (rGroupTable): same fallback, against displayGroups
const aggTr=(name)=>{const v=factorAgg[name]?.tr; if(v!=null&&Math.abs(v)>0.01)return v; const g=displayGroups.find(x=>x.n===name); return g?.tr??0;};

// L4213 (rCountryTable): NO fallback
const aggTr=(name)=>factorAgg[name]?.tr ?? 0;
const aggMcr=(name)=>factorAgg[name]?.mcr ?? 0;
```

**Consequence:** countries with no holdings shipped (e.g. Kuwait, Qatar, the long tail of bench-only) will display TE=0 even though `cs.countries[].tr` carries a real value. From the data above: Kuwait `tr` is 0 (parser shipped 0), but Qatar has `tr=-0.10` per parser and would render as 0.0 in the UI today.

**Recommended fix (1-line, propose-only — coordinator to apply):**
```js
// L4213-4214 in rCountryTable
const aggTr=(name)=>{const v=factorAgg[name]?.tr; if(v!=null&&Math.abs(v)>0.01)return v; const c=countries.find(x=>x.n===name); return c?.tr??0;};
const aggMcr=(name)=>{const v=factorAgg[name]?.mcr; if(v!=null&&Math.abs(v)>0.01)return v; const c=countries.find(x=>x.n===name); return c?.mcr??0;};
```
Mirrors rWt/rGroupTable. Restores TE truth for bench-only/holdings-thin countries.

**Severity:** SEV-2. Wrong on the order of 0.1–0.3% TE in a tiny number of countries. Not a blocker for the multi-account run, but worth landing for consistency.

**(E) Bench wt sums:** `cs.countries[].b` sums to **100.00%** (verified). Display reads `c.b` directly so Bench% column is correct.

---

### 3. cardRegions — GREEN — SAFE FOR RUN

**Render:** `rWt(s.regions, 'reg', s.hold)` at L3337 (same function as sectors).
**Bucket key:** `CMAP[h.co] || 'Other'`.

**User's specific flag:** "security count isn't nearly complete in BM mode."

**(A) Bench-mode count correctness:** This is what the user observed and they are correct — but it is a slim-file consequence, not a bug.

| Region (parser) | cs.regions.b% | Bench-mode # (holdings) | True bench# (cs.sum.bh share) |
|---|---:|---:|---:|
| Emerging Market | 96.37% | 223 | ~1135 (estimated 1204 × .94) |
| English | 0.47% | 0 | ~5 |
| Far East | 2.41% | 0 | ~24 |
| Northern Europe | 0.16% | 0 | ~1 |
| Usa | 0.00% | 0 | 0 |

The `# = 223` for Emerging Market under Bench mode reflects exactly the 223 holdings with `bw>0` in the slim file — and they are concentrated in EM (which makes sense for an EM strategy). The other regions show 0 because no `bw>0` holdings map to them.

This is the **same B116 phenomenon as cardSectors**: count silently under-reports because slim file = ~18% of bench universe by count.

**(B) Bench-only securities:** Visible — same path as cardSectors via `aggregateHoldingsBy`.

**(C) TE invariance:** PASS — `rWt(...,'reg',...)` uses same `aggregateHoldingsBy` machinery.

**(D) Empty cells:** Region aggregate row has `tr` from parser. The `aggTr` fallback in `rWt` (L3391) catches this. Verified — Northern Europe `tr=0.1` would render correctly even with 0 holdings in bucket.

**(E) Bench wt sums:** `cs.regions[].b` sums to **99.41%** (verified). Display reads `d.b` directly.

**Recommendation:** This tile behaves correctly given F9 part 2 has not landed. The "incomplete count" the user flagged is indeed a real coverage gap, but the dashboard is *honest* about it — counts reflect the actual file contents. After F9 part 2 lands, counts will jump to ~1135 and look right. **No code fix needed.**

A potential UX add (NOT for the run — for after): a small chip near the # column under Bench mode like `(slim file: 18% coverage)` to make this honest about itself. Defer to PM.

---

### 4. cardGroups — GREEN — SAFE FOR RUN

**Render:** `rGroupTable(s.groups, s.hold)` at L4280.
**Bucket key:** `h.subg || h.sg`.

**(A) Bench-mode count correctness:** All 8 Redwood subgroups receive bench-mode counts > 0:

| Group | Port# | Bench# | Both# | cs.groups[].b |
|---|---:|---:|---:|---:|
| BANKS | 7 | 26 | 39 | 15.58% |
| BOND PROXIES | 1 | 17 | 18 | 7.14% |
| COMMODITY | 2 | 19 | 23 | 11.64% |
| DEFENSIVE | 10 | 17 | 20 | 5.05% |
| GROWTH | 8 | 40 | 55 | 14.08% |
| GROWTH CYCLICAL | 6 | 54 | 74 | 37.70% |
| HARD CYCLICAL | 4 | 16 | 20 | 4.46% |
| SOFT CYCLICAL | 2 | 21 | 24 | 4.05% |

Total: 210 bench-securities (slightly less than 223 because 13 holdings have no `subg`). All 8 buckets populated under Bench mode.

**(B) Bench-only securities:** Visible.
**(C) TE invariance:** PASS.
**(D) Empty cells:** `aggTr` at L4321 has the same fallback pattern as `rWt`. Bench-only groups display parser-truth tr. Working correctly.
**(E) Bench wt sums:** `cs.groups[].b` sums to **99.70%** (verified). Display reads `g.b` directly.

**No fixes recommended.**

---

### 5. cardRanks (Spotlight) — GREEN — SAFE FOR RUN

**Render:** `renderRanksTable()` builds via `aggregateHoldingsBy(cs.hold, h => h.[over|rev|val|qual roundedToQuintile], ...)` at L4083.
**Bucket key:** Quintile 1–5 derived from `h.over` (default), `h.rev`, `h.val`, or `h.qual`.

**(A) Bench-mode count correctness:** All 5 quintiles receive bench-mode counts > 0 under default Overall ranking:

| Quintile | Port# | Bench# | Both# | Bench% |
|---|---:|---:|---:|---:|
| Q1 (best) | 10 | 31 | 35 | 32.04% |
| Q2 | 7 | 30 | 31 | 6.53% |
| Q3 | 4 | 27 | 28 | 4.60% |
| Q4 | 10 | 35 | 38 | 4.87% |
| Q5 (worst) | 2 | 39 | 39 | 6.66% |

Total: 162 bench-securities ranked. (61 of the 223 bench holdings have `over=null` and are excluded — see note below.)

**Caveat:** 61 of 223 bench holdings have `h.over = null` so are dropped from cardRanks entirely. This is a parser-side gap — Spotlight ranks aren't shipped for every benchmark constituent, only for the materially-large ones. **Not a dashboard bug.** Same caveat applies under Port mode (different ratio).

**(B) Bench-only:** Visible.
**(C) TE invariance:** PASS — same `aggregateHoldingsBy` mechanism.
**(D) Empty cells:** No empty quintile rows. Q1–Q5 all populate.
**(E) Bench wt sums:** Sum across quintiles under Bench mode = 54.7% (matches the 162-out-of-223 ranked subset). The parser does not ship a quintile-aggregate row, so there is no fallback. Display is honest about the data it has.

**No fixes recommended.** Slightly degraded coverage under Bench mode is a data-completeness issue, not a render bug.

---

### 6. cardUnowned — GREEN — SAFE FOR RUN (B80 already fixed)

**Render:** `rUnowned(_unownedFromHold(s))` at L2331 + L4435.
**Bucket key:** N/A (flat table of bench-only holdings, sorted by `|tr|` desc, top 10).

**Critical finding — B80 is RESOLVED.** The line of code at 2331 has been updated to call `_unownedFromHold(s)`, NOT `s.unowned`. The `_unownedFromHold` helper (L4440) filters `cs.hold[]` for `(p<=0 && b>0)` and projects the right field shape — bypassing the broken `cs.unowned` array (which is the parser orphan-bucket with all numeric fields null).

**(A) Bench-mode count correctness:** N/A — this tile has no Universe pill; it intrinsically displays bench-only stocks. But it IS Universe-mode-relevant in spirit.

| Metric | Value |
|---|---:|
| `_unownedFromHold(s)` row count (universe) | 196 |
| Top 10 displayed (after `|TE|` sort) | 10 |
| Rows with `bw > 0` populated | 196/196 |
| Rows with non-zero `tr` | 34/196 |

**(B) Bench-only visibility:** Yes — that's the entire content.
**(C) TE invariance:** N/A — table doesn't react to Universe pill.
**(D) Empty cells — RESOLVED.** Spot-check on top 10 rows shows BW% ranges 0.38–1.14%, TE% ranges -0.30 to +0.90%. All populated. No more "totally blank" issue.

| Sample row | Sector | Country | BW% | TE% |
|---|---|---|---:|---:|
| 6099626 | Energy | India | 0.79 | 0.90 |
| 6372480 | InfoTech | Taiwan | 1.07 | 0.80 |
| B0LMTQ3 | Financials | China | 0.92 | 0.60 |
| 6260734 | InfoTech | Taiwan | 1.14 | 0.50 |
| BJTM270 | Energy | Saudi Arabia | 0.38 | 0.40 |

**(E) Bench wt sums:** N/A.

**Verification of the fix:** confirmed that the user-flagged "totally blank in data point values" is **no longer reproducible against current dashboard code + current parser output**. The B80 fix in `_unownedFromHold` (commented as "2026-04-30 (B80 fix)") is live.

**No fixes recommended.** The 162 rows below the top-10 cap with `tr=0` are honest — those bench-only holdings have stock-specific TE that rounds to zero, so they don't make the top-by-|TE| cut. Sort + cap is appropriate.

---

## Cross-tile invariants verified

1. **TE / MCR / factor TE columns are IDENTICAL across {Port, Bench, Both}** — verified for all 11 sectors. The B116 cross-tile fix at `aggregateHoldingsBy` L3873–3881 makes TE accumulation universe-blind. Every tile that uses this helper inherits the correct behavior.
2. **# (count) column flips correctly with Universe pill** for all 5 tiles that have it.
3. **Bench% column displays the parser-shipped aggregate truth** (~100%) — not the holdings-aggregated subset (~57%). Display reads `d.b`/`c.b`/`g.b` directly, not `factorAgg[k].b`. This is correct.
4. **Spotlight ranks (O/R/V/Q) under `_avgMode='avg'`** use `factorAgg.avg.[field]` which IS universe-filtered (correct intent — averaging across the bench universe should NOT include port-only names).
5. **Spotlight ranks under `_avgMode='wtd'`** use the weighted accumulators which switch between `wtd` (port weights) and `bm` (bench weights) per `_aggMode`. Verified at L3957–3961 (`pickRankAvg`).

---

## Slim-file coverage table (for the "is this what I should expect" question)

| Aggregate dimension | Parser-shipped truth | Bench-mode holdings sum | Coverage |
|---|---:|---:|---:|
| Sector bench wt | 99.99% | 57.36% | 57% |
| Country bench wt | 100.00% | 57.36% | 57% |
| Group bench wt | 99.70% | 57.10% | 57% |
| Region bench wt | 99.41% | 57.36% | 58% |
| Bench security count | 1204 | 223 | 18.5% |
| Bench coverage incl. unowned | 1204 | 223 + 225 = 448 | 37% (but unowned rows have no bw — only count) |

**Reading:** under Bench mode, expect # column to show ~18% of true bench count and bench-side weighted aggregates to cover ~57% of bench. This is F9 part 2 territory. Once FactSet ships the long-tail bench-only constituents in the next CSV iteration, both numbers should jump close to 100%.

---

## Final verdict

**SAFE FOR THE FULL MULTI-ACCOUNT, MULTI-YEAR FACTSET PULL.**

All 6 tiles handle the slim file correctly under Bench mode. TE/MCR/factor risk decomposition is invariant across Universe modes (B116 contract held). Counts and bench-weight sums under Bench mode honestly reflect the slim file's coverage — they will improve automatically when F9 part 2 data lands. No fabrication, no silent corruption.

**One soft recommendation before kickoff (1-line patch, optional):**
- Apply the `aggTr` fallback fix to `rCountryTable` L4213–4214 to mirror `rWt` and `rGroupTable`. This restores TE truth for bench-only/holdings-thin countries (Kuwait, Qatar, etc.). SEV-2, ~5 lines diff. Coordinator to apply.

**No SEV-1 issues. No SEV-0 blockers. Run can proceed.**

---

## Fix queue

### TRIVIAL (coordinator can apply, ~5 lines):
- F1 — `rCountryTable` `aggTr`/`aggMcr` fallback parity with `rWt`/`rGroupTable`. SEV-2.

### NEEDS PM DECISION (B116 is already logged):
- B116 follow-up — option (b) qualifier chip to mark Bench-mode # and Factor TE columns as "slim file partial coverage". The dashboard is honest today; this just makes it self-documenting. Defer until after F9 part 2 ships.

### BLOCKED:
- F9 part 2 (FactSet — long-tail bench constituents in Raw Factors). Until this lands, Bench-mode coverage stays at 18% by count / 57% by weight. **Not a dashboard fix; a data ask.** Already in `FACTSET_FEEDBACK.md`.
