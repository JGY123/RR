# RR Architecture

**Status:** living document
**Last updated:** 2026-05-04
**Audience:** anyone touching this codebase — first-day contributor, future Claude session, the user re-reading after a break, anyone reviewing before firm-wide rollout.
**Purpose:** introduce the data flow, the tile contract, the design system, the integrity model, and the operational loops in one place. After reading this you should know where every kind of change belongs.

> **If you're about to edit anything that touches numeric data, stop and read this first**, plus `LESSONS_LEARNED.md` and `SOURCES.md`. The April 2026 data-integrity crisis is the formative event of this codebase; the rules below exist because of it.

---

## 1. What RR is, in one paragraph

RR (Redwood Risk Control Panel) is a single-pane portfolio risk dashboard for 6+ international investment strategies (ACWI, IDM, IOP, EM, GSC, ISC), built on FactSet Portfolio Attribution CSV exports. It is a **single-file HTML dashboard** (vanilla JS + Plotly + html2canvas) consuming JSON produced by a **single-source-of-truth Python parser**. ~30 tiles across 4 tabs (Overview / Exposures / Risk / Holdings), 7+ years of weekly history, used by PMs daily. Everything in RR's design serves one constraint above all others: **every number the user sees has a documented source path; we never silently fabricate**.

---

## 2. Quick start

```bash
# Parse a FactSet CSV export and open the dashboard
./load_data.sh ~/Downloads/factset_export.csv

# Multi-account workflow (with EM 6-year history merge)
./load_multi_account.sh

# Pre-flight checks before any risky edit
./smoke_test.sh             # ~1.8s — script integrity, JSON, lint, data-integrity layer
./smoke_test.sh --quick     # skip pytest (saves ~10s)
python3 verify_factset.py   # ~3s — 22+ pass/fail checks vs FactSet asks
python3 verify_section_aggregates.py --latest  # ~0.06s — Σ %TE invariant on latest week
python3 lint_week_flow.py --strict  # static lint for direct cs.X access in render fns
```

The dashboard opens in your default browser. CSV-in-browser is **disabled** (it throws); JSON drag-drop is supported. Single-source-of-truth pipeline only.

---

## 3. Data flow

```
┌────────────────┐    ┌──────────────────┐    ┌──────────────────────┐    ┌───────────────────┐
│  FactSet CSV   │───▶│  factset_parser  │───▶│  per-strategy JSON   │───▶│   dashboard.html  │
│  (96/101/42/9/ │    │  (header-driven, │    │  data/strategies/*   │    │   (renderer only) │
│   31-col blocks)│    │  Python, v3.1.0) │    │  + index.json (slim) │    │                   │
└────────────────┘    └──────────────────┘    └──────────────────────┘    └───────────────────┘
       │                       │                         │                         │
       │                       │                         │                         │
       ▼                       ▼                         ▼                         ▼
   raw bytes            verify_factset.py        verify_section_     _b115AssertIntegrity()
                        (L1, 22 checks)          aggregates.py (L2)   (load-time, render-side)
```

### 3.1 The parser is the only source of truth

`factset_parser.py` (PARSER_VERSION 3.1.0, FORMAT_VERSION 4.2) is the only code path that turns FactSet CSV into structured JSON. It is **header-driven** (column meaning detected from header text + section anchors), not positional, so when FactSet shifts a column the parser adapts rather than silently cross-wiring fields.

CSV section schemas (set in stone by FactSet):
- **96-col** — sector / country / region / group aggregates (5 groups × 18 metrics + 6 prefix)
- **101-col** — holdings (5 groups × 19 metrics + 6 prefix; the extra column is `Overall Rank` at position 5, dropped during parse)
- **42-col** — portfolio stats (TE, Beta, Active Share, fundamentals)
- **9-col** — factor exposure
- **31-col** — factor attribution (5 periods × 5 cols + prefix)

