# Tile Audit — cardBenchOnlySec (2026-04-23)

**Render fn:** `benchOnlySecHtml(s)` at dashboard_v7.html L1946–1989
**Card id:** `#cardBenchOnlySec` (L1979)
**Table id:** `#tbl-bo-sec` (L1982)
**Invoked from:** L1154 (Overview tab, directly after cardSectors)
**Empty-state:** returns `''` → parent template renders nothing (self-hiding card). L1947 (no holdings) and L1962 (no bench-only rows).

## Verdict

| Track | Color | Headline |
|---|---|---|
| T1 Data accuracy | **GREEN** | Field lookups correct; one minor ambiguity in "% of benchmark missed" denominator. |
| T2 Functionality parity | **YELLOW** | Missing right-click note hook; stray PNG button (user policy violation); incomplete `data-col`; sort on "Biggest Missed" broken. |
| T3 Design consistency | **GREEN** | Themed vars throughout; one hardcoded-color check passes; no ghost-tile / anon-id issues. |

---

## T1 — Data accuracy

### T1.1 Field lookups and aggregation — GREEN
- Bench-only filter at L1953: `(h.b||0)>0 && (!h.p||h.p<=0)`. Correct semantic (benchmark weight > 0, portfolio weight nil/non-positive). Same predicate used by `oDr` drill sibling at L4117 — no drift across the two sites.
- Per-sector aggregation (L1955–1959): `count++`, `wt += h.b`, `biggest = argmax(h.b)`. Straightforward; no weighted-rank traps (this tile doesn't compute ranks, so the `h.p>0?h.p:1` fallback pattern per AUDIT_LEARNINGS "Aggregation quirks" does not apply).
- Cash exclusion via shared `isCash(h)` (L1950 → L499). Consistent with sibling tiles.
- `h.sec` missing-guard at L1951 (`if(!h.sec)return;`) — silently drops bench-only holdings without a sector assignment. Possible under-count if FactSet ever ships `h.sec === null` on a real equity. Low-risk given per-holdings sector is reliably populated today.
- No parser Pattern A/B/C dependency — this tile reads `s.hold[]` directly; nothing goes through `hist.X` or gets re-derived from a local taxonomy config. Safe.

### T1.2 "% of benchmark missed" denominator is ambiguous — YELLOW (header-text only)
- L1980 title suffix: `${f2(totalMissed,1)}% of benchmark missed`. `totalMissed` (L1965) = Σ `h.b` for bench-only holdings. That is **percent of total benchmark weight** we don't own, NOT a share of any subset. Reads like it could mean "% of benchmark sectors missed" or "% of benchmark TE missed" — both wrong.
- Sibling `cardUnowned` shows TE-contribution; this tile shows bench-weight-gap. Worth disambiguating. Suggest: `${f2(totalMissed,1)}% bench wt not held`.
- `[PM gate]` — label change, PM sign-off.

### T1.3 Drill target exists and matches semantic — GREEN
- Row click (L1972) → `oDr('sec', <sectorName>)` → L4093–4117 loads sector holdings AND renders a bench-only subsection within the drill. Functional round-trip. `cs.hist.sec[name]` drives the trend chart, but per AUDIT_LEARNINGS "Known blockers", `hist.sec` is parser-empty (`factset_parser.py:837 "sec": {}`) — the drill's history chart silently falls through. This is a known cross-tile backlog item (B6), not a cardBenchOnlySec-specific finding.

---

## T2 — Functionality parity

### T2.1 Missing right-click note hook on card-title — YELLOW [trivial]
L1980 card-title has `class="card-title tip" data-tip="..."` but no `oncontextmenu="showNotePopup(event,'cardBenchOnlySec');return false"`. Note-badge *display* auto-attaches via `refreshCardNoteBadges` L3646 (matches `[id^="card"]`), but users can't create a new note — the contextmenu hook is the only create path.
Proposed fix (L1980):
```html
<div class="card-title tip" data-tip="..." oncontextmenu="showNotePopup(event,'cardBenchOnlySec');return false">Benchmark-Only Holdings by Sector ...
```

### T2.2 PNG button violates user policy — RED [trivial]
L1981: `<button class="export-btn" onclick="screenshotCard('#cardBenchOnlySec')">PNG</button>`. Per MEMORY.md `feedback_no_png_buttons.md` and AUDIT_LEARNINGS primitives checklist, user has removed PNG buttons multiple times. Keep CSV only.
Proposed fix: delete the PNG button; keep `<button class="export-btn" onclick="exportCSV('#tbl-bo-sec','bench_only_sec')">CSV</button>` (drop the `style="margin-left:4px"` once PNG is gone).

### T2.3 Missing `data-col` on every `<th>`/`<td>` — YELLOW [trivial]
Per AUDIT_LEARNINGS primitives checklist: every th+td should carry a stable `data-col` for any future column-picker. None present here (L1982–1987 ths, L1973–1976 tds). Proposed cols: `sec`, `missed`, `wt`, `biggest`. Same retrofit already flagged on cardRegions; batch this with that sweep.

### T2.4 "Biggest Missed" column sort is broken — YELLOW [trivial]
L1986 `<th>Biggest Missed</th>` — no `onclick="sortTbl(...)"` (intentional? user-facing still clickable-looking because no visual cue distinguishes sortable vs not). More importantly, if a future sweep adds `sortTbl('tbl-bo-sec',3)`, the cell HTML at L1976 is `${shortNm(big.n||big.t)} <span>(${f2(big.b,2)}%)</span>` — `textContent` parse falls through to mixed string; no `data-sv`. Sort would be alphabetic-with-garbage.
Fix options:
- (a) Leave non-sortable (current state) — add a tiny `cursor:default` + remove the `th` hover effect.
- (b) Add `data-sv="${big?.b??''}"` at L1976 and wire `sortTbl('tbl-bo-sec',3)` in the th. Sort by biggest-missed-weight desc is plausibly useful.
- Prefer (b); `[trivial]`.

### T2.5 Numeric cells use `data-sv="${d.wt}"` — GREEN
L1974–1975: `data-sv="${d.count}"` and `data-sv="${d.wt}"`. Both always numeric (`count` is an integer, `d.wt` accumulated from `h.b||0` so never null). No `??0` / `??''` nullability trap per AUDIT_LEARNINGS "Sort anti-patterns" — safe.

### T2.6 Empty-state: self-hiding — GREEN
L1947 (no holdings → `''`) and L1962 (no bench-only entries → `''`) both return empty string; parent template `${benchOnlySecHtml(s)}` at L1154 renders nothing. Intentional "hide when irrelevant" pattern, different from `<p>No X data</p>` convention used by other tables. Acceptable for an opportunistic insight card — no empty-state shell needed.

### T2.7 Row drill parity with sibling tiles — GREEN
Click → `oDr('sec', name)` matches cardSectors' row drill. Same modal opens. No divergence.

### T2.8 CSV export works — GREEN
L1981 `exportCSV('#tbl-bo-sec','bench_only_sec')` — stable table id, stable filename. CSV will capture Sector, Missed (count), Bench Wt, Biggest Missed (rendered HTML — that last col will contain the span markup in text form). Minor CSV polish: the Biggest cell would export as `"NVIDIA (0.85%)"` with the span stripped, acceptable.

---

## T3 — Design consistency

### T3.1 Theme tokens — GREEN
- L1970 `color:var(--txt)` — themed
- L1974 `color:var(--txth)` — themed
- L1975 `color:var(--warn)` — themed (semantic: amber/warning — correct for "missed weight")
- L1976 `color:var(--txth)`
- L1980 `color:var(--txt)` on the suffix
- No hardcoded hex in the render fn.

### T3.2 Header tooltips — GREEN
- Two `class="tip" data-tip="..."` on numeric headers (L1984–1985). "Sector" header (L1983) and "Biggest Missed" header (L1986) lack tooltips — arguably the meaning is self-evident from the column names, but if the tooltip sweep (`cardRegions` learnings) ever lands, add one-liners.
- `[trivial]` — Biggest Missed: `data-tip="Largest single benchmark holding we don't own in this sector (by bench weight)"`. Sector: skip (no value).

### T3.3 Row shading — GREEN
No threshold-based `thresh-alert` / `thresh-warn` classes used here. Semantically this table is "gaps we don't own" — every row is a gap, so uniform-weight rendering is correct (no relative severity axis). The `--warn` color on the weight cell (L1975) is the single semantic cue — clean.

### T3.4 Density — GREEN
No inline `font-size:` / `padding:` overrides on `th`/`td`. Relies on global table CSS. Passes the "density floor" check from AUDIT_LEARNINGS.

### T3.5 Ghost-tile / anon-id check — GREEN
`#cardBenchOnlySec` has a dedicated id, renders its own content, lives on the Overview tab (not Risk tab). Not a ghost-tile pattern. Not affected by B78 (anonymous Risk-tab cards).

### T3.6 `card-title` suffix styling — GREEN
L1980 inline `font-size:10px;color:var(--txt);font-weight:400;margin-left:8px` on the count+pct suffix. Matches sibling pattern used by cardSectors / cardHoldings subtitles — consistent.

---

## Cross-tile observations (append candidates for AUDIT_LEARNINGS)

- **PNG-button sweep is incomplete.** `cardBenchOnlySec` L1981 still has one; `cardRegions` L1331 flagged earlier. Worth a single grep-sweep commit: `grep -n 'screenshotCard\|Download PNG' dashboard_v7.html` and remove all matches not already removed. Quantify before landing.
- **Label ambiguity on "% of benchmark missed"** is a variant of the "% of TE vs % of factor risk" issue flagged in AUDIT_LEARNINGS "Factor-family patterns" — denominator of any summary percentage must be explicit in the label. Consider adding a one-liner to the learnings under "Domain-term labeling errors".
- Tile sits on Overview tab; it is NOT a Risk-tab anonymous card (B78 does not apply).

---

## Fix queue

### `[trivial]` — safe to apply inline (6 items)
1. **T2.1** Add `oncontextmenu="showNotePopup(event,'cardBenchOnlySec');return false"` to card-title (L1980).
2. **T2.2** Remove PNG button (L1981) per user policy. Drop trailing `style="margin-left:4px"` on CSV button.
3. **T2.3** Add `data-col="sec|missed|wt|biggest"` to 4 ths (L1983–1986) and matching tds (L1973–1976).
4. **T2.4** Wire sort on Biggest Missed col: add `onclick="sortTbl('tbl-bo-sec',3)"` to L1986 th, add `data-sv="${big?.b??''}"` to L1976 td.
5. **T3.2** Add `class="tip" data-tip="Largest single benchmark holding we don't own in this sector (by bench weight)"` to L1986 th.
6. **T3.2** Also sort-enable Sector header if not already (re-verify — L1983 already has `onclick="sortTbl('tbl-bo-sec',0)"`, confirmed).

### `[PM gate]` — defer to review marathon (1 item)
1. **T1.2** Rename the suffix `% of benchmark missed` → `% bench wt not held`. Label change, touches narrative — PM sign-off.

### Non-trivial / backlog
- None tile-specific. Dependency on B6 (`hist.sec:{}` parser gap) affects the drill history chart but not this tile's render.

---

## Verification checklist

- [x] Data accuracy: bench-only predicate and aggregation match the `oDr` sibling path.
- [x] Empty states: no-holdings + no-bench-only both return `''` (self-hide).
- [x] Sort works on cols 0–2 (via data-sv); col 3 broken (T2.4).
- [x] CSV export: stable id, stable filename, captures all rows.
- [x] Row click drill: `oDr('sec', n)` opens sector modal.
- [x] Themes: no hardcoded hex; `--warn` semantically correct.
- [ ] Right-click note create: **broken** — missing `oncontextmenu` (T2.1).
- [x] No console errors on empty-bench-only strategies (self-hides cleanly).
- [x] Not a ghost tile; not an anonymous Risk-tab card.

---

## Summary

Small, well-scoped insight tile. Data track is clean — no parser-pipeline traps, no half-built pipelines, no sign-collapse / active-vs-raw risks (doesn't touch factors). Functionality track has a cluster of 5 trivial primitives hygiene issues (PNG button to remove, note-hook missing, incomplete `data-col`, broken sort on col 3) that mirror findings across other batches. Design track is effectively clean.

**Recommendation:** batch the 6 trivial fixes with the next cross-tile primitives sweep (especially the PNG-button-removal + `data-col` backfill already queued for cardRegions). Single PM decision pending on the "% bench wt" label rename.
