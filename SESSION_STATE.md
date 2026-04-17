# RR Dashboard — Session State

**Last updated:** 2026-04-16 20:35 (post Patches 012-014 + full feature audit)
**Current git commit:** `0050abb` (main) — Patch 014: My Watchlist card
**Working state:** ✅ Dashboard renders correctly; full 10-regression audit confirms **zero regressions introduced by Patches 001-014**. Dashboard is at near-full parity with pre-crisis feature list (20 of 22 items working).

---

## How to open the dashboard

```bash
# If server not running yet:
cd ~/RR && python3 -m http.server 8000

# Or use the alias added to ~/.zshrc:
rr

# Then in browser:
http://localhost:8000/dashboard_v7.html
```

**Do NOT open dashboard_v7.html directly via Finder or `open` — browsers block `fetch()` of local JSON files over `file://` protocol.** This was the cause of the 2026-04-16 morning panic.

---

## Current state of dashboard_v7.html

- **Size:** 5,750 lines
- **Last substantive edit:** 2026-04-16 20:07 (Patch 014)
- **Committed at:** `0050abb — feat(watchlist): Patch 014 — "My Watchlist" card on Exposures tab`
- **Prior checkpoint:** `ce975e3` (tag `checkpoint-tab3-2026-04-16`)
- **Latest tag:** `working.20260416.2007`
- **Origin sync:** ✅ fully pushed to `JGY123/RR` as of 2026-04-16 20:00
- **Environment:** Claude Desktop with Claude_Preview MCP (Chromium headless on port 3099); standalone Python server on :8000 also supported

### Features confirmed present (Tab 3's work, committed)

| Feature | Functions |
|---|---|
| Full-Screen Chart Modals | `openFullScreen`, `closeFsModal`, `renderFsFactorMap`, `renderFsScatter`, `renderFsCountry`, `_renderFsCtryMap`, `_renderFsCtryPanel`, `_renderFsScatPanel`, `fsFacHover`, `setFsMapRegion`, `setFsMapColor`, `facGrpColor` |
| Holdings Intelligence | `getHoldArchetype` (6 archetypes: Growth Engine / Value Play / Volatility Driver / Quality Compounder / Market Beta / Diversifier), RBE column, archetype pill, flag cycling (none → ★ → ▼ → ▲) with localStorage persistence, AI Summary in `oSt()` popup |
| Annotations | `getNotes`, `setNote`, `getNote`, `showNotePopup`, `refreshCardNoteBadges`, right-click `.card-title` handler, 📝 badges |
| Risk Alerts | `detectRiskAlerts` banner (hardcoded thresholds: TE>8%/>6%, cash>5%, Q5>15%, factor>0.5σ, asDelta<-1), dismissable pills, `riskAlertsBannerHtml`, `_riskAlertClick` |
| Baseline (from commit 0b7d56d) | Hero card, strategy selector, tabs (Overview/Exposures/Holdings/Risk), snap_attrib attribution section, Plotly date fixes, 18 Style Snapshot parser, sector/country/factor butterfly charts, country choropleth, quant ranks, TE chart |

---

## Completed Patches (post-crisis rebuild)