Multi-month files: dates with row count ≥ 30% of max are "main dates" (holdings/sectors); the rest are "factor dates" (factor exposure only). This auto-detects multi-year files.

### 3.2 The dashboard is a pure renderer

`dashboard_v7.html` is ~13 K lines of vanilla JS that reads the per-strategy JSON and renders 30 tiles. **It does not parse CSV.** `parseFactSetCSV()` exists only as a `throw` that explains the policy. CSV-in-browser was the root cause of the April 2026 crisis; it's now a hard rule.

`normalize()` (line ~609) is **rename-only** — it maps parser-output field names to consumer-expected field names. **No synthesis.** No `if X null compute Y`. If a field is null in source, it stays null; the renderer chooses to show `—` or, if it must derive, marks the cell visibly with `ᵉ` superscript and documents the chain in `SOURCES.md`.

### 3.3 Per-strategy split-file architecture

A 7-year multi-strategy JSON is ~1.8 GB. Loading that into a browser is unworkable, and loading it into a verifier was painful enough to disable the verifier (the May 2026 smoke-test memory crisis). Solution: **summary-first, detail-on-demand**.

```
data/
├── strategies/
│   ├── index.json          (~500 KB) — slim summaries for every strategy, every week
│   ├── ACWI.json           (per-strategy detail, 10-500 MB)
│   ├── IDM.json
│   ├── IOP.json
│   ├── EM.json
│   ├── GSC.json
│   └── ISC.json
└── archive/                (older snapshots)
```

- `index.json` carries enough cross-strategy summary data to do most invariance checks without loading any per-strategy detail. Used by smoke-test, `verify_section_aggregates.py --latest`, dashboard "which strategy?" picker.
- Per-strategy `*.json` loads only when the user selects that strategy. The dashboard never holds more than one full strategy in memory.
- Heavy verifiers (full-history `verify_section_aggregates.py`) iterate per-strategy files with explicit `del` + `gc.collect()` between strategies — peak RSS stays bounded.

**Lesson:** when designing data on disk, split into "summary" + "detail" tiers. Summary should fit in <1 MB. Cheap monitoring is the difference between "we have a verifier" and "we run the verifier every day."

### 3.4 Two-layer history architecture (within a single strategy file)

Inside a per-strategy JSON, the same summary/detail split repeats:

```
strategy.sum             — latest-week summary (te, as, beta, h, bh, sr, cash, ...)
strategy.hist.summary    — ALL weeks: [{d, te, as, beta, h, sr}, ...]   ← always loaded
strategy.hist.sec        — monthly sector snapshots: {SectorName: [...]}
strategy.hist.fac        — factor exposure history: {FactorName: [{d, e, bm}, ...]}
strategy.available_dates — sorted list of all weekly dates
strategy.current_date    — latest date (= available_dates[-1])

strategy.hold[]          — DETAIL: only for the current/selected week
strategy.sectors[]
strategy.countries[]
strategy.regions[]
strategy.factors[]
strategy.snap_attrib
```

`hist.summary` is tiny; the week selector + time-series charts read from it without ever loading the heavy detail layer. The week selector affects which date the heavy detail represents (via per-week accessors, see §4.4).

---

## 4. The tile contract

A "tile" is one of the ~30 cards in the dashboard (`<div class="card" id="cardX">…</div>`). The tile contract is the set of conventions every tile follows so adding a feature to one place ships everywhere.

### 4.1 Tile chrome — `tileChromeStrip()`

Every tile's button row (About / Notes / Cols / CSV / Reset / Hide / Fullscreen / View toggle) is rendered by **one function**: `tileChromeStrip({...})` at `dashboard_v7.html:1511`.

