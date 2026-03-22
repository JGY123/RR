#!/usr/bin/env python3
"""
FactSet Portfolio Attribution CSV → Redwood Risk Dashboard JSON
===============================================================
Usage:
    python3 factset_parser.py <input.csv|input.txt> [output.json]

File structure (confirmed from risk_reports_sample.csv):
  The CSV is a concatenation of 14 separate tables, each preceded by an
  embedded header row (ACCT='ACCT').  Key section schemas:

  96-col (standard): 6 prefix + 5 weekly groups × 18 metrics
    W, BW, AW, %S, %T, %T_Check, OVER_WAvg, REV_WAvg, VAL_WAvg, QUAL_WAvg,
    MOM_WAvg, STAB_WAvg, OVER_Avg, VAL_Avg, QUAL_Avg, MOM_Avg, REV_Avg, STAB_Avg

  101-col (holdings): same as 96-col but with "Overall Rank" inserted at position 5
    W, BW, AW, %S, %T, [Overall Rank], %T_Check, OVER_WAvg, ...
    → group size = 19; Overall Rank skipped to restore standard 18-position layout

  42-col (section @119, portfolio stats): non-repeating, date=main_date
    col[8]  = Predicted TE          col[9]  = Predicted Beta
    col[10] = # of Securities       col[11] = Active Share
    col[12] = Market Cap ($M)       col[16] = EPS Growth 3Yr
    col[20] = FCF Yield NTM         col[21] = Dividend Yield
    col[22] = ROE NTM               col[23] = Operating Margin

  9-col  (section @340, factor exposure): date = exposure_date
    col[6] = Ending Portfolio Exposure
    col[7] = Ending Benchmark Exposure
    col[8] = Ending Active Exposure

  31-col (section @15818, factor attribution): date = attribution_date
    5 periods × 5 cols: AvgActiveExp, CompoundedFactorReturn,
    CompoundedFactorImpact, FactorStdDev, CumulativeFactorImpact
    → period 5 (cols 26–30) = most recent; used for c, ret, imp fields

  Group 5 (index 4) = most recent week → used as current snapshot
  "Data" Level2 rows contain portfolio summary stats
"""

import csv
import json
import math
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

PARSER_VERSION = "1.0.0"
FORMAT_VERSION = "2.1"

# ── Strategy / account mapping ──────────────────────────────────────────────

ACCT_TO_ID = {
    "IDM":     "IDM",
    "ACWIXUS": "IOP",   # IOP uses ACWIXUS in the file
    "EM":      "EM",
    "ISC":     "ISC",
    "SCG":     "SCG",
    "ACWI":    "ACWI",
    "GSC":     "GSC",
}

ACCT_TO_NAME = {
    "IDM":     "International Developed Markets",
    "ACWIXUS": "International Opportunities",
    "EM":      "Emerging Markets",
    "ISC":     "International Small Cap",
    "SCG":     "Small Cap Growth",
    "ACWI":    "All Country World",
    "GSC":     "Global Small Cap",
}

ACCT_TO_BENCHMARK = {
    "IDM":     "MSCI EAFE",
    "ACWIXUS": "MSCI ACWI ex USA",
    "EM":      "MSCI Emerging Markets",
    "ISC":     "MSCI World ex USA Small Cap",
    "SCG":     "Russell 2000 Growth",
    "ACWI":    "MSCI ACWI",
    "GSC":     "MSCI ACWI Small Cap",
}

STRATEGY_ACCTS = set(ACCT_TO_ID.keys())

# ── Level2 classification sets ───────────────────────────────────────────────

GICS_L1 = {
    "Communication Services", "Consumer Discretionary", "Consumer Staples",
    "Energy", "Financials", "Health Care", "Industrials",
    "Information Technology", "Materials", "Real Estate", "Utilities",
}

REGIONS = {
    "English", "Far East", "Northern Europe", "Western Europe",
    "Southern Europe", "Australia - New Zealand", "Emerging Market",
}

QUINTILE_MAP = {
    "1.000000": 1, "2.000000": 2, "3.000000": 3,
    "4.000000": 4, "5.000000": 5,
}

