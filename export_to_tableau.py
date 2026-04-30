#!/usr/bin/env python3
"""
export_to_tableau.py — Export one section of latest_data.json to a flat CSV
                       suitable for Tableau Show Me sketching.

R2-Q20 from INQUISITOR_QUEUE_R2_2026-04-30.md (user confirmed 2026-04-30).

Per TABLEAU_AND_MOCKUP_NOTES.md: Tableau is a sketchbook. Use it to discover
what visualization shape works for your data, then re-implement in Plotly
inside dashboard_v7.html. Don't deploy Tableau workbooks — the deployment
story for RR is "open one HTML file, drag JSON, done."

Usage:
    python3 export_to_tableau.py --strategy GSC --section sectors
    python3 export_to_tableau.py --strategy EM --section holdings --port-only
    python3 export_to_tableau.py --strategy EM --section snap_attrib --factor "Volatility"
    python3 export_to_tableau.py --list-sections

Flat-CSV outputs land in ~/Downloads/<strategy>_<section>_<timestamp>.csv.

Sections supported:
    holdings  — per-holding rows (one per security, one row per holding)
    sectors   — sector aggregate rows
    countries — country aggregate rows
    regions   — region aggregate rows
    groups    — Redwood subgroup aggregate rows
    factors   — RiskM factor rows (one per factor)
    snap_attrib_hist — long-form factor weekly history (factor × week)
    summary_hist — weekly summary stats (one row per week)
    chars     — Portfolio Characteristics (39 metrics × port/bench/active)

Anti-fabrication policy: only ships fields that the parser populated. Empty
cells are empty (not zero-filled, not synthesized). The synth markers
(`_pct_specific_source` etc.) are preserved as columns for transparency.
"""

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path


