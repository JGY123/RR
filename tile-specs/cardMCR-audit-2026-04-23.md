# Tile Audit: cardMCR — "Marginal Contribution to Risk (Top & Bottom)"

> **Audit date:** 2026-04-23
> **Auditor:** Tile Audit Specialist (CLI) — Batch 4 of Tier-1 sweep
> **Dashboard file:** `dashboard_v7.html` (~6,500 lines)
> **Methodology:** 3-track audit per `tile-audit-framework` + `AUDIT_LEARNINGS.md`
> **Sibling in same g2 row:** cardFRB (audited 2026-04-21 — YELLOW/YELLOW/YELLOW)
> **Upstream sibling (same field `h.mcr`):** cardScatter (audited 2026-04-21 — RED; B20 labeling blocker)
> **Gold-standard refs:** cardSectors, cardHoldings

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Marginal Contribution to Risk (Top & Bottom) |
| **Card DOM id** | `#cardMCR` |
| **Render function** | `rMCR(s)` at `dashboard_v7.html:L2717` |
| **Chart target div** | `#mcrDiv` (height 300px, L1282) |
| **Full-screen opener** | **ABSENT** — no `openFullScreen('mcr')` wired, no `renderFsMCR` |
| **Tab** | Risk (row 8 of Risk-tab template, L1277–1283) |
| **Paired tile** | cardFRB (same `g2` row, L1284–1288) |
| **Width** | Half (`g2`) |
| **Owner** | CoS / main session |
| **Spec status (prior)** | none — no `tile-specs/*mcr*.md` |

---

## 1. Data Source & Schema — TRACK 1 (Data Accuracy)

**Section grade: RED — same domain-term labeling error as cardScatter B20. Every label on this tile — card title, axis title, text labels on bars, hovertemplate, tooltip — calls `h.mcr` "MCR" / "Marginal Contribution to Risk". Per `CLAUDE.md` and `factset_parser.py:L501`, `h.mcr = g("PCT_S")` — literally the FactSet `%S` column, which is the stock-specific (idiosyncratic) component of each holding's tracking error. The rest of the codebase already knows this: stock-detail modal L4314 labels it "%S (Stock-Specific TE)", idio-risk computation L1101 sums `h.mcr` as idiosyncratic risk. Only cardMCR (and cardScatter, now fixed-in-queue) still broadcast the wrong term.**

### 1.1 Primary data source

- **Object path:** `s.hold[]` — per-holding array, read directly (not `getSelectedWeekHold()`).
- **Filter applied** (L2719): `!isCash(h) && isFinite(h.mcr) && h.mcr !== 0`.
- **Sort 1:** `Math.abs(b.mcr) - Math.abs(a.mcr)` → take top 10 by magnitude.
- **Sort 2 (after slice):** `(b.mcr) - (a.mcr)` → positives above, negatives below.

### 1.2 Field inventory

| # | Role | Field | Parser origin | CLAUDE.md meaning | Label in chart | Correct? |
|---|---|---|---|---|---|---|
| 1 | X axis | `h.mcr` | `PCT_S` (parser L501; also L569 `hn.mcr??hn.pct_s`) | **Stock-specific (idiosyncratic) TE component** | "MCR %" (axis L2728), "MCR" (card title L1280), "MCR" (hovertemplate L2727), "MCR" (card-title tooltip L1280) | **WRONG — mislabeled at 4 sites** |
| 2 | Y axis | `h.t` | Ticker | — | (category axis, no title) | Correct |
| 3 | Bar color | sign of `h.mcr` | derived | — | Purple `#8b5cf6` = positive, Green `#10b981` = negative | Semantically confused — see §1.7 |
| 4 | Bar text | `fp(h.mcr,2)` | — | signed 2-decimal | Right of bar | Correct value, but mis-worded label on axis |
| 5 | Hover | `h.n` (name), `h.t`, `h.mcr` | — | — | Name / ticker / "MCR: X.XX%" | Same mislabel |

### 1.3 Derived / computed values

