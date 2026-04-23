# cardUnowned — Tile Audit (2026-04-23)

**Tile:** Unowned Risk Contributors (Exposures tab, Row 10)
**Card id:** `#cardUnowned` at dashboard_v7.html:1292
**Renderer:** `rUnowned(s.unowned)` at L1991–1996
**Drill:** `oDrUnowned(ticker)` at L5461–5479
**Data source:** `s.unowned` — populated by `factset_parser.py:_extract_security` L577–644 (holdings with `w`/`bw`/`aw` all null), passed through at L840

---

## Verdicts

| Track | Verdict | Headline |
|---|---|---|
| **T1 Data accuracy** | **RED** | Every displayed numeric field (`u.b`, `u.tr`) is null in 100% of rows across all 7 strategies. Entire tile renders `—` for both numeric columns. Parser's "unowned" bucket is defined as *holdings with no weight data* — by construction those rows cannot carry a benchmark weight or TE contribution. |
| **T2 Functionality parity** | **YELLOW** | No notes hook on card-title; no `data-col`; table renders but sort on Bench Wt / TE Contrib is meaningless when all values null; drill modal missing `oncontextmenu` note hook; XSS risk in ticker string-interpolation for drill onclick. |
| **T3 Design consistency** | **YELLOW** | Hardcoded `color:var(--neg)` on TE column regardless of sign; header tooltips missing on 4 of 5 columns; raw FactSet region strings (`'Usa'`, `'English'`) leak into user-facing display; no `class="tip" data-tip` on numeric headers. |

---

## T1 — Data Accuracy (RED)

Data probe vs `/Users/ygoodman/RR/latest_data.json` (all 7 strategies):

| Strategy | Unowned rows | `bw` populated | `pct_t` populated | `reg` populated |
|---|---|---|---|---|
| ACWI | 1 | 0 | 0 | 1 |
| IOP | 1 | 0 | 0 | 1 |
| EM | 0 | — | — | — |
| GSC | 13 | 0 | 0 | 13 |
| IDM | 1 | 0 | 0 | 1 |
| ISC | 6 | 0 | 0 | 6 |
| SCG | 0 | — | — | — |

**Every row has `bw=None`, `pct_t=None`, `pct_s=None`, `w=None`, `aw=None`, `t_check=None`.** Only populated fields: `t`, `n`, `sec` (sometimes null), `reg`, and ORVQ ranks (`over`/`rev`/`val`/`qual`/`mom`/`stab`, sometimes populated).

### Findings

**T1.1** — **Tile is structurally unable to show what its title promises.** Parser `_extract_security` L639 puts a security into the `unowned` bucket iff `w`, `bw`, `aw` are ALL None (`if h.get("w") is None and h.get("bw") is None and h.get("aw") is None`). In other words: the bucket *requires* bench weight to be null to land here. The tile then reads `u.b` (mapped from `bw` via normalize L567) and `u.tr` (from `pct_t` via L570) — both guaranteed null by construction. Render displays `—` for every numeric cell. Card title claim "stocks that contribute most to tracking error" is a promise the data cannot keep.

→ **[PM gate]** The canonical "FactSet unowned-benchmark constituents" feed is a different section of the CSV (likely the 18 Style Snapshot benchmark-only stream, or a dedicated unowned-risk section not currently parsed). The current `unowned` bucket is actually *orphan securities the parser couldn't attribute to a weight category* — e.g. "Worldline Cash", "Great Eagle (Detached 2)", rights/warrants (`BTRT1D` = "Worldline SA Rights 2026-27.03.2026"). Either:
- (A) hide the tile entirely until a real unowned-risk source is wired (parser change), or
- (B) rename the tile to "Orphan / unattributed benchmark rows" and drop the TE/weight columns it can't populate, or
- (C) treat as BACKLOG pending a FactSet feed question.

This is the single biggest finding in the audit. New backlog item: **B79 — Unowned Risk Contributors tile has no data source.**

