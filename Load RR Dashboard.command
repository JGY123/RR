#!/bin/bash
# Redwood Risk — One-click CSV → Dashboard
# Drag a FactSet CSV onto this file, or double-click to pick the latest CSV in Downloads

cd "$(dirname "$0")"

# If a file was dragged onto this script, use it
if [ -n "$1" ]; then
  CSV_FILE="$1"
else
  # Find the most recent risk/factset CSV in Downloads
  CSV_FILE=$(ls -t ~/Downloads/*risk* ~/Downloads/*Risk* ~/Downloads/*factset* ~/Downloads/*FactSet* 2>/dev/null | grep -i '\.csv$\|\.txt$' | head -1)

  if [ -z "$CSV_FILE" ]; then
    echo "❌ No CSV found. Either:"
    echo "   1. Drag a CSV file onto this script"
    echo "   2. Put the FactSet CSV in ~/Downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
  fi
fi

echo "═══════════════════════════════════════"
echo "  Redwood Risk — Loading Dashboard"
echo "═══════════════════════════════════════"
echo ""
echo "  CSV:  $CSV_FILE"
echo "  Parsing..."
echo ""

# Parse CSV → JSON
python3 factset_parser.py "$CSV_FILE" latest_data.json 2>&1 | tail -20

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Parser failed. Check the CSV format."
  read -p "Press Enter to exit..."
  exit 1
fi

echo ""
echo "  ✅ JSON ready: latest_data.json"
echo "  📊 Opening dashboard..."
echo ""

# Open dashboard in default browser
open dashboard_v7.html

echo "  Drag latest_data.json onto the dashboard upload zone."
echo "  File is at: $(pwd)/latest_data.json"
echo ""

# Also reveal the JSON in Finder for easy drag
open -R latest_data.json

echo "  Done! Finder is showing the JSON file — drag it in."
