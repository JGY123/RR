# Scenario Analysis / What-If Engine

## What it does
PM can simulate changes to the portfolio and see projected impact on TE, factor exposures, and risk budget WITHOUT modifying actual data. A "sandbox" mode.

## 1. Position Simulator
In the Holdings tab, add a "Simulate" toggle button. When active:
- Each holding row gets a weight slider (or editable input) next to Port%
- Changing the weight recalculates in real-time:
  - New total TE (approximate: scale MCR by weight change ratio)
  - New factor exposure (scale factor_contr by weight ratio)
  - New sector/country allocation
  - New active share
- Show delta badges: "TE: 5.69% → 5.42% (↓0.27)" in amber
- "Reset" button restores original weights

## 2. Trade Impact Preview
"What if I buy/sell X?" mini-form:
- Input: Ticker + target weight (or delta weight)
- Output: projected TE change, factor exposure changes, sector weight changes
- Uses linear approximation: ΔTE ≈ Σ(MCR_i × Δw_i / w_i)
- Shows a before/after comparison card

## 3. Factor Stress Test
"What if Volatility factor spikes 2σ?"
- Select a factor + magnitude (1σ, 2σ, 3σ)
- Compute portfolio impact: exposure × factor return × magnitude
- Show which holdings are most affected
- Display as a waterfall: factor shock → per-holding impact → total portfolio impact

## 4. Benchmark Switch
"What if we used MSCI World instead of MSCI EAFE?"
- This requires loading a second benchmark dataset (not available yet)
- For now: stub the UI with a "Coming soon" message
- When available: re-compute all active weights, TE, and attribution against the new benchmark

## Implementation:
```javascript
let _simMode = false;
let _simWeights = {}; // ticker -> simulated weight

function toggleSimMode(){
  _simMode = !_simMode;
  if(!_simMode) _simWeights = {};
  renderHoldTab();
}

function simWeight(ticker, newW){
  _simWeights[ticker] = newW;
  recalcSimStats();
}

function recalcSimStats(){
  let hold = cs.hold.filter(h=>!isCash(h)&&(h.p||0)>0);
  let simTE = 0;
  hold.forEach(h => {
    let w = _simWeights[h.t] ?? h.p;
    let ratio = h.p > 0 ? w / h.p : 1;
    simTE += Math.abs((h.tr||0) * ratio);
  });
  // Show simulated TE vs actual
  let delta = simTE - hold.reduce((s,h)=>s+Math.abs(h.tr||0),0);
  // Update UI...
}
```

## Priority: MEDIUM — extremely valuable for daily PM workflow but complex to get right.
The linear approximation is good enough for small changes (±1-2% weight moves) but breaks down for large restructuring. Add a disclaimer: "Approximate impact — assumes linear MCR. Actual impact may differ for large changes."
