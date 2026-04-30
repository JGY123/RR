# RR · Inquisitor Question Queue
**Drafted:** 2026-04-28
**For commute review** · answer with letter / yes / no / short text · skip = take default
**Tags:** [parser] [data] [cardSectors] [cardCountry] [cardRegions] [cardGroups] [cardHoldings] [cardFactors] [cardRisk] [cardWatchlist] [chart] [viz] [ux] [infra] [docs] [workflow] [naming]

---

## [P0] Parser & data layer

- **Q1.** [parser] When SCG (or any strategy) is missing from the CSV, what should the dashboard do? *A: alert with red pill · B: silently hide option · C: fall back to last cached snapshot* (default: A)
- **Q2.** [parser] CSV column-count drifts from spec — refuse-to-load or warn-and-load? *A: refuse · B: warn-and-load* (default: A)
- **Q3.** [parser] Should integrity-check threshold for column drift be aggressive (any change alerts) or permissive (additions OK, removals alert)? *A: aggressive · B: permissive* (default: B)
- **Q4.** [parser] Store BOTH raw FactSet field names AND normalized names in JSON, or normalized only? *A: both · B: normalized only* (default: A — for provenance)
- **Q5.** [data] For ADRs in EM/ACWIxUS — confirm country-of-RISK (issuer domicile) is the convention, not country-of-listing? *yes/no* (default: yes)
- **Q6.** [parser] When a factor historically present (e.g., Currency for ACWI/GSC) is missing this week, auto-fill from prior snapshot or emit null? *A: prior snapshot · B: null · C: null + warn banner* (default: C)
- **Q7.** [parser] Should the parser keep `report_date` from filename, from CSV header, or both with mismatch warning? *A: filename · B: CSV · C: both* (default: C)
- **Q8.** [parser] @NA and [Unassigned] rows — drop, keep as separate "Unclassified" bucket, or merge into Other? *A: drop · B: separate bucket · C: merge into Other* (default: B)
- **Q9.** [parser] When CSV quoting breaks names with commas (Berkshire Hathaway, Inc.), should fallback be column-count-based recovery or hard-fail? *A: recovery · B: hard-fail* (default: A)
- **Q10.** [data] PARSER_VERSION bump policy — bump on every CSV schema change or only on output JSON shape change? *A: every CSV schema · B: every JSON output change* (default: B)
- **Q11.** [parser] If FactSet ships a partial week (Wed instead of Fri), append to history or wait for Fri? *A: append · B: wait · C: append flagged as "intra-week"* (default: C)
- **Q12.** [data] Stale-data alert — current default is none. Add alert if last pull > 7 days, > 14 days, or never? *A: 7d · B: 14d · C: never* (default: A)
- **Q13.** [parser] Should the parser emit a manifest.json (file hash, row count, dates extracted, accounts found) on every run? *yes/no* (default: yes)
- **Q14.** [data] Append-only history — write to a single `history.jsonl` per strategy or one file per week? *A: single jsonl · B: per-week files* (default: A)
- **Q15.** [parser] If CSV multi-month detection (30% threshold) misclassifies a date, should the user override via CLI flag or let it auto-correct from prior snapshots? *A: CLI flag · B: auto-correct* (default: A)

---

## [P0] cardSectors

- **Q16.** [cardSectors] Trend column when port-history is empty — show TE history, fall back to current-TE-sign indicator, or hide column? *A: TE history · B: TE-sign indicator · C: hide* (default: B)
- **Q17.** [cardSectors] Bench-only sectors in Port mode — keep visible greyed-out, hide entirely, or move to a footer "Not held" row? *A: visible greyed · B: hide · C: footer row* (default: C)
- **Q18.** [cardSectors] Quadrant chart Q3 yellow — keep yellow (current), switch to muted grey, or switch to red? *A: yellow · B: grey · C: red* (default: A)
- **Q19.** [cardSectors] Full-screen view auto-opens which panel? *A: chart only · B: table only · C: both side-by-side* (default: C)
- **Q20.** [cardSectors] Should the trend sparkline default range match the global chart range buttons (3M/6M/1Y) or always be 1Y? *A: match global · B: always 1Y* (default: A)
- **Q21.** [cardSectors] Sort default — by absolute TE contribution, by active weight, or alphabetical? *A: TE contrib · B: active wt · C: alpha* (default: A)
- **Q22.** [cardSectors] Add a "% of total active risk" column? *yes/no* (default: yes)
- **Q23.** [cardSectors] Should clicking a sector header drill into all holdings of that sector, or open the sector-vs-factor breakdown? *A: holdings · B: factor breakdown · C: choose via tab* (default: A)

