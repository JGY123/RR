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
echo "Opening dashboard..."
open "$DASHBOARD"
