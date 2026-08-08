#!/bin/bash
# sync.sh — commit workspace changes with a timestamped message.
# Commit-only by default so nothing leaves your machine unreviewed.
# Pass --push to also push to the CURRENT branch after committing.
set -e

# Resolve the repo root from this script's location (tools/ -> repo root).
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

git add -A
if git diff --cached --quiet; then
  echo "Nothing new to sync."
  exit 0
fi

git commit -m "Auto-sync from $(hostname) at $(date '+%Y-%m-%d %H:%M:%S')"

if [ "$1" = "--push" ]; then
  git push origin HEAD
else
  echo "Committed. Review and push manually, or re-run with --push."
fi
