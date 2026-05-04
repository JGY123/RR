# cardTreemap — Tile Audit (2026-05-04)

**Auditor:** tile-audit subagent
**Method:** three-track audit per `tile-audit-framework.md` — data accuracy / functionality parity / design consistency
**Scope:** audit + propose only — no edits to `dashboard_v7.html`
**Render entry:** `rTree(s)` at `dashboard_v7.html:7316`
**Card shell:** `<div id="cardTreemap">` at `dashboard_v7.html:3234`
**Note:** A prior audit exists at `tile-specs/cardTreemap-audit-2026-04-21.md`. The instruction prompt said "no prior audit on file." That is incorrect — prior audit identified B20–B28 + D1. This audit is a fresh independent pass; verified state of each prior B-item is annotated where relevant. Several have shipped (fullscreen, note popup, `_treeDrill` reset, `h.subg` parser-shipped). The remaining findings are independently re-derived below.

---

## Triage queue (top of doc)

### TRIVIAL (≤5 lines, no PM judgment, agent-applicable)

| # | Title | LoC | Lines |
|---|---|---|---|
| T1 | Hardcoded `#10b981` / `#ef4444` → `THEME().pos` / `THEME().neg` (Active mode bucket + drilled-holding colors) | 4 | 7339–7340 (already declared via `getComputedStyle`), 7343, 7358 |
| T2 | About-registry `cardTreemap.how` text contradicts shipped UI — wrong dims (`region/industry`), wrong sizes (`port wt/bench wt/|TE|/|MCR|`), wrong colors (`TE contrib` not present) | 1 | 1192 |
| T3 | Toolbar pill-button font 9px (line 3238–3242) — every other pill bar uses 10–11px; remove inline overrides; use `.toggle-btn` | 3 | 3238, 3240, 3242 |
| T4 | Add hairline footer with bucket-count + Σ size + F18 caveat when `_treeSize==='te'` (per ARCHITECTURE.md §5.3 "honest math, never rescale") | ~6 | new block after Plotly call |
| T5 | Empty-state — when bucket dict is empty (e.g., `_treeDim='grp'` on a strategy with no `subg`-tagged holdings), text reads "No holdings to visualize" but `s.hold.length>0`. Bucket-empty ≠ holdings-empty; differentiate | 3 | guard branch in 7317 vs after 7337 |
| T6 | `customdata` HTML-injection: `h.n` is interpolated raw into the tooltip (`<b>${h.n||tk(h)}</b>`, line 7360); names with `<` or `>` (rare but possible) escape the tooltip context. Wrap with `esc()` | 2 | 7360, 7369 |

### TRIVIAL-BUT-LARGER (5–30 lines, no PM judgment)

| # | Title | LoC | Notes |
|---|---|---|---|
| TL1 | Persist toolbar state to localStorage (`rr.tree.dim/size/color`) — same pattern used on cardRiskByDim, cardCountry, cardCalHeat. Per CLAUDE.md hard rule #3 (preferences-only) | ~15 | Init from localStorage at script load; persist in `setTreeDim/Size/Color` |
| TL2 | Unify rank palette — `_treeRankColor` uses 5-color literal, while the rest of dashboard uses `var(--r1..r5)` via `rc()` helper. Replace with `rc()` and resolve to hex at render | ~8 | Lines 7307–7310 → `getComputedStyle`-resolve `var(--r1..r5)` |
| TL3 | Surface `_treeColor==='active'` legend strip (red/green diverging) and `_treeColor==='rank'` legend strip (Q1→Q5) — currently no legend; user has to interpret colors from hover | ~20 | Below toolbar, swap based on `_treeColor` |
| TL4 | CSV export of bucket-level table (label, count, wt, active, te, avgRank) — chrome strip currently has no `csv:` key. Sibling tiles ship it | ~12 | New `exportTreeBuckets()`; add `csv:'exportTreeBuckets()'` to chrome strip |
| TL5 | Per-week (`_selectedWeek`) handling — currently silently shows latest week regardless of selector. Either banner ("treemap reflects latest week") or wire through `_selectedWeek`-aware accessor (no `_wHold` exists yet → larger refactor; banner is the cheap fix) | ~5 banner / ~30 wired | Banner-route is trivial; wired-route requires `_wHold(weekDate)` accessor since `cs.hold` only carries latest week |

### PM-GATE (needs product judgment)

| # | Title | Why |
|---|---|---|
| P1 | Bucket → sector/country/group drill modal (`oDr`/`oDrCountry`) instead of in-tile drill only — sibling tiles route to canonical drill modals; current treemap only offers in-tile drill into 80 holdings | UX call: shift-click? secondary "Open detail ›" button in breadcrumb? |
| P2 | Universe pill (Port-Held / In-Bench / All) — currently the treemap aggregates **everything** in `cs.hold[]` regardless of `_aggMode`. Per B116 and ARCHITECTURE §4.6, this should respect the universe pill the way cardSectors / cardCountry / cardGroups do. Or it should not, if the treemap is intentionally a different abstraction | PM call on default + whether to filter |
| P3 | F18 defensive UI for Size=TE — per-holding `h.tr` sums 94→134% across strategies (RED, escalated). When user picks Size=TE, treemap rectangles aggregate F18-contaminated values. Posture options: (a) suppress (gray out the TE pill); (b) honest math (show Σ in footer); (c) substitute section-aggregate where dim=Sector (clean L2-verified path). Cardsectors used (c); cardRiskByDim used (b) | Pick the posture; ARCHITECTURE.md §5.3 strongly prefers (b) over silent rescale |
| P4 | "Group" dimension uses `h.subg` (FactSet `SEC_SUBGROUP`), but the bucket labels (e.g., "GROWTH CYCLICAL", "STABLE") aren't user-defined; if a strategy has 80%+ in one subgroup the treemap is uninteresting. The "Rank" dimension (`Q1`–`Q5`) skews heavily to Q1 (~56% per CLAUDE.md). Both are technically correct but produce visually-degenerate treemaps on real data | PM call: keep both? Replace one with Region or Industry which are more diverse? |
| P5 | Color=Active uses **sign of bucket-sum** (`b.active>=0?posC:negC`). But `Σ h.a` per sector is approximately zero by definition (active weights sum to zero across the portfolio). When some sectors aggregate positive and some negative, the binary green/red coloring is informative; but the magnitude is lost — a sector at +0.1% looks the same as +12%. Diverging color scale (intensity by `\|active\|`) would be richer | PM call: keep binary or move to gradient? |