- None persisted. `rMCR` reads `s.hold` live.
- The narrative the tile tells itself in card-title tooltip (L1280) — "Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions)" — is specifically MCR-flavored reasoning (∂σ/∂w_i) applied to a field that is not MCR. `%S` is always non-negative in a standard FactSet `%` decomposition because it is a variance-share. **A negative `h.mcr` in a long-only portfolio is anomalous and, if observed, likely flags a parser-sign issue, not a hedge** — needs PM/FactSet confirmation before the "negative = hedge/short" narrative is correct. See §7 B39.

### 1.4 Ground truth verification

- [x] Parser mapping traced: `PCT_S → h.mcr` (factset_parser.py:L501 + v2 alias L569 `hn.pct_s`).
- [x] CLAUDE.md confirms `%S` = "stock-specific component of that holding's tracking error" — per-holding idio contribution, not MCR.
- [x] Code corroborates: L1101 sums `h.mcr` under the comment "Idiosyncratic risk percent of TE" — same data, correct name elsewhere in the codebase.
- [x] Code corroborates: stock-detail modal L4314 labels `h.mcr` literally as "%S (Stock-Specific TE)" — exact term.
- [x] Code corroborates: cardScatter full-screen L5632 (post-B20-aware) labels X axis "MCR (Stock-Specific TE)" — partial recognition.
- [ ] Spot-check pending a loaded JSON — flagged per AUDIT_LEARNINGS convention.
- [x] **Week-selector awareness:** `rMCR` reads `s.hold` directly. When `_selectedWeek` is set, the historical-week amber banner promises a past view but this tile silently shows latest holdings. Consistent with two-layer history architecture (holdings not persisted per-week) but same silent-drift caveat as cardScatter/cardSectors/cardCountry. Not a bug; document in tooltip.

### 1.5 Missing / null / edge handling

| Scenario | `rMCR` behavior |
|---|---|
| Empty `hold` | Renders `<p>No MCR data available</p>` into `#mcrDiv` — GOOD |
| `h.mcr` null | Filtered out via `isFinite(h.mcr)` — GOOD |
| `h.mcr === 0` | Filtered out via `h.mcr !== 0` — GOOD (avoids cluttering top-10 with zero bars) |
| `h.mcr` NaN/Infinity | Filtered out via `isFinite` — GOOD |
| Fewer than 10 holdings with non-zero `h.mcr` | Chart renders however many exist — OK |
| Tie on abs(mcr) | Arbitrary sort stability; low-risk | OK |
| All-negative portfolio (unlikely for %S, see §1.3) | Chart shows all green bars | silent |
| Cash row in hold | Excluded via `isCash(h)` | OK |

**Edge-handling is actually the best of the chart tiles audited to date.** Parser-side filtering is tight. The domain-term labeling is the only Section-1 defect.

### 1.6 Cross-tile data consistency

- `h.mcr` used here = same field as cardScatter X-axis. Both tiles tell the same wrong story with the same wrong word. Fixing B20 (cardScatter) without fixing cardMCR would introduce a NEW drift (one tile says "Stock-Specific TE", the other says "MCR") — **B20 and this audit's B39 must land together**.
- `h.mcr` also appears in: `idioSum` (L1101, correctly called "Idiosyncratic"), `riskDecompTree` (L2794+, via idio/factor split), stock-detail modal L4314 (correctly "%S"), Holdings tab CSV export L5931, full-screen scatter panel L5647. No other tile misnames it.

### 1.7 Color-semantic defect

Line 2724: `marker:{color:top.map(h=>(h.mcr||0)>=0?'#8b5cf6':'#10b981')}`.

- Positive `h.mcr` colored **purple** (`#8b5cf6`) — called out as "adds risk" in the tooltip.
- Negative `h.mcr` colored **green** (`#10b981`) — called out as "reduces risk (from short or hedging)".