---

## [P0] cardCountry

- **Q24.** [cardCountry] Map color-picker default — Active Weight, TE Contribution, or Avg Rank? *A: active wt · B: TE contrib · C: avg rank* (default: B)
- **Q25.** [cardCountry] Country-of-risk vs country-of-listing — toggleable, or pick one as canonical? *A: toggleable · B: canonical (risk)* (default: A)
- **Q26.** [cardCountry] Map projection — equirectangular (current default), Mercator, Robinson? *A: equirect · B: Mercator · C: Robinson* (default: C)
- **Q27.** [cardCountry] Should countries with zero exposure (port AND bench) be grey, white, or hidden? *A: grey · B: white · C: hidden* (default: A)
- **Q28.** [cardCountry] Add a search box to jump to a country by name/ISO code? *yes/no* (default: yes)
- **Q29.** [cardCountry] When viewing EM strategy, should developed-market countries be greyed out or shown at full saturation? *A: greyed · B: full sat · C: hidden* (default: A)

---

## [P0] cardRegions / cardGroups

- **Q30.** [cardRegions] Region taxonomy — keep RR's 7 regions, switch to FactSet's 5, or expose both via toggle? *A: RR's 7 · B: FactSet's 5 · C: both* (default: C)
- **Q31.** [cardRegions] Show "% coverage" pill when region data covers <50% of holdings? *yes/no* (default: yes — already implemented, confirm keep)
- **Q32.** [cardGroups] Allow multi-group membership (a stock can be in Growth AND Cyclical) or strict one-stock-one-group? *A: multi · B: strict* (default: B)
- **Q33.** [cardGroups] Group definitions sourced from — FactSet, Redwood internal, or hybrid? *A: FactSet · B: Redwood · C: hybrid* (default: B — PM's classifications are canonical)
- **Q34.** [cardRegions] Add a "Region vs Sector" cross-tab? *yes/no* (default: yes)

---

## [P0] cardHoldings

- **Q35.** [cardHoldings] Primary identifier shown — ticker-region (TSM-US), SEDOL, or company name? *A: ticker-region · B: SEDOL · C: name* (default: A — name with hover SEDOL)
- **Q36.** [cardHoldings] Benchmark-only holdings ("not owned") — inline with portfolio, separate "Unowned" subtab, or filter pill? *A: inline · B: subtab · C: filter pill* (default: C)
- **Q37.** [cardHoldings] Sort default — abs TE contribution, port weight, or active weight? *A: abs TE · B: port wt · C: active wt* (default: A)
- **Q38.** [cardHoldings] Track position continuity across SEDOL changes (corporate actions, M&A)? *yes/no* (default: yes)
- **Q39.** [cardHoldings] Show sparkline of port weight history per holding? *yes/no* (default: yes)
- **Q40.** [cardHoldings] When a holding exits the portfolio mid-week, should it stay visible for one week tagged "EXITED" or disappear immediately? *A: one week tagged · B: disappear* (default: A)
- **Q41.** [cardHoldings] Tab badge — show equity count or active position count (excludes near-zero)? *A: equity count · B: active count* (default: B)
- **Q42.** [cardHoldings] Add "% portfolio TE explained by top-10" pill at top of tile? *yes/no* (default: yes)

---

## [P0] cardRisk (TE / FRB / Corr)

- **Q43.** [cardRisk] cardTEStacked B96 math issue (pct_specific / pct_factor are "% Total Risk" not "% TE") — fix now or wait for FactSet schema doc? *A: fix now with disclaimer · B: wait* (default: A)
- **Q44.** [cardRisk] cardFRB donut for many factors becomes unreadable — switch to bar chart, treemap, or keep with "top 8 + Other"? *A: bar · B: treemap · C: top-8 + Other* (default: C)
- **Q45.** [cardRisk] cardCorr factor correlation matrix — keep heatmap, add network-graph alternative, or both via toggle? *A: heatmap · B: network · C: both* (default: C)
- **Q46.** [cardRisk] Time-series chart range buttons — add 5Y, since-inception, rolling-12M to existing 3M/6M/1Y/3Y/All? *A: add 5Y · B: add inception · C: add rolling-12M · D: add all three* (default: D)
- **Q47.** [cardRisk] Risk decomposition — show as % of TE² (variance) or % of TE (std)? *A: variance · B: std · C: both with toggle* (default: C)
- **Q48.** [cardRisk] Should TE history chart overlay benchmark TE for context? *yes/no* (default: yes if available)

---

## [P0] cardFactors

- **Q49.** [cardFactors] cardFacDetail TE% — once FactSet ships real values, REMOVE synth markers (sourced now) or KEEP-as-warning (was synth once)? *A: remove · B: keep* (default: A)
- **Q50.** [cardFactors] Default view — active factor exposures only, raw exposures only, or split-tab? *A: active · B: raw · C: split-tab* (default: A)
- **Q51.** [cardFactors] Factor sparkline timeframe — match global range, always 1Y, or always since-inception? *A: match global · B: 1Y · C: inception* (default: A)
- **Q52.** [cardFactors] When a factor's exposure flips sign (e.g., Value goes positive→negative), highlight with marker on sparkline? *yes/no* (default: yes)
- **Q53.** [cardFactors] cardFacButt buttons — keep current 7 factor buttons, add "All" toggle, or replace with dropdown? *A: keep · B: add All · C: dropdown* (default: B)
- **Q54.** [cardFactors] Factor attribution by period (1W/1M/3M/YTD/1Y) — show all 5 in one table or split into tabs? *A: one table · B: tabs* (default: A)

---

## [P0] cardWatchlist

- **Q55.** [cardWatchlist] Auto-watch top-10 TE contributors per strategy or stay user-curated only? *A: auto · B: user-curated · C: both with toggle* (default: C)
- **Q56.** [cardWatchlist] Notification when watchlisted ticker exits portfolio — "EXITED" chip (current), banner alert, or push email? *A: chip · B: banner · C: email · D: chip+banner* (default: D)
- **Q57.** [cardWatchlist] Multi-strategy watchlist — flag a stock once across all strategies or per-strategy? *A: once · B: per-strategy* (default: A)
- **Q58.** [cardWatchlist] Add notes/tags per watchlisted stock (e.g., "earnings 5/3", "PM concern")? *yes/no* (default: yes)
- **Q59.** [cardWatchlist] Show watchlist count badge on the tab? *yes/no* (default: yes)

---

## [P1] Drill modals

- **Q60.** [ux] Sector → drill modal shows ALL holdings or top-20 by TE? *A: all · B: top-20 · C: top-20 default + "Show all" link* (default: C)
- **Q61.** [ux] Drill modals — nest infinitely (sector → country → industry → ticker) or cap at 2 levels? *A: infinite · B: cap at 2 · C: cap at 3* (default: C)
- **Q62.** [ux] Right-click context menu — keep, simplify to copy-value-only, or remove? *A: keep · B: copy-only · C: remove* (default: B)
- **Q63.** [ux] When a drill is open, allow Esc to close and arrow keys to navigate row-by-row? *yes/no* (default: yes)
- **Q64.** [ux] Drill modal export — CSV of drill rows, full-page screenshot, or both? *A: CSV · B: screenshot · C: both* (default: A — no PNG buttons per pref)

---

## [P1] Charts and visualization

- **Q65.** [chart] Top-3 priorities for full-screen chart rebuild — pick 3: *A: multi-metric scatter · B: animated time-series · C: sector-vs-factor heatmap · D: small multiples · E: candlestick · F: parallel coordinates* (default: A, C, D)
- **Q66.** [chart] Plotly vs custom canvas — switch any tile to canvas for perf? *A: yes, holdings table · B: yes, all charts >100pts · C: stay Plotly* (default: C unless perf measurable)
- **Q67.** [chart] Sparkline cells — keep 72×22 fixed or expand to inline detail on hover? *A: fixed · B: hover expand* (default: B)
- **Q68.** [chart] Chart export — only via global ⬇ menu or per-chart button? *A: global only · B: per-chart* (default: A — no per-chart PNG buttons per pref)
- **Q69.** [chart] Default chart palette — keep current dark, switch to ColorBrewer, or use Tableau-10? *A: keep · B: ColorBrewer · C: Tableau-10* (default: A)
- **Q70.** [chart] Should charts respect a "colorblind-safe" mode toggle? *yes/no* (default: yes)
- **Q71.** [chart] Sector heatmap (cross-strategy) — symmetric color scale or per-strategy normalized? *A: symmetric · B: per-strategy* (default: A)

---

## [P1] Performance / UX

- **Q72.** [ux] 1217 holdings × 6 strategies — virtual-scroll the holdings table or paginate? *A: virtual scroll · B: paginate · C: only if perf complaint* (default: C)
- **Q73.** [ux] Light-mode toggle? *yes/no* (default: no)
- **Q74.** [ux] Tablet/iPad view — add responsive layout or stay desktop-only? *A: tablet view · B: desktop-only* (default: B)
- **Q75.** [ux] Keyboard shortcuts — add Cmd+K to jump to a tile? *yes/no* (default: yes)
- **Q76.** [ux] Add Cmd+/ to focus search box? *yes/no* (default: yes)
- **Q77.** [ux] Header week selector ‹ › — add jump-to-date date-picker? *yes/no* (default: yes)
- **Q78.** [ux] Strategy switcher — keep dropdown, switch to tab bar, or both? *A: dropdown · B: tabs · C: both* (default: B once 15+ accounts ship — too many for dropdown)
- **Q79.** [ux] On strategy switch, preserve current tab + week selection? *yes/no* (default: yes)
- **Q80.** [ux] Error states — toast, inline banner, or modal? *A: toast · B: banner · C: modal* (default: B)

---

## [P1] Data delivery / massive-run logistics

- **Q81.** [infra] 15+ accounts ship — share one strategy-mapping config or distinct per-family? *A: shared · B: per-family · C: shared with overrides* (default: C)
- **Q82.** [infra] Weekly delivery post-massive-run — auto-fetch from SFTP/S3 or manual upload via load_data.sh? *A: auto · B: manual · C: auto with manual override* (default: C)
- **Q83.** [infra] After auto-fetch, run smoke_test.py and email/slack the verdict? *A: email · B: slack · C: cli only · D: skip* (default: B)
- **Q84.** [infra] Append-only history retention — keep all weeks forever, prune > 5Y, or prune > 10Y? *A: forever · B: 5Y · C: 10Y* (default: C)
- **Q85.** [infra] When two CSVs have overlapping dates, prefer newer file or keep first-seen? *A: newer · B: first-seen · C: alert and ask* (default: A)
- **Q86.** [infra] Backup the JSON snapshots to S3/Drive on each pull? *yes/no* (default: yes)

---

## [P1] Documentation / institutional knowledge

- **Q87.** [docs] Render functions — docstring + JSON-paths-it-reads on all or only complex ones? *A: all · B: complex only* (default: A)
- **Q88.** [docs] Per-tile "About this tile" popup explaining provenance + math + caveats? *yes/no* (default: yes)
- **Q89.** [docs] Commit messages — include smoke_test exit code? *yes/no* (default: yes)
- **Q90.** [docs] Auto-update SOURCES.md from code annotations or manual? *A: auto · B: manual · C: auto with manual review* (default: C)
- **Q91.** [docs] FACTSET_FEEDBACK.md — add a "resolved" archive section once items close? *yes/no* (default: yes)
- **Q92.** [docs] LESSONS_LEARNED.md — append-only or curate quarterly? *A: append-only · B: curate quarterly* (default: A)

---

## [P1] Workflows / automation

- **Q93.** [workflow] After massive-run pull, run automated screenshot diffs to catch visual regressions? *yes/no* (default: yes)
- **Q94.** [workflow] Auto-create GitHub issue per FAIL in verifier output? *yes/no* (default: yes)
- **Q95.** [workflow] Pre-commit hook — run smoke_test.py before commit? *yes/no* (default: yes)
- **Q96.** [workflow] Pre-push hook — block if integrity assertion fails? *yes/no* (default: yes)
- **Q97.** [workflow] Tag-before-risky-edit — automate via hook on touching dashboard_v7.html / factset_parser.py? *yes/no* (default: yes — already in regression-checkpoint Skill, confirm enable)
- **Q98.** [workflow] Should "session end" auto-update LIEUTENANT_BRIEF.md and SESSION_STATE.md? *yes/no* (default: yes)

---

## [P1] Naming and branding

- **Q99.** [naming] "Spotlight" name — keep, rename, or contextual ("Spotlight Ranks" vs "Spotlight Quality")? *A: keep · B: rename · C: contextual* (default: A)
- **Q100.** [naming] Strategy short codes (IDM, IOP, EM…) — keep abbrevs, expand to full names by default, or both? *A: abbrevs · B: full · C: both (abbrev + tooltip)* (default: C)
- **Q101.** [naming] Tile naming — keep cardX (cardSectors), drop "card" prefix, or rename to "tileX"? *A: keep cardX · B: drop card · C: tileX* (default: A — too much rename churn)
- **Q102.** [naming] "Tracking Error" abbreviation in headers — TE, T.E., or full word? *A: TE · B: T.E. · C: full* (default: A)
- **Q103.** [naming] Active Share — AS, ActSh, or full word? *A: AS · B: ActSh · C: full* (default: A)

---

## [P2] Feature wishlist (yes/no — short answer if yes)

- **Q104.** [chart] Add an "anomaly detection" overlay on time-series (highlight 2σ moves)? *yes/no* (default: yes)
- **Q105.** [data] Add benchmark-only TE attribution (what would TE be if we owned the bench)? *yes/no* (default: no — low value)
- **Q106.** [chart] Brushable time-series (drag to filter holdings to that period)? *yes/no* (default: yes — high impact)
- **Q107.** [data] Add risk-budget mode (set max TE per sector/factor, alert on breach)? *yes/no* (default: yes)
- **Q108.** [chart] Compare two weeks side-by-side via week-selector multi-pick? *yes/no* (default: yes)
- **Q109.** [chart] Compare two strategies side-by-side? *yes/no* (default: yes)
- **Q110.** [data] Stress-test scenarios (e.g., "what if oil drops 20%")? *yes/no* (default: no — out of scope)
- **Q111.** [ux] Add a "presenter mode" that hides chrome and enlarges fonts for screen-share? *yes/no* (default: yes)
- **Q112.** [data] Cross-asset extension (bonds, FX) — even on roadmap or hard no? *A: roadmap · B: hard no* (default: B)
- **Q113.** [ux] Annotations — let user pin a note on a chart point (e.g., "earnings beat")? *yes/no* (default: yes)
- **Q114.** [data] Show fundamentals (P/E, P/B, ROE) per holding when FactSet ships them? *yes/no* (default: yes)

---

## [P2] FactSet pending items — pri ranking

- **Q115.** [data] Of the pending FactSet items, rank top-3 by impact: *A: Compounded Factor Return · B: Bench P/E and P/B · C: Per-holding sector/country/industry/region · D: CSV quoting fix · E: Hit rate / batting average · F: Date labels on weekly groups · G: @NA / [Unassigned] clarification · H: OVER_WAvg scale confirmation* (default: C, D, E)
- **Q116.** [data] Should we follow up on any item not currently on the list? *one sentence*
- **Q117.** [data] If FactSet pushes back on per-holding sector/country in CSV, accept a separate reference file or insist on inline? *A: separate file · B: insist inline* (default: A)

---

## [P2] Open-ended (1-2 sentences)

- **Q118.** What's the ONE missing capability that would have the biggest impact on your daily PM workflow?
- **Q119.** What's the most-distracting visual element on the current dashboard?
- **Q120.** If you could remove one tile, which one and why?
- **Q121.** If you could add one tile, what would it show?
- **Q122.** What's a question colleagues ask about a portfolio that the dashboard doesn't currently answer?
- **Q123.** What's the most-frequent manual lookup you do (Excel, Bloomberg, FactSet workstation) that the dashboard could replace?
- **Q124.** Which view do you screenshot most often for emails / meetings?
- **Q125.** What's a number you trust more in FactSet workstation than in this dashboard, and why?
- **Q126.** Most-confusing label or chart axis in the current build?
- **Q127.** What would make the "Copy Summary" output more useful (fields to add/remove)?
- **Q128.** A future user (analyst, junior PM, CIO) — what's the first thing you'd want them to learn from the dashboard?
- **Q129.** Top 1-2 risks in the current data pipeline that worry you most (silent breakage, fabrication, drift)?
- **Q130.** If a 6-month-from-now version of this dashboard is "great," what does it do that today's doesn't?

---

## [P2] Process & cadence

- **Q131.** [workflow] Weekly review cadence — Monday morning, Friday EOD, or ad-hoc? *A: Mon AM · B: Fri PM · C: ad-hoc* (default: A)
- **Q132.** [workflow] Tile audit signoff — keep current per-tile-explicit, batch-of-3, or trust verifier output? *A: per-tile · B: batch-of-3 · C: verifier* (default: A — current preference)
- **Q133.** [workflow] After signoff, archive prior tile-state in a snapshot folder for rollback? *yes/no* (default: yes)
- **Q134.** [workflow] Quarterly schema review with FactSet team — calendar invite, ad-hoc emails, or skip? *A: calendar · B: ad-hoc · C: skip* (default: A)
- **Q135.** [docs] Maintain a CHANGELOG.md visible in dashboard footer? *yes/no* (default: yes)

---

## End of queue
**Total questions: 135** · skip any section · default-everything is a valid commute outcome
