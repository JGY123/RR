# RR Dashboard — Tile Spec (Living Doc)

**Purpose:** Source of truth for every tile on the dashboard. One entry per tile. Reviewed systematically in workflow-priority order. Each entry captures current state, data, purpose, options, creative ideas, and final decision. Updated as we go.

**Methodology:** See `~/.claude/plans/iridescent-weaving-shannon.md`

---

## Status Legend
- 🔴 **Pending** — not yet reviewed
- 🟡 **In Review** — proposal drafted, awaiting decision
- 🟢 **Decided** — decision made, awaiting build
- 🔵 **Building** — implementation in progress
- ✅ **Built** — code changes committed
- ⭐ **Verified** — tested in browser, confirmed working

---

## Tile Inventory (workflow priority order)

### Tier 1 — Critical (always looked at first)
| # | Tile | Tab | Card ID | Status |
|---|------|-----|---------|--------|
| 1 | Summary Card — Tracking Error | Exposures | (inline sum-card) | ✅ Built (awaiting verification) |
| 2 | Summary Card — Idiosyncratic Risk | Exposures | (inline sum-card) | ✅ Built |
| 3 | Summary Card — Factor Risk | Exposures | (inline sum-card) | ✅ Built |
| 4 | Portfolio Characteristics | Exposures | cardChars | ✅ Built |
| 5 | Holdings Table | Holdings | cardHoldings | ✅ Built |
| 6 | Sector Active Weights | Exposures | cardSectors | ✅ Built |

### Tier 2 — Core risk analysis
| # | Tile | Tab | Card ID | Status |
|---|------|-----|---------|--------|
| 7 | TE Stacked Area (hero) | Risk | (inline) | ✅ Built |
| 8 | Factor Detail | Exposures | cardFacDetail | ✅ Built |
| 9 | Factor Contributions | Risk | (inline) | ✅ Built |
| 10 | MCR Top 10 | Exposures | cardMCR | ✅ Built |
| 11 | Factor Risk Budget | Exposures | cardFRB | ✅ Built |
| 12 | Factor Exposures Table | Risk | (inline) | ✅ Built |

### Tier 3 — Exposure analysis
| # | Tile | Tab | Card ID | Status |
|---|------|-----|---------|--------|
| 13 | Country Exposure | Exposures | cardCountry | ✅ Built |
| 14 | Industry | Exposures | cardIndustry | 🔵 Building |
| 15 | Redwood Groups | Exposures | cardGroups | ✅ Built |
| 16 | Quant Ranks | Exposures | cardRanks | ✅ Built |
| 17 | Region Active Weights | Exposures | cardRegions | ✅ Built |

### Tier 4 — Attribution
| # | Tile | Tab | Card ID | Status |
|---|------|-----|---------|--------|
| 18 | Factor Attribution — Return Impact Waterfall | Exposures | (inline) | ✅ Built |
| 19 | Factor Attribution — 18 Style Snapshot | Exposures | cardAttrib | ✅ Built |
| 20 | Beta History Chart | Risk | (inline) | ✅ Built |

### Tier 5 — Secondary visualizations
| # | Tile | Tab | Card ID | Status |
|---|------|-----|---------|--------|
| 21 | Factor Butterfly | Exposures | cardFacButt | ✅ Built |
| 22 | Risk/Return Scatter | Exposures | cardScatter | ✅ Built |
| 23 | Active Weight Treemap | Exposures | cardTreemap | ✅ Built |
| 24 | Unowned Risk Contributors | Exposures | cardUnowned | ✅ Built |
| 25 | Factor Correlation Matrix (Exposures preview) | Exposures | cardCorr | 🔵 Building |
| 26 | Factor Correlation Matrix (Risk full) | Risk | (inline) | ✅ Built |
| 27 | Factor Exposure History | Risk | (inline) | ✅ Built |
| 28 | Rank Distribution | Holdings | (inline) | ✅ Built |
| 29 | Sector Concentration (Top 10) | Holdings | (inline) | ✅ Built |

### Drill modals (reviewed as triggered from parent tiles)
- `oDrMetric` — metric detail (TE, Idio, Beta, etc.)
- `oSt` — stock detail
- `oDr` — sector/region drill
- `oDrCountry` — country drill
- `oDrGroup` — Redwood group drill
- `oDrUnowned` — unowned security detail
- `oDrChar` — characteristic time series
- `oDrRiskBudget` — factor risk budget breakdown
- `oDrFRisk` — factor time series drill
- `openComp` — strategy comparison modal

---

# 🟡 Tile 1: Summary Card — Tracking Error

**Tab:** Exposures (top row)
**Card ID:** (inline `.sum-card`, first of 3)
**Render Location:** `dashboard_v7.html:818-822`
**onClick:** `oDrMetric('te')` → opens metric time series modal
**Status:** 🟡 In Review — awaiting decision

## Current State

**What the tile shows right now:**
```
┌─────────────────────────┐
│ TRACKING ERROR  ⓘ       │
│                         │
│      5.1  ↓             │
│                         │
│ ↑ 157 wk trend          │
└─────────────────────────┘
```

