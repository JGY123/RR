#!/usr/bin/env python3
"""
slim_for_demo.py — slim latest_data.json for browser-friendly load.

Why: a 1.8GB JSON tends to OOM/freeze Chrome's JSON.parse on the 6-strategy
multi-year file. This script trims the largest sections while preserving
every visible tile's data needs:

  PRESERVED (full):
    - cs.sum (latest week summary)
    - cs.hold[] (every holding with factor_contr, raw_exp, etc.)
    - cs.factors, cs.sectors, cs.countries, cs.regions, cs.groups, cs.chars
    - cs.hist.summary (weekly TE/AS/Beta/Holdings — small, all years kept)
    - cs.hist.sec, ctry, ind, reg, grp, chars (group-level history — small)
    - cs.hold_prev (week-over-week diff data)
    - cs.unowned, cs.ranks, cs.raw_fac

  TRIMMED:
    - cs.snap_attrib[name].hist → last 156 weeks (3 years) only
      (Was 360-620 weeks per factor × 120-170 factor keys × 6 strategies =
      most of the file size. 156 weeks is enough for cardCorr, cardFacHist,
      cardFacButt at "All" period — and the whole-history versions still
      fit if user wants to swap back.)

Usage:
    python3 slim_for_demo.py             # in-place: latest_data.json → latest_data.json
    python3 slim_for_demo.py --keep 78   # 18 months instead of 3 years
    python3 slim_for_demo.py --backup    # also writes latest_data_full.json before slimming

Reverting:
    cp latest_data_full.json latest_data.json   # if --backup was used
"""
import json, os, sys, time, argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', default='latest_data.json')
    ap.add_argument('--output', default='latest_data.json')
    ap.add_argument('--keep', type=int, default=156,
                    help='Keep this many trailing weeks of snap_attrib.hist per factor (default: 156 = 3 years)')
    ap.add_argument('--backup', action='store_true',
                    help='Write latest_data_full.json before slimming')
    args = ap.parse_args()

    rr_dir = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(rr_dir, args.input)
    out_path = os.path.join(rr_dir, args.output)
    backup_path = os.path.join(rr_dir, 'latest_data_full.json')

    if not os.path.exists(in_path):
        print(f'ERROR: {in_path} not found.')
        sys.exit(1)

    in_size = os.path.getsize(in_path) / 1e9
    print(f'Input:  {in_path}  ({in_size:.2f} GB)')

    if args.backup:
        if os.path.exists(backup_path):
            print(f'Backup already exists at {backup_path} — skipping (delete to re-backup)')
        else:
            print(f'Backing up → {backup_path} ...')
            with open(in_path, 'rb') as src, open(backup_path, 'wb') as dst:
                while True:
                    chunk = src.read(64 * 1024 * 1024)  # 64MB chunks
                    if not chunk:
                        break
                    dst.write(chunk)
            print(f'  ✓ Backed up')

    print(f'Loading JSON ... (5-30 seconds for 1-2 GB)')
    t0 = time.time()
    with open(in_path) as f:
        data = json.load(f)
    print(f'  ✓ Loaded in {time.time()-t0:.1f}s')

    strats = data[0] if isinstance(data, list) else data.get('strategies', data)

    keep = args.keep
    print(f'Slimming snap_attrib.hist to last {keep} weeks per factor ...')

    total_factors_processed = 0
    total_weeks_dropped = 0
    for sid, s in strats.items():
        sa = s.get('snap_attrib') or {}
        for fn, info in sa.items():
            hist = info.get('hist') or []
            if len(hist) > keep:
                dropped = len(hist) - keep
                total_weeks_dropped += dropped
                info['hist'] = hist[-keep:]
            total_factors_processed += 1
        # Final summary
        sa_keys = len(sa)
        n_hold = len(s.get('hold') or [])
        weeks = len((s.get('hist') or {}).get('summary') or [])
        print(f'  {sid}: {sa_keys} factor keys · {n_hold} holdings · {weeks} hist.summary weeks (full kept)')

    print(f'Trimmed {total_weeks_dropped:,} factor-weeks across {total_factors_processed:,} factor entries.')

    print(f'Writing output ... ')
    t0 = time.time()
    with open(out_path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))  # compact format saves more bytes
    out_size = os.path.getsize(out_path) / 1e9
    print(f'  ✓ Wrote in {time.time()-t0:.1f}s')
    print()
    print(f'Output: {out_path}  ({out_size:.2f} GB)')
    print(f'Reduction: {in_size:.2f} GB → {out_size:.2f} GB  ({100*(1-out_size/in_size):.0f}% smaller)')
    print()
    print('Now hard-refresh the dashboard (Cmd+Shift+R).')
    print()
    if args.backup:
        print(f'Full version backed up at: {backup_path}')
        print('To revert: cp latest_data_full.json latest_data.json')


if __name__ == '__main__':
    main()
