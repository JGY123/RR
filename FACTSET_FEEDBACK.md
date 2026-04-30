# FactSet Feedback — Running Tracker

**Purpose:** capture every CSV-format issue surfaced during dashboard development. Each item is a question, request, or fix to relay to the FactSet team. Append-only.

**Date opened:** 2026-04-27
**Owner:** RR product (user) drives what gets sent to FactSet; advisor adds technical context.

> **2026-04-27 — Call-prep consolidation:** [FACTSET_CALL_PREP.md](FACTSET_CALL_PREP.md) is the single-page checklist for the upcoming finalization call. References every doc below. Use that as the call agenda; mark items resolved here as the call answers them.

---

## Open items

### F1 · Multiple security identifiers per row
**Status:** USER PLANNED — already decided to add in next CSV iteration.
**What to add:** explicit columns for `SEDOL`, `CUSIP`, `ISIN`, `Ticker-Region` per security row.
**Why:** today `Level2` (col 5 in Security section) is a mixed identifier (Japan 4-digit ticker, US ticker, EM SEDOL, etc.). 15% of holdings need name-fallback to enrich. Real user-facing tickers (e.g., `2330-TW`, `0700-HK`) live in our internal `data/security_ref.json` but should be in the source CSV.
**Affected today:** every security-detail tile and drill modal that shows an identifier.
**Affected once added:** parser extension to multi-key cascade match (see B113).

### F2 · RiskM section has data gaps + cells that don't match headers
**Status:** USER FLAGGED 2026-04-27 — needs careful examination by FactSet.
**What's wrong:** in the RiskM section of the new sample, many cells are blank, and some numeric cells appear in column positions where the header label doesn't make sense (e.g., a Period Start Date column position holding a numeric value, or factor-name columns missing entirely).
**Concrete impact:**
- The parser's `_extract_riskm` reads anchors `% of Variance` and `Active Exposure` from the header to identify port-vs-active factor blocks. The new format has neither anchor present.
- Result: `port_factor_cols` ends up empty. Every factor's raw portfolio exposure (`f.e`), benchmark exposure (`f.bm`), and contribution-to-TE (`f.c`) are null in the parsed JSON.
- Active exposure (`f.a`) IS populated because `active_factor_cols` extraction happened to succeed via different column detection. But this is fragile.
**Ask:** rebuild the RiskM section header so column headers match cell content unambiguously. Specifically request the per-factor `% of Variance` and `Active Exposure` blocks be present and labeled.

### F3 · Portfolio absolute exposure to factors — not currently shipped
**Status:** OPEN — user investigating CSV for it.
**What's needed:** for every factor in the model, the portfolio's **raw exposure** (in σ units, BEFORE active subtraction). Mathematically `f.e` = portfolio raw, `f.bm` = benchmark raw, `f.a = f.e − f.bm`. We have `f.a`, we need `f.e` (or `f.bm`).
**Where it might live:** user is searching the CSV; possibly in a non-RiskM section or in the 18 Style Snapshot. If found, parser needs to source from that location.
**If genuinely missing:** request FactSet add a per-factor portfolio-exposure column block to either (a) RiskM, or (b) the 18 Style Snapshot.
**Workaround:** B104 synthesis tile derives an approximate portfolio exposure by weighted-sum of per-security raw_fac × portfolio weights. Diverges 0.5σ from Axioma reported active because raw factors aren't orthogonalized. Useful as a sanity check, not a replacement.

### F4 · Benchmark absolute exposure to factors — not currently shipped
**Status:** OPEN — same as F3 from the other side.
**What's needed:** benchmark's raw factor exposure per factor. Either F3 or F4 needs to land; the other is derived (`bm = port − active` or `port = active + bm`).
**Implementation note:** parser hardcodes `bm: None` at `factset_parser.py:533` because the source data isn't there. One-line algebra fix once F3 lands.

### F5 · Per-factor TE contribution (`f.c`) — null on most factors
**Status:** OPEN — verify what FactSet ships.
**What's needed:** for each factor, the % of total tracking error attributable to it. Today `f.c` is null on Growth/most factors; only some factors have it populated (e.g., RiskM data cells around `% Factor Risk` anchor).
**Affected:** TE% column in cardFacDetail, drill modal stats, factor-contribution charts.

### F6 · Snapshot section needs full historical depth (not blocking, future-build)
**Status:** USER ARCHITECTURE NOTE — not a FactSet ask, dashboard concern.
**Context:** current sample has 3 weekly snap_attrib periods. Production massive-run will ship multi-year history. Once that lands, EVERY upload going forward should be APPEND-ONLY — historical data persists, new uploads add a new period.
**See:** `HISTORY_PERSISTENCE.md` (architecture doc forthcoming).