---

## §1 — Data accuracy (TRACK 1)

### 1.1 Field inventory — bucket level (top, `!_treeDrill`)

| # | Cell | Source path | Format | F18-impacted? | Spot-check status |
|---|---|---|---|---|---|
| 1 | Bucket label | `keyFn(h)` = `h.sec` (Sector) / `h.co` (Country) / `h.subg` (Group) / `'Q'+Math.round(h.over)` (Rank) | string | no | source: parser; `h.sec/h.co/h.subg/h.over` all sourced from FactSet Security section. **🟢 sourced.** |
| 2 | Rectangle size — `wt` mode | `b.wt = Σ h.p` per bucket (line 7333) | `+val.toFixed(2)` | no | **🟢 sourced** (`h.p` ← FactSet `W` column). Σ over all sectors ≈ 100% minus cash. |
| 3 | Rectangle size — `te` mode | `b.te = Σ \|h.tr\|` per bucket (line 7334) | `+val.toFixed(2)` | **YES — F18** | **🔴 contaminated.** `h.tr` = FactSet `%T` per-holding. Per F18 (FACTSET_FEEDBACK.md L173–207), Σ `h.pct_t` across the portfolio = 94.6% (EM) → 134.4% (IOP). Bucket-level sums inherit this skew; relative bucket sizes within a single tile are still informative, but absolute values are wrong by up to ±35%. |
| 4 | Rectangle size — `cnt` mode | `b.count = N holdings` per bucket | integer | no | **🟢 sourced.** |
| 5 | Bucket color — `active` mode | sign of `Σ h.a` (line 7343) | `posC`/`negC` from CSS vars (good) | no | **🟢 sourced.** Note: Σh.a ≈ 0 across all buckets by construction; binary-sign coloring is correct but loses magnitude. |
| 6 | Bucket color — `rank` mode | `b.rankSum/b.rankN` weighted-avg `h.over` → `_treeRankColor(q)` 5-step palette (line 7342) | hardcoded hex literals 7308–7309 | no | **🟢 sourced** but **🟡 derived weighting**. Weight is `h.p>0?h.p:1` — bench-only holdings (`h.p==0`) get weight 1, mixing weighted and unweighted in same bucket. Minor; current data has no shorts so the only effect is bench-only rows getting weight 1. Same finding as April 21 audit §1.3 — still applicable. |
| 7 | Hover: Holdings (count) | `b.count` | integer | no | **🟢 sourced.** |
| 8 | Hover: Weight | `b.wt = Σ h.p` | `f2(v,1)%` | no | **🟢 sourced.** |
| 9 | Hover: Active | `b.active = Σ h.a` | `fp(v,1)` | no | **🟢 sourced.** |
| 10 | Hover: TE | `b.te = Σ \|h.tr\|` | `f2(v,1)%` | **YES — F18** | **🔴 contaminated.** Same as size=te. Always shown in tooltip even when size mode is `wt` or `cnt`. |
| 11 | Hover: Avg Rank | weighted avg `h.over` | `toFixed(1)` | no | 🟢 sourced + 🟡 derived (weighted-avg with the `h.p>0?h.p:1` quirk above). |

### 1.2 Field inventory — drilled-into level (`_treeDrill && buckets[_treeDrill]`)

| # | Cell | Source path | Format | F18-impacted? | Status |
|---|---|---|---|---|---|
| 1 | Tile label | `h.t` (ticker; via `tk(h)` indirectly through hover) | string | no | **🟢 sourced.** |
| 2 | Tile size — `wt` | `h.p` | `+val.toFixed(4)` | no | **🟢 sourced.** |
| 3 | Tile size — `te` | `Math.abs(h.tr\|\|0)` | `+val.toFixed(4)` | **YES — F18** | **🔴 contaminated.** Per-holding %T, the exact field flagged by F18. |
| 4 | Tile size — `cnt` | `1` | int | no | **🟢 sourced.** When all rectangles are the same size, the visual collapses to a uniform grid — Plotly may render labels poorly. UX issue, not data. |
| 5 | Tile color — `active` | `(h.a\|\|0)>=0?'#10b981':'#ef4444'` | hardcoded hex (line 7358) | no | **🟢 sourced** but **theme drift** — different from line 7339–7340 where the bucket-level path correctly resolves CSS vars via `getComputedStyle`. Drilled-holding path uses raw hex. Inconsistent with line 7343. |
| 6 | Tile color — `rank` | `_treeRankColor(h.over)` | 5-color literal palette | no | **🟢 sourced** but palette drift (see B26 / TL2). |
| 7 | Hover: Weight | `h.p` | `f2(v,2)%` | no | **🟢 sourced.** |
| 8 | Hover: Active | `h.a` | `fp(v,2)` | no | **🟢 sourced.** |
| 9 | Hover: TE | `Math.abs(h.tr\|\|0)` | `f2(v,2)%` | **YES — F18** | **🔴 contaminated.** |
| 10 | Hover: Rank | `h.over!=null?'Q'+Math.round(h.over):'—'` | string | no | 🟢 sourced + 🟡 derived (`Math.round` truncation). |

### 1.3 F18 contamination — dedicated finding

**Finding D1.1 — F18 contamination on Size=TE and TE-tooltip line (HIGH/RED):**

`h.tr` is sourced from FactSet `%T` (parser line 668: `"tr": g("PCT_T")`). F18 (`FACTSET_FEEDBACK.md` L173–207) shows Σ `h.pct_t` per strategy ranges from 94.6% (EM) to 134.4% (IOP) — ±35% deviation from the documented "~100%" invariant. Status: OPEN, escalated to FactSet, automated monitor flagging RED on IDM/IOP/ACWI/ISC.

