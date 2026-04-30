# Tile Audit: cardMCR — "Marginal Contribution to Risk (Top & Bottom)" — REBUILD AUDIT

> **Audit date:** 2026-04-30
> **Auditor:** Tile Audit Specialist (CLI) — Marathon batch 5 of N (after cardScatter, cardChars, cardCountry, cardGroups)
> **Dashboard file:** `dashboard_v7.html` (~10,400 lines)
> **Methodology:** 3-track audit per `tile-audit-framework` + `AUDIT_LEARNINGS.md`
> **Predecessor audit:** `tile-specs/cardMCR-audit-2026-04-23.md` — graded **RED/YELLOW/YELLOW**, 6 trivial + 6 non-trivial (B39–B44). This audit re-grades after the 2026-04-30 rebuild (commit 2eff789).
> **Sibling-by-data:** cardHoldRisk (Holdings tab, NEW 2026-04-30 commit 2953eef — bubble-sized by `|h.mcr|`), cardTreemap (`size=specific` mode, color-mode `specific` mode), TE drill modal Idio breakdown.
> **Removed sibling:** cardScatter (DOM gone, `rScat` orphaned but renderer + About entry survive — flag E below).

---

## 0. Tile Identity

| Field | Value |
|---|---|
| **Tile name (human)** | Marginal Contribution to Risk (Top & Bottom) |
| **Card DOM id** | `#cardMCR` (L1961) |
| **Render function** | `rMCR(s)` at `dashboard_v7.html:L5619` |
| **Chart target div** | `#mcrDiv` (height 300px, L1964) |
| **CSV exporter** | `exportMcrCsv()` at L5654 |
| **About entry** | `_ABOUT_REG.cardMCR` at L764–771 (stale — see §1.6 / §6.7) |
| **ⓘ button wired** | yes — `aboutBtn('cardMCR')` at L1962 |
| **Full-screen opener** | **STILL ABSENT** — no `openFullScreen('mcr')`, no `renderFsMCR`. (`renderFsScatter` orphan at L10047 + `_renderFsScatPanel` at L10081 = available skeleton.) |
| **Tab** | Risk (Row 8 of Risk-tab template, L1955–1965) |
| **Paired tile (was)** | cardFRB — **REMOVED 2026-04-29** per L1957 comment |
| **Width** | Full row in Risk-tab grid (cardFRB removal made it solo on Row 8) |
| **Owner** | CoS / main session |
| **Spec status (this audit)** | `data-verified` candidate — domain-term mismatch with codebase still present at 4 user-visible sites; needs PM call before promotion |

---

## 1. Data Source & Schema — TRACK 1 (Data Accuracy)

**Section grade: YELLOW (down from RED).** The April-30 rebuild correctly stripped `%` from the MCR display (bar text, axis, hovertemplate — see §1.5 below) honoring the user's standing rule "MCR is not a percentage". That alone unblocks the worst PM-facing miscommunication. The remaining defect is the same one the 2026-04-23 audit flagged as **B39**: the field `h.mcr` is FactSet `%S` = stock-specific TE component, but the card title still says "Marginal Contribution to Risk", the axis still says "MCR (stock-specific TE component)", the hovertemplate still says "MCR (stock-specific TE)", and the About entry (L764) still says "MCR". The codebase already uses the right vocabulary 4 doors down (cardHoldRisk subtitle "active wt × risk contrib · bubble = idio (|MCR|)" L7319, the L4314 stock modal "%S (Stock-Specific TE)" pattern, and the L3092/L3112/L3909 sector/region/group `Stock TE%` columns). The "MCR" label is now a single-tile holdout against a project-wide convention.

### 1.1 Primary data source

- **Object path:** `s.hold[]` — per-holding array, read directly (no `getSelectedWeekHold()`).
- **Filter (L5625):** `!isCash(h) && isFinite(h.mcr) && h.mcr !== 0`.
- **Sort 1:** `Math.abs(b.mcr||0) - Math.abs(a.mcr||0)` → take top 10 by magnitude.
- **Sort 2 (after slice, L5628):** `(b.mcr||0) - (a.mcr||0)` → positives above, negatives below.
- **Latest-only:** ignores `_selectedWeek` (B43 still applies; tooltip note added but worded with same "MCR" string).

### 1.2 Field inventory (rebuilt tile)

| # | Role | Field | Parser origin | Domain meaning | Display label | Correct? |
|---|---|---|---|---|---|---|
| 1 | X axis | `h.mcr` | `PCT_S` (parser L587/L608) | **Stock-specific (idiosyncratic) TE component (%S)** | Axis: "MCR (stock-specific TE component)" L5650; bar text "+1.84" L5638 (signed, no `%`); hover "MCR (stock-specific TE): 1.84" L5646 | **Half-right** — every label parenthetically clarifies "stock-specific TE", but still leads with "MCR" against the codebase-elsewhere "%S" / "Stock-Specific TE" / "Idio" |
| 2 | Y axis | `tk(h) \|\| h.t` | `tkr_region` (post B-merge) → fallback `h.t` (SEDOL pre-merge) | TKR-REGION display per user 2026-04-29 standard | Y categorical, tickfont 10px | **Correct** — tk(h) wired correctly (L5633); honors the SEDOL→ticker merge fix from commit 5e7e1b6 |
| 3 | Bar color | sign of `h.mcr` | derived | — | Positive → `--pri` (indigo, fallback `#8b5cf6`); negative → `--pos` (green, fallback `#10b981`) | **Themed now (good)**, but semantic still confused — see §1.4 |
| 4 | Bar text | `(h.mcr).toFixed(2)` + `· {p}% port` | `h.mcr` + `h.p` | signed 2-decimal MCR + port wt% | Right of bar, e.g. `+1.84 · 2.3% port` | **Correct** — no `%` on the MCR number (honors the rule); the trailing `%` is only on port wt where `%` is right |
| 5 | Hover | `h.n`, `h.sec`, `h.co\|\|h.country`, `h.p`, `h.a`, `h.mcr`, `h.tr` | — | Name, sector, country, port wt, active wt, MCR, total TE contrib | rich multi-line tooltip via customdata array | **Correct payload, mislabeled term** (line says "MCR (stock-specific TE)") |
| 6 | Click → drill | `customdata[6]` = `h.t` ticker | — | passes ticker to `oSt()` | one-line `plotly_click` handler (L5652) | **Correct** — wired now |

