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
| Tracking Error big number | 🟢 sourced | RiskM section → "Predicted Tracking Error (Std Dev)" → `parser.sum.te` |
| Idiosyncratic Risk % | 🟢 sourced (current week) / ⚫ empty (historical week) | RiskM → `% Asset Specific Risk` → `parser.sum.pct_specific`. Hist weeks not shipped → `—` |
| Factor Risk % | 🟢 sourced (current week) / ⚫ empty (historical week) | RiskM → `% Factor Risk` → `parser.sum.pct_factor`. Hist weeks not shipped → `—` |
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
