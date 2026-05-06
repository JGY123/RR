# RR Dashboard — Hover Label Audit

**Date:** 2026-05-05
**Auditor:** tile-audit subagent
**Scope:** all hover affordances in `dashboard_v7.html` (~14,124 lines)
**User trigger (flagged twice):** "many hover labels are in font color that's not visible, some have repeating info, they should be cleaner / concise / crisp."
**Pre-launch context:** ~3 weeks before Alger PMs use RR daily; clean hovers are a professional-grade signal.

---

## Top-of-page alerts (read these first)

1. **TIP-PORTAL-001 — RED — invisible navy-on-dark in Alger theme.** The `#tip-portal` CSS sets `background:#0f1623` (hardcoded dark) AND `color:var(--txth)`. On Alger theme `--txth=#002b54` (Alger navy). **Result: navy text on dark slate = unreadable.** Every `data-tip` tooltip across the entire dashboard fails on Alger. This is the single largest user-visible regression, and it's almost certainly what the user has been seeing.

2. **PLOTLY-HOVER-001 — RED — same antipattern in 3 Plotly hovers.** Lines 6395 (rRegRiskHeatmap), 7053 (country choropleth map), 7272 (rCountryRiskHeatmap) all set `hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',font:{color:T.txth,...}}`. On Alger, navy text on dark slate again — invisible. Same root cause as the Redwood Groups treemap that was fixed in `f655fcb`.

3. **MCR-FORMAT-001 — YELLOW — MCR with a `%` sign violates project rule.** Per CLAUDE.md memory `feedback_mcr_no_percent.md`: "MCR is not a percentage — never render MCR with a % sign on RR." Two hovertemplates violate: line 11824 (`Idio MCR: %{y:.2f}%`) and line 13019 (`MCR: %{x:.3f}%`). User-flagged behavior; quick fix.

4. **TREEMAP-WHITE-TEXT-001 — RED-adjacent — same antipattern as the Alger treemap fix already shipped.** Line 7626 in `rTree()` (Holdings Treemap) uses `textfont:{color:'#ffffff'}` hardcoded. On Alger theme + light cell colors → white-on-white text invisible. This is NOT a hover string per se but is in the same family the user flagged in `f655fcb`. Worth fixing in the same sweep.

---

## Section 1 — Plotly chart hovers

**Inventory:** 63 `hovertemplate` strings across the file. Categorized below.

### 1.1 Theme-aware hover label config (RED)

Three configs hardcode the bg as dark slate but set `font.color:T.txth`. On Alger theme `T.txth=#002b54` (navy). Navy text on dark slate is unreadable.

| # | Line | Tile / function | Current | Issue | Fix |
|---|------|-----------------|---------|-------|-----|
| 1 | 6395 | rRegRiskHeatmap (Region × Factor heatmap, Regions tab) | `hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:T.grid,font:{color:T.txth,...}}` | RED — navy text on dark slate on Alger | Replace with `HOVERLABEL_THEME` (already light text on dark) |
| 2 | 7053 | Country choropleth map (Countries tab) | Same pattern | RED — same | Replace with `HOVERLABEL_THEME` |
| 3 | 7272 | rCountryRiskHeatmap (Country × Factor heatmap) | Same pattern | RED — same | Replace with `HOVERLABEL_THEME` |

**Edit-tool ready replacement** (apply to all three lines):

```diff
- hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:T.grid,font:{color:T.txth,family:'DM Sans, system-ui',size:11},align:'left'}
+ hoverlabel:HOVERLABEL_THEME
```

