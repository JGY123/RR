#!/bin/bash
# load_data.sh — Parse FactSet CSV exports and launch the dashboard
# Usage: ./load_data.sh [path/to/factset.csv]
#
# If no CSV path is given, looks for the most recent *.csv in ~/Downloads.
# Output JSON is placed at ~/RR/latest_data.json and opened in the browser.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARSER="$SCRIPT_DIR/factset_parser.py"
OUTPUT="$SCRIPT_DIR/latest_data.json"
DASHBOARD="$SCRIPT_DIR/dashboard_v7.html"

# --- Find CSV input ---
if [ $# -ge 1 ]; then
  CSV="$1"
else
  CSV=$(ls -t ~/Downloads/*.csv 2>/dev/null | head -1)
  if [ -z "$CSV" ]; then
    echo "ERROR: No CSV file found in ~/Downloads. Pass a path explicitly."
    echo "Usage: $0 path/to/factset_export.csv"
    exit 1
  fi
fi

if [ ! -f "$CSV" ]; then
  echo "ERROR: File not found: $CSV"
  exit 1
fi

echo "Parsing: $CSV"
echo "Output:  $OUTPUT"
echo ""

python3 "$PARSER" "$CSV" "$OUTPUT"

# Run the FactSet test-pull verifier against the parsed JSON.
# Produces a structured pass/fail report against every call-deck ask.
# Captures output to a log so we can re-read; non-fatal so the dashboard still opens.
echo ""
echo "Running FactSet verifier (verify_factset.py)..."
VERIFY_LOG="$SCRIPT_DIR/last_verify_report.log"
if python3 "$SCRIPT_DIR/verify_factset.py" "$OUTPUT" "$CSV" 2>&1 | tee "$VERIFY_LOG"; then
  echo "  ✓ Verifier passed — see $VERIFY_LOG for full report"
else
  echo "  ⚠ Verifier flagged issues — see $VERIFY_LOG"
fi

echo ""
echo "Starting local http server (so fetch() can auto-load the JSON)..."
# B115 (2026-04-27): serve via http://localhost so fetch() works for auto-load.
# file:// protocol blocks fetch() for security — page falls through to upload zone.
PORT=3099

# Check if port is already serving the RR directory; reuse if so, else start
if lsof -i ":${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "  Reusing existing http server on port ${PORT}"
else
  # Start in the RR directory so latest_data.json is at the root
  (cd "$SCRIPT_DIR" && nohup python3 -m http.server "$PORT" >/tmp/rr_http.log 2>&1 &)
  sleep 1
  echo "  Started http server (PID $!) — log: /tmp/rr_http.log"
fi

echo ""
echo "Opening dashboard in a fresh Chrome window..."
TIMESTAMP=$(date +%s)
DASHBOARD_URL="http://localhost:${PORT}/dashboard_v7.html?t=${TIMESTAMP}"

if [ -d "/Applications/Google Chrome.app" ]; then
  # Close any existing tabs pointing at the dashboard
  osascript <<EOF 2>/dev/null || true
tell application "Google Chrome"
  set windowList to every window
  repeat with w in windowList
    set tabList to every tab of w
    repeat with t in tabList
      if URL of t contains "dashboard_v7.html" then
        close t
      end if
    end repeat
  end repeat
end tell
EOF
  open -na "Google Chrome" --args --new-window "${DASHBOARD_URL}"
else
  open "${DASHBOARD_URL}"
fi
echo "✓ Opened ${DASHBOARD_URL}"
echo "  Auto-loads latest_data.json — wait ~1s, check DevTools console for ✓ B115 integrity check."
echo "  If anything looks off, hard-refresh with Cmd+Shift+R."
