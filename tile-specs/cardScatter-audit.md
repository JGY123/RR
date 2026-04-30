# Tile Audit: cardScatter — "MCR vs TE Contribution"

> **Audit date:** 2026-04-30
> **Auditor:** Tile Audit Specialist
> **Dashboard:** dashboard_v7.html (9,937 lines)
> **Prior audit:** `cardScatter-audit-2026-04-21.md` (10 days ago) — many trivial fixes applied since.
> **Gold standard:** cardFacRisk (L1449–1458) + rFacRisk (L4063–4149).
> **Methodology:** 3-track audit (data accuracy / functionality parity / design consistency).

---

## VERDICT: YELLOW

The data path on the half-tile (`rScat`, L4831) is now defensible — `isFinite` filters, theme colors, `plotly_click → oSt`, no PNG button, CSV export, and zero-line are all present, closing roughly 80% of the prior trivial queue. **The full-screen sibling `renderFsScatter` (L9048) has not received the same polish** and now contains a fresh, severity-1 data accuracy bug introduced by the new Raw Factors merge. The half-tile is also still missing the cardFacRisk-style header pattern (subtitle + KPI strip + ⛶ button), drives no period awareness, and exposes none of the rich per-holding fields (`mcap/over/adv`) that just landed via the SEDOL merge.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | MCR vs TE Contribution |
| Card DOM id | `#cardScatter` (L1581) |
| Render fn | `rScat(s)` at L4831–4845 |
| Chart div | `#scatDiv` (320px, L1587) |
| FS opener | `openFullScreen('scatter')` at L1584; routed at L8966 |
| FS renderer | `renderFsScatter(s)` at L9048–9077 |
| FS panel helpers | `_renderFsScatPanel` L9079, `_fsScat_selectHold` L9122, `_renderFsHoldDetail` L9136 |
| Tab / row | Exposures, Row 7 (paired with cardTreemap, half-width) |
| CSV export | `exportScatCsv()` L4846 |

---

## 1. DATA ACCURACY — FINDINGS

### 1.1 [SEV-1] FS scatter color logic falls through to red (Q5) when `h.r==null` — CRITICAL BUG, NEW

**Location:** `renderFsScatter` at L9055.
```js
let colors=hold.map(function(h){return h.r===1?'#10b981':h.r===2?'#34d399':h.r===3?'#f59e0b':h.r===4?'#fb923c':'#ef4444';});
```
**Problem.** After the new Raw Factors layout (group_size=23) merge, `h.over` is null for ~23% of portfolio holdings (11 of 48 in GSC sample — verified against latest_data.json). `normalize()` at L812 only sets `h.r` when `h.over!=null`. Result: the chained ternary's final `else` returns the worst-case color (`#ef4444`, Q5 red) for every unranked holding.

A PM looking at GSC right now would see 11 holdings (mostly small-cap names like Wienerberger, Zealand Pharma) painted red as if they're worst-quintile, when their rank is simply unknown. Same bug is duplicated in two more places:
- `_renderFsScatPanel` L9091: `(h.r<=2?'#10b981':h.r===3?'#f59e0b':'#ef4444')` → undefined `h.r` returns red.
- `_renderFsHoldDetail` L9156: same expression, same bug.

**Proposed fix.** Branch `h.r==null` to a neutral grey (`#94a3b8` or `var(--textDim)`) **before** the rank-color ternary, in all three sites. ~3-line change. The half-tile `rScat` is not affected — it colors by `h.a` (active weight), not rank.

### 1.2 [SEV-2] Half-tile and FS use **different color encodings on the same dataset**

**Half-tile** (L4841): continuous diverging on `h.a` (active weight, red→grey→green), legend = "Active".
**FS** (L9055): discrete on `h.r` (5-color quintile), no legend.

This was flagged in the prior audit (B21) and remains. The PM who screenshots the tile thinking "colored by active weight" and pastes it into an email captioned that way is correct for the tile and wrong for the FS view of the same data. Pick one or expose a toggle.

### 1.3 [SEV-2] Per-holding data sources NOT being surfaced

After the SEDOL→Raw Factors merge, every `cs.hold[h]` portfolio entry now carries `h.mcap`, `h.over` (Spotlight rank), `h.rev/val/qual/mom/stab`, and `h.adv`. **None of these reach the scatter:**

- Bubble size on tile is `h.p*3` (port weight only). `h.mcap` would be a more PM-meaningful encoding ("are we taking risk on small or large names?").
- Hover (L4842) shows only ticker, MCR, TE — no sector, no rank, no mcap, no name.
- FS hover (L9062) shows only ticker, sector, MCR, TE, port. No rank, no mcap, no spotlight composite.
- The tile uses `h.t` for label — should use `tk(h)` (= `h.tkr_region||h.t`) per project helper at L651, otherwise raw SEDOL ids show up for unmapped holdings (e.g. `5699373` for Wienerberger AG instead of `WIE-AT`).

### 1.4 [SEV-3] Naming residue — "MCR" still in card title and X-axis label