# Custom style buckets → (parent_group, sub_group)
CUSTOM_GROUP_MAP = {
    "HARD CYCLICAL":   ("CYCLICALS",      "HARD CYCLICAL"),
    "GROWTH CYCLICAL": ("CYCLICALS",      "GROWTH CYCLICAL"),
    "SOFT CYCLICAL":   ("CYCLICALS",      "SOFT CYCLICAL"),
    "DEFENSIVE":       ("DEFENSIVE",      "DEFENSIVE"),
    "GROWTH":          ("GROWTH",         "GROWTH"),
    "COMMODITY":       ("COMMODITY",      "COMMODITY"),
    "BANKS":           ("RATE SENSITIVE", "BANKS"),
    "BOND PROXIES":    ("RATE SENSITIVE", "BOND PROXIES"),
}

COUNTRIES = {
    "Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China",
    "Colombia", "Czech Republic", "Denmark", "Egypt", "Finland", "France",
    "Germany", "Greece", "Hong Kong", "Hungary", "India", "Indonesia",
    "Ireland", "Israel", "Italy", "Japan", "Korea", "Kuwait", "Malaysia",
    "Mexico", "Netherlands", "New Zealand", "Norway", "Peru", "Philippines",
    "Poland", "Portugal", "Qatar", "Saudi Arabia", "Singapore", "South Africa",
    "Spain", "Sweden", "Switzerland", "Taiwan", "Thailand", "Turkey",
    "United Arab Emirates", "United Kingdom", "United States", "Usa",
}

# FactSet factor name → dashboard display name
FACTOR_NAME_MAP = {
    "Growth":                    "Growth",
    "Medium-Term Momentum":      "Momentum",
    "Volatility":                "Volatility",
    "Market Sensitivity":        "Market Sensitivity",
    "Liquidity":                 "Liquidity",
    "Exchange Rate Sensitivity": "FX Sensitivity",
    "Profitability":             "Profitability",
    "Currency":                  "Currency",
    "Size":                      "Size",
    "Market":                    "Market",
    "Industry":                  "Industry",
    "Country":                   "Country",
    "Leverage":                  "Leverage",
    "Earnings Yield":            "Earnings Yield",
    "Value":                     "Value",
    "Dividend Yield":            "Dividend Yield",
}

# ── Column layout ────────────────────────────────────────────────────────────

PREFIX_COLS = 6    # ACCT, DATE, PortfolioCurCode, Level, Level2, SecurityName
GROUP_SIZE  = 18
NUM_GROUPS  = 5
CURRENT_GRP = 4    # 0-indexed; group 5 = most recent week

# Position within each 18-col group
C_W       = 0   # Portfolio weight (%)
C_BW      = 1   # Benchmark weight (%)
C_AW      = 2   # Active weight (%)
C_PCT_S   = 3   # % within sector
C_PCT_T   = 4   # % tracking error contribution / count (in Data rows)
C_CHECK   = 5   # %T_Check / active share (in Data rows)
C_OVER_WA = 6   # Overall factor score (weighted avg) / market cap (in Data rows)
C_REV_WA  = 7   # Revision score (weighted avg)
C_VAL_WA  = 8   # Value score (weighted avg)
C_QUAL_WA = 9   # Quality score (weighted avg)
C_MOM_WA  = 10  # Momentum score (weighted avg)
C_STAB_WA = 11  # Stability score (weighted avg)
# C_OVER_A, C_VAL_A, C_QUAL_A, C_MOM_A, C_REV_A, C_STAB_A = 12-17 (simple avgs)

# Expected column counts for the two main schemas
EXPECTED_96  = 96
EXPECTED_101 = 101

# ── Helpers ──────────────────────────────────────────────────────────────────

def pf(s):
    """Parse float → None on empty/invalid."""
    if not s or not str(s).strip():
        return None
    try:
        v = float(str(s).strip())
        return None if math.isnan(v) else v
    except (ValueError, TypeError):
        return None


def r2(v):
    """Round to 2 dp or None."""
    return round(v, 2) if v is not None else None


def get_group(row, g):
    """
    Return list of 18 floats for column group g (0-indexed).

    Handles two schemas automatically:
      - 96-col rows: 5 groups × 18 cols (standard)
      - 101-col rows: 5 groups × 19 cols (has 'Overall Rank' at group position 5)
        → position 5 is dropped to restore the standard 18-position layout
    """
    data_len = len(row) - PREFIX_COLS
    actual_sz = 19 if data_len >= NUM_GROUPS * 19 else GROUP_SIZE
    start = PREFIX_COLS + g * actual_sz
    chunk = row[start : start + actual_sz]
    if actual_sz == 19:
        # Drop "Overall Rank" at position 5 to keep standard column mapping
        chunk = chunk[:5] + chunk[6:]
    return [pf(chunk[i]) if i < len(chunk) else None for i in range(GROUP_SIZE)]


