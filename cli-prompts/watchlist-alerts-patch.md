# Watchlist + Threshold Alerts System

## What it does
PM sets personal thresholds on any metric. When data is loaded and a threshold is breached, an alert fires. Thresholds persist in localStorage.

## 1. Threshold configuration
Settings gear icon → "Alert Thresholds" panel:
```
TE Warning:     [  6.0  ] %    (default: 6)
TE Critical:    [  8.0  ] %    (default: 8)
Single-name TE: [ 10.0  ] %    (default: 10)
Cash Max:       [  5.0  ] %    (default: 5)
Active Share Min:[ 70.0 ] %    (default: 70)
Q5 Weight Max:  [ 15.0  ] %    (default: 15)
Factor Exp Max: [  0.5  ] σ    (default: 0.5)
```

## 2. Threshold checking
On every `upd()` call, run `checkThresholds(cs)`:
- Compare each metric against configured thresholds
- Return array of breaches: [{metric, value, threshold, severity}]
- Feed breaches into the risk alerts banner (patch 3)

## 3. Holding watchlist
PM can star holdings → they show in a persistent "Watchlist" section at the top of Holdings tab
Watchlist shows: ticker, name, current weight, weight change since last upload, TE contribution
Stored in localStorage: `rr_watchlist = ['NBIS','6857','ASND']`

## 4. Position limit alerts
For watchlisted holdings, set per-holding limits:
- Max weight: alert if position grows above X%
- Max TE: alert if TE contribution exceeds X%
- These are stored alongside the watchlist

## 5. Weekly delta summary
When a new file is uploaded, auto-compare vs the previous upload:
- New positions added
- Positions closed
- Biggest weight increases / decreases
- TE changes by sector
Show as a dismissable "What Changed" banner