```js
tileChromeStrip({
  id: 'cardSectors',
  about: true,             // ⓘ button + popover
  cols: 'tbl-sec',         // ⚙ Cols sidecar (table id to introspect)
  download: { csv: 'expSecCSV()', png: '#cardSectors' },
  view: { active: 'table', options: [['table','Table'],['chart','Chart']], onchange: 'toggleSecView' },
  fullscreen: 'openSecFullscreen()',
  resetView: true,         // ↺
  hide: true,              // × hide tile
})
```

**One config edit ships across all 30 tiles.** This was Phase D of the May 2026 refactor. Before: each tile assembled its own chrome inline (~30 lines per tile, 800+ lines total). After: ~50 lines of declarative configs.

### 4.2 Table column hide/show — `tableColHidePanelHtml()`

Every renderer that produces a table emits `data-col="X"` on every `<th>` and `<td>`. A sidecar (line ~1666) auto-discovers columns from the rendered DOM and offers a `⚙ Cols` checkbox panel. Hiding is via injected CSS rule (`td[data-col="X"], th[data-col="X"] { display:none }`); state persists per-table in `localStorage` under `rr.tableColHide.v1`.

**Renderers are not touched.** Add a new column → it auto-appears in the panel. Drop a column → it auto-disappears.

### 4.3 Design system — tokens + 10 canonical CSS classes

All spacing, typography, color, radius, weight, shadow comes from tokens in `:root`:

```css
--space-0…6   --text-xs…3xl   --w-light…bold   --radius-sm…lg
--wash-blue   --wash-amber    --hairline       --shadow-sm…lg
--textDim     --textBright    --bgCard         (etc.)
```

The 10 canonical CSS classes (Phase K of the refactor):

| Class | What it styles |
|---|---|
| `.tile-btn` | Every chrome button (uniform size/color/hover) |
| `.export-btn` | Inline CSV/Email export buttons (unified with `.tile-btn`) |
| `.section-label` | Section-divider text inside cards/modals |
| `.empty-state` | "No data" placeholders (+ explanatory subtitle) |
| `.stat-card` | KPI strip cells (cardThisWeek, sector summary, etc.) |
| `.modal-close-btn` | × button in modals (consistent placement + style) |
| `.modal-title` | Modal header text |
| `.tile-chrome` | The button-row container (output of `tileChromeStrip`) |
| `.kpi-strip` | Wrapper for stat-card rows |
| `.num-tabular` | `font-variant-numeric: tabular-nums` for aligned numbers |

**Hardcoded colors / spacing / fonts are forbidden.** A grep for `padding: 8px` or `color: #94a3b8` should return zero results in render code; if you find one, sweep it to the token.

### 4.4 Per-week data flow — accessors + lint

Every render function that reads a per-week dimension MUST go through a per-week accessor, not directly through `cs.<dim>`:

| Accessor | Returns | Replaces |
|---|---|---|
| `_wSec()` | sector aggregates for `_selectedWeek` | `cs.sectors` |
| `_wCtry()` | countries | `cs.countries` |
| `_wReg()` | regions | `cs.regions` |
| `_wGrp()` | groups (Redwood-defined) | `cs.groups` |
| `_wInd()` | industries | `cs.industries` |
| `_wChars()` | characteristics (39 metrics) | `cs.chars` |
| `_wFactors()` | factor exposures | `cs.factors` |
| `getSelectedWeekSum()` | `{te, as, beta, h, ...}` for selected week | `cs.sum` |
| `getDimForWeek(dim, weekDate)` | low-level accessor used by all the above | — |
| `getFactorsForWeek(weekDate)` | factor exposures for a specific week | — |

**Lint enforcement:** `lint_week_flow.py --strict` is wired into `smoke_test.sh`. Direct `cs.sectors` / `cs.countries` / `cs.hold` reads inside render functions fail the lint. Background: it was easy to forget the accessor when shipping a quick fix; the lint catches that before the regression ships.

### 4.5 Drill modals

