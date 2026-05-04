# Tile Spec: cardWeekOverWeek — Audit v1 (S1 follow-up)

> **Audited:** 2026-05-04 | **Auditor:** Tile Audit Specialist
> **Scope:** First formal audit since shipping 2026-04-30 (S1 strategic recommendation). Three-track standard.
> **Status:** **YELLOW — SHIPPABLE WITH FIXES.** No RED blockers. 3 YELLOW (chrome on empty branches; factor rotation not hist-aware; dropped-row drill silently no-ops). Several GREEN polish items.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| Tile name | Week over Week |
| Card DOM id | `#cardWeekOverWeek` (Exposures tab, rendered by `rExp()` line 2989) |
| Render fn | `rWeekOverWeek(s)` at `dashboard_v7.html:2764–2912` |
| CSS classes | `.wow-kpis .wow-kpi .wow-cols .wow-col .wow-row .wow-fac-rot .wow-fac-cell .wow-empty` (lines 382–420) |
| About entry | `_ABOUT_REG.cardWeekOverWeek` at line 1155–1162 |
| Click drill | `oSt(SEDOL)` per row |
| Data sources | `s.hist.sum[]` (KPIs), `s.hold` + `s.hold_prev` (move list), `s.snap_attrib[name].hist` (factor rot) |
| Per-week accessors | None — direct `s.hist.sum`, `s.hold`, `s.hold_prev`, `s.factors`, `s.snap_attrib` |
| Tab / Width / Full-screen | Exposures (top of tab) / Full-width / Generic clone fallback |
| Spec status | `audit-only` — coordinator serializes any code fixes |

---

## 1. Data Accuracy — Track 1

### 1.1 KPI strip — VERIFIED (GREEN)

Spot-check on `em_full_history.json` (EM, 383 weekly entries):

| Field | summary[-2] (`20260424`) | summary[-1] (`20260430`) | Δ shown | Match |
|---|---|---|---|---|
| TE | 5.39 | 5.51 | +0.12 | ✅ |
| AS | 68.54 | 68.92 | +0.38 | ✅ |
| Beta | 1.04 | 1.04 | ±0.00 | ✅ |
| Holdings | 40 | 40 | 0 | ✅ |

Source: parser ships as `hist.summary`; normalize layer (line 1907) renames to `hist.sum`. No fabrication.

### 1.2 Move list — VERIFIED (GREEN)

Hand-replicated on EM (40 port-held curr, 40 prev): added=0, dropped=0, resized (|Δwt|≥0.10%)=18, top resize BMXNYN0 +0.90%. SEDOL keying via `h.t` (parser line 793). `hold_prev` slim subset `{t,n,w,bw,aw,pct_t,pct_s}` (parser line 1171–1183) — sufficient.

### 1.3 Resize threshold — CONFIRMED (GREEN)

`WOW_RESIZE_THRESH = 0.10` (% absolute). Display label "Δwt threshold: 0.10%" in chrome `extra` slot. Documented in About registry (line 1160).

### 1.4 Factor rotation math — VERIFIED (GREEN)

`facRot` reads `(s.snap_attrib[name]||{}).hist[-1]` vs `[-2]`, computes `Δactive = (exp - bench_exp)[t] - [t-1]`. snap_attrib hist cadence is weekly (parser line 959). Top 3 by `|Δexp|`, sparkline of last 12 weeks. Edge cases: `null` exp/bench_exp → falls back to `f.a` for current, drops factor if `null` for prev. (See F2 below for unwired `_selectedWeek`.)

### 1.5 Anti-fabrication audit (per LESSONS_LEARNED.md) — PASS

- Empty `hold_prev` → empty-state banner. No synthesis.
- `hist.length < 2` → empty-state banner.
- Null factor exp/bench_exp → factor dropped from ranking, never zero-stamped.
- KPI delta on `null` source → label `'—'`, class `wow-delta-flat`.

**No fabrication patterns detected.**

---

## 2. Functionality Parity — Track 2

### 2.1 Chrome strip (post-Phase D)

