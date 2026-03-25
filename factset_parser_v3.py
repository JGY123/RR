#!/usr/bin/env python3
"""
FactSet CSV Parser v3 — Section-driven parser for the new format
================================================================
Reads the new FactSet format with explicit Section column and dates.
Outputs JSON compatible with dashboard_v7.html field names.

Usage: python3 factset_parser_v3.py <input.csv> [output.json]
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

# Strategy mapping
ACCT_TO_ID = {
    "IDM": "IDM", "ACWIXUS": "IOP", "EM": "EM",
    "ISC": "ISC", "SCG": "SCG", "ACWI": "ACWI", "GSC": "GSC",
}
ACCT_TO_NAME = {
    "IDM": "International Developed Markets",
    "ACWIXUS": "International Opportunities",
    "EM": "Emerging Markets",
    "ISC": "International Small Cap",
    "SCG": "Small Cap Growth",
    "ACWI": "All Country World",
    "GSC": "Global Small Cap",
}
ACCT_TO_BENCHMARK = {
    "IDM": "MSCI EAFE", "ACWIXUS": "MSCI ACWI ex USA",
    "EM": "MSCI Emerging Markets", "ISC": "MSCI World ex USA Small Cap",
    "SCG": "Russell 2000 Growth", "ACWI": "MSCI ACWI",
    "GSC": "MSCI ACWI Small Cap",
}

FACTOR_DISPLAY = {
    "Dividend Yield": "Dividend Yield", "Earnings Yield": "Earnings Yield",
    "Exchange Rate Sensitivity": "FX Sensitivity", "Growth": "Growth",
    "Leverage": "Leverage", "Liquidity": "Liquidity",
    "Market Sensitivity": "Market Sensitivity",
    "Medium-Term Momentum": "Momentum", "Profitability": "Profitability",
    "Size": "Size", "Value": "Value", "Volatility": "Volatility",
    "Market": "Market", "Industry": "Industry", "Country": "Country",
    "Currency": "Currency",
}


def pf(s):
    """Parse float, return None on empty/invalid."""
    if not s or not str(s).strip():
        return None
    try:
        v = float(str(s).strip())
        return None if v != v else v  # NaN check
    except (ValueError, TypeError):
        return None


def r2(v):
    return round(v, 2) if v is not None else None


def parse_date(s):
    """Parse date string like '1/30/2026' or '2/6/2026'."""
    if not s or not s.strip():
        return None
    return s.strip()


def parse(csv_path):
    """Parse the new-format FactSet CSV."""
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        file_header = next(reader)  # First row is file-level header
        for row in reader:
            rows.append(row)

    print(f"Read {len(rows)} data rows from {csv_path}")

    # Separate section headers from data rows
    section_headers = []
    data_rows = []
    for row in rows:
        if row[0] == "Section":
            section_headers.append(row)
        else:
            data_rows.append(row)

    print(f"Found {len(section_headers)} section headers, {len(data_rows)} data rows")

    # Build per-section-type column maps from headers
    # Identify header types by checking for distinctive columns
    riskm_header = None
    chars_header = None
    security_header = None
    weight_header = None  # For sectors, countries, regions, groups, ranks
    attrib_header = None  # 18 Style Snapshot

    for sh in section_headers:
        joined = "|".join(sh[7:50])
        if "Total Risk" in joined and "% Asset Specific" in joined:
            riskm_header = sh
        elif "Predicted Tracking Error" in joined and "# of Securities" in joined:
            chars_header = sh
        elif "Redwood GICS Sector" in joined:
            security_header = sh
        elif "Period End Date" in joined and "Compounded Factor Return" in joined:
            attrib_header = sh
        elif "W" in sh[8:9] and "Bench. Weight" in sh[9:10]:
            weight_header = sh  # Standard weight-based section

    # Initialize strategy data
    strategies = {}

    # Group data rows by section type and account
    for row in data_rows:
        section = row[0]
        acct = row[1]

        if acct not in ACCT_TO_ID:
            continue

        sid = ACCT_TO_ID[acct]
        if sid not in strategies:
            strategies[sid] = {
                "id": sid,
                "name": ACCT_TO_NAME.get(acct, acct),
                "benchmark": ACCT_TO_BENCHMARK.get(acct, ""),
                "sum": {"te": 0, "as": 0, "beta": 1, "h": 0, "bh": 0, "sr": None, "cash": 0},
                "hold": [], "sectors": [], "regions": [], "countries": [],
                "industries": [], "groups": [], "factors": [], "chars": [],
                "ranks": [], "unowned": [],
                "hist": {"sum": [], "fac": {}, "sec": {}},
            }

        s = strategies[sid]
        date = parse_date(row[7]) if len(row) > 7 else None

        # Route by section type
        if section == "RiskM":
            _handle_riskm(s, row, riskm_header)
        elif section == "Portfolio Characteristics":
            _handle_chars(s, row, chars_header)
        elif section == "Sector Weights":
            _handle_weight_section(s, "sectors", row, date)
        elif section == "Country":
            _handle_weight_section(s, "countries", row, date)
        elif section == "Region":
            _handle_weight_section(s, "regions", row, date)
        elif section == "Industry":
            _handle_weight_section(s, "industries", row, date)
        elif section == "Group":
            _handle_weight_section(s, "groups", row, date)
        elif section == "Overall":
            _handle_weight_section(s, "ranks", row, date)
        elif section in ("REV", "VAL", "QUAL"):
            _handle_weight_section(s, "ranks", row, date)
        elif section == "Security":
            _handle_security(s, row, date)
        elif section == "18 Style Snapshot":
            _handle_factor_attrib(s, row, attrib_header)

    # Post-process: pick most recent week for display, build history
    for sid, s in strategies.items():
        _finalize_strategy(s)

    return strategies


# ── 18-col weight group extraction ──────────────────────────────────────

def _get_weekly_groups(row):
    """Extract up to 5 weekly groups of 19 columns each (date + 18 metrics).
    Groups start at col 7 and repeat every 19 columns."""
    groups = []
    col = 7
    while col + 18 < len(row):
        date = parse_date(row[col])
        if not date:
            col += 19
            continue
        g = {
            "date": date,
            "w": pf(row[col + 1]),      # W (portfolio weight)
            "bw": pf(row[col + 2]),     # Bench. Weight
            "aw": pf(row[col + 3]),     # AW (active weight)
            "pct_s": pf(row[col + 4]),  # %S
            "pct_t": pf(row[col + 5]),  # %T
            "check": pf(row[col + 6]),  # %T_Check or %T-filter
            "over": pf(row[col + 7]),   # OVER_WAvg
            "rev": pf(row[col + 8]),    # REV_WAvg
            "val": pf(row[col + 9]),    # VAL_WAvg
            "qual": pf(row[col + 10]),  # QUAL_WAvg
            "mom": pf(row[col + 11]),   # MOM_WAvg
            "stab": pf(row[col + 12]),  # STAB_WAvg
        }
        groups.append(g)
        col += 19
    return groups


def _handle_weight_section(s, target, row, date):
    """Handle sector/country/region/industry/group/rank weight rows.
    Uses the LAST weekly group (most recent) for current display."""
    level2 = row[5] if len(row) > 5 else ""
    if not level2 or level2 == "Data":
        return  # Skip summary rows

    groups = _get_weekly_groups(row)
    if not groups:
        return

    # Use last group = most recent week
    g = groups[-1]

    entry = {
        "n": level2,
        # Dashboard reads p, b, a (v1 field names)
        "p": r2(g["w"]),
        "b": r2(g["bw"]),
        "a": r2(g["aw"]),
        "mcr": r2(g["pct_s"]),
        "tr": r2(g["pct_t"]),
        "over": r2(g["over"]),
        "rev": r2(g["rev"]),
        "val": r2(g["val"]),
        "qual": r2(g["qual"]),
        "mom": r2(g["mom"]),
        "stab": r2(g["stab"]),
    }

    target_list = s[target]
    # Avoid duplicates (same name)
    existing = next((x for x in target_list if x["n"] == level2), None)
    if not existing:
        target_list.append(entry)


# ── Security (holdings) ─────────────────────────────────────────────────

def _handle_security(s, row, date):
    """Handle individual holding rows. These have extra grouping columns."""
    ticker = row[5] if len(row) > 5 else ""
    name = row[6] if len(row) > 6 else ""

    if not ticker or ticker == "Data":
        return

    # Security section has grouping cols at 8-12, then weight groups start at 13
    sec = row[8] if len(row) > 8 else None   # Redwood GICS Sector
    reg = row[9] if len(row) > 9 else None   # Redwood Region1
    co = row[10] if len(row) > 10 else None  # Redwood Country
    ind = row[11] if len(row) > 11 else None  # Industry Rollup
    grp = row[12] if len(row) > 12 else None  # RWOOD_SUBGROUP

    # Weight groups start at col 13 for securities (after 5 grouping cols)
    groups = []
    col = 13
    while col + 18 < len(row):
        d = parse_date(row[col])
        if not d:
            col += 19
            continue
        g = {
            "date": d,
            "w": pf(row[col + 1]),
            "bw": pf(row[col + 2]),
            "aw": pf(row[col + 3]),
            "pct_s": pf(row[col + 4]),
            "pct_t": pf(row[col + 5]),
            "check": pf(row[col + 6]),
            "over": pf(row[col + 7]),
            "rev": pf(row[col + 8]),
            "val": pf(row[col + 9]),
            "qual": pf(row[col + 10]),
            "mom": pf(row[col + 11]),
            "stab": pf(row[col + 12]),
        }
        groups.append(g)
        col += 19

    if not groups:
        return

    # Use last group
    g = groups[-1]
    rank = g["over"]
    r_int = int(round(rank)) if rank is not None and 1 <= (rank or 0) <= 5 else None

    holding = {
        "t": ticker,
        "n": name if name else ticker,
        "sec": sec if sec and sec.strip() else None,
        "co": co if co and co.strip() else None,
        "reg": reg if reg and reg.strip() else None,
        "ind": ind if ind and ind.strip() else None,
        "grp": grp if grp and grp.strip() else None,
        # Dashboard v1 field names
        "p": r2(g["w"]),
        "b": r2(g["bw"]),
        "a": r2(g["aw"]),
        "mcr": r2(g["pct_s"]),   # %S → mcr
        "tr": r2(g["pct_t"]),    # %T → tr
        "r": r_int,               # overall rank → r
        "over": r2(g["over"]),
        "rev": r2(g["rev"]),
        "val": r2(g["val"]),
        "qual": r2(g["qual"]),
        "mom": r2(g["mom"]),
        "stab": r2(g["stab"]),
    }

    # Check if cash
    if ticker.startswith("CASH_"):
        s["sum"]["cash"] = (s["sum"].get("cash") or 0) + (holding["p"] or 0)
        return  # Don't add to holdings list

    s["hold"].append(holding)


# ── RiskM (risk decomposition + factor risks) ───────────────────────────

def _handle_riskm(s, row, header):
    """Handle RiskM rows — these have P/E, P/B, Total Risk, Beta,
    % Asset Specific, % Factor, and per-factor risk contributions."""
    if row[5] != "Data":
        return

    date = parse_date(row[7])

    # Map from header if available, else use known positions
    pe_p = pf(row[9])      # Price/Earnings
    pb_p = pf(row[10])     # Price/Book
    pe_b = pf(row[11])     # BMK Price/Earnings
    pb_b = pf(row[12])     # BMK Price/Book
    total_risk = pf(row[15])  # Total Risk
    bm_risk = pf(row[16])    # Benchmark Risk
    beta = pf(row[17])       # Predicted Beta
    pct_specific = pf(row[20])  # % Asset Specific Risk
    pct_factor = pf(row[21])    # % Factor Risk

    # Per-factor risk % contributions (cols 23-39)
    factor_risk = {}
    if header:
        for i in range(23, min(40, len(row))):
            if i < len(header) and header[i].strip() and pf(row[i]) is not None:
                fname = header[i].strip()
                if fname in FACTOR_DISPLAY:
                    factor_risk[FACTOR_DISPLAY[fname]] = pf(row[i])

    # Factor active exposures (cols 42-49)
    factor_exposure = {}
    if header:
        for i in range(43, min(50, len(row))):
            if i < len(header) and header[i].strip() and pf(row[i]) is not None:
                fname = header[i].strip()
                if fname in FACTOR_DISPLAY:
                    factor_exposure[FACTOR_DISPLAY[fname]] = pf(row[i])

    # Store the LATEST date's data in sum
    # (RiskM has one row per date — we want the most recent)
    if not s["sum"].get("_riskm_date") or (date and date > s["sum"].get("_riskm_date", "")):
        s["sum"]["te"] = r2(total_risk) if total_risk else s["sum"].get("te")
        s["sum"]["beta"] = r2(beta) if beta else s["sum"].get("beta")
        s["sum"]["pe_p"] = r2(pe_p)
        s["sum"]["pe_b"] = r2(pe_b)
        s["sum"]["pb_p"] = r2(pb_p)
        s["sum"]["pb_b"] = r2(pb_b)
        s["sum"]["pct_specific"] = r2(pct_specific)
        s["sum"]["pct_factor"] = r2(pct_factor)
        s["sum"]["total_risk"] = r2(total_risk)
        s["sum"]["bm_risk"] = r2(bm_risk)
        s["sum"]["_riskm_date"] = date
        s["sum"]["_factor_risk"] = factor_risk
        s["sum"]["_factor_exposure"] = factor_exposure

    # Build history
    s["hist"]["sum"].append({
        "d": date,
        "te": r2(total_risk),
        "beta": r2(beta),
        "pct_specific": r2(pct_specific),
        "pct_factor": r2(pct_factor),
    })


# ── Portfolio Characteristics ────────────────────────────────────────────

def _handle_chars(s, row, header):
    """Handle Portfolio Characteristics — TE, Beta, Active Share, etc.
    Has portfolio section (cols 7-25) and benchmark section (cols 26-44)."""
    if row[5] != "Data":
        return

    date = parse_date(row[7])

    # Portfolio section (P suffix in header)
    te = pf(row[10])       # Predicted Tracking Error
    beta_p = pf(row[11])   # Predicted Beta
    h = pf(row[12])        # # of Securities
    as_val = pf(row[13])   # Active Share
    mc = pf(row[14])       # Market Capitalization
    hist_beta = pf(row[16])  # Historical Beta
    mpt_beta = pf(row[17])  # MPT Beta
    epsg = pf(row[18])     # EPS Growth Hist 3Yr
    epsg_est = pf(row[19]) # EPS Growth Est 3-5Yr
    rev_3m = pf(row[20])   # 3M EPS Revisions FY1
    rev_6m = pf(row[21])   # 6M EPS Revisions FY1
    fcfy = pf(row[22])     # FCF Yield NTM
    divy = pf(row[23])     # Dividend Yield
    roe = pf(row[24])      # ROE NTM
    opmgn = pf(row[25])    # Operating Margin NTM

    # Benchmark section (B suffix, starts at col 26)
    bm_te = pf(row[30]) if len(row) > 30 else None
    bm_mc = pf(row[33]) if len(row) > 33 else None
    bm_fcfy = pf(row[38]) if len(row) > 38 else None
    bm_divy = pf(row[39]) if len(row) > 39 else None
    bm_roe = pf(row[40]) if len(row) > 40 else None
    bm_opmgn = pf(row[41]) if len(row) > 41 else None
    bm_epsg = pf(row[42]) if len(row) > 42 else None
    bm_rev_3m = pf(row[43]) if len(row) > 43 else None

    # Store most recent
    if not s["sum"].get("_chars_date") or (date and date > s["sum"].get("_chars_date", "")):
        if te is not None:
            s["sum"]["te"] = r2(te)
        if as_val is not None:
            s["sum"]["as"] = r2(as_val)
        if beta_p is not None:
            s["sum"]["beta"] = r2(beta_p)
        if h is not None:
            s["sum"]["h"] = int(h)
        s["sum"]["mc"] = r2(mc)
        s["sum"]["roe"] = r2(roe)
        s["sum"]["fcfy"] = r2(fcfy)
        s["sum"]["divy"] = r2(divy)
        s["sum"]["epsg"] = r2(epsg)
        s["sum"]["opmgn"] = r2(opmgn)
        s["sum"]["_chars_date"] = date

        # Betas
        s["sum"]["betas"] = {
            "predicted": r2(beta_p),
            "historical": r2(hist_beta),
            "mpt": r2(mpt_beta),
        }

        # Build chars array for the characteristics table
        s["chars"] = []
        char_pairs = [
            ("Market Cap ($M)", mc, bm_mc),
            ("P/E Ratio", s["sum"].get("pe_p"), s["sum"].get("pe_b")),
            ("P/B Ratio", s["sum"].get("pb_p"), s["sum"].get("pb_b")),
            ("ROE NTM (%)", roe, bm_roe),
            ("FCF Yield (%)", fcfy, bm_fcfy),
            ("Div Yield (%)", divy, bm_divy),
            ("EPS Growth 3Y (%)", epsg, bm_epsg),
            ("Op Margin (%)", opmgn, bm_opmgn),
        ]
        for m, p, b in char_pairs:
            s["chars"].append({"m": m, "p": r2(p), "b": r2(b)})

    # History
    s["hist"]["sum"].append({
        "d": date,
        "te": r2(te),
        "as": r2(as_val),
        "beta": r2(beta_p),
        "h": int(h) if h else None,
        "cash": s["sum"].get("cash"),
    })


# ── Factor Attribution (18 Style Snapshot) ───────────────────────────────

def _handle_factor_attrib(s, row, header):
    """Handle factor attribution rows from 18 Style Snapshot."""
    factor_name = row[5] if len(row) > 5 else ""
    if not factor_name or factor_name == "Data":
        return

    display_name = FACTOR_DISPLAY.get(factor_name, factor_name)

    # Find the last period's data (most recent)
    # Each period has 6 cols: start_date, end_date, avg_active_exp, comp_factor_ret, comp_factor_imp, factor_std_dev, cum_factor_imp
    # Periods start at col 7
    last_exp = None
    last_ret = None
    last_imp = None
    last_dev = None
    last_cimp = None

    col = 7
    while col + 6 < len(row):
        d = parse_date(row[col])
        if d:
            exp = pf(row[col + 2]) if col + 2 < len(row) else None
            ret = pf(row[col + 3]) if col + 3 < len(row) else None
            imp = pf(row[col + 4]) if col + 4 < len(row) else None
            dev = pf(row[col + 5]) if col + 5 < len(row) else None
            cimp = pf(row[col + 6]) if col + 6 < len(row) else None
            if exp is not None or ret is not None:
                last_exp = exp
                last_ret = ret
                last_imp = imp
                last_dev = dev
                last_cimp = cimp
        col += 7  # 7 cols per period (start, end, exp, ret, imp, dev, cimp)

    # Check if factor already exists (from RiskM)
    existing = next((f for f in s["factors"] if f["n"] == display_name), None)
    if existing:
        if last_exp is not None:
            existing["a"] = r2(last_exp)
        if last_ret is not None:
            existing["ret"] = r2(last_ret)
        if last_imp is not None:
            existing["imp"] = r2(last_imp)
    else:
        s["factors"].append({
            "n": display_name,
            "e": 0,  # portfolio exposure (filled from RiskM)
            "bm": 0,
            "a": r2(last_exp),  # active exposure
            "c": 0,  # TE contribution (filled from RiskM)
            "ret": r2(last_ret),
            "imp": r2(last_imp),
        })


# ── Finalize ─────────────────────────────────────────────────────────────

def _finalize_strategy(s):
    """Post-process: merge RiskM factor data, compute derived fields."""

    # Merge factor risk contributions from RiskM into factors
    factor_risk = s["sum"].pop("_factor_risk", {})
    factor_exposure = s["sum"].pop("_factor_exposure", {})

    for fname, risk_pct in factor_risk.items():
        existing = next((f for f in s["factors"] if f["n"] == fname), None)
        if existing:
            existing["c"] = r2(risk_pct)
        else:
            s["factors"].append({
                "n": fname, "e": 0, "bm": 0,
                "a": r2(factor_exposure.get(fname)),
                "c": r2(risk_pct), "ret": None, "imp": None,
            })

    for fname, exp in factor_exposure.items():
        existing = next((f for f in s["factors"] if f["n"] == fname), None)
        if existing and existing["a"] is None:
            existing["a"] = r2(exp)

    # Count holdings
    equity_hold = [h for h in s["hold"] if not (h["t"] or "").startswith("CASH")]
    s["sum"]["h"] = s["sum"].get("h") or len(equity_hold)

    # Benchmark holdings count (unowned with significant weight)
    bm_count = sum(1 for h in s["hold"] if (h.get("b") or 0) > 0 and (h.get("p") or 0) == 0)
    s["sum"]["bh"] = bm_count

    # Sort history by date
    s["hist"]["sum"].sort(key=lambda x: x.get("d") or "")
    # Remove duplicates
    seen = set()
    unique = []
    for h in s["hist"]["sum"]:
        if h["d"] not in seen:
            seen.add(h["d"])
            unique.append(h)
    s["hist"]["sum"] = unique

    # Clean up internal fields
    s["sum"].pop("_riskm_date", None)
    s["sum"].pop("_chars_date", None)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 factset_parser_v3.py <input.csv> [output.json]")
        sys.exit(1)

    csv_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else csv_path.replace(".csv", ".json")

    strategies = parse(csv_path)

    # Build output — strategies as DICT (keyed by ID) for dashboard compatibility
    output = {
        "generated": __import__("datetime").datetime.now().isoformat(),
        "parser_version": "3.0.0",
        "version": "4.0",
        "strategies": strategies,
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")
    print(f"Strategies: {list(strategies.keys())}")
    for sid, s in strategies.items():
        print(f"  {sid}: {len(s['hold'])} holdings  "
              f"TE={s['sum'].get('te')}  AS={s['sum'].get('as')}  "
              f"Beta={s['sum'].get('beta')}  "
              f"P/E={s['sum'].get('pe_p')} (BM:{s['sum'].get('pe_b')})  "
              f"Stock%={s['sum'].get('pct_specific')}  Factor%={s['sum'].get('pct_factor')}")


if __name__ == "__main__":
    main()