Click a tile or a row → opens a modal: `oDr()` (sector drill), `oDrCountry()`, `oDrMetric()`, `oDrChar()`, `oDrAttrib()`, `oSt()` (single ticker). Each modal embeds a time-series chart (Plotly) + a detail table.

**Note:** drill modals predate the `tileChromeStrip` migration. They still use inline chrome. Migrating them is queued (not blocking).

### 4.6 Universe pill

The toolbar carries a 3-way pill: **Port-Held** / **In Bench** / **All**. Universe affects which holdings appear in the holdings table and watchlist. **Universe-invariant** columns: TE / MCR / factor_contr / Beta — these come from the risk model, not the holdings filter, and don't change with the pill (B116 invariance, see lint comment at `dashboard_v7.html`).

### 4.7 Week selector

Header carries `‹ date ›` arrows + a date picker. Selecting a historical week:
- Updates `_selectedWeek` global
- Re-renders all tiles via `_withScrollPreserved(renderAll)` so scroll position survives the swap
- Tiles read the selected-week dimensions via accessors
- An amber "viewing historical week" banner appears
- For weeks where a dimension wasn't snapshotted (e.g., per-holding factor TE breakdown), tiles show `—` with a tooltip — never fabricate

---

## 5. Data integrity model

The single most important non-functional property of RR. Six rules, each born from a specific April 2026 failure:

1. **CSV in browser = error.** `parseFactSetCSV()` throws. User runs `./load_data.sh`. Single-source-of-truth pipeline only.
2. **`normalize()` is rename-only.** Any new "if X is null compute Y" patch must instead: (a) leave it null, OR (b) compute it AND add a `_X_synth=true` marker AND add a render-side `ᵉ` badge AND document in `SOURCES.md`.
3. **localStorage is for preferences only.** Never cache data. Every page load wipes `rr_*` except `PREFS_KEY`.
4. **Every numeric cell has provenance.** `SOURCES.md` is the index. UPDATE when render code changes.
5. **Integrity assertion runs on every load.** `_b115AssertIntegrity()` (line ~2017) catches drift in console with field-by-field diff.
6. **CSV format shift = audit every parser path.** Python parser is header-driven (adapts); ALL JS-side paths get re-audited or deleted.

### 5.1 The 4-layer monitoring framework

A single integrity assertion at load time is necessary but not sufficient. RR runs four layers:

| Layer | What it checks | When | Artifact |
|---|---|---|---|
| **L1 — Parser verifier** | 22+ checks vs the parser's own output: column counts, fingerprints, schema drift, FactSet-ask checklist | Every parse run | `last_verify_report.log` |
| **L2 — Cross-week aggregate verifier** | Per-cell sums obey stated invariants across ALL historical weeks (e.g., section-aggregate Σ %TE ≈ 100% on every (strategy × dim × week)) | Every smoke run, or `--latest` | `verify_section_aggregates.py` stdout |
| **L3 — Trend monitor** | Are verified invariants drifting over time? (Did a metric that was 100% last quarter now read 134%?) | Manual today; dashboard tile someday | trend chart |
| **L4 — Inquiry log** | When an anomaly fails L1/L2/L3, is there a tracked open question to upstream? | On every RED finding | `FACTSET_FEEDBACK.md` + `FACTSET_INQUIRY_<id>.md` |

Each layer feeds the next. An L2 anomaly becomes an L4 inquiry. A resolved L4 inquiry becomes either a parser fix (folded into L1) or a permanent monitor (folded into L2). **Knowledge accumulates monotonically.**

### 5.2 The structured inquiry workflow

When a finding requires upstream confirmation (the FactSet team or an internal model owner), the inquiry itself is a formal artifact, not a Slack message. Six-step flow:

1. **Observe** — record the cross-strategy / cross-week distribution. Numbers, not vibes.
2. **Hypothesize** — list 4-6 falsifiable causes (parser bug, doc wrong, undocumented filter, universe mismatch, period handling, source bug).
3. **Source-side test** — design experiments the user can run on the source platform that would rule out each hypothesis in <1 hour total.
4. **Letter** — draft a concise, technical, friendly letter to the upstream expert. Cross-strategy table + sample export + 4-6 sharp questions ranked by what would unblock us most.
5. **Reply integration** — when the answer comes back, fold it into the parser, the doc, OR a permanent automated check.
6. **Monitor** — even after resolution, keep the L2/L3 check active so the question can't silently recur.

Reusable template: `FACTSET_INQUIRY_TEMPLATE.md`. Active inquiries live in `FACTSET_FEEDBACK.md` (running log).

### 5.3 Defensive UI while an inquiry is open

When an anomaly is escalated but unresolved, the UI must not pretend the value is correct. Three acceptable postures:

1. **Suppress** — hide the value (footer/tooltip explains why).
2. **Honest math** — show what we have AND show its deviation from the expected invariant.
   *Example footer:* `Σ %T = 134.2% (expected 100% — see inquiry F18, FactSet escalation)`.
3. **Mark derived** — if we computed a workaround, flag visibly (`ᵉ` superscript) and link the tooltip to the inquiry doc.

**Never quietly normalize the deviation away.** A 134% rescaled to 100% would be the worst outcome — the user would never know to ask, and any source-side bug would compound silently.

---

## 6. The five operational loops

RR is not just a dashboard; it's a set of loops that make it more correct + more expert over time. Each loop has its own cadence, artifact, and feedback mechanism.

### Loop 1 — Tile audit cadence

`tile-audit` subagent → `tile-specs/<id>-audit-YYYY-MM-DD.md` → trivial fixes shipped, larger fixes queued, PM-decision items flagged. Three-track audit: data accuracy / functionality parity / design consistency. Parallel subagents (3-5 at a time) explore in <30 min what serial review would take hours. Quarterly cadence; full coverage of all 30 tiles.

### Loop 2 — Data integrity monitor

The 4-layer framework above. L1 + L2 wired into `smoke_test.sh` (gates every commit on data-layer files). L3 manual today. L4 on every RED finding.

### Loop 3 — FactSet inquiry workflow

The 6-step inquiry flow above. F18 (per-holding %T sums 94→134%) is the active pilot. Each cycle deepens our expertise on a specific metric and adds an automated check so the question can't recur.

### Loop 4 — Refactor + lint enforcement

Per-week data flow lint-enforced. Smoke test catches script parse bombs, missing render fns, schema drift. Tag-and-push discipline at session boundaries (see SESSION_GUIDE.md). Anti-fabrication policy stays sacred during all refactors.

### Loop 5 — Persona / agent training

`risk-reports-specialist.md` (98% confidence, RR-specific) + `data-integrity-specialist.md` (cross-project) + `factset-parser-engineer.md` (parser-specific) + `tile-audit` + `data-viz`. Updated when significant patterns emerge so future sessions inherit the lessons.

---

## 7. Key files map

```
RR/
├── CLAUDE.md                       — project guardrails (read first, every session)
├── ARCHITECTURE.md                 — this file
├── SESSION_GUIDE.md                — operator's spine: first-5-minutes checklist + end-of-session ritual
├── STRATEGIC_REVIEW.md             — bird's-eye view, periodic re-baselining
├── LESSONS_LEARNED.md              — formative pain (Apr 2026 + May 2026 lessons)
├── SOURCES.md                      — per-cell provenance index
├── FACTSET_FEEDBACK.md             — running log of CSV-side issues
├── FACTSET_INQUIRY_TEMPLATE.md     — reusable inquiry template
│
├── dashboard_v7.html               — the dashboard (~13 K lines)
├── factset_parser.py               — the parser (~2 K lines, header-driven)
├── test_parser.py                  — pytest suite (89 tests)
│
├── load_data.sh                    — parse + verify + open
├── load_multi_account.sh           — multi-strategy + EM history merge
├── smoke_test.sh                   — pre-flight pass/fail
├── verify_factset.py               — L1: 22+ checks against parser output
├── verify_section_aggregates.py    — L2: cross-week invariant checker
├── lint_week_flow.py               — per-week accessor lint
│
├── data/
│   ├── strategies/
│   │   ├── index.json              — slim summaries (load this for fast checks)
│   │   └── <ID>.json               — per-strategy detail (load on demand)
│   └── archive/
│
├── tile-specs/                     — per-tile audit reports
│   └── <id>-audit-YYYY-MM-DD.md
│
├── docs/
│   ├── INDEX.md                    — full doc navigator
│   └── archive/
│
└── REFACTOR_AUDIT.md / _PLAN / _IMPACT  — Phase A-K refactor records (historical reference)
```

