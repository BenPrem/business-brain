# Product Journal

The product journal records systems, workflows, templates, and integrations built during
operations that could generalize into standalone products or services. Every entry is
blueprint material for future productization — SaaS, licensing, template marketplace, or a
done-for-you service line.

This directory is owned by the **productization-journal skill**
(`.claude/skills/productization-journal/SKILL.md`) — that skill defines the capture
behavior; this README defines the on-disk structure.

## When to add an entry

- The operator explicitly asks: "log this", "document this workflow", "add to the product
  journal", "capture this for productization".
- The weekly review hook fires: "what did you build this week that isn't in the journal?"
- A deliverable format, client workflow, or integration is finalized in a form another
  business could benefit from — offer to log it; don't silently fire on every task.

What does NOT belong here: one-line business decisions (→ `decisions/log.md`), operating
corrections (→ `.claude/rules/learned-rules.md`), and session working context (→ memory).
If one piece of work produced all three plus a reusable system, each goes to its own home
and the journal entry links the others.

## Entry format

Entries live in `entries/`, one Markdown file each, named `YYYY-MM-DD_short-descriptor.md`.

```markdown
# [System Name]

**Date:** YYYY-MM-DD
**Origin:** [Which skill/workflow/project created this]
**Category:** [workflow | integration | template | skill | decision | edge-case | process]
**Client Context:** [Which client triggered this, or "internal"]
**Reusability Score:** [1-5 — 1 = very client-specific, 5 = works for any small business]

## What It Does
[2-4 sentences. Specific about tools, files, and systems involved.]

## The Problem It Solves
[The pain point. Why it matters to a business owner.]

## How It Works
- Trigger / Inputs / Process / Outputs / Tools involved

## Key Decisions & Why
[Tradeoffs, alternatives considered, why this approach won.]

## Productization Potential
[How this could become a standalone product or service — and the revenue model.]

## Abstraction Notes
[What's hardcoded that should be configurable; baked-in client/industry assumptions;
what a settings panel would expose; which integrations would need to be swappable.]

## Edge Cases & Gotchas
[What broke, what was unexpected, what to warn a future user about.]

## Dependencies
[Other systems, skills, or integrations this relies on.]

## Status
[active | deprecated | experimental | needs-refinement]
```

## Maintenance conventions

- **INDEX.md** groups entries By Category and By Reusability Score, plus a Product Module
  Map clustering entries into future product modules. Update the index in the same commit
  as the entry — an unindexed entry is invisible.
- **CHANGELOG.md** is the quick-log for small updates that don't warrant a full entry.
- **Version, don't overwrite:** an updated system gets a NEW entry referencing the old
  one — the evolution from v1 to v2 is itself product research.

## How the journal gets used

- **Building skills:** check the journal first; extend an existing system rather than
  duplicating it.
- **Pitching clients:** high-scoring entries are upsells and add-ons.
- **Planning products:** quarterly, review 4-5-score entries for paid-product candidates.
- **Archiving projects:** extract any reusable system as an entry BEFORE the project moves
  to `archives/`.
