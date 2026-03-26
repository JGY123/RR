#!/usr/bin/env python3
"""
FactSet Portfolio Attribution CSV Parser — Version 2
Section-driven rewrite for the new multi-section format.

Usage:
    python3 factset_parser_v2.py input.csv [output.json]
    python3 factset_parser_v2.py input.csv  → writes input_v2.json

Key changes from v1:
    - col[0] "Section" field routes every row (no column-count detection)
    - Explicit "Period Start Date" columns replace Friday-inference
    - Security rows now include per-holding sector/region/country/industry
    - BMK P/E and BMK P/B now available (from RiskM section)
    - Full benchmark characteristics for chars[] comparison
    - Industry section added to output

Output JSON is FORMAT_VERSION 4.0 — backward compatible with dashboard_v7.html.
"""

import csv
import json
import os
import sys
import time
from datetime import datetime

PARSER_VERSION = "2.0.0"
FORMAT_VERSION = "4.0"

# ── Strategy mapping ──────────────────────────────────────────────────────────
ACCT_MAP = {
    "IDM":     "IDM",
    "ACWIXUS": "IOP",
    "EM":      "EM",
    "ISC":     "ISC",
    "SCG":     "SCG",
    "ACWI":    "ACWI",
    "GSC":     "GSC",
}

# ── Factor definitions ────────────────────────────────────────────────────────
# Factor order in RiskM section: portfolio exposure at cols 23-39, active at 43-59
RISKM_FACTORS = [
    "Dividend Yield",
    "Earnings Yield",
    "Exchange Rate Sensitivity",
    "Growth",
    "Leverage",
    "Liquidity",
    "Market Sensitivity",
    "Medium-Term Momentum",
    "Profitability",
    "Size",
    "Value",
    "Volatility",
    "Market",
    "Local",          # new in v2 format — not shown in dashboard Factors tab
    "Industry",
    "Country",
    "Currency",
]

# Factors that map to old 16-factor list (exclude "Local")
STYLE_FACTORS = {f for f in RISKM_FACTORS if f != "Local"}

# Name mapping: new CSV name → old dashboard display name
FACTOR_DISPLAY_NAME = {
    "Medium-Term Momentum":    "Momentum (Medium-Term)",
    "Exchange Rate Sensitivity": "FX Sensitivity (Exchange Rate)",
}

# ── Column layout constants ───────────────────────────────────────────────────
# Standard sections (Sector Weights, Industry, Region, Country, Group, Overall, REV, VAL, QUAL)
# 5 groups; each group = 19 cols starting at date column
STD_DATE_COLS   = [7, 26, 45, 64, 83]   # period start date column for each group
STD_GROUP_SIZE  = 19

# Security section
# 5 groups; each group = 24 cols (1 date + 5 classification + 18 metrics)
SEC_DATE_COLS   = [7, 31, 55, 79, 103]
SEC_GROUP_SIZE  = 24

# 18 Style Snapshot
# 5 periods; each period = 7 cols
SNAP_DATE_COLS  = [7, 14, 21, 28, 35]
SNAP_GROUP_SIZE = 7

# RiskM column positions
RISKM_PE   = 9
RISKM_PB   = 10
RISKM_BPE  = 11
RISKM_BPB  = 12
RISKM_TOTAL_RISK  = 15
RISKM_BM_RISK     = 16
RISKM_PCT_SPEC    = 20
RISKM_PCT_FACTOR  = 21
RISKM_PORT_EXP_START   = 23   # Dividend Yield portfolio exposure
RISKM_ACTIVE_EXP_START = 43   # Dividend Yield active exposure

# Portfolio Characteristics column positions
PC_DATE    = 7
PC_TE      = 10
PC_BETA    = 11
PC_H       = 12
PC_AS      = 13
PC_MCAP    = 14
PC_EPSG    = 18
PC_EPSG_F  = 19
PC_EPS3M   = 20
PC_EPS6M   = 21
PC_FCFY    = 22
PC_DIVY    = 23
PC_ROE     = 24
PC_OPMGN   = 25
PC_BH      = 31
PC_BMCAP   = 33
PC_B_EPSG  = 37
PC_B_FCFY  = 41
PC_B_DIVY  = 42
PC_B_ROE   = 43
PC_B_OPMGN = 44

# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_float(s):
    """Return float or None for empty/non-numeric strings."""
    if not s or not s.strip():
        return None
    try:
        return float(s)
    except ValueError:
        return None

