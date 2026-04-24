# SurpriseEdge Design & Feature Study — FULL APP-LEVEL ADOPTION PLAN

**Updated:** 2026-04-24 (after deep-dive on the actual v3.2.0 Tauri desktop app source, not just the HTML report)
**Source location:** `~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/` + `~/Desktop/SurpriseEdge.app` + `~/Desktop/SE_screenshots/`
**Supersedes:** the prior (HTML-report-only) version of this document.

---

## What SurpriseEdge actually is

Not a one-off HTML report. It's a **production Tauri 2 desktop app** shipped at Redwood ISC:
- **~9,200 lines React + 750 lines Rust**
- **48+ analytics tiles across 7 tabs** (Overview, Spotlight, Returns, Analytics, Trends, Detail, Explorer)
- **Tech:** React 18 + Recharts + Vite + Tauri 2 + Claude API (SSE streaming via Rust)
- **Custom fonts:** DM Sans (body) + JetBrains Mono (numbers) — woff2 bundled
- **Tests:** 80 Vitest tests, 0 ESLint warnings
- **Distribution:** `.app` bundle macOS + Windows installer, auto-updater via shared network folder
- **Binary size:** 16 MB (vs Electron's ~150 MB)

**Tag line:** "Earnings Surprise Analytics for the Whole Firm" — built to a pitch-deck-ready level of polish.

## Honest gap assessment — RR vs SurpriseEdge

| Dimension | SurpriseEdge | RR (today) | Gap |
|---|---|---|---|
| **Visual polish** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | LARGE — fonts, palette, card chrome, hex-alpha discipline |
| **Interactivity depth** | ⭐⭐⭐⭐ (card AI, lineage, manual links) | ⭐⭐⭐ (note-hook, drill) | MEDIUM — meta-layer features RR lacks |
| **Data richness** | ⭐⭐⭐ (1 universe, earnings surprise) | ⭐⭐⭐⭐⭐ (7 strategies, multi-week hist, factors, raw_fac, security_ref) | RR WINS |
| **Historical state** | ⭐ (snapshot) | ⭐⭐⭐⭐ (week selector + hist.fac/summary) | RR WINS |
| **Framework weight** | Tauri + React (native app) | Single-file vanilla JS (no build) | Different goals — RR is simpler by design |
| **Distribution** | Installer, auto-updater, CI builds | HTML file you double-click | SurpriseEdge WINS |

**Summary:** RR has MORE data/history/capability. SurpriseEdge has MORE polish and meta-layer. To "match or exceed" we adopt the polish + meta-layer WITHOUT giving up RR's data richness or single-file simplicity.

---

## Design tokens — adopt as-is

From `src/constants.js` (SurpriseEdge's canonical palette):

```css
/* DARK PALETTE — dept register: enterprise fintech */
--bg:          #0b0e14;  /* body, deeper than RR's current */
--card:        #12161f;  /* card surface */
--cardBorder:  #1e2433;  /* card border, dividers, grid lines */
--text:        #c8cdd8;  /* body copy */
--textDim:     #6b7280;  /* muted / captions */
--textBright:  #eef0f4;  /* headings / emphasis */
--accent:      #22d3ee;  /* CYAN — primary accent (not indigo!) */
--accentDim:   #0e7490;  /* darker cyan for accents-on-accents */
--beat:        #10b981;  /* positive/green (same as RR today) */
--beatBg:      #10b98118; /* 18 hex = ~9% alpha — for tinted backgrounds */
--inline:      #f59e0b;  /* neutral/amber (same as RR today) */
--inlineBg:    #f59e0b18;
--miss:        #ef4444;  /* negative/red */
--missBg:      #ef444418;
--port:        #22d3ee;  /* portfolio = cyan */
--univ:        #6366f1;  /* universe/benchmark = indigo — RR's current --pri */
--upload:      #8b5cf6;  /* purple — for upload/CTA buttons */
--uploadBg:    #8b5cf620;
```

**Key insights:**
1. **Cyan (`#22d3ee`) is the primary accent**, NOT indigo. RR's current `--pri: #6366f1` becomes `--univ` (secondary/benchmark color).
2. **Hex-alpha pattern**: `#<color><alpha>` where alpha is 2 hex chars. `18 = ~9%`, `20 = ~12.5%`, `25 = ~15%`, `60 = ~38%`. Used EVERYWHERE for tinted backgrounds, chip borders, hover states.
3. **Upload/CTA** uses a linear gradient: `linear-gradient(135deg, #8b5cf6, #22d3ee)` with a glow shadow `0 0 20px #8b5cf630`. Distinctive, memorable.

## Typography — adopt the fonts

SurpriseEdge bundles these as woff2:
- **DM Sans** — body font (400 + 700 weights)
- **JetBrains Mono** — every numeric cell, every statistic

**Impact of font choice:** This single change is MORE visually transformative than palette change. System-ui looks like "web app." DM Sans looks like "Bloomberg Terminal." JetBrains Mono on numbers is the single biggest "enterprise feel" lever.

**Adoption path for RR (vanilla JS):**
1. Copy the 4 woff2 files from `~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/` into `~/RR/fonts/`
2. Inline the `@font-face` declarations from `fonts.css` into the `<style>` block of `dashboard_v7.html`
3. Set `body { font-family: 'DM Sans', system-ui, sans-serif; }`
4. Add `.mono { font-family: 'JetBrains Mono', Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }`
5. Apply `.mono` to every numeric cell (sweep across 24 tiles).

**Total size added to HTML:** ~80 KB (woff2 files can be embedded as base64 or loaded from same-dir path). Negligible.

## The "6 things that make it sharp" (unchanged from prior study, confirmed)

1. **Deeper palette** (`#0b0e14`) + cyan accent
2. **Custom 6px scrollbars** — `::-webkit-scrollbar`
3. **`.mono` class on every number** (JetBrains Mono)
4. **Card titles**: 11px uppercase, 600 weight, 1.5px letter-spacing, `textDim` color
5. **Subtle row separators** at 8% alpha
6. **Hex-alpha pills** with color-matched border/bg/text

## NEW patterns I didn't catch in the HTML-only study

### Card toolbar icons (every card has these in top-right)

From `Card.jsx`:

```
[ ⛶ expand ]    [ 💡 Ask AI ]    [ ℹ insight ]    [ 🔵3 notes ]
```

- **Expand**: opens card in full-page view
- **Ask AI**: opens Claude panel with tile-specific context + lineage
- **Insight (ℹ)**: toggleable panel showing methodology + clickable field lineage + manual PDF link
- **Notes badge**: count chip in accent color, only shows if count > 0

Each icon is a 22×22 button with subtle hover state (border + bg change on hover). Very polished.

### Card left-border accent when notes exist

```css
border-left: 3px solid var(--accent);  /* when noteCount > 0 */
border-left: 1px solid var(--cardBorder);  /* default */
```

Instantly shows which cards have your notes. RR has the note badge but not the border highlight.

### Insight panel — inline toggleable methodology

The `ℹ` button opens an in-card expandable panel with:
- Short methodology description
- **"Data fields"** chip list — each field is a toggle (click to disable per-tile)
- **"Open in Manual (p. 47)"** link — opens the bundled PDF at the right page

This is HUGE for user trust — they see EXACTLY what data each tile consumes and can toggle fields off to see impact.

### Smart filter bar (top-of-dashboard)

Pattern:
```
[SCOPE] <All>  <Portfolio>  <Universe>  |  [BIM] <All> <Beat> <Inline> <Miss>  |  [RETURN] <+1D> <+10D> ...  |  ⌕ Search  |  [≡ Filters (3)]  + [chips of active filters]
```

- Labeled groups separated by 1px × 20px vertical rules
- Each pill's active state inverts colors (bg=accent, text=bg)
- BIM pills USE the semantic color when active (not just accent)
- Search box with inline ⌕ icon and ✕ clear
- **Filter count badge** — cyan pill with count when dimensional filters active
- **Active filter chips** — inline removable pill per active filter dimension
- Vertical rules every group — tight visual grouping

### Header branding

```html
<div style="width:4px;height:24px;border-radius:2px;background:linear-gradient(180deg,var(--accent),var(--univ))"></div>
<span style="font-size:16px;font-weight:700;color:var(--textBright);letter-spacing:-0.3px">
  Surprise<span style="color:var(--accent)">Edge</span>
</span>
```

4px vertical gradient bar + two-tone wordmark. Distinctive identity element.

**For RR:** could render as `Redwood<cyan>Risk</cyan>` with the same gradient bar.

### Multi-select filter panel (not a dropdown, an inline panel)

Each dimension opens as a checkbox list:
- Uppercase label + "(count)" dim
- "Clear" button top-right if any selected
- Scrolls if >8 options
- Each option: 14×14 checkbox (accent border when checked) + label + **port/univ count in mono** (`88/1712`)

RR currently uses per-tile pill groups for filtering. The multi-select panel is DENSER for dimensions with >5 options.

### Key Takeaways tile (auto-generated + pinnable)

Example findings shown in `03_key_takeaways.png`:
- `▲ Best sector: Consumer Discretionary 71% n=93`
- `★ Rank 1 beat rate 59.1% n=3377`
- `⭕ 606 portfolio / 25461 universe`
- `▼ Worst sector: Telecommunication Services 0% n=0`
- `→ Port vs Univ spread: +14.3pp avg`
- `↑ Beat rate 2024→2025: +4.6pp`

Each has:
- Semantic icon (colored by direction)
- Bold label + key number in semantic color + dim caption
- **Pin icon** on right — click to persist as a saved takeaway across sessions
- Green dot when "pinned AND current findings still match"; red when "pinned BUT stale"

### Ask AI integration per tile

Each card carries:
```js
const aiPrompt = `FOCUS: The "${title}" tile in SurpriseEdge.
Tile description: ${insightStr}
Data lineage: ${lineageStr}
For this specific tile:
1. What key patterns or signals does it reveal?
2. Are there any anomalies or concerns?
3. How should I interpret the data shown?
4. What actionable insights can I derive?`;
```

Clicking the 💡 button opens a side panel with Claude's response streamed in real time. The context is rich: tile title + methodology + exact data fields consumed + aggregate context.

### Winsorize controls per tile

Small toolbar that appears on outlier-sensitive tiles:
```
[Winsorize] <None> <1%> <2.5%> <5%> <10%>     n=25,461 (234 clipped)
```

Click a percentile to trim tails. Shows clipped count in JetBrains Mono. "Rec" badge above the system's recommended choice.

### Lazy tile placeholder

Heavy tiles (big scatter, complex aggregations) don't compute until requested:
```
        [  🔄 Load  ]
        Click to compute
```

Big green button with refresh icon, glow shadow. Label underneath.

---

## Revised adoption plan — phased by ambition

### 🎯 Phase 1 — "Look as sharp" (~2 hours, single commit, zero risk)

**Goal:** RR visually reads at SurpriseEdge's level. No behavioral changes.

- Adopt palette tokens (swap `--pri` to cyan, add `--univ` as RR's old indigo)
- Bundle DM Sans + JetBrains Mono woff2 files, `@font-face` declarations
- `.mono` class applied to every numeric cell across 24 tiles
- 11px uppercase card-titles + 1.5px letter-spacing
- 6px custom scrollbars
- 8%-alpha row separators
- Hex-alpha pill convention across all toggles/filters
- Header gradient bar + two-tone wordmark

**Shipping:** tag `design-polish-v1`, browser regression check on all 24 tiles.

### 🎯 Phase 2 — "Feel as sharp" (~3–4 hours, multi-commit)

**Goal:** RR interaction patterns match the smart-filter + card-toolbar feel.

- **Card toolbar** (⛶ expand / 💡 AI / ℹ insight) on every tile — 3 buttons top-right. Expand + AI are stub-wired for now; insight button becomes the existing note-hook's companion.
- **Left-border accent** when card has notes
- **Smart filter bar** at top of dashboard — SCOPE / WEEK / STRATEGY pills with vertical-rule separators, search box, filter-count badge, active-filter chips
- **Multi-select filter panel** replacing the 4 separate cardRanks / cardCountry / etc. inline toggles with a shared component
- **Key Takeaways** tile on Overview — auto-generated findings with pin-to-persist (upgrade to cardThisWeek)

**Shipping:** tag `feel-parity-v1`.

### 🎯 Phase 3 — "Meta-layer depth" (~1–2 days, larger scope)

**Goal:** match SurpriseEdge on card AI / insight / lineage / manual. Adds RR's distinctive twist — historical context that SurpriseEdge lacks.

- **Insight panel per card** — toggleable "ℹ" showing methodology + data lineage + field toggles
- **Ask AI per card** — side panel with tile-specific prompts. Requires a Claude API key entry in settings. Integrates with RR's `AUDIT_LEARNINGS.md` so the AI knows the audit history of each tile ("you are inspecting cardMCR, which had a RED T1 finding on domain rename pair B20/B39, since resolved at .v1.fixes stage…")
- **Data lineage per card** — declare field sources in a `CARD_LINEAGE` map; render as clickable chips in insight panel
- **Manual deep links** — ship a PDF manual generated from the audit files, with `open_manual_pdf(page)` (Tauri) equivalent for a vanilla JS dashboard = open a new browser tab with `#page=N` anchor
- **Winsorize** for outlier-sensitive tiles (cardScatter, cardMCR, etc.)
- **Lazy tile placeholders** for heavy computations

**Shipping:** tag `depth-v1`.

### 🎯 Phase 4 — "Exceed" (the distinctive RR advantages, amplified)

**Goal:** RR does things SurpriseEdge cannot. Make them visible.

- **Time-travel banner** — when `_selectedWeek` is set, show a colored strip across the top: "Viewing WEEK OF Apr 17 2026 (2 weeks ago). Latest: Apr 24." Click strip to return to latest.
- **Strategy comparison overlay** — any tile's render can compare 2+ strategies side-by-side (RR has 7; SurpriseEdge has 1 universe).
- **Raw factor exposure decomposition** (B102–B104 already planned) — these are NATIVE to RR's data model; SurpriseEdge doesn't have this feature.
- **Historical animation** — play a tile's data through the weekly hist as a "heartbeat" view. New concept; pure RR differentiator.

**Shipping:** per-feature tags. This is post-review-marathon.

---

## Sequencing decision — what to ship now

**My recommendation:** **Phase 1 before marathon.** Here's why:

- Phase 1 is pure CSS + font swap + class additions. **Zero tile-render-function edits.** Every `.v1.fixes` state is preserved at the behavior level.
- Marathon reviews run on a dashboard that looks the way the user wants it to look.
- When user says "OK" to a tile, they're signing off on the polished version from day 1, not the pre-polish version that would need re-review post-polish.
- Biggest emotional payoff for the 2-hour investment: user sees the transformation in Stage 1 before they've invested marathon effort.

**Risks:**
- A font swap can subtly shift layouts (DM Sans is slightly narrower than system-ui). A browser regression pass across 24 tiles is mandatory. If any tile has hardcoded widths that get weird, we fix inline.
- Cyan accent (`#22d3ee`) replaces RR's current indigo (`#6366f1`). Any tile that uses `var(--pri)` as a color in semantic contexts (not just "accent") may need a review. Expected: <5 sites.

**Phase 2 and beyond:** post-marathon. Not worth destabilizing review state for the smart-filter-bar and card-toolbar lifts.

---

## Files referenced in this study (all on ~/Desktop)

- `SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/`
  - `src/constants.js` — canonical palette
  - `src/fonts/fonts.css` + woff2 files — font stack
  - `src/components/Card.jsx` — card primitive with toolbar + contexts
  - `src/components/UIComponents.jsx` — Pill, MultiSelectFilterSection, CustomTooltip
  - `src/App.jsx` — top-level layout, tabs, filter bar, header (lines 4280+ = header; 1174 = tab state)
  - `src/utils/formatters.js` — fmtVal, fmtMktCap
  - `SurpriseEdge-Cover-Letter.md` — product intent + tech stack rationale
  - `HANDOFF.md` — full technical handoff
- `SE_screenshots/` — 02_portfolio_vs_universe.png, 03_key_takeaways.png, 04_beat_rate_year.png (unique; others are duplicates)
- `SurpriseEdge.app/` — compiled .app bundle (8 MB native binary)

---

## BACKLOG update needed

Update B105 entry (currently scoped only to Tier A items from the prior study). Expand to reflect:
- **B105 · Phase 1 design polish** (palette + fonts + .mono + scrollbars + card-title typography + row separators + hex-alpha pills) — ~2 hours, PRE-marathon on user greenlight
- **B106 · Phase 2 feel parity** (smart filter bar + card toolbar + left-border-accent + multi-select filter panel + Key Takeaways tile) — ~3–4 hours, POST-marathon
- **B107 · Phase 3 meta-layer depth** (insight panels + Ask AI + lineage + manual deep links + winsorize + lazy placeholders) — ~1–2 days, POST-Phase 2

**Sequence to be pinned in SESSION_STATE "Next up":** marathon → B105 → Tier 2 tile builds (B102/B103/B104 adopting polish) → B106 → B107.
