# Tableau for RR + Visual Mockup Mechanism

**Drafted:** 2026-04-30
**Author:** data-viz subagent
**Coordinator:** main session
**Trigger:** User asked (a) how Tableau access could enrich RR's visualization toolkit, and (b) how new tile proposals should be previewed before being committed to the dashboard.

This doc is opinionated. The user is non-engineering and has asked for concrete recommendations, not options-trees.

---

## Section 1 — Tableau for RR

### TL;DR

**Tableau is a useful sketchbook, not a replacement.** Use it to *discover* visualization ideas (chart types, color encodings, layouts) that you'd otherwise not have considered. Then re-implement the chosen ideas in Plotly inside `dashboard_v7.html`. **Do not deploy Tableau workbooks to PMs.** RR's deployment story (open one HTML file, drag a JSON, done) is a feature — Tableau breaks that story badly.

### What Tableau is good for in RR's context

1. **Idea generation.** Tableau's "Show Me" panel offers ~24 chart types ranked by suitability for the data shape you've selected. It will suggest combinations a coder reaching for Plotly might never try (Gantt for time-on-position, packed bubbles for sector concentration, dual-axis combo charts where Plotly takes 40 lines to configure).
2. **Rapid layout iteration.** Drag-drop dashboards in Tableau take 10–15 minutes per concept. Equivalent Plotly-in-HTML mockup = ~1 hour.
3. **Statistical overlays out-of-the-box.** Trend lines, reference bands, forecast cones, R² annotations — Plotly can do all of these but each is a config exercise. Tableau gives them as right-click menus.
4. **Calculated fields without code.** "Show me TE per holding bucketed into top-quintile / mid / bottom by active weight" is a 3-click drag in Tableau. In Plotly you'd compute it in JS first.
5. **Cross-filtering across small multiples.** When you put 7 sector charts on one Tableau dashboard and click an industrial bar in chart #1, all 7 charts re-filter. We have a partial version of this in RR (drill modals), but Tableau makes the *exploratory* version trivial — useful when figuring out what views are worth committing.

### What Tableau cannot do for RR

1. **Ship to PMs as part of the product.** Tableau workbooks need either (a) Tableau Desktop at $70+/user/month, (b) Tableau Public (workbook becomes public on the internet — confidential portfolio data → no), or (c) Tableau Server / Cloud which is a $42/user/month deployed instance plus IT. Your current "open one HTML file" model dies the moment Tableau enters the deployment chain.
2. **Read FactSet CSVs as cleanly as the parser does.** Tableau will load the raw CSV but won't apply the 30%-row threshold for multi-month detection, won't dedupe the duplicate Overall Rank column, won't pivot the 5-period attribution section into long form. You'd pre-cook the JSON or write Tableau Prep flows — added maintenance for a sketchbook.
3. **Honor the dark theme + DM Sans + the project's exact color tokens.** Tableau will get close but not pixel-match. Mockups built in Tableau will look subtly off — distracting when the question is "is this the right viz?" versus "does this match our look?".
4. **Run client-side with no server / no internet.** RR works on a plane. Tableau needs network to render the workbook viewer (unless desktop is installed locally, which has its own problems).
5. **Write back to JSON / localStorage prefs.** Plotly + plain JS owns the entire two-way interaction loop in RR — you lose that the moment the chart is in Tableau.

### Tableau Public vs. Tableau Desktop — what's free and what's not

| Edition | Cost | Data privacy | Useful for RR? |
|---|---|---|---|
| **Tableau Public** | Free | Workbooks are **published to a public URL.** Anyone can see the portfolio. | **No.** Confidential holdings data must never touch a public Tableau site. |
| **Tableau Public Desktop** | Free | Local-only authoring, but saving requires public publish. | Partial — useful for sketching with **fake / anonymized data** only. Save the workbook locally as `.twbx` and never publish. |
| **Tableau Desktop** | ~$70/mo (Tableau Creator license) | Local + private + cloud | Yes for sketching. Still cannot deploy to PMs without Server/Cloud licensing. |
| **Tableau Cloud / Server** | $42–$70/user/mo | Private | Overkill for RR's use case — we already have a working dashboard. |

**Practical answer:** if you have a Tableau Creator license through your firm, use Tableau Desktop locally with **anonymized / synthesized data** to sketch new tile concepts. Never publish, never use real holding-level data outside your local laptop.

### Concrete workflow — when to reach for Tableau

A new tile or chart idea comes up. Before you ask me to spec it, do this:

1. **Export the relevant slice of the JSON to CSV.** A small helper would be useful (one I can write later): `python3 export_to_tableau.py --strategy GSC --section sectors`. Spits out a flat CSV of the 11 sector rows with all 17 columns the table shows.
2. **Open Tableau Desktop, drag the CSV in, hit "Show Me."** Spend 20 minutes trying 4–5 chart types. Save the screenshot of the one you like.
3. **Drop the screenshot in the chat with me.** Say: "Like this, but in our dark theme." I produce the spec + the HTML mockup (Section 2) for review.
4. **You decide go / no-go.** I implement only on green light.

### When to skip Tableau entirely

- **You already have a clear mental picture of the chart.** ("I want a stacked bar of TE by sector colored by sign.") Just spec it directly.
- **The chart is a small modification of an existing tile.** ("Add a second bar series.") Tableau adds zero — go straight to a HTML mockup or a Plotly tweak.
- **The data is highly nested / array-of-objects-of-arrays** (e.g. `cs.snap_attrib[name].hist`). Tableau struggles with non-tabular shapes; flattening them is more work than just sketching in Plotly.
- **You're optimizing a metric of *reading speed*** ("how fast can the PM glance at this and act?"). Reading-speed tuning needs the actual fonts + token colors + DPI. Mockup-in-browser beats Tableau here.

### Visualization patterns from Tableau worth borrowing into RR

These are patterns Tableau popularized that we have not used in RR yet, and that translate cleanly to Plotly:

| Pattern | Where in RR it would fit | Plotly equivalent |
|---|---|---|
| **Bullet chart** (single bar + reference line + qualitative bands) | Replace the four KPI sum-cards (TE / AS / Beta / Holdings) with bullet charts showing actual vs. target band. Adds 1 metric of context per cell. | Combination of a horizontal bar + shapes layer. ~30 lines per cell. |
| **Marimekko** (variable-width stacked bar) | Sector exposure: bar width = port wt, bar height = active wt. Single chart shows both dimensions. | Plotly has no native marimekko but can be built from `bar` with manual offsets. |
| **Slope chart** (two-period side-by-side line) | cardWeekOverWeek factor section: this week vs. last week active exposure for top 12 factors. Visually richer than a bar of deltas. | `scatter` mode `lines+markers` with x = ['prior','curr']. |
| **Highlight tables** (heatmap with cell text) | The sector × strategy heatmap already exists. Generalize to (factor × strategy) and (country × strategy). | Plotly `heatmap` with `texttemplate`. |
| **Dot plots** (bar replacement when bars are too dense) | Holdings table sparkline column — when 1000 holdings overwhelm a bar chart. | `scatter` with `mode:'markers'`. |
| **Reference band overlays** (5/95-percentile shading) | Historical Trends mini charts (TE, AS, Beta) — show the 5y range as shaded band. PM sees "is this week extreme?" at a glance. | `scatter` with `fill:'tonexty'` between two series. |
| **Bins-with-count quick view** (histogram with annotated mean/median) | Holdings active-weight distribution: skewness signals concentration risk. | Plotly `histogram` + shapes for mean line. |

If any of these speak to you, ping me and I'll spec it.

### The honest assessment

You will probably use Tableau **5-10 times during the next phase of RR** for sketching, then stop. The reason is friction:
- Re-exporting data from JSON to CSV every time you want to try a new chart gets old fast.
- The dark-theme mismatch makes the sketch feel "not real."
- Once you've used the HTML mockup mechanism (Section 2) a few times, it becomes the faster path because it lives **next to the actual code**.

That said, having Tableau in your back pocket is a real edge: when you're stuck on "what's the right chart for this?" the Show Me panel is genuinely the best brainstorming tool in the BI world. Use it for that.

---

## Section 2 — Visual Mockup Mechanism

### Decision: standalone HTML files in `/viz-specs/`

Every new viz proposal gets a single `.html` file you open directly in a browser. No build step, no Tableau, no PDF. The file is self-contained — Plotly via CDN, all CSS tokens copy-pasted from `dashboard_v7.html`, synthetic but realistic numbers.

### Why HTML wins over PDF / Figma / Tableau

