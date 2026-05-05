# RR Design Touch-Up — Professional-Grade for Alger

**Drafted:** 2026-05-05
**Trigger:** user direction post-roadmap — "we also need to revisit and touch up the design especially since I'm going to listen to you and not switch it into a desktop installed software... so let me make sure this is professional grade."
**Companion:** `ROADMAP.md` (the strategic plan), `ALGER_DEPLOYMENT.md` (the deployment spec).
**Audience:** the user (product owner) + future engineering sessions implementing the touch-up.

This doc is the design plan for taking RR from "internal-tools polish" to "professional-grade output you'd hand to a senior PM at Alger."

---

## TL;DR

Three categories of work:

1. **Brand alignment** — current dashboard is a dark "data-app" theme; Alger's brand is **light, navy + blue, Benton Sans**. We can ship an "Alger theme" variant without disrupting the existing dark mode (theme tokens are already in `:root`). ~6-8 hr of focused design work.

2. **Typography + density polish** — even within the existing dark theme, several tiles have inconsistent label sizing, awkward spacing, and visual debt accumulated during the rapid Phase A-K refactor. ~4 hr of pure polish — no new features, just making everything sing.

3. **Reader-facing chrome** — header (firm logo + dashboard name + last-updated), footer (version + ingest status + integrity-monitor green/red), print/PDF stylesheet for emailed reports. ~3 hr.

Total: ~15 hr to professional-grade. Plan below in priority order so partial work still ships value.

---

## 1. Alger brand — what we're matching

