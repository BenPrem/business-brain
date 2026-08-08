# Memory Conventions

Persistent agent memory: one file per fact, indexed, budgeted, and owned. This directory is
how the agent remembers things across conversations without re-reading the whole workspace.

## One File Per Fact

Every memory is its own markdown file with frontmatter:

```markdown
---
name: project_acme_website
description: One line the index can show — what this memory contains and why it matters
type: project
---

The actual memory content. Short, dense, current.
```

**Types:**
- `user` — who the owner is, working style, preferences, standing constraints
- `feedback` — corrections the owner gave; behavioral rules learned from mistakes
- `project` — state of a client project or venture (status, decisions, resume points)
- `reference` — durable how-to knowledge (API contracts, platform gotchas, workflows)

Name files `type_short_slug.md` (e.g. `feedback_never_fabricate_facts.md`,
`project_acme_website.md`) so the type is visible in every listing.

## The Index

`INDEX.md` is the only memory file that auto-loads — `CLAUDE.md` imports it via
`@memory/INDEX.md`. It carries **one line per memory** — the filename as a link plus the
description — and never the content itself:

```markdown
- [project_acme_website.md](project_acme_website.md) — Acme site rebuild: launched 2026-03-01, retainer phase next
```

The agent reads the index every session and opens individual memories just-in-time when a
task touches them. Content in the index defeats the whole design.

## Token Budgets

- Keep the always-loaded index small — it is a tax on every single conversation.
- Target roughly 8K tokens total for the index plus any always-load memories; split the
  index into sub-indexes (e.g. `reference-index.md`, `feedback-index.md`) before it bloats.
- Mark only genuinely load-bearing feedback memories as always-load; everything else is
  retrieved on demand.
- Prune on a schedule: completed projects get compressed to a 2-3 line closing state.

## Write-Owner Discipline

Decide which process may write which files, and hold to it:

- **The main agent** writes `user`, `feedback`, and `project` memories during sessions.
- **Subagents never write memory directly** — they return findings; the parent decides
  what becomes a memory.
- **Automated jobs** (cron agents, watchers) write only their designated files, never the
  index structure.

Uncontrolled writers turn memory into a landfill nobody trusts.

## Update, Don't Duplicate

- A new fact about an existing topic goes INTO the existing file — never a second file
  covering the same ground with a slightly different name.
- **Delete wrong memories.** A memory contradicted by verified reality is worse than no
  memory; fix it the moment the contradiction is found, in the same session.
- Never write a proposal or plan into memory as if it were live state — memory carries
  only what is verified true (see learned rule on proposals vs. state).

## Dates

Convert relative dates to absolute at write time. Relative dates rot — "last Tuesday" is
meaningless in three weeks, while `2026-01-13` stays unambiguous forever. Same for
"currently", "recently", "next month" — anchor them.

## Privacy: Store the FACT, Not the SOURCE

Record "client prefers invoices on the 1st" — not the email thread, message dump, or
transcript it came from. Raw sources belong in the client folder (or nowhere); memory holds
the distilled, minimal fact. This keeps memory small AND keeps sensitive material out of a
file class that loads broadly.

## Gating Client-Sensitive Memories

Files carrying client-sensitive data (deal terms, credentials context, personnel issues,
legal matters) must **never auto-load into shared or subagent contexts**. Keep them out of
the index's always-load set, and when spawning subagents, pass only the specific facts the
task needs — never point a subagent at the memory directory wholesale.
