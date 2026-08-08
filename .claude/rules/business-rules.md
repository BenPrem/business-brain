# Business Rules

## Brand Identity
- Business name: **<YOUR BUSINESS>**
- <YOUR NAME> is the founder, not a freelancer — positioning matters
- Name your live differentiators here (local expertise, vertical specialization, speed, senior-operator strategy) and keep the framing consistent across every surface
- See `communication-style.md` for tone and "we" vs "I" rules

## Client Work
- Current client work always takes priority over internal projects
- Never miss a client deadline — flag risks early
- All client deliverables must be reviewed by the owner before delivery
- Use a consistent proposal structure: Problem → Solution → Why Us → Investment → Next Steps

## Sales & Outreach
- Lead with value, not features — "we can save you X hours" beats "we use AI automation"
- Value-based pricing, not hourly — price based on ROI delivered to the client
- Always follow up — every pipeline contact gets a nurture cadence, not a single touch
- Cold email: keep first-touch copy short (under ~75 words), personalized, with one clear low-friction CTA
- Send cold outreach from secondary domains — never from the primary business domain

## Financial
- Track all revenue in an invoice ledger in the workspace; track payment follow-ups in <TASK SYSTEM>
- Log significant spending decisions in `decisions/log.md`
- Set a monthly tool/API-spend cap and re-baseline it deliberately — never drift past it
- Route API calls through one gateway where possible — one dashboard to monitor spending
- Use tiered model routing: cheap models for bulk work, mid-tier for content, top-tier only for orchestration and complex reasoning
- When building for clients, always calculate the ROI to justify the price
- Review API/tool spend weekly

## Security
- API keys go in `.env` ONLY — never in code files, never in conversation, never pushed to GitHub
- Conversation history stores plaintext in `~/.claude/` JSONL files — any key pasted in chat is persisted and searchable. Always reference keys by variable name, never paste the actual value.
- Always run a security review before deploying anything publicly — use a FRESH conversation (the dev agent is biased toward its own work)
- Audit npm/pip dependencies for hallucinated package names before running install
- Never store client passwords or sensitive credentials in project files
- Use `.gitignore` to exclude `.env`, local override files, and any credential files
- For any client project with a database: enable Row-Level Security (RLS) on every table — no exceptions
- See `references/security-checklist.md` for the full audit prompt and checklist

## Technical
- Test everything locally before deploying
- Use Plan Mode for any build more complex than a simple file edit
- When a skill or tool fails, fix the root cause — don't just patch the symptom
- Prefer skills over MCP tools when possible (cheaper on tokens, more reliable)
- When building websites, always include mobile responsiveness
