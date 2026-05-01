# Design Audit: dashboard_v7.html — Visual Inconsistencies

**Scope:** Dark-themed financial control panel (~13k lines).  
**Findings:** 6 categories of drift identified across typography, spacing, borders, colors, buttons, and empty states.

---

## 1. Typography Drift

**Issue:** Font sizes scattered across 9–22px for the same semantic roles.

| Role | Sizes Found | Lines | Canonical | Effort |
|------|-------------|-------|-----------|--------|
| Card titles (`.card-title`) | 11px | 75 | 11px ✓ | S |
| KPI/sum-card values | 32px, 20px | 82 | 32px ✓ | S |
| Table headers (`th`) | 9.5px | 93 | 9.5px ✓ | S |
| Subtitle/body text | 10px, 11px, 12px, 13px | scattered | **Standardize to 11px** | M |
| Button text | 10px, 11px, 12px, 13px | 1138–1266 | **11px** | M |
| Header brand ("ALGER", "REDWOOD RISK") | 13px, 14px, 18px | 480, 487, 625 | **14px** | S |

**Examples:**
- Tile chrome buttons (`aboutBtn`, `resetViewBtn`, `hideTileBtn`, `fsTileBtn`) use `font-size:11px` (line 1138–1266) ✓
- But inline summary text varies: `font-size:10px` (line 628, 630), `font-size:13px` (line 628)
- Sum-card subtitles use `font-size:11px` (line 84) but are inconsistent with body copy

**Recommendation:** Establish 3–4 canonical sizes:
- **Hero**: 32px (KPI values)
- **Title**: 14px (card titles, headers)
- **Body**: 11px (table data, pill text, labels)
- **Meta**: 9px (timestamps, tooltips)

**Effort:** M (audit ~300 text elements, update 60–80 occurrences).

---

## 2. Spacing Drift

**Issue:** Padding values scattered; no consistent margin/gap system.

| Element | Padding Used | Lines | Canonical | Drift |
|---------|--------------|-------|-----------|-------|
| Card body (`.card`) | 18px | 73 | 18px ✓ | None |
| Sum-cards (`.sum-card`) | 16px, 18px | 77, 77 | 16px + 18px for main `.card` ✓ | None |
| Small buttons (tile chrome) | 1px 7px, 2px 7px | 1138–1266 | **Standardize to 2px 7px** | S |
| Pill buttons | 2px 8px, 4px 12px | 100, 104–106 | 4px 12px (toggle) vs 2px 8px (inline) — both valid | None |
| Table cells (`td`) | 7.5px 11px | 94 | 7.5px 11px ✓ | None |
| Modal padding | 28px | 121 | 28px ✓ | None |
| Select/input padding | 8px | 356 | 8px ✓ | None |

**Examples:**
- Tile chrome buttons vary internally: `padding:1px 7px` (aboutBtn, line 1138) vs `padding:2px 7px` (resetViewBtn, line 1171; hideTileBtn, line 1222; fsTileBtn, line 1266)
- Export button in tileChromeStrip uses `padding:3px 7px` and `padding:3px 8px` (line 1299–1300) vs `export-btn` class at `padding:3px 8px` (line 291)
- Range buttons: `padding:3px 10px` (line 404) vs pagination buttons `padding:4px 12px` (line 115) — semantically similar but different padding

**Recommendation:**
- **Tile chrome buttons:** Standardize to `padding: 2px 8px; font-size: 11px` (affects 4 button types)
- **Range/filter buttons:** Use `padding: 3px 10px` consistently
- **Pagination/secondary buttons:** Use `padding: 4px 12px` consistently

**Effort:** S (update 15–20 lines in button template definitions).

---

## 3. Border Radius Drift

**Issue:** 10 distinct radius values in use; creates visual "family" confusion.

| Value | Occurrences | Role |
|-------|-------------|------|
| 4px | 34 | Small UI (pills, chips, export buttons) |
| 5px | 10 | Tile chrome buttons (aboutBtn, etc.) |
| 6px | 51 | Primary (toggle-btn, range-btn, search) |
| 8px | 43 | Cards, modals, inputs, dropdowns |
| 10px | 8 | Larger panels (hist-panel, valid-panel) |
| 12px | 6 | Large elements (upload zone, upload-zone label) |
| 3px | 10 | Tooltip portal, heatmap, pill variants |

