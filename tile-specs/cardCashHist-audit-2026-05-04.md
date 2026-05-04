# Tile Spec: cardCashHist — First-Pass Audit

> **Audited:** 2026-05-04 | **Auditor:** Tile Audit Specialist (subagent)
> **Scope:** First formal three-track audit on `cardCashHist`. No prior audit on file.
> **Status:** **YELLOW** — data layer is clean (T1 GREEN with one defensive-UI gap), but the tile is structurally **outside the tile contract** (T2 has no `tileChromeStrip`, no CSV export, no `data-col` table) and the chart leaks **8 inline hex literals** plus inline-styled chrome where the design system expects tokens (T3).
> **Color status by track:** Data **GREEN-with-amber** · Functionality **YELLOW** · Design **YELLOW**

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Cash Weight Over Time |
| **Card DOM id** | `#cardCashHist` (Exposures tab, bottom of grid per intentional 2026-04-30 placement) |
| **Card markup line** | `dashboard_v7.html:3376–3386` (inline IIFE template inside `rExposures`) |
| **Render function** | `rCashHist(s)` at `dashboard_v7.html:6137–6190` |
| **Render dispatch** | `rExposures` chart array, line 3398 (wrapped in B115 try/catch) |
| **Inner plot id** | `#cashHistDiv` (`height:160px` inline — does NOT use `.chart-h-sm` token class) |
| **CSV exporter** | **None** — no chrome buttons, no inline export, no `tileChromeStrip` config (see F1) |
| **About entry** | `_ABOUT_REG.cardCashHist` at `dashboard_v7.html:1299–1306` (registered, well-formed) |
| **Drill route** | None — intentional per author note line 3364–3368 ("self-contained — no drill modal; the band + alert chip in the header tell you everything") |
| **Right-click → note** | Wired on the title (`oncontextmenu="showNotePopup(event,'cardCashHist')"` line 3379) |
| **Tab** | Exposures (placed last — bottom of grid by user direction "the cash should be pushed all the way to the bottom of the page") |
| **Width** | Full-width within Exposures grid |
| **Full-screen path** | None registered — generic `openTileFullscreen('cardCashHist')` would work via DOM clone but tile has no chrome button to invoke it |
| **Spec status** | `audit-only` — coordinator serializes any code fixes |
| **Data source** | `cs.hist.sum[].cash` (per-period from `[Cash]` row in `Sector Weights` section, parser line 1407–1426 in `factset_parser.py`) + `cs.sum.cash` for header current/alert chip |

---

## Trivial fixes (1–5 lines each, agent can apply once approved)