| Format | Pros | Cons | Verdict |
|---|---|---|---|
| **Standalone HTML** | Pixel-matches the real dashboard. Interactive (hover, zoom, click). Plotly works natively. Lives in the repo, evolvable into the spec. Diffable in git. | Slightly more setup (one HTML file) than a PDF screenshot. | **Winner.** |
| **PDF** | Printable, shareable. | Static. Doesn't show hover behavior. Doesn't match font rendering exactly. PDF generation adds a build step. | No. |
| **Figma** | Best for early-stage "what if the layout looked totally different?" thinking. Easy multi-frame compare. | Can't show real Plotly interactions. PM sees a fake. Doesn't match production color/font without manual maintenance. | Optional, only for big layout rethinks. |
| **Tableau workbook** | Quick to author. | Doesn't match RR theme. Requires Tableau open. Loses interactivity gap. | Only for ideation, not previews. |
| **Markdown spec only** | Lightweight. | PM can't *see* the design. Decisions get postponed pending an actual render. | **Insufficient on its own.** Use mockup + spec together. |

### Mockup file conventions

Every mockup file:

1. **Lives at `/Users/ygoodman/RR/viz-specs/{tile-id}-mockup.html`.** Same directory as the markdown spec. Spec and mockup are siblings.
2. **Self-contained.** No imports of the real dashboard's JS. Plotly via `https://cdn.plot.ly/plotly-2.27.0.min.js`. CSS tokens copied verbatim from lines 25–30 of `dashboard_v7.html`.
3. **Has a banner at top.** "PREVIEW ONLY · synthetic numbers · NOT live." Prevents anyone (including future me) from confusing the mockup for a working tile.
4. **Shows 2–3 candidate designs side by side.** Even when one is recommended. Comparison is the whole point.
5. **Each candidate has a "Why this design wins / trade-off" notes box.** Plain English. No jargon.
6. **Synthetic numbers are realistic.** Use plausible TE/AS/Beta values. Use real-looking tickers (NESN-CH, SAP-DE, etc.). PMs reject mockups with `"AAA"` and `"BBB"` instantly.

### How you evaluate a mockup

When I ping you "mockup ready: `viz-specs/{tile}-mockup.html`," do this:

1. **Open it in a browser.** `open /Users/ygoodman/RR/viz-specs/{tile}-mockup.html` (or just double-click in Finder).
2. **Spend ~3 minutes.** Look at all candidates. Hover, click, try the interactions.
3. **Answer 3 questions:**
   - **a) Does the recommended option answer the PM question I asked it to?** (yes / no / mostly)
   - **b) Is the visual density right?** (too sparse / about right / too dense)
   - **c) Should I implement Option A as-is, blend two options, or rethink?**
4. **Reply in chat.** One paragraph is enough. Then I either implement (if green-lit) or revise the mockup (if not).

### Worked example: cardWeekOverWeek

I wrote a complete working mockup at:

**`/Users/ygoodman/RR/viz-specs/cardWeekOverWeek-mockup.html`**

It opened in your browser when this doc was generated. Three candidates:

- **Option A** — KPI strip + 3-column move list (added/dropped/resized) + factor rotation footer with sparklines. Recommended. Best for the PM's morning glance.
- **Option B** — Bubble scatter plot of every position's |Δwt| × |Δ%T|, sized by total %T contribution. Denser, more analytical, harder to glance.
- **Option C** — 13-week timeline strip showing each metric's recent history, current week highlighted. Good context, loses holdings-level detail.

Each has a "trade-off" notes box explaining why I'd pick or skip it. The mockup uses **fake** holdings data (NESN-CH, SAP-DE, etc.) but the visual behavior is exactly what production will look like.

### Mockup file lifecycle

```
spec request from user
        ↓
[1] data-viz subagent writes:
    /viz-specs/{tile}-mockup.html  (visual)
    /viz-specs/{tile}-spec.md      (technical)
        ↓
[2] user opens HTML, evaluates
        ↓
[3] user replies: "go with A" / "blend A+B" / "rethink"
        ↓
[4] subagent revises mockup (if needed)
        ↓
[5] coordinator implements in dashboard_v7.html
        ↓
[6] mockup file kept in /viz-specs/ as reference for the design decision
```

The mockup file is **never deleted.** It serves as the historical record of why the tile looks the way it does. Six months later when someone asks "why didn't we use a bubble chart?" the Option B alternative is right there with the trade-off note.

### What goes in the mockup vs. the spec

| Goes in the mockup (.html) | Goes in the spec (.md) |
|---|---|
| Visual layout | Field-by-field source data table |
| Color encoding | Plotly trace config (exact JSON) |
| Hover behavior | Edge case handling |
| Two or three design candidates | Implementation notes for coordinator |
| Synthetic numbers | localStorage prefs key (if interactive) |
| Trade-off notes per candidate | Validation plan / test checklist |

The mockup answers "**does this look right?**" The spec answers "**how do we build it?**"

