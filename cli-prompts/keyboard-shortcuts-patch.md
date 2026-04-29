# Keyboard Shortcuts + Navigation Improvements

## What it does
Power-user keyboard shortcuts for fast navigation, plus a help overlay showing all shortcuts.

## Shortcuts to add:

### Navigation
- `1` / `2` / `3` — Switch to Exposures / Risk / Holdings tab
- `←` / `→` — Previous / Next strategy
- `↑` / `↓` — Previous / Next week (when week selector is available)
- `Home` — Scroll to top of current tab
- `End` — Scroll to bottom

### Actions
- `c` — Open Compare mode (strategy comparison)
- `f` — Focus the search box (holdings tab) or Cmd+K search
- `?` — Show keyboard shortcuts help overlay
- `Escape` — Close any open modal/popup/overlay

### Quick jump (when on Exposures tab)
- `s` — Jump to Sector table
- `r` — Jump to Factor Risk Map
- `m` — Jump to Country Map
- `h` — Jump to Holdings (switch tab)
- `q` — Jump to Quant Ranks

## Implementation:
```javascript
document.addEventListener('keydown', e => {
  // Skip if user is typing in an input/search
  if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
  
  let key = e.key.toLowerCase();
  
  // Tab switching
  if(key === '1') { switchTab('exposures'); e.preventDefault(); }
  if(key === '2') { switchTab('risk'); e.preventDefault(); }
  if(key === '3') { switchTab('holdings'); e.preventDefault(); }
  
  // Strategy navigation
  if(key === 'arrowleft') { /* prev strategy */ }
  if(key === 'arrowright') { /* next strategy */ }
  
  // Escape closes modals
  if(key === 'escape') { ALL_MODALS.forEach(id => $(id)?.classList.remove('show')); }
  
  // Quick jumps
  if(key === 's') document.getElementById('cardSectors')?.scrollIntoView({behavior:'smooth'});
  if(key === 'r') document.getElementById('cardFacButt')?.scrollIntoView({behavior:'smooth'});
  if(key === 'm') document.getElementById('cardCountry')?.scrollIntoView({behavior:'smooth'});
  if(key === 'q') document.getElementById('cardRanks')?.scrollIntoView({behavior:'smooth'});
  
  // Help overlay
  if(key === '?') toggleShortcutHelp();
  
  // Compare
  if(key === 'c' && typeof openCompare === 'function') openCompare();
});
```

## Help overlay (triggered by '?'):
Small floating card showing all shortcuts in a 2-column grid.
Dark semi-transparent background, positioned bottom-right.
Auto-dismiss after 5 seconds or on any keypress.
