# 18 Style Snapshot Granular Data Integration

## Data source: cs.snap_attrib (object, 122 entries)
Keys are factor/country/industry/currency names. Each value has: exp, ret, imp, dev, cimp, risk_contr, full_period_imp, full_period_cimp, hist[{d, exp, ret, imp, dev, cimp, risk_contr}]

## Integration points (5 changes):

### 1. Factor Detail table: fill non-style factor data
Currently Country, Currency, Industry, Local, Market show "—" for TE%, Return, Impact.
In the rWt/rFac rendering for factor rows, check if snap_attrib has data for the factor name:
```javascript
// In factor row rendering:
let snapData = cs.snap_attrib?.[f.n];
if(snapData) {
  f.ret = f.ret ?? snapData.ret;
  f.imp = f.imp ?? snapData.imp;
  f.dev = f.dev ?? snapData.dev;
  // risk_contr from snap is the real TE contribution percentage
  if(f.c === 0 && snapData.risk_contr) f.c = snapData.risk_contr;
}
```
Apply this in enrichAllGroupings() or in the factor table renderer.

### 2. Country drill: show FactSet country-factor attribution
In oDrCountry(), after the holdings-based stats, add a "Country Factor Attribution" section:
```javascript
let countrySnap = cs.snap_attrib?.[countryName];
if(countrySnap) {
  // Show: Active Exposure, Return, Impact, Std Dev, Risk Contribution
  // Plus weekly time series chart from countrySnap.hist
}
```
This gives the REAL FactSet country-factor exposure/return/impact, not just aggregated from holdings.

### 3. Factor Risk Map: use real risk_contr for non-style factors
Currently non-style factors (Market, Industry, Country, Currency) are excluded from the bubble chart because f.c=0 and f.dev=null.
Fix: merge snap_attrib data into cs.factors during enrichment:
```javascript
cs.factors.forEach(f => {
  let snap = cs.snap_attrib?.[f.n];
  if(snap) {
    if(f.dev == null) f.dev = snap.dev;
    if(f.c === 0 && snap.risk_contr) f.c = snap.risk_contr;
  }
});
```
This will make all 17 factors show up as bubbles with real size/position.

### 4. Currency Exposure section (NEW)
Add a new tile between Country and Redwood Groups showing currency exposure:
- Table with 18 currencies: Name, Exposure, Return, Impact, Std Dev, Risk Contribution
- Bar chart showing active exposure per currency
- Data from cs.snap_attrib entries where key is 3-letter uppercase (USD, EUR, JPY, etc.)
- Period selector reusing existing _attribPeriod pattern

### 5. Industry Attribution enrichment
The Factor Attribution table already shows 65 industries. But the country drill doesn't show industry breakdown within that country.
In oDrCountry(), add: "Top Industries in [Country]" section by filtering snap_attrib entries that are industries AND cross-referencing holdings in that country by industry.

## Priority order: 1 (fills blanks), 3 (makes bubble chart complete), 2 (enriches drills), 4 (new tile), 5 (nice-to-have)
