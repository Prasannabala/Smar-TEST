#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# record.sh — Launch Playwright codegen to record a test
#
# Usage:
#   npm run record                        # opens browser, no URL
#   npm run record -- https://myapp.com  # opens browser at a URL
#
# After recording:
#   1. Save the generated script to recordings/<my-test>.recording.ts
#   2. Annotate it with @scenario / @block / @data / @param / @end-block tags
#   3. Convert it:  npm run convert recordings/<my-test>.recording.ts
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

TARGET_URL="${1:-}"
OUTPUT_DIR="recordings"

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  Playwright Test Recorder                                   │"
echo "│                                                             │"
echo "│  Instructions:                                              │"
echo "│  1. Interact with the browser to record your test           │"
echo "│  2. Use the recorder toolbar to copy the generated code     │"
echo "│  3. Save it to: recordings/<name>.recording.ts              │"
echo "│  4. Add @block / @data / @param annotations                 │"
echo "│  5. Run: npm run convert recordings/<name>.recording.ts     │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

if [ -n "$TARGET_URL" ]; then
  echo "Opening: $TARGET_URL"
  npx playwright codegen "$TARGET_URL"
else
  echo "No URL provided — opening blank browser"
  npx playwright codegen
fi
