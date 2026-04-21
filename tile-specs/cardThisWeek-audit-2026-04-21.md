# Tile Spec: cardThisWeek — This Week (Exec Summary + Weekly Insights)

> **Audit date:** 2026-04-21
> **Auditor:** Tile Audit Specialist (CLI)
> **Dashboard file:** `dashboard_v7.html`
> **Benchmark tile:** `cardSectors` (v1 signed off, 2026-04-19)
> **Methodology:** Three-track audit per `~/orginize/knowledge/skills/tile-audit-framework.md`

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | This Week — Exec Summary + Weekly Insights |
| **Card DOM id** | `#cardThisWeek` |
| **Render function(s)** | `thisWeekCardHtml(s)` at `dashboard_v7.html:L946`; embedded by `rExp()` at L1097 |
| **Tab** | **Exposures** (NOT a separate Overview tab — Exposures is the first/default tab per L416). Hero tile at the top of the tab, above the 3 sum-cards (TE / Idio / Factor) and the week banner. |
| **Grid row** | Row 0 (full-width, above the `sum-cards` grid) |
| **Width** | Full (inherits body width; no explicit grid class) |
| **Visibility** | Rendered when `s && s.sum && (stateBullets.length \|\| changeBullets.length) > 0`; returns empty string otherwise (silent suppression) |
| **Marker in code** | `// ===== "THIS WEEK" — Exec Summary + Weekly Insights (Patch 015) =====` |
| **Owner** | Tile Audit Specialist CLI |
| **Spec status** | `signed-off` (v1) |

**Important scope note:** the user described this as "currently-selected week's headline portfolio metrics (TE, AS, Beta, # Holdings, cash…)" — that description actually matches the **`sum-cards` row** (L1099–L1113: TE / Idiosyncratic / Factor Risk) + the **cash-strip** at L1115. Those are siblings of this card, NOT this card. `cardThisWeek` is a **narrative bullet-list card** that sits above them and synthesizes the week into two columns: "State" and "Changes vs Prior Week". The audit focuses on `#cardThisWeek` as DOM'd; the siblings are noted as related tiles (Section 9).

---

## 1. Data Source & Schema

### 1.1 Primary data source

- **Primary object:** `s.sum` (latest week summary — `te`, `cash`, etc.)
- **Sector roll-up:** `s.sectors[]` (filtered, cash-excluded, sorted by `a`)
- **Holdings:** `s.hold[]` (filtered via `isCash`, sorted by `|h.tr|`)
- **Factors:** `s.factors[]` (filtered by `|f.a| >= _thresholds.factorSigma`)
- **History:** `s.hist.sum[]` — prior-week delta via `hist[hist.length-2]` (L987)
- **Snapshot persistence (holdings WoW):** `localStorage['rr_holdsnap_v1']` — keyed by `s.id`, carries `{prior: {holdings: {ticker: weight}}}` (Patch 013)
- **Thresholds (user-configurable):** `_thresholds.{teRed, teAmber, factorSigma, cashMax}` — defaults `{teRed:8, teAmber:6, factorSigma:0.5, cashMax:5}` (L4818–4819); persisted via `saveThresholds()`.

**Array-length sensitivity:** this tile is a fixed-shape card. No per-strategy length variance; only bullet count varies (0–5 state bullets + 0–5 change bullets).

### 1.2 Field inventory — STATE column (`stateBullets`)

| # | Bullet | Source | Formatter | Gate (threshold) | Code |
|---|---|---|---|---|---|
| S1 | "Tracking error X% is above / amber / within …" | `s.sum.te` + `_thresholds.teRed` / `teAmber` | `f2(te,1)` | `te>=teRed` / `teAmb<=te<teRed` / `0<te<teAmb`. Null → skipped. | L950–L956 |
| S2 | "Largest overweight is **X** at Y%" | `s.sectors[]` filter `x.n && !/cash/i && isFinite(x.a)`, sort by `x.a` desc, top | `fp(topOW.a,1)` | `topOW.a >= 1` | L958–L961 |
| S3 | "Largest underweight is **X** at Y%" | Same list, bottom | `fp(topUW.a,1)` | `topUW.a <= -1` | L962–L963 |
| S4 | "**Name** dominates risk: P% weight, T% of TE" | `s.hold[]` filter `!isCash && isFinite(h.tr)`, sort by `|h.tr|`, top | `f2(topRisk.p,1)` + `f2(\|topRisk.tr\|,1)`. Name truncated to 24 chars. | `\|topRisk.tr\| >= 3` | L966–L970 |
| S5 | "Significant factor tilts (≥σσ): F1 ±xσ, F2 ±yσ, F3 ±zσ" | `s.factors[]` filter `\|f.a\| >= sigma`, sort desc, slice(0,3) | `fp(f.a,2)` | `sigma` = `_thresholds.factorSigma \|\| 0.5`; hard-coded max of 3 | L972–L977 |
| S6 | "Cash position X% exceeds the Y% alert threshold" | `s.sum.cash` + `_thresholds.cashMax` | `f2(cash,1)` | `cash > cashMax` (and not null) | L979–L982 |