def parse_date(s):
    """Convert 'M/D/YYYY' → 'YYYYMMDD'. Returns None if unparseable."""
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%m/%d/%Y").strftime("%Y%m%d")
    except ValueError:
        return None

def date_key(mdY_str):
    """Return datetime for sort key. Handles M/D/YYYY format."""
    try:
        return datetime.strptime(mdY_str.strip(), "%m/%d/%Y")
    except (ValueError, AttributeError):
        return datetime.min

def _g_offset(date_cols, group_idx):
    """Return date-column start offset for group at 0-based group_idx."""
    return date_cols[group_idx]

# ── Main parser class ─────────────────────────────────────────────────────────

class FactSetParserV2:
    """Section-driven parser for the new FactSet CSV format."""

    def __init__(self):
        # dash_id → raw data buckets
        self._data = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def parse(self, csv_path):
        """
        Parse CSV and return (strategies, validation_issues, main_date, parse_stats).
        Matches the signature of factset_parser.py v1 for drop-in compatibility.
        """
        t0 = time.time()

        rows = self._read_csv(csv_path)
        if not rows:
            return {}, ["Empty or unreadable file"], None, {}

        for row in rows:
            if not row or not row[0]:
                continue
            section = row[0]
            if section == "Section":
                continue  # skip column-header rows

            acct = row[1] if len(row) > 1 else ""
            dash_id = ACCT_MAP.get(acct)
            if not dash_id:
                continue

            if dash_id not in self._data:
                self._data[dash_id] = self._init_bucket()

            bucket = self._data[dash_id]

            if section == "Sector Weights":
                self._handle_sector_weights(bucket, row)
            elif section == "RiskM":
                self._handle_riskm(bucket, row)
            elif section == "Portfolio Characteristics":
                self._handle_portfolio_chars(bucket, row)
            elif section == "Country":
                self._handle_standard_geo(bucket, row, "countries")
            elif section == "Region":
                self._handle_standard_geo(bucket, row, "regions")
            elif section == "Industry":
                self._handle_standard_geo(bucket, row, "industries")
            elif section == "Group":
                self._handle_standard_geo(bucket, row, "groups")
            elif section == "Security":
                self._handle_security(bucket, row)
            elif section in ("Overall", "REV", "VAL", "QUAL"):
                self._handle_quintile(bucket, row, section)
            elif section == "18 Style Snapshot":
                self._handle_style_snapshot(bucket, row)

        strategies, validation_issues = self._assemble()

        parse_stats = {
            "total_rows": len(rows),
            "file_size_mb": round(os.path.getsize(csv_path) / 1e6, 2),
            "parse_time_s": round(time.time() - t0, 2),
            "encoding": self._encoding_used,
            "strat_stats": {d: {"holds": len(s.get("hold", []))} for d, s in strategies.items()},
        }

        all_dates = [s["current_date"] for s in strategies.values() if s.get("current_date")]
        main_date = max(all_dates) if all_dates else None

        return strategies, validation_issues, main_date, parse_stats

    # ── Section handlers ──────────────────────────────────────────────────────

    def _handle_sector_weights(self, bucket, row):
        level2 = row[5]
        if level2 in ("Data", "@NA", "[Unassigned]"):
            return

        # [Cash] → capture cash weight from current group (group 5)
        if level2 == "[Cash]":
            dc = STD_DATE_COLS[-1]  # 83
            bucket["_cash"] = safe_float(row[dc + 1]) if len(row) > dc + 1 else None
            return

        # Regular sector row — collect all 5 period snapshots
        name = level2.strip()
        for gi, dc in enumerate(STD_DATE_COLS):
            if len(row) <= dc:
                continue
            d = parse_date(row[dc])
            if not d:
                continue
            w   = safe_float(row[dc + 1])
            bw  = safe_float(row[dc + 2])
            aw  = safe_float(row[dc + 3])

            if gi == 4:  # current (group 5)
                bucket["_sectors"].append({"n": name, "p": w, "b": bw, "a": aw})

            # All periods → hist.sec
            bucket["_hist_sec"].setdefault(name, []).append({"d": d, "p": w, "b": bw, "a": aw})

    def _handle_riskm(self, bucket, row):
        """RiskM: fundamental chars + factor exposures."""
        if row[5] != "Data":
            return
        d = parse_date(row[7]) if len(row) > 7 else None
        if not d:
            return

        entry = {
            "d":    d,
            "pe":   safe_float(row[RISKM_PE])   if len(row) > RISKM_PE   else None,
            "pb":   safe_float(row[RISKM_PB])   if len(row) > RISKM_PB   else None,
            "bpe":  safe_float(row[RISKM_BPE])  if len(row) > RISKM_BPE  else None,
            "bpb":  safe_float(row[RISKM_BPB])  if len(row) > RISKM_BPB  else None,
            "total_risk":   safe_float(row[RISKM_TOTAL_RISK])  if len(row) > RISKM_TOTAL_RISK  else None,
            "bm_risk":      safe_float(row[RISKM_BM_RISK])     if len(row) > RISKM_BM_RISK     else None,
            "pct_specific": safe_float(row[RISKM_PCT_SPEC])    if len(row) > RISKM_PCT_SPEC    else None,
            "pct_factor":   safe_float(row[RISKM_PCT_FACTOR])  if len(row) > RISKM_PCT_FACTOR  else None,
            "exposures": {},
        }

        # Factor exposures: portfolio (23-39) and active (43-59)
        for fi, fname in enumerate(RISKM_FACTORS):
            if fname == "Local":
                continue  # not in dashboard factor list
            pc = RISKM_PORT_EXP_START + fi
            ac = RISKM_ACTIVE_EXP_START + fi
            e  = safe_float(row[pc]) if len(row) > pc else None
            a  = safe_float(row[ac]) if len(row) > ac else None
            bm = (e - a) if (e is not None and a is not None) else None
            entry["exposures"][fname] = {"e": e, "bm": bm, "a": a}

        bucket["_riskm"].append(entry)

    def _handle_portfolio_chars(self, bucket, row):
        """Portfolio Characteristics: one row per period (vertical layout)."""
        if row[5] != "Data":
            return
        d = parse_date(row[PC_DATE]) if len(row) > PC_DATE else None
        if not d:
            return

        def g(col):
            return safe_float(row[col]) if len(row) > col else None

        entry = {
            "d":     d,
            "te":    g(PC_TE),
            "beta":  g(PC_BETA),
            "h":     g(PC_H),
            "as":    g(PC_AS),
            "mcap":  g(PC_MCAP),
            "epsg":  g(PC_EPSG),
            "fcfy":  g(PC_FCFY),
            "divy":  g(PC_DIVY),
            "roe":   g(PC_ROE),
            "opmgn": g(PC_OPMGN),
            # Benchmark characteristics
            "bh":     g(PC_BH),
            "bmcap":  g(PC_BMCAP),
            "b_epsg": g(PC_B_EPSG),
            "b_fcfy": g(PC_B_FCFY),
            "b_divy": g(PC_B_DIVY),
            "b_roe":  g(PC_B_ROE),
            "b_opmgn": g(PC_B_OPMGN),
        }
        bucket["_pc"].append(entry)

    def _handle_standard_geo(self, bucket, row, key):
        """Country, Region, Industry, Group — same layout as Sector Weights."""
        level2 = row[5]
        if level2 in ("Data", "@NA", "[Unassigned]", "[Cash]"):
            return
        name = level2.strip()
        dc = STD_DATE_COLS[-1]  # current group
        if len(row) <= dc + 2:
            return
        w   = safe_float(row[dc + 1])
        bw  = safe_float(row[dc + 2])
        aw  = safe_float(row[dc + 3]) if len(row) > dc + 3 else None
        if aw is None and w is not None and bw is not None:
            aw = w - bw
        bucket["_geo"].setdefault(key, []).append({"n": name, "p": w, "b": bw, "a": aw})

    def _handle_security(self, bucket, row):
        """Security (holdings) — 5 groups, each with classification + metrics."""
        level2 = row[5]
        name   = row[6].strip() if len(row) > 6 else ""

        # Skip currency cash positions
        if level2.startswith("CASH_"):
            return

        # Special aggregate rows — skip for holdings list
        if level2 in ("Data", "@NA", "[Unassigned]", "[Cash]"):
            return

        ticker = level2.strip()

        # Use current group (group 5, date at col 103)
        dc = SEC_DATE_COLS[-1]   # 103
        if len(row) <= dc + 23:
            return

        d   = parse_date(row[dc])
        sec = row[dc + 1].strip() or None   # Redwood GICS Sector
        reg = row[dc + 2].strip() or None   # Redwood Region1
        co  = row[dc + 3].strip() or None   # Redwood Country
        ind = row[dc + 4].strip() or None   # Industry Rollup
        subg= row[dc + 5].strip() or None   # RWOOD_SUBGROUP
        w   = safe_float(row[dc + 6])
        bw  = safe_float(row[dc + 7])
        aw  = safe_float(row[dc + 8])
        pct_s = safe_float(row[dc + 9])
        pct_t = safe_float(row[dc + 10])
        # dc+11 = %T_Check (inclusion flag)
        over  = safe_float(row[dc + 12])
        rev   = safe_float(row[dc + 13])
        val   = safe_float(row[dc + 14])
        qual  = safe_float(row[dc + 15])
        mom   = safe_float(row[dc + 16])
        stab  = safe_float(row[dc + 17])

        hold = {
            "n": name,
            "t": ticker,
            "sec": sec,
            "reg": reg,
            "co":  co,
            "ind": ind,
            "subg": subg,
            "w":    w,
            "bw":   bw,
            "aw":   aw,
            "pct_s": pct_s,
            "pct_t": pct_t,
            "over":  over,
            "rev":   rev,
            "val":   val,
            "qual":  qual,
            "mom":   mom,
            "stab":  stab,
        }
        bucket["_holds"].append(hold)

    def _handle_quintile(self, bucket, row, section_name):
        """Overall/REV/VAL/QUAL: quintile rank distributions."""
        level2 = row[5]
        # Only keep aggregate quintile bucket rows (no SecurityName)
        name = row[6].strip() if len(row) > 6 else ""
        if name:
            return  # individual holding row within a quintile bucket — skip

        dc = STD_DATE_COLS[-1]
        if len(row) <= dc + 1:
            return
        w  = safe_float(row[dc + 1])
        bw = safe_float(row[dc + 2]) if len(row) > dc + 2 else None
        aw = safe_float(row[dc + 3]) if len(row) > dc + 3 else None

        key = section_name.lower()  # "overall", "rev", "val", "qual"
        bucket["_quintiles"].setdefault(key, []).append({
            "q": level2.strip(),
            "w": w, "bw": bw, "aw": aw,
        })

    def _handle_style_snapshot(self, bucket, row):
        """18 Style Snapshot: factor attribution across 5 periods."""
        factor_raw = row[5].strip()
        if not factor_raw or factor_raw in ("Data", "@NA", "[Unassigned]"):
            return

        # Only collect style factors (skip country/industry/currency attribution)
        if factor_raw not in STYLE_FACTORS:
            return

        factor = FACTOR_DISPLAY_NAME.get(factor_raw, factor_raw)

        # Build per-period data
        periods = []
        for gi, dc in enumerate(SNAP_DATE_COLS):
            if len(row) <= dc + 6:
                continue
            d_start = parse_date(row[dc])
            d_end   = parse_date(row[dc + 1])
            exp  = safe_float(row[dc + 2])
            ret  = safe_float(row[dc + 3])
            imp  = safe_float(row[dc + 4])
            dev  = safe_float(row[dc + 5])
            cimp = safe_float(row[dc + 6])
            periods.append({
                "d_start": d_start, "d_end": d_end,
                "exp": exp, "ret": ret, "imp": imp, "dev": dev, "cimp": cimp,
            })

        bucket["_snapshot"].setdefault(factor, []).extend(periods)

    # ── Assembly ──────────────────────────────────────────────────────────────

    def _assemble(self):
        strategies = {}
        issues = []

        for dash_id, bucket in self._data.items():
            s = {}

            # ── Portfolio Characteristics (sorted by date) ────────────────────
            pc_rows = sorted(bucket["_pc"], key=lambda r: r["d"])
            current_pc = pc_rows[-1] if pc_rows else {}

            # ── RiskM (sorted by date, take most recent) ──────────────────────
            riskm_rows = sorted(bucket["_riskm"], key=lambda r: r["d"])
            current_rm = riskm_rows[-1] if riskm_rows else {}

            # ── summary (sum) ─────────────────────────────────────────────────
            s["sum"] = {
                "te":    current_pc.get("te"),
                "as":    current_pc.get("as"),
                "beta":  current_pc.get("beta"),
                "h":     current_pc.get("h"),
                "bh":    current_pc.get("bh"),
                "sr":    None,   # selection rate — not in new format
                "cash":  bucket.get("_cash"),
                "pe":    current_rm.get("pe"),
                "pb":    current_rm.get("pb"),
                "bpe":   current_rm.get("bpe"),   # NEW: benchmark P/E
                "bpb":   current_rm.get("bpb"),   # NEW: benchmark P/B
                "mcap":  current_pc.get("mcap"),
                "roe":   current_pc.get("roe"),
                "fcfy":  current_pc.get("fcfy"),
                "divy":  current_pc.get("divy"),
                "epsg":  current_pc.get("epsg"),
                "opmgn": current_pc.get("opmgn"),
                "total_risk":   current_rm.get("total_risk"),
                "bm_risk":      current_rm.get("bm_risk"),
                "pct_specific": current_rm.get("pct_specific"),
                "pct_factor":   current_rm.get("pct_factor"),
            }

            # ── Current date ──────────────────────────────────────────────────
            # Use the most recent date seen across Portfolio Characteristics
            if pc_rows:
                s["current_date"] = pc_rows[-1]["d"]
            else:
                s["current_date"] = None

            # ── available_dates (from Sector Weights — 5 per month) ───────────
            all_dates = sorted(set(
                e["d"]
                for entries in bucket["_hist_sec"].values()
                for e in entries
                if e.get("d")
            ))
            s["available_dates"] = all_dates

            # ── Holdings ──────────────────────────────────────────────────────
            s["hold"] = bucket["_holds"]

            # ── Sectors ───────────────────────────────────────────────────────
            s["sectors"] = bucket["_sectors"]

            # ── Geo sections ──────────────────────────────────────────────────
            geo = bucket["_geo"]
            s["countries"]  = geo.get("countries", [])
            s["regions"]    = geo.get("regions", [])
            s["industries"] = geo.get("industries", [])
            s["groups"]     = geo.get("groups", [])

            # ── Quintile distributions ────────────────────────────────────────
            s["ranks"] = bucket["_quintiles"]

            # ── Factors ───────────────────────────────────────────────────────
            # Combine RiskM exposure data with 18 Style Snapshot attribution
            riskm_exp = current_rm.get("exposures", {})
            snapshot  = bucket["_snapshot"]

            factors = []
            for fname_raw in RISKM_FACTORS:
                if fname_raw == "Local":
                    continue
                display = FACTOR_DISPLAY_NAME.get(fname_raw, fname_raw)
                exp_data = riskm_exp.get(fname_raw, {})

                # Attribution from 18 Style Snapshot period 5 (cumulative)
                snap_periods = snapshot.get(display, [])
                snap_current = snap_periods[4] if len(snap_periods) >= 5 else (snap_periods[-1] if snap_periods else {})

                factors.append({
                    "n":    display,
                    "e":    exp_data.get("e"),
                    "bm":   exp_data.get("bm"),
                    "a":    exp_data.get("a"),
                    "ret":  snap_current.get("ret"),
                    "imp":  snap_current.get("imp"),
                    "dev":  snap_current.get("dev"),
                    "cimp": snap_current.get("cimp"),
                })
            s["factors"] = factors

            # ── Characteristics (chars) ───────────────────────────────────────
            # Now fully populated with benchmark data
            chars = [
                {
                    "m": "Tracking Error (%)", "p": s["sum"].get("te"), "b": None,
                    "a": None,
                },
                {
                    "m": "Beta", "p": s["sum"].get("beta"), "b": 1.0,
                    "a": _sub(s["sum"].get("beta"), 1.0),
                },
                {
                    "m": "Active Share (%)", "p": s["sum"].get("as"), "b": None, "a": None,
                },
                {
                    "m": "Market Cap ($M)", "p": current_pc.get("mcap"), "b": current_pc.get("bmcap"),
                    "a": _sub(current_pc.get("mcap"), current_pc.get("bmcap")),
                },
                {
                    "m": "Price/Earnings (P/E)", "p": current_rm.get("pe"), "b": current_rm.get("bpe"),
                    "a": _sub(current_rm.get("pe"), current_rm.get("bpe")),
                },
                {
                    "m": "Price/Book (P/B)", "p": current_rm.get("pb"), "b": current_rm.get("bpb"),
                    "a": _sub(current_rm.get("pb"), current_rm.get("bpb")),
                },
                {
                    "m": "ROE - NTM", "p": current_pc.get("roe"), "b": current_pc.get("b_roe"),
                    "a": _sub(current_pc.get("roe"), current_pc.get("b_roe")),
                },
                {
                    "m": "FCF Yield - NTM", "p": current_pc.get("fcfy"), "b": current_pc.get("b_fcfy"),
                    "a": _sub(current_pc.get("fcfy"), current_pc.get("b_fcfy")),
                },
                {
                    "m": "Dividend Yield", "p": current_pc.get("divy"), "b": current_pc.get("b_divy"),
                    "a": _sub(current_pc.get("divy"), current_pc.get("b_divy")),
                },
                {
                    "m": "EPS Growth 3Yr", "p": current_pc.get("epsg"), "b": current_pc.get("b_epsg"),
                    "a": _sub(current_pc.get("epsg"), current_pc.get("b_epsg")),
                },
                {
                    "m": "Operating Margin - NTM", "p": current_pc.get("opmgn"), "b": current_pc.get("b_opmgn"),
                    "a": _sub(current_pc.get("opmgn"), current_pc.get("b_opmgn")),
                },
            ]
            s["chars"] = chars

            # ── Historical data ───────────────────────────────────────────────
            # hist.summary: one entry per Portfolio Characteristics row
            hist_summary = []
            for pc in pc_rows:
                hist_summary.append({
                    "d":    pc["d"],
                    "te":   pc.get("te"),
                    "as":   pc.get("as"),
                    "beta": pc.get("beta"),
                    "h":    pc.get("h"),
                    "sr":   None,
                    "cash": bucket.get("_cash") if pc["d"] == (pc_rows[-1]["d"] if pc_rows else None) else None,
                })
            s["hist"] = {
                "summary": hist_summary,
                "sec":     bucket["_hist_sec"],
                "fac":     self._build_hist_fac(riskm_rows, bucket["_snapshot"]),
            }

            strategies[dash_id] = s

        return strategies, issues

    def _build_hist_fac(self, riskm_rows, snapshot):
        """Build hist.fac: factor_name → [{d, e, bm}, ...] from RiskM rows."""
        hist_fac = {}
        for rm in riskm_rows:
            d = rm["d"]
            for fname_raw, exp_data in rm.get("exposures", {}).items():
                display = FACTOR_DISPLAY_NAME.get(fname_raw, fname_raw)
                hist_fac.setdefault(display, []).append({
                    "d":  d,
                    "e":  exp_data.get("e"),
                    "bm": exp_data.get("bm"),
                })
        return hist_fac

    # ── CSV reading ───────────────────────────────────────────────────────────

    def _read_csv(self, path):
        self._encoding_used = "utf-8-sig"
        for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                with open(path, encoding=enc, newline="") as f:
                    rows = list(csv.reader(f))
                self._encoding_used = enc
                return rows
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        return []

    @staticmethod
    def _init_bucket():
        return {
            "_sectors":  [],
            "_holds":    [],
            "_pc":       [],
            "_riskm":    [],
            "_geo":      {},
            "_quintiles": {},
            "_snapshot": {},
            "_hist_sec": {},
            "_cash":     None,
        }


