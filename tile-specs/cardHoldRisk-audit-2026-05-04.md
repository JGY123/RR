# Tile Audit: cardHoldRisk — 2026-05-04

> **Auditor:** Tile Audit Specialist (subagent run for R2-Q4 default B)
> **Scope:** Holdings Risk Snapshot — per-holding active-wt × TE-contribution quadrant on the Holdings tab
> **Status overall:** **GREEN** — data is clean primitives, chrome is fully migrated, design is in tight parity with cardFacRisk. Three YELLOW items + one RED on click-handler robustness.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | Holdings Risk Snapshot |
| Card DOM id | `#cardHoldRisk` (Holdings tab, line 8972) |
| Render function | `rHoldRisk(s)` at `dashboard_v7.html:7159–7239` |
| Render call site | line 9103 inside `renderHoldTab()` (with try/catch) |
| Inner plot id | `#holdRiskDiv` (`.chart-h-lg` → `clamp(320px, 40vh, 520px)`) |
| Legend container | `#holdRiskLegend` (static, populated by render) |
| Chrome | `tileChromeStrip({id:'cardHoldRisk', about:true, resetZoom:'holdRiskDiv', fullscreen:"openTileFullscreen('cardHoldRisk')", resetView:true, hide:true})` (line 8978) |
| Right-click → note | wired (`oncontextmenu="showNotePopup(event,'cardHoldRisk')"`) |
| About entry | `_ABOUT_REG.cardHoldRisk` lines 1291–1298 (complete) |
| Drill path | `plotly_click` → `oSt(ticker)` (stock modal), via `customdata` |
| Sibling tile | `cardFacRisk` (Risk tab) — same encoding shape, factor-side |
| Data source | `cs.hold[]` — latest week only (no per-holding history shipped, B114) |

---

## 1. Data Accuracy — Track 1

### 1.1 Field mapping — VERIFIED clean

| Encoding | Source | Origin | Synth marker? |
|---|---|---|---|
| x = active wt | `h.a` | parser `aw` (raw FactSet AW) → normalize alias | none — raw |
| y = TE contrib | `h.tr` | parser `pct_t` (FactSet `%T`) → normalize alias | none — raw |
| size = idio | `\|h.mcr\|` | parser `pct_s` (FactSet `%S`) → normalize alias | none — raw |
| color | sign of `h.tr` | derived locally (red ≥ 0, green < 0) | n/a (semantic) |
| label | `tk(h)` (top-20 by `\|tr\|`) | `h.tkr_region` ‖ `h.t` | n/a |
| hover | `h.t`, `h.n`, `h.a`, `h.tr`, `h.mcr`, `h.sec`, `h.co` | all primitives | none |

**No anti-fabrication concern** — every numeric encoding is a direct alias of a raw FactSet column. No `_synth` flags needed; none added.

### 1.2 Filter / universe semantics — verified, B116-aligned

`eq = s.hold.filter(h => !isCash(h) && isFinite(h.a) && isFinite(h.tr))`