- **Label:** "Tracking Error" (10px uppercase, with hover tooltip)
- **Value:** `5.1` — rounded to 1 decimal, colored: green (<5), warn/purple (5-10), red (≥10). Includes a risk delta arrow (`riskDelta`) showing week-over-week change.
- **Sub-text:** Trend indicator character (`gt()` — probably ↑↓→) + "157 wk trend"
- **Interactions:** Click → `oDrMetric('te')` modal with full time series + breach analysis. Tooltip on label hover.

**Actual render code:**
```html
<div class="sum-card ${teClass}" onclick="oDrMetric('te')" tabindex="0" role="button">
  <div class="label tip" data-tip="Annualized standard deviation of excess returns vs benchmark">Tracking Error</div>
  <div class="value" style="${color based on value}">${f2(ws.te,1)}${riskDelta(ws.te,prevWs&&prevWs.te,1)}</div>
  <div class="sub">${gt(s.hist.sum,'te')} ${s.hist.sum.length} wk trend</div>
</div>
```

**Live data snapshot (IDM, latest week = 2026-01-30):**
- Current TE: **5.06%**
- 1 week ago: 5.04% (→ essentially flat)
- 4 weeks ago: 4.89% (→ slight rise)
- 13 weeks ago: 5.79% (→ came down meaningfully)
- 3-year range: 3.46 – 5.98% (157 weekly points, avg 4.17%)
- Current color classification: **warn/purple** (between 5-10)

**Live data snapshot across strategies:**
- ACWI: 6.27 | EM: 4.53 | GSC: 6.12 | IDM: 5.06 | IOP: 5.99 | ISC: 5.40 | SCG: 7.56

## Data Available

**In JSON for this tile:**
- `s.sum.te` — current TE (point-in-time, end of latest week) ✅
- `s.hist.summary[]` — 157 weekly TE values for the full 3-year history ✅
- `s.sum.total_risk` — absolute portfolio volatility (14.22 for IDM) ✅
- `s.sum.bm_risk` — absolute benchmark volatility (13.27 for IDM) ✅
- `s.sum.pct_specific` — 69.12% of TE is idiosyncratic
- `s.sum.pct_factor` — 30.88% of TE is factor-driven

**Not yet parsed:**
- TE bounds / risk limits (not in FactSet file — would need a PM-configured threshold)
- Predicted vs realized TE split (would need a separate computation)

## Purpose

**One-sentence:** Tell the PM at a glance whether the portfolio is currently running "hot, cold, or normal" on active risk, and whether it's trending up or down from recent weeks.

**Deeper:** TE is the single most important number on the whole dashboard. It's the PM's risk budget — if it breaches 10%, they need to cut positions; if it drops below 3%, they may be leaving alpha on the table. The card needs to surface **three things simultaneously:**
1. The current level (is it in budget?)
2. The short-term direction (is it rising or falling?)
3. The long-term context (is today high or low by historical standards?)

## Workflow

When would the PM look at this card?
1. **First thing every morning** — is anything on fire? TE is the alarm bell.
2. **After rebalancing** — did the trades do what we expected to the risk profile?
3. **Before CIO meetings** — can I walk in knowing my risk is where it should be?
4. **When market volatility jumps** — did our TE spike along with VIX, or did we stay contained?

**Action that follows from this tile:** If TE is rising or near a threshold, click → drill → see which holdings/factors are driving the rise → make a trade decision. The card's job is just "should I investigate further?"

## Current Issues

1. **Only one number visible.** The single "5.1" with a tiny trend char gives no historical context. Is 5.06 high or low for IDM? The card doesn't say.
2. **Trend character `↑↓→` is hard to read.** It's a single unicode arrow with unclear meaning (what lookback? what's the threshold for "up"?).
3. **"157 wk trend" is meta-data, not insight.** It tells you the sample size, not anything about the data itself.
4. **Color bands are arbitrary.** `<5 = green, 5-10 = warn, ≥10 = red` — but IDM's 3-year range is 3.46-5.98, so the card is always "warn" for IDM even when TE is totally fine. Bands should be strategy-relative or PM-configured.
5. **No visual of the history.** The most important context — "where does today sit in the distribution of the last 3 years?" — is invisible until you click the drill modal.
6. **No breach warning.** If TE just crossed a meaningful level (e.g., above the 3-year 90th percentile), the card should shout about it.
7. **`riskDelta` adds a second arrow that's confusing** next to the value (two different arrows telling different things).

## Conventional Options

### Option A — Minimal Polish (low risk, small gain)
Keep the single-number display but:
- Replace the trend character with an explicit "wk Δ" badge showing the actual week-over-week delta (e.g., `+0.02` in green, `-0.15` in red)
- Add a tiny sparkline (30-60px wide) across the bottom of the card showing the full 157-week history, with a dot marking "today"
- Replace static color bands with percentile-based coloring: today's TE vs its own 3-year distribution (top 10% = red, bottom 10% = cool blue, middle = neutral)
- Sub-text becomes: "13w: 5.79 → 5.06" (concrete past-to-present anchor)

