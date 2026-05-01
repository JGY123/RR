#!/bin/bash
# load_multi_account.sh — safely load a multi-account file while preserving
# the previously-vetted EM full history.
#
# WHAT IT DOES:
#   1. Backs up the current latest_data.json (which has EM full history) to
#      em_full_history.json
#   2. Auto-converts xlsx → csv if needed
#   3. Runs the standard ./load_data.sh pipeline (parser + verifier)
#   4. Calls merge_em_history.py to either:
#      - Replace EM in the new file with the backup's EM (if backup has more
#        weekly history), OR
#      - Add EM from backup if multi-account file doesn't include EM, OR
#      - Leave new file as-is (if multi-account file has equal/better EM)
#
# USAGE:
#   ./load_multi_account.sh ~/Downloads/risk_reports_sample.csv
#   ./load_multi_account.sh ~/Downloads/file.xlsx
#
# OUTPUT:
#   Writes latest_data.json with the multi-account file's data + EM full
#   history preserved. Opens the dashboard in Chrome at the end.

set -e

if [ -z "$1" ]; then
  echo "Usage: ./load_multi_account.sh <file.csv|file.xlsx>"
  echo ""
  echo "Recent CSV/xlsx files in ~/Downloads/:"
  ls -lt ~/Downloads/ 2>/dev/null | grep -E '\.(csv|xlsx)$' | head -8 | awk '{printf "  %s  %s  %s %s %s\n", $5, $9, $6, $7, $8}'
  exit 1
fi

FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LATEST="$SCRIPT_DIR/latest_data.json"
EM_BACKUP="$SCRIPT_DIR/em_full_history.json"

if [ ! -f "$FILE" ]; then
  echo "ERROR: file not found: $FILE"
  exit 1
fi

echo "──────────────────────────────────────────────────────────────────────"
echo " MULTI-ACCOUNT LOADER (preserves EM full history)"
echo "──────────────────────────────────────────────────────────────────────"
echo " Source file:  $FILE"
echo " Size:         $(du -h "$FILE" | awk '{print $1}')"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

# Step 1: backup current EM full history
if [ -f "$LATEST" ]; then
  cp "$LATEST" "$EM_BACKUP"
  echo "✓ Backed up current latest_data.json → em_full_history.json"
  EM_SIZE=$(du -h "$EM_BACKUP" | awk '{print $1}')
  echo "  ($EM_SIZE — this is the EM full-history snapshot we'll merge back if needed)"
else
  echo "⚠ No existing latest_data.json — nothing to back up. Multi-account file will be the only source."
fi
echo ""

# Step 2: convert xlsx → csv if needed
if [[ "$FILE" == *.xlsx ]]; then
  CSV_FILE="${FILE%.xlsx}.csv"
  if [ ! -f "$CSV_FILE" ] || [ "$FILE" -nt "$CSV_FILE" ]; then
    echo "→ Converting xlsx → csv (this can take 60-120s for files >1GB)..."
    python3 << PYEOF
import openpyxl, csv, time
t0 = time.time()
wb = openpyxl.load_workbook("$FILE", read_only=True, data_only=True)
ws = wb.active
n = 0
with open("$CSV_FILE", "w", newline="") as f:
    w = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        w.writerow([("" if c is None else c) for c in row])
        n += 1
        if n % 50000 == 0:
            print(f"  ... {n:,} rows ({time.time()-t0:.1f}s)")
print(f"✓ Wrote {n:,} rows to $CSV_FILE in {time.time()-t0:.1f}s")
PYEOF
  else
    echo "✓ CSV conversion already up-to-date: $CSV_FILE"
  fi
  FILE="$CSV_FILE"
fi
echo ""

# Step 3: run the standard parser pipeline (parser + verifier + opens dashboard)
echo "→ Running parser + verifier on $FILE ..."
echo "  (Large multi-account files: parsing can take 5-15 minutes; verifier auto-runs at the end.)"
echo ""

# Pass --no-open so we don't open the dashboard until after the merge step
"$SCRIPT_DIR/load_data.sh" "$FILE"

echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo " STEP 4 — MERGE EM FULL HISTORY"
echo "──────────────────────────────────────────────────────────────────────"

# Step 4: merge EM full history if needed
python3 "$SCRIPT_DIR/merge_em_history.py"

echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo " DONE — latest_data.json is ready"
echo "──────────────────────────────────────────────────────────────────────"
echo ""
echo "Next: hard-refresh the dashboard (Cmd+Shift+R)."
echo "       The browser tab that load_data.sh opened should auto-load the merged JSON."
echo ""
