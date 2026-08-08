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

### Google Places + PageSpeed (lead finding and site scoring)
Needed by `tools/lead_scraper.py`, `tools/competitor_analyzer.py`, `tools/website_auditor.py`, and `tools/prospect_workup.py`.

1. In Google Cloud Console, create a project and enable **Places API (New)** and **PageSpeed Insights API**. One API key serves both.
2. Restrict the key to exactly those two APIs (Credentials → key → API restrictions) and set a budget alert.
3. Add it to `.env` as `GOOGLE_PLACES_API_KEY`.
4. **Verify:** `python3 tools/lead_scraper.py --niche "coffee shop" --location "<your city>" --limit 3 --dry-run` returns real businesses.

### Firecrawl (website scraping for research tools)
Needed by the same four tools for scraping prospect/competitor sites (they degrade gracefully without it). Create a key at [firecrawl.dev](https://firecrawl.dev), add it to `.env` as `FIRECRAWL_API_KEY`, verify by running `website_auditor.py` against any URL and confirming the scrape step succeeds. (Firecrawl also offers an MCP server — see the MCP section below; the Python tools use the REST API and only need the env var.)

### Meta Graph API (Facebook/Instagram reporting for social clients)
Needed by `tools/meta_insights.py` and `tools/meta_posts.py`. Creating the Meta app, generating a long-lived Page access token, and finding your Page/IG IDs is a multi-step flow — follow `guides/meta-graph-api-setup.md`. It ends with three `.env` variables: `META_ACCESS_TOKEN`, `META_PAGE_ID`, `META_IG_ID`. **Verify:** `python3 tools/meta_posts.py --days 7` prints real posts.

### Groq (optional — fast hosted transcription)
`tools/meeting_listener.py` uses local Whisper by default (no account). If you want 10x faster transcription, create a key at console.groq.com and add it as `GROQ_API_KEY` — the script auto-detects it.

### Email/ESP, CRM, analytics, anything else
Same pattern every time: scoped token → registered via `claude mcp add` or your own `.env` → verified with one real read → recorded in `CLAUDE.md`'s "Tools Connected" list so the agent knows what's real. If a service only offers account-wide tokens, note that in `decisions/log.md` as accepted risk.

---

## Exact environment variables

Every env var the shipped tools read, in one place. All of them live in your gitignored `.env` at the repo root (or your shell profile) — the variable **names** are documented here; the values never appear in any file in this repo.

| Variable | Read by | Where to create it | Scope guidance |
|---|---|---|---|
| `OPENROUTER_API_KEY` | `tools/openrouter_client.py` (and everything that imports it: `prospect_workup.py`, `website_auditor.py`, `competitor_analyzer.py`, `cold_email.py`, `meeting_listener.py`) | [openrouter.ai](https://openrouter.ai) → Settings → Keys | Set a monthly spend limit on the key at creation; check spend weekly |
| `OPENROUTER_SITE_URL` / `OPENROUTER_APP_NAME` | `tools/openrouter_client.py` (optional) | n/a — your own values | Non-secret attribution strings shown on OpenRouter's dashboard |
| `ASANA_TOKEN` | `tools/asana_cli.py` | Asana → Settings → Apps → Developer → Personal access tokens | PAT is account-wide by nature; use a dedicated seat if you can. The CLI never prints it |
| `ASANA_WORKSPACE_GID` / `ASANA_DEFAULT_PROJECT_GID` | `tools/asana_cli.py` (optional defaults) | Discover via `asana_cli.py workspaces` / `projects` | IDs, not secrets — but business-identifying, keep out of public forks |
| `GOOGLE_PLACES_API_KEY` | `tools/lead_scraper.py`, `tools/competitor_analyzer.py`, `tools/website_auditor.py`, `tools/prospect_workup.py` | Google Cloud Console → Credentials | Restrict to Places API (New) + PageSpeed Insights API only; set a budget alert |
| `FIRECRAWL_API_KEY` | same four research tools (optional — scraping degrades gracefully) | [firecrawl.dev](https://firecrawl.dev) dashboard | Plan quota is the only scope lever; start on the free tier |
| `META_ACCESS_TOKEN` | `tools/meta_insights.py`, `tools/meta_posts.py` | Meta app → long-lived Page token (`guides/meta-graph-api-setup.md`) | Page-scoped token, not a user token; regenerate if it ever appears anywhere |
| `META_PAGE_ID` / `META_IG_ID` | `tools/meta_insights.py`, `tools/meta_posts.py` | Graph API Explorer / your Page settings (see the setup guide) | IDs, not secrets — but client-identifying, keep out of public forks |
| `GROQ_API_KEY` | `tools/meeting_listener.py` (optional — falls back to local Whisper) | console.groq.com → API Keys | Transcription-only usage; free tier is usually enough |
| `NETLIFY_AUTH_TOKEN` | netlify CLI, invoked by `tools/netlify_deploy.py` (optional — `netlify login` is preferred and stores the token in `~/.netlify/`) | Netlify → User settings → Applications → Personal access tokens | Only needed for headless machines; interactive machines should use `netlify login` instead |
| `NETLIFY_SITE_ID` | `tools/netlify_deploy.py` (optional default target) | `netlify sites:list` | ID, not a secret — but prefer passing `--site` explicitly per deploy |
| `SENDER_NAME` / `AGENCY_NAME` | `tools/cold_email.py` (optional — also settable via `--sender`/`--agency`) | n/a — your own values | Non-secret personalization strings |

Rule of thumb: if a tool errors about a missing variable, the fix is a line in `.env` — never a literal pasted into the tool.

---

## MCP connections for this stack

MCP servers give the agent direct tool calls (read a task, scrape a page) instead of shelling out to scripts. The pattern is always the same: pick the official/audited server, register it with `claude mcp add` (tokens land in Claude Code's MCP config, not this repo), then pass the **verification gate** — one real call returning real data you can cross-check in the service's own UI. "Connected, N tools listed" is not verified. The `mcp-integration` skill has the full decision tree.

**Task system** (Asana is the worked example; same shape for Linear/Trello):
```bash
claude mcp add asana -e ASANA_ACCESS_TOKEN=<paste-at-the-prompt> -- npx @<official-asana-mcp>@<pinned-version>
```
Verify: ask the agent to fetch one task you can see in the Asana UI and compare titles.

**Web scraping** (Firecrawl):
```bash
claude mcp add firecrawl -e FIRECRAWL_API_KEY=<paste-at-the-prompt> -- npx firecrawl-mcp@<pinned-version>
```
Verify: scrape one URL you control and confirm the returned markdown matches the live page.

**Email (Gmail):** prefer an official/hosted connector where available (OAuth handled by the provider) over community servers that want an app password. Register per its docs, then verify: search for one email you know exists and confirm the subject line matches. Treat inbox access as the highest-risk connection you have — narrowest scope available, and read-only unless a workflow truly needs send.

**Analytics (GA4):**
```bash
claude mcp add analytics -e GOOGLE_APPLICATION_CREDENTIALS=<path-outside-this-repo> -- npx <ga4-mcp-package>@<pinned-version>
```
Use a service account with **Viewer** on the one property, keep its JSON key outside this repo, and verify: pull yesterday's sessions and compare against the GA4 UI number.

For every server: pin the package version, audit community packages before first run (see SECURITY.md), and record the connection in `CLAUDE.md` → Tools Connected only after the verification call passes.

---

## When something wants a key this guide doesn't cover

Before connecting it, answer three questions in writing (a line in `decisions/log.md` is enough): What's the narrowest scope that works? Where will the secret live (never here)? What single real call proves it works? Then connect it, run the call, and add it to `CLAUDE.md` → Tools Connected.