Two problems:
1. **Green is the project's "positive/good" token** (`--pos`, used across sectors OW, factor "diversifies", gains etc.). Applying green to "negative idio TE contribution" conflates two different meanings of "good". A PM glancing at all-green bars at the bottom does not immediately parse "these are hedging/short positions"; they parse "these are good". Ambiguous at best, misleading at worst.
2. The purple color `#8b5cf6` is hardcoded, not themed. cardFRB (sibling, same row) uses `--pos`/`--neg` via `getComputedStyle` at L2735–2736. cardMCR should match.

**Proposed replacement** (needs PM call): positive → `var(--neg)` (red; risk-adding is the unwanted direction from a TE-minimization lens), negative → `var(--pos)` (green; diversifying). Or: positive → `var(--pri)` (indigo neutral, "contributes"), negative → `var(--pos)` (green, "offsets"). Either is better than the current purple/green duo.

---

## 2. Columns & Dimensions Displayed

No table — chart-only tile. Columns N/A.

---

## 3. Visualization Choice

### 3.1 Layout type
Horizontal bar chart (`type:'bar', orientation:'h'`), 10 bars, height 300px. One bar per top-|MCR| holding.

### 3.2 Axis behavior
- X-axis: "MCR %" title (mislabeled — see §1), `zeroline:true, zerolinecolor:THEME().zero, zerolinewidth:1` — GOOD; matches cross-tile convention. One of the few chart tiles that gets this right.
- Y-axis: category, `autorange:'reversed'` — top of chart = first in sorted order (highest positive mcr). Correct.
- No x-axis tick format override — uses Plotly default (scientific notation possible on very small values). Low risk.

### 3.3 Color semantics
- Purple `#8b5cf6` + green `#10b981` — hardcoded. See §1.7 for the semantic defect and §6 for the theme-token defect.
- Bar text (`textposition:'outside'`) uses `THEME().tick` — GOOD.

### 3.4 Interactivity
| Capability | cardMCR | cardFRB (peer) | Gap? |
|---|---|---|---|
| Plotly hover | yes | yes | — |
| Plotly click → drill | **no wiring** | yes → `oDrF(label)` L2745 | **TRIVIAL (one line)** |
| Full-screen modal | **no** | N/A | NON-TRIVIAL |
| Tile-wide onclick | no | yes → `oDrRiskBudget()` | n/a — different design |
| Right-click note popup | **no** (`oncontextmenu` missing) | yes (L1285) | TRIVIAL |
| PNG export | yes (L1281) | yes | **REMOVE** (user standing order) |
| CSV export | **no** | no | TRIVIAL |
| Keyboard a11y | n/a (no onclick) | yes (tabindex/role/onkeydown L1284) | n/a until click-drill added |

**Parity failure — same as cardScatter §4.1 #1:** clicking a bar should drill to the stock detail modal `oSt(ticker)`. Every bar has `customdata` set to `h.n || h.t` already; passing `.text` (the y-axis category = `h.t` ticker) to `oSt` is a one-liner. Without this, the top-|MCR| tile is read-only and forces users to context-switch to Holdings tab to find the stock.

### 3.5 Empty state
Writes `<p>No MCR data available</p>` directly into `#mcrDiv` (L2720) — GOOD, matches AUDIT_LEARNINGS §"Viz-renderer pattern".

### 3.6 Responsive behavior
- Fixed 300px height (L1282). Narrow viewport collapses `g2` grid but chart keeps height.
- No `config:{responsive:true}` override; inherits `plotCfg`.

### 3.7 Text label density
10 bars max, `textposition:'outside'` at `size:10`. Meets project font floor (9/10/11/12/13 per AUDIT_LEARNINGS §6). GOOD.

---

## 4. Functionality Matrix — TRACK 2 (Parity)

**Section grade: YELLOW** — tile is small and focused, but against the peer cardFRB in the same row it's missing three of four standard chart-tile primitives (right-click, click-drill, CSV). Against the user standing orders it still has a PNG button.

Benchmark: cardFRB (same row peer), cardFacButt (chart peer), cardScatter (same field peer).

