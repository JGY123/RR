# cardTreemap — Tile Audit v1

**Date:** 2026-04-21
**Auditor:** tile-audit subagent
**Batch:** Tier-1 Batch 3 (sibling-row sweep with cardRanks / cardChars / cardScatter)
**Scope:** audit + propose only — no edits to dashboard_v7.html
**Rating preview:** YELLOW / YELLOW / YELLOW (see §8)

---

## §0 — Identity

| Field | Value |
|---|---|
| Tile name | Holdings Treemap |
| Card DOM id | `#cardTreemap` |
| Render function | `rTree(s)` at dashboard_v7.html:2604 |
| Render trigger | called from exposures-tab `setTimeout(...,50)` block, L2343 |
| Tab | **Holdings** (renders inside `tab-exposures` innerHTML, L1251 — "Row 7: Scatter + Treemap") |
| Width | half (`.grid.g2` row with cardScatter, L1252) |
| Chart target | `#treeDiv` (Plotly treemap, fixed `height:360px`) |
| Toolbar | 3 toggle groups: **Group-by** (Sector / Country / Group / Rank), **Size** (Weight / TE / Count), **Color** (Active / Rank) — all reset on reload |
| Drill | in-tile via `plotly_treemapclick` → `treeDrillInto(name)` — full-screen / modal drill not wired |
| Phantom-spec | `tile-specs/active-weight-treemap-spec.md` is a raw JSONL agent-transcript (2026-04-13). Treat all of its claims as aspirational unless verified in code. |

---

## §1 — Data accuracy (TRACK 1)

### 1.1 Field inventory — bucket-level (top level, `!_treeDrill`)

| # | Displayed as | Source | Path | Format | Verified? |
|---|---|---|---|---|---|
| 1 | Bucket label | `h.sec` / `h.co` / `h.subg` / `'Q'+round(h.over)` | `cs.hold[].*` | raw string | See 1.2 — **`h.subg` never populated** |
| 2 | Rectangle size | Σ `h.p` / Σ `|h.tr|` / count | `cs.hold[].p`,`tr` | `val.toFixed(2)`, min clamp `0.01` | OK (min clamp prevents 0-area rects) |
| 3 | Rectangle color — Active mode | sign of Σ `h.a` | `cs.hold[].a` | `#10b981` / `#ef4444` hardcoded | L2629 — see §3 theme drift |
| 4 | Rectangle color — Rank mode | weighted avg `h.over` | `cs.hold[].over` | `_treeRankColor(q)` 5-step gradient | L2595, hardcoded colors |
| 5 | Hover: Holdings (count) | `b.count` | computed | integer | OK |
| 6 | Hover: Weight | `b.wt = Σ h.p` | `cs.hold[].p` | `f2(v,1)%` | OK |
| 7 | Hover: Active | `b.active = Σ h.a` | `cs.hold[].a` | `fp(v,1)` | ⚠ see 1.3 |
| 8 | Hover: TE | `b.te = Σ |h.tr|` | `cs.hold[].tr` | `f2(v,1)%` | OK |
| 9 | Hover: Avg Rank | `Σ(h.over × w) / Σ w` where `w=h.p>0?h.p:1` | `cs.hold[].over`,`p` | `toFixed(1)` | ⚠ see 1.3 |

### 1.2 Dead dimension — Group

- **Finding D1 (HIGH, trivial-ish):** `_treeDim==='grp'` maps to `h.subg` (L2610). `h.subg` is assigned by the parser at factset_parser.py:611/544 **only if the input CSV contains a `SEC_SUBGROUP` column** — it does not, in any current FactSet export. Result: clicking the **Group** toggle produces an empty treemap ("No holdings" via the `if(!k)return` filter at L2616). Silent dead button.
- **Proposed fix (5 lines, trivial):** compute `h.subg` in `enrichHold` using the same GROUPS_DEF → sector mapping already used at L1895 (`SEC_ALIAS` + `GROUPS_DEF[].secs[]` → `gd.sg`). Example:
  ```js
  let sg={};GROUPS_DEF.forEach(gd=>gd.secs.forEach(sec=>{
    let full=SEC_ALIAS[sec]||sec;(sg[full]=sg[full]||[]).push(gd.sg);}));
  return hold.map(h=>({...h, reg:CMAP[h.co]||'Other', subg:(sg[h.sec]||[])[0]||null, secRet:...}));
  ```
  Caveat: GROUPS_DEF has overlapping mappings (Info Technology appears in both GROWTH CYCLICAL and GROWTH). Taking `[0]` is a first-match heuristic — would need a PM decision if we want multi-group attribution. Flag as trivial-ish / soft-PM.

