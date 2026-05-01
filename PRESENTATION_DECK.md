# Redwood Risk Control Panel — Team Presentation Deck

**Drafted:** 2026-04-30 · **Audience:** Alger / Redwood PMs + analysts · **Length:** ~12 minutes
**Use:** paste each slide block into PowerPoint / Keynote / Google Slides, or read as live-demo narration script.

---

## Slide 1 — Title

# Redwood Risk Control Panel
### Portfolio Risk & Factor Analytics

**ALGER · REDWOOD**
April 30, 2026

*Speaker note:* "Today I'll show you the tool we've been building — what it does, the data discipline behind it, and where we're taking it next. Twelve minutes, then we open it live."

---

## Slide 2 — What is RR

### One dashboard. Seven strategies. Every Monday.

- **Single-pane risk view** for IDM, IOP, EM, ISC, ACWI, GSC, SCG — all 7 strategies in one selector
- **Three core lenses** — Exposures (snapshot), Risk (decomposition), Holdings (per-name)
- **Drill anywhere** — every cell, sum-card, factor row drills into 7+ years of weekly history
- **Portable** — single HTML file, drag-drop the parsed JSON, runs on any browser

*Speaker note:* "Replaces three separate workflows: pulling from FactSet, eyeballing the active-share spreadsheet, and the factor-tilt review. One open, one place."

**Show in dashboard:** header strategy dropdown + tab strip

---

## Slide 3 — The data layer

### Sourced. Verified. Never fabricated.

- **Source:** FactSet Portfolio Attribution CSV — single pipeline, header-driven parser
- **History:** 7+ years × 383 weekly snapshots × per-strategy holdings & factor exposures
- **Anti-fabrication policy** — every numeric cell traces to a CSV field; derived values flagged with ᵉ
- **Verifier on every load** — 22-check pass/fail report; schema fingerprint catches silent format drift
- **Bench coverage 21% → 70%** after fixing long-tail synthesis (B57c659, 2026-04-30)

*Speaker note:* "If a number isn't in the CSV, the dashboard does not invent one. It either flags it as derived or shows a dash. This was a deliberate choice after we caught four real integrity bugs by surfacing the gap rather than hiding it."

**Show in dashboard:** any ⓘ button → source path · DevTools console → `✓ B115 integrity check passed`

---

## Slide 4 — The Exposures tab

### Where the portfolio is, right now.

- **Six sum-cards** — Total TE, Active Share, Beta, Holdings, Idio %, Factor %
- **Sector / Region / Country tiles** — port vs bench weights, active deltas, TE contribution
- **Universe toggle** — switch between portfolio-only, benchmark-only, and combined views
- **Click any sum-card** → full historical chart drill across 7+ years

*Speaker note:* "This is the snapshot. If you wanted to know 'where am I overweight today,' it's three seconds away. Click the Idio sum-card for the time-series."

**Show in dashboard:** Exposures tab → Idio sum-card drill

---

## Slide 5 — cardWeekOverWeek

### The Monday-morning view.

- **Four KPI deltas at the top** — Δ TE, Δ AS, Δ Beta, Δ Holdings vs last week
- **Three columns of moves** — Added · Dropped · Resized (>0.10pp active weight shift)
- **Factor rotation footer** — three factors with the largest active-exposure shift
- **Mode-shift** — answers "what changed" not "what is" — first tile a PM sees Monday

*Speaker note:* "This is the new tile. Every other view is a snapshot — this is the diff. PM walks in Monday, scans this for 90 seconds, drills into one or two surprises. That's the workflow."

**Show in dashboard:** Exposures tab → top tile (cardWeekOverWeek)

---

## Slide 6 — The Risk tab

### TE decomposed. Factors ranked. History deep.

- **Five sum-cards** — Total TE, Factor Risk, Idiosyncratic, Active Share, Beta
- **Historical Trends** — TE / AS / Beta / Holdings mini-charts across all 7 strategies side-by-side
- **TE Stacked decomposition** — factor vs stock-specific risk evolution over 7+ years
- **Factor Exposures table** — every factor with active exposure, MCR, TE contribution; click any row → 7-year drill

*Speaker note:* "If Exposures answers 'where am I,' Risk answers 'what's driving the risk.' Factor correlation matrix is here too — for understanding which factor bets are correlated and amplifying."

**Show in dashboard:** Risk tab → click any factor row in Factor Exposures table

---

## Slide 7 — The Holdings tab

### Every name. Every exposure. One scroll.

- **Risk Snapshot quadrant** — every holding plotted by active weight × TE contribution, sized by stock-specific TE
- **Holdings table** — full position list with ratings (Overall · Revision · Value · Quality), factor pills, sparklines
- **Watchlist** — flag any holding (⚑) → builds a personal monitoring list, persisted across sessions
- **Top 10 + Rank Distribution + Portfolio Characteristics** — quintile breakdown shows the PM's natural Q1 skew (~56%)