**T1.2** — **Pattern B (parser-populated → normalize-mapped → still null):** normalize L568–L570 maps `hn.b ?? hn.bw ?? 0` and `hn.tr ?? hn.pct_t ?? 0` for holdings, but at L562 creates `st.unowned=[]` and never touches `st.unowned` rows. So unowned rows still carry `bw`/`pct_t` key names (not `b`/`tr`), yet render reads `u.b` and `u.tr`. Confirmed from data probe: `u.b` and `u.tr` are **undefined** (the keys don't even exist on the unowned row objects — they carry `bw`/`pct_t`/`aw`/`pct_s` verbatim from the parser). `f2(undefined)` → `'—'`, `fp(undefined)` → `'—'`, `${undefined}` in `data-sv` renders literal `"undefined"`.

→ **[trivial]** If a future fix populates `bw`/`pct_t` on unowned, normalize should mirror the holdings mapping for unowned: apply the same `hn.b = hn.b ?? hn.bw` transform to every `st.unowned` row. Current mismatch makes the tile non-functional even if parser later fills values. (2-line patch at L562.)

**T1.3** — Region display leaks raw FactSet region strings: `'Usa'`, `'English'` (UK), `'Far East'`, `'Western Europe'`. These don't match the normalized region labels used in cardRegions (which go through CMAP). User-facing "English" for UK-listed stocks is confusing.

→ **[trivial]** Apply the same `CMAP[u.co]||u.reg||'Other'` normalization for unowned, OR a simple `REG_LABEL_FIX = {'Usa':'USA','English':'UK/English'}` passthrough at render time.

**T1.4** — Sort spec uses `Math.abs(b.tr)-Math.abs(a.tr)` with no null guard at L1993. `Math.abs(undefined)` → `NaN`, sort becomes non-deterministic across browsers (V8 stable-sorts NaN comparisons to identity, so rows stay in insertion order — fine today, but fragile).

→ **[trivial]** `.sort((a,b)=>Math.abs(b.tr||0)-Math.abs(a.tr||0))` — one-liner.

**T1.5** — Empty-state fallback exists (L1992) and fires correctly for EM + SCG. Good. But when `unowned.length===1` (ACWI/IOP/IDM, all three have the single orphan `BMC4ZZ "JDE Peet's NV"` — a rights/cash line misclassified), the tile renders a one-row table of meaningless data. Threshold for useful display is probably `≥3` rows *with populated weights*; with current data the threshold is never met.

→ **[PM gate]** Part of the B79 decision.

---

## T2 — Functionality Parity (YELLOW)

Primitives checklist against gold-standard cardSectors/cardHoldings:

| Primitive | Status |
|---|---|
| `<table id="tbl-unowned">` | ✅ L1995 |
| Every `<th>` wired to `sortTbl` | ✅ all 5 cols |
| Numeric cells carry `data-sv` | ⚠️ Yes, but `data-sv="${undefined}"` renders `"undefined"` (see T1.2) — sort works via textContent fallback |
| `data-col="..."` on every th/td | ❌ **missing entirely** — blocks any future column-picker |
| Rows `class="clickable"` + drill | ✅ L1994 |
| Empty-state fallback | ✅ L1992 |
| CSV export (no PNG) | ✅ L1294 |
| Card-title tooltip (`class="tip" data-tip`) | ✅ L1293 |
| Card-title note hook (`oncontextmenu="showNotePopup(event,'cardUnowned')"`) | ❌ **missing** — every sibling tile with note-hook support has it |
| Full-screen (⛶) button | ❌ missing (probably unnecessary — short table) |

### Findings

**T2.1** — **No note-hook on card-title.** cardUnowned card-title at L1293 has `class="tip" data-tip="..."` but lacks `oncontextmenu="showNotePopup(event,'cardUnowned');return false"`. Users cannot attach notes to this tile. sibling tiles cardMCR (L1280), cardFRB (L1285), cardAttrib (L1307), cardGroups, cardChars, cardThisWeek, cardRiskFacTbl all have this hook.
→ **[trivial]** Add `oncontextmenu="showNotePopup(event,'cardUnowned');return false"` to L1293 card-title.

**T2.2** — **No `data-col` on any th or td.** Same gap noted cross-tile for cardRegions and cardGroups. Five columns (ticker/name/region/b/tr) all unaddressable by the column-picker infra that hooks via `[data-col="..."]` (e.g. L1489 `document.querySelectorAll('#tbl-sec [data-col="..."]')`).
→ **[trivial]** Add `data-col="t|n|reg|bw|tr"` to each th and td pair at L1994–1995.

**T2.3** — **Drill modal missing note-hook.** `oDrUnowned` modal h2 at L5468 has no `oncontextmenu`; every sibling modal's `h2` also lacks this (cross-tile observation; not new). Deferred — consistent at least.

**T2.4** — **XSS/quoting risk in drill invocation.** `onclick="oDrUnowned('${u.t}')"` at L1994 fails for tickers containing `'` (seen in GSC: `*NGD`, `*TCL.A`, `BCRX1J` — none contain `'` today, but `BMC4ZZ` "JDE Peet's NV" shows apostrophes can appear in *names*; `t` field is an opaque FactSet security ID and could carry unusual chars). Also, `u.n` is injected into text cells unescaped via backticks — for a benchmark-sourced name field this is defended-in-depth only, but "JDE Peet's NV" already appears as `Peet&#39;s` naturally on the page. Not exploitable today; audit flag for future.
→ **[trivial]** Use `onclick="oDrUnowned('${(u.t||'').replace(/'/g,\"\\\\'\")}'"` OR switch to `data-t="${u.t}"` + delegated click — same pattern recommended for cardHoldings rows.

**T2.5** — **Sort on `TE Contrib` column (idx 4) defaults to `sortTbl` numeric-sort via `data-sv`; with `data-sv="undefined"` literal, `parseFloat('undefined')→NaN` → sort silently becomes no-op / insertion-order.** Same for `Bench Wt%` (idx 3). Sort UX is dead in current data.
→ **[trivial]** `data-sv="${u.b??''}"`, `data-sv="${u.tr??''}"` — blocks anti-pattern called out in AUDIT_LEARNINGS sort section (nullish-coalesce to empty string, not 0).

**T2.6** — **Drill's "Your Holdings in ${u.reg}" filter works** — both `unowned[].reg` and `hold[].reg` use the same raw FactSet region vocabulary (verified — no CMAP mismatch in this path). But the user-visible region label in both the tile and modal header is FactSet-raw (`'Usa'`, `'English'`) — see T1.3.

**T2.7** — Drill modal body L5475 hardcodes text `"This stock has a ${f2(u.b)}% weight in the benchmark..."` — which renders as **"This stock has a — % weight in the benchmark but is not held in the portfolio. Its absence contributes — to tracking error."** on every open with current data. Narrative is nonsense.
→ **[PM gate]** Same root cause as T1.1. Block narrative until data available, OR add a guard: `${isFinite(u.b) ? '...' : 'No weight data available for this security.'}`.

**T2.8** — No `ticker→oSt` link on drill modal's "Your Holdings" table rows (L5477). Sibling drills (`oDrGroup` L5492, `oDrCountry`) wire `oSt(h.t)` on each row to cross-navigate. Minor parity gap.
→ **[trivial]** Wire `class="clickable" onclick="$('unownedModal').classList.remove('show');oSt('${h.t}')"` on each `<tr>` at L5477.

---

## T3 — Design Consistency (YELLOW)

### Findings

**T3.1** — **Hardcoded `color:var(--neg)` on TE Contrib cell regardless of sign.** L1994: `<td class="r" data-sv="${u.tr}" style="color:var(--neg);font-weight:600">${fp(u.tr)}</td>`. TE contribution can in principle be positive or negative (negative = diversifier — rare for benchmark-unowned but conceptually possible). Always red implies "this is bad", conflating the *role* of unowned risk (TE source) with the *sign*. Compare to sibling sign-collapse findings in cardFRB / cardRiskFacTbl (AUDIT_LEARNINGS L195-201, B74).
→ **[trivial]** `style="color:${(u.tr||0)>=0?'var(--neg)':'var(--pos)'};font-weight:600"` — OR unconditional `color:var(--txth)` if the tile's semantic is "magnitude of absence" rather than "direction". PM gate on which semantic wins — same family as B74.

**T3.2** — **Header tooltips missing on 4 of 5 columns.** Only card-title has `class="tip" data-tip` (L1293). Numeric cols "Bench Wt%" + "TE Contrib" badly need `data-tip` explaining "% of benchmark this stock represents" and "% of tracking error this absence contributes" — per sibling convention (cardSectors headers have `tip data-tip` on every numeric col).
→ **[trivial]** Add `class="tip" data-tip="..."` to each `<th>` at L1995.

**T3.3** — **Raw FactSet region strings in UI** (T1.3). `'Usa'` (not "USA"), `'English'` (meaning UK-listed, confusing to a risk PM), `'Far East'` (dated geography term vs "Asia Pacific ex-Japan" norm). Cross-tile: cardRegions normalizes via CMAP; cardUnowned does not.
→ **[trivial]** One-line lookup table or reuse of CMAP normalization at render-time.

**T3.4** — **Table lacks threshold shading / semantic cells.** Unlike cardSectors (`thresh-alert`/`thresh-warn` on `|a|>5`/`>3`), the unowned table has no visual gradient on TE Contrib even though that column is the entire reason-to-care-about this tile. For rows where `|tr|>2%` (a plausible "material TE absence" threshold), a row class would help prioritization.
→ **[PM gate]** Threshold for "material unowned-TE" — 1%? 2%? `_thresholds.intentionalFactorSigma` style entry? Deferred until T1.1 source issue is resolved.

**T3.5** — `<td>${u.n}</td>` (Name column) has no styling, no `data-sv`, no truncation. Long names like `"Worldline SA Rights 2026-27.03.2026"` and `"Great Lakes Dredge & Dock Corporation"` expand the column.
→ **[trivial]** Add `data-sv="${(u.n||'').toLowerCase()}"` for case-insensitive sort + CSS `max-width:260px;overflow:hidden;text-overflow:ellipsis` + `title="${u.n}"` for hover-reveal. Same pattern as cardHoldings.

**T3.6** — **Card-title tip copy at L1293 is aspirational, not descriptive.** "Benchmark stocks not held that contribute most to tracking error. Click for detail." — but (a) the table is not click-to-open (row clicks are), and (b) with current data no row shows any TE contribution. Minor.
→ **[trivial]** Once T1.1 is resolved, keep this copy. If T1.1 → "hide tile" or "rename", copy changes with it.

**T3.7** — **Font size / density consistent** with sibling tables (inherits global `th`=10px, `td`=11px via default table CSS). ✅

---

## Cross-tile learnings to append to AUDIT_LEARNINGS.md

1. **Pattern B variant: normalize() skips unowned rows.** normalize L562–L570 remaps field names (`w`→`p`, `bw`→`b`, `pct_t`→`tr`) for `st.hold` rows only; `st.unowned` rows retain parser's original `bw`/`pct_t` keys. Render reads normalized names and silently gets `undefined`. Every downstream tile reading `s.unowned[].b` / `s.unowned[].tr` will be broken in the same way. Any future tile that branches on "is this a held or unowned security" should apply the same field-name remap to both collections.

2. **Parser bucket semantics ≠ tile semantics.** `_extract_security` partitions by "has the security any weight data in this CSV row". That is not the same as "security is in benchmark but not in portfolio". A row with `w=0, bw=0.5, aw=-0.5` would go into `holdings`; a row with `w=None, bw=None, aw=None` goes into `unowned` — and is by definition weight-less. Treating the parser's `unowned` bucket as a "benchmark-unowned-constituents" feed is the mismatch. Audit heuristic: whenever a parser bucket is named aspirationally (`unowned`, `orphan`, `benchmark-only`), read the PARTITION CONDITION, not the name.

3. **Fourth sign-collapse site candidate.** `color:var(--neg)` on TE Contrib in cardUnowned L1994 is a static sign-collapse (always red). Not a `Math.abs` instance but the same anti-pattern class from B74.

---

## Fix queue

### Trivial (agent-applyable, zero PM gate)
1. Add `oncontextmenu="showNotePopup(event,'cardUnowned');return false"` to card-title L1293.
2. Add `data-col="t|n|reg|bw|tr"` to each `<th>` + `<td>` pair L1994–1995.
3. `data-sv="${u.b??''}"`, `data-sv="${u.tr??''}"` — nullish-coalesce to empty string (AUDIT_LEARNINGS sort anti-pattern).
4. Sort guard: `.sort((a,b)=>Math.abs(b.tr||0)-Math.abs(a.tr||0))` at L1993.
5. Ticker escaping in drill invocation: `onclick="oDrUnowned('${(u.t||'').replace(/'/g,\"\\\\'\")}')"`.
6. Sign-colored TE cell: `color:${(u.tr||0)>=0?'var(--neg)':'var(--pos)'}` — OR neutral `var(--txth)` pending PM pick.
7. Header tooltips: `<th class="tip" data-tip="..." onclick="...">` on Bench Wt% and TE Contrib columns.
8. Region label normalization: map `'Usa'→'USA'`, `'English'→'UK/English'` at render-time.
9. Wire `oSt` on drill modal's "Your Holdings" rows at L5477 for ticker cross-nav.
10. Name cell: `data-sv="${(u.n||'').toLowerCase()}"` + truncation CSS + hover title.
11. Normalize `st.unowned` rows to carry `b`/`tr` fields (mirror L564–L573 mapping for unowned rows).

### PM gate
12. **B79 — Source-of-truth for "Unowned Risk Contributors".** Current `s.unowned` is the parser's orphan-row catch-all, not a benchmark-unowned-TE feed. Options: (A) parser change to extract from a different CSV section / FactSet query; (B) hide tile until source is wired; (C) rename tile to reflect what the data actually is ("Unattributed Benchmark Rows"). **Blocks T1.1, T2.7, T3.4, T3.6.**
13. **Drill modal narrative block.** "This stock has a — % weight..." is user-facing nonsense on current data. Guard with `isFinite(u.b)` once source is picked.
14. **Threshold for "material unowned TE" shading.** Deferred until B79.
15. **Sign semantic on TE column** (T3.1) — absolute-magnitude (always red, CSV-sortable by |tr|) vs signed (rare case of diversifying unowned). Same family as B74 sign-collapse decision.

### Backlog (cross-tile / parser-dependent)
16. **B79** (new) — Unowned Risk Contributors has no data source. Parser change or tile removal. Single largest blocker from this audit.

---

## Audit metadata

- Data probe: `/Users/ygoodman/RR/latest_data.json` — all 7 strategies checked.
- Code refs: dashboard_v7.html L1292–1296 (shell), L1991–1996 (renderer), L5461–5479 (drill), L562–L573 (normalize), L6582–6584 (v2 normalize). factset_parser.py L577–644 (source bucket), L840.
- Learnings to propagate: Pattern B variant (normalize skips unowned), parser bucket semantics ≠ tile semantics, 4th sign-collapse candidate site.
- No edits to dashboard_v7.html — main session serializes.
