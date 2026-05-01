# Tile Spec: cardCorr — Audit v2 (post-promote)

> **Audited:** 2026-05-01 | **Auditor:** Tile Audit Specialist
> **Scope:** Re-audit of `cardCorr` after the 2026-04-30 promote-to-first-class (commit `819c493`). Pre-presentation gate (<4 hours).
> **Status:** **YELLOW — SAFE FOR PRESENTATION**, with one math defect that should be disclosed verbally and one cosmetic default-checkbox miss. No RED blockers.
> **Prior audit:** `cardCorr-audit-2026-04-23.md` — superseded for items B62, B64, B66, B67, B69, B70, B71, B72, B73, B74, B75, B76 (now closed). New finding C1 (monthly dedupe bug) raised.

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Factor Correlation Matrix |
| **Card DOM id** | `#cardCorr` (Risk tab, line 6946) |
| **Render function** | `rUpdateCorr()` at `dashboard_v7.html:4828–4967` |
| **CSV exporter** | `exportCorrCsv()` at `dashboard_v7.html:4968–4984` |
| **About entry** | `_ABOUT_REG.cardCorr` at `dashboard_v7.html:1045–1052` |
| **Inner plot id** | `#corrHeatPlot` (h scales `260 + 36/factor`) |
| **Controls** | `#corrPeriod`, `#corrFreq`, `#corrFactorSel` checkbox strip, CSV button, Reset Zoom (`⤾`), About (`ⓘ`) |
| **Right-click → note** | wired (`oncontextmenu="showNotePopup(event,'cardCorr')"`) |
| **Data source** | `cs.snap_attrib[name].hist` (per-factor weekly active-exposure history). `cs.hist.fac` is checked first as legacy path, but is empty in current samples — the snap_attrib fallback (lines 4870-4878) is the live path. |
| **Tab** | Risk |
| **Width** | Full-width |
| **Full-screen path** | None (B68 still open — non-blocker for presentation) |
| **Drill path** | None on cells; insight bullets click through to `oDrF(factorName)` (B74 closed) |
| **Spec status** | `audit-only` — coordinator serializes any code fixes |

---

## 1. Data Accuracy — Track 1

### 1.1 Pearson math — VERIFIED against numpy.corrcoef on EM full history

Live-data spot check on `em_full_history.json` (EM, 139 factors, 383 weekly observations 2019-01-04 → 2026-04-30):

| Factor pair | n | dashboard r | numpy r | match |
|---|---|---|---|---|
| Volatility × Value | 383 | -0.234 | -0.234 | ✅ |
| Growth × Medium-Term Momentum | 383 | 0.361 | 0.361 | ✅ |
| Profitability × Earnings Yield | 383 | 0.259 | 0.259 | ✅ |

