# B102 cardRiskByDim — questions for user (autonomous build, 2026-04-27)

User said: "be independent, keep working, when you get to questions maintain a list."
This is the list. None of these blocked the build — I picked a reasonable default for each and documented it. User can override at any point.

---

## Q1 · Sort order — DECIDED: largest absolute magnitude first

The BACKLOG spec says "largest TE contributor at top." In current EM data, some
country buckets have negative net TE contribution (diversifying). I sort by
`Math.abs(total_tr)` so the most-impactful country is at top regardless of sign.

If user wants signed sort (add-most-risk first, diversifying last) say so.

## Q2 · Sign coloring — DECIDED: red = adds risk, green = diversifies, gray = ~zero

Same convention as cardCorr / other risk tiles. Bar fill carries the color.
Threshold for "near zero": |tr| < 0.05% → gray.

## Q3 · "Unmapped" bucket — DECIDED: show with amber warning chip, never filter out

Per BACKLOG spec ("Fallback for the 3-7% unmapped holdings: bucket as 'Unmapped'").
EM has 100% enrichment via security_ref, but SCG has 86% — that 14% needs to
land somewhere. I bucket them as "Unmapped" with an amber `⚠` chip in the
chart label so the user can see the % they can't categorize.

## Q4 · Threshold slider — DECIDED: hidden by default, toolbar pill toggles it

Default threshold 0.5% (per BACKLOG). User can adjust via a pill in the toolbar
that opens an inline slider. Mirrors cardFacContribBars threshold UX.

## Q5 · Drill modal — DECIDED: mirror oDrFRisk with security list

Click a country bar → modal opens with:
- Header: "China — 22.6% of TE (575 holdings)"
- Stat cards: total TE contrib, top-10 stocks' share, avg quintile rank
- Table: securities sorted by abs(h.tr) desc, with ticker / name / weight / TE contrib / O R V Q ranks
- Click any row → drills further to oSt(ticker)

## Q6 · Tab placement — DECIDED: Risk tab, after cardRiskFacTbl

BACKLOG says "Risk tab. Sibling to cardRiskFacTbl." Goes immediately below it
so the user can compare factor-driven TE (cardRiskFacTbl) vs
country/currency/industry-driven TE (cardRiskByDim) side by side.

## Q7 · Default dimension — DECIDED: Country (per BACKLOG)

User can switch via the 3-pill toggle. Selection persists to localStorage
`rr.cardRiskByDim.dim` so it survives reload.

---

## Items to confirm with user post-flight

- [ ] Q1: signed-sort vs absolute-magnitude-sort preference
- [ ] Q3: "Unmapped" displayed inline OR filtered with a footer note
- [ ] Q5: stat cards on drill modal header — what KPIs are most useful for them
- [ ] Card width — full-width on Risk tab, OR half-width sibling to cardRiskFacTbl
  - Decided: full-width because country lists can have 30+ entries
- [ ] Threshold default — 0.5% feels right but PM would know better
