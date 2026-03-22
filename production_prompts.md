# RR Production CLI Prompts — Ship This Week

These are ready-to-paste prompts for the production CLI. Execute them in order.
Each prompt should complete in ~10-20 minutes.

## ✅ COMPLETED: Tile-by-Tile Audit (23m 35s)
- Factor exposure: f.a (active) not f.e (portfolio) — fixed across 7 locations
- Null-safety: all null values display as -- across holdings, factors, chars
- Label corrections: MCR→%S, Return%→%T, Exposure→Active Exposure
- P/E and P/B benchmark show -- instead of misleading +25.0

---

## Prompt 1: Dashboard Polish & Error Handling (Priority: Critical)

```
You are the Risk Reports Specialist — the full-time virtual worker for the RR (Redwood Risk) project at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md for complete domain context before starting.

TASK: Production-harden the dashboard (dashboard_v7.html) for real-world use.

Current state: Parser works perfectly (7 strategies, 0 validation issues). Dashboard renders all tabs. Need polish for shipping.

Do these specific improvements (NOTE: null-safety was already fixed by the audit — skip anything already handled):

1. **Upload error handling** — When a user uploads a malformed JSON file, show a human-readable error toast (not an alert()). List what's wrong: missing strategies key, empty object, wrong version, etc.

2. **Region sum disclaimer** — In the Regions tab, add a subtle note: "Note: US exposure is not classified into these regional groups" when region sum < 80% for the current strategy. This prevents confusion for SCG/ACWI/GSC.

3. ~~DONE by audit~~ — Null benchmark values already show -- correctly.

4. **Holdings search improvement** — The search box searches by ticker. Also search by company name (the `n` field) and by sector (the `sec` field) if available.

5. **Report date display** — Show the report date (from JSON `report_date` field) in the header next to the strategy selector, formatted as "Jan 30, 2026" style. Store the report_date in a global variable when JSON is loaded.

6. **Data freshness indicator** — Below the strategy buttons, show "Data as of: [date]" with a colored dot (green if < 7 days old, yellow if 7-30 days, red if > 30 days from today).

7. **Tab count badges** — Show count badges on tabs: Holdings (45), Factors (16), Countries (22), etc. from the current strategy data.

8. **Loading state** — Show a brief loading spinner/animation when parsing large JSON files on upload.

Commit after completing all changes: "Production polish: error handling, search, date indicators, tab badges"
```

---

## Prompt 2: Email Snapshot Enhancement (Priority: High)

```
You are the Risk Reports Specialist at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md first.

TASK: Improve the email snapshot export feature (generateEmailSnapshot function) in dashboard_v7.html.

Current state: Uses html2canvas to capture the visible tab. Needs to be more useful for weekly PM emails.

1. **Multi-tab snapshot** — Add a "Full Report Snapshot" button that captures Overview + Sectors + Holdings (top 20) + Factors tabs as a single tall image, with strategy name and report date as a header.

2. **Summary card export** — Add a "Copy Summary" button that generates a plain-text summary block:
   ```
   Redwood Risk — [Strategy Name]
   Report Date: [date]
   ───────────────────────
   Tracking Error: 5.33%    Active Share: 88.92%
   Beta: 1.03               Holdings: 45 / 775
   Cash: 4.4%
   ───────────────────────
   Top 5 Active Bets:
   1. [Ticker] [Name] +[AW]%
   2. ...
   ───────────────────────
   Top Risk Contributors (%T):
   1. [Ticker] [Name] [%T]%
   2. ...
   ```
   Copy to clipboard on click.

3. **CSV export for Holdings** — The exportCSV function exists but verify it exports: Ticker, Name, Portfolio Wt, Benchmark Wt, Active Wt, Overall Rank, REV, VAL, QUAL, MOM, STAB, %T, %S for all holdings.

Commit: "Enhanced email snapshot: multi-tab capture, summary copy, CSV export"
```

---

## Prompt 3: Cross-Strategy Comparison View (Priority: High)

```
You are the Risk Reports Specialist at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md first.

TASK: Build a cross-strategy comparison view in dashboard_v7.html.

Currently users can only view one strategy at a time. PMs need to compare across all 7 strategies.

1. **Add "Compare" tab** as the 8th tab. When clicked, show ALL strategies side-by-side:

   a. **Summary comparison table:**
   | Strategy | TE | Active Share | Beta | Holdings | Cash | P/E |
   |----------|-----|-------------|------|----------|------|-----|
   | IDM      | 5.33| 88.92%      | 1.03 | 45       | 4.4% | 25.0|
   | IOP      | 6.55| 89.07%      | 0.97 | 38       | 0.6% | 23.9|
   | ...      |     |             |      |          |      |     |

   b. **Active weight heatmap** — Plotly heatmap: rows = 11 GICS sectors, columns = 7 strategies, cells = active weight. Red/green diverging colorscale.

   c. **Shared holdings** — Table showing which stocks appear in multiple strategies: Ticker, Name, then 7 columns (one per strategy) showing portfolio weight or "—".

   d. **Risk profile radar** — Small Plotly radar/spider chart comparing TE, Active Share, Beta, Holdings, and Cash across strategies (normalized 0-1 scale for comparability).

2. The Compare tab should work with both real and synthetic data.

Commit: "Add cross-strategy comparison tab: summary table, sector heatmap, shared holdings, radar"
```

---

## Prompt 4: Parser Robustness for Production CSV (Priority: Critical)

