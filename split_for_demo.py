#!/usr/bin/env python3
"""
split_for_demo.py — split latest_data.json into per-strategy files for
browser-friendly lazy-loading.

Why: a 1.8GB combined JSON crashes Chrome's renderer (Aw, Snap! Error code 5).
Each strategy is only ~250-400MB → well within Chrome's per-tab memory limit.
Dashboard fetches one strategy at a time → no OOM, all data preserved.

What it writes:
    data/strategies/<ID>.json    one file per strategy, complete data
    data/strategies/index.json   tiny metadata: strategies list + default + per-strategy summaries (sum/sectors/factors only)

Usage:
    python3 split_for_demo.py             # preserves latest_data.json untouched
    python3 split_for_demo.py --remove    # also deletes the monolithic latest_data.json after split

After running:
    Hard-refresh dashboard (Cmd+Shift+R). It will detect the new structure and
    lazy-load the active strategy.
"""
import json, os, sys, time, argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', default='latest_data.json')
    ap.add_argument('--out-dir', default='data/strategies')
    ap.add_argument('--remove', action='store_true',
                    help='Delete the monolithic latest_data.json after successful split')
    args = ap.parse_args()

    rr_dir = os.path.dirname(os.path.abspath(__file__))
    in_path = os.path.join(rr_dir, args.input)
    out_dir = os.path.join(rr_dir, args.out_dir)

    if not os.path.exists(in_path):
        print(f'ERROR: {in_path} not found.')
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    in_size = os.path.getsize(in_path) / 1e9
    print(f'Input:  {in_path}  ({in_size:.2f} GB)')
    print(f'Output dir: {out_dir}')
    print()

    print('Loading JSON ... (10-30 sec for 1-2 GB)')
    t0 = time.time()
    with open(in_path) as f:
        data = json.load(f)
    print(f'  ✓ Loaded in {time.time()-t0:.1f}s')

    # Extract strategies + meta from the parser's 4-element list shape
    if isinstance(data, list):
        strats = data[0]
        report_date = data[2] if len(data) > 2 else ''
        parse_stats = data[3] if len(data) > 3 else {}
    else:
        strats = data.get('strategies', data)
        report_date = data.get('report_date', '')
        parse_stats = data.get('parse_stats', {})

    print(f'Splitting {len(strats)} strategies ...')
    print()

    # Per-strategy summaries (cheap to load — drives the strategy dropdown + cross-strategy compare)
    summaries = {}
    for sid, s in strats.items():
        # Slim summary keeps everything except the largest sections
        summary = {
            'id': sid,
            'name': s.get('name', sid),
            'benchmark': s.get('benchmark', ''),
            'current_date': s.get('current_date'),
            'available_dates': s.get('available_dates', []),
            'sum': s.get('sum'),
            'sectors': s.get('sectors'),
            'countries': s.get('countries'),
            'regions': s.get('regions'),
            'groups': s.get('groups'),
            'industries': s.get('industries'),
            'factors': s.get('factors'),
            'chars': s.get('chars'),
            'hist': {
                'summary': (s.get('hist') or {}).get('summary', []),
                # NOTE: skip hist.fac/sec/ctry/ind/reg/grp/chars — they're in the heavy file
            },
            '_lazy': True,  # marker that hold/snap_attrib/raw_fac are in the heavy file
        }
        summaries[sid] = summary

        # Heavy file: everything (the dashboard will MERGE summary + heavy on load)
        # Strategy: write the FULL strategy dict to its own file. Index.json holds the summaries.
        heavy_path = os.path.join(out_dir, f'{sid}.json')
        t1 = time.time()
        with open(heavy_path, 'w') as f:
            json.dump(s, f, separators=(',', ':'))
        heavy_size = os.path.getsize(heavy_path) / 1e6
        weeks = len((s.get('hist') or {}).get('summary') or [])
        n_hold = len(s.get('hold') or [])
        sa_keys = len(s.get('snap_attrib') or {})
        print(f'  {sid}: {weeks:>4} wk · {n_hold:>5} hold · {sa_keys:>3} snap_attrib keys → {heavy_size:>7.1f} MB · {time.time()-t1:.1f}s')

    # Write index.json
    index = {
        'strategies': sorted(strats.keys()),
        'default': sorted(strats.keys())[0],
        'report_date': report_date,
        'parse_stats': parse_stats,
        'summaries': summaries,
        'format_version': '4.2-split',
        'split_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    index_path = os.path.join(out_dir, 'index.json')
    with open(index_path, 'w') as f:
        json.dump(index, f, separators=(',', ':'))
    index_size = os.path.getsize(index_path) / 1e6
    print()
    print(f'  index.json: {len(strats)} strategies, {index_size:.1f} MB (loads first on page open)')

    # Optionally remove the monolithic file
    if args.remove:
        os.remove(in_path)
        print(f'\n  ✓ Removed {in_path}')

    total_out = sum(os.path.getsize(os.path.join(out_dir, fn)) for fn in os.listdir(out_dir)) / 1e9
    print()
    print(f'Done. {total_out:.2f} GB total across {len(strats)+1} files.')
    print(f'Largest single file: ~{max(os.path.getsize(os.path.join(out_dir, f"{s}.json")) for s in strats) / 1e6:.0f} MB (well under Chrome\'s parse limit)')
    print()
    print('Next: hard-refresh the dashboard (Cmd+Shift+R).')
    print('      Dashboard will detect data/strategies/index.json and lazy-load.')


if __name__ == '__main__':
    main()