### 1.3 Aggregation quirks

- **Weighted rank fallback trap (L2624):** `b.rankSum += h.over * (h.p>0?h.p:1); b.rankN += (h.p>0?h.p:1)`. For holdings with `h.p<=0` (cash-absent shorts or bench-only), the weight collapses to 1 — mixing a weighted average with an unweighted average within the same bucket. On strategies with meaningful shorts this will bias the "Avg Rank" hover tooltip toward the un-weighted side. Minor; prod data today has no shorts so the effect is the bench-only rows (`h.p==0`) getting weight 1.
- **Active aggregation, country dimension:** Σ(h.a) within a country bucket approximates `cs.countries[].a` for that country because `cs.hold[]` includes bench-only rows (verified via benchOnly filter at L3986). No correctness issue, but worth noting that the displayed "Active" is sensitive to the completeness of bench-side holdings the parser returned — if a bench-only row is dropped upstream, the treemap silently undercounts. Flag for verification when we eventually get a 3-year file.
- **Size='Count' bucket hover shows `Weight`/`Active`/`TE` even though the rectangle is sized by count** — hover tooltip always shows all four metrics. Acceptable (more info is fine) but worth a 1-line header note: "size = N holdings" when Count is active.
- **Cash handling:** `isCash(h)` exclusion at L2615 is consistent with cardMCR and cardScatter. Good.

### 1.4 Spot-check (pending — requires loaded JSON)

Not executable in this environment. Spot-checks to run when data is loaded:
- [ ] Sum of bucket weights at Group-by=Sector, Size=Weight ≈ 100% minus cash
- [ ] Σ bucket `active` ≈ 0 (active weights sum to zero across sectors)
- [ ] Σ bucket `te` ≈ portfolio TE contribution from cardMCR's denominator
- [ ] Rank-mode color for a known Q1-heavy sector renders green; known Q5-heavy sector renders red

### 1.5 Week-selector awareness

- `rTree(s)` is called with full `cs` object (L1343), reads `s.hold` directly — standard two-layer history behavior (detail tables silently show latest when `_selectedWeek` is set). Consistent with cardSectors / cardHoldings / cardMCR / cardScatter. Per AUDIT_LEARNINGS, this is by-design and not flagged as a bug. **No banner required on this tile.**

**Section 1 rating: YELLOW** — one dead dimension (D1), one aggregation quirk (weighted-rank fallback), but core numbers are sound.

---

## §2 — Functionality parity (TRACK 2)

Benchmark row: cardScatter (sibling in the same `g2` row), cardFacButt (has click-drill to factor modal), cardSectors (gold-standard table). Full-screen gold-standard: cardCountry map.

| Capability | cardScatter | cardFacButt | This tile | Gap? |
|---|---|---|---|---|
| PNG export | yes (L1257) | via dl-wrap | yes (L1263) | — |
| CSV export | — (chart) | — | **none** | minor — bucket data table is CSV-worthy (see B22) |
| Full-screen (⛶) button | yes (L1256, `openFullScreen('scatter')`) | yes (L1166) | **none** | **B20** |
| Drill to per-bucket modal (`oDr('sec',name)`) | n/a | n/a (factor drill) | **none** (drills in-tile only) | **B21** |
| Drill to per-stock modal (`oSt(ticker)`) | — | — | yes (only after first drill, L2671) | minor parity — see §2.1 |
| Right-click note popup (`showNotePopup(event,'cardXxx')`) | — | yes (L1158) | **none** | **B23** |
| Toolbar state persisted (localStorage) | — | `_facView` (module-shared) | **no** — resets on reload | B24 (trivial) |
| Empty-state fallback | — | — | yes (L2605) | — |
| Theme-aware (uses THEME()) | yes | yes | partial — see §3 | **B25** |
| Range selector / week awareness | n/a | n/a | n/a (detail tile) | — |

