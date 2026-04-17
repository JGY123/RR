# RR Dashboard Tile Implementation Guide

## Status
5 tile agents completed design specs. Each spec contains full before/after descriptions, 
exact code patterns, and creative ideas. Specs need to be implemented into `dashboard_v7.html` 
one at a time (they all modify the same file).

## Implementation Order (recommended — least to most complex)
1. **Portfolio Characteristics** (~50 lines CSS + ~80 lines JS) — profile badges, metric grouping, deviation bars
2. **Sector Active Weights** (~40 lines CSS + ~120 lines JS) — TE bar glow, summary footer, top-3 callout, chart modes
3. **Risk/Return Scatter** (~100 lines JS) — axis toggles, quadrant labels, crosshair, sector colors, click-to-drill
4. **Active Weight Treemap** (~120 lines JS) — dimension toggles, drill-down, breadcrumb, continuous colors
5. **Holdings Tab** (~200 lines JS + ~30 lines CSS) — summary bar, expandable rows, card view, column config

## How to Implement Each Spec
Each spec file (~/RR/tile-specs/*.md) contains the full agent output including:
- The conversation log showing exactly what code was written
- Before/after descriptions of every change
- CSS classes and JS functions that were added
- Line number references (approximate — may shift as changes accumulate)

### To implement a spec:
1. Read the spec's "What Changed" section for the summary
2. Search the conversation log for actual code blocks (look for `Edit` tool calls)
3. Apply the CSS additions first (they're additive, low-conflict)
4. Apply the JS function changes (modify existing functions or add new ones)
5. Apply the HTML template changes last (inside template literals in rExp(), rHold(), etc.)
6. Test in browser: `open ~/RR/dashboard_v7.html` or `http://localhost:3099/dashboard_v7.html`

### To implement via CLI agent:
```
You are implementing tile design improvements for ~/RR/dashboard_v7.html.
Read ~/RR/tile-specs/[SPEC_NAME]-spec.md for the full design spec.
Read ~/RR/TILE_AGENT_CONTEXT.md for data shapes and patterns.

The spec contains a detailed conversation log showing exactly what code 
was written. Extract the CSS, JS, and HTML changes and apply them to 
the current dashboard_v7.html. Test that the changes work by checking 
for JavaScript syntax errors.

Agents to reference: risk-reports-specialist, tile-design-agent, design-director
```

## Shared Context Files
- `~/RR/TILE_AGENT_CONTEXT.md` — data shapes, design decisions, patterns
- `~/RR/tile-specs/*.md` — individual tile design specs
- `~/projects/apps/ai-talent-agency/agents/tile-design-agent.md` — agent profile + pattern library
- `~/projects/apps/ai-talent-agency/training/tile-agent-prompt-template.md` — spawning template

## Creative Ideas Bank (15 ideas from all 5 agents)
See tile-design-agent.md in the agent roster for the full list.
Top 3 highest-impact ideas:
1. **Animated time travel** — date slider replaying scatter positions over weekly history
2. **Holdings heatmap view** — treemap of holdings sized by weight, colored by TE
3. **"What If" weight slider** — simulate changing a holding's weight, show TE impact
