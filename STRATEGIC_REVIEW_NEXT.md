# RR Strategic Review — 2026-05-04 PM (post-cycle-7)

**Drafted:** 2026-05-04 evening
**Purpose:** Re-baseline after a week of intense audit + refactor + fix work. Captures what's shipped, what's still in flight, and an ordered plan of what's next. Periodic re-baselining so the next session inherits clear priorities.
**Companion:** `STRATEGIC_REVIEW.md` (the May 1 baseline; this is the May 4 follow-on).

---

## 1. State of the dashboard — one paragraph

A single-pane portfolio risk Control Panel for 6 international strategies, sourced entirely from FactSet PA CSV exports. Phase A-K refactor complete (30/30 tiles use `tileChromeStrip`, 10 canonical CSS classes, design tokens). 14 tile audits filed in May (every Risk-tab + Holdings-tab tile classified for F18 contamination). Anti-fabrication discipline reaffirmed: the same `?? 0` pattern that produced the April crisis was found again in May (cardUnowned T1.1, normalize() L1877-1878) and de-fabricated. F19 (per-week pct_specific source-direct) shipped at parser layer + verified end-to-end on real data. F12(a) MCR-derived runtime fallback is the canonical Idio/Factor split today (since FactSet stopped shipping per-period pct_specific). B114 cumulative-merge architecture shipped with 13 tests + CLI + `--merge` flag in `load_multi_account.sh`. F18 letter polished, ready for human send. PM_ONBOARDING + DRILL_MODAL_MIGRATION_SPEC docs filed. **The dashboard is more correct, more disciplined, and more self-documenting than it was a week ago — and the audit cadence has compounded.**

---

## 2. Where we are right now

### 2.1 What shipped this week (May 1–4)

| Category | Items |
|---|---|
| **Parser fixes** | F19 (FORMAT 4.2 → 4.3, per-week pct_specific source-direct join in `_hist_entry`) · normalize() `?? 0` → `?? null` on tr/mcr (76% of bench-only EM holdings de-fabricated) · B114 merge_strategy_into_existing() + helpers |
| **Architecture** | merge_cumulative.py CLI · load_multi_account.sh `--merge` flag · ARCHITECTURE.md (433 lines, contributor-facing intro) |
| **Tile audits** | 14 audit docs filed: 5 Tier-2 (cardCorr, cardFacContribBars, cardTEStacked, cardBetaHist, cardFacHist) + 4 never-audited "Tier-3" (cardRiskDecomp, cardTreemap, cardUnowned, cardWatchlist, cardCashHist, cardRankDist, cardTop10) + 2 Tier-1 carryovers from earlier this week (cardHoldRisk, cardWeekOverWeek, cardRiskByDim) |
| **F18 disclosures** | cardRiskByDim (was canonical) · cardRanks · cardRiskDecomp · cardTreemap · cardUnowned · explicitly clean-by-design tiles labeled in SOURCES.md (cardWatchlist · cardCashHist · cardTop10) |
| **Defensive UI** | cardTEStacked three-tier provenance footer · console-warn on Σ-shares deviation > 5pp · cardFacHist Cum Return ᵉ marker + caveat · cardFacContribBars Profitability alert source fallback (snap_attrib) · cardUnowned 196/819 truth disclosure |
| **Cross-tile sweeps** | Week-marker on 4 of 5 Risk-tab time-series tiles · 4 CSV exporters defined where chrome was no-op (cardBetaHist · cardFacHist · cardFacContribBars · cardTop10) · plotly_click drill wirings (cardRankDist filterByRank · cardFacHist factor drill) |
| **Knowledge base** | 2 new lessons in LESSONS_LEARNED (15: `?? 0` is fab; 16: contamination map) · 3 new RED anti-patterns in data-integrity-specialist persona (13–15) · F18 contamination map in SOURCES.md · risk-reports-specialist persona refreshed (96% → 98%) |
| **PM-facing** | PM_ONBOARDING.md (cheat sheet w/ FAQ + glossary + screenshot placeholders) · DRILL_MODAL_MIGRATION_SPEC.md · F18 letter polished + ready-to-send checklist |
| **Tests** | 26/26 active passing (13 B114 + 7 F19 + 6 legacy) |

**Commit count this week:** ~25 RR commits + 2 talent-agency commits.

### 2.2 What's still imperfect (honest)