| Capability | cardSectors (gold) | cardFRB (peer same row) | cardMCR (current) | Gap? |
|---|---|---|---|---|
| Empty-state fallback in div | yes | yes | yes | — |
| Theme-aware colors (`--pos`/`--neg`) | yes | yes | **no — `#8b5cf6` + `#10b981` hardcoded** | **TRIVIAL** |
| `plotly_click` → drill | N/A (table) | yes → `oDrF` | **no** | **TRIVIAL (one line, → `oSt(ticker)`)** |
| Right-click `showNotePopup` on title | yes | yes (L1285) | **no** | **TRIVIAL** |
| Card-title tooltip `tip`/`data-tip` | yes | yes | yes | — |
| PNG export button | yes | yes | yes — **violates `feedback_no_png_buttons.md`** | **REMOVE** |
| CSV export | yes | **no** (same gap) | **no** | TRIVIAL (wire `exportCSV` to a synthetic table of the 10 plotted rows OR a full-holdings MCR table) |
| Full-screen modal | yes | N/A | **no** | NON-TRIVIAL (see §7 B42) |
| `isFinite` filter before plot | (N/A) | yes (L2732) | yes (L2719) | — |
| Sign-preserving `data-sv` (for any eventual table) | yes | n/a | n/a | — |
| Axis zero-line | (N/A) | N/A (pie) | yes | — |
| Keyboard a11y on clickable card | yes | yes | n/a until click-drill added | — |
| Sensitive to `_selectedWeek` | yes (via `getSelectedWeekSum`) | no | no — silent | see §1.4 bullet |

### 4.1 Functionality gaps — itemized

1. **No `plotly_click` handler.** Clicking a bar does nothing. Peer cardFRB has it (L2745). One-line fix at end of `rMCR`:
   ```js
   let el = document.getElementById('mcrDiv');
   if (el && el.on) el.on('plotly_click', d => {
     let t = d?.points?.[0]?.y;
     if (t && typeof oSt === 'function') oSt(t);
   });
   ```
2. **No `oncontextmenu="showNotePopup(event,'cardMCR');return false"` on card-title** (L1280). Every other same-row tile has this (cardFRB L1285, cardScatter L1255, cardTreemap L1263, cardFacButt L1159, cardFacDetail L1165).
3. **Hardcoded `#8b5cf6` / `#10b981` bar colors** (L2724). Should route through `getComputedStyle(...).getPropertyValue('--pos'/'--neg'/'--pri')` (see §1.7 for the palette choice — requires a PM call, but the mechanical swap-to-CSS-vars is trivial).
4. **PNG button present** (L1281 — `onclick="screenshotCard('#cardMCR')"`). Standing order: remove.
5. **No CSV export.** The 10-row top/bottom data is small but the *full* per-holding MCR list is valuable and not exported anywhere specifically by-MCR (Holdings tab CSV has everything but requires sorting). Add a CSV that emits `t,n,sec,p,a,mcr,tr` sorted by `|mcr|` desc.
6. **No full-screen variant** — unlike cardScatter/cardCountry/cardFacButt, there is no `openFullScreen('mcr')`. For a tile that shows only top-10, "show me the full 50 or all holdings by MCR" is a natural expansion. NON-TRIVIAL; flag as B42.
7. **Card title says "Marginal Contribution to Risk" but `h.mcr` is `%S` stock-specific TE.** Same labeling bug as cardScatter B20. See §1 / §7 B39.
8. **Card-title tooltip narrates MCR semantics** ("Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions)") applied to a `%S` field. §1.3 — needs rewrite alongside the title rename.
9. **No axis-range guard.** If a single holding's `|mcr|` dominates (e.g. 40% vs next biggest 2%), the 10-bar layout compresses the rest into invisible lines. Minor; a softer x-range or log-scale toggle would help high-concentration portfolios.

### 4.2 Full-screen — does not exist

There is no `renderFsMCR`. See §7 B42. Not a defect against current state (tile was designed as a small top-10), but a gap vs the expansion pattern the other chart tiles have adopted.

---

## 5. Popup / Drill / Expanded Card

None. Closest existing drill for `h.mcr`-flavored data is the stock detail modal `oSt(ticker)` (L4254), which exposes a "%S (Stock-Specific TE)" row (L4314). That is the natural click target — see §4.1 #1. No MCR-specific drill modal currently exists.

