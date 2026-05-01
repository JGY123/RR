#!/usr/bin/env python3
"""
FactSet Portfolio Attribution CSV Parser — Version 3 (header-driven).

Key differences from v2:
    - NO hard-coded column positions anywhere.
    - First pass builds a schema from Section header rows; second pass extracts
      data by canonical field name via the schema.
    - Wildcard column families (e.g. "% Factor Contr. to Tot. Risk:*") auto-capture
      into sub-dicts on each holding — any future factor columns become data
      without parser changes.
    - Portfolio Characteristics is fully dynamic: every :P / :B column pair in
      the header becomes a char row automatically.
    - RiskM factor list is read from the header, not hard-coded.
    - Handles both the old wide 3-year file (158 periods) and the new April
      sample (4 periods + new factor columns) from the same code path.
    - Unknown columns in Security and PortChars are preserved under `_extra`.

Usage:
    python3 factset_parser_v3.py input.csv [output.json]
    python3 factset_parser_v3.py input.csv  → writes input_v3.json

Output JSON shape matches v2 (FORMAT_VERSION 4.1 — same consumers, new fields).
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime

PARSER_VERSION = "3.1.0"
FORMAT_VERSION = "4.2"

# ── Strategy code → dashboard ID mapping ─────────────────────────────────────
# Only ACWIXUS gets renamed (to IOP). Anything else passes through unchanged —
# so new US-only accounts with arbitrary codes just show up in the output as-is.
STRATEGY_RENAME = {
    "ACWIXUS": "IOP",
}

# ── Canonical field names and alias map ──────────────────────────────────────
# Any raw column name not in ALIASES passes through unchanged.
# Alias mapping folds FactSet spelling/punctuation variants into one canonical key.
ALIASES = {
    # Weight / risk
    "W": "W",
    "Bench. Weight": "BW",
    "AW": "AW",
    "%S": "PCT_S",
    "%T": "PCT_T",
    "%T_Check": "T_CHECK",
    "%T-filter": "T_CHECK",
    # Rank WAvg (weighted average)
    "OVER_WAvg": "OVER_WAVG",
    "Over_WAvg": "OVER_WAVG",
    "REV_WAvg":  "REV_WAVG",
    "VAL_WAvg":  "VAL_WAVG",
    "QUAL_WAvg": "QUAL_WAVG",
    "QUAL_WA":   "QUAL_WAVG",
    "MOM_WAvg":  "MOM_WAVG",
    "STAB_WAvg": "STAB_WAVG",
    # Rank Avg (simple average)
    "OVER_Avg": "OVER_AVG",
    "REV_Avg":  "REV_AVG",
    "VAL_Avg":  "VAL_AVG",
    "Val_Avg":  "VAL_AVG",
    "QUAL_Avg": "QUAL_AVG",
    "Qual_Avg": "QUAL_AVG",
    "MOM_Avg":  "MOM_AVG",
    "STAB_Avg": "STAB_AVG",
    # Period dates (group marker)
    "Period Start Date": "PERIOD_START",
    "Period End Date":   "PERIOD_END",
    # Security-only classification cols
    "Redwood GICS Sector": "SEC_GICS",
    "Redwood Region":      "SEC_REGION",   # 2026-04-30: was "Redwood Region1" — fixed; EM full-history ships header without trailing "1"
    "Redwood Region1":     "SEC_REGION",   # legacy variant (some files used this header)
    "Redwood Country":     "SEC_COUNTRY",
    "Industry Rollup":     "SEC_INDUSTRY",
    "RWOOD_SUBGROUP":      "SEC_SUBGROUP",
    # 18 Style Snapshot
    "Average Active Exposure":    "SNAP_EXP",
    "Compounded Factor Return":   "SNAP_RET",
    "Compounded Factor Impact":   "SNAP_IMP",
    "Factor Standard Deviation":  "SNAP_DEV",
    "Cumulative_Factor_Impact":   "SNAP_CIMP",
    "% Factor Contr. to Tot. Risk": "SNAP_RISK_CONTR",
    # 18 Style Snapshot — NEW fields shipped 2026-04-28 (FactSet folded RiskM into 18 Style):
    "Axioma- Benchmark Exposure": "SNAP_BENCH_EXP",
    "% Specific Risk":            "SNAP_PCT_SPEC",
    "% Factor Risk":              "SNAP_PCT_FAC",
    # Period delimiter inside each group
    "Period End Date":            "PERIOD_END",
    # Security section — NEW fields shipped 2026-04-28
    "Market Capitalization":      "SEC_MCAP",
    "Price Volatility":           "SEC_PRICE_VOL",
    "Vol 30D Avg":                "SEC_VOL_30D",
    # Raw Factors — NEW SEDOLCHK identifier shipped 2026-04-28
    "SEDOLCHK":                   "SEDOLCHK",
    # Fixed prefix (outside repeating group)
    "Section": "SECTION",
    "ACCT":    "ACCT",
    "DATE":    "DATE",
    "PortfolioCurCode": "CURRENCY",
    "Level":   "LEVEL",
    "Level2":  "LEVEL2",
    "SecurityName": "SECURITY_NAME",
}

# ── Wildcard prefixes for Security section ───────────────────────────────────
# Any Security column whose name starts with one of these prefixes is auto-captured
# into the named sub-dict on the holding, keyed by the text after the prefix.
# Adding a new wildcard is the ONLY change needed when FactSet introduces a new
# factor column family.
SECURITY_WILDCARDS = [
    # (prefix,                                dict name on holding)
    ("% Factor Contr. to Tot. Risk:",         "factor_contr"),
    # Raw factor exposure — exact FactSet prefix TBD; update when real file arrives
    ("Factor Exposure:",                      "factor_exp"),
    ("Active Factor Exposure:",               "factor_active"),
    ("Factor Return:",                        "factor_ret"),
    ("Factor Impact:",                        "factor_imp"),
    ("Factor MCR:",                           "factor_mcr"),
]

GROUP_MARKER = "Period Start Date"
FIXED_PREFIX_NAMES = {"Section", "ACCT", "DATE", "PortfolioCurCode", "Level", "Level2", "SecurityName"}

# ── Raw Factors positional order ─────────────────────────────────────────────
# The "Raw Factors" section ships 12 per-security z-score columns per period
# with NO distinct header labels (all 12 cols read "Raw Factor Exposure").
# Positional order is alphabetical and confirmed by user (2026-04-24).
# If FactSet ever supplies distinct header labels in future files, honor them —
# see _extract_raw_factors for the fallback path.
RAW_FACTOR_ORDER = [
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
]

# ── Security reference (static country/currency/industry lookup) ─────────────
# Baked from security_flags_source.xlsx; 97% coverage of new-format CSV SEDOLs.
# Emits country/currency/industry onto each holding so the dashboard can
# decompose risk by dimension without a separate runtime lookup.
_SECURITY_REF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "security_ref.json"
)
_SECURITY_REF = {}
_SECURITY_REF_BY_NAME = {}
_SECURITY_REF_META = {}
try:
    with open(_SECURITY_REF_PATH) as _f:
        _sr_raw = json.load(_f)
    _SECURITY_REF = _sr_raw.get("by_sedol", {}) or {}
    _SECURITY_REF_META = _sr_raw.get("meta", {}) or {}
    for _k, _v in _SECURITY_REF.items():
        _nn = re.sub(r"[^a-z0-9]", "", (_v.get("n") or "").lower())[:30]
        if _nn:
            _SECURITY_REF_BY_NAME.setdefault(_nn, _v)
except (FileNotFoundError, json.JSONDecodeError):
    pass


def _enrich_holding(h):
    """Attach country / currency / industry from security_ref lookup.

    Tries SEDOL (h['t']) direct, then SEDOL with leading zeros stripped,
    then a lowercase-alphanumeric-first-30-chars name fallback. On miss,
    leaves fields absent so the dashboard can fall back to CSV-native sec/co."""
    if not _SECURITY_REF:
        return h
    key = (h.get("t") or "").upper()
    ref = _SECURITY_REF.get(key) or _SECURITY_REF.get(key.lstrip("0"))
    if not ref:
        nn = re.sub(r"[^a-z0-9]", "", (h.get("n") or "").lower())[:30]
        if nn:
            ref = _SECURITY_REF_BY_NAME.get(nn)
    if ref:
        h["country"] = ref.get("country")
        h["currency"] = ref.get("ccy")
        h["industry"] = ref.get("industry")
    return h

# GICS industry reclassification (unify old and new names)
GICS_NAME_MAP = {
    "Retailing": "Consumer Discretionary Distribution & Retail",
    "Media": "Media & Entertainment",
    "Commercial Services & Supplies": "Commercial & Professional Services",
    "Pharmaceuticals, Biotechnology & Life Sciences": "Pharmaceuticals Biotechnology & Life Sciences",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_float(s):
    """Return float or None for empty / non-numeric."""
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if not s: return None
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None

def parse_date(s):
    """Normalize a date string to YYYYMMDD, handling multiple FactSet formats.

    2026-04-30: EM full-history file ships per-period dates as
    "2019-01-01 00:00:00" (ISO datetime with zero time component) — added
    that format to the list. Without it, the parser fell back to the file's
    run-date column, stamping every weekly hist entry with the same date and
    making the week-selector / time-series charts unusable. Truncating to the
    leading 10 chars BEFORE the format match also catches any future variant
    that has trailing time / timezone garbage.
    """
    if not s:
        return None
    s = str(s).strip()
    if not s:
        return None
    # Try as-is first (covers all the legacy formats)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%Y%m%d", "%d-%b-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    # Last resort: take leading 10 chars and try YYYY-MM-DD
    if len(s) >= 10:
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            pass
    return None

def _sub(a, b):
    if a is None or b is None:
        return None
    try:
        return round(float(a) - float(b), 4)
    except (TypeError, ValueError):
        return None

def _alias(raw):
    """Map a raw column name to its canonical form. Unknown names pass through."""
    return ALIASES.get(raw, raw)

def _match_wildcard(raw_name):
    """If a Security column matches a wildcard prefix, return (dict_name, suffix).
    Otherwise return (None, None)."""
    for prefix, dict_name in SECURITY_WILDCARDS:
        if raw_name.startswith(prefix):
            return dict_name, raw_name[len(prefix):].strip()
    return None, None


# ── Schema representation ────────────────────────────────────────────────────

class SectionSchema:
    """Schema for one section, built from its Section header row.

    Detection rule for horizontal vs vertical sections:
    - HORIZONTAL: "Period Start Date" appears 2+ times (repeating weekly groups)
    - VERTICAL: 0 or 1 occurrences — the section has one row per period and
      every named column after the prefix is a distinct field (RiskM, PortChars)
    """

    def __init__(self, section_name, header_row):
        self.section_name = section_name
        self.total_cols = len(header_row)
        self.raw_cols = [c.strip() for c in header_row]

        # Fixed prefix columns (0-6 usually): canonical name → col index
        self.fixed = {}
        for i, name in enumerate(self.raw_cols[:7]):
            if name in FIXED_PREFIX_NAMES:
                self.fixed[_alias(name)] = i

        # Find every occurrence of the GROUP_MARKER
        group_starts = [i for i, name in enumerate(self.raw_cols) if name == GROUP_MARKER]

        # Horizontal if and only if there are 2+ repeating groups
        is_horizontal = len(group_starts) >= 2
        if is_horizontal:
            self.group_start = group_starts[0]
            self.group_size = group_starts[1] - group_starts[0]
            self.num_groups = len(group_starts)
        else:
            # Vertical section: all fields after the fixed prefix are individual cols
            self.group_start = None
            self.group_size = 0
            self.num_groups = 0

        # Between = all non-repeating cols after the fixed prefix.
        # For vertical sections this is everything from col 7 to end.
        # For horizontal sections this is anything between col 7 and group_start.
        self.between = {}      # canonical → col index
        self.between_raw = {}  # raw name → col index
        end_of_prefix = 7
        end_of_between = self.group_start if is_horizontal else self.total_cols
        for i in range(end_of_prefix, end_of_between):
            name = self.raw_cols[i]
            if not name:
                continue
            self.between_raw[name] = i
            self.between[_alias(name)] = i

        # Per-group column map (only populated for horizontal sections)
        self.group_cols = {}      # canonical → offset
        self.group_raw_cols = {}  # raw name → offset (for wildcard scanning)
        if is_horizontal:
            start = self.group_start
            end = min(start + self.group_size, self.total_cols)
            for i in range(start, end):
                name = self.raw_cols[i]
                if not name:
                    continue
                offset = i - start
                self.group_raw_cols[name] = offset
                self.group_cols[_alias(name)] = offset

    def group_col_index(self, canonical, group_index):
        if self.group_start is None or canonical not in self.group_cols:
            return None
        return self.group_start + group_index * self.group_size + self.group_cols[canonical]

    def num_groups_for_row(self, row):
        """How many complete groups actually fit in this specific row.

        2026-05-01 (jagged-CSV fix): different ACCT rows can have different
        widths (e.g. master CSV: header=9493 cols → 527 groups; IDM rows=11149
        cols → 619 groups; ACWI rows=9979 cols → 554 groups). Iterating with
        schema.num_groups overcounts for narrower rows (reads garbage/None
        past actual data) and undercounts for wider rows (drops trailing
        weeks). Use this method per-row to iterate only real groups.
        """
        if self.group_start is None or self.group_size <= 0:
            return 0
        row_groups = max(0, (len(row) - self.group_start) // self.group_size)
        return min(row_groups, self.num_groups)

    def get_group_value(self, row, canonical, group_index):
        col = self.group_col_index(canonical, group_index)
        if col is None or col >= len(row):
            return None
        return row[col]


# ── Main parser ──────────────────────────────────────────────────────────────

class FactSetParserV3:

    def __init__(self, path):
        self.path = path
        self.rows = []
        self.schemas = {}       # section_name → SectionSchema
        self.section_rows = {}  # section_name → list of data rows
        self._encoding_used = None
        self.stats = {
            "parser_version": PARSER_VERSION,
            "format_version": FORMAT_VERSION,
            "total_rows": 0,
            "file_size_mb": 0,
            "parse_time_s": 0,
            "encoding": None,
            "schemas_discovered": {},
            "rows_per_section": {},
        }

    # ------------------------------------------------------------ loading

    def _load(self):
        for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                with open(self.path, encoding=enc, newline="") as f:
                    self.rows = list(csv.reader(f))
                self._encoding_used = enc
                self.stats["encoding"] = enc
                return
            except UnicodeDecodeError:
                continue
        raise RuntimeError(f"Could not read {self.path} with any supported encoding")

    # -------------------------------------------------- schema discovery

    def _discover_schemas(self):
        """First pass: walk rows, find Section headers, build a schema for every
        data section encountered."""
        last_header = None
        for row in self.rows:
            if len(row) < 2:
                continue
            first = row[0].strip()
            if first == "Section":
                last_header = row
                continue
            if first and first not in self.schemas and last_header is not None:
                self.schemas[first] = SectionSchema(first, last_header)
                self.stats["schemas_discovered"][first] = {
                    "total_cols": self.schemas[first].total_cols,
                    "group_size": self.schemas[first].group_size,
                    "num_groups": self.schemas[first].num_groups,
                    "group_cols": len(self.schemas[first].group_cols),
                }
            if first and first != "Section":
                self.section_rows.setdefault(first, []).append(row)

        # 2026-05-01 (jagged-CSV fix): the Section header line sometimes has
        # FEWER "Period Start Date" markers than the longest data row holds
        # (observed in master CSV: header=9493 cols, IDM rows=11149 cols → 92
        # weeks of trailing data silently dropped; ACWI rows=9979 cols → 27
        # weeks dropped). Bump schema.num_groups to the max data-row width
        # so the SCHEMA covers the longest row, then iterate per-row using
        # schema.num_groups_for_row(row) which clamps to that specific row's
        # actual width — this way ACWI's narrower rows don't read garbage
        # past their data while IDM's wider rows recover the trailing weeks.
        for sec_name, schema in self.schemas.items():
            if schema.group_size <= 0 or schema.group_start is None:
                continue
            rows = self.section_rows.get(sec_name, [])
            if not rows:
                continue
            header_groups = schema.num_groups
            max_groups = max(
                (len(r) - schema.group_start) // schema.group_size
                for r in rows
            )
            if max_groups > header_groups:
                schema.num_groups = max_groups
                schema.total_cols = max(
                    schema.total_cols,
                    schema.group_start + max_groups * schema.group_size,
                )
                self.stats.setdefault("jagged_section_bump", {})[sec_name] = {
                    "header_num_groups": header_groups,
                    "row_num_groups": max_groups,
                    "weeks_recovered": max_groups - header_groups,
                }
                if sec_name in self.stats.get("schemas_discovered", {}):
                    self.stats["schemas_discovered"][sec_name]["num_groups"] = max_groups

    # ---------------------------------------------------------- extractors

    def _iter_strategies(self):
        """Every strategy code seen in any data row."""
        seen = set()
        for rows in self.section_rows.values():
            for row in rows:
                if len(row) > 1:
                    acct = row[1].strip()
                    if acct and acct != "ACCT":
                        seen.add(acct)
        return sorted(seen)

    def _dash_id(self, acct_code):
        return STRATEGY_RENAME.get(acct_code, acct_code)

    # -------- Portfolio Characteristics (fully dynamic :P / :B pairing)

    def _extract_port_chars(self, acct_code):
        """Dynamic extraction — every :P/:B pair in the header becomes a metric."""
        rows = self.section_rows.get("Portfolio Characteristics", [])
        schema = self.schemas.get("Portfolio Characteristics")
        if not schema or not rows:
            return [], []

        # Build metric → (p_col, b_col) pairing from raw header names
        pairs = {}  # metric_name → [p_col, b_col]
        solo  = {}  # non-paired cols
        for raw_name, col in schema.between_raw.items():
            if raw_name.endswith(":P"):
                metric = raw_name[:-2].strip()
                pairs.setdefault(metric, [None, None])[0] = col
            elif raw_name.endswith(":B"):
                metric = raw_name[:-2].strip()
                pairs.setdefault(metric, [None, None])[1] = col
            else:
                solo[raw_name] = col

        # Extract per-period rows for this account
        out = []
        for row in rows:
            if len(row) < 2 or row[1].strip() != acct_code:
                continue
            if len(row) > 5 and row[5].strip() != "Data":
                continue
            # Date: first prefer the :P Period Start Date, then fall back to fixed DATE col
            d = None
            ps_col = pairs.get("Period Start Date", [None, None])[0]
            if ps_col is not None and ps_col < len(row):
                d = parse_date(row[ps_col])
            if not d and "DATE" in schema.fixed:
                d = parse_date(row[schema.fixed["DATE"]])
            entry = {"d": d, "_metrics": {}, "_extra": {}}
            for metric, (pc, bc) in pairs.items():
                if metric == "Period Start Date":
                    continue
                p = safe_float(row[pc]) if pc is not None and pc < len(row) else None
                b = safe_float(row[bc]) if bc is not None and bc < len(row) else None
                entry["_metrics"][metric] = {"p": p, "b": b}
            for raw_name, col in solo.items():
                if raw_name in ("Period Start Date", "Portfolio",
                                "Axioma World-Wide Fundamental Equity Risk Model MH 4"):
                    continue
                v = row[col] if col < len(row) else ""
                if v:
                    entry["_extra"][raw_name] = v
            out.append(entry)
        out.sort(key=lambda e: e["d"] or "")
        metric_names = [m for m in pairs.keys() if m != "Period Start Date"]
        return out, metric_names

    # ------------------------------------------- RiskM (dynamic factor list)

    def _extract_riskm(self, acct_code):
        """Extract RiskM rows. Dynamically discovers the factor list from the
        header by splitting on the two anchor columns ("% of Variance" and
        "Active Exposure")."""
        rows = self.section_rows.get("RiskM", [])
        schema = self.schemas.get("RiskM")
        if not schema or not rows:
            return [], []

        between_items = sorted(schema.between_raw.items(), key=lambda kv: kv[1])

        def find_col(name):
            for rn, c in between_items:
                if rn == name:
                    return c
            return None

        pct_var_anchor = find_col("% of Variance")
        active_anchor  = find_col("Active Exposure")

        SKIP = {
            "Fundamental Characteristics", "Price/Earnings", "Price/Book",
            "BMK Price/Earnings", "BMK Price/Book", "Risk Characteristics",
            "Axioma World-Wide Fundamental Equity Risk Model MH 4",
            "Total Risk", "Benchmark Risk", "Predicted Beta", "Risk (%)",
            "% Asset Specific Risk", "% Factor Risk", "% of Variance",
            "Exposure", "Active Exposure", "Period Start Date",
        }

        port_factor_cols = {}    # factor name → col index (% of Variance block)
        active_factor_cols = {}  # factor name → col index (Active Exposure block)
        for rn, c in between_items:
            if rn in SKIP:
                continue
            if pct_var_anchor is not None and active_anchor is not None:
                if c < active_anchor:
                    port_factor_cols[rn] = c
                else:
                    active_factor_cols[rn] = c
            elif pct_var_anchor is not None:
                port_factor_cols[rn] = c

        pe  = find_col("Price/Earnings")
        pb  = find_col("Price/Book")
        bpe = find_col("BMK Price/Earnings")
        bpb = find_col("BMK Price/Book")
        tot = find_col("Total Risk")
        bmr = find_col("Benchmark Risk")
        pbeta = find_col("Predicted Beta")
        pct_spec = find_col("% Asset Specific Risk")
        pct_fac  = find_col("% Factor Risk")
        pstart   = schema.between_raw.get("Period Start Date")

        def g(row, col):
            return safe_float(row[col]) if col is not None and col < len(row) else None

        out = []
        for row in rows:
            if len(row) < 2 or row[1].strip() != acct_code:
                continue
            if len(row) > 5 and row[5].strip() != "Data":
                continue
            d = parse_date(row[pstart]) if pstart is not None and pstart < len(row) else None
            if not d and "DATE" in schema.fixed:
                d = parse_date(row[schema.fixed["DATE"]])

            entry = {
                "d": d,
                "pe":  g(row, pe),
                "pb":  g(row, pb),
                "bpe": g(row, bpe),
                "bpb": g(row, bpb),
                "total_risk":   g(row, tot),
                "bm_risk":      g(row, bmr),
                "pbeta":        g(row, pbeta),
                "pct_specific": g(row, pct_spec),
                "pct_factor":   g(row, pct_fac),
                "exposures": {},
            }
            factor_names = set(list(port_factor_cols.keys()) + list(active_factor_cols.keys()))
            for fname in factor_names:
                pc = port_factor_cols.get(fname)
                ac = active_factor_cols.get(fname)
                c_val = g(row, pc) if pc is not None else None
                a_val = g(row, ac) if ac is not None else None
                entry["exposures"][fname] = {"c": c_val, "a": a_val, "e": c_val, "bm": None}
            out.append(entry)

        out.sort(key=lambda e: e["d"] or "")
        all_factors = sorted(set(list(port_factor_cols.keys()) + list(active_factor_cols.keys())))
        return out, all_factors

    # ---- Generic horizontal group-table extractor (19-col/group sections)

    def _extract_group_table(self, section_name, acct_code):
        """Extract group-level data (Sector / Country / Industry / Region / Group).
        Returns latest-period rollup PLUS per-period history. The 19-col-per-period
        layout includes %T and %S which CHANGE per period — historical extraction
        unlocks risk-contribution time series at the group level (cardSectors etc.
        Trend column shows real risk history, not just active weight).
        2026-04-28: parser previously only extracted last period; now keeps `hist`."""
        schema = self.schemas.get(section_name)
        rows = self.section_rows.get(section_name, [])
        if not schema or not rows or schema.num_groups == 0:
            return []

        results = []
        for row in rows:
            if len(row) < 7 or row[1].strip() != acct_code:
                continue
            level2 = row[5].strip() if len(row) > 5 else ""
            if level2 in ("Data", "@NA", "[Unassigned]", "[Cash]", ""):
                continue
            # 2026-05-01 (jagged-CSV fix): each row has its own actual group
            # count — clamp to it so we don't read past the row's data.
            row_ng = schema.num_groups_for_row(row)
            if row_ng == 0:
                continue
            last_g = row_ng - 1

            def g(canonical, gi=last_g):
                return safe_float(schema.get_group_value(row, canonical, gi))
            def gd(canonical, gi=last_g):
                return parse_date(schema.get_group_value(row, canonical, gi))

            name = GICS_NAME_MAP.get(level2, level2)
            # Latest-period rollup (existing shape — dashboard reads these directly)
            entry = {
                "n": name,
                "p": g("W"),
                "b": g("BW"),
                "a": g("AW"),
                "mcr": g("PCT_S"),
                "tr":  g("PCT_T"),
                "over": g("OVER_WAVG"),
                "rev":  g("REV_WAVG"),
                "val":  g("VAL_WAVG"),
                "qual": g("QUAL_WAVG"),
                "mom":  g("MOM_WAVG"),
                "stab": g("STAB_WAVG"),
            }
            if entry["a"] is None and entry["p"] is not None and entry["b"] is not None:
                entry["a"] = round(entry["p"] - entry["b"], 2)
            # Per-period history — same 12 fields × per-row num_groups
            hist = []
            for gi in range(row_ng):
                d = gd("PERIOD_START", gi)
                if not d: continue
                hist.append({
                    "d": d,
                    "p": g("W", gi),
                    "b": g("BW", gi),
                    "a": g("AW", gi),
                    "mcr": g("PCT_S", gi),
                    "tr":  g("PCT_T", gi),
                    "over": g("OVER_WAVG", gi),
                    "rev":  g("REV_WAVG", gi),
                    "val":  g("VAL_WAVG", gi),
                    "qual": g("QUAL_WAVG", gi),
                    "mom":  g("MOM_WAVG", gi),
                    "stab": g("STAB_WAVG", gi),
                })
            hist.sort(key=lambda x: x.get("d") or "")
            if hist:
                entry["hist"] = hist
            results.append(entry)

        return self._dedup_by_name(results)

    def _dedup_by_name(self, items):
        """When GICS renaming merges two items, keep the one with non-null weight."""
        seen = {}
        for item in items:
            name = item["n"]
            if name in seen:
                if item.get("p") is not None and seen[name].get("p") is None:
                    seen[name] = item
            else:
                seen[name] = item
        return list(seen.values())

    # ------------- Security (wildcard-driven factor column extraction)

    def _extract_security(self, acct_code, period_offset=0):
        """Extract holdings. Uses wildcard prefixes to capture all factor-family
        columns into sub-dicts. Unknown columns go to _extra.
        Returns (holdings, unowned). Both empty if Security section missing —
        e.g., 2026-04-28 inception-to-date pulls omit Security to keep file size
        sane (per-holding × inception = millions of rows).

        period_offset: 0 = current week (default, last group), -1 = prior week
        (second-to-last group). cardWeekOverWeek tile uses period_offset=-1 to
        get the prior week's holdings for the diff view. If period_offset goes
        before the first group (e.g., -1 on a single-period file), returns
        empty — the dashboard renders an empty-state banner."""
        schema = self.schemas.get("Security")
        rows = self.section_rows.get("Security", [])
        if not schema or not rows or schema.num_groups == 0:
            return [], []
        # 2026-05-01 (jagged-CSV fix): target_g must be computed per-row
        # using row's own width — rows for narrower accounts (e.g. ACWI in a
        # mixed file) end before the schema's max group count. Computed
        # inside the per-row loop below.

        FIXED_FIELD_MAP = {
            "PERIOD_START": "d",
            "SEC_GICS":     "sec",
            "SEC_REGION":   "reg",
            "SEC_COUNTRY":  "co",
            "SEC_INDUSTRY": "ind",
            "SEC_SUBGROUP": "subg",
            "W": "w",
            "BW": "bw",
            "AW": "aw",
            "PCT_S": "pct_s",
            "PCT_T": "pct_t",
            "T_CHECK": "t_check",
            "OVER_WAVG": "over",
            "REV_WAVG":  "rev",
            "VAL_WAVG":  "val",
            "QUAL_WAVG": "qual",
            "MOM_WAVG":  "mom",
            "STAB_WAVG": "stab",
            # NEW 2026-04-28 — Security section additions
            "SEC_MCAP":      "mcap",        # Market Capitalization
            "SEC_PRICE_VOL": "price_vol",   # Price Volatility
            "SEC_VOL_30D":   "vol_30d",     # Vol 30D Avg
        }

        # Build per-offset dispatch once (group layout is the same for every group)
        dispatch = {}
        for raw_name, offset in schema.group_raw_cols.items():
            canonical = _alias(raw_name)
            if canonical in FIXED_FIELD_MAP:
                dispatch[offset] = ("fixed", FIXED_FIELD_MAP[canonical])
                continue
            dict_name, suffix = _match_wildcard(raw_name)
            if dict_name:
                dispatch[offset] = ("wildcard", (dict_name, suffix))
                continue
            if raw_name == "Period Start Date":
                continue
            dispatch[offset] = ("extra", raw_name)

        # 2026-05-01 (jagged-CSV): group_start now computed per-row using
        # the row's actual num_groups (some ACCTs have narrower rows than
        # schema.num_groups; reading at schema's last group reads garbage/None).
        holdings = []
        unowned = []
        for row in rows:
            if len(row) < 7 or row[1].strip() != acct_code:
                continue
            ticker = row[5].strip() if len(row) > 5 else ""
            name   = row[6].strip() if len(row) > 6 else ""
            if not ticker or ticker.startswith("CASH_"):
                continue
            if ticker in ("Data", "@NA", "[Unassigned]"):
                continue
            row_ng = schema.num_groups_for_row(row)
            if row_ng == 0:
                continue
            row_target_g = row_ng - 1 + period_offset
            if row_target_g < 0:
                continue
            group_start = schema.group_start + row_target_g * schema.group_size

            h = {
                "t": ticker,
                "n": name,
                "factor_contr": {},
                "factor_exp": {},
                "factor_active": {},
                "factor_ret": {},
                "factor_imp": {},
                "factor_mcr": {},
                "_extra": {},
            }

            for offset in range(schema.group_size):
                col = group_start + offset
                if col >= len(row):
                    continue
                raw_val = row[col]
                disp = dispatch.get(offset)
                if not disp:
                    continue
                kind, target = disp
                if kind == "fixed":
                    if target in {"sec", "reg", "co", "ind", "subg"}:
                        h[target] = raw_val.strip() if raw_val else None
                    elif target == "d":
                        h[target] = parse_date(raw_val)
                    else:
                        h[target] = safe_float(raw_val)
                elif kind == "wildcard":
                    dict_name, factor_key = target
                    v = safe_float(raw_val)
                    if v is not None:
                        h[dict_name][factor_key] = v
                elif kind == "extra":
                    v = safe_float(raw_val)
                    if v is None and raw_val:
                        v = raw_val.strip()
                    if v not in (None, ""):
                        h["_extra"][target] = v

            if h.get("ind") in GICS_NAME_MAP:
                h["ind"] = GICS_NAME_MAP[h["ind"]]
            # Drop empty sub-dicts to keep JSON clean
            for k in list(h.keys()):
                if k.startswith("factor_") and isinstance(h[k], dict) and not h[k]:
                    del h[k]
            if not h["_extra"]:
                del h["_extra"]

            _enrich_holding(h)
            # Separate active (have weight) from historical-only (no weight in latest)
            if h.get("w") is None and h.get("bw") is None and h.get("aw") is None:
                unowned.append(h)
            else:
                holdings.append(h)

        return holdings, unowned

    # ---- 18 Style Snapshot — factor-list helper

    # Standard Axioma factor set we expose as cs.factors. The 18 Style Snapshot ships
    # 100+ items (currencies, individual industries, individual countries) — those
    # stay in snap_attrib (granular data). cs.factors only holds the 16 model factors
    # so existing dashboard tiles keep their familiar shape.
    STD_FACTORS_16 = [
        "Medium-Term Momentum", "Volatility", "Growth", "Value",
        "Dividend Yield", "Earnings Yield", "Profitability", "Size",
        "Leverage", "Liquidity", "Market Sensitivity", "Exchange Rate Sensitivity",
        "Market", "Industry", "Country", "Currency",
    ]

    def _derive_factor_names_from_snap(self, snap):
        """Pick the 16 standard factor names that are also present in snap_attrib."""
        return [f for f in self.STD_FACTORS_16 if f in snap]

    def _build_factors_from_snap(self, snap, factor_names):
        """Build cs.factors[] entries from 18 Style Snapshot data, in the same shape
        the dashboard expects post-normalize:
          { n, a (active exp), bm (bench exp), c (TE %), e (alias for a), dev, ret, imp }.
        Returns [] if snap is empty.
        """
        if not snap:
            return []
        out = []
        for name in factor_names:
            entry = snap.get(name)
            if not entry:
                continue
            # Latest period values (already extracted by _extract_snapshot)
            out.append({
                "n":   name,
                "a":   entry.get("exp"),       # avg active exposure (latest period)
                "bm":  entry.get("bench_exp"), # NEW 2026-04-28
                "e":   entry.get("exp"),       # alias for a (legacy field name)
                "c":   entry.get("risk_contr"),# % factor contr to total risk
                "dev": entry.get("dev"),
                "ret": entry.get("ret"),
                "imp": entry.get("imp"),
                "cimp":entry.get("cimp"),
            })
        return out

    # ---- 18 Style Snapshot

    def _extract_snapshot(self, acct_code):
        """18 Style Snapshot: one row per factor/country/industry/currency item.
        Captures full per-period history plus a 'latest' rollup."""
        schema = self.schemas.get("18 Style Snapshot")
        rows = self.section_rows.get("18 Style Snapshot", [])
        if not schema or not rows or schema.num_groups == 0:
            return {}

        out = {}
        for row in rows:
            if len(row) < 7 or row[1].strip() != acct_code:
                continue
            item = row[5].strip() if len(row) > 5 else ""
            if not item or item in ("Data", "@NA"):
                continue

            row_ng = schema.num_groups_for_row(row)
            periods = []
            for g in range(row_ng):
                def gv(cn):
                    return safe_float(schema.get_group_value(row, cn, g))
                d_start = parse_date(schema.get_group_value(row, "PERIOD_START", g))
                d_end   = parse_date(schema.get_group_value(row, "PERIOD_END", g))
                periods.append({
                    "d":       d_end or d_start,
                    "d_start": d_start,
                    "d_end":   d_end,
                    "exp":     gv("SNAP_EXP"),
                    "ret":     gv("SNAP_RET"),
                    "imp":     gv("SNAP_IMP"),
                    "dev":     gv("SNAP_DEV"),
                    "cimp":    gv("SNAP_CIMP"),
                    "risk_contr": gv("SNAP_RISK_CONTR"),
                    "bench_exp":  gv("SNAP_BENCH_EXP"),  # NEW 2026-04-28: bench abs exposure per factor
                    "pct_spec":   gv("SNAP_PCT_SPEC"),
                    "pct_fac":    gv("SNAP_PCT_FAC"),
                })

            # Detect a full-period summary row (last entry spans inception → current)
            weekly = periods
            summary = None
            if len(periods) > 2:
                last = periods[-1]
                first_start = periods[0].get("d_start")
                if (last.get("d_start") == first_start and
                    last.get("d_end") != last.get("d_start")):
                    summary = last
                    weekly = periods[:-1]

            latest = weekly[-1] if weekly else (summary or {})
            out[item] = {
                "exp":  latest.get("exp"),
                "ret":  latest.get("ret"),
                "imp":  latest.get("imp"),
                "dev":  latest.get("dev"),
                "cimp": latest.get("cimp"),
                "risk_contr":       latest.get("risk_contr"),
                # NEW 2026-04-28 — bench abs exposure + risk-split per period (latest)
                "bench_exp":        latest.get("bench_exp"),
                "pct_spec":         latest.get("pct_spec"),
                "pct_fac":          latest.get("pct_fac"),
                "full_period_imp":  summary.get("imp")  if summary else latest.get("cimp"),
                "full_period_cimp": summary.get("cimp") if summary else latest.get("cimp"),
                "hist": weekly,
            }
        return out

    # ---- Raw Factors (12 unlabeled z-scores per security per period)

    def _extract_raw_factors(self, acct_code):
        """Extract per-security raw factor exposures from the "Raw Factors" section.

        Shape (2026-04-28 update — group_size=14):
          Per period block = [SEDOLCHK, Period Start Date, v0..v11]. SEDOLCHK
          repeats at the start of every period (same value across periods).
        Older files shipped group_size=13: [Period Start Date, v0..v11]. We
        support both layouts.

        The 12 value columns share an identical header ("Raw Factor Exposure"),
        so column names can't identify each factor — we use RAW_FACTOR_ORDER
        positionally. If a future file ships 12 distinct header labels, we
        detect that and emit the distinct labels instead.

        Output: dict keyed by `Level2` (which is the ticker-region for the
        new file format, e.g. "III-GB"). Each entry has {n, e, hist, sedol}.
        """
        schema = self.schemas.get("Raw Factors")
        rows = self.section_rows.get("Raw Factors", [])
        if not schema or not rows or schema.num_groups == 0:
            return {}, RAW_FACTOR_ORDER

        # Four-layout support:
        #   group_size=13 (legacy):    [Period Start Date, v0..v11]
        #   group_size=14 (2026-04-28): [Period Start Date, v0..v11, SEDOLCHK_of_next]
        #   group_size=23 (2026-04-30): fields moved from Security to Raw Factors:
        #       [Period Start Date, Market Cap, 90D_ADV, 52W_Vol,
        #        OVER, REV, VAL, QUAL, MOM, STAB,
        #        RawFactorExposure×12, SEDOLCHK]
        #   group_size=24 (2026-04-30 EM full-history): adds Bench. Ending
        #       Weight at offset 1 — this is the F9 ask FactSet shipped. The
        #       per-period order observed (column-name discovery confirms):
        #       [Period Start Date, Bench. Ending Weight, 90D_ADV, Market Cap,
        #        52W_Vol, OVER, REV, VAL, QUAL, MOM, STAB,
        #        RawFactorExposure×12, SEDOLCHK]
        # Date is always at offset 0.
        if schema.group_size == 13:
            date_offset = 0
            value_offset = 1
            extra_offset = None  # No moved fields in this legacy layout
            bw_offset    = None
        elif schema.group_size == 14:
            date_offset = 0
            value_offset = 1
            extra_offset = None
            bw_offset    = None
        elif schema.group_size == 23:
            date_offset = 0
            extra_offset = 1   # mcap/adv/vol/OVER/REV/VAL/QUAL/MOM/STAB at offsets 1..9
            value_offset = 10  # 12 raw factor exposures at offsets 10..21
            bw_offset    = None
        elif schema.group_size == 24:
            # 2026-04-30 EM full-history: F9 BM weight column added at offset 1.
            # Order shifts: ADV at 2, mcap at 3, vol at 4 (note: ADV before mcap
            # in this format vs. mcap before ADV in 23-col layout — verified
            # against TSMC row data). Ranks at 5..10. Factor exposures at 11..22.
            date_offset = 0
            bw_offset   = 1    # NEW: per-period benchmark weight
            extra_offset = 2   # adv/mcap/vol/OVER/REV/VAL/QUAL/MOM/STAB at offsets 2..10
            value_offset = 11  # 12 raw factor exposures at offsets 11..22
        else:
            return {}, RAW_FACTOR_ORDER

        # Detect distinct per-column header labels (future-proof path).
        g0 = schema.group_start
        header_slice = schema.raw_cols[g0 + value_offset:g0 + value_offset + 12]
        distinct_headers = [h for h in header_slice if h and h != "Raw Factor Exposure"]
        if len(distinct_headers) == 12 and len(set(distinct_headers)) == 12:
            labels = distinct_headers
        else:
            labels = list(RAW_FACTOR_ORDER)

        out = {}
        for row in rows:
            if len(row) < 7 or row[1].strip() != acct_code:
                continue
            ident = row[5].strip() if len(row) > 5 else ""  # Level2 = ticker-region
            if not ident or ident in ("Data", "@NA", "[Unassigned]", "[Cash]"):
                continue
            if ident.startswith("CASH_"):
                continue
            name = row[6].strip() if len(row) > 6 else ""
            # SEDOLCHK is at fixed col 7 (outside the group).
            sedol = row[7].strip() if len(row) > 7 else None

            row_ng = schema.num_groups_for_row(row)
            periods = []
            for gi in range(row_ng):
                base = schema.group_start + gi * schema.group_size
                if base + value_offset + 11 >= len(row):
                    continue
                d = parse_date(row[base + date_offset])
                if not d:
                    continue
                exps = [safe_float(row[base + value_offset + i]) for i in range(12)]
                period = {"d": d, "e": exps}
                # 2026-04-30: extract the moved fields. Layout differs by group_size.
                if extra_offset is not None:
                    if schema.group_size == 23:
                        # [date, mcap, adv, vol, OVER..STAB, exp×12, SEDOLCHK]
                        period["mcap"]    = safe_float(row[base + 1])
                        period["adv"]     = safe_float(row[base + 2])
                        period["vol_52w"] = safe_float(row[base + 3])
                        period["over"]    = safe_float(row[base + 4])
                        period["rev"]     = safe_float(row[base + 5])
                        period["val"]     = safe_float(row[base + 6])
                        period["qual"]    = safe_float(row[base + 7])
                        period["mom"]     = safe_float(row[base + 8])
                        period["stab"]    = safe_float(row[base + 9])
                    elif schema.group_size == 24:
                        # [date, BW, ADV, mcap, vol, OVER..STAB, exp×12, SEDOLCHK]
                        # Note: ADV at 2, mcap at 3 (swapped vs 23-col layout) —
                        # confirmed from EM full-history file's column headers.
                        period["bw"]      = safe_float(row[base + 1])  # F9 BM weight!
                        period["adv"]     = safe_float(row[base + 2])
                        period["mcap"]    = safe_float(row[base + 3])
                        period["vol_52w"] = safe_float(row[base + 4])
                        period["over"]    = safe_float(row[base + 5])
                        period["rev"]     = safe_float(row[base + 6])
                        period["val"]     = safe_float(row[base + 7])
                        period["qual"]    = safe_float(row[base + 8])
                        period["mom"]     = safe_float(row[base + 9])
                        period["stab"]    = safe_float(row[base + 10])
                periods.append(period)

            if not periods:
                continue
            periods.sort(key=lambda p: p["d"] or "")
            entry = {
                "n": name,
                "e": periods[-1]["e"],
                "hist": periods,
                "sedol": sedol,
            }
            # Surface the latest period's moved fields at the top level so
            # downstream code can read them without traversing hist[-1].
            last = periods[-1]
            for k in ("mcap","adv","vol_52w","over","rev","val","qual","mom","stab","bw"):
                if k in last:
                    entry[k] = last[k]
            out[ident] = entry
        return out, labels

    # ---- Rank tables (Overall / REV / VAL / QUAL)

    def _extract_rank_table(self, section_name, acct_code):
        schema = self.schemas.get(section_name)
        rows = self.section_rows.get(section_name, [])
        if not schema or not rows or schema.num_groups == 0:
            return []
        out = []
        for row in rows:
            if len(row) < 7 or row[1].strip() != acct_code:
                continue
            label = row[5].strip() if len(row) > 5 else ""
            if label in ("Data", "@NA", ""):
                continue
            row_ng = schema.num_groups_for_row(row)
            if row_ng == 0:
                continue
            last_g = row_ng - 1
            def g(cn):
                return safe_float(schema.get_group_value(row, cn, last_g))
            out.append({
                "q":  label,
                "w":  g("W"),
                "bw": g("BW"),
                "aw": g("AW"),
            })
        return out

    # ------------------------------------------------------------ assembly

    def _assemble(self):
        strategies = {}
        issues = []

        for acct in self._iter_strategies():
            dash_id = self._dash_id(acct)

            pc_rows, pc_metric_names = self._extract_port_chars(acct)
            riskm_rows, factor_names = self._extract_riskm(acct)
            sectors    = self._extract_group_table("Sector Weights", acct)
            industries = self._extract_group_table("Industry", acct)
            countries  = self._extract_group_table("Country", acct)
            regions    = self._extract_group_table("Region", acct)
            groups     = self._extract_group_table("Group", acct)
            # 2026-04-30: filter out group-aggregate rows that ship as completely
            # null (every numeric field None). Common case: a legacy sector name
            # like "Telecommunication Services" is retired by the GICS taxonomy
            # but FactSet still ships an empty row. Renders as a useless empty
            # row in cardSectors / cardCountry. Drop them at parse time.
            def _drop_all_null(items):
                num_fields = ('p','b','a','tr','mcr')
                return [x for x in items if any(x.get(k) is not None for k in num_fields)]
            sectors    = _drop_all_null(sectors)
            industries = _drop_all_null(industries)
            countries  = _drop_all_null(countries)
            regions    = _drop_all_null(regions)
            groups     = _drop_all_null(groups)
            holdings, unowned_hold = self._extract_security(acct)
            # 2026-04-30 (S1 cardWeekOverWeek): also extract prior week's
            # holdings for the diff tile. Slim subset {t,n,w,bw,aw,pct_t,pct_s}
            # — enough for added/dropped/resized + KPI deltas. If only one
            # period in file, prev_holdings = [] (renderer shows empty state).
            prev_holdings_full, _ = self._extract_security(acct, period_offset=-1)
            hold_prev = [
                {
                    "t": h.get("t"),
                    "n": h.get("n"),
                    "w": h.get("w"),
                    "bw": h.get("bw"),
                    "aw": h.get("aw"),
                    "pct_t": h.get("pct_t"),
                    "pct_s": h.get("pct_s"),
                }
                for h in prev_holdings_full
                if h.get("t") and not h["t"].startswith("CASH_")
            ]
            snap       = self._extract_snapshot(acct)
            raw_fac, raw_fac_labels = self._extract_raw_factors(acct)
            # Fallback: 2026-04-28 — FactSet folded RiskM into 18 Style Snapshot.
            # If RiskM is empty, derive factor list + per-factor metrics from snap.
            if not factor_names and snap:
                factor_names = self._derive_factor_names_from_snap(snap)
            # Cross-table linkage: 2026-04-28 — Raw Factors keys by ticker-region (Level2)
            # and exposes SEDOLCHK at col 7. Security keys by SEDOL (Level2). Match by
            # SEDOL to add tkr_region (display label) AND raw_exp (z-score loadings) to
            # each holding. Holdings without a Raw Factors match keep tkr_region=null.
            if raw_fac and holdings:
                # 2026-04-30 update: Security section was slimmed and per-security
                # market cap, ADV, 52w vol, and 6 spotlight ranks (OVER/REV/VAL/
                # QUAL/MOM/STAB) all moved into Raw Factors. Pull every moved
                # field onto each holding via SEDOL match so downstream tiles
                # (sector ORVQ averages, Holdings tab rank columns, cardRanks
                # quintile bucketing) keep working unchanged.
                sedol_to_info = {}
                for tkr_region, info in raw_fac.items():
                    sedol = info.get("sedol")
                    if sedol:
                        sedol_to_info[sedol] = (tkr_region, info)
                matched = 0
                for h in holdings + unowned_hold:
                    sedol = (h.get("t") or "").strip()
                    if not sedol:
                        continue
                    if sedol in sedol_to_info:
                        tkr_region, info = sedol_to_info[sedol]
                        h["tkr_region"] = tkr_region
                        h["raw_exp"]    = info.get("e")  # 12-element list of z-scores
                        # Merge the moved fields. Don't overwrite if Security
                        # still ships the field (legacy compat) — only fill blanks.
                        # 2026-04-30: 'bw' (Bench. Ending Weight) added — F9 fix.
                        # When Security section's bw is null but Raw Factors has
                        # it, take from Raw Factors. This unblocks B116 SEV-1 —
                        # the Universe='benchmark' aggregator under-report.
                        for k in ("mcap","adv","vol_52w","over","rev","val","qual","mom","stab","bw"):
                            if k in info and h.get(k) is None:
                                h[k] = info[k]
                        matched += 1
                if matched:
                    print(f"  {dash_id}: SEDOL→Raw Factors matched {matched}/{len(holdings)} port holdings")

            # 2026-04-30 (data-integrity F4): synthesize cs.hold[] entries
            # for raw_fac entries that have bw>0 but aren't in the slim
            # Security section. Brings bench-mode coverage from ~21% to
            # ~73% by count, ~57% to ~97% by weight. The user's "BM count
            # not nearly complete" complaint is fixed here on the parser
            # side — FactSet IS shipping the full bench universe in Raw
            # Factors; the parser was just dropping it.
            if raw_fac:
                existing_sedols = set(h.get("t") for h in holdings) | set(h.get("t") for h in unowned_hold)
                # Build country→region map from existing matched holdings
                # (parser-shipped reg). Synthesized entries inherit the
                # most-common region for their country. Falls back to None
                # for new countries — dashboard uses CMAP fallback then.
                country_to_reg = {}
                for h in holdings:
                    co = h.get("co") or h.get("country")
                    rg = h.get("reg")
                    if co and rg and co not in country_to_reg:
                        country_to_reg[co] = rg
                # Same for sector inference via industry → name lookup in
                # security_ref (industry name maps to GICS sector via the
                # holding pool's industry→sector mapping when available).
                industry_to_sec = {}
                for h in holdings:
                    ind = h.get("industry")
                    sec = h.get("sec")
                    if ind and sec and ind not in industry_to_sec:
                        industry_to_sec[ind] = sec
                synth_count = 0
                for tkr_region, info in raw_fac.items():
                    sedol = info.get("sedol")
                    if not sedol or sedol in existing_sedols:
                        continue
                    bw = info.get("bw")
                    if not bw or bw <= 0:
                        continue
                    synth = {
                        "t":           sedol,
                        "n":           info.get("n"),
                        "tkr_region":  tkr_region,
                        "w":           None,        # not held
                        "bw":          bw,
                        "aw":          -bw,         # implied active = -bench
                        "pct_t":       None,
                        "pct_s":       None,
                        "mcap":        info.get("mcap"),
                        "adv":         info.get("adv"),
                        "vol_52w":     info.get("vol_52w"),
                        "over":        info.get("over"),
                        "rev":         info.get("rev"),
                        "val":         info.get("val"),
                        "qual":        info.get("qual"),
                        "mom":         info.get("mom"),
                        "stab":        info.get("stab"),
                        "raw_exp":     info.get("e"),
                        "factor_contr": {},
                        "factor_exp":   {},
                        "factor_active":{},
                        "factor_ret":   {},
                        "factor_imp":   {},
                        "factor_mcr":   {},
                        "_synth_from_raw_fac": True,    # marker
                        "_extra":       {},
                    }
                    # Enrich via security_ref by SEDOL or name fallback
                    _enrich_holding(synth)
                    # 2026-04-30: ticker-region suffix is the most reliable
                    # source-of-truth for listing country for these synth
                    # entries. security_ref name-match can give US country
                    # for Brazilian/EM names with US ADR siblings (e.g.
                    # Banco Bradesco BBDC4-BR was getting country='United
                    # States' from a US listing match). Prefer the suffix.
                    suffix = tkr_region.split("-")[-1] if "-" in tkr_region else None
                    if suffix and len(suffix) == 2:
                        suffix_to_co = {
                            "BR": "Brazil", "CN": "China", "HK": "Hong Kong",
                            "TW": "Taiwan", "KR": "Korea", "IN": "India",
                            "ID": "Indonesia", "TH": "Thailand", "MY": "Malaysia",
                            "PH": "Philippines", "SA": "Saudi Arabia",
                            "AE": "United Arab Emirates", "ZA": "South Africa",
                            "MX": "Mexico", "TR": "Turkey", "PL": "Poland",
                            "HU": "Hungary", "GR": "Greece", "QA": "Qatar",
                            "PE": "Peru", "AR": "Argentina", "EG": "Egypt",
                            "CO": "Colombia", "CL": "Chile", "PK": "Pakistan",
                            "VN": "Vietnam", "RU": "Russia", "JP": "Japan",
                            "US": "United States", "GB": "United Kingdom",
                            "DE": "Germany", "FR": "France", "CH": "Switzerland",
                            "NL": "Netherlands", "SE": "Sweden", "DK": "Denmark",
                            "NO": "Norway", "FI": "Finland", "ES": "Spain",
                            "IT": "Italy", "PT": "Portugal", "IE": "Ireland",
                            "AT": "Austria", "BE": "Belgium", "AU": "Australia",
                            "NZ": "New Zealand", "SG": "Singapore", "CA": "Canada",
                            "IL": "Israel", "KW": "Kuwait", "BH": "Bahrain",
                            "OM": "Oman", "JO": "Jordan", "LK": "Sri Lanka",
                            "BD": "Bangladesh", "MA": "Morocco", "NG": "Nigeria",
                            "KE": "Kenya", "TN": "Tunisia", "RO": "Romania",
                            "CZ": "Czech Republic", "AR": "Argentina",
                        }
                        if suffix in suffix_to_co:
                            synth["co"] = suffix_to_co[suffix]
                            synth["country"] = suffix_to_co[suffix]
                    # Country naming normalization: existing parsed holdings use
                    # h.co='Korea' / 'Mexico' (FactSet shorthand); security_ref
                    # uses h.country='Korea, Republic of' / 'Mexico'. Prefer
                    # h.co convention so cardCountry tile doesn't show two
                    # rows for the same country.
                    co_norm_map = {}
                    for h in holdings:
                        cn = h.get("country")
                        co = h.get("co")
                        if cn and co and cn != co:
                            co_norm_map[cn] = co
                    co_raw = synth.get("co") or synth.get("country")
                    co = co_norm_map.get(co_raw, co_raw)
                    if co:
                        synth["co"] = co
                        if co in country_to_reg:
                            synth["reg"] = country_to_reg[co]
                    # Sector inference from industry
                    ind = synth.get("industry")
                    if ind and ind in industry_to_sec:
                        synth["sec"] = industry_to_sec[ind]
                        if not synth.get("ind"):
                            synth["ind"] = ind
                    holdings.append(synth)
                    existing_sedols.add(sedol)
                    synth_count += 1
                if synth_count:
                    print(f"  {dash_id}: synth +{synth_count} bench-only entries from Raw Factors (F4 — bench coverage now ~73%)")

            if _SECURITY_REF:
                enriched = sum(1 for h in holdings if h.get("country"))
                total = len(holdings)
                pct = (100.0 * enriched / total) if total else 0.0
                print(f"  {dash_id}: security_ref enrichment {enriched}/{total} ({pct:.1f}%)")

            ranks = {
                "overall": self._extract_rank_table("Overall", acct),
                "rev":     self._extract_rank_table("REV", acct),
                "val":     self._extract_rank_table("VAL", acct),
                "qual":    self._extract_rank_table("QUAL", acct),
            }

            current_pc = pc_rows[-1] if pc_rows else {}
            current_rm = riskm_rows[-1] if riskm_rows else {}

            pc_metrics = current_pc.get("_metrics", {}) if current_pc else {}
            def pcv(metric):
                m = pc_metrics.get(metric)
                return m["p"] if m else None
            def pcb(metric):
                m = pc_metrics.get(metric)
                return m["b"] if m else None

            te          = pcv("Predicted Tracking Error (Std Dev)")
            beta        = pcv("Axioma- Predicted Beta to Benchmark")
            h_cnt       = pcv("# of Securities")
            bh_cnt      = pcb("# of Securities")
            act_s       = pcv("Port. Ending Active Share")
            mcap        = pcv("Market Capitalization")
            bmcap       = pcb("Market Capitalization")
            hist_beta   = pcv("Axioma- Historical Beta")
            mpt_beta    = pcv("Port. MPT Beta")
            b_hist_beta = pcb("Axioma- Historical Beta")
            b_mpt_beta  = pcb("Port. MPT Beta")

            # Cash from Sector Weights [Cash] row, if present.
            # 2026-04-30: ALSO build cash_by_date — per-period cash % across the
            # full history, so cardCashHist (Exposures-tab time-series tile) can
            # plot cash drift over time. Was previously latest-only.
            cash = None
            cash_by_date = {}
            for r in self.section_rows.get("Sector Weights", []):
                if len(r) > 5 and r[1].strip() == acct and r[5].strip() == "[Cash]":
                    sch = self.schemas.get("Sector Weights")
                    if sch and sch.num_groups:
                        # 2026-05-01 (jagged-CSV): clamp to this row's actual width.
                        row_ng = sch.num_groups_for_row(r)
                        if row_ng == 0: break
                        # Latest week (last group of THIS row, not schema)
                        cash = safe_float(sch.get_group_value(r, "W", row_ng - 1))
                        # Per-period: walk every group, key by Period Start Date.
                        # get_group_value expects the canonical alias, not the raw column name.
                        for gi in range(row_ng):
                            d_raw = sch.get_group_value(r, "PERIOD_START", gi)
                            d_parsed = parse_date(d_raw) if d_raw else None
                            if d_parsed:
                                w = safe_float(sch.get_group_value(r, "W", gi))
                                if w is not None:
                                    cash_by_date[d_parsed] = w
                    break

            s = {
                "id": dash_id,
                "name": dash_id,
                "benchmark": "",
                "current_date": current_pc.get("d") if current_pc else None,
                "available_dates": sorted(set(e["d"] for e in pc_rows if e.get("d"))),
                "sum": {
                    "te":    te,
                    "beta":  beta,
                    "h":     h_cnt,
                    "bh":    bh_cnt,
                    "as":    act_s,
                    "mcap":  mcap,
                    "bmcap": bmcap,
                    "hist_beta":   hist_beta,
                    "mpt_beta":    mpt_beta,
                    "b_hist_beta": b_hist_beta,
                    "b_mpt_beta":  b_mpt_beta,
                    "betas": {
                        "predicted":  beta,
                        "historical": hist_beta,
                        "mpt":        mpt_beta,
                    },
                    # 2026-04-30: when RiskM section doesn't ship P/E (newer
                    # format folds RiskM → 18 Style Snapshot), fall back to
                    # Portfolio Characteristics metrics (pc_metrics has P/E -
                    # NTM, Price to Book - NTM, etc. with both port + bench).
                    "pe":    (current_rm.get("pe")
                              if current_rm.get("pe") is not None
                              else (pc_metrics.get("P/E - NTM",{}) or {}).get("p")),
                    "pb":    (current_rm.get("pb")
                              if current_rm.get("pb") is not None
                              else (pc_metrics.get("Price to Book - NTM",{}) or {}).get("p")),
                    "bpe":   (current_rm.get("bpe")
                              if current_rm.get("bpe") is not None
                              else (pc_metrics.get("P/E - NTM",{}) or {}).get("b")),
                    "bpb":   (current_rm.get("bpb")
                              if current_rm.get("bpb") is not None
                              else (pc_metrics.get("Price to Book - NTM",{}) or {}).get("b")),
                    "total_risk":   current_rm.get("total_risk"),
                    "bm_risk":      current_rm.get("bm_risk"),
                    # pct_specific / pct_factor: sourced from RiskM when present.
                    # 2026-04-28: FactSet folded RiskM → 18 Style Snapshot, but did NOT
                    # carry % Stock Specific / % Factor Risk forward at portfolio level.
                    # Per user direction: derive pct_specific = Σ(sector mcr) since no
                    # sectors are hidden anymore (Σ sector %T = 100 confirms invariant).
                    # Then pct_factor = 100 - pct_specific. Marked _derived to preserve
                    # provenance.
                    "pct_specific": (
                        current_rm.get("pct_specific")
                        if current_rm.get("pct_specific") is not None
                        else (round(sum((s.get("mcr") or 0) for s in sectors), 2) if sectors else None)
                    ),
                    "pct_factor": (
                        current_rm.get("pct_factor")
                        if current_rm.get("pct_factor") is not None
                        else (round(100 - sum((s.get("mcr") or 0) for s in sectors), 2) if sectors else None)
                    ),
                    "_pct_specific_source": "riskm" if current_rm.get("pct_specific") is not None else "sum_sector_mcr",
                    "_pct_factor_source":   "riskm" if current_rm.get("pct_factor")   is not None else "100_minus_pct_specific",
                    "cash": cash,
                    "sr": round(h_cnt / bh_cnt * 100, 2) if h_cnt and bh_cnt else None,
                },
                "sectors":    sectors,
                "industries": industries,
                "countries":  countries,
                "regions":    regions,
                "groups":     groups,
                "hold":       holdings,
                "hold_prev":  hold_prev,   # 2026-04-30: prior-week slim for cardWeekOverWeek
                "ranks":      ranks,
                "snap_attrib": snap,
                "factors": self._build_factor_list(current_rm, snap, factor_names),
                "chars":   self._build_chars(pc_metrics, current_rm, mcap, bmcap),
                "hist": {
                    "summary": [self._hist_entry(pc, cash_by_date) for pc in pc_rows],
                    "fac":  self._build_hist_fac(riskm_rows),
                    # 2026-04-28: per-period group history. Each value is a list of
                    # {d, p, b, a, mcr, tr, over, rev, val, qual, mom, stab} entries
                    # ordered by date. Empty-history entries are skipped.
                    "sec":  self._group_hist_dict(sectors),
                    "ctry": self._group_hist_dict(countries),
                    "ind":  self._group_hist_dict(industries),
                    "reg":  self._group_hist_dict(regions),
                    "grp":  self._group_hist_dict(groups),
                    # 2026-04-30: per-period chars history. {metric: [{d,p,b}, ...]}.
                    # Built from the same pc_rows used by hist.summary; lifts the
                    # "no historical data" wall on the cardChars drill modal for
                    # every numeric metric (TE / Beta / Active Share already
                    # surfaced via hist.summary; the other ~35 fundamentals
                    # were B114-blocked until now).
                    "chars": self._build_hist_chars(pc_rows),
                },
                "unowned": unowned_hold,
                "raw_fac": raw_fac,
                "raw_fac_labels": raw_fac_labels,
                "security_ref_version": _SECURITY_REF_META.get("schema_version") if _SECURITY_REF else None,
                "_portchars_metrics": pc_metric_names,
            }
            strategies[dash_id] = s

        return strategies, issues

    def _group_hist_dict(self, group_list):
        """Convert a list of group entries (with `hist` arrays) into a dict
        keyed by group name. Used to populate strategy.hist.{sec,ctry,ind,reg,grp}.
        Strips per-entry hist out of the original group dicts to keep latest-period
        rollup clean (history lives at strategy level)."""
        out = {}
        for g in (group_list or []):
            name = g.get("n")
            hist = g.pop("hist", None)
            if name and hist:
                out[name] = hist
        return out

    def _build_factor_list(self, current_rm, snap, factor_names):
        """Build cs.factors[]. Prefers RiskM-section values when available;
        falls back to 18 Style Snapshot values when RiskM is missing.
        2026-04-28 update: FactSet folded RiskM into 18 Style Snapshot, so the
        snap fallback path is now the primary source for new files.
        """
        out = []
        exposures = current_rm.get("exposures", {}) if current_rm else {}
        for fname in factor_names:
            exp = exposures.get(fname, {})
            snap_item = snap.get(fname, {})
            # Prefer RiskM `a` (active exposure) and `c` (% TE), fall back to snap.
            a_val   = exp.get("a")    if exp.get("a")    is not None else snap_item.get("exp")
            bm_val  = exp.get("bm")   if exp.get("bm")   is not None else snap_item.get("bench_exp")
            e_val   = exp.get("e")    if exp.get("e")    is not None else snap_item.get("exp")
            c_val   = exp.get("c")    if exp.get("c")    is not None else snap_item.get("risk_contr")
            out.append({
                "n":    fname,
                "e":    e_val,
                "bm":   bm_val,
                "a":    a_val,
                "c":    c_val,
                "ret":  snap_item.get("ret"),
                "imp":  snap_item.get("imp"),
                "dev":  snap_item.get("dev"),
                "cimp": snap_item.get("cimp"),
                "risk_contr": snap_item.get("risk_contr"),
            })
        return out

    def _build_chars(self, pc_metrics, current_rm, mcap, bmcap):
        """Characteristics table. Always-present derived rows + every :P/:B pair."""
        chars = []

        def pc_p(metric):
            m = pc_metrics.get(metric)
            return m["p"] if m else None
        def pc_b(metric):
            m = pc_metrics.get(metric)
            return m["b"] if m else None

        chars.append({"m": "Tracking Error (%)",
                      "p": pc_p("Predicted Tracking Error (Std Dev)"),
                      "b": None, "a": None})
        chars.append({"m": "Beta",
                      "p": pc_p("Axioma- Predicted Beta to Benchmark"),
                      "b": 1.0,
                      "a": _sub(pc_p("Axioma- Predicted Beta to Benchmark"), 1.0)})
        chars.append({"m": "Active Share (%)",
                      "p": pc_p("Port. Ending Active Share"),
                      "b": None, "a": None})
        chars.append({"m": "Market Cap ($B)",
                      "p": round(mcap / 1000, 1) if mcap else None,
                      "b": round(bmcap / 1000, 1) if bmcap else None,
                      "a": round((mcap - bmcap) / 1000, 1) if mcap and bmcap else None})
        if current_rm:
            chars.append({"m": "Price/Earnings (P/E)",
                          "p": current_rm.get("pe"),
                          "b": current_rm.get("bpe"),
                          "a": _sub(current_rm.get("pe"), current_rm.get("bpe"))})
            chars.append({"m": "Price/Book (P/B)",
                          "p": current_rm.get("pb"),
                          "b": current_rm.get("bpb"),
                          "a": _sub(current_rm.get("pb"), current_rm.get("bpb"))})

        # Auto-add every other :P/:B pair (excluding already-emitted / structural cols)
        already_emitted = {
            "Predicted Tracking Error (Std Dev)",
            "Axioma- Predicted Beta to Benchmark",
            "Port. Ending Active Share",
            "Market Capitalization",
            "Period Start Date",
            "Portfolio",
            "Axioma World-Wide Fundamental Equity Risk Model MH 4",
            "# of Securities",
            "Risk (%)",
        }
        for metric, pair in pc_metrics.items():
            if metric in already_emitted:
                continue
            p = pair.get("p")
            b = pair.get("b")
            chars.append({"m": metric, "p": p, "b": b, "a": _sub(p, b)})

        return chars

    def _hist_entry(self, pc_row, cash_by_date=None):
        pcm = pc_row.get("_metrics", {}) if pc_row else {}
        def v(metric):
            m = pcm.get(metric)
            return m["p"] if m else None
        d = pc_row.get("d")
        # 2026-04-30: cash extracted from Sector Weights [Cash] row per period
        # in _assemble; passed in via cash_by_date dict so per-period cash %
        # populates hist.summary[].cash (drives cardCashHist time-series tile).
        cash = (cash_by_date or {}).get(d) if d else None
        return {
            "d":    d,
            "te":   v("Predicted Tracking Error (Std Dev)"),
            "beta": v("Axioma- Predicted Beta to Benchmark"),
            "h":    v("# of Securities"),
            "as":   v("Port. Ending Active Share"),
            "sr":   None,
            "cash": cash,
        }

    def _build_hist_fac(self, riskm_rows):
        out = {}
        for r in riskm_rows:
            d = r.get("d")
            for fname, exp in r.get("exposures", {}).items():
                out.setdefault(fname, []).append({
                    "d":  d,
                    "e":  exp.get("c"),
                    "bm": exp.get("bm"),
                    "a":  exp.get("a"),
                })
        return out

    def _build_hist_chars(self, pc_rows):
        """Per-period chars history. Output: {metric: [{d, p, b}, ...]} ordered by date.
        Drives the cardChars drill modal time-series for every shipped metric —
        unblocks B114 for numeric :P/:B pairs without changing the snapshot
        cs.chars contract. Date matches Predicted Tracking Error column-style
        d-string; metric names match _build_chars output.
        """
        out = {}
        # Metrics already exposed at top-level (TE/Beta/AS) get aliases that
        # match cs.chars[].m so the dashboard's CHAR_META map can look them up.
        ALIAS = {
            "Predicted Tracking Error (Std Dev)": "Tracking Error (%)",
            "Axioma- Predicted Beta to Benchmark": "Beta",
            "Port. Ending Active Share": "Active Share (%)",
            "Market Capitalization": "Market Cap ($B)",
        }
        # Skip non-numeric / structural columns.
        SKIP = {
            "Period Start Date",
            "Portfolio",
            "Axioma World-Wide Fundamental Equity Risk Model MH 4",
            "# of Securities",
        }
        for pc in pc_rows:
            d = pc.get("d")
            if not d:
                continue
            metrics = pc.get("_metrics", {})
            for metric, pair in metrics.items():
                if metric in SKIP:
                    continue
                p = pair.get("p")
                b = pair.get("b")
                if p is None and b is None:
                    continue
                # Special transform: Market Cap shipped as $B in chars but
                # as raw $M in pc_metrics — divide by 1000 for consistency.
                if metric == "Market Capitalization":
                    p = round(p / 1000, 2) if p is not None else None
                    b = round(b / 1000, 2) if b is not None else None
                key = ALIAS.get(metric, metric)
                out.setdefault(key, []).append({"d": d, "p": p, "b": b})
        return out

    # ------------------------------------------------------------ public

    def parse(self):
        t0 = time.time()
        self._load()
        self.stats["file_size_mb"] = round(os.path.getsize(self.path) / 1024 / 1024, 2)
        self.stats["total_rows"] = len(self.rows)
        self._discover_schemas()
        for sec, rows in self.section_rows.items():
            self.stats["rows_per_section"][sec] = len(rows)
        strategies, issues = self._assemble()
        self.stats["parse_time_s"] = round(time.time() - t0, 3)

        report_date = None
        for s in strategies.values():
            cd = s.get("current_date")
            if cd and (not report_date or cd > report_date):
                report_date = cd

        return [strategies, issues, report_date, self.stats]


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 factset_parser_v3.py input.csv [output.json]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(inp)[0] + "_v3.json"

    parser = FactSetParserV3(inp)
    result = parser.parse()

    strategies, issues, report_date, stats = result
    print(f"Parsed {stats['total_rows']} rows in {stats['parse_time_s']}s  "
          f"({stats['file_size_mb']} MB input)")
    print(f"Encoding: {stats['encoding']}  |  Report date: {report_date}")
    print(f"Strategies: {list(strategies.keys())}")
    print(f"Schemas discovered:")
    for sec, info in stats["schemas_discovered"].items():
        print(f"  {sec:<30} cols={info['total_cols']:>5}  "
              f"group_size={info['group_size']:>3}  num_groups={info['num_groups']:>4}  "
              f"group_fields={info['group_cols']}")
    print()
    for sid, s in strategies.items():
        h_count = len(s.get("hold", []))
        te = s.get("sum", {}).get("te")
        pe = s.get("sum", {}).get("pe")
        bpe = s.get("sum", {}).get("bpe")
        # Sample factor_contr richness
        fc_msg = "—"
        if s.get("hold"):
            fh = s["hold"][0]
            fc = fh.get("factor_contr", {})
            if fc:
                fc_msg = f"{fh.get('t','?')}: {len(fc)} factor contrib"
        print(f"  {sid}: {h_count} holdings  TE={te}  P/E={pe}  BMK P/E={bpe}  sample={fc_msg}")

    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, default=str)
    print(f"\nOutput: {out}")


if __name__ == "__main__":
    main()