1. **F18 letter not yet sent** — recipient name + ~1 hr PA-side experiments (`PA_TESTS_F18.md`) still need a human session. Letter is otherwise ready.
2. **F19 fix is structurally correct but doesn't change today's data** — FactSet stopped shipping per-period pct_specific in current CSV format. Tier 2 (MCR-derived, L2-verified) does the work. F19 silently activates if FactSet ever resumes.
3. **B114 shipped but not yet exercised in production** — `--merge` flag works on synthetic + real-data dry-runs (verified on GSC.json: "+1 new · 526 overwritten"). First real production merge would happen on the next CSV ingest.
4. **3 PM-decision items blocking drill modal migration** — DRILL_MODAL_MIGRATION_SPEC.md Phase A waits on signoff.
5. **Tier-3 audit fixes outstanding** — most never-audited tiles got their RED items fixed but YELLOW polish items remain (catalogued in tile-spec docs). Cycle 7 (this commit) closed many one-line trivials; ~30 medium items still queued.
6. **PM_ONBOARDING screenshots** — 6 placeholders pending user fill.
7. **Drill modal migration not started** — full ~6-7 hour refactor plan filed; awaits user signoff.
8. **Linux server deployment runbook** — Path B in MIGRATION_PLAN.md is sketched but not battle-tested.
9. **End-to-end browser test harness** — Playwright not yet wired.
10. **Per-firm theming + auth/SSO** — only relevant if multi-firm interest emerges.

---

## 3. Strategic priorities for the next 1-2 weeks

Ordered by **leverage × accuracy-impact**, not urgency.

### Tier A — Highest leverage (do first)

**A1. Send the F18 letter.** 1-2 hours of human work. Confirm recipient name (FactSet account manager → quant attribution lead), run `PA_TESTS_F18.md` experiments (~1 hr), human-review the letter for tone, send. Update `FACTSET_FEEDBACK.md` F18 entry with "letter sent YYYY-MM-DD." When the reply comes back: either fold the answer into the parser/docs and close F18, or open a follow-up. **This is the highest-leverage move because it's the gate for closing F18 — once we know whether per-holding %T is supposed to sum to 100% or not, the dashboard's defensive UI either becomes unnecessary (clean) or becomes permanent (codified).**

**A2. Re-parse + merge production data.** ~5 minutes of human-supervised work. Run `./load_multi_account.sh --merge ~/Downloads/risk_reports_sample.csv` (the most recent CSV). This validates B114 cumulative-merge end-to-end on real data + lands FORMAT 4.3 in `data/strategies/*.json`. Optionally `--dry-run` first to preview. Low risk; merge is new-wins on conflicts so existing data only gains, never loses. **Why this matters:** every future ingest gains the audit-trail in `merge_history[]` and the append-only invariant; until the first real merge runs, B114 is "shipped but unproven in prod."

**A3. Drill modal migration sign-off + Phase A.** 15 minutes of PM review on DRILL_MODAL_MIGRATION_SPEC's 3 open questions, then ~2 hours to ship Phase A (helpers) + Phase B (oDrMetric canary). Phase C-G can land next session. **The migration drops ~240 lines of inline drill chrome → ~80 lines of declarative configs and unblocks "add a feature once, ship in all 8 drills" — same compounding value as the tile-chrome migration.**

### Tier B — Medium leverage

**B1. PM-facing onboarding finalization.** PM_ONBOARDING has 6 screenshot placeholders. Fill them after one in-browser walk-through with the user. The doc is otherwise complete (FAQ, glossary, conventions, "when something looks wrong"). **Unblocks firm-wide rollout** — currently the only doc that explains the dashboard from a PM's perspective.

**B2. Tier-3 audit fix sweep — round 2.** Most TRIVIAL items closed in cycles 1-7; the YELLOW polish items remain (~30 across all tiles, 1-15 LOC each). Bundle into 2-3 batched commits. Examples: cardTreemap T1 (color tokens) · cardRiskDecomp F1 (count badge), F2 (hairline footer), F6 (esc wrap) · cardHoldRisk D2/F3 (universe + week banner caveats) · cardRiskByDim D1b/D1c remaining footer label tweaks. **Compounds on the audit cadence — every round closes more.**

**B3. Drill modal migration Phases C-G.** ~4-5 hours after Phase A+B canary lands. Ships oDr · oDrF · oDrCountry · oDrChar · oDrAttrib · oSt · oDrUnowned through the unified helper.

**B4. cardCashHist remaining items + cardWatchlist remaining (per-week routing PM-1).** PM-decision items deferred from cycle 5.

### Tier C — Long-shelf (post first PM rollout)

**C1. End-to-end browser test harness (Playwright).** Currently the only end-to-end safety net is in-browser human review. A 2-3 hour Playwright setup catches: page load, strategy switch, week selector, drill open, CSV export, About popup. Each tile gets a smoke test. **Pays back on every refactor.**

**C2. Linux server deployment runbook.** Path B in MIGRATION_PLAN.md. Currently sketched. Battle-test when there's actual demand for shared deployment.

**C3. Per-firm theming + auth/SSO.** Only if multi-firm interest emerges. CSS variables already drive colors; the surface change is a theme-picker + per-user theme persistence.

**C4. DR / backup strategy formalized.** Today: git push discipline + `data/strategies/*` is committed. If that fails, the parser can rebuild from any CSV. Formalize as a runbook when scale demands.

**C5. Quarterly tile-audit cadence baked into project rhythm.** All 30 tiles audited this quarter (May 2026). Schedule the next sweep for August. Calendar reminder + STRATEGIC_REVIEW refresh.