---

## 8. How to add things (worked examples)

### 8.1 Add a new tile

1. Pick a target tab (Overview / Exposures / Risk / Holdings); locate the section in `dashboard_v7.html`.
2. Add the card shell:
   ```html
   <div class="card" id="cardNewThing" style="margin-bottom:16px">
     <div class="card-header">
       <h3 class="card-title">My New Thing</h3>
       ${tileChromeStrip({
         id: 'cardNewThing',
         about: true,
         download: { csv: 'expNewThingCSV()' },
         resetView: true,
         hide: true,
       })}
     </div>
     <div id="newThingBody"></div>
   </div>
   ```
3. Write the renderer `rNewThing()`. Read data via accessors (`_wSec()`, etc.), NOT direct `cs.X`. Emit `data-col="X"` on every `<th>`/`<td>` if it's a table.
4. Wire `rNewThing()` into the tab's render function.
5. Add a `SOURCES.md` entry: which JSON field every cell reads.
6. Add an "About" entry: what is this tile, what does each column mean, where does the data come from.
7. Add a tile-spec audit (`tile-audit` subagent). Three tracks: data / func / design.
8. Run `./smoke_test.sh` + `python3 lint_week_flow.py --strict`. Fix anything red.

### 8.2 Add a new column to an existing table

1. Update the renderer to emit the new column with `data-col="<key>"` on `<th>` and `<td>`.
2. Add a label to `COL_LABELS` in `dashboard_v7.html` so the ⚙ Cols panel shows a friendly name.
3. Source the value from a parsed JSON field (NEVER fabricate). If the field doesn't exist yet, add it to `factset_parser.py` first; if FactSet doesn't ship it, add it to `FACTSET_FEEDBACK.md` and either (a) leave the column showing `—` or (b) compute it with a `_synth` marker + `ᵉ` badge.
4. Update `SOURCES.md`.
5. Add a column tooltip on the `<th>`.

### 8.3 Add a new strategy

1. Confirm the file's risk model: worldwide (6 macro factors incl. Currency/Country/Exchange Rate Sensitivity) or domestic (smaller factor set).
2. Update the strategy mapping table in `CLAUDE.md`.
3. Run `./load_data.sh <new_csv>`. The verifier auto-runs; the schema fingerprint will flag drift if the model is new.
4. Delete `~/RR/.schema_fingerprint.json` to acknowledge the new model shape.
5. Re-run; verifier should classify domestic-mode missing factors as PARTIAL not FAIL.
6. The dashboard's strategy picker auto-discovers from `data/strategies/index.json`.

### 8.4 Investigate a "wacky number"

The procedure is in `LESSONS_LEARNED.md` and is mandatory:

1. Don't guess. Open the cell's `SOURCES.md` entry to find which JSON field it reads.
2. Open the per-strategy JSON and check the field directly.
3. Open the parser to verify how that field is extracted from the CSV.
4. Open the CSV in a spreadsheet to verify the source value.
5. If steps 1-4 disagree: **invoke the data-integrity-specialist agent** with the diff. It will produce a structured audit and propose fixes.
6. If 1-4 agree but the user says the value is wrong: this is an L4 inquiry candidate. Check `FACTSET_FEEDBACK.md` for an existing thread; if none, draft a new inquiry doc (`FACTSET_INQUIRY_TEMPLATE.md`).
7. Never paper over with rescaling, fallback constants, or "smart" recompute. Suppress, mark, or escalate — those are the only three acceptable postures.

