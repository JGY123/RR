# Tile Audit: cardRiskByDim — 2026-05-04

> **Auditor:** Tile Audit Specialist (subagent run for Tier-2 B102)
> **Scope:** Risk by Dimension — TE contribution decomposed by Country / Currency / Industry on the Risk tab
> **Overall:** **YELLOW** — aggregation logic clean, chrome + design in tight parity with peers. One **RED** on data-scale provenance (Σ%T ≠ 100% across every strategy, contradicting CLAUDE.md), three **YELLOW** UX/transparency items.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Card / render | `#cardRiskByDim` 7879–7900; `rRiskByDim(s)` 8440–8520; aggregator `aggregateRiskByDim` 8417–8438 |
| Drill / CSV | `oDrRiskByDim` 8524–8603 (reuses `#metricModal`); `exportRiskByDimCsv` 8606–8616 |
| Plot id / footer | `#rbdChartDiv` (dynamic height max(220, n×22+80)px); `#rbdFooter` 10px dim |
| Chrome | `tileChromeStrip({id:'cardRiskByDim', resetZoom:'rbdChartDiv', csv:'exportRiskByDimCsv()', fullscreen:..., resetView:true, hide:true})` (7895). About inline at 7883 (outside strip). |
| State | `_rbdDim` localStorage `rr.cardRiskByDim.dim` (default `country`); `_rbdThresh` localStorage `rr.cardRiskByDim.thresh` (default `0.5`%) |
| Right-click note | wired; About registry complete (1245–1252, 5 fields) |
| Data source | `cs.hold[].tr` (renamed from `pct_t` in normalize 1878), grouped by `h.country` / `h.currency` / `h.industry` |
| SOURCES.md | section "cardRiskByDim …" 140–152 — present, accurate |

---

## 1. Data Accuracy — Track 1

### 1.1 Aggregation correctness — VERIFIED

```js
s.hold.forEach(h => {
  if (isCash(h)) return;
  const tr = +h.tr || 0;
  let key = h[field] || 'Unmapped';
  map[key] ||= {n:key,total_tr:0,count:0,unmapped:key==='Unmapped'};
  map[key].total_tr += tr;
  map[key].count   += 1;
});
```

Each holding contributes its `pct_t` to exactly one bucket per dim. No double-count. Cash excluded consistently in aggregator (8423) and drill (8529). Threshold filter at 8458 (`b.abs_tr >= _rbdThresh`); hidden buckets reported in footer.

**IDM spot check (cs.sum.te = 6.47, 775 holdings, no SEDOL dups):**

| Country bucket | Σ pct_t | N | | Currency | Σ pct_t | N |
|---|---|---|---|---|---|---|
| Japan | +40.2 | 181 | | EUR | +45.4 | 218 |
| Netherlands | +24.5 | 24 | | JPY | +40.2 | 181 |
| Germany | +13.4 | 54 | | GBP | +7.9 | 72 |
| United Kingdom | +7.9 | 71 | | CAD | +7.4 | 81 |
| Canada | +7.4 | 81 | | AUD | -0.4 | 46 |

Python recomputation matches the JS-side aggregator byte-for-byte. Currency sums by SEDOL-keyed `h.currency` (security_ref enrichment, ~99% coverage).

### 1.2 Field provenance

| Field | Source | Class | Notes |
|---|---|---|---|
| `h.tr` | parser `pct_t` (FactSet `%T`) → normalize 1878 | sourced | raw passthrough |
| `h.country` / `h.currency` / `h.industry` | `data/security_ref.json` SEDOL lookup | derived | 97–99% coverage; Unmapped breakout w/ `⚠` chip in footer |
| Bucket sum | local `Σ h.tr` | derived | transparent — no fabricated synthesis |

### 1.3 Cross-strategy reconciliation — RED

User's stated sanity check: *"sum of all bars should match cs.sum.te approximately (~100% × te if no double-count)"*. CLAUDE.md line 108: `%T = sums to ~100%`.

