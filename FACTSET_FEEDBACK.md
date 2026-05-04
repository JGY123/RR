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

### F9 · Raw Factors section — BM Weight ✅ SHIPPED · long-tail bench universe ✅ SHIPPED
**Status:** RESOLVED on FactSet's side as of EM full-history file (2026-04-30).
**What was needed:** per-period Benchmark Weight column in Raw Factors + the full bench universe (long-tail bench-only constituents) included in the file.
**What FactSet shipped:** EM full-history file (`em_full_history.xlsx`, 91MB) includes:
- ✅ Raw Factors section group_size=24 with `Bench. Ending Weight` at offset 1
- ✅ Full bench constituent universe in Raw Factors: 1,489 entries, 796 with bw>0
- ✅ Tracked via parser commit `b57c659` (2026-04-30) — synthesizes cs.hold[] entries from raw_fac long-tail when SEDOL not in slim Security section
**Result:** Bench-mode coverage 21% → 70% by count, 57% → 97% by weight. cardRegions / cardCountry / cardSectors / cardGroups / cardRanks all show truthful BM-mode counts.
**Verification commits:**
- Parser format support: `819c493` (2026-04-30) — handles 24-col Raw Factors layout
- Long-tail synth fix: `b57c659` (2026-04-30) — synthesizes cs.hold[] entries when not in slim Security
**Note:** the 30% by-count gap remaining (846 / 1,204) is FactSet's bench universe truncation policy (some micro-cap names with bw < some threshold are dropped from Raw Factors). Acceptable.

---

## Open items — what FactSet still needs to ship

### F11 · Per-holding period return (Brinson attribution inputs) — STILL OPEN
**Status:** C1 in verifier — known C-tier nice-to-have; not blocking.
**What's needed:** `Period Return` column per security in the Security section (or Raw Factors). One number per security per period.
**Why it matters:** Brinson attribution (sector contribution to portfolio active return) requires per-holding returns. Today the dashboard cannot compute Brinson; the cardAttrib waterfall is factor-only (FactSet 18 Style Snapshot data).
**Ask to FactSet:** add `Period Start Date:Period Return` column to Security section (or Raw Factors) per period. Returns can be in % terms (close-to-close, USD, total return). One number per security per period.

### F12 · pct_t / pct_s for bench-only synth holdings — RECOMMENDED, NOT BLOCKING
**Status:** Identified during F4 fix work, 2026-04-30.
**Context:** the parser now synthesizes 623 cs.hold[] entries from Raw Factors for the EM long-tail bench universe. Each entry gets bw, mcap, raw_exp, and Spotlight ranks. But pct_t (% of TE contribution) and pct_s (stock-specific TE %) come from the Security section's `%T` and `%S` columns — NOT shipped for long-tail bench-only names.
**Symptom:** in cardUnowned (which lists bench-only names by |TE|), only the 196 names that ARE in slim Security have non-null pct_t. The 623 synth entries have null pct_t — they don't appear in cardUnowned despite having bench weight.
**Ask to FactSet:** ship `%T_implied` (or equivalent) for every Raw Factors row — same %T calculation but applied to the implied-underweight TE contribution from each long-tail bench-only name. Allows ALL ~1,200 bench constituents to show in cardUnowned ranked by their TE contribution to the portfolio's tracking error.
**Workaround if FactSet declines:** synthesize `pct_t = -bw × idiosyncratic_factor` parser-side. Approximate but better than zero.

### F13 · Date format standardization — RECOMMENDED
**Status:** Caught during EM full-history parse, 2026-04-30. Parser now handles both formats.
**What we observed:** EM file ships per-period dates as `"2019-01-01 00:00:00"` (ISO datetime with zero time component). Earlier files shipped plain `"2019-01-01"`.
**Why it matters:** the time suffix triggered a parser bug (parse_date fall-through to file run-date, collapsing all 7 years to one date). Bug fixed in commit `73326ed` but the underlying inconsistency is fragile.
**Ask to FactSet:** standardize on plain `YYYY-MM-DD` (or `YYYYMMDD`) format. Drop the trailing `00:00:00` time component.

