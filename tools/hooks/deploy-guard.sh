#!/bin/bash
# Deterministic deploy gates — PreToolUse hook on Bash.
#
# Enforces the house deployment rules mechanically instead of hoping the model
# remembers them:
#   - never `netlify link`/`unlink` (state files cause silent wrong-site deploys)
#   - every `netlify deploy` carries an explicit --site <SITE_ID>
#   - production deploys and pushes to main require an interactive confirmation
#
# Reads Claude Code hook JSON on stdin; emits permissionDecision JSON on stdout.
#
# Philosophy: FAIL-OPEN for convenience (unrelated commands pass on any script
# error), but the gates themselves FAIL-CLOSED — when a hard gate can't verify
# what it needs (missing jq, an unresolvable site ID), it denies or asks
# instead of assuming safety.
#
# Netlify is the worked example here. Deploying to Vercel/Cloudflare/anything
# else? Keep the shape — deny state-file footguns, require an explicit target,
# ask on production — and swap the command patterns for your host's CLI.
#
# REQUIRES: jq (brew install jq / apt install jq).
set -u

INPUT=$(cat 2>/dev/null) || exit 0

# Without jq we cannot parse the payload — but silently disabling the gates
# would be worse (security theater). Cheap raw-string prefilter: let clearly
# unrelated commands through, force a human decision on anything gate-shaped.
if ! command -v jq >/dev/null 2>&1; then
  if printf '%s' "$INPUT" | grep -qiE 'netlify|git[^a-z]+push'; then
    printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"deploy-guard cannot evaluate this command: jq is not installed (brew install jq). Gates on deploys and main pushes are unenforced until it is — confirm manually."}}'
  fi
  exit 0
fi

CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -z "$CMD" ] && exit 0

deny() {
  jq -cn --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}' 2>/dev/null
  exit 0
}
ask() {
  jq -cn --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}' 2>/dev/null
  exit 0
}

# netlify link/unlink write local state files that later deploys silently trust —
# the classic cause of deploying to the wrong site. Hard block.
if printf '%s' "$CMD" | grep -qE 'netlify[[:space:]]+(link|unlink)'; then
  deny "BLOCKED: never use netlify link/unlink — link state causes silent wrong-site deploys. Always pass --site <SITE_ID> explicitly on deploy."
fi

if printf '%s' "$CMD" | grep -qE 'netlify[[:space:]]+deploy'; then
  # --site is mandatory on every deploy. Never rely on link state.
  if ! printf '%s' "$CMD" | grep -qE -- '--site([[:space:]=])'; then
    deny "BLOCKED: netlify deploy without --site <SITE_ID>. Add the explicit --site flag (never rely on link state)."
  fi

  SITE_VAL=$(printf '%s' "$CMD" | sed -nE 's/.*--site[= ]+"?([^" ]+)"?.*/\1/p')

  # ------------------------------------------------------------------------
  # EXAMPLE: client-specific compliance gate (commented out — adapt to yours).
  #
  # If a client's deploys must pass a compliance/legal/brand scan first (e.g.
  # financing-language rules, regulated-industry copy review), gate it here.
  # Detect the client by name in the command/cwd OR by their known site IDs,
  # then require a fresh scan report on disk before allowing the deploy:
  #
  #   CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
  #   HAY="$CMD $CWD"
  #   if printf '%s' "$HAY" | grep -qiE '<client-slug>|<YOUR-SITE-ID>'; then
  #     SCANS="$CLAUDE_PROJECT_DIR/clients/<client-slug>/compliance/scans"
  #     FRESH=$(find "$SCANS" -name '*.md' -mtime -1 2>/dev/null | head -1)
  #     if [ -z "$FRESH" ]; then
  #       deny "BLOCKED: <client> deploy with no compliance scan in the last 24h. Run the compliance check, save the report to $SCANS, then retry this exact command."
  #     fi
  #   fi
  #
  # Pair the gate with an "ask" fallback (below) for the case where the hook
  # cannot tell WHICH site the deploy targets.
  # ------------------------------------------------------------------------

  # --site is a shell variable/substitution the hook cannot resolve. Any
  # site-identity-based gate above is blind here, so force a human confirmation.
  if printf '%s' "$SITE_VAL" | grep -q '[$`]'; then
    ask "Site ID is a shell variable the deploy gate can't resolve ('$SITE_VAL'). Confirm this targets the intended site and that any client-specific gates don't apply. Tip: inline the literal site ID so the gate can verify automatically."
  fi

  # Production deploys always surface an interactive confirmation.
  if printf '%s' "$CMD" | grep -qE -- '--prod'; then
    ask "Production deploy — needs an explicit green-light this session."
  fi
fi

# Push to main requires an explicit go (deploys and main pushes are human-gated).
if printf '%s' "$CMD" | grep -qE 'git[[:space:]]+push[[:space:]]' && printf '%s' "$CMD" | grep -qE '[[:space:]]main([[:space:]]|$|:)'; then
  ask "Push to main — needs an explicit go this session."
fi

exit 0
