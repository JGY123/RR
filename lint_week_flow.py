#!/usr/bin/env python3
"""
lint_week_flow.py — static lint to prevent week-flow regressions.

Catches the specific failure pattern from 2026-05-01: render functions
reading cs.sectors / cs.countries / cs.hold / cs.factors directly inside
template strings, bypassing the per-week-aware accessors (_wSec,
_wCtry, _wReg, _wGrp, _wInd, _wChars, _wFactors, getSelectedWeekSum).

When a renderer reads cs.X directly and the user picks a historical week,
the renderer ignores the selection — values stay at "latest" silently.
This is exactly the symptom user reported as "selector changes weights but
risk stays static."

Usage:
    python3 lint_week_flow.py              # standalone
    python3 lint_week_flow.py --strict     # exit 1 on warnings (CI gate)

What it checks:
  Within render functions (rExp, rRisk, rHold, rFac*, rChr, rAttribTable,
  rCountryTable, rGroupTable, rWt, riskHistoricalTrends, …), flags any
  reference to `cs.sectors`, `cs.countries`, `cs.regions`, `cs.groups`,
  `cs.industries`, `cs.factors`, `cs.chars` that is NOT inside a comment
  or a tooltip string.

  IGNORED (allowed):
    - Render functions that have an aggHold or _facsForWeek shadow var
      (these explicitly handle hist mode internally)
    - Comment lines (// ... cs.X)
    - data-tip="..." / title="..." string literals (tooltip text)
    - The wrappers themselves (_wSec returns cs.sectors when no week)

Output: list of (line, function, snippet) for each suspect access.
"""
from __future__ import annotations
import re
import sys
import os
from pathlib import Path


DASH = Path(__file__).parent / 'dashboard_v7.html'

# Render functions whose bodies we want to scan
RENDER_FNS = [
    'rExp', 'rRisk', 'rHold', 'rWt', 'rCountryTable', 'rGroupTable',
    'rChr', 'rAttribTable', 'rFac', 'rFacRisk', 'rFacTable',
    'riskHistoricalTrends', 'thisWeekCardHtml', 'rWeekOverWeek',
    'renderHoldTab',
]

# Direct cs.X access patterns we treat as suspect inside render bodies
SUSPECT_PATTERNS = [
    r'\bcs\.sectors\b',
    r'\bcs\.countries\b',
    r'\bcs\.regions\b',
    r'\bcs\.groups\b',
    r'\bcs\.industries\b',
    r'\bcs\.chars\b',
    r'\bcs\.factors\b',
    r'\bs\.sectors\b',       # when s = cs (rExp, rRisk start with `let s=cs`)
    r'\bs\.countries\b',
    r'\bs\.regions\b',
    r'\bs\.groups\b',
    r'\bs\.industries\b',
    r'\bs\.chars\b',
    r'\bs\.factors\b',
]

# Lines we ignore entirely
def is_ignored_line(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith('//'):
        return True
    if stripped.startswith('*'):  # JSDoc continuation
        return True
    # Per-line opt-out marker: append `// lint-week-flow:ignore` to the line
    # to silence the lint for an intentional latest-only access (e.g. legacy
    # fallback branch, factor list for toggle-checkbox labels).
    if 'lint-week-flow:ignore' in line:
        return True
    return False

# Parts of a line we mask before scanning (tooltips, comments-at-end, doc strings)
MASKABLE_RE = [
    re.compile(r'data-tip\s*=\s*"[^"]*"'),
    re.compile(r"data-tip\s*=\s*'[^']*'"),
    re.compile(r'title\s*=\s*"[^"]*"'),
    re.compile(r"title\s*=\s*'[^']*'"),
    re.compile(r'//[^\n]*$'),
    # Documentation registry strings (ABOUT_REGISTRY, _doc, _what, _how, _source)
    re.compile(r'(source|how|what|caveats|related|note)\s*:\s*[\'`"][^\'`"]*[\'`"]'),
]

def mask(line: str) -> str:
    for r in MASKABLE_RE:
        line = r.sub('""', line)
    return line


def find_function_ranges(src: str) -> dict[str, tuple[int, int]]:
    """Find (start_line, end_line) for each render function. Brace-counted."""
    ranges: dict[str, tuple[int, int]] = {}
    lines = src.split('\n')
    for fn in RENDER_FNS:
        # Find `function fn(` or `fn = function(` or `const fn = `
        pattern = re.compile(rf'^(?:function\s+{re.escape(fn)}\b|(?:const|let|var)\s+{re.escape(fn)}\s*=)')
        start_idx: int | None = None
        for i, ln in enumerate(lines):
            if pattern.search(ln):
                start_idx = i
                break
        if start_idx is None:
            continue
        # Brace-count from the line of the first { we see at or after start
        depth = 0
        seen_open = False
        end_idx = start_idx
        for i in range(start_idx, len(lines)):
            for ch in lines[i]:
                if ch == '{':
                    depth += 1
                    seen_open = True
                elif ch == '}':
                    depth -= 1
                    if seen_open and depth == 0:
                        end_idx = i
                        break
            if seen_open and depth == 0:
                break
        ranges[fn] = (start_idx, end_idx)
    return ranges


def scan(src: str) -> list[dict]:
    findings: list[dict] = []
    lines = src.split('\n')
    fn_ranges = find_function_ranges(src)
    compiled = [re.compile(p) for p in SUSPECT_PATTERNS]
    for fn, (start, end) in fn_ranges.items():
        for i in range(start, end + 1):
            ln = lines[i]
            if is_ignored_line(ln):
                continue
            masked = mask(ln)
            for pat in compiled:
                m = pat.search(masked)
                if not m:
                    continue
                findings.append({
                    'fn': fn,
                    'line': i + 1,
                    'pattern': m.group(0),
                    'snippet': ln.strip()[:140],
                })
                break
    return findings


def main():
    strict = '--strict' in sys.argv
    if not DASH.exists():
        print(f'ERROR: {DASH} not found', file=sys.stderr)
        sys.exit(2)
    src = DASH.read_text(encoding='utf-8')
    findings = scan(src)
    if not findings:
        print('\033[32m✓ week-flow lint OK — no suspect direct cs.X access in render functions\033[0m')
        sys.exit(0)
    print(f'\033[33m⚠ {len(findings)} suspect direct cs.X access(es) inside render functions:\033[0m')
    print()
    by_fn: dict[str, list[dict]] = {}
    for f in findings:
        by_fn.setdefault(f['fn'], []).append(f)
    for fn in sorted(by_fn):
        print(f'  \033[36m{fn}()\033[0m  ({len(by_fn[fn])} findings)')
        for f in by_fn[fn][:6]:
            print(f"    line {f['line']:>5}: \033[2m{f['pattern']:<14}\033[0m  {f['snippet']}")
        if len(by_fn[fn]) > 6:
            print(f"    \033[2m... {len(by_fn[fn]) - 6} more\033[0m")
        print()
    print(f'\033[33mFix: replace `cs.sectors` → `_wSec()`, `cs.countries` → `_wCtry()`, etc.\033[0m')
    print(f'\033[33m     For factors, use `_wFactors()`. For sum, use `getSelectedWeekSum()`.\033[0m')
    if strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
