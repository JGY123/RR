# Dashboard Number Sources — Provenance Index

**Drafted:** 2026-04-27
**Why:** every number visible on the dashboard needs a clear source so PMs can run sanity checks. Numbers come from one of three places:

1. **🟢 SOURCED** — directly from FactSet CSV. We can point at table + column.
2. **🟡 DERIVED** — computed from sourced fields. Math is documented; result is a sanity-check, NOT a substitute for real data. UI marks these with `ᵉ` (derived) badge or `(est)` qualifier.
3. **⚫ EMPTY** — value not shipped in current CSV; UI shows `—` and explains why on hover.

**Anti-fabrication policy (2026-04-27):** if a field is sourced, show the real number. If derived, mark visibly. **Never substitute a fabricated value that looks real.** If neither, show `—` — failing-to-display surfaces gaps in the data, which is the correct behavior.

---

## cardThisWeek (top of Exposures tab)

| Cell | Source class | Path |
|---|---|---|
| Tracking Error big number | 🟢 sourced | Portfolio Characteristics → "Predicted Tracking Error (Std Dev):P" → `parser.sum.te` |
| Idiosyncratic Risk % | 🟡 derived from aggregation (2026-04-28 update) | RiskM section was retired; FactSet did NOT carry portfolio-level % Asset Specific Risk forward to 18 Style Snapshot. Per user direction: derive `pct_specific = Σ(sector mcr)` since no sectors are hidden anymore (Σ sector %T = 100 confirms no missing buckets). Marker: `_pct_specific_source: 'sum_sector_mcr'` on the strategy. |
| Factor Risk % | 🟡 derived | `pct_factor = 100 − pct_specific` (math identity). Marker: `_pct_factor_source: '100_minus_pct_specific'`. |
| State bullets | 🟢 sourced + 🟡 derived | TE/AS/Beta from `parser.sum`; "largest overweight is X" from `cs.sectors[]` sort. Composition logic in `thisWeekCardHtml`. |
| 3-week trend arrow | 🟢 sourced | `cs.hist.sum[]` last 3 entries → `gt()` helper |

## cardSectors (Sector Active Weights table)

| Column | Source class | Path |
|---|---|---|
| Sector | 🟢 sourced | Sector Weights section → Level2 |
| PORT% (`p`) | 🟢 sourced | Sector Weights → `W` column |
| BENCH% (`b`) | 🟢 sourced | Sector Weights → `BW` column |
| ACTIVE (`a`) | 🟢 sourced | Sector Weights → `AW` column |
| TE Contrib (`tr`) | 🟢 sourced | Sector Weights → `%T` column |
| Stock TE% (`mcr`) | 🟢 sourced | Sector Weights → `%S` column |
| Factor TE% | 🟡 derived | `tr - mcr` (math identity) |
| O/R/V/Q rank cells | 🟢 sourced | Sector Weights → `OVER_WAVG`/`REV_WAVG`/`VAL_WAVG`/`QUAL_WAVG` |
| Trend column | ⚫ empty | `hist.sec` not populated (B6 backlog) |

## cardFacDetail (Factor Detail table)

| Column | Source class | Path |
|---|---|---|
| Factor name | 🟢 sourced | RiskM section / 18 Style Snapshot — factor names |
| **Active Exp** (`f.a`) | 🟢 sourced (some factors) / 🟡 fallback chain | Primary: parser populates from RiskM `active_factor_cols` (when present in CSV). Fallback: `f.e` (raw exposure), then `sum._fe[name]`, else null. Marker: `ᵉ` when fallback used. |
| **TE%** (`f.c`) | 🟡 derived | **Currently always synthesized** (FACTSET_FEEDBACK F5). Math: `\|f.a\| × f.dev → normalized so all factors sum to pct_factor`. Marker: `ᵉ` superscript. **The 15.1% Size case is exactly this synthesis.** |
| Return (`f.ret`) | 🟢 sourced | 18 Style Snapshot → `SNAP_RET` |
| Impact (`f.imp`) | 🟢 sourced + 🟡 period-aggregated | 18 Style Snapshot → `SNAP_IMP`. When period selector ≠ 'Latest': `getImpactForPeriod()` sums hist[] entries within the window. Hover shows actual date range. |