1Y-weekly window (52 obs — the user's preferred default per R2-Q12):

| Pair | dashboard r | numpy r | match |
|---|---|---|---|
| Volatility × Value | -0.859 | -0.859 | ✅ |
| Growth × Medium-Term Momentum | 0.317 | 0.317 | ✅ |
| Profitability × Earnings Yield | -0.927 | -0.927 | ✅ |

**Pearson math is correct.** The local implementation at lines 4900–4909 mirrors numpy to ≤0.001 precision across all tested pairs and windows. **GREEN.**

### 1.2 Edge-case handling

| Scenario | Code path | Status |
|---|---|---|
| `cs.hist.fac` empty | Fallback to `snap_attrib` synthesis at L4870-4878 | ✅ GREEN — works, kept legacy compatibility |
| All factors empty | "No factor history available" at L4879 | ✅ GREEN |
| <2 selected factors | "Select at least 2 factors" at L4883 | ✅ GREEN |
| <3 obs in any factor | Filtered out at L4898 (B75 closed) | ✅ GREEN |
| Insufficient overall (`minLen<3`) | Banner at L4912 | ✅ GREEN |
| Zero-variance factor | `pearson` returns `null`, cell renders "—" (B62 closed) | ✅ GREEN |
| `n<3` | `pearson` returns `null` (B62 closed) | ✅ GREEN |
| Self-correlation `f===f` | Hardcoded `1` at L4916 | ✅ GREEN — correct |
| `null` / missing `exp` value | Falls through to `+(h.e\|\|0)` → 0.0 | ⚠️ YELLOW — verified 2638 null `exp` values exist across all factor histories in EM. They are silently coerced to 0, biasing Pearson toward the mean for any factor with sparse history. Same flavor as the cardFacDetail sparkline pattern (logged in prior audit). Non-blocker for presentation. |

### 1.3 NEW FINDING — C1 — Monthly dedupe is broken (math defect, low blast radius)

**Severity: YELLOW.** Code at line 4893:
```js
if(freq==='monthly'){
  let seen=new Set();
  arr=arr.filter(h=>{let m=h.d.slice(0,7);if(seen.has(m))return false;seen.add(m);return true;});
}
```

The `d` field has format `YYYYMMDD` (no hyphen separator — confirmed in EM data: e.g. `'20190104'`). `slice(0,7)` therefore produces `'2019010'` (year + month + first digit of day-of-month). This creates 3-4 buckets per calendar month instead of 1.

**Empirical impact on EM data (Volatility series):**
- Weekly observations: 383
- Buggy "monthly" dedupe keeps: **283** (74% — barely a dedupe)
- Correct `[:6]` dedupe would keep: **88** (one per month, as intended)

**r-value impact (Volatility × Value, all-period):**
- Weekly r = -0.234
- Buggy "monthly" r = -0.231
- Correct monthly r = -0.227

The math drift is small (0.004 in this sample) because the buggy dedupe just removes a roughly-random subset of weekly obs. **The user toggling Weekly→Monthly will see r values change by ~0.005, not the substantial change they'd expect from true monthly resampling.**

**Why YELLOW not RED:**
- Math is "wrong but close to weekly," not "fabricated."
- All 88 true-month observations are used (just augmented with 195 extra mid-month weekly obs).
- Insight bullets and heatmap colors are visually unchanged from weekly mode.

**Why disclose verbally:**
- If the PM clicks "Monthly" expecting smoother (lower-frequency) correlations, what they get is essentially weekly with light dedupe. The advertised feature does not deliver what the dropdown label promises.
- One-line fix: `slice(0,7)` → `slice(0,6)`.

### 1.4 Functional fallback path — snap_attrib synthesis is sound

The 2026-04-30 hotfix at lines 4870-4878 maps `snap_attrib[name].hist[].exp/.bench_exp` → the legacy `{e, bm}` shape that the Pearson loop expects. Verified mapping is identity-correct: `e=p.exp`, `bm=p.bench_exp`, computed `active = e-bm` matches what numpy gets when given `(exp - bench_exp)`. **No fabrication, no synth marker needed** — this is purely a rename, complies with anti-fabrication rule 2.

### 1.5 Section 1 verdict

**YELLOW.** Pearson is correct. Hotfix path is clean. Monthly dedupe is broken (C1) and null-exp coercion to 0 is unmarked (legacy YELLOW from prior audit, not regressed). **Safe for presentation if user does not click "Monthly" or is briefed verbally that monthly mode currently behaves like weekly.**

---

## 2. Functionality Parity — Track 2

### 2.1 Closure status of prior-audit findings (B60–B77)

| # | Issue | 2026-04-23 | 2026-05-01 | Notes |
|---|---|---|---|---|
| B60 | Active-vs-raw fallback mixes series types | open | open | L4895 still mixes; no PM decision recorded |
| B61 | Positional `min(len)` pairing not date-aligned | open | open | Mostly moot now: all 139 EM factors have identical 383-obs histories (same parser, same row source), so no head-vs-tail misalignment in current data. Latent risk if a future factor has shorter hist. |
| B62 | Zero-variance / `n<3` silently returns 0 | open | **closed** | L4902 + L4908 both return `null`; L4950 maps null → "—" |
| B63 | Full symmetric matrix (redundant triangle) | open | open | nice-to-have, non-blocker |
| B64 | Hardcoded colorscale + text hex | open | **closed** | L4940-4944 use `getComputedStyle` for `--pos`, `--neg`, `--pri`, `--grid`, `--txth` |
| B65 | No cell click drill | open | open | non-blocker |
| B66 | Period/freq/factor state not persisted | open | **closed** (with caveat C2) | L4836-4850 save+restore via `rr.corr.{period,freq,facs}`; see C2 below for stale-state risk on strategy switch |
| B67 | No CSV export | open | **closed** | `exportCorrCsv()` at L4968 + button at L6957 |
| B68 | No full-screen modal | open | open | nice-to-have |
| B69 | No `id` on live card; no note popup wiring | open | **closed** | L6946 has `id="cardCorr"`; L6948 has `oncontextmenu="showNotePopup(event,'cardCorr')"` |
| B70 | No `data-tip` on live card title | open | **closed** | L6948 has comprehensive `data-tip` |
| B71 | Ghost tile in Exposures tab | open | **closed** | Removed 2026-04-30 (comment at L2461 records the removal) |
| B72 | Ghost PNG button | open | **closed** | (deleted with B71) |
| B73 | Hardcoded insight thresholds | open | **closed** | L4920-4921 read from `_thresholds.corrHigh / corrDiversifier` |
| B74 | Insight bullet factor names not clickable | open | **closed** | L4929-4930 wrap in `<a onclick="oDrF(...)">` |
| B75 | Factors with <3 obs silently appear | open | **closed** | L4898 filters them out |
| B76 | Monthly dedupe behavior undocumented | open | **closed** by comment, **but the implementation is buggy — see C1** | L4886 comment "B76: monthly dedupe keeps the FIRST observation per YYYY-MM" describes intent; code at L4893 fails to deliver it |
| B77 | Tile semantic ambiguity (active vs raw) | open | open (but tooltip clarifies) | About entry at L1047-1048 says "factor active exposures" — that's now explicit; full B77 fix would also rename the title |

**Net:** 12 of 18 prior findings closed in the promote. Outstanding non-blockers: B60, B61, B63, B65, B68, B77.

### 2.2 Chrome parity vs sibling Risk-tab tiles

Compared to `cardFacContribBars` (L6785), `cardRiskByDim` (L6889), `cardTEStacked` (L6758), `cardRiskDecomp` (L6536):

| Capability | cardCorr | Peer benchmark | Gap? |
|---|---|---|---|
| Stable DOM `id` | ✅ | ✅ | — |
| Card-title tooltip (`data-tip`) | ✅ | ✅ | — |
| About `ⓘ` button | ✅ | ✅ | — |
| Right-click → note popup | ✅ | ✅ | — |
| Reset Zoom button | ✅ (`⤾`) | ✅ | — |
| CSV export | ✅ | ✅ | — |
| Period dropdown | ✅ | mixed (some have, some don't) | — |
| Frequency dropdown | ✅ | unique to cardCorr | — |
| Factor multi-select | ✅ | unique to cardCorr | — |
| Plotly responsive | ✅ | ✅ | — |
| Full-screen modal (⛶) | ❌ | partial across siblings | non-blocker (B68) |
| Cell-click drill | ❌ | varies | non-blocker (B65) |
| Theme-aware colorscale | ✅ (B64 closed) | ✅ | — |

**Section 2 verdict: GREEN.** Chrome parity with peer Risk-tab tiles is now complete. The remaining functional gaps (FS modal, cell drill) are project-wide and non-blocking.

### 2.3 NEW FINDING — C2 — `_corrRestored` flag may strand persisted state on strategy switch

**Severity: low (cosmetic UX).** Lines 4834-4843:
```js
if(!window._corrRestored){
  // restore from localStorage…
  window._corrRestored=true;
}
```

The flag is set globally and never reset. After a strategy switch (`upd()` → `rRisk()` → fresh DOM with default-state selects), the flag is already `true`, so the user's persisted period/freq/factor selections from localStorage are NOT restored into the new DOM — selects revert to "All" / "Weekly" / FAC_PRIMARY-default.

**On the same strategy:** subsequent `rUpdateCorr()` calls (e.g. checkbox toggle) correctly skip the restore step (the live DOM state is the truth). So the flag *does* serve a purpose on a single strategy.

**Fix candidates (non-blocker):**
- Reset `window._corrRestored=false` inside the strategy-switch handler (`onAcct()` or wherever strategies switch).
- Or: gate the restore on "DOM was just rebuilt" rather than "page was just loaded" by removing the flag and accepting one extra restore per render.

**Why YELLOW not RED:** the persistence DOES work for the most common workflow (page load → user interacts with cardCorr → state persists across reloads). It only stops persisting on strategy switch — and that case is a known quirk across many tiles in the dashboard.

### 2.4 NEW FINDING — C3 — `FAC_PRIMARY` default checkbox set misses momentum on EM/IDM/IOP

**Severity: cosmetic.** `FAC_PRIMARY` (L3698) lists `'Momentum (Medium-Term)'`. The data ships `'Medium-Term Momentum'`. They are not equal strings.

Effect on EM data: of the 7 FAC_PRIMARY factors, only 5 are pre-checked (Volatility, Profitability, Dividend Yield, Growth, Value). Momentum is unchecked at first render. User sees a 5×5 matrix instead of 6×6.

**Workaround:** user clicks the Medium-Term Momentum checkbox manually. **Non-blocker for presentation** — but if you're showing momentum-aware insights, click it before screen-share.

---

## 3. Design Consistency — Track 3

### 3.1 Typography & spacing — measured against project standard (10/11/12px scale, `.card` padding)

| Element | Value | Standard | OK? |
|---|---|---|---|
| Card title | inherits `.card-title` | 14px / 600 weight | ✅ matches peers |
| Period / Freq selects | `font-size:11px; padding:3px 6px` | matches `cardFacButt` toolbar density | ✅ |
| CSV button | `class="export-btn"` | shared style | ✅ |
| About + Reset-Zoom | `1px solid var(--grid)`, `font-size:11-12px` | shared helpers | ✅ |
| Factor checkbox labels | `font-size:11px; padding:2px 6px` | matches | ✅ |
| Heatmap cell text | `size:10` | shared with cardMCR | ✅ |
| Axis tick fonts | `size:10` (x), `size:10` (y) | shared | ✅ |
| Colorbar tickfont | `size:9` | matches | ✅ |
| Insight bullets | `font-size:11px` | matches sibling alert chips | ✅ |
| Note (insufficient-data warning) | `font-size:10px; color:var(--warn)` | matches | ✅ |

### 3.2 Theme awareness

- Heatmap colorscale: themed (B64 closed). `[--neg, --grid, --pri]` diverging — clean.
- Cell text color: `--txth` — themed.
- Selects, controls, insight chip backgrounds, borders: all `var(--*)`-based.
- Hover labels (Plotly default): inherit from `plotBg` template — inherited theming.

### 3.3 Heatmap geometry

- Min height 260px, scales `36px/factor + 80px base` — works for 5-25 factors.
- Margins `l:150 r:60 t:20 b:110` — comfortable for ~28-char factor names.
- `tickangle:-35` on x — readable.
- Symmetric matrix renders both triangles + diagonal — visually wasteful (B63 open) but conventional and presentable.

### 3.4 Insights row design

`#corrInsights` chip uses `background:var(--surf)`, `padding:8px 10px`, `border-radius:6px`, `line-height:1.8`. Factor names are now linked to `oDrF` with underline + `var(--pri)` color (B74 closed). Clear visual affordance that they're clickable.

**Section 3 verdict: GREEN.** All density, alignment, and theme conventions match the Risk-tab peers. Symmetric matrix is the only design debt and it's cosmetic.

---

## 4. Verification Checklist

- [x] **Data accuracy:** Pearson math verified against numpy on 3 factor pairs × 2 windows (all-period, 1Y-weekly). All matches to ≤0.001.
- [x] **snap_attrib fallback path** is rename-only (compliant with anti-fabrication rule 2).
- [🟡] **Monthly dedupe (C1):** broken — keeps ~74% of weekly obs instead of ~23%. Math drift on r values is small (~0.005) but advertised feature does not deliver.
- [x] **Edge cases:** empty fac, <2 selected, <3 obs, zero-variance, self-correlation — all clean.
- [x] **Filter persistence (B66):** wired for period, freq, factor checkboxes. Caveat C2: stale on strategy switch.
- [x] **CSV export (B67):** wired and well-formed (CSV-quotes factor names, `null` → empty string).
- [x] **Reset zoom button:** wired against `corrHeatPlot`.
- [x] **About entry:** comprehensive 5-field record at L1045.
- [x] **Right-click → note:** wired with `cardCorr` id.
- [x] **Hover tooltip (cell):** wired, 3-dp precision.
- [x] **Hover tooltip (header):** wired with theme-explanatory text.
- [x] **Themes (dark + light):** colorscale + text fully themed via CSS vars.
- [x] **No console errors:** static read shows no obvious exceptions; live render path through try/catch wrapper at L6982-6985.
- [ ] **Default period is "All"** — user picked 1Y weekly (R2-Q12); logged for B117 backlog. Not a fix in this audit.
- [ ] **C3 cosmetic:** momentum factor missing from default checkbox set on accounts that ship `'Medium-Term Momentum'` (EM, likely IDM/IOP). Fix is one-line: add both spellings to FAC_PRIMARY or use a regex match.

---

## 5. Verdict

### **YELLOW — SAFE FOR PRESENTATION**

**Why YELLOW (not GREEN):**
- C1 (monthly dedupe bug) is a real math defect that mis-delivers the advertised "Monthly" feature.
- C3 (default checkbox momentum miss) is a cosmetic gap on the user's most likely accounts.
- B60, B61, B77 carry forward open from prior audit.

**Why SAFE (not RED):**
- Pearson math is correct against numpy.
- All 12 user-facing functionality items closed since prior audit (id, note, About, CSV, theme colors, b62 null sentinels, b75 short-history filter, b73 thresholds, b74 clickable insights).
- All chrome parity with sibling Risk-tab tiles is achieved.
- Design consistency: GREEN.
- C1 produces "wrong but visually-similar-to-weekly" results — won't catch the eye on stage and won't produce nonsensical numbers. Brief verbally if anyone clicks "Monthly."

### Pre-presentation recommended actions

**TRIVIAL (1-line fixes the coordinator could land before showtime):**
1. **C1**: change `h.d.slice(0,7)` → `h.d.slice(0,6)` at line 4893. Restores correct monthly dedupe. ~2 min including smoke-test.
2. **C3**: change `'Momentum (Medium-Term)'` → `'Medium-Term Momentum'` in FAC_PRIMARY (L3698), or add both. ~1 min.

**TALKING POINTS (if you don't want to ship code 4 hours before):**
- "Monthly mode is approximate today — we deduplicate by year-month-prefix; one-line fix landing post-presentation."
- "Default checkbox state shows Momentum factor only after you click it; on the roadmap to auto-select."

**NEEDS PM DECISION (out of scope for today):**
- B60: always-active vs always-raw exposure series.
- B77: rename tile to "Factor Active-Exposure Correlation" once B60 is settled.
- B117 backlog: change default period from "All" to "1Y" weekly per R2-Q12.

**LATER:**
- B68 (full-screen modal), B65 (cell-click drill), B63 (half/full triangle toggle), B61 (date-aligned pairing) — non-blockers, can ship anytime.

---

## 6. Sign-off summary

| Track | Verdict | One-line |
|---|---|---|
| **1. Data Accuracy** | **YELLOW** | Pearson correct vs numpy; C1 monthly dedupe defect (small drift, but mis-delivers feature). |
| **2. Functionality** | **GREEN** | 12/18 prior findings closed; chrome parity with Risk-tab peers. |
| **3. Design** | **GREEN** | Density, theme awareness, alignment all match project standard. |

**Overall: YELLOW — SAFE FOR PRESENTATION. Brief verbally if anyone clicks "Monthly."**

---

## 7. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Audit v1 — 18 findings B60–B77, RED verdict (ghost tile + missing CSV/FS/drill/id/note). | Tile Audit Specialist |
| 2026-04-30 | Promote-to-first-class commit `819c493` — closed B62, B64, B66, B67, B69, B70, B71, B72, B73, B74, B75. | (codebase) |
| 2026-05-01 | Audit v2 — re-verification of 18 prior findings (12 closed) + ground-truth Pearson against numpy on EM full history (3 pairs × 2 windows, all match) + 3 new findings: C1 (monthly dedupe bug), C2 (`_corrRestored` stale-on-strategy-switch), C3 (FAC_PRIMARY momentum-name mismatch). YELLOW / SAFE FOR PRESENTATION verdict. | Tile Audit Specialist |