Despite the prior audit's labeling-bug callout (B20), the card title at L1582 still reads "MCR vs TE Contribution" and the X-axis at L4843 says "Stock-Specific TE (MCR)". `h.mcr` is FactSet `%S` (stock-specific TE), not MCR (∂σ/∂w). The half-tile X-title at least leads with the correct term ("Stock-Specific TE"); the card title is the user-facing one and is misleading. The FS X-title at L9064 reads "MCR (Stock-Specific TE)" — same issue. This is a 3-line text edit but it's the single PM-confusing thing on the tile.

### 1.5 [SEV-3] `tk(h)` helper not used for label or hover ticker

The project ships `tk(h)=>h.tkr_region||h.t` (L651) precisely because raw `h.t` can be a SEDOL when no region-suffixed ticker is available. Both half-tile (L4840) and FS (L9061) use `h.t` directly. After the v2 merge, ~10% of hold rows in GSC have a SEDOL-shaped `t`. Use `tk(h)`.

---

## 2. FUNCTIONALITY PARITY — FINDINGS

### 2.1 [SEV-2] No KPI strip / subtitle — header is bare vs cardFacRisk gold standard

cardFacRisk (L1449–1458) uses the new pattern:
- Title + small subtitle ("exposure × risk · bubble = factor σ")
- KPI strip (`#facRiskKpi`) showing TE / Idio / Factor / Material count
- ⛶ button at right

