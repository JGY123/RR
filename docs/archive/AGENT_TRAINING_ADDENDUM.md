# Agent Training Addendum — 2026-04-17

> Draft additions to `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`. Merge these into the specialist agent file before the next work session.
>
> **Why this exists:** when the Chief-of-Staff conversation dies or its context decays, the continuity should survive outside the conversation. The specialist agent carries durable domain knowledge; this addendum keeps it current.

---

## New code patterns that became canonical 2026-04-16 → 04-17

### 1. Theme-aware color resolution
```js
function THEME(){
  let c=getComputedStyle(document.body),g=k=>(c.getPropertyValue(k)||'').trim();
  let light=document.body.classList.contains('light-theme');
  return {grid:g('--grid')||'#334155', tick:g('--txt')||'#94a3b8',
    tickH:g('--txth')||'#e2e8f0', zero:light?'#94a3b8':'#475569',
    land:light?'#e2e8f0':'#1e293b', ocean:light?'#f1f5f9':'#080e1e',
    heatMid:light?'#f1f5f9':'#12151e', card:g('--card')||'#0f172a',
    bg:g('--bg')||'#080e1e'};
}
```
**Rule:** any new chart MUST read colors from `THEME()` not hardcoded hex. `plotBg` is regenerated via `buildPlotBg()` on theme flip.

### 2. Dynamic `plotBg`
`plotBg` is `let` not `const`, reassigned in `applyPrefs()`. All `{...plotBg, ...}` spreads pick up the current theme automatically.

### 3. `isFinite` guard on numeric fields
```js
.filter(h=>!isCash(h)&&isFinite(h.p))
```
Non-negotiable for any filter over `cs.hold` or similar. Bad data in the JSON causes `NaN` which breaks Plotly. Lesson from Patch 003.

### 4. Plotly category-axis trap
Numeric-looking string tickers (`"688910"`, Chinese A-shares) trigger Plotly's auto-type as linear. Force `type:'category'` on the relevant axis. Lesson from Patches 004 and 008.

### 5. localStorage schema versioning
All new keys MUST be versioned: `rr_holdsnap_v1`, `rr_flags_{stratId}`, etc. Never use unversioned keys — schema changes need a migration path.

### 6. Modal Escape close registration
Every modal element id MUST be added to `ALL_MODALS` array (around line 3982) or Escape won't close it. Easy to forget; test after adding.

### 7. Specialist agent consultation
When in doubt about field meaning, consult the specialist agent file before asking the PM. It has the complete FactSet field dictionary and Redwood's PM preferences.

---

## Today's patch ledger (2026-04-16 → 04-17)

| # | Commit | Tag | Feature |
|---|---|---|---|
| 001 | `e5eaf6c` | `working.20260416.0940` | Settings panel + Alert Thresholds |
| 002 | `4ed2aa4` | `working.20260416.1430` | Country drill snap_attrib attribution |
| 003 | `8ca5912` | `working.20260416.1554` | tabBar + init() + isFinite guard fixes |
| 004 | `13273c6` | `working.20260416.1724` | rHoldConc category axis fix |
| 005 | `fc89aa9` | `working.20260416.1746` | Risk Decomposition Tree |
| 006 | `3b2a889` | `working.20260416.1755` | Keyboard shortcuts + help modal |
| 007 | `cf70c40` | `working.20260416.1805` | Glossary modal (13 terms) |
| 008 | `efd1462` | `working.20260416.1837` | Top 10 Holdings chart polish |
| 009 | `35b18ad` | `working.20260416.1844` | Factor Risk Map + Top TE chip strip |
| 010 | `cd2ea0f` | `working.20260416.1901` | Theme toggle foundation (THEME() helper) |
| 011 | `a5d6ab9` | `working.20260416.1910` | Theme long-tail sweep |
| 012 | `3f3eb05` | `working.20260416.1930` | Data freshness indicator |
| 013 | `8b77807` | `working.20260416.1945` | What Changed weight snapshot banner |
| 014 | `0050abb` | `working.20260416.2007` | My Watchlist card |
| — | `938f1bb`, `985fb27` | — | Parallel audit commits (Claude 4.6) — 11 quality fixes |
| — | `de6f946` | `working.20260416.2132` | Scatter/Treemap/MCR chart corrections |
| — | `6d70352` | — | Enhanced choropleth with 9+ color modes |
| — | `015eced` | — | Factor color fix (h.factor_contr not h.fac) |
| 015 | `38be615` | `working.20260416.2116` | This Week card — Exec Summary + Weekly Insights |
| — | `aa767fc` | — | Currency memo |
| — | `e98d628` | `working.20260416.2324` | Regional Driver archetype bucket |
| — | `b003125` | `working.20260416.2342` | Size/Liquidity/Leverage archetype buckets |
| — | `0c606cd` | `working.20260417.0011` | Inline map region zoom + cross-sync |

