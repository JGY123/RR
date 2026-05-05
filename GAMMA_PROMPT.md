# Gamma Prompt — RR Decks for Alger

**Drafted:** 2026-05-05
**Purpose:** A reusable Gamma prompt template for generating professional, on-brand decks about RR. The user pastes the prompt into Gamma (gamma.app), tweaks the variables, and gets a starting point that's already 70-80% of the way to a hand-finished slide deck.

---

## How to use

1. Open Gamma → "Create with AI" → paste the prompt below.
2. Replace the `[BRACKETED]` placeholders with the actual values for your deck.
3. Pick the deck length (8 / 12 / 20 slides) based on audience.
4. After Gamma generates: download as PowerPoint, hand-tune the 1-2 slides where Gamma misses nuance, ship.

---

## The master prompt

```
Create a professional, polished presentation deck for Fred Alger Management's
internal portfolio risk dashboard, "Redwood Risk Control Panel" (RR).

Audience: [SENIOR PM / RISK COMMITTEE / LEADERSHIP / FACTSET QUANT TEAM]
Length: [8 / 12 / 20] slides
Tone: Confident, data-driven, peer-quant. Avoid hype, marketing language, or
explanations of basic financial concepts (the audience is sophisticated).

Brand identity (Fred Alger Management):
- Primary navy: #002B54 (headers, axis labels)
- Primary blue: #136CAF (links, primary chart series, accent)
- Light blue accent: #4FA3DF (hover, secondary series)
- Background: #FFFFFF (white) with #F9F9F9 (off-white) panels
- Body text: #333 (high emphasis), #717073 (muted)
- Positive (gain): #41834F (green)
- Negative (loss): #A32F2F (red)
- Typography: Benton Sans family (Light, Book, Regular, Medium, Bold)
  fallback: "Helvetica Neue", Arial
- Logo: wordmark "Alger" in navy (no symbol)
- Visual signature: optional 32-degree skewed-parallelogram CTAs
- Tagline (use sparingly): "Inspired by Change. Driven by Growth."
- Brand voice: heritage + innovation, formal but not stuffy, declarative

What RR is (one paragraph for context):
A single-pane portfolio risk dashboard for Alger's investment strategies,
sourced entirely from FactSet Portfolio Attribution exports. ~30 tiles
across 4 tabs (Overview / Exposures / Risk / Holdings). Built around a
strict no-fabrication policy: every numeric cell traces back to a
documented source path; missing data renders as "—" rather than a guess.
Current scope: 6 international strategies (ACWI, IDM, IOP, EM, GSC, ISC)
with 7-12 years of weekly history per strategy. Roadmap to 25+ strategies
including domestic accounts.

Differentiators vs FactSet PA directly:
1. Single-pane synthesis across strategies (cross-strategy heatmaps,
   ranked top-N by TE, etc.)
2. Layered data-integrity monitoring (4-layer system: parser verifier,
   cross-week aggregate verifier, trend monitor, FactSet inquiry log)
3. Anti-fabrication discipline: when FactSet's data has gaps or
   inconsistencies, RR surfaces them honestly via "F18 disclosure footers"
   rather than silently rescaling
4. Append-only history: each weekly ingest unions into cumulative
   per-strategy state (B114 architecture)
5. Tile-audit cadence: every tile carries a structured audit doc
   (data accuracy / functionality parity / design consistency)

Deck structure (suggested; adapt to audience):
1. Title slide: "Redwood Risk Control Panel" + Alger logo + tagline + date
2. The PM problem we're solving (1-2 slides)
3. The dashboard at a glance (full-width screenshot of Overview tab)
4. The 5 operational loops (audit cadence / data integrity / FactSet
   inquiry / refactor + lint / persona training)
5. The data integrity model (visual diagram of the 4-layer monitoring)
6. Anti-fabrication in action: how we surface FactSet data issues
   honestly (F18 example)
7. Cross-strategy reconciliation example (the F18 cross-strategy table:
   94→134% per-holding %T sum behavior — one of the most concrete examples
   of the discipline)
8. The roadmap (next 1-2 weeks, 1-3 months, 3-6 months — tier A/B/C)
9. Scale plan (6 to 25+ accounts, gzip compression, weekly ingest
   pipeline)
10. Closing: "Make it right, scale it slowly, become more expert each
    cycle." (Alger's heritage-plus-innovation theme alignment)

Use plenty of white space. Each slide should have one core message.
Charts should be data-dense but uncluttered (Tufte-style, not
infographic-style). Where possible, use Alger's brand colors for
accent series rather than generic palette.

Avoid:
- Stock photos (especially of generic businesspeople / handshakes / globes)
- Marketing buzzwords (synergy, leverage as verb, etc.)
- Soft-focus claims ("transformative", "best-in-class", "cutting-edge")
- Graphs without axis labels or units
- Over-bulleted lists (3-5 bullets max per slide; if more, restructure)
- Quote blocks unless the quote is concrete (e.g., from a specific PM
  or a written commitment, not a generic motivational quote)
```