**Pros:** Immediate context improvement, zero interaction risk, keeps card compact
**Cons:** Still just one number — won't wow anyone, CIO still needs the drill modal for real insight

### Option B — Three-Metric Compact (more info, more dense)
Split the card into a 3-column micro-layout:
```
  TRACKING ERROR
┌──────┬──────┬──────┐
│ 5.06 │ 4.17 │ 5.98 │
│ Now  │ Avg  │ Max  │
└──────┴──────┴──────┘
[spark:  ∿∿∿∿∿∿∿∿∿∿∿∿ ]
wk Δ: +0.02   30d: -0.73
```

- Top row: Now / 3-year Avg / 3-year Max (three numbers side by side)
- Full-width sparkline across bottom
- Delta row: week-over-week + 30-day change

**Pros:** Much more context without opening the drill, answers "is this normal?" at a glance, visually richer
**Cons:** Denser → harder to scan, sparkline on a 200px-wide card might be cramped, risks feeling cluttered

### Option C — Bands + Threshold Bar (most actionable)
Replace the numeric-only display with a **horizontal gauge bar**:
```
TRACKING ERROR                         5.06%
├──────────────────────────────────────┤
 min           avg           •       max
 3.5           4.2           5.1     6.0
[Below target] [Target] [Elevated] [High]
wk Δ: +0.02
```

- Horizontal bar spanning the card, showing min/avg/max from 3-year history
- A marker (•) showing current position
- Colored zones for "target" (e.g., 4-5%) and "elevated" (>5%)
- Zone labels small underneath

**Pros:** Instantly shows "am I in budget?" — the most important workflow question. Bands are strategy-specific (based on the strategy's own history). Extremely scannable.
**Cons:** Target bands require PM judgment to set (or we auto-compute from history — but then "target" is circular). Takes more vertical space. Doesn't show trajectory.

## 💡 Creative / Out-of-the-Box Ideas

### Idea 1: **The Heartbeat Card** — TE as a living pulse
Instead of (or alongside) a sparkline, render a continuously-animated ECG-style waveform whose **pulse rate visibly speeds up when TE is rising and slows when falling**. The waveform is derived from the actual 157-week TE series, but the animation speed is mapped to the recent 4-week rate of change. Color shifts from calm blue (low/flat TE) through amber (rising) to urgent red (rising fast or near threshold).

- **Why it's different:** It's time-based motion, not static shape. Peripheral vision catches "urgency" without reading numbers.
- **Why it's useful:** The PM walking past the screen can tell the portfolio's "vital signs" without even focusing — a calm pulse = all is well, a racing pulse = investigate. It solves the "I forgot to check the dashboard" problem.
- **Feasibility:** **Medium.** Plotly doesn't animate natively like this, but we can implement with a small SVG + `requestAnimationFrame` or CSS `@keyframes` driven by JS-computed rate.
- **Risk of gimmick:** **Medium.** A PM will love it on day 1 and may find it distracting on day 30. Needs an option to silence the animation. Might be perfect for CIO meeting-room displays, less so for all-day screens.

### Idea 2: **The TE Distribution Ghost** — today's value against its own history
Render a **tiny horizontal histogram** (or a smoothed KDE curve) of the 157-week TE distribution inside the card. A vertical marker shows where "today" sits in that distribution. The area to the left of today's marker is filled in a cool color; the area to the right is unfilled. A label above the marker reads "67th pct" or similar.

Visually:
```
  TRACKING ERROR
      5.06   67th pct
        ▼
  ▁▂▃▅█▇▅▃▂▁▁
  3.5          6.0
```

- **Why it's different:** It shows the current value **as a position within its own past**, not just an absolute number. "Am I normal?" is answered instantly.
- **Why it's useful:** Humans are terrible at evaluating isolated numbers. "Is 5.06 high?" is unanswerable without context. But "you're at the 67th percentile of your own history" — that's immediate, specific, and actionable.
- **Feasibility:** **Easy.** Can be done as inline SVG (20 bars, 100px wide, ~20px tall). No Plotly needed. Completely fits inside the existing card layout.
- **Risk of gimmick:** **Low.** This is standard quant practice just rarely seen on dashboards. Clean, defensible, highly informative.

## Recommendation

**My recommendation: Option B (Three-Metric Compact) + Idea 2 (Distribution Ghost) combined.**

Rationale:
- Option B gives the three most important numbers (Now / Avg / Max) so the PM doesn't need to click through for basic context
- The Distribution Ghost replaces the "157 wk trend" sub-text with something that actually uses those 157 weeks to answer "is today normal?"
- Together they stay within a compact card footprint (~120px tall)
- Both are low-risk to build and verify
- Leaves the Heartbeat Card (Idea 1) as a future hero element for the CIO presentation version — not the daily workflow view

The TE card is the most-seen element on the entire dashboard. It should be **information-dense but instantly readable**, not flashy.

## Decision
*[Awaiting your input]*

## Action Items
*[To be filled in after decision]*

## Verification
*[To be filled in after implementation]*
