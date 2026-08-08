---
name: mcp-integration
description: Connect an MCP server into your agent surfaces — interactive Claude Code sessions and/or a headless always-on automation box. Triggers on "connect <service>", "add <service> MCP", "wire up <tool>" (task system, email, analytics, chat, GitHub, etc.). Runs the auth decision tree, audits + version-pins community packages, and enforces the verify-through-a-real-call gate. NOT for using an already-connected MCP or building a new server from scratch.
---

# MCP Integration

Wire an external service into the agent stack. Two kinds of surface:
- **Interactive** — Claude Code on your main machine; a human is present to click through browser auth.
- **Headless** — an always-on automation box or scheduled agent; nobody is there to re-authenticate.

## Step 1 — Ask which surface(s)
Interactive only, headless only, or both. Confirm — don't assume.

## Step 2 — The auth decision tree

Research the service's MCP offering (WebSearch/WebFetch its docs) and classify:

| Service offers… | Path |
|---|---|
| **stdio** server (npm/pip) taking a **token/API key** via env var | **Preferred, especially for headless.** No browser, survives reboots, revocable. |
| **remote OAuth** server **with** dynamic client registration (DCR) | Native OAuth: `claude mcp add --transport http <name> <url>`, then authenticate via `/mcp`. |
| **remote OAuth** server **without** DCR | Interactive: register a dev app, pass `--client-id/--client-secret --callback-port`. Headless: avoid browser-OAuth entirely — find a **stdio + token** community server instead. |

**Headless doctrine:** for any unattended box, prefer stdio + long-lived token over
browser-OAuth frameworks. A server that needs browser re-auth, pairing, or human
approval on an unattended machine is a liability — it WILL silently die at the worst
time. If the only official option is browser-OAuth, look for a token-based community
server (then run Step 3 hard) or skip the integration.

## Step 3 — Security gate (mandatory for community packages)

Before trusting any package with a credential:
1. **Audit:** `npm view <pkg>` (maintainer, last publish, weekly downloads); GitHub
   stars + last commit; read its `dependencies` for anything hallucinated,
   typosquatted, or suspicious.
2. **Pin the version** — install `@x.y.z`, never `@latest`. An auto-updating package
   holding your credentials is a supply-chain hole.
3. **Least-privilege credential** — scoped, revocable, treated like a password.
   Never paste a secret into chat or onto a bare command line (history persists).
4. After install, run whatever dependency/vulnerability scan your stack has; report
   findings and distinguish pre-existing issues from ones the new package introduced.

## Step 4 — Install

**Interactive (Claude Code):**
```bash
claude mcp add --transport http --scope user <name> <url>            # DCR OAuth
# or, no-DCR OAuth:
claude mcp add --transport http --scope user --client-id <ID> --client-secret --callback-port 8080 <name> <url>
# or, stdio + token:
claude mcp add <name> -e TOKEN_VAR=<value-from-.env> -- npx <pkg>@<pinned-version>
```
Then authenticate via `/mcp` in the session. Two gotchas:
- Programmatic auth tools that attempt DCR fail on no-DCR servers — use manual `/mcp`.
- Tools load only in a session started AFTER auth — fully restart the app.

**Headless box:** install the stdio server globally with the pinned version, register
it with your agent's MCP config using the absolute binary path, and set the real
token in the env — a placeholder left in config gets passed literally and fails
silently.

## Step 5 — THE VERIFICATION GATE (non-negotiable)

**"Connected, N tools discovered" ≠ authenticated.** Tool discovery is static schema
exchange; authentication is only exercised by a real call.

- `mcp list` / connection tests confirm wiring, NOT auth.
- **Done = a tool call returns real, recognizable data** — a workspace list showing
  YOUR workspace name, a record you know exists, a message that actually arrives.
- A config file with a surviving placeholder string will still report "connected."
  Grep configs for placeholder patterns after setup.
- Until a real call succeeds, the status is **"configured, pending live
  verification"** — never "done", "live", or "shipped."

## Step 6 — Record it

Write/update a memory or reference note per service (`reference_<service>_mcp.md`):
endpoint, auth path, package + pinned version, gotchas hit, and the verified-live
data point (what call, what data came back, date). Also update the "Tools Connected"
list in CLAUDE.md — honestly.

## Gotchas (learned the hard way)

- OAuth-based servers on headless boxes break on token expiry with no one to fix
  them — this is why the decision tree exists.
- Extras/plugins for an agent framework can silently downgrade pinned shared
  dependencies — watch the process on restart after installing.
- Service managers behave differently over SSH than at the console — manage the
  agent via its own CLI, not the OS service layer.
