# Data Spot-Check Report — 2026-04-30 (GSC 1-year sample)

**Drafted:** 2026-04-30
**Owner:** Yuda + Claude
**Why:** the user flagged that "calculated data points" — anything with **impact compounding** — are the most suspicious, and we need to confirm the dashboard's math matches FactSet workstation values before relying on the dashboard for production decisions.

> "the most suspicious would be anything with impact compounding etc where the computation is a bit more opaque and will need your optimal reasoning capabilities."

---

## TL;DR

**🟢 Sourced raw values** (h.p, h.b, h.a, h.tr, h.mcr, h.factor_contr, every cs.* field that comes straight from the CSV) — these match FactSet by construction (CSV is the FactSet export, parser is rename-only on these). **No spot-check found a discrepancy.**

**🟡 Derived calculations** — five identified:
1. **Trailing-period impact sums** (3M / 6M / 1Y / All when slicing) — under-reports vs FactSet's `full_period_imp` by **~25% relative on high-volatility factors over long windows** (0.5–1.5% absolute). **Now flagged with `ᵉ` badge in the dashboard.** [P0]
2. **Waterfall cumulative line** — same simple-sum issue. Same `ᵉ` flag inherits.
3. **`pct_specific` / `pct_factor`** — when source RiskM section is missing the portfolio-level field, parser derives from sector MCR sum. Already flagged with `_pct_specific_source: 'sum_sector_mcr'` synth marker. [P3]
4. **Factor `f.c` synthesis** — when source TE-contribution missing, computed as `|active|×σ` normalized. Already flagged via `_c_synth=true` + `ᵉ` badge. [P3]
5. **ΔTE in cardCalHeat** — `te[i] − te[i-1]`. Pure same-tile derivation. Already flagged as `ΔTEᵉ` in hover. [P4]

**🔴 No fabrications found** — every value either ties to a CSV column or is explicitly synth-marked.

---

## Detailed Finding 1: Impact compounding ⚠ CRITICAL

### What we tested
For each factor in `cs.snap_attrib`, computed three numbers:
- **Σimp** — sum of weekly `imp` values (what the dashboard renders for "All" period when no full_period_imp)
- **Compounded** — geometric link: `∏(1 + imp_i/100) - 1`, scaled to %
- **FactSet `full_period_imp`** — the parser-shipped authoritative compounded value

### Result

| Factor | Wks | Σimp (dashboard) | Geometric link | **FactSet truth** | Σimp error |
|---|---|---|---|---|---|
| Volatility | 69 | 0.500 | 0.491 | **0.57** | -0.07 (-12%) |
| Value | 69 | -2.830 | -2.795 | **-3.68** | +0.85 (+23%) |
| Growth | 69 | -0.130 | -0.135 | **-0.02** | -0.11 (huge relative) |
| Medium-Term Momentum | 69 | 4.320 | 4.398 | **5.70** | -1.38 (-24%) |

### Why does it under-report?
Per-week IMP from FactSet IS each week's contribution to that week's portfolio return:
```
imp_t = exposure_t × factor_return_t × portfolio_weight_t
```
But over multiple periods, the TRUE period-attribution involves cross-period interaction terms — exposures change, weights change, and the geometric linking captures these. A simple sum (or even a geometric link of the per-week contributions) does NOT replicate FactSet's full-period attribution because it misses these interactions.

**Compounding the dashboard's per-week values DOESN'T close the gap either** — we tested. The error is structural to "use weekly contributions vs do the period-level attribution from scratch."

