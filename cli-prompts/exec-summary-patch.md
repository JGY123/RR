# Executive Summary Card — Auto-Generated Weekly Insights

## What it does
A compact card that appears ABOVE the hero risk card showing 3-5 auto-generated bullet points about what changed this week. Computed from data, not hardcoded.

## Logic (inside rExp() before the hero card HTML):

```javascript
function generateExecSummary(s){
  let bullets=[];
  let hist=s.hist.sum||[];
  let prev=hist.length>=2?hist[hist.length-2]:null;
  let cur=hist[hist.length-1]||{};
  
  // 1. TE direction
  if(prev&&cur.te!=null&&prev.te!=null){
    let d=+(cur.te-prev.te).toFixed(2);
    if(Math.abs(d)>0.05){
      bullets.push({
        icon:d>0?'📈':'📉',
        text:`Tracking error ${d>0?'rose':'fell'} ${Math.abs(d).toFixed(2)}% to ${cur.te.toFixed(2)}% this week`,
        cls:d>0?'warn':'good'
      });
    }
  }
  
  // 2. Biggest sector bet
  let topSec=s.sectors?.reduce((max,sec)=>Math.abs(sec.a)>Math.abs(max.a)?sec:max,{a:0,n:''});
  if(topSec&&topSec.n){
    bullets.push({
      icon:topSec.a>0?'🟢':'🔴',
      text:`Largest sector bet: ${topSec.n} at ${topSec.a>0?'+':''}${topSec.a.toFixed(1)}% active`,
      cls:'neutral'
    });
  }
  
  // 3. Concentration risk
  let topHold=s.hold.filter(h=>!isCash(h)&&(h.p||0)>0).sort((a,b)=>Math.abs(b.tr||0)-Math.abs(a.tr||0))[0];
  if(topHold&&Math.abs(topHold.tr)>5){
    bullets.push({
      icon:'⚠️',
      text:`${topHold.n||topHold.t} contributes ${Math.abs(topHold.tr).toFixed(1)}% of total TE — monitor concentration`,
      cls:'warn'
    });
  }
  
  // 4. Factor tilt
  let topFac=s.factors?.reduce((max,f)=>Math.abs(f.a||0)>Math.abs(max.a||0)?f:max,{a:0,n:''});
  if(topFac&&topFac.n&&Math.abs(topFac.a)>0.2){
    bullets.push({
      icon:'🎯',
      text:`Strongest factor tilt: ${topFac.n} at ${topFac.a>0?'+':''}${topFac.a.toFixed(2)} active exposure`,
      cls:'neutral'
    });
  }
  
  // 5. Quality signal
  let avgRank=s.hold.filter(h=>!isCash(h)&&(h.p||0)>0&&h.over!=null).reduce((s,h,_,a)=>s+h.over/a.length,0);
  if(avgRank<2.5){
    bullets.push({icon:'✅',text:`Portfolio avg rank Q${avgRank.toFixed(1)} — above-average quality`,cls:'good'});
  } else if(avgRank>3.5){
    bullets.push({icon:'⚠️',text:`Portfolio avg rank Q${avgRank.toFixed(1)} — below-average quality, review positioning`,cls:'warn'});
  }
  
  return bullets.slice(0,4);
}
```

## HTML (insert before the hero-risk div):

```html
<div style="padding:10px 16px;margin-bottom:10px;background:linear-gradient(135deg,rgba(99,102,241,.06),rgba(139,92,246,.04));border:1px solid rgba(99,102,241,.15);border-radius:10px">
  <div style="font-size:9px;font-weight:700;color:var(--pri);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Weekly Insights</div>
  ${bullets.map(b=>`<div style="display:flex;gap:8px;align-items:flex-start;padding:3px 0;font-size:11px;color:${b.cls==='warn'?'var(--warn)':b.cls==='good'?'var(--pos)':'var(--txth)'}">
    <span>${b.icon}</span><span>${b.text}</span>
  </div>`).join('')}
</div>
```

## Notes
- Renders 3-4 bullets max
- Auto-computed from current strategy data
- Updates when switching strategies
- Colors: warn=amber, good=green, neutral=white
- Will be much richer with full 3-year history (TE trend, active share drift, factor rotation)