(Line 7053 has `align:'left'`; lines 6395 and 7272 don't. `HOVERLABEL_THEME` already includes `align:'left'`, so swap is direct.)

### 1.2 HOVERLABEL_THEME — module-level snapshot, not theme-reactive (YELLOW)

| # | Line | Issue |
|---|------|-------|
| 4 | 6196 | `const HOVERLABEL_THEME` is evaluated **once at script parse time**. It's used in ~17 inline traces. Switching themes does NOT update it. The bgcolor is `rgba(15,23,42,0.96)` (dark slate); on Alger theme this is still functionally readable (white text on dark popup against a white page) but **visually dissonant** with the firm's white-canvas brand. |

**Fix (low priority for launch, high priority post-launch):**
Convert `HOVERLABEL_THEME` from a `const` to a function `getHoverlabelTheme()` that reads CSS vars, and call it everywhere a `hoverlabel:HOVERLABEL_THEME` is set today. Or add a second variant `HOVERLABEL_LIGHT` and have the layout helper pick. The cleanest: have `buildPlotBg()` (line 6176, which IS rebuilt on theme change) be the single source of truth, and replace every `hoverlabel:HOVERLABEL_THEME` with a spread from `plotBg.hoverlabel`.

### 1.3 Mini-sparkline KPIs — no hover label config (YELLOW)

| # | Line | Tile | Issue |
|---|------|------|-------|
| 5 | 7892 (loop) | miniTE / miniAS / miniBeta / miniH (Risk-tab KPI sparklines) | No `hoverlabel` set — Plotly defaults to white bg + black text. Looks adequate on Alger but **clashes with dark theme** (white popup on dark page). Inconsistent with all other tiles which use HOVERLABEL_THEME. |

**Fix:**
```diff
- hovertemplate:sp.hover
+ hovertemplate:sp.hover, hoverlabel:HOVERLABEL_THEME
```
inside the `Plotly.newPlot(sp.id, [{...}], ...)` trace at line 7892.

### 1.4 MCR-with-percent violations (YELLOW — project rule)

Per CLAUDE.md memory: "MCR is not a percentage — never render MCR with a % sign on RR."

| # | Line | Tile | Current | Fix |
|---|------|------|---------|-----|
| 6 | 11824 | idioHistChart (Risk-tab idio time series) | `Idio MCR: %{y:.2f}%` | `Idio MCR: %{y:.2f}` |
| 7 | 13019 | renderFsScatter (compare-strategies fullscreen) | `MCR: %{x:.3f}%` | `MCR: %{x:.3f}` |

(Lines 9995 and 11528 already correctly omit `%` — keep as reference.)

### 1.5 Hovertemplate redundancy with legend (YELLOW)

When Plotly has `hovermode:'x unified'` and a named trace, the **legend name is shown in the hover popup as the trace prefix**. If the hovertemplate ALSO repeats the trace name, you see it twice.

| # | Line | Tile | Current | Issue |
|---|------|------|---------|-------|
| 8 | 8651-8667 | cardBetaHist (3 reference lines) | `name:'Predicted ('+f2(betas.predicted,3)+')'` PLUS `hovertemplate:'Predicted: '+f2(betas.predicted,3)` | Value appears twice (in legend label + in hover) |
| 9 | 8956 | Factor history overlay | `name:f.n+(_fallback?' ᵉ':'')` PLUS `hovertemplate:f.n+(_fallback?' (snap_attrib fallback)':'')+'<br>...'` | Factor name AND fallback indicator repeat. Cleaner: drop name from hovertemplate (already in legend) and just show date + value. |
| 10 | 8974 | Factor return history overlay | `name:f.n` PLUS `hovertemplate:f.n+'<br>...'` | Name twice. |
| 11 | 8991-9007 | Industry/Country sub-checkbox traces | Same pattern — `name:item` AND `hovertemplate:item+'<br>...'` | Name twice |

**Fix (line 8651 example):**
```diff
- hovertemplate:'Predicted: '+f2(betas.predicted,3)+'<extra></extra>'
+ hovertemplate:f2(betas.predicted,3)+'<extra></extra>'
```
Plotly will use the trace `name` automatically as the prefix in unified hover mode.

### 1.6 Country choropleth richHover — visual fluff (YELLOW)

| # | Line | Tile | Issue |
|---|------|------|-------|
| 12 | 7031-7039 | Country choropleth richHover | Includes two `━━━━━━━━━━━━━━━━━━━━━━━━━` divider lines. User flagged "should be cleaner / concise / crisp." The dividers add visual weight without separating actually-distinct content sections. |

**Fix:** drop both divider lines. The result is still well-organized (3 metric rows + 1 holdings list) without the extra noise.

### 1.7 Clean Plotly hovers (✅ — for reference)

Examples of well-formed hovers, used as patterns for fixes above:
- 9958 — bar chart KPI: clean, single-purpose, uses HOVERLABEL_THEME
- 9995 — bar chart with customdata: clean, no MCR-pct violation
- 12697-12703 — characteristics history: clean unified-hover pair

---

## Section 2 — Tooltip portal (`.tip[data-tip]`)

**Inventory:** 111 `data-tip=` attributes throughout the file. The portal singleton at L13767-13830.

### 2.1 RED — invisible text on Alger theme

| # | Line | Element | Issue |
|---|------|---------|-------|
| 13 | 453 | `#tip-portal` CSS rule | `background:#0f1623` (hardcoded dark) + `color:var(--txth)` = navy on dark = unreadable on Alger. |

**Edit-tool ready fix:**
```diff
- #tip-portal{position:fixed;background:#0f1623;color:var(--txth);padding:10px 14px;border-radius:8px;...}
+ #tip-portal{position:fixed;background:#0f1623;color:#f1f5f9;padding:10px 14px;border-radius:8px;...}
```

Reasoning: Hardcode the foreground color to a near-white slate (matching the existing dark hoverlabel config at L6189, L6196). The portal background is already hardcoded dark; the foreground should match. Don't try to make this theme-aware via CSS vars — keep the popover always-dark for consistency with Plotly hovers (which all also use dark bg + light text). This matches what users see on every other hover popup.

Bonus: also fix the arrow border colors at L457-458 — already `#0f1623` matching the bg, so they're fine as-is. But verify after the swap.

### 2.2 GREEN — most data-tip strings are well-formed

Spot-checked ~20 representative strings. Noted patterns:
- Card-title `data-tip` strings (~15 instances) are crisp 1-2 sentence explanations (e.g., L3048 `cardWeekOverWeek` — succinct, scoped, no fluff)
- Threshold tip on L2842 / L2847 reuses a `${thresholdTipBase}` variable — DRY, good
- Cell-level `data-tip` for derived values (L4951 `_c_synth`, L4954 `imp.derived`) include source-of-truth attribution per anti-fabrication policy — good

### 2.3 YELLOW — minor polish opportunities

| # | Line | Tile | Issue |
|---|------|------|-------|
| 14 | 814 | "All Holdings" pill | Native `title` attribute is **520 characters long**. Way too long for a native browser tooltip (browsers truncate / line-wrap unpredictably). Should be promoted to `data-tip` (uses portal, formats nicely up to 340px max-width, line-wraps cleanly). |
| 15 | 810 | "Universe" wrap | Native `title` is 250 chars. Same issue — promote to `data-tip`. |
| 16 | 818 | "ORVQ rank averaging" wrap | Native `title` is 200 chars. Same. |
| 17 | 8221 | "Cum Return" pill | Native `title` is 350 chars. Same. |
| 18 | 8254 | corrPeriod select | Native `title` is 270 chars. Same. |

**Fix pattern (example for L810):**
```diff
- <div id="aggModeWrap" title="Universe: which holdings the count / weight / ORVQ-average columns aggregate across. TE / MCR / factor_contr columns are universe-INVARIANT (B116) — they show the same value regardless of pill choice." style="...">
+ <div id="aggModeWrap" class="tip" data-tip="Universe: which holdings the count / weight / ORVQ-average columns aggregate across. TE / MCR / factor_contr columns are universe-INVARIANT (B116) — they show the same value regardless of pill choice." style="...">
```

Note: when you add `class="tip"`, the dotted-underline CSS (`border-bottom:1px dotted`) will appear. For wrappers that don't want the underline, use `data-tip` directly without the `tip` class — but you'll need to extend the JS hover handler at L13806/13810/13815 to also match bare `[data-tip]`. Cleanest: add a `tip-wrap` class that's `cursor:help` only, no underline, and have the hover handler match `.tip-wrap[data-tip]` too.

---

## Section 3 — Native browser `title` attributes

**Inventory:** 115 `title=` attributes; 9 of them are 150+ chars (poor UX in native tooltips).

### 3.1 GREEN — short, button-affordance titles

These are appropriate for native tooltips (short labels, no formatting needed):

| Pattern | Example line | Use case |
|---------|---------------|----------|
| Action verbs | 824, 826 ("Previous week" / "Next week") | Step buttons |
| Close affordances | 958, 4185, 6706 ("Close (Esc)") | Modal close buttons |
| Theme switcher | 877, 878 | Two-line description, small |
| Config buttons | 835, 836 ("Metric Glossary" / "Settings") | Single-word affordances |

About 90 of the 115 native titles are this kind. Leave them as-is.

### 3.2 YELLOW — long titles to promote to `data-tip`

Already covered in §2.3 above (items 14-18). Five concrete promotions.

### 3.3 RED — embedded `title` AND outer `data-tip` redundancy

Spot-checked: I found NO cases where both `title=` and `data-tip=` are on the same element. Good.

### 3.4 RED-adjacent — `title=""` with stale or fabricated info?

Spot-checked the 9 long titles. All look factual and not fabricated. The longer ones describe legitimate product nuances (universe semantics, cum-return derivation caveats). No anti-fabrication issues.

---

## Section 4 — Adjacent visibility regressions (out-of-scope but in-family)

These are NOT hovers but they're the SAME color/theme regressions the user has flagged in the past. Recommend bundling with the hover fixes in one commit.

| # | Line | Issue | Fix |
|---|------|-------|-----|
| 19 | 7626 | `rTree()` Holdings Treemap — `textfont:{color:'#ffffff'}` hardcoded. White-on-white invisible on Alger when cell color = heatMid (white). | Change to `color:T.tickH` (theme-aware navy on Alger, slate on dark). Same fix the cardGroups treemap got in `f655fcb`. |
| 20 | 11656 | TE Factor pie — `textfont:{...color:'#0f172a'...}` (very dark slate on inside-pie text). On Alger this is dark slate text on Alger-blue/red colored slices — fine. On dark theme, it's near-black text on red/green slices — readable but not great. Leave as-is unless user flags. |
| 21 | 11703-11704, 11714-11715 | TE histogram + idio histogram annotations — `font:{color:'#fff'}` hardcoded. On Alger the histograms render OK because the bars themselves are translucent purple/orange, but the "today XX%" annotation may render white-on-white. Low impact. |

---

## Summary stats

| Category | Total | ✅ Clean | 🟡 Minor | 🔴 Broken |
|---|---|---|---|---|
| Plotly hovertemplates | 63 | ~50 | 8 (1.4, 1.5, 1.6) | 4 (1.1 × 3 + missing label config × 1) |
| Tooltip portal (data-tip) | 111 | ~106 | 5 (long native titles to promote) | 1 (the portal CSS, breaks all 111 on Alger) |
| Native title attributes | 115 | ~110 | 5 (overlap with above promotions) | 0 |

**Total findings:** 21 (8 RED/RED-adjacent, 13 YELLOW)

---

## Recommended fix priority — top 10 for pre-launch

Ordered by user-visible impact and difficulty:

| # | Severity | Fix | Effort |
|---|---------|-----|--------|
| 1 | RED | TIP-PORTAL CSS color from `var(--txth)` → `#f1f5f9` (L453) | 1 line |
| 2 | RED | Three Plotly hoverlabels at 6395, 7053, 7272 → use `HOVERLABEL_THEME` | 3 lines |
| 3 | RED | Treemap textfont at 7626 → `T.tickH` (Alger-theme antipattern) | 1 line |
| 4 | YELLOW | MCR `%` violations at 11824, 13019 → drop trailing `%` | 2 lines |
| 5 | YELLOW | Mini sparklines at 7892 → add `hoverlabel:HOVERLABEL_THEME` to spec | 1 line |
| 6 | YELLOW | Country choropleth richHover at 7031-7039 → drop `━━━━` dividers | 2 lines |
| 7 | YELLOW | Promote 5 long native titles (L810, 814, 818, 8221, 8254) to `data-tip` | 5 elements + add `tip-wrap` class to CSS+JS |
| 8 | YELLOW | cardBetaHist hover redundancy (L8651-8667) — drop name from hovertemplate where already in legend | 3 lines |
| 9 | YELLOW | Factor history overlay redundancy (L8956, 8974, 8991, 8999, 9007) — drop name from hovertemplate | 5 lines |
| 10 | YELLOW post-launch | Convert `HOVERLABEL_THEME` const to a function called from `buildPlotBg()` so theme changes refresh all hover labels | ~30 min refactor |

**Backlog items 11-21** can ship after launch — they're cosmetic or theme-corner-case.

---

## Concrete edit-ready diffs (top 6 fixes)

### Fix 1 — Tip portal CSS

**File:** `dashboard_v7.html`
**Line:** 453

```diff
- #tip-portal{position:fixed;background:#0f1623;color:var(--txth);padding:10px 14px;border-radius:8px;font-size:11px;font-weight:400;line-height:1.55;white-space:normal;min-width:180px;max-width:340px;word-break:normal;overflow-wrap:break-word;hyphens:auto;opacity:0;pointer-events:none;transition:opacity .15s;z-index:10000;border:1px solid var(--grid);text-transform:none;letter-spacing:0.1px;box-shadow:0 8px 24px rgba(0,0,0,.45);font-family:'DM Sans',system-ui,sans-serif;text-align:left;display:none}
+ #tip-portal{position:fixed;background:#0f1623;color:#f1f5f9;padding:10px 14px;border-radius:8px;font-size:11px;font-weight:400;line-height:1.55;white-space:normal;min-width:180px;max-width:340px;word-break:normal;overflow-wrap:break-word;hyphens:auto;opacity:0;pointer-events:none;transition:opacity .15s;z-index:10000;border:1px solid #475569;text-transform:none;letter-spacing:0.1px;box-shadow:0 8px 24px rgba(0,0,0,.45);font-family:'DM Sans',system-ui,sans-serif;text-align:left;display:none}
```

Two changes: `color:var(--txth)` → `color:#f1f5f9` AND `border:1px solid var(--grid)` → `border:1px solid #475569` (so the border is also legible on the dark popup regardless of theme).

### Fix 2 — Plotly hoverlabel #1 (rRegRiskHeatmap)

**File:** `dashboard_v7.html`
**Line:** 6395

```diff
- hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:T.grid,font:{color:T.txth,family:'DM Sans, system-ui',size:11}},
+ hoverlabel:HOVERLABEL_THEME,
```

### Fix 3 — Plotly hoverlabel #2 (country choropleth)

**File:** `dashboard_v7.html`
**Line:** 7053

```diff
- hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:T.grid,font:{color:T.txth,family:'DM Sans, system-ui',size:11},align:'left'}
+ hoverlabel:HOVERLABEL_THEME
```

### Fix 4 — Plotly hoverlabel #3 (rCountryRiskHeatmap)

**File:** `dashboard_v7.html`
**Line:** 7272

```diff
- hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:T.grid,font:{color:T.txth,family:'DM Sans, system-ui',size:11}},
+ hoverlabel:HOVERLABEL_THEME,
```

### Fix 5 — Treemap white-text antipattern

**File:** `dashboard_v7.html`
**Line:** 7626

```diff
- textfont:{size:11,color:'#ffffff',family:'DM Sans, system-ui'},
+ textfont:{size:11,color:T.tickH,family:'DM Sans, system-ui'},
```

### Fix 6 — MCR percent violations

**File:** `dashboard_v7.html`
**Line:** 11824

```diff
- hovertemplate:'%{x|%b %d %Y}<br>Idio MCR: %{y:.2f}%<extra></extra>'}
+ hovertemplate:'%{x|%b %d %Y}<br>Idio MCR: %{y:.2f}<extra></extra>'}
```

**Line:** 13019

```diff
- hovertemplate:'<b>%{text}</b> (%{customdata[0]})<br>MCR: %{x:.3f}%<br>TE Contrib: %{y:.1f}%<br>Port: %{customdata[4]:.2f}%<extra></extra>'
+ hovertemplate:'<b>%{text}</b> (%{customdata[0]})<br>MCR: %{x:.3f}<br>TE Contrib: %{y:.1f}%<br>Port: %{customdata[4]:.2f}%<extra></extra>'
```

---

## Verification plan after applying fixes

1. **Smoke test:** `./smoke_test.sh --quick` (~1.5s)
2. **Theme toggle in browser:** open dashboard, ⚙ → Alger.
3. **Hover every chart:** 
   - Region × Factor heatmap (Regions tab) — text should be light-on-dark, readable
   - Country choropleth (Countries tab) — same
   - Country × Factor heatmap (Countries tab) — same
   - Holdings Treemap labels — should not disappear into white background
4. **Hover every cell with a dotted underline / `data-tip`** — should render with light text on dark popup, readable on both themes
5. **MCR cells on cardHoldRisk + on the strategy-compare modal** — verify no trailing `%`
6. **Toggle back to Dark theme** — verify nothing regressed there

---

## Notes for parent agent

- All fixes are read-only verified — no Edit/Write applied to `dashboard_v7.html` per the `subagents_no_edit` rule.
- The 6 top fixes total **~10 changed lines** — small, low-risk, single-commit eligible.
- The fix for finding 10 (`HOVERLABEL_THEME` to function) is a more invasive refactor; do post-launch.
- I did not propose changes to the data-tip strings themselves beyond format issues — the content is generally well-tuned. The user's "repeating info" complaint is mostly about Plotly hover (legend + hover) duplication, captured in §1.5.
- If you ship just fixes 1-4 (the 4 RED items), the user's "invisible font" complaint goes away on Alger, and the perception of "broken hover" disappears. Those 4 are the highest leverage.