## cardFacButt — Factor Risk Map "Top TE Contributors" pills

| Pill content | Source class | Path |
|---|---|---|
| Factor name | 🟢 sourced | from `cs.factors[]` |
| Active σ | 🟢 sourced | `f.a` |
| % TE | 🟡 derived | Same as cardFacDetail TE% — synthesized via `\|a\|×σ → normalized`. Same `ᵉ` marker should apply. **TODO: pending UI marker propagation when this tile comes up in marathon.** |

## cardFRB — Factor Risk Budget donut

| Slice value | Source class | Path |
|---|---|---|
| Per-factor % | 🟡 derived | Reads `f.c` post-synthesis. Same fallback lineage as cardFacDetail TE%. |
| Total | 🟢 sourced | `pct_factor` from RiskM |

## cardHoldings (Top-N holdings)

| Column | Source class | Path |
|---|---|---|
| Ticker | 🟢 sourced | Security section Level2 → `h.t` (mixed identifier today; B113 will pass through clean `tkr` from `data/security_ref.json`) |
| Name | 🟢 sourced | Security section col 6 |
| Sector | 🟢 sourced | Security section col 8 → `h.sec` |
| Country | 🟡 derived | Enriched at parse time from `data/security_ref.json` keyed by SEDOL. 97% coverage. Marker: TBD when displayed. |
| Currency | 🟡 derived | Same enrichment path as Country |
| Industry | 🟡 derived | Same enrichment path |
| PORT% / BENCH% / ACTIVE | 🟢 sourced | Security section `W`/`BW`/`AW` |
| %S / %T / TOTAL TE% | 🟢 sourced | Security section `%S`/`%T`/`%T_Check` |
| RBE | 🟢 sourced | Security section `OVER_WAvg` |

## cardCountry / cardRegion / cardGroups / cardIndustries (aggregate tables)

Same column shape as cardSectors. Sourced from their respective CSV sections (Country / Region / Group / Industry).

### Spotlight pattern rollout (B106, 2026-04-27) — applies to cardSectors, cardCountry, cardRegions, cardGroups

Each of the 4 sibling aggregation tiles received a uniform column set, all driven by the global `_aggMode` (Port / Bench / Both pill in header):

| Cell | Source class | Path |
|---|---|---|
| TE Contrib | 🟢 sourced + 🟡 derived (filter) | `Σ h.tr` across this bucket's holdings filtered by `_aggMode`. `h.tr` is sourced from CSV Security `%T`. The bucket-sum + universe filter is derived. |
| Stock TE% | 🟢 sourced + 🟡 derived (filter) | `Σ h.mcr` across this bucket's holdings filtered by `_aggMode`. `h.mcr` is sourced from CSV Security `%S` column. |
| Factor TE% | 🟡 derived | `TE Contrib − Stock TE%` (math identity from the two above). |
| Avg O / R / V / Q | 🟡 derived (per-tile) | Weighted/simple/bench-weighted averages of `h.over` / `h.rev` / `h.val` / `h.qual` per bucket. Driven by `_secRankMode` (Wtd/Avg/BM toggle) — separate from `_aggMode`. Wtd & BM apply port-weight or bench-weight independent of the Agg pill; Avg is universe-agnostic. |
| Mom · Val · Gro · Prof · Size · Vol | 🟢 sourced + 🟡 derived (filter + sum) | `Σ h.factor_contr[fname]` per bucket, filtered by `_aggMode`. `h.factor_contr` is sourced from CSV Security factor-attribution section (per-holding × per-factor contribution). Bucket-sum is derived. The column header tooltip names the exact factor it sums. |
| `Factor TE Breakdown` band header | UI affordance | Visual sub-header with current `_aggMode` label so users know which universe drives the 6 sums below. |