### 1.3 Field inventory — CHANGES column (`changeBullets`)

| # | Bullet | Source | Formatter | Gate | Code |
|---|---|---|---|---|---|
| C1 | "**TE:** X% ↑/↓ΔΔ pp vs prior week" | `s.sum.te − prev.te` where `prev = hist.sum[len-2]` | `f2(te,1)`; delta 2-decimal | `\|Δ\| >= 0.05` | L989–L993 |
| C2 | "**Active Share:** X% ↑/↓ΔΔ pp" | `s.sum.as − prev.as` | `f2(as,1)`; delta 1-decimal | `\|Δ\| >= 0.1` | L994–L998 |
| C3 | "**Beta:** X ↑/↓ΔΔΔ" (warn-color if moving further from 1.0) | `s.sum.beta − prev.beta` | `f2(beta,3)`; delta 3-decimal | `\|Δ\| >= 0.005` | L999–L1004 |
| C4 | "**Holdings:** N (+Δ) vs prior" | `s.sum.h − prev.h` | integer diff | `hD !== 0 && \|hD\| <= 100` (explicit data-bug suppression comment) | L1005–L1009 |
| C5 | "**Name:** ↑/↓Δ% weight" (top 2) | `rr_holdsnap_v1[s.id].prior.holdings` vs current `h.p` | `fp(d,2)` | `\|d\| >= 0.5`; slice top 2 by `\|d\|` | L1011–L1034 |

### 1.4 Derived / computed fields

| Field | Computation | Location |
|---|---|---|
| `te` delta | `+(s.sum.te − prev.te).toFixed(2)` | L989 |
| `as` delta | `+(s.sum.as − prev.as).toFixed(1)` | L994 |
| `beta` delta | `+(s.sum.beta − prev.beta).toFixed(3)` | L999 |
| Beta-distance color | `\|s.sum.beta-1\| > \|prev.beta-1\| ? --warn : --txt` (directional awareness) | L1002 |
| `h` delta | `s.sum.h − prev.h` with `\|Δ\| <= 100` data-sanity gate | L1005–L1007 |
| Holdings-snapshot diffs | For every ticker in union of `priorH` and `curMap`, `d = cur - prior`; keep `\|d\|>=0.5`, sort by `\|d\|`, top 2 | L1021–L1031 |
| Name truncation | `.slice(0,23)+'…'` at 24 chars (S4) / `.slice(0,19)+'…'` at 20 chars (C5) — **inconsistent lengths** | L968, L1029 |

### 1.5 Ground truth verification

- **How to verify (State bullets):**
  - TE / cash thresholds: compare `cs.sum.te`, `cs.sum.cash` against the values in the configuration modal's threshold fields. Flip the threshold in the modal and reload — State bullet wording should change band.
  - Top OW/UW: cross-check against Row 2 `cardSectors` table — the top row (by `|a|` desc) should match S2/S3. Cash is excluded here but NOT in the main Sectors table by default — watch for this divergence when auditing.
  - Top risk holding: cross-check Holdings tab, sort by `|TE Contrib|` desc — top row's name + `p%` + `|tr|%` should match S4.
- **How to verify (Changes bullets):**
  - TE/AS/Beta/H deltas: change the week selector to the prior week and compare `getSelectedWeekSum()` values. `prev` here is explicitly `hist.sum[len-2]`, meaning deltas are **always computed from the latest two weekly snapshots**, independent of the header week selector. This is a divergence worth flagging — see Issue #3.
  - C5 holdings deltas: inspect `localStorage.getItem('rr_holdsnap_v1')`, match the `prior.holdings` map to the Holdings tab WoW column.
