ROLE
You are a data-classification agent working on the RR (Redwood Risk) project. Your job is to take a list of "unassigned" securities and figure out which RWOOD custom Group + Subgroup each one belongs to, then output an Excel file the user will paste into the FactSet OFDB.

INPUT 1 — the unassigned list (Excel)
Path: /Users/ygoodman/Downloads/Groups un.xlsx
Sheet: "Weights"
Structure:
  Row 10 has the column headers. The columns we care about:
    col A (0): SEDOLCHK         e.g. "0059585"
    col B (1): Security Name    e.g. "ARM Holdings plc"
    col C (2): Ticker-Region    e.g. "ARM-GB"
    col D (3): Port. Weight
    col E (4): Bench. Weight
    col F (5): Active Weight
    col G (6): Sector Industry  e.g. "--" or actual sector
    col H (7): Redwood Industry e.g. "Diverse Finl Svc", "Prec Metal & Mineral"
  Rows 1–14 are header rows + Total/[Unassigned] aggregate rows. SKIP THEM.
  Rows 15 → ~5736 are the actual unassigned holdings (one per row).
Each row also carries weekly weight data in columns 8+ for 2010–2025 — IGNORE those columns. Only A through H matter for classification.

INPUT 2 — the reference dataset (already-classified stocks)
Path: /Users/ygoodman/Downloads/risk_reports_sample-3.csv
Section: "Security" rows. For each row, the columns we care about:
  col 5: Level2 (SEDOL identifier, e.g. "6889106")
  col 6: SecurityName
  col 8: Redwood GICS Sector
  col 11: Industry Rollup        ← KEY for matching by industry
  col 12: RWOOD_SUBGROUP         ← KEY: this is the answer we're trying to predict
The Security header row has 271 columns; the subgroup data lives once per period × 6 periods. Use the FIRST period block (cols 8–12 plus prefix). Already-classified stocks here are the "training data".

Also reference: /Users/ygoodman/RR/dashboard_v7.html line ~526 has the GROUPS_DEF taxonomy:
  CYCLICALS        / HARD CYCLICAL    (Materials, Energy)
  CYCLICALS        / GROWTH CYCLICAL  (Info Technology, Comm Services)
  CYCLICALS        / SOFT CYCLICAL    (Consumer Disc., Industrials)
  DEFENSIVE        / DEFENSIVE        (Health Care, Consumer Staples)
  GROWTH           / GROWTH           (Info Technology, Health Care)
  COMMODITY        / COMMODITY        (Materials, Energy)
  RATE SENSITIVE   / BANKS            (Financials)
  RATE SENSITIVE   / BOND PROXIES     (Utilities, Real Estate)

CLASSIFICATION ALGORITHM (in order of preference)

For each unassigned holding (row 15 onward), assign Group + Subgroup using this 3-tier fallback:

  Tier 1 — SEDOL match (HIGH confidence)
  If the SEDOLCHK from "Groups un.xlsx" matches a Level2 value in sample-3.csv Security section, copy that stock's Industry Rollup and RWOOD_SUBGROUP directly. The Group is implied by the Subgroup (per GROUPS_DEF mapping). Mark Confidence = HIGH, Source = "sedol_match".

  Tier 2 — Industry-Rollup match (MEDIUM confidence)
  If no SEDOL match, take the unassigned's "Redwood Industry" (col H) and find the MODE (most common) RWOOD_SUBGROUP among all sample-3 stocks whose Industry Rollup equals or contains that string. Use that subgroup. Mark Confidence = MEDIUM, Source = "industry_mode".

  Note: sample-3's "Industry Rollup" labels won't always exactly match the unassigned's "Redwood Industry" labels. Build a simple normalization (lowercase, strip punctuation, fuzzy-match on first 2–3 words). When in doubt, prefer broader matches.

  Tier 3 — GICS-sector rule fallback (LOW confidence)
  If neither match works, use the GROUPS_DEF taxonomy directly. Most stocks in a single GICS sector cleanly map to one subgroup (e.g., Financials → BANKS, Utilities → BOND PROXIES). For ambiguous sectors (Info Tech could be GROWTH or GROWTH CYCLICAL; Health Care could be DEFENSIVE or GROWTH), pick the more common assignment in sample-3 for that sector OR default to GROWTH CYCLICAL for Tech, DEFENSIVE for Health Care. Mark Confidence = LOW, Source = "gics_fallback".

  Tier 4 — Cannot classify (REVIEW)
  If "Redwood Industry" is missing/blank/"--" AND no SEDOL match: leave Group/Subgroup empty, mark Confidence = REVIEW, Source = "no_industry_data". User will handle manually.

OUTPUT
Path: /Users/ygoodman/Downloads/Groups un classified.xlsx
Sheet: "Classified"
Columns:
  SEDOLCHK | Ticker-Region | Security Name | Redwood Industry (orig) | Sector Industry (orig) | RWOOD_GROUP | RWOOD_SUBGROUP | Confidence | Source

One row per unassigned holding (~5,720 rows expected). Order: same as input.

Also produce a small summary printed to console at the end:
  Total holdings classified: N
  By confidence: HIGH=x, MEDIUM=y, LOW=z, REVIEW=w
  By subgroup: HARD CYCLICAL=…, GROWTH=…, BANKS=… (top 8)
  Sample of REVIEW rows (first 10) — so user can spot-check

CONSTRAINTS
- Do NOT modify any file outside ~/Downloads/. The output file goes there only.
- Do NOT call any external APIs.
- Use openpyxl for Excel I/O; csv module for the CSV.
- Memory-conscious: the input xlsx is 72 MB. Use openpyxl read_only=True for the input. The output is much smaller.
- Estimated wall time: 2–6 minutes including the cross-reference build.

WHEN DONE
Print the summary, then output the file path. Do not commit anything to git — this is a one-off classification artifact, not a code change.