---

## Variant prompts for specific audiences

### A. Internal PM walkthrough (12 slides, ~5-min talk)

Add to the master prompt:

```
ADDITIONAL CONTEXT FOR THIS DECK:

This is a daily-use walkthrough for PMs who'll use the dashboard.
Focus on:
- The 4 daily moves (glance Overview, check Risk tab, drill into
  Holdings, set notes/flags)
- Conventions to know (em-dash means missing, ᵉ means derived,
  Universe pill semantics, MCR is not a percent, signed TE colors)
- Honest caveats (F18 is open; B114 history is being built up)
- Where to look when something seems wrong (right-click for note;
  hover for source path; click About for full provenance)

Tone: practical, not promotional. PMs care about "how do I use this
on Monday morning" not "isn't our discipline cool."

DO NOT include:
- Slides about architecture or build process
- Slides about FactSet inquiries (that's a separate deck)
- Marketing claims about how this is better than alternatives
```

### B. Senior leadership / IC update (8 slides, ~3-min)

Add to the master prompt:

```
ADDITIONAL CONTEXT FOR THIS DECK:

This is an executive update — IC or senior leadership audience.
They want to know:
- What does the dashboard do (1 slide, 30 seconds)
- What's the discipline that makes it trustworthy (1 slide)
- What's the audit cadence + what does it surface (1-2 slides)
- What's queued for the next quarter (1 slide)
- Open risks they should be aware of (1 slide)
- Investment ask (if any — usually no; this is informational)

Tone: confident, terse. Each slide should fit on one breath of
spoken explanation.

DO NOT include:
- Code-level details (parser version, format version, anti-pattern names)
- Tool screenshots beyond Overview tab
- Long bullet lists
```

### C. FactSet quant team (10 slides, ~10-min meeting)

Add to the master prompt:

```
ADDITIONAL CONTEXT FOR THIS DECK:

The audience is FactSet's PA quant lead and team. They want to
understand:
- Our internal architecture (parser, JSON layer, tile contract — 1 slide)
- The cross-strategy reconciliation that surfaced F18 (the 94→134% finding)
- Our internal-side parser hygiene fixes (F19) so they know we've
  cleaned house before raising this
- The three patterns that we cannot reconcile (non-uniform deviation,
  GSC 100%-coverage counter-example, signed-semantics finding)
- Our six numbered questions
- What we'd love their team to share (methodology white paper, %T_Check
  semantics, etc.)

Tone: technical peer-to-peer, not customer-to-vendor. They are the
domain experts; we are sharp users with specific questions.

DO NOT include:
- Marketing about our dashboard being a great product
- Generic "thanks for being a great partner" closers
- Anything that sounds like a feature request unless it's literally one
  (if it is one, label it explicitly so they don't have to guess)
```

### D. Multi-strategy showcase (15-20 slides, ~15-min)

Add to the master prompt:

```
ADDITIONAL CONTEXT FOR THIS DECK:

Show the dashboard in action across all 6 strategies:
- 1 slide per strategy summarizing TE / Active Share / Beta / top
  contributors / factor tilts
- Cross-strategy comparison slide (heatmap of factor exposures across
  all 6)
- Cross-strategy %T reconciliation slide (the F18 finding)
- 1-2 slides on data freshness + ingest cadence

Tone: data-led. Every slide should have at least one chart or table.
Avoid prose-heavy slides.

Plotly chart conventions for this deck:
- Background: white (#FFFFFF)
- Axis text: #002B54 navy
- Primary series: #136CAF blue
- Secondary series: #4FA3DF light blue
- Benchmark / reference: #717073 gray, dotted
- Positive: #41834F green
- Negative: #A32F2F red
```

---

## Example: filled-in prompt for next week's PM walkthrough

