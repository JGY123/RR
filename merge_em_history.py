#!/usr/bin/env python3
"""
merge_em_history.py — preserve EM full history when loading the multi-account file.

After ./load_data.sh runs on the new multi-account file:
  - latest_data.json has all strategies from the multi-account run
  - em_full_history.json has the previously-vetted EM full history (backup
    of the prior latest_data.json)

This script:
  1. Compares EM in both files
  2. Picks whichever has MORE weekly history
  3. Keeps the multi-account version of all other strategies
  4. Writes back to latest_data.json

Run once after `./load_multi_account.sh` (which calls this automatically).
"""
import json, os, sys

RR_DIR = os.path.expanduser('~/RR')
LATEST = os.path.join(RR_DIR, 'latest_data.json')
BACKUP = os.path.join(RR_DIR, 'em_full_history.json')


def _strats(data):
    """Extract strategy dict from the parser's 4-element list shape."""
    if isinstance(data, list):
        return data[0]
    return data.get('strategies', data)


def _set_strats(data, strats):
    """Re-attach strategy dict in the parser's 4-element list shape."""
    if isinstance(data, list):
        data[0] = strats
    else:
        data['strategies'] = strats
    return data


def _hist_weeks(strategy):
    """Count weekly history entries for a strategy."""
    if not strategy:
        return 0
    hist = strategy.get('hist') or {}
    return len(hist.get('summary') or [])


def main():
    if not os.path.exists(LATEST):
        print(f'ERROR: {LATEST} does not exist. Run ./load_data.sh first.')
        sys.exit(1)

    if not os.path.exists(BACKUP):
        print('No backup at em_full_history.json — nothing to merge.')
        print('(Expected if this is the first run. Multi-account file is now active.)')
        sys.exit(0)

    new = json.load(open(LATEST))
    old = json.load(open(BACKUP))

    new_strats = _strats(new)
    old_strats = _strats(old)

    print('\n=== EM HISTORY MERGE ===')
    print(f'  Multi-account file: {sorted(new_strats.keys())}')
    print(f'  Backup (EM-only):   {sorted(old_strats.keys())}')

    new_em = new_strats.get('EM')
    old_em = old_strats.get('EM')

    new_em_weeks = _hist_weeks(new_em)
    old_em_weeks = _hist_weeks(old_em)

    print(f'\n  EM history in multi-account: {new_em_weeks} weeks')
    print(f'  EM history in backup:        {old_em_weeks} weeks')

    if old_em is None:
        print('\n  ⚠ Backup has no EM strategy. Multi-account file is final.')
    elif new_em is None:
        print(f'\n  → Multi-account file has no EM. Adding EM from backup ({old_em_weeks} weeks).')
        new_strats['EM'] = old_em
        new = _set_strats(new, new_strats)
        json.dump(new, open(LATEST, 'w'))
        print('  ✓ MERGED. latest_data.json now has multi-account + EM full history.')
    elif old_em_weeks > new_em_weeks:
        print(f'\n  → Backup has MORE EM history ({old_em_weeks} > {new_em_weeks}). Replacing EM with backup version.')
        new_strats['EM'] = old_em
        new = _set_strats(new, new_strats)
        json.dump(new, open(LATEST, 'w'))
        print('  ✓ MERGED. latest_data.json now has multi-account + EM full history.')
    else:
        print(f'\n  ✓ Multi-account file has equal-or-better EM history. No merge needed.')

    # Final summary
    final = json.load(open(LATEST))
    final_strats = _strats(final)
    print('\n=== FINAL latest_data.json ===')
    for sid in sorted(final_strats.keys()):
        s = final_strats[sid]
        weeks = _hist_weeks(s)
        n_hold = len(s.get('hold') or [])
        sum_d = s.get('sum') or {}
        te = sum_d.get('te')
        ad = s.get('available_dates') or []
        date_range = f'{ad[0]}→{ad[-1]}' if ad else '—'
        print(f'  {sid:>6}: {weeks:>4} wk · {n_hold:>4} hold · TE={te} · {date_range}')


if __name__ == '__main__':
    main()
