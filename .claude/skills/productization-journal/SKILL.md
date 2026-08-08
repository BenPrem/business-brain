---
name: productization-journal
description: Capture workflows, templates, integrations, and process decisions as reusable product specs for future productization (SaaS, licensing, done-for-you services). Trigger on explicit requests — "log this", "document this workflow", "add to the product journal", "capture this for productization" — and as a hook during the weekly review ("what did I build this week that isn't in the journal?"). NOT an every-task auto-logger.
---

# Productization Journal

Every workflow, template, integration, and decision documented here becomes blueprint
material for a sellable product later. Capture what was built, why it works, what it
replaced, and how it could be abstracted for any small business — not just the client
that triggered it.

## Lane definition (what goes where)

This journal is for **reusable system specs** — how a workflow/template/integration
works and how it would generalize to another business. It is NOT the place for:
- **`decisions/log.md`** — one-line business decisions with reasoning/context (no spec).
- **`.claude/rules/learned-rules.md`** — corrections and durable operating rules.
- **Memory files** — session-to-session working context.

If one piece of work produced all three (a decision, a lesson, and a reusable
system), each goes to its own home; the journal entry links the others rather than
duplicating them.

## When to log

- The operator explicitly asks: "log this", "document this workflow", "add to the
  product journal", "capture this for productization"
- Weekly review hook (the daily-brief skill's Friday review): ask "What did you
  build this week that isn't in the product journal?" and log the answers
- A deliverable format, client workflow, or integration is finalized in a form
  another business could benefit from — OFFER to log it; don't silently fire on
  every task

## Entry schema

Every entry is a Markdown file in `references/product-journal/entries/`, named
`YYYY-MM-DD_short-descriptor.md` (e.g. `2026-03-18_review-management-workflow.md`).

```markdown
# [System Name]

**Date:** YYYY-MM-DD
**Origin:** [Which skill/workflow/project created this]
**Category:** [workflow | integration | template | skill | decision | edge-case | process]
**Client Context:** [Which client triggered this, or "internal"]
**Reusability Score:** [1-5 — 1 = very client-specific, 5 = works for any SMB]

## What It Does
[2-4 sentences. Specific about tools, files, and systems involved.]

## The Problem It Solves
[The pain point. Why it matters to a small business owner.]

## How It Works
- Trigger (what kicks off this workflow)
- Inputs (what data/context is needed)
- Process (what happens, in what order)
- Outputs (what the client or system gets)
- Tools involved (records workspace, <TASK SYSTEM>, MCP servers, hosting, email platform, etc.)

## Key Decisions & Why
[Tradeoffs, alternatives considered, why this approach won.]

## Productization Potential
[How this could become a standalone product or service — and the revenue model:
licensing, SaaS, template marketplace, done-for-you service.]

## Abstraction Notes
- What's hardcoded that should be configurable?
- What assumptions are baked in about this client/industry?
- What would a settings panel need to expose?
- What integrations would need to be swappable?

## Edge Cases & Gotchas
[What broke, what was unexpected, what to warn a future user about.]

## Dependencies
[Other systems, skills, or integrations this relies on.]

## Status
[active | deprecated | experimental | needs-refinement]
```

## INDEX convention

Maintain `references/product-journal/INDEX.md`: entries grouped **By Category**,
**By Reusability Score**, and a **Product Module Map** table
(Module | Core Entries | Status) that clusters related entries into future product
modules. Update the index in the same commit as the entry — an unindexed entry is
invisible.

## CHANGELOG convention (quick-log)

For small updates that don't warrant a full entry, append to
`references/product-journal/CHANGELOG.md`:

```markdown
## YYYY-MM-DD
- **[category]** Brief description of what changed and why. Reusability: X/5
```

## How the journal gets used

- **When building skills:** check the journal first. If a new skill overlaps an
  existing entry, extend the system rather than duplicating it.
- **When pitching clients:** high-scoring entries are upsells or add-ons.
- **When planning products:** quarterly, review 4-5-score entries and assess which
  could become paid products.
- **When archiving projects:** extract any reusable system as an entry BEFORE the
  project moves to `archives/`.

## Behavior guidelines

1. **Be concrete, not abstract.** Actual file paths, field names, prompt snippets, config details.
2. **Capture the "why" ruthlessly.** The what is easy to reconstruct; the why disappears.
3. **Think in modules.** Every entry hints at which product module it belongs to.
4. **Flag manual steps.** Anywhere the operator is the bottleneck = a premium human-in-the-loop feature or a future automation target.
5. **Record the client's reaction.** Client feedback on a workflow is paid product research.
6. **Version, don't overwrite.** Updates get a new entry referencing the old one — the evolution tells you V1 vs V2.
