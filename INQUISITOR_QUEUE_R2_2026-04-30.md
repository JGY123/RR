# RR · Inquisitor Question Queue — Round 2
**Drafted:** 2026-04-30 (post tab-audit + data-viz subagent batch)
**For commute review** · answer with letter / yes / no / short text · skip = take default
**Tags:** [audit] [layout] [tile-move] [mockup] [tableau] [chrome] [ux] [data] [naming] [retire]

This round covers decisions surfaced by:
- `tile-specs/TAB_QUALITY_AUDIT_2026-04-30.md` (Risk + Holdings vs Exposures)
- `TABLEAU_AND_MOCKUP_NOTES.md` (data-viz agent recommendations)
- This session's chrome polish + responsive-sizing work
- Items the user touched but didn't fully resolve (cardWeekOverWeek mockup, etc.)

---

## [P0] Tile placement (audit fallout)

- **R2-Q1.** [tile-move] Move `cardWatchlist` from Exposures to Holdings tab? Audit recommends Yes — watchlist is a per-holding curation activity, flags are set from Holdings rows, makes sense to live with the source. *A: yes move to Holdings · B: keep on Exposures · C: render on both* (default: A)
- **R2-Q2.** [tile-move] Move `cardBetaHist` from Risk to Exposures (under sum-cards, above cardSectors)? Beta is a portfolio-state-snapshot metric and the Beta sum-card already opens the same drill. Risk tab focuses on TE decomposition. *A: yes move to Exposures · B: keep on Risk · C: clone to both* (default: A)
- **R2-Q3.** [retire] Bare Rank Distribution chart at bottom of Holdings tab — duplicates `cardRanks` Spotlight on Exposures. *A: delete · B: upgrade to first-class (id + About + drill) · C: keep bare* (default: A)
- **R2-Q4.** [retire] Bare Top 10 Holdings chart at bottom of Holdings — overlaps with `cardHoldRisk` quadrant. *A: delete · B: upgrade to first-class · C: keep bare* (default: B — useful at-a-glance view)
- **R2-Q5.** [tile-move] `cardChars` (Portfolio Characteristics) is currently full-width Exposures. Move to Holdings (PMs often look at fundamentals alongside the holdings list)? *A: move · B: keep on Exposures · C: clone* (default: B)

---

## [P1] Layout principles

- **R2-Q6.** [layout] Confirm placement principle going forward: Exposures = portfolio-state-snapshot · Risk = decomposition + time-series · Holdings = per-holding browse + scatters? *yes/no* (default: yes)
- **R2-Q7.** [layout] Ultra-wide breakpoint (≥1600px) — should some Risk tiles pair into 2-column rows (e.g. cardTEStacked + cardBetaHist side-by-side)? *A: yes pair · B: stay full-width even on ultra-wide · C: only the snapshot tiles, not time-series* (default: A)
- **R2-Q8.** [layout] When you mention "Chrome bigger screen tiles don't scale" — do you want chart heights to scale linearly with viewport, or stay fixed and let WHITE SPACE breathe more? Current fix: chart heights use `clamp(min, vh, max)` so they grow ~30-50% on a 1440p+ display. *A: ✓ keep clamp · B: revert to fixed pixels · C: scale even more aggressively* (default: A)

---

## [P1] Chrome consistency

- **R2-Q9.** [chrome] Reset Zoom button — on every chart tile (regardless of whether user typically zooms), or only on tiles with explicit zoom interaction (range slider, pan)? Current: swept across 7 chart tiles in this commit. *A: every chart · B: only zoomable charts · C: tiles where user has reported losing their place* (default: A)
- **R2-Q10.** [chrome] cardBetaHist click model — was "click anywhere on tile opens drill", now "click open detail › button". Confirm preference. *A: ✓ explicit button · B: revert to whole-card click · C: both (button + clickable card-title only)* (default: A)
- **R2-Q11.** [chrome] When Reset Zoom is clicked, should it ALSO reset other chart state (selected factors, threshold slider, view toggle)? Currently: zoom-only. cardFacContribBars has a separate ⤾ Reset that resets controls. *A: zoom-only (current) · B: zoom + all state · C: explicit "Reset All" combo button* (default: A)
- **R2-Q12.** [chrome] On `cardCorr` (Factor Correlation Matrix) — period dropdown default. Currently "All". For typical PM use, what's the right default? *A: All · B: 1Y · C: 3M · D: remember last choice via localStorage* (default: D)
- **R2-Q13.** [chrome] `cardRiskFacTbl` Impact column header — currently shows "(3M)" or whatever the global selector is. Should the Return column also be period-aware (cumulative return over period), or stay latest-week-only? *A: stay latest only · B: make Return period-aware too · C: add a separate "Cum Return (period)" column alongside* (default: A)
- **R2-Q14.** [chrome] About modal "related:" cross-references — when a tile is removed (cardMCR, cardCalHeat, cardRiskCtryFactor in this batch), do you want to keep the entry as an inert "this was retired, see X" stub, or delete entirely? *A: delete entirely (current) · B: keep as retired-stub · C: keep as stub with a Hidden flag in registry* (default: A)

