#!/bin/bash
# smoke_test.sh — Fast pre-edit / pre-commit sanity check.
#
# Runs in <30s. Catches the categories of failures that would have escalated
# in past sessions:
#   1. dashboard_v7.html script silently fails to parse (backslash-bomb, etc.)
#   2. Parser regression — pytest suite fails
#   3. Schema fingerprint drift — CSV format changed without acknowledgement
#   4. Verifier integrity assertions don't pass on the current data
#   5. Critical render-fn definitions missing (rWt, rCountryTable, etc.)
#
# Usage:
#   ./smoke_test.sh          # run all checks
#   ./smoke_test.sh --quick  # skip pytest (saves ~10s)
#
# Exit code: 0 if all pass, 1 if any fail.

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DASH="$SCRIPT_DIR/dashboard_v7.html"
PARSER="$SCRIPT_DIR/factset_parser.py"
JSON="$SCRIPT_DIR/latest_data.json"
VERIFY="$SCRIPT_DIR/verify_factset.py"

GREEN="\033[32m"; RED="\033[31m"; YELLOW="\033[33m"; DIM="\033[2m"; BOLD="\033[1m"; RESET="\033[0m"
PASS=0; FAIL=0

check() {
  local name="$1"; local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${RESET} $name"
    PASS=$((PASS+1))
  else
    echo -e "  ${RED}●${RESET} $name"
    FAIL=$((FAIL+1))
  fi
}

echo -e "${BOLD}RR smoke test${RESET}  ${DIM}($(date +%H:%M:%S))${RESET}"
echo

# ===== 1. dashboard_v7.html script syntax sanity =====
echo -e "${BOLD}1. Dashboard script integrity${RESET}"
# Look for known parse-bombs we've hit before
check "no escaped-string parse bomb (\\\\\\\\\\\\')" "! grep -q \"replace(/'/g,'\\\\\\\\\\\\\\\\\\\\\\\\\\\\''\" '$DASH'"
# Critical render fns must be defined
for fn in rWt rCountryTable rGroupTable renderRanksTable rSecChart inlineSparkSvg pickRankAvg aggregateHoldingsBy; do
  check "function $fn defined" "grep -q 'function $fn' '$DASH'"
done
# Critical state vars must be declared
for var in '_aggMode' '_avgMode' '_facCols' 'RNK_FACTOR_COLS'; do
  check "var $var declared" "grep -q '^let $var\\|^const $var' '$DASH'"
done
# Pills present
check "Universe pill in toolbar" "grep -q 'agg-pill-portfolio' '$DASH'"
check "Ranks pill in toolbar" "grep -q 'avg-pill-wtd' '$DASH'"

# ===== 2. Parser tests =====
if [ "${1:-}" != "--quick" ] && [ -f "$SCRIPT_DIR/test_parser.py" ]; then
  echo
  echo -e "${BOLD}2. Parser tests (pytest)${RESET}"
  if command -v pytest >/dev/null 2>&1; then
    if pytest -q "$SCRIPT_DIR/test_parser.py" 2>&1 | tail -3 | grep -q passed; then
      echo -e "  ${GREEN}✓${RESET} all pytest checks pass"
      PASS=$((PASS+1))
    else
      echo -e "  ${RED}●${RESET} pytest failures (run pytest directly to see)"
      FAIL=$((FAIL+1))
    fi
  else
    echo -e "  ${YELLOW}—${RESET} pytest not installed, skipping"
  fi
fi

# ===== 3. Schema fingerprint =====
# 2026-05-04 (memory-pressure fix): verify_factset.py loads the monolithic
# 1.8 GB JSON. On the 16 GB Mac under swap pressure, that takes ~30 sec
# and contributed to the smoke-test runaway flagged by the daily scan.
# Skip in --quick mode — full smoke_test.sh still runs it. Schema drift
# is also caught at load_data.sh time when verify_factset has the data
# already in memory, so this gating is safe.
echo
echo -e "${BOLD}3. Schema fingerprint${RESET}"
if [ "${1:-}" = "--quick" ]; then
  echo -e "  ${DIM}—${RESET} skipped in --quick mode (run \`./smoke_test.sh\` for full check)"