cardScatter (L1581–1588) has only title + ⛶ + CSV. The whole row of "context numbers" (TE total, idio share, # holdings ≥ |TE| 1.0, top contributor) that PMs need to interpret the chart is absent. This is the highest-leverage parity gap: ~25 lines lifted from `rFacRisk`'s KPI builder (L4070–4087) would land it.

### 2.2 [SEV-2] No global Impact-period awareness

The dashboard now has a global `_impactPeriod` (L557) wired to a header dropdown (L377). cardFacRisk is point-in-time by design (snapshot), but cardFacButt (L4032+) computes period-aware avg exposure / TE contribution from `getAvgFieldForPeriod(...)`. cardScatter is currently snapshot-only with no period dimension.

PM-facing question: should this scatter become period-aware (avg `pct_t` over selected period) or stay as a snapshot? If snapshot, add a small "snapshot — latest week" subtitle to make the contract obvious; if period-aware, wire `getAvgFieldForPeriod(h.t, 'pct_t', _impactPeriod)`.

### 2.3 [SEV-3] No quadrant annotations / portfolio-average crosshair

cardFacRisk (L4121–4126) plus cardFacButt (L4025–4030) both place quadrant text and a crosshair on the chart. cardScatter has neither. The chart's whole point is to spot outliers — a crosshair at portfolio-mean (`mean(h.mcr)`, `mean(h.tr)`) would be one of the most informative additions. Phantom-spec B23 from prior audit, still un-shipped.

### 2.4 [SEV-3] Dual-ratio not surfaced anywhere

Per user standing order ("show dual ratios on sub-component breakdowns"): when drilling into a holding's TE, show **both** "% of TE" AND "% of Idio". cardFacRisk hover (L4103) does this for factors:
```
TE Contrib: ${...% of TE} · ${...% of Factor}
```
cardScatter half-tile hover and FS hover both show only `pct_t` in absolute % (e.g. "TE Contrib: 0.6%"). Should be: `0.6% of TE · 1.2% of Idio` (numerator over `cs.sum.pct_specific*cs.sum.te/100`).

### 2.5 [SEV-3] FS panel still has hardcoded slate hex throughout (`#0f172a / #334155 / #94a3b8 / #e2e8f0 / #64748b`)

Lines 9087–9098, 9152–9159. Light-theme-hostile. Same gap flagged in the prior audit at §6.6 — not fixed.

### 2.6 [SEV-4] FS panel table has no `<table id>`, no sortable headers, no CSV button

Compare cardFacButt FS modal which builds a sticky-header sortable table (L4244+). FS panel is read-only stripped HTML.

---

## 3. DESIGN CONSISTENCY — FINDINGS

### 3.1 Header pattern doesn't match new gold standard

The card-title row at L1581–1586 lacks:
- `<span style="font-size:10px;color:var(--textDim);margin-left:8px;font-weight:400">…</span>` subtitle (used by cardFacRisk L1532, cardFacButt L1546).
- KPI strip below the title (cardFacRisk uses `#facRiskKpi`).
- The ⛶ button is the small-old-style (`background:none;border:1px solid var(--grid)`, L1584) rather than the project's `export-btn` class (cardFacRisk L1535 uses `class="export-btn"`).

### 3.2 Bubble size scaling diverges between tile and FS

- Tile (L4841): `Math.max(h.p*3, 6)` — linear.
- FS (L9054): `Math.max(Math.sqrt(h.p)*9, 5)` — sqrt.

cardFacRisk (L4095) and cardFacButt (L3994) both use `Math.max(14, Math.min(56, Math.sqrt(d)*9+10))`. Adopt the bounded sqrt pattern in both rScat and renderFsScatter for visual parity and outlier protection (currently a single 30%-weight holding can dominate the tile chart).

### 3.3 Hover label styling diverges

cardFacRisk uses `hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:'#475569',font:{color:'#f1f5f9',size:11,family:'DM Sans'}}` (L4133). rScat uses Plotly default. The dark project hoverlabel is more readable on a dark tile.

### 3.4 Tooltip provenance ("source:") tags absent

Per recent design lead direction: hover tooltips should include a "source: cs.hold[].pct_t" provenance line so PMs can trace numbers. cardFacRisk hover does this implicitly via the dual-ratio. cardScatter hover has no provenance — a PM seeing 0.6% TE Contrib has no way to know if that's `%T` (FactSet column) or a derived metric.

### 3.5 Text labels at size:9 still below project floor in some renders

L4840 reads `textfont:{size:9, ...}`. Project floor is 9 per AUDIT_LEARNINGS — at the floor, OK. But on tiles with 100+ holdings (IDM has ~450 portfolio holdings; ISC ~280), label soup remains. No top-N thinning. Phantom-spec B25 not yet addressed.

### 3.6 Inline `staticPlot:false` override on FS

L9068: `Object.assign({},plotCfg,{staticPlot:false})`. `plotCfg` already has no `staticPlot`. Dead override.

---

## 4. PROPOSED FIXES (PRIORITIZED, MAX 5)

| # | Severity | Effort | Description |
|---|---|---|---|
| **F1** | SEV-1 | 3 lines × 3 sites = ~9 lines | **Fix the FS rank-color fall-through.** In `renderFsScatter` L9055, `_renderFsScatPanel` L9091, `_renderFsHoldDetail` L9156: branch `h.r==null` to neutral grey (`#94a3b8`) before the rank ternary. Stops 23% of GSC portfolio holdings being painted as Q5 worst when their rank is unknown. **Critical — wrong data is going to a PM screen right now.** |
| **F2** | SEV-2 | ~30 lines | **Adopt the cardFacRisk header pattern.** Add subtitle ("snapshot · bubble = port wt · color = active wt"), KPI strip below title with cards for: TE total, Idio (% of TE + MCR), # holdings with `\|tr\|>1.0`, top contributor ticker. Lift the KPI builder skeleton from rFacRisk L4083–4087. Drops the tile from "label-with-chart" to a real summary tile. |
| **F3** | SEV-2 | ~5 lines per hover (×2) | **Enrich hover with provenance + dual ratio.** Replace the half-tile hovertemplate (L4842) and FS hover (L9062) with a multi-line layout matching cardFacRisk style: `<b>${tk(h)}</b><br>${h.n}<br>Sector: ${h.sec} · Rank: ${h.r??'—'}<br>Stock-Spec TE: ${pct_s}% (${dual} of Idio)<br>TE Contrib: ${pct_t}% (${dual} of total TE)<br>Port: ${p}% · Active: ${a}σ · Mcap $${mcap}M`. Use `tk(h)` for ticker. Dual-ratio uses `cs.sum.pct_specific` and 100 as denominators. |
| **F4** | SEV-2 | ~15 lines | **Rename "MCR" → "Stock-Specific TE" in user-visible strings.** Card title L1582 ("Stock-Specific TE vs TE Contribution"), card-title `data-tip` L1582 (already correct, leave), X-axis L4843 (drop the parenthetical "(MCR)"), FS X-axis L9064 ("Stock-Specific TE Contribution"), CSV header L4849 (already correct). One word everywhere; matches CLAUDE.md's `%S` definition. |
| **F5** | SEV-3 | ~30 lines | **Add quadrant annotations + portfolio-average crosshair.** Lift the `shapes`/`annotations` arrays from rFacRisk (L4113–4126) and adapt: x=mean(`h.mcr`), y=mean(`h.tr`); quadrant labels = "High idio · drives TE", "Low idio · drives TE", "High idio · doesn't matter", "Low idio · doesn't matter". This is the long-promised phantom-spec feature and the single biggest interpretability win. |

**Out of scope for this round (next backlog):** period awareness (sev-3, ~50 lines, PM-decision question first), bubble-size by mcap toggle (PM call), label thinning to top N by `|tr|`, FS panel sortable table + theme colors.

---

## 5. CARRY-OVER FROM PRIOR AUDIT

- **Closed:** isFinite filter (now L4833), theme colors via `--pos/--neg/--txt` (L4835–4837), `plotly_click → oSt` (L4844), PNG button removal, CSV export (L4846), X-axis zero-line (L4843), bubble opacity 0.8 (L4841).
- **Still open:** F1–F5 above. B21 (color-semantic drift), B23 (quadrant + crosshair), B25 (label thinning), B26 (FS panel primitives), B27 (shared `RANK_COLORS` helper) all remain.
- **New (introduced by Raw Factors merge, 2026-04-30):** F1 — the rank-color regression is a direct consequence of the new merge populating `h.over` for only matched SEDOLs.