Aggregation helper: `aggregateHoldingsBy(holds, groupKeyFn, factorList, opts)` (line ~2065). `groupKeyFn` accepts string-key (sector/country/region) or array-key (groups, since holdings can belong to multiple subgroups via GROUPS_DEF mapping). `opts.mode` is `'portfolio' | 'benchmark' | 'both'` and filters by `h.p>0` / `h.b>0` / no-filter respectively before aggregating.

`setAggMode(mode)` re-renders all 4 sibling tiles in lockstep so the universe pill flips them together. cardIndustries deferred (more nuance — multi-industry membership semantics).

## cardWatchlist

| Field | Source class | Path |
|---|---|---|
| Watchlist tickers | 🟢 sourced | localStorage `rr_flags_${strategyId}` |
| Per-ticker p / a | 🟢 sourced | Joined to `cs.hold[]` at render time. EXITED chip when ticker no longer in `cs.hold[]`. |

## cardChars (Portfolio Characteristics — 39 metrics, 2026-04-30 audit fixes)

| Cell | Source class | Path |
|---|---|---|
| Portfolio value (`c.p`) | 🟢 sourced | `cs.chars[].p` — every metric extracted by parser `_build_chars()` (factset_parser.py L1239) from FactSet "Portfolio Characteristics" section. Header-driven; 39 :P/:B column pairs become 39 metric rows. |
| Benchmark value (`c.b`) | 🟢 sourced or ⚫ empty | `cs.chars[].b`. NULL for portfolio-only metrics (TE, Active Share — no benchmark equivalent). |
| Diff cell | 🟡 derived | Computed `c.p - c.b` at render time (rChr L3322). Cell color via `charDiffClass(metric, diff)` — flips for "lower-is-better" metrics in `CHAR_META.inverted` set. |
| Group header (Risk/Valuation/etc) | 🟡 derived | `CHAR_META[c.m].group` static metadata. Unknown metrics fall through to "Other" bucket so new FactSet columns appear without code change. |
| Per-row tooltip | 🟢 sourced (CHAR_META static) | `data-tip` from `CHAR_META[c.m].doc`. One-line definition per metric. |
| Inverted (↓) marker | 🟢 sourced (CHAR_META static) | `CHAR_META[c.m].inverted === true`. Set: P/E variants, P/B, EV/SALES, EV/EBITDA, P/CF, P/S, Net Debt/Mcap, LT Debt to Capital. |
| ● history-shipped marker | 🟡 derived | `CHAR_META[c.m].histKey` truthy. Set: TE/Beta/Active Share (3 of 39). Other 36 await parser-side history persistence (B114). |
| Unit-aware formatter | 🟡 derived | `formatChar(metric, v)` reads `CHAR_META[metric].fmt` ∈ {pct, mult, beta, usdB, num}. |

## cardCalHeat (TE Calendar Heatmap, NEW 2026-04-30)