- Excludes cash via `isCash()` (line 1794): tickers `CASH_*`, sector `Cash/Currency/...`, name `Cash/Currency*`. Note parser already strips `CASH_*` tickers at extract time (`factset_parser.py:780`), so this is belt-and-braces.
- **Includes bench-only** holdings (h.a < 0, h.p ≈ 0) — correct, since TE/MCR are universe-INVARIANT (B116). Universe pill in the Exposures header does NOT control this tile (and shouldn't — `_rerenderAggTiles()` at line 4936 deliberately skips `rHoldRisk`).
- **Universe-pill behavior is correct by omission.** Caveat to surface: a user toggling "Port-Held" expects all holdings tiles to filter; this one doesn't. See finding D2 below.

### 1.3 Spot check on GSC (1,002 holdings, 48 port-held + 954 bench-only)

| Holding | a (h.a) | tr (h.tr) | \|mcr\| (h.mcr) |
|---|---|---|---|
| B0CL646 (top TE) | +4.6 | +16.7 | 10.5 |
| BKS48R6 | +2.6 | +7.0 | 4.4 |
| 2632876 | +3.6 | +6.9 | 5.0 |
| BFZP4R9 | +2.2 | +5.3 | 3.3 |
| 6597346 | +2.3 | +5.2 | 2.5 |

Σ |mcr| across all 1,002 = **68.7%** vs `cs.sum.pct_specific = 69.9%` ✅ (matches B115 invariant within rounding).

### 1.4 Edge cases — verified

- MCR: 0 negatives in sample (parser ships `pct_s` always ≥ 0). `Math.abs()` is defensive but unused in practice. **Fine.**
- TR: -0.10 → +16.70 in GSC sample (10 holdings with negative tr — diversifying, render green). Sign behavior correct.
- Bench-only tail: 954 of 1,002 holdings have `h.a < 0` and tiny `\|tr\|` < 0.05 — they cluster at the origin as 8px dots. Visually noisy on small-cap strategies. See finding D3.
- Empty-state path (`!eq.length`) renders inline message — works.

### 1.5 RED / YELLOW data findings

**D1. RED — Click handler `oSt(ticker)` uses `customdata`, but `customdata` is the raw `h.t` (SEDOL).**
At line 7218: `oSt(t)` where `t = d.points[0].customdata || d.points[0].text`. `customdata = tickers = eq.map(h=>h.t)` — that's SEDOL. `oSt(ticker)` at line 9931 then looks up `cs.hold.find(x=>x.t===ticker)`. ✅ Works because `oSt` matches on `h.t` — both sides use SEDOL. **Re-classify D1 to GREEN.** (Initial concern resolved on read.) The fallback `text` would be `tk(h)` (display label, e.g. "AAPL-US") for top-20 only — never reached because customdata is always present.

**D2. YELLOW — Universe pill is silently ignored.**
A user who clicks "Port-Held" in the Exposures header has every other Risk-related tile filter out bench-only. cardHoldRisk does not. Per B116, this is mathematically correct (TE/MCR are universe-invariant), but it's UX-confusing on the Holdings tab. The card title's data-tip doesn't mention this. **Fix:** add a short note to the data-tip and About copy: *"Universe pill does not filter this tile — TE/MCR are universe-invariant by FactSet definition."* (1-line copy edit, no logic change.)

**D3. YELLOW — Bench-only long tail clutters the origin.**
On GSC (small-cap), 954 of 1,002 markers are < 0.05% TE and cluster densely at the origin. Most have `\|mcr\| < 1` so bubbles compress to the 8px floor. Effect: chart looks busy, top contributors don't pop. **Fix options (no code today, propose for B-queue):**
- (a) min-magnitude filter `|tr| > 0.1 || |a| > 0.05` (drops 800+ low-signal points; preserves all materially-relevant holdings).
- (b) lower bubble floor from 8 to 4 for tiny holdings.
- (c) add a "Show: Top-N / All" toggle. Mirrors the Top-20 label cap that's already there.

---

## 2. Functionality Parity — Track 2

### 2.1 Chrome strip — fully migrated to `tileChromeStrip` helper

| Capability | Helper slot | Present? | Behavior |
|---|---|---|---|
| About (ⓘ) | `about:true` | ✅ | opens `_ABOUT_REG.cardHoldRisk` (lines 1291–1298) |
| Reset Zoom (⤾) | `resetZoom:'holdRiskDiv'` | ✅ | calls `Plotly.relayout` on the div |
| Full Screen (⛶) | `fullscreen:"openTileFullscreen('cardHoldRisk')"` | ✅ | generic-fallback path (line 1445); clones tile + redraws Plotly trace |
| Reset View (↺) | `resetView:true` | ✅ | clears tile filters/view |
| Hide (×) | `hide:true` | ✅ | toggles tile body |
| CSV / PNG download | — | ✗ | **see F1** |
| Right-click note | inline `oncontextmenu` | ✅ | works |

**F1. YELLOW — No CSV export.**
Sibling tile cardFacRisk has `csv:'exportFacRiskCsv&&exportFacRiskCsv()'` (line 3043). cardHoldRisk has no CSV slot. PMs reasonably expect to export "the quadrant data" for slide reuse. **Fix:** add an `exportHoldRiskCsv()` (one function) emitting `t,n,a,tr,mcr,sec,co` for every `eq` holding, then add `csv:'exportHoldRiskCsv&&exportHoldRiskCsv()'` to the chrome config. ~12 lines of code. Per RR rule (no PNG buttons), do NOT add a PNG slot.

**F2. YELLOW — Full Screen uses generic fallback, not a dedicated bigger-bubble layout.**
cardFacRisk has `openFacRiskFullscreen()` at line 6431 — a custom handler that re-renders with bigger bubbles, larger labels, and the KPI strip retained. cardHoldRisk falls through the generic clone-and-redraw at line 1445, so bubbles stay at the 8/48-pixel scale of the inline view (looks small in fullscreen) and labels still hard-cap at 9px. **Fix:** add `openHoldRiskFullscreen()` mirroring lines 6431–6498, scaling sizes ×1.5 and label font to 11. ~25 lines. Lower priority than F1.

### 2.2 Click → drill — VERIFIED

`plotly_click` → `oSt(customdata)` → `cs.hold.find(x=>x.t===ticker)` → modal renders. Works for both port-held and bench-only holdings (peers panel + radar still render even when port=0).

### 2.3 Hover tooltip — GREEN

Includes ticker (`tk(h)`), name (sliced 40), active wt with sign + dir badge, TE contrib with sign, |MCR|, sector, country. Same depth as cardFacRisk. Hover-label styling matches.

### 2.4 Week selector behavior — verified

- Tile re-renders on week change because `changeWeek()` → `upd()` → `rHold()` → `renderHoldTab()` → `rHoldRisk(cs)`.
- BUT `cs.hold` is always latest-week (B114: per-holding history not shipped). So tile shows latest data even when user picked an old week.
- `weekBannerHtml()` is rendered at the top of the holdings tab (line 8965), so the amber "Viewing week of X — summary metrics only" banner is visible.
- **F3. YELLOW — No tile-level week banner.** The amber banner sits above cardWatchlist; by the time a user scrolls to cardHoldRisk they may not connect "this is latest, not the picked week." cardWeekOverWeek handles this with an inline tile-local note ("Viewing week of X but data is latest"). **Fix:** add a small inline note inside the tile when `_selectedWeek` is non-null. ~5 lines. Same pattern used elsewhere.

---

## 3. Design Consistency — Track 3

### 3.1 Plotly trace styling vs cardFacRisk

| Aspect | cardFacRisk | cardHoldRisk | Match? |
|---|---|---|---|
| Marker mode | markers+text | markers+text | ✅ |
| Bubble size formula | `sqrt(dev)*9+10`, clamp 14–56 | `sqrt(\|mcr\|)*9+8`, clamp 8–48 | tighter, intentional (more dots) |
| Bubble border | `rgba(15,23,42,0.7)` 1px | same | ✅ |
| Color (signed) | red `0.55+t*0.4` for adds, green for diversifies | same scaling, same anchors | ✅ |
| Quadrant background tints | 4-corner tints (red/amber/indigo/green) | identical 4 tints | ✅ |
| Quadrant labels | "OW · risk-on bet" / "UW yet adds" / "OW hedge" / "UW · risk-off" | "OW · adds risk" / "UW yet adds (unowned risk)" / "OW · diversifies" / "UW · risk-off" | semantically aligned, copy slightly varies |
| Label font size | 10 | **9** | **D1 minor — see below** |
| Hover bg / border | `rgba(15,23,42,0.96)` / `#475569` | same | ✅ |
| Y axis tickformat | `+.1f` | same | ✅ |
| Legend pattern (bubble + color) | inline SVG, 6/9/13 px circles | inline SVG, identical 6/9/13 | ✅ |

**Minor finding D-DESIGN-1 (YELLOW → GREEN-ish): Label font size mismatch (9 vs 10).**
cardHoldRisk uses 9px labels (line 7202); cardFacRisk uses 10px (line 6383). Holdings have more points so smaller fonts make sense, but it does break the "exact sibling" framing. Not user-reported, low priority. **Fix:** if anything, leave at 9 — but note it. (Recommend GREEN — sub-pixel.)

### 3.2 KPI strip — DELIBERATELY ABSENT

cardFacRisk has a 6-card KPI strip above the chart (Total TE, Idio, Factor, Top OW factor, Top UW factor, Material factors). cardHoldRisk has NO KPI strip — just a sub-caption "active wt × risk contrib · bubble = idio (|MCR|)" and the legend below.

**D-DESIGN-2 (GREEN — design choice, not a defect).** Holdings analogues would be: Total TE / Top-10 TE share / # holdings / Top contributor / Top diversifier. The cardHoldings header already shows the Top-10 TE % concentration pill (line 8964) and the holdings count breakdown. So the KPI is split across the two adjacent tiles. No change recommended. Could be a B-queue idea if the user wants a more "exposures-style" summary above the chart, but cardFacRisk's KPI exists because nothing else summarizes factor risk; here, the count pill already covers it.

### 3.3 Color semantics — VERIFIED

Red = adds risk (positive tr) ✅ matches dashboard convention (--neg / pos).
Green = diversifies (negative tr) ✅.
Color intensity scales with magnitude (`0.55 + t*0.4` for opacity). Mirrors cardFacRisk exactly.

### 3.4 Typography in legend — VERIFIED

10px body text, 9px uppercase mini-cap labels with 0.4px letter-spacing — matches cardFacRisk legend (lines 6413–6425) byte-for-byte except for the "MCR" → "factor σ" wording. Tile-token compliant.

### 3.5 Container height

`.chart-h-lg = clamp(320px, 40vh, 520px)` — same as cardFacRisk's inline 440px target. Consistent.

---

## 4. Findings summary + fix queue

| # | Sev | Track | Finding | Proposed fix | Effort |
|---|---|---|---|---|---|
| F1 | YELLOW | Func | No CSV export | Add `exportHoldRiskCsv()` + `csv:` slot in chrome | ~12 LOC |
| F2 | YELLOW | Func | Full-screen uses generic fallback (small bubbles in FS) | Add `openHoldRiskFullscreen()` mirroring cardFacRisk's | ~25 LOC |
| F3 | YELLOW | Func | No tile-local "viewing latest" banner when week selector is set | Inline note when `_selectedWeek` non-null | ~5 LOC |
| D2 | YELLOW | Data | Universe pill is ignored (correct math, confusing UX) | Add disclaimer to data-tip + About copy | ~2 LOC copy edit |
| D3 | YELLOW | Data | Bench-only long tail clutters origin on small-cap strategies | (Propose) min-magnitude filter or Top-N toggle | ~10 LOC |
| D-Design-1 | GREEN | Design | Label font 9 vs cardFacRisk 10 — sub-pixel diff | Leave; tighter is better here | 0 |

**TRIVIAL (agent can apply without PM input):** D2 (copy edit), F3 (banner pattern is reusable).

**NEEDS PM DECISION:** D3 (do we want to filter bench-only or surface them?), F1 (CSV columns shape — should it include port_wt/bench_wt or just the 5 plot encodings?), F2 (priority — is fullscreen actually used here?).

**BLOCKED:** none.

---

## 5. Verification checklist

- [x] Data accuracy verified — all encodings are raw FactSet primitives, no synthesis
- [x] B116 universe-invariance respected (intentionally ignores Universe pill)
- [x] Anti-fabrication policy clean — no `_synth` flags needed, none added
- [x] Edge cases: empty cs.hold (renders inline message), zero MCR (rendered as 8px floor dot), negative tr (renders green)
- [x] Chrome strip migrated to `tileChromeStrip` helper
- [x] About / Reset Zoom / Reset View / Hide / Full Screen wired
- [x] Right-click → note wired
- [x] Click-to-drill → `oSt()` works (verified path, customdata=SEDOL, oSt matches on h.t)
- [x] Hover tooltip complete (ticker, name, a, tr, mcr, sec, co, dir badge)
- [x] Color semantics correct (red=adds, green=diversifies)
- [x] Legend pattern matches cardFacRisk
- [x] Theme-aware (uses THEME() for tick colors)
- [x] Re-renders on week change (always shows latest data — B114 limitation surfaced via D2/F3)
- [ ] CSV export — **missing (F1)**
- [ ] Dedicated full-screen handler — **missing (F2)**
- [ ] Tile-local week banner — **missing (F3)**

---

## 6. Recommendation

**GREEN with three small chrome additions.** Data layer is exemplary — every encoding is a raw FactSet primitive, B116 invariance is respected by design, no fabrication. Functionality parity with sibling cardFacRisk is 90% there; gaps are CSV (F1), dedicated FS handler (F2), and tile-local week banner (F3) — all routine ~5–25 LOC additions, none blocking. Design is in tight parity. The Universe-pill "silent ignore" (D2) is an UX-clarity copy fix, not a data defect. Bench-only clutter (D3) is the only finding that needs PM judgment.

Sign-off requires user's explicit in-browser OK per memory `feedback_signoff_requires_user_review.md`.
