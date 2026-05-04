#!/usr/bin/env python3
"""
merge_cumulative.py — B114 cumulative-history merge CLI.

Append-only ingest pipeline. Reads a fresh parser output (monolithic
latest_data.json or per-strategy split) + the existing per-strategy split
files at data/strategies/<ID>.json, and merges new weeks into existing.

Usage:
    # Merge a fresh monolithic ingest into per-strategy cumulative files:
    python3 merge_cumulative.py --new latest_data.json [--source-csv path.csv]

    # Merge specific strategy file (advanced):
    python3 merge_cumulative.py --new-strategy IDM=path/to/idm_new.json --source-csv path.csv

    # Dry-run: show what would change without writing:
    python3 merge_cumulative.py --new latest_data.json --dry-run

    # Force rebuild from new (skip merge — use sparingly, loses history):
    python3 merge_cumulative.py --new latest_data.json --replace

Behavior:
  - For each strategy in `new`:
      * If data/strategies/<ID>.json exists, MERGE new into existing
        (new-wins on overlapping dates; existing-only history preserved).
      * If not, create fresh data/strategies/<ID>.json.
  - Writes back per-strategy + updates data/strategies/index.json with
    fresh slim summaries.
  - Stamps merge_history[] audit trail on every merge.
  - PRINTS a summary of weeks added / overwritten per strategy.

Conflict policy: new-wins (default). When the same date appears in both
existing and new, the new value replaces the existing one. Per-strategy
top-level "current" arrays (sum, hold, sectors, factors) are always
replaced from the new ingest. Time-keyed history (hist.summary[],
hist.fac{}, hist.sec{}, etc.) is union by date.

This is the entry point for the load_multi_account.sh --merge flag.
"""
import argparse
import gzip
import json
import os
import sys
import time

# Import merge primitives from factset_parser.
import factset_parser as fp


def _load_json(path):
    """Load JSON or gzipped JSON."""
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write_json(path, obj):
    """Write JSON atomically (write + rename) to avoid partial files on crash."""
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(tmp, path)