def load_data(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data[0] if data else {}
    return data.get("strategies", data)


def export_holdings(strategy_dict, port_only=False):
    """Per-holding rows. One CSV row per security."""
    holdings = strategy_dict.get("hold", [])
    if port_only:
        holdings = [h for h in holdings if (h.get("w") or 0) > 0]
    if not holdings:
        return [], []
    # Discover fields across all holdings — flat columns only.
    fields = ["t", "tkr_region", "n", "sec", "co", "country", "currency",
              "industry", "subg", "w", "bw", "aw", "pct_t", "pct_s",
              "mcap", "adv", "vol_52w", "over", "rev", "val", "qual",
              "mom", "stab", "raw_exp"]
    # Dynamically add any factor_contr keys as separate columns (so Tableau can
    # treat each factor as its own dimension).
    fc_keys = set()
    for h in holdings:
        for k in (h.get("factor_contr") or {}).keys():
            fc_keys.add(k)
    fc_keys = sorted(fc_keys)
    cols = list(fields) + ["fc_" + k for k in fc_keys]
    rows = []
    for h in holdings:
        row = {f: h.get(f) for f in fields}
        # raw_exp is a list — flatten to a single comma-separated string for Tableau.
        if isinstance(row.get("raw_exp"), list):
            row["raw_exp"] = ";".join(str(x) for x in row["raw_exp"] if x is not None)
        for k in fc_keys:
            row["fc_" + k] = (h.get("factor_contr") or {}).get(k)
        rows.append(row)
    return cols, rows


def export_aggregate(strategy_dict, key):
    """sectors / countries / regions / groups — aggregate rows."""
    items = strategy_dict.get(key, [])
    if not items:
        return [], []
    # Use union of keys across all rows for column list — handles missing
    # fields gracefully (Tableau renders blanks).
    all_keys = []
    seen = set()
    for it in items:
        for k in it.keys():
            if k not in seen:
                seen.add(k)
                all_keys.append(k)
    return all_keys, items


def export_factors(strategy_dict):
    """RiskM factor rows. One per factor, latest snapshot."""
    facs = strategy_dict.get("factors", [])
    if not facs:
        return [], []
    fields = ["n", "e", "bm", "a", "c", "ret", "imp", "dev", "cimp",
              "risk_contr", "_a_synth", "_c_synth"]
    rows = [{f: f0.get(f) for f in fields} for f0 in facs]
    return fields, rows


def export_snap_attrib_hist(strategy_dict, factor_filter=None):
    """Long-form factor history: one row per (factor, week)."""
    sa = strategy_dict.get("snap_attrib", {})
    if not sa:
        return [], []
    cols = ["factor", "d", "d_start", "d_end", "exp", "bench_exp",
            "active_exp", "ret", "imp", "dev", "cimp", "risk_contr",
            "pct_spec", "pct_fac"]
    rows = []
    for factor_name, info in sa.items():
        if factor_filter and factor_name != factor_filter:
            continue
        hist = info.get("hist") or []
        for p in hist:
            exp = p.get("exp")
            be = p.get("bench_exp")
            active = (exp - be) if (exp is not None and be is not None) else None
            rows.append({
                "factor": factor_name,
                "d": p.get("d"),
                "d_start": p.get("d_start"),
                "d_end": p.get("d_end"),
                "exp": exp,
                "bench_exp": be,
                "active_exp": active,
                "ret": p.get("ret"),
                "imp": p.get("imp"),
                "dev": p.get("dev"),
                "cimp": p.get("cimp"),
                "risk_contr": p.get("risk_contr"),
                "pct_spec": p.get("pct_spec"),
                "pct_fac": p.get("pct_fac"),
            })
    return cols, rows


def export_summary_hist(strategy_dict):
    """One row per week from cs.hist.summary."""
    hist = (strategy_dict.get("hist") or {}).get("summary") or []
    if not hist:
        return [], []
    cols = ["d", "te", "as", "beta", "h", "sr", "cash"]
    return cols, [{c: e.get(c) for c in cols} for e in hist]


def export_chars(strategy_dict):
    """Portfolio Characteristics — 39 metrics × {port, bench, active}."""
    chars = strategy_dict.get("chars") or []
    if not chars:
        return [], []
    cols = ["m", "p", "b", "a", "_synth", "_synth_source", "_invert"]
    rows = []
    for c in chars:
        row = {col: c.get(col) for col in cols}
        rows.append(row)
    return cols, rows


def write_csv(out_path, cols, rows):
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="latest_data.json",
                    help="Path to latest_data.json (default: latest_data.json)")
    ap.add_argument("--strategy", help="Strategy ID (e.g. EM, GSC, IDM, IOP, ACWI, ISC, SCG)")
    ap.add_argument("--section", help="Section to export. See --list-sections.")
    ap.add_argument("--port-only", action="store_true",
                    help="(holdings only) include only port-held names")
    ap.add_argument("--factor", help="(snap_attrib_hist only) filter to one factor")
    ap.add_argument("--out", help="Output CSV path (default: ~/Downloads/<strategy>_<section>_<timestamp>.csv)")
    ap.add_argument("--list-sections", action="store_true",
                    help="List available sections and exit")
    args = ap.parse_args()

    sections = {
        "holdings": "Per-holding rows (one per security)",
        "sectors": "Sector aggregate rows",
        "countries": "Country aggregate rows",
        "regions": "Region aggregate rows",
        "groups": "Redwood subgroup aggregate rows",
        "factors": "RiskM factor rows (latest snapshot)",
        "snap_attrib_hist": "Long-form factor weekly history (factor × week)",
        "summary_hist": "Weekly summary stats (one row per week)",
        "chars": "Portfolio Characteristics (39 metrics × port/bench/active)",
    }

    if args.list_sections:
        print("Available sections:\n")
        for name, desc in sections.items():
            print(f"  {name:<22} {desc}")
        sys.exit(0)

    if not args.strategy or not args.section:
        ap.print_help()
        sys.exit(1)

    if args.section not in sections:
        print(f"Unknown section: {args.section}")
        print(f"Available: {', '.join(sections.keys())}")
        sys.exit(1)

    data = load_data(args.data)
    if args.strategy not in data:
        print(f"Strategy {args.strategy} not in {args.data}")
        print(f"Available: {', '.join(data.keys())}")
        sys.exit(1)
    sd = data[args.strategy]

    if args.section == "holdings":
        cols, rows = export_holdings(sd, port_only=args.port_only)
    elif args.section in ("sectors", "countries", "regions", "groups"):
        cols, rows = export_aggregate(sd, args.section)
    elif args.section == "factors":
        cols, rows = export_factors(sd)
    elif args.section == "snap_attrib_hist":
        cols, rows = export_snap_attrib_hist(sd, factor_filter=args.factor)
    elif args.section == "summary_hist":
        cols, rows = export_summary_hist(sd)
    elif args.section == "chars":
        cols, rows = export_chars(sd)
    else:
        sys.exit(2)

    if not rows:
        print(f"No rows to export — {args.strategy}.{args.section} is empty.")
        sys.exit(0)

    if args.out:
        out_path = Path(args.out).expanduser()
    else:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = "_port_only" if args.port_only else ""
        if args.factor:
            suffix += "_" + args.factor.replace(" ", "_").replace("/", "_")
        name = f"{args.strategy}_{args.section}{suffix}_{ts}.csv"
        out_path = Path.home() / "Downloads" / name

    write_csv(out_path, cols, rows)
    print(f"✓ Wrote {len(rows):,} rows × {len(cols)} cols → {out_path}")
    print(f"  Tableau Desktop: drag this file in, hit 'Show Me', explore.")
    print(f"  Reminder (TABLEAU_AND_MOCKUP_NOTES.md): never publish to Tableau Public.")


if __name__ == "__main__":
    main()