| Capability | Standard | Populated branch | Empty branches | Gap |
|---|---|---|---|---|
| About (ⓘ) | yes | ✅ via tileChromeStrip | ✅ inline `aboutBtn` | — |
| CSV (⬇) | per-table | ❌ no exporter | n/a | F4 |
| Reset View (↺) | yes | ❌ omitted | ❌ omitted | F1 |
| Hide (×) | yes | ✅ | ❌ omitted | F1 |
| Full Screen (⛶) | yes | ✅ generic clone | ❌ omitted | F1 |
| Right-click → note | yes | ✅ | ✅ | — |

### 2.2 Auto-update on week selection — VERIFIED (GREEN)

Wiring: `changeWeek(date)` → `_selectedWeek = date` → `_withScrollPreserved(upd)` → `upd()` → `rExp()` → `rWeekOverWeek(s)`. Inside renderer, `_selectedWeek` is honored at lines 2784–2797: KPI strip uses `hist[idx]` vs `hist[idx-1]`, sets `isHist=true`, title appends "· historical" warn-color tag.

### 2.3 Row tooltip disambiguator — VERIFIED (GREEN)

Line 2837: `title="${nmFull} · ${tk}${h.sec? ' · '+h.sec:''}"` with HTML-escape on quotes. Matches the 2026-05-01 Kongsberg fix (full name + ticker + sector for similarly-named issuers).

### 2.4 Drill click on dropped rows — YELLOW (F3)

Each row has `onclick="oSt('${escT}')"`. `oSt(ticker)` (line 9933) does `cs.hold.find(x => x.t === ticker)` and silently `return`s when no match. For DROPPED rows the SEDOL is in `hold_prev` but may not be in `hold` (zero in EM sample, but latent for fully-exited names not in benchmark). Click looks affordant but does nothing.

### 2.5 Factor rotation `_selectedWeek` wiring — YELLOW (F2)

Lines 2858–2885 hard-wire `s.factors` (latest) + `hist[-1]`/`[-2]` regardless of `_selectedWeek`. Currently hidden in hist mode (line 2891 ternary) rather than re-pointed at the selected week. Trivially fixable using KPI block's `idx`/`prev` pattern.

### 2.6 Comparison to benchmark tiles

Sortable / filterable / column picker / view toggle all reasonably n/a (curated top-N display, not a table). CSV export is the lone parity gap (F4).

---

## 3. Design Consistency — Track 3

### 3.1 Design token adoption (Phase K, 2026-05-01)

WoW CSS pre-dates the `--space-*` / `--text-*` tokens. Selected mismatches:

- `.wow-kpi padding:10px 14px` → off-scale (closest tokens: 8px / 12px / 16px)
- `.wow-kpi-val font-size:20px` → off the type scale (`--text-2xl`=18, `--text-3xl`=22)
- `.wow-kpis gap:10px;margin-bottom:14px` → off-scale (8/12/16)
- `.wow-row padding:5px 0` → off-scale (4/6)
- `.wow-kpi-label / .wow-col-h font-size:11px;letter-spacing:1px` → uses `--text-md` ✅ but letter-spacing not canonical (canonical 0.6px in `.section-label`)
- `.wow-col padding:12px;border-radius:8px` → both on token scale ✅

### 3.2 `.empty-state` adoption — D1

Three `.wow-empty` instances (lines 2774, 2791, 2892) duplicate canonical `.empty-state` (added Phase K). Functionally similar but missing flex-column + `.empty-state-hint` structure. Migration: replace divs and delete `.wow-empty` rule (line 419).

### 3.3 `.section-label` adoption — D2

`.wow-kpi-label` and `.wow-col-h` reimplement `.section-label` (uppercase, dim, semibold, letter-spaced). Consolidate via class composition.

### 3.4 Color semantics — VERIFIED with one caveat

- KPI delta colors: up=red(neg), down=green(pos). For TE this is correct (up=more risk). For Beta/AS/Holdings, the `riskMode:'neutral'` is intended but unused — see C1.
- Resize hbar `pos`/`neg` SVG: positive Δwt → red ✅ (PM convention: position increase = leaning into risk).
- Factor rotation arrow: up=red, down=green. As with MCR (cf. `feedback_mcr_no_percent.md`), applying risk colors to non-risk metrics is debatable — worth PM ratification.

---

## 4. Findings Summary

### RED (blockers): NONE

### YELLOW (close before next signoff)

