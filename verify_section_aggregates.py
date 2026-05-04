#!/usr/bin/env python3
"""
verify_section_aggregates.py — Layer 2 of the RR Data Integrity Monitor.

Reads latest_data.json. For every (strategy × dimension × week), computes
Σ %T across buckets in that dimension's section-aggregate row from FactSet.
Reports min / max / avg / deviation-count + a global "data integrity score."

Wired into smoke_test.sh so it runs on every pre-commit / pre-push.

USAGE:
    python3 verify_section_aggregates.py            # full check, all weeks
    python3 verify_section_aggregates.py --latest   # latest week only (faster)
    python3 verify_section_aggregates.py --strict   # exit 1 on any RED finding
    python3 verify_section_aggregates.py --tolerance 5  # ±5% counts as clean
    python3 verify_section_aggregates.py --json     # machine-readable output

WHY:
    The May 1 demo crisis (cardSectors holdings-sum 137%) and F18 (cardRiskByDim
    per-holding %T 94->134%) both surfaced from manual audits. This script
    automates the section-aggregate sum check so future drift is caught on
    the day it appears, not weeks later.

OUTPUT:
    Printable table. Color-coded:
        🟢 GREEN — within tolerance (default ±5%)
        🟡 YELLOW — within ±10% but outside tolerance
        🔴 RED — outside ±10%
    + a single "Data Integrity Score" = % of (strategy × dim × week)
      cells within ±5%.
"""

import argparse
import json
import os
import sys

# ANSI colors (POSIX-only; safe in CI/terminal/VS Code; degrades silently if redirected)
G = "\033[32m" if sys.stdout.isatty() else ""
Y = "\033[33m" if sys.stdout.isatty() else ""
R = "\033[31m" if sys.stdout.isatty() else ""
DIM = "\033[2m" if sys.stdout.isatty() else ""
END = "\033[0m" if sys.stdout.isatty() else ""

DIMS = [
    ("sec",  "Sector"),
    ("ctry", "Country"),
    ("reg",  "Region"),
    ("grp",  "Group"),
    ("ind",  "Industry"),
]


def severity(value, tol):
    """Return severity tier given Σ %T value and tolerance % (around 100)."""
    if 100 - tol <= value <= 100 + tol:
        return "GREEN"
    if 100 - 2 * tol <= value <= 100 + 2 * tol:
        return "YELLOW"
    return "RED"


def color_for(sev):
    return {"GREEN": G, "YELLOW": Y, "RED": R}[sev]


def compute_dim_sums(strategy_obj, dim_key):
    """For a single (strategy, dim), return list of (date, Σ tr) per week.

    Reads from cs.hist[dim] which is keyed by bucket name and ships an array of
    per-week entries. Each entry has a `tr` field (alias for FactSet %T)."""
    hist_dim = (strategy_obj.get("hist") or {}).get(dim_key) or {}
    if not hist_dim:
        return []
    # All buckets share the same date series; iterate by index.
    first_bucket = next(iter(hist_dim.values()))
    n_dates = len(first_bucket)
    sums = []
    for i in range(n_dates):
        tr_sum = 0.0
        for entries in hist_dim.values():
            if i < len(entries):
                e = entries[i]
                if e and e.get("tr") is not None:
                    tr_sum += e["tr"]
        date = (first_bucket[i] or {}).get("d", "?") if i < len(first_bucket) else "?"
        sums.append((date, tr_sum))
    return sums