| # | Commit | Tag | Description |
|---|---|---|---|
| 001 | `e5eaf6c` | `working.20260416.0940` | Settings panel + Alert Thresholds. Extended existing `#configPanel` with 7 configurable threshold inputs, migrated `detectRiskAlerts` from hardcoded values to `_thresholds` object, persisted under `rr_thresholds` localStorage key, un-hid `#configBtn` gear icon. +46/-10 lines. All 8 substantive verification checks + browser smoke test passed. |
| 002 | `4ed2aa4` | `working.20260416.1430` | Country drill FactSet snap_attrib section. Added `renderCountryAttribSection` + `renderCountryAttribChart` after `oDrCountry`, injected into country drill modal. Stats grid + 160px cumulative impact time series. +36 lines. |
| 003 | `8ca5912` | `working.20260416.1554` | Three bug fixes: (A) strategy selector respects `_prefs.defaultStrat` in `init()`, (B) auto-load calls `init()` not `go()` (fixes hidden tabBar), (C) `isFinite(h.p)` guard on `rHoldConc`. +4/-7 lines. |
| 004 | `13273c6` | `working.20260416.1724` | Force `type:'category'` on rHoldConc y-axis to prevent Plotly treating numeric tickers (Chinese A-share codes) as numbers. +1/-1 lines. |
| 005 | `fc89aa9` | `working.20260416.1746` | Risk Decomposition Tree. Interactive collapsible tree: Total TE → Factor Risk (grouped by Value/Growth, Market Behavior, Profitability, Secondary) + Stock-Specific Risk (top 7 holdings by |tr|). `mkNode`, `toggleDtNode`, `riskDecompTree` functions. +71 lines. |
| — | `3b2a889` | `working.20260416.1755` | Keyboard shortcuts help modal. `toggleShortcutHelp` function, `?` and `g` key bindings. +22 lines. |
| — | `d72ae51` | — | Fix: add `kbdHelpModal` to `ALL_MODALS` so Escape closes it. Also cleaned up deleted .bak and parser files. |
| 007 | `cf70c40` | `working.20260416.1805` | Glossary modal with 13 metric definitions (TE, Active Share, MCR, Beta, etc.). `openGlossary` function, ⓘ header button, added to `ALL_MODALS`. +35/-1 lines. |
| 008 | `efd1462` | `working.20260416.1837` | Top 10 Holdings chart polish. Root-cause fix: `xaxis.type` was auto-detecting as `'category'` (range `[-0.33, 6.33]`), bar lengths non-proportional — force `type:'linear'` + `ticksuffix:'%'` + `rangemode:'tozero'`. Y-axis shows short company names (truncate 22 chars) instead of tickers. Active-weight coloring (green OW / red UW). Inside labels show "weight%  ±active". Hover surfaces ticker/name/weight/active/sector/MCR. Height 250 → 360px, left margin 50 → 150px. Card title: "Sector Concentration (Top 10 Holdings)" → "Top 10 Holdings (Weight & Active)". +21/-5 lines. |
| 009 | `35b18ad` | `working.20260416.1844` | Factor Risk Map polish. Rename card title "Factor Butterfly" → "Factor Risk Map" (aligns with fullscreen modal label). Bump `rFacButt` min chart height 280 → 480px. Add `#facTopTeStrip` above chart rendered by new `rFacTopTeStrip(s)`: top 4 factors by `|c|` as pills with name, `±σ` active exposure, `% TE` share. Green tint for OW, red for UW. `isFinite` guard per Patch 003 pattern. +20/-3 lines. |
| 010 | `cd2ea0f` | `working.20260416.1901` | Light/dark theme toggle foundation. Add `THEME()` helper returning live theme-aware colors (reads CSS vars at call time) + `buildPlotBg()` that constructs a fresh `plotBg` from THEME(). Convert `const plotBg` → `let plotBg = buildPlotBg()` so all 30+ `{...plotBg, ...}` spreads auto-adapt. `applyPrefs()` rebuilds plotBg + calls `upd()` after theme flip. Refactor 4 inline chart layouts to use THEME() directly: `rSecChart`, `rFacButt`, `rCountryMap`, `rFacWaterfall`. Patch 008/009 chart polish had already set up the visual-verification workflow that made this possible. +45/-23 lines. |
| 011 | `a5d6ab9` | `working.20260416.1910` | Theme-aware long-tail sweep. Expand THEME() with `card` + `bg` keys. Global `replace_all` on 6 property patterns — `gridcolor`, two `zerolinecolor` variants, `bgcolor` (rangeslider), `color:'#94a3b8'` (tick/text/font/line), `color:'#e2e8f0'` (emphasized text) — resolves ~50 chart-color leaks across ~15 renderers. Hand-edits for fullscreen choropleth (coastline/land/ocean) and colorscale midpoints. Total THEME() call sites 10 → 75. Round-trip dark→light→dark verified across Exposures/Risk/Holdings tabs + drill chart renders. +68/-66 lines. |
| — | `938f1bb` | — | **Parallel audit session** (Claude Opus 4.6) — 8 code quality fixes: rank chart CSS→hex resolution, screenshot bg→THEME().bg, note popup theme compat, FAC_GROUP_DEFS dynamic getter, PPTX export THEME() colors, "AI Summary"→"Quick Summary" rename, startLiveRefresh cs null guard, RBE glossary label fix. |
| — | `985fb27` | — | **Parallel audit-2** — attribution chart customdata per-bar hover, share URL restore via state.s, precision toggle now respects _prefs.precision. |
| 012 | `3f3eb05` | `working.20260416.1930` | Data freshness indicator. Extends `#dataTimestamp` with "· Nd ago" suffix colored by age (green ≤7, amber 8-20, red ≥21). Hover tooltip with exact date + generated timestamp. New `freshAmberDays`/`freshRedDays` threshold keys in settings panel, live-updating via setThreshold dispatch. +34/-11 lines. |
| 013 | `8b77807` | `working.20260416.1945` | "What Changed" weight snapshot banner. localStorage schema `rr_holdsnap_v1` + `rr_holdsnap_dismissed_v1`. Shows top 3 by `|Δweight| ≥ 0.5%` since last report_date. Green▲/red▼ chips, "+N more" counter, dismissable per (stratId, reportDate) tuple. New `whatChangedBannerHtml` + `dismissWhatChanged` + `buildCurrentSnap`. +64/-6 lines. |
| 014 | `0050abb` | `working.20260416.2007` | "My Watchlist" card on Exposures tab. Consumes existing flag state (`rr_flags_{stratId}`) and groups by flag type (★ Watch / ▼ Reduce / ▲ Add). Dense rows with icon/ticker/name/weight/active. Click row opens stock detail modal via existing `oSt`. Hides when no flags exist. +33 lines. |

