# RR Dashboard — Session State

**Last updated:** 2026-04-16 17:30 (post Patch 004)
**Current git commit:** `13273c6` (main) — Patch 004: rHoldConc category axis fix
**Working state:** ✅ Dashboard renders correctly via local HTTP server

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

- **Size:** ~321K bytes / 5,450 lines
- **Last substantive edit:** 2026-04-16 17:24 (Patch 004)
- **Committed at:** `13273c6 — fix(hold): force category y-axis on rHoldConc to prevent NaN from numeric tickers`
- **Prior checkpoint:** `ce975e3` (tag `checkpoint-tab3-2026-04-16`)
- **Latest tag:** `working.20260416.1724`

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

---

## Features NOT on disk (CLI hallucinated writes, never persisted)

### Tab 1 (attempted, not yet rebuilt)
- Watchlist section in Holdings tab
- "What Changed" weight snapshot banner
- Quick-Nav sidebar (`buildQuickNav`, `#qnav`) — may have been pre-existing
- `generateExecSummary` — may have been pre-existing
- Strategy Comparison (`openCompare`)
- Keyboard shortcuts + `toggleShortcutHelp`
- Data freshness indicator
- Metric tooltips / Glossary modal (`openGlossary`)
- Risk Decomposition Tree (`riskDecompTree`, `mkNode`)
- Light/dark theme (`setThemePref`, `#themeBtn`)
- Color-blind safe mode (`toggleCbSafe`)

### Tab 2 (attempted, some rebuilt)
- ~~Country drill FactSet snap_attrib attribution section~~ — ✅ rebuilt as Patch 002 (`4ed2aa4`)
- Factor Risk Map height 340→480 + "Top TE" chip strip
- Print/Export report `openReport` (tile-picker modal vs 7-section print report)
- `generateEmailSnapshot` / `generateEmailBody`
- Performance Optimization (lazy charts via IntersectionObserver, debounce, Plotly.react wrapper `pPlot`)
- scenario-analysis
- multi-period-attribution
- industry-drilldown
- Currency Exposure tile

### Tab 3 (uncommitted items)
- `classifyHoldingArchetype` — does NOT exist; actual function is `getHoldArchetype` ✅ (naming discrepancy only)
- ~~Risk Alerts using `_thresholds` object~~ — ✅ resolved by Patch 001 (`e5eaf6c`)

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
| Tab 1/2 rebuilds ongoing | Medium | Settings ✅, Country drill ✅, bug fixes ✅; remaining: Risk Decomp Tree, keyboard shortcuts, glossary, Factor Risk Map polish |
| ~8 local commits ahead of `origin/main` | Low | Not pushed to remote; consider push after stability confirmed |
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

1. ✅ **DONE** (Patch 001) — Settings panel + Alert Thresholds
2. ✅ **DONE** (Patch 002) — Country drill snap_attrib
3. ✅ **DONE** (Patch 003) — tabBar + init + isFinite bug fixes
4. ✅ **DONE** (Patch 004) — rHoldConc category axis fix
5. **NEXT** — Rebuild Tab 1's **Risk Decomposition Tree** (crown-jewel, Patch 005)
6. Rebuild Tab 1's **Keyboard shortcuts + toggleShortcutHelp** (Patch 006)
7. Rebuild Tab 1's **Glossary modal** (Patch 007)
8. Deferred to Desktop (Chrome MCP): Factor Risk Map 480px polish, theme toggle, Holdings chart polish

---

## Emergency contacts

- Backup files on Desktop: `~/Desktop/dashboard_v7_BROKEN_20260416_*.html`, `~/Desktop/RR_gitlog_20260416_*.txt`, `~/Desktop/RR_backup_20260416_*/`
- Notion post-mortem: "RR Crisis 2026-04-16" (to be created)
- Session transcripts: `~/.claude/projects/-Users-ygoodman-RR/*.jsonl`