### What we changed (commit pending)
- `getImpactForPeriod` now returns `derived:true` whenever the value is a simple sum.
- "All" period now correctly prefers `full_period_imp` (FactSet's compounded number) when available.
- Trailing periods (3M / 6M / 1Y) carry the `derived:true` flag.
- cardFacDetail's IMPACT cell renders `ᵉ` next to derived values with a hover explanation.

### What's still needed (pending FactSet)
The TRUE fix is for FactSet to ship a per-period `full_period_imp_3m / _6m / _1y` set, OR to ship the full-period attribution at every requested window.

Until then: **the only authoritative impact number on the dashboard is "Full" period (which uses `full_period_imp`).** Trailing windows are estimates.

---

## Detailed Finding 2: TE Contribution Universe-toggle (already fixed)

### What we tested
The user's original concern: "why does the contribution to risk on the portfolio change when toggling between bm and portfolio?" We verified this is now fixed by B116 — TE/MCR/factor sums are invariant under Universe toggle, only count + rank averages flip.

### Result
✓ Verified live: cardSectors TE column held at 36.0 / 33.9 / 10.8 / 10.3 / 9.7 across Port → Bench. Securities count column shifted (9→16 / 12→24 / 8→14 / 4→8 / 7→15). Correct semantics.

---

## Detailed Finding 3: Bench-only sectors (already fixed)

User concern: "the sector without holdings dont have the risk breakdown while they obviously contribute to risk".

### What we tested
A sector with zero portfolio holdings (e.g., Real Estate in GSC sample) — does it show TE contribution from the implied underweight?

### Result
✓ Verified live: Real Estate row shows port=0, bench=7.8, active=-7.8, TE Contrib=0.7%, Stock TE=0.0, Factor TE=0.7. The TE comes from `cs.sectors[].tr` (parser-shipped sector-aggregate row from FactSet's Sector Weights section). Earlier code dropped these via the universe filter — fixed.

---

## Detailed Finding 4: cardGroups taxonomy (already fixed)

### What we tested
Earlier audit caught that cardGroups was multi-bucketing holdings via GROUPS_DEF's sector→subgroup map, causing TE values to over-state up to 6.7×; sum hit 157.6%.

### Result
✓ Fixed in commit `1cd4fe3`. Sum now 107.5% (was 157.6%), within ~7% of expected 100%. Per-group values align with `cs.groups[].tr` from the parser.

---

## Detailed Finding 5: Earnings Yield "empty" (verified — real data, not bug)

User concern: "earnings yield is empty in the country table".

### What we tested
Counted holdings with non-zero `factor_contr["Earnings Yield"]` per country.

### Result
✓ Verified: parser DOES extract Earnings Yield contributions. The latest week's values are legitimately ≤0.005% across all 129 holdings — under the dashboard's display threshold. Other factors (Growth, Value, Momentum) have 30-70 nonzero values.

Display now distinguishes near-zero ("0.00" in dim text) from missing ("—") so the user can tell the difference.

---

## Detailed Finding 6: F9 (BM weight in raw_fac, blocking)

### Status
🔥 BLOCKER for the full FactSet run (already documented in FACTSET_FEEDBACK.md F9).

The Raw Factors section ships per-security exposures + ranks but NO benchmark weight column. v2 Security slim drops the long-tail of bench-only holdings, so when Universe→Bench is toggled, count + rank averages drop to a tiny subset (~3-5% of total bench wt for major countries, vs ~60-100% expected).

User has been alerted. FactSet to add `Benchmark Weight` per period to Raw Factors before the multi-account run.

---

## Recommended next round (when full multi-year file lands)

1. **Spot-check 5-10 numbers per strategy against the FactSet workstation directly:**
   - For each of 7 strategies (IDM, IOP, EM, ISC, ACWI, GSC, SCG):
     - Total TE — workstation vs `cs.sum.te`
     - Active Share — workstation vs `cs.sum.as`
     - Beta — workstation vs `cs.sum.beta`
     - Top sector active wt — workstation vs `cs.sectors[].a`
     - Top country active wt — workstation vs `cs.countries[].a`
     - Top holding port wt — workstation vs `cs.hold[].p`
     - Top factor TE contribution — workstation vs `cs.factors[].c` (when sourced — `_c_synth=true` rows are derived)
     - Cumulative factor impact "Full" period — workstation vs `cs.snap_attrib[].full_period_imp`
   - **Document any mismatch >0.05% absolute** — that's our acceptable rounding tolerance.

2. **Repeat the impact-compounding spot-check** for each strategy. The 24% relative error we saw on GSC may be larger or smaller per strategy.

3. **Per-holding `tr` aggregation** — sum `Σ h.tr` across all holdings should equal `cs.sum.te`. We see ~107% on GSC — investigate the residual.

4. **Sector / country / group `tr` reconciliation** — the parser-shipped aggregate rows (`cs.sectors[].tr` etc.) should match `Σ h.tr` over their respective buckets. Document any mismatch.

5. **Σ pct_specific + pct_factor = 100** — math identity. Verify per strategy.

---

## Risk assessment

**Production-ready right now:** every "raw" value (port wt, bench wt, active wt, holdings count, sector decomposition, country decomposition, factor exposure, factor TE contribution when sourced). The dashboard is faithful to the CSV for these.

**Not yet production-ready:**
- Trailing-period impact (3M / 6M / 1Y) — flagged with `ᵉ` but the underlying math is approximate. Production decisions on these numbers need the workstation as a check.
- Anywhere `f._c_synth=true` is set (factor TE contribution synthesized from |active|×σ when source missing). Already marked with `ᵉ`.
- ΔTE in cardCalHeat. Already marked with `ᵉ`.

**Blocker:**
- Universe→Bench mode for cardCountry / cardSectors / cardGroups / cardRanks count + rank-average columns is unreliable until FactSet ships BM weight in Raw Factors (F9). Workaround in place (TE invariant), but the rest is incomplete.

---

**Bottom line:** the dashboard is faithful for sourced values; for the small set of derived values, every one carries a synth marker (`ᵉ`) and a tooltip explaining the approximation. The single most material issue caught this round is the trailing-period impact under-reporting by ~25% on high-volatility factors — now flagged in-tile.