### 2.1 Drill-parity gaps (detailed)

- **B20 — No full-screen button.** Sibling cardScatter, cardCountry, cardFacMap all have `openFullScreen(...)`. Treemap at 360px is cramped for a 30-bucket country view. Full-screen variant should preserve toolbar state (Dim/Size/Color + Drill).
- **B21 — No cross-link to sector/country/rank drill modal.** When a user clicks "Materials" at top level, the only route is in-tile drill → 80 holdings. There is no "Open sector detail" option that routes to `oDr('sec','Materials')` — the canonical sector drill modal with TE sparkline + benchmark comparison. Proposed UX: shift-click a bucket → `oDr(...)`; plain click = drill-in-tile (current). Or add a small "Open detail ›" button in the breadcrumb during drill mode.
- **Per-holding drill in drill mode works** (L2670–2672) — routes to `oSt(h.t)`. Parity with cardHoldings table is fine.
- **Drill-click returns false** (L2672, L2676) — prevents Plotly's native zoom. Good.

### 2.2 Dead control — Group toggle

See D1 in §1.2. The toggle itself renders and is clickable, but produces an empty treemap. This lands in Track 2 as a **FUNCTIONALITY gap** as much as Track 1.

### 2.3 `_treeDrill` shared-state trap

`_treeDrill` is module-global (L2589). If the user drills into "Financials" and then switches tabs and strategy, `_treeDrill` persists → on re-render the tile attempts to show "Financials" in a strategy that may not have that bucket. Guard at L2633 (`buckets[_treeDrill]`) handles the miss — it falls through to top-level render — but the breadcrumb stale-reset is then skipped and user loses context. Minor.

**Proposed:** reset `_treeDrill=null` in `normalize()` or on strategy switch. 1-line fix. Trivial.

**Section 2 rating: YELLOW** — 4 parity gaps, one dead button, one shared-state trap.

---

## §3 — Design consistency (TRACK 3)

Reference tokens: `--pri`, `--pos`, `--neg`, `--txt`, `--txth`, `--grid`, `--card`, `--surf`, `--r1..r5`. Gold-standard density: 11px values, 10px labels.

| Area | Standard | cardTreemap | Drift? |
|---|---|---|---|
| Positive color | `THEME().pos` / `var(--pos)` | hardcoded `#10b981` at L2629, L2644 | **B25** |
| Negative color | `THEME().neg` / `var(--neg)` | hardcoded `#ef4444` at L2629, L2644 | **B25** |
| Rank-quintile colors | `var(--r1..r5)` (used everywhere else in `rc(r)`) | hardcoded palette L2597: `#10b981 / #34d399 / #f59e0b / #fb923c / #ef4444` | **B26** — this is a new, 4th quint-palette variant: sectors use `rc()`, cardFacButt uses its own factor palette, cardFRB has a 7-color palette, and now this. CMAP drift in spirit. |
| Toggle buttons | `.toggle-btn` (11px, 4px 12px padding) | inline-styled overrides (L1266–1270): `padding:1px 6px;font-size:9px` | **B27** — font-size 9px is smaller than any other toggle in the app. Uncomfortable on 4K displays. |
| Card header (tip + export bar) | flex-between, tip card-title | flex-between with `flex-wrap:wrap;gap:6px` (L1262) — different shape for the wrap | acceptable (toolbar is wide) |
| Card-title tooltip | `data-tip="..."` | present (good, L1262) | — |
| Note popup (⋯ / right-click) | cardFacButt, cardFRB, cardFacDetail, cardSectors, cardCountry have it | **missing** | **B23** |
| Breadcrumb strip | new pattern (L2678-2687) — not seen elsewhere in dashboard | consistent coloring via `var(--txt/--txth/--surf)` | OK, but the "Back" button has `padding:2px 10px` while other pill buttons use 4px 12px — subtle |
| Heading "Holdings Treemap" | sentence-case | matches other tiles | OK |
| Toolbar labels "Group / Size / Color" | uppercase + 0.3px letter-spacing (L1265–1269) | matches Spotlight-group convention | OK, nice |
| Plotly margin | gold: `{l:5,r:5,t:5,b:5}` for treemap (L2662) | OK | — |
| Line color | `T.grid` (good, L2660) | OK | — |
| Font size in cells | `size:11, color:T.tickH` (L2660) | OK | — |