```
Create a professional, polished presentation deck for Fred Alger Management's
internal portfolio risk dashboard, "Redwood Risk Control Panel" (RR).

Audience: SENIOR PM (international equity desk)
Length: 12 slides
Tone: Confident, data-driven, peer-quant. Avoid hype, marketing language, or
explanations of basic financial concepts (the audience is sophisticated).

[... master prompt body unchanged ...]

ADDITIONAL CONTEXT FOR THIS DECK:

This is a daily-use walkthrough for PMs who'll use the dashboard.
Focus on:
- The 4 daily moves (glance Overview, check Risk tab, drill into
  Holdings, set notes/flags)
- Conventions to know (em-dash means missing, ᵉ means derived,
  Universe pill semantics, MCR is not a percent, signed TE colors)
- Honest caveats (F18 is open; B114 history is being built up)
- Where to look when something seems wrong (right-click for note;
  hover for source path; click About for full provenance)

Tone: practical, not promotional. PMs care about "how do I use this
on Monday morning" not "isn't our discipline cool."

DO NOT include:
- Slides about architecture or build process
- Slides about FactSet inquiries (that's a separate deck)
- Marketing claims about how this is better than alternatives
```

---

## Slide-by-slide ideas — for when you want to bypass Gamma and write it yourself

If you want a hand-crafted deck instead of Gamma-generated:

| # | Slide | Content |
|---|---|---|
| 1 | Title | Logo + "Redwood Risk Control Panel" + "Inspired by Change. Driven by Growth." + date + presenter |
| 2 | Why we built it | 3 bullets: PMs spend X minutes per day in PA; cross-strategy comparison is hard; data quality drift goes uncaught. RR addresses all three. |
| 3 | The dashboard at a glance | Full-width screenshot of Overview tab in Alger theme. One annotation pointing at cardThisWeek KPIs. |
| 4 | The 4 daily moves | Numbered list: glance / check / drill / flag. One screenshot per. |
| 5 | The data integrity discipline | The 4-layer monitoring diagram (L1 parser / L2 cross-week / L3 trend / L4 inquiry). One line per. |
| 6 | Anti-fabrication in action | Side-by-side: "what FactSet doesn't ship" vs "what we surface honestly." Example: cardUnowned 196/819 footer. |
| 7 | Cross-strategy reconciliation | The F18 table (94→134% across 6 strategies). One paragraph: this is the kind of question RR's discipline makes findable. |
| 8 | Tile audit cadence | Stat: 14 tile audit docs filed in May. Quarterly cadence. Sample audit doc snippet. |
| 9 | Roadmap | Tier A (next 2 wks) / Tier B (next 3 mo) / Tier C (next 6 mo). Bulleted. |
| 10 | Scale plan | 6 → 25 accounts. 1.6 GB → 5 GB. gzip → 700 MB. Weekly ingest. |
| 11 | Risks + open questions | F18 reply pending. First B114 production exercise. PM rollout scope TBD. |
| 12 | Closing | "Make it right. Scale it slowly. Become more expert each cycle." Alger heritage-plus-innovation logo. |

---

## After Gamma generates: hand-finishing checklist

Gamma is good at structure + brand colors but weak on:

1. **Specific numbers** — Gamma may invent "500+ holdings tracked" type stats. Replace with the actual numbers from `STRATEGIC_REVIEW_NEXT.md` and `ROADMAP.md`.
2. **Specific tile screenshots** — Gamma uses placeholder images. Replace with real screenshots from your dashboard (use the PNG download from any tile chrome).
3. **Tagline placement** — Gamma may overuse the tagline. Limit to 1-2 placements (title + closing).
4. **Logo file** — Gamma will use a generic placeholder. Replace with the actual Alger wordmark.
5. **Closing CTA** — Gamma defaults to "Get Started" / "Learn More" buttons. Replace with the actual CTA: "Open the dashboard at https://rr.alger.internal:3099" or "Email questions to [user-name]@alger.com."

---

## When to use Gamma vs hand-craft

**Use Gamma when:**
- You need a deck in <30 minutes
- The audience is internal and you're not the only voice presenting
- The deck is informational / status-update (low-stakes)
- You want a starting point + you'll hand-finish 1-2 slides

**Hand-craft (or have a designer) when:**
- The audience is external (FactSet exec, board, regulatory)
- The deck is the basis of a decision (investment ask, IC vote)
- You're presenting solo and the deck IS the meeting
- You have the time to do every slide yourself (typical: 4-6 hr for a 10-slide deck)

---

## Closing

This prompt template + the Alger brand specifics save the user 1-2 hours per deck on average. The marginal cost of generating a deck drops to ~10 minutes (paste prompt → tweak → download → hand-finish). Once the user has 3-4 of these decks (PM, leadership, FactSet, board), the deck library becomes a reusable asset.

When the dashboard ships major changes, regenerate decks with updated content — the prompt structure stays.
