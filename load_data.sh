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

echo ""
echo "Opening dashboard in a fresh Chrome window..."
# B115 (2026-04-27): force a fresh Chrome window with cache-bust + close stale tabs.
# Plain `open dashboard.html` reuses any existing tab, leaving stale state.
TIMESTAMP=$(date +%s)
DASHBOARD_URL="file://${DASHBOARD}?t=${TIMESTAMP}"

if [ -d "/Applications/Google Chrome.app" ]; then
  # Close any existing tabs pointing at this dashboard file
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
  # Open in a new Chrome window with the cache-bust query string
  open -na "Google Chrome" --args --new-window "${DASHBOARD_URL}"
else
  open "${DASHBOARD_URL}"
fi
echo "✓ Opened ${DASHBOARD_URL}"
echo "If anything looks off, hard-refresh with Cmd+Shift+R."
