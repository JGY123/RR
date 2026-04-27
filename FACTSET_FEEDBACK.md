# FactSet Feedback — Running Tracker

**Purpose:** capture every CSV-format issue surfaced during dashboard development. Each item is a question, request, or fix to relay to the FactSet team. Append-only.

**Date opened:** 2026-04-27
**Owner:** RR product (user) drives what gets sent to FactSet; advisor adds technical context.

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

### F7 · Per-currency / per-industry / per-country attribution rows in 18 Style Snapshot
**Status:** USER OBSERVATION — confirmed present.
**What's there:** the snap_attrib dict already has 122+ keys including `BRL`, `Hungary`, `HUF`, `Semiconductors & Semiconductor Equipment`, `Oil, Gas & Consumable Fuels`, etc. These ARE granular per-currency/industry/country attribution rows.
**Implication:** B110 (sub-factor drill on Country/Currency/Industry) doesn't need new CSV data — it just needs to consume the existing snap_attrib entries. **Big unblock for B110.**

---

## Closed / Resolved

*(none yet)*

---

## How to use this file

- Every time the user (or advisor) finds a CSV/data issue: add as a new F-id below the latest entry.
- When sending to FactSet team, copy the relevant `### F#` blocks.
- When resolved (data fixed in next CSV iteration), move to "Closed / Resolved" with date + verification commit SHA.
