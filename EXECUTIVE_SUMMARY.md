# Redwood Risk Control Panel — Executive Summary

**Date:** 2026-05-01
**For:** Alger / Redwood team meeting
**Reads in:** 90 seconds

---

## The headline

**Redwood Risk (RR) is a single-pane portfolio risk dashboard for all 7 strategies, sourced directly from FactSet, built on 7+ years of weekly history, with rigorous data-integrity discipline.** It's the morning-glance and the deep-drill, in one tool.

---

## What you can do with it

| In 30 seconds | What you see |
|---|---|
| **What's the portfolio doing right now?** | Sum-cards: TE / Active Share / Beta / Holdings / Idio% / Factor% — for any of 7 strategies |
| **What changed since last week?** | cardWeekOverWeek (top of Exposures): KPI deltas + Added/Dropped/Resized + factor rotation |
| **Where is the risk?** | Risk tab: TE decomposition + factor contribution + 7-year time series + factor correlation matrix |
| **Drill into anything** | Click any sum-card, sector, country, factor, or holding for full historical detail |

---

## The data discipline — why you can trust the numbers

**Single source of truth** — all 7 strategies parsed from FactSet via one Python parser (`factset_parser.py`, 89 pytest tests). No multiple parsing paths. No fabrication.

**Anti-fabrication policy** — every numeric cell is either:
- Source data from FactSet (the default), or
- Marked with an **ᵉ** badge + tooltip explaining how it was derived

**Verifier on every load** — `verify_factset.py` runs 22+ pass/fail checks: holding count, factor coverage, P/E populated, schema fingerprint, etc. Output: 🟢 GREEN-LIGHT or 🟡 NEEDS REVIEW or 🔴 SCHEMA DRIFT.

**Integrity assertion in the dashboard** — `_b115AssertIntegrity()` runs on every load, comparing critical fields between raw JSON and the normalized in-memory state. Drift surfaces as a console error, not a silent rendering bug.

**Per-tile provenance** — every tile has an ⓘ button explaining: what it shows, how it's computed, what the source CSV field is, and known caveats. PMs can verify any number without asking the analyst.

---

## What landed in the last 48 hours

5 critical data-integrity bugs were caught + fixed before the multi-account historical run:

1. **Date format** — EM file ships dates as `"2019-01-01 00:00:00"` (datetime with time component). Old `parse_date()` collapsed all 383 weeks of EM history to one date. Fix: extended format list. Lesson: format-tolerance must be defensive.

2. **Risk-tab vs Exposures-tab Idio/Factor split disagreed by 24.5pp** — Risk tab used a heuristic (`Σ|f.c|/100 × 1.2`); Exposures used `cs.sum.pct_specific` from source. Fix: Risk tab now reads same source. Single source of truth restored.

3. **cardRegions silently lost 46+ holdings** — `enrichHold()` was overwriting parser-shipped `h.reg` with a stale CMAP lookup that didn't include Korea, Saudi Arabia, UAE, Poland, Hungary, Malaysia, Qatar, Peru, Argentina, Singapore, Philippines. **Korea alone is 18.9% of port weight** — vanished from cardRegions until fixed.

4. **cardUnowned (Unowned Risk Contributors) was blank** — sourcing from the wrong array. Fixed to source from cs.hold filtered to bench-only-with-bw>0.

5. **Bench universe coverage 21% → 70%** — FactSet's slim Security section drops the long-tail of bench-only constituents (251/1204 = 21% on EM). But Raw Factors section ships the full 1,489-entry universe. Parser now synthesizes the missing 623 bench-only entries → coverage goes to 70% by count, 97% by weight.

---

## Where we go from here

**Today (presentation)** — runs locally on a Mac. Drop the FactSet file in `~/Downloads/`, run `./load_multi_account.sh`, dashboard opens.

**Next 2-4 weeks** — migrate to enterprise environment (PRESENTATION_DAY_GUIDE.md has the runbook):
- **Option A (recommended)** — Mac workstation on the firm network. ~30 min IT setup. Weekly cron job auto-loads the latest FactSet drop.
- **Option B (if multi-user wanted)** — Linux server with nginx + systemd timer. Hosted at `redwood-risk.firm.local`. Same dashboard, multi-user access.

**Open items needing FactSet (none blocking, all quality-of-life):**
- F11: per-holding period return (unlocks Brinson attribution)
- F12: %T_implied for the bench-only long-tail (cardUnowned more complete)
- F13: standardize date format (defensive against future format shifts)
- F14: pct_specific at portfolio-Data row directly (removes the ᵉ flag on Idio/Factor)
- F15: country-of-risk flag for ADRs

**Strategic next steps** (post-presentation):
1. **S2** — full Data Quality sidebar (today: stub via header freshness pill)
2. **B118** — period-aware Return columns across drill modals
3. **B120** — tile chrome capability sweep (Reset View, Hide, Full Screen, PNG on every tile)
4. **B124** — automated audit cadence (per-batch + bi-weekly + triggered)

---

## Why this works

**Disciplined over clever.** Every "smart" computation is a fabrication risk. The April 2026 data-integrity crisis (`LESSONS_LEARNED.md`) taught us that silent fall-throughs and "reasonable defaults" produce the worst kind of bug — wrong numbers that look right.

The dashboard is built on 6 hard rules:
1. CSV in browser = error. Single Python parser is authoritative.
2. `normalize()` is rename-only — no synthesis.
3. localStorage is for preferences only — never data.
4. Every numeric cell has provenance documented in `SOURCES.md`.
5. Integrity assertion runs on every load.
6. CSV format shift = audit every parser path.

**Built incrementally.** 138 git tags. 30+ tile-audit docs. 8-week marathon of per-tile review. Anti-pattern catalog growing.

**Iteratable.** Single HTML file, vanilla JS, Plotly charts. Every tile is independent. Adding a new view = ~150 lines. Pattern is documented.

---

## The team can use it tomorrow morning

- **PMs**: open the dashboard, scan cardWeekOverWeek for 90 seconds, drill into the 1-2 things that surprised you. Full historical context one click away.
- **Analysts**: the Risk tab gives 7-year TE decomposition, factor correlation, and the full Holdings table is searchable + sortable + filterable.
- **CIO**: every number is verifiable — click ⓘ on any tile to see source + math + caveats. No black boxes.

---

**Repo:** github.com/JGY123/RR · HEAD: ca411b3 · Tag: presentation-2026-05-01
**Single-file dashboard:** `dashboard_v7.html` (~12k lines)
**Parser:** `factset_parser.py` v3.1.0
**Documentation:** `docs/INDEX.md` for the doc map