**The treemap is on the F18 side**, not the L2-verified side:
- Section-aggregate `cs.sectors[].tr` (L2-verified clean ≈100% on 3,082/3,082 sector-weeks) is **not used** by the treemap. The treemap re-aggregates from `cs.hold[]` per-holding `%T`.
- Σ over all bucket `b.te` for `_treeDim='sec'` and `_treeSize='te'` will reproduce the F18 deviation (~94–134% per strategy).
- Even when `_treeSize='wt'`, the **TE row in the hover tooltip** is contaminated.

**Why it matters:**
- A PM glancing at the treemap with Size=TE may compare bucket sizes to known totals and see ~134% on IOP — looks like a bug.
- More dangerously, two adjacent strategies viewed side-by-side might suggest IOP has 1.4× more aggregate TE than EM when in fact the deviation is the F18 measurement artifact.
- Per ARCHITECTURE.md §5.3 — the **wrong** posture is to silently rescale to 100%; the **right** posture is honest-math + caveat, suppress, or mark-derived.

**Fix posture (P3 in PM-gate queue):**
- Option A — *suppress*: gray out / disable the TE size pill until F18 resolves. Cheap; loses functionality.
- Option B — *honest math*: render footer `Σ \|TE\| = 134.4% (per-holding %T sum, expected ~100% — see F18)`. Transparent; preserves functionality. Same pattern shipped on cardRiskByDim.
- Option C — *substitute on Sector dim*: when `_treeDim==='sec'`, read `cs.sectors[].tr` (L2-verified) instead of summing `h.tr`. Different code paths for Sector vs Country/Group/Rank — ugly but accurate. Same pattern shipped on cardSectors.

Strong recommendation: **Option B**. Matches the precedent on cardRiskByDim and aligns with the "doing it right" framing in STRATEGIC_REVIEW.md. The treemap is a high-signal visual; suppressing TE entirely would over-correct.

### 1.4 Spot-checks possible without loading JSON