### F14 · Portfolio-level pct_specific / pct_factor — RECOMMENDED, NOT BLOCKING
**Status:** Caught during data-integrity audit, 2026-04-30.
**Context:** the dashboard's Idio% / Factor% sum-cards on Risk + Exposures tabs need `% Specific Risk` and `% Factor Risk` at the portfolio-Data row level. The parser currently DERIVES these via `Σ sector mcr` (synth markers `_pct_specific_source: 'sum_sector_mcr'` are visible in JSON). Display shows ᵉ flag with hover explanation.
**Ask to FactSet:** ship `% Specific Risk` and `% Factor Risk` directly at the portfolio-Data row in Portfolio Characteristics (or Security section's portfolio aggregate row). Removes the synth marker, eliminates a derivation-error class.

### F15 · Country-of-RISK vs country-of-LISTING flag for ADRs — RECOMMENDED, MINOR
**Status:** Caught during F4 synth work, 2026-04-30.
**Context:** the EM bench includes ADRs of Brazilian/Chinese/etc. companies that are listed in US (e.g. NIO-US, MELI-US). Their ticker-region suffix is `-US` but their issuer domicile is EM. The dashboard needs both (one for listing exchange, one for "country of risk" attribution). Today we use the suffix.
**Ask to FactSet:** add a `Country of Risk` column per security in Security or Raw Factors section. Lets the parser distinguish listing country from risk country.

### F16 · IOP (ACWIXUS) shipped with major sections missing — 🔴 NEEDS RE-RUN
**Status:** Caught during multi-account run verification, 2026-05-01.
**File:** `risk_reports_sample.csv` (1.7 GB multi-account file, 5 strategies, parsed 2026-05-01).
**What's wrong:** IOP/ACWIXUS is in the file but with significantly less data than the other 4 strategies (ACWI, GSC, IDM, ISC). Same process was supposedly run for all 5 accounts.

**Sections present for IOP/ACWIXUS:**
- ✅ Raw Factors (3,849 rows) — per-bench-constituent data with bw/mcap/raw_exp/spotlight ranks
- ✅ Security (911 rows) — but factor_contr columns within these rows are EMPTY (per-period factor TE breakdown missing)
- ✅ Portfolio Characteristics (470 rows) — sum cards, P/E, P/B all populated
- ✅ 18 Style Snapshot (168 rows) — snap_attrib factor history works
- ✅ Country (52 rows), Industry (34 rows) — current snapshot works

**Sections MISSING for IOP/ACWIXUS:**
- ❌ RiskM — 0/12 factors with active exposure / TE % data
- ❌ Sector Weights section rows — per-period sector aggregates missing
- ❌ Region section rows
- ❌ Group section rows
- ❌ factor_contr per holding (Security section's per-period factor breakdown columns are empty)

**Visible symptoms:**
- Total TE / AS / Beta sum cards work (from Portfolio Characteristics)
- Risk tab mostly EMPTY: cardFacRisk, cardFacContribBars, cardRiskFacTbl, cardRiskByDim all sparse
- cardSectors / cardCountry / cardRegions / cardGroups: current snapshot works but no historical trend (hist.sec / hist.ctry / hist.reg / hist.grp = empty)

**Comparison vs working strategies:**
| Strategy | Sector Weights rows | Region rows | Group rows | Per-strategy file size |
|---|---:|---:|---:|---:|
| ACWI    | populated | populated | populated | 477 MB |
| ISC     | populated | populated | populated | 519 MB |
| IOP     | **0** | **0** | **0** | 292 MB |
| IDM     | populated | populated | populated | 204 MB |

**Ask to FactSet:** re-run IOP (ACWIXUS) end-to-end with the same process used for the other 4 strategies. The output should include RiskM section + Sector Weights / Region / Group section rows + factor_contr columns populated in the Security section.

### F17 · GSC shipped without Raw Factors data — 🔴 NEEDS RE-RUN
**Status:** Caught during multi-account run verification, 2026-05-01.
**What's wrong:** GSC is in the file with full Security + RiskM + factor TE + sector/country/group data — but the **Raw Factors section is missing or empty** for GSC. The per-strategy split file is only 10.6 MB vs 200-500 MB for other strategies (the 20-50× size gap is the missing Raw Factors data).

**Sections present for GSC:**
- ✅ Security (2,130 rows — actually larger than ACWI's 1,383)
- ✅ Portfolio Characteristics (526 rows) — sum cards, P/E, P/B
- ✅ 18 Style Snapshot (126 keys) — snap_attrib works
- ✅ Sector Weights / Country / Region / Group / Industry — all populated
- ✅ RiskM — 12/12 factors populated
- ✅ factor_contr per holding (16 factors) — full data

**Sections MISSING for GSC:**
- ❌ Raw Factors section — no per-bench-constituent enrichment (no mcap, no raw_exp, no spotlight ranks for the long-tail bench)

**Visible symptoms:**
- cs.hold has 1,002 holdings but only the slim Security section data — no F4 long-tail synthesis happens (Raw Factors empty)
- Holdings table shows SEDOLs (e.g. `BMMV2K8`) instead of ticker-regions (e.g. `700-HK`)
- No market cap / 52-week vol / 90D ADV columns
- Spotlight quintile coverage thinner (only port-held + materially-large bench-only get ranks from Security section, not the full bench-only universe via Raw Factors)

**Ask to FactSet:** re-run GSC ensuring the Raw Factors section is included in the output. All other 4 strategies (ACWI, IDM, IOP, ISC) had Raw Factors in this batch — GSC is the outlier. Same configuration / process should apply.

---

### F18 — Per-holding %T does NOT sum to 100% (CLAUDE.md says it should)

**Finding date:** 2026-05-04 (cardRiskByDim audit)
**Severity:** RED — contradicts the documented invariant in CLAUDE.md line 108.

CLAUDE.md states: `%T = Percentage of tracking error — each holding's % contribution to total portfolio TE (sums to ~100%)`. The audit measured Σ h.pct_t per strategy on 2026-05-04 latest week:

| Strategy | cs.sum.te | Σ h.pct_t | Σ h.pct_s | N holdings | Comment |
|---|---|---|---|---|---|
| IDM | 6.47 | 115.9 | 62.6 | 775 | +15.9 over |
| IOP | 7.11 | 134.4 | 52.6 | 1,703 | +34.4 over |
| EM | 5.51 | 94.6 | 60.0 | 914 | -5.4 under |
| ISC | 6.25 | 107.0 | 70.6 | 2,209 | +7.0 over |
| ACWI | 6.65 | 125.3 | 56.2 | 2,048 | +25.3 over |
| GSC | 6.98 | 109.8 | 68.7 | 1,002 | +9.8 over |

Range: **94.6 → 134.4** — ±35% deviation from the claimed "~100%". Same direction-pattern hit cardSectors during the May 1 demo (holdings-sum 137% for ACWI Industrials, fixed by reading section-aggregate `cs.sectors[].tr` instead). cardSectors had a workaround because FactSet ships per-sector aggregate rows; **cardRiskByDim has no analogous workaround** because Country / Currency / Industry aggregates aren't shipped from FactSet — they're computed locally from per-holding `h.country / h.currency / h.industry` (security_ref enrichment).

**Possible causes (any one or combination):**
1. CLAUDE.md is aspirational, not actual — `%T` has been ±35% the whole time and we never noticed.
2. `%T_Check` flag filters some rows; surviving %T values don't sum to 100%.
3. `%T` is sampled (per-holding rows are emitted only above a coverage threshold, not the full universe).
4. Negative `%T` (diversifying holdings) cancels differently than the doc implies.

**Ask to FactSet team:**
- Confirm whether `%T` per-holding **should** sum to ~100% per portfolio for every weekly snapshot, or whether the documented invariant is approximate.
- If approximate: what's the expected tolerance? (Docs imply ~100%; we observe 94–134%.)
- If exact: what's filtering / sampling on the per-holding rows?
- Per-strategy variance (EM under, IOP heavily over) suggests not uniform sampling — likely related to bench universe size or %T_Check inclusion logic.

**Workaround in cardRiskByDim (shipped 2026-05-04):** footer now reports `Σ %T` (signed) and `Σ |%T|` (absolute) explicitly so the deviation is visible to PMs rather than hidden behind a misleading "% of TE" label. About-registry caveat updated.

---

## Closed / Resolved

*(none yet)*

---

## How to use this file

- Every time the user (or advisor) finds a CSV/data issue: add as a new F-id below the latest entry.
- When sending to FactSet team, copy the relevant `### F#` blocks.
- When resolved (data fixed in next CSV iteration), move to "Closed / Resolved" with date + verification commit SHA.