## Archetype taxonomy (10 buckets total, as of 2026-04-17)
Defined in `getHoldArchetype(h)` around L3237:
1. **Growth Engine** — top factor matches `growth` or `momentum` → emerald
2. **Value Play** — `value` or `dividend` → amber-yellow
3. **Volatility Driver** — `volatil` or `sensitivity` → red-pink
4. **Quality Compounder** — `profit` or `quality` → violet
5. **Market Beta** — `market` → slate
6. **Regional Driver** — `country`, `region`, `industry`, `currency`, `local` → cyan
7. **Size Tilt** — `size` → amber-orange
8. **Liquidity Play** — `liquid` → teal
9. **Leverage Play** — `leverage` → pink
10. **Diversifier** — no single dominant factor → slate

On EM test data: 598/1218 holdings get archetypes. 620 lack `factor_contr` data entirely (secondary factor dates).

## Country map color modes (9+ modes, as of 2026-04-17)
Defined via `getMapColorGroups(s)` around L4951:
- **Weight group:** Active / Port / Bench
- **Risk group:** TE Contribution, Stock-Specific Risk, Factor Risk
- **Style Factors group (dynamic):** all `s.factors[].n` — Volatility, Value, Size, etc.

Each factor has an Exposure/Contribution secondary toggle (`#mapSecondary`). Both inline and full-screen maps support all modes + region zoom (World / Europe / Asia / Americas).

## Region zoom state
`_mapRegion` global shared between inline and fullscreen. `setMapRegion(region)` updates both views + button state. `MAP_REGIONS` const at L4950 with `{lon, lat, scale}` per region.

## Settings threshold keys (as of 2026-04-17)
Extended `_thresholdsDefault`:
- `teRed` / `teAmber` — TE severity
- `singleNameTE` — single-name TE contribution
- `cashMax` — cash alert
- `q5WeightMax` — Q5 holdings max weight
- `factorSigma` — factor exposure sigma threshold
- `asDeltaMin` — Active Share WoW delta
- `freshAmberDays` / `freshRedDays` — data staleness thresholds (Patch 012)

All persist to `localStorage['rr_thresholds']`, live-update via `setThreshold(key, val)`.

---

## Non-code knowledge — PM working style signals

(Observed 2026-04-16 → 04-17, worth encoding in the specialist agent.)

1. **Country+currency together.** When analyzing FX exposure, the PM looks at country + currency as a single visual block (e.g., "is Korea's weight neutralized by KRW being flat?"). See `CURRENCY_MEMO.md` for the memo arguing for a dedicated view.

2. **PM skips Chart/Table toggles.** Default view on Map panels is Map; Chart and Table are tolerated but not requested. When building new tiles with toggle views, default to the most visual one.

3. **Morning-review flow.** Monday morning, the PM lands on Exposures → scans (in order) Risk Alerts banner → What Changed banner → My Watchlist → This Week card → Sector table → Factor Risk Map. Build any new "heads-up" content to fit above the sector table (that's where the eye is).

4. **Tolerance for missing data.** Rather than showing a `—` that looks like -0.00, suppress entire rows or show a clear "not available" state. See the Holdings delta guard in Patch 015 (suppress implausible WoW deltas > 100).

5. **Against feature bloat for 20 users.** The PM explicitly refused color-blind safe mode for a 20-user internal tool. Use the same filter: "does this help the actual daily workflow of 20 PMs?" Before proposing a feature, check against that bar.

6. **Deep in the data, not the design.** The PM is first a data consumer, second a design reviewer. When showing new features, lead with "what changed in the numbers you'll see" not "what the UI looks like."

---

## Agent roster to consider for next session

### `rr-tile-architect` (new)
Specializes in filling `tile-specs/*.md` from `TILE_SPEC_TEMPLATE.md`. Knows the template structure intimately. Can be assigned to a specific tile (one CLI per tile) to work in parallel.

### `rr-data-validator` (new)
Specializes in section 1 (Data Source) of the spec template. Knows how to trace a displayed number back to a FactSet CSV field. Has a workflow for verifying against raw CSV.

### `rr-design-lead` (new)
Specializes in section 6 (Design). Consistent typography, spacing, emphasis across tiles. Reads every rendered tile and catches visual inconsistencies.

### `rr-recovery-specialist` (new)
Owns git hygiene — checkpoint tagging, push cadence, never-skip-hook discipline. Knows how to walk back to a known-good state when things go sideways.

### `risk-reports-specialist` (existing)
Master agent. Every other agent consults it for field dictionary / PM preferences / known edge cases. Must be kept current with every patch.

---

## How to apply this addendum

1. Open `~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`
2. Append the sections above under appropriate headings (create new headings as needed)
3. Verify the specialist agent loads cleanly when attached to a new conversation
4. When the next major change lands (another ~10 patches from now), produce the next addendum

This file itself is **durable** — keep it in the RR repo so the history of knowledge is versioned alongside the code.