def compute_holding_sum(strategy_obj):
    """Σ %T across all non-cash holdings (latest week only — that's what's in cs.hold)."""
    hold = strategy_obj.get("hold") or []
    # Match isCash() in dashboard: ticker startswith CASH_ or sector contains 'cash'
    s = 0.0
    for h in hold:
        t = (h.get("t") or "").upper()
        sec = (h.get("sec") or "").lower()
        if t.startswith("CASH_") or "cash" in sec:
            continue
        # tr alias of pct_t (parser ships pct_t; dashboard normalize aliases to tr)
        v = h.get("tr") if h.get("tr") is not None else h.get("pct_t")
        if v is not None:
            s += v
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--latest", action="store_true",
                    help="Check only the latest week per strategy (faster)")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 if any RED finding (CI gate)")
    ap.add_argument("--tolerance", type=float, default=5.0,
                    help="±%% tolerance around 100 to count as GREEN (default 5)")
    ap.add_argument("--json", action="store_true",
                    help="Machine-readable JSON output")
    ap.add_argument("--input", default="latest_data.json",
                    help="Path to parsed JSON (default latest_data.json)")
    args = ap.parse_args()

    rr_dir = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(rr_dir, args.input)
    if not os.path.exists(in_path):
        print(f"ERROR: {in_path} not found.", file=sys.stderr)
        sys.exit(2)

    with open(in_path) as f:
        d = json.load(f)
    strats = d[0] if isinstance(d, list) else d.get("strategies", d)

    results = {
        "version": "1.0",
        "tolerance_pct": args.tolerance,
        "latest_only": args.latest,
        "strategies": {},
    }

    # Iterate strategies in stable order
    for sid in sorted(strats.keys()):
        s = strats[sid]
        per_dim = {}
        for dim_key, dim_label in DIMS:
            sums = compute_dim_sums(s, dim_key)
            if not sums:
                continue
            if args.latest:
                sums = sums[-1:]
            tr_vals = [v for _, v in sums]
            tot = len(tr_vals)
            counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
            for v in tr_vals:
                counts[severity(v, args.tolerance)] += 1
            mn, mx = min(tr_vals), max(tr_vals)
            avg = sum(tr_vals) / tot
            latest_v = tr_vals[-1]
            worst = max(sums, key=lambda x: abs(x[1] - 100))
            per_dim[dim_label] = {
                "total_weeks": tot,
                "min": mn, "max": mx, "avg": avg,
                "latest": latest_v,
                "worst_date": worst[0], "worst_value": worst[1],
                "counts": counts,
                "n_buckets": len((s.get("hist") or {}).get(dim_key) or {}),
            }
        # Per-holding %T (latest week only — cs.hold is latest-only by design)
        per_dim["Per-holding"] = {
            "total_weeks": 1,
            "latest": compute_holding_sum(s),
            "n_buckets": len(s.get("hold") or []),
            "note": "F18 — latest week only; cs.hold doesn't ship per-week",
        }
        results["strategies"][sid] = per_dim

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0)

    # Pretty print
    print("=" * 86)
    print(f"RR Data Integrity Monitor — Section-Aggregate %TE Check")
    print(f"Tolerance: ±{args.tolerance:.1f}%   |   Mode: {'latest week' if args.latest else 'all weeks'}")
    print("=" * 86)

    grand_total = 0
    grand_within = 0
    any_red = False

    for sid in sorted(results["strategies"].keys()):
        per_dim = results["strategies"][sid]
        print(f"\n{sid}")
        print("-" * 86)
        for dim_label in [d[1] for d in DIMS] + ["Per-holding"]:
            r = per_dim.get(dim_label)
            if not r:
                continue
            if dim_label == "Per-holding":
                latest = r["latest"]
                sev = severity(latest, args.tolerance)
                col = color_for(sev)
                ic = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[sev]
                if sev == "RED":
                    any_red = True
                grand_total += 1
                if sev == "GREEN":
                    grand_within += 1
                note = r.get("note", "")
                print(f"  {ic} {col}{dim_label:<12}{END} latest = {latest:>6.1f} ({r['n_buckets']} holdings) {DIM}{note}{END}")
            else:
                tot = r["total_weeks"]
                mn, mx, avg = r["min"], r["max"], r["avg"]
                latest = r["latest"]
                cts = r["counts"]
                green_pct = 100 * cts["GREEN"] / tot if tot else 0
                # Aggregate severity for this row
                if cts["RED"] > 0:
                    rowsev = "RED"; any_red = True
                elif cts["YELLOW"] > 0:
                    rowsev = "YELLOW"
                else:
                    rowsev = "GREEN"
                ic = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[rowsev]
                col = color_for(rowsev)
                grand_total += tot
                grand_within += cts["GREEN"]
                print(f"  {ic} {col}{dim_label:<12}{END} {tot:>4} weeks · range {mn:>6.1f}-{mx:>6.1f} · avg {avg:>6.1f} · latest {latest:>6.1f}")
                print(f"     {DIM}within ±{args.tolerance:.0f}%: {cts['GREEN']:>4}/{tot} ({green_pct:>5.1f}%)  yellow {cts['YELLOW']:>3}  red {cts['RED']:>3}  worst {r['worst_date']}: {r['worst_value']:>6.1f}{END}")

    # Final score
    pct = 100 * grand_within / grand_total if grand_total else 100
    if pct >= 95:
        score_col, score_ic = G, "🟢"
    elif pct >= 85:
        score_col, score_ic = Y, "🟡"
    else:
        score_col, score_ic = R, "🔴"

    print()
    print("=" * 86)
    print(f"DATA INTEGRITY SCORE: {score_ic} {score_col}{pct:>5.1f}%{END}  ({grand_within:,} / {grand_total:,} cells within ±{args.tolerance:.0f}%)")
    print("=" * 86)

    if any_red and args.strict:
        print(f"\n{R}STRICT mode: RED findings present, exiting 1{END}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