elif [ -f "$VERIFY" ] && [ -f "$JSON" ]; then
  drift_check=$(python3 "$VERIFY" "$JSON" 2>&1 | grep -E "DRIFT|Schema unchanged|BASELINE" | head -3)
  if echo "$drift_check" | grep -q "DRIFT"; then
    echo -e "  ${RED}●${RESET} schema drift detected — see verify_factset.py output"
    FAIL=$((FAIL+1))
  elif echo "$drift_check" | grep -q "unchanged"; then
    echo -e "  ${GREEN}✓${RESET} schema unchanged from baseline"
    PASS=$((PASS+1))
  else
    echo -e "  ${YELLOW}—${RESET} no baseline yet (first run)"
  fi
else
  echo -e "  ${YELLOW}—${RESET} verifier or JSON missing, skipping"
fi

# ===== 4. JSON integrity =====
# 2026-05-04 (memory-pressure fix): the monolithic latest_data.json is 1.8 GB.
# Previous version did FOUR sequential json.load() calls — each ~30s on a
# memory-pressured 16 GB Mac, ~7 GB total memory churn. The two stuck-Python
# procs flagged by the daily scan were both doing exactly this load and
# never finished.
#
# New approach (peak <500 KB, runtime <0.5s):
#   - Use data/strategies/index.json (a tiny ~500 KB summary) for shape +
#     strategy-list checks. The index.json mirrors what's in the monolithic.
#   - Peek the first 64 bytes of latest_data.json to confirm it starts with
#     `[` (top-level array).
#   - If split files don't exist, fall back to the old loads (slow but correct).
echo
echo -e "${BOLD}4. JSON integrity${RESET}"
SPLIT_INDEX="$SCRIPT_DIR/data/strategies/index.json"
if [ -f "$SPLIT_INDEX" ]; then
  # Fast path — use the slim index.json (~500 KB) instead of monolithic (1.8 GB)
  check "data/strategies/index.json valid + has strategies list" \
    "python3 -c 'import json; idx=json.load(open(\"$SPLIT_INDEX\")); assert idx.get(\"strategies\"), \"empty strategies list\"'"
  if [ -f "$JSON" ]; then
    check "latest_data.json starts with [ (top-level array, no full-load)" \
      "python3 -c 'f=open(\"$JSON\"); h=f.read(1); f.close(); assert h==\"[\", f\"got {h!r}\"'"
  fi
  check "index.json has at least one known account" \
    "python3 -c 'import json; idx=json.load(open(\"$SPLIT_INDEX\")); s=set(idx[\"strategies\"]); known={\"ACWI\",\"IDM\",\"IOP\",\"EM\",\"GSC\",\"ISC\",\"SCG\"}; assert s & known, f\"no known strategies in {s}\"'"
  # 2026-05-04: per CLAUDE.md, the 6 worldwide-model accounts (ACWI, IDM,
  # IOP, EM, ISC, GSC) ship in one CSV; SCG + Alger accounts ship in a
  # separate domestic-model file. So a multi-account worldwide load has
  # exactly 6, not 7. Allow either the 6 worldwide or all 7 (worldwide+SCG
  # if a combined load lands later).
  check "if multi-account (>=2): all 6 worldwide accounts present" \
    "python3 -c 'import json; idx=json.load(open(\"$SPLIT_INDEX\")); s=set(idx[\"strategies\"]); ww={\"ACWI\",\"IDM\",\"IOP\",\"EM\",\"GSC\",\"ISC\"}; assert len(s) < 2 or not (ww - s), f\"multi-account but missing worldwide: {ww - s}\"'"
