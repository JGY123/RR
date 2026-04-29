# Performance Optimization

## What it does
The dashboard is now ~7,500+ lines with 200+ functions. With 2,500+ holdings and 47 Plotly charts, it needs performance tuning.

## 1. Lazy chart rendering
Only render Plotly charts that are in the viewport. Charts below the fold render when scrolled into view.
```javascript
// Use IntersectionObserver for lazy chart rendering
const chartObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if(e.isIntersecting && !e.target.dataset.rendered) {
      e.target.dataset.rendered = '1';
      let fn = e.target.dataset.chartFn;
      if(fn && typeof window[fn] === 'function') window[fn](cs);
    }
  });
}, {threshold: 0.1});

// Register chart divs
['facButtDiv','countryMapDiv','scatDiv','treeDiv','mcrDiv','frbDiv','facWaterfallDiv','attribChartDiv','secChartDiv'].forEach(id => {
  let el = document.getElementById(id);
  if(el) chartObserver.observe(el);
});
```

## 2. Debounce strategy switching
When clicking through strategies quickly, debounce the render to avoid queueing up multiple expensive renders:
```javascript
let _goDebounce;
function go(id){
  if(!A[id])return;
  cs=A[id];
  clearTimeout(_goDebounce);
  _goDebounce = setTimeout(()=>upd(), 150);
}
```

## 3. Reuse Plotly instances
Instead of `Plotly.newPlot` every render (which destroys and recreates), use `Plotly.react` for updates:
```javascript
// Check if plot already exists
if(document.getElementById(divId)?.data) {
  Plotly.react(divId, newData, newLayout);
} else {
  Plotly.newPlot(divId, newData, newLayout, plotCfg);
}
```

## 4. Virtual scroll for large tables
Holdings table with 775+ rows: use virtual scrolling that renders only visible rows:
- Keep a 20-row buffer above and below viewport
- Total height simulated with a spacer div
- On scroll, shift rendered window
- Already partially done with chunked rendering — enhance to be fully virtual

## 5. Minimize DOM size
- Factor Attribution table: 122 rows all rendered. Show top 20, "Load all" button for rest
- Country table: show top 15, "Show all N countries" button
- Reduce hidden tab content: defer Risk/Holdings tab rendering until tab is clicked

## 6. Bundle size
- Plotly is 3.5MB — consider loading plotly-basic (1.2MB) which covers scatter, bar, choropleth, pie
- html2canvas.min.js: only needed for screenshot — load on demand when user clicks a screenshot action
