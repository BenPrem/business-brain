# Security Posture

This repo is a *brain*, not a service. It runs inside Claude Code on your machine and ships no daemon and no management surface (the one network-capable tool, `tools/serve.mjs`, is opt-in, binds localhost only, and refuses dotfiles). That kills the biggest failure class of 2026's agent frameworks outright — but a business brain still concentrates sensitive material (client data, credentials, strategy), so the discipline below is part of the system, not an appendix.

## Lessons this design is built on

The agent ecosystem ran the experiments so you don't have to:

- **OpenClaw's CVE-2026-25253**: an unauthenticated export endpoint plus default-port deployments left [17,500+ instances leaking API keys](https://hunt.io/blog/cve-2026-25253-openclaw-ai-agent-exposure), with later scans finding [tens of thousands more exposed](https://www.penligent.ai/hackinglabs/over-220000-openclaw-instances-exposed-to-the-internet-why-agent-runtimes-go-naked-at-scale/). → *This repo has no server, no ports, no management surface. Keep it that way. If you ever bolt one on, auth-by-default, fail closed.*
- **Marketplace skills as a supply chain**: [Unit 42](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/) and [Koi Security](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) found hundreds of malicious skills in community marketplaces — infostealers, C2 payloads, scanner-evasion tricks — slipping past the marketplaces' own scanners. → *No marketplace here. Port patterns from anywhere; write every SKILL.md yourself and review it like code.*
- **Prompt injection through "data" fields**: [Imperva showed](https://thehackernews.com/2026/06/new-attacks-trick-openclaw-ai-agent.html) attacks riding in contact names and vCard fields that were flattened into the prompt with no trust boundary. → *Anything scraped, received, or third-party enters context framed as data-to-analyze, never instructions-to-follow. Skills that ingest external content must say so explicitly.*
- **Unintended autonomy**: proactive/scheduled agents have taken real actions nobody asked for. → *Standing instructions never authorize deploys, pushes to main, spending, deletions, or anything customer-facing. Each needs an explicit green-light in the same conversation. Hard gates live in hooks (code), not prose.*

## House rules

1. **Secrets live in `.env` only.** Reference keys by variable name in conversation — never paste a value. Claude Code chat history persists to disk in plaintext (`~/.claude/`), so a pasted key is a stored key. `.env` is gitignored; keep it that way.
2. **`.claude/settings.local.json` is gitignored here — deliberately.** Claude Code appends your approved commands to it, and approved commands can embed secrets (a real `env:set KEY "value"` approval once trapped a live API key in a tracked settings file in the parent system — found months later, in git history). Never commit it.
3. **Least privilege per integration.** Scoped tokens over account-wide ones. Revocable over permanent. One credential per surface, so one leak burns one thing.
4. **A verification gate on every connection.** "Connected, N tools discovered" is not authenticated — tool discovery is static. An integration is live only after a real call returns real, recognizable data.
5. **Public means audited.** Before any deploy or repo goes public, run the audit in `references/security-checklist.md` from a **fresh conversation** — the agent that built the thing is biased toward shipping it. Sweep for: leaked keys, real names/emails/IDs in "example" content, hallucinated package names in dependencies, missing RLS on any client database.
6. **The brain's contents are radioactive.** Client folders, memory files, and decision logs carry confidential material. Never publish, screenshot, or paste them into third-party tools. If you fork this template to share your own version: fresh repo, fresh history, hand-rewritten content — git history never forgets, so a "cleaned up" repo that once held client data is still a leak.
7. **Hooks fail toward safety on hard gates.** The deploy-guard denies what must never happen and asks on what needs a human. Convenience hooks may fail open; gates on money, production, and client-facing surfaces must not.

## Reporting

Found something wrong in this template? Open a GitHub issue (for anything sensitive, use GitHub's private vulnerability reporting instead of a public issue).