- **F1.** Tile has **no `tileChromeStrip`**. Even with no CSV export and no view-toggle, peer time-series tiles still emit a chrome row: at minimum `about + resetView + hide + fullscreen`. Add a minimal strip — keeps tile management consistent (the user's `× hide` muscle memory works on every other tile but not this one). 5–8 lines, no semantic change.
- **F2.** Negative-cash defensive-UI: when `cash < 0`, the tile already renders the value (red below-zero strip drawn at line 6176) but never **flags whether negative is real or a parser/CSV error**. Per CLAUDE.md hard rule #4 (every numeric cell has provenance), add a footnote/tooltip in the alert chip when `cur < 0`: "Negative cash is rare — confirm against FactSet [Cash] row". The chip currently says "cash is negative" (line 3375) — fine, but a `data-tip` with the source pointer would close the loop with the user's audit posture.
- **F3.** `cs.sum.cash` access on line 3370 happens unconditionally inside the IIFE before any defensive guard. If `s.sum` is missing (extreme edge but possible during partial-load races), this throws and the **entire `rExposures` HTML batch fails**. Safer: `const cur = s.sum?.cash ?? null;`.
- **F4.** Empty-state in `rCashHist` (line 6144–6147) uses inline `<div style="...">` instead of the canonical `.empty-state` class (defined line 115, used by 5+ peer tiles per `cardHoldRisk-audit-2026-05-04.md` precedent). Replace with `<div class="empty-state">No cash history shipped...<div class="empty-state-hint">FactSet weekly export does not always include % Cash.</div></div>`. Aligns with Phase K design system (ARCHITECTURE.md §4.3).
- **D1.** Plotly hex literals on lines 6157, 6172, 6174, 6176, 6178, 6179, 6182, 6185, 6186 — 9 inline RGB/hex literals. Per `LESSONS_LEARNED.md` lesson 9-13 (Plotly hex anti-pattern) and the precedent set in `rRiskFacBarsMode` lines 8170–8175, resolve `var(--warn)` (line `#f59e0b` on line 6157), `var(--pos)` (`#10b981` rgba band line 6172), `var(--neg)` (`#ef4444` rgba bands lines 6174, 6176) via `getComputedStyle(document.documentElement)` up-front. Restores light-theme parity (currently all amber/red strips render the same shade in dark + light, which is the symptom).
- **D2.** Footer caveat absent. The card has no hairline footer pointing to source — peer time-series tiles all carry one. Add an inline hairline div under the chart: `<div style="font-size:10px;color:var(--textDim);margin-top:4px;border-top:var(--hairline);padding-top:4px">Cash extracted from [Cash] sector row per period — null on weeks where FactSet didn't ship the row.</div>`. This pattern is exactly what the user's audit prompt requests; the data-tip on line 3379 says the same thing, but data-tips are hover-only, hidden from PMs scanning the page.
- **D3.** Inline `style="margin-top:16px"` on the card (line 3376), `style="height:160px"` on `#cashHistDiv` (line 3385), `style="font-size:11px;color:var(--txth);font-weight:600"` on the current-value span (line 3381) — 5+ inline-style invocations where tokens or classes exist. Sweep into `.tile-spacing`, `.chart-h-xs` (new size needed — 160px is below the existing `.chart-h-sm` clamp of 180px), `.tile-current-value` or similar. Aligns with §4.3 "hardcoded colors / spacing / fonts are forbidden" (currently violated).

## Larger fixes (1–2 hours each, queued)

- **F5.** No CSV export wired. Peer time-series tiles (`cardTEStacked`, `cardBetaHist` per its audit F4) are queued for `exportCashHistCsv` of the form `Date, Cash%, In Band?`. Pattern: copy `exportTEStackedCsv` (around line 8087). Trivial in code, requires F1 to land first so there's a chrome button to host the export.
- **F6.** Data-tip on title (line 3379) hardcodes the source path "Source: cs.hist.sum[].cash extracted per period from the [Cash] sector row." This is correct but **not registered in `SOURCES.md`** — search confirms no `cardCashHist` or `cs.hist.sum[].cash` entry in `SOURCES.md` (only `cardThisWeek` references current cash). Add `cardCashHist` block to `SOURCES.md` with: chart line / target band / current-value chip / alert chip rows. Closes the §4 of CLAUDE.md hard rule #4 ("`SOURCES.md` is the index. UPDATE when render code changes").
- **D4.** `connectgaps:false` (line 6160) is correct for "missing weeks render as gaps" (matches the about-entry caveat) but the chart shows no on-chart indicator for "this week is null." Two acceptable postures per ARCHITECTURE.md §5.3: (a) accept gaps silently with the footer caveat (current), or (b) overlay tiny `×` markers at null-x positions. Option (a) is fine — flagging only because a future PM may ask "is this missing or zero?" The footer (D2) covers it.
- **F7.** No `_TILE_FILTERS` integration — chrome strip currently absent (F1) so this is a non-issue, but if F1 lands, the chrome should NOT include filter chips (no per-week filter applies to cash history; the tile's purpose is the full timeline). Document in the chrome config comment.

## PM-decision items

- **X1.** Tile is intentionally **without a drill modal** per author note line 3364–3368 — user direction was "this is one of the only tiles that should just simply show what you have." However, peer time-series tiles all click into a drill (`oDrMetric('te')`, `oDrMetric('beta')`). Confirm with PM: does cash deserve a drill modal of its own (showing weekly cash + flow direction + a "biggest week" callout) or is the band-as-spec intentional and durable?
- **X2.** 0–5% target band is hardcoded (lines 6152). Should this be a configurable `_thresholds.cashMax` (which already exists — see `dashboard_v7.html:2495` which alerts at `sum.cash > _thresholds.cashMax`)? Currently the alert in cardThisWeek uses the threshold but cardCashHist uses a literal `5`. **Internal inconsistency** between two places that judge "is cash too high." PM call: which one is canonical? Recommend wire cardCashHist to read `_thresholds.cashMax` so a settings change updates both. (Not blocking — both default to 5% — but a real bug if the threshold ever moves.)

---

## 1. Data Accuracy — Track 1

### 1.1 Provenance — every plotted point traces to source

| Plotted | Source path | Fabricated? | Markers? |
|---|---|---|---|
| Cash line, y-values | `s.hist.sum[].cash` | No — direct read, parser-extracted from `[Cash]` row's `W` column per period | n/a |
| Cash line, x-values | `s.hist.sum[].d` via `isoDate(...)` | No | n/a |
| Header current value | `s.sum.cash` | No — parser populates from latest-week `[Cash]` row, line 1417 | n/a |
| Alert chip (in-band/out-of-band) | Computed: `cur >= 0 && cur <= 5` (line 3371) | No — math identity | Tooltip text drives green/red |
| Selected-week marker | `_selectedWeek` (added by coordinator commit `f2405c3`) | No — global selector | Vertical dotted line + "selected wk" annotation |
| Target band 0–5% rectangles | Hardcoded literals in `rCashHist` line 6152 | **YES — UI threshold, not data** | None — but see X2 (should source from `_thresholds.cashMax`) |

**T1 Verdict:** **GREEN** for plotted data and current-value chip. The two values that drive the entire visualization (`cash` per period + `cash` latest) trace directly to the parser's `[Cash]` row extraction with **no synthesis path** — verified by reading `factset_parser.py:1403–1426`. The 0/5 target boundaries are UI constants, which is fine (they're labels, not data), but **see X2** for the cross-tile inconsistency with `_thresholds.cashMax`.

### 1.2 Null / gap handling

`hist.map(h=>h.cash)` (line 6142) preserves nulls. The chart's `connectgaps:false` (line 6160) means a missing weekly cash shows as a visible gap (correct — no fabrication). The empty-state branch (line 6144) handles **all-null** case explicitly with a clear PM-readable message. **GREEN.** No `?? 0` substitutions, no synthesis. Note: the empty-state copy is verbose ("No cash history shipped (FactSet weekly export does not always include % Cash).") which is good — surfaces the upstream dependency to the PM.

### 1.3 Negative-cash defensive UI

The chart **does not guard against negative cash showing as a real signal in any misleading way**. Negative values render in a faint red "below-zero alert" strip drawn at line 6176, conditionally created only when `yMinData < 0`. The header alert chip says "cash is negative" when `cur < 0` (line 3375). This is **defensible** per the audit prompt, but **F2** flags an enhancement: append a tooltip pointer "confirm against FactSet [Cash] row" so a negative reading prompts a source check rather than passive acceptance. Negative cash from FactSet is rare-but-real (settlement/funding flows), so suppressing it would be wrong; the current posture is the right one. **YELLOW (defensible) → GREEN with F2 applied.**

### 1.4 Empty-state behavior when `cs.hist.sum[].cash` is null

When zero non-null cash values exist (`valid.length === 0` at line 6144), the chart short-circuits with the explanatory message — **does not call Plotly with empty arrays** (avoids potential downstream errors). This is the right posture. But the header's `current` value still reads `s.sum.cash` and renders `f2(cur,1)+'%'` if `cur != null` even when `hist.sum.cash` is all-null — a possible edge case where current is populated but history is not. Consider: should the header chip suppress when the chart is empty? Today it doesn't; not blocking.

### 1.5 Week-selector interaction (`_selectedWeek`)

**GREEN.** The coordinator added a vertical marker in commit `f2405c3` (lines 6181–6182 + annotation 6187). The marker reads `_selectedWeek` directly (consistent with `cardTEStacked` / `cardBetaHist` per code comment line 6181). Pattern matches the cross-tile sweep. **No action needed** per audit prompt (acknowledged).

The header alert chip is correctly suppressed when viewing a historical week (`isHistWeek` check line 3372 — alert chip becomes empty string; current-value display becomes `—`). **Good week-flow hygiene** — the historical alert state is correctly not implied to be the current state.

### 1.6 localStorage anti-pattern check

**Clean.** No `localStorage.getItem('rr_cash')` or similar pattern. Tile reads `cs.hist.sum`, `cs.sum.cash`, `_selectedWeek`, and DOM-only ephemeral state. Conforms to CLAUDE.md hard rule #3 (localStorage is for preferences only).

### 1.7 `_b115AssertIntegrity` coverage

`cash` is **not** a critical-field assertion in `_b115AssertIntegrity()` (verified by grep — only `te`, `as`, `beta`, `h` are checked). The cash field's parser path is well-tested (extracted in `_assemble`, populated into `_hist_entry`), and the empty-state branch correctly handles all-null. No drift mechanism is currently in place to catch a future parser regression. Consider adding `cash` to the integrity assertion's checked-fields list — non-blocking, but the cost is one line.

---

## 2. Functionality Parity — Track 2

Comparison vs the canonical time-series tile pattern (`cardTEStacked`, `cardBetaHist`).

| Capability | `cardTEStacked` (peer) | `cardBetaHist` (peer) | `cardCashHist` (this) | Gap? |
|---|---|---|---|---|
| `tileChromeStrip` | yes | yes | **NO** | **YES** — F1 |
| About entry | yes | yes | yes | — |
| Right-click note | yes | yes | yes | — |
| CSV export | yes | (queued, F4 in BetaHist audit) | **NO** | **YES** — F5 |
| Click drill | yes (`oDrMetric('te')`) | yes (`oDrMetric('beta')`) | **NO (intentional)** | X1 |
| Per-week marker (`_selectedWeek`) | yes | (queued, F6 in BetaHist audit) | yes (added by coordinator) | — |
| Empty-state | inline | (`return` silently — gap noted in BetaHist F3) | inline (with text) | partial — F4 (use `.empty-state` class) |
| Reset view button | yes (via chrome) | yes | **NO** | YES — F1 |
| Hide tile button | yes (via chrome) | yes | **NO** | YES — F1 |
| Fullscreen | yes (via chrome) | yes | **NO** | YES — F1 |
| Hover tooltip | yes (Plotly hovertemplate) | yes | yes (line 6158) | — |
| Theme-aware Plotly | partial (some hex) | partial (D1 hex sweep queued) | partial (D1 — 9 hex literals) | YES — D1 |
| `data-col` table | n/a (chart-only) | n/a (chart-only) | n/a | — |

**T2 Verdict:** **YELLOW.** The tile renders correctly and shows the right data, but it is **structurally outside the tile contract** — it's the only Tier-1 tile in the Exposures tab without a chrome strip. The intentional "no drill" decision is well-documented and defensible (X1 is a confirmation question, not a bug), but the missing chrome means the user can't hide the tile, can't reset the view, can't export to CSV, and can't go fullscreen. F1 + F5 close the gap.

The `_selectedWeek` marker added by the coordinator brings the tile to per-week parity; the chart correctly **does not respect the marker for chart slicing** (i.e., end-date stays latest), which is the right behavior for a "full history" tile.

---

## 3. Design Consistency — Track 3

Comparison vs ARCHITECTURE.md §4.3 design system + `LESSONS_LEARNED.md` lessons 9–16.

### 3.1 Inline hex / RGB literals

Found in `rCashHist`:
| Line | Literal | Should be |
|---|---|---|
| 6157 | `#f59e0b` (cash line color) | `var(--warn)` resolved |
| 6172 | `rgba(16,185,129,0.06)` (in-band fill) | `var(--pos)` resolved + alpha |
| 6174 | `rgba(239,68,68,0.07)` (above-band fill) | `var(--neg)` resolved + alpha |
| 6176 | `rgba(239,68,68,0.07)` (below-zero fill) | same |
| 6178 | `rgba(148,163,184,0.4)` (lower boundary) | `var(--grid)` resolved |
| 6179 | `rgba(148,163,184,0.4)` (upper boundary) | same |
| 6185 | `rgba(148,163,184,0.85)` (annotation color) | `var(--textDim)` resolved |
| 6186 | `rgba(148,163,184,0.85)` (annotation color) | same |

Found in `rExposures` IIFE template:
| Line | Literal | Should be |
|---|---|---|
| 3374 | `rgba(16,185,129,0.10)` + `rgba(16,185,129,0.3)` (in-band chip bg + border) | `var(--pos)` resolved + alpha |
| 3375 | `rgba(239,68,68,0.10)` + `rgba(239,68,68,0.3)` (out-of-band chip bg + border) | `var(--neg)` resolved + alpha |

**Total: 10 hex/rgba literals across 11 lines.** Per `LESSONS_LEARNED.md` (lesson on Plotly hex literals), Plotly does need literals (it can't read CSS vars), but the right pattern is `getComputedStyle(document.documentElement).getPropertyValue('--warn').trim()` once at the top of the function. **D1 covers this fix.**

### 3.2 Inline `style=` attributes vs design tokens

The card markup (lines 3376–3386) and inner template carry **5+ inline-style strings**:
- Line 3376: `style="margin-top:16px"`
- Line 3377: `style="margin-bottom:6px;flex-wrap:wrap;gap:8px"`
- Line 3378: `style="display:flex;align-items:center;gap:10px;flex-wrap:wrap"`
- Line 3381: `style="font-size:11px;color:var(--txth);font-weight:600"`
- Lines 3374, 3375: chip styling — `style="font-size:10px;color:var(--pos);font-weight:600;padding:2px 8px;background:...;border:...;border-radius:14px"`
- Line 3385: `style="height:160px"` on `#cashHistDiv`

The chip styling is the most egregious — **a reusable `.alert-chip-pos` / `.alert-chip-neg` pair** (likely already exists in the design system; needs a sweep) would replace 4+ lines of inline styling. The card-level margin should use a `.tile-spacing` token. **D3 covers.**

### 3.3 Empty-state class

`rCashHist` line 6144 hand-rolls an inline-styled div instead of using `.empty-state` (defined line 115, has matching `.empty-state-hint` for sub-text on line 128). **F4 covers.**

### 3.4 Tooltip on header

The card-title carries a `data-tip` (line 3379) — **GREEN** per design-system pattern. About-modal entry is registered (line 1299) — **GREEN**. Note-popup wired (line 3379) — **GREEN**. **The header is one of the cleaner aspects of this tile** — only the missing footer caveat (D2) breaks the pattern.

### 3.5 Hairline footer

**Missing.** Peer tiles emit a tile-level footer `<div style="...border-top:var(--hairline);...">` carrying provenance microcopy. `cardCashHist` ends at the chart div with no footer. The data-tip (line 3379) carries the source pointer but only on hover — a PM scanning the page sees nothing. **D2 covers** — should be standard for any tile making a "the band is the spec" claim.

### 3.6 Color semantics

In-band → green chip ✓ · Out-of-band → red chip ✓ · Cash line → amber ✓ (semantic — amber means "watch this") · Above-band fill → red strip ✓ · Below-zero fill → red strip ✓. **GREEN** — color usage is consistent with the project's red/amber/green vocabulary. The `D1` fix is purely about *how* the colors are sourced (tokens vs literals), not about the choices themselves.

**T3 Verdict:** **YELLOW.** The visual design is correct (color semantics, layout, band concept all good); the **execution leaks tokens to literals** in 10+ places and skips the `.empty-state` class + the hairline footer convention. None of these are user-facing bugs in dark theme; in light theme, the bands and the cash line color may render incorrectly because they were never resolved through the theme. **D1 + D2 + D3 + F4** close the gaps; they're each a small edit, none structurally hard.

---

## 4. Verification Checklist (Section 8)

- [x] Data accuracy verified — `s.hist.sum[].cash` traces to parser line 1407–1426; `s.sum.cash` traces to parser line 1417
- [x] No fabrication / synthesis path
- [x] Edge case: all-null cash → empty-state branch (line 6144) — works
- [x] Edge case: negative cash → red strip + alert chip — works (defensible; F2 enhances)
- [x] Edge case: historical week → header chip suppressed — works
- [x] `_selectedWeek` vertical marker — works (added by coordinator commit `f2405c3`)
- [ ] CSV export — **NOT WIRED** (F5)
- [ ] Chrome strip — **NOT WIRED** (F1)
- [ ] Reset/Hide/Fullscreen buttons — **NOT WIRED** (F1)
- [x] Right-click → note popup — works (line 3379)
- [x] About entry registered — `_ABOUT_REG.cardCashHist` line 1299
- [ ] About entry up-to-date — `_ABOUT_REG.cardCashHist.source` says "parser commit f1101cd added per-period extraction; 69/69 weeks populated for GSC sample" — **stale claim** if data has shifted. Re-verify on next ingest.
- [x] No console errors expected (B115 try/catch wraps `rCashHist` at line 3414)
- [ ] Theme-aware (dark + light) — **PARTIAL FAIL** (D1 — 10 hex literals)
- [ ] Footer caveat — **NOT PRESENT** (D2)
- [ ] `.empty-state` class — **NOT USED** (F4)
- [ ] `SOURCES.md` entry — **NOT REGISTERED** (F6)
- [x] localStorage hygiene — clean
- [x] Per-week routing handled — chart shows full history (correct), marker shows selected week (correct), header suppresses when historical (correct)

---

## 5. Triage Queue Summary

**TRIVIAL (agent can apply once approved):** F1, F2, F3, F4, D1, D2, D3 — 7 items
**LARGER (queued):** F5, F6 (SOURCES.md), F7 — 3 items
**PM-DECISION:** X1 (drill modal yes/no), X2 (`_thresholds.cashMax` wiring) — 2 items

**Recommended fix order:**
1. **F3** (`s.sum?.cash ?? null`) — defensive 1-line guard, zero risk
2. **F1** (`tileChromeStrip`) + **F5** (CSV export) — together, since chrome hosts the CSV button
3. **F6** (`SOURCES.md` entry) — closes the per-cell provenance index per CLAUDE.md hard rule #4
4. **D1** (hex literals → tokens) — single-pass sweep of ~12 lines; restores light-theme parity
5. **D2** (footer caveat) + **F4** (`.empty-state` class) — design system alignment
6. **F2** (negative-cash tooltip pointer) + **D3** (inline-style sweep) — polish
7. **X1** + **X2** — escalate to PM after the trivial sweep lands

---

## 6. Notes for Coordinator

- **Do NOT modify `dashboard_v7.html`** — auditor protocol per CLAUDE.md and subagent contract. Coordinator serializes edits.
- The tile is functionally **already in production and correct** — the `_selectedWeek` marker is in place, the parser-side path is rock-solid, the alert chip semantics are well-thought-out. The findings here are about **bringing the tile into the tile contract** (chrome, CSV, footer) and **closing token leaks** (D1 sweep) — not fixing broken behavior.
- F1 + F5 are the only items that would visibly change the user's experience. Everything else is hygiene.
- This audit confirms the user's note: the `_selectedWeek` marker is present and not flagged as a missing feature.
- Re-audit in ~30 days or after F1/F5/D1 land to flip this from YELLOW → GREEN across all three tracks.
