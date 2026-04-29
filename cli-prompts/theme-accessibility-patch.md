# Theme System + Accessibility

## 1. Light/Dark toggle
Currently dark-only. Add a toggle in the header (☀/🌙 icon):

```javascript
function toggleTheme(){
  document.body.classList.toggle('light-theme');
  localStorage.setItem('rr_theme', document.body.classList.contains('light-theme')?'light':'dark');
}
// On load:
if(localStorage.getItem('rr_theme')==='light') document.body.classList.add('light-theme');
```

Light theme CSS already partially exists (line ~398). Enhance it:
```css
body.light-theme {
  --bg:#f8fafc; --card:#ffffff; --surf:#f1f5f9; --grid:#e2e8f0; 
  --txt:#475569; --txth:#0f172a;
  --pos:#059669; --neg:#dc2626; --pri:#4f46e5; --acc:#7c3aed;
}
body.light-theme .card { box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
body.light-theme .hero-risk { background: linear-gradient(135deg, #f1f5f9, #e2e8f0); }
body.light-theme thead th { background: #f8fafc; }
body.light-theme .modebar-container { display:none!important; }
```

## 2. Color-blind safe mode
Toggle that switches the green/red scheme to blue/orange:
```css
body.cb-safe {
  --pos:#2563eb; --neg:#ea580c;
  --r1:#2563eb; --r2:#3b82f6; --r3:#eab308; --r4:#f97316; --r5:#ea580c;
}
```
All charts that use hardcoded #10b981/#ef4444 need to reference var(--pos)/var(--neg) instead.

## 3. Font size control
Three sizes: Compact / Normal / Large
```css
body.font-compact { font-size: 12px; }
body.font-normal { font-size: 14px; }
body.font-large { font-size: 16px; }
body.font-compact table { font-size: 10px; }
body.font-large table { font-size: 13px; }
```

## 4. ARIA accessibility
- All interactive elements need aria-label
- Tab switching needs role="tablist", role="tab", aria-selected
- Modals need role="dialog", aria-modal="true"
- Charts need aria-label describing the data ("Factor Risk Map showing 12 style factors plotted by exposure and volatility")
- Color-coded cells need aria-label with the value (not relying on color alone)

## 5. Settings panel
Gear icon in header opens a settings panel:
- Theme: Dark / Light
- Color-blind mode: On / Off
- Font size: Compact / Normal / Large
- Alert thresholds (from watchlist patch)
- Reset all settings to defaults
All persisted to localStorage under 'rr_prefs'
