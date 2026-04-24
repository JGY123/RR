# Handoff to Executor — B105 Phase 1 "Look as sharp"

**Date:** 2026-04-24
**From:** Advisor (prior Claude session in another tab — has full context on all 24 tile audits, data-foundation-v1, and the SurpriseEdge deep-dive)
**To:** You (fresh Claude Code session in `~/RR`)
**Relationship:** advisor ↔ executor. User relays questions. Same pattern as the `data-foundation-v1` handoff you successfully shipped earlier today (commits 7bef572 → 85c83a2).

---

## First 90 seconds — orient yourself

Run in order:

```bash
cat ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md    # mandatory RR context
cat ~/RR/CLAUDE.md                                                         # project conventions
cat ~/RR/SESSION_STATE.md                                                  # where we are (look at "Next up" #2)
cat ~/RR/design/SURPRISEEDGE_LESSONS.md                                    # YOUR MAIN SPEC
grep -A 20 "B105 · Phase 1" ~/RR/BACKLOG.md                                # scope confirmation
git -C ~/RR log --oneline -15
git -C ~/RR tag -l | tail -10
```

After reading: you'll know 24 tiles are audited and at `.v1.fixes`, data-foundation shipped, SurpriseEdge was studied directly from its v3.2.0 source on `~/Desktop`, and B105 is Phase 1 of a 3-phase adoption ladder.

---

## Your mission: B105 Phase 1 "Look as sharp"

**Goal:** transform RR's visual register from "web app dark mode" to "SurpriseEdge-tier enterprise terminal" in one commit. User's literal framing: "I'd settle for just as good as SurpriseEdge" — deliver parity or better.

**Scope is strictly cosmetic. Zero tile-render-function edits. Every `.v1.fixes` tile's behavior is preserved exactly.**

Tag at ship: `design-polish-v1`. Then it's marathon-time.

---

## Deliverables — execute in this order

### 1. Safety tag first
```bash
cd ~/RR
NOW=$(date +%Y%m%d.%H%M)
git tag "working.${NOW}.pre-b105"
```

### 2. Bundle fonts (~80 KB, the single biggest visual change)
```bash
mkdir -p ~/RR/fonts
cp ~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/dm-sans-latin.woff2 ~/RR/fonts/
cp ~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/dm-sans-latin-ext.woff2 ~/RR/fonts/
cp ~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/jetbrains-mono-latin.woff2 ~/RR/fonts/
cp ~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/jetbrains-mono-latin-ext.woff2 ~/RR/fonts/
ls -lh ~/RR/fonts/
```

Copy the `@font-face` declarations from `~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/fonts/fonts.css` into the top of `dashboard_v7.html`'s `<style>` block (update relative paths to `fonts/dm-sans-latin.woff2` etc.).

Set:
```css
body { font-family: 'DM Sans', system-ui, -apple-system, sans-serif; }
.mono { font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }
```

### 3. Adopt palette tokens
Swap the existing `--*` token declarations in the dashboard's `<style>` root rule. Use these SurpriseEdge-canonical values (from `~/Desktop/SurpriseEdge-Handoff/SurpriseEdge-v3.2.0-source/src/constants.js`):

```css
:root {
  --bg:          #0b0e14;
  --card:        #12161f;   /* was --surf */
  --cardBorder:  #1e2433;   /* was --grid */
  --grid:        #1e2433;
  --text:        #c8cdd8;   /* was --txt */
  --txt:         #c8cdd8;   /* alias kept for back-compat */
  --textDim:     #6b7280;   /* was --txtDim or similar */
  --textBright:  #eef0f4;   /* was --txth */
  --txth:        #eef0f4;   /* alias */
  --accent:      #22d3ee;   /* CYAN — was --pri */
  --pri:         #22d3ee;   /* alias — RR tiles use --pri extensively */
  --accentDim:   #0e7490;
  --univ:        #6366f1;   /* old indigo becomes secondary */
  --pos:         #10b981;
  --posBg:       #10b98118;
  --warn:        #f59e0b;
  --warnBg:      #f59e0b18;
  --neg:         #ef4444;
  --negBg:       #ef444418;
  --prof:        #fb923c;   /* keep existing */
  --upload:      #8b5cf6;
  --uploadBg:    #8b5cf620;
  --zero:        #1e2433;   /* plotly zerolines */
}
```

**Key decision:** keep `--pri` as an alias for the new cyan `--accent` so existing tiles that reference `var(--pri)` automatically inherit the cyan. Add `--univ: #6366f1` for any place that was semantically "benchmark indigo" vs "accent" (there may be ~5 such sites — grep `var(--pri)` and audit).

### 4. Custom scrollbars (4 lines, immediate polish)
```css
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--cardBorder); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--textDim); }
```

### 5. Card-title typography
Update the `.card-title` rule (or equivalent — RR may inline some):
```css
.card-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--textDim);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 8px;
}
```