| Cell | Source class | Path |
|---|---|---|
| Year × Week grid | 🟡 derived | Built from `cs.hist.sum[]` — every entry's `d` parsed via `parseDate` then bucketed by `(getFullYear, isoWeekNum)`. ISO 8601 week numbering (Thursday-anchored). Helper: `isoWeekNum(d)` near line 10026. |
| Cell color (|ΔTE| mode, default) | 🟡 derived | `dteAbs = Math.abs(te[i] - te[i-1])`. **Marked ᵉ** in hover template ("ΔTEᵉ"). Synth marker rationale: ΔTE is a same-tile derivation that doesn't write to `cs.*` — derivation visible in code only. |
| Cell color (TE level mode) | 🟢 sourced | `cs.hist.sum[].te` — same field as cardRiskHistTrends miniTE. |
| Hover tooltip | 🟢 sourced + 🟡 derived | `customdata = [isoDate(d), te, dte]` per cell. `te` sourced; `dte` derived (marked ᵉ). |
| Selected-week outline | UI state | `_selectedWeek` global → resolved to (year, week) and rendered as Plotly `shapes` rect. |
| Click handler | UI behavior | `plotly_click` → `customdata[0]` → `changeWeek(YYYYMMDD)` (existing global). Triggers full re-render including this tile's selection outline. |
| Color metric pill state | UI state | `localStorage.rr.calheat.metric` ∈ {`'dte'`, `'te'`}. Per CLAUDE.md hard rule #3 — preferences-only, never data. |
| Legend strip values | 🟡 derived | min/max of currently-rendered `z` matrix flattened. Recomputed on every `rCalHeat()` call. |

### Drill modal `oDrChar(metric, range)`

| Cell | Source class | Path |
|---|---|---|
| Big Port / Bench / Diff stat cards | 🟢 sourced + 🟡 derived | Same fields as the row, formatted via `formatChar`. Diff color via `charDiffClass`. |
| 5-stat history strip (Min/Avg/Max/σ/Pctile) | 🟢 sourced | Computed from `cs.hist.sum[].KEY` where KEY ∈ {te, beta, as} — sliced to the selected range (3M/6M/1Y/3Y/All). |
| History line chart | 🟢 sourced | `cs.hist.sum[]` with the same KEY. Avg reference line via dotted shape. Y-axis tick suffix (% / x / B / —) from `CHAR_META[metric].fmt`. |
| "No per-week history" callout | ⚫ empty (with explanation) | For metrics where `CHAR_META[metric].histKey` is unset. Names B114 explicitly so PMs see the gap → not silent. |

## cardRiskByDim — TE Contribution by Country / Currency / Industry (NEW B102, 2026-04-27)

| Cell | Source class | Path |
|---|---|---|
| Bar chart bars | 🟢 sourced + 🟡 derived (aggregation) | Per-bucket value = sum of `h.tr` for holdings where `h[dim] === bucketName`. `h.tr` is sourced from CSV's Security section `%T` column. The aggregation by dim (country/currency/industry) is a derived sum. |
| Bucket labels | 🟡 derived (security_ref enrichment) | `h.country` / `h.currency` / `h.industry` come from `data/security_ref.json` lookup keyed by SEDOL (97% coverage; 3-15% fall through to "Unmapped" bucket). The mapping is hardcoded from FactSet's static reference Excel. |
| "Unmapped" bucket | 🟡 derived (catch-all) | Holdings where `h[dim]` is null or empty after enrichment. Counted in footer with `⚠` chip. |
| Footer "X bucket" count | 🟡 derived | `Object.keys(buckets).length` |
| Footer "total |TE| coverage" | 🟡 derived | `Σ |bucket.total_tr|` — sums absolute magnitudes (so >100% if any buckets are diversifying). |
| Drill modal stat cards | 🟢 sourced | `h.tr` / `h.p` / `h.b` summed across holdings in the clicked bucket. |
| Drill modal table | 🟢 sourced | Direct read of `cs.hold[]` filtered by `h[dim]`. |
| Threshold slider | UI state | `_rbdThresh` localStorage `rr.cardRiskByDim.thresh`, default 0.5% |
| Active dimension | UI state | `_rbdDim` localStorage `rr.cardRiskByDim.dim`, default 'country' |

## Risk tab tiles