*Speaker note:* "The quadrant top-right cluster — high-conviction overweights driving risk. Bottom-right — overweights that paradoxically diversify. That's the chart that ends 'why is this position here' debates in 20 seconds."

**Show in dashboard:** Holdings tab → click any bubble in Risk Snapshot

---

## Slide 8 — Trust + provenance

### Every number has a paper trail.

- **ⓘ button on every tile** — explains what the tile shows, the math, the source CSV field, known caveats
- **ᵉ markers on derived cells** — visible badge with hover-tooltip explaining the derivation rule
- **Freshness pill in header** — color-coded (green / yellow / red) on data age
- **Integrity assertion runs on every load** — `B115` checks for silent drift; failure throws a console alert

*Speaker note:* "The discipline behind this is what separates RR from a spreadsheet. A PM should never have to ask the analyst 'where did this number come from.' Click any ⓘ — it's right there."

**Show in dashboard:** click any ⓘ button (Risk tab Factor Exposures has a good one)

---

## Slide 9 — The fixes that mattered

### What we caught and resolved pre-presentation.

- **h.reg parsing** — region field misaligned across format variants; cardRegions count restored
- **cardUnowned blank** — bench-only TE contributors weren't surfacing; long-tail synthesis added (623 entries)
- **F4 long-tail bench coverage 21% → 70%** — parser now synthesizes from Raw Factors when SEDOL not in slim Security
- **Risk vs Exposures Idio/Factor reconciliation** — both tabs now read from same `cs.sum.pct_specific` source; no more cross-tab divergence

*Speaker note:* "These were real integrity issues that surfaced because we refused to fabricate. The dashboard's first job is to be trustworthy — these fixes earn that trust."

---

## Slide 10 — Where we go from here

### From local file to weekly enterprise feed.

- **Today** — local Mac, manual file load via `./load_data.sh`
- **Next (Option A — Mac workstation, ~30 min)** — weekly cron pulls latest FactSet drop, dashboard auto-refreshes
- **Future (Option B — Linux server)** — multi-user URL (`redwood-risk.firm.local`), nginx static serve, systemd timer
- **Static + secure** — no backend, no DB, no external API calls; portfolio data stays on firm filesystem

*Speaker note:* "The architecture is deliberately boring — static HTML, JSON file, Python parser. Migration is a half-day of IT work, not a project."

---

## Slide 11 — Open items / FactSet asks

### What we've requested. What we'll build when it lands.

- **F11** — per-holding period return → unblocks Brinson attribution waterfall
- **F12** — `%T_implied` for full bench unowned tile → makes cardUnowned complete (not just top-196)
- **F13** — date format standardization (drop the `00:00:00` time suffix)
- **F14** — portfolio-Data row `pct_specific` directly → removes a derivation marker
- **F15** — country-of-risk column for ADRs → distinguishes listing exchange from risk country

*Speaker note:* "These are documented in FACTSET_FEEDBACK.md — none are blocking today. F9 (long-tail bench universe) just shipped and was a big unlock."

---

## Slide 12 — Demo

### Let's open it.

**90-second walkthrough:**

1. **Exposures sum-cards** — "Six numbers across the top, all from FactSet. Click Idio for 7-year history."
2. **cardWeekOverWeek** — "What changed since Friday. KPI deltas, three columns of moves, factor rotation."
3. **Risk tab** — "TE decomposed. Click any factor → 7-year drill."
4. **Holdings Risk Snapshot** — "Every name placed by active weight × TE. Click a bubble for full security drill."
5. **cardUnowned** — "Bench-only stocks contributing to TE through their absence."
6. **Any ⓘ button** — "Source, math, caveats — every tile has one."
7. **Where we're going** — "Weekly auto-refresh, multi-user, ~30 min of IT setup."

*Speaker note:* "Questions are easier with the dashboard open — let's switch over."

**Show in dashboard:** open dashboard_v7.html, hard-refresh, walk slides 1-7 above

---

## Appendix — Quick stats for live Q&A

- **Lines of code:** ~11,572 (single HTML file)
- **Parser tests:** 89 pytest, all passing
- **History depth:** 383 weeks × 7 strategies (when full file lands)
- **Tile count:** ~25 across 3 main tabs + 4 secondary tabs
- **Verifier checks:** 22 pass/fail on every load
- **Anti-fabrication discipline:** 4 RED bugs caught + fixed by surfacing gaps rather than synthesizing values
- **Repo:** github.com/JGY123/RR (private)

---

**Drafted:** 2026-04-30 · ship-ready · paste into Keynote / Slides