### F8 · ANTI-FABRICATION POLICY — never substitute a fabricated number for missing source data
**Status:** USER MANDATE 2026-04-27 — applies to all dashboard development going forward.
**Rule:** if a field is sourced from CSV, show the real number. If derived (sanity check from sourced fields), mark visibly with `ᵉ` badge + explanatory tooltip. **Never fabricate a plausible-looking value to fill a gap.** Surfacing missing data is more useful than hiding it.
**Why:** "even the main box at the top that shows idiosyncratic risk in big somehow shows a wacky number — at least it surfaced the issues. If I had calculated as a substitute and came up with a reasonable number that wouldn't have got my attention." (user, 2026-04-27)
**Fixes already shipped:**
- L1235 idio risk box: removed synthesis → shows `—` for historical weeks where pct_specific isn't shipped (commit forthcoming)
- L666-668 f.c synthesis (B99): kept (avoids breaking 4 dependent tiles) but marked `_c_synth=true` flag → cardFacDetail TE% now shows `ᵉ` superscript on derived cells
**Remaining work:** propagate `ᵉ` marker to cardFacButt Top-TE-Contributors pills, cardFRB donut, cardRiskFacTbl when those tiles come up in marathon. SOURCES.md tracks every cell's source class.

---

### F7 · Per-currency / per-industry / per-country attribution rows in 18 Style Snapshot
**Status:** USER OBSERVATION — confirmed present.
**What's there:** the snap_attrib dict already has 122+ keys including `BRL`, `Hungary`, `HUF`, `Semiconductors & Semiconductor Equipment`, `Oil, Gas & Consumable Fuels`, etc. These ARE granular per-currency/industry/country attribution rows.
**Implication:** B110 (sub-factor drill on Country/Currency/Industry) doesn't need new CSV data — it just needs to consume the existing snap_attrib entries. **Big unblock for B110.**

### F9 · Raw Factors section is missing Benchmark Weight column 🔥 BLOCKS FULL RUN
**Status:** USER FLAGGED 2026-04-30 — must be fixed BEFORE the full multi-year multi-account run.
**What's wrong:** the new Raw Factors section (group_size=23, parser updated 2026-04-30 commit `30f83b4`) ships per-security raw factor exposures, market cap, ADV, vol_52w, and Spotlight ranks (over/rev/val/qual/mom/stab) — **but no benchmark weight (BW) column.**
**Why it matters:** the v2 Security slim drops the long tail of bench-only constituents from the Security section. The dashboard's universe-aware aggregators (Spotlight count, country/sector/group rank averages under "Bench" mode) need to know which holdings are in the benchmark and at what weight. Today's only sources of bench weight are:
1. Security section (port + materially-large BM-only — long tail truncated, ~3.5% of total bench wt covered for major countries vs the actual ~61%).
2. Section-aggregate rows (cs.sectors, cs.countries, cs.groups, cs.regions) — these have correct bench weight totals per bucket but no per-holding granularity.
**Symptom on dashboard:** when user toggles Universe → Benchmark, holding counts and rank averages drop to a tiny subset because the parser only sees materially-large BM-only holdings. Cross-tile bug B116 (workaround landed 2026-04-30 commit `7d1b05a` — TE/MCR/factor stay invariant; counts and rank averages drop noisily under Bench mode).
**Real fix:** add `BW` (or `Benchmark Weight`) as a per-period column in the Raw Factors section so we get **the full benchmark constituent universe** with its weights. Combined with SEDOL the parser can then merge bench weights onto every holding (including ones not in the slimmed Security section) and show truthful Bench-mode aggregates.
**Ask to FactSet:** modify Raw Factors section to add a `Period Start Date:Benchmark Weight` column per period (matches existing convention). All benchmark constituents should have a row, even ones not held in any portfolio.
**Coordination:** user's plan as of 2026-04-30 — abort the full run that just kicked off, ask FactSet to add this column, re-run.
**Affected:** any tile using `aggregateHoldingsBy` with `mode='benchmark'` — cardSectors, cardCountry, cardGroups, cardRanks, cardChars (no), cardWatchlist (no), drill modals (yes).

---

## Closed / Resolved

*(none yet)*

---

## How to use this file

- Every time the user (or advisor) finds a CSV/data issue: add as a new F-id below the latest entry.
- When sending to FactSet team, copy the relevant `### F#` blocks.
- When resolved (data fixed in next CSV iteration), move to "Closed / Resolved" with date + verification commit SHA.