### 1.3 Derived / computed values

- None persisted. `rMCR` reads `s.hold` live each render.
- The narrative claim in card-title tooltip and About entry — "negative MCR from short or hedging positions" — is unchanged from the 2026-04-23 audit (B40) and remains unverified. `%S` is a variance-share decomposition; in standard long-only FactSet exports it should not go negative. **The rebuild did not address B40.** If the field genuinely cannot go negative for any of the 7 production strategies, the "Top & Bottom" framing of the card title is misleading because there is no "Bottom" — every bar would be positive. PM gate stands.

### 1.4 Color semantic — the rebuild improved theme adherence but didn't resolve the meaning conflict

- **Before (2026-04-23):** hardcoded `#8b5cf6` / `#10b981` — flagged.
- **Now (2026-04-30):** `getComputedStyle(...).getPropertyValue('--pri'/'--pos')` with hex fallbacks. ✅ Themed.
- **Still unresolved:** the *choice* of colors. Positive `h.mcr` (adds idio risk) is colored `--pri` indigo; negative is colored `--pos` green. Project convention everywhere else: `--pos` green = "good / OW / positive return / diversifying". Applying green to "negative idio TE contribution" repeats the older confusion. Worse, the in-row peer that just shipped — cardHoldRisk on the Holdings tab — uses **red for adds-risk, green for diversifies** (L5418). So now the same `h.mcr` story is colored *differently across two tiles*: cardMCR says positive=indigo, cardHoldRisk says adds-risk=red. PM glancing at both will misread.

**Recommendation:** match cardHoldRisk — positive `h.mcr` → `--neg` (red, adds idio risk; the unwanted direction in TE-minimization), negative → `--pos` (green, diversifies). Same color palette, same convention as the holdings-tab sibling. PM gate but the gate already happened on cardHoldRisk; cardMCR should follow.

### 1.5 The "MCR is not a percentage" rule — verification

User standing rule: **MCR must never be rendered with a `%` sign.** Verification of every render site:

| Site | Code | Rendered output | Compliant? |
|---|---|---|---|
| Bar text label | L5638 `${sgn}${m}${pwt}` where `m = (h.mcr).toFixed(2)` | `+1.84 · 2.3% port` | **YES** — `%` only on port wt suffix |
| X-axis title | L5650 `'MCR (stock-specific TE component)'` | `MCR (stock-specific TE component)` | **YES** |
| Hover line for MCR | L5646 `'MCR (stock-specific TE): %{x:.2f}'` | `MCR (stock-specific TE): 1.84` | **YES** — no trailing `%` |
| Empty state | L5627 `'No MCR data available'` | text only | YES |
| Card-title tooltip | L1962 `data-tip="Top 10 holdings by \|MCR\|. Purple = adds risk..."` | natural text — `\|MCR\|` is the bar absolute-value notation, not a percentage | YES |
| About `what` | L766 `'... ranked by \|MCR\|. Purple bars ...'` | text only | YES |
| **CSV export header** | L5657 `'ticker,name,sector,port_pct,active_pct,mcr_pct,te_contribution'` | column header literally `mcr_pct` | **NO — single violation** |

**Defect M1 (NEW):** the CSV column header says `mcr_pct` (line 5657). MCR is not a percentage; the column should be `mcr_specific_te` or `mcr` to honor the rule. Trivial 1-line edit. The other CSV columns (`port_pct`, `active_pct`, `te_contribution`) are correctly named because those values *are* percentages (port wt %, active wt %, %T). Only `mcr_pct` mislabels.

### 1.6 Ground truth verification

- [x] Parser mapping unchanged: `PCT_S → h.mcr` (parser L587 + L608 + alias L659 `pct_s`).
- [x] CLAUDE.md confirms `%S` = "stock-specific component of that holding's tracking error".
- [x] Code corroborates internally: `idioSum` aggregates `h.mcr` under "idiosyncratic" (L1101), stock modal L4314 labels it "%S (Stock-Specific TE)", sector tables L3092 labels Σh.mcr "Stock-specific TE", region tables L3112 same, group tables L3909 same.
- [x] Codebase-wide vocabulary on `h.mcr` is "%S" / "Stock-Specific TE" / "Idio". cardMCR is the holdout still calling it "MCR" in 4 user-visible sites + the About entry + the glossary L8393 (project-wide; Section 1.7 below).
- [x] **Bar label format spot-checked:** bar text is `+1.84 · 2.3% port` — `%` only on port wt, MCR rendered as bare signed decimal. **Compliant with user's rule.** ✅
- [ ] Production-data spot-check: pending a loaded JSON for any of {IDM, IOP, EM, ISC, ACWI, GSC} — does any strategy emit negative `h.mcr`? (B40 from 2026-04-23 still open.)

### 1.7 Project-wide MCR vocabulary drift (escalated finding — was B39 single-tile, now project-wide)

After the rebuild, `MCR` as a *display string* survives in:

1. **cardMCR** — card title, axis, hover, tooltip, About `what`/`how`/`source`/`caveats`, empty state, CSV.
2. **cardHoldRisk** subtitle (L7319): `"active wt × risk contrib · bubble = idio (|MCR|)"` and About entry `"bubble sized by stock-specific TE (|MCR|, the idio component)"` (L870). Already paired with the right term ("idio") — uses `|MCR|` only as parenthetical, which is OK.
3. **TE drill modal idio breakdown** L4586/L4587/L4593/L4594/L4702/L4704: `'MCR '+f2(te*idioPct/100,1)`. This is using "MCR" to label the absolute TE bps level (i.e., `te × idioPct / 100`). That's actually the conventional definition of MCR ("contribution in TE units"), so this site is **arguably correct** — different from cardMCR's misuse.
4. **cardRiskFacTbl** L6153: `data-col="mcrTE" ... "MCR to TE"`. Same as #3 — labels TE-units factor MCR. Correct.
5. **cardFacRisk drill** L6915: `'MCR to TE'`. Correct.
6. **cardFacButt drill** L7507: `'MCR: %{customdata[4]:.2f}'`. **Same bug as cardMCR** — labels `h.mcr` (= %S) as "MCR".
7. **Holdings table** L7623: column header "MCR". Same as #6.
8. **Glossary** L8393: defines MCR project-wide as "How much a single holding contributes to total portfolio tracking error. Sum of all MCRs ≈ total TE." — that's the conventional MCR definition (TE-units) but is misaligned with the cardMCR/cardFacButt/Holdings-table use which prints `h.mcr` directly (= %S, *share* not contribution-in-bps).

**Two MCRs are floating in the codebase and not distinguished from each other:**
- **MCR-idio (= h.mcr = FactSet %S = share of idiosyncratic risk per holding)** — what cardMCR / cardFacButt / Holdings table actually display.
- **MCR-TE-bps (= TE × idioPct/100 or TE × FactorContribPct/100)** — what TE drill modal / cardRiskFacTbl / glossary / cardFacRisk drill display.

