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
echo
echo -e "${BOLD}3. Schema fingerprint${RESET}"
if [ -f "$VERIFY" ] && [ -f "$JSON" ]; then
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
echo
echo -e "${BOLD}4. JSON integrity${RESET}"
if [ -f "$JSON" ]; then
  check "latest_data.json is valid JSON" "python3 -c 'import json; json.load(open(\"$JSON\"))'"
  # Top-level shape: 4-element array
  check "top-level is 4-element array" "python3 -c 'import json; d=json.load(open(\"$JSON\")); assert isinstance(d, list) and len(d)==4'"
  # First element has at least one known strategy (single-account test files
  # only ship one strategy at a time — multi-account run will ship all 7).
  # 2026-04-30: relaxed from "must have all 7" → "must have at least one of
  # the 7 known IDs" so single-strategy test files (e.g. EM full-history)
  # don't fail this check.
  check "strategies dict has at least one known account" "python3 -c 'import json; d=json.load(open(\"$JSON\")); s=set(d[0].keys()); known={\"ACWI\",\"IDM\",\"IOP\",\"EM\",\"GSC\",\"ISC\",\"SCG\"}; assert s & known, f\"no known strategies in {s}\"'"
  # When in multi-account mode (>=2 strategies), all 7 should be present.
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