**Examples:**
- Tile chrome buttons use `border-radius:5px` (lines 1138, 1150, 1171, 1222, 1266) — unique value, used nowhere else
- Card is `border-radius:12px` (line 73) but sum-card is `border-radius:10px` (line 77)
- Input fields use `border-radius:6px` (line 356) but select in header uses `border-radius:8px` (line 48)

**Recommendation:** Reduce to 4 canonical sizes:
- **Tight (micro):** 4px (pills, chips, small buttons)
- **Compact:** 6px (toggle-btn, inputs, search, range buttons)
- **Standard:** 8px (cards, modals, dropdowns)
- **Relaxed (oversize):** 12px (hero elements: upload zone)
  - Keep sum-card at 10px (currently at 77) as compromise between card/hero

**Effort:** S (update 15–20 lines; most are already in CSS classes, only tile chrome buttons scattered).

---

## 4. Color Drift

**Issue:** Multiple greys for "dim text"; two greens for "positive"; hardcoded fallbacks scattered.

| Intent | Variable | Hardcoded | Mismatch |
|--------|----------|-----------|----------|
| Dim text | `--textDim` (#6b7280) | #94a3b8 (36 uses), #64748b (21 uses), #475569 (9 uses) | **High** |
| Positive | `--pos` (#10b981) | #22c55e (rank 2), #10b981 (preferred) | **Medium** |
| Negative | `--neg` (#ef4444) | Direct use (consistent) | ✓ |
| Grid/border | `--grid` (#1e2433) | #334155 (in print, forms) | Low |

**Examples:**
- Plotly chart axis labels use hardcoded `#94a3b8` (lines 3933, 5648, 5731, 5735, 5767) instead of `var(--textDim)`
- Factor rank colors defined as `--r1`–`--r5` (line 32) where `--r2` is `#22c55e` (brighter green) but `--pos` is `#10b981` — asset table uses `--r2` not `--pos` (lines 3925, 5701)
- Tooltip portal uses hardcoded `#0f1623` (line 266) instead of `var(--card)` or `var(--surf)`
- Sort indicator hover in tips uses hardcoded `#94a3b8` instead of `var(--textDim)` (line 314 comment notes this is a F3 fix)

**Recommendation:**
- **In JS Plotly code:** Replace `#94a3b8` with `getComputedStyle(document.body).getPropertyValue('--textDim')` (already done in some places; standardize to all)
- **Rank colors:** Keep `--r2` (`#22c55e`) separate — it's intentionally brighter for visual hierarchy in rank tables. Document this distinction.
- **Tooltip portal:** Change `background:#0f1623` to `var(--card)` (line 266)
- **Print styles:** Acceptable to hardcode print colors (`#000`, `#fff`, `#ddd`) per @media print block

**Effort:** M (audit Plotly chart code sections, ~10 replace operations; tooltip is 1 line).

---

## 5. Button Style Drift

**Issue:** 3+ visual treatments for "small inline action button" (tile chrome).

| Button | Padding | Font-size | Border | Line-height | Weight |
|--------|---------|-----------|--------|-------------|--------|
| **aboutBtn** | 1px 7px | 11px | 1px solid var(--grid) | 1.2 | 600 |
| **resetZoomBtn** | 2px 7px | **12px** | 1px solid var(--grid) | 1 | (default) |
| **resetViewBtn** | 2px 7px | 11px | 1px solid var(--grid) | 1 | 600 |
| **hideTileBtn** | 2px 7px | 11px | 1px solid var(--grid) | 1 | 600 |
| **fsTileBtn** | 2px 7px | 11px | 1px solid var(--grid) | 1 | 600 |
| **export-btn** (class) | 3px 8px | **10px** | 1px solid var(--grid) | (inherit) | (inherit) |
| **CSV in tileChromeStrip** | 3px 7px | **11px** | (none, .export-btn) | (inherit) | (inherit) |
| **FS in tileChromeStrip** | 3px 8px | **13px** | (none, .export-btn) | (inherit) | (inherit) |

**Lines:** 1138–1266, 1299–1300, 291–292

**Examples:**
- `aboutBtn` has `line-height:1.2` (outlier) and `font-weight:600` but `resetZoomBtn` omits weight
- `resetZoomBtn` uses `font-size:12px` (not 11px like the others)
- CSV/FS buttons in `tileChromeStrip` use `.export-btn` class (padding: 3px 8px, font-size: 10px) but then inline override to 11px and 13px respectively
- One-off icon buttons in header use inconsistent styles: `stepWeek` arrows are `font-size:14px; padding:0 4px` (line 524–526) while `latestBtn` is `font-size:10px; padding:2px 7px` (line 527)

**Recommendation:**
- **Unified tile chrome style:**
  - padding: `2px 8px`
  - font-size: `11px`
  - font-weight: `600` (for clarity)
  - line-height: `1`
  - Applies to: aboutBtn, resetZoomBtn, resetViewBtn, hideTileBtn, fsTileBtn, and inline CSV/FS buttons
- **Export/secondary buttons:** Use `.export-btn` class without inline overrides (`padding:3px 8px; font-size:10px`)
- **Icon buttons in header:** Create a `.icon-btn` mixin (padding: 0 4px; font-size: 14px) for step controls

**Effort:** M (update 5–7 button template functions + review 15–20 inline overrides in tileChromeStrip).

---

## 6. Empty-State Drift

**Issue:** Inconsistent "no data" treatments across tiles.

| Tile | Empty Treatment | Line | Style |
|------|-----------------|------|-------|
| **Week over Week** | `.wow-empty` div, centered text | 233, 2516 | padding: 30px; font-size: 12px; color: var(--textDim) |
| **Week over Week (hist)** | `.wow-empty`, 18px 0 padding | 2533 | padding: 18px 0; font-size: 11px; (custom inline) |
| **Factor Impact (no data)** | Inline `<p>` | 3111 | font-size: 12px; padding: 40px; centered |
| **Factor table** | Inline `<p>` | 4421, 4426 | font-size: 12px; color: var(--txt) |
| **Risk indicators (empty)** | Implicit (renders "—" dashes) | scattered | (no explicit empty state) |

**Examples:**
- `.wow-empty` class defines `padding:30px` but one usage overrides with `style="padding:18px 0"` (line 2533)
- Factor "No data" uses both `.wow-empty` (consistent) and inline `<p>` (inconsistent font-size, padding)
- Some tiles show "—" when empty (line 4870) without a visual empty-state container (silent failure vs visible feedback)

**Recommendation:**
- **Canonical empty-state class:**
  ```css
  .empty-state {
    padding: 32px 24px;
    text-align: center;
    color: var(--textDim);
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.3px;
  }
  ```
- Use `.empty-state` in all tiles; remove per-tile `.wow-empty`
- Add icon/graphic (e.g., database icon 🔲, "No data" label) above text for visual hierarchy
- Tile code should wrap empty state in a container with min-height to prevent layout shift

**Effort:** S (1 new CSS class, audit ~8 tiles for consistent rendering, update 6–10 HTML templates).

---

## Summary: Effort Estimate

| Category | Effort | Priority | Lines Affected |
|----------|--------|----------|-----------------|
| Typography | M | High | 60–80 |
| Spacing | S | High | 15–20 |
| Border Radius | S | Medium | 15–20 |
| Colors | M | High | 30–40 (mostly JS Plotly code) |
| Buttons | M | High | 40–60 (5 template functions + overrides) |
| Empty States | S | Low | 10–15 |

**Total Effort:** ~2–3 days (S: 2–3 hours; M: 8–12 hours each = 2–3 days serial)  
**Recommended Order:**
1. **Colors** (highest impact on visual cohesion, mostly mechanical regex substitution)
2. **Buttons** (affects 30+ instances, affects first impression of chrome)
3. **Typography** (largest diff count, but safe to batch)
4. **Spacing** (builds on button fixes)
5. **Border Radius** (polish layer)
6. **Empty States** (UX polish, lowest impact)

---

## Notes

- **CSS custom properties are well-defined** (`:root` at lines 22–33). The drift is almost entirely in inline styles and JavaScript Plotly code.
- **Print styles** (line 172–435) deliberately hardcode colors — keep as-is.
- **Light theme** (line 440–446) correctly redefines CSS vars for contrast — no changes needed.
- **Tile chrome framework** (`tileChromeStrip`, lines 1293–1305) is the right place to enforce button consistency; all 5 button types should route through it.
