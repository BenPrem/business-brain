# Business Brain

**A file-based operating system for running a real business on Claude Code.**

Not a framework. Not a daemon. Not another agent platform. A folder of markdown files that turns Claude Code into an executive assistant, marketing director, and technical executor that actually knows your business — and gets smarter every week you use it.

This is the sanitized, share-ready version of the system a real solo-founder marketing agency runs on every day: client work, proposals, websites, deliverables, invoicing, research, and the agent discipline that keeps all of it from going off the rails.

---

## Why this exists

Everyone building on AI agents hits the same wall: the model is smart, but it wakes up every session knowing nothing about *your* business — your clients, your rules, your standards, the mistake it made last Tuesday that it must never make again.

The viral agent frameworks (OpenClaw, Hermes Agent) proved something important: **the agent's brain should be plain markdown files** — human-editable, git-trackable, portable, auditable. They also proved what happens when you skip the discipline: [17,500+ exposed instances leaking API keys](https://hunt.io/blog/cve-2026-25253-openclaw-ai-agent-exposure), [malicious marketplace skills](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/), and agents taking actions nobody asked for.

Business Brain takes the good idea — files as the brain — and pairs it with the operating discipline those projects learned the hard way. No server, no exposed ports, no skill marketplace, no always-on daemon. Just Claude Code, a folder, and conventions that have survived contact with real clients and real money.

## The 60-second tour

When Claude Code opens this folder, it boots in a defined order:

```
CLAUDE.md                      ← the constitution: who you are, what wins, hard gates
├── @context/work.md           ← what the business is (auto-loaded)
├── @context/current-priorities.md  ← what matters THIS week (auto-loaded)
.claude/rules/*.md             ← learned rules, business rules, comms style, source-of-truth map
.claude/skills/*/SKILL.md      ← repeatable playbooks (only frontmatter loads until invoked)
.claude/settings.json          ← deterministic hooks that enforce the hard gates
memory/                        ← what the agent remembers across sessions
decisions/log.md               ← append-only record of every significant decision
clients/ · ventures/           ← the actual work, one folder per client/venture
```

Each layer has one job. The constitution stays lean. Detail loads on demand. Rules that must *always* hold are enforced by hooks (code), not prose (hope).

## Quickstart

```bash
git clone https://github.com/BenPrem/business-brain.git my-brain
cd my-brain
# 1. Tell it who you are
$EDITOR context/me.md context/work.md context/current-priorities.md
# 2. Open Claude Code
claude
# 3. Say: "Read context/current-priorities.md. What should I work on today?"
```

Prerequisite for the guard hooks: `jq` (`brew install jq`). Without it, the deploy-guard asks you to confirm anything deploy-shaped instead of silently letting it through.

That's the whole install. **No API keys required to start — and none ship in this repo, not even placeholder files.** When a workflow needs a connection (task system, model routing, hosting), [`guides/connecting-tools.md`](guides/connecting-tools.md) walks through exactly what to connect, how each one authenticates, and where its secret lives (never here). Want to see what a filled-in brain looks like before writing your own? Open [`examples/summit-digital/`](examples/summit-digital/) — a fully populated fictional agency.

## The pieces

