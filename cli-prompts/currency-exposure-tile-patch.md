# Currency Exposure Tile (New)

## What it does
A new tile between Country Exposure and Redwood Groups showing the portfolio's currency exposure profile. Currently no currency visualization exists despite having 18 currencies in snap_attrib.

## Data source: cs.snap_attrib
Filter entries where key is 3-letter uppercase: USD, EUR, JPY, GBP, CHF, AUD, CAD, etc.
Each has: exp (active exposure), ret (return), imp (impact), dev (std dev), risk_contr, hist[].

## Layout:
### Card: "Currency Exposure"
- Toggle: Chart | Table
- Color-by dropdown (matching country pattern): Active Exposure | Risk Contribution | Impact

### Chart view: Horizontal butterfly
Left side: negative exposures (underweight currencies)
Right side: positive exposures (overweight currencies)
Sorted by absolute exposure. Color by risk contribution.
Width proportional to exposure magnitude.

### Table view:
| Currency | Exposure | Std Dev | Return | Impact | Risk % |
|----------|----------|---------|--------|--------|--------|
| JPY | -0.06 | 8.83 | +2.11 | -0.13 | -0.29 |
| EUR | +0.04 | 5.12 | -0.88 | -0.04 | +0.12 |
| USD | +0.08 | 3.45 | +0.22 | +0.02 | +0.15 |

All columns sortable. Click row → opens drill-down showing:
- Weekly exposure history chart
- Holdings contributing to this currency exposure
- Factor interaction (how currency correlates with other factor exposures)

### Key insight row:
"Net long JPY (-0.06), net short EUR (+0.04). JPY is the most volatile currency exposure (σ=8.83) contributing -0.29% risk."

## HTML insertion point:
After the country card (cardCountry) and before Redwood Groups (cardGroups) in the rExp() template.

## Implementation:
```javascript
function rCurrencyExposure(s){
  let snap = s.snap_attrib || {};
  let currencies = Object.entries(snap)
    .filter(([k,v]) => k.length === 3 && k === k.toUpperCase() && v.exp != null)
    .map(([k,v]) => ({name:k, ...v}))
    .sort((a,b) => Math.abs(b.exp) - Math.abs(a.exp));
  
  if(!currencies.length) return '';
  
  // Build chart + table
  // ...
}
```