| Strategy | te | **Σ h.pct_t** | Σ h.pct_s | N |
|---|---|---|---|---|
| IDM | 6.47 | **115.9** | 62.6 | 775 |
| IOP | 7.11 | **134.4** | 52.6 | 1,703 |
| EM | 5.51 | **94.6** | 60.0 | 914 |
| ISC | 6.25 | **107.0** | 70.6 | 2,209 |
| ACWI | 6.65 | **125.3** | 56.2 | 2,048 |
| GSC | 6.98 | **109.8** | 68.7 | 1,002 |

Range **94.6 → 134.4** — ±35% deviation from documented ~100%. **Aggregation is correct; the upstream data does not satisfy the stated invariant.** User-visible consequences:

- Footer `total |TE| coverage = 116%` looks suspicious to a PM.
- Hover `TE Contribution: %{x:.2f}%` reads as "share of portfolio TE", but if all bars sum to 116% the interpretation is broken.
- Cross-strategy comparison ("Japan = 40% of IDM TE") cannot be normalized.

This is upstream (parser or FactSet itself), not a cardRiskByDim bug. See **D1** for fix.

### 1.4 Threshold slider, edge cases — VERIFIED

- Slider 7893: `min=0 max=3 step=0.1 value=0.5`. `setRiskByDimThresh` (8408) parses, persists, re-renders. Below-threshold rollup `N hidden below X% (Y% combined)` in footer.
- Empty: 8441 → "No holdings data". All-below-threshold: 8473 → "No buckets above X% — try lowering the slider".
- Sign coloring: positive (adds risk) red `--neg`; negative (diversifies) green `--pos`; |v|<0.05 gray `--textDim` (8486). Sign-aware text label (`+` prefix).
- Unmapped chip `⚠` appended at 8480; click handler strips before drilling (8515). ✅
- Cash: filtered via `isCash(h)` in both aggregator and drill — consistent with siblings.

### 1.5 RED / YELLOW data findings

**D1. RED — Σ%T ≠ 100% across all 6 strategies.**
*Fix sequence:*
- (a) Investigate upstream — confirm with FactSet whether `%T` truly should sum to 100. CLAUDE.md may be aspirational; FACTSET_FEEDBACK.md should log the question.
- (b) **Defensive UI today**: relabel footer `total |TE| coverage` → `Σ |bucket TE| (absolute, not normalized)` so it reads truthfully.
- (c) Add a second footer entry: `Σ %T = 115.9 (FactSet %T should ≈ 100; deviation noted in FACTSET_FEEDBACK)`.

**D2. YELLOW — `agg.totalTr` computed but never displayed in chart footer.**
8421/8437 returns `totalTr`; CSV uses it (8612), but the chart footer recomputes `Σ |b.total_tr|` independently. Two coexisting "totals". *Fix:* show both signed and absolute sums in footer.

**D3. YELLOW — Drill modal lacks bucket-vs-portfolio share.**
Per the user's literal ask ("when security has 2% contribution from country, see which countries"), the drill should headline "Japan = +40.2% of portfolio TE-contrib (across 181 holdings)". Currently shown is only a "% of bucket" share for the top contributor. *Fix:* add a stat card or inline subtitle.

---

## 2. Functionality — Track 2

### 2.1 Chrome inventory — full parity

| Capability | Present | Notes |
|---|---|---|
| About (ⓘ) | yes | inline 7883 (outside strip, by pattern) |
| Reset Zoom / Reset View / Hide / Full Screen | yes | via tileChromeStrip 7895 |
| CSV | yes | `exportRiskByDimCsv` 8606 |
| Right-click note | yes | 7882 |
| PNG | none | per `feedback_no_png_buttons.md` — correct |
| Cols picker | n/a | chart, not table |

### 2.2 Pill toggle / drill / CSV — VERIFIED

- `setRiskByDim(dim)` validates against `RBD_DIM_LABELS`, persists, re-renders. Active class toggle 8447–8450. ✅
- `plotly_click` (8511) strips `⚠` chip → `oDrRiskByDim`. Modal renders 8 stat cards + securities table sorted by |tr| desc. Stock rows clickable via `oSt(t)`.
- CSV: `<DimLabel>,Holdings count,Total TE contrib %,Unmapped` rows + Total row. **F1 YELLOW**: Total row uses `cs.hold.length` (incl. cash) but bucket aggregator excludes cash → off-by-cash-count. *Fix (one-liner):* `cs.hold.filter(h=>!isCash(h)).length`.

