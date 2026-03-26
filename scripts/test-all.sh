#!/usr/bin/env bash
# Run unit tests for all 10 CLIs.
# Usage: bash scripts/test-all.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
FAILED_CLIS=()

CLIS=(
  "futbin:futbin"
  "notebooklm:notebooklm"
  "gh-trending:gh_trending"
  "producthunt:producthunt"
  "unsplash:unsplash"
  "booking:booking"
  "stitch:stitch"
  "pexels:pexels"
  "reddit:reddit"
  "gai:gai"
)

for entry in "${CLIS[@]}"; do
  dir="${entry%%:*}"
  pkg="${entry##*:}"
  test_file="$REPO_ROOT/$dir/agent-harness/cli_web/$pkg/tests/test_core.py"

  if [ ! -f "$test_file" ]; then
    echo "SKIP  cli-web-$dir — no test_core.py"
    continue
  fi

  echo ""
  echo "────────────────────────────────────────"
  echo "  cli-web-$dir"
  echo "────────────────────────────────────────"

  if python -m pytest "$test_file" -v --tb=short; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    FAILED_CLIS+=("cli-web-$dir")
  fi
done

echo ""
echo "════════════════════════════════════════"
echo "  Results: $PASS passed, $FAIL failed"
if [ ${#FAILED_CLIS[@]} -gt 0 ]; then
  echo "  Failed: ${FAILED_CLIS[*]}"
fi
echo "════════════════════════════════════════"

exit $FAIL