| Piece | What it does |
|---|---|
| **`CLAUDE.md`** | The operating system: role, #1 priority, source-of-truth hierarchy, hard gates, how the workspace works. Reviewed like code — every always-loaded token costs quality. |
| **`context/`** | Who you are (`me.md`), what the business is (`work.md`), what matters right now (`current-priorities.md`), where you're going (`goals.md`). The priorities file is the daily kickoff and trumps everything else. |
| **`.claude/rules/learned-rules.md`** | The compounding asset. Every correction you give the agent gets routed to the right layer — hook, script, skill edit, or a 1–3 line rule here. Six months in, this file is why the agent stops repeating mistakes. |
| **`.claude/skills/`** | Playbooks the agent runs on trigger phrases: daily briefs, client onboarding, research, QA checklists. Only frontmatter loads until a skill is invoked, so 50 skills cost almost nothing at rest. |
| **`tools/hooks/`** | Deterministic guardrails wired into Claude Code's hook system. The deploy guard blocks dangerous commands *in code* — an agent can't be talked out of a hook. (Netlify is the worked example; the shape ports to any host's CLI.) |
| **`memory/`** | Conventions for what the agent remembers, with token budgets, write-owners per file, and a privacy rule: store the fact, not the source. |
| **`decisions/log.md`** | Append-only decision record: `[DATE] DECISION … | REASONING … | CONTEXT …`. Superseded decisions get marked, never deleted. |
| **`workflows/` + `tools/`** | The WAT split: **W**orkflows are SOPs in markdown, **T**ools are deterministic scripts, the **A**gent is the flexible reasoning between them. If it must happen the same way every time, it's code, not prompting. |
| **`_templates/`** | Scaffolds for new clients, ventures, and session summaries so structure stays consistent as you grow. |
| **`references/`** | Deep methodology that loads only when needed: multi-agent patterns, eval design, the security checklist. |

## Design principles (learned from the agent wars of 2026)

These aren't aspirations — each one traces to a documented failure somewhere in the ecosystem, or in the real agency this system runs:

1. **Files are the brain; hooks are the law.** Prose rules bend under a persuasive prompt. A `PreToolUse` hook that denies `netlify unlink` does not. Anything that must *always* hold gets enforced deterministically. *(If an agent can be talked out of a guardrail, the guardrail doesn't exist.)*
2. **Verification-gated completion.** "HTTP 200" is not shipped. "Connected, 41 tools" is not authenticated. Done = a real read of the user-facing surface returning the expected result. "Couldn't verify" is a first-class state — never rounded up to "done," never rounded down to "failed."
3. **Least privilege, always.** Secrets live in `.env`, referenced by variable name, never pasted into conversation (chat history persists to disk in plaintext). Every integration gets scoped, revocable credentials. No daemon, no exposed surface — the one network-capable tool is an opt-in preview server that binds localhost only and refuses dotfiles.
4. **Untrusted input is data, not instruction.** Scraped pages, inbound emails, and third-party content get an explicit trust boundary before they enter the agent's context. This is the root cause behind most real-world agent exploits.
5. **Route corrections to the right layer.** Mechanically checkable + must-always-hold → hook. Procedural → script or skill. Judgment-shaped → a numbered rule. Something the model now does unprompted → delete the rule. This loop is the whole game.
6. **Context discipline.** Model quality degrades as context fills. Keep always-loaded files lean, delegate file-heavy research to subagents that report summaries, retrieve just-in-time instead of preloading.
7. **Never fabricate.** No invented client facts, reviews, metrics, or sources. An honest gap beats a confident hallucination — in client work, one fabricated number can end the relationship.
8. **Write your own skills.** No skill marketplace, by design. Security researchers found large fractions of community agent-skill marketplaces carrying malicious payloads. Port the *pattern* from anywhere; write the SKILL.md yourself.
9. **Autonomy has hard edges.** Standing "keep going" instructions never authorize a production deploy, a push to main, or anything customer-facing. Those need an explicit green-light, every time.
10. **Boring beats clever.** This system optimizes for a business's durability, not a demo's wow. Plain files, no magic, nothing that breaks when a dependency updates.

## The self-improvement loop

The reason this compounds instead of plateauing:

1. You correct the agent once.
2. The correction gets **routed**: hook, script, skill edit, or learned rule (with the full story archived, the distilled rule kept to 1–3 lines).
3. Sessions end with a summary that captures preferences learned, decisions to log, and skills worth building.
4. When the model starts doing something unprompted, the rule that taught it gets deleted. The rule file stays lean.

Six months of this and you have something no off-the-shelf agent has: an operating manual for *your* business that a stranger — or a model three generations from now — could pick up cold.

## What this is NOT

- **Not an always-on agent.** There's no daemon, gateway, or webhook here. (If you want that later, this folder is exactly the brain you'd mount into one — that's how the original runs its own automation box.)
- **Not a coding framework.** It's for running a *business* — client work, marketing, operations — with code as one of many outputs.
- **Not plug-and-play automation.** It's an operating system you inhabit. The first week is you teaching it your business; every week after is it giving that back with interest.

## License & credits

MIT. Built by [Benjamin Premenko](https://github.com/BenPrem) at **Vager Media**, a digital marketing agency in West Texas that runs its real client work on the private version of this system. Design lessons drawn from the documented successes and failures of [OpenClaw](https://github.com/openclaw/openclaw), [Hermes Agent](https://github.com/NousResearch/hermes-agent), and [Buzz](https://github.com/block/buzz) — see `SECURITY.md` for the specifics.

If this helps you run your business, a star helps other founders find it.
