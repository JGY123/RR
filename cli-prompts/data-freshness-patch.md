# Data Freshness + Auto-Reload + Upload History

## What it does
Shows clearly when data was loaded, how old it is, and provides quick access to reload or switch between uploaded files.

## 1. Data Freshness Indicator (header bar)
Next to the strategy dropdown, show:
- "Data: Apr 7, 2026 · 3 weeks · loaded 2m ago"
- If data is >1 day old: amber warning badge "⚠ Stale data"
- If data covers <4 weeks: info badge "ℹ Limited history (3 weeks)"

Implementation:
```javascript
function dataFreshnessHtml(){
  let reportDate = cs.current_date;
  let histLen = cs.hist?.sum?.length || 0;
  let dateStr = reportDate ? isoDate(reportDate) : 'Unknown';
  let staleBadge = ''; // TODO: compare to today's date
  let histBadge = histLen < 4 ? `<span style="color:var(--warn);font-size:9px">ℹ ${histLen}wk history</span>` : '';
  return `<span style="font-size:10px;color:var(--txt)">Data: ${dateStr} · ${histLen} wk ${histBadge}</span>`;
}
```

Add to the header bar next to the date navigator.

## 2. Upload History Panel
The history panel already exists (histPanel). Enhance:
- Show file name, upload time, strategy count, report date for each entry
- "Pin" button to keep a file in history (prevent auto-eviction)
- "Compare" button to diff two uploads side by side (delta report)
- Re-enable localStorage caching (currently disabled at line saveToHistory)

## 3. Auto-Refresh Indicator
When latest_data.json is auto-loaded:
- Show a subtle green pulse on the strategy dropdown for 3 seconds
- Toast message: "Auto-loaded latest data — 7 strategies"
- This already exists partially — enhance the visual feedback

## 4. CSV Drop Zone Enhancement
The upload zone should:
- Accept drag-and-drop of JSON files too (currently CSV/TXT only — JSON is already supported in the handler)
- Show a "Recent files" section with the last 3 uploaded filenames
- Show parse progress with a determinate progress bar (count rows parsed / total rows)