| Check | Expected | Method |
|---|---|---|
| Σ bucket `wt` (Sector × Weight) | ≈ 100% − cash | Sum `b.wt` across all entries; should equal `Σ h.p` for non-cash |
| Σ bucket `active` | ≈ 0 | Active weights sum to zero across the portfolio |
| Σ bucket `te` per strategy | 94–134% (matches F18 table) | Cross-check against `verify_section_aggregates.py --strict` output |
| Rank-mode color on Q1-heavy sector | Green (#10b981) | Spot a known Q1-heavy sector in cs.hold; weighted avg `h.over` should be near 1.5; `_treeRankColor(1.5)` → `Math.round(1.5)=2` → `#34d399` light green. Off-by-one note in §1.5 |
| `_treeDim='grp'` on a strategy with `subg` populated (post-D1 fix) | Renders 4–10 subgroup buckets | `factset_parser.py:745` ships `subg`; verify >0 holdings have `h.subg` non-null |

### 1.5 Rounding boundary on Rank dimension

`_treeRankColor(q)` uses `Math.round(q)` to map continuous quintile scores to 5 buckets. **Math.round(1.5) → 2** (banker's-rounding-aware: but JavaScript's Math.round always rounds halves up). So `q=1.5` is colored as Q2 (`#34d399` light green), not Q1 (`#10b981` deep green). For PMs interpreting "is this sector mostly Q1?" the boundary at 1.5 is arbitrary. Same boundary issue exists in cardSectors `rc()` helper — consistent, but worth noting that "Q1+" (1.0–1.49) and "Q1–" (1.5–2.0) are visually identical.

Minor — not a blocker. Documenting for posterity.

### 1.6 Per-week / `_selectedWeek` handling — silent latest

`rTree(s)` reads `s.hold` directly (line 7326). When the user selects a historical week via the header arrows, `cs.hold` does **not** change (per ARCHITECTURE.md §3.4 — `cs.hold[]` is detail-layer, latest week only). Yet the treemap continues to render without indicating the user is now seeing latest-week holdings while the rest of the dashboard reflects the selected week.

Same issue exists on cardSectors / cardHoldings / cardMCR per AUDIT_LEARNINGS.md — known pattern, accepted. The fix queue (TL5) is to either:
- Banner-route: render an amber "treemap reflects latest week" strip when `_selectedWeek` is set.
- Wired-route: build a `_wHold(weekDate)` accessor — but this requires the parser to emit per-week holdings snapshots in `hist.hold`, which is the B114 backlog item. Not feasible in this audit cycle.

Recommend: **banner-route as TL5** (5-line trivial). Wired-route deferred to B114.

**Section 1 rating: YELLOW → bordering RED on F18 path.** The Sector / Country / Group / Rank label paths are 🟢 sourced. Sizes are 🟢 sourced (Weight, Count) or 🔴 F18-contaminated (TE). Colors are 🟢 sourced. The hover-tooltip TE line is contaminated regardless of which size pill is active — every user sees an F18 number on every hover. Fix posture P3 is required to land GREEN.

---

## §2 — Functionality parity (TRACK 2)

Benchmark tiles: cardSectors (table gold-standard), cardCountry (chart + table gold-standard), cardGroups (treemap-with-toolbar precedent at line 7061+), cardRiskByDim (similar dim-toggle pattern with universe-aware footer).

### 2.1 `tileChromeStrip` usage

| Capability | Shipped? | Lines | Notes |
|---|---|---|---|
| `about: true` | yes | 3235 | About-registry entry at L1189 — but content **wrong** (see T2). |
| `csv: ...` | **no** | — | Sibling cardSectors / cardCountry ship CSV exports of underlying data. Treemap should expose `exportTreeBuckets()` (TL4). |
| `fullscreen: ...` | yes | 3235 | `openTileFullscreen('cardTreemap')` — **shipped post-April-21.** Need to verify FS view preserves Dim/Size/Color state and drill — quick browser check. |
| `resetView: true` | yes | 3235 | Resets toolbar state (verify in browser). |
| `hide: true` | yes | 3235 | OK. |
| Note popup right-click | yes | 3235 | `oncontextmenu="showNotePopup(event,'cardTreemap')"` — **shipped post-April-21.** |
| Card-title `data-tip` | yes | 3235 | Present (good). |

### 2.2 Drill behavior

| Behavior | Shipped? | Notes |
|---|---|---|
| Click bucket → in-tile drill (children = top-80 holdings) | yes | line 7400 (`treeDrillInto(label)`); cap at 80 holdings (line 7354). |
| Click drilled-tile → `oSt(ticker)` stock detail | yes | line 7395–7396. |
| Click bucket → canonical sector/country drill modal (`oDr(...)` / `oDrCountry(...)`) | **no** | **GAP** — siblings (cardSectors / cardCountry) route their click directly to the canonical drill. cardTreemap has its own in-tile drill but no path to the gold-standard modal. P1 in PM-gate. |
| Breadcrumb during drill | yes | line 7407. Useful UX; pattern unique to this tile. |
| `_treeDrill` reset on strategy switch | yes | line 2202 (**shipped post-April-21**). |
| `_treeDrill` reset on dim switch | yes | line 7302 (`setTreeDim` clears it). |

### 2.3 Per-week handling (`_selectedWeek`)

See §1.6. Silent latest. Banner recommended (TL5).

### 2.4 Universe pill (Port-Held / In-Bench / All)

Per ARCHITECTURE.md §4.6 and B116 invariance:
- Port-Held / In-Bench / All affects which holdings appear in tables (cardHoldings, cardSectors, cardCountry, cardGroups, cardWatchlist).
- Universe-invariant columns are TE / MCR / factor_contr / Beta from the risk model.

**Current state in cardTreemap:**
- Line 7326: `s.hold.forEach(h=>{ ... })` — reads ALL holdings unconditionally.
- No `inUniverse(h)` check, no `_aggMode` check, no `aggregateHoldingsBy(...,{mode:_aggMode})` call.

**Verdict:** the treemap **does not** respect the universe pill. Whether it should is a P2 question:
- **Argument for**: every other holdings-aggregate tile honors the pill. Inconsistency = surprise.
- **Argument against**: the treemap is a holistic-overview tile; restricting to Port-Held would hide bench-only positions which are interesting for an active manager.

PM should pick. If the answer is "should respect the pill", the fix is ~5 lines wrapping the forEach in an `inUniverse(h)`-style filter. If the answer is "intentionally all-universe", the fix is a one-line tooltip on the card-title explaining "treemap includes all holdings (port + bench-only) regardless of universe pill."

Recommend documenting the choice. Today, the behavior is undocumented.

### 2.5 Functionality matrix summary

| Capability | cardSectors | cardCountry | cardGroups | cardTreemap | Gap? |
|---|---|---|---|---|---|
| About popup | ✓ | ✓ | ✓ | ✓ | OK (but content wrong — T2) |
| CSV export | ✓ | ✓ | ✓ | **—** | TL4 |
| PNG export | (per CLAUDE memory: never ship PNG buttons) | — | — | — | OK |
| Fullscreen | ✓ | ✓ | ✓ | ✓ | OK (verify state preservation) |
| Note popup | ✓ | ✓ | ✓ | ✓ | OK |
| Universe pill awareness | ✓ | ✓ | ✓ | **—** | P2 (PM gate) |
| Week selector awareness | silent latest | silent latest | silent latest | silent latest | TL5 banner; B114 wired-route deferred |
| Click → canonical drill | ✓ `oDr` | ✓ `oDrCountry` | ✓ `oDrGroup` | in-tile drill only | P1 |
| Right-click context menu | (only via showNotePopup) | (same) | (same) | (same) | OK |
| Toolbar state persisted | various | ✓ | ✓ | **—** | TL1 |
| Reset view | ✓ | ✓ | ✓ | ✓ (via chrome strip) | OK |
| Hide | ✓ | ✓ | ✓ | ✓ | OK |
| Color legend | ✓ (sparklines) | ✓ (heatmap legend) | ✓ | **—** | TL3 |

**Section 2 rating: YELLOW.** Mostly parity-positive (5 prior B-items shipped: B20 fullscreen, B23 note popup, B28 reset, plus subg parser fix). Three remaining gaps: CSV export (TL4), toolbar persist (TL1), legend (TL3). Two PM-gate items: bucket→canonical drill (P1), universe-pill behavior (P2).

---

## §3 — Design consistency (TRACK 3)

Reference: `:root` design tokens (`--pos`, `--neg`, `--r1..r5`, `--txt`, `--txth`, `--surf`, `--card`, `--grid`), 10 canonical CSS classes, hairline footer pattern, monospace numbers.

### 3.1 Theme tokens

| Element | Token-correct? | Lines | Drift |
|---|---|---|---|
| Bucket-level pos/neg | ✓ via `getComputedStyle('--pos'/'--neg')` (lines 7339–7340) | 7339–7340, 7343 | **OK** — proper CSS-var resolve to hex (Plotly requires literal). |
| Drilled-holding pos/neg | **✗** hardcoded `'#10b981'`, `'#ef4444'` | 7358 | **T1** — should use the same `posC`/`negC` already declared at 7339–7340 (same scope). 1-line move. |
| Rank palette `_treeRankColor` | **✗** hardcoded 5-color literal | 7307–7310 | **TL2** — `var(--r1..r5)` exists in the design system. New 4th palette variant accelerates fragmentation (cardFRB has its own factor palette; cardFacButt has a factor palette; rc() has a quint palette). |
| Hover-label theme | ✓ via `HOVERLABEL_THEME` | 7386–7387 | OK |
| Plotly text color | ✗ hardcoded `'#ffffff'` (line 7383) | 7383 | Minor — labels render white on whatever bucket color. On light themes (rare on RR but exists), this would lose contrast on the lighter `#34d399` and `#fb923c` quintile colors. Borderline T-finding. |

### 3.2 Toolbar styling

Lines 3236–3243 — three pill bars (Group / Size / Color) inline-styled:

```html
<button class="toggle-btn active" data-dim="sec" onclick="setTreeDim('sec')"
  style="padding:1px 6px;font-size:9px">Sector</button>
```

| Issue | Severity | Fix |
|---|---|---|
| `font-size:9px` — every other pill bar in dashboard uses 10–11px | LOW-MED | T3 — remove inline override; use `.toggle-btn` class |
| `padding:1px 6px` — `.toggle-btn` standard is `4px 12px` | LOW | T3 — same |
| Inline styles on each of 9 buttons (4+3+2 = 9 places) — the `.toggle-btn` `.active` class still works (active state toggling at line 7312–7314) but a future CSS refactor that touches `.toggle-btn` could break the active state silently | MED | T3 — adopt class fully |

### 3.3 Card chrome and header

| Element | Status | Notes |
|---|---|---|
| `<div class="card" id="cardTreemap">` | ✓ | Standard. |
| `flex-between flex-wrap:wrap;gap:6px` (line 3235) | ✓ | OK — toolbar wraps on narrow widths. |
| Card-title `class="card-title tip"` | ✓ | Tooltip via `data-tip`. Good. |
| `tileChromeStrip(...)` | ✓ | Properly used; consistent with the 30/30 migration completion (Phase D refactor). |

### 3.4 Empty state

Line 7317: `<p style="color:var(--txt);font-size:12px;text-align:center;padding:60px">No holdings to visualize</p>`

| Issue | Fix |
|---|---|
| Should use `.empty-state` class (one of the 10 canonical classes per ARCHITECTURE §4.3) | T-tier — replace inline-styled `<p>` with `<div class="empty-state">No holdings to visualize</div>` |
| Bucket-empty case (e.g., `_treeDim='grp'` on a strategy with no `subg` data) returns from the loop without rendering an empty-state — `treeDiv` retains the previous render | T5 — explicit empty-state when bucket dict is empty after the forEach |

### 3.5 Hairline footer

**Currently absent.** Sibling tiles (cardSectors, cardCountry, cardRiskByDim, cardCalHeat) render a hairline footer with bucket-count + Σ + caveat. The treemap has none.

**Recommended footer content:**
```
{N buckets} · Σ size = {total} · F18-aware caveat when size=te
```

For the F18 case specifically, per P3, the footer should read:
```
Σ |TE| = 134.4% (per-holding %T sum, expected ~100% — see F18)
```
(Numbers per-strategy.) This is the honest-math posture from ARCHITECTURE.md §5.3.

**T4** in trivial queue.

### 3.6 Breadcrumb during drill

Line 7407 — well-designed; uses `var(--txt)`, `var(--txth)`, `var(--surf)`, `var(--grid)` correctly. The "← Back" button has `padding:2px 10px` while other dashboard pill buttons use `4px 12px` — minor; acceptable.

### 3.7 Plotly margin and sizing

| Element | Status | Notes |
|---|---|---|
| `margin:{l:5,r:5,t:5,b:5}` | ✓ | Tight margins appropriate for treemap; no axis labels. |
| `height:360px` | ✓ | Adequate for 6–12 buckets; cramped for 80-holding drill. Fullscreen handles the cramped case. |
| `textfont:{size:11, family:'DM Sans'}` | ✓ | Body font. Good. |

**Section 3 rating: YELLOW.** Five token/style drifts (T1 hardcoded hex, T3 toolbar font, T4 missing footer, TL2 palette unification, plus minor T-finding on white text). All trivial individually; cumulative effect is "this tile feels different from siblings." Overall the chrome is correct and the toolbar layout is good.

---

## §4 — Mode matrix coverage (special section)

The treemap is a 4 dim × 3 size × 2 color = **24-mode matrix.** This audit verified each mode by inspecting the source code paths (no live data — a follow-up live spot-check is queued).

| Dim | Size | Color | Source verified | F18 risk | Visual concern |
|---|---|---|---|---|---|
| Sector | Weight | Active | `Σ h.p`; `sign(Σ h.a)` | clean | OK |
| Sector | Weight | Rank | `Σ h.p`; weighted-avg `h.over` | clean | OK |
| Sector | TE | Active | `Σ \|h.tr\|`; `sign(Σ h.a)` | **F18** | OK |
| Sector | TE | Rank | `Σ \|h.tr\|`; weighted-avg `h.over` | **F18** | OK |
| Sector | Count | Active | `b.count`; `sign(Σ h.a)` | clean | uniform-rect risk |
| Sector | Count | Rank | `b.count`; weighted-avg `h.over` | clean | uniform-rect risk |
| Country | Weight | Active | `Σ h.p`; `sign(Σ h.a)` | clean | OK; high-card (>30 buckets typical) |
| Country | Weight | Rank | `Σ h.p`; weighted-avg `h.over` | clean | OK |
| Country | TE | Active | `Σ \|h.tr\|`; `sign(Σ h.a)` | **F18** | OK |
| Country | TE | Rank | `Σ \|h.tr\|`; weighted-avg `h.over` | **F18** | OK |
| Country | Count | Active | `b.count`; `sign(Σ h.a)` | clean | uniform-rect; many buckets |
| Country | Count | Rank | `b.count`; weighted-avg `h.over` | clean | uniform-rect; many buckets |
| Group | Weight | Active | `Σ h.p` (per `h.subg`); `sign(Σ h.a)` | clean | **degenerate** if 80%+ in one subgroup |
| Group | Weight | Rank | `Σ h.p`; weighted-avg `h.over` | clean | degenerate |
| Group | TE | Active | `Σ \|h.tr\|`; `sign(Σ h.a)` | **F18** | degenerate |
| Group | TE | Rank | `Σ \|h.tr\|`; weighted-avg `h.over` | **F18** | degenerate |
| Group | Count | Active | `b.count`; `sign(Σ h.a)` | clean | degenerate + uniform |
| Group | Count | Rank | `b.count`; weighted-avg `h.over` | clean | degenerate + uniform |
| Rank | Weight | Active | `Σ h.p` (per quintile bucket); `sign(Σ h.a)` | clean | **degenerate** — Q1 ~56% per CLAUDE.md |
| Rank | Weight | Rank | `Σ h.p`; weighted-avg `h.over` | clean | degenerate; **redundant** — coloring by rank inside a rank-bucketed tree is a visual tautology (every bucket is its own quintile) |
| Rank | TE | Active | `Σ \|h.tr\|`; `sign(Σ h.a)` | **F18** | degenerate |
| Rank | TE | Rank | `Σ \|h.tr\|`; weighted-avg `h.over` | **F18** | degenerate + redundant |
| Rank | Count | Active | `b.count`; `sign(Σ h.a)` | clean | degenerate + uniform |
| Rank | Count | Rank | `b.count`; weighted-avg `h.over` | clean | degenerate + uniform + redundant |

**Coverage:** 24/24 mode source paths verified by code inspection.
**F18 risk:** 8 of 24 modes (every Size=TE combination).
**Visual concern modes:**
- 8 modes: uniform-rect (Size=Count) — Plotly may render labels poorly when all rectangles are equal area.
- 6 modes: degenerate Group (top-1 subgroup likely dominates).
- 6 modes: degenerate Rank (Q1 dominates per CLAUDE.md).
- 2 modes: redundant Rank-color × Rank-dim (visual tautology).

**Recommendation:** PM gate P4 covers the degeneracy. If "Group" and "Rank" dimensions are kept, add a tooltip on those toggles explaining the expected skew so PMs don't mistake degeneracy for a bug.

---

## §5 — Numbered findings

### Track 1 — Data accuracy

**F1.1 — F18 contamination on Size=TE and TE-tooltip line.**
- **Severity:** RED (escalated, awaiting FactSet response per inquiry F18)
- **Location:** lines 7334, 7356, 7360, 7369
- **What:** treemap aggregates per-holding `h.tr` (FactSet `%T`); F18 shows Σ varies 94.6→134.4% across strategies vs documented ~100%.
- **Why matters:** users may compare bucket sums to known portfolio TE and see ±35% deviation — looks like a bug; cross-strategy comparisons are off by up to 1.4×.
- **Fix:** P3 PM gate. Recommended option B (honest-math footer per ARCHITECTURE.md §5.3): `Σ \|TE\| = X% (expected ~100%, see F18)`. ~6 LoC.

**F1.2 — TE row in hover tooltip is always shown, even when Size≠TE.**
- **Severity:** YELLOW
- **Location:** lines 7360, 7369
- **What:** the hover always exposes Weight/Active/TE/Rank; the TE line carries F1.1 contamination on every hover regardless of size pill.
- **Why matters:** PM hovering for Weight info still sees an F18-contaminated TE number.
- **Fix:** when F1.1 footer ships, the tooltip remains transparent because the user can read the caveat. Alternatively, suppress the TE row when `_treeSize !== 'te'`. PM call.

**F1.3 — Weighted-rank fallback mixes weighted and unweighted within the same bucket.**
- **Severity:** LOW
- **Location:** line 7336 (`b.rankSum += h.over*(h.p>0?h.p:1); b.rankN += (h.p>0?h.p:1)`)
- **What:** holdings with `h.p<=0` (bench-only) get weight=1, mixing with port-weighted holdings.
- **Why matters:** on strategies with meaningful bench-only universe (most), Avg Rank tooltip + bucket coloring biases toward the unweighted side. Today's data has many bench-only rows in cardCountry / cardSectors universe — non-trivial bias.
- **Fix:** decide weighting policy. Either (a) weight only by `h.p` (skip h.p<=0); or (b) consistently weight by 1 across all holdings; or (c) two separate values "Avg Rank (port-weighted)" and "Avg Rank (simple)" — same as the global Wtd/Avg toggle on cardSectors. PM gate. **TL-tier** if PM picks (a) or (b). **Larger** if PM picks (c).

**F1.4 — Per-week silent-latest.**
- **Severity:** LOW (consistent with sibling tiles per AUDIT_LEARNINGS)
- **Location:** line 7326 (`s.hold` direct read)
- **What:** treemap always renders latest-week holdings even when `_selectedWeek` is set.
- **Why matters:** dashboard-wide consistency expectation; user picks a week, expects all tiles to reflect it.
- **Fix:** TL5 — banner-route is 5 LoC; wired-route requires B114 (per-week holdings persistence) which is in backlog. Recommend banner now.

**F1.5 — Drilled-holding active color hardcoded `#10b981`/`#ef4444` instead of the resolved `posC`/`negC`.**
- **Severity:** LOW
- **Location:** line 7358
- **What:** drilled-tile coloring uses raw hex; bucket-level coloring (line 7339–7343) correctly resolves `--pos`/`--neg` via `getComputedStyle`. Inconsistent.
- **Why matters:** if user theme changes the `--pos`/`--neg` tokens, the drilled tiles won't follow.
- **Fix:** T1 — reuse `posC`/`negC` already in scope. 1-line change.

### Track 2 — Functionality parity

**F2.1 — Universe pill ignored.**
- **Severity:** MED (PM gate P2)
- **Location:** line 7326
- **What:** treemap aggregates all of `cs.hold[]` regardless of `_aggMode` (`portfolio`/`benchmark`/`both`). Sibling holdings-aggregate tiles all honor the pill.
- **Why matters:** inconsistency with the rest of the dashboard. If user flips to "Port-Held only", treemap continues to show bench-only-heavy buckets (e.g., a country that's all bench-only).
- **Fix:** PM call (P2). If "should respect", wrap the forEach in `inUniverse(h)`-style filter (~5 LoC). If "intentionally not", document via card-title tooltip (1 LoC).

**F2.2 — No bucket→canonical drill modal.**
- **Severity:** MED (PM gate P1)
- **Location:** line 7400
- **What:** click on Sector bucket → in-tile drill (top 80 holdings of that sector). Sibling tile cardSectors row click → `oDr('sec', sectorName)` opens canonical drill modal with TE sparkline + bench-only + ORVQ breakdown. cardTreemap has no path to that canonical modal.
- **Why matters:** PMs muscle-memory expects the canonical drill from any sector reference.
- **Fix:** PM call on UX (shift-click? button on breadcrumb? secondary "Open detail ›" link?). ~20 LoC.

**F2.3 — No CSV export of bucket data.**
- **Severity:** LOW
- **Location:** line 3235 (chrome strip lacks `csv:` key)
- **What:** sibling cardSectors / cardCountry / cardGroups all ship CSV exports of underlying tabular data.
- **Why matters:** bucket {label, count, wt, active, te, avgRank} is offline-useful (PM emails, regression testing). Parity gap.
- **Fix:** TL4 — `exportTreeBuckets()` helper + add `csv:'exportTreeBuckets()'` to chrome. ~12 LoC.

**F2.4 — Toolbar state not persisted.**
- **Severity:** LOW
- **Location:** lines 7301–7306
- **What:** every reload resets to Sector/Weight/Active. PMs using treemap daily expect sticky.
- **Why matters:** cardCountry, cardRiskByDim, cardCalHeat all persist toolbar state per CLAUDE.md hard rule #3. Inconsistent.
- **Fix:** TL1 — load from localStorage on init; persist on each `set*` call. ~15 LoC.

**F2.5 — Color legend missing.**
- **Severity:** LOW
- **Location:** below toolbar (no legend currently)
- **What:** no on-tile legend for "Active = green-positive / red-negative" or "Rank = Q1 deep green → Q5 deep red". Users discover meaning via hover or guessing.
- **Why matters:** cardCountry heatmap, cardCalHeat, cardCorr all ship inline color scales. Interpretation aid.
- **Fix:** TL3 — small legend strip below toolbar, swap on `_treeColor`. ~20 LoC.

### Track 3 — Design consistency

**F3.1 — About-text in registry contradicts shipped UI.**
- **Severity:** MED (user-facing wrong info)
- **Location:** line 1192
- **What:** registry says dims are `sector / region / industry / group` but UI ships `Sector / Country / Group / Rank`. Sizes registry says `port wt / bench wt / |TE| / |MCR|` but UI ships `Weight / TE / Count`. Colors registry says `active wt / TE contrib / spotlight rank` but UI ships `Active / Rank` (no TE-contrib color mode).
- **Why matters:** clicking the ⓘ About button on the tile shows incorrect feature description. Outright user-facing wrong content.
- **Fix:** T2 — rewrite the `how:` string in `cardTreemap` registry entry to match shipped UI. 1-line edit.

**F3.2 — Hardcoded hex literals for pos/neg in drilled-holding path.**
- See F1.5 above. Same finding from data and design lenses.
- **Fix:** T1 — 1 LoC.

**F3.3 — Toolbar pill font 9px, inline-styled.**
- **Severity:** LOW
- **Location:** lines 3238, 3240, 3242
- **What:** every button has `style="padding:1px 6px;font-size:9px"` overriding `.toggle-btn` defaults. 9px is below the dashboard's 10–11px pill standard.
- **Why matters:** accessibility; consistency. Inline override also hides this from any future `.toggle-btn` CSS refactor — silent-break risk.
- **Fix:** T3 — remove inline overrides on all 9 buttons; rely on `.toggle-btn` class. 9 inline-style attribute removals.

**F3.4 — Rank palette duplicates `rc()` design-system helper.**
- **Severity:** LOW-MED
- **Location:** lines 7307–7310
- **What:** `_treeRankColor(q)` defines its own 5-color literal palette. `var(--r1..r5)` exists; `rc()` helper exists. New 4th palette variant (after `rc()`, cardFRB, cardFacButt).
- **Why matters:** palette fragmentation accelerates over time; theme changes need to update N places.
- **Fix:** TL2 — replace `_treeRankColor` body with `rc()` (exported from somewhere) and resolve `var(--r1..r5)` to literal hex via `getComputedStyle`. ~8 LoC.

**F3.5 — No hairline footer.**
- **Severity:** LOW (but COUPLED with F1.1 — footer is also where the F18 caveat lives)
- **Location:** below `treeDiv`
- **What:** sibling tiles ship hairline footers with bucket-count + Σ + provenance caveats. Treemap has none.
- **Why matters:** missing self-documenting context; missing F18 caveat home.
- **Fix:** T4 — small `<div class="hairline-footer">` after Plotly init. Content per `_treeSize`: `Σ wt = X%`, `Σ |TE| = Y% (F18 caveat)`, or `N holdings`. ~6 LoC.

**F3.6 — Empty-state inline-styled instead of `.empty-state` class.**
- **Severity:** TRIVIAL
- **Location:** line 7317
- **What:** `<p style="color:var(--txt);font-size:12px;text-align:center;padding:60px">` should be `<div class="empty-state">`.
- **Why matters:** one of the 10 canonical CSS classes per ARCHITECTURE §4.3. Consistency.
- **Fix:** T-tier — 1-line replace.

**F3.7 — Bucket-empty case re-uses prior render.**
- **Severity:** LOW
- **Location:** after line 7337 forEach loop
- **What:** if `Object.keys(buckets).length === 0` (e.g., `_treeDim='grp'` on a strategy where no holdings have `subg`), the function continues to call `Plotly.purge` + `Plotly.newPlot` with only the root node — the treemap renders a single Portfolio rectangle with no children. Looks broken.
- **Why matters:** dead-state UX. Better: explicit empty-state when bucket dict is empty.
- **Fix:** T5 — guard after forEach: `if(!Object.keys(buckets).length){ /* render empty-state */ return; }`. ~3 LoC.

**F3.8 — `customdata` HTML-injection on holding name.**
- **Severity:** LOW (security/correctness)
- **Location:** lines 7360, 7369
- **What:** `<b>${h.n||tk(h)}</b>` interpolates `h.n` directly. FactSet ships company names with `&`, occasional `<` (rare). Plotly hover supports limited HTML; raw `<` could escape the `<b>` tag boundary.
- **Why matters:** rare edge case; not currently a security issue (no user input), but a malformed name like `Halma & Co. <Plc>` could render funny tooltips.
- **Fix:** T6 — wrap with `esc()` helper (already exists in dashboard for similar purposes). 2 LoC.

---

## §6 — Color-status by section

| Section | Status | Why |
|---|---|---|
| §1 Data accuracy | **YELLOW (RED on F18 path)** | 🟢 sourced for label/wt/cnt/active/rank; 🔴 F18-contaminated for Size=TE and tooltip-TE. Per-week silent-latest acceptable per AUDIT_LEARNINGS. |
| §2 Functionality parity | **YELLOW** | 5 prior B-items shipped (fullscreen, note popup, drill reset, subg parser); 5 gaps remain (universe pill, canonical drill, CSV, persist, legend). |
| §3 Design consistency | **YELLOW** | 8 token/style drifts (T1, T2, T3, T4, T5, T6, plus TL2 palette + minor white text). All trivial individually; cumulative drift is "this tile feels different." |

**Overall: YELLOW** — bordering RED on the F18 path until P3 lands.

---

## §7 — Recommended fix queue (ordered by leverage)

### Phase 1 — Trivial main-session fixes (≤ 20 LoC total)

1. **T2** — Fix About-registry text (1 LoC). [Highest user-facing leverage; one-line edit.]
2. **T1** — Drilled-tile pos/neg → `posC`/`negC` (1 LoC).
3. **T3** — Remove inline toolbar styles, use `.toggle-btn` (9 attribute removals).
4. **T6** — `esc()` wrap on `h.n` (2 LoC).
5. **F3.6** — `.empty-state` class on line 7317 (1 LoC).
6. **F3.7** — Guard for bucket-empty case (3 LoC).
7. **TL5 banner** — `_selectedWeek` amber strip (5 LoC).

### Phase 2 — F18 defensive UI (PM gate P3 → ship within session)

8. **T4 / F1.1** — Hairline footer + F18 caveat when `_treeSize==='te'`. ~10 LoC. **Required to land Track 1 GREEN.**

### Phase 3 — Trivial-but-larger (next session)

9. **TL1** — Persist toolbar state (~15 LoC).
10. **TL2** — Unify rank palette via `rc()` (~8 LoC).
11. **TL3** — Color legend strip (~20 LoC).
12. **TL4** — CSV bucket export (~12 LoC).

### Phase 4 — PM gates (queue)

13. **P1** — Bucket → canonical `oDr`/`oDrCountry` modal route. UX call needed.
14. **P2** — Universe-pill behavior. Document or wire.
15. **P3** — F18 posture confirmation (recommended option B above; main-session ship after PM nod).
16. **P4** — Group / Rank dimension fate (degeneracy concerns).
17. **P5** — Active color: binary vs gradient.

---

## §8 — Verification checklist

- [x] Render path located (`rTree` at 7316; toolbar at 3236–3243; helpers at 7300–7314)
- [x] Data fields mapped (label / size / color / hover for both top-level and drilled-into modes)
- [x] Mode-matrix coverage (24/24 paths source-verified)
- [x] F18 lens applied (Size=TE flagged; recommended posture per ARCHITECTURE §5.3)
- [x] Universe-pill behavior (B116) checked — finding F2.1
- [x] Per-week (`_selectedWeek`) handling checked — finding F1.4
- [x] Tile-chrome migration verified (line 3235 uses `tileChromeStrip`; fullscreen + about + reset + hide present; csv missing)
- [x] Note popup checked (line 3235 — shipped post-April-21)
- [x] `_treeDrill` shared-state trap checked (line 2202 — shipped post-April-21)
- [x] Theme-token audit (T1, T3, T4, TL2)
- [x] Empty-state class audit (F3.6, F3.7)
- [x] Customdata escape audit (T6 / F3.8)
- [x] Cross-checked About-registry against shipped UI (T2 — major mismatch)
- [ ] **Live spot-check** — blocked, no JSON loaded in this audit cycle. Spot-checks queued in §1.4.
- [ ] **Browser verification of full-screen state preservation** — queued (chrome strip ships `openTileFullscreen('cardTreemap')` but FS modal preservation of Dim/Size/Color + drill not verified)
- [x] Prior audit reconciled (April 21 audit B20/B23/B28/D1 → all shipped; B22/B24/B25/B26/B27 → still open as TL/T-items above)

---

## §9 — Cross-reference

- **CLAUDE.md** rules 1–6: all preserved (no fabrication; no localStorage-as-data; integrity assertion runs).
- **ARCHITECTURE.md** §3.4 (per-week silent-latest accepted) · §4.6 (universe-invariance — F2.1 is the gap) · §5.3 (defensive UI for F18 — P3 / F1.1).
- **SOURCES.md** — needs update with cardTreemap row (currently absent from the index). Action: add a row mapping `b.wt` / `b.te` / `b.active` / `b.over` to their sources, with F18 caveat on `b.te`.
- **FACTSET_FEEDBACK.md** F18 — direct dependency for Track 1 RED → GREEN.
- **LESSONS_LEARNED.md** Lesson 12 (escalate, don't paper over) → directly applicable to F1.1 fix posture.
- **STRATEGIC_REVIEW.md** "doing it right" framing → favors honest-math caveat (option B) over silent rescale.

---

## §10 — Three-line summary for coordinator

> cardTreemap audit (2026-05-04): YELLOW / YELLOW / YELLOW (Track 1 borders RED on F18 contamination, Size=TE path). Top finding: hover-tooltip `Σ |TE|` line carries F18 deviation (94→134%) on every hover regardless of size pill — needs honest-math footer per ARCHITECTURE §5.3 (P3 PM-gate). About-registry text at L1192 contradicts shipped UI (wrong dims / sizes / colors — T2 trivial, 1-line edit). Trivial queue of 7 fixes (~20 LoC); PM gates for universe-pill behavior, canonical-drill route, F18 posture, dimension fate.
