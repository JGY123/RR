# Tile Chrome Capability Matrix

**Drafted:** 2026-05-01 (R2-Q25)
**Purpose:** for every tile, list buttons it currently has vs buttons it could have. User checks ☐ → ☑ for any chrome they want added.

**Legend:**
- **Existing:** ✅ has it · ❌ doesn't · 🔶 partial / inconsistent
- **Possible affordances:**
  - **About** — ⓘ button → opens registry entry
  - **Notes** — right-click anywhere on title → opens free-text note popup (saved to localStorage)
  - **Reset Zoom** — ⤾ button → Plotly autorange back to full data
  - **Reset View** — ↺ button → resets ALL state (filters, toggles, view, zoom)
  - **Hide** — × button → collapses tile (state remembered per session)
  - **Full Screen** — ⛶ button → opens tile in modal at max width
  - **CSV** — exports tile data to CSV
  - **PNG** — html2canvas screenshot of the tile
  - **Drill** — clickable rows / bars open detail modal
  - **View toggle** — Table / Chart / Map / etc. variants
  - **Period** — global Impact-period selector applies to this tile

---

## Tier 1 — Hero tiles (PM glances every Monday)

| Tile | About | Notes | Reset Zoom | Reset View | Hide | Full Screen | CSV | PNG | Drill | View toggle |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `cardThisWeek` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ | n/a |
| `cardWeekOverWeek` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ (rows) | n/a |
| `cardSectors` | ✅ | ✅ | ❌ | ☐ | ☐ | ✅ | ✅ | ✅ | ✅ | ✅ Table/Chart |
| `cardCountry` | ✅ | ✅ | ❌ | ☐ | ☐ | ✅ | ✅ | ✅ | ✅ | ✅ Map/Chart/Table |
| `cardFacRisk` | ✅ | ✅ | ❌ | ☐ | ☐ | ✅ | ❌ | ✅ | ✅ | n/a |
| `cardHoldings` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ✅ | ✅ | ✅ | ✅ Table/Cards |
| `cardHoldRisk` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ | n/a |

**Summary**: most Tier 1 tiles have About + Notes + Drill + CSV/PNG. **Missing across the board: Reset View + Hide button.** Full-screen is on Sectors/Country/FacRisk only.

---

## Tier 2 — Risk decomposition

| Tile | About | Notes | Reset Zoom | Reset View | Hide | Full Screen | CSV | PNG | Drill | View toggle |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `cardRiskHistTrends` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ (mini-cards) | n/a |
| `cardRiskDecomp` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ☐ | ☐ | ❌ | n/a |
| `cardTEStacked` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ✅ | ☐ | ✅ (chart) | n/a |
| `cardBetaHist` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ (whole-card) | n/a |
| `cardFacContribBars` | ✅ | ✅ | ✅ | 🔶 | ☐ | ❌ | ❌ | ❌ | ✅ | ✅ TE/Exp/Both |
| `cardRiskFacTbl` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ✅ | ❌ | ✅ | n/a |
| `cardRiskByDim` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ✅ | ❌ | ✅ | ✅ Country/Currency/Industry |
| `cardFacHist` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ❌ | ❌ | ❌ | ✅ Active/Return/Cum |
| `cardCorr` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ✅ | ❌ | ❌ | ✅ Period+Freq |

**Summary**: Risk-tab Reset Zoom is in good shape. **Missing: Reset View + Hide + Full Screen on most tiles. cardFacContribBars has its own ⤾ Reset that resets controls — should be unified with the global ↺ pattern.**

---

## Tier 3 — Exposures secondary

| Tile | About | Notes | Reset Zoom | Reset View | Hide | Full Screen | CSV | PNG | Drill | View toggle |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `cardGroups` | ✅ | ✅ | ❌ | ☐ | ☐ | ✅ | ✅ | ✅ | ✅ | ✅ Treemap/Table |
| `cardRanks` | ✅ | ✅ | n/a | ☐ | ☐ | ❌ | ✅ | ❌ | ✅ | ✅ Wtd/Avg |
| `cardFacButt` | ✅ | ✅ | ❌ | ☐ | ☐ | ❌ | ❌ | ✅ | ✅ | n/a |
| `cardFacDetail` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ❌ | ❌ | ✅ | ✅ Primary/All |
| `cardRegions` | ✅ | ✅ | ❌ | ☐ | ☐ | ✅ | ✅ | ❌ | ✅ | ✅ Table/Chart |
| `cardAttrib` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ❌ | ❌ | ✅ | ❌ |
| `cardAttribWaterfall` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ❌ | ❌ | ❌ | n/a |
| `cardCashHist` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ❌ | ❌ | ❌ | n/a |
| `cardChars` | ✅ | ✅ | n/a | ☐ | ☐ | ❌ | ✅ | ❌ | ✅ | n/a |
| `cardTreemap` | ✅ | ✅ | ✅ | ☐ | ☐ | ❌ | ❌ | ❌ | ✅ | ✅ Group/Size/Color |
| `cardFRB` | ✅ | ✅ | n/a | ☐ | ☐ | ❌ | ❌ | ❌ | ✅ | n/a |
| `cardUnowned` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ✅ | ❌ | ✅ | n/a |
| `cardWatchlist` | ✅ | ✅ | n/a | ☐ | ☐ | ☐ | ❌ | ❌ | ✅ | n/a |

---

## Tier 4 — Holdings tab secondary

| Tile | About | Notes | Reset Zoom | Reset View | Hide | Full Screen | CSV | PNG | Drill | View toggle |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `cardRankDist` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ (bars) | n/a |
| `cardTop10` | ✅ | ✅ | ✅ | ☐ | ☐ | ☐ | ☐ | ☐ | ✅ (bars) | n/a |

---

## Aggregate gaps (where the same chrome is missing across multiple tiles)

| Affordance | # tiles missing | Tiles |
|---|:-:|---|
| **Reset View** (↺) | 30 of 30 | (framework just shipped — needs sweep across all tiles) |
| **Hide** (×) | 30 of 30 | (not yet implemented — would need new collapse-state mechanism) |
| **Full Screen** (⛶) | ~24 of 30 | only cardSectors / cardCountry / cardGroups / cardRegions / cardFacRisk have it |
| **PNG** (📷) | ~22 of 30 | most tiles missing — could be added uniformly via screenshotCard() |
| **CSV** | ~14 of 30 | drill-modal-driven tiles often skip; chart-only tiles especially |

---

## Recommended next sweeps (defer past presentation)

1. **Add Reset View ↺ button to every chart tile** that has filters or view toggles. Register custom handler in `window._tileDefaults`. Single batch ~2hrs.
2. **Add Full Screen ⛶ button to every chart tile.** Use the `openSecFullscreen` / `openCountryFullscreen` pattern — generalize into `openTileFullscreen(tileId)` that copies the tile's HTML into a full-bleed modal.
3. **Add Hide × button to every tile** + collapse-state localStorage persistence. New mechanism — needs backlog spec first.
4. **Add PNG export to every tile** via existing `screenshotCard(selector)` — uniform pattern.

---

## How to use this matrix

Print this doc. For any tile where you want a missing affordance, change the `☐` to `☑`. Send it back to me — I'll do the sweep in one batch.

Or paste the tile names with what you want, e.g.:
> "cardSectors: add Reset View, Hide. cardTEStacked: add Hide, Full Screen, PNG."

---

**Drafted:** 2026-05-01 by Claude (1M context)
**Coverage:** 30 tiles across Exposures + Risk + Holdings tabs
**Last update:** 2026-05-01 (post Round 2 reverts + Reset View framework)