---

## 9. Glossary

| Term | Meaning |
|---|---|
| **Tier-1 / Tier-2 tile** | Tier-1 = first-screen / most-used (cardThisWeek, cardSectors, cardCountry, cardHoldings, etc.). Tier-2 = secondary surfaces (Risk-tab charts: cardCorr, cardFacContribBars, cardTEStacked, cardBetaHist, cardFacHist). Tier classification drives audit priority. |
| **F-item** | An entry in `FACTSET_FEEDBACK.md` (F1, F2, …, F18 …). Each is a CSV-side issue or open question to FactSet. |
| **B-item** | An entry in `BACKLOG.md` (B114, B115, B116 …). Internal work items. |
| **`cs`** | The current-strategy global object on the dashboard side. `cs.sum`, `cs.hold`, `cs.sectors`, etc. |
| **`cs.hist.summary`** | The always-loaded summary layer (one row per week, light fields only). |
| **%TE** | Percentage of tracking error contributed by a holding/sector/factor. Per-holding %T column F18 currently anomalous (94→134% across strategies). |
| **%S** | Stock-specific (idiosyncratic) component of TE. |
| **MCR** | Marginal contribution to risk. **Never rendered with a `%` sign** (PM preference; see `feedback_mcr_no_percent.md`). |
| **Universe-invariance** | Property of risk-model columns (TE, MCR, factor_contr, Beta) — they don't change when the universe pill is flipped. Verified by lint (B116). |
| **`_synth=true`** | Sidecar marker indicating a normalized value was computed, not sourced. Render layer should display the cell with an `ᵉ` superscript and a tooltip pointing at the derivation. |
| **Worldwide vs Domestic risk model** | Two FactSet model files: worldwide (6 international strategies, larger factor set) and domestic (SCG + Alger US accounts, smaller factor set, no FX/country macros). Parser is header-driven and adapts. |
| **Anti-fabrication policy** | Six hard rules in CLAUDE.md, born from the April 2026 crisis. The most important non-functional property of RR. |

---

## 10. What this doc does NOT cover (yet)

- Specific tile-by-tile data-source mapping → that's `SOURCES.md`.
- Backlog items → `BACKLOG.md`.
- The day-to-day "what changed in this commit" → `CHANGELOG.md`.
- Refactor history (Phase A-K) → `REFACTOR_AUDIT.md` / `_PLAN.md` / `_IMPACT.md`.
- Linux server deployment runbook → `MIGRATION_PLAN.md` (sketched not battle-tested).
- PM-facing onboarding → `EXECUTIVE_SUMMARY.md` + `PRESENTATION_DECK.md` + `PRESENTATION_DAY_GUIDE.md` (existing) + a future "first Monday morning" cheat sheet (queued).

---

## 11. Closing thought

The user's framing has been consistent across every session: **make it right, scale it slowly, become more expert each cycle.** Not "ship fast." That bias has produced a dashboard with rare data discipline, an audit cadence that compounds, and a knowledge base that future contributors can stand on.

If you're about to make a change to this codebase, ask three questions:

1. **Does it preserve the anti-fabrication policy?** No `?? 0`, no synthesis without markers, no localStorage-as-data.
2. **Does it use the right abstraction?** `tileChromeStrip` for chrome, accessors for per-week data, design tokens for styling.
3. **Will the next person know where it came from?** A `SOURCES.md` entry, a tooltip with provenance, an audit doc, an inquiry log.

If yes to all three, ship it. If any are no, fix that first.