```
You are the Risk Reports Specialist at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md first.

TASK: Harden factset_parser.py for production-scale CSV files.

The sample CSV (~3.5MB) works perfectly. Production CSVs may be larger (10-50MB), may have slightly different formatting, and may include new strategies/accounts.

1. **Encoding robustness** — Currently using utf-8-sig. Add fallback: try utf-8-sig → utf-8 → latin-1 → cp1252. Use chardet if all fail. Print encoding used.

2. **Comma-in-name protection** — When a row has MORE columns than expected (e.g., 97 instead of 96), attempt to repair by detecting that columns 5 (SecurityName) contains unquoted commas. Merge the extra columns back into SecurityName. Log a warning with the ticker and original value.

3. **New account handling** — If an ACCT code is found that's not in ACCT_TO_ID, don't crash. Log a warning: "Unknown account [X] — skipping. Add to ACCT_TO_ID if this is a new strategy." Continue parsing other accounts.

4. **Performance** — For files >10MB, add a progress indicator: "Parsing... [X] rows processed" every 50,000 rows.

5. **Validation report enhancements:**
   - Show date range: "Report covers: YYYY-MM-DD to YYYY-MM-DD"
   - Show total row count and parsing time
   - Show per-strategy: number of Data rows found, factor dates found
   - Flag if ANY strategy has 0 holdings (something went wrong)
   - Flag if sector weight sum differs from (100 - cash) by more than 2% (tighter tolerance for production)

6. **Output format version** — Bump version to "2.1" and add "parser_version": "1.0.0" to the JSON output.

7. **TXT file support** — The user may receive TXT files with the same CSV structure. Add handling: if input file ends in .txt, parse exactly the same way as .csv (just change the file extension handling, content is identical).

Test against ~/Downloads/risk_reports_sample.csv and verify same output as before (regression test).

Commit: "Harden parser for production: encoding fallback, comma repair, unknown accounts, progress, TXT support"
```

---

## Prompt 5: Historical Trend Charts (Priority: Medium)

```
You are the Risk Reports Specialist at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md first.

TASK: Enhance the Risk tab's historical trend visualization in dashboard_v7.html.

The parser extracts up to 4 weekly data points per strategy (from the 5 column groups). The dashboard should display these as time-series mini-charts.

1. **TE Trend Line** — Plotly line chart showing Tracking Error over the 4-5 weeks. Include reference lines for the strategy's typical TE range (mean ± 1 std from historical values).

2. **Active Share Trend** — Same format. Mark any week where AS dropped below 80% with a red dot.

3. **Beta Trend** — Same format. Mark weeks where beta > 1.1 or < 0.9 with warning colors.

4. **Holdings Count Trend** — Bar chart showing portfolio holdings count per week.

5. **Factor Exposure Sparklines** — For each of the 16 factors, show a tiny sparkline (50px wide) in the factor table showing the 2 historical data points we have. Helps PMs see if exposures are trending.

6. **All these should be in the existing Risk tab**, organized as a "Trends" section below the current risk decomposition content.

Use Plotly for all charts. Match the existing dark theme (--bg, --card, --txt color variables). No new dependencies.

Commit: "Add historical trend charts: TE, Active Share, Beta, Holdings, factor sparklines"
```

---

## Prompt 6: Automated Test Suite (Priority: Medium)

```
You are the Risk Reports Specialist at ~/RR/. Read ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md first.

TASK: Create a test suite for factset_parser.py.

Create test_parser.py using pytest. Tests should validate:

1. **Unit tests for helpers:**
   - pf() handles: empty string, None, NaN, valid floats, negative numbers, parenthesized negatives
   - r2() rounds to 2dp, handles None
   - get_group() with 96-col row returns 18 values
   - get_group() with 101-col row drops Overall Rank, returns 18 values
   - classify_row() correctly identifies: sectors, regions, countries, holdings, cash, CASH_USD, Data, @NA, custom groups, factors
   - weekly_dates_for() returns 5 Fridays for a given month-end date

2. **Integration tests using sample data:**
   - Parse ~/Downloads/risk_reports_sample.csv
   - Assert exactly 7 strategies returned
   - Assert 0 validation issues
   - Per strategy: sectors count = 11, regions > 0, countries > 0, factors = 16
   - Summary stats are reasonable: 0 < TE < 15, 50 < AS < 100, 0.5 < beta < 1.5
   - Weight reconciliation: sector sum within 5% of (100 - cash)
   - Holdings have non-null ticker, weight > 0
   - Factor data has non-null names

3. **Regression test:**
   - Parse sample CSV, compare output to a saved "known good" JSON snapshot
   - Detect if any strategy's summary metrics changed

4. **Edge case tests:**
   - Row with too many columns (comma in name) — should not crash
   - Unknown account code — should be skipped
   - Empty file — should return empty dict
   - File with only headers — should return empty dict

Run the tests and confirm all pass. Save known-good JSON as test_baseline.json.

Commit: "Add pytest test suite for parser: unit, integration, regression, edge cases"
```

---

## Usage

Paste one prompt at a time into the RR production CLI. Wait for each to complete before pasting the next.

**Priority order for shipping this week:**
1. Prompt 4 (Parser robustness) — FIRST, before the large CSV arrives
2. Prompt 1 (Dashboard polish) — Make it presentable
3. Prompt 2 (Email snapshot) — PMs need this for weekly emails
4. Prompt 3 (Cross-strategy comparison) — High value for decision-making
5. Prompt 6 (Test suite) — Safety net
6. Prompt 5 (Historical trends) — Nice-to-have enhancement

**Total estimated time:** ~2-3 hours across all 6 prompts.