From the brand-discovery pass on alger.com (saved in this session's context, 2026-05-05):

| Token | Alger | RR (current dark theme) | Recommendation |
|---|---|---|---|
| **Primary navy** | `#002B54` | n/a | Use for headlines, axis titles, header |
| **Primary blue (link/CTA)** | `#136CAF` | `--pri` (currently `#6366f1` indigo) | Map `--pri` to `#136CAF` in the Alger theme |
| **Light blue accent** | `#4FA3DF` | n/a | Hover, active states, chart secondary series |
| **Background** | `#FFFFFF` | dark `#0f172a` | Light theme variant |
| **Panel background** | `#F9F9F9` | `--surf` `#1e293b` | Light theme variant |
| **Body text** | `#333` / `#444` | `--text` `#c8cdd8` | Flip in light theme |
| **Muted gray** | `#717073` | `--textDim` `#6b7280` | Close enough; keep |
| **Positive (gain)** | `rgb(65,131,79)` ≈ `#41834F` | `--pos` `#10b981` | Use Alger's green in Alger theme |
| **Negative (loss)** | `#A32F2F` | `--neg` `#ef4444` | Use Alger's red |
| **Accent (mid)** | `#C64C31` orange / `#712F7E` purple | various | For factor-category color coding |
| **Typography** | Benton Sans (self-hosted) | DM Sans + JetBrains Mono | Add Benton Sans fallback chain |
| **Logo** | Wordmark "Alger" navy | none | Add to header (~120 px wide) |
| **Tagline / signature** | "Inspired by Change. Driven by Growth." / "Unlock Your Growth Potential℠" | n/a | Reference somewhere subtle (footer? About modal?) |
| **Visual signature** | Skewed-parallelogram buttons (32° transform) | rounded rect | Optional — could pick this up as our primary CTA shape |

The current dashboard's dark theme is a great "PM bloomberg-terminal vibe" but reads as third-party tooling. The Alger theme makes it look firm-issued.

---

## 2. Recommendation: ship light theme as a sibling, not a replacement

**Don't rip out the dark theme.** Some PMs (and analysts) will prefer it. Some will prefer Alger-light.

**Action:** add a theme picker (top-right of header) that toggles between:
- `Dark` (current) — for analysts, late-night work, dense data review
- `Alger` (new) — for client-facing demos, screenshots in decks, formal contexts

Persist choice in localStorage. Default to **Alger** for first-load on Alger's VM (firm-issued look-and-feel for PMs); default to Dark for users on the user's local laptop (dev/admin context).

This is a 2-3 hour refactor: introduce a `data-theme="alger"` attribute on `<html>`, define CSS variables under `:root[data-theme="alger"]` that override the defaults, update Plotly's `THEME()` function to read from CSS variables instead of hardcoded JS, add the picker UI.

After the refactor: every existing tile renders correctly in both themes without touching tile code. (This is exactly what the Phase K design-token work set up; we just need to use it.)

---

## 3. Typography + density polish (intra-theme)

These items improve the dashboard regardless of theme:

### 3.1 Header — give it weight

Current: thin top bar with strategy picker + week selector + universe pill + ranks pill + notes button. Reads as utilitarian.

**Touch-up:**
- **Add the Alger logo** (left side, navy wordmark, ~120 px wide). When in Dark theme, logo is white; when in Alger theme, logo is navy.
- **Dashboard name + tagline** centered or left-of-controls: "Redwood Risk Control Panel" + small subtitle "Inspired by Change. Driven by Growth." (in Alger theme) or just the name (in Dark).
- **Last updated** indicator (right side): "Data through 2026-04-30 · Ingested 2026-05-05" — pulls from `cs.current_date` + the most recent `merge_history[]` entry. **This is gold for trust** — every PM sees freshness at a glance.
- **Integrity-monitor pulse** (small dot next to "Last updated"): green = all green, amber = warning, red = RED finding. Hover for details. Pulled from the L2 monitor output.

### 3.2 Card titles — consistent weight + size

Current: `card-title.tip` style varies in render (some `font-size:13px`, some inherit, some bold, some not). Audit pass found ~5 inconsistencies in May.

**Touch-up:** lock to a single class signature. `font-size: var(--text-md)` (15px) bold for all card titles. Subtitle (smaller, dim) for the data-tip preview.

### 3.3 Numeric tabular alignment

`.num-tabular` class exists but isn't applied universally. Numeric columns in 4-5 tiles still use proportional digits → numbers don't line up vertically.

**Touch-up:** sweep `data-col` cells with `font-variant-numeric: tabular-nums` via a global rule on `td.r`. ~1 hr work, instant readability win across 8 tables.

### 3.4 Stat-card hierarchy

`.stat-card` is the canonical KPI cell. Currently:
- label (10px, dim)
- value (lg / xl, theme color)
- subtitle (10px, dim)

**Touch-up:** add a subtle bottom-border accent (4px) keyed to the metric category — TE = primary blue, AS = accent purple, Beta = warning amber, Holdings = neutral. Picks up the Alger color-coding language. Doesn't shout; reads as intentional.

### 3.5 Footer — give the dashboard a footer

Current: dashboard ends abruptly. No footer.

**Touch-up:** small footer below the active tab content with:
- Dashboard version (Git tag)
- Parser version (`PARSER_VERSION` from JSON)
- Format version (`FORMAT_VERSION` from JSON)
- Latest ingest timestamp
- Integrity status
- Link to PM_ONBOARDING + the F-feedback log
- Tagline (Alger theme only)

Like a desktop app's "About" status bar but inline.

### 3.6 Print stylesheet

When PMs print or save to PDF (for committee meetings), the dashboard currently looks bad — dark theme on white paper, charts cut off, etc.

**Touch-up:** `@media print` ruleset that:
- Forces light theme regardless of selected
- Drops the universe pill / ranks pill / week selector (screenshot-only context)
- Adds firm logo + report timestamp at top of every page
- Uses `page-break-inside: avoid` on tile cards
- Hides interactive chrome (× hide, ⤾ reset, ⛶ fullscreen buttons)

This is what makes PMs say "looks like the firm made this" instead of "looks like a screenshot."

### 3.7 Empty-state copy + tone

`.empty-state` class is canonical. Some empty states still read informally ("No factors selected" — fine; "No cash history shipped" — too internal-jargon).

**Touch-up:** rewrite empty-state copy where it reads internal. Examples:
- "No cash history shipped (FactSet weekly export does not always include % Cash)" → "No cash history available for this strategy yet."
- "No TE history" (already replaced) ✓
- "No factor data" → "No factor exposures available — confirm the strategy file shipped factor data."

Small but compounds. PMs read these in-product; they shouldn't sound like internal devops.

### 3.8 Tile-chrome button hover states

Current hover on `.tile-btn` is a faint background. In Alger theme that should be a 1-2 shade darker blue. In dark theme already fine.

**Touch-up:** define hover/focus states per theme.

### 3.9 Modal close-buttons + reset button shapes

The 32° skewed-parallelogram is Alger's visual signature (per brand discovery). We don't need to adopt this on every button (would feel costume-y) but the **primary CTAs** (e.g., "Export PDF", "Reset View") could use it in Alger theme. Optional touch.

---

## 4. Reader-facing chrome (the parts non-PM stakeholders see)

### 4.1 Email-snapshot button

Already exists on cardThisWeek. Currently emits a plain-text snapshot.

**Touch-up:** also generate an HTML version with inline styling using Alger brand colors. PM emails the HTML to clients/IC; renders properly in Outlook.

### 4.2 PNG export

Per user preference (`feedback_no_png_buttons.md`), no standalone PNG buttons. PNGs are inside the per-tile download dropdown only.

**Touch-up:** ensure the PNG export uses the **active theme** (currently always dark). When in Alger theme, exported PNG is light. Decision rule: WYSIWYG.

### 4.3 PDF export

Not yet shipped. Triggered by the print stylesheet (§3.6) + the browser's "Save as PDF."

**Touch-up:** add a "Generate PDF report" link in the header that opens `window.print()`. The print stylesheet handles formatting. Net experience: one click → professional PDF.

### 4.4 Watchlist export to clipboard / email

Already shipped. No design change needed.

### 4.5 "Generate deck" → Gamma integration

See `GAMMA_PROMPT.md` — separate doc. The dashboard doesn't need to integrate Gamma directly; the user generates decks externally with the prompt.

---

## 5. Plotly charts — bring them on-brand

Plotly charts are the visual workhorse. Tuning them for brand:

- **Background:** transparent (already done) — picks up theme background
- **Axis colors:** `THEME().tick` (already token-driven)
- **Grid lines:** `rgba(148,163,184,0.06)` — neutral; works in both themes
- **Default series colors:** sequence today is `[#6366f1, #10b981, #a78bfa, #ef4444, #8b5cf6, #38bdf8, #ec4899]` (mostly DM-style indigo+purple). Replace in Alger theme with: `[#136CAF, #41834F, #4FA3DF, #C64C31, #712F7E, #717073, #A32F2F]` — Alger's brand-coded palette.
- **Reference lines / target bands:** muted via brand-coded greens (in target) and reds (out of target). Already done; just adjust hex values per theme.
- **Data labels font:** Benton Sans fallback chain in Alger theme; DM Sans in Dark theme.

Touch-up: add `THEME().series` returning the per-theme sequence. Charts read from this instead of hardcoded sequences.

---

## 6. Density / information-architecture polish

The dashboard is dense (intentionally). Some tiles cram more than they should:

- **cardChars** (39 metrics) — could benefit from a categorical group toggle that surfaces only the 6-7 metrics most PMs look at, with "show all" as a secondary action.
- **cardCorr** heatmap labels can collide on narrow viewports — abbreviate factor names below ~1280 px (already does some; could be cleaner).
- **cardRiskFacTbl** has lots of columns; let users hide via the existing `⚙ Cols` panel — already shipped, but the default visible set could be re-curated.

These are already covered in tile-spec docs as "larger fixes / PM gate." Bundle into a "round 2 polish" cycle.

---

## 7. Loading states

Dashboard currently shows nothing while `index.json` and the active strategy are fetching. ~1-2 second blank period.

**Touch-up:**
- Initial load: minimal skeleton with the firm logo + "Loading..." + a thin progress bar
- Strategy switch: keep the previous strategy's tiles visible but dimmed (50% opacity); replace as the new data arrives
- Per-tile: rendering errors → small `.empty-state` per tile rather than blank space

This is what professional-grade products do. Microsoft, Bloomberg, FactSet's own UI all show skeleton loaders.

---

## 8. Accessibility (a11y) — pass before firm-wide rollout

The current dashboard is keyboard-functional but not formally a11y-tested:

- All interactive elements have `tabindex` (mostly; spot checks may catch gaps)
- Tooltips use `data-tip` + a custom popup — not screen-reader friendly. Should also have `title` attribute as fallback for screen readers and basic browsers.
- Color is sometimes the only signal (red/green for sign of TE) — should pair with a glyph (▲ adds, ▼ diversifies — already done in some places).
- Focus-visible outlines vary tile-to-tile — should be consistent (Phase K touched but didn't sweep).

**Touch-up:**
- `:focus-visible` ring color = primary blue, 2px, all interactive elements
- `aria-label` on every icon-only button (× hide, ⤾ reset, ⛶ fullscreen)
- `role="button"` and `tabindex="0"` on clickable cards (cardBetaHist, cardRiskHistTrends drill cards)
- Audit with axe-core or Lighthouse before rollout

---

## 9. Phased plan — what to ship when

### Phase 1 — pre-rollout polish (~6 hr)

Best-bang-for-buck before PMs see it:

1. **Header revamp** (§3.1) — logo, name, last-updated, integrity pulse [2 hr]
2. **Footer** (§3.5) — version + freshness + integrity status [1 hr]
3. **Print stylesheet** (§3.6) — for PDF export [1 hr]
4. **Empty-state copy rewrites** (§3.7) — strip internal jargon [30 min]
5. **a11y sweep** (§8) — focus-visible + aria-label [1 hr]
6. **Tabular nums sweep** (§3.3) — global rule + apply [30 min]

After Phase 1: dashboard already feels firm-issued.

### Phase 2 — Alger theme variant (~6 hr)

1. **Theme tokens for Alger** (§1, §2) — CSS variables under `:root[data-theme="alger"]` [2 hr]
2. **Theme picker UI** (§2) — toggle in header, persist to localStorage [1 hr]
3. **Plotly THEME().series** (§5) — per-theme series palette [1 hr]
4. **Logo asset** — fetch from alger.com or have user provide a hi-res PNG [15 min]
5. **Verify every tile in Alger theme** — visual sweep [1.5 hr]

After Phase 2: dashboard is Alger-branded for client-facing demos.

### Phase 3 — refinement (~3 hr)

1. **Stat-card category accent** (§3.4) [30 min]
2. **Skewed-parallelogram CTA buttons** (§3.9, optional) [30 min]
3. **Loading skeleton** (§7) [1 hr]
4. **Tile cleanups from Tier-3 audit polish round 2** (deferred from ROADMAP T1.3) [30 min]
5. **Testing on Alger VDI memory profile** (per `ALGER_DEPLOYMENT.md` §8) [as available]

### Phase 4 — long-shelf nice-to-haves

- HTML email export (§4.1)
- Per-firm theme variants (if multi-firm rollout happens)
- Skeleton loader animations
- Compact/comfortable density toggle
- Density-aware tile re-arrangement

---

## 10. What this doc does NOT cover

- **Per-tile redesigns** — that's `tile-specs/*.md` audit docs + `data-viz` subagent territory.
- **Drill modal redesign** — covered by `DRILL_MODAL_MIGRATION_SPEC.md`.
- **Architecture changes** — covered by `ROADMAP.md` and `ALGER_DEPLOYMENT.md`.

This doc is purely the visual + interaction polish layer.

---

## 11. Open questions for user

1. **Which Alger logo asset?** Do you have a high-res version (preferably SVG)? Or should we use the live site's `https://www.alger.com/Style%20Library/Alger/img/logo.png` (304×53, transparent PNG)?
2. **Default theme on Alger's VM?** I'm proposing Alger-theme as default; PMs can switch to Dark. Confirm.
3. **Tagline placement?** "Inspired by Change. Driven by Growth." — header subtitle, footer, or About modal? Or skip entirely (tagline on a daily-use tool can read as marketing-y)?
4. **Skewed-parallelogram CTAs?** Optional Alger visual nod — adopt or skip?
5. **Benton Sans typography?** It's self-hosted on alger.com. We can either (a) load it from alger.com/Style Library/Alger/fonts/ (cross-origin font load — needs CORS), (b) pack the woff2 files into our /srv/rr/fonts/ folder (have the user obtain the fonts properly), or (c) fall back to "Helvetica Neue, Arial" which is close enough that most PMs won't notice. Recommendation: (c) for v1 and revisit if there's pushback.
6. **PDF export priority?** PMs will likely want this for committee meetings. Could ship in Phase 1 or defer to Phase 3.
7. **Theme decision urgency?** If first PM rollout is imminent, do Phase 1 first (theme-agnostic) and Phase 2 after. If we have a few weeks, do Phase 2 first so first impression is on-brand.

---

## 12. Closing

Going from "internal-tools polish" to "professional-grade output" is mostly a few hours of focused design work, not a redesign. The Phase A-K refactor laid the foundation (design tokens, canonical classes, lint enforcement). Phase 2 here just adds an Alger color set on top.

The dashboard already does the hardest things right (anti-fabrication, audit cadence, defensive UI). Brand polish is the visible layer that signals "the firm built this." It's worth doing, and it's tractable.