### 3.1 Design-drift summary

- **B25** — theme-token drift (4 hardcoded color literals) — trivial 2-line fix.
- **B26** — new 5-color rank palette introduces a 4th variant of quintile coloring. Either unify to `rc(q)` (already accepts 1–5) or expose a single `RANK_PALETTE` constant consumed by both `rc()` and `_treeRankColor()`.
- **B27** — 9px toggle font-size undershoots the 11px minimum used elsewhere. Inline styling also bypasses `.toggle-btn.active` styles — behaviourally the active state works because the manual `data-*` matcher at L2600–2602 still toggles `.active`, but future CSS refactors could break it silently.
- No PNG button removal required — the tile already offers PNG and CSV parity is a separate proposal (B22). **No PNG-removal trivial fix here** (per user preference, PNG is not being mass-removed — only mass-not-added).

**Section 3 rating: YELLOW** — three token/palette drifts, all trivial.

---

## §4 — Functionality matrix (full)

| Capability | Benchmark presence | This tile |
|---|---|---|
| Sort | n/a (chart) | — |
| Filter | n/a | — |
| Column picker | n/a | — |
| PNG export | yes | yes |
| CSV export of underlying bucket data | cardSectors yes | **no** (B22) |
| Row / bucket click → drill-in-tile | — | yes |
| Row / bucket click → per-bucket detail modal (`oDr`) | gold-standard on tables | **no** (B21) |
| Per-holding click → `oSt()` | gold-standard | yes (in drill mode) |
| Right-click context note | 3+ siblings have it | **no** (B23) |
| Card-title tooltip | yes | yes |
| Hover tooltip on chart | yes | yes |
| Toggle views | cardSectors Table/Chart | 3-axis toolbar (Group/Size/Color) — richer; good |
| Full-screen modal | scatter, country, facmap yes | **no** (B20) |
| Theme-aware | gold-standard | partial (B25) |
| Toolbar state persisted | `_facView` persists across tab renders | **no** (B24) |
| Empty-state | yes | yes (L2605) |
| Dead-control protection (resets on strategy switch) | normalize clears state | **no** (`_treeDrill` leaks, §2.3) |

---

## §5 — Popup / drill detail

- **In-tile drill breadcrumb** (L2678-2687): "Sector › Financials [← Back]   Click a tile for stock detail" — clear, good pattern. One unresolved concern: the word "tile" inside a tile can confuse PMs; consider "rectangle" or "box".
- **No dedicated modal** for treemap (unlike cardFRB → `oDrRiskBudget`, cardFacButt → `oDrF`). Full-screen version (B20) could double as the modal.

---

## §6 — Design (see §3)

---

## §7 — Non-trivial queue (backlog candidates)

