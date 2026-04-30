# RR Continuation Prompt
**Paste this at the start of a new session to restore context.**

---

I'm working on the RR (Redwood Risk) project — a portfolio risk analytics dashboard that parses FactSet CSV data and displays it in a single-file HTML dashboard.

Before doing ANYTHING, read these files in order:

1. `cat ~/projects/apps/ai-talent-agency/agents/risk-reports-specialist.md`
2. `cat ~/RR/SESSION_CONTEXT.md`
3. `cat ~/RR/DATA_FLOW_MAP.md`

Key rules:
- **VERIFY every claim against actual CSV data** — check the raw file at `/Users/ygoodman/Downloads/risk_reports_3yr.csv`, not just the parsed JSON. Check MULTIPLE periods, not just the last one.
- **One change at a time.** Small, verified steps. תפסת מרובה לא תפסת.
- **No synthetic/fake data.** Every number must come from the real FactSet file.
- **Ask before taking large actions** (like swapping libraries, restructuring files, etc.)

Key files:
- Parser: `~/RR/factset_parser_v2.py`
- Dashboard: `~/RR/dashboard_v7.html`
- Parsed data: `~/RR/latest_data.json`
- Real CSV: `/Users/ygoodman/Downloads/risk_reports_3yr.csv` (29.7MB, 158 weekly periods, 7 strategies)
- Trimmed CSV (last 2 weeks): `~/RR/risk_reports_last2weeks.csv`

Current state: Email sent to FactSet with data questions and expansion requests (see `~/RR/factset_email_READY_TO_SEND.md`). Awaiting response. Meanwhile continuing parser improvements and dashboard validation.

Remaining work:
1. Parse 18 Style Snapshot country/industry/currency rows (data exists, parser skips them)
2. Fix MCap display (millions → billions on dashboard)
3. Compute Selection Rate (h/bh)
4. GICS name mapping for legacy industry names
5. TE chart y-axis 3-10 range (code is there but didn't take effect)
6. Continue tile-by-tile dashboard validation
7. When FactSet responds: re-parse expanded file, verify all fixes
