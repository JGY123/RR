# User Annotations + Notes System

## What it does
Let the PM add personal notes to any tile, holding, or sector. Notes persist in localStorage and show as small sticky notes on the tiles.

## 1. Note on any card
Right-click (or long-press) any card → "Add note" option → small textarea popup
Note shows as a subtle sticky badge on the card corner
Notes stored in localStorage keyed by strategy+tile

## 2. Holding flags
In the holdings table, each row gets a small flag icon
Click to cycle: none → ⭐ watch → 🔴 reduce → 🟢 add → none
Flags persist per strategy in localStorage
Filter chips: "Flagged only" shows only flagged holdings

## 3. Sector/Country annotations
In sector drill, add a "Notes" section at the bottom
Free-text textarea for PM commentary ("Industrials OW is intentional — capex cycle thesis, review Q3")
Shows on the sector table as a 📝 icon in the sector name cell

## Implementation:
```javascript
const NOTES_KEY = 'rr_notes';
function getNotes(){ try{return JSON.parse(localStorage.getItem(NOTES_KEY)||'{}');}catch(e){return{};} }
function setNote(key, text){ let n=getNotes(); if(text)n[key]=text; else delete n[key]; localStorage.setItem(NOTES_KEY,JSON.stringify(n)); }
function getNote(key){ return getNotes()[key]||''; }
// Key format: "IDM:sector:Industrials" or "IDM:hold:NBIS" or "IDM:card:cardSectors"
```

## 4. Export notes
"Export Notes" button in settings → downloads a JSON file with all annotations
"Import Notes" accepts the JSON file to restore