- [x] All 6 state bullets + 5 change bullets traced to source fields
- [x] All thresholds have fallback defaults (`|| 8`, `|| 6`, `|| 0.5`, `|| 5`)
- [x] `isFinite` guards on `x.a` (sectors), `h.tr` (holdings), and `h.p` in snap diff (L1019)
- [x] Cash filter via `/cash/i.test(x.n)` AND central `isCash(h)` helper — dual-layer protection
- [x] Snap-read wrapped in `try/catch` (L1012, L1034) — bad localStorage cannot crash the card
- [ ] **Spot-check pending:** no `latest_data.json` in repo at audit time — cannot verify specific numbers
- [x] Data-sanity: `|hD| <= 100` guard on holdings WoW (the "data bug signal" comment at L1006 reflects a real past incident; keep)

### 1.6 Missing / null handling

| Scenario | Behavior | Code |
|---|---|---|
| `s` falsy or `s.sum` missing | Returns empty string (card not rendered, not even a container) | L947 |
| Both bullet arrays empty | Returns empty string (silent suppression) | L1036 |
| `s.sum.te` null | S1 skipped | L951 |
| `s.sectors` missing | S2/S3 skipped via `\|\|[]` | L958 |
| `s.hold` missing | S4 and C5 skipped via `\|\|[]` | L966, L1019 |
| `s.hist.sum` empty or length < 2 | All C1–C4 skipped (`prev` stays null) | L987 |
| `localStorage['rr_holdsnap_v1']` corrupt / absent | Swallowed by try/catch; C5 skipped silently | L1012, L1034 |
| `h.t` missing on a holding | Holding excluded from curMap (L1019 `if(h.t && isFinite(h.p))`) | L1019 |
| `f.a` null in factors | Gets `\|\|0`, then fails `>= sigma` gate; skipped | L973 |
| `prev.te` or similar null | Per-bullet `!= null` checks skip that delta | L989, L994, L999 |

**Assessment: GREEN** — Null handling is thorough, defensive coding is better than most tiles in the dashboard (try/catch around localStorage read, `isFinite` on numerics, explicit data-bug sanity gate on `hD`). Primary pending item is the spot-check (blocked on data file availability — same as cardCountry audit).

---

## 2. Columns & Dimensions Displayed

`cardThisWeek` is **not a table or chart** — it is a two-column flex layout of `<ul>` bullets.

| Column | Contents | DOM | Styling |
|---|---|---|---|
| Left: "State" | Up to 6 bullets (S1–S6) synthesizing current-week status | `<div style="flex:1;min-width:300px">` with `<ul>` | label=10px uppercase indigo; bullets 12px line-height 1.7 `var(--txth)` |
| Right: "Changes vs Prior Week" | Up to 5 bullets (C1–C5) synthesizing WoW movement | same shell | same |

Layout wrapper: `display:flex; flex-wrap:wrap; gap:24px; margin-top:8px` (L1047).

**Encodings within bullets:**
- **Bold** via `<strong>` for the subject (metric name or entity)
- **Inline color** on the delta arrow span (`var(--neg)` up, `var(--pos)` down for TE — because ↑TE = more risk = bad); neutral `var(--txt)` for AS/Holdings where direction has no risk judgment; `var(--warn)` for Beta when moving away from 1.0
- Arrows use Unicode `↑` / `↓` (U+2191 / U+2193)

---

## 3. Visualization Choice

### 3.1 Type
Narrative insight card — a **hybrid of static text and conditional rule-based synthesis**. No chart, no table, no sparkline. Closest analogue in the codebase: `whatChangedBannerHtml` and `riskAlertsBannerHtml` (siblings in the Exposures tab).

### 3.2 Axis scaling
N/A — no axes.

### 3.3 Color semantics
- `var(--neg)` (red): ↑TE (risk increased) — **risk-directional**, not direction-directional
- `var(--pos)` (green): ↓TE (risk decreased)
- `var(--txt)` (muted): AS / Holdings deltas — explicitly no judgment
- `var(--warn)` (amber / `#a78bfa` dark, indigo-ish): Beta moved further from 1.0
- `var(--pri)` (indigo `#6366f1`): column-header mini-caps
- `var(--txth)` (bright): bullet body text
- All reads from CSS vars — **theme-aware by construction**. Confirmed works in both themes (L13, L283).

### 3.4 Responsive behavior
- Uses `flex-wrap:wrap` with `min-width:300px` per column — will stack vertically on narrow viewports (< ~640px body width)
- `gap:24px` preserved when wrapped