def repair_comma_in_name(row, expected_len):
    """
    Attempt to repair a row that has more columns than expected due to an
    unquoted comma in the SecurityName field (col[5]).

    The repair merges extra columns back into SecurityName by finding how many
    extra columns there are and concatenating col[5] through col[5+extra].

    Returns (repaired_row, repaired_name) or (None, None) if repair fails.
    """
    extra = len(row) - expected_len
    if extra <= 0:
        return None, None
    # SecurityName spans col[5] through col[5 + extra]
    name_parts = row[5:6 + extra]
    repaired_name = ",".join(name_parts)
    repaired_row = row[:5] + [repaired_name] + row[6 + extra:]
    if len(repaired_row) == expected_len:
        return repaired_row, repaired_name
    return None, None


def classify_row(lv2, secname):
    """Return a string tag describing what this row represents."""
    if not lv2 or lv2 in ("Data", "@NA", "[Unassigned]", ""):
        return "special"
    if lv2 == "[Cash]":
        return "cash"
    # Currency cash entries (CASH_USD, CASH_CAD, etc.) — aggregate captured by [Cash] rows
    if lv2.startswith("CASH_"):
        return "other"
    # Named grouping dimensions must be checked BEFORE ticker patterns
    if lv2 in GICS_L1:
        return "sector"
    if lv2 in REGIONS:
        return "region"
    if lv2 in QUINTILE_MAP:
        return "quintile"
    if lv2 in CUSTOM_GROUP_MAP:
        return "custom_group"
    if lv2 in COUNTRIES:
        return "country"
    if lv2 in FACTOR_NAME_MAP:
        return "factor"
    # Security: populated SecurityName, asterisk-prefix, or compact ticker code
    if secname:
        return "holding"
    if lv2.startswith("*"):
        return "holding"
    # Compact ticker codes: no spaces, no decimal, min 4 chars, AND all-uppercase
    # or all-digits (excludes descriptive GICS L2 names like "Banks", "Insurance")
    if (" " not in lv2 and "." not in lv2 and len(lv2) >= 4
            and (lv2.isupper() or lv2.isdigit())):
        return "holding"
    return "other"   # GICS L2 sub-sectors, regional sub-groups, etc.


def weekly_dates_for(report_date_str):
    """
    Given YYYYMMDD end-of-month date, walk back to find the 5 most recent
    Fridays (inclusive) that fall within that month.
    Returns list of 5 date strings YYYY-MM-DD, oldest first.
    """
    d = datetime.strptime(report_date_str, "%Y%m%d").date()
    fridays = []
    cur = d
    while len(fridays) < NUM_GROUPS:
        if cur.weekday() == 4:   # 4 = Friday
            fridays.append(cur)
        cur -= timedelta(days=1)
    fridays.reverse()   # oldest → newest
    return [dt.strftime("%Y-%m-%d") for dt in fridays]


def open_with_encoding(csv_path):
    """
    Try opening the file with a fallback encoding chain.
    Returns (file_handle, encoding_used).
    """
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            fh = open(csv_path, newline="", encoding=enc)
            # Try reading a small chunk to verify the encoding works
            fh.read(1024)
            fh.seek(0)
            print(f"  Encoding: {enc}")
            return fh, enc
        except (UnicodeDecodeError, LookupError):
            try:
                fh.close()
            except Exception:
                pass
            continue
    raise ValueError(f"Could not decode {csv_path} with any of: {encodings}")


# ── Main parser ──────────────────────────────────────────────────────────────