Many RR card titles are inline-styled. You may need to add class `card-title` explicitly where it's missing, or update inline styles. Don't change the title TEXT — only the typography rule.

### 6. Row separators at 8% alpha
Find the current `table td` or `tbody tr` border rule and swap to:
```css
table td { border-bottom: 1px solid color-mix(in srgb, var(--cardBorder) 15%, transparent); }
```
(Or `#1e243326` — 26 hex ≈ 15% alpha — if `color-mix` isn't reliable across target browsers. Test.)

### 7. Apply `.mono` to every numeric cell
This is the highest-impact sweep. Strategy:
- First, add a global fallback: `td.r { font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }` — catches every right-aligned cell.
- That's probably 80% of the work.
- Audit the remaining: grep for cells that hold numbers but aren't class `r` (rare — RR's convention is consistent). Add `class="mono"` individually if needed.

### 8. Hex-alpha pill convention
Pills vary across tiles. Unify to:
```css
.pill {
  padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all .15s;
  background: transparent; color: var(--textDim);
  border: 1px solid var(--cardBorder); white-space: nowrap;
}
.pill.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
.pill.pos    { background: color-mix(in srgb, var(--pos) 15%, transparent); color: var(--pos); border-color: color-mix(in srgb, var(--pos) 40%, transparent); }
.pill.neg    { background: color-mix(in srgb, var(--neg) 15%, transparent); color: var(--neg); border-color: color-mix(in srgb, var(--neg) 40%, transparent); }
.pill.warn   { background: color-mix(in srgb, var(--warn) 15%, transparent); color: var(--warn); border-color: color-mix(in srgb, var(--warn) 40%, transparent); }
```

Find existing pill-like toggles across tiles — cardFacContribBars mode toggle, cardRanks rank pills, cardTreemap dim picker, filter-bar pills on Overview — and migrate inline styles to this class where possible. If migration is risky for any tile, leave it alone and note it for Phase 2 (B106).

### 9. Header gradient bar + two-tone wordmark
RR probably has a header/brand area. Find it and update to:
```html
<div style="display:flex;align-items:center;gap:8px">
  <div style="width:4px;height:24px;border-radius:2px;background:linear-gradient(180deg,var(--accent),var(--univ))"></div>
  <span style="font-size:16px;font-weight:700;color:var(--textBright);letter-spacing:-0.3px">
    Redwood<span style="color:var(--accent)">Risk</span>
  </span>
</div>
```

(Or whatever naming the user prefers. Current dashboard may say "RR" or "Redwood Risk Control Panel" — match the existing title convention, just apply the two-tone + gradient bar pattern.)

---

## Verification protocol (mandatory before push)

After all CSS is in place:

1. **Disk verify:**
   ```bash
   ls -lh ~/RR/fonts/                # 4 woff2 files
   grep -c "JetBrains Mono" ~/RR/dashboard_v7.html    # ≥ 1 (font-face + .mono rule)
   grep -c "DM Sans" ~/RR/dashboard_v7.html           # ≥ 1
   grep -c "#22d3ee\|--accent" ~/RR/dashboard_v7.html # many (new cyan accent)
   wc -l ~/RR/dashboard_v7.html                      # delta = small (mostly CSS additions)
   ```

2. **Syntax check** (confirms no broken HTML/JS):
   ```bash
   node -e "
   const fs=require('fs');
   const html=fs.readFileSync('dashboard_v7.html','utf8');
   const re=/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g;
   let m,i=0,errs=0;
   while((m=re.exec(html))!==null){i++;try{new Function(m[1])}catch(e){errs++;console.log('Block',i,':',e.message)}}
   console.log('Parsed',i,'script blocks;',errs,'errors');
   "
   ```
   Expect 0 errors.

3. **Browser regression — MANDATORY.** Open `dashboard_v7.html` in Chrome/Safari, drag-drop `sample_data.json`. Walk every tab:
   - Overview → cardThisWeek, cardSectors, cardChars, cardFacButt, cardFacDetail, cardFRB, cardAttribWaterfall, cardCountry, cardGroups, cardRanks, cardScatter, cardTreemap, cardMCR, cardUnowned, cardCorr, cardAttrib, cardRegions, cardBenchOnlySec, cardWatchlist
   - Sectors tab
   - Regions / Countries / Holdings / Factors tabs
   - Risk tab → cardRiskHistTrends, cardRiskFacTbl, cardTEStacked, cardFacContribBars

   **For each tile:** confirm it renders, no console errors, text is readable (DM Sans is slightly narrower — if any hardcoded-width column gets weird, fix inline), numbers look aligned (JetBrains Mono on right-align cells).

   **Known risk zones:**
   - Tiles with inline `color:#6366f1` (indigo) as a semantic "benchmark" color, now auto-switched to cyan — may need to swap those specific inline references to `var(--univ)` instead of inheriting `var(--pri)` = cyan.
   - `cardTreemap` has a 5-color rank palette (hardcoded hex) — leave as-is for Phase 1; flag for B106.
   - Plotly charts that used `THEME().tick` etc. already pick up the new palette via `getComputedStyle` — should JUST WORK.
   - `inlineSparkSvg` already tokenized (confirmed Batch 5 ledger correction).