def _build_index(strategies_dir, out_path):
    """Rebuild data/strategies/index.json — slim summaries for cheap loads."""
    summaries = {}
    strategies_list = []
    default_id = None
    report_date = None
    parse_stats = {"total_strategies": 0}
    fmt_version = None

    for fn in sorted(os.listdir(strategies_dir)):
        if not fn.endswith(".json") or fn == "index.json":
            continue
        sid = fn[:-5]
        path = os.path.join(strategies_dir, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                s = json.load(f)
        except Exception as e:
            print(f"  ! WARN: skipped {fn} — {e}")
            continue
        # Slim summary — drop heavy detail layers but keep enough for
        # cross-strategy aggregate checks + UI strategy picker.
        slim = {
            "id": s.get("id", sid),
            "name": s.get("name", sid),
            "benchmark": s.get("benchmark", ""),
            "current_date": s.get("current_date"),
            "available_dates": s.get("available_dates", []),
            "sum": s.get("sum", {}),
            "sectors": s.get("sectors", []),
            "countries": s.get("countries", []),
            "regions": s.get("regions", []),
            "groups": s.get("groups", []),
            "industries": s.get("industries", []),
            "factors": s.get("factors", []),
            "chars": s.get("chars", []),
            # hist.summary IS the slim per-week history (no per-week detail);
            # heavy hist.sec/ctry/etc. deliberately excluded — load on demand.
            "hist": {"summary": (s.get("hist") or {}).get("summary", [])},
            "_lazy": True,
        }
        summaries[sid] = slim
        strategies_list.append(sid)
        if default_id is None:
            default_id = sid
        cd = s.get("current_date")
        if cd and (not report_date or cd > report_date):
            report_date = cd
        if fmt_version is None:
            fmt_version = s.get("format_version")
    parse_stats["total_strategies"] = len(strategies_list)

    idx = {
        "strategies": strategies_list,
        "default": default_id,
        "report_date": report_date,
        "parse_stats": parse_stats,
        "summaries": summaries,
        "format_version": fmt_version,
        "split_at": fp._now_iso(),
    }
    _atomic_write_json(out_path, idx)


def _print_merge_summary(sid, hist_record, dry_run):
    """Print a one-line summary of the merge for a strategy."""
    if dry_run:
        prefix = "[dry-run]"
    else:
        prefix = "[merged]"
    wa = hist_record["weeks_added"]
    wo = hist_record["weeks_overwritten"]
    if wa == 0 and wo == 0:
        print(f"  {prefix} {sid}: no change (existing already covers new ingest's range)")
    elif wa > 0 and wo == 0:
        dr = hist_record.get("date_range") or [None, None]
        print(f"  {prefix} {sid}: +{wa} weeks added ({dr[0]} → {dr[1]})")
    elif wa == 0 and wo > 0:
        print(f"  {prefix} {sid}: {wo} weeks overwritten (no new dates, all overlap)")
    else:
        dr = hist_record.get("date_range") or [None, None]
        print(f"  {prefix} {sid}: +{wa} new ({dr[0]} → {dr[1]}) · {wo} overwritten")


def main():
    ap = argparse.ArgumentParser(description="B114 cumulative-history merge CLI")
    ap.add_argument("--new", help="Path to fresh monolithic JSON (e.g. latest_data.json)")
    ap.add_argument("--new-strategy", action="append", default=[],
                    help="Override one strategy with a fresh per-strategy JSON: ID=path/to/file.json (repeatable)")
    ap.add_argument("--source-csv", help="Source CSV path (recorded in merge_history audit trail)")
    ap.add_argument("--strategies-dir", default="data/strategies",
                    help="Directory containing per-strategy cumulative files (default: data/strategies)")
    ap.add_argument("--dry-run", action="store_true", help="Print what would change but don't write files")
    ap.add_argument("--replace", action="store_true",
                    help="Skip merge — write new ingest as-is (DESTROYS existing history; use with caution)")
    args = ap.parse_args()

    if not args.new and not args.new_strategy:
        ap.error("--new or --new-strategy is required")

    t0 = time.time()
    strategies_dir = args.strategies_dir
    os.makedirs(strategies_dir, exist_ok=True)

    # Collect new strategies dict {ID: strategy_dict}
    new_strats = {}
    if args.new:
        print(f"Loading new ingest from {args.new} ...")
        # Output is either a list-of-strategies (top-level array) or a dict
        # with "strategies": {...} layout. Handle both.
        new_blob = _load_json(args.new)
        if isinstance(new_blob, list):
            for s in new_blob:
                sid = s.get("id")
                if sid:
                    new_strats[sid] = s
        elif isinstance(new_blob, dict):
            if "strategies" in new_blob and isinstance(new_blob["strategies"], dict):
                new_strats.update(new_blob["strategies"])
            else:
                # Treat the dict itself as {ID: strategy_dict}
                for k, v in new_blob.items():
                    if isinstance(v, dict) and v.get("id") == k:
                        new_strats[k] = v
        print(f"  found {len(new_strats)} strategies in new ingest")

    for spec in args.new_strategy:
        if "=" not in spec:
            ap.error(f"--new-strategy format is ID=path, got: {spec}")
        sid, path = spec.split("=", 1)
        new_strats[sid] = _load_json(path)
        print(f"  loaded override {sid} from {path}")

    if not new_strats:
        print("ERROR: no strategies parsed from new ingest. Aborting.")
        sys.exit(1)

    # For each new strategy, load existing (if any), merge, write back.
    merged_any = False
    for sid in sorted(new_strats):
        new_s = new_strats[sid]
        existing_path = os.path.join(strategies_dir, f"{sid}.json")
        if args.replace:
            print(f"  --replace: overwriting {existing_path} with new ingest (history NOT preserved)")
            stamped = fp.merge_strategy_into_existing(new_s, None, source_csv=args.source_csv)
            if not args.dry_run:
                _atomic_write_json(existing_path, stamped)
            _print_merge_summary(sid, stamped["merge_history"][-1], args.dry_run)
            merged_any = True
            continue

        existing_s = None
        if os.path.exists(existing_path):
            try:
                existing_s = _load_json(existing_path)
            except Exception as e:
                print(f"  ! WARN: existing {existing_path} unreadable ({e}) — falling back to first-ingest.")

        merged = fp.merge_strategy_into_existing(new_s, existing_s, source_csv=args.source_csv)
        _print_merge_summary(sid, merged["merge_history"][-1], args.dry_run)
        if not args.dry_run:
            _atomic_write_json(existing_path, merged)
            merged_any = True

    # Rebuild index.json — only if we actually wrote files.
    if merged_any and not args.dry_run:
        idx_path = os.path.join(strategies_dir, "index.json")
        _build_index(strategies_dir, idx_path)
        print(f"  index.json rebuilt at {idx_path}")

    print()
    print(f"Done in {time.time() - t0:.1f}s. {'(dry-run, no writes)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
