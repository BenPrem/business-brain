---
name: client-onboarding
description: Set up everything when a new client signs. Use when the operator says "new client", "onboard [name]", "we closed [name]", "client signed", "deal closed", "kickoff", "set up project for [client]", or moves a lead to Closed Won. Scaffolds clients/<slug>/ from _templates/client/, updates records and the task system, drafts the kickoff email, and generates a discovery prep brief. NOT for lead prospecting.
---

# Client Onboarding

Deal closed → project set up in under 5 minutes. No scrambling.

## When to use
- The operator confirms a deal closed
- A lead moves to "Closed Won" in <TASK SYSTEM>

---

## Step 1 — Gather info

Pull from the existing lead/client record and <TASK SYSTEM> task. Ask for anything
missing:
- **Client name**
- **Contact name and email**
- **Service sold** (website build, redesign, strategy, automation, retainer)
- **Contract value** (one-time phase + monthly retainer if applicable)
- **Timeline** (from the proposal)
- **Deliverables list** (from the proposal)

Check `clients/[client-slug]/deliverables/proposal/` for an existing proposal — pull
scope details from there rather than re-asking.

---

## Step 2 — Create the project folder

Duplicate the standard scaffold at `_templates/client/` and rename to the client slug.
Never hand-roll the tree.

```bash
CLIENT="client-slug"
cp -R _templates/client "clients/$CLIENT"
mkdir -p "clients/$CLIENT/deliverables/proposal" "clients/$CLIENT/deliverables/notes"
```

This gives the standard subfolders (`brand/`, `research/`, `strategy/`,
`deliverables/`) plus `_index.md`. Fill in `_index.md` (Status: Active, Contact,
Service, Start Date, Monthly Value) and append below its Notes heading:

```markdown
## Scope
[From proposal or the operator's description]

## Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

## Timeline
- Week 1: [Phase]
- Week 2: [Phase]

**Phase 1 Value**: [amount] | **Monthly Retainer**: [amount or N/A] | **Target Completion**: [date]
```

---

## Step 3 — Update records + task system

- Update or create the client record: status `Active`, deal value, service sold,
  timeline, project folder path
- Move the <TASK SYSTEM> lead to `Closed Won` or into the active client project
- Create kickoff/setup tasks: assets, access, kickoff call, first deliverable

---

## Step 4 — Draft the kickoff email

For the operator to review and send. Follow the external client tone in
`.claude/rules/communication-style.md`.

```
Subject: Let's get started — [Project Type] for <CLIENT>

Hi [First Name],

Really glad to be working together. Here's what happens next:

1. **This week**: We'll send over a short list of things we need from you
   (logo files, photos, login credentials — nothing complicated).
2. **Kickoff call**: [Propose 2-3 times] — 30 minutes, we'll walk
   through the plan and make sure we're aligned.
3. **First deliverable**: You'll see [first milestone] by [date].

If you have brand files, photos, or anything you'd like included,
go ahead and send them over whenever — no rush on that.

Talk soon,
<YOUR NAME>
<YOUR BUSINESS>
```

Save the draft to `clients/[client-slug]/deliverables/notes/kickoff-email-draft.md`.

---

## Step 5 — Generate the kickoff call agenda

Save to `clients/[client-slug]/deliverables/notes/kickoff-agenda.md`:

```markdown
# Kickoff Call — <CLIENT>
**Date**: [TBD]
**Duration**: 30 minutes

## Agenda
1. Quick intros + relationship building (5 min)
2. Confirm goals — what does success look like? (5 min)
3. Review scope and timeline (10 min)
4. What we need from you — assets, access, content (5 min)
5. Communication preferences — how often, what channel (3 min)
6. Questions + next steps (2 min)

## Assets Needed from Client
- [ ] Logo files (PNG + SVG preferred)
- [ ] Brand colors (hex codes if they have them)
- [ ] Photos (team, office, product — whatever they have)
- [ ] Website login credentials (if redesign)
- [ ] Social media logins (if managing socials)
- [ ] Content/copy they want included
```

---

## Step 6 — Brand groundwork (if website project)

If the service includes a website build or redesign AND the client has an existing
site, extract their branding (colors, type, logo usage, voice) into
`clients/[client-slug]/brand/brand.md` so builder skills can read it. If no existing
site, note in `_index.md` that brand assets must come from the client or be designed
from scratch.

---

## Step 7 — Report

```
Client Onboarded: <CLIENT>
=================================
Project folder: clients/[client-slug]/ (from _templates/client/, _index.md filled in)
Records + <TASK SYSTEM>: Updated to Closed Won / Active
Kickoff email: Drafted → deliverables/notes/kickoff-email-draft.md
Kickoff agenda: Created → deliverables/notes/kickoff-agenda.md
Brand guide: [Extracted from site / Pending client assets]

Assets still needed from client:
  - [List]

Next step: Review the kickoff email and send it.
```
