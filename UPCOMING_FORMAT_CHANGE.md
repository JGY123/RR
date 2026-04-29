# Upcoming FactSet Format Change — heads-up from user (2026-04-29)

In response to the missing-Security crisis on the GSC bulk pull, FactSet is reshaping the export. **This file ships before the new sample arrives so we don't lose context.**

## What's changing

### 1. Security section — slimmer rows, fewer BM-only

The Security section will now contain:
- **All portfolio holdings** (W > 0)
- **Only the BM-only holdings that meet a materiality threshold**:
  - `BW > 0.3%`, OR
  - `|risk contribution| > 0.25%` (approximate)

So the BM-only enumeration is heavily pruned. Most low-weight benchmark names won't be in Security at all.

### 2. Some columns moved out of Security → Raw Factors

To keep Security lean and put per-security attributes where they actually apply across the broader universe, these fields move:

| Column | Old location | New location |
|---|---|---|
| Market Cap (`mcap`) | Security | Raw Factors |
| ADV / Vol_30D (`adv`, `vol_30d`) | Security | Raw Factors |
| Spotlight ranks: OVER, REV, VAL, QUAL, MOM, STAB | Security | Raw Factors |

Raw Factors already covers the broader security universe (8,389 rows on GSC bulk), so it's the right home for fields that need to apply to BM-only securities the dashboard might still look up.

## What this means for our parser + dashboard

### Parser work (factset_parser.py)

The existing SEDOL → ticker-region matching (lines ~1006-1024) already populates `tkr_region` and `raw_exp` on each holding from Raw Factors. The same matching needs to extend to the new fields. Tentative changes:

```python
# In _assemble(), after the existing SEDOL match block:
# Also pull mcap, adv, ranks from Raw Factors and merge into holding objects
for h in holdings + unowned_hold:
    sedol = h.get("t") or ""
    info = sedol_to_rawfac_info.get(sedol)
    if info:
        h["mcap"]  = h.get("mcap")  or info.get("mcap")
        h["adv"]   = h.get("adv")   or info.get("adv")
        h["over"]  = h.get("over")  or info.get("over")
        h["rev"]   = h.get("rev")   or info.get("rev")
        h["val"]   = h.get("val")   or info.get("val")
        h["qual"]  = h.get("qual")  or info.get("qual")
        h["mom"]   = h.get("mom")   or info.get("mom")
        h["stab"]  = h.get("stab")  or info.get("stab")
```

Need to verify which Raw Factors columns will carry these new fields once the new sample lands. The header-driven schema discovery should pick them up automatically — just need to update the field-name → output-key mapping table (look around line 668 where `SEC_MCAP`, `SEC_PRICE_VOL`, `SEC_VOL_30D` are mapped today inside the Security extractor).

### Dashboard impact (zero changes if parser merges correctly)

By merging the moved fields back onto the holding objects in the parser, downstream JS code reading `h.mcap`, `h.over`, `h.rev`, `h.val`, `h.qual`, `h.mom`, `h.stab` keeps working unchanged.

Survey of affected lines (counted 2026-04-29):
- 34 lines in `dashboard_v7.html` reference the moved fields directly on `h.*`
- All of them would silently become null if we DON'T merge from Raw Factors after the format change.

Already-aware tiles using these fields:
- cardSectors / cardCountry / cardGroups / cardRegions — for sector-level ORVQ averages (loops over holdings, summing `h.over`, `h.rev`, etc.)
- Idiosyncratic modal — uses `h.mcr` (still in Security)
- Holdings tab — uses `h.over` + ranks for the rank column display
- Spotlight (cardRanks) — uses ranks for quintile bucketing
- Top contributors strip — uses `h.tr`, `h.mcr` (still in Security)

### BM-only side-effects

Tiles that enumerate BM-only holdings will now show fewer items:
- Sector drill bench-only table
- "Top 10 Benchmark Weights" in AS modal
- cardUnowned (full bench-only enumeration)

These will display only the materially-large BM-only names. Should be flagged in tile copy: "Showing benchmark holdings above 0.3% weight or 0.25% risk contribution; smaller bench-only holdings excluded for compactness."

## Action items when the new sample lands

1. **Run the parser** — header-driven so it should ingest the new shape automatically
2. **Verify merge** — confirm `h.mcap`, `h.adv`, ranks are populated on portfolio holdings
3. **Smoke-test the dashboard** — sector ORVQ averages, holdings tab, Spotlight should all populate
4. **Update tile copy** for BM-only views: explicit note about the materiality filter
5. **Re-run verifier** — schema fingerprint will flag drift; delete baseline to acknowledge the new format

## Sources of truth on this change

- User heads-up: 2026-04-29 conversation
- Reason: solving the missing-Security problem from the GSC bulk pull (sample-4)
- Related: factset_gsc_response_email.md (the original ask that led to this)