(See cardRiskHistTrends, cardTEStacked, cardRiskFacTbl, cardFacContribBars sections in `tile-specs/*.md`. Most read directly from `cs.factors[]` / `cs.hist.sum` / `cs.snap_attrib` — sourced. cardTEStacked has a known math issue per B96 where `pct_specific`/`pct_factor` are interpreted as TE-shares but per CSV spec they're "% of Total Risk".)

### F18 contamination map (2026-05-04) — which tiles aggregate per-holding %T

F18 is the open inquiry on per-holding `%T` summing to 94→134% across strategies (vs. CLAUDE.md-stated ~100%). When tracing a "wacky number," use this map to know if a tile is on the contaminated side or the L2-verified side.

| Tile / View | Aggregates per-holding %T? | Path | Contaminated by F18? | Defensive UI? |
|---|---|---|---|---|
| **cardRiskByDim** | YES — Σ h.tr by Country / Currency / Industry, totals row visible | per-holding | **YES** | YES — footer shows Σ %T = X% with F18 link (L8520) |
| **cardSectors / cardCountry / cardGroups / cardRegions** | NO — per-row only, no totals row visible | per-bucket (sector/country/etc.) | NO — per-row values are L2-verified (Σ section %TE = 100% on 3,082/3,082 weeks per `verify_section_aggregates.py`) | n/a — no Σ shown |
| **cardTEStacked** | NO — sits on portfolio-level pct_specific/pct_factor (not per-holding) | section-aggregate via F12(a) tier-2 / source-direct via F19 tier-1 | NO | YES — three-tier provenance footer |
| **cardFacContribBars** | NO — reads `cs.factors[].c` (factor MCR) | factor-aggregate | NO | YES — disclosure footer (visible/total + Σ \|c\| explained) |
| **cardFacHist** | NO — per-factor exposure / return | factor-aggregate / snap_attrib | NO | YES — ᵉ marker on Cum Return + snap_attrib fallback |
| **cardCorr** | NO — pairwise factor correlations | factor-aggregate | NO | YES — universe-invariance disclosure |
| **cardBetaHist** | NO — single per-week β scalar | portfolio-level | NO | n/a |
| **cardRanks** (Spotlight rank table) | YES — Σ h.tr per quintile (TE Contrib column) | per-holding | **YES at quintile-Σ level** | YES — F18 footer shipped 2026-05-04 ✓ |
| **cardRankDist** (port-weight histogram) | NO — bar heights are port weight only, not %T | per-quintile port weight | NO | n/a — universe-coverage only |
| **cardHoldRisk** | NO — per-holding scatter (each dot is one h.tr) | per-row | YES — but each dot is a single value, not a Σ | n/a |
| **cardRiskDecomp** (idio sub-tree) | YES — top-7 idio leaves are h.tr values | per-holding | **YES at top-7-Σ level** (Σ |top-7| often > parent due to F18) | YES — F18 footer + leaf ᵉ markers shipped 2026-05-04 ✓ |
| **cardTreemap (Size=TE mode)** | YES — leaf areas are |h.tr| | per-holding | **YES** at total-leaf level | YES — F18 footer (visible only when Size=TE) shipped 2026-05-04 ✓ |
| **cardTreemap (Size=Weight or Count)** | NO — h.p portfolio weight or simple count | per-row | NO | n/a |
| **cardUnowned** | per-row only (no aggregate) | per-holding | per-row clean (F12 long-tail = '—' now after T1.1 fix) | YES — provenance footer shipped 2026-05-04 ✓ (M of N has shipped %T disclosure) |

Rule: **any tile that displays a sum of per-holding %T values needs an F18 disclosure footer.** Per-row displays are clean. Section-aggregate displays are clean (L2-verified). Per-strategy total of per-holding %T is the F18 finding.

### cardTEStacked — per-week Idio/Factor split (F12(a) + F19, 2026-05-04)

The Idio/Factor decomposition over time uses a three-tier provenance resolution. Every per-week point on the chart now carries one of these three sources, surfaced in the chart footer caveat:

| Tier | Source | When used | Marker |
|---|---|---|---|
| **1 — Source-direct** | `cs.hist.sum[i].pct_specific` / `.pct_factor` (parser-shipped, FORMAT_VERSION ≥ 4.3 — F19 fix) | When parser ships per-week values from CSV | green ● |
| **2 — MCR-derived** | `getPctSpecificForWeek(d) = Σ |cs.hist.sec[name].mcr|` over all sectors at date `d` | When tier 1 is null but `hist.sec` has MCR for that date. **L2-verified** by `verify_section_aggregates.py` (Σ pct_specific ≈ 100% on 3,082/3,082 sector-weeks). Same math as parser's `_pct_specific_source = "sum_sector_mcr"` for the latest week. Spot-check: GSC latest = 69.9 = source-direct exactly. | indigo ● + ᵉ |
| **3 — Broadcast** | Latest-week split (`cs.sum.pct_specific` / `cs.sum.pct_factor`) repeated onto every week | Last-resort when both tiers above fail (e.g., `hist.sec` has no entry for that date) | warn ● + ᵉ |

`exportTEStackedCsv()` (the tile's CSV export) uses the same three-tier resolution and emits a `Source` column so downstream consumers can see provenance per row.

**Renormalization invariant:** when `pct_specific + pct_factor` for a given week deviates from 100% by >5 pp, a console warning fires (`[cardTEStacked] N/M weeks: Σ shares deviate ...`) and the chart's footer surfaces a `⚠` caveat. The chart still renders (renormalized to fit `te`) but the deviation is never silently absorbed.

**Pre-F12(a) state (do not regress):** the chart used to fall back to a flat broadcast of the latest-week split when `pct_specific` was null — visually misleading because real per-week share varies (46→74% on GSC over 10 yrs). All three tiers are now visible to the user.

## Typography conventions (design-polish-v1 / B105.5, 2026-04-24)

Global CSS rules establish visual provenance for every numeric cell. These are NOT per-tile choices — if a number "looks different" between tiles, it should not be a font/typography difference, since the rules below are global.

| Treatment | Rule (global, in `<style>` block) | Where applied |
|---|---|---|
| Monospace numbers | `td.r { font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace }` | Every right-aligned table cell — auto-inherited by all 24 tile tables. |
| Tabular numerals | `td.r { font-variant-numeric: tabular-nums }` | Same. Numbers align column-wise even when values differ in width. |
| Body font | `body { font-family: 'DM Sans', system-ui, … }` | Whole dashboard. |
| Card-title typography | `.card-title { font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--textDim); margin-bottom: 8px }` | Every tile title via class — applied uniformly. |
| Reusable `.mono` helper | `.mono { font-family: 'JetBrains Mono', …; font-variant-numeric: tabular-nums }` | Add to any element rendering numbers OUTSIDE a `td.r` cell. |

**Provenance implication:** if a tile renders a numeric value somewhere other than a right-aligned table cell (e.g., a `<span>` in a hero KPI block), add `class="mono"` to it explicitly. Otherwise it falls back to DM Sans body font, which mixes oldstyle and lining figures depending on glyph and is NOT column-aligning.

---

## How to verify a number on the dashboard

1. Hover the cell. The tooltip says where it came from (in 🟢 sourced cells) or what derivation was applied (in 🟡 derived cells, marked with `ᵉ`).
2. If still uncertain: open the source CSV in a spreadsheet, navigate to the section name shown above, find the column shown above. The exact value should match (within rounding).
3. If a derivation path is shown: substitute the source values and re-compute. Result should match the rendered cell.
4. If you find a mismatch: log as a new finding in `FACTSET_FEEDBACK.md` (if CSV-side) or as a tile bug (if rendering-side).

---

## How to keep this index current

- Every tile that gets a render-fn change MUST update its row(s) in this doc.
- Every new derivation path requires a `🟡 derived` marker on the cell + tooltip explaining the math + entry here.
- Every CSV-side gap that's surfaced (e.g., F5 RiskM blanks) gets marked `⚫ empty` and the reason linked to FACTSET_FEEDBACK.md.

This is a living document. Newest changes at top of each tile section.
