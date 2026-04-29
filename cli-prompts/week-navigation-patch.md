# Historical Week Navigation Enhancement

## What it does
The ‹ Apr 7, 2026 › date nav in the header lets you step through weeks. Currently it changes the hero card and some values but many tiles don't respond. Make EVERY tile react to week changes.

## Current state
- `_selectedWeek` variable tracks the selected historical week
- `getSelectedWeekSum()` returns the week's summary stats
- Hero card responds (TE, pctSpec, pctFac update)
- Some charts DON'T update (they always show latest data)

## Fixes needed:

### 1. When week changes, ALL tiles must update:
- Sector table: show weights/TE from that week's data (if available in cs.hist.sec)
- Factor Detail: show exposure/TE from that week's snap_attrib history
- Country map: re-color based on that week's data
- Holdings table: show weights from that week (if per-holding history exists)
- Quant Ranks: recalculate from that week's holding data

### 2. Visual indicator for historical mode
When viewing a non-current week:
- Add amber banner below header: "Viewing historical data: Week of Mar 27, 2026 (2 weeks ago)"
- Dim the "Risk rising" text in hero card (current-week-only insight)
- Disable upload/edit actions (read-only historical view)

### 3. Week comparison mode
Double-click the date → opens a split view:
- Left: selected week
- Right: current week (or another selected week)
- Delta column/cells highlighted showing what changed

### 4. Week animation
Click-and-hold the ‹ or › arrows → auto-play through weeks at 1 per second
Shows a timeline scrubber below the header
Good for presentations — "watch how TE evolved over 3 years"

## Implementation priority:
1. Make all tiles respond to week changes (HIGH — this is broken)
2. Historical mode visual indicator (MEDIUM)
3. Week comparison (LOW — nice to have)
4. Week animation (LOW — presentation feature)