def parse(csv_path):
    """
    Parse the FactSet CSV and return (strategies_dict, validation_issues, main_date, stats).
    strategies_dict keys are dashboard IDs (IDM, IOP, EM, ISC, SCG, ACWI, GSC).
    stats is a dict with parse metadata (row_count, parse_time_s, etc.)
    """
    t_start = time.time()
    csv_path = Path(csv_path)
    file_size_mb = csv_path.stat().st_size / (1024 * 1024)
    show_progress = file_size_mb > 10

    rows_by_acct_date  = defaultdict(list)
    unknown_accts_seen = set()
    repair_warnings    = []
    total_rows         = 0

    fh, enc_used = open_with_encoding(csv_path)
    try:
        reader = csv.reader(fh)
        headers = next(reader)
        for row in reader:
            total_rows += 1
            if show_progress and total_rows % 50_000 == 0:
                print(f"  Parsing... {total_rows:,} rows processed")
            if len(row) < PREFIX_COLS:
                continue
            acct, dt = row[0], row[1]
            if acct in ("ACCT", "Level") or dt in ("DATE",):
                continue

            # Handle unknown account codes gracefully
            if acct not in STRATEGY_ACCTS and acct not in ("ACCT", "Level", ""):
                if acct not in unknown_accts_seen:
                    unknown_accts_seen.add(acct)
                    print(f"  ⚠ Unknown account [{acct}] — skipping. "
                          f"Add to ACCT_TO_ID if this is a new strategy.")
                continue

            if acct not in STRATEGY_ACCTS:
                continue

            # Comma-in-name repair for holdings rows only
            # Skip aggregate/special rows: Data, @NA, [Unassigned], [Cash], etc.
            lv2_raw = row[4] if len(row) > 4 else ""
            _skip_repair = (not lv2_raw or lv2_raw in
                            ("Data", "@NA", "[Unassigned]", "[Cash]", "ACCT", "Level"))
            row_len = len(row)
            if not _skip_repair and row_len > EXPECTED_101:
                # Too long even for 101-col: attempt repair
                repaired, rname = repair_comma_in_name(row, EXPECTED_101)
                if repaired:
                    ticker = row[4] if len(row) > 4 else "?"
                    orig_name = ",".join(row[5:5 + (row_len - EXPECTED_101 + 1)])
                    repair_warnings.append(
                        f"  ⚠ Comma-in-name repaired: acct={acct} ticker={ticker} "
                        f"name={repr(orig_name)} (merged {row_len - EXPECTED_101 + 1} cols)"
                    )
                    row = repaired
                else:
                    repair_warnings.append(
                        f"  ⚠ Could not repair row with {row_len} cols "
                        f"(acct={acct}, ticker={row[4] if len(row)>4 else '?'})"
                    )
            elif not _skip_repair and row_len > EXPECTED_96 and row_len < EXPECTED_101:
                repaired, rname = repair_comma_in_name(row, EXPECTED_96)
                if repaired:
                    ticker = row[4] if len(row) > 4 else "?"
                    orig_name = ",".join(row[5:5 + (row_len - EXPECTED_96 + 1)])
                    repair_warnings.append(
                        f"  ⚠ Comma-in-name repaired: acct={acct} ticker={ticker} "
                        f"name={repr(orig_name)} (merged {row_len - EXPECTED_96 + 1} cols)"
                    )
                    row = repaired

            rows_by_acct_date[(acct, dt)].append(row)
    finally:
        fh.close()

    # Print any repair warnings
    if repair_warnings:
        print(f"\n  Comma-in-name repairs ({len(repair_warnings)}):")
        for w in repair_warnings:
            print(w)

    # Identify which DATE is the main holdings date vs factor dates
    date_counts = defaultdict(int)
    for (acct, dt), rows in rows_by_acct_date.items():
        date_counts[dt] += len(rows)
    sorted_dates = sorted(date_counts, key=lambda d: date_counts[d], reverse=True)
    if not sorted_dates:
        return {}, ["No data rows found (all accounts unknown or file empty)"], "", {
            "total_rows": total_rows, "parse_time_s": round(time.time() - t_start, 2),
            "file_size_mb": round(file_size_mb, 2), "encoding": enc_used,
            "strat_stats": {}, "repair_warnings": len(repair_warnings),
        }
    main_date    = sorted_dates[0]      # most rows = sector/country/holdings data
    factor_dates = sorted_dates[1:]     # smaller row counts = factor snapshots

    # Date range for report
    all_dates    = sorted(sorted_dates)
    date_range   = (all_dates[0], all_dates[-1]) if all_dates else (main_date, main_date)

    week_dates = weekly_dates_for(main_date)   # 5 Friday dates for history

    strategies        = {}
    validation_issues = []

    # Track per-strategy stats
    strat_stats = {}

    for acct in sorted(STRATEGY_ACCTS):
        strat_id   = ACCT_TO_ID[acct]
        main_rows  = rows_by_acct_date.get((acct, main_date), [])

        strat_stats[strat_id] = {
            "data_rows_found": 0,
            "factor_dates":    [],
        }

        if not main_rows:
            validation_issues.append(f"{strat_id}: no rows found for main date {main_date}")
            continue

        s = {
            "id":        strat_id,
            "name":      ACCT_TO_NAME[acct],
            "benchmark": ACCT_TO_BENCHMARK.get(acct, ""),
            "sum":       {},
            "sectors":   [],
            "regions":   [],
            "countries": [],
            "factors":   [],
            "hold":      [],
            "ranks":     [],
            "chars":     [],
            "groups":    [],
            "unowned":   [],
            "hist":      {"summary": [], "fac": {}},
        }

        cash_weight = None
        data_rows   = []       # rows for Level2='Data'

        # ── Pass 1: classify and extract main_date rows ──────────────────────
        seen_sectors   = set()
        seen_regions   = set()
        seen_countries = set()
        seen_groups    = set()
        seen_holdings  = set()

        for row in main_rows:
            lv2     = row[4] if len(row) > 4 else ""
            secname = row[5].strip() if len(row) > 5 else ""
            # Normalize country aliases before classification
            if lv2 == "Usa":
                lv2 = "United States"
            rtype   = classify_row(lv2, secname)
            cur     = get_group(row, CURRENT_GRP)   # group 5 = most recent week

            if rtype == "cash":
                w = cur[C_W]
                if w is not None:   # don't overwrite a real value with a later empty row
                    cash_weight = w

            elif rtype == "sector":
                if lv2 not in seen_sectors:
                    seen_sectors.add(lv2)
                    s["sectors"].append({
                        "n": lv2,
                        "p": r2(cur[C_W]),
                        "b": r2(cur[C_BW]),
                        "a": r2(cur[C_AW]),
                        "s": r2(cur[C_PCT_S]),
                        "t": r2(cur[C_PCT_T]),
                    })

            elif rtype == "region":
                if lv2 not in seen_regions:
                    seen_regions.add(lv2)
                    s["regions"].append({
                        "n": lv2,
                        "p": r2(cur[C_W]),
                        "b": r2(cur[C_BW]),
                        "a": r2(cur[C_AW]),
                    })

            elif rtype == "country":
                if lv2 not in seen_countries:
                    seen_countries.add(lv2)
                    s["countries"].append({
                        "n": lv2,
                        "p": r2(cur[C_W]),
                        "b": r2(cur[C_BW]),
                        "a": r2(cur[C_AW]),
                    })

            elif rtype == "custom_group":
                sg_key = CUSTOM_GROUP_MAP[lv2][1]
                if sg_key not in seen_groups:
                    seen_groups.add(sg_key)
                    pg, sg = CUSTOM_GROUP_MAP[lv2]
                    s["groups"].append({
                        "g":  pg,
                        "sg": sg,
                        "p":  r2(cur[C_W]),
                        "b":  r2(cur[C_BW]),
                        "a":  r2(cur[C_AW]),
                    })

            elif rtype == "holding":
                if lv2 in seen_holdings:
                    continue
                seen_holdings.add(lv2)

                w  = cur[C_W]
                bw = cur[C_BW]
                aw = cur[C_AW]
                if aw is None and (w is not None or bw is not None):
                    aw = r2((w or 0.0) - (bw or 0.0))

                # OVER_WAvg contains the overall analyst rating (1–5 scale)
                over_score = cur[C_OVER_WA]
                rank = max(1, min(5, round(over_score))) if over_score is not None else None

                holding = {
                    "t":    lv2,
                    "n":    secname,
                    "sec":  None,    # sector not embedded per holding in this CSV
                    "co":   None,    # country not embedded per holding in this CSV
                    "p":    r2(w),
                    "b":    r2(bw),
                    "a":    r2(aw),
                    "mcr":  r2(cur[C_PCT_S]),   # %S stock-specific TE component
                    "tr":   r2(cur[C_PCT_T]),   # %T tracking error contribution
                    "r":    rank,
                    "over": r2(cur[C_OVER_WA]),
                    "rev":  r2(cur[C_REV_WA]),
                    "val":  r2(cur[C_VAL_WA]),
                    "qual": r2(cur[C_QUAL_WA]),
                    "mom":  r2(cur[C_MOM_WA]),
                    "stab": r2(cur[C_STAB_WA]),
                }

                if w and w > 0:
                    s["hold"].append(holding)
                elif bw and bw > 0:
                    # In benchmark but not portfolio → unowned risk
                    s["unowned"].append({
                        "t":   lv2,
                        "n":   secname,
                        "reg": None,
                        "b":   r2(bw),
                        "tr":  r2(cur[C_PCT_T]),
                    })

            elif rtype == "special" and lv2 == "Data":
                data_rows.append(row)

        strat_stats[strat_id]["data_rows_found"] = len(data_rows)

        # ── Summary stats from Data rows ─────────────────────────────────────
        te = as_ = beta = h = bh = None
        mktcap_p = mktcap_b = None
        pe_p = pb_p = None          # P/E and P/B (portfolio only; no benchmark in export)
        eps_growth_p = eps_growth_b = None
        fcf_yield_p  = fcf_yield_b  = None
        div_yield_p  = div_yield_b  = None
        roe_p        = roe_b        = None
        op_margin_p  = op_margin_b  = None

        for row in data_rows:
            g1 = get_group(row, 0)
            if g1[C_W] is None and g1[C_OVER_WA] is not None and g1[C_OVER_WA] > 1000:
                te       = g1[C_AW]           # Predicted Tracking Error %
                beta     = g1[C_PCT_S]         # Predicted Beta to Benchmark
                h_raw    = g1[C_PCT_T]         # # of Securities
                as_raw   = g1[C_CHECK]         # Active Share %
                mktcap_p = g1[C_OVER_WA]       # Portfolio Market Cap ($M)

                h   = int(h_raw)  if h_raw  is not None else None
                as_ = as_raw

                # Fundamentals (portfolio)
                eps_growth_p = g1[10]
                fcf_yield_p  = g1[14]
                div_yield_p  = g1[15]
                roe_p        = g1[16]
                op_margin_p  = g1[17]

                g2 = get_group(row, 1)
                if g2[C_PCT_T] is not None:
                    bh       = int(g2[C_PCT_T])
                    mktcap_b = g2[C_OVER_WA]

                # Fundamentals (benchmark)
                eps_growth_b = g2[10]
                fcf_yield_b  = g2[14]
                div_yield_b  = g2[15]
                roe_b        = g2[16]
                op_margin_b  = g2[17]

            # Section @90: Fundamental characteristics (P/E, P/B)
            elif g1[C_W] is None and g1[C_BW] is not None:
                pe_p = g1[C_BW]    # Price/Earnings (portfolio only)
                pb_p = g1[C_AW]    # Price/Book (portfolio only)

        h_actual = len(s["hold"])
        s["sum"] = {
            "te":   r2(te),
            "as":   r2(as_),
            "beta": r2(beta),
            "h":    h_actual,
            "bh":   bh,
            "sr":   None,
            "cash": r2(cash_weight),
        }

        # Portfolio characteristics
        chars_data = [
            ("Market Cap ($M)", mktcap_p,    mktcap_b),
            ("P/E Ratio",       pe_p,        None),
            ("P/B Ratio",       pb_p,        None),
            ("ROE NTM (%)",     roe_p,        roe_b),
            ("FCF Yield (%)",   fcf_yield_p,  fcf_yield_b),
            ("Div Yield (%)",   div_yield_p,  div_yield_b),
            ("EPS Growth 3Y (%)", eps_growth_p, eps_growth_b),
            ("Op Margin (%)",   op_margin_p,  op_margin_b),
        ]
        for label, p_val, b_val in chars_data:
            if p_val is not None:
                s["chars"].append({"m": label, "p": r2(p_val), "b": r2(b_val)})

        # ── Ranks from holdings' r field ─────────────────────────────────────
        for r_val in range(1, 6):
            grp_holds  = [h for h in s["hold"] if h.get("r") == r_val]
            ct = len(grp_holds)
            p  = sum(hh["p"] or 0 for hh in grp_holds)
            label = "R1 (Best)" if r_val == 1 else ("R5 (Worst)" if r_val == 5 else f"R{r_val}")
            s["ranks"].append({"r": r_val, "l": label, "ct": ct, "p": r2(p), "a": None})

        # ── Factors from other dates ─────────────────────────────────────────
        factor_map = {}

        for fdate in sorted(factor_dates):
            factor_rows = rows_by_acct_date.get((acct, fdate), [])
            if not factor_rows:
                continue
            has_bw = any(
                get_group(r, 0)[C_BW] is not None
                for r in factor_rows if r[4] in FACTOR_NAME_MAP
            )
            fdate_str = f"{fdate[:4]}-{fdate[4:6]}-{fdate[6:]}"
            strat_stats[strat_id]["factor_dates"].append(fdate_str)

            for row in factor_rows:
                lv2   = row[4] if len(row) > 4 else ""
                fname = FACTOR_NAME_MAP.get(lv2)
                if not fname:
                    continue
                g1 = get_group(row, 0)
                w  = g1[C_W]
                bw = g1[C_BW]
                aw = g1[C_AW]

                if fname not in factor_map:
                    factor_map[fname] = {
                        "n": fname, "a": None, "bm": None, "e": None,
                        "c": None, "ret": None, "imp": None,
                    }

                entry = factor_map[fname]

                if has_bw:
                    entry["e"]  = r2(w)
                    entry["bm"] = r2(bw)
                    entry["a"]  = r2(aw if aw is not None else
                                     ((w or 0) - (bw or 0)))
                else:
                    ATTR_PERIOD = 5
                    last_start  = PREFIX_COLS + (NUM_GROUPS - 1) * ATTR_PERIOD
                    if len(row) > last_start + 4:
                        entry["c"]   = r2(pf(row[last_start + 2]))
                        entry["ret"] = r2(pf(row[last_start + 1]))
                        entry["imp"] = r2(pf(row[last_start + 4]))

                if fname not in s["hist"]["fac"]:
                    s["hist"]["fac"][fname] = []
                s["hist"]["fac"][fname].append({
                    "d":  fdate_str,
                    "e":  r2(w),
                    "bm": r2(bw),
                })

        s["factors"] = list(factor_map.values())

        # ── Weekly history summary from Data stat rows ────────────────────────
        weekly_stats = []
        for row in data_rows:
            g1 = get_group(row, 0)
            if g1[C_W] is None and g1[C_OVER_WA] is not None and g1[C_OVER_WA] > 1000:
                weekly_stats.append(g1)

        offset = NUM_GROUPS - len(weekly_stats)
        for i, g1 in enumerate(weekly_stats):
            wdate  = week_dates[offset + i] if (offset + i) < len(week_dates) else week_dates[-1]
            te_w   = g1[C_AW]
            beta_w = g1[C_PCT_S]
            as_w   = g1[C_CHECK]
            h_w    = int(g1[C_PCT_T]) if g1[C_PCT_T] is not None else h
            s["hist"]["summary"].append({
                "d":    wdate,
                "te":   r2(te_w)   if te_w   and 0  < te_w   < 20  else None,
                "as":   r2(as_w)   if as_w   and 50 < as_w   < 100 else None,
                "beta": r2(beta_w) if beta_w and 0  < beta_w < 3   else None,
                "h":    h_w,
                "sr":   None,
            })

        if not s["hist"]["summary"]:
            s["hist"]["summary"].append({
                "d": week_dates[-1], "te": r2(te), "as": r2(as_),
                "beta": r2(beta), "h": h, "sr": None,
            })

        # ── Consistent ordering ───────────────────────────────────────────────
        reg_order = ["Far East", "English", "Northern Europe", "Western Europe",
                     "Southern Europe", "Emerging Market", "Australia - New Zealand"]
        s["regions"].sort(key=lambda r: reg_order.index(r["n"]) if r["n"] in reg_order else 99)
        s["sectors"].sort(key=lambda x: -(x["p"] or 0))
        s["countries"].sort(key=lambda x: -(x["p"] or 0))
        s["hold"].sort(key=lambda x: -(x["p"] or 0))
        s["unowned"].sort(key=lambda x: -(x["b"] or 0))

        strategies[strat_id] = s

        # ── Per-strategy validation ───────────────────────────────────────────
        sector_sum  = sum(x["p"] or 0 for x in s["sectors"])
        region_sum  = sum(x["p"] or 0 for x in s["regions"])
        country_sum = sum(x["p"] or 0 for x in s["countries"])
        equity_exp  = 100 - (cash_weight or 0)

        # Flag 0 holdings
        if len(s["hold"]) == 0:
            validation_issues.append(
                f"{strat_id}: ⚠ 0 portfolio holdings found — check CSV for this account"
            )

        # Flag sector sum off by more than 2% from (100 - cash)
        if s["sectors"] and abs(sector_sum - equity_exp) > 2:
            validation_issues.append(
                f"{strat_id}: sector weights sum to {sector_sum:.1f}% "
                f"(expected ~{equity_exp:.1f}%, diff {sector_sum - equity_exp:+.1f}%)"
            )
        if s["countries"] and abs(country_sum - equity_exp) > 5:
            validation_issues.append(
                f"{strat_id}: country weights sum to {country_sum:.1f}% "
                f"(expected ~{equity_exp:.1f}%, diff {country_sum - equity_exp:+.1f}%)"
            )

    t_elapsed = time.time() - t_start

    parse_stats = {
        "total_rows":     total_rows,
        "parse_time_s":   round(t_elapsed, 2),
        "file_size_mb":   round(file_size_mb, 2),
        "encoding":       enc_used,
        "main_date":      main_date,
        "factor_dates":   factor_dates,
        "date_range":     date_range,
        "repair_warnings": len(repair_warnings),
        "unknown_accts":  list(unknown_accts_seen),
        "strat_stats":    strat_stats,
    }

    return strategies, validation_issues, main_date, parse_stats


