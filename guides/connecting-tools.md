# Connecting Tools

This repo ships **zero credential files — not even an example one**. An `.env.example` listing key names is one copy-paste away from becoming an `.env.example` containing key values, and "example" files are where leaks hide. Instead, this guide tells you exactly what to connect, how each connection authenticates, and where its secret actually lives.

**The rules that govern every connection:**

1. Secrets never enter this repo, in any file, under any name. `.gitignore` blocks `.env` and `.env.*` wholesale — there is no exception pattern.
2. If a tool needs an environment variable, create `.env` at the repo root yourself (it is gitignored) or export the variable in your shell profile. Reference it by name in conversation — never paste the value; Claude Code chat history persists to disk in plaintext.
3. Prefer auth that never produces a file in this folder at all: CLI logins that store tokens in their own config (`~/.netlify/`, `~/.config/gh/`), and MCP servers registered via `claude mcp add`.
4. Nothing counts as connected until a **real call returns real data** ("configured" ≠ working — see the `mcp-integration` skill).

---

## Tier 0 — required, no accounts or keys

| Tool | Why | Install | Verify |
|---|---|---|---|
| Claude Code | The runtime | [claude.com/claude-code](https://claude.com/claude-code) | `claude` opens in this folder |
| git | Version the brain | preinstalled on macOS / `apt install git` | `git status` |
| jq | The deploy-guard hook parses hook JSON with it | `brew install jq` | `jq --version` |
| Python 3.10+ | The `tools/*.py` scripts | preinstalled / python.org | `python3 --version` |
| Node 18+ | `tools/serve.mjs` local preview | nodejs.org | `node --version` |

No secrets involved anywhere in this tier.

## Tier 1 — recommended for daily driving

### A task system (Asana, Linear, Trello, …)
The brain treats `<TASK SYSTEM>` as the owner of live task state. Connect yours as an MCP server so the agent can read and write tasks:

1. Pick the official (or audited, version-pinned) MCP server for your system.
2. Create a **scoped personal access token** in that system's developer settings — the narrowest scope that can read/write your projects, nothing account-wide if avoidable.
3. Register it: `claude mcp add <name> -e <TOKEN_VAR>=<paste-at-the-prompt> -- npx <package>@<pinned-version>` — the token lands in Claude Code's MCP config, not in this repo.
4. **Verify:** ask the agent to fetch one real task you can see in the UI. Tool discovery succeeding is not verification.

Run the `mcp-integration` skill for the full decision tree (including why headless setups want stdio + long-lived tokens over browser OAuth).

### Playwright (screenshots for QA)
Needed by `tools/shot.py` and `tools/screenshot.py` (used by the `site-qa-checklist` skill).

```bash
pip install -r requirements.txt
playwright install chromium
```

No account, no key. Verify: `python3 tools/shot.py https://example.com` produces a screenshot.

## Tier 2 — optional, connect when a workflow needs it

### OpenRouter (multi-model routing)
Only needed if you use `tools/openrouter_client.py` (the 60/30/10 cheap/mid/premium routing described in `CLAUDE.md`). Claude Code itself needs none of this.

1. Create a key at [openrouter.ai](https://openrouter.ai) → Settings → Keys. Set a monthly spend limit on the key when you create it.
2. Create `.env` at the repo root (first confirm: `git check-ignore .env` prints `.env`) and add a line assigning the key to `OPENROUTER_API_KEY`.
3. **Verify:** `python3 -c "from tools.openrouter_client import complete_cheap; print(complete_cheap('say ok'))"`
4. Check spend weekly at openrouter.ai/activity.

### Static hosting CLI (Netlify is the worked example)
Needed only when you deploy client sites from here.

1. `npm i -g netlify-cli`, then `netlify login` — the token lives in the CLI's own config in your home directory, never in this repo.
2. Note your site IDs somewhere non-secret (site IDs identify, they don't authenticate — but they're still client-identifying, so keep them out of public forks).
3. The `tools/hooks/deploy-guard.sh` gates activate automatically: every deploy needs an explicit `--site`, production deploys need a human green-light. Using Vercel/Cloudflare instead? Swap the command patterns in the hook — keep the shape.
4. **Verify:** deploy to a draft URL, then re-fetch the draft URL and confirm your change is actually in the response body.

### Email/ESP, CRM, analytics, anything else
Same pattern every time: scoped token → registered via `claude mcp add` or your own `.env` → verified with one real read → recorded in `CLAUDE.md`'s "Tools Connected" list so the agent knows what's real. If a service only offers account-wide tokens, note that in `decisions/log.md` as accepted risk.

---

## When something wants a key this guide doesn't cover

Before connecting it, answer three questions in writing (a line in `decisions/log.md` is enough): What's the narrowest scope that works? Where will the secret live (never here)? What single real call proves it works? Then connect it, run the call, and add it to `CLAUDE.md` → Tools Connected.