### 3.5 Empty state
**Silent suppression** — if `stateBullets.length===0 && changeBullets.length===0`, returns `''`. The card never renders. This is correct UX for an insight card (don't show an empty "nothing to report" shell), but it means a first-run user with no history and no threshold triggers sees nothing, with no explanation of what the card would look like when populated. Consider a fall-back "No material changes this week" message for the "all quiet" case. See Issue #1.

### 3.6 Loading state
Inherits global `#loading` overlay. Nothing per-tile.

---

## 4. Functionality Matrix (vs cardSectors benchmark)

| Capability | cardSectors (benchmark) | cardThisWeek (this tile) | Match? |
|---|---|---|---|
| **Sort** | ✅ all cols `sortTbl` + `data-sv` | ❌ N/A (no table) | ✅ N/A |
| **Filter** | ❌ (by design — 11 rows) | ❌ N/A (no list to filter) | ✅ N/A |
| **Column picker (⚙)** | ✅ `rr_sec_cols` | ❌ N/A | ✅ N/A |
| **Row click → drill** | ✅ `oDr('sec', name)` | ❌ NONE — no bullet is clickable; S1 (TE), S4 (top risk holding), S2/S3 (sectors), and S5 (factors) all reference entities that have natural drill targets (`oDrMetric('te')`, `oSt(ticker)`, `oDr('sec',name)`, `oDrFacRiskBreak()`) but none are wired | ❌ GAP (high-value) |
| **Cell value click** | ❌ n/a | ❌ n/a | ✅ parity |
| **Right-click context menu (cell copy)** | ✅ global contextmenu → `copyValue()` | ⚠ Global handler should still fire on text selection, but there are no discrete "cells" to right-click — lesser value here | ⚠ partial |
| **Card-title right-click (note popup)** | ✅ `showNotePopup(e,'cardSectors')` | ✅ Inherits global delegation (L6049); `cardThisWeek` is a `.card` with `.card-title` so it will get a note popup | ✅ YES |
| **📝 Note badge** | ✅ `refreshCardNoteBadges()` scans all `.card[id]` | ✅ Inherits — `#cardThisWeek` has a stable id, so badge refresh will find it | ✅ YES |
| **Export PNG** | ✅ `screenshotCard('#cardSectors')` | ❌ NONE — no ⬇ menu rendered | ⛔ N/A per user hard rule (no PNG buttons) |
| **Export CSV** | ✅ `exportCSV('#secTable table',...)` | ❌ NONE — no table to export; could export bullets as `state\|change\|text` rows | ⚠ GAP (low value, optional) |
| **Full-screen modal (⛶)** | ❌ not present | ❌ not present | ✅ parity |
| **Toggle views** | ✅ Table / Chart | ❌ N/A | ✅ N/A |
| **Range selector** | ✅ in drill modal | ❌ N/A — tile represents "this week" by definition | ✅ N/A |
| **Color-mode picker** | ❌ n/a | ❌ n/a | ✅ parity |
| **Hover tooltip** | ✅ `.tip::after` on all numeric headers | ❌ NONE — no column-header tooltips explaining the rule thresholds (e.g., "TE red ≥ 8% configurable in Settings") | ⚠ GAP (minor) |
| **Theme-aware** | ✅ `THEME()` / `var(--x)` | ✅ All colors via CSS vars (`--neg`, `--pos`, `--txt`, `--warn`, `--pri`, `--txth`); no hardcoded hex in this function | ✅ YES |
| **Color-blind safe** | ❌ not implemented | ❌ not implemented (but arrows ↑/↓ provide non-color cue — better than cardSectors in this regard) | ✅ PLUS (implicit) |
| **Threshold classes (row warn/alert)** | ✅ `thresh-warn` / `thresh-alert` | N/A — tile IS the threshold alert | ✅ N/A |
| **Week-selector sensitivity** | ✅ reads `getSelectedWeekSum()` | ❌ **Reads `s.sum` directly + `hist.sum[len-2]`** — always shows latest-week insight regardless of header week selector. `rExp()` uses `getSelectedWeekSum()` for the sum-cards below but this tile does NOT | ⚠ GAP / divergence |
| **Historical-week banner** | ✅ shown via `weekBannerHtml()` when `_selectedWeek` set | ✅ banner renders above this tile — but tile itself still shows LATEST, creating potential confusion (banner says "Viewing week of April 14" while tile bullets are about the most recent week) | ⚠ inconsistency |
| **Empty state** | ❌ renders empty tbody silently | ⚠ silently suppresses entire card when nothing to report — intentional for insight cards but no user-facing explanation | ⚠ minor |

### 4.1 Functionality gaps vs Sectors benchmark

**Missing (should add — high value):**
1. **Clickable bullets / inline drill links** — S1 → `oDrMetric('te')`; S4 → `oSt(topRisk.t)`; S2/S3 → `oDr('sec', topOW.n)`; S5 → `oDrFacRiskBreak()`; S6 → `oDrMetric('cash')`; C1 → `oDrMetric('te')`; C5 → `oSt(ticker)`. Pattern: wrap the `<strong>` span in `<a onclick="...">` with `cursor:pointer;text-decoration:underline dotted`. Every bullet subject has a natural drill target — currently none are wired. **This is the top feature gap.**
2. **Header tooltips** — add a tiny `(?)` icon next to "State" and "Changes vs Prior Week" column-headers with `class="tip" data-tip="Thresholds: TE red ≥ Y%, cash > X%, factor \|σ\| ≥ Z. Configure in Settings."` Makes the rule transparent.
3. **Week-selector awareness** — tile reads `s.sum` directly, so when a user selects a historical week via the header `‹ date ›`, this tile does NOT refresh to reflect that week's insights. The banner above says "Viewing week of …" but the card still narrates the latest week. Options: (a) read `getSelectedWeekSum()` and compute deltas vs the week *before* selected, (b) suppress the card entirely on historical weeks with a short "Insight card reflects latest week only" note, or (c) leave as-is with explicit label "(latest week)". PM decision — flag in Issue #3.

**Minor (polish):**
4. **Name truncation inconsistency** — S4 truncates at 24 chars, C5 at 20. Pick one (recommend 24) and apply both places.
5. **C5 missed-holding edge** — snap diffs only surface if `h.p >= 0.5` swing; a completely-new holding (0 → 0.3%) at 0.3% weight is invisible. Document or tighten the threshold rule.
6. **Hardcoded thresholds in fallbacks** — `teRed||8, teAmb||6, sigma||0.5, cashMax||5` duplicate the defaults at L4818. Single source of truth: use `_thresholdsDefault.teRed` etc. as the fallback.
7. **Empty-state message** — if both arrays are empty, render a small neutral "No material state bullets or week-over-week changes worth surfacing." Better than silent suppression for the "all quiet" case (which is itself signal).
8. **CSV export of bullet list** — wire up an `exportCSV` that emits `column,bullet` rows. Low value but would match the benchmark's download affordance. Skip if not demanded.

**Exceeds benchmark (keep):**
- **Risk-directional color** (TE ↑=red, not just "delta↑=red") — a semantic choice that's more sophisticated than cardSectors' purely-sign-based coloring
- **Beta-distance warning** (amber when moving further from 1.0) — nuance absent in other deltas
- **Data-sanity gate** (`|hD|<=100`) — explicit defense against a known parser bug class
- **Arrow glyphs** provide color-blind-safe direction cues

---

## 5. Popup / Drill / Expanded Card

**N/A — this tile has no drill modal of its own.** It is the synthesis tier; drills live on the child tiles it summarizes (cardSectors, Holdings, Factor Exposures, cardFacButt, etc.). See Issue #1 — the fix is to WIRE inline drill links from bullets to the relevant existing modals, not to add a new modal.

---

## 6. Design Guidelines

### 6.1 Density

| Element | Value | Dashboard standard | Match? |
|---|---|---|---|
| Card padding | `16px` (inherits `.card`) | 16px | ✅ |
| Card border-radius | `12px` (inherits `.card`) | 12px | ✅ |
| Card bg | `var(--card)` | standard | ✅ |
| Card-title font | 12px (inherits `.card-title`) | 12px | ✅ |
| Column header "State" / "Changes" | 10px, uppercase, letter-spacing 0.5px, 600, color `var(--pri)` | Matches section-header pattern used throughout (e.g., Spotlight group headers) | ✅ |
| Bullet body font | 12px, line-height 1.7, color `var(--txth)` | Dashboard standard for body text is 11–12px; line-height 1.7 is more generous than the 1.5 used in tables (intentional for readability) | ✅ |
| Delta arrow font | 9px, weight 500 | — | ✅ intentionally compact |
| Inter-column gap | `24px` | — | ✅ generous, appropriate for a narrative card |
| Inter-card margin | `margin-bottom:16px` (inline) | Standard | ✅ |
| Min-column-width | `300px` (triggers wrap on narrow) | — | ✅ reasonable |

### 6.2 Emphasis & contrast

| Element | Treatment | Rationale |
|---|---|---|
| Bullet subject | `<strong>` bold | Draws eye to the entity/metric |
| Bullet body | regular weight, `var(--txth)` | Primary content |
| Column headers ("State" / "Changes…") | `var(--pri)` indigo, uppercase, mini-cap | Consistent with rest of dashboard's section-divider pattern |
| TE delta | `var(--neg)` up / `var(--pos)` down | **Risk-directional** — semantically correct (↑ risk = red) |
| AS/Holdings delta | `var(--txt)` muted | Neutral — no directional judgment |
| Beta delta | `var(--warn)` when moving away from 1.0 else `var(--txt)` | Nuanced: magnitude vs position matters |
| C5 holdings delta | `var(--pos)` up / `var(--neg)` down | Sign-directional — bigger position = more conviction = "good" is PM's read (but debatable; a rising underweight is also "up") |

**Minor semantic question:** C5 uses sign-directional coloring (`d>0 → pos`), not risk-directional. For a position increase in a bad stock this could mislead. Flagged but not urgent (PM decision).

### 6.3 Alignment

| Element | Alignment | Implementation |
|---|---|---|
| Bullets | Left | default `<ul>` with `padding-left:18px` |
| Column headers | Left | inline `margin-bottom:6px`, no explicit align |
| Arrow + delta value | Inline after value | `<span style="margin-left:3px">` |

No right-aligned numerics (none here — all numbers are inline in prose).

### 6.4 Whitespace

| Gap | Value |
|---|---|
| Inter-column | 24px |
| Column-header → first bullet | 6px |
| Inter-bullet | default `<ul>` line-height 1.7 |
| Card-title → columns | 8px (`margin-top:8px` on the flex wrapper) |
| Bullet `<li>` padding | default |

### 6.5 Motion / interaction feedback

| State | Treatment |
|---|---|
| Card entry | Inherits `.card` slide-up animation (global) |
| Hover on bullets | **NONE** — bullets are not interactive, so no hover state (fix when drill-links are added — Issue #1) |
| Click | **NONE** currently (see Issue #1) |
| Card-title right-click | Note-popup (inherited) |
| Empty | Silent suppression |

### 6.6 Cross-tile conventions check

Per `AUDIT_LEARNINGS.md`:
- [x] Theme-aware (all CSS vars, no hardcoded hex)
- [N/A] `data-sv` / `sortTbl` primitives — not applicable (no table)
- [N/A] Rank-cell alignment / Spotlight group — not applicable
- [N/A] Threshold row classes — the whole card IS the threshold alert
- [x] No PNG buttons (compliant with user hard rule — verified 2026-04-20)
- [x] Empty-state guard — present (silent suppress); could be improved with a fallback message
- [x] Stable card id `#cardThisWeek` for note-badge refresh

**Assessment: GREEN** — Design is clean, theme-aware, and semantically thoughtful (risk-directional colors, data-sanity gates, dual-language sophistication). Main gap is interactivity (Section 4).

---

## 7. Known Issues & Open Questions

| # | Issue | Severity | Category |
|---|---|---|---|
| 1 | **No inline drill links** on any bullet — every bullet subject has a natural existing modal target but none are wired. Highest-value fix. | **High** | Feature gap |
| 2 | **No header tooltips** explaining the threshold rules (teRed/teAmber/sigma/cashMax). Users have no way to know what "amber" means without opening Settings. | Medium | Consistency |
| 3 | **Tile ignores week selector** — reads `s.sum` + `hist.sum[len-2]`, always latest-week. On a historical week view, the banner says "Viewing week of April 14" while this tile silently narrates the current (latest) week. PM decision: (a) make week-aware, (b) suppress on historical weeks, or (c) label explicitly as "latest week only". | Medium | UX / consistency |
| 4 | **Name truncation inconsistent** — 24 chars in S4, 20 chars in C5. | Low | Polish |
| 5 | **C5 threshold** (±0.5%) may miss new/closed positions with small weights. Small holdings never appear; new positions that go 0→0.3% are invisible. | Low | Data rule |
| 6 | **Fallback thresholds duplicated** — `|| 8 / || 6 / || 0.5 / || 5` hard-coded, should read from `_thresholdsDefault`. | Low | Code hygiene |
| 7 | **Silent empty state** — card disappears entirely on "all quiet" weeks; no user-facing signal. Could confuse users ("where did that card go?"). | Low | UX |
| 8 | **C5 sign-directional color** — a position increase in a bad-ranked stock colors green (good); a position decrease in a winner colors red. Debatable, PM call. | Low | Semantic |
| 9 | **Spot-check pending** — no `latest_data.json` in repo at audit time. | Medium | Verification |
| 10 | **Max 3 factor bullets (S5)** — if more than 3 factors exceed σ threshold, silently dropped. Consider "+ N more" suffix. | Low | UX |
| 11 | **No CSV export affordance** — the download `⬇` menu present on all other tiles is absent here. Low-value but breaks expectation. | Low | Feature gap |
| 12 | **Tile name vs location** — user refers to it as Overview/hero tile; code places it in Exposures. There is no separate Overview tab in the current DOM (Exposures is the default/first). Worth confirming naming with PM — if the tab will be renamed "Overview", adjust accordingly. | Low | Naming |

---

## 8. Verification Checklist (before sign-off)

- [x] **Data accuracy**: all 6 state-bullet paths + 5 change-bullet paths traced to source (`s.sum`, `s.sectors`, `s.hold`, `s.factors`, `s.hist.sum`, `_thresholds`, `localStorage.rr_holdsnap_v1`)
- [x] **Edge cases**: `s.sum` null, arrays missing, `hist.sum` length<2, localStorage corrupt, individual field nulls — all handled with guards or skip-the-bullet semantics
- [N/A] **Sort**: no table
- [N/A] **Filter**: no list
- [N/A] **Column picker**: no columns
- [N/A] **Export PNG**: compliant with no-PNG rule
- [ ] **Export CSV**: not present (low-value gap — optional)
- [N/A] **Full-screen modal**: not designed for one
- [x] **Popup / drill**: none — this is a synthesis tile, not a drill source (but should gain inline drill links per Issue #1)
- [x] **Responsive**: `flex-wrap:wrap; min-width:300px` — columns stack on narrow
- [x] **Themes**: all CSS vars, no hardcoded hex — dark + light both fine
- [x] **Keyboard**: inherits global Escape handler (no modal here); tab-order N/A since bullets aren't interactive
- [x] **No console errors**: try/catch around localStorage read; `isFinite` + null-guards on all numerics
- [x] **Theme-aware colors**: 6 CSS vars used (`--pos`, `--neg`, `--warn`, `--pri`, `--txt`, `--txth`), zero hardcoded hex in `thisWeekCardHtml`
- [x] **isFinite guards**: present on `x.a`, `h.tr`, `h.p` (snap map)
- [ ] **Spot-check vs CSV**: pending — no data file in repo
- [x] **Stable DOM id**: `#cardThisWeek` confirmed for note-badge + inspector targeting

---

## 9. Related Tiles

| Related Tile | Relationship |
|---|---|
| **sum-cards row (TE / Idio / Factor)** | Sibling; renders directly below this card (L1099–L1113). This is what the user colloquially calls "headline metrics" — if tiles get renamed/restructured, this card and the sum-cards should be considered together. |
| **cash+benchmark strip (L1115)** | Sibling directly below sum-cards; shows `s.sum.cash` numerically. S6 (cash bullet) surfaces the same field when exceeding threshold. |
| **riskAlertsBanner** | Rendered below this card (L1125); uses same `_thresholds` object. State bullets S1/S6 overlap with alert content — potential duplication. |
| **whatChangedBanner** | Rendered below (L1126); `holdsnap` data source overlaps with C5 logic. Two tiles reading same localStorage. |
| **watchlistCard** | Rendered below (L1127). Independent. |
| **cardSectors** | S2/S3 (OW/UW bullets) summarize the cardSectors table; inline-drill target candidate for Issue #1. |
| **Holdings tab / oSt modal** | S4 (top TE holding) + C5 (position changes) are both natural drills to `oSt(ticker)`. |
| **Factor Exposures tab / oDrFacRiskBreak** | S5 (factor tilts) is natural drill to factor detail. |
| **oDrMetric('te' / 'cash' / 'as')** | S1, S6, and all C1–C3 bullets are candidates for inline-drill to these metric modals. |
| **Settings → Thresholds modal** | S1/S5/S6 all reference user-configurable thresholds. Tooltips on this card's headers (Issue #2) should link to Settings. |

---

## 10. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-21 | Full three-track audit. Signed off v1. | Tile Audit Specialist CLI |

---

## Agents that should know this tile

- **risk-reports-specialist** — master agent, field authority (TE/AS/Beta/cash definitions)
- **tile-audit-specialist** — authored this audit
- **rr-design-lead** — for section 6 sign-off (column-header tooltips, arrow treatment)
- **rr-data-validator** — for section 1.5 spot-check when data becomes available

---

## Section Summary

| Section | Status | Notes |
|---|---|---|
| **0. Identity** | 🟢 GREEN | Tile is at top of Exposures tab (not Overview); scope clarified vs sibling sum-cards. Stable DOM id + single render fn. |
| **1. Data Source** | 🟢 GREEN | All 11 bullets (6 state + 5 change) traced to fields. Best-in-file defensive coding: try/catch on localStorage, `isFinite` on numerics, explicit data-sanity gate on holdings delta. Spot-check pending (no data file). |
| **4. Functionality** | 🟡 YELLOW | Clean and bug-free, but **no inline drill links** on any bullet (highest-value gap) and **ignores week-selector** (UX inconsistency with banner). Header tooltips missing. |
| **6. Design** | 🟢 GREEN | Fully theme-aware (6 CSS vars, zero hardcoded hex). Semantic color choices (risk-directional TE, beta-distance warn) are more sophisticated than benchmark. Consistent density/spacing. |

---

## Proposed fixes (for main session to serialize)

### Trivial (main session can apply directly — pattern already established)

| # | Fix | Lines affected | Pattern |
|---|---|---|---|
| T1 | **Add header tooltips** to "State" and "Changes vs Prior Week" column headers explaining the threshold config | L1038, L1042 | `class="tip" data-tip="Thresholds: TE red ≥ ${_thresholds.teRed}% (configurable in Settings)"` |
| T2 | **Unify name truncation** at 24 chars across S4 and C5 (currently 24/20) | L1029 | change `slice(0,19)+'…'` at length `>20` to `slice(0,23)+'…'` at length `>24` |
| T3 | **Use `_thresholdsDefault` as fallback source** instead of hard-coded duplicated literals | L952, L972, L979 | `_thresholds.teRed ?? _thresholdsDefault.teRed` — single source of truth |
| T4 | **Add empty-state message** when both bullet arrays are empty — small muted "No material risk alerts or week-over-week changes this week." instead of silent suppression | L1036 | 3-line change: replace `return ''` with a minimal card shell + quiet-state paragraph |
| T5 | **Add "+ N more" suffix** to S5 factor list when more than 3 tilts exceed σ | L976 | `bigFac.length > 3 ? `…, +${bigFac.length-3} more` : ''` |

### Non-trivial (need PM nod or structural change)

| # | Fix | Rationale |
|---|---|---|
| N1 | **Wire inline drill links on all bullet subjects** — S1→`oDrMetric('te')`, S2/S3→`oDr('sec', name)`, S4→`oSt(ticker)`, S5→`oDrFacRiskBreak()`, S6→`oDrMetric('cash')`, C1→`oDrMetric('te')`, C2→`oDrMetric('as')`, C5→`oSt(ticker)`. Wrap the `<strong>` spans in clickable anchors with `cursor:pointer;text-decoration:underline dotted`. Highest-value UX upgrade on this tile. | Turns a passive insight card into a navigational hub. Every target modal already exists. |
| N2 | **Decide week-selector behavior** — (a) refresh card to selected week's insights using `getSelectedWeekSum()` (requires restructuring data reads to use historical `hist.sum` entries, which lack sector/hold/factor data, so some bullets won't compute historically) OR (b) suppress tile when `_selectedWeek` is set OR (c) label "(latest week only)". PM decision. | Fixes the banner-vs-tile narrative mismatch. Option (b) is simplest; (a) is most complete but blocked by the two-layer history architecture (no historical sector/holdings). |
| N3 | **Reconsider C5 coloring** — currently sign-directional (up=green). Consider risk-directional or at least quintile-aware (down in a Q5 holding = good, not bad). | Semantic correctness; blocked on PM clarification. |
| N4 | **Add CSV export affordance** via `exportCSV` matching the `⬇` menu on other tiles — emits bullet rows `column,text`. | Consistency with other tiles' affordances. Low user value but breaks expectation. Skip unless requested. |

---

**Sign-off:** All verifiable checklists pass (data-accuracy spot-check pending on no-data-file blocker, same as prior audits). Status changed to `signed-off`. Fix queue above for main-session serialization.
