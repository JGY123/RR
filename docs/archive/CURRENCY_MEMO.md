# Memo: Should Currency Exposure Get More Attention?

**Written:** 2026-04-16
**Context:** The RR dashboard has holding-level country data (`h.co`) plus `factor_contr.Currency` and `factor_contr["Exchange Rate Sensitivity"]`, but no dedicated currency view. The PM's current approach is to scan country and currency together (e.g., "is the Korea overweight neutralized by KRW being flat?"). This memo argues for a modest upgrade to that workflow.

---

## Thesis

Currency is often **the second-largest driver of total return** in international portfolios — typically 20–40% of unhedged return volatility over rolling 3-year periods. For an ACWI ex-USA strategy, **failing to monitor it as a first-class dimension means risk is being taken implicitly rather than intentionally.** The current mental model (glancing at country + currency together) is directionally right but leaves three structural blind spots that a dedicated view would close.

---

## Why the country lens alone misses things

### 1. Cross-country currency correlation

Taiwan and Korea are separate country bets but TWD and KRW move with correlation ~0.7 against USD. If you're overweight both, you've implicitly made a leveraged "Asian EM currency" bet, not two independent country bets. The country table shows two separate lines; a currency view would stack them into one block and reveal the concentration.

### 2. Disconnect between country-of-listing and currency-of-risk

TSMC trades in TWD on Taiwan exchange. But TSMC's revenue is ~60% USD. A "Taiwan overweight" of 16% isn't 16% of TWD risk — it's closer to 6–8%. Country ≠ currency for multinationals. The `Exchange Rate Sensitivity` factor in FactSet data captures this mismatch; the country view doesn't.

### 3. Dollar-cycle regime shifts

In strong-USD regimes (2014–16, 2022), EM currencies drawdown together and can swamp 2-3% of alpha in a single quarter. You'd see this as "all my EM countries underperformed" in a country view, when the actual story is one currency factor blew out. Attribution gets cleaner with an FX lens.

---

## Where the current approach (country + currency glance) is right

If Korea is +2% active weight and Japan is -2% active weight, your Won / Yen net is basically zero because KRW and JPY are roughly uncorrelated. Good instinct. The country-by-country scan handles this well **when correlations are stable**.

Where it breaks: during regime shifts (e.g., BOJ policy pivot, Korean political crisis, China slowdown affecting both) correlations spike and what looked canceling-out suddenly co-moves. A currency-grouped view would show those "Asian EM" or "EMEA EM" clusters that get hidden in country-level aggregation.

---

## What the right level of attention looks like (three tiers)

### Tier A — a single weekly scan (lowest cost)

One table, 8–12 rows, sorted by `|active FX contribution|`:

| Currency | Countries rolled up | Port Wt | BM Wt | Active | FX Contrib to TE |
|---|---|---|---|---|---|
| USD | United States, ADRs | 12% | 8% | +4% | … |
| KRW | Korea | 6% | 8% | −2% | … |
| TWD | Taiwan | 16% | 14% | +2% | … |

If nothing looks unusual (no currency >3% active, no currency >5% of TE), you skip it in <15 seconds. That's the goal — **spending zero time when things are fine, and seeing the thing that matters when it's not.**

### Tier B — a correlation-aware cluster view (medium cost)

Group currencies into 4 clusters by their historical correlation:

- **USD** (USD, HKD)
- **EUR-linked** (EUR, DKK, SEK, PLN, CZK)
- **Asian EM** (KRW, TWD, THB, INR, PHP)
- **LatAm / EMEA** (BRL, MXN, ZAR, TRY)

Show cluster-level net active. This is what would have flagged the implicit "Asian EM" bet in scenario #1 above.

### Tier C — scenario stress (highest cost, rarely worth it)

"What happens to P&L if USD strengthens 5%?" — requires running through `Exchange Rate Sensitivity` factor contributions. Most investors don't need this; only useful during regime-shift moments.

---

## How to wire it in if you decide to

**Data we have:**

- `h.co` (country)
- `h.factor_contr.Currency` (per-holding currency factor contribution)
- `h.factor_contr["Exchange Rate Sensitivity"]` (FX sensitivity)
- A static country→currency mapping (~47 lines, similar to existing `COUNTRY_ISO3`)

**Minimum viable:** Tier A as a card next to the Country Exposure card on Exposures tab. ~80 lines. Shows the table above, with warning highlight when a single currency exceeds some threshold (maybe 3% active or 5% of TE contribution).

**The key UI decision:** does it live alongside the Country card, or replace one of the country views (Map/Chart/Table) with a fourth "Currency" tab? Latter is more discoverable but adds complexity.

---

## Bottom line

**Yes, build Tier A** if/when the thinking time is available. Not because currency exposure is always important, but because **the cost of glancing at it weekly is ~15 seconds** and the cost of missing a 3% FX tilt is material. The data is already in the dashboard — there's just no view into it.

Skip Tier B and C unless Tier A surfaces real issues for 2-3 weeks running.
