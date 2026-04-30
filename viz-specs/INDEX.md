# Viz Specs & Mockups Index

**Updated:** 2026-04-30 (auto-curated; update when adding new specs/mockups).

Per `TABLEAU_AND_MOCKUP_NOTES.md`: every new viz proposal lives here as a
self-contained `.html` mockup + a `.md` spec. Three candidate designs per
mockup. Open the HTML in a browser, evaluate in 3 minutes, reply with go /
rethink / blend.

---

## Lifecycle

1. **proposed** — mockup + spec written, awaiting PM evaluation
2. **approved** — PM said "go" — coordinator implements in `dashboard_v7.html`
3. **implemented** — landed in production; mockup kept as historical record
4. **archived** — superseded or rejected; mockup preserved for the design archive

---

## Catalog

| Tile | Mockup (visual) | Spec (technical) | Status | Notes |
|---|---|---|---|---|
| `cardWeekOverWeek` | [cardWeekOverWeek-mockup.html](cardWeekOverWeek-mockup.html) | (inline) | **implemented 2026-04-30** | Option A (KPI strip + 3-col move list + factor rotation) shipped as the diff tile at top of Exposures. Strategic-recommendation S1. |
| `cardCalendarHeatmap` | (none) | [cardCalendarHeatmap-spec.md](cardCalendarHeatmap-spec.md) | **archived** | cardCalHeat removed in commit `fd31b26` — calendar pattern preserved here for future cyclic-time-series tile reuse. |
| `cardCountry` (chart view) | (none) | [cardCountry-chart-spec.md](cardCountry-chart-spec.md) | **implemented** | Country × Factor TE heatmap as Chart-view of cardCountry. Specs shipped earlier. |
| `cardSectors` | (none) | [cardSectors-spec.md](cardSectors-spec.md) | **implemented** | Sector active-weights table + chart-view spec. |

---

## Conventions

- File naming: `{tileId}-mockup.html` (visual) + `{tileId}-spec.md` (technical)
- Mockups self-contained: Plotly via CDN, CSS tokens copy-pasted from `dashboard_v7.html` lines 14-30
- Three candidate designs per new mockup, side-by-side
- `meta` banner at top of each mockup: "PREVIEW ONLY · synthetic numbers · NOT live"
- Synthetic numbers must look real (NESN-CH, SAP-DE, etc. — not AAA/BBB)
- "Why this design wins / trade-off" notes box per candidate

---

## Adding a new mockup (workflow)

1. User describes new tile concept → I (or a `data-viz` subagent) write the mockup
2. Mockup lands at `viz-specs/{tileId}-mockup.html`
3. Spec at `viz-specs/{tileId}-spec.md` (data fields, Plotly trace config, edge cases)
4. INDEX entry added with **status: proposed**
5. User opens HTML in browser, evaluates ~3 min
6. User replies: "go with A" / "blend A+B" / "rethink"
7. Coordinator implements in `dashboard_v7.html` → INDEX status flips to **implemented**
8. Mockup file is **never deleted** — design archive

Helpers to add later (per `TABLEAU_AND_MOCKUP_NOTES.md`):
- `mockup-template.html` — skeleton with all CSS tokens + Plotly + 3-candidate grid
- `tokens-sync.sh` — diff `:root` block in mockups vs `dashboard_v7.html`, alert on drift

---

## Pending mockups (from NEW_TILE_CANDIDATES.md, ranked)

These are queued for mockup design when the user decides to build them:

| Rank | Tile | Effort | Why |
|---|---|---|---|
| #2 | `cardRegimeDetector` | Higher (~250 lines) | "Are we in a new market regime?" — needs multi-year history. |
| #3 | `cardWhatIf` | High (~300 lines) | "What if I trim AAPL by 100bps?" counterfactual. |
| #4-10 | (see NEW_TILE_CANDIDATES.md) | Various | Brainstormed pool. |

Mockups for these will be drafted when user signals they want one of them
to move from "candidate" to "shippable."
