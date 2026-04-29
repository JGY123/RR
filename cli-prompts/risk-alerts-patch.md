# Risk Alerts Banner — Anomaly Detection

## What it does
A dismissable alerts strip below the exec summary that auto-detects portfolio anomalies and surfaces them as colored badges. Each alert is actionable — clicking it scrolls to or opens the relevant tile/drill.

## Alert detection logic:

```javascript
function detectRiskAlerts(s){
  let alerts=[];
  
  // 1. TE above threshold
  if(s.sum.te>8) alerts.push({severity:'red',text:`TE at ${s.sum.te.toFixed(2)}% — above 8% threshold`,action:()=>oDrMetric('te')});
  else if(s.sum.te>6) alerts.push({severity:'amber',text:`TE elevated at ${s.sum.te.toFixed(2)}%`,action:()=>oDrMetric('te')});
  
  // 2. Single-name concentration
  let topTE=s.hold.filter(h=>!isCash(h)&&(h.p||0)>0).sort((a,b)=>Math.abs(b.tr||0)-Math.abs(a.tr||0))[0];
  if(topTE&&Math.abs(topTE.tr)>10) alerts.push({severity:'red',text:`${topTE.n||topTE.t} contributes ${Math.abs(topTE.tr).toFixed(1)}% TE — high concentration`,action:()=>oSt(topTE.t)});
  
  // 3. Cash drag
  if(s.sum.cash>5) alerts.push({severity:'amber',text:`Cash at ${s.sum.cash.toFixed(1)}% — above normal range`,action:()=>oDrMetric('cash')});
  
  // 4. Q5 overweight
  let q5=s.hold.filter(h=>!isCash(h)&&(h.p||0)>0&&h.r===5);
  let q5wt=q5.reduce((sum,h)=>sum+(h.p||0),0);
  if(q5wt>15) alerts.push({severity:'amber',text:`Q5 holdings: ${q5wt.toFixed(1)}% of portfolio — worst-ranked concentration`,action:()=>filterByRank(5)});
  
  // 5. Factor exposure outlier
  let bigFac=s.factors?.filter(f=>Math.abs(f.a||0)>0.5);
  if(bigFac?.length) alerts.push({severity:'info',text:`${bigFac.length} factor(s) with exposure >0.5σ: ${bigFac.map(f=>f.n).join(', ')}`,action:()=>document.getElementById('cardFacButt')?.scrollIntoView({behavior:'smooth'})});
  
  // 6. Active share decline
  let hist=s.hist.sum||[];
  if(hist.length>=2){
    let asDelta=hist[hist.length-1].as-hist[hist.length-2].as;
    if(asDelta<-1) alerts.push({severity:'amber',text:`Active share fell ${Math.abs(asDelta).toFixed(1)}% this week`,action:()=>oDrMetric('as')});
  }
  
  return alerts;
}
```

## HTML:
```html
<!-- Insert after exec summary, before hero card -->
<div id="riskAlerts" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">
  ${alerts.map(a=>`<button onclick="..." style="
    display:flex;align-items:center;gap:4px;padding:4px 10px;border-radius:16px;border:1px solid;
    font-size:10px;font-family:inherit;cursor:pointer;transition:all .15s;
    background:${a.severity==='red'?'rgba(239,68,68,.1)':a.severity==='amber'?'rgba(245,158,11,.1)':'rgba(99,102,241,.08)'};
    color:${a.severity==='red'?'var(--neg)':a.severity==='amber'?'var(--warn)':'var(--pri)'};
    border-color:${a.severity==='red'?'rgba(239,68,68,.3)':a.severity==='amber'?'rgba(245,158,11,.3)':'rgba(99,102,241,.2)'}
  ">${a.severity==='red'?'🔴':a.severity==='amber'?'🟡':'ℹ️'} ${a.text}</button>`).join('')}
</div>
```

## Behavior
- Each alert is a clickable pill
- Clicking opens the relevant drill or scrolls to the tile
- Alerts auto-update when switching strategies
- No alerts = the strip is hidden (display:none)