# ── Utility ───────────────────────────────────────────────────────────────────

def _sub(a, b):
    """Return a - b, or None if either is None."""
    if a is not None and b is not None:
        return round(a - b, 6)
    return None


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 factset_parser_v2.py input.csv [output.json]")
        sys.exit(1)

    csv_path = sys.argv[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        base = os.path.splitext(csv_path)[0]
        out_path = base + "_v2.json"

    parser = FactSetParserV2()
    strategies, issues, main_date, stats = parser.parse(csv_path)

    if not strategies:
        print("ERROR: No strategies extracted.", issues)
        sys.exit(1)

    output = {
        "format_version":  FORMAT_VERSION,
        "parser_version":  PARSER_VERSION,
        "report_date":     main_date,
        "strategies":      strategies,
    }

    with open(out_path, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Parsed {stats.get('total_rows', '?')} rows in {stats.get('parse_time_s', '?')}s "
          f"({stats.get('file_size_mb', '?')} MB input → {size_kb:.0f} KB output)")
    print(f"Strategies: {list(strategies.keys())}")
    for sid, s in strategies.items():
        hold_ct = len(s.get("hold", []))
        te      = s["sum"].get("te")
        pe      = s["sum"].get("pe")
        bpe     = s["sum"].get("bpe")
        print(f"  {sid}: {hold_ct} holdings  TE={te}  P/E={pe}  BMK P/E={bpe}")
    if issues:
        print(f"Validation issues: {issues}")
    print(f"Output: {out_path}")

    return output


if __name__ == "__main__":
    main()


# ── APPEND / MERGE MODE ──────────────────────────────────────────────────────
# Usage:
#   First load:    python3 factset_parser_v2.py full_history.csv latest_data.json
#   Weekly append:  python3 factset_parser_v2.py new_week.csv latest_data.json --append
#   New account:    python3 factset_parser_v2.py new_acct.csv latest_data.json --append

def merge_data(existing_path, new_data):
    """Merge new parsed data into existing JSON file.
    
    - New strategies are added
    - Existing strategies: new holdings/sectors/factors REPLACE current
    - History entries are APPENDED (deduplicated by date)
    """
    import json
    
    with open(existing_path) as f:
        existing = json.load(f)
    
    ex_strats = existing.get('strategies', {})
    new_strats = new_data.get('strategies', {})
    
    for sid, new_s in new_strats.items():
        if sid not in ex_strats:
            # Brand new account — add entirely
            ex_strats[sid] = new_s
            print(f"  + Added new strategy: {sid}")
            continue
        
        ex_s = ex_strats[sid]
        
        # Replace current snapshot with newest data
        ex_s['sum'] = new_s['sum']
        ex_s['hold'] = new_s['hold']
        ex_s['sectors'] = new_s['sectors']
        ex_s['regions'] = new_s['regions']
        ex_s['countries'] = new_s['countries']
        ex_s['industries'] = new_s.get('industries', [])
        ex_s['groups'] = new_s.get('groups', [])
        ex_s['factors'] = new_s['factors']
        ex_s['chars'] = new_s['chars']
        ex_s['ranks'] = new_s.get('ranks', [])
        
        # Append history (deduplicate by date)
        ex_hist = ex_s.get('hist', {})
        new_hist = new_s.get('hist', {})
        
        # Summary history
        ex_sum = {h['d']: h for h in ex_hist.get('sum', [])}
        for h in new_hist.get('sum', []):
            ex_sum[h['d']] = h  # overwrite if same date
        ex_hist['sum'] = sorted(ex_sum.values(), key=lambda x: x.get('d', ''))
        
        # Factor history
        ex_fac = ex_hist.get('fac', {})
        new_fac = new_hist.get('fac', {})
        for fname, entries in new_fac.items():
            if fname not in ex_fac:
                ex_fac[fname] = entries
            else:
                ex_dates = {e['d']: e for e in ex_fac[fname]}
                for e in entries:
                    ex_dates[e['d']] = e
                ex_fac[fname] = sorted(ex_dates.values(), key=lambda x: x.get('d', ''))
        ex_hist['fac'] = ex_fac
        
        # Sector history
        ex_sec = ex_hist.get('sec', {})
        new_sec = new_hist.get('sec', {})
        for sname, entries in new_sec.items():
            if sname not in ex_sec:
                ex_sec[sname] = entries
            else:
                ex_dates = {e['d']: e for e in ex_sec[sname]}
                for e in entries:
                    ex_dates[e['d']] = e
                ex_sec[sname] = sorted(ex_dates.values(), key=lambda x: x.get('d', ''))
        ex_hist['sec'] = ex_sec
        
        ex_s['hist'] = ex_hist
        print(f"  ↻ Updated {sid}: {len(ex_hist.get('sum', []))} history entries")
    
    existing['strategies'] = ex_strats
    
    with open(existing_path, 'w') as f:
        json.dump(existing, f, separators=(',', ':'))
    
    print(f"\n✓ Merged into {existing_path}")
    print(f"  Strategies: {list(ex_strats.keys())}")
    total_hist = sum(len(s.get('hist', {}).get('sum', [])) for s in ex_strats.values())
    print(f"  Total history entries: {total_hist}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 factset_parser_v2.py input.csv output.json          # Full parse")
        print("  python3 factset_parser_v2.py new_data.csv existing.json --append  # Append/merge")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_json = sys.argv[2]
    append_mode = '--append' in sys.argv
    
    # Parse the CSV
    parser = FactSetParserV2()
    result = parser.parse(input_csv)
    
    if append_mode:
        import os
        if not os.path.exists(output_json):
            print(f"No existing file at {output_json} — creating fresh")
            append_mode = False
    
    if append_mode:
        merge_data(output_json, result)
    else:
        import json
        with open(output_json, 'w') as f:
            json.dump(result, f, separators=(',', ':'))
        print(f"Output: {output_json}")