| # | Finding | Proposed fix |
|---|---|---|
| **F1** | Empty-state branches (lines 2770–2776, 2787–2793) skip `tileChromeStrip` — only `aboutBtn` rendered. Inconsistent with populated state. | Add `${tileChromeStrip({id:'cardWeekOverWeek', about:true, hide:true, fullscreen:"openTileFullscreen('cardWeekOverWeek')"})}` to both empty branches. |
| **F2** | Factor rotation hard-wired to latest week. Hidden in hist mode rather than re-targeted. | Reuse KPI block's `idx`/`prev` pattern: find `_selectedWeek` in `fhist`, slice `hist[idx]`/`hist[idx-1]`. Drop the hist-mode hide on `facRot`. |
| **F3** | Dropped-row drill: `oSt(SEDOL)` silently returns when SEDOL not in `cs.hold`. Affordant click does nothing. | Either skip `onclick` for `mode==='dropped'` rows + `cursor:default`, OR fall back `oSt` to `cs.hold_prev.find(...)`. (a) is simpler. |

### GREEN (polish, ship-when-convenient)

| # | Finding | Proposed fix |
|---|---|---|
| C1 | `_wowDelta()` `riskMode` parameter has no effect — both branches return identical class mapping (lines 2759–2760). | Either delete the unused param (current behavior: all-risk-semantics) OR implement neutral branch as `var(--txt)`. **Needs PM decision.** |
| F4 | No CSV export. | Add `exportWowCsv()` + `csv:` slot in chrome strip. |
| D1 | `.wow-empty` duplicates `.empty-state`. | Replace 3 instances; delete CSS rule. |
| D2 | `.wow-kpi-label` / `.wow-col-h` reimplement `.section-label`. | Class composition + collapse rules. |
| D3 | KPI value font-size 20px off the type scale. | Pick `--text-3xl` (22px). |
| D4 | Sparkline color in factor rotation uses `mkSparkline`'s auto-trend (positive trend → green) which conflicts with the WoW arrow logic (positive Δexp → red). Two conventions in the same row. | Pass explicit color into `mkSparkline(f.tail, 80, 18, color)` matching the arrow's direction class. |

---

## 5. Verification Checklist

- [x] Data accuracy verified (KPI deltas + move list spot-checked on EM)
- [x] Edge cases handled (empty hold_prev, single-period file, hist[idx]<=0 first-week)
- [x] Anti-fabrication policy honored (no synthesis on missing values)
- [x] Auto-update on week selector (end-to-end verified)
- [x] Row tooltip carries name + ticker + sector (Kongsberg fix shipped)
- [ ] Empty-state branches carry full chrome (F1)
- [ ] Factor rotation hist-aware (F2)
- [ ] Dropped-row drill safe (F3)
- [ ] CSV export (F4)
- [ ] `.empty-state` / `.section-label` adoption (D1, D2)
- [ ] No console errors (needs in-browser pass)

---

## 6. Sign-off Recommendation

Coordinator should land **F1 + F3** before next user-review pass — both short, low-risk, parity-restoring. **F2** is a feature ask; queue with PM. C1, F4, D1–D4 are polish; ship as a Phase K sweep.

**Status: YELLOW.** No data-integrity issue, no fabrication, no missing functionality blocking the core "what changed this week" question. YELLOW items close the parity gap with neighboring tiles after the chrome-strip standardization.

---

## 7. Fix Queue (for coordinator)

**TRIVIAL (agent can apply, ~5–15 lines each):**
- F1 (empty-branch chrome) — copy the `tileChromeStrip` call into both empty branches.
- F3 (dropped-row drill safety) — add `mode==='dropped'?'':onclick` guard in `rowHtml`, set `cursor:default`.
- D1 (empty-state class) — swap `.wow-empty` → `.empty-state`, delete CSS rule.

**NEEDS PM DECISION:**
- C1 — neutral coloring on Beta/AS/Holdings deltas, or current "all-risk-semantics"?
- D4 — sparkline color: match arrow direction or keep mkSparkline auto-trend?

**LARGER (queue with next feature ask):**
- F2 (factor rotation hist-aware) — ~20 lines; needs multi-week file test.
- F4 (CSV export) — new exporter helper + `csv:` slot.

**BLOCKED:** none.