### Anti-patterns I will not fall into

- ❌ **A mockup file with no real data shape.** If the live tile pulls from `cs.hold[].factor_contr.value`, the mockup must show what `factor_contr.value` realistically looks like across 5–10 holdings. No `Math.random()`.
- ❌ **A mockup that uses the wrong tokens.** Pixel-exact match to `dashboard_v7.html` colors/fonts is the whole point.
- ❌ **A mockup with one candidate.** Always 2–3. Forces the trade-off conversation.
- ❌ **A mockup that's prettier than the live dashboard.** Defeats the purpose. Use the same density / spacing / type scale as the rest of RR.
- ❌ **A mockup that wires to live data via JS imports.** Defeats the standalone-preview promise. Synthetic numbers only.

---

## Section 3 — Workflow Proposal

### The new design loop, end to end

```
        ┌─────────────────────────────────────────────────────┐
        │  USER has a vague idea: "tile that shows turnover"  │
        └─────────────────────────────────────────────────────┘
                                ↓
                  [optional] Tableau sketch (5-15 min)
                  – use anonymized data
                  – screenshot the chart you like
                                ↓
                  USER pings me: "spec the tile"
                  (with screenshot if you have one)
                                ↓
        ┌──────────────────────────────────────────────┐
        │  data-viz subagent produces TWO files:       │
        │  – /viz-specs/{tile}-mockup.html  ← visual   │
        │  – /viz-specs/{tile}-spec.md      ← technical│
        └──────────────────────────────────────────────┘
                                ↓
                  USER opens the .html, evaluates 3 min
                                ↓
              ┌─────────────────┴─────────────────┐
              ↓                                   ↓
    "implement Option A"                  "blend A+B" / "rethink"
              ↓                                   ↓
    coordinator implements         data-viz subagent revises mockup
              ↓                                   ↓
    smoke_test.sh + visual                    loop back
    QA in real dashboard
              ↓
    USER signs off in browser
              ↓
    BACKLOG entry closed
```

### What I commit to

1. **Every new viz proposal gets both a mockup file and a spec file.** No spec without a visual.
2. **Mockup files are ready to open within the same session you ask.** No "I'll send it tomorrow."
3. **Three candidates, not one.** Even when one is obvious, the comparison forces clarity.
4. **Synthetic numbers always look plausible.** Real-looking tickers, realistic TE values, sensible factor names.
5. **The mockup file is never deleted, even after implementation.** Permanent design archive in `/viz-specs/`.
6. **CSS tokens stay in sync.** When `dashboard_v7.html` changes its color tokens, I update the mockup `:root` block to match. Manual today, scriptable later.

### What you commit to (asks)

1. **3 minutes of evaluation per mockup.** Open, look, reply with "go" / "rethink" / "blend." Don't let mockups pile up un-reviewed.
2. **Use Tableau when you're stuck on "what chart should this even be?"** Skip it for "I want a bar chart with X column added."
3. **Tell me when a screenshot mismatches reality** (color off, font wrong, density looks weird). I'll fix the token map.

### Toolchain helpers I would add (when asked)

These are not built yet. Mention if you want them:

| Helper | What it does | Effort |
|---|---|---|
| `export_to_tableau.py` | Export one section of `latest_data.json` to a flat CSV for Tableau Show Me sketching. | 30 min. |
| `mockup-template.html` | Skeleton with all CSS tokens + Plotly + 3-candidate grid. Copy-paste base for new mockups. | 15 min. |
| `tokens-sync.sh` | Diff `:root` block in mockups vs. `dashboard_v7.html`, alert on drift. | 20 min. |
| `viz-specs/INDEX.md` | Auto-generated index of every mockup/spec pair, status (proposed / approved / implemented). | 30 min. |

### The honest expectation

Of the 10 candidates in `NEW_TILE_CANDIDATES.md`, you'll probably implement 4–5 in the next phase. Each one runs through this loop. The first 1–2 will feel slow (you're learning the eval rhythm); by tile #3 the loop will feel snappy and you'll wonder why we didn't always work this way.

---

## Quick reference

**Tableau** — sketchbook only, never deployment. Use Tableau Desktop locally with anonymized data. Don't publish.
**Mockups** — always at `/viz-specs/{tile}-mockup.html`. Self-contained HTML with Plotly CDN. Three candidates. Open in browser, evaluate in 3 min.
**Working example** — `/Users/ygoodman/RR/viz-specs/cardWeekOverWeek-mockup.html` (already opened in browser when this doc was generated).