| B-id | Severity | Title | Rationale | Est. effort |
|---|---|---|---|---|
| **B20** | MED | Full-screen variant for cardTreemap | 360px is cramped for Country/80-bucket views; siblings all have ⛶ button. Must preserve Dim/Size/Color state + Drill path. | 60–100 LOC + 1 fs-render fn mirroring `renderFsCountryMap` |
| **B21** | MED-HIGH | Bucket → sector/country detail modal (`oDr`) route | Users click a sector expecting the gold-standard sector drill (TE sparkline, bench-only, ORVQ breakdown); currently buried behind an extra step. Needs PM UX call: shift-click? breadcrumb button? context menu? | 20 LOC + PM UX |
| **B22** | LOW | CSV export of bucket table | Bucket-level {label, count, wt, active, te, avgRank} is a useful offline artefact; matches sibling-tile convention. | 15 LOC + new helper `exportTreeBuckets()` |
| **B23** | LOW | Right-click note popup (`showNotePopup`) | 3+ sibling tiles have it; cardTreemap doesn't. Cheap add. | 1 LOC |
| **B24** | LOW | Persist `_treeDim`/`_treeSize`/`_treeColor`/`_treeDrill` | Every reload resets to Sector/Weight/Active; PMs using the tile daily will expect sticky. Similar to `_facView` pattern but local. | 10 LOC; localStorage key `rr.tree.*` |
| **B25** | LOW-MED | Replace hardcoded `#10b981`/`#ef4444` at L2629 + L2644 with `THEME().pos/neg` | Design tokens; standard cross-tile drift. | 2 LOC (trivial — eligible for main-session fix pass) |
| **B26** | MED | Unify quint-rank palette (`_treeRankColor` → `rc()` or shared `RANK_PALETTE`) | New 4th quint palette; accelerates palette fragmentation (cardFRB audit flagged same direction). | 15 LOC + regression check across all tiles using `rc()` |
| **B27** | LOW | Toolbar toggle 9px → 11px, remove inline overrides, use `.toggle-btn` class | Accessibility + consistency with all other toolbars. | 3 LOC |
| **B28** | LOW | Reset `_treeDrill=null` on strategy / week switch | Shared-state trap (§2.3). | 1 LOC in `normalize()` or the tab-switch callback |
| **D1** | MED | Populate `h.subg` in `enrichHold` using GROUPS_DEF | Dead "Group" toggle button silently renders empty tree. Bridges spec-to-reality gap. PM note: GROUPS_DEF has overlaps — need to confirm first-match heuristic or expose multi-attribution. | 6 LOC + PM decision on overlap |

### Trivial queue (≤5 lines, no PM judgment)

- **B23** — note popup wire (1 line)
- **B25** — theme-token swap (2 lines)
- **B27** — toggle-btn class adoption (3 lines)
- **B28** — `_treeDrill=null` on strategy switch (1 line)

### Non-trivial queue (backlog)

- **B20** (full-screen), **B21** (bucket→modal UX), **B22** (CSV), **B24** (persist), **B26** (palette unify), **D1** (enrichment + PM decision on GROUPS_DEF overlap)

---

## §8 — Verification checklist

- [x] Render path located (L2604)
- [x] Data fields mapped
- [x] Parser-side reverse-lookup verified for `subg` (factset_parser.py:544)
- [x] Week-selector awareness checked (§1.5)
- [x] Theme-token audit (§3)
- [x] Drill-parity with siblings (§2.1)
- [x] Shared-state traps (§2.3)
- [ ] Live-data spot-check (§1.4) — blocked, no loaded JSON
- [x] Phantom-spec flagged (§0)

---

## §9 — Final rating

**Data accuracy:        YELLOW** — numbers sound, but dead Group dimension + weighted-rank fallback quirk
**Functionality parity: YELLOW** — 4 parity gaps (no fullscreen, no bucket→modal, no note popup, no persist) + 1 dead control
**Design consistency:   YELLOW** — 3 token/palette drifts (B25, B26, B27)

**Overall: YELLOW.** The tile works and is information-dense, but it accumulates a cluster of low-to-medium debts that each sibling tile resolves individually. The single highest-leverage fix is **D1** (populate `h.subg`) — transforms a dead toggle into a differentiating feature.

---

## §10 — Proposed 3-line summary for CoS

> cardTreemap audit: YELLOW/YELLOW/YELLOW. Top finding = Group-by toggle silently dead (`h.subg` never populated, fix is 6 lines + PM call on GROUPS_DEF overlap). Trivial fix queue of 4 (note popup, theme tokens, toggle-btn class, `_treeDrill` reset); non-trivial queue of 6 (fullscreen, bucket→modal, CSV, palette unify, toolbar persist, D1).