4. If any tile breaks visually, surface it as `ADVISOR QUESTION: cardXXX looks broken because Y — should I fix inline or defer?`

---

## Commit + tag

```bash
# Stage by name (per project standing rule — NEVER git add .)
git add dashboard_v7.html fonts/ design/SURPRISEEDGE_LESSONS.md  # lessons doc is already committed but no harm to restage if you updated
git status --short

git commit -m "$(cat <<'EOF'
feat(design): B105 Phase 1 — SurpriseEdge-parity visual polish

Implements B105 from BACKLOG. Pure cosmetic + font bundle + class sweep.
Zero tile-render-function edits; all 24 .v1.fixes tile states preserved.

Changes:
- fonts/: bundled DM Sans + JetBrains Mono woff2 (4 files, ~80 KB) copied
  from SurpriseEdge v3.2.0 source (LICENSED: DM Sans SIL OFL; JetBrains
  Mono Apache 2.0 — both permissive, redistributable)
- @font-face declarations inlined in <style>
- body font-family → 'DM Sans'
- .mono class applied globally via td.r + explicit class on inline nums
- Palette tokens adopted from SurpriseEdge constants.js:
    --bg #0b0e14, --accent #22d3ee (cyan primary, was indigo)
    --univ #6366f1 (RR's old --pri retained as benchmark-semantic)
    --text/--textDim/--textBright + hex-alpha conventions
- 6px custom scrollbars (::-webkit-scrollbar)
- 11px uppercase card-titles with 1.5px letter-spacing
- Row separators at ~15% alpha (#1e243326)
- Unified .pill convention with color-mix hex-alpha backgrounds
- Header: 4px vertical gradient bar + two-tone wordmark

Verification: disk greps clean, node syntax check 0 errors, browser
regression across all 24 tiles → all render, no console errors,
DM Sans layout shifts within tolerance.

Next phase: B106 "Feel as sharp" (post-marathon).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"

git tag design-polish-v1 <HEAD_SHA> -m "SurpriseEdge-parity visual polish applied. All 24 tiles render cleanly with DM Sans + cyan palette."
gh auth switch --user JGY123
git push origin main
git push origin design-polish-v1
```

## Update SESSION_STATE after push

Append to the "Checkpoint log" section, newest-on-top:

```
- **2026-04-24 · B105 Phase 1 shipped — SurpriseEdge-parity visual polish** — DM Sans + JetBrains Mono bundled, palette migrated to SurpriseEdge canonical tokens (cyan accent, deeper bg), .mono + hex-alpha pills + 6px scrollbars + uppercase card-titles + row-alpha separators applied globally. Zero tile-render-fn edits; all 24 .v1.fixes states preserved. Browser regression clean. Committed <SHA>, tagged `design-polish-v1`, pushed. Marathon ready to start on polished dashboard.
```

Update `last_updated:` field too.

---

## Back-channel (ADVISOR QUESTION protocol)

When you hit real ambiguity, draft:
```
ADVISOR QUESTION: [question here with context]
```

The user will paste it to me in the advisor tab; I'll respond; you'll get my reply.

**Expected ambiguity zones:**
- If a specific tile's inline color usage makes `--pri → cyan` look wrong (it was semantically indigo), ask: should I add `var(--univ)` override at that site, or fold into B106?
- If DM Sans causes hardcoded-width overflow anywhere, ask before widening.
- If a pill variant doesn't cleanly migrate to the unified `.pill` convention, ask before leaving it inconsistent vs forcing migration.

**Don't ask about:**
- Font file paths (spelled out above)
- Palette values (spelled out above)
- Whether to ship — you ship after browser regression passes
- Standing project conventions (CLAUDE.md)

---

## Hard rules (standing user preferences)

- **No PNG buttons.** Ever.
- **No `git add .`** — stage by filename.
- **`gh auth switch --user JGY123`** before pushing to JGY123/RR. Default is `yuda420-dev`.
- **Verify writes hit disk** after every Edit/Write.
- **Safety-tag before risky edits.**
- **Do NOT touch any tile's render function.** Pure CSS + font bundle + class sweep only. If you find yourself tempted to "just fix this one thing while I'm in there" — don't. That's B106.

---

## Emotional context

User explicitly said: "at this point I will settle to have one that is just as good" as SurpriseEdge. That's a lowered-expectations signal. B105 is the opening move to reverse that — deliver visual parity so the user sees the transformation and regains ambition.

**Bring the same level of care as SurpriseEdge was built with.** 9,200 lines of React in the reference app — the polish wasn't accidental, it was disciplined. The CSS work here is smaller but the same discipline applies.

Ship clean. I'll be in the other tab if you hit anything.

— Advisor (2026-04-24)