---

## [P1] Mockup mechanism

- **R2-Q15.** [mockup] Confirm the data-viz subagent's mockup mechanism: standalone HTML at `/viz-specs/{tile}-mockup.html`, 3 candidates per mockup, evaluated in 3 min in browser. *A: ✓ ship it · B: prefer PDF · C: prefer Figma · D: just describe in markdown* (default: A)
- **R2-Q16.** [mockup] Worked example at `/viz-specs/cardWeekOverWeek-mockup.html` shows 3 candidate designs (KPI strip + move list / bubble scatter / 13-week timeline). Which design do you want me to implement? *A: Option A (KPI + 3-col move list) · B: Option B (bubble scatter) · C: Option C (timeline strip) · D: blend two · E: rethink* (default: A)
- **R2-Q17.** [mockup] When a mockup file is "approved + implemented," what happens to the file? *A: keep forever as design archive (current proposal) · B: delete after implementation · C: move to /viz-specs/archive/* (default: A)
- **R2-Q18.** [mockup] Should I add a `viz-specs/INDEX.md` auto-generated index of every mockup/spec pair with status (proposed / approved / implemented)? *yes/no* (default: yes)

---

## [P2] Tableau

- **R2-Q19.** [tableau] Do you have a Tableau Creator license through your firm? *yes/no/unsure* (default: unsure → I'll assume Tableau Public Desktop with anonymized data only)
- **R2-Q20.** [tableau] If yes — do you want me to write a `export_to_tableau.py` helper that exports one section of `latest_data.json` to a flat CSV for Tableau Show Me sketching? *yes/no* (default: yes)
- **R2-Q21.** [tableau] Of the 7 Tableau-popularized patterns I flagged (bullet, marimekko, slope, highlight tables, dot plots, reference bands, annotated histograms) — which ONE most speaks to you for next-up integration? *A: bullet on KPI strip · B: marimekko on cardSectors · C: slope on cardWeekOverWeek · D: reference bands on Historical Trends · E: none — wait until I have more data · F: other (text)* (default: D — high signal-to-effort)

---

## [P2] Going-forward audit cadence

- **R2-Q22.** [workflow] Tab quality audit cadence — re-audit Risk + Holdings vs Exposures after every batch of 5+ changes, every 2 weeks, or only when triggered? *A: per-batch · B: bi-weekly · C: triggered (drift suspected)* (default: B)
- **R2-Q23.** [workflow] cardRiskFacTbl is now period-aware on Impact. Should I do a similar sweep across ALL drill modals to ensure period selector is honored everywhere it's labeled? *yes/no* (default: yes — consistency win)
- **R2-Q24.** [data] Now that Factor Correlation Matrix is first-class, should it be tile-audited like the other tiles? Adds a row to MARATHON_PROTOCOL.md. *yes/no* (default: yes)

---

## [P3] Naming + docs

- **R2-Q25.** [naming] Should `cardRiskDecomp` (just promoted) appear in the section ABOVE or BELOW `cardTEStacked` on Risk tab? Currently above (between Historical Trends and TE Stacked). *A: above (current) · B: below TE Stacked · C: collapse cardRiskDecomp into cardTEStacked as a slide-out panel* (default: A)
- **R2-Q26.** [docs] When I delete orphan code (~150 lines this batch), should the commit message list the deleted function names as a paste-able diff, or just a high-level summary? *A: summary (current) · B: full function-name diff · C: both* (default: A)
- **R2-Q27.** [docs] Should `BACKLOG.md` get a new section labeled "Audit follow-ups" listing the 3 PM-decision items from this round, or stay as-is with mentions inline? *A: new section · B: stay as-is · C: separate `AUDIT_FOLLOWUPS.md`* (default: A)

---

## [P3] Free-form

- **R2-Q28.** [free] Anything in this session's batch you want to roll back? (cardBetaHist click model, FacRisk top-OW/UW KPIs, cardCorr being first-class, etc.) *list anything · skip = nothing* (default: nothing)
- **R2-Q29.** [free] Most surprising thing you saw in the tab-audit doc? *short text · skip* (default: skip)
- **R2-Q30.** [free] One thing you want me to do BEFORE the next audit cadence kicks in? *short text · skip* (default: skip — proceed with backlog)

---

**Total round-2 questions: 30**
**Estimated reply time: 5-8 min on commute**
**Defaults are all conservative — skip = move on, no harm.**