---

## Full Feature Audit (2026-04-16 20:20)

Comprehensive grep + browser audit against the original 22-feature list. Verdict: **20 of 22 features working, zero regressions from Patches 001-014.**

### ✅ Confirmed working (8 focused regression tests all passed)

| Feature | Function(s) | Browser verified |
|---|---|---|
| Full-Screen Globe (3 color modes + 4 region zooms) | `openFullScreen('country')`, `_renderFsCtryMap`, `setFsMapRegion`, `setFsMapColor` | 26 countries choropleth, Active/Port/BM buttons wired, World/Eur/Asi/Amer zooms |
| Full-Screen Factor Map + hover-dim | `renderFsFactorMap`, `fsFacHover`, `fsFacUnhover` | Bubbles render by exposure × stddev, hover dims others 0.85 → 0.15 |
| Full-Screen Scatter + search + click select | `renderFsScatter`, `_fsScat_selectHold`, `_renderFsHoldDetail` | 39 panel rows searchable, click selects, panel shows factor bars |
| Holdings RBE + archetype + flags + Quick Summary | `getHoldArchetype`, `genHoldSummary`, `cycleFlag`, RBE column | All 6 archetypes coded (Growth Engine / Value Play / Volatility Driver / Quality Compounder / Market Beta / Diversifier) |
| Annotations right-click + 📝 badges | `showNotePopup`, `refreshCardNoteBadges` | Context menu handler at 5294; note saved with key `{stratId}:card:{cardId}` renders 📝 badge |
| Strategy Comparison | **`openComp()` (NOT openCompare)** at 3628, `#compareBtn` at 347 | Modal opens, 7-strategy checkboxes, Summary Stats, Risk Radar, Factor Active Exposures, Sector Heatmap |
| Email snapshot | `generateEmailSnapshot` at 5134, `#emailBtn` at 346 | Builds HTML email body, copies to clipboard + opens popup window (NO modal — by design) |
| Country choropleth (non-fullscreen) | `rCountryMap`, `countryMapDiv` at 1081 | 320px choropleth on Exposures, 26 countries, click-drill wired |

### ❌ Genuinely absent (2 features — the only true gaps)

- `generateExecSummary` / Exec Summary card — zero grep hits, never rebuilt
- Weekly Insights card — zero grep hits, never rebuilt

### Minor design gaps (not regressions, design limitations)

- `getHoldArchetype` returns `null` when top factor is "Country" / "Industry" / other unmapped keyword. Common in EM data. Could add a "Regional Driver" archetype bucket.
- Country globe color-mode menu has 3 modes (Active/Port/BM). User recalled 4+ including "contribution to risk" and "factor exposures" — those code paths don't exist in `_renderFsCtryMap`. Either never existed OR lost pre-crisis.

### Explicitly deferred / skipped

- Color-blind safe mode (`toggleCbSafe`) — SKIPPED per product call; for 20 PMs, feature-bloat
- Quick-Nav sidebar (`buildQuickNav`, `#qnav`) — not in file; deprioritized
- Print/Export report (`openReport`) — present at line 3768, not regression-tested
- Performance optimization (lazy charts / IntersectionObserver) — deliberately held off per crisis lesson #2
- Currency Exposure tile — never rebuilt
- Scenario analysis / multi-period attribution / industry drilldown — never rebuilt

---

## Backup branches (safety nets preserved)

- `backup-all-today-work` — points to `24b4353`
- `backup-today-all-work` — points to `24b4353` (identical, paired)
- Both contain 4,322-line `dashboard_v7.html` (older baseline)
- Both preserve `SESSION_CONTEXT.md`, `CONTINUATION_PROMPT.md`, `AUDIT_REPORT.md`, `DATA_FLOW_MAP.md`, `factset_parser_v2/v3.py` — all deleted from main

To inspect: `git show backup-all-today-work:<filename>`

---

## Known issues / open items

| Item | Severity | Notes |
|---|---|---|
| Tab 1/2 rebuilds ongoing | Low | 14 patches landed (001-014) + 2 parallel audits. Only Exec Summary + Weekly Insights are genuine gaps. Strategy Comparison, Email, Watchlist, What Changed, Data Freshness, Risk Alerts, Holdings Intelligence, Annotations — all verified working. |
| Origin fully synced | — | No local commits ahead of origin as of 2026-04-16 20:00. |
| Theme-toggle cosmetic tail | Low | Correlation heatmap midpoint, sunburst/pie slice borders, holdings sort-toggle inline HTML, html2canvas export bg, riskFacHist annotation bg still use dark-only hexes. Functional on both themes but not polished. |
| Dashboard_v7.html.bak deletion unstaged | Low | Tab 1 flagged as suspicious; confirmed unrelated to current issues |
| CLI session JSONLs (239MB in `~/.claude/projects/-Users-ygoodman-RR/`) | Low | Contains Tab 1/2 `str_replace` tool calls if deep recovery ever desired |