# ── Validation report ────────────────────────────────────────────────────────

def print_validation(strategies, issues, parse_stats):
    print("\n" + "=" * 62)
    print("VALIDATION REPORT")
    print("=" * 62)

    # Parse metadata header
    dr = parse_stats["date_range"]
    d0 = f"{dr[0][:4]}-{dr[0][4:6]}-{dr[0][6:]}"
    d1 = f"{dr[1][:4]}-{dr[1][4:6]}-{dr[1][6:]}"
    print(f"\n  Report covers:  {d0}  →  {d1}")
    print(f"  Total rows:     {parse_stats['total_rows']:,}")
    print(f"  Parse time:     {parse_stats['parse_time_s']}s")
    print(f"  File size:      {parse_stats['file_size_mb']} MB")
    print(f"  Encoding:       {parse_stats['encoding']}")
    if parse_stats["repair_warnings"]:
        print(f"  Comma repairs:  {parse_stats['repair_warnings']}")
    if parse_stats["unknown_accts"]:
        print(f"  Unknown accts:  {parse_stats['unknown_accts']}")

    for sid, s in strategies.items():
        sm = s["sum"]
        ss = parse_stats["strat_stats"].get(sid, {})
        sector_sum  = sum(x["p"] or 0 for x in s["sectors"])
        country_sum = sum(x["p"] or 0 for x in s["countries"])
        region_sum  = sum(x["p"] or 0 for x in s["regions"])
        print(f"\n{sid:6s}  {s['name']}")
        print(f"  Holdings:   {len(s['hold'])} portfolio, {len(s['unowned'])} unowned")
        print(f"  Sectors:    {len(s['sectors'])} items, weight sum = {sector_sum:.1f}%")
        print(f"  Regions:    {len(s['regions'])} items, weight sum = {region_sum:.1f}%")
        print(f"  Countries:  {len(s['countries'])} items, weight sum = {country_sum:.1f}%")
        print(f"  Groups:     {len(s['groups'])} custom buckets")
        print(f"  Factors:    {len(s['factors'])} factors")
        print(f"  Data rows:  {ss.get('data_rows_found', '?')} found  "
              f"| Factor dates: {ss.get('factor_dates', [])}")
        print(f"  Summary:    TE={sm['te']}  AS={sm['as']}%  "
              f"H={sm['h']}  BH={sm['bh']}  Cash={sm['cash']}%")
        if s["chars"]:
            for c in s["chars"]:
                print(f"  Chars:      {c['m']} portfolio={c['p']}  bench={c['b']}")

    if issues:
        print(f"\n{'─'*62}")
        print(f"ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  ⚠  {issue}")
    else:
        print(f"\n  ✓  No validation issues detected")
    print()


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 factset_parser.py <input.csv|input.txt> [output.json]")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: file not found: {csv_path}")
        sys.exit(1)

    # Accept both .csv and .txt extensions (same format)
    if csv_path.suffix.lower() not in (".csv", ".txt"):
        print(f"Warning: unexpected extension {csv_path.suffix!r} — treating as CSV")

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else csv_path.with_suffix(".json")

    print(f"Parsing {csv_path} …")
    strategies, issues, main_date, parse_stats = parse(csv_path)

    output = {
        "generated":      datetime.now().isoformat(timespec="seconds"),
        "version":        FORMAT_VERSION,
        "parser_version": PARSER_VERSION,
        "freq":           "weekly-in-month",
        "report_date":    f"{main_date[:4]}-{main_date[4:6]}-{main_date[6:]}",
        "strategies":     strategies,
    }

    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"Output written to {out_path}")

    print_validation(strategies, issues, parse_stats)


if __name__ == "__main__":
    main()