### 2.3 Universe pill (B116) — correctly omitted

cardRiskByDim does NOT subscribe to universe-pill state. Confirmed by inspection — no `_uni` reads, no `_rerenderAggTiles` registration. Per B116, TE contributions are universe-invariant. **F2 YELLOW**: extend `_ABOUT_REG.cardRiskByDim.caveats` with: *"Universe pill (Port-Held / Bench-Only / All) does not affect this tile — TE contributions are universe-invariant by FactSet definition."*

---

## 3. Design — Track 3

### 3.1 Tokens & typography — clean

- `.card-title` (11px uppercase, letter-spacing 1.5px). ✅
- "Dim" / "Min" labels use `.section-label` — matches cardCountry, cardWatchlist etc. ✅
- Threshold readout `font-family:'JetBrains Mono'` + `min-width:32px` — tabular align. ✅
- Footer 10px var(--textDim) text-right — matches sibling tile convention. ✅
- Color semantics inverted from OW/UW (red = adds-risk, green = diversifies) — justified, About copy clarifies. ✅

### 3.2 Bar chart visuals — clean

Horizontal bars sorted ascending so largest |TE| at top. Outside-text labels at 10px. Hover template clean. Dynamic left margin for long bucket names. Bold zero-line (`zerolinewidth:2`). Bargap 0.25. ✅

### 3.3 RED / YELLOW design findings

**G1. YELLOW — pill cluster lacks chip-card wrapper.**
Lines 7888–7890 use bare `<button class="pill">`. cardCountry's analogous Top-N cluster (3133) wraps in `<span style="…background:var(--surf);border:1px solid var(--grid);border-radius:8px;padding:3px 6px">`. *Fix (cosmetic, ~2 lines):* wrap Dim+Min in matching chip-card spans.

**G2. YELLOW — slider lacks "show all" / "PM-default deep" presets.**
Continuous 0–3% slider; PMs typically toggle between "show all" and "material-only". *Fix (additive, 4 lines):* preset buttons (`0%` / `0.5%` / `1%`) flanking the slider, calling `setRiskByDimThresh(N)`.

**G3. GREEN — Empty/no-bucket states styled consistently with siblings.**

---

## 4. Verification Checklist

- [x] Aggregation correct per dim (verified vs Python recompute)
- [x] Edge cases handled (empty, single bucket, all-below-threshold, unmapped, cash)
- [x] Threshold slider + pill toggle persist via localStorage
- [x] Click → drill modal correct; CSV export correct structure
- [x] Full-screen / Reset / Hide all wired via chrome strip
- [x] Right-click note + About registry complete
- [x] Universe-pill correctly NOT applied (B116)
- [ ] **Σ %T sums close to 100%** — fails for all 6 strategies (D1)
- [ ] Footer label is unambiguous (D1b)
- [ ] CSV total row excludes cash (F1)

---

## 5. Open Questions (data-validator / PM)

1. Is FactSet's %T meant to sum to 100% per portfolio? CLAUDE.md says yes; data shows 94→134%. Owner: data-validator + FactSet team email.
2. Should the "Unmapped" bucket be visible above threshold, or always shown when N>0? Currently treated like any other bucket.
3. Add a 4th pill for **Region**? `h.reg` already exists in security_ref. 4-line change. Proposal — needs PM nod.

---

## 6. Fix Queue

**TRIVIAL (agent can apply, ≤5 lines each):**
- D1b — relabel footer total to "Σ |bucket TE| (absolute)"
- D1c / D2 — show both signed `agg.totalTr` AND absolute `Σ|b.total_tr|` in footer
- F1 — exclude cash from CSV "Total" row count
- F2 — append universe-invariance caveat to About-registry
- G1 — wrap Dim+Min controls in matching chip-card spans

**NEEDS PM DECISION:**
- D1a — investigate Σ%T scale; escalate to FactSet
- D3 — bucket-share-of-portfolio in drill modal
- G2 — preset buttons flanking threshold slider
- Open-Q #2 — Unmapped visibility policy
- Open-Q #3 — add Region as 4th dimension

**BLOCKED:** none.

---

> Tile audit complete. **YELLOW** — fully functional, design-compliant; one upstream data-scale question (D1) merits a PM/FactSet conversation before final signoff.