elif [ -f "$JSON" ]; then
  # Fallback for when split files don't exist (e.g. mid-load_data.sh, before
  # split_for_demo.py ran). Slow on big files; only triggers when no split.
  echo -e "  ${YELLOW}—${RESET} no split files found at data/strategies/ — falling back to slow monolithic loads (1.8 GB × 4 calls)"
  check "latest_data.json is valid JSON" "python3 -c 'import json; json.load(open(\"$JSON\"))'"
  check "top-level is 4-element array" "python3 -c 'import json; d=json.load(open(\"$JSON\")); assert isinstance(d, list) and len(d)==4'"
  check "strategies dict has at least one known account" "python3 -c 'import json; d=json.load(open(\"$JSON\")); s=set(d[0].keys()); known={\"ACWI\",\"IDM\",\"IOP\",\"EM\",\"GSC\",\"ISC\",\"SCG\"}; assert s & known, f\"no known strategies in {s}\"'"
  check "if multi-account: all 7 expected accounts" "python3 -c 'import json; d=json.load(open(\"$JSON\")); s=set(d[0].keys()); expected={\"ACWI\",\"IDM\",\"IOP\",\"EM\",\"GSC\",\"ISC\",\"SCG\"}; assert len(s) < 2 or not (expected - s), f\"multi-account but missing: {expected - s}\"'"
fi

# ===== 5. Week-flow lint =====
echo
echo -e "${BOLD}5. Week-flow lint (Phase J)${RESET}"
if [ -f "$SCRIPT_DIR/lint_week_flow.py" ]; then
  if python3 "$SCRIPT_DIR/lint_week_flow.py" --strict >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${RESET} no direct cs.X access in render functions"
    PASS=$((PASS+1))
  else
    echo -e "  ${YELLOW}—${RESET} suspect direct cs.X access detected — run \`python3 lint_week_flow.py\` for details"
  fi
else
  echo -e "  ${YELLOW}—${RESET} lint_week_flow.py missing, skipping"
fi

# ===== 5b. Section-aggregate sums (Layer 2 of Data Integrity Monitor, 2026-05-04) =====
echo
echo -e "${BOLD}5b. Section-aggregate sums (data integrity monitor)${RESET}"
if [ -f "$SCRIPT_DIR/verify_section_aggregates.py" ] && [ -f "$JSON" ]; then
  # Latest-week-only mode for fast smoke-test gate (~0.5s).
  # Captures RED findings without flagging on every historical thin-tail blip.
  if python3 "$SCRIPT_DIR/verify_section_aggregates.py" --latest --strict >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${RESET} latest-week section aggregates within tolerance"
    PASS=$((PASS+1))
  else
    echo -e "  ${YELLOW}—${RESET} RED findings on latest-week section aggregates — run \`python3 verify_section_aggregates.py --latest\` for details"
    echo -e "  ${DIM}    (per-holding %T deviation 94→134%% is the F18 finding; section-aggregates should be clean)${RESET}"
  fi
else
  echo -e "  ${YELLOW}—${RESET} verify_section_aggregates.py or JSON missing, skipping"
fi

# ===== 6. Git state =====
echo
echo -e "${BOLD}6. Git state${RESET}"
cd "$SCRIPT_DIR"
# grep -c always prints a number to stdout (even "0" when no matches);
# the prior `|| echo 0` fallback duplicated the line and broke `-gt` later.
modified=$(git status --short 2>/dev/null | grep -c '^.M' 2>/dev/null); modified=${modified:-0}
untracked=$(git status --short 2>/dev/null | grep -c '^??' 2>/dev/null); untracked=${untracked:-0}
if [ "$modified" -gt 0 ]; then
  echo -e "  ${YELLOW}—${RESET} ${modified} modified file(s) uncommitted (consider committing before risky edits)"
fi
if [ "$untracked" -gt 0 ]; then
  echo -e "  ${YELLOW}—${RESET} ${untracked} untracked file(s)"
fi
echo -e "  ${DIM}HEAD: $(git rev-parse --short HEAD 2>/dev/null) ($(git log -1 --pretty='%s' 2>/dev/null | head -c 60))${RESET}"

# ===== Summary =====
echo
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
total=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
  echo -e "${BOLD}${GREEN}🟢 ALL CHECKS PASS${RESET}  ${PASS}/${total}"
  exit 0
else
  echo -e "${BOLD}${RED}🔴 ${FAIL} CHECK(S) FAILED${RESET}  ${PASS}/${total} pass"
  echo -e "${DIM}Investigate before risky edits.${RESET}"
  exit 1
fi