---

## 6. Design Guidelines — TRACK 3 (Consistency)

**Section grade: YELLOW** — three small but consistent theme-token defects plus missing right-click hook. Collectively they put cardMCR behind every other Risk-tab tile on theme adherence.

### 6.1 Density
- Height 300px — slightly shorter than cardScatter's 320px (L1259), cardFRB's 260px (L1287). Acceptable.
- 10 bars + labels + x-axis ~ 240px plot area. Comfortable.

### 6.2 Emphasis & contrast
- Bar text `size:10` with `THEME().tick` color — compliant with project font floor.
- Hover labels use Plotly default; no hoverlabel style override (cardFRB uses `tickfont:{color:THEME().tickH}` at L2742). Minor inconsistency.

### 6.3 Alignment
- Plot area uses default `plotBg` margins. No explicit override. `autorange:'reversed'` on y-axis means the largest positive bar sits top-left — correct PM narrative order (biggest risk-adder first).

### 6.4 Whitespace / padding
- Standard `.card` base. OK.

### 6.5 Motion / feedback
- Plotly default hover only. No bar-highlight on hover. Fine for a 10-bar chart.

### 6.6 Theme adherence — key findings
- **Bar colors hardcoded** (L2724): `#8b5cf6`, `#10b981`. Should use `getComputedStyle(document.body).getPropertyValue('--pri')` / `--pos` / `--neg` (peer cardFRB does exactly this at L2735–2736, 4 lines below rMCR's body in the same file). Zero-effort copy.
- Bar text color and zeroline color *do* route through `THEME()` — partial compliance, which makes the hardcoded bar-fill colors more glaring.
- **Light theme** not smoke-tested here, but the hardcoded hexes will render identically in both themes — the purple/green loses all theme-differentiation while the rest of the tile flips correctly. Visible drift.

### 6.7 Consistency issues in one list
1. Bar fill hexes hardcoded (not themed) — L2724.
2. No right-click note-popup on title — L1280 missing `oncontextmenu` attr.
3. PNG button present — L1281, against user standing order.
4. No CSV export button.
5. No full-screen (⛶) button — inconsistent with cardScatter / cardCountry / cardFacButt chart-tile pattern (AUDIT_LEARNINGS §"Viz-tile checklist" item #1 explicitly calls out cardMCR as a tile that should have one).
6. Card-title wording misrepresents the metric (see §1/§7 B39) — style issue subordinate to the data-accuracy defect.
7. No hoverlabel styling — cardFRB has `tickfont:{color:THEME().tickH}`, cardMCR inherits Plotly default.

---

## 7. Known Issues & Open Questions

**Non-trivial queue (backlog — PM decision or medium-effort):**

1. **B39 — Card title / axis / hovertemplate / card-title tooltip all call `h.mcr` "MCR" or "Marginal Contribution to Risk", but the field is FactSet `%S` = stock-specific (idiosyncratic) TE component.** Exact same class of bug as cardScatter B20; both tiles read the same field. Proposed rename: **"Top Idiosyncratic Risk Contributors"** or **"Top Stock-Specific TE"** (card title), "Stock-Specific TE %" (axis), "Stock-Specific TE: %{x:.2f}%" (hovertemplate), and rewrite tooltip to drop "Marginal Contribution to Risk" and the "negative MCR from short/hedging" narrative (see B40). **Must land in the same commit as the cardScatter B20 rename** to avoid one tile saying "MCR" while the other says "Stock-Specific TE" for the same field. Ripples: L1280 (card title + tooltip), L2727 (hovertemplate), L2728 (axis title), possibly the card DOM id `cardMCR` (leave id — risk of dangling CSS/JS refs; rename only user-visible strings).

2. **B40 — The card-title tooltip claims "Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions)."** `%S` is a variance-share decomposition and should not go negative in a standard long-only extract; a negative value likely indicates a parser/FactSet-export quirk, not a hedge. **PM gate**: confirm whether any strategy in production (SCG / GSC / ACWI etc.) actually emits negative `h.mcr` values. If yes, investigate why (short positions? FactSet sign convention on shorts?). If no, simplify tooltip and drop the hedge narrative. Until resolved, the tile teaches PMs a wrong story about their own data. Not as acute as B39 but in the same family.

3. **B41 — Color-semantic confusion (§1.7 / §6.6).** Green = "reduces risk" here, but green = "OW good sector" / "positive return" / "diversifying factor" elsewhere. Project-wide green-as-good is the stronger convention. Proposed: positive `%S` → `--neg` (red, unwanted risk), negative `%S` → `--pos` (green, offsetting). **Requires PM call** because the whole tile narrative flips. Alternative: positive → `--pri` (indigo neutral, "contributes"), negative → `--pos` (green, "offsets"). Either unlocks a single-color-convention dashboard.

4. **B42 — No full-screen variant.** AUDIT_LEARNINGS §"Viz-tile checklist" explicitly lists cardMCR as a tile that should have a `⛶` full-screen button. `renderFsMCR` would naturally show: (a) all holdings with non-zero `%S` as a paginated bar chart, (b) sortable side-panel table (reuse `_renderFsScatPanel` pattern), (c) click a bar → open `oSt(ticker)` drill. Medium effort (~80 lines). Same panel skeleton as cardScatter FS so probably 50 lines after refactor.

5. **B43 — No week-selector awareness, silently shows latest.** Same two-layer-history trap as cardScatter / cardSectors / cardCountry. `s.hold` is latest-only. When user selects a past week via the header arrow, the amber banner fires, the Overview stats flip, but cardMCR silently renders today's top-|%S| holdings. Not a bug (historical holdings not persisted) but worth a 1-line inline note in the tooltip: "Always shows latest holdings — historical MCR not persisted."

6. **B44 — CSV export** of the per-holding `%S` list (all holdings, not just top 10) is missing. Holdings tab CSV at L5931 includes `h.mcr` as a column among many; a dedicated MCR-sorted export with just `{t,n,sec,p,a,mcr,tr}` would be a natural CSV for this tile. Small task but crosses into B42 (full-screen export).

**Open questions for PM:**

- Accept B39 rename end-to-end on cardMCR AND cardScatter in the same commit? (Strong recommendation: yes. Single-tile rename creates drift.)
- B40: do any strategies actually emit negative `h.mcr`? If so, is it a parser sign convention or genuine hedge? (Need spot-check on a short-enabled strategy's JSON.)
- B41 color semantic: purple/green, red/green, or indigo/green? Default recommendation: red/green (matches FRB sibling).
- Is the tile-title "Top & Bottom" phrasing still meaningful after B40 resolves? (If all-long-only strategies never emit negative `%S`, "Top & Bottom" is misleading because there is no "bottom" — should become "Top Idiosyncratic Risk Contributors".)

---

## 8. Verification Checklist

- [x] Data path traced: `s.hold[].mcr` sourced from parser `PCT_S` (factset_parser.py:L501).
- [ ] Data accuracy: **axis / card title / hovertemplate mislabel `h.mcr` as "MCR".** See §1 / B39.
- [x] Empty state: writes to div (`<p>No MCR data available</p>`) — GOOD.
- [x] `isFinite` filter present (L2719).
- [x] Cash exclusion via `isCash(h)` (L2719).
- [x] Non-zero filter (`h.mcr !== 0`) — avoids zero bars polluting top 10.
- [x] Zero-line on x-axis wired (L2728) — GOOD.
- [ ] `plotly_click` drill → `oSt(ticker)`: NOT WIRED. Peer cardFRB has it.
- [ ] Right-click → `showNotePopup(event,'cardMCR')` on card-title: NOT WIRED (L1280 missing attr).
- [ ] Theme-aware bar colors: **hardcoded `#8b5cf6` / `#10b981`** (L2724). Peer cardFRB uses CSS vars.
- [ ] PNG button: **present** (L1281) — violates standing order.
- [ ] CSV export: **absent.**
- [ ] Full-screen (⛶) button: absent.
- [x] Bar label font ≥ project floor: `size:10` meets floor.
- [x] Bar label text color themed: `THEME().tick`.
- [ ] Card-title tooltip accuracy: **parrots the MCR mislabel + a hedge narrative that may not describe the data.**
- [ ] Week-selector: silently latest (acceptable — see B43 for tooltip note).
- [ ] No console errors: untestable without loaded JSON.
- [ ] Spot-check 3–5 rows vs source JSON: pending loaded JSON (AUDIT_LEARNINGS blocker convention).

---

## 9. Related Tiles & Cross-Tile Patterns

- **cardScatter** (audited 2026-04-21, B20 RED) — same field `h.mcr`, same class of labeling bug. B39 and B20 **must land in the same commit** to avoid introducing a new drift (one tile renames, the other doesn't → users see two different names for the same column).
- **cardFRB** (same g2 row, audited 2026-04-21) — is the immediate peer for chart-tile conventions. Three of the defects found here (`oncontextmenu`, themed colors via CSS vars, `plotly_click` → drill) are things cardFRB already does correctly 4–60 lines down from `rMCR` in the same file. Zero-friction adoption.
- **cardTreemap** (audited 2026-04-21) — shares `h.mcr` access via color mode `'specific'` (L2425 / L5770). Same underlying semantic; if B39 rename lands, treemap's "Specific Risk %" color-mode label (already correct!) becomes the naming template for cardMCR too.
- **Stock-detail modal `oSt`** (L4254) — L4314 already correctly labels `h.mcr` as "%S (Stock-Specific TE)". This is the nomenclature target for B39.
- **`riskDecompTree`** (L2794) and **`idioSum`** (L1101) — both aggregate `h.mcr` correctly under "idiosyncratic" / "specific". cardMCR is the last holdout using "MCR" for this field.
- **AUDIT_LEARNINGS §"Domain-term labeling errors" (added in cardScatter audit)** — append cardMCR to that list on next sweep. The pattern is now confirmed at 2 tiles for the same field; the "MCR" misnomer is a codebase-level defect, not a single-tile bug.

---

## 10. Phantom Spec Drift

No prior `tile-specs/*mcr*.md` exists. Not a phantom-spec case; the tile was built without a dedicated spec. Recommend creating one post-B39/B42 if PM wants the full-screen expansion.

---

## 11. Proposed Fix Queue

### TRIVIAL (agent can apply, ≤5 lines each, no PM judgment needed beyond the rename wording)

T1. **Add `plotly_click` drill** at end of `rMCR` (after L2728):
```js
let mcrEl = document.getElementById('mcrDiv');
if (mcrEl && mcrEl.on) mcrEl.on('plotly_click', d => {
  let t = d && d.points && d.points[0] && d.points[0].y;
  if (t && typeof oSt === 'function') oSt(t);
});
```

T2. **Add right-click note popup** — change L1280 from:
```html
<div class="card-title tip" data-tip="Top 10 holdings by |MCR|. ...">Marginal Contribution to Risk (Top & Bottom)</div>
```
to:
```html
<div class="card-title tip" data-tip="..." oncontextmenu="showNotePopup(event,'cardMCR');return false">...</div>
```

T3. **Remove PNG button** at L1281 — standing order. Same removal applied to prior batches.

T4. **Route bar colors through CSS vars.** Replace L2724 `#8b5cf6` / `#10b981` with `getComputedStyle(document.body).getPropertyValue('--pri').trim() || '#8b5cf6'` and `'--pos'` + fallback. (Final color choice depends on P1 below; the mechanical var-routing is trivial.)

T5. **Add CSV export** button in an export-bar (replacing the removed PNG slot). Reuse `exportCSV` against a synthetic table built in JS, or build the CSV string inline and trigger download. Payload: `t,n,sec,p,a,mcr,tr` for all holdings with non-zero `h.mcr`, sorted by `|mcr|` desc.

T6. **Rewrite card-title tooltip** (L1280) to match reality. Current: "Top 10 holdings by |MCR|. Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions)." Proposed (after B39): "Top 10 holdings by |Stock-Specific TE|. Larger bars = bigger contributors to idiosyncratic (stock-specific) portfolio risk. Click a bar for the stock detail." Drop the hedge narrative until B40 resolves.

T7. **Rewrite axis title** L2728 `title:'MCR %'` → `title:'Stock-Specific TE %'` (after B39).

T8. **Rewrite hovertemplate** L2727 `'MCR: %{x:.2f}%'` → `'Stock-Specific TE: %{x:.2f}%'` (after B39).

T9. **Rename card title string** L1280 "Marginal Contribution to Risk (Top & Bottom)" → "Top Idiosyncratic Risk Contributors" (or PM's preferred phrasing — see P1). Do NOT rename the DOM id `cardMCR` — risk of dangling CSS/JS refs. Only user-visible strings.

T10. **Add a small "Latest holdings" inline note** to the card-title tooltip so week-selector users don't expect historical MCR (B43): append "Always shows latest holdings — historical stock-specific TE not persisted." to the tooltip.

### NEEDS PM DECISION (cannot apply without call)

P1. **B39 rename wording.** "Top Idiosyncratic Risk Contributors" vs "Top Stock-Specific TE Contributors" vs PM's preferred shorthand. Must match cardScatter B20 wording — land both together.

P2. **B40 negative-`%S` semantics.** Does any production strategy emit negative `h.mcr`? Confirms whether "Top & Bottom" phrasing and the green/negative encoding are meaningful.

P3. **B41 color semantic.** Red/green (matches FRB), purple/green (current), or indigo/green? Recommendation: red/green.

P4. **B42 full-screen.** Build now or backlog? Natural place for CSV + full-holdings bar chart + click-to-`oSt` drill.

### NON-TRIVIAL / BACKLOG (B-ids)

B39. **"MCR" → "Stock-Specific TE" rename** on cardMCR. Sibling of cardScatter B20 — must land in same commit. (§7 #1)
B40. **Verify `%S` can legitimately go negative** in production data. Currently the tile's narrative assumes it can. (§7 #2)
B41. **Color semantic unification** purple/green → red/green (or similar), themed via CSS vars. (§7 #3)
B42. **Full-screen `renderFsMCR`** + CSV export + click-to-`oSt` drill. (§7 #4)
B43. **Week-selector awareness inline disclaimer.** (§7 #5 — resolvable via T10 immediately.)
B44. **CSV export** of per-holding `%S` list. Partially resolved via T5; full version lives inside B42 full-screen.

---

## 12. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Audit completed; 3-track methodology; B39 confirms `h.mcr` "MCR" mislabel on 4 sites — same field/same bug as cardScatter B20; must land together. PNG + right-click + click-drill + themed colors all missing vs cardFRB peer. | tile-audit CLI |

---

## 13. Sign-off

**Status:** `draft` — do not promote to `signed-off` until B39 lands (coordinated with cardScatter B20) AND T1–T9 trivial queue is applied. The labeling correctness is a domain-accuracy issue; the tile should not ship to a PM review calling `%S` "MCR" while the rest of the codebase (stock modal, idio-risk aggregator, treemap color-mode) already uses the correct term.

**Grades:**
- Section 1 (Data Accuracy): **RED** — correct field sourcing, but 4 user-visible sites broadcast the wrong term; same class as cardScatter B20. Plus B40 open question on negative-`%S` semantics.
- Section 4 (Functionality Parity): **YELLOW** — missing click-drill, right-click, CSV, full-screen; PNG still present against standing order. Individually trivial, collectively "this tile has been untouched while its peers caught up."
- Section 6 (Design Consistency): **YELLOW** — hardcoded bar hexes + no right-click hook + no full-screen button = three tile-standard misses vs same-row peer cardFRB.

**Overall tile grade: RED** (Track-1 domain-accuracy override per audit rubric). Recommend landing B39 + T1–T9 before any further polish; B42 full-screen and B40 PM-gate in follow-up.