Same word, two units, different magnitudes (typically `%S ≈ 0–10`, `TE × idio% ≈ 50–400 bps). PMs reading "MCR" across tiles will conflate. **This is a project-wide naming defect, not a single-tile bug.** Recommend renaming cardMCR / cardFacButt / Holdings col `%S` use to "Stock-Specific TE" or "Idio TE" and reserving "MCR" for the conventional TE-units quantity.

### 1.8 Edge / null handling

| Scenario | `rMCR` behavior | Status |
|---|---|---|
| Empty `hold` | `<p>No MCR data available</p>` (L5627) | GOOD — preserve from 2026-04-23 |
| `h.mcr` null | filtered via `isFinite` | GOOD |
| `h.mcr === 0` | filtered (`!== 0`) | GOOD — prevents zero bars padding |
| `h.mcr` NaN/Infinity | filtered via `isFinite` | GOOD |
| Fewer than 10 nonzero | renders all that exist | GOOD |
| Tie on \|mcr\| | sort-stability dependent; very low risk | OK |
| All-positive (likely the production case) | top 10 all `--pri` indigo | OK but card title's "Top & Bottom" then misleads — see B40 |
| Cash row | excluded via `isCash` | GOOD |
| `h.tkr_region` missing on a holding | `tk(h)` falls back to `h.t` | GOOD — matches commit 5e7e1b6 |
| `h.p` null | port-wt suffix omitted via `h.p!=null` guard L5637 | GOOD |
| `h.t` missing | `customdata[6]=''` L5645, click-handler then no-ops on falsy ticker | GOOD |
| `h.co \|\| h.country` both missing | hover renders `'—'` | GOOD |

**Edge handling on the rebuild is excellent.** Every node has a fallback and the tile cannot crash on missing fields. This is best-in-class for chart tiles audited so far.

### 1.9 Cross-tile data consistency

- `h.mcr` here = same field as cardHoldRisk bubble size, cardTreemap `specific` color/size mode, TE drill idio breakdown. All five sites read the same value. Color semantics now diverge between cardMCR (positive=indigo) and cardHoldRisk (positive=red). §1.4.
- `h.mcr` is also rendered as a column in the Holdings table (L7623), labeled "MCR". §1.7.
- Sector / region / group tables aggregate Σ h.mcr correctly under "Stock TE%" (L3092, L3112, L3909) — different word. §1.7.

---

## 2. Columns & Dimensions Displayed

No table — chart-only tile. Columns N/A.

---

## 3. Visualization Choice

**Section grade: YELLOW.** The chart is well constructed for what it is — top 10 horizontal bars, clean — but a 10-bar fixed view of one of the seven strategies' top-MCR holdings is a thin tile compared to its peers. cardHoldRisk now does the per-holding scatter view richly; cardMCR's job after the rebuild is the *narrow ranked top-10 view*, which is fine but redundant with what cardHoldings tab table can sort to in two clicks. See §11 (Open question on tile redundancy with cardHoldRisk).

### 3.1 Layout type

Horizontal bar chart, 10 bars, height 300px. Y axis = TKR-REGION categorical, X axis = signed `h.mcr` value. Bar text outside bars: `+1.84 · 2.3% port`.

### 3.2 Axis behavior

- **X-axis:** title "MCR (stock-specific TE component)" (L5650), `zeroline:true`, `zerolinecolor:THEME().zero`, `zerolinewidth:1.5` — GOOD.
- **Y-axis:** category, `autorange:'reversed'` (L5649) — top of chart = first in sorted order (highest positive `h.mcr`). Correct.
- **Margin override:** `l:80, r:60` (L5648) — accommodates tk(h) labels (e.g. "SIMO-US", "WIE-AT", up to ~7 char) on left and `+12.34 · 12.3% port` (~17 char at size 10) on right. Reasonable.
- **No tick format override on x-axis** — uses Plotly default. Low risk for `h.mcr` typical range (0.1–10). If a strategy emits an outlier (e.g. one holding at 30), default formatting still works.

### 3.3 Color semantics

- Positive `h.mcr` → `--pri` (indigo, hex `#8b5cf6` fallback).
- Negative `h.mcr` → `--pos` (green, hex `#10b981` fallback).
- Bar text color: `THEME().tick` — theme-aware, GOOD.
- **Drift vs cardHoldRisk:** §1.4. Same field, different palette, different narrative. Recommend swap to red/green to match cardHoldRisk.

### 3.4 Interactivity

| Capability | Pre-rebuild (2026-04-23) | Post-rebuild (2026-04-30) | Notes |
|---|---|---|---|
| Plotly hover | basic 1-line | rich multi-line via customdata | ✅ improved |
| Plotly click → drill | not wired | wired → `oSt(ticker)` via `customdata[6]` | ✅ resolves T1 from prior audit |
| Right-click note popup | missing | wired (L1962 `oncontextmenu`) | ✅ resolves T2 from prior audit |
| PNG export | present | **removed** | ✅ resolves T3 — honors `feedback_no_png_buttons.md` |
| CSV export | absent | **wired** (`exportMcrCsv` at L5654) | ✅ resolves T5 |
| Themed colors | hardcoded | `getComputedStyle` + fallback | ✅ resolves T4 |
| ⓘ About button | absent | wired (L1962 `aboutBtn('cardMCR')`) | ✅ NEW since 2026-04-23 audit |
| Card-title tip | yes | yes | — |
| Full-screen modal | absent | **still absent** | B42 unresolved |
| Filter integration | none | none | not applicable in current form |

**Five of six trivial fixes from the 2026-04-23 audit applied.** Click-drill, right-click, PNG-removal, themed colors, CSV export, ⓘ About — all landed. **The rebuild substantially closed the prior parity gap.**

### 3.5 Empty state

`<p style="color:var(--txt);font-size:12px;text-align:center;padding:60px">No MCR data available</p>` — same pattern as 2026-04-23, GOOD.

### 3.6 Responsive behavior

Fixed 300px height. The `g2` row was retired with cardFRB removal (L1957 comment) — cardMCR is now full-width on Row 8. With more horizontal real estate, the 300px height feels short and the bars look stretched. Consider 360–400px height to match cardHoldRisk's 380px (L7325).

### 3.7 Text label density

10 bars at 28–30px each + outside text labels at size 10. Project font floor = 9; passes.

---

## 4. Functionality Matrix — TRACK 2 (Parity)

**Section grade: GREEN/YELLOW.** Five of six trivial fixes from prior audit landed. Remaining gaps are full-screen (B42, NON-TRIVIAL) and the card-title-tooltip narrative cleanup.

Benchmark used: cardHoldRisk (Holdings tab sibling, same field), cardFacButt (chart peer), cardSectors (gold-standard table).

| Capability | cardSectors (gold) | cardHoldRisk (sibling, same field) | cardMCR (current) | Gap? |
|---|---|---|---|---|
| Empty-state fallback in div | yes | yes | yes | — |
| Theme-aware colors via CSS vars | yes | yes (`THEME()`) | yes (`--pri`/`--pos` lookup) | — ✅ since rebuild |
| Plotly_click → drill | N/A | yes → `oSt(ticker)` | yes → `oSt(ticker)` | — ✅ since rebuild |
| Right-click `showNotePopup` on title | yes | yes | yes | — ✅ since rebuild |
| Card-title tooltip `data-tip` | yes | yes | yes | — |
| ⓘ About button | yes | yes | yes | — ✅ since rebuild |
| PNG export button | yes (in dropdown) | no | no | — ✅ since rebuild |
| CSV export | yes | no | yes (`exportMcrCsv`) | — ✅ since rebuild |
| Full-screen ⛶ button | yes | no | **no** | open (B42 from prior audit) |
| `isFinite` filter before plot | (N/A) | yes | yes | — |
| Sign-preserving `data-sv` | yes | n/a | n/a | — |
| Axis zero-line | (N/A) | uses quadrant overlays | yes (L5650) | — |
| Keyboard a11y on clickable card | yes | n/a | n/a — chart, not card-level click | — |
| Sensitive to `_selectedWeek` | yes | no | no — same drift trap | open (B43 from prior audit) |
| Filter integration (sector, ticker) | yes | no | no | open — see §4.1 #3 |
| Tile redundancy with sibling | (different role) | overlapping w/ cardMCR by design | overlapping w/ cardHoldRisk | open — see §11 |

### 4.1 Functionality gaps — itemized (post-rebuild)

1. **No full-screen variant.** B42 unresolved. With cardScatter removed but `renderFsScatter` + `_renderFsScatPanel` orphaned at L10047/L10081, a `renderFsMCR` would be ~30 lines of skeleton-reuse: replace the scatter trace with a paginated bar chart, side panel = full sortable table of all-holdings-by-|MCR|, click bar → `oSt`. Medium effort. Not blocking.

2. **No filter integration.** Holdings tab has `secFilter` and `rankFilter` dropdowns; cardMCR ignores both (it's on Risk tab, not Holdings tab). If the user has filtered Holdings to "Information Technology only", cardMCR still shows portfolio-wide top 10. Acceptable because the tile is on a different tab, but worth a sentence in the tooltip: "Top 10 across full portfolio — not affected by Holdings tab filters."

3. **Card-title tooltip narrative not updated for the rebuild** (L1962): `"Top 10 holdings by |MCR|. Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions). Always shows latest holdings — historical MCR not persisted. Click a bar for stock detail."` 
   - "Purple" — bar color is now `--pri` token, which renders indigo not purple in dark theme. Wording is approximately right but loose.
   - "negative MCR from short or hedging positions" — same B40 hedge-narrative claim, still unverified, still likely wrong for long-only %S decomposition.
   - **Should rewrite** when B40 resolves and B39 (rename) lands. Until then, suggest: `"Top 10 holdings by |stock-specific TE| (FactSet %S). Indigo = adds idiosyncratic risk; green = offsets it. Click a bar for the stock drill."`

4. **About entry stale (L764–771).** The April-30 rebuild updated the tile but not its About:
   - L765 title: "Marginal Contribution to Risk (Top & Bottom)" — same B39 issue.
   - L766 `what`: "Top 10 + Bottom 10 holdings ranked by |MCR|" — but the chart shows top 10 not "top 10 + bottom 10". The 2-step sort (slice 10, then sign-sort) makes the top 10 inclusive of any negative-`h.mcr` outliers if they have large `|mcr|`. The wording oversells it.
   - L766 `what` continued: "Purple bars = adds risk. Green bars = reduces risk (negative MCR — typically short or hedging positions)." — same B40 narrative.
   - L770 `related`: still references `cardScatter` which was removed. **cardScatter no longer exists** → broken cross-reference.
   - **All four needs rewrite.**

5. **CSV column header `mcr_pct`** (L5657) — defect M1 from §1.5. Single edit, rename `mcr_pct` → `mcr` or `mcr_specific_te`. Honors user's "MCR is not a percentage" rule.

6. **`renderFsScatter` orphaned.** `cardScatter` DOM was removed (L1934 comment) but the renderer at L10047 + the `_renderFsScatPanel` helper at L10081 + the `'scatter'` branch in `openFullScreen()` at L9965 + `rScat` at L5485 + the About entry `cardScatter` at L708 all survive. No tile invokes them. Either: (a) wire them into a `renderFsMCR` to resolve B42, or (b) delete the orphans (~150 lines of dead code). Cleanup task either way.

7. **Tile-vs-sibling redundancy.** cardHoldRisk on Holdings tab visualizes the *same* `h.mcr` (as bubble size) plus active wt × TE contrib for all holdings, with quadrant context. cardMCR shows top 10 of `h.mcr` alone. The two tiles answer overlapping questions; PM standing question — see §11.

### 4.2 Full-screen — still does not exist

`renderFsMCR` is unbuilt. `renderFsScatter` (orphan, L10047) and `_renderFsScatPanel` (L10081) provide the skeleton. Likely 30–50 lines after refactor.

---

## 5. Popup / Drill / Expanded Card

Click any bar → `oSt(ticker)` → stock detail modal at L4254. The modal correctly labels `h.mcr` as "%S (Stock-Specific TE)" (L4314) — so once a user clicks through cardMCR to a specific holding, the language correctly resolves. **The drill side of the link works.** The mismatch is only in cardMCR's own surface labels.

No MCR-specific drill modal exists.

---

## 6. Design Guidelines — TRACK 3 (Consistency)

**Section grade: GREEN/YELLOW.** Theme adherence dramatically improved. Layout density is slightly under-utilized for the now-full-width row.

### 6.1 Density

- 300px height was sized for the old `g2` half-width slot. Now full-width (cardFRB gone). Recommend 360–400px height to match cardHoldRisk and let bars breathe horizontally.
- 10 bars at 28–30px each + outside labels — comfortable.
- Y-axis tick font 10px (L5649), bar label font 10px (L5643), x-axis title default — all at or above project font floor of 9. GOOD.
- Bar label text at 17 chars (`+12.34 · 12.3% port`) at size 10 — well within plot area when `r:60` margin is reserved (L5648). GOOD.

### 6.2 Emphasis & contrast

- Bar text uses `THEME().tick` — theme-aware. GOOD.
- Bar fill uses CSS vars — theme-aware. GOOD.
- Hover label uses Plotly default — minor inconsistency vs cardHoldRisk which sets `hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:'#475569',font:{color:'#f1f5f9',size:11,family:'DM Sans'}}` (L5450). Worth adopting same treatment for visual unity. TRIVIAL.

### 6.3 Alignment

- Default plot margins. Y-axis labels left-aligned (categorical). X-axis numeric. GOOD.

### 6.4 Whitespace / padding

- Standard `.card` base. `flex-between` header (L1962). OK.
- Export bar contains only a CSV button now (PNG removed). The bar is not centered, sits right-aligned per `flex-between`. OK.

### 6.5 Motion / feedback

- Plotly default hover only. No bar-highlight on hover. Fine for 10 bars.
- Click → `oSt` modal animation. Standard.

### 6.6 Theme adherence — post-rebuild scorecard

| Element | Before | After | Status |
|---|---|---|---|
| Bar fill colors | hardcoded hex | `getComputedStyle().getPropertyValue('--pri'/'--pos')` + hex fallback | ✅ |
| Bar text color | `THEME().tick` | unchanged | — |
| Zero line color | `THEME().zero` | unchanged | — |
| Hover label style | Plotly default | Plotly default | inconsistent vs cardHoldRisk — minor |
| Y-axis tick color | inherited | inherited | — |

### 6.7 About registry consistency

- About entry `cardMCR` at L764 was **not updated during the rebuild**. Three of its fields are now stale:
  - **`title`** still says "Marginal Contribution to Risk (Top & Bottom)" — matches the card title; both will rename together when B39 resolves.
  - **`what`** still narrates the "Purple bars = adds risk, green = reduces risk (negative MCR — typically short or hedging positions)" line — which is the unverified hedge claim from B40 plus references "Purple" not "indigo" plus references "Top 10 + Bottom 10" which the rebuild silently turned into a sign-sorted top-10.
  - **`how`** still says "MCR = h.mcr (FactSet %S, the stock-specific TE component for each holding)" — *correct*, this line is fine; in fact this is the most candid acknowledgment in the codebase that the field name is wrong.
  - **`source`** is correct.
  - **`caveats`** still says "MCR not historized" — correct.
  - **`related`** references **cardScatter which no longer exists** (`'cardScatter · cardHoldings · TE drill modal Idio breakdown'`). Should rewrite to `'cardHoldRisk · cardHoldings · TE drill modal Idio breakdown'`.

### 6.8 Consistency issues — itemized list

1. **Card title still says "Marginal Contribution to Risk"** while `h.mcr` is `%S` per parser + project-wide convention. (B39 from prior audit, unresolved.)
2. **About entry stale** — title, `what`, `related` all need refresh.
3. **About `related` references removed cardScatter** — broken cross-reference.
4. **CSV header column `mcr_pct`** violates "MCR is not a percentage" rule (M1, NEW).
5. **Color choice diverges from same-field sibling cardHoldRisk** (positive=indigo here, positive=red there). Recommend harmonizing on red/green.
6. **300px height under-utilized for full-row layout.** Recommend 360–400px to match cardHoldRisk.
7. **No hover-label styling override** — inconsistent vs cardHoldRisk's themed hover-label.
8. **Card-title tooltip narrative** not updated for rebuild ("Purple", "negative MCR from short or hedging positions").
9. **No full-screen ⛶ button** (B42, unresolved). Less critical now that `renderFsScatter` provides a clear skeleton if/when this is built.

---

## 7. Verification Checklist (post-rebuild)

- [x] **Data path:** `s.hold[].mcr` from parser `PCT_S` — unchanged, traced.
- [x] **Empty state:** `<p>No MCR data available</p>` — preserved.
- [x] **`isFinite` + cash filter** — preserved.
- [x] **Non-zero filter** — preserved.
- [x] **Zero-line on x-axis** — preserved.
- [x] **`plotly_click` → `oSt(ticker)`** — wired (L5652). RESOLVED.
- [x] **Right-click → `showNotePopup(event,'cardMCR')`** — wired (L1962). RESOLVED.
- [x] **Theme-aware bar colors** — `getComputedStyle` (L5629–5630). RESOLVED.
- [x] **PNG button removed.** RESOLVED.
- [x] **CSV export wired** — `exportMcrCsv` (L5654). RESOLVED.
- [x] **ⓘ About button.** RESOLVED.
- [x] **TKR-REGION display via `tk(h)`.** RESOLVED.
- [x] **Bar label MCR rendered without `%`.** Verified — bar text format is `+1.84 · 2.3% port` (the `%` is on the port-wt suffix, where `%` is correct).
- [x] **X-axis title rendered without `%`.** Verified — "MCR (stock-specific TE component)".
- [x] **Hovertemplate MCR rendered without `%`.** Verified — `MCR (stock-specific TE): %{x:.2f}` (no trailing `%`).
- [ ] **CSV column header for MCR** — `mcr_pct` violates rule. M1, NEW DEFECT.
- [ ] **Card title says "Marginal Contribution to Risk"** but field is `%S` — B39 unresolved.
- [ ] **About entry stale** (title, what, related).
- [ ] **B40 hedge narrative** unverified.
- [ ] **Color choice diverges** from cardHoldRisk sibling (positive=indigo here, positive=red there).
- [ ] **B42 full-screen** absent.
- [ ] **Production-data spot-check** pending loaded JSON.

---

## 8. Track-by-track grades

| Track | Pre-rebuild (2026-04-23) | Post-rebuild (2026-04-30) | Δ |
|---|---|---|---|
| Track 1: Data Accuracy | RED | YELLOW | UP one notch — `%`-on-MCR rule honored at all chart-display sites; B39 (rename) still open; M1 CSV-header is a small new finding |
| Track 2: Functionality Parity | YELLOW | GREEN/YELLOW | UP — 5 of 6 trivials applied; B42 full-screen still absent |
| Track 3: Design Consistency | YELLOW | GREEN/YELLOW | UP — themed colors landed; About-entry staleness + color-choice divergence vs cardHoldRisk are open |

**Overall tile grade: YELLOW (up from RED).** The rebuild moved this from "do-not-promote" to "near-ship". Three blockers remain: (1) B39 rename — needs PM call; (2) M1 CSV header `mcr_pct` — TRIVIAL, can apply now; (3) About-entry refresh including the stale cardScatter cross-ref — TRIVIAL.

---

## 9. Known Issues & Open Questions (post-rebuild)

### Carried over (re-graded)

- **B39 (UNRESOLVED, downgraded from RED to YELLOW):** card title / About title / About `what` still say "Marginal Contribution to Risk" while field is FactSet `%S`. Rebuild moved every chart-display site (axis, hover, bar text) into a parenthetical "stock-specific TE component" so the worst PM-facing miscommunication is now defused, but the canonical card title remains. **Cannot fix without the rename PM call** (originally paired with cardScatter B20 — but cardScatter no longer exists, so cardMCR is now solo on this rename and the PM call is independent). 
  - **Recommended new title:** "Top Idiosyncratic Risk Contributors" or "Top Stock-Specific TE Holdings".
  - **Codebase ripple:** L1962 card title, L1962 tooltip, L766 About title, L766 About `what`, L770 About `related`, L5650 axis title, L5646 hover line, L5627 empty state, L5657 CSV header.

- **B40 (UNRESOLVED):** "negative MCR from short or hedging positions" — narrative claim about negative `%S`. Standard FactSet `%S` is variance-share, non-negative for long-only. PM needs to confirm whether any production strategy emits negative `h.mcr`. If no, "Top & Bottom" framing is wrong; if yes, investigate parser sign convention. Spot-check pending loaded JSON.

- **B41 (PARTIALLY RESOLVED):** color semantic. The hardcoded-hex defect is fixed (CSS vars now). The *choice* of indigo-for-positive remains, and now diverges from cardHoldRisk's red-for-positive. Re-graded YELLOW. Recommend match cardHoldRisk = red(adds risk) / green(diversifies). PM gate but cardHoldRisk already passed it.

- **B42 (UNRESOLVED):** no full-screen variant. With `renderFsScatter` orphaned, the skeleton is freely available. Medium-effort task.

- **B43 (PARTIALLY RESOLVED):** week-selector latest-only drift. The 2026-04-30 tooltip adds "Always shows latest holdings — historical MCR not persisted." (L1962). ✅ The disclaimer landed. Tile still uses the word "MCR" in the disclaimer; will rename with B39.

- **B44 (RESOLVED):** CSV export wired. `exportMcrCsv` (L5654) emits `ticker,name,sector,port_pct,active_pct,mcr_pct,te_contribution` for all non-cash, nonzero-`mcr` holdings, sorted by `|mcr|` desc. (Defect M1 = column header, not the export itself.)

### NEW since 2026-04-30 rebuild

- **M1 (NEW, TRIVIAL):** CSV column header `mcr_pct` (L5657) violates "MCR is not a percentage" rule. Rename `mcr_pct` → `mcr` or `mcr_specific_te`. 1-line fix.

- **M2 (NEW, TRIVIAL):** About entry `related` field references removed `cardScatter` (L770). Rewrite as `'cardHoldRisk · cardHoldings · TE drill modal Idio breakdown'`.

- **M3 (NEW, TRIVIAL):** About entry `what` describes pre-rebuild behavior ("Top 10 + Bottom 10") and uses "Purple" wording. Refresh to match the actual ranked top-10 + sign-sort behavior, and use theme-neutral language ("indigo" or "the positive-color bars").

- **M4 (NEW, TRIVIAL):** card-title tooltip narrative still says "Purple = adds risk, green = reduces risk (negative MCR from short or hedging positions)". Same content issue as B40 + theme-color-name issue ("Purple"). Rewrite when B39 lands.

- **M5 (NEW, NON-TRIVIAL):** **`renderFsScatter` orphaned.** With cardScatter DOM removed, the FS-scatter renderer + `_renderFsScatPanel` + `'scatter'` branch in `openFullScreen` + `rScat` itself + the About entry `cardScatter` are all dead code (~150 lines). Either reuse the skeleton for `renderFsMCR` (B42) or delete. Cleanup task either way; don't ship unused code.

- **M6 (NEW, OBSERVATION):** **Project-wide MCR vocabulary drift.** Per §1.7, "MCR" is being used in the codebase for two different quantities: (a) `h.mcr` = `%S` = share-of-idio-TE (cardMCR, cardFacButt drill, Holdings table column header), and (b) TE × idioPct/100 = idio-TE in bps (TE drill modal, cardRiskFacTbl `MCR to TE`, glossary L8393). Two units, same word. **Project-level convention call needed**, not single-tile fix. Recommend: rename (a) sites to "Stock-Specific TE" / "%S" / "Idio TE"; reserve "MCR" for (b).

### Open questions for PM

- **Q1 (B39):** Accept the rename "Marginal Contribution to Risk" → "Top Idiosyncratic Risk Contributors" (or PM's preferred phrasing) on cardMCR? The rebuild defused the worst PM-facing miscommunication via parentheticals, but the card title is the dashboard's primary surface and still misleads a fresh-eye PM.
- **Q2 (B40):** Does any production strategy emit negative `h.mcr`? If none, "Top & Bottom" wording is misleading and "negative-MCR-from-shorts" narrative is fiction.
- **Q3 (B41):** Match cardHoldRisk's red(adds-risk)/green(diversifies) palette on cardMCR? Strong recommend yes.
- **Q4 (Big one — see §11):** **Tile redundancy with cardHoldRisk.** cardHoldRisk now does per-holding active-wt × TE-contrib × |MCR| richly on the Holdings tab. cardMCR shows the same data restricted to top-10 by |%S|. Should cardMCR be (a) kept as-is on Risk tab as a focused top-10 view, (b) merged into cardHoldRisk by adding a "Top 10 by |MCR|" highlight overlay, (c) moved to Holdings tab to live next to cardHoldRisk, (d) reframed as a "Risk Concentration" view (idio-TE Herfindahl, top-10 share of total %S, etc.) that *isn't* duplicated by cardHoldRisk?

---

## 10. Proposed Fix Queue (post-rebuild)

### TRIVIAL (agent can apply, ≤5 lines each, no PM judgment)

T1. **M1 — Rename CSV header `mcr_pct` → `mcr`** at L5657. 1 line.
```js
let lines=['ticker,name,sector,port_pct,active_pct,mcr,te_contribution'];
```

T2. **M2 — Update About `related` field** at L770:
```js
related:'cardHoldRisk · cardHoldings · TE drill modal Idio breakdown'
```

T3. **M3 — Refresh About `what` field** at L766. Replace with text that matches the rebuilt behavior + drops the Purple/Bottom narrative until B39/B40 resolve. Suggested:
```js
what:'Top 10 holdings ranked by |stock-specific TE| (FactSet %S — the per-holding idiosyncratic TE component). Bars sign-sorted: positive contributors above the zero-line, any negative-%S holdings below. Each bar shows the signed value plus the holding\'s portfolio weight for context. Click any bar to drill into the stock detail.'
```

T4. **M4 — Refresh card-title tooltip** at L1962 to match rebuild + de-color-namify. Suggested:
```html
data-tip="Top 10 holdings by |stock-specific TE| (FactSet %S, the per-holding idio component). Indigo bars = adds idiosyncratic risk; green bars = offsets it (rare; usually shorts/hedges if present). Latest holdings only — historical %S not persisted. Click a bar for stock detail."
```

T5. **Refresh About `caveats` and About title together when B39 lands** (PM-gated — see Q1 / B39).

T6. **(Design polish) Increase `mcrDiv` height** L1964 from `300px` to `360px` to match cardHoldRisk now that cardMCR has the full row.

T7. **(Design polish) Add hover-label styling** in the Plotly newPlot config (after L5650) to match cardHoldRisk:
```js
hoverlabel:{bgcolor:'rgba(15,23,42,0.96)',bordercolor:'#475569',font:{color:'#f1f5f9',size:11,family:'DM Sans'}}
```

### NEEDS PM DECISION

P1. **B39 rename wording.** "Top Idiosyncratic Risk Contributors" / "Top Stock-Specific TE" / other. Now solo (cardScatter removed) so PM call doesn't have to coordinate two tiles.

P2. **B40 negative-`%S` semantics.** Spot-check on EM / IDM / GSC JSONs whether any holding has `h.mcr < 0`.

P3. **B41 color choice.** Match cardHoldRisk red/green? Strong recommend yes.

P4. **Q4 — Tile redundancy with cardHoldRisk.** Four options listed in §9 / §11.

### NON-TRIVIAL (B-id backlog)

B39. **"MCR" → domain-correct rename** on cardMCR (8 ripple sites listed in §9). Now solo since cardScatter is gone.

B40. **Verify negative `%S` legitimacy** in production data.

B42. **Full-screen `renderFsMCR`** — reuse `renderFsScatter` orphan skeleton (M5). 30–50 lines.

M5. **Decide: reuse `renderFsScatter` for cardMCR's FS, or delete the orphan** (~150 lines). Cleanup task either way.

M6. **Project-wide MCR vocabulary clean-up** — disambiguate %S (per-holding idio share) from MCR-bps (TE-units factor MCR). Spans cardMCR, cardFacButt drill (L7507), Holdings table col (L7623), glossary L8393. Multi-tile coordination.

---

## 11. Tile redundancy with cardHoldRisk — strategic question

User wrote: "marginal contribution to risk also must be presented elsewhere and if not needs a much better tile". The 2026-04-30 rebuild took the second path (better tile) but, in parallel, cardHoldRisk also shipped on the Holdings tab and now presents per-holding `|h.mcr|` as bubble size on a quadrant scatter. The two tiles now overlap.

| Question | cardMCR (Risk tab) | cardHoldRisk (Holdings tab) |
|---|---|---|
| What's the data | top 10 by `\|h.mcr\|` | all holdings by `h.a × h.tr` with bubble = `\|h.mcr\|` |
| Why I'd look at it | "which 10 stocks drive my idio risk most" | "what's the structure of risk across all holdings" |
| Where it lives | Risk tab Row 8 (was paired w/ cardFRB which got removed) | Holdings tab top |
| Already-shipped strength | focused, ranked, signed | rich quadrant context, color-coded direction |
| Already-shipped weakness | only 10 rows; redundant w/ "sort Holdings by %S" | doesn't rank, can't see the top names without hovering |

**Four resolution options:**

1. **Keep both as-is (status quo).** Pro: each has a distinct visual answer ("ranked list" vs "structural quadrant"). Con: same field, two places, slight maintenance overhead.
2. **Add a "Top 10 by |MCR|" highlight overlay on cardHoldRisk.** Bold the top-10 bubbles and show their tickers prominently. Then cardMCR can be retired. Pro: one tile, no overlap. Con: cardHoldRisk gets visually busy.
3. **Move cardMCR to the Holdings tab next to cardHoldRisk.** Both tiles co-located, user sees ranked + structural side by side. Pro: discoverability. Con: Risk tab loses a holdings-level tile (it currently has cardMCR + cardUnowned).
4. **Reframe cardMCR as "TE Concentration".** Drop the per-holding bar chart; instead show: (a) idio-TE Herfindahl index (concentration), (b) top-10 share of total `Σ|h.mcr|`, (c) compare to total-TE concentration from cardHoldings (the `_concPill` at L7311 does this for `\|h.tr\|`). This makes cardMCR answer a question cardHoldRisk *can't* — concentration risk — and removes the redundancy. Pro: portfolio-level risk-summary tile, distinct from holding-level views. Con: more design work; bigger reframing.

**Recommendation:** option (4) is the strongest "much better tile" interpretation of the user's original note. Option (1) is fine status-quo if PM accepts the overlap. Options (2)/(3) are intermediate. Decision should be made before B39 rename so the renamed title can match the new role.

---

## 12. Change log

| Date | What | Who |
|---|---|---|
| 2026-04-23 | Initial audit. RED/YELLOW/YELLOW. 6 trivials + 6 non-trivials (B39–B44). | tile-audit CLI |
| 2026-04-30 | Rebuild commit 2eff789: bar labels expanded, tk(h) on y-axis, rich hover, click-drill via customdata, themed colors, CSV export, ⓘ About wired, PNG removed, right-click added, week-selector disclaimer added. | main session |
| 2026-04-30 | This re-audit. YELLOW/GREEN-YELLOW/GREEN-YELLOW. B44 RESOLVED, B43/B41 PARTIAL, B39/B40/B42 still open. M1–M6 new findings. | tile-audit CLI |

---

## 13. Sign-off

**Status:** `data-verified` candidate — promote after T1 (M1 CSV header rename) + T2 (About `related` cardScatter removal) + T3 (About `what` refresh) + T4 (tooltip refresh) land. **Final `signed-off` requires user in-browser review** per `feedback_signoff_requires_user_review.md`. The rebuild closed 5 of 6 trivials from the prior audit — substantial progress. The lingering domain-term mismatch (B39) is a single-PM-decision blocker that, if resolved, would push this tile to GREEN/GREEN/GREEN.

**Color status by section:**
- Section 1 (Data Source / Accuracy): **YELLOW** — `%`-on-MCR rule honored at all chart sites; B39 unresolved; M1 CSV header is a 1-line fix.
- Section 4 (Functionality Parity): **GREEN/YELLOW** — 5 of 6 prior trivials applied; B42 full-screen still absent (low-priority for a top-10 tile).
- Section 6 (Design Consistency): **GREEN/YELLOW** — themed colors + ⓘ About + CSV all landed; About-entry staleness + color-divergence vs cardHoldRisk are open.

**Overall tile grade: YELLOW** — substantial improvement from RED. Recommend ship-after-trivials with PM call on B39/Q4 in parallel.
