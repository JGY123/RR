# RR Changelog

Visible from the dashboard footer. Most recent first. Format: `- YYYY-MM-DD — short description (commit)`.

## 2026-04-30

- Header polish: REDWOOD wordmark expanded to "REDWOOD RISK · Control Panel" two-line lockup; new page footer at bottom with changelog + repo links + live status dot. (cb3b245)
- NEW_TILE_CANDIDATES.md: 10 new-tile ideas ranked by PM impact ÷ effort, plus 8 honorable mentions and a recommended 5-tile build order for Phase 2-3. (2052367)
- About-popup framework: ⓘ button in tile headers opens a What/How/Source/Caveats/Related modal. _ABOUT_REG covers all 25 major tiles. Trust-layer surface for PMs to check provenance without reading code. (05e9a7d, 437ff5a)
- cardChars audit RED → GREEN: drill modal now plots history for TE/Beta/Active Share (was dead-end "no historical data"); 39 metrics grouped by Risk/Valuation/Quality/Growth/Revisions/Size; per-row tooltips; unit-aware formatters (P/E "18.3x", Mcap "$4.2B", ROE "x.x%"); inverted color semantics for "lower-is-better" valuation/leverage rows; cardFacRisk-pattern header. (11a5c7e)
- cardScatter SEV-1 fix: holdings with null Spotlight rank were rendering Q5-red (~23% of GSC sample); now neutral grey. Title rebrand "MCR vs TE Contribution" → "Stock-Specific TE vs Total TE Contribution". (05e9a7d)
- Parser: support new Raw Factors layout (group_size=23) with merged mcap/adv/spotlight ranks via SEDOL match. Verifier 17/4/2 GREEN-LIGHT WITH NOTES on GSC quick sample, full GREEN on 1-year sample. (30f83b4, ec7c0f7)
- Holdings tab: ticker display now shows TKR-REGION (e.g., SIMO-US, WIE-AT) instead of SEDOL when the merge succeeds — falls back to SEDOL otherwise. (5e7e1b6, 6f1abb1)
- Risk tab summary cards: responsive grid (auto-fit) so values render fully on narrow viewports. (fbe86d1)
- INQUISITOR_DECISIONS_2026-04-30.md captured: 135 questions answered, 10-item action queue prioritized. (a0107a1)
- MIGRATION_PLAN.md drafted: end-to-end runbook for GSC validation → professional environment → multi-account massive run.
- Holdings tab: "Top-10 TE" concentration pill in title showing what share of total |TE contribution| the top 10 holdings drive.
- Drill modals: keyboard navigation — Esc closes, ↑/↓ navigates rows, Enter activates focused row.

## 2026-04-29

- Factor section split into Snapshot + Performance tiles (cardFacRisk + cardFacButt). Snapshot is point-in-time; Performance is period-aware (3M default) with view toggle (Bubble / Waterfall) and period chips.
- Performance Map quadrant: avg active exposure (x) × period impact (y), sized by avg risk contribution. Period-coherent — 3M impact pairs with 3M avg exposure.
- Factor pie redesign: side legend with three clearly-labeled ratios (% Fac, % TE, σ active).
- σ symbol fix in column headers — was rendering as Σ (summation operator) due to CSS uppercase transform.
- Removed redundant cardFRB tile (replaced by Snapshot quadrant + factor pie + cardFacDetail).
- Six sum-card modals fully rebuilt: TE / Idiosyncratic / Factor / Beta / Active Share / Holdings Count. Each with 4-5 stat boxes, dual-ratio breakdowns, period-aware history, clickable detail expansion.
- Stacked-area decomposition on TE history (idio bottom + factor stacked + TE line).
- Per-cell drill carries factor context (cardCountry heatmap pattern propagated to factor pies).

## 2026-04-28

- B102: cardRiskByDim — TE contribution by Country/Currency/Industry on Risk tab.
- B106: group-level history extraction; verifier 100 PASS.
- Anti-fabrication policy formalized in CLAUDE.md after April 2026 data-integrity crisis.

---

For detailed commit history: `git log --oneline` or [github.com/JGY123/RR/commits/main](https://github.com/JGY123/RR/commits/main).