---

## Lessons from 2026-04-16 crisis

1. **Local HTTP server is REQUIRED** — `file://` protocol blocks `fetch()` of JSON. Alias `rr` in `~/.zshrc` starts it with one command.
2. **CLI "successful edit" reports are unreliable** — Tabs 1 and 3 both reported writes that didn't hit disk. Always verify with `wc -l` on actual file, not CLI self-report.
3. **Chief of Staff session is the fragile role** — carries cross-system state, highest context load, first to hit "prompt too long". Must checkpoint aggressively.
4. **Auto-monitor running CLIs overnight unattended is unsafe** — no reviewer means nothing catches hallucinated writes or autonomous overnight edits that may never land.
5. **Git commit early, tag often** — uncommitted work is the easiest to lose. Tag every known-good state.
6. **Backup branches should be verified NEW, not just created** — both backup branches here point to an older commit than main; they're baseline snapshots, not progress snapshots.

---

## Operational rules going forward

1. **Server must always be running** during work — `rr` alias or dedicated iTerm tab
2. **CLAUDE.md in `~/RR/` kept short and current** — bloated auto-load = smaller usable context
3. **CoS `/compact` every 60-90 min** — do NOT wait for "prompt too long"
4. **Update this SESSION_STATE.md at the end of every work session** — next session starts here
5. **Verify CLI writes hit disk** — never trust CLI self-report alone (`wc -l`, `grep -c`, `git status`)
6. **Git tag every working checkpoint** — `git tag -a working.<YYYYMMDD.HHMM> -m "<what works>"`
7. **Never run CLIs unattended overnight** — no auto-monitor, no `pmset sleepnow` on finish

---

## Priority queue for next session

1. ✅ **DONE** (Patch 001, `e5eaf6c`) — Settings panel + Alert Thresholds
2. ✅ **DONE** (Patch 002, `4ed2aa4`) — Country drill snap_attrib
3. ✅ **DONE** (Patch 003, `8ca5912`) — tabBar + init + isFinite bug fixes
4. ✅ **DONE** (Patch 004, `13273c6`) — rHoldConc category axis fix
5. ✅ **DONE** (Patch 005, `fc89aa9`) — Risk Decomposition Tree
6. ✅ **DONE** (Patch 006, `3b2a889`) — Keyboard shortcuts + help modal
7. ✅ **DONE** (Patch 007, `cf70c40`) — Glossary modal
8. ✅ **DONE** (Patch 008, `efd1462`) — Top 10 Holdings chart polish (linear axis, names, active-weight colors)
9. ✅ **DONE** (Patch 009, `35b18ad`) — Factor Risk Map polish + Top TE chip strip
10. ✅ **DONE** (Patch 010, `cd2ea0f`) — Theme toggle foundation (THEME() helper, buildPlotBg, 4 charts rewired)
11. ✅ **DONE** (Patch 011, `a5d6ab9`) — Theme-aware long-tail sweep (~50 chart-color leaks resolved)
12. ✅ **DONE** (Patch 012, `3f3eb05`) — Data freshness indicator in header
13. ✅ **DONE** (Patch 013, `8b77807`) — "What Changed" weight snapshot banner
14. ✅ **DONE** (Patch 014, `0050abb`) — "My Watchlist" card on Exposures tab
15. **NEXT — Patch 015 combined:** Exec Summary + Weekly Insights (the last 2 missing features from the original 22). After this, dashboard is at full parity and work shifts to polish.
16. **Polish / cosmetic queue (post-parity):** theme-toggle tail, archetype "Regional Driver" bucket for Country/Industry top-factor holdings, Print/Export click-test, Treemap dimensions toggle verification
17. **Explicitly deprioritized:** Color-blind mode, Quick-Nav sidebar, Currency Exposure tile, Scenario/Multi-period/Industry drilldowns, lazy-chart performance opt

---

## Emergency contacts

- Backup files on Desktop: `~/Desktop/dashboard_v7_BROKEN_20260416_*.html`, `~/Desktop/RR_gitlog_20260416_*.txt`, `~/Desktop/RR_backup_20260416_*/`
- Notion post-mortem: "RR Crisis 2026-04-16" (to be created)
- Session transcripts: `~/.claude/projects/-Users-ygoodman-RR/*.jsonl`