---

## 4. The five operational loops (refreshed)

The May 1 strategic review introduced the "5 loops" framing. After this week's work, all 5 are running better:

| Loop | Cadence | Recent compounding |
|---|---|---|
| **L1 — Tile audit** | Quarterly, on-demand for hot spots | 14 audits filed in May. F18 contamination map closed for known sites. |
| **L2 — Data integrity monitor** | On every smoke run | `verify_section_aggregates.py` confirmed clean on 3,082/3,082 sector-weeks. Wired into `smoke_test.sh`. |
| **L3 — FactSet inquiry workflow** | Per anomaly | F18 letter polished + ready. F19 self-resolved at parser layer. F12 (long-tail bench-only %T_implied) now cross-referenced in the F18 letter. |
| **L4 — Refactor + lint enforcement** | Per session | Phase A-K complete (30/30 tiles). lint_week_flow.py + smoke_test.sh hold the line. Push discipline (SESSION_GUIDE.md Step 7) caught the 71-commit drift. |
| **L5 — Persona / agent training** | When patterns emerge | `risk-reports-specialist.md` 96% → 98%. `data-integrity-specialist.md` +3 new RED anti-patterns (13-15). LESSONS_LEARNED +2 (15-16). |

---

## 5. What changes our trajectory (early-warning indicators)

- **F18 reply** — could reveal a parser bug (changes "fix code" path) OR confirm the doc is wrong (changes "update doc + close" path). Letter is the trigger; reply timing is unknown.
- **First PM using it daily** — first real-world feedback. Probably surfaces 2-3 issues we haven't anticipated. PM_ONBOARDING shipping unblocks this.
- **Multi-firm interest** — would prioritize auth + theming + Linux deployment.
- **SCG + Alger domestic-model file lands** — schema fingerprint catches it; verify_factset.py runs PARTIAL classification; we acknowledge + add domestic-strategy mapping.
- **B114 first production merge** — first real exercise. Probably surfaces edge cases (date format conflicts, missing dim, etc.) — tests cover the obvious cases but real CSVs always surprise.

---

## 6. Definition of "winning"

Same as May 1 — the metrics aren't ship-date, they're quality + cadence:

| Metric | Current state |
|---|---|
| Σ %TE within ±5% on every (strategy × dim × week) cell PMs see | ✅ 99.7% (3,082/3,082 sector-weeks pass; per-holding F18 escalated) |
| 0 RED findings on smoke test for any session start | ✅ data-integrity layer 5b green; pre-existing parse-bomb (cosmetic) deferred |
| <2 second smoke test wall time | ✅ 1.76s / 22 MB peak (was: hangs forever, 3.4 GB stuck) |
| All Tier-1 + Tier-2 tiles audited within rolling quarter | ✅ 14 audits filed in May; full Risk-tab + Holdings-tab covered |
| Every F-item either resolved or has an active inquiry letter out | 🟡 F18 letter ready (not yet sent); F12 cross-referenced; F11/F14 etc. tracked |
| No commit accumulates more than 1 session's worth before push | ✅ Push discipline baked into SESSION_GUIDE Step 7. 0 commits ahead at session end. |
| PM survey post-rollout: "I trust the numbers" / "I find what I need" / "I haven't been surprised" | ⏳ PM_ONBOARDING shipped; first PM daily-use = next milestone |

**Still hold:** the bias toward "make it right, scale it slowly, become more expert each cycle" is unchanged. This week reinforced that bias — every fix shipped because it improved correctness, not because it was novel.

---

## 7. Concrete next-session action items

When the next session starts, the operator should:

1. Open this doc + STRATEGIC_REVIEW.md (May 1 baseline) for context.
2. Pick the highest-leverage item from §3 Tier A that has user-time available (likely A1 F18 letter or A2 production re-parse).
3. If neither A1 nor A2 is available: ship Tier B items in batches, run smoke + tests + commit/push per session.
4. If something looks like a regression in production data: re-run `./smoke_test.sh` + `python3 verify_section_aggregates.py --latest` + check `last_verify_report.log`. The L2 layer should catch it.
5. End every session with `git push origin main && git push origin --tags` (SESSION_GUIDE.md Step 7).

---

## 8. Closing thought

The May 1 STRATEGIC_REVIEW closed with: *"make it right, scale it slowly, become more expert each cycle. Not 'ship fast.' That bias has produced a dashboard with rare data discipline, an audit cadence that compounds, and a knowledge base that future contributors can stand on."*

Three days later: the bias held. The audit cadence found and de-fabricated a `?? 0` violation that had survived since the April crisis. The F18 contamination map is now closed. F19 + B114 shipped clean architectures, not just fixes. Knowledge accumulated monotonically — every lesson written down made the next finding cheaper.

**The next move isn't to slow down. It's to stay disciplined while moving on the highest-leverage items in §3 Tier A.**
