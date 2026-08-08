#!/bin/bash
# SessionStart hook: warn the model when context/current-priorities.md is past
# its self-declared 14-day refresh trigger. Silent when fresh. Fail-open on any
# error — a broken staleness check must never block a session.
set -u

F="${CLAUDE_PROJECT_DIR:-.}/context/current-priorities.md"
[ -f "$F" ] || exit 0
NOW=$(date +%s) || exit 0
# stat differs between macOS/BSD (-f %m) and GNU/Linux (-c %Y); try both.
MTIME=$(stat -f %m "$F" 2>/dev/null || stat -c %Y "$F" 2>/dev/null) || exit 0
[ -n "$MTIME" ] || exit 0
AGE_DAYS=$(( (NOW - MTIME) / 86400 ))
if [ "$AGE_DAYS" -ge 14 ]; then
  jq -cn --arg c "STALE CONTEXT: context/current-priorities.md is ${AGE_DAYS} days old — past its 14-day refresh trigger. Do not trust its status claims; verify against your live task system and records, and offer the user a refresh before planning work." \
    '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}' 2>/dev/null
fi
exit 0
